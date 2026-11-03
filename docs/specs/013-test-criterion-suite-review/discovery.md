# Discovery — 013-test-criterion-suite-review

**Borrador para decisión del dueño; no es una spec ni una aprobación.**

## Alcance y método

Inspección del repo anidado, en `HEAD 0eab565c0f262a3411489c5a822466c86d1ed8e8`. Vía **legacy**, solo lectura del producto.

Se utilizaron `cdad-suite.py validate/list/measure`, colección de pytest e inspección dirigida. La única ejecución de tests comprendió **cinco archivos**, con corte preventivo a 560 segundos: terminó normalmente en **252,25 s**.

No se ejecutaron la suite completa, `make validate` ni el instalador. Los resultados temporales no constituyen un artefacto durable: las mediciones relevantes se reproducen abajo.

---

## A. Hallazgos

### 1. El criterio canónico ya rechaza la acumulación por cobertura

R2 selecciona por promesa observable, permite proteger varias postcondiciones con un test y prohíbe multiplicar resultados equivalentes. También exige declarar «sin este test, el usuario…» (`sources/roles/test-writer.md:82-108`).

R4 exige registrar esa consecuencia antes de aprobar RED; sus promociones excepcionales requieren motivo (`sources/roles/orchestrator.md:313-325`). R7 impide que reducir redundancia reduzca las garantías comprometidas (`skills/cdad-cycle/references/stage-3-tdd.md:27-43`).

**Consecuencia:** no hace falta inventar otra doctrina general. Hace falta volver coherente su aplicación y comprobar la **contribución del test respecto de los que ya existen**.

Hay evidencia de aplicación útil: el cierre de integración del epic 010 reutilizó 26 nodos decisivos y agregó **cero tests** porque no faltaba verificación testable (`docs/activeContext.md:140-144`).

### 2. Persisten instrucciones operativas que empujan hacia postcondición→test

Aunque la selección canónica es por promesa:

- El paquete RED pide un test para «the assigned postcondition» (`skills/cdad-cycle/packets/substages/test-writer-red.md:1`).
- El resumen del ciclo ejemplifica la unidad como «one postcondition, one test» (`skills/cdad-cycle/SKILL.md:204`).
- El handoff conserva nombres y commits por postcondición, y su regla final prescribe «one postcondition per test-writer» (`skills/cdad-cycle/references/handoff-prompts.md:401-406,714`).
- Re-entry continúa con la postcondición N+1 (`skills/cdad-cycle/references/re-entry.md:318-322`).

El gate «cada postcondición tiene al menos un test» **no obliga matemáticamente** a tests distintos: admite muchos-a-uno. El problema es su combinación con esos ejemplos y unidades operativas, que favorece interpretarlo como cuota (`skills/cdad-cycle/SKILL.md:354-355`).

El verificador doctrinal busca la expresión literal retirada «one test per … postcondition», pero no demuestra ausencia de instrucciones semánticamente equivalentes (`scripts/cdad-doctrine-check.py:117-136`). Su propio límite declara que verifica presencia, no suficiencia semántica (`:29-35`).

### 3. Existe retiro por desaparición del comportamiento, pero falta un procedimiento explícito para retirar redundancia

No sería correcto afirmar que nunca se eliminan tests: POST-AUDIT ordena borrarlos cuando desaparece el comportamiento (`skills/cdad-cycle/references/handoff-prompts.md:304-309`).

Sin embargo:

- AUDIT clasifica modificaciones, incorporaciones, intactos y riesgos, sin una disposición explícita de consolidación o sustitución (`skills/cdad-cycle/packets/substages/test-writer-audit.md:1`).
- POST-AUDIT exige dejar exactamente intactos los declarados como tales (`skills/cdad-cycle/packets/substages/test-writer-post-audit.md:1`).
- La plantilla enumera tests nuevos e intactos, pero no ofrece un registro equivalente para redundantes sustituidos (`skills/cdad-cycle/assets/spec-template/test-audit.md:66-87`).

**Diagnóstico:** la entrada tiene controles de pertinencia; el mantenimiento conserva por defecto. Falta una salida ordinaria y segura para un test cuya obligación sigue vigente, pero ya está mejor protegida por otro.

### 4. Dos skills cargadas por los roles conservan criterios incompatibles

`cdad-spec-and-test`:

