# FINAL TEXT — test-writer / post-audit · `010-004-packet-dispatch-ergonomics-test-writer-post-audit-005`

Route C validated (canonical render ≡ PACKET.md, all sha256 match, repository scripts, exit 0). Subfase única completada. Un solo archivo modificado: `tests/test_packet_prepare.py`, solo los tres tests nombrados.

## (1) Traza por test

| Test | Expectativa anterior | Requisito (PC-04/§4.1/§7) | Corrección aplicada |
|---|---|---|---|
| `TestPrepareEffects::test_p1_prepare_writes_three_files_and_stdout_equals_packet_and_render` | Snapshot `before` tomado **antes** de `args()`; literal esperado incluía `".cdad"` como creación de `prepare` (falso bajo la convención canónica: la fixture lo materializa al primer acceso de `execution_path`, dentro de `args()`) | PC-04 (:406) + §4.1 (localizador canónico); scope-correction **§2** | `args()` evaluado antes del snapshot; `run_prepare(PACKET_CLI, *args)` con el chequeo rc==0 conservado; `".cdad"` retirado del literal. Conjunto exacto e igualdades de bytes intactas |
| `TestPrepareFailureHasNoEffects::test_p4_unserializable_state_fails_without_effects` | `before = tree_snapshot(...)` antes de `project.args()` → la fixture "cambiaba" el árbol entre snapshots y la igualdad `tree_snapshot == before` fallaba sin promesa rota | §4.1/PC-04; scope-correction **§3** | `args` calculado antes de `before` y esos argumentos pasados a `run_prepare`. **Ni una aserción cambió** |
| `TestPrepareDefaults::test_p2_default_request_derivations_per_role` | Dict esperado del conjunto cerrado **sin** `execution_context` | **PC-04** (:406): «declara en request y cabecera su localizador canónico»; **§7** (:449-460) lista no exhaustiva; scope-correction **§4** | Clave añadida al dict esperado con el **valor canónico exacto** `".cdad/executions/{EXECUTION_ID}/execution.json"` (`exec-003-001-role-packets-001`), trazada en comentario a PC-04/§7. Igualdad exacta del documento conservada |

## (2) Prueba de NO-debilitamiento por oráculo

- **p1 — conjunto:** sigue siendo `assertEqual(added, sorted(...))` — comparación por igualdad de conjunto completa. Literal final: `[packet_dir_rel, request_rel, packet_rel, ".opencode", ".opencode/agents"] + [f".opencode/agents/{name}" for name in derived_names] + ([".cdad/.lock"] if lock_added else [])`. Sin subconjuntos, sin exclusiones de árbol, sin subconjunto-sidestep; la rama condicional `.cdad/.lock` y la promesa (tres archivos + `stdout == PACKET.md == render` + `validate-packet`) intactas.
- **p4 — árbol:** la igualdad `tree_snapshot(project.root) == before` sigue comparando **antes/después** con las mismas aserciones (`assert_clean_exit_2`, out-dir vacío, state byte-idéntico, sin `.tmp`).
- **p2 — conjunto cerrado:** el dict sigue siendo la igualdad **exacta** del `request` completo; `execution_context` entra con su valor canónico exacto (no presencia, no sufijo, no sustracción del campo). Auditoría del diff: `19 → 16` tests sin ningún cambio (los 3 hunks caen íntegros dentro de los tres tests nombrados); ninguna aserción añadida, quitada ni relajada fuera de ellos.
- **Fixture no tocada:** `StateFixture`, `PrepareProject.__init__`/`execution_path`, `test_role_packets.py` y todo otro archivo — sin cambios (verificación (b) y (c) lo confirman en ejecución).
- **Declaración honesta:** no leí implementación alguna (`skills/scripts/sources/agents/`); el trabajo derivó de la spec, los documentos declarados y los propios tests.

## (3) Conteos

| Verificación | Comando | Antes → Después |
|---|---|---|
| (a) archivo | `python3 -m pytest tests/test_packet_prepare.py -q` | `3 failed, 16 passed` → **`19 passed`** |
| (b) universo 14 archivos (13 C1 + `tests/test_004_002_t7_acceptance.py`) | una sola invocación `pytest <14 archivos> -q --tb=no` | `3 failed, 96 passed` → **`99 passed`**, 0 fallos |
| (c) 14 tests protegidos (6 RED T2 + 2 POST-AUDIT + 5 PC-08a + C3 f6), nombrados, una invocación | `pytest tests/test_010_004_t2_red.py <2 POST-AUDIT> <4 PC-08a> <CRLF> <f6> -q` | **`14 passed`** — y byte-idénticos por evidencia del diff (ningún hunk fuera de los tres tests) |
| (d) `git status --porcelain` tras commit | — | solo el untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md`, conservado tal cual |

## (4) Diff completo

`40 insertions(+), 6 deletions(-)` en `tests/test_packet_prepare.py` — reproducido completo arriba antes del commit y confirmado byte-identical en el commit (`git show 60fa29a1`).

## (5) Commit

```
60fa29a16e13b484a315566d14455b3b959e1a3a
test: cerrar oraculos residuales de T2 (010-004 POST-AUDIT -005)
```

## (6) Regresiones

Ninguna. El cierre del T2 queda en el estado exigido: archivo completamente verde y universo de 14 archivos sin fallos.

**Límites declarados:** la suite completa NO se corrió (política común del paquete: quien cierra la tarea la corre al cierre). Detengo aquí: es UNA subfase.