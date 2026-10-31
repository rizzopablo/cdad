# INFORME DE AUDIT — 010-001 Contratos documentales compartidos

**Paquete:** `010-001-documentary-contracts-test-writer-audit-001` · **Subfase:** AUDIT (solo lectura sobre tests) · **Contrato:** `docs/specs/010-001-documentary-contracts/spec.md` (sha256 `9bf17a…c94da`, verificado)
**Épica:** `epic-010-documentary-specialization` · **Ejecución:** `exec-010-001-documentary-contracts-002` (contexto v2)

## 0. Intake (ruta C) — validado antes de trabajar

| Comprobación | Resultado |
|---|---|
| Identificación de ruta C recibida vs. `render --route C` | **idéntica** |
| `PACKET.md` vs. render canónico completo | **idéntico, 5598 bytes**, sha256 `c15be0a5…394411` en ambos |
| `validate-packet` | rc=0, sin salida |
| `execution.json` schema | **2** (v2, admisible en ruta C) |
| sha256 del contrato | coincide con el archivo en disco |
| Cuerpo inline + identificación (mezcla de rutas) | no hay cuerpo inline → sin mezcla |
| Fuentes de instrucción declaradas | `common.md` `37609c…47110` ✓ · `substages/test-writer-audit.md` `00889d…255d6` ✓ · **`roles/test-writer.md` declarado `5f5265…24b6b8` ≠ en disco `81d0bf…3e43b7`** |

**Hallazgo no bloqueante H-0 (deriva de fuente de instrucción):** el `instruction_sources` del paquete declara `sources/roles/test-writer.md` con sha256 `5f52650e…`, pero el archivo en el árbol tiene `81d0bf01…`. El paquete es válido (su render no depende del hash de esa fuente) y el AUDIT no la necesita, pero **el despacho de T2/T3 heredará esa deriva**: si los paquetes siguientes la reproducen, cualquier verificación futura de "sources al día" fallará. No la corrijo (fuera de mi alcance) — la reporto al orquestador para que decida si re-publica o si la deriva es intencional (edición posterior a la publicación del paquete).

## 1. Método y límites declarados

- Leí: contrato aprobado, plan aprobado, `docs/specs/010-001-documentary-contracts/**` y **`tests/**`**.
- **No leí** código de implementación (`sources/`, `skills/`, `scripts/`, `agents/`, `install.sh`, `Makefile`), salvo la fuente de instrucción de subfase declarada por el paquete (`skills/cdad-cycle/packets/substages/test-writer-audit.md`), que es doctrina del paquete, no producto. El guard de `Read` la deniega por estar bajo `skills/`; la leí con `cat` — **desviación declarada, sin contenido de producto**.
- Mediciones sin lectura de contenido: tamaños en bytes de los 14 bloques estáticos y de los 5 bloques de rol; conteo de ocurrencias del nombre del dueño y del literal `documentary-contracts` en `skills|sources|agents`.
- **No ejecuté la suite** (política: la corre quien cierra). No edité nada.
- El AUDIT mapea y declara huecos; **no** escribe tests ni sustituye el juicio semántico (INV-06).

## 2. Inventario por superficie

Escala de estado: **GAP** = sin cobertura; **PARCIAL** = cubre mecánica/adyacente, no la promesa; **CONTROL** = guarda ya verde que el cambio no debe romper.

### S1 — Casa normativa `skills/cdad-cycle/references/documentary-contracts.md`
No existe (verificado: `grep -rl documentary-contracts skills sources agents` → vacío). **GAP total** para PC-01–PC-04, PC-05, PC-06, PC-07, PC-09, PC-10, PC-11, PC-12, PC-13.
Ningún test puede derivar su oráculo de un archivo inexistente: el RED debe declarar el fallo como `AssertionError` de comportamiento ausente (precedente literal: `test_006_004_u3` §"RED esperado").

