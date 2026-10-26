# Changelog

Cambios publicados del proyecto CDAD. El historial de desarrollo completo permanece en el
repositorio local; este archivo resume cada publicación.

## 2026-10-26 — Epic 007 «Operación confiable del ciclo» (8/8, cerrado) y reparación de génesis legado

**Publicado como un único commit de resumen.** El detalle por unidad vive en
`docs/specs/<feature>/` y en `docs/progress.md`; el estado del epic, en
`docs/epics/epic-007-reliable-cycle-operation/`.

### Capacidades entregadas

- **007-001 — Entrada inequívoca.** La vista compacta (`status`) declara situación, siguiente
  operación con su script, y una referencia verificable a la aprobación vigente.
- **007-002 — Recuperación de despachos.** Una disposición registrada resuelve el intento ante
  `reconcile`; el sucesor se prepara sin reconstrucción manual ni repetición de efectos.
- **007-003 — Continuidad en los bordes.** `begin` / `verify-begin` antes del despacho y
  `checkpoint-receipt` después de la recepción; reparación de historia legada mediante `reanchor`
  explícito, aprobado y con `legacy_anchor` (enmienda 007-003 §2.3.1).
- **007-004 — Terminar no es entregar.** El sobre de delegación incorpora `delivery`
  (`none | staged | received`) con tabla cerrada; ni `rc` ni `termination` acreditan recepción ni
  aprobación. La compatibilidad histórica se valida y vincula con el verificador del productor.
- **007-005 — Recepción serial real.** Un tramo entre proyectos atravesó entrada → paquete →
  continuidad → despacho → entrega → recepción → cierre con la versión adoptada, sin editar estado a
  mano. Se entrega como evidencia verificable (manifiesto con resolución privada), no como cambio de
  producto. Incluye una desviación de presupuesto declarada y aceptada (dos transportes; el primero
  rechazado por identidad, sin registro ni efectos).
- **007-006 — Retiro y republicación.** `register-transition --transition withdraw` retira con motivo
  un paquete `prepared` que no se despachará y libera `prepare`; `republish-agents` republica los
  agentes derivados sin preparar paquete, conservando el `model:` instalado. Publicación transaccional
  con rollback.
- **007-008 — Acción del cierre de recibo.** Un cierre nuevo deja de heredar la orden previa al despacho
y escribe una acción canónica: recibir es mecánico, no se repite despacho ni recepción, y revisar no
presume aprobación. Los cierres históricos no se migran.
- **007-007 — Suspender y reanudar.** Una unidad se suspende en un borde seguro, se trabaja otra y la
  primera se reanuda explícitamente, sin perder identidad ni repetir efectos. Primera aplicación real
  durante la propia épica.

### Operación

- Despliegue en HOME de la versión adoptada `538ec57`, con respaldo previo y los `model:` del dueño
  preservados.
- Suite completa: **1705 passed, 5 skipped, 0 failed**.
- Gate por superficie incorporado como práctica: los gates focales ocultaban regresiones en
  consumidores de continuidad.

### Deudas declaradas

- `REC-NEXT-ACTION-STALE`: el cuerpo del cierre de recepción conserva el `next_action` previo; la
  vista compacta y `reconcile` protegen contra repetir el efecto.
- `SUITE-CONTAMINATION`: tests que pasan aislados y fallan en corridas grandes por HOME/XDG no
  aislados; auditoría de la suite por capacidad pendiente.
- `SUSP-GUARD`, `SUSP-LOCK`, `SUSP-APPROVAL`, `SUSP-IDENTITY` y heredadas (DT-8/F011, DT-9, CI).
- El epic **cierra 8/8**. El recorrido feliz desde reposo quedó **observado con alcance declarado**
  (entrada y despachos packetizados de 007-008; RED/GREEN/review nativos sin paquete, desviación
  declarada en su cierre). El recorrido de fallo **no se observó como uso real**: su mecanismo está
  verificado en entorno controlado. La suite de cierre fue 1721 passed, 5 skipped, 1 failed aislado
  verde (`SUITE-CONTAMINATION`), y no se declara verde.

### Corrección editorial

- Se sustituyó una ruta absoluta local por `<repo>` en `docs/specs/007-004-termination-not-success/spec.md`
  §11 (evidencia del draft), sin cambio semántico del contrato.
