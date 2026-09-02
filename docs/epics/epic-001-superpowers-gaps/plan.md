---
epic_id: epic-001-superpowers-gaps
epic_name: superpowers-gaps
created_at: 2026-09-02
approved_by: <pendiente>
approved_at: <pendiente>
---

# Epic epic-001: superpowers-gaps

## Resumen

Cinco mejoras al framework CDAD inspiradas en obra/superpowers, con los gaps
verificados contra el código real del repo (no contra el README): protocolo
de recepción de feedback, git safety al cierre, debugging sistemático,
planning granular spec→TDD y despacho paralelo de sub-agentes. Cuando esté
done, el ciclo CDAD cubre los 5 huecos operativos identificados, sin tocar su
núcleo (etapas, gates, roles).

## Scope

**In scope:**
- Protocolo de recepción de feedback (anti-sicofantía) para todos los roles.
- Mecánica de git segura al cerrar una feature (menú fijo, base confirmada,
  descarte literal).
- Protocolo de debugging sistemático con disparador de ADR (3+ fixes).
- Metodología de planning granular (tareas, Consumes/Produces,
  anti-placeholder) para features complejas.
- Despacho paralelo de sesiones independientes del mismo rol.

**Out of scope:**
- Soporte de worktrees para el ciclo (feature aparte, si se decide).
- Cambios al núcleo de CDAD: etapas, gates, verdict-tuple, matriz de
  severidad, aislamiento por sesión (todos cubiertos y más rigurosos que
  Superpowers — verificado 02 Sep 2026).
- Skills auxiliares de Superpowers no relevantes (executing-plans,
  verification-before-completion, etc.).

## Decomposición en features

| # | Feature ID                | Descripción (1 línea)                                                                                    | Dependencias | Paralelizable |
|---|---------------------------|----------------------------------------------------------------------------------------------------------|--------------|---------------|
| 1 | cdad-005-receiving-feedback | Reference receiving-feedback.md + AP-16 + sección de loop en stage-4-review + mención en handoff-prompts | —            | Sí            |
| 2 | cdad-006-git-safety-close   | §5.4 "Cierre de branch" en stage-5-merge.md (entorno, base, menú fijo, discard literal, limpieza)        | —            | Sí            |
| 3 | cdad-007-systematic-debugging | Reference stage-debugging.md (4 fases, 3+ fixes → ADR) + regla en SKILL.md + contracto implementer    | 005 (blando) | No            |
| 4 | cdad-008-granular-planning  | Sección "Planning de features complejas" en stage-2-specification.md + extensión del rol architect      | —            | Sí            |
| 5 | cdad-009-parallel-dispatch  | Despacho paralelo en stage-3-tdd.md + semántica de sesiones/state file en sub-agent-strategies.md       | 008          | No            |

Orden de ejecución: 005 → 006 → 007 → 008 → 009 (007 usa el protocolo de
recepción de 005 en su loop de fixes; 009 usa los contratos Consumes/Produces
de 008). 005, 006 y 008 son mutuamente independientes.

## Contratos cross-feature

```markdown
1. Formato de bloque Consumes/Produces (definido por cdad-008):
   **Consumes:** <firmas exactas de contrato público, apto test-writer>
   **Produces:** <firmas exactas que las tareas siguientes asumen>
   — nota de implementación NUNCA en este bloque (aislamiento test-writer).
2. Convención AP-N (catálogo anti-patterns.md): cdad-005 agrega AP-16;
   features siguientes continúan la numeración correlativa.
3. Protocolo de recepción de feedback (cdad-005) invocado por: el loop de
   fixes de review (stage-4), el loop de debugging (cdad-007) y cualquier
   re-entry con feedback de usuario.
```

Usado por: 008 y 009 (1), 005-009 (2), 007 (3).

## Criterios de aceptación del epic

- [ ] Las 5 features están done individualmente (spec → RED → GREEN → review → merge).
- [ ] E2E cross-feature: cada nueva reference/section está enlazada desde su
      punto de entrada (SKILL.md tabla de lectura, stage-N correspondiente) y
      el repo pasa la suite bash de invariantes (121/121 + checks nuevos).
- [ ] E2E de fallo: cada reference nueva incluye su tabla
      anti-racionalización / "cuándo NO usar" (formato del repo).
- [ ] Sin regresión: los tests de cdad-003 y cdad-004 siguen verdes tras
      cada feature (suite completa al cierre de cada una).
- [ ] La numeración AP-N quedó correlativa sin duplicados (grep verificable).

## Riesgos / deuda esperada

- Riesgo: sprawl de references (SKILL.md crece y la tabla de lectura queda
  desalineada). Mitigación: cada feature actualiza la tabla de lectura del
  SKILL.md como parte de su contrato.
- Riesgo: cdad-009 (paralelismo) crece en alcance al definir ownership del
  state file. Mitigación: regla única "solo el orquestador escribe el state
  file, siempre"; si el diseño excede M, se divide la feature.
- Riesgo operativo: runtime `delegate` (roles read-only) falló 8/8 por
  timeout en la sesión del 02 Sep. Mitigación: investigar infra antes de
  arrancar 007; fallback documentado (review inline con caveat o chat nuevo).
- Deuda esperada: dogfood de `make lint` contra addon Odoo real (H3 de
  cdad-004) queda fuera de este epic.

## Stakeholders

- **Aprobador del plan del epic**: Pablo
- **Aprobador de specs de features**: Pablo
- **Operador del resultado**: cdad-orchestrator

## Cambios al plan

_(vacío — se actualiza durante el loop de features si el plan cambia)_

---

Status: Pending approval
