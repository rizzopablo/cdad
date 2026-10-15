# Deuda — 003-004-context-continuity

Criterio MVP: lo que no rompe el camino feliz va a deuda priorizada.

## Alta
- (ninguna)

## Media
- **T3-O1:** el perfil 200k (reserva 50k, preparar a 120k) se extrapola a cualquier límite entero. Falta nombrar el perfil en el envelope o documentar la regla.
- **T3-O2:** valores enteros sin sentido (negativos, `limit<=0`) producen una señal definitiva; deberían dar `unknown` con la anomalía nombrada.
- **V1/V3 (runtime):** no está verificado si los tokens de `step-finish` son por paso o acumulados, ni si existe un límite de contexto observable. Hoy `trigger` es casi siempre `unknown`. Calibrar con uso real.
- **Rollback/replay de un head viejo y tamper autoconsistente:** sin firma ni contraste de `seq`; documentado en `continuity.md`.
- **Validadores:** F011 (`validate-subagents.sh`, que depende de `install.sh --check` contra copias en HOME o staging ausente) y A3 de `validate-odoo-specialization.sh` (patrones sensibles en 004-003 y en `.pyc`). Son preexistentes a 003-004 y quedan fuera de su alcance.

## Baja
- **T3-N1..N7:**
  - `--runtime` no tiene efecto;
  - el envelope de `trigger` no declara `trigger-v1`;
  - `budget` es siempre un dict;
  - `budget` no se valida al escribirlo;
  - una frase de `continuity.md` sobre `--max-bytes`;
  - el focal solo corre con discover;
  - la conducta de tamper en `trigger` no tiene test.
- **T2 nits:** el test A llama `setUp()` a mano; los mensajes de C usan etiquetas distintas; R-STR (el schema del head no se valida en runtime).
- **F2 (T2):** los cuerpos huérfanos no se verifican.

## Agregado tras T4 (uso real)
- **Media — RU-2a:** en el modo de despacho actual la salida de los roles no pasa por `cdad_result receive`, así que `reconcile` solo puede dar `dispatched-unknown`. Adoptar `receive` en el flujo de despacho, o documentarlo como límite.
- **Baja — RU-2b:** el checkpoint no incluye HEAD ni timestamp de emisión. Hoy se cubren con `--update` (por ejemplo, en `references` y `next_action`); son candidatos a campo.
