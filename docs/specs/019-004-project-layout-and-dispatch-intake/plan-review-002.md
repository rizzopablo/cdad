# Revisión independiente — borradores 019-004

**Dictamen:** no identifiqué hallazgos bloqueantes adicionales en los borradores revisados. Esto **no constituye aprobación** ni autoriza la implementación.

- Plan `draft-002`: SHA-256 `321a005f2aa0d27ea6100342b20637c509a4c47a753ab251241c8f55ce063833`
- Especificación `draft-002`: SHA-256 `29f7c39bf3972d8783503f5e9978635362b07f351428474cc68ad26399b21be1`

## Hallazgos

No se identificaron hallazgos nuevos con el umbral de confianza exigido.

Los cuatro bloqueos de la revisión anterior quedan **resueltos a nivel de definición del borrador**, sujetos a su implementación y verificación:

1. **Detección heredada:** se fijan los dos marcadores exactos, su precedencia y los casos ambiguos (`spec.md`, §4.2).
2. **Continuación:** se conserva la identidad designada y se exige contrastarla con el estado seleccionado y la política registrada, incluso si falta o cambia el locator (§4.5).
3. **Compatibilidad de política:** se exige una comprobación previa de clasificación y destinos; el conflicto no autoriza reescritura ni ampliación de permisos (§4.4).
4. **Route C:** se admiten preámbulo y texto final inertes, manteniendo los rechazos de duplicados, cuerpos inline y valores divergentes (§6.4). La compatibilidad histórica efectiva permanece pendiente de evidencia.

La reconciliación del índice de ADR sigue siendo un hallazgo **opcional y fuera del alcance** de esta feature; el borrador no decide el estado de esos ADR.

## Verificación y límites

Contrasté las estrategias declaradas para las promesas A–E con `stage-2-specification.md` § “Verification strategy per promise”. Su **cierre de producto aún no es verificable**: se revisaron documentos no aprobados, no una implementación ni sus resultados de aceptación.

- La identificación Route C coincidió con el render canónico; `validate-request` y `validate-packet` finalizaron sin salida ni error.
- `sha256sum` confirmó los digests indicados.
- `git rev-parse HEAD` devolvió `17a7283621d52a45f7488e5931448e5520fab0f1`.
- No ejecuté tests de producto ni la suite completa: el objeto era el borrador.
- No modifiqué archivos ni creé commits. El árbol ya mostraba cambios en el estado, los borradores y el archivo de procedencia.

Comandos principales, ejecutados desde la raíz del proyecto:

```sh
python3 scripts/cdad_packet.py validate-request --request "$p/REQUEST.json" --execution-context "$e"
python3 scripts/cdad_packet.py validate-packet --request "$p/REQUEST.json" --packet "$p/PACKET.md" --execution-context "$e"
python3 scripts/cdad_packet.py render --route C --request "$p/REQUEST.json" --execution-context "$e"
sha256sum docs/specs/019-004-project-layout-and-dispatch-intake/{spec.md,plan.md}
git status --short
git rev-parse HEAD
```

## Abstentions

- No acredito compatibilidad con una **representación histórica recibida de Route C**: el borrador exige recuperarla con procedencia o declarar la falta de evidencia, pero no se presentó tal representación en esta revisión.
- No acredito captura fiel de mensajes nativos por ningún runtime, ni funcionamiento, protección o ausencia de mutaciones de una implementación futura.