GREEN T3 complete. All validation and evidence below is real output from this session.

## 0. Route C validation (before work)

- Identification block vs. files: `packet_id`, `execution_id`, `execution_context`, `request`, `packet`, contract (`fc6b2ccc…`) and plan pin (`2ae8ada3…`, plan_version 2 per `approval-pending-plan-v2.md:10`) all match.
- Repository toolchain (`--project-root <repo>`, global copy untouched):
  - `render --request … --execution-context …` → exit 0, **byte-identical** to the published `PACKET.md`, sha256 `90d519df…` = declared `packet_sha256`.
  - `validate-request` → exit 0; `validate-packet` → exit 0; `validate-state` → `VALID: execution=exec-010-004-… feature=010-004-… model_policy=ordinary`.

## 1. Product diff

`skills/cdad-cycle/scripts/cdad_packet.py` (+141 lines, 3 hunks, commit `931dddea`):

1. **Parser** — `--route` added only to `render`, `choices=("C",)`. Without it, no code path changes.
2. **New section `010-004 T3`** (after `_resolve_request_execution_context`):
   - `_route_c_published_request`: `--request` must resolve to the one canonical `.cdad/packets/<packet_id>/REQUEST.json` inside the root; a byte-identical copy is rejected with the safe project-relative expected reference.
   - `_route_c_execution_context`: reuses the §4.1 matrix resolution, then requires schema v2 (v1 → explicit “route C requires a v2 … `prepare --new-execution`” cause, no conversion/relocation) and, for historical requests without locator, that the explicit file **is** the canonical `.cdad/executions/<id>/execution.json`.
   - `route_c_identification`: ordered §4.2 binding — published request → canonical v2 context → `validate_request` → `verify_published_packet` (identity/file concordance guard) → identification. Emits exactly `Route C — explicit file backup` + blank line + one ```json block with the exact 7 fields (`project_root` canonical absolute; `execution_context`, `request`, `packet` project-relative; `contract` as declared, digest already verified); `sort_keys` → deterministic; no A marker, no body, no writes.
3. **`main`** — dedicated branch: `render` + `--route C` → `route_c_identification`; the default render/validate branch is untouched.

## 2. Matrix → behavior

| PC | Implemented behavior |
|---|---|
| **PC-01** §4.2 representation | Only the literal declaration and one ```json block; exact 7-key object concordant with request/context/state; contract fields + verified digest; absolute usable `project_root`; byte-identical across runs; request/packet/state/context unmodified; no new packet dirs. |
| **PC-02** binding/rejections | v1 context → explicit route-C-requires-v2 + `prepare --new-execution` continuation; request copy outside published location → rejection naming `.cdad/packets/<id>/REQUEST.json`; non-canonical v2 context (matrix row 2/3) → mismatch naming the canonical locator; divergent `PACKET.md` (body altered, header intact) → `verify_published_packet` divergence cause. All: exit 2, stdout empty, no side effects. |
| **PC-08a** §4.4 | C verification delegates to `verify_published_packet`/`_canonical_block`: compares from the single A marker to EOF, accepts a legitimate preamble, never normalizes or rewrites bytes; `validate-packet` keeps its full-file comparison (unchanged). |
| **PC-09** §4.5 | Distinguishable causes, next action, project-relative expected reference when known; no body/objective/fragments/diffs in stderr; existing `ERROR:` wrapper and exit codes preserved; rejection only reads. |

## 3. Focused evidence (real output)

```
$ python3 -m pytest tests/test_010_004_t3_red.py -q --tb=line
7 passed in 6.96s            # 6 RED now green + the declared PC-08a regression

$ python3 -m pytest <the 6 reused tests declared in red-t3.md> -q --tb=line
6 passed in 23.14s

$ python3 -m pytest tests/test_role_packet_render.py \
    tests/test_role_packet_review_regressions.py tests/test_010_004_t2_red.py -q --tb=short
31 passed in 191.47s (0:03:11)
```

Extra read-only smoke on the repo's own published packet: `render --route C` → exit 0, emits the identification (contract `fc6b2ccc…`, canonical context, project-relative request/packet); default `render` (no `--route`) still **byte-identical** to `PACKET.md`; `--route A` → `ERROR: … invalid choice: 'A' (choose from C)`, rc=2. `py_compile` OK.

## 4. Modified files and intact surfaces

- Modified: `skills/cdad-cycle/scripts/cdad_packet.py` only (`git show --name-only HEAD` confirms).
- `git diff --stat 1b96efa5 -- tests/` → empty (tests unchanged since RED).
- Hashes: `spec.md fc6b2ccc…`, `plan.md 2ae8ada3…`, `tests/test_010_004_t3_red.py e5701b84…`, wrapper `scripts/cdad_packet.py df6463fb…` (unmodified; still the thin `runpy` entry).
- `git status`: only the pre-existing untracked `docs/specs/010-000-continuity-relative-root/discovery.md`, untouched.

## 5. Commit

`931dddea` — `feat(010-004): emision C v2-only desde paquetes publicados (T3 GREEN)` (1 file, +141).

## 6. Declarations

No full suite was run (full-suite policy: the closer runs it once at closure). No push, no global installation or modification of the installed copy, no T4/T5 work, no test or spec/plan edits.