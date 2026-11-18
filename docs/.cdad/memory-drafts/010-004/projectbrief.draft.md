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

## Despacho de encargos y frontera con la instalación

- **El paquete es un artefacto publicado, no un mensaje.** Un encargo CDAD se
  prepara con `cdad_packet.py prepare` y queda en `.cdad/packets/<packet_id>/`
  (`REQUEST.json` + `PACKET.md` canónico). El rol lo admite por una de dos rutas
  exclusivas: **ruta A** (paquete inline completo, comparado byte a byte contra el
  render) o **ruta C** (bloque de identificación + lectura del paquete publicado).
- **Ruta C es la vía de despacho sin retranscribir el cuerpo.** `render --route C`
  emite solo la declaración y un bloque JSON con `project_root`, `packet_id`,
  `execution_id`, `execution_context`, `request`, `packet` y `contract`; no reproduce
  instrucciones, objetivo, entradas, scopes ni cuerpo. Exige el request **publicado**
  en su ubicación canónica, contexto v2 canónico y el `PACKET.md` completo verificado
  contra el render antes de emitir. No modifica archivos ni estado. Base: `010-004`
  (`docs/specs/010-004-packet-dispatch-ergonomics/spec.md` §4.2, PC-01/PC-02).
- **El contexto de ejecución se declara, no se infiere.** Toda publicación nueva
  declara `execution_context` con la forma exacta
  `.cdad/executions/<execution_id>/execution.json` en `REQUEST.json` y en la cabecera
  de `PACKET.md`; toda preparación nueva —ordinaria, sucesora o de recuperación que
  publique generación nueva— usa ejecución **v2**, incluso al continuar un proyecto
  viejo. Los requests históricos v1 se reconocen, validan y reemiten por sus vías
  explícitas; ninguno de esos usos habilita preparación nueva v1.
- **Frontera con la instalación (R1).** La unidad `010-004` queda **cerrada en el
  repositorio y NO vigente en la instalación**: el despacho real usa la toolchain del
  repo (`skills/cdad-cycle/scripts/…` y sus envoltorios `scripts/`) hasta que el dueño
  decida publicar. La copia instalada conserva el comportamiento anterior (sin
  `--route`, esquema cerrado que desconoce el campo, preparación v1 implícita sin
  policy). Publicar es decisión del dueño, no del orquestador. Detalle y hashes
  medidos en `docs/specs/010-004-packet-dispatch-ergonomics/closure.md` §7.

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
- La admisión del rol es **documental**: las guardas verifican tokens estables y su
  supervivencia en los derivados, no la conducta de un modelo ni los bytes que recibió
  una sesión nativa. Toda afirmación de cumplimiento se lee con ese límite (R3).

## Scope general

Cubre: ciclo de 5 etapas, roles especializados (+variantes Odoo), epic
coordinado, bootstrap de Memory Bank, ejecución por proyecto v2 (política
única + agentes derivados + guard), continuidad, medición de contexto,
orientación acotada del orquestador y despacho de encargos por paquete
publicado (rutas A y C). Fuera de scope: runtimes específicos de
CI, adaptadores privados de entornos Odoo (viven en repos privados),
conectores o interceptores nativos de transporte, y certificación automática
de fidelidad semántica.

## Recursos externos

- Repo: https://github.com/rizzopablo/cdad
- Referencia de skills externos: obra/superpowers (comparación documentada en
  el epic superpowers-gaps)

---

Última actualización: 2026-10-31