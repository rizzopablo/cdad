# Informe — Implementer GREEN (review-fix B3), T5 de `005-012-transition-registration`

**Paquete:** `005-012-transition-registration-implementer-green-010` · **Ejecución:** `exec-005-012-transition-registration-001` · **Tarea:** T5 (review-fix del bloqueante B3, subetapa `green`)
**Contrato:** `docs/specs/005-012-transition-registration/spec.md` (sha256 `9e34750f…e7cc9`, draft-004 vigente: PD-14 / D-8 enmendados) · **Plan:** §4 ficha T5 · **Oráculo rojo:** `b3-red.md`. Raíz del repo: `<repo>`.

*Nota de anonimización:* sin rutas absolutas del dueño, ids crudos de sesión ni nombres de otros proyectos.

## (a) Qué implementé y dónde

**Un solo archivo, una sola condición.** `skills/cdad-cycle/scripts/cdad_packet.py` — control de exclusión de PD-14 en `register_transition` (bloque `if transition == "gate" and stage == SPEC_GATE_STAGE and contract_path is not None`):

```python
            vigente = [item for item in _approved_spec_entries(state, feature_id)
                       if item.get("contract_path") == contract_path
                       and item.get("contract_sha256") == contract_sha256]
```

- El predicado «VIGENTE» pasa a ser **el pin que NOMBRA los bytes actuales**: mismo `contract_path` **y** `contract_sha256` **ya resuelto** de esos bytes (PD-20) — el **mismo criterio** que el cierre consume en PD-8(b). Consumí ese criterio; **no** re-declaré la regla del pin (D3/PD-18) ni normalicé nada nuevo.
- Efecto mecánico: una entrada cuyo pin ya no nombra los bytes actuales **no** compite → el `gate` de etapa 2 tras una enmienda se registra **sin `--supersedes`**, tenga o no `transition_key` la entrada vieja (consecuencia 1 / B3). Con los **mismos** bytes (pin al día) nada cambia: sigue exigido `--supersedes` y el rechazo conserva marcador `state incoherent`, el nombre de la entrada vigente y el campo `supersedes` (consecuencia 2). El caso raro keyless con los mismos bytes queda intacto → deuda **D-16**.
- `contract_path is not None` **implica** `contract_sha256 is not None` (`_pin_relative_digest` los asigna juntos), así que la comparación no puede degradarse a `None == None`.
- Comentario **en inglés**; **sólo afloja** el control en el caso declarado y no agrega exigencia alguna a entradas históricas (INV-3/PD-17). La entrada con el pin viejo **ya** era inoperante para el lector (D3/PD-18): nada que habilitara dejó de habilitar.

**No toqué:** ningún archivo de tests; `_contract_approval_for` (la regla del pin del lector); `_validate_v2_vigency`; el comportamiento de `--supersedes`; las demás clases; ni el state (el `M docs/.cdad-state.json` del árbol es del orquestador). Diff: **+13 / −1**, todas en el bloque citado.

## (b) Comandos exactos y salida (pegada)

**1. Focal de B3 (oráculo congelado):**
```
$ python3 -m pytest tests/test_005_012_t5_approval_vigency.py -q
........                                                                 [100%]
8 passed in 16.12s
```

**2. Regresiones de T2, T3 y T5 (pedidas por el orquestador):**
```
$ python3 -m pytest tests/test_005_012_t2_gate_authority.py tests/test_005_012_t3_closure_dispatch_resolution.py tests/test_005_012_t5_approval_vigency.py -q
.................................                                        [100%]
33 passed in 44.86s
```

**3. Resto de los focales de la feature (no romperlos):**
```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py tests/test_005_012_t4_late_delivery.py tests/test_005_012_t6_open_context_guard.py -q
...............................                                          [100%]
31 passed in 42.95s
```

**4. Regresiones declaradas por el paquete:**
```
$ python3 -m pytest tests/test_005_001_t1_role_approval.py tests/test_005_001_tcorr.py tests/test_005_005_t1_replace_conserved.py tests/test_packet_prepare.py -q
..........................................                               [100%]
42 passed in 44.06s
```

**5. Puerta de integración del paquete:**
```
$ python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root .
VALID: execution=exec-005-012-transition-registration-001 feature=005-012-transition-registration model_policy=ordinary

$ ruff check skills/cdad-cycle/scripts/cdad_packet.py
All checks passed!
```
La **suite completa no se corrió** (política: la corre quien cierra).

## (c) Prueba de que `tests/` no se tocó

```
$ git diff --name-only dc13903..HEAD -- tests/
          <— vacío
$ sha256sum tests/test_005_012_t5_approval_vigency.py
39b3602eec9c6931f8fb53ff1dafaa019f9b18428a9761828eb2779c86a83b24  tests/test_005_012_t5_approval_vigency.py
```
Las corridas se ejecutaron sobre el árbol con ese mismo hash: el snapshot de los tests al correrlos es el del RED congelado, no sólo el estado final.

## (d) El commit

```
$ git show --stat --oneline HEAD
ffb7abd feat: 005-012 review-fix B3 — vigencia por el pin que nombra los bytes actuales (reaprobacion tras enmienda sin --supersedes en el control de exclusion de PD-14)
 skills/cdad-cycle/scripts/cdad_packet.py | 14 +++++++++++++-
 1 file changed, 13 insertions(+), 1 deletion(-)
```

## (e) Interpretaciones, límites y por qué no me detuve

1. **Consumir el criterio vs. extraer un helper compartido.** Implementé la condición **inline**, en la misma forma que la usaba el cierre en PD-8(b), en vez de extraer un helper y reescribir la comprobación del cierre: el alcance es el control de exclusión y la extracción habría editado la clase `closure`. Consumí el **criterio**; no agregué un tercero.
2. **Mensaje del rechazo intacto:** sigue siendo `state incoherent` nombrando la entrada vigente y el campo `supersedes`. En el caso keyless (D-16) sigue imprimiendo `transition_key None`; es el comportamiento declarado como deuda, no lo amplié.
3. **Aditividad (INV-3/PD-17):** el predicado **lee** `contract_path`/`contract_sha256` (campos que las entradas `specification` ya tienen por D3) y **no** lee `transition_key`/`transition_key_payload`; el caso 4 del RED lo verifica con `validate-state` rc=0 antes y después y la historia sin clave intacta.
4. **`--supersedes` intacto:** su verificación (entrada existente, misma feature, mismo `contract_path`) no cambió; el caso 6 del focal y la mitad «mismos bytes con `--supersedes`» siguen verdes.
5. **Nada me bloqueó.** No hubo que tocar ningún test ni intervino un límite de permisos; no detecté contradicción entre el contrato y el oráculo.
6. **Límite heredado:** el caso raro de D-16 (mismos bytes, la vigente es keyless) queda sin salida por la operación y sin test propio; no inventé mecanismo ni oráculo.

**Estado:** 8/8 focal, 33/33 (T2+T3+T5), 31/31 (T1+T4+T6), 42/42 (regresiones declaradas), `validate-state` rc=0, ruff limpio, tests intactos, commit `ffb7abd`.
