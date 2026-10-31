#!/usr/bin/env python3
"""RED de review-fix (etapa 4) — 005-007-progressive-planning: UN TEST POR
hallazgo BLOQUEANTE de la review formal
(docs/specs/005-007-progressive-planning/review.md; criterio vigente del
2026-10-12: se bloquea y corrige ya lo que compromete el resultado, la
evidencia o el uso previsto).

Contrato: docs/specs/005-007-progressive-planning/spec.md (sha256
54877103d622ca75994b503ee4be016bf39682c2c6a6f89962a8436d8d309a4a):

- **B1 → PD-1 (spec.md:42, AC-1 spec.md:96), ACOTADO al camino `planned`.**
  La revisión formal (review.md:23-35) halla que una tarea
  `detail: "planned"` sin la clave `depends_on` pasa HOY el validador
  (probe: `planned-absent-depends_on -> PASSED`, review.md:28-30) — la
  representación progresiva quedó sin la mitad que la diferencia (D2:
  cobertura global de dependencias, spec.md:109-110). La condición de
  cierre de la review exige a la tarea `planned` la clave `depends_on`
  presente (lista, `[]` válido = «sin dependencias») y acota expresamente
  el hallazgo: «No se requiere tocar el camino sin marcador (INV-5)»
  (review.md:33).
- **B2 → PD-9 (spec.md:66, AC-4 spec.md:99).** Una llamada `shell` que
  invoca REALMENTE la interfaz común de delegación ENVUELTA en un prefijo
  (`time python3 …`, `env …`, `nohup …`, `nice …`, `timeout 60 python3 …`)
  es un DESPACHO observado, con el método declarado. Hallazgo B2
  (review.md:37-44): hoy el medidor resuelve el programa del SEGMENTO y los
  envoltorios reportan `absent` — falso negativo en la clase de invocación
  que es la práctica real del repo (debt D-2 de la spec).

Comportamiento a través de los CLI del producto (sin leer implementación):

- B1: `prepare` sobre un proyecto temporal con plan draft declarado — los
  fixtures y helpers del oráculo T2
  (tests/test_005_007_t2_progressive_plan_validator.py), que están en el
  read scope declarado del packet. Negativo: rc≠0, `ERROR: ...`, stdout
  vacío, nada publicado, state y árbol sin cambios, diagnóstico que nombra
  la tarea y el campo.
- B2: el wrapper `scripts/cdad_context_meter.py` por SUBPROCESO con la
  bandera ya implementada por T5 (`--delegation-dispatch`) — fixtures
  sintéticos 100% (SQLite temporal, contenido inventado; la base real
  NUNCA se abre: INV-6), construidos con los builders del oráculo T5
  (tests/test_005_007_t5_delegation_dispatch.py).

DECLARACIÓN RED caso por caso (lo que falla HOY y por qué):

RETIRO POR CONTRADICCIÓN DE CONTRATO (probado con evidencia dura por el
implementer: reviewfix-green.md:22-58; confirmado y adjudicado por el
orquestador). Los casos del packet original sobre el camino `next`/sin
marcador NO se exigen en este oráculo: codifican PD-1 sobre ese camino y
contradicen PD-2/INV-5 — spec.md:44 («Un bloque sin el marcador se
comporta exactamente como hoy») y spec.md:84 («Sin el campo `detail`, el
bloque `plan-tasks` … idénticos a hoy») — y el oráculo congelado de T2
`TestPd2NextAndUnmarkedStillAccepted`
(tests/test_005_007_t2_progressive_plan_validator.py:402-417), que exige
ACEPTADO el mismo fixture byte-idéntico (`next_task("t1")` sin
`objective`, con y sin `detail`). Casos retirados, sin reemplazo
exigible:
  * `b-sin-objective` (variantes `detail-next` y `sin-marcador`):
    SIN `objective` en tareas `next`/sin marcador.
  * `c-sin-clave-depends_on` sobre tarea NO marcada (con `objective`,
    para que el único defecto fuera la clave ausente); su control
    positivo sin marcador (d, `depends_on: []` + `objective`) queda
    ya fijado por T2 (TestPd2NextAndUnmarkedStillAccepted y el control
    de este módulo, `prepare_valid_control`) y no se repite aquí.
Ningún oráculo debe REINTRODUCIR esos casos salvo que el dueño reconcilie
PD-1 con PD-2/INV-5 a favor de PD-1 para el camino sin marcador: la
review acota B1 al camino `planned` y lo dice expresamente: «No se
requiere tocar el camino sin marcador (INV-5)» (review.md:33; bloque
B1, review.md:23-35 — «Condición de cierre verificable»).

- B1 (a) tarea `planned` SIN la clave `depends_on` → HOY rc=0 (probe de
  la review: `planned-absent-depends_on -> PASSED`, review.md:28-30):
  AssertionError en el chequeo de rechazo («plan accepted despite a
  required postcondition»). ÚNICO caso ROJO de este oráculo.
- B1 (b) CONTROL — verde HOY por diseño: una tarea `planned` con
  `depends_on: []` y `objective` no vacío sigue ACEPTADA (no se inventa
  una dependencia donde no hay; la review acepta el `[]` explícito,
  review.md:33).
- B1 (c) tarea `planned` sin `objective` no vacío → rechazada (ya
  implementada en la etapa 3) y ya cubierta por el oráculo congelado de
  T2 (`TestPd1PlannedFieldNegativesAreRejected`, :315-329).
  REPETICIÓN DECLARADA: se conserva aquí para cerrar la superficie del
  AC-1 acotado al camino `planned`; no introduce una postcondición
  nueva (verde HOY).
- B2 (a) cada envoltura (`time`, `env`, `nohup bash -c`, `nice`,
  `timeout 60`) → HOY `first_dispatch: absent` con causa (falso negativo,
  review.md:39): AssertionError en el chequeo `status == "observed"`.
- B2 (b) CONTROL negativo — verde HOY: una llamada que sólo MENCIONA el
  programa (write/grep) o una de ayuda (`--help`/`-h`) sigue `absent` con
  la causa que nombra el límite (oráculo T5 casos 2 y 3, ya verdes).
- B2 (c) CONTROL — verde HOY: el registro NEUTRAL sin la bandera sigue
  byte-idéntico (oráculo T5 caso 4, ya verde).

Todos los fallos nuevos son AssertionError sobre la postcondición ausente
(failureException de unittest); ningún fallo por ImportError ni sintaxis:
el test NO importa los módulos del producto.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_004_003_t1_draft_contract import (
    DRAFT_PLAN_BYTES,
    DRAFT_PLAN_RELPATH,
    DRAFT_PLAN_VERSION,
)
from tests.test_packet_prepare import (
    PACKET_CLI,
    PrepareProject,
    run_prepare,
    tree_snapshot,
)
# Fixtures ya verdes de los oráculos de esta feature (read scope del packet):
# T2 aporta el harness del validador; T5 el harness del medidor.
from tests.test_005_007_t2_progressive_plan_validator import (
    plan_bytes,
    next_task,
    planned_task,
)
from tests.test_005_007_t5_delegation_dispatch import (
    CLI_TIMEOUT_S,
    DELEGATE_HELP_CMD,
    DELEGATE_HELP_SHORT_CMD,
    DELEGATION_FLAG,
    DELEGATION_PROGRAM,
    MENTION_GREP_CMD,
    MENTION_WRITE_CONTENT,
    METER_WRAPPER,
    NEUTRAL_RECORD_GOLDEN_SHA256,
    REPO_ROOT,
    STORE_ENV_VAR,
    _build_trace_store,
    _canonical_record,
)


# =====================================================================
# B1 — validador (PD-1): objective no vacío y la clave depends_on SIEMPRE
# (patrón y helpers del oráculo T2, reusados verbatim)
# =====================================================================


class _B1ValidatorCase(unittest.TestCase):
    """Helpers del oráculo T2 (misma superficie `prepare`, mismos flags)."""

    def project(self) -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-005-007-reviewfix-b1-")
        self.addCleanup(temp.cleanup)
        project = PrepareProject(Path(temp.name).resolve(), "reviewer", "plan-review")
        # 010-004 T2 POST-AUDIT (PC-04/§4.1): contexto canónico materializado
        # en la construcción (ver ObjectFormCase.project para la convención).
        _ = project.execution_path
        return project

    @staticmethod
    def draft_flags() -> tuple[str, ...]:
        return (
            "--contract-kind",
            "draft-plan",
            "--contract-path",
            DRAFT_PLAN_RELPATH,
            "--plan-version",
            DRAFT_PLAN_VERSION,
        )

    def write_plan(self, project: PrepareProject, tasks: list[dict]) -> None:
        draft = project.root / DRAFT_PLAN_RELPATH
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_bytes(plan_bytes(tasks))

    def assert_accepted_and_published(self, project: PrepareProject) -> None:
        result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "la superficie honesta fue rechazada (control roto): "
            + result.stderr.decode(errors="replace"),
        )
        packet_dir = project.out_dir / project.packet_id()
        self.assertTrue(
            (packet_dir / "PACKET.md").is_file(),
            "el plan aceptado no publicó su paquete",
        )

    def assert_rejected_without_publication(
        self, project: PrepareProject, tokens: tuple[str, ...]
    ) -> None:
        before = tree_snapshot(project.root)
        state_before = project.state_path.read_bytes()
        result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))

        stderr = result.stderr.decode(errors="replace")
        self.assertNotEqual(
            result.returncode,
            0,
            f"plan aceptado pese a la postcondición PD-1 exigida "
            f"(hallazgo B1): {stderr!r}",
        )
        self.assertRegex(stderr, r"(?m)^ERROR: ", f"stderr sin 'ERROR: ...': {stderr!r}")
        for token in tokens:
            self.assertIn(
                token,
                stderr,
                f"el diagnóstico no nombra el token ofensor {token!r}: {stderr!r}",
            )
        self.assertEqual(result.stdout, b"", "stdout debe quedar vacío")
        self.assertEqual(list(project.out_dir.iterdir()), [], "out-dir ganó entradas")
        self.assertEqual(project.state_path.read_bytes(), state_before, "state cambió")
        self.assertEqual(tree_snapshot(project.root), before, "el árbol cambió")

    def prepare_valid_control(self) -> None:
        """Control honesto primero (patrón congelado de 004-003/T2): la
        superficie sin marcador y con plan de validación completo es verde,
        de modo que un rechazo sólo puede venir del defecto específico."""
        control = self.project()
        self.write_plan(control, [next_task("t1")])
        self.assert_accepted_and_published(control)


class TestB1TaskAlwaysDeclaresObjectiveAndDependsOn(_B1ValidatorCase):
    """B1 (PD-1/AC-1), ACOTADO al camino `planned` (review.md:23-35):
    la tarea `planned` SIN la clave `depends_on` es rechazada con un
    diagnóstico que nombra la tarea y el campo; el control
    `depends_on: []` + `objective` no vacío sigue aceptado. Los casos
    `next`/sin marcador del packet original fueron RETIRADOS por
    contradicción de contrato con PD-2/INV-5 y el oráculo congelado de
    T2 (ver RETIRO en el docstring del módulo)."""

    def test_b1_pd1_planned_task_always_declares_depends_on(self) -> None:
        """B1 → PD-1 acotado: (a) tarea `planned` SIN la clave
        `depends_on` → rechazo rc≠0 (ROJO HOY); (b) CONTROL `planned` con
        `depends_on: []` + `objective` no vacío → aceptada (verde HOY);
        (c) REPETICIÓN DECLARADA (ya cubierta por el oráculo congelado de
        T2, TestPd1PlannedFieldNegativesAreRejected :315-329): la tarea
        `planned` sin `objective` → rechazo (verde HOY)."""
        self.prepare_valid_control()

        # (a) una tarea `planned` SIN la clave `depends_on` → rc≠0 con
        #     diagnóstico que nombre la tarea y el campo. HOY: rc=0.
        with self.subTest(caso="a-planned-sin-clave-depends_on"):
            project = self.project()
            self.write_plan(project, [planned_task("t1", depends_on=None)])
            self.assert_rejected_without_publication(project, ("t1", "depends_on"))

        # (b) CONTROL (planned): una tarea `planned` con `depends_on: []`
        #     y `objective` no vacío sigue ACEPTADA — no se inventa una
        #     dependencia donde no hay; el `[]` explícito vale
        #     (review.md:33). Verde HOY por diseño (declara el
        #     comportamiento que la corrección no puede cambiar).
        with self.subTest(caso="b-control-planned-depends_on-vacio-aceptada"):
            project = self.project()
            self.write_plan(project, [planned_task("t1")])
            self.assert_accepted_and_published(project)

        # (c) REPETICIÓN DECLARADA: la tarea `planned` sin `objective` no
        #     vacío ya es rechazada por el oráculo congelado de T2
        #     (`TestPd1PlannedFieldNegativesAreRejected`, :315-329). Se
        #     conserva aquí para cerrar la superficie del AC-1 acotado al
        #     camino `planned`; no introduce una postcondición nueva.
        with self.subTest(caso="c-planned-sin-objective-repeticion-declarada-de-t2"):
            project = self.project()
            self.write_plan(project, [planned_task("t1", objective=None)])
            self.assert_rejected_without_publication(project, ("t1", "objective"))


# =====================================================================
# B2 — medidor (PD-9): la invocación real envuelta en un prefijo es un
# despacho observado (patrón y builders del oráculo T5, reusados)
# =====================================================================

# Argumentos de delegación de la invocación fixture (los declarados por
# PD-9/--project-root/--packet/--destination, el patrón ya verde de T5).
DELEGATE_ARGS = (
    "--project-root . --packet fixture-packet-reviewfix-b2-001 "
    "--destination cdad_delegate_fixture.py"
)
DELEGATION_SKILLS_PATH = f"skills/cdad-cycle/scripts/{DELEGATION_PROGRAM}"

# La clase del hallazgo B2 (debt D-2 de la spec): envoltorios reales del
# repo. `nohup` replica la práctica registrada (`nohup bash -c "python3 …"`).
WRAPPED_COMMANDS: dict[str, str] = {
    "time": f"time python3 {DELEGATION_SKILLS_PATH} {DELEGATE_ARGS}",
    "env": f"env CDAD_FIXTURE_MODE=b2 python3 {DELEGATION_SKILLS_PATH} {DELEGATE_ARGS}",
    "nohup": f'nohup bash -c "python3 {DELEGATION_SKILLS_PATH} {DELEGATE_ARGS}"',
    "nice": f"nice -n 5 python3 {DELEGATION_SKILLS_PATH} {DELEGATE_ARGS}",
    "timeout": f"timeout 60 python3 {DELEGATION_SKILLS_PATH} {DELEGATE_ARGS}",
}

# Posición esperada, derivada del PROPIO fixture: read, shell(envoltura), read
# → la shell envuelta es la llamada #2 (seq 3, 1.0 min; patrón de T5).
POS_WRAPPED_SHELL = (2, 3, 1.0)


class _B2MeterCase(unittest.TestCase):
    """Helpers del oráculo T5 (corrida por subproceso, fixtures SQLite)."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="cdad-005-007-reviewfix-b2-")
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.stores: dict[str, Path] = {}

        def build(name: str, sid: str, calls: list[tuple[str, dict]]) -> Path:
            store = base / name / "sessions.db"
            _build_trace_store(store, sid=sid, calls=calls)
            self.stores[name] = store
            return store

        # Caso (a): una traza por envoltorio — la shell envuelta es el
        # PRIMER despacho (llamada #2).
        for name, command in WRAPPED_COMMANDS.items():
            build(name, f"sess-fixture-reviewfix-b2-{name}", [
                ("read", {"path": "/fixture/dir/f1.md"}),
                ("shell", {"command": command}),
                ("read", {"path": "/fixture/dir/f3.md"}),
            ])
        # Caso (b) CONTROL negativo: mención pura y ayuda (trazas de T5).
        # Sids y llamadas IDÉNTICOS a los del oráculo T5: el registro
        # canónico porta el sid (verificado black-box), y el golden sha del
        # control (c) fue capturado con los sids de T5.
        build("mention", "sess-fixture-t5-mention", [
            ("read", {"path": "/fixture/dir/f1.md"}),
            ("write", {"path": "/fixture/dir/instrucciones.md",
                       "content": MENTION_WRITE_CONTENT}),
            ("shell", {"command": MENTION_GREP_CMD}),
            ("read", {"path": "/fixture/dir/f3.md"}),
        ])
        build("help", "sess-fixture-t5-help", [
            ("read", {"path": "/fixture/dir/f1.md"}),
            ("shell", {"command": DELEGATE_HELP_CMD}),
            ("shell", {"command": DELEGATE_HELP_SHORT_CMD}),
            ("read", {"path": "/fixture/dir/f3.md"}),
        ])
        # Caso (c) CONTROL: traza neutral para la byte-identidad (T5 caso 4).
        build("neutral", "sess-fixture-t5-neutral", [
            ("read", {"path": "/fixture/dir/f1.md"}),
            ("glob", {"pattern": "fixture-*"}),
            ("shell", {"command": "echo fixture-step"}),
            ("read", {"path": "/fixture/dir/f3.md"}),
        ])

    # -- corrida del wrapper (patrón T5: SIEMPRE subproceso, nunca import) --

    def run_meter(self, *argv: str) -> subprocess.CompletedProcess:
        cmd = [sys.executable, str(METER_WRAPPER), *argv]
        env = os.environ.copy()
        env.pop(STORE_ENV_VAR, None)  # sin fuga del entorno del host
        return subprocess.run(
            cmd, cwd=REPO_ROOT, env=env, capture_output=True,
            timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL)

    def run_with_flag(self, store: Path, label: str) -> dict:
        proc = self.run_meter("--store", str(store), DELEGATION_FLAG)
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="replace")
            self.fail(
                f"{label}: precondición rota — la corrida con "
                f"`{DELEGATION_FLAG}` (ya implementada por T5) debe salir "
                f"rc=0; rc={proc.returncode} stderr={err[:300]!r}")
        return self.parse_session(proc, label)

    def parse_session(self, proc: subprocess.CompletedProcess, label: str) -> dict:
        out = proc.stdout.decode("utf-8", errors="replace")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:
            self.fail(f"{label}: stdout no es JSON parseable ({exc}): "
                      f"{out[:400]!r}")
        self.assertEqual(
            doc.get("run", {}).get("schema"), "recognized",
            msg=f"{label}: el fixture replica el esquema observado y debe "
                f"reconocerse; run={doc.get('run')}")
        sessions = doc.get("sessions")
        self.assertIsInstance(sessions, list, msg=f"{label}: sessions[]")
        self.assertEqual(len(sessions), 1, msg=f"{label}: UNA sesión")
        return doc

    def milestone(self, session: dict, key: str, ctx: str) -> dict:
        milestones = session.get("milestones")
        self.assertIsInstance(milestones, dict, msg=f"{ctx}: milestones objeto")
        self.assertIn(key, milestones, msg=f"{ctx}: milestones trae {key!r}")
        return milestones[key]


