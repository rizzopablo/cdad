I have the full surface verified. Delivering the discovery report as final text (read-only; no repo writes).

---

# Discovery — 005-003-orientation-reduction

**Subetapa:** discovery (stage 1). **Rol:** architect, read-only. **Contrato:** fila 8 del `docs/epics/epic-005-real-operation/plan.md` (sha256 `fbb0770b…`) + sección «Ajuste de los ciclos pendientes» + `discovery-inputs.md` + delta `discovery-inputs-2026-10-12.md`.
**No se redacta spec ni plan.** Este informe cierra decisiones del borrador o deja el VERIFY abierto.
**Línea base reutilizada, no repetida:** `docs/specs/005-003-orientation-reduction/evidence/baseline-meter-2026-10-12.md`.

Método: lectura de las fuentes declaradas; verificación de la superficie real de CLI/estado/paquetes por lectura de código y por ejecución **de solo lectura**; dos reproducciones vivas de evidencia mecánica (§1.3). Ningún test, ninguna suite, ningún despliegue, ninguna escritura.

---

## 1. Superficies y entidades verificadas

### 1.1 El estado y su bloat de historial (hallazgo central para (a))

| Entidad | Valor verificado | Procedencia |
|---|---|---|
| `docs/.cdad-state.json` | 2.975 líneas; **320.880 B** serializado | `python3` sobre el archivo |
| `stage_history` | **304.075 B = 94,8 % del state**; **315 entradas** | ídem |
| Claves de primer nivel | `version, stack, active_epic, epic_stage, active_feature, current_stage, audit_status, review_status, postconditions_status, epic_features, epic_history, stage_history, approver, hitl_delegation, last_updated, delegation_history, execution, active_packet, tdd_substage` | ídem |
| Valores relevantes | `active_epic=epic-005-real-operation`; `active_feature=005-003-orientation-reduction`; `current_stage=discovery`; `active_packet={id:…architect-discovery-001, role:architect, substage:discovery, **status:prepared**, contract_kind:approved-epic-plan, contract_sha256:fbb0770b…}`; `execution={id:exec-005-003-…-001, authority_ref:docs/epics/…/execution.md, policy_sha256:f508ab1e…}`; `hitl_delegation.status=active` | ídem |
| Memory Bank | `projectbrief.md` 2.067 B; `activeContext.md` **156.378 B**; `progress.md` 52.531 B; `systemPatterns.md` 37.996 B (≈249 KB) | `wc -c` |

**Consecuencia directa:** el caso S-BOOT-04 leyó «4 fragmentos consecutivos, líneas 1–2068» del state = 215.292 caracteres (51,4 % de su salida total) para descubrir un puñado de campos operativos. Una **proyección** compacta — no una reescritura del estado — es la palanca correcta: el historial (`stage_history`, 94,8 %) se consulta selectivamente.

### 1.2 Superficie de CLI y de artefactos (extensiones disponibles, sin inventar)

| Superficie | Qué expone (verificado) | Procedencia |
|---|---|---|
| `cdad_packet.py` | subcomandos `validate-state`, `validate-policy`, `render`, `validate-request`, `validate-packet`, `prepare`, `validate-metric` | `build_parser` `scripts/cdad_packet.py:3452-3510` |
| `prepare` — sub‑modos mutuamente excluyentes | ordinario; `--resume-packet`; `--replace-packet`+`--reason`; `--reconcile-policy`+`--decision-ref`; `--record-dispatch`+`--attempt-id`; `--propose-policy`; `--new-execution` | `:3470-3510`, `:3529-3578` |
| Manejo de error de argv | `_Parser.error` → `self.exit(2, "ERROR: prog: msg")` | `:3447-3449` |
| Registro de despacho | `.cdad/executions/<id>/dispatches/<attempt-id>.json`; observación con `runtime, model_configured, model_reported, session, started_at` + `provenance` (exactamente, sin resultados ni gate) | `:2213`, `:2215`, `:2339-2395`; `project-execution.md` §5 |
| Ejecución v2 | `.cdad/executions/<id>/execution.json`: `{execution{}, path_policy{}, policy{path,schema_version,sha256,snapshot}, policy_history[], schema_version:2}` | lectura del archivo |
| Paquete | `.cdad/packets/<id>/REQUEST.json` con claves `schema_version, packet_id, execution_id, feature_id, role, substage, objective, contract, inputs, read_scope, write_scope, invariants, expected_output, evidence_required`; `PACKET.md` con bloque `---cdad-packet-json … ---end-cdad-packet-json` | `REQUEST.json`, `PACKET.md` |
| `cdad_result.py` | `receive`, `validate-receipt`, `materialize`, `run-python-unittest`, `validate-run-evidence`; inbox fijo `.cdad/inbox`; recibo con `semantic_status` siempre `pending` (nunca aprueba) | `:1457-1493`, `:63`; `re-entry.md:25-64` |
| `cdad_continuity.py` | `begin`, `checkpoint`, `reconcile`, `resume`, `trigger`; `resume` proyecta **goal / authority(actual) / decisions / uncertainties / next_action** + referencias, `--max-bytes` por defecto 16 KiB y **falla cerrado sin truncar** | `:1297-1299`, `:1216-1226`, `:1229-1291`; `continuity.md:59-60` |
| checkpoint actual | `head.json` de 6.488 B con `references` `contract`/`living` (incluye el state proyectado a `hitl_delegation, approver, execution`) | lectura de `head.json` |
| `cdad-version-check.py` | veredictos `COHERENT`(0)/`DRIFT`(1)/`UNKNOWN`(3)/`NO-PROJECT-AGENTS`(4); lee el marcador **solo en la raíz de su propio árbol** (un checkout da `UNKNOWN`) | `scripts/cdad-version-check.py:21-32,87-107,154-169` |
| `cdad_context_meter.py` | presente **en el repo** (55.973 B); **ausente** de las skills instaladas de OpenCode y de Claude Code | `ls` de ambas instalaciones |
| Referencias de procedimiento | `project-start.md` (reconocimiento→primer encargo, §1-§10), `project-execution.md` (§1-§8), `continuity.md`, `context-meter.md`, `state-detection.md` (**owner canónico del reconocimiento feature/Memory-Bank**), `re-entry.md` | lectura |
| OpenChamber | CLI instalada y **servidor respondiendo HTTP 200**; subcomandos `serve/stop/status/schedule/session/models/projects/control/tunnel/startup/logs/connect-url/update`; `session` = `list/create/send/fork/status/messages` con `--dir/--project/--agent/--model` | `command -v` + `curl` + `--help` |

