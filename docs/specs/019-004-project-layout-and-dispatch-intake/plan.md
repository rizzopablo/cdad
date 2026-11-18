# Plan — 019-004-project-layout-and-dispatch-intake

**Plan version:** draft-002  
**Status:** Unapproved; approve with the revised specification after independent review.

## 1. Feature ficha

**Result:** existing projects retain methodology locations; new projects default to `cdad/`; declarations are root-bound; installed roles gain one structural received-dispatch validation command.

**Coverage:** specification Promises A–E, PC-01–PC-16.

**Consumes:** approved unit contract, recorded owner decisions, technical consultation, independent draft review and subsequently approved specification.

**Produces:** `project-layout-v1`, `layout-lifecycle-v1`, `received-intake-v1` and coherent effective consumers.

**Acceptance-of-use:** specification §9.

**Global constraints:**

- Preserve existing project locations and historical artifacts; no migration or automatic registration.
- Keep `.cdad/` operational storage unchanged.
- Resolve declarations against the explicit product root.
- Preserve CLI file-argument semantics and historical context rules.
- Preserve roles, approvals, policy snapshots and independent verification.
- Reject execution-binding or policy-compatibility conflicts without automatic repair, project switching or permission widening.
- Do not infer semantic acceptance, provenance or filesystem isolation from structural validation.
- No installation, deployment or publication is authorized by feature approval.

**Deferrals:** specification §11, including optional ADR index reconciliation.

All tasks remain serial. Shared packet CLI and instruction-generation edits make speculative parallelization unhelpful.

## 2. Task boundaries

### T1 — Publish deterministic project-layout resolution

**Next batch. Covers:** PC-01, PC-02, PC-04 and resolution aspects of PC-08/PC-09.

**Consumer:** packet CLI, then lifecycle consumers and bootstrap guidance.

**Create:**

- `skills/cdad-cycle/scripts/cdad_layout.py`
- `tests/test_019_004_layout.py` — test-writer only.

**Modify:**

- `skills/cdad-cycle/scripts/cdad_packet.py`

**Public contract:** `project-layout-v1`, specification §4 placement resolution.

```text
cdad_packet.py layout --project-root ROOT [--for-bootstrap]
```

Emit the specified object or a diagnostic without writes. No internal function signature is promised.

**Verification:**

- Independent test-writer writes black-box tests before implementation.
- Establish registered/custom selection, exact legacy-marker precedence, insufficient-evidence ambiguity, ordinary-documentation non-recognition, explicit new proposal and root binding.
- Include incomplete/malformed markers without treating the project as new.
- Snapshot fixture trees around success and failure.
- Preserve already-green behavior as regression, not fabricated RED.
- Distinguish placement-query success from operational policy/identity validation.

Suggested focal command after the test file exists:

```sh
python3 -m unittest tests.test_019_004_layout
```

Regression selection includes relative-root and policy tests affected by resolution.

### T2 — Make lifecycle and protections consume the resolved layout

**Planned. Covers:** PC-05–PC-09.

**Consumer:** an operator completing the existing lifecycle in a registered custom directory or unchanged legacy project.

**Consumes:** `project-layout-v1`.

**Produces:** `layout-lifecycle-v1`, specification Promises B/C.

**Expected modify surfaces:**

- Packet, result, continuity, guard, dispatch and contract-link scripts named in specification §7.
- `skills/cdad-cycle/assets/artifact-policy.json`
- `scripts/cdad-generate.py`
- `scripts/claude-code-path-guard.sh`

**Expected test:**

- `tests/test_019_004_lifecycle_layout.py`

Do not modify historical contracts, packets or this repository’s accepted policy as an integration shortcut.

**Required behavioral detail:**

- Preserve the execution identity designated by the operation’s existing request/context/binding.
- Require selected state membership and policy-path/snapshot agreement.
- Reject missing/altered locator continuations that select absent or alternative state without searching for a substitute.
- Preflight effective policy classification before operational effects.
- Show a compatible layout works and a test/implementation-overlapped layout fails with an actionable authorization diagnostic, unchanged policy and unchanged permissions.

