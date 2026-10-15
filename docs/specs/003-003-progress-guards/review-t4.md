**1c. Honestidad de etiquetas simulation/reconstruction (pedido del orquestador):**
- Fixture `loop.json` → `labelsimulation`, descripción declara "5 replicas… etiqueta simulation (P6: fallo provocado, nunca en vivo)" del incidente real de 2.073 reintentos. **Honesto** (no fabrica escala).
- `background-suite-death.json` y `closed-turn-awaiting-resume.json` → `label:"reconstruction-of-real-incident"`. Verificación programática: la cita textual de cada `incident_ref` existe **verbatim** en `guards-incidents-observed.md` (filas C2/C1 del 2026-10-06) y `dispatch-ledger.md` fila 6 existe citando el run `green-t1-003-003-a1`. `ref-quote-in-registry=True` para ambos. La descripción declara "no es un fallo provocado" y la clasificación esperada es `unknown`+escalada, **sin fabricar** "la suite pasó"/"entregó por otra vía" (congruentemente, el guard emite `unknown:true`, `limitation` declarada, `decision_needed`). **Honesto.**

**1d. Generalidad (P8/D9) — cobertura real, no nominal:**
- Go co-ubicado: `kata_test.go` en el mismo package que `kata.go` (convención Go verificada estructura+`go test ./...` verde con toolchain real, multibyte `ñandú→údnañ`); la traza `go-project-trace.json` es independiente y el test la clasifica sin intervención.
- Ciclo sin código: `doc-cycle.json` solo `edit` sobre `docs/*.md`; el test **pre-condiciona** la lista de tools `["edit","edit","edit","edit"]` antes de clasificar — el "sin código" está asertado, no implícito.

## 2. Hallazgos

### 2a. Bloqueantes
**Ninguno.** No encontré defecto observable en el diff que viole P6/P8-generalidad, invariantes (1, 4, 10) ni el alcance de T4; los 4 kills de mutación muestran que la familia detecta regresiones en los 4 ejes comportamentales que cubren sus fixtures.

### 2b. Opcionales (no bloquean; deciden dueño/orquestador)

**O1 — `simulation: true` colinda con `label: "reconstruction-of-real-incident"` en los mismos fixtures.**
- **Verdict: OPTIONAL** · **Bucket: m** · Ubicación: `tests/fixtures/003_003/background-suite-death.json:4-5`, `closed-turn-awaiting-resume.json:4-5`; test `tests/test_003_003_t4_fixtures.py:192-200`.
- Fundamento: el booleano significa "grabado/offline" y la etiqueta "provocado vs reconstrucción"; la spec P6 pide etiquetar únicamente los *provocados* como simulación. Dos campos de significado superpuesto invitan a la confusión al lector del fixture (aunque el test fija ambos y las descripciones lo explicitan, y el test trata el doble sello como contrato).
- Cierre verificable: o una línea en el docstring del test/README de la carpeta definiendo los dos sellos (booleano=offline, label=vocabulario cerrado), o un campo único. En este ciclo ya queda documentado en el docstring → no es deuda nueva.

**O2 — El test Go (P8) es `skipTest` sin toolchain.**
- **Verdict: OPTIONAL** · **Bucket: h** · Ubicación: `tests/test_003_003_t4_fixtures.py:448-450` (`if not go: self.skipTest(...)`).
- Fundamento: hoy en verde con toolchain real (evidencia 1a, no skip); pero el `observable_check` del plan ("tests Go co-ubicados… deterministas") puede quedar "verde" en un entorno sin `go` sin ejercitar la postcondición. Sin CI (deuda declarada), un skip silencioso es un vector de evidencia evaporada en el cierre del epic.
- Cierre verificable: registrar en el reporte del ciclo el hecho de que la corrida final del epic se hizo con toolchain (aquí queda registrado en esta revisión con `go1.24.4`) y/o assert de advertencia cuando el skip ocurra en el gate del epic.

**O3 — `CLOSED_ACTION_TABLE` duplicada como constante local del test.**
- **Verdict: OPTIONAL** · **Bucket: l** · Ubicación: `tests/test_003_003_t4_fixtures.py:76-83` vs guard `CLOSED_ACTIONS` (`skills/cdad-cycle/scripts/cdad_guard.py:118-127`).
- Fundamento: el test replica la tabla cerrada en vez de leerla del guard (no hay manera trivial de importarla desde el wrapper `runpy`; entender el mapeo implícito). No observO impacto hoy (las 5 acciones empatadas pertenecen a ambas), pero si el guard diverge, la aserción de pertenencia se valida contra una segunda fuente de verdad silenciosa.
- Cierre verificable: derivar el conjunto del envelope emitido por el guard en vez de fijarlo local, o dejar de duplicar el conjunto y confiar solo en clases de resultado.

