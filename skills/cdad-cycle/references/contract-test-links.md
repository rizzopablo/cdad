# Vínculos contrato↔test — referencia canónica de formato y uso (016-001)

Hogar canónico del formato del registro y de su uso. El contrato es
`docs/specs/016-001-contract-test-link/spec.md` (PC-1..PC-8); este archivo es
su referencia operativa y no lo sustituye.

## Ubicación y responsabilidad

Registro convencional: `docs/specs/<unit-id>/contract-test-links.json`. La
ruta se entrega explícitamente al validador y a los paquetes pertinentes; no
se descubre recorriendo todas las specs.

- El test-writer propone el delta como texto; el orquestador materializa el
  registro.
- GREEN no modifica registro, contrato ni verificadores.
- La revisión independiente contrasta pertinencia y suficiencia.
- Los tramos de revisión producen deltas en los registros de las unidades
  cuyos contratos protegen.

El inventario conserva clasificación; `pc-map` conserva genealogía. Este
registro no duplica capacidad, confianza ni cadenas de sustitución.

## Forma mínima

```json
{
  "schema_version": 1,
  "unit": "example-unit",
  "contract": {"path": "docs/specs/example-unit/spec.md", "sha256": "<sha256 del contrato aprobado>"},
  "links": [
    {
      "pc_ids": ["PC-1", "PC-2"],
      "verifier": {"kind": "test", "nodeid": "tests/test_example.py::test_observable_promise"},
      "protects": "Resultado observable que comprueba el verificador.",
      "evidence": [],
      "limits": "Declarado; ejecución y pertinencia aún no acreditadas."
    }
  ]
}
```

Reglas:

- `unit`, `pc_ids`, `protects` y `limits` contienen valores no vacíos.
- El contrato se identifica por ruta y hash de sus bytes. Un cambio de hash
  exige reconciliar el registro con el contrato aprobado, no actualizarlo
  automáticamente para obtener verde.
- `pc_ids` referencia obligaciones del contrato identificado. Una obligación
  admite varios verificadores; un verificador, varias obligaciones.
- `evidence` con cero o más referencias recuperables. Vacío significa **sin
  evidencia adjunta**, no «ejecutado».
- Una referencia documental tiene `path`, `sha256` y `locator`; `locator` es
  un fragmento literal no vacío que aparece una sola vez en el archivo
  identificado.
- Las rutas de referencias permanecen dentro del proyecto, también después de
  resolver symlinks.

## Marcadores estables y legado

Para contratos nuevos que adopten el registro, cada postcondición lleva un
marcador estable: `<!-- cdad:pc PC-1 promise=A -->`. Los marcadores forman el
universo mecánico de obligaciones; cada ID aparece una sola vez; `promise`
identifica su agrupación observable. El texto de la promesa y de la
postcondición permanece en la spec, no se copia al registro.

