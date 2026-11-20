## Borrador de enmienda — no aprobado

La decisión directa de <owner> autoriza esta excepción para 019-001; no modifica la metodología general ni el TDD de 019-002 (`execution.md:16–28`). Propongo únicamente estos tres reemplazos en `docs/specs/019-001-discovery-dialogue-contract/spec.md`.

### 1. Reemplazar el contenido de “Documentary product and protected inputs” (`46–54`)

```markdown
**Proposed documentary product scope:**

`docs/specs/019-001-discovery-dialogue-contract/operating-design/`

The directory contains the operating design and its worked examples. It is separate from this specification, discovery, approved epic sources, the protected review checklist and other acceptance inputs.

Before any product is produced, the orchestrator materializes the independent reviewer’s contract-derived checklist outside the product directory as a protected acceptance input. Independent review reports are also materialized outside that directory. The producer never edits the checklist, admitted sources or acceptance contract. A necessary checklist correction returns to the independent reviewer; a contract change requires the applicable explicit approval.

This declaration grants no write permission in the current architect session.
```

### 2. Reemplazar PC-12 (`189`)

```markdown
**PC-12.** Verification of 019-001 is independent semantic review against the approved contract. The reviewer uses a protected checklist derived from PC-1 through PC-12 and the admitted sources, fixed before any product is produced and never edited by the producer. Closure evidence identifies the checklist version used and records, for every PC, the verification result, cited evidence with recoverable locators and examined versions, and any findings, missing evidence, limitations or abstentions. Missing evidence or a failed postcondition cannot establish acceptance.
```

### 3. Reemplazar el último párrafo de “Acceptance criteria” (`260`)

```markdown
For this purely documentary unit, independent semantic review IS the verification; no automated test, structural-interface verifier, RED/GREEN phase or test-writer participation is required. Before any product is produced, the independent reviewer derives the checklist from this approved contract’s PC-1 through PC-12 and its admitted sources, not from the produced design. The orchestrator materializes it as a protected acceptance input outside the product directory; the producer never edits it. The reviewer applies that fixed checklist and returns a per-PC result with cited product and source evidence, examined versions, findings and verification limits. Acceptance requires evidence satisfying every committed postcondition, no blocking contradiction or missing evidence, and explicit approval by the authorized approver. This verification establishes documentary fidelity, consistency and an actionable activation contract, not deployment or observed agent compliance. PC-11 and all acceptance obligations assigned to 019-002 remain unchanged.
```

**Criterio:** conservar la revisión independiente y la protección del criterio de aceptación, eliminando solamente el mecanismo automatizado que la decisión del propietario descarta. No introduce gates, roles ni campos. PC-11, los criterios numerados de aceptación y el handoff a 019-002 quedan intactos.

## Evidencia de ejecución

- **Ruta C validada:** contexto v2; identificación coincidente; `PACKET.md` completo idéntico byte a byte al render canónico.
- **Revisión examinada:** `444a65eabb3be4079b324b32ec2f926013e6675c`.
- **Fuentes:** contrato aprobado; `spec.md`; `execution.md:16–28`; `verification-blocker.md`; referencias canónicas de diseño y contratos documentales.
- **Archivos modificados por esta sesión:** ninguno.
- **Commit creado:** ninguno.
- **Pruebas:** no ejecutadas; esta tarea entrega exclusivamente texto propuesto.

Comandos principales ejecutados desde `<repo>`:

```bash
python3 ~/.agents/skills/cdad-cycle/scripts/cdad_packet.py validate-request --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-006/REQUEST.json
python3 ~/.agents/skills/cdad-cycle/scripts/cdad_packet.py validate-packet --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-006/REQUEST.json --packet .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-006/PACKET.md
python3 ~/.agents/skills/cdad-cycle/scripts/cdad_packet.py render --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-006/REQUEST.json --route C
git status --short
git diff --exit-code -- docs/specs/019-001-discovery-dialogue-contract/spec.md
git rev-parse HEAD
```

Validadores: salida 0. Comparación completa mediante Python: `PASS`. Diff de la especificación: vacío. El estado inicial y final conserva únicamente los cambios preexistentes en `docs/.cdad-state.json` y `docs/epics/epic-019-discovery-dialogue/amend2-begin.json`.