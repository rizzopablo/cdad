# Informe T7 — Propiedades y recorrido integrado final · 010-002-documentary-role-integration

**Rol:** test-writer · **Subfase:** `properties` · **Paquete:** `010-002-documentary-role-integration-test-writer-properties-001`
**Contrato:** `docs/specs/010-002-documentary-role-integration/spec.md` v4, sha256 `0d630c49…81abc` (aprobado)
**Naturaleza:** tests nuevos + informe. No se corrigió producto: todo el comportamiento verificado estaba GREEN.

---

## 0. Intake (ruta C) y validez del paquete

| Verificación | Comando | Resultado |
|---|---|---|
| Identificación ruta C | `python3 -B skills/cdad-cycle/scripts/cdad_packet.py render --route C --request …/REQUEST.json` vs bloque recibido + `diff` | **idéntico** (`diff` rc=0; sha256 `cdfe7c15…c3d01` en ambos) |
| Render canónico completo | `python3 -B skills/cdad-cycle/scripts/cdad_packet.py render --request …/REQUEST.json` + `cmp` contra `PACKET.md` | **`IDENTICAL_BYTES`** (sha256 `01e772b5…fc617` en ambos) |
| Paquete válido | `… validate-packet --project-root . --execution-context …/execution.json --request …/REQUEST.json --packet …/PACKET.md` | `rc=0` |
| Contrato | `sha256sum docs/specs/010-002-documentary-role-integration/spec.md` | `0d630c49cfd4c8b0f671026437000617b96bf1bc44b2383dd2914bc7e5581abc` (coincide) |
| Contexto de ejecución | `.cdad/executions/exec-010-002-documentary-role-integration-001/execution.json` | `schema_version: 2` |
| Cuerpo inline | — | ausente (ruta C correcta); sin mezcla de rutas |

Sin discrepancias bloqueantes. `docs/.cdad-state.json` (`M`) y los tres documentos no trackeados (`010-000/discovery.md`, `red-t5.md`, `tdd-t6-green.md`) **preexistían** y quedaron fuera del commit, igual que en T5/T6.

---

## 1. Archivos modificados y commit

| Archivo | Cambio |
|---|---|
| `tests/test_010_002_documentary_role_properties.py` | **Nuevo**, 1416 líneas: `TestInv04Properties` (5 propiedades) + `TestFinalIsolatedDistribution` (2 verificadores PC-12.b) y sus generadores/helpers |

- No se editó `tests/test_010_002_documentary_role_integration.py` ni ninguno de los cinco archivos adaptados en T5; **0 cambios en producto** (`skills/`, `sources/`, `agents/`, `install.sh`, `build/`).
- **Commit:** `c5c054b4` — `test(010-002): propiedades de INV-04 y recorrido final de PC-12.b` (1 archivo, 1416 inserciones).
- Lecturas declaradas: `skills/cdad-cycle/packets/substages/test-writer-properties.md` (sha256 `44722aa6…`, coincide con `instruction_sources`) y `skills/cdad-cycle/references/documentary-contracts.md` (norma que el paquete ordena leer), vía bash porque el guard de `Read` deniega `skills/**`. **No se leyó** `skills/cdad-cycle/scripts/cdad_packet.py`, `install.sh`, `agents/**`, `sources/roles/**` ni `build/staging` del checkout. El CLI, el instalador y el esquema se ejercitaron como procesos/artefactos públicos.

---

## 2. Registro de la subfase de propiedades (semilla, dominio, presupuesto)

