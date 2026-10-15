# Informe del architect — corrección focal C0 (delta + spec/plan 004-001)

Sesión aislada cdad-architect vía delegación nativa; materializado por el orquestador GLM el 2026-09-24. Base: HEAD `21238de`. Envoltorio de delegación omitido de origen (política de sanitización); cuerpo íntegro sin edición. Las secciones 6 y 7 de este informe fueron materializadas como `docs/specs/004-001-canonical-runtime-artifacts/{spec,plan}.md`.

## 0. Estado verificado

- **Repositorio**: `cdad/` anidado; rama `codex/epic-003-context-efficiency`; HEAD `21238de` (verificado hoy: `21238de → b808e07 → e7f68a1`). Cambios documentales sin commit leídos tal como están; no se tocó nada (read-only).
- **Dictamen C0 de Claude** leído completo (`c0-review-claude-2026-09-24.md`, 105 líneas). El informe revisado es `spec-plan-004-001-architect-2026-09-24.md` (262 líneas). Este informe es un parche del revisado, no un re-análisis.
- **Verificaciones nuevas realizadas hoy**:
  1. `cdad_packet.py:34` — verificado el nombre exacto y contenido de la constante: `VALID_EPIC_STAGES = {"features-loop", "epic-integration", "epic-closure"}` (tres valores, **sin** `epic-planning`). La constante se consume **solo** en `:231`, dentro de la rama `scoped-exception`; el modo `ordinary` retorna en `:219-221` sin consultar `epic_stage`, y la rama `scoped-exception` está acotada a epic-003 single-model (`:223-224`).
  2. `state-detection.md:14` — verificado: seis valores, incluido `epic-planning`.
  3. `scripts/cdad-bash-allowlist.sh:152` — verificado: `rule "wc *" allow` sin par `rtk wc` (grep repo-wide: 0 matches de `rtk wc` en el script). Confirmado el gap del par.
  4. **Reproducción en vivo del paradox de T1, en esta misma sesión**: la llamada `wc -c agents/cdad-*.md agents/claude-code/cdad-*.md` fue **denegada** pese a que el error enumera `"wc *": allow` — reproducción exacta del rechazo no-attribuído documentado en `findings/permission-friction-c0-2026-09-24.md:38-43`. Consecuencia material: **la sesión orquestador tampoco tiene capacidad de medición fiable hoy**, lo que invalida una de las dos opciones del dictamen (ver §1).
  5. `cdad_packet.py:411-412` (techo 12.000 bytes), `:418-421` (hashes en `instruction_sources`), `:552-556` (prepare exige `.cdad/execution.json`), `:590-595` (write de state), `:605-624` (rollback acotado) — todos verificados hoy.
  6. `docs/specs/004-001-canonical-runtime-artifacts/` **no existía**; se crea al materializar.
  7. `.gitignore` verificado (11 líneas): **no** contiene `build/`.
  8. Citas cruzadas re-verificadas donde se reutilizan: `enmienda:80-81,96-98,33,34,44,109-112`; `ADR-011:92,104-109,118-126,151-153`; `c0-review-gpt:86-96,109-114,205-207,228-236`; `plan.md(epic):126-131,166-169,184-185,189-198,267-274`; `test_role_packet_consumers.py:46-47`. Tres citas del predecesor resultaron mal atribuidas → §8 Errata.

## 1. Corrección requerida resuelta

### Opción elegida: **(a) — T1 incluye el mínimo de capacidad de medición (los pares faltantes), declarado como el primer aterrizaje del rediseño.**

**Por qué (a) y no (b).** La opción (b) requiere un rol que "ya tenga la capacidad". Hoy no existe tal rol en los runtimes disponibles: la sesión architect tiene el par faltante y además los rechazos de `wc` simple no atribuidos (`finding:38-43`), y **la sesión orquestador acaba de reproducir el mismo rechazo en vivo**. La única sesión que midió bytes fue la de review GPT, por lectura binaria independiente en otro runtime; su capacidad no es asumible para cada re-ejecución de T1. Elegir (b) hoy sería fichar la línea base otra vez con evidencia prestada — el fallo que originó la errata.

