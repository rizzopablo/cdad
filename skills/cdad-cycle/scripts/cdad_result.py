#!/usr/bin/env python3
"""CDAD result reception: atomic, idempotent persistence of original bytes.

003-002 T1 GREEN. The reception operation (`receive`) consumes the v2 runtime of
001 (execution context, published packet, state) without redefining it:

- validates execution/state and the packet through the public validators of
  `cdad_packet.py` (validate-state / validate-request / rendered packet);
- persists each part byte-for-byte under
  `PROJECT_ROOT/.cdad/runtime/results/<execution_id>/<packet_id>/`
  (`parts/<name>.utf8`, `bundle.json`, `receipt.json`) through a sibling
  temporary directory published with one exclusive rename;
- is idempotent: an identical retry returns the durable receipt byte-for-byte;
  conflicting content fails without overwriting;
- emits a mechanical receipt (`semantic_status` always `pending`) and never
  touches `docs/.cdad-state.json`.

`receive --late` (005-012 T4, PD-13/D-5) is the DECLARED late mode: it reuses
this same receipt machine and is the ONLY mode that inverts the vigency
precondition, persisting the staged delivery of an already CLOSED feature whose
cited packet belongs to that (closed) execution. Identity, parts, digests, scope
and the receipt schema are unchanged; nothing else is relaxed.

`validate-receipt` re-verifies a durable receipt against its stored payload.

003-002 T3 GREEN adds the supported runner evidence (`run-python-unittest`) and
its re-validation (`validate-run-evidence`). The runner admits only an argv whose
prefix is exactly `python3 -m unittest` (no shell, redirection or operator),
computes the before/after snapshots itself (never caller-supplied digests) and
records argv/log/exit/counts. `validate-run-evidence` recomputes the current
snapshots and only approves `valid-current` for a green, non-empty, unmoved tree
under a current contract.

Only Python 3 stdlib is used; no workflow engine, blob store or cache.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


# The canonical packet CLI lives next to this module; importing it (never
# re-running it) gives access to the public validators and the path policy.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cdad_packet  # noqa: E402


class ResultError(ValueError):
    """A result descriptor, manifest or store state violates the contract."""


RUNTIME_RELPATH = Path(".cdad") / "runtime"
RESULTS_RELPATH = RUNTIME_RELPATH / "results"
MATERIALIZE_RELPATH = RUNTIME_RELPATH / "materializations"
INBOX_RELPATH = Path(".cdad") / "inbox"
EXECUTIONS_RELPATH = Path(".cdad") / "executions"
STATE_RELPATH = Path("docs") / ".cdad-state.json"
BUNDLE_LIMIT_BYTES = 1024 * 1024
ASSETS_DIR = _SCRIPT_DIR.parent / "assets"
ARTIFACT_POLICY_NAME = "artifact-policy.json"
FEATURE_PLACEHOLDER = "<feature>"
SEGMENT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
HEX_RE = re.compile(r"[0-9a-f]{64}")
VALID_OBSERVATION_STATUS = {"trusted", "unknown"}
VALID_OPERATIONS = {"added", "modified", "deleted", "renamed"}
DESCRIPTOR_KEYS = {
    "schema_version", "execution_id", "packet_id", "feature_id", "source",
    "parts", "run_evidence_ref",
}
OBSERVED_CHANGES_KEYS = {
    "observation_status", "baseline_ref", "baseline_sha256", "manifest_path",
}
MANIFEST_KEYS = {
    "schema_version", "observation_status", "baseline_ref", "baseline_sha256",
    "changes",
}
AUTHORIZATION_KEYS = {
    "schema_version", "execution_id", "packet_id", "receipt_sha256",
    "authorized_by", "authority_ref", "approval_effect", "copies",
}
COPY_KEYS = {"part", "target", "expected_previous_sha256"}
JOURNAL_KEYS = {
    "schema_version", "execution_id", "packet_id", "receipt_sha256",
    "authorization_sha256", "copies",
}
JOURNAL_COPY_KEYS = {"part", "target", "sha256"}
RUN_REQUEST_KEYS = {
    "schema_version", "execution_id", "packet_id", "argv",
    "source_selection", "test_selection", "contract_sha256",
}
RUN_EVIDENCE_KEYS = {
    "schema_version", "execution_id", "packet_id", "argv", "cwd", "exit",
    "tests_run", "failures", "errors", "skipped", "runner_exceptions", "log",
    "source_selection", "test_selection", "contract_sha256", "snapshots",
    "started_at", "finished_at",
}
RUN_ARGV_PREFIX = ["python3", "-m", "unittest"]
# Closed whitelist of unittest flags INVARIANT to the test selection: they do
# not change WHICH tests run, so they may accompany a fully bindable target.
# Any other option changes what executes and degrades to `unknown` (§8
# fail-closed: the equivalence is only green when it can be bound completely).
RUN_INVARIANT_FLAGS = frozenset({
    "-v", "--verbose",
    "-q", "--quiet",
    "-b", "--buffer",
})
RUN_SHELL_OPERATOR_TOKENS = {
    "&&", "||", ";", "|", "&", "<", ">", ">>", "<<",
    "1>", "1>>", "2>", "2>>",
}
RUN_SHELL_OPERATOR_CHARS = frozenset(";&|<>`")
SNAPSHOT_EXCLUDED_RELPATHS = (".cdad/runtime", ".cdad/inbox")
_RAN_RE = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)
_FAILURES_RE = re.compile(r"failures=(\d+)")
_ERRORS_RE = re.compile(r"errors=(\d+)")
_SKIPPED_RE = re.compile(r"skipped=(\d+)")



def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ResultError(f"{label} must be an object")
    return value


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as stream:
            return _object(json.load(stream), label)
    except FileNotFoundError as exc:
        raise ResultError(f"{label} not found: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ResultError(f"cannot read {label} {path}: {exc}") from exc


def _read_bytes(path: Path, label: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ResultError(f"cannot read {label} {path}: {exc}") from exc


def _serialize(document: dict[str, Any], *, sort_keys: bool = False) -> bytes:
    try:
        return (json.dumps(document, ensure_ascii=False, indent=2,
                           sort_keys=sort_keys) + "\n").encode("utf-8")
    except (UnicodeError, ValueError) as exc:
        raise ResultError(f"cannot serialize document: {exc}") from exc


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _cwd_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else Path.cwd() / path


def _project_path(project_root: Path, raw: Any, label: str) -> Path:
    """Resolve a project-relative path, rejecting traversal and escape."""
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise ResultError(f"{label} must be a non-empty project-relative path")
    relative = Path(raw)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ResultError(f"{label} is unsafe: {raw!r}")
    candidate = project_root.joinpath(*relative.parts)
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(project_root)
    except ValueError as exc:
        raise ResultError(f"{label} escapes project root: {raw!r}") from exc
    except (OSError, RuntimeError) as exc:
        raise ResultError(f"cannot resolve {label} {raw!r}: {exc}") from exc
    return resolved


def _is_within(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _segment(value: Any, label: str) -> str:
    if not isinstance(value, str) or SEGMENT_RE.fullmatch(value) is None or ".." in value:
        raise ResultError(
            f"{label} must be a safe segment ([A-Za-z0-9][A-Za-z0-9._-]{{0,127}}): "
            f"{value!r}")
    return value


def _final_dir(project_root: Path, execution_id: str, packet_id: str) -> Path:
    return (project_root / RESULTS_RELPATH
            / _segment(execution_id, "execution_id")
            / _segment(packet_id, "packet_id"))


# --------------------------------------------------------------- descriptor


def _validate_descriptor(descriptor: dict[str, Any]) -> None:
    if descriptor.get("schema_version") != 1:
        raise ResultError("result descriptor schema_version must be 1")
    unknown = set(descriptor) - (DESCRIPTOR_KEYS | {"observed_changes"})
    if unknown:
        raise ResultError(
            "result descriptor has unknown fields: " + ", ".join(sorted(unknown)))
    missing = DESCRIPTOR_KEYS - set(descriptor)
    if missing:
        raise ResultError(
            "result descriptor is missing fields: " + ", ".join(sorted(missing)))
    for field in ("execution_id", "packet_id", "feature_id"):
        _segment(descriptor.get(field), f"descriptor.{field}")


def _validate_source(descriptor: dict[str, Any]) -> dict[str, Any]:
    source = _object(descriptor.get("source"), "descriptor.source")
    if source.get("kind") != "staged-file":
        raise ResultError(
            f"descriptor.source.kind must be 'staged-file' in the MVP: "
            f"{source.get('kind')!r}")
    unknown = set(source) - {"kind", "sdk_message_ref"}
    if unknown:
        raise ResultError(
            "descriptor.source has unknown fields: " + ", ".join(sorted(unknown)))
    return source


def _read_parts(descriptor: dict[str, Any],
                project_root: Path) -> list[dict[str, Any]]:
    """Read and validate every staged part; returns name/kind/digest/bytes/data."""
    raw_parts = descriptor.get("parts")
    if not isinstance(raw_parts, list) or not raw_parts:
        raise ResultError("descriptor.parts must be a non-empty list")
    inbox = (project_root / INBOX_RELPATH).resolve()
    parts: list[dict[str, Any]] = []
    seen: set[str] = set()
    total = 0
    for index, raw in enumerate(raw_parts):
        part = _object(raw, f"descriptor.parts[{index}]")
        if set(part) != {"name", "artifact_kind", "staged_path"}:
            raise ResultError(
                f"descriptor.parts[{index}] fields must be exactly name, "
                f"artifact_kind and staged_path")
        name = _segment(part.get("name"), f"descriptor.parts[{index}].name")
        if name in seen:
            raise ResultError(f"descriptor.parts has a duplicate name: {name!r}")
        seen.add(name)
        kind = part.get("artifact_kind")
        if not isinstance(kind, str) or not kind:
            raise ResultError(
                f"descriptor.parts[{index}].artifact_kind must be a non-empty string")
        staged = _project_path(project_root, part.get("staged_path"),
                               f"descriptor.parts[{index}].staged_path")
        if not _is_within(staged, inbox):
            raise ResultError(
                f"part {name!r} escapes the inbox ({INBOX_RELPATH.as_posix()}): "
                f"{part.get('staged_path')!r}")
        if not staged.is_file():
            raise ResultError(f"staged part {name!r} not found: {staged}")
        data = _read_bytes(staged, f"staged part {name!r}")
        if not data:
            raise ResultError(f"staged part {name!r} is empty")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ResultError(f"staged part {name!r} is not valid UTF-8: {exc}") from exc
        total += len(data)
        parts.append({
            "name": name,
            "artifact_kind": kind,
            "data": data,
            "sha256": _sha256(data),
            "bytes": len(data),
        })
    if total > BUNDLE_LIMIT_BYTES:
        raise ResultError(
            f"bundle exceeds {BUNDLE_LIMIT_BYTES} bytes: {total}")
    return parts


# ------------------------------------------------------------------- scope


def _validate_manifest(project_root: Path, raw_path: Any) -> dict[str, Any]:
    path = _project_path(project_root, raw_path, "observed_changes.manifest_path")
    if not path.is_file():
        raise ResultError(f"observed changes manifest not found: {raw_path}")
    manifest = _load_json(path, "observed changes manifest")
    if set(manifest) != MANIFEST_KEYS:
        raise ResultError("observed changes manifest fields do not match schema")
    if manifest.get("schema_version") != 1:
        raise ResultError("observed changes manifest schema_version must be 1")
    if manifest.get("observation_status") not in VALID_OBSERVATION_STATUS:
        raise ResultError(
            "observed changes manifest observation_status must be trusted or unknown")
    if not isinstance(manifest.get("baseline_ref"), str) or not manifest["baseline_ref"]:
        raise ResultError("observed changes manifest baseline_ref must be a non-empty string")
    if HEX_RE.fullmatch(str(manifest.get("baseline_sha256"))) is None:
        raise ResultError("observed changes manifest baseline_sha256 must be 64 lowercase hex")
    changes = manifest.get("changes")
    if not isinstance(changes, list):
        raise ResultError("observed changes manifest changes must be a list")
    paths: list[str] = []
    for index, raw in enumerate(changes):
        change = _object(raw, f"changes[{index}]")
        operation = change.get("operation")
        if operation not in VALID_OPERATIONS:
            raise ResultError(f"changes[{index}].operation is invalid: {operation!r}")
        expected = {"path", "operation", "previous_path"} if operation == "renamed" else {"path", "operation"}
        if set(change) != expected:
            raise ResultError(f"changes[{index}] fields do not match operation {operation!r}")
        _project_path(project_root, change.get("path"), f"changes[{index}].path")
        paths.append(change["path"])
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ResultError("observed changes manifest must be sorted by path without duplicates")
    return manifest


def _validate_scope(descriptor: dict[str, Any], request: dict[str, Any],
                    execution_document: dict[str, Any], project_root: Path) -> str:
    """Return the mechanical scope_validation: passed / failed / unknown."""
    observed = descriptor.get("observed_changes")
    if observed is None:
        return "unknown"
    observed = _object(observed, "descriptor.observed_changes")
    if set(observed) != OBSERVED_CHANGES_KEYS:
        raise ResultError("descriptor.observed_changes fields do not match schema")
    status = observed.get("observation_status")
    if status not in VALID_OBSERVATION_STATUS:
        raise ResultError(
            "descriptor.observed_changes.observation_status must be trusted or unknown")
    manifest = _validate_manifest(project_root, observed.get("manifest_path"))
    if (manifest["observation_status"] != status
            or manifest["baseline_ref"] != observed.get("baseline_ref")
            or manifest["baseline_sha256"] != observed.get("baseline_sha256")):
        raise ResultError(
            "descriptor.observed_changes and the manifest disagree on status, "
            "baseline_ref or baseline_sha256")
    if status != "trusted":
        return "unknown"
    contract_dir = str(Path(request["contract"]["path"]).parent.as_posix())
    policy = execution_document["path_policy"]
    write_scope = request["write_scope"]
    for change in manifest["changes"]:
        candidates = [change["path"]]
        if "previous_path" in change:
            candidates.append(change["previous_path"])
        for path in candidates:
            if not any(cdad_packet._scope_contains(scope, path, contract_dir,
                                                   policy, project_root)
                       for scope in write_scope):
                raise ResultError(
                    f"observed change path {path!r} is outside the declared write "
                    f"scope/alcance: no write_scope entry contains it")
    return "passed"


# ------------------------------------------------------------------ publish


def _write_synced(path: Path, data: bytes) -> None:
    with path.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _fsync_dir(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _verify_durable(final_dir: Path, receipt: dict[str, Any]) -> None:
    """Re-verify a durable receipt against its stored payload (integrity)."""
    if receipt.get("schema_version") != 1:
        raise ResultError("durable receipt schema_version must be 1")
    parts = receipt.get("parts")
    if not isinstance(parts, list) or not parts:
        raise ResultError("durable receipt parts must be a non-empty list")
    for part in parts:
        part = _object(part, "durable receipt part")
        # The receipt is caller input: the name must be a safe segment before
        # it is projected into the junction `parts/<name>.utf8` (§3). Without
        # this, a forged traversal name resolves and reads outside the project
        # root for both call sites (retry and validate-receipt).
        name = _segment(part.get("name"), "durable receipt part name")
        stored = final_dir / "parts" / f"{name}.utf8"
        if not stored.is_file():
            raise ResultError(f"durable result is incomplete: missing part {name!r}")
        data = _read_bytes(stored, f"stored part {name!r}")
        if _sha256(data) != part.get("sha256") or len(data) != part.get("bytes"):
            raise ResultError(f"durable part {name!r} is tampered or incomplete")
    bundle_path = final_dir / "bundle.json"
    if not bundle_path.is_file():
        raise ResultError("durable result is incomplete: missing bundle.json")
    if _sha256(_read_bytes(bundle_path, "bundle")) != receipt.get("bundle_sha256"):
        raise ResultError("durable bundle is tampered or incomplete")


def _load_durable_receipt(final_dir: Path) -> dict[str, Any] | None:
    if not final_dir.is_dir():
        return None
    receipt_path = final_dir / "receipt.json"
    if not receipt_path.is_file():
        raise ResultError(f"durable result is incomplete: missing {receipt_path.name}")
    receipt = _load_json(receipt_path, "durable receipt")
    _verify_durable(final_dir, receipt)
    return receipt


def _require_identical_result(durable: dict[str, Any], source: dict[str, Any],
                              parts: list[dict[str, Any]]) -> None:
    """Raise a conflict diagnostic unless the incoming result is identical."""
    if durable.get("source") != source:
        raise ResultError(
            "conflict: the incoming source differs from the durable receipt; "
            "refusing to overwrite the existing finalization")
    durable_parts = {part["name"]: part for part in durable.get("parts", [])}
    incoming = {part["name"]: part for part in parts}
    if set(durable_parts) != set(incoming):
        raise ResultError(
            "conflict: the incoming part set differs from the durable receipt; "
            "refusing to overwrite the existing finalization")
    for name, part in incoming.items():
        stored = durable_parts[name]
        if (stored.get("sha256") != part["sha256"]
                or stored.get("bytes") != part["bytes"]
                or stored.get("artifact_kind") != part["artifact_kind"]):
            raise ResultError(
                f"conflict: incoming part {name!r} differs from the durable receipt "
                f"(digest/bytes/kind); refusing to overwrite the existing finalization")


def _publish(final_dir: Path, parts: list[dict[str, Any]], bundle_bytes: bytes,
             receipt_bytes: bytes) -> bool:
    """Publish the final directory with one exclusive rename.

    Returns True when this invocation published; False when a concurrent
    receive had already published the same identity (the temporary directory is
    always removed, success or failure).
    """
    parent = final_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = parent / f".{final_dir.name}.tmp-{os.getpid()}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    try:
        (tmp_dir / "parts").mkdir(parents=True)
        for part in parts:
            _write_synced(tmp_dir / "parts" / f"{part['name']}.utf8", part["data"])
        _write_synced(tmp_dir / "bundle.json", bundle_bytes)
        _write_synced(tmp_dir / "receipt.json", receipt_bytes)
        _fsync_dir(tmp_dir / "parts")
        _fsync_dir(tmp_dir)
        try:
            os.rename(tmp_dir, final_dir)
        except OSError:
            if not final_dir.exists():
                raise
            return False
        return True
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)


# ------------------------------------------------------------------ receive


def _late_vigency(state: dict[str, Any], execution_document: dict[str, Any],
                  request: dict[str, Any]) -> None:
    """PD-13 (1)/D-5: the DECLARED inverse precondition of `receive --late`.

    The normal reception requires an OPEN active feature whose active packet is
    `dispatched` (through `cdad_packet.validate_request`). The late mode — the
    ONLY mode that inverts the vigency precondition — requires the OPPOSITE and
    nothing else: the destination feature is CLOSED and the cited packet belongs
    to that (closed) execution. Every other validation of `receive` (descriptor
    identity, source, parts, digests, scope and the receipt schema) is the
    shared machine and is NOT relaxed."""
    execution = execution_document.get("execution")
    if not isinstance(execution, dict):
        raise ResultError("the execution context has no execution object")
    feature_id = execution.get("feature_id")
    if request.get("execution_id") != execution.get("id"):
        raise ResultError(
            "the cited packet does not belong to its execution: the request "
            f"execution_id {request.get('execution_id')!r} does not match "
            f"{execution.get('id')!r}")
    if request.get("feature_id") != feature_id:
        raise ResultError(
            "the cited packet does not belong to its execution: the request "
            f"feature_id {request.get('feature_id')!r} does not match {feature_id!r}")
    status = cdad_packet._feature_status(state, feature_id)
    if status not in cdad_packet.CLOSED_FEATURE_STATUSES:
        raise ResultError(
            f"state incoherent: the late reception is declared for a CLOSED feature, but "
            f"{feature_id!r} has epic_features status {status!r}; receiving with the feature "
            f"open and its packet dispatched is the normal route")


def receive(args: argparse.Namespace, project_root: Path) -> bytes:
    # The late mode is a declared flag of THIS operation (PD-13/D-5): the receipt
    # machine is shared; only the vigency precondition is inverted.
    late = bool(getattr(args, "late", False))
    descriptor_path = _cwd_path(args.descriptor)
    descriptor = _load_json(descriptor_path, "result descriptor")
    _validate_descriptor(descriptor)
    source = _validate_source(descriptor)
    final_dir = _final_dir(project_root, descriptor["execution_id"],
                           descriptor["packet_id"])

    # A durable finalization is reconciled before requiring the active packet:
    # an identical read-only retry converges even after the packet advanced.
    durable = _load_durable_receipt(final_dir)
    if durable is not None:
        parts = _read_parts(descriptor, project_root)
        _require_identical_result(durable, source, parts)
        return _read_bytes(final_dir / "receipt.json", "durable receipt")

    state = _load_json(project_root / STATE_RELPATH, "project state")
    execution_document = _load_json(_cwd_path(args.execution_context),
                                    "execution context")
    request = _load_json(_cwd_path(args.request), "packet request")
    if late:
        # PD-13 (1)/D-5: the late mode replaces the ONE precondition that blocks
        # the normal reception (the active feature is not closed and the active
        # packet is `dispatched`) with its declared inverse: the destination
        # feature IS closed and the cited packet belongs to that execution.
        _late_vigency(state, execution_document, request)
    else:
        cdad_packet.validate_request(request, execution_document, state, project_root)
    packet_path = _cwd_path(args.packet)
    rendered = cdad_packet.render_packet(request, execution_document,
                                         project_root).encode("utf-8")
    if _read_bytes(packet_path, "packet") != rendered:
        raise ResultError("packet differs from its canonical rendering (validate-packet)")

    execution = execution_document["execution"]
    if descriptor["execution_id"] != execution["id"]:
        raise ResultError("descriptor.execution_id does not match the execution context")
    if descriptor["feature_id"] != execution["feature_id"]:
        raise ResultError("descriptor.feature_id does not match the execution context")
    if descriptor["packet_id"] != request["packet_id"]:
        raise ResultError("descriptor.packet_id does not match the published packet")
    if not late:
        active = state.get("active_packet")
        if not isinstance(active, dict) or active.get("status") != "dispatched":
            raise ResultError(
                "the active packet is not dispatched: reception requires the I8 dispatch "
                "observation (or an existing durable receipt)")

    parts = _read_parts(descriptor, project_root)
    scope_validation = _validate_scope(descriptor, request, execution_document,
                                       project_root)

    bundle_parts = sorted(
        ({"name": part["name"], "artifact_kind": part["artifact_kind"],
          "sha256": part["sha256"], "bytes": part["bytes"]} for part in parts),
        key=lambda entry: entry["name"])
    bundle_document = {
        "schema_version": 1,
        "execution_id": descriptor["execution_id"],
        "packet_id": descriptor["packet_id"],
        "feature_id": descriptor["feature_id"],
        "parts": bundle_parts,
    }
    bundle_bytes = _serialize(bundle_document, sort_keys=True)

    receipt = {
        "schema_version": 1,
        "execution_id": descriptor["execution_id"],
        "packet_id": descriptor["packet_id"],
        "feature_id": descriptor["feature_id"],
        "role": request["role"],
        "substage": request["substage"],
        "source": source,
        "parts": [
            {
                "name": part["name"],
                "artifact_kind": part["artifact_kind"],
                "sha256": part["sha256"],
                "bytes": part["bytes"],
                "stored_ref": (
                    f"{RESULTS_RELPATH.as_posix()}/{descriptor['execution_id']}/"
                    f"{descriptor['packet_id']}/parts/{part['name']}.utf8"),
            }
            for part in parts
        ],
        "bundle_sha256": _sha256(bundle_bytes),
        "packet_validation": "passed",
        "identity_validation": "passed",
        "scope_validation": scope_validation,
        "run_evidence_status": "not-provided",
        "semantic_status": "pending",
        "state_transition_requested": "received",
        "received_at": _utc_now(),
    }
    receipt_bytes = _serialize(receipt, sort_keys=True)

    if not _publish(final_dir, parts, bundle_bytes, receipt_bytes):
        # A concurrent receive published first: converge on its durable receipt.
        concurrent = _load_durable_receipt(final_dir)
        if concurrent is None:
            raise ResultError(
                "a concurrent publication left no readable durable result")
        _require_identical_result(concurrent, source, parts)
        return _read_bytes(final_dir / "receipt.json", "durable receipt")
    return receipt_bytes


# --------------------------------------------------------- validate-receipt


def validate_receipt(args: argparse.Namespace, project_root: Path) -> None:
    receipt_path = _cwd_path(args.receipt)
    receipt = _load_json(receipt_path, "receipt")
    final_dir = _final_dir(project_root, receipt.get("execution_id"),
                           receipt.get("packet_id"))
    if not final_dir.is_dir():
        raise ResultError(f"durable result not found for the receipt: {final_dir}")
    _verify_durable(final_dir, receipt)


# --------------------------------------------------------------- materialize


def _artifact_policy() -> dict[str, str]:
    """Load the closed artifact_kind -> allowed root/exact target table (§7)."""
    document = _load_json(ASSETS_DIR / ARTIFACT_POLICY_NAME, "artifact policy")
    if document.get("schema_version") != 1:
        raise ResultError("artifact policy schema_version must be 1")
    kinds = document.get("kinds")
    if not isinstance(kinds, dict) or not kinds:
        raise ResultError("artifact policy kinds must be a non-empty object")
    for kind, allowed in kinds.items():
        if not isinstance(kind, str) or not kind or not isinstance(allowed, str) or not allowed:
            raise ResultError(
                "artifact policy kinds must map a kind to a non-empty allowed path")
    return kinds


def _allowed_target(kind: str, feature_id: str) -> str:
    """The single allowed root/exact target for an artifact_kind (closed table)."""
    kinds = _artifact_policy()
    if kind not in kinds:
        raise ResultError(
            f"artifact_kind {kind!r} is not in the closed materialization policy")
    return kinds[kind].replace(FEATURE_PLACEHOLDER, feature_id)


def _allowed_kinds(role: str, substage: str) -> frozenset[str]:
    """The closed role/subphase -> artifact_kinds table (§7).

    The role axis closes the table: a kind that belongs to another role or
    subphase must fail even when it is present in the kind table.
    """
    if role == "architect":
        drafts = frozenset({"architect-spec-draft", "architect-plan-draft"})
        # The architect's role report / the draft delivered through the common
        # delegation interface arrives as a single `role-report` part; admit it
        # in the architect's discovery/draft subphases without relaxing the role
        # axis (a role-named kind of another role stays rejected).
        if substage in {"discovery", "draft"}:
            return drafts | {"role-report"}
        return drafts
    if role == "test-writer":
        return (frozenset({"test-audit"}) if substage == "audit"
                else frozenset({"test-writer-role-report"}))
    if role == "reviewer":
        return frozenset({substage} if substage in {"review", "plan-review"} else ())
    if role == "scribe":
        # The scribe's role report / the delivery through the common delegation
        # interface arrives as a single `role-report` part (PD-26/§2.8.3, D-17):
        # admit it in the scribe's only subphase (`memory`), alongside the four
        # per-file kinds. Same responsibility and same form as the architect's
        # report (005-007 T4), and the role axis stays closed: the Memory Bank
        # is not reachable through this kind (its allowed root is
        # `docs/specs/<feature>/`), and a role-named kind of another role stays
        # rejected.
        return frozenset({"scribe-projectbrief", "scribe-systemPatterns",
                          "scribe-activeContext", "scribe-progress",
                          "role-report"})
    if role == "implementer":
        return frozenset({"implementer-role-report"})
    return frozenset()


def _validate_authorization(authorization: dict[str, Any]) -> None:
    if authorization.get("schema_version") != 1:
        raise ResultError("materialize authorization schema_version must be 1")
    unknown = set(authorization) - AUTHORIZATION_KEYS
    if unknown:
        raise ResultError(
            "materialize authorization has unknown fields: " + ", ".join(sorted(unknown)))
    missing = AUTHORIZATION_KEYS - set(authorization)
    if missing:
        raise ResultError(
            "materialize authorization is missing fields: " + ", ".join(sorted(missing)))
    for field in ("execution_id", "packet_id"):
        _segment(authorization.get(field), f"authorization.{field}")
    if HEX_RE.fullmatch(str(authorization.get("receipt_sha256"))) is None:
        raise ResultError("authorization.receipt_sha256 must be 64 lowercase hex")
    if not isinstance(authorization.get("authorized_by"), str) or not authorization["authorized_by"]:
        raise ResultError("authorization.authorized_by must be a non-empty string")
    if not isinstance(authorization.get("authority_ref"), str) or not authorization["authority_ref"]:
        raise ResultError("authorization.authority_ref must be a non-empty string")
    if authorization.get("approval_effect") is not False:
        raise ResultError(
            "authorization.approval_effect must be false: materialize never approves")
    copies = authorization.get("copies")
    if not isinstance(copies, list) or not copies:
        raise ResultError("authorization.copies must be a non-empty list")
    for index, raw in enumerate(copies):
        copy = _object(raw, f"authorization.copies[{index}]")
        if set(copy) != COPY_KEYS:
            raise ResultError(
                f"authorization.copies[{index}] fields must be exactly part, target "
                f"and expected_previous_sha256")
        _segment(copy.get("part"), f"authorization.copies[{index}].part")
        if not isinstance(copy.get("target"), str) or not copy["target"]:
            raise ResultError(
                f"authorization.copies[{index}].target must be a non-empty project-relative path")
        expected = copy.get("expected_previous_sha256")
        if expected is not None and HEX_RE.fullmatch(str(expected)) is None:
            raise ResultError(
                f"authorization.copies[{index}].expected_previous_sha256 must be null "
                f"or 64 lowercase hex")


def _journal_path(project_root: Path, execution_id: str, packet_id: str,
                  authorization_sha: str) -> Path:
    return (project_root / MATERIALIZE_RELPATH / _segment(execution_id, "execution_id")
            / _segment(packet_id, "packet_id") / f"{authorization_sha}.json")


def _load_journal(path: Path, execution_id: str, packet_id: str,
                  receipt_sha: str, authorization_sha: str) -> dict[str, dict[str, str]]:
    """Load a durable journal bound to receipt + authorization; missing is empty."""
    if not path.is_file():
        return {}
    document = _load_json(path, "materialization journal")
    if set(document) != JOURNAL_KEYS or document.get("schema_version") != 1:
        raise ResultError("materialization journal fields do not match schema")
    if (document.get("execution_id") != execution_id
            or document.get("packet_id") != packet_id
            or document.get("receipt_sha256") != receipt_sha
            or document.get("authorization_sha256") != authorization_sha):
        raise ResultError(
            "materialization journal does not match the receipt/authorization binding")
    entries: dict[str, dict[str, str]] = {}
    for raw in document.get("copies", []):
        entry = _object(raw, "materialization journal copy")
        if set(entry) != JOURNAL_COPY_KEYS:
            raise ResultError("materialization journal copy fields do not match schema")
        entries[entry["target"]] = entry
    return entries


def _write_journal(path: Path, base: dict[str, Any],
                   entries: dict[str, dict[str, str]]) -> None:
    document = dict(base)
    document["copies"] = [entries[target] for target in sorted(entries)]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.tmp-{os.getpid()}"
    try:
        _write_synced(tmp, _serialize(document, sort_keys=True))
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
    _fsync_dir(path.parent)


def _atomic_write(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.parent / f".{target.name}.tmp-{os.getpid()}"
    try:
        _write_synced(tmp, data)
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
    _fsync_dir(target.parent)


def _apply_copy(copy: dict[str, Any], journal: dict[str, dict[str, str]],
                journal_path: Path, journal_base: dict[str, Any]) -> None:
    target = copy["target"]
    source = copy["source"]
    source_sha = copy["sha256"]
    label = copy["target_rel"]

    recorded = journal.get(label)
    if recorded is not None and recorded.get("sha256") == source_sha:
        if target.is_file() and target.read_bytes() == source:
            return  # already applied and identical: skip, never rewrite
        raise ResultError(
            f"conflict: journal records {label!r} as applied but its content diverged; "
            f"refusing to overwrite")

    if target.is_file():
        current = target.read_bytes()
        if current != source:
            expected = copy["expected"]
            if expected is None:
                raise ResultError(
                    f"conflict: target {label!r} already exists with divergent content "
                    f"and expected_previous_sha256 is null (create-only)")
            if _sha256(current) != expected:
                raise ResultError(
                    f"conflict: target {label!r} current digest does not match "
                    f"expected_previous_sha256 (CAS): refusing to overwrite")
    elif copy["expected"] is not None:
        raise ResultError(
            f"conflict: target {label!r} is absent but expected_previous_sha256 is not "
            f"null (CAS needs an existing previous digest)")

    if not (target.is_file() and target.read_bytes() == source):
        _atomic_write(target, source)
    journal[label] = {"part": copy["part"], "target": label, "sha256": source_sha}
    _write_journal(journal_path, journal_base, journal)


def materialize(args: argparse.Namespace, project_root: Path) -> None:
    authorization_path = _cwd_path(args.authorization)
    authorization_bytes = _read_bytes(authorization_path, "materialize authorization")
    authorization = _load_json(authorization_path, "materialize authorization")
    _validate_authorization(authorization)
    authorization_sha = _sha256(authorization_bytes)

    receipt_path = _cwd_path(args.receipt)
    receipt_bytes = _read_bytes(receipt_path, "receipt")
    if _sha256(receipt_bytes) != authorization["receipt_sha256"]:
        raise ResultError(
            "authorization.receipt_sha256 does not match the durable receipt (binding)")
    receipt = _load_json(receipt_path, "receipt")

    execution_id = _segment(receipt.get("execution_id"), "receipt.execution_id")
    packet_id = _segment(receipt.get("packet_id"), "receipt.packet_id")
    feature_id = _segment(receipt.get("feature_id"), "receipt.feature_id")
    if authorization["execution_id"] != execution_id or authorization["packet_id"] != packet_id:
        raise ResultError(
            "authorization execution_id/packet_id do not match the receipt identity")
    if receipt.get("semantic_status") != "pending":
        raise ResultError(
            "receipt semantic_status must remain pending: materialize never approves")

    execution_document = _load_json(
        project_root / EXECUTIONS_RELPATH / execution_id / "execution.json",
        "execution context")
    execution = _object(execution_document.get("execution"), "execution context execution")
    if execution.get("id") != execution_id or execution.get("feature_id") != feature_id:
        raise ResultError("receipt identity does not match the execution context")
    if authorization["authority_ref"] != execution.get("authority_ref"):
        raise ResultError(
            f"authorization.authority_ref {authorization['authority_ref']!r} does not match "
            f"the execution authority {execution.get('authority_ref')!r} (binding)")

    # R1 (§5): a lapsed/revoked authority blocks new materializations, just as
    # it blocks new receptions. Reading the state is allowed (§9 forbids writing
    # it); reuse the public validator's delegation/vigency block so the exact
    # same contract is applied.
    state = _load_json(project_root / STATE_RELPATH, "project state")
    cdad_packet.validate_state(execution_document, state, project_root)

    final_dir = _final_dir(project_root, execution_id, packet_id)
    _verify_durable(final_dir, receipt)
    parts = {part["name"]: part for part in receipt["parts"]}

    role = receipt.get("role")
    substage = receipt.get("substage")
    if not isinstance(role, str) or not isinstance(substage, str):
        raise ResultError(
            "receipt role/substage must be strings: the closed §7 role table "
            "needs both")
    allowed_kinds = _allowed_kinds(role, substage)

    # Pre-flight: resolve and validate every copy before writing anything, so a
    # rejected target/kind never leaves a partial prefix.
    planned: list[dict[str, Any]] = []
    for copy in authorization["copies"]:
        name = copy["part"]
        part = parts.get(name)
        if part is None:
            raise ResultError(
                f"authorization copy references a part absent from the receipt: {name!r}")
        kind = part.get("artifact_kind")
        if kind not in allowed_kinds:
            raise ResultError(
                f"artifact_kind {kind!r} is not permitted for role {role!r}/"
                f"substage {substage!r}: a kind of another role fails in the "
                f"closed §7 table")
        allowed = _allowed_target(kind, feature_id)
        allowed_path = _project_path(project_root, allowed,
                                     f"artifact policy path for kind {kind!r}")
        target = _project_path(project_root, copy["target"],
                               f"copy target {copy['target']!r}")
        if not _is_within(target, allowed_path):
            raise ResultError(
                f"target {copy['target']!r} is outside the allowed root for "
                f"artifact_kind {kind!r} ({allowed!r}) in the closed policy")
        stored = final_dir / "parts" / f"{name}.utf8"
        source = _read_bytes(stored, f"stored part {name!r}")
        planned.append({
            "part": name,
            "target_rel": copy["target"],
            "target": target,
            "expected": copy["expected_previous_sha256"],
            "source": source,
            "sha256": _sha256(source),
        })

    journal_path = _journal_path(project_root, execution_id, packet_id, authorization_sha)
    journal_base = {
        "schema_version": 1,
        "execution_id": execution_id,
        "packet_id": packet_id,
        "receipt_sha256": authorization["receipt_sha256"],
        "authorization_sha256": authorization_sha,
    }
    journal = _load_journal(journal_path, execution_id, packet_id,
                            authorization["receipt_sha256"], authorization_sha)
    for copy in planned:
        _apply_copy(copy, journal, journal_path, journal_base)


# ------------------------------------------------------------- run evidence


def _validate_run_argv(argv: Any) -> list[str]:
    """Admit only an argv whose prefix is exactly `python3 -m unittest` (§8)."""
    if not isinstance(argv, list) or len(argv) < len(RUN_ARGV_PREFIX):
        raise ResultError(
            "run request argv must be a list beginning with 'python3 -m unittest'")
    if argv[:3] != RUN_ARGV_PREFIX:
        raise ResultError(
            "run request argv prefix must be exactly 'python3 -m unittest': no other "
            "interpreter, runner or shell wrapper is admitted")
    for token in argv:
        if not isinstance(token, str) or not token:
            raise ResultError("run request argv entries must be non-empty strings")
        if token in RUN_SHELL_OPERATOR_TOKENS or any(
                char in RUN_SHELL_OPERATOR_CHARS for char in token):
            raise ResultError(
                "run request argv must not contain shell operators or redirections "
                f"(no shell): {token!r}")
    return list(argv)


def _normalize_rel(value: str) -> str:
    """Normalize a project-relative path for mechanical comparison."""
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def _rel_within(rel: str, root: str) -> bool:
    """True when `rel` is `root` itself or lives below it."""
    return rel == root or rel.startswith(root + "/")


def _module_tree(target: str, project_root: Path) -> str | None:
    """Containing source tree of a dotted module/package target (§8).

    `a.b.c` maps to the package tree `a/b`; a single segment `a` maps to the
    tree `a` when it is a package/directory and to `.` when it is a top-level
    module `a.py`. A target that cannot be resolved to a tree yields None so the
    binding degrades to `unknown` (fail-closed).
    """
    dotted = target
    if dotted.endswith(".py"):
        dotted = dotted[:-3].replace("/", ".")
    if dotted.endswith("."):
        dotted = dotted[:-1]
    if not dotted or dotted.startswith("."):
        return None
    if "." in dotted:
        return dotted.rsplit(".", 1)[0].replace(".", "/")
    candidate = project_root / dotted
    if (candidate / "__init__.py").is_file() or candidate.is_dir():
        return dotted
    if (project_root / f"{dotted}.py").is_file():
        return "."
    return None


def _argv_test_roots(argv: list[str], project_root: Path
                     ) -> tuple[list[str], list[str]]:
    """Derive the test tree(s) argv executes and flag un-bindable forms (§8).

    Fail-closed: only two forms are fully bindable to `test_selection` — the
    `discover -s <root>` form with an explicit declared root, and module/package
    targets mapped to their containing tree. The only options accepted are the
    closed whitelist of flags invariant to the selection. Any other option, an
    unclassifiable target or a `discover` form without an explicit root degrades
    the equivalence to `unknown` (never a green gate).
    """
    rest = argv[len(RUN_ARGV_PREFIX):]
    reasons: list[str] = []
    roots: list[str] = []
    if not rest:
        return [], ["argv declares no test target: the equivalence is unknown"]
    if rest[0] == "discover":
        saw_root = False
        index = 1
        while index < len(rest):
            token = rest[index]
            if token in ("-s", "--start-directory"):
                if index + 1 >= len(rest):
                    reasons.append(
                        "argv discover option declares no directory: the "
                        "equivalence is unknown")
                    break
                roots.append(rest[index + 1])
                saw_root = True
                index += 2
                continue
            if token.startswith("--start-directory="):
                roots.append(token.split("=", 1)[1])
                saw_root = True
                index += 1
                continue
            if token in RUN_INVARIANT_FLAGS:
                index += 1
                continue
            reasons.append(
                f"argv discover argument {token!r} is not invariant to the "
                "test selection: the equivalence is unknown")
            index += 1
        if not saw_root:
            reasons.append(
                "argv discover declares no explicit -s start directory: the "
                "equivalence is unknown")
        return roots, reasons
    for token in rest:
        if token in RUN_INVARIANT_FLAGS:
            continue
        if token.startswith("-"):
            reasons.append(
                f"argv option {token!r} is not invariant to the test "
                "selection: the equivalence is unknown")
            continue
        tree = _module_tree(token, project_root)
        if tree is None:
            reasons.append(
                f"argv target {token!r} cannot be bound to a test tree: the "
                "equivalence is unknown")
            continue
        if tree not in roots:
            roots.append(tree)
    if not roots and not reasons:
        reasons.append(
            "argv declares no bindable test target: the equivalence is unknown")
    return roots, reasons


def _run_selection_binding_reasons(run_request: dict[str, Any],
                                   execution_document: dict[str, Any],
                                   project_root: Path) -> list[str]:
    """Mechanically bind the declared selections to what argv executes (§8).

    §8: the selections are explicit roots/paths; if it cannot be demonstrated
    that they cover what is relevant, the equivalence is `unknown`. Fail-closed:
    only forms that can be FULLY bound to `test_selection` are accepted; every
    other argv shape (unknown options such as `-k`, module targets outside the
    declared tree, `discover` without an explicit root) degrades to `unknown`.
    Additionally `source_selection` must intersect the implementation roots of
    the path policy (otherwise a mutation of the real source would stay
    invisible).
    """
    reasons: list[str] = []
    test_selection = [_normalize_rel(item)
                      for item in run_request["test_selection"]]
    roots, binding_reasons = _argv_test_roots(run_request["argv"], project_root)
    reasons.extend(binding_reasons)
    for root in roots:
        root_norm = _normalize_rel(root)
        if not any(_rel_within(root_norm, declared)
                   for declared in test_selection):
            reasons.append(
                f"argv test tree {root!r} is not declared in test_selection: "
                "the equivalence is unknown")
    policy = execution_document.get("path_policy")
    policy = policy if isinstance(policy, dict) else {}
    relevant = [_normalize_rel(str(item))
                for item in (policy.get("implementation_roots") or [])]
    relevant += [_normalize_rel(str(item))
                 for item in (policy.get("implementation_files") or [])]
    source_selection = [_normalize_rel(item)
                        for item in run_request["source_selection"]]
    if not relevant:
        reasons.append(
            "path policy declares no implementation roots: the source selection "
            "relevance is unknown")
    elif not any(_rel_within(sel, root) or _rel_within(root, sel)
                 for sel in source_selection for root in relevant):
        reasons.append(
            "source_selection does not cover the declared implementation roots: "
            "the equivalence is unknown")
    return reasons


def _run_log_reasons(log: Any, counts: dict[str, int]) -> list[str]:
    """Re-derive the captured log with the runner parser and require agreement.

    §8: the evidence is re-derived, never trusted by self-coincidence. The same
    parser the runner used on the live log is applied to the recorded log, and
    exit/'Ran N tests'/'failures='/'skipped=' must be consistent.
    """
    if not isinstance(log, str) or not log.strip():
        return ["evidence log is missing or malformed"]
    log_tests, log_failures, log_errors, log_skipped, ran = _parse_unittest_counts(log)
    if not ran:
        return ["evidence log does not show a completed unittest run "
                "('Ran N tests'): the equivalence is unknown"]
    reasons: list[str] = []
    if log_tests != counts.get("tests_run"):
        reasons.append("evidence tests_run differs from the captured log")
    if log_failures != counts.get("failures"):
        reasons.append("evidence failures differs from the captured log")
    if log_errors != counts.get("errors"):
        reasons.append("evidence errors differs from the captured log")
    if log_skipped != counts.get("skipped"):
        reasons.append("evidence skipped differs from the captured log")
    return reasons


def _validate_run_selection(project_root: Path, raw: Any, label: str) -> list[str]:
    """Each selection is an explicit existing project-relative root/path (§8)."""
    if not isinstance(raw, list) or not raw:
        raise ResultError(f"run request {label} must be a non-empty list")
    selections: list[str] = []
    for item in raw:
        path = _project_path(project_root, item, f"run request {label} entry")
        if not path.exists():
            raise ResultError(
                f"run request {label} entry does not exist (selection unknown): "
                f"{item!r}")
        selections.append(item)
    return selections


def _load_run_request(path: Path, project_root: Path) -> dict[str, Any]:
    document = _load_json(path, "run request")
    if document.get("schema_version") != 1:
        raise ResultError("run request schema_version must be 1")
    if set(document) != RUN_REQUEST_KEYS:
        unknown = set(document) - RUN_REQUEST_KEYS
        missing = RUN_REQUEST_KEYS - set(document)
        detail = []
        if unknown:
            detail.append("unknown: " + ", ".join(sorted(unknown)))
        if missing:
            detail.append("missing: " + ", ".join(sorted(missing)))
        raise ResultError(
            "run request fields do not match schema (" + "; ".join(detail) + "); "
            "the tool computes snapshots and never accepts caller-supplied digests")
    _segment(document.get("execution_id"), "run request execution_id")
    _segment(document.get("packet_id"), "run request packet_id")
    document["argv"] = _validate_run_argv(document.get("argv"))
    document["source_selection"] = _validate_run_selection(
        project_root, document.get("source_selection"), "source_selection")
    document["test_selection"] = _validate_run_selection(
        project_root, document.get("test_selection"), "test_selection")
    if HEX_RE.fullmatch(str(document.get("contract_sha256"))) is None:
        raise ResultError("run request contract_sha256 must be 64 lowercase hex")
    return document


def _load_run_binding(args: argparse.Namespace, project_root: Path
                      ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Validate execution/packet/request and bind them to the run request."""
    state = _load_json(project_root / STATE_RELPATH, "project state")
    execution_document = _load_json(_cwd_path(args.execution_context),
                                    "execution context")
    request = _load_json(_cwd_path(args.request), "packet request")
    cdad_packet.validate_request(request, execution_document, state, project_root)
    packet_path = _cwd_path(args.packet)
    rendered = cdad_packet.render_packet(request, execution_document,
                                         project_root).encode("utf-8")
    if _read_bytes(packet_path, "packet") != rendered:
        raise ResultError("packet differs from its canonical rendering (validate-packet)")
    run_request = _load_run_request(_cwd_path(args.run_request), project_root)
    execution = execution_document["execution"]
    if run_request["execution_id"] != execution["id"]:
        raise ResultError(
            "run request execution_id does not match the execution context")
    if run_request["packet_id"] != request["packet_id"]:
        raise ResultError("run request packet_id does not match the published packet")
    if run_request["contract_sha256"] != request["contract"]["sha256"]:
        raise ResultError(
            "run request contract_sha256 does not match the current contract: the "
            "contract is not vigente")
    return run_request, request, execution_document


