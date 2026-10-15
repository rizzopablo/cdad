---
feature_id: <NNN-feature-id>
feature_name: <short name>
plan_version: <draft-NNN | approved-NNN>
approved_by: <pending>
approved_at: <pending>
---

# Feature plan: <feature name>

For a complex feature the architect drafts `plan.md` from this template, before
closing Stage 2; the plan is approved together with the spec.

## Ficha de la feature

- **Feature ID:** `<NNN-feature-id>` — a stable id plus the declared plan version.
- **Resultado observable:** <the user-visible result the feature delivers, one or two lines>.
- **Postcondiciones cubiertas:** <PD-x, PD-y, ...>.
- **Alcance incluido / excluido:** <what the plan includes, and what it explicitly excludes>.
- **Consume / Produce:** <the contracts this feature consumes and produces, each with its producer or consumer>.
- **Contexto global:** <the project-wide constraints copied verbatim from the spec header; every task includes them implicitly>.
- **Aceptación de uso:** the feature anchors the minimum acceptance-of-use recipe
  by name (contract / integration / use, each with its producer, evaluating actor
  and evidence); its detail lives with the feature's acceptance material and is
  referenced, never copied here.

## Canonical `plan-tasks` block

The per-task facts travel in exactly one canonical fenced `plan-tasks` block,
with a `validation_strategy` for the plan and a task per unit. The format —
field names, fence, semantics and the closed `detail` marker — is declared once
in `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4.1:
this template is a consumer of that declaration and never restates it. Replace
the example below with the feature's tasks; a malformed block is rejected, never
silently ignored.

```plan-tasks
{
  "validation_strategy": "suite completa una vez por quien cierra; regresiones del area tocada",
  "tasks": [
    {
      "id": "T1",
      "objective": "Publicar el contrato que la unidad siguiente consume.",
      "produce": [{"artifact": "aligned-templates", "contract": "templates-v1"}],
      "consume": [],
      "depends_on": [],
      "parallel": [],
      "files": ["<ruta/de/la/implementacion>"],
      "focal_tests": ["<tests/test_focal.py>"],
      "regressions": ["<tests/test_regresion.py>"],
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer"
    },
    {
      "id": "T2",
      "objective": "Consumir el contrato publicado por T1 y entregar su resultado observable.",
      "produce": [],
      "consume": [{"artifact": "aligned-templates", "producer": "T1", "contract": "templates-v1"}],
      "depends_on": ["T1"],
      "parallel": [],
      "files": [],
      "observable_checks": ["<el artefacto declarado existe y cumple la comprobacion X>"],
      "regressions": [],
      "integration_gate": "revision del artefacto por el evaluador",
      "owner": "test-writer"
    }
  ]
}
```

A code task declares `focal_tests`; a code-less task declares
`observable_checks` instead. Every task declares its `objective`, `depends_on`,
`regressions`, `integration_gate` and `owner`.

## Self-review before closing Stage 2

1. **Spec coverage**: every postcondition maps to at least one task, and every task maps to a postcondition.
2. **Placeholder scan**: no "TBD", "TODO", "implement later", "similar to Task N" or vagueness without a contract.
3. **Signature consistency**: the same interface keeps the same name across tasks.
