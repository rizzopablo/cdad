The README now has the three corrections from `2de6e72b`, and the four protected tests that were failing pass. I committed only `README.md` as `1ccc1eaf`.

**What changed**
- I applied the historical diff directly with `git show 2de6e72b -- README.md | git apply`. It applied cleanly, and no other README content was reverted.
- There is now a short "Guided start" section with a pointer to `skills/cdad-cycle/references/project-start.md`.
- The installer-only `CDAD_INSTALL_ROOT` paragraph is gone from the runtime wiring, replaced by a pointer to project adoption.
- The status example now reads `<skill-dir>/scripts/cdad_packet.py status`.

**Test results**
- Before the edit, `tests/test_005_006_t4_readme.py` and `tests/test_005_006_t6_owner_reviewfix.py` gave 4 failed, 3 passed.
- After the edit, the same command gives 7 passed:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_005_006_t4_readme.py tests/test_005_006_t6_owner_reviewfix.py`
- I also ran four other test files that reference the README: `test_005_005_t1_replace_conserved`, `test_003_007_t1_reference_classes`, `test_003_003_t2_preflight` and `test_010_002_documentary_role_integration`. All 53 tests passed.
- I did not run the complete suite.

**Working tree:** `docs/.cdad-state.json` was already modified before my edit, and I left it out of the commit. I didn't edit tests, agents, docs, the installer or models.

I didn't run `cdad_packet.py render`, because `.cdad/cdad_packet.py` doesn't exist at that path. The packet header and REQUEST.json matched on packet id, execution id, contract and objective.