---
feature_id: 016-001-contract-test-link
approved_by: Pablo (HITL delegada al orquestador, docs/epics/epic-016-traceability-and-suite-review/execution.md)
approved_at: 2026-11-03
source: architect draft (sesión <ses-345>), materializado por el orquestador (ADR-003)
decision: se aprueban el registro por unidad con marcadores optativos en contratos nuevos, el índice legacy por demanda, la colección independiente del runner y el verificador kind=review sin dispensar la promesa
---

# Spec: 016-001-contract-test-link

## 1. Descripción funcional

**Actor:** quien desarrolla o revisa una unidad CDAD.
**Objetivo:** recuperar qué compromiso protege un test y detectar compromisos sin verificador declarado.
**Punto de partida:** contrato aprobado y colección atribuible del proyecto, con o sin inventario vivo.
**Primer resultado útil:** un informe que identifica vínculos válidos, referencias rotas y promesas sin verificador, sin confundir esa comprobación con ejecución o pertinencia semántica.

La trazabilidad se incorpora a tests nuevos y, por demanda, a tests revisados. No exige reescribir contratos antiguos ni añadir tests equivalentes.

## 2. Contrato de datos

### Ubicación y responsabilidad

Registro convencional: `docs/specs/<unit-id>/contract-test-links.json`. La ruta se entrega explícitamente al validador
y a los paquetes pertinentes; no se descubre recorriendo todas las specs.

- El test-writer propone el delta como texto; el orquestador materializa el registro.
- GREEN no modifica registro, contrato ni verificadores.
- La revisión independiente contrasta pertinencia y suficiencia.
- Los tramos de revisión producen deltas en los registros de las unidades cuyos contratos protegen.

El inventario conserva clasificación; `pc-map` conserva genealogía. Este registro no duplica capacidad, confianza ni cadenas de sustitución.

### Forma mínima

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
- El contrato se identifica por ruta y hash de sus bytes. Un cambio de hash exige reconciliar el registro con el contrato aprobado, no actualizarlo automáticamente para obtener verde.
- `pc_ids` referencia obligaciones del contrato identificado. Una obligación admite varios verificadores; un verificador, varias obligaciones.
- `evidence` con cero o más referencias recuperables. Vacío significa **sin evidencia adjunta**, no «ejecutado».
- Una referencia documental tiene `path`, `sha256` y `locator`; `locator` es un fragmento literal no vacío que aparece una sola vez en el archivo identificado.
- Las rutas de referencias permanecen dentro del proyecto, también después de resolver symlinks.

### Obligaciones nuevas y contratos antiguos

Para contratos nuevos que adopten el registro, cada postcondición lleva un marcador estable: `<!-- cdad:pc PC-1 promise=A -->`.
Los marcadores forman el universo mecánico de obligaciones; cada ID aparece una sola vez; `promise` identifica su
agrupación observable. El texto de la promesa y de la postcondición permanece en la spec, no se copia al registro.

Para contratos antiguos sin marcadores se admite, por demanda:

```json
"legacy_obligations": [
  {"id": "PD-1", "promise": "entrega-correlacionada", "locator": "<fragmento literal único del contrato antiguo>"}
]
```

- Los identificadores históricos se conservan literalmente.
- No se mezclan marcadores e índice legacy para un mismo contrato.
- En modo legacy el informe declara que cubre **las obligaciones indexadas**, no que extrajo exhaustivamente el contrato.
- La revisión independiente contrasta esa selección. Las specs todavía no indexadas no se presentan como cubiertas.

La extracción y el informe sobre specs cerradas corresponden a **016-002**.

### Verificadores no automatizados

Se admite `"verifier": {"kind": "review", "reference": {"path", "sha256", "locator"}, "reason": "<por qué este método>"}`.
Declara otro método de verificación; **no dispensa la promesa** ni acredita automáticamente suficiencia. Una obligación
sin verificador sigue siendo un hueco; no existe un valor `excluded` que la convierta en satisfecha.

