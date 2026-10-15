# Registro de supervisión PD-17 — 004-002 (orquestador Claude)

Formato de 004-001: (a) resultado frente al contrato, (b) ámbito de cambios,
(c) desviaciones con su disposición proporcional (ADR-011).

## T1 — Política y clasificación (cerrada 2026-09-30)

- **(a) Resultado vs contrato:** PD-1, PD-2 y PD-9 con interfaz I1
  (`validate-policy`, `prepare --propose-policy`).
  - RED `f675ff3` (22) + corrección del oráculo `49d2ebf` (23; D1–D4
    detectados por el implementer, D5 agregado por el orquestador).
  - GREEN `7d48922`.
  - Review de Codex/astra: **changes-required** (B1 conflictos co-ubicados,
    B2 symlink de la política, B3 exclusividad de la propuesta, más O1–O4).
  - Review-fix: RED `8c079de` + `45c95cf`; GREEN `a62ab68`.
  - Re-review: B3 residual (valores vacíos) → RED `3050a8f`, GREEN `2ca91f9`,
    verificado por el orquestador (diff + sonda del reviewer, rc=2).
  - 7/7 mutaciones del reviewer detectadas.
  - **Suite completa reproducida por el orquestador en `2ca91f9`: 163
    passed** (`env -u TMPDIR`, 738 s). odoo-specialization PASS;
    consistency: solo F011, esperado (productor fijado, sin reinstalar
    hasta el corte C).
- **(b) Ámbito:** `skills/cdad-cycle/scripts/cdad_packet.py`, en los tres
  commits de implementación; `tests/test_004_002_t1_policy.py` y
  `tests/test_004_002_t1_reviewfix.py`. Diffs revisados por el reviewer y
  por el orquestador.
- **(c) Desviaciones y disposición:**
  - **Oráculo defectuoso en el primer RED** (fixtures rotos, D4
    contradictorio con PD-9). El implementer se detuvo sin tocar tests,
    como corresponde. Disposición: corrección por el test-writer; el
    orquestador decidió D4 a favor de PD-9.
  - **Tests de B1 que pasaban por otro conflicto** (`implementation_roots`
    solapado en el fixture). Detectado por el orquestador reproduciendo B1.
    Disposición: fixture exacto provisto al test-writer.
  - **El implementer leyó `tests/.sensitive-patterns.local`** para
    diagnosticar un falso positivo de A3; la lista local pasó por el
    proveedor del modelo. Disposición: registrar; instrucción explícita en
    los paquetes siguientes (no leer esa lista, reportar la línea). Sin
    barrera nueva.
  - **El test-writer ejecutó `git checkout` sobre un archivo de
    implementación** (no-op, contenido idéntico). Disposición: registrar y
    recordarle el principio.
  - **A3 es demasiado amplio:** uno de los patrones locales coincide como
    subcadena dentro de un identificador de código común (falso positivo).
    Follow-up fuera de 004-002: acotar los patrones a palabra completa. El
    patrón concreto no se nombra aquí, porque la lista es privada.
  - **Codex llegó a su límite de uso;** se reintentó tras el reset (01:43)
    sin cambiar de modelo.
  - **Tiempos:** la suite completa tarda 12–20 min. Decisión de proceso: en
    RED, solo el archivo focal y `--collect-only`; la suite completa, una vez
    por GREEN (implementer) y una en el cierre (orquestador).
  - **Hallazgo lateral para T6 (PD-12):** en un checkout limpio fallan 6
    tests porque dependen de `build/staging` (ignorado por git).
  - **O1 diferido a T6:** inferencia de layouts de la propuesta (tests de
    Odoo, co-ubicados sin raíz).
  - **Error del orquestador (2026-09-30):** este registro nombró el patrón
    sensible y la palabra que lo contiene; A3 lo detectó. Corregido sin
    nombrarlo. El texto sigue en el historial local de `c0511e1` (no hubo
    push): antes de publicar el repo, sanear ese commit.

## T2 — Bootstrap autorizado e identidad (cerrada 2026-09-30)

