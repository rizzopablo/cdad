# Report — test-writer RED, 006-005 U6-7

## 1. Files modified (only `tests/`)

| File | Change |
|---|---|
| `tests/test_006_005_u6fix7_write_lever.py` | **New** (594 lines). RED for U6-7: effective write verdict = `edit` map verdict, for generated agents and for `prepare`-published derivatives. |
| `tests/test_role_packet_consumers.py` | **A-1 reformulation**: replaced the assert that fixed the *presence* of `write: ask`. |

Commit: `850667441600bcab07606fa8caece82ba88d23ae` — `test: 006-005 U6-7 RED — la palanca write no anula el mapa edit` (2 files, +615/−2). Untracked `docs/planning/`, `findings/*` untouched.

No implementation code was read. Files read: the approved spec, `execution.md`, `tests/**`, and the **generated artifacts** `agents/*.md` / `.opencode/agents/*.md`. `scripts/cdad-generate.py` and `scripts/cdad_packet.py` were only invoked as processes.

## 2. ORACLE (what the test evaluates)

- `write_rule_list()` merges the `permission` block's `edit` **and** `write` keys **in file order**; `evaluate()` (reused from `tests/test_opencode_read_map_and_steps.py`) applies findLast: **last matching rule wins**, default `allow`. The only new parsing is positional and admits the measured `ask` verb — no evaluation semantics duplicated.
- `edit_verdict()` reuses `perm_map()` from `tests/pd10_permission_semantics.py`.
- Contract fact encoded: `write: ask` **after** the `edit` map makes every write `ask` (v2.0.27, probes P1/E1b). Assertion: `write_verdict == edit_verdict` **and** `write_verdict != "ask"`.

## 3. Test → postcondition map (all docstrings «E2/PD-24 (U6-7)»)

| Test | Postcondition |
|---|---|
| `TestGeneratedAgentsWriteLever::test_u6_7_every_generated_agent_keeps_its_edit_verdict` | E2/PD-24: each role (`architect`, `test-writer`, `implementer`, `reviewer`, `scribe`), each `-odoo` variant and `orchestrator`: effective write verdict == `edit` map for 12 probes. |
| `…::test_u6_7_no_generated_agent_resolves_write_to_ask` | E2/PD-24: no route of any generated agent resolves `ask` (the P1/E1b annulment). |
| `TestGeneratedRoleBarriers::…test_writer…` | test-writer: `tests/x.py` allow, `docs/x.md` deny; odoo: addons tests allow, models deny. |
| `…::…implementer…` | implementer: `tests/x.py` deny, code allow; odoo: tests deny, models/views allow. |
| `…::…read_only_roles_deny_every_route` | architect/reviewer/scribe (+`-odoo`): every route deny. |
| `…::…orchestrator_permission_allow_is_preserved` | orchestrator (`permission: allow`): write allow, never `ask` (passing control today). |
| `TestDerivedAgentsWriteLever::test_u6_7_every_derived_agent_keeps_its_edit_verdict` | E2/PD-24 over every derivative published by `prepare`. |
| `…::test_u6_7_derived_test_writer_keeps_temporary_and_tests_writable` | PD-24: `tests/x.py` allow, `.cdad/tmp/x` allow (declared temp root), docs/implementation deny — through the write tool. |
| `…::test_u6_7_derived_implementer_and_readers_keep_their_maps` | implementer code allow / tests deny; readers all deny (derived). |
| `TestDerivedTemporaryRootKeepsBarriers::…` | PD-24/INV-16: temp root allow does **not** open policy, derivatives or private paths (fixture `tests/.sensitive-patterns.fixture.local` is fictional; the real local file was never read). |

## 4. A-1 — reformulated test (declared)

- **Replaced:** `tests/test_role_packet_consumers.py::TestInstalledConsumerEntrypoint::test_p3_critical_opencode_permissions_survive_consumer_migration` used to assert `(?m)^\s{2}write:\s*ask\s*$` on every installed role agent.
- **Replacement + reason (in the docstring/comment):** assert **absence** of a `write:` entry. The cdad-010 P1 lever's own watch rule (“if a future OpenCode version evaluates `write` at runtime… revisit on migration”) was fulfilled in v2.0.27, where `write` is evaluated for the write tool together with `edit` and the last match wins; the lever is retired so the `edit` map governs.
- **Search result:** only that test fixed the lever. `tests/pd10_permission_semantics.py:72` mentions `cdad-010` only in a docstring about `edit: deny` (not a lever assertion). No other `write: ask` occurrence in `tests/`.

## 5. Commands and outputs

```
$ python3 -m pytest tests/test_006_005_u6fix7_write_lever.py -q
9 failed, 1 passed in 2.82s
```
All 9 are `AssertionError` of the form `'ask' != 'allow'` / `'ask' != 'deny'`, e.g.:
```
E   AssertionError: 'ask' != 'deny'
E    : E2/PD-24 (U6-7): la herramienta de escritura de cdad-architect.md resolvió 'ask' para 'tests/x.py'; el mapa `edit` del rol resuelve 'deny'.
```
No ImportError, no fixture error. The 1 passing test is the orchestrator control (it has no lever).

```
$ python3 -m pytest tests/test_006_005_*.py -q
9 failed, 119 passed in 145.38s
```
(The 9 failures are exactly the new U6-7 tests; all other 006-005 focals are green.)

```
$ python3 -m pytest tests/test_004_002_t5_runtime.py tests/test_004_002_t7_l1_derived.py \
    tests/test_004_002_t7_w2.py tests/test_cdad_generate.py tests/test_packet_prepare.py \
    tests/test_004_001_t7_pd10.py tests/test_004_002_t7_private_paths.py -q
89 passed in 44.98s
```

```
$ python3 -m pytest tests/test_role_packet_consumers.py -q
1 failed, 4 passed in 10.43s
```
The single failure is the declared A-1 replacement (installed agents still carry `  write: ask`).

```
$ python3 tests/pd10_permission_semantics.py
PD-10 semantic checks: 39/39 passed
```

**Green-readiness check (simulation on artifact copies, no repo edit):** removing only the `  write:` line from the generated and published-derived artifacts yields `0` mismatches between write and edit verdicts across all probes and all roles — so the RED is caused solely by the lever, not by a bug in the oracle.

## 6. Notes / limits

- Full suite not run (closure policy PD-21). No `--no-verify`, no `stash`, no push.
- `.cdad/tmp` is already granted in the derived `edit` map by the landed U3; the U6-7 assertion confirms the write tool no longer turns it into `ask`.
- Honest limit: bash was used freely per the writer policy; no implementation content was read (only artifacts and tests).