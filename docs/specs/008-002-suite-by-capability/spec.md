# 008-002 — Suite por capacidad y contrato

**Estado:** aprobada por el orquestador (HITL delegada) el 2026-10-27, tras plan-review con 3 bloqueantes cerrados (B1 plan-tasks, B2 alcance de PC-4, B3 oráculo de PC-3) y 4 importantes atendidos.  
**Epic:** `epic-008-suite-coherence`.  
**Dependencia:** 008-001-home-xdg-isolation.  
**Autoridad:** contrato aprobado de unidad y plan del epic, no una especificación previa.

## 1. Objetivo

Organizar la suite existente mediante un inventario versionado por capacidad y contrato, ofrecer selección ejecutable por CLI y consolidar un lote acotado de duplicación sin perder obligaciones ni variantes acreditadas.

La organización es inicialmente **lógica**, no una migración de directorios. Los nombres históricos pueden permanecer.

## 2. Evidencia y decisiones

### Superficie verificada

- El discovery propone ocho familias y advierte que los módulos mixtos necesitan clasificación por test: `discovery.md:13-24`.
- El gate local sólo considera cambios comprometidos de scripts de producto y busca referencias en `tests/test_*.py`: `.cdad/local/surface-gate.sh:6-11`. Un cambio exclusivamente de tests puede producir selección vacía.
- El gate anterior sobrescribe los intentos: `008-001-home-xdg-isolation/closure.md:102-117`.
- El techo instrumental de espera es actualmente 5s: `tests/test_005_009_t2_opencode_adapter.py:417-421`. Cuatro aserciones de respuesta sin espera adicional dependen de él:
  - dos casos PD-2 en `test_005_010_t1_durable_signal.py:250-340`;
  - R3 en `test_005_010_reviewfix.py:380-428`;
  - B1 en `test_005_010_b1_last_assistant.py:175-184`.
- La fixture transversal y sus recursos de sesión están en `tests/conftest.py:80-140`; las cachés estables, en `tests/product_staging.py:35-54`.
- La paridad de modelo entre vías no equivale a probar cada vía individualmente: `test_006_005_u6fix6_model_parity.py:16-65`. No se autoriza eliminarla por semejanza.
- Las enmiendas de oráculos tienen genealogía contractual: `test_006_005_reviewfix.py:30-59`.

### Decisiones

1. **Un índice versionado compartido**, no carpetas nuevas ni clasificación por prefijos de feature. Permite módulos mixtos y selección sin romper imports.
2. **Una CLI pequeña alrededor de pytest existente**, no otro framework ni scheduler. Las interfaces descritas abajo son propuestas nuevas, no APIs existentes.
3. **Clasificación por nodeid cuando haga falta**; el módulo completo es abreviatura válida sólo si pertenece íntegramente a la misma capacidad y contrato.
4. **Consolidación piloto en señal durable y clasificación de entrega**, limitada a los tres módulos 005-010 indicados arriba y sus helpers directamente necesarios. No se presupone que alguno sea redundante.
5. **Gate canónico versionado**, que reemplaza los mecanismos locales de selección y cierre; no se mantienen implementaciones independientes y los scripts locales históricos quedan únicamente como evidencia. PC-5 y PC-6 permanecen en esta unidad por decisión HITL: sin selección sensible a cambios exclusivamente de tests, esta reorganización sería invisible al gate, y la preservación de intentos resuelve el defecto de evidencia transferido explícitamente desde 008-001 (`docs/specs/008-001-home-xdg-isolation/closure.md`, §«Historial del gate»). **Contrato que hereda 008-005:** CI ejecuta el gate canónico, conserva sus códigos de salida y evidencia, y no redefine selección ni reserva de intentos.
6. **Techo de 2s re-declarado como deuda explícita**, no como garantía universal ni requisito silenciosamente satisfecho por una tolerancia de 5s. Esta unidad separa su declaración de la cota instrumental; no cambia tiempos del producto para aparentar cumplimiento.

