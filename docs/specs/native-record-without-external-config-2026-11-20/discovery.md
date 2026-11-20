# Native record configuration dependency — discovery

## Confirmed direction

The owner requested initiating the fix after the investigation confirmed that
native `record --native-result` incorrectly requires external runtime configuration.
Keep this a standalone maintenance correction; do not redesign the orchestrator,
provision external settings, change user configuration, or repeat the affected dispatch.
Prefer adapting existing tests without increasing the test count.

## Evidence and attribution

- Orchestrator: reproduced `record` against a disposable canonical project with
  an empty runtime map, a native payload and a declared session. Result: rc=1,
  missing `opencode` configuration; content snapshot showed zero project changes.
- Architect, separate read-only consultation: confirmed the unconditional loader
  at `skills/cdad-cycle/scripts/cdad_dispatch.py:1086–1094` and payload read at
  `:1129`. PD-9 in the existing 006-005 contract scopes required configuration
  to external transport; PD-6 permits native byte-exact delivery with explicitly
  reduced identity assurance.
- Architect: observation remains conditional and bounded. OpenCode observation
  requires `sessions_db`; contradictory evaluable identity is a rejection,
  not missing evidence. The empty installer template is intentional user data.
- No implementation changes or tests were performed by the architect.

## Process

The compact view reported at-rest with no active feature or packet. `open-unit`
refused without changes because the sole queued unit belongs to a closed epic.
This fix does not reopen that epic. The standalone architect consultation used
the documented legacy route, with explicit product/CLI locators and no prepared
packet claimed.

The architect's final spec text is materialized in `spec.md`, still a draft.
Independent draft review and owner approval remain pending; no implementation
is authorized by the draft itself.

## Verification selection

Without the regression check, a user can complete native delegation yet remain
unable to record or receive it on a default installation.

Existing case candidates identified by the architect:

- `tests/test_006_005_u1b_dispatch_entry.py`: PD-6 native bytes with unverifiable
  identity; PD-5 contradiction; PD-4 no final text. Preserve original controls
  while adding configuration partitions inside these existing cases.
- Retain PD-3 byte-exact staging, positive correlation and retired-option controls.
- `tests/test_006_005_u1a_runtime_config.py`: applicable native invalid-config and
  runtime-resolution coverage, without replacing external fail-closed controls.
- Retain capabilities regression coverage.

Proposed correction ceiling: 2 per draft/audit/result family, as justified by the
architect. No correction round consumed yet. No ceiling extension authorized.

## Draft review re-entry

The independent reviewer returned one blocker: PC-3 must not gate a
runtime-neutral observation call on OpenCode's `sessions_db` key. The final
report is materialized unchanged in `plan-review.md`. The architect is asked
to correct the draft, not the implementation. No tests or implementation
have been authorized by this re-entry.

review-round unit=native-record-without-external-config-2026-11-20; family=draft; round=1/2; event=assessment; outcome=blocking runtime-specific observation prerequisite; evidence=plan-review.md; next=architect correction followed by independent verification; authority=orchestrator applying architect proposed finite ceiling to draft correction

The architect returned a corrected final spec. Only PC-3, PC-4 and Promise B's
verification paragraph changed: motivated observation always delegates once to
the runtime module with the available section, even `{}`; availability belongs
to the module, not to an OpenCode-specific entry-level key check. The original
review report remains unchanged. Implementation and tests remain untouched.

review-round unit=native-record-without-external-config-2026-11-20; family=draft; round=1/2; event=correction; outcome=architect removed runtime-specific observation prerequisite; evidence=spec.md PC-3 PC-4 and Promise B verification; next=independent closing verification; authority=orchestrator materializing architect final text

Independent closing verification resolved the sole blocker and identified no
new blocking findings. Report materialized unchanged in `plan-review-002.md`.
The spec remains a draft pending owner approval; no implementation or tests
have been changed. Current-decision-table completeness and model-family
independence were not established by the reviewer; no such assurance is claimed.

