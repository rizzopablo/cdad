I've validated route C, and the packet is admitted. Below is the review, written as `plan-review.md`, which you'll need to save as a file.

# plan-review — 010-004 packet-dispatch-ergonomics (SPEC draft)

**Reviewed object:** `docs/specs/010-004-packet-dispatch-ergonomics/spec.md` (form: spec, kind: draft-plan, plan_version 1)
**Digest:** `3a52522f285e42756d7240f84b5b76338837c7642169970ae8893e708961a038` (recomputed, matches)
**Packet:** `010-004-packet-dispatch-ergonomics-reviewer-plan-review-002` · execution `exec-010-004-packet-dispatch-ergonomics-001` · HEAD `c5e3dd6b`

**Dictamen:** this is a review, not an approval. The draft holds 2 BLOCKING findings and 5 OPTIONAL ones. It reaches its stated intention only once B-1 and B-2 are fixed. Neither touches the overall direction (reuse route C, add a context field, separate the three kinds of evidence), which the code supports. Pablo decides the blockers and the plan/observations tension.

## Intake (route C)

```
python3 scripts/cdad_packet.py validate-request --project-root . --execution-context .cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json --request .cdad/packets/<id>/REQUEST.json   → rc=0
python3 scripts/cdad_packet.py render  (same args) > /tmp/render-rev002.md; cmp /tmp/render-rev002.md .cdad/packets/<id>/PACKET.md → rc=0, IDENTICAL
python3 scripts/cdad_packet.py validate-packet (same args) --packet .cdad/packets/<id>/PACKET.md → rc=0
sha256sum docs/specs/010-004-packet-dispatch-ergonomics/spec.md → 3a52522f…a038
```

The identification metadata matches REQUEST.json and the header: packet_id, execution_id, contract and its sha256. The incident report `incident-reviewer-packet-001.md` was not read or relied on.

## Findings

### B-1 — Rule 4.1.6 contradicts PC-04 for old requests, and claims to preserve behaviour that doesn't exist
**Verdict: BLOCKING · Bucket: h · Severity: Required**

- **Evidence:**
  - Rule 4.1.6 (`spec.md:83`) says that for old requests with no locator, "se conserva el uso explícito existente y la resolución por identidad v2".
  - Rule 4.1.5 (`spec.md:82`) lets a command skip `--execution-context` "cuando puedan resolverlo desde el request".
  - PC-04 (`spec.md:171`) says "Un contexto ausente … se rechaza … sin buscar alternativas".
  - In the code, `render`, `validate-request` and `validate-packet` today **require** the flag (`cdad_packet.py:9485-9488`) and load it relative to the working directory (`:9900-9903`). None of them resolve by v2 identity. Only `verify_published_packet` does (`:1975`), and so do the result paths (`:3046,:3414,:3616`).
  - The source the spec cites for v1/v2 conditions, `_select_execution` (`:2893-2942`), is the selection logic for `prepare`, not for these three commands.
- **Consequence:** take an old request (no locator) run without the flag. One reading resolves it by `execution_id` (rule 4.1.6 read as a fallback). The other rejects it as a missing context (PC-04). The test-writer cannot write one deterministic test for this case. And if it is a fallback, it is new behaviour presented as "conservation", without a postcondition of its own and in tension with PC-04's "sin buscar alternativas".
- **Fix:** add one rule with a matching postcondition. Either:
  - old requests keep requiring `--execution-context` on these three commands, and leaving it out is rejected; or
  - deterministic resolution by `execution_id` → `.cdad/executions/<id>/execution.json` is a declared new behaviour, with its own PC and a v1 case that has no flag.

  Also fix the citation: the v1 conditions for `render` and `validate` are those of `validate_state` (`:1182`), not those of `_select_execution`.
- **Closed when:** for the four cases (new request, with or without flag × old request, with or without flag) the spec states one observable outcome each, and PC-04 and PC-05 agree on all four.

### B-2 — The locator has no defined domain, and it adds a second source of truth next to `execution_id`
**Verdict: BLOCKING · Bucket: m · Severity: Required (security / architecture axes)**

- **Evidence:**
  - Rule 4.1.8 (`spec.md:85`) says the current rules on admitted locations "no se amplían". But no such rule exists for this input: today `--execution-context` accepts any path, absolute or relative to the working directory (`:9900-9903`, `_cwd_path` `:2175`). The project's safe-path rule `_project_path` (`:294-300`) is not applied to it.
  - For v2, the location is already a pure function of `execution_id` (`_load_execution_context`, `:2945-2955`).
  - The state binding does not store a digest of REQUEST.json (`docs/.cdad-state.json` `active_packet`: only id, role, substage, status and contract fields).
  - Rule 4.1.3 only validates the identity of the document the locator points to.
- **Consequence:** a published request becomes the thing that chooses which authority file gets loaded. Any JSON file with the same identity validates, and rule 4.1.3 cannot tell it apart: a stale copy, a file outside the project, or an absolute path. Rule 4.1.4 compares the locator against the flag, but not against the canonical path derived from `execution_id`. Locator and identity can drift apart without anyone noticing.
- **Fix:** define the locator's domain in the contract: a safe project-relative path that equals `.cdad/executions/<execution_id>/execution.json` for v2, or `.cdad/execution.json` for v1 under its existing conditions. Any other value is rejected with a context diagnostic (PC-07). This also gives PC-04 an observable "incompatible" case.
- **Closed when:** the spec states the domain and the "locator ≠ identity-derived path" case, with a rejection postcondition and no new effects.

### O-1 — The C identification has no fixed delimiter, and nothing says what happens when it arrives alongside an inline body
**Verdict: OPTIONAL · Bucket: m · Severity: Consider**