### 1.3 Reproducciones vivas de evidencia mecánica (requeridas)

**(e2) `--project-root` relativo rechazado.** Comando y salida exactos:
```
$ python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root .
ERROR: --project-root must be an absolute existing directory: .
rc=2
$ python3 skills/cdad-cycle/scripts/cdad_packet.py prepare --project-root . --role architect --substage discovery --objective x
ERROR: --project-root must be an absolute existing directory: .
rc=2
```
Aplica a `validate-state` **y** a `prepare`. (No lo verifiqué exhaustivamente en `cdad_continuity.py`/`cdad_result.py`: **VERIFY** abierto, §2-(e).)

**(e1) `rc` enmascarado por tubería.** Comando y salida exactos:
```
$ python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root . | head -40
ERROR: --project-root must be an absolute existing directory: .
$ echo $?
0
# capturando PIPESTATUS inmediatamente:
PIPESTATUS=(2 0)   # el CLI devolvió 2; head devolvió 0
```
Y con la misma firma sobre un error legítimo distinto (raíz absoluta, contexto inexistente):
```
$ python3 … validate-state --project-root "$ABS" --execution-context <inexistente> | head -40
ERROR: execution context not found: …/does-not-exist/execution.json
PIPESTATUS=(2 0)      # sin tubería: rc=2
```
Confirmado: la tubería devuelve `0` aunque el CLI devolvió `2`, y el error real se imprime.** Hallazgo (e1) reproducido tal como lo describe el encargo.

Nota de precisión: `$?` **es** el de la tubería (el último comando, `head`); `PIPESTATUS[0]` conserva el del CLI. El texto del encargo dice «`$?` es el de la tubería» — correcto.

**(d) version-check vivo:**
```
$ python3 skills/cdad-cycle/scripts/cdad-version-check.py --project-root "$ABS"   # artefacto del checkout
  project: c9f4810…   agents: c9f4810…   CLI: (no version.txt found)
verdict: UNKNOWN (rc=3)
$ python3 <instalación>/.config/opencode/…/cdad-version-check.py --project-root "$ABS"
  project: c9f4810…   agents: c9f4810…   CLI: c9f4810…
verdict: COHERENT (rc=0)          # ídem instalación de Claude Code
```
El **medidor no está** en ninguna de las dos instalaciones (listado de sus `scripts/` sin `cdad_context_meter.py`). Confirma el hecho 1 del encargo.

### 1.4 Lo que NO pude verificar (explícito)

1. **Contrato agente↔OpenChamber para notas/planes/previews/diffs.** Verifiqué instalación, servidor vivo y CLI con `session`/`projects`/`control`. **No** verifiqué que las capacidades visibles de la UI (notas por proyecto, diff avanzado, previews) sean alcanzables por el **agente** por una API estable, ni su autenticación. → §2-(g), VERIFY.
2. **El medidor sobre el producto instalado**: no está instalado; no lo ejecuté (la línea base prohíbe repetir la medición). Su comportamiento en el producto solo se puede afirmar por el artefacto del repo.
3. **R4 sigue abierto en el reference.** `context-meter.md` «Output size» declara el límite **por documento de sesión** (16.384 B) y **no** contiene la regla del documento multiplexado (total ≤ N × límite). La condición de cierre de R4 («declarar la regla … ANTES de que 005-003 consuma corridas multi-sesión») **no está cumplida** (`context-meter.md:237-247`).
4. **La base «18 lecturas previas al `resume`» de la fila 8** proviene de la sonda 2 de 003-007 y **no está entre los casos medidos** en `baseline-meter-2026-10-12.md`. No la reproduje (no repetir desarrollos). → desalineación §3.
5. **Rechazo de raíz relativa en `cdad_continuity.py`/`cdad_result.py`**: no exhaustivo.
6. **Contenido crudo de `.cdad/local/runs/005-003-baseline/`** (mapeo id↔hash): no leído (privacidad).
7. **D6/R6 (versión de runtime heterogénea)**: no ejercitado (las corridas medidas fueron homogéneas).
8. **D11 (chequeo de no-escritura sobre base viva)**: no reproducido; se toma el estado declarado en `debt.md`.

