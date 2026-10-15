#!/usr/bin/env python3
"""003-004 T2 RED — write-ahead + `reconcile` + conflictos de clave (P3, O1, R-B1, R-B2).

Contract:
- docs/specs/003-004-context-continuity/spec.md (§2 matriz, §3 D6/O1,
  criterios 3 y 4; P3; dejar sembrada la señal para P8-fixtures).
- docs/specs/003-004-context-continuity/plan.md (T2; focales declarados
  `tests/test_003_004_t2_writeahead.py` y `tests/test_003_004_t2_reconcile.py`;
  "begin divergente con la misma clave → conflicto/escalado sin sobrescribir",
  "autoridad vencida no escribe checkpoint").
- docs/specs/003-004-context-continuity/review-t1-rereview.md (residuos
  R-B1: cuerpo malformado → rc≠0 en `begin`; R-B2: `--role` sin política
  → rc≠0) y review-t1-decision.md (O1: planificado para T2, criterio 3).

Superficie observable bajo prueba (V6 — formas fijadas en RED;
`begin`/`checkpoint` ya existen de T1, `reconcile` es NUEVO de T2):

    python3 scripts/cdad_continuity.py begin \
        --project-root ROOT --execution-context EXEC.json \
        --update UPDATE.json [--max-bytes N] [--json]
    python3 scripts/cdad_continuity.py checkpoint … idem
    python3 scripts/cdad_continuity.py reconcile \
        --project-root ROOT --execution-context EXEC.json \
        --packet PACKET_ID [--json]

Envolvente JSON de `reconcile` (contract `reconcile-v1`, fijada en RED
para GREEN/reviewer):

    {
      "schema_version": 1,
      "reconcile": "reconcile-v1",
      "execution_id": "...", "packet_id": "...",
      "classification": "not-started" | "dispatched-unknown" | "received"
                      | "already-closed" | "expired-authority"
                      | "split-brain" | "stale" | "unknown",
      "repeat_effect": false,
      "escalate": false,
      "authority": {"authority_ref": "...", "expires_on": "...",
                    "state": "current" | "expired" | "unknown"},
      "head": {"seq": <int>, "body_sha256": "<sha>"} | null,
      "reasons": ["…"],
      "unknowns": ["…"]   // no vacío cuando classification == "unknown"
    }

`reconcile` es read-only y determinista (§3): reporta el estado; el juicio
y la escritura del state siguen siendo del orquestador (invariante 1).
Con la autoridad vencida NO autoriza ni dispatch ni materialize (D4/D6).

Este archivo (T2 write-ahead) cubre:
- P3/D6 (write-ahead): `begin` persiste el head ANTES de despachar y
  `reconcile` lo consume sin señalar intervención (escenario
  no-dispachado: `not-started`), nunca falla por artefacto ausente que
  no es obligatorio (O1: sin `ACTIVE.json` persistida).
- O1 / criterio 3 (faceta divergente, plan.md T2): `begin` con la MISMA
  clave `(execution_id, packet_id, attempt)` y cuerpo canónico
  DIVERGENTE del head → conflicto/escalado: rc≠0, head INTACTO (sin
  sobrescribir, sin duplicar cadena, `seq` sin crecer).
- R-B1 (residuo de review-t1, rereview B1): cuerpo malformado en
  `begin`/`checkpoint` (goal no string|null, decisions sin rationale,
  uncertainties con no-string, next_action no string|null) → rc≠0
  fail-closed, el diagnóstico nombra el campo, NADA persistido.
- Autoridad vencida (plan T2): `begin`/`checkpoint` con delegación HITL
  expirada → rc≠0 y sin checkpoint (la escritura no procede).

El resto de la matriz de §2 (dispatched-unknown, received,
already-closed, stale/tamper, split-brain, unknown y el escenario
continuo legítimo) vive en `tests/test_003_004_t2_reconcile.py` junto a
los fixtures etiquetados SIMULACIÓN de `tests/fixtures/003_004/`.

Fixtures: proyecto sintético en tmp (execution context, update y
política PROPIOS, deterministas); stores de 002/004 sembrados
exclusivamente como DATOS (nunca se corren los flujos reales 002/004 y
no se provoca incidente real); ninguna escritura en este repo.

RED hoy (probes observables del CLI actual, 2026-10-07): `reconcile` no
existe (invalid choice); `begin` divergente con la misma clave SOBRE-
SCRIBE el head y crece la cadena (rc 0, O1 abierto); un cuerpo malformado
se acepta rc 0 (R-B1); `--role` sin política sigue rc 0 (R-B2, cubierto
en el archivo reconcile). Cada aserción positiva fracasa por compor-
tamiento ausente/incorrecto (AssertionError con el elemento violado
nombrado), nunca por ImportError ni sintaxis — el test no importa el
módulo del CLI.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_SCRIPT = REPO_ROOT / "scripts" / "cdad_continuity.py"  # wrapper

FEATURE_ID = "003-004-context-continuity"

EXEC_ID = "exec-003-004-t2-red-001"
PACKET_ID = "003-004-context-continuity-implementer-t2-001"

AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"

CLI_TIMEOUT_S = 120

CONTINUITY_DIR_REL = f".cdad/executions/{EXEC_ID}/continuity"
HEAD_REL = f"{CONTINUITY_DIR_REL}/head.json"
STATE_REL = "docs/.cdad-state.json"
ACTIVE_REL = "ACTIVE.json"  # proceso on-demand (O1): nunca persistida


# ---------------------------------------------------------------- fixtures


def exec_context_fixture(**extra: object) -> dict:
    """Execution context mínimo (001) con delegación HITL vigente."""
    doc = {
        "schema_version": 1,
        "execution_id": EXEC_ID,
        "runtime": "opencode",
        "hitl_delegation": {
            "authority_ref": AUTHORITY_REF,
            "expires_on": "2099-12-31",
        },
    }
    doc.update(extra)
    return doc


def update_fixture(**overrides: object) -> dict:
    """Cuerpo D11 válido (forma de T1): packet_id + attempt + contenido."""
    doc = {
        "packet_id": PACKET_ID,
        "attempt": 1,
        "goal": "T2: write-ahead y reconcile de 003-004-context-continuity",
        "decisions": [
            {"decision": "V6 fijado en RED",
             "rationale": "la forma del CLI se declara en el RED y "
                          "el GREEN la implementa"},
        ],
        "uncertainties": ["V2: status de sesión no distingue vivo-estancado"],
        "next_action": "reconciliar antes de cualquier reintento (D6)",
        "references": [],
    }
    doc.update(overrides)
    return doc


# ---------------------------------------------------------------- helpers


class WriteAheadCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con la superficie real de T1."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-004-t2wa-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)
        self.exec_context = self.write_json("fixture/exec.json",
                                            exec_context_fixture())

    # -- construcción del proyecto fixture --------------------------------

    def write_json(self, rel: str, doc: dict) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    def write_update(self, doc: dict, name: str = "update.json") -> Path:
        return self.write_json(f"fixture/{name}", doc)

    def exec_context_path(self, **overrides: object) -> Path:
        return self.write_json("fixture/exec.json",
                               exec_context_fixture(**overrides))

    # -- corridas del CLI --------------------------------------------------

    def run_cli(self, *argv: str) -> subprocess.CompletedProcess:
        """Corrida acotada, stdin cerrado ( foreground real, sin background)."""
        try:
            return subprocess.run(
                [sys.executable, str(CONTINUITY_SCRIPT), *argv],
                cwd=REPO_ROOT, capture_output=True, timeout=CLI_TIMEOUT_S,
                stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P3 (acotado): el CLI no terminó dentro de "
                f"{CLI_TIMEOUT_S}s — un comando determinista nunca puede "
                f"colgarse; got timeout={exc!r}")

    def run_write(self, command: str, update: Path,
                  exec_context: Path | None = None,
                  ) -> subprocess.CompletedProcess:
        return self.run_cli(command, "--project-root", str(self.root),
                            "--execution-context",
                            str(exec_context or self.exec_context),
                            "--update", str(update), "--json")

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str) -> None:
        """RED: el fracaso debe ser el comportamiento ausente, con mensaje
        explícito — nunca un fallo de import o sintaxis."""
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(
            "invalid choice", out + err,
            msg=f"P3: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv `cdad_continuity.py " + which +
                " --project-root --execution-context --packet` declarado en "
                "§3 (V6) es obligatorio")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P3: el comando `{which}` no existe aún (RED por CLI "
                f"ausente); rc={proc.returncode} "
                f"stdout={out!r} stderr={err!r}")
        self.assertNotIn(
            "Traceback", err, msg=f"P3: `{which}` terminó con traceback")

    def write_envelope(self, proc: subprocess.CompletedProcess,
                       which: str) -> dict:
        self.assert_command_exists(proc, which)
        return json.loads(proc.stdout.decode("utf-8"))

    # -- observación de stores --------------------------------------------

    def store_files(self) -> dict[str, bytes]:
        """Snapshot {rel: bytes} del proyecto (stores reales y producto)."""
        return {
            str(p.relative_to(self.root)): p.read_bytes()
            for p in sorted(self.root.rglob("*"))
            if p.is_file() and not str(p.relative_to(self.root)).startswith(
                ("fixture/",))
        }

    def head_bytes(self) -> bytes | None:
        head = self.root / HEAD_REL
        return head.read_bytes() if head.is_file() else None

    def head_document(self) -> dict:
        raw = self.head_bytes()
        self.assertIsNotNone(
            raw, msg="precondición: el head persistido existe en "
                     f"`{HEAD_REL}`")
        return json.loads(raw)


# ---------------------------------------------------------------- tests


class TestP3WriteAheadConsumeReconcile(WriteAheadCase):
    """P3/D6 — el head del write-ahead precede al despacho y `reconcile`
    lo consume sin intervención ni error por artefacto no obligatorio."""

    def test_p03_writeahead_head_procede_al_despacho_y_reconcile_lo_consume(
            self) -> None:
        """P3/D6: `begin` persiste el head ANTES de que exista ningún
        despacho; `reconcile` sobre ese estado lo clasifica como
        `not-started` (rc 0, SIN intervención, `repeat_effect` false) y
        NUNCA falla por ausencia de `ACTIVE.json` (memoria activa =
        proyección on-demand, O1: no hay proceso persistido)."""
        update = self.write_update(update_fixture())
        self.write_envelope(self.run_write("begin", update), "begin")

        head_raw = self.head_bytes()
        self.assertIsNotNone(
            head_raw,
            msg="P3/D6 (precondición): el write-ahead `begin` persistió "
                "el head ANTES de despachar nada (cero dispatches en el "
                "proyecto)")
        self.assertFalse(
            list((self.root / ".cdad/executions" / EXEC_ID
                  / "dispatches").glob("*"))
            if (self.root / ".cdad/executions" / EXEC_ID
                / "dispatches").exists() else [],
            msg="precondición: ningún despacho registrado aún")

        proc = self.run_cli("reconcile", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--packet", PACKET_ID, "--json")
        env = self.write_envelope(proc, "reconcile")

        self.assertEqual(
            env.get("reconcile"), "reconcile-v1",
            msg=f"P3: la envolvente declara el contract `reconcile-v1`; "
                f"got {env!r}")
        self.assertEqual(
            env.get("classification"), "not-started",
            msg=f"P3: con el head write-ahead y SIN despacho/receipt el "
                f"trabajo se clasifica `not-started`; got "
                f"{env.get('classification')!r} (full={env!r})")
        self.assertFalse(
            env.get("repeat_effect"),
            msg=f"P3: `repeat_effect` es false sin nada que reconciliar; "
                f"got {env.get('repeat_effect')!r}")
        self.assertFalse(
            env.get("escalate"), msg="P3: no se escala un flujo sano")

        # O1: la ausencia de la proyección persistida NO es error de
        # reconcile (nunca hubo `ACTIVE.json` en este proyecto).
        self.assertFalse(
            (self.root / ACTIVE_REL).exists(),
            msg="O1 (control del fixture): este proyecto nunca persiste "
                "ACTIVE.json — su ausencia debe seguir sin ser un error")


class TestO1BeginDivergenteMismaClave(WriteAheadCase):
    """O1 / criterio 3 / plan T2 — conflicto sin sobrescribir (D7).

    ENMIENDA RU-2 (2026-10-08; docs/specs/003-006-runtime-adoption/
    t4-ru2-decision.md, cerrada junto al RED focal
    tests/test_003_006_t4_ru2_refused_write.py): el cierre "un `begin` o
    un `checkpoint` rechazado no escribe nada: ni cuerpo, ni cabeza, ni
    directorios nuevos (todo o nada)" corrige el defecto que este test
    fijaba originalmente (el cuerpo divergente QUEDABA escrito y
    `reconcile` daba split-brain para siempre). Mantenido: rc≠0 del
    rechazo, su mensaje, head intacto, `seq` estable. Cambiado por la
    enmienda: NINGÚN archivo nuevo en el store y `reconcile --packet`
    de la clave → rc=0 SIN split-brain."""

    def test_o1_begin_divergente_misma_clave_conflicto_sin_sobrescribir(
            self) -> None:
        """O1 (criterio 3, faceta divergente; plan T2 "begin divergente
        con la misma clave → conflicto/escalado sin sobrescribir"): un
        `begin` con la MISMA clave `(execution_id, packet_id, attempt)`
        y cuerpo canónico DIVERGENTE del head falla (rc≠0) con mensaje
        de rechazo del conflicto, NO sobrescribe el head (bytes
        intactos) y NO duplica la cadena (`seq` del head sin crecer).

        ENMIENDA RU-2 (2026-10-08; docs/specs/003-006-runtime-adoption/
        t4-ru2-decision.md): el rechazo es todo-o-nada — el cuerpo
        divergente NO queda escrito (la cola original de este docstring
        fijaba el defecto: el begin divergente se aceptaba rc=0 en el
        RED de 003-004 y, tras su T2, dejaba el cuerpo + split-brain
        permanente). La clave conserva UN ÚNICO cuerpo, así que
        `reconcile --packet` ya NO queda bloqueado en split-brain
        (rc=0, clasificación sin error de divergencia: un rechazo no
        convierte un error de uso en un bloqueo permanente)."""
        update = self.write_update(update_fixture())
        self.write_envelope(self.run_write("begin", update), "begin")
        head_before = self.head_bytes()
        head_doc_before = self.head_document()
        store_before = self.store_files()
        self.assertEqual(
            head_doc_before.get("seq"), 1,
            msg="O1 (precondición): el head arranca con seq 1")
        self.assertEqual(
            head_doc_before.get("attempt"), 1,
            msg="O1 (precondición): la clave en juego tiene attempt 1")

        divergent = self.write_update(
            update_fixture(
                goal="VARIANTE divergente del MISMO attempt 1 "
                     "(sesión bifurcada simulada — fixture de datos)"),
            name="update-divergente.json")

        proc = self.run_write("begin", divergent)
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"O1/criterio 3: un begin divergente con la misma clave "
                f"debe fallar (conflicto/escalado, rc≠0); got "
                f"rc={proc.returncode} stdout={out!r} stderr={err!r}")
        self.assertIn(
            "split-brain", out + err,
            msg="O1/D7: el rechazo del begin divergente nombra el "
                "conflicto (split-brain); no un rc≠0 incidental por "
                f"otra causa; got stdout={out!r} stderr={err!r}")

        self.assertEqual(
            self.head_bytes(), head_before,
            msg="O1/criterio 3: el conflicto NO sobrescribe el head — "
                "los bytes del head son EXACTAMENTE los del checkpoint "
                "previo")
        self.assertEqual(
            self.head_document().get("seq"),
            head_doc_before.get("seq"),
            msg="O1/criterio 3: la cadena NO se duplica ni crece con el "
                "begin divergente (seq intacta)")

        # ENMIENDA RU-2 (todo o nada): el begin divergente RECHAZADO no
        # escribe nada — el store queda byte a byte igual (ningún
        # cuerpo huérfano nuevo en continuity/bodies/, head intacto,
        # ningún directorio nuevo).
        self.assertEqual(
            self.store_files(), store_before,
            msg="RU-2 (todo o nada): el begin divergente RECHAZADO no "
                "escribe nada — el store del proyecto queda byte a byte "
                "igual que antes del rechazo (ningún cuerpo nuevo en "
                "continuity/bodies/, ningún directorio nuevo)")

        # ENMIENDA RU-2: con un único cuerpo para la clave, la sesión
        # real queda determinada por el head ORIGINAL y `reconcile`
        # ya NO escala split-brain (un rechazo no deja divergencia
        # permanente): rc=0, clasificación sin error de divergencia.
        proc_recon = self.run_cli(
            "reconcile", "--project-root", str(self.root),
            "--execution-context", str(self.exec_context),
            "--packet", PACKET_ID, "--json")
        combined_recon = (
            proc_recon.stdout.decode("utf-8", errors="replace")
            + proc_recon.stderr.decode("utf-8", errors="replace"))
        self.assertNotIn(
            "invalid choice", combined_recon,
            msg="O1/RU-2: el comando `reconcile` no existe (RED por CLI "
                "ausente): el argv declarado en §3 (V6) es obligatorio")
        self.assertNotIn(
            "Traceback", combined_recon,
            msg="O1/RU-2: `reconcile` terminó con traceback sin manejar")
        self.assertEqual(
            proc_recon.returncode, 0,
            msg="RU-2: tras un rechazo todo-o-nada, `reconcile --packet` "
                "de la clave NO queda bloqueado en split-brain (rc=0); "
                f"got rc={proc_recon.returncode} "
                f"stdout={proc_recon.stdout!r} "
                f"stderr={proc_recon.stderr!r}")
        env_recon = json.loads(proc_recon.stdout.decode("utf-8"))
        self.assertNotEqual(
            env_recon.get("classification"), "split-brain",
            msg=f"RU-2: la clasificación NO es split-brain (no hay dos "
                f"cuerpos para la misma clave); got "
                f"{env_recon.get('classification')!r} "
                f"(full={env_recon!r})")
        self.assertNotIn(
            "divergent checkpoint heads", combined_recon,
            msg="RU-2: la salida de `reconcile` NO contiene el error de "
                "divergencia permanente (`divergent checkpoint heads`); "
                f"got stdout+stderr={combined_recon[:400]!r}")


class TestRB1CuerpoMalformado(WriteAheadCase):
    """R-B1 (residuo rereview B1) — cuerpo malformado → fail-closed."""

    def test_rb1_cuerpo_malformado_falla_cerrado_y_persiste_nada(
            self) -> None:
        """R-B1: los campos de contenido del cuerpo D11 viajan SIN validar
        hoy (probe A1 de la rereview: proyección con 4 violaciones a
        active-record-v1). T2 consume esta proyección (`reconcile-v1`),
        por lo que el cierre es fail-closed en `begin`/`checkpoint`:
        goal (string|null), decisions[] (decision+rationale strings),
        uncertainties[] (strings) y next_action (string|null) — rc≠0 con
        el campo nombrado, sin persistir un head NUNCA (mismo mecanismo
        fail-closed que O2)."""
        malformed_bodies: dict[str, dict] = {
            "goal-no-string": update_fixture(goal=42),
            "decision-sin-rationale": update_fixture(
                decisions=[{"decision": "d sin razón"}]),
            "uncertainty-no-string": update_fixture(
                uncertainties=["v1 válida", 7]),
            "next-action-no-string": update_fixture(next_action=5),
        }
        for name, bad_body in malformed_bodies.items():
            with self.subTest(cuerpo=name):
                self.setUp()  # proyecto fresco por caso
                bad_path = self.write_update(bad_body,
                                             name=f"update-{name}.json")
                proc = self.run_write("begin", bad_path)
                out = proc.stdout.decode("utf-8", errors="replace")
                err = proc.stderr.decode("utf-8", errors="replace")

                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"R-B1: el cuerpo malformado `{name}` debe fallar "
                        f"cerrado (rc≠0); got rc={proc.returncode} "
                        f"stdout={out!r} stderr={err!r}")
                self.assertFalse(
                    self.store_files(),
                    msg=f"R-B1: NADA persistido para el cuerpo malformado "
                        f" `{name}` (fail-closed: sin head truncado ni "
                        f"cuerpo huérfano)")
                # El delta nombra el campo violado (mismo estándar que O2).
                field = {
                    "goal-no-string": "goal",
                    "decision-sin-rationale": "rationale",
                    "uncertainty-no-string": "uncertainties",
                    "next-action-no-string": "next_action",
                }[name]
                self.assertIn(
                    field, out + err,
                    msg=f"R-B1: el diagnóstico del cuerpo `{name}` nombra "
                        f"el campo violado ({field!r}); got stdout={out!r} "
                        f"stderr={err!r}")

                # El subcomando `checkpoint` (T2, write-ahead posterior)
                # comparte el mismo fail-closed.
                proc_ckpt = self.run_write("checkpoint", bad_path)
                self.assertNotEqual(
                    proc_ckpt.returncode, 0,
                    msg=f"R-B1: `checkpoint` también rechaza el cuerpo "
                        f"malformado `{name}` (la proyección congelada "
                        f"nunca viola active-record-v1); got "
                        f"rc={proc_ckpt.returncode}")


class TestAutoridadVencidaNoEscribe(WriteAheadCase):
    """Plan T2 — «autoridad vencida no escribe checkpoint» (D4/D6)."""

    def test_d4_autoridad_vencida_no_persiste_checkpoint(self) -> None:
        """D4/plan T2: una delegación HITL expirada (`expires_on` en el
        pasado) puede reconstruir contexto pero NO escribe checkpoints:
        `begin` falla cerrado (rc≠0) y el store queda vacío (la escritura
        no procede; el orquestador decide — el CLI nunca aprueba)."""
        expired_context = self.exec_context_path(
            hitl_delegation={
                "authority_ref": AUTHORITY_REF,
                "expires_on": "2020-01-01",
            })
        update = self.write_update(update_fixture())

        proc = self.run_write("begin", update, exec_context=expired_context)
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"D4/plan T2: begin/checkpoint con autoridad vencida no "
                f"escribe checkpoint (rc≠0); got rc={proc.returncode} "
                f"stdout={out!r} stderr={err!r}")
        self.assertFalse(
            self.store_files(),
            msg="D4/plan T2: sin checkpoint persistido con autoridad "
                "vencida (falla cerrado)")
        self.assertIn(
            "expires_on", out + err,
            msg=f"D4: el diagnóstico cita la vigencia (`expires_on`); "
                f"got stdout={out!r} stderr={err!r}")

        proc_ckpt = self.run_write("checkpoint", update,
                                   exec_context=expired_context)
        self.assertNotEqual(
            proc_ckpt.returncode, 0,
            msg="D4/plan T2: `checkpoint` tampoco escribe con autoridad "
                f"vencida; got rc={proc_ckpt.returncode} "
                f"stdout={proc_ckpt.stdout!r}")


if __name__ == "__main__":
    unittest.main()
