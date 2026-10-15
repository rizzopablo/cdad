# Cierre — 005-006-guided-project-start

**Feature:** `005-006-guided-project-start` · **Epic:** `epic-005-real-operation`
**Ciclo técnico cerrado:** 2026-10-10 · **Aprobado por:** orquestador OpenCode (HITL delegada epic-005)
**Contrato:** `spec.md` sha256 `f6b28af8f1243021a8321a679c5ad74091e2cfd975b030072209216a2b3c1b18`
(aprobada 2026-10-10; decisiones D1–D8) · **Plan:** `plan.md` (T1–T5 + review-fix F1)
**Versión de ejecución del ciclo:** instalación global v9 `7f66619` (el repo se desarrolla; su CLI no
se usó para operar).
**Estado:** **`in-progress`** — ciclo técnico completo; **la aceptación real R2 queda como condición
del dueño** (§6).

## 1. Resultado

Una instrucción breve («usá CDAD para inicializar este proyecto y comenzar su análisis preliminar»)
basta para llegar a una **primera delegación útil**.

- **T1 — procedimiento corto de arranque + cableado (PD-1, PD-3..PD-9, PD-13, PD-15; INV-1..INV-4).**
  Nuevo `skills/cdad-cycle/references/project-start.md` (106 líneas): reconoce la raíz sin imponer
  layout (el directorio de sesión es pista, no norma; sin búsqueda global), clasifica
  nuevo/parcial/incompleta **por referencia**, preserva lo existente, registra cada restricción en su
  lugar canónico (tabla restricción→lugar), distingue inferible de decisión del usuario y **encadena
  hasta el primer encargo**. `SKILL.md` gana la fila en la tabla de referencias, la rama «sin
  ejecución activa → no `resume`» y las rutas del CLI instalado; `state-detection.md` declara su
  dueño canónico; `continuity.md` usa el CLI instalado. Commit `421ddf2` (+ enmienda de oráculo
  `91eaaaf`).
- **T2 — intake con arranque desde reposo (PD-2, PD-10, PD-14; INV-4/INV-5).**
  `sources/roles/orchestrator.md` incorpora la entrada *boot-at-rest* (cargar la metodología
  primero + señalar el procedimiento), el cableado con `$CDAD_INSTALL_ROOT/…` y la salida legítima
  ante bloqueo (qué falta + cómo seguir; sin fabricar autoridad ni cambiar de versión en silencio).
  Agentes regenerados con el generador (**byte-parity**). Commit `4d96905`.
- **T3 — responsable de `epic_features` (PD-12; INV-3).** `epic-planning.md` asigna el responsable
  (coordinador de epic) y reafirma al orquestador como escritor único del state; `project-start.md`
  trata el desfase (nombra faltantes/sobrantes y encamina a `cdad-epic`). **Sin cambios de código**:
  el enforcement de `cdad_packet.py` queda como lock verde. Commit `8dd8c09`.
- **T4 — README (PD-11; INV-6).** Sección corta de arranque guiado que remite al procedimiento, sin
  reproducir el prompt ni crear plantilla. Commit `fe8d742`.
- **T5 — aceptación (PD-16/PD-17).** Cuatro comprobaciones de comportamiento con fixtures
  deterministas en tempdir, agnósticas del proyecto y del entorno: R1 (proyecto nuevo → paquete
  **preparado y despachable**), R3(a) (política ausente → cierre con diagnóstico accionable, sin
  publicar), R3(b) (autoridad sin pin → `rc=2 approval pending` nombrando el registro contradicho y
  cómo seguir) y `resume` sin checkpoint (`rc=0`, proyección vacía `no-checkpoint`). **Verdes por
  diseño** (el producto lo entregaron T1–T4; precedente 003-002 T4): **locks de regresión anclados a
  precondiciones verificadas**, no verdes vacíos. Commit `2b69074`.
- **Review-fix F1 (review formal, hallazgo opcional).** `SKILL.md:278` marcaba el CLI como
  `scripts/cdad_result.py` (ruta relativa al consumidor); pasa a la ruta instalada. Los entramados de
  PD-10/INV-5 se extendieron a los Pasos 5-8 de `SKILL.md` (`934527f` + `19d561e`).

## 2. Gate de etapa 5

- **Suite completa verde** en el árbol final (corrida del orquestador, §5). La corrida del reviewer
  dio **680 passed / 0 failed** (12m23s) sobre el árbol de producto.
- **`make validate`: 141 PASS / 2 FAIL**, ambos **preexistentes y ajenos al diff**: **F011** (drift de
  la instalación en HOME — el producto instalado **no** contiene los textos nuevos, porque la
  activación es del dueño) y **A3** de odoo (solo donde existe `tests/.sensitive-patterns.local`,
  con **0** archivos del diff). Sin CI (gate local).