---

## 2. Resolución técnica de cada punto (a)–(i)

### (a) Vista compacta del estado operativo — **DECISIÓN: proyección por código; separar el historial NO es requisito**

**Decisión.** Una **proyección generada por código** desde las fuentes existentes alcanza; **no** hace falta separar el historial del state en este ciclo. Fuentes (todas ya existentes y verificadas): `docs/.cdad-state.json` (solo los campos operativos), `.cdad/executions/<id>/execution.json`, `.cdad/packets/<id>/REQUEST.json` + `active_packet`, `docs/cdad-policy.json`, `cdad-version-check.py` (versión) y el `head.json` de continuidad.

**Fundamento.**
- El coste real lo paga el **agente** que lee el state a contexto, no el CLI (que lo parsea en milisegundos). Una proyección de salida resuelve eso **sin migrar el formato**.
- Separar el historial obligaría a: cambiar el documento de estado (`stage_history`), mantener compatibilidad de todos los consumidores actuales (`prepare`, `validate-state`, `_approved_spec_entries`, `_approved_epic_plan_entry`, la continuidad con `fields` proyectados), y arriesgar hashes/referencias (el `head.json` ya pincha `docs/.cdad-state.json` con `sha256` sobre los campos `hitl_delegation/approver/execution` — separar el historial movería bytes fuera del alcance de ese pin). La restricción del insumo es explícita: «no convertir esta optimización en una reescritura obligatoria del sistema de estado».
- Superficie mínima a emitir (todas verificables hoy): proyecto reconocido; `active_epic`/`epic_stage`; `active_feature`/`current_stage`/`tdd_substage`; ejecución vigente (`execution.id`, `authority_ref`, `model_policy`, `policy_sha256`); `active_packet{id,role,substage,status}`; autoridad/aprobación relevante (`hitl_delegation.status`, `approver`, y la entrada de aprobación que habilita al rol); versión (`COHERENT|DRIFT|UNKNOWN|NO-PROJECT-AGENTS`); ruta operativa siguiente (el `next_action` que ya vive en el checkpoint de continuidad, o una derivación explícita).

**Dónde vive.** Reusar la familia de CLI existente (un subcomando **read-only** nuevo en `cdad_packet.py`, p. ej. una vista de estado) o el `resume` de continuidad para la parte de `next_action`; **una sola fuente de verdad**, sin segunda memoria ni dashboard. Preferible el CLI de paquetes que ya conoce el estado y las aprobaciones. **No** es requisito del borrador un nombre de subcomando concreto; la spec lo fija.

**Presupuesto de tamaño (criterio, no límite universal).** La proyección debe caber en unos pocos KB (el `head.json` de continuidad ya logra 6.488 B con referencias); el state medido es 320.880 B → la reducción es de dos órdenes de magnitud y **medible** por inspección del artefacto.

**VERIFY abierto:** ninguno bloqueante. Decisión cerrada.

### (b) Selección explícita de entrada — **DECISIÓN: mapa de estados explícito, atendiendo paquete preparado; VERIFY sobre la forma exacta de detección de "trabajo pendiente"**

**Decisión.** La selección es un **mapa explícito** sobre la proyección de (a), **no** una inferencia por `current_stage` ni por la palabra «inicializar»:

| Condición observada | Entrada |
|---|---|
| `active_packet.status ∈ {prepared, dispatched}` **o** ejecución vigente con trabajo pendiente | **Continuidad y reconciliación** (`resume`/`reconcile`; si el contrato cambió, `--replace-packet`; si está despachado, reconciliar antes de repetir) |
| Ejecución activa, sin paquete pendiente | Continuidad (`resume` de continuidad) y siguiente unidad de esa ejecución |
| Reposo sin trabajo pendiente | Apertura de la **unidad siguiente** por el procedimiento existente (`project-start.md` §6-§7) |
| Configuración incompleta (sin `docs/cdad-policy.json`, autoridad sin pin) | Diagnóstico accionable de `project-start.md` §8 (marcadores `approval pending`/`state incoherent` **por referencia**) |

**Caso real que prueba el riesgo:** hoy `current_stage=discovery` **y** `active_packet.status=prepared` para `…architect-discovery-001`. Una inferencia ingenua («está en discovery, no hay nada activo») perdería un paquete ya preparado. La condición de la tabla lo evita por construcción.

**Fundamento.** `resume` **no** es la entrada desde reposo (`project-start.md:134-138: «Without an active execution, do not run resume»`); y sin checkpoint devuelve una proyección vacía `no-checkpoint` con `rc=0` (`continuity.md:20`, `cdad_continuity.py:1240-1261`), es decir, **no** cura la selección. Por eso la selección debe ser explícita y previa.

**VERIFY abierto (acotado):** la definición operativa de «trabajo pendiente» debe apoyarse en campos ya existentes (`active_packet.status`, `current_stage`, `postconditions_status`, `execution`), pero **no** existe hoy un campo que enumere "paquetes pendientes". El borrador debe decidir si basta `active_packet` + `current_stage` o si se deriva de los sub‑directorios `.cdad/packets/<id>/` con `status` no-`completed`. → dejarlo explícito en la spec; **no** requiere campo nuevo.

