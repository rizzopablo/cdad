#!/usr/bin/env python3
"""CDAD dispatch entry — the execution configuration layer (006-005 U1a).

One entry for the orchestrator. This unit carries the **execution
configuration** and nothing else:

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
    `model` nor a credential value.

The rest of the surface (`dispatch` transport, `record`, `capabilities`) is
006-005 U1b. The verbs are declared so argv is parsed as the final CLI; the ones
this unit does not implement fail closed with a named diagnostic instead of
pretending.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import cdad_delegate

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

VERBS = ("dispatch", "record", "capabilities", "migrate")
DEFAULT_VERB = "dispatch"
# The verbs this unit does not implement yet (006-005 U1b): they fail closed.
U1A_DEFERRED_VERBS = ("record", "capabilities")

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


def _section_of(document: Any, runtime: str) -> Any:
    runtimes = document.get(RUNTIMES_KEY) if isinstance(document, dict) else None
    return runtimes.get(runtime) if isinstance(runtimes, dict) else None


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
    """§2.6.1: move exactly the correspondence keys.

    `runtime` becomes the section id, and `model`/the credential route are
    never moved — the report tells where they live instead.
    """
    return {key: document[key] for key in SECTION_KEYS if key in document}


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
    lines += [f"  {key}: {section[key]}" for key in SECTION_KEYS if key in section]
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


# ------------------------------------------------------------------- verbs


def dispatch(runtime: str, project_root: str | None, packet: str | None) -> int:
    """The external path: resolve the runtime, then its configuration section.

    006-005 U1b adds the transport (the module call, the transient derived
    configuration and the envelope); this unit stops at the configuration and
    the packet the transport would consume.
    """
    resolve_runtime_module(runtime)
    load_runtime_section(runtime)
    if not packet:
        raise DispatchError(
            "dispatch requires --packet <id>: the id of a packet already "
            "published by `cdad_packet.py prepare`")
    root = Path(project_root) if project_root else Path.cwd()
    packet_dir = root / PACKETS_RELPATH / packet
    if not (packet_dir / PACKET_MD_NAME).is_file():
        raise DispatchError(
            f"unknown packet {packet!r}: no {PACKET_MD_NAME} under {packet_dir} "
            f"— prepare the packet before dispatching")
    raise DispatchError(
        "the external transport is not available in this build: 006-005 U1a "
        "carries the execution configuration and the migration step; the entry "
        "verbs (dispatch transport, record, capabilities) arrive with U1b")


def _verb_not_available(verb: str) -> DispatchError:
    return DispatchError(
        f"the `{verb}` verb is not available in this build: 006-005 U1a carries "
        f"the execution configuration and the migration step; `{verb}` arrives "
        f"with U1b")


# ---------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdad_dispatch.py",
        description=(
            "The orchestrator's single entry (006-005). The runtime enters "
            "explicitly by --runtime (PD-8) and its execution configuration is "
            "the runtime section of runtimes.json under the CDAD user config "
            "(PD-9); the bounded migrate verb moves a retired exec-config into "
            "it (PD-25)."
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
        if args.verb in U1A_DEFERRED_VERBS:
            raise _verb_not_available(args.verb)
        return dispatch(args.runtime, args.project_root, args.packet)
    except DispatchError as exc:
        print(f"cdad_dispatch: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
