# 005-004 — T5: recorrido real corto en Claude Code con recepción CDAD (acceptance-report-v1)

**Fecha:** 2026-10-13. **Coordinador:** sesión nueva de Claude Code (instrucción breve: «usá CDAD en el proyecto: seguí con la unidad activa»), con la skill `cdad-cycle` y los agentes `cdad-*` de la instalación global, `--project-root <repo>` explícito en cada CLI. **HEAD al correr:** `6afa238`. **Paso a** (gate de cierre) de PD-6; el paso b queda para después del despliegue.

> Este informe es **evidencia**, no aprobación. El recibo es `pending` (no aprueba el gate). La aprobación del gate de la feature y el cierre (etapa 5, Memory Bank, `epic_features`) **no** se ejecutan en esta sesión: corresponden a quien tiene la delegación HITL del epic-005, tras la revisión del orquestador Claude.

## 1. Recorrido (PD-6) — productor / evaluador / evidencia (PD-11)

| # | Paso | Productor | Evaluador | Evidencia |
|---|---|---|---|---|
| 1 | Orientación con la vista compacta | `cdad_packet.py status` instalado | coordinador | `entry: continuity-reconcile`; `packet.status: prepared` (ver §5, F-1); `version.verdict: COHERENT` |
| 2 | Versión, CLI instalado | `cdad-version-check.py` instalado | coordinador | `project/agents/CLI = 9d89a4b8…` → **COHERENT**, rc 0 (sin pata CC: la versión instalada no la trae) |
| 3 | Versión **con la pata CC** (PD-3) | `skills/cdad-cycle/scripts/cdad-version-check.py` **del repo en `6afa238`**, `--install-root <home>` | coordinador | `project/agents/CLI/claude-code = 9d89a4b8…` → **COHERENT**, rc 0. Sin `--install-root` el checkout de desarrollo da `CLI: (no version.txt found)` → **UNKNOWN rc 3** (comportamiento declarado F2; fricción F-3) |
| 4 | Paquete | `render` instalado | coordinador | sha256 de `render` = sha256 de `PACKET.md` publicado = `c3cc5cc0…b6b92d`. **Verificado en lo recibido:** el primer mensaje del sidechain del subagente tiene sha256 `e5cf29f0…5a33e0a`, y con el `\n` final agregado da `c3cc5cc0…b6b92d`: el rol recibió el paquete byte a byte **salvo el salto de línea final** (fricción F-7: `Agent` toma el prompt como parámetro tipeado por el coordinador; nada transporta los bytes del archivo) |
| 5 | Checkpoint write-ahead | `cdad_continuity.py begin` | — | seq 1, body `29243779…087140`, referencia de contrato `spec.md` `5e11f2ef…` |
| 6 | Registro del intento (I8) | `prepare --record-dispatch … --attempt-id cc-t5-attempt-1` | coordinador | `.cdad/executions/exec-005-004-claude-code-roles-001/dispatches/cc-t5-attempt-1.json`: `runtime: claude-code`, `model_configured: sonnet`, `model_reported: null` con causa en `provenance`, `session: <ses-cc-t5-coordinator>`, `started_at: 2026-10-13T16:19:49Z`; paquete `prepared → dispatched` |
| 7 | Despacho nativo | herramienta **`Agent`**, `subagent_type: cdad-reviewer`, `model: sonnet`, foreground | — | fila del transcript del coordinador: `{"name":"Agent","subagent_type":"cdad-reviewer","model":"sonnet","run_in_background":false}`; meta del subagente: `agentType: cdad-reviewer`, `requestNonInteractive: true`, `model: sonnet` |
| 8 | Señal durable del rol | transcript sidechain del subagente | coordinador | 3 filas `assistant` con `message.model: claude-sonnet-5-5` (`isSidechain: true`); identidad `cdad-reviewer`, **sin** fallback a un agente genérico |
| 9 | Recepción | `cdad_result.py receive` instalado | — | parte `review-report` (`artifact_kind: review`), 2223 bytes, sha256 `d5b5f1d0…3374e0` = texto final del subagente extraído byte a byte del transcript; `bundle_sha256 c7649677…6eea0b`; **`semantic_status: pending`**; `identity_validation/packet_validation: passed`; `scope_validation: unknown`; `receipt.json` sha256 `5145111b…b2a2f`; `validate-receipt` → `VALID` |
| 10 | Re-entry | `cdad_continuity.py reconcile` | coordinador | `classification: received`, `repeat_effect: false`, contrato `unchanged`, `unknowns: []` |
| 11 | Transición del state | coordinador (escritor único), edición a mano | coordinador | `active_packet.status: dispatched → completed` + entrada `tdd-t5-cc-run` en `stage_history` (re-entry.md §4) |

