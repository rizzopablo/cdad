# Cierre e integración — epic-004-single-source-planning

Fecha: 2026-10-05. Orquestador: OpenCode (`cdad-orchestrator`), HITL delegada por el
dueño. Autorización explícita: «completar la integración y cerrar epic-004 si la
evidencia satisface sus criterios, con las excepciones justificadas expresamente
registradas».

Este documento cierra el epic. **No cierra epic-003** (regla explícita de
`plan.md:339-340`): sus features 003-002/003/004 siguen pendientes de su propia
evidencia.

---

## 1. Estado de los tres ciclos

| Ciclo | Estado | Cierre | Evidencia de cierre |
|---|---|---|---|
| 004-001-canonical-runtime-artifacts | **cerrado** (2026-09-29) | `specs/004-001-canonical-runtime-artifacts/closure.md` | 7 criterios verificados; suite 132 passed; 3 validadores PASS |
| 004-002-project-execution-bootstrap | **cerrado** (2026-10-03) | `stage_history.closure`; `cut-c.md`, `t7-live-walk.md`, `review-second-look.md` | 8 criterios; suite de cierre 329 passed en worktree fijado `5b14f0e`; ADR-012 |
| 004-003-planning-procedures | **cerrado** (2026-10-05) | `specs/004-003-planning-procedures/closure.md` | 8 criterios (AC-7 eximido por decisión del dueño); suite 364 passed en `287f6c7` |

Los tres ciclos están aprobados y cerrados. **Esta integración no reabre ninguno.**

---

## 2. Recorrido consumidor (`plan.md:308-325`) — verificación de los 8 pasos

Regla aplicada: **reutilizar la evidencia válida de las tres features y ejecutar
solo lo que faltaba o había quedado invalidado**. No se repitieron las suites
completas de las tres features.

| # | Paso | Productor → Consumidor | Evidencia | Ejecutado ahora |
|---|---|---|---|---|
| 1 | Fuentes y configuración de runtime | Repo canónico + config explícita → **Generador**, con validación de combinaciones | 004-001: matriz `4 perfiles × 2 runtimes × 11 agentes = 88 celdas` (`test_004_001_acceptance_matrix.py`); PD-4/PD-5 outputs declarados | **Sí**: `make staging` + `make agents` sobre `8cb6580` → **0 diferencias** (determinismo = fuentes sin edición manual competidora) |
| 2 | Agentes/skills derivados | Generador → **Instalador**, con propiedad/destinos y check | 004-001: ownership manifest, `install.sh --check`; PD-18 (nunca lee `sources/`) | **Sí**: instalación del commit adoptado en raíz aislada, `Verify: PASS — 11 cdad agents`, `--check PASS (303 grupos)` |
| 3 | Política del proyecto | Bootstrap propone; responsable resuelve → **Preparación y adaptadores** | 004-002 T1/T5: `docs/cdad-policy.json`, clasificador I1, guard CC que carga la política al ejecutarse; ADR-012 | Reutilizada (misma política, sha `9ffb7d16…`); `validate-policy` incluido en el smoke |
| 4 | Identidad y autoridad de ejecución | Bootstrap → **State/prepare** | 004-002 T2: contexto v2, I2 (autoridad verificable), I8 (`--record-dispatch`), `--new-execution` | Reutilizada; el smoke usó el contexto v2 real |
| 5 | Objetivo y plan | Usuario/discovery + architect → **Reviewer de plan en otra sesión** | 004-003 T7: replan de 003-002 por architect (deepseek) + plan-review por reviewer (GLM) en sesión independiente; `evidence/t7-journey.md` | Reutilizada |
| 6 | Contrato aprobado para construir | Responsable autorizado tras resolver hallazgos → **Prepare y rol** | 004-002 I2 (prepare exige spec aprobada); 004-003: el plan revisado **siguió en `draft`** (revisar ≠ aprobar) | Reutilizada |
| 7 | REQUEST/PACKET | Prepare extendido → **Agente instalado**, inputs y scopes comprobados | 004-003 T7: agente real consumió un paquete real (`architect-draft-001`, `reviewer-plan-review-001`); `plan-tasks` validado por el validador real | **Sí**: smoke con el **CLI INSTALADO** del root adoptado → `prepare` rc=0, paquete `…-reviewer-plan-review-003` publicado, agentes derivados de proyecto publicados con `source_dir` = el root adoptado |
| 8 | Resultado del rol | Canal real del runtime → **Coordinador conserva original** | T7 y todo el ciclo 004-003: el orquestador conservó los artefactos y materializó los de solo-lectura (ADR-003) | Reutilizada. La **recepción automatizada** pertenece a **003-002** (`plan.md:319`) y no se implementó acá |