review-round unit=native-record-without-external-config-2026-11-20; family=draft; round=1/2; event=verification; outcome=sole blocker resolved with no new blockers identified; evidence=plan-review-002.md; next=owner spec approval before test audit and RED; authority=orchestrator recording independent reviewer final text

## Owner approval

On 2026-11-20, after clarification of the existing native delivery mechanism,
the owner approved proceeding with this fix: "Ok, hagamos el fix que decías
ahora y luego vemos este otro asunto de la entrega."
This approves the reviewed scope and its finite correction ceiling. Direct
agent delivery to disk is deferred and is not part of this contract.
No publication, deployment or recovery of an unidentified client packet is
included in this approval.

The state expansion at this boundary is limited to opening this standalone
unit and pinning its approved contract, because the previous execution belongs
to a closed epic and cannot supply authority for this fix.

## Audit approval and RED selection

The owner approved the five-case audit selection with "ok", following the
explicit request to proceed to RED and implementation. Preserve existing nodeids
and original controls. No substitutes or POST-AUDIT are needed.

The approved spec remains controlling where the audit uses shorthand:
PC-2 requires `completed + staged` and an actual descriptor, not merely a
termination value. PC-7 requires rejection of a present non-object runtime
section, invalid/unreadable JSON and forbidden keys; it does not authorize a
broader top-level schema validation campaign. Unreadability checks must be real
and feasible under the executing OS user, not fabricated permission failures.

RED consequence recorded: without these protections, a default installation can
execute native delegation but cannot record it; skipping observation could
also hide a contradictory identity. Family audit had no correction findings;
the report's "round 1 of 2" describes its initial assessment, not a consumed
correction round. Draft correction consumption remains 1/2; result 0/2.

## RED re-entry — fixture correction required

The test-writer committed `2f7e1d7f`, tests only, and reported assertion failures
for missing native runtime configuration. Its exact final report is preserved in
`red-report.md` through the native receipt. No implementation is authorized yet.

Boundary check by the orchestrator: the fixture's `_observe()` returns
`(None, "no-store")` at `tests/test_006_005_u1b_dispatch_entry.py:310–313`,
while its CLI emits successful JSON `null` for that outcome. This cannot
distinguish unavailable observation from successful observation with no
candidate. PC-6 requires that distinction, not production code interpreting a
fixture-specific `"no-store"` reason. Return to test-writer to make unavailable
surface explicit at the fixture module boundary and preserve available/no-row
behavior. A directory is not evidence of an unreadable regular file; accurately
label non-regular cases and exercise unreadability where feasible.

The report also gives inconsistent focused/full RED counts. Require actual
pytest collection nodeid equality and saved exact command outputs on the next
delivery, not a comparison of method names presented as collection evidence.
The original report and receipt remain unchanged.

review-round unit=native-record-without-external-config-2026-11-20; family=result; round=1/2; event=assessment; outcome=RED fixture conflates unavailable observation with successful null and evidence summary is inconsistent; evidence=red-report.md and tests/test_006_005_u1b_dispatch_entry.py fixture boundary; next=test-writer correction before GREEN; authority=orchestrator verifying result against approved PC-6

## RED correction verification

Test-writer correction `51b89346` makes the fixture's unavailable surface
return nonzero with a named diagnostic, retaining successful `null` for
available observation without a candidate. It labels non-regular input
accurately and conditionally exercises a genuinely unreadable regular file.
The original controls and nodeids remain. The correction report is preserved
unchanged as `red-correction-report.md`.

Orchestrator verified saved collection evidence: identical 36 nodeids across
u1b/u1a before and after; saved pytest output reports exactly the same five
audited failures and 31 passes, with assertion failures on missing runtime
configuration. These are pending-contract failures, not import/setup errors.
Some later guards remain unexecuted until earlier assertions turn green; GREEN
must demonstrate them. No new test nodeids or origin/destination map delta.
Materialized the role's inventory description delta for u1b; the previously
unlisted installer helper files remain a separately reported integrity issue
to resolve before Review, not a RED blocker.