**Detail resolution:** after T1 acceptance, inventory operational literals by consumer and distinguish historical citations. Independently review exact next-batch files, identity sources and proportional verification selection before dispatch.

This task closes a complete configured-location lifecycle; it does not create one task per path substitution.

### T3 — Validate supplied received dispatch through one command

**Planned. Covers:** PC-10–PC-14 and intake root behavior in PC-08/PC-09.

**Consumer:** a role session with an actual supplied received representation.

**Consumes:** `project-layout-v1`, `layout-lifecycle-v1`.

**Produces:** `received-intake-v1`, specification §6.

**Expected modify:**

- `skills/cdad-cycle/scripts/cdad_packet.py`

**Expected test:**

- `tests/test_019_004_received_intake.py`

Reuse request/context validators, complete canonical rendering, marker parsing and Route C publication helpers.

**Required behavioral detail:**

- Preserve Route A complete suffix byte equality and historical context boundaries.
- Admit Route C inert preamble/trailing text around one declaration and canonical identification.
- Reject duplicate declarations or identifications, mixed/partial bodies and mismatching values without normalization.
- Preserve full validation of the one named published packet.
- Preserve read-only success and rejection.
- Recover a documented legitimate historical received Route C representation for compatibility evidence. Report missing evidence rather than inventing provenance.

**Detail resolution:** after T2 acceptance, independently review helper composition, historical-context matrix, wrapper grammar controls and comparator boundaries. Independent test-writer receives the approved contract, not implementation code.

### T4 — Align effective consumers and demonstrate bounded installed use

**Planned. Covers:** PC-03, PC-15, PC-16 and specification §9.

**Consumer:** a fresh installed role and a new-project bootstrap operator.

**Consumes:** all preceding contracts.

**Produces:** revised bootstrap/effective instructions and installed-use evidence.

**Expected modify surfaces:**

- `skills/cdad-cycle/references/bootstrap.md`
- Affected cycle/epic detection, stage, lightweight, handoff and intake guidance.
- `skills/cdad-cycle/packets/`
- Affected `sources/roles/` and runtime adapters.
- Affected specialized consumers.
- Generated outputs through their generator.
- Installation sources only if packaging/invocation requires change.

**Expected test:**

- `tests/test_019_004_installed_intake.py`

Guidance must explain:

- Exact legacy signals versus ambiguity and ordinary documentation.
- Layout query versus operational authorization.
- Execution-bound continuation and no search/switch recovery.
- Policy incompatibility and owner-authorized reconciliation.
- A/C distinctions, inert wrappers and actual-input requirements.
- Installed invocation without checkout discovery.

**Detail resolution:** after T3 acceptance, enumerate exact canonical sources and generated outputs. Resolve the tested installed invocation. Record native capture capability as verified or unavailable; never invent it.

This remains combined work: executable installation/use checks and independent contextual review of meaning.

## 3. Canonical task block