### (c) Interfaz operativa suficiente — **DECISIÓN: referencia corta + ejemplos EJECUTADOS; reutilizar esquemas; sin generador de documentación**

**Decisión.** Exponer para `prepare` (y sus sub‑modos), validación (`validate-state`/`validate-request`/`validate-packet`), `begin` (continuidad) y **registro de despacho** (`--record-dispatch` + `docs/attempt.json`): cuándo usarlos, argumentos **requeridos**, defaults relevantes, efectos y un **ejemplo mínimo válido** de sus archivos de entrada. Reusar: `docs/attempt.json` (§1.2), `UPDATE.json` (continuidad), `state-template.json`/`packet-request.schema.json`/`execution-context.schema.json`. **Sin** segundo manual extenso y **sin** generador de documentación completo.

Los defaults/efectos ya están en las referencias existentes (`project-execution.md` §1-§8, `continuity.md`) → la tarea es **consolidar y ejecutar**, no reescribir. Hallazgo operativo a incorporar (de §1.3): el **`--project-root` debe ser absoluto** y el **`rc` no se lee por tubería**.

**Las tres prácticas del delta quedan como HIPÓTESIS A MEDIR** (no soluciones decididas), y el borrador debe declarar cómo se miden:
- (i) *Validación concreta en cada encargo*: el paquete nombra los comandos de validación aplicables; la suite completa la corre **una vez** quien cierra. Medición: por observación del paquete + ejecuciones reales (no por grep de frases).
- (ii) *Verificación en dos niveles*: siempre procedencia+diff+alcance+focales (segundos); suite/integración solo con motivo concreto; reutilizar evidencia equivalente **con procedencia verificada**. La regla de equivalencia **ya existe y es canónica** (`re-entry.md:67-79`) → reusar, no duplicar.
- (iii) *Agrupar sin mezclar roles*: un RED para varios defectos de una misma clase + un GREEN, cada uno en su sesión, con el contrato aplicable y referencias. Aquí hay **frontera con 005-007** (tamaño de unidad/preparación) → 005-003 aporta el **contrato aplicable y las referencias del paquete**, 005-007 el tamaño.

**VERIFY abierto:** confirmar que (i)-(iii) no pisan el alcance de 005-007 (declarado como frontera, §2-(h)).

### (d) Comprobación de versión única y correctamente situada — **DECISIÓN: reusar el instalado; tratar la ausencia del medidor explícitamente**

**Decisión.** Reusar `cdad-version-check.py` **instalado** (no el del checkout, que da `UNKNOWN`). Distinguir: **ausencia** (`NO-PROJECT-AGENTS`=4, `UNKNOWN`=3) de **incoherencia** (`DRIFT`=1); republicar por el camino legítimo (`prepare` + `--replace-packet`/derivados) y **verificar después**; **no** duplicar inspecciones de manifiestos/marcadores sin una contradicción nueva; recordar su límite declarado: **la coincidencia de archivos no demuestra lo cargado por una sesión abierta** (`project-start.md:187-191`).

**Caso hoy (hecho 1):** el medidor **no está instalado** en ninguna skill; la versión instalada da `COHERENT` en `c9f4810`, anterior a `eac25ac`. Por lo tanto: (i) tratar «medidor ausente» como **ausencia distinta de incoherencia**, no como `DRIFT`; (ii) medir con el **artefacto del repo** sin desplegar (desplegar es del dueño y fuera de este ciclo); (iii) si el gate exige el medidor instalado, eso es un **bloqueo declarado**, no un atajo.

**VERIFY abierto:** ninguno bloqueante.

### (e) Evidencia mecánica fiable — **DECISIÓN: patrón de captura que no enmascare el `rc`; salida acotada con evidencia completa**

**Decisión.** Regla operativa (documentable y verificable): capturar el retorno real del CLI **sin tubería que lo enmascare** — usar `PIPESTATUS` (o `set -o pipefail`, o ejecutar sin tubería y acotar por separado). Salida acotada al contexto, con la evidencia completa disponible por referencia. Errores accionables con el formato esperado (`ERROR: …`) y recuperación legítima. **No** ampliar alcances, fabricar aprobaciones ni borrar registros.

Hallazgos vivos incorporados: (e1) `PIPESTATUS=(2 0)` — el CLI devolvió `2`; (e2) la raíz relativa devuelve `ERROR: --project-root must be an absolute existing directory: .` (rc=2) en `prepare` **y** `validate-state`. Ambos quedan como **hallazgos** con su comando y salida (§1.3).

**VERIFY abierto:** comprobar si `cdad_continuity.py` y `cdad_result.py` también exigen raíz absoluta (§1.4-5) — un comando por CLI lo cierra.

### (f) Criterio de preparación suficiente — **DECISIÓN**

**Decisión.** Investigar más **solo** cuando hay un bloqueo o una incertidumbre que **afecta al siguiente despacho**. Una investigación técnica del producto pertenece al **architect**; el orquestador **no** la repite preventivamente. **No** prohibir la inspección de código cuando sí es necesaria (p. ej. verificar un contrato o un hito del medidor). La proyección de (a) + la interfaz de (c) reducen la necesidad de reconstruir por código; no la eliminan por decreto.

