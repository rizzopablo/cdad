#!/usr/bin/env python3
"""BLACK-BOX RED — 010-004 T3 (promesa A: PC-01, PC-02, PC-09; PC-08a A1).

Contrato: `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`
(pin `fc6b2ccc…`). El CLI (`skills/cdad-cycle/scripts/cdad_packet.py`) se
ejercita como subproceso, caja negra: no se importan ni leen `skills/`,
`scripts/`, `sources/`, `agents/` ni `build/`. Archivo NUEVO: no edita
tests existentes, `StateFixture`, `PrepareProject` ni fixture compartida.

Trazabilidad test → postcondición numerada → consecuencia de usuario (R4):

| Test | PC | Promesa observable | R4: sin este test el usuario… |
|---|---|---|---|
| `test_pc01_…exact_identification` | PC-01 | `render --route C` sobre paquete publicado válido con contexto canónico v2 emite SOLO la declaración literal y un único bloque ```json con el objeto completo de §4.2, concordante con archivos/contexto, determinista y sin modificar request, paquete ni estado | …recibiría una identificación incompleta, absoluta o no concordante y el receptor resolvería otro archivo (o ninguno): el encargo ejecutado no sería el publicado (INV-05/INV-12). |
| `test_pc02_…v1_context` | PC-02 | C rechaza un contexto v1 con diagnóstico explícito de C v2-only (causa + siguiente acción), sin identificación y sin efectos | …C podría identificar un paquete sobre el contexto v1 histórico que la regla de publicación nueva no admite, despachando trabajo sobre una autoridad no v2 (INV-08/INV-12). |
| `test_pc02_…request_outside_published_location` | PC-02 | C rechaza un request byte-idéntico fuera de `.cdad/packets/<packet_id>/REQUEST.json`, con referencia segura y sin efectos | …una copia del request podría representar el paquete publicado y el receptor no sabría cuál archivo es el entregado (O-2/INV-05). |
| `test_pc02_…non_canonical_context_copy` | PC-02 | C rechaza un contexto v2 en copia no canónica aunque el argumento sea byte-idéntico, indicando el localizador canónico y sin efectos | …una copia fuera de `.cdad/executions/<id>/execution.json` sería aceptada como fuente de contexto sin autoridad de ubicación (INV-03). |
| `test_pc02_…divergent_packet` | PC-02/PC-09 | C rechaza un `PACKET.md` publicado divergente (cuerpo alterado, cabecera intacta) con diagnóstico seguro que no divulga el cuerpo ni reescribe archivos | …se despacharía un paquete cuyas instrucciones no son las validadas (INV-05) o el diagnóstico filtraría contenido del encargo (§4.5). |
| `test_pc08a_validate_packet_does_not_strip_preamble` | PC-08a (§4.4, A1) | `validate-packet --packet` acepta el archivo canónico sin envoltura y RECHAZA el que antepone un preámbulo legítimo al marcador A (no elimina el preámbulo ni reescribe bytes) | …una unificación futura de comparadores haría pasar por validate-packet mensajes envueltos, ampliando la superficie de confianza sin contrato (§4.4). |
| `test_pc08a_route_c_accepts_published_preamble` | PC-08a (§4.4, A1) | la verificación publicada que usa C acepta un `PACKET.md` con preámbulo legítimo antes del único marcador A, comparando desde el marcador hasta el final y sin normalizar ni reescribir el archivo | …C rechazaría paquetes legítimos con preámbulo de runtime (falso negativo) o normalizaría los bytes del archivo publicado. |

Redacción de estado (honesta, sin RED fabricado):
- PC-01/PC-02 y PC-08a-lado-C son comportamiento AUSENTE hoy: `--route` no
  existe en el CLI (`unrecognized arguments: --route C`), por lo que esas
  pruebas fallan con `AssertionError` por ausencia de conducta, nunca por
  importación ni sintaxis.
- PC-08a-lado-`validate-packet` (rechazo de envoltura con control positivo
  canónico) está VERDE hoy: se declara REGRESIÓN (A1), no se fabrica RED.

PC-09 se asserta DENTRO de cada prueba negativa (causa distinguible, siguiente
acción/referencia esperada segura, sin divulgación del cuerpo, código de
salida no-cero y envoltura `ERROR:` conservados): no hay pruebas de
diagnóstico separadas.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from tests.test_packet_prepare import PrepareProject, run_prepare
from tests.test_role_packets import REPO_ROOT


# CLI del repo, invocado por subproceso con `--project-root` explícito.
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"

# §4.2 «Representación»: línea literal única y bloque Markdown único.
ROUTE_C_DECLARATION = "Route C — explicit file backup"
ROUTE_C_CONTRACT_KEYS = {
    "project_root",
    "packet_id",
    "execution_id",
    "execution_context",
    "request",
    "packet",
    "contract",
}

# §4.4: preámbulo legítimo de un mensaje/runtime; NO contiene marcador A.
RUNTIME_PREAMBLE = (
    "Runtime note: this preamble is transparent for the published verifier.\n\n"
)


def run_cli(
    *args: str, cwd: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )


@dataclass(frozen=True)
class Published:
    """Paquete publicado por la interfaz pública (`prepare`) en un tempdir."""

    root: Path
    state_path: Path
    packet_id: str
    request: dict
    request_path: Path
    packet_path: Path

    @property
    def execution_context_rel(self) -> str:
        return self.request["execution_context"]

    @property
    def context_path(self) -> Path:
        return self.root / self.execution_context_rel


class PublishedPacketCase(unittest.TestCase):
    """Fixture: preparación v2 real que publica el paquete en
    `.cdad/packets/<packet_id>/` con su contexto canónico v2 en
    `.cdad/executions/<execution_id>/execution.json`."""

    def publish(self, prefix: str) -> Published:
        temp = tempfile.TemporaryDirectory(prefix=prefix)
        self.addCleanup(temp.cleanup)
        root = Path(temp.name).resolve()
        project = PrepareProject(root)
        packets_dir = root / ".cdad" / "packets"
        result = run_prepare(CLI, *project.args(out_dir=packets_dir))
        self.assertEqual(
            result.returncode,
            0,
            msg="fixture: `prepare` debe publicar el paquete v2 del fixture: "
                + result.stderr.decode(errors="replace"),
        )
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        packet_id = state["active_packet"]["id"]
        packet_dir = packets_dir / packet_id
        request_path = packet_dir / "REQUEST.json"
        packet_path = packet_dir / "PACKET.md"
        self.assertTrue(
            request_path.is_file(),
            msg=f"fixture: falta el request publicado {request_path}",
        )
        self.assertTrue(
            packet_path.is_file(),
            msg=f"fixture: falta el paquete publicado {packet_path}",
        )
        request = json.loads(request_path.read_text(encoding="utf-8"))
        self.assertEqual(
            request["packet_id"],
            packet_id,
            msg="fixture: el request publicado no declara el paquete activo",
        )
        self.assertEqual(
            state["execution"]["id"],
            request["execution_id"],
            msg="fixture: state.execution no concuerda con el request",
        )
        return Published(
            root=root,
            state_path=project.state_path,
            packet_id=packet_id,
            request=request,
            request_path=request_path,
            packet_path=packet_path,
        )

    # -- rutas y bytes de control -------------------------------------------

    def route_c(self, case: Published, *extra: str) -> subprocess.CompletedProcess[str]:
        return run_cli(
            "render",
            "--project-root",
            str(case.root),
            "--request",
            str(case.request_path),
            "--route",
            "C",
            *extra,
            cwd=case.root,
        )

    def tracked_bytes(self, case: Published) -> dict[str, bytes]:
        """Archivos que §4.2 prohíbe modificar (request, paquete, estado y
        el contexto canónico resuelto)."""
        return {
            "request": case.request_path.read_bytes(),
            "packet": case.packet_path.read_bytes(),
            "state": case.state_path.read_bytes(),
            "context": case.context_path.read_bytes(),
        }

    def packet_dirs(self, case: Published) -> list[str]:
        return sorted(
            entry.name
            for entry in (case.root / ".cdad" / "packets").iterdir()
        )

    def expected_identification(self, case: Published) -> dict:
        """Objeto completo y exacto de §4.2, derivado de los archivos
        publicados (no de la implementación)."""
        request = case.request
        context = json.loads(case.context_path.read_text(encoding="utf-8"))
        state = json.loads(case.state_path.read_text(encoding="utf-8"))
        contract_path = case.root / request["contract"]["path"]
        self.assertEqual(
            hashlib.sha256(contract_path.read_bytes()).hexdigest(),
            request["contract"]["sha256"],
            msg="fixture: el digest declarado del contrato no corresponde al "
                "archivo del contrato",
        )
        # Concordancia de identidad entre request, contexto y state.
        self.assertEqual(request["execution_id"], context["execution"]["id"])
        self.assertEqual(request["execution_id"], state["execution"]["id"])
        self.assertEqual(request["packet_id"], state["active_packet"]["id"])
        return {
            "project_root": str(case.root),
            "packet_id": request["packet_id"],
            "execution_id": request["execution_id"],
            "execution_context": request["execution_context"],
            "request": case.request_path.relative_to(case.root).as_posix(),
            "packet": case.packet_path.relative_to(case.root).as_posix(),
            "contract": request["contract"],
        }

    # -- oráculos de salida C ----------------------------------------------

    def route_c_identification(
        self, result: subprocess.CompletedProcess[str]
    ) -> dict:
        """Parsea la salida C exigida por §4.2: SOLO la declaración literal y
        un único bloque ```json; devuelve el objeto."""
        self.assertEqual(
            result.returncode,
            0,
            msg="§4.2: `render --route C` debe emitir la identificación: "
                + result.stderr.strip(),
        )
        self.assertNotIn(
            "---cdad-packet-json",
            result.stdout,
            msg="§4.2: la identificación C no usa el marcador de cabecera de A",
        )
        text = result.stdout
        self.assertEqual(
            text.count(ROUTE_C_DECLARATION),
            1,
            msg="§4.2: la declaración literal debe aparecer exactamente una "
                f"vez; salida={text!r}",
        )
        lines = text.splitlines()
        self.assertTrue(lines, msg="§4.2: salida C vacía")
        self.assertEqual(
            lines[0],
            ROUTE_C_DECLARATION,
            msg="§4.2: la primera línea debe ser la declaración literal "
                f"{ROUTE_C_DECLARATION!r}; salida={text!r}",
        )
        remainder = "\n".join(lines[1:]).strip("\n")
        self.assertTrue(
            remainder.startswith("```json\n"),
            msg="§4.2: falta el bloque Markdown ```json; salida=" + repr(text),
        )
        self.assertTrue(
            remainder.endswith("\n```"),
            msg="§4.2: el bloque Markdown no cierra con ```; salida="
                + repr(text),
        )
        fences = [
            line for line in remainder.splitlines() if line.startswith("```")
        ]
        self.assertEqual(
            fences,
            ["```json", "```"],
            msg="§4.2: debe haber un ÚNICO bloque ```json y ningún otro "
                f"contenido; salida={text!r}",
        )
        payload = remainder[len("```json\n") : -len("\n```")]
        return json.loads(payload)

    def assert_rejection(
        self,
        result: subprocess.CompletedProcess[str],
        label: str,
    ) -> str:
        """Rechazo observable con PC-09: sin identificación, código no-cero,
        envoltura `ERROR:` conservada y sin traceback."""
        self.assertNotEqual(
            result.returncode,
            0,
            msg=f"{label}: C no debe emitir una identificación; rc=0 con "
                f"stdout={result.stdout!r}",
        )
        self.assertEqual(
            result.stdout,
            "",
            msg=f"{label}: el rechazo no debe dejar identificador utilizable "
                f"en stdout (obtuvo {result.stdout!r})",
        )
        stderr = result.stderr
        self.assertTrue(
            stderr.strip(), msg=f"{label}: rechazo sin diagnóstico"
        )
        self.assertTrue(
            stderr.startswith("ERROR: "),
            msg=f"{label}: se conserva la envoltura `ERROR:` existente; "
                f"stderr={stderr!r}",
        )
        self.assertNotIn(
            "Traceback",
            stderr,
            msg=f"{label}: el rechazo debe ser diagnóstico, no traceback",
        )
        self.assertNotIn(
            ROUTE_C_DECLARATION,
            stderr,
            msg=f"{label}: el rechazo no debe emitir la declaración C",
        )
        return stderr


