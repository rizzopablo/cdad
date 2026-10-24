# ADR-036: El verificador de una decisión lo ejerce su productor, y los consumidores lo importan

- **Status**: Accepted (2026-10-24; aprobado por el orquestador bajo HITL delegada del dueño, epic-007).
- **Date**: 2026-10-24
- **Confidence**: Alta.
- **Origen**: `007-002-dispatch-recovery` (§2.1, §2.3; `review-001.md` B-1/B-2).

## Contexto

Una decisión del ciclo se registra en `docs/.cdad-state.json:stage_history` con una **identidad canónica**: un payload completo que produce `cdad_packet` y del que se deriva un SHA-256. Esa decisión tiene más de un consumidor: `cdad_continuity.py` la **observa** (`reconcile`) y `cdad_packet.py` la **usa para crear trabajo** (`prepare --replace-packet`). Son umbrales distintos sobre el mismo registro.

El riesgo medido: si cada consumidor valida a su manera, dos lectores de la misma decisión divergen. La review reprodujo que un consumidor aceptaba payloads **que el productor no puede emitir** (`exemption={}`, `current_stage` fuera de vocabulario, digests que no son SHA-256) con la clave recalculada: el resultado fue `disposed` y, en un caso, la **publicación de un sucesor**. Un subconjunto del payload, con hash correcto, no es la decisión.

## Decisión

El verificador canónico pertenece al **productor** del registro y los consumidores lo **importan**; ninguno lo reimplementa:

1. Un solo punto decide si una entrada es una decisión canónica verificable, y vive en `cdad_packet.py`, junto al escritor de la identidad.
2. `cdad_continuity.py` lo importa (mismo directorio de scripts; precedente en `cdad_result.py:47-59`) y no valida por su cuenta.
3. Se exige la **estructura completa** que el productor emite, con vocabularios cerrados y representación canónica de artefactos; un payload reducido se rechaza **aunque su hash sea correcto**.
4. El verificador **devuelve causas**, no excepciones, para que el consumidor informe `unknown` con diagnóstico en lugar de abortar.
5. Certifica **correspondencia estructural**, no autenticidad del autor ni aprobación.

## Alternativas rechazadas

- **Reimplementar la validación en cada consumidor:** dos definiciones de la misma identidad, condenadas a divergir.
- **Validación laxa (hash + pocos campos):** acepta lo que el productor no emite; es el defecto de B-1.
- **Endurecer sólo el productor:** no cubre un estado escrito o editado fuera de él ni da una respuesta graduada.
- **Módulo de verificación neutral nuevo:** tercera pieza que también puede divergir, sin el contexto de la identidad.

## Consecuencias

**Positivas.** Una decisión, un lector; cualquier cambio de identidad alcanza a todos los consumidores. El consumidor distingue «no hay decisión» de «fuente ilegible o ambigua» y dice `unknown` en vez de abortar (B-2). Un payload fabricado no habilita una publicación.

**Negativas / límites.** Acopla continuidad a paquetes (deben instalarse juntos, como ya ocurre con `cdad_result`). El verificador es estructural: no prueba autoría. Los registros históricos sin payload verificable no habilitan recuperación y no se migran. Un cambio futuro del payload obliga a actualizar el verificador antes de que las decisiones nuevas sean consumibles: visible y preferible a una aceptación silenciosa.

## Cumplimiento

`tests/test_007_002_dispatch_recovery.py` (18 casos) cubre la aceptación de la estructura completa, el rechazo de variantes con hash recalculado, la degradación a `unknown` de una fuente ilegible y la paridad de selección entre `reconcile` y `prepare --replace-packet`.