## 3. Alcance

### Dentro

- Inventario exhaustivo de módulos Python versionados bajo `tests/`.
- Mapa de obligaciones acreditadas y sus tests antes/después.
- Selección y ejecución por capacidad.
- Consolidación piloto con reducción efectiva y preservación demostrada.
- Selección por superficie que incluya cambios sólo de tests.
- Preservación independiente de cada intento del gate de cierre.
- Informe reproducible y disposición explícita de la deuda temporal.

### Fuera

Framework nuevo, renombres globales, migración masiva, reescritura de contratos cerrados, mutation testing completo, paralelismo, publicación de CI y cambios funcionales del ciclo.

No se cambian `status`, recibos, continuidad ni reglas de aislamiento de 008-001.

## 4. Artefactos versionados

Bajo `docs/specs/008-002-suite-by-capability/`:

- `suite-inventory.json`
- `pc-map.json`
- `measurement-before.json`
- `measurement-after.json`
- `suite-report.md`
- `variant-controls.json`
- `timing-disposition.json`

### Inventario

Formato JSON con `schema_version: 1` y entradas deterministas ordenadas por ruta.

Cada módulo contiene:

- `path`;
- `kind`: `test`, `helper` o `bootstrap`;
- asignaciones de capacidad y contrato;
- `decision`: `mantener`, `fusionar` o `eliminar`;
- justificación;
- destinos, cuando corresponda;
- superficies de producto ejercitadas y dependencias de helpers conocidas.

Las asignaciones de módulos mixtos declaran nodeids explícitos. Un test puede proteger varias capacidades; la selección deduplica sus nodeids.

Las capacidades iniciales son entrega/evidencia, continuidad, despacho/recuperación, orientación/planificación, suspensión, retiro, paquetes/autoridad/identidad, generación/instalación/permisos y suite/aislamiento. Suspensión y retiro permanecen separados.

### Mapa de obligaciones

Cada registro conserva:

- referencia contractual estable: archivo, identificador PC/PD/INV o sección;
- fuente de acreditación y enmienda aplicable;
- nodeid original;
- variante y resultado observable protegido;
- nodeid destino;
- decisión y justificación de equivalencia.

El mapa se construye desde especificaciones, enmiendas, reviews y cierres acreditados; **no se deduce únicamente de docstrings ni nombres**.

Una referencia no resuelta se declara `VERIFY` y bloquea eliminar o debilitar los tests relacionados. Una obligación antes acreditada no puede desaparecer del mapa después.

### Controles de variante y disposición temporal

Cada entrada de `variant-controls.json` declara obligación, variante, nodeid original, destino, desviación contractual introducida, comando reproducible, resultado esperado y evidencia obtenida. El **test-writer** escribe y ejecuta los controles; el **reviewer independiente** contrasta su correspondencia con el contrato.

Los controles ejecutables viven en `tests/test_008_002_variant_controls.py` y operan sobre copias sintéticas aisladas, sin modificar el checkout del producto:

```text
python3 -m pytest -q tests/test_008_002_variant_controls.py
```

`timing-disposition.json` declara, por separado, la deuda de «no esperar de más» (objetivo de 2 s, umbral efectivo actual, motivo por el que 5 s no acredita 2 s, criterio de resolución futura). Estas rutas e interfaces son **propuestas nuevas**, no capacidades existentes.

## 5. CLI propuesta

Archivo propuesto: `scripts/cdad-suite.py`.

```text
python3 scripts/cdad-suite.py validate
python3 scripts/cdad-suite.py list --capability <id>
python3 scripts/cdad-suite.py run --capability <id>
python3 scripts/cdad-suite.py surface --base <ref> --collect-only
python3 scripts/cdad-suite.py surface --base <ref>
python3 scripts/cdad-suite.py surface --base <ref> --all
python3 scripts/cdad-suite.py measure
python3 scripts/cdad-suite.py close --evidence-root <directorio>
```