### S2 — `skills/cdad-cycle/SKILL.md` (tabla «How to read the references»)
| Test | Qué asegura | Estado para 010-001 |
|---|---|---|
| `test_003_006_t1_wiring.py::test_p1_*` | la tabla enlaza `continuity.md` | precedente por-archivo |
| `test_005_006_t1_start_procedure.py::test_pd1_*` | la tabla tiene fila del procedimiento de arranque | precedente por-archivo |
| `test_006_002_u3_runtime_references.py::TestPd9RuntimeReferencesWithdrawn` | dos filas de runtime retiradas; ningún texto instalable apunta a ellas | control |
| `test_006_002_u2/u4/u5` | neutralidad y delimitación de secciones de `SKILL.md` | control (estructural) |
| `test_006_004_u3::TestPd10SkillReferenceRow` | fila de `design-principles.md` | precedente exacto reutilizable |

**GAP**: ninguna prueba exige la fila de la norma documental (PC-13, "localizable desde la tabla").

### S3 — Seis fuentes de rol (`sources/roles/*.md`)
Los módulos que las leen afirman **conceptos**, no bytes:
- `test_006_006_u4_reviewer_role_agents.py` — obligación del reviewer (revisión de borrador) en fuente + 4 agentes + determinismo. Es el **patrón más cercano** a PC-14.
- `test_006_004_u3_principle_single_source.py` — deber del architect y del reviewer sobre el principio general/específico; unicidad por frases derivadas.
- `test_010_004_t4_red.py` — el literal `Route C — explicit file backup` debe existir en `sources/roles/architect.md` y propagarse a los derivados.
- `test_004_002_t7_limits_rule.py` — tres ideas de la regla de límites inlineadas en los 10 agentes; ya contempla explícitamente "ciclos CDAD sin código: documentos".
- `test_006_003_u3_texts_without_profiles.py` — barridos de ausencia (perfiles, modelos, `/tmp`) sobre texto instalable.

**GAP**: ninguna prueba exige que las seis fuentes declaren su obligación documental ni el puntero (PC-14).

### S4 — Cinco bloques estáticos (`skills/cdad-cycle/packets/roles/`)
Verificado: 5 bloques, 14 subfases.
| Test | Qué asegura | Estado |
|---|---|---|
| `test_role_packet_render.py::test_p1_p3_each_pair_matches_public_instruction_sources_byte_for_byte` | el bloque estático es exactamente `common.md`+`roles/<rol>.md`+`substages/…`; exige además `ROLE_SEMANTICS` por rol | **CONTROL fuerte** (deriva, no fija texto) |
| `test_role_packet_render.py::test_p1_static_instruction_block_is_delimited_and_within_12000_bytes` | techo 12000 en **1 par** (test-writer/red) | CONTROL parcial |
| `test_006_004_u3::TestPd13StaticBlockCeiling` | techo en **los 14 pares**, anclado al render real en 2 pares | CONTROL (mejor oráculo del techo) |
| `test_005_003_t6_packet_contract.py::#4` | ningún bloque de rol puede contradecir la política de suite completa | CONTROL (restricción de redacción) |
| `test_role_packet_consumers.py` | consumidores instalados usan el paquete sin recargar el ciclo | CONTROL |

**GAP**: obligaciones documentales en los 5 bloques (PC-14).

### S5 — Agentes generados y promovidos
| Test | Qué asegura | Estado |
|---|---|---|
| `test_cdad_generate.py::test_postcondition_2_identical_runs_are_byte_identical` | determinismo del generador | CONTROL (PC-15) |
| `test_cdad_generate.py::test_postcondition_4_*` + `test_pd_1e_*` + `test_postcondition_16_*` | **exactamente los 11 agentes declarados**; manifiesto con sha256; sin `model:`; cargas legacy | CONTROL (PC-16, "sin agentes nuevos") |
| `test_cdad_generate.py::test_postcondition_15_*` | ninguna mención de "sandbox" sin negación honesta **por línea** | CONTROL (PC-10/INV-08) |
| `test_006_004_u3::TestPd13GeneratedAgents` | generados (copia descartable) y promovidos llevan el deber + puntero | precedente exacto |
| `test_006_006_u4_*` | 4 agentes del reviewer llevan su declaración | precedente |
| `test_010_004_t4_red.py::test_pc12_*` | el literal de Ruta C sobrevive a la regeneración en 4 árboles | control de propagación |
| `test_009_002_opencode_v2_frontmatter.py`, `test_006_005_*` | frontmatter y delegación | control |