def _ignore_patterns(project_root: Path) -> list[str]:
    """Minimal `.gitignore` patterns (non-negated lines) for snapshot discovery."""
    patterns: list[str] = []
    gitignore = project_root / ".gitignore"
    if gitignore.is_file():
        try:
            text = gitignore.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        for raw in text.splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and not line.startswith("!"):
                patterns.append(line)
    return patterns


def _is_ignored(rel_posix: str, name: str, is_dir: bool,
                patterns: list[str]) -> bool:
    for pattern in patterns:
        candidate = pattern
        dir_only = candidate.endswith("/")
        if dir_only:
            candidate = candidate.rstrip("/")
        candidate = candidate.lstrip("/")
        if not candidate:
            continue
        if dir_only and not is_dir:
            continue
        target = rel_posix if "/" in candidate else name
        if fnmatch.fnmatch(target, candidate):
            return True
    return False


def _collect_snapshot(project_root: Path, base: Path, patterns: list[str],
                      entries: dict[str, str]) -> None:
    stack = [base]
    visited: set[str] = set()
    while stack:
        current = stack.pop()
        try:
            resolved = current.resolve()
            rel = resolved.relative_to(project_root).as_posix()
        except (ValueError, OSError):
            continue
        parts = rel.split("/")
        if ".git" in parts or any(
                rel == excluded or rel.startswith(excluded + "/")
                for excluded in SNAPSHOT_EXCLUDED_RELPATHS):
            continue
        if current.is_dir():
            if rel in visited:
                continue
            visited.add(rel)
            if _is_ignored(rel, current.name, True, patterns):
                continue
            try:
                children = sorted(current.iterdir())
            except OSError:
                continue
            stack.extend(children)
        elif current.is_file():
            if _is_ignored(rel, current.name, False, patterns):
                continue
            entries[rel] = _sha256(_read_bytes(current, "snapshot file"))