- Declara inútil cualquier test que no corra en menos de 30 segundos (`skills/cdad-spec-and-test/SKILL.md:80-85`).
- Resume el cierre como «todos pasan → Merge» (`:65-78`).
- Presenta otra numeración de gates y `spec.yaml` (`:95-102`).

Eso no coincide con la aceptación contractual, la revisión independiente ni los gates del ciclo. La duración sola no determina la utilidad de una garantía.

Además, R2 fija **100–1000 entradas por propiedad** y stage 3 exige al menos 100, mientras la skill Odoo prescribe por defecto **8–10**, como calibración y no semántica:

- `sources/roles/test-writer.md:99-102`
- `skills/cdad-cycle/references/stage-3-tdd.md:225-233`
- `skills/odoo-test-writer/SKILL.md:141-147`

La muestra de código confirma que el número de tests tampoco describe su trabajo: un módulo de siete tests declara presupuestos internos de 100 publicaciones, 100 discordancias estáticas y 100 contextuales (`tests/test_010_002_documentary_role_properties.py:25-31,108-114`). **No se midió su duración.**

### 5. El inventario actual no acredita trazabilidad semántica de toda la suite y, además, está desactualizado

`validate` devuelve **rc=1**: quedan **18 módulos y 158 nodeids** sin asignación de capacidad/contrato.

Ejemplos: `test_008_002_suite_evidence.py`, `test_010_002_documentary_role_integration.py` y `test_012_installer_ignore_pycache.py`.

Hay que distinguir:

1. **Asignación inventariada:** capacidad y referencia de contrato.
2. **Trazabilidad acreditada:** obligación, variante observable y test que efectivamente la protege.

El cierre de 008-002 ya declaró que la segunda cubría únicamente su piloto de 17 nodeids; fuera del piloto había clasificación, no trazabilidad obligación→test (`docs/specs/008-002-suite-by-capability/closure.md:79-85`).

El mapa actual contiene 29 registros: 27 acreditados y dos `VERIFY`. **No son 29 tests ni el mapa completo de los 1937.**

Por tanto, esta revisión no puede dar honestamente una cantidad global de «tests sin promesa». Sí acredita la brecha del inventario y el alcance limitado del mapa.

### 6. Se reutilizan helpers, pero muchos tests vuelven a recorrer los preparativos CLI

Ejemplos medidos e inspeccionados:

- `_RecoveryProject` construye el proyecto y ejecuta `prepare` en su constructor (`tests/test_007_002_dispatch_recovery.py:409-426`).
- `_Project` hace lo mismo para continuidad (`tests/test_007_003_continuity_at_edges.py:490-512`).
- Sus consumidores los importan y extienden: retiro usa los fixtures de recuperación y suspensión; entrega usa los de continuidad (`tests/test_007_006_withdraw_and_republish.py:91-106`; `tests/test_007_004_termination_not_success.py:17-28`).

La matriz de flags ajenos repite construcción, `prepare`, consulta de ayuda, snapshots y rechazo para **21 variantes** (`tests/test_007_006_withdraw_and_republish.py:142-165,1250-1269`). Su coste medido conjunto fue **21,879 s**.

Esto acredita **repetición del recorrido preparatorio**, no redundancia semántica de las 21 obligaciones. La interfaz comprometida enumera los flags rechazados; no se autoriza eliminarlos por compartir `rc=2`.

### 7. Hay candidatos de consolidación, pero no un lote acreditado como eliminable sin sustitución

Ejemplo concreto: los dos tests B1 de colisión de 005-013 repiten publicación, edición de alcance e intento de colisión:

- Uno protege rechazo, diagnóstico y conservación de bytes (`tests/test_005_013_t1_unit_projection.py:1117-1166`).
- Otro agrega despacho previo y receivabilidad posterior (`:1169-1223`).

**No son equivalentes hoy.** Ninguno sustituye íntegramente al otro. Son candidatos a un recorrido consolidado que conserve ambos conjuntos de aserciones, sujeto a contraste independiente de los estados ejercitados.

Su coste conjunto fue **1,919 s**: es coste observado, **no ahorro demostrado**. Tampoco parece el primer objetivo si se prioriza tiempo.

El precedente de 008-002 demuestra una poda acreditada, pero también sus límites: fusionó un caso y el piloto terminó con **más bytes y líneas**, declarado sin ocultarlo (`docs/specs/008-002-suite-by-capability/closure.md:12-13,44-46`). Reducir cantidad no equivale automáticamente a simplificar ni acelerar.

