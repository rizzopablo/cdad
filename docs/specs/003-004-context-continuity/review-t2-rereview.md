## Dictamen por hallazgo

| Hallazgo | Veredicto | Bucket | Evidencia del cierre |
|---|---|---|---|
| **A** — señal perdida en `expired-authority` | **CERRADO** | m | `_run_reconcile` agrega `signals` (receipt state/effect/`semantic_status`, materialization, dispatch); `unknowns` siempre preservados; clasificación dominante intacta; rc 0. RED falla por la razón correcta (sin `signals`), GREEN pasa ambos subTest (vencido+received+closed → señales reportadas; receipt ilegible → `unknowns[]` no vacío pese a `expired-authority`) |
| **B** — render de `resume` reclama contrato que viola | **CERRADO** | m | Ningún render (frío/caliente) reclama `continuity-checkpoint-v1`: sin clave `checkpoint` y sin la cadena en el render (aserciones en ambos archivos de test); frío → `state: "no-checkpoint"` rc 0. Enmienda de `test_p02` **declarada** en docstring del RED y ledger #16; verificada: falla en `02bc021` por la razón del defecto, pasa en `00dd557` |
| **C** — `--packet` sin validar (traversal + oráculo alimentable) | **CERRADO** | m | `_safe_segment(args.packet, "packet")` en `_run_reconcile` y `_safe_segment(packet_id, "update.packet_id")` en `_require_key_fields` (cubre `begin` y `checkpoint`). `../../x`, `..`, `a/b` → rc≠0 en los tres comandos, campo nombrado, store byte-intacto / nada persistido. Cerrado **antes de T3** como pedía la decisión ✓ |
| **D** — `_write_synced` sin fsync | **CERRADO** (por lectura, como se dispuso) | m | fsync de archivo + dir-fsync tras rename; tolerante a FS restrictivos. Sin test de crash — conforme a la decisión |
| **E1** — `decision: ""` admitida | **CERRADO** | m | `decision` no vacía tras strip (hermana de `rationale`); `""` y `"   "` → rc≠0 en `begin` y `checkpoint`, campo nombrado, nada persistido. RED→GREEN verificado |
| **E2** — focales `reconcile` de los 3 negativos P1 restantes | **CERRADO** (cierre de letra) | l | Focal cubre cadena rota (`prev_checkpoint_sha256`), referencia inexistente (path nombrado) y digest de referencia alterado → rc≠0, delta que nombra el elemento, y `reconcile` no repara el head alterado. Ya estaba verde sobre `02bc021` (el mismo `_verify_*` corre desde `reconcile`); el ledger lo declara así (#16) y la decisión lo pedía como cobertura, no como cambio de comportamiento — consistente |

**Residuos de clase B/A/C/D/E1/E2 originados por el diff de cierre: ninguno detectado.** La pauta E3 se respeta: en la serie, `.cdad-state.json` solo cambia en commits de bookkeeping (`e0eb97c` docs, `bf03157` chore), nunca en los commits de feature (`2209841` tests-only, `00dd557` script-only).

## Nuevos hallazgos (solo misma clase, por mandate focal)

1. **Cobertura del reclamo `record: active-record-v1` (clase B, cobertura) — Nit · Verdict: OPTIONAL · Bucket: l.** Los renders de `resume` ahora portan el único reclamo de contrato que queda (`record: active-record-v1`), pero ningún test valida ese reclamo contra `active-record.schema.json` (el `jsonschema` del reviewfix solo está cableado a la rama fría-que-reclama-checkpoint). Mis probes (comando 8) muestran conformancia real en frío y caliente hoy, así que **no hay defecto observable** — es la letra del mismo patrón B sin test. Remedio barato en T3: un focal `jsonschema.validate(projection, active-record.schema.json)` para frío y caliente.
2. **`TestASenalesEnExpiredAuthority` llama `self.setUp()` manualmente dentro del test (Nit · OPTIONAL · l).** Funciona (los `addCleanup` se acumulan y cada re-setup encierra su tmp), pero es acoplamiento frágil; un método helper `reset_project()` sería más directo. Menor.
3. **Asimetría de etiqueta en el guard de C (Nit · OPTIONAL · l):** `reconcile` reporta `"packet"` y `begin`/`checkpoint` `"update.packet_id"` en el mensaje de error. Inconsistencia cosmética; el test de C exige `packet_id` en la salida de `begin`, no de `reconcile` — cubierto tal como está.

Ninguno escala a BLOCKING: no hay defecto observable actual, solo deuda de cobertura/estilo.

## Abstentions

1. **Suite completa (508) no re-corrida** — el paquete acota a focales T1+T2 (los 21 + los 8 del reviewfix + p02 enmendado = todo lo corrido, en verde). Evidencia de la corrida completa: ledger #14/#16 (implementer/test-writer, stdin cerrado, foreground).
2. **Disciplina RED del T2 original (`d14d80d`)** — fuera del foco de esta re-review; abstención heredada de review-t2 sin cambios.
3. **Interpretación del FAIL F011** en mi checkout (`install.sh --check` por `build/staging/manifest.json` ausente en árbol limpio) vs. los 2 FAIL del autor (141/2): la diferencia se explica por artefactos no-trackeados del repo real; no diagnosticé el estado de las copias instaladas en `$HOME` — per decisión, los F011/A3 se tratan al cierre del epic, fuera de 003-004.
4. **El FAIL F011/A3** — los validadores corrieron; el FAIL residual es `install.sh --check` preexistente y ajeno a 003-004 (decisión del orquestador: "se tratan al cierre"). No adjudico drift de copias instaladas.

## Evidencia de auditoría

- **Archivos modificados por esta revisión: ninguno** (`write_scope: []`; el checkout de verificación y los probes viven en `/tmp/opencode/verify-t2rf/` y `/tmp/opencode/probe_b_*.py`, fuera del repo; `git status` del repo real queda como estaba — solo la modificación preexistente de `docs/.cdad-state.json` del orquestador).
- **Commits evaluados:** `502a01f`, `e0eb97c`, `2209841` (RED), `bf03157`, `00dd557` (GREEN); **ningún commit emitido** por esta revisión.
- **Dictamen:** los 6 hallazgos focal (A, B, C, D, E1, E2) **están cerrados y verificados** con RED→GREEN reproducible, enmienda de `test_p02` declarada y fiel; sin regresiones en los 21 focales pre-rango; sin residuos nuevos de las mismas clases (solo 3 Nits de cobertura/estilo, no bloqueantes); el único FAIL de validador es el F011 preexistente pactado para tratamiento al cierre. Sin bloqueantes; listo para que el orquestador decida el paso a T3.
