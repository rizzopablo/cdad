# Revisión focal independiente — 019-002

**Resultado: sin hallazgos bloqueantes nuevos en el alcance de esta revisión.** El bloqueo restante del handoff queda resuelto en el candidato revisado. Esto **no acredita la aceptación completa de la feature**: PC-7 y la suite completa siguen pendientes de evidencia separada.

## Cierre del hallazgo anterior

**Cerrado.** La plantilla de borrador ahora pide las decisiones recuperables del diálogo y un resumen de consulta **solo si hubo consulta** (`skills/cdad-cycle/references/handoff-prompts.md:261–269`, commit `54b40d76`). La contrasté con Stage 2, que permite omitir la consulta cuando corresponde (`stage-2-specification.md:9–19,33–37`), y con reentrada, que conserva esa ruta y la revisión independiente o exención existente (`re-entry.md:228–253`).

Así, la ruta sin consulta ya no exige fabricar un resumen inexistente. No identifiqué una regresión material introducida por esta corrección.

## Estado por promesa y auditoría test → promesa

| Promesa | Categoría y alcance |
|---|---|
| **PC-1 y PC-2** | **Supported within declared limits** para la revisión contextual: diálogo del orquestador, consulta condicional y decisiones recuperables. No demuestra cumplimiento universal de agentes. |
| **PC-3** | **Supported within declared limits** para el ejemplo contextual: `_apply_copy` conserva un destino idéntico y rechaza la divergencia (`cdad_result.py:971–984`). Reutilizo los dos tests de reintento registrados por la revisión 001; no los repetí. |
| **PC-4** | **Supported within declared limits**, reutilizando el GREEN registrado de 17 tests. Los cuatro tests focales se corresponden con derivación nativa, entrega OpenCode, materialización y rechazo de borradores; no prueban fidelidad del diálogo. |
| **PC-5** | **Supported within declared limits**: la guía de cierre y el handoff describen `idle`/`null`; `status` aplica la misma comprobación de coherencia que `open-unit`. Reutilizo los 105 tests GREEN registrados; no los repetí. |
| **PC-6** | **Supported within declared limits para coherencia contextual y evidencia mecánica registrada**, incluido el handoff corregido. F011 permanece rojo por drift de instalación según la revisión anterior; no es un check verde ni acredita carga del candidato. |
| **PC-7** | **Missing**: faltan el ejercicio real y su evaluación independiente. Está pendiente por secuencia, no se presenta como un nuevo defecto de diseño. |

La auditoría focal de tests a promesas no identificó tests nuevos superfluos ni mocks sobre el plumbing: los tests revisados usan CLI y fixtures descartables. Las pruebas no sustituyen la revisión semántica.

## Evidencia y límites

- **Ruta C:** `validate-request` y `validate-packet` terminaron sin error; `render --route C` coincidió con la identificación recibida. `render … | cmp - …/PACKET.md` devolvió **0**. El SHA-256 del spec coincide con el contratado.
- **Candidato:** `54b40d76fa8f4759f135ec3e9ba134acbbcb16b7`; cambió únicamente `skills/cdad-cycle/references/handoff-prompts.md`. `HEAD` observado: `196c6f4a37c72e19e1ce096af3afb2a548587329`. `git diff --quiet 54b40d76 HEAD -- sources agents skills scripts tests install.sh build CDAD_metodologia.md` devolvió **0**.
- `git diff --check bc922c04 HEAD -- sources agents skills scripts tests install.sh build CDAD_metodologia.md` devolvió **0**.
- Contrasté la tabla de decisiones con `docs/adr/`: los identificadores de sus filas tienen archivo; los tres ADR sin fila adicional observados están marcados *Proposed*. No identifiqué contradicción nueva aplicable a esta revisión.
- **Archivo declarado pero ausente:** `recovery-handoff-fix.md` no existe en el checkout. Verifiqué directamente el commit y el diff de la corrección; no doy por leído ese informe.
- **Suite completa no realizada.** Tampoco repetí los GREEN focales ni F011; sus resultados son evidencia previa atribuida, no ejecuciones de esta sesión.
- No modifiqué archivos ni creé commits. El estado observado conservaba `M docs/.cdad-state.json`.

## Abstentions

- No acredito la carga efectiva de instrucciones candidatas en sesiones reales, la fidelidad del recorrido PC-7 ni su evaluación independiente: aún faltan esos registros.
- No acredito un resultado verde de la suite completa ni de F011.