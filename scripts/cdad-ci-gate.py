#!/usr/bin/env python3
"""Gate de CI de CDAD: un comando, una corrida, un veredicto atribuible.

Contrato: ``docs/specs/008-005-ci-gate/spec.md`` (PC-1..PC-8, D1..D10,
INV-1..INV-6).

Uso::

    python3 scripts/cdad-ci-gate.py --base <ref> [--repo-root <dir>]
                                    [--evidence-root <dir>]

Orden fijo, cada paso **una** vez (D1): ``validate-state`` -> ``surface
--collect-only`` (solo si el cambio incluye alguna ruta no documental) ->
doctrina -> especializacion Odoo -> ``close --all`` (la unica corrida de
pytest de la corrida entera).

Evidencia (D8/D10): una raiz nueva por invocacion bajo la base de evidencia
(default ``.cdad/local``), con ``gate.json`` (esquema 1) y
``suite-report.md``. Toda corrida deja ``gate.json``, incluso cuando falla
antes de llegar a ``close`` (PC-7): la raiz se reserva antes de resolver la
base.

Codigos de salida: ``0`` verde atribuible; ``1`` rojo (cualquier causa,
nombrada); ``2`` error de uso (``--base`` ausente, raiz de evidencia o
``--repo-root`` inutilizables).

El gate no publica (sin push, tag, red ni instalacion) y escribe solo bajo la
raiz de la corrida (INV-2/INV-3). No reimplementa ``validate-state``,
``surface``, ``close``, el clasificador de rutas ni el parser de pytest: los
invoca (INV-6). Las funciones ``build_verdict``, ``render_report`` y
``extract_failures`` son puras: sin lectura de archivos ni subprocess, para
verificarlas sin pagar la suite (plan W1).

Limite declarado: si la corrida se aborta antes de enumerar el cambio (base que
no resuelve, git que no responde), ``change.kind`` queda ``"desconocido"``
(valor del vocabulario del esquema) y la causa es ``base-invalida`` o
``cambio-ilegible``; los pasos siempre aplicables se registran
``applicable: false`` nombrando la precondicion (F4): el gate prefiere declarar
que no sabe y por que a inventar una clasificacion. Una excepcion imprevista
deja ``gate.json`` con la causa ``fallo-interno`` y salida distinta de cero
(F9/PC-7): la evidencia de la corrida nunca se pierde.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
TOOL = "cdad-ci-gate"
DEFAULT_EVIDENCE_ROOT = ".cdad/local"

GATE_NAMES = ("validate-state", "surface", "doctrine",
              "odoo-specialization", "close")

# Pasos que la tabla D1 declara siempre aplicables. ``surface`` es condicional
# (solo cambio de codigo): sin clasificacion posible no se registra (F4).
ALWAYS_STEPS = tuple(name for name in GATE_NAMES if name != "surface")

# Token estable de cada paso del gate (esquema de ``causes``, PC-2).
STEP_CAUSE = {
    "validate-state": "validate-state-rc",
    "surface": "surface-rc",
    "doctrine": "doctrine-rc",
    "odoo-specialization": "odoo-rc",
    "close": "close-rc",
}

# Vocabulario de ``change.kind``. ``desconocido`` es la clasificacion no
# resuelta por una precondicion fallida (review F3), no un valor inventado.
CHANGE_KINDS = ("sin-cambios", "solo-documentacion", "codigo",
                "desconocido")
CHANGE_UNKNOWN = "desconocido"

# Tokens de precondicion del esquema (review F3): la corrida no llega a los
# pasos y el veredicto es rojo por la causa que los produjo.
PRECONDITION_BASE = "base-invalida"
PRECONDITION_CHANGE = "cambio-ilegible"
PRECONDITION_CAUSES = (PRECONDITION_BASE, PRECONDITION_CHANGE)

# Causa de ultimo recurso: una excepcion imprevista deja evidencia (F9/PC-7).
INTERNAL_FAILURE = "fallo-interno"

# Lineas del bloque "short test summary info" de pytest: ``FAILED nodeid -
# motivo``. El nodeid se toma entero hasta el separador, porque las
# parametrizaciones pueden llevar espacios.
SHORT_SUMMARY_LINE = re.compile(r"^\s*(?P<outcome>FAILED|ERROR)\s+(?P<body>\S.*?)\s*$")

# Linea de progreso de pytest ``-v``: ``nodeid FAILED [ 20%]``.
PROGRESS_LINE = re.compile(
    r"^\s*(?P<nodeid>\S.*?::.*?)\s+(?:FAILED|ERROR)\s+\[\s*\d+%\]\s*$")

# Caches de ejecucion: no son dependencias de la suite (mismo criterio que
# ``scripts/cdad-suite.py``, del que el gate toma el universo de rutas).
CACHE_ARTIFACT_PARTS = ("__pycache__", ".pytest_cache")


class ChangeUnreadable(Exception):
    """El cambio contra la base no se puede enumerar: no hay veredicto."""


def utc_stamp() -> str:
    """Componente ordenable y unico del nombre de la raiz de la corrida."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def write_json_atomic(path: Path, data: dict) -> None:
    """Escribe ``path`` completo o no lo toca: nunca un JSON a medias."""
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    temporary = path.with_name("." + path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def one_line(text) -> str:
    """Detalle en una sola linea, para causas y resumen humano."""
    return " ".join(str(text or "").split())


# ------------------------------------------------------------------ evidencia


def reserve_run_root(evidence_root: Path) -> Path:
    """Raiz nueva de esta corrida, creada en exclusiva (PC-7, D8).

    La base se crea si no existe: un checkout solo-versionado no tiene
    ``.cdad/`` y ese directorio esta ignorado. ``mkdir`` sin ``exist_ok`` es
    la reserva: si el nombre colisiona la corrida falla (codigo 2), nunca
    adopta ni pisa la evidencia de otra corrida.
    """
    evidence_root.mkdir(parents=True, exist_ok=True)
    name = f"gate-{utc_stamp()}-{os.getpid()}-{secrets.token_hex(4)}"
    run_root = evidence_root / name
    os.mkdir(run_root)
    return run_root


def display_path(path: Path) -> str:
    """Ruta relativa a la invocacion cuando vive dentro de ella; si no, absoluta."""
    try:
        relative = os.path.relpath(str(path), os.getcwd())
    except ValueError:
        return str(path)
    if relative.startswith(".."):
        return str(path)
    return Path(relative).as_posix()


def find_attempts(run_root: Path) -> list[Path]:
    """Directorios de intento que ``close`` dejo en la raiz de la corrida."""
    try:
        entries = list(run_root.iterdir())
    except OSError:
        return []
    return sorted(path for path in entries
                  if path.is_dir() and path.name.startswith("attempt-"))


def read_attempt(attempt: Path) -> dict | None:
    """``attempt.json`` del intento, o ``None`` si falta, no es JSON valido o
    no es un objeto.

    Un intento ilegible no se corrige ni se reintenta: se declara no
    atribuible (fail-closed, D4). Un JSON que no es objeto se descarta en el
    borde en vez de propagarse a los consumidores (F9).
    """
    path = attempt / "attempt.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def attempt_stdout_text(attempt: Path, record: dict | None) -> str:
    """Contenido de ``stdout.log`` del intento (fuente de motivos, PC-3)."""
    raw = dig(record, "artifacts", "stdout")
    if not isinstance(raw, str) or not raw:
        raw = "stdout.log"
    path = Path(raw)
    if not path.is_absolute():
        path = attempt / path
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def dig(mapping, *keys):
    """Descenso defensivo por diccionarios anidados; ``None`` si no existe."""
    value = mapping
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


# ---------------------------------------------------------------- git y pasos


def git_run(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    """git del checkout medido; un git inejecutable se reporta como fallo."""
    try:
        return subprocess.run(["git", *args], cwd=str(repo_root),
                              capture_output=True, text=True)
    except OSError as exc:
        return subprocess.CompletedProcess(["git", *args], 127, "", str(exc))


def resolve_commit(repo_root: Path, ref: str) -> str | None:
    """sha de la ref, o ``None`` si la ref no resuelve a un commit (D6)."""
    proc = git_run(repo_root, "rev-parse", "--verify", "--quiet",
                   f"{ref}^{{commit}}")
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def is_cache_artifact(path: str) -> bool:
    parts = Path(path).parts
    return ("__pycache__" in parts or ".pytest_cache" in parts
            or path.endswith((".pyc", ".pyo")))


def changed_paths(repo_root: Path, base_commit: str) -> list[str]:
    """Cambios que ``surface`` considera: comprometidos e indexados desde la
    base, mas los no ignorados, sin renombrar (``--no-renames``).

    El gate solo enumera (D9): la clasificacion de cada ruta la hace el
    clasificador canonico de la politica.
    """
    tracked = git_run(repo_root, "diff", "--name-only", "--no-renames", "-z",
                      base_commit, "--")
    if tracked.returncode != 0:
        raise ChangeUnreadable(
            f"git diff contra {base_commit} fallo: "
            f"{tracked.stderr.strip() or 'sin stderr'}")
    untracked = git_run(repo_root, "ls-files", "--others",
                        "--exclude-standard", "-z")
    if untracked.returncode != 0:
        raise ChangeUnreadable(
            f"git ls-files --others fallo: "
            f"{untracked.stderr.strip() or 'sin stderr'}")
    paths = {path for path in
             (tracked.stdout.split("\0") + untracked.stdout.split("\0"))
             if path}
    return sorted(path for path in paths if not is_cache_artifact(path))


def classify_path(repo_root: Path, path: str) -> str:
    """Clase canonica de la ruta (``python3 scripts/cdad_packet.py
    validate-policy --classify``).

    Una clasificacion ilegible se trata como ``unclassified``: fail-closed,
    el paso de superficie se ejecuta en vez de declararse no aplica.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "scripts/cdad_packet.py", "validate-policy",
             "--classify", path],
            cwd=str(repo_root), capture_output=True, text=True)
    except OSError:
        return "unclassified"
    if proc.returncode != 0:
        return "unclassified"
    for line in proc.stdout.splitlines():
        if line.strip():
            fields = line.split("\t")
            if len(fields) >= 2 and fields[1].strip():
                return fields[1].strip()
            return "unclassified"
    return "unclassified"


def summarize_change(paths: list[str], kinds: list[str]) -> dict:
    """Tipo de cambio y recuentos (D9/PC-4)."""
    documentation = sum(1 for kind in kinds if kind == "documentation")
    if not paths:
        kind = "sin-cambios"
    elif documentation == len(paths):
        kind = "solo-documentacion"
    else:
        kind = "codigo"
    return {"kind": kind, "paths": len(paths),
            "documentation_paths": documentation}


def step_argv(name: str, base: str, run_root: Path) -> list[str]:
    """argv del paso. El ``python3`` del contrato es el interprete en curso
    (``sys.executable``): mismo comando sin depender del PATH (PC-5)."""
    if name == "validate-state":
        return [sys.executable, "scripts/cdad_packet.py", "validate-state"]
    if name == "surface":
        return [sys.executable, "scripts/cdad-suite.py", "surface",
                "--base", base, "--collect-only"]
    if name == "doctrine":
        return [sys.executable, "scripts/cdad-doctrine-check.py", "--quiet"]
    if name == "odoo-specialization":
        return ["bash", "tests/validate-odoo-specialization.sh"]
    if name == "close":
        return [sys.executable, "scripts/cdad-suite.py", "close",
                "--evidence-root", str(run_root), "--all"]
    raise AssertionError(f"paso desconocido: {name}")


def step_detail(proc: subprocess.CompletedProcess) -> str:
    """Detalle registrado del paso: la salida del hijo, sin inventar nada."""
    stderr = (proc.stderr or "").strip()
    stdout = (proc.stdout or "").strip()
    text = stderr or stdout
    if not text:
        return "sin salida"
    if proc.returncode == 0:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[0][:500] if lines else "sin salida"
    return text[:4000]


def surface_selection_detail(stdout: str) -> str:
    """Resumen legible de la seleccion emitida por ``surface --collect-only``."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return "seleccion por superficie emitida (collect-only)"
    nodeids = data.get("nodeids")
    if not isinstance(nodeids, list):
        return "seleccion por superficie emitida (collect-only)"
    return f"seleccion por superficie: {len(nodeids)} nodeid(s) (collect-only)"


def run_step(name: str, argv: list[str], repo_root: Path) -> dict:
    """Ejecuta un paso aplicable una sola vez y registra su veredicto.

    Un paso que no se puede lanzar no se omite en silencio: queda como
    aplicable sin rc y su detalle lo nombra, de modo que el veredicto sea rojo
    con causa (PC-7: toda corrida deja ``gate.json``).
    """
    try:
        proc = subprocess.run(argv, cwd=str(repo_root), capture_output=True,
                              text=True)
    except OSError as exc:
        return {"name": name, "rc": None, "applicable": True,
                "detail": f"el paso no se pudo ejecutar ({argv[0]}): {exc}"}
    if name == "surface" and proc.returncode == 0:
        detail = surface_selection_detail(proc.stdout)
    else:
        detail = step_detail(proc)
    return {"name": name, "rc": proc.returncode, "applicable": True,
            "detail": detail}


def run_gates(repo_root: Path, base: str, run_root: Path,
              change: dict) -> list[dict]:
    """Los cinco pasos en el orden declarado, cada uno una vez (D1/PC-1)."""
    gates = [run_step("validate-state",
                      step_argv("validate-state", base, run_root), repo_root)]
    if change["kind"] == "codigo":
        gates.append(run_step("surface",
                              step_argv("surface", base, run_root),
                              repo_root))
    else:
        gates.append({
            "name": "surface",
            "rc": None,
            "applicable": False,
            "detail": (f"cambio {change['kind']}: {change['paths']} ruta(s), "
                       f"ninguna fuera de documentation (D9/PC-4)"),
        })
    gates.append(run_step("doctrine",
                          step_argv("doctrine", base, run_root), repo_root))
    gates.append(run_step("odoo-specialization",
                          step_argv("odoo-specialization", base, run_root),
                          repo_root))
    gates.append(run_step("close",
                          step_argv("close", base, run_root), repo_root))
    return gates


def precondition_gates(causes: list[dict]) -> list[dict]:
    """Pasos siempre aplicables registrados como no ejecutados (F4/PC-7).

    Una precondicion fallida (base invalida o cambio ilegible) impide
    clasificar el cambio y correr cualquier paso. En vez de ``gates: []``, los
    pasos que el contrato declara ``siempre`` quedan ``applicable: false`` con
    un detalle que nombra la precondicion. ``surface`` no se registra: su
    aplicabilidad depende de la clasificacion que la precondicion impide.
    """
    tokens = ", ".join(cause["token"] for cause in causes) or "sin causa"
    detail = (f"no se ejecuta: precondicion fallida ({tokens}): "
              f"{causes[0]['detail'] if causes else 'sin detalle'}")
    return [{"name": name, "rc": None, "applicable": False, "detail": detail}
            for name in ALWAYS_STEPS]


def measured_commit(repo_root: Path) -> str | None:
    proc = git_run(repo_root, "rev-parse", "HEAD")
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def measured_dirty(repo_root: Path) -> int | None:
    """Entradas de ``git status --porcelain``: el arbol que el gate mide.

    ``None`` (git no responde) no es cero: la atribucion lo trata como no
    atribuible (fail-closed, AC-2).
    """
    proc = git_run(repo_root, "status", "--porcelain")
    if proc.returncode != 0:
        return None
    return len([line for line in proc.stdout.splitlines() if line.strip()])


def loadavg() -> list[float]:
    """Carga de la maquina como diagnostico (PC-8): nunca decide."""
    try:
        return [round(value, 2) for value in os.getloadavg()]
    except (OSError, AttributeError):
        return [0.0, 0.0, 0.0]


# ------------------------------------------------------- funciones puras (W1)


def extract_failures(stdout_text: str, summary: dict | None = None) -> list[dict]:
    """Fallos con nodeid y motivo desde ``stdout.log`` (PC-3).

    Pura. El motivo se toma del bloque ``short test summary info`` de pytest;
    si no es atribuible sin ambiguedad queda ``None`` (nunca se inventa un
    motivo). Las lineas ``ERROR <ruta>`` sin ``::`` son errores de coleccion:
    se nombran por su ruta como fallo no atribuible a un nodeid, con motivo
    ``None`` para que el reporte referencie ``stdout.log`` (F5). ``summary``
    aporta el recuento verificado: si declara cero fallos no se buscan nodeids
    en lineas sueltas.
    """
    failures: list[dict] = []
    positions: dict[str, int] = {}

    def record(key: str, reason: str | None) -> None:
        key = (key or "").strip()
        if not key:
            return
        index = positions.get(key)
        if index is None:
            positions[key] = len(failures)
            failures.append({"nodeid": key, "reason": reason})
            return
        if failures[index]["reason"] is None and reason is not None:
            failures[index]["reason"] = reason

    def add(nodeid: str, reason: str | None) -> None:
        if "::" in (nodeid or ""):
            record(nodeid, reason)

    for line in (stdout_text or "").splitlines():
        match = SHORT_SUMMARY_LINE.match(line)
        if not match:
            continue
        nodeid, separator, reason = match.group("body").partition(" - ")
        if "::" in nodeid:
            add(nodeid, reason.strip() if separator and reason.strip()
                else None)
        else:
            # ``ERROR <ruta>``: error de coleccion, no un nodeid ejecutado.
            record(nodeid, None)

    expected = 0
    if isinstance(summary, dict):
        for key in ("failed", "errors"):
            value = summary.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                expected += value
    if expected:
        for line in (stdout_text or "").splitlines():
            match = PROGRESS_LINE.match(line)
            if match:
                add(match.group("nodeid"), None)

    return failures


def _count(summary: dict, key: str) -> int:
    value = summary.get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 0


def build_verdict(evidence: dict) -> dict:
    """``gate.json`` (esquema 1) a partir de la evidencia recolectada.

    Pura: sin lectura de archivos ni subprocess. ``evidence`` declara
    ``base``, ``base_commit``, ``commit`` (medido), ``dirty`` (medido),
    ``run_root``, ``attempt``, ``change``, ``gates``, ``attempts``,
    ``attempt_record``, ``canary_delta``, ``loadavg``, ``stdout_text`` y
    ``precondition_causes``.

    Atribucion fail-closed (D4/PC-2): verde solo con exactamente un intento,
    ``finished``, ``verified``, ``rc == 0``, commit no nulo y arbol medido
    limpio.
    """
    gates = [dict(gate) for gate in evidence.get("gates") or []]
    attempts = int(evidence.get("attempts") or 0)
    record = evidence.get("attempt_record")
    record = record if isinstance(record, dict) else {}
    summary = record.get("pytest_summary")
    summary = summary if isinstance(summary, dict) else {}
    measured_dirty = evidence.get("dirty")
    change = dict(evidence.get("change") or {})
    if change.get("kind") not in CHANGE_KINDS:
        raise ValueError(f"change.kind fuera del esquema: "
                         f"{change.get('kind')!r}")

    failures = extract_failures(evidence.get("stdout_text") or "", summary)
    pytest_block = {
        "passed": _count(summary, "passed"),
        "failed": _count(summary, "failed"),
        "skipped": _count(summary, "skipped"),
        "errors": _count(summary, "errors"),
        "xfailed": _count(summary, "xfailed"),
        "xpassed": _count(summary, "xpassed"),
        "verified": summary.get("verified") is True,
        "failures": failures,
        "skips": [dict(skip) for skip in (summary.get("skips") or [])
                  if isinstance(skip, dict)],
    }

    attribution = {
        "attributable": False,
        "commit": None,
        "dirty": measured_dirty,
        "attempt_state": None,
        "summary_verified": None,
        "attempts": attempts,
        "causes": [],
    }

    rows: list[dict] = []
    attribution_rows: list[dict] = []
    seen: set[str] = set()

    def add_cause(token: str, detail, *, attribution: bool = False) -> None:
        if token in seen:
            return
        seen.add(token)
        row = {"token": token, "detail": one_line(detail)}
        rows.append(row)
        if attribution:
            attribution_rows.append(row)

    for cause in evidence.get("precondition_causes") or []:
        if cause.get("token") not in PRECONDITION_CAUSES:
            raise ValueError("causa de precondicion fuera del esquema: "
                             f"{cause.get('token')!r}")
        add_cause(cause["token"], cause["detail"])

    for gate in gates:
        if not gate.get("applicable"):
            continue
        token = STEP_CAUSE.get(gate.get("name"))
        if gate.get("rc") != 0 and token:
            add_cause(token, f"paso {gate.get('name')} rc={gate.get('rc')}: "
                             f"{gate.get('detail')}")

    if attempts != 1:
        if attempts == 0:
            add_cause("sin-intento",
                      "la raiz de la corrida no tiene ningun intento; se "
                      "exige exactamente uno", attribution=True)
        else:
            add_cause("intentos-multiples",
                      f"{attempts} intentos en la raiz de la corrida; se "
                      f"exige exactamente uno", attribution=True)
    else:
        commit = record.get("commit")
        state = record.get("state")
        verified = summary.get("verified") is True
        rc = record.get("rc")
        attribution.update(commit=commit, attempt_state=state,
                           summary_verified=verified)
        if state != "finished":
            add_cause("attempt-no-finished", f"estado del intento: {state!r}",
                      attribution=True)
        if not commit:
            add_cause("commit-null", "el intento no declara commit",
                      attribution=True)
        if measured_dirty != 0:
            add_cause("dirty-no-cero",
                      f"el arbol medido tiene {measured_dirty!r} entrada(s) "
                      f"en git status --porcelain; se exige 0",
                      attribution=True)
        if not verified:
            diagnosis = summary.get("diagnosis") or "resumen no verificable"
            add_cause("summary-unverified",
                      f"pytest_summary.verified no es true: {diagnosis}",
                      attribution=True)
        if rc != 0:
            add_cause("close-rc", f"el intento declaro rc={rc!r}",
                      attribution=True)
        attribution["attributable"] = (
            state == "finished" and bool(commit) and measured_dirty == 0
            and verified and rc == 0)

    attribution["causes"] = [f"{row['token']}: {row['detail']}"
                             for row in attribution_rows]

    applicable_green = all(gate.get("rc") == 0 for gate in gates
                           if gate.get("applicable"))
    verdict = ("green" if applicable_green
               and attribution["attributable"] else "red")

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL,
        "base": evidence.get("base"),
        "base_commit": evidence.get("base_commit"),
        "commit": evidence.get("commit"),
        "dirty": measured_dirty,
        "run_root": evidence.get("run_root"),
        "attempt": evidence.get("attempt"),
        "change": change,
        "gates": gates,
        "pytest": pytest_block,
        "attribution": attribution,
        "canary": {"delta_lines": evidence.get("canary_delta")},
        "loadavg": list(evidence.get("loadavg") or []),
        "verdict": verdict,
        "causes": [f"{row['token']}: {row['detail']}" for row in rows],
    }


def render_report(data: dict) -> str:
    """Forma humana del mismo veredicto (D10, PC-3, PC-8). Pura."""
    attempt = data.get("attempt")
    stdout_ref = (f"{attempt}/stdout.log" if attempt
                  else f"{data.get('run_root')}/attempt-*/stdout.log")
    change = data.get("change") or {}
    dirty = data.get("dirty")

    lines = [f"# Gate de CI — {str(data.get('verdict', 'red')).upper()}", ""]
    lines.append(f"- base: {data.get('base')} "
                 f"(sha {data.get('base_commit') or 'sin resolver'})")
    lines.append(f"- commit: {data.get('commit') or 'desconocido'}")
    lines.append(f"- dirty: {dirty if dirty is not None else 'no medido'} "
                 f"archivo(s)")
    lines.append(f"- cambio: {change.get('kind')} "
                 f"({change.get('paths', 0)} ruta(s), "
                 f"{change.get('documentation_paths', 0)} de documentación)")
    lines.append(f"- raíz de la corrida: {data.get('run_root')}")
    lines.append(f"- intento: {attempt or 'ninguno'}")

    lines.extend(["", "## Pasos", ""])
    gates = data.get("gates") or []
    if gates:
        for gate in gates:
            applicable = "aplica" if gate.get("applicable") else "no aplica"
            detail = one_line(gate.get("detail")) or "sin detalle"
            lines.append(f"- {gate.get('name')}: rc={gate.get('rc')} "
                         f"({applicable}) — {detail}")
    else:
        lines.append("- (sin veredicto de pasos registrado)")

    pytest = data.get("pytest") or {}
    lines.extend(["", "## Pytest", ""])
    lines.append(
        "- passed={passed} failed={failed} skipped={skipped} "
        "errors={errors} xfailed={xfailed} xpassed={xpassed} "
        "verified={verified}".format(
            passed=pytest.get("passed", 0),
            failed=pytest.get("failed", 0),
            skipped=pytest.get("skipped", 0),
            errors=pytest.get("errors", 0),
            xfailed=pytest.get("xfailed", 0),
            xpassed=pytest.get("xpassed", 0),
            verified=str(bool(pytest.get("verified"))).lower()))

    failures = pytest.get("failures") or []
    lines.extend(["", "### Fallos", ""])
    if failures:
        lines.append(f"- fuente de motivos: `{stdout_ref}`")
        for item in failures:
            reason = item.get("reason")
            if reason:
                lines.append(f"- `{item.get('nodeid')}`: {reason}")
            else:
                lines.append(f"- `{item.get('nodeid')}`: motivo no atribuible; "
                             f"ver `{stdout_ref}`")
    else:
        lines.append("- (ninguno)")
    unattributed = (_count(pytest, "failed") + _count(pytest, "errors")
                    - len(failures))
    if unattributed > 0:
        lines.append(f"- {unattributed} fallo(s) o error(es) sin nodeid "
                     f"atribuible; ver `{stdout_ref}`")

    lines.extend(["", "### Skips", ""])
    skips = pytest.get("skips") or []
    if skips:
        for item in skips:
            lines.append(f"- `{item.get('nodeid')}`: "
                         f"{item.get('reason') or ''}")
    else:
        lines.append("- (ninguno)")

    canary = (data.get("canary") or {}).get("delta_lines")
    lines.extend(["", "## Diagnóstico", ""])
    lines.append(f"- Canario: delta_lines="
                 f"{canary if canary is not None else 'no medido'} "
                 f"(no decisorio, D5/INV-5)")
    load = data.get("loadavg") or []
    rendered = ", ".join(
        f"{value:.2f}" if isinstance(value, (int, float)) else "n/d"
        for value in load)
    lines.append(f"- Carga (loadavg): {rendered} "
                 f"(no decisoria, INV-5)")

    causes = data.get("causes") or []
    lines.extend(["", "## Causas", ""])
    if causes:
        lines.extend(f"- {cause}" for cause in causes)
    else:
        lines.append("- (ninguna: verde atribuible)")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------- main


def write_evidence(run_root: Path, verdict: dict, report: str) -> None:
    """``gate.json`` y el resumen humano de la corrida (D8/D10)."""
    write_json_atomic(run_root / "gate.json", verdict)
    (run_root / "suite-report.md").write_text(report, encoding="utf-8")


def internal_failure_verdict(base: str, run_root: Path,
                             exc: BaseException) -> dict:
    """``gate.json`` minimo cuando una excepcion imprevista corta la corrida.

    Pura respecto de la evidencia parcial: si el veredicto no se pudo
    construir, no hay veredicto de pasos que declarar. La causa
    ``fallo-interno`` deja la corrida auditable y el veredicto en rojo: una
    excepcion nunca produce un verde (F9/PC-7).
    """
    detail = one_line(f"{type(exc).__name__}: {exc}") or "sin detalle"
    cause = f"{INTERNAL_FAILURE}: {detail}"
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL,
        "base": base,
        "base_commit": None,
        "commit": None,
        "dirty": None,
        "run_root": display_path(run_root),
        "attempt": None,
        "change": {"kind": CHANGE_UNKNOWN, "paths": 0,
                   "documentation_paths": 0},
        "gates": [],
        "pytest": {"passed": 0, "failed": 0, "skipped": 0, "errors": 0,
                   "xfailed": 0, "xpassed": 0, "verified": False,
                   "failures": [], "skips": []},
        "attribution": {"attributable": False, "commit": None, "dirty": None,
                        "attempt_state": None, "summary_verified": None,
                        "attempts": 0, "causes": [cause]},
        "canary": {"delta_lines": None},
        "loadavg": loadavg(),
        "verdict": "red",
        "causes": [cause],
    }


