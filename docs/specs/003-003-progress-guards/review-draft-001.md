**Veredicto por eje:** Correctness · Architect · Security: [(2 , m)] / [(2 , l)] — sin bloqueantes. Readability: [(1 , m)]. Performance: [(1 , l)].

## Veredicto

**APROBABLE CON CORRECCIONES MENORES — 0 bloqueantes, 1 Requerido agrupado, 3 opcionales.** Los ejes verdaderamente en riesgo se cierran blanco en este borrador: (a) **todas las señales citadas existen de verdad** — 18/19 anclas verificadas file:line contra el repo real (el resto: abstención); (b) el MVP **es sobredimensionado: 7 tareas → 5 proposables sin pérdida**; (c) **no implementa 003-004** — exclusión explícita y verificada; (d) **no contradice ninguno de los 4 criterios** — los declara como invariante o decisión, no como contradicción.

## (a) Señales citadas: verificadas una a una (cero señales inventadas)

| Ancla del draft | Verificación | Resultado |
|---|---|---|
| `opencode-session-scan.py:21-54` (DB RO, `session_v2`+`session_message`, `tool`, `permission.rejected`) | líneas 21-54 del archivo real | ✅ exacto |
| `scan:23` `parent_id`; `scan:34-41` steps por sesión | ídem | ✅ |
| `runtime-discovery.md:23-25` children/fork; `:27-29` tokens/step-finish/costo; `:60-65` config heredada | README del probe | ✅ las 3 |
| `exec-…-bootstrap-001/dispatches/review-009-a1.json` | existe en `<repo>/.cdad/executions/exec-004-002-project-execution-bootstrap-001/dispatches/review-009-a1.json` (26 despachos) | ✅ |
| `003-001…/spec.md:478-480` estados del paquete; `:560-568` unknown=inválido | líneas 478-479, 566-567 | ✅ |
| `packet-metric.schema.json`: `retry_count`, tokens, `context_limit`, `additionalProperties:false` | líneas 5, 21-22 del schema | ✅ |
| `003-002/closure.md:13-19` `semantic_status:pending`; `:53` single-writer | tabla + "invariantes verificados" | ✅ |
| Incidente 2.073 reintentos / ~20 h / 15,86 vs 0,14 | `docs/specs/opencode-read-map-and-steps-2026-09-29/spec.yaml:19-20` — frase exacta | ✅ |
| Techo `steps:300` desplegado pero **NOT exercised live** | `evidence/results.md:24` | ✅ (declarado en V5, honesto) |
| "Esperar sobre la base de sesiones, no el cliente" | `evidence/results.md:37-39` | ✅ |
| `friction-intake:42-44` cliente muere/sesión viva; `:44-48` ECONNRESET+`time_created`; `:52-61` `install.sh`/`git stash`; `:13-14` rechazo=defecto, no métrica | ídem | ✅ las 4 |
| `evidence-utility:50-54` 5 ocurrencias suite-background; `:15-21` ~10 citaciones; `:104` tokens desconocido | ídem | ✅ |
| `re-entry.md:67-79` regla de dos intentos / no reintentos ilimitados | sección canónica | ✅ |
| `planning-contract-draft.md:132-137` `observable_checks`; `:163-167` revisión independiente; `:208-209` no-relajaciones/desconocidos; `:213-216` `additionalProperties:false` | existe en `docs/epics/epic-004-single-source-planning/` | ✅ |
| `t7-live-walk.md:38-66` grep/glob mediados por patrón | `004-002…/t7-live-walk.md` | ✅ |
| `ADR-011:75-79` "worktree no es un sandbox"; ADR-013, ADR-003 existen | `docs/adr/` | ✅ |
| `docs/cdad-policy.json`, `cdad_packet.py`, `cdad_result.py`, los 3 validadores | existen | ✅ |

**Única ancla dudosa** (5 citas, agrupadas en el hallazgo F2): verdad real, archivo equivocado (ver abajo).

## Bloqueantes

