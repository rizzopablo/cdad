---cdad-packet-json
{"contract":{"commit":null,"kind":"approved-feature-spec","path":"docs/specs/010-003-documentary-pilot/spec.md","sha256":"f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5"},"execution":{"authority_ref":"docs/epics/epic-010-documentary-specialization/execution.md","epic_id":"epic-010-documentary-specialization","feature_id":"010-003-documentary-pilot","id":"exec-010-003-documentary-pilot-001","model_policy":"ordinary","policy_sha256":"f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711","scope":"epic-010-documentary-specialization"},"execution_context":".cdad/executions/exec-010-003-documentary-pilot-001/execution.json","execution_id":"exec-010-003-documentary-pilot-001","feature_id":"010-003-documentary-pilot","instruction_sources":[{"path":"common.md","sha256":"37609c566bf8f827a082699745b4cc0e915e37421a34d65f98b29db179647110"},{"path":"roles/reviewer.md","sha256":"73e9a8f4d049a49788d23f4064765d21f9677a44085dc2ab364e9a73b047cb92"},{"path":"substages/reviewer-review.md","sha256":"b914cfd63bcec89ef5ba2b2edf36993c12e3a280e0eba833212b57b6836efc06"}],"packet_id":"010-003-documentary-pilot-reviewer-review-003","packet_version":1,"path_policy":{"documentation_files":["README.md"],"documentation_roots":["docs"],"implementation_files":["install.sh"],"implementation_roots":["agents","skills","scripts","sources","build"],"private_paths":["tests/.sensitive-patterns.local"],"test_roots":["tests"]},"policy":{"path":"docs/cdad-policy.json","schema_version":1,"sha256":"f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711","snapshot":"ewogICJwYXRoX3BvbGljeSI6IHsKICAgICJkb2N1bWVudGF0aW9uX3Jvb3RzIjogWwogICAgICAiZG9jcyIKICAgIF0sCiAgICAiaW1wbGVtZW50YXRpb25fZmlsZXMiOiBbCiAgICAgICJpbnN0YWxsLnNoIgogICAgXSwKICAgICJpbXBsZW1lbnRhdGlvbl9yb290cyI6IFsKICAgICAgImFnZW50cyIsCiAgICAgICJza2lsbHMiLAogICAgICAic2NyaXB0cyIsCiAgICAgICJzb3VyY2VzIiwKICAgICAgImJ1aWxkIgogICAgXSwKICAgICJ0ZXN0X3Jvb3RzIjogWwogICAgICAidGVzdHMiCiAgICBdLAogICAgInByaXZhdGVfcGF0aHMiOiBbCiAgICAgICJ0ZXN0cy8uc2Vuc2l0aXZlLXBhdHRlcm5zLmxvY2FsIgogICAgXSwKICAgICJkb2N1bWVudGF0aW9uX2ZpbGVzIjogWwogICAgICAiUkVBRE1FLm1kIgogICAgXQogIH0sCiAgInNjaGVtYV92ZXJzaW9uIjogMSwKICAidGVtcG9yYXJ5X3Jvb3RzIjogW10KfQo="},"read_scope":[{"class":"contract","path":"docs/specs/010-003-documentary-pilot/spec.md"},{"class":"contract","root":"docs/specs/010-003-documentary-pilot/product"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/product-review.md"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/tdd-t7-review-fix.md"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/challenge-contrast.md"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/sources"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/challenge"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/oracle"},{"class":"implementation","root":"skills/cdad-cycle/references"}],"role":"reviewer","substage":"review","write_scope":[]}
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
Re-verificacion del producto corregido de 010-003-documentary-pilot (T7, reviewer/review), en sesion distinta de T6 y de T5. Revisas TODO el diff del producto, no solo el hallazgo que lo motivo: el producto corregido en el commit 6596e804654f9b76d3e7710c2011b312350fe75d, que desciende del producto anterior 7fcca219e119ea72f29d68f406642afa5b2e1483. Emites dictamen final de revision del producto antes del cierre.

