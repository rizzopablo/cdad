# Discovery — 008-002-suite-by-capability

## Superficie y criterio

Contrato y plan verificados por SHA-256; coinciden con el paquete. No existe una spec acreditada por este discovery. Base observada: `0cef470975b2a84f94c3e7f9a471a96e7bd456b8`.

Premisas del orquestador: **137.712 líneas / 205 módulos Python**, frente a 22.137 líneas de producto. El denominador incluye helpers: no debe presentarse como 205 módulos recolectados de tests.

Propongo **índice por capacidad + consolidación de contratos**, inicialmente conservando `tests/test_<capacidad>_<contrato>.py`. Frente a mover todo a subdirectorios, esta alternativa permite selección por capacidad sin romper de entrada imports ni el gate plano. No introducir otro framework de tests.

## Inventario mantener / fusionar / eliminar

Mapa inicial por familias, comprobado con docstrings de todos los `tests/*.py`; los módulos mixtos necesitan clasificación por test, no traslado ciego:

| Capacidad | Familias actuales — prefijos `test_` omitidos | Acción propuesta |
|---|---|---|
| Entrega y evidencia | `003_002_*`, `003_006_t3_*`, `005_012_t{1,4}_*`, `007_004_*`, `007_008_*` | Fusionar reviewfix por recepción, materialización y evidencia; mantener recorridos distintos. |
| Continuidad | `003_004_*`, `003_006_t4_*`, `003_007_t{1,2}_*`, `007_003_*` | Consolidar checkpoint/resume/reconcile; conservar reanclaje legado. |
| Despacho y recuperación | `005_009_*`, `005_010_*`, `006_001_*`, `006_005_u{1a,1b,2,4,5}_*`, `006_005_u6fix{1,4,5,6,8}_*`, `007_002_*`, `008_001_pc{7,8}_*` | Prioridad de consolidación por contrato: selección, señal durable, write-ahead, correlación y presupuesto. |
| Orientación y planificación | `003_003_*`, `003_006_t1_*`, `003_007_t4_*`, `004_003_*`, `005_001_*`, `005_002_*`, `005_003_*`, `005_006_*`, `005_007_*`, `005_011_t3_*`, `006_004_*`, `006_006_*`, `007_001_*` | Fusionar fixes dentro del contrato; conservar diferencias entre reglas documentales y comportamiento CLI. |
| Suspensión / retiro | `007_007_*` / `007_006_*` | Mantener contratos separados. |
| Paquetes, autoridad e identidad | `role_packet*`, `role_packets`, `packet_prepare`, `004_002_t{1,2,3,4}*`, `004_002_t34*`, `005_011_t1_*`, `005_012_t{2,3,5,6}_*`, `005_013_*`, `005_014_*`, `006_005_u1c_*`, `006_005_u7_*` | Consolidar por política, publicación, transición y proyección. |
| Generación, instalación y permisos | `004_001_*`, restantes `004_002_*`, `003_006_t2_*`, `005_004_*`, `005_005_*`, `005_008_*`, `006_002_*`, `006_003_*`, `006_005_u3*`, `006_005_u6fix7*`; módulos sin número de generación/adaptación/instalación/bash/read-map/static-ceiling | Mantener capacidad propia; repartir reviewfix mixtos por requisito. |
| Suite / aislamiento | `008_001_home_*`, `conftest`, `product_staging`, `pd10_permission_semantics`, `_rf2_open_pause` | Mantener infraestructura; helpers no son cobertura por sí mismos. |

**Eliminar:** ningún test autorizado todavía. `reviewfix` o `u6fix` identifica procedencia, no redundancia.

## Duplicación, oráculos y preservación

Hay solapamiento documentado de `model_reported`: `tests/test_006_005_u6fix6_model_parity.py:16-29,48-65` remite a pruebas anteriores, pero añade **paridad entre vías**; fusionar no significa eliminar ese caso. `test_006_005_reviewfix.py:30-59` registra oráculos corregidos y una enmienda: conservar esa genealogía en el mapa. El write-ahead mantiene escenarios únicos de caída y fallo cerrado (`test_006_005_u6fix5_write_ahead.py:62-92`).

Los oráculos documentales requieren revisión, no poda automática: `test_005_006_t4_readme.py:183-243` usa regex sobre prosa/nombres, pero acredita INV-6. **No se verificó ningún test sin PC vigente ni equivalencia de mutantes.** Aplicar el criterio de poda únicamente con evidencia: mismo fallo detectable, ningún requisito/variante único y mayor costo medido; sin prueba suficiente, mantener.

Mapa propuesto: **spec/enmienda + PC/PD/INV → nodeid original → variantes/oráculo → nodeid destino → procedencia review**. Auditar conjuntos antes/después y existencia de destinos recolectables; contar PCs solas no demuestra conservación de variantes.

## Lotes, riesgos y resultado utilizable

1. Inventario exhaustivo y mapa base, sin mover tests.
2. Suspensión y retiro, cada capacidad por separado.
3. Continuidad y entrega, separadamente.
4. Despacho por subcontrato.
5. Orientación; después paquetes y generación/permisos.

Extraer únicamente helpers realmente compartidos, sin importar clases recolectables accidentalmente. Hay dependencias concretas entre módulos (`test_007_003_legacy_reanchor.py:14-23`; `test_008_001_pc8_adapter_budget.py:49-53`). Preservar aislamiento y cachés de sesión (`conftest.py:80-126`; `product_staging.py:35-54`).

Cada lote valida colección, consumidores de helpers y subconjunto afectado. El gate actual **no basta para reorganizaciones**: usa cambios de producto comprometidos y busca sólo `tests/test_*.py` (`.cdad/local/surface-gate.sh:6-11`). Una migración sólo de tests puede quedar sin selección. No declarar estabilidad ni cobertura equivalente por ese resultado vacío. Suite completa: una vez por el closer al cierre, según paquete.

Dejar para después mutation testing completo, testmon y markers `req/tier`; tampoco migrar masivamente subprocesos a ejecución interna.

**PC candidatas para discutir, no aprobadas:**

1. Cada módulo Python del inventario tiene capacidad, tipo y decisión justificada.
2. Cada obligación acreditada conserva destino recolectable y variantes trazadas.
3. Toda eliminación identifica sustituto y evidencia de no perder un caso único.
4. Seleccionar una capacidad mediante CLI recolecta sus tests sin errores de imports.
5. Cada lote conserva el aislamiento y supera sus pruebas afectadas.
6. El informe antes/después contabiliza módulos y líneas con el mismo método, mostrando reducción efectiva sin umbral inventado.

Ganancia concreta: el test-writer localiza una PC existente antes de crear otra prueba; el orquestador obtiene un subconjunto explícito; un fallo muestra capacidad, contrato y procedencia.

**Evidencia operativa:** lecturas mediante `cat`, `nl -ba`, `rg`; inventario mediante Python `ast.parse`/`ast.get_docstring` sobre `tests/*.py`; verificaciones mediante `sha256sum`, `git rev-parse HEAD`, `git status --short`, `git diff --stat`. Hashes coincidentes indicados arriba. Sin tests ejecutados, archivos modificados ni commit propio. Estado preexistente conservado: `M docs/.cdad-state.json` (15 inserciones, 6 eliminaciones).
