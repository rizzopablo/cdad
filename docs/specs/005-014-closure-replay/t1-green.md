## Result — 005-014 T1 GREEN

**Postcondition:** the `closure` class resolves its feature from three sources and decides by identity before applying anything — the approved focal is green and the four PD-26 modules stay green.

### Modified files (write scope: `implementation`)
- `skills/cdad-cycle/scripts/cdad_packet.py` (+134/−13)
  - new `_resolve_closure_feature` (PD-22 three sources + PD-24 coherence)
  - new `_transition_noop_message` (shared no-op text, PD-11 — behavior-preserving extraction)
  - `register_transition`: closure feature resolution + closure-specific null guard (PD-22)
  - `register_transition`, closure branch: closed / no-active-feature sub-branch runs closure-document resolution (PD-20) and identity lookup **before** PD-8(a)/(b), the `--closure-path` requirement and the authority (PD-23), then PD-25 / PD-27(c)
  - The first-application path (PD-26), PD-10 identity payload, the closure effect and every other class are untouched.

No test file was edited.

### (a) Focal — exact command and output
```
$ python3 -m pytest tests/test_005_014_closure_replay.py -q -p no:cacheprovider
....                                                                     [100%]
4 passed in 4.30s
```

### (b) Touched modules — exact command and output
```
$ python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py \
    tests/test_005_012_t1_register_transition_base.py \
    tests/test_005_012_t4_late_delivery.py \
    tests/test_005_012_t5_approval_vigency.py -q -p no:cacheprovider
...............................................                          [100%]
47 passed in 79.19s (0:01:19)
```

### (c) Commit
```
a4028afd40ed0ad886a13011c924b6e274f02aa3
feat: 005-014 T1 GREEN — closure resuelve su feature y decide el replay por identidad (PD-22/23/24/25/27)

 skills/cdad-cycle/scripts/cdad_packet.py | 147 ++++++++++++++++++++++++++++---
 1 file changed, 134 insertions(+), 13 deletions(-)
```
Only the implementation file was committed; the pre-existing `docs/.cdad-state.json` modification (the orchestrator's dispatch record, `implementer-green-001`) was **not** staged. `git diff HEAD~1 --stat -- tests/` is empty (tests intact).

### How each PD is satisfied
- **PD-22:** `--feature` → `active_feature` → `state.execution.feature_id` (the key the closure effect does not clear); none of the three → rc=2 `state incoherent`, offers `--feature <feature-id>`, no `open-unit`.
- **PD-23:** in the closed/no-active branch, `_pin_relative_digest` + `_registered_transition` run before PD-8(a)/(b), the `--closure-path` requirement and authority; a hit returns the shared no-op message (rc=0) with no write. Verified: the replay payload mirrors the apply-path payload field-for-field.
- **PD-24:** `--feature` unknown → rc=2; `--feature` diverging from the resolved feature → rc=2 naming both; equal/absent → the resolved feature.
- **PD-25:** unregistered distinct closure of a closed feature → rc=2 `state incoherent`, names feature + `done`, no `open-unit`/`open the unit`, points at the legitimate exits, no effects.
- **PD-27:** `closure_active_feature is None` forces the recognition/rejection branch; unregistered + not-closed → rc=2 `state incoherent` with `--feature <feature-id>`, no `open-unit`.
- **PD-26:** the apply path keeps its current order (PD-8(a) → PD-8(b) → `--closure-path` → authority → apply); all 47 PD-26 modules green.

### Notes / honest limits
- Per the declared policy, the **full suite was not run** here (the closer runs it once at closure).
- Rejections occur before any publication inside `_ProjectLock`, so the state stays byte-for-byte identical (INV-7/INV-11); the four RED cases assert this and now pass.
- `docs/.cdad-state.json` remains modified in the working tree (orchestrator-owned dispatch record) — left untouched by me.
