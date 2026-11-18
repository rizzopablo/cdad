# Revisión independiente — 019-003

**Resultado: dos bloqueos para acreditar la entrega.** Esta revisión no constituye aprobación.

## 1. La excepción para efectos laterales o UI contradice el gate de propiedades

**Required — Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-cycle/references/stage-3-tdd.md:293-299`, en contraste con las líneas `144` y `340`.

La corrección condiciona el envío a *properties* a que el contrato aprobado seleccione pruebas de propiedades ejecutables. Sin embargo, la misma sección añade sin condición que la subfase «no aplica» a código con muchos efectos laterales o a UI.

Un contrato puede seleccionar expresamente pruebas de propiedades para uno de esos casos. Entonces las instrucciones simultáneamente ordenan ejecutar esas pruebas y excluyen la subfase que las produce. **Consecuencia:** el equipo puede omitir evidencia comprometida o quedar detenido ante instrucciones incompatibles.

**Movimiento propuesto:** reconciliar la excepción con el método aprobado. Si un compromiso no es viable, devolverlo a revisión y aprobación; no excluir unilateralmente la verificación seleccionada.

**Cierre verificable:** contrastar un contrato que selecciona propiedades para código con efectos laterales o UI y comprobar que la ruta conserva su ejecución y gate, o que detiene el trabajo para corregir el contrato por el procedimiento aplicable.

## 2. Falta evidencia atribuible de la distribución instalada del candidato final

**Required — Verdict: BLOCKING · Bucket: m**  
**Ubicación:** PC-6 y aceptación en `docs/specs/019-003-contract-verification-strategy/spec.md:64-72`; evidencia previa en `review-007.md:23-31`; cambios posteriores en `implementer-fix-report-007.md:5-12`.

La instalación aislada registrada en la revisión anterior precede a los últimos cambios de fuentes y agentes de *test-writer*. En esta revisión comparé los dos agentes genéricos actuales con staging: ambos `cmp` devolvieron `0`. Eso establece igualdad para esas dos parejas, **no** que la instalación aislada distribuya el candidato final completo ni que cubra los demás consumidores afectados.

El informe del implementador registra además `make validate` fallido por F011 y atribuye el fallo al drift de copias instaladas. No repetí esa comprobación ni observé su comparación con la base. Por tanto, no atribuyo el fallo al cambio, pero tampoco lo cuento como evidencia verde.

**Consecuencia:** se podría acreditar PC-6 sin demostrar que la entrega instalada contiene las instrucciones finales; un usuario podría recibir un consumidor anterior al arreglo.

**Movimiento propuesto y cierre verificable:** aportar una comprobación reproducible y atribuible del candidato final —incluida instalación aislada o evidencia equivalente de la protección de distribución aplicable— con resultados y comparaciones de las superficies afectadas. La igualdad de bytes debe acompañar, no reemplazar, la revisión semántica.

## Evidencia y alcance

- **Intake:** `validate-packet` terminó sin error; `render --route C` reprodujo la identificación recibida.
- **Tests primero:** examiné `test-audit.md` antes de contrastar el contrato y las instrucciones. El audit no acredita por sí solo fidelidad semántica.
- **Ejecución independiente:** `PYTHONDONTWRITEBYTECODE=1 pytest -p no:cacheprovider -q tests/test_cdad_generate.py` → `10 passed in 2.64s`.
- **Evidencia comunicada, no reejecutada:** el informe de fix-007 registra 216 tests aprobados, uno omitido y `make validate` fallido. No los presento como ejecución propia.
- **Suite completa:** no realizada; la selección anterior no acredita una suite completa.
- **Protección histórica:** `git diff --quiet 0b11b5fb HEAD -- tests 'docs/specs/019-001*' 'docs/specs/019-002*'` → código `0`.
- **Candidato examinado:** HEAD `51decfa7`, respecto de `0b11b5fb`; `docs/.cdad-state.json` estaba modificado al inicio. El diff revisado contiene instrucciones, agentes derivados y documentación, no cambios de addon.
- **Archivos modificados por esta revisión:** ninguno. **Commit:** ninguno.

## Abstentions

- No acredito la instalación aislada del candidato final ni la causa del drift de las instalaciones reales.
- No acredito una ejecución integral con agentes reales ni el cumplimiento universal de las instrucciones.
- Consulté la tabla de decisiones y el directorio de ADR, pero no completé una comprobación exhaustiva de correspondencia entre todas sus filas y archivos.