- **(a) Resultado vs contrato:** PD-3, PD-4 y PD-10 con las interfaces
  I2 (autoridad desde `stage_history` + `hitl_delegation`), I3 (bootstrap
  implícito, `--new-execution`), I4 más su refinamiento (v1 explícito y
  legacy sin política) e I7 (reanudar sin opciones ordinarias).
  - RED `ee28dd2` + `91d0310`; GREEN `114709a`.
  - Review Codex/astra: **6 BLOCKING** (F1 vigencia al reutilizar; F2 epic
    terminal y scope por subcadena; F3/F4 resume sin validar, con
    recorrido de rutas; F5 rollback incompleto con traceback; F6 fallback
    legacy ante política inválida).
  - Review-fix: RED `50aebe7`; GREEN `2aafe5f`; micro-ciclo I7 `37f8aec` +
    `809ba1a`.
  - Re-review del suplente Opus (Codex sin cuota): B1 autoridad no
    centralizada, B2/B3 tests que pasaban por la razón equivocada →
    `04ec226` + `6cea734`.
  - Verificación de cierre (Opus): **approved**, con todas las mutaciones
    sobrevivientes detectadas.
  - **Suite completa reproducida por el orquestador en un worktree fijado en
    `6cea734`: 199 passed** (sin los RED de T3/T4, que pertenecen a otras
    tareas).
- **(b) Ámbito:** `skills/cdad-cycle/scripts/cdad_packet.py`;
  `tests/test_004_002_t2_bootstrap.py` (incluye un cambio de oráculo firmado
  por el orquestador para I7) y `tests/test_004_002_t2_reviewfix.py`.
- **(c) Desviaciones y disposición:**
  - **Defectos en los tests escritos por el test-writer**, en tres
    ocasiones: un kwarg espurio; una mutación en memoria sin persistir; dos
    tests F4 y los subtests de I7 que pasaban por I7 en vez de por la lógica
    que dicen probar. Los dos primeros los detectó el implementer, que se
    detuvo sin editar tests. El tercero lo detectaron el reviewer con
    mutaciones y el orquestador. **Patrón a vigilar:** tests negativos que
    fallan por un motivo anterior al que dicen probar. Disposición: el
    reviewer exige mutaciones por garantía, y los paquetes de RED piden un
    argv mínimo por caso.
  - **Parche del implementer para una tensión entre tests** (comparar
    opciones solo con el paquete no activo), que dejaba F3 sin efecto. El
    orquestador no lo aceptó y resolvió con la decisión I7.
  - **Un RED descarrilado:** tras un corte del proveedor, el modelo respondió
    sin contexto y terminó sin trabajar. Se redespachó. En el segundo
    intento la sesión terminó sin commit y el orquestador materializó el
    artefacto, dejando constancia de la autoría.
  - **Codex sin cuota dos veces:** en T1 se reintentó tras el reset; en T2
    se aplicó el suplente Opus (regla del dueño).
  - **Error del orquestador:** `pkill -f` con un patrón que coincidía con su
    propia línea de comandos mató su shell. Ya estaba registrado en memoria;
    ahora se mata por PID.
  - **Error del orquestador:** una suite corrida en el árbol compartido
    mientras el implementer de T3 editaba no vale como evidencia. Se repitió
    en un worktree fijado. Regla: la evidencia de cierre se corre en un
    worktree fijado en el commit que se cierra.

## T3 y T4 — Consistencia durable y registro de despacho (cerradas 2026-10-01)

T3 y T4 se cierran juntas: la segunda y la tercera corrección tocaron las dos.

- **(a) Resultado frente al contrato:**
  - T3 (PD-5, PD-11; I5, I6): RED `df2adfa`, GREEN `954f14c`. T4 (PD-6; I8):
    RED `3fc6776`, GREEN `860b60f`.
  - Primera review de T3 (Codex `gpt-6-astra`): F1–F6 y O1, con tres
    críticos (exclusión, carrera, borrado ajeno) → RED `944fb06`/`d8440b4`,
    decisión I5c del orquestador, GREEN `fc184c1`.
  - Re-review de T3 + review de T4 (suplente Opus; Codex sin cuota):
    A-1 crítico (el perdedor borraba el `.lock` del tenedor: F2
    reintroducido), A-2/B-3, B-1, B-2, más cobertura A-3, A-4, B-4, B-5 →
    I5d, RED `ab5d403`…`291c492` + `bde2fb0`, GREEN `814c980`.
  - Verificación GLM (`review-t34-rf2.md`): siete garantías cerradas con
    sondas propias (incluido un SIGKILL real entre los dos renames) y 9/11
    mutaciones detectadas; dejó R-1 (reconcile admitía `--input`) y R-2 (la
    rama de reintento de B-1 sin test) → RED `c605f9c`, GREEN `903a3c4`
    (R-1 y el nit R-4). El orquestador verificó que el test de R-2 mata
    M-B1b por la razón correcta y revisó el diff de `903a3c4`.
  - **Suite completa reproducida por el orquestador en un worktree fijado en
    `903a3c4`: 261 passed, EXIT=0, en 17 min** (sin los RED de T6, que pertenecen a esa
    tarea; incluye T5).
