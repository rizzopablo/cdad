#!/usr/bin/env python3
"""cdad_contract_links.py — validate contract-test link registries (016-001).

Contract: ``docs/specs/016-001-contract-test-link/spec.md`` (PC-1..PC-8).

Usage::

    python3 cdad_contract_links.py validate \
      --project-root ROOT --registry REGISTRY --collection CURRENT.json \
      [--baseline BASE.json]

    python3 cdad_contract_links.py gap-report \
      --project-root ROOT --state STATE.json \
      [--registry UNIT=REGISTRY.json ...] [--collection CURRENT.json] \
      [--exclusions EXCLUSIONS.json]

Read-only: never modifies files, never executes tests. It only reads the
registry, the approved contract, the referenced documents and the collection
artifacts produced by the project's declared runner, and emits one
deterministic JSON object on stdout.

Exit codes: ``0`` no defects inside the declared scope, or no registry
configured (``not_configured``); ``1`` invalid data, broken references, gaps
or new unlinked nodeids; ``2`` invalid CLI usage.

The ``gap-report`` subcommand (016-002) emits a reproducible coverage-gap
report from the CDAD state, explicit registries, an optional collection and
optional exclusions. Exit codes: ``0`` report produced (it may list gaps,
exclusions or non-indexed contracts); ``1`` invalid data or broken
references (explicitly partial result); ``2`` invalid CLI usage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_INVALID = 1
EXIT_USAGE = 2

STATUS_OK = "ok"
STATUS_INVALID = "invalid"
STATUS_NOT_CONFIGURED = "not_configured"

MARKER_RE = re.compile(
    r"<!--\s*cdad:pc\s+(?P<id>[A-Za-z0-9_.-]+)\s+promise=(?P<promise>[A-Za-z0-9_.-]+)\s*-->"
)

NO_NEW_CHECK = "tests nuevos no comprobados"
NO_REGISTRY_MSG = "sin registro de vínculos declarado"
SCOPE_LIMITS = (
    "Estructural: declara su ámbito y sus límites; no acredita ejecución, "
    "ni pertinencia semántica, ni sensibilidad, ni aprobación."
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside_project(project_root: Path, candidate: Path) -> Path | None:
    """Resolve symlinks; return the resolved path iff it stays in the project."""
    try:
        root = project_root.resolve()
        resolved = (project_root / candidate).resolve()
    except OSError:
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def _error_belongs_to_link(err_where: str, link_where: str) -> bool:
    """True if a doc-reference error belongs to the given link.

    Exact match or dot-prefixed child (``links[1].evidence[0]`` belongs
    to ``links[1]``); a plain prefix would confuse ``links[1]`` with
    ``links[10]``.
    """
    return err_where == link_where or err_where.startswith(link_where + ".")


def _emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, sort_keys=True, ensure_ascii=False))
    sys.stdout.write("\n")


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"no existe el archivo: {path}"
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"no se pudo leer el archivo: {path} ({exc})"
    except json.JSONDecodeError as exc:
        return None, f"registro corrupto, no es JSON válido: {path} ({exc})"


def _check_doc_ref(
    project_root: Path,
    ref: Any,
    errors: list[dict[str, Any]],
    where: str,
) -> bool:
    if not isinstance(ref, dict):
        errors.append({"code": "bad_reference", "where": where,
                       "message": f"referencia no es un objeto en {where}"})
        return False
    ok = True
    for key in ("path", "sha256", "locator"):
        value = ref.get(key)
        if not isinstance(value, str) or not value:
            errors.append({"code": "bad_reference", "where": where,
                           "message": f"referencia sin {key} válido en {where}"})
            ok = False
    if not ok:
        return False
    resolved = _inside_project(project_root, Path(ref["path"]))
    if resolved is None:
        errors.append({"code": "broken_reference", "where": where,
                       "message": (
                           f"referencia fuera del proyecto en {where}: "
                           f"{ref['path']}"
                       )})
        return False
    if not resolved.is_file():
        errors.append({"code": "broken_reference", "where": where,
                       "message": (
                           f"referencia que no resuelve en {where}: "
                           f"{ref['path']}"
                       )})
        return False
    actual = _sha256_file(resolved)
    if actual != ref["sha256"]:
        errors.append({"code": "hash_mismatch", "where": where,
                       "message": (
                           f"hash distinto en {where}: {ref['path']} "
                           f"(esperado {ref['sha256']}, actual {actual})"
                       )})
        return False
    try:
        text = resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append({"code": "broken_reference", "where": where,
                       "message": (
                           f"referencia ilegible en {where}: {ref['path']} ({exc})"
                       )})
        return False
    locator = ref["locator"]
    count = text.count(locator)
    if count != 1:
        errors.append({"code": "broken_reference", "where": where,
                       "message": (
                           f"locator no único en {where}: {ref['path']} "
                           f"(apariciones: {count})"
                       )})
        return False
    return True


TICK_RUN_RE = re.compile(r"`+")


def _fence_marker(line: str) -> tuple[str, int] | None:
    """Return (fence_char, run_length) if the line opens a fenced block.

    Fences are runs of at least three backticks or three tildes; an info
    string may follow the run (for backtick fences the info string
    itself holds no backticks). The caller filters out indented code
    lines first, so up to three leading spaces may precede the run.
    """
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
    """A closing fence uses the same char, at least the opening length,
    and contains nothing else except whitespace."""
    stripped = line.strip()
    if not stripped or stripped[0] != char:
        return False
    run = len(stripped) - len(stripped.lstrip(char))
    if run < length:
        return False
    return stripped[run:].strip() == ""


def _extract_markers(contract_text: str) -> tuple[dict[str, str], list[str]]:
    """Return ({id: promise}, duplicate_ids) for real markers only.

    A real marker is a line whose content is exactly the comment
    (whitespace around is allowed), outside fenced code blocks
    (``` and ~~~, info strings allowed) and outside inline code spans.
    Examples in prose — inline or fenced — never form obligations.
    """
    found: dict[str, str] = {}
    duplicates: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    open_tick = ""  # backtick run opening a multi-line inline code span
    pending: list[str] = []  # stripped lines skipped inside the current paragraph

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
        """End of paragraph (blank line, fence boundary or EOF).

        Inline code spans never cross a paragraph break: a span still
        open here is unbalanced, so its backticks are literal text and
        the skipped lines of this paragraph count again.
        """
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
            continue  # indented code block: never a real marker
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
        # Track multi-line inline code spans: a backtick run opens a span
        # closed only by a run of the same length. A bare marker line
        # inside such a span is an example, not an obligation.
        for run in TICK_RUN_RE.finditer(line):
            if open_tick == "":
                open_tick = run.group(0)
            elif run.group(0) == open_tick:
                open_tick = ""
        if open_tick != "":
            # Ends inside an inline code span (opened here or above). A
            # bare marker line here is still example text unless the
            # paragraph ends unbalanced (handled in _flush_paragraph).
            pending.append(stripped)
            continue
        # Exactness excludes prose embedding and single-line spans: any
        # extra character (text or backticks) breaks the fullmatch.
        _record(stripped)
    _flush_paragraph()
    return found, sorted(set(duplicates))


def cmd_validate(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root)
    if not project_root.is_dir():
        _emit({"status": STATUS_INVALID,
               "errors": [{"code": "usage", "message": (
                   f"project-root inexistente: {args.project_root}")}]})
        return EXIT_USAGE

    registry_arg = Path(args.registry)
    registry_path = (
        registry_arg
        if registry_arg.is_absolute()
        else (project_root / registry_arg)
    )
    if not registry_path.exists():
        _emit({"status": STATUS_NOT_CONFIGURED,
               "registry": str(args.registry),
               "message": f"{NO_REGISTRY_MSG}: {args.registry}",
               "limits": [SCOPE_LIMITS]})
        return EXIT_OK

    errors: list[dict[str, Any]] = []

    registry, err = _load_json(registry_path)
    if err is not None:
        errors.append({"code": "corrupt_registry",
                       "message": f"{err} ({registry_path})"})
        _emit({"status": STATUS_INVALID,
               "registry": str(args.registry),
               "scope": [],
               "limits": [SCOPE_LIMITS],
               "gaps": [],
               "gaps_by_promise": {},
               "new_unlinked": [],
               "errors": sorted(errors, key=lambda e: json.dumps(e, sort_keys=True))})
        return EXIT_INVALID
    if not isinstance(registry, dict):
        errors.append({"code": "corrupt_registry",
                       "message": f"el registro no es un objeto: {registry_path}"})
        _emit({"status": STATUS_INVALID,
               "registry": str(args.registry),
               "scope": [],
               "limits": [SCOPE_LIMITS],
               "gaps": [],
               "gaps_by_promise": {},
               "new_unlinked": [],
               "errors": errors})
        return EXIT_INVALID

    unit = registry.get("unit")
    if not isinstance(unit, str) or not unit:
        errors.append({"code": "bad_registry", "message": "unit vacío"})
    links = registry.get("links")
    if not isinstance(links, list):
        errors.append({"code": "bad_registry",
                       "message": "links no es una lista"})
        links = []
    contract_ref = registry.get("contract")
    contract_path_s: str | None = None
    contract_sha: str | None = None
    if not isinstance(contract_ref, dict):
        errors.append({"code": "bad_registry",
                       "message": "contract no es un objeto"})
    else:
        contract_path_s = contract_ref.get("path")
        contract_sha = contract_ref.get("sha256")
        if not isinstance(contract_path_s, str) or not contract_path_s:
            errors.append({"code": "bad_registry",
                           "message": "contract.path vacío"})
            contract_path_s = None
        if not isinstance(contract_sha, str) or not contract_sha:
            errors.append({"code": "bad_registry",
                           "message": "contract.sha256 vacío"})
            contract_sha = None
    legacy = registry.get("legacy_obligations")

    # --- contract resolution + obligations universe -------------------------
    obligations: dict[str, str] = {}
    markers_found: dict[str, str] = {}
    contract_text: str | None = None
    has_legacy_index = isinstance(legacy, list) and len(legacy) > 0
    if contract_path_s is not None and contract_sha is not None:
        resolved_contract = _inside_project(project_root, Path(contract_path_s))
        if resolved_contract is None or not resolved_contract.is_file():
            errors.append({"code": "broken_contract",
                           "message": (
                               f"el contrato no resuelve: {contract_path_s} "
                               f"(debe permanecer dentro del proyecto)"
                           )})
        else:
            actual_sha = _sha256_file(resolved_contract)
            if actual_sha != contract_sha:
                linked_pcs = sorted({
                    str(pid)
                    for link in links if isinstance(link, dict)
                    for pid in (link.get("pc_ids") or [])
                    if isinstance(pid, str)
                })
                errors.append({"code": "hash_mismatch",
                               "message": (
                                   f"hash distinto del contrato {contract_path_s} "
                                   f"(esperado {contract_sha}, actual {actual_sha}); "
                                   f"vínculos afectados: "
                                   f"{', '.join(linked_pcs) if linked_pcs else 'ninguno'}"
                               )})
            else:
                try:
                    contract_text = resolved_contract.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    errors.append({"code": "broken_contract",
                                   "message": (
                                       f"contrato ilegible: {contract_path_s} ({exc})"
                                   )})
    if contract_text is not None:
        markers, duplicates = _extract_markers(contract_text)
        markers_found = markers
        for dup in duplicates:
            errors.append({"code": "duplicate_marker",
                           "message": (
                               f"marcador duplicado en el contrato "
                               f"{contract_path_s}: {dup}"
                           )})
        if markers and has_legacy_index:
            errors.append({"code": "mixed_index",
                           "message": (
                               "no se mezclan marcadores e índice legacy "
                               f"para {contract_path_s}"
                           )})
        elif markers:
            obligations = markers
        elif isinstance(legacy, list) and legacy:
            for entry in legacy:
                if not isinstance(entry, dict):
                    errors.append({"code": "bad_legacy",
                                   "message": "entrada legacy no es un objeto"})
                    continue
                lid = entry.get("id")
                promise = entry.get("promise")
                locator = entry.get("locator")
                if not all(isinstance(v, str) and v for v in (lid, promise, locator)):
                    errors.append({"code": "bad_legacy",
                                   "message": (
                                       "entrada legacy sin id/promise/locator "
                                       "válidos"
                                   )})
                    continue
                count = contract_text.count(locator)
                if count != 1:
                    errors.append({"code": "broken_legacy_locator",
                                   "message": (
                                       f"locator legacy no único para {lid} "
                                       f"(apariciones: {count})"
                                   )})
                    continue
                if lid in obligations:
                    errors.append({"code": "duplicate_legacy",
                                   "message": f"obligación legacy duplicada: {lid}"})
                else:
                    obligations[lid] = promise
        if (
            contract_text is not None
            and not obligations
            and not markers_found
            and not has_legacy_index
        ):
            errors.append({"code": "no_obligations",
                           "message": (
                               f"el contrato {contract_path_s} no declara "
                               "obligaciones: cero obligaciones (sin "
                               "marcadores ni índice legacy); el registro "
                               "presente sin vínculos no acredita cobertura"
                           )})

    # --- collections --------------------------------------------------------
    if not args.collection:
        _emit({"status": STATUS_INVALID,
               "errors": [{"code": "usage",
                           "message": "falta --collection (requerido con registro)"}]})
        return EXIT_USAGE
    current, cerr = _load_json(Path(args.collection))
    current_nodeids: list[str] = []
    current_scope: list[str] = []
    baseline_nodeids: list[str] | None = None
    new_check: str | None = None
    if cerr is not None:
        errors.append({"code": "bad_collection", "message": cerr})
    elif not isinstance(current, dict):
        errors.append({"code": "bad_collection",
                       "message": "la colección no es un objeto"})
    else:
        nodeids = current.get("nodeids")
        scope = current.get("scope")
        exit_code = current.get("exit_code")
        if not isinstance(nodeids, list) or not all(isinstance(n, str) for n in nodeids):
            errors.append({"code": "bad_collection",
                           "message": "nodeids de CURRENT no es lista de literales"})
        else:
            current_nodeids = list(nodeids)
        if not isinstance(scope, list) or not all(isinstance(s, str) for s in scope):
            errors.append({"code": "bad_collection",
                           "message": "scope de CURRENT no es lista"})
        else:
            current_scope = list(scope)
        if exit_code != 0:
            errors.append({"code": "failed_collection",
                           "message": (
                               "colección fallida: no acredita existencia "
                               f"(exit_code={exit_code!r})"
                           )})

    if args.baseline:
        base, berr = _load_json(Path(args.baseline))
        if berr is not None:
            errors.append({"code": "bad_collection", "message": berr})
        elif not isinstance(base, dict):
            errors.append({"code": "bad_collection",
                           "message": "el baseline no es un objeto"})
        else:
            bnodes = base.get("nodeids")
            bscope = base.get("scope")
            bexit = base.get("exit_code")
            if not isinstance(bnodes, list) or not all(isinstance(n, str) for n in bnodes):
                errors.append({"code": "bad_collection",
                               "message": "nodeids de BASE no es lista de literales"})
            else:
                baseline_nodeids = list(bnodes)
            if bexit != 0:
                errors.append({"code": "failed_collection",
                               "message": (
                                   "colección baseline fallida "
                                   f"(exit_code={bexit!r})"
                               )})
            if not isinstance(bscope, list) or not all(isinstance(s, str) for s in bscope):
                errors.append({"code": "bad_collection",
                               "message": "scope de BASE no es lista"})
            elif isinstance(current, dict) and isinstance(current.get("scope"), list):
                if list(bscope) != list(current.get("scope")):
                    errors.append({"code": "scope_mismatch",
                                   "message": (
                                       "BASE y CURRENT declaran ámbitos distintos; "
                                       "los nuevos nodeids no son comparables"
                                   )})

    # --- links --------------------------------------------------------------
    covered: set[str] = set()
    linked_nodeids: set[str] = set()
    obligation_verifiers: dict[str, list[dict[str, Any]]] = {}
    for index, link in enumerate(links):
        where = f"links[{index}]"
        if not isinstance(link, dict):
            errors.append({"code": "bad_link",
                           "message": f"vínculo no es un objeto en {where}"})
            continue
        pc_ids = link.get("pc_ids")
        if (not isinstance(pc_ids, list) or not pc_ids
                or not all(isinstance(p, str) and p for p in pc_ids)):
            errors.append({"code": "bad_link",
                           "message": f"pc_ids vacíos en {where}"})
            continue
        for pid in pc_ids:
            if pid not in obligations:
                errors.append({"code": "unknown_obligation",
                               "message": (
                                   f"obligación inexistente {pid} en {where}; "
                                   f"no resuelve contra el contrato {contract_path_s}"
                               )})
        protects = link.get("protects")
        limits = link.get("limits")
        if not isinstance(protects, str) or not protects:
            errors.append({"code": "bad_link",
                           "message": f"protects vacío en {where}"})
        if not isinstance(limits, str) or not limits:
            errors.append({"code": "bad_link",
                           "message": f"limits vacío en {where}"})
        verifier = link.get("verifier")
        verifier_ok = True
        verifier_info: dict[str, Any] | None = None
        if not isinstance(verifier, dict):
            errors.append({"code": "bad_verifier",
                           "message": (
                               f"verificador ausente en {where} "
                               f"(pc_ids: {', '.join(pc_ids)})"
                           )})
            verifier_ok = False
        else:
            kind = verifier.get("kind")
            if kind == "test":
                nodeid = verifier.get("nodeid")
                if not isinstance(nodeid, str) or not nodeid:
                    errors.append({"code": "bad_verifier",
                                   "message": (
                                       f"verificador test sin nodeid en {where} "
                                       f"(pc_ids: {', '.join(pc_ids)})"
                                   )})
                    verifier_ok = False
                else:
                    linked_nodeids.add(nodeid)
                    if nodeid not in current_nodeids:
                        errors.append({"code": "unlinked_nodeid",
                                       "message": (
                                           f"nodeid vinculado ausente de la "
                                           f"colección en {where}: {nodeid} "
                                           f"(pc_ids: {', '.join(pc_ids)})"
                                       )})
                        verifier_ok = False
                    else:
                        verifier_info = {"kind": "test", "nodeid": nodeid}
            elif kind == "review":
                reason = verifier.get("reason")
                reference = verifier.get("reference")
                if not isinstance(reason, str) or not reason:
                    errors.append({"code": "bad_verifier",
                                   "message": (
                                       f"verificador review sin motivo en {where} "
                                       f"(pc_ids: {', '.join(pc_ids)})"
                                   )})
                    verifier_ok = False
                if not _check_doc_ref(project_root, reference, errors,
                                      f"{where}.verifier.reference"):
                    verifier_ok = False
                if verifier_ok:
                    verifier_info = {
                        "kind": "review",
                        "reason": reason,
                        "reference": reference,
                    }
            else:
                errors.append({"code": "bad_verifier",
                               "message": (
                                   f"verificador con kind inválido en {where}: "
                                   f"{kind!r} (pc_ids: {', '.join(pc_ids)})"
                               )})
                verifier_ok = False
        evidence = link.get("evidence", [])
        if not isinstance(evidence, list):
            errors.append({"code": "bad_evidence",
                           "message": f"evidence no es lista en {where}"})
        else:
            for eindex, ref in enumerate(evidence):
                _check_doc_ref(project_root, ref, errors,
                               f"{where}.evidence[{eindex}]")
        if verifier_ok and not any(
            _error_belongs_to_link(e.get("where", ""), where) for e in errors
        ):
            for pid in pc_ids:
                if pid in obligations:
                    covered.add(pid)
                    if verifier_info is not None:
                        obligation_verifiers.setdefault(pid, []).append(
                            {"where": where, **verifier_info}
                        )

    # --- gaps ----------------------------------------------------------------
    gaps = sorted(set(obligations) - covered)
    if gaps:
        by_promise: dict[str, list[str]] = {}
        for pid in gaps:
            by_promise.setdefault(obligations[pid], []).append(pid)
        for promise in by_promise:
            by_promise[promise] = sorted(by_promise[promise])
        errors.append({"code": "gaps",
                       "message": (
                           "obligaciones sin verificador: "
                           + ", ".join(
                               f"{pid} (promesa {obligations[pid]})" for pid in gaps
                           )
                       )})
    else:
        by_promise = {}

    # --- new nodeids ----------------------------------------------------------
    new_unlinked: list[str] = []
    if baseline_nodeids is None:
        new_check = NO_NEW_CHECK
    else:
        base_set = set(baseline_nodeids)
        new_nodeids = [n for n in current_nodeids if n not in base_set]
        for nodeid in sorted(set(new_nodeids)):
            if nodeid not in linked_nodeids:
                new_unlinked.append(nodeid)
        if new_unlinked:
            errors.append({"code": "new_unlinked",
                           "message": (
                               "nodeids nuevos sin vínculo (CURRENT−BASE): "
                               + ", ".join(new_unlinked)
                           )})

    status = STATUS_OK if not errors else STATUS_INVALID
    if markers_found:
        mode = "markers"
        coverage = (
            "cubre las obligaciones de marcadores del contrato "
            "(universo mecánico de marcadores reales)."
        )
    elif has_legacy_index:
        mode = "legacy"
        coverage = (
            "cubre las obligaciones indexadas, no una extracción "
            "exhaustiva del contrato."
        )
    else:
        mode = "markers"
        coverage = (
            "el contrato no declara obligaciones: sin marcadores "
            "ni índice legacy no hay universo que cubrir."
        )
    obligations_payload = [
        {
            "id": pid,
            "promise": promise,
            "verifiers": sorted(
                obligation_verifiers.get(pid, []),
                key=lambda v: json.dumps(v, sort_keys=True),
            ),
        }
        for pid, promise in sorted(obligations.items())
    ]
    payload: dict[str, Any] = {
        "status": status,
        "registry": str(args.registry),
        "contract": {"path": contract_path_s, "sha256": contract_sha},
        "unit": unit if isinstance(unit, str) else None,
        "mode": mode,
        "coverage": coverage,
        "obligations": obligations_payload,
        "scope": sorted(current_scope),
        "limits": [SCOPE_LIMITS],
        "gaps": [{"id": pid, "promise": obligations[pid]} for pid in gaps],
        "gaps_by_promise": by_promise,
        "new_unlinked": sorted(new_unlinked),
        "errors": sorted(errors, key=lambda e: json.dumps(e, sort_keys=True)),
    }
    if new_check is not None:
        payload["new_check"] = new_check
    _emit(payload)
    return EXIT_OK if status == STATUS_OK else EXIT_INVALID


# ---------------------------------------------------------------------------
# gap-report (016-002): informe reproducible de huecos de cobertura
#
# Contrato: ``docs/specs/016-002-gap-report/spec.md`` (PC-1..PC-10).
# Solo lectura: no modifica archivos ni ejecuta tests. Lee el estado CDAD,
# los registros explícitos, la colección admitida y las exclusiones
# opcionales, y emite un JSON determinista por stdout.
# ---------------------------------------------------------------------------

GAP_FORMAT_VERSION = 1

GAP_NO_REGISTRY_NOTE = "sin registro de vínculos declarado"

GAP_LIMIT_STRUCTURAL = (
    "Estructural: el informe declara universo, huecos y excluidos a partir "
    "de entradas identificadas; no ejecuta tests ni modifica archivos."
)
GAP_LIMIT_REPRODUCIBLE = (
    "Reproducible: mismos bytes de entrada y argumentos producen mismos "
    "bytes de salida; orden estable sin hora, rutas absolutas ni "
    "identificadores aleatorios."
)
GAP_LIMIT_NO_PROTECTION = (
    "Producir el informe no acredita protección de los contratos."
)
GAP_COVERAGE_MARKERS = (
    "cubre las obligaciones de marcadores del contrato "
    "(universo mecánico de marcadores reales)."
)
GAP_COVERAGE_LEGACY = (
    "cubre las obligaciones indexadas; no extracción exhaustiva del contrato."
)
GAP_COVERAGE_NOT_INDEXED = (
    "sin marcadores ni índice declarado: no indexada; sin obligaciones "
    "conocidas ni huecos."
)
GAP_EMPTY_REGISTRY_MSG = (
    "el registro presente sin vínculos no acredita cobertura"
)


def _gap_resolve(root: Path, given: str) -> Path | None:
    """Resuelve una ruta (absoluta o relativa a ROOT) dentro del proyecto."""
    candidate = Path(given)
    full = candidate if candidate.is_absolute() else (root / candidate)
    try:
        resolved = full.resolve()
    except OSError:
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def _gap_rel(root: Path, resolved: Path) -> str:
    return resolved.relative_to(root).as_posix()


def _gap_display(root: Path, given: str) -> str:
    """Ruta reproducible para diagnósticos (N2): relativa a ROOT o marcador."""
    try:
        cand = Path(given)
        full = cand if cand.is_absolute() else (root / cand)
        try:
            res = full.resolve()
        except OSError:
            res = full
        return res.relative_to(root).as_posix()
    except (ValueError, OSError):
        if not Path(given).is_absolute():
            return Path(given).as_posix()
        return "<fuera del proyecto>"


def _gap_sort_key(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def _gap_load_json(resolved: Path, rel: str) -> tuple[Any | None, str | None]:
    try:
        return json.loads(resolved.read_text(encoding="utf-8")), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"no se pudo leer el archivo: {rel} ({exc})"
    except json.JSONDecodeError as exc:
        return None, f"registro corrupto, no es JSON válido: {rel} ({exc})"


def _gap_empty_payload() -> dict[str, Any]:
    return {
        "format_version": GAP_FORMAT_VERSION,
        "status": STATUS_INVALID,
        "inputs": {},
        "universe": [],
        "scope": {"current_rows": 0, "history_rows": 0},
        "unregistered_closures": [],
        "out_of_universe": [],
        "invalid_units": [],
        "diagnostics": [],
        "index": {},
        "obligations": [],
        "declared": [],
        "gaps": [],
        "gaps_by_promise": {},
        "not_indexed": [],
        "excluded": [],
        "limits": [
            GAP_LIMIT_STRUCTURAL,
            GAP_LIMIT_REPRODUCIBLE,
            GAP_LIMIT_NO_PROTECTION,
        ],
    }


def _gap_sort_diagnostics(
    diagnostics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        diagnostics,
        key=lambda d: (
            str(d.get("where", "")),
            str(d.get("code", "")),
            str(d.get("message", "")),
            _gap_sort_key(d),
        ),
    )


def cmd_gap_report(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root)
    if not project_root.is_dir():
        payload = _gap_empty_payload()
        payload["diagnostics"] = [{
            "code": "usage",
            "where": "cli",
            "message": f"project-root inexistente: {args.project_root}",
        }]
        _emit(payload)
        return EXIT_USAGE
    root = project_root.resolve()

    diagnostics: list[dict[str, Any]] = []

    def _early(diags: list[dict[str, Any]]) -> int:
        payload = _gap_empty_payload()
        payload["diagnostics"] = _gap_sort_diagnostics(diags)
        payload["invalid_units"] = sorted(
            {str(d["unit"]) for d in diags if "unit" in d}
        )
        _emit(payload)
        return EXIT_INVALID

    def _usage(message: str) -> int:
        payload = _gap_empty_payload()
        payload["diagnostics"] = [{
            "code": "usage", "where": "cli", "message": message,
        }]
        _emit(payload)
        return EXIT_USAGE

    # ---- estado: universo de contratos ----------------------------------
    state_resolved = _gap_resolve(root, args.state)
    if state_resolved is None or not state_resolved.is_file():
        return _early([{
            "code": "bad_state", "where": "state",
            "message": (
                "el estado no resuelve dentro del proyecto: "
                f"{_gap_display(root, args.state)}"
            ),
        }])
    state_rel = _gap_rel(root, state_resolved)
    state_sha = _sha256_file(state_resolved)
    state_obj, state_err = _gap_load_json(state_resolved, state_rel)
    if state_err is not None:
        return _early([{
            "code": "corrupt_state", "where": "state", "message": state_err,
        }])
    if not isinstance(state_obj, dict):
        return _early([{
            "code": "bad_state", "where": "state",
            "message": "el estado no es un objeto",
        }])
    current_rows = state_obj.get("epic_features")
    history_entries = state_obj.get("epic_history", [])
    if not isinstance(current_rows, list) or not isinstance(history_entries, list):
        return _early([{
            "code": "bad_state", "where": "state",
            "message": (
                "el estado no declara epic_features ni epic_history "
                "como listas"
            ),
        }])

    current_lists: dict[str, list[dict[str, Any]]] = {}
    for row in current_rows:
        if (not isinstance(row, dict) or not isinstance(row.get("id"), str)
                or not row["id"]):
            return _early([{
                "code": "bad_state", "where": "state:epic_features",
                "message": "fila actual sin id válido",
            }])
        current_lists.setdefault(row["id"], []).append(row)
    hist_by_unit: dict[str, list[dict[str, Any]]] = {}
    history_count = 0
    for hindex, entry in enumerate(history_entries):
        where = f"state:epic_history[{hindex}]"
        if (not isinstance(entry, dict)
                or not isinstance(entry.get("epic_features"), list)):
            return _early([{
                "code": "bad_state", "where": where,
                "message": "entrada histórica sin epic_features como lista",
            }])
        for row in entry["epic_features"]:
            if (not isinstance(row, dict) or not isinstance(row.get("id"), str)
                    or not row["id"]):
                return _early([{
                    "code": "bad_state", "where": where,
                    "message": "fila histórica sin id válido",
                }])
            hist_by_unit.setdefault(row["id"], []).append(row)
            history_count += 1

    def _norm_evidence(row: dict[str, Any]) -> Any | None:
        ev = row.get("closure_evidence")
        if not isinstance(ev, dict):
            return None
        return {"path": ev.get("path"), "sha256": ev.get("sha256")}

    def _norm_row(row: dict[str, Any]) -> dict[str, Any]:
        return {"status": row.get("status"),
                "closure_evidence": _norm_evidence(row)}

    current: dict[str, dict[str, Any]] = {}
    for unit in sorted(current_lists):
        rows = current_lists[unit]
        if len(rows) == 1:
            current[unit] = rows[0]
            continue
        first_current = _gap_sort_key(_norm_row(rows[0]))
        if all(_gap_sort_key(_norm_row(r)) == first_current
               for r in rows[1:]):
            current[unit] = rows[0]
        else:
            diagnostics.append({
                "code": "ambiguous_closure",
                "where": f"state:epic_features:{unit}",
                "unit": unit,
                "message": (
                    f"filas actuales incompatibles para {unit}: "
                    "evidencias o estados distintos; no se elige ninguna"
                ),
            })

    chosen: dict[str, dict[str, Any]] = {}
    for unit in sorted(set(current) | set(hist_by_unit)):
        if unit in current:
            # La fila actual tiene precedencia: las copias históricas
            # no la reincorporan.
            chosen[unit] = current[unit]
            continue
        rows = hist_by_unit[unit]
        first = _gap_sort_key(_norm_row(rows[0]))
        if all(_gap_sort_key(_norm_row(r)) == first for r in rows[1:]):
            chosen[unit] = rows[0]
        else:
            diagnostics.append({
                "code": "ambiguous_closure",
                "where": f"state:epic_history:{unit}",
                "unit": unit,
                "message": (
                    f"cierres históricos incompatibles para {unit}: sin "
                    "fila actual y evidencias distintas; no se elige ninguno"
                ),
            })
    invalid_units: set[str] = set()
    for diag in diagnostics:
        if "unit" in diag:
            invalid_units.add(str(diag["unit"]))

    universe: dict[str, dict[str, Any]] = {}
    spec_text: dict[str, str] = {}
    unregistered: list[dict[str, Any]] = []
    out_of_universe: list[dict[str, Any]] = []
    for unit in sorted(chosen):
        row = chosen[unit]
        if row.get("status") != "done":
            out_of_universe.append({
                "unit": unit,
                "status": row.get("status"),
                "reason": (
                    f"fuera del universo: estado {row.get('status')!r}; "
                    "solo done entra al universo; estado recuperable "
                    "desde el archivo de estado"
                ),
            })
            continue
        ev = row.get("closure_evidence")
        if (not isinstance(ev, dict)
                or not isinstance(ev.get("path"), str) or not ev["path"]
                or not isinstance(ev.get("sha256"), str)
                or not ev["sha256"]):
            unregistered.append({
                "unit": unit,
                "status": "done",
                "reason": (
                    "cierre no registrado: la fila done no declara "
                    "evidencia de cierre utilizable"
                ),
            })
            continue
        closure_resolved = _gap_resolve(root, str(ev["path"]))
        if closure_resolved is None or not closure_resolved.is_file():
            diagnostics.append({
                "code": "broken_closure_evidence",
                "where": f"closure:{unit}",
                "unit": unit,
                "message": (
                    f"evidencia de cierre rota para {unit}: {ev['path']} "
                    "no resuelve dentro del proyecto"
                ),
            })
            invalid_units.add(unit)
            continue
        actual_closure = _sha256_file(closure_resolved)
        if actual_closure != ev["sha256"]:
            diagnostics.append({
                "code": "broken_closure_evidence",
                "where": f"closure:{unit}",
                "unit": unit,
                "message": (
                    f"evidencia de cierre rota para {unit}: {ev['path']} "
                    f"(esperado {ev['sha256']}, actual {actual_closure})"
                ),
            })
            invalid_units.add(unit)
            continue
        spec_candidate = root / "docs" / "specs" / unit / "spec.md"
        try:
            spec_resolved = spec_candidate.resolve()
            spec_resolved.relative_to(root)
        except (OSError, ValueError):
            spec_resolved = None  # type: ignore[assignment]
        if spec_resolved is None or not spec_resolved.is_file():
            out_of_universe.append({
                "unit": unit,
                "status": "done",
                "reason": (
                    f"fuera del universo: sin spec en "
                    f"docs/specs/{unit}/spec.md; estado recuperable"
                ),
            })
            continue
        try:
            text = spec_resolved.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            out_of_universe.append({
                "unit": unit,
                "status": "done",
                "reason": (
                    f"fuera del universo: spec ilegible en "
                    f"docs/specs/{unit}/spec.md; estado recuperable"
                ),
            })
            continue
        universe[unit] = {
            "unit": unit,
            "spec": {
                "path": _gap_rel(root, spec_resolved),
                "sha256": hashlib.sha256(
                    text.encode("utf-8")).hexdigest(),
            },
            "closure": {
                "path": _gap_rel(root, closure_resolved),
                "sha256": actual_closure,
            },
        }
        spec_text[unit] = text
    unregistered.sort(key=_gap_sort_key)
    out_of_universe.sort(key=_gap_sort_key)

    # ---- vínculos explícitos --------------------------------------------
    raw_bindings: dict[str, list[str]] = {}
    for raw in (args.registry or []):
        if "=" not in raw:
            return _usage(
                "vínculo mal formado (se espera UNIT=RUTA): "
                f"{raw}"
            )
        unit_name, given = raw.split("=", 1)
        if not unit_name or not given:
            return _usage(
                "vínculo mal formado (unidad o ruta vacía): "
                f"{raw}"
            )
        raw_bindings.setdefault(unit_name, []).append(given)

    # ---- colección admitida ----------------------------------------------
    collection_nodeids: set[str] = set()
    collection_scope: list[str] = []
    collection_info: dict[str, str] | None = None
    collection_usable = True
    if args.collection is not None:
        collection_resolved = _gap_resolve(root, args.collection)
        if collection_resolved is None or not collection_resolved.is_file():
            diagnostics.append({
                "code": "bad_collection", "where": "collection",
                "message": (
                    "la colección no resuelve dentro del proyecto: "
                    f"{_gap_display(root, args.collection)}"
                ),
            })
            collection_usable = False
        else:
            collection_rel = _gap_rel(root, collection_resolved)
            collection_sha = _sha256_file(collection_resolved)
            collection_obj, collection_err = _gap_load_json(
                collection_resolved, collection_rel)
            if collection_err is not None:
                diagnostics.append({
                    "code": "bad_collection", "where": "collection",
                    "message": collection_err,
                })
                collection_usable = False
            elif not isinstance(collection_obj, dict):
                diagnostics.append({
                    "code": "bad_collection", "where": "collection",
                    "message": "la colección no es un objeto",
                })
                collection_usable = False
            else:
                nodeids = collection_obj.get("nodeids")
                scope = collection_obj.get("scope")
                exit_code = collection_obj.get("exit_code")
                if (not isinstance(nodeids, list)
                        or not all(isinstance(n, str) for n in nodeids)):
                    diagnostics.append({
                        "code": "bad_collection", "where": "collection",
                        "message": "nodeids de CURRENT no es lista de literales",
                    })
                    collection_usable = False
                elif (not isinstance(scope, list)
                        or not all(isinstance(s, str) for s in scope)):
                    diagnostics.append({
                        "code": "bad_collection", "where": "collection",
                        "message": "scope de CURRENT no es lista",
                    })
                    collection_usable = False
                elif exit_code != 0:
                    diagnostics.append({
                        "code": "failed_collection", "where": "collection",
                        "message": (
                            "colección fallida: no acredita existencia "
                            f"(exit_code={exit_code!r})"
                        ),
                    })
                    collection_usable = False
                else:
                    collection_nodeids = set(nodeids)
                    collection_scope = sorted(scope)
                    collection_info = {
                        "path": collection_rel,
                        "sha256": collection_sha,
                    }
    elif raw_bindings:
        return _usage("falta --collection (requerido con registro)")

    # ---- registros por unidad --------------------------------------------
    registry_inputs: dict[str, dict[str, str]] = {}
    obligations: dict[str, dict[str, str]] = {}
    unit_markers: dict[str, dict[str, str]] = {}
    unit_mode: dict[str, str] = {}
    covered: dict[str, set[str]] = {}
    obligation_verifiers: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for unit in sorted(raw_bindings):
        if unit not in universe:
            diagnostics.append({
                "code": "unknown_unit_registry",
                "where": f"registry:{unit}",
                "unit": unit,
                "message": (
                    f"el registro de {unit} no pertenece al universo "
                    "del informe"
                ),
            })
            invalid_units.add(unit)
            continue
        seen_files: dict[str, Any] = {}
        registry_failed = False
        for given in raw_bindings[unit]:
            resolved = _gap_resolve(root, given)
            if resolved is None or not resolved.is_file():
                diagnostics.append({
                    "code": "bad_registry",
                    "where": f"registry:{unit}",
                    "unit": unit,
                    "message": (
                        f"el registro de {unit} no resuelve dentro del "
                        f"proyecto: {_gap_display(root, given)}"
                    ),
                })
                registry_failed = True
                break
            rel = _gap_rel(root, resolved)
            sha = _sha256_file(resolved)
            obj, err = _gap_load_json(resolved, rel)
            if err is not None:
                diagnostics.append({
                    "code": "corrupt_registry",
                    "where": f"registry:{unit}",
                    "unit": unit,
                    "message": err,
                })
                registry_failed = True
                break
            if sha in seen_files:
                prev_rel, _, _ = seen_files[sha]
                if rel < prev_rel:
                    seen_files[sha] = (rel, sha, obj)
                continue
            if seen_files:
                diagnostics.append({
                    "code": "duplicate_registry",
                    "where": f"registry:{unit}",
                    "unit": unit,
                    "message": (
                        f"vínculos distintos para {unit} con contenido "
                        "distinto; no se elige ninguno"
                    ),
                })
                registry_failed = True
                break
            seen_files[sha] = (rel, sha, obj)
        if registry_failed or not seen_files:
            invalid_units.add(unit)
            continue
        rel, sha, reg = sorted(seen_files.values(), key=lambda t: t[0])[0]
        registry_inputs[unit] = {"path": rel, "sha256": sha}
        where = f"registry:{unit}"
        if not isinstance(reg, dict):
            diagnostics.append({
                "code": "bad_registry", "where": where, "unit": unit,
                "message": "el registro no es un objeto",
            })
            invalid_units.add(unit)
            continue
        if reg.get("unit") != unit:
            diagnostics.append({
                "code": "bad_registry", "where": where, "unit": unit,
                "message": "la unidad del registro no coincide con el vínculo",
            })
            invalid_units.add(unit)
            continue
        links = reg.get("links")
        if not isinstance(links, list):
            diagnostics.append({
                "code": "bad_registry", "where": where, "unit": unit,
                "message": "links no es una lista",
            })
            invalid_units.add(unit)
            continue
        cref = reg.get("contract")
        if (not isinstance(cref, dict)
                or not isinstance(cref.get("path"), str)
                or not cref["path"]
                or not isinstance(cref.get("sha256"), str)
                or not cref["sha256"]):
            diagnostics.append({
                "code": "bad_registry", "where": where, "unit": unit,
                "message": "contract sin path/sha256 válidos",
            })
            invalid_units.add(unit)
            continue
        contract_resolved = _gap_resolve(root, str(cref["path"]))
        expected_spec = (root / "docs" / "specs" / unit / "spec.md").resolve()
        if (contract_resolved is None or not contract_resolved.is_file()
                or contract_resolved != expected_spec
                or _sha256_file(contract_resolved)
                != universe[unit]["spec"]["sha256"]):
            diagnostics.append({
                "code": "contract_mismatch", "where": where, "unit": unit,
                "message": (
                    "el contrato del registro no coincide con "
                    f"docs/specs/{unit}/spec.md"
                ),
            })
            invalid_units.add(unit)
            continue
        legacy = reg.get("legacy_obligations")
        markers, duplicates = _extract_markers(spec_text[unit])
        unit_markers[unit] = markers
        if duplicates:
            diagnostics.append({
                "code": "duplicate_marker", "where": where, "unit": unit,
                "message": (
                    "marcador duplicado en el contrato "
                    f"docs/specs/{unit}/spec.md: "
                    f"{', '.join(sorted(duplicates))}"
                ),
            })
            invalid_units.add(unit)
            continue
        has_legacy_index = isinstance(legacy, list) and len(legacy) > 0
        unit_obligations: dict[str, str] = {}
        if markers and has_legacy_index:
            diagnostics.append({
                "code": "mixed_index", "where": where, "unit": unit,
                "message": (
                    "no se mezclan marcadores e índice legacy para "
                    f"docs/specs/{unit}/spec.md"
                ),
            })
            invalid_units.add(unit)
            continue
        elif markers:
            unit_obligations = dict(markers)
            unit_mode[unit] = "markers"
        elif isinstance(legacy, list) and legacy:
            legacy_ok = True
            for entry in legacy:
                if not isinstance(entry, dict):
                    diagnostics.append({
                        "code": "bad_legacy", "where": where, "unit": unit,
                        "message": "entrada legacy no es un objeto",
                    })
                    legacy_ok = False
                    break
                lid = entry.get("id")
                promise = entry.get("promise")
                locator = entry.get("locator")
                if not all(isinstance(v, str) and v
                           for v in (lid, promise, locator)):
                    diagnostics.append({
                        "code": "bad_legacy", "where": where, "unit": unit,
                        "message": (
                            "entrada legacy sin id/promise/locator válidos"
                        ),
                    })
                    legacy_ok = False
                    break
                count = spec_text[unit].count(str(locator))
                if count != 1:
                    diagnostics.append({
                        "code": "broken_legacy_locator",
                        "where": where, "unit": unit,
                        "message": (
                            f"locator legacy no único para {lid} "
                            f"(apariciones: {count})"
                        ),
                    })
                    legacy_ok = False
                    break
                if lid in unit_obligations:
                    diagnostics.append({
                        "code": "duplicate_legacy", "where": where,
                        "unit": unit,
                        "message": (
                            f"obligación legacy duplicada: {lid}"
                        ),
                    })
                    legacy_ok = False
                    break
                unit_obligations[str(lid)] = str(promise)
            if not legacy_ok:
                invalid_units.add(unit)
                continue
            unit_mode[unit] = "legacy"
        if not unit_obligations:
            diagnostics.append({
                "code": "no_obligations", "where": where, "unit": unit,
                "message": (
                    f"el contrato docs/specs/{unit}/spec.md no declara "
                    "obligaciones: sin marcadores ni índice legacy; el "
                    "registro presente sin obligaciones es inválido"
                ),
            })
            invalid_units.add(unit)
            continue
        if not links:
            diagnostics.append({
                "code": "empty_registry", "where": where, "unit": unit,
                "message": GAP_EMPTY_REGISTRY_MSG + f" para {unit}",
            })
            invalid_units.add(unit)
            continue
        if not collection_usable:
            diagnostics.append({
                "code": "unverified_registry", "where": where, "unit": unit,
                "message": (
                    f"sin colección válida: los vínculos de {unit} "
                    "no se acreditan"
                ),
            })
            invalid_units.add(unit)
            continue
        covered[unit] = set()
        obligation_verifiers[unit] = {}
        unit_broken = False
        for index, link in enumerate(links):
            link_where = f"{where}:links[{index}]"
            before = len(diagnostics)
            if not isinstance(link, dict):
                diagnostics.append({
                    "code": "bad_link", "where": link_where, "unit": unit,
                    "message": "vínculo no es un objeto",
                })
                unit_broken = True
                continue
            pc_ids = link.get("pc_ids")
            if (not isinstance(pc_ids, list) or not pc_ids
                    or not all(isinstance(p, str) and p for p in pc_ids)):
                diagnostics.append({
                    "code": "bad_link", "where": link_where, "unit": unit,
                    "message": "pc_ids vacíos",
                })
                unit_broken = True
                continue
            for pid in pc_ids:
                if pid not in unit_obligations:
                    diagnostics.append({
                        "code": "unknown_obligation",
                        "where": link_where, "unit": unit,
                        "message": (
                            f"obligación inexistente {pid}; no resuelve "
                            f"contra docs/specs/{unit}/spec.md"
                        ),
                    })
            protects = link.get("protects")
            limits = link.get("limits")
            if not isinstance(protects, str) or not protects:
                diagnostics.append({
                    "code": "bad_link", "where": link_where, "unit": unit,
                    "message": "protects vacío",
                })
            if not isinstance(limits, str) or not limits:
                diagnostics.append({
                    "code": "bad_link", "where": link_where, "unit": unit,
                    "message": "limits vacío",
                })
            verifier = link.get("verifier")
            verifier_ok = True
            verifier_info: dict[str, Any] | None = None
            if not isinstance(verifier, dict):
                diagnostics.append({
                    "code": "bad_verifier", "where": link_where,
                    "unit": unit,
                    "message": (
                        "verificador ausente "
                        f"(pc_ids: {', '.join(pc_ids)})"
                    ),
                })
                verifier_ok = False
            else:
                kind = verifier.get("kind")
                if kind == "test":
                    nodeid = verifier.get("nodeid")
                    if not isinstance(nodeid, str) or not nodeid:
                        diagnostics.append({
                            "code": "bad_verifier", "where": link_where,
                            "unit": unit,
                            "message": (
                                "verificador test sin nodeid "
                                f"(pc_ids: {', '.join(pc_ids)})"
                            ),
                        })
                        verifier_ok = False
                    elif nodeid not in collection_nodeids:
                        diagnostics.append({
                            "code": "unlinked_nodeid",
                            "where": link_where, "unit": unit,
                            "message": (
                                "nodeid vinculado ausente de la colección: "
                                f"{nodeid} (pc_ids: {', '.join(pc_ids)})"
                            ),
                        })
                        verifier_ok = False
                    else:
                        verifier_info = {"kind": "test", "nodeid": nodeid}
                elif kind == "review":
                    reason = verifier.get("reason")
                    reference = verifier.get("reference")
                    if not isinstance(reason, str) or not reason:
                        diagnostics.append({
                            "code": "bad_verifier", "where": link_where,
                            "unit": unit,
                            "message": (
                                "verificador review sin motivo "
                                f"(pc_ids: {', '.join(pc_ids)})"
                            ),
                        })
                        verifier_ok = False
                    link_errors: list[dict[str, Any]] = []
                    if not _check_doc_ref(
                            project_root, reference, link_errors,
                            f"{link_where}.verifier.reference"):
                        diagnostics.extend(
                            {**e, "unit": unit} for e in link_errors
                        )
                        verifier_ok = False
                    if verifier_ok and isinstance(reference, dict):
                        ref_resolved = _gap_resolve(
                            root, str(reference["path"]))
                        ref_rel = (
                            _gap_rel(root, ref_resolved)
                            if ref_resolved is not None else
                            str(reference["path"])
                        )
                        verifier_info = {
                            "kind": "review",
                            "reason": reason,
                            "reference": {
                                "path": ref_rel,
                                "sha256": reference["sha256"],
                                "locator": reference["locator"],
                            },
                        }
                else:
                    diagnostics.append({
                        "code": "bad_verifier", "where": link_where,
                        "unit": unit,
                        "message": (
                            "verificador con kind inválido: "
                            f"{kind!r} (pc_ids: {', '.join(pc_ids)})"
                        ),
                    })
                    verifier_ok = False
            evidence = link.get("evidence", [])
            if not isinstance(evidence, list):
                diagnostics.append({
                    "code": "bad_evidence", "where": link_where,
                    "unit": unit,
                    "message": "evidence no es lista",
                })
            else:
                for eindex, ref in enumerate(evidence):
                    ref_errors: list[dict[str, Any]] = []
                    _check_doc_ref(
                        project_root, ref, ref_errors,
                        f"{link_where}.evidence[{eindex}]")
                    diagnostics.extend(
                        {**e, "unit": unit} for e in ref_errors)
            if verifier_ok and not any(
                    _error_belongs_to_link(
                        str(e.get("where", "")), link_where)
                    for e in diagnostics[before:]):
                for pid in pc_ids:
                    if pid in unit_obligations:
                        covered[unit].add(pid)
                        if verifier_info is not None:
                            obligation_verifiers[unit].setdefault(
                                pid, []).append(
                                {"where": link_where, **verifier_info})
            if any(str(e.get("where", "")) == link_where
                   or str(e.get("where", "")).startswith(link_where + ".")
                   or str(e.get("where", "")).startswith(link_where + ":")
                   for e in diagnostics[before:]):
                unit_broken = True
        # Los defectos de enlaces invalidan el registro de la unidad.
        link_diags = [
            e for e in diagnostics
            if e.get("unit") == unit and str(e.get("where", "")).startswith(
                f"{where}:links[")
        ]
        if link_diags:
            unit_broken = True
        if unit_broken:
            invalid_units.add(unit)
            obligations.pop(unit, None)
            covered.pop(unit, None)
            obligation_verifiers.pop(unit, None)
            continue
        obligations[unit] = unit_obligations

    # Unidades sin registro: obligaciones solo desde marcadores reales.
    for unit in sorted(universe):
        if unit in invalid_units or unit in obligations or unit in raw_bindings:
            continue
        markers, _duplicates = _extract_markers(spec_text[unit])
        unit_markers[unit] = markers
        if markers:
            obligations[unit] = dict(markers)
            unit_mode[unit] = "markers"
        else:
            unit_mode[unit] = "not_indexed"
    for unit in sorted(universe):
        if unit not in unit_mode:
            markers = unit_markers.get(unit)
            if markers is None:
                markers, _duplicates = _extract_markers(spec_text[unit])
                unit_markers[unit] = markers
            if unit in invalid_units:
                unit_mode[unit] = (
                    "markers" if markers else "not_indexed")
            elif markers:
                unit_mode[unit] = "markers"
            else:
                unit_mode[unit] = "not_indexed"

    # ---- exclusiones justificadas -----------------------------------------
    applied: dict[tuple[str, str], dict[str, Any]] = {}
    exclusions_info: dict[str, str] | None = None
    if args.exclusions is not None:
        exclusions_resolved = _gap_resolve(root, args.exclusions)
        if exclusions_resolved is None or not exclusions_resolved.is_file():
            diagnostics.append({
                "code": "bad_exclusions", "where": "exclusions",
                "message": (
                    "las exclusiones no resuelven dentro del proyecto: "
                    f"{_gap_display(root, args.exclusions)}"
                ),
            })
        else:
            exclusions_rel = _gap_rel(root, exclusions_resolved)
            exclusions_sha = _sha256_file(exclusions_resolved)
            exclusions_info = {
                "path": exclusions_rel, "sha256": exclusions_sha,
            }
            exclusions_obj, exclusions_err = _gap_load_json(
                exclusions_resolved, exclusions_rel)
            if exclusions_err is not None:
                diagnostics.append({
                    "code": "bad_exclusions", "where": "exclusions",
                    "message": exclusions_err,
                })
            elif (not isinstance(exclusions_obj, dict)
                    or not isinstance(
                        exclusions_obj.get("exclusions"), list)):
                diagnostics.append({
                    "code": "bad_exclusions", "where": "exclusions",
                    "message": "las exclusiones no declaran una lista",
                })
            else:
                entries = exclusions_obj["exclusions"]
                counts: dict[tuple[str, str], int] = {}
                for _e in entries:
                    if (isinstance(_e, dict)
                            and isinstance(_e.get("unit"), str)
                            and _e.get("unit")
                            and isinstance(_e.get("promise"), str)
                            and _e.get("promise")):
                        _k = (_e.get("unit"), _e.get("promise"))
                        counts[_k] = counts.get(_k, 0) + 1
                for eindex, entry in enumerate(entries):
                    entry_where = f"exclusions[{eindex}]"
                    if not isinstance(entry, dict):
                        diagnostics.append({
                            "code": "bad_exclusion",
                            "where": entry_where,
                            "message": "la exclusión no es un objeto",
                        })
                        continue
                    unit = entry.get("unit")
                    cref = entry.get("contract")
                    promise = entry.get("promise")
                    reason = entry.get("reason")
                    if (isinstance(unit, str) and unit
                            and isinstance(promise, str) and promise
                            and counts.get((unit, promise), 0) > 1):
                        diagnostics.append({
                            "code": "bad_exclusion",
                            "where": entry_where, "unit": unit,
                            "message": (
                                f"exclusión repetida para {unit} "
                                f"promesa {promise}: no se aplica ninguna"
                            ),
                        })
                        continue
                    if (not isinstance(unit, str) or not unit
                            or unit not in universe
                            or unit in invalid_units
                            or unit not in obligations):
                        diagnostics.append({
                            "code": "bad_exclusion",
                            "where": entry_where,
                            "unit": unit if isinstance(unit, str) else None,
                            "message": (
                                f"la unidad {unit!r} no pertenece al "
                                "universo indexado del informe"
                            ),
                        })
                        continue
                    if (not isinstance(cref, dict)
                            or not isinstance(cref.get("path"), str)
                            or not cref["path"]
                            or not isinstance(cref.get("sha256"), str)
                            or not cref["sha256"]
                            or _gap_resolve(root, str(cref["path"]))
                            != (root / "docs" / "specs" / unit
                                / "spec.md").resolve()
                            or str(cref["sha256"])
                            != universe[unit]["spec"]["sha256"]):
                        diagnostics.append({
                            "code": "bad_exclusion",
                            "where": entry_where, "unit": unit,
                            "message": (
                                f"el contrato de la exclusión no coincide "
                                f"con docs/specs/{unit}/spec.md"
                            ),
                        })
                        continue
                    if (not isinstance(promise, str) or not promise
                            or promise not in set(
                                obligations[unit].values())):
                        diagnostics.append({
                            "code": "bad_exclusion",
                            "where": entry_where, "unit": unit,
                            "message": (
                                f"la promesa {promise!r} no pertenece a "
                                f"las obligaciones de {unit}"
                            ),
                        })
                        continue
                    if not isinstance(reason, str) or not reason.strip():
                        diagnostics.append({
                            "code": "bad_exclusion",
                            "where": entry_where, "unit": unit,
                            "message": (
                                f"exclusión sin motivo válido para {unit} "
                                f"promesa {promise}"
                            ),
                        })
                        continue
                    applied[(unit, promise)] = {
                        "unit": unit,
                        "promise": promise,
                        "obligations": sorted(
                            pid for pid, prom
                            in obligations[unit].items()
                            if prom == promise),
                        "reason": reason,
                        "file": exclusions_rel,
                        "file_sha": exclusions_sha,
                        "entry": eindex,
                    }

    # ---- clasificación por obligación --------------------------------------
    obligation_rows: list[dict[str, Any]] = []
    declared_rows: list[dict[str, Any]] = []
    gap_rows: list[dict[str, Any]] = []
    for unit in sorted(obligations):
        if unit in invalid_units:
            continue
        for pid in sorted(obligations[unit]):
            promise = obligations[unit][pid]
            verifiers = sorted(
                (obligation_verifiers.get(unit, {}).get(pid, [])),
                key=_gap_sort_key,
            )
            if (unit, promise) in applied:
                disposition = "excluded"
            elif pid in covered.get(unit, set()):
                disposition = "declared"
            else:
                disposition = "gap"
            obligation_rows.append({
                "unit": unit,
                "id": pid,
                "promise": promise,
                "disposition": disposition,
                "verifiers": verifiers,
            })
            if disposition == "declared":
                declared_rows.append({
                    "unit": unit,
                    "id": pid,
                    "promise": promise,
                    "verifiers": verifiers,
                })
            elif disposition == "gap":
                gap_rows.append({
                    "unit": unit, "id": pid, "promise": promise,
                })
    gaps_by_promise: dict[str, list[dict[str, str]]] = {}
    for gap in gap_rows:
        gaps_by_promise.setdefault(gap["promise"], []).append(
            {"unit": gap["unit"], "id": gap["id"]})
    for promise in gaps_by_promise:
        gaps_by_promise[promise] = sorted(
            gaps_by_promise[promise],
            key=lambda g: (g["unit"], g["id"]),
        )
    not_indexed = sorted(
        unit for unit in universe
        if unit not in invalid_units
        and unit not in obligations
        and unit not in raw_bindings
    )
    missing_registries = sorted(
        unit for unit in universe
        if unit not in invalid_units and unit not in raw_bindings
    )
    excluded_rows = sorted(
        applied.values(),
        key=lambda e: (str(e["unit"]), str(e["promise"])),
    )
    index: dict[str, dict[str, str]] = {}
    for unit in sorted(universe):
        mode = unit_mode.get(unit, "not_indexed")
        if mode == "markers":
            coverage = GAP_COVERAGE_MARKERS
        elif mode == "legacy":
            coverage = GAP_COVERAGE_LEGACY
        else:
            coverage = GAP_COVERAGE_NOT_INDEXED
        entry: dict[str, str] = {"mode": mode, "coverage": coverage}
        if unit in missing_registries:
            entry["registry"] = GAP_NO_REGISTRY_NOTE
        index[unit] = entry

    status = STATUS_OK if not diagnostics else STATUS_INVALID
    payload: dict[str, Any] = {
        "format_version": GAP_FORMAT_VERSION,
        "status": status,
        "inputs": {
            "state": {"path": state_rel, "sha256": state_sha},
            "registries": {
                unit: registry_inputs[unit]
                for unit in sorted(registry_inputs)
            },
            "collection": collection_info,
            "exclusions": exclusions_info,
        },
        "universe": [universe[unit] for unit in sorted(universe)],
        "scope": {
            "state": state_rel,
            "current_rows": len(current_lists),
            "history_rows": history_count,
        },
        "unregistered_closures": unregistered,
        "out_of_universe": out_of_universe,
        "invalid_units": sorted(invalid_units),
        "diagnostics": _gap_sort_diagnostics(diagnostics),
        "index": index,
        "obligations": obligation_rows,
        "declared": declared_rows,
        "gaps": gap_rows,
        "gaps_by_promise": gaps_by_promise,
        "not_indexed": not_indexed,
        "excluded": excluded_rows,
        "limits": [
            GAP_LIMIT_STRUCTURAL,
            GAP_LIMIT_REPRODUCIBLE,
            GAP_LIMIT_NO_PROTECTION,
        ],
    }
    if missing_registries:
        payload["registry_note"] = (
            f"{GAP_NO_REGISTRY_NOTE} para: "
            f"{', '.join(missing_registries)}"
        )
    _emit(payload)
    return EXIT_OK if status == STATUS_OK else EXIT_INVALID


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdad_contract_links.py",
        description="Valida registros de vínculos contrato↔test (016-001) "
                    "e informa huecos de cobertura (016-002).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser(
        "validate", help="validar un registro contra contrato y colecciones")
    validate.add_argument("--project-root", required=True)
    validate.add_argument("--registry", required=True)
    validate.add_argument("--collection", required=False, default=None)
    validate.add_argument("--baseline", required=False, default=None)
    gap = sub.add_parser(
        "gap-report", help="informar huecos de cobertura (016-002)")
    gap.add_argument("--project-root", required=True)
    gap.add_argument("--state", required=True)
    gap.add_argument("--registry", required=False, action="append",
                     default=[])
    gap.add_argument("--collection", required=False, default=None)
    gap.add_argument("--exclusions", required=False, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "gap-report":
        return cmd_gap_report(args)
    parser.error("comando desconocido")
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
