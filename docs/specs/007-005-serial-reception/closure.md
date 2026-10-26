# Cierre 007-005-serial-reception

Fecha: 2026-10-26. Epic: `epic-007-reliable-cycle-operation`. Colección: 7/7.

## Resultado

Un tramo pendiente y autorizado del consumidor activo atravesó **entrada → paquete → continuidad →
despacho real → entrega → recepción → cierre** con la versión adoptada `538ec57`, sin editar el
estado a mano y sin repetir efectos. El informe entregado queda con aprobación semántica
**pendiente**: recibir no aprueba.

## Recorrido observado

| Borde | Hecho observado |
|---|---|
| Entrada | `status` = `continuity-reconcile`/`execution-active`; autoridad `active`; versión `COHERENT` (proyecto, agentes, CLI y Claude Code en `538ec57`). |
| Paquete | `prepare --role architect --substage draft`, scope de escritura vacío; contrato por fallback al plan del epic (diagnóstico registrado). |
| Decisión del delta | `begin` con N=1 (seq 16) declarando lo ya resuelto por el antecedente (digest) y la pregunta diferencial restante. |
| Pretransporte | `verify-begin` válido para el paquete y N=1. |
| Despacho | Sesión raíz en el consumidor; `record` verificó `parent`, `moment` y `project`; `delivery=staged`. `model_reported` observado del almacén; `model_configured` nulo con procedencia explícita (CDAD no elige modelo). |
| Recepción | `receive --continuity-attempt 1` sobre el descriptor; recibo validado (`VALID`), `semantic_status=pending`. |
| Continuidad | Checkpoint de recibo seq 17 enlazado por `prev` al `begin` seq 16 y con el digest del recibo. |
| Salida | Transición de entrega registrada; `status` final = `execution-active → resume`; `reconcile` clasifica `received` y `repeat_effect=false`. |

## Evidencia

- Contrato: `spec.md` (PC-01..PC-08 + AJ1–AJ4) con la **enmienda PC-03** (`amendment-pc03.md`, sustitución contractual
  retrospectiva autorizada): la moneda del `begin` se acredita por encadenamiento (`verify-begin` seq/body_sha256 = `begin`;
  `prev` del cierre = ese mismo cuerpo; sin checkpoint intermedio), no por cercanía temporal.
- Manifiesto materializado: `evidence/manifest.json` (31 entradas, rutas parametrizadas, digest,
  cobertura por PC y límites por entrada).
- Verificación privada (misma máquina, resolución alias→ruta privada):

```text
entradas verificadas: 31/31
postcondiciones cubiertas: 8/8
documentos escaneados: 7 — identidad: sin filtraciones
PASS
```

- Desviación declarada y aceptada: `deviation-2026-10-26.md`.
- Límites no observados: fallos de runtime, timeout, cuota, reparación y retiro; el informe no está
  aprobado; las identidades de sesión y la resolución de rutas permanecen privadas. `reconcile`
  agrega «historia anterior conservada, no demostrable»: el encadenamiento acredita el borde
  observado, no toda la historia previa.

## Postcondiciones

| PC | Estado |
|---|---|
| PC-01 | **Satisfecha.** Autoridad activa, procedencia coherente y versión adoptada verificadas; la autorización de despliegue consta en el handoff de CDAD (2026-10-26) como decisión del dueño, con la versión desplegada y su respaldo. |
| PC-02 | **Satisfecha.** Paquete read-only y decisión del delta con el digest del antecedente. |
| PC-03 | **Satisfecha bajo el contrato enmendado (sustitución autorizada).** `verify-begin` devuelve `seq 16` y `body_sha256 dedb50df…`; el cierre seq 17 tiene `prev` con ese mismo cuerpo y no hay checkpoint intermedio. **El requisito original de inmediatez temporal no se cumple** y se declara no observado; la enmienda sustituye esa garantía, no la cumple. |
| PC-04 | **Satisfecha.** Registro verificado con correlación y observaciones honestas del runtime. |
| PC-05 | **Satisfecha.** `delivery=staged` consumido por `receive`; sin otra recepción. |
| PC-06 | **Satisfecha.** Recibo válido contra los bytes del informe; `semantic_status=pending`. |
| PC-07 | **Satisfecha.** Cierre enlazado por `prev`, con el recibo y su digest. |
| PC-08 | **Satisfecha.** `status` final con verbo explícito, `reconcile` sin repetición y manifiesto validado. `reconcile.unknowns` declara «historia anterior conservada, no demostrable». |

## Gate de cierre

**Suite completa: 1705 passed, 5 skipped, 0 failed** (log `.cdad/local/full-007-005.log`).
No hay cambio de producto en esta unidad; la suite ya no muestra la contaminación que apareció en la
corrida de 007-004.

## Deudas y observaciones

1. **`REC-NEXT-ACTION-STALE` (nueva, observada):** el cuerpo del checkpoint de recepción conserva el
   `next_action` previo («despachar el mismo paquete») aunque ya referencia el recibo. La vista
   compacta (`resume`) y `reconcile` protegen contra repetir el efecto, pero un lector del cuerpo
   puede re-despachar. Se registra para decisión y alcance propios; **no se repara en esta unidad**.
2. `SUITE-CONTAMINATION` y `SUSP-*` siguen abiertas; no afectan este tramo.
3. El informe entregado responde a la pregunta diferencial y declara incógnitas; su contenido no se
   aprueba aquí.
4. El primer transporte rechazado por identidad es fallo observado; su sesión ejecutó el mismo
   encargo (desviación aceptada en `deviation-2026-10-26.md`).

## Criterio del epic

Aporta la **recepción real** que faltaba, **con una desviación operativa aceptada** (dos transportes;
el primero rechazado por identidad, sin registro ni efectos). **No acredita el recorrido feliz del
epic**: éste exige entrar desde reposo y aquí la entrada observada fue una ejecución activa; tampoco
acredita el recorrido de fallo como uso real, la reparación natural, el retiro ni la suspensión en
este tramo. El recorrido feliz del epic queda **pendiente de evidencia independiente**.
