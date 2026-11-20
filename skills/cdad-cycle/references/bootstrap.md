# Bootstrap — Initializing a new project in CDAD

Bootstrap applies only when the layout query reports a genuinely new project. This is the first time CDAD is applied to this project.

## Your goal

Leave the project ready for the **first feature** to enter Stage 1 (Discovery) without friction. This means:

1. The methodology directory created with templates filled in (`cdad/` for a new project; see the layout step).
2. State file initialized.
3. Operational decisions made (which framework, which tooling, what counts as "green").

## Steps

### Step 0: resolve the layout first

Run the read-only query from the product root (`<product-root>`, not the session directory), before asking anything or creating files:

```bash
python3 <skill-dir>/scripts/cdad_packet.py layout --project-root <product-root>
```

- `source: registered` → use its `methodology_dir`. Never overwrite the locator and never fall back to `docs/`. This is not a bootstrap; continue with the existing layout.
- `source: legacy` → the project is not new: do not bootstrap, and do not move or rewrite it.
- Uninitialized → genuinely new, if Step 1 confirms it. Only then run `layout --project-root <product-root> --for-bootstrap`, which proposes `cdad/`.
- Any other failure → stop and report the CLI's diagnostic to the user. Do not bootstrap over it and do not pick a directory.

The query creates nothing; `layout --help` states its exact contract.

### Step 1: confirm the user wants to bootstrap

Before creating files, ask:

> *"I didn't detect CDAD in this project. Is this the first time you're applying CDAD here? If so, I offer to create the methodology directory (`cdad/`) with initial templates — you will have to fill in some parts yourself (the ones requiring project knowledge I don't have). Shall we proceed?"*

Also ask whether CDAD already exists elsewhere in the repository. These are two separate conditions, and the bootstrap proposal stands only when **both** are explicitly confirmed:

1. It is confirmed that this is the **first** application of CDAD to this project (the user answers yes to the first question).
2. It is confirmed that CDAD **does not exist elsewhere** in the repository (the user answers no to the second question).

Stop, without creating anything, when either condition is not confirmed: silence, doubt or "I don't know" on either one, a negative answer to the first question, or an affirmative answer to the second one (CDAD exists elsewhere, or there was a previous installation). Then ask where the existing Memory Bank is, rather than creating a second one.

### Step 2: collect project context

Ask these questions (one per turn, or grouped if the user is expeditive):

1. **Project name and purpose** — for `projectbrief.md`.
2. **Main language and framework** — for `systemPatterns.md`. See Step 2b
   (below) for `stack` detection — do not rely on this question alone: in
   unattended bootstrap (no human present) nobody answers it.
3. **Are there existing tests? With which tool?** (pytest, jest, rspec, etc.).
4. **Is CI configured?** If not, mention it as debt to be addressed soon.
5. **Who approves specs?** Usually the user, but confirm it to register the name in the state.

Do not make a long questionnaire. Three or four concrete questions and get going.

### Step 2b: `stack` detection (automatic, non-blocking)

`<methodology_dir>/.cdad-state.json` (the `stack` field; `docs/` only for a legacy project) is the generic field that activates specialized
role variants (`cdad-<role>-<stack>`) — see `cdad-cycle` §3.1. **CDAD knows
no stack by name**: detection lives in each specialization skill, not here.
This is what lets Django, Rails, Odoo, or any other future specialization
join without touching the core.

Convention: a specialization for `<stack>` is distributed as a skill
`<stack>-architect`, and **that same skill declares how to detect itself** — typically
a short section like "Automatic detection" with objective repo markers (a
characteristic file, a dependency, etc.).

Procedure:

1. List the installed skills that follow the `*-architect` pattern (with a dash,
   distinct from `cdad-architect`).
2. For each candidate, load its automatic-detection section (if it has one)
   and evaluate it against the repo.
3. **A single candidate with clear, objective evidence** → set
   `stack: <name>` in the state file, **without asking**. It is automatic on
   purpose: in unattended bootstrap there is nobody to ask.
