I'll start by reading the contract (spec, including Enmienda 001) and the existing test file.
Now I understand the contract. Let me check the remaining u5 test and the test directory listing to confirm no other test fixes the "never /tmp" rule.
No other test fixes the "never /tmp" rule (`tests/validate-consistency.sh` has zero `/tmp` matches; u5 only names `.cdad/inbox`). Now let me reformulate the module.
Now the constants block:
Now replace the rule-4 test class:
Now let me run the reformulated module to observe the RED (before finalizing the docstring's observed section):
Test (b) fails for the right reason (missing "same process" concept). Test (a) passed — my (a) oracle isn't yet discriminating, because the amended rule 4 ties the durable→stable clause to the `/tmp` mention (one rule). Let me anchor (a) on the `/tmp` mention and re-order (b):
The (b) negative check needs a sharper discriminator, and (a)'s "durable" group is too broad (satisfied by the mere word "receipt"). Let me tighten both, contract-faithfully:
Now the (c) absence oracle with the sharper "place/channel" detector:
Both rule-4 tests now fail by assertion. Let me make (b) report both halves in one run (same postcondition), then capture the full evidence:
Now update the module docstring's observed-RED section with the actual observations:
Let me self-check the oracle with a synthetic contract-faithful text (and an absolute-prohibition text) — never touching implementation:
The oracle accepts a contract-faithful text and rejects the absolute rule. Let me review the final diff, then commit only `tests/`:
## Report — test-writer / RED (packet `006-002-delegation-by-layer-test-writer-red-008`)

### 1. Modified files (write scope `tests/**` only)

```
 M tests/test_006_002_u6_context_discipline.py   (+260 / −84)
```

Commit: **`b9d9455` `test: 006-002 enmienda 001 RED — regla 4 de contexto relativizada`** (only `tests/`; `docs/planning/` and `findings/…` left untracked and untouched — verified with `git status --porcelain`).

### 2. What changed (contract: spec «Enmienda 001 — regla 4 de contexto», 2026-10-17)

The three rule-4 oracles were reformulated; rules 1–3, the `orientation.md`-owner citation, the staging fixture and the helper machinery (`read`, `rule_units`, `rule_region`, `assert_rule`, `require_any` reuse) are unchanged.

**Test → PD map (reformulated entries in bold):**

| # | Test | PD |
|---|---|---|
| 1 | `TestPd6Rule1OrientationFirst::…orient_first_with_the_compact_status_view_without_dumps` | PD-6(1) (guard) |
| 2 | `TestPd6Rule2SessionRotation::…rotate_the_session_at_task_boundaries_not_mid_unit` | PD-6(2) (guard) |
| 3 | `TestPd6Rule3NoSelfRepair::…no_self_repair_redispatch_the_role_naming_the_defect` | PD-6(3) (guard) |
| **4** | **`TestPd6Rule4TmpRelativized::…durable_evidence_and_cross_role_reads_go_to_stable_workspace_paths`** | **PD-6(4)/INV-4 enmienda 001 (a)** |
| **5** | **`TestPd6Rule4TmpRelativized::…tmp_relativized_admitted_for_same_process_drafts_without_absolute_prohibition`** | **PD-6(4)/INV-4 enmienda 001 (b)** |
| 6 | `TestPd6OrientationOwnerCited::…orchestrators_reference_the_view_first_owner` | PD-6 (cita, no duplica) |
| **7** | **`TestPd6NoTmpCrossScopeInstructionInInstallableText::…no_installable_text_uses_tmp_as_cross_scope_channel_or_artifact_place`** | **PD-6(4)/INV-4 enmienda 001 (c) — oráculo de ausencia** |

Removed: `test_pd6_rule4_never_tmp_as_channel_or_workspace`, `test_pd6_rule4_declares_the_sanctioned_alternative_to_tmp`, `test_pd6_no_installable_text_instructs_tmp` and the constants `SANCTIONED_ALTERNATIVE_RE` / `RULE4_ALTERNATIVE_GROUPS` / `TMP_PROHIBITION_RE`-as-rule (no leftover references; `ast.parse` OK). New concepts with language alternatives: `TMP_PERMISSION_RE`, `EPHEMERAL_DRAFT_RE`, `SAME_PROCESS_RE`, `DURABLE_OR_XPROCESS_RE`, `STABLE_WORKSPACE_PATH_RE`, `RECEIPT_INBOX_RE`, `CROSS_PROCESS_ROLE_RE`, `ARTIFACT_RECEIPT_EVIDENCE_RE`, `TMP_AS_PLACE_RE`, plus helper `absolute_tmp_prohibitions()`. Docstrings tagged «PD-6 (enmienda 001)».

### 3. Commands + output

```bash
$ grep -rn "/tmp" tests/*.py tests/*.sh     # pedido por la enmienda 001
```
No `*.sh` match; `tests/validate-consistency.sh` has zero `/tmp`. In `*.py`, besides this module, `/tmp` only appears as `temporary_roots: [".cdad/tmp"]` fixtures, `tempdir`/absolute-path policy fixtures (`test_004_001_t7_capacity.py:76`, `test_003_003_t2_reviewfix.py:77,120`, `test_005_002_t3_application_privacy.py:348`, …) and a mention-only docstring in `test_006_002_u5_transport_equivalence.py:7`. **None fixes the orchestrator/skill «never /tmp» rule → nothing else reformulated** (as the objective required).

```bash
$ python3 -m pytest tests/test_006_002_u6_context_discipline.py -v
```
```
TestPd6Rule1OrientationFirst::…            PASSED
TestPd6Rule2SessionRotation::…             PASSED
TestPd6Rule3NoSelfRepair::…                PASSED
TestPd6Rule4TmpRelativized::…stable_workspace_paths                 FAILED
TestPd6Rule4TmpRelativized::…without_absolute_prohibition           FAILED
TestPd6OrientationOwnerCited::…            PASSED
TestPd6NoTmpCrossScopeInstructionInInstallableText::…               PASSED
2 failed, 5 passed in 1.51s
```

RED is **AssertionError de contenido**, never ImportError/SyntaxError/fixture failure:

- (a): `PD-6 (agents/opencode): la regla «lo durable / la evidencia / lo que lee otro proceso o rol va a rutas estables del workspace, con `.cdad/inbox` para el recibo» tiene sus conceptos en el documento pero NO co-ubicados en una misma unidad/ventana ([…]): la regla no puede quedar dispersa por el documento`
- (b) (both halves in one run): `… la regla «`/tmp` admitido para borradores efímeros de un mismo proceso» no está declarada — conceptos ausentes: ['de un mismo proceso']` **and** `prohibición ABSOLUTA de `/tmp` sin matiz … ['- **Never `/tmp` as channel or workspace.** …']`

Oracle sanity-check with **synthetic** text (never implementation; `/tmp/opencode/u6_oracle_probe.py`): the contract-faithful rule 4 (permission + same process + durable/evidence/other-process → stable workspace + `.cdad/inbox`) → `(a) PASS, (b) PASS, absolute prohibitions: []`; the absolute «Never `/tmp` as channel or workspace» rule → `(a) FAIL, (b) FAIL, absolute prohibitions: [attrs]`. The oracle discriminates in both directions.

### 4. Honest limitations (PD-15)

- (c) and tests 1–3 + the orientation-owner citation are **pre-satisfied guards** (observed green), kept against regression; the new RED is (a) and (b) — as required.
- Prose oracles are heuristic over *concepts with alternatives*: (a)/(b) use unit/±10-line co-location; (c) uses line-level `TMP_AS_PLACE_RE` + a cross-scope marker on the same line (a `/tmp` mention merely co-mentioned with "receipt" in another clause is **not** flagged — false-positive control). Fine wording remains stage-4 review's job.
- The test proves the rule **exists**, not that it is **obeyed** (unchanged honest limit; the only behavioural evidence is the U8 acceptance transcript).
- Phase isolation kept: no implementation code (`skills/`, `sources/`, `scripts/`, `agents/`, `build/`) was read to derive assertions — only run-time oracle execution. No `--no-verify`, no `git stash`, no push; full suite not run (closer runs it at closure). Model observed: `mofgw/deepseek-v4.1-flash` (observation only).

### 5. Test → PD summary of the reformulated behaviour

- **(a)** both generated orchestrators (staging `basic`, copia temporal) must co-locate, in one rule unit: `/tmp` mention + durable/evidence/cross-process-or-role condition + stable workspace path + `.cdad/inbox` receipt → **RED (not co-located today)**.
- **(b)** `/tmp` must be admitted for same-process ephemeral drafts (3 concepts) **and** no `/tmp` prohibition may stand without that matiz (scoped-to-cross-role/permission exceptions allowed) → **RED (nuance absent, absolute prohibition present)**.
- **(c)** installable text (`skills/**` + `agents/**`) must not instruct `/tmp` as a cross-process/role channel or as the place of an artifact/receipt/evidence (prohibitions and same-process ephemeral admissions are valid) → guard green.
