# Stage 1 — Discovery

Destroy the LLM's assumptions about the system before coding.

## Your role as orchestrator in this stage

YOU do not do the discovery. You coordinate:

1. Detect whether `docs/landscape.md` is missing (initial discovery) or whether the feature requires point-in-time discovery.
2. If initial discovery: the **user** does it manually (do not delegate to the architect; the user (human or higher-hierarchy autonomous agent) needs to gain first-hand knowledge in order to evaluate later). You guide it with structuring questions and assemble the document from their answers.
3. If per-feature discovery: emit the handoff packet to the **architect** (read-only) who maps the relevant APIs/hooks/modules.
4. Validate the result at re-entry.

## Mode A — Initial discovery

Applies only if `docs/landscape.md` does not exist AND it is the first feature.

### Your work

Ask the user questions (one to three per turn) so they cover:

- Central entities/models of the system.
- Hooks or extension points of the framework.
- Naming, organization, and layering conventions.
- Differences between the version in use and the documented one.
- Recommended / discouraged patterns.

Structure the answers into `docs/landscape.md` with clear sections. You deliver a draft; the user edits and confirms it.

**You do not emit a handoff to any role here.** This mode is you + user (human or agent owning the process) directly.

### Typical structure

```markdown
# Landscape — <project>

## System context
## Central entities and models
## Extension points
## Project conventions
## Differences from official documentation
## What we do NOT use
```

## Mode B — Per-feature discovery

The usual mode before each feature.

### Your work

1. Ask the user which parts of the system the feature touches (modules, models, endpoints, layers).
2. Load `references/handoff-prompts.md` section "Architect (Stage 1 — Per-feature discovery)".
3. Generate the handoff packet with:
   - The preliminary functional description (one sentence).
   - The list of relevant files the user gave you.
   - The content of `docs/landscape.md`, `docs/projectbrief.md`, `docs/systemPatterns.md`.
4. **Deliver the packet and end the turn.**

### Re-entry

When the user comes back with the architect's output, load `references/re-entry.md` section "Architect — per-feature discovery" and validate.

If it passes: the output goes to the "Technical context" section of the spec in Stage 2.

## 🛑 Exit gate (Stage 1 → Stage 2)

- [ ] If first feature: `docs/landscape.md` with real content (no placeholders).
- [ ] For this feature: the user can explain which APIs/hooks it will touch without opening the code.
- [ ] No assumptions of the form "I think X exists" remain pending.

If all OK: update the state file (`current_stage: specification`), announce the transition, and emit the handoff to the architect in brainstorm mode for Stage 2.

If something is missing: identify specifically what, and go back to the user / the architect.

## Anti-patterns

- **Jumping to the spec without discovery** → guarantee of inventions in Stage 3.
- **Exhaustive discovery** mapping the entire project (mode A for each feature) → consumes time without ROI.
- **You doing the discovery** instead of coordinating it → you lose the architect's independent oracle and, worse, the user loses the opportunity to learn first-hand.
