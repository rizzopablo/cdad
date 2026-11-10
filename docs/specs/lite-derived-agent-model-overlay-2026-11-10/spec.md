# Lite spec — el `model:` del agente derivado es del dueño del proyecto (2026-11-10)

## Problema
`prepare`/`republish-agents` derivan `.opencode/agents/cdad-*.md` desde la
instalación y heredan su `model:`. Si el dueño cambia el `model:` del derivado
(p. ej. a haiku), `prepare` lo rechaza como "modified by hand" y la recuperación
(republish o `git checkout`) lo vuelve al modelo instalado. El instalador ya
trata `model:` como clave del usuario (009-001, `scripts/agent-overlay.py`); la
derivación por proyecto no adoptó esa regla.

## Postcondición
El comportamiento (cuerpo y frontmatter salvo `model:`) viene de la fuente
instalada; los permisos, de la política del proyecto; el `model:` es del
proyecto. Concretamente:

1. Un derivado cuya única diferencia con lo publicado es la línea `model:`
   NO es una modificación a mano: `prepare`/`republish-agents` lo aceptan (rc 0).
2. El derivado republicado conserva ese `model:` aunque la fuente cambie
   (incluido su propio `model:`), y en republicaciones posteriores.
3. Sin `model:` propio del proyecto, se hereda el instalado (PC-09 de 007-006
   sigue vigente, incluida la ausencia).
4. Una edición fuera de `model:` sigue rechazándose (PD-8/I9).
5. Manifiestos previos (sin `base_sha256`): una edición solo de `model:` se
   acepta si el resto coincide con la derivación actual.
6. CDAD sigue sin elegir modelo (I6): solo transporta el del dueño.

## Límite declarado
La línea `model:` se reconoce en columna 0 del frontmatter (misma gramática que
`agent-overlay.py`). Una reescritura completa del frontmatter por un editor
externo sigue contando como edición a mano.

## Verificación
- `tests/test_lite_derived_model_overlay.py` (RED antes del cambio, GREEN después).
- Focales: `test_007_006_withdraw_and_republish.py`, `test_packet_prepare.py`.
