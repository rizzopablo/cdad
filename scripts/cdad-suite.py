#!/usr/bin/env python3
"""Selector canonico de la suite por capacidad y contrato (008-002 §5).

Seis subcomandos, sin framework nuevo: la ejecucion delegada es el pytest ya
instalado.

- ``validate``  integridad estructural del inventario, del mapa y de la
                disposicion temporal frente a la coleccion real de pytest.
- ``list``      nodeids de una capacidad, ordenados y sin duplicados (JSON).
- ``run``       ejecuta exactamente esa seleccion y propaga el resultado.
- ``surface``   selecciona por superficie contra una ref de git.
- ``measure``   medicion informativa y read-only del universo de tests.
- ``close``     gate final del closer: reserva un directorio de intento propio
                y conserva comando, seleccion, commit, estado, tiempos,
                resultado, skips, salidas y snapshots del canario (PC-6, AJ7).

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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

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


def run_pytest_to_logs(attempt: Path, nodeids: list[str]) -> int:
    """Ejecuta la seleccion; la salida se escribe directo en los logs.

    Escribir a los logs (en vez de capturar y volcar al final) conserva la
    salida parcial de un intento interrumpido.

    La salida efectiva del hijo se controla en tres frentes, porque el resumen
    del intento depende de sus lineas por test: ``PYTEST_ADDOPTS`` se elimina
    del entorno (opciones como ``-qq`` las silencian), ``-o addopts=`` anula
    los ``addopts`` declarados en la configuracion del proyecto y ``COLUMNS``
    se fija para que el motivo publicado de un skip no se trunque con el
    ancho del terminal (008-005 D3: el parser no cambia).
    """
    argv = [sys.executable, "-m", "pytest", "-v", "-rs", "-o", "addopts=",
            "-p", "no:cacheprovider", *nodeids]
    env = {key: value for key, value in os.environ.items()
           if key != "PYTEST_ADDOPTS"}
    env["COLUMNS"] = "1000"
    with (attempt / "stdout.log").open("w", encoding="utf-8") as out, \
            (attempt / "stderr.log").open("w", encoding="utf-8") as err:
        return subprocess.run(argv, stdout=out, stderr=err,
                              stdin=subprocess.DEVNULL, env=env).returncode


def cmd_close(evidence_root: str, capability, nodeids_file) -> int:
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
        "artifacts": {"stdout": "stdout.log", "stderr": "stderr.log"},
    }
    attempt_json = attempt / "attempt.json"
    write_json_atomic(attempt_json, record)

    before = canary_snapshot()
    write_canary(attempt / "canary-before.txt", before)
    try:
        rc = run_pytest_to_logs(attempt, selection["nodeids"])
    except KeyboardInterrupt:
        record.update(state="interrupted", finished_at=utc_now())
        write_json_atomic(attempt_json, record)
        print(f"cdad-suite: close interrumpido: {attempt}", file=sys.stderr)
        return 130
    except BaseException:
        record.update(state="interrupted", finished_at=utc_now())
        write_json_atomic(attempt_json, record)
        raise

    after = canary_snapshot()
    write_canary(attempt / "canary-after.txt", after)
    record["canary"]["delta_lines"] = canary_delta_lines(before, after)
    stdout = (attempt / "stdout.log").read_text(encoding="utf-8", errors="replace")
    summary = parse_pytest_verbose(stdout)
    record.update(state="finished", finished_at=utc_now(), rc=rc,
                  pytest_summary=summary)
    write_json_atomic(attempt_json, record)

    print(f"cdad-suite: intento {attempt} (rc={rc}, "
          f"canary_delta_lines={record['canary']['delta_lines']})", file=sys.stderr)
    if not summary["verified"]:
        print("cdad-suite: aviso: resumen de pytest no verificable en "
              f"{attempt}: {summary['diagnosis']}", file=sys.stderr)
    if record["canary"]["delta_lines"]:
        print("cdad-suite: aviso: el canario detecto cambios en el HOME real "
              f"durante el intento ({attempt})", file=sys.stderr)
    return rc


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
            return cmd_close(args.evidence_root, args.capability, args.nodeids)
        return cmd_measure()
    except UsageError as exc:
        print(f"cdad-suite: {exc}", file=sys.stderr)
        return 2
    except Diagnosis as exc:
        print(f"cdad-suite: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
