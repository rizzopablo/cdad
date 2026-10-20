#!/usr/bin/env python3
"""CDAD dispatch entry — the orchestrator's single entry (006-005).

One entry for the orchestrator, in its two paths, plus the bounded migration
step. The execution configuration layer is 006-005 U1a; the entry verbs are
U1b:

  * the runtime is resolved **explicitly and uniquely**: it enters by
    `--runtime <X>` (PD-8) and is never read from a project document, so the
    same project can be driven from several runtimes. An id with no runtime
    module — the `cdad_delegate_<id>.py` convention the interface already owns
    (005-009 PD-1) — fails closed naming the value;
  * the execution configuration of the external path is the **runtime section**
    of `runtimes.json` under the CDAD user config (PD-9): one section per
    runtime id, at the single location rule `cdad_delegate.cdad_config_dir`
    already owns. The configuration is never re-derived here (INV-12);
  * neither the `model` (it is `delegation.json`, ADR-033 D3) nor the credential
    route (ADR-033 point 6) lives in the section; a section that carries one is
    rejected, naming where it lives;
  * the retired `--exec-config` is **not an option**. Its token in argv — either
    form — is a usage error *before the verb is parsed*: the sweep is over argv,
    by exact token, on every verb (D-11/O-10), with one migration diagnostic
    that names the file, the section and the key-by-key correspondence (§2.6);
  * the bounded migration step
    `migrate --runtime X --legacy-exec-config FILE` (PD-25/§2.6.1) moves the
    correspondence keys into the section **only when it does not exist** — user
    data is never overwritten (INV-7) — supports `--dry-run` and never moves the
    `model` nor a credential value. U6-8: it does not move the
    `binary_version` either — the runtime version is observed, so the migration
    carries no number that can drift.

The entry verbs (U1b):

  * **`dispatch` (external path).** Resolves the runtime and its section,
    *derives* the internal configuration of the module as a transient file under
    `.cdad/` (removed when the call ends, never carrying a model or a credential
    value) and hands the transport to the ONE implementation that already owns
    it — the common interface `cdad_delegate.delegate`, which transports the
    published `PACKET.md` byte-identical to the runtime module. The module
    launches, waits, collects and **registers its own attempt**; this entry
    relays the module's envelope, `attempt` included, and neither registers nor
    stages anything (one writer per dispatch, PD-1/D-14). Reusing the interface
    is deliberate: a second transport implementation could diverge (§12).
  * **`record` (native path).** Builds the closed-key I8 observation, verifies
    the association with the evidence of this path (§2.3: the observable store
    columns, with the O-3 discrimination threshold, `unknown` when a key the
    store exposes cannot be evaluated and a **rejection** when an evaluable key
    contradicts). The `project` key has THREE values (U6-3): a session directory
    inside the authorized root coincides, an ANCESTOR of the root (the container
    the coordinator was started from) is not evaluable — it neither proves nor
    contradicts — and a foreign directory is a contradiction. It then registers
    the attempt through the existing command (`prepare --record-dispatch`) and,
    when it received the final text, stages it **byte-exact** under `.cdad/inbox`
    with its `RESULT.json` descriptor, declaring the artifact kind derived from
    the packet's role and subphase (§2.8/PD-23). It never runs `receive`: the
    receipt belongs to the re-entry protocol (§2.1).
  * **`capabilities`.** Asks the runtime module for its declared capabilities
    (§2.2) and answers the five keys; a module without that surface is declared
    `native_observation: false` with a `reason` that names the missing surface —
    never a silent degradation (O-6).

`record` reads the store **once** per invocation (PD-13: no polling, bounded
timeout) through the module's `--observe` surface, and only when there is a
motive: the invocation declares correlation inputs (`--session`/`--parent`) or
there is no byte-exact native result (the store is then the only evidence of the
association). The core is not a second writer: it never writes
`docs/.cdad-state.json`, never writes the store, and touches the ledger only
through the existing command (PD-2/INV-5); every other write stays under
`.cdad/`.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

# The canonical CLIs live next to this entry; importing them (never copying
# them) keeps ONE implementation of every helper (INV-12). `cdad_delegate` owns
# the destination convention and the user-config location rule; `cdad_result`
# owns the closed role/subphase -> artifact_kind table this entry derives from.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cdad_delegate  # noqa: E402
import cdad_result  # noqa: E402

# §2.6: the document, its version and the map of one section per runtime id.
RUNTIMES_CONFIG_NAME = "runtimes.json"
RUNTIMES_CONFIG_VERSION = 1
RUNTIMES_KEY = "runtimes"

# §2.6 correspondence: the keys the section carries — the ones the runtime
# module already reads, MOVED from the retired exec-config, never renamed.
SECTION_KEYS = (
    "binary", "binary_version", "mode", "server", "service", "auto",
    "sessions_db", "wait",
)

# §2.6.1 (U6-8): the keys the bounded migration step MOVES. `binary_version`
# is not one of them: the runtime version is OBSERVED (a difference with the
# configured one is declared and does not block), so the migration stops
# carrying a number that can drift. The key stays in the section's vocabulary
# (the owner may keep it as a note) and the key-by-key correspondence of the
# missing-section diagnostic keeps naming it.
MIGRATED_SECTION_KEYS = tuple(
    key for key in SECTION_KEYS if key != "binary_version")

# §2.6: the key of the delegation config that routes the credential (ADR-033
# point 6). It is named here only to say the section never carries it.
CREDENTIAL_ENV_FILE_KEY = "credential_env_file"

# §2.6/INV-12: keys that must NOT live in the section, with where they live.
FORBIDDEN_SECTION_KEYS = {
    "model": (f"the delegated model is chosen in "
              f"{cdad_delegate.DELEGATION_CONFIG_NAME} (ADR-033 D3)"),
    CREDENTIAL_ENV_FILE_KEY: (f"the credential route lives in "
                              f"{cdad_delegate.DELEGATION_CONFIG_NAME}"
                              f".{CREDENTIAL_ENV_FILE_KEY} (ADR-033 point 6)"),
}

# PD-1 of 005-009: the packet is published under `.cdad/packets/<id>/`.
PACKETS_RELPATH = Path(".cdad") / "packets"
PACKET_MD_NAME = "PACKET.md"
REQUEST_NAME = "REQUEST.json"

# §2.1: the staging surface of the native path (the step the re-entry protocol
# consumes: `.cdad/inbox/RESULT.json` plus the staged parts it points at).
INBOX_RELPATH = Path(".cdad") / "inbox"
DESCRIPTOR_NAME = "RESULT.json"
# The single part the common delivery produces today (§2.8): one role report.
DELIVERY_PART_NAME = "role-report"
# The transient directory of the derived internal configuration (§2.6).
RUNTIME_RELPATH = Path(".cdad") / "runtime"

# §2.1/§2.4: the closed observation schema and the library that validates it.
OBSERVATION_KEYS = (
    "runtime", "model_configured", "model_reported", "session", "started_at",
    "provenance",
)

# §2.3: the keys of the native correlation, the store column each one reads and
# the discriminating subset (O-3: the positive accreditation needs at least one
# of them; `agent` alone never accredits because two concurrent native
# dispatches of the same role share it).
CORRELATION_COLUMNS = {
    "parent": "parent_id",
    "agent": "agent",
    "moment": "time_created",
    "project": "directory",
}
DISCRIMINATING_KEYS = ("parent", "moment", "project")

# §2.3/INV-15 + U6-3: the third evaluation state of a key the store exposes. The
# `project` key has THREE values — the session directory is the root or lives
# inside it (`match`), is an ANCESTOR of the root (`not-evaluable`: the
# container folder the coordinator was started from can host other projects, so
# it neither proves nor contradicts), or is foreign to the root
# (`contradiction`). A not-evaluable key is not evidence in either direction: it
# neither blocks the positive accreditation of the keys that do discriminate nor
# is counted as a contradiction.
KEY_NOT_EVALUABLE = "not-evaluable"

# §2.2: the capability document of a runtime module.
CAPABILITY_KEYS = (
    "native_observation", "external_transport", "session_correlation",
    "version", "reason",
)

# Both waits are bounded and declared: a single `--observe` read (PD-13: no
# polling) and a single `--capabilities` question.
DEFAULT_OBSERVE_TIMEOUT_SECONDS = 30.0
CAPABILITIES_TIMEOUT_SECONDS = 30.0

VERBS = ("dispatch", "record", "capabilities", "migrate")
DEFAULT_VERB = "dispatch"

RETIRED_OPTION = "--exec-config"


class DispatchError(RuntimeError):
    """Fail-closed diagnostic of the dispatch entry."""


# ------------------------------------------------------------- configuration


def runtimes_config_path() -> Path:
    """`runtimes.json` under the ONE user-config location rule (INV-12).

    The rule is owned by the interface (`cdad_delegate.cdad_config_dir`); it is
    reused, never re-derived, so this reader and the installer's writer cannot
    diverge.
    """
    return cdad_delegate.cdad_config_dir() / RUNTIMES_CONFIG_NAME


def resolve_runtime_module(runtime: str) -> Path:
    """PD-8: the runtime id resolves to its module by the existing convention.

    A value without an available module is rejected naming the value; there is
    no project-level fallback (the id is the destination, V-9).
    """
    try:
        module = cdad_delegate._adapter_path(runtime)
    except cdad_delegate.DelegateError as exc:
        raise DispatchError(
            f"invalid value for --runtime: {exc}") from exc
    if not module.is_file():
        raise DispatchError(
            f"no runtime module for `{runtime}`: expected {module.name} next to "
            f"this entry — --runtime names the destination runtime and needs an "
            f"available module")
    return module


def _correspondence_lines() -> list[str]:
    """§2.6: where each retired exec-config key lives now (key by key)."""
    moved = ", ".join(f"`{key}`" for key in SECTION_KEYS)
    return [
        f"  `runtime`    -> the --runtime flag and, with it, the id of the "
        f"`{RUNTIMES_KEY}` section in {RUNTIMES_CONFIG_NAME}",
        f"  {moved} -> the same keys, inside the runtime section",
        f"  `model`      -> {cdad_delegate.DELEGATION_CONFIG_NAME} (ADR-033 D3: "
        f"the model is chosen in a single place, never in {RUNTIMES_CONFIG_NAME})",
        f"  (credential) -> {cdad_delegate.DELEGATION_CONFIG_NAME}"
        f".{CREDENTIAL_ENV_FILE_KEY}, or the default "
        f"cdad/{cdad_delegate.DELEGATION_ENV_FILE_NAME} — never in "
        f"{RUNTIMES_CONFIG_NAME}",
    ]


def _missing_section_message(runtime: str) -> str:
    return "\n".join([
        f"no execution configuration for runtime `{runtime}`: "
        f"{RUNTIMES_CONFIG_NAME} ({runtimes_config_path()}) has no `{runtime}` "
        f"section under `{RUNTIMES_KEY}`",
        f"`{RUNTIMES_CONFIG_NAME}` is the single source for the external path "
        f"(one section per runtime id); the retired exec-config keys live there "
        f"now, key by key:",
        *_correspondence_lines(),
    ])


def retired_option_message(token: str) -> str:
    """D-11: the single migration diagnostic of the retired `--exec-config`."""
    return "\n".join([
        f"`{RETIRED_OPTION}` is not an option of this entry (got {token!r}): the "
        f"execution configuration is the runtime section of "
        f"{RUNTIMES_CONFIG_NAME}, read under the CDAD user config",
        f"the retired exec-config keys live there now, key by key:",
        *_correspondence_lines(),
        f"migrate an existing exec-config explicitly with: cdad_dispatch.py "
        f"migrate --runtime <X> --legacy-exec-config <file>",
    ])


def load_runtime_section(runtime: str) -> dict[str, Any]:
    """PD-9: read and validate the runtime section — the single config source.

    Absent section or absent document ⇒ the fail-closed diagnostic with the
    correspondence; a forbidden key ⇒ rejection naming where it lives.
    """
    path = runtimes_config_path()
    section = _section_of(_read_document(path), runtime) if path.is_file() else None
    if not isinstance(section, dict):
        raise DispatchError(_missing_section_message(runtime))
    for key, guidance in FORBIDDEN_SECTION_KEYS.items():
        if key in section:
            raise DispatchError(
                f"`{key}` must not live in the {RUNTIMES_CONFIG_NAME} section "
                f"`{runtime}` ({path}): {guidance}. Remove it from the section — "
                f"the section carries only the execution configuration keys")
    return section


def _read_document(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DispatchError(
            f"{RUNTIMES_CONFIG_NAME} is not readable JSON ({path}): {exc}") from exc


def _load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DispatchError(f"{label} is not readable JSON ({path}): {exc}") from exc


def _section_of(document: Any, runtime: str) -> Any:
    runtimes = document.get(RUNTIMES_KEY) if isinstance(document, dict) else None
    return runtimes.get(runtime) if isinstance(runtimes, dict) else None


def _internal_config_path(root: Path, runtime: str) -> Path:
    """§2.6: the transient file the module reads, inside the already
    git-ignored coordination space (`.cdad/`), unique per invocation."""
    return (root / RUNTIME_RELPATH
            / f".internal-{runtime}-{os.getpid()}.json")


def derived_internal_config(root: Path, runtime: str,
                            section: dict[str, Any]) -> Path:
    """§2.6: DERIVE the internal configuration of the module from the section.

    It carries only the correspondence keys — never the `model` (which lives in
    `delegation.json`) nor any credential value — plus the runtime id, which is
    the value of `--runtime` and is never resolved from a project document. The
    caller removes the file when the call ends.
    """
    directory = root / RUNTIME_RELPATH
    directory.mkdir(parents=True, exist_ok=True)
    path = _internal_config_path(root, runtime)
    document = {key: section[key] for key in SECTION_KEYS if key in section}
    document["runtime"] = runtime
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    return path


# ------------------------------------------------------------------ migration


def find_retired_option(argv: Sequence[str]) -> str | None:
    """D-11/O-10: sweep argv, by EXACT token, before the verb is parsed.

    `--legacy-exec-config` (the migration flag) is a different token and is
    never caught here.
    """
    for token in argv:
        if token == RETIRED_OPTION or token.startswith(f"{RETIRED_OPTION}="):
            return token
    return None


def section_from_legacy(document: dict[str, Any]) -> dict[str, Any]:
    """§2.6.1: move exactly the correspondence keys the migration carries.

    `runtime` becomes the section id, and `model`/the credential route are
    never moved — the report tells where they live instead. `binary_version` is
    not moved either (U6-8): the version is observed at runtime, so the
    migration does not carry a number that can drift.
    """
    return {key: document[key] for key in MIGRATED_SECTION_KEYS
            if key in document}


def migration_target(path: Path, runtime: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """The document to write and its `runtimes` map, refusing an existing section.

    Returns a shared, mutable pair so the caller adds the section and writes the
    same document; nothing is written here.
    """
    if not path.is_file():
        runtimes: dict[str, Any] = {}
        return {"version": RUNTIMES_CONFIG_VERSION, RUNTIMES_KEY: runtimes}, runtimes
    document = _read_document(path)
    runtimes = document.get(RUNTIMES_KEY) if isinstance(document, dict) else None
    if not isinstance(runtimes, dict):
        raise DispatchError(
            f"{RUNTIMES_CONFIG_NAME} ({path}) has no `{RUNTIMES_KEY}` object to "
            f"migrate into")
    if runtime in runtimes:
        raise DispatchError(
            f"{RUNTIMES_CONFIG_NAME} ({path}) already has a section for runtime "
            f"`{runtime}`: the migration never overwrites it (user data, INV-7) "
            f"— edit it by hand or remove the section first")
    return document, runtimes


def _load_legacy_document(raw_path: str) -> dict[str, Any]:
    path = Path(raw_path)
    if not path.is_file():
        raise DispatchError(f"--legacy-exec-config not found: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DispatchError(
            f"--legacy-exec-config is not readable JSON ({path}): {exc}") from exc
    if not isinstance(document, dict):
        raise DispatchError(f"--legacy-exec-config must be a JSON object: {path}")
    return document


def _migration_report(runtime: str, section: dict[str, Any], path: Path, *,
                      dry_run: bool, as_json: bool) -> None:
    """PD-25: the section, key and value by key and value, plus where the model
    and the credential live (they are never moved)."""
    action = "would be written (dry-run)" if dry_run else "written"
    lines = [f"{RUNTIMES_CONFIG_NAME} section `{runtime}` {action} in {path}:"]
    lines += [f"  {key}: {section[key]}"
              for key in MIGRATED_SECTION_KEYS if key in section]
    lines += [
        f"  model: {cdad_delegate.DELEGATION_CONFIG_NAME} — the delegated model "
        f"is chosen there (ADR-033 D3), never in {RUNTIMES_CONFIG_NAME}",
        f"  credential: {cdad_delegate.DELEGATION_CONFIG_NAME}"
        f".{CREDENTIAL_ENV_FILE_KEY} (default "
        f"cdad/{cdad_delegate.DELEGATION_ENV_FILE_NAME}) — never in "
        f"{RUNTIMES_CONFIG_NAME}",
    ]
    if as_json:
        print(json.dumps({
            "runtime": runtime,
            "config": str(path),
            "dry_run": dry_run,
            "written": not dry_run,
            "section": section,
        }, indent=2, sort_keys=True))
    print("\n".join(lines))


def migrate(runtime: str, legacy_path: str, *, dry_run: bool, as_json: bool) -> int:
    """PD-25/§2.6.1: move one retired exec-config into the runtime section.

    Writes the section only when it does not exist; `--dry-run` writes nothing.
    """
    section = section_from_legacy(_load_legacy_document(legacy_path))
    path = runtimes_config_path()
    document, runtimes = migration_target(path, runtime)
    runtimes[runtime] = section
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    _migration_report(runtime, section, path, dry_run=dry_run, as_json=as_json)
    return 0


# --------------------------------------------------------------- common shape


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _envelope(*, attempt: str | None, session: str | None, termination: str,
              delivery_ref: str | None, diagnosis: str | None) -> dict[str, Any]:
    """§2.1: exactly the keys of `OUTPUT_KEYS`, `termination` in the closed
    vocabulary the interface declares (`cdad_delegate.TERMINATION_VOCABULARY`)."""
    if termination not in cdad_delegate.TERMINATION_VOCABULARY:
        termination = "unknown"
    return {
        "attempt": _as_text(attempt),
        "session": _as_text(session),
        "termination": termination,
        "delivery_ref": _as_text(delivery_ref),
        "diagnosis": _as_text(diagnosis),
    }


def _report_envelope(envelope: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(envelope, ensure_ascii=False, sort_keys=True))
        return
    print(" ".join(
        f"{key}={envelope[key]!r}" for key in cdad_delegate.OUTPUT_KEYS
        if envelope.get(key) is not None))


def _project_root(raw: str | None) -> Path:
    root = Path(raw) if raw else Path.cwd()
    if not root.is_dir():
        raise DispatchError(f"--project-root is not a directory: {root}")
    return root.resolve()


def _packet_dir(root: Path, packet: str) -> Path:
    return root / PACKETS_RELPATH / packet


def _known_packet(root: Path, packet: str, verb: str) -> tuple[Path, Path]:
    """Resolve a packet already published by `prepare` (fail closed otherwise)."""
    directory = _packet_dir(root, packet)
    packet_md = directory / PACKET_MD_NAME
    request_path = directory / REQUEST_NAME
    if not packet_md.is_file() or not request_path.is_file():
        raise DispatchError(
            f"unknown packet {packet!r}: no packet published under {directory} — "
            f"prepare the packet before {verb}")
    return packet_md, request_path


# ------------------------------------------------------- external path (U1b)


def dispatch(runtime: str, project_root: str | None, packet: str | None, *,
             as_json: bool) -> int:
    """§2.1 (external path): resolve the runtime and its single configuration
    source, then hand the transport to the ONE implementation that owns it.

    The module registers its own attempt (PD-1) and this entry relays its
    envelope — `attempt` included — without registering or staging anything.
    """
    resolve_runtime_module(runtime)
    section = load_runtime_section(runtime)
    if not packet:
        raise DispatchError(
            "dispatch requires --packet <id>: the id of a packet already "
            "published by `cdad_packet.py prepare`")
    root = _project_root(project_root)
    _known_packet(root, packet, "dispatching")
    envelope = _transport(runtime, section, root, packet)
    _report_envelope(envelope, as_json=as_json)
    return 0


def _transport(runtime: str, section: dict[str, Any], root: Path,
               packet: str) -> dict[str, Any]:
    """Delegate the external transport to the common interface (one
    implementation of launch/wait/collect/transport, §2.1/§12)."""
    derived = derived_internal_config(root, runtime, section)
    try:
        output = cdad_delegate.delegate(argparse.Namespace(
            project_root=str(root),
            packet=packet,
            destination=runtime,
            exec_config=str(derived),
        ))
    except cdad_delegate.DelegateError as exc:
        raise DispatchError(f"the external transport failed: {exc}") from exc
    finally:
        derived.unlink(missing_ok=True)
    return {key: output.get(key) for key in cdad_delegate.OUTPUT_KEYS}


# --------------------------------------------------------- native path (U1b)


def _observe_timeout(section: dict[str, Any]) -> float:
    wait = section.get("wait")
    if isinstance(wait, dict):
        seconds = wait.get("timeout_seconds")
        if isinstance(seconds, (int, float)) and seconds > 0:
            return float(seconds)
    return DEFAULT_OBSERVE_TIMEOUT_SECONDS


def _run_module(module: Path, argv: Sequence[str], *,
                timeout: float) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(argv, capture_output=True, text=True,
                              timeout=timeout, cwd=str(module.parent))
    except (OSError, subprocess.SubprocessError):
        return None


def observe_model(*, module: Path, runtime: str, section: dict[str, Any],
                  root: Path, packet: str, session: str | None,
                  parent: str | None, agent: str | None = None,
                  since: str | None = None
                  ) -> tuple[dict[str, Any] | None, str | None, str | None]:
    """§2.2/§2.3: ONE bounded read of the store through the module's `--observe`.

    Returns `(row, problem, detail)`: the observable row (or `None` when the
    module answers `null`), and, when the surface is unusable, the reason that
    **names the missing surface** (never a silent degradation, O-6/INV-4). The
    module (which knows its store) receives the packet's `agent` and the
    declared `--since` so IT selects the candidate and hands an interpretable
    instant; `detail` is the declared diagnostic of a read that accredits no row
    (no candidate, ambiguity, uninterpretable instant) — never a rejection.
    """
    derived = derived_internal_config(root, runtime, section)
    argv = [
        sys.executable, str(module),
        "--project-root", str(root),
        "--packet-id", packet,
        "--destination", runtime,
        "--exec-config", str(derived),
        "--observe",
    ]
    if session:
        argv += ["--session", session]
    if parent:
        argv += ["--parent", parent]
    if agent:
        argv += ["--agent", agent]
    if since:
        argv += ["--since", since]
    try:
        proc = _run_module(module, argv, timeout=_observe_timeout(section))
    finally:
        derived.unlink(missing_ok=True)
    if proc is None:
        return None, (f"the runtime module {module.name} could not be run to read "
                      f"the store (`--observe`)"), None
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return None, (f"the runtime module {module.name} answered `--observe` with "
                      f"rc={proc.returncode}: {detail[:200]}"), None
    text = (proc.stdout or "").strip()
    try:
        row = json.loads(text)
    except ValueError:
        return None, (f"the runtime module {module.name} does not declare the "
                      f"`--observe` surface of §2.2 (its answer is not the "
                      f"observable row JSON): {text[:200]!r}"), None
    detail = (proc.stderr or "").strip() or None
    if row is None:
        return None, None, detail
    if not isinstance(row, dict):
        return None, (f"the observable row of `--observe` is not an object: "
                      f"{row!r}"), None
    return row, None, detail


@dataclass(frozen=True)
class Correlation:
    """§2.3: the outcome of the native association for one attempt."""

    verified: bool
    session: str | None
    model_reported: str | None
    note: str
    model_note: str


def _compare_key(observed: Any, declared: Any) -> str:
    if _as_text(observed) is None or _as_text(declared) is None:
        return "unknown"
    return "match" if observed == declared else "contradiction"


def _membership_key(observed: Any, root: Path) -> str:
    """§2.3/INV-15 + U6-3: the project is corroborated BY MEMBERSHIP — the
    session's directory is the authorized root or lives inside it — never by a
    rigid `directory == root`. Three values, never two:

    * the directory is the root or lives INSIDE it ⇒ `match` (membership);
    * the directory is an ANCESTOR of the root — the container folder from which
      the coordinator was started — ⇒ `not-evaluable`: the container can host
      other projects, so it neither proves nor contradicts the walk (U6-3: this
      is the legitimate E1 layout the rigid rule used to reject);
    * anything else (neither inside nor an ancestor) ⇒ `contradiction`.
    """
    directory = _as_text(observed)
    if directory is None:
        return "unknown"
    try:
        resolved = Path(directory).expanduser().resolve()
    except OSError:
        return "unknown"
    if resolved == root or root in resolved.parents:
        return "match"
    return KEY_NOT_EVALUABLE if resolved in root.parents else "contradiction"


def _instant(value: Any) -> datetime | None:
    text = _as_text(value)
    if text is None:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _moment_key(observed: Any, since: str | None) -> str:
    declared = _instant(since)
    row_instant = _instant(observed)
    if declared is None or row_instant is None:
        return "unknown"
    if declared.tzinfo is None and row_instant.tzinfo is not None:
        declared = declared.replace(tzinfo=row_instant.tzinfo)
    if row_instant.tzinfo is None and declared.tzinfo is not None:
        row_instant = row_instant.replace(tzinfo=declared.tzinfo)
    return "match" if row_instant > declared else "contradiction"


def _key_states(row: dict[str, Any], request: dict[str, Any], *,
                parent: str | None, since: str | None,
                root: Path) -> dict[str, str]:
    """Evaluate the keys the observed store version exposes.

    A key whose column the row does not carry is simply NOT part of the evidence
    this version offers (it is not evaluated). A key the row DOES expose but
    whose declared input is missing is `unknown` — never compared against a
    supposed value (§2.3).
    """
    states: dict[str, str] = {}
    if CORRELATION_COLUMNS["parent"] in row:
        states["parent"] = (_compare_key(row.get(CORRELATION_COLUMNS["parent"]),
                                         parent)
                            if parent else "unknown")
    if CORRELATION_COLUMNS["agent"] in row:
        agent = _as_text(request.get("agent"))
        states["agent"] = (_compare_key(row.get(CORRELATION_COLUMNS["agent"]), agent)
                           if agent else "unknown")
    if CORRELATION_COLUMNS["moment"] in row:
        states["moment"] = (_moment_key(row.get(CORRELATION_COLUMNS["moment"]), since)
                           if since else "unknown")
    if CORRELATION_COLUMNS["project"] in row:
        states["project"] = _membership_key(
            row.get(CORRELATION_COLUMNS["project"]), root)
    return states


def correlate(row: dict[str, Any] | None, request: dict[str, Any], *,
              packet: str, parent: str | None, since: str | None, root: Path,
              problem: str | None, detail: str | None = None) -> Correlation:
    """§2.3: three outcomes with their own consequence.

    `verified` when every evaluated key matches and at least one DISCRIMINATING
    key was evaluated (O-3); `unknown` when a key the store exposes cannot be
    evaluated or no discriminating key was; and a **rejection** — raised, never
    returned as `unknown` and never as an accepted delivery — when an evaluable
    key contradicts. A key that is NOT EVALUABLE for the walk (U6-3: the project
    key when the session directory is an ancestor of the root) is named in the
    diagnosis but is evidence in neither direction: it neither blocks the
    accreditation the discriminating keys give nor counts as a contradiction.

    U6-4: `detail` is the module's declared diagnostic of a read that accredits
    no row (no candidate, ambiguity, uninterpretable instant). It is named in
    the non-verified note, never turned into a rejection, and a non-verified
    note also names the keys that DID match.
    """
    if row is None:
        text = detail or problem or ("the store offered no observable session row")
        return Correlation(
            verified=False, session=None, model_reported=None,
            note=(f"not verified: {text}; no discriminating key "
                  f"(parent, moment, project) was evaluated — no session is "
                  f"accredited (INV-2)"),
            model_note="not observed: the identity of the attempt is not verified")
    states = _key_states(row, request, parent=parent, since=since, root=root)
    contradictions = [key for key in CORRELATION_COLUMNS
                      if states.get(key) == "contradiction"]
    if contradictions:
        named = ", ".join(f"`{key}`" for key in contradictions)
        raise DispatchError(
            f"the native identity contradicts the observation of packet "
            f"{packet!r}: the {named} key does not match — the entry refuses the "
            f"delivery and never accredits a session the store denies (§2.3, "
            f"INV-2). The session directory must belong to the authorized "
            f"project root, and the declared parent/instant must be the observed "
            f"one")
    unknowns = [key for key in CORRELATION_COLUMNS
                if states.get(key) == "unknown"]
    not_evaluable = [key for key in CORRELATION_COLUMNS
                     if states.get(key) == KEY_NOT_EVALUABLE]
    matched = [key for key in DISCRIMINATING_KEYS if states.get(key) == "match"]
    session_id = _as_text(row.get("id"))
    if not unknowns and matched:
        if session_id is not None:
            verified_note = (
                f"verified: the observable row of the module's single store "
                f"read matches the declared evidence "
                f"({', '.join(matched)}) — the session comes from the "
                f"store, never from the invocation")
            if not_evaluable:
                verified_note += (
                    "; not evaluable: "
                    + ", ".join(f"`{key}`" for key in not_evaluable)
                    + " (the session directory is an ancestor of the "
                      "authorized project root: it neither proves nor "
                      "contradicts the project)")
            return Correlation(
                verified=True, session=session_id,
                model_reported=_as_text(row.get("model")),
                note=verified_note,
                model_note=("durable session row (the module's `--observe`): "
                            "session_v2.model" if _as_text(row.get("model"))
                            else "the observed row does not carry a model column: "
                                 "the module did not report a model"))
        unknowns = [*unknowns, "id"]
    reasons: list[str] = []
    if unknowns:
        reasons.append("not evaluable: "
                       + ", ".join(f"`{key}`" for key in unknowns))
    if not_evaluable:
        reasons.append("not evaluable: "
                       + ", ".join(f"`{key}`" for key in not_evaluable)
                       + " (the session directory is an ancestor of the "
                         "authorized project root: it neither proves nor "
                         "contradicts the project)")
    if not matched:
        reasons.append("no discriminating key (parent, moment, project) was "
                       "evaluated and matched")
    else:
        reasons.append("matched: "
                       + ", ".join(f"`{key}`" for key in matched))
    if detail:
        reasons.append(detail)
    note = ("not verified: " + "; ".join(reasons)
            + " — no session is accredited and nothing is delivered by this "
              "path unless a byte-exact native result is provided (PD-6/INV-2)")
    return Correlation(verified=False, session=None, model_reported=None,
                       note=note,
                       model_note=("not observed: the identity of the attempt is "
                                   "not verified"))


def _read_native_result(raw: str | None) -> bytes | None:
    """PD-3/§2.1: the final text exactly as it was received (`FILE` or `-`),
    never re-typed, summarised nor regenerated; absent means no delivery."""
    if raw is None:
        return None
    if raw == "-":
        payload = sys.stdin.buffer.read()
        label = "stdin"
    else:
        path = Path(raw)
        if not path.is_file():
            raise DispatchError(f"--native-result not found: {path}")
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise DispatchError(f"--native-result is not readable ({path}): {exc}") from exc
        label = str(path)
    if not payload:
        raise DispatchError(
            f"--native-result ({label}) is empty: without final text or artifact "
            f"there is no delivery (INV-1)")
    return payload


def _observation_payload(*, runtime: str, correlation: Correlation) -> dict[str, Any]:
    """§2.4/INV-8: the closed-key I8 observation of the native path.

    `model_configured` is null with declared provenance — CDAD does not choose
    the model of the internal delegation (ADR-033 D2, INV-9) — and `session` is
    the observed one or null with the declared reason (PD-6).
    """
    return {
        "runtime": runtime,
        "model_configured": None,
        "model_reported": correlation.model_reported,
        "session": correlation.session,
        "started_at": _now(),
        "provenance": {
            "runtime": ("the --runtime flag: the destination runtime id, never "
                        "read from a project document"),
            "model_configured": ("CDAD does not choose the model of the internal "
                                 "delegation (ADR-033 D2): the runtime fixes it"),
            "model_reported": correlation.model_note,
            "session": correlation.note,
            "started_at": "the entry's clock (UTC)",
        },
    }


def _register_attempt(root: Path, packet: str, request: dict[str, Any],
                      attempt_id: str, observation: dict[str, Any]) -> None:
    """PD-1/§2.4: the ONE registration of the native path, written through the
    command that already owns the ledger and the state transition
    (`cdad_packet.py prepare --record-dispatch`, INV-5)."""
    if set(observation) != set(OBSERVATION_KEYS):
        raise DispatchError(
            "the observation does not carry the closed schema "
            f"({', '.join(OBSERVATION_KEYS)})")
    execution_id = _as_text(request.get("execution_id"))
    if execution_id is None:
        raise DispatchError(f"packet {packet!r} request has no execution_id")
    packet_cli = _SCRIPT_DIR / cdad_delegate.PACKET_CLI_NAME
    if not packet_cli.is_file():
        raise DispatchError(
            f"cannot register the attempt: {cdad_delegate.PACKET_CLI_NAME} is not "
            f"next to this entry")
    stage = root / ".cdad" / "executions" / execution_id
    stage.mkdir(parents=True, exist_ok=True)
    observation_path = stage / f".{attempt_id}.observation.json"
    payload = (json.dumps(observation, ensure_ascii=False, sort_keys=True,
                          indent=2) + "\n").encode("utf-8")
    try:
        observation_path.write_bytes(payload)
    except OSError as exc:
        raise DispatchError(f"cannot stage the dispatch observation: {exc}") from exc
    try:
        proc = subprocess.run(
            [sys.executable, str(packet_cli), "prepare",
             "--project-root", str(root),
             "--record-dispatch", packet,
             "--attempt-id", attempt_id,
             "--input", str(observation_path)],
            capture_output=True, text=True, cwd=str(root))
    finally:
        observation_path.unlink(missing_ok=True)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise DispatchError(
            f"the attempt {attempt_id!r} could not be registered: {detail[:300]}")


def derive_artifact_kind(role: Any, substage: Any) -> str:
    """§2.8/PD-23/INV-14: the kind of the delivered part comes from the closed
    role/subphase table (`cdad_result`), never from a hardcoded constant."""
    role_name = _as_text(role)
    if role_name is None:
        raise DispatchError(
            "the packet request declares no role: the artifact kind of the "
            "delivered part cannot be derived (§2.8)")
    kinds = cdad_result._allowed_kinds(role_name, substage if isinstance(substage, str) else "")
    if "role-report" in kinds:
        return "role-report"
    if len(kinds) == 1:
        return next(iter(kinds))
    raise DispatchError(
        f"the closed role/subphase table does not determine a single artifact "
        f"kind for role {role_name!r}/substage {substage!r}: "
        f"{sorted(kinds) or 'no kind admitted'} — the delivered part declares one "
        f"kind (§2.8/PD-23)")


def stage_delivery(root: Path, request: dict[str, Any], packet: str,
                   attempt_id: str, kind: str, payload: bytes) -> Path:
    """§2.1/PD-3: stage the byte-exact part under `.cdad/inbox` and write the
    `RESULT.json` descriptor the re-entry protocol consumes, declaring the kind
    derived from role and subphase. Nothing here approves anything."""
    execution_id = _as_text(request.get("execution_id"))
    feature_id = _as_text(request.get("feature_id"))
    if execution_id is None or feature_id is None:
        raise DispatchError(
            f"packet {packet!r} request lacks execution_id/feature_id")
    inbox = root / INBOX_RELPATH
    inbox.mkdir(parents=True, exist_ok=True)
    part_name = f"{attempt_id}-{DELIVERY_PART_NAME}"
    staged = inbox / f"{part_name}.md"
    staged.write_bytes(payload)
    descriptor = {
        "schema_version": 1,
        "execution_id": execution_id,
        "packet_id": packet,
        "feature_id": feature_id,
        "source": {"kind": "staged-file", "sdk_message_ref": None},
        "parts": [{
            "name": part_name,
            "artifact_kind": kind,
            "staged_path": f"{INBOX_RELPATH.as_posix()}/{part_name}.md",
        }],
        "run_evidence_ref": None,
    }
    descriptor_path = inbox / DESCRIPTOR_NAME
    descriptor_path.write_text(
        json.dumps(descriptor, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")
    return descriptor_path


def record(runtime: str, project_root: str | None, packet: str | None,
           attempt_id: str | None, *, native_result: str | None,
           session: str | None, parent: str | None, since: str | None,
           as_json: bool) -> int:
    """§2.1 (native path): the single body of observation + registration + the
    mechanical staging step; the receipt belongs to the re-entry protocol."""
    module = resolve_runtime_module(runtime)
    section = load_runtime_section(runtime)
    if not packet:
        raise DispatchError(
            "record requires --packet <id>: the dispatched packet this attempt "
            "belongs to")
    if not attempt_id:
        raise DispatchError(
            "record requires --attempt-id <id>: the identity of the attempt this "
            "invocation registers")
    root = _project_root(project_root)
    _known_packet(root, packet, "recording its attempt")
    request = _load_json(_packet_dir(root, packet) / REQUEST_NAME, "packet request")
    if not isinstance(request, dict):
        raise DispatchError(
            f"the packet request is not an object: {_packet_dir(root, packet) / REQUEST_NAME}")
    kind = derive_artifact_kind(request.get("role"), request.get("substage"))

    payload = _read_native_result(native_result)
    # ONE bounded read, only when there is a motive (§2.1/PD-13).
    row: dict[str, Any] | None = None
    problem: str | None = None
    if session or parent or payload is None:
        row, problem, detail = observe_model(
            module=module, runtime=runtime, section=section, root=root,
            packet=packet, session=session, parent=parent,
            agent=_as_text(request.get("agent")), since=since)
        if problem is not None and payload is None:
            raise DispatchError(
                f"the native observation is not available and no byte-exact "
                f"native result was provided: {problem}. Without either there is "
                f"no delivery by this path (§2.2, INV-4)")
    else:
        problem = ("no correlation evidence was declared (--session/--parent) and "
                   "the byte-exact native result travels with the lower guarantee "
                   "of PD-6: the store is read only when there is a motive (one "
                   "bounded read per invocation)")
        detail = None
    correlation = correlate(row, request, packet=packet, parent=parent,
                            since=since, root=root, problem=problem,
                            detail=detail)

    _register_attempt(root, packet, request, attempt_id,
                      _observation_payload(runtime=runtime,
                                           correlation=correlation))
    notes = [correlation.note]
    delivery_ref: str | None = None
    termination = "unknown"
    if payload is not None:
        delivery_ref = str(stage_delivery(root, request, packet, attempt_id,
                                          kind, payload))
        termination = "completed"
    else:
        notes.append(
            "no final text or artifact was provided: nothing was staged, no "
            "descriptor was written and the registered attempt is the only effect "
            "(PD-4/INV-1, the receipt is the protocol's)")
    envelope = _envelope(attempt=attempt_id, session=correlation.session,
                         termination=termination, delivery_ref=delivery_ref,
                         diagnosis="; ".join(notes))
    _report_envelope(envelope, as_json=as_json)
    return 0


# -------------------------------------------------------------- capabilities


def _uncredited_capabilities(reason: str) -> dict[str, Any]:
    return {
        "native_observation": False,
        "external_transport": False,
        "session_correlation": False,
        "version": "unknown",
        "reason": reason,
    }


def module_capabilities(module: Path, *, runtime: str,
                        section: dict[str, Any], root: Path) -> dict[str, Any]:
    """§2.2/PD-10/O-6: the module's declared capabilities, or the fail-closed
    declaration naming the missing surface (never a silent degradation).

    The runtime section travels to the module on the same channel the external
    path already uses (§2.6): the derived transient configuration handed by
    `--exec-config`, removed when the call ends. Without it the module cannot
    observe the configured binary or store and could only answer `unknown`
    (U6-1): the capability of a configured runtime is observed, never supposed.
    """
    derived = derived_internal_config(root, runtime, section)
    try:
        proc = _run_module(
            module,
            [sys.executable, str(module), "--capabilities",
             "--exec-config", str(derived)],
            timeout=CAPABILITIES_TIMEOUT_SECONDS)
    finally:
        derived.unlink(missing_ok=True)
    if proc is None:
        return _uncredited_capabilities(
            f"the runtime module {module.name} could not be run to answer "
            f"`--capabilities` (the surface of §2.2)")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return _uncredited_capabilities(
            f"the runtime module {module.name} does not declare the "
            f"`--capabilities` surface of §2.2 (rc={proc.returncode}): "
            f"{detail[:200]}")
    text = (proc.stdout or "").strip()
    try:
        document = json.loads(text)
    except ValueError:
        return _uncredited_capabilities(
            f"the runtime module {module.name} does not declare the "
            f"`--capabilities` surface of §2.2 (its answer is not the capability "
            f"document JSON): {text[:200]!r}")
    if not isinstance(document, dict) or set(document) != set(CAPABILITY_KEYS):
        return _uncredited_capabilities(
            f"the runtime module {module.name} does not declare the capability "
            f"document of §2.2 (expected {', '.join(CAPABILITY_KEYS)}; got "
            f"{sorted(document) if isinstance(document, dict) else type(document).__name__})")
    return document


def capabilities(runtime: str, project_root: str | None, *,
                 as_json: bool) -> int:
    """PD-10/PD-25: the declared capabilities of the runtime, from its module.

    The section of `runtimes.json` is resolved first (PD-9: without it the verb
    fails closed with the single-source diagnostic) and reaches the module as
    the derived configuration, exactly as the external path delivers it; the
    answer therefore reports the OBSERVED binary version and store columns of
    the configured runtime, never a supposed capability (U6-1).
    """
    module = resolve_runtime_module(runtime)
    section = load_runtime_section(runtime)
    root = _project_root(project_root)
    document = module_capabilities(module, runtime=runtime, section=section,
                                   root=root)
    if as_json:
        print(json.dumps(document, ensure_ascii=False, sort_keys=True))
    else:
        print(" ".join(f"{key}={document[key]!r}" for key in CAPABILITY_KEYS))
    return 0


# ---------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdad_dispatch.py",
        description=(
            "The orchestrator's single entry (006-005). The runtime enters "
            "explicitly by --runtime (PD-8) and its execution configuration is "
            "the runtime section of runtimes.json under the CDAD user config "
            "(PD-9); `dispatch` runs the external transport through the runtime "
            "module, `record` registers the attempt of the native path, "
            "`capabilities` asks the module and the bounded `migrate` verb moves "
            "a retired exec-config into the section (PD-25)."
        ),
    )
    parser.add_argument(
        "verb", nargs="?", choices=VERBS, default=DEFAULT_VERB,
        help="dispatch (default) | record | capabilities | migrate")
    parser.add_argument(
        "--project-root", default=None,
        help="project root; never the coordinator's cwd by assumption")
    parser.add_argument(
        "--packet", default=None,
        help="id of a canonical packet already published by prepare")
    parser.add_argument(
        "--runtime", required=True,
        help="destination runtime id; the id of its runtimes.json section")
    parser.add_argument(
        "--attempt-id", default=None,
        help="record only: the identity of the attempt this invocation registers "
             "(its record in the dispatch ledger)")
    parser.add_argument(
        "--native-result", default=None,
        help="record only: the file carrying the byte-exact final text of the "
             "role ('-' reads it from stdin); staged unchanged")
    parser.add_argument(
        "--session", default=None,
        help="record only: the session id the native dispatch observed")
    parser.add_argument(
        "--parent", default=None,
        help="record only: the session that dispatched the native child")
    parser.add_argument(
        "--since", default=None,
        help="record only: the declared instant of the native dispatch (the "
             "moment key)")
    parser.add_argument(
        "--legacy-exec-config", default=None,
        help="migrate only: the one retired exec-config document to move")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="migrate only: print the section that would be written, write nothing")
    parser.add_argument(
        "--json", action="store_true",
        help="machine-readable form of the report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    retired = find_retired_option(arguments)
    if retired is not None:
        print(retired_option_message(retired), file=sys.stderr)
        return 2
    args = build_parser().parse_args(arguments)
    try:
        if args.verb == "migrate":
            if not args.legacy_exec_config:
                raise DispatchError(
                    "migrate requires --legacy-exec-config <file>: it is the "
                    "only document the migration reads (no location is probed)")
            return migrate(args.runtime, args.legacy_exec_config,
                           dry_run=args.dry_run, as_json=args.json)
        if args.verb == "capabilities":
            return capabilities(args.runtime, args.project_root,
                                as_json=args.json)
        if args.verb == "record":
            return record(args.runtime, args.project_root, args.packet,
                          args.attempt_id, native_result=args.native_result,
                          session=args.session, parent=args.parent,
                          since=args.since, as_json=args.json)
        return dispatch(args.runtime, args.project_root, args.packet,
                        as_json=args.json)
    except DispatchError as exc:
        print(f"cdad_dispatch: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
