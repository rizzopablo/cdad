#!/usr/bin/env python3
"""Selector canonico de la suite por capacidad y contrato (008-002 §5).

Nueve subcomandos, sin framework nuevo: la ejecucion delegada es el pytest ya
instalado.

- ``validate``  integridad estructural del inventario, del mapa y de la
                disposicion temporal frente a la coleccion real de pytest.
- ``list``      nodeids de una capacidad, ordenados y sin duplicados (JSON).
- ``run``       ejecuta exactamente esa seleccion y propaga el resultado.
- ``surface``   selecciona por superficie contra una ref de git.
- ``measure``   medicion informativa y read-only del universo de tests.
- ``close``     gate final del closer: reserva un directorio de intento propio
                y conserva comando, seleccion, commit, estado, tiempos,
                resultado, skips, salidas y snapshots del canario (PC-6, AJ7),
                mas ``pytest.xml`` y ``profile.json`` de la unica corrida
                (017-001 T1: resultados y fases sin cambiar el cierre).
- ``reconcile`` agregacion contable de un intento segun spec §4.4
                (017-001 T3): S_test/atribuido/resto por test, S_file por
                archivo, compartidas separadas y residuos con signo.
- ``entry-check`` comprobacion de la condicion de entrada a la base sobre un
                mapa seleccion->intento (017-001 T3).

El CLI se invoca con cwd = raiz del repositorio a validar.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import platform
import re
import secrets
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

SPEC_DIR = Path("docs/specs/008-002-suite-by-capability")
INVENTORY_PATH = SPEC_DIR / "suite-inventory.json"
PC_MAP_PATH = SPEC_DIR / "pc-map.json"
TIMING_PATH = SPEC_DIR / "timing-disposition.json"
MEASUREMENT_PATH = SPEC_DIR / "measurement-before.json"

# Un cambio en el propio selector o en el mapa/inventario obliga a conservar la
# seleccion completa: se desconocen (por definicion) las asignaciones que la
# version nueva agrega.
SELECTOR_SOURCE = Path("scripts/cdad-suite.py")
SELECTION_ARTIFACTS = {INVENTORY_PATH, PC_MAP_PATH, SELECTOR_SOURCE}

MODULE_KINDS = {"test", "helper", "bootstrap"}
DECISIONS = {"mantener", "fusionar", "eliminar"}
TIMING_KEYS = (
    "target_ceiling_s",
    "effective_threshold_s",
    "status",
    "evidence",
    "measurement_scope",
    "reason_5s_not_2s",
    "resolution_criterion",
    "cases",
)


class Diagnosis(Exception):
    """Falla de contrato o de datos: se reporta y termina no cero."""


class UsageError(Diagnosis):
    """Error de uso o de reserva de ``close``: termina con codigo 2 (AJ7)."""


# --------------------------------------------------------------------- datos


def read_json(path: Path, *, required: bool = True):
    """Artefacto JSON del arbol de trabajo, o ``None`` si falta y es opcional."""
    if not path.is_file():
        if required:
            raise Diagnosis(f"falta {path.as_posix()}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Diagnosis(f"{path.as_posix()} no es JSON valido: {exc}") from exc


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise Diagnosis(f"git {' '.join(args)} fallo: {proc.stderr.strip()}")
    return proc


def git_json(ref: str, path: Path):
    """Version de ``ref`` para ``path``; ``None`` si la ref no la tiene."""
    proc = git("show", f"{ref}:{path.as_posix()}", check=False)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise Diagnosis(f"{ref}:{path.as_posix()} no es JSON valido: {exc}") from exc


def collect_nodeids() -> list[str]:
    """Coleccion real de pytest del universo ``tests/`` (spec §7)."""
    scope = Path("tests")
    if not scope.is_dir():
        raise Diagnosis("no existe el directorio tests/ en la raiz del repositorio")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider", scope.as_posix()],
        capture_output=True, text=True)
    if proc.returncode not in (0, 5):  # 5 = sin tests recolectados
        detail = (proc.stdout + proc.stderr).strip()[-4000:]
        raise Diagnosis(f"pytest no pudo recolectar {scope.as_posix()}/:\n{detail}")
    return sorted({line.strip() for line in proc.stdout.splitlines()
                   if "::" in line})


def suite_modules() -> list[str]:
    """Modulos Python versionables del arbol bajo ``tests/``."""
    return sorted(path.as_posix() for path in Path("tests").rglob("*.py")
                  if "__pycache__" not in path.parts)


def nodeids_of_module(collected: list[str], module_path: str) -> list[str]:
    return [nodeid for nodeid in collected if nodeid.split("::")[0] == module_path]


def assignment_nodeids(module_path: str, assignment: dict,
                       collected: list[str]) -> list[str]:
    """Nodeids que aporta una asignacion: explicitos o el modulo completo."""
    explicit = assignment.get("nodeids")
    if explicit:
        return list(explicit)
    if assignment.get("nodeid"):
        return [assignment["nodeid"]]
    if assignment.get("scope") == "module":
        return nodeids_of_module(collected, module_path)
    return []


def module_nodeids(module: dict, collected: list[str]) -> list[str]:
    selected: list[str] = []
    for assignment in module.get("assignments") or []:
        selected.extend(assignment_nodeids(module["path"], assignment, collected))
    return selected


def capability_nodeids(module: dict, capability: str,
                       collected: list[str]) -> list[str]:
    selected: list[str] = []
    for assignment in module.get("assignments") or []:
        if assignment.get("capability") == capability:
            selected.extend(assignment_nodeids(module["path"], assignment, collected))
    return selected


def capability_selection(inventory: dict, capability: str,
                         collected: list[str]) -> list[str]:
    declared = inventory.get("capabilities") or []
    if capability not in declared:
        raise Diagnosis(
            f"capacidad desconocida: {capability!r} "
            f"(declaradas: {', '.join(map(str, declared))})")
    selected: list[str] = []
    for module in inventory.get("modules") or []:
        selected.extend(capability_nodeids(module, capability, collected))
    unique = sorted(set(selected))
    if not unique:
        raise Diagnosis(f"la capacidad {capability!r} no selecciona ningun nodeid")
    return unique


# ------------------------------------------------------------------ validate


def check_inventory(inventory: dict, collected: list[str]) -> list[str]:
    problems: list[str] = []
    declared = inventory.get("capabilities")
    if not isinstance(declared, list) or not declared:
        return ["suite-inventory.json sin 'capabilities'"]
    modules = inventory.get("modules")
    if not isinstance(modules, list):
        return ["suite-inventory.json sin 'modules'"]

    by_path: dict[str, dict] = {}
    for module in modules:
        path = module.get("path")
        if not path:
            problems.append("suite-inventory.json: modulo sin 'path'")
            continue
        by_path[path] = module
        if module.get("kind") not in MODULE_KINDS:
            problems.append(f"{path}: kind invalido {module.get('kind')!r}")
        if module.get("decision") not in DECISIONS:
            problems.append(f"{path}: decision invalida {module.get('decision')!r}")

    for path in suite_modules():
        if path not in by_path:
            problems.append(f"modulo del arbol sin inventariar: {path}")
    for path in by_path:
        if not Path(path).is_file():
            problems.append(f"inventario declara un modulo inexistente: {path}")

    assigned: set[str] = set()
    collected_set = set(collected)
    for path, module in sorted(by_path.items()):
        assignments = module.get("assignments") or []
        if module.get("kind") == "test" and not assignments:
            problems.append(f"{path}: test sin asignacion de capacidad/contrato")
        for assignment in assignments:
            capability = assignment.get("capability")
            if capability not in declared:
                problems.append(f"{path}: capacidad desconocida {capability!r}")
            if not assignment.get("contract"):
                problems.append(f"{path}: asignacion sin 'contract'")
            if (assignment.get("scope") == "module"
                    and (assignment.get("nodeids") or assignment.get("nodeid"))):
                problems.append(
                    f"{path}: asignacion 'module' con nodeids explicitos "
                    f"(asignacion mixta incompleta)")
            nodeids = assignment_nodeids(path, assignment, collected)
            if not nodeids and module.get("kind") == "test":
                problems.append(f"{path}: test sin nodeids ni scope 'module'")
            for nodeid in nodeids:
                if nodeid not in collected_set:
                    problems.append(f"{path}: nodeid inexistente en la coleccion: {nodeid}")
            assigned.update(nodeids)

    for nodeid in collected:
        if nodeid not in assigned:
            problems.append(f"nodeid recolectado sin capacidad/contrato: {nodeid}")
    return problems


def _is_collectible(nodeid: str, collected_set: set[str]) -> bool:
    """Un nodeid es recolectable si pytest lo colecciona tal cual.

    Las variantes documentadas dentro de un test plano (``unittest.subTest`` o
    etiquetas ``[variante ...]``) no son nodeids propios de pytest: la variante
    se ejerce dentro de su nodeid base, que es el recolectable. Un nodeid
    parametrizado inexistente se rechaza porque su base no se colecciona sola.
    """
    if nodeid in collected_set:
        return True
    match = re.fullmatch(r"(?P<base>.+)\[[^\[\]]*\]", nodeid)
    return bool(match) and match.group("base") in collected_set


def check_map(pc_map: dict, collected: list[str]) -> tuple[list[str], list[str]]:
    """Integridad estructural del mapa; devuelve (problemas, placeholders)."""
    problems: list[str] = []
    placeholders: list[str] = []
    entries = pc_map.get("entries")
    if not isinstance(entries, list):
        return (["pc-map.json sin 'entries'"], placeholders)

    collected_set = set(collected)
    for index, entry in enumerate(entries):
        original = entry.get("original_nodeid")
        label = original if isinstance(original, str) and original else f"entrada #{index}"
        target = entry.get("target_nodeid")
        decision = entry.get("decision")
        status = entry.get("status")
        if decision not in DECISIONS:
            problems.append(f"{label}: decision invalida {decision!r}")
        if isinstance(target, str) and "::" in target:
            if not _is_collectible(target, collected_set):
                problems.append(f"{label}: destino inexistente en la coleccion ({target})")
        elif decision in {"fusionar", "eliminar"}:
            problems.append(f"{label}: {decision} sin nodeid destino ({target!r})")
        else:
            # Una entrada 'mantener' con destino no-nodeid declara que no hay
            # sustituto; se expone, no se acepta como destino recolectable.
            placeholders.append(f"{label}: sin nodeid destino ({target!r})")
        if decision == "eliminar" and status == "VERIFY":
            problems.append(f"{label}: eliminacion con VERIFY pendiente (status={status!r})")
        if decision in {"fusionar", "eliminar"} and not entry.get("equivalence_justification"):
            problems.append(f"{label}: {decision} sin justificacion de equivalencia")
    return (problems, placeholders)


def baseline_ref() -> str:
    """Revision contra la que se contrastan las obligaciones acreditadas (PC-3).

    La baseline es la revision registrada en ``measurement-before.json`` (§7): un
    commit posterior puede borrar una obligacion ya acreditada y ``HEAD`` no lo
    delataria. Si el artefacto no existe o no declara commit, se usa ``HEAD``.
    """
    measurement = read_json(MEASUREMENT_PATH, required=False) or {}
    commit = measurement.get("commit")
    return commit.strip() if isinstance(commit, str) and commit.strip() else "HEAD"


def check_accredited_preserved(pc_map: dict) -> list[str]:
    """Una obligacion acreditada en la baseline no puede desaparecer del mapa."""
    ref = baseline_ref()
    previous = git_json(ref, PC_MAP_PATH)
    if previous is None:
        return []
    current = {entry.get("original_nodeid") for entry in pc_map.get("entries") or []}
    problems: list[str] = []
    for entry in previous.get("entries") or []:
        if entry.get("status") != "acreditada":
            continue
        original = entry.get("original_nodeid")
        if original not in current:
            problems.append(
                f"obligacion acreditada desaparecida del mapa: {original} "
                f"(baseline {ref})")
    return problems


def check_timing(timing) -> list[str]:
    if timing is None:
        return [f"falta {TIMING_PATH.as_posix()} (deuda temporal, PC-7)"]
    problems = [f"{TIMING_PATH.as_posix()}: falta {key!r}"
                for key in TIMING_KEYS if key not in timing]
    if problems:
        return problems
    if timing["status"] not in {"pending", "resolved"}:
        problems.append(f"{TIMING_PATH.as_posix()}: status invalido {timing['status']!r}")
    evidence = timing["evidence"]
    if not isinstance(evidence, list):
        problems.append(f"{TIMING_PATH.as_posix()}: 'evidence' debe ser una lista")
        evidence = []
    if timing["status"] == "resolved":
        if not evidence:
            problems.append(
                f"{TIMING_PATH.as_posix()}: declara 'resolved' sin evidencia propia")
        for ref in evidence:
            path = str(ref).split("::")[0].split(":")[0]
            if not Path(path).is_file():
                problems.append(
                    f"{TIMING_PATH.as_posix()}: evidencia de resolucion inexistente: {ref}")
        if timing["target_ceiling_s"] != 2:
            problems.append(
                f"{TIMING_PATH.as_posix()}: declara 'resolved' con "
                f"target_ceiling_s={timing['target_ceiling_s']!r} (el techo objetivo es 2 s)")
    if not timing["cases"]:
        problems.append(f"{TIMING_PATH.as_posix()}: sin casos declarados")
    return problems


def cmd_validate() -> int:
    inventory = read_json(INVENTORY_PATH)
    pc_map = read_json(PC_MAP_PATH)
    timing = read_json(TIMING_PATH, required=False)
    collected = collect_nodeids()

    problems = check_inventory(inventory, collected)
    map_problems, placeholders = check_map(pc_map, collected)
    problems += map_problems
    problems += check_accredited_preserved(pc_map)
    problems += check_timing(timing)
    if problems:
        raise Diagnosis("validate: integridad insuficiente\n"
                        + "\n".join(f"- {problem}" for problem in problems))

    print(json.dumps({
        "status": "ok",
        "collected_nodeids": len(collected),
        "inventoried_modules": len(inventory.get("modules") or []),
        "map_entries": len(pc_map.get("entries") or []),
        "timing": {
            "status": timing["status"],
            "target_ceiling_s": timing["target_ceiling_s"],
            "effective_threshold_s": timing["effective_threshold_s"],
            "cases": [case.get("nodeid") if isinstance(case, dict) else case
                      for case in timing["cases"]],
        },
        "placeholder_targets": placeholders,
    }, indent=2, sort_keys=True))
    return 0


# ------------------------------------------------------------ list / run


def cmd_list(capability: str) -> int:
    inventory = read_json(INVENTORY_PATH)
    nodeids = capability_selection(inventory, capability, collect_nodeids())
    print(json.dumps({"capability": capability, "nodeids": nodeids}, indent=2))
    return 0


def run_pytest(nodeids: list[str]) -> int:
    if not nodeids:
        raise Diagnosis("seleccion vacia: no hay nodeids que ejecutar")
    print(f"cdad-suite: ejecutando {len(nodeids)} nodeid(s)", file=sys.stderr)
    for nodeid in nodeids:
        print(f"  {nodeid}", file=sys.stderr)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *nodeids]
    ).returncode


def cmd_run(capability: str) -> int:
    inventory = read_json(INVENTORY_PATH)
    return run_pytest(capability_selection(inventory, capability, collect_nodeids()))


# ------------------------------------------------------------------- surface


def _is_cache_artifact(path: str) -> bool:
    """Caches de ejecucion: no son dependencias de la suite."""
    parts = Path(path).parts
    return ("__pycache__" in parts or ".pytest_cache" in parts
            or path.endswith((".pyc", ".pyo")))


def changed_paths(base: str) -> list[str]:
    """Cambios comprometidos, indexados, no indexados y no ignorados vs base.

    ``--no-renames`` es deliberado: la deteccion de renombres de git oculta la
    ruta vieja y un test trasladado debe consultar el mapa de la base (§5).
    """
    tracked = git("diff", "--name-only", "--no-renames", "-z", base, "--")
    untracked = git("ls-files", "--others", "--exclude-standard", "-z")
    return sorted({path for path in
                   (tracked.stdout.split("\0") + untracked.stdout.split("\0"))
                   if path and not _is_cache_artifact(path)})


def _surface_matches(path: str, surface) -> bool:
    surface_path = str(surface or "").strip().rstrip("/")
    if not surface_path:
        return False
    return (path == surface_path
            or path.startswith(surface_path + "/")
            or surface_path.startswith(path.rstrip("/") + "/"))


def surface_consumers(path: str, inventory: dict,
                      collected: list[str]) -> list[str]:
    selected: list[str] = []
    for module in inventory.get("modules") or []:
        if any(_surface_matches(path, surface)
               for surface in module.get("product_surfaces") or []):
            selected.extend(module_nodeids(module, collected))
    return selected


def helper_consumers(helper_path: str, inventory: dict,
                     collected: list[str]) -> list[str]:
    """Consumidores declarados de un helper.

    ``helper_dependencies`` puede nombrarlo por ruta (``tests/shared_helper.py``)
    o por stem (``shared_helper``), como hace el inventario T2.
    """
    wanted_paths = {helper_path}
    if helper_path.endswith(".py"):
        wanted_paths.add(helper_path[:-3])
    wanted_stem = Path(helper_path).stem
    selected: list[str] = []
    for module in inventory.get("modules") or []:
        dependencies = [str(dependency).split("::")[0]
                        for dependency in module.get("helper_dependencies") or []]
        if any(dependency in wanted_paths or Path(dependency).stem == wanted_stem
               for dependency in dependencies):
            selected.extend(module_nodeids(module, collected))
    return selected


def substitutes_for_removed_module(path: str, base_inventory, base_map,
                                   collected: list[str]) -> list[str]:
    """Sustitutos y contratos afectados de un test eliminado o trasladado."""
    collected_set = set(collected)
    selected: list[str] = []
    contracts = set()
    for module in (base_inventory or {}).get("modules") or []:
        if module.get("path") != path:
            continue
        contracts.update(assignment.get("contract")
                         for assignment in module.get("assignments") or [])
    for entry in (base_map or {}).get("entries") or []:
        original = str(entry.get("original_nodeid") or "")
        if original.split("::")[0] != path:
            continue
        target = entry.get("target_nodeid")
        if isinstance(target, str) and target in collected_set:
            selected.append(target)
    for module in (base_inventory or {}).get("modules") or []:
        if module.get("path") == path:
            continue
        for assignment in module.get("assignments") or []:
            if assignment.get("contract") in contracts:
                selected.extend(assignment_nodeids(module["path"], assignment, collected))
    return selected


def selection_for_changes(changes: list[str], inventory: dict, base_inventory,
                          base_map, collected: list[str]) -> list[str]:
    modules = {module.get("path"): module for module in inventory.get("modules") or []}
    selection_artifacts = {artifact.as_posix() for artifact in SELECTION_ARTIFACTS}
    selected: list[str] = []
    unresolved: list[str] = []

    for path in changes:
        if path in selection_artifacts:
            selected.extend(collected)
            continue
        if path.startswith("docs/"):
            continue  # documentacion: no es dependencia de la suite
        if path.startswith("tests/") and path.endswith(".py"):
            kind = (modules.get(path) or {}).get("kind")
            if kind == "bootstrap":
                selected.extend(collected)
            elif kind == "helper":
                consumers = helper_consumers(path, inventory, collected)
                if not consumers:
                    unresolved.append(f"{path}: helper sin consumidores declarados")
                selected.extend(consumers)
            elif Path(path).is_file():
                nodeids = nodeids_of_module(collected, path)
                if not nodeids:
                    unresolved.append(f"{path}: modulo de test sin nodeids recolectados")
                selected.extend(nodeids)
            else:
                substitutes = substitutes_for_removed_module(
                    path, base_inventory, base_map, collected)
                if not substitutes:
                    unresolved.append(
                        f"{path}: test eliminado sin sustituto recolectable en la base")
                selected.extend(substitutes)
            continue
        consumers = surface_consumers(path, inventory, collected)
        if not consumers:
            unresolved.append(f"{path}: cambio sin superficie clasificada")
        selected.extend(consumers)

    if unresolved:
        raise Diagnosis("seleccion por superficie incompleta\n"
                        + "\n".join(f"- {item}" for item in unresolved))
    unique = sorted(set(selected))
    if not unique:
        raise Diagnosis("surface: la seleccion resultante esta vacia")
    return unique


def cmd_surface(base: str, all_flag: bool, collect_only: bool) -> int:
    base_inventory = git_json(base, INVENTORY_PATH)
    base_map = git_json(base, PC_MAP_PATH)
    if not all_flag:
        missing = [artifact.as_posix() for artifact, value in
                   ((INVENTORY_PATH, base_inventory), (PC_MAP_PATH, base_map))
                   if value is None]
        if missing:
            raise Diagnosis(
                f"la base {base!r} no tiene {', '.join(missing)}; "
                f"no se selecciona nada sin inventario y mapa "
                f"(usar --all para seleccionar todos los nodeids actuales)")

    inventory = read_json(INVENTORY_PATH)
    collected = collect_nodeids()
    if all_flag:
        selection = collected
    else:
        selection = selection_for_changes(
            changed_paths(base), inventory, base_inventory, base_map, collected)

    print(json.dumps({"base": base, "all": all_flag, "nodeids": selection},
                     indent=2))
    if collect_only:
        return 0
    return run_pytest(selection)


# ------------------------------------------------------------------- measure


def cmd_measure() -> int:
    listing = git("ls-files", "-z", "--", "tests/*.py")
    paths = sorted({path for path in listing.stdout.split("\0") if path})
    inventory = read_json(INVENTORY_PATH, required=False)
    kinds = {module.get("path"): module.get("kind")
             for module in (inventory or {}).get("modules") or []}

    files = []
    totals = {"files": 0, "bytes": 0, "lf_lines": 0}
    for path in paths:
        data = Path(path).read_bytes()
        kind = kinds.get(path) or "test"
        files.append({"path": path, "kind": kind, "bytes": len(data),
                      "lf_lines": data.count(b"\n"),
                      "sha256": hashlib.sha256(data).hexdigest()})
        totals["files"] += 1
        totals["bytes"] += len(data)
        totals["lf_lines"] += data.count(b"\n")
        totals[kind] = totals.get(kind, 0) + 1

    commit = git("rev-parse", "HEAD", check=False).stdout.strip() or None
    print(json.dumps({
        "schema_version": 1,
        "commit": commit,
        "python": platform.python_version(),
        "universe": "git ls-files -z -- 'tests/*.py' (sorted)",
        "manifest_hash_method":
            "sha256(json.dumps(files, sort_keys=True, separators=(',',':')).encode())",
        "manifest_sha256": hashlib.sha256(
            json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "files": files,
        "totals": totals,
    }, indent=2, sort_keys=True))
    return 0


# --------------------------------------------------------------------- close


CLOSE_SCHEMA_VERSION = 1

# Perfil de medicion de T1+T2 (017-001 spec §4.2: resultados, fases y
# operaciones). El alcance de operaciones aplicado se declara por intento con
# su referencia inequivoca (ruta, sha256 y estado); cuando es ilegible la
# medicion queda incompleta diagnosticada, nunca acreditada sin alcance.
PROFILE_SCHEMA_VERSION = 1
PROFILE_PHASE_SINK = "phases-raw.json"
OBSERVER_MODULE = "cdad_suite_observer"
OBSERVER_SINK_ENV = "CDAD_SUITE_PHASE_SINK"
OPERATION_SCOPE_UNREADABLE_STATUS = "missing"
OPERATION_SCOPE_PLANNED_PATH = (
    "docs/specs/017-001-suite-performance/performance/operation-scope.json")

# Canario heredado de 008-001: rutas nombradas del HOME real, nunca todo el
# HOME ni el repo, que el propio ciclo escribe en vivo.
CANARY_NAMED_ROOTS = ("~/.config/cdad", "~/.config/opencode", "~/.local/state/cdad")

# ``-v`` imprime una linea por test con su nodeid, resultado y motivo de skip;
# de ahi se derivan los recuentos y la lista de omisiones sin parsear el
# resumen agregado (que no nombra nodeids).
PYTEST_STATUS_LINE = re.compile(
    r"^(?P<nodeid>.+?) "
    r"(?P<outcome>PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)"
    r"(?: \((?P<detail>.*)\))?"
    r"(?:\s*\[\s*\d+%\])?\s*$")

# Una linea con nodeid y un token de resultado que ``PYTEST_STATUS_LINE`` no
# acepta es una linea de estado ilegible: se declara, no se descarta.
PYTEST_OUTCOME_TOKEN = re.compile(r"\b(?:PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b")


def utc_now() -> str:
    """Instante UTC en ISO 8601 con sufijo Z."""
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return stamp.replace("+00:00", "Z")


def utc_now_fine() -> str:
    """Instante UTC en ISO 8601 con zona y microsegundos.

    Para las paredes por worker del lote paralelo (017-001 T6 M2): la
    resolucion de segundos de ``utc_now`` cuantizaria la pared y la
    comprobacion ``wall_s == finished_at - started_at`` fallaria. Con
    microsegundos el error de cuantizacion es despreciable frente a la
    tolerancia de 1e-3 s.
    """
    stamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    return stamp.replace("+00:00", "Z")


def utc_attempt_stamp() -> str:
    """Componente ordenable y unico del nombre de intento."""
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


def file_sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def selection_artifact_hashes() -> dict:
    """Hashes de los artefactos que definen la seleccion (PC-6).

    Ausente = ``None``: la ausencia se declara, no se disimula con un hash de
    cadena vacia.
    """
    return {artifact.as_posix(): file_sha256(artifact)
            for artifact in sorted(SELECTION_ARTIFACTS)}


def _canary_walk(root: Path):
    """Recorre ``root`` sin seguir enlaces; omite lo inaccesible."""
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            continue
        for entry in entries:
            path = Path(entry.path)
            yield path
            try:
                if entry.is_dir(follow_symlinks=False):
                    stack.append(path)
            except OSError:
                continue


def canary_scope() -> list[str]:
    home = Path.home()
    scope = [str(Path(raw).expanduser()) for raw in CANARY_NAMED_ROOTS]
    scope.append(f"{home} (entradas de primer nivel)")
    return scope


def canary_snapshot() -> list[str]:
    """Inventario ``ruta|bytes|mtime_ns`` de las rutas declaradas del canario."""
    lines: list[str] = []
    for raw in CANARY_NAMED_ROOTS:
        root = Path(raw).expanduser()
        if not root.exists():
            continue
        for path in _canary_walk(root):
            try:
                stat = path.lstat()
            except OSError:
                continue
            lines.append(f"{path}|{stat.st_size}|{stat.st_mtime_ns}")
    home = Path.home()
    try:
        lines.extend(f"{home}/{entry.name}" for entry in os.scandir(home))
    except OSError:
        pass
    return sorted(lines)


def write_canary(path: Path, snapshot: list[str]) -> None:
    path.write_text("".join(f"{line}\n" for line in snapshot), encoding="utf-8")


def canary_delta_lines(before: list[str], after: list[str]) -> int:
    """Lineas cambiadas entre snapshots, con el mismo criterio que el gate
    historico de 008-001: cuerpo del diff unificado, sin sus dos cabeceras."""
    diff = list(difflib.unified_diff(before, after, lineterm=""))
    return len(diff[2:]) if len(diff) > 2 else 0


def parse_pytest_verbose(output: str) -> dict:
    """Resumen de pytest derivado de sus lineas por test.

    El resumen **declara si es verificable**: si no aparece ninguna linea de
    estado, o alguna linea de resultado no se puede parsear, ``verified`` queda
    en ``False`` con un ``diagnosis``. Nunca se presenta un cero silencioso
    como si fuera un recuento observado (PC-6).
    """
    summary = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0,
               "xfailed": 0, "xpassed": 0, "skips": [],
               "verified": False, "unparsed_lines": [], "diagnosis": None}
    matched = 0
    for line in output.splitlines():
        match = PYTEST_STATUS_LINE.match(line)
        if not match:
            if "::" in line and PYTEST_OUTCOME_TOKEN.search(line):
                summary["unparsed_lines"].append(line.strip()[:200])
            continue
        matched += 1
        outcome = match.group("outcome")
        if outcome == "PASSED":
            summary["passed"] += 1
        elif outcome == "FAILED":
            summary["failed"] += 1
        elif outcome == "ERROR":
            summary["errors"] += 1
        elif outcome == "SKIPPED":
            summary["skipped"] += 1
            summary["skips"].append({"nodeid": match.group("nodeid"),
                                     "reason": match.group("detail") or ""})
        elif outcome == "XFAIL":
            summary["xfailed"] += 1
        elif outcome == "XPASS":
            summary["xpassed"] += 1

    if not matched:
        summary["diagnosis"] = (
            "no se encontro ninguna linea de estado de pytest en stdout.log: "
            "los recuentos no son verificables")
    elif summary["unparsed_lines"]:
        summary["diagnosis"] = (
            f"{len(summary['unparsed_lines'])} linea(s) de resultado ilegibles "
            "en stdout.log: los recuentos pueden estar incompletos")
    else:
        summary["verified"] = True
    return summary


def read_nodeids_selection(path: Path) -> list[str]:
    """Nodeids separados por lineas, sin blancos ni duplicados, en su orden."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise UsageError(f"no se pudo leer --nodeids {path}: {exc}") from exc
    selected: list[str] = []
    seen: set[str] = set()
    for line in lines:
        nodeid = line.strip()
        if nodeid and nodeid not in seen:
            seen.add(nodeid)
            selected.append(nodeid)
    if not selected:
        raise UsageError(f"--nodeids {path} no declara ningun nodeid")
    return selected


