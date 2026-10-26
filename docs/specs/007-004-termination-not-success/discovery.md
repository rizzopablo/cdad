<!-- materializado del recibo .cdad/runtime/results/exec-007-004-termination-not-success-001/007-004-termination-not-success-architect-discovery-001 (cdad-architect, gpt-6.1-sol) -->
## Discovery — 007-004 termination-not-success

**Recomendación:** conservar por ahora el significado compatible del rc («la interfaz produjo una respuesta»), pero completar el contrato explícito del sobre y corregir sus consumidores. **No basta cambiar rc:** no distingue resultado preparado de recibo durable ni acredita continuidad o aprobación.

No redacté ni aprobé una spec.

### 1. Contrato y estado verificados

Los SHA-256 del contrato, política y plan coinciden exactamente con los declarados en el paquete:

- Contrato: `9285fabe…a15b`.
- Política: `f508ab1e…2711`.
- Plan: `713194aa…2440`.

HEAD observado: `b038ec90945b95b9f657262785cbf7bd2a5a7ecd`.

### 2. Superficie real y consumidores

| Consumidor / productor | Lectura real y riesgo |
|---|---|
| `cdad_delegate.py` | Interpreta el sobre del adaptador; si existe, lo conserva aunque el proceso haya terminado con rc no cero. Sin sobre produce `transport-error`. Luego imprime el sobre y devuelve 0. Evidencia: `skills/cdad-cycle/scripts/cdad_delegate.py:253-286,403-413`. |
| `cdad_dispatch.py record` | Correlación contradictoria: `blocked`, sin entrega y sin registrar intento, pero rc 0. Con intento registrado y sin payload: `unknown`, `delivery_ref=null`, rc 0. Con payload: `completed` y descriptor staged, todavía sin recibo. Evidencia: `skills/cdad-cycle/scripts/cdad_dispatch.py:1086-1124`. |
| Adaptador OpenCode | Clasifica hechos durables y persiste mediante recepción antes de emitir `completed` con referencia. Sus bloqueos también pueden emitir sobre y rc 0. Evidencia: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:2945-2991`. |
| Orquestador canónico y agentes generados | El texto describe `delivery_ref` como **recibo durable**, correcto para la ruta externa pero insuficiente como regla general para `record`, que devuelve un descriptor. Evidencia: `sources/roles/orchestrator.md:51-54`; `sources/agents/adapters/opencode.md:98-100`; `sources/agents/adapters/claude-code.md:117-119`; `agents/cdad-orchestrator.md:272-274`. |
| Referencia CLI | Declara explícitamente rc 0 cuando se produjo el esquema; vocabulario cerrado de seis terminaciones. Ya advierte que `completed` no aprueba un gate. Evidencia: `skills/cdad-cycle/references/cli-delegation.md:100-132,424`. |
| Reentrada | Distingue correctamente texto final, descriptor staged y recibo durable; exige validación y transición separadas. Es el mecanismo que debe consumir la señal explícita. Evidencia: `skills/cdad-cycle/references/re-entry.md:23-85`. |
| Envoltorio local | Ejecuta el adaptador en background, guarda stdout/stderr y escribe `$?` en `.rc`; anuncia únicamente lanzamiento. No interpreta el sobre ni valida recibo. Evidencia: `.cdad/local/deleg.sh:15-17`. La existencia de `.rc` acredita término del proceso, no entrega. |
| Entrypoint de repositorio | `scripts/cdad_delegate.py:10` apunta al script canónico del skill. No hay `scripts/cdad_dispatch.py` en este checkout; no asumir esa ruta para el consumidor instalado. |

**Distinción importante:** encontré un envoltorio que **almacena** rc; no verifiqué un programa posterior que lea ese archivo y avance automáticamente. Eso queda como **VERIFY**, no como fallo demostrado de automatización.

### 3. Problema principal del protocolo

Actualmente `delivery_ref` tiene dos significados:

1. Ruta nativa: descriptor `RESULT.json` preparado por `stage_delivery`, aún no recibido (`cdad_dispatch.py:994-1027`).
2. Ruta externa: recibo durable ya persistido.

Por ello, ni `rc=0`, ni `termination=completed`, ni una referencia no nula bastan individualmente para determinar «recibido».

Además, el contrato no debe exigir que todo `attempt` del sobre tenga registro: el bloqueo por contradicción devuelve identificador, pero deliberadamente no registra una identidad rechazada.

### 4. Alternativas

| Alternativa | Ventaja | Insuficiencia / compatibilidad |
|---|---|---|
| Cambiar solo rc | Protege consumidores shell que únicamente comprueban éxito del proceso. | No representa staged frente a recibido; modifica el contrato publicado; scripts con `set -e` pueden abandonar sin consumir diagnóstico. |
| Sobre explícito + consumidores | Distingue las situaciones reales y conserva compatibilidad de rc. | Exige actualizar efectivamente envoltorios y procedimientos; documentarlo sin consumo verificable no cierra AC-7.8. |
| Ambos | Defensa adicional para consumidores shell. | Requiere migración y regla precisa por verbo; no elimina la necesidad del sobre ni de validación durable. |

**Criterio elegido:** resolver la familia completa de llegadas, no únicamente `blocked`. Recomiendo **sobre explícito y consumo obligatorio**, manteniendo rc compatible inicialmente. Si se decide cambiar rc, hacerlo como cambio adicional coordinado, nunca como sustituto.

### 5. Contrato recomendado para discutir

Propuesta, **no interfaz existente ni aprobada**:

- Mantener `termination` como causa de terminación.
- Hacer explícita la condición de entrega: ninguna, descriptor staged o recibo durable.
- Mantener una sola referencia al artefacto existente; no crear otro recibo, ledger ni registro de intentos.
- Definir combinaciones válidas y rechazo de contradicciones.
- Separar:
  - comando procesado;
  - bloqueo o terminación no concluyente;
  - resultado disponible;
  - recepción mecánica validada;
  - aprobación semántica, siempre fuera de estas señales.

El consumidor debe parar ante sobre ausente, ilegible o contradictorio. Con descriptor debe ejecutar la recepción existente; con recibo debe validarlo sin recibir otra vez. Ninguna rama puede aprobar un gate por rc o terminación.

### 6. Integración con 007-001 y 007-003

**007-001:** conservar exactamente la forma y vocabulario de `situation` y `next.operation`. El sobre es evidencia del comando, no una nueva autoridad sobre el estado. Un bloqueo no implica transición exitosa; después se consulta la vista existente. Un paquete despachado sigue orientando a `reconcile`; no introducir una situación nueva «success».

Evidencia: `docs/specs/007-001-unambiguous-entry/spec.md:25-36,68-100`.

**007-003:** conservar `provenance.continuity` y el mecanismo de cierre existente. Un descriptor staged no acredita cierre; un recibo durable tampoco prueba por sí solo que el checkpoint se completó. Si hubo interrupción después de publicar el recibo, recuperar mediante `validate-receipt --close-continuity --continuity-attempt N`, sin repetir recepción ni transición.

Evidencia: `docs/specs/007-003-continuity-at-edges/spec.md:119-135`. El entero de continuidad se propaga explícitamente; nunca se deduce del identificador textual.

### 7. Decisiones pendientes

1. ¿Se aprueba conservar rc compatible y exigir consumo del sobre, o también una migración de rc?
2. ¿Qué nombre y versión tendrá la distinción explícita descriptor/recibo?
3. ¿Cómo se aceptarán sobres históricos sin esa distinción? Recomiendo contexto de operación más validación del artefacto; nunca inferencia por nombre de archivo.
4. ¿El envoltorio local se corrige como evidencia de consumo o se sustituye por un ejemplo portable soportado? Su modificación local sola no beneficia a otros proyectos.
5. **VERIFY:** consumidores externos al repositorio y lector efectivo de `.rc`, para comprobar adopción en 007-005.

### 8. Evidencia operativa

- Operaciones realizadas: lectura completa de `PACKET.md`, contrato y principios; `sha256sum`; búsquedas `rg -n` sobre scripts, fuentes, agentes y referencias; lecturas `sed`/`cat`; `git status --short`, `git rev-parse HEAD`, `git diff --stat`.
- Salidas relevantes: hashes coincidentes; HEAD citado; estado inicial y final con la misma entrada ` M docs/.cdad-state.json`.
- Hubo consultas a rutas inexistentes, corregidas al localizar las rutas reales; no se usaron como evidencia.
- Una búsqueda incluyó logs locales y produjo ruido histórico; se acotaron las consultas posteriores a fuentes y archivos concretos.
- **Archivos modificados por este rol:** ninguno.
- **Tests ejecutados:** ninguno; discovery read-only, sin suite completa.
- **Commit creado:** ninguno.
## Decisiones del orquestador (HITL delegada, 2026-10-24)

Criterio: lo que lee de verdad cada consumidor y la compatibilidad del contrato publicado.

1. **rc compatible; sin migración de rc en esta feature.** El rc sigue significando «la interfaz produjo un sobre». Cambiarlo no distingue descriptor de recibo y rompe consumidores con `set -e` antes de leer el diagnóstico. El cierre de AC-7.8 es que **ningún consumidor documentado avance por rc o `termination` solos**.
2. **Distinción explícita en el sobre:** campo nuevo `delivery` con vocabulario cerrado `none | staged | received` (sin descriptor; descriptor `RESULT.json` preparado y aún no recibido; recibo durable ya persistido). `delivery_ref` conserva una sola referencia al artefacto existente. Combinaciones inválidas (p. ej. `delivery=none` con `delivery_ref` no nulo, `termination=blocked` con `delivery=received`) son contradicción: el productor nunca las emite y el consumidor se detiene.
3. **Sobres históricos sin `delivery`:** el consumidor no infiere por nombre de archivo; usa el contexto de la operación (externa → recibo a validar; `record` nativo → descriptor a recibir) y valida el artefacto. Ausente o contradictorio → parar y diagnosticar.
4. **Consumidores a alinear dentro del producto:** el cuerpo del orquestador (`sources/roles/orchestrator.md` y adaptadores), `references/re-entry.md` y `references/cli-delegation.md` declaran la regla de consumo por `delivery`. El envoltorio local `.cdad/local/deleg.sh` no es producto: se registra como consumidor local a revisar en 007-005, sin cambiarlo aquí.
5. Un `--strict-exit` opcional es un detalle no esencial: fuera de alcance, sin deuda.

Se autoriza el draft de la spec.
