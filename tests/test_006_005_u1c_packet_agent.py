#!/usr/bin/env python3
"""006-005 U1c RED — el agente viaja en el paquete (PD-7).

Contract: `docs/specs/006-005-native-path-parity/spec.md` (aprobado, sha256
3a824be3…): §2.7 (el agente viaja en el paquete, D-ADP-4), PD-7 (§3), INV-13
(§4) y D-13 (§10). Plan: la ficha U1c (`plan.md` §3) y su bloque `plan-tasks`
(focal `tests/test_006_005_u1c_packet_agent.py`; regresiones de la ficha).

Disciplina de oráculo (caja negra). El CLI del skill
(`scripts/cdad_packet.py`, envoltorio fino del producto) se invoca como
SUBPROCESO contra un proyecto descartable creado por el propio fixture
(`tests/test_packet_prepare.py::PrepareProject`); nunca se importa ni se lee
ningún archivo de implementación (`skills/cdad-cycle/scripts/**`). Lo observado
son efectos publicados: rc, stdout/stderr, los bytes de `PACKET.md`, el
documento `REQUEST.json` y el recibo durable del comando `receive` (la
superficie existente). Ningún fixture toca el repo real ni el HOME real.

INTERFAZ DECLARADA POR ESTE TEST (la satisface el implementer leyendo este
test; el test-writer no ve el código y la spec §2.7 deja libre la mecánica
dentro del contrato fijado):

1. `prepare` resuelve el agente del paquete con **rol + `stack` del estado**
   (`docs/.cdad-state.json.stack`) y lo escribe en `REQUEST.json` como campo
   `agent`:
     * `stack` presente (p. ej. `"odoo"`) ⇒ `cdad-<rol>-<stack>`
       (`cdad-test-writer-odoo`, `cdad-reviewer-odoo`);
     * `stack` `null` **o ausente** ⇒ `cdad-<rol>` (`cdad-test-writer`).
2. `agent` es una **propiedad opcional declarada** del documento del request:
   el conjunto cerrado de campos de `validate_request` lo admite y **sigue
   rechazando cualquier otra clave** (el mismo patrón con que 005-003 sumó
   `plan_task`). El rechazo es por rc≠0, sin publicar nada.
3. `agent` **no entra al render**: los bytes de `PACKET.md` son idénticos con y
   sin el campo (y su metadata no lo declara).
4. Un paquete sin `agent` —la forma de los publicados antes de esta feature—
   sigue siendo **recibible**: `receive` rc=0 y recibo durable escrito. Como el
   render no cambia (punto 3), la forma pre-feature se reconstruye con fidelidad
   quitándole al request publicado el campo opcional declarado.

Mapeo test → postcondición (un test por oráculo de PD-7):

  test_pd7_agent_is_role_plus_stack_of_the_state
      -> PD-7 (con `stack` el agente es `cdad-<rol>-<stack>`)
  test_pd7_agent_without_stack_falls_back_to_the_role_agent
      -> PD-7 (sin `stack` —`null` o ausente— el agente es `cdad-<rol>`)
  test_pd7_request_with_agent_validates_and_unknown_keys_stay_rejected
      -> PD-7 (propiedad opcional declarada; el conjunto cerrado no se relaja)
  test_pd7_agent_does_not_enter_the_packet_render
      -> PD-7 (bytes de `PACKET.md` idénticos con y sin `agent`)
  test_pd7_pre_feature_packet_without_agent_is_still_received
      -> PD-7 (`receive` rc=0 sobre el paquete sin el campo)

DEPENDENCIA DECLARADA (aquí no se escribe ningún test que falle por ella):
* El caso «`stack` con agente **no publicado**» (`--agent
  cdad-<rol>-odoo` cuando ese derivado no existe ⇒ el módulo falla cerrado
  antes de despachar, PD-14) es superficie de U2: el módulo del runtime traduce
  el campo y falla cerrado. U1c sólo publica el campo; no hay test que lo
  afirme aquí.

REGLA A-1 (test acoplado a la superficie que esta unidad cambia; el reemplazo
se declara y se hace EN ESTE RED, nunca en GREEN — `plan.md` §4):

* `tests/test_packet_prepare.py::TestPrepareDefaults::
  test_p2_default_request_derivations_per_role` fija el documento EXACTO de
  `REQUEST.json` (igualdad de diccionario completo) y por eso la nueva
  conducta lo rompe.
  REEMPLAZADO POR: la misma igualdad exacta —el conjunto de claves del request
  sigue cerrado— con el campo declarado `agent` presente, derivado del `stack`
  del estado del fixture (`stack: null` ⇒ `cdad-<rol>`).
  POSTCONDICIÓN NUEVA: PD-7 (§2.7) — `prepare` escribe `agent` = rol + `stack`
  del estado.
  RAZÓN: el oráculo de esa prueba es el documento completo del request; la
  extensión declarada del conjunto cerrado (PD-7) cambia ese documento, así que
  el valor esperado se actualiza sin relajar el oráculo. Los demás oráculos de
  esa prueba (derivaciones por rol, scopes, invariantes, contrato) no cambian.

RED hoy esperado (declarado, no accidental): `prepare` no resuelve el `stack`
ni escribe `agent`, así que cada prueba focal falla en su PRIMERA aserción de
comportamiento (`request.get("agent")` es `None`, con el mensaje de PD-7). El
caso de compatibilidad (`receive` sin el campo) también falla primero ahí —no
en `receive`— porque el campo declarado todavía no se publica. Ningún fallo es
ImportError, SyntaxError, JSONDecodeError ni error de E/S del fixture.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.test_003_002_t1_receive import STAGED_PARTS, EstablishedProjectCase
from tests.test_packet_prepare import (
    PACKET_CLI,
    PrepareProject,
    run_cli_bytes,
    run_prepare,
)
from tests.test_role_packet_render import parse_packet

# Centinelas del fixture: `stack` nulo es un valor del estado; «ausente» es la
# ausencia de la clave (las dos formas que PD-7 declara equivalentes).
STACK_ABSENT = object()

AGENT_WITH_STACK = {
    ("test-writer", "red", "odoo"): "cdad-test-writer-odoo",
    ("reviewer", "review", "odoo"): "cdad-reviewer-odoo",
}


class PacketAgentCase(unittest.TestCase):
    """Proyecto descartable cuyo `stack` de estado fija cada subcaso."""

    maxDiff = None

    def project(
        self,
        role: str = "test-writer",
        substage: str = "red",
        *,
        stack: object = None,
    ) -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-u1c-agent-")
        self.addCleanup(temp.cleanup)
        project = PrepareProject(Path(temp.name).resolve(), role, substage)
        self.apply_stack(project, stack)
        return project

    def apply_stack(self, project: PrepareProject, stack: object) -> None:
        """Fija el `stack` del estado del fixture (`None`, un valor o ausente)."""
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        if stack is STACK_ABSENT:
            state.pop("stack", None)
        else:
            state["stack"] = stack
        project.pre_state = state
        project.state_path.write_text(
            json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")

    def prepare_ok(self, project: PrepareProject) -> None:
        result = run_prepare(PACKET_CLI, *project.args())
        self.assertEqual(
            result.returncode,
            0,
            msg="precondición (fixture): `prepare` debe publicar el paquete: "
                + result.stderr.decode(errors="replace"),
        )

    def request_of(self, project: PrepareProject) -> dict:
        path = project.out_dir / project.packet_id() / "REQUEST.json"
        self.assertTrue(path.is_file(), msg=f"prepare no publicó {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def validate_request(self, project: PrepareProject, request_path: Path):
        return run_cli_bytes(
            PACKET_CLI,
            "validate-request",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
            "--request",
            str(request_path),
        )

    def agent_or_fail(self, project: PrepareProject) -> str:
        """PD-7: el request publicado declara el agente del paquete."""
        request = self.request_of(project)
        agent = request.get("agent")
        self.assertIsNotNone(
            agent,
            msg="PD-7 violada (§2.7/D-13): el REQUEST.json publicado no lleva "
                "el campo declarado `agent` (el agente no viaja en el paquete): "
                f"{sorted(request)}",
        )
        return agent


class TestAgentIsRolePlusStack(PacketAgentCase):
    def test_pd7_agent_is_role_plus_stack_of_the_state(self) -> None:
        """PD-7: con `stack` en el estado, `agent` = `cdad-<rol>-<stack>`."""
        for (role, substage, stack), expected in AGENT_WITH_STACK.items():
            with self.subTest(role=role, substage=substage, stack=stack):
                project = self.project(role, substage, stack=stack)
                self.prepare_ok(project)
                self.assertEqual(
                    self.agent_or_fail(project),
                    expected,
                    msg="PD-7 violada (§2.7): el agente del paquete debe "
                        f"resolverse con rol + `stack` del estado: {expected!r}",
                )

    def test_pd7_agent_without_stack_falls_back_to_the_role_agent(self) -> None:
        """PD-7: sin `stack` (`null` o ausente), `agent` = `cdad-<rol>`."""
        for label, stack in (("null", None), ("ausente", STACK_ABSENT)):
            with self.subTest(stack=label):
                project = self.project(stack=stack)
                self.prepare_ok(project)
                self.assertEqual(
                    self.agent_or_fail(project),
                    "cdad-test-writer",
                    msg="PD-7 violada (§2.7): sin `stack` el agente del paquete "
                        "debe ser `cdad-<rol>`",
                )


class TestRequestFieldSetStaysClosed(PacketAgentCase):
    def test_pd7_request_with_agent_validates_and_unknown_keys_stay_rejected(
        self,
    ) -> None:
        """PD-7: `agent` es una propiedad opcional DECLARADA (valida) y el
        conjunto cerrado de campos del request NO se relaja (una clave
        desconocida sigue rechazándose)."""
        project = self.project(stack="odoo")
        self.prepare_ok(project)
        request_path = project.out_dir / project.packet_id() / "REQUEST.json"
        self.assertEqual(
            self.agent_or_fail(project),
            "cdad-test-writer-odoo",
            msg="PD-7 violada (§2.7): el agente del paquete con `stack: odoo`",
        )

        declared = self.validate_request(project, request_path)
        self.assertEqual(
            declared.returncode,
            0,
            msg="PD-7 violada (§2.7/INV-13): el campo opcional DECLARADO "
                "`agent` no valida (el conjunto cerrado del request no lo "
                "admite): " + declared.stderr.decode(errors="replace"),
        )

        mutated = dict(self.request_of(project))
        mutated["unknown_key_outside_the_closed_set"] = 1
        mutated_path = project.root / "mutated-request.json"
        mutated_path.write_text(
            json.dumps(mutated, ensure_ascii=False) + "\n", encoding="utf-8")
        rejected = self.validate_request(project, mutated_path)
        self.assertNotEqual(
            rejected.returncode,
            0,
            msg="PD-7 violada (§2.7): se relajó el cierre de campos del request "
                "(una clave desconocida fue aceptada)",
        )


class TestAgentDoesNotEnterTheRender(PacketAgentCase):
    def test_pd7_agent_does_not_enter_the_packet_render(self) -> None:
        """PD-7: los bytes de `PACKET.md` son idénticos con y sin `agent`, y su
        metadata no declara el campo."""
        project = self.project(stack="odoo")
        self.prepare_ok(project)
        packet_dir = project.out_dir / project.packet_id()
        published = (packet_dir / "PACKET.md").read_bytes()
        request_path = packet_dir / "REQUEST.json"
        request = self.request_of(project)
        self.assertEqual(
            request.get("agent"),
            "cdad-test-writer-odoo",
            msg="PD-7 violada (§2.7): el request publicado debe declarar el "
                "agente del paquete antes de comparar el render",
        )

        without = dict(request)
        without.pop("agent")
        without_path = project.root / "request-without-agent.json"
        without_path.write_text(
            json.dumps(without, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        common = [
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
        ]
        with_agent = run_cli_bytes(
            PACKET_CLI, "render", *common, "--request", str(request_path))
        without_agent = run_cli_bytes(
            PACKET_CLI, "render", *common, "--request", str(without_path))
        self.assertEqual(
            with_agent.returncode,
            0,
            msg="precondición (fixture): `render` debe aceptar el request "
                "publicado: " + with_agent.stderr.decode(errors="replace"),
        )
        self.assertEqual(
            without_agent.returncode,
            0,
            msg="PD-7 violada (§2.7): el request sin el campo DECLARADO "
                "`agent` debe seguir renderizando: "
                + without_agent.stderr.decode(errors="replace"),
        )
        self.assertEqual(
            with_agent.stdout,
            published,
            msg="precondición (fixture): stdout de `render` debe ser el "
                "`PACKET.md` publicado",
        )
        self.assertEqual(
            without_agent.stdout,
            published,
            msg="PD-7 violada (§2.7): `agent` entró al render — los bytes de "
                "`PACKET.md` difieren con y sin el campo",
        )
        metadata, _, _ = parse_packet(published.decode("utf-8"))
        self.assertNotIn(
            "agent",
            metadata,
            msg="PD-7 violada (§2.7): la metadata del paquete declara `agent` "
                f"(el render debe usar su lista explícita de claves): "
                f"{sorted(metadata)}",
        )


class TestPreFeaturePacketIsStillReceived(EstablishedProjectCase):
    def test_pd7_pre_feature_packet_without_agent_is_still_received(self) -> None:
        """PD-7: un paquete publicado sin `agent` (la forma pre-feature) sigue
        siendo recibible —`receive` rc=0 y recibo durable—.

        La forma pre-feature se reconstruye quitándole al request publicado el
        campo opcional declarado; es fiel porque el render no cambia con el
        campo (el oráculo de bytes de PD-7 en esta misma unidad)."""
        self.new_dispatched_project()
        request = json.loads(self.request_path.read_text(encoding="utf-8"))
        self.assertIn(
            "agent",
            request,
            msg="PD-7 violada (§2.7/D-13): `prepare` no publicó el campo "
                f"declarado `agent` en el REQUEST.json del paquete: "
                f"{sorted(request)}",
        )
        request.pop("agent")
        self.request_path.write_text(
            json.dumps(request, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        parts = self.write_staged_parts()
        self.assertEqual(parts, STAGED_PARTS)
        self.write_manifest(changes=[])
        descriptor = self.write_descriptor(
            self.build_descriptor(parts=parts, observed=self.observed_changes())
        )
        proc = self.run_receive(descriptor)
        self.assertEqual(
            proc.returncode,
            0,
            msg="PD-7 violada (§2.7): `receive` debe seguir recibiendo un "
                "paquete sin `agent` (publicado antes de la feature): "
                + proc.stderr.decode("utf-8", errors="replace"),
        )
        self.assertTrue(
            self.receipt_path().is_file(),
            msg="PD-7 violada (§2.7): el paquete sin `agent` debe producir "
                "recibo durable",
        )


if __name__ == "__main__":
    raise SystemExit(unittest.main())