def _snapshot_excluded(rel: str) -> bool:
    """Excluded from snapshots: `.git` and the coordination stores of `.cdad`."""
    parts = rel.split("/")
    if ".git" in parts:
        return True
    return any(rel == excluded or rel.startswith(excluded + "/")
               for excluded in SNAPSHOT_EXCLUDED_RELPATHS)


def _git_listing(project_root: Path) -> list[str] | None:
    """Tracked + untracked non-ignored project-relative paths via git (§8).

    §8 requires discovering "tracked and untracked non-ignored files". When the
    project is a git work tree, `git ls-files -z --cached --others
    --exclude-standard` is authoritative: it lists tracked files (which git does
    not ignore even if they match `.gitignore`) plus untracked non-ignored files.
    `-z` emits NUL-separated raw paths, so names with special/non-ASCII
    characters are not C-quoted by `core.quotepath` and stay in the snapshot.
    When the project is not a git repo this returns None and the caller falls
    back to the declared `.gitignore` approximation (accepted limitation).
    """
    if not (project_root / ".git").exists():
        return None
    try:
        listed = subprocess.run(
            ["git", "-C", str(project_root), "ls-files", "-z", "--cached",
             "--others", "--exclude-standard"],
            capture_output=True)
    except OSError:
        return None
    if listed.returncode != 0:
        return None
    paths: list[str] = []
    for rel in listed.stdout.decode("utf-8", errors="replace").split("\0"):
        if rel and not rel.startswith("../"):
            paths.append(rel)
    return paths