### 8. Los oráculos sobre prosa tienen una función válida, pero no prueban conducta ni verdad semántica

El módulo documental 010-001 usa vocabularios y ventanas de proximidad para detectar conceptos (`tests/test_010_001_documentary_contracts.py:200-203,486-550`). Su límite declara correctamente que esas comprobaciones son estructurales, no prueba de fidelidad o suficiencia (`:120-123`).

Asimismo, `cdad-doctrine-check.py` comprueba marcadores y artefactos, no si la consecuencia de usuario declarada es verdadera.

**No corresponde eliminar todos los tests textuales:** el texto normativo distribuido también es producto observable. Corresponde separar:

- presencia, distribución y forma;
- comportamiento de los CLI;
- revisión semántica independiente.

La norma documental ya exige esa separación (`skills/cdad-cycle/references/documentary-contracts.md:151-164`). Añadir más sinónimos al detector no sustituye la revisión de significado.

---

## B. Mediciones y procedencia

### Inventario actual

Comandos ejecutados desde la raíz del repo:

```text
python3 scripts/cdad-suite.py measure
python3 scripts/cdad-suite.py validate
python3 scripts/cdad-suite.py list --capability <capacidad>
python3 -m pytest --collect-only -q -p no:cacheprovider tests
```

| Medición | Resultado | Procedencia |
|---|---:|---|
| Python / pytest | 3.13.5 / 8.3.5 | Comandos de versión |
| Tests recolectados | 1937 | `1937 tests collected in 2.92s` |
| Archivos con nodeids | 224 | Agrupación de colección por ruta |
| Python versionados bajo `tests/` | 230 | `measure`: 224 test, 5 helper, 1 bootstrap |
| Tamaño de esos Python | 7.162.922 bytes; 156.367 líneas LF | `measure` |
| Inventario declarado | 212 módulos | Lectura del inventario: 206 test, 5 helper, 1 bootstrap |
| Unión seleccionable por capacidades | 1779 nodeids | Unión de los nueve `list` |
| Fuera de esa unión | 158 nodeids, 18 archivos | Diferencia con colección; coincide con diagnóstico de `validate` |
| Integridad | `rc=1` | `validate`: módulos y nodeids sin inventariar |
| `pytest-xdist` instalado | No | `importlib.util.find_spec("xdist") → None` |

El dato recibido de 223 archivos no se reproduce con la definición «rutas con nodeids»: hoy son **224**. No se presupone la causa de esa diferencia.

### Selección actual por capacidad

Son selecciones del inventario existente, **no particiones exhaustivas**: cuatro nodeids pertenecen a más de una capacidad.

| Capacidad | Nodeids | Archivos |
|---|---:|---:|
| delivery-evidence | 230 | 24 |
| continuity | 113 | 15 |
| dispatch-recovery | 284 | 34 |
| orientation-planning | 385 | 45 |
| suspension | 19 | 1 |
| retirement | 61 | 1 |
| packets-authority-identity | 251 | 27 |
| generation-install-permissions | 394 | 55 |
| suite-isolation | 46 | 5 |

### Muestra temporal deliberada, no aleatoria

Se escogieron los tres archivos con mayor colección, un candidato de consolidación histórica y un control documental. No representa estadísticamente la suite.

Comando: `python3 -m pytest -q -p no:cacheprovider --durations=0`, sobre los cinco archivos siguientes, con `--basetemp` y `--junitxml` temporales.

**Salida:** `205 passed in 252.25s (0:04:12)`, **rc=0**. Tiempo del proceso controlador: 253,092 s.

Los tiempos por archivo se agregaron del XML de **esa misma corrida**, con precisión de milisegundos; incluyen las fases registradas por pytest.

| Archivo, bajo `tests/` | Tests | Tiempo agregado |
|---|---:|---:|
| `test_007_001_unambiguous_entry.py` | 49 | 60,407 s |
| `test_007_006_withdraw_and_republish.py` | 61 | 89,924 s |
| `test_007_004_termination_not_success.py` | 69 | 89,385 s |
| `test_005_013_t1_unit_projection.py` | 18 | 12,007 s |
| `test_010_003_documentary_pilot.py` | 8 | 0,047 s |
| **Suma de tiempos de tests** | **205** | **251,770 s** |

