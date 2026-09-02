# cdad-004: Gate de lint pre-commit-vauxoo en el contrato Odoo

> Estado: APROBADO — Status: Approved by Pablo Manuel Rizzo on 2026-09-02
> Fecha: 2026-09-02 · Origen: análisis de mejora propuesto por Pablo (02 Sep 2026).
> Evidencia de discovery: verificación empírica en sesión (PyPI, uvx, --help,
> hooks del .jinja fuente, ubicaciones actuales).

## Descripción funcional

El contrato de ejecución de tests Odoo (`odoo-make-env`) define hoy 3 targets
(`test`, `test-one`, `test-clean`) pero NO un target de lint; el skill
`odoo-reviewer` pide pre-commit solo "si el repo lo usa" (opcional) y con un
typo ("hoo-oca-pre-commit-hooks"). Se incorpora **pre-commit-vauxoo**
(Vauxoo, PyPI 8.3.18 — wrapper de pre-commit con config Vauxoo: pylint-odoo,
ruff-odoo, flake8, eslint + hooks genéricos) como gate obligatorio de lint
para módulos Odoo, sin modificar el núcleo de CDAD.

## Restricciones de diseño (decididas en discovery)

- **R1 — `--no-overwrite` siempre en el contrato**: la bootstrap de configs
  de pre-commit es decisión explícita del proyecto cliente, nunca del agente.
- **R2 — Invocación pinneada**: `uvx pre-commit-vauxoo==8.3.18` (o versión
  actual documentada en el skill); el Makefile la referencia pinneada.
- **R3 — El lint corre en host**, no dentro del runtime sandbox (requiere red
  en primera corrida: clona repos de hooks). Coherente con la nota ya
  existente en `odoo-reviewer` ("el lint corre en la máquina del
  desarrollador").
- **R4 — Autofixes deshabilitados** (default del tool; `-t all` no entra en
  el contrato).

## Contrato (postcondiciones numeradas)

**P1 — Target de contrato.** `odoo-make-env/SKILL.md` define `make lint` en
la tabla del contrato (nombres exactos, columna "Usado por") con semántica
explícita: `pre-commit-vauxoo` con `--diff` en desarrollo y `--all` para
evidencia de gate, siempre con `--no-overwrite`; regla de que corre en host
(R3) y pinneado (R2). El contracto pasa a tener 4 targets.

**P2 — Evidencia obligatoria en review.** `odoo-reviewer/SKILL.md` reemplaza
la línea "pre-commit limpio (hoo-oca-pre-commit-hooks) si el repo lo usa" por
evidencia obligatoria: output de `make lint` (`--all`) pegado, 0
bloqueantes; typo corregido. La sección "Evidencia requerida" pasa de 3 a 4
ítems numerados.

**P3 — Gate GREEN y verificación del reviewer.**
`cdad-implementer-odoo.md` incluye "lint limpio (`make lint`)" en su gate
GREEN; `cdad-reviewer-odoo.md` verifica esa evidencia en su checklist de
entrada (junto a `make test-clean` + oca-checks).

**P4 — Sincronización de instalación.** Tras los cambios, `install.sh
--check` reporta sin drift entre repo e instalaciones
(`~/.config/opencode/skills/` y `~/.agents/skills/`); ejecución de
`install.sh` para sincronizar, verificado con `--check`.

## Invariantes

- No se modifica ningún archivo de `cdad-cycle/references/` ni agentes
  genéricos (ortogonalidad con el epic Superpowers en planeación).
- El skill `odoo-reviewer` conserva el split mandatory/advisory: el lint es
  mandatory como evidencia; los hallazgos W/C siguen siendo advisory salvo
  regla explícita.
- Nada del contrato obliga a un proyecto cliente a adoptar configs Vauxoo en
  su repo (`--no-overwrite` siempre, R1).

## Criterios de aceptación (verificables)

1. Grep en `odoo-make-env/SKILL.md`: existe fila `make lint` en la tabla del
   contrato; el texto menciona `--no-overwrite`, `--diff` y `--all`.
2. Grep en `odoo-reviewer/SKILL.md`: no existe la cadena "hoo-oca"; la
   sección "Evidencia requerida" lista 4 ítems y el 4º exige output de lint.
3. Grep en `cdad-implementer-odoo.md` y `cdad-reviewer-odoo.md`: mencionan
   lint en gate GREEN / checklist de evidencia.
4. `install.sh --check` ejecutado con output sin drift.
5. RED: los checks 1-3 definidos ANTES de editar y fallando sobre los
   archivos actuales (output pegado).
