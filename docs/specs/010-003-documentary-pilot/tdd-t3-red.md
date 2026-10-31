Validación de la entrada y trabajo completados. Informe final:

## 0. Entrada validada (ruta C, contexto v2)

| Comprobación | Comando | Resultado |
|---|---|---|
| `REQUEST.json` | `python3 scripts/cdad_packet.py validate-request --request .cdad/packets/010-003-documentary-pilot-test-writer-red-001/REQUEST.json` | rc=0 |
| `PACKET.md` completo | `python3 scripts/cdad_packet.py validate-packet --request …/REQUEST.json --packet …/PACKET.md` | rc=0 |
| Render canónico | `render --request …/REQUEST.json` vs `PACKET.md` | **byte-idéntico** (`diff` rc=0) |
| Identificación | `render --route C --request …/REQUEST.json` vs bloque del despacho | **idéntico** |
| Contexto de ejecución | `validate-state --execution-context …/execution.json` | `VALID: execution=exec-010-003-documentary-pilot-001 feature=010-003-documentary-pilot model_policy=ordinary` |
| Contrato pineado | `sha256sum docs/specs/010-003-documentary-pilot/spec.md` | `f2dce9e0…1d5e5` = el declarado |

**Lecturas:** solo insumos declarados (`spec.md`, `plan.md`, `test-audit.md`, `post-audit.md`, `audit-reading-deviation-2026-10-31.md`), mi raíz `tests/` y los archivos de control de la ruta C. **No leí código de implementación** (`agents/`, `skills/`, `scripts/`, `sources/` del producto); ejecuté `scripts/cdad_packet.py` sin leer su fuente. **No leí ni intenté leer `skills/cdad-cycle/references/**`** ni `tests/.sensitive-patterns.local`. El bloque común del paquete remite a la norma documental (`PACKET.md:12`, «read it»); el `objective` la declara no-insumo y el POST-AUDIT fijó el precedente de **no intentar** la lectura: la tensión queda reportada, no resuelta por otra vía. Todo lo necesario estaba en `spec.md` §2.4 y §3.

## 1. Artefactos (commit `cd2d57b3`)

| Ruta | SHA-256 |
|---|---|
| `tests/fixtures/…/sources/s1.md` | `9f8c3cb3c7da6de8e654ee83b492f11136125e2615eaae76e4d6518356b6daff` |
| `tests/fixtures/…/sources/s2.md` | `2d7133724cae17218ab718784d53b3282cf6b3501ac838262a317fad44d70117` |
| `tests/fixtures/…/sources/inventory.md` | `86ffe51cb8cb825502b97a2d87faefc713f9a4cab97d9b99292697abe6ab2fdf` |
| `tests/fixtures/…/challenge/negative.md` | `ff45d9e3613c74145f5a85e23cae5d8ffb5008362642dbc9124fc59b1c249e1e` |
| `tests/fixtures/…/structural/broken.md` | `12b2697ca6f0188c6c77e3ad53593658721e9478757ad7aec0cdd962d5912e4c` |
| `tests/fixtures/…/structural/corrected.md` | `4ef7d8edaca7a8a5c78993457b869cbce859704ab0c44226bf61d325c82e7393` |
| `tests/fixtures/…/structural/no-references.md` | `89e325185e26ca3e190a75044da15785b6aa26c9e4d58860806baa48f2e196b7` |
| `tests/fixtures/…/structural/uninventoried.md` | `9b1ca18f9d410b23bd41fcf29c3294b55a66a58b89385fdf4721717b299a5538` |
| `tests/fixtures/…/oracle/contrast-key.md` | `91c277c1d7167db8a3df756a66c0e93166ac620ec95f9166e001a6a8921f7423` |
| `tests/test_010_003_documentary_pilot.py` | `8e2a1878538838306543e2767d54993480cb4147f8f7b205415d9f7f48e35737` |

El inventario es `inventory-010-003-v1`; los dos digests de la tabla coinciden byte a byte con `s1.md`/`s2.md` (T7 verde). Corpus y candidato se declaran sintéticos; el candidato se declara **NO CONFORME**.

## 2. Los tres defectos y su ubicación en el candidato