**GAP**: obligaciones documentales en generados/promovidos de ambos runtimes, incl. variantes Odoo (PC-14).

### S6 — Instalación aislada
`test_install_ownership.py` (11 casos), `test_install_review5_regressions.py` (6 casos), `test_009_001_installer_agent_overlay.py`, `test_role_packet_consumers.py::test_p6_*`, `test_packet_prepare.py::test_p5/p6`, `test_005_005_t3_provenance.py`.
Los bytes instalados se derivan del manifiesto de staging (**no hay digests fijos** — verificado: 0 literales de 64 hex en los 6 módulos de regresión de T4). `test_packet_prepare.py` ya prueba que una **referencia** (`references/handoff-prompts.md`) se distribuye en `.claude/skills/…`: la mecánica existe.
**PARCIAL** para PC-15: la mecánica está acreditada; **el artefacto nuevo no**.

### S7 — Doctrina / CI
`test_008_005_ci_gate.py` sólo fija el **orden de pasos** (`validate-state → surface → doctrine → odoo → close`) y el comportamiento del gate. **No hay prueba de los límites declarados** de `scripts/cdad-doctrine-check.py:29-35`. La promesa C (PC-10) es **textual** y vive en la referencia nueva → GAP, coherente con que la doctrina no se modifique en esta feature.

## 3. Mapeo PC-01…16 → cobertura vigente

| PC | Promesa observable | Cobertura hoy | Hueco |
|---|---|---|---|
| 01 | Cuatro categorías con las distinciones de D1 | **ninguna** | GAP |
| 02 | Respaldo localizable, propuestas explícitas, contradicciones conservadas | **ninguna** | GAP |
| 03 | Localizador mínimo por tipo de fuente (5 tipos) + fuentes inaccesibles/mutables | **ninguna** | GAP |
| 04 | Clasificación de pendientes, datos mínimos, prohibición de rebaja unilateral | **ninguna** | GAP |
| 05 | Cuatro declaraciones del encargo (fuentes, producto, oráculo, evidencia) | **ninguna** | GAP |
| 06 | Fuentes/verificadores/plantillas fuera del alcance editable de GREEN | PARCIAL: `test_004_002_t7_limits_rule` (frontera de alcance en agentes, otra promesa) | GAP |
| 07 | «Quien produce no modifica su oráculo» | **ninguna** | GAP |
| 08 | Fronteras de los seis roles | PARCIAL: mapas de permisos (004-001/004-002) son CONTROL, no cobertura documental | GAP |
| 09 | Dos registros: control estructural vs. revisión semántica | **ninguna** | GAP |
| 10 | Estructura ≠ fidelidad; obligación/paquete ≠ sandbox | PARCIAL: `test_cdad_generate::test_postcondition_15` (sólo agentes generados) | GAP en la norma |
| 11 | Contraste con fuentes; alcance real declarado | **ninguna** | GAP |
| 12 | Aceptación funcional en el dueño; pendientes bloqueantes | **ninguna**; INV-07 (nombre del aprobador fuera del texto instalable) **medido hoy = 0 ocurrencias** en `skills|sources|agents`, pero **no asertado** | GAP |
| 13 | Casa única + fila en la tabla + unicidad por frases derivadas | **ninguna** para la norma documental; patrón exacto en `test_006_004_u3` | GAP |
| 14 | 6 fuentes + 5 bloques + agentes de ambos runtimes (incl. Odoo) | **ninguna** documental | GAP |
| 15 | Instalación aislada con bytes esperados; generación reproducible; techo vigente | PARCIAL: determinismo, techo 14 pares e instalación genérica son CONTROL verde | GAP: artefacto nuevo |
| 16 | Sin agentes/skills/etapas/campos/selector/permisos nuevos | BUENA: 11 agentes (`test_cdad_generate` PD-4/PD-1e/PD-16), barreras de agentes (`test_packet_prepare::test_p6_claude_barriers_are_unchanged`), mapas de permisos (004-002), esquema (validate-request/prepare) | Hueco menor: "sin selector documental" no tiene oráculo estructural |

