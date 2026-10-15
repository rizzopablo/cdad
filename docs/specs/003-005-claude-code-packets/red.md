# RED 003-005 (cdad-test-writer, Claude)

`tests/test_packet_prepare.py`: 15 métodos; `pytest` → 14 failed, 1 passed (barreras sin cambios, pasa a propósito).
Fallos por contrato: `invalid choice: 'prepare'` (P1–P5); agentes Claude Code sin marcador de paquete,
sin la regla de paquete inválido y sin skills de dominio en el camino de paquete; orquestadores y handoff sin `cdad_packet.py prepare` (P6).

Ambigüedades resueltas por el test-writer:
- "Conservan su hook" = las barreras (tools y modos de path-guard) no cambian; los roles sin hooks siguen sin hooks.
- `prepare` no valida el state previo (puede tener `execution: null`); valida el resultante.
- Un directorio `OUT/<id>-NNN` existente cuenta como ocupado.
- P5 usa el CLI instalado en `.claude/skills/cdad-cycle/scripts/`.

Fricción observada: el hook `test-writer-bash` instalado (versión del 2026-09-13) bloquea `python3 -m pytest`;
el test-writer tuvo que correr unittest.
