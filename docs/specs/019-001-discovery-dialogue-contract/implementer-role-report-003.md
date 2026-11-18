Commit `b0b7c8d9` corrige los dos hallazgos bloqueantes de review-002 en `operating-design/`. Las dos comprobaciones finales salieron limpias: no hay referencias colgantes a la cláusula de epic ni a líneas desplazadas de `activation-handoff-019-002.md`, y el README solo registra digests del spec, del discovery y del checklist, que no cambiaron.

## Validación de la ruta C (antes de tocar nada)

- `sha256sum` del spec: `1e50141c91b84a309be92d115c8df025a1fb5e138dc0ba35b2c13f74bd864853`, coincide con el contrato.
- `validate-request` y `validate-packet` (`skills/cdad-cycle/scripts/cdad_packet.py`): rc=0.
- `validate-state`: `VALID: execution=exec-019-001-discovery-dialogue-contract-001 feature=019-001-discovery-dialogue-contract model_policy=ordinary`, rc=0.
- `cmp PACKET.md` contra `render` completo: idénticos (8480 bytes).
- `render --route C`: coincide línea a línea con el bloque de identificación recibido.
- `scripts/cdad_packet.py` es un wrapper fino; la implementación canónica es `skills/cdad-cycle/scripts/cdad_packet.py`. Ambas dan el mismo render.

## Hallazgo 1 (review-002 §1): regla general de delegación por epic, eliminada

- `roles-and-dialogue.md:29`: se quitó la frase «una solicitud epic-level cuenta como solicitud para cada feature». Se mantiene «nunca se infiere de otra feature o etapa».
- `roles-and-dialogue.md:31`: el «For an epic, the scope is that epic» genérico se reformuló como término de la concesión concreta. La concesión de 019 (`execution.md:8-14`) se limita a ese epic y termina con cierre, cancelación o revocación.
- `roles-and-dialogue.md:36`: el párrafo de «epic-scope clause» se reemplazó por una frase: una concesión concreta se aplica como tal, dentro de sus términos registrados, y nunca se generaliza.
- `activation-map.md:21` y `:24`: se quitó «including its epic-scope rule» y el texto de la regla en la excepción (3).
- `activation-handoff-019-002.md:68` y `:71`: se eliminó la propuesta de añadir la regla de epic a `stage-2-specification.md` §2.3.
- `activation-handoff-019-002.md`: se eliminó la viñeta de regresión «epic-scope rule… covers each of its features» (antes en la línea 74).
- Criterio que tomé: el requisito que queda es que la aprobación cite y evalúe la autoridad registrada aplicable al caso. `verification.md:59` y `readiness-and-approval.md:66` citan la concesión concreta de 019 y sus límites, y no los toqué.

Cierre verificable del hallazgo: lo cumple `roles-and-dialogue.md:31` y `:36` (concesión concreta citada y evaluada, sin generalización).

## Hallazgo 2 (review-002 §2): materializar vs. escribir, uniforme

- Materializar sin alterar, en su propia sección: informe del arquitecto. Líneas: `roles-and-dialogue.md:68` y `:70`; `handoff-fidelity.md:30`, `:31` y `:126-127`; `activation-map.md:24` y `:59`; `activation-handoff-019-002.md:70` y `:71`.
- Escribir solo en Dialogue context: respuestas del propietario, correcciones y notas. Líneas: los mismos archivos anteriores.
- Regresión (`activation-handoff-019-002.md:73`): ahora verifica que el informe se materializa sin alterar en su sección y que las respuestas y notas van solo a Dialogue context. Ya no dice «the report body».
- «Not allowed» (`activation-handoff-019-002.md:74`): ajustado a la misma distinción.

## Residuos (greps en `operating-design/`)

- Términos prohibidos (`epic-level`, `epic-scope`, `epic-wide`, `covers each`, `report body`, `sub-section`, `appended`, `added later`): sin resultados.
- Referencias a §2.3: todas son citas del texto vigente de la excepción (`roles:16`, `:27`; `map:21`, `:24`, `:106`; `handoff-019-002:68`, `:71`, `:73`). Ninguna propone cambiar §2.3.
- `examples.md:41` («the orchestrator writes "owner agreed"») es un ejemplo de lo inadmisible, no una regla.

## Commit y alcance

- `git diff --stat`: 4 archivos, 19 inserciones, 20 eliminaciones (`activation-handoff-019-002.md`, `activation-map.md`, `handoff-fidelity.md`, `roles-and-dialogue.md`).
- Commit `b0b7c8d9`, prefijo `fix:`, limitado con `-- docs/specs/019-001-discovery-dialogue-contract/operating-design/`. No incluye `docs/.cdad-state.json` (modificado) ni `docs/epics/epic-019-discovery-dialogue/fix2-begin.json` (sin seguimiento). Ambos estaban antes y los dejé como estaban.
- No toqué spec, checklist, reportes de revisión, discovery ni nada fuera de `operating-design/`.

## Pruebas

No ejecuté pruebas automatizadas. `execution.md:16-28` (decisión del propietario) establece que una unidad solo documental no requiere RED/GREEN automatizado, y que la revisión semántica independiente es la verificación. La selección ejecutada fue validación del paquete y greps, y su límite es que no demuestra la coherencia semántica del texto.

## Nota para el revisor

review-002 marcó los hallazgos 2 y 3 de los cuatro anteriores como cierre parcial por estos dos defectos. Este cambio los corrige en el texto, pero el veredicto sobre ellos corresponde al reviewer, no a mí. Los archivos temporales de render están en `/tmp`, fuera del repo.