- `validate` contrasta la **integridad estructural** del inventario y el mapa frente a la colección real de pytest: destinos existentes, conservación de obligaciones acreditadas y ausencia de `VERIFY` pendiente para una eliminación. También valida `timing-disposition.json`. **No acredita semánticamente la conservación de variantes.**
- `list` devuelve JSON con nodeids ordenados y sin duplicados.
- `run` ejecuta exactamente la selección mediante pytest existente.
- `surface` selecciona la unión de superficies de producto afectadas y tests afectados.
- `measure` es exclusivamente informativo y read-only: emite JSON por stdout, sin modificar archivos, índice ni snapshots.
- `close` es el **único mecanismo del closer** para ejecutar y registrar el gate final; no existe una segunda vía manual equivalente de cierre.
- Si la base carece del inventario o del mapa requerido, `surface` termina no cero con diagnóstico identificable. Únicamente `--all` explícito permite continuar seleccionando todos los nodeids actuales; no constituye un fallback silencioso.

Errores de capacidad, referencias inexistentes, inventario inválido o selección requerida vacía terminan con diagnóstico y código no cero. Los comandos de ejecución propagan el resultado de pytest. No hay fallback silencioso a éxito.

### Cambios considerados por superficie

`surface` compara el árbol actual contra `<ref>`, incluyendo cambios comprometidos, indexados y no indexados; incluye tests nuevos no ignorados.

- Test modificado o añadido: selecciona sus nodeids actuales.
- Test eliminado o trasladado: consulta el inventario y mapa de la base para seleccionar sus sustitutos y contratos afectados.
- Helper modificado: selecciona sus consumidores declarados.
- Bootstrap transversal modificado: selecciona todas las capacidades.
- Producto modificado: selecciona las asignaciones del inventario a esa superficie.
- Cambio de selección o mapa: selecciona las asignaciones anteriores y actuales afectadas.

Una dependencia sin clasificación produce diagnóstico no cero; nunca «sin superficies tocadas» como evidencia suficiente de una reorganización.

## 6. Postcondiciones verificables

### PC-1 — Inventario exhaustivo y selector válido

`validate` devuelve cero cuando todos los módulos Python versionados bajo `tests/` están inventariados y todos los tests recolectados tienen capacidad y contrato.

**Controles negativos:** módulo omitido, nodeid inexistente, asignación mixta incompleta y capacidad desconocida producen código no cero y diagnóstico identificable.

**Oráculo:** JSON emitido, rutas y nodeids de colección.

### PC-2 — Selección ejecutable por capacidad

`list --capability X` devuelve exactamente los nodeids asignados a X, ordenados y sin duplicados. `run` ejecuta esa selección sin errores de imports ni ejecución de tests ajenos.

**Variantes:** capacidad repartida entre módulos, módulo mixto, test asignado a varias capacidades y fallo de un test seleccionado.

**Oráculo:** selección JSON, resultados de pytest y código de salida.

### PC-3 — Conservación de obligaciones y variantes

Cada obligación acreditada antes conserva destinos recolectables después. Cada variante observable original queda preservada por un caso destino, no sólo por conservar el identificador PC.

Cada eliminación exige sustituto identificado y evidencia de que éste detecta la misma desviación contractual. Se usan controles negativos dirigidos sobre las variantes retiradas; no se exige una campaña general de mutantes.

**Oráculo estructural:** `validate` rechaza destinos inexistentes, desaparición de obligaciones acreditadas y eliminaciones con `VERIFY` pendiente.

**Oráculo de variantes:** controles negativos dirigidos, versionados y reproducibles según `variant-controls.json` y `tests/test_008_002_variant_controls.py`. Para cada variante retirada, el sustituto debe detectar la desviación contractual declarada; conservar una etiqueta en el mapa no acredita ese resultado.

Sin control satisfactorio, el caso original se mantiene. No se exige una campaña general de mutation testing.

### PC-4 — Consolidación acotada con reducción real

