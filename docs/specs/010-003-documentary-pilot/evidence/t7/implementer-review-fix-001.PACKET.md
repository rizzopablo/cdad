---cdad-packet-json
{"contract":{"commit":null,"kind":"approved-feature-spec","path":"docs/specs/010-003-documentary-pilot/spec.md","sha256":"f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5"},"execution":{"authority_ref":"docs/epics/epic-010-documentary-specialization/execution.md","epic_id":"epic-010-documentary-specialization","feature_id":"010-003-documentary-pilot","id":"exec-010-003-documentary-pilot-001","model_policy":"ordinary","policy_sha256":"f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711","scope":"epic-010-documentary-specialization"},"execution_context":".cdad/executions/exec-010-003-documentary-pilot-001/execution.json","execution_id":"exec-010-003-documentary-pilot-001","feature_id":"010-003-documentary-pilot","instruction_sources":[{"path":"common.md","sha256":"37609c566bf8f827a082699745b4cc0e915e37421a34d65f98b29db179647110"},{"path":"roles/implementer.md","sha256":"ef3dab65a4d7c646be1c1953f92488e4e8f92fd7fb091869a3250d257e46e69b"},{"path":"substages/implementer-review-fix.md","sha256":"719bcbea0587014c9b54d08527d32079218a81ad92d8507510f0c647a77620d5"}],"packet_id":"010-003-documentary-pilot-implementer-review-fix-001","packet_version":1,"path_policy":{"documentation_files":["README.md"],"documentation_roots":["docs"],"implementation_files":["install.sh"],"implementation_roots":["agents","skills","scripts","sources","build"],"private_paths":["tests/.sensitive-patterns.local"],"test_roots":["tests"]},"policy":{"path":"docs/cdad-policy.json","schema_version":1,"sha256":"f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711","snapshot":"ewogICJwYXRoX3BvbGljeSI6IHsKICAgICJkb2N1bWVudGF0aW9uX3Jvb3RzIjogWwogICAgICAiZG9jcyIKICAgIF0sCiAgICAiaW1wbGVtZW50YXRpb25fZmlsZXMiOiBbCiAgICAgICJpbnN0YWxsLnNoIgogICAgXSwKICAgICJpbXBsZW1lbnRhdGlvbl9yb290cyI6IFsKICAgICAgImFnZW50cyIsCiAgICAgICJza2lsbHMiLAogICAgICAic2NyaXB0cyIsCiAgICAgICJzb3VyY2VzIiwKICAgICAgImJ1aWxkIgogICAgXSwKICAgICJ0ZXN0X3Jvb3RzIjogWwogICAgICAidGVzdHMiCiAgICBdLAogICAgInByaXZhdGVfcGF0aHMiOiBbCiAgICAgICJ0ZXN0cy8uc2Vuc2l0aXZlLXBhdHRlcm5zLmxvY2FsIgogICAgXSwKICAgICJkb2N1bWVudGF0aW9uX2ZpbGVzIjogWwogICAgICAiUkVBRE1FLm1kIgogICAgXQogIH0sCiAgInNjaGVtYV92ZXJzaW9uIjogMSwKICAidGVtcG9yYXJ5X3Jvb3RzIjogW10KfQo="},"read_scope":[{"class":"contract","path":"docs/specs/010-003-documentary-pilot/spec.md"},{"class":"contract","root":"docs/specs/010-003-documentary-pilot/product"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/product-review.md"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/sources"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/challenge"},{"class":"implementation","root":"skills/cdad-cycle/references"}],"role":"implementer","substage":"review-fix","write_scope":[{"class":"docs","root":"docs/specs/010-003-documentary-pilot/product"}]}
---end-cdad-packet-json
# CDAD task

<!-- cdad-instructions:start -->
You are executing one isolated CDAD role task. Follow the approved contract, the declared scopes, and the stated invariants. Read only declared inputs and scope; edit only declared write scope. Preserve session separation, gates, approvals, and evidence requirements. The configured and reported models are observations; model policy never broadens permissions. Report modified files, exact commands, outputs, and commit evidence. If the contract or test conflicts with the request, stop and report the mismatch. Do not load the full cycle instructions: this packet is the execution contract.

Full-suite policy (declared once, here in the common part): the complete suite is not run unless the packet explicitly asks for it, and the one who closes the task runs it — the closer runs the full suite once, at closure. Every role and subphase instruction references this policy and never restates it.

Act as implementer. Do not edit tests. Implement only behavior required by the approved contract and current failing tests. Keep the change minimal, preserve unrelated behavior, and run the focused tests and the proportional regression the change requires (the commands the project declares); the full-suite policy is declared once in the common part of this instruction. Evidence policy: `skills/cdad-cycle/references/stage-3-tdd.md` §"Test evidence policy".
Documentary duty: when the contract expressly authorizes a documentary product, produce only that authorized product inside the declared paths and leave the engagement's sources, verifiers and protected inputs unedited; the test ban above applies unchanged. The shared norm lives in `skills/cdad-cycle/references/documentary-contracts.md` (read it, never restate it).
Documentary engagements keep the role boundaries and the separation of responsibilities as they are; no documentary variant, selector or agent is created.

Verify each review finding against its original evidence before changing code. Apply only grounded fixes, preserve the full feedback provenance, and rerun the affected tests and the proportional regression the change requires (the commands the project declares). Evidence policy: `skills/cdad-cycle/references/stage-3-tdd.md` §"Test evidence policy".

<!-- cdad-instructions:end -->

## Objective
Correccion del producto de 010-003-documentary-pilot (T7, implementer/review-fix). Escribes SOLO `docs/specs/010-003-documentary-pilot/product/relevamiento.md`. Es una correccion acotada del producto existente: no lo reescribas ni lo reestructures.

INSUMOS AUTORIZADOS (nada mas): el contrato aprobado, el inventario `inventory-010-003-v1`, las dos fuentes `s1.md` y `s2.md`, el candidato negativo, el producto actual y el informe de revision `product-review.md`. La norma `skills/cdad-cycle/references/documentary-contracts.md` se declara como lectura normativa (el selector mecanico es mas amplio y NO autoriza otras referencias). Quedan FUERA y no debes leerlos: `tests/fixtures/010_003_documentary_pilot/oracle/`, `tests/fixtures/010_003_documentary_pilot/structural/`, el verificador `tests/test_010_003_documentary_pilot.py`, y cualquier otro documento de la feature. No ejecutes operaciones git que muestren contenido (`git show`, `git log -p`, `git diff`).

CAMBIOS A APLICAR (el informe trae la evidencia y las ubicaciones):

1. F-1 (BLOQUEANTE, obligatorio). Hoy la seccion "Plazo de respuesta" yuxtapone reglas de inicio sin declarar la incertidumbre: `s1-f03` cuenta desde el registro de la solicitud, `s1-f01` registra toda solicitud el dia de su recepcion, y `s1-f05` y `s2-f04` cuentan desde la recepcion completa; ninguna fuente dice si una solicitud completada se registra de nuevo. Debes:
   - atribuir cada regla de inicio a su fuente con localizador (ya estan las citas: conservalas y haz explicita la diferencia de inicio, no solo la del plazo);
   - declarar expresamente que el corpus no aclara si una solicitud completada despues se registra de nuevo, y que por eso el inicio exacto queda sin dirimir;
   - NO elegir una regla ni inventar una conciliacion;
   - agregar un pendiente nuevo (P-02) con TODOS los campos de PC-12: informacion o decision faltante, condicion de cierre, responsable conocido o designacion pendiente, y clasificacion justificada. No lo marques como bloqueante si el contrato promete documentar la divergencia; justificalo.
   - el pendiente debe quedar referido a la seccion por su nombre.

2. O-1 (adoptado). En P-01, citar `s2-f01` como contexto (la nota de que el procedimiento de `s2` se aplica junto con el del Area de Registro y no lo reemplaza), SIN extraer de el una prelacion que la fuente no fija.

3. O-2 (adoptado). En "Archivo", agregar una frase breve que indique que la diferencia de organizacion del legajo entre `s1-f04` y `s2-f05` queda sin dirimir. No la presentes como contradiccion cerrada ni como consenso.

4. N-1 (adoptado). Reemplazar las referencias fragiles ("seccion anterior", "la seccion") por los nombres de seccion, para que los pendientes sean rastreables.

RESTRICCIONES: conserva la estructura por secciones, las nueve citas existentes y la conservacion de ambas posiciones sobre la aprobacion de casos limite. Toda cita debe seguir resolviendo a fuente inventariada y ancla registrada. No agregues datos, personas ni organizaciones reales. No cambies la declaracion de documento sintetico ni la de correccion del candidato.

VERIFICACION OBLIGATORIA: ejecuta `python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py` y reporta salida y rc (debe quedar verde); ejecuta tambien las regresiones `python3 -B -m pytest -q --tb=no tests/test_010_001_documentary_contracts.py tests/test_010_002_documentary_role_integration.py` y reporta su rc. No leas ni modifiques el verificador.

COMMIT: commitea SOLO el producto, con mensaje `fix(010-003): declara la divergencia del inicio del plazo y clasifica los pendientes (T7)`. El commit debe descender de `7fcca219e119ea72f29d68f406642afa5b2e1483` (el commit del producto de T4); cita ese hash y el nuevo en el informe.

Devolver como FINAL TEXT: el diff conceptual de lo cambiado (que se agrego, que se preciso, que se dejo igual), la nueva seccion "Plazo de respuesta" y el nuevo P-02 completos, la tabla de comandos con salida y rc, el hash del commit y su ascendencia, y la lista de archivos modificados.

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
- docs/specs/010-003-documentary-pilot/spec.md: contrato aprobado v5 (PC-10..PC-13, §2.4)
- docs/specs/010-003-documentary-pilot/product/relevamiento.md: producto actual a corregir
- docs/specs/010-003-documentary-pilot/product-review.md: informe de revision T6: F-1 bloqueante y O-1/O-2/N-1
- tests/fixtures/010_003_documentary_pilot/sources/inventory.md: inventario inventory-010-003-v1
- tests/fixtures/010_003_documentary_pilot/sources/s1.md: fuente autorizada s1
- tests/fixtures/010_003_documentary_pilot/sources/s2.md: fuente autorizada s2
- tests/fixtures/010_003_documentary_pilot/challenge/negative.md: candidato negativo de referencia
- skills/cdad-cycle/references/documentary-contracts.md: norma documental (lectura normativa declarada)

## Read scope
[{"class":"contract","path":"docs/specs/010-003-documentary-pilot/spec.md"},{"class":"contract","root":"docs/specs/010-003-documentary-pilot/product"},{"class":"contract","path":"docs/specs/010-003-documentary-pilot/product-review.md"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/sources"},{"class":"tests","root":"tests/fixtures/010_003_documentary_pilot/challenge"},{"class":"implementation","root":"skills/cdad-cycle/references"}]

## Write scope
[{"class":"docs","root":"docs/specs/010-003-documentary-pilot/product"}]

## Invariants
- Do not edit tests
- El producto corregido no lee ni cita la clave ni las muestras estructurales: no estan en el alcance. La correccion se escribe contra las fuentes y el informe de revision.
- El commit del producto corregido desciende de 7fcca219e119ea72f29d68f406642afa5b2e1483 y solo toca docs/specs/010-003-documentary-pilot/product/relevamiento.md.
- El corpus no resuelve el inicio exacto del plazo cuando la solicitud llega incompleta: la correccion lo declara y agrega P-02, nunca elige una regla.

## Expected output
Role report with the required evidence

## Evidence required
- modified files
- exact commands
- command output
- commit
