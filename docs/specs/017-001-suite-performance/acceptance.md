# Aceptación — 017-001-suite-performance

**Revisión aceptada:** `bf0e7483c0403b545760efbcb0134cd958d31a30`.
**Autoridad:** el dueño delegó HITL al orquestador («Te delego hitl, eres el
dueño del proceso, toma decisiones con criterio amplio pensando en el uso real
del sistema por el usuario final»), registrado en `docs/.cdad-state.json`
(`hitl_delegation`). La firma la ejecuta el orquestador; la decisión es del
dueño por delegación expresa.

## Objetivo registrado (PC-4) — cumplido

Registrado en `performance/parallelism.md` **antes** de medir:

```
(pared_serial − pared_paralela) / pared_serial >= 0.15
```

más conjuntos de `passed/failed/skipped` idénticos por nodeid y cero fallos,
errores o skips no declarados.

| Medición final (`--all`, misma revisión, `dirty = 0` en ambas) | Valor |
|---|---:|
| Serial (`close --all`, `T_exterior`) | 4459 s |
| Paralela (`parallel --all --workers 2`, `total_wall_s`) | 2593.15 s |
| **Reducción de pared** | **41.84 %** (umbral 15 %) |
| Equivalencia por nodeid | 2059 vs 2059, **0** diferencias |
| Resultado | 2054 passed + 5 skipped en ambos, 0 failed |

Artefactos: `performance/comparison.json`, `performance/parallelism.md`,
`.cdad/tmp/017-001-final-evidence/`, crudos en
`evidence/017-001-final4/{serial,parallel}`.

## Postcondiciones

| PC | Cómo queda | Evidencia |
|---|---|---|
| **PC-1** | Calibración focal con XML, perfil, correspondencia nodeid↔resultado↔fase e intervalos comprometidos contabilizados | `tests/test_017_001_suite_profile.py`, `performance/operation-scope.json` (`calibrated: true`), `review-fix-T1*` |
| **PC-2** | `close` conserva selección, rc, skips, interrupciones, reserva, logs y canarios; sin otra ejecución de pytest en el gate | `close` idéntico por comparación AST (`review-T6-005`), `tests/test_017_001_suite_operations.py`, `review-fix-T2-*` |
| **PC-3** | Línea base completa sobre revisión fijada, reconstruible desde la evidencia | `performance/baseline.json`/`.md` (4994.27 s, 2029 passed, `7426438b`), `review-T4-002` |
| **PC-4** | Objetivo, magnitud, selección, condiciones y regla registrados antes de aceptar optimización, con límites de atribución | `performance/parallelism.md`, esta aceptación |
| **PC-5** | Todos los nodeids con fases, agregación por archivo, clasificación preparación / resto; desconocidos con su límite | `performance/baseline.md`, `performance/remainder-measurement.md`, `installer-calls-audit.md` |
| **PC-6** | Conciliación reproducible desde crudos por comando versionado, con residual y diagnóstico; sin doble conteo | `scripts/cdad-suite.py reconcile`, `tests/test_017_001_suite_reconcile.py`, `review-T3-003`; salida final: preparación 448.90 s, resto 4002.51 s, `R_pytest` 7.12 s, `R_exterior` 0.47 s |
| **PC-7** | **Ninguna optimización de preparación aplicada**: la auditoría mostró 0 de 76 instalaciones compartibles (47 acción bajo prueba, 29 mixtas). Se documenta el costo que se pretendía reducir y por qué no existe | `installer-calls-audit.md`, `performance/remainder-measurement.md` |
| **PC-8** | La optimización serial **se evaluó y se midió**: 186.2 s de preparación sobre 4994.27 s (3.73 %), resto 96.27 % no desglosado; el balance registra frente al objetivo que la reducción serial viable es nula y deja el objetivo pendiente. Decisión del dueño: pasar a PC-9 | `performance/baseline.md`, `installer-calls-audit.md`, `progress.md` |
| **PC-9** | Decisión de paralelismo registrada después de la medición serial, por costo residual y objetivo pendiente; el dueño fijó workers configurables (default 2, tope `nproc-1`) y exigió demostrar aislamiento antes de aplicar | `performance/parallelism.md`, decisión registrada 2026-11-07 |
| **PC-10** | Inventario de recursos compartidos, HOME/XDG/TMP por worker, scratch de test fuera del checkout, sin cachés con escritura compartida, procesos finalizados y evidencia por intento sin colisión; costo de preparación duplicada medido (16.34 s) y sumas concurrentes nunca presentadas como pared | `performance/parallelism.md`, `parallel.json` (orphans 0, family_verifiable true, canario limpio), `tests/test_017_001_suite_parallel.py` |
| **PC-11** | Revisión independiente del diff completo: sin poda, sin aserciones debilitadas, sin omisiones nuevas ni esperas recortadas | `review-final-tests.md` (17 archivos, cita por archivo), `review-final-product*.md` |
| **PC-12** | La candidata final conserva corrida completa instrumentada verde y atribuible, skips declarados (5), canario examinado y `validate` ok sobre la misma revisión | corrida de `bf0e7483`, `validate` 2059 nodeids `status: ok`, `suite-inventory.json` |

