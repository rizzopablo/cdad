I stopped before reviewing because the packet failed validation. The packet I received does not match the canonical render of its validated request, so it is invalid. **I did not review the 010-004 spec** (sha256 `3a52522f…a038`), and nothing in this report is a verdict on that spec.

# plan-review.md: invalid packet, review not started

## Packet validation

- **Packet:** `010-004-packet-dispatch-ergonomics-reviewer-plan-review-001`
- **Route:** A, with exactly one `---cdad-packet-json` marker and its closing marker present.
- **Request:** `.cdad/packets/010-004-packet-dispatch-ergonomics-reviewer-plan-review-001/REQUEST.json`
- **Execution context:** `.cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json`

Commands run from the repository root, all read-only (`E` and `P` are the execution context and packet directory above):

```
python3 scripts/cdad_packet.py validate-request --execution-context $E --request $P/REQUEST.json        # rc=0
python3 scripts/cdad_packet.py validate-packet  --execution-context $E --request $P/REQUEST.json --packet $P/PACKET.md   # rc=0
python3 scripts/cdad_packet.py render --execution-context $E --request $P/REQUEST.json | cmp - $P/PACKET.md   # SAME_AS_PACKET_MD
python3 scripts/cdad_packet.py render ... | sha256sum   # 8e5196ab0355a50aa928da8ff7eb3ea94794eccced5d2a265d22ac28a2b89e10
grep -o 'review a .\{0,140\}' $P/PACKET.md | od -c      # shows: r e v i e w   a   ` " p l a n n e d " `
grep -o 'review a .\{0,12\}' .cdad/010-004-reviewer-plan-review-packet.txt   # review a `"planned"`
```

The stored request, `PACKET.md` and the canonical render all match each other. `docs/specs/…/spec.md` and `docs/cdad-policy.json` hash to the sha256 values the packet declares.

## Blocking difference (Critical)

- **Verdict:** BLOCKING
- **Bucket:** h
- **Location:** the `<!-- cdad-instructions -->` block, in the sentence about the per-task `detail` marker (the last sentence of the instructions block).
  - Canonical text: ``review a `"planned"` task … and a `"next"` or unmarked task``
  - Text I received: `review a "planned" task … and a "next" or unmarked task`
  - The backticks are missing in both places in the text I received.
- **Consequence:** the inline packet is not byte-identical to the canonical render. The packet contract says any difference blocks and that text is never rebuilt or normalized, so I cannot treat this packet as valid.
- **Likely cause (not proven):** `PACKET.md` and the dispatch file `.cdad/010-004-reviewer-plan-review-packet.txt` both contain the backticks. That points to the backtick-plus-quote sequence being lost on the way to this session, not to a change in the stored packet.
- **Closure condition:** the orchestrator sends the packet again, either as a byte-exact inline copy or by naming it through route C. Choosing which is up to the orchestrator.

## Not verified by tool

I did not confirm the JSON header line byte-for-byte with a tool. A first `cmp` showed a difference, but it came from my own hand-copy of the base64 policy snapshot (I left out a block). The packet as received does contain the full snapshot. That result is not a finding.

## FYI

This failure is a live example of the problem 010-004 is meant to fix: inline packets not arriving intact. It belongs in `observations-packet-dispatch.md` as orchestrator input, not in a review verdict.

## Abstentions

- I make no judgement on the 010-004 spec or any of the review questions in the objective. Those questions are:
  - whether the optional `execution_context` field breaks older renders or the request schema;
  - whether PC-04 is consistent with section 4.1's resolution and fallback and with PC-05;
  - whether route C identification is unambiguous and rejects an invalid inline packet instead of using it;
  - whether I-4, safe diagnostics and the isolated installed consumer are preserved;
  - the tension between the approved `plan.md:123-130` and `observations:36-46`.

  The packet blocked before review, so all of these are left for a valid re-dispatch.

## Evidence required

- **Modified files:** none (write scope is empty).
- **Commit:** none.
- **Commands and outputs:** listed above.