La evidencia cruda (I8, receipt, bundle, transcripts copiados, huellas, salidas de CLI) vive bajo `.cdad/` (ignorado por git); las rutas y digests de arriba la anclan.

## 2. Gate del paquete (verificación contra la fuente)

El rol respondió el encargo de solo lectura sin modificar archivos ni commitear. Verificado por el coordinador contra el árbol:

- **(1) sha256 de `spec.md`** — informó `5e11f2ef3199ca4f9072c04341abf15e6cac6b49cdf26a5dcab7abee51a33f5e`: **correcto** (igual al contrato del paquete).
- **(2) ids PD-n que define la spec** — informó **PD-1..PD-13**, con PD-10/12/13 «sin detalle verificado»: **incorrecto**. La spec define **PD-1..PD-11** (encabezados `**PD-n` en `spec.md:55-94`); PD-12 y PD-13 aparecen sólo como referencias a otras specs (005-007 PD-12 en `:139`, 005-005 PD-13 en `:106`), y PD-10 sí está definido (`:92`). Causa observable: el rol extrapoló desde un `grep` de menciones sin leer las definiciones.
- **(3) veredicto de la review** — «0 bloqueantes / 3 opcionales / 2 abstenciones»: **correcto** (coincide con `review_status.verdict`).

**Decisión del coordinador:** entrega **recibida**; el ítem (2) se **rechaza** como defecto del contenido del rol. No se reintenta: un reintento idéntico no aporta información nueva (re-entry.md, regla de reintentos) y el objetivo del recorrido —que las piezas encajen desde CC— no depende de ese ítem. El defecto se declara; no se presenta como verde.

## 3. Frontera de HOME (PD-7) y cruces del dueño (PD-11)

- **Huellas de la instalación — tres coberturas, declaradas por separado:**
  - *Comparación de bytes antes/después:* sha256 de 107 archivos (`<home>/.claude/skills/cdad-*`, `<home>/.claude/agents/cdad-*`, `<home>/.claude/cdad-scripts`): **idénticos** (digest del listado `9cfa2717…` en ambos). Excluye `__pycache__`.
  - *Lo que esa comparación NO cubrió:* el marcador de versión `<home>/version.txt` y el manifiesto de propiedad `<home>/.cdad-install-manifest.json` (los dos que PD-7(ii) nombra primero), ni `<home>/.agents` ni `<home>/.config/opencode`. Para ellos no hay snapshot previo; se verificó por **mtime**: marcador y manifiesto tienen mtime `2026-10-13 08:59:56 -0300`, **anterior** al inicio de la sesión (13:15).
  - *Barrido por mtime* (`find -newermt '2026-10-13 13:15'`) sobre `<home>/.claude/agents`, `<home>/.claude/skills`, `<home>/.claude/cdad-scripts`, `<home>/.agents`, `<home>/.config/opencode`: aparecen sólo el `.pyc` de abajo y dos archivos de `<home>/.claude/skills/synced/…` (sincronización de skills del harness de Claude Code, ajena a CDAD y no escrita por el coordinador).
