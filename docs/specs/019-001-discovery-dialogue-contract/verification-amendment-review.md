# Revisión del borrador de enmienda

**Objeto revisado:** `docs/specs/019-001-discovery-dialogue-contract/verification-amendment-draft.md`  
**SHA-256:** `847e0e9c003783b991a4516661e814baa7a107d50cd6482a7ed53bb1b0099232`

**Dictamen:** el borrador identifica correctamente que la revisión semántica no sustituye el RED seleccionado. Sin embargo, **la excepción propuesta no tiene una vía de autorización acreditada bajo el procedimiento vigente**. No corresponde habilitar GREEN con esta enmienda tal como está planteada.

## Hallazgos

### 1. La excepción propuesta entra en conflicto con el gate vigente

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

El borrador propone que una autoridad competente apruebe una excepción acotada al RED antes de producción, sin cambiar las instrucciones canónicas (`verification-amendment-draft.md:84–90`). Pero el procedimiento vigente exige RED separado para comportamiento pendiente y GREEN después de un RED válido (`stage-3-tdd.md:149–158, 185–191`; `sources/roles/orchestrator.md:342`). La selección aprobada añade expresamente que la revisión semántica no sustituye RED (`red-selection.md:10–16`).

La delegación del epic autoriza decisiones sobre gates y evidencia dentro de su ámbito (`execution.md:3–12`), pero los documentos examinados **no establecen que esa delegación permita dispensar este requisito canónico manteniéndolo intacto**. Si se procediera solo con la autorización propuesta, se ejecutaría un recorrido contrario al gate declarado.

**Cierre verificable:** mantener GREEN bloqueado y escoger una de estas salidas:

1. Obtener un RED conductual válido conforme al procedimiento vigente; o
2. Tramitar una modificación metodológica explícita por la autoridad competente, con alcance y consumidores afectados identificados, antes de usar una ruta que prescinda de RED.

Reemplazar `red-selection.md` por sí solo no resuelve el conflicto con la norma canónica.

### 2. El procedimiento manual está respaldado como verificación semántica, no como sustituto autorizado de RED

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

La especificación aprobada exige revisión semántica independiente y permite controles estructurales (`spec.md:249–260`); la norma documental también exige registros separados de control y revisión semántica (`documentary-contracts.md:151–164`). Esto respalda una rúbrica manual derivada del contrato **como parte de la aceptación documental**.

No obstante, el borrador la presenta como vía para continuar sin el RED requerido (`verification-amendment-draft.md:34–37, 84–90`). Los especímenes correctos y defectuosos pueden demostrar sensibilidad de la rúbrica, como el propio borrador aclara en la línea 74, pero no demuestran un fallo del producto pendiente ni satisfacen por sí mismos el gate RED.

**Consecuencia:** una rúbrica útil y protegida podría confundirse con autorización para avanzar, aunque falte la evidencia previa exigida.

**Cierre verificable:** conservar la rúbrica como evidencia semántica complementaria y separar explícitamente su aceptación del mecanismo que resuelva el gate RED. No atribuirle cumplimiento de RED sin una modificación metodológica autorizada.

### 3. El índice de decisiones vigentes omite un ADR documental aceptado

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

`docs/systemPatterns.md:5–41` declara ser el índice de decisiones vigentes, pero omite `ADR-040`, que figura como **Accepted** y afecta también al reviewer (`docs/adr/ADR-040-especializacion-documental-por-contrato-casa-unica-y-dos-registros.md:3–9`). Ese ADR establece precisamente la norma documental y la separación de registros.

La consecuencia es que una revisión guiada por la tabla puede no descubrir una decisión aplicable al encargo. No hace falta incorporarla al producto propuesto para resolver este hallazgo: corresponde reconciliar el índice con el estado efectivo del ADR o registrar una decisión autorizada sobre su estado.

## Alternativa práctica bajo las reglas actuales

Solicitar al test-writer un nuevo intento **acotado a Promise A**, con un ejercicio conductual derivado de la especificación y un fallo atribuible a una asignación incorrecta de roles, no a la ausencia de un directorio ni a palabras clave. La forma concreta del verificador debe determinarla el test-writer sin leer el producto ni inventar una interfaz contractual.

Si no puede construir ese oráculo, debe informar el límite; **no está demostrado que añadir una interfaz máquina sea la única alternativa**. En ese caso, mantener el bloqueo y elevar una propuesta de cambio metodológico explícito. La revisión manual protegida sigue siendo valiosa para la fidelidad documental, pero no desbloquea por sí misma GREEN.

## Abstentions

- No puedo acreditar que el mandato delegado incluya una facultad excepcional de dispensar RED: el texto autoriza decisiones sobre gates, pero no explicita una dispensa de este requisito canónico.
- No puedo asegurar que el test-writer logre construir el RED propuesto sin introducir una interfaz innecesaria; requiere su evaluación independiente.
- No evalué un producto `operating-design/` ni su cumplimiento de PC-1–PC-12: esta revisión corresponde al borrador de enmienda, no a la aceptación del producto.

## Evidencia de la revisión

- **Intake Route C:** `validate-request` y `validate-packet` finalizaron sin salida y con código de éxito; el contexto declara `schema_version: 2`. La identificación recibida coincide con el contrato y el paquete validados.
- **Comandos principales:** `python3 scripts/cdad_packet.py validate-request …`; `python3 scripts/cdad_packet.py validate-packet …`; `sha256sum docs/specs/019-001-discovery-dialogue-contract/verification-amendment-draft.md`; `git status --short`; `git rev-parse HEAD`. Se comparó además el índice de ADR con los archivos existentes mediante Python.
- **Revisión examinada:** `24ecf294fbcb14aed0fe02425dc642d7d1eb992c`.
- **Archivos modificados por esta revisión:** ninguno. **Commit creado:** ninguno.
- **Tests:** no ejecutados; revisión de un borrador, no verificación del producto. La suite completa no fue ejecutada ni se acredita su resultado.
- El estado inicial mostraba cambios preexistentes en `docs/.cdad-state.json` y un archivo no seguido `docs/epics/epic-019-discovery-dialogue/replan-review-begin.json`; no se modificaron.