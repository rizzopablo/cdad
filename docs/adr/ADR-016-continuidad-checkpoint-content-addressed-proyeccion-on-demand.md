# ADR-016 — La continuidad es un checkpoint content-addressed; la proyección y el juicio quedan fuera del state

## Estado
Propuesto para aprobación del dueño (2026-10-07).

## Contexto
El trabajo prolongado se interrumpe (rotación de sesión, crash, límite de contexto) y hoy
obliga a repetir objetivo y autorizaciones o a recargar historial. 003-004 resuelve
memoria activa + checkpoints + reanudación **sin** redefinir el estado/paquete (001), los
receipts/idempotencia (002) ni los eventos/presupuesto (003). La observabilidad del
runtime es limitada: no hay límite de contexto duro verificado (V1/V3) y la ausencia de
receipt no distingue "no entregó" de "entregó por otra vía". Se necesita que reanudar sea
barato, auditable y sin duplicar efectos, sin introducir un servicio ni un agente
permanente.

## Decisión
`skills/cdad-cycle/scripts/cdad_continuity.py` (Python stdlib, determinista) es un CLI
**read-only sobre el producto** con `begin`/`checkpoint` (write-ahead, escriben solo bajo
`.cdad/executions/<id>/continuity/**`), `reconcile`, `resume` y `trigger` (estos tres
read-only y deterministas). Tres contratos con nombre: `continuity-checkpoint-v1`,
`reconcile-v1`, `trigger-v1`.

1. **Checkpoint inmutable content-addressed (L2).** Cuerpo canónico cuyo `sha256` es el
   digest del checkpoint, más `prev_checkpoint_sha256`, `seq` monotónico y `references[]`
   con digest. `resume`/`reconcile` verifican sha del cuerpo, eslabón previo y
   existencia+digest de cada referencia; cualquier fallo → rc≠0 con el delta exacto.
   `begin` con cuerpo idéntico al head es **no-op (rc 0)**, clave
   `(execution_id, packet_id, attempt)`; cabezas divergentes o
   igual-sha-con-cuerpo-distinto ⇒ **escalar**.
2. **Memoria activa = proyección on-demand (L1), no persistida.** No existe `ACTIVE.json`;
   la proyección se reconstruye desde la cabeza L2 y su ausencia no es error. `--max-bytes`
   (default 16 KiB) falla cerrado sin truncar. La historia es L3 y se consulta **por
   referencia** (state/`stage_history`, receipts 002, eventos 003, dispatches I8, Memory
   Bank).
3. **`reconcile` como oráculo, antes de todo retry/resume.** Con receipt/journal de 002
   válido **no** repite el efecto; `dispatched-unknown` ≠ fracaso ≠ autorización de
   repetir. `continuity` **consume** el receipt 002 y **no materializa**.
4. **`trigger` es señal, no límite.** Solo `prepare`/`rotate` con contador **y** límite
   enteros; en cualquier otro caso `unknown` con `context_*: null`.
5. **Un solo escritor del state y de la aprobación.** El CLI **nunca** escribe
   `docs/.cdad-state.json` ni aprueba: el orquestador es el único escritor (ADR-003) y la
   aprobación estratégica es del dueño (ADR-004). Autoridad y vigencia se leen del estado
   estructurado (`hitl_delegation` + `authority_ref`); la autoridad vencida reconstruye
   contexto pero **no** autoriza dispatch/materialize.

## Alternativas consideradas
- **Estado/proyección persistido (`ACTIVE.json`) como fuente.** Descartado: crea una
  segunda verdad que puede divergir del checkpoint; la proyección on-demand desde la
  cabeza L2 evita el problema y su ausencia no es un error.
- **Contador `generation` para detectar split-brain.** Descartado: un solo `seq` monotónico
  más la comparación de cabezas (divergentes o igual-sha-con-cuerpo-distinto) basta y
  escala sin estado extra.
- **`trigger` con un límite estimado (p. ej. bytes→tokens).** Descartado por invariante de
  honestidad: desconocido permanece desconocido; no se fabrica un límite ni un proxy.
- **Servicio/agente permanente de continuidad o subcomando `budget` propio.** Descartado
  por el epic: consume más de lo que ahorra y redefiniría el presupuesto durable de 003 (se
  consulta con `cdad_guard budget`).
- **`--allow-stale` y subcomando `verify-checkpoint`.** Descartados (O3/R1): stale → rc≠0
  con el delta exacto, y tamper/referencias se verifican dentro de `resume`/`reconcile`.

## Consecuencias
- (+) Reanudar es barato y auditable: objetivo, decisiones con razón, autoridad e
  incertidumbres se reconstruyen sin recargar historial; idempotencia real verificada
  (RU-1b, `no_op: true`). Interfaces durables keyed por `execution_id` conviven con 002 y
  003 sin redefinirlos.
- (+) Separación limpia de responsabilidades: el CLI nunca escribe el state ni aprueba; el
  checkpoint es create-only; la proyección no se persiste.
- (−) La utilidad de `trigger` depende de observabilidad hoy ausente: **casi siempre
  `unknown`** hasta calibrar V1/V3 con uso real.
- (−) `reconcile` queda **limitado sin `receive`**: si el despacho no pasa la salida por
  `cdad_result receive`, solo puede clasificar `dispatched-unknown` (deuda RU-2a).
- (−) **Rollback/replay de un head viejo y tamper autoconsistente no son detectables**
  (sin firma ni contraste de `seq`); documentado en `continuity.md`.
- (−) El uso real (RU-1) expuso un defecto de integración que los fixtures no vieron y
  exigió un review-fix antes de cerrar T4.

## Confianza
**Media.** El diseño y las postcondiciones están verificados por tests focales
(`continuity-checkpoint-v1`/`reconcile-v1`/`trigger-v1`) y por **una** rotación real en
frío (RU-2, P2/P3 demostradas) e idempotencia real (RU-1b); la separación
analizador/orquestador es consistente con ADR-003/ADR-011/ADR-014/ADR-015. Sin embargo,
`trigger` es casi siempre `unknown` y `reconcile` está limitado sin `receive`, y la primera
adopción real reveló un defecto de integración → la confianza sube con calibración de uso
real.
