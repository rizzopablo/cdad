#!/usr/bin/env python3
"""BLACK-BOX RED — 010-004 T2 subfase RED nuevo (promesa B: PC-04, PC-05, PC-06, PC-07).

Contrato: `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`
(pin `fc6b2ccc…`). El CLI (`scripts/cdad_packet.py`) se ejercita como
subproceso, caja negra: no se importan ni leen `skills/`, `scripts/`,
`sources/`, `agents/` ni `build/`. Toda edición de esta subfase vive en
`tests/**`; los tests actualizados por POST-AUDIT y los declarados intactos
por el AUDIT no se tocan (archivo NUEVO, sin hunks en archivos existentes).

Trazabilidad test → postcondición numerada → consecuencia de usuario (R4):

| Test | PC | Promesa observable | R4: sin este test el usuario… |
|---|---|---|---|
| `test_pc04a_…declares_locator` | PC-04(a) | Una preparación nueva con contexto v2 canónico publica el paquete y declara el localizador `.cdad/executions/<id>/execution.json` en request y cabecera | …despacharía encargos nuevos que no dicen dónde vive el contexto v2 canónico, obligando al rol a adivinarlo o a confiar en ubicaciones sin autoridad (INV-12). |
| `test_pc05a_…without_argument` | PC-05(a) fila 1 | request CON localizador y SIN `--execution-context` resuelve exclusivamente el localizador en `render`, `validate-request` y `validate-packet` | …tendría que transcribir la ruta del contexto por CLI aunque el paquete Ya la declara: la fila 1 de la matriz queda sin oráculo y la promesa de despacho sin retranscripción muere. |
| `test_pc06a_…variants` | PC-06(a) | Checks compartidos: localizador absoluto/vacío/con escapes/no canónico/discordante en identidad o schema se rechazan con causa y sin efectos | …aceptaría copias no canónicas como fuente de contexto o recibiría rechazos sin causa distinguible, sin saber qué corrección hacer. |
| `test_pc06b_…agree` | PC-06(b)/PC-05 fila 2 | El argumento explícito de los tres CLI debe resolver al MISMO archivo canónico que el localizador; si discrepa, rechazo con causa y sin efectos | …validaría o renderizaría contra un contexto cuyo archivo no es el canónico declarado, silenciosamente. |
| `test_pc07a_…cwd` | PC-07(a) | Con raíz explícita y argumentos absolutos desde otro cwd, la resolución por localizador produce la MISMA validación y el MISMO bytes de render que desde la raíz | …no podría despachar ni validar desde otra raíz de trabajo: la independencia del directorio de invocación queda sin garantía. |
| `test_pc07c_…no_locator_metadata` | PC-07(c) | El request histórico sin campo no gana metadatos en el render ni provoca reescritura o migración de sus archivos | …vería sus requests históricos migrados o anotados silenciosamente (INV-08). |

Saturaciones citadas (sin duplicar; no se escriben tests nuevos para ellas):
- PC-04(b) selección v1 EXPLÍCITA ya repelida con diagnóstico, sin conversión
  ni publicación: `tests/test_004_002_t6_landing.py::TestPd10ExplicitV1Context`
  (verde hoy). La selección v1 IMPLÍCITA sin policy y la copia v2 no canónica
  ya están rojas en los tests que POST-AUDIT dejó actualizados (pc: PC-04c):
  NO se duplican aquí (frontera del objetivo).
- PC-05(b)/(c) fila histórica y fila 4: `tests/test_role_packet_render.py::
  TestPublicTask2Surface::test_p1_all_role_substage_pairs_render_and_validate`
  cubre la fila histórica con argumento; la fila 4 (histórico sin argumento →
  rechazo por contexto no proporcionado) se comporta hoy como la exige el
  AUDIT (§4, focales): no se multiplica.
- PC-05 fila 3 (histórico con argumento): la misma cita anterior.

RED esperado hoy (comportamiento sustituto confirmado por sondas caja-negra):
- `render`/`validate-request`/`validate-packet` con request que declara el
  campo terminan rc=2 — hoy: «request fields do not match schema» (campo
  fuera del conjunto cerrado) o «the following arguments are required:
  --execution-context» (sin argumento). Puede observarse rc≠0 con causa
  AJENA: la aserción de causa de localizador es lo que falla, no el rc.
- `prepare` con contexto v2 canónico publica hoy (sigue verde) pero su
  REQUEST.json y su cabecera NO declaran el localizador.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from tests.test_packet_prepare import PrepareProject, run_prepare, tree_snapshot
from tests.test_role_packet_render import PACKET_BEGIN, PacketFixture, parse_packet
from tests.test_role_packets import EXECUTION_ID, PACKET_CLI, REPO_ROOT

CANONICAL_LOCATOR = f".cdad/executions/{EXECUTION_ID}/execution.json"


def run_cli(command: str, *args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PACKET_CLI), command, *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )


class T2RedTestCase(unittest.TestCase):
    """Proyectos sintéticos PacketFixture con el contexto v2 en su ubicación
    canónica y el localizador declarado en el request."""

    def tempdir(self: unittest.TestCase, prefix: str) -> Path:
        temp = tempfile.TemporaryDirectory(prefix=prefix)
        self.addCleanup(temp.cleanup)
        return Path(temp.name).resolve()

    def locator_project(
        self, locator: str | None = CANONICAL_LOCATOR
    ) -> tuple[Path, PacketFixture, Path]:
        """Proyecto público cuyo contexto v2 real vive en
        `.cdad/executions/<EXECUTION_ID>/execution.json`; el request declara
        el `execution_context` indicado (o ninguno, si `locator` es None).
        `EXECUTION.json` se retira del proyecto para que la única vía de
        contexto sea el localizador (y, en GREEN, el argumento explícito
        cuando se pasa)."""
        root = self.tempdir("cdad-t2red-")
        fixture = PacketFixture(root, "test-writer", "red")
        if locator is not None:
            fixture.request["execution_context"] = locator
        fixture.write()
        canonical = root / ".cdad" / "executions" / EXECUTION_ID / "execution.json"
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_bytes((root / "EXECUTION.json").read_bytes())
        (root / "EXECUTION.json").unlink()
        return root, fixture, canonical


class TestPC04NewPreparationDeclaresLocator(T2RedTestCase):
    def test_pc04a_new_preparation_with_canonical_v2_context_declares_locator(
        self,
    ) -> None:
        """PC-04(a) (spec §4.1 «Toda nueva publicación declara en request y
        cabecera el localizador», §5 PC-04; INV-12).

        Una preparación nueva con contexto v2 canónico publica el encargo y
        su REQUEST.json declara el localizador canónico, y la cabecera del
        paquete publicado (bloque canónico de metadatos) declara el mismo
        localizador. Se verifica leyendo los artefactos publicados.

        R4: sin esta prueba, un encargo nuevo despachado no diría dónde vive
        el contexto v2 canónico: el rol tendría que adivinarlo o aceptar
        ubicaciones sin autoridad.

        RED hoy (sonda caja-negra): prepare con contexto canónico publica
        rc=0, pero request y cabecera NO contienen `execution_context`.
        """
        temp = tempfile.TemporaryDirectory(prefix="cdad-t2red-pc04a-")
        self.addCleanup(temp.cleanup)
        proj = PrepareProject(Path(temp.name).resolve())
        canonical = (
            proj.root / ".cdad" / "executions" / EXECUTION_ID / "execution.json"
        )
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_bytes(proj.execution_path.read_bytes())

        result = run_prepare(
            PACKET_CLI,
            "--project-root",
            str(proj.root),
            "--execution-context",
            str(canonical),
            "--role",
            proj.role,
            "--substage",
            proj.substage,
            "--objective",
            "PC-04a locator declaration",
        )
        self.assertEqual(
            result.returncode,
            0,
            msg="PC-04(a): la preparación nueva con contexto v2 canónico "
                "debe publicar: "
                + result.stderr.decode(errors="replace"),
        )
        packet_dir = proj.root / ".cdad" / "packets" / proj.packet_id()
        request = json.loads(
            (packet_dir / "REQUEST.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            request.get("execution_context"),
            CANONICAL_LOCATOR,
            msg="PC-04(a) RED: el REQUEST.json publicado debe declarar el "
                f"localizador canónico {CANONICAL_LOCATOR} "
                f"(obtuvo: {request.get('execution_context')!r})",
        )
        published_bytes = (packet_dir / "PACKET.md").read_bytes()
        self.assertTrue(
            published_bytes.startswith(
                PACKET_BEGIN.encode("utf-8")
            ),
            msg="PC-04(a): el paquete publicado no es un render canónico",
        )
        metadata, _, _ = parse_packet(published_bytes.decode("utf-8"))
        self.assertEqual(
            metadata.get("execution_context"),
            CANONICAL_LOCATOR,
            msg="PC-04(a) RED: la cabecera del paquete publicado debe "
                f"declarar el mismo localizador canónico "
                f"{CANONICAL_LOCATOR} "
                f"(obtuvo: {metadata.get('execution_context')!r})",
        )


class TestPC05MatrixLocatorWithoutArgument(T2RedTestCase):
    def test_pc05a_locator_resolved_without_explicit_argument_by_three_clis(
        self,
    ) -> None:
        """PC-05(a), fila 1 de la matriz de §4.1 (spec §5 PC-05).

        Request CON localizador y SIN `--execution-context`: los tres CLI
        resuelven exclusivamente el localizador y validan.

        R4: sin esta prueba, la fila 1 de la matriz queda sin oráculo y el
        despacho sin retranscribir el cuerpo tampoco tiene contexto
        declarado: la promesa B muere en el primer paso.

        RED hoy (sonda caja-negra): `--execution-context` sigue siendo un
        argumento requerido de los tres CLI, así que el request con
        localizador no puede resolverse solo. Mientras el render falle
        (rc=2), validate-packet recibe bytes vacíos; el rechazo observable
        sigue siendo la resolución ausente.
        """
        root, _, canonical = self.locator_project()
        request_path = root / "REQUEST.json"
        packet_path = root / "PACKET.md"
        packet_path.write_text("", encoding="utf-8")

        rendered = run_cli(
            "render", "--project-root", str(root), "--request", str(request_path)
        )
        with self.subTest(command="render"):
            self.assertEqual(
                rendered.returncode,
                0,
                msg="PC-05(a): render debe resolver el localizador sin "
                    "--execution-context (RED hoy: el argumento sigue "
                    "exigiéndose): " + rendered.stderr.strip(),
            )
        validated_request = run_cli(
            "validate-request",
            "--project-root",
            str(root),
            "--request",
            str(request_path),
        )
        with self.subTest(command="validate-request"):
            self.assertEqual(
                validated_request.returncode,
                0,
                msg="PC-05(a): validate-request debe resolver el localizador "
                    "sin --execution-context (RED hoy): "
                    + validated_request.stderr.strip(),
            )
        if rendered.stdout.startswith(PACKET_BEGIN):
            packet_path.write_text(rendered.stdout, encoding="utf-8")
        validated_packet = run_cli(
            "validate-packet",
            "--project-root",
            str(root),
            "--request",
            str(request_path),
            "--packet",
            str(packet_path),
        )
        with self.subTest(command="validate-packet"):
            self.assertEqual(
                validated_packet.returncode,
                0,
                msg="PC-05(a): validate-packet debe resolver el localizador "
                    "sin --execution-context (RED hoy): "
                    + validated_packet.stderr.strip(),
            )
        self.assertEqual(
            rendered.stdout,
            packet_path.read_text(encoding="utf-8"),
            msg="PC-05(a): el render debe ser determinista frente al paquete "
                "validó por validate-packet",
        )


class TestPC06SharedChecksRejectOutOfDomainLocator(T2RedTestCase):
    def test_pc06a_out_of_domain_locator_variants_rejected_with_cause(
        self,
    ) -> None:
        """PC-06(a) (spec §4.1 «Dominio del localizador», §4.5 diagnóstico
        por causa, §5 PC-06; INV-11).

        Los checks compartidos rechazan localizadores fuera del dominio —
        absoluto, vacío, con escapes `..`, ubicación no canónica incluso
        byte-idéntica, e identidad o schema discordantes con el request —
        con diagnóstico de causa distinguida y siguiente acción disponible
        (no se congela la prosa), sin efectos persistentes.

        Variantes agrupadas en subTests: una sola promesa (rechazo de
        localizador fuera del dominio), no variantes de cobertura.

        Controles positivos: la superficie no es rechazo universal — la
        promesa de aceptación de un request con localizador canónico cuando
        no hay argumento es el test PC-05a de este paquete (y, tras GREEN,
        en el mismo fixture, rc=0).

        R4: sin esta prueba, el proyecto toleraría copias no canónicas como
        fuente de contexto (rutas absolutas, `.cdad/legacy.json`, documentos
        con otra identidad) o recibiría errores genéricos sin causa.

        RED hoy (sonda caja-negra): el campo nuevo fuera del schema produce
        rc=2 «request fields do not match schema» — neutro. La aserción de
        causa de localizador falla: el diagnóstico no nombra el dominio
        buscado (`.cdad/executions/<id>/execution.json`).
        """
        domain_cause = r"(\.cdad/executions|(?i:execution_context|localiz|locator))"
        identity_cause = r"([Ee]xecution[ _-]?id|\.cdad/executions|(?i:localiz|locator|execution_context))"
        schema_cause = r"(?i:(\bv2\b|schema[_ -]?version|version\b.{0,8}\b2\b))"

        def assert_out_of_domain(root: Path, label: str, cause_pattern: str) -> None:
            """Rechazo observado por validate-request (los checks
            compartidos), con causa distinguible y sin efectos."""
            before = tree_snapshot(root)
            probe = run_cli(
                "validate-request",
                "--project-root",
                str(root),
                "--request",
                str(root / "REQUEST.json"),
            )
            self.assertNotEqual(
                probe.returncode,
                0,
                msg=f"PC-06(a): localizador fuera de dominio ({label}) "
                    "debe rechazarse",
            )
            self.assertEqual(
                probe.stdout,
                "",
                msg=f"PC-06(a): el rechazo ({label}) no debe emitir "
                    "paquete por stdout",
            )
            self.assertTrue(
                probe.stderr.strip(),
                msg=f"PC-06(a): el rechazo ({label}) debe producir un "
                    "diagnóstico con causa",
            )
            self.assertRegex(
                probe.stderr,
                cause_pattern,
                msg=f"PC-06(a) RED: el diagnóstico del rechazo ({label}) "
                    "debe distinguir la causa del localizador y "
                    "(cuando se conoce) presentar la referencia canónica "
                    "esperada; hoy el error genérico del schema cerrado "
                    "no discrimina: "
                    + probe.stderr.strip(),
            )
            self.assertEqual(
                tree_snapshot(root),
                before,
                msg=f"PC-06(a): el rechazo ({label}) no debe producir "
                    "efectos persistentes (INV-11)",
            )

        def with_absolute() -> None:
            """Variante absoluta: los bytes correctos pero en forma absoluta
            (el dominio exige la cadena project-relative exacta)."""
            with self.subTest(locator_variant="absolute"):
                root, fixture, canonical = self.locator_project(
                    locator=None
                )
                fixture.request["execution_context"] = str(canonical)
                fixture.write_request()
                assert_out_of_domain(root, "absolute", domain_cause)

        with_absolute()
        for label, locator, cause_pattern in (
            ("empty", "", domain_cause),
            ("escape", ".cdad/executions/../evil.json", domain_cause),
            ("non-canonical copy", ".cdad/legacy-context.json", domain_cause),
            (
                "identity mismatch",
                ".cdad/executions/exec-other-identity/execution.json",
                identity_cause,
            ),
            (
                "schema mismatch",
                CANONICAL_LOCATOR,
                schema_cause,
            ),
        ):
            with self.subTest(locator_variant=label):
                root, fixture, canonical = self.locator_project(locator)
                if label == "non-canonical copy":
                    (root / ".cdad" / "legacy-context.json").write_bytes(
                        canonical.read_bytes()
                    )
                if label == "identity mismatch":
                    alt = root / ".cdad" / "executions" / "exec-other-identity"
                    alt.mkdir(parents=True, exist_ok=True)
                    doc = json.loads(canonical.read_text(encoding="utf-8"))
                    doc["execution"]["id"] = "exec-other-identity"
                    (alt / "execution.json").write_text(
                        json.dumps(doc), encoding="utf-8"
                    )
                if label == "schema mismatch":
                    doc = json.loads(canonical.read_text(encoding="utf-8"))
                    doc["schema_version"] = 1
                    canonical.write_text(json.dumps(doc), encoding="utf-8")
                assert_out_of_domain(root, label, cause_pattern)


class TestPC06ExplicitArgumentAgreesWithLocator(T2RedTestCase):
    def test_pc06b_explicit_argument_must_agree_with_declared_locator(
        self,
    ) -> None:
        """PC-06(b) / PC-05 fila 2 (spec §4.1 «Resolución de los tres CLI»).

        El argumento explícito `--execution-context` de los tres CLI debe
        resolver al mismo archivo canónico que el localizador declarado;
        si discrepa (aunque sea byte-idéntico en otra ruta), rechazo con
        diagnóstico de contexto y sin probar otra ubicación ni efectos.

        ¿Por qué el lado positivo en el mismo test? La promesa única es
        «el argumento debe concordar con el localizador»: el rechazo sin
        control positivo sería rechazo universal (prohibido por el
        contrapeso R7 del objetivo).

        R4: sin esta prueba, un encargo declararía un localizador canónico
        pero validaría contra otro archivo elegido por argumento, sin aviso.

        RED hoy (sonda caja-negra): el lado positivo cae — hoy el CLI
        rechaza el request con «request fields do not match schema» (rc=2)
        y quizá también el lado negativo por esa misma causa ajena; el
        RED esperado es la aceptación ausente de la fila 2 — la aserción
        de rc del lado positivo es la que falla primero.
        """
        root, _, canonical = self.locator_project()
        request_path = root / "REQUEST.json"
        packet_path = root / "PACKET.md"
        packet_path.write_text("", encoding="utf-8")

        agreement = {}
        rendered = run_cli(
            "render",
            "--project-root",
            str(root),
            "--request",
            str(request_path),
            "--execution-context",
            str(canonical),
        )
        agreement["render"] = rendered
        if rendered.stdout.startswith(PACKET_BEGIN):
            packet_path.write_text(rendered.stdout, encoding="utf-8")
        agreement["validate-request"] = run_cli(
            "validate-request",
            "--project-root",
            str(root),
            "--request",
            str(request_path),
            "--execution-context",
            str(canonical),
        )
        agreement["validate-packet"] = run_cli(
            "validate-packet",
            "--project-root",
            str(root),
            "--request",
            str(request_path),
            "--execution-context",
            str(canonical),
            "--packet",
            str(packet_path),
        )
        for command in ("render", "validate-request", "validate-packet"):
            with self.subTest(post=command):
                self.assertEqual(
                    agreement[command].returncode,
                    0,
                    msg=f"PC-06(b): {command} aceptando la fila 2 — request "
                        "con localizador + argumento explícito que resuelve "
                        "al MISMO archivo canónico; hoy la fila 2 no existe: "
                        + agreement[command].stderr.strip(),
                )

        # Lado negativo (una sola promesa, variantes por CLI): el argumento
        # apunta a una copia byte-idéntica en ubicación NO canónica.
        disagree_path = root / "EXECUTION.json"
        disagree_path.write_bytes(canonical.read_bytes())
        context_cause = r"(?i:context|localiz|locator)"
        for command in ("render", "validate-request", "validate-packet"):
            extra = ("--packet", str(packet_path)) if command == "validate-packet" else ()
            before = tree_snapshot(root)
            probe = run_cli(
                command,
                "--project-root",
                str(root),
                "--request",
                str(request_path),
                "--execution-context",
                str(disagree_path),
                *extra,
            )
            self.assertNotEqual(
                probe.returncode,
                0,
                msg=f"PC-06(b): {command} no debe aceptar un argumento "
                    "explícito que resuelve a otra ubicación que el "
                    "localizador declarado, aunque los bytes coincidan",
            )
            self.assertEqual(
                probe.stdout,
                "",
                msg=f"PC-06(b): el rechazo de {command} no debe emitir "
                    "paquete por stdout",
            )
            self.assertRegex(
                probe.stderr,
                context_cause,
                msg=f"PC-06(b): el diagnóstico de {command} debe nombrar la "
                    "causa de contexto (discordancia localizador/argumento): "
                    + probe.stderr.strip(),
            )
            self.assertEqual(
                tree_snapshot(root),
                before,
                msg=f"PC-06(b): el rechazo de {command} no debe producir "
                    "efectos persistentes (INV-11); el CLI tampoco debe "
                    "probar otra ubicación (la copia no canónica no se "
                    "convierte ni se reubica)",
            )


class TestPC07InvocationDirectoryIndependence(T2RedTestCase):
    def test_pc07a_locator_resolution_is_invocation_directory_independent(
        self,
    ) -> None:
        """PC-07(a) (spec §4.1 «Raíz y argumentos», §5 PC-07, O-3).

        La raíz se declara explícitamente (ruta absoluta) y los argumentos
        de archivo son válidos desde el directorio distinto: el request con
        localizador resuelve el MISMO contexto: la validación acepta y los
        bytes del render son iguales a los obtenidos desde la raíz.

        R4: sin esta prueba, el despacho desde otra raíz de trabajo rompería
        la resolución o cambiaría los bytes: la salida quedaría atada al
        directorio de invocación del orquestador.

        RED hoy (sonda caja-negra): los CLI exigen `--execution-context`,
        así que desde otro cwd la aceptación no se alcanza; la aserción de
        rc de aceptación falla primero.
        """
        root, _, canonical = self.locator_project()
        other = self.tempdir("cdad-t2red-cwd-")
        request_path = root / "REQUEST.json"
        common = ("--project-root", str(root), "--request", str(request_path))
        validated_from_root = run_cli(
            "validate-request", *common, cwd=REPO_ROOT
        )
        with self.subTest(surface="validate-request-from-root"):
            self.assertEqual(
                validated_from_root.returncode,
                0,
                msg="PC-07(a): el miembro 'desde la raíz' de la comparación "
                    "debe ser aceptado (hoy rc=2 se explica por el "
                    "argumento requerido): "
                    + validated_from_root.stderr.strip(),
            )
        validated_from_other = run_cli(
            "validate-request", *common, cwd=other
        )
        with self.subTest(surface="validate-request-from-other-cwd"):
            self.assertEqual(
                validated_from_other.returncode,
                0,
                msg="PC-07(a) RED: con raíz explícita y argumentos absolutos "
                    "desde otro cwd, validate-request debe resolver el "
                    "mismo localizador y aceptar; hoy: "
                    + validated_from_other.stderr.strip(),
            )
        rendered_from_root = run_cli("render", *common, cwd=REPO_ROOT)
        rendered_from_other = run_cli("render", *common, cwd=other)
        with self.subTest(surface="render-bytes-agree-across-cwd"):
            self.assertEqual(
                rendered_from_root.returncode,
                0,
                msg="PC-07(a): el miembro 'desde la raíz' del render debe aceptar: "
                    + rendered_from_root.stderr.strip(),
            )
            self.assertEqual(
                rendered_from_other.returncode,
                0,
                msg="PC-07(a) RED: render debe resolver el mismo contexto "
                    "desde otro cwd con raíz explícita: "
                    + rendered_from_other.stderr.strip(),
            )
            self.assertEqual(
                rendered_from_root.stdout,
                rendered_from_other.stdout,
                msg="PC-07(a): los bytes del render deben ser iguales desde "
                    "la raíz y desde otro directorio (el mismo contexto se "
                    "resuelve: exactamente el "
                    f"{CANONICAL_LOCATOR})",
            )


class TestPC07HistoricalRequestWithoutField(T2RedTestCase):
    def test_pc07c_historical_request_without_field_gains_no_locator_metadata(
        self,
    ) -> None:
        """PC-07(c) (spec §4.1 «Reentrada y replay históricos», §5 PC-07;
        INV-08).

        El request HISTÓRICO sin campo conserva su uso explícito v2 con las
        condiciones de validación existentes y la ausencia del campo NO
        añade metadatos al render (`execution_context` no aparece en la
        cabecera canónica) ni reescribe request, contexto o state.

        R4: sin esta prueba, las ejecuciones nuevas podrían filtrar campos
        de localizador o reescribir los archivos históricos en silencio.

        ESTADO ESTE PAQUETE: GREEN hoy (saturación declarada) — el render
        histórico ya es indeterminista y آر se comporta igual; se fija para
        prevenir una regresión invasiva del GREEN de T2 sobre la vía
        histórica (la promesa es separada de la de PC-05a y restaría sin
        test si no se escribe).
        """
        root = self.tempdir("cdad-t2red-pc07c-")
        fixture = PacketFixture(root, "test-writer", "red")  # sin campo nuevo
        fixture.write()
        tracked = ("REQUEST.json", "EXECUTION.json", "docs/.cdad-state.json")
        before = {name: (root / name).read_bytes() for name in tracked}
        rendered = fixture.render()
        self.assertEqual(
            rendered.returncode,
            0,
            msg="PC-07(c): el request histórico, con argumento explícito "
                "v2, debe seguir renderizando (fila histórica de la matriz): "
                + rendered.stderr,
        )
        metadata, _, _ = parse_packet(rendered.stdout)
        self.assertNotIn(
            "execution_context",
            metadata,
            msg="PC-07(c): la cabecera canónica del request histórico no "
                "debe ganar metadatos de localizador por la ausencia del "
                "campo",
        )
        after = {name: (root / name).read_bytes() for name in tracked}
        self.assertEqual(
            after,
            before,
            msg="PC-07(c): el render histórico no debe reescribir request, "
                "contexto ni state (sin migración ni adopción silenciosa, "
                "INV-08)",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
