# Discovery — 007-002-dispatch-recovery

Epic-007, fila 2. Fecha 2026-10-24. Base verificada por el architect (read-only) sobre el código canónico.

## Superficie y bloqueos

| Superficie | Evidencia | Qué impide hoy |
|---|---|---|
| Clasificación de reconciliación | `skills/cdad-cycle/scripts/cdad_continuity.py:965-991` | `_classify` considera autoridad, recibo, despacho y materialización; no la disposición. Con despacho sin recibo devuelve `dispatched-unknown` para siempre. |
| Obtención de señales | `cdad_continuity.py:1010-1017` | No consulta la decisión registrada en el estado. |
| Salida observable | `cdad_continuity.py:1022-1060` | Publica `repeat_effect=False` pero no una salida operativa hacia la disposición canónica. |
| Reemplazo de despacho | `cdad_packet.py:2590-2602` | `prepare --replace-packet` rechaza todo estado distinto de `prepared`: también el `failed` que deja la disposición. |
| Reemplazo sin deriva | `cdad_packet.py:2631-2639` | Exige obsolescencia por contrato, companion o política; un abandono con contrato intacto no la satisface. |
| Reconstrucción del encargo | `cdad_packet.py:2672-2733` | Ya conserva encargo y correcciones explícitas: no hace falta otro mecanismo. |
| Trazabilidad y publicación | `cdad_packet.py:2741-2774` | Ya existen validación, diff de campos, `.superseded.json` y publicación del sucesor. |

La disposición ya existe y funciona (`cdad_packet.py:6051-6100` valida pertenencia, despacho sin recibo y feature abierta; `6470-6477` registra `resolution`/`replaced_by`; `6513-6529` marca `failed`). **Faltan consumidores coherentes de esa decisión**, no el mecanismo.

## Decisiones del orquestador (HITL delegada, 2026-10-24)

1. **«Resuelto» = sólo disposición**, no paquetes con recibo o completados. Repetir trabajo ya recibido exige distinguir reparación de duplicación de efectos; esa distinción no es de esta feature.
2. **Se extiende `prepare --replace-packet`** al paquete activo dispuesto, reutilizando `.superseded.json`, sin exigir deriva. El estado `failed` aislado no basta: la elegibilidad exige disposición canónica verificable.
3. **Nueva clasificación `disposed` en `reconcile`**, con precedencia posterior a autoridad expirada y a recibo ilegible/recibido, y **referencia verificable a la disposición**. Si la disposición declara `replaced_by` y ese sucesor ya existe, no se genera otro: el vínculo declarado se respeta.

## Invariantes

- Disposición única (`register-transition --transition disposition`); sin otro registro de intentos.
- Escritor único del estado; publicación por los mecanismos existentes.
- `reconcile` y `status` observan: no registran decisiones ni autorizan efectos.
- Disposición ≠ recibo ≠ aprobación ≠ terminación del worker.
- Sin despacho automático del sucesor ni reutilización del identificador anterior.
- Sin cambiar nombres, tipos ni significados de `situation`, `next.operation` y `authority.approval_reference` (007-001).
- Sin despliegue global, concurrencia ni integración de checkpoints (007-003).
