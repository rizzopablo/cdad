# Re-review — 005-006 guided-project-start (etapa 4, tras el GREEN del review-fix del dueño)

**Packet:** `005-006-guided-project-start-reviewer-review-002` · **Rol:** reviewer (solo lectura) · **Fecha:** 2026-10-10
**Contrato aprobado:** `docs/specs/005-006-guided-project-start/spec.md` — sha256 `f6b28af8…c1b18` verificado contra el pin del packet ✓ (el spec NO fue editado durante el review-fix).
**Árbol revisado:** submódulo `cdad` @ `97d03cc` (GREEN) ← `5963914` (review-fix) ← `db0f4b6`/`e616c3d` (RED); `docs/.cdad-state.json` dirty (binding de ESTE paquete reviewer-review-002 en `prepared`; verificado con `git diff`).

## Dictamen

A1, A2 y C **verifican cerrados** con evidencia empírica nueva. No los reabro. La revisión reabre por **tres defectos NUEVOS con evidencia dura** (F1, F2, F3) y registra cuatro opcionales/deuda (F4–F8). Sin F1–F3 resueltos, el review-fix no declara cierre; con sus cierres verificables aplicados, se puede cerrar sin un nuevo ciclo formal de revisión.

## Verificación de los hallazgos acordados

**A1 — `CDAD_INSTALL_ROOT` fuera del cableado: ✓ CERRADO.**
Residuos del token solo en (a) `install.sh:45,385,548-555` — raíz de INSTALACIÓN, archivo NO tocado por el diff (acto requerido cumplido); (b) `scripts/validate-subagents.sh:58-67` — validador de instalación, fuera del set de 7; (c) bytes históricos de `.cdad/packets/` e `inbox/` (registros, no distribuidos ni ejecutables). Verificado en vivo que la variable no existe en runtime: `bash -c 'echo "${CDAD_INSTALL_ROOT:-UNDEFINED}"'` → `UNDEFINED`. Byte-parity de los agentes generados **ejecutando el generador**: 6/6 comparaciones byte-idénticas contra `agents/cdad-orchestrator.md` y `agents/claude-code/cdad-orchestrator.md` (perfiles economical/optimus/premium × opencode/claude-code); el perfil `basic` difiere solo en la columna de modelos (vacía por diseño del perfil) — no es drift.

**A2 — marcador `<skill-dir>` resoluble: ✓ CERRADO.** Toda invocación del shell de cableado usa el marcador con su definición textual al lado. La resolvibilidad es **real en OpenCode**: el tool de skills renderiza la salida con la línea literal `Base directory for this skill: <directory>` (código fuente del runtime, `packages/core/src/tool/skill.ts`, `toModelOutput`; consultado hoy). No es convención sin anclaje.

**B1 — receta concreta: secuencia ✓ / argumentos ✗ (F3).** La secuencia (abrir ejecución nueva → prepare → validate-state/request/packet → begin → record-dispatch) existe con flags que coinciden con los `--help` reales del CLI (verificados en vivo). Dos defectos: F3 (argumento erróneo de `validate-packet`) y F4 (completitud).

**B2 — comprobación única: doc ✓ / script ✗ (F2).** §10 existe con los tres actores y delimitación de alcance honesta («no corre la suite, no valida política, no relee la skill cargada»). El script nuevo vive bien en `skills/cdad-cycle/scripts/` (raíz `skills` de la política; stdlib; declarado read-only y cumple). Pero su veredicto no es honesto en árboles sin marcador propio — ver F2.

**C — convenciones propias primero: ✓ CERRADO.** `project-start.md` §3: «**preserve the project's own conventions and naming** … CDAD's own naming convention is `<epic-num>-<feat-num>-<slug>`; use it only when the project does not already have a convention of its own». El defecto original («convención del proyecto» en :42-43) está proscrito y el test C lo codifica (GREEN verificado).

## Verificación independiente