def _snapshot(project_root: Path, selections: list[str]) -> dict[str, Any]:
    """Discover tracked/untracked non-ignored files and hash them canonically (§8).

    Uses git when the project is a git repo; otherwise it falls back to the
    declared `.gitignore` pattern approximation (accepted limitation of this
    feature, not a green gate).
    """
    entries: dict[str, str] = {}
    git_paths = _git_listing(project_root)
    if git_paths is not None:
        roots: list[str] = []
        for selection in selections:
            base = _project_path(project_root, selection, "snapshot selection")
            roots.append(base.relative_to(project_root).as_posix())
        for rel in git_paths:
            if not any(_rel_within(rel, root) for root in roots):
                continue
            if _snapshot_excluded(rel):
                continue
            full = project_root / rel
            if full.is_file():
                entries[rel] = _sha256(_read_bytes(full, "snapshot file"))
    else:
        patterns = _ignore_patterns(project_root)
        for selection in selections:
            base = _project_path(project_root, selection, "snapshot selection")
            _collect_snapshot(project_root, base, patterns, entries)
    ordered = [{"path": path, "sha256": entries[path]} for path in sorted(entries)]
    payload = json.dumps(ordered, ensure_ascii=False, sort_keys=True,
                         indent=2).encode("utf-8")
    return {"sha256": _sha256(payload), "entries": ordered}


