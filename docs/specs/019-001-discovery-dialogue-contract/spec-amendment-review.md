# Revisión del borrador de enmienda

**Objeto:** `docs/specs/019-001-discovery-dialogue-contract/spec-amendment-draft.md`  
**SHA-256:** `800ad0a92673d71c1f4138d206fc416c2e9a696328d0abdcee9ad8f8884db21b`

**Dictamen:** el borrador define una interfaz cuyo incumplimiento podría producir un RED estructural honesto, sin presentar ese resultado como prueba de fidelidad semántica. No revive el ensayo de lector cuestionado: cambia explícitamente el contrato del producto para hacer verificable una propiedad estructural.

Esa conclusión es **de diseño, no evidencia de un RED ejecutado**. Subsiste el hallazgo previo sobre ADR-040, que el borrador no resuelve. Esta revisión no aprueba la enmienda ni autoriza GREEN.

## Hallazgos bloqueantes

### ADR-040 sigue ausente del índice de decisiones vigentes

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

`docs/systemPatterns.md:5–9` declara la tabla como índice de las decisiones del proyecto, pero no incluye ADR-040. El encabezado de ese ADR lo declara **Accepted** y aplicable a los seis roles (`docs/adr/ADR-040-especializacion-documental-por-contrato-casa-unica-y-dos-registros.md:3–9`); su sección de confianza conserva, además, una afirmación incompatible sobre su adopción (`:124–132`).

La enmienda se apoya precisamente en la separación entre control estructural y revisión semántica, y reconoce que no resuelve los demás hallazgos anteriores (`spec-amendment-draft.md:61–63`). La desalineación puede dejar fuera de la distribución de decisiones una norma aplicable a quienes ejecuten esa separación.

**Cierre verificable:** que la autoridad competente reconcilie el estado y la redacción del ADR con el índice, o registre una decisión autorizada diferente, y compruebe la distribución aplicable mediante `current_decisions`. La corrección puede tramitarse separadamente de la redacción de esta enmienda.

## Hallazgos no bloqueantes

Ninguno con confianza suficiente para informar.

## Alcance del juicio

- La ruta, secciones, asignación PC–promesa, marcadores y requisito de contenido están fijados en el borrador (`:12–29`). Una aserción sobre la ausencia del documento o una estructura incompleta puede, por tanto, fallar sobre el **producto exigido**, no sobre instrucciones basales distintas.
- El borrador distingue expresamente estructura de suficiencia y corrección (`:31, 49–51`), mantiene la revisión independiente y no añade un rol, gate o campo (`:53`).
- Esto no demuestra todavía que un verificador concreto esté implementado, que su RED sea aceptable ni que el producto satisfaga PC-1–PC-12. Esas son evidencias posteriores.

## Abstentions

- No puedo acreditar un RED o GREEN: no se presentó ni ejecutó un verificador para esta interfaz.
- No evalué un producto `operating-design/` ni su fidelidad semántica.
- No determino si la autoridad del encargo alcanza para aprobar la enmienda; esa decisión corresponde al propietario u orquestador autorizado.

## Evidencia de la revisión

- **Intake:** Route C; `validate-packet` terminó con código de éxito y sin salida; el contexto declara versión 2. El render Route C mostró la identificación recibida.
- **Comandos principales:** `python3 ~/.agents/skills/cdad-cycle/scripts/cdad_packet.py validate-packet --project-root "$PWD" --execution-context .cdad/executions/exec-019-001-discovery-dialogue-contract-001/execution.json --request .cdad/packets/019-001-discovery-dialogue-contract-reviewer-plan-review-005/REQUEST.json --packet .cdad/packets/019-001-discovery-dialogue-contract-reviewer-plan-review-005/PACKET.md`; `render` con las mismas rutas y `--route C`; `sha256sum docs/specs/019-001-discovery-dialogue-contract/spec-amendment-draft.md`; lecturas con `cat`, `sed`, `nl` y `rg`; `git status --short`; `git rev-parse HEAD`.
- **Salida relevante:** el hash coincidió con el contrato; `HEAD` era `261080d7f5b2dbb92d6b10f941b0976a1e9bb551`.
- **Archivos modificados por esta revisión:** ninguno. Había cambios preexistentes en `docs/.cdad-state.json` y `docs/epics/epic-019-discovery-dialogue/amend-review-begin.json`.
- **Commit creado:** ninguno. **Tests:** no ejecutados; suite completa no realizada.