- **(b) Ámbito:** `skills/cdad-cycle/scripts/cdad_packet.py`; tests
  `test_004_002_t3_durable.py`, `t3_reviewfix.py`, `t4_dispatch.py`,
  `t34_reviewfix2.py`, `t34_reviewfix3.py`, el helper `_rf2_open_pause.py`
  y la enmienda p1 de `test_packet_prepare.py`.
- **(c) Desviaciones y disposición:**
  - **Concurrencia:** dos defectos críticos de exclusión (F2 y su
    reintroducción como A-1) solo aparecieron con sondas de carrera
    adversariales, no con los tests del RED. Disposición: puntos de pausa
    deterministas (I5b, I5d) y mutaciones por garantía en cada review.
  - **Helpers del test-writer que inyectaban opciones ordinarias**: seis
    tests de reconciliación pasaban por la razón equivocada. El implementer
    se detuvo sin editar tests (bien); se corrigieron con argv puro
    (`bde2fb0`). Es el mismo patrón ya vigilado desde T2.
  - **Implementer:** `git stash` de sus propios cambios para comparar (estado
    compartido). No causó daño; se registró y el principio se repite en cada
    paquete. En otra ronda dejó la suite en segundo plano y su turno terminó
    sin resultado: el orquestador esperó el `EXIT=` y lo retomó para el
    commit. Los paquetes ahora piden correr en primer plano.
  - **R-3** (marcador `.cdad-txn` no autenticado) se acepta como limitación:
    plantarlo exige escribir dentro de `.cdad`, estado del orquestador fuera
    del modelo de amenaza de PD-11.
  - **Proveedores:** Codex sin cuota hasta el 2026-10-03 y un corte del
    límite semanal de Opus; se aplicó la regla de suplencia y después la
    enmienda de modelos del 2026-10-01 (reviewer de rutina
    `glm-5.3-flash`).
  - **Error del orquestador:** un heredoc sin comillas ejecutó el comando de
    pytest citado en un objetivo y metió su salida en el paquete de la review
    de T5. Se mató el proceso por PID, se anuló el paquete y se redespachó
    (ledger). Regla: heredocs de objetivos siempre con `'EOF'`.

## T5 — Mecanismos runtime: agentes OpenCode por proyecto y guard CC dinámico (cerrada 2026-10-01)

- **(a) Resultado frente al contrato (PD-7, PD-8; I9, I10; C2):**
  - RED `c5ddd88`; GREEN `dd6448e`.
  - Review GLM (`review-t5.md`): B1 (el guard dejaba al implementer editar
    la política y los derivados), B2 (`path="."` evadía el bloqueo de
    búsqueda global), B3 (los mapas OpenCode ampliaban la política), R1–R10;
    el orquestador agregó B4 (`pattern` de Glob sin mediar) y B5 (raíz por
    cwd en vez de `CLAUDE_PROJECT_DIR`). RED `d47ea15` + control corregido
    `e003899`; GREEN `cc3ac72` (guard), `90c55c6` (CLI).
  - Review combinada (`review-t56.md`, parte A): 16/17 mutaciones eliminadas
    (el superviviente lo sostiene una segunda capa); B6 nuevo (rutas `~` en
    el guard v2) → RED `aa966fe`, GREEN `b1cfacd`, diff revisado por el
    orquestador.
  - C2 cumplida en forma: el guard media `Grep`/`Glob` por su forma real de
    entrada (`path` y `pattern`), con tests de la forma real. La prueba en
    una sesión real queda para T7 (C1).
- **(b) Ámbito:** `scripts/claude-code-path-guard.sh` (rama v2; el bloque
  legacy sin política quedó byte a byte, verificado en cada review);
  `skills/cdad-cycle/scripts/cdad_packet.py`; tests
  `test_004_002_t5_runtime.py`, `t5_reviewfix.py`, `t56_reviewfix.py`.
