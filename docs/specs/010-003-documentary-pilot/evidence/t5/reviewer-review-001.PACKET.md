---cdad-packet-json
{"contract":{"commit":null,"kind":"approved-feature-spec","path":"docs/specs/010-003-documentary-pilot/spec.md","sha256":"f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5"},"execution":{"authority_ref":"docs/epics/epic-010-documentary-specialization/execution.md","epic_id":"epic-010-documentary-specialization","feature_id":"010-003-documentary-pilot","id":"exec-010-003-documentary-pilot-001","model_policy":"ordinary","policy_sha256":"f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711","scope":"epic-010-documentary-specialization"},"execution_context":".cdad/executions/exec-010-003-documentary-pilot-001/execution.json","execution_id":"exec-010-003-documentary-pilot-001","feature_id":"010-003-documentary-pilot","instruction_sources":[{"path":"common.md","sha256":"37609c566bf8f827a082699745b4cc0e915e37421a34d65f98b29db179647110"},{"path":"roles/reviewer.md","sha256":"73e9a8f4d049a49788d23f4064765d21f9677a44085dc2ab364e9a73b047cb92"},{"path":"substages/reviewer-review.md","sha256":"b914cfd63bcec89ef5ba2b2edf36993c12e3a280e0eba833212b57b6836efc06"}],"packet_id":"010-003-documentary-pilot-reviewer-review-001","packet_version":1,"path_policy":{"documentation_files":["README.md"],"documentation_roots":["docs"],"implementation_files":["install.sh"],"implementation_roots":["agents","skills","scripts","sources","build"],"private_paths":["tests/.sensitive-patterns.local"],"test_roots":["tests"]},"policy":{"path":"docs/cdad-policy.json","schema_version":1,"sha256":"f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711","snapshot":"ewogICJwYXRoX3BvbGljeSI6IHsKICAgICJkb2N1bWVudGF0aW9uX3Jvb3RzIjogWwogICAgICAiZG9jcyIKICAgIF0sCiAgICAiaW1wbGVtZW50YXRpb25fZmlsZXMiOiBbCiAgICAgICJpbnN0YWxsLnNoIgogICAgXSwKICAgICJpbXBsZW1lbnRhdGlvbl9yb290cyI6IFsKICAgICAgImFnZW50cyIsCiAgICAgICJza2lsbHMiLAogICAgICAic2NyaXB0cyIsCiAgICAgICJzb3VyY2VzIiwKICAgICAgImJ1aWxkIgogICAgXSwKICAgICJ0ZXN0X3Jvb3RzIjogWwogICAgICAidGVzdHMiCiAgICBdLAogICAgInByaXZhdGVfcGF0aHMiOiBbCiAgICAgICJ0ZXN0cy8uc2Vuc2l0aXZlLXBhdHRlcm5zLmxvY2FsIgogICAgXSwKICAgICJkb2N1bWVudGF0aW9uX2ZpbGVzIjogWwogICAgICAiUkVBRE1FLm1kIgogICAgXQogIH0sCiAgInNjaGVtYV92ZXJzaW9uIjogMSwKICAidGVtcG9yYXJ5X3Jvb3RzIjogW10KfQo="},"read_scope":[{"class":"contract","path":"docs/specs/010-003-documentary-pilot/spec.md"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/sources"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/challenge"},{"class":"implementation","root":"skills/cdad-cycle/references"}],"role":"reviewer","substage":"review","write_scope":[]}
---end-cdad-packet-json
# CDAD task

<!-- cdad-instructions:start -->
You are executing one isolated CDAD role task. Follow the approved contract, the declared scopes, and the stated invariants. Read only declared inputs and scope; edit only declared write scope. Preserve session separation, gates, approvals, and evidence requirements. The configured and reported models are observations; model policy never broadens permissions. Report modified files, exact commands, outputs, and commit evidence. If the contract or test conflicts with the request, stop and report the mismatch. Do not load the full cycle instructions: this packet is the execution contract.

Full-suite policy (declared once, here in the common part): the complete suite is not run unless the packet explicitly asks for it, and the one who closes the task runs it — the closer runs the full suite once, at closure. Every role and subphase instruction references this policy and never restates it.