**Conclusión del recorrido:** los 8 pasos tienen productor, consumidor y evidencia.
El paso 7 era el único sin ejecución desde el **producto instalado**; queda cubierto
por el smoke de abajo.

### 2.1 Smoke mecánico del producto instalado (etiquetado: resultado sintético)

`plan.md:322-323` autoriza smokes mecánicos con resultados sintéticos, etiquetados
como tales. Se ejecutó uno, en un worktree desechable:

```
worktree desechable en HEAD (8cb6580) + copia de .cdad/ (contexto v2 real)
state sintético: 004-003 vuelto a in-progress, current_stage=smoke-installed-cli
CLI = <home>/.cache/cdad-adopted-8cb6580/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py
CDAD_OPENCODE_AGENTS_DIR = <root adoptado>/.config/opencode/agents
→ prepare --role reviewer --substage plan-review --contract-kind draft-plan \
     --contract-path docs/specs/003-002-artifact-tools/plan.md
   rc=0 · paquete …-reviewer-plan-review-003 publicado
   .opencode/agents/ publicado con source_dir = <root adoptado>
```

El CLI instalado es **byte-idéntico** al del árbol de trabajo
(sha256 `c75ccc646be1b2c728663adefe486433a35d94ff547e9c668c925b70aea83ba4` en
ambos), por lo que el paquete que consumió el agente real en T7 y el que produce el
producto instalado son el mismo artefacto para la misma entrada.

**Etiqueta explícita:** el smoke usa un estado sintético (feature reabierta solo en
el worktree desechable). No sustituye al recorrido real de T7: lo complementa en el
único punto que faltaba (procedencia instalada del render).

---

## 3. Criterios de cierre del epic (`plan.md:329-336`)

| Criterio | Estado | Evidencia |
|---|---|---|
| Ciclos aprobados/cerrados | ✅ | §1 |
| Fuentes sin edición manual competidora | ✅ | `make staging`+`make agents` → 0 diffs sobre `8cb6580`; outputs declarados (PD-4/PD-5); PD-18: el instalador lee solo staging |
| Ambos runtimes con compatibilidad y límites documentados | ✅ | ADR-008 (**Verified**); `skills/cdad-cycle/references/project-execution.md` §7 (mecanismos y límites declarados por runtime); agentes CC + guard instalados en el root adoptado |
| Proyecto consumidor funcionando | ✅ | El propio repo dogfoodea: 004-001→004-003 construidas con el producto; T7 (recorrido real) + smoke del paso 7 |
| Plan real revisado | ✅ | T7: plan de 003-002 revisado por sesión independiente, con dictamen y cambios concretos |
| Handoff a 003 actualizado | ✅ | `epic-003-context-efficiency/handoff-resume-2026-10-05.md` (nuevo) + `handoff.md` |
| Suite de base y los tres validadores, en raíces aisladas | ✅ con excepción | Suite 364 passed (`287f6c7`, worktree fijado); validadores: consistency 141 PASS / **2 FAIL preexistentes**, odoo-specialization FAIL esperado (RED de otra feature), subagents FAIL por drift de mirrors `$HOME` → **excepción registrada en §5** |
| Gate de CI resuelto explícitamente | ✅ (resuelto como inexistente) | **No hay CI configurado.** Se declara explícitamente: la evidencia es local y **no se declara CI verde**. Sigue como deuda priorizada con dueño (§5) |

---

## 4. Las tres distinciones exigidas

### 4.1 Producto comprobado en instalación aislada

- **Versión adoptada:** commit `8cb6580dbc8f3ab2936447151c75cf7a284e1591`
  (004-003 cerrada), perfil `optimus`, stack `odoo`, runtimes OpenCode + Claude Code.
- **Raíz aislada:** `<home>/.cache/cdad-adopted-8cb6580`
  (`install.sh --force` rc=0 → `Verify: PASS — 11 cdad agents`;
  `install.sh --check` rc=0 → `Check: PASS (303 artifact groups in sync with staging/skills)`).
- Contiene los tres ciclos: skills `cdad-{cycle,epic,spec-and-test}` + `odoo-*`,
  11 agentes por runtime, guard CC (`path-guard.sh`), CLI del renderer.
- Registro operativo: `docs/runtime-adopted-version.md`.

### 4.2 Instalaciones personales desactualizadas (fuera de alcance por regla del proyecto)

- `~/.config/opencode/{skills,agents}`, `~/.claude/{skills,agents,cdad-scripts}`,
  `~/.agents/skills`.
- **Están desactualizadas**: los agentes del HOME **difieren** de los del repo
  (verificado archivo por archivo) y la skill `cdad-cycle` instalada carece de todo
  el contenido de 004-002/004-003 (`sha256` distinto del repo).