| Clase (PC-02) | Ubicación exacta | Justificación contra el corpus |
|---|---|---|
| (a) Afirmación como hecho sin respaldo | sección «Revisión del proceso»: «El proceso se revisa cada año mediante una encuesta interna de satisfacción…» (sin cita) | `grep` de «encuesta/satisfacción/revisión anual» en `s1`/`s2`: **sin coincidencias**; el corpus no respalda la afirmación |
| (b) Contradicción omitida | sección «Aprobación de casos límite»: «Las fuentes coinciden en un criterio único: los casos límite los aprueba la Dirección de Operaciones (…`s2.md#s2-f03`)» | `s2-f03` (solo Dirección de Operaciones, sin Cumplimiento) vs `s1-f02` (Jefe de Registro **con** visto bueno de Cumplimiento): posiciones incompatibles presentadas como consenso |
| (c) Referencia que resuelve y no sostiene | sección «Archivo»: «El archivo se organiza por número correlativo de recepción (…`s1.md#s1-f03`)» | `s1-f03` trata el plazo de respuesta, no el archivo; el respaldo real es `s1-f04`. El enlace resuelve estructuralmente |

Las 4 citas del candidato resuelven (`resolved_citations` → `s1-f01`, `s2-f03`, `s1-f03`, `s1-f03`): T3 verde acredita **resolubilidad**, no persistencia (C-2, dicho en docstring y mensaje).

## 3. RED registrado

```
$ python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
.....F..                                                                 [100%]
=========================== short test summary info ============================
FAILED tests/test_010_003_documentary_pilot.py::test_the_product_cites_only_inventoried_fragments_and_at_least_one
1 failed, 7 passed in 0.13s
RC=1
```

Causa (con `--tb=short`, misma corrida):

```
tests/test_010_003_documentary_pilot.py:427: in test_the_product_cites_only_inventoried_fragments_and_at_least_one
    assert PRODUCT.is_file(), (
E   AssertionError: El relevamiento del piloto todavía no existe: la obligación ausente de GREEN es crear …/product/relevamiento.md …
E   assert False
```

Composición exacta del plan (`plan.md:151-152`): **7 verdes** (T1–T5, T7, T8) y **1 rojo: T6**, por `AssertionError` de la aserción de existencia — **no** `FileNotFoundError` ni `ImportError`. No escribí el producto ni simulé revisión semántica. La semántica de resolución del destino del producto la validé en `/tmp/opencode` (copia del corpus), sin tocar `docs/`.

## 4. Evidencia de que ningún control lee la clave

- `grep -n "oracle\|contrast-key\|FAIL" tests/test_010_003_documentary_pilot.py` → **sin coincidencias** (el verificador ni siquiera nombra el directorio protegido; el control solo abre inventario, fuentes y documento examinado).
- `grep -n "encuesta\|criterio único\|coinciden\|se revisa cada año\|El archivo se organiza\|Dirección de Operaciones\|Cumplimiento"` sobre el verificador → **sin coincidencias**: ningún mensaje ni valor de aserción reproduce contenido de la clave.
- La clave se escribió **desde el contrato y el corpus**, nunca desde el verificador ni desde un producto (no existe).

## 5. Condiciones del POST-AUDIT §3, cumplidas

1. T7 lee `challenge/negative.md` y afirma ambas declaraciones sintéticas. 2. T7 es **bidireccional** (`sources/` ↔ tabla; archivo no listado ⇒ rojo). 3. T2 declara y usa `structural/broken.md`; T6 declara y usa inventario+fuentes. 4. `\d{2}` se declara **convención del piloto** en el inventario y en el docstring; T8 declara las **cuatro combinaciones** (corregida original/re-envuelta, rota original/re-envuelta) y compara veredicto+diagnóstico (`document`/`reference`/`cause`), con variante de rewrap derivada en el test.

## 6. Commit

`cd2d57b3` — `test(010-003): corpus, clave, muestras y verificador del piloto (RED)` — 10 archivos, 767 inserciones, solo bajo `tests/`. `docs/`, implementación y `tests/.sensitive-patterns.local` intactos (el único cambio ajeno en el árbol es `docs/.cdad-state.json`, del orquestador).
