## Propuesta de enmienda — no aprobada

**Recomiendo verificación manual derivada del contrato, con revisión semántica independiente, sin introducir una interfaz máquina únicamente para conseguir un RED.** Esta opción necesita una decisión procedimental explícita en el gate existente; **no permite declarar retrospectivamente un RED válido ni avanzar ahora a GREEN**.

### 1. Diagnóstico fundamentado

La especificación compromete un diseño documental, no una API (`spec.md:129–133`). Permite controles automáticos estructurales, pero reserva la evaluación de fidelidad a revisión semántica independiente (`:249–260`).

El bloqueo comunicado es real:

- El primer test falló por ausencia del directorio, no por una asignación incorrecta de responsabilidades.
- Su comprobación de palabras podía aceptar instrucciones semánticamente equivocadas.
- El test-writer eliminó ese test y no acreditó otro RED (`test-writer-role-report-002.md:3–7`).
- La norma documental exige comunicar insuficiencia del contrato para construir el oráculo, no deducirlo del producto (`documentary-contracts.md:133–136`).

Existe además una incompatibilidad procedimental que no debemos ocultar: Stage 3 exige un test que falle por el comportamiento comprometido antes de GREEN (`stage-3-tdd.md:160–191`), y la selección aprobada establece expresamente que la revisión semántica no sustituye RED (`red-selection.md:10–14`).

Por tanto, **aprobar únicamente una rúbrica manual, dejando intacta esa selección, no resolvería el bloqueo**.

### 2. Alternativas y criterio

**A. Interfaz máquina contractual.**  
Podría especificarse un artefacto normativo consumible por herramientas: responsabilidades, prohibiciones y transiciones con significado definido, y verificación de sus valores y relaciones.

Consecuencias:

- Cambiaría la firma y los entregables actualmente aprobados.
- Necesitaría un consumidor y una utilidad observable justificados.
- Exigiría resolver cómo obtener un RED conductual real: una interfaz ausente tampoco acredita por sí sola ese RED.
- Seguiría necesitando revisión semántica para comprobar coherencia con la prosa, suficiencia y comprensión.

**No la recomiendo:** no hay evidencia de que un consumidor necesite esa interfaz. Añadir JSON para facilitar el test convertiría una decisión de verificación en un requisito de producto innecesario.

**B. Verificación manual contractual y protegida — recomendada.**  
El test-writer prepara el procedimiento sin leer el producto; el reviewer independiente lo aplica al producto y a sus fuentes. Los controles estructurales permanecen separados.

Conserva el producto y las promesas aprobadas. Su coste es hacer explícita una excepción acotada al requisito de RED automatizado, sin presentarla como cumplimiento ordinario de ese requisito.

**C. Mantener el bloqueo.**  
Si la autoridad competente no admite esa excepción, no procede GREEN. Se vuelve a diseñar una interfaz realmente necesaria o se reconsidera el encargo. No corresponde repetir búsquedas de palabras.

### 3. Texto propuesto para incorporar a la especificación

El siguiente bloque es **borrador para revisión independiente y reaprobación**. Conserva PC-1–PC-12, D1–D5, alcance y exclusiones.

> ### Verification method for this documentary engagement
>
> The normative product remains the operating design and its illustrative examples. No machine-readable product interface is required.
>
> Before production, the isolated test-writer derives a protected manual verification procedure and acceptance inputs exclusively from this approved specification and its admitted sources. These materials reside under the authorized `tests/` scope, outside the editable product. The test-writer does not read the produced design to construct or revise the oracle.
>
> The procedure specifies, for each observable promise:
>
> - the reader task and relevant postconditions;
> - admitted inputs;
> - the expected determination and unacceptable alternatives;
> - evidence to record;
> - conditions for pass, fail or inability to verify.
>
> The protected procedure covers:
>
> **Promise A — PC-1–PC-2:** determine who performs each committed action, follow the mediated question-and-answer round trip, and identify both the proposed permission changes and retained prohibitions. Incorrect role ownership or fictitious direct interaction fails.
>
> **Promise B — PC-3–PC-4:** reconstruct the current decision, its authority, the superseded understanding and the remaining question using only the durable inputs supplied by the worked example. Invented authority, inaccessible history or simultaneous treatment of superseded and current decisions fails.
>
> **Promise C — PC-5–PC-6:** determine the next action and readiness outcome for each distinct committed condition. Trace drafting through independent review and explicit approval. Invented consent or premature readiness fails.
>
> **Promise D — PC-7:** determine the applicable obligations for trivial normal-cycle and standalone lightweight work. Unjustified full-cycle ceremony or unearned normal-cycle accreditation fails.
>
> **Promise E — PC-8–PC-9:** contrast the ownership and consumer map with the cited repository sources. Verify actionable reconciliation of all four specified activation issues and their assignment to 019-002. Treating documentary design as activation fails.
>
> **Promise F — PC-10–PC-12:** examine the meaning of acceptable and unacceptable examples, and verify that the activation protocol requires both the real-agent journey and recoverable observed coverage of all five PC-11 cases. Illustrations, structural passes and declared limitations cannot substitute for those observations.
>
> Contract-derived correct and defective specimens may be used to check the procedure’s discrimination. Their results demonstrate sensitivity of the procedure only: they are not a RED against the actual product, product acceptance, or observed compliance with activated instructions.
>
> An independent reviewer audits the procedure-to-postcondition mapping before production and later applies the protected procedure to the identified product revision. The reviewer records actual determinations, supporting passages, contradictory evidence, findings and limits. Unrecoverable evidence or inability to determine a committed result blocks acceptance; it is not a pass.
>
> Structural verification records the checks actually executed, results and limitations separately. File presence, headings, labels, keywords and resolvable references do not establish semantic acceptance.
>
> Every PC-1–PC-12 requires a cited verification result before acceptance. No fixed scenario count is required, and one exercise may verify several postconditions.
>
> The complete observed real-agent acceptance exercise remains a delivery obligation of 019-002. Neither this manual verification nor its calibration specimens discharge that obligation.
>
> ### Procedural authorization required before production
>
> This verification method does not establish a valid automated RED. Production remains blocked until the competent authority expressly approves a bounded departure from that prerequisite for 019-001, records its authority and rationale, and supersedes the conflicting RED selection.
>
> The departure changes neither canonical CDAD instructions nor other engagements. It preserves isolated test-writing, protected acceptance inputs, independent review, explicit approval and verification of every committed promise. It creates no new role, state field or gate.
>
> If that authorization is unavailable, production remains blocked.
>
> ### deferred-hardening — clarification
>
> Existing deferrals remain unchanged. Semantic verification of PC-1–PC-12 is not deferred. Automated semantic certification is not claimed; its absence is an explicit verification limit, not permission to leave a committed promise unverified.

