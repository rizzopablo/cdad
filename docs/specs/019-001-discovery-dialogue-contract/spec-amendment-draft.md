## Borrador de enmienda — no aprobado

Propongo **tres cambios localizados** en `spec.md`. No reescriben las promesas ni modifican la metodología canónica.

**Criterio:** declarar una interfaz documental pequeña permite verificar su estructura sin inventar un lector conductual. La fidelidad sigue requiriendo revisión independiente. Reutilizo la forma completa del marcador existente, `<!-- cdad:pc PC-1 promise=A -->`, documentada en `contract-test-links.md:58–71`; no introduzco otro formato ni adopción automática del registro.

### 1. Insertar antes de `## Proposed design decisions`

```markdown
### Declared product interface — structural part of PC-12

The operating design has one required entry document:

`docs/specs/019-001-discovery-dialogue-contract/operating-design/README.md`

This is an externally inspectable navigation and evidence-location interface, not a prescribed implementation of the operating rules.

The entry document contains each of the following level-two headings exactly once, outside fenced code blocks:

- `## Promise A`: PC-1 and PC-2.
- `## Promise B`: PC-3 and PC-4.
- `## Promise C`: PC-5 and PC-6.
- `## Promise D`: PC-7.
- `## Promise E`: PC-8 and PC-9.
- `## Promise F`: PC-10, PC-11 and PC-12.

Each listed PC has exactly one standalone marker in its assigned promise section, outside fenced code blocks, using the existing marker form `<!-- cdad:pc PC-1 promise=A -->` with the corresponding PC identifier and promise letter.

Each marker introduces a content block ending at the next PC marker, level-two heading or end of file. Each block contains at least one nonblank prose line outside headings, HTML comments and fenced code blocks. That line may explain the treatment or point to supporting material within the product directory. Other headings, supporting files and organization remain free, provided they do not replace these required locations.

These checks establish only that the declared sections and nonempty PC locations exist and are correctly grouped. They do not establish that the prose is correct, sufficient, actionable or supported by its citations. Placeholder or incorrect prose cannot earn semantic acceptance merely by satisfying this interface.

The PC-12 location describes the closure-evidence arrangement; it does not allow the producer to issue its own independent review. Independent review reports remain outside the product directory.
```

### 2. Sustituir únicamente el párrafo de PC-12

```markdown
**PC-12.** The product exposes the declared structural interface under “Declared product interface — structural part of PC-12.” Structural verification rejects an absent or incomplete interface. Closure evidence for 019-001 separately records that structural result and independent semantic review of every committed postcondition against the admitted sources. Every PC has cited evidence and a verification result; the existence of its product locator is not evidence that its substantive promise has been met. Neither record replaces the other, and a structural pass alone cannot establish semantic acceptance.
```

### 3. Sustituir el último párrafo de `## Acceptance criteria`

Es el párrafo que comienza `The test-writer derives checks…`.

```markdown
The test-writer derives the structural verifier and protected fixtures from this approved specification and admitted inputs, without reading the produced design to construct or revise the oracle. The fixed expectations are the declared entry path, promise headings, PC-to-promise mapping, markers and nonempty content-block requirement. The verifier may inspect the candidate product when executed.

Structural RED must demonstrate an assertion failure against that interface when the product is absent or structurally incomplete. Absence of the required document is an unmet product-interface requirement, not an import, collection or fixture failure. The assertion identifies the missing or incomplete contractual structure; a directory-existence check alone is insufficient. A valid RED and its later GREEN use the same approved structural expectations. Neither result claims to distinguish correct from incorrect role assignments or to prove any other semantic obligation.

Independent semantic review remains required under `skills/cdad-cycle/references/documentary-contracts.md` section 6 and PC-12. The independent reviewer examines the product, its admitted sources and the meaning of its examples, recording recoverable evidence and a result for every PC. Structurally valid but incorrect, unsupported or incomplete content remains an acceptance failure. Semantic review never replaces RED, and structural RED/GREEN never replaces semantic review.

These are applications of the existing verification and review responsibilities, not a new gate, role, state or packet field. This amendment grants no construction permission. Before GREEN, the amendment requires independent review and explicit authorized approval, followed by a test-writer-produced structural RED accepted through the existing procedure. No RED, GREEN or semantic acceptance is accredited by this amendment itself.
```

## Fundamento y límites

- La separación entre producto y entradas protegidas ya existe (`spec.md:44–54`).
- PC-12 ya exige ambos registros (`spec.md:189`); faltaba concretar la interfaz estructural.
- El test-writer identificó precisamente esa carencia (`test-writer-role-report-002.md:3–4`).
- La norma admite una forma específica cuando pertenece a la promesa observable y conserva la revisión semántica independiente (`documentary-contracts.md:11–15, 133–145, 151–162`).

La propuesta no revive el ensayo de lector rechazado ni acredita su procedencia. Tampoco declara resueltos los demás hallazgos de `verification-amendment-review-002.md`.

## Evidencia de ejecución

- **Intake:** identificación Route C coincidente; contexto v2; contrato SHA-256 coincidente; `PACKET.md` idéntico byte a byte al render canónico completo.
- **Comandos:** `validate-request`, `validate-packet`, `render` y `render --route C`, mediante `python3 scripts/cdad_packet.py`, con las rutas del paquete recibido. Los comandos completos y el script de comparación están registrados en esta sesión.
- **Salida:** validaciones exitosas; comparación `BYTE-IDENTICAL`. La consulta preliminar a `validate --help` devolvió opción inexistente; se consultaron después los subcomandos correctos.
- **Revisión examinada:** `851841776c70709ba900468d16906db75dce5849`.
- **Archivos modificados por esta sesión:** ninguno. Persisten los cambios preexistentes en `docs/.cdad-state.json` y `docs/epics/epic-019-discovery-dialogue/amend-begin.json`.
- **Commit creado:** ninguno.
- **Tests:** no ejecutados; suite completa no realizada. Se entrega únicamente un borrador para revisión y aprobación.