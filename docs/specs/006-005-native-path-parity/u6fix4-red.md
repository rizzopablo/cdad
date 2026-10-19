## Resultado

RED de U6-4 escrito, ejecutado y commiteado. **8 tests fallan por `AssertionError` de conducta y 1 guard declarado pasa**; ningún fallo es `ImportError`, `SyntaxError` ni error de fixture. No leí código de implementación: la entrada y el módulo real se ejecutan como procesos desde una copia staged del skill tree, con `XDG_CONFIG_HOME`/`HOME` temporales.

## Archivo

- **Nuevo:** `tests/test_006_005_u6fix4_native_selection.py` (906 líneas, 9 tests).

Fixture: proyecto descartable (`build_project` + `prepare` test-writer/red), copia staged de `skills/cdad-cycle` con el **módulo real** `cdad_delegate_opencode.py` junto a la entrada, sección `opencode` en `runtimes.json` temporal, binario falso que reporta la versión configurada, y store SQLite descartable con la forma real de V-7 ampliada: `time_created INTEGER NOT NULL` en **milisegundos epoch**, `parent_id`/`agent` TEXT, `directory TEXT NOT NULL`. Ninguna invocación usa `--session` en los casos de selección.

## Mapa test → PD

| Test | PD / caso | Qué fija |
|---|---|---|
| `test_u64_verified_child_inside_the_root` | PD-5/E1 (U6-4) — (a) | hijo único, agente del paquete, ms posterior a `--since`, directorio dentro de la raíz ⇒ verificada con el id del store + entrega byte-exacta |
| `test_u64_ancestor_directory_is_verified_by_parent_and_moment` | PD-5/E1 (U6-4) + U6-3 — (a) variante | directorio ancestro ⇒ verificada por padre+momento; proyecto **no evaluable y nombrado** |
| `test_u64_same_agent_child_before_since_is_not_a_candidate` | PD-5/E1 (U6-4) — momento (derivado de a/d) | dos hijos del mismo agente, uno anterior y uno posterior a `--since` en **ms** ⇒ un solo candidato (discrimina ms vs segundos vs no interpretable) |
| `test_u64_earlier_child_of_another_role_is_not_a_candidate` | PD-5/E1 (U6-4) — (b) | hijo anterior de otro rol insertado primero ⇒ verificada sobre el hijo del paquete; nunca rechazo |
| `test_u64_two_candidates_are_ambiguous_and_never_accredited` | PD-5/E1 (U6-4) + PD-6 — (c) | dos candidatos ⇒ `session: null`, ambigüedad nombrada, sin rechazo; con resultado nativo hay entrega |
| `test_u64_no_candidate_earlier_child_is_not_a_rejection` | PD-5/E1 (U6-4) + PD-4 — (d), **GUARD declarado** | único hijo anterior a `--since` ⇒ no se acredita, sin rechazo; sin texto final no hay entrega |
| `test_u64_no_candidate_other_agent_with_native_result_delivers_under_pd6` | PD-5/E1 (U6-4) + PD-6 — (d) | único hijo de otro agente ⇒ no acredita ni contradice; con nativo byte-exacto rige PD-6 |
| `test_u64_uninterpretable_instant_is_named_as_such` | PD-5/E1 (U6-4)/O-6/INV-4 — (e) | `time_created` ilegible ⇒ no acredita y el diagnóstico lo nombra **no interpretable** (no vale la frase del ancestro) |
| `test_u64_unverified_note_names_the_keys_that_matched` | PD-5/E1 (U6-4) — (f) | nota no verificada nombra las llaves que sí coincidieron (`parent`) |

Los oráculos son sólo conducta observable: rc, JSON del sobre, registro I8, entrega escenificada y ausencia de descriptor/recibo. No dependen de qué lado filtra.

## A-1

**No hubo reformulaciones.** Lo declaro explícitamente en el encabezado del test:

- `tests/test_006_005_u2_opencode_module.py` fija `time_created REAL` = `time.time() - 5.0` (:1117-1123, :1179-1186), pero sus aserciones **no dependen de la unidad**: el caso de observación pinea la fila con `--session` y verifica el id devuelto (:1125-1143); el de PD-13 verifica bytes del store y `store_reads` (:1177-1209). Ninguno compara un instante contra `--since`.
- Ningún test fija como conducta de producto «tomar el primer hijo bajo el padre»: el módulo de U1b es un **stub de fixture** de la superficie del módulo, no la selección bajo prueba.

## Comandos y salida

```
$ python3 -m pytest -q --tb=line tests/test_006_005_u6fix4_native_selection.py
FFFF.FFFF                                                                [100%]
...
AssertionError: None != 'ses-u64-inside-0001' ...        (verificada)
AssertionError: None != 'ses-u64-ancestor-0001' ...      (ancestro)
AssertionError: None != 'ses-u64-after-0001' ...         (ms antes/después)
AssertionError: 1 != 0 : U6-4 (b) ... rc=1 agent contradiction
AssertionError: 1 != 0 : U6-4 (d) ... rc=1 agent contradiction
AssertionError: Regex didn't match ... AMBIGÜEDAD ...
AssertionError: Regex didn't match ... NO INTERPRETABLE ...
AssertionError: Regex didn't match ... llaves que SÍ coincidieron ...
8 failed, 1 passed in 10.30s
```

```
$ python3 -m pytest -q tests/test_006_005_*.py
8 failed, 97 passed in 124.08s (0:02:04)
```

Los 8 fallos son del archivo nuevo; los otros 97 tests `tests/test_006_005_*.py` siguen verdes. El guard `(d) único hijo anterior` pasa hoy porque el momento es `unknown` por la razón defectuosa; queda discriminante al leer la unidad real (segundos ⇒ candidato falso).

## Commit

```
8fe0d8c test: 006-005 U6-4 RED — momento en ms y selección del candidato nativo
 tests/test_006_005_u6fix4_native_selection.py | 906 ++++++++++++++++++++++++++
 1 file changed, 906 insertions(+)
```

Sólo `tests/`. Los untracked `docs/planning/` y `findings/incremental-construction-and-reproducible-validation-2026-10-17.md` quedaron fuera.

## Declaraciones honestas de alcance

- Leí la sección «006-005 U6: recorrido real» / hallazgo U6-4 de `docs/epics/epic-006-opencode-concurrency/execution.md`, que el objetivo cita como fuente. Está fuera del `read_scope` del packet (contract root + tests), pero es documentación y venía declarada en el enunciado.
- Para ubicar el runner grepeé el `Makefile`; no es implementación y no se usó para derivar aserciones.
- **No abrí** `skills/cdad-cycle/scripts/*.py`: la entrada y `cdad_delegate_opencode.py` se copiaron sin inspección y se ejecutaron como procesos.