Procedural limitation: the correction role validated request and packet but
reported not running received-dispatch intake. No automated received-text
validation is claimed. The request, packet, declared role, committed write
scope and durable receipt have been checked at re-entry. Future dispatches
retain the explicit intake duty; this does not expand any permission.

review-round unit=native-record-without-external-config-2026-11-20; family=result; round=1/2; event=verification; outcome=fixture boundary corrected and consistent defect-sensitive RED evidence verified; evidence=red-correction-report.md and tests/.native-record-evidence; next=GREEN with unchanged approved tests; authority=orchestrator validating scoped role delivery against approved contract

## GREEN re-entry — test cleanup defect

Implementer returned `5be4ff93`, changing only the dispatch entry and the targeted
reference, with no test changes. Its report records 35 passed and one failing
test in u1b/u1a, plus seven passing proportional-regression modules. GREEN is
not declared complete. The exact report is preserved in `green-report.md`.

The reported remaining error is independently visible in the test:
`self.addCleanup(lambda: unreadable.chmod(0o600))` executes after `tearDown`
has removed the temporary tree. Fixing this belongs to the test-writer; it
must not change the product, assertions or feature behavior. Require the
complete 36-test run after correction, not absence of an assertion before a
cleanup exception.

review-round unit=native-record-without-external-config-2026-11-20; family=result; round=2/2; event=assessment; outcome=unreadable-file cleanup runs after temporary-tree removal; evidence=green-report.md and tests/test_006_005_u1b_dispatch_entry.py cleanup/tearDown; next=test-writer minimal cleanup correction and full focal verification then adjudication at ceiling; authority=orchestrator verifying GREEN boundary

### Cleanup dispatch delivery gap

The first cleanup worker returned before editing or running tests because it
could not access literal received-dispatch bytes for intake. Its exact final
text is retained in the durable receipt of
`native-record-without-external-config-2026-11-20-test-writer-post-audit-001`.
No product correction was attempted; result round remains 2/2, not reset or
extended. The successor provides a literal native prompt capture inside its
declared documentation read scope. Its content is generated from route C
renderer stdout and explicit locator lines, without a packet-body fallback.
This resolves a delivery resource gap and changes no authority or test scope.

## Final ordinary correction verified — Review entry

Test-writer commit `2140c64a` changes only the cleanup lifetime and adds fresh
evidence. Orchestrator checked the diff: no assertions or nodeids were changed.
The role reports 36 passed; its exact final text is preserved in
`cleanup-report.md`. Intake succeeded using the literal capture; provenance
beyond structural validation is not claimed.

Independent orchestration execution after that commit:

```text
python3 -m pytest -q -rf tests/test_006_005_u1b_dispatch_entry.py tests/test_006_005_u1a_runtime_config.py tests/test_006_005_reviewfix.py tests/test_006_005_u6fix4_native_selection.py tests/test_006_005_u6fix6_model_parity.py tests/test_006_005_u6fix1_capabilities_entry.py tests/test_006_005_u4_single_entry.py tests/test_007_003_continuity_at_edges.py tests/test_007_003_legacy_reanchor.py
95 passed in 419.98s (0:06:59)
```

Exact stdout is retained at
`.cdad-execution/native-record-proportional-verification.txt`.

The role's two previously unlisted helper metadata entries are materialized
with capability `generation-install-permissions`, zero nodeids, low confidence
and explicit `VERIFY` contracts. This fixes inventory presence, not semantic
accreditation. No new helper behavior, retirement or substitution is claimed.
`python3 scripts/cdad-suite.py validate` now returns rc=0, status `ok`,
2208 collected nodeids, 260 inventoried modules; its existing placeholder-map
and pending-timing notes remain visible. Tests and helper deltas are already
present in the revision measured by that integrity check.

At the ordinary result correction ceiling 2/2, both admitted defects are
verified resolved; no remaining finding is dismissed by budget exhaustion.
Independent review of the product diff and test-to-contract mapping is still
required. Any newly found blocker requires explicit adjudication/replanning,
not an automatic third correction.