- **Auditoría de relevancia** (review formal): 31 tests, **0 superfluos, 0 postcondiciones sin
  test**; único hueco INV-7/INV-8, declarado por el plan y cumplido por el diff.
- **Una sola review formal** (`review.md`, `approved-with-conditions`, **0 bloqueantes**), que
  verificó por sí misma la suite, `make validate`, la ausencia de cambios en `scripts/`, el
  byte-parity de los agentes, la integridad del plan/execution del epic y el RED real (25 fallos al
  revertir el producto).
- **Memory Bank** materializado con el flujo (receive + materialize CAS): `activeContext.md`,
  `progress.md`. **`systemPatterns.md` sin cambios** (el patrón del arranque guiado queda cubierto
  por **ADR-021**). `projectbrief.md` sin cambios (sin cambio de propósito/stack/alcance).

## 3. Decisiones (D1–D8, aprobadas tal como se propusieron)

D1 referencia nueva **y** entrada de intake; D2 `resume` no aplica en reposo (solo la rama de
arranque); D3 CLI instalado por la procedencia de 005-005; D4 dueño canónico por objeto de
reconocimiento; D5 responsable de `epic_features` = coordinador de epic; D6 README con sección
corta; D7 aceptación por comportamiento (R2 real + R1/R3 por fixture), criterio funcional y no un
tope de lecturas; D8 sin plantilla del prompt largo. Razonamiento completo en la spec §7 y
**ADR-021**.

## 4. Desviaciones y hallazgos de proceso

1. **Enmienda de oráculo (T1 PD-9).** El implementer alcanzó 14/15 y **se detuvo** ante un rojo
   insatisfacible (`window_hits` lista de strings recorrida como `(lineno, _)`). El orquestador
   reprodujo el defecto y autorizó una **enmienda firmada** por el test-writer (`91eaaaf`: solo
   tuplas, misma ventana, ninguna aserción debilitada).
2. **Devoluciones sin cierre del implementer (T2 y F1).** Dos veces el rol devolvió control con la
   suite completa corriendo en background (que no sobrevive entre turnos). Se **reanudó la misma
   sesión** con la instrucción de commitear y correr solo la regresión proporcional. La suite
   completa de cierre la corre el orquestador.
3. **Hallazgo de plan (T3).** El plan no enumeraba `project-start.md` en los `Files` de T3, pero
   PD-12(b) lo exige. El orquestador lo autorizó como **consecuencia directa del PD** (desvío de
   alcance nulo: el archivo ya estaba en el write scope) y lo registró. Nota de orden para
   **005-007**: T1 y T3 corrieron en paralelo tocando el mismo archivo (sin conflicto aquí).
4. **Esquema cerrado de la observación de despacho (v9).** El CLI v9 exige **exactamente**
   `runtime/model_configured/model_reported/session/started_at/provenance`; los registros de 005-005
   traían además `execution_id/packet_id/role/substage` — forma que el v9 **rechaza fail-closed sin
   efectos**. `model_reported` queda en `null` (no hubo reporte independiente del modelo efectivo).
5. **Tests de consistencia estructural, no de frases.** Condición de aprobación registrada en
   `plan.md` (regla vigente `efficient-orchestration-requirements.md:107`; precedente 005-005 T2).

## 5. Evidencia

- **Commits de producto:** T1 `421ddf2`, T2 `4d96905`, T3 `8dd8c09`, T4 `fe8d742`, F1 `19d561e`.
  **Tests:** `0c7d951`, `91eaaaf`, `b2740a0`, `485503f`, `3c4b2be`, `2b69074`, `934527f`.
- **Artefactos:** `discovery.md`, `spec.md`, `plan.md`, `review.md`; `tests/test_005_006_t{1..5}_*.py`.
- **Receipts:** `architect-draft-001`, `reviewer-review-001`, `scribe-memory-001`
  (`.cdad/runtime/results/exec-005-006-guided-project-start-001/…`).
- **Checkpoints de continuidad:** `begin` (seq 1..18) + `checkpoint` en los cortes de unidad
  (`.cdad/executions/exec-005-006-guided-project-start-001/continuity/`).
- **Suite de cierre (corrida del orquestador sobre el árbol final, `env -u TMPDIR`):**
  **680 passed / 0 failed, exit 0** en 789.44 s (`python3 -m pytest tests -q -p no:cacheprovider`),
  en el commit de cierre técnico. Coincide con la corrida del reviewer (680/0 en 12m23s).