**Costo de (a), acotado:**
- Cambio de producto mínimo: en `scripts/cdad-bash-allowlist.sh:152` sustituir `rule "wc *" allow` por `pair "wc"` (el helper de pares ya existe, `finding:31-33`), que emite `wc *: allow` **y** `rtk wc *: allow`. ~1 línea en fuente + reinstalación por el camino de instalación existente (F009 se mantiene).
- El assert F009 asociado se actualiza en el mismo cambio.
- Mini-ciclo acotado: positivo (el architect mide bytes con `rtk wc -c` desde su sesión; RTK lista `wc` como soportado, `finding:109-112`) + negativo (los efectos no listados siguen en catch-all deny — el par es aditivo, el catch-all se retiene).
- Deuda evitada: en T4 la tabla de capacidades genera los pares desde la fuente; el aterrizaje 0 se declara en el plan como primer aterrizaje del rediseño.
- No contradice "no corrección aislada de `wc`": es el primer aterrizaje del rediseño, no un parche suelto.

**T1 revisada** — dos sub-aterrizajes: (i) **Aterrizaje 0**: par `rtk wc *` completo en fuente+instalación, con su micro-ciclo positivo/negativo y assert F009 actualizado en el mismo cambio; (ii) **Baseline**: medición por el architect con la capacidad recién aterrizada — conteo de líneas y bytes por rol×runtime×camino (clásico vs paquete), método (`rtk wc -l`/`-c`), versión, configuración y sesión ejecutora registrados, **totales mecánicos del propio comando** (los totales de `wc`, no una agregación manual — la lección del finding:54-66), valor efectivo del techo de bytes registrado, y los bytes de GPT como **contraste externo**, no como fuente.

**PD-13 revisada**: la baseline se produce **con la capacidad de medición aterrizada en el propio feature**, no con evidencia prestada. Si una medición excede la capacidad aterrizada, se declara VERIFY y se diagnostica como error de entorno — nunca se sustituye por estimación.

**Duda 4 corregida**: retirado "la fricción `wc` persiste hasta T3/T4". Texto nuevo: *"El costo de fricción del incidente C0 no recae sobre la evidencia de T1: el aterrizaje 0 de T1 provee la capacidad determinista (`rtk wc *`) antes de medir la línea base. Las variantes residuales (rechazo de `wc` simple, no atribuido; `du`) pueden persistir hasta T4, pero ninguna medición de PD-13 depende de ellas; cada rechazo injustificado se registra como defecto del producto para 003-003, sin bloquear la baseline."*

## 2. R13 añadida

**Cita errónea corregida.** El predecesor citó `cdad_packet.py:34` como respaldo de usar `epic-planning` en la activación. Verificado hoy: `VALID_EPIC_STAGES` (`cdad_packet.py:34`) contiene solo `{"features-loop", "epic-integration", "epic-closure"}` — **no** incluye `epic-planning`. La definición de seis valores está en `skills/cdad-epic/references/state-detection.md:14`.

| ID | Hallazgo | Impacto hoy | Dueño |
|---|---|---|---|
| **R13** | Vocabulario de `epic_stage` duplicado y divergente: `state-detection.md:14` define **seis** valores; `VALID_EPIC_STAGES` (`cdad_packet.py:34`) admite **solo tres**. Regla compartida viviendo en dos fuentes editables que ya divergieron. | Práctico: **nulo hoy** — el modo `ordinary` no valida `epic_stage` (retorna en `:219-221`). Riesgo latente: cualquier validación estilo `scoped-exception` para un epic futuro rechazaría `epic-planning`. | **PD-4**; unificación en **T2**. |

**Procedimiento de activación desacoplado de la cita errónea**: la activación escribe `epic_stage: epic-planning` porque (1) es un valor definido por el vocabulario canónico de `state-detection.md:14`; (2) es **seguro en modo `ordinary`** porque `validate_state` retorna sin tocar `epic_stage` (`cdad_packet.py:219-221`); al iniciar el ciclo de 004-001 la etapa pasa a `features-loop`, valor presente en **ambos** vocabularios.

## 3. Tareas reorganizadas

La observación 2 del dictamen se incorpora con **dos aterrizajes** dentro de 004-001 y una regla de crecimiento para T5:

- **Aterrizaje A (intermedio utilizable — instalación SIN CAMBIOS)**: T1–T4. Al cerrar T4 existe un estado utilizable end-to-end: fuentes canónicas → generador determinista → 22 agentes como salidas declaradas → `install.sh` funciona **exactamente como hoy**.
- **Aterrizaje B**: T5–T7. **Regla de tamaño para T5**: si la instalación con manifest (D4 completo) excede su mini-ciclo, T5 pasa a **candidata a feature propia** (spec breve propia, p. ej. `004-004`), decisión del orquestador del epic.