class TestRouteCPositiveIdentification(PublishedPacketCase):
    def test_pc01_route_c_emits_only_declaration_and_exact_identification(
        self,
    ) -> None:
        """PC-01 (spec §4.2 «Representación» y «Binding con el request
        publicado»; §5 PC-01; INV-05, INV-12).

        Promesa observable: para un paquete publicado válido con contexto
        canónico v2, `render --route C` emite SOLO la declaración literal y un
        único bloque ```json con el objeto completo de §4.2 (sus siete campos
        exactos y el contrato con todos sus campos y digest); `project_root`
        absoluto, request/paquete/contexto project-relative, identificación
        concordante con los archivos y el estado, dos corridas
        byte-idénticas, sin modificar REQUEST.json, PACKET.md ni el estado.

        R4: sin esta prueba, el receptor resolvería una identificación
        incompleta, con rutas absolutas o no concordante con el paquete
        publicado: ejecutaría otro archivo o ninguno, y el encargo despachado
        no sería el validado (INV-05).

        RED hoy: `--route` no existe (`unrecognized arguments: --route C`).
        """
        case = self.publish("cdad-t3red-pc01-")
        before = self.tracked_bytes(case)

        first = self.route_c(case)
        identification = self.route_c_identification(first)
        self.assertEqual(
            set(identification),
            ROUTE_C_CONTRACT_KEYS,
            msg="§4.2: el objeto de identificación debe tener exactamente "
                f"los siete campos declarados; obtuvo {sorted(identification)}",
        )
        expected = self.expected_identification(case)
        self.assertEqual(
            identification,
            expected,
            msg="§4.2: la identificación debe ser el objeto completo y "
                "exacto derivado de los archivos publicados (prohibidos "
                "subconjuntos o aserciones de mera presencia)",
        )
        self.assertTrue(
            Path(identification["project_root"]).is_absolute(),
            msg="§4.2: `project_root` debe ser una raíz absoluta utilizable "
                f"por el receptor; obtuvo {identification['project_root']!r}",
        )
        for field, expected_rel in (
            ("request", f".cdad/packets/{case.packet_id}/REQUEST.json"),
            ("packet", f".cdad/packets/{case.packet_id}/PACKET.md"),
            (
                "execution_context",
                f".cdad/executions/{case.request['execution_id']}"
                "/execution.json",
            ),
        ):
            self.assertEqual(
                identification[field],
                expected_rel,
                msg=f"§4.2: `{field}` debe ser project-relative y designar "
                    f"el archivo publicado ({expected_rel!r})",
            )
        self.assertEqual(
            identification["contract"],
            case.request["contract"],
            msg="§4.2: el contrato debe conservar todos sus campos "
                "declarados y su digest",
        )

        second = self.route_c(case)
        self.assertEqual(
            first.stdout.encode("utf-8"),
            second.stdout.encode("utf-8"),
            msg="§4.2: para iguales archivos y raíz la salida C debe ser "
                "determinista (dos corridas byte-idénticas)",
        )
        self.assertEqual(
            self.route_c_identification(second),
            identification,
            msg="§4.2: ambas corridas deben emitir el mismo objeto",
        )
        self.assertEqual(
            self.tracked_bytes(case),
            before,
            msg="PC-01: C no debe modificar REQUEST.json, PACKET.md ni el "
                "estado (ni el contexto canónico)",
        )
        self.assertEqual(
            self.packet_dirs(case),
            [case.packet_id],
            msg="PC-01: C no debe publicar ni crear otro paquete",
        )


