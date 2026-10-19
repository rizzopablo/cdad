## Role report — test-writer, substage RED (testfix) — 006-005 U1c

### Result in one line
U1b PD-5 oracle unblocked by rebuilding the pre-feature packet form **inside the fixture** (removing the now always-published optional `agent`); the postcondition assertion is untouched and the oracle is proven still discriminating. U1b focal **13 passed**, U1c focal **5 passed**, **zero failures**.

### 1. Contract / packet
- Contract: `docs/specs/006-005-native-path-parity/spec.md` sha256 `3a824be3…` (approved). Packet `006-005-native-path-parity-test-writer-red-006`, write scope `tests/**` only.
- Postcondition under test (unchanged): PD-5 / §2.3 — a packet **without** `agent` ⇒ the «agente» key is `unknown`, never `cdad-<rol>` (no accredited session), diagnosis naming the key.

### 2. Pre-fix RED observed (the failure the testfix removes)
```
$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py::TestPd5NativeCorrelation::\
test_pd5_native_packet_without_agent_never_invents_the_agent -q
E  AssertionError: 'agent' unexpectedly found in {… 'agent': 'cdad-test-writer', …}
   : precondición (declarada): esta unidad NO depende de PD-7; el paquete del fixture no declara `agent`
tests/test_006_005_u1b_dispatch_entry.py:1186: AssertionError
1 failed in 0.39s
```
A **fixture precondition** failure (U1c/PD-7 makes `prepare` write `agent` always), not an oracle failure — exactly what `u1c-green.md` §4 declared.

### 3. Modified file (write scope: `tests/`) — commit `12e710a`
`tests/test_006_005_u1b_dispatch_entry.py` (+48/−9):
- **New fixture helper `U1bEntryCase.drop_optional_agent()`** (+ `request_path()` extracted, `request_doc()` now reads through it): pops the declared optional `agent` from the **published** `REQUEST.json` and rewrites it with `sort_keys=True` — the same device declared in `tests/test_006_005_u1c_packet_agent.py:332-336`, faithful because the render is invariant to the field (that file's own PD-7 byte oracle). Only usage of these helpers is this file.
- In `test_pd5_native_packet_without_agent_never_invents_the_agent`: a fixture precondition `assertIn("agent", …)` (the field is published, so a pre-feature form exists to rebuild) → `drop_optional_agent()` → the **original, literally unchanged** `assertNotIn("agent", request, …)` now runs on the reconstructed document. **No behavioural assertion was changed**: `record["session"] in (None, "unknown")`, the diagnosis regex naming «agente», and `!= NATIVE_SESSION` are byte-identical to before.
- Docstrings updated (module §PD-5 dependency note + the test's) to state the reconstruction instead of the stale "the packet of this unit carries no `agent`".

### 4. Oracle sensitivity (why the testfix does not make the test vacuous)
Throwaway copies (deleted, never committed):
- variant 1 (keep `agent`, precondition intact): fails at the precondition, as expected.
- variant 2 (keep `agent`, precondition neutered → the **postcondition** is what must fail):
```
E  AssertionError: 'ses-native-u1b-0001' not found in (None, 'unknown')
   : PD-5: sin `agent` en el paquete la llave «agente» es `unknown` (nunca `cdad-<rol>`), aunque el padre coincida: se persiste 'ses-native-u1b-0001'
```
With the field present the entry *does* accredit the session, so the assertion discriminates exactly the behaviour the reconstruction isolates: the pre-feature form is the only difference.

### 5. Evidence — exact commands and outputs (after the change)
```
$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py -q
13 passed in 14.78s
$ python3 -m pytest tests/test_006_005_u1c_packet_agent.py -q
5 passed in 3.74s
$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py tests/test_006_005_u1c_packet_agent.py -q
18 passed in 19.94s
```
Validation width: the change is a **local correction inside a U1b focal test file** (no shared fixture signature changed, no product file touched), so per the packet's "Widen" rule the focal tests are the scope; the closer runs the full suite once (PD-21). No `--no-verify`, no `git stash`, no push.

### 6. Commit
```
12e710a test: 006-005 U1c testfix — paquete pre-feature reconstruido en la correlacion nativa
 tests/test_006_005_u1b_dispatch_entry.py | 57 +++++++++++++++++++++++++++----- (48 insertions, 9 deletions)
```
`git status --porcelain`: only the declared non-mine untracked `docs/planning/` and `findings/incremental-construction-and-reproducible-validation-2026-10-17.md` — untouched.

### 7. Honest limitations
- Implementation code was **never read** (`skills/cdad-cycle/scripts/**` untouched; the read scope used was `tests/**` + `docs/specs/006-005-native-path-parity/**`, including the implementer's `u1c-green.md` §4 which declared this fix). The implementation was only **executed** as a black box by the tests (subprocess), which is the oracle's normal operation.
- The reconstruction's faithfulness rests on PD-7's declared byte oracle (render invariant to `agent`); if that oracle were ever falsified, this reconstruction would need revisiting.
- `tests/.sensitive-patterns.local` was not read; no host values are reported.