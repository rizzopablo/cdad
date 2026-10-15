# Project Brief

## Propósito del proyecto

CDAD (Contract-Driven AI Development): metodología + framework de agentes para
desarrollar software con IA bajo disciplina de contratos — spec aprobado, TDD
anti-trampa con sesiones aisladas por rol, review two-layer y Memory Bank.
Para equipos (humanos + agentes) que quieren calidad verificable, no teatro.

## Stack técnico

- **Formato**: markdown (skills + agents frontmatter opencode) + bash + Python 3 (stdlib).
- **CLI canónicos del ciclo** (familia `skills/cdad-cycle/scripts/`, con wrapper fino en
  `scripts/`): paquetes/estado (`cdad_packet.py`), recepción/materialización/evidencia
  (`cdad_result.py`), continuidad (`cdad_continuity.py`), guards (`cdad_guard.py`),
  medición de contexto (`cdad_context_meter.py`), versión (`cdad-version-check.py`);
  generador/activación en `scripts/` (`cdad-generate.py`, `cdad-activate.py`).
- **Instalación**: `install.sh` (copia a `~/.config/opencode/` y `~/.agents/`,
  flags `--check/--force/--uninstall`); agentes generados desde `sources/` a staging
  (nunca editados a mano) e instalados solo desde staging.
- **Tooling de tests**: suite **pytest** (Python) por feature (`tests/test_<feature>_t*.py`,
  RED/GREEN por tarea) + validadores **bash** de consistencia (`tests/validate-*.sh`,
  `make validate`); checks por feature en `docs/specs/<id>/VALIDATION.md`.
- **Lint / type check**: para proyectos Odoo gestionados con CDAD:
  `make lint` (pre-commit-vauxoo) + `make test*` (contrato odoo-make-env).
- **CI**: pendiente (deuda registrada; la suite local hace de gate, ver progress).

## Stakeholders y roles

- **Aprobador de specs / dueño**: el dueño del repo (humano, HITL).
- **Orquestador de referencia**: `cdad-orchestrator` (agente); en epic-005 la HITL está
  delegada al orquestador OpenCode (`docs/epics/epic-005-real-operation/execution.md`).
- **Runtimes soportados**: OpenCode (nativo, ADR-008 para Claude Code), Zed.

## Restricciones conocidas

- Español rioplatense (vos) en toda la documentación.
- En OpenCode: TODOS los roles cdad son task-ables y se delegan vía `task`
  (palanca `write: ask`, cdad-010/ADR-009; el canal `delegate` está muerto en
  deploys con default global sin crédito). En otros runtimes, Agent/handoff
  manual.
- Los modelos por rol viven en el frontmatter de `agents/*.md` (perfiles
  optimus/economical/premium via install.sh).

## Scope general

Cubre: ciclo de 5 etapas, roles especializados (+variantes Odoo), epic
coordinado, bootstrap de Memory Bank, ejecución por proyecto v2 (política
única + agentes derivados + guard), continuidad, medición de contexto y
orientación acotada del orquestador. Fuera de scope: runtimes específicos de
CI, adaptadores privados de entornos Odoo (viven en repos privados).

## Recursos externos

- Repo: https://github.com/rizzopablo/cdad
- Referencia de skills externos: obra/superpowers (comparación documentada en
  el epic superpowers-gaps)

---

Última actualización: 2026-10-12
