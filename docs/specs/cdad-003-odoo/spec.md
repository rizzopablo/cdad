# cdad-003: Especialización Odoo de CDAD (Odoo-CDAD)

> Estado: APROBADO 2026-08-28 — Ofap como orquestador/HITL designado por Pablo
> ("decide con el mejor criterio de visión general y de calidad"). Ciclo CDAD
> habilitado (RED → GREEN → Review → Merge).
> Fecha: 2026-08-28 · Origen: fases F0/F2/F3/Fb (evidencia empírica en dos
> entornos reales: odoo.sh y un staging interno privado).

## Descripción funcional

CDAD se especializa para proyectos Odoo **sin modificar su núcleo**: variantes
Odoo de los 5 agentes (thin shells: frontmatter + una línea de skill), skills
de conocimiento por rol, y un contrato de ejecución de tests (`make`) que los
agentes invocan sin saber dónde corre el entorno. Todo lo publicable es
genérico; los adaptadores de entornos privados viven en repos privados.

## Contrato (postcondiciones numeradas)

**P1 — Variantes de agentes.** Existen 5 archivos de agente variante Odoo
(architect, test-writer, implementer, reviewer, scribe) que difieren del
genérico SOLO en:
- frontmatter: paths acotados a módulos Odoo (test-writer: niega
  `**/models/**`, `**/views/**`, `**/controllers/**`, `**/wizards/**`,
  permite `**/tests/**` y `__manifest__.py`; implementer: niega
  `**/tests/**`), allowlist bash limitada a `make *`, `pre-commit *`,
  `pylint *`, `git *` (sin comandos de entorno específico), modelo del
  reviewer distinto al del implementer;
- cuerpo: misma directiva del rol + carga del skill Odoo del rol.

**P2 — Skills por rol.** Existen skills Odoo para: architect (guía de
implementación de proyectos: modelo GAP→Kick-Off→Implementation→Go-Live,
roles PL/SPoC/Developer, "configuración primero, custom solo si hay gap",
inventario OCA antes de especificar), test-writer (framework de tests Odoo:
TransactionCase, `@tagged` obligatorio, Form→web, freeze_time, fixtures
self-contained sin demo data, `make test-one` para RED), reviewer (checklist
OCA + catálogo pylint-odoo vigente + split mandatory/advisory + mapeo a los
5 ejes de review). El implementer reutiliza `odoo-dev-methodology` +
`odoo-expert` existentes, sin duplicar contenido.

**P3 — Contrato make.** Los assets publicables incluyen `Makefile.template` y
`odoo-test.conf.template` (placeholders) con los 3 targets del contrato Fb
(`test`, `test-one`, `test-clean`) y la tabla de varianza por entorno
(verificado: F2 odoo.sh, F3 staging privado).

**P4 — Activación por stack.** El state (`docs/.cdad-state.json`) admite
`"stack": "odoo"`; el skill `cdad-cycle` documenta que con ese valor el
orquestador delega a las variantes Odoo. El núcleo sin cambios.

**P5 — Instalación.** `install.sh` instala las 5 variantes y los skills
nuevos sin tocar los agentes existentes ni las skills de otros dominios
(misma política G2 verificada en fases previas).

**P6 — Lecciones empíricas incorporadas.** Los hallazgos F2/F3/Fb quedan en
referencias de los skills: `res.groups.privilege_id` (19), `<list>` en vez
de `<tree>` (19), `Form` exige `web`, `-i` no-op sobre instalado, drift de
schema en builds gestionados, saturación de postgres compartido, `-i`/`-u`
para carga de tests nuevos.

## Invariantes

**I1** El núcleo CDAD (agentes genéricos, ciclo de 5 etapas, state machine,
verdict tuple) no se modifica — la especialización es aditiva.
**I2** Ningún artefacto publicable contiene referencias privadas
(hostnames, rutas reales, credenciales): verificación con `git ls-files` +
grep de patrones sensibles antes de publicar.
**I3** Los gates de tests de todas las etapas se definen SOLO sobre el
contrato make (3 targets) — nunca sobre comandos de un entorno concreto.

## Criterios de aceptación

**A1 — Ciclo completo sobre el módulo de ejemplo `idea_log`:** RED (un test
nuevo falla por AssertionError con `make test-one`) → GREEN (suite verde con
`make test`) → gate clean (`make test-clean` verde con demo data cargada) →
review (pylint-odoo sin E/W bloqueantes + oca-checks 0 hallazgos + suite).
**A2 — Dos entornos, mismos targets:** F2 (odoo.sh) y F3 (staging privado) verdes —
evidencia ya obtenida en spikes: 7/7 tests, 3 targets funcionales (odoo.sh
completo; el runtime del staging privado pendiente de postgres, gates estáticos verdes).
**A3 — Sanitización:** el grep de patrones sensibles sobre lo publicable
devuelve 0 coincidencias.
**A4 — Reviewer ≠ implementer en modelo** (perfiles ADR-007).

## Fuera de alcance (explícito)

CI completa estilo OCA (workflows GitHub Actions), Runbot propio, entornos
adicionales (docker local, oca-ci), record rules e i18n/.pot en el módulo de
ejemplo, propiedad de data demo más allá del gate de instalación.

## Contexto técnico (fuentes verificadas)

- Docs oficiales Odoo (coding guidelines, ORM, views, security, testing) — F0.
- Estándares OCA (CONTRIBUTING.rst, pylint-odoo, oda-pre-commit-hooks,
  manifestoo, CI) — F0.
- Whitepaper oficial de metodología de implementación Odoo (GAP→Go-Live,
  roles PL/SPoC) — F0.
- Evidencia empírica: `drafts/f0-odoo-sh-environment.md`,
  `drafts/fb-make-contract.md`, `drafts/odoo-test-module-definition.md`
  (repo público) y doc privado F0/F3 en infra privada.