**Fundamento:** S-BOOT-04 inspeccionó 21 llamadas ≈70.138 caracteres de código del CLI **sin** un bloqueo que lo exigiera («El primer `prepare` finalmente funcionó sin un bloqueo que exigiera esa investigación previa», `discovery-inputs.md:68-73`). Eso es orientación evitable, no preparación legítima.

### (g) Capacidades efectivas del entorno — **DECISIÓN: inventario corto + OpenChamber verificado como consumidor con fallback portable; VERIFY sobre API agente**

**Decisión.** Entregar un **inventario compacto ligado a versión/configuración** de cómo el orquestador encuentra capacidades existentes para **presentar planes, archivos, previews y diffs**, con **fallback portable por archivos o enlaces**. **OpenChamber NO es dependencia** de la metodología ni dashboard nuevo de esta feature.

**Verificado hoy:** OpenChamber **está instalado** (CLI en PATH) y su **servidor responde HTTP 200**; su CLI expone `session` (`list/create/send/fork/status/messages`), `projects`, `control`, `schedule`, `connect-url`, `logs`. Esto satisface el «verificar la instalación y el mecanismo de acceso ANTES de prometer automatización»: **el mecanismo existe (CLI y HTTP)**. Lo que **no** está verificado es el contrato estable agente↔superficie para notas/previews/diffs (§1.4-1) → una integración compleja de UI queda como **propuesta posterior**, no comprometida.

**No se implementa** OpenChamber ni OnlyOffice; no se crea fuente de estado. El fallback portable (archivos + enlaces + explicación breve) es el requisito mínimo y ya es posible.

**VERIFY abierto:** si el borrador quisiera prometer algo más que el fallback, debe primero cerrar el contrato agente↔OpenChamber (hoy no verificado). Recomendación: **no** comprometerlo en esta feature.

### (h) Frontera con 005-006 y 005-007 — **DECISIÓN: reusar el procedimiento existente; sin otro bootstrap**

**Decisión.** El arranque/arranque-desde-reposo-tras-enmienda usa **el procedimiento existente** `project-start.md` (que compone por referencia `state-detection.md`, `bootstrap.md`, `project-execution.md`, `continuity.md`) — **no** se crea otro bootstrap. `state-detection.md` es el **owner canónico** del reconocimiento feature/Memory-Bank (Steps 1-2); 005-003 **no** lo redefine. Tamaño de unidades y preparación de encargos → **005-007**; 005-003 es dueño de **orientación y acceso compacto a información operativa**.

**Fundamento:** `project-start.md:3-16,81-90`; `state-detection.md:5-10`. La frontera ya está declarada en el plan («005-006 resuelve el arranque; 005-003, la orientación al retomar; comparten el mismo procedimiento de reconocimiento», `plan.md:36`).

### (i) Aceptación — **DECIDIDA (a concretar en la spec; no redactada acá)**

Decisión de criterios, cada uno con su evidencia y su límite:
1. **Reposo → primer despacho legítimo** sin leer toda la historia ni reconstruir el CLI desde su código (recorrido normal). Evidencia: la proyección (a) sustituye la lectura del state; la interfaz (c) evita la arqueología del CLI.
2. **Reanudación con trabajo activo** preserva autoridad, aprobaciones y efectos; una ausencia/incoherencia devuelve **el bloqueo y cómo resolverlo**. Un resumen corto **no** oculta un paquete pendiente ni declara válido un contrato cambiado (por eso (b) mira `active_packet.status` y (d) reusa el pin por hash/path).
3. **Los ejemplos operativos se EJECUTAN** contra la versión correspondiente — **no** se verifica utilidad buscando frases en Markdown (por eso (c) exige ejemplos ejecutados).
4. **El uso real siguiente reduce orientación y contexto CON EVIDENCIA del medidor**: tiempo hasta despacho, herramientas, volumen de salidas y proxy de entrada cuando esté disponible; **lo ausente queda `unknown`** con causa (contrato del medidor).
5. **La meta numérica se fija DESPUÉS de la medición** (§4), atendiendo a trabajo legítimo distinto; **sin límite universal** de minutos ni de llamadas; **sin** afirmar operar bajo 100k/200k sin evidencia de las sesiones pertinentes.
6. **La reducción no traslada trabajo al primer worker**: observar si el encargo quedó completo, si hubo bloqueos/retrabajo y si las responsabilidades siguen claras.
7. Un primer despacho más rápido es **señal**, no aceptación; la aceptación usa una **próxima sesión real** y registra ayudas extraordinarias, bloqueos y resultado.