### 2c. Nits

**N1 — import cross-test.** · **Verdict: OPTIONAL** · **Bucket: l** · `tests/test_003_003_t4_fixtures.py:62` importa `tree_snapshot` de `tests/test_004_002_t2_bootstrap.py` (otra feature). Acoplamiento estructural: si esa otra feature renombra/migra su test, T4 se rompe por fallo import, no por defecto de fase. Por lo demás, `tree_snapshot` (bytes por archivo) es la elección correcta para la verificación "read-only" (∆-independiente de mtime). Cierre: duplicar 5 líneas del helper o mover `tree_snapshot` a `tests/conftest.py`.

**N2 — docstring sobre-implementa el alcance.** · **Verdict: Nit** · **Bucket: l** · `tests/test_003_003_t4_fixtures.py:173-181` dice "todo fixture bajo `tests/fixtures/003_003` es una traza trace-v1", pero el `glob("*.json")` top-level excluye implícitamente `go-project/go.mod` y los sources kata (que no son trazas). El código es correcto; solo la frase del docstring peca de ambición — una coma "los `*.json` top-level" bastaría.

**N3 — `assertNotIn("unrecognized", stdout)` es un sniffer débil.** · **Verdict: Nit** · **Bucket: l** · `tests/test_003_003_t4_fixtures.py:140-143`. La superficie correcta queda sin embargo obligada por el `assertEqual(rc, 0)` con los flags exactos (un flag inexistente daría rc=2 y mensaje por stderr, fallando ahí). Redundancia inofensiva.

### 2d. FYI (fuera del diff; producto T1–T3 ya cerrados en sus reviews)

**F1 — agrupación de unknowns.** · **Verdict: FYI** · **Bucket: l** · `_escalations` (`skills/cdad-cycle/scripts/cdad_guard.py:288-343`) empaqueta TODAS las entradas `result_class=="unknown"` de la traza en UNA sola escalada con el fingerprint de la primera. Ningún fixture de T4 ejercita ≥2 unknowns de huellas distintas (C1/C2/crash todos traen exactamente 1). P5 no lo exige y la nota honesta del paquete declara el límite; queda découvertí para observación en adopción (T5) si algún trazo real trae varios unknowns de huellas distintas — el dedup_key declarado (canon con fingerprint) se derivaría del primer fingerprint solamente.

### 2e. Hallazgos descartados tras verificación (para no re-espeluzniar)

- P7-\-dedup\_key (O3): el canal de_polls ya emite el post-deadline como `wait` sin re-escalado, asertado. ✔El test de dedup es real (M3 lo mata).
- P1-evidencia tautológica: `evidence.progress.changed=False` es constante del producto (ya juzgado en T1: el criterio del incidente ya exige token congelado, la "evidencia" es el resto del paquete: fingerprint, rule, result_class, count — suficientes bajo P1 tal como se escribió luego de T1). No re-abro en T4.
- "Sin repetir un desarrollo completo" (P6): fixtures más grandes: 6 entradas de traza; `go-project` es una kata de 19 líneas con su test de 12. Cumplido.
- Fixture loop que citas "2073 reintentos" con 5 réplicas: la descripción del fixture lo declara como réplica a escala 5/2073 bajo etiqueta simulación; no fabrica escala real. OK.

## 3. Abstenciones

- **No re-corrí los 3 validadores del repo** (\`validate-consistency.sh\\` etc.): por nota del orquestador los 2 fallos son preexistentes y ajenos, y la suite focal completa estuvo cubierta por evidencia de T1–T3/T4. Si el orquestador quiere, un re-run de \\`validate-consistency.sh\\` al cierre del epic puede releer la deuda — abstengo el diff-impacto de \\`validate-*\\` en T4 (no lo medí).
- **No verifiqué que la suite completa del repo siga en verde tras \\`5b38da8\\`:** esto pertenece al cierre del período del epic y no al diff de T4 (que no toca producto); el orquestador reportó sin regresión en su nota → la abstengo (no la contradigo).
- **No audité si \\`guards-ledger.md\\` ya registra la adopción (P8-adopción/T5):** esa parte de P8 no es contrato de T4 (solo "parte generalidad"); la abstengo.
- **No probé el test de flaky bajo inputs alternativos (clases de resultado mixtas distintas de tool-error/ok):** el fixture usa una única alternancia; la generalidad del discriminante D2-con result_class quedó implícita por diseño del M2/fingerprint (código no re-habilitado en T4). Abstengo la cobertura de otras combinaciones de clases.