def handle_internal_failure(run_root: Path, base: str,
                            exc: BaseException) -> int:
    """Deja la evidencia del fallo interno y sale != 0 (F9/PC-7).

    ``gate.json`` se escribe primero: es la evidencia que el contrato exige
    incluso cuando la corrida no alcanza un veredicto de pasos.
    """
    verdict = internal_failure_verdict(base, run_root, exc)
    try:
        write_json_atomic(run_root / "gate.json", verdict)
    except OSError as write_exc:
        print(f"cdad-ci-gate: {verdict['causes'][0]}; tampoco se pudo "
              f"escribir {run_root / 'gate.json'}: {write_exc}",
              file=sys.stderr)
        return 1
    try:
        (run_root / "suite-report.md").write_text(render_report(verdict),
                                                  encoding="utf-8")
    except OSError as report_exc:
        print(f"cdad-ci-gate: gate.json escrito; el resumen humano fallo: "
              f"{report_exc}", file=sys.stderr)
    print(f"cdad-ci-gate: {verdict['causes'][0]}; evidencia en {run_root}",
          file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdad-ci-gate.py",
        description="Gate de CI de CDAD: un comando, una corrida, un "
                    "veredicto atribuible.")
    parser.add_argument("--base", required=True,
                        help="ref contra la que se clasifica el cambio "
                             "(obligatoria: no hay default silencioso, D6)")
    parser.add_argument("--repo-root", default=None,
                        help="checkout a medir (costura de test; default: el "
                             "checkout del script)")
    parser.add_argument("--evidence-root", default=DEFAULT_EVIDENCE_ROOT,
                        help="base donde se reserva la raiz de esta corrida "
                             f"(default {DEFAULT_EVIDENCE_ROOT})")
    return parser


