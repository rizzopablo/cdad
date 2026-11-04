# review.md — 016-001-contract-test-link (stage 4, reviewer)

**Intake:** route C. I checked the packet before working:

- `validate-request` and `validate-packet` both returned rc=0.
- `render` matched `PACKET.md` byte for byte (`cmp` → MATCH).
- `render --route C` matched the identification I received.
- The contract sha256 `88b144e5…a8bb278a…eca688e` matches the file on disk.
- The execution context is v2.

**What I reviewed:** the diff `8950629f..HEAD` (14 commits, up to `d46ed99f`). I modified no files and made no commit. The only uncommitted change in the worktree, `docs/.cdad-state.json`, was already there and is not mine.

**Commands I ran:**
- `python3 -m pytest -q tests/test_016_001_contract_test_link.py` → `7 passed in 5.81s`.
- The CLI on the unit's own registry, with a real collection from `pytest --collect-only` → `status: ok`, rc=0. That run had no baseline, so the result says "tests nuevos no comprobados".
- Breakage reproductions in `/tmp/rv16`, and mutation runs on copies in `/tmp/rv16/m` (shown below).

## Blocking findings

### B1 — Critical: one stray backtick silently drops every later marker, which can give a false green (PC-3, review item 4)
- **Where:** `skills/cdad-cycle/scripts/cdad_contract_links.py:212-224`. The tracking of multi-line inline code (`open_tick`) never closes at a blank line or the end of a paragraph. Markdown does close it there.
- **Evidence:** a contract with `<!-- cdad:pc PC-1 promise=A -->`, then `See the \`x`, a blank line, and `<!-- cdad:pc PC-2 promise=A -->`. The registry only links PC-1. Result: `status: ok`, rc=0, and the PC-2 gap does not appear. Without the stray backtick, the same contract correctly gives rc=1 with `gaps: PC-2`.
- **Consequence:** a common typo in prose shrinks the set of obligations without any warning. The user gets a structural green while promises have no verifier. That is the exact defect PC-3 exists to prevent, and it was introduced by the GREEN-003 fix.
- **Closure condition:**
  - Close the open inline span at a blank line (paragraph end), or treat any span still unbalanced at a paragraph boundary as text.
  - Add a RED test with the fixture above that expects rc=1 and `PC-2` in `gaps`.
- **Verdict:** BLOCKING · **Bucket:** h

### B2 — Required: the result does not say which obligations it covered; an empty set of obligations passes, and legacy mode does not declare "obligaciones indexadas" (PC-3, PC-8, PC-1; spec §2 "Obligaciones nuevas y contratos antiguos")
- **Where:** `cdad_contract_links.py:599-610`. The payload has no mode (markers or legacy), no list of obligations and no list of links.
- **Evidence:**
  1. **Legacy mode:** `legacy_obligations` with one entry and a valid link → the output is identical to markers mode. It never says it covers "las obligaciones indexadas", which spec §2 requires literally. The unit's own registry only states this in its `coverage_note` field, which the CLI never reads.
  2. **Empty set:** a contract with no markers, no legacy index and `links: []` → `status: ok`, rc=0.
  3. **Unrecognised markers:** markers inside list items (`- <!-- cdad:pc PC-1 … -->`), blockquotes, or after text on the same line (`**PC-3.** text <!--…-->`) are not counted. The result is `ok` with zero obligations and nothing tells the author.
  4. **PC-1:** it promises that "el resultado permite recuperar … obligación, promesa, verificador y comprobación protegida". The result only returns `contract` and `unit`; obligations and verifiers can only be recovered by reading the registry by hand.
- **Consequence:** a green with zero obligations, or a legacy green, looks the same as a complete green. A reader takes it as full coverage, which PC-8 and §2 forbid ("no se presentan como cubiertas").
- **Closure condition:**
  - The payload states `mode` (`markers|legacy`) and lists `obligations` (id, promise, verifiers).
  - In legacy mode it carries the "obligaciones indexadas" declaration.
  - An empty set of obligations with a registry present gives `invalid`, or at least an explicit diagnostic that is not `ok`.
  - Tests that assert each of these.
