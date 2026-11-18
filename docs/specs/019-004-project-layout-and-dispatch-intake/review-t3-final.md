## T3 review

**T3’s CLI contract should not yet be declared closed.** The two previously reported cases are addressed, but I reproduced acceptance of another packet fragment that §6.4 and PC-12 say must be rejected.

### Required — A published objective is accepted as trailing wrapper text

**Verdict: BLOCKING · Bucket: h**  
**Location:** `skills/cdad-cycle/scripts/cdad_packet.py`, `_intake_fragment_guard` and `_intake_route_c`  
**Closure evidence:** Executable reproduction and contextual contract review.

I rendered the valid Route C identification for this review packet, appended the **exact objective paragraph** from its published `PACKET.md`—without the `## Objective` heading—and passed the result to `intake` via stdin. The command returned **exit 0** and `validation: "structural-dispatch"`.

The guard recognizes canonical headings and instruction delimiters, but not the actual objective content. This does **not** demonstrate that the appended text gains authority: the validated request remains authoritative. The observable defect is narrower: the CLI accredits an input containing a published packet-body fragment despite the contract’s prohibition.

**Remedy and closure:** After identifying the named publication, account for identifiable body content as well as delimiters, while retaining genuinely inert wrapper text. Demonstrate that the reproduced objective fragment is rejected and that ordinary unrelated prose remains accepted. If the intended boundary instead excludes body content without a delimiter, that requires an explicit contract decision rather than silently claiming the current prohibition is satisfied.

## Previously reported cases

The targeted refined-wrapper tests passed:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_019_004_received_intake.TestRouteCRefinedWrapperDecisions

Ran 3 tests in 49.657s
OK
```

That selection covers ordinary-key JSON as inert, objects carrying `packet_id` or `execution_id` as candidates, partial identifiers, and instruction delimiters before and after the identification. These results close the **specific prior reproductions**, not the broader fragment prohibition above.

## Evidence and limits

- Route C request and published packet validation succeeded; the supplied identification was accepted by `intake`.
- Reviewed implementation commit: **`7f46564e80f3b1b616acb6acab5d40390d7b2d70`**, changing `skills/cdad-cycle/scripts/cdad_packet.py`. Current HEAD was `2f97d053d9111368413d7f74fafd73c501abdd11`.
- The reproduction used `render --route C`, appended the objective paragraph read from the named published packet, and piped the result to `intake --project-root . --received -`; output was exit 0 and structural-dispatch validation.
- An attempted run of the whole focused intake module timed out after 120 seconds; it is **not** reported as passing. An initial targeted invocation used the wrong test class and produced three loader errors; the corrected class invocation passed above.
- No files were modified by this review and no commit was created. `docs/.cdad-state.json` was already modified when inspected.

## Outstanding outside this focused CLI review

- **T4:** installed-consumer and affected-instruction verification remain outstanding for the wider feature.
- **Spec §10:** historical Route C compatibility needs a recovered legitimate received representation or an explicit report of missing evidence to the orchestrator.
- **Spec §10:** faithful native runtime-message acquisition remains unverified; this limits any native-capture claim, not the bounded file/stdin interface.

## Abstentions

- I did not establish historical Route C provenance, verify all installed consumers, or review the complete feature for closure.
- I did not run the complete suite.