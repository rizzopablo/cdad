#!/usr/bin/env python3
"""005-003 T6 RED — contrato aplicable del encargo (PD-10; INV-4, INV-5).

Contract:
- docs/specs/005-003-orientation-reduction/spec.md §2.8 (contrato aplicable del
  encargo, D11b), §3 PD-10, §4 INV-4/INV-5.
- docs/specs/005-003-orientation-reduction/plan.md §3 (ficha T6) y §4 (bloque
  canónico `plan-tasks`, tarea T6).

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI del
repo; el módulo NUNCA se importa y la implementación NUNCA se lee):

    python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root <ABS> \\
        --role <rol> --substage <subfase> --objective <encargo> \\
        [--plan-task <TASK_ID>]

Los fixtures son autocontenidos (proyecto temporal con su state, su política,
su contrato y un plan aprobado con su bloque canónico `plan-tasks`; HOME del
subproceso SIEMPRE en un tempdir vacío). Nunca se toca el repo real, ni el
state real, ni rutas de este host. El bloque canónico lo parsea el PROPIO test
(mismo formato declarado: bloque cercado `plan-tasks` con `tasks` y
`validation_strategy`) y compara contra lo EMITIDO por el paquete: la sección de
validación no puede satisfacerse con texto escrito a mano.

INTERFAZ DECLARADA POR ESTE TEST (la satisface el implementer leyendo el test;
la fija este paquete porque el test-writer no ve el código y la spec §2.8 deja
libre la mecánica dentro del contrato fijado — §11, nota final):

1. `prepare --plan-task <TASK_ID>` (opción aditiva). Con ella el REQUEST.json
   lleva el campo opcional `plan_task == <TASK_ID>` y el PACKET.md emite DOS
   secciones declaradas: `## Task validation plan` y `## Applicable contract`.
   SIN la opción no hay campo ni secciones y el paquete es ADITIVO: no depende
   del plan (idéntico al de un proyecto cuyo plan no declara bloque).
2. `## Task validation plan`: los valores `focal_tests` / `observable_checks` /
   `regressions` / `integration_gate` de la tarea declarada, tomados del bloque
   canónico `plan-tasks` del plan aprobado, con el literal
   `@validation_strategy` RESUELTO contra el `validation_strategy` a nivel de
   plan; dice CUÁNDO ampliar la validación; declara la procedencia del plan
   (path + sha256). Una tarea ausente del bloque falla cerrado nombrando el id.
3. `## Applicable contract`: la referencia del contrato (path + sha256, igual
   que la del paquete) y los ids `PD-n`/`INV-n`/`D-n` aplicables que el encargo
   declara. El test NO afirma que el paquete derive la aplicabilidad
   automáticamente (límite honesto de §2.8-b): afirma que cada id EMITIDO
   resuelve a un encabezado del contrato (pertenencia de conjunto, mecánica).
   La fuente declarada de los ids en el fixture es la ficha de la tarea en el
   plan (formato del plan aprobado: `- **Resultado observable / PD cubiertas:**`).
4. La instrucción del paquete (bloque `<!-- cdad-instructions -->`, compuesto
   por `packets/common.md` + `packets/roles/<rol>.md` +
   `packets/substages/<rol>-<subfase>.md`, declarados en `instruction_sources`
   con sus hashes) declara que la SUITE COMPLETA NO se corre salvo que el
   paquete lo pida y que la corre quien cierra; ningún asset de
   `packets/roles/**` ni `packets/substages/**` afirma lo contrario (hoy
   `packets/roles/implementer.md` y `packets/substages/implementer-green.md`
   dicen «the complete suite is the closure gate» y se corrigen).
5. El cierre incluye el commit: `## Evidence required` exige `commit` y la
   instrucción lo declara como parte de la entrega.

RED hoy: `--plan-task` es una opción DESCONOCIDA (argparse rc=2), las secciones
`## Task validation plan` / `## Applicable contract` no existen, la política de
la suite completa no está declarada y los dos assets citados la contradicen.
Cada test falla por `AssertionError` de CONTRATO (rc / sección / valor /
diagnóstico), nunca por ImportError, sintaxis, JSONDecodeError ni error de E/S
no capturado.

Mapeo test → postcondición/borde:
  test_pd10_task_declared_and_additive_without_option
      -> PD-10(i) (tarea declarada explícita: `--plan-task` + `plan_task`; las
         dos secciones declaradas) + INV-4 (sin la opción el paquete es
         aditivo: no depende del plan; sin sección ni fallo)
  test_pd10_validation_plan_matches_canonical_block
      -> PD-10(ii) (valores iguales al bloque canónico, `@validation_strategy`
         resuelto, cuándo ampliar, procedencia path+sha256 del plan)
  test_pd10_absent_task_fails_closed_naming_id
      -> PD-10(ii) borde (tarea ausente del bloque → fallo cerrado nombrando el
         id, sin publicación)
  test_pd10_applicable_contract_references_resolve_to_headings
      -> PD-10(iii) (referencia del contrato coincide con la del paquete; cada
         id emitido resuelve a un encabezado del contrato)
  test_pd10_instruction_declares_full_suite_policy
      -> PD-10(iv) (la parte común declara la política de la suite completa; la
         corre quien cierra; ningún asset de rol/subetapa la contradice)
  test_pd10_closure_includes_commit
      -> PD-10(v) (el cierre exige el commit y la instrucción lo declara)
  test_inv4_plan_task_is_declared_optional_and_closure_not_relaxed
      -> INV-4 (el campo opcional declarado valida; una clave desconocida sigue
         rechazándose: no se relaja el cierre)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import (
    CONTRACT_FILE,
    FEATURE_ID,
    build_project,
    prepare_args,
    read_state,
    tree_snapshot,
    write_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
# Superficie declarada por la spec §2.8 / plan §3 (ficha T6): el CLI del skill.
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
PACKETS_ROOT = REPO_ROOT / "skills" / "cdad-cycle" / "packets"
PLAN_REL = f"docs/specs/{FEATURE_ID}/plan.md"
CLI_TIMEOUT_S = 60

PACKET_BEGIN = "---cdad-packet-json\n"
PACKET_END = "\n---end-cdad-packet-json\n"

# ---------------------------------------------------------------- contrato fixture

# El contrato del fixture declara los ids como encabezados: la resolución de un
# id emitido es mecánica (id -> encabezado del contrato).
SPEC_BYTES = (
    "# Spec fixture — contrato aplicable del encargo (005-003 T6)\n\n"
    "## 3. Postcondiciones\n\n"
    "### PD-10 — contrato aplicable del encargo\n\n"
    "### PD-1 — vista compacta del estado operativo\n\n"
    "## 4. Invariantes\n\n"
    "### INV-4 — frontera con 005-007\n\n"
    "### INV-5 — no se reescriben los contratos de 005-002\n\n"
    "## 10. Decisiones\n\n"
    "### D1 — vista compacta como proyección\n"
).encode("utf-8")

VALIDATION_STRATEGY = (
    "Estrategia fixture: focal por unidad (segundos); la suite completa se corre "
    "una sola vez al cierre y la corre quien cierra; se reutiliza evidencia "
    "equivalente con procedencia verificada."
)

T1_FOCAL = "tests/test_fixture_t1.py"
T1_CHECK = "la seccion de validacion de la tarea coincide con el bloque canonico del plan"
T1_REGRESSION = "tests/test_fixture_regression.py"
T2_FOCAL = "tests/test_fixture_t2.py"
T2_CHECK = "segunda tarea: comprobacion observable distinta"


def _task(
    task_id: str,
    *,
    files: list[str],
    focal: list[str],
    checks: list[str],
    regressions: list[str],
) -> dict:
    return {
        "id": task_id,
        "produce": [{"artifact": f"fixture-{task_id.lower()}", "contract": "fixture-v1"}],
        "consume": [],
        "depends_on": [],
        "parallel": [],
        "files": files,
        "focal_tests": focal,
        "observable_checks": checks,
        "regressions": regressions,
        "integration_gate": "@validation_strategy",
        "owner": "RED: test-writer; GREEN: implementer",
    }


TASKS = [
    _task(
        "T1",
        files=["tests/test_fixture_t1.py"],
        focal=[T1_FOCAL],
        checks=[T1_CHECK],
        regressions=[T1_REGRESSION],
    ),
    _task(
        "T2",
        files=["tests/test_fixture_t2.py"],
        focal=[T2_FOCAL],
        checks=[T2_CHECK],
        regressions=[],
    ),
]

PLAN_TASKS_FENCE_OPEN = "```plan-tasks\n"
PLAN_TASKS_FENCE_CLOSE = "```"


def _plan_bytes(
    tasks: list[dict] | None,
    *,
    strategy: str = VALIDATION_STRATEGY,
    ficha_ids: str = "PD-10, INV-4, D1",
) -> bytes:
    """Plan aprobado del fixture: ficha de la tarea (fuente humana de los ids
    aplicables) + bloque canónico `plan-tasks` (fuente de los comandos de
    validación). `tasks=None` produce un plan SIN bloque (fixture aditivo)."""
    head = (
        "# Plan fixture — contrato aplicable del encargo (005-003 T6)\n\n"
        "## 3. Fichas mínimas de tarea\n\n"
        "### T1 — Fixture task one\n\n"
        f"- **Resultado observable / PD cubiertas:** {ficha_ids}\n"
        "- **Alcance incluido:** fixture.\n\n"
        "### T2 — Fixture task two\n\n"
        "- **Resultado observable / PD cubiertas:** PD-1\n\n"
        "## 4. Bloque canónico plan-tasks\n\n"
    )
    if tasks is None:
        return (head + "(fixture aditivo: sin bloque canónico)\n").encode("utf-8")
    block = json.dumps(
        {"validation_strategy": strategy, "tasks": tasks},
        indent=1,
        sort_keys=True,
    )
    return (head + PLAN_TASKS_FENCE_OPEN + block + "\n" + PLAN_TASKS_FENCE_CLOSE + "\n").encode(
        "utf-8"
    )


def _canonical_block(plan_bytes: bytes) -> dict:
    """El MISMO lector declarado del bloque canónico: un único bloque cercado
    `plan-tasks` con JSON (`tasks` + `validation_strategy`)."""
    text = plan_bytes.decode("utf-8")
    assert text.count(PLAN_TASKS_FENCE_OPEN) == 1, (
        "fixture: el plan debe declarar exactamente un bloque plan-tasks"
    )
    inner = text.split(PLAN_TASKS_FENCE_OPEN, 1)[1].split(
        "\n" + PLAN_TASKS_FENCE_CLOSE, 1
    )[0]
    return json.loads(inner)


def _canonical_task(plan_bytes: bytes, task_id: str) -> dict:
    block = _canonical_block(plan_bytes)
    for entry in block.get("tasks", []):
        if entry.get("id") == task_id:
            return entry
    raise AssertionError(
        f"fixture: la tarea {task_id!r} no está en el bloque canónico"
    )


# ---------------------------------------------------------------- proyecto fixture


def _build(
    root: Path,
    *,
    plan_tasks: list[dict] | None = TASKS,
    strategy: str = VALIDATION_STRATEGY,
) -> Path:
    """Proyecto sintético válido (política + state I2 + contrato con encabezados
    de ids + plan aprobado con su bloque canónico)."""
    build_project(root)
    (root / CONTRACT_FILE).write_bytes(SPEC_BYTES)
    state = read_state(root)
    for entry in state.get("stage_history", []):
        if entry.get("stage") == "specification":
            entry["contract_path"] = CONTRACT_FILE
            entry["contract_sha256"] = hashlib.sha256(SPEC_BYTES).hexdigest()
    write_state(root, state)
    plan = root / PLAN_REL
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_bytes(_plan_bytes(plan_tasks, strategy=strategy))
    return root


class _Fixture:
    """Proyecto autocontenido en un tempdir, con HOME del subproceso aislado."""

    def __init__(
        self,
        base: Path,
        *,
        plan_tasks: list[dict] | None = TASKS,
        strategy: str = VALIDATION_STRATEGY,
    ) -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        _build(self.root, plan_tasks=plan_tasks, strategy=strategy)
        self.env = dict(os.environ)
        self.env["HOME"] = str(self.home)  # NUNCA el HOME real

    def run(self, *args: str) -> subprocess.CompletedProcess:
        assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env=self.env,
            stdin=subprocess.DEVNULL,
            timeout=CLI_TIMEOUT_S,
        )

    def prepare(
        self,
        *extra: str,
        role: str = "test-writer",
        substage: str = "red",
        objective: str = "005-003 T6 fixture",
    ) -> subprocess.CompletedProcess:
        return self.run(
            *prepare_args(
                self.root,
                role=role,
                substage=substage,
                objective=objective,
                extra=tuple(extra),
            )
        )

    def packet_dirs(self) -> list[Path]:
        base = self.root / ".cdad" / "packets"
        if not base.is_dir():
            return []
        return sorted(d for d in base.iterdir() if d.is_dir())

    def packet_dir(self) -> Path:
        dirs = self.packet_dirs()
        assert len(dirs) == 1, (
            f"fixture: se esperaba exactamente un paquete publicado, hay "
            f"{[d.name for d in dirs]}"
        )
        return dirs[0]

    def request(self) -> dict:
        path = self.packet_dir() / "REQUEST.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AssertionError(
                f"PD-10 violada: el paquete no publicó un REQUEST.json válido: {exc}"
            ) from exc

    def packet_text(self) -> str:
        path = self.packet_dir() / "PACKET.md"
        assert path.is_file(), f"fixture: no existe {path}"
        return path.read_text(encoding="utf-8")

    def execution_context(self) -> Path:
        base = self.root / ".cdad" / "executions"
        docs = sorted(base.glob("*/execution.json")) if base.is_dir() else []
        assert docs, "fixture: no hay contexto de ejecución v2 publicado"
        return docs[0]

    def validate_request(self, request_path: Path) -> subprocess.CompletedProcess:
        return self.run(
            "validate-request",
            "--project-root",
            str(self.root),
            "--execution-context",
            str(self.execution_context()),
            "--request",
            str(request_path),
        )


@pytest.fixture
def fx(tmp_path: Path) -> _Fixture:
    return _Fixture(tmp_path)


# ---------------------------------------------------------------- parseo del paquete


def _parse_packet(text: str) -> tuple[dict, str]:
    assert text.startswith(PACKET_BEGIN), (
        "el paquete no comienza con el delimitador canónico ---cdad-packet-json"
    )
    assert PACKET_END in text, "el paquete no cierra el delimitador canónico"
    meta_text, body = text[len(PACKET_BEGIN):].split(PACKET_END, 1)
    try:
        metadata = json.loads(meta_text)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"el bloque de metadatos del paquete no es JSON válido: {meta_text[:200]!r}"
        ) from exc
    return metadata, body


def _section(body: str, title: str) -> str | None:
    """El texto de la sección `## <title>` del cuerpo del paquete, o None."""
    marker = f"\n## {title}\n"
    idx = body.find(marker)
    if idx < 0:
        return None
    start = idx + len(marker)
    nxt = body.find("\n## ", start)
    return body[start : nxt if nxt >= 0 else len(body)]


def _require_ok(proc: subprocess.CompletedProcess, context: str) -> None:
    out = proc.stdout + proc.stderr
    assert "unrecognized" not in out, (
        f"PD-10 violada: la opción declarada `--plan-task` debe reconocerse; "
        f"{context}: {out.strip()!r}"
    )
    assert proc.returncode == 0, (
        f"PD-10 violada: {context} debe tener éxito (rc=0); hoy rc={proc.returncode}: "
        f"{out.strip()!r}"
    )


# ---------------------------------------------------------------- PD-10 (i) / INV-4


def test_pd10_task_declared_and_additive_without_option(tmp_path: Path) -> None:
    """PD-10(i): `--plan-task T1` declara la tarea (campo opcional `plan_task`)
    y emite las dos secciones declaradas. INV-4/PD-10 borde: SIN la opción no
    hay campo ni secciones y el paquete es ADITIVO (byte-idéntico al de un
    proyecto cuyo plan no declara bloque)."""
    # Borde aditivo (primero: es el camino que HOY ya debe funcionar): dos
    # proyectos que difieren SOLO en si el plan declara el bloque canónico; sin
    # la opción el paquete no puede depender del plan.
    with_plan = _Fixture(tmp_path / "with-plan")
    no_plan = _Fixture(tmp_path / "no-plan", plan_tasks=None)
    proc_with = with_plan.prepare()
    proc_without = no_plan.prepare()
    assert proc_with.returncode == 0, proc_with.stderr
    assert proc_without.returncode == 0, proc_without.stderr

    req_with = (with_plan.packet_dir() / "REQUEST.json").read_bytes()
    req_without = (no_plan.packet_dir() / "REQUEST.json").read_bytes()
    assert b"plan_task" not in req_with, (
        "PD-10(i)/INV-4 violada: sin `--plan-task` el REQUEST.json emite igual "
        "el campo `plan_task`"
    )
    assert req_with == req_without, (
        "INV-4 violada: sin `--plan-task` el REQUEST.json no es aditivo (depende "
        "del bloque canónico del plan)"
    )
    pkt_with = (with_plan.packet_dir() / "PACKET.md").read_bytes()
    pkt_without = (no_plan.packet_dir() / "PACKET.md").read_bytes()
    assert pkt_with == pkt_without, (
        "INV-4 violada: sin `--plan-task` el PACKET.md no es aditivo (depende del "
        "bloque canónico del plan)"
    )
    _, body_plain = _parse_packet(pkt_with.decode("utf-8"))
    assert _section(body_plain, "Task validation plan") is None, (
        "PD-10 borde violado: sin `plan_task` no debe emitirse `## Task "
        "validation plan`"
    )
    assert _section(body_plain, "Applicable contract") is None, (
        "PD-10 borde violado: sin `plan_task` no debe emitirse `## Applicable "
        "contract`"
    )

    # Con la tarea declarada: campo opcional + las dos secciones declaradas.
    declared = _Fixture(tmp_path / "declared")
    proc = declared.prepare("--plan-task", "T1")
    _require_ok(proc, "prepare --plan-task T1")
    request = declared.request()
    assert request.get("plan_task") == "T1", (
        f"PD-10(i) violada: el REQUEST.json no lleva el campo opcional "
        f"`plan_task` de la tarea declarada: {request.get('plan_task')!r}"
    )
    _, body_declared = _parse_packet(declared.packet_text())
    assert _section(body_declared, "Task validation plan") is not None, (
        "PD-10(ii) violada: el paquete con tarea declarada no emite la sección "
        "declarada `## Task validation plan`"
    )
    assert _section(body_declared, "Applicable contract") is not None, (
        "PD-10(iii) violada: el paquete con tarea declarada no emite la sección "
        "declarada `## Applicable contract`"
    )


# ---------------------------------------------------------------- PD-10 (ii)


def test_pd10_validation_plan_matches_canonical_block(tmp_path: Path) -> None:
    """PD-10(ii): la sección `## Task validation plan` de la tarea declarada
    lleva los valores de `focal_tests` / `observable_checks` / `regressions` /
    `integration_gate` IGUALES a los del bloque canónico `plan-tasks` del plan
    aprobado (con `@validation_strategy` resuelto contra el
    `validation_strategy` de plan), dice cuándo ampliar la validación y declara
    la procedencia del plan (path + sha256)."""
    fx = _Fixture(tmp_path)
    proc = fx.prepare("--plan-task", "T1")
    _require_ok(proc, "prepare --plan-task T1")
    packet = fx.packet_text()
    _, body = _parse_packet(packet)
    section = _section(body, "Task validation plan")
    assert section is not None, (
        "PD-10(ii) violada: falta la sección declarada `## Task validation plan`"
    )

    plan_bytes = (fx.root / PLAN_REL).read_bytes()
    canonical = _canonical_task(plan_bytes, "T1")

    for value in canonical["focal_tests"]:
        assert value in section, (
            f"PD-10(ii) violada: `focal_tests` emitido no coincide con el bloque "
            f"canónico (falta {value!r}); no puede satisfacerse con texto a mano"
        )
    for value in canonical["observable_checks"]:
        assert value in section, (
            f"PD-10(ii) violada: `observable_checks` emitido no coincide con el "
            f"bloque canónico (falta {value!r})"
        )
    for value in canonical["regressions"]:
        assert value in section, (
            f"PD-10(ii) violada: `regressions` emitido no coincide con el bloque "
            f"canónico (falta {value!r})"
        )

    # `@validation_strategy` RESUELTO contra el validation_strategy de plan.
    assert VALIDATION_STRATEGY in section, (
        "PD-10(ii) violada: `integration_gate` no resolvió `@validation_strategy` "
        "contra el `validation_strategy` a nivel de plan"
    )
    assert "@validation_strategy" not in section, (
        "PD-10(ii) violada: la sección dejó el literal `@validation_strategy` sin "
        "resolver"
    )

    # La sección es de LA tarea declarada: no filtra los valores de otra tarea.
    assert T2_FOCAL not in section, (
        "PD-10(ii) violada: la sección de la tarea declarada filtra valores de "
        "otra tarea del bloque canónico"
    )
    assert T2_CHECK not in section, (
        "PD-10(ii) violada: la sección de la tarea declarada filtra valores de "
        "otra tarea del bloque canónico"
    )

    # Dice CUÁNDO ampliar la validación (regla derivada de la estrategia común y
    # del gate/regresiones declarados).
    assert re.search(r"(?i)ampli|expand|widen", section), (
        "PD-10(ii) violada: la sección no dice cuándo AMPLIAR la validación: "
        f"{section.strip()[:300]!r}"
    )
    assert re.search(r"(?i)focal", section), (
        "PD-10(ii) violada: la regla de ampliación no nombra las pruebas focales: "
        f"{section.strip()[:300]!r}"
    )

    # Procedencia del plan (path + sha256), como ya hace con sus instrucciones.
    plan_sha = hashlib.sha256(plan_bytes).hexdigest()
    assert PLAN_REL in packet, (
        f"PD-10(ii) violada: el paquete no declara la procedencia del plan "
        f"(path {PLAN_REL!r})"
    )
    assert plan_sha in packet, (
        "PD-10(ii) violada: el paquete no declara la procedencia del plan "
        "(sha256 de sus bytes)"
    )


def test_pd10_absent_task_fails_closed_naming_id(tmp_path: Path) -> None:
    """PD-10(ii) borde: una tarea AUSENTE del bloque canónico falla cerrado
    nombrando el id, sin emitir proyección por stdout y sin publicar nada."""
    fx = _Fixture(tmp_path)
    before = tree_snapshot(fx.root)
    state_before = (fx.root / "docs" / ".cdad-state.json").read_bytes()

    proc = fx.prepare("--plan-task", "T99")
    out = proc.stdout + proc.stderr

    assert "unrecognized" not in out, (
        f"PD-10 violada: `--plan-task` debe reconocerse: {out.strip()!r}"
    )
    assert proc.returncode != 0, (
        "PD-10 borde violado: una tarea ausente del bloque canónico no falló "
        f"cerrado (rc={proc.returncode})"
    )
    assert proc.stdout == "", (
        f"PD-10 borde violado: el fallo emitió contenido por stdout: "
        f"{proc.stdout[:200]!r}"
    )
    assert re.search(r"(?m)^ERROR: ", proc.stderr), (
        f"PD-10 borde violado: el diagnóstico no tiene el formato `ERROR: …`: "
        f"{proc.stderr.strip()!r}"
    )
    assert "T99" in proc.stderr, (
        f"PD-10 borde violado: el diagnóstico no nombra el id ausente (T99): "
        f"{proc.stderr.strip()!r}"
    )
    assert "Traceback" not in proc.stderr, (
        f"PD-10 borde violado: el fallo cerrado trae traceback: {proc.stderr!r}"
    )
    assert tree_snapshot(fx.root) == before, (
        "PD-10 borde violado: el fallo por tarea ausente publicó archivos"
    )
    assert (fx.root / "docs" / ".cdad-state.json").read_bytes() == state_before, (
        "PD-10 borde violado: el fallo por tarea ausente modificó el estado"
    )


# ---------------------------------------------------------------- PD-10 (iii)


def test_pd10_applicable_contract_references_resolve_to_headings(tmp_path: Path) -> None:
    """PD-10(iii): `## Applicable contract` declara la referencia del contrato
    (path + sha256) IGUAL a la del paquete y los ids aplicables que el encargo
    declara; CADA id emitido resuelve a un encabezado del contrato (pertenencia
    de conjunto, mecánica). Límite honesto: no se afirma que el paquete derive
    la aplicabilidad automáticamente."""
    fx = _Fixture(tmp_path)
    proc = fx.prepare("--plan-task", "T1")
    _require_ok(proc, "prepare --plan-task T1")
    metadata, body = _parse_packet(fx.packet_text())
    section = _section(body, "Applicable contract")
    assert section is not None, (
        "PD-10(iii) violada: falta la sección declarada `## Applicable contract`"
    )

    contract = metadata["contract"]
    assert contract["path"] in section, (
        f"PD-10(iii) violada: la sección no referencia el contrato "
        f"({contract['path']!r})"
    )
    assert contract["sha256"] in section, (
        "PD-10(iii) violada: la referencia del contrato (sha256) no coincide con "
        "la del paquete"
    )

    contract_text = (fx.root / CONTRACT_FILE).read_text(encoding="utf-8")
    ids = re.findall(r"\b(PD-\d+|INV-\d+|D-\d+)\b", section)
    assert ids, (
        "PD-10(iii) violada: la sección `## Applicable contract` no emite ningún "
        "id aplicable (solo la referencia): el encargo declara los ids en la "
        "ficha de su tarea en el plan"
    )
    for token in ids:
        assert re.search(rf"(?m)^#{{1,6}}\s+{re.escape(token)}\b", contract_text), (
            f"PD-10(iii) violada: el id emitido {token!r} no resuelve a un "
            f"encabezado del contrato"
        )


# ---------------------------------------------------------------- PD-10 (iv)


_SUITE = re.compile(r"suite", re.IGNORECASE)
_SUITE_CONDITION = re.compile(
    r"unless|only if|only when|no se corre|salvo|solo si|sólo si|not run|"
    r"does not run|is not run",
    re.IGNORECASE,
)
_SUITE_PACKET = re.compile(r"packet|paquete", re.IGNORECASE)
_SUITE_CLOSER = re.compile(
    r"closer|who closes|quien cierra|la corre quien|el que cierra|closes it",
    re.IGNORECASE,
)


def _suite_policy_declared(text: str) -> bool:
    """¿El texto declara que la suite completa NO se corre salvo que el paquete
    lo pida y que la corre quien cierra? (ventana alrededor de cada `suite`)."""
    for match in _SUITE.finditer(text):
        window = text[max(0, match.start() - 160) : match.start() + 420]
        if (
            _SUITE_CONDITION.search(window)
            and _SUITE_PACKET.search(window)
            and _SUITE_CLOSER.search(window)
        ):
            return True
    return False


def test_pd10_instruction_declares_full_suite_policy(tmp_path: Path) -> None:
    """PD-10(iv): el bloque de instrucción del paquete (sus TRES fuentes
    declaradas en `instruction_sources`, con sus hashes) declara en su parte
    común que la suite completa no se corre salvo que el paquete lo pida y que
    la corre quien cierra; ningún asset de `packets/roles/**` ni
    `packets/substages/**` afirma lo contrario."""
    fx = _Fixture(tmp_path)
    proc = fx.prepare()
    assert proc.returncode == 0, proc.stderr
    metadata, _ = _parse_packet(fx.packet_text())
    sources = metadata.get("instruction_sources")
    assert isinstance(sources, list) and len(sources) == 3, (
        f"PD-10(iv) violada: `instruction_sources` debe declarar las tres fuentes "
        f"(common + rol + subetapa): {sources!r}"
    )
    for entry in sources:
        path = PACKETS_ROOT / entry["path"]
        assert path.is_file(), f"fixture: falta el asset declarado {entry['path']!r}"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], (
            f"PD-10(iv) violada: el hash declarado de {entry['path']!r} no coincide "
            f"con sus bytes"
        )

    common = next(
        (PACKETS_ROOT / e["path"] for e in sources if e["path"] == "common.md"), None
    )
    assert common is not None, (
        f"PD-10(iv) violada: `instruction_sources` no declara la parte común "
        f"(common.md): {[e['path'] for e in sources]!r}"
    )
    common_text = common.read_text(encoding="utf-8")
    composed = "\n".join(
        (PACKETS_ROOT / e["path"]).read_text(encoding="utf-8") for e in sources
    )
    assert _suite_policy_declared(common_text), (
        "PD-10(iv) violada: la parte común de la instrucción no declara que la "
        "suite completa NO se corre salvo que el paquete lo pida (y que la corre "
        "quien cierra)"
    )
    assert _suite_policy_declared(composed), (
        "PD-10(iv) violada: el bloque de instrucción del paquete no declara la "
        "política de la suite completa"
    )

    contradiction = re.compile(r"(?i)complete suite[^\n]{0,40}closure gate")
    assets = sorted(PACKETS_ROOT.glob("roles/*.md")) + sorted(
        PACKETS_ROOT.glob("substages/*.md")
    )
    assert assets, f"fixture: no hay assets de rol/subetapa bajo {PACKETS_ROOT}"
    for asset in assets:
        text = asset.read_text(encoding="utf-8")
        assert not contradiction.search(text), (
            f"PD-10(iv) violada: el asset {asset.relative_to(PACKETS_ROOT)} afirma "
            f"que la suite completa es el gate de cierre (contradice la política "
            f"declarada una sola vez)"
        )
    assert not contradiction.search(composed), (
        "PD-10(iv) violada: la instrucción compuesta todavía afirma que la suite "
        "completa es el gate de cierre"
    )


# ---------------------------------------------------------------- PD-10 (v)


def test_pd10_closure_includes_commit(tmp_path: Path) -> None:
    """PD-10(v): el cierre del encargo incluye el commit — `## Evidence
    required` lo exige y la instrucción lo declara como parte de la entrega.
    Límite honesto: no hay gate automático que lo fuerce (lo audita el
    orquestador)."""
    fx = _Fixture(tmp_path)
    proc = fx.prepare()
    assert proc.returncode == 0, proc.stderr
    packet = fx.packet_text()
    _, body = _parse_packet(packet)
    evidence = _section(body, "Evidence required")
    assert evidence is not None, (
        "PD-10(v) violada: el paquete no emite la sección `## Evidence required`"
    )
    assert re.search(r"(?i)\bcommit\b", evidence), (
        f"PD-10(v) violada: la evidencia de cierre no exige el commit: "
        f"{evidence.strip()!r}"
    )
    assert re.search(
        r"(?is)\bcommit\b.{0,160}(evidence|evidencia|closure|cierre|delivery|"
        r"entrega|report|reporte|include|incluye)",
        packet,
    ), (
        "PD-10(v) violada: la instrucción/el cierre no declara el commit como "
        "parte de la entrega"
    )


# ---------------------------------------------------------------- INV-4


def test_inv4_plan_task_is_declared_optional_and_closure_not_relaxed(
    tmp_path: Path,
) -> None:
    """INV-4 (§2.8 frontera): la extensión es aditiva y DECLARADA — el campo
    opcional `plan_task` valida, y el cierre de campos del request NO se relaja
    (una clave desconocida sigue rechazándose)."""
    fx = _Fixture(tmp_path)
    proc = fx.prepare("--plan-task", "T1")
    _require_ok(proc, "prepare --plan-task T1")

    request_path = fx.packet_dir() / "REQUEST.json"
    request = json.loads(request_path.read_text(encoding="utf-8"))
    assert request.get("plan_task") == "T1", (
        f"PD-10(i)/INV-4 violada: el REQUEST.json no lleva `plan_task`: {request.get('plan_task')!r}"
    )

    declared_ok = fx.validate_request(request_path)
    assert declared_ok.returncode == 0, (
        "INV-4 violada: el campo opcional DECLARADO `plan_task` no valida "
        f"(el conjunto cerrado de campos no lo admite): "
        f"{declared_ok.stderr.strip()!r}"
    )

    mutated = dict(request)
    mutated["totally_unknown_key"] = 1
    mutated_path = fx.root / "mutated-request.json"
    mutated_path.write_text(json.dumps(mutated), encoding="utf-8")
    rejected = fx.validate_request(mutated_path)
    assert rejected.returncode != 0, (
        "INV-4 violada: se relajó el cierre de campos del request (una clave "
        "desconocida fue aceptada)"
    )
    assert rejected.stdout == "", (
        f"INV-4 violada: el rechazo de una clave desconocida emitió stdout: "
        f"{rejected.stdout[:200]!r}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
