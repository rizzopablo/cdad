## Report — test-writer / RED (testfix)

### Contradiction reproduced (before the fix, HEAD a0d96b5 + GREEN worktree)

```
python3 -m pytest tests/test_006_005_u6fix5_write_ahead.py -q -k redispatch
>       self.assertEqual(len(after), 1, ...)
E       AssertionError: 2 != 1 : PD-1: el re-despacho bloqueado no debe registrar un segundo intento:
        ['opencode-db3ab4915bd1', 'opencode-e10b8545672f']
1 failed, 10 deselected in 2.17s
```

### Correction (only oracle 3, `TestU65ReDispatchLiveSession`)

Aligned with D-U65-1 last bullet (a termination **before** the write-ahead registers as today, final) and oracle 8; PD-1 is one record **per dispatch**, and the blocked re-dispatch is another dispatch. Kept unchanged: `blocked`, `session: null` in the envelope, zero additional `run` invocations, crash setup and the single provisional record before the re-dispatch.

After the re-dispatch the test now asserts:
- `len(after) == 2` (D-U65-1/PD-1);
- the first dispatch's provisional record is **intact**: same stem present, **same bytes** (`record_bytes` equality), `write-ahead:` mark + O-4 provisional shape, the chosen session, `model_reported: null`;
- one new record: final per `assert_final_record` (no mark, PD-3 pairs at the end), `session: None` (PD-8), provenance names the not-dispatched case (`not dispatched`, 006-001 §2.6);
- `provisional_records()` still 1 (the new record is final).

Docstring declares: «testfix: oraculo 3 alineado con D-U65-1 y el oraculo 8».

### Modified files

| File | Change |
|---|---|
| `tests/test_006_005_u6fix5_write_ahead.py` | +61/−6, only oracle 3's method (docstring + final assertions); captured the provisional stem/bytes after the crash |

Nothing else touched: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` and `cdad_packet.py` remained as the implementer left them (modified, uncommitted); `docs/planning/` and `findings/…` untracked and untouched.

### Focal (after the fix)

```
python3 -m pytest tests/test_006_005_u6fix5_write_ahead.py -q
...........                                                              [100%]
11 passed in 18.22s
```

### Commit

```
569682da941cd62449321ebba727047b1a74bdd8
test: 006-005 U6-5 testfix — oraculo 3 alineado con D-U65-1
 tests/test_006_005_u6fix5_write_ahead.py | 67 +++++++++++++++++++++++++++++---
 1 file changed, 61 insertions(+), 6 deletions(-)
```

Only `tests/` in the commit (`git add tests/test_006_005_u6fix5_write_ahead.py`); no `--no-verify`, no stash, no push. Full suite not run (closer policy); no implementation file was read.