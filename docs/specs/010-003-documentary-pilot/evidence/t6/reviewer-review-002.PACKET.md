---cdad-packet-json
{"contract":{"commit":null,"kind":"approved-feature-spec","path":"docs/specs/010-003-documentary-pilot/spec.md","sha256":"f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5"},"execution":{"authority_ref":"docs/epics/epic-010-documentary-specialization/execution.md","epic_id":"epic-010-documentary-specialization","feature_id":"010-003-documentary-pilot","id":"exec-010-003-documentary-pilot-001","model_policy":"ordinary","policy_sha256":"f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711","scope":"epic-010-documentary-specialization"},"execution_context":".cdad/executions/exec-010-003-documentary-pilot-001/execution.json","execution_id":"exec-010-003-documentary-pilot-001","feature_id":"010-003-documentary-pilot","instruction_sources":[{"path":"common.md","sha256":"37609c566bf8f827a082699745b4cc0e915e37421a34d65f98b29db179647110"},{"path":"roles/reviewer.md","sha256":"73e9a8f4d049a49788d23f4064765d21f9677a44085dc2ab364e9a73b047cb92"},{"path":"substages/reviewer-review.md","sha256":"b914cfd63bcec89ef5ba2b2edf36993c12e3a280e0eba833212b57b6836efc06"}],"packet_id":"010-003-documentary-pilot-reviewer-review-002","packet_version":1,"path_policy":{"documentation_files":["README.md"],"documentation_roots":["docs"],"implementation_files":["install.sh"],"implementation_roots":["agents","skills","scripts","sources","build"],"private_paths":["tests/.sensitive-patterns.local"],"test_roots":["tests"]},"policy":{"path":"docs/cdad-policy.json","schema_version":1,"sha256":"f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711","snapshot":"ewogICJwYXRoX3BvbGljeSI6IHsKICAgICJkb2N1bWVudGF0aW9uX3Jvb3RzIjogWwogICAgICAiZG9jcyIKICAgIF0sCiAgICAiaW1wbGVtZW50YXRpb25fZmlsZXMiOiBbCiAgICAgICJpbnN0YWxsLnNoIgogICAgXSwKICAgICJpbXBsZW1lbnRhdGlvbl9yb290cyI6IFsKICAgICAgImFnZW50cyIsCiAgICAgICJza2lsbHMiLAogICAgICAic2NyaXB0cyIsCiAgICAgICJzb3VyY2VzIiwKICAgICAgImJ1aWxkIgogICAgXSwKICAgICJ0ZXN0X3Jvb3RzIjogWwogICAgICAidGVzdHMiCiAgICBdLAogICAgInByaXZhdGVfcGF0aHMiOiBbCiAgICAgICJ0ZXN0cy8uc2Vuc2l0aXZlLXBhdHRlcm5zLmxvY2FsIgogICAgXSwKICAgICJkb2N1bWVudGF0aW9uX2ZpbGVzIjogWwogICAgICAiUkVBRE1FLm1kIgogICAgXQogIH0sCiAgInNjaGVtYV92ZXJzaW9uIjogMSwKICAidGVtcG9yYXJ5X3Jvb3RzIjogW10KfQo="},"read_scope":[{"class":"contract","path":"docs/specs/010-003-documentary-pilot/spec.md"},{"class":"contract","root":"docs/specs/010-003-documentary-pilot/product"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/challenge-contrast.md"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/preparation-record.md"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/sources"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/challenge"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/oracle"},{"class":"implementation","root":"skills/cdad-cycle/references"}],"role":"reviewer","substage":"review","write_scope":[]}
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
Revision del producto corregido de 010-003-documentary-pilot (T6, reviewer/review), en sesion distinta de la del ensayo T5 y del productor. Revisas el relevamiento `docs/specs/010-003-documentary-pilot/product/relevamiento.md` contra el contrato aprobado, el inventario `inventory-010-003-v1`, las dos fuentes autorizadas, el candidato negativo, la clave de contraste fijada y `challenge-contrast.md`. Es una revision independiente: el producto ya te es revelado, y aqui si puedes inspeccionar el diff real del commit del producto.

QUE DEBES HACER, con ubicacion exacta (ruta:linea) y evidencia:
1. Confirmar que el diff real corresponde al producto documental autorizado: identifica el commit del producto y comprueba que su diff toca SOLO `docs/specs/010-003-documentary-pilot/product/relevamiento.md` y ningun otro archivo. El commit del producto debe descender del commit de preparacion `cd2d57b32e43e138cd831a3a40b5dd8fa075a67a`; el registro de preparacion se versiono en `4c822805`. Verifica ambas cosas y dilo.
2. Contrastar TODAS las afirmaciones factuales del relevamiento contra las fuentes inventariadas: para cada afirmacion, si esta respaldada por el fragmento citado, si la cita resuelve a una fuente y ancla registradas, y si el fragmento citado sostiene realmente lo afirmado.
3. Revisar la correccion de los tres defectos conocidos usando candidato, clave y contraste posterior: (a) la afirmacion sin respaldo, (b) la contradiccion omitida entre `s1-f02` y `s2-f03`, (c) la referencia que existia y no sostenia lo afirmado. Para cada uno: esta corregido, como, y queda alguna traza del defecto.
4. Verificar la conservacion de ambas posiciones incompatibles sobre la aprobacion de casos limite, con sus localizadores, y que el producto no invente consenso ni elija una posicion sin decision acreditada. Verificar que los pendientes esten localizados y clasificados con informacion o decision faltante y responsable conocido o designacion pendiente (P-01 y los que encuentres).
5. Ejecutar el control estructural declarado: `python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py`, reportar la salida y el rc, y declarar expresamente sus limites: acredita resolubilidad estructural de citas, inventario y anclas; NO acredita fidelidad semantica ni que el documento sea correcto.
6. Emitir hallazgos con veredicto, confianza, fundamento y ubicacion exacta; alcance examinado; abstenciones. Si no hay hallazgos bloqueantes, decirlo; si los hay, nombrarlos con su condicion de cierre. No edites nada: eres read-only.

INVARIANTE DE CONFIDENCIALIDAD (O-15): `product-review.md` se fundamenta contra las fuentes, el inventario, el candidato y la clave, pero NO transcribe el contenido de la clave. Puedes citar la ubicacion de un defecto en el candidato y el fragmento de la fuente que lo demuestra; no copies ni parafrasees la clave linea por linea, porque este informe se entrega despues como insumo del encargo de correccion (T7) y no debe transportarla.

ALCANCE DE LECTURA: el producto, el contrato, el inventario, las dos fuentes, el candidato, la clave, `challenge-contrast.md` y el registro de preparacion. Puedes ejecutar git para inspeccionar el diff del producto. Queda FUERA de tu alcance `tests/fixtures/010_003_documentary_pilot/structural/`: no lo leas; las muestras estructurales se ejercitan ejecutando el control, no leyendolas. Tampoco leas implementacion ni otros documentos de la feature. `skills/cdad-cycle/references` es lectura normativa de metodo: el selector mecanico es mas amplio que esta autorizacion y no habilita otras referencias.

FORMATO: FINAL TEXT con (1) verificacion del diff y de la ascendencia, (2) tabla de afirmaciones contrastadas, (3) dictamen de los tres defectos, (4) conservacion de posiciones y pendientes, (5) control estructural ejecutado con salida y limites, (6) hallazgos con veredicto/confianza/ubicacion, (7) alcance y abstenciones, (8) recomendacion.

## Contract
- kind: approved-feature-spec
- path: docs/specs/010-003-documentary-pilot/spec.md
- sha256: f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5
- commit: null

## Task validation plan

- Task: T6
- focal_tests:
  - python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
- observable_checks:
  - Otro encargo reviewer/review, en sesion distinta de T5 y posterior a su primer informe cerrado: examina producto, contrato, inventario, fuentes, candidato, clave y challenge-contrast.md; no edita producto.
  - Contrastar todas las afirmaciones factuales, la correccion de los tres defectos conocidos, ambas posiciones incompatibles y la clasificacion de pendientes contra PC-10..PC-13.
  - Ejecutar el control estructural y declarar sus limites; comprobar el diff autorizado.
  - El orquestador materializa product-review.md desde un resultado review, conservando hallazgos, alcance y abstenciones para T7.
- regressions:
  - none declared (none affected)
- integration_gate: Revision independiente del producto recuperable y completa respecto del alcance comprometido; hallazgos identificados para correccion y re-verificacion.
- Widen (ampliar) the validation when the change leaves the focal tests: a shared contract or an uncertain impact expands the validation to the declared regressions and the integration gate; a local correction uses the focal tests.
- Plan provenance: docs/specs/010-003-documentary-pilot/plan.md (sha256 49ce6f813aeb4e0bea0ff4f44d541a48deef29dc42f2af5aa6e05e5bf3352b04)

## Applicable contract

- Contract: docs/specs/010-003-documentary-pilot/spec.md (sha256 f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5)

## Inputs
- docs/specs/010-003-documentary-pilot/spec.md: approved contract
- docs/specs/010-003-documentary-pilot/spec.md: contrato aprobado v5 (PC-10..PC-13, promesa D)
- tests/fixtures/010_003_documentary_pilot/sources/inventory.md: inventario inventory-010-003-v1 con digests, anclas y convencion
- tests/fixtures/010_003_documentary_pilot/sources/s1.md: fuente autorizada s1
- tests/fixtures/010_003_documentary_pilot/sources/s2.md: fuente autorizada s2
- tests/fixtures/010_003_documentary_pilot/challenge/negative.md: candidato negativo que el producto corrige
- tests/fixtures/010_003_documentary_pilot/oracle/contrast-key.md: clave de contraste fijada (protegida: no transcribir)
- docs/specs/010-003-documentary-pilot/product/relevamiento.md: producto corregido bajo revision
- docs/specs/010-003-documentary-pilot/challenge-contrast.md: contraste posterior del ensayo T5
- docs/specs/010-003-documentary-pilot/preparation-record.md: registro de preparacion: commit cd2d57b3, hashes e inspeccion
- skills/cdad-cycle/references/stage-4-review.md: referencia normativa de la revision

## Read scope
[{"class":"contract","path":"docs/specs/010-003-documentary-pilot/spec.md"},{"class":"contract","root":"docs/specs/010-003-documentary-pilot/product"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/challenge-contrast.md"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/preparation-record.md"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/sources"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/challenge"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/oracle"},{"class":"implementation","root":"skills/cdad-cycle/references"}]

## Write scope
[]

## Invariants
- El commit del producto debe descender del commit de preparacion cd2d57b32e43e138cd831a3a40b5dd8fa075a67a y el registro de preparacion se versiono en 4c822805; ambas citas se verifican.
- product-review.md no transcribe el contenido de la clave (O-15): cita ubicaciones en el candidato y fragmentos de las fuentes, nunca la clave linea por linea, porque viaja como insumo a T7.
- El control estructural se ejecuta con python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py y su limite declarado es que acredita resolubilidad estructural, no fidelidad semantica.

## Expected output
Role report with the required evidence

## Evidence required
- modified files
- exact commands
- command output
- commit