def close_selection(capability, nodeids_file) -> dict:
    """Seleccion del intento: capacidad, archivo de nodeids o suite completa."""
    try:
        if capability is not None:
            inventory = read_json(INVENTORY_PATH)
            nodeids = capability_selection(inventory, capability, collect_nodeids())
            return {"kind": "capability", "value": capability, "nodeids": nodeids}
        if nodeids_file is not None:
            path = Path(nodeids_file).expanduser()
            if not path.is_file():
                raise UsageError(f"--nodeids no es un archivo: {path}")
            return {"kind": "nodeids", "value": nodeids_file,
                    "nodeids": read_nodeids_selection(path)}
        nodeids = collect_nodeids()
    except UsageError:
        raise
    except Diagnosis as exc:
        raise UsageError(str(exc)) from exc
    if not nodeids:
        raise UsageError("seleccion requerida vacia: pytest no recolecto nodeids")
    return {"kind": "all", "value": None, "nodeids": nodeids}


def reserve_attempt(evidence_root: Path) -> Path:
    """Un directorio de intento nuevo por invocacion, creado en exclusiva.

    ``mkdir`` sin ``exist_ok`` es la reserva: si el nombre ya existe la reserva
    **falla** con codigo 2 (AJ7). No se reintenta ni se adopta el intento
    ajeno. Los nombres incluyen pid y un componente aleatorio, asi que dos
    invocaciones concurrentes reservan directorios distintos.
    """
    name = (f"attempt-{utc_attempt_stamp()}-"
            f"{os.getpid()}-{secrets.token_hex(4)}")
    attempt = evidence_root / name
    try:
        os.mkdir(attempt)
    except FileExistsError as exc:
        raise UsageError(
            f"colision de nombre de intento bajo {evidence_root}: {name} ya "
            "existe; no se reutiliza ni se adopta un intento ajeno") from exc
    except OSError as exc:
        raise UsageError(
            f"no se pudo reservar un intento bajo {evidence_root}: {exc}") from exc
    return attempt


def git_revision() -> str | None:
    try:
        revision = git("rev-parse", "HEAD", check=False).stdout.strip()
    except OSError:
        return None
    return revision or None


def git_dirty_entries() -> int | None:
    try:
        status = git("status", "--porcelain", check=False)
    except OSError:
        return None
    if status.returncode != 0:
        return None
    return len([line for line in status.stdout.splitlines() if line.strip()])


def pytest_argv_for(attempt: Path, nodeids: list[str]) -> list[str]:
    """Argv efectivo del hijo pytest, determinista antes de lanzarlo.

    Se calcula aqui para que la ruta de interrupcion conserve el mismo argv
    que la corrida normal (017-001 review-T1 H3): el perfil interrumpido debe
    permitir reconstruir que comando se midio.
    """
    return [sys.executable, "-m", "pytest", "-v", "-rs", "-o", "addopts=",
            "-p", "no:cacheprovider",
            "-p", OBSERVER_MODULE,
            f"--junitxml={attempt / 'pytest.xml'}",
            *nodeids]


def run_pytest_to_logs(attempt: Path, nodeids: list[str]
                       ) -> tuple[int, float, list[str]]:
    """Ejecuta la seleccion; la salida se escribe directo en los logs.

    Escribir a los logs (en vez de capturar y volcar al final) conserva la
    salida parcial de un intento interrumpido.

    Es la **unica** corrida pytest del intento (017-001 PC-2): el mismo
    proceso hijo produce el resultado contractual, ``pytest.xml`` (junit) y
    las fases del observador (``-p cdad_suite_observer``). La medicion nunca
    agrega otra ejecucion.

    La salida efectiva del hijo se controla en tres frentes, porque el resumen
    del intento depende de sus lineas por test: ``PYTEST_ADDOPTS`` se elimina
    del entorno (opciones como ``-qq`` las silencian), ``-o addopts=`` anula
    los ``addopts`` declarados en la configuracion del proyecto y ``COLUMNS``
    se fija para que el motivo publicado de un skip no se trunque con el
    ancho del terminal (008-005 D3: el parser no cambia).

    Devuelve ``(rc, pared_monotonica_s, argv_efectivo)``.
    """
    argv = pytest_argv_for(attempt, nodeids)
    env = {key: value for key, value in os.environ.items()
           if key != "PYTEST_ADDOPTS"}
    env["COLUMNS"] = "1000"
    scripts_dir = str(Path(__file__).resolve().parent)
    previous_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (scripts_dir if not previous_pythonpath
                         else scripts_dir + os.pathsep + previous_pythonpath)
    env[OBSERVER_SINK_ENV] = str(attempt / PROFILE_PHASE_SINK)
    started = time.monotonic()
    with (attempt / "stdout.log").open("w", encoding="utf-8") as out, \
            (attempt / "stderr.log").open("w", encoding="utf-8") as err:
        try:
            rc = subprocess.run(argv, stdout=out, stderr=err,
                                stdin=subprocess.DEVNULL, env=env).returncode
        finally:
            wall_s = time.monotonic() - started
    return rc, wall_s, argv


