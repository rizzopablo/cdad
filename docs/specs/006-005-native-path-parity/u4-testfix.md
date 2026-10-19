## Role report — test-writer / RED testfix (006-005 U4)

**Path used:** validated packet `006-005-native-path-parity-test-writer-red-012` (no cycle reload). Read only `docs/specs/006-005-native-path-parity/spec.md` and `tests/**`. Implementation code was **not** opened or grepped; the cited source lines came from the task brief.

### Change 1 — `tests/test_006_003_u3_texts_without_profiles.py`

**Test:** `TestInv4InstallableTextWithoutTmp::test_inv4_installable_skill_text_names_no_tmp`
**Postcondition:** INV-4 (006-002) — no installable text names the **host’s** `/tmp` (absolute root). Project-relative `.cdad/tmp` is not the prohibited thing (006-005 §2.9 / §5 D-5).
**Oracle replaced:** `re.compile(r"/tmp\b")` — matched any `/tmp` substring, including `.cdad/tmp`.
**Reason:** substring matching conflated a legitimate project-relative temp root with the host root, producing a false positive on `skills/cdad-cycle/scripts/cdad_packet.py`.
**Replacement (tightened, not loosened):** `(?<![\w.~/\\$}-])/tmp\b` — `/tmp` only when not preceded by a path character or expansion closer (`letter/digit/_/./~/\/-` or `$`/`}`).
**Vacuity controls added:** host forms `/tmp/cdad-run/aux.txt`, `aux under /tmp`, `"/tmp"` must match; `.cdad/tmp`, `.cdad/tmp/aux.txt`, `foo/tmp/aux.txt`, `~/tmp/aux.txt` must **not** match.

### Change 2 — `tests/test_005_004_t2_installer_claims.py`

**Test:** `test_pd2_i_sweep_no_declared_surface_claims_the_installer_removes_the_model_field`
**Postcondition:** PD-2(i)/AC-2 — no declared surface claims **the installer** strips/removes/trims the `model:` field.
**Oracle replaced:** `removal_claim_lines` matched any removal verb with “model” within ±90 chars, ignoring the subject.
**Reason:** `skills/cdad-cycle/scripts/cdad_dispatch.py:34` (“removed when the call ends, never carrying a model or a credential value”) is about a transient file, not the installer.
**Replacement (tightened):** hit requires `INSTALLER_SUBJECT_RE` (installer / install.sh / installation process / instalador / instalación …) within 90 chars **before** the verb, or a passive agent (`by the installer`, `por el instalador`) within 60 chars after. All four pre-existing vacuity controls kept intact.
**Controls added, both directions:** transient-file sentence in EN and ES ⇒ `[]`; `The installer STRIPS the model field at install time.` ⇒ `[1]` (kept); `The model field is stripped by the installer…` ⇒ `[1]`; `El campo model es eliminado por el instalador…` ⇒ `[1]`. Negations (`does not strip`, `strips nothing`) still ⇒ `[]`.

### Exact commands and output

```
$ python3 -m pytest tests/test_006_003_u3_texts_without_profiles.py tests/test_005_004_t2_installer_claims.py -q
..................                                                       [100%]
18 passed in 9.08s
```

```
$ python3 -m pytest tests/test_006_005_u4_single_entry.py -q
6 failed, 1 passed in 2.68s
FAILED ...TestPd20FiveD6Rows::test_pd20_mandate_has_the_five_d6_rows_in_order_without_shared_conditions
FAILED ...TestPd20NoStaleExecutionJsonCondition::test_pd20_stale_execution_json_condition_is_gone
FAILED ...TestPd20TransportRule::test_pd20_transport_rule_is_declared
FAILED ...TestPd20DelegationSections::test_pd20_delegation_sections_name_entry_packet_agent_and_module_credential
FAILED ...TestPd20AdoptionBorder::test_pd20_cli_delegation_declares_the_migration_adoption_border
FAILED ...TestPd20GeneratedDelegationLabel::test_pd20_generated_delegation_label_drops_the_adapter_qualifier
```

Focal RED is content-level (`AssertionError`, e.g. `['## Delegation (adapter)'] != []`), no `ImportError`/`SyntaxError`; it is the expected pre-GREEN state of U4, unrelated to this testfix.

```
$ git diff --stat
 tests/test_005_004_t2_installer_claims.py       | 111 ++++++++++++++++++++++--
 tests/test_006_003_u3_texts_without_profiles.py |  81 +++++++++++++++++++--
 2 files changed, 174 insertions(+), 18 deletions(-)
```

### Commit

`b76aa5d` — `test: 006-005 testfix — oraculos de texto de /tmp del host y de strip del instalador` (only the two `tests/` files; untracked `docs/planning/` and `findings/` left untouched).

### Declared limits
- No host path values reproduced; did not read `tests/.sensitive-patterns.local`; no `--no-verify`, no stash, no push.
- Not run: the full suite and the non-focal regression list (packet says the closer runs the full suite once; unit integration gate runs regressions at U4 GREEN). Both edited files’ complete suites were run and are green.