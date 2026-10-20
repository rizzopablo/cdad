# Stage 5 — Merge and Memory Bank

Full CI + Memory Bank update with the Scribe pattern.

## Your role as orchestrator

You do NOT update the Memory Bank on your own. You coordinate:

1. Verify full CI (you run it if you have bash, or ask the user for the output).
2. Emit handoff to the **scribe** with spec + diff + review + current Memory Bank.
3. Validate the drafts at re-entry.
4. Pass the drafts to the **user** for APPROVAL (non-delegable); you commit them after the approval.
5. Feature closure when CI is green + Memory Bank committed.

## 5.1 — CI verification

**Not optional.**

Mandatory checks:

- Full linter over the modified files.
- Type checker (mypy / tsc / etc.).
- Import-linter or equivalent.
- Full suite: unit + integration + contract + property.
- Project-specific checks.

The complete suite belongs to **closure** (evidence policy owner:
`stage-3-tdd.md` §"Test evidence policy"); the project declares the exact command.

If you have bash: run the suite. If not: ask the user for the output.

> *"Run the full suite (`<the project's command>`). I need to see: linter, type checker, import-linter, all the tests. If anything fails, we go back to Stage 3."*

If CI fails: activate `stage-debugging` (`references/stage-debugging.md`) with the failure output — without a verified root cause there is no fix. With the diagnosis and the red loop, go back to Stage 3. No exceptions.

## 5.2 — Handoff to the Scribe

Load `references/handoff-prompts.md` section "Scribe (Stage 5)".

Generate the packet with:

- Approved spec (`docs/specs/<feat>/spec.md`).
- Full diff of the PR.
- Reviewer's report (`docs/specs/<feat>/review.md`).
- Current Memory Bank (`projectbrief`, `activeContext`, `progress`, `systemPatterns`, `adr/`).

Deliver the packet, end the turn.

### Re-entry

Load `re-entry.md` section "Scribe". Validate that the three drafts are present (activeContext entry, progress changes, ADR draft or "no ADR").

## 5.3 — User validation (non-delegable)

Pass the drafts to the user for approval:

> *"The scribe is done. Three drafts:*
>
> *1. activeContext.md entry: <paste>*
> *2. progress.md changes: <paste>*
> *3. ADR: <paste | "no ADR suggested", confidence <X>>*
>
> *Edit whatever the scribe got wrong. When you're satisfied, approve; the orchestrator commits with the `docs(memory):` prefix. Let me know when it's done."*

**The approval belongs to the user (non-delegable); the git execution belongs to the
orchestrator.** If the user approves the drafts, you commit them with `git add
docs/**` + `git commit` (prefix `docs(memory):`).

## 5.4 — Decision on the ADR

If the scribe proposed an ADR:

- **High confidence**: it probably deserves an ADR. Pass it to the user so they can expand it.
- **Medium confidence**: ask the user whether the decision warrants an ADR.
- **Low confidence**: discard by default, unless the user sees value in it.

General heuristic: could someone in 6 months ask "why did we do X this way"? If yes → ADR. If no → discard.

**Upkeep of the decisions table.** When an ADR is approved, the orchestrator adds
its row to the "Current decisions" section of the project's `docs/systemPatterns.md`
(file, state `vigente`, a one-line summary, the roles that must consume it and the
reference where its rule lives) and commits it with the `docs(memory):` prefix.
When the new ADR replaces a previous one, the orchestrator marks the previous row
as obsolete — it keeps the row, with the replacement named in it — so the history
stays in the table. The exit gate of this stage does not change: the upkeep is a
step of the decision, not a new checkbox of the gate.

## 5.5 — Merge

Once CI is green + Memory Bank committed (+ ADR if applicable):

Merge to main. Strategy (squash, merge, rebase) per the project's convention, not the skill's.

## 5.6 — Branch closure (git safety)

**Inherited precondition**: suite already green (§5.1) and Memory Bank closed (§5.2-5.3). They are not re-verified here; this section covers what happens with the branch and the worktree once the work is finished and approved.

### Step 1 — Detect the environment

Before touching anything, determine what type of repo you are in:

```bash
git rev-parse --git-dir
git rev-parse --git-common-dir
git rev-parse --show-superproject-working-tree
```

- If `--git-dir` and `--git-common-dir` match → normal repo.
- If `--git-common-dir` points elsewhere → linked worktree.
- Submodule guard: if `--show-superproject-working-tree` returns a path → you are inside a submodule; the real repo is the superproject (a normal repo for closure purposes).

| Detected environment | What applies |
|---|---|
| Normal repo | Full menu, including local merge. |
| Linked worktree with its own branch | Full menu. |
| Detached HEAD | Menu without local merge (push + PR, keep or discard). |

