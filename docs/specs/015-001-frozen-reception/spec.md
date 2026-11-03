---
feature_id: 015-001-frozen-reception
approved_by: Pablo (HITL delegada al orquestador, docs/epics/epic-015-dispatch-reception/execution.md)
approved_at: 2026-11-02
source: architect draft (sesión <ses-340>), materializado por el orquestador (ADR-003)
decision: se aprueban D1 (instruction_sources con snapshot base64, schema_version 1 ampliado) y D2 (históricos sin el campo conservan validación estricta; no se repara GREEN-002 ni paquetes históricos divergentes)
---

# Borrador de spec — 015-001-frozen-reception (architect, sesión <ses-340>)

**Estado:** aprobada (2026-11-02, HITL delegada; D1 y D2 aprobados expresamente).

## Discovery breve

Base: commit `34dce2c8d55b93d6d53f1a31c04d8beedd04a293`.
- `scripts/cdad_packet.py:10–11` y `scripts/cdad_result.py:10–11` son wrappers; la implementación está en `skills/cdad-cycle/scripts/`.
- Diferencia respecto del objetivo: actualmente `REQUEST.json` no contiene `instruction_sources`; su esquema cerrado tampoco admite ese campo (`cdad_packet.py:1779–1800`). Los hashes se calculan desde archivos vivos y se incluyen únicamente en el encabezado renderizado (`1995–2042`).
- `prepare --record-dispatch` verifica el paquete mediante ese render vivo (`4357–4361`, `2185–2197`). `receive` lo vuelve a hacer (`cdad_result.py:674–679`).
- El incidente está registrado en `docs/.cdad-state.json:31971–32004`: GREEN-002 modificó `common.md`; falló **record-dispatch** y terminó en `withdraw`. No acredita una recepción fallida posterior.
- 008-004 PC-03 exige integridad completa, no solo del encabezado; PC-06 mantiene la protección de referencias contract.

Conclusión: conservar hashes no basta; hace falta preservar también los bytes, con autoridad independiente del `PACKET.md` que se verifica.

## Spec propuesta

### 1. Descripción funcional
Los paquetes publicados por la nueva versión conservarán sus instrucciones exactas. Cambiar posteriormente las fuentes vivas no impedirá registrar su despacho ni recibir su entrega, siempre que sigan vigentes las demás precondiciones. La aceptación seguirá verificando el paquete completo. Congelar no permitirá aceptar un `PACKET.md` alterado.

### 2. Alcance
Dentro: publicación del respaldo congelado en preparación ordinaria y sucesores legítimos; validación y render determinista desde ese respaldo; registro de despacho y recepción con el mismo criterio; regresiones de consumidores. Fuera: diagnósticos de formatos cerrados, conflicto docs=docs, open-unit (015-002); reescribir contratos/paquetes/cierres históricos; cambiar aprobaciones, scopes, vigencia, continuidad o reemplazo; publicar o desplegar.

### 3. Contrato propuesto
**D1 — Congelar bytes por fuente en REQUEST.json** (extensión propuesta; no existe hoy): lista ordenada de fuentes canónicas (common, rol, subfase), cada entrada con exactamente `path`, `sha256`, `snapshot` (bytes originales en base64). La publicación obtiene los bytes una vez y calcula hashes; no acepta digests del llamador. El encabezado de PACKET.md conserva la proyección path+sha256 derivada del respaldo. El render reconstruye desde esos bytes sin consultar archivos vivos. Formato inválido/rutas discordantes/faltantes/duplicadas/digest incorrecto → rechazo, nunca fallback silencioso. Se mantienen validaciones existentes (UTF-8, límite del bloque estático). Se propone conservar `schema_version: 1` ampliando el conjunto cerrado de campos opcionales.
**D2 — Compatibilidad histórica explícita:** requests anteriores sin `instruction_sources` conservan validación estricta actual contra fuentes vivas. No se modifican ni se les atribuye respaldo retrospectivo. La garantía nueva aplica solo a publicaciones con respaldo. No se promete reparar GREEN-002 ni recibir paquetes históricos divergentes. Requiere aprobación expresa antes de RED.
**D3 — Un criterio compartido:** se conserva la comparación completa contra el render canónico, cambiando su origen para requests congelados. Sin recibos/registros/códigos nuevos. Los consumidores comparten la solución; sin excepción para GREEN, common.md o un incidente particular.

### 4. Postcondiciones
**PC-01:** preparación nueva publica REQUEST con fuentes, snapshots y hashes coherentes; stdout coincide con PACKET.md publicado. Sucesor legítimo captura sus propias instrucciones vigentes.
**PC-02:** tras preparar un paquete congelado, cambiar fuentes vivas no altera `render`; `validate-request` y `validate-packet` siguen aceptando.
**PC-03:** con esa deriva, `prepare --record-dispatch` registra y permite la transición a `dispatched`; `receive` conserva `packet_validation=passed` y alcanza la recepción, sin `withdraw`.
**PC-04:** alterar cuerpo/metadatos de PACKET.md respecto del request congelado impide registrar/recibir; incluye alterar instrucciones y solo actualizar hashes del encabezado. Respaldo inválido también se rechaza sin recurrir a fuentes vivas.
**PC-05:** request histórico sin el campo conserva comportamiento anterior; validarlo no añade snapshots ni modifica archivos.
**PC-06:** repetir recepción acreditada conserva precedencia del replay durable y devuelve el mismo recibo aunque cambien instrucciones vivas; no duplica registros. La congelación no valida un contrato alterado ni una referencia contract cubierta por write_scope.

### 5. Invariantes
Comparación completa sin normalizar texto alterado; REQUEST/contrato/verificadores fuera del producto editable de GREEN; sin cambios de permisos/aprobación/identidad/vigencia; publicación nueva usa su respaldo; sin promesa criptográfica si un actor sustituye todos los archivos de autoridad.

### 6. Superficie y aceptación
Producto: `skills/cdad-cycle/scripts/cdad_packet.py`, `skills/cdad-cycle/scripts/cdad_result.py` si aplica, tests bajo `tests/`. El paquete de implementación debe autorizar rutas canónicas bajo `skills/`; solo `scripts/` sería insuficiente. Aceptación: PC-01…PC-06 por CLIs públicos y oráculos independientes; RED con fallo conductual de deriva; regresión proporcional de preparación/render/recepción y 008-004; sin cambios en contratos cerrados; regeneración solo si cambian fuentes generadoras; suite completa al cierre del epic.

### 7. deferred-hardening
Migración de paquetes históricos sin snapshots; congelación de todos los insumos vivos; compatibilidad con cambios arbitrarios del ejecutable tras redespliegue; firmas externas/fuzzing/rendimiento; recepción tardía de unidades cerradas.

## Evidencia del architect
`validate-request` y `validate-packet` rc=0; render canónico 6718 bytes; contract sha256 `c14c8c4e77d4a87079bab20cbbfc7992f3af958a6a3b28080a8db791c4e9665f`; execution schema 2. Simulación en memoria: sin `instruction_sources` hoy; baseline render = publicado; con deriva simulada de common.md el render cambia (dependencia del renderer acreditada, no prueba end-to-end). Diff de producto vacío; solo `docs/.cdad-state.json` modificado. Sin archivos modificados, sin commit, sin tests.

**Pendiente bloqueante:** aprobación del borrador, especialmente D1 y el límite histórico D2.
