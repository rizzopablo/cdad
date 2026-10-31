# POST-AUDIT — 010-003-documentary-pilot — T2 (test-writer/post-audit)

**Encargo:** `010-003-documentary-pilot-test-writer-post-audit-001` (T2, segundo encargo, sesión distinta del AUDIT).
**Contrato auditado:** `docs/specs/010-003-documentary-pilot/spec.md` v5, sha256 `f2dce9e0…1d5e5` (coincide con el pineado).
**Entrada:** ruta C con contexto v2. `validate-packet` rc=0; `render` byte-idéntico a `PACKET.md` (10.222 bytes); `render --route C` idéntico al bloque de identificación del despacho; sha256 de `spec.md` y `plan.md` coinciden con los declarados.
**Escritura:** ninguna. No se creó, modificó ni borró ningún test. `write_scope` (`tests/`) no ejercido. No se inició RED, no se implementó, no se corrió la suite completa.

---

## 1. DEBER 1 — Tests existentes intactos: evidencia medida

| Archivo | Colectados | Resultado medido | rc |
|---|---|---|---|
| `tests/test_010_001_documentary_contracts.py` | 11 | **11 passed** (en la corrida conjunta) | 0 |
| `tests/test_010_002_documentary_role_integration.py` | 29 | **29 passed** (en la corrida conjunta) | 0 |
| **Regresión declarada (ambos)** | **40** | **40 passed in 51.25s** (2026-10-31T19:39:54Z) | **0** |
| `tests/test_010_002_documentary_role_properties.py` (**no declarado en el plan**) | 7 | **7 passed in 190.39s** (19:40:50Z→19:44:01Z) | 0 |

**Comandos exactos:**
```
python3 -B -m pytest -q --collect-only tests/test_010_001_documentary_contracts.py
  → 11 tests collected
python3 -B -m pytest -q --collect-only tests/test_010_002_documentary_role_integration.py
  → 29 tests collected
python3 -B -m pytest -q --collect-only tests/test_010_002_documentary_role_properties.py
  → 7 tests collected
python3 -B -m pytest -q --tb=no \
  tests/test_010_001_documentary_contracts.py \
  tests/test_010_002_documentary_role_integration.py
  → ........................................ [100%]
  → 40 passed in 51.25s
  → RC=0
python3 -B -m pytest -q --tb=no tests/test_010_002_documentary_role_properties.py
  → ....... [100%]
  → 7 passed in 190.39s (0:03:10)
  → RC=0
```

**Verificación de la enumeración del AUDIT, no solo del conteo.** Extraje los node IDs colectados y los comparé con la lista de `test-audit.md:76-78`:
- 010-001: **11/11 exactos**, sin faltantes ni sobrantes.
- 010-002: **29/29 exactos** tras expandir la abreviatura `…::` en orden (el AUDIT nombra la clase completa la primera vez y la abrevia después).
- Propiedades: el AUDIT las identifica por clase y conteo (`TestInv04Properties::` 5, `TestFinalIsolatedDistribution::` 2). Los 7 node IDs completos son:
  `TestInv04Properties::test_contextual_contrast_rejects_a_new_intent_with_a_discordant_agent`;
  `…::test_presence_rule_rejects_context_without_agent_and_admits_the_historical`;
  `…::test_publication_conserves_the_admitted_request_and_render_fields`;
  `…::test_publication_derivation_matches_the_canonical_rule`;
  `…::test_static_contrast_admits_the_declared_role_and_rejects_foreign_families`;
  `TestFinalIsolatedDistribution::test_final_documentary_journeys_keep_domain_product_and_frontiers`;
  `…::test_isolated_install_distributes_the_final_cli_and_schema`.

**47 node IDs existentes intactos y verdes** (40 declarados + 7 de propiedades), confirmados hoy. `git status --porcelain -- tests/` vacío; los últimos commits que tocan los tres archivos (`6e9ef3b6`, `58b0bcd7`, `c5c054b4`) son anteriores al AUDIT, así que la medición no está stale.

**Selección:** confirmo los 2 archivos del plan (`plan.md:71-72,211-213,376-378`). El archivo de propiedades se corrió y se reporta **por separado**; no lo agrego a la selección porque el plan está pineado.

---

## 2. DEBER 2 — Dictamen de suficiencia e independencia

### 2.1. Las quince PC están clasificadas — **correcto**

