# Revisión independiente — 019-003

**Resultado: un bloqueo de coherencia de instrucciones.** Esta revisión no constituye aprobación.

## Hallazgo

### La ruta semántica sigue exigiendo pruebas aleatorias por declarar invariantes

**Required — Verdict: BLOCKING · Bucket: h**  
**PC afectadas:** PC-3 y PC-6.  
**Ubicaciones:** `skills/cdad-cycle/references/stage-3-tdd.md:15,144,168,291-299,326,340` y `skills/cdad-cycle/references/handoff-prompts.md:478-495`.

La nueva ruta distingue correctamente la producción exclusivamente semántica de las promesas con comportamiento ejecutable pendiente. Sin embargo, la misma guía sigue ordenando delegar a *properties* y exigir pruebas de propiedades verdes **si la especificación declara invariantes**, sin condicionar esa obligación al método aprobado o a que los invariantes sean verificables mediante una campaña ejecutable. El handoff correspondiente pide explícitamente entradas aleatorias.

Esto afecta directamente a contratos como el de esta feature: declara invariantes y aclara que son restricciones revisables, **no una demanda automática de pruebas aleatorias**. Un orquestador que siga ambas instrucciones recibe órdenes incompatibles: respetar la revisión contextual comprometida y, a la vez, fabricar una campaña no comprometida para atravesar el gate.

**Consecuencia para el usuario:** una tarea semántica puede quedar bloqueada en Stage 3, o generar pruebas aleatorias que no verifican la fidelidad prometida, antes de llegar a la revisión independiente que sí establece su aceptación.

**Movimiento propuesto:** condicionar coherentemente el enrutamiento, el gate y el handoff de propiedades a los invariantes para los que el contrato realmente selecciona pruebas de propiedades ejecutables; conservar la revisión contextual de los demás. Regenerar los consumidores afectados cuando corresponda.

**Cierre verificable:** contrastar las instrucciones canónicas y efectivas con dos casos: un contrato semántico con invariantes revisables, que llega a revisión sin campaña fabricada, y otro que compromete expresamente pruebas de propiedades, que conserva su gate y evidencia.

## Bloqueo anterior: staging e instalación

La discrepancia concreta de `review-006` **quedó subsanada para la entrega examinada**:

- La evidencia persistida registra `make staging` con código `0`, seguido de instalación aislada con código `0` y comparaciones iguales para los agentes y archivos de skills modificados.
- Comprobé independientemente con `cmp` que las dos variantes actuales de `cdad-orchestrator.md` en staging coinciden con las candidatas; ambos comandos devolvieron `0`.
- El procedimiento normal documentado exige `make staging` antes de instalar y nuevamente al actualizar (`README.md:73-97`). `install.sh:92-95` consume staging por diseño. Por tanto, la necesidad de regenerarlo **no demuestra por sí sola un defecto durable de la instalación normal documentada**. Una instalación que omite ese paso puede usar staging obsoleto; no he verificado una protección automática contra esa omisión y no la atribuyo a la promesa aprobada.

No repetí la instalación aislada: los resultados de esa operación son **evidencia registrada por otra sesión**, no una ejecución observada por mí.

## Alcance y evidencia

- **Intake:** `validate-request` y `validate-packet` terminaron sin error; `render --route C` reprodujo la identificación recibida.
- **Tests primero:** examiné `test-audit.md` y la evidencia de instalación antes de contrastar el contrato y las instrucciones. No ejecuté tests ni la suite completa; esta última estaba excluida del encargo.
- **PC-1 y PC-2:** la guía examinada declara estrategia por promesa, revisión de suficiencia y exención registrada. No identifico un nuevo defecto en esas superficies.
- **PC-3 y PC-6:** afectadas por el bloqueo anterior. La corrección de staging no resuelve la contradicción de *properties*.
- **PC-4 y PC-5:** en las superficies examinadas no identifiqué un nuevo debilitamiento de criterios protegidos ni una presentación de evidencia ausente como éxito.
- **Protección histórica:** `git diff --quiet 0b11b5fb HEAD -- tests docs/specs/019-001* docs/specs/019-002*` devolvió `0`.
- **Decisiones vigentes:** consulté la tabla y el directorio de ADR. No concluí una comprobación exhaustiva de correspondencia entre todas sus filas y archivos.
- **Diff:** instrucciones, agentes derivados y documentación; no observé cambios de addon que activen una batería Odoo.
- **Revisión examinada:** HEAD `48945297`; base de comparación `0b11b5fb`. `docs/.cdad-state.json` aparecía modificado al inicio.
- **Archivos modificados por esta revisión:** ninguno. **Commit:** ninguno.

## Abstentions

- No acredito un recorrido integral con agentes reales ni la ejecución de la suite completa.
- No determino la procedencia del drift de la instalación real señalado en la revisión anterior.
- No acredito exhaustivamente la correspondencia de la tabla de decisiones con todos los ADR.