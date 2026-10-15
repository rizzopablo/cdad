---
feature_id: 003-007-living-continuity
feature_name: Continuidad que tolera documentos vivos
created_at: 2026-10-08
status: approved
approved_by: orchestrator (HITL delegation epic-003)
approved_at: 2026-10-08
---

# Plan — 003-007-living-continuity (borrador, ronda 2)

> Borrador del architect derivado de `architect-draft-001.md` aplicando
> `review-draft-001.md` con la disposición `review-draft-001-decision.md`
> (BL-1, BL-2, BL-3; R-1, R-2, R-3, R-4; R-5 rechazado; abstención de
> `reconcile` aceptada). 4 tareas (máximo del encargo). La **última** tarea
> concentra los cambios de `sources/roles/orchestrator.md` (clases del wiring
> BL-1 + texto D9/R-4) y regenera agentes (`make agents`). El plan define el
> contrato, nunca el código. Gate de tests vigente (2026-10-08): el implementer
> corre **focales + tests de los módulos tocados**; suite completa al cierre o si
> toca instalador/staging/renderer. Focales nombrados por tarea.

## Restricciones globales (copia de la spec)

- Repo en español. Tooling Python **stdlib-only**.
- Nunca instalar/modificar CDAD en el HOME real; raíces aisladas bajo `~/.cache`.
- Sin push automático. Ledger y docs nuevos **sin rutas absolutas** (marcadores
  `<adopted-root>`/`<project-root>`).
- No endurecer permisos; sin CLI nuevo; reutilizar `cdad_continuity.py`.
- No tocar `docs/cdad-policy.json` (esquema estricto, `cdad_packet.py:404-415`).
- Instalación aislada con el perfil del proyecto: `CDAD_INSTALL_ROOT=… bash install.sh --optimus`
  (R-5 rechazado).

## 1. Tareas

### T1 — Clases de referencia (contrato/vivo) + proyección de autoridad + compatibilidad
- **Postcondiciones:** P1, P2, P3, P4, P7, P8.
- **Alcance incluido:** `--update.references[]` acepta string u objeto
  (`class`, `fields`); modo `fields` para JSON con **fallo cerrado al escribir**
  si el archivo no es JSON o si la proyección resuelve vacía (BL-3); el digest de
  `contract` bloquea y el de `living` informa (`state`/`current_sha256` en el
  sobre de `resume`/`reconcile`/`trigger`); clase resuelta congelada en el body;
  **legado por comparación** (D6/R-1): igual → verificado `contract`, distinto →
  `changed` con `legacy: true` sin bloquear; filtro de rol intacto. `continuity.md`
  documenta la forma, la convención de clases y **un ejemplo que declara clases**
  (BL-1).
- **Excluido:** T4-CKPT (T2); defaults por policy (deuda).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Modify `skills/cdad-cycle/assets/continuity-checkpoint.schema.json`;
  Modify `skills/cdad-cycle/references/continuity.md`;
  Create `tests/test_003_007_t1_reference_classes.py`.
- **Focales:** `tests/test_003_007_t1_reference_classes.py`,
  `tests/test_003_004_t1_resume.py`, `tests/test_003_004_t1_checkpoint.py`,
  `tests/test_003_004_t4_real_context.py`.
- **Validación (fixtures autocontenidos, R-3):** `contract` cambiada → `rc≠0`;
  `living` cambiada → `rc 0` con `state: changed`; cambio de `stage_history` no
  bloquea y de `hitl_delegation` bloquea; `fields` sobre no-JSON → `rc≠0`;
  `fields` con proyección vacía → `rc≠0`; `resume --role test-writer` sin
  implementación. **P7 se prueba con copias de los stores en tmp**; el render
  sobre los stores reales queda como observable de T3.
- **Detener si:** V2 (canonicalización de `fields`) no se fija sin ambigüedad.
- **Owner:** RED test-writer; GREEN implementer.

### T2 — T4-CKPT: `checkpoint` distinto de `begin`
- **Postcondiciones:** P5, P6.
- **Alcance incluido:** `record` en el body de checkpoint (begin byte-idéntico);
  `checkpoint` con la clave del head apendea eslabón (`seq+1`, `prev`); `begin`
  divergente con la misma clave sigue cerrado; `record` en el sobre;
  `_detect_split_brain` redefinido (**≥2 bodies con `record != "checkpoint"` por
  clave**, p. ej. huérfanos pre-RU-2). **Se declara explícitamente la
  modificación de la faceta `checkpoint` de
  `tests/test_003_006_t4_ru2_refused_write.py`** (BL-2): el test-writer la
  reespecifica en el RED de T2 con trazabilidad a P5; la faceta `begin`
  divergente y el all-or-nothing RU-2 quedan **intactos** y siguen siendo el
  corazón del test. Incluir en el RED el escenario de la abstención aceptada:
  `reconcile` de un paquete **cuya clave ya no es el head** tras un append.
  Actualizar `continuity.md` (detección vigente + límite de orfans).