```plan-tasks
{
  "validation_strategy": "Independent test-writer owns tests and RED for pending executable behavior; implementer supplies GREEN and proportional regression; reviewer independently evaluates contextual promises and integration evidence. Follow skills/cdad-cycle/references/stage-3-tdd.md Test evidence policy. Never substitute structural checks for contextual acceptance.",
  "tasks": [
    {
      "id": "T1",
      "detail": "next",
      "objective": "Expose deterministic, read-only project-layout resolution with exact legacy markers and explicit ambiguity through the installed packet CLI.",
      "produce": [
        {
          "artifact": "project-layout",
          "contract": "project-layout-v1"
        }
      ],
      "consume": [],
      "depends_on": [],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/scripts/cdad_layout.py",
        "skills/cdad-cycle/scripts/cdad_packet.py",
        "tests/test_019_004_layout.py"
      ],
      "focal_tests": [
        "tests/test_019_004_layout.py"
      ],
      "regressions": [
        "tests/test_010_000_continuity_relative_root.py",
        "tests/test_004_002_t1_policy.py"
      ],
      "integration_gate": "Reviewer evaluates project-layout-v1 precedence, exact legacy markers, insufficient-evidence diagnostics, ordinary-documentation handling, unchanged fixtures and read-only failures before T2 detail is dispatched.",
      "owner": "RED/tests: independent test-writer; GREEN: implementer; evaluation: reviewer; coordination: orchestrator"
    },
    {
      "id": "T2",
      "detail": "planned",
      "objective": "Complete the existing lifecycle using the selected methodology directory while enforcing execution-bound continuation and effective-policy compatibility without automatic repair.",
      "produce": [
        {
          "artifact": "layout-lifecycle",
          "contract": "layout-lifecycle-v1"
        }
      ],
      "consume": [
        {
          "artifact": "project-layout",
          "contract": "project-layout-v1",
          "producer": "T1"
        }
      ],
      "depends_on": ["T1"],
      "parallel": [],
      "uncertainty": "Exact operational-path changes, existing execution-identity sources and proportional regressions across lifecycle, materialization, generation and guards require the accepted resolver and a bounded consumer inventory.",
      "owner": "Orchestrator prepares next-batch detail with architect input; independent test-writer, implementer and reviewer retain their roles.",
      "resolves_when": "T1 is accepted and the named consumers, exact files, verification selection, designated-execution binding and policy-compatibility preflight are independently reviewed as the next batch."
    },
    {
      "id": "T3",
      "detail": "planned",
      "objective": "Expose one read-only received Route A/C validation command, admitting inert C wrappers without weakening canonical, identity or duplicate/mixed-input boundaries.",
      "produce": [
        {
          "artifact": "received-intake",
          "contract": "received-intake-v1"
        }
      ],
      "consume": [
        {
          "artifact": "project-layout",
          "contract": "project-layout-v1",
          "producer": "T1"
        },
        {
          "artifact": "layout-lifecycle",
          "contract": "layout-lifecycle-v1",
          "producer": "T2"
        }
      ],
      "depends_on": ["T1", "T2"],
      "parallel": [],
      "uncertainty": "Helper composition must preserve historical execution-context behavior and comparator boundaries; a legitimate historical received Route C representation must be identified for compatibility evidence.",
      "owner": "Orchestrator prepares next-batch detail; independent test-writer owns the oracle, implementer owns code, reviewer evaluates integration.",
      "resolves_when": "T2 is accepted and helper mapping, historical representation provenance and contract-derived black-box verification of canonical input, inert wrappers and duplicate/mixed/partial rejection are reviewed for the next batch."
    },
    {
      "id": "T4",
      "detail": "planned",
      "objective": "Align bootstrap and effective installed consumers and demonstrate bounded installed use without overstating native capture or structural acceptance.",
      "produce": [
        {
          "artifact": "effective-layout-and-intake-consumers",
          "contract": "effective-layout-and-intake-consumers-v1"
        }
      ],
      "consume": [
        {
          "artifact": "project-layout",
          "contract": "project-layout-v1",
          "producer": "T1"
        },
        {
          "artifact": "layout-lifecycle",
          "contract": "layout-lifecycle-v1",
          "producer": "T2"
        },
        {
          "artifact": "received-intake",
          "contract": "received-intake-v1",
          "producer": "T3"
        }
      ],
      "depends_on": ["T1", "T2", "T3"],
      "parallel": [],
      "uncertainty": "Exact affected canonical/generated consumers and tested runtime input-capture capability must be established without assuming universal native export.",
      "owner": "Orchestrator prepares the bounded exercise; test-writer owns executable checks; implementer updates sources; reviewer independently evaluates instruction fidelity and use evidence.",
      "resolves_when": "T3 is accepted, exact source/output files and installed invocation are identified, and capture capability or its explicit limitation is recorded before dispatch."
    }
  ]
}
```