- **Verdict:** BLOCKING · **Bucket:** h for the legacy declaration (literal spec text); m for the empty set and PC-1.

## Non-blocking findings

### O1 — Duplicate markers are detected but no test protects it (PC-3, "cada ID aparece una sola vez")
- **Evidence:** I replaced `if pid in found:` at line 232 with `if False:` → 7 passed.
- **Consequence:** if this regresses, a repeated ID with a different promise is silently resolved in favour of the first one, and gaps get grouped under the wrong promise.
- **Fix:** add a fixture with a duplicate ID and assert `duplicate_marker` plus rc=1. Defer it under `deferred-hardening` if the orchestrator decides so.
- **Verdict:** OPTIONAL · **Bucket:** m

### O2 — The PC-6 test only checks how the CLI exits, not that the handoffs carry the rule (item 5)
- **Evidence:** `test_R_C2` checks rc=0 without a baseline and rc=1 with a baseline. I changed every `RED` in `stage-3-tdd.md` to `R3D` → 7 passed.
- **What is fine:** the pointers in `handoff-prompts.md`, `stage-3-tdd.md`, `re-entry.md` and `SKILL.md` all point to one home (`contract-test-links.md`). None of them restates the format or promises a gate at RED. That part is consistent with PC-6.
- **What is missing:** no packet source (`substages/*.md`) was touched. Carrying the rule in packets depends on the orchestrator writing it into the objective.
- **Consequence:** if a later edit drops the rule from the handoffs, no test fails and the deltas get lost.
- **Verdict:** OPTIONAL · **Bucket:** m

### O3 — Nit: matching link errors by prefix (`startswith(where)`, line 557)
- An error in `links[10]` marks `links[1]` as not covering its obligations. This only produces false reds, never a false green.
- **Fix:** compare `where == w or w.startswith(where + ".")`.
- **Verdict:** OPTIONAL · **Bucket:** l

### O4 — Nit: dead code
- Lines 395-396 (`pass`).
- `current_nodeids is not None` at line 520 is always true.
- **Verdict:** OPTIONAL · **Bucket:** l

## Do the tests catch breakage? (item 2, mutations on copies)

| Group | Mutation | Result |
|---|---|---|
| A | contract hash ignored | 1 failed ✔ |
| A | failed collection accepted | 1 failed ✔ |
| B | gaps turned off | 2 failed ✔ |
| B | duplicate markers ignored | 7 passed ✘ (O1) |
| C | new unlinked nodeids not reported | 2 failed ✔ |
| C | no-baseline message removed | 2 failed ✔ |
| C | PC-6 pointer in stage-3 changed | 7 passed ✘ (O2) |
| D | `not_configured` made blocking | 1 failed ✔ |
| D | `limits` removed from `not_configured` | 7 passed (low effect) |

## Remaining review items
- **Item 3:** the registry indexes PC-1..PC-8. Each locator appears exactly once, which the CLI confirms (rc=0 on the real collection). It does not mix markers with the legacy index. The selection is declared as limited only in `coverage_note`, not in the result (see B2).
- **Item 6 / PC-7:** a missing registry gives `not_configured`, rc=0, without asking for a collection. A corrupt registry gives `invalid`. Both are confirmed by tests and by mutation.
- **Inventory:** the delta in `suite-inventory.json` adds one entry with 7 nodeids, matching what was collected.

## Abstentions
- I did not run the full suite, and I did not run the installer group, which the orchestrator runs in parallel. I make no claim about regressions outside this test file.
- I did not check how packets mechanically carry the registry path; that depends on the orchestrator.
- I did not judge the semantic relevance of each `protects` field against its test beyond reading the names. That is an independent judgement I can't credit from structure alone.
- I only examined the RED-002 / GREEN-003 conflict through its results (the tests and B1), not the history in the inbox.
