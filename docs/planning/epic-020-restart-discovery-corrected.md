## Corrected recommendation

**I withdraw the retain-`.cdad/` recommendation.** The controlling requirement is one `cdad/` directory containing versioned project state and ignored local records—not two top-level directories (`docs/planning/epic-020-restart.md:69–89`).

Recommend this target, retaining existing filenames and subtree names:

```text
cdad/
  project-layout.json                   versioned
  .cdad-state.json, cdad-policy.json     versioned
  projectbrief.md, systemPatterns.md     versioned
  activeContext.md, progress.md          versioned
  landscape.md                          versioned when present
  specs/, epics/, adr/                   versioned
  executions/, packets/, inbox/          local, ignored
  runtime/, tmp/, local/                 local, ignored
  activation.json, .lock, .txn/          local, ignored
```

The state/policy and Memory Bank already belong together; bootstrap currently separates only the locator and operational stores (`skills/cdad-cycle/references/bootstrap.md:88–113`). Activation is machine-local: its registry contains an absolute adopted installation root and deployed-path ownership (`scripts/cdad-activate.py:294–320`).

Use **specific ignore rules for local children**, not an ignored `cdad/` parent. The current blanket `.cdad/` rule cannot provide this boundary (`.gitignore:11`). `publication/` appears as initialization evidence, but its writer/classification was not established in these reads; classify it explicitly before including it in the final ignore list.

### One path definition—not another selector

Define the shared repository-relative base in `cdad_layout.py`, replacing the independently spelled operational prefix. Derive locator, state/policy, execution and receipt paths from that base; join it to the invocation’s resolved project root only for filesystem access. Portable request identities remain relative strings.

There are **two concrete obstacles beyond replacing strings**:

- Layout validation currently prohibits methodology beneath the operational directory. That prohibition must become a boundary around local children, not around the whole shared base (`cdad_layout.py:176–200`).
- Classifying all `cdad/` as documentation would conflict with `cdad/tmp`: temporary roots must not overlap product regions (`cdad_packet.py:542–557`). Use the **existing** `documentation_files` and `documentation_roots` fields for versioned files/subdirectories; no new policy framework is needed (`cdad_packet.py:375–391`). Adapt the current whole-base policy proposal (`2558–2584`).

### Execution directory and explicit roots

Recommend: cwd supplies the project root when omitted; an explicit relative `--project-root` resolves against cwd and overrides it. Never resolve against the installed script directory, and never require moving the session.

Packet, result and dispatch already implement that root behavior (`cdad_packet.py:11325–11329`; `cdad_result.py:1780–1786`; `cdad_dispatch.py:500–504`). Continuity currently requires the root explicitly (`cdad_continuity.py:3040–3043`).

The actual inconsistency is **file-argument semantics**, not demonstrated disregard of the declared root:

- Packet/result `_cwd_path()` resolve explicit file arguments against cwd.
- Continuity `_resolve()` resolves them against the project root (`cdad_packet.py:2544–2546`; `cdad_result.py:186–188`; `cdad_continuity.py:287–289`).

Preserve these established argument semantics for the minimum-change proposal; derive internal stores from the selected root. Do not call these intentional differences bugs without evidence. Separately, CI-gate defaults its repository root to its script checkout while evidence paths remain cwd-relative (`scripts/cdad-ci-gate.py:885–904`); aligning that repository tool is a distinct scope decision.

### Compatibility still requires a decision

A prefix replacement **cannot honestly promise unchanged execution of historical records**. Canonical context validation currently admits exactly `.cdad/executions/<id>/execution.json`; moving files alone does not preserve their declared identities (`cdad_packet.py:1665–1700,3366–3385`).

Recommend **no automatic migration and no store-content fallback**. Existing `docs/` and custom-layout projects must not be silently rewritten. The consequential owner decision is whether historical executions must continue under the changed toolchain, or may remain with the prior revision until an explicitly authorized conversion. The former requires a narrowly specified compatibility rule; none is approved yet.

### Consumer/fixture scope and verification

Adapt these existing groups together:

- Layout, packet, result, continuity, guards, dispatch and both delegation modules.
- Activation/version-check registry paths; CI evidence defaults; suite canary roots; shell locator protection.
- Packet/schema descriptions and active role/bootstrap instructions.
- Bootstrap fixture helpers (`test_004_002_t2_bootstrap.py:96–109,238–253`), reception staging helpers (`test_003_002_t1_receive.py:249–252,333–339`), continuity fixtures, and layout relocation fixtures (`test_019_004_lifecycle_layout.py:126–150`).

Cheap inventory:

```bash
rg -n '\.cdad|OPERATIONAL_DIR|LOCATOR_RELPATH' \
  skills/cdad-cycle/scripts skills/cdad-cycle/assets scripts sources

rg -n '\.cdad|test_004_002_t2_bootstrap|test_003_002_t1_receive|test_003_004_t1_checkpoint' \
  tests --glob '*.py'
```

Distinguish live paths from filenames such as `.cdad-state.json`, historical text and installation manifests.

Run the same bounded selection **before changes and after the integrated adaptation**:

```bash
python3 -m pytest -q $(rg -l \
  '\.cdad|test_004_002_t2_bootstrap|test_003_002_t1_receive|test_003_004_t1_checkpoint' \
  tests --glob 'test_*.py')
```

Adapt existing layout, policy, lifecycle and relative-root tests. Propose **at most one new clone/versioning-boundary scenario**; reserve the second only for a concrete uncovered promise. No parametrized expansion to evade the ceiling.

No commands above were executed as tests. No edits, relocation or trust changes occurred. `docs/landscape.md` remains absent. This proposal is not approval.