Las fases `call` visibles en `--durations` suman 250,96 s. Esto sitúa el coste principalmente dentro de las funciones de test —incluidos los preparativos que llaman—, no en el bootstrap visible de pytest. No separa el coste individual de todos los helpers.

Los dos casos más lentos fueron:

- `transport_failures_have_no_delivery[own-timeout]`: **7,76 s call**.
- `opencode_noncompleted_never_claims_delivery[client-hangs-timeout]`: **4,86 s call**.

### Qué no mide la evidencia histórica permitida

`measurement-after.json` contiene **cinco archivos, 72.287 bytes y 1443 líneas LF**: es la medición del piloto, no duración ni inventario completo (`docs/specs/008-002-suite-by-capability/measurement-after.json:2-37`).

Los **46–103 minutos** están documentados en `docs/ci-gate.md:64-66`; los **3878,91 s** corresponden al cierre histórico de 010-003 (`docs/activeContext.md:203`). No son una línea base temporal actual ni permiten atribuir minutos a archivos.

---

## C. Causa raíz del criterio

La hipótesis mejor respaldada es una combinación de tres factores:

1. **Criterio correcto, instrucciones operativas parcialmente antiguas.** La promesa selecciona; la postcondición sigue organizando numerosos despachos y ejemplos.
2. **La pertinencia se justifica aisladamente.** Es fácil decir qué riesgo cubre un test sin demostrar qué garantía se perdería realmente al retirarlo, considerando los demás.
3. **Conservación sin revisión ordinaria de redundancia.** La suite crece por features y correcciones; la sustitución exige trabajo especial, mientras mantener es la disposición por defecto.

Esto explica un mecanismo plausible de acumulación. **No demuestra qué proporción de los 1937 tests sobra ni qué proporción del tiempo es evitable.**

El paralelismo podría reducir espera de ejecución, pero no corrige ninguno de esos tres factores.

---

## D. Propuesta de cambio, archivo por archivo

Intenciones para el brainstorm, **sin redactar la spec ni modificar contratos cerrados**:

| Archivo o superficie | Intención |
|---|---|
| `sources/roles/test-writer.md`, R2 | Aplicar la selección contra la suite existente: reutilizar, extender o consolidar antes de incorporar otro oráculo equivalente. Interpretar la consecuencia como contribución efectiva del test, no descripción genérica del riesgo. Sin cuotas nuevas. |
| `sources/roles/orchestrator.md`, R4 | Registrar en el AUDIT existente la disposición de redundancias y sustitutos; exigir preservación acreditada antes de retirar. No añadir otra puerta mecánica. |
| `sources/roles/reviewer.md` | Orientar la auditoría independiente hacia equivalencia y garantías conservadas, por referencia a R2/R4/R7. |
| `skills/cdad-cycle/references/stage-3-tdd.md` | Mantener R7; hacer explícito el uso de verificadores existentes y la consolidación aprobada en AUDIT/POST-AUDIT. Revisar el mínimo universal de entradas de propiedades. |
| `skills/cdad-cycle/SKILL.md` | Alinear unidades y ejemplos con promesas y trazabilidad muchos-a-uno; conservar la obligación de verificar todas las postcondiciones comprometidas. |
| `skills/cdad-cycle/references/handoff-prompts.md` y `re-entry.md` | Quitar la inducción operativa a un nuevo test por postcondición. Incorporar sustitución por redundancia, no solo por desaparición del comportamiento. Corregir además la instrucción de importar módulos bajo prueba en Pre-RED (`handoff-prompts.md:367`), incompatible con el aislamiento. |
| `skills/cdad-cycle/packets/substages/test-writer-{audit,red,post-audit}.md` | Transportar ese criterio también por paquetes, sin redefinirlo. |
| `skills/cdad-cycle/assets/spec-template/test-audit.md` | Añadir disposiciones y destinos de consolidación al registro existente; documentar obligaciones conservadas y motivos para mantener variantes distintas. |
| `skills/cdad-spec-and-test/SKILL.md` | Eliminar el umbral de 30 s como juicio de utilidad y remitir al ciclo para aceptación, gates y formato aplicables. |
| `skills/odoo-test-writer/SKILL.md` | Resolver con el hogar genérico la contradicción de presupuestos de propiedades; mantener semilla y presupuesto declarado, sin cuotas rivales. |
| `skills/cdad-cycle/references/anti-patterns.md` | Señalar acumulación sin garantía adicional y confusión entre presencia textual y garantía semántica; remitir a los hogares existentes. |
| `scripts/cdad-doctrine-check.py` | Ajustar únicamente controles estructurales justificables. No convertirlo en juez automático de pertinencia. |
| Inventario/mapa de 008-002 | Actualizar sus datos vivos y conservar la genealogía de obligaciones sustituidas. **No reescribir su spec ni la de 008-006.** |
| `agents/` y `build/` | Solo regeneración desde fuentes, nunca edición manual. |

