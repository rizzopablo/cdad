---
epic_id: epic-007-reliable-cycle-operation
epic_name: Operación confiable del ciclo
created_at: 2026-10-23
approved_by: Orquestador (Claude) por HITL delegada del dueño
approved_at: 2026-10-23
---

<!-- cdad:plan-anchors
{"history": ["Plan changes", "Cambios al plan"], "authorization": ["Stakeholders", "Autoridad"]}
-->

# Epic 007: Operación confiable del ciclo

## Resumen

El recorrido real de AC-7 (2026-10-22/23) mostró que retomar, despachar y recibir con la versión
desplegada funciona, pero en la ruta observada exigió diagnóstico externo repetido: la entrada no
distingue situaciones, un intento abandonado queda irresoluble, la ruta no integra la continuidad
existente en sus bordes y
algunas señales se leen como éxito sin entrega. Este epic deja ese recorrido serial confiable,
reutilizando los mecanismos existentes. Planificación y evidencia de capacidades (Epic A de
Superlite, S-SYS-01) quedan para el epic siguiente.

Insumos: `docs/planning/next-epic-discovery-notes.md` (E1, con la consulta al architect del
2026-10-23), `docs/epics/epic-006-opencode-concurrency/closure.md` (hallazgos de AC-7),
`docs/planning/superlite-followups-2026-10-19/plan.md` §5 (B1/B2),
`docs/planning/proposed-cycle-incremental-construction.md` (parte de continuidad y reparación).

## Alcance

**Dentro:**
- Orientación desde la vista compacta: situación, siguiente operación, dónde ejecutarla y referencia verificable a la aprobación vigente.
- Recuperación de un despacho abandonado o resuelto, con sucesor trazable y sin repetir efectos.
- Continuidad en los bordes del recorrido normal (antes del despacho, después de la recepción), incluida la reparación: objetivo, cambios, evidencia válida, próxima hipótesis.
- Terminación y entrega no confundibles para el consumidor (bloqueo, resultado disponible, recibido), resolviendo protocolo y consumo.
- Recepción serial real en el otro proyecto activo.

**Fuera:**
- Concurrencia (B3/B4), scheduler, jobs, rol nuevo, formato de recibo o registro de intentos nuevos, selección de modelos.
- Productor de `observed_changes` (brecha 7): deuda aparte salvo bloqueo demostrado del consumidor.
- Brechas 8-11 (dependencias operativas, transferencia de hallazgos, niveles de evidencia, plan desactualizado): epic siguiente.
- Una fachada CLI que sólo oculte los scripts sin completar operaciones.

## Descomposición en features

| # | Feature ID | Resultado consumible (1 línea) | Cierra | Dependencias | Paralelizable |
|---|-----------|------------------------------|--------|--------------|---------------|
| 1 | 007-001-unambiguous-entry | La vista compacta nombra situación, siguiente operación con su script, y referencia a la aprobación vigente | AC-7.2, .5, .7 | — | No |
| 2 | 007-002-dispatch-recovery | Una disposición registrada resuelve el intento ante `reconcile`; se prepara un sucesor trazable sin reconstrucción manual | AC-7.3, .4, .6 | 001 | No |
| 3 | 007-003-continuity-at-edges | El recorrido normal deja continuidad vigente en sus bordes y una reparación se retoma sin repetir intentos | AC-7.1; B2; continuidad de S-ITER-01 | 001; coordinada con 002 | Parcial (con 004) |
| 4 | 007-004-termination-not-success | El consumidor distingue comando procesado, bloqueo, resultado disponible y recepción; no avanza por rc 0 solo | AC-7.8; W-2 | 001 | Sí (con 003) |
| 5 | 007-005-serial-reception | Un tramo pendiente autorizado del otro proyecto activo atraviesa entrada–despacho–recepción con la versión adoptada | recepción del epic | 001-004 + adopción autorizada por el dueño | No |

Detalle de cada una: su propia spec en `cdad-cycle`. Las líneas de código que sustentan cada
brecha están en la consulta del architect (discovery notes §8).

## Contratos entre features

- **Disposición canónica:** `register-transition --transition disposition` sigue siendo el único registro de la decisión sobre un intento; 002 y 003 la consumen, no crean otra.
- **Vista compacta (`cdad_packet.py status`):** 001 define los campos de situación y siguiente operación; 002-004 los alimentan sin cambiar su forma.
- **Continuidad (`cdad_continuity.py`):** almacenamiento y encadenamiento de checkpoints se reutilizan; 003 integra el recorrido, no inventa almacenamiento.

## Criterios de aceptación del epic

- [ ] Las 5 features cerradas individualmente.
- [ ] **Recorrido feliz:** desde reposo, un orquestador sin diagnóstico externo ni lectura de implementación (puede ampliar por las referencias que la vista indica) identifica la acción correcta en la vista, despacha, registra y recibe una unidad, con continuidad vigente al terminar.
- [ ] **Recorrido de fallo:** un intento que falla sin entrega se dispone, `reconcile` deja de reportarlo irresoluble, se prepara el sucesor y se recibe, sin repetir efectos ni editar a mano el state o el encargo.
- [ ] **Señales:** ningún consumidor documentado de CDAD avanza a «éxito» con un bloqueo o sin entrega.
- [ ] **Precondición de la recepción:** versión candidata adoptada con autorización vigente del dueño y procedencia comprobada. Si falta, la recepción queda pendiente y registrada; no se sustituye por pruebas controladas ni se activa el candidato globalmente.
- [ ] **Recepción real** en el otro proyecto activo con evidencia positiva de la capacidad del tramo; lo no observado (p. ej. una reparación que no ocurrió naturalmente) se declara «verificado en entorno controlado, no observado en consumidor».
- [ ] Sin mecanismos duplicados (intentos, disposición, almacenamiento de continuidad).

## Riesgos / deuda esperada

- Duplicar autoridad o estado. Mitigación: los contratos de arriba; el review de etapa 4 lo verifica.
- Cambiar códigos de salida sin revisar consumidores. Mitigación: 004 parte del inventario de consumidores; cambiar rc es una alternativa, no la conclusión previa.
- Usar checkpoints para acreditar evidencia invalidada por una reparación. Mitigación: 003 distingue estado construido de evidencia vigente.
- AC-7.9 (modelo pasado contra I8 y reporte inexacto) no es mecanismo nuevo: se verifica en la recepción (005) y en review.
- Deuda que se mantiene: brecha 7, W-U6-*, flakes heredadas, F011.

## Autoridad

- **Aprobación del plan y de specs/planes de features:** el orquestador (Claude), por HITL delegada por el dueño el 2026-10-23 (discovery notes §7); dudas importantes se consultan al architect.
- **Reservado al dueño:** despliegue o activación global, HOME, servicios compartidos, runtime, push y publicación.
- **Operador del resultado:** orquestadores CDAD de los proyectos consumidores.

## Cambios al plan

### 2026-10-23 — Ajustes de la revisión del borrador
Revisión read-only del reviewer (sesión `ses_e94d5fd29ffe…`, APTO CON AJUSTES, sin BLOCKING): se precisa «sin diagnóstico externo», se explicita la adopción como precondición de 005 y se acota el diagnóstico de continuidad a la ruta observada. Hallazgo de producto: no existe `plan-review` para planes de epic (`prepare` exige feature activa).

---

Status: Approved by Orquestador (Claude), por HITL delegada del dueño (2026-10-23), on 2026-10-23