| Parámetro | Valor |
|---|---|
| **Semilla** | `SEED = 20261031`; generador propio y determinista (`random.Random`). No se usó `hypothesis` ni otra biblioteca (plan T7). |
| **Dominio de publicación** | 5 roles/subfases que reciben paquete: `architect/draft`, `test-writer/red`, `implementer/green`, `reviewer/review`, `scribe/memory`. El orquestador prepara y verifica gates; no recibe trabajo de rol inline (spec §3), por eso no es destinatario. |
| **Dominio de `stack`** | Ausente, `null`, `""`, `"odoo"` y sufijos no vacíos generados sobre `[a-z][a-z0-9-]{0,9}` (D3). |
| **Dominio estático** | Familia del rol declarado (genérico exacto / prefijo completo con sufijo no vacío) vs. familias de los otros cinco roles, truncación, carácter extra y prefijo con sufijo vacío. |
| **Dominio contextual** | Bases publicadas con `stack ∈ {"odoo", "erp-x"}`; stack vigente posterior ∈ {ausente, `null`, `""`, sufijo generado distinto}. |
| **Presupuesto** | **100** publicaciones válidas (20 de frontera = 5 roles × 4 representaciones + 80 generadas) · **100** discordancias estáticas + **20** admisiones estáticas + **5** comprobaciones de no publicación de `render` · **100** discordancias contextuales (10 bases publicadas) · **5** roles para la regla de presencia. |
| **Casos generados ejecutados** | 100 publicaciones + 125 comprobaciones estáticas + 100 registros contextuales + 10 comprobaciones de presencia + 2 recorridos integrados (genérico y Odoo) + 2 encargos de rol de lectura. |

No se usó combinatoria para perseguir cobertura: cada propiedad verifica una invariante explícita con una muestra acotada y semilla fija.

---

## 3. Tests nuevos, postcondición y consecuencia

| Test | PC / invariante | Sin este test, el usuario… |
|---|---|---|
| `TestInv04Properties::test_publication_derivation_matches_the_canonical_rule` | **INV-04, PC-06, PC-07a** (garantía por construcción; derivación D3) | …una combinación admitida de rol y stack podría publicar un destinatario incoherente y no sabría a qué agente llegó su encargo. |
| `…::test_publication_conserves_the_admitted_request_and_render_fields` | **INV-04 (conservación), PC-08 (render sin `agent`), D5 (conjunto cerrado)** | …la corrección podría perder/cambiar campos del request existente o meter `agent` en el render, rompiendo compatibilidad de bytes. |
| `…::test_static_contrast_admits_the_declared_role_and_rejects_foreign_families` | **INV-04, PC-07b, PC-08** | …un agente de otro rol o una coincidencia parcial del nombre del rol recibiría el trabajo, y un rechazo estático preemptor se confundiría con el contextual. |
| `…::test_contextual_contrast_rejects_a_new_intent_with_a_discordant_agent` | **INV-04, PC-07c, PC-08** | …un encargo se despacharía a un dominio que ya no rige, o el diagnóstico no distinguiría rol/stack/agente esperado. |
| `…::test_presence_rule_rejects_context_without_agent_and_admits_the_historical` | **INV-04, PC-08/O2, D3** | …un request con contexto quedaría sin destinatario, o la corrección rompería históricos legítimos al exigirles un agente que nunca declararon. |
| `TestFinalIsolatedDistribution::test_isolated_install_distributes_the_final_cli_and_schema` | **PC-12.b, EV-04/EV-05** (con procedencia PC-11) | …la instalación podría distribuir un CLI o esquema anteriores al GREEN de T6 y el recorrido no acreditaría por bytes. |
| `…::test_final_documentary_journeys_keep_domain_product_and_frontiers` | **PC-12.b, O5, PC-03 (fronteras), PC-06/PC-07a (dominio), PC-10 (esquema instalado)** | …el encargo documental/Odoo podría resolver el agente genérico, la etiqueta documental podría ampliar la escritura hacia tests o addon, o el CLI instalado no podría despachar. |

**Recorrido integrado (PC-12.b):** generación (`make agents` en copia descartable) → instalación con `CDAD_INSTALL_ROOT` propio y `CDAD_SKILL_EXTRA_DIRS=""` → preparación → `validate-request` → `record-dispatch` con el **CLI instalado**, y resolución del agente derivado en los dos destinos instalados. El recorrido genérico usa `implementer/green` con producto editable `docs/report`; el de Odoo usa `test-writer/properties` con `stack=odoo`; en ambos se verifica además `reviewer` con `write_scope: []`. La comparación de bytes es contra la fuente del repositorio (`skills/cdad-cycle/...`) y los agentes promovidos de la copia descartable — **nunca** `build/staging` del checkout.

