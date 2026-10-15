# Review formal (etapa 4) — 005-009-cli-delegation

- Veredicto: **OK** (sin bloqueantes; 2 familias de `make validate` preexistentes, documentadas abajo)
- Alcance del diff: `git diff 9f11b4f..HEAD` (17 archivos, +4736/−13): interfaz común + wrapper + referencia,
  adaptador OpenCode, reconciliación de spawn (SKILL.md + fuente orquestador + ref CC + 2 generados) y 4 ficheros de tests.
- Ejecutado read-only; nada editado ni aprobado; cero modificaciones de código/tests/state por parte del reviewer.

## Verificación ejecutada (comandos y salida)

| Qué | Comando | Resultado |
|---|---|---|
| Suite completa | `python3 -m pytest tests/ -q` | `734 passed, 1 skipped` en 935s (el 1 skip = PD-10 declarado) |
| Validadores | `make validate` | `Assert PASS: 141 / Assert FAIL: 2` (ver atribución abajo) |
| Paridad generados | `cdad-generate.py --runtime opencode/claude-code --stack odoo --profile optimus --out <tmp>` + sha256 | **22/22 agentes byte-idénticos** (incluidos los 2 del diff) |
| Estabilidad T2 | `pytest tests/test_005_009_t2_opencode_adapter.py -q` ×5 | 6/6 en las 5 corridas (14–15s cada una); flakiness documentada (10-11/40) extinguida |
| RED genuino | worktrees en `6d367e8` (T1), `5fd859d` (T2), `aca65c1` (T3), `6fc958d` (review-fix RED) | T1: 4 failed/0 errors, `AssertionError: RED: no existe la interfaz…` · T2: 5 failed/0 errors, puerta común aplicada · T3: 8 failed/8 passed/5 skipped (conservación en verde, INV-8 skips honestos) · review-fix RED: `AssertionError: 'environ.get("PWD"' is not None` — falla por la razón correcta |
| Atribución de `make validate` | worktree limpio en `9f11b4f` + `make staging` + `make validate` | **en base ya falla 1** (`validate-subagents.sh`: la instalación en HEAD difiere del repo, la instalación con 74 ficheros vs repo 73; instalación reservada al dueño) · la familia A3 (patrones privados) ya falla en base con el mismo fichero de patrones copiado mecánicamente sin leerlo |
| Portabilidad PD-8 | barrido de valores locales/de instalación (rutas absolutas de host, identidades de cuenta, direcciones de red, nombres de proveedor y de modelo concretos, nombres internos de proyecto) sobre los 4 productos nuevos + las líneas añadidas de SKILL/orchestrator/ref CC/generados | limpio |
| Independencia de cwd PD-3 | grep `environ|getenv|PWD` en interfaz+adaptador; lectura del código | solo `cwd=str(project_root)` explícito en subprocesos; cero resolución desde el cwd coordinador |

## Test ↔ postcondición