1. **RED honesto:** worktree en `db0f4b6` (tests del RED + cableado viejo): **8 failed**, todos `AssertionError` con enumeración de posiciones concretas (A1 lista las 22 file:línea ofensoras; B1/B2/C citan la propiedad ausente). Cero ImportError/SyntaxError.
2. **GREEN/regresión:** `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/ -q -p no:cacheprovider` → **685 passed** (864.75 s), rc=0, en 97d03cc + state dirty (equivalencia por re-ejecución: mismo árbol, misma política `f508ab1e…`).
3. **make validate:** rc=2, **2 FAIL F011**: `scripts/validate-subagents.sh` (pre-existente: falla idéntico en el baseline `3f6f1b2`; drift de copias instaladas + `install.sh --check`) y `tests/validate-odoo-specialization.sh` — sección A3: pre-existente en sus otros hits, **pero el set de archivos pateados se AMPLIÓ con el test nuevo de este review-fix** (→ F1). El resto: 141 PASS / 2 FAIL.
4. **Sin debilitamiento:** `git diff db0f4b6^..HEAD` toca solo los 12 archivos declarados; `cdad_packet.py`, `cdad_continuity.py`, `cdad_result.py`, `install.sh`, `scripts/`, `build/` **sin cambios** — el enforcement de `epic_features` (cdad_packet.py:549-554, :1459-1509) y el comportamiento de `prepare` intactos (spec §2).
5. **Tests = comportamiento, no verdes vacíos:** T6 lee los archivos al ejecutarse y evalúa propiedades (tokens, secuencia con argumentos, trilogía de versión, prohibición); los dos tests de familia ajustados conservan la detección de rutas relativas y **endurecen** el marcador (antes aceptaban 9 cadenas de marca débil incluida la palabra “instalación”; ahora solo `<skill-dir>`). Garantía PD-10/INV-5 conservada y extendida.

## Hallazgos — veredicto-tupla por finding (bucket por observables: familia de modelo distinta +1, diff completo +1, racional citado file:lines +1, spec+convenciones en contexto +1 → `b=h`)

### F1 — Ŷ=BLOCKING, b=h — nombre privado «<proyecto-de-aceptacion>» en el test publicado; dispara A3 del propio repo
- **Rationale:** `tests/test_005_006_t6_owner_reviewfix.py` (creado en el RED de este review-fix) menciona 4 veces el nombre real del proyecto de aceptación del dueño, «<proyecto-de-aceptacion>» (`:54, :363, :414, :463`, docstring y mensajes de aserción). Es el ÚNICO archivo trackeado con ese nombre. El criterio A3 del validador del repo (sanitización de contenido publicable, una de las 2 condiciones FAIL de F011) lo patea: la lista de hits de A3 en HEAD incluye el test nuevo (+ pycs derivados). Contraevidencia controlada: con `CDAD_SENSITIVE_PATTERNS='zzznomatch'` (que, por diseño del validador, bypasea el archivo local de patrones, que este rol no lee) **A3 pasa**; sin el bypass, A3 patea el archivo → el match proviene del archivo privado de patrones, y la única referencia privada nueva y exclusiva del archivo es «<proyecto-de-aceptacion>». Consecuencia: identidad de cliente publicable en artefacto distribuido con el producto; violación material del criterio A3 con contenido nuevo de este feature.
- **Provenance:** `tests/test_005_006_t6_owner_reviewfix.py:54,363,414,463`; salida de make validate (log `/tmp/opencode/make-validate.log`); `tests/validate-odoo-specialization.sh:243-272` (mecánica A3).
- **Cierre verificable:** reemplazar las 4 menciones por placeholder neutro (el test solo aserciona sobre `E001`/`F001-001`; rename seguro) → `grep -rln <proyecto-de-aceptacion>` deja de listar el test; A3 vuelve a la lista de hits pre-RED ({docs/specs/004-003/supervision-record.md, review-t5.md, test_role_packets.py}).

### F2 — Ŷ=BLOCKING, b=h — `cdad-version-check.py` etiqueta como «CLI» un marcador ajeno (caminata sin frontera de instalación)
- **Rationale:** la búsqueda del marcador CLI camina ancestros hasta 8 niveles y acepta el primer `version.txt`, sin frontera. En el repo@97d03cc imprime `CLI: 7f66619…` — valor de `<home>/version.txt` (instalación global v9) — mientras el árbol que aloja y ejecuta el script es el repo; veredicto impreso: `COHERENT`. En fixture aislado con instalación propia `zzzv1`, el «CLI» vuelve a imprimir `7f66619…` (ajeno). Solo es correcto cuando el script corre desde el árbol instalado (mismo root). §10 manda la comprobación «antes de confiar una sesión» sin excluir checkouts de desarrollo; la propiedad B2 del dueño exigía honestidad del veredicto (qué verifica y qué no).
- **Provenance:** `cdad-version-check.py:44-58` (caminata), `:100-104` (label CLI); el modelo de instalación del producto usa frontera explícita (`cdad_packet.py:2504-2509`, `_installation_root` = `parents[2]` del layout `.config/opencode/agents`) — no reusado aquí; dos corridas reales con salidas reproducidas (arriba).
- **Cierre verificable (opciones equivalentes, decide el dueño):** (a) la búsqueda CLI se detiene en frontera de instalación (aceptar solo un marcador cuyo root contenga el layout del árbol que aloja el script; checkout → devuelve UNKNOWN), o (b) documentar el caveat (docstring + §10) y forzar UNKNOWN cuando el marcador hallado no pertenece al propio árbol. Cierre por corrida: (i) desde el repo NO puede imprimir `COHERENT` con el valor de `<home>/version.txt` como «CLI»; (ii) en fixture con instalación `zzzv1`, «CLI» imprime `zzzv1`.

