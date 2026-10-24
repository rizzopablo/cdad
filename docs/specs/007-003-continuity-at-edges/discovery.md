# Discovery — 007-003-continuity-at-edges

Epic-007, fila 3. Fecha 2026-10-24. Base verificada por el architect (read-only).

## (a) Dónde se espera continuidad y dónde se omite

- El orquestador exige `begin` antes del despacho y `checkpoint` al cerrar: `sources/roles/orchestrator.md:157-159`; la orientación prescribe validar → `begin` → transporte → registro (`references/orientation.md:189`).
- La omisión observada está documentada: continuidad atrasada tres días porque la ruta usada no registraba los bordes; `reconcile` lo detectó (`docs/epics/epic-006-opencode-concurrency/closure.md:38`).
- `cdad_dispatch.py record` observa y registra el intento, no escribe continuidad (`cdad_dispatch.py:963-1043`); el registro canónico publica observación y binding de estado, no continuidad (`cdad_packet.py:3259-3274`).
- **Registrar después del transporte no sustituye el `begin` previo**: integrarlo sólo en `record` dejaría abierto el fallo principal.
- El almacenamiento ya resuelve persistencia, encadenamiento e idempotencia (`cdad_continuity.py:633-689`).

## (b) Qué falta en recepción

- `receive` publica recibo durable con `semantic_status=pending`; no actualiza continuidad (`cdad_result.py:599-638`).
- Su repetición converge al mismo recibo (`cdad_result.py:542-548`).
- El protocolo común termina en validar recibo → materializar → registrar transición, sin cerrar continuidad (`references/re-entry.md:55-89`).
- La llegada externa puede traer recibo durable y saltarse `receive` (`re-entry.md:27-31,101-109`).
- **Cubrir sólo `receive` sería insuficiente**: hace falta un cierre común para las tres entradas y las transiciones aplicables, incluida la recuperación de una interrupción entre recibo/transición y checkpoint.

## (c) Evidencia vigente frente a invalidada

Piezas reutilizables: `goal`, `decisions` con fundamento, `uncertainties`, `next_action` (`cdad_continuity.py:496-540,557-581`); `references` con hashes y clases (`822-886`); cadena de checkpoints (`660-687`); disposición canónica de 007-002 (`1126-1152`).

**Brecha:** `unchanged` significa igualdad de bytes, no aplicabilidad de una prueba al producto reparado. Un log intacto puede haber perdido validez. Además, agregar `changes` o `evidence` al UPDATE no funciona hoy: el cuerpo canónico y la proyección seleccionan campos explícitos (`557-581`, `1337-1348`).

## Decisiones del orquestador (HITL delegada, 2026-10-24)

1. **Integración mecánica, no sólo protocolo.** La continuidad se exige en los bordes ejecutables: el transporte (nativo y externo) no procede sin un `begin` vigente para el paquete; el registro del intento verifica que exista y falla cerrado si no; la recepción cierra continuidad de forma idempotente, también para el recibo durable externo y para una interrupción entre recibo/transición y checkpoint. Repetir la instrucción existente no cierra el fallo observado.
2. **Evidencia con aplicabilidad explícita.** Se autoriza una extensión **aditiva** del contenido y de la proyección de los checkpoints existentes para declarar evidencia `vigente` o `invalidada` con motivo y referencia al antecedente. La reparación conserva el antecedente histórico y retira su acreditación vigente; un cambio de hash o un reanclaje no rehabilitan evidencia. `contract`/`living` sigue significando comportamiento ante deriva, no un segundo significado de validez. Sin almacenamiento ni registro de intentos nuevos.

## Invariantes

- Almacenamiento y encadenamiento existentes; sin nuevo registro de intentos.
- El orquestador sigue siendo el único escritor del estado; la continuidad no escribe `docs/.cdad-state.json`.
- La continuidad no acredita evidencia invalidada por una reparación.
- No se duplica la disposición (007-002) ni la vista (007-001).
- El cierre de continuidad no recibe, materializa ni aprueba.
