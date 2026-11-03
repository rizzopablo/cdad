# test-audit.md — 015-001-frozen-reception (AUDIT, TEXTO FINAL)

**Feature:** 015-001-frozen-reception · **Subfase:** AUDIT (test-writer, sesión <ses-341>)
**Contrato:** `docs/specs/015-001-frozen-reception/spec.md` (sha256 `f0493229…fb63ce` verificado) · **Packet:** `015-001-frozen-reception-test-writer-audit-001` (route C, execution v2 verificada)
**Método:** lectura de spec aprobada + barrido de verificadores de prepare/record-dispatch/render/receive e integridad; validate-request/packet rc=0; render byte-idéntico (7237 bytes); route C idéntica; regresión proporcional de `test_role_packet_review_regressions.py` (8 passed) y `test_role_packet_render.py` (17 passed). Sin lectura de implementación. Sin edición de tests.

**Regla de selección:** un verificador por promesa observable (A–D), no por PC ni por archivo.

**Vocabulario:** Mantener · Extender · Sustituir · Consolidar · Añadir · Retirar.

## 1. Disposiciones

- `tests/test_008_004_packet_enforcement.py` (18 tests): todos **Mantener**. Fijan rechazo de PACKET alterado en record/dispatch/receive, replay sin efectos, y el par estricto-nuevo/histórico (plantilla de D2). La variante congelada (instrucciones alteradas + hashes de encabezado actualizados) queda para Añ-C1.
- `tests/test_role_packet_render.py` (17 tests): todos **Mantener**. Fijan el render vivo = comportamiento histórico D2 y línea base determinista de PC-02; el cuarto P1 es el oráculo de composición byte-a-byte del que D1 deriva.
- `tests/test_role_packet_review_regressions.py` (8 tests): todos **Mantener** (CRLF, symlink, scopes, ruta C, installs).
- `tests/test_010_004_*` (t2 7, t3 6, t4 2, t5_e2e 2, t6 2, t5_properties 2, t6_b1 1): todos **Mantener**. Precedentes de PC-01 (sucesor declara), PC-04 (divergencia), PC-05 (histórico sin campo, sin atribución retrospectiva), PC-06 (replay).
- `tests/test_packet_prepare.py`: 14× **Mantener**, 1× **Extender** — `test_p1_prepare_writes_three_files_and_stdout_equals_packet_and_render` (dueño de la promesa A: extender con fuentes ordenadas, snapshots y hashes coherentes, stdout≡PACKET.md).
- `tests/test_005_003_t6_packet_contract.py` (7 tests): todos **Mantener**. Fijan que `instruction_sources` declara exactamente las tres fuentes canónicas (oráculo de composición de D1).

Sin Sustituir/Consolidar/Retirar. Ningún contrato cerrado se reescribe.

## 2. Mapeo promesa → verificadores RED (8 Añadir)

- **Añ-A1** (A/PC-01): prepare congelado publica REQUEST con fuentes ordenadas, claves exactas, `sha256==sha256(snapshot)`, snapshot≡vivo, proyección del encabezado derivada, stdout≡PACKET.md.
- **Añ-A2** (A/PC-01): el sucesor legítimo captura sus instrucciones vigentes (snapshots nuevos coherentes con lo vivo).
- **Añ-B1 ★** (B/PC-02, RED nuclear): tras preparar congelado, mutar las tres fuentes vivas → `render` byte-idéntico, validate-request/packet rc=0. Hoy falla (renderer lee fuentes vivas).
- **Añ-B2** (B/PC-03): con esa deriva → `record-dispatch` registra → `dispatched`; `receive` con `packet_validation=passed`, sin `withdraw`.
- **Añ-C1 ★** (C/PC-04): clases de alteración rechazadas en record y receive, incluido instrucciones alteradas con hashes de encabezado actualizados a lo alterado.
- **Añ-C2** (C/PC-04): respaldo inválido (base64 roto, digest discordante, ruta faltante/duplicada/discordante) se rechaza sin consultar fuentes vivas.
- **Añ-D1** (D/PC-05): request histórico sin el campo → validación estricta viva intacta, sin snapshots, sin modificar archivos.
- **Añ-D2** (D/PC-06): recepción acreditada repetida tras deriva → mismo recibo, replay durable, cero registros nuevos; contrato alterado y referencia cubierta por write_scope siguen rechazados.

E2E con deriva y propiedades con semilla pertenecen a sus subfases, no al RED.

deferred-hardening (§7 de la spec): migración histórica, congelación total de insumos, cambios arbitrarios del ejecutable, firmas/fuzzing/rendimiento, recepción tardía, campaña de propiedades, e2e instalado.

## 3. Evidencia
Archivos modificados: ninguno. Commit: ninguno. Suite completa no realizada (momento «durante el ciclo»: regresión proporcional de los dos archivos citados). sha256 de spec verificado.

## 4. Decisión del orquestador (HITL delegada, 2026-11-02)
Aprobadas las disposiciones (todo Mantener salvo la Extensión de `test_p1_prepare…`) y el mapeo RED (8 Añadir A1–D2). Sin ajuste: el RED nuclear B1 y el C1 falsifican el defecto comprometido.