### F3 — Ŷ=BLOCKING, b=h — receta B1: `validate-packet --packet PACKET_ID` pasa un ID; el flag consume un PATH físico
- **Rationale:** `cdad_packet.py:3699` lee `--packet` como archivo (`_read_bytes(Path(args.packet))`, relativo al cwd); el uso canónico pasa la ruta (`tests/test_004_003_t1_draft_contract.py:175`: `--packet str(packet_dir/"PACKET.md")`); el paquete publicado vive en `.cdad/packets/<id>/PACKET.md`. Tal como está en `project-start.md:98-99`, el paso 2 de la receta falla al ejecutarse con el ID tal cual.
- **Cierre verificable:** corregir el argumento a la ruta física (p. ej. `--packet "$PWD/.cdad/packets/<PACKET_ID>/PACKET.md"` o capturado del stdout de `prepare`) y ejecutar los 4 pasos de validate en un fixture real con paquete publicado (corrida registrada). Cambio mínimo; no toca código de producto.

### F4 — Ŷ=OPTIONAL, b=h — receta B1 no ejecutable en la forma anotada para proyecto «truly empty» (R1); placeholders sin definir
- **Rationale:** comprobado en fixtures: `prepare` sin `--new-execution` sobre estado template → `ERROR: no active feature in state: cannot bootstrap an execution`; con `--new-execution` sigue fallando hasta política + plan del epic + `epic_history` con aprobación (PD-1) + delegación activa. El paso 0 que attempt-2 realmente hizo («sincronizó `epic_features`, escribió el objetivo», evidence :18) no aparece en la receta ni se referencia quién lo ejecuta (PD-12 → `cdad-epic`; la aprobación del plan del epic no es delegable). Además `EXEC.json`/`REQUEST.json`/`UPDATE.json`/`docs/attempt.json` quedan sin atar: el esquema de `attempt.json` vive en `project-execution.md:113-116` (lectura obligada, contra el objetivo declarado de B1).
- **Cierre (opcional):** delimitar el dominio de la receta (válido con epic activa + feature registrada) y para R1 encadenar el paso 0 explícito (sincronización PD-12 + aprobación PD-1) con el binding de paths; o capturar los nombres de archivo del stdout de `prepare`. Los pasos 2–4 sí son una mejora mayor real sobre el estado previo (attempt-2 reconstruía todo a mano).

### F5 — Ŷ=OPTIONAL, b=h — marca del CLI no unificada fuera del set guardado (deuda pre-existente; la nota del commit sobreafirma)
- **Rationale:** coexisten `<skill-dir>` (set guardado), `<skill>` (`project-execution.md:42,87,…`) y rutas relativas invocables sin marca: `handoff-prompts.md:6,551`, `opencode-delegation.md:44`, `progress-guards.md:3`, `re-entry.md:19`. El commit dice «toda invocación del CLI se expresa como `<skill-dir>/…`» — cierto para el set de wiring, no para todo el bundle. No es regresión (esos archivos nunca usaron `$CDAD_INSTALL_ROOT`), pero es la misma clase de defecto que el dueño marcó como A: copiar el template de `handoff-prompts.md:551` en un proyecto consumidor falla.
- **Cierre (opcional):** unificar marca en esos 5 puntos y extender el barrido del A2-test, o acotar la claim. No bloquea.

### F6 — Ŷ=Nit, b=h — §10 dice «imprime un veredicto COHERENT/DRIFT»; el script imprime 4 veredictos y no tiene tests propios
- **Rationale:** el script tiene 4 salidas (`COHERENT` rc0, `DRIFT` rc1, `NO-PROJECT-AGENTS` **rc0**, `UNKNOWN` rc3); `project-start.md:153-154` nombra 2, y rc=0 de `NO-PROJECT-AGENTS` lo lee un consumidor como «ok». Hoy el script no tiene ningún test propio (ningún test lo ejecuta): unit de los 4 veredictos + rc en fixtures, incluido el caso DRIFT/UNKNOWN.

