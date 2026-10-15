# Review 2 — 003-005 (cdad-reviewer, Claude)

Veredicto: **APROBADO-COMENTARIOS**. 0 bloqueantes. B1, B2 y B3 resueltos en f6396f1; los probes se repitieron y la salida está pegada en el informe del reviewer:
B1 `File exists` con rc 2 y el directorio ajeno intacto; B2 `surrogates not allowed` con rc 2 y el state igual; B3 `feature_id must be a flat name` con rc 2 y nada creado fuera del proyecto.
`pytest tests/test_packet_prepare.py` 19 passed. Camino feliz: stdout == PACKET.md == render, validate-packet OK.

Opcionales: (aplicado) el rollback de out-dir usa `rmdir` (solo si está vacío) en vez de `rmtree`; (aplicado) comentario corregido;
(no aplicado) `mkdir(parents=True)` puede dejar directorios intermedios vacíos si falla; un `.cdad-state.json.tmp` preexistente de otro proceso se pisa.