QUE DEBES VERIFICAR, con ubicacion (ruta:linea) y evidencia:
1. El diff: `git diff 7fcca219 6596e804 -- docs/specs/010-003-documentary-pilot/product/relevamiento.md`. Comprueba que toca SOLO ese archivo, que el commit desciende del anterior y que no hay cambios fuera del producto. Contrasta el diff con el informe del implementer (`tdd-t7-review-fix.md`): lo declarado coincide con lo efectivamente cambiado, sin cambios silenciosos.
2. Cierre de F-1 (el bloqueante de `product-review.md`): la seccion "Plazo de respuesta" ahora atribuye cada regla de inicio a su fuente, declara que el corpus no aclara si una solicitud completada se registra de nuevo y que el inicio exacto queda sin dirimir, sin elegir regla ni inventar conciliacion. Verifica que la declaracion sea verdadera contra el corpus: `s1-f01`, `s1-f03`, `s1-f05`, `s2-f04`. Si el texto afirma algo que el corpus no sostiene, es bloqueante.
3. P-02: existe, tiene todos los campos de PC-12 (informacion faltante, condicion de cierre, responsable conocido o designacion pendiente, clasificacion justificada) y su clasificacion no bloqueante esta justificada por el contrato. Verifica tambien que P-01 sigue completo y con su clasificacion.
4. O-1, O-2 y N-1 adoptados: la cita de contexto `s2-f01` en P-01 no extrae prelacion; la diferencia de organizacion del legajo queda declarada sin dirimir; las referencias por nombre de seccion son correctas y no rompen la trazabilidad.
5. NO REGRESION de lo ya aprobado: las tres correcciones de defectos (afirmacion sin respaldo eliminada, contradiccion `s1-f02`/`s2-f03` conservada con ambas posiciones, referencia del archivo apuntando a `s1-f04`), las nueve citas originales siguen resolviendo a fuente inventariada y ancla registrada, y la declaracion de documento sintetico se conserva. Usa la clave de contraste para confirmar que el diff no reintrodujo ninguno de los tres defectos, sin transcribirla en tu informe.
6. Todas las afirmaciones factuales del producto, incluidas las nuevas, siguen respaldadas por el fragmento citado. Si una cita nueva no sostiene lo que afirma, es bloqueante.
7. Ejecuta el control estructural `python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py` y las regresiones `python3 -B -m pytest -q tests/test_010_001_documentary_contracts.py tests/test_010_002_documentary_role_integration.py`; reporta salida y rc, y declara los limites del control (resolubilidad estructural, no fidelidad semantica).

ALCANCE DE LECTURA: producto, contrato, `product-review.md`, `tdd-t7-review-fix.md`, inventario, las dos fuentes, candidato, clave de contraste, `challenge-contrast.md` y la referencia normativa de revision. Puedes ejecutar git para el diff. Queda fuera `tests/fixtures/010_003_documentary_pilot/structural/` (se ejercita ejecutando el control, no leyendolo) y la implementacion del producto. `skills/cdad-cycle/references` es lectura normativa de metodo y el selector mecanico no autoriza otras referencias.

FORMATO: FINAL TEXT con (1) verificacion del diff y de la ascendencia sincera, (2) dictamen de F-1 con ubicaciones, (3) dictamen de P-01/P-02 y de O-1/O-2/N-1, (4) no regresion de los tres defectos y de las citas, (5) afirmaciones nuevas contrastadas, (6) comandos con salida y rc, (7) hallazgos con veredicto/confianza/ubicacion, (8) alcance y abstenciones, (9) recomendacion final: aprobado para cierre o bloqueantes con su condicion.

## Contract
- kind: approved-feature-spec
- path: docs/specs/010-003-documentary-pilot/spec.md
- sha256: f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5
- commit: null

## Task validation plan

- Task: T7
- focal_tests:
  - python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