### 4. Secuencia y evidencia concretas

Después de revisar y aprobar la enmienda:

1. **Orchestrator:** registra la decisión procedimental y su autoridad; sustituye `red-selection.md`, conservando su historia. La delegación existente abarca decisiones sobre gates y evidencia dentro del epic (`execution.md:3–12`), pero este informe no ejerce esa autoridad.
2. **Test-writer aislado:** prepara, bajo `tests/`, el procedimiento y los inputs protegidos. Actualiza su auditoría, sin leer el producto.
3. **Reviewer aislado:** comprueba suficiencia, sensibilidad y trazabilidad del procedimiento. No confunde su calibración con RED del producto.
4. **Orchestrator:** verifica la autorización y las evidencias antes de habilitar producción.
5. **Implementer:** escribe exclusivamente `operating-design/`.
6. **Reviewer independiente:** aplica el procedimiento y contrasta producto, contrato y fuentes.
7. **Orchestrator:** materializa por separado controles estructurales, revisión semántica y decisión de aceptación.

Rutas propuestas — **todavía inexistentes y no autorizadas por este informe**:

- `tests/019_001_documentary_verification/`: procedimiento e inputs protegidos.
- `docs/specs/019-001-discovery-dialogue-contract/verification-method-review.md`: auditoría independiente.
- `docs/specs/019-001-discovery-dialogue-contract/structural-verification.md`: comprobaciones y límites.
- `docs/specs/019-001-discovery-dialogue-contract/semantic-review.md`: resultados por PC y localizadores del producto examinado.

La forma de esos registros no se convierte en una nueva interfaz del producto.

### 5. Evidencia de esta sesión

**Intake:** Route C validada; contexto v2; identificación coincidente; `PACKET.md` completo idéntico byte a byte al render canónico.

- Render: **7.062 bytes**
- SHA-256: `9e9d47201551c992df35cb07882f5bf117ef65e03540a070c14a36255d400183`
- Revisión examinada: `32f89bc3bc1ef78eb3077aebc5debf5ac5f87fc2`
- Especificación examinada: SHA-256 `80d26ba7826fe94c85329953014ff013281f843d2ddf1211e7c11675201f0539`
- Herramienta de cálculo: Python **3.13.5**, comparación de bytes y SHA-256, sin archivos temporales.

Comandos de validación ejecutados, desde la raíz del proyecto:

```sh
python3 ~/.agents/skills/cdad-cycle/scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-003/REQUEST.json

python3 ~/.agents/skills/cdad-cycle/scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-003/REQUEST.json --packet .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-003/PACKET.md

python3 ~/.agents/skills/cdad-cycle/scripts/cdad_packet.py render --project-root . --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-003/REQUEST.json --route C

git rev-parse HEAD
python3 --version
git show --stat --oneline fc029f67
git show --stat --oneline 309d8e8d
git status --short
git diff --stat
git diff --cached --stat
```

Las validaciones finalizaron correctamente. Los commits confirman la incorporación de 128 líneas y su posterior eliminación. El estado inicial y final mostró únicamente los cambios preexistentes:

```text
 M docs/.cdad-state.json
?? docs/epics/epic-019-discovery-dialogue/replan-begin.json
```

**Archivos modificados por este rol:** ninguno.  
**Commit creado:** ninguno.  
**Suite completa no realizada:** trabajo de arquitectura; no se ejecutaron tests ni se acredita aceptación.

**Siguiente decisión:** revisión independiente de esta enmienda y decisión explícita de la autoridad competente. Hasta entonces, GREEN permanece bloqueado.