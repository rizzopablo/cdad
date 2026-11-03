# review.md — 015-001-frozen-reception (stage 4, reviewer)

**Sesión:** `<ses-339>` · **Packet:** `015-001-frozen-reception-reviewer-review-001` (route C re-despachado tras rechazo válido del primer despacho: el orquestador había armado el bloque a mano con un `packet_id` ajeno; el reviewer lo rechazó como INVALID PACKET y en el re-despacho verificó byte-identidad con el render canónico).
**Contrato:** spec sha256 `f0493229…fb63ce` verificado · **Diff:** `8c3c5625..c2183ee0` · **Modelo de la sesión:** deepseek-v4.1-flash vía opencode-go (observación).
Materializado por el orquestador (ADR-003).

**Veredicto:** no pasa tal cual. 2 bloqueantes; resto opcional/deuda/FYI.

## Verificación
- Intake route C verificado (validate-request/packet rc=0; render==PACKET.md 47 líneas; route C byte-idéntico; execution v2).
- 015-001 + packet_prepare: 27 passed. Falsificación base+tests HEAD: 9 failed/18 passed (D2 guarda verde).
- Mutantes: M1 muere (B1/B2/C1); M2 muere (C1+8 de 008-004); M3 sobrevive pero no observable (validate_request rechaza antes; borde receive--late diferido en §7); M6 (sucesor reusa bytes del predecesor) sobrevive 143 passed → F-2.
- Regresión proporcional 312 passed (7 lotes). TestRequestSchema: 3 failed → F-1.

## Hallazgos
1. **BLOQUEANTE (F-1)** — `skills/cdad-cycle/assets/packet-request.schema.json` sin `instruction_sources` (`additionalProperties:false`): el esquema publicado rechaza requests nuevos; `TestRequestSchema` (010-002 PC-10) 3 failed en HEAD, 3 passed en base. Regresión de este diff (R-13 006-004). Cierre: añadir la propiedad opcional con la forma exacta; TestRequestSchema → 3 passed (verificado en copia descartable por el reviewer).
2. **BLOQUEANTE (F-2)** — PC-01 «sucesor legítimo» solo verificada para `prepare`, no para `prepare --replace-packet` (`cdad_packet.py:3977-3980` hoy correcto, pero el mutante M6 sobrevive). Cierre: verificador A2b (publicar congelado → derivar common.md → forzar obsolescencia → replace-packet → snapshot(sucesor)==vivo derivado, !=predecesor). Alternativa: enmendar PC-01 (decisión del dueño — se rechaza: la promesa cubre sucesores legítimos).
3. Opcional (F-3) — helpers muertos `_forge_live_consistent`, `_drift_forge_common` en el test 015-001 (borrar o usar).
4. Opcional (F-4) — `.superseded.json`/ASSIGNMENT_UNIVERSE no traza `instruction_sources` como campo re-derivado.
5. FYI (F-5) — Memory Bank debe registrar D1/D2/D3 y el campo nuevo (etapa 5, scribe).

Contraste PC: PC-01 parcial (falta sucesor por reemplazo); PC-02/03/04/05/06 cubiertas y sensibles. D1 vs alternativas justificado (9,6 KB base64 < techo 12.000; sin sidecar/recibo nuevo). INV intactos. Sin ADR nuevo (respeta ADR-036/038/019).

Abstenciones: suite completa no realizada (312 tests proporcionales); HOME instalado no evaluado; `receive --late` con congelado no ejercitado e2e (spec §7); modelo del implementer no declarado (buckets en `h` por otros 3 observables).

## Decisión del orquestador (HITL delegada, 2026-11-02)
- F-1 + F-2: review-fix obligatorio. F-1 → implementer (esquema). F-2 → test-writer (A2b pasa en verde + mata M6).
- F-3: se incluye en el mismo test-writer (coste mínimo, mismo archivo). F-4: deuda. F-5: scribe.
- Sin segunda review independiente del fix (límite declarado, como en 014-001).