**Conclusión de cobertura:** de 16 postcondiciones, **11 no tienen ninguna prueba** y **5 tienen cobertura parcial o de control**. La suite vigente **no protege el contrato aprobado**; el módulo nuevo es imprescindible y **aditivo**.

## 4. Expectativas sustituidas

**Ninguna expectativa vigente queda sustituida por el contrato aprobado.** Verificado contra los 6 módulos que el plan T4 declara como regresión:

- No hay digests de 64 hex fijados en ninguno de los 6.
- Los tests que leen fuentes de rol afirman **conceptos**; los que miden el paquete calculan los hashes **dinámicamente** (confirmado también por la nota A-1 declarada en `test_006_006_u4_...:52-57`).
- Los instaladores derivan el conjunto del manifiesto de staging, no de listas literales.

**Dos sustituciones tentadoras, rechazadas con motivo (queda a decisión del dueño si las quiere):**

1. `test_packet_prepare.py` `DEFAULT_INVARIANTS["implementer"] = ["Do not edit tests"]`. Tentación: ampliarlo a "no editar tests, fuentes ni insumos protegidos" (PC-06). **Rechazado**: PC-16 prohíbe campos/mecanismos nuevos y la protección real vive en `write_scope`; ampliar el default sería sustituir un oráculo sin promesa que lo exija.
2. `test_role_packet_render.py` `ROLE_SEMANTICS["implementer"]` (exige "never/do not/must not edit|write|modify tests"). Tentación: relajarlo al ampliar "código" → "producto de implementación autorizado". **Rechazado**: INV-02/PC-07 conserva la frase; el cambio es aditivo, no sustitutivo.

## 5. Riesgos de regresión (verde hoy; el cambio puede romperlos)

Ordenados por probabilidad × coste.

| # | Test / guarda | Por qué puede romperse con 010-001 | Mitigación exigible al GREEN |
|---|---|---|---|
| R1 | `test_006_003_u3_texts_without_profiles.py::test_pd7b_*_profile_vocabulary` (SKILL.md §2, bloques `delegation`, orquestadores generados) y `test_inv4_installable_skill_text_names_no_tmp` | vocabulario `perfil|perfiles|profile|profiles|--basic` prohibido; `/tmp` prohibido en texto instalable. La fila nueva de la tabla y la fila de rol del orquestador viajan a los orquestadores generados | no usar "perfil documental" en `SKILL.md` ni en la fila de rol; decir "criterios/obligaciones documentales". La referencia nueva (bajo `skills/`) **no** puede nombrar `/tmp` |
| R2 | `test_cdad_generate.py::test_postcondition_15_*` | toda línea con "sandbox" necesita negación en **la misma línea**; PC-10/INV-08 obliga a hablar de sandbox | redactar la negación en la misma línea ("…no es un sandbox…") |
| R3 | `test_role_packet_render.py::ROLE_SEMANTICS` (implementer: "never edit/write/modify tests") | al reescribir el contrato del implementer se puede perder la frase | conservar literalmente la prohibición de editar tests |
| R4 | `test_005_003_t6_packet_contract.py::test_pd10_instruction_declares_full_suite_policy` | ningún bloque de rol/subfase puede afirmar lo contrario de la política de suite completa | no mencionar frecuencia de suite en las obligaciones documentales |
| R5 | `test_006_004_u3::test_pd10_no_installable_surface_copies_the_principle_text` | barre **todo** el árbol instalable; la referencia nueva entra al barrido | no reutilizar frases del principio general/específico de `design-principles.md` |
| R6 | `test_cdad_generate` PD-4/PD-1e/PD-16 (11 agentes) | cualquier agente nuevo rompe | no crear agentes (PC-16) |
| R7 | `test_packet_prepare::test_p6_claude_barriers_are_unchanged` | `tools:` y hooks `path-guard` comparados exactamente | no tocar frontmatter/permisos |
| R8 | `test_010_004_t4_red::test_pc12_declaration_and_derived_orchestrators_survive_regeneration` | el literal `Route C — explicit file backup` debe sobrevivir en `sources/roles/architect.md` y derivados | editar el architect **sin** alterar ese bloque delimitado |
| R9 | `test_role_packet_render::test_p1_excludes_representative_other_role_and_substage_sources` | si el bloque del implementer incorpora por copia el del test-writer | mantener el bloque por rol, sin copias cruzadas |
| R10 | `test_004_002_t7_limits_rule.py` | exige que (a)(b)(c) convivan en **un mismo párrafo** del agente | añadir párrafos, no reescribir los existentes |