**Sobre el hecho 2 (reorientación de rol), 3 (tiempo entre despachos), 4 (redundancia), 5/6 (R4, D11/D6):**
- **(hecho 2)** Cada sesión de rol emite `previous_*` y `time_to_first_*` como `unknown` con causa (no hay `resume` ni hito de «primera acción del encargo»). **Decisión: proxy declarado AHORA + extensión acotada PROPUESTA (no asumida).** El proxy: por rol, usar las medidas existentes de **tramo completo** (`session_reads`, `total_output`, `tool_calls`) declarando **explícitamente** que **no** son un corte «pre-acción». La extensión acotada (hito nuevo, p. ej. «primera acción del encargo = primera llamada de herramienta que no sea `read`, o primera escritura dentro del scope») se propone como **tarea candidata** con su costo (tocar el contrato de 005-002 = spec+asset+tests+reference) y su riesgo (depende de clasificar herramientas por versión de runtime; D6). **No** se asume hecha.
- **(hecho 3)** El tiempo del orquestador entre despachos **no** es medida del medidor. **Decisión: la aceptación admite la derivación con su criterio declarado**, y el criterio es parte de la entrega: huecos entre sesiones hijas sobre el store en solo lectura, con los límites declarados (huecos **negativos** si dos roles se solapan; el tiempo del orquestador **dentro** de la ventana de un rol es **invisible**; `time_updated` de una hija no marca el fin del trabajo del orquestador). Se reproduce el ~38-40 min (§4).
- **(hecho 4)** La redundancia (suite fuera del cierre, gate re-ejecutado) **solo** es observable por **declaración**. **Decisión: se declara en el ledger/evidencia del paquete** (donde ya se registran observaciones y gates), y la **fidelidad** se verifica por **evidencia reutilizable con procedencia** (la regla de equivalencia ya canónica en `re-entry.md:67-79`) + el cierre corriendo la suite **una vez**. **No** se expande el medidor para leer comandos (privacidad PD-10/PD-12).
- **(hecho 5 → R4)** La superficie mínima de **resumen del conjunto** (sesiones incluidas, cobertura, hitos, magnitudes relevantes, referencias al detalle) **vive en la salida del medidor** (una sección de resumen del run multi-sesión), **no** en un dashboard ni en otra memoria. **Dependencia dura:** R4 (declarar la regla del documento multiplexado en `context-meter.md`) debe cerrarse **antes** de que 005-003 consuma corridas multi-sesión (hoy **abierto**, §1.4-3).
- **(hecho 6)** D11 es **prerrequisito para usar la integración real como gate** (no bloquea discovery); D6/R6 exige comparar contextos por versión de runtime antes de consumir `run.runtime_version`. Ambos se declaran como condiciones del gate de aceptación, no del discovery.

---

## 3. Desalineación de la fila 8 del plan del epic y enmienda PROPUESTA (no aprobada)

La fila 8 (`plan.md:41`) dice: *«cambios en el cableado o las guías del orquestador que reducen las lecturas previas al `resume` (base: 18 en la sonda 2). Se acepta solo con una sonda nueva medida con la herramienta de 005-002; la meta numérica se fija en la spec a partir de los datos.»*

**Puntos de desalineación (con los hechos del discovery):**

1. **Ancla de la medición.** La fila ancla en «lecturas previas al `resume`» (base 18, sonda 2 de 003-007). Pero (i) el delta aprobado el 2026-10-12 amplía el alcance al **proceso completo de delegación** (preparación/reorientación/redundancia); (ii) `previous_*` **no es medible para sesiones de rol** (hecho 2) y `resume` **no es la entrada desde reposo** (`project-start.md:134-138`); (iii) la base 18 **no está entre los casos medidos** de la línea base (no reproducible sin repetir desarrollos). El ancla real debe ser **el primer despacho legítimo**, no el `resume`.
2. **Medio de aceptación.** La fila acepta «solo con una sonda nueva medida con la herramienta de 005-002», pero **el medidor no está instalado** (hecho 1) y **D11/R4 son prerrequisitos** para usarlo como gate (hecho 6). La fila no declara esa dependencia; tal como está, la aceptación no es satisfacible legítimamente hoy sin desplegar (reservado al dueño).
3. **Alcance material.** La fila se limita a «cableado o guías»; el delta y la dirección estratégica agregan **estado compacto generado por código, selección explícita de entrada, interfaz operativa suficiente y capacidades efectivas ligadas a versión/configuración**.
4. **Fronteras.** La fila no menciona la frontera con 005-006 (mismo procedimiento de reconocimiento) ni con 005-007 (tamaño de unidad), que el insumo fija explícitamente.

**Enmienda propuesta a la fila 8 (para aprobación del dueño, NO aprobada por mí):**

> **005-003-orientation-reduction** — Orientación al retomar y arranque desde reposo tras enmienda con **contexto acotado**: una **vista compacta del estado operativo generada por código** desde las fuentes existentes (proyecto, epic/feature, ejecución vigente, paquete y estado, autoridad/aprobación, versión y ruta operativa siguiente), una **selección explícita de entrada** (continuidad/reconciliación · siguiente unidad · diagnóstico) que **atiende un paquete preparado o pendiente** y no depende de la palabra «inicializar», una **interfaz operativa suficiente** para `prepare`/validación/`begin`/registro de despacho con **ejemplos ejecutados**, y la **disposición de versión/medidor** (incluido el caso «medidor no instalado» como *ausencia*, distinta de incoherencia). El arranque reutiliza el procedimiento de 005-006 (sin otro bootstrap); el tamaño de unidad/preparación de encargos es de 005-007. Aceptación: una sesión nueva en reposo llega al primer despacho legítimo sin leer toda la historia ni reconstruir el CLI desde su código; una reanudación preserva autoridad/aprobaciones/efectos y una ausencia/incoherencia devuelve el bloqueo y cómo resolverlo; los ejemplos **se ejecutan**; y el uso real siguiente reduce orientación/contexto **con evidencia del medidor** (artefacto del repo, despliegue reservado al dueño; D11 y R4 como condiciones del gate y D6/R6 como condición de comparación por versión). La **meta numérica se fija después de la medición**, desde la línea base medida, sin límite universal de minutos ni de llamadas.

