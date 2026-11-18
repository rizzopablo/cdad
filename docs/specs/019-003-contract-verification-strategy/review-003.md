# Revisión independiente — 019-003

**Resultado:** queda un hallazgo bloqueante de coherencia en el cierre de compromisos exclusivamente semánticos. La revisión no constituye aprobación.

Revisión examinada: `5b7f1c186b5dc16a7d72e800a37a9c50101bd57d`, contra la especificación aprobada y el diff desde `0b11b5fb`.

## Hallazgo

### El cierre de revisión exige una suite verde incluso cuando la ruta semántica dice que no existe

**Required — Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-cycle/references/stage-4-review.md:200-215`; contraste con `skills/cdad-cycle/references/stage-3-tdd.md:135-155, 322-342`.  
**Afecta:** PC-3 y PC-6.

La ruta de Stage 3 permite una feature exclusivamente semántica sin RED fabricado y señala que no tiene una suite que deba estar verde, aunque mantiene los controles estructurales aplicables. Sin embargo, Stage 4 exige que «la suite siga verde después de cada corrección» y, sin condición, incluye «suite still green after the fixes» en su gate de salida.

**Consecuencia:** si una revisión semántica encuentra algo que corregir —y aun en la lectura literal del gate de salida— el operador recibe instrucciones incompatibles: no hay suite de la promesa que acreditar, pero el gate exige su verde. Esto puede bloquear el cierre legítimo o incentivar la presentación de una corrida ajena como evidencia de la promesa.

**Cierre verificable:** condicionar el loop y el gate de Stage 4 a las verificaciones ejecutables y estructurales que realmente correspondan, conservando la revisión contextual independiente y la política de evidencia vigente. Contrastar un recorrido semántico con corrección y otro mixto, sin omitir los checks aplicables.

## Revisión de los dos bloqueos anteriores

1. **Estrategia previa en el flujo ligero:** la regla 2 y la fila 1→2 ahora exigen revisión independiente de suficiencia o exención registrada antes de producir; también declaran los campos de verificación por promesa (`skills/cdad-spec-and-test/SKILL.md:20-33, 64-65, 108-111`). La ruta ligera remite expresamente a la aprobación y al registro canónicos, y declara que el ciclo es dueño de los gates. **No encuentro evidencia suficiente para sostener que haga falta inventar otro gate o registro autónomo.** La preocupación sobre una ejecución sin contexto de ciclo queda como límite de interpretación, no como bloqueo acreditado.

2. **Recepción de paquetes congelados:** la instrucción ahora distingue solicitudes con snapshots de históricas y separa integridad estructural de vigencia semántica (`re-entry.md:283-309`). El renderer confirma que las primeras usan bytes congelados y las históricas leen fuentes vivas (`cdad_packet.py:1762-1770, 1868-1879`). Los logs del probe reportan los casos de drift y restauración; **no repetí ese probe**, cuyo script no está en el repositorio. El código y los registros respaldan el cierre de la contradicción anterior dentro de ese límite.

La guía ligera también conserva explícitamente ambas familias de verificación para compromisos mixtos; una no sustituye a la otra.

## Evidencia y límites

- **Entrada:** `validate-request` y `validate-packet` terminaron sin error; `render --route C` reprodujo la identificación recibida. Contexto de ejecución v2.
- **Ejecución propia focalizada:**
  ```text
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
    tests/test_006_006_u3_review_route_and_gate.py::test_pd16b_reentry_declares_the_compatibility_policy_between_revisions \
    tests/test_006_006_u5_exemption_record.py

  15 passed in 32.35s
  ```
- Los tres logs de la selección del implementer registran **94 passed** cada uno; no reproduje esa selección completa. No ejecuté la suite completa, excluida por el encargo.
- El docstring de `test_pd16b_reentry_declares_the_compatibility_policy_between_revisions` sigue afirmando que *todo* paquete deja de ser recibible tras el cambio de fuentes (`tests/test_006_006_u3_review_route_and_gate.py:623-646`). Es deuda de mantenimiento: el test pasa con la declaración histórica y no acredita la distinción semántica completa. Una eventual modificación corresponde al test-writer; no atribuyo por sí sola a ese texto un bloqueo adicional.
- El diff examinado es de documentación e instrucciones, sin cambio de addon; no corresponde exigir por él una instalación limpia Odoo.
- **Archivos modificados por esta revisión:** ninguno. **Commit de esta revisión:** ninguno. `docs/.cdad-state.json` ya figuraba modificado al inicio y seguía así al finalizar.

## Abstentions

- No acredito PC-6 en su totalidad: no comparé exhaustivamente todas las salidas instaladas y variantes de dominio.
- No reproduje el probe de drift ni una transición integral de una feature nueva. Los resultados del probe se presentan como registros examinados, no como ejecución propia.