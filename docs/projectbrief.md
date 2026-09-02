# Project Brief

## Propósito del proyecto

CDAD (Contract-Driven AI Development): metodología + framework de agentes para
desarrollar software con IA bajo disciplina de contratos — spec aprobado, TDD
anti-trampa con sesiones aisladas por rol, review two-layer y Memory Bank.
Para equipos (humanos + agentes) que quieren calidad verificable, no teatro.

## Stack técnico

- **Formato**: markdown (skills + agents frontmatter opencode) + bash
- **Instalación**: `install.sh` (copia a `~/.config/opencode/` y `~/.agents/`,
  flags `--check/--force/--uninstall`)
- **Tooling de tests**: bash asserts — `tests/validate-odoo-specialization.sh`
  (cdad-003) + checks por feature en `docs/specs/<id>/VALIDATION.md`
- **Lint / type check**: para proyectos Odoo gestionados con CDAD:
  `make lint` (pre-commit-vauxoo) + `make test*` (contrato odoo-make-env)
- **CI**: pendiente (deuda registrada; suite local hace de gate, ver progress)

## Stakeholders y roles

- **Aprobador de specs / dueño**: el dueño del repo (humano, HITL)
- **Orquestador de referencia**: `cdad-orchestrator` (agente)
- **Runtimes soportados**: OpenCode (nativo, ADR-008 para Claude Code), Zed

## Restricciones conocidas

- Español rioplatense (vos) en toda la documentación.
- Los roles read-only delegan vía `delegate`; write-capable vía `task`
  (runtime OpenCode; en otros runtimes, Agent/handoff manual).
- Los modelos por rol viven en el frontmatter de `agents/*.md` (perfiles
  optimus/economical/premium via install.sh).

## Scope general

Cubre: ciclo de 5 etapas, roles especializados (+variantes Odoo), epic
coordinado, bootstrap de Memory Bank. Fuera de scope: runtimes específicos de
CI, adaptadores privados de entornos Odoo (viven en repos privados).

## Recursos externos

- Repo: https://github.com/rizzopablo/cdad
- Referencia de skills externos: obra/superpowers (comparación documentada en
  el epic superpowers-gaps)

---

Última actualización: 2026-09-02
