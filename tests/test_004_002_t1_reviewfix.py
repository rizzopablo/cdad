#!/usr/bin/env python3
"""004-002 T1 RED review-fix — hallazgos B1, B2, B3, O2, O3, P-VALID.

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md (PD-1,
PD-2, PD-9) + docs/specs/004-002-project-execution-bootstrap/review-t1.md
(disposición del orquestador al final del documento).

Cada test nombra su hallazgo de review. RED hoy contra 49d2ebf (estado
equivalente de scripts/cdad_packet.py): las sondas del reviewer reproducen
los defectos fuera de la cobertura actual; estos tests los fijan como
contrato verificable.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.test_004_002_t1_policy import (
    POLICY_FILE,
    ProjectCase,
    parse_classify,
    run_classify,
    run_cli,
    run_propose,
    run_validate,
    tree_digest,
    write_policy,
)


class RmCase(ProjectCase):
    """Igual que ProjectCase, registrando también los tempdir externos."""

    _externals: list[Path]

    def setUp(self) -> None:
        super().setUp()
        self._externals = []

    def make_outside(self) -> Path:
        outside = Path(tempfile.mkdtemp(
            prefix="cdad-t1-rfix-outside-"))
        self._externals.append(outside)
        self.addCleanup(
            lambda: subprocess.run(
                ["rm", "-rf", *[str(p) for p in self._externals]],
                check=False))
        return outside


# ---------------------------------------------------------------- B1


class TestB1ColocatedConflicts(RmCase):
    """B1: los solapamientos incluyen las convenciones co-ubicadas."""

    def test_b1_documentation_root_over_colocated_tests_rejected(self) -> None:
        """B1 (PD-2): documentation_roots=["pkg"] con tests co-ubicados
        declarados en el mismo paquete (prefix test_) es conflicto → rc≠0:
        documentation contra tests es conflicto también para tests
        co-ubicados, no solo para test_roots. Fixture del orquestador
        (sin implementation_roots: el único solapamiento es documentación
        vs tests co-ubicados; colisión trivial doc-vs-doc excluida):
        contra 49d2ebf hoy rc=0 VALID y pkg/test_a.py se clasifica
        colocated-test, o sea el defecto reproducido."""
        (self.root / "pkg").mkdir()
        (self.root / "pkg" / "test_a.py").write_text("", encoding="utf-8")
        write_policy(self.root, path_policy={
            "documentation_roots": ["pkg"],
            "colocated_test_roots": ["pkg"],
            "colocated_test_prefixes": ["test_"],
        }, temporary_roots=[])
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0,
                            msg="documentación solapada con tests co-ubicados aceptada")
        self.assertTrue((proc.stdout + proc.stderr).strip(),
                        msg="sin diagnóstico del conflicto")

    def test_b1_temporary_root_over_declared_colocated_tests_rejected(self) -> None:
        """B1 (PD-9): temporary_roots=["pkg"] cubre los tests co-ubicados
        declarados (prefix test_): garantía doble —
        (a) validate-policy rechaza el solapamiento temporal-vs-test
            co-ubicado → rc≠0 con diagnóstico; y
        (b) pkg/test_a.py nunca se clasifica `temporary`
            (reproduce la sonda (b) del orquestador: contra 49d2ebf hoy
            rc=0 y responde temporary)."""
        (self.root / "pkg").mkdir()
        (self.root / "pkg" / "test_a.py").write_text("", encoding="utf-8")
        write_policy(self.root, path_policy={
            "colocated_test_roots": ["pkg"],
            "colocated_test_prefixes": ["test_"],
        }, temporary_roots=["pkg"])
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0,
                            msg="temporary_roots sobre tests co-ubicados aceptado")
        self.assertTrue((proc.stdout + proc.stderr).strip(),
                        msg="sin diagnóstico del solapamiento")
        proc2 = run_classify(self.root, "pkg/test_a.py")
        classes = parse_classify(proc2.stdout)
        self.assertNotEqual(
            classes.get("pkg/test_a.py"), "temporary",
            msg="pkg/test_a.py clasificada temporary bajo temporary_roots "
                "cubierta por temporary_roots con el test co-ubicado declarado "
                f"(mapa: {classes})")


# ---------------------------------------------------------------- B2


class TestB2PolicySymlinkOutsideProject(RmCase):
    """B2 (PD-1 + PD-2): la resolución de la política debe ser la misma con
    y sin --classify: symlink fuera del proyecto → rc≠0 SIEMPRE."""

    def test_b2_policy_symlink_outside_rejected_with_and_without_classify(self) -> None:
        """B2: docs/cdad-policy.json symlink → JSON externo válido.
        Hoy sin --classify devuelve rc=0 VALID; con --classify rc=2
        'path escapes project root': el mismo documento cambia de validez."""
        outside = self.make_outside()
        outside_json = outside / "external-policy.json"
        outside_json.write_text(
            '{"schema_version": 1,\n'
            ' "path_policy": {"test_roots": ["tests"]},\n'
            ' "temporary_roots": []}\n',
            encoding="utf-8")
        write_policy(self.root, path_policy={"test_roots": ["tests"]},
                     temporary_roots=[])
        (self.root / POLICY_FILE).unlink()
        (self.root / POLICY_FILE).symlink_to(outside_json)

        # el documento NO es válido, con o sin --classify
        for label, args in (
                ("sin-classify",
                 ["validate-policy", "--project-root", str(self.root)]),
                ("con-classify",
                 ["validate-policy", "--project-root", str(self.root),
                  "--classify", "tests/test_a.py"])):
            with self.subTest(caso=label):
                proc = run_cli(args)
                self.assertNotEqual(proc.returncode, 0,
                                    msg=label + ": symlink fuera del proyecto validó")
                self.assertTrue((proc.stdout + proc.stderr).strip(),
                                msg=label + ": sin diagnóstico")


# ---------------------------------------------------------------- B3


class TestB3ProposePolicyRejectsOrdinaryOptions(RmCase):
    """B3 (PD-1, spec §2): --propose-policy no requiere rol/substage/objetivo,
    pero mezclarlo con ellos es un modo exclusivo violado → diagnóstico,
    rc≠0 y ninguna escritura."""

    def test_b3_propose_policy_with_prepare_options_fails_without_writes(self) -> None:
        """B3: prepare --propose-policy junto con cualquier opción ordinaria
        → rc≠0 con diagnóstico; el árbol del proyecto queda intacto.
        Cubre valores no vacíos en roles/substage/objetivo y, por el B3
        residual de la re-review, opciones escalares con valor vacío
        (--role "", --substage "", --objective "", --execution-context "",
        --expected-output "", --out-dir ""): hoy (a62ab68) el guard confunde
        opción ausente con escalar "" y emite la propuesta con rc=0."""
        write_policy(self.root, path_policy={"test_roots": ["tests"]},
                     temporary_roots=["tmp"])
        before = tree_digest(self.root)
        cases = [
            # valores no vacíos (RED original de B3)
            ("role", ["--role", "reviewer"]),
            ("substage", ["--substage", "red"]),
            ("objective", ["--objective", "encargo"]),
            # escalares con valor vacío (B3 residual, re-review)
            ("role-vacio", ["--role", ""]),
            ("substage-vacio", ["--substage", ""]),
            ("objective-vacio", ["--objective", ""]),
            ("execution-context-vacio", ["--execution-context", ""]),
            ("expected-output-vacio", ["--expected-output", ""]),
            ("out-dir-vacio", ["--out-dir", ""]),
        ]
        for label, extra in cases:
            with self.subTest(opcion=label):
                proc = run_cli([
                    "prepare", "--project-root", str(self.root),
                    "--propose-policy", *extra,
                ])
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=label + ": propuesta mezclada con preparación ordinaria válida")
                self.assertTrue(
                    (proc.stdout + proc.stderr).strip(),
                    msg=label + ": mezcla rechazada sin diagnóstico")
        self.assertEqual(
            tree_digest(self.root), before,
            msg="--propose-policy inválido escribió en el árbol")


# ---------------------------------------------------------------- O2


class TestO2ExactFileSemantics(RmCase):
    """O2 (PD-2): los archivos exactos se comparan por igualdad con las
    raíces enfrentadas, no por ascendencia (semántica de archivo exacto).
    Si al materializar la ruta resultara imposible (archivo y directorio con
    el mismo nombre), la política se valida en abstracto: las sondas de la
    review usan rutas inexistentes y no afirman que esos árboles puedan
    materializarse con `pkg` como archivo regular."""

    def test_o2_documentation_file_not_overlapping_implementation_root(self) -> None:
        """O2 (PD-2): documentation_files=["pkg"] con
        implementation_roots=["pkg/src"] es VÁLIDA (rc=0): archivo exacto se
        compara por igualdad, no por ascendencia; `pkg/src` no es igual al
        archivo exacto `pkg`. Sobre rutas inexistentes/abstractas."""
        write_policy(self.root, path_policy={
            "documentation_files": ["pkg"],
            "implementation_roots": ["pkg/src"],
        }, temporary_roots=[])
        proc = run_validate(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg="documentation_files=[pkg] con implementation_roots=[pkg/src] "
                "rechazada por ascendencia: " + (proc.stdout + proc.stderr))

    def test_o2_implementation_file_not_overlapping_temporary_root(self) -> None:
        """O2 (PD-9): implementation_files=["pkg"] con
        temporary_roots=["pkg/tmp"] es VÁLIDA (rc=0): archivo exacto ≠
        ascendencia."""
        write_policy(self.root, path_policy={
            "implementation_files": ["pkg"],
        }, temporary_roots=["pkg/tmp"])
        proc = run_validate(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg="implementation_files=[pkg] con temporary_roots=[pkg/tmp] "
                "rechazada por ascendencia: " + (proc.stdout + proc.stderr))


# ---------------------------------------------------------------- O3


class TestO3EmptyTemporaryList(RmCase):
    """O3 (PD-9): el test de lista vacía debe exigir la clasificación
    explícita de scratch/anything.txt como unclassified."""

    def test_o3_empty_list_classifies_scratch_anything_txt_unclassified(self) -> None:
        """O3 (PD-9): temporary_roots=[] → las rutas NO temporales responden
        unclassified, no un mapa vacío. Control bonus: la lista vacía sigue
        validando rc=0."""
        write_policy(self.root, path_policy={"test_roots": ["tests"]},
                     temporary_roots=[])
        proc = run_validate(self.root)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
        proc2 = run_classify(self.root, "scratch/anything.txt")
        classes = parse_classify(proc2.stdout)
        self.assertEqual(proc2.returncode, 0, msg=proc2.stderr or proc2.stdout)
        self.assertEqual(
            classes.get("scratch/anything.txt"), "unclassified",
            msg=f"clase de scratch/anything.txt con lista vacía: {classes}")


# ---------------------------------------------------------------- P-VALID


class TestProposeValidatedBeforeEmit(RmCase):
    """Propuesta validada antes de emitir (disposición: parte de O1)."""

    def test_pvalid_propose_invalid_layout_fails_without_emitting(self) -> None:
        """P-VALID: si el layout produce una propuesta inválida (src symlink
        fuera del proyecto), --propose-policy da rc≠0 con diagnóstico, sin
        emitir una política que validate-policy rechazaría."""
        write_policy(self.root, path_policy={"test_roots": ["tests"]},
                     temporary_roots=["tmp"])
        outside = self.make_outside()
        (self.root / "src").symlink_to(outside, target_is_directory=True)
        proc = run_propose(self.root)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="--propose-policy emitió una propuesta inválida (src symlink fuera)")
        self.assertTrue(
            (proc.stdout + proc.stderr).strip(),
            msg="propuesta rechazada sin diagnóstico")
        # Sin propuesta emitida que valide en abstracto: dado un stdout con
        # un JSON candidato, materializarlo en una copia NO debe validar
        # (anti-escape de la emisión).
        if proc.stdout.strip():
            copy_root = Path(self.root.parent / "proj-copy")
            if not (copy_root / POLICY_FILE).exists():
                (copy_root / "docs").mkdir(parents=True, exist_ok=True)
                (copy_root / POLICY_FILE).write_text(
                    proc.stdout, encoding="utf-8")
                vproc = run_validate(copy_root)
                self.assertNotEqual(
                    vproc.returncode, 0,
                    msg="la propuesta emitida valida, contradice rc≠0 de --propose-policy")


if __name__ == "__main__":
    unittest.main()
