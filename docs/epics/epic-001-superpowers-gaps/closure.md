# Epic epic-001-superpowers-gaps — Closure

**Cerrado**: 2026-09-02 (formalizado retroactivamente el mismo día, durante
epic-002-cdad-audit-fixes — ver nota abajo)
**Duración**: 2026-09-02 → 2026-09-02 (mismo día; 5 features consecutivas)

## Resumen

Cinco mejoras al framework CDAD inspiradas en obra/superpowers: protocolo de
recepción de feedback anti-sicofantía, git safety al cierre de branch,
debugging sistemático, planning granular spec→TDD, y despacho paralelo de
sub-agentes. El ciclo CDAD cubre los 5 huecos operativos identificados sin
tocar su núcleo (etapas, gates, roles).

**Nota sobre esta closure**: el epic tenía `plan.md` aprobado y las 5
features `done` en `progress.md`, pero nunca se ejecutó formalmente la Etapa
E4 (Closure) de `cdad-epic` — el state file quedó en `idle` sin
`epic_stage`/`epic_features`/`epic_history`, y no existía este archivo. La
auditoría de consistencia de `epic-002-cdad-audit-fixes` (finding M9,
corregido: la afirmación original de que `docs/epics/` estaba vacío era
incorrecta — el `plan.md` sí existía y estaba aprobado) detectó el gap real:
faltaba el cierre formal. Se completa acá, escrito con el mismo criterio que
se le pediría a cualquier closure — sin inventar retrospectiva que no está
respaldada por los artefactos reales del repo.

## Features entregadas

| ID | Nombre | Cerrada |
|----|--------|---------|
| cdad-005-receiving-feedback | Protocolo anti-sicofantía (AP-16) | 2026-09-02 |
| cdad-006-git-safety-close | §5.6 cierre de branch (menú fijo, discard literal, AP-17) | 2026-09-02 |
| cdad-007-systematic-debugging | stage-debugging.md (loop rojo, 3+ fixes → ADR, AP-18) | 2026-09-02 |
| cdad-008-granular-planning | Planning de features complejas (Consumes/Produces, AP-19) | 2026-09-02 |
| cdad-009-parallel-dispatch | Despacho paralelo de sesiones independientes | 2026-09-02 |

## Criterios de aceptación

- [x] Las 5 features están done individualmente (spec → RED → GREEN → review → merge) — verificado en `docs/progress.md`.
- [x] E2E cross-feature: cada reference nueva enlazada desde su punto de entrada — verificado en `SKILL.md` "Cómo leer las references" (con los gaps que `epic-002-cdad-audit-fixes` 002-004/002-005 corrigió: `verdict-tuple.md` y `claude-code-delegation.md` faltaban en la tabla).
- [x] Sin regresión: `tests/validate-odoo-specialization.sh` en verde tras cada feature (evidencia en los commits de cada `docs(review):`).
- [x] Numeración AP-N correlativa sin duplicados — verificado (AP-16 a AP-19, sin huecos).
- [ ] Cierre formal de Etapa E4 (`closure.md` + campos de epic en el state file) — **no se hizo en su momento**; se completa recién acá.

## Retrospectiva breve

### Lo que funcionó bien
- Las 5 features se ejecutaron en una sola sesión continua con disciplina RED→GREEN→review por feature, sin atajos documentados.
- La convención `Consumes/Produces` de cdad-008 se reusó correctamente en cdad-009 (dependencia declarada en el plan, cumplida).

### Lo que se complicó
- El cierre formal del epic (Etapa E4 de `cdad-epic`) no se ejecutó — el ciclo pasó de "última feature done" directo a "siguiente epic" sin pasar por el coordinador de epic. Es exactamente el gap que este mismo archivo corrige.
- El state file no llevaba los campos `epic_stage`/`epic_features`/`epic_history` en su momento (el schema de `cdad-epic` los define, pero `assets/state-template.json` — la fuente única desde `epic-002-cdad-audit-fixes` 002-002 — no los tenía integrados con el de `cdad-cycle` hasta ese fix).

### Aprendizajes para futuros epics
- Cerrar la Etapa E4 explícitamente, aunque el epic se sienta "obviamente terminado" — es la misma tentación de saltar un gate que el resto de la metodología ya nombra (AP-5 con otro disfraz).
- El schema de state file necesita ser una sola fuente compartida entre `cdad-cycle` y `cdad-epic` desde el bootstrap del proyecto, no algo que se reconcilia después.

## Deuda técnica que se llevó

- CI del repo (GitHub Actions) — deuda de bootstrap, ya registrada en `progress.md` desde antes de este epic, sin cambios.
- Dogfood pendiente (ya registrado en `progress.md`): `make lint` contra addon Odoo real, §5.6 con worktree real, `receiving-feedback` con bloqueantes reales, `stage-debugging` con bug real, despacho paralelo con 2+ dominios disjuntos.

## Decisiones arquitectónicas tomadas

Sin ADRs nuevos durante este epic (las 5 features fueron extensiones documentales al skill `cdad-cycle`, no decisiones arquitectónicas de infraestructura).

## Notas finales

Este closure se escribió como parte de `epic-002-cdad-audit-fixes` (feature
002-012), con delegación HITL explícita de Pablo para todo el epic-002
(spec approval, priorización, Memory Bank) — ver `docs/.cdad-state.json`
campo `hitl_delegation`. La escritura retroactiva de un closure no es el
patrón recomendado (Gate E4 debería cerrarse en su momento); se documenta
así para que quede trazable que fue un cierre tardío, no una omisión sin
registro.
