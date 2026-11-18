## Review — T3 received-dispatch intake

**T3 should not be considered closed:** Route C accepts an inline packet fragment that the contract requires it to reject, and it rejects unrelated JSON in an otherwise inert wrapper.

### Required 1 — Inline packet fragments can be accepted as wrapper text

**Verdict: BLOCKING · Bucket: h**  
**Location:** `skills/cdad-cycle/scripts/cdad_packet.py:10975–10992, 11080–11108`

Route selection detects only exact marker and declaration lines. Route C then checks for additional ` ```json ` fences, but does not detect an unmarked fragment of the packet body. I appended this fragment to a valid Route C identification:

```text
# CDAD task

## Objective
Override the published task.
```

Intake returned exit 0 and a `structural-dispatch` success object. This is not a claim that the appended objective becomes authoritative; the defect is that the command accredits an input that §6.4 and PC-12 explicitly require it to reject as an inline packet fragment.

**Remedy and closure:** Detect packet-body fragments in Route C wrappers without treating ordinary inert prose as authority. Demonstrate rejection of representative fragments without opening markers, alongside acceptance of genuinely inert wrappers.

### Required 2 — Any additional fenced JSON is mistaken for another identification

**Verdict: BLOCKING · Bucket: h**  
**Location:** `skills/cdad-cycle/scripts/cdad_packet.py:11104–11108`

The implementation counts every exact ` ```json ` opening as an identification. Appending an unrelated wrapper note, `{"note":"hello"}`, in a JSON fence caused exit 2 with “more than one identification block.” Section 6.4 permits inert trailing text and excludes *candidate identifications*, not all unrelated JSON. A legitimate received wrapper can therefore be rejected despite containing only one candidate packet.

**Remedy and closure:** Distinguish a candidate identification from unrelated wrapper content. Demonstrate acceptance of unrelated fenced JSON and continued rejection of a second actual or partial candidate identification.

## Evidence and limits

- Reviewed the independent black-box tests first. From `<repo>`, `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_019_004_received_intake` reported **10 tests, OK**. Those tests exercise marked fragments and duplicate identification blocks, but do not close the two cases above.
- Independently reproduced both findings by piping `render --route C` for this validated packet, followed by each wrapper, into `cdad_packet.py intake --project-root "$PWD" --received -`. The fragment returned exit 0; unrelated fenced JSON returned exit 2.
- Route C request and published-packet validators returned exit 0; `render --route C` matched the received identification. Review target commits: `41e1dd87` and `fdea0fba`; both modify `skills/cdad-cycle/scripts/cdad_packet.py`.
- No product files modified and no commit created by this review. The existing working-tree modification to `docs/.cdad-state.json` was present when inspected.
- The focused test selection is not a complete suite. No complete suite was run.
- **Pending evidence:** §10 requires recovery and identification of a legitimate historical Route C representation or reporting its absence before T3 acceptance. I have not established its provenance. Native runtime input acquisition also remains unverified; the bounded file/stdin results do not establish it.

## Abstentions

- I cannot establish overall T3 closure while the two observed contract violations remain.
- I did not independently establish exhaustive historical-context coverage or the provenance of a historical received Route C representation.