Cambios estructurales: T1 absorbe el Aterrizaje 0; T2 incorpora la unificación R13; T3 gana salidas declaradas con instalación sin cambios + `build/` en `.gitignore` + techo 12k parametrizado (PD-19); T4 pasa a ser el cierre del aterrizaje A; T5 gana la regla de crecimiento y PD-18; T6 gana la decisión del flag post-migración; cada cierre de tarea gana el registro de supervisión (PD-17).

## 4. Supervisión con dueño

**Postcondición nueva PD-17 en la spec de 004-001** (no asignación a 004-003), con nota de que el formato durable del registro se consolida en 004-003. Justificación: 004-001 es la **primera feature que se ejecuta bajo autonomía supervisada**; diferir el dueño dejaría sin verificación de re-entry justamente la ventana en que más importa. Texto completo en la spec materializada. Costo: un registro por cierre de tarea (7 en total); cero código de producto.

## 5. Detalles incorporados

1. **Firma de autoridad**: el usuario en `docs/epics/epic-004-single-source-planning/execution.md`; no se exige otra aprobación para la activación misma (más allá de la aprobación de la spec, que es patrón CDAD).
2. **Esquema `hitl_delegation`**: se conserva sin extender en 004-001.
3. **Layout público**: fuera del default; decisión del flag recién después de migrar los fixtures (T6); sin consumidor real → no hay flag. PD-9 redactada en consecuencia.
4. **`build/` en `.gitignore`**: añadida a la lista de archivos de T3.
5. **El instalador nunca lee `sources/`**: elevado a **PD-18** (revisión de rutas + prueba conductual).
6. **Techo de 12.000 bytes**: parametrizar + diagnosticar, y el valor efectivo se registra en la baseline (PD-19).

Rutas `sources/`, `scripts/cdad-generate.py`, `build/staging/` confirmadas.

## 6. Spec final 004-001

Materializada verbatim en `docs/specs/004-001-canonical-runtime-artifacts/spec.md` (19 postcondiciones, 8 invariantes, 7 criterios de aceptación; marca de aprobación del usuario añadida por el orquestador tras la instrucción en sesión).

## 7. Plan final 004-001

Materializado verbatim en `docs/specs/004-001-canonical-runtime-artifacts/plan.md` (T1–T7 en dos aterrizajes, cobertura trazable de las 19 PD, self-review sin TBD).

## 8. Errata

Correcciones al informe del predecesor (`spec-plan-004-001-architect-2026-09-24.md`), según el patrón de errata enlazada (el original no se reescribe):

1. **Cita `cdad_packet.py:34` como respaldo de `epic-planning`** — no lo incluye; verificado hoy. Resuelto con R13 (§2) y §6 revisado.
2. **Duda 4 del predecesor** ("la fricción persiste hasta T3/T4") — incompatible con baseline medida antes de generar; resuelto con aterrizaje 0 dentro de T1 (§1).
3. **Cita "enmienda `:151-153`"** para el pasaje de aplicación — el pasaje es **ADR-011:151-153**; re-citada corregida.
4. **Cita "enmienda `:107-108` prohíbe patch aislado"** — la prohibición está en **enmienda:80-81**; decisión correcta, cita no.
5. **Cita "enmienda `:110-111`" para "sin repetir toda la tarea"** — la regla de no repetición automática es **ADR-011:126**; errata registrada.
6. **Marcadores `<!-- table not formatted -->`** en el informe del predecesor — artefacto de materialización, no del autor; no replicados aquí.
7. **§0 del predecesor, atribución de bytes** — honesta y correcta en su momento; el plan revisado cierra el hueco con el aterrizaje 0; los bytes de GPT (140.161) quedan como contraste externo.

## 9. Dudas acotadas

Ninguna que bloquee. Las seis dudas del predecesor quedan resueltas con decisión vinculante en §1 (duda 4) y §5 (dudas 1, 2, 3, 5, 6). Único punto abierto de forma: la forma exacta de la unificación R13 (recomendación: vocabulario completo canónico en `state-detection.md:14` + `VALID_EPIC_STAGES` como subconjunto documentado) es decisión de implementación de T2.
