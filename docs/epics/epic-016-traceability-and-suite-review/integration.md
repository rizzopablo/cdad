# Integración — epic-016-traceability-and-suite-review

- Features: `016-001-contract-test-link` (forma y validación mecánica del vínculo test→contrato→promesa),
  `016-002-gap-report` (informe reproducible de promesas sin verificador en specs cerradas) y
  `016-003-suite-review-tranche-1` (revisión del tramo 1 del 20 % con costo medido y decisión registrada).
  Las tres cerradas; ninguna publicada ni desplegada.
- **Suite completa de cierre (obligatoria por defecto, ADR-042):** gate atribuible `scripts/cdad-ci-gate.py`
  con `--base 116ef8cf` (el cierre del epic 015: el punto donde empezó el trabajo de este epic, 81 commits
  atrás), commit `4c543721`, árbol limpio: **1 989 passed, 0 failed, 5 skipped**,
  verde atribuible (`.cdad/local/gate-20261104T051729363892Z-3050014-fbd7fdcc`, ~71 min de reloj).
- **Primera corrida, declarada:** se lanzó con `--base origin/main` y salió roja por `surface-rc`.
  `origin/main` no es ancestro de la rama local: es una línea de publicación construida con squash (9 commits
  de release que la rama local no tiene, y 81 commits locales que la publicación no tiene), así que el diff
  contra esa base mezcló 593 rutas de divergencia previa al epic. Tres quedaron sin superficie: una nota de
  `findings/` (raíz que la política de rutas no clasifica) y dos artefactos de fixture
  (`tests/fixtures/003-007-legacy-store/.cdad/…`), que `surface` trata como superficie de producto por no ser
  `.py`. Ninguna de las tres la tocó este epic y la suite de esa corrida ya estaba verde (1 989 passed, 0
  failed, 5 skipped); el rojo era de clasificación, no de producto. Reejecutado con la base honesta del epic,
  el paso de superficie clasifica sólo el trabajo del epic y da rc 0.
- Skips (5): las cinco son integraciones reales que se habilitan por variables de entorno (`CDAD_CONTEXT_METER_REAL_STORE` + ids de sesión reales, `CDAD_OPENCODE_INTEGRATION=1`, o el recorrido Claude → OpenCode que corre el orquestador con el dueño). Ninguna es promesa de este epic y el gate las registra como omisiones declaradas, no como pases.

## Cómo se integran

- **Un formato, dos consumidores.** 016-001 define la forma del vínculo y su CLI autónoma
  (`cdad_contract_links.py`: códigos 0/1/2, JSON determinista, sin escribir ni ejecutar tests). 016-002 la usa
  para el informe de huecos; 016-003 la usa para los vínculos que produce cada tramo auditado.
- **La extensión nació de un defecto real.** Durante el tramo 1, 35 de los 36 módulos auditados pertenecían a
  contratos anteriores a los marcadores `cdad:pc`. El validador no resolvía sus obligaciones, así que se extendió
  con `--registry` repetible y resolución legacy por `contract.path` + `sha256` (RED `37af51dc`, fixture
  `34e628f4`, GREEN `81c6d0fd`), sin relajar los umbrales ni mezclar ambos universos.
- **Un solo dueño del dato.** El inventario vivo (008-002) sigue clasificando; el registro guarda el vínculo; el
  mapa de PC guarda genealogía. Ningún campo se duplica: 016-002 agrupa huecos por promesa leyendo obligaciones,
  no copiándolas.
- **La auditoría produce altas de vínculo, no un informe que se descarta.** El tramo 1 dejó 25 unidades con
  registro validado (26 registros del proyecto, 26/26 rc 0) y fusionó por unidad cuando un mismo contrato apareció
  en dos lotes (010-002 = B2b+B5; 007-006 = B3+B4), sin duplicar ni perder vínculos.

## Compatibilidad hacia atrás

Un proyecto sin registro sigue su ciclo y recibe el diagnóstico no bloqueante (016-001 **PC-7**), y el informe de
huecos puede producirse sin colección declarando «sin registro de vínculos declarado» (016-002 **PC-9**). Ninguna
de las tres features agrega un gate al ciclo normal, y sus verificadores están dentro de la suite completa de
arriba: la compatibilidad no se afirma, se mide.

## Estado del inventario vivo

`python3 scripts/cdad-suite.py validate` → `ok`: 1 994 nodeids, 238 módulos, 31 entradas de mapa. El módulo de la
revisión de tramos queda inventariado en la capacidad `suite-review-tranche` con sus 6 verificadores R-A..R-F y su
contrato; la ampliación se materializó en el POST-AUDIT de cierre (`94c86e80`).

## Lo que el epic no promete

- El tramo 1 es el 20 % **más nuevo** del inventario por construcción: no es una muestra aleatoria del resto y no
  autoriza extrapolación estadística.
- Cero candidatos **no** acredita que la suite no tenga redundancia: sólo declara que, con la lectura exigida por
  el contrato, no se identificó protección observable duplicada ni promesa irrecuperable en ese tramo.
- El costo experimental quedó **sin calibrar**: sin candidatos no hubo experimentos, y la ausencia de candidatos no
  se lee como costo experimental cero.
- El verde de la suite completa no convierte en resueltos los pendientes declarados en las closures de las tres
  features; siguen abiertos y así figuran en sus secciones de deuda.
