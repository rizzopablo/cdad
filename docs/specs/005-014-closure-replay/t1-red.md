**RED completo.** Informe de la tarea T1 de `005-014-closure-replay`:

## Artefacto escrito (único archivo modificado por este rol)
- `tests/test_005_014_closure_replay.py` — **NUEVO**, 4 tests, cada uno apuntando a su postcondición numerada. Solo toca proyectos descartables en `tmp_path` con `HOME` del subproceso aislado (patrón y helpers de `tests/test_005_012_t3_closure_dispatch_resolution.py` / `test_005_012_t1_register_transition_base.py`). No leí implementación, no modifiqué tests existentes, no toqué el state de este repo desde los tests.

## Comando exacto y salida
```
python3 -m pytest tests/test_005_014_closure_replay.py -q -p no:cacheprovider
```
```
FAILED ...::test_pd23_identical_closure_replay_is_noop_naming_the_registered_entry
FAILED ...::test_pd25_distinct_closure_after_closure_rejects_closed_naming_feature_and_done
FAILED ...::test_pd24_closure_with_feature_differing_from_active_feature_fails_closed
FAILED ...::test_pd22_closure_without_feature_and_without_active_feature_rejects_without_open_unit
4 failed in 4.08s
```

## Razón del rojo por test (todas AssertionError de contrato, ninguna de import/colección)
1. **PD-23 (replay idéntico)** — falla `assert 2 == 0`: la primera invocación cierra (rc=0, comportamiento existente PD-9), pero la **repetición idéntica muere hoy en el guard de feature nula** (`:5062-5065`, antes del no-op `:5310`) → rc=2 con «open the unit first (`open-unit`)»; el no-op nunca se alcanza.
2. **PD-25 (cierre distinto)** — falla `assert 'demo-100-transition-fixture' in 'ERROR: state incoherent: there is no active feature … open the unit first (`open-unit`)'`: hoy rc=2/marcador presentes, pero el mensaje **no nombra la feature ni su estado `done`** y **SÍ sugiere `open-unit`/`open the unit`** (en ambas variantes: otro `--stage` y otro `--closure-path` con otros bytes).
3. **PD-24 (--feature que difiere)** — falla `assert 0 == 2`: hoy `--feature` se **ignora en silencio** con feature activa → el cierre cierra la feature EQUIVOCADA (rc=0), nunca rechaza.
4. **PD-22 (--feature faltante sin activa)** — falla `assert 'open-unit' not in '…open the unit first (`open-unit`)…'`: hoy el guard rechaza con el texto que sugiere abrir la unidad y **sin ofrecer `--feature <feature-id>`** (mutación de fixture: `active_feature: null`, sin cierre previo en la historia).

## Commit
- `8a969d3` en `codex/epic-005-real-operation`: `test: 005-014 T1 RED focal closure replay (PD-22/23/24/25) sin feature activa` — solo `tests/test_005_014_closure_replay.py` (+446).

## Notas honestas para el orquestador
- El diff preexistente de `docs/.cdad-state.json` en el working tree es el despacho de este paquete (bookkeeping del orquestador, fuera de mi write scope): quedó **sin commitear** y sin tocar por mí.
- No corrí la suite completa (política declarada: la corre quien cierra, una vez, en el cierre).
- Dato para el GREEN: los comandos de verificación de PD-23/PD-25 en la spec repiten la orden **sin `--feature`** (tras el cierre `active_feature` queda `null`), mientras PD-22 ofrece la vía `--feature` para el replay; la implementación deberá resolver la feature del replay cerrado sin desvío (p. ej. desde la entrada de cierre registrada) para satisfacer PD-23 sin contradecir PD-22 — la focal aserta el contrato tal como está escrito (los 4 casos fallan hoy exactamente por el defecto medido en el discovery §0).
