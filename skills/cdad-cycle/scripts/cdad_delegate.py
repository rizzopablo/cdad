#!/usr/bin/env python3
"""CDAD common delegation interface (005-009 T1; PD-1/PD-2/PD-3/PD-8).

Destination-agnostic CLI. Given a project, a canonical packet published by
`prepare`, a destination id and an execution configuration, it

  1. resolves the destination adapter by module convention
     (`cdad_delegate_<destination>.py` next to this file) -- adding a
     destination never edits this interface (PD-1/INV-2);
  2. transports the published `PACKET.md` byte-identical to the adapter
     (PD-2/INV-3), never re-rendering nor re-writing the packet rules;
  3. registers the attempt in the SAME I8 ledger by reusing
     `cdad_packet.py prepare --record-dispatch`
     (`.cdad/executions/<execution-id>/dispatches/<attempt>.json`), taking
     execution_id/packet_id/role/substage FROM THE PUBLISHED PACKET (PD-3)
     and the observed configuration from `--exec-config` (PD-8);
  4. returns the T1 output schema on stdout:
     `{attempt, session, termination, delivery_ref, diagnosis}`.

It never writes `docs/.cdad-state.json` itself and never creates another ledger
or state: the only state change is the `prepared -> dispatched` transition the
reused machinery performs (INV-1). Execution configuration (runtime, model,
binary, logs, timeouts) arrives by `--exec-config`/flags; no host-specific value
is embedded here (PD-8/INV-7).

Adapter invocation contract (also documented in
`references/cli-delegation.md`): the adapter is run as a subprocess with the
canonical packet bytes on stdin, `--project-root`, `--packet-id`,
`--destination` and `--exec-config` on argv, and must print one JSON envelope
`{attempt, session, termination, delivery_ref, diagnosis}` on stdout. See that
reference for the termination vocabulary, the one-adapter-per-destination rule
and the honest limits.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TERMINATION_VOCABULARY = (
    "completed", "blocked", "transport-error", "timeout", "cancelled", "unknown",
)
OUTPUT_KEYS = ("attempt", "session", "termination", "delivery_ref", "diagnosis")
DESTINATION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
FLAT_NAME = re.compile(r"[A-Za-z0-9._-]+")
ADAPTER_PREFIX = "cdad_delegate_"
PACKET_CLI_NAME = "cdad_packet.py"


class DelegateError(RuntimeError):
    """Fail-closed diagnostic of the delegation interface."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _load_json(path: str | os.PathLike[str], label: str) -> dict[str, Any]:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DelegateError(f"{label} not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise DelegateError(f"{label} is not readable JSON: {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise DelegateError(f"{label} must be a JSON object: {path}")
    return document


def _adapter_path(destination: str) -> Path:
    """Resolve the adapter by destination id (module convention, PD-1)."""
    if not isinstance(destination, str) or DESTINATION_RE.fullmatch(destination) is None:
        raise DelegateError(
            f"invalid destination id {destination!r}: expected "
            "[A-Za-z0-9][A-Za-z0-9_-]*")
    return Path(__file__).resolve().parent / f"{ADAPTER_PREFIX}{destination}.py"


def _packet_paths(project_root: Path, packet_id: str) -> tuple[Path, dict[str, Any]]:
    """Resolve the published packet inside the explicit project (PD-3)."""
    if not isinstance(packet_id, str) or FLAT_NAME.fullmatch(packet_id) is None or ".." in packet_id:
        raise DelegateError(f"invalid packet id {packet_id!r}: expected a flat name")
    packet_dir = project_root / ".cdad" / "packets" / packet_id
    packet_md = packet_dir / "PACKET.md"
    request_path = packet_dir / "REQUEST.json"
    if not packet_md.is_file() or not request_path.is_file():
        raise DelegateError(
            f"unknown packet {packet_id!r}: expected a packet published by "
            f"prepare under {packet_dir}")
    return packet_md, _load_json(request_path, "packet request")


def _wait_timeout(config: dict[str, Any]) -> float | None:
    """Bound the adapter wait from the execution configuration (PD-5/PD-8)."""
    wait = config.get("wait")
    if isinstance(wait, dict):
        seconds = wait.get("timeout_seconds")
        if isinstance(seconds, (int, float)) and seconds > 0:
            return float(seconds)
    return None


def _parse_envelope(stdout: str) -> dict[str, Any] | None:
    """Read the adapter's JSON envelope from stdout (last valid object wins)."""
    text = stdout.strip()
    if not text:
        return None
    lines = [line for line in text.splitlines() if line.strip()]
    for candidate in [text, *reversed(lines)]:
        try:
            document = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(document, dict):
            return document
    return None


def _run_adapter(adapter: Path, project_root: Path, packet_id: str,
                 destination: str, exec_config: str | None,
                 packet_bytes: bytes, timeout: float | None) -> dict[str, Any]:
    """Invoke the adapter, transporting the packet bytes byte-identical."""
    argv = [sys.executable, str(adapter),
            "--project-root", str(project_root),
            "--packet-id", packet_id,
            "--destination", destination]
    if exec_config:
        argv += ["--exec-config", exec_config]
    env = dict(os.environ)
    env["CDAD_DELEGATE_DESTINATION"] = destination
    try:
        proc = subprocess.run(argv, input=packet_bytes, capture_output=True,
                              cwd=str(project_root), timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"termination": "timeout", "session": None, "delivery_ref": None,
                "diagnosis": f"destination {destination!r} did not answer within "
                             f"{timeout} seconds"}
    except OSError as exc:
        return {"termination": "transport-error", "session": None,
                "delivery_ref": None,
                "diagnosis": f"destination {destination!r} could not be started: {exc}"}
    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace").strip()
    envelope = _parse_envelope(stdout)
    if envelope is None:
        return {"termination": "transport-error", "session": None,
                "delivery_ref": None,
                "diagnosis": f"destination {destination!r} returned no envelope "
                             f"(rc={proc.returncode}): {stderr[:200]}"}
    return envelope


def _normalize_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    termination = envelope.get("termination")
    if termination not in TERMINATION_VOCABULARY:
        termination = "unknown"
    return {
        "session": _as_text(envelope.get("session")),
        "termination": termination,
        "delivery_ref": _as_text(envelope.get("delivery_ref")),
        "diagnosis": _as_text(envelope.get("diagnosis")),
    }


def _observation(runtime: str | None, model: str | None, session: str | None,
                 started_at: str) -> dict[str, Any]:
    """Build the closed-key I8 observation document (PD-3/PD-8)."""
    return {
        "runtime": runtime,
        "model_configured": model,
        "model_reported": None,
        "session": session,
        "started_at": started_at,
        "provenance": {
            "runtime": "execution config (--exec-config): runtime",
            "model_configured": "execution config (--exec-config): model",
            "model_reported": "destination adapter reported no model",
            "session": "destination adapter envelope: session",
            "started_at": "delegation interface clock (UTC)",
        },
    }


def _register_dispatch(project_root: Path, packet_id: str, request: dict[str, Any],
                       attempt_id: str, observation: dict[str, Any]) -> None:
    """Register the attempt by reusing `cdad_packet.py prepare --record-dispatch`.

    The observation document is staged under the execution directory (inside
    the project) and removed afterwards; the record and the state transition
    are written by the reused machinery in its own ledger (PD-2)."""
    execution_id = _as_text(request.get("execution_id"))
    if execution_id is None:
        raise DelegateError(f"packet {packet_id!r} request has no execution_id")
    observation_dir = project_root / ".cdad" / "executions" / execution_id
    observation_dir.mkdir(parents=True, exist_ok=True)
    observation_path = observation_dir / f".{attempt_id}.observation.json"
    payload = (json.dumps(observation, ensure_ascii=False, sort_keys=True, indent=2)
               + "\n").encode("utf-8")
    packet_cli = Path(__file__).resolve().parent / PACKET_CLI_NAME
    if not packet_cli.is_file():
        raise DelegateError(
            f"cannot register the dispatch: {PACKET_CLI_NAME} is not next to "
            "the delegation interface")
    try:
        observation_path.write_bytes(payload)
    except OSError as exc:
        raise DelegateError(f"cannot stage the dispatch observation: {exc}") from exc
    try:
        proc = subprocess.run(
            [sys.executable, str(packet_cli), "prepare",
             "--project-root", str(project_root),
             "--record-dispatch", packet_id,
             "--attempt-id", attempt_id,
             "--input", str(observation_path)],
            capture_output=True, text=True, cwd=str(project_root))
    finally:
        observation_path.unlink(missing_ok=True)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise DelegateError(
            f"dispatch registration failed for attempt {attempt_id!r}: {detail[:300]}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdad_delegate.py",
        description="CDAD common delegation interface (destination-agnostic).")
    parser.add_argument("--project-root", required=True,
                        help="project root (explicit, independent of the cwd)")
    parser.add_argument("--packet", required=True,
                        help="canonical packet id published by prepare")
    parser.add_argument("--destination", required=True,
                        help="destination adapter id (cdad_delegate_<id>.py)")
    parser.add_argument("--exec-config", default=None,
                        help="execution configuration JSON "
                             "(runtime/model/binary/logs/wait)")
    return parser


def delegate(args: argparse.Namespace) -> dict[str, Any]:
    project_root = Path(args.project_root)
    if not project_root.is_dir():
        raise DelegateError(f"--project-root is not a directory: {args.project_root}")
    project_root = project_root.resolve()
    destination = args.destination
    adapter = _adapter_path(destination)
    if not adapter.is_file():
        raise DelegateError(
            f"no adapter for destination {destination!r}: expected adapter "
            f"module {adapter.name} next to the delegation interface")
    packet_md, request = _packet_paths(project_root, args.packet)
    config = (_load_json(args.exec_config, "execution config")
              if args.exec_config else {})
    runtime = _as_text(config.get("runtime"))
    model = _as_text(config.get("model"))
    started_at = _now()
    attempt_id = f"delegate-{destination}-{uuid.uuid4().hex[:12]}"
    packet_bytes = packet_md.read_bytes()
    envelope = _run_adapter(adapter, project_root, args.packet, destination,
                            args.exec_config, packet_bytes,
                            _wait_timeout(config))
    normalized = _normalize_envelope(envelope)
    observation = _observation(runtime, model, normalized["session"], started_at)
    _register_dispatch(project_root, args.packet, request, attempt_id, observation)
    return {
        "attempt": attempt_id,
        "session": normalized["session"],
        "termination": normalized["termination"],
        "delivery_ref": normalized["delivery_ref"],
        "diagnosis": normalized["diagnosis"],
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output = delegate(args)
    except DelegateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(output, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