### Disposiciones y auditoría

Se consumen las disposiciones de R2 desde su hogar canónico, sin redefinirlas. Cuando el vínculo procede de una
revisión de mantenimiento, admite `audit_ref`, referencia recuperable al AUDIT que contiene la disposición.
El registro explica protección actual; el AUDIT conserva la decisión de mantenimiento; `pc-map` conserva genealogía
cuando corresponde. La selección y las condiciones de Sustituir/Consolidar no cambian.

## 3. Interfaz de validación

```sh
python3 <cdad-cycle>/scripts/cdad_contract_links.py validate \
  --project-root ROOT --registry REGISTRY --collection CURRENT.json [--baseline BASE.json]
```

No modifica archivos ni ejecuta tests.

### Colección admitida

`CURRENT.json` y `BASE.json` son resultados de colección real del runner declarado por el proyecto:
`{"revision", "command": [...], "scope": [...], "exit_code": 0, "nodeids": [...]}`.

- Los nodeids se comparan literalmente, incluidos parámetros.
- Una colección fallida no sirve para acreditar existencia.
- Con baseline, ambos artefactos declaran el mismo ámbito; los nuevos nodeids son `CURRENT − BASE`.
- Sin baseline se comprueban vínculos y huecos, pero el informe dice **«tests nuevos no comprobados»**.

El orquestador conserva comando y salida reales. El validador comprueba los artefactos recibidos; no autentica que un
tercero haya ejecutado el comando ni que la revisión declarada sea verdadera.

### Resultado

JSON con `status` (`ok`, `invalid`, `not_configured`), errores con archivo y referencia afectada, obligaciones y
promesas sin verificador, nodeids nuevos sin vínculo, ámbito comprobado y límites. Orden determinista.

Códigos: `0` sin defectos dentro del ámbito declarado o registro no configurado; `1` datos inválidos, referencias
rotas, huecos o tests nuevos sin vínculo; `2` uso inválido de la CLI.

Si la ruta explícita del registro no existe, devuelve `not_configured`, «sin registro de vínculos declarado», sin exigir
colecciones ni bloquear. Un registro presente pero corrupto no se trata como ausente.

## 4. Promesas y postcondiciones

### A — Recuperar el compromiso protegido
**PC-1.** Dado un registro válido, el resultado permite recuperar contrato y revisión por hash, obligación, promesa,
verificador y comprobación protegida. Admite muchos-a-muchos y reutilización de tests existentes.
**PC-2.** Si el contrato, una obligación, una referencia documental o un nodeid vinculado no resuelve contra los
insumos admitidos, la validación termina con `1` e identifica el vínculo afectado. Un hash distinto o una colección
fallida no obtiene verde.

### B — Ver huecos sin imponer cuotas
**PC-3.** Sobre todas las obligaciones obtenidas de marcadores, o sobre el índice legacy explícitamente acotado, el
resultado enumera las que carecen de verificador y las agrupa por promesa; su presencia produce `1`.
**PC-4.** Un test existente puede satisfacer varias obligaciones sin exigir tests adicionales. Un verificador de
revisión requiere motivo y referencia resoluble, pero el resultado no lo presenta como ejecución de test ni como
aceptación semántica.

### C — Aplicar el vínculo hacia adelante
**PC-5.** Con colecciones actual y baseline válidas del mismo ámbito, cada nodeid nuevo aparece vinculado o se informa
como nuevo sin vínculo con `1`. Sin baseline, esa comprobación queda explícitamente no realizada.
**PC-6.** En proyectos que adopten el registro, los handoffs legacy y por paquetes transmiten ruta, contrato, regla de
delta y comprobación aplicable. El test-writer entrega el delta y el orquestador lo materializa antes de la siguiente
transición. En entrada a Review y cierre se exige comprobación sobre los deltas y tests actuales; los resultados
intermedios se registran sin convertirse en gate de RED.