- Verificación programática: la spec tiene **15** bullets `PC-01..PC-15` y el AUDIT tiene **15** filas; conjuntos iguales, sin faltantes ni sobrantes (`spec.md:121-198`; `test-audit.md:16-30`).
- PC que exigen sesión real y su vía: PC-02 (b), PC-03 (b), PC-07 (b para recepción efectiva), PC-08 (b), PC-09 (b para orden/originalidad), PC-11 (b), PC-12 (b), PC-13 (b); PC-14/15 incluyen (c). **Ninguna figura como control automático**: los 8 focales solo tocan PC-01, PC-04, PC-05, PC-06, PC-10, §2.4:111, §2.2:44 e INV-06 (`test-audit.md:42-49`).
- Ninguna estructural se presenta como fidelidad semántica: cada fila lleva su límite, y los casos sensibles están marcados — PC-06 con C-2 (`test-audit.md:21,126`), PC-10-b con `spec.md:113` (`test-audit.md:25`), PC-01 con C-3 (`test-audit.md:16,127`), PC-15 con "presencia ≠ cumplimiento" (`test-audit.md:30`). La regla del encargo está explícita en `test-audit.md:32`.

**Observación menor (redacción, no bloqueante):** la fila PC-02 declara vía **(b)** pero su columna de fracción menciona "(a) solo existencia y declaración explícita de no conformidad" (`test-audit.md:17`), y ningún control de los 8 cubre esa fracción. Debe decir "no propuesto" o nombrar la dependencia incidental de T3 (que lee `challenge/negative.md`). No afecta la clasificación: PC-02 no queda presentada como automática.

### 2.2. Los 8 controles: sin huérfanos ni redundancias — **correcto**

| Test | Ancla contractual | Consecuencia distinta que protege |
|---|---|---|
| T1 | PC-04 (`spec.md:131`) | Rechazo con diagnóstico (documento, referencia, causa) |
| T2 | PC-05 (`spec.md:132`) | Aceptación de la corregida + equivalencia del resto |
| T3 | PC-06 (`spec.md:133`) | Aceptación estructural del candidato semántico; límite C-2 |
| T4 | `spec.md:111,137` | Rechazo del verde vacío (cero referencias) |
| T5 | `spec.md:111` | Rechazo de fuente no inventariada (frontera de autorización) |
| T6 | PC-10 (`spec.md:175`) | Trazabilidad del producto: existe y toda cita resuelve |
| T7 | PC-01 + `spec.md:95-109` | Integridad del inventario: identidad, digests, anclas, origen sintético |
| T8 | `spec.md:44,211` (INV-06) | Invariancia al rewrap: falsifica la alternativa "ventanas de línea" |

- **Sin huérfanos:** cada test tiene ancla y consecuencia nombrada (`test-audit.md:51-56`).
- **Sin redundancias:** T1/T2 comparten muestra pero afirman veredictos opuestos más la equivalencia; T4/T5 son clases de defecto distintas exigidas por separado en la spec; T8 no repite T2 (un control por ventanas pasaría T1/T2 y fallaría T8); T3 y T6 operan sobre objetos distintos (candidato negativo vs producto corregido). Un control puede regresar sin el otro en cada par.
- **No hay prueba por postcondición:** 8 tests cubren 4 de 15 PC + §2.4 + INV-06; C y E no tienen test focal y el AUDIT lo declara (`test-audit.md:55`). Coherente con `spec.md:240` ("no se exige una prueba por postcondición ni variantes equivalentes sin consecuencia distinta") y con el `deferred-hardening` (`spec.md:266`).
- **Sin substage de propiedades:** justificado en `spec.md:214` ("los invariantes procedimentales no se convierten artificialmente en propiedades aleatorias").

**C-1..C-4 — verificadas contra el contrato:**
- **C-1 correcta.** PC-11 y PC-12 no llevan control automático porque el contrato no fija marcador: `spec.md:176-177` deja la forma libre y `spec.md:115` prohíbe introducir formato nuevo; la verificación de PC-10..PC-13 es control estructural + revisión semántica (`spec.md:180`). La cita externa a `documentary-contracts.md:11-13` no pude verificarla por texto (ver §4), pero la conclusión se sostiene en el silencio del contrato.
- **C-2 correcta.** `spec.md:133` exige aceptación estructural "aunque conserva los tres defectos"; la persistencia es (b) por clave y contraste (`spec.md:125,135`).
- **C-3 correcta.** T7 mide bytes en disco contra digests registrados, no "las versiones usadas en el ensayo"; eso último es (b) por snapshots y commits (`spec.md:96-99,127`).
- **C-4 correcta.** El verificador no puede leer `oracle/` ni reproducir la clave (`spec.md:82,186`; `plan.md:126`); la comparación contra la clave pertenece al contraste del orquestador. PC-03 no puede tener test honesto y el AUDIT lo deja constancia (`test-audit.md:128`).

### 2.3. El oráculo no se derivó del producto — **correcto en el contenido; hallazgo de proceso en las lecturas**