- **Excluido:** detección de forks de checkpoint mismo-key (deuda).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Modify `skills/cdad-cycle/assets/continuity-checkpoint.schema.json`;
  Modify `skills/cdad-cycle/references/continuity.md`;
  Modify `tests/test_003_006_t4_ru2_refused_write.py` (sólo faceta `checkpoint`);
  Create `tests/test_003_007_t2_checkpoint_vs_begin.py`.
- **Dependencias:** T1 (mismo archivo; evita conflicto).
- **Focales:** `tests/test_003_007_t2_checkpoint_vs_begin.py`,
  `tests/test_003_006_t4_ru2_refused_write.py`,
  `tests/test_003_004_t2_writeahead.py`.
- **Validación:** checkpoint mismo-key → `seq+1` con `prev` correcto; begin
  divergente mismo-key → `rc≠0`; checkpoint idéntico re-ejecutado → no-op;
  split-brain para dos begins; `reconcile` con clave no-head consistente.
- **Owner:** RED test-writer; GREEN implementer.

### T3 — Aceptación: rotación real dentro de 003-007
- **Postcondición:** P9.
- **Alcance incluido:** instalar la versión nueva en una raíz aislada
  (`CDAD_INSTALL_ROOT=… bash install.sh --optimus`, bajo `~/.cache`) e invocarla
  por ruta explícita, **sin reactivar** el repo (D7); tras el último checkpoint
  de un paquete, escribir en un documento vivo (ledger/deuda) → `resume`
  **rinde** y reporta los vivos cambiados; verificar el bloqueo de una referencia
  `contract` (spec aprobada) sin editar la spec del repo (proyecto sintético en
  T1 y/o copia controlada). **Verificar el render sobre los stores reales** de
  `exec-003-004-context-continuity-001` y `exec-003-006-runtime-adoption-001`
  (R-3). Registrar en el ledger.
- **Excluido:** editar la spec aprobada; benchmark.
- **Archivos:** Create `docs/specs/003-007-living-continuity/continuity-ledger.md`;
  Modify `docs/specs/003-007-living-continuity/dispatch-ledger.md`.
- **Registro obligatorio:** `situación | evidencia (file:line) | decisión |
  autoridad vigente | presupuesto (intentos/contexto o null) | falsas alarmas |
  retrabajo | pendiente`, con rutas en marcadores.
- **Observable:** `resume` sobre la ejecución real de 003-007 rinde y lista los
  vivos `changed`; `resume` sobre las dos ejecuciones existentes rinde y reporta
  los legados divergidos; bloqueo `contract` reproducido (copia); sin
  reactivación.
- **Dependencias:** T1, T2 verdes.
- **Owner:** orquestador.

### T4 — Regla de encargo reconciliada + declaración de clases del wiring (última, separada)
- **Postcondición:** P10.
- **Alcance incluido (BL-1 + R-4):**
  (a) reemplazar el paréntesis "one postcondition, one test, one diff; do not
  group sub-phases" de `sources/roles/orchestrator.md:69-72` por el texto de D9,
  que incluye el ejemplo: *una tarea del plan cuyos RED y GREEN son despachos
  separados satisface la regla*;
  (b) en el bloque "Continuity wiring" (`orchestrator.md:77-82`) declarar
  explícitamente qué se registra `living` (ledgers, `debt.md`, Memory Bank,
  borradores de cierre/enmienda) y qué `contract` (spec/plan aprobados,
  `docs/cdad-policy.json`, state con `fields` de autoridad), o un puntero
  estricto a la sección de `continuity.md`;
  (c) regenerar `agents/` (`make agents`).
- **Excluido:** cualquier cambio de código del CLI.
- **Archivos:** Modify `sources/roles/orchestrator.md`;
  Regenerate `agents/cdad-orchestrator.md`,
  `agents/claude-code/cdad-orchestrator.md` (`make agents`);
  Create `tests/test_003_007_t4_atomic_unit_rule.py`.
- **Focales:** `tests/test_003_007_t4_atomic_unit_rule.py`,
  `tests/test_003_006_t3_receive_wiring.py`.
- **Regresión / gate:** `tests/validate-consistency.sh`; **suite completa** (toca
  staging/renderer vía `make agents`).
- **Validación:** el agente regenerado expresa la unidad despachable, la
  trazabilidad test↔postcondición, el diff acotado, el ejemplo RED/GREEN y la
  declaración de clases del wiring; `make agents` determinista (sin diff
  inesperado).
- **Nota:** T4 es funcionalmente independiente de T1–T3 y se secuencia última
  (mismo archivo de rol que nada más toca; regenera agentes).
- **Owner:** RED test-writer; GREEN implementer.

## 2. Cobertura spec↔plan