## 4. Regression and closure strategy

Candidates already present include:

```text
tests/test_010_004_t2_red.py
tests/test_010_004_t3_red.py
tests/test_010_004_t5_e2e.py
tests/test_010_000_continuity_relative_root.py
tests/test_019_002_resting_orientation.py
tests/test_003_002_t2_materialize.py
tests/test_004_002_t1_policy.py
tests/test_cdad_generate.py
tests/test_install_ownership.py
```

Select proportionately by affected behavior. This list is not blanket authorization to run the complete suite.

At re-entry, preserve:

- Exact commands, working directories, exit codes and relevant output.
- Executable and contextual-review evidence separately.
- Before/after artifact comparisons and write-scope audit.
- Missing, failed, contradictory or unverifiable evidence and limits.
- Actual commit evidence.

Planning estimate remains qualitative, not measured: T1 is bounded; T2 has the widest integration uncertainty; T3 is bounded but trust-boundary-sensitive; T4 crosses consumers. No token, time or performance estimate is asserted.

Failed assumptions about compatibility, protection or input acquisition return to the orchestrator for scoped reconciliation. They do not authorize changing the acceptance contract or protected tests.

ADR index reconciliation is optional outside this plan; it is not a prerequisite or an incidental cleanup task.

---

## Evidence from this revision session

**Examined HEAD:**

```text
17a7283621d52a45f7488e5931448e5520fab0f1
```

Validation commands, executed from `<repo>`:

```sh
python3 scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/019-004-project-layout-and-dispatch-intake-architect-draft-002/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/019-004-project-layout-and-dispatch-intake-architect-draft-002/REQUEST.json --packet .cdad/packets/019-004-project-layout-and-dispatch-intake-architect-draft-002/PACKET.md

python3 scripts/cdad_packet.py render --project-root . --request .cdad/packets/019-004-project-layout-and-dispatch-intake-architect-draft-002/REQUEST.json --route C
```

Both validators returned 0 without output. Rendered identification matched the received identification.

Additional exact in-memory verification:

```sh
python3 - <<'PY'
import pathlib,subprocess,json,hashlib
p=pathlib.Path('.cdad/packets/019-004-project-layout-and-dispatch-intake-architect-draft-002')
r=json.loads((p/'REQUEST.json').read_bytes())
b=subprocess.check_output(['python3','scripts/cdad_packet.py','render','--project-root','.', '--request',str(p/'REQUEST.json')])
assert b==(p/'PACKET.md').read_bytes()
assert hashlib.sha256(pathlib.Path(r['contract']['path']).read_bytes()).hexdigest()==r['contract']['sha256']
assert json.loads(pathlib.Path(r['execution_context']).read_bytes())['schema_version']==2
print('Complete PACKET.md canonical byte equality: PASS',len(b),'bytes')
print('Contract SHA-256: PASS; execution context v2: PASS')
PY
```

Output:

```text
Complete PACKET.md canonical byte equality: PASS 8043 bytes
Contract SHA-256: PASS; execution context v2: PASS
```

Input snapshots confirmed with:

```sh
sha256sum docs/specs/019-004-project-layout-and-dispatch-intake/{spec.md,plan.md,plan-review-001.md}
```

```text
733e7ea270af05563af1efec0f15b9188888fa7ad996ed22440dc975e29a8937  spec.md
723a3ad7f25a53866043c41838d1634c67ea1b6bf9efdb0f4fee18641c13fa56  plan.md
f3382cb66c5a8797780bad067d86eb8cedabb2ce86a751b795fcfd2d358e24ec  plan-review-001.md
```

Initial and final `git status --short`:

```text
 M docs/.cdad-state.json
```

That modification predated this role’s work.

**Product tests/full suite:** not run; this was read-only specification revision.  
**Modified files:** none by this role.  
**Commit created:** none.  
**Acceptance:** not claimed; revised drafts require independent review and approval.
