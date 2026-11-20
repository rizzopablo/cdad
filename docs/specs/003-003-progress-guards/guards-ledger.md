# Guards ledger — 003-003 (uso real, T5)

Versión operativa: `939f501`, raíz aislada `<home>/.cache/cdad-adopted-939f501`. Consumo verificado: un agente nuevo cargó `cdad-cycle` desde esa raíz y vio `scripts/cdad_guard.py`.
Datos **reales**: cuatro sesiones del desarrollo de esta misma feature. **No hay incidentes provocados.**
Grabador: un script **desechable** fuera del producto, `evidence/t5/recorder.py`, que lee la DB de OpenCode en solo lectura; producirlo fue trabajo del orquestador (deepseek). Salidas: `evidence/t5/*.classify.json`.

| Sesión (real) | Situación real | Lo que dio el guard | Lectura | dedup_key | cambio_relevante |
|---|---|---|---|---|---|
| `ses_eec41f67…` (T1 GREEN) | **C2 + C1 reales**: la suite se lanzó en segundo plano y murió con la sesión, y el turno se cerró «esperando que me retomen» | 0 incidentes, 0 escaladas | **Falso negativo.** La llamada en segundo plano vuelve `ok` al instante y la espera se ve como `sleep`/`echo` `ok` | — | — |
| `ses_eebf15cd…` (T2 rf GREEN) | **C2 + C1 reales**, repetidos; luego se recuperó con una reanudación | 1 `repetition-without-progress` ×5 | **Falsa alarma**: 5 ediciones distintas al mismo archivo. El incidente real **no** se detectó | `repetition-without-progress·sha256:2405a99d…·exec-003-003-progress-guards-001·…-green-00x` | — |
| `ses_eeb95ac0…` (T3 rf GREEN) | Sana (475 passed) | 1 `repetition-without-progress` ×7 | **Falsa alarma**, por la misma causa | misma huella; difiere solo el `packet_id` | — |
| `ses_eeb7c146…` (T4 test-writer) | Sana | 0 | Correcto | — | — |

## Qué permitió decidir
Con datos reales, el guard **no** detectó los incidentes reales. Los detectó el seguimiento del orquestador:
- el PID real;
- el archivo `.rc`;
- la inactividad (DONE/GONE/STALLED);
- la lectura del final de la salida.

Las dos alertas del guard fueron falsas. Costo de la supervisión: una corrida de deepseek para el grabador y 4 `classify`, de menos de 1 s cada uno.

## Causas (verificadas en las trazas)
1. **C2 es invisible en la traza:** un comando con `> log 2>&1 &` o `nohup` vuelve `ok`. Hace falta que el grabador marque los lanzamientos desacoplados como `result_class: unknown`, con una limitación declarada.
2. **C1 es invisible:** el cierre de turno sin entrega final no es una llamada de herramienta. Hace falta una señal de fin de sesión: la última parte del asistente, sin el artefacto `produce` ni un receipt.
3. **Progreso demasiado grueso:** el digest del *conjunto de rutas* no ve cambios de contenido, y eso causa las falsas alarmas. Se necesita un digest del contenido o del diff.
4. `classify` ignora `at` en `tool_call`, así que los huecos de más de 20 min no existen para el guard.
5. Nota de uso: `--trace` se resuelve contra `--project-root`.

## Pendiente (sin comprobar)
- No se comprobó la escalada real (`unknown`) ni el polling con datos reales: el grabador no los produce.
- El dedup se comprobó solo con fixtures (T4). En el uso real, la misma huella aparece en dos packets distintos y el `dedup_key` las separa por `packet_id`, como corresponde.

## Corrección tras revisión con el dueño (2026-10-07)
Los C1/C2 «reales» de hoy son, con alta probabilidad, **artefactos del modo de despacho del orquestador** y no del entorno nativo. El registro muestra que el implementer usó el shell nativo de OpenCode con `"background": true`. En una sesión OpenCode normal, esa opción notifica al agente cuando el comando termina y el agente sigue trabajando. El orquestador, en cambio, lanzaba los roles con `opencode run`, que mata el proceso al terminar el turno y con él el trabajo en segundo plano y la notificación. En el entorno nativo no hay dos niveles de agentes. No se comprobó dentro de una sesión OpenCode nativa.
Consecuencias:
- G1 baja a **media**: el lector por runtime sirve para calibrar, no es urgente.
- G2 se **retira**: `launch.sh`/`watch.sh` son herramientas de este modo de orquestación, no producto.
- Las falsas alarmas por el progreso medido por conjunto de rutas siguen siendo un hallazgo válido (deuda media).