Además, en el **criterio de aceptación del epic nº 3** («Informe de medición … producido por la herramienta de 005-002»), anotar que hoy el medidor se invoca **desde el repo** (no instalado) y que D11/R4 condicionan su uso como gate.

---

## 4. Meta numérica PROPUESTA (derivada de la línea base medida)

**Regla transversal:** rango + criterio de comparación, jamás un número suelto ni un límite universal. Se distingue **medido** (línea base) de **derivado/predicho** (no medido; se declara como tal).

### 4.1 Línea base medida (reutilizada, no repetida)

**Caso C — S-BOOT-04 (reposo → primer despacho; el caso más comparable a 005-003):**
`time_to_first_dispatch` **8,29 min** (cut del medidor) / **≈8,78 min** (cut del insumo); primer despacho en **`call_index` 73** → **72 llamadas antes del despacho**; salida pre-despacho **418.841 car.**; composición 72 = 50 shell, 11 read, 10 edit, 1 skill; state leído = **4 fragmentos (líneas 1–2068) = 215.292 car. (51,4 %)**; consultas de código **21 llamadas ≈70.138 car.**; proxy de entrada pre-despacho **200.076 tokens**; skill inyectada 37.667 car. (**no observable** por el medidor).

**Caso A — reapertura de 005-002 (orquestación con ejecución preparada):** `first_resume` 1,92 min (llamada 29); `first_dispatch` **9,42 min** (llamada 76); `previous_calls=28` (shell 25, read 3); `previous_reads=3`.

**Caso B — ciclo original de 005-002:** `first_resume` 0,42; `first_dispatch` **6,17 min**.

**Rol (reorientación, proxy de tramo completo):** `session_reads` implementer 12/22/17/24; test-writer 12/12/10/6/4/4; reviewer 3/9.

**Derivación del orquestador entre despachos:** primer tramo 9,84 min + 11 huecos (Σ 28,62) = **38,46 min**; suma de roles 116,40 min; madre 174,65 min; cola 19,79 min; el implementer de 30,01 min es compatible con **dos corridas de suite** en un GREEN.

### 4.2 Meta propuesta (bandas + criterio), con trabajo legítimo declarado

Comparación **like-for-like** sobre la **próxima sesión real** de 005-003 (y, si está disponible, el primer arranque real de 005-006), medida con el **artefacto del repo** en solo lectura, mismos cuts.

| Medida | Base medida | Meta propuesta (banda) | Fundamento / límite |
|---|---|---|---|
| **Llamadas antes del primer despacho** (derivable de `first_dispatch.call_index`−1) | 72 (S-BOOT-04) | **≈45–55** | Quita las **21 consultas de código** (orientación evitable medida: ≈70 KB) y no agrega trabajo; el resto es preparación legítima (leer encargo, sincronizar, preparar). **Derivado, no medido.** |
| **Volumen de salida antes del primer despacho** | 418.841 car. | **≈120–180 KB** | Colapsa los 215 KB de state a una proyección de pocos KB y quita los ≈70 KB de código: 418,8−(215,3−~4)−70,1 ≈ **137 KB**. **Derivado, no medido.** |
| **`time_to_first_dispatch`** | 8,29–8,78 min (C); 6,17–9,42 (A/B, otro tipo de trabajo) | **≤ banda de C, sin aumento** | **Trabajo legítimo distinto**: C incluye una **enmienda real** (incorporar aprobación, sincronizar state, pausar una feature); A/B arrancan con ejecución ya preparada → **no se promedian** ni se exige el mínimo de A/B. |
| **Lecturas antes del primer `resume`** | plan base 18 (sonda 2, **no medida en esta base**); A: 3; B: 41 | **sin lectura del state completo; ≤ decena** | Criterio: la proyección reemplaza la lectura íntegra (320 KB). Se declara que **A/B difieren** (3 vs 41) → banda, no umbral. |
| **Reorientación de rol** (proxy declarado de tramo completo) | `session_reads` por rol (arriba) | **sin aumento sobre la banda por rol** | Proxy **declarado** (hecho 2): no es un corte pre-acción. La reducción esperada es que el rol ya no relea la spec entera (~50 KB) sino el contrato aplicable del paquete. |
| **Tiempo del orquestador entre despachos** | 38,46 min (derivación) | **reducción, con criterio declarado** | Derivación, no medida; límites declarados (huecos negativos, tiempo in-window invisible). |
| **Ejecuciones redundantes** | 2 corridas de suite en un GREEN (compatible con 30,01 min) | **0 corridas de suite fuera del cierre** | **Solo observable por declaración** (hecho 4); fidelidad por procedencia + equivalencia (`re-entry.md:67-79`) y suite **una vez** al cierre. |

