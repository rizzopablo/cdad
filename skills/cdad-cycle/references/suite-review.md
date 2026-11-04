# Revisión de suite por tramos — procedimiento del tramo (016-003)

Cómo congelar el tramo más nuevo de una colección y cómo comprobar la
fotografía que el orquestador materializa. Contrato en
`docs/specs/016-003-suite-review-tranche-1/spec.md` (PC-1..PC-10).
Herramienta: `skills/cdad-cycle/scripts/cdad_suite_review.py` (solo
lectura; el orquestador conserva las fotografías).

## Congelar (`select`)

Toma una colección válida del ámbito `["tests"]` y una revisión completa,
ordena cada nodeid por la antigüedad de incorporación de su módulo
(par `(timestamp, hash)` mínimo de
`git log --no-renames --diff-filter=A --format='%ct %H'`) con desempates
por ruta y nodeid literales, y recorta el primer quinto
(`(N+4)//5`). No sigue renombrados ni mira fechas del sistema de
archivos. La identidad literal incluye parámetros.

Entradas: `--project-root` (raíz con el checkout), `--revision` (revisión
completa a acreditar), `--collection` (JSON con `revision`, `command`,
`scope`, `exit_code` y `nodeids` literales).

Salida por stdout: revisión, identidad del insumo (ruta dada y sha256 de
sus bytes), regla aplicada, incorporaciones por módulo, total, tamaño y
lista ordenada del tramo.

Códigos: `0` tramo acreditado; `1` insumo o historial incompatible
(colección fallida, duplicados, revisión que no resuelve, módulo ausente
en la revisión, clon superficial, incorporación no recuperable, git no
disponible); `2` invocación mal formada.

## Comprobar (`validate`)

Revisa que el tramo materializado (`audit.json`, `costs.json`,
`decision.md`, `experiments/`) tenga exactamente una fila por nodeid
seleccionado, con comprobación, consecuencia, evidencia que resuelve,
disposición del vocabulario R2 vigente y motivo; que cada candidato
declare hipótesis, defecto concreto, comparación, revisiones, entorno,
comandos, presupuesto y resultado de los pasos, sin presentar lo acotado
como si autorizara poda; que el costo distinga actividades, sesiones y
comandos, marque métricas ausentes como no disponibles (nunca como cero)
y proyecte con fórmula, cantidades y supuestos; que la decisión nombre
responsable, autoridad, motivo, evidencia y alcance con un curso de
acción; y que los experimentos vivan en la copia y el workspace
declarados con el original intacto.

La disposición de cada fila pertenece al vocabulario R2 vigente
(Mantener, Extender, Sustituir, Consolidar, Añadir, Retirar); la forma
del registro de vínculos y su uso viven en `contract-test-links.md` y no
se repiten aquí.

Entradas: `--project-root`, `--tranche` (directorio del tramo),
`--selection` (lista literal del tramo, objeto con `selection`/`nodeids`/
`tranche` o lista directa), y `--registry REGISTRO.json` repetible para
contratos sin marcadores.

Sin `--registry`, el camino con marcadores queda idéntico al actual. Con
`--registry`, cada fila cuyo contrato no tiene marcadores reales `cdad:pc`
resuelve por índice legacy enlazado: se busca el registro cuyo
`contract.path` y `contract.sha256` coincidan exactamente con los de la
fila; la `obligation` debe existir en su índice y la `promise` de la fila
debe coincidir con la del índice. Si no hay registro enlazado, la
obligación no existe o la promesa difiere, la fila es error y nunca `ok`.
Un registro que declara índice para un contrato que sí tiene marcadores
es error de mezcla (016-001: no se mezclan), nombrando registro y
contrato. Un registro corrupto o con forma inválida es error nombrando el
archivo. La forma del registro vive en `contract-test-links.md` y no se
repite aquí.

Salida por stdout: `status` (`ok`/`invalid`) primero, luego selección,
conteos, entrega tripartita (estructural, ejecución registrada, revisión
independiente), límites y `errors` con archivo y referencia afectada.

Códigos: `0` tramo con forma válida; `1` forma inválida o original
tocado; `2` invocación mal formada.

## Límites

Comprobación de forma sobre entradas identificadas: no ejecuta pruebas,
no modifica archivos y no acredita pertinencia de la protección, acierto
de la disposición ni sensibilidad real de los experimentos. Sin git
disponible, la intactitud del original se ancla a la congelación (ninguna
fuente revisada posterior al archivo más nuevo del tramo) en lugar del
estado del checkout. Repetir con los mismos insumos produce los mismos
bytes. Ningún resultado de esta herramienta autoriza poda,
consolidación ni el tramo siguiente.
