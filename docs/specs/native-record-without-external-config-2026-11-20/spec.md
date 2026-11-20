# Draft spec: `native-record-without-external-config-2026-11-20`

**Standalone maintenance feature; no epic.**  
**Status: Approved by the owner on 2026-11-20.** Independent draft review is recorded in `plan-review-002.md`.

## 1. Functional description

Native delegation has already delivered final text. Recording that delivery must not require configuration used to launch an external worker. Preserve evidence-based correlation when observation is possible and explicitly declare reduced assurance when it is not.

Existing CLI signature remains unchanged:

```text
cdad_dispatch.py record --project-root R --packet P --attempt-id A --runtime X
    [--native-result FILE|-] [--session S] [--parent S] [--since TS]
    [--continuity-attempt N] [--json]
```

## 2. Contract

### Promise A — Record genuine native delivery without external transport setup

**PC-1.** For an otherwise admissible request and nonempty native result, an absent `runtimes.json`, absent runtime section, or empty runtime map does not prevent recording. No external launch settings are required.

**PC-2.** When identity cannot be verified, recording produces exactly one attempt and stages the original bytes with the existing descriptor binding. The envelope declares `completed + staged`; accredited session and reported model remain null, with provenance/diagnosis explaining the missing evidence. Recording does not receive or approve the delivery.

**Verification:** executable. Adapt the existing PD-6 case for configuration-availability partitions and retain the existing PD-3 byte-integrity/reception check. Acceptance requires successful staging, exact bytes, one attempt, null unverified identity, and explicit explanation. Evidence: focused test output and resulting fixture records. Limits: fixtures establish recording behavior, not authenticity of upstream native capture.

### Promise B — Preserve observation and reject contradictory identity

**PC-3.** Preserve the existing observation motive: a declared session, declared parent, or absent native payload. `--since` alone does not introduce an observation motive. With a motive, invoke the runtime module’s existing bounded observation exactly once, passing the available runtime section, including an empty `{}`, even when native bytes are available. The runtime-neutral entry must not gate observation on `sessions_db` or another module-specific configuration key; the module determines whether its observation surface is unavailable. Without a motive, do not observe.

**PC-4.** When motivated module observation reports an unavailable surface—including missing configuration/store location—nonempty native bytes may still be recorded under PC-2. Explain the unavailable surface; never infer a store location, copy the supplied session into accredited identity, or invent a model.

**PC-5.** An observed contradictory evaluable identity key still returns `blocked + none + null`, naming the key, without registering an attempt or staging the payload. Available native bytes do not override contradiction. Existing positive-correlation thresholds remain unchanged.

**PC-6.** Omitted native text never creates a delivery. If observation is unavailable, fail nonzero without durable registration or staging. If observation is available, preserve existing attempt-only behavior: no staged part, descriptor, or receipt, and `unknown + none`. An explicitly missing, unreadable, or empty native-result input remains an error rather than becoming “omitted.”

**Verification:** executable. Retain configured-observation controls; adapt the existing observation control to demonstrate that motivated observation reaches a runtime module without `sessions_db`, including with an empty runtime section, and preserves rejection of contradictory identity returned by that module. Strengthen the existing contradiction case with native bytes and no-effect assertions; extend the existing no-final-text case to unavailable observation. Acceptance requires exactly one bounded module observation when motivated, none without a motive, and the specified envelope, ledger/staging effects, and named diagnostics. Evidence: focused subprocess-test output and fixture snapshots. Limits: no live runtime/schema compatibility claim or exhaustive timeout campaign.

### Promise C — Optional configuration does not mean invalid configuration is ignored

**PC-7.** Native recording tolerates absence, not configuration errors: unreadable/invalid JSON and a present non-object runtime section fail nonzero without durable registration or staging. A present object section still rejects the existing forbidden keys with their existing guidance. Do not introduce broader schema validation or change unrelated-key policy.

**PC-8.** Runtime validation remains mandatory: missing, invalid, or unavailable runtime-module identifiers cannot succeed merely because native text exists. Never infer runtime from project configuration.

**PC-9.** External dispatch/default-dispatch, capabilities, migration, retired-option rejection, and installer behavior remain unchanged. In particular, missing external runtime configuration remains fail-closed with its existing diagnostic.

**Verification:** combined. Executable checks exercise native invalid-configuration/runtime rejection and retain external configuration/capabilities regressions. Independent contextual review confirms the native-only relaxation, unchanged producer/protocol boundaries, and accurate reference wording. Acceptance requires all mapped checks passing and no unresolved blocking review findings. Evidence: focused/proportional regression output and review report. Limits: neither tests nor diff review prove every runtime integration.

## 3. Verifiable invariants

- Existing packet verification, suspension and continuity admission precede observation and new recording effects.
- Only existing ledger/staging mechanisms write recording artifacts; no new receipt or approval path.
- No runtime launch, inferred session-store path, service management, or user-configuration mutation.
- Missing evidence is declared; contradictory evidence is never downgraded to missing evidence.
- No reopening or modification of the closed epic.

These restrictions receive independent contextual review; existing applicable admission and no-effect regressions remain controls.

## 4. Scope and acceptance criteria

**Implementation scope:** `skills/cdad-cycle/scripts/cdad_dispatch.py`; targeted clarification in `skills/cdad-cycle/references/cli-delegation.md`.

**Test scope:** adapt existing native-record/config cases, preserving nodeids. No OpenCode module change is presently justified; its observation surface already reports missing `sessions_db`.

Acceptance requires every PC’s selected evidence, defect-sensitive RED evidence for newly committed behavior, green focused/proportional regression, independent result review, and ordinary CDAD approvals. Record any unexecuted full-suite gate explicitly.

**Correction ceiling:** **2 rounds**, adopted with owner approval, applied independently to draft, audit, and result families. The change is localized, but confusing missing evidence with contradiction can falsely accredit identity; two rounds allow a focused correction and verification without an open-ended redesign. The orchestrator records and adjudicates it.

### Deferred-hardening

- No new runtime-config schema/version enforcement: unrelated to the native/external dependency defect.
- No store discovery, live-runtime provisioning, exhaustive timeout testing, or upstream capture attestation.
- No orchestrator redesign, installer changes, broad test replacement, or new epic.
