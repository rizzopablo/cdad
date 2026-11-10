Route C validated (summary): identification == REQUEST.json (packet `017-001-suite-performance-test-writer-audit-002`, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…` == file, execution `exec-017-001-suite-performance-001`); canonical `render` byte-identical to PACKET.md (8713 B, diff empty; `validate-request` and `validate-packet` exit 0); execution context `schema_version: 2` (v2). Read only declared inputs + `tests/`; no implementation read; no test edited.

---

# FINAL TEXT — test-writer AUDIT-002 (T5, 017-001-suite-performance)

**Packet:** `017-001-suite-performance-test-writer-audit-002` — route C validated. Solo `tests/` + spec y entradas declaradas (`spec.md` §4.4, `performance/remainder-measurement.md`, `red-T4b-external.md`). No se leyó implementación. No se editó ningún test: es un informe.

## Objetivo ejecutado

Clasificar las 76 ejecuciones de `install.sh` instrumentadas con `external.install` en los archivos más caros, para distinguir preparación compartible de promesa bajo prueba. Reconciliación del alcance: el sexto archivo más caro (`tests/test_role_packet_render.py`) tiene **0** pares `external.install` (295 pares `external.python`), por lo que las 76 ejecuciones viven en los otros cinco: 31 (009) + 1 (010_002) + 22 (ownership) + 15 (review5) + 7 (012) = **76**. El conteo estático sitio-por-sitio de esta auditoría reproduce exactamente el inventario medido de RED-021, sin segundos (los une el orquestador desde el perfil).

## Regla aplicada

- **accion-bajo-prueba:** alguna aserción evalúa ESA ejecución (rc, stdout/stderr, archivos creados, manifest, idempotencia, ownership, pycache).
- **preparacion:** solo produce estado para aserciones ajenas a la instalación y podría compartirse sin debilitar nada.
- **mixta:** ambas; se trata como acción.
- Disposición de auditoría (§R2/PC-4): todos los tests existentes **Mantener** — esta auditoría no propone cambios; ante incertidumbre se conserva.

## Tabla completa (76 sitios)

Comando base en todos los sitios: `bash <producto>/install.sh <flags>`, cwd = copia del producto, env con `CDAD_INSTALL_ROOT=<tmp>` y `CDAD_SKILL_EXTRA_DIRS=""` (review5-b3a/b3b añaden `XDG_CONFIG_HOME` redirigido). `∅` = sin flags.

### 009 — `tests/test_009_001_installer_agent_overlay.py` (clase `AgentOverlayContract`, helper `run()` L28-36, 31 ejecuciones)

| # | sitio | test | flags | clase | aserción/consumidor que sostiene |
|---|---|---|---|---|---|
| 1 | 009:101 | test_pc1_preserves… | ∅ | mixta | `check_returncode()` + setup (el target se muta después) |
| 2 | 009:109 | test_pc1_preserves… | ∅ | accion | overlay preservado + cero líneas CONFLICT en stdout+stderr |
| 3 | 009:121 | test_pc2_update… | ∅ | mixta | rc + setup (mutación de instalado y staging) |
| 4 | 009:128 | test_pc2_update… | ∅ | accion | rc==0 + overlay sobrevive + sentinel upstream llega |
| 5 | 009:137 | test_pc3_overlay… | ∅ | mixta | rc + setup |
| 6 | 009:142 | test_pc3_overlay… | ∅ | accion | rc==0 + manifest owned + digest == bytes instalados |
| 7 | 009:150 | test_pc3_overlay… | ∅ | accion | `sync` en salida (idempotencia) |
| 8 | 009:153 | test_pc3_overlay… | `--check` | accion | rc==0 |
| 9 | 009:157 | test_pc4_non_overlay… | ∅ | mixta | rc + setup |
| 10 | 009:162 | test_pc4_non_overlay… | ∅ | accion | bytes preservados + `conflict` + no adoptado en manifest |
| 11 | 009:169 | test_pc4_non_overlay… | `--check` | accion | rc≠0 (drift no resuelto) |
| 12 | 009:173 | test_pc5_validator… | ∅ | mixta | rc + setup para piernas del validador (aserciones ajenas a install) |
| 13 | 009:194 | test_pc6_check_diagnostics… | ∅ | mixta | rc + setup |
| 14 | 009:198 | test_pc6_check_diagnostics… | `--check` | accion | nombra path instalado + `overlay` |
| 15 | 009:205 | test_pc7_uninstall… | ∅ | mixta | rc==0 + setup |
| 16 | 009:210 | test_pc7_uninstall… | ∅ | mixta | rc==0 + registra overlay (setup: bytes `before`) |
| 17 | 009:213 | test_pc7_uninstall… | `--uninstall` | accion | rc==0 + preservado byte-idéntico + `preserv` |
| 18 | 009:240 | test_pc1a_changing… | ∅ | mixta | rc + setup |
| 19 | 009:244 | test_pc1a_changing… | ∅ | mixta | rc + setup |
| 20 | 009:246 | test_pc1a_changing… | ∅ | accion | sin CONFLICT + `model: user/B` retenido |
| 21 | 009:236 (helper `_assert_owned_clean_check`) | test_pc1a_changing… | `--check` | accion | digest manifest==bytes + rc==0 |
| 22 | 009:253 | test_pc1b_removing… | ∅ | mixta | rc + setup |
| 23 | 009:257 | test_pc1b_removing… | ∅ | mixta | rc + setup |
| 24 | 009:259 | test_pc1b_removing… | ∅ | accion | bytes instalados == staging |
| 25 | 009:236 (helper) | test_pc1b_removing… | `--check` | accion | digest + rc==0 |
| 26 | 009:267 | test_pc3_legacy… | ∅ | mixta | rc + setup |
| 27 | 009:271 | test_pc3_legacy… | ∅ | mixta | rc + setup (manifest mutilado después) |
| 28 | 009:276 | test_pc3_legacy… | ∅ | accion | reparado sin CONFLICT + modelo sobrevive |
| 29 | 009:236 (helper) | test_pc3_legacy… | `--check` | accion | digest + rc==0 |
| 30 | 009:283 | test_pc6_check_summary… | ∅ | mixta | rc + setup (drift plantado después) |
| 31 | 009:287 | test_pc6_check_summary… | `--check` | accion | resumen `Check: FAIL` nombra el path instalado |

(`test_pc5_validator_uses_agent_overlay…` no ejecuta install: solo lee el texto del validador — fuera del conteo.)

### ownership — `tests/test_install_ownership.py` (helper `run_installer()` L83-98, 22 ejecuciones)

| # | sitio | test | flags | clase | aserción/consumidor que sostiene |
|---|---|---|---|---|---|
| 32 | ownership:271 | test_t5_case1… | `--basic` | accion | rc==0 + foreign intacto + set staged desplegado + manifest consistente |
| 33 | ownership:304 | test_t5_r3o2… | `--basic` | accion | manifest registra stack/runtime + ausencia de `profile` |
| 34 | ownership:344 | test_t5_case2… | `--basic` | mixta | rc==0 + setup (mutación local después) |
| 35 | ownership:352 | test_t5_case2… | `--dry-run --basic` | accion | reporta `conflict` nombrando el path |
| 36 | ownership:366 | test_t5_case2… | `--basic` | accion | reporta `conflict` + bytes preservados |
| 37 | ownership:387 | test_t5_case5… | `--basic` | mixta | rc==0 + setup (symlink después) |
| 38 | ownership:396 | test_t5_case5… | `--dry-run --basic` | accion | conflicto de symlink + nombra path |
| 39 | ownership:410 | test_t5_case5… | `--basic` | accion | conflicto + canario intacto + symlink no reemplazado |
| 40 | ownership:448 | test_t5_case6… | `--basic` | accion | rc≠0 (el fallo parcial reportado ES la promesa) |
| 41 | ownership:462 | test_t5_case6… | `--basic` | accion | rc==0 + manifest consistente (retry que sana) |
| 42 | ownership:475 (helper `_install_with_foreign_files`) | test_t5_case4… | `--basic` | mixta | rc==0 + setup (foreign plantados después) |
| 43 | ownership:492 | test_t5_case4… | `--basic` | accion | foreign sobreviven intactos al reinstall |
| 44 | ownership:475 (helper) | test_t5_case7… | `--basic` | mixta | rc==0 + setup |
| 45 | ownership:523 | test_t5_case7… | `--uninstall` | accion | owned eliminados + foreign sobreviven |
| 46 | ownership:548 | test_t5_case7… | `--uninstall` | accion | rc==0 (idempotencia) |
| 47 | ownership:587 | test_t5_case8… | `--basic` | accion | rc==0 + bytes staged con sources/ inaccesible |
| 48 | ownership:629 | test_t5_case9… | `--dry-run --basic` | accion | anuncia el fixture + raíz intacta (dry-run exacto) |
| 49 | ownership:646 | test_t5_case9… | `--basic` | accion | despliega los bytes anunciados |
| 50 | ownership:666 | test_t5_case3… | `--basic` | mixta | rc==0 + setup (retiro de staging después) |
| 51 | ownership:677 | test_t5_case3… | `--check` | accion | rc≠0 + nombra el artefacto obsoleto |
| 52 | ownership:701 | test_t5_case10… | `--basic` | mixta | rc==0 + setup (staging regenerado después) |
| 53 | ownership:711 | test_t5_case10… | `--check` | accion | rc≠0 + nombra el path con drift |

### review5 — `tests/test_install_review5_regressions.py` (helper `run_installer()` L141-165, 15 ejecuciones)

| # | sitio | test | flags | clase | aserción/consumidor que sostiene |
|---|---|---|---|---|---|
| 54 | review5:341 | test_review5_b1… | `--basic` | mixta | rc==0 + setup (mutación del instalado después) |
| 55 | review5:349 | test_review5_b1… | `--check` | accion | rc≠0 + nombra el drift + bytes preservados |
| 56 | review5:387 | test_review5_b2… | `--basic` | mixta | rc==0 + setup (skill/guard mutados después) |
| 57 | review5:399 | test_review5_b2… | `--dry-run --basic` | accion | `conflict` nombrando skill y guard |
| 58 | review5:418 | test_review5_b2… | `--basic` | accion | `conflict` + ambos preservados byte a byte |
| 59 | review5:476 | test_review5_b3a…(retired_by_reinstall) | `--basic` | mixta | rc==0 + registra despliegue (setup del retiro) |
| 60 | review5:506 | test_review5_b3a… | `--basic` | accion | rc==0 + retirado de disco y de manifest |
| 61 | review5:537 | test_review5_b3a… | `--check` | accion | rc==0 + PASS + sin PENDING-REMOVAL |
| 62 | review5:564 | test_review5_b3a… | `--uninstall` | accion | rc==0 + retira lo registrado, sin resurrección |
| 63 | review5:600 | test_review5_b3b…(preserved) | `--basic` | mixta | rc==0 + setup (edición local + retiro después) |
| 64 | review5:624 | test_review5_b3b… | `--basic` | accion | CONFLICT nombrando el path + preservado + sigue registrado |
| 65 | review5:679 | test_review5_b4… | `--dry-run --basic` | accion | rc==0 + exactamente un aviso de deprecación |
| 66 | review5:683 | test_review5_b4… | `--basic` | accion | rc==0 + un aviso + sin marker retirado + sin `profile` |
| 67 | review5:742 | test_review5_e1… | `--basic` | mixta | rc==0 + setup (edición pre-uninstall después) |
| 68 | review5:750 | test_review5_e1… | `--uninstall` | accion | informa modificación + nombra path + preserva bytes exactos |

### 012 — `tests/test_012_installer_ignore_pycache.py` (helper `run_installer()` L67-82, 7 ejecuciones)

| # | sitio | test | flags | clase | aserción/consumidor que sostiene |
|---|---|---|---|---|---|
| 69 | 012:203 | test_pc1… | `--basic` | accion | rc==0 + cero claves cache + cero fuentes cache |
| 70 | 012:230 | test_pc2… | `--basic` | accion | manifest limpio (línea base de la igualdad conjunta) |
| 71 | 012:232 | test_pc2… | `--basic` | accion | manifest con-cache idéntico (claves+digests+fuentes) |
| 72 | 012:259 | test_pc3… | `--basic` | mixta | rc==0 + setup (bytecode regenerado después) |
| 73 | 012:263 | test_pc3… | `--check` | accion | rc==0 + cero líneas drift/missing de bytecode |
| 74 | 012:317 | test_pc4… | `--basic` | mixta | rc==0 + línea base `content_before` (setup de la poda) |
| 75 | 012:385 | test_pc4… | `--basic` | accion | rc==0 + cero restos cache + contenido idéntico |

### 010_002 — `tests/test_010_002_documentary_role_properties.py` (helper `_run_product_install()` L437-448, 1 ejecución compartida)

| # | sitio | test(s) | flags | clase | aserción/consumidor que sostiene |
|---|---|---|---|---|---|
| 76 | 010_002:472 (`final_install_bundle`, 1 ejecución por proceso) | `TestFinalIsolatedDistribution::test_isolated_install_distributes…` + `::test_final_documentary_journeys…` | ∅ | mixta | Faceta acción: rc==0 + CLI/esquema instalados byte-idénticos a la fuente + canario HOME. Faceta preparación: el CLI instalado ejecuta los 2 recorridos documentales del segundo test. |

## Totales por clase

| clase | sitios | % |
|---|---|---|
| accion-bajo-prueba | 47 (009:16, ownership:16, review5:10, 012:5, 010_002:0) | 62 % |
| mixta (se trata como acción) | 29 (009:15, ownership:6, review5:5, 012:2, 010_002:1) | 38 % |
| preparacion pura | **0** | 0 % |
| **equivalente-acción (accion+mixta)** | **76** | 100 % |
| **preparación compartible** | **0** | — |

Flags observados: `∅` (instalación ordinaria), `--basic` (alias deprecado sin efecto), `--dry-run --basic`, `--check`, `--uninstall`.

## Lectura (para T5)

Ninguna de las 76 ejecuciones es preparación pura compartible: cada una tiene al menos una aserción que evalúa su rc, su salida, sus archivos o su manifest. Cachear o compartir cualquiera de ellas dejaría sin ejecutar una transición que el test verifica (spec INV-4). Barrera adicional de aislamiento (spec INV-3): cada test instala en una raíz temporal propia y varios mutan instalado y staging (009-pc2 muta staging; ownership/review5 restauran staging de sandbox por test) — compartir raíces exigiría copy-on-write, no una caché de resultados. La optimización serial debe buscarse fuera de `install.sh` repetido como promesa (copias de producto/`.cdad`, CLI repetidas de `test_role_packet_render.py`, resto in-process de 010_002), nunca sustituyendo estas 76 ejecuciones.

## Dudas declaradas

1. **Frontera mixta/accion (sin efecto en la decisión):** las instalaciones iniciales con rc asserted se clasifican mixta por su doble rol (rc evaluado + setup). Si el orquestador aplica la regla estricta «rc asserted ⇒ accion», las 15+6+5+2 colapsan a accion y el equivalente-acción sigue 76; nada se vuelve compartible.
2. **010_002 ya comparte:** su única ejecución está cacheada por proceso (`final_install_bundle`) entre sus 2 tests — estado preexistente, no propuesta; se clasifica mixta porque sus bytes instalados también se asertan.
3. **pc2 de 012 (sitios 70/71):** ambas ejecuciones se clasifican accion porque la igualdad de manifests evalúa los dos resultados de instalación; ninguna es setup de aserciones ajenas.
4. **B4 de review5 (sitios 65/66):** el aviso de deprecación de `--basic` se trata como conducta de instalación (D1/INV-7: nada silencioso), luego accion.
5. **Método:** enumeración estática + cruce con `red-T4b-external.md` y `remainder-measurement.md` (totales 31/1/22/15/0/7 reproducidos exactos). No se re-ejecutó la suite para esta auditoría estática.

## Evidencia

- modified files: ninguno (subfase audit: no se altera tests).
- exact commands: `python3 scripts/cdad_packet.py render --request …` + `validate-request` + `validate-packet` (exit 0, render == PACKET.md); `sha256sum spec.md` (`472bab0c…` == contrato); `grep -n` de `external.install|_run_product_install|run_installer(|self.install(|run_validator(` sobre los 5 archivos + `tests/suite_operation_markers.py`; lecturas completas de los 5 archivos de test y de las 3 entradas declaradas.
- command output: conteos 31/1/22/15/7 = 76 reconciliados con RED-021 (76 install + 2 cli + 301 python); suite completa no realizada (auditoría estática sin cambios; sin selección ejecutada).
- commit: ninguno (el informe se entrega como FINAL TEXT para aprobación; lo materializa el orquestador).
