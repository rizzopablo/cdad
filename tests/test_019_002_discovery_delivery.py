#!/usr/bin/env python3
"""019-002 T2 RED (recovery) — entrega única de la consulta técnica del architect en
`brainstorm` (PC-4 de `docs/specs/019-002-effective-discovery-instructions/
recovery-spec.md`; contrato aprobado `spec.md` sha cd61455c…; reutiliza como
evidencia los tests retirados del commit 91835a6b, reevaluados de forma
independiente contra PC-4 de recuperación).

Promesa observable: cuando el orquestador consulta al architect durante el
descubrimiento (`brainstorm`), el informe que éste devuelve se registra. Hoy esa
consulta técnica legítima se rechaza antes de que su informe quede registrado.

Contrato PC-4: architect/brainstorm admite exactamente `role-report`; los kinds
de borrador (`architect-spec-draft`, `architect-plan-draft`) se rechazan para
esa subfase; el despacho nativo y el adaptador OpenCode derivan el mismo kind
único, que la ruta existente de resultado/materialización acepta. El resto de
los permisos rol/subfase no cambia.

Caja negra: sólo subprocess sobre los CLI públicos del repo, en proyectos
descartables (HOME/XDG redirigidos al tempdir). Ningún módulo del producto se
importa ni se lee; sólo se reutilizan las clases base de FIXTURE de tests
existentes (U1bEntryCase, U2ModuleCase, ScribeRowCase).

Consecuencia (R4): sin estos tests la consulta del architect no puede devolver
de forma fiable su informe por el transporte soportado (nativo/OpenCode) y el
descubrimiento se interrumpe. No hay exigencia global de cardinalidad de partes.

Mapeo test → postcondición (todos RED hoy por ASERCIÓN sobre comportamiento
pendiente):

  TestPc4NativeDerivation.test_pc4_native_brainstorm_delivery_kind_is_role_report
      -> PC-4 (derivación nativa). Sin él, el architect de `brainstorm` por la
         vía nativa no puede entregar su consulta (el `record` la rechaza).
  TestPc4OpenCodeDerivation.test_pc4_opencode_brainstorm_delivery_materializes
      -> PC-4 (derivación del adaptador + materialización con sha idéntico).
         Sin él, el adaptador despacha pero la consulta no se acepta.
  TestPc4BrainstormMaterialization.test_pc4_brainstorm_role_report_materializes_with_identical_sha
      -> PC-4 (kind admitido por la ruta existente de materialización).
  TestPc4BrainstormMaterialization.test_pc4_brainstorm_draft_kinds_are_rejected
      -> PC-4 (los kinds de borrador se rechazan en `brainstorm`; sin target
         escrito, state y receipt intactos).

Controles (ancla, ya cubiertos y NO duplicados aquí): architect/draft conserva
sus kinds en `test_005_007_t4_architect_report_materialization.py`,
`test_006_005_u1b…::TestPd23NativeDescriptorKind` y
`test_006_005_u2…::TestPd23DerivedArtifactKind`; los demás rechazos de
`role-report` por eje rol siguen en `test_006_005_u7…::TestPd26RoleAxisStaysClosed`
(menos architect/brainstorm, retirado deliberadamente: obligación obsoleta).
"""

from __future__ import annotations

import unittest

from test_006_005_u1b_dispatch_entry import (
    ATTEMPT_PD23_ARCH,
    NATIVE_SESSION,
    U1bEntryCase,
)
from test_006_005_u2_opencode_module import (
    U2ModuleCase,
    err_text as u2_err_text,
    out_text as u2_out_text,
    tail,
)
from test_006_005_u7_scribe_role_report import (
    TARGET_REPORT,
    ScribeRowCase,
    err_text,
    out_text,
)

ROLE = "architect"
SUBSTAGE = "brainstorm"
CONSULTATION_KIND = "role-report"
DRAFT_KINDS = ("architect-spec-draft", "architect-plan-draft")