def execute_run(repo_root: Path, base: str, run_root: Path) -> int:
    """Una corrida completa: precondiciones, pasos, veredicto y evidencia."""
    base_commit = resolve_commit(repo_root, base)
    precondition_causes: list[dict] = []
    change = {"kind": CHANGE_UNKNOWN, "paths": 0, "documentation_paths": 0}
    paths: list[str] | None = None

    if base_commit is None:
        precondition_causes.append({
            "token": PRECONDITION_BASE,
            "detail": f"la base {base!r} no resuelve a un commit en "
                      f"{repo_root}; no se ejecuta ningun paso",
        })
    else:
        try:
            paths = changed_paths(repo_root, base_commit)
        except ChangeUnreadable as exc:
            precondition_causes.append({"token": PRECONDITION_CHANGE,
                                        "detail": str(exc)})
        else:
            kinds = [classify_path(repo_root, path) for path in paths]
            change = summarize_change(paths, kinds)

    commit = measured_commit(repo_root)
    dirty = measured_dirty(repo_root)

    gates = (run_gates(repo_root, base, run_root, change)
             if paths is not None else precondition_gates(precondition_causes))

    attempts = find_attempts(run_root)
    record = read_attempt(attempts[0]) if len(attempts) == 1 else None
    stdout_text = (attempt_stdout_text(attempts[0], record)
                   if len(attempts) == 1 else "")
    canary_delta = dig(record, "canary", "delta_lines")

    verdict = build_verdict({
        "base": base,
        "base_commit": base_commit,
        "commit": commit,
        "dirty": dirty,
        "run_root": display_path(run_root),
        "attempt": display_path(attempts[0]) if len(attempts) == 1 else None,
        "change": change,
        "gates": gates,
        "attempts": len(attempts),
        "attempt_record": record,
        "canary_delta": canary_delta,
        "loadavg": loadavg(),
        "stdout_text": stdout_text,
        "precondition_causes": precondition_causes,
    })

    report = render_report(verdict)
    write_evidence(run_root, verdict, report)

    print(f"cdad-ci-gate: evidencia en {run_root}", file=sys.stderr)
    sys.stdout.write(report)
    return 0 if verdict["verdict"] == "green" else 1


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    repo_root = (Path(args.repo_root).expanduser().resolve() if args.repo_root
                 else Path(__file__).resolve().parents[1])
    if not repo_root.is_dir():
        print(f"cdad-ci-gate: --repo-root no es un directorio: {repo_root}",
              file=sys.stderr)
        return 2

    evidence_root = Path(args.evidence_root).expanduser()
    try:
        run_root = reserve_run_root(evidence_root)
    except OSError as exc:
        print(f"cdad-ci-gate: raiz de evidencia inutilizable "
              f"({evidence_root}): {exc}", file=sys.stderr)
        return 2

    try:
        return execute_run(repo_root, args.base, run_root)
    except Exception as exc:  # noqa: BLE001 -- ultimo recurso (F9/PC-7)
        return handle_internal_failure(run_root, args.base, exc)


if __name__ == "__main__":
    sys.exit(main())