El piloto reduce **bytes y líneas LF** del conjunto delimitado de tests/helpers afectados, incluyendo helpers extraídos y controles nuevos necesarios para acreditar su conservación.

La delimitación inicial se registra antes de consolidar; cualquier archivo añadido para implementar o comprobar esa consolidación se incorpora al conjunto final. No se reduce el denominador trasladando código fuera de él.

El delta de toda la suite se informa separadamente, contabilizando los tests nuevos de la feature, pero **no condiciona el cierre**. No se adelgazan pruebas ni aserciones para ganar bytes.

PC-4 compara únicamente las mediciones antes/después de esta feature realizadas con idéntico método; los números históricos de `discovery.md` y §7 son contexto, no extremos de esa comparación.

Se conserva el comportamiento de casos distintos: esquema desconocido, store ilegible, ausencia total de texto final y último assistant sin texto aunque exista texto anterior.

**Oráculo:** manifests antes/después, mapa PC→test y subconjunto afectado verde. No se fija un porcentaje mínimo inventado.

**AJ6 (directiva del owner, 2026-10-27):** la reducción se **informa con números** y **no condiciona el cierre**. Lo que condiciona es no perder ninguna variante acreditada y no debilitar ninguna aserción. Un objetivo de bytes sobre tests es de la misma familia que un objetivo de cobertura, y la directiva vigente los prohíbe. La medición real del piloto se publica tal como sale, incluso si es negativa.

### PC-5 — Gate sensible a cambios exclusivamente de tests

En un repositorio sintético, modificar únicamente un test hace que `surface` lo seleccione; si falla, el comando termina no cero.

**Variantes:** test nuevo, eliminación con sustituto, helper compartido, cambio sin commit, cambio de producto y base sin inventario/mapa —diagnóstico no cero—; la misma situación con `--all` explícito selecciona todos los tests actuales y el resultado de pytest sigue propagándose.

**Oráculo:** nodeids seleccionados, salida de pytest y código de retorno. No basta una búsqueda textual de referencias a producto.

### PC-6 — Evidencia de cierre sin sobrescritura

Cada invocación de `close` reserva exclusivamente un directorio de intento nuevo bajo la raíz declarada: no reutiliza un intento existente aunque se repita el número lógico de corrida, y la reserva debe resolver correctamente invocaciones concurrentes. La garantía es de creación exclusiva y no reuso; no promete inmutabilidad frente a modificaciones externas posteriores.

Conserva por intento:

- comando y selección;
- commit, estado del árbol y hashes de los artefactos de selección;
- inicio, final, resultado y motivos de skips;
- stdout/stderr;
- snapshots del canario y su alcance;
- estado `running`, `finished` o interrupción declarada.

Un segundo intento fallido o exitoso no altera los bytes del primero. Una interrupción abrupta puede dejar `running`: nunca se interpreta como éxito.

**Oráculo:** dos intentos secuenciales controlados con resultados distintos, más dos invocaciones **simultáneas** bajo la misma raíz que obtienen directorios distintos y evidencia independiente; una colisión no sobrescribe ni adopta el intento ajeno. Se comparan nombres y hashes del primer intento antes/después. Las pruebas de esta PC usan una selección sintética pequeña; no ejecutan la suite completa.

### PC-7 — Deuda temporal explícita y no confundida con la cota instrumental

El informe identifica los cuatro casos de «no esperar de más» citados en §2, su obligación y umbral efectivo actual de 5s. Declara por separado:

- objetivo pendiente de techo propio de 2s;
- alcance temporal de la medición actual;
- motivo por el que 5s no acredita 2s;
- deuda pendiente para el epic y criterio de resolución futura.

La validación de los artefactos rechaza una disposición ausente o que declare resuelto el techo de 2s sin evidencia propia.

