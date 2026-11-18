# Contract-Driven AI Development (CDAD)

**Make AI-assisted work easier to specify, verify and hand over.**

An agent can produce convincing work without meeting the need behind it. Reviewing
everything afterward is expensive, and a new session can lose the decisions that
made the work understandable.

CDAD is a methodology and a set of skills, role definitions and command-line tools
for addressing that problem. Agree on the outcome before implementation, separate
production from verification, and keep decisions and evidence available for the
next session. It adds discipline and traceability, not a guarantee of correctness.

## Is it for you?

CDAD fits teams and individuals who regularly delegate to AI agents, maintain
work over time, or need to explain why a change is acceptable. It is useful when
requirements, independent checks and continuity matter more than the shortest
path to a first draft.

The full cycle may be excessive for disposable experiments or small, low-risk
edits. The smaller `cdad-spec-and-test` skill provides a focused spec-and-check
workflow; choose the scope deliberately rather than scoring a project against
an arbitrary threshold. CDAD complements TDD, BDD and domain modeling rather than
replacing them.

## How the work happens

1. **Discovery:** understand the existing system, constraints and actual need.
2. **Specification:** describe the promised behavior, limits and acceptance evidence;
   obtain the required approval before implementation.
3. **Anti-gaming TDD:** inspect existing protection, write discriminating checks for
   new behavior, implement, and refactor. Select checks by the promise they protect,
   not quotas per postcondition or a coverage target.
4. **Review:** a separate reviewer challenges the result and reports prioritized
   findings; the authorized decision-maker determines their disposition.
5. **Merge and memory:** verify the required evidence, obtain approval, and preserve
   decisions, remaining risks and next steps in the project's Memory Bank.

An orchestrator coordinates; an architect investigates and specifies; a
test-writer checks; an implementer builds; a reviewer challenges; a scribe drafts
the memory update. Separate sessions and scoped context reduce shared blind
spots, but **they are not a sandbox or proof of independence**. Runtime permissions
and deployment controls still matter; ignore files are not access controls.

**You decide the objective, privacy boundaries and authority.** Agents can research,
draft, test and coordinate. Approval checkpoints remain with you unless you
explicitly delegate the applicable decisions with recorded limits. A receipt,
successful command or completed agent session never grants approval. Publication,
deployment and model changes need their own authority.

There is an operational cost: more preparation, evidence and review. Tests can miss
semantic defects, reviews can miss defects, and instructions cannot force a model
to read correctly. See the [methodology](CDAD_metodologia.md) and
[supervised-autonomy decision](docs/adr/ADR-011-autonomia-supervisada-limites-proporcionales.md).

## First steps

Start with one bounded piece of work and a person available to decide its scope.
After installation, ask your agent to **initialize this project with CDAD and run
its preliminary analysis**. It should preserve existing conventions, identify
what is missing, ask only for decisions it cannot infer, and prepare the first
useful delegation. The [guided start](skills/cdad-cycle/references/project-start.md)
owns that procedure; existing work must be resumed rather than initialized again.

### Requirements and installation

Use a local checkout of this repository, **Bash 4 or newer, Python 3**, and **Make** to generate
staging. The packet tools use Python's standard library; the installer does not
download Python dependencies. Your chosen runtime and the project's own test
environment must already be available. CDAD does not install either for you.

Run these commands **from the repository root**, after reviewing the installer:

```sh
bash install.sh --help
make staging
bash install.sh --dry-run
bash install.sh
bash install.sh --check
```

`make staging` generates the OpenCode and Claude Code agent sets (the current
Makefile includes the Odoo stack). The installer consumes `build/staging/manifest.json`,
not the role sources directly. It deploys owned copies into runtime directories
under HOME: `.config/opencode/`, `.claude/` and `.agents/skills/`; it does not install
into a public `agents/` or `skills/` directory at the install root.

To install into a separate adoption root, outside the source tree, and activate
it for OpenCode, Claude Code or Codex, follow
[project adoption](skills/cdad-cycle/references/runtime-adoption.md). Codex activation exposes skills;
it is not a claim that all runtimes have identical agent or transport support.
`CDAD_SKILL_EXTRA_DIRS` adds colon-separated skill destinations for other
environments; it does not configure their runtime integration.