def _parse_unittest_counts(log: str) -> tuple[int, int, int, int, bool]:
    """Extract tests_run/failures/errors/skipped and whether the runner ran."""
    ran = _RAN_RE.search(log)
    tests_run = int(ran.group(1)) if ran else 0
    failures = int(match.group(1)) if (match := _FAILURES_RE.search(log)) else 0
    errors = int(match.group(1)) if (match := _ERRORS_RE.search(log)) else 0
    skipped = int(match.group(1)) if (match := _SKIPPED_RE.search(log)) else 0
    return tests_run, failures, errors, skipped, ran is not None


def run_python_unittest(args: argparse.Namespace, project_root: Path) -> bytes:
    run_request, _request, _execution = _load_run_binding(args, project_root)
    selections = (list(run_request["source_selection"])
                  + list(run_request["test_selection"]))
    before = _snapshot(project_root, selections)
    started_at = _utc_now()
    try:
        completed = subprocess.run(run_request["argv"], cwd=str(project_root),
                                   capture_output=True)
    except OSError as exc:
        raise ResultError(f"cannot execute the run request argv: {exc}") from exc
    finished_at = _utc_now()
    log = (completed.stdout + completed.stderr).decode("utf-8", errors="replace")
    exit_code = completed.returncode
    tests_run, failures, errors, skipped, ran = _parse_unittest_counts(log)
    runner_exceptions = 0 if ran else (1 if exit_code != 0 else 0)
    after = _snapshot(project_root, selections)
    evidence = {
        "schema_version": 1,
        "execution_id": run_request["execution_id"],
        "packet_id": run_request["packet_id"],
        "argv": list(run_request["argv"]),
        "cwd": ".",
        "exit": exit_code,
        "tests_run": tests_run,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "runner_exceptions": runner_exceptions,
        "log": log,
        "source_selection": list(run_request["source_selection"]),
        "test_selection": list(run_request["test_selection"]),
        "contract_sha256": run_request["contract_sha256"],
        "snapshots": {"before": before, "after": after},
        "started_at": started_at,
        "finished_at": finished_at,
    }
    return _serialize(evidence, sort_keys=True)


