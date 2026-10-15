# T4 RU-1 — el hook de Claude Code resuelve el clasificador desde HOME (orquestador, delegación HITL)

**Defecto de integración real** (encontrado en el recorrido de T4; los tests no lo veían porque
la raíz sintética no tiene `path-guard.sh` real). `path-guard.sh` busca el clasificador en
`${CDAD_PACKET_CLI:-$HOME/.claude/skills/cdad-cycle/scripts/cdad_packet.py}` (`path-guard.sh:134`).
Con una política de proyecto y la copia vieja en HOME, el guard sale con rc=2 y bloquea toda
escritura del rol. Es fail-closed, no fail-open como decía P5.

**Cierre:** la activación emite el hook como
`command: CDAD_PACKET_CLI=<A>/.claude/skills/cdad-cycle/scripts/cdad_packet.py <A>/.claude/cdad-scripts/path-guard.sh <rol>`.
Ningún `command:` emitido depende de `$HOME`. Va como review-fix RED → GREEN. El orquestador
lo verifica después en T4, pasando el JSON del hook por `bash -c` con la línea emitida: debe
bloquear `tests/` y permitir `scripts/`.

**Corrección de redacción:** el "fail-open" de P5 vale para el guard sin política o con un
script ausente (exit 127). Con política presente y clasificador inválido, el guard falla cerrado.
