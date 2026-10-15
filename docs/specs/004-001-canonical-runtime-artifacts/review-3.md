# Review-3 focal T4 — 004-001-canonical-runtime-artifacts

Fecha: 2026-09-26. Reviewer: GPT/Codex (familia distinta del implementer GLM).
Árboles: `5f2389c` (RED, verificado en worktree separado) y `71f17ee` (fix).
Read-only: código, tests y estado sin modificaciones por el reviewer.

## Verdict

```
dictamen: changes-required
blocking: 1
optional: 2
abstain:  1
```

## Cierre de R2-B1: confirmado

- **El RED era real.** Worktree en `5f2389c` (test presente, fix ausente) falla
  por aserción contra el defecto vivo: `AssertionError: ... stack-odoo-emitted
  output lost the odoo-declared permit 'pylint'`. La regresión de dobles
  prefijos pasa, como se declaró.
- **La paridad vale para los 5 roles**, no solo implementer: `<rol> --stack
  odoo` vs `<rol>-odoo` idénticos en architect, test-writer, implementer,
  reviewer y scribe; los 5 emiten las 4 reglas `pylint`/`pre-commit` con sus
  pares rtk.
- **El fix es por selección, no parches**: el diff solo elige la variante según
  el stack resuelto del manifest y falla rápido ante un stack inesperado. Sin
  reglas manuales (condición de la review-2).
- **Sin regresiones en lo verificado:** `install.sh --check` PASS 46/46 y los
  tres validadores PASS en raíz aislada; pares `rtk wc *` y `du *` presentes
  (fricción C0 resuelta dentro del rediseño).
- Sospecha descartada: el staging es `mktemp -d` por invocación; sin carrera
  entre instalaciones concurrentes.

## Hallazgo bloqueante

### R3-B1 — El adaptador rompe la garantía de instalar sin `HOME`

- **Verdict:** BLOCKING · **Bucket:** h · **Confianza:** alta
- **Ubicación:** `scripts/cdad-bash-allowlist.sh:128`, introducido en
  `297a77a` (aterrizaje anterior, no en `71f17ee`).
- **Motivo:** `STAGE_DIR="$(mktemp -d "${TMPDIR:-$HOME}/.cdad-allowlist-XXXXXX")"`
  bajo `set -u`. Si `TMPDIR` no está definido y `HOME` tampoco, aborta con
  `HOME: unbound variable`. Rompe la postcondición P6 de 003-001 (raíz
  explícita `CDAD_INSTALL_ROOT` sin depender de `HOME`), con su propio test de
  regresión.
- **Evidencia:** con `TMPDIR` sin definir, `pytest tests -q` da 68 passed,
  1 failed: `test_p6_explicit_install_root_works_without_home` →
  `AssertionError: 1 != 0 : explicit CDAD_INSTALL_ROOT still depended on HOME:
  scripts/cdad-bash-allowlist.sh: line 128: HOME: unbound variable`. Con
  `TMPDIR=/tmp` el mismo test pasa. Reproducido también por el orquestador en
  su entorno.
- **Corrección mínima:** `${TMPDIR:-/tmp}` (o `${TMPDIR:-${HOME:-/tmp}}`).
  Siguiendo el precedente de la review-2, la regresión entra en el mismo
  arreglo: el test existente debe limpiar también `TMPDIR`, para que la
  garantía se verifique siempre y no según la máquina. **Esa parte es del
  test-writer, no del implementer.**

## Opcionales

- **R3-O1 (coverage):** ningún test ejercita `--stack auto`. En una máquina con
  odoo detectado, los agentes genéricos pasan a recibir el bloque de la
  variante odoo — sin cobertura, y aquí no cubrible por falta del binario
  `odoo`. Se resuelve con stub en el `PATH`; para T6/T7, no bloquea T4.
- **R3-O2 (tensión de contrato):** el criterio de aceptación 8 del spec dice
  stack como entrada explícita y "no efecto oculto de la máquina", pero el
  camino `auto` lo resuelve por detección. Queda registrado en el manifest de
  staging (auditable en generación); T5 lo registrará también en el manifest de
  instalación y el texto del spec acota ese principio al generador.

## Abstenciones

- No verificada la paridad del adaptador de Claude Code (es T6) ni el
  comportamiento en una máquina con odoo real.

## Lección de evidencia (para el bucket de 003-003 y el contrato de evidencia)

El reporte de 69/69 del orquestador no fue deshonesto: fue **dependiente del
entorno**. Con `TMPDIR` definido el test pasa; sin definir, falla. Una corrida
verde en una máquina no prueba la garantía si el test depende de una variable
que el propio entorno provee. La corrección de fondo no es solo la línea 128:
el test debe fijar esa condición en vez de heredarla.

## Cierre de T4

No se cierra T4 todavía. Con R3-B1 arreglado (una línea más su regresión
env-independiente), el aterrizaje A queda cerrado.

## Decisión del epic (registro)

T5 permanece dentro de 004-001, con la condición ya planteada: aterrizaje
intermedio utilizable (generador y adaptadores funcionando, instalación sin
cambios). Si al abrir T5 el manifest de propiedad crece más allá de su
semántica definida, se promueve a feature propia.

Materializado por el orquestador (GLM) desde el reporte final del reviewer
(ADR-003).
