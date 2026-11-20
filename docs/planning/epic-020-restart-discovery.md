## Recommendation — retain the operational directory

Keep `.cdad/` as the operational location, centralize its live path uses through the existing `cdad_layout.OPERATIONAL_DIR`, and make **only its placement declaration versionable** through an ignore-rule exception. Keep execution records ignored. This introduces indirection without relocating records, selecting between stores, or requiring compatibility fallback.

The current problem is visible directly: the locator is `.cdad/project-layout.json`, while `.gitignore` excludes all of `.cdad/` (`cdad_layout.py:22–25`; `.gitignore:11`). Versioning that locator does **not** require changing the operational directory.

This is a recommendation, not an approved design.

### Declaration and interfaces

- **One relative value:** the existing `OPERATIONAL_DIR = Path(".cdad")` in `skills/cdad-cycle/scripts/cdad_layout.py:23`. Derive operational subtree constants and live paths from it.
- **Filesystem access:** join that relative value to the supplied product root, never the coordinator’s cwd. Retain repository-relative strings in requests and evidence. The existing execution-context interface already distinguishes those identities from filesystem access (`cdad_packet.py:1665–1700`).
- An import-time **relative constant** is safe here; an import-time absolute root is unnecessary. Existing consumers already accept roots explicitly, including continuity’s `_continuity_dir(root, …)` and `_results_dir(root, …)` (`cdad_continuity.py:314–335`).
- **Existing JSON declaration:** retain its present shape. It declares methodology placement and strictly accepts only `schema_version` and `methodology_dir` (`cdad_layout.py:141–164`). It *could* carry another field after a contract change, but no demonstrated requirement needs per-project operational-directory configuration.

Prefer shared Python imports over independently resolving a store in every consumer. Shell references to the fixed **locator** are declaration references, not evidence that a second operational resolver is needed.

### Compatibility

Recommend **no new compatibility rule**: preserve `.cdad/`, existing locator bytes, and existing methodology-layout resolution. Registered projects and legacy `docs/` projects retain their current placement rules (`cdad_layout.py:47–62`). No migration, directory rename, fixture pin, or alternative-store search is necessary.

The existing JSON declaration remains the clone’s placement identity; its recognition is independent of operational validation (`tests/test_019_004_layout.py:314–320`).

## Bounded consumer and fixture scope

**Production groups to inspect/adapt:**

- Layout constants, initialization evidence, and locator protection: `cdad_layout.py:22–36,188–200,255–265`; `cdad_packet.py:5021–5022`.
- Packet publication, execution contexts, locks, transactions, temporary roots and request identities: `cdad_packet.py:145–166,266,1665–1700,2236`.
- Reception/materialization and snapshot exclusions: `cdad_result.py:69–73,133,1495–1501`.
- Continuity and guards: `cdad_continuity.py:143–146,314–335,3119`; `cdad_guard.py:116–117`.
- Dispatch/delegation, activation and version checks: their operational constants and direct path joins, including `cdad_dispatch.py:133–144`, `cdad_delegate.py:230`, `cdad_delegate_opencode.py:277`, `cdad-activate.py:25`, and `cdad-version-check.py:70`.
- Local verification tooling: `cdad-ci-gate.py:58`; checkout canary roots in `cdad-suite.py:1517–1519`.

Keep locator references in `claude-code-path-guard.sh:58,201` distinct from operational filesystem paths. Likewise, `.cdad-state.json`, installation manifests, explanatory strings and historical specifications are **not blanket replacement targets**.

**Fixture hotspots:**

- Bootstrap builder: fixed temporary roots and packet/execution helpers (`test_004_002_t2_bootstrap.py:96–109,198–207,238–253`).
- Reception builder and staging: `test_003_002_t1_receive.py:174–189,249–252,333–339`.
- Standalone continuity fixtures: `test_003_004_t1_checkpoint.py:106–114`.
- Registered-layout lifecycle fixtures: `test_019_004_lifecycle_layout.py:100–147`.
- Relative-root integration fixtures: `test_010_000_continuity_relative_root.py:131–151`.

With the recommended unchanged directory, these fixtures should mostly remain unchanged—not acquire locator pins merely to follow an implementation refactor.

### Cheap review searches

```bash
rg -n '\.cdad|OPERATIONAL_DIR|LOCATOR_RELPATH' \
  skills/cdad-cycle/scripts scripts sources skills/cdad-cycle/assets

rg -n '\.cdad|test_004_002_t2_bootstrap|test_003_002_t1_receive|test_003_004_t1_checkpoint' \
  tests --glob '*.py'
```

Classify results into declaration references, live paths, observable identity strings, and historical text. Review remaining literals deliberately rather than demanding zero matches. Check the final tracking boundary with `git check-ignore -v --no-index` for the locator and representative operational files, plus `git ls-files .cdad`.

## Verification proposal — commands only

Run this **same bounded regression superset** before changes and immediately after the integrated change, rather than repairing fixtures serially:

```bash
python3 -m pytest -q $(rg -l \
  '\.cdad|test_004_002_t2_bootstrap|test_003_002_t1_receive|test_003_004_t1_checkpoint' \
  tests --glob 'test_*.py')
```

After changes, supplement with the existing surface selector:

```bash
python3 scripts/cdad-suite.py surface --base 95e09290
```

These commands were **not executed**. The search selection is a conservative candidate set, not a claim of exhaustive dependency coverage.

Honor the owner’s **two-new-tests-total ceiling**, not a target (`epic-020-restart.md:54–62`). Adapt existing tests first. The concrete gap found is clone recognition with the locator tracked and records excluded: no matching clone/ignore check appeared in the inspected `019_004` tests. That warrants at most one proposed integrated scenario, subject to the later audit—not new tests per consumer.

## Pending owner decision and limits

Confirm retaining `.cdad/` and versioning its locator by exception. A requirement for a distinct operational directory would change this recommendation; none is established here.

`docs/landscape.md` is absent. No substitute was invented. No files or tests were changed, no tests ran, and no trust setting was accepted or bypassed; consultation reads were not blocked.