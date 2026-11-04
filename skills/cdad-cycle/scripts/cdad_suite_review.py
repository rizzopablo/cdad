#!/usr/bin/env python3
"""cdad_suite_review.py — tramo congelado y validacion estructural (016-003).

Contrato: ``docs/specs/016-003-suite-review-tranche-1/spec.md`` (PC-1..PC-10).

Uso::

    python3 skills/cdad-cycle/scripts/cdad_suite_review.py select \
      --project-root ROOT --revision REVISION_COMPLETA --collection COLLECTION.json
    python3 skills/cdad-cycle/scripts/cdad_suite_review.py validate \
      --project-root ROOT --tranche DIR --selection SELECTION.json \
      [--registry REGISTRY.json ...]

Solo lectura: nunca modifica archivos ni ejecuta tests. Lee la coleccion y el
historial git (``select``) o el tramo materializado (``validate``) y emite un
unico objeto JSON determinista por stdout.

Codigos: ``0`` resultado valido; ``1`` insumo o historial incompatible
(diagnostico en el JSON); ``2`` uso invalido de la CLI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_INVALID = 1
EXIT_USAGE = 2

STATUS_OK = "ok"
STATUS_INVALID = "invalid"

R2_VOCABULARY = (
    "Mantener",
    "Extender",
    "Sustituir",
    "Consolidar",
    "Añadir",
    "Retirar",
)

# Raices del producto original que los experimentos no deben mutar. Los
# nodeids de la seleccion aportan ademas sus rutas de modulo exactas, vivan
# donde vivan bajo el proyecto.
PRODUCT_ROOTS = ("skills", "sources", "src", "app", "lib")
TESTS_ROOT = "tests"

SELECTION_KEYS = ("selection", "nodeids", "tranche")
AUDIT_KEYS = ("rows", "audit", "filas")

STEP_KEYS = (
    "sano_candidato",
    "sano_comparacion",
    "degradado_candidato",
    "degradado_comparacion",
    "correspondence",
)

MARKER_RE = re.compile(
    r"<!--\s*cdad:pc\s+(?P<id>[A-Za-z0-9_.-]+)\s+promise=(?P<promise>[A-Za-z0-9_.-]+)\s*-->"
)
TICK_RUN_RE = re.compile(r"`+")


# ---------------------------------------------------------------------------
# Utilidades de base (frontera: parseo y emision; sin efectos laterales).
# ---------------------------------------------------------------------------

def _emit(payload: dict[str, Any]) -> None:
    """El producto es stdout: un unico JSON determinista.

    La primera clave es siempre ``status`` (los consumidores separan el
    estado del resto del documento a partir de ella); el resto del orden es
    fijo por construccion y las listas variables se ordenan antes de emitir.
    """
    ordered: dict[str, Any] = {"status": payload.get("status")}
    for key, value in payload.items():
        if key != "status":
            ordered[key] = value
    sys.stdout.write(json.dumps(ordered, ensure_ascii=False) + "\n")


def _sorted_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(errors, key=lambda e: json.dumps(e, sort_keys=True, ensure_ascii=False))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"no existe el archivo: {path}"
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"no se pudo leer el archivo: {path} ({exc})"
    except json.JSONDecodeError as exc:
        return None, f"registro corrupto, no es JSON valido: {path} ({exc})"


def _resolve_arg(project_root: Path, given: str) -> Path:
    """Una ruta absoluta se usa tal cual; una relativa cuelga del proyecto."""
    candidate = Path(given)
    if candidate.is_absolute():
        return candidate
    return project_root / candidate


def _display(project_root: Path, path: Path) -> str:
    """Ruta reproducible: relativa al proyecto cuando es posible."""
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix() if path.is_absolute() else Path(path).as_posix()


def _inside_project(project_root: Path, rel: str) -> Path | None:
    """Resuelve un enlace documental sin salir del proyecto (symlinks incluidos)."""
    try:
        root = project_root.resolve()
        resolved = (project_root / rel).resolve()
    except OSError:
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    """Git de lectura. Devuelve None si git no esta disponible."""
    try:
        return subprocess.run(
            ["git", "-C", str(project_root), *args],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Marcadores de contrato (universo mecanico; misma regla que 016-001).
# ---------------------------------------------------------------------------

def _fence_marker(line: str) -> tuple[str, int] | None:
    stripped = line.lstrip(" \t")
    if stripped.startswith("```") or stripped.startswith("~~~"):
        char = stripped[0]
        run = len(stripped) - len(stripped.lstrip(char))
        if run >= 3:
            if char == "`" and "`" in stripped[run:]:
                return None
            return char, run
    return None


def _is_closing_fence(line: str, char: str, length: int) -> bool:
    stripped = line.strip()
    if not stripped or stripped[0] != char:
        return False
    run = len(stripped) - len(stripped.lstrip(char))
    if run < length:
        return False
    return stripped[run:].strip() == ""


def _extract_markers(contract_text: str) -> tuple[dict[str, str], list[str]]:
    """Obligaciones reales: linea cuyo contenido es exactamente el marcador,
    fuera de bloques cercados y de code spans inline."""
    found: dict[str, str] = {}
    duplicates: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    open_tick = ""
    pending: list[str] = []

    def _record(stripped: str) -> None:
        match = MARKER_RE.fullmatch(stripped)
        if match is None:
            return
        pid, promise = match.group("id"), match.group("promise")
        if pid in found:
            duplicates.append(pid)
        else:
            found[pid] = promise

    def _flush_paragraph() -> None:
        nonlocal open_tick, pending
        if open_tick != "":
            for skipped in pending:
                _record(skipped)
        open_tick = ""
        pending = []

    for line in contract_text.splitlines():
        expanded_indent = (
            line[: len(line) - len(line.lstrip(" \t"))].replace("\t", "    ")
        )
        if len(expanded_indent) > 3:
            continue
        fence = _fence_marker(line)
        if not in_fence and fence is not None:
            _flush_paragraph()
            in_fence = True
            fence_char, fence_len = fence
            continue
        if in_fence:
            if _is_closing_fence(line, fence_char, fence_len):
                in_fence = False
                fence_char, fence_len = "", 0
            continue
        stripped = line.strip()
        if stripped == "":
            _flush_paragraph()
            continue
        for run in TICK_RUN_RE.finditer(line):
            if open_tick == "":
                open_tick = run.group(0)
            elif run.group(0) == open_tick:
                open_tick = ""
        if open_tick != "":
            pending.append(stripped)
            continue
        _record(stripped)
    _flush_paragraph()
    return found, sorted(set(duplicates))


# ---------------------------------------------------------------------------
# Registros legacy por demanda (016-001, sin duplicar su formato).
# ---------------------------------------------------------------------------

def _load_registries(
    project_root: Path,
    registry_args: list[str],
    errors: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[tuple[str, str], list[dict[str, Any]]]]:
    """Carga y valida registros legacy; un registro corrupto es error.

    Devuelve (validos, indice por (contract.path, contract.sha256)).
    La forma exigida es la de 016-001: unit, contract{path,sha256},
    legacy_obligations[{id,promise,locator}]. No duplica el hogar del
    formato (contract-test-links.md): solo lo consume.
    """
    valid: list[dict[str, Any]] = []
    for given in registry_args:
        reg_path = _resolve_arg(project_root, given)
        try:
            display = _display(project_root, reg_path)
        except Exception:
            display = str(given)
        obj, err = _load_json(reg_path)
        if err is not None:
            errors.append({"file": display, "ref": display,
                           "message": f"registro corrupto en {display}: {err}"})
            continue
        if not isinstance(obj, dict):
            errors.append({"file": display, "ref": display,
                           "message": f"registro corrupto en {display}: no es un objeto"})
            continue
        unit = obj.get("unit")
        contract_ref = obj.get("contract")
        legacy = obj.get("legacy_obligations", [])
        if not isinstance(unit, str) or not unit:
            errors.append({"file": display, "ref": display,
                           "message": f"registro sin unit valida en {display}"})
            continue
        if not isinstance(contract_ref, dict):
            errors.append({"file": display, "ref": display,
                           "message": f"registro sin contract valido en {display}"})
            continue
        cpath = contract_ref.get("path")
        csha = contract_ref.get("sha256")
        if not isinstance(cpath, str) or not cpath:
            errors.append({"file": display, "ref": display,
                           "message": f"registro sin contract.path valido en {display}"})
            continue
        if not isinstance(csha, str) or not csha:
            errors.append({"file": display, "ref": display,
                           "message": f"registro sin contract.sha256 valido en {display}"})
            continue
        if legacy is None:
            legacy = []
        if not isinstance(legacy, list):
            errors.append({"file": display, "ref": display,
                           "message": f"registro con legacy_obligations no lista en {display}"})
            continue
        obligations: dict[str, str] = {}
        bad = False
        for entry in legacy:
            if not isinstance(entry, dict):
                errors.append({"file": display, "ref": display,
                               "message": f"registro con entrada legacy no objeto en {display}"})
                bad = True
                break
            lid = entry.get("id")
            promise = entry.get("promise")
            locator = entry.get("locator")
            if not all(isinstance(v, str) and v for v in (lid, promise, locator)):
                errors.append({"file": display, "ref": display,
                               "message": f"registro con entrada legacy sin id/promise/locator en {display}"})
                bad = True
                break
            assert isinstance(lid, str) and isinstance(promise, str) and isinstance(locator, str)
            if lid in obligations:
                errors.append({"file": display, "ref": display,
                               "message": f"registro con obligacion legacy duplicada {lid} en {display}"})
                bad = True
                break
            obligations[lid] = promise
        if bad:
            continue
        # Locator unico solo cuando el hash coincide y no hay mezcla:
        # si el contrato tiene marcadores reales, el error que corresponde
        # es mezcla (016-001), no localizador; se preserva el registro para
        # que la mezcla nombre registro, contrato y fila.
        if obligations:
            resolved = _inside_project(project_root, str(cpath))
            if resolved is not None and resolved.is_file():
                try:
                    actual = _sha256_file(resolved)
                except OSError:
                    actual = None
                if actual == csha:
                    try:
                        text = resolved.read_text(encoding="utf-8")
                    except (OSError, UnicodeDecodeError):
                        text = ""
                    if text:
                        markers_here, _ = _extract_markers(text)
                        if not markers_here:
                            for lid, entry in zip(
                                list(obligations.keys()),
                                [e for e in legacy if isinstance(e, dict)],
                            ):
                                loc = str(entry.get("locator"))
                                if text.count(loc) != 1:
                                    errors.append(
                                        {"file": display, "ref": str(cpath),
                                         "message": f"localizador legacy no unico para {lid} "
                                                    f"en {display} (contrato {cpath})"})
                                    bad = True
                                    break
                            if bad:
                                continue
        valid.append({
            "display": display,
            "unit": unit,
            "contract_path": str(cpath),
            "contract_sha": str(csha),
            "obligations": obligations,
        })
    index: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for reg in sorted(valid, key=lambda r: (r["contract_path"], r["contract_sha"], r["display"])):
        key = (reg["contract_path"], reg["contract_sha"])
        index.setdefault(key, []).append(reg)
    return valid, index


def _registry_has_legacy_for_markers(
    project_root: Path,
    reg: dict[str, Any],
) -> bool:
    """True si el contrato del registro tiene marcadores reales y legacy."""
    if not reg.get("obligations"):
        return False
    resolved = _inside_project(project_root, str(reg["contract_path"]))
    if resolved is None or not resolved.is_file():
        return False
    try:
        if _sha256_file(resolved) != reg["contract_sha"]:
            # Sin hash coincidente no se acredita el contenido; la mezcla
            # se juzga sobre el contenido acreditable (ver _check_row).
            # Para el chequeo global se lee igual el archivo si existe,
            # porque 016-001 prohibe mezclar por contrato, no por hash.
            pass
        text = resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    markers, _ = _extract_markers(text)
    return bool(markers)


# ---------------------------------------------------------------------------
# select — seleccion congelada (§4).
# ---------------------------------------------------------------------------

def _check_doc_ref(
    project_root: Path,
    ref: Any,
    errors: list[dict[str, Any]],
    where: str,
) -> bool:
    if not isinstance(ref, dict):
        errors.append({"file": where, "ref": where,
                       "message": f"referencia no es un objeto en {where}"})
        return False
    ok = True
    for key in ("path", "sha256", "locator"):
        value = ref.get(key)
        if not isinstance(value, str) or not value:
            errors.append({"file": where, "ref": where,
                           "message": f"referencia sin {key} valido en {where}"})
            ok = False
    if not ok:
        return False
    resolved = _inside_project(project_root, str(ref["path"]))
    if resolved is None:
        errors.append({"file": str(ref["path"]), "ref": where,
                       "message": f"referencia fuera del proyecto en {where}: {ref['path']}"})
        return False
    if not resolved.is_file():
        errors.append({"file": str(ref["path"]), "ref": where,
                       "message": f"referencia que no resuelve en {where}: {ref['path']}"})
        return False
    actual = _sha256_file(resolved)
    if actual != ref["sha256"]:
        errors.append({"file": str(ref["path"]), "ref": where,
                       "message": f"hash distinto en {where}: {ref['path']}"})
        return False
    try:
        text = resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append({"file": str(ref["path"]), "ref": where,
                       "message": f"referencia ilegible en {where}: {ref['path']} ({exc})"})
        return False
    count = text.count(str(ref["locator"]))
    if count != 1:
        errors.append({"file": str(ref["path"]), "ref": where,
                       "message": f"localizador no unico en {where}: {ref['path']} "
                                  f"(apariciones: {count})"})
        return False
    return True


def cmd_select(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root)
    if not project_root.is_dir():
        _emit({"status": STATUS_INVALID,
               "errors": [{"file": str(args.project_root), "ref": "project-root",
                           "message": f"project-root inexistente: {args.project_root}"}]})
        return EXIT_USAGE

    revision = str(args.revision)
    collection_path = _resolve_arg(project_root, str(args.collection))

    def _invalid(message: str, ref: str = "collection") -> int:
        _emit({"status": STATUS_INVALID, "revision": revision,
               "errors": [{"file": _display(project_root, collection_path),
                            "ref": ref, "message": message}]})
        return EXIT_INVALID

    try:
        raw = collection_path.read_text(encoding="utf-8")
    except OSError as exc:
        return _invalid(f"no se pudo leer la coleccion: {exc}")
    try:
        collection = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _invalid(f"coleccion corrupta, no es JSON valido ({exc})")
    if not isinstance(collection, dict):
        return _invalid("la coleccion no es un objeto")
    nodeids = collection.get("nodeids")
    if (not isinstance(nodeids, list) or not nodeids
            or not all(isinstance(n, str) and n for n in nodeids)):
        return _invalid("nodeids de la coleccion no es lista de literales no vacios")
    scope = collection.get("scope")
    if not isinstance(scope, list):
        return _invalid("coleccion sin ambito acreditable: scope no es lista")
    if list(scope) != ["tests"]:
        return _invalid(f"ambito incompatible: se exige [\"tests\"] (actual: {scope!r})")
    if collection.get("exit_code") != 0:
        return _invalid(f"coleccion fallida: no acredita existencia "
                        f"(exit_code={collection.get('exit_code')!r})")
    seen: set[str] = set()
    dups: set[str] = set()
    for nodeid in nodeids:
        if nodeid in seen:
            dups.add(nodeid)
        seen.add(nodeid)
    if dups:
        return _invalid("nodeids duplicados en la coleccion: "
                        + ", ".join(sorted(dups)))

    probe = _run_git(project_root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")
    if probe is None:
        return _invalid("git no disponible: no se puede acreditar la seleccion")
    if probe.returncode != 0:
        return _invalid(f"revision inexistente o incompatible: {revision}")
    shallow = _run_git(project_root, "rev-parse", "--is-shallow-repository")
    if shallow is not None and shallow.returncode == 0 \
            and shallow.stdout.strip() == "true":
        return _invalid("historial superficial: el clon no conserva las incorporaciones")

    modules = sorted({n.split("::", 1)[0] if "::" in n else n for n in nodeids})
    incorporations: dict[str, dict[str, Any]] = {}
    for module in modules:
        cat = _run_git(project_root, "cat-file", "-e", f"{revision}:{module}")
        if cat is None:
            return _invalid("git no disponible durante la inspeccion de modulos")
        if cat.returncode != 0:
            return _invalid(f"modulo ausente en la revision: {module}", ref=module)
        log = _run_git(project_root, "log", "--no-renames", "--diff-filter=A",
                       "--format=%ct %H", revision, "--", module)
        if log is None or log.returncode != 0:
            return _invalid(f"incorporacion no recuperable para el modulo: {module}",
                            ref=module)
        best: tuple[int, str] | None = None
        for line in log.stdout.splitlines():
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            try:
                stamp = int(parts[0])
            except ValueError:
                continue
            candidate = (stamp, parts[1].strip())
            if best is None or candidate < best:
                best = candidate
        if best is None:
            return _invalid(f"incorporacion no recuperable para el modulo: {module}",
                            ref=module)
        incorporations[module] = {"timestamp": best[0], "commit": best[1]}

    def _module_of(nodeid: str) -> str:
        return nodeid.split("::", 1)[0] if "::" in nodeid else nodeid

    ordered = sorted(nodeids,
                     key=lambda n: (-incorporations[_module_of(n)]["timestamp"],
                                    _module_of(n), n))
    total = len(nodeids)
    size = (total + 4) // 5
    selection = ordered[:size]

    _emit({
        "status": STATUS_OK,
        "revision": revision,
        "collection": {
            "arg": str(args.collection),
            "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "revision": collection.get("revision"),
            "scope": ["tests"],
        },
        "rule": "ceil(N/5) = (N+4)//5; orden por antiguedad de modulo "
                "(timestamp desc, ruta asc, nodeid asc); "
                "git log --no-renames --diff-filter=A --format='%ct %H'",
        "incorporations": incorporations,
        "total": total,
        "size": size,
        "selection": selection,
        "errors": [],
    })
    return EXIT_OK


# ---------------------------------------------------------------------------
# validate — estructura del tramo materializado (PC-3..PC-10).
# ---------------------------------------------------------------------------

def _read_selection(path: Path) -> tuple[list[str] | None, Any, str | None]:
    """Devuelve (nodeids, revision declarada, diagnostico)."""
    obj, err = _load_json(path)
    if err is not None:
        return None, None, err
    if isinstance(obj, list):
        items: Any = obj
        rev: Any = None
    elif isinstance(obj, dict):
        rev = obj.get("revision")
        items = None
        for key in SELECTION_KEYS:
            value = obj.get(key)
            if isinstance(value, list):
                items = value
                break
        if items is None:
            return None, rev, "la seleccion no trae lista literal (selection/nodeids/tranche)"
    else:
        return None, None, "la seleccion no es un objeto ni una lista"
    if not isinstance(items, list) or not all(isinstance(n, str) and n for n in items):
        return None, rev, "la seleccion no es lista de literales no vacios"
    return list(items), rev, None


def _signal(value: str) -> str:
    """Senal de deteccion de un paso: positiva, negativa o desconocida."""
    low = value.lower()
    if "fail" in low:
        return "positiva"
    if "pass" in low:
        return "negativa"
    if "no detecta" in low or "no lo detecta" in low:
        return "negativa"
    if "detecta" in low:
        return "positiva"
    return "desconocida"


def _check_row(project_root: Path, row: Any, index: int,
               selection: set[str], markers_cache: dict[str, Any],
               errors: list[dict[str, Any]],
               registries: dict[tuple[str, str], list[dict[str, Any]]] | None = None) -> str | None:
    where = f"audit.json:rows[{index}]"
    if not isinstance(row, dict):
        errors.append({"file": "audit.json", "ref": where,
                       "message": f"fila no es un objeto en {where}"})
        return None
    nodeid = row.get("nodeid")
    if not isinstance(nodeid, str) or not nodeid:
        errors.append({"file": "audit.json", "ref": where,
                       "message": f"fila sin nodeid en {where}"})
        return None
    if not isinstance(row.get("revision"), str) or not row.get("revision"):
        errors.append({"file": "audit.json", "ref": nodeid,
                       "message": f"fila sin revision congelada: {nodeid}"})
    contract = row.get("contract")
    if not isinstance(contract, dict) \
            or not isinstance(contract.get("path"), str) or not contract.get("path") \
            or not isinstance(contract.get("sha256"), str) or not contract.get("sha256"):
        errors.append({"file": "audit.json", "ref": nodeid,
                       "message": f"contrato sin path/sha256 en la fila: {nodeid}"})
    else:
        resolved = _inside_project(project_root, str(contract["path"]))
        if resolved is None or not resolved.is_file():
            errors.append({"file": str(contract["path"]), "ref": nodeid,
                           "message": f"el contrato no resuelve dentro del proyecto: "
                                      f"{contract['path']} (fila: {nodeid})"})
        elif _sha256_file(resolved) != contract["sha256"]:
            errors.append({"file": str(contract["path"]), "ref": nodeid,
                           "message": f"hash distinto del contrato {contract['path']} "
                                      f"(fila: {nodeid})"})
        else:
            try:
                text = resolved.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                errors.append({"file": str(contract["path"]), "ref": nodeid,
                               "message": f"contrato ilegible: {contract['path']} ({exc})"})
                text = ""
            if text:
                cache_key = f"{contract['path']}\x00{contract['sha256']}"
                cached = markers_cache.get(cache_key)
                if cached is None:
                    cached = _extract_markers(text)
                    markers_cache[cache_key] = cached
                obligations, dups = cached
                if dups:
                    errors.append({"file": str(contract["path"]), "ref": nodeid,
                                   "message": f"marcador duplicado en {contract['path']}: "
                                              f"{', '.join(dups)}"})
                obligation = row.get("obligation")
                if not isinstance(obligation, str) or not obligation:
                    errors.append({"file": "audit.json", "ref": nodeid,
                                   "message": f"fila sin obligacion: {nodeid}"})
                elif obligations:
                    if obligation not in obligations:
                        errors.append({"file": str(contract["path"]), "ref": nodeid,
                                       "message": f"obligacion {obligation} no resuelve contra "
                                                  f"el contrato {contract['path']} (fila: {nodeid})"})
                    else:
                        # Mezcla 016-001: legacy para un contrato con marcadores.
                        reg_index = registries or {}
                        key = (str(contract["path"]), str(contract["sha256"]))
                        for reg in reg_index.get(key, []):
                            if reg.get("obligations"):
                                errors.append(
                                    {"file": str(reg["display"]), "ref": nodeid,
                                     "message": f"mezcla no permitida: el registro "
                                                f"{reg['display']} declara legacy_obligations "
                                                f"para el contrato {contract['path']} que si "
                                                f"tiene marcadores (fila: {nodeid})"})
                else:
                    # Sin marcadores reales: resuelve solo por indice legacy.
                    reg_index = registries or {}
                    key = (str(contract["path"]), str(contract["sha256"]))
                    linked = reg_index.get(key, [])
                    if not linked:
                        errors.append({"file": str(contract["path"]), "ref": nodeid,
                                       "message": f"contrato sin marcadores sin registro "
                                                  f"enlazado para {contract['path']} "
                                                  f"(fila: {nodeid})"})
                    else:
                        have_obligation = False
                        promise_ok = False
                        for reg in sorted(linked, key=lambda r: str(r["display"])):
                            reg_obligations = reg.get("obligations") or {}
                            if obligation in reg_obligations:
                                have_obligation = True
                                row_promise = row.get("promise")
                                if isinstance(row_promise, str) and row_promise \
                                        and row_promise == reg_obligations[obligation]:
                                    promise_ok = True
                                    break
                        if not have_obligation:
                            errors.append({"file": str(contract["path"]), "ref": nodeid,
                                           "message": f"obligacion {obligation} no existe en "
                                                      f"el indice legacy para {contract['path']} "
                                                      f"(fila: {nodeid})"})
                        elif not promise_ok:
                            errors.append({"file": str(contract["path"]), "ref": nodeid,
                                           "message": f"promesa de la fila distinta de la del "
                                                      f"indice legacy para {obligation} en "
                                                      f"{contract['path']} (fila: {nodeid})"})
    if not isinstance(row.get("promise"), str) or not row.get("promise"):
        errors.append({"file": "audit.json", "ref": nodeid,
                       "message": f"fila sin promesa: {nodeid}"})
    check = row.get("check")
    if not isinstance(check, dict):
        errors.append({"file": "audit.json", "ref": nodeid,
                       "message": f"fila sin comprobacion: {nodeid}"})
    else:
        assertions = check.get("assertions")
        if (not isinstance(assertions, list) or not assertions
                or not all(isinstance(a, str) and len(a) >= 3 for a in assertions)):
            errors.append({"file": "audit.json", "ref": nodeid,
                           "message": f"comprobacion sin aserciones recuperables: {nodeid}"})
        if not isinstance(check.get("setup"), str) or not check.get("setup"):
            errors.append({"file": "audit.json", "ref": nodeid,
                           "message": f"comprobacion sin preparacion: {nodeid}"})
        helpers = check.get("helpers")
        if (not isinstance(helpers, list) or not helpers
                or not all(isinstance(h, str) and h for h in helpers)):
            errors.append({"file": "audit.json", "ref": nodeid,
                           "message": f"comprobacion sin helpers necesarios: {nodeid}"})
    consequence = row.get("consequence")
    if not isinstance(consequence, str) or len(consequence) < 8:
        errors.append({"file": "audit.json", "ref": nodeid,
                       "message": f"fila sin consecuencia concreta: {nodeid}"})
    for key in ("evidence", "references"):
        refs = row.get(key)
        if not isinstance(refs, list) or not refs:
            errors.append({"file": "audit.json", "ref": nodeid,
                           "message": f"fila sin {key} recuperable: {nodeid}"})
        else:
            for rindex, ref in enumerate(refs):
                _check_doc_ref(project_root, ref, errors, nodeid)
                _ = rindex
    disposition = row.get("disposition")
    if disposition not in R2_VOCABULARY:
        errors.append({"file": "audit.json", "ref": nodeid,
                       "message": f"disposicion fuera del vocabulario R2: "
                                  f"{disposition!r} (fila: {nodeid})"})
    if not isinstance(row.get("motive"), str) or not row.get("motive"):
        errors.append({"file": "audit.json", "ref": nodeid,
                       "message": f"fila sin motivo de la disposicion: {nodeid}"})
    uncertainties = row.get("uncertainties", [])
    if not isinstance(uncertainties, list):
        errors.append({"file": "audit.json", "ref": nodeid,
                       "message": f"incertidumbres no es lista: {nodeid}"})
    return nodeid


def _check_candidate(tranche: Path, project_root: Path, cand: Any, index: int,
                     selection: set[str], comparisons: set[str],
                     errors: list[dict[str, Any]]) -> None:
    where = f"experiments/candidates.json[{index}]"
    if not isinstance(cand, dict):
        errors.append({"file": where, "ref": where,
                       "message": f"candidato no es un objeto en {where}"})
        return
    name = None
    for key in ("candidate", "nodeid", "test"):
        value = cand.get(key)
        if isinstance(value, str) and value:
            name = value
            break
    ref = name or where
    if name is None:
        errors.append({"file": where, "ref": where,
                       "message": f"candidato sin test identificado en {where}"})
        return
    if name not in selection:
        errors.append({"file": where, "ref": name,
                       "message": f"candidato fuera del tramo seleccionado: {name}"})
    for key in ("hypothesis", "defect", "justification"):
        value = cand.get(key)
        if not isinstance(value, str) or len(value) < 8:
            errors.append({"file": where, "ref": name,
                           "message": f"candidato sin {key} concreto: {name}"})
    if not isinstance(cand.get("promise"), str) or not cand.get("promise"):
        errors.append({"file": where, "ref": name,
                       "message": f"candidato sin promesa: {name}"})
    comparison = cand.get("comparison")
    if (not isinstance(comparison, list) or not comparison
            or not all(isinstance(c, str) and c for c in comparison)):
        errors.append({"file": where, "ref": name,
                       "message": f"candidato sin comparacion literal: {name}"})
    else:
        comparisons.update(c for c in comparison if isinstance(c, str))
        if name in comparison:
            errors.append({"file": where, "ref": name,
                           "message": f"la comparacion incluye al propio candidato: {name}"})
    revisions = cand.get("revisions")
    if (not isinstance(revisions, dict)
            or not isinstance(revisions.get("healthy"), str)
            or not revisions.get("healthy")
            or not isinstance(revisions.get("degraded"), str)
            or not revisions.get("degraded")):
        errors.append({"file": where, "ref": name,
                       "message": f"candidato sin revisiones sana/degradada: {name}"})
    elif revisions.get("healthy") == revisions.get("degraded"):
        errors.append({"file": where, "ref": name,
                       "message": f"revisiones sana y degradada identicas: {name}"})
    if not isinstance(cand.get("environment"), str) or not cand.get("environment"):
        errors.append({"file": where, "ref": name,
                       "message": f"candidato sin entorno declarado: {name}"})
    commands = cand.get("commands")
    if (not isinstance(commands, list) or not commands
            or not all(isinstance(c, str) and c for c in commands)):
        errors.append({"file": where, "ref": name,
                       "message": f"candidato sin comandos recuperables: {name}"})
    budget = cand.get("budget")
    if (not isinstance(budget, dict) or budget.get("max_attempts") is None
            or not isinstance(budget.get("stop_condition"), str)
            or not budget.get("stop_condition")):
        errors.append({"file": where, "ref": name,
                       "message": f"candidato sin presupuesto y condicion de parada: {name}"})
    steps = cand.get("steps")
    if not isinstance(steps, dict):
        errors.append({"file": where, "ref": name,
                       "message": f"candidato sin resultado de los pasos: {name}"})
        steps = {}
    else:
        for key in STEP_KEYS:
            value = steps.get(key)
            if not isinstance(value, str) or not value:
                errors.append({"file": where, "ref": name,
                               "message": f"candidato sin paso {key}: {name}"})
    classification = cand.get("classification")
    if not isinstance(classification, str) or not classification:
        errors.append({"file": where, "ref": name,
                       "message": f"candidato sin clasificacion acotada: {name}"})
    else:
        low = classification.lower()
        if "universal" in low:
            errors.append({"file": where, "ref": name,
                           "message": f"la clasificacion presenta el resultado acotado "
                                      f"como si autorizara poda: {name}"})
        elif "diferencial" in low:
            cand_sig = _signal(str(steps.get("degradado_candidato", "")))
            comp_sig = _signal(str(steps.get("degradado_comparacion", "")))
            if cand_sig != "positiva" or comp_sig != "negativa":
                errors.append({"file": where, "ref": name,
                               "message": f"aporte diferencial sin contraejemplo: el candidato "
                                          f"no detecta en solitario ({name})"})
    evidence = cand.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append({"file": where, "ref": name,
                       "message": f"candidato sin evidencia: {name}"})
    else:
        for entry in evidence:
            if isinstance(entry, str):
                if not entry:
                    errors.append({"file": where, "ref": name,
                                   "message": f"candidato con evidencia vacia: {name}"})
                    continue
                found = tranche / entry
                if not found.is_file():
                    alt = project_root / entry
                    if not alt.is_file():
                        errors.append({"file": where, "ref": name,
                                       "message": f"evidencia del candidato no resuelve: "
                                                  f"{entry} ({name})"})
            else:
                _check_doc_ref(project_root, entry, errors, name)


def _check_costs(costs: Any, selection: set[str], comparisons: set[str],
                 errors: list[dict[str, Any]]) -> None:
    if not isinstance(costs, dict):
        errors.append({"file": "costs.json", "ref": "costs",
                       "message": "costs.json no es un objeto"})
        return
    activities = costs.get("activities")
    if not isinstance(activities, list) or not activities:
        errors.append({"file": "costs.json", "ref": "activities",
                       "message": "costs.json sin actividades observadas"})
        return
    allowed = set(selection) | set(comparisons)
    for index, act in enumerate(activities):
        where = f"costs.json:activities[{index}]"
        if not isinstance(act, dict):
            errors.append({"file": "costs.json", "ref": where,
                           "message": f"actividad no es un objeto en {where}"})
            continue
        for key in ("session", "role", "scope"):
            if not isinstance(act.get(key), str) or not act.get(key):
                errors.append({"file": "costs.json", "ref": where,
                               "message": f"actividad sin {key} en {where}"})
        covered: list[str] = []
        for key in ("nodeids", "candidates"):
            value = act.get(key)
            if isinstance(value, list):
                covered.extend([v for v in value if isinstance(v, str) and v])
        if not covered:
            errors.append({"file": "costs.json", "ref": where,
                           "message": f"actividad sin nodeids ni candidatos en {where}"})
        else:
            for item in covered:
                if item not in allowed:
                    errors.append({"file": "costs.json", "ref": where,
                                   "message": f"actividad fuera del alcance del tramo "
                                              f"en {where}: {item}"})
        commands = act.get("commands")
        if not isinstance(commands, list) or not commands:
            errors.append({"file": "costs.json", "ref": where,
                           "message": f"actividad sin comandos en {where}"})
        else:
            for cmd in commands:
                if (not isinstance(cmd, dict)
                        or not isinstance(cmd.get("command"), str)
                        or not cmd.get("command")
                        or not isinstance(cmd.get("exit_code"), int)
                        or isinstance(cmd.get("exit_code"), bool)):
                    errors.append({"file": "costs.json", "ref": where,
                                   "message": f"comando sin invocacion ni salida en {where}"})
        tokens = act.get("tokens")
        if tokens is None:
            errors.append({"file": "costs.json", "ref": where,
                           "message": f"actividad sin metricas: ausentes no es cero "
                                      f"en {where}"})
        elif isinstance(tokens, str):
            if "no disponibles" not in tokens.lower():
                errors.append({"file": "costs.json", "ref": where,
                               "message": f"metricas sin valor ni marca de ausencia "
                                          f"en {where}"})
        elif isinstance(tokens, dict):
            if _is_number(tokens.get("input")) and _is_number(tokens.get("output")):
                pass
            elif any(isinstance(v, str) and "no disponibles" in v.lower()
                     for v in tokens.values()):
                pass
            else:
                errors.append({"file": "costs.json", "ref": where,
                               "message": f"metricas sin entrada/salida ni marca de "
                                          f"ausencia en {where}"})
        else:
            errors.append({"file": "costs.json", "ref": where,
                           "message": f"metricas con forma desconocida en {where}"})
        if not isinstance(act.get("started"), str) or not act.get("started"):
            errors.append({"file": "costs.json", "ref": where,
                           "message": f"actividad sin inicio observado en {where}"})
        if not isinstance(act.get("ended"), str) or not act.get("ended"):
            errors.append({"file": "costs.json", "ref": where,
                           "message": f"actividad sin fin observado en {where}"})
        if not _is_number(act.get("duration_s")):
            errors.append({"file": "costs.json", "ref": where,
                           "message": f"actividad sin duracion observada en {where}"})
    totals = costs.get("totals")
    if (not isinstance(totals, dict)
            or not _is_number(totals.get("elapsed_s"))
            or not _is_number(totals.get("aggregated_s"))
            or not _is_number(totals.get("commands_s"))):
        errors.append({"file": "costs.json", "ref": "totals",
                       "message": "costs.json sin totales reconstruidos "
                                  "(elapsed/aggregated/commands)"})
    projection = costs.get("projection")
    if not isinstance(projection, dict):
        errors.append({"file": "costs.json", "ref": "projection",
                       "message": "costs.json sin proyeccion"})
        return
    if not isinstance(projection.get("formula"), str) or not projection.get("formula"):
        errors.append({"file": "costs.json", "ref": "projection",
                       "message": "proyeccion sin formula"})
    observed = projection.get("observed")
    if not isinstance(observed, dict) or not observed:
        errors.append({"file": "costs.json", "ref": "projection",
                       "message": "proyeccion sin cantidades observadas"})
    assumptions = projection.get("assumptions")
    if (not isinstance(assumptions, list) or not assumptions
            or not all(isinstance(a, str) and a for a in assumptions)):
        errors.append({"file": "costs.json", "ref": "projection",
                       "message": "proyeccion sin supuestos declarados"})
    else:
        joined = " ".join([str(projection.get("formula", ""))] + assumptions).lower()
        if "aleatoria" in joined and "no " not in joined and "sin " not in joined:
            errors.append({"file": "costs.json", "ref": "projection",
                           "message": "la proyeccion presenta el tramo mas nuevo "
                                      "como muestra del resto"})


def _check_decision(text: str | None, errors: list[dict[str, Any]]) -> None:
    if text is None:
        errors.append({"file": "decision.md", "ref": "decision",
                       "message": "falta decision.md en el tramo"})
        return
    low = text.lower()
    for key in ("responsable", "autoridad", "motivo", "evidencia", "alcance"):
        if key not in low:
            errors.append({"file": "decision.md", "ref": "decision",
                           "message": f"decision sin {key} explicito"})
    if "decisi" not in low:
        errors.append({"file": "decision.md", "ref": "decision",
                       "message": "decision sin veredicto explicito"})
    if not any(v in low for v in ("continu", "deten", "detie", "modific", "cambi")):
        errors.append({"file": "decision.md", "ref": "decision",
                       "message": "decision sin curso de accion (continuar, modificar, detener)"})
    for pending in ("pendiente de definir", "queda pendiente",
                    "pendiente de decision", "pendiente de decisión"):
        if pending in low:
            errors.append({"file": "decision.md", "ref": "decision",
                           "message": f"decision pendiente: {pending}"})


def _check_manifest(tranche: Path, manifest: Any,
                    errors: list[dict[str, Any]]) -> None:
    if not isinstance(manifest, dict):
        errors.append({"file": "experiments/manifest.json", "ref": "manifest",
                       "message": "manifest sin copia ni workspace declarados"})
        return
    copy = manifest.get("copy")
    workspace = manifest.get("workspace")
    if not isinstance(copy, str) or not copy or copy in (".", "/"):
        errors.append({"file": "experiments/manifest.json", "ref": "manifest",
                       "message": "copia de experimentos sin declarar"})
    if not isinstance(workspace, str) or not workspace or workspace in (".", "/"):
        errors.append({"file": "experiments/manifest.json", "ref": "manifest",
                       "message": "workspace de experimentos sin declarar"})
    if (isinstance(copy, str) and copy
            and isinstance(workspace, str) and workspace and copy == workspace):
        errors.append({"file": "experiments/manifest.json", "ref": "manifest",
                       "message": "copia y workspace identicos: no hay confinamiento"})
    logs = manifest.get("logs")
    if not isinstance(logs, list) or not logs \
            or not all(isinstance(l, str) and l for l in logs):
        errors.append({"file": "experiments/manifest.json", "ref": "manifest",
                       "message": "manifest sin bitacoras declaradas"})
    else:
        for entry in logs:
            if not (tranche / entry).is_file():
                errors.append({"file": "experiments/manifest.json", "ref": entry,
                               "message": f"bitacora declarada que no existe: {entry}"})


def _interesting_files(project_root: Path, tranche: Path, selection_path: Path,
                       selection: list[str]) -> list[Path]:
    """Fuentes del original cuyo cambio posterior al tramo invalida PC-9."""
    wanted: list[Path] = []
    for dirname in (TESTS_ROOT, *PRODUCT_ROOTS):
        base = project_root / dirname
        if not base.is_dir():
            continue
        try:
            for path in sorted(base.rglob("*")):
                if path.is_file() and not path.is_symlink():
                    wanted.append(path)
                elif path.is_symlink():
                    try:
                        if path.resolve().is_file():
                            wanted.append(path)
                    except OSError:
                        continue
        except OSError:
            continue
    for nodeid in selection:
        module = nodeid.split("::", 1)[0] if "::" in nodeid else nodeid
        candidate = project_root / module
        try:
            if candidate.is_file() and candidate not in wanted:
                wanted.append(candidate)
        except OSError:
            continue
    try:
        tranche_resolved = tranche.resolve()
    except OSError:
        tranche_resolved = tranche
    try:
        selection_resolved = selection_path.resolve()
    except OSError:
        selection_resolved = selection_path
    kept: list[Path] = []
    for path in wanted:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved == selection_resolved:
            continue
        try:
            resolved.relative_to(tranche_resolved)
            continue
        except ValueError:
            pass
        kept.append(path)
    return kept


def _check_original_intact(project_root: Path, tranche: Path, selection_path: Path,
                           selection: list[str],
                           errors: list[dict[str, Any]]) -> None:
    """PC-9: el original permanece intacto durante los experimentos.

    Con arbol git disponible, el arbitro es el estado del checkout
    restringido a pruebas y producto. Sin git (origen no versionado), el
    ancla es la congelacion: ninguna fuente revisada puede ser posterior al
    archivo mas nuevo del tramo.
    """
    interesting = _interesting_files(project_root, tranche, selection_path, selection)
    probe = _run_git(project_root, "rev-parse", "--is-inside-work-tree")
    if probe is not None and probe.returncode == 0 and probe.stdout.strip() == "true":
        top_proc = _run_git(project_root, "rev-parse", "--show-toplevel")
        top = Path(top_proc.stdout.strip()) if top_proc and top_proc.returncode == 0 \
            and top_proc.stdout.strip() else project_root
        status = _run_git(project_root, "status", "--porcelain")
        if status is not None and status.returncode == 0:
            try:
                tranche_resolved = tranche.resolve()
            except OSError:
                tranche_resolved = tranche
            try:
                selection_resolved = selection_path.resolve()
            except OSError:
                selection_resolved = selection_path
            interesting_abs = set()
            for path in interesting:
                try:
                    interesting_abs.add(path.resolve())
                except OSError:
                    continue
            dirty: list[str] = []
            for line in status.stdout.splitlines():
                entry = line[3:] if len(line) > 3 else line.strip()
                if " -> " in entry:
                    entry = entry.split(" -> ", 1)[1]
                entry = entry.strip().strip('"')
                if not entry:
                    continue
                try:
                    abs_entry = (top / entry).resolve()
                except OSError:
                    continue
                if abs_entry == selection_resolved:
                    continue
                try:
                    abs_entry.relative_to(tranche_resolved)
                    continue
                except ValueError:
                    pass
                if abs_entry in interesting_abs:
                    dirty.append(_display(project_root, abs_entry))
                else:
                    for base in interesting_abs:
                        if base.is_dir() and abs_entry != base:
                            try:
                                abs_entry.relative_to(base)
                                dirty.append(_display(project_root, abs_entry))
                                break
                            except ValueError:
                                continue
            for hit in sorted(set(dirty)):
                errors.append({"file": hit, "ref": "checkout",
                               "message": f"cambio en el checkout original "
                                          f"durante los experimentos: {hit}"})
            return
    try:
        tranche_files = [p for p in tranche.rglob("*") if p.is_file()]
    except OSError:
        tranche_files = []
    if not tranche_files or not interesting:
        return
    newest = 0
    for path in tranche_files:
        try:
            stamp = path.stat().st_mtime_ns
        except OSError:
            continue
        if stamp > newest:
            newest = stamp
    if newest == 0:
        return
    for path in sorted(interesting):
        try:
            stamp = path.stat().st_mtime_ns
        except OSError:
            continue
        if stamp > newest:
            errors.append({"file": _display(project_root, path), "ref": "checkout",
                           "message": f"cambio en el checkout original durante "
                                      f"los experimentos: {_display(project_root, path)}"})


def cmd_validate(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root)
    if not project_root.is_dir():
        _emit({"status": STATUS_INVALID,
               "errors": [{"file": str(args.project_root), "ref": "project-root",
                           "message": f"project-root inexistente: {args.project_root}"}]})
        return EXIT_USAGE

    tranche = _resolve_arg(project_root, str(args.tranche))
    selection_path = _resolve_arg(project_root, str(args.selection))

    def _base_invalid(message: str, where: str) -> int:
        _emit({"status": STATUS_INVALID,
               "errors": [{"file": where, "ref": where, "message": message}],
               "delivery": _delivery(0, 0),
               "limits": _limits()})
        return EXIT_INVALID

    if not tranche.is_dir():
        return _base_invalid(f"tramo inexistente: {args.tranche}", "tranche")
    selection, _selection_rev, sel_err = _read_selection(selection_path)
    if sel_err is not None or selection is None:
        return _base_invalid(f"seleccion ilegible: {sel_err}", "selection")
    if len(set(selection)) != len(selection):
        dups = sorted({n for n in selection if selection.count(n) > 1})
        return _base_invalid("seleccion con nodeids duplicados: " + ", ".join(dups),
                             "selection")
    selection_set = set(selection)

    errors: list[dict[str, Any]] = []

    registry_args: list[str] = list(getattr(args, "registry", []) or [])
    _, registry_index = _load_registries(project_root, registry_args, errors)
    # Mezcla global 016-001: legacy para un contrato con marcadores reales.
    # Nombra registro y contrato; las filas afectadas agregan su ref abajo.
    for key, regs in sorted(registry_index.items()):
        for reg in regs:
            if _registry_has_legacy_for_markers(project_root, reg):
                errors.append(
                    {"file": str(reg["display"]), "ref": str(reg["contract_path"]),
                     "message": f"mezcla no permitida: el registro {reg['display']} "
                                f"declara legacy_obligations para el contrato "
                                f"{reg['contract_path']} que si tiene marcadores"})

    audit_path = tranche / "audit.json"
    audit_obj, audit_err = _load_json(audit_path)
    rows: list[Any] = []
    if audit_err is not None:
        errors.append({"file": "audit.json", "ref": "audit",
                       "message": audit_err})
    elif not isinstance(audit_obj, dict):
        errors.append({"file": "audit.json", "ref": "audit",
                       "message": "audit.json no es un objeto"})
    else:
        found = None
        for key in AUDIT_KEYS:
            if isinstance(audit_obj.get(key), list):
                found = audit_obj.get(key)
                break
        if found is None:
            errors.append({"file": "audit.json", "ref": "audit",
                           "message": "audit.json sin filas (rows/audit/filas)"})
        else:
            rows = found

    markers_cache: dict[str, Any] = {}
    seen_rows: set[str] = set()
    row_nodeids: list[str] = []
    for index, row in enumerate(rows):
        nodeid = _check_row(project_root, row, index, selection_set,
                            markers_cache, errors, registry_index)
        if nodeid is not None:
            row_nodeids.append(nodeid)
            if nodeid in seen_rows:
                errors.append({"file": "audit.json", "ref": nodeid,
                               "message": f"fila duplicada para el nodeid: {nodeid}"})
            seen_rows.add(nodeid)
    for missing in sorted(selection_set - set(row_nodeids)):
        errors.append({"file": "audit.json", "ref": missing,
                       "message": f"nodeid seleccionado sin fila de auditoria: {missing}"})
    for extra in sorted(set(row_nodeids) - selection_set):
        errors.append({"file": "audit.json", "ref": extra,
                       "message": f"fila fuera del tramo seleccionado: {extra}"})

    comparisons: set[str] = set()
    candidates_path = tranche / "experiments" / "candidates.json"
    candidates_obj, candidates_err = _load_json(candidates_path)
    if candidates_err is not None:
        errors.append({"file": "experiments/candidates.json", "ref": "candidates",
                       "message": candidates_err})
    elif not isinstance(candidates_obj, list):
        errors.append({"file": "experiments/candidates.json", "ref": "candidates",
                       "message": "candidates.json no es una lista"})
    else:
        for index, cand in enumerate(candidates_obj):
            _check_candidate(tranche, project_root, cand, index,
                             selection_set, comparisons, errors)

    costs_path = tranche / "costs.json"
    costs_obj, costs_err = _load_json(costs_path)
    if costs_err is not None:
        errors.append({"file": "costs.json", "ref": "costs",
                       "message": costs_err})
    else:
        _check_costs(costs_obj, selection_set, comparisons, errors)

    decision_path = tranche / "decision.md"
    try:
        decision_text: str | None = decision_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        decision_text = None
    _check_decision(decision_text, errors)

    manifest_path = tranche / "experiments" / "manifest.json"
    manifest_obj, manifest_err = _load_json(manifest_path)
    if manifest_err is not None:
        errors.append({"file": "experiments/manifest.json", "ref": "manifest",
                       "message": manifest_err})
    else:
        _check_manifest(tranche, manifest_obj, errors)

    _check_original_intact(project_root, tranche, selection_path, selection, errors)

    if errors:
        _emit({"status": STATUS_INVALID,
               "selection": {"total": len(selection), "size": len(selection)},
               "rows": len(row_nodeids),
               "errors": _sorted_errors(errors),
               "delivery": _delivery(len(row_nodeids), 0),
               "limits": _limits()})
        return EXIT_INVALID
    _emit({"status": STATUS_OK,
           "selection": {"total": len(selection), "size": len(selection)},
           "rows": len(row_nodeids),
           "candidates": len(candidates_obj) if isinstance(candidates_obj, list) else 0,
           "errors": [],
           "delivery": _delivery(len(row_nodeids),
                                 len(candidates_obj)
                                 if isinstance(candidates_obj, list) else 0),
           "limits": _limits()})
    return EXIT_OK


def _delivery(rows: int, candidates: int) -> dict[str, str]:
    return {
        "estructural": f"control estructural: {rows} filas y {candidates} candidatos "
                       "con forma, vinculos y costos verificados; original intacto",
        "ejecucion": "ejecucion real registrada: comandos, resultados y limites "
                     "recuperables en el tramo; la herramienta no ejecuta pruebas",
        "revision": "revision semantica independiente: vinculos, correspondencia "
                    "y decision quedan para contraste independiente; ninguna "
                    "clasificacion autoriza poda",
    }


def _limits() -> list[str]:
    return [
        "estructural: declara ambito y limites a partir de entradas identificadas; "
        "no acredita pertinencia semantica ni sensibilidad de los experimentos",
        "reproducible: mismos insumos producen mismos bytes; sin hora, rutas fuera "
        "del proyecto ni identificadores aleatorios",
        "los experimentos pertenecen a la copia declarada; el original permanece "
        "intacto; sin git disponible la intactitud se ancla a la congelacion",
    ]


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdad_suite_review.py",
        description="Tramo congelado y validacion estructural de la revision "
                    "de suite (016-003). Solo lectura.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_select = sub.add_parser("select", help="Seleccion congelada (§4).")
    p_select.add_argument("--project-root", required=True)
    p_select.add_argument("--revision", required=True)
    p_select.add_argument("--collection", required=True)
    p_select.set_defaults(func=cmd_select)

    p_validate = sub.add_parser("validate", help="Estructura del tramo (PC-3..PC-10).")
    p_validate.add_argument("--project-root", required=True)
    p_validate.add_argument("--tranche", required=True)
    p_validate.add_argument("--selection", required=True)
    p_validate.add_argument("--registry", action="append", default=[],
                            dest="registry",
                            help="Registro legacy 016-001 (repetible) para "
                                 "contratos sin marcadores.")
    p_validate.set_defaults(func=cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
