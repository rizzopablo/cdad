# review-T2-002 — Revisión focal de T2

**Revisión examinada:** `27a07239026b1e459fbbd9e955a4932dd40f1c44` (HEAD).  
**Dictamen:** **T2 no pasa el gate**. Se verificaron las correcciones de captura y los seis recorridos calibrados, pero el registro todavía compromete intervalos que no fueron calibrados. No es una aprobación: la decisión corresponde al responsable.

## Hallazgo 1 — La calibración deja sin ejercitar operaciones que el registro compromete

**Severidad:** Required  
**Verdict:** BLOCKING · **Bucket:** m

**Evidencia.** `performance/operation-scope.json:7-9` establece `state: comprometida` como valor por defecto. La familia `portable-product-staging` no lo reemplaza y declara `product.lookup`, `product.copy` y `product.generate`, con expectativas para `C-P-cold` y `C-P-present` (`operation-scope.json:246-289`). Las dos selecciones son verificadores propuestos, no existentes (`:79-106`).

Sin embargo, `performance/calibration.md:77-85` indica que ninguna de esas selecciones se ejecutó, trata la familia como parcialmente desconocida y concluye que la evidencia puede consumirse en T3/T4. La spec exige calibrar **todos los intervalos comprometidos** antes de la base y no permite convertir retrospectivamente una ausencia en desconocimiento para aceptar la calibración (`spec.md:235-248,314-324`).

**Consecuencia.** Quien consuma el registro encontrará operaciones comprometidas sin evidencia focal que acredite sus ramas, límites y anidamiento. La regla de no atribuirles costo es prudente, pero no resuelve la contradicción entre el alcance registrado y la conclusión de la calibración.

**Cierre verificable.** Reconciliar el alcance con la autoridad competente, sin reclasificar retroactivamente una captura fallida para obtener aceptación. Calibrar las operaciones que permanezcan comprometidas mediante selecciones reales que ejerzan sus ramas y conservar el contraste esperado/observado; para cualquier desconocido admisible, registrar explícitamente su parte, motivo y regla de decisión conforme a la spec. Actualizar la conclusión de `calibration.md` según la evidencia resultante.

## Contrastes efectuados

- **Recorridos reales:** examiné los `profile.json` y XML crudos de C-R, C-E, C-U1, C-U3, C-U4 y C-D. Los perfiles contienen respectivamente **5, 8, 7, 9, 10 y 15** intervalos, con estado `complete`. Los conteos publicados para esas selecciones coinciden con los perfiles; en C-D también aparecen una `u3.copy` y una `u3.initial-generate`, como exige el registro. Los IDs son únicos dentro de cada perfil, los padres referenciados existen y contienen temporalmente a sus hijos, y todas las terminaciones son `ok`. Los XML contienen 1, 1, 2, 2, 2 y 3 casos, respectivamente, en correspondencia numérica con los nodeids de fases.
- **P5:** el diagnóstico consulta selecciones tanto de familia como de operación (`scripts/cdad-suite.py:995-1054`). La focal incluye contraste con selección ajena y sin selección.
- **P6:** la focal reproduce el layout ambiguo bare/paquete, exige captura y conserva el contraste sin marcas.
- **Desconocidos:** la calibración no presenta como tiempo medido las esperas ni el subcosto de `.cdad`; el registro contiene reglas para detener una decisión dependiente de esos costos (`operation-scope.json:479-526,561-567`). El problema de C-P es la contradicción de estado descrita arriba.
- **Conservación:** contrasté los diffs de los helpers y tests instrumentados respecto de `05b58cc4`. No identifiqué poda de aserciones ni sustitución de las transiciones revisadas; además de los envoltorios, aparece el cambio declarado de `_temp_root`.
- **Decisiones vigentes:** las rutas citadas en la tabla existen. No concluí la clasificación completa de todos los ADR no indexados.

## Verificación independiente

| Comando | Resultado |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py tests/test_017_001_suite_profile.py tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` | `72 passed in 78.13s`; rc 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py` | `2 passed in 1.06s`; rc 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` | `status: ok`; 2019 nodeids; timing `pending`; rc 0 |

No ejecuté la suite completa. No modifiqué archivos ni generé commits; `docs/.cdad-state.json` ya figuraba modificado al inicio.

## Abstentions

- No acredito la fidelidad de `product.lookup/copy/generate` en C-P-cold ni C-P-present: no existe la calibración focal correspondiente.
- No verifiqué exhaustivamente la fidelidad semántica de cada línea de todos los diffs ni todas las rutas excepcionales del observador.
- No verifiqué de forma completa la correspondencia entre cada ADR no indexado y su estado vigente o propuesto.
- La evidencia de volumen declarada para las copias (`operation-scope.json:529-560`) no fue contrastada contra manifiestos de origen y destino; la cifra de `calibration.md:81` no se usa aquí como prueba de costo temporal.
