# Epic-level anti-patterns

Specific to epic coordination. They are additive to the feature anti-patterns (`cdad-cycle/references/anti-patterns.md`); the AP-N ones keep applying within each feature.

## EAP-1 — Kilometer-long plan that never closes

**Symptom**: epic planning takes more than 90 minutes. The plan exceeds 5 pages. Sections like "Appendix A", "Annex of considerations" appear.

**Why it's bad**: the light plan becomes a heavy plan. Most of the extra content is speculation about the how (which is each feature's work) or about hypothetical risks.

**Correction**: you cut where you are. What's missing stays as TBD to be decided when the corresponding feature starts. The plan is updated on the fly.

> *"<X minutes> in. The plan already has the essentials. What comes next looks like more detail on the how of each feature, which is cdad-cycle's work, not the epic plan's. Shall we close planning and start the first feature?"*

## EAP-2 — Mini-specs inside the plan

**Symptom**: each feature in the plan's decomposition has its own 1-page block with technical details, postconditions, acceptance criteria.

**Why it's bad**: it duplicates the work of the real spec (which is done in `cdad-cycle` when the feature starts). The mini-spec inside the plan ages badly: when the feature starts, the real spec may diverge, and the plan's mini-spec remains as noise.

**Correction**: in the plan, one line per feature. Enough to understand what it does and why it is in the epic. The spec is done when the feature is executed.

## EAP-3 — Speculative ADRs at the start of the epic

**Symptom**: the plan includes a section "Architectural decisions" with several hypothetical ADRs: "We are going to use PostgreSQL", "We are going to split into bounded contexts", etc., **before** any feature has started.

**Why it's bad**: ADRs are immutable. If you create them speculatively and later the reality of the features tells you otherwise, you have to create an ADR-NNN-Supersede that replaces the original one. That is noise.

**Correction**: ADRs emerge when the decision is real. If in E1 (discovery) it is crystal clear that "we are going to use PostgreSQL" and that affects several features, it is worth creating ONE epic ADR. But don't fill the plan with 5 speculative ADRs. When in doubt, **defer**: the ADR when the feature needs it.

## EAP-4 — Skipping cross-feature integration

**Symptom**: the individual features passed their E2Es. The user wants to go straight to closure. *"They're all green already, what else?"*

**Why it's bad**: individual tests do not cover the cross-feature flow. Cross-feature bugs only appear in integration.

**Correction**: identify the plan's cross-feature acceptance criteria and require an E2E for each one. If your argument is "there's no time left", require at least ONE: the epic's main flow.

## EAP-5 — Sub-epics appearing unrequested (epic creep)

**Symptom**: during the epic, "a related functionality" appears that was not in the plan, and it sneaks into the current epic instead of remaining as a separate epic or a later standalone feature.

**Why it's bad**: the epic's scope grows without control. The epic never closes because "there's always something else left".

**Correction**: if the new functionality is NOT in the plan's original scope, it stays out of the epic. Options:

- Create a standalone feature to do it after the current epic.
- Create a next epic with that functionality as its base.
- If it is genuinely urgent and blocks the current epic: update the plan with user re-approval, adding the functionality as an explicit feature.

Do NOT sneak it in silently. It is the main cause of epics taking twice as long as planned.

## EAP-6 — Epic tracking only in one's head

**Symptom**: the state file is not updated. `epic_features` is left with stale data. `progress.md` does not reflect the real state.

**Why it's bad**: when you come back to the epic after a few days, you don't remember where you were. Time is lost rediscovering.

**Correction**: every feature closure updates the state. Every plan change updates the state. The update is the epic coordinator's responsibility; you, as the skill, do it when appropriate.

## EAP-7 — Broken coordination with `cdad-cycle`

**Symptom**: the user is in `cdad-cycle` working on a feature of the epic and never comes back to `cdad-epic` to coordinate the next one. Features get completed but the epic stays in `features-loop` indefinitely.

**Why it's bad**: coordination is lost. The next feature might have dependencies that the plan accounts for but the user forgot.

**Correction**: in the feature handoff (when you delegate to `cdad-cycle`), remind the user to come back to `cdad-epic` when the feature closes. In `cdad-cycle`, feature closure should suggest going back to the epic coordinator if the feature belongs to one.

(Note: this requires a minor change in `cdad-cycle`; see `references/coordination-with-cdad-cycle.md` or equivalent.)

## EAP-8 — Ritualistic closure

**Symptom**: epic closure ends up being "mark everything done and merge", without a retrospective or reflection on what was learned.

**Why it's bad**: it loses the value of closure. The brief retrospective (3 points of "what worked", 3 of "what got complicated", 3 of "lessons learned") is what makes the next epic better.

**Correction**: insist on the brief retrospective. It is not ritualism; it is ROI on the invested work. If genuinely there is nothing to retrospect on, mark it: *"No relevant findings for the retrospective."*

---

## How to use this file

Load it when you detect signals. Cite the code (`EAP-N`) in your message to the user:

> *"We are in EAP-1: the plan is growing beyond light. Shall we close what we have and start features?"*

Do not load it preventively.
