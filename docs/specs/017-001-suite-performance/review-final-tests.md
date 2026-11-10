# review-final-tests.md

## Veredicto

En los 17 archivos asignados **no encontré un debilitamiento de las promesas preexistentes** en el diff desde `c3c38c5d1a7f2d362bc026edf4863e1e1ca82c4d` hasta `1eb8a65d02ae30500f0a52b68cfc6f6b4ff15841`. Los asserts movidos conservan su condición; no observé skips o xfails nuevos, comparaciones relajadas ni aumentos de timeout.

Este dictamen se limita a las adaptaciones de tests asignadas. No constituye aprobación de la feature completa.

| Archivo | Juicio | Fundamento |
|---|---|---|
| `tests/conftest.py` | Legítima | `:99`, `:125`: marcas alrededor del aislamiento existente. |
| `tests/product_staging.py` | Legítima | `:63-101`: marcas de copia, generación y consulta; se conservan las ramas y la comprobación del manifiesto. |
| `tests/suite_operation_markers.py` | Nuevo; sin promesa anterior debilitada | `:116-173`: incorpora la costura de observación; no reemplaza asserts anteriores. |
| `tests/test_005_002_t3_application_privacy.py` | Legítima | `:347-355`: elige una raíz temporal escribible sin cambiar el escenario ni sus asserts. |
| `tests/test_006_002_u1_delegation_section.py` | Legítima | `:183-211`: instrumenta caché, copia y generación; conserva la comprobación de retorno y manifiesto. |
| `tests/test_006_004_u3_principle_single_source.py` | Legítima | `:627-631`, `:643-697`: cambia el fallback temporal e instrumenta la preparación; conserva los errores y hashes comprobados. |
| `tests/test_006_005_u4_single_entry.py` | Legítima | `:860-887`, `:899-921`: conserva la generación inicial y las dos regeneraciones contractuales con sus asserts. |
| `tests/test_007_002_dispatch_recovery.py` | Legítima | `:413-444`: instrumenta la construcción; conserva los asserts de publicación e identificadores activos. |
| `tests/test_007_003_continuity_at_edges.py` | Legítima | `:496-521`: conserva `assert_rc0` y la comprobación de identificadores, dentro de las marcas. |
| `tests/test_009_001_installer_agent_overlay.py` | Legítima | `:32-45`, `:182-188`: extrae el mismo subprocess de validación, con el timeout de 300 s existente y los asserts intactos. |
| `tests/test_010_002_documentary_role_integration.py` | Legítima | `:1139-1151`, `:1173-1196`: instrumenta regeneración e instalación; conserva la comprobación de tipo y resultados. |
| `tests/test_010_002_documentary_role_properties.py` | Legítima | `:381-390`, `:437-480`: envuelve subprocesses y extrae la instalación equivalente. |
| `tests/test_010_004_t5_e2e.py` | Legítima | `:256-262`: mueve la raíz descartable fuera del checkout; no modifica los asserts del recorrido instalado. |
| `tests/test_012_installer_ignore_pycache.py` | Legítima | `:74-84`: marca la invocación existente del instalador sin cambiar argumentos ni resultado. |
| `tests/test_install_ownership.py` | Legítima | `:90-100`: marca la invocación existente del instalador sin cambiar argumentos ni resultado. |
| `tests/test_install_review5_regressions.py` | Legítima | `:157-167`: marca la invocación del instalador y conserva las variables adicionales. |
| `tests/test_role_packet_render.py` | Legítima | `:63-71`: marca la invocación CLI sin cambiar sus argumentos ni resultado. |

## Evidencia y límites

- Validé la solicitud y el paquete mediante `python3 scripts/cdad_packet.py validate-request` y `validate-packet`: ambos terminaron con **rc 0**. `render --route C` produjo la identificación recibida.
- Ejecuté `git diff --no-ext-diff c3c38c5d1a7f2d362bc026edf4863e1e1ca82c4d -- <los 17 archivos asignados>` y examiné los hunks. Un filtro adicional sobre asserts, skips, xfails y timeouts mostró asserts reindentados y el timeout existente trasladado al helper.
- No modifiqué archivos ni creé commits. El checkout ya mostraba `docs/.cdad-state.json` modificado y `docs/specs/017-001-suite-performance/review-final-001.md` sin seguimiento.
- **Suite completa no realizada**: esta unidad solicitó una auditoría estática acotada; tampoco ejecuté una selección focal. El registro de progreso menciona corridas anteriores, pero no las acredité independientemente.

## Abstentions

- No dictamino sobre la corrección general del runner, la fidelidad de las métricas, la seguridad del paralelismo ni los demás archivos del diff: corresponden a un alcance distinto.
- No acredito mediante ejecución que las marcas sean neutras en todos los entornos; el juicio de esta unidad se basa en el diff y en la conservación visible de las comprobaciones.
