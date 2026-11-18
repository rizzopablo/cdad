Corregí el hallazgo 1 de la auditoría de regresión de 019-002, y el commit es `deda7786`. Todos los tests corridos pasan.

**Validación del paquete (ruta C):** `cdad_packet.py render --request` sobre `REQUEST.json` coincide byte a byte con `PACKET.md`. El sha256 del contrato coincide.

**Cambio:** en `sources/roles/orchestrator.md`, línea 157, `` `re-entry.md` `` pasó a `` `<skill-dir>/references/re-entry.md` ``. Corrí `make agents` para regenerar los agentes.

**Archivos modificados:**
- `sources/roles/orchestrator.md`
- `agents/cdad-orchestrator.md`
- `agents/claude-code/cdad-orchestrator.md`

**Comandos:**
- `make agents`
- `python3 -m pytest -q` sobre estos tests: `tests/test_004_001_t7_pd10.py`, `tests/test_019_002_discovery_delivery.py` y las ocho regresiones declaradas en el paquete.
- Resultado: 100 passed en 243.96 s.

**Commit:** `deda7786` incluye solo esos tres archivos. `docs/.cdad-state.json` aparecía modificado en el árbol y no lo incluí.

No edité tests ni toqué nada fuera del alcance de escritura. No corrí la suite completa, solo los tests focales y las regresiones declaradas; queda registrada como suite completa no realizada, porque es un fix local de una línea y la política no la exige durante el ciclo.