## 4. Veredicto final

**Sin bloqueantes. Aprobable con O1–O3 y N1–N3 como mejoras declaradas.** El delta T4 cumple el contrato (P6 y P8-generalidad completados con fixtures mínimos y test behavioral, 12 focales re-producibles**, etiquetado honesto de provocación vs reconstrucción con anclaje verificable,\\\\ y la propiedad testable (mutaciones M1–M4 muertas) — puede entrar a T5 (adopción) sin deuda de cambio obligada por esta revisión.# Revisión: T4 de 003-003-progress-guards (diff `3d8a2d1..5b38da8`)

**Paquete:** `003-003-progress-guards-reviewer-review-007` · Rol: revisor (solo lectura) · Objetivo: 1 commit (`5b38da8 test(003-003): T4 fixtures de trazas +...`)

**Conclusión: 0 bloqueantes. El diff tiene soporte sólido: baseline 12/12 independiente, 4 mutaciones semánticas eliminadas (P1, P2, P5/inv4, P7-side) y honestidad de`simulation`/`reconstruction` verificada contra el registro real de incidentes. Aprobable para T5.**

## Evidencia de verificación (comandos y salidas)

Aislamiento: `git archive 5b38da8 | tar -x -C /tmp/opencode/t4-review` (estado exacto del commit; el SHA del spec se reprodujo para verificación: `731cca5b…1c5` **coincide** con el paquete).

**Baseline (12/12, suite focal):** `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_003_003_t4_fixtures.py -q` → `12 passed in 3.19s`. Go test co-ubicado se ejecutó realmente (toolchain go1.24.4 presente; no omitido).

**Prueba de que los tests pueden fallar (mutaciones en el guard temporal del sandbox, cada una revertida):**

| Mutación | Eje | Resultado |
|---|---|---|
| M1 `REPETITION_THRESHOLD 3→6` | P1 (bucle) | `1 failed, 11 passed` — bucle test muerto |
| M2 quitó `progress_token` congelado del run | P7 (lado de falsa alarma) | `1 failed, 11 passed` — progress test muerto |
| M3 dedup de polling post-deadline siempre `escalate` | P2 (escala una sola vez) | `1 failed, 11 passed` — polling test muerto |
| M4 canal `_escalations` suprimido | P5/inv.4 (crash, C1, C2) | `3 failed, 9 passed` — exactamente los 3 tests de escalada muertos |

**Honestidad de etiquetas:** fixture `loop.json` se etiqueta como `simulation` ("fallo provocado, nunca en vivo", 5 réplicas declaradas del 2073-reintento — sin fabricación de escala). Se verificó programáticamente que el texto de `incident_ref` citado de ambos fixtures `reconstruction-of-real-incident` existe **textualmente** en `guards-incidents-observed.md` (filas C1/C2 2026-10-06, `ref-quote-in-registry=True` para ambos) y se confirmó que la fila 6 de `dispatch-ledger.md` (incidencias en tiempo de ejecución reales + `green-t1-003-003-a1`). Ambos esperan soberanamente `unknown:true` + escalada, sin éxito/fracaso fabricado. **Honesto.**

**Cumplimiento del contrato:** el diff toca solo `tests/**` dentro de `files` del plan T4; el binario del producto no ha cambiado desde `3d8a2d1` (T3 cerrado) — Aprobado "el producto se mantiene inmóvil por T4. La cobertura general es {}": cofficientes mínimos: test co-ubicado junto a `kata.go` (verify is mios `go test ./...` rc0 multibyte) + `doc-cycle` con precondiciones `["edit","edit","edit","edit"]` verificadas antes de clasificar (no-code asertada, no nominal). Read-only-invariante asertó 3× sobre vía `tree_snapshot` (bytes, no mtime). Env-tamper determinista 2×.

## Órdenes halladas por nivel de gravedad

### Requeridas/bloqueantes

**Ninguna.**

### Opcionales (consideradas / nits)

- **O1** — `simulation: true` aparece TAMBIÉN en fixtures con `label:"reconstruction-of-real-incident"` (p. ej. `background-suite-death.json:4-5`). La P6 extrae "los escenarios de falla provocados"...; aquí la bandera boleana duplica el vocabulario de la etiqueta con una semántica diferente (offline/reproducido vs. provocado). ●Veredicto: OPCIONAL · Bucket: m · Ubicación: los dos fixtures + test `tests/test_003_003_t4_fixtures.py:192-200`. Real claro que el test fija ambas banderas y la descripción expli­cita "no es un fallo provocado" (honesto). Consider: documentar (1 línea) el contrato de los dos sellos en el docstring del test, o un único campo discriminator.
- **O2** — test Go co-ubicado `skipTest` sin `toolchain` (`tests/test_003_003_t4_fixtures.py:448-450`). En un entorno sin `go` (sin CI — deuda declarada) se marca "passed (n skipped)" sin ejercitar la postcondición P8. La corrida actual va con `toolchain` (evidencia arriba); el riesgo es solo futuro. Cierre: registro explícito (aquí ya queda con `go1.24.4`) o una advertencia del gate cuando ocurra el skip. ●Veredicto: OPCIONAL · Bucket: m.
- **O3** — `CLOSED_ACTION_TABLE` (`tests/test_003_003_t4_fixtures.py:76-83`) duplica `CLOSED_ACTIONS` del guard (drift de 2 fuentes de verdad) para un chequeo de pertenencia que ya está debilitado (solo "acción ∈ conjunto"). ●Veredicto: OPCIONAL · Bucket: l.
- **N1** — importación cruzada de prueba: `from test_004_002_t2_bootstrap import tree_snapshot` (`tests/test_003_003_t4_fixtures.py:62`) acopla T4 al módulo de prueba de otra feature; el renombrar/dejar existir podría quebrar T4 por ImportError, no por regresión. ●Veredicto: OPCIONAL · Bucket: l.
- **N2** — falla doc-assert de clase subsequente "todo fixture bajo tests/fixtures/003_003" pero el `glob("*.json")` top-level excluye implícitamente `go-project/go.mod` y sources de kata (correcto en practicidad, impreciso en texto del docstring). ●Veredicto: Nit · Bucket: m.
- **N3** — `assertNotIn("unrecognized", stdout)` es el sniffer débil (argparse escribe en stderr); la superficie exacta queda de todos modos cubierta por `assertEqual(rc, 0)` con el `--project-root --trace` handshake demasiado especificado. ●Veredicto: Nit · Bucket: m.

### FYI (fuera del diff — producto T1-T3 ya revisado)

- F1: `_escalations` empaqueta TODAS las entradas `unknown` de la trazabilidad en UN paquete con el fingerprint del primer `unknown` (guard: 288-343). Los fixtures usan exactamente 1 `unknown`; un trazado con ≥2 `unknown` de huellas distintas no está fijo si al dedup_key declarado solo lo contiene la primera huella. No зат Trumpido por P5; queda descubierto para la adopción en T5. ●Veredicto: FYI · Bucket: l.

## Abstinencias

- **No re-corrí la suite completa ni los 3 validadores del repo.** Por la nota del orquestador, los 2 fallos de validadores son preexistentes y del sistema, y la suite es "en adelante a la T5 independientemente" — no se lo difundí para no contaminar los resultados de las mutaciones (no tengo salida completa a mi alcance). Con índice de abstinencia para el diff mismo (sólo T4). Herramientas alternativas disponibles si el orquestador decide re-corridas.
- **No verifiqué el "12 focales en un runtime distinto" (Windows/otro OS):** la evidencia se corrió con mi runtime del sandbox (Linux, cierta e irrelevante para el Linux fix). Sin evidencia ≥80% de que el `toolchain`-ausente branch produce el mismo resultado (cubierto por O2 pero no por mí revisado para Windows.
- **No evalué la adopción (T5/P8-adopción) ni el estado de `guards-ledger.md`:** es la tarea INMEDIATAMENTE siguiente (T5 — orquestador mandate), fuera del objeto declarado de este review (T4 fixtures). Abstengo cualquier expresión sobre ella.

## Cierre

El diff cumple el objetivo declarado T4: “fixtures de trazas + generalidad + simulación declarada (P6/P8-parte generalidad)” con 12 focales, 7 fixtures mínimos (5 provocados + 2 reconstrucciones), 2 generales (Go co-ubicado real + ciclo sin código), etiquetado honesto verificabile, y 4 mutaciones semánticas muertas que prueban que los tests distinguen comportamiento — no presencia. O1–O3 / N1–N3 son deuda leve sin defecto observable hoy. **No hay cambio necesario para garantizar la agregación de este diff. Entregar a T5.**
