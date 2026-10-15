## Lo que primero (verificación básica del autor)

- El test RED (`3f6f5f9`) fija la superficie observable por CLI subprocess (sin imports del módulo, sin mocks); el implementer no tocó los tests salvo el fix de snapshots (`5ee784e`, justificado). Suite 467 + focales 30/30: **no re-ejecutada** por instrucción del orquestador.
- Alcance del diff: solo los 4 archivos declarados en plan T3 (`cdad_guard.py`, `guard-event.schema.json`, 2 test focales). Sin `docs/.cdad-state.json`, sin artefactos de 003-004/checkpoints ✓.

## Bloqueantes

### F1 — Escape de containment en `record`: `execution_id` sin validar llega al path durable (D4/invariante 1/Violación de la seguridad/regla de contención de la función)
- **Lugar:** `skills/cdad-cycle/scripts/cdad_guard.py` — `_guards_dir()` (`root.joinpath(*GUARDS_TREE, execution_id, "guards")`, sin sanitizar) + `validate_event()` (solo exige string no vacía) + `_cmd_record()` (`mkdir(parents=True)`, `write_text`, y `durable` reportado vía `relative_to(root)`).
- **Evidencia:** `_slug()` solo se aplica a `packet_id`/`kind` en el *nombre de archivo*; `execution_id` se une cruda. `Path.joinpath` con un componente **absoluto descarta el prefijo** y con `..` el OS resuelve fuera de la raíz. Reproducido (fixture efímero en /tmp, demostración de solo escritura):
  ```
  ev.execution_id = "/tmp/cdad-esc-demo" → rc: 1
  file outside root exists: ['/tmp/cdad-esc-demo/guards/p-attempt-0001-recovery-attempt.json']
  ```
  El archivo durable **se escribe fuera de la raíz** y luego el comando muere con traceback (`ValueError` en `relative_to`). Variante `../../x`: el archivo cae fuera de la raíz y el campo `durable` del envelope imprime una cadena que *parece* contenida (`.cdad/executions/../../x/guards/…`) — el envelope miente.
- **Consecuencia:** la promesa central de T3 — "escritura SOLO bajo `.cdad/executions/<id>/guards/**` (nunca `docs/.cdad-state.json`, single-writer)" (plan T3; invariante 1; nota del orquestador) — no se sostiene para un evento mal formado/malicioso. Exactamente el escenario que el predecesor de este mismo repo ya blindó: 002 introduce `_segment()` ("must be a safe segment … Without this, a forged traversal name…") en `cdad_result.py:198-213`.
- **Cierre (verificable):** validar `execution_id`/`packet_id` en `validate_event` con la misma ligadura de clase que 002 (`[A-Za-z0-9][A-Za-z0-9._-]{0,127}`, sin `..`; o resolve del path final anclado bajo la raíz); bajada rc≠0 con diagnóstico stderr, sin escribir nada. Focal: evento con `execution_id="../x"` → rc≠0 y cero escrituras nuevas en el árbol.
- Hoja: F1 · Veredicto: **BLOCKING** · Contenedor: **m**

### F2 — `record` sobrescribe en silencio un evento durable (con la misma clave): el historial no es append-only y la identidad por `_slug` colisiona (D4/invariante 11/P4)
- **Lugar:** `_cmd_record()` — `durable_path.write_text(...)` incondicional; identidad = `_slug(packet_id)-attempt-NNNN-_slug(kind).json` con `_slug` (todo no-alnum → `_`: `"a b"` ≡ `"a_b"` ≡ `"a/b"`).
- **Evidencia:** no hay detección de existencia ni conflicto; un segundo `record` mismo `(execution, packet, attempt, kind)` con causa distinta **reemplaza byte a byte** el evento anterior. P4/invariante 11 exige "reanudar conserva intentos y **causas anteriores**"; la prueba (`test_p04_reanudar_conserva_intentos_y_causas`) solo cubre intentos *distintos* — el overwrite intra-attempt no está probado y destruye la causa anterior sin señal.
- **Consecuencia:** presupuesto durable editable silenciosamente: un reintento del reporter con causa corregida borra la evidencia original; con colisión de `_slug`, el overwrite cruza entre packet_ids distintos. El predecesor 002 fija el patrón correcto de la casa: *"conflict: refusing to overwrite the existing finalization"* (rc≠0, `cdad_result.py`).
- **Cierre (verificable):** creación exclusiva (fail-loud rc≠0 + diagnóstico de conflicto ante (packet, attempt, kind) existente, espejando la convención 002), o renombrar con sufijo del contenido; focal: dos `record` con misma clave y payloads distintos → rc≠0 y bytes originales intactos.
- Hoja: F2 · Veredicto: **BLOCKING** · Contenedor: **m** (ruta realista: retry del reporter tras fallo parcial; overwrite es la conducta actual, no hipotética)