- **Escrituras del harness:** Claude Code escribe los transcripts de la sesión bajo `<home>/.claude/projects/`; de ahí sale la evidencia de transcript (§1 #7-#8). No son escrituras del coordinador, pero PD-7 enumera `<home>/.claude*` y se declaran. Una invocación del CLI instalado al inicio de la sesión (antes de fijar `PYTHONDONTWRITEBYTECODE=1`) actualizó `cdad_packet.cpython-313.pyc` en el `__pycache__` de la skill instalada (mtime 13:16:25 -0300): es caché del intérprete, no producto, pero **es una escritura en HOME** y se declara (F-4).
- **Confianza de carpeta:** la entrada del proyecto en `<home>/.claude.json` está **ausente** antes y después; no se modificó.
- **Diff del repo:** sólo `docs/.cdad-state.json` y este informe.
- **BLOQUEO con responsable (dueño), no ejecutados:** (i) confiar la carpeta de este proyecto; (ii) copias viejas/despliegue en HOME; (iii) emitir activación de proyecto para CC; (iv) activar versiones en el repo real. **Paso b** de PD-6 (confirmación con el CLI instalado tras el despliegue: pata CC instalada y orchestrator CC declarando `Agent`): **BLOQUEO**, depende del despliegue del dueño.

## 4. Desconocidos conservados (PD-8) y procedencia de modelo (PD-5)

- (i) `exit 2` de un hook en modo no interactivo: **unknown** — el rol despachado (`cdad-reviewer`) no lleva hooks; este recorrido no lo ejercita.
- (ii) hooks del frontmatter aplicados a subagentes nativos: **unknown** — misma causa.
- (iii) modelo heredado por un subagente sin `model:`: **unknown** — el modelo se **declaró por llamada** (`model: sonnet`), así que la herencia no se observó.
- (iv) medición de contexto por rol del lado CC: **unknown** — no hay adaptador CC del medidor (D-4). Sólo se observa el contador del harness para el subagente (`subagent_tokens: 45512`, 2 tool uses, 12 s), que **no** es una medición CDAD.
- **PD-5:** modelo declarado de la revisión `sonnet` (`message.model` reportado `claude-sonnet-5-5`, familia Claude), distinto de la familia del implementer registrado (`deepseek-v4.1-flash`). `model_reported` quedó `null` en el I8 con causa (no observable antes del despacho); el valor observado está en las filas del transcript (§1 #8), **sin** un segundo registro I8.

## 5. Fricciones declaradas (el recorrido no es de intervención cero)

- **F-1 — estado de partida.** Al abrir la sesión, `docs/.cdad-state.json` tenía un cambio **sin commitear** que volvía el paquete `005-004-claude-code-roles-reviewer-review-001` de `completed` a `prepared` (HEAD lo tenía `completed`), con un `REQUEST.json`/`PACKET.md` ya preparados para este encargo. El coordinador lo tomó como preparación del lanzador y **no** lo revirtió; se registra.
- **F-2 — descriptor de recepción a mano (PD-10/D-10).** El buzón (`.cdad/inbox/t5/`), la copia byte a byte del texto final (extraído del JSONL del subagente) y el descriptor `staged-file` se escribieron a mano; el helper de 005-003 no existe en esta copia. Hubo además dos errores de uso recuperados (`receive --packet` espera la ruta a `PACKET.md`; `begin --update` exige `packet_id`, `attempt` y decisiones `{decision, rationale}`).
- **F-3 — pata CC desde el checkout.** Requiere `--install-root <home>`; sin él, UNKNOWN rc 3.
- **F-4 — `.pyc` en la skill instalada** (§3).
- **F-5 — kind de la parte.** PD-10 nombra `role-report` (caso architect); para el **reviewer** la tabla cerrada sólo admite `review` (`_allowed_kinds`). Se usó `review`. No se materializó la parte (no requerido por PD-6; sería creación en `docs/specs/<feature>/` con autorización explícita).
- **F-6 — transición del state a mano** (re-entry.md §4): no hay CLI que la registre (D-10 / unidad 005-012).
- **F-7 — prompt del despacho tipeado** (§1 #4): el rol recibió el paquete sin el salto de línea final.

## 6. Lo que queda para quien cierra

Revisión de esta evidencia por el orquestador Claude; decisión del gate de la feature por la autoridad HITL del epic; suite completa una vez y `make validate` en un worktree fijado al commit de cierre; etapa 5 (Memory Bank). Nada de eso se ejecutó aquí. Sin push, sin `--no-verify`, sin despliegue.

## 7. Revisión del orquestador Claude (2026-10-13)

**Cómo se armó la prueba:**
- **Proyecto:** un clon descartable del repo, en un directorio temporal del workspace, al commit `6afa238`.
- **Paquete:** lo preparó el orquestador Claude con el CLI instalado (reviewer, de solo lectura, con oráculo determinista) y lo dejó sin commitear. Esto explica F-1, que es la preparación del lanzador.
- **Coordinador:** `claude -p` lanzado desde un directorio confiable que no carga la memoria de este proyecto. Se cargan las instrucciones globales del dueño, que son su entorno. Herramientas autorizadas: `Bash Read Edit Write Glob Grep Agent Skill`, sin modos de permiso ampliados.
- **Limitación declarada:** el clon contiene esta spec, que describe el recorrido, y el coordinador la leyó (llamadas 4–6). La prueba de orientación no es ciega.

**Verificaciones propias:**
- **Huella de la instalación global:** coincide antes y después (`c990a716…`). Cubre el marcador de versión, los agentes y las skills CDAD de Claude Code, `cdad-scripts`, los marcadores `.cdad-*` de OpenCode y la confianza de carpeta. Excluye `__pycache__`, así que la escritura del `.pyc` (F-4) no entra en esta comparación y queda declarada.
- **Oráculo del rol:** el rechazo del ítem (2) es correcto, porque la spec define PD-1 a PD-11. Es un error de contenido del rol, detectado por el coordinador; no es un defecto del producto.

**Medición, con conteo propio sobre el transcript.** El medidor no tiene adaptador para Claude Code (D-4), y con otro instrumento y otro modelo estos números no se comparan con los de OpenCode:
- 47 llamadas en total; el primer `Agent` aparece en la llamada 23;
- 105 mil caracteres de salida antes del despacho;
- 8,7 minutos;
- costo informado por el harness: 3,88 USD;
- leyó el state completo en la llamada 2, antes de `status` (llamada 7). Es la misma entrada que corrige 005-011.

**Decisión del gate de T5** (orquestador Claude, con la HITL delegada por el dueño): **aprobado para el paso a.** Se cumplen PD-6, PD-7, PD-8 y PD-11, con las fricciones declaradas, que son deuda (D-10 → 005-012; F-3, F-5 y F-7, abajo). El paso b queda BLOQUEADO hasta el despliegue del dueño.

**Deuda nueva:**
- **F-7:** el paquete viaja tipeado en el prompt de `Agent` y pierde el salto de línea final. La integridad del paquete depende del coordinador.
- **F-5:** PD-10 nombra `role-report`, pero la parte del reviewer es `review`. Es un texto de spec impreciso y no cambia el resultado.
- **F-3:** desde el checkout, la pata CC necesita `--install-root`.

## 8. Paso b — después del despliegue (2026-10-13)

- **Despliegue:** lo autorizó el dueño, con el otro proyecto activo en reposo: `.cdad/local/deploy-005-003-home.sh 905c3e1`.
  - `<home>/version.txt` = `905c3e1…`.
  - El chequeo dio DRIFT solo por `__pycache__` de `cdad-cycle` (83 archivos contra 85).
  - `cdad-cycle` es idéntico al repo en las tres instalaciones.
  - El respaldo completo quedó fuera del repo.
- **Orquestador de Claude Code instalado:** declara `tools: Read, Grep, Glob, Bash, Edit, Write, Agent, Skill`.
- **Comprobador de versión instalado, con su pata Claude Code:**
  - agents, CLI y claude-code dan `905c3e1…`;
  - project da `9d89a4b…`, los agentes derivados del proyecto, que el próximo `prepare` republica (se vio en 005-004);
  - el veredicto es DRIFT, con esa causa.
- **Paso b cumplido.**
- **Alcance:** no se corrió un despacho con `--agent cdad-orchestrator`, así que el uso real de `Agent` desde ese agente sigue sin observarse.

## 9. Precisiones posteriores (revisión de Codex, 2026-10-13)

- **Qué prueba T5:** un recorrido de delegación a un reviewer, no un ciclo completo de desarrollo. Los hooks de test-writer e implementer no se ejercitaron.
- **Reintentos:**
  - no repetir un encargo idéntico es correcto;
  - darle al rol el diagnóstico concreto («PD-12 y PD-13 son referencias, no definiciones») sí es información nueva;
  - en una tarea donde esa respuesta fuera necesaria, corresponde corregirla y volver a verificar.

  Aquí no se hizo porque el objetivo del recorrido no dependía de ese ítem.
