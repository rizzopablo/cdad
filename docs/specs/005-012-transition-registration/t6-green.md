# Informe GREEN — 005-012 T6 (`prepare --new-execution` rechaza el contexto abierto y sin uso)

**Rol:** implementer · **Etapa 3, subetapa `green`** · **Tarea:** T6 · **PD:** PD-16 (con PD-17/INV-7 de soporte)
**Paquete:** `005-012-transition-registration-implementer-green-006` · **Ejecución:** `exec-005-012-transition-registration-001`
**Contrato leído:** `docs/specs/005-012-transition-registration/spec.md` §2.3 PD-16 / §2.4 INV-7 y PD-17; oráculo rojo `docs/specs/005-012-transition-registration/t6-red.md`; ficha T6 en `plan.md` §4; focal congelado `tests/test_005_012_t6_open_context_guard.py`.

## (a) Qué implementé y dónde

**Único archivo modificado (implementación): `skills/cdad-cycle/scripts/cdad_packet.py`** (+72 líneas, sin borrados ni cambios de comportamiento fuera del guard). Nada más se tocó: **cero** archivos de `tests/`, cero documentación, cero `agents/`/`build/`.

Dos piezas nuevas, ambas **read-only**, más el punto de rechazo:

1. `_packet_cites_execution(project_root, execution_id) -> bool` — ¿hay algún paquete publicado en `.cdad/packets/*/REQUEST.json` cuyo `execution_id` (el registro canónico que el CLI relee en `--resume-packet` y en el despacho) sea el del contexto? Un `REQUEST.json` ilegible **no** cuenta como uso (una publicación interrumpida se recupera en `prepare`, PD-11/I5), de modo que no se inventa uso.
2. `_open_unused_context(project_root, state) -> str | None` — devuelve el id del contexto v2 **abierto y sin uso** de la feature activa, o `None`. «Abierto»: `state.execution` apunta a un contexto **v2** con archivo en `.cdad/executions/<id>/execution.json` y `execution.feature_id == state.active_feature`. «Sin uso»: ni paquete que lo cite (punto 1) ni registros de despacho (`_dispatched_packet_ids` — la noción derivada que ya usa el cierre, PD-8(a)). Salidas tempranas en cada disyuntor; si el binding no está respaldado por un contexto legible, devuelve `None` (aditividad: sin la condición del guard, `prepare` se comporta como hoy).
3. **Punto de rechazo** en `_select_execution`, en la rama de `--new-execution` y **antes** de `_next_execution_id`/`_bootstrap_v2_execution` — es decir, antes de cualquier escritura (INV-7, byte a byte idéntico) y sin acuñar un segundo id:

```
ERROR: state incoherent: the execution context .cdad/executions/exec-005-012-t6-open-context-fixture-001/execution.json of feature '005-012-t6-open-context-fixture' is already open and unused (no packet published with its execution_id and no dispatch record); a second context would leave it orphaned. Use the open context, or prepare without `--new-execution`
```

(rc=2; marcador `state incoherent`; nombra el contexto abierto; dice cómo seguir: usar el contexto abierto o preparar sin `--new-execution`.)

**Aditividad:** el camino de reuso (sin `--new-execution`) no pasa por el guard; el camino de contexto explícito (`--execution-context`, incluido su rechazo v1 de PD-10) queda intacto porque el guard vive después de esa rama; `open-unit` y el resto de las precondiciones de `prepare` no se tocaron. Comentarios en inglés, diagnostico accionable en el estilo existente.

## (b) Corridas y salidas (pegadas)

**Focal de T6 — `python3 -m pytest tests/test_005_012_t6_open_context_guard.py -q`**
```
...                                                                      [100%]
3 passed in 3.50s
```
(los 3: el caso del contrato **rc=2** + los dos controles positivos.)

**Focales T1..T5 — `python3 -m pytest tests/test_005_012_t1_register_transition_base.py tests/test_005_012_t2_gate_authority.py tests/test_005_012_t3_closure_dispatch_resolution.py tests/test_005_012_t4_late_delivery.py tests/test_005_012_t5_approval_vigency.py -q`**
```
.................................................                        [100%]
49 passed in 62.68s (0:01:02)
```

