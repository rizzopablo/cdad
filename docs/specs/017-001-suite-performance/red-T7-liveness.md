Verificación completa, sin discrepancias. Entrego el FINAL TEXT.

---

# FINAL TEXT — test-writer RED-030 (017-001-suite-performance, T7)

## Validez del packet (ruta C)

- Identificación recibida `017-001-suite-performance-test-writer-red-030` comparada contra el render canónico: `render` coincide byte a byte con `PACKET.md`, `validate-packet` rc=0, `validate-request` rc=0, `render --route C` reproduce exactamente el bloque de identificación recibido (sin mezcla de rutas: cero marcadores inline en el dispatch).
- Contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e` verificado contra el archivo. `execution.json` con `schema_version: 2` (contexto v2, admitido). Metadata (packet_id, contract+sha, execution_id) coincidente en las tres piezas.
- Alcances respetados: leídos solo los tres inputs declarados (spec, `performance/parallelism.md`, el oráculo); editado solo `tests/`; **implementación (`scripts/`) nunca leída** — el runner se ejercitó como caja negra vía CLI, que es la acción ordenada por el packet. No se cargó `cdad-cycle` ni ningún otro skill de ciclo: el packet validado fue el contrato de ejecución.

## Corrección aplicada (commit `2981f9aa`, solo `tests/`)

En `tests/test_017_001_suite_parallel.py`, los **6 timeouts de liveness que acotan una invocación anidada de `cdad-suite.py parallel`** pasaron de `120` literal a `TIMEOUT_S` (=300, convención de la familia):

1. `test_parallel_cleans_process_family_without_cmdline_marker` (N1): `_run(..., timeout=TIMEOUT_S)`.
2. `test_parallel_altered_checkout_canary_rejects_run` (N2): `communicate(timeout=TIMEOUT_S)` + mensaje de diagnóstico interpolado con `TIMEOUT_S`.
3. `test_parallel_detects_session_escaped_descendant_and_discards_run` (O1): `_run(..., timeout=TIMEOUT_S)`.
4. `test_parallel_checkout_fingerprint_detects_same_size_same_mtime_rewrite` (O2): `communicate(timeout=TIMEOUT_S)` + mensaje interpolado con `TIMEOUT_S`.
5. `test_parallel_accepts_cdad_tmp_subdir_churn_without_content_change` (Q1, el que falló en el segundo intento T7): `_run(..., timeout=TIMEOUT_S)`.
6. `test_parallel_transient_child_within_grace_window_is_accepted` (P1): `_run(..., timeout=TIMEOUT_S)`.

Sin cambios de promesas, asserts ni selección: el diff commiteado (9 inserciones, 8 eliminaciones) contiene **cero líneas que toquen `assert`, nodeids, `NODEIDS` o definiciones de tests**; la colección sigue en **18 tests**. Intactos: `M1_TIMEOUT_S=90`, todos los `proc.wait(timeout=30)` y el `timeout=30` de la sonda `ps` (waits cortos sobre procesos ya lanzados). Los `sleep 120` restantes son payload de la sonda O1, no timeouts.

## Prueba bajo contención real (no en aislamiento)

Comando exacto (sobre el commit `2981f9aa`, selección de 27 nodeids = archivo paralelo completo de 18 tests + compañero pesado `tests/test_017_001_suite_operations.py` de 9 tests):

```
python3 -m pytest tests/test_017_001_suite_parallel.py tests/test_017_001_suite_operations.py --collect-only -q | grep "::" | sort -u > /tmp/red030/nodeids   # 27 nodeids
mkdir -p /tmp/red030/evidence
python3 scripts/cdad-suite.py parallel --workers 2 --evidence-root /tmp/red030/evidence --nodeids /tmp/red030/nodeids
```

Resultado (`/tmp/red030/outer_rc.txt`, `/tmp/red030/evidence/parallel.json`):

- **Tests: 27, rc=0, 27 passed / 0 failed / 0 skipped, veredicto `accepted`**.
- Pared total `total_wall_s=175.67 s` (pared exterior medida por fechas: 183 s, 10:22:19Z→10:25:22Z; la diferencia es arranque del comando).
- Worker 0 (los 18 meta-tests): 175.67 s. Worker 1 (companion): 13.01 s.
- `checkout_canary.unchanged=true` (20439 archivos, 450419748 bytes, huella `60b33cf3…`, costo 3.08 s); `orphans=0`, `orphans_found=7` (transitorios gestionados), `children_terminated=true`.

Duración observada de cada corrida anidada bajo contención (fase `call` de cada test del worker 0 en `worker-0/profile.json`, cota superior de la corrida anidada; 18/18 valores):

- **máximo 20.55 s** (`..._cleans_process_family_without_cmdline_marker`), **mediana 9.13 s**, mínimo 0.69 s (test de conteos inválidos, sin anidada).
- Q1 bajo carga: 8.47 s (vs 7.36 s en aislamiento). Margen contra `TIMEOUT_S=300`: el peor caso observado está a ~15× del techo.
- Conclusión: ninguna corrida anidada supera `TIMEOUT_S` bajo esta carga; **no se sube ningún timeout** — el techo de 300 s queda con margen amplio y justificado por medición, no a ciegas.

## Coincidencia de números

Verifiqué cada cifra del reporte del orquestador contra los artefactos: RC=0, WALL_S=183, 27/0/0, `accepted`, 175.7 s vs 13.0 s, canario sin cambios, 0 huérfanos con 7 transitorios — **todo coincide, sin discrepancias**.

## Límites declarados

- Suite completa no realizada: corrida focal de 27 tests bajo contención (autorizada por este packet); no se acredita verde de suite completa.
- Las duraciones anidadas provienen de fases `call` del perfil del worker 0 (incluyen overhead del test además de la CLI anidada): son cotas superiores honestas, no paredes internas exactas.
- Evidencia de la corrida en `/tmp/red030/` (scratch fuera del checkout, no entra al repo); el árbol queda con el commit `2981f9aa` limitado a `tests/`. El `M docs/.cdad-state.json` del working tree es preexistente y ajeno a este rol — no tocado ni commiteado aquí.
- Ausencia de lecturas de implementación declarada honestamente (límite: guard por nombre ≠ sandbox; la CLI se ejecutó como caja negra según lo ordenado).
