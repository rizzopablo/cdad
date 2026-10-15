# Evidencia de utilidad — casos concretos (epic-003, 2026-10-05)

Registro de uso real del sistema construido en epic-004 mientras se desarrolla
epic-003. **Sin maquinaria nueva**: son casos tomados de los registros existentes
(`dispatch-ledger.md`, `supervision-record.md`, `docs/runtime-adopted-version.md`).
Los números son observados; lo que no se midió queda declarado **desconocido**.

---

## 1. Una ejecución REUTILIZADA y por qué es válida

**Caso:** el orquestador reutilizó la corrida de suite del implementer en lugar de
re-ejecutarla, en varios cierres.

| Dónde | Ejecución reutilizada | Por qué es válida |
|---|---|---|
| 004-003 T1–T5 | suites 331/333/338/340/345/353/356/364 **citadas**, no re-ejecutadas | identidad de producto (mismo commit), de tests (el rango no toca `tests/`), de selección (`tests -q`) y de entorno (misma máquina, `env -u TMPDIR`); el árbol no cambió entre la corrida y el cierre |
| 003-002 T1 | 371 passed citada por el reviewer de T1 | el único cambio posterior era `docs/.cdad-state.json` (binding del orquestador), que no afecta al producto |

**Regla aplicada:** la reutilización exige equivalencia de **producto + tests +
selección + entorno**. Cuando alguna falla, la evidencia se descarta.

**Contraejemplo registrado (reutilización RECHAZADA):** en T2 el orquestador
encontró que el lock `R4a` era **flaky** aunque el rol reportaba «6/6». La
reutilización de esa evidencia se rechazó y se re-corrió: el resultado real fue
3/3/3/4 fallas. **Una cita no se acepta sin verificar su reproducibilidad cuando el
resultado es un lock que debe ser determinista.**

---

## 2. Un cambio que EXIGE una ejecución nueva y qué evidencia invalida

| Cambio | Evidencia invalidada | Por qué |
|---|---|---|
| `32d290c` / `5c76fee` (cambio de producto en `cdad_result.py`) | toda la suite previa | cambia el producto ⇒ el «mismo árbol» deja de valer |
| `27c2a39` / `8333649` / `feed7e1` (cambio de **tests**) | la suite previa | cambia el conjunto de tests ⇒ el total ya no es comparable |
| `675c18e` (regeneración de salidas declaradas) | la suite previa | cambian artefactos que el producto consume |
| Adopción de una versión nueva (`8cb6580`) | la evidencia de la versión anterior | cambian las instrucciones/herramientas que ejecutan los roles |
| Cambio de política (`policy_sha256`) | prepare/resume/dispatch y la evidencia de la revisión anterior | el contexto de ejecución exige reconciliación |

**Qué invalida exactamente:** un cambio en (a) el producto, (b) los tests, (c) la
selección declarada, (d) el entorno relevante, o (e) la política/versión. Un cambio
**solo** en documentación de estado (`docs/.cdad-state.json`) **no** invalida la
evidencia de producto — y así se registró explícitamente cada vez.

---

## 3. Fricciones, repeticiones improductivas y retrabajo (observados)

1. **La suite en background muere con la sesión del subagente.** Ocurrió **5 veces**
   (3 en 004-003: implementer T2, reviewer T3, reviewer T5; 2 en 003-002: reviewer T1,
   reviewer T2). Costo: una reanudación por caso (~5 despachos extra). **Fricción
   operativa del runtime, no del método.** Mitigación adoptada: pedir la suite en
   primer plano; y al reanudar, citar la corrida vigente por PD-5 en vez de repetirla.
2. **Un lock flaky es peor que ninguno.** `R4a` (T2) se entregó con una carrera
   SIGSTOP/SIGKILL: fallaba ~1 de cada 3. Detectado por el orquestador re-corriendo
   (el rol reportó 6/6). Retrabajo: 1 reanudación. **Lección registrada:** el
   orquestador debe re-correr los locks, no aceptar el reporte.
3. **Un test con defecto propio se disfraza de RED válido.** El RED de T3 tenía 13
   fallas «correctas» pero **una** era un `AttributeError` por un helper inexistente
   (`append_to`). Se detectó recién en el GREEN. Retrabajo: 1 reanudación.
   **Lección registrada:** verificar la **razón** de cada falla, no el conteo.
4. **Espiral de variantes en la revisión (T3, 3 rondas).** El reviewer encontró, en
   rondas sucesivas, variantes del mismo defecto de ligadura `argv`↔selecciones
   (`R1` → `F1` → `R-F1a/b` → `R-F1c`). Cada hallazgo era correcto y **ninguno cerraba
   la familia**. Costo: 3 rondas de RED/GREEN/re-review sobre el mismo eje.
   **Disposición del dueño:** calibración de la review (proporcionalidad, cierre por
   clase, usabilidad como criterio) — `docs/owner-decision-review-calibration-2026-10-05.md`.
   Aplicada: remedio de **clase** fail-closed en **una** ronda (`5c76fee`), que cerró
   `R-F1a/b/c` juntos. **Este es el retrabajo más caro del ciclo y el que produjo la
   mejora de proceso más valiosa.**
5. **Defecto posterior (post-GREEN) que el diseño debía haber previsto.** El RED de T1
   no cubría la batería focal que el propio plan declaraba (interrupción + dos
   procesos): el reviewer lo marcó bloqueante (R2) y se agregó como locks en el
   review-fix. No fue un defecto del producto sino del **oráculo** — el test-writer no
   cubrió lo que el plan pedía.

---

## 4. Tiempo de pruebas observado (tokens: DESCONOCIDO)

Tiempos de suite completa **observados** (no estimados) durante el ciclo de 003-002:

| Momento | Resultado | Tiempo |
|---|---|---|
| T1 RED (baseline) | 364 passed | 620.78 s (worktree fijado) |
| T1 GREEN | 371 passed | 493.80 s |
| T2 GREEN | 389 passed | 772.83 s |
| T2 review-fix GREEN | 401 passed | 684.08 s |
| T3 GREEN | 413 passed + 1 falla de test | 622.62 s |
| T3 review-fix r1 | 422 passed | 620.34 s |
| T3 review-fix r2 | 427 passed | 565.41 s |
| T3 review-fix r3 (clase) | 433 passed | 586.92 s |
| Calibración | 433 passed | 595.86 s |
| Re-review final (verificación independiente) | 433 passed | 583 s |

Focales (orden de magnitud): T1 5–9 s · T2 13–18 s · T3 7–30 s · review-fixes 5–60 s.

**Lo que estos números NO dicen:** no son «ahorros» ni comparaciones de modelos; son
duraciones de corrida en una máquina, con la suite creciendo de 364 a 433 tests.
Convertirlos en causalidad sería fabricar un dato.

**Tokens: desconocido.** El entorno no expone el consumo por sesión; no se estima a
partir de tamaños de archivo.

---

## 5. Lo que la evidencia sostiene y lo que no

- **Sostiene:** la reutilización de evidencia vigente es real, verificable y ahorra
  corridas completas (10 citas válidas en el ciclo); la delegación por unidades
  coherentes funcionó (cada tarea cerró con su ciclo completo); la revisión
  independiente encontró defectos materiales que el orquestador no había visto
  (R1 de T2: escape de autoridad, **reproducido**; R1 de T3: alcance auto-elegido).
- **No sostiene:** ninguna afirmación de ahorro porcentual, de causalidad entre
  cambios y tiempos, ni de equivalencia entre configuraciones de modelos. El objetivo
  de <100k de contexto sigue **sin medir** (el entorno no expone la métrica).