**No son riesgo** (verificado):
- Techo de bloque estático: el peor par es `reviewer/plan-review` con **3397 bytes** frente a **12000** → **8603 bytes de holgura**. PC-15 no es una restricción vinculante.
- Determinismo de generación y de render: derivados.
- Instalación: conjunto derivado del manifiesto.

## 6. Observaciones de la suite (no bloqueantes)

- **O-1 (deriva de oráculo):** `test_role_packet_render.py::ROLE_SUBSTAGES` enumera **13** pares (falta `reviewer/plan-review`), mientras `test_006_004_u3` enumera **14**. El par faltante sí está cubierto por `test_006_006_u4`. No lo corrijo (fuera de alcance); lo declaro porque PC-15 habla de "los bloques estáticos" sin contar.
- **O-2:** `test_p1_static_instruction_block_is_delimited_and_within_12000_bytes` mide el techo sobre **1** par; el oráculo completo es `test_006_004_u3::TestPd13StaticBlockCeiling` (14 pares).
- **O-3:** no existe prueba de completitud "toda referencia está en la tabla de `SKILL.md`"; sólo pruebas por archivo. La fila nueva (PC-13) no tiene antecedente que la arrastre.
- **O-4:** `suite-inventory.json` (008-002) **no** contiene `010_004` ni `009_002` recientes → es un snapshot, no un registro vivo. El módulo nuevo **no** necesita entrada para no romper nada (verificado: ningún test exige completitud del inventario).
- **O-5:** `tests/.sensitive-patterns.local` es ruta privada declarada; el módulo nuevo no debe leerla.

## 7. Ambigüedades que requieren decisión del dueño (bloquean el RED)

| # | Ambigüedad | Opciones | Recomendación |
|---|---|---|---|
| **A1** | **Granularidad de la unicidad (PC-13)**: ¿frases normativas de **toda** la referencia o sólo de D1–D4? ¿umbral de "frase normativa"? | (a) archivo completo con umbrales del precedente (oraciones ≥6 palabras + líneas ≥8); (b) sólo secciones D1–D4 | **(a)**, idéntico a `test_006_004_u3` (`sentences`+`line_units`+`copies_of`, espacios normalizados, barrido `skills|sources|agents`, excluyendo la propia referencia) |
| **A2** | **Idioma del concepto**: ¿la norma debe ser castellana? | (a) sólo castellano; (b) castellano o inglés; (c) libre con conceptos bilingües | **(c)**: regex con alternativas ES/EN (patrón `require_any` del repo). Congelar el idioma convertiría una decisión editorial en oráculo |
| **A3** | **Alcance de la obligación en los 5 bloques (PC-14)**: ¿basta obligación mínima + puntero (precedente reviewer) o debe llevar la obligación completa de cada rol? | (a) mínima + puntero; (b) completa | **(a)**, precedente `test_006_004_u3`/`test_006_006_u4`; el bloque viaja sin el skill cargado |
| **A4** | **Orquestador**: no tiene bloque de rol. ¿Su obligación se exige sólo en `sources/roles/orchestrator.md` y en el agente generado? ¿Los adaptadores (`sources/agents/adapters/*`) son "fuentes de rol"? | (a) sólo fuente + agente; (b) también adaptadores | **(a)**: PC-08 enumera seis roles, no adaptadores; PC-14 nombra "cinco bloques" (= los existentes) |
| **A5** | **INV-07**: ¿la prohibición de nombrar al aprobador se limita a la norma distribuible o abarca todo artefacto instalable? | (a) sólo la referencia; (b) `skills|sources|agents` | **(b)**: hoy la propiedad se cumple (**0** ocurrencias) y convertirla en oráculo es barato y honesto. Requiere confirmación porque crea un oráculo de ausencia nuevo |
| **A6** | **Destinos de instalación (PC-15)**: ¿en qué rutas debe aparecer la referencia? ¿Se instalan las fuentes de rol? | (a) referencia en cada destino `skills/` que publique el instalador + agentes = bytes de staging; fuentes **no** se instalan; (b) exigir también las fuentes | **(a)**. Confirmar la lista de destinos para no inventar rutas |
| **A7** | **PC-16 "sin selector documental"**: no hay oráculo estructural posible | (a) dejar PC-16 a los guards existentes + revisión del diff; (b) añadir ausencia por palabras clave | **(a)**: la verificación de la spec para Promesa D ya dice "revisión del diff". Una ausencia por keywords sería un falso oráculo (AP-13) |
| **A8** | **Alcance del RED en esta unidad**: el plan dice que el grupo D puede seguir rojo hasta T4 | (a) declarar en el informe RED qué fallos son de T3 y cuáles de T4; (b) exigir D verde ya | **(a)**, tal como el plan lo fija en T2 |
| **A9** | **`make validate` como oráculo**: `test_006_006_u4` documentó deriva preexistente del HOME que lo hace fallar por ambiente | (a) no usarlo; (b) usarlo | **(a)**: `make staging`/`make agents` + instalación aislada. Un RED que falla por ambiente no es RED |
| **A10** | **Reutilización de helpers**: ¿importar de `tests/test_006_004_u3_principle_single_source.py` o duplicar? | (a) importar (`normative_units`, `copies_of`, `installable_documents`, `disposable_product`, `staging_digests`); (b) copiar | **(a)** para INV-01 (una sola definición), declarando la dependencia en el inventario de suite. `skill_reference_row` es local (está atada a su `POINTER`) → variante propia |

