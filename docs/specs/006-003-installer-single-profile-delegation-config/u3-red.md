I'll start by reading the approved contract and the referenced tests.
Now let me read the tests I must reformulate and the plan's U3 sheet.
Now I have the state I need. Let me write the new focal test module.
Now the reformulations. First, `test_006_002_u4_skill_without_models.py` (concepts 6/7/8):
Now update the two test docstrings in that module that still describe the profile-based sentence:
Now the `test_006_002_u1_delegation_section.py` reformulation:
Now `test_005_010_t3_references.py` (the model-table pointer):
# Role report — test-writer / RED · `006-003-installer-single-profile-delegation-config` U3

Packet: `006-003-installer-single-profile-delegation-config-test-writer-red-004` · substage `red` · contract sha256 `32ed55c4…`.
Write scope respected: **only `tests/`**. Implementation (`install.sh`, `scripts/`, `skills/`, `sources/`, `agents/`) was never read as guidance — only asserted by the oracles at run time; the current-state survey used the contract's own `grep`-style oracles and **file/line metadata only**. `tests/.sensitive-patterns.local` untouched/unread.

## 1. Files

| File | Kind |
|---|---|
| `tests/test_006_003_u3_texts_without_profiles.py` | **new** — focal oracle (10 tests, 637 lines) |
| `tests/test_006_002_u4_skill_without_models.py` | reformulated (concepts 6/7/8) |
| `tests/test_006_002_u1_delegation_section.py` | reformulated (`basic` family branch inverted) |
| `tests/test_005_010_t3_references.py` | reformulated (model-table pointer inverted) |
| `tests/validate-consistency.sh` | reformulated (F001) |
| `tests/test_006_002_u5_transport_equivalence.py`, `tests/test_006_002_u6_context_discipline.py` | follow-up of the renamed staging fixture helper (`make staging`, no `PROFILE`) |

## 2. Test → postcondition map

| # | Test (new module) | Contract |
|---|---|---|
| 1 | `TestPd7a…::test_pd7a_installable_skill_tree_names_no_model` | PD-7a / INV-3 (`skills/**`, all files = `grep -rE`) |
| 2 | `TestPd7a…::test_pd7a_generated_orchestrators_name_no_model` | PD-7a / INV-3 (the two generated orchestrators) |
| 3 | `TestPd7bSkillSection2…::test_pd7b_skill_section2_has_no_profile_vocabulary` | PD-7b / D7 (§2: no `perfil/profile`, no `--basic`) |
| 4 | `TestPd7bSkillSection2…::test_pd7b_skill_section2_declares_the_family_as_configuration_verification` | PD-7b / INV-5 |
| 5 | `TestPd7bAdapterDelegationSections…::…have_no_profile_vocabulary` | PD-7b / D7 (both adapter `delegation` blocks) |
| 6 | `TestPd7bAdapterDelegationSections…::…declare_the_family_as_configuration_verification` | PD-7b / INV-5 |
| 7 | `TestPd7bGeneratedOrchestratorComposition…::…carry_no_profile_vocabulary` | PD-7b / D7 (composition) |
| 8 | `TestPd7bGeneratedOrchestratorComposition…::…declare_the_family_configuration_verification` | PD-7b / INV-5 (composition, co-located ±12 lines around the `reviewer` anchor) |
| 9 | `TestRetiredModelMapNotReferenced::test_retired_model_map_is_unreferenced_by_role_sources_and_generated_agents` | PD-1c / PD-7 / INV-3 (`sources/roles/*.md` + generated agents) |
| 10 | `TestInv4InstallableTextWithoutTmp::test_inv4_installable_skill_text_names_no_tmp` | INV-4 (non-regression) |

Declared oracle choices: PD-7a reuses the single `MODEL_NAME_RE` definition from U1's module; **no** `context-meter.md` exclusion (PD-7a doesn't declare one and the reader contract names no model today — excluding would weaken the oracle); §2 delimited with the shared `numbered_section_region`; adapter blocks with the generator's section grammar; concepts carry language alternatives, never exact phrases.

## 3. RED evidence (exact commands, summarized output)