**Update by regenerating staging and repeating install/check.** Valid user-owned
`model:` overlays survive updates. Other local modifications and conflicting
symlinks are preserved and reported, not silently overwritten. Exit code 1 can
mean pending conflicts, removals or drift: partial deployment is **not** a clean
success. Resolve the named items and check again. `--force` skips confirmation;
it is not an overwrite-conflicts switch. Uninstall is `bash install.sh --uninstall`
and follows recorded ownership. The [installer](install.sh) owns options and details.

### Runtime, model and delegation choices

Installing definitions is not the same as configuring delegation. External CLI
delegation uses **`runtimes.json` for execution settings** and **`delegation.json`
for model selection and the credential-file reference**. These are deployment
configuration, not choices an installer or agent should invent. The installer
preserves existing runtime configuration; deprecated model-profile options do
not select a model.

Follow the [delegation guide](skills/cdad-cycle/references/cli-delegation.md) for
configuration locations, destination adapters, execution modes, migration and
`capabilities` verification before dispatch. Use the runtime's own supported
configuration for permissions; do not copy configuration syntax between versions.

## Guided start

One brief instruction is enough to start a project from rest, up to the first
useful delegation: CDAD composes the existing primitives for you. The short
procedure is in
[project start](skills/cdad-cycle/references/project-start.md).

## Operating an adopted project

This section is for the human supervising work and the agent carrying it out.
`<skill-dir>` means the actual directory reported when `cdad-cycle` is loaded,
not an assumed machine path. Each CLI and subcommand provides `--help`.

- **Orient and continue:** start with `<skill-dir>/scripts/cdad_packet.py status`; it reports the
  situation and next operation, not authorization. `open-unit` opens eligible
  queued work; continuity checkpoints, `reconcile` and resume preserve the
  execution boundary. See [orientation](skills/cdad-cycle/references/orientation.md)
  and [continuity](skills/cdad-cycle/references/continuity.md).
- **Delegate and receive:** prepare a canonical packet and transmit its bytes
  unchanged. Routes A/C have different delivery forms; neither permits manual
  reconstruction of the packet. Receive, validate the durable receipt and
  materialize only authorized artifacts before the applicable state transition.
  Reception is mechanical, not acceptance. See
  [execution](skills/cdad-cycle/references/project-execution.md) and
  [re-entry](skills/cdad-cycle/references/re-entry.md).
- **Recover without repeating effects:** withdraw a prepared assignment that
  will not be dispatched; reconcile uncertain delivery before retrying;
  `republish-agents` refreshes derived project agents without preparing another
  packet and preserves supported model overlays. These operations are owned by
  the execution and continuity references above.
- **Choose evidence by promise:** reuse existing checks where they protect the
  obligation, explain each addition, and declare property-test budgets. Full-suite
  policy distinguishes focal work, feature closure and epic closure; CI hosting
  is not a universal installation prerequisite. See
  [TDD](skills/cdad-cycle/references/stage-3-tdd.md) and
  [closure](skills/cdad-cycle/references/stage-5-merge.md).
- **Use the right domain:** documentary engagements use evidence-backed
  [documentary contracts](skills/cdad-cycle/references/documentary-contracts.md).
  Odoo roles and skills apply when the product or actual change is Odoo-related,
  not merely because the coordinator runs in that environment. See
  [Odoo architecture](skills/odoo-architect/SKILL.md).

## Maintaining CDAD itself

This repository also contains its **own development tooling**, not a mandatory
toolchain for every adopting project. Its suite inventory and capability/surface
selection are described in [suite maintenance](docs/suite-maintenance.md);
[contract links](skills/cdad-cycle/references/contract-test-links.md) and
[suite review](skills/cdad-cycle/references/suite-review.md) distinguish structural
traceability from semantic protection. A valid inventory is not proof that every
promise is adequately tested.

The repository's [CI gate](docs/ci-gate.md) records attributable evidence.
Suite profiling, reconciliation and parallel execution have recorded results and
limits in the [performance closure](docs/epics/epic-017-suite-performance/closure.md);
those measurements are not a speed guarantee for another project or host.

## Further reading

- [Full methodology](CDAD_metodologia.md)
- [Project brief](docs/projectbrief.md), [progress](docs/progress.md) and [changelog](CHANGELOG.md)
- [Specifications](docs/specs/) and [architecture decisions](docs/adr/)
- [Study resources on NotebookLM](https://notebooklm.google.com/notebook/c4a9bab2-d26d-49bd-9ec7-50d256ed1dec)

## License

See [LICENSE](LICENSE) for the GNU General Public License, version 3.
