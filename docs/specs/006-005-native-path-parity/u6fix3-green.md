## Informe — implementer, subfase GREEN (006-005 U6-3)

**Vía de intake:** packet validado (`006-005-native-path-parity-implementer-green-010`). No cargué skills de ciclo completas ni los insumos completos del ciclo: solo el contrato aprobado (`spec.md`), el informe RED (`u6fix3-red.md`), el hallazgo U6-3 (`execution.md`), los tests focales y el código de implementación dentro del write scope.

### Qué cambió y por qué

La evaluación de la llave «proyecto» de la vía nativa **vive en el núcleo** (`skills/cdad-cycle/scripts/cdad_dispatch.py`, `_membership_key` → `_key_states` → `correlate`); el módulo OpenCode solo entrega la fila observada (`--observe`), no la evalúa. Por eso el cambio es **de un solo archivo**.

| Antes | Después |
|---|---|
| `directory == raíz` o dentro ⇒ `match`; cualquier otra ⇒ `contradiction` | dentro de la raíz o la raíz ⇒ `match`; **ancestro de la raíz** ⇒ `not-evaluable` (evidencia en ninguna dirección, nombrada en el diagnóstico); ajeno ⇒ `contradiction` (rechazo) |

- `KEY_NOT_EVALUABLE = "not-evaluable"` (constante nueva con el fundamento §2.3/INV-15 + U6-3).
- `_membership_key`: guardas primero (`dir` ausente / no resoluble ⇒ `unknown`), luego las tres ramas. Función pura, sin mutación, mismo input → mismo output.
- `correlate`: lista `not_evaluable` separada; **no** bloquea la acreditación positiva que dan las llaves discriminantes (padre/momento) ni se cuenta como contradicción; se suma al diagnóstico nombrando la llave y la causa (ancestro). El **umbral O-3 no cambió** (`if not unknowns and matched`), las contradicciones siguen lanzando rechazo igual.
- Docstrings del módulo y de `correlate`/`_membership_key` actualizados para declarar los tres valores.
- La vía externa no se tocó.

### Archivos modificados

```
skills/cdad-cycle/scripts/cdad_dispatch.py | 49 +++++++++++++++++++++++++-----
1 file changed, 41 insertions(+), 8 deletions(-)
```
Nada de `tests/**`. Los no trackeados ajenos (`docs/planning/`, `findings/…`) quedaron intactos.

### Tabla test → resultado

| Test | Resultado |
|---|---|
| `u1b::TestPd5E1NativeProjectKeyU63::test_u63_ancestor_directory_with_a_matching_parent_is_verified` | **RED → GREEN** (era `AssertionError: 1 != 0` por rechazo `the project key does not match`) |
| `u1b::…::test_u63_ancestor_directory_without_a_discriminating_key_is_unknown_pd6` | **RED → GREEN** (era el mismo rechazo) |
| `u1b::…::test_u63_foreign_directory_is_a_rejection_naming_the_project_key` | Pasa (control: hermano ajeno sigue rechazo) |
| `u1b::…::test_u63_directory_inside_the_root_still_matches` | Pasa (control: pertenencia intacta) |
| Focal completo `tests/test_006_005_u1b_dispatch_entry.py` | **17 passed** |
| Todos los focales `tests/test_006_005_*.py` (10 archivos) | **96 passed** (en RED: 94 passed + 2 failed) |
| Regresiones de la ficha U1b (15 archivos) | **118 passed, 2 skipped** (skips declarados: PD-10 de `005-009_t4` y PD-8 de `005-010_t4`, que exigen binario/instalación real) |
| `make validate` | **168 PASS / 1 FAIL** — el FAIL es **F011** (`scripts/validate-subagents.sh`, perfil activo: drift de copia instalada), **preexistente y ambiental** |

### Comandos con salida

```
$ git log --oneline -1
6068588 docs(state): 006-005 U6-3 GREEN preparado

$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py -q -k u63
2 failed, 2 passed, 13 deselected in 3.33s        # RED reproducido (AssertionError del rechazo)

$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py -q -k u63
4 passed, 13 deselected in 3.96s                  # GREEN

$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py -q
17 passed in 19.83s

$ python3 -m pytest tests/test_006_005_u1a_runtime_config.py … u7_scribe_role_report.py -q
96 passed in 109.36s (0:01:49)

$ python3 -m pytest tests/test_005_009_t1_interface.py … tests/test_packet_prepare.py -q
118 passed, 2 skipped in 241.00s (0:04:01)

$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
make: *** [Makefile:22: validate] Error 1
```

**F011 declarado (gate ambiental):** verificado contra **HEAD sin mi cambio** (copia del árbol con `cdad_dispatch.py` restaurado a HEAD, fuera de mi working tree): `Assert PASS: 168 / Assert FAIL: 1` — **idéntico**, mismo F011. No es regresión de esta unidad.

### Comportamiento bajo carga (declarado, no oculto)

En dos de las cuatro corridas del set de regresiones, `tests/test_006_001_t1_selection.py` falló por *timing* (`TestPd4SameErrandInServerMode`: `'timeout' != 'completed'`, cota observada 0.285 s con `settle_seconds: 0.3`), con **test distinto en cada corrida**. No es atribuible a este cambio: ese archivo **no invoca `cdad_dispatch.py`** (`grep -c cdad_dispatch` = 0) y **falla igual en HEAD** — la copia de HEAD falló 4 y luego 2 tests de ese archivo en dos corridas, y el test puntual pasa 3/3 en HEAD, en el árbol con el cambio y en el árbol original una vez que la carga bajó (load average 9.2/8 cores durante las fallas). Dejo la observación registrada; no sustituí ninguna corrida.

### Commit

```
$ git commit -m "fix: 006-005 U6-3 — llave proyecto de la vía nativa: ancestro no evaluable"
[main e7c39a5] fix: 006-005 U6-3 — llave proyecto de la vía nativa: ancestro no evaluable
 1 file changed, 41 insertions(+), 8 deletions(-)

$ git status --porcelain
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
```
Sin `--no-verify`, sin `git stash`, sin push. Suite completa **no** ejecutada (política declarada: la corre quien cierra).