### F7 — Ŷ=Nit, b=h — el barrido A3 incluye `tests/__pycache__`
- **Rationale:** los hits de A3 incluyeron `.pyc` compilados (ruido binario); conviene `--exclude='__pycache__'` en el grep del validador.

### F8 — Ŷ=FYI, b=h — el spec aprobado fija el marcador que el fix retiró, sin amendment
- **Rationale:** spec :189 (PD-10) y §6:329 fijan `$CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/…` como el marcador del cableado «verificable»; el fix lo cambió a `<skill-dir>` con decisión del dueño (autorizada en el objetivo del GREEN, declarada en el packet) y NO enmendó el spec ni dejó nota de cierre. El sha del contrato no cambió (correcto: decisión de cierre, no re-escritura del contrato); falta el registro de trazabilidad (nota en closure.md o ADR) para que un revisor futuro no lea la divergencia sin contexto.

## Reabertura por hallazgo acordado

| Hallazgo | ¿Reabre? | Base |
|---|---|---|
| A1 | NO | 22/22 posiciones limpias; install.sh intacto; variable INDEFINIDA en runtime demostrada; byte-parity verificado |
| A2 | NO | `Base directory for this skill:` literal en el output del runtime |
| B1 | PARCIAL | La secuencia existe (RED satisfecho); F3 rompe «argumentos correctos», F4 «completos» |
| B2 | PARCIAL | Doc ✓; F2 rompe la honestidad del veredicto con 2 contraejemplos reproducidos |
| C | NO | Texto correcto; test C verde; defecto original proscrito |

## Abstenciones

Ninguna relevante para el veredicto. Registradas: (1) no declaro público/privado el repo de destino — F1 no lo necesita (el criterio A3 del repo juzga por su propia regla, no por destino); (2) la aceptación real R2 del proyecto del dueño sigue ABIERTA por diseño (spec VERIFY 5/PD-16) — fuera del alcance de esta re-review; el state dirty la refleja.

## Evidence pack (comandos y salidas clave)

```
git -C cdad log --oneline -3   # 97d03cc GREEN ← 5963914 fix ← e616c3d/db0f4b6 RED

# RED (worktree db0f4b6): 8 failed / AssertionError con posiciones; worktree eliminada al cierre
# Suite 97d03cc: pytest -q → 685 passed (14:24 min), rc=0
# make validate → rc=2 (2 FAIL F011); subagents pre-existente @3f6f1b2; A3 → F1
# CDAD_SENSITIVE_PATTERNS='zzznomatch' validate-odoo-specialization.sh → A3 PASS (patrón local bypaseado)
# generación de agentes: 6/6 profiles byte-idénticos a los commiteados (basic difiere solo columnas de modelo)
# version-check repo@97d03cc → COHERENT con CLI=7f66619 (= <home>/version.txt)  [falso "!: F2"]
# version-check fixture (instalación zzzv1) → CLI=7f66619 [valor ajeno], DRIFT
# bash : "${CDAD_INSTALL_ROOT:-UNDEFINED}" → UNDEFINED (variable no existe en runtime)
# receta B1 en fixtures: 3 errores explícitos successivos (state/policy → plan → approval pending);
#   prepare sin --new-execution → "no active feature in state"
# validate-packet: cdad_packet.py:3699 consume PATH físico (uso canónico con ruta en test_004_003_t1:175)

# Escrituras de este rol: NINGUNA en el repo. Solo este informe en
# /tmp/opencode/005-006-rereview.md (workspace temporal declarado); borrado de
# tests/__pycache__ (artefactos regenerables); worktrees temporales creados y eliminados.
```

**Agregado:** 3 BLOCKING (F1, F2, F3) · 2 OPTIONAL (F4, F5) · 2 Nit (F6, F7) · 1 FYI (F8) · 0 abstenciones de bloqueo. κ-dedupe: F2/F3/F4 comparten bloque de commit (5963914) y clase receta/CLI → cuentan como 1 bloque correlacionado para el LLR; F1 es de clase distinta (contenido publicable). Base de re-review: solo se reabrió con evidencia nueva y verificable, medida contra las reglas de calibración de stage-4-review.