class TestB2WrappedInvocationIsObservedDispatch(_B2MeterCase):
    """B2 (PD-9/AC-4): la invocación REAL de la interfaz común de delegación
    envuelta en un prefijo es un despacho observado, con el método
    declarado; la mención y la ayuda siguen sin serlo; el registro neutral
    sin la bandera sigue byte-idéntico."""

    def test_b2_pd9_wrapped_invocation_reports_observed_dispatch(self) -> None:
        """B2 → PD-9: caso (a) las cinco envolturas (falla HOY: absent con
        causa — falso negativo); (b) CONTROL negativo y (c) CONTROL de
        byte-identidad (verdes HOY, declara el comportamiento que la
        corrección no puede romper)."""
        # (a) cada envoltura reporta `first_dispatch` OBSERVADO en la
        #     posición de la shell envuelta, con el MÉTODO declarado para la
        #     entrada de la interfaz de delegación. HOY: `absent` con causa.
        with self.subTest(caso="a-envolturas-despacho-observado"):
            for name in WRAPPED_COMMANDS:
                with self.subTest(envoltura=name):
                    doc = self.run_with_flag(self.stores[name], f"B2 (a) {name}")
                    session = doc["sessions"][0]
                    fd = self.milestone(session, "first_dispatch",
                                        f"B2 (a) {name}")
                    self.assertEqual(
                        fd.get("status"), "observed",
                        msg=f"B2 (a) [{name}]: la shell que invoca REALMENTE "
                            f"`{DELEGATION_PROGRAM}` bajo el prefijo `{name}` "
                            "es un despacho OBSERVADO (PD-9); hoy el medidor "
                            "resuelve el programa del segmento y reporta "
                            f"absent con causa — falso negativo (fue "
                            f"{fd.get('status')!r}; causa="
                            f"{fd.get('cause')!r})")
                    position = fd.get("position")
                    self.assertEqual(
                        (position or {}).get("call_index"), POS_WRAPPED_SHELL[0],
                        msg=f"B2 (a) [{name}]: la posición del despacho es la "
                            f"llamada #{POS_WRAPPED_SHELL[0]} (la shell "
                            f"envuelta; fue {position!r})")
                    method = fd.get("method")
                    self.assertIsInstance(
                        method, str,
                        msg=f"B2 (a) [{name}]: el hito observado declara su "
                            f"MÉTODO (fue {method!r})")
                    self.assertTrue(
                        method.strip(),
                        msg=f"B2 (a) [{name}]: el método declarado no es vacío")
                    recognition = doc.get("reader", {}).get(
                        "dispatch_recognition")
                    self.assertIsInstance(
                        recognition, dict,
                        msg=f"B2 (a) [{name}]: el registro declara el conjunto "
                            "reconocido (superficie ya fijada por T5)")
                    delegate_name = next(
                        n for n in recognition
                        if DELEGATION_PROGRAM in str(n))
                    self.assertEqual(
                        method, recognition[delegate_name]["method"],
                        msg=f"B2 (a) [{name}]: el método del hito es el "
                            "declarado para la entrada de la interfaz de "
                            f"delegación ({delegate_name!r}; fue "
                            f"{method!r})")
        # (b) CONTROL negativo: una llamada que sólo MENCIONA el programa, o
        #     una de ayuda (`--help`/`-h`), sigue SIN ser despacho (verde
        #     HOY: oráculo T5 casos 2 y 3).
        with self.subTest(caso="b-control-mencion-y-ayuda-siguen-absent"):
            for name, token in (("mention", "mention"), ("help", "help")):
                with self.subTest(control=name):
                    doc = self.run_with_flag(self.stores[name],
                                             f"B2 (b) {name}")
                    fd = self.milestone(doc["sessions"][0], "first_dispatch",
                                        f"B2 (b) {name}")
                    self.assertEqual(
                        fd.get("status"), "absent",
                        msg=f"B2 (b) [{name}]: sin invocación real NO hay "
                            f"despacho (fue {fd.get('status')!r})")
                    cause = str(fd.get("cause") or "").lower()
                    self.assertIn(
                        token, cause,
                        msg=f"B2 (b) [{name}]: la causa nombra el límite "
                            f"({token!r}; fue {fd.get('cause')!r})")
        # (c) CONTROL: el registro NEUTRAL sin la bandera sigue
        #     byte-idéntico (verde HOY: oráculo T5 caso 4).
        with self.subTest(caso="c-control-neutral-byte-identico"):
            proc = self.run_meter("--store", str(self.stores["neutral"]))
            self.assertEqual(
                proc.returncode, 0,
                msg="B2 (c): la corrida default sobre el fixture neutral "
                    f"sale rc=0; stderr={proc.stderr[:300]!r}")
            doc = self.parse_session(proc, "B2 (c)")
            digest = hashlib.sha256(
                _canonical_record(doc).encode("utf-8")).hexdigest()
            self.assertEqual(
                digest, NEUTRAL_RECORD_GOLDEN_SHA256,
                msg="B2 (c): el registro neutral SIN la bandera es "
                    "byte-idéntico (sha256 del registro canónico con "
                    f"run.store_ref normalizado; calculado {digest})")


if __name__ == "__main__":
    unittest.main(verbosity=2)
