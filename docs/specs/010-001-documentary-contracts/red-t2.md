## FINAL TEXT — Informe RED · 010-001 contratos documentales compartidos (T2)

### 1. Intake (ruta C) — validado antes de trabajar

| Comprobación | Resultado |
|---|---|
| Identificación recibida vs. `render --route C` | **idéntica** |
| `validate-packet` (REQUEST + PACKET + execution) | **rc=0**, sin salida |
| `execution.json` `schema_version` | **2** (v2, admisible en ruta C) |
| sha256 del contrato vs. `spec.md` en disco | `9bf17a398b55384e271815c8a6c2910563f75a5d2475ec291c31d4f4d26c94da` — **coincide** |
| `tdd_substage` del state | `red` — coincide con el paquete |
| Cuerpo inline junto a la identificación | **no hay** → sin mezcla de rutas |

### 2. Archivos modificados y commit

- **Nuevo:** `tests/test_010_001_documentary_contracts.py` (1404 líneas, sha256 `970d3977ba64acdaef73d11944899998cb67c11e97514285d26cbadc4ac6f9e5`).
- **Commit:** `6e9ef3b6818dbeb76b72ba0bee96d27292ead51a` — `test(010-001): RED T2 - once pruebas por promesa (A-D) y cuatro controles declarados` (1 archivo, +1404).
- **Ningún test existente modificado** (`git diff HEAD -- tests` vacío; el working tree conserva intacto el estado preexistente de `docs/`).

### 3. Comandos exactos y salida

```bash
python3 -B -m unittest tests.test_010_001_documentary_contracts
```
```text
Ran 11 tests in 0.524s
FAILED (failures=64)
```
`grep -c '^ERROR:'` → **0**. Todos los fallos son `AssertionError` de comportamiento ausente (ningún `ImportError`, `SyntaxError` ni error de fixture; los artefactos que faltan se declaran con `read_document`/`assertTrue`).

```bash
python3 -B -m unittest \
  tests.test_006_004_u3_principle_single_source.TestPd13GeneratedAgents.test_pd13_make_staging_is_deterministic_across_two_runs \
  tests.test_006_004_u3_principle_single_source.TestPd13StaticBlockCeiling.test_pd13_the_static_block_of_the_fourteen_role_substage_pairs_is_under_the_ceiling \
  tests.test_cdad_generate.TestDeterministicGenerator.test_pd_1e_generated_agents_carry_no_model_line \
  tests.test_packet_prepare.TestPreparedInstalled.test_p6_claude_barriers_are_unchanged
```
```text
Ran 4 tests in 9.338s
OK
PD-13/V-4: máximo 3397 bytes (reviewer/plan-review), techo declarado 12000 bytes
```

### 4. Mapeo test → promesa → postcondiciones (11 tests, 64 fallos por subtest)

| # | Test | Promesa / PCs | Causa del fallo hoy |
|---|---|---|---|
| 1 | `TestPromiseA::test_the_norm_defines_the_four_categories_with_their_distinctions` | A · PC-01, PC-02, INV-05 | la casa no existe |
| 2 | `TestPromiseA::test_the_norm_prescribes_locators_per_source_type_and_pending_classification` | A · PC-03, PC-04 | la casa no existe |
| 3 | `TestPromiseB::test_the_norm_requires_the_four_engagements_and_protects_the_oracle` | B · PC-05, PC-06, PC-07 | la casa no existe |
| 4 | `TestPromiseB::test_the_norm_states_the_six_role_boundaries` | B · PC-08 | la casa no existe |
| 5 | `TestPromiseC::test_the_norm_separates_structural_control_from_semantic_review` | C · PC-09, PC-10, INV-06/08 | la casa no existe |
| 6 | `TestPromiseC::test_the_norm_requires_contrast_with_sources_and_owner_acceptance` | C · PC-11, PC-12, INV-07 | la casa no existe |
| 7 | `TestPromiseD::test_the_norm_lives_in_one_house_listed_in_the_reference_table` | D · PC-13, INV-01 | la casa no existe |
| 8 | `TestPromiseD::test_no_installable_surface_copies_the_normative_phrases` | D · PC-13, INV-01 | la casa no existe (y control de vacuidad preparado) |
| 9 | `TestPromiseD::test_the_six_role_sources_and_five_blocks_carry_their_obligation_and_pointer` | D · PC-14 | 6 fuentes + 5 bloques sin puntero `documentary-contracts.md` |
| 10 | `TestPromiseD::test_generated_and_promoted_agents_of_both_runtimes_carry_the_obligations` | D · PC-14 | 22 generados + 22 promovidos (11 × 2 runtimes, incl. Odoo) sin puntero |
| 11 | `TestPromiseD::test_isolated_install_distributes_the_reference_with_source_bytes` | D · PC-15 | la referencia no existe en la raíz de producto |