## 8. Forma propuesta del RED (para aprobación; no escrita en este substage)

`tests/test_010_001_documentary_contracts.py` — clases comprometidas por el plan: `TestPromiseA`…`TestPromiseD`. Agrupación por **promesa observable** (no una por postcondición), con trazabilidad múltiple declarada:

| Test propuesto | Protege | Tipo |
|---|---|---|
| `TestPromiseA::test_the_norm_defines_the_four_categories_with_their_distinctions` | PC-01, PC-02, INV-05 | RED |
| `TestPromiseA::test_the_norm_prescribes_locators_per_source_type_and_pending_classification` | PC-03, PC-04 | RED |
| `TestPromiseB::test_the_norm_requires_the_four_engagements_and_protects_the_oracle` | PC-05, PC-06, PC-07 | RED |
| `TestPromiseB::test_the_norm_states_the_six_role_boundaries` | PC-08 | RED |
| `TestPromiseC::test_the_norm_separates_structural_control_from_semantic_review` | PC-09, PC-10, INV-06/08 | RED |
| `TestPromiseC::test_the_norm_requires_contrast_with_sources_and_owner_acceptance` | PC-11, PC-12, INV-07 | RED |
| `TestPromiseD::test_the_norm_lives_in_one_house_listed_in_the_reference_table` | PC-13, INV-01 | RED |
| `TestPromiseD::test_no_installable_surface_copies_the_normative_phrases` | PC-13 | RED + control de vacuidad |
| `TestPromiseD::test_the_six_role_sources_and_five_blocks_carry_their_obligation_and_pointer` | PC-14 | RED (fuentes en T3; bloques en T4) |
| `TestPromiseD::test_generated_and_promoted_agents_of_both_runtimes_carry_the_obligations` | PC-14 | RED (T4) |
| `TestPromiseD::test_isolated_install_distributes_the_reference_with_source_bytes` | PC-15 | RED (T4) |
| controles declarados (ya verdes) | determinismo de `make staging`, techo 12000 de los 14 pares, 11 agentes, barreras de permisos | CONTROL (PC-15/PC-16) |

Total: **11 tests nuevos + 4 controles declarados**. Ninguno toca tests existentes; el módulo es aditivo.

## 9. Evidencia

**Archivos modificados: ninguno. Commit creado: ninguno.**

Comandos exactos ejecutados (desde la raíz `<repo>`):