### D — Conservar compatibilidad y límites
**PC-7.** Un proyecto sin registro continúa su ciclo y obtiene el diagnóstico no bloqueante. La adopción no exige
inventario vivo, `pc-map` ni actualización masiva de contratos anteriores.
**PC-8.** Un resultado estructural verde declara su ámbito y no afirma pertinencia, ejecución, sensibilidad ni
aprobación. La entrega conserva separadas evidencia de ejecución y revisión independiente.

## 5. Invariantes verificables
- Validar no modifica contrato, registro, inventario, genealogía ni tests.
- Reordenar registros, vínculos o nodeids no cambia los conjuntos de defectos y huecos.
- Ningún vínculo se acredita contra un contrato con hash diferente.
- La ausencia de evidencia nunca se transforma en evidencia de ejecución.
- Un verificador compartido no genera una obligación de crear otro test.
- Las propiedades, si se ejercitan, usan presupuesto y semilla declarados conforme a R2.

## 6. Alcance de implementación
Dentro de `skills/`: CLI autónoma y referencia canónica del formato y su uso; plantilla de spec con marcadores
estables **cuando se adopta el registro**; referencias de TDD, handoffs y re-entry; consumidores de paquetes
pertinentes de AUDIT, RED, properties, E2E, POST-AUDIT y revisión.
Dentro de `tests/`: verificación observable de las promesas; fixtures de contratos nuevos y antiguos, colecciones y
registros.

No requiere modificar R2 ni generar reglas nuevas en `sources/`. La materialización documental del registro de esta
unidad corresponde al orquestador, fuera del write-scope de GREEN.

## 7. Criterios de aceptación
- Desde un contrato y colección válidos se obtiene un vínculo recuperable; al romper una referencia aparece el defecto.
- Al quitar el último verificador de una obligación aparece el hueco; compartir un test entre varias obligaciones no
  provoca exigencias adicionales.
- Un nodeid nuevo sin vínculo se detecta comparando colecciones.
- El ciclo sin registro sigue funcionando sin inventario específico de CDAD.
- Los tests nuevos de esta unidad quedan vinculados mediante delta y materialización del orquestador.
- Una sesión independiente contrasta contrato, vínculos, comprobaciones y límites antes de aceptar.

## 8. deferred-hardening
- Extracción general de Markdown histórico (se usa índice por demanda; no se promete extracción exhaustiva aquí).
- Autenticación criptográfica de colecciones y logs (se conserva atribución operacional y su límite explícito).
- Inferencia automática de pertinencia o sensibilidad (se mantiene revisión independiente).
- Rendimiento sobre todo el corpus y backfill masivo (el costo se mide en el primer tramo).

## 9. Fuera de alcance
Informe global de specs cerradas (016-002); ejecución y decisión del primer tramo (016-003); poda, normalización
retroactiva, gates universales, publicación o despliegue.

## Discovery (resumen del architect)
- El plan exige registro por unidad, separado del inventario y de la genealogía, sin backfill masivo.
- El inventario clasifica; `pc-map` conserva obligaciones, variantes y sustituciones; ninguno acredita protección semántica.
- Ya existe la separación operativa (test-writer devuelve delta como texto, el orquestador materializa; bloquea en
  Review y cierre, no en RED).
- R2 permite reutilizar verificadores y que un test proteja varias postcondiciones: el vínculo no puede ser cuota.
- El selector actual es específico de este repositorio; no conviene convertirlo en dependencia del producto instalable.

Decisión propuesta: registro JSON pequeño por unidad y validador instalable bajo `skills/cdad-cycle/`; recibe
colección del runner declarado por el proyecto; no introduce otro runner ni depende del inventario de CDAD.

## Evidencia del architect
Ruta C validada (render byte a byte, contrato y contexto v2). Revisión examinada `82644528`. Sin archivos modificados,
sin tests, sin commit.
