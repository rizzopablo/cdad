Tengo todo el material. Informe final:

---

# Informe de review — T1 `003-007-living-continuity` (diff `3b9dbf2..4e82ca4`)

**Rol:** reviewer (stage 4) · **Contrato:** `docs/specs/003-007-living-continuity/spec.md` — sha256 verificado: `3b4e8c4a…07c` ✅ coincide con el declarado en el packet · **Alcance:** P1, P2, P3, P4, P7, P8 (plan T1)

## Veredicto

**SIN HALLAZGOS BLOQUEANTES.** El diff cumple el contrato aprobado en las seis postcondiciones de T1. Los puntos adversariales que planteó el orquestador fueron verificados con sondas propias (no dados por ciertos); queda una deuda declarada y tres observaciones menores.

## Verificación del autor (lo que reclamé, no lo que afirmó)

| Afirmación del autor | Mi verificación | Resultado |
|---|---|---|
| GREEN `b1e56e9`: 50 passed / 2 failed | `git archive b1e56e9` → tmp → gate completo | **Reproducido exacto:** `2 failed, 50 passed` |
| Rojo 1 = defecto de test (P3 sin crear el archivo) | Re-corrida del test aislado en el archive | **Confirmado:** `begin` falla con `reference does not exist: fixture/work-ledger.md`, rc=1 — nunca llega a probar la clase |
| Rojo 2 = cambio de contrato declarado (exact-dict sin `class`) | Output del failure | **Confirmado:** `got [{'class': 'contract', 'path': …}]` vs esperado `[{path, sha256}]` |
| RED fix `4e82ca4` sin tocar producción | `git show 4e82ca4 --stat` | **Confirmado:** solo 2 archivos de tests (+31/−9) |
| Gate tras el fix | Re-corrida en el árbol (idéntico al árbol de `4e82ca4` salvo docs) | **52 passed** |

La decisión `t1-green-decision.md` (opción A: clase estampada en body, reflejada en head.json) es consistente con spec §3 ("la clase resuelta se estampa en el body") y con el código (`_checkpoint_envelope` incluye `references` en head.json, línea 594). Sin contradicción.

## Respuestas a las preguntas del orquestador (con evidencia)

**1. ¿Algún camino deja pasar un cambio de referencia `contract` sin rc≠0 (reconcile, trigger, fields)?** — **No encontré ninguno dentro del CLI actual.** Los tres comandos de lectura pasan por `_reference_reports` (líneas 974, 1129 vía `_frozen_budget`, 1231) **antes** de filtrar por rol y antes de emitir; `ContinuityError` → rc 1 (`main`, línea 1316). Sondas propias: reconcilie rc=1 y trigger rc=1 ante cambio de `hitl_delegation` proyectada con `fields` (delta cita path + digests esperado/real); file que se corrompe a no-JSON en lectura → rc=1 (bloquea). Progreso-only → rc 0. El único camino no-bloqueante es el **legado por comparación**, que es comportamiento de contrato (D6/P7), ver hallazgo O-1.

**2. P7: ¿un body nuevo sin class reconocible podría pasar por legado y no bloquear?** — **Sí, y la distinción no existe en el código.** La resolución es **por referencia** (`declared not in REFERENCE_CLASSES`, línea ~838), no por body: un body sin `class` en sus referencias se reporta `changed`/`missing` con `legacy: true` y **nunca bloquea**. Lo demostré con una sonda: store nuevo con clase eliminada del body+head (escritor deshonesto/regresado) + archivo divergido → **rc 0, state changed, legacy true**. Mitigantes: (a) la spec lo declara excepción explícita ("la clase de legado no está congelada", P7/D6); (b) el único escritor del contrato es este CLI, que estampa siempre vía `_digest_references` — el escape exige un escritor que lo esquive. **Veredicto: OPTIONAL, bucket l** (deuda declarada, no defecto observable). Remedio estructural: cuando T2 aterrice `record` en el body (P6), discriminar legado por **ausencia de `record` a nivel body**, no por referencia — un body nuevo sin `class` entonces fallaría cerrado.

**3. BL-3 (fields sobre no-JSON / proyección vacía):** verificado por código y tests. `_digest_references` (línea 619) corre **antes** de cualquier escritura (`_write_synced` en 651-654) → falla sin persistir nada (`_field_digest`, líneas 407-437; mensajes nombran el mecanismo, sin traceback). La sonda de `fields: []` también falla cerrado (`[] resuelve ninguna clave`). Correcto.

**4. P8 (`current_sha256`, `state` no filtran con `--role`):** `_reference_reports` bloquea sobre TODAS las referencias (correcto — P1 no es rol-dependiente); el filtrado ocurre solo en el render vía `_visible_references(report_list, role, policy)` (línea 1251), que filtra por `path`. Test `test_p08_*` + lectura del código: los campos nuevos viajan dentro de la entrada filtrada, no por separado. Sin fuga. Correcto.