- **(c) Desviaciones y disposición:**
  - **Controles de oráculo defectuosos**: el control de B1 exigía que el
    implementer pudiera editar tests (contra PD-7). El implementer se detuvo
    sin editar tests; un micro-ciclo del test-writer lo corrigió.
  - **Fail-open declarado como diagnóstico** (R9): con política y sin
    agentes de origen, `prepare` avisa y no falla, porque un proyecto puede
    usar solo Claude Code. Limitaciones aceptadas: R4, R5 (costo de un
    `python3` por llamada mediada, a medir en T7), R8, R10, OPT-3.
  - **Error del orquestador**: un heredoc sin comillas ejecutó el pytest
    citado en el objetivo de la review y contaminó el paquete; se anuló y
    se redespachó (ledger).

## T6 — Aterrizaje utilizable (cerrada 2026-10-01)

- **(a) Resultado frente al contrato (PD-10, PD-12; I4):**
  - RED `08af34f`, `f50c3d8`, `c84fe49`; oráculo corregido `33a20db`.
  - Transformación previa del portador v1→v2 de los suites heredados
    (filas 3–9 de `v1-fixture-trace.md`): `c50f521`, `47109ff`, con la suite
    en verde contra el código anterior al GREEN.
  - GREEN `87bca83` (instalación desde staging, sin `agents/`), `20be19c`
    (retiro de I4 con diagnóstico), `697a61a` (guía instalada).
  - Review combinada (parte B): recorrido completo desde una instalación
    aislada propia del reviewer en verde (propuesta → bootstrap → I9 →
    resume → record-dispatch → reconcile; guard instalado; legacy;
    standalone; v1 explícito rechazado sin escrituras). B7 (la guía
    prometía reanudar tras reconciliar y el CLI no podía) → decisión I11 del
    orquestador, RED `aa966fe`, GREEN `4b6134e` + `28324af`; OPT-1/2/4
    corregidos; OPT-5 corregido en la trazabilidad.
- **(b) Ámbito:** `install.sh`, `skills/cdad-cycle/scripts/cdad_packet.py`,
  `skills/cdad-cycle/references/project-execution.md`, `SKILL.md`; tests
  `test_004_002_t6_landing.py` y los suites heredados de las filas 3–9.
- **(c) Desviaciones y disposición:**
  - **Dos defectos de oráculo en el RED de T6** (precedencia en Python; un
    segundo `prepare` que contradecía PD-4). El implementer se detuvo y los
    reportó; el orquestador los verificó y un micro-ciclo del test-writer los
    corrigió sin debilitar aserciones.
  - **Error del orquestador**: el paquete de transformación pedía al
    test-writer editar `v1-fixture-trace.md`, fuera de su ámbito. El rol se
    negó con razón y entregó el texto; el orquestador lo materializó.
  - **Celdas retiradas** de la matriz heredada (fila 3): dependían de la
    rama por política de modelos (ADR-010), que la spec v2 elimina; el
    reviewer las verificó contra la spec.

**Suite de cierre de T5 y T6 reproducida por el orquestador en un worktree
fijado en `28324af`: 284 passed, EXIT=0, en 17 min (incluye T6).**

## T7: micro-ciclo W-2 (2026-10-02)

- **(a) Resultado contra el contrato.**
  - Los agentes derivados ya no emiten entradas por ruta en `grep`/`glob` (`0477be6`). `read` y `edit` conservan sus mapas. Una derivación anterior se regenera, y un derivado editado a mano se sigue rechazando (`test_004_002_t7_w2.py`, RED `f2bfc1e` → GREEN).
  - La guía es honesta sobre los mecanismos (`44df268`). Suite completa: 307 passed.
- **(b) Alcance.** Los commits del rol tocan solo `skills/`. Ninguno usa `--no-verify`.
- **(c) Desvíos y su disposición.**
  - **W-3.** La sonda en vivo del orquestador mostró que en OpenCode 2.0.16 `write`/`edit` escriben fuera del mapa: crearon archivos en `scripts/` y `docs/` y modificaron `docs/cdad-policy.json`, que se restauró. Decisión del dueño: no perseguir una barrera mecánica de escritura. Restringir de más es contraproducente, y tests y código no siempre se pueden separar por ruta (Go, ciclos sin código). La garantía de escritura es instrucción más auditoría del orquestador (`git diff --name-only` contra `write_scope`). La investigación técnica se paró.
  - **Prompts de rol.** La auditoría del review-fix mostró que la regla general de límites (detenerse y reportar, y por qué saltarse un límite invalida el resultado) no llega explícita a los prompts compuestos de implementer y reviewer. Pasa a T7 como mejora del producto.
  - **Registro del modelo.** El registro del orquestador OpenCode atribuyó el GREEN a glm-5.3-flash; la base de datos de OpenCode muestra deepseek-v4.1-flash. Quedó corregido en el ledger.
  - **Lectura del archivo sensible.** El review-008 citó la longitud de un patrón de `tests/.sensitive-patterns.local`, lo que sugiere que leyó ese archivo prohibido; no reveló su contenido. Queda pendiente verificar si la barrera de `read` lo cubre.

