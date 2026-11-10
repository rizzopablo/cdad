Route C validated and task complete. FINAL TEXT follows.

---

# FINAL TEXT — test-writer RED (red-012) — 017-001-suite-performance, T2

## 1. Validación de ruta C (antes de trabajar)

- Dispatch declara `Route C — explicit file backup` con un solo bloque de identificación; sin cuerpo inline (sin marcadores `---cdad-packet-json`): sin mezcla de rutas.
- `validate-request` → rc 0. `validate-packet` → rc 0.
- `render --route C` reproduce byte por byte el JSON de identificación del dispatch (`packet_id 017-001-suite-performance-test-writer-red-012`, `execution_id exec-017-001-suite-performance-001`, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab…192672e`, que coincide con el sha256 del archivo en disco).
- Contexto de ejecución v2 (`schema_version: 2`). Sin cambio silencioso de ruta.
- Lecturas control-plane: solo REQUEST.json, PACKET.md, execution.json.

## 2. Declaración honesta RED vs verde

**No hay RED.** No existe comportamiento nuevo: `tests/product_staging.py` ya implementa las tres ramas (`cold`, `checkout-manifest`, `cached`). Los dos verificadores agregados **pasan de entrada**: son **verificadores VERDES de calibración**, exigidos por el cierre bloqueante de review-T2-002 (hallazgo 1). La protección que aportan —antes ausente— es la evidencia focal de ramas, anidamiento, árbol devuelto y no-mutación del checkout para la familia `portable-product-staging` (PC-1 parte operaciones, INV-1/INV-3/INV-8). Sin ellos, la base seguiría comprometiendo intervalos jamás ejercitados.

## 3. Archivos modificados (solo tests, +200/−0)

- `tests/test_017_001_suite_operations.py`: solo adición al final (diff `200 insertions, 0 deletions`; los seis tests existentes intactos).
  - `test_product_root_cold_then_reuse` (PC-1, INV-1/INV-3/INV-8): fuente descartable real SIN manifiesto → primer `product_root()` emite `product.lookup[cold]` con `product.copy[cold]` y `product.generate[cold]` anidados (padre verificado), segundo emite `product.lookup[cached]`; verifica árbol generado con manifiesto JSON válido, que la fuente sigue sin manifiesto y que el checkout real conserva sus bytes.
  - `test_product_root_existing_manifest_then_reuse` (PC-1, INV-1/INV-3/INV-8): fuente descartable CON manifiesto real copiado (procedencia registrada) → lookups `checkout-manifest` + `cached`, cero eventos copy/generate; la raíz devuelta es la fuente por presencia; checkout intacto.
  - Aislamiento: `REPO_ROOT` y `_product_root` guardados/restaurados en `finally`; fuente bajo `tmp_path`; `.cdad` excluida de las copias (evidencia viva fuera de orígenes copiados, mapeo §D; `make staging` no la necesita — probado).
- Estado global reutilizado del módulo (`check_begin_contract`, `observed`, `shutil`, `json`, `Path`): sin tocar líneas existentes (imports del helper dentro de cada test).

## 4. Comandos exactos y resultados

```sh
# Focal nueva (2 tests):
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider \
  "tests/test_017_001_suite_operations.py::test_product_root_cold_then_reuse" \
  "tests/test_017_001_suite_operations.py::test_product_root_existing_manifest_then_reuse"
# → 2 passed in 4.52s (pared total con copia slim ~0.5s + make staging real ~0.3s por rama fría)

# Archivo completo (6 existentes + 2 nuevos):
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider \
  tests/test_017_001_suite_operations.py
# → 8 passed in 10.73s
```

Sondas previas (no evidencia, solo dimensionamiento; scratch en `/var/tmp`, limpiado después): copia slim del repo 0.5s/982KB; `make staging` real en copia mínima rc 0 en ~0.3s con manifiesto generado.

## 5. Commit

- `7541c436` — `test(017-001-T2): C-P-cold y C-P-present calibran product.lookup/copy/generate` — 1 archivo, 200 inserciones. Solo tests.

## 6. Límites y pendientes honestos

- **Suite completa no realizada**: selección focal ejecutada (archivo completo, 8 passed); sin corrida completa ni `close` en este paquete.
- **Delta de inventario vivo no actualizado**: fuera de mi write-scope (solo `tests/`); queda para el orquestador. `docs/.cdad-state.json` figura modificado desde antes de mi sesión (preexistente, no mío) y no lo toqué.
- **Sin lecturas de implementación**: nunca leí `scripts/`; oráculo construido solo desde spec, review-T2-002, mapeo, calibration y los helpers bajo `tests/`. Transparencia: leí el encabezado del `Makefile` raíz (fuera de `implementation_roots`, entrypoint ya citado por la spec) únicamente para la sonda de tiempos; ningún `.py` fuera de `tests/` fue leído.
- Trazabilidad por promesa: cada test declara sus postcondiciones (PC-1, INV-1/INV-3/INV-8) y su consecuencia («sin este test, el usuario…») en la docstring; nada va a `deferred-hardening` (ambos tienen consecuencia nombrada).