### Step 2 — Confirm the base branch

If the base is not recorded in the spec nor in the state file, **confirm with the user**: *"This branch came off `<best candidate>` — correct?"*. **Never** assume it or infer it silently: a merge onto the wrong base is expensive to revert.

### Step 3 — Fixed closure menu

> *"Implementation complete. What do we do?"*
>
> 1. **Local merge** to `<base>`
> 2. **Push** and create a **PR**
> 3. **Keep**: leave the branch as is
> 4. **Discard**: throw the work away

The user chooses; the orchestrator executes (§5.3). Never choose by default.

**Execution per option:**

1. **Local merge**: run the merge and re-verify the suite over the merged result (the gate validates the tree being merged, not the tree as it was when you ran the suite an hour ago). If conflicts appeared: **STOP** — list the affected files, without auto-resolving anything, and bring the decision to the user. If the merge fails, the branch and the worktree stay in place.
2. **Push + PR**: the worktree stays alive to iterate on the PR feedback.
3. **Keep**: report where the branch and the worktree ended up.
4. **Discard**: ONLY on the user's explicit request. Show what gets deleted (branch, list of commits, worktree) and wait for the user to type the literal word `discard` — *"yes, delete it"* is not enough. Only then: `git branch -D` + cleanup.

### Cleanup by provenance

Only clean the worktrees the cycle itself created (`.worktrees/` / `worktrees/`). A worktree foreign to the cycle stays intact.

```bash
git worktree remove <path>   # from the repo root
git worktree prune
```

If the removal is rejected (uncommitted files): show the output of `git status --porcelain` and ask the user. **No `--force` on your own initiative** — the rejection means there are files that exist only there.

### ⚠️ Critical order

**Merge first → worktree after → branch last.** Deleting the branch while a live worktree still references it fails; and removing the worktree before confirming the merge destroys work if the merge fails.

### Anti-rationalization

| Rationalization | Correction |
|---|---|
| "We already ran the suite a while ago" | The gate validates the tree being merged: re-run over the merge result. |
| "It's obvious he wants to merge" | The decision is the user's (§5.3). Present the menu. |
| "'Yes, delete it' is enough as confirmation" | Only the literal word `discard` authorizes destruction. |
| "I'll clean that other old worktree while I'm at it" | Provenance: only the ones this cycle created. |
| "The worktree remove rejection is a technicality, I'll use --force" | The rejection means files that exist only there; forcing destroys them. |
| "The merge failed but it's flaky, I'll retry" | A red merged result halts everything; the branch and worktree stay while it's investigated. |
| "I'll detect the base with git and be done" | A merge onto the wrong base is expensive to revert; confirm with the user. |

### When it does not apply

- **Projects with squash or rebase-merge by convention**: the integration command changes, not the user's decision nor the menu.
- **Repos without a feature branch** (committing directly to main — common in solo projects or monorepos): the menu reduces to push/PR, and the section applies only to the non-destructive parts.

## 🛑 Exit gate (Stage 5 → done)

- [ ] **If CI is configured:** full CI green (linter, type checker,
      import-linter, unit, integration, contract, property).
- [ ] **If NO CI is configured** (new project, first feature): the local green
      suite equals the gate, and the absence of CI is recorded as explicit
      debt in `docs/progress.md` — never silently. It does not block
      the closure of the first feature while waiting for a CI that bootstrap already noted as
      pending (`references/bootstrap.md` Step 2, question 4).
- [ ] `docs/activeContext.md` with a new entry.
- [ ] `docs/progress.md` moved the feature to "done".
- [ ] If an architectural decision → new ADR in `docs/adr/`.
- [ ] Commit with the `docs(memory):` prefix — approved by the user, executed by the orchestrator.
- [ ] Feature merged.

When all OK: update state (`current_stage: done`, `active_feature: null`).

**If the feature belongs to an epic** (`active_epic` not null in the state file), close like this:

> *"Feature `<X>` closed. Memory Bank updated. The feature belongs to epic `<epic-id>`. I recommend going back to `cdad-epic` (in a new chat) to coordinate the next feature of the epic. Or would you rather start a standalone feature outside the epic here?"*

**If the feature does NOT belong to an epic** (standalone case), close like this:

> *"Feature `<X>` closed. Memory Bank updated. Next feature, or are we done for today?"*

If next feature → back to Stage 1.

## Anti-patterns

- **AP-7**: outdated Memory Bank. Block the closure.
- **AP-8**: speculative or missing ADRs.
- **AP-9**: CI skipped.
- **AP-10**: delegating the Memory Bank APPROVAL to the LLM. The commit execution is the orchestrator's; the decision to approve is the user's (non-delegable).
