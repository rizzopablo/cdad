# ADR-046 — El registro nativo no exige configuración de transporte; la superficie de observación pertenece al módulo de runtime

- **Estado:** Aceptado (aprobación del Memory Bank por el dueño el 2026-11-20).
- **Fecha:** 2026-11-20.
- **Decisor:** <owner> (aprobado el 2026-11-20).
- **Confianza:** Media — alta sobre la frontera de configuración; media sobre si la decisión merece estatus permanente de ADR o basta la spec.
- **Origen:** `docs/specs/native-record-without-external-config-2026-11-20/{spec.md,review.md}`; producto `5be4ff93`.

**Contexto.** La delegación nativa ya entrega el texto final: la entrega ocurrió y sólo falta registrarla. Sin embargo, `record` exigía la sección de runtime del archivo de configuración de transporte externo, de modo que una instalación por defecto podía ejecutar la delegación nativa y no poder registrarla (`rc=1`, configuración de runtime faltante). A la vez, la observación debe seguir motivada y acotada, y una identidad contradictoria no puede convertirse en evidencia faltante.

**Decisión.**

1. **La configuración de lanzamiento externo no es requisito para registrar una entrega ya ocurrida.** La carga de la sección es opcional únicamente en la ruta `record` nativa: archivo, mapa `runtimes` o sección ausentes equivalen a `{}`. El resto de las rutas mantiene su fallo cerrado con su diagnóstico existente.
2. **La ausencia se tolera; el error de configuración no.** JSON ilegible o inválido, sección presente pero no-objeto, claves prohibidas, y runtime ausente o inválido siguen rechazando sin registro durable ni staging. No se introduce validación de esquema más amplia.
3. **La disponibilidad de la observación la decide el módulo de runtime.** Con motivo (sesión declarada, padre declarado o payload nativo ausente), la entrada neutral invoca al módulo una sola vez con la sección disponible, incluso `{}`, y no condiciona por `sessions_db` ni por otra clave específica de módulo. Sin motivo, no se observa.
4. **Evidencia faltante se declara; la contradicción nunca se degrada.** Identidad no verificable se registra como `completed + staged` con sesión y modelo acreditados en null y provenance explícita; una identidad contradictoria evaluable sigue devolviendo `blocked + none + null` nombrando la clave, sin intento ni staging.
5. **Sin cambio de productores ni del protocolo externo.** Despacho externo/default, capacidades, migración, rechazo de opciones retiradas e instalador permanecen intactos; no se infiere ubicación de store ni se reescribe la identidad suministrada.

**Consecuencias.**

- *Positivas:* una instalación por defecto puede registrar la delegación nativa; la observación conserva su motivo y su cota; el rechazo por contradicción no se relaja.
- *Costos:* el cargador de sección tiene dos modos y la relajación debe permanecer acotada a la ruta nativa; el módulo deja de recibir la clave sintética `runtime` durante `--observe`.
- *Límites:* un documento de nivel superior o un mapa `runtimes` sintácticamente válido pero mal formado se trata como configuración ausente (F1, hardening diferido); la compatibilidad de módulos de terceros que dependían de la clave sintética queda sin verificar (F2); los fixtures establecen conducta de registro, no autenticidad de la captura nativa upstream.
- *Alcance:* esta decisión no acredita despliegue, publicación, recuperación de un cliente real ni compatibilidad de esquema en vivo.

**Alternativas consideradas.**

- **Exigir `runtimes.json` y pedir al usuario que lo configure:** rechazada; convierte un registro de algo ya ocurrido en una dependencia de transporte externo y contradice la promesa de reducción declarada.
- **Hacer opcional la carga en todas las rutas:** rechazada; relajaría el fallo cerrado del despacho externo, que sí necesita configuración de lanzamiento.
- **Inferir la ubicación del store cuando no está configurada:** rechazada; la promesa prohíbe inferir ubicaciones y copiar identidad suministrada.
- **Validar el esquema completo del mapa `runtimes`:** diferida (F1), fuera del límite elegido; se registra como deuda en lugar de ampliar el fix.
