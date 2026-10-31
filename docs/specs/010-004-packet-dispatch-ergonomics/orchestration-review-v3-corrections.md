# Review v3: correcciones acotadas antes de aprobación

Recibido el FINAL TEXT completo de `<session>` para reviewer-plan-review-004. Receipt validado, materialización CAS sobre la base de `eebc08dd`; review previo conservado en `plan-review-v2.md`. Attempt de continuidad 8 cerrado por receive (head seq 16); sin segundo begin ni nuevo dispatch del reviewer.

Según mandato del supervisor, aplicar N-2 y N-3 (BLOCKING) y O-C (formato) mediante un único encargo architect de corrección textual. N-1 cerrado; conservar cierres B-1/B-2, O-1..O-5, O-A/O-B e I-4/I-5. No aprobación ni avance a TDD.

- N-2: explicitar laguna real para v1 activo no terminal, incluido prepared: no hay CLI terminal existente aplicable. Diagnosticar causa y escalar al owner; mantener state intacto, sin preparar v1 ni prometer procedimiento inexistente. Es la laguna/escalación ya solicitada por la decisión owner, no una petición de nueva funcionalidad ni de nueva elección sobre v2. Sin migración ni withdraw v1.
- N-3: declarar sustitución explícita del comportamiento de 004-002 PD-12 (`spec.md:115`) por `owner-decision-v2-new-assignments.md`. Identificar los dos tests verificados: `tests/test_004_002_t6_landing.py::test_pd12_legacy_without_policy_keeps_legacy_intake` y `tests/test_packet_prepare.py::test_p2_default_execution_context_and_out_dir_under_project_cdad`. El test-writer audita la lista completa y actualiza expectativas con trazabilidad en su etapa; implementer no toca tests. Spec histórica intacta.
- O-C: quitar la línea vacía que divide la tabla markdown de §8.

Evidencia conservada sin inflarla: reviewer informa un test focal pasado y timeout de 120 s en PD12; no suite completa aprobada. §2.1 permanece pendiente para Pablo. Esta coordinación no añade un gate ni mecanismos.

Próximo encargo: architect-draft-004 por handoff C manual al padre, packet validado y rutas únicas; sin begin ni spawn aquí. Próximo attempt previsto 9 a partir del head verificado; corresponde al padre verificarlo de nuevo inmediatamente antes de su begin/verify-begin/dispatch.
