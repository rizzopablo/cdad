## Route C validation (before work)

- Identification block metadata matches the validated `REQUEST.json` / `PACKET.md`: `packet_id`, `execution_id`, contract path and sha256 (`fc6b2ccc…`), plan pin (`2ae8ada3…`).
- Repository toolchain (`skills/cdad-cycle/scripts/cdad_packet.py … --project-root <repo>`):
  - `validate-request` → exit 0, no output.
  - `validate-packet` → exit 0, no output.
  - `render` → byte-identical to the published `PACKET.md` (empty `diff`), sha256 `c323e4a67a19f7c5e192b56457643a63f2c58510746dfa6c78039effbdc7b235` = declared `packet_sha256`. Nothing installed or modified globally.

## 1. New tests (file created: `tests/test_010_004_t3_red.py`, 857 lines)

Each test docstring records its numbered PC, observable promise and R4 user consequence; the module header carries the full traceability table.

1. `TestRouteCPositiveIdentification::test_pc01_route_c_emits_only_declaration_and_exact_identification` — **PC-01**. `render --route C` on a valid published packet with canonical v2 context: only the literal line `Route C — explicit file backup` plus one ```json block; exact 7-field object of §4.2 (not a subset — full equality, key set included); `project_root` absolute, request/packet/context project-relative; contract with all declared fields and digest verified against the file; identity concordant with request, context and state; two runs byte-identical; no change to `REQUEST.json`, `PACKET.md`, state or context. R4: otherwise the receiver resolves another file (or none) and executes work that is not the published packet (INV-05/INV-12).
2. `TestRouteCRejections::test_pc02_route_c_rejects_v1_context_as_v2_only` — **PC-02**. Canonical context replaced by a legitimate v1 document of the same identity → no usable identification, diagnostic names route C and the v2 requirement, offers the continuation (prepare/new execution/bootstrap), no conversion or rewrite. R4: no C identification on non-admitted v1 authority (INV-08/INV-12).
3. `…test_pc02_route_c_rejects_request_outside_published_location` — **PC-02**. Byte-identical request copy outside `.cdad/packets/<packet_id>/REQUEST.json` → rejection with the safe project-relative expected reference. R4: a copy could stand for the published request (O-2/INV-05).
4. `…test_pc02_route_c_rejects_non_canonical_context_copy` — **PC-02**. Byte-identical v2 context copy passed via `--execution-context` → rejection naming the canonical `.cdad/executions/<id>/execution.json`. R4: no context source without location authority (INV-03).
5. `…test_pc02_route_c_rejects_divergent_published_packet` — **PC-02/PC-09**. Published `PACKET.md` body altered, header intact → rejection; diagnostic does not print the tampered marker, `cdad-instructions`, `cdad-packet-json` or the objective; files are not rewritten/normalized. R4: no dispatch of non-validated instructions (INV-05), no body disclosure (§4.5).
6. `TestPC08aPreambleBoundary::test_pc08a_validate_packet_does_not_strip_preamble` — **PC-08a (§4.4, A1)**. Canonical file passes; file with a legitimate preamble prepended to marker A is rejected; bytes untouched. Declared **REGRESIÓN** (passes today), not fabricated RED.
7. `…test_pc08a_route_c_accepts_published_packet_with_legitimate_preamble` — **PC-08a (§4.4, A1)**. C accepts a published `PACKET.md` with a preamble before the single marker A and emits the same exact identification; the file keeps its preamble/bytes (no normalization). R4: no false negative on legitimate runtime preambles and no byte rewriting.

PC-09 is asserted inside each negative test (cause distinguished, safe expected reference/continuation, no body disclosure, non-zero exit code and existing `ERROR:` wrapper preserved); no separate diagnostic tests.

## 2. RED evidence (real output)

```
python3 -m pytest tests/test_010_004_t3_red.py -q --tb=line
… 6 failed, 1 passed in 8.58s
```

- The 6 failures are `AssertionError` for absent behaviour (`unrecognized arguments: --route C`, missing C-specific causes/references) — no `ImportError`/`SyntaxError`.
- The 1 pass is test 6 (PC-08a `validate-packet` side), declared regression per A1.

## 3. Positive controls

- The two C positive tests (1 and 7) are the controls that prevent a universal rejection from satisfying this file; they are RED today because `--route C` does not exist and become the GREEN controls.
- The currently green control is test 6’s canonical `validate-packet` acceptance (rc=0).

## 4. Reused regressions — verified green, not touched

```
python3 -m pytest tests/test_role_packet_render.py::TestPublicTask2Surface::test_p1_all_role_substage_pairs_render_and_validate \
  tests/test_role_packet_render.py::TestPublicTask2Surface::test_p1_repeated_render_is_byte_deterministic \
  tests/test_role_packet_render.py::TestPacketIntegrity::test_p2_metadata_is_canonical_and_matches_request \
  tests/test_role_packet_render.py::TestPacketIntegrity::test_p2_validate_packet_rejects_tampered_body_metadata_and_hash \
  tests/test_role_packet_review_regressions.py::TestReviewRegressions::test_p2_validate_packet_rejects_crlf_byte_variant \
  tests/test_010_004_t2_red.py::TestPC07HistoricalRequestWithoutField::test_pc07c_historical_request_without_field_gains_no_locator_metadata -q
… 6 passed in 28.41s
```

Covers: canonical acceptance/determinism, canonical metadata, altered body/metadata/hash, CRLF raw-byte rejection, default full render without `--route C`, and historical v2 request without locator gaining no metadata.

## 5. Commit

`1b96efa53743ce82b5a5a9eb65f72809310f2b41` — `test(010-004): RED T3 - emision C v2-only y frontera de preambulo PC-08a`
`git show --name-status`: only `A tests/test_010_004_t3_red.py`. Working tree clean except the pre-existing untracked `docs/specs/010-000-continuity-relative-root/discovery.md`, untouched.

## 6. Declarations

- No existing test, `StateFixture`, `PrepareProject` or shared fixture was edited; the packet was the only changed file.
- No implementation code was read: only the contract docs, existing tests and black-box CLI execution were used. The full suite was not run.