- **No hay producto del cual derivar:** `docs/specs/010-003-documentary-pilot/product/` no existe; `tests/fixtures/010_003_documentary_pilot/` tampoco; `tests/test_010_003_documentary_pilot.py` no existe. Verificado por `ls` (ENOENT).
- **El oráculo se rastrea al contrato:** las 8 aserciones y sus fixtures se derivan de `spec.md:95-109` (inventario y convención), `spec.md:131-137` (comportamiento del control), `spec.md:175` (producto), `spec.md:44,211` (rewrap). Ninguna lectura de producto o clave.
- **Sin impacto sobre lo existente:** `grep -rn "010_003\|010-003" tests/` → **sin coincidencias**; ningún test de los declarados enumera el árbol `tests/` (los `glob`/`rglob` de los tres archivos y `conftest.py` apuntan a HOME aislado, staging, agentes o directorios de dispatch, no a `tests/`). `git status -- tests/` vacío.

**Hallazgo de proceso (declarado por el AUDIT, requiere registro de la autoridad).** `test-audit.md:160` declara que el guard denegó `read` sobre `skills/cdad-cycle/references/documentary-contracts.md` y `…/stage-3-tdd.md` ("raíz de implementación") y que las leyó **por `bash`**. Esas rutas están bajo `skills`, que `execution.json:21-26` clasifica como raíz de implementación. El contrato de la feature, I-8 (`spec.md:246`), dice: "una denegación de lectura necesaria al test-writer se informa y escala; **no se rodea con otra herramienta**". La lectura fue declarada, no oculta, pero rodear la denegación es una desviación de I-8.

- **Atenuante sistémico:** el bloque común del paquete ordena leer la norma (`PACKET.md:12`, "read it, never restate it"), en conflicto con la política de rutas que clasifica `skills` como implementación. No es una invención del AUDIT; el conflicto es del paquete.
- **Efecto sobre el oráculo:** ninguno verificable. No existían producto, clave ni muestras que revelar; las dos referencias son norma y procedimiento de método, no las respuestas del piloto. La única cita a la norma es C-1, y su conclusión la verifiqué por el silencio del contrato (`spec.md:115,176-177`) y por `spec.md:180,240-242`.
- **Condición de cierre:** la autoridad registra la desviación antes de T3 y decide: **(a)** aceptar el AUDIT con registro, dado que no reveló respuestas y el mapeo es derivable del contrato, o **(b)** rehacer el AUDIT en sesión limpia sin esa lectura. En ambos casos debe resolverse el conflicto `PACKET.md:12` vs política de rutas para T3; si no, el encargo de RED repetirá la misma disyuntiva. **No es bloqueante del mapeo**, pero si no se registra, el gate de T2 no debería cerrarse.

### 2.4. El RED declarado es correcto — **legítimo**

- El plan lo fija: "Las demostraciones estructurales pueden estar verdes desde su creación: el rechazo de una muestra negativa es el resultado esperado de una prueba que pasa. La obligación aún ausente es el documento funcional: su prueba falla mediante una aserción explícita por producto inexistente, **no por errores de importación**" (`plan.md:151-152`).
- Composición declarada: **7 pasan al crearse** (T1–T5, T7, T8 operan sobre fixtures que construye el test-writer) y **1 falla: T6**, por `assert path.is_file()` → **AssertionError** (`test-audit.md:115`). Es exactamente la composición del plan; "todos rojos" sería leer mal `plan.md:151`.
- No hay ImportError posible: el control vive en el archivo de test declarado (`test-audit.md:58`), no importa implementación. Queda la condición de T3: **la aserción de existencia debe preceder a toda lectura** y la evidencia del RED debe mostrar `AssertionError`, no `FileNotFoundError`.

### 2.5. R2 y R4 — **declarados, no silenciados**

- **R2** (`test-audit.md:113`): la regresión declarada omite `test_010_002_documentary_role_properties.py`; el AUDIT no la amplía por su cuenta y exige enmienda del plan para hacerlo. La vía declarada es coherente con el plan: T4/T7 corren los dos declarados y el cierre `close --all` cubre el tercero (`plan.md:399,421,444`). El despacho **pinea el plan**, que es la decisión de la autoridad de mantener la selección; medición suplementaria de hoy: 7 passed. Sin cambio silencioso.
- **R4** (`test-audit.md:115`): declarado y correcto contra `plan.md:151-153`. El gate de T3 tiene ahora un criterio explícito: **1 rojo (T6, AssertionError) + 7 verdes**, no "todos rojos". Resuelto por el plan; no requiere enmienda.

---

## 3. Condiciones de precisión para T3 (no bloqueantes, no se deben maquillar)

