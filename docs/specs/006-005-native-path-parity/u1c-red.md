RED de U1c (006-005-native-path-parity) entregado y commiteado.

## Archivos

| Archivo | Cambio |
|---|---|
| `tests/test_006_005_u1c_packet_agent.py` (nuevo, 360 líneas) | 5 focales de PD-7, caja negra sobre `prepare`/`render`/`validate-request` y `receive` en proyecto descartable |
| `tests/test_packet_prepare.py` | A-1: reformulación declarada de `TestPrepareDefaults::test_p2_default_request_derivations_per_role` (+19/−1) |

Sin cambios fuera de `tests/`. `docs/planning/` y `findings/…` siguen sin trackear y sin tocar.

## Mapa test → postcondición

| Test | PD / oráculo |
|---|---|
| `test_pd7_agent_is_role_plus_stack_of_the_state` | PD-7: con `stack:"odoo"` ⇒ `REQUEST.json.agent == cdad-test-writer-odoo` / `cdad-reviewer-odoo` (dos roles, subtests) |
| `test_pd7_agent_without_stack_falls_back_to_the_role_agent` | PD-7: `stack` `null` **y ausente** ⇒ `cdad-test-writer` |
| `test_pd7_request_with_agent_validates_and_unknown_keys_stay_rejected` | PD-7: `validate-request` rc=0 con `agent`; clave desconocida ⇒ rc≠0 (conjunto cerrado intacto) |
| `test_pd7_agent_does_not_enter_the_packet_render` | PD-7: `render(request con agent) == render(sin agent) == bytes de PACKET.md`; metadata sin `agent` |
| `test_pd7_pre_feature_packet_without_agent_is_still_received` | PD-7: paquete sin `agent` (forma pre-feature) ⇒ `receive` rc=0 + recibo durable |

Dependencia declarada en el docstring (sin test que falle por ella): «`stack` con agente no publicado» es superficie de U2 (PD-14, `--agent cdad-<rol>-odoo` ⇒ fallo cerrado del módulo).

**A-1 (declarado en el propio RED, docstring del módulo + docstring del test + comentario inline):** `tests/test_packet_prepare.py::test_p2_default_request_derivations_per_role` fijaba el documento **exacto** de `REQUEST.json` (igualdad de dict completo) y la nueva conducta lo rompía. **Reemplazado por**: la misma igualdad exacta —conjunto de claves del request sigue cerrado— con el campo declarado `agent` presente, derivado del `stack` del estado del fixture (`stack: null` ⇒ `cdad-<rol>`). **Postcondición nueva**: PD-7 (§2.7). **Razón**: el oráculo de esa prueba es el documento completo del request, y la extensión declarada del conjunto cerrado lo cambia; se actualiza el valor esperado sin relajar el oráculo. Ningún otro test de las regresiones fija el conjunto de claves (verificado por grep).

## Comandos y salida

```
python3 -m pytest tests/test_006_005_u1c_packet_agent.py -q
→ 5 failed in 2.19s
   todos por AssertionError de PD-7 (ninguno ImportError/SyntaxError/fixture):
   "PD-7 violada (§2.7/D-13): el REQUEST.json publicado no lleva el campo declarado `agent` …"
   y en el caso de compatibilidad: "PD-7 violada (§2.7/D-13): `prepare` no publicó el campo declarado `agent` …"

python3 -m pytest tests/test_packet_prepare.py tests/test_005_006_t2_intake.py \
                   tests/test_role_packet_render.py tests/test_005_013_t1_unit_projection.py -q
→ 1 failed, 59 passed in 104.15s
   el único fallo es el test A-1 reformulado (mismo mensaje de PD-7);
   las otras tres regresiones de la ficha: verdes.

make validate
→ Assert PASS: 168 / Assert FAIL: 1
   FAIL: F011: scripts/validate-subagents.sh → install.sh --check
   DRIFT en ~/.claude/skills/cdad-cycle/references/cli-delegation.md y un __pycache__ del .pyc
```

Sobre `make validate`: el único FAIL es **drift pre-existente de las copias instaladas en HOME** (`install.sh --check` compara el repo con `~/.config|~/.agents|~/.claude/skills/cdad-cycle`), ajeno a `tests/` — mi diff no toca `skills/` ni `scripts/` (`git diff --stat` sólo lista los dos archivos de test). No lo toqué: la copia instalada está fuera de mi write scope; queda reportado al orquestador.

## Commit

`eab7e2f5b6ae819f6e20a08015e66e05b33130f1  test: 006-005 U1c RED — el agente viaja en el paquete (PD-7)` (sólo los dos paths de `tests/`; sin `--no-verify`, sin stash, sin push).

## Aislamiento (honesto)

No leí código de implementación (`skills/cdad-cycle/scripts/**`): el CLI se invoca como subproceso y sólo observé efectos publicados (rc, stdout/stderr, bytes de `PACKET.md`, `REQUEST.json`, recibo). Una sonda previa listó el árbol que `prepare` publica en un proyecto descartable (efectos, no fuentes). No leí `tests/.sensitive-patterns.local`. Sin valores del host: todos los proyectos son tempdirs. Límite honesto: la forma «paquete pre-feature» del último test se reconstruye quitándole al request publicado el campo opcional declarado — es fiel porque el render es invariante al campo, y ese mismo invariante es el oráculo del test de bytes.