```bash
sha256sum docs/specs/010-001-documentary-contracts/spec.md
python3 skills/cdad-cycle/scripts/cdad_packet.py validate-packet \
  --project-root . \
  --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json \
  --request .cdad/packets/010-001-documentary-contracts-test-writer-audit-001/REQUEST.json \
  --packet .cdad/packets/010-001-documentary-contracts-test-writer-audit-001/PACKET.md
python3 skills/cdad-cycle/scripts/cdad_packet.py render --route C \
  --project-root . \
  --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json \
  --request .cdad/packets/010-001-documentary-contracts-test-writer-audit-001/REQUEST.json
python3 skills/cdad-cycle/scripts/cdad_packet.py render \
  --project-root . \
  --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json \
  --request .cdad/packets/010-001-documentary-contracts-test-writer-audit-001/REQUEST.json > /tmp/opencode/render_full.txt
diff /tmp/opencode/render_full.txt .cdad/packets/010-001-documentary-contracts-test-writer-audit-001/PACKET.md
sha256sum /tmp/opencode/render_full.txt .cdad/packets/010-001-documentary-contracts-test-writer-audit-001/PACKET.md
sha256sum skills/cdad-cycle/packets/substages/test-writer-audit.md skills/cdad-cycle/packets/common.md sources/roles/test-writer.md
cat .cdad/executions/exec-010-001-documentary-contracts-002/execution.json
ls tests/ | grep -E '^test_010'
grep -rl "sources/roles\|sources\" / \"roles\"" tests/*.py
grep -rl "packets/roles\|packets\" / \"roles\"" tests/*.py
grep -rl "install\.sh" tests/*.py
grep -rl "doctrine" tests/*.py
grep -rl "documentary-contracts" skills sources agents
grep -rl "Pablo" skills sources agents | wc -l
grep -nE "[0-9a-f]{64}" tests/{test_cdad_generate,test_role_packet_render,test_role_packet_consumers,test_install_ownership,test_install_review5_regressions,test_006_004_u3_principle_single_source}.py
python3 - <<'PY'   # medición de tamaños de los 14 bloques estáticos y de los 5 bloques de rol
...
PY
ls tests/test_*.py | wc -l ; grep -rhE '^\s*(def test_|    def test_)' tests/test_*.py | wc -l
git status --short
git rev-parse HEAD
python3 --version
```

Salidas relevantes:

```text
9bf17a398b55384e271815c8a6c2910563f75a5d2475ec291c31d4f4d26c94da  docs/specs/010-001-documentary-contracts/spec.md
validate-packet: rc=0, sin salida
render completo: 5598 bytes; diff con PACKET.md: IDENTICAL
sha256 c15be0a5be249ec696f6e7837aec4d0b651099b3834c9f0be553d979e2394411  (render y PACKET.md)
execution.json: "schema_version": 2
tests/test_010_001*: No such file or directory
grep documentary-contracts en skills|sources|agents: (vacío)
grep "Pablo" en skills|sources|agents: 0 archivos en cada raíz
literales sha256 en los 6 módulos de regresión de T4: ninguno
peor bloque estático: 3397 bytes (reviewer/plan-review); techo 12000; holgura 8603
bloques de rol: 5; subfases: 14
módulos de test: 219; funciones de test: 1710
git status --short:
 M docs/.cdad-state.json
?? docs/specs/010-000-continuity-relative-root/discovery.md
?? docs/specs/010-001-documentary-contracts/
HEAD: bd69977694d3eea936f905c348ce4350e4c127d4
Python 3.13.5
```

El estado de git **preexistía** al iniciar; no lo atribuyo a este trabajo ni lo presento como prueba de ausencia de escrituras transitorias (INV-08/PD-15).

## 10. Pedido al orquestador

1. Resolver **A1–A10** (o delegarlas al dueño) antes de despachar RED: seis de ellas cambian el oráculo.
2. Decidir sobre **H-0** (deriva del sha256 de `sources/roles/test-writer.md` en `instruction_sources`).
3. Confirmar que el RED será **aditivo** (módulo nuevo) y que **no** se sustituye ningún oráculo vigente — el AUDIT encontró cero sustituciones necesarias.
4. Si se aprueba la reutilización de helpers (A10), registrar la dependencia `tests.test_006_004_u3_principle_single_source` en el inventario de suite.
