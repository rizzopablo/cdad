#!/usr/bin/env python3
"""RED 010-004 T6 — remediación de B2 y B4 (archivo NUEVO, dos pruebas).

Contrato: `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`
(pin `fc6b2ccc…`). `spec.md:205`, `:222` y `:352` fijan el resultado
observable ÚNICO ante un paquete v1 activo no terminal —incluido
`prepared`—: diagnosticar el bloqueo y la ausencia de una ruta CLI
terminal existente, escalar al owner, dejar el state intacto y no
preparar v1; prohíben indicar «completar o fallar» como procedimiento y
dicen que `--new-execution` no elude el bloqueo. `spec.md:462` exige
comprobar la incorporación del campo/localizador en las generaciones
nuevas afectadas; PC-04 (`spec.md:406`) fija que un sucesor nuevo declara
el localizador canónico aunque el predecesor histórico no lo declarara.

El CLI DEL PRODUCTO del repo (`skills/cdad-cycle/scripts/cdad_packet.py`)
se ejercita como SUBPROCESO, caja negra: este archivo no importa ni lee
`skills/`, `scripts/`, `sources/`, `agents/` ni `build/`. Todas las
fixtures viven en directorios temporales (`tempfile`), nunca en el árbol
del repo.

Trazabilidad test → PC → consecuencia de usuario (R4):

| Test | PC | Promesa observable | R4: sin este test el usuario… |
|---|---|---|---|
| `test_b2_…` | PC-07b / spec `:205`,`:222`,`:352` | Con un paquete v1 activo `prepared`, `prepare` y `prepare --new-execution` diagnostican el bloqueo nombrando el paquete, la ausencia de ruta CLI terminal y la escalación al owner, sin ofrecer «completar o fallar» y sin tocar state ni publicar v1 | …sigue la indicación que hoy recibe (`prepare --new-execution`), choca con «complete or fail it» —una orden que la spec prohíbe— y termina en un callejón sin salida, sin ningún paso que escale al owner (bloqueante B2). |
| `test_b4_…` | PC-04 / spec `:462` | `prepare --replace-packet` publica un sucesor que declara el localizador canónico en su request y en la cabecera de su paquete aunque el predecesor histórico no lo declarara, sin reescribir el predecesor | …si esa línea del producto se rompe, el sucesor se publica sin localizador y aun así pasa con `--execution-context` explícito: el defecto no se ve hasta el gate del padre, o no se ve (bloqueante B4). |

RED de hoy (medido con sondas caja-negra, no leído del producto):
- `test_b2_…` falla con `AssertionError` en la aserción del id del
  paquete para el primer comando: hoy `prepare` ofrece
  `prepare --new-execution` sin nombrar el paquete que bloquea, y
  `prepare --new-execution` responde «complete or fail it».
- `test_b4_…` pasa hoy: es una guarda de una capacidad EXISTENTE. La
  exigencia del contrato era la prueba faltante (B4), no un cambio de
  conducta; se declara como tal en el informe, no se debilita.
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
# El CLI DEL PRODUCTO (la copia del repo que el despacho declara como fuente
# de verdad); se INVOCA, su código nunca se lee.
PRODUCT_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"

EPIC_ID = "epic-010-documentary-specialization"
FEATURE_ID = "010-004-packet-dispatch-ergonomics"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
EXECUTION_ID = "exec-010-004-t6-fixture-001"
CANONICAL_LOCATOR = f".cdad/executions/{EXECUTION_ID}/execution.json"
POLICY_PATH = "docs/cdad-policy.json"
STATE_PATH = "docs/.cdad-state.json"
CONTRACT_PATH = f"docs/specs/{FEATURE_ID}/spec.md"
LEGACY_PACKET_ID = "legacy-v1-packet"
LEGACY_EXECUTION_ID = "exec-legacy-v1"

PACKET_BEGIN = "---cdad-packet-json\n"
PACKET_END = "\n---end-cdad-packet-json\n"


def header_metadata(packet_text: str) -> dict:
    """El bloque canónico de metadatos del paquete, como objeto JSON."""
    if not packet_text.startswith(PACKET_BEGIN) or PACKET_END not in packet_text:
        raise AssertionError("el paquete no tiene el bloque canónico de metadatos")
    metadata_text, _body = packet_text[len(PACKET_BEGIN) :].split(PACKET_END, 1)
    return json.loads(metadata_text)


def tree_digests(root: Path) -> dict[str, str | None]:
    """Cada entrada bajo root: archivos → sha256, directorios → None."""
    digests: dict[str, str | None] = {}
    for path in sorted(root.rglob("*")):
        key = path.relative_to(root).as_posix()
        digests[key] = (
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        )
    return digests


class T6Project:
    """Proyecto sintético descartable: política REAL del repo (`docs/cdad-policy.json`),
    contrato mínimo, autoridad HITL y contexto v2 canónico. La raíz vive en un
    directorio temporal; el árbol del repo nunca se escribe."""

    def __init__(self, root: Path) -> None:
        self.root = root
        for rel in ("tests", "src", "lib", "docs"):
            (root / rel).mkdir(parents=True, exist_ok=True)
        self.policy_bytes = (REPO_ROOT / POLICY_PATH).read_bytes()
        (root / POLICY_PATH).write_bytes(self.policy_bytes)
        self.contract = root / CONTRACT_PATH
        self.contract.parent.mkdir(parents=True, exist_ok=True)
        self.contract.write_bytes(b"# Contrato fixture T6 (010-004)\n")
        self.authority = root / AUTHORITY_REF
        self.authority.parent.mkdir(parents=True, exist_ok=True)
        self.authority.write_text("# Autoridad fixture T6\n", encoding="utf-8")

    # -- documentos -------------------------------------------------------

    def state_document(self) -> dict:
        """State con los registros de autoridad vigentes (aprobación pineada
        del contrato, delegación HITL) y SIN binding ni paquete activo: todo
        binding observado después lo escribió el CLI."""
        return {
            "version": 1,
            "stack": None,
            "active_epic": EPIC_ID,
            "epic_stage": "features-loop",
            "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
            "epic_history": [],
            "active_feature": FEATURE_ID,
            "current_stage": "tdd",
            "tdd_substage": "red",
            "audit_status": "approved",
            "postconditions_status": {},
            "stage_history": [
                {
                    "feature": FEATURE_ID,
                    "stage": "specification",
                    "approved_by": "Pablo",
                    "approved_at": "2026-10-20T00:00:00Z",
                    "contract_path": CONTRACT_PATH,
                    "contract_sha256": hashlib.sha256(
                        self.contract.read_bytes()
                    ).hexdigest(),
                }
            ],
            "approver": "Pablo",
            "last_updated": "2026-10-20T00:00:00Z",
            "execution": None,
            "active_packet": None,
            "hitl_delegation": {
                "status": "active",
                "epic_id": EPIC_ID,
                "source": AUTHORITY_REF,
                "scope": EPIC_ID,
                "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
            },
        }

    def write_state(self, state: dict | None = None) -> None:
        path = self.root / STATE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        document = self.state_document() if state is None else state
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def read_state(self) -> dict:
        return json.loads((self.root / STATE_PATH).read_text(encoding="utf-8"))

    def state_bytes(self) -> bytes:
        return (self.root / STATE_PATH).read_bytes()

    def write_v2_context(self) -> Path:
        """Contexto v2 canónico en `.cdad/executions/<execution_id>/execution.json`
        (la ubicación que PC-04 declara), con la política real del repo."""
        policy_sha = hashlib.sha256(self.policy_bytes).hexdigest()
        policy_doc = json.loads(self.policy_bytes)
        snapshot = base64.b64encode(self.policy_bytes).decode("ascii")
        document = {
            "schema_version": 2,
            "execution": {
                "id": EXECUTION_ID,
                "epic_id": EPIC_ID,
                "feature_id": FEATURE_ID,
                "scope": EPIC_ID,
                "model_policy": "ordinary",
                "authority_ref": AUTHORITY_REF,
                "policy_sha256": policy_sha,
            },
            "path_policy": policy_doc["path_policy"],
            "policy": {
                "path": POLICY_PATH,
                "schema_version": 1,
                "sha256": policy_sha,
                "snapshot": snapshot,
            },
            "policy_history": [{"sha256": policy_sha, "snapshot": snapshot}],
        }
        canonical = self.root / CANONICAL_LOCATOR
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8"
        )
        self.write_state()
        return canonical

    def write_v1_context(self) -> Path:
        """Contexto v1 histórico en `.cdad/execution.json` (schema_version 1)."""
        document = {
            "schema_version": 1,
            "execution": {
                "id": LEGACY_EXECUTION_ID,
                "epic_id": EPIC_ID,
                "feature_id": FEATURE_ID,
                "runtime": "opencode",
                "scope": "legacy-scope",
                "model_policy": "ordinary",
                "authority_ref": AUTHORITY_REF,
                "model": {"configured": None, "reported": None},
            },
            "path_policy": {
                "test_roots": ["tests"],
                "implementation_roots": ["src", "lib"],
                "documentation_roots": ["docs"],
            },
        }
        legacy = self.root / ".cdad" / "execution.json"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.write_state()
        return legacy

    def publish_legacy_active_packet(self) -> str:
        """Publica el paquete v1 activo `prepared` en
        `.cdad/packets/<id>/{REQUEST.json,PACKET.md}`, con la forma histórica:
        su request NO declara `execution_context`."""
        contract_sha = hashlib.sha256(self.contract.read_bytes()).hexdigest()
        request = {
            "schema_version": 1,
            "packet_id": LEGACY_PACKET_ID,
            "execution_id": LEGACY_EXECUTION_ID,
            "feature_id": FEATURE_ID,
            "role": "test-writer",
            "substage": "red",
            "objective": "paquete legacy v1 activo (fixture T6)",
            "contract": {
                "kind": "approved-feature-spec",
                "path": CONTRACT_PATH,
                "sha256": contract_sha,
                "commit": None,
            },
            "inputs": [{"path": CONTRACT_PATH, "purpose": "approved contract"}],
            "read_scope": [{"class": "contract", "root": f"docs/specs/{FEATURE_ID}"}],
            "write_scope": [{"class": "tests", "root": "tests"}],
            "invariants": ["paquete legacy v1 (fixture T6)"],
            "expected_output": "registro legacy v1",
            "evidence_required": ["command"],
        }
        packet_dir = self.packet_dir(LEGACY_PACKET_ID)
        packet_dir.mkdir(parents=True, exist_ok=True)
        (packet_dir / "REQUEST.json").write_text(
            json.dumps(request, indent=2) + "\n", encoding="utf-8"
        )
        (packet_dir / "PACKET.md").write_text(
            PACKET_BEGIN
            + json.dumps(request, sort_keys=True)
            + PACKET_END
            + "# Legacy v1 packet (fixture T6)\n",
            encoding="utf-8",
        )
        state = self.read_state()
        state["active_packet"] = {
            "id": LEGACY_PACKET_ID,
            "role": "test-writer",
            "substage": "red",
            "status": "prepared",
            "packet_version": 1,
            "contract_kind": "approved-feature-spec",
            "contract_sha256": contract_sha,
        }
        self.write_state(state)
        return LEGACY_PACKET_ID

    # -- invocaciones -----------------------------------------------------

    def prepare(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(PRODUCT_CLI),
                "prepare",
                "--project-root",
                str(self.root),
                *args,
            ],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )

    def publish_predecessor(self) -> str:
        """Publica un predecesor `prepared` por la vía pública de preparación
        (contexto v2 canónico, sin opciones de otro sub-modo)."""
        proc = self.prepare(
            "--execution-context",
            str(self.root / CANONICAL_LOCATOR),
            "--role",
            "test-writer",
            "--substage",
            "red",
            "--objective",
            "predecesor prepared (fixture T6)",
        )
        if proc.returncode != 0:
            raise AssertionError(
                "fixture: la preparación del predecesor falló: "
                f"{proc.stdout!r} {proc.stderr!r}"
            )
        return self.active_packet_id()

    def replace(self, packet_id: str, reason: str) -> subprocess.CompletedProcess[str]:
        """`--replace-packet` con argv PURO: ningún flag de otro sub-modo."""
        return self.prepare("--replace-packet", packet_id, "--reason", reason)

    # -- mutaciones de fixture -------------------------------------------

    def outdate_contract(self) -> None:
        """Obsolescencia verificable (PD-8a): cambian los bytes del contrato y
        el registro `specification` se re-pinea a los bytes vigentes (el
        orquestador registra la aprobación; el test no finge autoridad)."""
        self.contract.write_bytes(b"# Contrato fixture T6 (revision vigente)\n")
        current = hashlib.sha256(self.contract.read_bytes()).hexdigest()
        state = self.read_state()
        for entry in state.get("stage_history", []):
            if (
                entry.get("feature") == FEATURE_ID
                and entry.get("stage") == "specification"
            ):
                entry["contract_sha256"] = current
        self.write_state(state)

    def strip_legacy_locator(self, packet_id: str) -> None:
        """Da al predecesor la forma de una generación HISTÓRICA: ni su
        REQUEST.json ni la cabecera de su PACKET.md declaran el campo."""
        request_path = self.packet_dir(packet_id) / "REQUEST.json"
        request = json.loads(request_path.read_text(encoding="utf-8"))
        request.pop("execution_context", None)
        request_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")

        packet_path = self.packet_dir(packet_id) / "PACKET.md"
        packet_text = packet_path.read_text(encoding="utf-8")
        metadata = header_metadata(packet_text)
        metadata.pop("execution_context", None)
        body = packet_text[len(PACKET_BEGIN) :].split(PACKET_END, 1)[1]
        packet_path.write_text(
            PACKET_BEGIN + json.dumps(metadata, sort_keys=True) + PACKET_END + body,
            encoding="utf-8",
        )

    # -- lectura de artefactos -------------------------------------------

    def packet_dir(self, packet_id: str) -> Path:
        return self.root / ".cdad" / "packets" / packet_id

    def packet_bytes(self, packet_id: str, name: str) -> bytes:
        return (self.packet_dir(packet_id) / name).read_bytes()

    def packet_request(self, packet_id: str) -> dict:
        return json.loads(
            self.packet_bytes(packet_id, "REQUEST.json").decode("utf-8")
        )

    def packet_text(self, packet_id: str) -> str:
        return self.packet_bytes(packet_id, "PACKET.md").decode("utf-8")

    def active_packet_id(self) -> str:
        active = self.read_state().get("active_packet") or {}
        packet_id = active.get("id")
        if not packet_id:
            raise AssertionError(f"fixture: no hay paquete activo: {active!r}")
        return packet_id


class TestB2ActiveV1PacketDiagnosis(unittest.TestCase):
    """B2 (review T6): con un paquete v1 activo no terminal —incluido
    `prepared`—, `prepare` y `prepare --new-execution` deben diagnosticar el
    bloqueo, la ausencia de una ruta CLI terminal y la escalación al owner,
    sin ofrecer «completar o fallar» y sin tocar el state ni publicar v1."""

    def test_b2_active_v1_packet_is_diagnosed_and_escalated_without_effects(
        self,
    ) -> None:
        """PC-07b (spec:205,222,352): un único resultado observable ante un
        paquete v1 activo no terminal.

        R4: sin esta prueba, el usuario sigue la indicación que hoy recibe
        (`prepare --new-execution`), choca con «complete or fail it» —orden
        que la spec prohíbe— y queda en un callejón sin salida, sin ningún
        paso que escale al owner.
        """
        with tempfile.TemporaryDirectory(prefix="cdad-010-004-t6-b2-") as tmp:
            # CONTROL POSITIVO (a), ordenado ANTES de la aserción RED: la
            # misma fixture v2 SIN paquete activo prepara y publica.
            control = T6Project(Path(tmp) / "v2-control")
            control.write_v2_context()
            prepared = control.prepare(
                "--execution-context",
                str(control.root / CANONICAL_LOCATOR),
                "--role",
                "test-writer",
                "--substage",
                "red",
                "--objective",
                "control positivo B2 (fixture T6)",
            )
            self.assertEqual(
                prepared.returncode,
                0,
                msg="CONTROL POSITIVO (a): la fixture v2 sin paquete activo "
                "debe preparar y publicar; si falla, el caso negativo no "
                f"prueba el bloqueo v1: {prepared.stdout!r} {prepared.stderr!r}",
            )
            control_active = control.read_state().get("active_packet") or {}
            self.assertEqual(
                control_active.get("status"),
                "prepared",
                msg=f"CONTROL POSITIVO (a): paquete activo: {control_active!r}",
            )
            control_id = control_active.get("id") or ""
            self.assertTrue(
                (control.packet_dir(control_id) / "REQUEST.json").is_file(),
                msg=f"CONTROL POSITIVO (a): no se publicó el request de {control_id!r}",
            )
            self.assertTrue(
                (control.packet_dir(control_id) / "PACKET.md").is_file(),
                msg=f"CONTROL POSITIVO (a): no se publicó el paquete de {control_id!r}",
            )

            # CASO: paquete v1 activo `prepared` ya publicado y contexto v1
            # en `.cdad/execution.json`.
            project = T6Project(Path(tmp) / "v1-active")
            project.write_v1_context()
            packet_id = project.publish_legacy_active_packet()
            before = tree_digests(project.root)
            state_before = project.state_bytes()

            for label, extra in (
                ("prepare", ()),
                ("prepare --new-execution", ("--new-execution",)),
            ):
                proc = project.prepare(
                    "--role",
                    "test-writer",
                    "--substage",
                    "red",
                    "--objective",
                    "diagnóstico de remediación T6",
                    *extra,
                )
                output = proc.stdout + proc.stderr
                lowered = output.lower()

                self.assertNotEqual(
                    proc.returncode,
                    0,
                    msg=f"{label}: con un paquete v1 activo no terminal el "
                    f"comando no puede tener éxito: {output!r}",
                )
                self.assertIn(
                    "ERROR:",
                    output,
                    msg=f"{label}: se conserva la envoltura `ERROR:` existente: "
                    f"{output!r}",
                )
                self.assertIn(
                    packet_id,
                    output,
                    msg=f"{label}: el diagnóstico no nombra el paquete v1 activo "
                    f"que bloquea ({packet_id!r}), así que el usuario no sabe "
                    f"qué registro lo detiene: {output!r}",
                )
                self.assertNotIn(
                    "complete or fail",
                    lowered,
                    msg=f"{label}: la spec prohíbe indicar «completar o fallar» "
                    f"como procedimiento disponible: {output!r}",
                )
                self.assertNotIn(
                    "completar o fallar",
                    lowered,
                    msg=f"{label}: la spec prohíbe indicar «completar o fallar» "
                    f"como procedimiento disponible: {output!r}",
                )
                self.assertIn(
                    "owner",
                    lowered,
                    msg=f"{label}: el diagnóstico no escala al owner: {output!r}",
                )
                self.assertIn(
                    "terminal",
                    lowered,
                    msg=f"{label}: el diagnóstico no declara la ausencia de una "
                    f"ruta CLI terminal: {output!r}",
                )

            self.assertEqual(
                tree_digests(project.root),
                before,
                msg="un rechazo no publica archivos ni modifica el árbol: el "
                "state y los bytes de la fixture deben quedar idénticos",
            )
            self.assertEqual(
                project.state_bytes(),
                state_before,
                msg="un rechazo no modifica el state (deja el state intacto y "
                "no prepara v1)",
            )


class TestB4ReplaceSuccessorDeclaresLocator(unittest.TestCase):
    """B4 (review T6): el sucesor de `--replace-packet` declara el localizador
    canónico en request y cabecera aunque el predecesor no lo declarara, y no
    reescribe los bytes del predecesor."""

    def _assert_successor_declares_canonical_locator(
        self, project: T6Project, successor_id: str, label: str
    ) -> None:
        """Asserts 2-4 del caso: request, cabecera y bytes del predecesor."""
        request = project.packet_request(successor_id)
        self.assertEqual(
            request.get("execution_context"),
            CANONICAL_LOCATOR,
            msg=f"{label}: el REQUEST.json del sucesor ({successor_id!r}) debe "
            f"declarar el localizador canónico {CANONICAL_LOCATOR!r} y no "
            f"{request.get('execution_context')!r}",
        )
        metadata = header_metadata(project.packet_text(successor_id))
        self.assertEqual(
            metadata.get("execution_context"),
            CANONICAL_LOCATOR,
            msg=f"{label}: la cabecera del PACKET.md del sucesor "
            f"({successor_id!r}) debe declarar el mismo localizador canónico "
            f"{CANONICAL_LOCATOR!r} y no {metadata.get('execution_context')!r}",
        )

    def test_b4_replace_successor_declares_locator_over_historical_predecessor(
        self,
    ) -> None:
        """PC-04 (spec:462): comprobar la incorporación del campo/localizador
        en las generaciones nuevas afectadas (el sucesor de
        `--replace-packet`).

        R4: sin esta prueba, si esa línea del producto se rompe el sucesor se
        publica sin localizador y aun así pasa con `--execution-context`
        explícito: el defecto no se ve hasta el gate del padre, o no se ve.
        """
        with tempfile.TemporaryDirectory(prefix="cdad-010-004-t6-b4-") as tmp:
            # CONTROL POSITIVO (b), ordenado ANTES del caso: un sucesor cuyo
            # predecesor YA declara `execution_context`.
            control = T6Project(Path(tmp) / "predecessor-declared")
            control.write_v2_context()
            control_predecessor = control.publish_predecessor()
            self.assertEqual(
                control.packet_request(control_predecessor).get("execution_context"),
                CANONICAL_LOCATOR,
                msg="CONTROL POSITIVO (b): el predecesor publicado por una "
                "preparación nueva debe declarar ya el localizador canónico",
            )
            control.outdate_contract()
            control_request_before = control.packet_bytes(
                control_predecessor, "REQUEST.json"
            )
            control_packet_before = control.packet_bytes(
                control_predecessor, "PACKET.md"
            )
            control_proc = control.replace(
                control_predecessor,
                "control positivo B4: predecesor que declara el localizador",
            )
            self.assertEqual(
                control_proc.returncode,
                0,
                msg="CONTROL POSITIVO (b): el reemplazo de un paquete "
                "obsoleto debe tener éxito; si falla, la fixture no prueba el "
                f"caso histórico: {control_proc.stdout!r} {control_proc.stderr!r}",
            )
            control_successor = control.active_packet_id()
            self.assertNotEqual(
                control_successor,
                control_predecessor,
                msg="CONTROL POSITIVO (b): el reemplazo publica un paquete nuevo",
            )
            self._assert_successor_declares_canonical_locator(
                control, control_successor, "CONTROL POSITIVO (b)"
            )
            self.assertEqual(
                control.packet_bytes(control_predecessor, "REQUEST.json"),
                control_request_before,
                msg="CONTROL POSITIVO (b): los bytes del request del predecesor "
                "no cambian",
            )
            self.assertEqual(
                control.packet_bytes(control_predecessor, "PACKET.md"),
                control_packet_before,
                msg="CONTROL POSITIVO (b): los bytes del paquete del predecesor "
                "no cambian",
            )

            # CASO B4: predecesor de una generación HISTÓRICA, cuyo request
            # (ni cuya cabecera) no declaraba `execution_context`.
            project = T6Project(Path(tmp) / "historical-predecessor")
            project.write_v2_context()
            predecessor = project.publish_predecessor()
            project.strip_legacy_locator(predecessor)
            self.assertNotIn(
                "execution_context",
                project.packet_request(predecessor),
                msg="fixture B4: el predecesor debe tener la forma histórica, "
                "sin el campo en su request",
            )
            project.outdate_contract()
            request_before = project.packet_bytes(predecessor, "REQUEST.json")
            packet_before = project.packet_bytes(predecessor, "PACKET.md")

            proc = project.replace(
                predecessor,
                "reemplazo T6: predecesor histórico sin localizador",
            )
            self.assertEqual(
                proc.returncode,
                0,
                msg="B4: el reemplazo de un paquete prepared y obsoleto debe "
                f"publicar el sucesor: {proc.stdout!r} {proc.stderr!r}",
            )
            successor = project.active_packet_id()
            self.assertNotEqual(
                successor,
                predecessor,
                msg="B4: el reemplazo debe publicar un paquete nuevo, no "
                "reutilizar el predecesor",
            )
            self._assert_successor_declares_canonical_locator(
                project, successor, "B4"
            )
            self.assertEqual(
                project.packet_bytes(predecessor, "REQUEST.json"),
                request_before,
                msg="B4: el reemplazo no reescribe el REQUEST.json del "
                "predecesor (bytes idénticos antes/después)",
            )
            self.assertEqual(
                project.packet_bytes(predecessor, "PACKET.md"),
                packet_before,
                msg="B4: el reemplazo no reescribe el PACKET.md del predecesor "
                "(bytes idénticos antes/después)",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
