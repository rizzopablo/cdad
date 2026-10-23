# Próximo epic — Discovery notes (E1, borrador)

Fecha: 2026-10-23. Estado: **borrador de E1; sin epic creado, sin id, sin cambio de estado.**
Autoridad: **HITL delegada al orquestador (Claude) el 2026-10-23** — ver §7.

## 1. Insumos reconciliados

| Insumo | Qué aporta | Relación |
|---|---|---|
| [Construcción incremental (S-ITER-01)](proposed-cycle-incremental-construction.md) | Conservar avance y aprendizaje; encargos con margen de corrección; re-entry honesto; separar exploración y validación. | Su propio texto pide recibirse dentro de A/B. **Se consolida, no se ejecuta aparte.** |
| [Plan Superlite, Epic A](superlite-followups-2026-10-19/plan.md) | A1 criterio de división, A2 fronteras y transferencia de hallazgos, A3 recepción. | Planificación y evidencia de capacidades. |
| [Plan Superlite, Epic B](superlite-followups-2026-10-19/plan.md) | B1 simplificar operaciones frecuentes, B2 continuidad de reparación, B3/B4 concurrencia. | Operación del ciclo. |
| [S-SYS-01](../../findings/system-capability-planning-evidence-2026-10-21.md) | Dependencias operativas no representadas, aprendizaje no transferido, niveles de evidencia (decisión/ejecución/integración/uso). | Entrada necesaria de A1. |
| AC-7, `docs/epics/epic-006-opencode-concurrency/closure.md` (hallazgos 1-9 + post-cierre) | Uso real de la versión desplegada en el otro proyecto activo, 2026-10-22/23. | Evidencia nueva y medida; cae casi entera en B1/B2. |

## 2. Qué ya está cubierto (no se replanifica)

- Tabla de decisiones vigentes que viaja en el paquete — 006-004.
- Revisión independiente de spec/plan antes de aprobar — 006-006.
- Entrada única de despacho por runtime, `record` nativo, recibos — 006-005.
- Modelo por configuración, CDAD no elige — ADR-033 / I8.
- Consumes/Produces, detalle progresivo, evidencia proporcional — fuentes canónicas existentes (inventario, «Límites»).

## 3. Brechas abiertas con evidencia

**Operación del ciclo (B1/B2), medidas en AC-7:**
1. La ruta de despacho no registra `begin`/`checkpoint`: continuidad 3 días atrasada, detectada sólo por `reconcile`.
2. `reconcile` ignora la disposición del estado (`dispatched-unknown` permanente) y no nombra la salida.
3. `status`: misma `entry` para «despacho sin resolver» y «sólo `resume`»; no expone el gate vigente.
4. Verbos repartidos entre tres scripts sin mapa en el cuerpo del orquestador (3 invocaciones erróneas).
5. No hay verbo para rehacer un paquete abandonado.
6. Señales de éxito engañosas: W-2 (`blocked` con rc 0) y `record` sin `--parent/--since` (rc 0 sin entrega).
7. `scope_validation: unknown` (sin productor de `observed_changes`).

**Planificación y evidencia (A1/A2), de S-SYS-01 y del consumidor:**
8. Tareas válidas que no representan dependencias operativas (configuración efectiva, identidad, estado previo, efectos).
9. Hallazgos de exploración que no llegan al artefacto consumidor.
10. Evidencia sin nivel declarado; rechazo permanente que satisface la garantía defensiva.
11. Plan que deja de reflejar el trabajo real: en el consumidor, `plan.md` decía «T3b no ejecutada» mientras el trabajo había avanzado por G5-G21 (2026-10-23).

**Construcción incremental (consolidada):** conservar estado y aprendizaje en reparaciones (≈ B2) y encargos con margen de corrección y re-entry honesto (≈ A2/B2).

## 4. Fuera de alcance inicial

Concurrencia (B3/B4) hasta que la operación serial sea confiable; scheduler, jobs, rol nuevo, formato de recibo nuevo, selección de modelos, telemetría nueva, porcentajes de cobertura.

## 5. Consumidor y restricciones

- Consumidor de recepción: el otro proyecto activo (trabajo pendiente real; F001-003/F001-004).
- El ciclo usa la versión instalada; despliegue sólo por decisión del dueño, entre ciclos.
- Publicación: anonimización antes de cada push.

## 6. Preguntas abiertas al dueño

Ver la conversación de E1 del 2026-10-23; las respuestas se registran aquí antes del gate E1 → E2.

## 7. Mandato — 2026-10-23

El dueño: «Tengo que salir. Te delego todo hitl, pero consulta al architect cada vez que tengas una duda importante, ok? él te va a apoyar.» (Pablo, 2026-10-23).

- **Delegado:** Claude (sesión de Claude Code en este repo), orquestador.
- **Alcance:** las decisiones de E1/E2 de este epic (alcance, orden, plan), aprobación de spec/plan de sus features, gates, priorización de reviews y Memory Bank con evidencia. Las preguntas abiertas de alcance se resuelven consultando al architect (rol read-only) y quedan registradas con su respuesta.
- **Reservado al dueño** (igual que en epic-006): despliegue o activación global, cambios en HOME, servicios o procesos compartidos, actualizaciones del runtime, push y publicación.
- **Vencimiento:** al cerrar, cancelar o revocar el epic. La severidad de los defectos no se relaja.
