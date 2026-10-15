# Gate de spec 002 — revisión de architect-draft-002 (004-002)

Fecha: 2026-09-29. Revisor: Claude (orquestador; familia distinta del
architect). Verifiqué el HEAD inspeccionado (`1a72597`, el del despacho).

## Dictamen

```
dictamen: aprobable, con 2 condiciones que se aplican al plan sin otra ronda del architect
blocking: 0
condiciones: 2
hallazgo retroactivo: 1 (sobre la evidencia de 004-001)
```

Cierre del gate 001:
- **G1:** PD-8 fija el mecanismo (`.opencode/agents/` de proyecto + guard CC
  que carga la política) y separa derivación de activación. Lo no probado
  (guard CC en sesión real, servicio de fondo de OpenCode) queda como
  verificación exigida, no como supuesto.
- **G2:** PD-13 = 004-002 en este repo, con dos tramos a ambos lados del corte.
- **G3:** el caso legacy representativo se conserva; D2 decidió el resto.
- **O1 y O2:** incorporados (invariantes 3 y 9, PD-1, PD-6).

Las tensiones declaradas son reales y están bien resueltas. La principal, dos
ejecuciones lógicas por D2, es la consecuencia correcta de no migrar.

## Condiciones

- **C1 — T7 debe tener trabajo real concreto.** PD-13 exige que test-writer,
  implementer, reviewer y scribe trabajen por paquetes v2 después del corte.
  Si T1–T6 agotan la implementación, T7 quedaría vacía o fabricada. Condición:
  el trabajo real de T7 es **adoptar v2 en este repo**, que además cierra la
  fuga confirmada en el spike:
  1. el dueño materializa `docs/cdad-policy.json` de este repo
     (`scripts`, `agents`, `skills`, `sources`, `build`, `install.sh` como
     implementación);
  2. se generan y publican los agentes de proyecto `.opencode/agents/`;
  3. se verifica en vivo que el test-writer ya no lee `scripts/`.

  Ese recorrido cubre test-writer (aceptación), implementer (integración y
  defectos), reviewer y scribe.
- **C2 — Guard de Claude Code con Grep/Glob.** El architect observó que el
  guard deja pasar herramientas sin `file_path`. Lo confirmé en
  `scripts/claude-code-path-guard.sh:36-41`: `Grep` y `Glob` envían
  `path`/`pattern`, no `file_path`, así que hoy **no están mediadas** aunque
  el matcher `Read|Grep|Glob` las nombre. T5 debe:
  - mediar `Grep` y `Glob` por su forma real de entrada, o declararlas como
    limitación antes del despacho;
  - probarlo con la forma real de entrada, y en una sesión real (PD-8).

## Hallazgo retroactivo sobre 004-001

`tests/test_004_001_t7_capacity.py::test_pd12_cc_guard_out_of_role_blocked`
probó `Grep`/`Glob` con JSON sintético que traía `file_path`. Esa forma de
entrada no la envían las herramientas reales, así que el negativo de PD-12
para Grep/Glob en Claude Code **no demuestra la barrera**: en uso real pasa
sin bloqueo.

Disposición:
- registrarlo en el cierre de 004-001 como evidencia sobredeclarada;
- corregir la barrera y su prueba en T5 de 004-002 (C2);
- no reabrir 004-001: la garantía de lectura con `Read` sí se probó con la
  forma real.