- **No se tocan**: el proyecto prohíbe modificar instalaciones globales en HOME
  (regla vigente desde 004-001 y reforzada en 004-002/004-003). Su deriva es la
  causa del FAIL `F011-A` de `validate-subagents.sh`, preexistente a 004-003.
- **Consecuencia operativa:** por eso la versión operativa se adopta en **ámbito de
  proyecto** (§ `docs/runtime-adopted-version.md`), con precedencia sobre el global.

### 4.3 Limitaciones funcionales aceptadas y pendientes

Declaradas, no ocultas. Ninguna se convierte en verde:

1. **PD-5/PD-6 (equivalencia y re-entry) sin enforcement ejecutable** — disciplina
   del orquestador verificada por revisión, no un mecanismo (004-003 `closure.md`).
2. **OpenCode: los mapas `write`/`edit` de los agentes derivados no se aplican en
   vivo** (W-3, `t7-live-walk.md`): son intención documentada, no garantía. La única
   barrera verificada en vivo es `read`.
3. **OpenCode: `grep`/`glob` se median por el patrón de búsqueda, no por ruta**
   (W-2). Por eso los derivados no emiten entradas de path para esas herramientas.
4. **Claude Code: `Grep`/`Glob` no quedan mediados** en uso real (hallazgo posterior
   al cierre de 004-001; corregido y probado en 004-002 T5, C2). `Read` sí.
5. **Sin CI de repositorio** — la evidencia es local (§3).
6. **T6/F4 de 004-003 condicional**: scopes co-ubicados no ejercitables en este
   repo (`test_roots:["tests"]`); deuda para el primer consumidor Go.
7. **Recepción automatizada de resultados**: pendiente por diseño, es 003-002.

---

## 5. Excepciones registradas expresamente (autorizadas por el dueño)

| # | Excepción | Justificación | Dueño / siguiente acción |
|---|---|---|---|
| E1 | `AC-7` de 004-003 (validadores en verde) eximido | `make validate` = 141 PASS / 2 FAIL **preexistentes** y no implicados por el diff: `F011-A` drift de mirrors `$HOME` (irresoluble por la regla de no tocar HOME) y `F011-B` A3 sobre `tests/test_role_packets.py` | Deuda priorizada: acotar el patrón A3 a palabra completa, excluir `__pycache__`, y decidir la política de mirrors |
| E2 | Validadores del epic: `consistency` 2 FAIL, `odoo-specialization` FAIL, `subagents` FAIL | Los tres preexisten al epic o son el estado RED esperado de otra feature (odoo); ninguno es causado por 004-001/002/003 | Igual que E1 |
| E3 | Gate de CI | No existe CI en el repositorio; se resuelve declarándolo explícitamente | Deuda: GitHub Actions (backlog de bootstrap) |
| E4 | Paso 8 del recorrido (recepción) | Pertenece a 003-002 por diseño (`plan.md:319`) | 003-002 |

---

## 6. Garantías de 003-001/003-005 preservadas

`plan.md:338-340` exige conservar las garantías ya aprobadas de 001/005 de epic-003
y no cerrar 003 junto con 004.

- 003-001 (role-packets) y 003-005 (claude-code-packets) siguen **cerradas** y no se
  reabren; sus contratos son la base de 004 y ninguna de las tres features de 004 los
  sustituyó: 004-001 derivó de las fuentes canónicas, 004-002 añadió política/bootstrap
  y 004-003 añadió el contrato de plan borrador (ADR-013) — **aditivo**, sin retirar
  garantías de 001/005.
- `make agents` determinista sobre las fuentes canónicas vigentes confirma que la
  cadena de derivación de 001 sigue intacta.
- **epic-003 no se cierra acá.**

---

## 7. Entrega a epic-003

Handoff: [`../epic-003-context-efficiency/handoff-resume-2026-10-05.md`](../epic-003-context-efficiency/handoff-resume-2026-10-05.md).

Incluye: estado reconciliado (no restauración ciega del snapshot), autoridad HITL
re-registrada por el dueño, versión operativa adoptada, lo que cambió en 004 y afecta
a 003, el plan de 003-002 revisado y sus pendientes, y la siguiente acción.

---

## 8. Veredicto

**El epic cumple sus criterios de cierre con las excepciones E1–E4 registradas.**
La integración se verificó reutilizando la evidencia válida de los tres ciclos y
ejecutando únicamente lo que faltaba: el determinismo de las fuentes y el smoke del
paso 7 desde el producto instalado.

**Status: cerrado (2026-10-05), con excepciones expresas.**
