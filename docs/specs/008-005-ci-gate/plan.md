# 008-005 — Plan del gate de CI

## Steps

- [x] W0. Discovery y spec aprobadas (orquestador, HITL).
- [ ] W1. Contrato del veredicto y funciones puras (sin I/O).
- [ ] W2. `COLUMNS` en el entorno del hijo de `run_pytest_to_logs` (D3).
- [ ] W3. Entrypoint `scripts/cdad-ci-gate.py`: pasos, aplicabilidad, evidencia, resumen.
- [ ] W4. Regla de cotas de reloj en su única casa y agentes regenerados.
- [ ] W5. Ajustar los sitios de cota de los 5 archivos (T-A/T-B) leyendo el PC original de cada spec.
- [ ] W6. Documentar el entrypoint y la evidencia en `docs/ci-gate.md`.
- [ ] W7. Cerrar con los gates compartidos y una corrida verde atribuible.

## Detalle

### W1. Contrato del veredicto

El gate se escribe como módulo importable con funciones puras, para no necesitar una suite de 46-103 min
para verificarlo: `build_verdict(evidence)` (dict de entrada, dict de salida), `render_report(verdict)`
(texto) y `extract_failures(stdout_text, summary)` (lista de `{nodeid, reason|null}`). Sin lectura de
archivos ni subprocess en esas tres.

La costura al binario es `main(argv)` con `--repo-root`: los tests construyen un repo sintético con CLIs
grabadoras en `scripts/` (mismo patrón que `tests/test_008_002_suite_evidence.py`), observan argv y orden,
y no pagan la suite real.

### W2. `COLUMNS` (D3)

Agregar `COLUMNS` fijo (el valor medido completo por la discovery: `1000`) al entorno del hijo en
`scripts/cdad-suite.py:872-873`; el parser no cambia. Verificación: un intento sobre una selección con
skips de motivo largo expone el motivo completo en `attempt.json`; con el valor anterior queda vacío.

### W3. Entrypoint del gate

`scripts/cdad-ci-gate.py`, sin dependencias externas:

1. Resolver `--base` y su sha; crear la raíz de la corrida en exclusiva.
2. Enumerar y clasificar los cambios con el clasificador canónico.
3. Pasos 1-5 en orden; registrar `rc`, aplicabilidad y detalle.
4. Consumir `attempt.json`, construir el veredicto, escribir `gate.json` y `suite-report.md`, imprimir el
   resumen humano y salir con el código correspondiente.

Toda falla deja `gate.json` con su causa (PC-7). Sin `--base` → rc 2 con diagnóstico.

### W4. Regla de cotas de reloj

Agregar la regla al bloque `cdad-shared:convention-rule` de `sources/roles/test-writer.md` (casa única; el
reviewer ya la apunta, `sources/roles/reviewer.md:88-89`). No duplicar el texto en la spec ni en el plan.

Después: `make agents` y commitear las salidas declaradas de `agents/`; verificar
`python3 scripts/cdad-doctrine-check.py --quiet` rc 0.

### W5. Sitios de cota (17 verificados por el architect; el encargo decía 16)