review-round unit=native-record-without-external-config-2026-11-20; family=result; round=2/2; event=verification; outcome=cleanup corrected, 95 proportional tests green and inventory integrity rc0; evidence=cleanup-report.md and native-record-proportional-verification.txt; next=independent result and test-mapping review at ceiling, no further correction authorized; authority=orchestrator verifying final permitted correction

Full suite not executed at this boundary: proportional checks directly exercise
native/external configuration, observation, correlation, reference wording,
capabilities and continuity edges. No claim of full-suite green, live-client
recovery, deployment or publication is made.

## Independent review re-entry — owner prioritization pending

The read-only reviewer found no blockers and judged PC-1..PC-9 met. It
independently ran 63 focused tests (rc=0), compared the same 36 collected
u1b/u1a nodeids and audited original-assertion preservation and test mapping.
Its exact final report is materialized unchanged in `review.md`.

Three optional findings are retained without dismissal:

- F1: syntactically valid JSON with a malformed top-level document or
  `runtimes` map is treated as absent configuration on the native path. PC-7
  deliberately selected invalid JSON/non-object *section* rejection without
  broader schema validation. The reviewer classifies this as optional, not a
  violated numbered postcondition. Proposed disposition: explicit deferred
  hardening, not expansion of this fix.
- F2: native observation no longer adds the synthetic `runtime` key to the
  available section; supported OpenCode observation and configured regression
  tests pass. Compatibility for third-party observation modules that depended
  on that synthetic key is unverified. Proposed disposition: accept the
  disclosed compatibility limit for this narrowly approved correction.
- N1: inventory indentation is cosmetic; JSON parses and integrity validates.
  Proposed disposition: accept cosmetic residue, no new correction round.

These are proposals for owner prioritization, not recorded acceptance. Review
gate remains pending that strategic decision; no automatic third correction
is authorized. No blockers were dismissed due to the ceiling.

review-round unit=native-record-without-external-config-2026-11-20; family=result; round=2/2; event=verification; outcome=independent review reports no blockers, three optional findings preserved; evidence=review.md; next=owner prioritization before closure drafts; authority=orchestrator recording independent review without self-approval

## Owner prioritization and closure preparation

The owner answered "si ok" to the explicit proposal to proceed to closure with
the disclosed optional findings, without expanding this fix. Dispositions:

- F1 accepted as deferred hardening: broader top-level runtime-config schema
  validation remains outside the selected PC-7 boundary. This accepts the
  described current behavior, not a claim that malformed structure is validated.
- F2 accepted as a disclosed compatibility limit: no supported OpenCode
  regression observed; third-party reliance on the synthetic observation
  `runtime` key remains unverified.
- N1 accepted as cosmetic residue: inventory JSON is valid and integrity rc=0.

No blocker is waived and no third result correction is authorized. Family
consumption closes at draft 1/2, audit 0/2, result 2/2. Direct-to-disk delivery
remains deferred as the owner requested.

Review priority is owner-approved. Memory Bank drafts and their approval remain
the next stage; no feature closure, deployment or publication is claimed yet.

review-round unit=native-record-without-external-config-2026-11-20; family=result; round=2/2; event=adjudication; outcome=owner accepted optional F1 deferred-hardening F2 compatibility limit and N1 cosmetic residue, no blockers; evidence=review.md and owner "si ok" approving disclosed limits; next=scribe closure drafts, no additional correction; authority=owner explicit review-priority approval

## Memory Bank approval and release authorization

The owner approved the materialized Memory Bank drafts, including ADR-046,
with "ok", and explicitly authorized deployment, anonymization, squash and push.
The approved activeContext entry and Done entry are materialized; the
pending-approval-only progress replacement (draft 2a) is not applied at closure.
ADR status/decisor metadata now records the actual approval; its decision text
is unchanged. Original drafts and receipt remain unchanged.

Publication follows the standing separate-export, single fast-forward commit
policy: preserve private main and existing public history; sanitize the complete
candidate tree before push. This authorization does not authorize rewriting
previous remote history. Release results will be recorded in the local
operational publication report; deployment and push are not claimed by this
approval record.
