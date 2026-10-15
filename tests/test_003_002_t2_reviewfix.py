#!/usr/bin/env python3
"""003-002 T2 RED review-fix — hallazgos R1–R5 de review-t2.md.

Contract:
- docs/specs/003-002-artifact-tools/spec.md (§2 interfaz; §5 «la autoridad
  vencida impide nuevas recepciones y materializaciones»; §7 materialización
  explícita: tabla cerrada rol↔kind, journal durable, retry multi-copy, CAS;
  §8 crash en el límite observable; §9 propiedad del estado)
- docs/specs/003-002-artifact-tools/review-t2.md (dictamen: R1–R5 BLOCKING;
  distribución: R1–R3 → review-fix del implementer; R4–R5 → RED del
  test-writer)

Mapa hallazgo → test (cada test nombra su hallazgo y su postcondición):

- R1 (BLOCKING, RED hoy): `test_r1_materialize_with_revoked_hitl_delegation_is_rejected`
  — con la delegación HITL revocada en el state (`hitl_delegation.status =
  "user-revoked"` tras el receipt durable, E5-[A] de la review), `materialize`
  debe RECHAZAR con diagnóstico (§5: la autoridad vencida impide
  materializaciones; §9: leer el state está permitido, escribirlo no). Hoy el
  comando aplica la copia con rc=0 (no consulta la vigencia de la autoridad).
- R2 (BLOCKING, RED hoy): `test_r2_closed_policy_admits_exactly_the_spec_audit_row`
  — el universo de kinds admitidos coincide con la tabla cerrada de §7
  nombre por nombre: la spec tiene UNA fila de auditoría («test-writer
  audit», target fijo `test-audit.md`); hoy la instalación admite DOS kinds
  de auditoría (`test-audit` y el extra `test-writer-audit`, no nombrado por
  la tabla aprobada — E6 de la review). El test no fija cuál sobrevive:
  exige exactamente uno (remedio: eliminar la clave extra, o enmienda de
  spec que la fije).
- R3 (BLOCKING, RED hoy): `test_r3_materialize_rejects_part_kind_of_another_role`
  — «Rol/subfase y artifact_kind usan una tabla cerrada; un kind de otro rol
  falla» (§7). Cuatro cruces que hoy se aceptan (indexado por kind sin
  consultar `receipt.role`/`substage`): test-writer/red con kind `review`;
  test-writer/red con kind `scribe-projectbrief`; reviewer/review con kind
  `test-writer-role-report`; scribe/memory con kind `test-audit`. Todos
  deben fallar; cada cruce usa el target que el kind —solo— autoriza hoy,
  de modo que el único preflight capaz de rechazarlos sea el cierre rol↔kind.
- R4 (lock, pasa hoy): `test_r4a_interrupted_before_second_copy_continues_from_real_journal`
  — interrupción DETERMINISTA de una corrida real en el límite observable
  de la copy 2 (§8: «crash… o preparando pending dirs documentados»: el
  punto de falla se fabrica con un archivo regular en el padre de la copy
  2, de modo que la copy 1 queda publicada y ya REGISTRADA en el journal
  real `.cdad/runtime/materializations/<exec>/<packet>/<authorization_sha256>.json`
  y la copy 2 sin publicar — sin carreras ni timing); el retry con la MISMA
  authorization continúa desde el journal (§7). Y
  `test_r4b_journal_divergent_retry_refuses_without_overwrite` — journal
  del retry con target divergido (contenido cambiado por fuera del efecto
  registrado) → el retry se rehusa y no sobrescribe (§7: «nunca repite ni
  sobrescribe un efecto divergente»).
- R5 (locks, pasan hoy): matriz §7 sin cobertura (review-t2 R5) —
  `test_r5_scribe_file_roots_materialize_all_memory_bank_files` (los únicos
  kinds cuya raíz permitida es un ARCHIVO),
  `test_r5_scribe_cas_memory_bank_end_to_end` (CAS de Memory Bank:
  create-only + reemplazo contra el digest anterior exacto),
  `test_r5_review_row_materializes_declared_target` (reviewer `review`,
  read-only),
  `test_r5_plan_review_row_materializes_declared_target` (reviewer
  `plan-review` con contrato `draft-plan`),
  `test_r5_audit_row_materializes_the_fixed_target` (target fijo
  `test-audit.md`),
  `test_r5_kind_outside_closed_table_is_rejected` y
  `test_r5_approval_effect_true_is_rejected`.

Los tests no leen implementación: la superficie observable es el CLI de §2,
el recibo durable de T1, los targets y el journal (artefacto durable de §7).
Las corridas del CLI van con cwd en la raíz del fixture; todo fixture es un
tempdir, nunca el repo. Un fallo de RED debe ser aserción de comportamiento,
nunca CLI ausente (guard anti-RED inválida).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.test_003_002_t2_materialize import (
    BASELINE_REF,
    BASELINE_SHA256,
    DESCRIPTOR_PATH,
    FEATURE_ID,
    MANIFEST_PATH,
    PART_BYTES,
    STATE_FILE,
    TARGET_REPORT,
    TARGET_SECOND,
    MaterializeProjectCase,
    assert_reachable_or_invalid_red,
    err_text,
    out_text,
)
from tests.test_004_003_t1_draft_contract import (
    DRAFT_PLAN_RELPATH,
    DRAFT_PLAN_VERSION,
    DRAFT_PLAN_WITH_TASKS,
)

ALLOWED_ROOT = f"docs/specs/{FEATURE_ID}/"
AUDIT_BYTES = (
    b"# Test-writer audit (fixture T2 review-fix)\n"
    b"Evidencia mecanica del audit de T2 (003-002).\n"
)
TARGET_FIXED_AUDIT = ALLOWED_ROOT + "test-audit.md"
OTHER_BYTES = b"# contenido divergente (no es el efecto registrado)\n"
ATTEMPT_ID = "attempt-t2-reviewfix-001"

# R3 — cruces de la tabla cerrada: receipt role/substage con el kind de
# OTRO rol (target = el que el kind solo autoriza hoy, §7).
ROLE_KIND_CROSSINGS = (
    ("test-writer", "red", "review", ALLOWED_ROOT + "review-t2.md"),
    ("test-writer", "red", "scribe-projectbrief", "docs/projectbrief.md"),
    ("reviewer", "review", "test-writer-role-report", TARGET_REPORT),
    ("scribe", "memory", "test-audit", TARGET_FIXED_AUDIT),
)


# ---------------------------------------------------------------- fixtures


class ReviewFixProjectCase(MaterializeProjectCase):
    """Proyecto sintético parametrizable por rol/substage/contrato.

    Igual que `MaterializeProjectCase` pero con rol, substage, parts y kinds
    por instancia, y soporte de contrato `draft-plan` para la fila
    plan-review (prepare de 004-003: `--contract-kind/--contract-path/
    --plan-version`).
    """

    role = "test-writer"
    substage = "red"
    attempt_id = ATTEMPT_ID
    drafts_contract: tuple[str, str, str] | None = None   # (path, kind, version)

    def new_dispatched_project(self) -> None:
        tmp = tempfile.mkdtemp(prefix="cdad-003-002-t2rf-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", tmp], check=False))
        self.root = self.build_project(Path(tmp) / "proj")
        self.establish_dispatched()

    def establish_dispatched(self) -> None:
        """Paquete dispatched del fixture con el rol/substage del caso."""
        args = [
            "prepare", "--project-root", str(self.root),
            "--role", self.role, "--substage", self.substage,
            "--objective",
            f"T2 review-fix objective ({self.role}/{self.substage})",
        ]
        if self.drafts_contract is not None:
            path, _, version = self.drafts_contract
            draft = self.root / path
            draft.parent.mkdir(parents=True, exist_ok=True)
            draft.write_bytes(DRAFT_PLAN_WITH_TASKS)
            args += ["--contract-kind", "draft-plan",
                     "--contract-path", path,
                     "--plan-version", version]
        prep = self.run_packet_cli(args)
        self.assertEqual(
            prep.returncode, 0,
            msg=f"precondición (fixture): `prepare` debe tener éxito: "
                f"{out_text(prep)} {err_text(prep)}")
        state = json.loads((self.root / STATE_FILE).read_text(encoding="utf-8"))
        self.packet_id = state["active_packet"]["id"]
        self.assertEqual(
            state["active_packet"]["role"], self.role,
            msg="precondición (fixture): el paquete activo pertenece al rol "
                "del caso")
        execution_id = (state.get("execution") or {}).get("id")
        self.assertTrue(
            execution_id, msg="precondición (fixture): binding v2 de 001")
        self.execution_id = execution_id
        self.execution_context_path = (
            self.root / ".cdad" / "executions" / execution_id
            / "execution.json")
        self.assertTrue(
            self.execution_context_path.is_file(),
            msg="precondición (fixture): contexto v2 debe existir")
        self.packet_dir = self.root / ".cdad" / "packets" / self.packet_id
        self.packet_path = self.packet_dir / "PACKET.md"
        self.request_path = self.packet_dir / "REQUEST.json"
        for path in (self.packet_path, self.request_path):
            self.assertTrue(
                path.is_file(),
                msg=f"precondición (fixture): paquete publicado {path}")
        # Observación de dispatch I8 (documento de claves cerradas).
        observation_path = self.root / "docs" / "observations-t2-reviewfix.json"
        observation_path.write_text(json.dumps({
            "runtime": "opencode",
            "model_configured": "glm-5.3-flash",
            "model_reported": "glm-5.3-flash",
            "session": "ses-003-002-t2-reviewfix-0001",
            "started_at": "2026-10-05T00:00:00Z",
            "provenance": {
                "runtime": "reported by runtime",
                "model_reported": "orchestrator",
                "session": "orchestrator",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        record = self.run_packet_cli([
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", self.packet_id,
            "--attempt-id", self.attempt_id,
            "--input", str(observation_path),
        ])
        self.assertEqual(
            record.returncode, 0,
            msg=f"precondición (fixture): --record-dispatch debe registrar "
                f"el intento: {out_text(record)} {err_text(record)}")
        state = json.loads((self.root / STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(
            state["active_packet"]["status"], "dispatched",
            msg="precondición (fixture): paquete dispatched (I8)")

    def establish_received(self) -> None:
        """Fixture hasta el recibo durable (receive de T1) con parts propios."""
        staged_parts = self.staged_parts()
        inbox = self.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        for name, data in staged_parts.items():
            (inbox / f"{name}.md").write_bytes(data)
        (self.root / MANIFEST_PATH).write_text(json.dumps({
            "schema_version": 1,
            "observation_status": "trusted",
            "baseline_ref": BASELINE_REF,
            "baseline_sha256": BASELINE_SHA256,
            "changes": [],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        descriptor_doc = {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "feature_id": FEATURE_ID,
            "source": {"kind": "staged-file", "sdk_message_ref": None},
            "parts": [
                {"name": name, "artifact_kind": self.part_kind(name),
                 "staged_path": f".cdad/inbox/{name}.md"}
                for name in staged_parts
            ],
            "observed_changes": {
                "observation_status": "trusted",
                "baseline_ref": BASELINE_REF,
                "baseline_sha256": BASELINE_SHA256,
                "manifest_path": MANIFEST_PATH,
            },
            "run_evidence_ref": None,
        }
        descriptor_path = self.root / DESCRIPTOR_PATH
        descriptor_path.write_text(
            json.dumps(descriptor_doc, ensure_ascii=False, sort_keys=True)
            + "\n", encoding="utf-8")
        proc = self.run_receive_cli([
            "receive",
            "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path),
            "--packet", str(self.packet_path),
            "--request", str(self.request_path),
            "--descriptor", str(descriptor_path),
        ])
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): `receive` de T1 debe tener éxito: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assertTrue(
            self.receipt_path.is_file(),
            msg="precondición (fixture): receipt durable debe existir")

    # -- parámetros por caso -------------------------------------------------

    def staged_parts(self) -> dict[str, bytes]:
        raise NotImplementedError("cada caso declara sus parts")

    def part_kind(self, name: str) -> str:
        raise NotImplementedError("cada caso declara sus kinds")

    # -- oráculos del journal (artefacto durable §7) --------------------------

    @property
    def journal_dir(self) -> Path:
        return (self.root / ".cdad" / "runtime" / "materializations"
                / self.execution_id / self.packet_id)

    def journal_copies(self) -> list[dict]:
        """Copias registradas en los journals durables del packet (lectura
        del artefacto observable de §7: journal ligado a receipt/auth hash;
        una escritura parcial/incompleta se ignora en ese instante)."""
        entries: list[dict] = []
        if not self.journal_dir.is_dir():
            return entries
        for path in sorted(self.journal_dir.glob("*.json")):
            try:
                doc = json.loads(path.read_bytes())
            except (json.JSONDecodeError, OSError):
                continue
            entries.extend(doc.get("copies") or [])
        return entries


class SinglePartCase(ReviewFixProjectCase):
    """Fixture con un juego fijo de parts/kinds declarados por clase."""

    _STAGED: dict[str, bytes] = {}
    _KINDS: dict[str, str] = {}

    def staged_parts(self) -> dict[str, bytes]:
        return type(self)._STAGED

    def part_kind(self, name: str) -> str:
        return type(self)._KINDS[name]


class WriterReportCase(SinglePartCase):
    """Fila test-writer no-audit (§7): receipt test-writer/red."""

    _STAGED = {"role-report": PART_BYTES}
    _KINDS = {"role-report": "test-writer-role-report"}


# ------------------------------------------------------------------- R1


class TestR1RevokedAuthority(WriterReportCase):
    """R1 (BLOCKING): delegación HITL revocada bloquea materialize."""

    def test_r1_materialize_with_revoked_hitl_delegation_is_rejected(self) -> None:
        """R1/P4: con `hitl_delegation.status = "user-revoked"` en el state
        (revocado después del receipt durable, E5-[A] de la review),
        `materialize` debe fallar sin aplicar copias y sin tocar el state,
        el receipt ni el contexto de ejecución; el diagnóstico debe nombrar
        la autoridad/delegación (§5: la autoridad vencida impide
        materializaciones; §9: leer el state está permitido, escribirlo
        no)."""
        self.new_dispatched_project()
        self.establish_received()
        state_raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        state_raw["hitl_delegation"]["status"] = "user-revoked"
        self.state_path.write_text(
            json.dumps(state_raw, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        state_after_flip = self.state_path.read_bytes()
        receipt_before = self.receipt_path.read_bytes()
        context_before = self.execution_context_path.read_bytes()

        proc = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "role-report", "target": TARGET_SECOND,
                  "expected_previous_sha256": None}])))
        self.assertNotIn(
            "invalid choice", err_text(proc),
            msg="R1: los argv de §2 declaran `materialize`; un rechazo por "
                "CLI ausente sería RED inválida")
        self.assertNotEqual(
            proc.returncode, 0,
            msg="R1: materialize debe RECHAZAR con la delegación HITL "
                "revocada (§5: la autoridad vencida impide "
                "materializaciones; hoy aplica la copia con rc=0) — "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        assert_reachable_or_invalid_red(err_text(proc),
                                        "R1: rechazo por autoridad revocada")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="R1: fallo con traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg="R1: el rechazo no debe emitir evidencia por stdout")
        self.assertFalse(
            (self.root / TARGET_SECOND).exists(),
            msg="R1: el rechazo aplicó la copia pese a la delegación "
                "revocada (escape de la vigencia de la autoridad)")
        self.assertEqual(
            self.state_path.read_bytes(), state_after_flip,
            msg="R1: materialize no debe modificar el state (§9: el único "
                "escritor es el orquestador)")
        self.assertEqual(
            self.receipt_path.read_bytes(), receipt_before,
            msg="R1: materialize no toca el receipt durable")
        self.assertEqual(
            self.execution_context_path.read_bytes(), context_before,
            msg="R1: materialize no toca el contexto de ejecución v2")
        self.assertTrue(
            re.search(
                r"authorit|delegaci|hitl|vigencia|state",
                err_text(proc), re.IGNORECASE),
            msg="R1: el diagnóstico no nombra la autoridad/delegación "
                f"(§5): {err_text(proc)!r}")


# ------------------------------------------------------------------- R2


class TestR2ClosedAuditRow(ReviewFixProjectCase):
    """R2 (BLOCKING): el universo de kinds coincide con la tabla cerrada §7."""

    role = "test-writer"
    substage = "audit"
    current_kind = "test-audit"

    def staged_parts(self) -> dict[str, bytes]:
        return {"audit-part": AUDIT_BYTES}

    def part_kind(self, name: str) -> str:
        assert name == "audit-part"
        return self.current_kind

    def _probe(self, kind: str) -> tuple[subprocess.CompletedProcess, bool]:
        """Un fixture fresco por kind (el kind va ligado en el recibo)."""
        self.current_kind = kind
        self.new_dispatched_project()
        self.establish_received()
        proc = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "audit-part", "target": TARGET_FIXED_AUDIT,
                  "expected_previous_sha256": None}])))
        written = (self.root / TARGET_FIXED_AUDIT).is_file()
        if proc.returncode == 0:
            self.assertEqual(
                (self.root / TARGET_FIXED_AUDIT).read_bytes(), AUDIT_BYTES,
                msg=f"R2 (precondición): el materializado de {kind!r} "
                    f"conserva los bytes")
        self.assertEqual(
            proc.stdout, b"",
            msg="R2: ningún outcome del probe debe emitir evidencia "
                "por stdout")
        return proc, written

    def test_r2_closed_policy_admits_exactly_the_spec_audit_row(self) -> None:
        """R2/P4: la tabla cerrada de la spec §7 tiene UNA fila de
        auditoría («test-writer audit», target fijo `test-audit.md`);
        exactamente uno de los dos kinds que hoy despliega la instalación
        (`test-audit`, `test-writer-audit`) puede estar admitido: el extra
        (hoy `test-writer-audit`) no nombra la tabla aprobada y se admite
        sin ganancia pero ensanchando en silencio el control declarado
        (review-t2 R2/E6). Remedio: eliminar la clave extra o enmienda de
        spec que la fije."""
        admitted: list[str] = []
        rejected: list[str] = []
        for kind in ("test-audit", "test-writer-audit"):
            with self.subTest(kind=kind):
                proc, written = self._probe(kind)
                if proc.returncode == 0:
                    self.assertTrue(
                        written,
                        msg="coherencia: rc=0 debe dejar el target escrito")
                    admitted.append(kind)
                else:
                    assert_reachable_or_invalid_red(
                        err_text(proc), f"R2: rechazo de {kind!r}")
                    self.assertNotIn(
                        "Traceback", err_text(proc),
                        msg=f"R2: el rechazo de {kind!r} fue por traceback")
                    rejected.append(kind)
        self.assertEqual(
            len(admitted), 1,
            msg="R2: la tabla cerrada §7 fija UNA fila de auditoría; hoy "
                f"se admiten {len(admitted)} kinds de auditoría "
                f"({', '.join(admitted) or 'ninguno'} admitidos / "
                f"{', '.join(rejected) or 'ninguno'} rechazados) — el "
                "universo de kinds se ensanchó en silencio respecto de la "
                "tabla aprobada")


# ------------------------------------------------------------------- R3


class TestR3RoleKindClosure(ReviewFixProjectCase):
    """R3 (BLOCKING): un kind de otro rol en el recibo falla (§7).

    Cada cruce usa el target que ese kind solo autoriza hoy, de modo que la
    única razón de rechazo observable sea el cierre rol↔kind (no la raíz).
    """

    crossing_kind = "review"
    crossing_bytes = PART_BYTES

    def staged_parts(self) -> dict[str, bytes]:
        return {"crossing": self.crossing_bytes}

    def part_kind(self, name: str) -> str:
        assert name == "crossing"
        return self.crossing_kind

    def _assert_rejected_crossing(self, role: str, substage: str,
                                  kind: str, target: str) -> None:
        self.role = role
        self.substage = substage
        self.crossing_kind = kind
        self.new_dispatched_project()
        self.establish_received()
        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(
            receipt["role"], role,
            msg="precondición (fixture): el recibo liga el rol del caso")
        state_before = self.state_path.read_bytes()
        proc = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "crossing", "target": target,
                  "expected_previous_sha256": None}])))
        self.assertNotIn(
            "invalid choice", err_text(proc),
            msg="R3: los argv de §2 declaran `materialize`; un fallo por "
                "CLI ausente sería RED inválida")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"R3 ({role}/{substage} con el kind ajeno {kind!r}): el "
                "cierre rol↔kind debe fallar (§7: «un kind de otro rol "
                "falla»): hoy sólo se indexa por kind sin consultar "
                f"receipt.role/substage — rc={proc.returncode} "
                f"stdout={out_text(proc)!r} stderr={err_text(proc)!r}")
        assert_reachable_or_invalid_red(
            err_text(proc), f"R3 ({role}/{substage}): kind ajeno")
        self.assertNotIn("Traceback", err_text(proc),
                         msg=f"R3 ({role}/{substage}): fallo con traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg=f"R3 ({role}/{substage}): el rechazo no debe emitir stdout")
        self.assertFalse(
            (self.root / target).exists(),
            msg=f"R3 ({role}/{substage}): el kind ajeno se materializó")
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg=f"R3 ({role}/{substage}): el rechazo no toca el state")
        self.assertTrue(
            re.search(r"rol|role|kind|artifact", err_text(proc),
                      re.IGNORECASE),
            msg=f"R3 ({role}/{substage}): el diagnóstico no nombra el "
                f"motivo (§7): {err_text(proc)!r}")

    def test_r3_materialize_rejects_part_kind_of_another_role(self) -> None:
        """R3/P4: todos los cruces de la tabla cerrada (writer con kind de
        reviewer o scribe; reviewer con kind de test-writer; scribe con
        kind de auditoría) deben fallar porque el kind pertenece a otro rol
        del recibo (§7)."""
        for role, substage, kind, target in ROLE_KIND_CROSSINGS:
            with self.subTest(role=role, substage=substage, kind=kind):
                self._assert_rejected_crossing(role, substage, kind, target)


# ------------------------------------------------------------------- R4


class TestR4RealJournalObserve(WriterReportCase):
    """R4 (lock): el retry multi-copy se observa DESDE EL JOURNAL real.

    Fixture con journal real: una corrida previa truncada de forma
    DETERMINISTA en el límite observable de la copy 2 (§8: «crash… o
    preparando pending dirs documentados» — el punto de falla se fabrica
    con un archivo regular en el padre de la copy 2, de modo que la copy 1
    queda publicada y ya registrada en el journal real y la copy 2 sin
    publicar; sin carreras ni dependencia de timing), y el negativo de
    journal divergente (§7 retry/journal).
    """

    def test_r4a_interrupted_before_second_copy_continues_from_real_journal(self) -> None:
        """R4/P4: una primera corrida truncada DETERMINISTAMENTE antes de la
        copy 2 (el pre-flight no rechaza el estado del fixture: el fallo
        `Not a directory` ocurre en el punto de OPERACIÓN de la copy 2,
        después de que la copy 1 está publicada y ya registrada en el
        journal real de esa authorization); el retry con la MISMA
        authorization continúa desde el journal: copy 1 íntegra (sin
        repetir ni sobrescribir), copy 2 aplicada, journal actualizado con
        ambas, state intacto (§7/§8)."""
        deep_second = f"{ALLOWED_ROOT}lvl1/lvl2/test-writer-red-deep.md"
        copies = [
            {"part": "role-report", "target": TARGET_REPORT,
             "expected_previous_sha256": None},
            {"part": "role-report", "target": deep_second,
             "expected_previous_sha256": None},
        ]
        self.new_dispatched_project()
        self.establish_received()
        auth_path = self.write_authorization(self.build_authorization(copies))
        # Bloqueo determinista del punto de fallo: `lvl1` es un archivo
        # regular → el materializado de la copy 2 falla en su punto de
        # operación (tras la copy 1), no en el pre-flight.
        blocker = self.root / f"{ALLOWED_ROOT}lvl1"
        blocker.write_bytes(b"archivo regular, no directorio (bloqueo del fixture)\n")

        first = self.materialize(auth_path)
        self.assertNotIn(
            "invalid choice", err_text(first),
            msg="R4: los argv de §2 declaran `materialize`; un fallo por "
                "CLI ausente sería RED inválida")
        self.assertNotEqual(
            first.returncode, 0,
            msg="R4 (precondición): la corrida bloqueada debe interrumpirse "
                "en la copy 2 (bloqueo determinista del fixture) — "
                f"rc={first.returncode} stdout={out_text(first)!r} "
                f"stderr={err_text(first)!r}")
        assert_reachable_or_invalid_red(
            err_text(first), "R4: interrupción determinista de la copy 2")
        self.assertNotIn("Traceback", err_text(first),
                         msg="R4: la interrupción dejó un traceback")
        self.assertEqual(
            first.stdout, b"",
            msg="R4: la corrida interrumpida no debe emitir evidencia por "
                "stdout")
        # Estado de interrupción observable: copy 1 publicada y ya
        # registrada en el journal real; copy 2 sin publicar ni journalizar.
        first_target = self.root / TARGET_REPORT
        deep_target = self.root / deep_second
        self.assertTrue(
            first_target.is_file(),
            msg="R4 (precondición): la copy 1 debe estar publicada con el "
                "estado de interrupción")
        self.assertEqual(
            first_target.read_bytes(), PART_BYTES,
            msg="R4 (precondición): la copy 1 publicada conserva los bytes "
                "originales")
        self.assertFalse(
            deep_target.is_file(),
            msg="R4 (precondición): la copy 2 debe seguir sin publicar "
                "(bloqueo determinista)")
        entries = self.journal_copies()
        self.assertTrue(
            entries,
            msg="R4 (precondición): el journal real debe existir tras la "
                "corrida interrumpida")
        self.assertEqual(
            [entry.get("target") for entry in entries], [TARGET_REPORT],
            msg="R4 (precondición): el journal real debe registrar SÓLO la "
                "copy 1 (límite observable: copy 2 sin efecto)")
        journal_root = (self.root / ".cdad" / "runtime" / "materializations"
                        / self.execution_id / self.packet_id)
        journal_before = sorted(p.name for p in journal_root.glob("*.json"))
        self.assertEqual(
            len(journal_before), 1,
            msg="R4 (precondición): un journal por authorization (ligado a "
                "receipt/authorization hash)")
        state_before = self.state_path.read_bytes()

        # Se retira el bloqueo: la copy 2 vuelve a ser materializable para
        # el retry con la MISMA authorization.
        blocker.unlink()

        retry = self.materialize(auth_path)
        self.assertEqual(
            retry.returncode, 0,
            msg=f"R4: el retry debe continuar desde el journal real "
                f"(copy ya aplicada e idéntica omitida, restante aplicada): "
                f"rc={retry.returncode} stdout={out_text(retry)!r} "
                f"stderr={err_text(retry)!r}")
        self.assertNotIn("Traceback", err_text(retry),
                         msg="R4: el retry dejó un traceback")
        self.assertEqual(
            (self.root / TARGET_REPORT).read_bytes(), PART_BYTES,
            msg="R4: la copia ya registrada en el journal permanece "
                "byte-idéntica (sin repetir ni sobrescribir)")
        self.assertEqual(
            deep_target.read_bytes(), PART_BYTES,
            msg="R4: la copia restante debe aplicarse con los bytes "
                "originales")
        after = sorted(
            entry.get("target") for entry in self.journal_copies())
        self.assertEqual(
            after,
            sorted((TARGET_REPORT, deep_second)),
            msg="R4: el journal real debe terminar con ambas copias "
                "registradas (continuó desde el journal, no desde cero)")
        self.assertEqual(
            journal_before,
            sorted(p.name for p in journal_root.glob("*.json")),
            msg="R4: el retry con la misma authorization reutiliza el "
                "mismo journal (ligado a receipt/authorization hash)")
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="R4: materialize/retry no toca el state (§9)")

    def test_r4b_journal_divergent_retry_refuses_without_overwrite(self) -> None:
        """R4/P4: con una corrida real previa (journal registra el target
        con su SHA final), un contenido del target cambiado por fuera del
        efecto registrado hace DIVERGENTE el retry: la operación se rehusa
        con diagnóstico, no sobrescribe y el state queda intacto (§7:
        «nunca repite ni sobrescribe un efecto divergente»)."""
        self.new_dispatched_project()
        self.establish_received()
        auth_path = self.write_authorization(self.build_authorization(
            [{"part": "role-report", "target": TARGET_REPORT,
              "expected_previous_sha256": None}]))
        first = self.materialize(auth_path)
        self.assertEqual(
            first.returncode, 0,
            msg=f"R4 (precondición): la corrida inicial debe publicar el "
                f"target y el journal: rc={first.returncode} "
                f"stderr={err_text(first)!r}")
        target = self.root / TARGET_REPORT
        self.assertEqual(
            target.read_bytes(), PART_BYTES,
            msg="R4 (precondición): target con los bytes originales")
        # divergencia externa del contenido ya registrado en el journal
        target.write_bytes(OTHER_BYTES)
        state_before = self.state_path.read_bytes()

        retry = self.materialize(auth_path)
        self.assertNotEqual(
            retry.returncode, 0,
            msg="R4: el retry divergente debe rehusarse sin sobrescribir "
                "(§7: nunca repite ni sobrescribe un efecto divergente)")
        assert_reachable_or_invalid_red(
            err_text(retry), "R4: conflicto por journal divergente")
        self.assertNotIn("Traceback", err_text(retry),
                         msg="R4: fallo con traceback")
        self.assertEqual(
            retry.stdout, b"",
            msg="R4: el rechazo no debe emitir evidencia por stdout")
        self.assertEqual(
            target.read_bytes(), OTHER_BYTES,
            msg="R4: el retry divergente NO debe sobrescribir el target")
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="R4: el retry divergente no toca el state")
        self.assertTrue(
            re.search(r"journal|conflict|diverg|contenido", err_text(retry),
                      re.IGNORECASE),
            msg="R4: el diagnóstico no nombra el journal/conflicto (§7): "
                f"{err_text(retry)!r}")


# ------------------------------------------------------------------- R5


class TestR5ScribeFileRoots(ReviewFixProjectCase):
    """R5 (lock): kinds del scribe — la raíz permitida es un ARCHIVO (§7)."""

    role = "scribe"
    substage = "memory"

    _PARTS = {
        "mb-projectbrief": (b"# Project brief (fixture T2 RF scribe)\n",
                            "scribe-projectbrief", "docs/projectbrief.md"),
        "mb-systemPatterns": (
            b"# System patterns (fixture T2 RF scribe)\n",
            "scribe-systemPatterns", "docs/systemPatterns.md"),
        "mb-activeContext": (
            b"# Active context (fixture T2 RF scribe)\n",
            "scribe-activeContext", "docs/activeContext.md"),
        "mb-progress": (b"# Progress (fixture T2 RF scribe)\n",
                        "scribe-progress", "docs/progress.md"),
    }

    def staged_parts(self) -> dict[str, bytes]:
        return {name: data for name, (data, _, _) in type(self)._PARTS.items()}

    def part_kind(self, name: str) -> str:
        return type(self)._PARTS[name][1]

    def test_r5_scribe_file_roots_materialize_all_memory_bank_files(self) -> None:
        """R5/P4: la fila `scribe` de la tabla §7 fija raíces que son
        ARCHIVOS concretos del Memory Bank (`docs/projectbrief.md`,
        `docs/systemPatterns.md`, `docs/activeContext.md`,
        `docs/progress.md`); materializar los cuatro kinds del scribe hacia
        su archivo raíz copia los bytes originales sin tocar el state."""
        self.new_dispatched_project()
        self.establish_received()
        state_before = self.state_path.read_bytes()
        copies = [
            {"part": name, "target": type(self)._PARTS[name][2],
             "expected_previous_sha256": None}
            for name in type(self)._PARTS
        ]
        proc = self.materialize(self.write_authorization(
            self.build_authorization(copies)))
        self.assertEqual(
            proc.returncode, 0,
            msg=f"R5: los kinds del scribe hacia sus raíces archivo deben "
                f"materializarse: rc={proc.returncode} "
                f"stdout={out_text(proc)!r} stderr={err_text(proc)!r}")
        for name, (data, _, target) in type(self)._PARTS.items():
            stored = self.root / target
            self.assertTrue(
                stored.is_file(), msg=f"R5: target del scribe {target}")
            self.assertEqual(
                stored.read_bytes(), data,
                msg=f"R5: el materializado {target!r} conserva los bytes "
                    "originales del part del scribe (§7 raíz archivo)")
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="R5: materialize no toca el state (§9)")


class TestR5ScribeCASMemoryBank(ReviewFixProjectCase):
    """R5 (lock): CAS de Memory Bank end-to-end (create-only → CAS)."""

    role = "scribe"
    substage = "memory"

    _A = b"# System patterns v1 (fixture T2 RF CAS)\n"
    _B = b"# System patterns v2 (fixture T2 RF CAS)\n"

    def staged_parts(self) -> dict[str, bytes]:
        return {"mb-v1": type(self)._A, "mb-v2": type(self)._B}

    def part_kind(self, name: str) -> str:
        return "scribe-systemPatterns"

    def test_r5_scribe_cas_memory_bank_end_to_end(self) -> None:
        """R5/P4: sobre un archivo del Memory Bank con kind del scribe, el
        ciclo completo CAS: primera autorización create-only publica los
        bytes; segunda autorización con `expected_previous_sha256` del
        digest exacto anterior REEMPLAZA el contenido (CAS §7) sin tocar
        state ni agregar aprobación."""
        self.new_dispatched_project()
        self.establish_received()
        target = "docs/systemPatterns.md"
        first = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "mb-v1", "target": target,
                  "expected_previous_sha256": None}])))
        self.assertEqual(
            first.returncode, 0,
            msg=f"R5 (precondición CAS): la autorización create-only debe "
                f"aplicarse: rc={first.returncode} stderr={err_text(first)!r}")
        self.assertEqual(
            (self.root / target).read_bytes(), type(self)._A,
            msg="R5 (precondición CAS): contenido inicial con bytes del "
                "part v1")
        state_before = self.state_path.read_bytes()

        cas = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "mb-v2", "target": target,
                  "expected_previous_sha256":
                      hashlib.sha256(type(self)._A).hexdigest()}])))
        self.assertEqual(
            cas.returncode, 0,
            msg=f"R5: el CAS de Memory Bank contra el digest anterior "
                f"exacto debe aplicar el reemplazo: rc={cas.returncode} "
                f"stdout={out_text(cas)!r} stderr={err_text(cas)!r}")
        self.assertEqual(
            (self.root / target).read_bytes(), type(self)._B,
            msg="R5: el CAS reemplazó el contenido end-to-end con los "
                "bytes del part v2")
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="R5: el CAS no toca el state (§9)")


class TestR5ReviewRow(SinglePartCase):
    """R5 (lock): fila reviewer (`review`) — rol read-only (§7)."""

    role = "reviewer"
    substage = "review"
    _STAGED = {"review": b"# Revision de T2 (fixture T2 RF review)\n"}
    _KINDS = {"review": "review"}
    _TARGET = ALLOWED_ROOT + "review-t2.md"

    def test_r5_review_row_materializes_declared_target(self) -> None:
        """R5/P4: el kind `review` del reviewer (obra read-only) se
        materializa hacia el target exacto declarado en la autorización
        bajo la raíz `docs/specs/<feature>/` sin tocar el state."""
        self.new_dispatched_project()
        self.establish_received()
        state_before = self.state_path.read_bytes()
        proc = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "review", "target": self._TARGET,
                  "expected_previous_sha256": None}])))
        self.assertEqual(
            proc.returncode, 0,
            msg=f"R5: la fila reviewer/review debe materializarse: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assert_target_bytes(self._TARGET, type(self)._STAGED["review"])
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="R5: materialize no toca el state (§9)")


class TestR5PlanReviewRow(SinglePartCase):
    """R5 (lock): fila reviewer (`plan-review`) con contrato draft-plan (§7)."""

    role = "reviewer"
    substage = "plan-review"
    attempt_id = "attempt-t2-reviewfix-plan-review-001"
    drafts_contract = (DRAFT_PLAN_RELPATH, "draft-plan", DRAFT_PLAN_VERSION)
    _STAGED = {"plan-review": b"# Plan review de T2 (fixture T2 RF)\n"}
    _KINDS = {"plan-review": "plan-review"}
    _TARGET = ALLOWED_ROOT + "review-plan-fit.md"

    def test_r5_plan_review_row_materializes_declared_target(self) -> None:
        """R5/P4: el kind `plan-review` del reviewer, sobre un paquete
        cuyo contrato es el draft-plan (procedimiento 004-003), se
        materializa hacia el target declarado bajo la raíz permitida sin
        tocar el state."""
        self.new_dispatched_project()
        self.establish_received()
        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(
            (receipt["role"], receipt["substage"]),
            ("reviewer", "plan-review"),
            msg="precondición: el recibo liga la fila plan-review")
        state_before = self.state_path.read_bytes()
        proc = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "plan-review", "target": self._TARGET,
                  "expected_previous_sha256": None}])))
        self.assertEqual(
            proc.returncode, 0,
            msg=f"R5: la fila reviewer/plan-review debe materializarse: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assert_target_bytes(self._TARGET,
                                 type(self)._STAGED["plan-review"])
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="R5: materialize no toca el state (§9)")


class TestR5AuditRow(SinglePartCase):
    """R5 (lock): fila test-writer audit — target fijo `test-audit.md` (§7)."""

    role = "test-writer"
    substage = "audit"
    _STAGED = {"audit-part": AUDIT_BYTES}
    _KINDS = {"audit-part": "test-audit"}

    def test_r5_audit_row_materializes_the_fixed_target(self) -> None:
        """R5/P4: el kind `test-audit` del test-writer AUDIT se materializa
        hacia su target fijo `test-audit.md` (tabla cerrada §7) sin tocar
        state ni agregar aprobación al recibo."""
        self.new_dispatched_project()
        self.establish_received()
        receipt_before = self.receipt_path.read_bytes()
        state_before = self.state_path.read_bytes()
        proc = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "audit-part", "target": TARGET_FIXED_AUDIT,
                  "expected_previous_sha256": None}])))
        self.assertEqual(
            proc.returncode, 0,
            msg=f"R5: la fila audit con target fijo debe materializarse: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        stored = self.root / TARGET_FIXED_AUDIT
        self.assertTrue(
            stored.is_file(),
            msg=f"R5: el target fijo {TARGET_FIXED_AUDIT} debe existir")
        self.assertEqual(
            stored.read_bytes(), AUDIT_BYTES,
            msg="R5: el materializado del audit conserva los bytes "
                "originales")
        self.assertEqual(
            self.receipt_path.read_bytes(), receipt_before,
            msg="R5: materialize no toca el receipt (sin aprobación)")
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="R5: materialize no toca el state (§9)")


class TestR5KindOutsideTable(WriterReportCase):
    """R5 (lock): kind fuera de la tabla cerrada rechazado (§7)."""

    # la fila test-writer no-audit lleva el kind fuera de la tabla
    _KINDS = {"role-report": "kind-not-in-closed-policy"}

    def test_r5_kind_outside_closed_table_is_rejected(self) -> None:
        """R5/P4: un part con kind que la tabla cerrada §7 no nombra debe
        rechazarse (E5-[B1] de la review) con diagnóstico que nombre el
        control (kind/policy) y sin target escrito ni state tocado."""
        self.new_dispatched_project()
        self.establish_received()
        state_before = self.state_path.read_bytes()
        proc = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "role-report", "target": TARGET_REPORT,
                  "expected_previous_sha256": None}])))
        self.assertNotEqual(
            proc.returncode, 0,
            msg="R5: un kind fuera de la tabla cerrada debe rechazarse")
        assert_reachable_or_invalid_red(
            err_text(proc), "R5: kind fuera de tabla")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="R5: fallo con traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg="R5: el rechazo no debe emitir evidencia por stdout")
        self.assertFalse(
            (self.root / TARGET_REPORT).exists(),
            msg="R5: el rechazo creó el target con kind fuera de tabla")
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="R5: el rechazo no toca el state")
        self.assertTrue(
            re.search(r"kind|artifact|pol[íi]tica|policy", err_text(proc),
                      re.IGNORECASE),
            msg="R5: el diagnóstico no nombra el kind/política (§7): "
                f"{err_text(proc)!r}")


class TestR5ApprovalEffectTrueRejected(WriterReportCase):
    """R5 (lock): `approval_effect` ≠ false debe ser rechazado (§7)."""

    def test_r5_approval_effect_true_is_rejected(self) -> None:
        """R5/P3-P4: «`approval_effect` siempre es false en esta feature»
        (§7): una autorización con true NO materializa: rechazo sin copia,
        sin stdout, diagnosticando la marca de aprobación (la aprobación
        requiere la decisión CDAD externa correspondiente)."""
        self.new_dispatched_project()
        self.establish_received()
        state_before = self.state_path.read_bytes()
        proc = self.materialize(self.write_authorization(
            self.build_authorization(
                [{"part": "role-report", "target": TARGET_REPORT,
                  "expected_previous_sha256": None}],
                approval_effect=True)))
        self.assertNotEqual(
            proc.returncode, 0,
            msg="R5: approval_effect=true debe rechazarse (§7)")
        assert_reachable_or_invalid_red(
            err_text(proc), "R5: approval_effect=true")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="R5: fallo con traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg="R5: el rechazo no debe emitir evidencia por stdout")
        self.assertFalse(
            (self.root / TARGET_REPORT).exists(),
            msg="R5: el rechazo aplicó la copia con approval_effect=true")
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="R5: el rechazo no toca el state")
        self.assertTrue(
            re.search(r"approval|aprob|effect", err_text(proc),
                      re.IGNORECASE),
            msg="R5: el diagnóstico no nombra approval_effect (§7): "
                f"{err_text(proc)!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