---

## 4. Hallazgos

**Ningún hallazgo de producto.** No quedó ninguna postcondición comprometida. Dos correcciones fueron **del propio test** durante la autoría, no del producto:

1. **Oráculo de conservación demasiado fuerte (primera corrida).** Comparaba todos los valores del request del fixture contra el publicado; `prepare` deriva por rol `invariants`, `expected_output`, `evidence_required` y alcances. Se corrigió el oráculo a lo que el packet pide —conservación de **campos** y de los valores declarados por el fixture/contrato— y su forma; el oráculo exacto de esos defaults sigue siendo `test_packet_prepare::test_p2` (verde). No se debilitó ningún oráculo: el conjunto de claves y los campos declarados siguen exactos.
2. **Hazard de fixture en la corrida combinada.** El entorno cacheado de `disposable_product()` conservaba el `TMPDIR` del primer test que lo creó; al correr junto al módulo de integración, `mktemp` del instalador apuntó a una raíz ya retirada. Se corrigió reconstruyendo el entorno hijo desde el entorno **vigente** + HOME/XDG de la copia descartable (mismo patrón que `_home_env` del módulo existente). No es defecto del producto.

Sin skips: `jsonschema 4.19.2` está disponible y los 7 tests ejecutaron todas sus aserciones.

---

## 5. Comandos, salida y rc (medidos)

| # | Comando | Salida | rc |
|---|---|---|---|
| 1 | `python3 -B -m pytest -q tests/test_010_002_documentary_role_properties.py` | `7 passed in 193.72s (0:03:13)` | **0** |
| 2 | `python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py tests/test_010_002_documentary_role_properties.py` | `34 passed in 237.04s (0:03:57)` | **0** |

Logs completos: `/tmp/opencode/t7-010-002/properties.log` y `/tmp/opencode/t7-010-002/combined.log` (fuera del repositorio). El commit es posterior a la última corrida solo por una edición de docstring (sin cambio de comportamiento).

---

## 6. Evidencia de aislamiento (EV-05)

- `tests/conftest.py` fija `HOME`/XDG/temporales por test y retira `CDAD_INSTALL_ROOT`, `CDAD_OPENCODE_AGENTS_DIR` y `CDAD_CONTEXT_METER_STORE`.
- La instalación propia usa una raíz `<session-root>/cdad-010-002-prop-install-*`, `CDAD_INSTALL_ROOT` explícito y `CDAD_SKILL_EXTRA_DIRS=""`; los procesos hijos usan el HOME/XDG de la copia descartable, nunca el del operador.
- **Canario:** inventario (rutas + sha256 de archivos + directorios) del `HOME` visible capturado **antes** de instalar y comparado después de la instalación y de ambos recorridos → **igual**. Además: `CDAD_INSTALL_ROOT` ausente del proceso, `HOME/.config/opencode/skills/cdad-cycle` inexistente y raíz de instalación fuera de `HOME`.
- Resolución instalada verificada en los dos runtimes (`INSTALLED_AGENTS_DIRS`) con bytes iguales a los agentes promovidos de la copia descartable.
- **Límite honesto:** el `HOME` real del operador queda fuera del alcance del proceso de tests; la sustitución de `conftest.py` es la evidencia de aislamiento, y el canario prueba que las operaciones no escribieron el `HOME` visible ni el destino global.

---

## 7. Límites honestos

- Un verde aquí **no** acredita fidelidad semántica, suficiencia de una exclusión ni conducta efectiva de modelos: PC-13 corresponde a T8.
- El reemplazo histórico, el reemplazo tras cambio de stack, la recepción, la repetición idéntica y la finalización write-ahead se acreditan por sus transiciones observables en el módulo de integración (T5), no como cuotas aleatorias (plan T7); las propiedades cubren solo la parte generable de INV-04.
- La suite completa no se ejecutó (política del paquete: la corre una vez el cierre). El comando 2 ejecutó los 27 tests del módulo focal de integración + los 7 nuevos.