class TestRouteCRejections(PublishedPacketCase):
    def test_pc02_route_c_rejects_v1_context_as_v2_only(self) -> None:
        """PC-02 (spec §4.2 punto 4: «Un contexto v1 se rechaza con
        diagnóstico explícito: C requiere v2»; §4.5; §5 PC-02).

        Promesa observable: con el contexto canónico reemplazado por un
        documento v1 legítimo de la misma identidad, C no emite identificación
        utilizable; el diagnóstico nombra la ruta C y la exigencia de v2 e
        indica la continuación (preparación/bootstrap de una ejecución nueva),
        sin convertir ni reescribir el v1.

        R4: sin esta prueba, C podría identificar un paquete histórico v1 y
        despachar trabajo sobre una autoridad que la regla v2-only no admite
        (INV-08/INV-12); o el rechazo no diría cómo continuar.

        RED hoy: `--route` no existe; además el diagnóstico vigente del
        contexto v1 no nombra C.
        """
        case = self.publish("cdad-t3red-v1-")
        canonical = case.context_path
        v2_document = json.loads(canonical.read_text(encoding="utf-8"))
        v1_document = {
            "schema_version": 1,
            "execution": {
                "id": v2_document["execution"]["id"],
                "epic_id": v2_document["execution"]["epic_id"],
                "feature_id": v2_document["execution"]["feature_id"],
                "runtime": "opencode",
                "scope": v2_document["execution"]["scope"],
                "model_policy": v2_document["execution"]["model_policy"],
                "authority_ref": v2_document["execution"]["authority_ref"],
                "model": {"configured": None, "reported": None},
            },
            "path_policy": v2_document.get("path_policy", {}),
        }
        canonical.write_text(
            json.dumps(v1_document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        before = self.tracked_bytes(case)
        execution_dir = canonical.parent
        execution_entries = sorted(entry.name for entry in execution_dir.iterdir())

        stderr = self.assert_rejection(self.route_c(case), "PC-02/v1")

        self.assertRegex(
            stderr,
            r"(?i)route\s+c\b"
            r"|(?<![A-Za-z0-9_])c(?![A-Za-z0-9_])[^\n]{0,40}"
            r"(requires?|requiere|only|v2)",
            msg="PC-02: el diagnóstico de C con contexto v1 debe nombrar la "
                f"ruta C (causa distinguible, §4.5); stderr={stderr!r}",
        )
        self.assertRegex(
            stderr,
            r"(?i)(v2|schema[ _-]?version\s*2)",
            msg="PC-02: el diagnóstico debe informar que C requiere v2 "
                f"(§4.2 punto 4); stderr={stderr!r}",
        )
        self.assertRegex(
            stderr,
            r"(?i)(--new-execution|new[-_ ]execution"
            r"|new\s+(?:v2\s+)?execution|nueva\s+ejecuci[oó]n"
            r"|prepare\b|bootstrap)",
            msg="PC-02/PC-09: el diagnóstico debe ofrecer la siguiente "
                "acción pertinente para trabajo nuevo sobre legado "
                f"(§4.1/§4.5: bootstrap/prepare de una ejecución v2); "
                f"stderr={stderr!r}",
        )
        self.assertEqual(
            self.tracked_bytes(case),
            before,
            msg="PC-02: el rechazo no convierte ni reescribe el request, el "
                "paquete, el estado o el contexto v1 (INV-08), ni deja "
                "efectos persistentes",
        )
        self.assertEqual(
            sorted(entry.name for entry in execution_dir.iterdir()),
            execution_entries,
            msg="PC-02: el rechazo no debe fabricar un contexto v2 junto al "
                "v1 (§4.1: no se copia, convierte ni reubica)",
        )
        self.assertEqual(
            self.packet_dirs(case),
            [case.packet_id],
            msg="PC-02: el rechazo no debe publicar paquetes",
        )

    def test_pc02_route_c_rejects_request_outside_published_location(
        self,
    ) -> None:
        """PC-02 (spec §4.2 punto 1-2: `--request` debe designar el propio
        archivo publicado; una copia byte-idéntica no basta; §4.5; §5 PC-02).

        Promesa observable: una copia byte-idéntica del request fuera de
        `.cdad/packets/<packet_id>/REQUEST.json` no emite identificación; el
        rechazo ofrece la referencia esperada project-relative y no produce
        efectos.

        R4: sin esta prueba, una copia del request podría seleccionar o
        representar el paquete publicado y el receptor no sabría cuál
        archivo es el entregado (O-2/INV-05).

        RED hoy: `--route` no existe; el render histórico acepta cualquier
        ruta de request.
        """
        case = self.publish("cdad-t3red-copy-")
        copy_path = case.root / "REQUEST-copy.json"
        copy_path.write_bytes(case.request_path.read_bytes())
        self.assertEqual(
            copy_path.read_bytes(),
            case.request_path.read_bytes(),
            msg="fixture: la copia debe ser byte-idéntica al request publicado",
        )
        before = self.tracked_bytes(case)
        copy_before = copy_path.read_bytes()

        result = run_cli(
            "render",
            "--project-root",
            str(case.root),
            "--request",
            str(copy_path),
            "--route",
            "C",
            cwd=case.root,
        )
        stderr = self.assert_rejection(result, "PC-02/request no publicado")

        expected_reference = (
            f".cdad/packets/{case.packet_id}/REQUEST.json"
        )
        self.assertIn(
            expected_reference,
            stderr,
            msg="PC-02/PC-09: el diagnóstico debe presentar de manera segura "
            "y project-relative la referencia esperada del request publicado "
            f"({expected_reference!r}); stderr={stderr!r}",
        )
        self.assertEqual(
            copy_path.read_bytes(),
            copy_before,
            msg="PC-02: el rechazo no reescribe la copia",
        )
        self.assertEqual(
            self.tracked_bytes(case),
            before,
            msg="PC-02: el rechazo no modifica el request publicado, el "
                "paquete, el estado ni el contexto (sin efectos persistentes)",
        )
        self.assertEqual(
            self.packet_dirs(case),
            [case.packet_id],
            msg="PC-02: el rechazo no debe publicar paquetes",
        )

    def test_pc02_route_c_rejects_non_canonical_context_copy(self) -> None:
        """PC-02 (spec §4.1 matriz fila 2 —el argumento explícito debe
        resolver al mismo archivo canónico— y §4.2 punto 3; §4.5; §5 PC-02).

        Promesa observable: un contexto v2 en copia no canónica, aunque sea
        byte-idéntico y se pase con `--execution-context`, no emite
        identificación; el rechazo nombra el contexto y presenta la
        referencia canónica segura project-relative, sin efectos.

        R4: sin esta prueba, una copia fuera de
        `.cdad/executions/<id>/execution.json` sería aceptada como fuente de
        contexto, contra la autoridad de ubicación (INV-03).

        RED hoy: `--route` no existe; el render histórico sí acepta el
        argumento explícito no canónico cuando el request declara el
        localizador (el rechazo de la matriz es parte del GREEN de T2 y aquí
        se exige desde C).
        """
        case = self.publish("cdad-t3red-ctxcopy-")
        copy_path = case.root / "EXECUTION.json"
        self.assertTrue(
            copy_path.is_file(),
            msg="fixture: debe existir la copia ROOT/EXECUTION.json del "
                "portador v2",
        )
        self.assertEqual(
            copy_path.read_bytes(),
            case.context_path.read_bytes(),
            msg="fixture: la copia debe ser byte-idéntica al contexto "
                "canónico (el rechazo no puede basarse en bytes distintos)",
        )
        before = self.tracked_bytes(case)
        copy_before = copy_path.read_bytes()

        result = run_cli(
            "render",
            "--project-root",
            str(case.root),
            "--execution-context",
            str(copy_path),
            "--request",
            str(case.request_path),
            "--route",
            "C",
            cwd=case.root,
        )
        stderr = self.assert_rejection(result, "PC-02/contexto no canónico")

        canonical_reference = (
            f".cdad/executions/{case.request['execution_id']}/execution.json"
        )
        self.assertRegex(
            stderr,
            r"(?i)(execution context|contexto de ejecuci[oó]n)",
            msg="PC-02/PC-09: el diagnóstico debe distinguir la causa de "
                f"contexto (§4.5); stderr={stderr!r}",
        )
        self.assertIn(
            canonical_reference,
            stderr,
            msg="PC-02/PC-09: el diagnóstico debe presentar la referencia "
                f"canónica segura project-relative ({canonical_reference!r}); "
                f"stderr={stderr!r}",
        )
        self.assertEqual(
            copy_path.read_bytes(),
            copy_before,
            msg="PC-02: el rechazo no reescribe la copia del contexto",
        )
        self.assertEqual(
            self.tracked_bytes(case),
            before,
            msg="PC-02: el rechazo no modifica request, paquete, estado ni "
                "contexto (sin efectos persistentes)",
        )
        self.assertEqual(
            self.packet_dirs(case),
            [case.packet_id],
            msg="PC-02: el rechazo no debe publicar paquetes",
        )

    def test_pc02_route_c_rejects_divergent_published_packet(self) -> None:
        """PC-02/PC-09 (spec §4.2 punto 6 —verificación del `PACKET.md`
        publicado completo—, §4.5 «no se imprimen fragmentos del cuerpo»;
        §5 PC-02/PC-09; INV-05).

        Promesa observable: un `PACKET.md` publicado divergente (cuerpo
        alterado, cabecera intacta) no emite identificación; el diagnóstico
        distingue la causa de divergencia sin divulgar el contenido añadido y
        el rechazo no reescribe el paquete ni produce efectos.

        R4: sin esta prueba, C podría identificar un paquete cuyas
        instrucciones no son las validadas (INV-05), o el diagnóstico
        filtraría el cuerpo del encargo (§4.5).

        RED hoy: `--route` no existe; el render histórico no verifica el
        paquete publicado.
        """
        case = self.publish("cdad-t3red-divergent-")
        tampered_marker = "tampered-body-line-not-part-of-the-contract"
        original = case.packet_path.read_bytes()
        self.assertTrue(
            original.startswith(b"---cdad-packet-json\n"),
            msg="fixture: el paquete publicado debe comenzar con el marcador A",
        )
        case.packet_path.write_bytes(
            original + tampered_marker.encode("utf-8") + b"\n"
        )
        before = self.tracked_bytes(case)

        stderr = self.assert_rejection(self.route_c(case), "PC-02/divergente")

        self.assertRegex(
            stderr,
            r"(?i)(?<![A-Za-z0-9_])packet(?!\.py)[^\n]{0,60}"
            r"(differ|diverg|match|can[oó]nic)"
            r"|(differ|diverg|match|can[oó]nic)[^\n]{0,60}"
            r"(?<![A-Za-z0-9_])packet(?!\.py)",
            msg="PC-02/PC-09: el diagnóstico debe distinguir la causa de "
                f"divergencia del paquete publicado; stderr={stderr!r}",
        )
        self.assertNotIn(
            tampered_marker,
            stderr,
            msg="PC-09: el diagnóstico no debe imprimir fragmentos del "
                "cuerpo divergente",
        )
        # PC-09: tampoco fragmentos del cuerpo original ni del marcador A.
        for fragment in (
            "cdad-instructions",
            "cdad-packet-json",
            "Prepare objective",
        ):
            self.assertNotIn(
                fragment,
                stderr,
                msg="PC-09: el diagnóstico de divergencia no debe divulgar "
                    f"el cuerpo del encargo (fragmento {fragment!r}); "
                    f"stderr={stderr!r}",
            )
        self.assertEqual(
            self.tracked_bytes(case),
            before,
            msg="PC-02: el rechazo no modifica request, estado ni contexto; "
                "tampoco reescribe ni normaliza el PACKET.md divergente",
        )
        self.assertEqual(
            self.packet_dirs(case),
            [case.packet_id],
            msg="PC-02: el rechazo no debe publicar paquetes",
        )


class TestPC08aPreambleBoundary(PublishedPacketCase):
    def test_pc08a_validate_packet_does_not_strip_preamble(self) -> None:
        """PC-08a (spec §4.4 tabla: `validate-packet --packet` compara el
        archivo suministrado completo y NO elimina preámbulo; A1 los cubre en
        T3; §5 PC-08a).

        Promesa observable: el archivo canónico sin envoltura PASA
        `validate-packet`, y un archivo que antepone un preámbulo legítimo al
        marcador A se RECHAZA (la comparación es del archivo completo); el
        archivo no se reescribe.

        R4: sin esta prueba, una unificación futura de comparadores haría
        pasar por `validate-packet` mensajes envueltos por el runtime,
        ampliando la superficie de confianza sin contrato (§4.4).

        ESTADO: REGRESIÓN verde hoy (A1: no se fabrica RED para una garantía
        existente). El control positivo (canónico aceptado) impide que el
        rechazo sea universal.
        """
        case = self.publish("cdad-t3red-preamble-validate-")
        common_args = (
            "validate-packet",
            "--project-root",
            str(case.root),
            "--execution-context",
            str(case.context_path),
            "--request",
            str(case.request_path),
        )
        canonical = run_cli(
            *common_args,
            "--packet",
            str(case.packet_path),
            cwd=case.root,
        )
        self.assertEqual(
            canonical.returncode,
            0,
            msg="PC-08a (control positivo): el archivo canónico sin envoltura "
                "debe pasar `validate-packet`: " + canonical.stderr.strip(),
        )

        wrapped_path = case.root / "PACKET-wrapped.md"
        wrapped_bytes = RUNTIME_PREAMBLE.encode("utf-8") + case.packet_path.read_bytes()
        wrapped_path.write_bytes(wrapped_bytes)
        self.assertEqual(
            wrapped_bytes.count(b"---cdad-packet-json"),
            1,
            msg="fixture: el archivo envuelto conserva un único marcador A",
        )

        wrapped = run_cli(
            *common_args,
            "--packet",
            str(wrapped_path),
            cwd=case.root,
        )
        self.assertNotEqual(
            wrapped.returncode,
            0,
            msg="PC-08a (§4.4): `validate-packet` compara el archivo completo "
                "y NO debe eliminar el preámbulo; un archivo envuelto no debe "
                "pasar",
        )
        self.assertEqual(
            wrapped.stdout,
            "",
            msg="PC-08a: el rechazo de `validate-packet` no publica stdout",
        )
        self.assertTrue(
            wrapped.stderr.strip(),
            msg="PC-08a: el rechazo de `validate-packet` debe diagnosticar",
        )
        self.assertEqual(
            wrapped_path.read_bytes(),
            wrapped_bytes,
            msg="PC-08a (§4.4): `validate-packet` no reescribe ni normaliza "
                "el archivo suministrado (no elimina el preámbulo)",
        )

    def test_pc08a_route_c_accepts_published_packet_with_legitimate_preamble(
        self,
    ) -> None:
        """PC-08a (spec §4.4 tabla: la verificación publicada usada por C
        compara desde el ÚNICO marcador A del archivo publicado hasta su
        final; el preámbulo anterior es transparente; sin normalizar bytes;
        A1; §5 PC-08a).

        Promesa observable: con un preámbulo legítimo antepuesto al único
        marcador A del `PACKET.md` publicado, `render --route C` acepta y
        emite la misma identificación exacta que sin preámbulo; el archivo
        conserva sus bytes (no se normaliza ni se reescribe).

        R4: sin esta prueba, C rechazaría paquetes legítimos con preámbulo de
        runtime (falso negativo) o normalizaría los bytes del archivo
        publicado, perdiendo la frontera de §4.4.

        RED hoy: `--route` no existe; el comportamiento de aceptación desde
        el marcador es nuevo en esta superficie.
        """
        case = self.publish("cdad-t3red-preamble-c-")
        expected = self.expected_identification(case)
        original = case.packet_path.read_bytes()
        wrapped_bytes = RUNTIME_PREAMBLE.encode("utf-8") + original
        case.packet_path.write_bytes(wrapped_bytes)
        self.assertEqual(
            wrapped_bytes.count(b"---cdad-packet-json"),
            1,
            msg="fixture: el archivo publicado conserva un único marcador A",
        )
        before = {
            "request": case.request_path.read_bytes(),
            "state": case.state_path.read_bytes(),
            "context": case.context_path.read_bytes(),
        }

        result = self.route_c(case)
        identification = self.route_c_identification(result)
        self.assertEqual(
            identification,
            expected,
            msg="PC-08a (§4.4): C debe aceptar el paquete publicado con "
                "preámbulo legítimo y emitir la misma identificación exacta "
                "que sin preámbulo (comparación desde el marcador A hasta el "
                "final)",
        )
        self.assertEqual(
            case.packet_path.read_bytes(),
            wrapped_bytes,
            msg="PC-08a (§4.4): C no debe normalizar ni reescribir el "
                "PACKET.md publicado: el preámbulo y los bytes se conservan",
        )
        self.assertEqual(
            {
                "request": case.request_path.read_bytes(),
                "state": case.state_path.read_bytes(),
                "context": case.context_path.read_bytes(),
            },
            before,
            msg="PC-08a: la aceptación C no debe modificar request, estado ni "
                "contexto",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
