GREEN is mostly done but one of the 36 u1b+u1a tests still fails, and it fails because of a test defect, not production code. Implementation commit is `5be4ff93`.

**Intake.** I ran `cdad_packet.py intake --project-root . --received <file>` on the dispatch text, written verbatim to `/tmp/recv.txt`. It returned rc=0, route C. `render` against `REQUEST.json` is identical to the on-disk `PACKET.md`.

**Changed sites (2 files, no tests touched; `git diff HEAD~1 -- tests` is empty):**
- `skills/cdad-cycle/scripts/cdad_dispatch.py`:
  - `load_runtime_section` has a new `optional` flag, used only by `record`. With it, an absent file, `runtimes` map or section becomes `{}`. Unreadable JSON, a present non-object section (a directory counts as present) and forbidden keys still reject.
  - `derived_internal_config` has a new `with_runtime` flag. `observe_model` passes `False`, so the module receives the available section as it is, including `{}`, with no added `runtime` key. The PC-3 test requires `{}` here.
  - The required-config loader used by external dispatch and `capabilities` is unchanged, and `observe_model` has no `sessions_db` gate.
- `skills/cdad-cycle/references/cli-delegation.md`: a short note that native `record` treats a missing config as `{}`, and that unreadable JSON, a non-object section and forbidden keys still reject.

**Test results:**

| Command | rc | Result |
|---|---|---|
| `pytest -q -rf tests/test_006_005_u1b_dispatch_entry.py tests/test_006_005_u1a_runtime_config.py` | 1 | 35 passed, 1 failed (86.72s) |
| `tests/test_006_005_reviewfix.py` | 0 | 9 passed |
| `tests/test_006_005_u6fix4_native_selection.py` | 0 | 9 passed |
| `tests/test_006_005_u6fix6_model_parity.py` | 0 | 2 passed |
| `tests/test_006_005_u6fix1_capabilities_entry.py` | 0 | 3 passed |
| `tests/test_006_005_u4_single_entry.py` | 0 | 7 passed |
| `tests/test_007_003_continuity_at_edges.py` | 0 | 10 passed |
| `tests/test_007_003_legacy_reanchor.py` | 0 | 19 passed |

I ran the seven regression files in parallel after one combined run timed out at 900s.

**The one failure:** `TestPd4WithoutFinalTextThereIsNoDelivery::test_pd4_without_final_text_no_staging_no_descriptor_no_receipt`.
- The error is a `FileNotFoundError` at `tests/test_006_005_u1b_dispatch_entry.py:1221`. It comes from `self.addCleanup(lambda: unreadable.chmod(0o600))` in the new unreadable-file case.
- `tearDown` (line 552) calls `self._tmp.cleanup()` first, which deletes the file. Cleanups run after `tearDown`, so the `chmod` hits a missing path.
- No assertion failure appeared in the error output for this test before the cleanup error; I did not confirm that every subtest passed.
- Production code cannot fix this, and I did not touch the test. The fix is to make the cleanup tolerant of a missing file (for example `missing_ok`-style handling or a try/except), or to chmod inside `tearDown` before the tmp cleanup. The test-writer needs to do it.

**Not run:** the full suite (recorded as "suite completa no realizada"), and the other 007-003 tests beyond the two files above. I did not deploy, publish, change user config or state, or recover any client dispatch. Correction consumption is unchanged at 1/2.
