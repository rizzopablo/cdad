### Plan draft — `docs/specs/018-001-orchestrator-start/plan.md` (borrador)

Tareas T1–T4 con ficha completa (`validation_strategy` + bloque `plan-tasks` canónico), con `objective`, `depends_on`, `regressions`, `integration_gate`, `owner`, separadas por subfase TDD (AUDIT/RED/GREEN nunca en una misma invocación). Plan-tasks:

- T1 — Entrada y encargo coherentes (PC-1, PC-2, PC-6).
- T2 — Formatos y ayudas accionables (PC-3, PC-4).
- T3 — Recorrido ejecutable y captura fiable (PC-5, PC-7).
- T4 — Revisión, ensayo y adopción voluntaria (PC-8, PC-9).

Rutas A/C, control de retorno, reemplazo/retirada/reconciliación y excepción legítima de disposición (`register-transition --transition withdraw` vs `disposition`) se mantienen conforme al diseño aprobado.

## Bloque canonico `plan-tasks`

```plan-tasks
{
  "tasks": [
    {
      "id": "T0",
      "consume": [],
      "depends_on": [],
      "files": [
        "docs/adr/ADR-021-arranque-guiado-procedimiento-corto-por-referencia.md"
      ],
      "focal_tests": [],
      "observable_checks": [
        "commit 0c83f2dd presente en git log",
        "enmienda materializada en docs/adr/ADR-021",
        "grep \"compacta\" docs/adr/ADR-021-arranque-guiado-procedimiento-corto-por-referencia.md"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "orchestrator",
      "parallel": [],
      "produce": [
        {
          "artifact": "adr-021-amendment",
          "contract": "adr-amendment-v1"
        }
      ],
      "regressions": []
    },
    {
      "id": "T1",
      "consume": [],
      "depends_on": [
        "T0"
      ],
      "files": [
        "sources/roles/orchestrator.md",
        "sources/agents/adapters/opencode.md",
        "sources/agents/adapters/claude-code.md",
        "skills/cdad-cycle/SKILL.md",
        "skills/cdad-cycle/references/orientation.md",
        "skills/cdad-cycle/references/project-start.md",
        "skills/cdad-cycle/references/continuity.md",
        "skills/cdad-cycle/references/project-execution.md",
        "skills/cdad-cycle/references/handoff-prompts.md"
      ],
      "focal_tests": [
        "tests/test_005_006_t1_start_procedure.py",
        "tests/test_006_002_u6_context_discipline.py",
        "tests/test_006_005_u4_single_entry.py",
        "tests/test_007_001_unambiguous_entry.py"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "parallel": [],
      "produce": [
        {
          "artifact": "orchestrator-entry",
          "contract": "compact-entry-v1"
        }
      ],
      "regressions": [
        "test_005_006_t1_start_procedure.py",
        "test_006_002_u6_context_discipline.py",
        "test_006_005_u4_single_entry.py",
        "test_007_001_unambiguous_entry.py"
      ],
      "observable_checks": [
        "make agents + diff limpio para PC-8"
      ]
    },
    {
      "id": "T2",
      "consume": [
        {
          "artifact": "orchestrator-entry",
          "producer": "T1",
          "contract": "compact-entry-v1"
        }
      ],
      "depends_on": [
        "T1"
      ],
      "files": [
        "skills/cdad-cycle/scripts/cdad_packet.py",
        "skills/cdad-cycle/scripts/cdad_continuity.py"
      ],
      "focal_tests": [
        "tests/test_orchestrator_startup_usability.py"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "parallel": [],
      "produce": [
        {
          "artifact": "cli-help",
          "contract": "help-v1"
        }
      ],
      "regressions": [
        "test_003_002_t1_receive.py",
        "test_005_003_t2_examples_execute.py",
        "test_orchestrator_startup_usability.py"
      ]
    },
    {
      "id": "T3",
      "consume": [
        {
          "artifact": "orchestrator-entry",
          "producer": "T1",
          "contract": "compact-entry-v1"
        },
        {
          "artifact": "cli-help",
          "producer": "T2",
          "contract": "help-v1"
        }
      ],
      "depends_on": [
        "T1",
        "T2"
      ],
      "files": [
        "skills/cdad-cycle/assets/orientation-examples.json",
        "skills/cdad-cycle/references/orientation.md",
        "skills/cdad-cycle/references/project-start.md"
      ],
      "focal_tests": [
        "tests/test_005_003_t2_examples_execute.py",
        "tests/test_orchestrator_startup_usability.py"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "parallel": [],
      "produce": [
        {
          "artifact": "examples-connected",
          "contract": "examples-v1"
        }
      ],
      "regressions": [
        "test_005_003_t2_examples_execute.py",
        "test_orchestrator_startup_usability.py"
      ]
    },
    {
      "id": "T4",
      "consume": [
        {
          "artifact": "orchestrator-entry",
          "producer": "T1",
          "contract": "compact-entry-v1"
        },
        {
          "artifact": "cli-help",
          "producer": "T2",
          "contract": "help-v1"
        },
        {
          "artifact": "examples-connected",
          "producer": "T3",
          "contract": "examples-v1"
        }
      ],
      "depends_on": [
        "T1",
        "T2",
        "T3"
      ],
      "files": [],
      "focal_tests": [],
      "observable_checks": [
        "make validate",
        "python3 scripts/cdad-suite.py validate",
        "make agents + diff limpio",
        "ensayo en sesion nueva con entorno aislado y registro de metricas",
        "revision independiente sin hallazgos bloqueantes (gate externo, no auto-referencia)",
        "caso sintético R1-R5 con sensibilidad R3: aceptar completo, rechazar variante sin R3, oráculo intacto"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "reviewer; orchestrator; scribe",
      "parallel": [],
      "produce": [
        {
          "artifact": "review-and-trial",
          "contract": "review-v1"
        }
      ],
      "regressions": [
        "test_orchestrator_startup_usability.py"
      ]
    }
  ],
  "validation_strategy": "Documental + subprocess + regresion proporcional + make validate + cdad-suite.py validate"
}
```
