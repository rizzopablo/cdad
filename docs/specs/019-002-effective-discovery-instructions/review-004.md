# Revisión focal de `00dff4a7`

**Resultado: persiste un hallazgo bloqueante en la entrega efectiva del contexto al reviewer cuando se revisan juntos un plan y su spec.** La corrección resuelve el caso de una spec como objeto principal, pero no toda la ruta de revisión declarada. No apruebo la feature.

## Hallazgo bloqueante

### El reviewer puede omitir el diálogo al revisar un plan con spec acompañante

**Required · Verdict: BLOCKING · Bucket: h**

**Ubicación:** `skills/cdad-cycle/packets/substages/reviewer-plan-review.md:3`; `skills/cdad-cycle/references/handoff-prompts.md:628–643`; `skills/cdad-cycle/references/stage-2-specification.md:59–68`.  
**Contrato:** PC-2 y PC-9, `docs/specs/019-002-effective-discovery-instructions/spec.md:45–49,115–117`.

La instrucción nueva exige leer el `Dialogue context` solo cuando la forma principal del contrato es `spec`. Sin embargo, el procedimiento también admite revisar **una spec y su plan juntos**: en ese caso la forma principal es `plan` y la spec viaja como acompañante.

Preparé independientemente un packet real con `--object-kind plan`, `--spec-path` y un input declarado como `Dialogue context`. La preparación y validación terminaron con **rc 0**. El packet contiene el input, pero su instrucción de lectura está condicionada a `form: spec`; tampoco exige bloquear si ese contexto falta o es ilegible para el caso de plan con spec acompañante.

**Consecuencia:** en una revisión conjunta legítima, el reviewer puede seguir el packet sin contrastar la spec acompañante con decisiones, correcciones o autoridad registradas en el diálogo. El mismo riesgo identificado en `review-003` permanece para esa ruta.

**Movimiento propuesto:** hacer que la obligación de declarar, leer y contrastar el contexto —y de informar como bloqueante su ausencia o inaccesibilidad— cubra toda revisión que incluya una spec, sea principal o acompañante. Conservar la revisión de un plan que realmente no incluye spec sin imponerle ese input.

**Cierre verificable:** preparar packets nuevos desde las fuentes candidatas para ambos casos: spec principal y plan con spec acompañante. Verificar en cada packet la instrucción efectiva de lectura y el tratamiento bloqueante de contexto ausente o ilegible; comprobar además que un plan sin spec ni contexto sigue siendo revisable sin ese requisito. La conducta efectiva de agentes permanece sujeta a las observaciones comprometidas en PC-11.

## Resultado del bloqueo anterior

Para **spec como objeto principal**, el arreglo está sustentado por la composición independiente de un packet nuevo:

- El `--input` citado aparece íntegro y la forma declarada es `spec`.
- El packet ordena leer el archivo completo, contrastarlo con el borrador y reportar como bloqueante su ausencia o inaccesibilidad.
- El digest de la fuente congelada en el packet coincide con el de la fuente candidata: `0d3c28ed9ff876f14336123ce828d228f77ee4284cd81a40dac86123f3f66193`. No se usó como evidencia una fuente instalada anterior.
- Al retirar el archivo de la fixture, `render` siguió terminando con rc 0 y conservó la instrucción de bloqueo. Esto verifica la **instrucción**, no una respuesta observada de un reviewer real ni un bloqueo automático del CLI.

El ejemplo documentado mantiene correctamente el argumento citado y explica que una spec principal requiere `--object-kind spec`. La corrección de la convención de supersesión quedó examinada en `review-003`; esta revisión focal no la reabre.

## Categorías de evidencia

- **PC-1–3: Failed / Missing.** La revisión conjunta conserva el defecto indicado; además falta la aplicación observada comprometida por PC-11.
- **PC-4: Missing.** No se observaron las rutas revisada, exenta y de exenciones ausentes o incompletas.
- **PC-5: Supported within declared limits.** La regresión focal pasó; acredita transporte y materialización, no fidelidad semántica.
- **PC-6: Missing.** Sigue pendiente el inventario de publicaciones candidatas y paquetes en vuelo afectados con sus versiones congeladas.
- **PC-7: Supported within declared limits.** Pasaron las pruebas focales de cierre y orientación; se conserva el límite contextual de la revisión anterior.
- **PC-8–10: Failed / Missing.** Persiste el defecto de entrega efectiva indicado; faltan evidencias completas de versiones consumidas y cobertura de entrega.
- **PC-11: Missing.** No se acreditaron J1–J7 ni C1–C5. La ausencia de estas observaciones impide acreditar la aceptación de la feature.

## Comprobaciones y límites

- **Intake ruta C:** `validate-request` y `validate-packet` terminaron con rc 0; la identificación renderizada coincidió con la recibida y `render | cmp PACKET.md` confirmó igualdad de bytes. El contexto de ejecución es v2.
- **Tests primero:** examiné los tests focales y ejecuté:

  ```bash
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q \
    tests/test_019_002_discovery_delivery.py \
    tests/test_019_002_resting_orientation.py \
    tests/test_006_006_w1_replace_draft_packet.py \
    tests/test_006_006_u2_review_procedure.py \
    tests/test_006_006_u3_review_route_and_gate.py
  ```

  **Resultado:** `30 passed in 19.10s`. No ejecuté la suite completa.

- **Composición independiente:** preparé en fixtures descartables un packet de spec y otro de plan con spec acompañante; ambos prepararon y validaron con rc 0. El primer intento de inspección de la fixture terminó con `KeyError: 'packet_id'`; corregí únicamente el script de inspección y repetí la comprobación.
- `git diff --check bc922c04..00dff4a7 -- skills sources agents scripts tests README.md CDAD_metodologia.md`: **rc 0**.
- Las 32 rutas ADR indexadas existen; no detecté contradicción con las decisiones gobernantes en este alcance focal.
- **Contrato examinado:** SHA-256 `5cca6fa6d0cde92cadab961c8218126a741432b575bc169df24c7901eef34eb0`.
- **Archivos modificados por esta revisión:** ninguno. **Commit de revisión:** ninguno. `git status --short` mostró únicamente la modificación preexistente de `docs/.cdad-state.json`.

## Abstentions

- No puedo acreditar el comportamiento de agentes reales, la fidelidad de transcripts ni las rutas PC-4 y PC-11 sin las observaciones y registros comprometidos.
- No verifiqué una instalación desplegada ni una revisión real del caso de archivo ilegible. Tampoco ejecuté la suite completa.