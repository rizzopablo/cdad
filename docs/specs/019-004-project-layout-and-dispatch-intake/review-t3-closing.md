## T3 review

**T3 should not yet be considered closed for its CLI contract.** The focused tests pass, and the previously reported exact-heading and fenced-JSON examples are covered. Two material boundaries remain: an identifiable packet fragment is accepted, and the adopted candidate definition rejects unrelated JSON that happens to use a common key.

### Required 1 — An identifiable inline packet fragment is accepted

**Verdict: BLOCKING · Bucket: h**  
**Location:** `skills/cdad-cycle/scripts/cdad_packet.py:11093–11109`  
**Closure category:** Executable reproduction and contextual contract review.

The fragment guard recognizes only exact heading lines. Appending the renderer’s instruction-block marker:

```text
<!-- cdad-instructions:start -->
```

to a valid Route C identification returned exit **0** and `validation: "structural-dispatch"`. This is a recognizable fragment of the inline packet, but §6.4 and PC-12 require packet fragments beside a Route C identification to be rejected. The result does **not** establish that the fragment gains authority; the defect is that the CLI accredits the mixed input as structurally valid.

**Remedy and closure:** Detect the renderer’s identifiable instruction-block delimiters as fragments, as well as its section headings. Verify rejection before and after the identification and retain positive controls for genuinely inert wrapper text.

### Required 2 — Candidate-key rule rejects unrelated JSON

**Verdict: BLOCKING · Bucket: h**  
**Location:** `skills/cdad-cycle/scripts/cdad_packet.py:10938–10942, 11128–11154`; `decisions.md:78–87`  
**Closure category:** Executable reproduction and contextual contract review.

A valid Route C identification followed by this unrelated JSON wrapper is rejected with exit **2** as a second identification:

```json
{"note":"x", "request":"coffee"}
```

The implementation follows the recorded decision’s rule that *any* object containing `request` is a candidate. But `request` and `contract` are ordinary JSON keys, so that definition does not satisfy the requested distinction between candidate identifications and unrelated JSON in any form. A legitimate wrapper can be rejected even though it identifies no packet.

**Remedy and closure:** Reconcile the recorded candidate definition with wrapper tolerance through an explicit decision on distinguishable identifying evidence, then test unrelated objects using ordinary keys alongside real and partial competing identifications. Do not silently select one candidate.

## Evidence and scope

- Route C `validate-request` and `validate-packet` completed successfully; `render --route C` matched the supplied identification.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_019_004_received_intake` → **16 tests, OK**.
- Reproductions piped the canonical Route C render plus each quoted wrapper to `python3 scripts/cdad_packet.py intake --project-root "$PWD" --received -`; outputs and exit codes are stated above.
- Reviewed target commits **`5f545845`** and **`ba514d3a`**, both modifying `skills/cdad-cycle/scripts/cdad_packet.py`. This review modified no files and created no commit. `docs/.cdad-state.json` was already modified when inspected.
- The focused selection is not a complete suite; no complete suite was run.

## Outstanding evidence outside this CLI closure

- **Historical Route C compatibility:** §10 requires recovery and identification of a legitimate historical received representation, or a report of missing evidence to the orchestrator. I did not establish its provenance.
- **Native runtime acquisition:** faithful capture of the original native message remains unverified. The spec says this does not block the bounded file/stdin contract, but it does block a claim that native capture was demonstrated.
- The wider feature’s installed-consumer and affected-instruction verification remain outside this focused T3 review.

## Abstentions

- I did not assess exhaustive historical-context compatibility or the complete feature’s closure.
- I did not independently verify all affected consumers or the full suite.