# Bootstrap — Initializing a new project in CDAD

When the project has no Memory Bank and no `docs/specs/`, the user is starting from scratch. This is the first time CDAD is applied to this project.

## Your goal

Leave the project ready for the **first feature** to enter Stage 1 (Discovery) without friction. This means:

1. The `docs/` structure created with templates filled in.
2. State file initialized.
3. Operational decisions made (which framework, which tooling, what counts as "green").

## Steps

### Step 1: confirm the user wants to bootstrap

Before creating files, ask:

> *"I didn't detect a Memory Bank in this project. Is this the first time you're applying CDAD here? If so, I offer to create the `docs/` structure with initial templates — you will have to fill in some parts yourself (the ones requiring project knowledge I don't have). Shall we proceed?"*

If they say no, ask whether the Memory Bank is in another location.

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

`docs/.cdad-state.json.stack` is the generic field that activates specialized
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

Copy the templates from `assets/memory-bank-templates/` to the project's `docs/`. Fill in what you know, and leave clear `<TODO: ...>` placeholders for what the user must complete.

Structure to create:

```
docs/
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

Initial content:

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

> *"Done. Memory Bank created in `docs/`, state file initialized. What's left for **you** to complete:*
>
> *- `docs/projectbrief.md`: the sections marked TODO.*
> *- `docs/systemPatterns.md`: the technical conventions you already have (layers, naming, framework patterns).*
>
> *When you're ready, tell me what the first feature is and we start with Stage 1 (Discovery)."*

## About `landscape.md`

`docs/landscape.md` is the document of **initial system discovery** — what the AI agent learns about the APIs, hooks, and conventions of the framework it is going to work with. It is NOT created in bootstrap; it is created in the first Stage 1 when the user starts the first feature, because only then is it known which parts of the system are worth mapping.

If the user insists on doing it in bootstrap, that's fine — explain that it will remain a static input of the project and that it gets updated at every Stage 1 when new things are discovered.

## Anti-patterns to avoid in bootstrap

- **Do not create specs in bootstrap.** Specs are per feature; in bootstrap there is no active feature yet.
- **Do not create empty ADRs.** ADRs document decisions made; they are not pre-filled speculatively. The `adr/` folder is created; concrete ADRs arise when there are real architectural decisions.
- **Do not promise CDAD will be instant.** Bootstrap takes an honest 30-60 minutes, mainly to complete `projectbrief.md` and `systemPatterns.md`. If the user expects 5 minutes, they are underestimating the initial cost — and that cost is what pays for the later performance.

## After bootstrap

Load `references/stage-1-discovery.md` and start the first feature.
