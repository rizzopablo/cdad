# Informe — implementer GREEN (review-fix B1)

**Feature:** `005-012-transition-registration` · **Ejecución:** `exec-005-012-transition-registration-001`
**Paquete:** `005-012-transition-registration-implementer-green-009` · **Tarea:** T3 (review-fix del bloqueante B1)
**Contrato:** `docs/specs/005-012-transition-registration/spec.md` (sha256 `56d0be4b…edd5`) — PD-6 (gate **y** `closure`, tres casos), PD-8, PD-9, PD-21, PD-12(iv), INV-4, INV-7. Raíz del repo: `<repo>`.

## (a) Qué implementé y dónde

Único archivo modificado: `skills/cdad-cycle/scripts/cdad_packet.py` (+28/−13, un solo commit). Tres ediciones, todas dentro de `register_transition` y su vecindad:

1. **La rama de `closure` ahora consume el control de autoridad de PD-6.** Al final de las comprobaciones previas a cualquier escritura (después de PD-8(a), PD-8(b) y de resolver/derivar la cita del cierre) se agrega la misma llamada que ya hacía `gate`: `source = _gate_authority(state, project_root, execution_document["execution"])`. Reusado **sin** re-declarar ni tocar `_validate_v2_vigency` (INV-4) y sin tocar PD-8 ni el efecto del cierre. Con `hitl_delegation` revocado o vencido (por eventos o por `expires_on` ISO en el pasado) `_gate_authority` lanza `approval pending` **antes de cualquier escritura** → rc=2, marcador, nombrando el registro, state byte a byte idéntico (INV-7). Sin registro de delegación devuelve `None`: no se bloquea al dueño (P2) y el cierre sigue (rc=0).
2. **La nota de autoridad se comparte entre las dos clases.** Extraje el texto de los tres casos a un helper `_authority_note(state, source)` y lo usé en `gate` (reemplaza su bloque inline, **mismo texto exacto**) y en `closure`, para que `closure` **declare** su caso de autoridad igual que `gate` («no hitl_delegation registered … there is no delegation to verify»).
3. **Salida de `closure`:** `lines.append(authority_note)` junto a `approved_by`/`closure`.

Diff (extracto):
```diff
+def _authority_note(state, source) -> str:
+    """PD-6: the note BOTH approvals (`gate` and `closure`) print for the three
+    cases of the authority they consumed (`_gate_authority`). Shared so the two
+    classes declare the same thing …"""
@@ rama closure @@
+            source = _gate_authority(state, project_root, execution_document["execution"])
+            authority_note = _authority_note(state, source)
@@   if transition == "closure":
         lines.append(f"approved_by: {args.approve_by}")
         lines.append(f"closure: {closure_path} {closure_sha256}")
+        lines.append(authority_note)
```
No se agregó ninguna validación que exija campos nuevos a entradas históricas; sin delegación registrada el comportamiento es el de antes (rc=0) más la declaración.

## (b) Corridas y salidas (pegadas)

Baseline RED **antes** de tocar nada:
```
$ python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py -q
3 failed, 8 passed in 26.49s
```
Focal de B1 (ahora verde):
```
$ python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py -q
...........                                                              [100%]
11 passed in 20.49s
```
Focal de B2 (no romperlo):
```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py -q
.....................                                                    [100%]
21 passed in 37.10s
```
Resto de los focales (incluye T2, el de la autoridad de `gate`, que ahora comparte el helper):
```
$ python3 -m pytest tests/test_005_012_t2_gate_authority.py tests/test_005_012_t4_late_delivery.py tests/test_005_012_t5_approval_vigency.py tests/test_005_012_t6_open_context_guard.py -q
.............................                                            [100%]
29 passed in 54.42s
```
Regresiones declaradas por la ficha T3:
```
$ python3 -m pytest tests/test_005_001_t3_idle.py tests/test_005_003_f2_idle_history.py tests/test_005_007_t3_open_unit.py tests/test_003_002_t1_receive.py -q
....................                                                     [100%]
20 passed in 26.40s
```
State y compilación:
```
$ python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root .
VALID: execution=exec-005-012-transition-registration-001 feature=005-012-transition-registration model_policy=ordinary   (rc=0)
$ python3 -m py_compile skills/cdad-cycle/scripts/cdad_packet.py && echo "compile OK"
compile OK
```
La suite completa **no** se corre acá (política: la corre quien cierra).

## (c) Prueba de que `tests/` no se tocó

```
$ git diff --name-only 64a32d3..HEAD -- tests/
(vacío)
$ git show --name-only --oneline HEAD | tail -3
724ca3c feat: 005-012 review-fix B1 — PD-6 aplicada a closure (comprobacion de autoridad antes de cualquier escritura)
skills/cdad-cycle/scripts/cdad_packet.py
```
Queda `M docs/.cdad-state.json` en el árbol: **ya venía** modificado por el orquestador; no lo stageé ni commiteé.

## (d) El commit

```
$ git show --stat --oneline HEAD
724ca3c feat: 005-012 review-fix B1 — PD-6 aplicada a closure (comprobacion de autoridad antes de cualquier escritura)
 skills/cdad-cycle/scripts/cdad_packet.py | 41 ++++++++++++++++++++++----------
 1 file changed, 28 insertions(+), 13 deletions(-)
```

## (e) Interpretaciones y detenciones

1. **Posición de la comprobación dentro de la rama `closure`:** al **final** de las comprobaciones previas a la escritura (después de PD-8(a)/PD-8(b) y de resolver la cita), porque el código ya declara que PD-8 comprueba «antes que nada» y el encargo pide el control de autoridad «antes de cualquier escritura», no un orden relativo a PD-8. Ningún caso lo distingue (los casos 1/2 de B1 aislan la causa con PD-8 verde) y ambas comprobaciones ocurren antes de la única publicación atómica.
2. **La nota del caso C reusa el texto exacto de `gate`** vía el helper compartido (refactor sin cambio de comportamiento observable, verificado porque el focal de T2 sigue verde).
3. **No se tocó `_validate_v2_vigency` ni el mecanismo de vencimiento por fecha**: `_gate_authority` ya implementa los tres casos y el `expires_on` ISO en el pasado (D4/O4); `closure` lo consume tal cual. La exigencia de `--approve-by` no vacío para `closure` ya existía.
4. **Sin bloqueo (no hubo detención).** El contrato fue verificable y los tests no lo contradicen; el control positivo del caso C (P2/D-10) se conserva y no se asertó la vigencia del estado (deuda D-10, fuera de alcance). Ninguna escritura fuera del alcance; no edité ningún test.

**Anonimización:** sin rutas absolutas del dueño, sin ids crudos de sesión, sin nombres de otros proyectos.
