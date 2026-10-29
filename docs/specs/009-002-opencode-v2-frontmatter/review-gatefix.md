**Verdict: 1 BLOCKING.** The two migrated oracles are correct, but the write-absence oracle in the same P3 test no longer checks anything.

The packet is valid: `validate-request` rc=0, and `render` is identical to PACKET.md. The spec sha256 matches the contract. I could not observe my own received bytes, so I used route C.

- **What 937bad1 gets right.** In `test_006_005_u3b…py:339-367` the oracle drops only edit entries for `scratch` or `scratch/**` and leaves the other bytes alone. Its negative control works, because if `mode: subagent` were missing the check would fail. In `test_role_packet_consumers.py:229-259`, read-only, tests-only and implementer verdicts are evaluated last-match-wins with deny by default.
- **BLOCKING (Bucket m), `test_role_packet_consumers.py:218-222`.** The check `^  write:` is still the V1 shape. V2 writes `  - action: write`, so a reintroduced write rule would slip through and undo the path barriers. Fix: assert that no rule has `action == "write"` in `v2_permissions`.

Command: `pytest -q` on the two modules gave `11 passed`. Nothing was edited or committed.
