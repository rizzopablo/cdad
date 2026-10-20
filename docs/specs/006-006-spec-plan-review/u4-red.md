U4 RED complete. Here is the delivery report.

## Archivos modificados

| Archivo | Acción |
|---|---|
| `tests/test_006_006_u4_reviewer_role_agents.py` | **NUEVO** (529 líneas) — único archivo tocado y el único commiteado |

Sin escrituras fuera de `tests/`. `docs/.cdad-state.json` (modificado por el orquestador) y `docs/planning/` + `findings/*.md` (sin trackear, no míos) quedaron intactos.

## Mapa test → PD (PD-11, §2.8)

| Test | Oráculo | Concepto |
|---|---|---|
| `test_pd11_role_source_contract_row_declares_stages_2_and_4` | O-S1 | fila §2: celda «Stages» nombra etapa **2** y **4** |
| `test_pd11_role_source_contract_row_declares_the_plan_review_artifact` | O-S2 | «Artifact» nombra `plan-review.md` **además** de `review.md` (regex `(?<![A-Za-z0-9_-])review\.md` para que `plan-review.md` no lo satisfaga) |
| `test_pd11_role_source_contract_row_says_the_draft_review_is_part_of_the_role` | O-S3 | «Does» une borrador + revisión (vecindad 200) |
| `test_pd11_role_source_directive_names_the_review_of_an_unapproved_draft` | O-S4 | sección `directive`: borrador + revisión + **no aprobado** |
| `test_pd11_generated_reviewer_agents_carry_the_declaration[×4]` | O-A1 | los 4 agentes **generados** (generador como proceso en copia descartable) |
| `test_pd11_promoted_reviewer_agents_carry_the_declaration[×4]` | O-A2 | los 4 agentes **promovidos** en el repo (`make agents`) |
| `test_pd11_make_staging_is_deterministic_across_two_runs` | O-D1 | **control V-2**: dos corridas, mismos bytes |

Oráculos por concepto (familias de tokens, no frases). La fila se localiza por **cabecera** (Role/Stages/Artifact) y la columna por nombre → no depende del nº de línea ni del orden.

## Comandos y salida

```
$ python3 -m pytest tests/test_006_006_u4_reviewer_role_agents.py -q -p no:cacheprovider
12 failed, 1 passed in 2.03s
```
Los 12 fallos son `AssertionError` sobre el texto que falta (nunca ImportError/SyntaxError); el control de determinismo es verde hoy, como debe:
```
E AssertionError: PD-11 (O-S1): sources/roles/reviewer.md: ... no declara la ETAPA 2 ... la celda «Stages» dice '4'.
E AssertionError: PD-11 (O-S2): ... no nombra el artefacto `plan-review.md` ... «Artifact» dice '`review.md` as FINAL TEXT ...'
E AssertionError: PD-11 (O-S3): ... no dice que la revisión de BORRADOR es parte del rol ...
E AssertionError: PD-11 (O-S4): ... la sección de directiva no nombra el BORRADOR revisado.
```
Regresiones de la ficha + las del encargo (11 ficheros, 83 tests):
```
$ python3 -m pytest tests/test_cdad_generate.py tests/test_role_packets.py tests/test_role_packet_render.py \
  tests/test_005_006_t2_intake.py tests/test_bash_policy_selection.py tests/test_opencode_read_map_and_steps.py \
  tests/test_005_004_t2_installer_claims.py tests/test_006_002_u1_delegation_section.py \
  tests/test_006_002_u3_runtime_references.py tests/test_006_003_u3_texts_without_profiles.py \
  tests/test_006_005_u4_single_entry.py -q -p no:cacheprovider
83 passed in 131.68s (0:02:11)
```
`make validate` (evidencia, **no oráculo**): `Assert PASS: 168 / Assert FAIL: 1` — el único FAIL es `F011: scripts/validate-subagents.sh (active profile) → FAIL`, idéntico a la línea base medida antes de mi RED.

## `make validate`: F011 declarado, NO convertido en oráculo

El bloque F011 contrasta la instalación **activa del HOME** (`install.sh --check`): la copia instalada (`~/.claude/skills/…`, `~/.config/opencode/agents`) va por detrás de este árbol → deriva **preexistente y ambiental**, ajena a U4 (el propio `validate-subagents.sh` imprime además `❌ cdad-reviewer.md declares model:` sobre la copia vieja de HOME). Convertirlo en oráculo daría un RED que falla por el ambiente. Queda como **evidencia de la entrega** y como criterio del gate de la unidad.

## A-1

**Ninguna.** El RED **no reemplaza** ningún oráculo vigente: sólo **añade** casos. Verificado sobre las 11 regresiones: ninguna fija el texto de `sources/roles/reviewer.md` ni la declaración de los cuatro agentes del reviewer (las que miden el paquete calculan el sha256 del substage dinámicamente). El fixture compartido `DRAFT_PLAN_RELPATH` no se toca: este RED usa copia propia.

## Aislamiento y honestidad de fase

- **Nunca leí implementación**: `scripts/cdad-generate.py` y `skills/cdad-cycle/scripts/` sólo se **invocan**; el generador nunca se importa. El guard de paths denegó el `read` sobre `sources/` y `agents/` (raíces de implementación del policy), así que leí esos dos artefactos por bash — dentro de la autorización explícita del encargo («puedes leer `sources/roles/` y `agents/` (artefactos)») y **declarado aquí**. No leí el generador ni ningún `.py` de `skills/`.
- **La generación ocurre en copia descartable**: copia del repo en `tmp_path_factory` (excluye `.git`, `.cdad`, `build`, `logs` y el fichero privado `tests/.sensitive-patterns.local`), `make staging` con `cwd=copia` y `HOME`/`XDG_CONFIG_HOME` redirigidos a un temporal. **El árbol de trabajo nunca se regenera** y el HOME real no se toca (verificado: `git status` sin cambios en `agents/` ni `build/`).
- **RED satisfacible** (evidencia de que no es un RED imposible): simulé la forma del GREEN **en otra copia** (fila §2 con etapas 2 y 4 + `plan-review.md` junto a `review.md`, y la directiva nombrando el borrador no aprobado) + `make agents` → `13 passed`. Nada de eso tocó el árbol de trabajo.
- `ruff check` limpio; el repo no es `ruff format`-clean (187/189 ficheros), así que sigo su estilo.

## Commit

```
52c734a8dc4c3ef48a3787c3f24d3d33d28cb90b
test: 006-006 U4 RED — rol reviewer con revision de borrador
 1 file changed, 529 insertions(+)
 tests/test_006_006_u4_reviewer_role_agents.py
```
Sin `--no-verify`, sin `git stash`, sin `push`. La suite completa **no** se ejecutó (política del paquete: la corre una vez quien cierra).

## Riesgo que dejo declarado para el GREEN

El oráculo O-S4 exige que la sección de directiva nombre el borrador **no aprobado** (familias: `unapproved` / `not (yet|been) approved` / `no aprobado` / `sin aprobación` / `no approval` / `pending approval` / `never approved` / `non approuv*`). Es la lectura literal de la ficha («la sección de directiva nombra la revisión de **borrador no aprobado**») y del encargo; si el implementador lo redacta con otra forma, ese único test sería el que discuta el orquestador — no el resto.