- **Suite tras el review-fix del dueño (ver §8):** **685 passed / 0 failed, exit 0** en 753.56 s
  (corrida del implementer en `1fba283`, reproducida por el reviewer en `97d03cc` con 685/0 en
  864.75 s). `make validate` sigue con **141 PASS / 2 FAIL** preexistentes.

## 6. Cierre y despliegue (2026-10-10)

**Instrucción del dueño (2026-10-10):** «Despliega 005-006 y cierra; no vamos a continuar con
005-002 aún». Es la autorización explícita de la acción reservada (activar una versión en HOME,
INV-7) y la decisión de cerrar la feature.

- **Despliegue:** versión = este commit de cierre, perfil `basic`, con un script local análogo al
  del despliegue de la v9 (`.cdad/local/deploy-005-006-home.sh`): respaldo del estado previo,
  `make staging PROFILE=basic` sobre un worktree fijado al commit, retiro de los agentes
  existentes para que el instalador los reemplace, `install.sh --basic --force` y
  `install.sh --check`.
- **Verificación del despliegue:** se registra en §9 (completada tras instalar).
- **Aceptación real (R2):** **no se ejecutó como corrida de sesión nueva** en el proyecto de
  aceptación. Es la única verificación que el ciclo no pudo hacer por sí mismo (requiere una
  sesión nueva del orquestador en ese proyecto, con el producto ya desplegado). Queda declarada
  como verificación del dueño: si esa corrida fallara, la feature **se reabre**. Lo que sí se
  verificó del producto es el comportamiento en fixtures deterministas (T5) y, tras desplegar,
  que la instalación contiene la versión completa (§9).

## 7. Deuda registrada

- **F2 (opcional):** INV-7/INV-8 sin test dedicado → un diff futuro podría pisar la fila 3 del plan
  del epic o sus criterios sin que la suite proteste (misma clase que el lock de T3 cerró para
  `cdad_packet.py`).
- **F3 (nota):** desviación de T3 y paralelismo T1/T3 sobre `project-start.md` (insumo para 005-007:
  tamaño de unidad / `files` por tarea).
- **F5 (opcional-considerar):** aserciones con ventanas absolutas y marcadores laxos, tolerantes por
  diseño; revisitar si otra feature desplaza las ventanas.
- **Preexistentes:** F011 (drift de la instalación en HOME) y A3 (patrones sensibles); sin CI.
- **Fuera de alcance (spec §5/§9):** medición de contexto (005-002), orientación al retomar y
  reducción de lecturas (005-003), roles en Claude Code (005-004), planificación progresiva
  (005-007), CI / ANON-1 / R2-STAGE / POLICY-CLASS.
- **Límite declarado:** el **doble bootstrap** (Memory Bank vs ejecución v2) sigue siendo dos
  procedimientos distintos; el arranque corto los **encadena**, no los fusiona.

## 8. Review-fix del dueño (2026-10-10) — posterior al cierre técnico

La revisión del dueño sobre el ciclo cerrado encontró **tres defectos materiales** que habrían hecho
fallar la aceptación real (R2), más un detalle de texto. Se corrigieron como review-fix
(RED → GREEN → re-review focal), antes de desplegar:

- **A — la ruta del CLI instalado estaba mal.** El cableado escribía
  `$CDAD_INSTALL_ROOT/skills/cdad-cycle/...`, pero `CDAD_INSTALL_ROOT` es una variable de
  **instalación** (no existe en runtime) y `~/skills/cdad-cycle` no existe. **Cerrado:** el cableado
  usa el marcador `<skill-dir>` — el directorio que el **runtime informa al cargar la skill**
  (verificado: OpenCode emite literalmente `Base directory for this skill: <dir>`). Cero
  ocurrencias de la variable en el cableado. RED `db0f4b6`, GREEN `5963914`.
- **B — el arranque no tenía receta concreta.** La evidencia `005-006-attempt-2.md` midió ~6 de 9,7
  minutos leyendo el código del CLI para deducir la secuencia. **Cerrado:** `project-start.md` da la
  secuencia concreta con argumentos y **una comprobación única de versión**
  (`<skill-dir>/scripts/cdad-version-check.py`, nuevo, read-only).
- **C — texto de convenciones.** `project-start.md:42-43` presentaba la convención de CDAD como «del
  proyecto». **Cerrado:** manda conservar las convenciones **propias** del proyecto y etiqueta
  `<epic-num>-<feat-num>-<slug>` como convención de CDAD, a usar solo si el proyecto no tiene una.
