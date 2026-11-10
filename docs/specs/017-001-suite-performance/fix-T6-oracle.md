Work complete. FINAL TEXT report below.

---

# FINAL TEXT — test-writer RED fix T6 (017-001-suite-performance), packet `017-001-suite-performance-test-writer-red-023`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación del dispatch (`packet_id …-test-writer-red-023`, `execution_id exec-017-001-suite-performance-001`, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json --execution-context …/execution.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md --execution-context …` → **EXIT 0**.
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**, sin switch silencioso. Cero marcadores inline en el prompt → sin mezcla route A/C. **No se cargó `cdad-cycle`, `cdad-spec-and-test` ni otro skill de ciclo**: el packet es el contrato.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e` ✓.
- Solo leí insumos declarados (`spec.md`, `green-T6-parallel.md`, los 3 tests) más el helper bajo `tests/` (`suite_operation_markers.py`, alcance tests) y el directorio de la spec para el formato del delta. Solo edité el write_scope (`tests/`). **No toqué `scripts/` ni el contrato.**

## 2. Cambios entregados (mapeo a postcondiciones, sin tests nuevos — R2: la promesa no cambió)

**Commit:** `2acaa250` — solo los 3 archivos (`M docs/.cdad-state.json` es del orquestador, quedó fuera del commit).

- **D1 — nodeid inexistente (PC-10, promesa E):** `tests/test_017_001_suite_parallel.py:39` decía `…_emit_branch_and_stays_neutral`; el real es `…_emit_branch_and_stay_neutral` (verificado contra `tests/test_017_001_suite_tranche2.py:64`). Una palabra, sin cambio de promesa.
- **D2 — `assert not is_active()` global (PC-1, promesa A):** en `tranche1.py`/`tranche2.py` la aserción inicial se reformuló en rama condicional **sin debilitar la promesa**:
  - Sin sumidero externo: se exige la neutralidad como hoy (`assert not is_active()` con mensaje).
  - Con sumidero externo (observador del suite desde arranque de sesión): no se exige ausencia; se verifica (a) que el contexto `observed()` propio recibe sus eventos —los asserts existentes de begins/ends/ramas/nodeid corren en ambas ramas y prueban coexistencia—, (b) que el resultado de la frontera es idéntico —igualdad pre/post `observed()` existente—, y (c) **nuevo**: relectura explícita con solo el externo conectado (`later == first` en tranche1; las 4 fronteras en tranche2) que demuestra que el sumidero ajeno no altera el valor.
  - **Blindaje del `finally`:** `observed()` ya retira el sumidero propio; el `detach()` final quedó guardado por `if not external_sink_present` —sin externo es el no-op de siempre; con externo **retiraría el sumidero ajeno del observador y corrompería la medición de la sesión**. Sin este resguardo el test pasaba pero envenenaba el `close`.
- Sin tests nuevos: las dos correcciones reparan verificadores vigentes de PC-1/PC-10, no agregan promesas (R2, sin cuota).

## 3. Evidencia de comandos y salidas

- Pytest plano: `python3 -m pytest tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py -v` → **2 passed en 1.11 s**.
- Close instrumentado: nodeids de ambos tests en `/tmp/tw-red023.nodeids`, `python3 scripts/cdad-suite.py close --evidence-root /tmp/tw-red023-close --nodeids /tmp/tw-red023.nodeids` → **`rc=0, canary_delta_lines=0`**; `attempt.json`: `passed=2, failed=0, skipped=0, errors=0, verified=True`.
- Oráculo paralelo: `python3 -m pytest tests/test_017_001_suite_parallel.py -v` → **6 passed en 12.55 s** (agregado+equivalencia serial, raíces, partición, canario+hijos, rechazos, default). **Nada sigue fallando: D1 y D2 quedan resueltos del lado verificador.**
- `git show --stat HEAD`: solo los 3 tests (54+/5−).

## 4. Límites

- **Suite completa no realizada**: sin autorización para corrida completa; selección ejecutada: 2 tranche (plano + close) + 6 del oráculo paralelo. Cierre de epic con completa obligatoria queda pendiente con su autorización.
- Evidencia de corridas en `/tmp/tw-red023-close`, `/tmp/tw-red023.nodeids` y `tmp_path` (fuera del repo); sin restos en el repo.
- La implementación GREEN (`10dfae99`) no se re-ejecutó más allá de lo que el propio oráculo invoca (parallel/close como caja negra); su re-acreditación formal (GREEN/review-fix) queda al orquestador.

## 5. Delta de inventario vivo (como texto — no edito `docs/`, lo materializa el orquestador)

```
~ tests/test_017_001_suite_parallel.py (017-001 T6, PC-10): correccion D1 —
  nodeid tranche2 `stays` -> `stay` (el real). Sin cambio de promesa.
  Estado: VERDE (6/6) sobre implementacion 10dfae99.
~ tests/test_017_001_suite_tranche1.py (017-001 T2-check-6, PC-1): correccion D2 —
  asercion inicial observer-aware (neutralidad sin externo; con externo,
  eventos propios + valor identico + externo no altera) + finally que no
  retira sumidero ajeno. Estado: VERDE plano (1/1) y bajo close (1/1).
~ tests/test_017_001_suite_tranche2.py (017-001 T2-check-7, PC-1): idem D2
  sobre las 4 fronteras U1/U3/U4/documental. Estado: VERDE plano y bajo close.
Total del oraculo T6: 6 nodeids en verde; T2 sin cambios de inventario.
```

## 6. Declaraciones honestas

- **Nunca leí implementación**: no abrí ningún archivo bajo `scripts/` (el reporte `green-T6-parallel.md` ya describía el ciclo de vida del observador como insumo declarado). Solo ejecuté CLIs como caja negra según ordena el packet.
- Los timeouts del oráculo (300 s) son guardas de liveness, no oráculos de duración (convención 11).
- La rama `external_sink_present=True` bajo pytest plano no se ejercita (no hay sumidero externo); su cobertura es el run bajo `close`, evidenciado arriba.
