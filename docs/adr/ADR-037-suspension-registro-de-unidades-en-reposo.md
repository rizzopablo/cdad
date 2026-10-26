# ADR-037: La suspensión es un registro de unidades en reposo, no una segunda ejecución

- **Status**: Proposed
- **Date**: 2026-10-25
- **Confidence**: Media
- **Aprobación**: orquestador bajo HITL delegada del epic-007 (review de 4 rondas → APTO CON
  AJUSTES, sesión `ses_e8ad5f723ffenb7IaCoN0egiCv`), a partir del borrador del scribe (patrón
  Scribe; ADR-003/ADR-011).
- **Origen**: `007-007-suspend-resume-units` (`spec.md` PC-01..PC-17 / A1–A5; `docs/planning/handoff-2026-10-24-epic-007.md`, secciones «007-007» y «007-007 en cierre»).

## Contexto

El ciclo ejecuta **una sola unidad** y el estado del proyecto guarda el binding activo (feature,
etapa, subfase, paquete, ejecución). Interrumpir una unidad para trabajar otra obligaba a cerrarla o
retirarla: no había forma de pausar y volver. Dos bloqueos reales lo mostraron — la unidad 007-004
quedó abierta en RED bloqueando `open-unit`, y la ejecución de este repo necesitó dos excepciones de
arranque (despachos nativos sin registro) porque el ciclo serial no permitía cambiar de unidad.

El paralelismo (B3/B4, epic siguiente) está explícitamente fuera de alcance. La pregunta es **cómo
interrumpir y retomar sin convertir el estado en un mapa de ejecuciones concurrentes ni en una pila
implícita**, y sin que ninguna operación existente pueda avanzar una unidad dormida.

## Decisión

1. **Registro por id, no pila.** Se conserva el binding activo y se agrega `suspended_units` como
   campo aditivo (`{}` si falta; mal formado es incoherencia, no ausencia). Una suspendida **no es
   ejecutable**: no despacha, no recibe, no transiciona (I1, I7).
2. **Estado de unidad separado del estado del proyecto.** Se preservan valor **y presencia/ausencia**
   de un inventario normativo único —`active_feature`, `current_stage`, `tdd_substage`,
   `postconditions_status`, `audit_status`, `review_status`, `active_packet`, `execution`— y **no** se
   archivan historia global, epic, autoridad, política, aprobador, versión ni metadatos. La
   restauración no revierte estado global.
3. **Reanudación verificada, no confiada.** Se construye una vista candidata sin publicarla y se
   valida contra identidad y binding, epic y autoridad vigentes, política y versión, digests de
   `resume_checks`, aprobación y contrato pineado, y cadena de continuidad. El verbo no aprueba
   sustituciones ni tiene opción de omisión; lo inconcluso nunca equivale a ausencia ni a evidencia
   vigente (I5).
4. **Suspensión ≠ retiro.** Un `prepared` sigue preparado; no se usa `withdraw`, no se marca éxito,
   no se cierra (I2). La suspensión no exige suite verde: RED con entrega recibida es borde válido.
5. **Continuidad enlazada.** Con cabeza existente se anexan checkpoints por `prev` con decisión y
   `next_action`; sin cabeza no se fabrica cadena ni se crea `begin`, recibo o ejecución nueva.
6. **Selección explícita.** `--feature` obligatorio; sin selección por directorio reciente, orden ni
   única candidata (I8). La orientación expone `units-suspended`, `select-unit` como **instrucción**
   y `next.alternatives`, sin elegir ni abrir por su cuenta. Es una ampliación aditiva del dominio
   cerrado de 007-001/ADR-027, sin reemplazarlo.
7. **Un punto de guarda para todos los consumidores.** Toda entrada mutante resuelve la unidad desde
   su propia identidad (paquete/request/ejecución) y rechaza antes del efecto; las lecturas quedan
   permitidas y no habilitan avance.

## Alternativas rechazadas

- **Pila de unidades** (desapilar al reanudar): reanudación implícita, incompatible con I8 y con la
  trazabilidad; el orden de suspensión no es una decisión del usuario.
- **Mapa general de ejecuciones concurrentes:** es paralelismo (B3/B4), otro epic; además rompe I1.
- **Guardar una copia del estado global y restaurarla:** revierte avances de historia y de otras
  unidades (I3).
- **Cerrar o retirar la unidad para liberar el ciclo:** destruye trabajo en curso y confunde
  suspensión con entrega, fallo o cierre (I2).
- **Copiar la guarda en cada CLI:** divergencia asegurada; se adoptó el punto compartido (precedente
  ADR-036).
- **Reanudar sin revalidar** («el estado guardado ya estaba aprobado»): rehabilita evidencia vieja y
  contratos distintos (I5).

## Consecuencias

**Positivas.** El ciclo serial deja de exigir excepciones de arranque para cambiar de unidad: se
puede pausar una unidad trabada, trabajar otra y volver. El estado conserva una sola unidad
ejecutable y la traza completa (ejecuciones, requests, paquetes, recibos y ancestros permanecen). La
publicación es transaccional bajo el lock y la repetición no tiene efectos extra.

**Negativas / límites.** El registro agrega un inventario que hay que mantener coherente: todo campo
futuro específico de unidad debe entrar en el inventario canónico (no en listas por operación). La
reanudación puede bloquear por pins, autoridad o política, y desbloquearla exige los procedimientos
existentes: no hay bypass. Límites declarados: la clasificación gestionado/standalone se elude
retirando además el registro canónico (no es frontera de seguridad y no habilita despacho); los
escritores de continuidad no comparten el lock del proyecto (preexistente); no se re-verifica la
aprobación ante borrado manual del historial; la identidad la suministra el llamador.

**Confianza Media** porque: (i) el comportamiento **no existe en la versión instalada** (`6b3da4e`)
hasta el despliegue; (ii) el uso real previsto —suspender 007-004, abrir 007-006 y reanudar 007-004—
es criterio de aceptación declarado y **todavía no ejercido**; (iii) quedan límites con condición de
cierre. No es Baja: la decisión está implementada, cubierta por 16 casos, suite completa corrida
(1582 passed / 38 failed ajenos, todos del RED de 007-004) y una review de 4 rondas sin bloqueantes
abiertos.

## Cumplimiento

`tests/test_007_007_suspend_resume_units.py` (16 casos, parametrizados) cubre: preservación y
restauración exacta del estado, bordes seguros (prepared, dispatch sin paquete, RED recibido),
checkpoints enlazados sin historia fabricada y sin estado gestionado, selección explícita y
exclusión de la activa, rechazo por autoridad/contrato/política/evidencia, apertura conservando el
registro y las dependencias, prohibición de mutaciones parametrizada por consumidor, proyección de
`status`/`validate-state` con `units-suspended`, atomicidad de publicación y repetición, y el
recorrido integrado (suspender A en RED, abrir B, reanudar A hasta `verified begin`).
