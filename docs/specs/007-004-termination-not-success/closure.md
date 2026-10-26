# Cierre 007-004-termination-not-success

Fecha: 2026-10-26. Epic: `epic-007-reliable-cycle-operation`. Colección: 6/7.

## Resultado

Terminar no acredita entregar. El sobre de delegación declara `delivery` (`none | staged | received`) con tabla cerrada de combinaciones y `delivery_ref` única; ni `rc` ni `termination` acreditan recepción, cierre de continuidad ni aprobación.

- Productores: `record` (staged / unknown / blocked), adaptador OpenCode (received, fail-closed), `delegate` y `dispatch` retransmiten los seis campos sin efectos.
- Ruta externa rechaza `completed+staged`; las contradicciones se diagnostican como `transport-error+none+null` sin normalizarse borrando la referencia.
- Compatibilidad histórica sólo por ausencia del campo, decidida por contexto y, en llegada externa, validada y vinculada con el localizador y el verificador del productor (`durable_receipt_path` + `validate_receipt`, importados).
- Dueños documentales: `cli-delegation.md` (forma) y `re-entry.md` (consumo); fuentes y adaptadores remiten; derivados regenerados byte a byte.
- 007-001 (orientación) y 007-003 (continuidad) intactas.

## Evidencia

- Contrato: `spec.md` (PC-01..PC-18), aprobada 2026-10-24.
- Tests: `tests/test_007_004_termination_not_success.py` (18 funciones parametrizadas, 69 casos).
- Review: 3 rondas (`ses_e8747b264ffev3rxxRyB0r1SNe`): ronda 1 NO APTO (3 bloqueantes + 1 menor) → ronda 2 (producto cerrado, B3 parcial) → ronda 3 APTO sin bloqueantes.
- Gate por superficie (`6c5e0da`): 507 passed, 2 failed (fixtures del contrato anterior, corregidos en `cdf66b3`).
- **Suite completa (orquestador): 1704 passed, 5 skipped, 1 failed** — `test_pd5_durable_signal_gates_completion_not_client_rc`, que **pasa aislado** (`8 passed`): es la contaminación entre tests ya declarada (`SUITE-CONTAMINATION`), no una regresión de esta feature.

## Ciclo

Primera aplicación real de suspender/reanudar: la unidad se suspendió el 2026-10-26T02:18 para trabajar 007-006 y se reanudó explícitamente a las 13:16, conservando identidad, binding y digests, sin re-despachar ni repetir recepción.

## Deudas declaradas

1. El relay explícito `completed+received` no revalida el recibo: la validación es del consumidor (límite declarado, §4.3/§6.2).
2. `delivery=none` y el `transport-error` de protocolo no prueban ausencia de efectos durables.
3. `SUITE-CONTAMINATION` sigue abierta (HOME/XDG); pendiente la auditoría de la suite por capacidad.
4. `SUSP-LOCK`, `SUSP-GUARD`, `SUSP-APPROVAL`, `SUSP-IDENTITY` y las heredadas (DT-8/F011, DT-9, sin CI).
