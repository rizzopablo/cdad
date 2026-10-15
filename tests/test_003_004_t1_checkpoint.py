#!/usr/bin/env python3
"""003-004 T1 RED — checkpoint inmutable + `begin` idempotente + cap (P1, P7).

Contract:
- docs/specs/003-004-context-continuity/spec.md (§3 firma V6, P1, P7,
  invariante 1; criterios de aceptación 2? no — este archivo cubre
  criterios 3 y 8; los negativos de tamper (criterio 2) y P2/P5 viven en
  `tests/test_003_004_t1_resume.py`).
- docs/specs/003-004-context-continuity/plan.md (T1; focales declarados
  `tests/test_003_004_t1_checkpoint.py` y `tests/test_003_004_t1_resume.py`).

Superficie observable bajo prueba (V6: forma del CLI fijada en RED; §3):

    python3 scripts/cdad_continuity.py begin \
        --project-root ROOT --execution-context EXEC.json \
        --update UPDATE.json [--max-bytes N] [--json]
    python3 scripts/cdad_continuity.py checkpoint \
        --project-root ROOT --execution-context EXEC.json \
        --update UPDATE.json [--max-bytes N] [--json]

Decisiones de superficie fijadas por este RED (V6 — declaradas para el
GREEN/reviewer):

- El wrapper invocado es `scripts/cdad_continuity.py` (misma convención
  que `scripts/cdad_guard.py` en 003-003).
- Envolvente JSON (`--json`, contract `continuity-checkpoint-v1`):

      {
        "schema_version": 1,
        "checkpoint": "continuity-checkpoint-v1",
        "execution_id": "...", "packet_id": "...", "attempt": 1,
        "seq": 1,
        "body_sha256": "<sha256 del cuerpo canónico>",
        "prev_checkpoint_sha256": null | "<sha256>",
        "references": [{"path": "<relativa a ROOT>",
                        "sha256": "<sha256 del contenido>"}],
        "bytes": <tamaño de la proyección>,
        "max_bytes": <cap aplicado>,
        "no_op": false
      }

- El head inmutable se persiste en
  `.cdad/executions/<execution_id>/continuity/head.json` (contenido = el
  documento del checkpoint); es el artefacto que `resume` verifica.
- `--update` viaja D11: claves `goal`, `decisions` (cada una con
  `rationale`), `uncertainties`, `next_action` y `references` (lista de
  rutas relativas a ROOT, contenido existente al checkpointear).
- Determinismo: el cuerpo canónico NO embebe rutas absolutas ni marcas
  de tiempo (mismo input en dos proyectos distintos → mismo
  `body_sha256`; checkpoint portable, D8/O2).

Este archivo (T1 checkpoint) cubre:
- P1 (estructura observable): round-trip determinista (mismo input →
  mismo digest), cadena `seq`/`prev_checkpoint_sha256` y `references[]`
  con digest del contenido.
- Invariante 1: `begin`/`checkpoint` escriben SÓLO bajo
  `.cdad/executions/<id>/continuity/**` (nunca `docs/.cdad-state.json`).
- Criterio 3 (faceta asignada: SÓLO el no-op idéntico): `begin` con
  cuerpo canónico idéntico al head → no-op rc 0, sin artefacto nuevo.
- P7 / criterio 8: exceder `--max-bytes` falla cerrado sin truncar
  (default 16 KiB), sin checkpoint persistido.

Fuera de este archivo (otro focal): criterio 2 (los cuatro negativos de
tamper vía `resume`), P2 (reanudación frío) y P5 (rol) en
`test_003_004_t1_resume.py`; conflicto de `begin` divergente (criterio 3,
otra faceta) en T2.

Fixtures: proyecto sintético en tmp con execution context y update
PROPIOS, deterministas; ninguna escritura en este repo; no se provoca
ningún incidente real (matriz de simulación es T2).

RED hoy: `scripts/cdad_continuity.py` no existe aún; cada aserción
positiva fracasa por comportamiento ausente (AssertionError con el
mensaje `el comando no existe aún`), nunca por ImportError ni sintaxis —
el test no importa el módulo del CLI.
"""

from __future__ import annotations

import hashlib
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

EXEC_ID = "exec-003-004-t1-red-001"
PACKET_ID = "003-004-context-continuity-implementer-green-001"

AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"

# Tope duro: un CLI determinista nunca puede colgarse (acotado).
CLI_TIMEOUT_S = 120

# Cap por defecto declarado en la spec (P7).
DEFAULT_MAX_BYTES = 16 * 1024

