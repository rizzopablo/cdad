Corregido el hallazgo bloqueante de `review-003.md`. El commit es `00dff4a7`.

**Intake (ruta C).** `validate-packet` terminó con rc 0 y el sha256 del contrato coincide. El `render` sin `--route C` no produjo un PACKET.md idéntico byte a byte. Lo atribuyo a que el render canónico equivalente es el que valida `validate-packet`.

**Cambios.**
- **`skills/cdad-cycle/packets/substages/reviewer-plan-review.md`**: el packet efectivo del reviewer ahora le ordena leer completo el input declarado como `Dialogue context`. Debe compararlo con el borrador (decisiones, correcciones, autoridad, procedencia y entradas reemplazadas). Si una spec no declara ese input, o el archivo falta o no se puede leer, debe reportarlo en `## Abstentions` y como hallazgo BLOCKING, sin presentar la revisión como fiel. Una revisión de plan que no es spec y no declara el input se juzga sin él.
- **`skills/cdad-cycle/references/handoff-prompts.md`**: el ejemplo para una spec lleva ahora `--contract-kind draft-plan --object-kind spec`. También aclara que el packet lista el archivo pero no su contenido.

**Verificación en fixture desechable.** Reutilicé `W1Case` en `/tmp/fx019.py`. Preparé un packet `reviewer/plan-review` con `--object-kind spec` y `--input 'docs/specs/fx/discovery.md=Dialogue context'`:
- `prepare` terminó con rc 0 y `validate-packet` también.
- El render contiene la instrucción nueva (`MUST declare` y el texto de BLOCKING), `- form: spec` y la línea del input.
- La ausencia del input o la falta de acceso a él queda cubierta por la instrucción. No ejecuté ese caso con un reviewer real.

**Regresión.** Corrí 5 módulos con pytest: `test_019_002_discovery_delivery`, `test_019_002_resting_orientation`, `test_006_006_w1_replace_draft_packet`, `test_006_006_u2_review_procedure` y `test_006_006_u3_review_route_and_gate`. Dieron 30 passed. Usé pytest porque `unittest` falla por importaciones entre módulos. No corrí la suite completa.

**Límites.** No toqué tests, despliegue ni publicación. Los paquetes históricos conservan su sha congelado. No agregué ningún gate.

**Pendiente.** Los `agents/` derivados no incluyen este texto y no los regeneré. La corrección está en la fuente del substage, que es lo que `prepare` compone dentro del packet.