### F3 — `guard-event.schema.json` declarado pero jamás ejercitado; el escritor y el schema divergen (V7/§3/Contrato: "los schemas de evento/presupuesto se validan en RED")
- **Lugar:** `skills/cdad-cycle/assets/guard-event.schema.json` (nuevo; `additionalProperties: false`) vs `validate_event()` (`cdad_guard.py:515-540`, acepta **campos extra**).
- **Evidencia:** grep en `tests/` y `skills/` → el schema no es referenciado por ningún test ni código (solo mencionado en el docstring del test: *"el activo … se valida en GREEN contra esta forma"*. GREEN (`5604725`) llegó **sin** esa validación). Divergencia concreta: un evento con una propiedad extra pasa `validate_event` (persistida en guards/) y viola el schema declarado; además `action` queda libre de la tabla cerrada D5 (los fixtures mismos usan `resume-same-session`/`retry`, fuera de `CLOSED_ACTIONS`).
- **Consecuencia:** un contrato de interfaz entregado (archivo plan T3) puede desincronizarse del escritor silenciosamente — exactamente el escape de V7 que la spec ordena cerrar en RED; los durables bajo guards/ pueden no satisfacer su schema declarado (falsifica el claim de la interfaz D10 "schema estable" para 003-004).
- **Cierre (verificable):** focal que valida un `guard-event-v1` (válido + inválido con propiedad extra + `action` fuera de tabla o decisión explícita documentada) contra el asset (stdlib `json` o el validador que la casa use), o alignar `validate_event` con `additionalProperties:false`. Si la decisión es que `action` no pertenece a la tabla cerrada en events durables, dejarlo declarado en el description del schema.
- Hoja: F3 · Veredicto: **BLOCKING** · Contenedor: **m**

## Opcionales (no prolongados, agrupados por familia)

### O1 — Fidelidad de referencia de reconciliación (D7)
`_find_receipt()` devuelve `files[0]` de `sorted(rglob(...))` sobre `.cdad/runtime/results/<exec>/<packet>/`: en el layout real de 002 (`parts/<name>.utf8`, `bundle.json`, `receipt.json`, `cdad_result.py:_publish`) eso devuelve **`bundle.json`**, nunca `receipt.json`. La publicación es atómica (una sola rename del directorio), así que *presencia ⇒ terminado* es sólido — pero el campo `receipt_ref` que "citan el receipt" (aserción del test, `test_003_003_t3_budget.py:609-618`) cita el bundle. Remedio: buscar `receipt.json` nominalmente y solo eso. Veredicto: OPCIONAL · Contenedor: **m** · Severidad: Nit/Required-light.

### O2 — Interfaz de escalado insuficiente para dedup/continuidad (D10/D11, observación ponte para T5 — no reabre T1/T2)
El paquete `escalation-v1` no lleva `execution_id`, `packet_id` ni fingerprint de las llamadas unknown (lleva `incident_kind` genérico `unknown-signal` + count). El `dedup_key` declarado (plan T5/O3: `canon(incident_kind, fingerprint_canónico, execution_id, packet_id)`) no puede derivarse de lo que el canal emite. No es deuda de T3 según el plan (dedup = T5), pero conviene materializar los campos en la interfaz *antes* de T5 para no truncar el contrato (D10). Veredicto: OPCIONAL · Contenedor: **m**.