**Regresiones declaradas por la ficha — `python3 -m pytest tests/test_004_002_t2_bootstrap.py tests/test_packet_prepare.py tests/test_005_007_t3_open_unit.py -q`**
```
..........................................                               [100%]
42 passed in 28.53s
```

**Regresión proporcional extra (no declarada, la que el cambio exige):** el único otro consumidor vivo de `--new-execution` con contexto previo v2 es `test_004_002_t4_dispatch.py` (uso legítimo: la ejecución 1 **usada** se cierra y el dueño abre la 2). Corrí además los dos archivos que nombran `--new-execution` en rechazos de argv:
`python3 -m pytest tests/test_004_002_t4_dispatch.py tests/test_005_001_tcorr.py tests/test_004_002_t2_reviewfix.py -q`
```
...........................................                              [100%]
43 passed in 37.40s
```

**No corrí la suite completa:** la política declarada en el paquete dice que la corre una vez quien cierra.

**Evidencia del rechazo (sonda descartable fuera del repo, reutilizando el fixture congelado como caja negra):**
```
open context in state: exec-005-012-t6-open-context-fixture-001
active feature: 005-012-t6-open-context-fixture
returncode: 2
stdout: ''
stderr: ERROR: state incoherent: … (el diagnóstico de arriba)
executions dir after: ['exec-004-002-…-bootstrap-001', 'exec-005-012-t6-open-context-fixture-001']
```
→ rc=2, y `.cdad/executions/` **no creció**: ningún segundo id acuñado.

## (c) Prueba de que `tests/` no se tocó

```
$ git diff --name-only 4b8bf5c..HEAD -- tests/
[sin salida]
$ git show --stat --oneline HEAD
721990f feat: 005-012 T6 GREEN — prepare --new-execution rechaza el contexto abierto y sin uso (PD-16)
 skills/cdad-cycle/scripts/cdad_packet.py | 72 ++++++++++++++++++++++++++++++++
 1 file changed, 72 insertions(+)
$ git status --short
 M docs/.cdad-state.json      # del orquestador (despacho del paquete), NO mío, NO commiteado
```
El focal está intacto y sigue siendo el oráculo: no lo edité ni lo regeneré.

## (d) Commit

`721990f` — `feat: 005-012 T6 GREEN — prepare --new-execution rechaza el contexto abierto y sin uso (PD-16)` · 1 archivo (`skills/cdad-cycle/scripts/cdad_packet.py`), 72 inserciones, 0 borrados. El `docs/.cdad-state.json` modificado en el working tree **no** es mío y **no** se commiteó.

## (e) Interpretaciones y condiciones de detención

- **`feature_id` del contexto vs `active_feature`:** interpreté «de la feature activa» como igualdad estricta entre `execution.feature_id` del contexto v2 vinculado y `state.active_feature`; un contexto de otra feature no dispara el guard (declarado, no ampliado).
- **«Sin registros de despacho»:** usé la noción ya derivada del repo (`_dispatched_packet_ids`, PD-8(a): registros `*.json` con `packet_id` bajo `.cdad/executions/<id>/dispatches/`). Un directorio vacío o con contenido que no son registros no cuenta como uso; un `REQUEST.json` ilegible tampoco (se recupera en `prepare`, PD-11/I5). En ambos casos la decisión es **conservadora** (no dispara el guard = comportamiento de hoy), para no bloquear un uso legítimo.
- **Caso 4 (contexto abierto CON uso) y contexto creado por otra vía:** fuera de alcance por la ficha (límite D-5); no lo cubrí ni lo aserté, como declara el oráculo rojo.
- **Aditividad verificada:** el control positivo del focal (proyecto sin contexto previo → rc=0, acuña un id y publica) y el camino de reuso siguen verdes; las regresiones declaradas y la extra también.
- **NO me detuve:** la condición de detención de la ficha («si el rechazo bloqueara un uso legítimo de `--new-execution`») **no se cumplió** — el control positivo sigue en verde y el uso legítimo con contexto **usado** (`test_004_002_t4_dispatch.py`) también. No hubo bloqueos de alcance ni de permisos; no toqué `tests/**` en ningún momento.