- **Evidence:**
  - Section 4.2 says only "Declara expresamente la ruta C" and "único bloque de identificación" (`spec.md:103-104`).
  - Section 4.3 rejects a modified inline body (`:125`).
  - The current intake picks the route starting from the A marker (`sources/roles/architect.md:16-18`).
- **What's open:** if the C block reuses `---cdad-packet-json`, the A-route counting rules decide first. The case "C identification plus a matching inline body" has no stated outcome. The harmful case (a divergent inline body) is already covered, so this does not block.
- **Suggestion:** fix a marker distinct from the A marker, and a precedence rule.

### O-2 — The interface `render --request <path> --route C` doesn't say which request it binds to
**Verdict: OPTIONAL · Bucket: m · Severity: Consider**

- **Evidence:**
  - `--request` accepts any path (`:9905-9906`).
  - The published-packet verifier works from `packet_id` and the published files (`:1935-1987`).
  - Section 4.2 says it verifies "el request y el archivo publicado" (`spec.md:110`) but does not require the argument to be the published REQUEST.json, byte for byte.
- **What's open:** a request copied or edited somewhere else could produce an identification for the published packet when it should not. This also overloads `render` with a different operation (verify, then emit).
- **Suggestion:** require `--request` to be the published file, or take a `packet_id`.

### O-3 — Rule 4.1.2 overstates PC-03
**Verdict: OPTIONAL · Bucket: h · Severity: Nit**

- **Evidence:** rule 4.1.2 says resolution "no depende del directorio desde el que se invoque" (`spec.md:79`). But without `--project-root`, the root is the working directory (`:9800-9801`). PC-03 states the precondition correctly: "cuando se declara la raíz" (`:169`).
- **Suggestion:** align rule 4.1.2 with PC-03.

### O-4 — PC-06 doesn't name who it binds, and the mechanical part is already true
**Verdict: OPTIONAL · Bucket: h · Severity: Consider**

- **Evidence:**
  - `_canonical_block` and `verify_published_packet` already compare from the marker to the end (`:1885-1932`, `:1981-1985`).
  - The intake has said "not the header alone" since `d7cbb1fb` (2026-10-28). That is before I-2 was observed during 010-000 (`observations-packet-dispatch.md:17-25`).
- **Consequence:** a RED test for PC-06 against the CLI would pass before GREEN. The actual remedy for I-2 is only a text change, and §7.3 already admits text is not evidence of how a model behaves.
- **Suggestion:** split PC-06 into two parts: (a) a mechanical regression that is already green, and (b) the explicit wording "header ≠ end of packet" in the intake, checked by review.

### O-5 — Loose ends: an unaddressed verifier divergence and a vague consumer scope
**Verdict: OPTIONAL · Bucket: m · Severity: FYI**

- **Unaddressed divergence:** `validate-packet` compares the whole file and does not strip a preamble. The published-packet verifier does (`discovery.md:27`; `:9910-9913` vs `:1878-1932`). The spec neither adopts nor defers this divergence that Discovery reported, and it touches §4.3 ("preámbulo … no autoriza").
- **Vague consumer scope:** §3 says "consumidores afectados" without listing them. `cdad_result.py receive/run/validate-run` also require `--execution-context` (`cdad_result.py:1678,1718,1726`).
  - Recommendation: list the consumers explicitly, or mark `cdad_result` as out of scope.
  - `skills/cdad-cycle/references/handoff-prompts.md:5-30` still presents v1 as the main entry. PC-10 should name it if it falls within "coherencia de fuentes".

## Checked areas with no finding

- **Historical render compatibility:** the header is built from a closed list of keys (`:1825-1839`), and optional fields are added only when present, following the existing pattern (`:1620`, `:1846-1852`). "Ausencia ⇒ bytes idénticos" (`spec.md:87`) can be implemented and tested.
- **Request schema:** the field set is closed, with three optional keys added in the past without loosening the rule (`:1599-1620`). Adding `execution_context` fits that pattern.
- **I-4, safe diagnostics, evidence table (§4.5), deferred-hardening:** consistent with `observations-packet-dispatch.md:48-72` and `discovery.md:64-74`. They promise nothing that can't be observed.
- **Plan/observations tension:** §2.1 states it explicitly and leaves it for approval. It does not edit the plan. Citations checked: `plan.md:123-130` and `observations-packet-dispatch.md:36-46`. **This is a pending decision for Pablo, not something the review resolves.**

## Abstentions

- I can't judge whether each runtime can export the received message (`discovery.md:74`). That is outside the repository, and no evidence is available.
- Real cross-version compatibility: an older installed CLI would reject `execution_context` with "request fields do not match schema" (`:1621-1623`). I did not check whether an orchestrator and a role can run different installed versions, so I make no finding on it.
- Whether the installed isolated consumer of PC-10 can be built: there are earlier isolated-validation artefacts (`.cdad/evidence/isolated-validate-010-000-*`), but I did not run them.
- Table of current decisions / `docs/adr/`: the packet declares no `current_decisions`. ADR-038 is *Proposed* (according to `discovery.md:72`; not reopened). I make no finding on it.

## Evidence

- **Modified files:** none (read-only; `write_scope: []`).
- **Commands:** the intake validation commands above, plus reads (`cat -n`, `sed -n`, `grep -n`) of `cdad_packet.py`, `cdad_result.py`, `cdad_continuity.py`, `sources/roles/{architect,orchestrator}.md` and `handoff-prompts.md`, and `git log -S'not the header alone' -- sources/roles/architect.md` → `d7cbb1fb 2026-10-28`.
- **Outputs:** quoted inline with each finding.
- **Commit:** none. No tests, suite, generation or install were run.

**Draft not approved. This review authorizes no implementation.**