Act as reviewer. Work read-only and assess the object the contract declares, with its declared form (spec or plan): the complete diff against the approved contract for approved contracts, and the specification object for `draft-plan`. Give every finding a verdict, confidence bucket, grounded rationale, and exact location. Abstain when evidence is insufficient.
Design criterion: judge a design by its real consequences, and keep its limit — the absence of an abstraction is not, by itself, a defect; the principle and its limit live in `skills/cdad-cycle/references/design-principles.md` (the canonical owner), and the duty over the table of current decisions lives in `references/stage-4-review.md` (its canonical owner).
Documentary duty: in an independent read-only session, set the documentary product against its contract and its sources, and record findings, limits and abstentions; structure is not proof of fidelity. The shared norm lives in `skills/cdad-cycle/references/documentary-contracts.md` (read it, never restate it).
Documentary engagements keep the role boundaries and the separation of responsibilities as they are; no documentary variant, selector or agent is created.

Review correctness, readability, architecture, security, performance, and contract compliance. Separate blocking findings, optional improvements, and abstentions; never soften a blocking observable defect.

<!-- cdad-instructions:end -->

## Objective
EnsayO semantico independiente del desafio de 010-003-documentary-pilot (T5, reviewer/review). Revisas UN SOLO OBJETO: el candidato negativo `tests/fixtures/010_003_documentary_pilot/challenge/negative.md`, contrastado contra el contrato aprobado, el inventario `inventory-010-003-v1` y las dos fuentes autorizadas. Entregas tu primer informe y ese informe queda cerrado: no habra una segunda oportunidad de "encontrar" lo que falte.

OBJETO Y PRECEDENCIA (decision de la autoridad, registrada en plan-review-2-resolutions-2026-10-31.md, BN-1): el objeto revisado es SOLO el candidato frente al contrato, el inventario y las fuentes. El diff de la unidad y cualquier operacion git que muestre contenido (`git show`, `git log -p`, `git diff`) quedan FUERA del objeto y del alcance. Esta declaracion especifica prevalece sobre la frase generica del bloque de reviewer sobre "the complete diff against the approved contract"; no modifica los bloques de instrucciones ni concede lecturas adicionales.

QUE DEBES HACER, con evidencia localizable (ruta y ancla de la fuente):
1. Contrastar CADA afirmacion del candidato con el corpus inventariado y decir, para cada una, si esta respaldada, no respaldada, o respaldada por una referencia que no sostiene lo afirmado.
2. Identificar y fundamentar las tres clases de defecto que el contrato compromete (PC-02): una afirmacion presentada como hecho sin respaldo en el corpus; una contradiccion omitida entre dos fuentes que sostienen posiciones incompatibles; y una referencia que existe y resuelve pero no sostiene lo afirmado. Para cada una: ubicacion en el candidato (seccion y oracion), fundamento contra el corpus (fuente y fragmento), y por que el fragmento citado no alcanza cuando corresponda.
3. Distinguir lo que examinaste de lo que no: declara alcance y abstenciones. No conviertas la ausencia de respaldo en falsedad universal.
4. Si no encuentras una de las tres clases, dilo y fundamenta por que; no inventes un hallazgo para completar la lista.

LIMITES: no leas `product/`, `oracle/`, `structural/`, `discovery.md`, informes GREEN o de contraste, ni el plan ni los registros de preparacion: no son insumos y leerlos fuera del alcance clasifica la lectura segun la tabla de auditoria del contrato (las rutas reveladoras invalidan el ensayo). No leas el verificador. No ejecutes operaciones git que muestren contenido. No edites nada: eres read-only. Tus lecturas declaradas seran auditadas contra esas exclusiones; declarar una lectura no la autoriza. Las referencias normativas de metodo (`design-principles.md`, `stage-4-review.md`, `verdict-tuple.md`) se registran sin invalidar; `documentary-contracts.md` es la norma que el paquete manda leer. El selector mecanico de la raiz es mas amplio que esta autorizacion: no leas otras referencias.

FORMATO DEL INFORME (FINAL TEXT): un hallazgo por defecto con (a) ubicacion exacta en el candidato, (b) fundamento contra el corpus con fuente y ancla, (c) veredicto y confianza, (d) consecuencia; mas una seccion de alcance examinado, otra de abstenciones y una conclusion sobre si el candidato es conforme o no conforme al contrato. No reproduzcas la clave: no la tienes. No propongas la correccion; tu trabajo es encontrar y fundamentar, no corregir.

## Contract
- kind: approved-feature-spec
- path: docs/specs/010-003-documentary-pilot/spec.md
- sha256: f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5
- commit: null

## Task validation plan

- Task: T5
- focal_tests:
  - none declared (none affected)