def _snapshot_digest(node: Any) -> str | None:
    if isinstance(node, str) and HEX_RE.fullmatch(node):
        return node
    if isinstance(node, dict):
        for key in ("sha256", "digest", "hash"):
            value = node.get(key)
            if isinstance(value, str) and HEX_RE.fullmatch(value):
                return value
    return None


def validate_run_evidence(args: argparse.Namespace, project_root: Path) -> bytes:
    """Recompute current snapshots and classify the evidence (§8).

    Never trusts the digests/argv recorded in the evidence: the current tree is
    recomputed from `RUN.json` and compared against the record.
    """
    run_request, _request, execution_document = _load_run_binding(args, project_root)
    evidence = _load_json(_cwd_path(args.evidence), "run evidence")
    reasons: list[str] = []
    if evidence.get("schema_version") != 1:
        reasons.append("evidence schema_version must be 1")
    unknown_keys = set(evidence) - RUN_EVIDENCE_KEYS
    missing_keys = RUN_EVIDENCE_KEYS - set(evidence)
    if unknown_keys or missing_keys:
        detail: list[str] = []
        if unknown_keys:
            detail.append("unknown: " + ", ".join(sorted(unknown_keys)))
        if missing_keys:
            detail.append("missing: " + ", ".join(sorted(missing_keys)))
        reasons.append(
            "evidence fields do not match the canonical schema ("
            + "; ".join(detail) + ")")
    if evidence.get("argv") != run_request["argv"]:
        reasons.append("evidence argv does not match the run request")
    if evidence.get("execution_id") != run_request["execution_id"]:
        reasons.append("evidence execution_id does not match the run request")
    if evidence.get("packet_id") != run_request["packet_id"]:
        reasons.append("evidence packet_id does not match the run request")
    if evidence.get("contract_sha256") != run_request["contract_sha256"]:
        reasons.append("evidence contract_sha256 does not match the current contract")
    if evidence.get("source_selection") != run_request["source_selection"]:
        reasons.append("evidence source_selection does not match the run request")
    if evidence.get("test_selection") != run_request["test_selection"]:
        reasons.append("evidence test_selection does not match the run request")
    if evidence.get("cwd") != ".":
        reasons.append(
            "evidence cwd does not match the project-root working directory")
    reasons.extend(_run_selection_binding_reasons(
        run_request, execution_document, project_root))

    snapshots = evidence.get("snapshots")
    before = _snapshot_digest(snapshots.get("before")) if isinstance(snapshots, dict) else None
    after = _snapshot_digest(snapshots.get("after")) if isinstance(snapshots, dict) else None
    if before is None or after is None:
        reasons.append("evidence snapshots before/after are missing or malformed")
    elif before != after:
        reasons.append("evidence snapshot before/after differ (tree mutated during the run)")

    selections = (list(run_request["source_selection"])
                  + list(run_request["test_selection"]))
    current = _snapshot(project_root, selections)
    if after is not None and current["sha256"] != after:
        reasons.append("current snapshot differs from the recorded evidence (stale)")

    exit_code = evidence.get("exit", evidence.get("exit_code"))
    counts: dict[str, int] = {}
    for key in ("tests_run", "failures", "errors", "skipped", "runner_exceptions"):
        value = evidence.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            reasons.append(f"evidence {key} must be an integer")
        else:
            counts[key] = value
    if not reasons and counts:
        if exit_code != 0:
            reasons.append("run exit code is not 0")
        if counts["tests_run"] <= 0:
            reasons.append("run has zero tests")
        elif counts["skipped"] >= counts["tests_run"]:
            reasons.append("run has no non-skipped test")
        if counts["failures"] or counts["errors"] or counts["runner_exceptions"]:
            reasons.append("run has failures, errors or runner exceptions")
    if not reasons:
        reasons.extend(_run_log_reasons(evidence.get("log"), counts))

    if not reasons:
        status = "valid-current"
    elif any("stale" in reason or "differ" in reason for reason in reasons):
        status = "stale"
    elif any("missing or malformed" in reason or "unknown" in reason
             for reason in reasons):
        status = "unknown"
    else:
        status = "invalid"
    document = {"schema_version": 1, "status": status, "reasons": reasons}
    return _serialize(document, sort_keys=True)


