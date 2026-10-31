**Subphase complete — implementer REVIEW-FIX (010-004 T2).** One subphase, stopped at the end.

## 1. Full diff

```diff
diff --git a/skills/cdad-cycle/scripts/cdad_packet.py b/skills/cdad-cycle/scripts/cdad_packet.py
index d7ccbc95..4ff53281 100644
@@ -3022,6 +3022,45 @@ def _require_canonical_selected_context(project_root: Path, path: Path,
             "`prepare --new-execution` (010-004 §4.1/PC-04)")
 
 
+def _require_preparation_configuration(project_root: Path) -> None:
+    """Name the configuration defect of a new preparation BEFORE a v1 rejection.
+
+    Owner decision of 2026-10-30 (`decision-diagnostic-precedence.md`, restoring
+    010-004 §4.5/:352 and PC-09): when a new preparation meets BOTH a
+    configuration defect and a v1 context, the actionable configuration cause is
+    the one the user sees. The context version/location rejection still runs
+    afterwards, unchanged, with no persistent effect — nothing is converted,
+    published or adopted, and no legacy fallback is opened.
+
+    Only what the CLI can verify WITHOUT selecting a v2 context is diagnosed
+    here: a project policy the owner has materialised, that is a regular file and
+    that its own validator accepts. Authority, approval and pins are validated
+    against the SELECTED execution (`_validate_v2_state`); on this path there is
+    no such context, so they are neither guessed nor fabricated.
+    """
+    location = POLICY_RELPATH.as_posix()
+    path = _policy_location(project_root)
+    if not path.exists():
+        raise PolicyError(
+            f"the project policy is missing: {location} does not exist and a new "
+            "preparation requires one. Propose it with `prepare --propose-policy` and "
+            "ask the owner to materialise the proposal at the policy path")
+    if not path.is_file():
+        raise PolicyError(
+            f"policy location is invalid: {location} exists but is not a regular file, "
+            "so no project policy can be read and a new preparation requires one. "
+            "Replace it with the policy the owner materialises from "
+            "`prepare --propose-policy`")
+    raw = _read_bytes(path, "project policy")
+    try:
+        _load_policy_from_bytes(raw, project_root)
+    except PolicyError as exc:
+        raise PolicyError(
+            f"the project policy at {location} is invalid: {exc}; a new preparation "
+            "requires a valid policy (propose it with `prepare --propose-policy` and ask "
+            "the owner to materialise the fix)") from exc
+
+
 def _select_execution(args: argparse.Namespace, project_root: Path,
                       state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], bool]:
@@ -3044,6 +3083,9 @@ (explicit v1 branch)
         # to --new-execution / bootstrap. Checked before any publication.
+        # §4.5/PC-09: an actionable configuration defect is named first; this
+        # rejection still follows when the configuration is usable.
+        _require_preparation_configuration(project_root)
         raise PolicyError(
@@ -3080,6 +3122,9 @@ (implicit v1 branch)
     # stays byte-identical and the new work starts on a v2 execution.
+    # §4.5/PC-09: the configuration cause is named first when it is defective;
+    # this rejection still follows, unchanged, when it is not.
+    _require_preparation_configuration(project_root)
     raise PolicyError(
```

`git diff --stat`: 1 file changed, 45 insertions(+).

## 2. New order and why it satisfies §4.5/PC-09 without weakening rejections

This is not an extra pre-pass in `prepare`: the check sits **inside the two v1 rejection branches of `_select_execution`**, so precedence applies **exactly when both defects coexist** — the scope the owner decision grants — and nowhere else. The bootstrap, v2-reuse and canonical-locator paths are byte-for-byte untouched.

For a new preparation the order is now: resolve decomposition of the defect → if the project policy is missing, is not a regular file, or is rejected by its own validator, raise that actionable cause (with the existing procedure `prepare --propose-policy` and owner materialisation) → otherwise raise the unchanged v1 version/location rejection. Nothing is converted, published, bound or adopted, and no legacy fallback opens: every class still exits rc=2 with empty stdout and an unchanged tree.

It is general by defect class, not by fixture: the branch is chosen from filesystem/validation state, the policy travels through the same `_load_policy_from_bytes` the loaders use, and the message names the location either way. No diagnostic was weakened (the v1 messages are not edited — the diff only inserts calls), no exit code or wrapper changed, and no `--new-execution` hint is attached to a policy defect. The authority/approval/pin bullet is deliberately **not** implemented: those are validated against a *selected* v2 execution (`_validate_v2_state`), which does not exist on this path, and the packet forbids inventing such checks or fabricating authority — that is recorded in the docstring.

## 3. Evidence (real commands, real summary lines)

**(a) C3 green**
`python3 -m pytest tests/test_004_002_t2_reviewfix.py::TestF6NoLegacyFallbackOnInvalidPolicyLocation::test_f6_policy_directory_with_v1_context_no_legacy_fallback -q` → `1 passed in 0.53s` (before: `1 failed`, `AssertionError: unexpectedly None : F6: diagnóstico no menciona la política`)