## T7: L-1, regla general de límites en los prompts generados (2026-10-02)

- **(a) Resultado contra el contrato.** Un bloque único, compartido y generado desde `sources/` por `scripts/cdad-generate.py` llega a los 22 agentes (`717e6a7`). Dice tres cosas:
  - saltarse un límite no adelanta la tarea: se audita y se invalida;
  - los límites mecánicos varían según el proyecto y el runtime, y la regla aplica igual;
  - si un límite bloquea trabajo legítimo, el rol se detiene y reporta con evidencia, y el orquestador decide.

  RED `ad79703` → GREEN; suite 310 passed; review-010 APPROVE.
- **(b) Alcance.** El GREEN tocó solo `agents/`, `sources/` y el generador; el RED, solo `tests/`. Ningún commit usa `--no-verify`.
- **(c) Desvíos y su disposición.**
  - En el RED, el test-writer leyó `agents/**` con `bash` tras una denegación de `read`, en lugar de reportar. La causa fue un paquete del orquestador que contradecía la política. La lección queda para los paquetes: no pedir a un rol que lea fuera de su política sin autorizarlo de forma explícita.
  - F-1 (FYI) se acepta sin cambios.

## T7: P-1, rutas privadas en la política (2026-10-02)

- **(a) Resultado contra el contrato.** Decisión del dueño en `owner-decision-p1-2026-10-02.md`. El campo opcional `path_policy.private_paths` produce:
  - en OpenCode, deny en `read` y `edit` para todos los roles; una entrada simple cubre también su subárbol y la barra final se normaliza;
  - en Claude Code, bloqueo de las herramientas mediadas, incluido un Glob cuyo patrón apunte a la ruta privada;
  - un orquestador derivado con YAML válido;
  - sin el campo, ningún cambio.

  Commits `aa41b31` → `52db017` → `54f1454` → `17863f3` → `83b7f17` → `e3c88cc` → `9c92350`; suite 329 passed; review-013 APPROVE.
- **(b) Alcance.** Producto: `cdad_packet.py`, el guard y la guía. Tests: `test_004_002_t7_private_paths.py` y la enmienda de `without_maps` en T5, firmada por el orquestador. Ningún commit usa `--no-verify`.
- **(c) Desvíos y su disposición.**
  - El review-011 no dio dictamen. Lección: a los reviewers se les pide revisar leyendo el código y los tests, sin cadenas de `opencode run` anidadas.
  - Limitaciones declaradas, por decisión del dueño: un Grep sobre una carpeta padre, las entradas glob de mejor esfuerzo y bash sin acotar.
  - R5 aceptado: unos 252 ms por llamada.

### Disposición del review-014 (conjunto de T7)

- **F-SET-1.** El ítem pendiente "verificar si la barrera de `read` cubre `tests/.sensitive-patterns.local`" queda cerrado:
  - **Resultado de la verificación:** antes de P-1 no lo cubría, porque la política lo clasificaba como `test`. Así lo determinó el inventario `discovery-001`.
  - **Disposición:** con P-1 y la revisión `9ffb7d16`, OpenCode lo deniega a todos los roles, y el guard de Claude Code lo bloquea a los roles mediados (`t7-live-walk.md` §6).
  - **Posible lectura del review-008:** se dispone como lección para los paquetes. Ese reviewer no reveló el contenido; solo citó una longitud. No se rota ni se cambia nada del archivo; queda a criterio del dueño.
- **F-SET-2.** Cerrado con las sondas en vivo de `t7-live-walk.md` §6.
- **F-SET-3.** La guía §1 afirmaba que `edit` se aplicaba en OpenCode, lo que contradice W-3. Se corrige en un review-fix de una línea.
- **F-SET-4.** Nit sobre el paquete: la spec usa PD-1..PD-13. Sin acción.

### Suite de cierre de T7

Worktree fijado en `5b14f0e`, con `make staging` previo: **329 passed** (470 s). Una primera corrida sin staging dio 10 fallos de instalación por el staging ausente, que git ignora; no es un defecto.