**Oráculo:** `python3 scripts/cdad-suite.py validate` valida `timing-disposition.json`, rechaza una disposición ausente o una declaración de resolución del techo de 2 s sin evidencia propia referenciada, y expone las referencias de los casos existentes. Esta comprobación documental acredita transparencia de la deuda, no latencia de 2 s.

### PC-8 — Informe comparable e aislamiento preservado

El informe antes/después utiliza idéntico algoritmo y distingue:

- módulos de test, helpers y bootstrap;
- bytes y líneas LF;
- obligaciones y variantes;
- casos fusionados/eliminados con sustitutos;
- duplicación confirmada frente a similitud no demostrada;
- resultados del subconjunto afectado y del gate final.

Los tests de aislamiento 008-001 y los consumidores afectados permanecen verdes. Selección mínima obligatoria de aislamiento:

```text
python3 -m pytest -q \
  tests/test_008_001_home_xdg_isolation.py \
  tests/test_008_001_pc7_wrapper_margin.py \
  tests/test_008_001_pc8_adapter_budget.py
```

Y para el piloto y sus consumidores compartidos:

```text
python3 -m pytest -q \
  tests/test_005_009_t2_opencode_adapter.py \
  tests/test_005_010_t1_durable_signal.py \
  tests/test_005_010_reviewfix.py \
  tests/test_005_010_b1_last_assistant.py \
  tests/test_005_010_t2_load_mode_invocation.py \
  tests/test_005_010_t4_integration.py
```

Si el inventario identifica consumidores adicionales de un helper modificado, se incorporan a la selección afectada antes de aceptar el lote. Los skips opt-in conservan su motivo y no sustituyen evidencia positiva. No se desactiva aislamiento ni se reduce una aserción para lograr la consolidación.

## 7. Método de medición

Universo: archivos Python versionados bajo `tests/`, enumerados con `git ls-files`, rutas ordenadas.

Para cada archivo: ruta, tipo, longitud de bytes, cantidad de bytes LF y SHA-256. Se incluyen helpers extraídos y tests nuevos; se excluyen cachés, generados y archivos no versionados.

La medición final se toma con los archivos nuevos ya incorporados al índice. Se registra commit, diff y versión de Python. El hash del manifest utiliza JSON con claves ordenadas y separadores compactos.

La duplicación confirmada se mide mediante registros del mapa que documentan equivalencia de obligación, variante y fallo detectable. No se presenta similitud textual como porcentaje de cobertura.

Observación actual, no baseline definitiva del implementador:

```text
commit: ef6256a815f4fac47608fab20040fdfe32e7ca4e
Python: 3.13.5
módulos Python: 207
módulos con nombre test_: 203
bytes: 6.400.297
líneas LF: 138.436
manifest SHA-256:
c077ac047bd96481a2b7ddd6b81bb079ee89c63b005f897c690adb6f970769c1
```

Estos valores no sustituyen la baseline del discovery: corresponden a otra revisión y un método declarado.

## 8. Límites y cierre

El índice es una declaración auditada, no análisis semántico completo de dependencias. La conservación del mapa no demuestra ausencia universal de regresiones; los controles dirigidos y ejecución aportan evidencia adicional acotada.

El canario conserva los límites de 008-001: no observa todas las lecturas ni escrituras transitorias revertidas. El aislamiento no es una sandbox.

Los gates canónicos nuevos deben quedar versionados. Los archivos locales históricos no aparecen en `git ls-files` y no bastan para distribuir la capacidad.

El closer aplica la política de suite del paquete. Una interrupción o fallo conserva su intento y bloquea el cierre; una repetición requiere su autorización correspondiente. No se heredan como nuevas las tres corridas de 008-001.

## Ajustes del orquestador

**AJ6 — Regla del owner: test por contrato, no por cobertura (provisional, 2026-10-27).** Rige esta unidad la directiva del dueño registrada en `docs/epics/epic-008-suite-coherence/owner-rule-tests-contract.md`, con sus nueve cláusulas. Consecuencias directas en 008-002:

