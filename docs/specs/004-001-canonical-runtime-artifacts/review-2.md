# Review-2 focal T4 — 004-001-canonical-runtime-artifacts

Fecha: 2026-09-26. Reviewer: GPT/Codex (familia distinta del implementer GLM).
Árbol: `c337654`; cambios revisados: `be06c94` (B1) y `297a77a` (B2).
Read-only: código, tests y estado sin modificaciones por el reviewer.

## Verdict

```
dictamen: changes-required
blocking: 1
optional: 0
abstain:  0
```

## Cierre confirmado de review-1

- **B1 resuelto** (expansión de comandos git) — reglas correctas en readers
  instalados, verificado independientemente por el reviewer.
- **Mejoras de B2 llegan a la instalación genérica** — `du` recuperado,
  `rtk ls/pwd` en writers, `--check` PASS 46/46, instalación aislada PASS,
  3 tests focales en verde.

## Hallazgo

### R2-B1 — El adaptador selecciona la variante genérica cuando se solicita Odoo

- **Verdict:** BLOCKING · **Bucket:** h
- Con `--stack odoo`, el generador produce agentes genéricos y especializados,
  pero el adaptador siempre extrae `cdad-$ROLE.md`. Omite los permisos de
  `pylint` y `pre-commit`, incluidos sus pares RTK. Reproducido con
  `implementer --stack odoo` y con `implementer-odoo`; ambos terminan
  exitosamente con política incompleta. Las variantes Odoo copiadas
  directamente por el instalador conservan los permisos: el defecto está en
  este camino del adaptador.
- Provenance: `297a77a`, `scripts/cdad-bash-allowlist.sh:139`; el generador
  produce ambas variantes en `scripts/cdad-generate.py:956`. Contrato: PD-1,
  preservación de la especialización Odoo y capacidades de T4.
- Comparación reproducida por el reviewer:
  `/tmp/cdad-t4-rereview-uqfq1wf_/odoo-comparison.json`.

## Corrección mínima avalada

Seleccionar el artefacto correspondiente al stack resuelto y comprobar la
paridad del adaptador con esa variante. **No** agregar permisos manualmente
para compensarlo: reintroduciría la duplicación.

## Sobre la deuda de tests (corrección del reviewer a la nota del state)

El reviewer **no** indicó postergar las regresiones hasta T5/T6. Pidió evitar
una batería por comando; bastan pruebas pequeñas que protejan (a) la expansión
de nombres y (b) la selección/paridad genérica–Odoo. **Conviene incorporarlas
en este arreglo**, porque ya existe una regresión que los tres tests actuales
no detectan.

## Dictamen

El avance es válido; falta este arreglo localizado para cerrar T4.
Materializado por el orquestador (GLM) desde el reporte final del reviewer
(ADR-003).
