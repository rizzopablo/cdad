# Revisión independiente — 019-003

**Resultado: permanece un hallazgo bloqueante de coherencia en la guía principal.** La revisión no constituye aprobación.

La candidata examinada es `b82724a8`, contra la base `0b11b5fb` y la especificación aprobada. El diff revisado es documental y de instrucciones; no observé cambios de addon que justifiquen exigir una instalación limpia Odoo.

## Hallazgo

### La guía principal sigue exigiendo tests y suite para compromisos exclusivamente semánticos

**Required — Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-cycle/SKILL.md:538-553, 586-588`, en contraste con `skills/cdad-cycle/references/stage-3-tdd.md:146-155, 322-342`.  
**Afecta:** PC-3, PC-5 y PC-6.

La referencia de Stage 3 permite producir una promesa exclusivamente semántica sin fabricar RED ni exigir una suite para ella; su aceptación depende de revisión contextual independiente. Sin embargo, la sección **“Verification — required evidence (non-negotiable)”** de la guía principal:

- enumera RED, GREEN y suite verde como evidencia mínima por subfase, sin distinguir la ruta semántica;
- dice que una postcondición se verifica mediante un test de comportamiento;
- presenta una postcondición sin test como no verificada en la tabla de refutaciones.

**Consecuencia:** un operador que siga la tabla explícitamente presentada como evidencia no negociable recibe una obligación incompatible con la ruta semántica. Puede bloquear un cierre legítimo o fabricar un test que no acredita la fidelidad comprometida. Las condiciones corregidas de los gates no eliminan esta instrucción contradictoria en el mismo consumidor principal.

**Cierre verificable:** condicionar esa tabla y sus refutaciones al método aprobado para cada promesa: mantener RED/GREEN y evidencia ejecutable donde correspondan; para semántica, controles estructurales aplicables y revisión contextual independiente; para mixtas, ambas familias. Contrastar los tres recorridos sin debilitar la política vigente de evidencia.

## Revisión de las correcciones anteriores

- **Blocker de `review-003`:** la contradicción concreta del loop y gate de Stage 4 queda corregida en `stage-4-review.md:203-215` y `cdad-cycle/SKILL.md:370`: las partes semánticas reciben controles aplicables y revisión contextual; las mixtas conservan ambas familias. El hallazgo anterior identifica otra sección efectiva que conserva el requisito incondicional.
- **Excepción de segunda pasada:** la restricción de `stage-4-review.md:207` es consistente con el contrato para una corrección semántica: sin revisar el producto corregido no se acredita su fidelidad. La regla conserva la excepción para las demás correcciones mecánicas; no identifico una restricción adicional injustificada.
- **Bloqueos de `review-001` y `review-002`:** las rutas señaladas permanecen corregidas en Stage 3, el gate de exención, la guía ligera y la distinción de paquetes congelados. No repetí el probe de cambio de fuente viva.

## Resultado por postcondición

| PC | Resultado |
|---|---|
| **PC-1 y PC-2** | La guía normal y la ligera declaran estrategia por promesa y revisión de suficiencia o exención registrada. Sin nuevo defecto identificado en lo examinado. |
| **PC-3** | **No acreditado:** persiste la contradicción descrita en el hallazgo. |
| **PC-4** | La guía examinada protege el criterio aprobado y devuelve cambios necesarios a aprobación. |
| **PC-5** | Las categorías de cierre están declaradas, pero la evidencia incondicional de la guía principal contradice el método semántico. |
| **PC-6** | **No acreditado:** existe el hallazgo de coherencia y permanecen los límites de comparación indicados abajo. |

## Evidencia y límites

- **Entrada:** `validate-request` y `validate-packet` terminaron sin salida ni error. `render --route C` reprodujo la identificación recibida; el contexto es v2.
- Revisé el inventario de tests y su alcance en `test-audit.md` y `tests/test_010_001_documentary_contracts.py`. Los controles estructurales no acreditan por sí solos fidelidad semántica.
- El log `.cdad/orchestration/epic-019/019-003-fix-003-final-pytest.log` registra **138 passed in 85.75s**. Lo examiné, pero **no ejecuté esa selección** ni atribuyo el resultado a una corrida propia.
- Los logs de los validadores registran **182 passed, 1 failed** en consistencia y fallo de `validate-subagents.sh`; este último identifica drift y archivos instalados ausentes. **No medí la base**, por lo que no determino que todo el drift sea preexistente ni considero esos checks verdes.
- `git diff --quiet 0b11b5fb HEAD -- docs/specs/019-001* docs/specs/019-002* tests` devolvió `0`: no hay diferencias en esas rutas rastreadas. Esto verifica preservación física, no toda su fidelidad semántica.
- Contrasté la tabla de decisiones vigentes con su índice de ADR; no identifiqué una contradicción adicional atribuible al diff en lo examinado.
- **Suite completa:** no realizada, excluida por el encargo. **Archivos modificados por esta revisión:** ninguno. **Commit:** ninguno. `docs/.cdad-state.json` ya figuraba modificado al inicio y seguía así al finalizar.

## Abstentions

- No acredito PC-6 en su totalidad: no comparé exhaustivamente todas las variantes de dominio, salidas instaladas ni antecedentes protegidos.
- No ejecuté un recorrido integral de una feature nueva ni reproduje el probe de drift de paquetes congelados.
- No determino si los fallos de instalación reportados son exclusivamente preexistentes.