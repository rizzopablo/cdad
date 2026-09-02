# System Patterns

Convenciones técnicas, patrones, y reglas estructurales del proyecto. Este archivo se carga al inicio de cada sesión de agente.

## Capas y boundaries

- `agents/*.md` — definición de roles: frontmatter (permisos por path, bash
  allowlist, modelo) + directiva del rol. Thin shells: la lógica vive en
  skills, no en el agente.
- `skills/cdad-cycle/` — el ciclo: `SKILL.md` (contrato mínimo siempre
  cargado) + `references/stage-N-*.md` (profundización por etapa, se carga
  una a la vez).
- `skills/cdad-epic/` — coordinación multi-feature (planning light,
  deliberadamente sin descomposición exhaustiva).
- `skills/odoo-*/` — especialización por stack: variante `cdad-*-odoo` de
  cada agente + skills de conocimiento por rol + contrato make.
- `tests/` — validación estructural del framework (bash asserts).
- `docs/specs/<NNN-id>/` — spec + VALIDATION + review por feature.
- `install.sh` — única vía de instalación (copia, nunca symlink, sin --delete).

## Convenciones de código

### Naming

- Agentes: `cdad-<rol>` y variante `cdad-<rol>-odoo`.
- Skills: kebab-case con prefijo de dominio (`odoo-reviewer`).
- Specs: `NNN-feature-id/` (numeración correlativa).

### Organización de archivos

- Reference nueva vs. extensión: se decide por "¿es una etapa/flujo o una
  profundización?" (ver epic superpowers-gaps para los 5 casos resueltos).
- Todo artefacto de rol read-only lo materializa el orquestador (§5 del
  contrato de roles).

### Errores y excepciones

- Anti-patrones: `references/anti-patterns.md` (AP-N) — toda desviación se
  cita con su código.
- Anti-rationalization table: excusas ya refutadas por escrito; no se
  negocia con la excusa, se aplica la refutación.

## Patrones del framework

- Contrato de roles con invariantes anti-bias: reviewer en familia de modelo
  distinta al implementer; test-writer nunca ve `src/`; mapeo
  test↔postcondición auditado por sesión distinta.
- Delegación por orden de preferencia: sub-agentes nativos → handoff packet →
  inline (último recurso, con caveat de aislamiento registrado).
- Evidencia, no confianza: cada gate se cierra con output pegado.

## Convenciones de tests

- **Framework**: bash + grep asserts (`assert_file_has`/`assert_file_not_has`).
- **Estructura**: `tests/*.sh` para invariantes de cdad-003; checks por
  feature en `docs/specs/<id>/VALIDATION.md` (mapeo check↔postcondición).
- Los checks se definen ANTES de editar (RED) y corren desde la raíz del repo.

## Tooling enforcement

- Sin CI aún: gate local = suite bash + checks VALIDATION (deuda registrada).
- Proyectos Odoo gestionados con CDAD: `make lint` (pre-commit-vauxoo,
  pinneado, --no-overwrite, host) + `make test/test-one/test-clean`.

## Anti-patrones del proyecto

- Orquestador escribiendo código/tests inline sin conmutar de modo (AP-10,
  §4). Implementer tocando tests (AP-4). "Verde" sin output (AP-3). Aprobación
  delegada al LLM (indelegable: Memory Bank, specs, priorización de review).

---

Última actualización: 2026-09-02