class TestPc4NativeDerivation(U1bEntryCase):
    """PC-4 (nativo): el descriptor que `record` escenifica para architect/
    brainstorm declara el único kind de consulta."""

    def test_pc4_native_brainstorm_delivery_kind_is_role_report(self) -> None:
        ctx = self.new_project(role=ROLE, substage=SUBSTAGE)
        self.write_store(
            ["id TEXT PRIMARY KEY", "agent TEXT"],
            [{"id": NATIVE_SESSION, "agent": "cdad-architect"}])
        proc = self.record(
            ctx=ctx, attempt=ATTEMPT_PD23_ARCH,
            native_result=self.native_result_file("native-brainstorm.md"))
        self.assertEqual(
            proc.returncode, 0,
            msg="PC-4: el `record` nativo de architect/brainstorm debe "
                "escenificar la consulta técnica (kind `role-report`) en vez "
                "de rechazarla: rc=%s\n%s"
                % (proc.returncode, tail(self.output(proc))))
        descriptor = self.descriptor(ctx)
        kinds = [part.get("artifact_kind")
                 for part in descriptor.get("parts") or []
                 if isinstance(part, dict)]
        self.assertEqual(
            kinds, [CONSULTATION_KIND],
            msg="PC-4: el despacho nativo de architect/brainstorm declara "
                "exactamente `role-report` (nunca kinds de borrador): %r"
                % (descriptor.get("parts"),))


class TestPc4OpenCodeDerivation(U2ModuleCase):
    """PC-4 (adaptador OpenCode): la entrega de architect/brainstorm declara
    `role-report` y la ruta existente la materializa con sha idéntico."""

    def test_pc4_opencode_brainstorm_delivery_materializes(self) -> None:
        ctx = self.new_project(role=ROLE, substage=SUBSTAGE,
                               epic_plan_approved=True)
        fake = self.fake_runtime()
        proc = self.dispatch(ctx, fake)
        self.assertEqual(
            proc.returncode, 0,
            msg="PC-4: el adaptador debe entregar la consulta de architect/"
                "brainstorm: rc=%s stdout=%s stderr=%s"
                % (proc.returncode, tail(u2_out_text(proc)),
                   tail(u2_err_text(proc))))
        out = self.envelope(proc, "PC-4 opencode brainstorm")
        self.assertEqual(
            out["termination"], "completed",
            msg="PC-4: el despacho externo debe completar: %r"
                % (out.get("diagnosis"),))
        self.assert_materializes_with_identical_sha(
            ctx, CONSULTATION_KIND, "PC-4 opencode architect/brainstorm")


class TestPc4BrainstormMaterialization(ScribeRowCase):
    """PC-4 (tabla de materialización): `role-report` entra en brainstorm y los
    kinds de borrador salen."""

    ROLE = ROLE
    SUBSTAGE = SUBSTAGE
    PART_NAME = "consultation-report"
    PART_BYTES = (
        b"# Architect consultation report (fixture 019-002 PC-4)\n"
        b"Hallazgos tecnicos devueltos al orquestador como UNA sola parte.\n"
    )

    def authorize_report(self) -> object:
        self.prepare_target(TARGET_REPORT)
        auth_path = self.write_authorization(
            self.build_authorization(
                [{"part": self.PART_NAME, "target": TARGET_REPORT,
                  "expected_previous_sha256": None}]))
        self.snapshot_state_and_receipt()
        return auth_path

    def test_pc4_brainstorm_role_report_materializes_with_identical_sha(
            self) -> None:
        self.new_dispatched_project(part_kind=CONSULTATION_KIND)
        proc = self.materialize(self.authorize_report())
        self.assertEqual(
            proc.returncode, 0,
            msg="PC-4: architect/brainstorm admite `role-report`; sin ello la "
                "consulta técnica legítima se rechaza antes de registrarse: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assertNotIn("Traceback", err_text(proc))
        self.assert_target_identical(self.root / TARGET_REPORT)
        self.assert_no_state_or_receipt_change("PC-4 (brainstorm role-report)")

    def test_pc4_brainstorm_draft_kinds_are_rejected(self) -> None:
        for kind in DRAFT_KINDS:
            with self.subTest(kind=kind):
                self.new_dispatched_project(part_kind=kind)
                proc = self.materialize(self.authorize_report())
                self.assert_rejection(
                    proc, f"PC-4 (brainstorm rechaza {kind})",
                    (TARGET_REPORT,))


if __name__ == "__main__":
    unittest.main(verbosity=2)
