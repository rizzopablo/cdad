## Implementer role report — 006-005 U1c GREEN

### Result in one line
U1c implemented (two zones of `skills/cdad-cycle/scripts/cdad_packet.py`). U1c focal **GREEN**, ficha regressions **GREEN**, U1a focal **GREEN**. **One U1b focal oracle is blocked by its own declared precondition**, which PD-7 contradicts by construction (details in §4). No test was edited.

### 1. Commit
```
e958a0c feat: 006-005 U1c GREEN — el agente viaja en el paquete
 skills/cdad-cycle/scripts/cdad_packet.py | 32 ++++++++++++++++++++++++++++++--
 1 file changed, 30 insertions(+), 2 deletions(-)
```
No `--no-verify`, no `git stash`, no push. `git status` clean except the declared non-mine untracked `docs/planning/` and `findings/incremental-construction-and-reproducible-validation-2026-10-17.md`.

### 2. Modified file (write scope: `skills/`)
- `skills/cdad-cycle/scripts/cdad_packet.py`
  - **Zone A — request construction in `prepare`** (:4487): `"agent": _packet_agent(role, state)`.
  - **New helper `_packet_agent(role, state)`**: non-empty string `stack` ⇒ `cdad-<role>-<stack>`; `null`/absent ⇒ `cdad-<role>`.
  - **Zone B — `validate_request` closed set** (:772-789): `optional = {"plan_task", "agent"}`, closure expressed as `required <= set(document) <= required | optional` (any combination of declared optionals is legal, everything else still rejected), plus `request.agent` must be a non-empty string when present — same pattern as `plan_task`.
  - Render untouched (`render_packet` uses its explicit key list); `receive` untouched.

### 3. Test → result

| Gate | Command | Result |
|---|---|---|
| U1c focal | `python3 -m pytest tests/test_006_005_u1c_packet_agent.py -q` | **5 passed** in 4.11s |
| U1c ficha regressions (`test_packet_prepare.py`, `test_005_006_t2_intake.py`, `test_role_packet_render.py`, `test_005_013_t1_unit_projection.py`) | `python3 -m pytest <4 files> -q` | **60 passed** in 172.27s |
| U1a focal (touches prepare) | `python3 -m pytest tests/test_006_005_u1a_runtime_config.py -q` | **19 passed** in 46.83s |
| U1b focal (touches prepare/receive) | `python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py -q` | **12 passed, 1 failed** — blocked precondition, §4 |
| Widened regression (shared request/render/receipt contract) | `python3 -m pytest tests/test_005_003_t6_packet_contract.py tests/test_005_005_t1_replace_conserved.py tests/test_003_002_t1_receive.py tests/test_005_012_t4_late_delivery.py tests/test_005_007_t4_architect_report_materialization.py tests/test_004_003_t2_plan_review.py tests/test_005_006_t5_acceptance.py tests/test_005_001_t2_replace_packet.py -q` | **51 passed** in 59.50s |
| `make validate` | `make validate` | `Assert PASS: 168` / `Assert FAIL: 1` → **`FAIL: F011: scripts/validate-subagents.sh (active profile)`**, the declared environmental failure |

RED evidence before the change (`eab7e2f` behaviour): `AssertionError: unexpectedly None : PD-7 violada (§2.7/D-13): el REQUEST.json publicado no lleva el campo declarado agent …` — a behaviour failure, not ImportError/SyntaxError/JSONDecodeError.

### 4. Blocked oracle (conflict, not fixed by editing tests)
```
FAILED tests/test_006_005_u1b_dispatch_entry.py::TestPd5NativeCorrelation::
       test_pd5_native_packet_without_agent_never_invents_the_agent
E  AssertionError: 'agent' unexpectedly found in {… 'agent': 'cdad-test-writer', …}
```
- The test declares a **precondition** `assertNotIn("agent", self.request_doc())` — "esta unidad NO depende de PD-7; el paquete del fixture no declara `agent`".
- `self.request_doc()` reads the packet that the fixture publishes with the **product's `prepare`** (`new_project` → `python scripts/cdad_packet.py prepare …`).
- PD-7 (approved spec §2.7) makes `prepare` write `agent` **always** (`stack` absent ⇒ `cdad-<role>`). No implementation can satisfy PD-7 and that precondition at once; weakening PD-7 would break the U1c focal and the reformulated A-1 oracle.
- The contract actually under test (natively recording a packet **without** `agent` ⇒ key «agente» `unknown`, never `cdad-<role>`) is unaffected.
- Minimal test-side correction for the test-writer (A-1, declared in a RED testfix, **not** in GREEN): build the pre-feature form by popping `agent` from the published request and rewriting the file — the same device U1c's own compatibility test already uses, faithful because the render does not change with the field — keeping the PD-5/§2.3 postcondition. The plan §4 A-1 table does not list this test, so it needs the test-writer's declared replacement.

### 5. Quality checks
- **Early exit / guard clauses**: single helper, one condition; no nesting added.
- **Illegal states unrepresentable**: request closure expressed as a subset invariant (`required <= keys <= required ∪ declared optionals`) instead of an enumeration of optional combinations, so a future declared optional cannot silently widen the set.
- **Predictable and atomic**: pure function of `(role, state)`; `prepare` keeps its all-or-nothing publication path untouched.
- **Fail fast, fail loud**: an empty/non-string `agent` is rejected naming `request.agent`; unknown keys still fail with the same `request fields do not match schema`.
- **Intentional naming**: `_packet_agent` names the domain concept (the agent that travels in the packet), not the mechanism.

### 6. Notes
- `agent` deliberately does **not** flow into `--replace-packet` successors (that path rebuilds the request from the assignment universe); PD-7 does not require it and the spec scopes U1c to `prepare` + `validate_request`. Successors remain valid because `agent` is optional.
- Untracked `docs/planning/` and the `findings/` file were left untouched.