Todo verificado y commiteado. Entrego el FINAL TEXT.

---

# FINAL TEXT — test-writer RED-031 (017-001-suite-performance, hallazgo T7)

## Ruta y validación del packet (route C)

- Identificación declarada: packet `017-001-suite-performance-test-writer-red-031`, execution `exec-017-001-suite-performance-001`, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…92672e`.
- `validate-request` rc 0; `validate-packet` rc 0 (comparación completa contra el render canónico).
- Contrato verificado por sha256 contra el archivo; execution context v2 (`schema_version: 2`); cero marcadores inline (sin mezcla route A/C). Packet válido; trabajé solo bajo ese contrato.

## Cambio (1 archivo, 13+/13-, commit `03c22039`)

**`tests/test_010_004_t5_e2e.py`** — la raíz aislada del E2E sale del checkout:

- Antes: `ISOLATED_ROOT_PARENT = REPO_ROOT / ".cdad" / "tmp" / "t5-isolated-consumer"` + `tempfile.mkdtemp(dir=…)` dentro del checkout.
- Ahora: `run_scoped_mkdtemp(f"cdad-t5-isolated-run-{os.getpid()}-")` desde `tests.product_staging` (fuera del checkout), unicidad por corrida y limpieza de clase intactas.
- Docstrings actualizados (módulo + clase): `.cdad/tmp` **no** es raíz temporal declarada (`temporary_roots` vacío en `docs/cdad-policy.json`).
- **Sin cambios de promesas ni aserciones**: copia del producto en la raíz, las seis env redirigidas, instalación desde la copia y prohibición del wrapper del checkout intactos (verificado: ninguna línea `assert/expect/PC-12/promesa` tocada en el diff).
- Revisión de otras escrituras en ese archivo: ninguna — `CHECKOUT_WRAPPER` es solo comparación de solo-lectura; todo lo demás escribe bajo `iso_root` o el proyecto consumidor sintético.
- **No tocados**: `scripts/`, el contrato, `tests/test_017_001_suite_parallel.py`.

## Otros tests que escriben en el checkout (informados, NO tocados)

- `tests/test_017_001_suite_parallel.py:1257` (sentinela bajo `build/`), `:1497` (sonda de reescritura bajo `build/`), `:1782` (churn transitorio bajo `.cdad/tmp`): sondas canarias intencionales del propio meta-test.
- `test_006_004_u1/u2`, `test_004_002_t2`: escriben en raíces sintéticas (`self.root`/`project.root`), no en el checkout real.

## Evidencia exigida por el packet

1. **Archivo solo**: `python3 -m pytest tests/test_010_004_t5_e2e.py -v` → **2 passed in 23.89s**.
2. **Escenario que fallaba**: nodeids con los 18 de `test_017_001_suite_parallel.py` + 2 de `test_010_004_t5_e2e.py` = 20:
   `python3 scripts/cdad-suite.py parallel --workers 2 --evidence-root /tmp/cdad-red031-ev-2f6DnH --nodeids /tmp/cdad-red031-nodeids-20.txt` → **rc 0**, `verdict: accepted`, consolidado **20 passed / 0 failed / 0 skipped**, `checkout_canary.unchanged: true` (20458 archivos, huella `5a7d4013…`, scope `build/`+`.cdad/`), `canary_delta_lines: 0`, `orphans: 0`, pared total **175.54s** (worker-0: 18 passed en 174.86s; worker-1: 2 passed en 30.69s).
3. **Residuos**: `.cdad/tmp` sin `t5-isolated-consumer`; `find` de `*t5-isolated*` en el checkout vacío. (Removí además el directorio padre vacío y stale de corridas viejas, scratch git-ignorado, antes de la corrida.)

## Comandos exactos (todos con cwd en la raíz del repo)

- `python3 scripts/cdad_packet.py validate-request --request .cdad/packets/…/REQUEST.json`
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md`
- `python3 -m pytest tests/test_010_004_t5_e2e.py -v`
- nodeids: `pytest … --collect-only -q | grep ::` (18+2=20) → `/tmp/cdad-red031-nodeids-20.txt`
- `python3 scripts/cdad-suite.py parallel --workers 2 --evidence-root /tmp/cdad-red031-ev-2f6DnH --nodeids /tmp/cdad-red031-nodeids-20.txt`
- `git add tests/test_010_004_t5_e2e.py && git commit` → **`03c22039`** (solo ese archivo)

## Límites y desvíos declarados honestamente

- **`tmp-valid/`**: directorio scratch creado por mí en la raíz del repo (nodeids + logs intermedios); **ya borrado** (`rm -rf`, verificado ausente). Los logs de la corrida válida viven fuera del checkout (`/tmp/cdad-red031-*`).
- **Primera corrida duplicada (mi defecto, corregido)**: el intento foreground inicial superó el timeout de 120s pero su worker-0 sobrevivió huérfano contra el mismo evidence-root que el reintento en background. Detecté ambos por `ps`, maté toda la familia (`TERM` + `KILL`, verificado limpio, sin residuos en `.cdad/tmp` ni `build/`), creé evidence-root nuevo y relancé **una sola** corrida — la aquí acreditada. La corrida contaminada no se usa para nada.
- **`docs/.cdad-state.json`** figura `M` en `git status` pero **no lo toqué**: mtime 07:31:35, anterior a mi sesión; no inspeccioné su contenido (fuera de mi read scope); queda para el orquestador.
- **Aislamiento de fase**: no leí implementación (`scripts/`, `sources/`, etc.); solo packet, spec, `parallelism.md`, `tests/test_010_004_t5_e2e.py` y `tests/product_staging.py`. Diff final limitado a `tests/`.
- Evidencia cruda completa en `/tmp/cdad-red031-ev-2f6DnH` (`parallel.json`, `parallel.md`, `worker-*/`, canaries); no se afirma suite completa: selección de 20 nodeids, resto no corrido.