- **La re-review focal** (`review-owner-reviewfix.md`, `changes-required`) cerró A1/A2/C con
  evidencia propia y **reabrió B1/B2 parcialmente** con tres bloqueantes nuevos, todos cerrados:
  - **F1** — un nombre privado del proyecto de aceptación quedó publicado en el test del review-fix
    y lo pateaba el criterio A3 del propio repo. **Cerrado** (`1d99bdc`): placeholder neutro; el
    barrido A3 volvió exactamente a su lista pre-RED. **Causa raíz registrada: el nombre viajó en el
    objetivo del paquete RED que escribió el orquestador** — no en el rol.
  - **F2** — `cdad-version-check.py` etiquetaba como «CLI» un marcador **ajeno** (caminaba ancestros
    sin frontera de instalación: desde el repo imprimía el marcador de la instalación global y decía
    `COHERENT`). **Cerrado** (`1fba283`): frontera de instalación propia; desde un checkout de
    desarrollo el veredicto es `UNKNOWN` (rc≠0) y nunca presta el marcador global.
  - **F3** — la receta pasaba un **ID** a `validate-packet --packet`, que consume un **PATH** físico:
    el paso fallaba al ejecutarse. **Cerrado:** ruta física; los tres `validate-*` corrieron a rc=0 en
    un fixture con paquete publicado, con control negativo que reproduce el fallo viejo.
  - **F6/F4** (misma familia/archivo) plegados: `NO-PROJECT-AGENTS` deja de devolver rc=0 (solo
    `COHERENT` es 0; §10 enumera los cuatro veredictos y su rc) y la receta delimita su dominio
    (epic activo + feature registrada) y ata los paths de `.cdad/`.

**Nota de trazabilidad (F8).** La spec aprobada (PD-10 y §6) fija como marcador
`$CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/…`; ese marcador quedó **superado** por la decisión del
dueño (este review-fix). No se reescribió el contrato —su sha sigue siendo el pin vigente—: la
decisión de cierre se registra aquí y en ADR-021. Un revisor futuro debe leer PD-10 con esta nota.

**Deuda que queda (no bloquea):** **F5** (la marca del CLI no está unificada fuera del set guardado:
`handoff-prompts.md`, `opencode-delegation.md`, `progress-guards.md`, `re-entry.md` conservan
variantes; misma clase que A, sin uso en el arranque) y **F7** (`__pycache__` en el barrido A3).

**Estado tras el review-fix:** el ciclo está **listo para desplegar**; la aceptación real (R2) sigue
siendo la condición de cierre del dueño (§6).

## 9. Despliegue verificado (2026-10-10)

Ejecutado por el orquestador **por instrucción directa del dueño** («Despliega 005-006 y cierra»),
con un script local análogo al de la v9 (`.cdad/local/deploy-005-006-home.sh`, fuera de git):

- **Versión desplegada:** commit de cierre `35062b0`, perfil `basic`, en los tres roots de HOME
  (`~/.config/opencode`, `~/.agents`, `~/.claude`). Respaldo previo de agentes, manifiesto y
  marcador en `<workspace>/archive/20261010-opencode-agents-pre-005-006/`.
- **Marcadores:** `~/version.txt` y `source_version` del manifiesto = `35062b0` ✔
- **`install.sh --check`: PASS** (358 grupos de artefactos en sincronía con el staging del commit).
  Nota: el check **cuenta archivos**, así que un `__pycache__/*.pyc` generado al correr el CLI
  instalado produce un drift espurio (se retiró uno rancio; ver deuda).
- **El agente del orquestador instalado lleva el producto nuevo:** `cdad-orchestrator.md` tiene
  **8** ocurrencias de `<skill-dir>` y **0** de `CDAD_INSTALL_ROOT`; `references/project-start.md`
  y `scripts/cdad-version-check.py` están instalados en los tres roots ✔
- **`cdad-version-check.py` (desde el producto instalado):** `DRIFT` (rc=1) — **esperado y honesto**:
  `agents` y `CLI` son `35062b0`, pero **`project` = `7f66619`** porque el marcador del proyecto sale
  de los **agentes derivados de este repo** (`.opencode/agents/.cdad-derived.json → source_version`),
  que quedaron v9-derivados y **ensombrecen a los globales nuevos**. Se resuelve al **republicarlos
  desde la instalación nueva** (el primer `prepare` del próximo ciclo los republica) o activando el
  proyecto — y **activar una versión en el repo real es acción reservada al dueño**, que no fue
  pedida. Queda declarado, no forzado.

**Deuda nueva detectada en el despliegue:** `install.sh --check` es sensible a los subproductos de
ejecución (`__pycache__/*.pyc` que Python escribe junto al CLI instalado): tras cualquier uso real
del CLI instalado el check reporta drift espurio hasta retirarlos.
