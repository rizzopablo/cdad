# Línea base instrumentada — 017-001-suite-performance (T4)

- Fecha: 2026-11-07
- Intento: `evidence/017-001-baseline2/attempt-20261107T171212569537Z-1474770-69bdbdcf`
  (copia de solo lectura para revisión: `.cdad/tmp/017-001-baseline-attempt`)
- Revisión: `7426438bdbace78d55f3ea97f1a74e2d000a7310` (árbol limpio, `dirty=0`)
- Selección: `--all` — 2034 nodeids
- Comando: `python3 scripts/cdad-suite.py close --all --evidence-root ~/<workspace>/projects/cdad/evidence/017-001-baseline2`
- Canary de configuración: 0 líneas de diferencia antes/después

## Resultado

| Métrica | Valor |
|---|---|
| Pared de pytest (`T_pytest`) | **4994.27 s (83.2 min)** |
| Exterior del comando (`T_exterior`, resolución 1 s) | 4995.0 s |
| Resultados | **2029 passed, 0 failed, 0 errors, 5 skipped** |
| `sum_S_test` (fases observadas) | 4986.6 s |
| Preparación medida (operaciones) | **186.506 s (3.74 %)** |
| Resto no desglosado | **4800.094 s (96.26 %)** — desconocido |
| `R_pytest` | 7.671 s |
| `R_exterior` | 0.73 s (menor que la resolución de 1 s) |

Identidad contable: `preparación + resto = sum_S_test` y
`sum_S_test + R_pytest = T_pytest` dentro de la tolerancia declarada de 1e-3 s.
Los totales se calculan desde los valores sin redondear; la suma de los valores
por test publicados puede desviarse hasta `N × 0.0005 s = 1.017 s` (cota
declarada).

## Qué está medido y qué no

Lo único clasificado es la **preparación medida**: 186.5 s repartidos en
operaciones instrumentadas. El **resto de 4800.1 s no está desglosado** y
permanece **desconocido**: no se lo clasifica como trabajo contractual ni como
preparación, y por sí solo no fundamenta ninguna decisión de optimización
(spec §4.4). Los archivos y tests más costosos se listan abajo solo para ubicar
dónde mirar si se decide medir más.

Operaciones top-level medidas (tiempo exclusivo):

| Operación | Total | Ocurrencias | % de `sum_S_test` |
|---|---:|---:|---:|
| `continuity.construct` | 78.636 s | 210 | 1.58 % |
| `recovery.construct` | 74.522 s | 162 | 1.49 % |
| `u1.lookup` | 9.684 s | 24 | 0.19 % |
| `documentary.install-lookup` | 8.600 s | 4 | 0.17 % |
| `u4.lookup` | 6.036 s | 11 | 0.12 % |
| `isolation.seed` | 5.286 s | 1905 | 0.11 % |
| `u3.lookup` | 1.543 s | 6 | 0.03 % |

Archivos con mayor `S_file` (fases observadas, sin clasificar su composición):
`test_009_001_installer_agent_overlay.py` 299.0 s,
`test_010_002_documentary_role_properties.py` 241.2 s,
`test_install_ownership.py` 178.3 s, `test_007_003_legacy_reanchor.py` 162.9 s,
`test_install_review5_regressions.py` 150.9 s.

## Contraste de alcance declarado vs observado

`coverage.status = all-selection`; `missing: []`, `without_entry: []`,
`blocked: false`, `measurement: complete`.

No ejercitadas por la corrida completa, declaradas de antemano en el registro:

- `product.copy` y `product.generate` — la rama fría de `product_root` requiere
  una fuente **sin** `build/staging/manifest.json`; el checkout base lo trae y
  toma la rama `checkout-manifest`. La rama fría se calibró en `C-P-cold` sobre
  fuente descartable *slim* (0.52 s de lookup, 0.23 s de copia, 0.29 s de
  generación) y su duración **no** se extrapola al árbol completo.

Ningún intervalo comprometido faltó por fallo de captura. Las esperas
deliberadas siguen declaradas desconocidas y fuera del alcance comprometido.

## Condición de entrada a la base

Satisfecha antes de esta corrida (`entry-check`, ocho selecciones,
`satisfied=true`, seis checks). El método de agregación se reprodujo desde la
evidencia cruda con `reconcile` (T3), con el contraste de alcance completo
protegido por el oráculo (14 tests).

## Límites declarados

- Resolución del reloj exterior: 1 s. `R_exterior` no distingue diferencias
  menores y no se usa como explicación.
- `.cdad` dentro de las copias: el volumen es una observación (19.141 archivos /
  386 MB), no un tiempo; el tiempo aislado de `.cdad` sigue desconocido.
- Esperas deliberadas: familia declarada desconocida, no medida en esta base.
- La carga del host no se muestreó al iniciar; la corrida convivió con
  actividad del operador. La comparación antes/después deberá registrar la
  carga de cada corrida.
- No se extrapola esta corrida a otra revisión ni configuración.

## Lectura para la decisión de optimización

1. La preparación medida y reducible de forma demostrable es 186.5 s (3.74 %),
   concentrada en las dos construcciones de proyecto descartable
   (`continuity.construct` + `recovery.construct` = 153.2 s en 372
   ocurrencias).
2. El 96.26 % restante es desconocido. Si el objetivo de reducción exige tocarlo,
   la spec obliga a medirlo con una focal adicional antes de modificarlo; esta
   base no autoriza a suponer que sea eliminable.
3. El paralelismo (T6) es una decisión separada: no se deduce de esta
   atribución y requiere demostrar seguridad.

El objetivo de reducción se fija con el dueño después de esta lectura (decisión
reservada al dueño en las cuatro decisiones de Discovery).
