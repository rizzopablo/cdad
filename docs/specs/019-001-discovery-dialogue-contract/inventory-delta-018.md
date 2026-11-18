## Auditoría — delta de inventario

**No edité archivos.** La tarea pedía entregar el delta como texto. No leí `docs/specs/018-001-orchestrator-start/spec.md`; las promesas y la procedencia se derivan del módulo y sus docstrings, como indica el encargo. Por eso la confianza propuesta es `baja`.

La salida de `validate` confirma exactamente los siete faltantes del encargo: un módulo y seis nodeids.

### Entrada propuesta para `modules`

Las capacidades se asignan por nodeid para no extender una categoría a pruebas con promesas distintas. Cada asignación usa el localizador contractual indicado, sin afirmar que haya sido verificado.

```json
{
  "path": "tests/test_orchestrator_startup_usability.py",
  "kind": "test",
  "decision": "mantener",
  "confidence": "baja",
  "assignments": [
    {
      "capability": "orientation-planning",
      "contract": "docs/specs/018-001-orchestrator-start/spec.md",
      "scope": "nodeids",
      "nodeids": [
        "tests/test_orchestrator_startup_usability.py::test_pc1_pc2_pc3_pc5_coverage"
      ]
    },
    {
      "capability": "dispatch-recovery",
      "contract": "docs/specs/018-001-orchestrator-start/spec.md",
      "scope": "nodeids",
      "nodeids": [
        "tests/test_orchestrator_startup_usability.py::test_pc4_negatives_fail_with_actionable_diagnostic"
      ]
    },
    {
      "capability": "orientation-planning",
      "contract": "docs/specs/018-001-orchestrator-start/spec.md",
      "scope": "nodeids",
      "nodeids": [
        "tests/test_orchestrator_startup_usability.py::test_pc6_transmission_preserves_r3_sensitivity"
      ]
    },
    {
      "capability": "delivery-evidence",
      "contract": "docs/specs/018-001-orchestrator-start/spec.md",
      "scope": "nodeids",
      "nodeids": [
        "tests/test_orchestrator_startup_usability.py::test_pc7_evidence_capture_preserves_output"
      ]
    },
    {
      "capability": "generation-install-permissions",
      "contract": "docs/specs/018-001-orchestrator-start/spec.md",
      "scope": "nodeids",
      "nodeids": [
        "tests/test_orchestrator_startup_usability.py::test_pc8_deterministic_generation_matches_published"
      ]
    },
    {
      "capability": "delivery-evidence",
      "contract": "docs/specs/018-001-orchestrator-start/spec.md",
      "scope": "nodeids",
      "nodeids": [
        "tests/test_orchestrator_startup_usability.py::test_pc9_real_trial_delivers_comparable_record"
      ]
    }
  ],
  "helper_dependencies": [],
  "product_surfaces": [
    "docs/.cdad-state.json",
    "skills/cdad-cycle/assets/orientation-examples.json",
    "skills/cdad-cycle/references/orientation.md",
    "skills/cdad-cycle/scripts/cdad_continuity.py",
    "skills/cdad-cycle/scripts/cdad_packet.py",
    "sources/roles/orchestrator.md"
  ],
  "rationale": "Alta de inventario propuesta: el docstring declara PC-4, PC-6, PC-7, PC-8 y PC-9; los comentarios de los seis tests describen sus promesas, y el último cubre PC-1/2/3/5. Localizador contractual 018-001 citado por el encargo; no se leyó la spec, así que la clasificación deriva solo del módulo y sus docstrings.",
  "static_test_nodeids": 6,
  "targets": []
}
```

### Evidencia

Comando ejecutado:

```text
python3 scripts/cdad-suite.py validate
```

Salida: `rc=1`, con faltantes exactamente iguales al delta anterior:

```text
cdad-suite: validate: integridad insuficiente
- modulo del arbol sin inventariar: tests/test_orchestrator_startup_usability.py
- nodeid recolectado sin capacidad/contrato: tests/test_orchestrator_startup_usability.py::test_pc1_pc2_pc3_pc5_coverage
- nodeid recolectado sin capacidad/contrato: tests/test_orchestrator_startup_usability.py::test_pc4_negatives_fail_with_actionable_diagnostic
- nodeid recolectado sin capacidad/contrato: tests/test_orchestrator_startup_usability.py::test_pc6_transmission_preserves_r3_sensitivity
- nodeid recolectado sin capacidad/contrato: tests/test_orchestrator_startup_usability.py::test_pc7_evidence_capture_preserves_output
- nodeid recolectado sin capacidad/contrato: tests/test_orchestrator_startup_usability.py::test_pc8_deterministic_generation_matches_published
- nodeid recolectado sin capacidad/contrato: tests/test_orchestrator_startup_usability.py::test_pc9_real_trial_delivers_comparable_record
```

**Archivos modificados:** ninguno. **Commit:** no aplica; no hubo cambios.