Regla de extracción (el formato se define una sola vez en el párrafo
anterior): el universo de obligaciones son los marcadores reales, es decir
la línea cuyo contenido sea exactamente el marcador (se admite espacio en
blanco alrededor), fuera de bloques de código cercados (``` y ~~~) y fuera de code
spans inline. Un ejemplo del marcador en la prosa —inline o en bloque
fenced— no es una obligación y nunca produce un hueco fantasma.

Para contratos antiguos sin marcadores se admite, por demanda:

```json
"legacy_obligations": [
  {"id": "PD-1", "promise": "entrega-correlacionada", "locator": "<fragmento literal único del contrato antiguo>"}
]
```

- Los identificadores históricos se conservan literalmente.
- No se mezclan marcadores e índice legacy para un mismo contrato.
- En modo legacy el informe declara que cubre **las obligaciones indexadas**,
  no que extrajo exhaustivamente el contrato.
- La revisión independiente contrasta esa selección. Las specs todavía no
  indexadas no se presentan como cubiertas.

## Verificadores no automatizados

Se admite `"verifier": {"kind": "review", "reference": {"path", "sha256", "locator"}, "reason": "<por qué este método>"}`.
Declara otro método de verificación; **no dispensa la promesa** ni acredita
automáticamente suficiencia. Una obligación sin verificador sigue siendo un
hueco; no existe un valor `excluded` que la convierta en satisfecha.

## Colección admitida

`CURRENT.json` y `BASE.json` son resultados de colección real del runner
declarado por el proyecto:
`{"revision", "command": [...], "scope": [...], "exit_code": 0, "nodeids": [...]}`.

- Los nodeids se comparan literalmente, incluidos parámetros.
- Una colección fallida no sirve para acreditar existencia.
- Con baseline, ambos artefactos declaran el mismo ámbito; los nodeids nuevos
  son `CURRENT − BASE`.
- Sin baseline se comprueban vínculos y huecos, pero el informe dice
  «tests nuevos no comprobados».

El orquestador conserva comando y salida reales. El validador comprueba los
artefactos recibidos; no autentica que un tercero haya ejecutado el comando ni
que la revisión declarada sea verdadera.

## Resultado y códigos

JSON con `status` (`ok`, `invalid`, `not_configured`), errores con archivo y
referencia afectada, obligaciones y promesas sin verificador, nodeids nuevos
sin vínculo, ámbito comprobado y límites. Orden determinista.

Códigos: `0` sin defectos dentro del ámbito declarado o registro no
configurado; `1` datos inválidos, referencias rotas, huecos o tests nuevos sin
vínculo; `2` uso inválido de la CLI.

Si la ruta explícita del registro no existe, devuelve `not_configured`, «sin
registro de vínculos declarado», sin exigir colecciones ni bloquear. Un
registro presente pero corrupto no se trata como ausente.

## Forma del payload

El resultado declara qué universo cubrió y qué obligaciones contiene:

- `mode`: `markers` (universo mecánico de marcadores reales del contrato)
  o `legacy` (universo acotado al índice legacy del registro).
- `obligations`: lista ordenada por `id`; cada entrada trae `id`,
  `promise` y `verifiers` (lista de verificadores vinculados que pasaron
  la comprobación; vacía cuando la obligación es un hueco).
- `coverage`: en modo `legacy` declara que cubre **las obligaciones
  indexadas**, no una extracción exhaustiva del contrato; en modo
  `markers` declara el universo mecánico.
- Un contrato sin marcadores ni índice legacy, con registro presente,
  da `invalid` con diagnóstico explícito («no declara obligaciones»),
  nunca `ok`.

## Comprobación aplicable (PC-6)

En proyectos que adopten el registro, los handoffs legacy y por paquetes
transmiten ruta del registro, contrato, regla de delta y comprobación
aplicable. El test-writer entrega el delta y el orquestador lo materializa
antes de la siguiente transición. En entrada a Review y cierre se exige
comprobación sobre los deltas y tests actuales; los resultados intermedios se
registran sin convertirse en gate de RED. Detalle de transporte en
`references/handoff-prompts.md`, de subfase en `references/stage-3-tdd.md` y
de re-entry en `references/re-entry.md`.

## Consumidores por paquete

AUDIT, RED, properties, E2E, POST-AUDIT y revisión consumen esta referencia
por puntero cuando el proyecto adopta el registro; ningún paquete copia su
formato. La plantilla de spec (`assets/spec-template/spec.md`) la cita solo
como sección optativa al adoptar el registro.

## Interfaz de validación

```sh
python3 <cdad-cycle>/scripts/cdad_contract_links.py validate \
  --project-root ROOT --registry REGISTRY --collection CURRENT.json [--baseline BASE.json]
```

No modifica archivos ni ejecuta tests.

## Límites declarados

Un resultado estructural verde declara su ámbito y no afirma pertinencia,
ejecución, sensibilidad ni aprobación. La entrega conserva separadas
evidencia de ejecución y revisión independiente.

## Informe de huecos (gap-report, 016-002)

Subcomando propuesto por `docs/specs/016-002-gap-report/spec.md`
(PC-1..PC-10); esta sección es su referencia operativa y no sustituye al
contrato. No crea gates: el ciclo normal no adquiere comprobaciones nuevas
por adoptar este informe.

### Interfaz

```sh
python3 <cdad-cycle>/scripts/cdad_contract_links.py gap-report \
  --project-root ROOT --state STATE.json \
  [--registry UNIT=REGISTRY.json ...] [--collection CURRENT.json] \
  [--exclusions EXCLUSIONS.json]
```

- `ROOT` es el proyecto; toda ruta relativa se interpreta respecto de él y
  debe permanecer dentro del proyecto después de resolver symlinks.
- Los registros se entregan explícitamente como `UNIT=RUTA`, igual que el
  registro único de `validate` pero nombrados por unidad; no se descubren
  recorriendo las specs. Reordenar los vínculos no altera el resultado.
- `CURRENT.json` conserva el formato de colección admitida descrito arriba
  (revisión, comando, ámbito, `exit_code`, `nodeids`). Se requiere cuando se
  procesa al menos un registro; sin registros el informe se produce sin
  colección.
- No se recibe baseline: este informe no comprueba altas de tests.
- La CLI produce JSON por stdout y no modifica archivos ni ejecuta tests.

Códigos: `0` informe producido con entradas válidas (puede listar huecos,
exclusiones o contratos no indexados); `1` datos presentes inválidos o
referencias rotas (resultado explícitamente parcial); `2` uso inválido de
la CLI. Esto no cambia los códigos ni el comportamiento de `validate`.

### Entradas y universo

- Estado CDAD con `epic_features[]` y `epic_history[].epic_features[]`; la
  fila actual tiene precedencia sobre sus copias históricas.
- Cada unidad `done` entra al universo con su evidencia de cierre
  (`closure_evidence` con ruta y hash que resuelven y coinciden) y su
  `docs/specs/<unit>/spec.md`. Una fila `done` sin evidencia queda fuera
  como cierre no registrado; una evidencia declarada rota produce `1`.
- Las demás filas quedan fuera del universo en `out_of_universe` con
  `unit`, `status` y `reason` recuperables (incluida la fila actual
  `in-progress`); no entran al universo.
- Filas actuales duplicadas para la misma unidad se tratan como
  ambigüedad igual que el caso histórico: si son equivalentes se
  deduplican, si son incompatibles no se elige ninguna y produce `1`.
- Obligaciones: marcadores reales o `legacy_obligations` del registro, sin
  mezclar; sin ambos, la spec queda como no indexada. Un registro presente
  sin vínculos no acredita cobertura.
- El informe identifica cada entrada usada con ruta relativa y hash, el
  universo admitido con spec y cierre por unidad, y el modo de indexación
  con su límite de cobertura por contrato.

### Exclusiones justificadas

Archivo opcional con `{"schema_version": 1, "exclusions": [...]}` donde
cada entrada declara `unit`, `contract{path, sha256}`, `promise` y `reason`
no vacío. La exclusión válida aparta la promesa completa a su sección con
motivo, archivo, hash y localizador recuperables; la inválida produce `1`
sin suprimir el hueco. Nunca crea verificadores ni protección. No se
admiten varias exclusiones para la misma unidad y promesa: si hay más de
una, no se aplica ninguna, todas se marcan inválidas y el hueco subyacente
se conserva en `gaps`. El orquestador materializa las exclusiones
autorizadas conforme a la decisión; GREEN no escribe este archivo para
obtener un resultado favorable.

### Salida y límites

JSON determinista con versión del formato, estado, entradas, universo y
alcance, cierres no registrados, unidades fuera del universo, unidades
inválidas con diagnósticos por ubicación y código, índice por contrato,
obligaciones con disposición única (`declared`/`gap`/`excluded`) y sus
verificadores, huecos agrupados por unidad y promesa, no indexadas,
excluidas y límites. Orden estable; sin hora, rutas absolutas ni
identificadores aleatorios. Los diagnósticos muestran las rutas relativas
a ROOT cuando es posible o `<fuera del proyecto>`; con dos vínculos del
mismo contenido se conserva la ruta menor en orden lexicográfico, por lo
que reordenar los vínculos no altera el resultado.

Materialización: stdout es el producto. Una fotografía versionada la
conserva el orquestador con su comando y su revisión, sin que la CLI
escriba el archivo.

Límites: comprobación estructural a partir de entradas identificadas; no
ejecuta tests ni modifica archivos; producir el informe no acredita
protección de los contratos. Detalle de transporte en
`references/handoff-prompts.md`, de subfase en
`references/stage-3-tdd.md` y de re-entry en `references/re-entry.md`.

## Tramos de revisión (016-003)

El selector congelado y la comprobación estructural del tramo viven en
`references/suite-review.md` (herramienta
`scripts/cdad_suite_review.py`). Los deltas de vínculos que un tramo
acredite se proponen como texto y los materializa el orquestador en los
registros de las unidades protegidas, con la forma de este archivo.
