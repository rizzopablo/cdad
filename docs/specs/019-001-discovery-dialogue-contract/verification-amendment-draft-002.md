# Propuesta de replanteo — no aprobada

**Recomiendo intentar un test conductual sobre la respuesta de un lector, sin exigir una interfaz máquina al producto documental. Un informe manual de fallo, por sí solo, no habilita GREEN.**

No se ha ejecutado ese ensayo ni se acredita ahora un RED válido.

## 1. Qué admite el procedimiento vigente

La norma permite comprobar efectos observables por un consumidor externo, sin exigir un mecanismo específico de implementación (`skills/cdad-cycle/references/stage-3-tdd.md:7–11`). Esto permite proponer como observación **la decisión concreta que un lector obtiene de unas instrucciones**, no solamente su estructura.

Pero el gate exige también:

- un test bajo `tests/`, con ejecución y commit separados;
- un fallo por aserción contractual, no por ausencia de archivos;
- GREEN posterior a ese RED válido.

Lo establecen `stage-3-tdd.md:149–191` y `re-entry.md:290–302`. La expresión «AssertionError or equivalent» de re-entry no acredita una dispensa del resto de esas obligaciones.

Por tanto:

- **Evaluación manual con un hallazgo:** evidencia útil, pero insuficiente como RED autónomo.
- **Test ejecutable que contrasta una respuesta real con una expectativa contractual protegida:** alternativa defendible para evaluación independiente.
- **Test que solamente comprueba que un evaluador escribió “FAIL”:** no recomendado; automatizaría el registro de un juicio, sin comprobar la conducta observada.

La norma documental conserva además la separación entre control y revisión semántica, y no amplía permisos (`documentary-contracts.md:133–145,151–164,184–188`). ADR-040 tampoco establece una excepción al gate RED.

### Un segundo límite importante

Un fallo al leer instrucciones actuales **no demuestra automáticamente** un fallo del nuevo diseño documental. Son objetos distintos.

Antes del ensayo debe aprobarse qué comportamiento se compara: **la capacidad de determinar responsabilidades a partir de una base documental identificada**, primero con las instrucciones actuales y después con el diseño propuesto. No puede introducirse ese cambio de objeto silenciosamente al presentar el resultado.

Esto requiere una enmienda explícita de verificación y revisión independiente; no una dispensa metodológica.

## 2. Alternativa concreta: test sobre una decisión de lectura

### Objeto del ensayo

Una tarea acotada de comprensión de Promise A, PC-1 y PC-2:

> Ante una elección funcional todavía pendiente, determinar quién pregunta al dueño, quién investiga la incertidumbre técnica, cómo vuelve la respuesta al arquitecto y qué responsabilidades siguen prohibidas al orquestador.

El lector interpreta documentos. **No ejecuta el nuevo flujo, no recibe nuevas facultades y no activa instrucciones.** El recorrido real completo permanece en 019-002.

### Preparación independiente

El test-writer deriva exclusivamente de la especificación:

1. El caso de lectura.
2. Las decisiones esperadas y sus alternativas incorrectas.
3. El test ejecutable.
4. El formato mínimo de la respuesta observada.

Ese formato pertenece al **instrumento de prueba**, no al diseño documental. GREEN continúa produciendo prosa y ejemplos; no debe generar JSON, tablas normativas ni campos nuevos para satisfacerlo.

Una sesión independiente del reviewer realiza la lectura con alcance explícito. El test-writer no necesita leer el diseño para construir o corregir su oráculo. El orquestador coordina y materializa el informe de esa sesión; no redacta la respuesta ni decide por el lector.

### RED sobre instrucciones reales

El lector recibe:

- el caso protegido;
- las instrucciones actuales pertinentes, completas y con versiones identificadas;
- la petición de explicar qué actuación prescriben, con localizadores.

**No recibe la respuesta esperada ni una orden de equivocarse.** Las instrucciones examinadas se tratan como objeto de análisis, no como una autorización para operar.

Existe una base concreta para investigar el fallo: el handoff actual asigna al arquitecto ayudar al usuario mediante preguntas y espera de respuestas (`handoff-prompts.md:235–259`), mientras el contrato actual del orquestador exige delegar trabajo de rol (`sources/roles/orchestrator.md:128–147`). Esto acredita el problema documental que motiva el ensayo; **todavía no acredita una respuesta errónea observada**.