- Las postcondiciones de esta spec se leen como **promesas observables**; donde enumeran variantes, se mantiene sólo la que produce un resultado observable distinto (cláusula 2). PC-5 ya no exige "7 variantes": exige que el gate no acepte una reorganización invisible, y las variantes que sólo difieren en el camino interno se retiran o se difieren.
- Cada test nuevo declara «sin este test, el usuario…» (cláusula 4).
- Lo que se decide no probar va a **`deferred-hardening`** al final de esta spec (cláusula 5) y pasa al `closure.md`.
- El **reviewer** no bloquea por un test faltante sin consecuencia de usuario (cláusula 7); el **orquestador** puede promover un hallazgo por seguridad, integridad o regresión cara (cláusula 9), registrando el motivo.
- El **implementer** queda fuera de la regla: la robustez razonable no se limita a lo mínimo que pasa el test.

**AJ7 — Interfaz de `close` y forma de la evidencia (2026-10-27).** PC-6 exigía una garantía sin declarar la interfaz que la hace observable. Se fija así:

```
python3 scripts/cdad-suite.py close --evidence-root DIR [--capability C | --nodeids FILE | --all]
```

- `--evidence-root DIR` es obligatorio y debe existir; `close` crea dentro **un** directorio de intento nuevo por invocación, con nombre único (`attempt-<UTC>-<pid>-<rand>`), mediante creación exclusiva: si el nombre existe, falla en vez de reutilizarlo. Dos invocaciones concurrentes obtienen directorios distintos.
- `--capability`, `--nodeids` y `--all` son mutuamente excluyentes y definen la selección; sin ninguno, la selección es la completa del repositorio. `--nodeids FILE` lee nodeids separados por líneas.
- Cada intento escribe, antes de ejecutar pytest, `attempt.json` con `state: "running"` y los campos: `schema_version`, `command` (argv completo), `selection` (`{kind, value, nodeids}`), `commit`, `dirty` (cantidad de entradas de `git status --porcelain`), `started_at`, `finished_at`, `rc`, `pytest_summary` (`passed`, `failed`, `skipped`, `skips: [{nodeid, reason}]`), `canary` (`{scope, before, after, delta_lines}`) y `artifacts` (`{stdout, stderr}`).
- Al terminar, reescribe `attempt.json` con `state: "finished"`, `finished_at` y `rc` de pytest. Si el proceso se interrumpe, el archivo conserva `state: "running"` (o `"interrupted"` si alcanzó a declararlo) y **nunca** se interpreta como éxito.
- Escribe además `stdout.log` y `stderr.log` con la salida de pytest, y guarda los snapshots del canario en `canary-before.txt` / `canary-after.txt` dentro del intento; `canary.scope` declara las rutas cubiertas.
- `rc` de `close` es el de pytest; los errores de uso o de reserva salen con código 2 y no dejan un intento a medias declarado como exitoso.

## deferred-hardening

Lo que se decide **no** probar en esta unidad, con su motivo:

| Qué queda sin test | Por qué | Dónde se probará |
|---|---|---|
| Variantes de PC-5 que sólo difieren en el camino interno (helper sin consumidores declarados, test nuevo sin trackear, etc. más allá de la que acredita el gate) | Mismo resultado observable que el caso ya cubierto | Endurecimiento posterior del epic |
| `measure` como contrato de bytes/líneas | Es instrumento de reporte, no promesa al usuario | No se prueba; se informa |
| Detección de etiquetas de variante inexistentes (`[ghost]`) | Integridad estructural laxa, sin consecuencia de usuario | Endurecimiento posterior |
| Preservación semántica de variantes fuera del piloto | El piloto es el conjunto acotado; el resto queda en el mapa | 008-006 / epic de endurecimiento |
| Atomicidad real de `close` bajo concurrencia (más allá de creación exclusiva) | Cubierto por cláusula 9 (integridad): se conserva el caso concurrente, se difiere la prueba de fallo del sistema de archivos | Endurecimiento posterior |