# ---------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cdad_result.py")
    commands = parser.add_subparsers(dest="command", required=True)
    receive_parser = commands.add_parser(
        "receive", help="persist the original result bytes and emit a receipt")
    receive_parser.add_argument("--project-root")
    receive_parser.add_argument("--execution-context", required=True)
    receive_parser.add_argument("--packet", required=True)
    receive_parser.add_argument("--request", required=True)
    receive_parser.add_argument("--descriptor", required=True)
    # PD-13 (005-012 T4, D-5): the DECLARED late mode. It reuses THIS receipt
    # machine and is the ONLY mode that inverts the vigency precondition — a
    # CLOSED feature whose cited packet belongs to its (closed) execution,
    # instead of the active feature not closed with its packet `dispatched`.
    # No other validation of `receive` is relaxed.
    receive_parser.add_argument(
        "--late", action="store_true",
        help="receive a staged delivery of an already CLOSED feature (PD-13)")
    validate_parser = commands.add_parser(
        "validate-receipt", help="re-verify a durable receipt against its payload")
    validate_parser.add_argument("--project-root")
    validate_parser.add_argument("--receipt", required=True)
    materialize_parser = commands.add_parser(
        "materialize", help="copy receipt parts to authorized canonical targets")
    materialize_parser.add_argument("--project-root")
    materialize_parser.add_argument("--receipt", required=True)
    materialize_parser.add_argument("--authorization", required=True)
    run_parser = commands.add_parser(
        "run-python-unittest",
        help="run the supported python3 -m unittest runner and emit evidence")
    run_parser.add_argument("--project-root")
    run_parser.add_argument("--execution-context", required=True)
    run_parser.add_argument("--packet", required=True)
    run_parser.add_argument("--request", required=True)
    run_parser.add_argument("--run-request", required=True)
    validate_run_parser = commands.add_parser(
        "validate-run-evidence",
        help="recompute current snapshots and classify the run evidence")
    validate_run_parser.add_argument("--project-root")
    validate_run_parser.add_argument("--execution-context", required=True)
    validate_run_parser.add_argument("--packet", required=True)
    validate_run_parser.add_argument("--request", required=True)
    validate_run_parser.add_argument("--run-request", required=True)
    validate_run_parser.add_argument("--evidence", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        project_root = (Path.cwd().resolve() if args.project_root is None
                        else Path(args.project_root).resolve())
        if not project_root.is_dir():
            raise ResultError(f"--project-root must be an existing directory: {project_root}")
        if args.command == "receive":
            sys.stdout.buffer.write(receive(args, project_root))
            return 0
        if args.command == "validate-receipt":
            validate_receipt(args, project_root)
            print("VALID: receipt")
            return 0
        if args.command == "materialize":
            materialize(args, project_root)
            return 0
        if args.command == "run-python-unittest":
            sys.stdout.buffer.write(run_python_unittest(args, project_root))
            return 0
        if args.command == "validate-run-evidence":
            sys.stdout.buffer.write(validate_run_evidence(args, project_root))
            return 0
        raise ResultError(f"unknown command: {args.command}")
    except (ResultError, cdad_packet.PolicyError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
