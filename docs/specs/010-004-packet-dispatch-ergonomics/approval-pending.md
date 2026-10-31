# 010-004 — aprobación del owner pendiente

Estado operativo: **specification-awaiting-owner**. No es aprobación ni autorización de tests o implementación.

Objeto: `spec.md`, SHA-256 `054d4657b5dae096114a9e41beaad3c356234fe8fd5c60236752c24c89212008` (sin modificación).

## Resultado de revisión

`plan-review.md` contiene el FINAL TEXT de reviewer-plan-review-005, sesión `<session>`: **0 BLOCKING, 3 OPTIONAL**. N-2, N-3 y O-C cerrados; cierres anteriores conservados según el dictamen. El informe conserva sus abstenciones y no aprueba la spec. La revisión anterior queda en `plan-review-v3.md`; las anteriores se preservan.

## Propuesta de disposición, no resolución

- **N-4:** wording legacy `dispatched` con recibo. Proponer aclaración focal con el owner si lo desea; no afirmar que está resuelto. La implementación no debe cerrar vías históricas soportadas. Esta advertencia no introduce una interpretación técnica nueva vinculante.
- **N-5:** precedencia de diagnósticos. Proponer decisión focal del owner si lo desea; no imponer aquí una precedencia ni afirmar que está resuelto.
- **N-6:** nit de consistencia; proponer postergarlo sin bloquear la aprobación.

No se abre otro loop architect/reviewer por estos opcionales. El owner puede aprobar el borrador exacto con opcionales postergados y límites legacy documentados; la disposición definitiva sigue pendiente.

## Resumen para aprobar

1. **C emitida por renderer, preferente para nuevos despachos nativos.** Confirmar expresamente §2.1: C como alcance de esta unidad, «sin retranscripción» como carga del cuerpo publicado, no conexión mecánica renderer→herramienta nativa. Se conserva A explícita y el render completo predeterminado.
2. **Toda preparación nueva utiliza v2; legacy conserva reentrada histórica bajo condiciones existentes.** Ya decidido en `owner-decision-v2-new-assignments.md`: no se vuelve a preguntar por separado ni se transforma en aprobación global de la spec.
3. **Diagnósticos seguros y observabilidad limitada.** Causa accionable sin divulgar contenido; evidencia insuficiente no demuestra corrupción ni permite ignorar divergencias conocidas o autoridad inválida. No se promete certificación independiente de entrega sin capacidad demostrada.

Siguiente acción: pedir aprobación explícita del owner sobre este digest, incluyendo resolución expresa de §2.1 y disposición de opcionales. Hasta entonces: sin audit/RED, sin nuevos packets, sin aprobación automática, sin push.
