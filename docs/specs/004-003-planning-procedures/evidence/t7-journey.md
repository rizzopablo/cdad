# T7 — Recorrido instalado real sobre 003-002 (PD-13) — evidencia

Fecha: 2026-10-05. Orquestador: OpenCode (`cdad-orchestrator`), HITL delegada.

## 1. Promulgación (PD-12, F2 de `review-t5.md`)

Instalación en **raíz aislada** (regla del proyecto: nunca instalar CDAD en HOME
real), desde el árbol de trabajo:

```
$ make staging                                  # rc=0 (12 agentes OpenCode + 12 Claude Code)
$ CDAD_INSTALL_ROOT=<home>/.cache/cdad-004-003-root bash install.sh --force
   → rc=0; "Verify: PASS — 11 cdad agents present after install"
$ CDAD_INSTALL_ROOT=<home>/.cache/cdad-004-003-root bash install.sh --check
   → rc=0; "Check: PASS (303 artifact groups in sync with staging/skills)"
```

El producto instalado **contiene** lo construido en 004-003:

| Artefacto | Evidencia |
|---|---|
| T1 — `draft-plan` | 12 ocurrencias de `draft-plan` en el renderer instalado |
| T2 — subfase plan-review | `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` presente |
| T4 — bloque obligatorio | 14 ocurrencias de `plan-tasks` en el renderer instalado |
| T5 — equivalencia | 5 ocurrencias de la regla en `references/re-entry.md` instalado |

**F2 de review-t5 queda cerrado con evidencia de instalación aislada.** La deriva
de los mirrors de `$HOME` (F011 de `validate-subagents.sh`) es **preexistente** y
queda **fuera de alcance por regla del proyecto**.

## 2. Replan de 003-002 (consumo real del procedimiento)

El architect (`mofgw/deepseek-v4.1-flash`, sesión `<ses-26>`)
replanificó el draft del 2026-09-18 al contrato vigente, entregado como TEXTO
FINAL y materializado en `docs/specs/003-002-artifact-tools/plan.md`
(`plan-draft.md` se conserva como historia). Verificó el bloque contra el
validador real: `VALIDATOR OK: ['T1','T2','T3','T4']`, `plan-tasks token count: 1`.

**La brecha D8 que originó 004-003 queda cerrada:** el paquete v2 del **architect**
se preparó por primera vez (`contract_kind: approved-epic-plan`, paquete
`004-003-planning-procedures-architect-draft-001`, rc=0), imposible antes del
registro I2 (`cdad_packet.py:1220-1231`) y del soporte de contrato de T1.

## 3. Revisión de plan (PD-2/PD-4) — dictamen real

Paquete `004-003-planning-procedures-reviewer-plan-review-001` (contrato
`draft-plan` + `plan_version: v1-replan-2026-10-05`), preparado con **rc=0**: la
cadena T1+T2+T3+T4 validó el plan del architect de punta a punta (bloque
obligatorio, campos de validación por tarea, productor/consumidor, ciclos,
paralelismo). El render llevó la instrucción de rol **generalizada** (fix B3 de
`review-t2.md`) y el input con `purpose: "draft plan for review"` (fix F2 de
`review-t1.md`).

Reviewer: `mofgw/glm-5.3-flash`, sesión `<ses-27>`,
read-only, independiente del autor.

**Dictamen técnico (revisar ≠ aprobar):** el replan alcanza su intención y la capa
estructural pasa el validador; **no debe pasar a ejecución** hasta resolver F1 y
F2. 2 BLOCKING, 4 opcionales, 4 abstenciones.

- **F1 (BLOCKING, m):** el bloque `plan-tasks` de T4 omitía
  `skills/cdad-cycle/scripts/cdad_packet.py`, que la ficha sí declara → divergencia
  ficha↔bloque (rompe la declaración única, PD-12) y ruta ambigua entre los dos
  `cdad_packet.py` del repo.
- **F2 (BLOCKING, m):** T4 modifica `install.sh` sin declarar las regresiones que lo
  ejercitan (`tests/test_install_ownership.py`, `tests/test_install_review5_regressions.py`).
- **F3 (OPTIONAL, l):** T2 y T3 comparten `cdad_result.py` y ambos dependen solo de
  T1, sin protocolo de serialización declarado.
- **F4 (OPTIONAL, l):** wording "referencia pequeña en state" contradice la
  restricción de ownership; el draft original decía "payload fuera del state".
- **F5 (OPTIONAL, l):** `Modify .gitignore` de T1 es probablemente no-op (`.cdad/`
  ya está ignorado).
- **F6 (OPTIONAL, l):** la incertidumbre VERIFY de T4 sobre la ruta del state schema
  es resoluble hoy (existe `state-template.json`; el validador es el canónico).

## 4. Cambios aplicados (conservar lo válido, corregir solo lo invalidado)

Decisión del orquestador (HITL delegada), proporcional: se aplican **F1 y F2** (los
dos bloqueantes, mecánicos y verificados) al plan materializado; F3–F6 quedan
**abiertos para el dueño de 003-002** (epic-003, suspendido) por ser de precisión,
no defectos observables:

- F1: `files` de T4 en el bloque += `skills/cdad-cycle/scripts/cdad_packet.py`; la
  ficha desambigua el canónico vs. el wrapper.
- F2: `regressions` de T4 += `tests/test_install_ownership.py`,
  `tests/test_install_review5_regressions.py`.

## 5. Alcance respetado

**003-002 NO se reimplementó**: no se escribió código de `cdad_result.py` ni de
ninguna tarea de 003-002; el plan sigue `status: draft`, **no aprobado**. La
aprobación del plan de 003-002 pertenece a su propio ciclo (epic-003, suspendido) y
no se ejerce acá.
