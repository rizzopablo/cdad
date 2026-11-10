# FINAL TEXT — implementer GREEN T3 (017-001-suite-performance): GREEN, focal + regresión + calibración real

## 1. Route C validation — PASS (before working)

- Dispatch carries only the identification block (no inline packet body → no route mixture): `packet_id` 017-001-suite-performance-implementer-green-004, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`.
- `validate-request` and `validate-packet`: exit 0. Canonical `render --request …` → `diff` limpio contra `PACKET.md` (`PACKET_MATCH`). Contract sha256 coincide con `sha256sum` del spec en disco. Execution context `schema_version: 2` → v2, Route C admisible.
- Trabajé sobre Route C, substage `green`, solo inputs/scopes del packet. Sin cargar `cdad-cycle` ni otro skill de ciclo. `tests/` solo lectura; único write scope `scripts/`. Contexto leído: `docs/systemPatterns.md`.

## 2. Implementation (solo `scripts/cdad-suite.py`, +773/−1)

Dos subcomandos nuevos, read-only sobre la evidencia (nunca reescriben el intento, nunca reejecutan pytest), según `t3-aggregator-contract.md` §§comandos/reglas/cobertura/entrada:

- **`reconcile --attempt --out [--register]`** → `reconciliation.json` + `reconciliation.md`, rc 0 producido / rc 2 entrada inutilizable (motivo por stderr nombrando `profile.json`/`attempt.json`). `S_test` = suma de `duration_s` por nodeid; atribuido = **unión** de intervalos `[started,finished]` de operaciones `owner_scope: test` de ese nodeid (anidados/solapados una sola vez, INV-5); resto = `S_test − atribuido` con signo; compartidas en bloque `shared` propio con su unión; `S_file` por archivo; `T_pytest/R_pytest/T_exterior/R_exterior` con signo, resolución declarada (`resolution`, `resolution_s`, `tolerance_s: 1e-3`) y `T_exterior` que acepta epoch numérico e ISO-8601 (los intentos reales usan `"2026-11-07T15:08:54Z"`, resolución 1 s declarada); tests y archivos por costo descendente con desempate por nodeid; JSON `sort_keys` sin timestamps → byte a byte determinista. Diagnósticos como códigos exactos: `profile-incomplete`, `capture-error`, `operation-error`, `attribution-exceeds-phases`, `residual-sign`, `scope-unavailable`, `scope-not-calibrated`, `missing-operation-vs-register`, `unexpected-operation`, `operation-without-register-entry`.
- **`entry-check --attempts --out [--register]`** → `entry.json` + `entry.md`, rc 0 satisfecha / 1 no satisfecha / 2 mapa o intento inutilizable (stderr no vacío). Seis checks nombrados del contrato evaluados y publicados: `register-calibrated`, `selection-coverage` (requeridas = `required_for_current_calibration != false`; extras fuera del registro fallan), `attempts-complete`, `counts-match-register`, `evidence-locatable`, `unknowns-declared` (`volume_observations.*.unknown_component.decision_rule`). Cobertura con `expected` entero o por selección/rama con `total`; selección propia de operación prevalece sobre la de familia; `all-required-selections` aplica a toda requerida; familias `state != comprometida` excluidas (criterio T2); `expected` cadena/ausente = desconocido, nunca cero.
- Puerta de calidad: guards al inicio, parseo en el borde (`_t3_parse_wall`, lectores con forma verificada), escrituras atómicas existentes reutilizadas, fallos de captura/entrada ruidosos (rc 2 / diagnósticos), nombres intencionales.

## 3. Evidence (comandos exactos, salidas conservadas)

- **Focal T3:** `python3 -m pytest -q -p no:cacheprovider tests/test_017_001_suite_reconcile.py` → **9 passed in 3.24s** (antes: 9 failed RED; verificado también sobre el árbol commiteado).
- **Focal T1:** `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **17 passed in 32.34s**.
- **Focal T2:** misma invocación sobre `tests/test_017_001_suite_operations.py` → **9 passed in 18.81s**.
- **Regresión proporcional** (ruta `close` compartida): `tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **49 passed in 54.71s**.
- **Calibración real** (8 selecciones, outs en `<tmp>/017-001-T3-green/`, intentos intactos — `READONLY_OK`): los 8 `reconcile` rc 0, `status=complete`, `diagnostics=none`, cobertura `available` con su selección inferida. Números (atribuido ≤ S_test, residuos positivos, sin doble conteo):
  - C-R: S=1.416 attr=0.356 resto=1.061; R_pytest=0.806 R_exterior=0.778
  - C-U4: top S=4.648 attr=4.633 resto=0.015; R_pytest=0.978 R_exterior=0.859
  - C-D: top S=13.710 attr=12.994 resto=0.717; R_pytest=3.576 R_exterior=1.731
  - Determinismo real verificado: `cmp` de dos reconciliaciones de C-R → `BYTE_IDENTICAL`.
- **Veredicto de entrada:** `entry-check` sobre el mapa de las 8 selecciones con el registro calibrado → **rc 0, `satisfied: true`**, los seis checks en `pass`, `diagnostics: []`.
- **Suite completa no realizada** (ciclo focal + regresión proporcional como rutina; sin autorización para completa).

## 4. Límites y rol (honestidad PD-15)

- `python3 scripts/cdad-suite.py validate` → rc 1 por el oráculo RED sin inventariar (`tests/test_017_001_suite_reconcile.py` + sus 9 nodeids). **Preexistente**: idéntico rc 1 con mi cambio stasheado; es deber de integración del orquestador (inventario fuera de mi write_scope) — lo reporto, no lo toco.
- `tests/` intacto (`git diff --name-only -- tests/` vacío); contrato intacto; `docs/.cdad-state.json` modificado preexistente del orquestador, dejado sin commitear.
- Commit: `2ccebd86` (`feat: implement T3 reconcile and entry-check aggregation (017-001)`, 1 archivo, solo `scripts/cdad-suite.py`).