- observable_checks:
  - Encargo reviewer/review en sesion independiente del productor y del autor de la clave: recibe solo contrato exacto, inventario, fuentes, candidato y lecturas normativas declaradas: documentary-contracts.md, design-principles.md, stage-4-review.md y verdict-tuple.md. Objective e invariants fijan solo challenge/negative.md como objeto y excluyen el diff de la unidad y operaciones git con contenido. La declaracion especifica prevalece sobre la frase generica del rol por decision BN-1; esa frase no impone otra lectura y cualquier otra imposicion incompatible se detiene y escala.
  - Validar paquete, destinatario y fijacion de T3: commit de preparacion con verificador citado por el request de T4 y antecesor del commit del producto; commit del registro anterior al despacho de T5 y ambos commits de preparacion y registro citados por su request; conservar sesion, despacho y snapshots. Recuperar en modo lectura la transcripcion del store de sesiones del runtime mediante la sesion identificada en el despacho; si no se recupera, no acreditar independencia.
  - Auditar las lecturas declaradas hasta el cierre segun O-10: product, oracle, structural, discovery.md, informes GREEN o de contraste y sus copias invalidan; el diff de la unidad y git show, git log -p o git diff con contenido invalidan; referencias normativas de metodo no reveladoras, incluidas design-principles.md, stage-4-review.md y verdict-tuple.md, se registran sin invalidar; cualquier otro documento no listado como insumo se registra y el auditor decide y funda si revela respuestas. Si revela, invalida; si no, no invalida por contaminacion. Invalida lo que revela respuestas, no lo que ensena a revisar; registrar no autoriza lecturas fuera de alcance.
  - El primer informe fundamenta los tres defectos con localizadores, alcance y abstenciones; se conserva original cerrado en challenge-review.md antes del contraste posterior con la clave en challenge-contrast.md. Versionar ambos informes en un commit descendiente del de preparacion; las fechas de git no prueban orden por si solas.
  - Sin FINAL TEXT por falla tecnica, registrar incidente y re-despacho declarado; un informe entregado sin un hallazgo no acredita deteccion y no se reintenta para encontrarlo, ni se sustituye por revision informada. Una contaminacion observada no se borra con un re-despacho.
- regressions:
  - none declared (none affected)
- integration_gate: PC-07..PC-09 acreditadas por una sesion real y los tres hallazgos fundamentados, transcripcion recuperable auditada segun O-10 sin lecturas invalidantes, informe original cerrado antes de revelar la correccion e informes versionados conforme a la fijacion requerida.
- Widen (ampliar) the validation when the change leaves the focal tests: a shared contract or an uncertain impact expands the validation to the declared regressions and the integration gate; a local correction uses the focal tests.
- Plan provenance: docs/specs/010-003-documentary-pilot/plan.md (sha256 49ce6f813aeb4e0bea0ff4f44d541a48deef29dc42f2af5aa6e05e5bf3352b04)

## Applicable contract

- Contract: docs/specs/010-003-documentary-pilot/spec.md (sha256 f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5)

## Inputs
- docs/specs/010-003-documentary-pilot/spec.md: approved contract
- docs/specs/010-003-documentary-pilot/spec.md: contrato aprobado v5 (PC-02, PC-07..PC-09, promesa C)
- tests/fixtures/010_003_documentary_pilot/sources/inventory.md: inventario inventory-010-003-v1 con digests, anclas y convencion de enlaces
- tests/fixtures/010_003_documentary_pilot/sources/s1.md: fuente autorizada s1
- tests/fixtures/010_003_documentary_pilot/sources/s2.md: fuente autorizada s2
- tests/fixtures/010_003_documentary_pilot/challenge/negative.md: candidato negativo bajo revision, declarado no conforme
- skills/cdad-cycle/references/documentary-contracts.md: norma documental (lectura normativa declarada)
- skills/cdad-cycle/references/design-principles.md: referencia de metodo (lectura registrada, no invalidante)
- skills/cdad-cycle/references/stage-4-review.md: referencia de metodo (lectura registrada, no invalidante)
- skills/cdad-cycle/references/verdict-tuple.md: referencia de metodo (lectura registrada, no invalidante)

## Read scope
[{"class":"contract","path":"docs/specs/010-003-documentary-pilot/spec.md"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/sources"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/challenge"},{"class":"implementation","root":"skills/cdad-cycle/references"}]

## Write scope
[]

## Invariants
- El objeto revisado es solo el candidato negativo frente al contrato, el inventario y las fuentes; el diff y las operaciones git que muestren contenido quedan fuera del objeto y del alcance, y esta declaracion prevalece sobre la frase generica del bloque de reviewer (BN-1).
- Leer product/, oracle/, structural/, discovery.md, informes reveladores o el verificador antes de cerrar el primer informe invalida el ensayo; declarar una lectura no la autoriza.

## Expected output
Role report with the required evidence

## Evidence required
- modified files
- exact commands
- command output
- commit
