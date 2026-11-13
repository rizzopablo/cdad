# Review — 018-001 orchestrator-start

## Scope reviewed
- Diff: commits `6fad577c` (feat) + `0ef0e7e2` (test). Files: `sources/roles/orchestrator.md`, `skills/cdad-cycle/scripts/cdad_packet.py`, `skills/cdad-cycle/scripts/cdad_continuity.py`, `skills/cdad-cycle/references/orientation.md`, `skills/cdad-cycle/assets/orientation-examples.json`, `tests/test_orchestrator_startup_usability.py`.
- Contract: `docs/specs/018-001-orchestrator-start/spec.md` (sha256 `96f25143…` verified, matches validated REQUEST/PACKET).
- Execution context: v2 (`schema_version: 2`) — OK for Route C.

## Findings

### 1. Correctness — PC-4 help text now actionable
- `--input` help declares both formats (`PATH=PURPOSE` / JSON file of dispatch observations); `--update` declares JSON object (not literal/Markdown); `--replace-packet` declares incompatibilities with `--role/--substage/--objective` + requires `--reason` + active authority. Matches PC-3/PC-4.
- Verdict: **OPTIONAL** · Bucket: h · confidence ≥80%.

### 2. Correctness — PC-7 evidence capture pattern
- `orientation.md` §2 now documents capture to `.cdad/inbox/cli.stdout/.stderr`, `rc=$?` immediate, explicit condition under `set -e`, and byte-preserving payload guidance. Matches PC-7.
- Verdict: **OPTIONAL** · Bucket: m.

### 3. Architecture — PC-1/PC-2 entry change
- `orchestrator.md` session entry now consults compact `status` first; full `cdad-cycle` skill loaded only on legacy path (contract absent/unrecognized). Matches PC-1/PC-2 compact entry. No new state/gate/approval introduced (invariant preserved).
- Verdict: **OPTIONAL** · Bucket: h.

### 4. PC-8 deterministic generation
- `orientation-examples.json` adds `_procedures` pointing to `orientation.md` + `project-start.md`. Matches PC-8 doctrinal check.
- Verdict: **OPTIONAL** · Bucket: m.

### 5. Tests
- `tests/test_orchestrator_startup_usability.py` converted from `assert False` placeholders to real assertions traced to PC-4/6/7/8/9 and PC-1/2/3/5. All 6 pass.
- No test weakening observed: assertions now check concrete help strings, file presence, structural markers. No mocks over plumbing.
- Verdict: **OPTIONAL** · Bucket: h.

### 6. `make validate` F011 — environmental, not a feature defect
- Fails on `scripts/validate-subagents.sh` → `install.sh --check` drift for `skills/odoo-expert` (installed 0 files vs repo 10). Pre-existing environment/install drift, unrelated to 018-001 (no odoo-expert changes in this diff). Recommend orchestrator treat as environment follow-up, not a blocker for this feature.
- Verdict: **FYI** · Bucket: l.

## Blocking findings
None. No observable defect with ≥80% confidence under the contract.

## Abstentions
- PC-9 "real trial delivers comparable record": test only checks `docs/.cdad-state.json` is valid JSON; the actual trial record (calls/reads/context/times with coverage & limits) is not present in the diff I reviewed. I cannot verify it exists; abstain pending evidence.
- Deferred-hardening items (model read/compliance control, statistical benchmarks, causal attribution, exhaustive CLI help, history/medidor redesign, full external transport) are explicitly out of scope per spec — not reviewed.

## Verdict tuple
- Verdict: **NO BLOCKING** · Bucket: h · all axes (correctness, readability, architecture, security, performance) clean for the reviewed diff. Security/performance: no new inputs/SQL/secrets/loops; help text + reference doc only. Performance: no hot paths touched.

Report complete. No code or tests modified (read-only review).