- **T1** (4): PD-1 (posición + control negativo + hash «agregar destino no edita la interfaz»), PD-2 (bytes transportados == PACKET.md; mismo ledger; state fuera de la frontera), PD-3 (cwd ajeno + forma cerrada I8 + provenance), PD-8 (dos configs → dos registros; unknown honesto). Sin huérfanos ni superfluos; separación en el fixture declarada (nunca lee skills/**).
- **T2** (6): PD-4 negativa/positiva, PD-5 (rc=0 sin señal → timeout, NO completed; señal → completed), PD-6 (vocabulario desde hechos, recibo pending), PD-7 (contexto acotado + una sola invocación + texto final durable), #6 review-fix cwd (PD-3/PD-8). Todos mapean a postcondición.
- **T3**: conservación SPAWN GUARD (3 fuentes + 2 generados), distinción co-ubicada (±80 líneas), proyección byte-idéntica por regeneración, INV-1 (único escritor), INV-4 (frontera de autoridad), INV-8 (sin promesas de sandbox). Consistencia estructural sancionada por la condición de aprobación del plan; no frases del prompt ni funciones internas (compruebo conceptos en ±80/15/20 líneas sobre artefactos publicados).
- **T4** (2 + 1 skip): entrega≠gate (recibo pending + reconcile → `received`/repeat `false`), interrupción (timeout no niega hechos; `dispatched-unknown`; read-only byte a byte) con-intento-material del binario falso; PD-10 skip con mensaje explícito (no verde fabricado).
- **Compararon RED→HEAD**: T1 solo ensancha el staging (árbol completo de la skill + paridad de nombres — refuerza, no debilita); T2 solo añade el test #6 y el regex PWD + docs del flaky; 8f6b812 solo hace SATISFACIBLE la aserción estructural (formateo perezoso), garantía intacta (verificado: en el árbol pre-fix la aserción falla exactamente en `environ.get("PWD"`). T3 y T4: sin cambios desde su RED.

## Revisión de los review-fix de T2

1. **d413c0c** (cwd): corrige sin máscara — elimina la resolución desde `os.environ["PWD"]`, resuelve el árbol SOLO co-ubicado al adaptador y falla cerrado con diagnóstico nombrado si está incompleto; el test de comportamiento (cwd ajeno sin escrituras) + la guarda estructural (regex PWD) han sido añadidos.
2. **15c8dab** (cota): correcto — `transport-error` desde el hecho material ya observable (rc≠0 sin señal — exactamente la clase (d) del oráculo aprobado), presupuesto `timeout − 1.0` con la invocación del destino acotada por ese mismo presupuesto → el adaptador siempre responde dentro de la cota recibida; la flakiness se extinguió: 6/6 en 5 corridas.
3. **Estabilidad reportada sostenida** (competencia del orquestador replicada): SÍ, medida 5/5 verdes (~15s cada una).

## Hallazgos — Bloqueantes: NINGUNO

### Opcionales (no prolongan el ciclo)

1. **Espera sin cota si falta `wait.timeout_seconds`** — Veredicto: OPTIONAL · Bucket: m · Axis: corrección/robustez.
   Evidencia: `cdad_delegate.py` (`_run_adapter(..., timeout=None)` y `subprocess.run` sin timeout si la config no trae `wait.timeout_seconds`) y `cdad_delegate_opencode.py` (`timeout=None` → invocación del destino sin cota). Consecuencia: con una config sin/wait mal cargado, PD-5 («espera ACOTADA») se degrada a espera indefinida de proceso; la interfaz podría no terminar jamás. Condición de cierre: falta de la cota → envelope `blocked` fail-closed (o cota default declarada) + un test negativo que lo fije.
2. **A3 falsificación en el fixture T1** — Veredicto: OPTIONAL · Bucket: l. Evidencia: `tests/validate-odoo-specialization.sh` A3 añade a su lista de hits `tests/test_005_009_t1_interface.py` porque el regex #1 (privado) captura una subcadena corta dentro de una palabra de la prosa del fixture (fixture prose, línea ~30); la familia ya fallaba en base (docs 004-003 ×2, `test_role_packets.py`). Consecuencia: ruido en `make validate`, sin fuga real (el host/producto está limpio). Condición de cierre: en la prosa del fixture, eludir la subcadena o actualizar `tests/.sensitive-patterns.local` (dueño del fichero privado).
3. **Frontera de presupuesto `_wait_budget` ≤ 1.0s** — Veredicto: OPTIONAL · Bucket: l. Evidencia: con `timeout_seconds` ≤ 1.0, budget=0.0 → `subprocess.run(timeout=0.0)` → TimeoutExpired inmediato → `transport-error` contra un binario sano. Condición de cierre: validación de sanidad (cota > reserva) con `blocked` + diagnóstico nombrado.
4. **«no polling loop» vs `POLL_INTERVAL_SECONDS` bounded** — Veredicto: OPTIONAL · Bucket: l. Evidencia: `cli-delegation.md` (~`:99`) exige adapter «…con no invented callback and no polling loop» mientras `_wait_signal` sondea a 50 ms dentro de la cota (el oráculo de T2 aprobado interpreta «sin sondeo EN BUCLE SIN LÍMITE»). Consecuencia: la prosa de referencia se excede sobre lo enviado; el drift se lee en los pasos del legado/otro periodo. Condición de cierre: alinear la prosa («no unbounded polling») o usar mecanismo bloqueante.
5. **`--packet-id` sin validación en el adaptador** — Veredicto: OPTIONAL · Bucket: l · Axis: seguridad. Evidencia: el adaptador concatena `args.packet_id` en `project_root/.cdad/packets/<id>` sin la guarda FLAT_NAME/»..» que sí tiene la interfaz; en la práctica se invoca solo vía interfaz (que valida). Condición de cierre: misma guarda o delegar en la interfaz exclusively.

### FYI

- Dos intents por delegación completing en el mismo ledger I8 (worker `opencode-…` por el adaptador + `delegate-opencode-…` por la interfaz): o prima `dispatched` — consistente con receive y con el oráculo de T4 (el attempt qualification queda abierto; documentado en el código; ok).
- La instalación en HEAD (`~/.claude`, `~/.config/opencode`, `~/.agents`) incluye los 2 scripts nuevos pero NO la distinción de spawn de T3 (fotografía intermedia): el re-instalado es acción del dueño (reservado); requisito previo del gate PD-10.
- Cambios sin comitear en `docs/.cdad-state.json` (registro del paquete de review) y `docs/specs/005-003-orientation-reduction/` sin trackear — registry del orquestador propio, fuera de este diff.
- El barrido A3 incluye `__pycache__` (artefacto no trakeado derivado de correr la suite): ruido de higiene.

### Abstenciones (declaradas)

- **PD-10 / recorrido real** : no hay evidencia del recorrido real (correcto, deliberado): el gate de integración/aceptación es del orquestador+dueño desde la instalación elegida; no puedo dictaminar sobre nada no registrado. La verificación honesta del skip ha sido comprobada (mensaje explícito, no verde).
- **VERIFY-3** (modo de carga vigente en la versión de OpenCode instalada): la entry soportada `mode: all` se fija con la evidencia de 2026-09-29; el soportado de la vigente no es verificable desde aquí (owner-loaded T4/T2).
- **`tests/.sensitive-patterns.local`**: no ha sido leído (path privado del packet); la atribución del A3 se hizo con sondas mecánicas por-patrón (booleanos, sin exponer contenido).
- **Familia A3 pre-existente** (docs 004-003, test_role_packets.py): prefecha el diff; la causa concreta del hit de esos ficheros no es parte de este dictamen.

## Dictamen por postcondición (resumen)

PD-1..PD-9: **verificadas** con evidencia archivo:línea + suite + RED + paridad (22/22 byte-idénticos) + barrido portable + tests del comportamiento del review-fix. PD-10: **gate del dueño, skip honesto declarado** (no bloqueante). Suite 734 passed / 1 skipped; `make validate` = 2 fails, ambos de familias **preexistentes en base** (F011 instalación vs repo — cierre vacío reservado al dueño mediante reinstall; A3 patrones privados — pre-existente, con 1 hit nuevo de falsificación por prosa del fixture).