**(b) 6 RED green** — `python3 -m pytest tests/test_010_004_t2_red.py -q` → `6 passed in 10.64s`

**(c) 2 POST-AUDIT green** — `python3 -m pytest tests/test_004_002_t6_landing.py::TestPd12LegacyIntake::test_pd12_legacy_without_policy_keeps_legacy_intake tests/test_packet_prepare.py::TestPrepareDefaults::test_p2_default_execution_context_and_out_dir_under_project_cdad -q` → `2 passed in 15.41s`

**(d) 5 PC-08a green** — `python3 -m pytest tests/test_role_packet_render.py::TestPacketIntegrity::test_p2_validate_packet_rejects_tampered_body_metadata_and_hash tests/test_role_packet_render.py::TestPublicTask2Surface::test_p1_all_role_substage_pairs_render_and_validate tests/test_role_packet_render.py::TestPublicTask2Surface::test_p1_repeated_render_is_byte_deterministic tests/test_role_packet_render.py::TestPacketIntegrity::test_p2_metadata_is_canonical_and_matches_request tests/test_role_packet_review_regressions.py::TestReviewRegressions::test_p2_validate_packet_rejects_crlf_byte_variant -q` → `5 passed in 26.44s`

**(e) 15-file universe** — `python3 -m pytest <the 15 files> -q --tb=line -rf -p no:cacheprovider`
- BEFORE: `64 failed, 53 passed in 97.23s` (117 tests — matches the declared baseline)
- AFTER: `63 failed, 54 passed in 108.47s` (117 tests)
- Per-file failures, before → after (identical except C3): u1_draft_object_form 16→16, packet_prepare 8→8, t4_validation_fields 8→8, t2_progressive_plan_validator 6→6, t3_plan_checks 5→5, t2_plan_review 5→5, u1c_packet_agent 4→4, u3_review_route_and_gate 2→2, t2_reviewfix 2→2, t1_reviewfix 2→2, t1_draft_contract 2→2, t6_templates 1→1, reviewfix_blockings 1→1, t7_acceptance 1→1, **t2_reviewfix 1→0**.
- `diff` of the failing-id sets: only the C3 line disappears; no new failure.

**(f) Proportional regression beyond the universe** (files that drive `prepare` over v1 contexts): `python3 -m pytest tests/test_004_002_t2_bootstrap.py tests/test_004_002_t6_landing.py tests/test_005_012_t6_open_context_guard.py tests/test_005_001_tcorr.py tests/test_007_002_dispatch_recovery.py -q` → `56 passed in 149.98s`

**Scope/state** — `git diff --stat` → `skills/cdad-cycle/scripts/cdad_packet.py | 45 ++++`; `git status --porcelain` → ` M skills/cdad-cycle/scripts/cdad_packet.py` then, post-commit, only the pre-existing `?? docs/specs/010-000-continuity-relative-root/discovery.md` (preserved untouched). Wrapper `scripts/cdad_packet.py` and every other file untouched. Eight boundary probes (absent / directory / malformed / structurally-invalid policy × implicit and explicit v1; valid policy × both) all gave rc=2, empty stdout, no traceback, tree unchanged, and the v1 messages identical when configuration is usable. No full suite, no push, no global install, no installed-copy edit.

## 4. Files intact (hashes)

- `docs/specs/010-004-packet-dispatch-ergonomics/spec.md` → `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64` (approved pin)
- `docs/specs/010-004-packet-dispatch-ergonomics/plan.md` → `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685` (approved pin)
- `docs/specs/010-004-packet-dispatch-ergonomics/decision-diagnostic-precedence.md` → `e5088091d723f19b333b947f768dccf4357247310064cb0e926a596bf02ba087` (unchanged)
- `tests/**` (219 `.py` files, sha256 manifest per file) → aggregate `ece8d8c854cbccda8e7514649ebfbf4aa859d78db56fe03b6695ea7a8eea4774` **identical before and after** (per-file `diff` empty); `git status --porcelain -- tests docs` shows nothing but the pre-existing untracked discovery file.

## 5. Residual failures

None new and none of a different cause: the 63 remaining universe failures are exactly the pre-existing set (62 C1 fixture-migration + 1 C2), with identical test ids before/after, so nothing was absorbed, weakened or masked. One out-of-scope observation, left unchanged on purpose: on the **bootstrap** path (no v1 coexisting) an absent policy still reports `cannot read project policy <abs path>: [Errno 2] No such file or directory` without the `--propose-policy` next action, because the owner decision grants precedence only over the v1 rejection.

## 6. Commit

`3eda073a03090782e7c889dd9a80ae57a77ec2e4` — `fix: 010-004 T2 — precedencia de diagnósticos de configuración sobre contexto v1` (1 file, 45 insertions).