El test compara decisiones explícitas del lector, no palabras presentes en el documento. Un RED pertinente sería, por ejemplo:

> La respuesta real asignó al arquitecto la pregunta funcional directa al dueño; la expectativa aprobada exige mediación del orquestador.

La salida debe mostrar una aserción sobre esa diferencia. La explicación y sus citas permiten comprobar si el fallo es atribuible a las instrucciones o a un problema del ensayo.

Si el lector responde correctamente, el ensayo **no es RED**. No se repite hasta obtener el resultado deseado, ni se altera el caso retrospectivamente.

### Comprobación posterior del diseño

Tras un RED aceptado, GREEN escribe únicamente `operating-design/`.

Se repite la misma tarea de comprensión usando el diseño como propuesta documental, con el mismo oráculo y condiciones declaradas. El cambio de base examinada debe estar previsto desde la aprobación del procedimiento, no depender de una selección oportunista de resultados.

Una evidencia anterior no puede acreditar esta comprobación: el registro debe vincular la respuesta con los documentos efectivamente suministrados y sus versiones.

**No basta con cambiar un “FAIL” por “PASS”, incorporar una respuesta esperada al expediente o comprobar que el directorio ya existe.**

### Límites y condición de parada

Esta alternativa no necesita un parser semántico universal ni un servicio nuevo. Sí necesita concretar cómo se captura fielmente la respuesta y cómo el test consume esa observación.

**VERIFY:** el test-writer debe confirmar esa ejecución concreta, su independencia y su suficiencia contractual. Este informe no inventa una API de ejecución de lectores.

Si no puede construirla bajo las reglas existentes, GREEN continúa bloqueado. La salida siguiente sería una modificación metodológica expresamente autorizada, no una excepción local presentada como cumplimiento ordinario.

## 3. Enmienda propuesta a la especificación

El siguiente texto es **borrador para revisión y aprobación**, manteniendo PC-1–PC-12 y D1–D5.

### Functional description

Evaluate whether a reader can determine the responsibilities committed by Promise A from an identified documentary basis. Compare existing instructions with the proposed operating design without activating the latter.

### Promise A — Reader-verifiable responsibility assignment

**VA-1.** Before production, a protected reading task and executable verifier are derived from PC-1 and PC-2, without deriving the oracle from the produced design.

**VA-2.** RED requires a recoverable actual response to unmodified existing instructions and an executed contractual assertion identifying a concrete incorrect responsibility assignment. Missing documents, fabricated responses and defective calibration specimens do not establish RED.

**VA-3.** The approved procedure identifies in advance the baseline and candidate documentary bases and explains their relationship to the same observable reading task. A baseline failure alone does not establish candidate verification.

**VA-4.** Candidate verification applies the unchanged contractual oracle to a fresh response obtained from the identified design revision. It does not require a machine-readable product interface.

### Promise F — Evidence remains bounded

**VA-5.** Each observation identifies the supplied documents and versions, protected task, reader configuration, actual response, relevant locators, executed assertion and result. Missing or unattributable evidence is not a pass.

**VA-6.** Independent semantic review still examines PC-1–PC-12 against the admitted sources. The reading test does not establish universal comprehension, activated agent compliance or completion of the 019-002 journey.

### Invariants

- GREEN cannot modify the verifier, protected task, expected decisions or evidence records.
- No new role, gate, state field or product interface is introduced.
- Existing instruction powers remain effective until 019-002 activates their approved reconciliation.
- No fabricated baseline, concealed failed attempt or retrospective acceptance criterion is admitted.

### Acceptance

Before authorizing GREEN, an independent review must accept the procedure’s contractual relevance and baseline–candidate relationship, and the existing RED gate must receive the actual failing test evidence.

The Promise A test does not mark other promises verified or waive their applicable verification obligations.

### deferred-hardening

Existing deferrals remain unchanged. No committed fidelity behavior is deferred. Statistical comprehension claims and universal runtime certification remain outside this bounded assay.

## 4. ADR-040: reconciliar el índice, no esconder el hallazgo

El hallazgo sigue vigente:

- `docs/systemPatterns.md:5–41` se presenta como índice de decisiones vigentes y omite ADR-040.
- ADR-040 declara estado **Accepted** y alcanza los seis roles (`ADR-040…md:3–9`).
- Su apartado final conserva una frase incompatible con ese estado: «impiden proponerlo como Accepted hoy» (`:124–132`).

Propongo que el orquestador tramite su reconciliación documental mediante el mantenimiento existente del índice (`systemPatterns.md:93–104`), separado del producto `operating-design/`.

La resolución debe incorporar la decisión aplicable al índice y aclarar la redacción residual del ADR, o registrar una decisión autorizada distinta sobre su estado. **No corresponde que este arquitecto lo declare obsoleto o no aceptado.**

Su distribución a paquetes afectados debe utilizar `current_decisions` cuando corresponda, sin añadir mecanismos nuevos. El hallazgo no se cierra porque el diseño mencione ADR-040.

## 5. Secuencia y rutas de evidencia

Rutas propuestas; **no creadas por esta sesión**:

| Evidencia | Ruta |
|---|---|
| Procedimiento, caso y expectativas protegidas | `tests/019_001_documentary_verification/` |
| Test ejecutable de Promise A | `tests/test_019_001_discovery_dialogue_contract.py` |
| Revisión independiente del procedimiento | `docs/specs/019-001-discovery-dialogue-contract/verification-method-review-002.md` |
| Lectura basal, respuesta y ejecución RED | `docs/specs/019-001-discovery-dialogue-contract/reader-red-evidence.md` |
| Lectura del diseño y comprobación posterior | `docs/specs/019-001-discovery-dialogue-contract/reader-green-evidence.md` |
| Revisión semántica independiente | `docs/specs/019-001-discovery-dialogue-contract/semantic-review.md` |

Orden recomendado:

1. Revisar esta propuesta y aprobar o corregir la enmienda.
2. Encargar al test-writer la concreción del procedimiento y la actualización de su selección/auditoría.
3. Revisar independientemente el oráculo y la relación baseline–candidate.
4. Ejecutar y evaluar RED; **sin fallo contractual válido, no avanzar**.
5. Producir el diseño y comprobarlo.
6. Revisar semánticamente todas las promesas y solicitar aceptación.
7. Mantener en 019-002 la activación coherente, corrección idle/done y aceptación real completa.

Se conserva así el epic de dos unidades. No recomiendo fabricar una interfaz documental para facilitar tests ni ampliar ahora el epic a una reforma metodológica.

## 6. Evidencia de esta sesión

**Intake:** Route C validada, contexto v2 e identificación coincidente. Comparación completa de `PACKET.md` con el render: **idénticos**, 7.135 bytes, SHA-256:

```text
c15926d08bf921d281926ea86cb1fd1eda862f721ea1a854d1c44a884c2c41f1
```

**Revisión examinada:**

```text
3cfb6b6c63cdec98000c059544a7231e1605f63d
```

Comandos principales ejecutados desde la raíz declarada:

```sh
python3 scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-004/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-004/REQUEST.json --packet .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-004/PACKET.md

python3 scripts/cdad_packet.py render --project-root . --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-004/REQUEST.json --route C

python3 scripts/cdad_packet.py render --project-root . --request .cdad/packets/019-001-discovery-dialogue-contract-architect-draft-004/REQUEST.json

git status --short
git diff --stat
git diff --cached --stat
git rev-parse HEAD
```

Las validaciones finalizaron correctamente. Se contrastaron bytes y SHA-256 mediante Python 3.13.5, en memoria y sin temporales. Una consulta exploratoria a `validate --help` devolvió “invalid choice”; se utilizaron después los subcomandos existentes indicados arriba.

El estado inicial y final conservó los mismos cambios preexistentes:

```text
 M docs/.cdad-state.json
?? docs/epics/epic-019-discovery-dialogue/replan-2-begin.json
```

**Archivos modificados por este rol:** ninguno.  
**Commit creado:** ninguno.  
**Tests y ensayo de lectura:** no ejecutados.  
**Suite completa no realizada:** trabajo de arquitectura, no aceptación ni cierre.

**Resultado:** propuesta no aprobada para evaluar una vía de RED conductual; GREEN permanece bloqueado hasta acreditar su validez y ejecución.