- observable_checks:
  - Primer encargo implementer/review-fix: corregir hallazgos reales solo en product, repetir control estructural y regresiones y registrar version y diff. Su read_scope repite el de T4 corregido: contrato por ruta exacta de clase contract; inventario y fuentes por raiz tests/fixtures/010_003_documentary_pilot/sources/ y candidato por raiz tests/fixtures/010_003_documentary_pilot/challenge/, clase tests, restringidas a esos insumos; la ruta exacta de clase tests se rechaza. Normas por raiz skills/cdad-cycle/references, clase implementation, restringida a documentary-contracts.md y stage-3-tdd.md. Anade el informe de T6 product-review.md como lectura de clase contract y la raiz de lectura docs/specs/010-003-documentary-pilot/product/, clase contract, para incluir el producto declarado como insumo. No usa repository-read; excluye oracle, structural y el veredicto del reviewer sobre el desafio, challenge-review.md. El verificador no es input ni lectura: se ejecuta con --tb=no como focal_test sin leerlo; el implementer ve nombres de casos, mensajes y valores de asercion, no el cuerpo, y no recibe clave ni muestras estructurales como insumo. Su salida informa la correccion; pytest no es un sandbox, sin aislamiento tecnico. Un selector mecanico mas amplio no autoriza otras referencias.
  - Segundo encargo reviewer/review independiente: cubrir todo el diff del producto, incluidas afirmaciones nuevas y respaldos cambiados, y vincular cada correccion con su evidencia; conservar informes previos.
  - Si no hay correcciones necesarias, registrar esa conclusion sin fabricar cambios.
  - Una necesidad de cambiar fuentes, clave o verificador se detiene y vuelve al rol competente; si cambia el contrato requiere aprobacion y decision sobre evidencia anterior.
- regressions:
  - tests/test_010_001_documentary_contracts.py
  - tests/test_010_002_documentary_role_integration.py
- integration_gate: Sin bloqueantes, pruebas y regresiones pertinentes verdes y correcciones re-verificadas; request del implementer con read_scope recortado conforme a O-12, O-13 y O-14; fuentes, clave y verificadores protegidos.
- Widen (ampliar) the validation when the change leaves the focal tests: a shared contract or an uncertain impact expands the validation to the declared regressions and the integration gate; a local correction uses the focal tests.
- Plan provenance: docs/specs/010-003-documentary-pilot/plan.md (sha256 49ce6f813aeb4e0bea0ff4f44d541a48deef29dc42f2af5aa6e05e5bf3352b04)

## Applicable contract

- Contract: docs/specs/010-003-documentary-pilot/spec.md (sha256 f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5)

## Inputs
- docs/specs/010-003-documentary-pilot/spec.md: approved contract
- docs/specs/010-003-documentary-pilot/spec.md: contrato aprobado v5 (PC-10..PC-13)
- docs/specs/010-003-documentary-pilot/product/relevamiento.md: producto corregido bajo re-verificacion
- docs/specs/010-003-documentary-pilot/product-review.md: informe de T6: F-1 bloqueante y O-1/O-2/N-1
- docs/specs/010-003-documentary-pilot/tdd-t7-review-fix.md: informe del implementer sobre la correccion
- docs/specs/010-003-documentary-pilot/challenge-contrast.md: contraste del ensayo T5
- tests/fixtures/010_003_documentary_pilot/sources/inventory.md: inventario inventory-010-003-v1
- tests/fixtures/010_003_documentary_pilot/sources/s1.md: fuente autorizada s1
- tests/fixtures/010_003_documentary_pilot/sources/s2.md: fuente autorizada s2
- tests/fixtures/010_003_documentary_pilot/challenge/negative.md: candidato negativo de referencia
- tests/fixtures/010_003_documentary_pilot/oracle/contrast-key.md: clave de contraste fijada (protegida: no transcribir)
- skills/cdad-cycle/references/stage-4-review.md: referencia normativa de la revision

## Read scope
[{"class":"contract","path":"docs/specs/010-003-documentary-pilot/spec.md"},{"class":"contract","root":"docs/specs/010-003-documentary-pilot/product"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/product-review.md"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/tdd-t7-review-fix.md"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/challenge-contrast.md"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/sources"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/challenge"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/oracle"},{"class":"implementation","root":"skills/cdad-cycle/references"}]

## Write scope
[]

## Invariants
- Se re-verifica TODO el diff del producto (7fcca219..6596e804), no solo F-1: afirmaciones nuevas, cambios de respaldo, divergencias y pendientes.
- El diff toca solo docs/specs/010-003-documentary-pilot/product/relevamiento.md y desciende de 7fcca219e119ea72f29d68f406642afa5b2e1483.
- La clave de contraste se usa para confirmar que el diff no reintrodujo los tres defectos y NO se transcribe en el informe.

## Expected output
Role report with the required evidence

## Evidence required
- modified files
- exact commands
- command output
- commit