Prefiero esta solución general —decisión de pertinencia y mantenimiento de garantías— a arreglos por prefijo de feature, renombres masivos o un clasificador semántico nuevo.

---

## E. Poda y velocidad: alternativas

| Alternativa | Qué sabemos | Ganancia acreditada |
|---|---|---|
| Criterio + poda piloto | Hay recorridos repetidos y candidatos concretos; R7 y el mapa existente permiten conservar obligaciones | **No medida** |
| Consolidar el par B1 de 005-013 | Coste actual conjunto: 1,919 s; protecciones diferentes que deben reunirse | **No medida**; no atribuir todo su coste como ahorro |
| Revisar la matriz de 21 flags | Coste actual: 21,879 s; repite preparación CLI | **No medida**; contrato enumerado impide poda automática |
| Compartir preparación inmutable y copiarla por test | Los constructores ejecutan preparación real repetidamente | **No medida**; requiere preservar aislamiento y caminos de integración |
| Paralelismo con xdist | No instalado; hay aislamiento HOME/XDG/TMP por sesión y test | **No medida ni probada su seguridad** |
| Reducir propiedades por presupuesto | Hay presupuestos internos grandes y reglas contradictorias | Duración y ganancia **no medidas** |
| Podar controles documentales baratos | El piloto medido cuesta 0,047 s | No es un objetivo relevante de velocidad en esta muestra |

El aislamiento actual es una base favorable para estudiar workers, no una acreditación de seguridad paralela (`tests/conftest.py:80-126`). Las cachés de `product_staging` son globales por proceso; podrían multiplicar generación por worker (`tests/product_staging.py:12-15,33-38,84-92`). Compartir estado mutable para ahorrar preparación sería un riesgo distinto.

008-002 dejó paralelismo fuera de alcance (`docs/specs/008-002-suite-by-capability/spec.md:50-54`). Puede abrirse otra feature sin modificar retrospectivamente ese contrato.

**Respuesta temporal:** hoy no hay base para repartir los 3878,91 s históricos entre «poda» y «mecánica». Se midieron costes de candidatos, no ahorros.

---

## F. Riesgos y límites

- Confundir igual resultado superficial con equivalencia de garantías, especialmente en seguridad, integridad, idempotencia y variantes acreditadas.
- Usar una consecuencia genérica como justificación suficiente de cualquier test repetido.
- Sustituir varios tests por un recorrido enorme que dificulte diagnóstico o mezcle promesas independientes.
- Tratar toda comprobación textual como inútil, o presentarla como prueba semántica.
- Optimizar fixtures alterando autoridad, rutas, estado o aislamiento.
- Añadir paralelismo y perder atribución del verde, o multiplicar staging sin acelerar.
- Comparar corridas bajo carga distinta como si toda diferencia proviniera del cambio.
- Convertir esta revisión en una auditoría exhaustiva de 1937 tests antes de obtener una mejora útil.

**VERIFY pendientes:** cantidad global de redundancias; equivalencias fuera del piloto; distribución temporal completa; ahorro de consolidación; seguridad y rendimiento paralelo.

El estado git final conserva únicamente los cambios documentales preexistentes: `docs/.cdad-state.json` y el discovery no versionado de 010-000. `git diff --name-only -- sources skills tests scripts agents build` no produjo salida.

---

## G. Preguntas para el dueño

1. **¿Una feature —criterio más poda— o dos, dejando paralelismo aparte?** Recomiendo 013 para criterio coherente y poda piloto acreditada; otra feature para paralelismo, si sigue siendo necesario.
2. **¿Autorizas una corrida completa de línea base**, con duraciones y evidencia atribuible, antes de fijar objetivos de velocidad? Esta autorización todavía no existe y aquí no se ejecutó.
3. **¿Aprobamos como criterio de poda preservar garantías, no cantidades**, comenzando por un lote acotado con sustitutos y auditoría independiente, sin meta arbitraria de tests eliminados o minutos ahorrados?
