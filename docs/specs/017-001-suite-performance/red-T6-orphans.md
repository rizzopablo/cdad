Route C work complete. FINAL TEXT report below.

---

# FINAL TEXT — test-writer RED corrección orphans T6 (017-001-suite-performance), packet `017-001-suite-performance-test-writer-red-025`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única en el dispatch (`packet_id` 017-001-suite-performance-test-writer-red-025, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md` → **EXIT 0**.
- `python3 scripts/cdad_packet.py render --request …` → **byte a byte igual** a `PACKET.md`; `render --route C` → identificación canónica **igual** a la del dispatch. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C.
- Contexto de ejecución `schema256_version`… (`schema_version: 2`) → **v2 confirmado**, sin switch silencioso. **No cargué `cdad-cycle` ni otro skill de ciclo**: el packet es el contrato.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.
- Solo leí insumos declarados (`spec.md`, `review-T6.md`, `red-T6-fixes.md`, `green-T6-fixes.md`, `tests/test_017_001_suite_parallel.py`) y solo edité el write_scope (`tests/`). **Nunca leí implementación**: ningún archivo bajo `scripts/` fue abierto; la CLI se ejercitó como caja negra y solo se leyeron sus artefactos de evidencia (`parallel.json`) para calibrar el rojo.

## 2. Pre-RED

Búsqueda en `tests/` + contrato + insumos autorizados: los once tests existentes cubren agregado, raíces, partición, canario/hijos genérico, rechazos, default y M1–M5. Ninguno exige `orphans == 0` exacto tras una corrida limpia, y el M3a acepta cualquier evidencia de hijos terminados sin distinguir un conteo por coincidencia de cmdline de un conteo real de descendientes. Protección faltante → **extensión justificada del archivo existente**, sin tocar los once tests (`git diff --numstat` final: `142 0`, puro agregado; cero líneas originales removidas).

Calibración del rojo (caja negra, evidencia descartable): una corrida `parallel --workers 1` con un archivo liviano invocada de modo que un proceso vivo no descendiente mencione la raíz en su cmdline publica `orphans=1` con `children_terminated=true`; sin ese proceso publica `orphans=0`. Cáscaras intermedias con la raíz en su cmdline resultaron excluidas, de modo que la sonda determinista es un **hermano** del lote (no descendiente) con la raíz en su cmdline — misma clase de defecto (el conteo incluye no descendientes: invocador, ancestros o envoltorios según la topología) — vivo durante el lote y muerto siempre (`finally` + `killpg` + `wait`) antes de la comprobación de hijo cero. Sin suerte ni carreras: vive 300 s, se mata explícitamente.

## 3. Resultado RED

**Archivo:** `tests/test_017_001_suite_parallel.py` (+142/−0). 1 test nuevo → **PC-10 (promesa E)**:

- `test_parallel_single_worker_reports_zero_orphans_excluding_invoker_and_ancestors` (M6): corrida limpia `parallel --workers 1` con un archivo liviano (tranche1) debe informar `orphans == 0` exacto (entero, no bool; no basta `orphans_checked == true`), con barrido propio `/proc` (excluyendo invocador y ancestros) que demuestra que no queda ningún hijo justo después del éxito. Sin este test, el usuario adoptaría como limpio un lote que cuenta no descendientes como huérfanos. Falla hoy con `AssertionError: … informa orphans=1 … assert 1 == 0`.

**Comandos exactos y salidas:**
- `python3 -m pytest tests/test_017_001_suite_parallel.py::test_parallel_single_worker_reports_zero_orphans_excluding_invoker_and_ancestors -q -p no:cacheprovider` → **1 failed en 3.09 s**, `AssertionError` de promesa (`orphans=1`). Cero `ImportError`/errores de colección (`py_compile` OK). Sin procesos sonda residuales tras la corrida.
- `python3 -m pytest tests/test_017_001_suite_parallel.py -q -p no:cacheprovider` → **11 passed, 1 failed en 63.91 s**. Los 11 existentes siguen verdes (sin modificar); el nuevo falla solo por la aserción de promesa.
- Barrido `/proc` post-corrida del test → vacío (probado por el propio test). Nunca quedaron procesos vivos.

**Commit:** `7f150eb9` — solo `tests/test_017_001_suite_parallel.py`. (`M docs/.cdad-state.json` es preexistente a este packet y quedó fuera del commit.)

## 4. Delta de inventario vivo (como texto)

```
+ tests/test_017_001_suite_parallel.py::test_parallel_single_worker_reports_zero_orphans_excluding_invoker_and_ancestors (017-001 T6-M6, PC-10): corrida limpia --workers 1 de un archivo informa orphans == 0 exacto (no solo orphans_checked == true); el conteo excluye invocador y ancestros (barrido /proc sin descendientes vivos justo despues del exito). Estado: RED (informa orphans=1).
```

## 5. Declaraciones honestas

- **Nunca leí implementación**: no abrí ningún archivo bajo `scripts/`. Calibré el rojo ejecutando la CLI como caja negra con evidencia descartable (eliminada tras verificar: sin restos en el árbol salvo el commit) y leyendo `parallel.json` para precisar el motivo del rojo.
- Timeout de subprocess (300 s heredado) y `sleep 300` de la sonda son guardas de liveness, no oráculos de duración (convención 11).
- Suite completa no realizada: sin autorización para corrida completa; selección ejecutada: el archivo T6 (12 tests: 11 viejos verdes + 1 nuevo rojo).
- La sonda modela la clase de defecto con un hermano determinista porque, bajo pytest, las cáscaras invocadoras intermedias con la raíz en su cmdline resultaron ya excluidas del conteo; el defecto observable y reproducible es la inclusión de procesos vivos no descendientes. Si el implementador demuestra otra topología, el test sigue valiendo: exige `orphans == 0` cuando ningún descendiente queda vivo.