### O3 — Interacciones de señal (clasificados solo como diseño)
(a) ≥3 llamadas `unknown` equivalentes disparan **simultáneamente** incidente `repetition-without-progress` (T1 preexistente) y la escalada honesta `unknown` — señales paralelas parcialmente contradictorias que el orquestador debe reconciliar; ninguna línea del contrato las prohíbe y el remedio pertenece a T1. (b) `budget` cuenta **todo** `guard-event-v1` del packet sin filtro por `kind`: un evento administrativo/poll grabado vía `record` consume presupuesto y puede provocar `reconsider` prematuro (semántica de P4 ambigua: "cada recuperación consume" no dice "solo recuperaciones"). Veredicto: OPCIONAL · Contenedor: **m** · Severidad: Considere.

### O4 — Higiene (Nits)
Docstring del módulo cabeza staled (`(003-003, T1 GREEN)`, "Two slices" cuando hay cuatro; el cuerpo T3 sí está actualizado). Fallo de E/S en `record` (OSError en `write_text`) termina en traceback rc=1 en vez del diagnóstico stderr rc≠0 que §3 pide. Veredicto: OPCIONAL · Contenedor: **l** · Severidad: Nit.

## Lo verificado en verde contra la nota del orquestador

- **Reanudar conserva intentos y causas** (P4/i11): probado en 2 procesos distintos, sesiones A/B, causas conservadas por attempt ✓ — con la salvedad intra-attempt de F2.
- **Límite de intentos = señal** (D3): `exhausted/reconsider` con rc 0, sin auto-bloqueo ✓ (`test_p04_limite_agotado…`).
- **Timeout ≠ bloqueo** (i3): `lone_timeout_trace` → sin incidente ni escalada ✓.
- **Unknown no se fabrica** (i4): `unknown: true`, `limitation` declarada, nunca `recommend-block`, sin incidente de repetición forzada en count=1 ✓ (interacción multi-count: O3a).
- **Reconciliación con 002 antes de repetir** (D7): consulta + `do_not_repeat` solo-señala ✓; fidelidad de la cita: O1.
- **Escritura solo bajo guards/**: **NO se sostiene** — F1/F2.
- **Sin checkpoints de 003-004** (D10): diff limpio de ello ✓; canal `escalations` siempre presente en classify-v1 ✓.

## Verificación realizada (solo lectura)

Comandos (repo intacto, `git diff` posterior = 0):
- `git log --oneline 33fe1d9..5604725` · `git diff --stat 33fe1d9..5604725` · `git diff 33fe1d9..5604725 -- <4 archivos>`
- Lectura: `spec.md`, `plan.md`, `review-t2-decision.md`, `closure.md` (002), `cdad_result.py` (`_segment`, `_publish`, `_final_dir`), `cdad_guard.py` completo, ambos tests focales.
- Grep: referencias a `guard-event.schema` (ninguna fuera del docstring).
- Reproducción de F1 en fixture efímero bajo /tmp con el CLI del repo (escritura solo en tempdir, `[root del repo intacto]`).

## Evidencia requerida

- **Modified files (por este reviewer):** ninguno (write_scope vacía; árbol idéntico a `5604725`).
- **Commit evaluado:** `5604725` (`feat(003-003): T3 durable budget + events + escalations (P4/P5)`), sobre `33fe1d9`; fix de tests `5ee784e` intermedio.

## Abstenciones

- **Calibración de severidad de `read_scope`/preflight:** deferida por decisión del dueño (`review-t2-decision.md`); no reabierta aquí.
- **Dedup de alertas end-to-end (P7/D11):** es la superficie de T5; solo constaté la ausencia de campos necesarios en la interfaz (O2) — no juzgo si el mecanismo T5 lo resolviera, porque no existe aún.
- **Señales reales de DB (trace-v1 vivo):** fuera del alcance de este diff (T1); no re-evaluadas.

**Resumen:** F1–F3 bloqueantes (una familia de containment/durabilidad + una de validación de contrato); remediables en una ronda con los patrones ya existentes en 002 (`_segment` + conflict-no-overwrite + validación schema-focal). El resto son opcionales acotados y nits.