CONTINUITY_DIR_REL = f".cdad/executions/{EXEC_ID}/continuity"
HEAD_REL = f"{CONTINUITY_DIR_REL}/head.json"
STATE_REL = "docs/.cdad-state.json"


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
    """Contenido D11 del cuerpo: lo que queda congelado en el checkpoint."""
    doc = {
        "packet_id": PACKET_ID,
        "attempt": 1,
        "goal": "Implementar cdad_continuity.py begin/checkpoint/resume "
                "(T1 de 003-004-context-continuity)",
        "decisions": [
            {"decision": "CLI stdlib determinista, sin servicio",
             "rationale": "D1 de la spec: sin agente permanente"},
        ],
        "uncertainties": ["V1: tokens de step-finish ¿por paso o acumulados?"],
        "next_action": "Correr el focal RED y pasar a GREEN",
        "references": [],
    }
    doc.update(overrides)
    return doc


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------- helpers


class ContinuityProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con execution context y update propios."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-004-t1-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)
        self.exec_context = self.write_json("fixture/exec.json",
                                            exec_context_fixture())

    def write_json(self, rel: str, doc: dict) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    def write_reference(self, rel: str, content: str) -> Path:
        """Referencia L3 existente bajo el proyecto (fixture)."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_update(self, doc: dict) -> Path:
        return self.write_json("fixture/update.json", doc)

    def run_cli(self, *argv: str) -> subprocess.CompletedProcess:
        """Corrida del CLI (V7) con tope de tiempo y stdin cerrado."""
        try:
            return subprocess.run(
                [sys.executable, str(CONTINUITY_SCRIPT), *argv],
                cwd=REPO_ROOT, capture_output=True, timeout=CLI_TIMEOUT_S,
                stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P1 (acotado): el CLI no terminó dentro de "
                f"{CLI_TIMEOUT_S}s — un comando determinista nunca puede "
                f"colgarse; got timeout={exc!r}")

    def run_write(self, command: str, update: Path,
                  max_bytes: int | None = None) -> subprocess.CompletedProcess:
        argv = [command, "--project-root", str(self.root),
                "--execution-context", str(self.exec_context),
                "--update", str(update), "--json"]
        if max_bytes is not None:
            argv += ["--max-bytes", str(max_bytes)]
        return self.run_cli(*argv)

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str) -> None:
        """RED: el fracaso debe ser el comportamiento ausente, con mensaje
        explícito — nunca un fallo de import o sintaxis."""
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(
            "invalid choice", out + err,
            msg=f"P1: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv `cdad_continuity.py " + which +
                " --project-root --execution-context --update` declarado "
                "en §3 (V6) es obligatorio")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P1: el comando `{which}` no existe aún (RED por CLI "
                f"ausente); rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertNotIn(
            "Traceback", err,
            msg=f"P1: `{which}` terminó con traceback "
                f"stderr={err!r}")

    def write_envelope(self, proc: subprocess.CompletedProcess,
                       which: str) -> dict:
        self.assert_command_exists(proc, which)
        return json.loads(proc.stdout.decode("utf-8"))

    def assert_writes_confined_to_continuity(self) -> None:
        """Invariante 1: los archivos nuevos del proyecto (fuera de los
        fixtures declarados) viven bajo `continuity/` y NUNCA se crea
        `docs/.cdad-state.json` (el orquestador es su único escritor)."""
        self.assertFalse(
            (self.root / STATE_REL).exists(),
            msg="P1/Invariante 1: el CLI nunca escribe docs/.cdad-state.json")
        fixture_prefixes = ("fixture/",)
        foreign = [
            str(p.relative_to(self.root)) for p in self.root.rglob("*")
            if p.is_file()
            and not str(p.relative_to(self.root)).startswith(fixture_prefixes)
        ]
        allowed_prefix = CONTINUITY_DIR_REL + "/"
        self.assertTrue(
            all(rel.startswith(allowed_prefix) for rel in foreign),
            msg=f"P1/Invariante 1: begin/checkpoint escriben SÓLO bajo "
                f"`{CONTINUITY_DIR_REL}/**`; archivos fuera de ese "
                f"prefijo: {foreign!r}")

    def continuity_files(self) -> dict[str, bytes]:
        """Snapshot {ruta relativa: bytes} del store de continuity."""
        base = self.root / CONTINUITY_DIR_REL
        if not base.exists():
            return {}
        return {
            str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()
        }


# ---------------------------------------------------------------- tests


class TestP1RoundTripDeterminista(ContinuityProjectCase):
    """P1 — mismo input → mismo digest; escritura confinada (inv. 1)."""

    def test_p1_round_trip_determinista_y_escritura_confinada(self) -> None:
        """P1/inv.1: dos proyectos independientes con el MISMO
        execution context + update producen el MISMO `body_sha256`
        (el cuerpo canónico no embebe rutas absolutas ni timestamps);
        `seq` arranca en 1 con `prev_checkpoint_sha256` null; y la
        escritura queda confinada a `continuity/**`."""
        digests: list[str] = []
        for _ in range(2):
            fresh_tmp = tempfile.mkdtemp(prefix="cdad-003-004-t1-rt-")
            self.addCleanup(
                lambda: subprocess.run(["rm", "-rf", fresh_tmp],
                                       check=False))
            self.root = Path(fresh_tmp) / "proj"
            self.root.mkdir(parents=True, exist_ok=True)
            self.exec_context = self.write_json(
                "fixture/exec.json", exec_context_fixture())
            update = self.write_update(update_fixture())

            proc = self.run_write("begin", update)
            env = self.write_envelope(proc, "begin")
            self.assert_writes_confined_to_continuity()

            self.assertEqual(
                env.get("checkpoint"), "continuity-checkpoint-v1",
                msg=f"P1: la envolvente declara el contract "
                    f"`continuity-checkpoint-v1`; got {env!r}")
            self.assertEqual(
                env.get("seq"), 1,
                msg=f"P1: el primer checkpoint de la cadena tiene seq 1; "
                    f"got {env.get('seq')!r}")
            self.assertIsNone(
                env.get("prev_checkpoint_sha256"),
                msg=f"P1: el primer checkpoint no tiene predecesor "
                    f"(cadena vacía → null); got "
                    f"{env.get('prev_checkpoint_sha256')!r}")
            self.assertEqual(
                env.get("no_op"), False,
                msg=f"P1: un begin nuevo (sin head previo) NO es no-op; "
                    f"got {env.get('no_op')!r}")
            body_sha = env.get("body_sha256")
            self.assertIsInstance(
                body_sha, str, msg="P1: la envolvente expone `body_sha256`")
            self.assertEqual(
                len(body_sha), 64,
                msg=f"P1: `body_sha256` es un digest sha256 hex; got "
                    f"{body_sha!r}")
            digests.append(body_sha)

        self.assertEqual(
            digests[0], digests[1],
            msg=f"P1 (round-trip determinista): mismo input → mismo "
                f"digest; got {digests!r} (¿el cuerpo canónico embebe "
                f"rutas absolutas o timestamps?)")


class TestP1CadenaYReferencias(ContinuityProjectCase):
    """P1 — cadena seq/prev y referencias con digest del contenido."""

    def test_p1_segundo_checkpoint_encadena_y_digesta_referencias(
            self) -> None:
        """P1: un segundo `checkpoint` con cuerpo nuevo encadena
        `prev_checkpoint_sha256` = body_sha256 del head previo y `seq` 2;
        cada referencia declarada en `--update` queda registrada con el
        sha256 de su contenido real (no se fabrica).

        Cambio de contrato P3 (003-007-living-continuity, declarado en
        docs/specs/003-007-living-continuity/t1-green-decision.md): cada
        entrada de `references` lleva además la `class` estampada
        (`contract` para la forma string) — se exige path y sha256
        EXACTOS como antes, y la `class` resuelta `contract`."""
        ref_path = self.write_reference(
            "fixture/notes.md",
            "Historia L3 por referencia: estado 001, receipts 002.\n")
        update1 = self.write_update(update_fixture(
            references=["fixture/notes.md"]))

        env1 = self.write_envelope(self.run_write("begin", update1), "begin")
        self.assertEqual(
            env1.get("seq"), 1, msg="P1 (precondición): primer head seq 1")
        first_sha = env1.get("body_sha256")
        refs1 = env1.get("references")
        self.assertIsInstance(
            refs1, list, msg=f"P1: la envolvente expone `references`; got "
                             f"{refs1!r}")
        self.assertEqual(
            len(refs1), 1,
            msg=f"P1: la unica referencia declarada se registra; got "
                f"{refs1!r}")
        entry = refs1[0]
        self.assertEqual(
            entry.get("path"), "fixture/notes.md",
            msg=f"P1: la referencia se registra con su path relativo "
                f"EXACTO; got {entry!r}")
        self.assertEqual(
            entry.get("sha256"), sha256_of(ref_path.read_bytes()),
            msg=f"P1: la referencia lleva el sha256 REAL de su contenido "
                f"(no se fabrica); got {entry!r}")
        self.assertEqual(
            entry.get("class"), "contract",
            msg=f"P3 (003-007, cambio de contrato declarado en "
                f"t1-green-decision.md): la referencia en forma string se "
                f"estampa `class: contract` (la envolvente refleja el "
                f"body); got {entry!r}")

        update2 = self.write_update(update_fixture(
            attempt=2,
            goal="Objetivo avanzado tras el primer checkpoint",
            references=["fixture/notes.md"]))
        env2 = self.write_envelope(
            self.run_write("checkpoint", update2), "checkpoint")

        self.assertEqual(
            env2.get("seq"), 2,
            msg=f"P1: la cadena usa un `seq` monotónico (D7, sin "
                f"`generation`); got {env2.get('seq')!r}")
        self.assertEqual(
            env2.get("prev_checkpoint_sha256"), first_sha,
            msg=f"P1: el segundo checkpoint encadena "
                f"`prev_checkpoint_sha256` = body_sha256 del head previo "
                f"({first_sha!r}); got "
                f"{env2.get('prev_checkpoint_sha256')!r}")
        self.assertNotEqual(
            env2.get("body_sha256"), first_sha,
            msg="P1: un cuerpo distinto produce un digest distinto "
                "(content-addressed)")


class TestP3BeginIdenticoNoop(ContinuityProjectCase):
    """P3 (faceta criterio 3) — `begin` idéntico al head es no-op rc 0."""

    def test_p03_begin_con_cuerpo_identico_al_head_es_noop(self) -> None:
        """P3/criterio 3 (faceta no-op idéntico): repetir `begin` con el
        MISMO update (mismo cuerpo canónico, misma clave
        `(execution_id, packet_id, attempt)`) → rc 0, `no_op: true`, y el
        store de continuity queda byte a byte SIN cambios (no se crea un
        checkpoint nuevo ni se duplica la cadena)."""
        update = self.write_update(update_fixture())
        env1 = self.write_envelope(self.run_write("begin", update), "begin")
        before = self.continuity_files()
        self.assertTrue(
            before, msg="P3 (precondición): el primer begin persistió el "
                        "head bajo continuity/**")

        proc2 = self.run_write("begin", update)
        env2 = self.write_envelope(proc2, "begin")

        self.assertEqual(
            env2.get("no_op"), True,
            msg=f"P3/criterio 3: un begin con cuerpo canónico idéntico al "
                f"head es no-op (`no_op: true`); got {env2.get('no_op')!r}")
        self.assertEqual(
            self.continuity_files(), before,
            msg="P3/criterio 3: el no-op NO escribe: el store de "
                "continuity queda byte a byte idéntico (sin checkpoint "
                "nuevo ni duplicado de cadena)")
        self.assertEqual(
            env2.get("seq"), env1.get("seq"),
            msg="P3/criterio 3: el no-op devuelve el checkpoint existente "
                "(misma seq), no uno nuevo")


class TestP7CapFallaCerrado(ContinuityProjectCase):
    """P7 / criterio 8 — exceder `--max-bytes` falla cerrado sin truncar."""

    def test_p07_exceso_max_bytes_falla_cerrado_y_no_persiste_truncado(
            self) -> None:
        """P7/criterio 8: una proyección que excede el cap declarado →
        rc≠0 con diagnóstico que cita el cap, y NO se persiste ningún
        checkpoint truncado (falla cerrado, nunca trunca). El default
        16 KiB también se aplica."""
        update_small_cap = self.write_update(update_fixture(
            goal="G" * 3000))
        before = self.continuity_files()

        proc = self.run_write("begin", update_small_cap, max_bytes=64)
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P7/criterio 8: exceder --max-bytes falla cerrado "
                f"(rc≠0); got rc={proc.returncode} stdout={out!r}")
        self.assertFalse(
            self.continuity_files(),
            msg="P7/criterio 8: sin truncar — NO se persiste ningún "
                "checkpoint truncado cuando la proyección excede el cap")
        self.assertIn(
            "max-bytes", out + err,
            msg=f"P7: el diagnóstico cita el cap (`max-bytes`); got "
                f"stdout={out!r} stderr={err!r}")

        # Default declarado: 16 KiB (P7). Un cuerpo de ~20 KiB excede el
        # default incluso sin --max-bytes explícito.
        update_over_default = self.write_update(update_fixture(
            goal="G" * (DEFAULT_MAX_BYTES + 4096)))
        proc_default = self.run_write("checkpoint", update_over_default)
        self.assertNotEqual(
            proc_default.returncode, 0,
            msg=f"P7: el default --max-bytes es 16 KiB — un cuerpo de "
                f"~20 KiB sin --max-bytes explícito también falla cerrado; "
                f"got rc={proc_default.returncode} "
                f"stdout={proc_default.stdout!r}")


if __name__ == "__main__":
    unittest.main()