```
$ python3 -m pytest tests/test_006_003_u3_texts_without_profiles.py -q
7 failed, 3 passed in 0.16s
```
- §2: `skills/cdad-cycle/SKILL.md:80`, `:81` — profile vocabulary (region 65-88); concepts `3. configuración` and `4. no verificable` absent.
- Adapters: `sources/agents/adapters/opencode.md:77`, `claude-code.md:96` — profile vocabulary inside the `delegation` block; concepts 2/3/5 absent.
- Orchestrators: `agents/cdad-orchestrator.md:201` + `:181 (--basic)`, same in `agents/claude-code/…`; config-verification concept absent around the reviewer anchor.
- Model map: 5 `sources/roles/*.md` + 21 generated agents still name `cdad-models.sh` (exact `file:line` list in the assertion).
- **Passing today (declared guards, not evidence of U3):** PD-7a (1)(2) and INV-4 (10) — U1 already removed model names from generated agents and `skills/**` is clean.

```
$ python3 -m pytest tests/test_006_002_u1_delegation_section.py \
    tests/test_006_002_u4_skill_without_models.py \
    tests/test_005_010_t3_references.py -q
4 failed, 16 passed in 2.48s
```
Failures are exactly the reformulated assertions (`TestPd4FamilyConfigurationDeclaration` ×2, `TestPd11Section2WithoutModels` ×2); `test_005_010_t3` is green as a declared guard (map already retired by U1).

```
$ python3 -m pytest tests/test_006_003_u3… tests/test_006_002_u1/u2/u3/u4/u5/u6 \
    tests/test_006_002_reviewfix.py tests/test_005_010_t3_references.py \
    tests/test_006_003_u1/u2 -q
11 failed, 58 passed in 41.80s        # same 11 declared REDs, zero collateral
```
```
$ python3 -m pytest tests/test_role_packets.py tests/test_packet_prepare.py \
    tests/test_role_packet_{consumers,render,review_regressions}.py -q
52 passed in 157.05s
```
```
$ bash tests/validate-consistency.sh | grep -E "F001|Assert PASS|Assert FAIL"
9 FAIL + 7 PASS in F001 (all nine are the reformulated PD-7b asserts)
Assert PASS: 157   Assert FAIL: 10
```
**Expected regression, declared:** `F011 → FAIL` is **pre-existing and environmental**, not caused by this RED — `bash scripts/validate-subagents.sh` reports drift between the repo and the *installed* copies (`~/.config/opencode/skills` has 85 files vs 84, `~/.claude` `__pycache__`). Tests-only changes cannot produce that; the closer should decide whether DT applies.

No failure anywhere is `ImportError`/`SyntaxError`/fixture failure (`py_compile` + `bash -n` OK on all touched files).

## 4. A-1 replacements declared (nothing deleted silently)

- **u4** concepts 6/7/8 → *configuration verification* / *not verifiable* / *declared*; the old "profile" condition becomes an **absence** (`PROFILES_PARAGRAPH_PATTERNS` second pattern replaced, rationale in-file).
- **u1** `TestPd4BasicFamilyDeclaration` → `TestPd4FamilyConfigurationDeclaration`: `basic` + "not guaranteed" co-location **inverted** into "no profile vocabulary, no `--basic`" plus the PD-7b concepts; registration fields / "never chooses" / "model only from configuration" preserved; staging fixture `make staging PROFILE=basic` → `make staging` (u5/u6 follow).
- **005-010 T3** pointer test → `test_pd10_model_pointer_retired_with_the_map`: asserts the map's **absence** instead of its existence, plus that the installable `cli-delegation.md` names it nowhere.
- **F001** (§2 and orchestrators) → profile absence + configuration-verification + not-verifiable/declared; comment block records the inversion.

## 5. Commit

```
54c6ac6 test: 006-003 U3 RED — textos instalables sin perfiles ni modelos (PD-7a/PD-7b, INV-3/4/5)
7 files changed, 953 insertions(+), 171 deletions(-)
```
Only `tests/` staged; `docs/planning/` and `findings/incremental-construction-…md` left untracked and untouched (not added). No `--no-verify`, no stash, no push.

## 6. Notes for the orchestrator

- The spec's PD-7a baseline ("hoy matchean los dos orquestadores") is **already satisfied** by U1; the U3 RED for model names is therefore a guard. All actual U3 failures come from PD-7b + the retired model map reference.
- Full suite **not** run (packet policy — the closer runs it once).
- Files U3 must touch to turn this green: `skills/cdad-cycle/SKILL.md` §2, `sources/agents/adapters/{opencode,claude-code}.md` (`delegation` section), regenerated `agents/**` (role sources lose the `cdad-models.sh` load), and `tests/` stays untouched by the implementer.