**Ninguno.** No encontré señal inventada, violación silenciosa de un criterio del encargo, ni invasión de los contratos de 001/002/003-004 con evidencia de consecuencia. La calibración pedida (bloqueante solo con archivo:línea + consecuencia + condición de cierre) no se satisface para ningún item; lo más serio es F2, y la condición de cierre son 5 minutos de corrección mecánica antes de materializar `spec.md`/`plan.md`.

## Hallazgos no bloqueantes

**F2 — [Requerido, no bloqueante] Citas apuntando a `remaining-features-handoff.md` donde el contenido real vive en `handoff-architect-001.md` (5 casos) + 1 cita muerta en el plan del epic.**
- Evidencia: `remaining-features-handoff.md:38` es la fila "| Active record/checkpoint | 004 de epic 003 |…" del draft C4; el texto real "un rechazo no es mala conducta" está en `handoff-architect-001.md:38`. Ídem: `…remaining…:41` usado en D7 (real: `handoff-architect-001.md:41`), `:44` en D5 (real: encargo:44), `:47` en D10 (real: encargo:47 — y la segunda pata `epic plan.md:37` de la misma decisión apunta a "El mandato de este epic está en execution.md", línea sin relación; el soporte real es `plan.md:86`), `:54-56` en D11 y T7 (real: encargo:54-56, el texto "situación, evidencia, decisión, falsas alarmas, costo, pendiente").
- Consecuencia: el dueño que resuelva **D10 (decisión B, frontera con 003-004) siguiendo la cita cae en texto ajeno**; el método del borrador es "citas ancladas", y 5/19 rompen la trazabilidad.
- Condición de cierre: re-apuntar las 5 citas al encargo y `D10→plan.md:86`. **No porlonga el ciclo** — todo el contenido real ya está verificado por mí (tabla §a), así que la sustancia se aprueba igual; es corrección de formato de evidencia antes de materializar.

**O1 — [Opcional, bucket l] `C3` infla levemente el techo `steps:300`.** `(architect-draft-001.md:23)`: "El techo `steps:300` ya corta el runaway mecánico" — pero V5 (`:202-203`) declara honestamente **NOT exercised live** (`results.md:24`). Reformular: "puede cortar; sin exercise en vivo". Coste: 1 línea, cero retardo.

**O2 — [Opcional, bucket l] Ambigüedad en archivos de T3.** `(architect-draft-001.md:305)`: T3 lista `docs/cdad-policy.json` en `files` (escritura), siendo que el invariante 10 y D6 describen el pre-flight como **lectura** de la política. Si GREEN modifica el policy file compartido, arrastra regresión cross-feature sin necesidad. Aclarar "morphology": es write de anotaciones o read-only — si read-only, sacar de `files`. No afecta coherencia del MVP.

**O3 — [Opcional, bucket l] P7 "no vuelve a alertar" necesita criterio de "cambio relevante".** `(architect-draft-001.md:129-132)`: el de-dup requiere decidir semánticamente si algo "cambió de forma relevante". El draft lo deja a D11/ledger (aceptable y no bloqueante), pero el cierre del incidente real (T5: "2.073 reintentos sin `steps:300`") podría re-alertar si el orquestador no tiene un key de dedup explícito. Dejar anotado en T7 que `guards-ledger.md` registre el "key de dedup usado" como campo.

## (b) Propuesta de fusión de tareas: 7 → 5 (sin pérdida de coherencia)

El pipeline ya es totalmente serializado (`"parallel": []` en las 7) — el split en 7 no compra paralelismo, solo mini-ciclos RED/GREEN. Dos fusiones son seguras porque las piezas comparten **archivo único** (`cdad_guard.py`), **contrato productor** y el mismo dominio de decisión:

| Fusión | Contenido combinado | P-Ps que conserva (como sub-postcondiciones, cada una con su test focal) | Por qué es segura |
|---|---|---|---|
| **T1+T2 → U1** "Núcleo de traza + clasificación de repetición/polling" | traza `trace-v1` + **núcleo determinista** + polling/no-alarma | P1, P2, P7 | Misma superficie, misma DB de sesiones; "repetición improductiva" y "legítimo que progresa" son el mismo **truco de separación** (§1 los distingue **junto**): separarlos en RED/GREEN es doble dispatch para un solo código |
| **T4+T5 → U2** "Presupuesto durable + eventos + tabla de escalado" | presupuesto `budget-v1` + `guard-event.schema.json` + tabla cerrada | P4, P5 | Comparten el **canal de escritura** (`guards/`) y el paquete de escalado **consulta** el presupuesto para decidir si hay margen: separarlos obliga a orquestación redundante para una integración ya implícita |
| **Se quedan solas: T3** (previo-flight, dominio policy/permisos aislado), **T6** (product owner: test-writer —inquilino correcto), **T7** (owner: orquestador, **dueño distinto**; es la adopción en límite real, gate del epic) |

Cuidado: T6 y T7 **no se fusionan** — `T7.owner = "orquestador"`, es la validación de "capacidad aplicada en un desarrollo real" (requisito inamovible del `remaining-features-handoff.md`).

## (c) No implementa 003-004 — verificada en blanco

- No produce checkpoints, ni reconstrucción, ni active record, ni triggers de rotación.
- **Frontera próstalic:** D10 + Fuera de alcance §5 + invariante 8 declaran explícitamente solo "schema de evento/presupuesto estable, keyed por `execution_id`, sin truncar" — el mismo contrato que `remaining-features-handoff.md:223-224` exige como **entrada** de 003-004 ("003 aporta presupuestos, eventos, acciones… No diseñar continuidad ignorando esos schemas"). Compatible, no invasivo. ✔

## (d) Criterios del encargo — sin contradicción

| Criterio | Unicidad | Dónde cumple |
|---|---|---|
| Límite de intentos = **señal**, no falta | cumplido como decisión B, no como estática | D3 (artifact-draft:46) + invariante 2 + `re-entry.md:79` |
| Rechazo ≠ mala conducta | aplica en C4, P3, invariante 2, T3 (sin auto-grant/auto-harden), y clasifica por objetivo/rol/scope | artifact-draft:24, 143-144 |
| Timeout ≠ bloqueo | invariante 3 explícito + distinción §1 (long-but-healthy vs stalled vía `time_created`) | artifact-draft:144-145, 30 |
| `unknown` permanece `unknown` | el guard no fabrica éxito; tokens/exit/context= `null` (P5, criterio 7, "Sin señal fiable" §1) | artifact-draft:34-36, 124-125, 174 |
| (extra) Falta de progreso ≠ contar herramientas | P1 no cuenta llamadas; exige **regla explícita + ausencia de cambio en artefacto/state/git** | artifact-draft:110-113 |

## Cierre y abstenciones

- Entregado: veredicto, 0 bloqueantes, 1 Requerido (F2 cierre mecánico), 3 opcionales, fusión 7→5.
- Itens de cierre propuestos re-ejecutables por mí si el dueño desea materialización tras resolver D1–D7 (borrador) + F2.

## Abstenciones

- **No ejecuté sondas nuevas sobre la DB de OpenCode** (el encargo y V6 las prohíben hasta resolver el aislamiento de config heredada — `runtime-discovery.md:58-63`); verifiqué la *estructura* de señales contra el scanner y documentación, no contra datos en vivo.
- **No verifiqué la cita de 5 casos de "aplicado 10×" exacto** (es ~7 suites citadas en `evidence-utility:15-21`; el número redondeado no altera la premisa de C2 porque la asignación a T4 de `evidence-utility:50-54` sí está verificada).
- **No afirmo verificado el `status` de sesión vivo vs estancado** (la pregunta es V2 del propio draft — honestamente marcada VERIFY por el autor, coincide con mi abstención).
- No bloqueo D1–D7: son decisiones de dueño, fuera de mi capacidad como reviewer (responsabilidad: no apruebo, señalo solo que ninguna decisión B quita el veredicto "aprobable con corrección F2 + O1").
