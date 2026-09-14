# TRANSLATION-GLOSSARY.md — ES→EN Terminology Contract

**Status:** Working artifact for the `translation-en` branch. Delete or keep at merge time.
**Purpose:** Binding terminology decisions for the Spanish→English translation of the CDAD docs. Every translator MUST apply these decisions verbatim. Consistency across files matters more than any individual preference.

## Hard rules (apply to every file)

1. **Atomic tokens:** `CDAD`, `cdad-*`, `cdad_`, `cdad_state`, `.cdad-state.json`, `cdad_model_*`, and every token derived from `cdad` are IDENTIFIERS. Translate around them, never inside them. They will be renamed (`cdad` → `coda`) in a separate mechanical commit. Example: `cdad-cycle` stays `cdad-cycle`.
2. **Do not touch:** markdown structure (headings levels, tables, lists, blockquotes), URLs, arXiv references, file paths, YAML frontmatter keys (`name:`, `mode:`, `permission:` stay verbatim), inline code, code blocks (translate ONLY Spanish comments and Spanish user-facing strings inside them).
3. **No information added or removed.** Do not "improve", summarize, or expand. Translate the same meaning with the same precision. If a passage is genuinely ambiguous, choose the most literal faithful rendering and FLAG it in your final report.
4. **Register:** professional technical English. Source uses Argentine voseo ("usá", "chequeá", "tenés") → standard English imperative ("use", "check", "you have"). Keep the direct, opinionated voice of the original — it is deliberately opinionated.
5. **Verdict values in code/tables stay SCREAMING_CASE:** `BLOQUEANTE` → `BLOCKING`, `OPCIONAL` → `OPTIONAL`, `ABSTENER` → `ABSTAIN`.

## Binding term decisions

| Spanish | English (USE THIS) | Notes |
|---|---|---|
| Anti-trampa (TDD) | Anti-gaming (TDD) | Gaming the test = aligning tests to implementation. NOT "anti-cheating". |
| Ley de Hierro (TDD) | Iron Law (TDD) | |
| brainstorm socrático | Socratic brainstorm | |
| veredicto | verdict | |
| hallazgo (de review) | finding | |
| bucket de confiabilidad | reliability bucket | |
| capas (review en dos capas) | layers (two-layer review) | Capa 1 = layer 1 (reviewer agent); Capa 2 = layer 2 (human validation) |
| validación humana | human validation | |
| aprobación humana | human approval | |
| aprobado (estado) | approved | |
| sesiones aisladas | isolated sessions | |
| sub-fase | sub-phase | |
| prueba de propiedad / property test | property test | Already anglicism in ES |
| invariantes | invariants | |
| contratos verificables | verifiable contracts | |
| postcondiciones ortogonales | orthogonal postconditions | |
| postcondiciones acopladas | coupled postconditions | |
| frameworks opinados | opinionated frameworks | |
| matriz observable de activación | observable activation matrix | |
| spec antes que código | spec before code | |
| enforzar / enforceada | enforce / enforced | Source already mixes languages |
| modalidad outside-in (E2E) | outside-in mode (E2E) | |
| modalidad cierre (E2E) | closure mode (E2E) | |
| Etapa 1..5 | Stage 1..5 | |
| Etapa 2 — Especificación | Stage 2 — Specification | |
| Etapa 3 — TDD anti-trampa | Stage 3 — Anti-gaming TDD | |
| Etapa 4 — Review en dos capas | Stage 4 — Two-layer review | |
| Etapa 5 — Merge y Memory Bank | Stage 5 — Merge and Memory Bank | |
| gate | gate | Keep |
| handoff | handoff | Keep |
| Memory Bank | Memory Bank | Keep |
| Implementer / Test-writer / Reviewer / Scribe / Refactorer / Architect / Orchestrator | Same (already English) | |
| sesión (de agente) | session | |
| redacción del spec | spec writing | |
| semilla (de ejemplo) | seed | |
| trampa (en tests) | gaming / trap | Context: "escribir la trampa" → "gaming the test" |
| tapar el sol con la mano | a token gesture / papering over the problem | Translate the MEANING, not literally |
| de oficio | by trade | |
| Vibe coding | Vibe coding | Keep |

## Source-of-truth definitions

The methodology's own glossary (§13.4 of `CDAD_metodologia.md`) defines 27 terms in Spanish. The English translations above are the canonical names for those definitions. When translating the §13.4 glossary itself, translate the definitions and keep the canonical English term as the bold headword.