Los 44 fallos del test 10 confirman además que el conjunto declarado de **11 agentes por runtime** existe de hecho en generados y promovidos (el fallo es el puntero, no la ausencia de archivo): orquestador sin variante Odoo, 5 roles con genérico + Odoo, en `opencode` y `claude-code`.

### 5. Separación T3 / T4 (A8)

- **T3 (contenido normativo y consumidores de fuente):** tests 1–6, test 7 (casa + fila de `SKILL.md`) y la mitad «fuentes de rol» del test 9 (6 subtest).
- **T4 (transporte y distribución):** test 8 (unicidad medida sobre el árbol instalable final), la mitad «bloques estáticos» del test 9 (5 subtest), test 10 (agentes) y test 11 (instalación aislada).
- El grupo D puede seguir rojo hasta T4 conforme al plan; si el test 8 ya quedara verde al cerrar T3 (fuentes parafraseadas, bloques aún sin tocar), se informará como tal, pero su garantía de cierre es T4.

### 6. Controles declarados (verdes hoy, no reimplementados — INV-01/A10)

Determinismo de `make staging`, techo de 12000 en los 14 pares, exactamente 11 agentes por runtime y barreras de permisos de Claude Code: se declaran en el docstring con sus selectores exactos y se ejecutaron focalizadamente (**rc=0, 4/4 OK**). No son la falla; son guardas que deben seguir verdes. `make validate` no se usó (A9) y la suite completa no se ejecutó (política: la corre quien cierra).

### 7. Interfaz declarada al implementer (publicada en el módulo)

1. La casa es `skills/cdad-cycle/references/documentary-contracts.md`; puntero verbatim `documentary-contracts.md` (nombre de archivo, no redacción).
2. Conceptos con alternativas ES/EN, insensibles a acentos/mayúsculas/ajuste de línea (A2); no se congela idioma ni párrafos.
3. Unicidad (A1): frases normativas de **toda** la referencia, umbrales del precedente (`sentences` ≥6 palabras, `line_units` ≥8), espacios normalizados, barrido `skills|sources|agents` **excluyendo la propia referencia**. Las obligaciones de rol se **parafrasean**; tampoco se copian frases ya existentes hacia la referencia (habría dos casas de la misma frase).
4. Seis fuentes con obligación completa + puntero; cinco bloques con obligación **mínima** + puntero (A3); orquestador sólo en su fuente y agente, sin bloque ni adaptadores (A4).
5. Agentes generados y promovidos de ambos runtimes con puntero + obligación mínima, incluidas variantes Odoo.
6. Instalación aislada: la referencia con los **bytes de la fuente** en los dos destinos `skills/cdad-cycle` que declaran los tests del instalador (A6, sin rutas inventadas); los agentes con los **bytes de staging**.
7. INV-07 como ausencia del nombre del aprobador de esta unidad en `skills/`, `sources/` y `agents/`, con control de vacuidad (A5). PC-16 queda en los guards existentes y la revisión del diff (A7).
8. Dependencias declaradas (A10): `copies_of`, `normative_units`, `installable_documents`, `disposable_product`, `normalized`, `read_document`, `relative` del precedente `test_006_004_u3`; destinos de `test_004_001_t6`; staging de `product_root()`. **No** se reutiliza `staging_digests` porque está atada al subconjunto architect/reviewer y este oráculo mide los 11 agentes de ambos runtimes (mezclaría alcances y perdería cobertura) — desviación declarada con motivo.

### 8. Límites y desviaciones declarados (PD-15 / INV-06/INV-08)

- Las comprobaciones son **estructurales**: un verde no acredita fidelidad semántica ni aceptación funcional (eso es T5 y el dueño). El módulo no es un sandbox ni prueba ausencia de escrituras transitorias.
- **Desviación declarada (honesta):** la primera corrida del borrador usó `assertIn` con el archivo completo como contenedor y el mensaje de fallo **volcó texto de `sources/roles/*.md` y de los agentes generados** en la salida. El oráculo ya estaba escrito y no cambió un solo concepto al corregirlo (`assertIn` → `assertTrue`, sólo mensajes). No se leyó código de implementación (`scripts/`, `install.sh`, `skills/`); `make agents` / `make staging` / `install.sh` se ejecutaron **en negro** desde los tests (copia descartable y `CDAD_INSTALL_ROOT` temporal; el árbol real sólo ganó el módulo nuevo).
- La raíz de producto puede ser el checkout si ya tiene `build/staging`; con staging obsoleto el test 11 falla honestamente (hay que correr `make staging` en T4), nunca por ambiente.
- No se usó `make validate` como oráculo ni se ejecutó la suite completa.