1. **T7 y la declaración sintética del candidato.** La fila T7 afirma "corpus **y candidato** se declaran sintéticos" (`test-audit.md:48`; PC-01 en `spec.md:121`), pero sus fixtures listados son `sources/inventory.md`, `sources/s1*.md`, `sources/s2*.md`; el candidato vive en `challenge/negative.md`. **Cierre:** T3 agrega `challenge/negative.md` a las lecturas de T7, o mueve esa fracción a (b) y lo declara. Si no, la fracción "candidatos declarados sintéticos" queda sin acreditar.
2. **T7 debe ser bidireccional.** El nombre dice "accounts for every source", pero la aserción dice "toda fuente listada". Para PC-01 ("todas las fuentes autorizadas", `spec.md:121`) hay que afirmar también que **todo archivo bajo `sources/` figura en el inventario**; si no, un archivo no listado pasa.
3. **Dependencias de fixtures omitidas:** T2 necesita `structural/broken.md` para probar la equivalencia (`test-audit.md:43`); T6 necesita el inventario y las fuentes para resolver citas (`test-audit.md:47`). No son errores de selección, pero T3 debe declararlas para no implementar una versión más débil.
4. **Observaciones menores:** el regex de anclas de T7 (`\d{2}`) es más estricto que el ejemplo de `spec.md:105`; declararlo como convención del piloto o relajarlo. La fila PC-02 debe decir "no propuesto" en su fracción (a). T8 debe especificar las "cuatro combinaciones" que afirma (`test-audit.md:49`).

---

## 4. Bloqueantes

- **Del mapeo: ninguno.** La clasificación de las 15 PC, la selección de 8 controles y las condiciones C-1..C-4 son correctas y suficientes.
- **Hallazgo de proceso I-8:** no bloquea el mapeo, pero exige registro y decisión de la autoridad antes de T3 (§2.3). Condición de cierre: registro de la desviación + resolución del conflicto `PACKET.md:12` vs política de rutas, o rehacer el AUDIT en sesión limpia.
- **Condiciones de precisión §3:** deben trasladarse a T3; si T3 las omite, la fracción afectada vuelve a (b) o el mapa se enmienda. No cambian la selección ni el RED.

---

## 5. Veredicto

**El mapeo es suficiente y el RED declarado es legítimo.** Las quince PC están clasificadas sin que ninguna sesión real figure como control automático ni ninguna estructural se presente como fidelidad semántica; los 8 focales protegen consecuencias distintas sin huérfanos ni redundancias; C-1..C-4 son correctas contra el contrato; el oráculo es derivable del contrato y no del producto (que no existe); y la composición del RED — 7 verdes al crearse y T6 rojo por `AssertionError` — es exactamente la que fija el plan. Se registran como condiciones: el hallazgo de proceso I-8 (con su doble cierre posible) y las precisiones de fixtures de §3. Ninguna invalida la selección.

---

## 6. Lecturas declaradas y límites

**Leídas (inputs declarados):** `docs/specs/010-003-documentary-pilot/spec.md`, `plan.md`, `test-audit.md`, `discovery-decisions-2026-10-31.md`.

**Leídas fuera de los inputs, declaradas:**
- Plano de control de la ruta C: `.cdad/executions/exec-010-003-documentary-pilot-001/execution.json`, `.cdad/packets/…/REQUEST.json`, `PACKET.md`; listado de `.cdad/` y `find` para localizar `cdad_packet.py`.
- CLI `skills/cdad-cycle/scripts/cdad_packet.py` ejecutado (`validate-packet`, `render`, `render --route C`, `--help`); **no leí su fuente**.
- `tests/`: los tres archivos de test (grep/sed), `tests/conftest.py:55-70`, `tests/suite_signal_helpers.py:20-40`, y el contexto de `tests/test_003_002_t3_run_evidence.py:395-410` (fixture aislado, no el árbol real).
- Metadatos git de los tres archivos (`git status`, `git log -1`), sin contenido de implementación.

**No leídas:** código de implementación (`agents/`, `scripts/`, `sources/`, `build/`); `skills/cdad-cycle/references/*` — **no intenté la lectura**: el `objective` del encargo la prohíbe expresamente y ordena detenerse y reportarlo si el bloque del rol remite a ella (`PACKET.md:31`). El bloque común sí remite (`PACKET.md:12`); reporto la tensión y no la resolví leyendo por otra vía. Consecuencia: no pude verificar por texto la cita `documentary-contracts.md:11-13` de C-1; la conclusión se verificó contra el silencio del contrato.

**Límites honestos:** la declaración del AUDIT sobre sus lecturas es auto-reportada; no puedo probar ausencia de accesos no declarados. Las afirmaciones del AUDIT sobre `grep` en `scripts/` y `skills/` no las repetí (fuera de mi alcance); verifiqué `tests/`, que es la superficie que decide el impacto de la regresión. La estimación de que los 8 focales no lanzan procesos es de diseño (el código no existe aún).

---

## 7. Archivos y commit

**Archivos modificados:** ninguno.
**Commit:** ninguno. Este encargo no escribe; el orquestador materializa la evidencia del POST-AUDIT.