| # | Archivo:línea | Cota hoy | Plazo que vigila | Promesa origen | Transformación |
|---|---|---|---|---|---|
| 1 | `tests/test_005_010_b1_last_assistant.py:164` | `< 5` (= `TEST_WAIT_TIMEOUT_SECONDS`) | `wait.timeout_seconds` 5 | 005-010 PD-5; la terminación ya se asserta | T-B |
| 2 | `tests/test_005_010_reviewfix.py:204` | `< 30` | cota de `wait` del caso R1 | 005-010 PD-5/INV-4; `termination == timeout` ya se asserta | T-B |
| 3 | `tests/test_005_010_reviewfix.py:405` | `< 5` | 5 | 005-010 PD-5 (R3) | T-B |
| 4 | `tests/test_005_010_t1_durable_signal.py:293` | `< 5` | 5 | 005-010 PD-2; `blocked` ya se asserta | T-B |
| 5 | `tests/test_005_010_t1_durable_signal.py:333` | `< 5` | 5 | 005-010 PD-2 (segundo caso) | T-B |
| 6 | `tests/test_006_001_reviewfix.py:556` | `< cota + 2` (12) | cota 10 | 006-001 PC-8/PD-7; el discriminador no es el reloj | T-B |
| 7 | `tests/test_006_001_reviewfix.py:720` | `< 3.5` | cota 2 | 006-001 PC-8 (agotamiento preparatorio: la cota es el sujeto) | T-A |
| 8 | `tests/test_006_001_reviewfix.py:735` | `< 3.5` | cota 2 | 006-001 PC-8/PD-7 | T-A |
| 9 | `tests/test_006_001_reviewfix.py:799` | `< 11.0` | cota 10 | 006-001 PC-8 (B3b) | T-A |
| 10 | `tests/test_006_001_t2_wait_recovery.py:904` | `< 3.0` | cota 2 | 006-001 PC-8 (agotamiento) | T-A |
| 11 | `tests/test_006_001_t2_wait_recovery.py:919` | `< 3.0` | cota 2 | 006-001 PD-7 | T-A |
| 12 | `tests/test_006_001_t2_wait_recovery.py:987` | `< hang - 1` (5) | hang natural 6 | 006-001 PD-7/PD-11 | T-A |
| 13 | `tests/test_006_001_t2_wait_recovery.py:1301` | `< 2.5` | cota 2 | 006-001 PD-11 (agotamiento) | T-A |
| 14 | `tests/test_006_001_t2_wait_recovery.py:1317` | `< 2.5` | cota 2 | 006-001 PD-11 (dentro de la cota) | T-A |
| 15 | `tests/test_006_001_t2_wait_recovery.py:1322` | `< 10.0` (presupuesto total) | 3 variantes × 2 | 006-001 PD-11 | T-A |
| 16 | `tests/test_006_001_t2_wait_recovery.py:1382` | `< 2.5` | cota 2 | 006-001 PD-11 (agotamiento) | T-A |
| 17 | `tests/test_006_001_t2_wait_recovery.py:1396` | `< 2.5` | cota 2 | 006-001 PD-11 (cota + margen) | T-A |

T-A = agrandar la separación del fixture para que el techo quede a ≥10× la conducta correcta y siga por
debajo del valor del defecto. T-B = degradar a liveness (la decisión que la cota custodiaba ya está
assertada en el mismo test), declarándolo como liveness y no como cota. Ningún sitio queda con techo igual
al plazo que vigila.

### W6. Documentación

`docs/ci-gate.md`: el comando, los cinco pasos, dónde queda la evidencia, qué no hace (sin runner, sin
publicación, sin secretos) y por qué no se versiona un workflow (política).

### W7. Cierre

1. `bash tests/validate-odoo-specialization.sh` → 68/0.
2. `python3 scripts/cdad-doctrine-check.py --quiet` → rc 0.
3. Suite focal de la feature y después la suite completa una vez, por el closer.
4. Una corrida del gate sobre el commit de cierre con árbol limpio: `gate.json` con `verdict: green`,
   `attributable: true`, `attempts: 1`.
5. Tres corridas consecutivas verdes son criterio del epic (008-001/008-002), no de esta feature.

## Riesgos

- **Gate verde no atribuible**: mitigado por PC-2/AC-2; el árbol queda sucio por `docs/.cdad-state.json`
  durante la operación, así que la corrida de cierre exige árbol limpio y eso es intencional.
- **Costo de la corrida de cierre**: 46-103 min; una sola corrida, sin reintentos.
- **Regla de cotas mal aplicada donde la cota es el sujeto**: la tabla fija T-A/T-B por sitio; el reviewer
  contrasta que ninguna decisión quedó sin assertar.
- **Deriva de agentes**: editar `sources/roles/test-writer.md` sin `make agents` deja las salidas
  desactualizadas; W4 lo incluye y la doctrina lo detecta.
