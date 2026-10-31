# plan-review: 010-004 packet-dispatch-ergonomics, spec draft v2

- **Object reviewed:** `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`. Form: spec. Kind: draft-plan. plan_version 2.
- **Digest:** `8d2b948e2fd596ce1298c036423e5c8b91d905396bba26e8dc6a8df6571a4517`. I recomputed it with `sha256sum` and it matches the contract.
- **Packet:** `010-004-packet-dispatch-ergonomics-reviewer-plan-review-003` · execution `exec-010-004-packet-dispatch-ergonomics-001` · HEAD `ffef53bd`.

**Verdict:** this is a review, not an approval. I found **1 BLOCKING** and **2 OPTIONAL** findings.

- **B-1 and B-2 are closed.** O-1 to O-5 are also handled correctly.
- **New blocking finding (N-1):** a contradiction between v1 contexts and route C, which v2 itself introduced. It has a single closing condition.
- **No unjustified expansions.**
- **I-4 and I-5 are preserved.** The tension between the plan and the observations stays pending for Pablo.

## Intake (route C)

```
python3 scripts/cdad_packet.py render --request $P/REQUEST.json --execution-context $E > /tmp/opencode-render.md   → rc=0
cmp /tmp/opencode-render.md $P/PACKET.md                                                                         → IDENTICAL
python3 scripts/cdad_packet.py validate-request --request $P/REQUEST.json --execution-context $E                 → rc=0
python3 scripts/cdad_packet.py validate-packet --request $P/REQUEST.json --execution-context $E --packet $P/PACKET.md → rc=0
sha256sum docs/specs/010-004-packet-dispatch-ergonomics/spec.md → 8d2b948e…4517
```

- **Paths:** `P=.cdad/packets/010-004-packet-dispatch-ergonomics-reviewer-plan-review-003` and `E=.cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json`.
- **Failed attempts before these, reported verbatim:**
  - `cdad_packet.py validate …` → rc=2, `invalid choice: 'validate'`.
  - `render --request …` without `--execution-context` → rc=2, `the following arguments are required: --execution-context`.
- **Metadata check:** the identification metadata matches REQUEST.json and PACKET.md. That covers packet_id, execution_id, execution_context, and contract with its sha256.
- **Not read:** the incident `incident-reviewer-packet-001.md`, and the previous reviewer's verdict, which I did not take as proof.

## Closure of the previous plan-review

| Finding | Status | Grounds |
|---|---|---|
| B-1 | **Closed** | The 4-case matrix gives one outcome per row and applies to all three commands (`spec.md:136-147`). An old request with no flag is rejected, with no fallback (`:143`). PC-05 (`:323`) and PC-04/PC-06 agree. v1 conditions are cited from `validate_state` (`:119`), which matches `cdad_packet.py:1181-1233`. |
| B-2 | **Closed** | Canonical v1/v2 domain (`:100-111`). Link to identity and version (`:113-122`). Copies rejected (`:111`). No location fallback (`:120`). Rejection without effects in PC-06 (`:325`). Uses the real `_project_path` (`cdad_packet.py:295-310`). |
| O-1 | Closed | Literal declaration plus a JSON fence (`:186-201`). A and C are exclusive, and a mix is rejected even when the inline copy matches (`:228-236`). |
| O-2 | Closed | C is bound to the published `REQUEST.json`; a copy is not enough (`:171-182`, PC-02). |
| O-3 | Closed | Independence from cwd now depends on the root and on valid arguments (`:124-132`, PC-07). This is consistent with `cdad_packet.py:9800-9801,9900-9906`. |
| O-4 | Closed | PC-08a is an existing regression, and §7.3 forbids an artificial RED (`:331`, `:367`). PC-08b is instruction text, reviewed by reading (`:333`). |
| O-5 | Closed, with a nuance (see O-B) | `cdad_result` is out of scope (`:74`), the preamble rule is kept and its unification is deferred (`:242-256`, `:408`), and handoff is included (`:68`). |

## Findings

### N-1: route C promises v1 contexts but specifies a verifier that only loads v2
**Verdict: BLOCKING · Bucket: h · Severity: Required (correctness)**

**Evidence:**
- §4.1 admits a v1 locator, `.cdad/execution.json` (`spec.md:102-105`, `:116`).
- PC-01 covers any "contexto admisible" (`:313`).
- §7.2 requires "condiciones v1/v2 pertinentes" (`:366`).
- §4.4 says C's comparison runs "mediante el verificador existente" (`:249`). §4.2 step 5 validates the published PACKET.md (`:179`).
- The existing verifier, `verify_published_packet`, loads the context **only by v2 identity**. It calls `_load_execution_context` (`cdad_packet.py:1975-1976`), which builds `.cdad/executions/<id>/execution.json` and fails with "execution context not found" if that file is missing (`:2945-2955`).
- v1 can still be reached for new packets:
  - `_select_execution` returns a v1 context when the project has no policy (`:2937-2942`).
  - `prepare` publishes it with v1 binding fields (`:6202`, `:6433`).

**Consequence:** with a new v1 packet, `render --route C` has two incompatible readings:

- **Reading 1:** it uses the existing verifier. The emission then fails with a misleading v2 diagnostic ("not found: .cdad/executions/…"). That contradicts PC-01 and the specific diagnostics in §4.5.
- **Reading 2:** it compares against the "contexto seleccionado" (step 3, `:177`). The existing verifier cannot be used as written, and changing it would affect its other consumers: `cdad_delegate.py:550`, `cdad_dispatch.py:512` and `cdad_continuity.py:1257`.

The test-writer cannot write one deterministic test for PC-01 with v1. Without a test, a v1 user gets either a wrong rejection or a change to a shared verifier that §3 never declares.

