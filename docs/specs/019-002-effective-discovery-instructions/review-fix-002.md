Corregí los dos bloqueos de `review-002.md` y los dejé en el commit `166b481a`. T3 sigue sin observarse.

**Intake.** Ruta C. El `REQUEST.json` es válido y el render coincide byte a byte con `PACKET.md`. El contrato tiene el sha256 esperado.

**Archivos modificados** (no toqué tests, no desplegué):
- `skills/cdad-cycle/references/stage-2-specification.md`
- `skills/cdad-cycle/references/handoff-prompts.md`
- `sources/roles/orchestrator.md`
- `agents/cdad-orchestrator.md`
- `agents/claude-code/cdad-orchestrator.md`

**Bloqueo 1 (comando al reviewer).**
- El input ahora va como un único argumento entre comillas: `--input 'docs/specs/<feature>/discovery.md=Dialogue context'`.
- Lo cambié en la instrucción de `stage-2-specification.md`, que ahora avisa que sin comillas el shell lo parte en el espacio.
- Lo cambié en el texto de `handoff-prompts.md` y en el ejemplo completo de `prepare`, que antes no incluía `--input`.
- Verifiqué con un fixture desechable en `/tmp`, sin tocar el estado real. Armé el proyecto con el helper `PrepareProject` de los tests y ejecuté `prepare` con la forma entrecomillada. Terminó con rc 0 y el paquete lista `docs/specs/f1/discovery.md: Dialogue context`.
- Sin comillas, el CLI falla con `unrecognized arguments: context`.
- Revisé que el input aparece en el render del paquete. No comparé el contenido del archivo íntegro.

**Bloqueo 2 (convención de correcciones).**
- El registro es solo-append: ninguna entrada existente se edita ni se reescribe.
- Una corrección es una entrada nueva con `supersedes: <old-id>`.
- En el mismo append se añade al final del Dialogue context una línea `<old-id> superseded-by <new-id>` en un `Supersession index` (se crea con la primera corrección).
- Así el vínculo se recupera en ambos sentidos sin tocar la entrada anterior.
- Actualicé el mismo texto en la fuente del orchestrator y en sus dos consumidores generados.
- Regeneré con `scripts/cdad-generate.py` en `/tmp`, para ambos runtimes. El orchestrator generado es idéntico al de `agents/`.

**Pruebas.**
- `pytest` sobre los tests 019_002 de entrega y orientación, `test_cdad_generate`, `test_004_002_t7_l1_derived` y los tres 006_006 (reviewer, ruta de review, registro de exención): 63 passed en 54.6 s.
- `git diff --check` limpio.
- No corrí la suite completa. Queda como suite completa no realizada, ya que esta es una corrección focal de documentación y fuentes.

`docs/.cdad-state.json` sigue modificado desde antes y no lo incluí en el commit.