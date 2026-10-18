I'll start by reading the contract spec, the RED test, and the target file.
Now I understand the constraints. Let me check the guards' current state and write the subsection.
## Role report — implementer / GREEN (006-002 U5)

### Change (minimal, implementation only)
**1 file, 1 subsection, +13 lines** — `skills/cdad-cycle/references/re-entry.md`, immediately after the «Orchestrator materialization protocol» (§ PD-5/D-4):

```diff
+## Transport equivalence: one receipt route
+
+Native delegation does not change the delivery contract: the role returns its
+**FINAL TEXT** in the **orchestrator's session**, and the orchestrator stages
+the **exact bytes** under `.cdad/inbox` with their `RESULT.json` descriptor,
+**without retyping, summarizing or regenerating** them. The staged bytes are
+the original ones, and receiving approves nothing — `semantic_status` stays
+`pending`.
+
+The transport equivalence holds for every transport: it is the same route —
+`receive` → `validate-receipt` → `materialize` → the state transition — for
+the handoff to a new chat and for the CLI adapter.
```

Coverage of PD-5(a) concepts: native delegation + FINAL TEXT in the orchestrator's session; exact bytes + `.cdad/inbox` + descriptor (`RESULT.json`); the four-step chain; verbatim prohibition co-located with its negation; `semantic_status: pending` + «approves nothing»; same route for new-chat handoff and CLI adapter. Neutrality (PD-1) preserved: no runtime dispatch tool, no `subagent_type`, no model/provider token.

**Not touched:** `tests/**`, `SKILL.md` (§4 already links to the materialization protocol — guard green from U2; no missing link), `sources/agents/**`, context rules (U6), `install.sh`, `cdad-models.sh`, the CLI adapter, `docs/adr/ADR-007*`; the untracked `docs/planning/` and `findings/…` were left alone and untracked.

### Table test → result

| Test | Before | After |
|---|---|---|
| `…::test_pd5a_reentry_declares_the_transport_equivalence_route` | FAIL (AssertionError, `regions == []`) | **PASS** |
| `…::test_pd5a_reentry_keeps_the_bytes_verbatim_and_the_receipt_pending` | FAIL | **PASS** |
| `…::test_pd5a_transport_route_is_the_same_for_handoff_and_cli_adapter` | FAIL | **PASS** |
| `…::test_pd5b_section4_links_to_the_materialization_protocol` | PASS (guard, U2) | PASS |
| `…::test_pd5b_delegation_sections_link_to_the_materialization_protocol` | PASS (guard, U1) | PASS |
| `…::test_pd5c_receive_rejects_a_descriptor_with_another_source_kind` | PASS (guard, 003-002) | PASS |

### Exact commands and output

```
$ python3 -m pytest tests/test_006_002_u5_transport_equivalence.py -v
6 passed in 2.89s   (3 PD-5(a) tests red→green; the 3 guards stay green)

$ python3 -m pytest tests/test_006_002_u{1..5}*.py tests/test_003_002_t1_receive.py \
    tests/test_004_003_t5_reentry_equivalence.py -q
46 passed in 11.59s

$ python3 -m pytest $(grep -l "re-entry" tests/*.py | tr '\n' ' ') -q
93 passed, 1 skipped in 32.19s      # every test that reads re-entry.md

$ make validate
Assert PASS: 161
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
$ bash tests/validate-odoo-specialization.sh
Assert PASS: 67 / Assert FAIL: 0 — PASS: all postconditions P1..P6 and the A3 criterion verified.
```

**F011 is NOT green — and it is pre-existing, not caused by this packet** (blocked-by-environment, declared, not patched over): `scripts/validate-subagents.sh` fails inside `install.sh --check`, which compares the repo against the copies installed in `$HOME`; those copies are stale from U1–U4 (drift names `skills/cdad-cycle/SKILL.md` and `references/sub-agent-strategies.md` + the 22 agent files — never `re-entry.md`). Proof of pre-existence: the same validator run on a pristine HEAD archive without my change fails identically:

```
$ git archive HEAD | tar -x -C /tmp/opencode/u5-head && (cd /tmp/opencode/u5-head && bash scripts/validate-subagents.sh)
❌ install.sh --check failed (rc=1)  →  == RESULT: FAIL ==
```

Reinstalling (`bash install.sh`) is outside this packet's write scope (it writes outside the repo), so I stopped there and report the block to the orchestrator.

### Commit
```
$ git add skills/cdad-cycle/references/re-entry.md
$ git commit -m "feat: 006-002 U5 GREEN — transport equivalence subsection in re-entry.md (PD-5a)"
[main 8d4b302] feat: 006-002 U5 GREEN — transport equivalence subsection in re-entry.md (PD-5a)
 1 file changed, 13 insertions(+)
```
No `--no-verify`, no `git stash`, no push; `git status` shows only the two untracked pre-existing items.