**No** se impone límite universal de minutos ni de llamadas; **no** se afirma operar bajo 100k/200k (la línea base **no** mide la ventana real del modelo: el proxy `input+cache.read+cache.write` **no** es la ventana ni el consumo). Los datos ausentes quedan `unknown` con causa.

---

## 5. Tareas candidatas para el plan (dependencia · producto verificable · criterio de verificación)

> Sin redactar el plan. Numeración tentativa.

| # | Tarea | Dependencia | Producto verificable | Criterio de verificación |
|---|---|---|---|---|
| **T1** | **Vista compacta del estado operativo** generada por código desde las fuentes existentes (proyección, no migración) | — | Subcomando read-only (o equivalente) que emite `{proyecto, epic/feature, ejecución, paquete+status, autoridad/aprobación, versión, ruta siguiente}` | Test determinista sobre un proyecto fixture: la proyección contiene los campos y queda **acotada** (KB); **surfacea** `active_packet.status=prepared`; **no** toca el state. Uso real: el orquestador no lee el state entero |
| **T2** | **Selección explícita de entrada** (mapa continuidad·siguiente unidad·diagnóstico) | T1 | Regla documentada + función de selección | Test: `prepared`→continuidad; rest+pendiente→siguiente unidad; config incompleta→diagnóstico; **no** depende de la palabra «inicializar». Caso real: el paquete preparado de hoy se atiende |
| **T3** | **Interfaz operativa suficiente** (`prepare`/validación/`begin`/registro de despacho) con ejemplos **ejecutados** | T1 | Referencia corta + ejemplos mínimos válidos + corrida real de esos ejemplos | Test que **ejecuta** los ejemplos contra la versión correspondiente (no grep de frases); reusa `attempt.json`/`UPDATE.json`/schemas existentes |
| **T4** | **Evidencia mecánica fiable** (captura del `rc` sin enmascarar; salida acotada + evidencia completa) | — | Patrón documentado + (si aplica) helper; recuperación para raíz relativa | Test/reproducción: `PIPESTATUS` correcto; raíz relativa da diagnóstico accionable. Cierra el VERIFY de (e) para continuity/result |
| **T5** | **Disposición de versión/medidor único y situado** | — | Uso del `cdad-version-check.py` instalado; tratamiento explícito de **medidor ausente** (ausencia ≠ incoherencia) | Corrida real COHERENT; caso "sin medidor" declarado; **sin** duplicar inspecciones de manifiestos |
| **T6** | **Resumen del conjunto para corridas multi-sesión (R4)** — sin dashboard, sin segunda memoria | **R4 cerrada primero** (regla del documento multiplexado en `context-meter.md`) | Sección de resumen del run (sesiones incluidas, cobertura, hitos, magnitudes, referencias al detalle) + detalle a pedido | Test determinista sobre el resumen; verifica que R4 esté declarada **antes**; el detalle no se inyecta por defecto |
| **T7** | **(PROPUESTA, no asumida) Extensión acotada de 005-002**: hito «primera acción del encargo» para la reorientación de rol | Aprobación del dueño + T6/R4 | Hito nuevo en el record + asset/tests/reference actualizados | **Costo:** spec+asset+tests+reference de 005-002 (no se reescribe su contrato sin aprobación). **Riesgo:** clasificación de herramientas por versión de runtime (D6). Solo si se aprueba |
| **T8** | **Inventario de capacidades efectivas + fallback portable** (OpenChamber como consumidor verificado) | — | Matriz corta (observada/documentada/no disponible/desconocida) ligada a versión/configuración + demostración agente→artefacto→revisión por archivos/enlaces | Se apoya en lo verificado hoy (instalación + servidor + CLI). **No** promete API de UI (VERIFY §1.4-1); integración compleja = propuesta posterior |
| **T9** | **Declaración de ejecuciones redundantes** (dónde y cómo se verifica la fidelidad) | — | Patrón de declaración en ledger/evidencia del paquete | La fidelidad se verifica por procedencia + equivalencia (`re-entry.md`); el cierre corre la suite **una vez**; no se leen comandos (privacidad) |
| **T10** | **Medición y aceptación de uso real** (antes/después) | T1-T5 (y R4/D11 para el gate) | Informe de medición con el artefato del repo + próxima sesión real registrada (ayudas extraordinarias, bloqueos, resultado) | Aplica la meta de §4 con comparación like-for-like; lo ausente queda `unknown` |

**Orden/dependencias sugeridas:** T1 → (T2, T3) → T10 con T4/T5 transversales; T6 depende de cerrar R4; T7 solo con aprobación; T8 y T9 en paralelo. Frontera: T3 **no** define tamaño de unidad (005-007); T2/harness **no** crea bootstrap (005-006).

---

**Cierre honesto.** Todo lo afirmado en §1 tiene procedencia (archivo:línea o comando con su salida, §1.3). Lo no verificado está listado en §1.4. La enmienda de §3 es **propuesta**, no aprobada. La meta de §4 se **deriva** de la línea base medida y distingue medido de derivado. El medidor **no está instalado** (medido: `COHERENT` en la versión instalada sin `cdad_context_meter.py`; `UNKNOWN` en el checkout); R4 sigue **abierto** en el reference; D11/D6 quedan como condiciones del gate, no del discovery. No escribí en el repo, no aprobé nada, no desplegué, no repetí mediciones.