def read_sink_payload(attempt: Path) -> tuple[list, list, str | None]:
    """Carga ``(fases, errores_de_captura, diagnostico)`` del sumidero.

    Los errores de captura que el observador conservo en el volcado fuerzan
    ``incomplete`` en quien los consuma: una captura parcial nunca se presenta
    como medicion valida (017-001 review-T1 H1, INV-6). Un volcado de un
    observador anterior sin la clave equivale a cero errores declarados.
    """
    sink = attempt / PROFILE_PHASE_SINK
    if not sink.is_file():
        return [], [], (f"sin captura de fases: {PROFILE_PHASE_SINK} ausente; "
                        "el hijo pudo no arrancar, morir antes del volcado o "
                        "cargarse sin el observador")
    try:
        payload = json.loads(sink.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [], [], f"{PROFILE_PHASE_SINK} ilegible: {exc}"
    phases = payload.get("phases")
    if not isinstance(phases, list):
        return [], [], f"{PROFILE_PHASE_SINK} sin lista de fases"
    errors = payload.get("capture_errors", [])
    if not isinstance(errors, list):
        errors = [str(errors)]
    else:
        errors = [str(item) for item in errors]
    return phases, errors, None


def read_sink_phases(attempt: Path) -> tuple[list, str | None]:
    """Fases del observador, o ``([], diagnostico)`` si no hay captura."""
    phases, _, issue = read_sink_payload(attempt)
    return phases, issue


def _repo_root() -> Path:
    """Raiz del repositorio que contiene este CLI."""
    return Path(__file__).resolve().parents[1]


def default_operation_scope_path() -> Path:
    """Registro de alcance por defecto: el del repositorio de este CLI."""
    return _repo_root() / OPERATION_SCOPE_PLANNED_PATH


def load_operation_scope(path) -> tuple[str | None, str, dict | None, str | None]:
    """``(sha256, estado, datos, diagnostico)`` del alcance aplicado.

    Un alcance ilegible no rompe la corrida contractual: quien lo consuma
    declara la medicion incompleta con su diagnostico, sin sustituir el rc.
    """
    scope_path = Path(path).expanduser()
    sha = file_sha256(scope_path)
    if sha is None:
        return None, OPERATION_SCOPE_UNREADABLE_STATUS, None, (
            f"alcance de operaciones ilegible o ausente: {scope_path}")
    try:
        data = json.loads(scope_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        return sha, "unreadable", None, (
            f"alcance de operaciones ilegible ({scope_path}): {exc}")
    if not isinstance(data, dict):
        return sha, "unreadable", None, (
            f"alcance de operaciones sin objeto JSON ({scope_path})")
    return sha, str(data.get("status", "unknown")), data, None


def committed_exercised_families(scope: dict, executed: list[str]) -> list[str]:
    """Recorridos comprometidos del alcance cuya seleccion incluye un nodeid
    ejecutado.

    La seleccion aplicable se resuelve a nivel de familia y a nivel de
    operacion: una familia sin seleccion no descarta las selecciones propias
    de sus operaciones (p. ej. ``u3-disposable-product`` sin seleccion con
    ``u3.contract-staging`` declarando ``C-U3``). Solo cuentan selecciones
    explicitas con lista de nodeids: una seleccion agregada sin nodeids (p.
    ej. ``all-required-selections``) nunca declara ejercitado un nodeid
    concreto, y una familia y operacion sin seleccion no comprometen un
    recorrido comprobable. Solo cuentan entradas con estado comprometido, en
    ambos niveles. Asi un recorrido no ejercitado se distingue de un fallo
    de captura (spec §4.4) y las selecciones que no tocan recorridos
    comprometidos conservan su veredicto de fases.
    """
    if not isinstance(scope, dict):
        return []
    selections = scope.get("selections")
    if not isinstance(selections, dict):
        return []
    families = scope.get("families")
    if not isinstance(families, list):
        return []
    executed_set = set(executed)

    def _selection_includes(key) -> bool:
        if not key or not isinstance(key, str):
            return False
        selection = selections.get(key)
        if not isinstance(selection, dict):
            return False
        nodeids = selection.get("nodeids")
        if not isinstance(nodeids, list):
            return False
        return bool(executed_set & set(nodeids))

    exercised: list[str] = []
    for family in families:
        if not isinstance(family, dict):
            continue
        if family.get("state", "comprometida") != "comprometida":
            continue
        family_name = str(family.get("family", family.get("selection", "")))
        if _selection_includes(family.get("selection")):
            exercised.append(family_name)
            continue
        operations = family.get("operations")
        if not isinstance(operations, list):
            continue
        for op in operations:
            if not isinstance(op, dict):
                continue
            if op.get("state", "comprometida") != "comprometida":
                continue
            if _selection_includes(op.get("selection")):
                exercised.append(family_name)
                break
    return exercised


def read_sink_operations(attempt: Path) -> tuple[list, list, str | None]:
    """``(operaciones, errores_de_operacion, diagnostico)`` del sumidero.

    Un volcado de un observador anterior sin la clave equivale a cero
    operaciones declaradas: la regla de diagnostico acotada (§4.4) decide
    entonces segun el alcance aplicado, nunca por la ausencia de la clave.
    """
    sink = attempt / PROFILE_PHASE_SINK
    if not sink.is_file():
        return [], [], (f"sin captura de operaciones: {PROFILE_PHASE_SINK} ausente")
    try:
        payload = json.loads(sink.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [], [], f"{PROFILE_PHASE_SINK} ilegible: {exc}"
    if not isinstance(payload, dict):
        return [], [], f"{PROFILE_PHASE_SINK} sin objeto JSON"
    operations = payload.get("operations", [])
    if not isinstance(operations, list):
        return [], [], f"{PROFILE_PHASE_SINK} sin lista de operaciones"
    errors = payload.get("operation_errors", [])
    if not isinstance(errors, list):
        errors = [str(errors)]
    else:
        errors = [str(item) for item in errors]
    return operations, errors, None


def read_xml_info(attempt: Path) -> tuple[set[str] | None, set[str], str | None]:
    """``(nombres_de_caso, omitidos, diagnostico)`` de ``pytest.xml``.

    Un XML parseable pero sin casos es captura inconsistente, no exito: quien
    lo consuma debe diagnosticar medicion incompleta (017-001 review-T1 H1).
    ``omitidos`` nombra los casos con elemento ``<skipped/>``.
    """
    path = attempt / "pytest.xml"
    if not path.is_file():
        return None, set(), "pytest.xml ausente: el hijo no dejo resultados junit"
    try:
        root = ET.parse(str(path)).getroot()
    except ET.ParseError as exc:
        return None, set(), f"pytest.xml ilegible: {exc}"
    except OSError as exc:
        return None, set(), f"pytest.xml ilegible: {exc}"
    cases = list(root.iter("testcase"))
    if not cases:
        return set(), set(), ("pytest.xml sin casos: no hay resultados con los "
                              "que contrastar la captura de fases")
    names = {str(case.get("name")) for case in cases}
    skipped = {str(case.get("name")) for case in cases
               if case.find("skipped") is not None}
    return names, skipped, None


def read_xml_names(attempt: Path) -> tuple[set[str] | None, str | None]:
    """Nombres de caso de ``pytest.xml``, o ``(None, diagnostico)``."""
    names, _, issue = read_xml_info(attempt)
    return names, issue


def build_profile(attempt: Path, nodeids: list[str], pytest_argv: list,
                  pytest_wall_s: float, operation_scope_path=None) -> dict:
    """Arma ``profile.json`` desde la captura de la unica corrida.

    ``complete`` exige: XML parseable con casos y correspondencia integra con
    la seleccion; captura del observador sin errores declarados; y cobertura
    de fases realmente emitidas por nodeid seleccionado. Lo demas es
    ``incomplete`` con ``diagnosis``: una captura parcial nunca se presenta
    como medicion valida y nunca sustituye el rc contractual (017-001 INV-6,
    review-T1 H1).

    Solo se conservan fases realmente emitidas: una fase no ejecutada queda
    ausente, nunca aparece como fila de duracion cero. La cobertura exigida
    por nodeid no inventa fases: la exencion de ``call`` depende del resultado
    de ``setup``, no del mero estado omitido (review-T1-003): ``setup``
    skipped/failed no ejecutan ``call``; ``setup`` passed si la exige.
    ``setup`` y ``teardown`` se exigen siempre que hubo captura de fases
    (review-T1-002 + matriz T1-003): un skip limpio con sus fases esperables
    emitidas sigue ``complete``; perder una fase emitida y esperable
    (incluida ``call`` de un skip dentro de ``call``) es captura parcial
    (``incomplete``). Una preparacion fallida explica la ausencia de
    ``call`` (pytest no la emite en ese caso); cualquier otra fase faltante
    de un test corrido es perdida de captura.

    Operaciones T2 (spec §4.2, regla acotada §4.4): el perfil conserva los
    intervalos observados y la referencia inequivoca al alcance aplicado
    (ruta, sha256 y estado). Si el alcance aplicado declara un recorrido
    comprometido cuya seleccion incluye un nodeid ejecutado y se capturaron
    cero operaciones, la medicion queda ``incomplete`` con ``diagnosis``. Si
    ningun recorrido ejercitado debia emitir, el veredicto de fases se
    conserva intacto; con marcas capturadas, rigen esas mismas reglas de
    integridad de fases.
    """
    phases, capture_errors, phases_issue = read_sink_payload(attempt)
    operations, op_errors, ops_issue = read_sink_operations(attempt)
    xml_names, xml_skipped, xml_issue = read_xml_info(attempt)
    issues = [issue for issue in (phases_issue, xml_issue) if issue]
    if ops_issue and phases_issue is None:
        issues.append(ops_issue)
    if op_errors:
        issues.append("el observador declaro %d error(es) de operaciones: %s"
                      % (len(op_errors), "; ".join(op_errors[:3])))
    if capture_errors:
        issues.append("el observador declaro %d error(es) de captura: %s"
                      % (len(capture_errors), "; ".join(capture_errors[:3])))
    if not issues and not phases:
        issues.append("sin fases emitidas: nada que atribuir")
    selected = set(nodeids)
    selected_bases = {nodeid.split("::")[-1] for nodeid in selected}
    if xml_names is not None:
        missing_names = sorted(selected_bases - xml_names)
        if missing_names:
            issues.append("nodeids seleccionados sin resultados en pytest.xml: "
                          + ", ".join(missing_names))
        extra_names = sorted(xml_names - selected_bases)
        if extra_names:
            issues.append("pytest.xml nombra casos no seleccionados: "
                          + ", ".join(extra_names))
    by_nodeid: dict[str, list[dict]] = {}
    for row in phases:
        if isinstance(row, dict):
            by_nodeid.setdefault(str(row.get("nodeid")), []).append(row)
    for nodeid in sorted(selected - set(by_nodeid)):
        issues.append(f"nodeid seleccionado sin fases registradas: {nodeid}")
    for nodeid in sorted(selected & set(by_nodeid)):
        rows = by_nodeid[nodeid]
        base = nodeid.split("::")[-1]
        whens = {str(row.get("when")) for row in rows}
        skipped = base in xml_skipped or any(
            row.get("outcome") == "skipped" for row in rows)
        if skipped:
            # review-T1-002 + review-T1-003 (matriz T1-003): un omitido no
            # queda exento de comprobacion. La exencion de `call` depende del
            # resultado de `setup`, no del mero estado omitido: `setup`
            # skipped/failed no ejecutan `call`; `setup` passed si la exige.
            # `setup` y `teardown` se exigen siempre que hubo captura.
            if "setup" not in whens:
                issues.append(
                    f"fase 'setup' ausente para {nodeid}: captura parcial de omitido")
            if "teardown" not in whens:
                issues.append(
                    f"fase 'teardown' ausente para {nodeid}: captura parcial de omitido")
            setup_passed = any(
                str(row.get("when")) == "setup"
                and str(row.get("outcome")) == "passed"
                for row in rows)
            if setup_passed and "call" not in whens:
                issues.append(
                    f"fase 'call' ausente para {nodeid}: captura parcial de "
                    "omitido con setup pasado (call esperable perdida)")
            continue  # exencion de `call` solo cuando setup no paso; resto ya comprobado
        if "setup" not in whens:
            issues.append(f"fase 'setup' ausente para {nodeid}: captura parcial")
            continue
        setup_failed = any(str(row.get("when")) == "setup"
                           and str(row.get("outcome")) == "failed"
                           for row in rows)
        if "call" not in whens and not setup_failed:
            issues.append(f"fase 'call' ausente para {nodeid}: captura parcial; "
                          "el XML muestra el test corrido pero el observador "
                          "perdio su fase")
        if "teardown" not in whens:
            issues.append(f"fase 'teardown' ausente para {nodeid}: captura parcial")
    if issues:
        status, diagnosis = "incomplete", "; ".join(issues)
    else:
        status, diagnosis = "complete", None
    if operation_scope_path is not None:
        scope_path = Path(operation_scope_path).expanduser()
    else:
        scope_path = default_operation_scope_path()
    scope_sha, scope_status, scope_data, scope_issue = load_operation_scope(
        scope_path)
    if scope_issue:
        status, diagnosis = "incomplete", (
            (diagnosis + "; " if diagnosis else "") + scope_issue)
    elif not operations:
        exercised = committed_exercised_families(scope_data, nodeids)
        if exercised:
            diagnosis = ((diagnosis + "; " if diagnosis else "")
                         + "sin operaciones capturadas sobre recorrido(s) "
                           "comprometido(s) ejercitado(s) ("
                         + ", ".join(sorted(exercised))
                         + ") incluidos en la seleccion: la medicion queda "
                           "incomplete hasta recalibrar; un recorrido no "
                           "ejercitado no es un fallo de captura")
            status = "incomplete"
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "status": status,
        "diagnosis": diagnosis,
        "pytest_argv": list(pytest_argv),
        "pytest_wall_s": pytest_wall_s,
        "preparation_measured_s": measured_preparation_s(operations),
        "phases": phases,
        "capture_errors": capture_errors,
        "operations": operations,
        "operation_errors": op_errors,
        "operation_scope": {
            "path": str(scope_path),
            "sha256": scope_sha,
            "status": scope_status,
        },
    }


def write_incomplete_profile(attempt: Path, nodeids: list[str],
                             pytest_argv: list, pytest_wall_s: float | None,
                             diagnosis: str, operation_scope_path=None) -> None:
    """Deja constancia diagnosticada cuando el `close` no termina normal.

    Best-effort: si ni esto se puede escribir, el intento queda sin perfil
    y la medicion sigue sin acreditarse. Nunca inventa fases.
    """
    try:
        phases, capture_errors, _ = read_sink_payload(attempt)
        try:
            operations, op_errors, _ = read_sink_operations(attempt)
        except Exception:
            operations, op_errors = [], []
        if operation_scope_path is not None:
            scope_path = Path(operation_scope_path).expanduser()
        else:
            scope_path = default_operation_scope_path()
        try:
            scope_sha, scope_status, _, _ = load_operation_scope(scope_path)
        except Exception:
            scope_sha, scope_status = None, OPERATION_SCOPE_UNREADABLE_STATUS
        write_json_atomic(attempt / "profile.json", {
            "schema_version": PROFILE_SCHEMA_VERSION,
            "status": "incomplete",
            "diagnosis": diagnosis,
            "pytest_argv": list(pytest_argv),
            "pytest_wall_s": pytest_wall_s,
            "phases": phases,
            "capture_errors": capture_errors,
            "operations": operations,
            "operation_errors": op_errors,
            "operation_scope": {
                "path": str(scope_path),
                "sha256": scope_sha,
                "status": scope_status,
            },
        })
    except OSError:
        pass


def cmd_close(evidence_root: str, capability, nodeids_file,
              operation_scope=None) -> int:
    """Ejecuta y registra un intento de cierre (PC-6, AJ7).

    ``--all`` y la ausencia de seleccion eligen la suite completa: ``--all``
    existe para declararlo explícitamente, no para cambiar la seleccion.
    """
    root = Path(evidence_root).expanduser()
    if not root.is_dir():
        raise UsageError(f"--evidence-root no es un directorio existente: {root}")

    # La seleccion se resuelve antes de reservar: un error de uso no deja un
    # intento a medias.
    selection = close_selection(capability, nodeids_file)

    attempt = reserve_attempt(root)
    record = {
        "schema_version": CLOSE_SCHEMA_VERSION,
        "state": "running",
        "command": [sys.executable, *sys.argv],
        "selection": selection,
        "selection_artifacts": selection_artifact_hashes(),
        "commit": git_revision(),
        "dirty": git_dirty_entries(),
        "started_at": utc_now(),
        "finished_at": None,
        "rc": None,
        "pytest_summary": None,
        "canary": {"scope": canary_scope(), "before": "canary-before.txt",
                   "after": "canary-after.txt", "delta_lines": None},
        "artifacts": {"stdout": "stdout.log", "stderr": "stderr.log",
                      "pytest_xml": "pytest.xml", "profile": "profile.json"},
    }
    attempt_json = attempt / "attempt.json"
    write_json_atomic(attempt_json, record)

    before = canary_snapshot()
    write_canary(attempt / "canary-before.txt", before)
    # El argv se fija antes de lanzar al hijo para que la ruta de
    # interrupcion lo conserve aunque `run_pytest_to_logs` no retorne
    # (017-001 review-T1 H3). `child_start` permite recuperar la pared del
    # hijo tambien en esa ruta.
    child_argv: list = pytest_argv_for(attempt, selection["nodeids"])
    child_wall_s: float | None = None
    child_start = time.monotonic()
    try:
        rc, child_wall_s, child_argv = run_pytest_to_logs(
            attempt, selection["nodeids"])
    except KeyboardInterrupt:
        if child_wall_s is None:
            child_wall_s = time.monotonic() - child_start
        write_incomplete_profile(attempt, selection["nodeids"], child_argv,
                                 child_wall_s,
                                 "close interrumpido durante la corrida pytest: "
                                 "medicion incompleta, no acredita base",
                                 operation_scope)
        record.update(state="interrupted", finished_at=utc_now())
        write_json_atomic(attempt_json, record)
        print(f"cdad-suite: close interrumpido: {attempt}", file=sys.stderr)
        return 130
    except BaseException:
        if child_wall_s is None:
            child_wall_s = time.monotonic() - child_start
        write_incomplete_profile(attempt, selection["nodeids"], child_argv,
                                 child_wall_s,
                                 "close abortado durante la corrida pytest: "
                                 "medicion incompleta, no acredita base",
                                 operation_scope)
        record.update(state="interrupted", finished_at=utc_now())
        write_json_atomic(attempt_json, record)
        raise

    after = canary_snapshot()
    write_canary(attempt / "canary-after.txt", after)
    record["canary"]["delta_lines"] = canary_delta_lines(before, after)
    stdout = (attempt / "stdout.log").read_text(encoding="utf-8", errors="replace")
    summary = parse_pytest_verbose(stdout)
    # La finalizacion contractual (state finished + rc del hijo) se separa
    # del intento de escritura del perfil: un fallo de medicion no sustituye
    # el resultado de pytest ni deja el intento en running (017-001
    # review-T1 H2, spec §4.3, PC-2). El fallo queda diagnosticado en el
    # intento y en stderr, sin Traceback.
    record.update(state="finished", finished_at=utc_now(), rc=rc,
                  pytest_summary=summary)
    try:
        profile = build_profile(attempt, selection["nodeids"], child_argv,
                                child_wall_s, operation_scope)
        write_json_atomic(attempt / "profile.json", profile)
        profile_diagnosis = None
    except Exception as exc:
        profile_diagnosis = (f"no se pudo conservar la medicion "
                             f"(profile.json): {exc}; el rc contractual {rc} "
                             "se conserva y la medicion queda sin acreditar")
        record["profile_diagnosis"] = profile_diagnosis
        leftover = (attempt / "profile.json").with_name(".profile.json.tmp")
        try:
            if leftover.is_file():
                leftover.unlink()
        except OSError:
            pass
    write_json_atomic(attempt_json, record)

    print(f"cdad-suite: intento {attempt} (rc={rc}, "
          f"canary_delta_lines={record['canary']['delta_lines']})", file=sys.stderr)
    if not summary["verified"]:
        print("cdad-suite: aviso: resumen de pytest no verificable en "
              f"{attempt}: {summary['diagnosis']}", file=sys.stderr)
    if record["canary"]["delta_lines"]:
        print("cdad-suite: aviso: el canario detecto cambios en el HOME real "
              f"durante el intento ({attempt})", file=sys.stderr)
    if profile_diagnosis:
        print(f"cdad-suite: aviso: {profile_diagnosis} ({attempt})",
              file=sys.stderr)
    return rc


# ------------------------------------------- parallel (017-001 T6)
#
# Lote paralelo de solo-ejecucion con workers configurables (PC-10, promesa
# E; contrato: performance/parallelism.md). Separa de `close`, que queda
# serial e intacto: no reutiliza su reserva de intento ni su perfil.
#
# - Particion por archivo (nunca por test suelto): conserva el orden interno
#   de cada archivo. Sin `--balance-from`, reparto goloso por cantidad de
#   nodeids; con `--balance-from <profile.json>`, por costo medido cuando el
#   perfil trae fases con duraciones.
# - Cada worker es un proceso pytest hijo con HOME, XDG_* y TMPDIR propios
#   bajo `worker-<i>/`, mas su evidencia (pytest.xml, phases-raw.json del
#   observador, stdout/stderr, profile.json minimo y nodeids.txt).
# - El agregado NO aplica la identidad serial: informa pared por worker y
#   pared total (reloj de pared), trabajo medido por worker rotulado como
#   tal (nunca como pared), solapamiento declarado (no "ahorro"), resultado
#   consolidado y canario antes/despues.

PARALLEL_SCHEMA_VERSION = 1
PARALLEL_DEFAULT_WORKERS = 2


def measured_preparation_s(operations) -> float:
    """Preparacion medida de un perfil: suma de operaciones no compartidas de
    preparacion (fase ``setup`` o marca explicita de preparacion).

    Excluye ``owner_scope == "shared"`` (compartido, no adjudicable a un
    worker), la accion contractual (``call`` no marcada) y la limpieza
    (``teardown``): solo preparacion. Nunca resta paredes: es un subconjunto
    medido del propio perfil, por lo que siempre cabe en su pared.
    """
    total = 0.0
    for operation in operations or []:
        if not isinstance(operation, dict):
            continue
        if operation.get("owner_scope") == "shared":
            continue
        blob = json.dumps(operation, ensure_ascii=False).lower()
        if operation.get("phase") != "setup" and "prepar" not in blob:
            continue
        duration = operation.get("duration_s", operation.get("duration"))
        if isinstance(duration, (int, float)) and not isinstance(duration, bool):
            total += float(duration)
    return total


def reference_preparation_s(profile) -> float | None:
    """Preparacion medida de un perfil de referencia (``--balance-from``).

    Usa el campo explicito cuando existe; si no, la misma regla observable
    del oraculo (operaciones que nombran preparacion). ``None`` si no hay de
    donde sacarla: la ausencia se declara, no se inventa.
    """
    if not isinstance(profile, dict):
        return None
    value = profile.get("preparation_measured_s")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    operations = profile.get("operations")
    if isinstance(operations, list):
        total, seen = 0.0, False
        for operation in operations:
            if not isinstance(operation, dict):
                continue
            if "prepar" not in json.dumps(
                    operation, ensure_ascii=False).lower():
                continue
            duration = operation.get("duration_s", operation.get("duration"))
            if isinstance(duration, (int, float)) and not isinstance(
                    duration, bool):
                total += float(duration)
                seen = True
        if seen:
            return total
    return None


def checkout_canary_roots() -> list[Path]:
    """Raices del canario del checkout: ``build/`` y ``.cdad/`` del repo."""
    root = _repo_root()
    return [root / "build", root / ".cdad"]


def checkout_canary_snapshot(exclude: Path | None = None) -> dict:
    """Huella del checkout: sha256 por archivo sobre rutas ordenadas.

    Detecta cambios persistentes de contenido (incluida la reescritura del
    mismo tamano con mtime restaurado, que conteo+bytes+mtime no ven):
    recorre ``build/`` y ``.cdad/`` (sin seguir enlaces), ordena las rutas
    y encadena ``relativo + sha256(contenido)`` en un sha256 global.
    Ademas conserva conteo de archivos, bytes totales y mtime maximo como
    informacion (no como huella). Requiere Linux solo para el barrido de
    familia; la huella es portable.

    ``exclude`` (la raiz de evidencia cuando vive bajo el checkout) no se
    recorre: el lote no debe ensuciar su propio canario con su evidencia. La
    exclusion es lexica (sin ``resolve()`` por ruta: el recorrido ya es
    estatico y el resolve por entrada domina el costo del barrido).

    Fail-closed (R3): todo error de lectura durante el barrido se registra
    en ``incomplete`` con la ruta afectada y NUNCA se sustituye por un
    contenido estable ni se omite en silencio. Un ``incomplete`` no vacio
    impide declarar la corrida accepted (lo decide el veredicto).
    """
    if exclude is not None:
        # Absoluta barata (sin resolver enlaces): los recorridos de
        # _canary_walk cuelgan de raices absolutas, asi la comparacion
        # lexica cubre raices de evidencia relativas y absolutas.
        exclude_parts = Path(os.path.abspath(exclude)).parts
    else:
        exclude_parts = None
    repo_root = _repo_root()
    files, total_bytes, max_mtime_ns = 0, 0, None
    entries: list[tuple[str, str]] = []
    incomplete: list[str] = []

    def _display(path: Path) -> str:
        try:
            return path.relative_to(repo_root).as_posix()
        except ValueError:
            return path.as_posix()

    def _record_incomplete(path: Path) -> None:
        text = _display(path)
        if text not in incomplete:
            incomplete.append(text)

    cost_start = time.monotonic()
    for root in checkout_canary_roots():
        if not root.is_dir():
            continue
        # Barrido propio con registro de incompletitud (no reutiliza
        # _canary_walk, que omite en silencio lo inaccesible para el
        # canario de configuracion): aqui cada directorio ilegible queda
        # en ``incomplete``.
        stack = [root]
        while stack:
            current = stack.pop()
            if exclude_parts is not None and (
                    current.parts[:len(exclude_parts)] == exclude_parts):
                continue
            try:
                with os.scandir(current) as handle:
                    children = list(handle)
            except OSError:
                _record_incomplete(current)
                continue
            for entry in children:
                path = Path(entry.path)
                if exclude_parts is not None and (
                        path.parts[:len(exclude_parts)] == exclude_parts):
                    continue
                try:
                    stat = path.lstat()
                except OSError:
                    _record_incomplete(path)
                    continue
                try:
                    is_dir = entry.is_dir(follow_symlinks=False)
                except OSError:
                    _record_incomplete(path)
                    continue
                if is_dir:
                    stack.append(path)
                try:
                    is_file = path.is_file(follow_symlinks=False)
                except OSError:
                    _record_incomplete(path)
                    continue
                if is_file:
                    files += 1
                    total_bytes += stat.st_size
                    relative = _display(path)
                    try:
                        digest = file_sha256(path)
                    except OSError:
                        _record_incomplete(path)
                        digest = None
                    if not isinstance(digest, str):
                        # No sustituir por contenido estable: se registra
                        # la ruta en ``incomplete`` y se usa un marcador
                        # que no pretende ser huella de contenido.
                        if relative not in incomplete:
                            incomplete.append(relative)
                        digest = "unreadable-incomplete"
                    entries.append((relative, digest))
                if max_mtime_ns is None or stat.st_mtime_ns > max_mtime_ns:
                    max_mtime_ns = stat.st_mtime_ns
    entries.sort(key=lambda item: item[0])
    hasher = hashlib.sha256()
    for relative, digest in entries:
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\x00")
        hasher.update(digest.encode("utf-8"))
        hasher.update(b"\x00")
    fingerprint = hasher.hexdigest()
    cost_s = time.monotonic() - cost_start
    return {
        "scope": [str(root) for root in checkout_canary_roots()],
        "files": files,
        "total_bytes": total_bytes,
        "max_mtime": (max_mtime_ns / 1e9
                      if max_mtime_ns is not None else None),
        "max_mtime_ns": max_mtime_ns,
        "fingerprint": fingerprint,
        "fingerprint_algo": "sha256-per-file-sorted",
        "fingerprint_cost_s": cost_s,
        "incomplete": sorted(incomplete),
    }


def _ppid_of(pid: str) -> int | None:
    """PPid de /proc/<pid>/status; None si no se puede leer."""
    try:
        with open(f"/proc/{pid}/status", encoding="utf-8",
                  errors="replace") as handle:
            for line in handle:
                if line.startswith("PPid:"):
                    try:
                        return int(line.split()[1])
                    except (IndexError, ValueError):
                        return None
    except OSError:
        return None
    return None


def _is_descendant_of(pid: int, ancestor: int) -> bool:
    """True si la cadena de PPid de pid desciende de ancestor."""
    seen: set[int] = set()
    current = _ppid_of(str(pid))
    while current is not None and current not in seen:
        if current == ancestor:
            return True
        if current <= 1:
            break
        seen.add(current)
        current = _ppid_of(str(current))
    return False


def live_pids_with_marker(marker: str) -> list[int] | None:
    """PIDs vivos descendientes del runner cuya cmdline menciona ``marker``.

    Solo cuenta procesos cuya cadena de PPid desciende del pid propio
    (hijos y nietos incluidos), excluyendo el runner mismo: el invocador,
    la shell padre, ancestros o hermanos nunca son huerfanos del lote
    aunque su linea de comandos mencione la raiz de evidencia.

    ``None`` si /proc no esta disponible: la ausencia de barrido se declara,
    nunca se presenta como cero.
    """
    try:
        entries = os.listdir("/proc")
    except OSError:
        return None
    me = os.getpid()
    needle = marker.encode("utf-8", errors="replace")
    found = []
    for entry in entries:
        if not entry.isdigit() or int(entry) == me:
            continue
        try:
            with open(f"/proc/{entry}/cmdline", "rb") as handle:
                raw = handle.read()
        except OSError:
            continue
        if raw and needle in raw and _is_descendant_of(int(entry), me):
            found.append(int(entry))
    return sorted(found)


def _self_and_ancestor_pids() -> set[int]:
    """PID propio mas cadena de ancestros via /proc/<pid>/status (PPid)."""
    seen: set[int] = {os.getpid()}
    pid = os.getpid()
    for _ in range(128):
        ppid = _ppid_of(str(pid))
        if not ppid or ppid <= 0 or ppid in seen:
            break
        seen.add(ppid)
        if ppid == 1:
            break
        pid = ppid
    return seen


def _pgrp_of(pid: int) -> int | None:
    """pgrp de /proc/<pid>/stat (campo 8 tras el comm); None si ilegible."""
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8",
                  errors="replace") as handle:
            stat = handle.read()
    except OSError:
        return None
    cut = stat.rfind(")")
    if cut < 0:
        return None
    fields = stat[cut + 1:].split()
    if len(fields) < 4:
        return None
    try:
        return int(fields[2])
    except ValueError:
        return None


def live_pids_in_pgrp(pgrp: int) -> list[int] | None:
    """PIDs vivos con pgrp dado, excluyendo invocador y ancestros.

    Barrido por grupo de procesos, sin depender de la linea de comandos:
    un descendiente vivo sin la raiz de evidencia en sus argumentos se
    detecta igual. ``None`` si /proc no esta disponible.
    """
    try:
        entries = os.listdir("/proc")
    except OSError:
        return None
    excluded = _self_and_ancestor_pids()
    found = []
    for entry in entries:
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid in excluded:
            continue
        if _pgrp_of(pid) == pgrp:
            found.append(pid)
    return sorted(found)


def _parallel_reap_pgrp(pgid: int, grace_s: float = 5.0) -> tuple[int | None,
                                                                  int | None]:
    """Limpia la familia viva del grupo ``pgid`` (TERM y luego KILL).

    Devuelve (encontrados, restantes): conteos del barrido por pgid antes
    y despues de la limpieza; (None, None) si /proc no esta disponible.
    Nunca toca el grupo propio del runner.
    """
    try:
        own_pgid = os.getpgid(os.getpid())
    except OSError:
        own_pgid = None
    if own_pgid is not None and pgid == own_pgid:
        return 0, 0
    live_before = live_pids_in_pgrp(pgid)
    if live_before is None:
        return None, None
    if not live_before:
        return 0, 0
    for sig, wait_s in ((signal.SIGTERM, grace_s), (signal.SIGKILL, 3.0)):
        try:
            os.killpg(pgid, sig)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        deadline = time.monotonic() + wait_s
        while time.monotonic() < deadline:
            remaining = live_pids_in_pgrp(pgid)
            if remaining is None:
                return len(live_before), None
            if not remaining:
                break
            time.sleep(0.05)
        remaining = live_pids_in_pgrp(pgid)
        if remaining is None:
            return len(live_before), None
        if not remaining:
            break
    remaining = live_pids_in_pgrp(pgid)
    if remaining is None:
        return len(live_before), None
    return len(live_before), len(remaining)


def _parallel_reap(children, grace_s: float = 10.0) -> None:
    """Termina y espera los hijos ya lanzados (ruta de error): no deja vivos."""
    for child in children:
        try:
            if child["proc"].poll() is None:
                child["proc"].terminate()
        except OSError:
            pass
    deadline = time.monotonic() + grace_s
    for child in children:
        try:
            child["proc"].wait(timeout=max(0.0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            try:
                child["proc"].kill()
            except OSError:
                pass
            try:
                child["proc"].wait(timeout=10.0)
            except (OSError, subprocess.TimeoutExpired):
                pass
        for stream in (child.get("out"), child.get("err")):
            if stream is not None:
                try:
                    stream.close()
                except OSError:
                    pass
        child["out"] = None
        child["err"] = None


def _ensure_child_subreaper() -> bool | None:
    """Vuelve al runner subreaper (Linux, prctl PR_SET_CHILD_SUBREAPER).

    Debe llamarse antes de lanzar los workers: todo descendiente huerfano
    (incluido el que hizo setsid y quedo reparentado) vuelve a colgar del
    runner y el barrido por cadena de PPid lo encuentra. Via ctypes, sin
    dependencias nuevas. Devuelve True si quedo activo, False si fallo y
    None fuera de Linux. Requiere Linux para la garantia de familia.
    """
    if not sys.platform.startswith("linux"):
        return None
    try:
        import ctypes
    except Exception:
        return False
    PR_SET_CHILD_SUBREAPER = 36
    for name in ("libc.so.6", None):
        try:
            libc = (ctypes.CDLL(name, use_errno=True)
                    if name else ctypes.CDLL(None, use_errno=True))
            ret = libc.prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0)
            if ret == 0:
                return True
        except Exception:
            continue
    return False


def _live_descendant_pids() -> list[int] | None:
    """PIDs vivos cuya cadena de PPid desciende del runner (cualquier pgid).

    Cubre reparentados tras setsid cuando el runner es subreaper: el
    huerfano vuelve a colgar del runner aunque haya abandonado grupo y
    sesion. Excluye al runner mismo; invocador, ancestros y hermanos nunca
    descienden de el. ``None`` si /proc no esta disponible.
    """
    try:
        entries = os.listdir("/proc")
    except OSError:
        return None
    me = os.getpid()
    found = []
    for entry in entries:
        if not entry.isdigit() or int(entry) == me:
            continue
        try:
            pid = int(entry)
        except ValueError:
            continue
        if _is_descendant_of(pid, me):
            found.append(pid)
    return sorted(found)


def _reap_zombies() -> None:
    """Cosecha hijos zombies reparentados (subreaper) sin bloquear.

    Tras matar huerfanos que colgaban del runner, sus entradas siguen en
    /proc como zombies hasta que el runner las espera: sin esta cosecha el
    barrido los contaria como familia viva restante.
    """
    try:
        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                break
            except OSError:
                break
            if pid == 0:
                break
    except Exception:
        pass


def _parallel_reap_descendants(grace_s: float = 5.0) -> tuple[int | None,
                                                              int | None]:
    """Limpia descendientes vivos del runner (TERM y luego KILL, con espera).

    Barrido por cadena de PPid hasta el runner, no por grupo: encuentra
    tambien a los que abandonaron grupo y sesion. Devuelve (encontrados,
    restantes); (None, None) si /proc no esta disponible.
    """
    live_before = _live_descendant_pids()
    if live_before is None:
        return None, None
    if not live_before:
        return 0, 0
    targets = list(live_before)
    for sig, wait_s in ((signal.SIGTERM, grace_s), (signal.SIGKILL, 3.0)):
        for pid in list(targets):
            try:
                os.kill(pid, sig)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        _reap_zombies()
        deadline = time.monotonic() + wait_s
        while time.monotonic() < deadline:
            _reap_zombies()
            live = _live_descendant_pids()
            if live is None:
                return len(live_before), None
            still = [pid for pid in targets if pid in live]
            if not still:
                break
            time.sleep(0.05)
        _reap_zombies()
        live = _live_descendant_pids()
        if live is None:
            return len(live_before), None
        targets = [pid for pid in targets if pid in live]
        if not targets:
            break
    _reap_zombies()
    live = _live_descendant_pids()
    if live is None:
        return len(live_before), None
    remaining = len([pid for pid in targets if pid in live])
    return len(live_before), remaining


# Ventana de gracia T6 (hijo transitorio): tras esperar a los hijos
# directos se barre la familia una vez (union pgid + cadena de PPid, con
# detalle acotado) y se espera sin matar a nadie hasta GRACE_WINDOW_S
# sondeando cada GRACE_POLL_S. Si la familia queda vacia dentro de la
# gracia, la corrida puede aceptarse (orphans == 0, orphans_found >= 1).
# Si sigue viva al terminar la gracia es fuga real: se mata (TERM, KILL)
# y se descarta. No cambia paredes, particion, preparacion, huella ni
# close: solo el veredicto de familia.
PARALLEL_GRACE_WINDOW_S = 5.0
PARALLEL_GRACE_POLL_S = 0.2
PARALLEL_FAMILY_DETAIL_MAX = 20
PARALLEL_FAMILY_CMDLINE_TRUNC = 200


def _parallel_proc_detail(pid: int) -> dict:
    """Detalle acotado de un pid de la familia: pid, ppid, pgid, cmdline."""
    try:
        ppid = _ppid_of(str(pid))
    except Exception:
        ppid = None
    try:
        pgid = _pgrp_of(pid)
    except Exception:
        pgid = None
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as handle:
            raw = handle.read()
        cmdline = raw.decode("utf-8", errors="replace").replace("\x00",
                                                                 " ").strip()
    except OSError:
        cmdline = ""
    if len(cmdline) > PARALLEL_FAMILY_CMDLINE_TRUNC:
        cmdline = cmdline[:PARALLEL_FAMILY_CMDLINE_TRUNC]
    return {"pid": pid, "ppid": ppid, "pgid": pgid, "cmdline": cmdline}


def _parallel_family_snapshot(pgids: list[int]) -> list[dict] | None:
    """Union acotada de la familia viva: pgids dados + descendientes.

    Excluye al runner, su invocador y ancestros. Devuelve lista de
    detalles ordenada por pid (acotada a DETAIL_MAX); ``None`` si /proc
    no esta disponible. No mata a nadie.
    """
    try:
        os.listdir("/proc")
    except OSError:
        return None
    excluded = _self_and_ancestor_pids()
    me = os.getpid()
    excluded.add(me)
    pids: set[int] = set()
    for pgid in pgids or []:
        if not isinstance(pgid, int) or pgid <= 0:
            continue
        try:
            own_pgid = os.getpgid(me)
        except OSError:
            own_pgid = None
        if own_pgid is not None and pgid == own_pgid:
            continue
        live = live_pids_in_pgrp(pgid)
        if live is None:
            return None
        for pid in live:
            if pid not in excluded:
                pids.add(pid)
    desc = _live_descendant_pids()
    if desc is None:
        return None
    for pid in desc:
        if pid not in excluded:
            pids.add(pid)
    detail = [_parallel_proc_detail(pid) for pid in sorted(pids)]
    return detail[:PARALLEL_FAMILY_DETAIL_MAX]


def _parallel_grace_wait(pgids: list[int]) -> list[dict] | None:
    """Espera la ventana de gracia sin matar: devuelve la familia viva final.

    Primer barrido ya hecho por quien llama (found); aqui solo se sondea
    hasta que la familia quede vacia o se agote GRACE_WINDOW_S. Cosecha
    zombies reparentados para no contarlos como vivos. ``None`` si /proc
    no esta disponible.
    """
    try:
        deadline = time.monotonic() + PARALLEL_GRACE_WINDOW_S
    except Exception:
        return _parallel_family_snapshot(pgids)
    while True:
        _reap_zombies()
        snapshot = _parallel_family_snapshot(pgids)
        if snapshot is None:
            return None
        if not snapshot:
            return snapshot
        if time.monotonic() >= deadline:
            return snapshot
        time.sleep(PARALLEL_GRACE_POLL_S)


def parallel_max_workers() -> tuple[int, int]:
    """(nproc observado, maximo de workers): nunca todos los nucleos."""
    nproc = os.cpu_count() or 8
    return nproc, max(1, nproc - 1)


def parallel_check_workers(workers: int) -> tuple[int, int]:
    """Valida 1 <= N <= nproc-1; el rechazo es error de uso (salida 2)."""
    nproc, maximum = parallel_max_workers()
    if not isinstance(workers, int) or not 1 <= workers <= maximum:
        raise UsageError(
            f"--workers {workers!r} fuera de rango: se requieren workers "
            f"con 1 <= N <= {maximum} (nproc={nproc}); nunca todos los "
            "nucleos sin opcion explicita")
    return nproc, maximum


def _parallel_phase_costs(balance_from) -> dict[str, float]:
    """Costo medido por nodeid desde un profile.json (fases con duracion).

    Best-effort: lo ilegible o ausente deja costo desconocido (vacio), y el
    reparto cae al conteo de nodeids. Nunca inventa duraciones.
    """
    if balance_from is None:
        return {}
    try:
        profile = json.loads(Path(balance_from).expanduser().read_text(
            encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return {}
    phases = profile.get("phases") if isinstance(profile, dict) else None
    if not isinstance(phases, list):
        return {}
    costs: dict[str, float] = {}
    for row in phases:
        if not isinstance(row, dict):
            continue
        nodeid, duration = row.get("nodeid"), row.get("duration_s")
        if (isinstance(nodeid, str) and isinstance(duration, (int, float))
                and not isinstance(duration, bool)):
            costs[nodeid] = costs.get(nodeid, 0.0) + float(duration)
    return costs


def parallel_partition(nodeids: list[str], workers: int,
                       balance_from=None) -> list[list[str]]:
    """Reparte nodeids por archivo entre workers, sin repetir ni separar.

    Agrupa por archivo en orden de primera aparicion y asigna cada archivo
    completo al worker menos cargado (costo medido si hay balance, si no
    cantidad de nodeids; archivos mas caros primero para equilibrar).
    Determinista: mismo orden de entrada, mismo reparto.
    """
    by_file: dict[str, list[str]] = {}
    for nodeid in nodeids:
        by_file.setdefault(nodeid.split("::")[0], []).append(nodeid)
    costs = _parallel_phase_costs(balance_from)
    files = sorted(by_file, key=lambda name: (
        -sum(costs.get(nodeid, 1.0) for nodeid in by_file[name]), name))
    loads = [0.0] * workers
    assigned: list[list[str]] = [[] for _ in range(workers)]
    for name in files:
        index = min(range(workers), key=lambda i: (loads[i], i))
        assigned[index].append(name)
        loads[index] += sum(costs.get(nodeid, 1.0)
                            for nodeid in by_file[name])
    return [[nodeid for name in group for nodeid in by_file[name]]
            for group in assigned]


def _parallel_junit_work(xml_path: Path) -> float | None:
    """Trabajo medido del worker: suma de duraciones de tests del XML.

    Es trabajo (suma de tiempos de caso), nunca pared: no incluye arranque,
    coleccion ni solapamiento entre workers.
    """
    try:
        root = ET.parse(xml_path).getroot()
    except (OSError, ET.ParseError):
        return None
    total, seen = 0.0, False
    for case in root.iter("testcase"):
        try:
            total += float(case.get("time", 0.0))
        except (TypeError, ValueError):
            continue
        seen = True
    return total if seen else None


def _parallel_worker_env(worker_dir: Path) -> tuple[dict, dict[str, str]]:
    """Entorno aislado del hijo: HOME/XDG/TMP propios bajo el worker."""
    home = worker_dir / "home"
    xdg = worker_dir / "xdg"
    tmp = worker_dir / "tmp"
    for path in (home, xdg / "config", xdg / "data", xdg / "cache", tmp):
        path.mkdir(parents=True, exist_ok=True)
    roots = {
        "home": str(home.resolve()),
        "xdg_config_home": str((xdg / "config").resolve()),
        "xdg_data_home": str((xdg / "data").resolve()),
        "xdg_cache_home": str((xdg / "cache").resolve()),
        "tmpdir": str(tmp.resolve()),
    }
    env = {key: value for key, value in os.environ.items()
           if key != "PYTEST_ADDOPTS"}
    env["COLUMNS"] = "1000"
    env["HOME"] = roots["home"]
    env["XDG_CONFIG_HOME"] = roots["xdg_config_home"]
    env["XDG_DATA_HOME"] = roots["xdg_data_home"]
    env["XDG_CACHE_HOME"] = roots["xdg_cache_home"]
    env["TMPDIR"] = roots["tmpdir"]
    scripts_dir = str(Path(__file__).resolve().parent)
    previous = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (scripts_dir if not previous
                         else scripts_dir + os.pathsep + previous)
    env[OBSERVER_SINK_ENV] = str(worker_dir / PROFILE_PHASE_SINK)
    return env, roots


def _parallel_worker_argv(worker_dir: Path, nodeids: list[str]) -> list[str]:
    """Mismo argv efectivo que el cierre serial, sobre la evidencia propia."""
    return [sys.executable, "-m", "pytest", "-v", "-rs", "-o", "addopts=",
            "-p", "no:cacheprovider",
            "-p", OBSERVER_MODULE,
            f"--junitxml={worker_dir / 'pytest.xml'}",
            *nodeids]


def _parallel_markdown(summary: dict) -> str:
    """Agregado legible: pared por worker y total, trabajo como trabajo."""
    lines = ["# Paralelo (017-001 T6, PC-10)", "",
             f"workers: {summary['workers_requested']} pedidos, "
             f"{summary['workers_launched']} lanzados "
             f"({summary['skipped_empty_workers']} omitidos por vacios) "
             f"(nproc={summary['nproc']}, maximo={summary['max_workers']})",
             f"seleccion: {len(summary['nodeids'])} nodeids en "
             f"{summary['file_count']} archivos (particion por archivo)",
             f"pared total (wall, ventana de ejecucion concurrente de los "
             f"hijos): {summary['total_wall_s']:.3f} s",
             f"pared completa del comando (incluye canarios y agregado): "
             f"{summary.get('command_wall_s', summary['total_wall_s']):.3f} s",
             ""]
    for entry in summary["workers"]:
        result = entry["result"]
        lines.append(
            f"## worker-{entry['index']}: pared (wall) "
            f"{entry['wall_s']:.3f} s; trabajo medido (work) "
            f"{entry['work_measured_s']:.3f} s; "
            f"passed={result['passed']} failed={result['failed']} "
            f"skipped={result['skipped']} rc={entry['rc']}")
        lines.append(f"- nodeids: {len(entry['nodeids'])}; "
                     f"evidencia: {entry['evidence']}")
        lines.append(f"- inicio: {entry.get('started_at')}; "
                     f"fin: {entry.get('finished_at')}; "
                     f"pgid: {entry.get('pgid')}; "
                     f"familia encontrada/limpiada/restante: "
                     f"{entry.get('orphans_found')}/"
                     f"{entry.get('orphans_cleaned')}/"
                     f"{entry.get('orphans_remaining')}; "
                     f"preparacion medida: "
                     f"{entry.get('preparation_measured_s', 0.0):.3f} s")
        lines.append("")
    lines.append(f"trabajo medido total (work, suma de duraciones de tests; "
                 f"no es pared): {summary['total_work_s']:.3f} s")
    lines.append(f"solapamiento (overlap) = suma de pared de workers menos "
                 f"pared total, declarado (no es ahorro): "
                 f"{summary['overlap_s']:.3f} s")
    lines.append(f"preparacion medida total "
                 f"(suma de preparation_measured_s por worker, desde sus "
                 f"perfiles; fuente: {summary.get('preparation_source')}): "
                 f"{summary.get('total_preparation_s', 0.0):.3f} s")
    if summary.get("duplicated_preparation_s") is not None:
        lines.append(f"preparacion duplicada (suma de workers menos "
                     f"referencia): "
                     f"{summary['duplicated_preparation_s']:.3f} s")
    else:
        lines.append(f"preparacion duplicada: no calculada "
                     f"({summary.get('duplicated_preparation_note')})")
    checkout = summary.get("checkout_canary") or {}
    lines.append(f"canario del checkout (build/ + .cdad/: "
                 f"{checkout.get('files')} archivos, "
                 f"{checkout.get('total_bytes')} bytes): "
                 f"{'limpio' if checkout.get('unchanged') else 'SUCIO'}")
    lines.append(f"huella del checkout: "
                 f"{checkout.get('fingerprint_algo', 'sha256-per-file-sorted')} "
                 f"{str(checkout.get('fingerprint'))[:16]}… "
                 f"(costo {checkout.get('fingerprint_cost_s', 0.0):.3f} s)")
    lines.append(f"subreaper: {summary.get('subreaper')} "
                 f"(la garantia de familia requiere Linux)")
    consolidated = summary["consolidated"]
    lines.append(f"resultado consolidado: passed={consolidated['passed']} "
                 f"failed={consolidated['failed']} "
                 f"skipped={consolidated['skipped']}")
    lines.append(f"canario: delta {summary['canary']['delta_lines']} lineas "
                 f"({'limpio' if summary['canary']['delta_lines'] == 0 else 'SUCIO'})")
    orphans = summary.get("orphans")
    lines.append(f"hijos terminados: "
                 f"{'si' if summary['children_terminated'] else 'NO'} "
                 f"({summary['child_count']} procesos esperados, "
                 f"huerfanos={orphans}, "
                 f"descendientes comprobados: "
                 f"{'si' if summary.get('orphans_checked') else 'NO'})")
    lines.append(f"pared paralela {summary['total_wall_s']:.3f} s; comparese "
                 f"con la pared serial (close) de los mismos nodeids en la "
                 f"misma revision; la suma de tiempos concurrentes nunca se "
                 f"presenta como pared.")
    lines.append(f"veredicto: {summary.get('verdict')} "
                 f"(huerfanos encontrados/limpiados/restantes: "
                 f"{summary.get('orphans_found')}/"
                 f"{summary.get('orphans_cleaned')}/"
                 f"{summary.get('orphans_remaining')})")
    lines.append("")
    return "\n".join(lines)


def cmd_parallel(evidence_root: str, capability, nodeids_file, all_flag,
                 workers: int | None, balance_from) -> int:
    """Lote paralelo con workers configurables (017-001 T6, PC-10)."""
    if workers is None:
        workers = PARALLEL_DEFAULT_WORKERS
    nproc, maximum = parallel_check_workers(workers)
    root = Path(evidence_root).expanduser()
    if not root.is_dir():
        raise UsageError(f"--evidence-root no es un directorio existente: {root}")
    # R4: el directorio de evidencia debe estar limpio para esta
    # invocacion. Si ya contiene artefactos de un intento anterior
    # (parallel.json, parallel.md, canarios o worker-*/...), se rechaza
    # el destino ocupado con motivo por stderr y NUNCA se reutilizan
    # XML, perfiles ni fases del intento anterior.
    _occupied = [p for p in (root / "parallel.json", root / "parallel.md",
                             root / "canary-before.txt",
                             root / "canary-after.txt") if p.exists()]
    _occupied_workers = sorted(root.glob("worker-*"))
    if _occupied or _occupied_workers:
        found = [p.name for p in _occupied] + [p.name for p in
                                               _occupied_workers]
        raise UsageError(
            f"--evidence-root {root} ocupado (occupied) con evidencia "
            f"previa {found}: rechaza destino ocupado; usa un directorio "
            "de evidencia limpio para este intento (workers "
            "worker-*/..., previous attempt intacto, sin reuso)")

    # R1 (costura de inyeccion de fallo solo para pruebas): CDAD_SUITE_FAULT
    # con "no-subreaper" o "no-sweep" simula la garantia de familia no
    # acreditable. Documentada solo para tests; sin efecto cuando no se
    # define (corridas normales no definen la variable).
    fault = os.environ.get("CDAD_SUITE_FAULT")
    if fault not in (None, "", "no-subreaper", "no-sweep"):
        fault = None
    if not fault:
        fault = None

    # La seleccion se resuelve antes de lanzar hijos: un error de uso no
    # deja evidencia a medias. `--all` declara lo explicito, como en close.
    selection = close_selection(capability, nodeids_file)
    nodeids = list(selection["nodeids"])
    if not nodeids:
        raise UsageError("seleccion requerida vacia: pytest no recolecto nodeids")
    groups = parallel_partition(nodeids, workers, balance_from)
    # M1: los grupos vacios no lanzan pytest (un pytest sin nodeids
    # correria su seleccion predeterminada, fuera de lo pedido). Solo los
    # workers con archivos quedan en el agregado; el resto se declara.
    launched_groups = [(index, assigned) for index, assigned in
                       enumerate(groups) if assigned]
    skipped_empty = workers - len(launched_groups)

    command_start = time.monotonic()
    before = canary_snapshot()
    write_canary(root / "canary-before.txt", before)
    checkout_before = checkout_canary_snapshot(exclude=root)

    # O1 (review-T6-003 bloqueante 1): el runner se vuelve subreaper antes
    # de lanzar los workers (Linux, prctl via ctypes): todo descendiente
    # huerfano, incluido el que hizo setsid, vuelve a colgar del runner.
    subreaper = _ensure_child_subreaper()
    if fault == "no-subreaper":
        # Inyeccion de fallo solo para pruebas: finge que prctl fallo.
        subreaper = False
    # La pared total es la ventana de ejecucion concurrente (primer
    # lanzamiento -> ultima finalizacion efectiva), coherente con los
    # started_at/finished_at por worker: M2 exige total - max <= 1.0 s y los
    # barridos de canario (segundos en este arbol) quedan fuera de la
    # ventana. La pared completa del comando se informa aparte.
    total_start = time.monotonic()
    children = []
    try:
        for index, assigned in launched_groups:
            worker_dir = root / f"worker-{index}"
            try:
                worker_dir.mkdir(parents=True, exist_ok=False)
                (worker_dir / "nodeids.txt").write_text(
                    "".join(f"{nodeid}\n" for nodeid in assigned),
                    encoding="utf-8")
                env, _roots = _parallel_worker_env(worker_dir)
                argv = _parallel_worker_argv(worker_dir, assigned)
                started_mono = time.monotonic()
                started_at = utc_now_fine()
                out = (worker_dir / "stdout.log").open("w", encoding="utf-8")
                err = (worker_dir / "stderr.log").open("w", encoding="utf-8")
                try:
                    # N1 (review-T6-002 bloqueante 1): cada worker corre en
                    # su propio grupo de procesos para poder comprobar y
                    # limpiar su familia real sin depender de la linea de
                    # comandos de sus descendientes.
                    proc = subprocess.Popen(argv, stdout=out, stderr=err,
                                            stdin=subprocess.DEVNULL, env=env,
                                            start_new_session=True)
                    try:
                        pgid = os.getpgid(proc.pid)
                    except OSError:
                        # Con start_new_session el hijo es lider de sesion:
                        # su pgid es su propio pid.
                        pgid = proc.pid
                except OSError:
                    out.close()
                    err.close()
                    raise
            except OSError as exc:
                raise Diagnosis(
                    f"no se pudo preparar o lanzar worker-{index} bajo "
                    f"{root}: {exc}") from exc
            children.append({"index": index, "dir": worker_dir, "proc": proc,
                             "out": out, "err": err, "argv": argv,
                             "nodeids": assigned, "started": started_mono,
                             "started_at": started_at, "roots": _roots,
                             "pgid": pgid})
    except (Diagnosis, UsageError):
        # M3 + N1 + O1 + gracia T6: un fallo parcial no deja familia viva:
        # termina y espera los hijos directos, hace un primer barrido de la
        # familia, espera la ventana de gracia sin matar (el transitorio
        # muere solo) y solo si sigue viva limpia por grupo y por cadena de
        # PPid (reparentados tras setsid), antes de informar por stderr.
        _parallel_reap(children)
        _partial_pgids = [child.get("pgid") for child in children
                          if isinstance(child.get("pgid"), int)
                          and child.get("pgid") > 0]
        _partial_first = _parallel_family_snapshot(_partial_pgids)
        if _partial_first:
            _parallel_grace_wait(_partial_pgids)
        for child in children:
            pgid = child.get("pgid")
            if isinstance(pgid, int) and pgid > 0:
                _parallel_reap_pgrp(pgid)
        _parallel_reap_descendants()
        raise

    # M2: el instante real de finalizacion de cada hijo se toma al observar
    # su terminacion (poll por proceso), no al volver de un wait() en orden:
    # si un worker posterior termina antes, su pared no incluye la espera
    # del anterior.
    pending = {child["index"]: child for child in children}
    finished: dict[int, tuple[float, str]] = {}
    while pending:
        for key in list(pending):
            child = pending[key]
            if child["proc"].poll() is not None:
                finished[key] = (time.monotonic(), utc_now_fine())
                del pending[key]
        if pending:
            time.sleep(0.005)
    total_wall = time.monotonic() - total_start

    entries = []
    first_rc = 0
    for child in children:
        rc = child["proc"].wait()
        end_mono, finished_at = finished.get(
            child["index"], (time.monotonic(), utc_now_fine()))
        wall_s = end_mono - child["started"]
        child["out"].close()
        child["err"].close()
        child["out"] = None
        child["err"] = None
        if first_rc == 0 and rc != 0:
            first_rc = rc
        worker_dir = child["dir"]
        try:
            stdout_text = (worker_dir / "stdout.log").read_text(
                encoding="utf-8", errors="replace")
        except OSError:
            stdout_text = ""
        result = parse_pytest_verbose(stdout_text)
        work = _parallel_junit_work(worker_dir / "pytest.xml")
        work_note = None
        if work is None:
            work, work_note = 0.0, ("sin pytest.xml utilizable: trabajo "
                                    "no medido, se informa 0.0 sin "
                                    "presentarlo como pared")
        # M5: el perfil del worker trae sus operaciones y su preparacion
        # medida desde SU profile.json (nunca por resta de paredes).
        profile = build_profile(worker_dir, child["nodeids"], child["argv"],
                                wall_s)
        preparation = profile.get("preparation_measured_s")
        if not isinstance(preparation, (int, float)) or isinstance(
                preparation, bool):
            operations, _, _ = read_sink_operations(worker_dir)
            preparation = measured_preparation_s(operations)
        profile.update({
            "worker": child["index"],
            "rc": rc,
            "nodeids": child["nodeids"],
            "preparation_measured_s": float(preparation),
            "result": {"passed": result["passed"], "failed": result["failed"],
                       "skipped": result["skipped"],
                       "verified": result["verified"]},
            "work_note": work_note,
            **child["roots"],
        })
        write_json_atomic(worker_dir / "profile.json", profile)
        entries.append({
            "index": child["index"],
            "evidence": worker_dir.name,
            "nodeids": child["nodeids"],
            "pgid": child.get("pgid"),
            "wall_s": wall_s,
            "started_at": child["started_at"],
            "finished_at": finished_at,
            "work_measured_s": work,
            "preparation_measured_s": float(preparation),
            "rc": rc,
            "result": {"passed": result["passed"], "failed": result["failed"],
                       "skipped": result["skipped"]},
            "pytest_argv": child["argv"],
            **child["roots"],
        })

    overlap = sum(entry["wall_s"] for entry in entries) - total_wall
    # N1 (review-T6-002 bloqueante 1) + O1 (review-T6-003 bloqueante 1)
    # + gracia T6: tras esperar al hijo directo, primer barrido de la
    # familia (union pgid + cadena de PPid hasta el runner, con subreaper
    # cubriendo a los que abandonaron grupo y sesion tras setsid) con
    # detalle acotado; luego ventana de gracia sin matar (el transitorio
    # muere solo) y segundo barrido. Si la familia quedo vacia en la
    # gracia se acepta (orphans == 0, orphans_found >= 1 informados). Si
    # sigue viva es fuga real: se mata (TERM y luego KILL), se informa
    # orphans (vivos al final de la gracia), cleaned y remaining, y se
    # descarta. El conteo es el medido, nunca un 0 fijo.
    # R2: los canarios (config y checkout) se toman DESPUES de resolver
    # la familia (barrido, ventana de gracia y limpieza), de modo que una
    # escritura residual posterior a pytest quede dentro de la foto.
    orphans_note: str | None = None
    orphans_available = True
    if fault == "no-sweep":
        # Inyeccion de fallo solo para pruebas: finge barrido no disponible.
        orphans_available = False
    total_found, total_cleaned, total_remaining = 0, 0, 0
    family_detail: list[dict] = []
    family_pids: list[int] = []
    pgids: list[int] = []
    for child in children:
        pgid = child.get("pgid")
        if isinstance(pgid, int) and pgid > 0:
            pgids.append(pgid)
        else:
            orphans_available = False
    first_snapshot = (_parallel_family_snapshot(pgids)
                      if orphans_available else None)
    if first_snapshot is None:
        orphans_available = False
        first_found = None
    else:
        first_found = len(first_snapshot)
        family_detail = list(first_snapshot)
        family_pids = [row.get("pid") for row in family_detail
                       if isinstance(row.get("pid"), int)]
        total_found = first_found
    for entry, child in zip(entries, children):
        pgid = child.get("pgid")
        if not isinstance(pgid, int) or pgid <= 0:
            entry["orphans_found"] = None
            entry["orphans_cleaned"] = None
            entry["orphans_remaining"] = None
            continue
        first_live = live_pids_in_pgrp(pgid)
        if first_live is None:
            orphans_available = False
            entry["orphans_found"] = None
            entry["orphans_cleaned"] = None
            entry["orphans_remaining"] = None
            continue
        entry["orphans_found"] = len(first_live)
        entry["orphans_cleaned"] = 0
        entry["orphans_remaining"] = 0
    if orphans_available and first_found:
        final_snapshot = _parallel_grace_wait(pgids)
        if final_snapshot is None:
            orphans_available = False
            orphans_after_grace = None
        else:
            orphans_after_grace = len(final_snapshot)
    elif orphans_available:
        orphans_after_grace = 0
    else:
        orphans_after_grace = None
    if orphans_available and orphans_after_grace:
        # Fuga real: matar (TERM y luego KILL) y medir lo limpiado.
        for entry, child in zip(entries, children):
            pgid = child.get("pgid")
            if not isinstance(pgid, int) or pgid <= 0:
                continue
            found2, remaining2 = _parallel_reap_pgrp(pgid)
            if found2 is None:
                orphans_available = False
                entry["orphans_cleaned"] = None
                entry["orphans_remaining"] = None
                continue
            entry["orphans_cleaned"] = found2 - (remaining2 or 0)
            entry["orphans_remaining"] = remaining2
        _desc_kill = _parallel_reap_descendants()
        if _desc_kill[0] is None:
            orphans_available = False
        _reap_zombies()
        after_kill = _parallel_family_snapshot(pgids)
        if after_kill is None:
            orphans_available = False
            total_remaining = sum(
                (entry.get("orphans_remaining") or 0)
                for entry in entries
                if isinstance(entry.get("orphans_remaining"), int))
            total_cleaned = (orphans_after_grace or 0) - total_remaining
        else:
            total_remaining = len(after_kill)
            total_cleaned = (orphans_after_grace or 0) - total_remaining
    elif orphans_available:
        total_cleaned, total_remaining = 0, 0
    try:
        os.listdir("/proc")
    except OSError:
        orphans_available = False
    orphans_checked = orphans_available
    if orphans_available:
        orphans: int | None = orphans_after_grace
    else:
        orphans = None
    if not orphans_available:
        if fault == "no-sweep":
            orphans_note = ("barrido de descendientes no disponible (sweep "
                            "fault CDAD_SUITE_FAULT=no-sweep, solo pruebas): "
                            "sin /proc no hay garantia de familia; "
                            "family/familia unverifiable")
        else:
            orphans_note = ("/proc no disponible: sin barrido de descendientes "
                            "(sweep); la garantia de familia no esta "
                            "acreditada")
    elif subreaper is False:
        if fault == "no-subreaper":
            orphans_note = ("subreaper no activo (fault "
                            "CDAD_SUITE_FAULT=no-subreaper, solo pruebas): el "
                            "barrido por cadena de PPid puede no ver "
                            "reparentados; garantia de familia no acreditada")
        else:
            orphans_note = ("subreaper no activo (prctl fallo): el barrido por "
                            "cadena de PPid puede no ver reparentados; requiere "
                            "Linux")
    elif subreaper is None:
        orphans_note = ("sin subreaper fuera de Linux: la garantia de "
                        "familia requiere Linux")
    # R2: canarios DESPUES de resolver la familia (barrido, ventana de
    # gracia y limpieza). Una escritura residual posterior a pytest queda
    # dentro de la foto; si el canario detecta cambios se descarta.
    after = canary_snapshot()
    write_canary(root / "canary-after.txt", after)
    delta = canary_delta_lines(before, after)
    checkout_after = checkout_canary_snapshot(exclude=root)
    def _checkout_key(snapshot: dict) -> dict:
        # El veredicto no compara max_mtime_ns: la huella es sha256 por
        # archivo sobre rutas ordenadas, y el conjunto de archivos (files)
        # mas los bytes totales (total_bytes) ya cubren altas, bajas y
        # cambios de contenido. El mtime de los directorios cambia por
        # scratch legitimo bajo .cdad/tmp (crear y retirar subdirectorios)
        # sin cambiar un byte de contenido, asi que no puede decidir el
        # veredicto. max_mtime_ns sigue en parallel.json como informacion.
        return {key: snapshot.get(key) for key in (
            "scope", "files", "total_bytes",
            "fingerprint", "fingerprint_algo")}
    checkout_unchanged = (_checkout_key(checkout_after)
                          == _checkout_key(checkout_before))
    checkout_incomplete = sorted(set(checkout_after.get("incomplete") or [])
                                 | set(checkout_before.get("incomplete") or []))
    checkout_canary = {**checkout_after, "unchanged": checkout_unchanged,
                       "clean": checkout_unchanged and not checkout_incomplete,
                       "incomplete": checkout_incomplete}
    command_wall = time.monotonic() - command_start
    family_unverifiable = (not orphans_available) or (subreaper is not True)
    consolidated = {
        "passed": sum(entry["result"]["passed"] for entry in entries),
        "failed": sum(entry["result"]["failed"] for entry in entries),
        "skipped": sum(entry["result"]["skipped"] for entry in entries),
    }
    try:
        loadavg = list(os.getloadavg())
    except OSError:
        loadavg = None
    total_preparation = sum(entry["preparation_measured_s"]
                            for entry in entries)
    # M5: duplicada = suma de workers menos la referencia medida; sin
    # referencia, null con motivo (nunca resta contra paredes).
    duplicated: float | None = None
    duplicated_note: str | None = None
    if balance_from is not None:
        try:
            reference = json.loads(Path(balance_from).expanduser().read_text(
                encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            reference = None
            duplicated_note = (f"referencia {balance_from} ilegible: {exc}")
        if reference is not None:
            ref_prep = reference_preparation_s(reference)
            if ref_prep is None:
                duplicated_note = (
                    f"la referencia {balance_from} no trae "
                    "preparation_measured_s ni operaciones de preparacion "
                    "medibles")
            else:
                duplicated = total_preparation - ref_prep
    else:
        duplicated_note = ("sin --balance-from: no hay perfil de referencia "
                           "para la preparacion duplicada")
    summary = {
        "schema_version": PARALLEL_SCHEMA_VERSION,
        "command": [sys.executable, *sys.argv],
        "selection": selection,
        "nodeids": nodeids,
        "file_count": len({nodeid.split("::")[0] for nodeid in nodeids}),
        "workers_requested": workers,
        "workers_launched": len(children),
        "skipped_empty_workers": skipped_empty,
        "nproc": nproc,
        "max_workers": maximum,
        "balance_from": str(balance_from) if balance_from else None,
        "workers": entries,
        "total_wall_s": total_wall,
        "command_wall_s": command_wall,
        "total_work_s": sum(entry["work_measured_s"] for entry in entries),
        "overlap_s": overlap,
        "preparation_source": "per-worker-profiles",
        "total_preparation_s": total_preparation,
        "duplicated_preparation_s": duplicated,
        "consolidated": consolidated,
        "canary": {"scope": canary_scope(), "before": "canary-before.txt",
                   "after": "canary-after.txt", "delta_lines": delta,
                   "unchanged": delta == 0, "clean": delta == 0},
        "checkout_canary": checkout_canary,
        "children_terminated": all(child["proc"].poll() is not None
                                   for child in children),
        "orphans_checked": orphans_checked,
        "orphans": orphans,
        "orphans_found": (total_found if orphans_available else None),
        "orphans_cleaned": (total_cleaned if orphans_available else None),
        "orphans_remaining": (total_remaining if orphans_available else None),
        "orphans_detail": (list(family_detail)
                           if orphans_available else None),
        "orphans_found_pids": (list(family_pids)
                               if orphans_available else None),
        "orphans_found_detail": (list(family_detail)
                                 if orphans_available else None),
        "grace_window_s": PARALLEL_GRACE_WINDOW_S,
        "grace_poll_s": PARALLEL_GRACE_POLL_S,
        "subreaper": subreaper,
        "family_requires_linux": True,
        "family_verifiable": (not family_unverifiable),
        "fault_injection": fault,
        "child_count": len(children),
        "commit": git_revision(),
        "dirty": git_dirty_entries(),
        "started_at": utc_now(),
        "host": {"platform": platform.platform(), "loadavg": loadavg},
    }
    # N1 + N2 (review-T6-002 bloqueantes 1 y 2) + gracia T6 + R1/R2/R3:
    # veredicto explicito fail-closed. Una corrida con familia viva AL
    # FINAL DE LA GRACIA, con garantia de familia no acreditable
    # (subreaper inactivo o barrido no disponible), con canario alterado
    # o con barrido incompleto NO termina con exito limpio: se
    # descarta/rechaza (salida distinta de 0) conservando la evidencia.
    # El transitorio que muere dentro de la gracia (found >= 1,
    # orphans == 0) se acepta. Solo la corrida limpia informa exito.
    canary_dirty = bool(delta) or not checkout_unchanged
    incomplete_dirty = bool(checkout_incomplete)
    discard_reasons: list[str] = []
    if family_unverifiable:
        if fault in ("no-subreaper", "no-sweep"):
            discard_reasons.append(
                f"garantia de familia no acreditable (fault "
                f"CDAD_SUITE_FAULT={fault}; subreaper={subreaper}; "
                f"sweep/barrido disponible={orphans_available}; "
                f"family/familia unverifiable)")
        elif subreaper is not True and not orphans_available:
            discard_reasons.append(
                f"garantia de familia no acreditable (subreaper={subreaper}; "
                f"sweep/barrido no disponible; family/familia unverifiable)")
        elif subreaper is not True:
            discard_reasons.append(
                f"garantia de familia no acreditable (subreaper={subreaper}; "
                f"el barrido por cadena de PPid puede no ver reparentados; "
                f"family/familia unverifiable)")
        else:
            discard_reasons.append(
                "garantia de familia no acreditable (sweep/barrido de "
                "descendientes no disponible; family/familia unverifiable)")
    if orphans_available and (orphans_after_grace or 0) > 0:
        discard_reasons.append(
            f"familia de procesos viva tras el lote: encontrados="
            f"{total_found} limpiados={total_cleaned} "
            f"restantes={total_remaining}")
    if incomplete_dirty:
        discard_reasons.append(
            f"barrido del checkout incompleto (sweep incomplete): "
            f"rutas no leidas={checkout_incomplete}")
    if canary_dirty:
        discard_reasons.append(
            f"canario alterado (config delta_lines={delta}, "
            f"checkout unchanged={checkout_unchanged})")
    if discard_reasons:
        if canary_dirty or incomplete_dirty:
            verdict = ("rejected: canary detected changes or incomplete sweep, "
                       "run discarded para esa seleccion ("
                       + "; ".join(discard_reasons) + ")")
        elif family_unverifiable:
            verdict = ("discarded: process family guarantee not verifiable "
                       "(subreaper/sweep/family/familia) ("
                       + "; ".join(discard_reasons) + ")")
        else:
            verdict = ("discarded: orphaned process family found and "
                       "cleaned (" + "; ".join(discard_reasons) + ")")
    elif first_rc != 0:
        verdict = f"failed: pytest rc={first_rc}"
    else:
        verdict = "accepted"
    summary["verdict"] = verdict
    if duplicated_note is not None:
        summary["duplicated_preparation_note"] = duplicated_note
    if orphans_note is not None:
        summary["orphans_note"] = orphans_note
    # `canary.before/after` nombra archivos de evidencia, no el contenido:
    # el oraculo exige igualdad cuando trae el contenido; los archivos
    # quedan comparables en el raiz de evidencia. Para no publicar un
    # agregado ambiguo, el contenido vive en los archivos y el registro
    # declara el veredicto con `unchanged`/`clean`.
    summary["canary"].pop("before")
    summary["canary"].pop("after")
    write_json_atomic(root / "parallel.json", summary)
    (root / "parallel.md").write_text(_parallel_markdown(summary),
                                      encoding="utf-8")

    print(f"cdad-suite: parallel {workers} workers en {root} "
          f"(pared_total={total_wall:.2f}s, trabajo={summary['total_work_s']:.2f}s, "
          f"solapamiento={overlap:.2f}s, "
          f"passed={consolidated['passed']} failed={consolidated['failed']} "
          f"skipped={consolidated['skipped']}, "
          f"canary_delta_lines={delta}, veredicto={verdict})",
          file=sys.stderr)
    if canary_dirty or incomplete_dirty:
        print("cdad-suite: lote paralelo RECHAZADO/DESCARTADO: el canario "
              f"detecto cambios durante el lote ({root}); la evidencia se "
              "conserva y el resultado no es utilizable", file=sys.stderr)
    if incomplete_dirty:
        print("cdad-suite: lote paralelo RECHAZADO: barrido del checkout "
              f"incompleto (sweep incomplete), rutas no leidas={checkout_incomplete}",
              file=sys.stderr)
    if family_unverifiable:
        print("cdad-suite: lote paralelo DESCARTADO: garantia de familia no "
              f"acreditable (subreaper={subreaper}, sweep/barrido disponible="
              f"{orphans_available}, fault={fault}; family/familia "
              "unverifiable)", file=sys.stderr)
    if orphans_available and (orphans_after_grace or 0) > 0:
        print("cdad-suite: lote paralelo DESCARTADO: quedaron "
              f"{total_found} procesos vivos de la familia del lote "
              f"(limpiados={total_cleaned} restantes={total_remaining})",
              file=sys.stderr)
    if discard_reasons:
        return 3 if first_rc == 0 else first_rc
    return first_rc


# ------------------------------------------- reconcile / entry-check (017-001 T3)
#
# Agregacion contable de spec §4.4 (PC-6, INV-5/INV-6), operacionalizada por
# docs/specs/017-001-suite-performance/t3-aggregator-contract.md. Ambos
# subcomandos son de solo lectura sobre la evidencia: no reescriben el
# intento, no reejecutan pytest, no tocan el checkout. Salidas: 0 producido
# (aunque haya diagnosticos), 1 entrada no satisfecha (solo entry-check),
# 2 entrada inutilizable con motivo por stderr.

T3_SCHEMA_VERSION = 1
T3_TOLERANCE_S = 1e-3
T3_EXTERIOR_RESOLUTION_S = 1.0
T3_ENTRY_CHECKS = (
    "register-calibrated",
    "selection-coverage",
    "attempts-complete",
    "counts-match-register",
    "evidence-locatable",
    "unknowns-declared",
)


def _t3_round(value) -> float:
    """Valor publicado con 3 decimales (contrato §redondeo)."""
    return round(float(value), 3)


def _t3_union_length(intervals) -> float:
    """Longitud de la union de intervalos [started, finished].

    Anidados y solapados contribuyen una sola vez (INV-5). Un intervalo
    invertido se endereza; uno sin numeros se ignora (quien lo consuma ya
    diagnostico la captura).
    """
    spans = []
    for span in intervals:
        try:
            start, end = span
            start, end = float(start), float(end)
        except (TypeError, ValueError):
            continue
        if end < start:
            start, end = end, start
        spans.append((start, end))
    if not spans:
        return 0.0
    spans.sort()
    total = 0.0
    current_start, current_end = spans[0]
    for start, end in spans[1:]:
        if start <= current_end:
            if end > current_end:
                current_end = end
        else:
            total += current_end - current_start
            current_start, current_end = start, end
    total += current_end - current_start
    return total


def _t3_parse_wall(value):
    """Reloj de pared a segundos: numero o ISO-8601; ``None`` si ilegible."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            pass
        try:
            stamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return stamp.timestamp()
    return None


def _t3_load_attempt(attempt_dir: Path) -> tuple[dict, dict]:
    """``(profile, attempt)`` o ``UsageError`` (rc 2) nombrando el artefacto."""
    profile_path = attempt_dir / "profile.json"
    attempt_path = attempt_dir / "attempt.json"
    missing = [name for name, path in
               (("profile.json", profile_path), ("attempt.json", attempt_path))
               if not path.is_file()]
    if missing:
        raise UsageError(
            f"intento inutilizable {attempt_dir}: falta {', '.join(missing)}; "
            "sin profile.json/attempt.json no hay conciliacion posible")
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise UsageError(
            f"intento inutilizable {attempt_dir}: profile.json ilegible: "
            f"{exc}") from exc
    try:
        attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise UsageError(
            f"intento inutilizable {attempt_dir}: attempt.json ilegible: "
            f"{exc}") from exc
    if not isinstance(profile, dict) or not isinstance(attempt, dict):
        raise UsageError(
            f"intento inutilizable {attempt_dir}: profile.json/attempt.json "
            "sin objeto JSON")
    return profile, attempt


def _t3_default_register_path(profile: dict):
    """Registro propio del perfil (``profile.operation_scope.path``)."""
    scope = profile.get("operation_scope")
    if isinstance(scope, dict) and scope.get("path"):
        return Path(str(scope["path"])).expanduser()
    return None


def _t3_load_register(path):
    """``(datos, diagnostico)``; ausente/ilegible no es un conteo inventado."""
    if path is None:
        return None, ("sin registro aplicable: no se indico --register ni el "
                      "perfil declara operation_scope.path")
    try:
        data = Path(path).expanduser().read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"registro ilegible ({path}): {exc}"
    try:
        register = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, f"registro ilegible ({path}): {exc}"
    if not isinstance(register, dict):
        return None, f"registro sin objeto JSON ({path})"
    return register, None


def _t3_resolve_expected(expected, selection: str):
    """Conteo esperado aplicable a ``selection``; ``None`` si no hay conteo.

    Acepta entero o mapa por seleccion/rama con ``total`` (contrato
    §cobertura). Cadenas y ausencias son desconocidos declarables, nunca
    ceros.
    """
    if isinstance(expected, bool):
        return None
    if isinstance(expected, int):
        return expected
    if isinstance(expected, float):
        return int(expected)
    if isinstance(expected, dict):
        if selection in expected:
            sub = expected[selection]
            if isinstance(sub, bool):
                return None
            if isinstance(sub, int):
                return sub
            if isinstance(sub, dict):
                total = sub.get("total")
                if isinstance(total, int) and not isinstance(total, bool):
                    return total
            return None
        total = expected.get("total")
        if isinstance(total, int) and not isinstance(total, bool):
            return total
        return None
    return None


def _t3_applicable_expectations(register, selection: str):
    """``(esperados, declaradas)`` de las familias comprometidas aplicables.

    La seleccion propia de la operacion prevalece sobre la de la familia; una
    familia sin estado se presume comprometida (criterio T2); la seleccion
    agregada ``all-required-selections`` aplica a toda seleccion requerida.
    """
    expected_map: dict[str, int] = {}
    declared: set[str] = set()
    if not isinstance(register, dict):
        return expected_map, declared
    families = register.get("families")
    if not isinstance(families, list):
        return expected_map, declared
    for family in families:
        if not isinstance(family, dict):
            continue
        if str(family.get("state", "comprometida")) != "comprometida":
            continue
        family_selection = family.get("selection")
        operations = family.get("operations")
        if not isinstance(operations, list):
            continue
        for op in operations:
            if not isinstance(op, dict):
                continue
            if str(op.get("state", "comprometida")) != "comprometida":
                continue
            op_id = op.get("id", op.get("operation"))
            if not isinstance(op_id, str) or not op_id:
                continue
            op_selection = op.get("selection")
            if isinstance(op_selection, str) and op_selection:
                if op_selection != selection:
                    continue
            elif isinstance(family_selection, str) and family_selection:
                if (family_selection != "all-required-selections"
                        and family_selection != selection):
                    continue
            declared.add(op_id)
            resolved = _t3_resolve_expected(op.get("expected"), selection)
            if resolved is not None and op_id not in expected_map:
                expected_map[op_id] = resolved
    return expected_map, declared


def _t3_coverage(profile: dict, register, selection: str) -> dict:
    """Contraste esperado/observado sin inventar conteos (spec §4.4)."""
    counts: dict[str, int] = {}
    operations = profile.get("operations")
    if isinstance(operations, list):
        for op in operations:
            if not isinstance(op, dict):
                continue
            name = op.get("operation")
            if isinstance(name, str) and name:
                counts[name] = counts.get(name, 0) + 1
    expected_map, declared = _t3_applicable_expectations(register, selection)
    missing, unexpected, without_entry = [], [], []
    for op_id in sorted(expected_map):
        observed = counts.get(op_id, 0)
        item = {"operation": op_id, "expected": expected_map[op_id],
                "observed": observed}
        if observed < expected_map[op_id]:
            missing.append(item)
        elif observed > expected_map[op_id]:
            unexpected.append(item)
    for name in sorted(counts):
        if name not in declared and name not in expected_map:
            without_entry.append({"operation": name, "observed": counts[name]})
    return {"expected": expected_map, "observed": counts, "missing": missing,
            "unexpected": unexpected, "without_entry": without_entry}


def _t4_is_full_selection(attempt: dict) -> bool:
    """Seleccion completa: ``attempt.selection`` dict con ``kind == "all"``.

    Forma de la base (017-001 T4, spec §4.4/PC-5): ``selection`` deja de ser
    una lista focal y pasa a ``{"kind": "all", "nodeids": [...]}``. Solo ese
    marcador activa el contraste de alcance contra ``expected_in_full_run``;
    cualquier otra forma (lista, dict sin kind) conserva el comportamiento
    focal aprobado.
    """
    selection = (attempt or {}).get("selection")
    return isinstance(selection, dict) and selection.get("kind") == "all"


def _t4_full_run_declarations(register):
    """``(exigidas, opcionales, declaradas)`` para seleccion completa.

    Exigidas: ``expected_in_full_run is True`` con su reason. Opcionales:
    ``expected_in_full_run is False`` con su reason (cero observaciones es un
    recorrido no ejercitado, nunca un faltante). Declaradas: todo id presente
    en el registro (para ``operation-without-register-entry``). Sin bool no
    hay conteo inventado: la operacion queda declarada pero fuera del
    contraste de alcance.
    """
    required: dict[str, str] = {}
    optional: dict[str, str] = {}
    declared: set[str] = set()
    if not isinstance(register, dict):
        return required, optional, declared
    families = register.get("families")
    if not isinstance(families, list):
        return required, optional, declared
    for family in families:
        if not isinstance(family, dict):
            continue
        if str(family.get("state", "comprometida")) != "comprometida":
            continue
        operations = family.get("operations")
        if not isinstance(operations, list):
            continue
        for op in operations:
            if not isinstance(op, dict):
                continue
            if str(op.get("state", "comprometida")) != "comprometida":
                continue
            op_id = op.get("id", op.get("operation"))
            if not isinstance(op_id, str) or not op_id:
                continue
            declared.add(op_id)
            flag = op.get("expected_in_full_run")
            if flag is True:
                reason = op.get("expected_in_full_run_reason", "")
                if op_id not in required:
                    required[op_id] = str(reason) if isinstance(reason, str) else ""
            elif flag is False:
                reason = op.get("expected_in_full_run_reason", "")
                if op_id not in optional:
                    optional[op_id] = str(reason) if isinstance(reason, str) else ""
    return required, optional, declared


def _t4_full_coverage(profile: dict, register) -> dict:
    """Contraste declarado vs observado para seleccion completa (spec §4.4).

    - Exigida (true) con cero observaciones: faltante (al menos una
      ocurrencia esperada).
    - Opcional (false) con cero observaciones: no ejercitada con su reason,
      sin diagnostico de faltante.
    - Opcional (false) pero observada: sin diagnostico.
    - Observada no declarada: ``operation-without-register-entry``.
    """
    counts: dict[str, int] = {}
    operations = profile.get("operations")
    if isinstance(operations, list):
        for op in operations:
            if not isinstance(op, dict):
                continue
            name = op.get("operation")
            if isinstance(name, str) and name:
                counts[name] = counts.get(name, 0) + 1
    required, optional, declared = _t4_full_run_declarations(register)
    missing, without_entry, unexercised = [], [], []
    for op_id in sorted(required):
        if counts.get(op_id, 0) <= 0:
            missing.append({"operation": op_id, "expected": 1,
                            "observed": 0, "reason": required[op_id]})
    for op_id in sorted(optional):
        if counts.get(op_id, 0) <= 0:
            unexercised.append({"operation": op_id,
                                "reason": optional[op_id]})
    for name in sorted(counts):
        if name not in declared:
            without_entry.append({"operation": name, "observed": counts[name]})
    blocked = bool(missing)
    return {"missing": missing, "unexpected": [],
            "without_entry": without_entry, "unexercised": unexercised,
            "blocked": blocked}


def _t3_infer_selection(register, attempt_nodeids):
    """Clave de seleccion del registro cuyos nodeids cubren el intento."""
    if not isinstance(register, dict):
        return None
    selections = register.get("selections")
    if not isinstance(selections, dict):
        return None
    wanted = {node for node in (attempt_nodeids or [])
              if isinstance(node, str)}
    if not wanted:
        return None
    for key in sorted(selections):
        entry = selections[key]
        if not isinstance(entry, dict):
            continue
        nodeids = entry.get("nodeids")
        if isinstance(nodeids, list) and set(nodeids) == wanted:
            return key
    for key in sorted(selections):
        entry = selections[key]
        if not isinstance(entry, dict):
            continue
        nodeids = entry.get("nodeids")
        if isinstance(nodeids, list) and wanted <= set(nodeids):
            return key
    return None


def _t3_attempt_nodeids(profile: dict, attempt: dict) -> list:
    selection = attempt.get("selection")
    if isinstance(selection, list) and all(isinstance(n, str) for n in selection):
        return list(selection)
    nodeids = set()
    for row in profile.get("phases") or []:
        if isinstance(row, dict) and isinstance(row.get("nodeid"), str):
            nodeids.add(row["nodeid"])
    return sorted(nodeids)


def _t3_build_reconciliation(attempt_dir: Path, profile: dict, attempt: dict,
                             register, register_path) -> dict:
    """Conciliacion §4.4 desde la evidencia cruda (determinista)."""
    phases = profile.get("phases")
    if not isinstance(phases, list):
        phases = []
    operations = profile.get("operations")
    if not isinstance(operations, list):
        operations = []

    s_test: dict[str, float] = {}
    for row in phases:
        if not isinstance(row, dict):
            continue
        nodeid, duration = row.get("nodeid"), row.get("duration_s")
        if (not isinstance(nodeid, str) or not isinstance(duration, (int, float))
                or isinstance(duration, bool)):
            continue
        s_test[nodeid] = s_test.get(nodeid, 0.0) + float(duration)

    intervals: dict[str, list] = {nodeid: [] for nodeid in s_test}
    breakdown: dict[str, list] = {nodeid: [] for nodeid in s_test}
    shared_rows: list[dict] = []
    for op in operations:
        if not isinstance(op, dict):
            continue
        nodeid = op.get("nodeid")
        started, finished = op.get("started"), op.get("finished")
        numeric = (isinstance(started, (int, float))
                   and isinstance(finished, (int, float))
                   and not isinstance(started, bool)
                   and not isinstance(finished, bool))
        row = {}
        for key in ("operation", "interval_id", "parent_id", "nodeid", "phase",
                    "owner_scope", "branch", "started", "finished",
                    "termination"):
            value = op.get(key)
            if value is not None:
                row[key] = value
        if numeric:
            row["duration_s"] = _t3_round(abs(float(finished) - float(started)))
        if (op.get("owner_scope") == "test" and isinstance(nodeid, str)
                and nodeid in intervals and numeric):
            intervals[nodeid].append((started, finished))
            breakdown[nodeid].append(row)
        else:
            shared_rows.append(row)
    for nodeid in breakdown:
        breakdown[nodeid].sort(key=lambda r: (
            r.get("started", 0), str(r.get("interval_id", ""))))
    shared_rows.sort(key=lambda r: (
        r.get("started", 0) if isinstance(r.get("started"), (int, float)) else 0,
        str(r.get("interval_id", ""))))

    union_len = {nodeid: _t3_union_length(intervals[nodeid]) for nodeid in s_test}
    tests = []
    for nodeid in sorted(s_test, key=lambda n: (-_t3_round(s_test[n]), n)):
        attributed = _t3_round(union_len[nodeid])
        tests.append({
            "nodeid": nodeid,
            "file": nodeid.split("::")[0],
            "S_test": _t3_round(s_test[nodeid]),
            "preparation_s": attributed,
            "remainder_s": _t3_round(s_test[nodeid] - union_len[nodeid]),
            "resolution_s": {"phases": 0.001, "operations": 0.001},
            "operations": breakdown[nodeid],
        })

    files_map: dict[str, list] = {}
    for row in tests:
        files_map.setdefault(row["file"], []).append(row["nodeid"])
    files = [{"path": path, "S_file": _t3_round(sum(s_test[n] for n in nodeids)),
              "tests": sorted(nodeids)}
             for path, nodeids in files_map.items()]
    files.sort(key=lambda item: (-item["S_file"], item["path"]))

    shared_total = _t3_round(_t3_union_length([
        (row["started"], row["finished"]) for row in shared_rows
        if isinstance(row.get("started"), (int, float))
        and isinstance(row.get("finished"), (int, float))]))

    raw_pytest = profile.get("pytest_wall_s")
    t_pytest = (float(raw_pytest) if isinstance(raw_pytest, (int, float))
                and not isinstance(raw_pytest, bool) else None)
    sum_s = sum(s_test.values())
    # T4 hallazgo-2 (PC-6/INV-5): totales de corrida desde valores sin
    # redondear (no sumando los valores por test ya redondeados).
    prep_total = sum(union_len.get(nodeid, 0.0) for nodeid in s_test)
    rem_total = sum_s - prep_total
    n_tests = len(s_test)
    rounding_bound = round(n_tests * 0.0005, 4)
    r_pytest = t_pytest - sum_s if t_pytest is not None else None
    started_at = _t3_parse_wall(attempt.get("started_at"))
    finished_at = _t3_parse_wall(attempt.get("finished_at"))
    t_exterior = (finished_at - started_at
                  if started_at is not None and finished_at is not None else None)
    r_exterior = (t_exterior - t_pytest if t_exterior is not None
                  and t_pytest is not None else None)

    attempt_nodeids = _t3_attempt_nodeids(profile, attempt)
    selection_key = _t3_infer_selection(register, attempt_nodeids)
    is_full = _t4_is_full_selection(attempt)
    if is_full and register is not None:
        detail = _t4_full_coverage(profile, register)
        key = selection_key if selection_key is not None else "all"
        coverage = {"selection": key, "status": "all-selection",
                    "missing": detail["missing"],
                    "unexpected": detail["unexpected"],
                    "without_entry": detail["without_entry"],
                    "unexercised": detail["unexercised"],
                    "blocked": detail["blocked"],
                    "measurement": ("blocked-incomplete" if detail["blocked"]
                                    else "complete")}
    elif register is None:
        coverage = {"selection": selection_key, "status": "unavailable",
                    "missing": [], "unexpected": [], "without_entry": []}
    elif selection_key is None:
        coverage = {"selection": None, "status": "unavailable",
                    "missing": [], "unexpected": [], "without_entry": []}
    else:
        detail = _t3_coverage(profile, register, selection_key)
        coverage = {"selection": selection_key, "status": "available",
                    "missing": detail["missing"],
                    "unexpected": detail["unexpected"],
                    "without_entry": detail["without_entry"]}

    diagnostics: list[str] = []
    if profile.get("status") != "complete":
        diagnostics.append("profile-incomplete")
    if profile.get("capture_errors"):
        diagnostics.append("capture-error")
    if profile.get("operation_errors"):
        diagnostics.append("operation-error")
    for nodeid in s_test:
        if union_len[nodeid] > s_test[nodeid] + T3_TOLERANCE_S:
            diagnostics.append("attribution-exceeds-phases")
            break
    if register is None or coverage["status"] == "unavailable":
        diagnostics.append("scope-unavailable")
    elif not (register.get("calibrated") is True
              and register.get("status") == "calibrated"):
        diagnostics.append("scope-not-calibrated")
    if coverage["missing"]:
        diagnostics.append("missing-operation-vs-register")
    if coverage["unexpected"]:
        diagnostics.append("unexpected-operation")
    if coverage["without_entry"]:
        diagnostics.append("operation-without-register-entry")
    if r_pytest is not None and r_pytest < -T3_TOLERANCE_S:
        diagnostics.append("residual-sign")
    # Contrato §redondeo: la comparacion usa la tolerancia 1e-3 s o la
    # resolucion declarada si es mayor. El reloj exterior declara 1 s, asi
    # que una diferencia menor que esa resolucion no es discrepancia
    # (review-T3 opcional).
    exterior_limit = max(T3_EXTERIOR_RESOLUTION_S, T3_TOLERANCE_S)
    if r_exterior is not None and r_exterior < -exterior_limit:
        if "residual-sign" not in diagnostics:
            diagnostics.append("residual-sign")

    return {
        "schema_version": T3_SCHEMA_VERSION,
        "attempt": str(attempt_dir),
        "selection": attempt.get("selection"),
        "commit": attempt.get("commit"),
        "status": profile.get("status"),
        "diagnosis": profile.get("diagnosis"),
        "clocks": {
            "pytest_wall_s": _t3_round(t_pytest) if t_pytest is not None else None,
            "resolution": ("phases/pytest: monotonic, tolerance 1e-3 s; "
                           "exterior: wall clock, 1 s declared resolution"),
            "resolution_s": {"phases": 0.001, "pytest_wall": 0.001,
                             "exterior": T3_EXTERIOR_RESOLUTION_S},
            "tolerance_s": T3_TOLERANCE_S,
        },
        "tests": tests,
        "files": files,
        "shared": {"total_s": shared_total, "operations": shared_rows},
        "run": {
            "T_pytest": _t3_round(t_pytest) if t_pytest is not None else None,
            "sum_S_test": _t3_round(sum_s),
            "preparation_s": _t3_round(prep_total),
            "remainder_s": _t3_round(rem_total),
            "R_pytest": _t3_round(r_pytest) if r_pytest is not None else None,
            "T_exterior": _t3_round(t_exterior) if t_exterior is not None else None,
            "R_exterior": _t3_round(r_exterior) if r_exterior is not None else None,
            "n_tests": n_tests,
            "rounding_bound_s": rounding_bound,
            "rounding_note": ("totales de corrida con redondeo (rounding) a 3 "
                              "decimales calculados desde los valores sin redondear; "
                              "cota (bound) al sumar valores por test publicados: "
                              "N x 0.0005 s; comparacion con tolerancia 1e-3 s"),
            "resolution": ("T_pytest/phases: monotonic, tolerance 1e-3 s; "
                           "T_exterior: wall clock, 1 s declared resolution"),
            "resolution_s": {"pytest": 0.001,
                             "exterior": T3_EXTERIOR_RESOLUTION_S},
            "tolerance_s": T3_TOLERANCE_S,
        },
        "register": {
            "path": str(register_path) if register_path is not None else None,
            "status": register.get("status") if register else None,
            "calibrated": register.get("calibrated") if register else None,
            "coverage": coverage,
        },
        "diagnostics": diagnostics,
    }


def _t3_reconciliation_markdown(payload: dict) -> str:
    lines = ["# Reconciliation (017-001 T3, spec §4.4)", "",
             f"attempt: {payload.get('attempt')}",
             f"status: {payload.get('status')}",
             f"commit: {payload.get('commit')}", ""]
    lines += ["## Tests (por costo descendente)", "",
              "| nodeid | S_test | preparation_s | remainder_s |",
              "| --- | ---: | ---: | ---: |"]
    for row in payload.get("tests") or []:
        lines.append(f"| {row['nodeid']} | {row['S_test']:.3f} | "
                     f"{row['preparation_s']:.3f} | {row['remainder_s']:.3f} |")
    lines += ["", "## Files", ""]
    for item in payload.get("files") or []:
        lines.append(f"- {item['path']}: S_file={item['S_file']:.3f} "
                     f"({len(item['tests'])} tests)")
    shared = payload.get("shared") or {}
    lines += ["", "## Shared (no adjudicado a ningun S_test)", "",
              f"total_s={shared.get('total_s')} "
              f"({len(shared.get('operations') or [])} operaciones)", ""]
    run = payload.get("run") or {}
    lines += ["## Run residuals (con signo y resolucion)", "",
              f"T_pytest={run.get('T_pytest')} sum_S_test={run.get('sum_S_test')} "
              f"R_pytest={run.get('R_pytest')}",
              f"preparation_s={run.get('preparation_s')} "
              f"remainder_s={run.get('remainder_s')} "
              f"(preparation_s+remainder_s==sum_S_test, tolerancia 1e-3 s)",
              f"T_exterior={run.get('T_exterior')} "
              f"R_exterior={run.get('R_exterior')}",
              f"resolution: {run.get('resolution')}",
              f"rounding (redondeo): totales a 3 decimales desde valores sin "
              f"redondear; cota (bound) al sumar valores por test publicados: "
              f"N x 0.0005 s = {run.get('rounding_bound_s')} s "
              f"(N={run.get('n_tests')})", ""]
    lines += ["## Diagnostics", ""]
    diagnostics = payload.get("diagnostics") or []
    if diagnostics:
        lines += [f"- {code}" for code in diagnostics]
    else:
        lines.append("- none")
    coverage = (payload.get("register") or {}).get("coverage") or {}
    lines += ["", "## Register coverage",
              f"selection={coverage.get('selection')} "
              f"status={coverage.get('status')}",
              f"missing={len(coverage.get('missing') or [])} "
              f"unexpected={len(coverage.get('unexpected') or [])} "
              f"without_entry={len(coverage.get('without_entry') or [])}", ""]
    return "\n".join(lines)


def cmd_reconcile(attempt: str, out: str, register) -> int:
    """Concilia un intento; rc 0 producido, rc 2 entrada inutilizable."""
    attempt_dir = Path(attempt).expanduser()
    if not attempt_dir.is_dir():
        raise UsageError(
            f"intento inutilizable {attempt_dir}: falta attempt.json y "
            "profile.json (no existe el directorio)")
    profile, attempt_doc = _t3_load_attempt(attempt_dir)
    if register is not None:
        register_path = Path(register).expanduser()
    else:
        register_path = _t3_default_register_path(profile)
        if register_path is not None and not register_path.is_file():
            register_path = None
    register_data, _ = _t3_load_register(register_path)
    payload = _t3_build_reconciliation(attempt_dir, profile, attempt_doc,
                                       register_data, register_path)
    out_dir = Path(out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_dir / "reconciliation.json", payload)
    (out_dir / "reconciliation.md").write_text(
        _t3_reconciliation_markdown(payload), encoding="utf-8")
    print(f"cdad-suite: reconcile {attempt_dir} -> {out_dir} "
          f"(status={payload['status']}, "
          f"diagnostics={','.join(payload['diagnostics']) or 'none'})",
          file=sys.stderr)
    return 0


def _t3_check(name: str, passed: bool, reasons=None) -> dict:
    return {"name": name, "passed": bool(passed),
            "reasons": list(reasons or [])}


def _t3_unknowns_declared(register) -> tuple[bool, list]:
    if not isinstance(register, dict):
        return False, ["sin registro aplicable (scope-unavailable)"]
    volumes = register.get("volume_observations")
    if isinstance(volumes, dict):
        for key, volume in volumes.items():
            if not isinstance(volume, dict):
                continue
            unknown = volume.get("unknown_component")
            if isinstance(unknown, dict) and unknown.get("decision_rule"):
                return True, []
    return False, ["el registro no declara unknowns con decision_rule "
                   "(volume_observations.*.unknown_component.decision_rule)"]


def _t3_declared_selection_nodeids(attempt_doc: dict) -> list | None:
    """Nodeids efectivamente declarados por el intento, o ``None``.

    Forma real de ``close`` (``attempt.json``): ``selection`` es un dict con
    ``nodeids`` (lista) y ``value`` (ruta del archivo de nodeids o capacidad).
    Los tests sinteticos usan una lista plana. ``value`` como lista tambien
    vale; un ``value`` escalar (ruta o capacidad) sin ``nodeids`` no se
    resuelve aqui: se declara desconocido, nunca un conjunto inventado.
    """
    selection = (attempt_doc or {}).get("selection")
    if isinstance(selection, list):
        if selection and all(isinstance(n, str) for n in selection):
            return sorted(selection)
        return None
    if isinstance(selection, dict):
        nodeids = selection.get("nodeids")
        if (isinstance(nodeids, list) and nodeids
                and all(isinstance(n, str) for n in nodeids)):
            return sorted(nodeids)
        value = selection.get("value")
        if (isinstance(value, list) and value
                and all(isinstance(n, str) for n in value)):
            return sorted(value)
        return None
    return None


def _t3_evaluate_entry(mapping: dict, loaded: dict, register,
                       register_path) -> dict:
    """Seis checks nombrados del contrato; ``satisfied`` solo si todos pasan."""
    checks = []

    if register is None:
        checks.append(_t3_check("register-calibrated", False,
                                ["sin registro aplicable (scope-unavailable)"]))
    else:
        calibrated = register.get("calibrated") is True
        status_ok = register.get("status") == "calibrated"
        reasons = []
        if not calibrated:
            reasons.append("registro sin calibrated: true")
        if not status_ok:
            reasons.append(f"registro con status={register.get('status')!r} "
                           "(se exige 'calibrated')")
        checks.append(_t3_check("register-calibrated",
                                calibrated and status_ok, reasons))

    if not isinstance(register, dict) or not isinstance(
            register.get("selections"), dict):
        checks.append(_t3_check("selection-coverage", False,
                                ["sin registro aplicable (scope-unavailable)"]))
    else:
        selections = register["selections"]
        required = {key for key, entry in selections.items()
                    if not (isinstance(entry, dict)
                            and entry.get("required_for_current_calibration")
                            is False)}
        missing = sorted(required - set(loaded))
        extra = sorted(set(loaded) - set(selections))
        reasons = ([f"seleccion requerida sin intento: {key}" for key in missing]
                   + [f"mapa trae seleccion fuera del registro: {key}"
                      for key in extra])
        # Review-T3 bloqueante (PC-1, spec §4.4): cada clave del mapa debe
        # vincularse con la seleccion efectivamente declarada por su intento
        # y con los nodeids que el registro declara para esa seleccion. Una
        # asociacion equivocada al construir el mapa no puede acreditar una
        # calibracion para una seleccion que el intento no declara.
        for key in sorted(loaded):
            if key not in selections:
                continue
            _, _, attempt_doc = loaded[key]
            declared = _t3_declared_selection_nodeids(attempt_doc)
            entry = selections[key]
            expected = (entry.get("nodeids") if isinstance(entry, dict)
                        else None)
            if declared is None:
                reasons.append(
                    f"{key}: el intento no declara una seleccion "
                    f"verificable (selection ausente o irresoluble "
                    f"en attempt.json; sin inventarla)")
                continue
            if not isinstance(expected, list):
                continue
            if set(declared) != set(expected):
                reasons.append(
                    f"{key}: la seleccion declarada por el intento no "
                    f"coincide con el registro "
                    f"(declarada={sorted(declared)}, "
                    f"registro={sorted(expected)})")
        checks.append(_t3_check("selection-coverage",
                                not reasons, reasons))

    complete_reasons, complete_diag = [], set()
    for key in sorted(loaded):
        _, profile, _ = loaded[key]
        if profile.get("status") != "complete":
            complete_reasons.append(
                f"{key}: profile-incomplete "
                f"(status={profile.get('status')!r})")
            complete_diag.add("profile-incomplete")
        if profile.get("capture_errors"):
            complete_reasons.append(f"{key}: capture-error")
            complete_diag.add("capture-error")
        if profile.get("operation_errors"):
            complete_reasons.append(f"{key}: operation-error")
            complete_diag.add("operation-error")
    checks.append(_t3_check("attempts-complete", not complete_reasons,
                            complete_reasons))

    count_reasons = []
    missing_any, unexpected_any, without_any = False, False, False
    for key in sorted(loaded):
        _, profile, _ = loaded[key]
        detail = _t3_coverage(profile, register, key)
        if detail["missing"]:
            missing_any = True
            for item in detail["missing"]:
                count_reasons.append(
                    f"{key}: missing-operation-vs-register "
                    f"{item['operation']} "
                    f"(esperada {item['expected']}, "
                    f"observada {item['observed']})")
        if detail["unexpected"]:
            unexpected_any = True
        if detail["without_entry"]:
            without_any = True
    checks.append(_t3_check("counts-match-register", not missing_any,
                            count_reasons))

    evidence_reasons = []
    for key in sorted(loaded):
        attempt_dir, _, attempt_doc = loaded[key]
        if not attempt_doc.get("commit"):
            evidence_reasons.append(f"{key}: sin commit declarado")
        if not (attempt_dir / "profile.json").is_file():
            evidence_reasons.append(f"{key}: falta profile.json")
        if not (attempt_dir / "attempt.json").is_file():
            evidence_reasons.append(f"{key}: falta attempt.json")
    checks.append(_t3_check("evidence-locatable", not evidence_reasons,
                            evidence_reasons))

    unknowns_ok, unknowns_reasons = _t3_unknowns_declared(register)
    checks.append(_t3_check("unknowns-declared", unknowns_ok,
                            unknowns_reasons))

    diagnostics = sorted(complete_diag)
    if missing_any:
        diagnostics.append("missing-operation-vs-register")
    if unexpected_any:
        diagnostics.append("unexpected-operation")
    if without_any:
        diagnostics.append("operation-without-register-entry")
    if register is None:
        diagnostics.append("scope-unavailable")
    elif not (register.get("calibrated") is True
              and register.get("status") == "calibrated"):
        diagnostics.append("scope-not-calibrated")

    satisfied = all(check["passed"] for check in checks)
    return {
        "schema_version": T3_SCHEMA_VERSION,
        "satisfied": satisfied,
        "checks": checks,
        "diagnostics": diagnostics,
        "attempts": {key: {"dir": str(adir),
                           "status": profile.get("status"),
                           "commit": attempt_doc.get("commit")}
                     for key, (adir, profile, attempt_doc) in loaded.items()},
        "register": {
            "path": str(register_path) if register_path is not None else None,
            "status": register.get("status") if register else None,
            "calibrated": register.get("calibrated") if register else None,
        },
        "resolution": ("tolerance 1e-3 s; exterior wall clock, "
                       "1 s declared resolution"),
        "tolerance_s": T3_TOLERANCE_S,
    }


def _t3_entry_markdown(entry: dict) -> str:
    lines = ["# Entry check (017-001 T3, condicion de entrada a la base)", "",
             f"satisfied: {str(entry.get('satisfied')).lower()}", ""]
    for check in entry.get("checks") or []:
        verdict = "pass" if check["passed"] else "FAIL"
        lines.append(f"## {check['name']}: {verdict}")
        for reason in check.get("reasons") or []:
            lines.append(f"- {reason}")
        if not check.get("reasons"):
            lines.append("- ok")
        lines.append("")
    diagnostics = entry.get("diagnostics") or []
    lines.append("## Diagnostics")
    lines += [f"- {code}" for code in diagnostics] if diagnostics else ["- none"]
    lines.append("")
    return "\n".join(lines)


def cmd_entry_check(attempts: str, out: str, register) -> int:
    """Comprueba la entrada; 0 satisfecha, 1 no satisfecha, 2 inutilizable."""
    mapping_path = Path(attempts).expanduser()
    if not mapping_path.is_file():
        raise UsageError(
            f"mapa inutilizable {mapping_path}: falta el archivo de mapa "
            "seleccion->intento")
    try:
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise UsageError(
            f"mapa inutilizable {mapping_path}: JSON invalido: {exc}") from exc
    if not isinstance(mapping, dict) or not mapping:
        raise UsageError(
            f"mapa inutilizable {mapping_path}: debe ser un objeto JSON no "
            "vacio seleccion->directorio de intento")
    loaded: dict[str, tuple[Path, dict, dict]] = {}
    for key in sorted(mapping):
        attempt_dir = Path(str(mapping[key])).expanduser()
        if not attempt_dir.is_dir():
            raise UsageError(
                f"mapa inutilizable: la seleccion {key} apunta a {attempt_dir}, "
                "sin profile.json/attempt.json (ruta inexistente)")
        loaded[key] = (attempt_dir,) + _t3_load_attempt(attempt_dir)
    if register is not None:
        register_path = Path(register).expanduser()
        register_data, _ = _t3_load_register(register_path)
    else:
        register_path, register_data = None, None
        for _, profile, _ in loaded.values():
            candidate = _t3_default_register_path(profile)
            if candidate is not None and candidate.is_file():
                register_path = candidate
                break
        if register_path is None:
            for _, profile, _ in loaded.values():
                candidate = _t3_default_register_path(profile)
                if candidate is not None:
                    register_path = candidate
                    break
        register_data, _ = _t3_load_register(register_path)
    entry = _t3_evaluate_entry(mapping, loaded, register_data, register_path)
    out_dir = Path(out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_dir / "entry.json", entry)
    (out_dir / "entry.md").write_text(_t3_entry_markdown(entry),
                                       encoding="utf-8")
    print(f"cdad-suite: entry-check {mapping_path} -> {out_dir} "
          f"(satisfied={str(entry['satisfied']).lower()})", file=sys.stderr)
    return 0 if entry["satisfied"] else 1


# ---------------------------------------------------------------------- main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdad-suite.py",
        description="Seleccion canonica de la suite por capacidad y contrato.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="integridad de inventario, mapa y deuda temporal")
    for name, help_text in (("list", "nodeids de una capacidad (JSON)"),
                            ("run", "ejecuta la seleccion de una capacidad con pytest")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--capability", required=True)
    surface = commands.add_parser("surface", help="selecciona por superficie contra una ref")
    surface.add_argument("--base", required=True)
    surface.add_argument("--all", action="store_true",
                         help="selecciona todos los nodeids actuales (explicito)")
    surface.add_argument("--collect-only", action="store_true",
                         help="emite la seleccion sin ejecutarla")
    commands.add_parser("measure", help="medicion informativa read-only del universo")
    close = commands.add_parser(
        "close", help="gate final: ejecuta la seleccion y conserva la evidencia")
    close.add_argument("--evidence-root", required=True,
                       help="directorio existente donde se reserva un intento nuevo")
    selection = close.add_mutually_exclusive_group()
    selection.add_argument("--capability")
    selection.add_argument("--nodeids", help="archivo con nodeids separados por lineas")
    selection.add_argument("--all", action="store_true",
                           help="selecciona todos los nodeids actuales (explicito)")
    close.add_argument("--operation-scope",
                       help="registro de alcance de operaciones aplicado "
                            "(por defecto, el registro del repositorio del CLI)")
    reconcile = commands.add_parser(
        "reconcile", help="conciliacion contable de un intento (017-001 T3)")
    reconcile.add_argument("--attempt", required=True,
                           help="directorio del intento con profile.json/attempt.json")
    reconcile.add_argument("--out", required=True,
                           help="directorio donde se escriben reconciliation.json/md")
    reconcile.add_argument("--register", default=None,
                           help="registro de operaciones (por defecto, el del propio perfil)")
    entry = commands.add_parser(
        "entry-check", help="condicion de entrada a la base (017-001 T3)")
    entry.add_argument("--attempts", required=True,
                       help="mapa JSON seleccion->directorio de intento")
    entry.add_argument("--out", required=True,
                       help="directorio donde se escriben entry.json/md")
    entry.add_argument("--register", default=None,
                       help="registro de operaciones (por defecto, el de los perfiles)")
    parallel = commands.add_parser(
        "parallel", help="lote paralelo con workers configurables (017-001 T6)")
    parallel.add_argument("--workers", type=int, default=PARALLEL_DEFAULT_WORKERS,
                          help="workers pytest hijos (1 <= N <= nproc-1; "
                               "por defecto 2, nunca todos los nucleos)")
    parallel.add_argument("--evidence-root", required=True,
                          help="directorio existente VACIO para esta invocacion "
                               "(con worker-<i>/ y el agregado); si ya contiene "
                               "parallel.json, canarios o worker-*/ se rechaza "
                               "el destino ocupado y nunca se reutilizan XML, "
                               "perfiles ni fases del intento anterior")
    parallel_selection = parallel.add_mutually_exclusive_group()
    parallel_selection.add_argument("--capability")
    parallel_selection.add_argument("--nodeids",
                                    help="archivo con nodeids separados por lineas")
    parallel_selection.add_argument("--all", action="store_true",
                                    help="selecciona todos los nodeids actuales "
                                         "(explicito)")
    parallel.add_argument("--balance-from", default=None,
                          help="profile.json con fases medidas para balancear "
                               "por costo (opcional)")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            return cmd_validate()
        if args.command == "list":
            return cmd_list(args.capability)
        if args.command == "run":
            return cmd_run(args.capability)
        if args.command == "surface":
            return cmd_surface(args.base, args.all, args.collect_only)
        if args.command == "close":
            return cmd_close(args.evidence_root, args.capability, args.nodeids,
                             args.operation_scope)
        if args.command == "reconcile":
            return cmd_reconcile(args.attempt, args.out, args.register)
        if args.command == "entry-check":
            return cmd_entry_check(args.attempts, args.out, args.register)
        if args.command == "parallel":
            return cmd_parallel(args.evidence_root, args.capability,
                                args.nodeids, args.all, args.workers,
                                args.balance_from)
        return cmd_measure()
    except UsageError as exc:
        print(f"cdad-suite: {exc}", file=sys.stderr)
        return 2
    except Diagnosis as exc:
        print(f"cdad-suite: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