4. **Ambiguity (zero or more than one candidate)** → if a user is present,
   ask them; if not, leave `stack` absent (generic agents) and record it in
   `activeContext.md` as something to confirm when a human returns.

You don't need to know in advance which stacks exist: it is self-discovery
over whatever is installed.

### Step 3: create the structure

Copy the templates from `assets/memory-bank-templates/` to the methodology directory: `cdad/` for a new project, or the registered `methodology_dir` when a locator exists. Fill in what you know, and leave clear `<TODO: ...>` placeholders for what the user must complete. Never overwrite existing metadata, documentation or plans.

For a new project, record the placement before anything else is created: write `cdad/project-layout.json` (the fixed declaration path) with exactly this closed schema, under this bootstrap's authorization only (no other role may edit it):

```json
{
  "schema_version": 2,
  "methodology_dir": "cdad",
  "operational_dir": ".cdad-execution"
}
```

Then re-run `layout --project-root <product-root>` and confirm `source: registered`. Classify the methodology directory as documentation in the proposed policy, keeping applicable end-user documentation paths as they are. `validate-policy` reports whether the effective policy accepts that placement; an incompatibility blocks operational use until the owner authorizes a policy reconciliation. Bootstrap does not change the policy to make it pass.

Structure to create (the tree is rooted at the methodology directory):

```
cdad/                     (<methodology_dir>; `docs/` only for a legacy project)
├── projectbrief.md       (from assets/memory-bank-templates/projectbrief.md)
├── systemPatterns.md     (from assets/memory-bank-templates/systemPatterns.md)
├── activeContext.md      (from assets/memory-bank-templates/activeContext.md)
├── progress.md           (from assets/memory-bank-templates/progress.md)
├── adr/
│   └── README.md         (brief guide on how to create ADRs)
├── specs/
│   └── README.md         (brief guide on spec structure)
└── .cdad-state.json      (from assets/state-template.json)
```

You create `landscape.md` in the first Stage 1, not here.

### Step 4: initialize state file

Create `<methodology_dir>/.cdad-state.json`. Initial content:

```json
{
  "version": 1,
  "active_feature": null,
  "current_stage": "discovery",
  "stage_history": [],
  "tdd_substage": null,
  "postconditions_status": {},
  "approver": "<the name the user told you>",
  "last_updated": "<ISO timestamp>"
}
```

### Step 5: offer the next step

After creating the structure, communicate:

> *"Done. Memory Bank created in `cdad/` (the methodology directory), state file initialized. What's left for **you** to complete:*
>
> *- `cdad/projectbrief.md`: the sections marked TODO.*
> *- `cdad/systemPatterns.md`: the technical conventions you already have (layers, naming, framework patterns).*
>
> *When you're ready, tell me what the first feature is and we start with Stage 1 (Discovery)."*

## About `landscape.md`

`docs/landscape.md` is the document of **initial system discovery** — what the AI agent learns about the APIs, hooks, and conventions of the framework it is going to work with. It is NOT created in bootstrap; it is created in the first Stage 1 when the user starts the first feature, because only then is it known which parts of the system are worth mapping.

If the user insists on doing it in bootstrap, that's fine — explain that it will remain a static input of the project and that it gets updated at every Stage 1 when new things are discovered.

## Anti-patterns to avoid in bootstrap

- **Do not create specs in bootstrap.** Specs are per feature; in bootstrap there is no active feature yet.
- **Do not create empty ADRs.** ADRs document decisions made; they are not pre-filled speculatively. The `adr/` folder is created; concrete ADRs arise when there are real architectural decisions.
- **Do not bootstrap over a legacy marker, an ambiguous layout or an existing locator.** Report the layout diagnostic instead; never migrate or repoint.
- **Do not promise CDAD will be instant.** Bootstrap takes an honest 30-60 minutes, mainly to complete `projectbrief.md` and `systemPatterns.md`. If the user expects 5 minutes, they are underestimating the initial cost — and that cost is what pays for the later performance.

## After bootstrap

Load `references/stage-1-discovery.md` and start the first feature.