P1,P2,P3,P4,P7,P8→T1; P5,P6→T2; P9→T3; P10→T4. Ninguna P sin tarea; ninguna
tarea sin P.

## 3. Estimaciones (rango, método, incertidumbre)

- Rango: **medio** (T1), **bajo–medio** (T2), **bajo** (T3), **bajo–medio** (T4).
  Método: comparación cualitativa con 003-004. Incertidumbre **media** por V2
  (canonicalización de `fields`) y V5 (headroom 16 KiB, no medido por la review:
  queda para el RED).

## 4. Integración final

1. Suite completa del repo + validadores (sin regresiones; F011 y A3 deuda
   preexistente declarada).
2. Rotación real registrada en `continuity-ledger.md`, con render sobre las dos
   ejecuciones reales.
3. Spec y plan revisados juntos por sesión independiente antes de aprobar.

## 5. Incertidumbres / replanificación

- Si V2 no se resuelve, reacotar el shape de `fields` antes de RED.
- Si el render legado revela una deriva de spec no prevista, escalar al
  orquestador (no reinterpretar el puente D6/R-1).

```plan-tasks
{
  "validation_strategy": "focales por unidad (pytest, env -u TMPDIR) con proyectos y stores copiados a tmp (fixtures autocontenidos); módulos tocados (test_003_004_*, test_003_006_t4_*) en cada tarea; suite completa y validadores al cierre y en T4 (make agents toca staging/renderer); aceptación real en raíz aislada invocada por ruta explícita, sin reactivar el repo ni editar la spec aprobada; render sobre los stores reales como observable de T3; ledger anonimizado",
  "tasks": [
    {"id": "T1", "produce": [{"artifact": "cdad-continuity-reference-classes", "contract": "continuity-checkpoint-v1"}], "consume": [], "depends_on": [], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "skills/cdad-cycle/assets/continuity-checkpoint.schema.json", "skills/cdad-cycle/references/continuity.md", "tests/test_003_007_t1_reference_classes.py"], "focal_tests": ["tests/test_003_007_t1_reference_classes.py", "tests/test_003_004_t1_resume.py", "tests/test_003_004_t1_checkpoint.py", "tests/test_003_004_t4_real_context.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T2", "produce": [{"artifact": "cdad-continuity-checkpoint-record", "contract": "continuity-checkpoint-v1"}], "consume": [{"artifact": "cdad-continuity-reference-classes", "contract": "continuity-checkpoint-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "skills/cdad-cycle/assets/continuity-checkpoint.schema.json", "skills/cdad-cycle/references/continuity.md", "tests/test_003_006_t4_ru2_refused_write.py", "tests/test_003_007_t2_checkpoint_vs_begin.py"], "focal_tests": ["tests/test_003_007_t2_checkpoint_vs_begin.py", "tests/test_003_006_t4_ru2_refused_write.py", "tests/test_003_004_t2_writeahead.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T3", "produce": [{"artifact": "continuity-ledger-003-007", "contract": "n/a"}], "consume": [{"artifact": "cdad-continuity-reference-classes", "contract": "continuity-checkpoint-v1", "producer": "T1"}, {"artifact": "cdad-continuity-checkpoint-record", "contract": "continuity-checkpoint-v1", "producer": "T2"}], "depends_on": ["T1", "T2"], "parallel": [], "files": ["docs/specs/003-007-living-continuity/continuity-ledger.md", "docs/specs/003-007-living-continuity/dispatch-ledger.md"], "observable_checks": ["una rotacion real dentro de 003-007 con escrituras de ledger posteriores al ultimo checkpoint: resume rinde y reporta los documentos vivos cambiados", "una edicion deliberada de la spec aprobada (contrato) bloquea, verificado sin editar la spec del repo", "la version nueva se invoca por ruta explicita desde una raiz aislada bajo ~/.cache sin reactivar el repo", "resume sobre exec-003-004-context-continuity-001 y exec-003-006-runtime-adoption-001 rinde proyeccion y reporta los legados divergidos"], "regressions": ["tests/validate-consistency.sh", "tests/validate-odoo-specialization.sh"], "integration_gate": "@validation_strategy", "owner": "orquestador"},
    {"id": "T4", "produce": [{"artifact": "regla-encargo-atomico-y-clases-wiring", "contract": "n/a (reglas operativas)"}, {"artifact": "agentes-regenerados", "contract": "n/a (salidas generadas)"}], "consume": [], "depends_on": ["T3"], "parallel": [], "files": ["sources/roles/orchestrator.md", "agents/cdad-orchestrator.md", "agents/claude-code/cdad-orchestrator.md", "tests/test_003_007_t4_atomic_unit_rule.py"], "focal_tests": ["tests/test_003_007_t4_atomic_unit_rule.py", "tests/test_003_006_t3_receive_wiring.py"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"}
  ]
}
```

---

Status: approved (orquestador bajo delegación HITL de epic-003, 2026-10-08).
