# Cierre 008-005-ci-gate

Fecha: 2026-10-28. Epic: `epic-008-suite-coherence`. Feature 5 de 6.

## Resultado

El criterio del epic —«suite, gate por superficie y `validate-state` en cada push; el rojo no se publica»—
tiene **un solo entrypoint versionado** que lo ejecuta, lo evidencia y **falla cerrado cuando el verde no es
atribuible**: `scripts/cdad-ci-gate.py`.

- Corre los cinco pasos en orden fijo y **una sola vez** cada uno: `validate-state`, superficie
  (`--collect-only`, sólo clasificación), doctrina, especialización Odoo y `close --all` —la única corrida de
  pytest—.
- Deja por corrida una raíz nueva con `gate.json` (para máquina) y `suite-report.md` (para humanos), más el
  intento de `close`.
- Un `0` exige commit no nulo, árbol limpio, un solo intento `finished`, resumen verificado y rc 0: el verde
  no atribuible deja de ser posible.
- No publica, no instala, no usa red ni credenciales, y no depende del HOME del operador.
- Un push que sólo toca documentación no enrojece el paso de superficie (clasificación por la política, no
  por prefijos); el producto sin superficie clasificada sí es rojo y nombra la ruta.
- `COLUMNS` fijado en el hijo de `run_pytest_to_logs`: los motivos de skip dejan de truncarse (causa raíz
  medida: la línea de estado se corta al ancho de terminal).

## Contrato

`docs/specs/008-005-ci-gate/spec.md` — 8 PCs, D1–D10 y la regla de cotas (PC-6). Spec enmendada tras el
review: esquema de `gate.json` con `attribution.causes` y los valores de precondición; errores de colección
nombrados; pérdida declarada de la discriminación «acotada por encima de la cota».

## Cambios

- `scripts/cdad-ci-gate.py` (nuevo, ~900 líneas): pasos, aplicabilidad por clasificación, veredicto,
  escrituras confinadas a la raíz de la corrida, funciones puras (`build_verdict`, `render_report`,
  `extract_failures`) y costura `--repo-root` para probarlo sin la suite.
- `scripts/cdad-suite.py`: `COLUMNS` en el entorno del hijo de `run_pytest_to_logs`; parser intacto.
- `sources/roles/test-writer.md`: la regla de cotas de reloj de pared, en su única casa; agentes regenerados.
- `tests/test_008_005_ci_gate.py` (nuevo, 19 tests) + ajuste de las cotas en los 5 archivos de 005-010/006-001.

## Evidencia

| Etapa | Commit |
|---|---|
| Discovery | `4ff74ca` |
| Spec y plan | `ede95ab` (enmendada) |
| RED (16 rojos por la razón correcta + 17 cotas) | `c89d432` |
| GREEN (gate, `COLUMNS`, regla, agentes) | `df5af77` |
| Fixture PC-5 (test-writer) | `0e0a9ce` |
| Review-fix F3/F4/F5/F9 | `84631f3` |
| Tests F1/F5/F7/F8 | `0dd044f` |
| Review | `docs/specs/008-005-ci-gate/review.md` |

- Módulo del gate: **19/19**; 5 archivos de cotas: **32 passed**; doctrina rc 0; Odoo 68/68.
- Control negativo de los tests nuevos contra `df5af77`: 3 fallan por la razón correcta (F3/F4/F5).
- Gate de cierre: ver «Gate».

## PCs y acreditación

| PC | Acreditación |
|---|---|
| 01 | Tests PC-1: orden, multiplicidad, `surface` sin ejecutar pytest |
| 02 | 8 casos de atribución fail-closed + `attribution.causes` |
| 03 | Fallos y skips con motivo completo; errores de colección nombrados con `stdout.log` |
| 04 | docs-only/README-only no ejecutan superficie; producto sin superficie = rojo que nombra la ruta |
| 05 | Hermético sin HOME/red/push; portabilidad por lectura y grep; pipeline real ejercido en el cierre |
| 06 | 17 sitios con par declarado; **pérdida declarada** en los 5 de «en la cota» |
| 07 | Raíces independientes; `gate.json` también en fallo de precondición e interno |
| 08 | Canario y carga visibles y no decisorios |

## Gate

`python3 scripts/cdad-suite.py close --evidence-root .cdad/local/008-005/evidence --all`

| Dato | Valor |
|---|---|
| Intento | `attempt-20261028T085622344866Z-2157456-1ac199cc` |
| Commit | `0dd044f` |
| Resultado | **1827 passed, 5 skipped, 0 failed, 0 errors** |
| `rc` | **0** |
| `verified` | **true** |
| Canario | **delta 0** |
| Duración | 49:55 |
| Carga del host | `loadavg` ~6 sobre 8 CPU durante toda la corrida (agentes ajenos) |
| Skips con motivo | **5/5** (antes 0/5: el fix de `COLUMNS` los completa) |

La corrida se hizo con `docs/.cdad-state.json` modificado por las transiciones de la propia unidad
(`dirty: 1`), como en los cierres anteriores. **La suite pasó verde con el host cargado** —el escenario que
en 008-004 produjo siete falsos rojos—, que es la primera evidencia de que el re-anclaje de cotas de PC-6
cumple su propósito.

La corrida **del gate** (`scripts/cdad-ci-gate.py`) sobre árbol limpio se registra con el cierre del epic:
tres corridas consecutivas verdes son criterio del epic (008-001/008-002), no de esta feature.

## Pérdida declarada (F1 del review)

En los cinco sitios cuya promesa es «responde/termina en la cota» (B3a, B3b, PD-7, PD-11 ×2) el techo
re-anclado mide el host, no la clase «espera acotada **por encima** de la cota»: el envelope del adaptador
no expone duración y la espera de la interfaz (cota + gracia) no se dispara con un exceso de 2×. Queda
registrada en `deferred-hardening`; restituirla exige un observable de duración en el producto (otra
unidad). Los textos de esos sitios ya no la presentan como guarda «en la cota».

## Límites declarados

- Sin runner, sin workflow versionado y sin publicación: `.github/**` y `Makefile` son `unclassified` en la
  política, así que versionar un workflow exige una enmienda del dueño. El gate es neutral de proveedor.
- Sin secretos: no lee credenciales ni configura entornos.
- Costo: una suite completa por corrida (46–103 min medidos). El criterio del epic se mantiene literal; la
  excepción docs-only sobre la corrida de la suite es decisión del dueño.
- `make validate` queda fuera del gate (necesita instalar agentes en un HOME real).

## Deuda y hallazgos operativos

- **Split-brain de continuidad (incidente, reparado a mano):** dos `begin` consecutivos del mismo intento,
  con un archivo de actualización mal nombrado, dejaron dos cabezas divergentes; el CLI no elige ganador por
  diseño. Se restauró la cabeza coherente (seq 15) desde el cuerpo íntegro, se retiraron los cuerpos
  huérfanos y se re-emitió el `begin`. Respaldo en
  `.cdad/executions/exec-008-005-ci-gate-001/continuity/head.json.split-brain-20261028.bak`.
- **Recibo durable no alcanzable en un paquete:** el `record` del review-fix del implementer se negó porque
  la spec se enmendó **después** del `begin`. El trabajo está en `84631f3` y verificado; el paquete se
  retiró. Regla operativa reforzada: **registrar antes de enmendar**.
- **Sin `make validate` en el gate:** F011 depende de una instalación real; tras el deploy del 2026-10-28
  pasa 68/68.
- **Costo por push:** declarado; su reducción es decisión del dueño.