**5. Fixture `tests/fixtures/003-007-legacy-store/`:** verificado: (a) es un store pre-003-007 **real** generado con el CLI pre-GREEN — el body congelado contiene `{"path","sha256"}` sin `class`/`record`; (b) **sin datos del repo**: la policy del fixture difiere de `docs/cdad-policy.json` real (sintética, forma reducida), cero rutas absolutas (`grep /home/|ofap` → vacío), execution_id sintético sin colisión con los stores reales (`exec-003-007-t1-red-001` vs `exec-003-004…`/`exec-003-006…`); (c) el forzado sobre `.gitignore:11 .cdad/` está **declarado** (ledger fila 6, commit `4ba979a`) y los archivos están trackeados (`git ls-files` los lista; `git check-ignore` sin `--no-index` no los reporta justamente por estar trackeados). Aceptable. Los tests copian a tmp (`copytree`), nunca leen `.cdad/` real.

**6. `continuity.md`:** el ejemplo declara clases en todas las referencias (`contract` para spec/plan/policy/state+fields; `living` para ledgers/debt) y la convención coincide con spec §1/§3 y D8/BL-1. Sin contradicción.

## Hallazgos

**BLOCKING: ninguno.**

| # | Severidad | Veredicto | Bucket | Hallazgo |
|---|---|---|---|---|
| O-1 | Required-deuda (ya declarada) | OPTIONAL | l | Legado por comparación es fail-open si un escritor nuevo omite `class` (demostrado, probe 3). Excepción documentada en spec P7. Remedio: en T2, discriminar legado por ausencia de `record` a nivel body. |
| N-1 | Nit | OPTIONAL | l | Estado `missing` para un archivo **existente** pero no-proyectable (`fields` + no-JSON en lectura, probe 1): la taxonomía `unchanged/changed/missing` lo reporta "missing" aunque el archivo existe. Bloquea correctamente (rc≠0), pero el diagnóstico es impreciso. Remediar con un estado `unreadable` o mensaje que lo distinga. |
| N-2 | FYI | OPTIONAL | l | `_resolve_reference_declaration` estampa `fields` sin trim: `[" a"]` con key `a` no resuelve y se silencia por campo (V2 lo permite: "solo las claves que SÍ resuelven"); el estampa congelado muestra el campo declarado aunque no protege nada. Por contrato (V2 fijado en RED), pero conviene documentar en `continuity.md` que un campo no resuelto protege cero. |
| N-3 | FYI | OPTIONAL | l | `begin`/`checkpoint` (comandos de escritura) no re-verifican las referencias `contract` del head previo al apender — dentro del scope de P1 de la spec (solo resume/reconcile/trigger), preexistente. Solo señal: el orquestador podría checkpoint-ear sobre una spec ya divergida. |

**Positivos verificables** (constatan, no endosan): P3/D2 sin clasificación por rutas está blindada por test (`test_p03_el_cli_no_deriva_la_clase_de_rutas`) y código (la ruta nunca se inspecciona); P5/P6 correctamente **ausentes** del diff (T2, plan); el RED fix respeta la separación de sesiones (solo tests); suite de 52 focal/registros verde; `_normalize_reference` (anti-traversal) intacto; el CLI sigue stdlib-only y determinista.

## Abstentions

- **P9 (rotación real sobre stores reales de 003-004/003-006):** es observable de T3 por diseño (R-3); no revisado aquí.
- **P5/P6 (T2):** no están en este diff — correcto por plan; no emití juicio sobre su futura implementación.
- **Suite completa:** no corrida (gate del orquestador lo prohíbe); las regresiones se limitan a los focales declarados en plan T1. Sin regresiones allí, pero no afirmo cero regresiones fuera de ese conjunto.
- **V5 (headroom 16 KiB):** medición pendiente según spec; sin claim en este diff — nada que revisar.
- **Autoría del commit `4e82ca4`:** el historial no permite confirmar en qué sesión se ejecutó el fix de tests (la decisión declara un paquete test-writer red-002; el state lo registra "prepared"). El contenido del commit (solo tests) es consistente con la separación declarada; la asignación de sesión es un registro del orquestador que no puedo verificar desde el repo.

## Evidencia

**Archivos modificados en el rango** (`git diff 3b9dbf2..4e82ca4 --name-status`): `docs/.cdad-state.json` (M), `dispatch-ledger.md` (M), `t1-green-decision.md` (A), `continuity-checkpoint.schema.json` (M, class/fields — sin `record`, scope T1 respetado), `references/continuity.md` (M, +49 con ejemplo), `scripts/cdad_continuity.py` (M, +201/−31), `tests/test_003_004_t1_checkpoint.py` (M), `tests/test_003_007_t1_reference_classes.py` (M).

**Comandos exactos:**
```
env -u TMPDIR python3 -m pytest -q tests/test_003_007_t1_reference_classes.py tests/test_003_004_*.py tests/test_003_006_t4_*.py < /dev/null   # → 52 passed
git archive b1e56e9 | tar -x -C /tmp/opencode/rv-b1e56e9 && (gate allí)   # → 2 failed, 50 passed
python3 /tmp/opencode/rv-probes/probe.py   # 6 sondas adversariales en tmp
```
Son >200k palabras de diff no; todas las escrituras de sondas quedaron en `/tmp/opencode/` (read-only sobre el producto; write_scope respetado: cero archivos modificados).

**Commits:** revisados `8de58c4`, `b1e56e9` (GREEN), `7fcee1d`, `5d02b4d`, `4e82ca4` (RED fix) en rama `codex/epic-003-context-efficiency`; HEAD actual `85ad9b4` (solo docs del paquete de review respecto a `4e82ca4` — verificado `git diff 4e82ca4 --stat`).