## Invariantes

- **INV-1 Identidad:** toda cifra publicada remite a intento, revisión, selección y método; `comparison.json` fija la revisión y la regla.
- **INV-2 Conservación:** sin optimización de preparación aplicada, no hubo sustitución de transiciones verificadas.
- **INV-3 Aislamiento:** cada worker usa sus raíces HOME/XDG/TMP; el scratch de test se sacó del checkout (`test_010_004_t5_e2e`), y el aislamiento se verificó con el canario.
- **INV-4 Caché válida:** no se introdujo ninguna caché de preparación.
- **INV-5 Contabilidad:** `reconcile` verifica que un intervalo contribuya una sola vez; `preparation_s + remainder_s = sum_S_test` dentro de tolerancia.
- **INV-6 Honestidad:** el resto se publica como desconocido; una corrida descartada no acredita; los tres intentos fallidos quedan documentados.
- **INV-7 Separación:** cada rol en sesión propia; el reviewer no editó; el orquestador no hizo trabajo de rol.
- **INV-8 Calibración previa:** los intervalos se calibraron antes de la base (`calibrated: true`).

## Límites declarados (no dispensas)

1. **Carga del host en la pierna serial no instrumentada.** `close` no registra
   carga ni canario del checkout; esas dos condiciones del contrato de T7 **no
   quedan demostradas** en la pierna serial y así se declara. Sustitutos
   verificables: mismo `commit`, `dirty: 0` en ambos, resultados idénticos por
   nodeid y paredes seriales consistentes en cuatro corridas (4235, 4239, 4370,
   4459 s; ±5 %). Mejora pendiente para `close`.
2. **El resto (89.9 %) sigue desconocido.** No se clasifica por descarte.
3. **Familia de procesos:** la garantía requiere Linux (`prctl` + `/proc`); sin
   ella la corrida no se acepta (fail-closed).
4. **Un solo host y una sola repetición por régimen.** No se promete
   significancia estadística (spec §9).
5. **La huella del checkout no detecta cambios de modo** ni directorios vacíos;
   sí detecta altas, bajas y cambios de contenido.

## Qué no se acepta como acreditado

- El par de `83674246` (30.92 %) es **histórico**: se midió con un runner sin
  las correcciones *fail-closed* y no se usa como evidencia.
- Los intentos 1, 2 y 3 de la corrida final, con sus causas, quedan
  documentados y **no acreditan** nada.

## Decisión

Se acepta la feature `017-001-suite-performance` sobre la revisión `bf0e7483`,
con el objetivo de PC-4 cumplido (41.84 % ≥ 15 % con equivalencia exacta), las
doce postcondiciones cubiertas como se detalla, los invariantes conservados y
los límites anteriores declarados en lugar de omitidos.

**No autoriza** publicar ni desplegar: eso queda reservado al dueño.
