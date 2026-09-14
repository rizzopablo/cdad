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

## Palanca `write: ask` y permisos de bash (cdad-010, ADR-009)

### Palanca `write: ask` (2026-09-12; enmienda de ubicación 2026-09-13)

Los 10 agentes declaran `permission.write: ask` — la clave `write` ANIDADA
dentro del bloque `permission:` del frontmatter (NO top-level: el KNOWN_KEYS
del clasificador no incluye `write` top-level y una palanca top-level es
inerte — el agente colapsa a read-only y `task` lo rechaza; verificado por
probe en cdad-010, enmienda registrada en el spec H1). Doble rol NO obvio: es
la palanca que hace al agente **task-able**. Motivo: el clasificador del
plugin de sub-agentes lee la clave `write` del bloque `permission:` anidado
para decidir si el agente es write-capable o read-only; el runtime NO la
evalúa (el tool `write` pide "edit" — cero evaluaciones `permission=write`
en logs). Mecánica: el agente queda task-able sin generar prompts de permiso.

**REGLA DE VIGILANCIA: si una versión futura de opencode empieza a evaluar
`write` en runtime, la palanca `write: ask` genera prompts de permiso en cada
escritura y hay que revisar los 10 agentes.** Checklist al migrar versión:
(1) grep de logs buscando `permission=write`; (2) si aparece, migrar la
palanca a otra vía y re-probar la clasificación task/delegate con los probes
de cdad-010 como baseline.

### Bloques `permission:` anidados y orden findLast

El clasificador del plugin lee SOLO el bloque anidado `permission:`
(edit/bash/read); las claves top-level caen en `options` — inertes en
runtime. Semántica del matcher: **catch-all primero, específicas después**
(findLast: la última regla que matchea gana). Una regla específica antes del
catch-all es un bug de config. Única excepción documentada de `ask`: la
palanca `permission.write: ask` (anidada).

### Política de enforcement (2026-09-13, Pablo — decisión de Capa 2 de cdad-010)

1. **Bloquear vectores directos y evidentes**, no bypasses hipotéticos: un
   agente con ganas de saltar las vallas siempre encontrará cómo.
2. **La expectativa se documenta** en skills y archivos de procedimiento:
   qué debe hacer el agente, qué no, y para qué.
3. **El agente debe SABER lo que se espera de él**: si no puede cumplir,
   devuelve la tarea explicando por qué; si cumple sin respetar el protocolo
   y sin motivo válido que pueda explicar, **la tarea se considera NO
   cumplida (fallida)** — aunque el artefacto exista.

**Definición operativa de "vector directo y evidente" (2026-09-13, N3 del
re-review de cdad-010):** un vector es directo y evidente si y solo si es
**demostrable con un probe de una sola invocación con output pegado** (Regla
de Oro). No califican: razonamientos sobre lo que el matcher "debería"
hacer, observaciones narradas sin paste, ni construcciones hipotéticas
multi-paso. Motivo: en el propio ciclo cdad-010, dos sesiones concluyeron
veredictos OPUESTOS sobre el mismo matcher ("compuestos pasan por prefijo"
vs "por segmento") — el que tenía probes pegados tenía razón. Cuando un
hallazgo de seguridad no pueda demostrarse con un probe de una invocación,
se registra como candidato de hardening con la premisa explícita a
verificar, nunca como bloqueante por intuición.

### Pares rtk `X*` + `rtk X*` (ADR-009)

Los modelos del workspace envuelven comandos en `rtk` (proxy CLI), así que
las allowlists por comando llevan SIEMPRE el par (`"pytest*"` y
`"rtk pytest*"`), con los subcomandos peligrosos de rtk denegados en todos
los roles. Matriz completa y razones: `docs/adr/ADR-009-politica-rtk-allowlists.md`.

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

Última actualización: 2026-09-12