**Proposed remedy:** an explicit choice by the owner, in one rule plus its postcondition. Either:
- **(a) C is v2-only.** A v1 locator is rejected with a context diagnostic from §4.5. This is consistent with external transport, which already depends on the same v2-only verifier.
- **(b) C compares the published PACKET.md, using `_canonical_block`, against `render_packet` with the selected context.** The text should then say it does not reuse `verify_published_packet` and does not change that function.

**Closed when:** §4.2 and §4.4 state which context C's comparison uses, and PC-01 or PC-02 gives one observable outcome for a v1 locator.

### O-A: the matrix doesn't apply cleanly to `validate_request`, the validator every consumer shares
**Verdict: OPTIONAL · Bucket: h · Severity: Consider (architecture)**

**Evidence:**
- `validate_request` receives the context document, never its path (`cdad_packet.py:1595`).
- It is called by the three commands (`:9907`), by `prepare` and its recovery paths (`:3082`, `:3571`, `:6441`), by the verifier (`:1980`), and by `cdad_result` with an arbitrary explicit path resolved against cwd (`cdad_result.py:664,674,1359-1362`).
- The spec says the shared consumers "comprueban el campo cuando existe" (`spec.md:159`) and "seguirán comprobando el request extendido" (`:84`). It does not say what they check.
- Row 2 of the matrix ("el argumento resuelva al mismo archivo canónico", `:141`) can only be enforced in the CLI layer of the three commands.

**What's open:** for a new request, if `cdad_result receive` gets a context that is a byte-identical copy outside the canonical location, nothing says whether it accepts or rejects. The harm is limited, because §3 keeps `cdad_result`'s resolution unchanged and INV-03 speaks of the locator. That is why this does not block.

**Suggestion:** state that the shared layer (`validate_request`) checks the locator's domain, its consistency with `execution_id`, and the schema version of the loaded document. Path equality (row 2) belongs only to the three commands, and to C.

### O-B: the spec's evidence section points at the architect's packet with no label marking it as encargo evidence
**Verdict: OPTIONAL · Bucket: h · Severity: FYI (facts and format only)**

**Evidence:** the evidence section is part of the reviewed contract (`spec.md:422-458`). I checked its numbers without editing them:
- `wc -c` of the architect's draft-002 PACKET.md is **6577**, which matches `:430`.
- `fd3afba7` exists as a commit (`git cat-file -t` → commit), which matches `:446`.

**What's open:** delivery evidence is mixed into the body of the contract that will be approved. If it is approved as is, the digest covers transient material. Moving it out, or labelling it as encargo evidence and not normative text, is a cosmetic choice for the owner.

## Checked areas with no finding

- **No unjustified expansions:**
  - `prepare` now rejects a non-canonical explicit context. This is declared in §3, §4.1 and PC-04 (`:75`, `:154`, `:321`).
  - The A/C exclusivity rule is the tightening O-1 asked for.
  - The symlink rule and the general path rule are deferred in §10 (`:410`).
- **Historical compatibility:** an absent field adds nothing to the header (`:158`). This can be implemented with the existing pattern of optional keys (`cdad_packet.py:1609`), and nothing is migrated (`:81`, INV-08).
- **I-4 and I-5:** §2.2 and §2.3 (`:35-48`), PC-11 (`:341`) and §4.7 are consistent with `observations-packet-dispatch.md:67-90`. C does not rescue the altered inline dispatch.
- **Plan and observations tension:** §2.1 (`:21-33`) states it and leaves it for approval. Its citations to `plan.md` (the change on 2026-10-29) and `observations:36-46` are correct. **This decision is pending for Pablo, and this review does not resolve it.**
- **Closure criteria from the observations** (`observations:38-44`) are all covered:
  - The declared context is accepted (PC-05).
  - A foreign context is rejected, naming the expected one (PC-06, PC-09).
  - A divergent body is rejected with a diagnostic (PC-08a, PC-09).
  - The intake keeps header and body distinct (PC-08b).

## Abstentions

- **Table of current decisions / `docs/adr/`:** the packet declares no `current_decisions`, and I did not reopen ADR-038, which is Proposed according to `discovery.md:72`. No finding.
- **Whether each runtime can export the received message:** outside the repository, no evidence available (§10 already defers it).
- **Real interoperability between different installed versions:** not checked. The spec scopes it in §4.6 and §10.
- **Whether the isolated installed consumer for PC-12 can be built:** not run.

## Evidence

- **Files modified:** none (`write_scope: []`). The only write was the temporary `/tmp/opencode-render.md`, outside the repo, used for the `cmp`.
- **Commands:**
  - The intake commands above.
  - Reads with `cat -n` and `sed -n` of the spec, plan-review, discovery, observations, `plan.md:110-140`, and `cdad_packet.py` at 290-312, 1180-1235, 1289-1314, 1593-1626, 1874-1993, 2170-2180, 2890-2960, 6195-6215, 9480-9495, 9795-9805 and 9895-9925.
  - `grep -n` for `validate_request(`, `verify_published_packet(` and `_load_execution_context(` across `skills/cdad-cycle/scripts/*.py`.
  - `wc -c` on the architect's packet → 6577.
  - `git cat-file -t fd3afba7` → commit.
- **Git state:**
  - `git rev-parse HEAD` → `ffef53bdaf780191e1dd1380e2d582810308418e`.
  - `git status --short` → `?? docs/specs/010-000-continuity-relative-root/discovery.md`, which was already there.
  - `git diff --exit-code` → 0. `git diff --cached --exit-code` → 0.
- **Commit:** none. I ran no tests, suite, generation, install or push.

**Draft not approved. This review authorizes no implementation.**