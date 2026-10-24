#!/usr/bin/env python3
"""CDAD common delegation interface (005-009 T1; PD-1/PD-2/PD-3/PD-8).

Destination-agnostic CLI. Given a project, a canonical packet published by
`prepare`, a destination id and an execution configuration, it

  1. resolves the destination adapter by module convention
     (`cdad_delegate_<destination>.py` next to this file) -- adding a
     destination never edits this interface (PD-1/INV-2);
  2. transports the published `PACKET.md` byte-identical to the adapter
     (PD-2/INV-3), never re-rendering nor re-writing the packet rules;
  3. RELAYS the attempt its destination declares: the destination module is the
     ONE writer of the I8 record of an external dispatch (006-005 PD-1/D-14), so
     this interface never registers a second attempt, never derives one of its
     own and never writes the ledger itself;
  4. returns the T1 output schema on stdout:
     `{attempt, session, termination, delivery_ref, diagnosis}`, with the
     `attempt` the destination declared.

It never writes `docs/.cdad-state.json` itself and never creates another ledger
or state: the only state change of an external dispatch is the
`prepared -> dispatched` transition the destination's own registration performs
through the reused machinery (INV-1). Execution configuration (runtime, binary,
logs, timeouts) arrives by `--exec-config`/flags; the delegated MODEL comes only
from the delegation config (`delegation.json`, 006-003 D3). No host-specific
value is embedded here (PD-8/INV-7).

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
from pathlib import Path
from typing import Any

# The ONE verifier of the pre-transport proof (007-003 §2.1) lives in the
# continuity CLI; it is imported, never re-implemented.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cdad_continuity  # noqa: E402

TERMINATION_VOCABULARY = (
    "completed", "blocked", "transport-error", "timeout", "cancelled", "unknown",
)
OUTPUT_KEYS = ("attempt", "session", "termination", "delivery_ref", "diagnosis")
DESTINATION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
FLAT_NAME = re.compile(r"[A-Za-z0-9._-]+")
ADAPTER_PREFIX = "cdad_delegate_"
PACKET_CLI_NAME = "cdad_packet.py"
# 006-003 D3/§2.2: the delegation configuration is the ONLY source of the
# delegated model, by destination and role. It is USER DATA under the config
# dir; the installer creates a template and never overwrites it.
DELEGATION_CONFIG_NAME = "delegation.json"
DELEGATION_CONFIG_VERSION = 1
# 006-003 §2.3/D5: the default server-credential file, sibling of the
# delegation config (`credential_env_file` redirects it).
DELEGATION_ENV_FILE_NAME = "opencode-server.env"


class DelegateError(RuntimeError):
    """Fail-closed diagnostic of the delegation interface."""


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


def cdad_config_dir() -> Path:
    """The ONE location rule of the user configuration (§2.2/§2.3, O-2): the
    same rule the installer applies when it WRITES these files, so the reader
    and the writer can never diverge.

    `$XDG_CONFIG_HOME/cdad/` when `XDG_CONFIG_HOME` is defined and non-empty;
    otherwise `<base>/.config/cdad/` with `<base>` = `CDAD_INSTALL_ROOT` when
    that variable is defined and non-empty (a redirected install root confines
    every write, INV-6), and the user's HOME otherwise. Read-only here: these
    are the user's files.
    """
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "")
    if xdg_config_home:
        return Path(xdg_config_home) / "cdad"
    base = os.environ.get("CDAD_INSTALL_ROOT", "") or str(Path.home())
    return Path(base) / ".config" / "cdad"


def delegation_config_path() -> Path:
    """Resolve the delegation config (§2.2/D3): the user configuration dir
    (`cdad_config_dir`) plus `delegation.json`."""
    return cdad_config_dir() / DELEGATION_CONFIG_NAME


def delegation_env_file_path() -> Path:
    """Default server-credential file (§2.3/D5), sibling of the delegation
    config: `<config-dir>/cdad/opencode-server.env` — the same location rule
    (§2.2), never its own."""
    return cdad_config_dir() / DELEGATION_ENV_FILE_NAME


def delegation_credential_env_file() -> str | None:
    """The `credential_env_file` the delegation config declares (§2.2), or
    `None` (meaning: use the default path).

    Read TOLERANTLY: the key is optional user data, so a missing, unreadable
    or foreign document -- or a non-string value -- resolves to the default
    path instead of blocking the dispatch. The strict v1 validation of
    `delegation_model` guards the contract-bearing key (the model), not this
    optional redirection.
    """
    path = delegation_config_path()
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(document, dict):
        return None
    value = document.get("credential_env_file")
    return value if isinstance(value, str) and value else None


def delegation_model(destination: str, role: str | None) -> str | None:
    """The model the delegation config declares for (destination, role).

    `delegation.json` is the only source (D3, no fallback): a role without an
    entry has NO model. A missing file is an empty configuration; a malformed
    one fails loud instead of silently delegating with no model (INV-7).
    """
    path = delegation_config_path()
    if not path.is_file():
        return None
    document = _load_json(path, "delegation config")
    version = document.get("version")
    if version != DELEGATION_CONFIG_VERSION:
        raise DelegateError(
            f"unsupported delegation config version {version!r} in {path}: "
            f"expected {DELEGATION_CONFIG_VERSION}")
    models = document.get("models")
    if not isinstance(models, dict):
        raise DelegateError(
            f"delegation config has no `models` object: {path}")
    destination_models = models.get(destination)
    if not isinstance(destination_models, dict) or not role:
        return None
    return _as_text(destination_models.get(role))


def _warn_legacy_model(destination: str, role: str | None) -> None:
    """One-line deprecation notice: the exec-config `model` is ignored (D3).

    The notice names the delegation config path and how to migrate (INV-7:
    nothing silent); it never prints the ignored value."""
    path = delegation_config_path()
    print(
        f"DEPRECATED: the `model` key of the execution configuration is "
        f"ignored (006-003 D3) — move it to "
        f"models.{destination}.{role or '<role>'} in {path}, the only source "
        f"of the delegated model",
        file=sys.stderr)


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
                 packet_bytes: bytes, timeout: float | None,
                 continuity_attempt: int | None = None) -> dict[str, Any]:
    """Invoke the adapter, transporting the packet bytes byte-identical."""
    argv = [sys.executable, str(adapter),
            "--project-root", str(project_root),
            "--packet-id", packet_id,
            "--destination", destination]
    if exec_config:
        argv += ["--exec-config", exec_config]
    # 007-003 §2.3.3: the arrival propagates the SAME integer it received; the
    # module never infers it from the textual attempt id.
    if continuity_attempt is not None:
        argv += ["--continuity-attempt", str(continuity_attempt)]

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
    """The declared output schema (T1): the attempt is RELAYED from the
    destination's own envelope — the module registers and declares it (PD-1 of
    006-005); this interface never replaces it with one of its own."""
    termination = envelope.get("termination")
    if termination not in TERMINATION_VOCABULARY:
        termination = "unknown"
    return {
        "attempt": _as_text(envelope.get("attempt")),
        "session": _as_text(envelope.get("session")),
        "termination": termination,
        "delivery_ref": _as_text(envelope.get("delivery_ref")),
        "diagnosis": _as_text(envelope.get("diagnosis")),
    }


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
    # 007-003 §2.1/§2.2: the INTEGER continuity attempt of this transport. The
    # adapter confirms the pre-transport proof at its own border, so invoking it
    # directly never bypasses the precondition.
    parser.add_argument("--continuity-attempt", type=int, default=None,
                        metavar="N",
                        help="the INTEGER continuity attempt of the dispatch "
                             "(mandatory when the execution has continuity; "
                             "never inferred from a textual id)")
    return parser


def require_continuity_attempt(value: Any) -> int | None:
    """007-003 §2.1/§2.2 (enmienda): the integer continuity attempt, or `None`
    when it was omitted — its obligation depends on whether the execution has
    continuity (never on a textual id)."""
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise DelegateError(
            f"--continuity-attempt must be a positive integer; got {value!r}")
    return value


def continuity_presence(project_root: Path, request: dict[str, Any]) -> str:
    """§2.2: presence declared by the execution of this request (fail closed on
    an unreadable identity)."""
    execution_id = _as_text(request.get("execution_id")) \
        if isinstance(request, dict) else None
    if execution_id is None:
        return cdad_continuity.CONTINUITY_PRESENT
    return cdad_continuity.continuity_presence(project_root, execution_id)


def verify_transport_proof(project_root: Path, packet_id: str, attempt: int,
                           request: dict[str, Any]) -> None:
    """007-003 §2.2: the adapter's OWN border check before the worker launch.

    It reuses the ONE verifier of §2.1 (`verify-begin`), so a direct invocation
    of this interface cannot bypass the precondition the entry already checks.
    """
    execution_id = _as_text(request.get("execution_id"))
    if execution_id is None:
        raise DelegateError(
            f"packet {packet_id!r} request has no execution_id: the continuity "
            f"proof cannot be checked (007-003)")
    try:
        cdad_continuity.verify_begin(
            project_root,
            cdad_continuity.execution_context_path(project_root, execution_id),
            packet_id, attempt)
    except cdad_continuity.ContinuityError as exc:
        raise DelegateError(f"the transport is refused: {exc}") from exc


def delegate(args: argparse.Namespace) -> dict[str, Any]:
    project_root = Path(args.project_root)
    if not project_root.is_dir():
        raise DelegateError(f"--project-root is not a directory: {args.project_root}")
    project_root = project_root.resolve()
    destination = args.destination
    attempt = require_continuity_attempt(
        getattr(args, "continuity_attempt", None))
    adapter = _adapter_path(destination)
    if not adapter.is_file():
        raise DelegateError(
            f"no adapter for destination {destination!r}: expected adapter "
            f"module {adapter.name} next to the delegation interface")
    packet_md, request = _packet_paths(project_root, args.packet)
    # §2.2: the proof is verified at THIS border, before the worker is launched.
    # Without the integer it is only mandatory when the execution HAS continuity
    # (enmienda 2026-10-24): a chainless execution proceeds and the omission is
    # declared in the attempt record.
    if attempt is not None:
        verify_transport_proof(project_root, args.packet, attempt, request)
    elif continuity_presence(project_root, request) \
            == cdad_continuity.CONTINUITY_PRESENT:
        raise DelegateError(
            "the transport is refused: --continuity-attempt N is required — the "
            f"execution of packet {args.packet!r} has continuity (a head exists "
            f"or the context declares it), and the integer is never inferred "
            f"from a textual attempt id (007-003 §2.2)")
    config = (_load_json(args.exec_config, "execution config")
              if args.exec_config else {})
    role = _as_text(request.get("role"))
    # 006-003 D3/§2.2: the model of the delegation is NEVER this interface's
    # business; a `model` left in the exec-config is ignored with a one-line
    # notice that names the delegation config.
    if _as_text(config.get("model")) is not None:
        _warn_legacy_model(destination, role)
    packet_bytes = packet_md.read_bytes()
    envelope = _run_adapter(adapter, project_root, args.packet, destination,
                            args.exec_config, packet_bytes,
                            _wait_timeout(config), attempt)
    # 006-005 PD-1/D-14: ONE attempt per dispatch, and it is the destination
    # module's — it registers its own record and declares its attempt in the
    # envelope; this interface RELAYS it and registers nothing (a second record
    # with a different observation would make the external path have two
    # writers of the same attempt).
    return _normalize_envelope(envelope)


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
