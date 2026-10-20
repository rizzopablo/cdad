#!/usr/bin/env python3
"""Canonical CDAD packet renderer and policy entrypoint."""

from __future__ import annotations

import argparse
import base64
from datetime import date, datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any


class PolicyError(ValueError):
    """A user-supplied execution or state document violates the contract."""


BINDING_FIELDS = (
    "id",
    "epic_id",
    "feature_id",
    "runtime",
    "scope",
    "model_policy",
    "authority_ref",
)
AUTHORIZED_PAIRS = {("opencode", "opencode-mvp"), ("codex", "codex-construction")}
AUTHORIZED_SINGLE_MODEL_EPIC = "epic-003-context-efficiency"
# "Stages eligible for an active packet" ("etapas aptas para paquete activo") —
# documented SUBSET of the canonical epic_stage vocabulary. Single editable
# definition of the vocabulary: skills/cdad-epic/references/state-detection.md:14
# (R13 — 004-001 T2, PD-4). Membership unchanged; sole consumer:
# validate_state (cdad_packet.py:231). Never add a value here that the canonical
# vocabulary does not define; adding a stage goes to state-detection.md first.
VALID_EPIC_STAGES = {"features-loop", "epic-integration", "epic-closure"}
REQUIRED_EXPIRY_EVENTS = {"epic-closed", "epic-cancelled", "user-revoked"}
VALID_PACKET_STATUSES = {"prepared", "dispatched", "completed", "failed"}
VALID_METRIC_OUTCOMES = {"prepared", "dispatched", "completed", "failed"}
VALID_ROLES = {"architect", "test-writer", "implementer", "reviewer", "scribe"}
VALID_SUBSTAGES = {
    "discovery", "brainstorm", "draft", "audit", "post-audit", "red",
    "properties", "e2e", "green", "refactor", "review-fix", "review",
    "plan-review", "memory",
}
VALID_CONTRACT_KINDS = {"approved-epic-plan", "approved-unit-contract",
                        "approved-feature-spec", "draft-plan"}
# 006-006 U1 (R-1..R-8): the reviewed object's FORM is declared in the contract
# (`object_kind`) and, when the review covers a spec AND a plan, the companion
# spec is fixed by digest (`spec_path`/`spec_sha256`/`spec_version`). The
# extension is ADDITIVE: the contract's key set stays closed, and the new keys
# are carried only when the invocation declares them.
OBJECT_FORM_VALUES = ("spec", "plan")
# R-4: absent means `plan` — the fail-closed direction: forgetting the flag
# produces the vigente rejection, never a silent acceptance.
DEFAULT_OBJECT_FORM = "plan"
OBJECT_FORM_CONTRACT_KEYS = ("object_kind", "spec_path", "spec_sha256", "spec_version")
COMPANION_CONTRACT_KEYS = ("spec_path", "spec_sha256", "spec_version")
# 005-013 T1: the architect's contract is EITHER the generated unit projection
# (kind + the file published beside its packet) OR the declared fallback (the
# whole approved epic plan). The two names live here, with the kinds.
UNIT_CONTRACT_KIND = "approved-unit-contract"
EPIC_PLAN_KIND = "approved-epic-plan"
UNIT_PROJECTION_NAME = "UNIT-CONTRACT.md"
ROLE_SUBSTAGES = {
    "architect": {"discovery", "brainstorm", "draft"},
    "test-writer": {"audit", "post-audit", "red", "properties", "e2e"},
    "implementer": {"green", "refactor", "review-fix"},
    "reviewer": {"review", "plan-review"},
    "scribe": {"memory"},
}
# PD-15 (006-005 U3): `temporary` is a first-class write scope of the
# vocabulary (classify_path_observable already names it from
# `temporary_roots`); it authorizes writes inside a root the ACCEPTED policy
# declares, and nothing else (§2.9/INV-16).
SCOPE_CLASSES = {"contract", "docs", "tests", "colocated-tests", "implementation",
                 "repository-read", "temporary"}
EXECUTION_KEYS = set(BINDING_FIELDS) | {"model"}
# Execution context v2 (PD-3/PD-4): logical identity plus a verifiable policy
# snapshot. Runtime, model and session are dispatch observations, never part of
# the identity, so they do not appear here (I3).
V2_SCHEMA_VERSION = 2
V2_EXECUTION_KEYS = {
    "id", "epic_id", "feature_id", "scope", "authority_ref",
    "model_policy", "policy_sha256",
}
V2_BINDING_FIELDS = (
    "id", "epic_id", "feature_id", "scope", "authority_ref",
    "model_policy", "policy_sha256",
)
# PD-5: the v2 context carries a verifiable snapshot of the policy bytes it was
# built from and a history of accepted revisions (initial + reconciled).
V2_DOCUMENT_KEYS = {"schema_version", "execution", "path_policy", "policy", "policy_history"}
V2_POLICY_KEYS = {"path", "schema_version", "sha256", "snapshot"}
V2_POLICY_HISTORY_KEYS = {"sha256", "snapshot"}
DEFAULT_MODEL_POLICY = "ordinary"
EXECUTIONS_DIR = Path(".cdad") / "executions"
FLAT_EXECUTION_RELPATH = Path(".cdad") / "execution.json"
# PD-11/I5: single writer per project, and inert interruption/synchronisation
# hooks. `.cdad/.lock` is a PERMANENT rendezvous file: only the flock and the
# descriptor are released, never the file (F1).
LOCK_RELPATH = Path(".cdad") / ".lock"
TXN_DIRNAME = Path(".cdad") / ".txn"
# I9: project-local OpenCode agents derived from the installed sources + the
# project policy. Published under .opencode/agents/ with a hash manifest.
DERIVED_AGENTS_ENV = "CDAD_OPENCODE_AGENTS_DIR"
DEFAULT_DERIVED_SOURCE = Path.home() / ".config" / "opencode" / "agents"
DERIVED_RELPATH = Path(".opencode") / "agents"
DERIVED_MANIFEST_NAME = ".cdad-derived.json"
DERIVED_STAGE_DIRNAME = "derived"
# 005-005 T3 (PD-12..PD-14/INV-7): the project activation registry names the
# adopted installation the project runs against; the runtime lays the OpenCode
# agents out at `<adopted_root>/.config/opencode/agents` and the installer
# records the origin version/commit in `version.txt` at the installation root.
ACTIVATION_REGISTRY_REL = Path(".cdad") / "activation.json"
OPENCODE_AGENTS_SUBDIR = (".config", "opencode", "agents")
INSTALL_VERSION_MARKER = "version.txt"
DERIVED_MAP_KEYS = ("read", "grep", "glob", "edit")
# U6-7b (006-005, E2/PD-24): the `write` key of the installed copy joins the
# region the derivation replaces — it is RETIRED (removed, never emitted).
# In OpenCode v2.0.27 the write tool evaluates `edit` and `write` together
# (findLast): a `write: ask` inherited from an installation prior to the
# U6-7 fix would override the derived `edit` map — with --auto it approves
# even what `edit` denies, and without interaction it rejects even what
# `edit` allows. The effective write verdict of a derived agent must be
# EXACTLY the verdict of its derived `edit` map.
DERIVED_RETIRED_MAP_KEYS = ("write",)
# The `permission` map keys the derivation owns: the replaced ones (read,
# grep, glob, edit) and the retired one (write). A key is recognized with its
# scalar form (`  edit: deny`) and with its block form (`  edit:` + children).
PERMISSION_MAP_KEY_RE = re.compile(
    r"^  (%s):" % "|".join(DERIVED_MAP_KEYS + DERIVED_RETIRED_MAP_KEYS))
FAIL_AT_ENV = "CDAD_TEST_FAIL_AT"
FAIL_AT_RC = 97
PAUSE_AT_ENV = "CDAD_TEST_PAUSE_AT"
PAUSE_FILE_ENV = "CDAD_TEST_PAUSE_FILE"
PAUSE_TIMEOUT_SECONDS = 30
CLOSED_FEATURE_STATUSES = {"done", "cancelled", "canceled", "closed", "archived"}
ACTIVE_PACKET_STATUSES = {"prepared", "dispatched"}
# 005-003 T1 (PD-1/PD-2/PD-5; INV-1/INV-2/INV-9): the compact operational view
# (`compact-view-v1`) and its explicit entry-selection map. The byte limit is
# the repo's normative one (16 KiB), the same default `--max-bytes` continuity
# uses; the view never emits `stage_history`, so the limit does not grow with
# the state. The three `ENTRY_*` constants are the closed vocabulary of §2.2.
DEFAULT_VIEW_MAX_BYTES = 16_384
ENTRY_CONTINUITY_RECONCILE = "continuity-reconcile"
ENTRY_NEXT_UNIT = "next-unit"
ENTRY_DIAGNOSIS = "diagnosis"
# D5 (005-001 T3): the resting value between features. `current_stage == IDLE_STAGE`
# is valid iff `active_feature` is null; single editable definition of the
# invariant lives in skills/cdad-cycle/references/state-detection.md:27-30.
IDLE_STAGE = "idle"
PATH_POLICY_LISTS = {
    "implementation_roots",
    "test_roots",
    "colocated_test_roots",
    "documentation_roots",
    "colocated_test_suffixes",
    "colocated_test_prefixes",
}
PATH_POLICY_OPTIONAL_LISTS = {"implementation_files", "documentation_files", "test_files"}
# P-1 (004-002, owner decision 2026-10-02): optional owner-declared private
# paths (exact paths or globs) denied in read AND edit for EVERY role, in both
# runtimes. Same rejection rules as the other roots (project-relative, no "..",
# non-empty); absent means no behavior change (compatibility).
PATH_POLICY_PRIVATE = "private_paths"
PATH_POLICY_KNOWN = PATH_POLICY_LISTS | PATH_POLICY_OPTIONAL_LISTS | {PATH_POLICY_PRIVATE}
POLICY_RELPATH = Path("docs") / "cdad-policy.json"
POLICY_KEYS = {"schema_version", "path_policy", "temporary_roots"}
# Observable class per mechanical classification token; single vocabulary
# shared by the classifier and the conflict diagnostics.
CLASS_BY_TOKEN = {
    "tests": "test",
    "colocated-tests": "colocated-test",
    "implementation": "implementation",
    "docs": "documentation",
}
LAYOUT_IMPL_ROOTS = (
    "src", "lib", "app", "agents", "skills", "scripts", "sources", "build", "addons",
)
# D-5 (006-005 U3, C2): the PROPOSED temporary root — a subdirectory, disjoint
# from the subtrees the CLI writes (`inbox/`, `packets/`, `executions/`,
# `runtime/`), never `.cdad/` itself. The owner accepts it; the proposal never
# touches a project's accepted policy (INV-7).
DEFAULT_TEMPORARY_ROOT = ".cdad/tmp"


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PolicyError(f"{label} must be an object")
    return value


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as stream:
            return _object(json.load(stream), label)
    except FileNotFoundError as exc:
        raise PolicyError(f"{label} not found: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot read {label} {path}: {exc}") from exc


def _project_path(project_root: Path, raw: Any, label: str) -> Path:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise PolicyError(f"{label} must be a non-empty project-relative path")
    relative = Path(raw)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise PolicyError(f"{label} is unsafe: {raw!r}")
    candidate = project_root.joinpath(*relative.parts)
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(project_root)
    except ValueError as exc:
        raise PolicyError(f"{label} escapes project root: {raw!r}") from exc
    except (OSError, RuntimeError) as exc:
        raise PolicyError(f"cannot resolve {label} {raw!r}: {exc}") from exc
    return resolved


def _path_is_within(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _validate_private_paths(path_policy: dict[str, Any], project_root: Path) -> None:
    """P-1: private_paths is optional; when present each entry follows the same
    rejection rules as the roots (project-relative, no "..", non-empty)."""
    values = path_policy.get(PATH_POLICY_PRIVATE, [])
    if not isinstance(values, list) or any(
            not isinstance(value, str) or not value for value in values):
        raise PolicyError(
            f"path_policy.{PATH_POLICY_PRIVATE} must be a list of non-empty strings")
    for value in values:
        _project_path(project_root, value, f"path_policy.{PATH_POLICY_PRIVATE}")


def _validate_path_policy(policy: Any, project_root: Path) -> dict[str, Any]:
    policy = _object(policy, "path_policy")
    missing = PATH_POLICY_LISTS - policy.keys()
    unknown = policy.keys() - PATH_POLICY_KNOWN
    if missing:
        raise PolicyError("path_policy missing fields: " + ", ".join(sorted(missing)))
    if unknown:
        raise PolicyError("path_policy has unknown fields: " + ", ".join(sorted(unknown)))
    for field in PATH_POLICY_LISTS | PATH_POLICY_OPTIONAL_LISTS:
        values = policy.get(field, [])
        if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
            raise PolicyError(f"path_policy.{field} must be a list of non-empty strings")
        if field.endswith("_roots") or field.endswith("_files"):
            for value in values:
                _project_path(project_root, value, f"path_policy.{field}")
    _validate_private_paths(policy, project_root)
    return policy


def _colocated_name(name: str, path_policy: dict[str, Any]) -> bool:
    """True when a file name matches the declared co-located test convention."""
    prefixes = path_policy.get("colocated_test_prefixes", [])
    suffixes = path_policy.get("colocated_test_suffixes", [])
    return any(name.startswith(value) for value in prefixes) or any(
        name.endswith(value) for value in suffixes)


def classify_path(raw_path: str, path_policy: dict[str, Any], project_root: Path) -> str | None:
    """Return the single mechanical class for a project path, or None."""
    candidate = _project_path(project_root, raw_path, "path")
    name = candidate.name

    def exact(field: str) -> bool:
        return any(
            candidate == _project_path(project_root, value, f"path_policy.{field}")
            for value in path_policy.get(field, [])
        )

    def beneath(field: str) -> bool:
        return any(
            _path_is_within(candidate, _project_path(project_root, root, f"path_policy.{field}"))
            for root in path_policy.get(field, [])
        )

    is_test_name = _colocated_name(name, path_policy)
    if exact("test_files") or beneath("test_roots"):
        return "tests"
    if beneath("colocated_test_roots") and is_test_name:
        return "colocated-tests"
    if exact("implementation_files") or beneath("implementation_roots"):
        return "implementation"
    if exact("documentation_files") or beneath("documentation_roots"):
        return "docs"
    return None


def _private_path_entries(path_policy: dict[str, Any]) -> list[str]:
    """Normalized private entries (trailing slash trimmed once, R3).

    Single source of truth shared by the classifier (`_is_private_path`) and the
    derived OpenCode maps (`_derived_maps`): normalizing here keeps both barriers
    in parity, so `tests/x/` yields `tests/x` (and its `tests/x/**` subtree)
    instead of the inert `tests/x//**`.
    """
    return [entry.rstrip("/")
            for entry in (path_policy.get(PATH_POLICY_PRIVATE, []) or [])]


def _glob_to_regex(pattern: str) -> str:
    """Glob -> regex: `*` matches anything (including `/`), `?` one character."""
    return "".join(
        ".*" if char == "*" else "." if char == "?" else re.escape(char)
        for char in pattern
    )


def _is_private_path(relative: str, path_policy: dict[str, Any]) -> bool:
    """P-1: True when a project-relative path is covered by a private entry.

    An entry with glob wildcards matches with glob semantics; a plain entry
    covers itself and its whole subtree (a declared private directory).
    """
    for entry in _private_path_entries(path_policy):
        if any(char in entry for char in "*?["):
            if re.fullmatch(_glob_to_regex(entry), relative):
                return True
        elif relative == entry or relative.startswith(entry + "/"):
            return True
    return False


def classify_path_observable(raw_path: str, path_policy: dict[str, Any], project_root: Path,
                             temporary_roots: list[str]) -> str:
    """Present a project path under the observable class vocabulary.

    Precedence: the policy file itself, then declared private paths, then
    temporary roots, then the mechanical product classification (test /
    colocated-test / implementation / documentation); anything else is
    unclassified.
    """
    candidate = _project_path(project_root, raw_path, "path")
    policy_path = _project_path(project_root, POLICY_RELPATH.as_posix(), "policy path")
    if candidate == policy_path:
        return "policy"
    relative = candidate.relative_to(project_root).as_posix()
    if _is_private_path(relative, path_policy):
        return "private"
    for root in temporary_roots:
        if _path_is_within(candidate, _project_path(project_root, root, "temporary_roots")):
            return "temporary"
    token = classify_path(raw_path, path_policy, project_root)
    return CLASS_BY_TOKEN.get(token, "unclassified")


# Validation regions mirror classify_path: an exact-file rule covers one path
# (matched by equality), a root rule covers its whole subtree (ancestry) and a
# co-located test root covers only the names under it that match the declared
# convention. The classifier and both validators share this representation.
_EXACT_FILE_FIELDS = {"implementation_files", "documentation_files", "test_files"}
_IMPLEMENTATION_FIELDS = ("implementation_roots", "implementation_files")
_TEST_FIELDS = ("test_roots", "test_files", "colocated_test_roots")
_DOCUMENTATION_FIELDS = ("documentation_roots", "documentation_files")
Region = tuple[str, Path]


def _policy_regions(path_policy: dict[str, Any], fields: tuple[str, ...],
                    project_root: Path) -> list[Region]:
    regions: list[Region] = []
    for field in fields:
        kind = ("file" if field in _EXACT_FILE_FIELDS
                else "colocated" if field == "colocated_test_roots" else "root")
        regions.extend(
            (kind, _project_path(project_root, value, f"path_policy.{field}"))
            for value in path_policy.get(field, []))
    return regions


def _region_contains(region: Region, candidate: Path, path_policy: dict[str, Any]) -> bool:
    kind, root = region
    if not _path_is_within(candidate, root):
        return False
    return kind != "colocated" or _colocated_name(candidate.name, path_policy)


def _regions_overlap(a: Region, b: Region, path_policy: dict[str, Any]) -> bool:
    if "colocated" in (a[0], b[0]) and not (
            path_policy.get("colocated_test_prefixes")
            or path_policy.get("colocated_test_suffixes")):
        return False
    if a[0] == "file" and b[0] == "file":
        return a[1] == b[1]
    if a[0] == "file":
        return _region_contains(b, a[1], path_policy)
    if b[0] == "file":
        return _region_contains(a, b[1], path_policy)
    return _path_is_within(a[1], b[1]) or _path_is_within(b[1], a[1])


def _relative_display(path: Path, project_root: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _reject_overlap(path_policy: dict[str, Any], project_root: Path,
                    left_fields: tuple[str, ...], left_label: str,
                    right_fields: tuple[str, ...], right_label: str) -> None:
    for left in _policy_regions(path_policy, left_fields, project_root):
        for right in _policy_regions(path_policy, right_fields, project_root):
            if _regions_overlap(left, right, path_policy):
                raise PolicyError(
                    f"{left_label} path {_relative_display(left[1], project_root)!r} conflicts with "
                    f"{right_label} path {_relative_display(right[1], project_root)!r}")


def _validate_policy_class_conflicts(path_policy: dict[str, Any], project_root: Path) -> None:
    _reject_overlap(path_policy, project_root, _DOCUMENTATION_FIELDS, "documentation",
                    _IMPLEMENTATION_FIELDS, "implementation")
    _reject_overlap(path_policy, project_root, _DOCUMENTATION_FIELDS, "documentation",
                    _TEST_FIELDS, "tests")


def _validate_policy_path_policy(path_policy: Any, project_root: Path) -> dict[str, Any]:
    """Validate the policy file's classification rules (partial lists allowed)."""
    path_policy = _object(path_policy, "path_policy")
    if not path_policy:
        raise PolicyError("path_policy must declare at least one rule")
    unknown = path_policy.keys() - PATH_POLICY_KNOWN
    if unknown:
        raise PolicyError("path_policy has unknown fields: " + ", ".join(sorted(unknown)))
    for field, values in path_policy.items():
        if field == PATH_POLICY_PRIVATE:
            continue
        if not isinstance(values, list) or any(
                not isinstance(value, str) or not value for value in values):
            raise PolicyError(f"path_policy.{field} must be a list of non-empty strings")
        if field.endswith("_roots") or field.endswith("_files"):
            for value in values:
                _project_path(project_root, value, f"path_policy.{field}")
    _validate_private_paths(path_policy, project_root)
    _validate_policy_class_conflicts(path_policy, project_root)
    return path_policy


def _validate_temporary_roots(raw: Any, path_policy: dict[str, Any],
                              project_root: Path) -> None:
    if not isinstance(raw, list) or any(
            not isinstance(value, str) or not value for value in raw):
        raise PolicyError("temporary_roots must be a list of non-empty strings")
    product = _policy_regions(
        path_policy,
        _IMPLEMENTATION_FIELDS + _TEST_FIELDS + _DOCUMENTATION_FIELDS,
        project_root)
    for value in raw:
        temporary: Region = ("root", _project_path(project_root, value, "temporary_roots"))
        for region in product:
            if _regions_overlap(temporary, region, path_policy):
                raise PolicyError(
                    f"temporary root {value!r} conflicts with product path "
                    f"{_relative_display(region[1], project_root)!r}")


def _validate_policy_document(document: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """Validate docs/cdad-policy.json: exactly schema_version, path_policy, temporary_roots."""
    unknown = set(document) - POLICY_KEYS
    missing = POLICY_KEYS - set(document)
    if unknown or missing:
        details: list[str] = []
        if unknown:
            details.append("unknown field(s): " + ", ".join(sorted(unknown)))
        if missing:
            details.append("missing field(s): " + ", ".join(sorted(missing)))
        raise PolicyError(
            "policy fields do not match schema: schema_version, path_policy and "
            "temporary_roots are required and no other field is allowed ("
            + "; ".join(details) + ")")
    version = document.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        raise PolicyError("policy schema_version must be the integer 1")
    path_policy = _validate_policy_path_policy(document.get("path_policy"), project_root)
    _validate_temporary_roots(document.get("temporary_roots"), path_policy, project_root)
    return path_policy


def _validate_execution_document(document: dict[str, Any], project_root: Path) -> dict[str, Any]:
    if set(document) != {"schema_version", "execution", "path_policy"}:
        raise PolicyError("execution context fields do not match schema")
    if document.get("schema_version") != 1:
        raise PolicyError("execution schema_version must be 1")
    execution = _object(document.get("execution"), "execution")
    if set(execution) != EXECUTION_KEYS:
        raise PolicyError("execution fields do not match schema")
    missing = [field for field in BINDING_FIELDS if not isinstance(execution.get(field), str) or not execution[field]]
    if missing:
        raise PolicyError("execution missing non-empty fields: " + ", ".join(missing))
    model = _object(execution.get("model"), "execution.model")
    if set(model) != {"configured", "reported"}:
        raise PolicyError("execution.model fields do not match schema")
    for field in ("configured", "reported"):
        if model.get(field) is not None and not isinstance(model.get(field), str):
            raise PolicyError(f"execution.model.{field} must be string or null")
    _project_path(project_root, execution["authority_ref"], "execution.authority_ref")
    _validate_path_policy(document.get("path_policy"), project_root)
    return execution


def _validate_active_packet(packet: Any) -> None:
    if packet is None:
        return
    packet = _object(packet, "active_packet")
    required = {
        "id": str,
        "role": str,
        "substage": str,
        "status": str,
        "packet_version": int,
        "contract_kind": str,
        "contract_sha256": str,
    }
    missing = [key for key, kind in required.items() if not isinstance(packet.get(key), kind)]
    if missing:
        raise PolicyError("active_packet missing or invalid fields: " + ", ".join(missing))
    if set(packet) != set(required):
        raise PolicyError("active_packet fields do not match schema")
    if not packet["id"]:
        raise PolicyError("active_packet.id must be non-empty")
    if packet["role"] not in ROLE_SUBSTAGES or packet["substage"] not in ROLE_SUBSTAGES[packet["role"]]:
        raise PolicyError("active_packet role/substage is invalid")
    if packet["status"] not in VALID_PACKET_STATUSES:
        raise PolicyError("active_packet.status is invalid")
    if packet["packet_version"] != 1 or isinstance(packet["packet_version"], bool):
        raise PolicyError("active_packet.packet_version must be 1")
    if packet["contract_kind"] not in VALID_CONTRACT_KINDS:
        raise PolicyError("active_packet.contract_kind is invalid")
    if re.fullmatch(r"[0-9a-f]{64}", packet["contract_sha256"]) is None:
        raise PolicyError("active_packet.contract_sha256 must be 64 lowercase hex characters")


def _validate_idle_coherence(state: dict[str, Any]) -> bool:
    """PD-13/PD-14/PD-15 (005-001 T3): resting-state coherence invariant.

    `active_feature is None` ⟺ `current_stage == IDLE_STAGE` (the source of
    truth is skills/cdad-cycle/references/state-detection.md:27-30). Returns
    True when the state is a legitimate idle rest — tolerant of an `execution`
    remnant from the last feature and/or a terminal `active_packet`. Raises a
    `state incoherent` diagnostic (PD-12) that names the concrete contradicted
    record and the legitimate next action, without effects.
    """
    active_feature = state.get("active_feature")
    current_stage = state.get("current_stage")
    if active_feature is None and current_stage != IDLE_STAGE:
        raise PolicyError(
            f"state incoherent: active_feature is null but current_stage is "
            f"{current_stage!r} (not {IDLE_STAGE!r}); repair docs/.cdad-state.json "
            f"by setting current_stage to {IDLE_STAGE!r} or naming the active feature"
        )
    if active_feature is not None and current_stage == IDLE_STAGE:
        raise PolicyError(
            f"state incoherent: current_stage is {IDLE_STAGE!r} but active_feature is "
            f"{active_feature!r}; repair docs/.cdad-state.json by setting active_feature "
            f"to null or naming the feature's real stage"
        )
    if active_feature is None:
        packet = state.get("active_packet")
        status = packet.get("status") if isinstance(packet, dict) else None
        if status in ACTIVE_PACKET_STATUSES:
            raise PolicyError(
                f"state incoherent: the state is resting (active_feature null, "
                f"current_stage {IDLE_STAGE!r}) but active_packet "
                f"{packet.get('id')!r} is still {status!r}; repair docs/.cdad-state.json "
                f"by completing or discarding the in-flight packet before resting"
            )
        return True
    return False


def validate_state(execution_document: dict[str, Any], state: dict[str, Any], project_root: Path) -> str:
    if execution_document.get("schema_version") == V2_SCHEMA_VERSION:
        return _validate_v2_state(execution_document, state, project_root)
    execution = _validate_execution_document(execution_document, project_root)
    if state.get("version") != 1:
        raise PolicyError("state version must be 1")
    state_execution = _object(state.get("execution"), "state.execution")
    if set(state_execution) != set(BINDING_FIELDS):
        raise PolicyError("state.execution fields do not match schema")
    for field in BINDING_FIELDS:
        if state_execution.get(field) != execution[field]:
            raise PolicyError(f"execution binding mismatch: {field}")

    if execution["model_policy"] != "epic-003-single-model":
        _validate_active_packet(state.get("active_packet"))
        return "ordinary"

    if execution["epic_id"] != AUTHORIZED_SINGLE_MODEL_EPIC:
        raise PolicyError("epic-003-single-model is restricted to epic-003-context-efficiency")
    if (execution["runtime"], execution["scope"]) not in AUTHORIZED_PAIRS:
        raise PolicyError("runtime/scope pair is not authorized for epic-003-single-model")
    if state.get("active_epic") != execution["epic_id"]:
        raise PolicyError("active_epic does not match execution")
    if state.get("active_feature") != execution["feature_id"]:
        raise PolicyError("active_feature does not match execution")
    if state.get("epic_stage") not in VALID_EPIC_STAGES:
        raise PolicyError("epic stage is closed, cancelled, or inactive")

    features = state.get("epic_features")
    if not isinstance(features, list):
        raise PolicyError("epic_features must be a list")
    matching = [item for item in features if isinstance(item, dict) and item.get("id") == execution["feature_id"]]
    if len(matching) != 1:
        raise PolicyError("execution feature must occur exactly once in epic_features")
    if matching[0].get("status") in {"done", "cancelled"}:
        raise PolicyError("execution feature is done or cancelled")

    delegation = _object(state.get("hitl_delegation"), "hitl_delegation")
    if delegation.get("status") != "active":
        raise PolicyError("HITL delegation is not active")
    if delegation.get("epic_id") != execution["epic_id"]:
        raise PolicyError("HITL delegation epic mismatch")
    if delegation.get("source") != execution["authority_ref"]:
        raise PolicyError("HITL delegation authority mismatch")
    expires_on = delegation.get("expires_on")
    if not isinstance(expires_on, list) or set(expires_on) != REQUIRED_EXPIRY_EVENTS or len(expires_on) != 3:
        raise PolicyError("HITL delegation expiry events are incomplete or invalid")
    authority = _project_path(project_root, execution["authority_ref"], "execution.authority_ref")
    if not authority.is_file():
        raise PolicyError(f"authority reference not found: {execution['authority_ref']}")

    _validate_active_packet(state.get("active_packet"))
    return "scoped-exception"


def _validate_policy_snapshot(value: Any, label: str) -> str:
    """PD-5: a verifiable policy snapshot is base64 whose bytes re-decode."""
    if not isinstance(value, str) or not value:
        raise PolicyError(f"{label} must be a non-empty base64 string")
    try:
        base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as exc:
        raise PolicyError(f"{label} is not valid base64") from exc
    return value


def _validate_v2_execution_document(document: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """Validate a v2 execution context: logical identity + policy snapshot + history."""
    if set(document) != V2_DOCUMENT_KEYS:
        raise PolicyError("execution context fields do not match the v2 schema")
    if document.get("schema_version") != V2_SCHEMA_VERSION:
        raise PolicyError(f"execution schema_version must be {V2_SCHEMA_VERSION}")
    execution = _object(document.get("execution"), "execution")
    if set(execution) != V2_EXECUTION_KEYS:
        raise PolicyError("execution fields do not match the v2 schema")
    for field in ("id", "feature_id", "scope", "authority_ref", "model_policy", "policy_sha256"):
        if not isinstance(execution.get(field), str) or not execution[field]:
            raise PolicyError(f"execution missing non-empty field: {field}")
    epic_id = execution.get("epic_id")
    if epic_id is not None and (not isinstance(epic_id, str) or not epic_id):
        raise PolicyError("execution.epic_id must be a non-empty string or null")
    if re.fullmatch(r"[0-9a-f]{64}", execution["policy_sha256"]) is None:
        raise PolicyError("execution.policy_sha256 must be 64 lowercase hex characters")
    _validate_policy_path_policy(document.get("path_policy"), project_root)
    policy = _object(document.get("policy"), "policy")
    if set(policy) != V2_POLICY_KEYS:
        raise PolicyError("policy snapshot fields do not match schema")
    if policy.get("schema_version") != 1:
        raise PolicyError("policy snapshot schema_version must be 1")
    if policy.get("sha256") != execution["policy_sha256"]:
        raise PolicyError("policy snapshot hash does not match the execution policy_sha256")
    _project_path(project_root, policy.get("path"), "policy.path")
    _validate_policy_snapshot(policy.get("snapshot"), "policy.snapshot")
    history = document.get("policy_history")
    if not isinstance(history, list) or not history:
        raise PolicyError("policy_history must be a non-empty list of accepted revisions")
    accepted: set[str] = set()
    for index, entry in enumerate(history):
        entry = _object(entry, f"policy_history[{index}]")
        if set(entry) != V2_POLICY_HISTORY_KEYS:
            raise PolicyError(f"policy_history[{index}] fields do not match schema")
        if re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256"))) is None:
            raise PolicyError(f"policy_history[{index}].sha256 must be 64 lowercase hex characters")
        _validate_policy_snapshot(entry.get("snapshot"), f"policy_history[{index}].snapshot")
        accepted.add(entry["sha256"])
    if execution["policy_sha256"] not in accepted:
        raise PolicyError("the execution policy_sha256 is absent from policy_history")
    return execution


def _validate_v2_state(execution_document: dict[str, Any], state: dict[str, Any],
                       project_root: Path) -> str:
    execution = _validate_v2_execution_document(execution_document, project_root)
    if state.get("version") != 1:
        raise PolicyError("state version must be 1")
    binding = _object(state.get("execution"), "state.execution")
    if set(binding) != set(V2_BINDING_FIELDS):
        raise PolicyError("state.execution fields do not match the v2 binding schema")
    for field in V2_BINDING_FIELDS:
        if binding.get(field) != execution[field]:
            raise PolicyError(f"execution binding mismatch: {field}")
    _validate_active_packet(state.get("active_packet"))
    # F1 + B1: one current-vigency validation for every consumer, plus the
    # authority-derived binding check (authority_ref is the verified source).
    source = _validate_v2_vigency(state, project_root, execution["feature_id"],
                                  execution["epic_id"])
    if source is not None and execution["authority_ref"] != source:
        raise PolicyError(
            f"execution authority_ref {execution['authority_ref']!r} does not match the "
            f"current delegation source {source!r}"
        )
    return execution["model_policy"]


def _absolute_existing_directory(raw: str, label: str) -> Path:
    path = Path(raw).resolve()
    if not path.is_dir():
        raise PolicyError(f"{label} must be an existing directory: {raw}")
    return path


def _read_bytes(path: Path, label: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PolicyError(f"cannot read {label} {path}: {exc}") from exc


def _accepted_temporary_roots(execution_document: dict[str, Any],
                              project_root: Path) -> list[str]:
    """Temporary roots of the ACCEPTED policy (§2.9/PD-24, D-5).

    The source is the policy revision the execution context already pins and
    whose digest governs the derived-agent manifest: in a v2 context the
    verified `policy.snapshot` (checked against `policy_sha256`), in a flat v1
    context — which carries no snapshot — the project policy file. Both go
    through `_validate_policy_document`, so PD-18 (a temporary root overlapping
    product) keeps rejecting the policy itself.
    """
    if execution_document.get("schema_version") != V2_SCHEMA_VERSION:
        if not _policy_present(project_root):
            return []
        document = _load_json(_policy_location(project_root), "project policy")
        _validate_policy_document(document, project_root)
        return list(document["temporary_roots"])
    policy = _object(execution_document.get("policy"), "policy")
    try:
        raw = base64.b64decode(policy.get("snapshot"), validate=True)
    except (TypeError, ValueError) as exc:
        raise PolicyError(f"policy snapshot is not valid base64: {exc}") from exc
    if hashlib.sha256(raw).hexdigest() != policy.get("sha256"):
        raise PolicyError(
            "policy snapshot does not match its recorded sha256: the accepted "
            "temporary roots cannot be read from this context")
    try:
        document = _object(json.loads(raw.decode("utf-8")), "project policy")
    except (UnicodeError, ValueError) as exc:
        raise PolicyError(f"cannot parse the accepted policy snapshot: {exc}") from exc
    _validate_policy_document(document, project_root)
    return list(document["temporary_roots"])


def _validate_scope(scope: Any, *, role: str, write: bool, contract_dir: str,
                    policy: dict[str, Any], project_root: Path,
                    temporary_roots: list[str] | None = None) -> dict[str, Any]:
    scope = _object(scope, "scope")
    scope_class = scope.get("class")
    if scope_class not in SCOPE_CLASSES:
        raise PolicyError("scope class is invalid")
    if scope_class == "repository-read":
        if set(scope) != {"class"} or write:
            raise PolicyError("repository-read is read-only and has no selector")
        selector = None
    else:
        if set(scope) not in ({"class", "root"}, {"class", "path"}):
            raise PolicyError("scope must have exactly one root or path selector")
        key = "root" if "root" in scope else "path"
        selector = scope[key]
        candidate = _project_path(project_root, selector, f"scope.{key}")
        if key == "root" and candidate.exists() and not candidate.is_dir():
            raise PolicyError("scope root must designate a directory")
        if key == "path" and candidate.exists() and not candidate.is_file():
            raise PolicyError("scope path must designate a file")
        if key == "root" and selector == ".":
            raise PolicyError("scope root cannot cover the project")
        classified = classify_path(selector, policy, project_root)
        if scope_class == "contract":
            contract_root = _project_path(project_root, contract_dir, "contract directory")
            if not _path_is_within(candidate, contract_root):
                raise PolicyError("contract scope is outside the contract directory")
        elif scope_class == "temporary":
            # PD-15 (§2.9/INV-16): a temporary selector is accepted only inside
            # a root the ACCEPTED policy declares; the empty list authorizes
            # nothing, and the diagnostic names the file and the field.
            declared = [_project_path(project_root, root, "temporary_roots")
                        for root in (temporary_roots or [])]
            if not any(_path_is_within(candidate, root) for root in declared):
                raise PolicyError(
                    f"temporary scope selector {selector!r} is not inside any "
                    f"temporary_roots declared by {POLICY_RELPATH.as_posix()}: "
                    f"declared temporary_roots={list(temporary_roots or [])!r} "
                    f"(the owner declares that list; PD-15)")
        elif scope_class != classified:
            raise PolicyError(f"scope selector is not classified as {scope_class}")
        if key == "path":
            field = {"implementation": "implementation_files", "docs": "documentation_files", "tests": "test_files"}.get(scope_class)
            if field and selector not in policy.get(field, []):
                raise PolicyError(f"exact {scope_class} path is not declared by path_policy")

    if role == "test-writer":
        allowed = ({"contract", "docs", "tests", "colocated-tests"} if not write
                   else {"tests", "colocated-tests", "temporary"})
    elif role == "implementer":
        allowed = SCOPE_CLASSES if not write else {"implementation", "docs"}
    else:
        allowed = SCOPE_CLASSES if not write else set()
    if scope_class not in allowed:
        raise PolicyError(f"{role} cannot use {scope_class} in {'write' if write else 'read'} scope")
    return scope


def _scope_contains(scope: dict[str, Any], raw_path: str, contract_dir: str,
                    policy: dict[str, Any], project_root: Path) -> bool:
    if scope["class"] == "repository-read":
        return True
    selector = scope.get("path", scope.get("root"))
    candidate = _project_path(project_root, raw_path, "input.path")
    scope_path = _project_path(project_root, selector, "scope selector")
    if "path" in scope:
        return candidate == scope_path
    if not _path_is_within(candidate, scope_path):
        return False
    if scope["class"] == "temporary":
        # PD-17/INV-16: the temporary contains only what is NOT product — a
        # temporary root is disjoint from the product regions by policy
        # (PD-18), and a path the classifier calls product or private is never
        # contained by it.
        return (classify_path(raw_path, policy, project_root) is None
                and not _is_private_path(
                    candidate.relative_to(project_root).as_posix(), policy))
    contract_root = _project_path(project_root, contract_dir, "contract directory")
    actual = "contract" if _path_is_within(candidate, contract_root) else classify_path(raw_path, policy, project_root)
    return actual == scope["class"] or (scope["class"] == "docs" and actual == "docs")


def validate_request(document: dict[str, Any], execution_document: dict[str, Any],
                     state: dict[str, Any], project_root: Path,
                     contract_bytes_override: bytes | None = None) -> dict[str, Any]:
    """Validate a packet request against its contract, role and execution.

    `contract_bytes_override` (005-013 T1, VERIFY V6) is the ONLY additive input:
    the caller that publishes the contract inside its own transaction (`prepare`
    with a generated unit projection) passes the exact bytes it is about to
    publish, so the digest is verified against the transaction's bytes instead of
    reading a not-yet-published file. Every check — the exact digest, the
    kind/path pair and the active-packet binding — is unchanged; when no override
    is given the bytes are read from `contract.path`, as before.
    """
    validate_state(execution_document, state, project_root)
    required = {"schema_version", "packet_id", "execution_id", "feature_id", "role", "substage",
                "objective", "contract", "inputs", "read_scope", "write_scope", "invariants",
                "expected_output", "evidence_required"}
    # PD-10/INV-4 (005-003 T6): the closed field set is EXTENDED with one declared
    # optional property (`plan_task`, the explicit task selector). It is never
    # relaxed: any other unknown key still fails the set equality below.
    # PD-7/INV-4 (006-005 U1c): a second declared optional property is added the
    # same way (`agent`, the role+stack agent that travels in the package); the
    # closure is not relaxed — the set equality below still rejects every other
    # unknown key.
    optional = {"plan_task", "agent"}
    if (not required <= set(document) <= (required | optional)
            or document.get("schema_version") != 1):
        raise PolicyError("request fields do not match schema")
    if "plan_task" in document and (
            not isinstance(document["plan_task"], str) or not document["plan_task"]):
        raise PolicyError("request.plan_task must be a non-empty string")
    if "agent" in document and (
            not isinstance(document["agent"], str) or not document["agent"]):
        raise PolicyError("request.agent must be a non-empty string")
    for key in ("packet_id", "execution_id", "feature_id", "role", "substage", "objective", "expected_output"):
        if not isinstance(document.get(key), str) or not document[key]:
            raise PolicyError(f"request.{key} must be a non-empty string")
    execution = execution_document["execution"]
    if document["execution_id"] != execution["id"] or document["feature_id"] != execution["feature_id"]:
        raise PolicyError("request identity does not match execution")
    role, substage = document["role"], document["substage"]
    if role not in ROLE_SUBSTAGES or substage not in ROLE_SUBSTAGES[role]:
        raise PolicyError("request role/substage pair is invalid")
    contract = _object(document.get("contract"), "request.contract")
    contract_keys = {"kind", "path", "sha256", "commit"}
    plan_version = contract.get("plan_version")
    if "plan_version" in contract:
        contract_keys = contract_keys | {"plan_version"}
    # 006-006 U1 (R-1): the declared object form and the companion identity are
    # an ADDITIVE extension of the closed key set — the four new keys are
    # admitted, and any other unknown key is still rejected.
    for optional_key in OBJECT_FORM_CONTRACT_KEYS:
        if optional_key in contract:
            contract_keys = contract_keys | {optional_key}
    if set(contract) != contract_keys:
        raise PolicyError("request.contract fields do not match schema")
    # PD-1 (004-003 T1): a draft-plan contract is a first-class, non-approved
    # object. It declares its own plan version and path; it must never be
    # confused with (nor masquerade as) an approved contract. An approval kind
    # that also declares a plan version is a forged draft over `approved-*`
    # (or vice versa) and is rejected before anything is written.
    is_draft = contract.get("kind") == "draft-plan"
    if is_draft:
        if not isinstance(plan_version, str) or not plan_version:
            raise PolicyError("draft-plan contract requires a non-empty plan_version")
    else:
        # 006-006 U1 (R-2): the declared form and the companion belong to the
        # draft surface. An `approved-*` kind that declares any of them is a
        # forgery and is rejected before anything is published.
        for forged_key in OBJECT_FORM_CONTRACT_KEYS:
            if forged_key in contract:
                raise PolicyError(
                    f"an approved contract kind must not declare {forged_key}: the "
                    "declared object form and its companion belong to a draft plan (PD-1)")
        if plan_version is not None:
            raise PolicyError(
                "an approved contract kind must not declare plan_version: a draft plan "
                "carries its own version and cannot reuse an approved-* kind (PD-1)"
            )
    if not isinstance(contract.get("kind"), str) or contract["kind"] not in VALID_CONTRACT_KINDS:
        raise PolicyError("request.contract kind is invalid")
    # B1/B2 (004-003 T2 review-fix, PD-2 + acceptance criterion 1): the draft
    # plan and its review subphase are a BIDIRECTIONAL pair, enforced in one
    # place for the reviewer role. A `draft-plan` object is admissible only
    # with the `plan-review` procedure, and `plan-review` only over a
    # `draft-plan` object — otherwise a draft would be diff-reviewed against
    # an approved contract, or an approved spec would be run through a
    # draft-only procedure, and a packet would be produced for an unsupported
    # contract. Both escapes are rejected before anything is written.
    if role == "reviewer":
        if is_draft and substage != "plan-review":
            raise PolicyError(
                "draft-plan contract requires the plan-review subphase: "
                f"reviewer/{substage} would diff-review a draft against an approved contract (PD-2)"
            )
        if not is_draft and substage == "plan-review":
            raise PolicyError(
                "plan-review subphase requires a draft-plan contract: "
                "an approved contract is not the object this procedure reviews (PD-2)"
            )
    if not is_draft:
        # PD-5 (005-013 T1): the architect's contract is EITHER the generated
        # unit projection published with its own packet (kind
        # `approved-unit-contract`, path bound to THIS packet's id) OR the
        # declared fallback (kind `approved-epic-plan`, the whole epic plan).
        # Exactly those two pairs are accepted; any other pair fails closed with
        # the existing diagnostic. Every other role keeps its single pair.
        if role == "architect":
            epic_id = execution.get("epic_id")
            accepted_pairs = (
                (EPIC_PLAN_KIND, f"docs/epics/{epic_id}/plan.md"),
                (UNIT_CONTRACT_KIND,
                 f".cdad/packets/{document['packet_id']}/{UNIT_PROJECTION_NAME}"),
            )
            if (contract["kind"], contract.get("path")) not in accepted_pairs:
                raise PolicyError("contract kind/path does not match role and execution")
        else:
            expected_kind = "approved-feature-spec"
            expected_path = f"docs/specs/{execution['feature_id']}/spec.md"
            if contract["kind"] != expected_kind or contract.get("path") != expected_path:
                raise PolicyError("contract kind/path does not match role and execution")
    else:
        _project_path(project_root, contract.get("path"), "contract.path")
    if contract.get("commit") is not None and not isinstance(contract["commit"], str):
        raise PolicyError("contract.commit must be string or null")
    contract_path = _project_path(project_root, contract["path"], "contract.path")
    contract_content = (contract_bytes_override if contract_bytes_override is not None
                        else _read_bytes(contract_path, "contract"))
    digest = hashlib.sha256(contract_content).hexdigest()
    if contract.get("sha256") != digest:
        raise PolicyError("contract sha256 does not match exact content")
    # 006-006 U1 (R-3..R-8): the declared form of the reviewed object and the
    # companion identity. The companion's digest is verified against the file's
    # bytes exactly like the principal's (R-5): an asserted digest that does not
    # match the bytes is rejected, naming the divergence.
    object_form = _declared_object_form(contract.get("object_kind"), "contract.object_kind")
    if any(key in contract for key in COMPANION_CONTRACT_KEYS):
        missing_companion = [key for key in COMPANION_CONTRACT_KEYS if key not in contract]
        if missing_companion:
            raise PolicyError(
                "the companion spec identity is all-or-none: missing "
                + ", ".join(missing_companion) + " (R-6)")
        if object_form != "plan":
            raise PolicyError(
                "the companion document is the spec and only exists over a plan-form "
                "principal: contract.object_kind must be 'plan' (R-7, R-8)")
        companion_path = _project_path(project_root, contract["spec_path"], "contract.spec_path")
        if not companion_path.is_file():
            raise PolicyError(
                f"the companion spec document does not exist: {contract['spec_path']}")
        companion_digest = hashlib.sha256(
            _read_bytes(companion_path, "contract.spec_path")).hexdigest()
        if contract["spec_sha256"] != companion_digest:
            raise PolicyError(
                "contract.spec_sha256 does not match the companion document's exact "
                f"content: asserted {contract['spec_sha256']!r}, bytes digest "
                f"{companion_digest!r}")
    # 005-001 T1 (D6): the role-specific contract approval is enforced here,
    # where both the role and the verified contract bytes are known. This is the
    # single enforcement point for `prepare`, `validate-request`, `render`,
    # `validate-packet` and `--resume-packet` (all go through `validate_request`).
    _contract_approval_for(role, contract, state, execution, project_root)
    contract_dir = str(Path(contract["path"]).parent.as_posix())
    policy = execution_document["path_policy"]
    # PD-15/PD-24 (§2.9): a `temporary` scope is accepted only inside the roots
    # the ACCEPTED policy declares; both the packet validation and the derived
    # agent map read the same source.
    temporary_roots = _accepted_temporary_roots(execution_document, project_root)
    for field in ("inputs", "read_scope", "write_scope", "invariants", "evidence_required"):
        if not isinstance(document.get(field), list):
            raise PolicyError(f"request.{field} must be a list")
    read_scopes = [_validate_scope(x, role=role, write=False, contract_dir=contract_dir,
                                   policy=policy, project_root=project_root,
                                   temporary_roots=temporary_roots)
                   for x in document["read_scope"]]
    [_validate_scope(x, role=role, write=True, contract_dir=contract_dir,
                     policy=policy, project_root=project_root,
                     temporary_roots=temporary_roots)
     for x in document["write_scope"]]
    for item in document["inputs"]:
        item = _object(item, "request input")
        if set(item) != {"path", "purpose"} or not isinstance(item.get("purpose"), str) or not item["purpose"]:
            raise PolicyError("request input fields are invalid")
        _project_path(project_root, item.get("path"), "input.path")
        if not any(_scope_contains(scope, item["path"], contract_dir, policy, project_root) for scope in read_scopes):
            raise PolicyError(f"input is outside read scope: {item['path']}")
    if any(not isinstance(x, str) or not x for x in document["invariants"] + document["evidence_required"]):
        raise PolicyError("request invariants and evidence must be non-empty strings")
    active = state.get("active_packet")
    if active is None:
        raise PolicyError("rendering requires an active_packet")
    bindings = {"id": "packet_id", "role": "role", "substage": "substage"}
    for state_key, request_key in bindings.items():
        if active[state_key] != document[request_key]:
            raise PolicyError(f"active_packet mismatch: {state_key}")
    if active["packet_version"] != 1 or active["contract_kind"] != contract["kind"] or active["contract_sha256"] != digest:
        raise PolicyError("active_packet contract/version does not match request")
    return document


def _asset_root() -> Path:
    return Path(__file__).resolve().parents[1]


def render_packet(request: dict[str, Any], execution_document: dict[str, Any],
                  project_root: Path | None = None) -> str:
    asset = _asset_root() / "packets"
    source_paths = [Path("common.md"), Path("roles") / f"{request['role']}.md",
                    Path("substages") / f"{request['role']}-{request['substage']}.md"]
    source_bytes = [_read_bytes(asset / path, "packet instruction") for path in source_paths]
    static_bytes = b"\n".join(source_bytes)
    try:
        static = static_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PolicyError(f"packet instruction is not UTF-8: {exc}") from exc
    # PD-19 (004-001): the static-instruction byte ceiling is a declared policy
    # parameter — read from the environment AT CHECK TIME, default 12000.
    raw_limit = os.environ.get("CDAD_STATIC_BLOCK_LIMIT")
    if raw_limit is None:
        limit = 12_000
    else:
        try:
            limit = int(raw_limit.strip())
        except ValueError as exc:
            raise PolicyError(
                f"CDAD_STATIC_BLOCK_LIMIT is not an integer byte ceiling: {raw_limit!r}"
            ) from exc
        if limit < 1:
            raise PolicyError(f"CDAD_STATIC_BLOCK_LIMIT must be a positive byte ceiling, got {limit}")
    if len(static_bytes) > limit:
        raise PolicyError(
            f"static instruction block exceeds the byte limit: {len(static_bytes)} > {limit} "
            f"UTF-8 bytes (CDAD_STATIC_BLOCK_LIMIT={raw_limit if raw_limit is not None else 'unset, default 12000'})"
        )
    metadata = {key: request[key] for key in ("packet_id", "execution_id", "feature_id", "role", "substage", "contract", "read_scope", "write_scope")}
    metadata.update({
        "packet_version": 1,
        "execution": execution_document["execution"],
        "path_policy": execution_document["path_policy"],
        # PD-5/F6: the packet carries the exact policy snapshot (and its digest)
        # of the revision the execution was built from, so the package alone
        # proves which policy bytes it was generated under.
        "policy": execution_document.get("policy"),
        "instruction_sources": [
            {"path": path.as_posix(), "sha256": hashlib.sha256(content).hexdigest()}
            for path, content in zip(source_paths, source_bytes)
        ],
    })
    canonical = json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    contract_lines = [f"- kind: {request['contract']['kind']}",
                      f"- path: {request['contract']['path']}",
                      f"- sha256: {request['contract']['sha256']}",
                      f"- commit: {json.dumps(request['contract']['commit'])}"]
    # 006-006 U1 (R-9): the declared form and the companion identity are
    # ADDITIVE — they are emitted only when the contract declares them, so a
    # package without the new keys keeps the exact bytes of this revision.
    if request["contract"].get("object_kind"):
        contract_lines.append(f"- form: {request['contract']['object_kind']}")
    if request["contract"].get("spec_path"):
        contract_lines.append(f"- spec_path: {request['contract']['spec_path']}")
        contract_lines.append(f"- spec_sha256: {request['contract']['spec_sha256']}")
        contract_lines.append(f"- spec_version: {request['contract']['spec_version']}")
    lines = ["---cdad-packet-json", canonical, "---end-cdad-packet-json", "# CDAD task",
             "", "<!-- cdad-instructions:start -->", static, "<!-- cdad-instructions:end -->",
             "", "## Objective", request["objective"], "", "## Contract", *contract_lines]
    # PD-10/INV-4: with a declared plan task the packet emits its two declared
    # sections; without it the render is byte-identical (the additive surface).
    lines.extend(_plan_task_sections(request, project_root))
    lines.extend(["", "## Inputs"])
    lines.extend(f"- {x['path']}: {x['purpose']}" for x in request["inputs"])
    lines.extend(["", "## Read scope", json.dumps(request["read_scope"], ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                  "", "## Write scope", json.dumps(request["write_scope"], ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                  "", "## Invariants"])
    lines.extend(f"- {x}" for x in request["invariants"])
    lines.extend(["", "## Expected output", request["expected_output"], "", "## Evidence required"])
    lines.extend(f"- {x}" for x in request["evidence_required"])
    return "\n".join(lines) + "\n"


def validate_metric(metric: dict[str, Any], state: dict[str, Any]) -> None:
    required = {"schema_version", "execution_id", "packet_id", "epic_id", "feature_id", "role", "substage",
                "runtime", "model", "started_at", "ended_at", "input_tokens", "output_tokens", "context_limit",
                "retry_count", "outcome"}
    if set(metric) != required or metric.get("schema_version") != 1:
        raise PolicyError("metric fields do not match schema")
    execution = _object(state.get("execution"), "state.execution")
    comparisons = {"execution_id": "id", "epic_id": "epic_id", "feature_id": "feature_id", "runtime": "runtime"}
    for metric_key, execution_key in comparisons.items():
        if metric.get(metric_key) != execution.get(execution_key):
            raise PolicyError(f"metric identity mismatch: {metric_key}")
    role, substage = metric.get("role"), metric.get("substage")
    if role not in ROLE_SUBSTAGES or substage not in ROLE_SUBSTAGES[role]:
        raise PolicyError("metric role/substage pair is invalid")
    active = state.get("active_packet")
    if active is None:
        raise PolicyError("metric requires an active_packet identity")
    _validate_active_packet(active)
    for metric_key, packet_key in (("packet_id", "id"), ("role", "role"), ("substage", "substage")):
        if metric.get(metric_key) != active.get(packet_key):
            raise PolicyError(f"metric identity mismatch: {metric_key}")
    model = _object(metric.get("model"), "metric.model")
    if set(model) != {"configured", "reported"} or any(v is not None and not isinstance(v, str) for v in model.values()):
        raise PolicyError("metric.model fields are invalid")
    for field in ("input_tokens", "output_tokens", "context_limit", "retry_count"):
        value = metric.get(field)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
            raise PolicyError(f"metric.{field} must be a non-negative integer or null")
    started_at = _parse_rfc3339(metric.get("started_at"), "metric.started_at")
    ended_value = metric.get("ended_at")
    ended_at = None if ended_value is None else _parse_rfc3339(ended_value, "metric.ended_at")
    if ended_at is not None and ended_at < started_at:
        raise PolicyError("metric.ended_at must not precede metric.started_at")
    if metric.get("outcome") not in VALID_METRIC_OUTCOMES:
        raise PolicyError("metric.outcome is invalid")


RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$"
)


def _parse_rfc3339(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or RFC3339_PATTERN.fullmatch(value) is None:
        raise PolicyError(f"{label} must be an RFC3339 timestamp with an explicit offset")
    normalized = value.upper().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise PolicyError(f"{label} must be a valid RFC3339 timestamp") from exc
    if parsed.utcoffset() is None:
        raise PolicyError(f"{label} must include an explicit offset")
    return parsed


DEFAULT_INVARIANTS = {
    "test-writer": ["Do not read implementation code", "Each test maps to a postcondition"],
    "implementer": ["Do not edit tests"],
}
DEFAULT_EXPECTED_OUTPUT = "Role report with the required evidence"
DEFAULT_EVIDENCE = ["modified files", "exact commands", "command output", "commit"]
FLAT_NAME = re.compile(r"[A-Za-z0-9._-]+")


def _contract_for(role: str, execution: dict[str, Any]) -> tuple[str, str]:
    if role == "architect":
        epic_id = execution.get("epic_id")
        if not isinstance(epic_id, str) or not epic_id:
            # OPT-4 (PD-12): the standalone architecture intake follows the
            # legacy path; without an active epic there is no plan contract.
            # Diagnose it explicitly instead of fabricating docs/epics/None/.
            raise PolicyError(
                "architect requires an active epic: the execution has no active_epic "
                "bound, so there is no docs/epics/<epic>/plan.md contract; the "
                "standalone architecture intake follows the legacy path (PD-12)"
            )
        return EPIC_PLAN_KIND, f"docs/epics/{epic_id}/plan.md"
    return "approved-feature-spec", f"docs/specs/{execution['feature_id']}/spec.md"


def _declared_object_form(form: Any, label: str) -> str:
    """006-006 U1 (R-3/R-4): the declared form of the reviewed object.

    `spec` | `plan`; absent means `plan` (the fail-closed direction: forgetting
    the flag produces the vigente rejection, never a silent acceptance). A value
    outside the closed set is rejected, naming the value and the admitted forms.
    """
    if form is None:
        return DEFAULT_OBJECT_FORM
    if form not in OBJECT_FORM_VALUES:
        raise PolicyError(
            f"{label} is invalid: {form!r} (the admitted forms are: "
            f"{', '.join(OBJECT_FORM_VALUES)})")
    return form


def _cli_scope(raw: str, project_root: Path) -> dict[str, Any]:
    scope_class, separator, selector = raw.partition("=")
    if not separator:
        if scope_class != "repository-read":
            raise PolicyError(f"scope must be CLASS=SELECTOR: {raw!r}")
        return {"class": scope_class}
    candidate = _project_path(project_root, selector, "scope selector")
    return {"class": scope_class, "path" if candidate.is_file() else "root": selector}


def _cli_input(raw: str) -> dict[str, str]:
    path, separator, purpose = raw.partition("=")
    if not separator or not path or not purpose:
        raise PolicyError(f"input must be PATH=PURPOSE: {raw!r}")
    return {"path": path, "purpose": purpose}


def _default_scopes(role: str, contract_path: str,
                    policy: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if role == "test-writer":
        tests = [{"class": "tests", "root": root} for root in policy["test_roots"]]
        contract = {"class": "contract", "root": Path(contract_path).parent.as_posix()}
        return [contract, *tests], list(tests)
    if role == "implementer":
        write = [{"class": "implementation", "root": root} for root in policy["implementation_roots"]]
        write += [{"class": "implementation", "path": path} for path in policy.get("implementation_files", [])]
        return [{"class": "repository-read"}], write
    return [{"class": "repository-read"}], []


def _next_packet_id(out_dir: Path, prefix: str) -> str:
    number = 1
    while (out_dir / f"{prefix}-{number:03d}").exists():
        number += 1
    return f"{prefix}-{number:03d}"


def _require_ignored_temporary_scope(write_scope: list[dict[str, Any]],
                                     project_root: Path) -> None:
    """PD-16 (§2.9/INV-3): a declared temporary must be ignored by Git.

    Read-only `git check-ignore` over the declared selectors; a selector that
    is not ignored, or a project that is not a Git work tree, fails CLOSED
    naming both legitimate exits (declare the root in `.gitignore`, or do not
    request the temporary). Only the temporary class is verified: every other
    scope keeps today's behavior.
    """
    selectors = [scope.get("root", scope.get("path"))
                 for scope in write_scope
                 if isinstance(scope, dict) and scope.get("class") == "temporary"]
    for selector in selectors:
        if not isinstance(selector, str) or not selector:
            continue
        try:
            proc = subprocess.run(
                ["git", "check-ignore", "-q", "--", selector],
                cwd=str(project_root), capture_output=True, text=True)
        except OSError as exc:
            raise PolicyError(
                f"temporary scope {selector!r} cannot be verified: `git "
                f"check-ignore` is unavailable ({exc}); the legitimate exits are "
                f"to declare the temporary in .gitignore, or to not request the "
                f"temporary (omit --write-scope temporary=...)"
            ) from exc
        if proc.returncode == 0:
            continue
        if proc.returncode == 1:
            raise PolicyError(
                f"temporary scope {selector!r} is not ignored by Git: a "
                f"temporary root must be declared in .gitignore (a Git work "
                f"tree is required); the legitimate exits are to declare it in "
                f".gitignore, or to not request the temporary (omit "
                f"--write-scope temporary=...)"
            )
        raise PolicyError(
            f"temporary scope {selector!r} cannot be verified: {project_root} "
            f"is not a Git work tree (`git check-ignore` exited "
            f"{proc.returncode}); the legitimate exits are to declare the "
            f"temporary in .gitignore inside a Git work tree, or to not "
            f"request the temporary (omit --write-scope temporary=...)"
        )


def _cwd_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else Path.cwd() / path


def propose_policy(project_root: Path) -> str:
    """Deterministic, read-only policy proposal derived from the detected layout."""
    path_policy: dict[str, list[str]] = {
        "test_roots": ["tests"] if (project_root / "tests").is_dir() else [],
        "implementation_roots": [name for name in LAYOUT_IMPL_ROOTS
                                 if (project_root / name).is_dir()],
        "documentation_roots": ["docs"] if (project_root / "docs").is_dir() else [],
    }
    if (project_root / "install.sh").is_file():
        path_policy["implementation_files"] = ["install.sh"]
    document = {
        "schema_version": 1,
        "path_policy": path_policy,
        # D-5 (006-005 U3, C1/C2): the default temporary root is a PROPOSAL for
        # the owner (`.cdad/tmp`, a subdirectory disjoint from the CLI's own
        # subtrees); the accepted policy of a project is never touched here.
        "temporary_roots": [DEFAULT_TEMPORARY_ROOT],
    }
    # A proposal that its own validator would reject is not emitted.
    _validate_policy_document(document, project_root)
    return json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _policy_location(project_root: Path) -> Path:
    """Resolve docs/cdad-policy.json inside the project (never an escaping symlink)."""
    return _project_path(project_root, POLICY_RELPATH.as_posix(), "policy path")


def _policy_present(project_root: Path) -> bool:
    """True when a usable policy file exists. An existing but non-file location
    (e.g. a directory) is invalid and must not fall back to the legacy path (F6)."""
    path = _policy_location(project_root)
    if path.exists():
        if not path.is_file():
            raise PolicyError(
                f"policy location is invalid: {POLICY_RELPATH.as_posix()} exists but is "
                f"not a regular file"
            )
        return True
    return False


def _load_policy(project_root: Path) -> tuple[dict[str, Any], str, str]:
    """Load docs/cdad-policy.json: return (path_policy, exact file sha256, snapshot).

    The snapshot is the base64 of the exact bytes the digest covers, so a
    consumer can verify the recorded revision against the file content (PD-5).
    """
    path = _policy_location(project_root)
    raw = _read_bytes(path, "project policy")
    return _load_policy_from_bytes(raw, project_root)


def _load_policy_from_bytes(raw: bytes, project_root: Path) -> tuple[dict[str, Any], str, str]:
    """Derive (path_policy, sha256, snapshot) from ONE set of policy bytes.

    The classification, the digest and the snapshot come from the same read
    (F4): a caller that accepts a revision validates exactly the bytes it will
    record, and an invalid policy is rejected before any publication."""
    try:
        document = _object(json.loads(raw.decode("utf-8")), "project policy")
    except (UnicodeError, ValueError) as exc:
        raise PolicyError(f"cannot parse project policy: {exc}") from exc
    path_policy = _validate_policy_document(document, project_root)
    digest = hashlib.sha256(raw).hexdigest()
    return path_policy, digest, base64.b64encode(raw).decode("ascii")


def _fail_point(point: str) -> None:
    """Inert interruption hook (I5/PD-11): exits at a declared point only when
    CDAD_TEST_FAIL_AT names it. Without the variable it never has an effect."""
    if os.environ.get(FAIL_AT_ENV) == point:
        os._exit(FAIL_AT_RC)


def _pause_point(point: str) -> None:
    """Inert synchronisation hook (I5b/PD-11): at the declared point the
    process creates <file>.reached and waits until <file> exists (up to
    PAUSE_TIMEOUT_SECONDS). Without the variables it never has an effect."""
    if os.environ.get(PAUSE_AT_ENV) != point:
        return
    raw = os.environ.get(PAUSE_FILE_ENV)
    if not raw:
        return
    flag = Path(raw)
    deadline = time.monotonic() + PAUSE_TIMEOUT_SECONDS
    try:
        flag.with_name(flag.name + ".reached").write_text("reached", encoding="utf-8")
    except OSError:
        return
    while not flag.exists() and time.monotonic() < deadline:
        time.sleep(0.05)


# Files a publication transaction may create inside its staging/packet dirs.
# Recovery and rollback both clean ONLY these names, so a foreign entry placed
# inside a reused directory is never removed (F3, invariant 7).
TXN_OWNED_FILES = ("execution.json", "REQUEST.json", "PACKET.md", "state.json")
# A-4: a transaction-owned staging directory is identified by this manifest,
# so recovery only ever touches directories created by this mechanism and
# never a foreign directory that happens to sit under .cdad/.txn.
TXN_MANIFEST = ".cdad-txn"


def _remove_owned_files(directory: Path) -> None:
    """Remove only the transaction-owned files from a directory, never the
    directory itself and never a foreign entry (F3)."""
    for name in TXN_OWNED_FILES:
        target = directory / name
        if target.is_file():
            try:
                target.unlink()
            except OSError:
                pass


def cleanup_stale_transactions(project_root: Path) -> None:
    """Recover from an interrupted publication: remove the transaction-owned
    FILES left under .cdad/.txn. Only directories carrying OUR manifest are
    touched, and only their own files are removed (the directory itself is
    kept as the journal entry); a foreign directory — and every file inside
    it — always survives (A-4, invariant 7)."""
    base = project_root / TXN_DIRNAME
    if not base.is_dir():
        return
    for stage_dir in sorted(base.iterdir()):
        if not stage_dir.is_dir():
            continue
        if not (stage_dir / TXN_MANIFEST).is_file():
            continue  # not one of ours: leave it (and its contents) untouched
        _remove_owned_files(stage_dir)
        derived_stage = stage_dir / DERIVED_STAGE_DIRNAME
        if derived_stage.is_dir():
            for entry in sorted(derived_stage.iterdir()):
                if entry.is_file():
                    try:
                        entry.unlink()
                    except OSError:
                        pass
            try:
                derived_stage.rmdir()
            except OSError:
                pass


def _current_policy_bytes_and_sha(project_root: Path) -> tuple[bytes, str]:
    """Read docs/cdad-policy.json once: (exact bytes, sha256) (PD-5)."""
    path = _policy_location(project_root)
    if not path.is_file():
        raise PolicyError(f"project policy not found: {POLICY_RELPATH.as_posix()}")
    raw = _read_bytes(path, "project policy")
    return raw, hashlib.sha256(raw).hexdigest()


def _ensure_policy_reconciled(project_root: Path, execution_document: dict[str, Any]) -> None:
    """PD-5: a v2 execution may only proceed while its policy revision matches
    the current bytes of docs/cdad-policy.json. A byte change (even a valid
    JSON change) blocks prepare, resume and dispatch registration until the
    owner reconciles the accepted revision."""
    if execution_document.get("schema_version") != V2_SCHEMA_VERSION:
        return
    expected = execution_document["execution"]["policy_sha256"]
    _, current = _current_policy_bytes_and_sha(project_root)
    if current != expected:
        raise PolicyError(
            f"docs/cdad-policy.json changed since the execution snapshot "
            f"({expected} -> {current}): the policy revision must be reconciled before "
            f"preparing, resuming or registering a dispatch "
            f"(prepare --reconcile-policy {current} --decision-ref <ruta>)"
        )


class _ProjectLock:
    """Single-writer lock per project: fcntl.flock on .cdad/.lock (I5/PD-11).

    Held during resolution, identity reservation and publication. A second
    writer is rejected immediately (LOCK_NB) with a busy diagnostic. The lock
    is released by the OS if the process dies, so it is never orphaned.

    I5c/I5d (T3 review-fix):
    - Success: `.cdad/.lock` is a PERMANENT rendezvous handle; on exit only the
      flock and the descriptor are released, never the file (F1).
    - Failure AFTER a verified acquisition: if THIS invocation created
      `.cdad/.lock` (and `.cdad`), they are removed as the last step, still
      while holding the flock and after the caller's rollback (PD-3).
    - The acquisition-failure path NEVER removes the file: a process that did
      not obtain the flock of that inode must not touch the holder's lock
      (A-1). It only closes its descriptor.
    - The file is created with O_CREAT|O_EXCL, so "this invocation created it"
      is known race-free; otherwise it is opened plainly.
    - Acquisition verification: after the flock, `fstat(fd).st_ino` must equal
      `stat(path).st_ino`; a mismatch (retired/replaced inode) or a vanished
      path counts as busy and never acquires (I5c, A-3)."""

    def __init__(self, project_root: Path) -> None:
        self._path = project_root / LOCK_RELPATH
        self._fd: int | None = None
        self._acquired = False
        self._created_dir = False
        self._created_file = False

    def __enter__(self) -> "_ProjectLock":
        parent = self._path.parent
        if not parent.exists():
            try:
                parent.mkdir(parents=True)
            except OSError as exc:
                raise PolicyError(f"cannot create .cdad for the project lock: {exc}") from exc
            self._created_dir = True
        # I5d: decide FIRST whether the rendezvous file must be created, then
        # take the optional pause point, which sits after that decision and
        # before opening the file; inert without the variables.
        must_create = not self._path.exists()
        _pause_point("before-lock-open")
        try:
            # Open the existing rendezvous plainly; only create it (race-free,
            # O_CREAT|O_EXCL) when it does not exist, so "this invocation
            # created it" is known (A-1/A-3).
            if not must_create:
                self._fd = os.open(self._path, os.O_RDWR)
                self._created_file = False
            else:
                try:
                    self._fd = os.open(self._path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o644)
                    self._created_file = True
                except FileExistsError:
                    # Another process created it between the check and the
                    # open: open theirs without claiming ownership.
                    self._fd = os.open(self._path, os.O_RDWR)
                    self._created_file = False
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # The inode actually locked must still be the one the path names:
            # if another process retired the file between open and flock, a
            # third process could lock a fresh inode concurrently (I5c, A-3).
            held = os.fstat(self._fd).st_ino
            if not self._path.exists() or os.stat(self._path).st_ino != held:
                self._close_fd()
                raise PolicyError(
                    f"another process holds the project lock: {LOCK_RELPATH.as_posix()} is "
                    f"busy (bloqueo ocupado, lock in use): the lock inode was replaced"
                )
            self._acquired = True
        except PolicyError:
            # Acquisition failure: NEVER remove the lock (A-1). Only a
            # verified acquisition may clean up its own file on exit.
            self._close_fd()
            raise
        except OSError as exc:
            self._close_fd()
            raise PolicyError(
                f"another process holds the project lock: {LOCK_RELPATH.as_posix()} is "
                f"busy (bloqueo ocupado, lock in use): {exc}"
            ) from exc
        return self

    def _close_fd(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None

    def _remove_own(self) -> None:
        """Remove the rendezvous only after a verified acquisition and only if
        THIS invocation created it, while the flock is still held (no other
        process can be in the critical section)."""
        if self._created_file:
            try:
                self._path.unlink()
            except OSError:
                pass
            self._created_file = False
        if self._created_dir:
            try:
                self._path.parent.rmdir()
            except OSError:
                pass
            self._created_dir = False

    def __exit__(self, exc_type, exc, tb) -> bool:
        # On failure after a verified acquisition the caller's rollback has
        # already run: drop our own trace as the last step, still holding the
        # flock, then release it. A failed acquisition never reaches here with
        # _acquired set, so it can never remove another process's lock.
        if exc_type is not None and self._acquired:
            self._remove_own()
        if self._fd is not None:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
            except OSError:
                pass
            self._close_fd()
        return False


def _approved_epic_plan_entry(state: dict[str, Any], epic_id: str | None) -> dict[str, Any] | None:
    """The architect's mandate: an `epic_history` entry for the active epic with
    `stage == "epic-plan"` and a non-empty `approved_by` (D1). Either the `epic`
    or the `epic_id` key names the epic; there is no hash pin (D2, the epic plan
    is the epic's live mandate, not a frozen feature contract)."""
    history = state.get("epic_history")
    if isinstance(history, list):
        for item in history:
            if not isinstance(item, dict):
                continue
            if (item.get("epic", item.get("epic_id")) == epic_id
                    and item.get("stage") == "epic-plan"
                    and isinstance(item.get("approved_by"), str) and item["approved_by"]):
                return item
    return None


def _superseded_transition_keys(state: dict[str, Any]) -> set[str]:
    """PD-14 (D-8): the transition keys a later entry declared replaced.

    The replacement is marked on the NEW entry (`supersedes`, naming the
    `transition_key` of the replaced one) and never by rewriting it: the
    history stays append-only (INV-3). A state with no `supersedes` key — the
    historical history, which never carries the additive field — yields the
    empty set, so the selection below is unchanged (additivity, PD-17)."""
    history = state.get("stage_history")
    if not isinstance(history, list):
        return set()
    superseded: set[str] = set()
    for item in history:
        if not isinstance(item, dict):
            continue
        mark = item.get("supersedes")
        if isinstance(mark, str) and mark:
            superseded.add(mark)
    return superseded


def _approved_spec_entries(state: dict[str, Any], feature_id: str) -> list[dict[str, Any]]:
    """Spec-approval records for the feature: `stage_history` entries with the
    feature, `stage == "specification"` and a non-empty `approved_by`. The
    caller decides whether their `contract_path`/`contract_sha256` pin matches
    the contract verified for this role (D3); an entry without a matching pin
    never authorizes anything (INV-6).

    PD-14 (D-8): among those records only the VIGENTE ones authorize. An entry
    named by another entry's `supersedes` is ignored from then on. The
    predicate is additive: the pin rule (D3/PD-18) is consumed untouched and a
    history without `supersedes` selects exactly as before (PD-17/INV-3)."""
    history = state.get("stage_history")
    if not isinstance(history, list):
        return []
    superseded = _superseded_transition_keys(state)
    return [item for item in history
            if isinstance(item, dict) and item.get("feature") == feature_id
            and item.get("stage") == "specification"
            and isinstance(item.get("approved_by"), str) and item["approved_by"]
            and item.get("transition_key") not in superseded]


def _contract_approval_for(role: str, contract: dict[str, Any], state: dict[str, Any],
                           execution: dict[str, Any], project_root: Path) -> None:
    """Role-aware contract approval (005-001 T1; D1/D2/D3).

    The approval that authorizes a role is specific to *that role's object* and
    is checked only where the contract bytes are already verified
    (`validate_request`), never as a role-agnostic vigency condition of the
    state (that was the circular I2 this feature corrects):

    - **architect** — an `epic_history` entry for the active epic with
      `stage == "epic-plan"` and a non-empty `approved_by` (D1; the epic plan
      is the architect's mandate, no hash pin — D2).
    - **every other role** — a `stage_history` entry for the execution feature
      with `stage == "specification"`, a non-empty `approved_by`, and the
      mandatory `contract_path`/`contract_sha256` pin whose digest equals the
      contract already verified here (D3). A drifted contract invalidates the
      approval (PD-4).

    A declared `draft-plan` is a first-class, non-approved review object: it
    never requires an approval record here. `project_root` belongs to the
    declared interface; the compared digest is the one verified by the caller.
    """
    if contract.get("kind") == "draft-plan":
        return
    if role == "architect":
        epic_id = execution.get("epic_id")
        if _approved_epic_plan_entry(state, epic_id) is not None:
            return
        raise PolicyError(
            f"approval pending: the architect is enabled by the approved plan of the "
            f"active epic, not by a feature spec; epic_history has no entry with epic "
            f"{epic_id!r}, stage 'epic-plan' and a non-empty approved_by (plan del epic) "
            f"(PD-1/PD-2). Register the epic plan approval in epic_history"
        )
    feature_id = execution.get("feature_id")
    contract_path = contract.get("path")
    current = contract.get("sha256")
    entries = _approved_spec_entries(state, feature_id)
    if not entries:
        raise PolicyError(
            f"approval pending: contract approval record missing: stage_history has no "
            f"entry with feature {feature_id!r}, stage 'specification' and a non-empty "
            f"approved_by whose contract_path names {contract_path!r} and whose "
            f"contract_sha256 matches the current contract (sha256 {current}); register "
            f"the spec approval in stage_history with stage 'specification', approved_by, "
            f"contract_path and contract_sha256 (D3)"
        )
    # C1/PD-18 (INV-8): the pin must NAME the contract — path AND sha. An entry
    # with the right digest but a foreign (or absent) contract_path authorizes
    # nothing; it is the signature of an approval copied from another feature.
    if any(entry.get("contract_sha256") == current
           and entry.get("contract_path") == contract_path for entry in entries):
        return
    sha_matching = [entry for entry in entries if entry.get("contract_sha256") == current]
    if sha_matching:
        registered_path = sha_matching[0].get("contract_path")
        raise PolicyError(
            f"approval pending: contract approval record does not name the current "
            f"contract: the stage_history entry for feature {feature_id!r} and stage "
            f"'specification' registered contract_path {registered_path!r} but the "
            f"verified contract path is {contract_path!r} (sha256 {current}); the "
            f"approval must name the contract it approves (PD-18). Re-register the spec "
            f"approval in stage_history (stage 'specification', approved_by, "
            f"contract_path {contract_path!r}, contract_sha256)"
        )
    registered = entries[0].get("contract_sha256")
    raise PolicyError(
        f"approval pending: contract approval record does not match the current "
        f"contract: the stage_history entry for feature {feature_id!r} and stage "
        f"'specification' registered contract_sha256 {registered!r} but the current "
        f"{contract_path!r} sha256 is {current!r}; the contract drifted after approval, "
        f"re-register the spec approval in stage_history (stage 'specification', "
        f"approved_by, contract_path, contract_sha256) (PD-4)"
    )


def _reject_absent_contract_without_approval(role: str, contract: dict[str, Any],
                                             state: dict[str, Any],
                                             execution: dict[str, Any]) -> None:
    """PD-3/PD-17 (T4): report a construction role's missing contract as the
    actionable approval gap, not as a generic read error.

    A construction role's authority is a `specification` entry pinned to the
    verified contract bytes, so when the contract file is absent there is no
    sha256 to match and the role cannot be enabled. If no entry even names the
    contract path, raise the stable `approval pending` diagnostic (PD-12)
    naming the record to register — this is exactly PD-17's step 2, where the
    spec is created only in the following step. An entry that names the path is
    left to the ordinary read diagnostic (the file itself is the problem). The
    architect's unpinned mandate and a declared draft plan (a non-approved
    object) are not pinned approvals and fall through unchanged.
    """
    if contract.get("kind") == "draft-plan" or role == "architect":
        return
    feature_id = execution.get("feature_id")
    contract_path = contract.get("path")
    if any(entry.get("contract_path") == contract_path
           for entry in _approved_spec_entries(state, feature_id)):
        return
    raise PolicyError(
        f"approval pending: contract approval record missing: the contract "
        f"{contract_path!r} does not exist and stage_history has no entry with "
        f"feature {feature_id!r}, stage 'specification' and a non-empty approved_by "
        f"whose contract_path names it; register the spec approval in stage_history "
        f"with stage 'specification', approved_by, contract_path and contract_sha256 "
        f"(PD-3/PD-17)"
    )


def _active_feature_entry(state: dict[str, Any], feature_id: str) -> dict[str, Any]:
    features = state.get("epic_features")
    if not isinstance(features, list):
        raise PolicyError("epic_features record missing: state.epic_features must be a list")
    matching = [item for item in features
                if isinstance(item, dict) and item.get("id") == feature_id]
    if len(matching) != 1:
        raise PolicyError(
            f"active_feature mismatch: active_feature {feature_id!r} does not match exactly one "
            f"epic_features entry"
        )
    status = matching[0].get("status")
    if status in CLOSED_FEATURE_STATUSES:
        raise PolicyError(
            f"active feature {feature_id!r} is closed: epic_features status {status!r} "
            f"is not in-progress"
        )
    return matching[0]


def _scope_names_epic(scope: Any, epic_id: str) -> bool:
    """An unambiguous reference to the epic: the exact identifier, or the exact
    identifier as a standalone token of a scope list/string. Never a substring
    or prefix of a different identifier (F2)."""
    if isinstance(scope, list):
        return epic_id in scope
    if isinstance(scope, str):
        if scope == epic_id:
            return True
        # W-1c: ':' and parentheses are token separators too (the real scope is
        # "<epic-id>: ..."), so the identifier is matched as an exact token.
        tokens = re.split(r"[,\s;/|:()]+", scope.strip())
        return epic_id in [token for token in tokens if token]
    return False


def _validate_v2_vigency(state: dict[str, Any], project_root: Path, feature_id: str,
                         epic_id: str | None) -> str | None:
    """Current-vigency validation (F1/F2), run once by every consumer through
    `_validate_v2_state` (bootstrap, reuse, validate-state and resume): the
    active feature is the execution feature and is not closed, the active epic
    matches, the epic is not terminal and the delegation is active and
    resolvable. Returns the delegation source when an epic is active, else None.

    The role-specific contract approval is deliberately NOT checked here: it
    depends on the role and on the contract bytes, both known only in
    `validate_request` (`_contract_approval_for`). Validating it in this
    role-agnostic path was the circular I2 that 005-001 T1 corrects.

    Standalone (no active epic) needs only the state coherence below.
    """
    # O2: check the active_feature identity before its epic_features entry so the
    # diagnostic names the feature that actually changed.
    if state.get("active_feature") != feature_id:
        raise PolicyError(
            f"active_feature {state.get('active_feature')!r} does not match the execution "
            f"feature {feature_id!r}"
        )
    _active_feature_entry(state, feature_id)
    if state.get("active_epic") != epic_id:
        raise PolicyError(
            f"active_epic {state.get('active_epic')!r} does not match the execution "
            f"epic {epic_id!r}"
        )
    if epic_id is None:
        return None
    if state.get("epic_stage") not in VALID_EPIC_STAGES:
        raise PolicyError(
            f"epic {epic_id!r} is not vigente: epic_stage "
            f"{state.get('epic_stage')!r} is not one of {sorted(VALID_EPIC_STAGES)}"
        )
    delegation = state.get("hitl_delegation")
    if not isinstance(delegation, dict):
        raise PolicyError(
            "hitl_delegation record missing: an active epic requires a delegation record"
        )
    if delegation.get("revoked_at") is not None or delegation.get("status") == "revoked":
        raise PolicyError("hitl_delegation is revoked: revoked_at is set, no authority remains")
    # W-1 (I2, cut C §4): a vigente record need not carry `status` (it is a
    # field exclusive to another epic). Its absence does not invalidate; when
    # present, the only accepted value is "active".
    status = delegation.get("status")
    if status is not None and status != "active":
        raise PolicyError("hitl_delegation is not active")
    # W-1b: `epic_id` is optional; when present it must match, and its absence
    # leaves the decision to `scope` below.
    delegation_epic = delegation.get("epic_id")
    if delegation_epic is not None and delegation_epic != epic_id:
        raise PolicyError(
            f"hitl_delegation epic mismatch: {delegation_epic!r} != {epic_id!r}"
        )
    scope = delegation.get("scope")
    if not _scope_names_epic(scope, epic_id):
        raise PolicyError(
            f"hitl_delegation scope {scope!r} does not name the active epic {epic_id!r} exactly"
        )
    source = delegation.get("source")
    if not isinstance(source, str) or not source:
        raise PolicyError("hitl_delegation source missing: no authority reference to verify")
    authority = _project_path(project_root, source, "hitl_delegation.source")
    if not authority.is_file():
        raise PolicyError(f"authority reference not found: {source}")
    return source


def _next_execution_id(project_root: Path, feature_id: str) -> str:
    base = project_root / EXECUTIONS_DIR
    number = 1
    while (base / f"exec-{feature_id}-{number:03d}").exists():
        number += 1
    return f"exec-{feature_id}-{number:03d}"


def _bootstrap_v2_execution(args: argparse.Namespace, project_root: Path,
                            state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], bool]:
    """Create an implicit v2 execution from state, policy and authority (PD-3/I3)."""
    feature_id = state.get("active_feature")
    if not isinstance(feature_id, str) or not feature_id:
        raise PolicyError("no active feature in state: cannot bootstrap an execution")
    if FLAT_NAME.fullmatch(feature_id) is None or ".." in feature_id:
        raise PolicyError("active_feature must be a flat name ([A-Za-z0-9._-], no '..')")
    epic_id = state.get("active_epic")
    if epic_id is not None and (not isinstance(epic_id, str) or not epic_id):
        raise PolicyError("active_epic must be a non-empty string or null")
    path_policy, policy_sha256, policy_snapshot = _load_policy(project_root)
    _, contract_path = _contract_for(args.role, {"feature_id": feature_id, "epic_id": epic_id})
    # The authority reference is derived here; the single vigency validation that
    # checks it lives in _validate_v2_state, shared by every consumer (B1).
    authority_ref = contract_path
    if epic_id is not None:
        delegation = state.get("hitl_delegation")
        source = delegation.get("source") if isinstance(delegation, dict) else None
        if isinstance(source, str) and source:
            authority_ref = source
    execution = {
        "id": _next_execution_id(project_root, feature_id),
        "epic_id": epic_id,
        "feature_id": feature_id,
        "scope": epic_id or feature_id,
        "authority_ref": authority_ref,
        "model_policy": DEFAULT_MODEL_POLICY,
        "policy_sha256": policy_sha256,
    }
    document = {
        "schema_version": V2_SCHEMA_VERSION,
        "execution": execution,
        "path_policy": path_policy,
        "policy": {
            "path": POLICY_RELPATH.as_posix(),
            "schema_version": 1,
            "sha256": policy_sha256,
            "snapshot": policy_snapshot,
        },
        "policy_history": [{"sha256": policy_sha256, "snapshot": policy_snapshot}],
    }
    return document, execution, True


def _find_prior_context(project_root: Path, state: dict[str, Any]) -> tuple[dict[str, Any], str] | None:
    """Locate an existing execution context: the state binding, the flat v1 path or
    any published v2 context. Returns (document, 'v1'|'v2') or None."""
    candidates: list[Path] = []
    binding = state.get("execution")
    if isinstance(binding, dict) and isinstance(binding.get("id"), str) and binding["id"]:
        candidates.append(project_root / EXECUTIONS_DIR / binding["id"] / "execution.json")
    flat = project_root / FLAT_EXECUTION_RELPATH
    if flat.is_file():
        candidates.append(flat)
    base = project_root / EXECUTIONS_DIR
    if base.is_dir():
        candidates.extend(sorted(base.glob("*/execution.json")))
    for path in candidates:
        if not path.is_file():
            continue
        document = _load_json(path, "execution context")
        kind = "v2" if document.get("schema_version") == V2_SCHEMA_VERSION else "v1"
        return document, kind
    return None


def _packet_cites_execution(project_root: Path, execution_id: str) -> bool:
    """Whether a published packet declares this execution id (PD-16).

    A published packet records the execution it belongs to in its REQUEST.json
    (`execution_id`) — the canonical record the CLI re-reads on resume and
    dispatch. Read-only."""
    base = project_root / ".cdad" / "packets"
    if not base.is_dir():
        return False
    for request_path in sorted(base.glob("*/REQUEST.json")):
        try:
            request = json.loads(request_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            # An unreadable request is not evidence of use: an interrupted
            # publication is recovered by `prepare` (PD-11/I5), not here.
            continue
        if isinstance(request, dict) and request.get("execution_id") == execution_id:
            return True
    return False


def _open_unused_context(project_root: Path, state: dict[str, Any]) -> str | None:
    """PD-16: the id of the active feature's v2 context when it is OPEN and
    UNUSED — the one `open-unit` minted — and None otherwise.

    "Open" means the state binding points at a published v2 context of the
    active feature; "unused" means no packet was published under its
    `execution_id` and no dispatch record exists. Read-only resolution: the
    caller rejects with `state incoherent` BEFORE any write (INV-7). The scope
    is the declared limit (D-5): a context created by another route, or one
    already used, is not covered."""
    binding = state.get("execution")
    execution_id = binding.get("id") if isinstance(binding, dict) else None
    if (not isinstance(execution_id, str) or FLAT_NAME.fullmatch(execution_id) is None
            or ".." in execution_id):
        return None
    context_path = project_root / EXECUTIONS_DIR / execution_id / "execution.json"
    if not context_path.is_file():
        return None
    try:
        document = _load_json(context_path, "execution context")
    except PolicyError:
        # The binding is not backed by a readable context: nothing is open.
        return None
    if document.get("schema_version") != V2_SCHEMA_VERSION:
        return None
    execution = document.get("execution")
    if not isinstance(execution, dict) or execution.get("feature_id") != state.get("active_feature"):
        return None
    if _packet_cites_execution(project_root, execution_id):
        return None
    if _dispatched_packet_ids(project_root, execution_id):
        return None
    return execution_id


def _select_execution(args: argparse.Namespace, project_root: Path,
                      state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], bool]:
    """Choose the execution for this prepare: explicit context (I4), reused v2,
    implicit bootstrap, or the preserved legacy v1 path. Returns
    (document, execution, write_context)."""
    if args.execution_context:
        document = _load_json(_cwd_path(args.execution_context), "execution context")
        if document.get("schema_version") == V2_SCHEMA_VERSION:
            return document, _validate_v2_execution_document(document, project_root), False
        # PD-10/I4 (retired in the T6 GREEN): a v1 context is never adopted
        # forward — it is not converted, rewritten or validated. The new work
        # context is v2, so an explicit v1 fails with a diagnostic that points
        # to --new-execution / bootstrap. Checked before any publication.
        raise PolicyError(
            "an explicit v1 execution context is not adopted forward (PD-10/D2): "
            f"{args.execution_context} carries schema_version 1; v1 contexts are never "
            "converted or rewritten. Start the new v2 working context with "
            "`prepare --new-execution` (bootstrap) instead"
        )
    if args.new_execution:
        # PD-16: with an OPEN and UNUSED context of the active feature, minting
        # a second id would leave the first one orphaned (the real defect of
        # 005-013). Refused here, before any publication, so the rejection has
        # no effects at all (INV-7). A context already used, or created by
        # another route, is outside this scope (D-5).
        open_execution = _open_unused_context(project_root, state)
        if open_execution is not None:
            relative = (EXECUTIONS_DIR / open_execution / "execution.json").as_posix()
            raise PolicyError(
                f"state incoherent: the execution context {relative} of feature "
                f"{state.get('active_feature')!r} is already open and unused (no packet "
                "published with its execution_id and no dispatch record); a second context "
                "would leave it orphaned. Use the open context, or prepare without "
                "`--new-execution`"
            )
    prior = None if args.new_execution else _find_prior_context(project_root, state)
    if args.new_execution or prior is None:
        return _bootstrap_v2_execution(args, project_root, state)
    document, kind = prior
    if kind == "v2":
        # Vigency and the authority binding are validated once, in
        # _validate_v2_state, for reuse, validate-state and resume alike (B1).
        return document, _validate_v2_execution_document(document, project_root), False
    # A v1 context is only a candidate for forward adoption, never for implicit reuse (I3).
    if _policy_present(project_root):
        raise PolicyError(
            "an existing v1 execution context is present at .cdad/execution.json: "
            "prepare requires --new-execution to start a v2 execution (PD-10)"
        )
    return document, _validate_execution_document(document, project_root), False


def _load_execution_context(project_root: Path, execution_id: Any) -> dict[str, Any]:
    """Load a v2 execution context by its identity (no flag; I3)."""
    if (not isinstance(execution_id, str) or not execution_id
            or FLAT_NAME.fullmatch(execution_id) is None or ".." in execution_id):
        raise PolicyError("execution_id must be a flat name ([A-Za-z0-9._-], no '..')")
    path = project_root / EXECUTIONS_DIR / execution_id / "execution.json"
    if not path.is_file():
        raise PolicyError(
            f"execution context not found: .cdad/executions/{execution_id}/execution.json"
        )
    return _load_json(path, "execution context")


def _reject_resume_with_ordinary_options(args: argparse.Namespace) -> None:
    """I7: resuming re-emits verified bytes; no ordinary prepare option is accepted."""
    present = [flag for flag, value in (
        ("--role", args.role),
        ("--substage", args.substage),
        ("--objective", args.objective),
        ("--expected-output", args.expected_output),
        ("--out-dir", args.out_dir),
        ("--execution-context", args.execution_context),
        ("--reconcile-policy", args.reconcile_policy),
        ("--decision-ref", args.decision_ref),
        ("--record-dispatch", args.record_dispatch),
        ("--attempt-id", args.attempt_id),
        ("--contract-kind", args.contract_kind),
        ("--contract-path", args.contract_path),
        ("--plan-version", args.plan_version),
        ("--object-kind", args.object_kind),
        ("--spec-path", args.spec_path),
        ("--spec-version", args.spec_version),
        ("--plan-task", args.plan_task),
    ) if value is not None]
    if args.new_execution:
        present.append("--new-execution")
    if args.input or args.read_scope or args.write_scope or args.invariant or args.evidence:
        present.append("scopes, inputs, invariants or evidence")
    if present:
        raise PolicyError(
            "--resume-packet re-emits the verified packet bytes and accepts no ordinary "
            "prepare options: " + ", ".join(present)
        )


def _packet_policy_revision(packet_id: str, packet_bytes: bytes) -> str:
    """I11 (B7): the policy revision recorded by the packet itself.

    Every published packet carries its canonical metadata as the first JSON
    line (`execution.policy_sha256` is the revision it was rendered under), so
    the packet alone proves which policy bytes produced it — no re-render
    against a superseded revision is needed.
    """
    try:
        text = packet_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PolicyError(f"packet {packet_id!r} is not valid UTF-8: {exc}") from exc
    lines = text.split("\n", 2)
    if len(lines) < 2 or lines[0] != "---cdad-packet-json":
        raise PolicyError(f"packet {packet_id!r} has no canonical metadata header")
    try:
        metadata = json.loads(lines[1])
    except ValueError as exc:
        raise PolicyError(
            f"packet {packet_id!r} has an unreadable canonical metadata header: {exc}"
        ) from exc
    execution = metadata.get("execution")
    if not isinstance(execution, dict) or not isinstance(execution.get("policy_sha256"), str):
        raise PolicyError(f"packet {packet_id!r} does not record its policy revision")
    return execution["policy_sha256"]


def _resume_packet(args: argparse.Namespace, project_root: Path) -> bytes:
    """Re-emit the verified bytes of a published packet, changing nothing (PD-4/I7).

    No ordinary prepare option is accepted; the identifier must be a flat name
    confined to the packets directory and the stored request must still render
    the canonical packet.

    I11 (B7): a packet rendered under a policy revision that is not the one the
    execution currently accepts is NOT resumed. Re-rendering it against the
    current document would re-dispatch scopes from a superseded policy and
    defeat the owner's reconciliation; its bytes stay on disk and a new packet
    must be prepared under the accepted revision.
    """
    _reject_resume_with_ordinary_options(args)
    packet_id = args.resume_packet
    if not isinstance(packet_id, str) or FLAT_NAME.fullmatch(packet_id) is None or ".." in packet_id:
        raise PolicyError(f"--resume-packet requires a flat packet id, got {packet_id!r}")
    out_dir = project_root / ".cdad" / "packets"
    packet_dir = out_dir / packet_id
    try:
        packet_dir.resolve().relative_to(out_dir.resolve())
    except (OSError, ValueError) as exc:
        raise PolicyError(f"--resume-packet escapes the packets directory: {packet_id!r}") from exc
    request_path = packet_dir / "REQUEST.json"
    packet_path = packet_dir / "PACKET.md"
    if not request_path.is_file() or not packet_path.is_file():
        raise PolicyError(f"packet not found for --resume-packet: {packet_id}")
    request = _load_json(request_path, "packet request")
    state = _load_json(project_root / "docs" / ".cdad-state.json", "project state")
    execution_document = _load_execution_context(project_root, request.get("execution_id"))
    _ensure_policy_reconciled(project_root, execution_document)
    actual = _read_bytes(packet_path, "packet")
    recorded = _packet_policy_revision(packet_id, actual)
    accepted = execution_document["execution"]["policy_sha256"]
    # PD-16/PD-12: an obsolete packet (its contract or its policy revision
    # changed after it was generated) is diagnosed with the stable
    # `packet obsolete` marker, naming the registered and current values and
    # the legitimate next step, instead of a generic mismatch message. The
    # bytes stay on disk and nothing is written.
    stale_contract = request.get("contract") if isinstance(request.get("contract"), dict) else {}
    registered = stale_contract.get("sha256")
    registered_path = stale_contract.get("path")
    current: str | None = None
    if isinstance(registered_path, str) and registered_path:
        candidate = _project_path(project_root, registered_path, "contract.path")
        if candidate.is_file():
            current = hashlib.sha256(_read_bytes(candidate, "contract")).hexdigest()
    if recorded != accepted or current != registered:
        active = state.get("active_packet")
        status = (active.get("status") if isinstance(active, dict)
                  and active.get("id") == packet_id else None)
        if status == "prepared":
            action = f"prepare --replace-packet {packet_id} --reason <texto>"
        elif status == "dispatched":
            action = "reconciliation of the dispatched packet is required"
        else:
            action = "prepare a new packet under the accepted revision"
        raise PolicyError(
            f"packet obsolete: packet {packet_id!r} was rendered under contract "
            f"sha256 {registered} and policy revision {recorded}, but the current "
            f"contract sha256 is {current} and the accepted policy revision is "
            f"{accepted}; the contract or the policy revision changed after this "
            f"packet was generated, so it is not resumed; its bytes are preserved "
            f"on disk. Legitimate next step: {action} (PD-16/I11)"
        )
    validate_request(request, execution_document, state, project_root)
    rendered = render_packet(request, execution_document, project_root).encode("utf-8")
    if actual != rendered:
        raise PolicyError(f"packet {packet_id!r} does not match its canonical rendering")
    return actual


# PD-24 (C2): the assignment universe the superseded record traces field by
# field (conserved vs changed), in the order of the REQUEST.json contract.
ASSIGNMENT_UNIVERSE = (
    "execution_id", "role", "substage", "objective", "inputs", "read_scope",
    "write_scope", "invariants", "expected_output", "evidence_required",
)


def _sentinel_list(values: list[str], flag: str) -> list[str] | None:
    """PD-20 (C2/D7): None when the option was not given, [] for the `-`
    sentinel (an explicitly empty list), the given values otherwise. `-` mixed
    with other values of the same field is an ambiguity, rejected without
    effects."""
    if not values:
        return None
    if "-" in values:
        if len(values) > 1:
            raise PolicyError(
                f"ambiguous {flag} sentinel: '-' must be the only value of {flag} to "
                f"leave the list empty; mixing '-' with other values of the same field "
                f"is rejected (PD-20)"
            )
        return []
    return list(values)


def _with_role_floor(values: list[str], floors: list[str]) -> list[str]:
    """PD-21 (C2/INV-7): a correction replaces the list but never drops the
    role's mandatory floor (re-added, preserving order and without duplicates)."""
    result = list(values)
    for floor in floors:
        if floor not in result:
            result.append(floor)
    return result


def _validate_corrections(
    request: dict[str, Any], *, role: str,
    contract_dir: str, policy: dict[str, Any], project_root: Path,
    temporary_roots: list[str] | None = None,
) -> None:
    """PD-22 (C2) / 005-005 PD-1 (D1): the resulting assignment — conserved and
    corrected fields alike — passes the same validations as an ordinary prepare,
    with a diagnostic that names the field, the reason and the option that
    corrects it (so the owner knows what to change)."""
    for item in request["inputs"]:
        if (not isinstance(item, dict) or set(item) != {"path", "purpose"}
                or not isinstance(item.get("purpose"), str) or not item["purpose"]):
            raise PolicyError(
                "inputs: --input requires PATH=PURPOSE with a non-empty purpose; "
                "correct it with --input (PD-22)")
        candidate = _project_path(project_root, item["path"], "input.path")
        if not candidate.is_file():
            raise PolicyError(
                f"inputs: --input path does not exist: input.path {item['path']!r}; "
                f"correct it with --input (PD-22)")
    for scope in request["read_scope"]:
        try:
            _validate_scope(scope, role=role, write=False, contract_dir=contract_dir,
                            policy=policy, project_root=project_root,
                            temporary_roots=temporary_roots)
        except PolicyError as exc:
            raise PolicyError(
                f"read_scope: --read-scope is invalid: {exc}; correct it with "
                f"--read-scope (PD-22)") from exc
    for item in request["inputs"]:
        if not any(_scope_contains(scope, item["path"], contract_dir, policy, project_root)
                   for scope in request["read_scope"]):
            raise PolicyError(
                f"read_scope: --read-scope leaves input {item['path']!r} outside the "
                f"read scope; correct it with --read-scope (PD-22)")
    for scope in request["write_scope"]:
        try:
            _validate_scope(scope, role=role, write=True, contract_dir=contract_dir,
                            policy=policy, project_root=project_root,
                            temporary_roots=temporary_roots)
        except PolicyError as exc:
            raise PolicyError(
                f"write_scope: --write-scope is invalid: {exc}; correct it with "
                f"--write-scope (PD-22)") from exc


def _replace_packet(args: argparse.Namespace, project_root: Path) -> bytes:
    """Replace a prepared, never-dispatched, genuinely obsolete packet (PD-7..PD-11).

    The sub-mode reuses the previous packet's identity (role/substage/objective/
    execution_id) and re-resolves the contract and policy of the day. It never
    creates or edits approval records (INV-2) and never rewrites the superseded
    packet's bytes (INV-3); it publishes a successor only when the pre-existing
    role-aware approval still matches the current contract (INV-1/PD-11).
    """
    reason = args.reason
    if not isinstance(reason, str) or not reason.strip():
        raise PolicyError("--replace-packet requires a non-empty --reason (PD-9)")
    packet_id = args.replace_packet
    if not isinstance(packet_id, str) or FLAT_NAME.fullmatch(packet_id) is None or ".." in packet_id:
        raise PolicyError(f"--replace-packet requires a flat packet id, got {packet_id!r}")
    out_dir = project_root / ".cdad" / "packets"
    packet_dir = out_dir / packet_id
    with _ProjectLock(project_root):
        cleanup_stale_transactions(project_root)
        state_path = project_root / "docs" / ".cdad-state.json"
        state = _load_json(state_path, "project state")
        active = state.get("active_packet")
        if not isinstance(active, dict) or active.get("id") != packet_id:
            raise PolicyError(
                f"--replace-packet {packet_id!r} is not the active packet: only the "
                f"active packet can be replaced"
            )
        try:
            packet_dir.resolve().relative_to(out_dir.resolve())
        except (OSError, ValueError) as exc:
            raise PolicyError(
                f"--replace-packet escapes the packets directory: {packet_id!r}") from exc
        request_path = packet_dir / "REQUEST.json"
        packet_path = packet_dir / "PACKET.md"
        if not request_path.is_file() or not packet_path.is_file():
            raise PolicyError(f"packet not found for --replace-packet: {packet_id}")
        status = active.get("status")
        # PD-10: a dispatched packet is never replaced in the cold; reconciliation
        # is named as the only legitimate next step, with the stable marker.
        if status == "dispatched":
            raise PolicyError(
                f"packet obsolete: packet {packet_id!r} is dispatched and is not "
                f"replaced in the cold; reconciliation of the dispatched packet is "
                f"required before any new packet is prepared (PD-10)"
            )
        if status != "prepared":
            raise PolicyError(
                f"packet {packet_id!r} is {status!r}: only a prepared packet can be replaced"
            )
        request = _load_json(request_path, "packet request")
        execution_document = _load_execution_context(project_root, request.get("execution_id"))
        _ensure_policy_reconciled(project_root, execution_document)
        execution = execution_document["execution"]
        contract = _object(request.get("contract"), "packet request.contract")
        registered_sha = contract.get("sha256")
        registered_path = contract.get("path")
        actual = _read_bytes(packet_path, "packet")
        recorded_policy = _packet_policy_revision(packet_id, actual)
        accepted_policy = execution["policy_sha256"]
        current_sha: str | None = None
        if isinstance(registered_path, str) and registered_path:
            current_path = _project_path(project_root, registered_path, "contract.path")
            if current_path.is_file():
                current_sha = hashlib.sha256(_read_bytes(current_path, "contract")).hexdigest()
        contract_drifted = current_sha != registered_sha
        policy_drifted = recorded_policy != accepted_policy
        # PD-8: replacement is not a shortcut around PD-4. Without verifiable
        # obsolescence (contract digest or accepted policy revision) nothing is
        # published.
        if not (contract_drifted or policy_drifted):
            raise PolicyError(
                f"--replace-packet {packet_id!r} refused: no verifiable obsolescence "
                f"(the packet's contract and policy revision still match the current "
                f"ones); replacement does not bypass the active-packet rule (PD-8)"
            )
        role, substage = request.get("role"), request.get("substage")
        contract_kind, contract_path = _contract_for(role, execution)
        contract_bytes = _read_bytes(
            _project_path(project_root, contract_path, "contract.path"), "contract")
        digest = hashlib.sha256(contract_bytes).hexdigest()
        new_packet_id = _next_packet_id(out_dir, f"{execution['feature_id']}-{role}-{substage}")
        # PD-19 (C2/INV-7): the successor CONSERVES the predecessor's assignment
        # field by field (identity, role, substage, objective and the six
        # lists/fields), instead of recomputing the role defaults.
        assignment: dict[str, Any] = {
            "execution_id": request.get("execution_id"),
            "role": role,
            "substage": substage,
            "objective": request.get("objective"),
            "inputs": request.get("inputs"),
            "read_scope": request.get("read_scope"),
            "write_scope": request.get("write_scope"),
            "invariants": request.get("invariants"),
            "expected_output": request.get("expected_output"),
            "evidence_required": request.get("evidence_required"),
        }
        # PD-20/PD-21 (C2): each explicit correction option replaces its whole
        # list/field; the `-` sentinel empties it; the role floors are re-added.
        raw_inputs = _sentinel_list(args.input, "--input")
        if raw_inputs is not None:
            assignment["inputs"] = [_cli_input(raw) for raw in raw_inputs]
        raw_read = _sentinel_list(args.read_scope, "--read-scope")
        if raw_read is not None:
            assignment["read_scope"] = [_cli_scope(raw, project_root) for raw in raw_read]
        raw_write = _sentinel_list(args.write_scope, "--write-scope")
        if raw_write is not None:
            assignment["write_scope"] = [_cli_scope(raw, project_root) for raw in raw_write]
        raw_invariants = _sentinel_list(args.invariant, "--invariant")
        if raw_invariants is not None:
            assignment["invariants"] = _with_role_floor(
                raw_invariants, DEFAULT_INVARIANTS.get(role, []))
        if args.expected_output is not None:
            assignment["expected_output"] = ("" if args.expected_output == "-"
                                             else args.expected_output)
        raw_evidence = _sentinel_list(args.evidence, "--evidence")
        if raw_evidence is not None:
            assignment["evidence_required"] = _with_role_floor(raw_evidence, DEFAULT_EVIDENCE)
        new_request = {
            "schema_version": 1,
            "packet_id": new_packet_id,
            "feature_id": execution["feature_id"],
            "contract": {"kind": contract_kind, "path": contract_path,
                         "sha256": digest, "commit": None},
            **assignment,
        }
        # PD-10/INV-4 (iv): the successor CONSERVES the declared plan task; the
        # validation content is re-resolved from the current plan at render time
        # (the contract is re-resolved, never conserved).
        if "plan_task" in request:
            new_request["plan_task"] = request["plan_task"]
        # PD-1 (005-005): the complete resulting assignment — conserved and
        # corrected fields alike — passes the same validations as an ordinary
        # prepare, with a diagnostic naming the field, the reason and the
        # correcting option.
        _validate_corrections(
            new_request, role=role,
            contract_dir=str(Path(contract_path).parent.as_posix()),
            policy=execution_document["path_policy"], project_root=project_root,
            temporary_roots=_accepted_temporary_roots(
                execution_document, project_root))
        new_state = dict(state)
        new_state["active_packet"] = {
            "id": new_packet_id, "role": role, "substage": substage, "status": "prepared",
            "packet_version": 1, "contract_kind": contract_kind, "contract_sha256": digest,
        }
        # INV-1/PD-11: the new contract passes the SAME role-aware approval check
        # as an ordinary prepare. A drifted, unauthorized contract raises
        # `approval pending` here, before any publication.
        validate_request(new_request, execution_document, new_state, project_root)
        packet = render_packet(new_request, execution_document, project_root).encode("utf-8")
        # PD-24 (C2): trace field by field what the successor conserved and what
        # a correction changed; the two sets are disjoint and cover the whole
        # assignment universe (the observable diff between both REQUEST.json).
        conserved_fields = [field for field in ASSIGNMENT_UNIVERSE
                            if new_request.get(field) == request.get(field)]
        changed_fields = [field for field in ASSIGNMENT_UNIVERSE
                          if new_request.get(field) != request.get(field)]
        superseded = {
            "superseded_by": new_packet_id,
            "reason": reason,
            "superseded_at": datetime.now(timezone.utc).isoformat(),
            "contract_sha256_old": registered_sha,
            "contract_sha256_new": digest,
            "conserved_fields": conserved_fields,
            "changed_fields": changed_fields,
        }
        try:
            superseded_bytes = (
                json.dumps(superseded, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n").encode("utf-8")
        except (UnicodeError, ValueError) as exc:
            raise PolicyError(f"cannot serialize superseded record: {exc}") from exc
        _publish_generation(
            project_root=project_root,
            execution_document=execution_document,
            execution=execution,
            write_context=False,
            request=new_request,
            new_state=new_state,
            packet=packet,
            packet_id=new_packet_id,
            out_dir=out_dir,
            extra_writes=[(packet_dir / ".superseded.json", superseded_bytes)],
        )
        return packet


def _resolve_active_execution(project_root: Path, state: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """Resolve the bound execution context from state.execution, without a flag (I3)."""
    binding = state.get("execution")
    if not isinstance(binding, dict) or not isinstance(binding.get("id"), str) or not binding["id"]:
        raise PolicyError("no active execution binding in state: state.execution is empty")
    execution_id = binding["id"]
    return _load_execution_context(project_root, execution_id), execution_id


def reconcile_policy(args: argparse.Namespace, project_root: Path) -> None:
    """Accept a policy revision for the active execution (PD-5/I6).

    Requires a decision-ref inside the project that literally contains the
    accepted sha256, the revision to match the current policy bytes and no
    pending packet. path_policy, snapshot and hash are validated and derived
    from ONE read of the accepted bytes (F4): an invalid policy is never
    accepted. The context and the state binding are published together, so
    validate-state is coherent immediately afterwards (F5); the previous
    revision stays in the history and packages are untouched.
    """
    sha = args.reconcile_policy
    if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{64}", sha) is None:
        raise PolicyError("--reconcile-policy requires a 64-character lowercase hex sha256")
    ref = args.decision_ref
    if not isinstance(ref, str) or not ref:
        raise PolicyError("--reconcile-policy requires --decision-ref <ruta>")
    with _ProjectLock(project_root):
        # Recover any interrupted publication before touching the state.
        cleanup_stale_transactions(project_root)
        decision_path = _project_path(project_root, ref, "decision-ref")
        if not decision_path.is_file():
            raise PolicyError(f"decision-ref not found inside the project: {ref!r}")
        content = _read_bytes(decision_path, "decision-ref").decode("utf-8", errors="replace")
        if sha not in content:
            raise PolicyError(
                f"decision-ref {ref!r} does not contain the accepted revision {sha}")
        # F4: a single read of the accepted bytes yields path_policy, snapshot
        # and hash together; an invalid policy is rejected before any write.
        path = _policy_location(project_root)
        if not path.is_file():
            raise PolicyError(f"project policy not found: {POLICY_RELPATH.as_posix()}")
        raw = _read_bytes(path, "project policy")
        current = hashlib.sha256(raw).hexdigest()
        if sha != current:
            raise PolicyError(
                f"accepted revision {sha} does not match the current policy bytes {current}")
        path_policy, digest, snapshot = _load_policy_from_bytes(raw, project_root)
        if digest != sha:
            raise PolicyError(
                f"accepted revision {sha} does not match the policy digest {digest}")
        state = _load_json(project_root / "docs" / ".cdad-state.json", "project state")
        active = state.get("active_packet")
        if isinstance(active, dict) and active.get("status") in ACTIVE_PACKET_STATUSES:
            raise PolicyError(
                f"cannot reconcile while packet {active.get('id')!r} is "
                f"{active.get('status')!r}: pending packet (prepared/dispatched)")
        execution_document, execution_id = _resolve_active_execution(project_root, state)
        if execution_document.get("schema_version") != V2_SCHEMA_VERSION:
            raise PolicyError("reconciliation requires an active v2 execution context")
        _validate_v2_execution_document(execution_document, project_root)
        execution = execution_document["execution"]
        old_sha = execution["policy_sha256"]
        history = list(execution_document.get("policy_history") or [])
        if not any(entry.get("sha256") == old_sha for entry in history):
            history.append({"sha256": old_sha, "snapshot": execution_document["policy"]["snapshot"]})
        history.append({"sha256": digest, "snapshot": snapshot})
        new_execution = {**execution, "policy_sha256": digest}
        new_document = {
            "schema_version": V2_SCHEMA_VERSION,
            "execution": new_execution,
            "path_policy": path_policy,
            "policy": {
                "path": POLICY_RELPATH.as_posix(),
                "schema_version": 1,
                "sha256": digest,
                "snapshot": snapshot,
            },
            "policy_history": history,
        }
        _validate_v2_execution_document(new_document, project_root)
        new_state = dict(state)
        new_state["execution"] = {field: new_execution[field] for field in V2_BINDING_FIELDS}
        _validate_v2_state(new_document, new_state, project_root)

        context_path = project_root / EXECUTIONS_DIR / execution_id / "execution.json"
        state_path = project_root / "docs" / ".cdad-state.json"
        _publish_owned_atomically([
            (context_path, _serialize_document(new_document, sorted_keys=True)),
            (state_path, _serialize_document(new_state)),
        ])


def _serialize_document(document: dict[str, Any], *, sorted_keys: bool = False) -> bytes:
    try:
        return (json.dumps(document, ensure_ascii=False, indent=2,
                           sort_keys=sorted_keys) + "\n").encode("utf-8")
    except (UnicodeError, ValueError) as exc:
        raise PolicyError(f"cannot serialize document: {exc}") from exc


def _publish_owned_atomically(writes: list[tuple[Path, bytes]]) -> None:
    """Publish several files with temp files and atomic renames (PD-11).

    All temp files are written first, then renamed into place, so an error
    during preparation leaves the previous generation intact; the owner's
    transaction files are registered for recovery. Foreign entries are never
    touched."""
    temps: list[tuple[Path, Path]] = []
    committed: list[tuple[Path, Path]] = []
    try:
        for target, payload in writes:
            tmp = target.with_name(target.name + ".tmp")
            tmp.write_bytes(payload)
            temps.append((tmp, target))
        for tmp, target in temps:
            os.replace(tmp, target)
            committed.append((tmp, target))
    except OSError as exc:
        for tmp, _target in temps:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
        raise PolicyError(f"cannot publish reconciliation: {exc}") from exc


# PD-6/I8: the dispatch observation document has exactly these keys; identity
# (execution_id, packet_id, role, substage) never comes from it.
OBSERVATION_KEYS = {
    "runtime", "model_configured", "model_reported", "session", "started_at",
    "provenance",
}
OBSERVATION_TEXT_FIELDS = ("runtime", "model_configured", "model_reported", "session", "started_at")
UNOBSERVED_RUNTIME = "multi-runtime"
DISPATCHES_DIRNAME = "dispatches"
# 006-005 U6-5 (D-U65-2): the DECLARED mark of a PROVISIONAL dispatch record.
# `provenance.session` of a write-ahead record starts with it; such a record
# admits exactly ONE completion — a later observation with the SAME fixed
# identity and WITHOUT the mark replaces it. A record without the mark is final
# and the write-once rule is untouched.
WRITE_AHEAD_MARK = "write-ahead:"
DISPATCH_IDENTITY_FIELDS = (
    "execution_id", "packet_id", "role", "substage", "runtime", "started_at",
)


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    """Persist bytes next to their destination and rename atomically (PD-11)."""
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_bytes(payload)
        os.replace(tmp, path)
    except OSError as exc:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise PolicyError(f"cannot write {path.name}: {exc}") from exc


def _load_packet_request(project_root: Path, packet_id: str) -> dict[str, Any]:
    """Load the canonical request of a published packet, confined to .cdad/packets."""
    if not isinstance(packet_id, str) or FLAT_NAME.fullmatch(packet_id) is None or ".." in packet_id:
        raise PolicyError(f"--record-dispatch requires a flat packet id, got {packet_id!r}")
    out_dir = project_root / ".cdad" / "packets"
    packet_dir = out_dir / packet_id
    try:
        packet_dir.resolve().relative_to(out_dir.resolve())
    except (OSError, ValueError) as exc:
        raise PolicyError(f"--record-dispatch escapes the packets directory: {packet_id!r}") from exc
    request_path = packet_dir / "REQUEST.json"
    if not request_path.is_file():
        raise PolicyError(f"unknown packet for --record-dispatch: {packet_id!r}")
    return _load_json(request_path, "packet request")


def _load_observation_document(path: Path) -> dict[str, Any]:
    """Validate the closed-key observation document (I8).

    Every field is text or null; `provenance` maps a field to its source.
    Unknown keys (including forged identity fields or reception results) are
    rejected before anything is written.
    """
    document = _load_json(path, "dispatch observation")
    if set(document) != OBSERVATION_KEYS:
        raise PolicyError(
            "dispatch observation fields do not match the closed schema: runtime, "
            "model_configured, model_reported, session, started_at, provenance")
    for field in OBSERVATION_TEXT_FIELDS:
        value = document.get(field)
        if value is not None and (not isinstance(value, str) or not value):
            raise PolicyError(f"dispatch observation.{field} must be a non-empty string or null")
    # B-5: `multi-runtime` never represents an observed runtime; compare
    # without regard to case so `Multi-Runtime` is rejected the same way.
    runtime = document.get("runtime")
    if isinstance(runtime, str) and runtime.strip().lower() == UNOBSERVED_RUNTIME:
        raise PolicyError(
            f"{UNOBSERVED_RUNTIME!r} does not represent an observed runtime: record a concrete "
            f"runtime or null")
    provenance = document.get("provenance")
    if not isinstance(provenance, dict) or any(
            not isinstance(key, str) or not key
            or not isinstance(value, str) or not value
            for key, value in provenance.items()):
        raise PolicyError("dispatch observation.provenance must be an object of field -> source strings")
    # B-2: provenance may only annotate the five observed fields; it must never
    # become a channel to smuggle reception (result/gate/postconditions_status).
    unknown = sorted(set(provenance) - set(OBSERVATION_TEXT_FIELDS))
    if unknown:
        raise PolicyError(
            "dispatch observation.provenance keys must be among the observed fields "
            f"{', '.join(OBSERVATION_TEXT_FIELDS)}: unexpected {', '.join(unknown)}")
    return document


def _provenance_session_text(record: dict[str, Any]) -> str:
    """The `provenance.session` source text of a dispatch record, or `""`."""
    provenance = record.get("provenance")
    value = provenance.get("session") if isinstance(provenance, dict) else None
    return value if isinstance(value, str) else ""


def _is_write_ahead(record: dict[str, Any]) -> bool:
    """Is this record the PROVISIONAL write-ahead observation? (D-U65-2)."""
    return _provenance_session_text(record).startswith(WRITE_AHEAD_MARK)


def _completion_rejection(existing: dict[str, Any],
                          incoming: dict[str, Any]) -> str | None:
    """Why `incoming` may NOT complete the recorded attempt, or `None` (D-U65-2).

    The ONE completion is admitted over a record that carries the
    `write-ahead:` mark, produces a record WITHOUT it, and keeps the fixed
    identity (`execution_id`, `packet_id`, attempt, role, substage, runtime,
    `started_at`). A final record, a completion that is itself still marked (it
    would not produce a final record) and a changed identity are all rejected.
    """
    if not _is_write_ahead(existing):
        return ("the existing dispatch record is final (its provenance.session "
                f"does not start with {WRITE_AHEAD_MARK!r}): only a provisional "
                "write-ahead record admits ONE completion")
    if _is_write_ahead(incoming):
        return ("the completion must PRODUCE a final record: the incoming "
                f"observation still carries the {WRITE_AHEAD_MARK!r} mark")
    changed = [
        field for field in DISPATCH_IDENTITY_FIELDS
        if existing.get(field) != incoming.get(field)]
    if changed:
        return ("the completion changes the fixed identity of the attempt: "
                + ", ".join(
                    f"{field} {existing.get(field)!r} -> {incoming.get(field)!r}"
                    for field in changed))
    return None


def _serialize_dispatch(record: dict[str, Any]) -> bytes:
    try:
        return (json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    except (UnicodeError, ValueError) as exc:
        raise PolicyError(f"cannot serialize dispatch record: {exc}") from exc


def _publish_dispatch_atomic(dispatch_path: Path, dispatch_payload: bytes,
                             state_path: Path, state_payload: bytes) -> None:
    """Publish the attempt record and the state in ONE transaction (B-1).

    Both payloads are staged next to their destinations first; only when both
    temps are written does the commit begin (dispatch, then the state binding,
    the authoritative switch). If the state commit fails after the dispatch was
    renamed into place, the dispatch is rolled back so no record survives a
    failed state write."""
    dispatch_tmp = dispatch_path.with_name(dispatch_path.name + ".tmp")
    state_tmp = state_path.with_name(state_path.name + ".tmp")
    created = [] if dispatch_path.parent.exists() else _create_dirs_tracked(dispatch_path.parent)
    try:
        try:
            dispatch_tmp.write_bytes(dispatch_payload)
            state_tmp.write_bytes(state_payload)
        except OSError as exc:
            for tmp in (dispatch_tmp, state_tmp):
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass
            _remove_empty_dirs(created)
            raise PolicyError(f"cannot stage dispatch record and state: {exc}") from exc
        dispatch_committed = False
        try:
            os.replace(dispatch_tmp, dispatch_path)
            dispatch_committed = True
            os.replace(state_tmp, state_path)
        except OSError as exc:
            try:
                state_tmp.unlink(missing_ok=True)
            except OSError:
                pass
            if dispatch_committed:
                try:
                    dispatch_path.unlink(missing_ok=True)
                except OSError:
                    pass
            _remove_empty_dirs(created)
            raise PolicyError(f"cannot publish dispatch record and state: {exc}") from exc
    except PolicyError:
        raise


def _record_dispatch(args: argparse.Namespace, project_root: Path) -> None:
    """Register one dispatch attempt as an observation (PD-6/I8).

    Reads the attempt document from --input, takes execution_id, packet_id, role
    and substage from the published packet, and stores the record under
    .cdad/executions/<execution-id>/dispatches/<attempt-id>.json. The attempt
    record and the state binding are published in ONE transaction (B-1), under
    the T3 lock and atomic-write discipline. Repeating an identical record is
    idempotent (same bytes) and completes any pending prepared -> dispatched
    transition; reusing the attempt id with different data fails without
    overwriting, EXCEPT for the ONE completion of a provisional write-ahead
    record (006-005 U6-5/D-U65-2): an unmarked observation with the same fixed
    identity replaces a record whose `provenance.session` starts with
    `write-ahead:`, and produces a final record. The packet may move prepared
    -> dispatched, never to completed/failed; results, gates and postconditions
    are never touched.
    """
    packet_id = args.record_dispatch
    attempt_id = args.attempt_id
    if not isinstance(attempt_id, str) or not attempt_id:
        raise PolicyError("--record-dispatch requires --attempt-id <id>")
    if (FLAT_NAME.fullmatch(attempt_id) is None or ".." in attempt_id
            or attempt_id in {".", ".."}):
        raise PolicyError(f"--attempt-id must be a plain name ([A-Za-z0-9._-], no path), got {attempt_id!r}")
    if len(args.input) != 1:
        raise PolicyError("--record-dispatch requires exactly one --input <observaciones.json>")
    observation_path = _cwd_path(args.input[0])

    with _ProjectLock(project_root):
        state_path = project_root / "docs" / ".cdad-state.json"
        state = _load_json(state_path, "project state")
        execution_document, execution_id = _resolve_active_execution(project_root, state)
        if execution_document.get("schema_version") != V2_SCHEMA_VERSION:
            raise PolicyError("dispatch registration requires an active v2 execution context")
        # PD-5 control point for the registration (T3): a changed policy blocks
        # it before anything is written.
        _ensure_policy_reconciled(project_root, execution_document)
        request = _load_packet_request(project_root, packet_id)
        if request.get("execution_id") != execution_id:
            raise PolicyError(
                f"packet {packet_id!r} belongs to execution "
                f"{request.get('execution_id')!r}, not the active one {execution_id!r}")
        observation = _load_observation_document(observation_path)

        record = {
            "execution_id": execution_id,
            "packet_id": packet_id,
            "role": request.get("role"),
            "substage": request.get("substage"),
            **{field: observation[field] for field in OBSERVATION_TEXT_FIELDS},
            "provenance": observation["provenance"],
        }
        payload = _serialize_dispatch(record)
        dispatch_path = (project_root / EXECUTIONS_DIR / execution_id
                         / DISPATCHES_DIRNAME / f"{attempt_id}.json")

        already_recorded = dispatch_path.is_file()
        completion = False
        if already_recorded:
            existing_payload = _read_bytes(dispatch_path, "dispatch record")
            if existing_payload != payload:
                try:
                    existing_record = json.loads(
                        existing_payload.decode("utf-8"))
                except (UnicodeDecodeError, ValueError):
                    existing_record = None
                rejection = (
                    None if not isinstance(existing_record, dict)
                    else _completion_rejection(existing_record, record))
                if rejection is not None:
                    raise PolicyError(
                        f"attempt {attempt_id!r} already exists with different observation data: "
                        f"refusing to overwrite a dispatch record ({rejection}; idempotent "
                        f"repeats must be byte-identical)")
                # D-U65-2: the ONE completion of a provisional write-ahead
                # record. It replaces the observation and leaves a final record.
                completion = True

        # Compute the state transition if it is still pending (B-1): an
        # idempotent retry must still complete it, never early-return.
        active = state.get("active_packet")
        transition_pending = (
            isinstance(active, dict) and active.get("id") == packet_id
            and active.get("status") not in {"completed", "failed", "dispatched"})
        if already_recorded and not transition_pending and not completion:
            return
        if transition_pending:
            new_state = dict(state)
            new_state["active_packet"] = {**active, "status": "dispatched"}
            try:
                state_bytes = (json.dumps(new_state, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            except (UnicodeError, ValueError) as exc:
                raise PolicyError(f"cannot serialize project state: {exc}") from exc
        else:
            state_bytes = _read_bytes(state_path, "project state")

        if already_recorded and not completion:
            # The attempt is already on disk; only the state transition remains,
            # published with the same atomic discipline.
            _atomic_write_bytes(state_path, state_bytes)
        else:
            _publish_dispatch_atomic(dispatch_path, payload, state_path, state_bytes)


def _create_dirs_tracked(path: Path) -> list[Path]:
    """Create path and its missing parents, returning the directories this call
    created (shallowest first) so the caller can remove them if they stay empty."""
    missing: list[Path] = []
    current = path
    while not current.exists() and current != current.parent:
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True)
    return list(reversed(missing))


def _remove_empty_dirs(created: list[Path]) -> None:
    """Best-effort removal of directories this operation created, deepest first.

    Never touches preexisting or non-empty entries, and never masks the original
    diagnostic: cleanup errors are swallowed (F5)."""
    for directory in reversed(created):
        try:
            directory.rmdir()
        except OSError:
            pass


def _derived_role(name: str) -> str | None:
    """Classify a project-local OpenCode agent name under the I9 role vocabulary."""
    if not name.startswith("cdad-") or not name.endswith(".md"):
        return None
    stem = name[len("cdad-"):-len(".md")]
    if stem.endswith("-odoo"):
        stem = stem[:-len("-odoo")]
    if stem in {"architect", "reviewer", "scribe"}:
        return "reader"
    if stem in {"test-writer", "implementer", "orchestrator"}:
        return stem
    return None


def _activation_registry(project_root: Path) -> dict[str, Any] | None:
    """The project activation registry (PD-12), or None when absent/invalid."""
    path = project_root / ACTIVATION_REGISTRY_REL
    if not path.is_file():
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return document if isinstance(document, dict) else None


def _registered_agents_dir(project_root: Path) -> Path | None:
    """The registered installation's OpenCode agents directory (PD-12)."""
    registry = _activation_registry(project_root)
    if registry is None:
        return None
    adopted_root = registry.get("adopted_root")
    if not (isinstance(adopted_root, str) and adopted_root.strip()):
        return None
    return Path(adopted_root).expanduser().joinpath(*OPENCODE_AGENTS_SUBDIR)


def _derived_source_dir(project_root: Path) -> Path:
    """Resolve the origin of the installed OpenCode agents (PD-12/INV-7).

    Order: (1) the explicit `CDAD_OPENCODE_AGENTS_DIR`; (2) the installation
    registered in the project activation registry (`.cdad/activation.json`);
    (3) the runtime global default.
    """
    raw = os.environ.get(DERIVED_AGENTS_ENV)
    if raw:
        return Path(raw).expanduser()
    registered = _registered_agents_dir(project_root)
    if registered is not None:
        return registered
    return DEFAULT_DERIVED_SOURCE


def _installation_root(source_dir: Path) -> Path:
    """The installation root behind an OpenCode agents directory (PD-14).

    The installer lays the agents out at `<root>/.config/opencode/agents`.
    """
    parts = source_dir.parts
    if len(parts) >= 3 and parts[-3:] == OPENCODE_AGENTS_SUBDIR:
        return source_dir.parents[2]
    return source_dir


def _installation_version(source_dir: Path) -> str | None:
    """Version/commit marker of the installation behind `source_dir` (PD-14).

    The marker is `version.txt` at the installation root (or, when the layout
    differs, next to the agents). An absent marker declares no version.
    """
    for candidate in (_installation_root(source_dir) / INSTALL_VERSION_MARKER,
                      source_dir / INSTALL_VERSION_MARKER):
        try:
            text = candidate.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if text:
            return text
    return None


def _describe_installation(source_dir: Path) -> str:
    """Human label of an installation: path plus its declared version (PD-13)."""
    version = _installation_version(source_dir)
    return f"{source_dir} (version {version})" if version else str(source_dir)


def _previous_derived_source(derived_dir: Path) -> str | None:
    """`source_dir` declared by the previous derived manifest, if any (PD-13)."""
    manifest_path = derived_dir / DERIVED_MANIFEST_NAME
    if not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    source_dir = manifest.get("source_dir") if isinstance(manifest, dict) else None
    return source_dir if isinstance(source_dir, str) and source_dir else None


def _warn_origin_contradiction(*, source_dir: Path, registered: Path | None,
                               previous: str | None) -> None:
    """Diagnose an origin that changed against the registry or the previous
    manifest (PD-13/INV-7): says which origin would be used and how to resolve
    it, and names the registry and every version in play. Never silent.
    """
    registry_rel = ACTIVATION_REGISTRY_REL.as_posix()
    changed_registry = registered is not None and str(registered) != str(source_dir)
    changed_previous = previous is not None and previous != str(source_dir)
    if not (changed_registry or changed_previous):
        return
    lines = [
        "CDAD prepare: OpenCode agents origin contradiction (INV-7) — resolved "
        f"source {_describe_installation(source_dir)}",
    ]
    if registered is not None:
        lines.append(
            f"  registered in {registry_rel}: "
            f"{_describe_installation(registered)}")
    if previous is not None:
        lines.append(
            "  previous derived manifest source_dir: "
            f"{_describe_installation(Path(previous))}")
    lines.append(
        f"  using the resolved source above; re-run scripts/cdad-activate.py "
        f"with the intended --adopted-root to reconcile {registry_rel}")
    print("\n".join(lines), file=sys.stderr)


def _load_derived_sources(base: Path) -> dict[str, bytes] | None:
    """Installed cdad-*.md agents, or None when there is nothing to derive."""
    if not base.is_dir():
        return None
    sources = {path.name: path.read_bytes() for path in sorted(base.glob("cdad-*.md"))}
    return sources or None


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _implementation_patterns(path_policy: dict[str, Any]) -> list[str]:
    patterns = [f"{root}/**" for root in path_policy.get("implementation_roots", [])]
    patterns.extend(path_policy.get("implementation_files", []))
    return patterns


def _test_patterns(path_policy: dict[str, Any]) -> list[str]:
    patterns: list[str] = []
    for root in path_policy.get("test_roots", []):
        # B3 (PD-7/PD-2): only the declared root, never `**/<root>/**` — a
        # literal `tests/` nested under an implementation root is classified
        # implementation by the policy and must not be amplified into tests.
        patterns.append(f"{root}/**")
    # D1 (005-008/PD-5): declared test files are tests too — the classifier
    # already returns "tests" for exact("test_files"). Include them as literal
    # patterns (never a global `**/*.t`) so read/edit stay in parity with the
    # classifier: allowed to the test-writer, denied to the implementer.
    patterns.extend(path_policy.get("test_files", []))
    return patterns


def _colocated_test_patterns(path_policy: dict[str, Any]) -> list[str]:
    """Globs matching the declared co-located test convention under each root."""
    patterns: list[str] = []
    for root in path_policy.get("colocated_test_roots", []):
        for prefix in path_policy.get("colocated_test_prefixes", []):
            patterns.extend([f"{root}/{prefix}*", f"{root}/**/{prefix}*"])
        for suffix in path_policy.get("colocated_test_suffixes", []):
            patterns.append(f"{root}/*{suffix}")
    return patterns


def _temporary_patterns(temporary_roots: list[str]) -> list[str]:
    """Patterns a derived agent needs to write inside a declared temporary root.

    Same convention as the private barrier (P-1): the literal root plus its
    subtree glob, so OpenCode's findLast map covers descendants too. Roots
    already carrying glob wildcards are emitted verbatim.
    """
    patterns: list[str] = []
    for root in temporary_roots:
        patterns.append(root)
        if not any(char in root for char in "*?["):
            patterns.append(f"{root}/**")
    return patterns


# Role-level test conventions the implementer never edits (anti-gaming,
# ADR-011:94 — same barrier the generator emits in its `edit` map,
# scripts/cdad-generate.py `_IMPL_TEST_GLOBS`). The derived map keeps it on top
# of the policy's declared test roots: under a policy whose test roots do not
# cover, say, `addons/m/tests/`, "never edit tests" still holds (006-005 U6-7).
# B-1 (006-005 review-fix): the barrier is emitted AFTER the implementation
# allows, so it wins over the policy's classification of a test that lives
# inside an implementation root (the derived is never more permissive than the
# generated agent it derives from).
_IMPLEMENTER_TEST_GLOBS = [
    "tests/**", "**/tests/**", "**/*_test.go",
    "**/*.test.js", "**/*.test.ts", "**/*.test.mjs", "**/*.test.cjs",
    "**/*.spec.ts", "**/*.spec.js", "**/test_*.py",
]


def _derived_maps(role: str | None, path_policy: dict[str, Any],
                  temporary_roots: list[str] | None = None
                  ) -> dict[str, list[tuple[str, str]]]:
    """Permission maps (findLast order) for one derived agent (I9/PD-7).

    test-writer: deny implementation reads (co-located tests allowed), edits
    only tests. implementer: edits everything except tests — the policy's
    declared tests plus the role's own test conventions, which win over the
    implementation allows (B-1: a test inside an implementation root stays
    denied to the implementer, as the generated agent denies it). reader:
    the existing read-only map is kept (edit deny). orchestrator: allow-all
    except the policy. Every role excludes docs/cdad-policy.json AND the
    published derivatives under .opencode/agents/ on edit (invariant 3: the
    derivatives are not editable sources by any role).

    W-2 (t7-live-walk.md §3, live probe): OpenCode evaluates `grep`/`glob`
    permissions against the SEARCH PATTERN, not the path. Path entries in those
    maps are inert and would declare a barrier that does not exist, so the
    derived agents emit NO `grep`/`glob` path entries; the live per-path
    barrier is `read` (and `edit`). Claude Code keeps its path-guard mediation
    for Grep/Glob (PD-8/C2), which is a different runtime.
    """
    policy_pattern = POLICY_RELPATH.as_posix()
    derived_pattern = f"{DERIVED_RELPATH.as_posix()}/**"
    # P-1 (004-002): declared private paths are denied in read AND edit for
    # EVERY role, emitted AFTER the role's allow rules so findLast gives the
    # private barrier precedence (obvious, minimal; absent = no change).
    # P-1 review-fix (F-P1): a private entry WITHOUT glob wildcards covers its
    # whole subtree in the Claude Code guard (_is_private_path: entry itself
    # plus `entry/`), but OpenCode's findLast map needs an explicit
    # `<entry>/**` to match descendants — otherwise the runtimes disagree.
    # Emit both the literal entry and its subtree glob; glob-bearing entries
    # are emitted verbatim (they already express their own coverage).
    private: list[tuple[str, str]] = []
    for pattern in _private_path_entries(path_policy):
        private.append((pattern, "deny"))
        if not any(char in pattern for char in "*?["):
            private.append((f"{pattern}/**", "deny"))
    if role == "test-writer":
        colocated = _colocated_test_patterns(path_policy)
        # PD-24 (§2.9/INV-16): the DECLARED temporary roots are the only paths
        # that gain permission, emitted next to the role's allow rules and
        # BEFORE the policy, the derivatives and the private barriers, so
        # findLast keeps those barriers on top (O-4). With an empty list the
        # map is byte-identical to today's (control negativo).
        temporary = [(pattern, "allow")
                     for pattern in _temporary_patterns(temporary_roots or [])]
        # D2 (005-008/PD-1/PD-6): the declared test tree reopens AFTER the
        # implementation deny and BEFORE `private`, so findLast keeps the
        # private barrier on top while the test-writer can read its tests.
        read = ([(pattern, "deny") for pattern in _implementation_patterns(path_policy)]
                + [(pattern, "allow") for pattern in _test_patterns(path_policy)]
                + [(pattern, "allow") for pattern in colocated]
                + private)
        edit = ([("*", "deny")]
                + [(pattern, "allow") for pattern in _test_patterns(path_policy)]
                + [(pattern, "allow") for pattern in colocated]
                + temporary
                + [(policy_pattern, "deny"), (derived_pattern, "deny")]
                + private)
        return {"read": read, "edit": edit}
    if role == "implementer":
        # B-1 (006-005 review-fix): the ROLE BARRIER wins over the policy's
        # classification. The implementation allows are emitted FIRST, so the
        # role's own test conventions (`_IMPLEMENTER_TEST_GLOBS`) come AFTER
        # them and win by findLast: a test that lives inside an implementation
        # root (`scripts/tests/test_example.py`, `skills/demo/test_example.py`,
        # `sources/ui/widget.spec.ts`) resolves `deny` for the implementer,
        # exactly as the GENERATED agent denies it. The policy only RESTRICTS:
        # its own test/colocated denies, the policy file, the derivatives and
        # the private paths come last and keep their precedence.
        implementation_allows = [(pattern, "allow")
                                 for pattern in _implementation_patterns(path_policy)]
        denied = (_test_patterns(path_policy)
                  + _colocated_test_patterns(path_policy))
        edit = ([("*", "allow")]
                + implementation_allows
                + [(pattern, "deny") for pattern in _IMPLEMENTER_TEST_GLOBS]
                + [(pattern, "deny") for pattern in denied]
                + [(policy_pattern, "deny"), (derived_pattern, "deny")]
                + private)
        maps: dict[str, list[tuple[str, str]]] = {"edit": edit}
        if private:
            maps["read"] = list(private)
        return maps
    if role == "orchestrator":
        edit = ([("*", "allow"), (policy_pattern, "deny"),
                 (derived_pattern, "deny")] + private)
        maps = {"edit": edit}
        if private:
            maps["read"] = list(private)
        return maps
    if private:
        # Read-only roles keep their blanket edit deny and gain a read deny.
        return {"read": list(private), "edit": [("*", "deny")] + private}
    return {}


def _rewrite_derived_agent(origin: bytes, maps: dict[str, list[tuple[str, str]]]) -> bytes:
    """Return origin with its read/grep/glob/edit maps replaced and its
    `write` key retired; the rest byte for byte. With no maps the origin is
    copied verbatim apart from the retired `write` key (PD-8/I9).

    R3 (PD-8): every installed source is validated — a source without YAML
    frontmatter fails loudly as a PolicyError (rc 2 with a diagnostic) instead
    of an uncaught ValueError traceback, for every derived role.

    U6-7b (006-005, E2/PD-24): the `write` key of the installed copy belongs
    to the region the derivation replaces and is NOT emitted. The write tool
    of OpenCode v2.0.27 evaluates `edit` and `write` together (findLast), so
    a `write: ask` inherited from an installation prior to the U6-7 fix would
    override the derived `edit` map. The effective write verdict of a derived
    agent must be EXACTLY the verdict of its derived `edit` map.
    """
    text = origin.decode("utf-8")
    start = text.find("---")
    fm_end = text.find("\n---", start + 3) if start != -1 else -1
    if start == -1 or fm_end == -1:
        raise PolicyError(
            "installed derived source has no valid YAML frontmatter; cannot "
            "derive the project-local agents (PD-8/I9)")
    frontmatter = text[:fm_end]
    rest = text[fm_end:]
    kept: list[str] = []
    first_map: int | None = None
    scalar_permission_at: int | None = None
    lines = frontmatter.split("\n")
    index = 0
    while index < len(lines):
        key_match = PERMISSION_MAP_KEY_RE.match(lines[index])
        if key_match is None:
            # R1 (PD-8): an origin whose `permission` is a SCALAR (the
            # orchestrator's `permission: allow`) cannot receive indented map
            # children — that is invalid YAML. Replace the scalar with the map
            # key so the generated block nests as valid YAML; semantically
            # everything not in the map stays allowed (equivalent to `allow`).
            if maps and re.match(r"^permission:[ \t]+\S", lines[index]):
                scalar_permission_at = len(kept)
                kept.append("permission:")
                index += 1
                continue
            kept.append(lines[index])
            index += 1
            continue
        key = key_match.group(1)
        # The key and its children (the map block, scalar form included).
        entry: list[str] = [lines[index]]
        index += 1
        while index < len(lines) and lines[index].startswith("    "):
            entry.append(lines[index])
            index += 1
        if key in DERIVED_MAP_KEYS:
            if not maps:
                # Nothing to replace: the origin keeps its own map.
                kept.extend(entry)
                continue
            # The replaced keys give the insertion point of the derived block.
            if first_map is None:
                first_map = len(kept)
            continue
        # The retired key (`write`): removed with its children, never emitted.
    if not maps:
        # No map to replace: the origin is copied verbatim apart from the
        # retired `write` key (U6-7b) — the read-only roles keep the map
        # their installed copy declares.
        return ("\n".join(kept) + rest).encode("utf-8")
    if first_map is not None:
        insert_at = first_map
    elif scalar_permission_at is not None:
        insert_at = scalar_permission_at + 1
    else:
        insert_at = len(kept)
        for position, line in enumerate(kept):
            if line == "permission:":
                insert_at = position + 1
                break
    block: list[str] = []
    for key in DERIVED_MAP_KEYS:
        rules = maps.get(key)
        if not rules:
            continue
        block.append(f"  {key}:")
        block.extend(f'    "{pattern}": {verb}' for pattern, verb in rules)
    return ("\n".join(kept[:insert_at] + block + kept[insert_at:]) + rest).encode("utf-8")


def _reject_hand_modified_derived(derived_dir: Path, policy_sha: str) -> None:
    """PD-8/I9: a derived agent changed by hand makes prepare fail before any
    write, while the manifest matches the accepted policy revision."""
    manifest_path = derived_dir / DERIVED_MANIFEST_NAME
    if not manifest_path.is_file():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if not isinstance(manifest, dict) or manifest.get("policy_sha256") != policy_sha:
        return  # misaligned with the accepted policy: regenerate
    agents = manifest.get("agents")
    if not isinstance(agents, dict):
        return
    for name, entry in sorted(agents.items()):
        path = derived_dir / name
        if not path.is_file():
            return
        recorded = entry.get("derived_sha256") if isinstance(entry, dict) else None
        try:
            actual = _sha256_bytes(path.read_bytes())
        except OSError:
            return
        if recorded != actual:
            raise PolicyError(
                f"derived agent {name!r} in {DERIVED_RELPATH.as_posix()} was modified by "
                f"hand; resolve the difference before preparing a new packet (PD-8/I9)")


def _retired_derived_names(derived_dir: Path,
                           current_names: set[str]) -> list[str]:
    """R2 (PD-8): derived cdad-*.md declared by the PREVIOUS manifest whose
    source is gone. Only manifest-declared cdad-*.md files are retired; foreign
    files are never touched."""
    manifest_path = derived_dir / DERIVED_MANIFEST_NAME
    if not manifest_path.is_file():
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    agents = manifest.get("agents") if isinstance(manifest, dict) else None
    if not isinstance(agents, dict):
        return []
    return [name for name in sorted(agents)
            if name not in current_names
            and name.startswith("cdad-") and name.endswith(".md")]


def _build_derived_payloads(project_root: Path,
                            execution_document: dict[str, Any]
                            ) -> tuple[Path, list[tuple[str, bytes]], bytes, list[str]] | None:
    """Derive the project-local OpenCode agents for the accepted policy (I9).

    Returns (target_dir, [(name, bytes)], manifest_bytes, retired_names) or None
    when there is no installed source to derive from. Fails before any write
    when an existing derived agent diverges from an aligned manifest.
    """
    source_dir = _derived_source_dir(project_root)
    derived_dir = project_root / DERIVED_RELPATH
    # PD-13/INV-7: a resolved origin that differs from the activation registry
    # or from the previous manifest is never silent; diagnose it, naming the
    # registry and the versions in play, and keep the resolved source.
    _warn_origin_contradiction(
        source_dir=source_dir,
        registered=_registered_agents_dir(project_root),
        previous=_previous_derived_source(derived_dir),
    )
    sources = _load_derived_sources(source_dir)
    if sources is None:
        return None
    policy_sha = execution_document["execution"]["policy_sha256"]
    _reject_hand_modified_derived(derived_dir, policy_sha)
    path_policy = execution_document["path_policy"]
    temporary_roots = _accepted_temporary_roots(execution_document, project_root)
    payloads: list[tuple[str, bytes]] = []
    manifest_agents: dict[str, dict[str, str]] = {}
    for name, origin in sources.items():
        derived = _rewrite_derived_agent(
            origin, _derived_maps(_derived_role(name), path_policy, temporary_roots))
        payloads.append((name, derived))
        manifest_agents[name] = {
            "source_sha256": _sha256_bytes(origin),
            "derived_sha256": _sha256_bytes(derived),
        }
    manifest = {
        "schema_version": 1,
        "policy_sha256": policy_sha,
        # R7 (PD-8/§2): the manifest records the origin of every derivative.
        "source_dir": str(source_dir),
        # PD-14/D5: the published artifact names the origin version/commit so
        # the version a session loaded is verifiable from the manifest.
        "source_version": _installation_version(source_dir),
        "agents": manifest_agents,
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2,
                                 sort_keys=True) + "\n").encode("utf-8")
    retired = _retired_derived_names(derived_dir, set(sources))
    return derived_dir, payloads, manifest_bytes, retired


PLAN_TASKS_FENCE = re.compile(
    r"^```plan-tasks[ \t]*\n(?P<body>.*?)\n?^```[ \t]*$",
    re.DOTALL | re.MULTILINE,
)

# PD-8/F1 (004-003 T4): the token that identifies a plan-tasks declaration.
PLAN_TASKS_TOKEN = "```plan-tasks"
# PD-8 (004-003 T4): the literal that lets a task reference the plan-level
# validation strategy declared once, instead of repeating its content.
VALIDATION_STRATEGY_REF = "@validation_strategy"
# PD-1/PD-2 (005-007 T2): the closed per-task `detail` marker of the plan-tasks
# block. `"next"` (the default, also when the marker is absent) keeps owing the
# per-task validation plan; `"planned"` declares its own detail instead.
PLAN_TASK_DETAIL_VALUES = ("next", "planned")
PLAN_TASK_DETAIL_PLANNED = "planned"
# PD-1: the non-dependency fields a `"planned"` task always declares. The
# mandatory `depends_on` key (present, list-shaped, `[]` valid) is enforced in
# the same branch (`_check_plan_validation_plan`).
PLAN_TASK_PLANNED_FIELDS = ("objective", "uncertainty", "owner", "resolves_when")


def _is_strategy_ref(value: Any) -> bool:
    """A per-task field references the plan strategy (bare or single-element list)."""
    return value == VALIDATION_STRATEGY_REF or (
        isinstance(value, list) and value == [VALIDATION_STRATEGY_REF])


def _plan_tasks_from_contract(
    contract_bytes: bytes,
) -> tuple[list[dict[str, Any]], str | None]:
    """Return the declared tasks and plan-level strategy of a draft plan.

    PD-8 (004-003 T4) makes the canonical fenced ```plan-tasks block mandatory:
    the per-task validation plan is part of the plan, so a declared draft plan
    without it is rejected. F1 (review-t3) closes the silent-skip path: any
    declaration carrying the ```plan-tasks token that is not exactly one
    canonical block — an indented open, an open without a closing fence, an
    open carrying a tag suffix, CRLF line endings or a second block — fails
    loud instead of being treated as "block absent". A plan is never published
    with its checks skipped.
    """
    text = contract_bytes.decode("utf-8", errors="replace")
    if PLAN_TASKS_TOKEN not in text:
        raise PolicyError(
            "draft plan is missing the required plan-tasks block: the per-task "
            "validation plan is part of the plan (PD-8)")
    matches = list(PLAN_TASKS_FENCE.finditer(text))
    if text.count(PLAN_TASKS_TOKEN) != 1 or len(matches) != 1:
        raise PolicyError(
            "draft plan declares a malformed plan-tasks block: exactly one "
            "canonical ```plan-tasks fence is required (unindented open, "
            "closing fence, LF endings, no tag suffix)")
    match = matches[0]
    try:
        document = json.loads(match.group("body"))
    except json.JSONDecodeError as exc:
        raise PolicyError(f"plan-tasks block is not valid JSON: {exc}") from exc
    document = _object(document, "plan-tasks block")
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise PolicyError("plan-tasks block must carry a tasks list")
    for entry in tasks:
        entry = _object(entry, "plan task")
        if not isinstance(entry.get("id"), str) or not entry["id"]:
            raise PolicyError("plan task requires a non-empty id")
    strategy = document.get("validation_strategy")
    if strategy is not None and not isinstance(strategy, str):
        raise PolicyError("plan-tasks validation_strategy must be a string")
    return tasks, strategy


def _check_plan_tasks(tasks: list[dict[str, Any]]) -> None:
    """Mechanical producer/consumer and dependency checks over a draft plan.

    These are the structural mirror of the planning contract's blocking
    findings (planning-contract-draft.md §5): an input without producer, a
    dependency cycle, an incompatible contract and unsafe parallelism. The
    schema/rules decide nothing about plan quality — the reviewer does (PD-2).
    Every diagnostic names the offending tokens only, never exact wording.
    """
    by_id: dict[str, dict[str, Any]] = {}
    produced: dict[str, dict[str, str]] = {}
    for entry in tasks:
        producer_id = entry["id"]
        if producer_id in by_id:
            raise PolicyError(f"plan declares duplicate task id {producer_id!r}")
        by_id[producer_id] = entry
        for item in entry.get("produce") or []:
            item = _object(item, "plan produce entry")
            artifact = item.get("artifact")
            contract = item.get("contract")
            if not isinstance(artifact, str) or not artifact:
                raise PolicyError(f"plan task {producer_id!r} produce entry lacks an artifact")
            if not isinstance(contract, str) or not contract:
                raise PolicyError(
                    f"plan task {producer_id!r} produce entry for {artifact!r} lacks a contract")
            produced.setdefault(artifact, {})[producer_id] = contract

    # 1. Input without producer: a consume entry names a producer that no
    # declared task provides, or a producer that does not produce the artifact.
    for entry in tasks:
        consumer_id = entry["id"]
        for item in entry.get("consume") or []:
            item = _object(item, "plan consume entry")
            artifact = item.get("artifact")
            named_producer = item.get("producer")
            if not isinstance(artifact, str) or not artifact:
                raise PolicyError(f"plan task {consumer_id!r} consume entry lacks an artifact")
            if not isinstance(named_producer, str) or not named_producer:
                raise PolicyError(
                    f"plan task {consumer_id!r} consume entry for {artifact!r} lacks a producer")
            declarations = produced.get(artifact)
            if named_producer not in by_id or not declarations or named_producer not in declarations:
                raise PolicyError(
                    f"plan input {artifact!r} has no producer: task {consumer_id!r} "
                    f"consumes it from undeclared producer {named_producer!r}")

    # 3. Incompatible contract: a consume entry demands a contract version that
    # differs from the one its named producer declares for the same artifact.
    for entry in tasks:
        consumer_id = entry["id"]
        for item in entry.get("consume") or []:
            item = _object(item, "plan consume entry")
            artifact = item.get("artifact")
            named_producer = item.get("producer")
            demanded = item.get("contract")
            if not isinstance(demanded, str) or not demanded:
                raise PolicyError(
                    f"plan task {consumer_id!r} consume entry for {artifact!r} lacks a contract")
            offered = produced.get(artifact, {}).get(named_producer)
            if offered is not None and offered != demanded:
                raise PolicyError(
                    f"incompatible contract for artifact {artifact!r}: task {consumer_id!r} "
                    f"demands {demanded!r} but producer {named_producer!r} declares {offered!r}")

    # 2. Circular dependency: depends_on must form a graph without cycles.
    dependencies: dict[str, list[str]] = {}
    for entry in tasks:
        task_id = entry["id"]
        raw_deps = entry.get("depends_on") or []
        if not isinstance(raw_deps, list) or any(not isinstance(d, str) or not d for d in raw_deps):
            raise PolicyError(f"plan task {task_id!r} depends_on must be a list of task ids")
        missing = [d for d in raw_deps if d not in by_id]
        if missing:
            raise PolicyError(
                f"plan task {task_id!r} depends on undeclared task {missing[0]!r}")
        dependencies[task_id] = list(raw_deps)

    visiting: list[str] = []
    visited: set[str] = set()

    def _visit(task_id: str) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            cycle = visiting[visiting.index(task_id):] + [task_id]
            raise PolicyError(
                "plan depends_on declares a circular dependency: " + " -> ".join(cycle))
        visiting.append(task_id)
        for dependency in dependencies[task_id]:
            _visit(dependency)
        visiting.pop()
        visited.add(task_id)

    for task_id in dependencies:
        _visit(task_id)

    # 4. Invalid parallelism: two tasks declared parallel (mutual ids) that
    # both declare edits to the same file collide.
    for entry in tasks:
        task_id = entry["id"]
        raw_parallel = entry.get("parallel") or []
        if not isinstance(raw_parallel, list) or any(not isinstance(p, str) or not p for p in raw_parallel):
            raise PolicyError(f"plan task {task_id!r} parallel must be a list of task ids")
        files = set(entry.get("files") or [])
        for other_id in raw_parallel:
            other = by_id.get(other_id)
            if other is None:
                raise PolicyError(
                    f"plan task {task_id!r} is parallel with undeclared task {other_id!r}")
            if task_id not in (other.get("parallel") or []):
                continue
            collision = sorted(files & set(other.get("files") or []))
            if collision:
                raise PolicyError(
                    f"unsafe parallelism: tasks {task_id!r} and {other_id!r} declare edits "
                    f"to the same file {collision[0]!r}")


def _check_plan_validation_plan(
    tasks: list[dict[str, Any]], strategy: str | None
) -> None:
    """PD-8/PD-1 (005-007 T2): every task carries the validation its detail asks.

    PD-1/PD-2: the closed per-task ``detail`` marker selects the shape. A
    ``"next"`` task (or one without the marker — the default) keeps declaring
    its per-task validation plan; a ``"planned"`` task is validated by its own
    fields (``objective``, ``uncertainty``, ``owner`` and ``resolves_when``)
    plus the mandatory ``depends_on`` key (present, list-shaped, ``[]`` valid),
    and owes no per-task validation plan. A value outside the closed set fails
    closed naming the task and the value. A block without the marker behaves
    exactly as today (INV-5).

    Structural presence only (PD-2): the checks assert the declared fields
    exist and are non-empty, never their quality. A code task (non-empty
    ``files``) declares ``focal_tests``; a code-less task declares
    ``observable_checks`` instead — a documentary artifact is not validated
    with a fabricated software suite. Every task declares ``regressions``
    (present, possibly empty = "none affected"), ``integration_gate`` and
    ``owner``. A task may reference the plan-level ``validation_strategy``
    with the literal ``@validation_strategy`` instead of repeating content.
    """
    strategy_declared = isinstance(strategy, str) and bool(strategy.strip())
    for entry in tasks:
        task_id = entry["id"]
        detail = entry.get("detail")
        if detail is not None and detail not in PLAN_TASK_DETAIL_VALUES:
            raise PolicyError(
                f"plan task {task_id!r} declares detail {detail!r} outside the "
                "closed set ('next' | 'planned') (PD-1)")
        if detail == PLAN_TASK_DETAIL_PLANNED:
            for field in PLAN_TASK_PLANNED_FIELDS:
                value = entry.get(field)
                if not (isinstance(value, str) and value.strip()):
                    raise PolicyError(
                        f"plan task {task_id!r} is marked detail 'planned' but "
                        f"declares no non-empty {field} (PD-1)")
            # B1 (review-fix, PD-1): a `planned` task always declares its
            # dependencies — the key is PRESENT and list-shaped; `[]` is valid
            # and declares 'no dependencies' (same mechanics as `regressions`).
            # Bounded to the marked path: the next/unmarked path is untouched
            # (INV-5).
            depends_on = entry.get("depends_on")
            if not (isinstance(depends_on, list)
                    and all(isinstance(item, str) and item for item in depends_on)):
                raise PolicyError(
                    f"plan task {task_id!r} is marked detail 'planned' but "
                    f"declares no depends_on list ([] declares no dependencies) (PD-1)")
            continue
        files = entry.get("files")
        is_code = isinstance(files, list) and len(files) > 0
        primary = "focal_tests" if is_code else "observable_checks"
        value = entry.get(primary)
        if _is_strategy_ref(value):
            if not strategy_declared:
                raise PolicyError(
                    f"plan task {task_id!r} references {VALIDATION_STRATEGY_REF!r} "
                    "but the plan-tasks block declares no validation_strategy")
        elif not (isinstance(value, list) and value):
            raise PolicyError(
                f"plan task {task_id!r} is missing its per-task validation plan: "
                "a non-empty focal_tests (code task) or observable_checks "
                "(code-less task) is required (PD-8)")
        if "regressions" not in entry or not isinstance(entry["regressions"], list):
            raise PolicyError(
                f"plan task {task_id!r} must declare its regressions (an empty "
                "list declares 'none affected')")
        gate = entry.get("integration_gate")
        if not _is_strategy_ref(gate) and not (isinstance(gate, str) and gate.strip()):
            raise PolicyError(
                f"plan task {task_id!r} must declare a non-empty integration_gate")
        owner = entry.get("owner")
        if not (isinstance(owner, str) and owner.strip()):
            raise PolicyError(
                f"plan task {task_id!r} must declare a non-empty owner")


# 005-003 T6 (PD-10/INV-4): the additive per-task contract of a packet. A packet
# may DECLARE its plan task (`plan_task`); with it, the render emits the task's
# validation plan — taken from the approved plan's canonical `plan-tasks` block —
# and the applicable contract references, by reference. Without the field the
# render is byte-identical (INV-4: the closed request field set is extended with
# one declared optional property, never relaxed).
PLAN_RELPATH_TEMPLATE = "docs/specs/{feature_id}/plan.md"
PLAN_TASK_HEADING = re.compile(r"(?m)^(#{1,6})[ \t]+(\S+)")
PLAN_TASK_FICHA = re.compile(
    r"Resultado observable\s*/\s*PD cubiertas:\*{0,2}[ \t]*(?P<ids>.+)")
PLAN_TASK_ID_TOKEN = re.compile(r"\b(?:PD|INV|D)-?\d+\b")


def _plan_task_ficha(plan_text: str, task_id: str) -> str:
    """The markdown ficha of a task in the approved plan (from its heading to the
    next heading), or an empty string when the plan does not declare it."""
    headings = list(PLAN_TASK_HEADING.finditer(plan_text))
    for index, match in enumerate(headings):
        if match.group(2) != task_id:
            continue
        start = match.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(plan_text)
        return plan_text[start:end]
    return ""


def _plan_task_applicable_ids(ficha: str) -> list[str]:
    """The PD/INV/D ids the task ficha declares as applicable, in order."""
    match = PLAN_TASK_FICHA.search(ficha)
    if match is None:
        return []
    return PLAN_TASK_ID_TOKEN.findall(match.group("ids"))


def _resolve_task_values(value: Any, strategy: str | None) -> list[str]:
    """A per-task field as a list of strings, resolving the plan-level reference.

    `@validation_strategy` (bare or single-element list) resolves against the
    plan-level `validation_strategy`; an unresolved reference fails closed.
    """
    if _is_strategy_ref(value):
        if not (isinstance(strategy, str) and strategy.strip()):
            raise PolicyError(
                f"plan task references {VALIDATION_STRATEGY_REF!r} but the "
                "plan-tasks block declares no validation_strategy")
        return [strategy]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def _plan_task_sections(request: dict[str, Any], project_root: Path | None) -> list[str]:
    """The two declared sections of a task-scoped packet (PD-10), or [].

    `[]` when the packet declares no plan task (byte-identical render, INV-4).
    With a declared task: `## Task validation plan` carries the task's values
    from the approved plan's canonical `plan-tasks` block (`focal_tests` /
    `observable_checks` / `regressions` / `integration_gate`, with
    `@validation_strategy` resolved), the rule of when to widen the validation
    and the plan provenance (path + sha256); `## Applicable contract` carries the
    applicable PD/INV/D references (from the task ficha) and the contract
    reference. A task absent from the block fails closed naming its id, before
    anything is published.
    """
    task_id = request.get("plan_task")
    if task_id is None:
        return []
    if not isinstance(task_id, str) or not task_id:
        raise PolicyError("request.plan_task must be a non-empty string")
    if project_root is None:
        raise PolicyError(
            f"rendering a packet that declares plan task {task_id!r} requires the "
            "project root to read the approved plan")
    plan_rel = PLAN_RELPATH_TEMPLATE.format(feature_id=request["feature_id"])
    plan_bytes = _read_bytes(_project_path(project_root, plan_rel, "plan.path"), "plan")
    plan_sha = hashlib.sha256(plan_bytes).hexdigest()
    tasks, strategy = _plan_tasks_from_contract(plan_bytes)
    entry = next((task for task in tasks if task.get("id") == task_id), None)
    if entry is None:
        raise PolicyError(
            f"plan task {task_id!r} is absent from the plan-tasks block of "
            f"{plan_rel}: declare the task in the approved plan before preparing "
            f"its packet (PD-10)")
    ficha = _plan_task_ficha(plan_bytes.decode("utf-8", errors="replace"), task_id)
    ids = _plan_task_applicable_ids(ficha)
    lines = ["", "## Task validation plan", "", f"- Task: {task_id}"]
    for label in ("focal_tests", "observable_checks", "regressions"):
        lines.append(f"- {label}:")
        values = _resolve_task_values(entry.get(label), strategy)
        if values:
            lines.extend(f"  - {value}" for value in values)
        else:
            lines.append("  - none declared (none affected)")
    gate = ", ".join(_resolve_task_values(entry.get("integration_gate"), strategy))
    lines.append(f"- integration_gate: {gate}")
    lines.append(
        "- Widen (ampliar) the validation when the change leaves the focal tests: "
        "a shared contract or an uncertain impact expands the validation to the "
        "declared regressions and the integration gate; a local correction uses "
        "the focal tests.")
    lines.append(f"- Plan provenance: {plan_rel} (sha256 {plan_sha})")
    lines.extend([
        "", "## Applicable contract", "",
        f"- Contract: {request['contract']['path']} "
        f"(sha256 {request['contract']['sha256']})",
    ])
    if ids:
        lines.append("- Applicable references: " + ", ".join(ids))
    return lines


# ---------------------------------------------------------------- 005-013 T1
# PD-1/PD-2/PD-3 (unit-projection-v1): the contract of a unit is a projection
# GENERATED from the approved epic plan — the origin block, the unit row located
# STRUCTURALLY (the unique body row of a table that contains the feature id as a
# complete token, with the header of that table) and every level-2 section
# verbatim except the ones the PRODUCT declares as history, with the located
# table's lines removed from its section. The declaration lives ONCE in the
# product asset (PD-3/INV-4): never a per-project list of titles, never prose.

# An id is a flat name; a "complete token" occurrence is delimited by characters
# that cannot be part of an id (`[A-Za-z0-9._-]`).
_ID_CHARS = r"[A-Za-z0-9._-]"
# A markdown table: a header row followed by a separator row (`|---|---|`).
TABLE_SEPARATOR = re.compile(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$")
# A level-2 section heading (`## `, never `### `).
SECTION_HEADING = re.compile(r"^##[ \t]+\S")
# The product's machine-readable anchor declaration (an HTML comment so it never
# renders). The title of the declaration is fixed here; the titles it lists are
# the product's, read from the asset.
ANCHORS_DECLARATION = re.compile(
    r"<!--\s*cdad:plan-anchors\s*\n(?P<body>.*?)\n\s*-->", re.DOTALL)


def _plan_anchors_asset() -> Path:
    """The product asset that declares the plan anchors (PD-3).

    `epic-planning.md` mandates loading and filling this same template, so the
    declaration is a property of the product, not of any one project.
    """
    return (Path(__file__).resolve().parents[2] / "cdad-epic" / "assets"
            / "epic-plan-template.md")


def _declared_plan_anchors() -> dict[str, list[str]]:
    """The product's declared anchors for `history` and `authorization` (PD-3).

    An absent, unreadable or malformed declaration yields NO anchors: every
    section then counts as shared (conservative) and nothing fails closed.
    """
    try:
        text = _plan_anchors_asset().read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {}
    match = ANCHORS_DECLARATION.search(text)
    if match is None:
        return {}
    try:
        document = json.loads(match.group("body"))
    except ValueError:
        return {}
    if not isinstance(document, dict):
        return {}
    anchors: dict[str, list[str]] = {}
    for role in ("history", "authorization"):
        names = document.get(role)
        if isinstance(names, list):
            anchors[role] = [name for name in names if isinstance(name, str) and name]
    return anchors


def _normalize_heading(title: str) -> str:
    """Normalize a heading title: lowercase, collapsed whitespace."""
    return " ".join(title.split()).lower()


def _heading_text(line: str) -> str:
    return line.lstrip("#").strip()


def _heading_matches_anchor(title: str, names: list[str]) -> bool:
    """Whether a heading title IS a declared anchor (PD-3, structural).

    Equality after normalization, or the title starting with the declared name
    followed by a non-alphanumeric separator (so `Autoridad (decisión del
    dueño)` recognizes the anchor `Autoridad`).
    """
    normalized = _normalize_heading(title)
    for name in names:
        candidate = _normalize_heading(name)
        if not candidate:
            continue
        if normalized == candidate:
            return True
        if (len(normalized) > len(candidate) and normalized.startswith(candidate)
                and not normalized[len(candidate)].isalnum()):
            return True
    return False


def _is_table_row(line: str) -> bool:
    return line.lstrip().startswith("|")


def _feature_id_in_line(line: str, feature_id: str) -> bool:
    pattern = re.compile(
        rf"(?<!{_ID_CHARS}){re.escape(feature_id)}(?!{_ID_CHARS})")
    return pattern.search(line) is not None


def _locate_unit(plan_text: str, feature_id: str
                 ) -> tuple[dict[str, Any] | None, str]:
    """Locate the UNIQUE table body row that contains the feature id as a
    complete token (PD-1). Returns `(located, reason)`.

    The search is structural: it walks the tables of the plan (header row +
    separator row + body rows) and never depends on a section title nor on the
    cell's exact form (plain text, a link or backticks all match). `located`
    carries the table's header/separator/row lines and the line span of the
    whole table; `reason` is the non-empty diagnostic when the locator is
    ambiguous (zero rows, or more than one).
    """
    lines = plan_text.split("\n")
    matches: list[dict[str, Any]] = []
    index = 0
    total = len(lines)
    while index < total:
        if (_is_table_row(lines[index]) and index + 1 < total
                and TABLE_SEPARATOR.match(lines[index + 1])):
            body = index + 2
            while body < total and _is_table_row(lines[body]):
                body += 1
            for row_index in range(index + 2, body):
                if _feature_id_in_line(lines[row_index], feature_id):
                    matches.append({
                        "header": lines[index],
                        "separator": lines[index + 1],
                        "row": lines[row_index],
                        "table_start": index,
                        "table_end": body,
                    })
            index = body
        else:
            index += 1
    if not matches:
        return None, (f"no table row contains the feature id {feature_id!r} "
                      f"as a complete token")
    if len(matches) > 1:
        return None, (f"{len(matches)} table rows contain the feature id "
                      f"{feature_id!r} as a complete token (ambiguous)")
    return matches[0], ""


def _unit_contract_fallback_reason(feature_id: str, plan_rel: str,
                                   locator_reason: str) -> str:
    """The declared fallback reason (PD-2): names the plan and why."""
    return (f"unit contract fallback: {locator_reason} in {plan_rel}; the "
            f"approved epic plan is the contract (PD-2)")


def _section_spans(lines: list[str]) -> list[dict[str, Any]]:
    """The level-2 sections of the plan: (start, end) line spans and title."""
    spans: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if SECTION_HEADING.match(line):
            spans.append({"start": index, "title_line": line})
    for position, span in enumerate(spans):
        span["end"] = (spans[position + 1]["start"] if position + 1 < len(spans)
                       else len(lines))
    return spans


def _shared_section_parts(plan_text: str, table_start: int, table_end: int,
                          anchors: dict[str, list[str]]
                          ) -> tuple[list[str], list[str], list[str]]:
    """The `shared` parts of the projection (PD-1/PD-3).

    Every level-2 section verbatim, EXCEPT the sections the product declares as
    history (excluded) and with the located table's lines (header, separator and
    ALL its body rows) removed from the section that contains it. Returns the
    section texts, their labels and the history labels recognized.
    """
    lines = plan_text.split("\n")
    removed = set(range(table_start, table_end))
    shared_texts: list[str] = []
    shared_labels: list[str] = []
    history_labels: list[str] = []
    for span in _section_spans(lines):
        title = _heading_text(span["title_line"])
        if _heading_matches_anchor(title, anchors.get("history", [])):
            history_labels.append(_normalize_heading(title))
            continue
        kept = [lines[index] for index in range(span["start"], span["end"])
                if index not in removed]
        shared_texts.append("\n".join(kept))
        shared_labels.append(span["title_line"].strip())
    return shared_texts, shared_labels, history_labels


def _build_unit_projection(*, feature_id: str, plan_rel: str, plan_bytes: bytes,
                           approved_by: str, policy_sha256: str,
                           located: dict[str, Any],
                           anchors: dict[str, list[str]]) -> bytes:
    """Generate the unit projection deterministically (PD-1/PD-12).

    Origin (provenance: unit, plan, plan sha at generation, approving
    `epic-plan` entry, policy revision, the locator trace and the anchors) +
    the `unit` part (the located table's header + its row, verbatim) + the
    `shared` parts. The same plan bytes, unit and origin inputs produce the same
    projection bytes.
    """
    plan_text = plan_bytes.decode("utf-8", errors="replace")
    plan_sha = hashlib.sha256(plan_bytes).hexdigest()
    lines = plan_text.split("\n")
    section_title = ""
    for index in range(located["table_start"] - 1, -1, -1):
        if SECTION_HEADING.match(lines[index]):
            section_title = lines[index].strip()
            break
    shared_texts, shared_labels, history_labels = _shared_section_parts(
        plan_text, located["table_start"], located["table_end"], anchors)
    authorization = anchors.get("authorization", [])
    authorization_labels = [
        _normalize_heading(_heading_text(text.split("\n", 1)[0]))
        for text in shared_texts
        if _heading_matches_anchor(_heading_text(text.split("\n", 1)[0]), authorization)
    ]
    unit_part = f"{located['header']}\n{located['separator']}\n{located['row']}\n"
    origin = [
        "# Unit contract (unit-projection-v1)",
        "",
        "## Origin",
        "",
        f"- unit: {feature_id}",
        f"- plan: {plan_rel}",
        f"- plan_sha256: {plan_sha}",
        f"- approved_by: {approved_by}",
        f"- policy_sha256: {policy_sha256}",
        f"- locator_section: {section_title}",
        f"- locator_table_header: {located['header']}",
        "- anchors_history: " + _format_names(history_labels),
        "- anchors_authorization: " + _format_names(authorization_labels),
        "- parts:",
        f"  - unit: {section_title}",
    ]
    origin.extend(f"  - shared: {label}" for label in shared_labels)
    projection = ("\n".join(origin) + "\n\n## Unit\n\n" + unit_part
                  + "\n## Shared\n\n" + "\n".join(shared_texts) + "\n")
    return projection.encode("utf-8")


def _format_names(names: list[str]) -> str:
    return "[" + ", ".join(names) + "]"


# ---------------------------------------------------------------- 005-013 T2
# PD-7..PD-11 (change-consequence-v1): the verdict of a change compares the LIVE
# projection (regenerated, read-only) with the REGISTERED one — the projection of
# the most recent packet of the unit — PART BY PART (ignoring the origin), and
# emits `current` (no effect), `impact` (durable, idempotent impact record; the
# orchestrator decides) or `impeded` (authorization withdrawn: fail closed, with
# the existing exit named). Classification is by part identity and part class,
# never by prose (INV-8); only `validate-unit-contract` writes, and only its own
# impact journal (INV-1/INV-9).

IMPACT_JOURNAL_NAME = ".impact.json"


def _execution_policy_sha256(state: dict[str, Any], project_root: Path) -> str | None:
    """The accepted policy revision of the bound execution (provenance only)."""
    binding = state.get("execution")
    if (not isinstance(binding, dict) or not isinstance(binding.get("id"), str)
            or not binding["id"]):
        return None
    path = project_root / EXECUTIONS_DIR / binding["id"] / "execution.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    execution = document.get("execution")
    if isinstance(execution, dict):
        value = execution.get("policy_sha256")
    else:
        value = document.get("policy_sha256")
    return value if isinstance(value, str) else None


def _resolve_live_unit_projection(state: dict[str, Any], project_root: Path
                                  ) -> dict[str, Any]:
    """Regenerate the LIVE unit projection of the active unit (PD-1, read-only).

    Reuses the SAME generator and the same origin inputs as `prepare`, so the
    live digest is the one a new generation would publish. When the unit cannot
    be located without ambiguity the mode is `fallback` and `projection` is None:
    the declared fallback of PD-2, never an error.
    """
    result: dict[str, Any] = {
        "unit": None, "mode": "fallback", "reason": None,
        "projection": None, "plan_rel": None,
    }
    feature_id = state.get("active_feature")
    if not isinstance(feature_id, str) or not feature_id:
        result["reason"] = "no active feature to project a unit contract"
        return result
    result["unit"] = feature_id
    epic_id = state.get("active_epic")
    if not isinstance(epic_id, str) or not epic_id:
        result["reason"] = "no active epic: the architect contract is the legacy path"
        return result
    plan_rel = f"docs/epics/{epic_id}/plan.md"
    plan_path = project_root / plan_rel
    if not plan_path.is_file():
        result["reason"] = f"plan not found: {plan_rel}"
        return result
    try:
        plan_bytes = plan_path.read_bytes()
    except OSError as exc:
        result["reason"] = f"plan not readable: {plan_rel} ({exc})"
        return result
    located, locator_reason = _locate_unit(
        plan_bytes.decode("utf-8", errors="replace"), feature_id)
    if located is None:
        result["reason"] = _unit_contract_fallback_reason(
            feature_id, plan_rel, locator_reason)
        return result
    result["mode"] = "projection"
    result["plan_rel"] = plan_rel
    approving = _approved_epic_plan_entry(state, epic_id) or {}
    result["projection"] = _build_unit_projection(
        feature_id=feature_id,
        plan_rel=plan_rel,
        plan_bytes=plan_bytes,
        approved_by=approving.get("approved_by") or "",
        policy_sha256=_execution_policy_sha256(state, project_root) or "",
        located=located,
        anchors=_declared_plan_anchors(),
    )
    return result


def _projection_parts(text: str) -> dict[str, str]:
    """Decompose a `unit-projection-v1` document into its classified parts.

    Returns `{part_id: content}` preserving order: the `unit` part under the
    literal id `unit`, and each `shared` part under its SECTION TITLE (PD-9).
    The origin is provenance and is not a part: it is never returned, so a
    change that only touches the origin (e.g. the plan sha) is invisible here.
    """
    parts: dict[str, str] = {}
    unit_marker = "\n## Unit\n\n"
    shared_marker = "\n## Shared\n\n"
    unit_index = text.find(unit_marker)
    shared_index = text.find(shared_marker)
    if unit_index == -1 or shared_index == -1 or shared_index < unit_index:
        return parts
    parts["unit"] = text[unit_index + len(unit_marker):shared_index]
    current: str | None = None
    buffer: list[str] = []
    for line in text[shared_index + len(shared_marker):].split("\n"):
        if SECTION_HEADING.match(line):
            if current is not None:
                parts[current] = "\n".join(buffer)
            current = line.strip()
            buffer = [line]
        elif current is not None:
            buffer.append(line)
    if current is not None:
        parts[current] = "\n".join(buffer)
    return parts


def _changed_projection_parts(registered: bytes, live: bytes) -> list[str]:
    """The parts that differ between the registered and the live projection.

    Compared by identity and content, ignoring the origin (PD-8/PD-9). A part
    present on one side only counts as changed; a section whose title changed
    counts on both sides. Deterministic order: the registered order first, then
    the parts that only exist in the live projection.
    """
    registered_parts = _projection_parts(
        registered.decode("utf-8", errors="replace"))
    live_parts = _projection_parts(live.decode("utf-8", errors="replace"))
    changed = [part_id for part_id, content in registered_parts.items()
               if live_parts.get(part_id) != content]
    changed.extend(part_id for part_id in live_parts
                   if part_id not in registered_parts)
    return changed


def _packet_belongs_to_feature(packet_dir: Path, feature_id: str) -> bool:
    """Whether a packet directory was prepared for the given unit (PD-7)."""
    try:
        request = json.loads(
            (packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(request, dict) and request.get("feature_id") == feature_id


def _baseline_projection(state: dict[str, Any], project_root: Path,
                         feature_id: str) -> tuple[str, bytes] | None:
    """The registered projection the verdict compares against (PD-7).

    It is the projection of the LAST packet of the unit: the packet of the
    active feature whose `UNIT-CONTRACT.md` was published most recently (order
    by the file's publication time; tie → the greater packet id; the state's
    `active_packet` also counts as a candidate). Without any packet of the unit
    carrying a registered projection there is NO baseline and the verdict is
    `current`.
    """
    base = project_root / ".cdad" / "packets"
    best: tuple[float, str] | None = None
    if base.is_dir():
        for entry in base.iterdir():
            if not entry.is_dir():
                continue
            projection = entry / UNIT_PROJECTION_NAME
            if not projection.is_file():
                continue
            if not _packet_belongs_to_feature(entry, feature_id):
                continue
            try:
                candidate = (projection.stat().st_mtime, entry.name)
            except OSError:
                continue
            if best is None or candidate > best:
                best = candidate
    active_packet = state.get("active_packet")
    if (isinstance(active_packet, dict)
            and isinstance(active_packet.get("id"), str) and active_packet["id"]):
        entry = base / active_packet["id"]
        projection = entry / UNIT_PROJECTION_NAME
        if projection.is_file() and _packet_belongs_to_feature(entry, feature_id):
            try:
                candidate = (projection.stat().st_mtime, active_packet["id"])
            except OSError:
                candidate = None
            if candidate is not None and (best is None or candidate > best):
                best = candidate
    if best is None:
        return None
    packet_id = best[1]
    try:
        return packet_id, (base / packet_id / UNIT_PROJECTION_NAME).read_bytes()
    except OSError as exc:
        raise PolicyError(
            f"registered unit projection not readable for packet {packet_id!r}: {exc}")


def _authorization_withdrawn(state: dict[str, Any], epic_id: str
                             ) -> dict[str, str] | None:
    """The withdrawn-authorization cause of `impeded` (PD-10), or None.

    The ONLY cause of `impeded`: no `epic_history` `epic-plan` entry with a
    non-empty `approved_by` for the active epic (the existing `approval pending`
    marker), or a `hitl_delegation` revoked or not active (the existing
    `state incoherent` marker). No section of the plan produces `impeded`.
    """
    if _approved_epic_plan_entry(state, epic_id) is None:
        return {
            "marker": "approval pending",
            "detail": (f"epic_history has no entry with epic {epic_id!r}, stage "
                       f"'epic-plan' and a non-empty approved_by"),
            "exit": ("register the epic-plan approval in epic_history (stage "
                     "'epic-plan', approved_by) under the current HITL, or "
                     "restore the hitl_delegation"),
        }
    delegation = state.get("hitl_delegation")
    if not isinstance(delegation, dict):
        return {
            "marker": "state incoherent",
            "detail": "the hitl_delegation record is missing",
            "exit": ("restore the hitl_delegation for the active epic, or "
                     "register the epic-plan approval in epic_history"),
        }
    if (delegation.get("revoked_at") is not None
            or delegation.get("status") == "revoked"):
        return {
            "marker": "state incoherent",
            "detail": ("the hitl_delegation is revoked (status 'revoked' / "
                       "revoked_at set)"),
            "exit": ("restore the hitl_delegation for the active epic, or "
                     "register the epic-plan approval in epic_history"),
        }
    status = delegation.get("status")
    if status is not None and status != "active":
        return {
            "marker": "state incoherent",
            "detail": f"the hitl_delegation is not active (status {status!r})",
            "exit": ("restore the hitl_delegation for the active epic, or "
                     "register the epic-plan approval in epic_history"),
        }
    return None


def _withdrawn_reason(withdrawn: dict[str, str]) -> str:
    return (f"authorization withdrawn ({withdrawn['marker']}): "
            f"{withdrawn['detail']} (PD-10). Exit: {withdrawn['exit']}; then "
            "prepare rc=0 and the new packet publishes the new projection, "
            "which becomes the baseline (PD-7/PD-10)")


def _unit_contract_verdict(state: dict[str, Any], project_root: Path,
                           feature_id: str, epic_id: str) -> dict[str, Any]:
    """Compute the change verdict, READ-ONLY (PD-7..PD-11).

    Shared by `validate-unit-contract` and the `unit_contract` block of
    `status`. It reads the state, the plan and the packet projections and
    writes nothing. The verdict is `current` (no part differs, or no baseline),
    `impact` (the `unit` part or some `shared` part differs) or `impeded`
    (authorization withdrawn).
    """
    block: dict[str, Any] = {
        "mode": "fallback", "unit": feature_id, "registered": None, "live": None,
        "verdict": None, "changed_parts": [], "reason": None,
    }
    live = _resolve_live_unit_projection(state, project_root)
    if live["mode"] != "projection" or live["projection"] is None:
        block["reason"] = live["reason"]
    else:
        block["mode"] = "projection"
        live_sha = hashlib.sha256(live["projection"]).hexdigest()
        block["live"] = {"sha256": live_sha}
        baseline = _baseline_projection(state, project_root, feature_id)
        if baseline is None:
            block["verdict"] = "current"
            block["reason"] = ("no packet of the unit has a registered "
                               "projection: nothing to compare (PD-7)")
        else:
            packet_id, registered_bytes = baseline
            block["registered"] = {
                "packet_id": packet_id,
                "sha256": hashlib.sha256(registered_bytes).hexdigest(),
            }
            block["changed_parts"] = _changed_projection_parts(
                registered_bytes, live["projection"])
            if block["changed_parts"]:
                block["verdict"] = "impact"
                block["reason"] = (
                    "parts differ from the registered projection of packet "
                    f"{packet_id} (PD-9): "
                    + ", ".join(block["changed_parts"]))
            else:
                block["verdict"] = "current"
                block["reason"] = (
                    "no part differs from the registered projection of packet "
                    f"{packet_id} (PD-8)")
    withdrawn = _authorization_withdrawn(state, epic_id)
    if withdrawn is not None:
        block["verdict"] = "impeded"
        block["reason"] = _withdrawn_reason(withdrawn)
    return block


def _unit_contract_status(state: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """The additive, READ-ONLY `unit_contract` block of the compact view (PD-11).

    It informs the mode (`projection` | `fallback`), the declared baseline, the
    live digest, the verdict, the parts that differ and the reason, and writes
    nothing (state byte-identical, no projection, no journal).
    """
    feature_id = state.get("active_feature")
    if not isinstance(feature_id, str) or not feature_id:
        return {
            "mode": "fallback", "unit": None, "registered": None, "live": None,
            "verdict": None, "changed_parts": [],
            "reason": "no active feature to project a unit contract",
        }
    epic_id = state.get("active_epic")
    if not isinstance(epic_id, str) or not epic_id:
        return {
            "mode": "fallback", "unit": feature_id, "registered": None,
            "live": None, "verdict": None, "changed_parts": [],
            "reason": "no active epic: the architect contract is the legacy path",
        }
    return _unit_contract_verdict(state, project_root, feature_id, epic_id)


def _impact_records_in(document: Any) -> list[dict[str, Any]]:
    """Every impact record of a journal document, preserving order.

    A record is a dict carrying the digest pair (`contract_sha256_old` and
    `contract_sha256_new`); a journal is a single record or a collection of
    them (the shape reuses `.superseded.json`).
    """
    records: list[dict[str, Any]] = []
    if isinstance(document, dict):
        if "contract_sha256_old" in document and "contract_sha256_new" in document:
            return [document]
        for value in document.values():
            records.extend(_impact_records_in(value))
    elif isinstance(document, list):
        for value in document:
            records.extend(_impact_records_in(value))
    return records


def _write_impact_record(packet_dir: Path, record: dict[str, Any]) -> None:
    """Write the durable impact record, IDEMPOTENT by the digest pair (PD-9).

    A record whose `(contract_sha256_old, contract_sha256_new)` pair is already
    present is NOT duplicated: running the verdict twice with the same pair
    leaves the journal bytes identical. A distinct pair appends a new record
    without overwriting the previous ones. It is a NEW file in the baseline
    packet's directory (INV-3), never an approval (INV-1).
    """
    path = packet_dir / IMPACT_JOURNAL_NAME
    records: list[dict[str, Any]] = []
    if path.is_file():
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise PolicyError(
                f"impact journal not readable: {IMPACT_JOURNAL_NAME} ({exc})") from exc
        records = _impact_records_in(document)
    pair = (record["contract_sha256_old"], record["contract_sha256_new"])
    if any((item.get("contract_sha256_old"), item.get("contract_sha256_new")) == pair
           for item in records):
        return
    records.append(record)
    try:
        payload = (json.dumps({"schema_version": 1, "impact": records},
                              ensure_ascii=False, indent=2, sort_keys=True)
                   + "\n").encode("utf-8")
    except (UnicodeError, ValueError) as exc:
        raise PolicyError(f"cannot serialize impact record: {exc}") from exc
    try:
        packet_dir.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_bytes(payload)
        os.replace(temporary, path)
    except OSError as exc:
        raise PolicyError(f"cannot write impact record: {IMPACT_JOURNAL_NAME} ({exc})") from exc


def _format_unit_contract_verdict(block: dict[str, Any]) -> str:
    """The verdict emitted by `validate-unit-contract` (stdout, PD-9/PD-11)."""
    registered = block.get("registered")
    registered_line = ("none" if not registered else
                       f"{registered.get('packet_id')} {registered.get('sha256')}")
    live = block.get("live")
    live_line = "none" if not live else str(live.get("sha256"))
    parts = ", ".join(block.get("changed_parts") or []) or "none"
    return "\n".join([
        f"verdict: {block.get('verdict')}",
        f"unit: {block.get('unit')}",
        f"mode: {block.get('mode')}",
        f"registered: {registered_line}",
        f"live: {live_line}",
        f"changed_parts: {parts}",
        f"reason: {block.get('reason')}",
    ]) + "\n"


def validate_unit_contract(args: argparse.Namespace, project_root: Path) -> str:
    """The READ-ONLY verdict operation (PD-7..PD-11).

    It regenerates the live projection and compares it, part by part, with the
    baseline; `current`/`impact` return rc=0 and `impeded` (authorization
    withdrawn) fails closed with rc=2 and no effects. Only in the `impact` case
    it writes its durable, idempotent impact record; it never writes the state
    (the orchestrator records the reconciliation in `stage_history.note`).
    """
    state = _load_json(project_root / "docs" / ".cdad-state.json", "project state")
    feature_id = state.get("active_feature")
    epic_id = state.get("active_epic")
    if (not isinstance(feature_id, str) or not feature_id
            or not isinstance(epic_id, str) or not epic_id):
        return _format_unit_contract_verdict({
            "mode": "fallback", "unit": feature_id, "registered": None,
            "live": None, "verdict": "current", "changed_parts": [],
            "reason": "no active unit: nothing to compare (PD-7)",
        })
    withdrawn = _authorization_withdrawn(state, epic_id)
    if withdrawn is not None:
        raise PolicyError(f"impeded: {_withdrawn_reason(withdrawn)}")
    block = _unit_contract_verdict(state, project_root, feature_id, epic_id)
    if block.get("verdict") == "impact":
        registered = block.get("registered") or {}
        packet_id = registered.get("packet_id")
        if not packet_id:
            raise PolicyError(
                "impact verdict without a declared baseline packet: nothing to record")
        _write_impact_record(
            project_root / ".cdad" / "packets" / packet_id,
            {
                "reason": block.get("reason") or "unit contract changed (PD-9)",
                "contract_sha256_old": registered.get("sha256"),
                "contract_sha256_new": (block.get("live") or {}).get("sha256"),
                "changed_parts": list(block.get("changed_parts") or []),
            })
    return _format_unit_contract_verdict(block)


def _publish_generation(
    *,
    project_root: Path,
    execution_document: dict[str, Any],
    execution: dict[str, Any],
    write_context: bool,
    request: dict[str, Any],
    new_state: dict[str, Any],
    packet: bytes,
    packet_id: str,
    out_dir: Path,
    extra_writes: list[tuple[Path, bytes]] | None = None,
) -> None:
    """Publish one prepared packet generation transactionally (PD-11).

    Reused by `prepare` and `--replace-packet`. Every artifact (context,
    request, packet, derived OpenCode agents, extra durable records such as
    `.superseded.json`, and the state binding) is staged and committed
    atomically: a death before the final state rename never leaves a
    despachable packet, and an error leaves the previous generation intact
    (INV-1/INV-3/INV-5).
    """
    state_path = project_root / "docs" / ".cdad-state.json"
    _ensure_policy_reconciled(project_root, execution_document)
    # PD-16 (§2.9/INV-3): a declared temporary must be ignored by Git, verified
    # read-only before anything is staged. Fails closed, naming both exits.
    _require_ignored_temporary_scope(request.get("write_scope") or [], project_root)
    # I9: the project-local OpenCode agents derive from the installed sources
    # and the accepted policy. They are computed BEFORE the transaction so a
    # hand-modified derived agent fails loudly without any write; the
    # payloads are then published inside the same transaction and lock.
    derived_spec = None
    if (execution_document.get("schema_version") == V2_SCHEMA_VERSION
            and _policy_present(project_root)):
        derived_spec = _build_derived_payloads(project_root, execution_document)
        if derived_spec is None:
            # R9 (PD-8): policy present but no installed OpenCode agents to
            # derive from. A project may use Claude Code only: warn, do not
            # fail (rc 0), and publish no derivatives.
            print(
                "CDAD prepare: OpenCode agents source directory not found; "
                "derived agents were not published without a source "
                f"directory ({DERIVED_AGENTS_ENV})",
                file=sys.stderr,
            )
    try:
        request_bytes = (json.dumps(request, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        state_bytes = (json.dumps(new_state, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        context_bytes = (None if not write_context else
                         (json.dumps(execution_document, ensure_ascii=False, indent=2,
                                     sort_keys=True) + "\n").encode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise PolicyError(f"cannot serialize prepared packet: {exc}") from exc

    packet_dir = out_dir / packet_id
    context_dir = project_root / EXECUTIONS_DIR / execution["id"] if write_context else None
    state_tmp = state_path.with_name(state_path.name + ".tmp")

    stage_dir = project_root / TXN_DIRNAME / packet_id
    stage_created = not stage_dir.exists()
    created_dirs: list[Path] = []
    if stage_created:
        created_dirs = _create_dirs_tracked(stage_dir)
    # A single register of the artifacts this transaction wrote (F3): the
    # rollback removes exactly these files, never a whole directory that
    # could hold a foreign entry.
    owned_files: list[Path] = []
    derived_committed: list[Path] = []
    extra_committed: list[Path] = []
    context_committed: Path | None = None
    context_dir_created = False
    packet_dir_created = False
    try:
        # The manifest names this staging directory as OURS, so recovery
        # only ever cleans directories this mechanism created (A-4).
        stage_manifest = stage_dir / TXN_MANIFEST
        stage_manifest.write_bytes(b"cdad transaction\n")
        owned_files.append(stage_manifest)
        context_stage = context_dir / "execution.json" if context_dir is not None else None
        stage_context = stage_dir / "execution.json"
        stage_request = stage_dir / "REQUEST.json"
        stage_packet = stage_dir / "PACKET.md"
        stage_state = stage_dir / "state.json"
        if context_stage is not None:
            stage_context.write_bytes(context_bytes)
            owned_files.append(stage_context)
        stage_request.write_bytes(request_bytes)
        stage_packet.write_bytes(packet)
        stage_state.write_bytes(state_bytes)
        owned_files.extend([stage_request, stage_packet, stage_state])
        derived_stage = stage_dir / DERIVED_STAGE_DIRNAME
        if derived_spec is not None:
            created_dirs.extend(_create_dirs_tracked(derived_stage))
            for name, payload in derived_spec[1]:
                (derived_stage / name).write_bytes(payload)
                owned_files.append(derived_stage / name)
            (derived_stage / DERIVED_MANIFEST_NAME).write_bytes(derived_spec[2])
            owned_files.append(derived_stage / DERIVED_MANIFEST_NAME)
        # Extra durable records (e.g. `.superseded.json`, the unit projection)
        # are staged INSIDE the transaction directory and moved into place during
        # the commit, so a target inside a packet directory this generation is
        # about to create is published atomically (PD-11/INV-3).
        extra_temps: list[tuple[Path, Path]] = []
        for position, (target, payload) in enumerate(extra_writes or []):
            extra_tmp = stage_dir / f"extra-{position:03d}"
            extra_tmp.write_bytes(payload)
            extra_temps.append((extra_tmp, target))
            owned_files.append(extra_tmp)

        # Commit: context, then (after the declared interruption points) the
        # packet and executable files (atomic renames), then the state
        # binding, which is the authoritative switch. Only after that final
        # rename is the generation published; a death before it still
        # leaves an unpublished on-disk packet directory that `prepare`
        # reclaims on the next run. No packet is ever printed first.
        if context_stage is not None:
            if not context_stage.parent.exists():
                created_dirs.extend(_create_dirs_tracked(context_stage.parent))
                context_dir_created = True
            # Atomic: never overwrite an existing context (publication resumes
            # from it after an interrupted first bootstrap).
            if not context_stage.exists():
                os.replace(stage_context, context_stage)
                context_committed = context_stage
        _fail_point("context-written")
        if not packet_dir.exists():
            created_dirs.extend(_create_dirs_tracked(packet_dir))
            packet_dir_created = True
        _fail_point("packet-written")
        os.replace(stage_state, state_tmp)
        _fail_point("before-state")
        os.replace(stage_request, packet_dir / "REQUEST.json")
        os.replace(stage_packet, packet_dir / "PACKET.md")
        for extra_tmp, target in extra_temps:
            # INV-3/PD-4: an extra durable record may live in a packet
            # directory this generation does not itself create (e.g. the unit
            # projection published on the canonical path while the packet goes
            # to a custom --out-dir). Create its parent INSIDE the transaction,
            # tracked for rollback, and publish atomically.
            if not target.parent.exists():
                created_dirs.extend(_create_dirs_tracked(target.parent))
            os.replace(extra_tmp, target)
            extra_committed.append(target)
        if derived_spec is not None:
            derived_dir = derived_spec[0]
            if not derived_dir.exists():
                created_dirs.extend(_create_dirs_tracked(derived_dir))
            for name, _payload in derived_spec[1]:
                os.replace(derived_stage / name, derived_dir / name)
                derived_committed.append(derived_dir / name)
            os.replace(derived_stage / DERIVED_MANIFEST_NAME,
                       derived_dir / DERIVED_MANIFEST_NAME)
            derived_committed.append(derived_dir / DERIVED_MANIFEST_NAME)
        os.replace(state_tmp, state_path)
        _fail_point("after-state")
        # R2 (PD-8/PD-5): retire derivatives whose source was removed from
        # the origin — only the names the PREVIOUS manifest declared; foreign
        # files are never touched. The generation is already published.
        if derived_spec is not None:
            for name in derived_spec[3]:
                try:
                    (derived_spec[0] / name).unlink(missing_ok=True)
                except OSError:
                    pass
        # The publication is complete: remove the transaction-owned files.
        # A staging directory THIS invocation created is dropped entirely
        # (no leftover artifact); a pre-existing one (recovery of an
        # interrupted publication) is kept as its journal entry, so its
        # directory — and any foreign file in it — survives (A-4).
        cleanup_stale_transactions(project_root)
        if stage_created:
            try:
                stage_manifest.unlink(missing_ok=True)
            except OSError:
                pass
            try:
                stage_dir.rmdir()
            except OSError:
                pass
            try:
                (project_root / TXN_DIRNAME).rmdir()
            except OSError:
                pass
        _remove_empty_dirs(created_dirs)
    except OSError as exc:
        # Roll back exactly the files this transaction owns, then the empty
        # directories this operation created. A foreign entry inside any of
        # them is preserved (F3).
        for path in owned_files:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        for path in derived_committed + extra_committed:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        if context_committed is not None:
            try:
                context_committed.unlink(missing_ok=True)
            except OSError:
                pass
        if context_dir_created and context_dir is not None:
            try:
                context_dir.rmdir()
            except OSError:
                pass
        if packet_dir_created and packet_dir.is_dir():
            # Only remove the packet dir when it holds nothing but this
            # transaction's own files; a foreign entry keeps it (F3).
            remaining = [p.name for p in packet_dir.iterdir()
                         if p.name not in {"REQUEST.json", "PACKET.md"}]
            if not remaining:
                _remove_owned_files(packet_dir)
                try:
                    packet_dir.rmdir()
                except OSError:
                    pass
        _remove_empty_dirs(created_dirs)
        raise PolicyError(f"cannot write prepared packet: {exc}") from exc


def _packet_agent(role: str, state: dict[str, Any]) -> str:
    """PD-7 (006-005 U1c, §2.7/D-13): the agent that travels in the package.

    The agent is resolved from the packet's role plus the execution stack
    declared by the project state (`docs/.cdad-state.json.stack`): with a
    non-empty stack it is `cdad-<role>-<stack>` (e.g. `cdad-architect-odoo`),
    without it `cdad-<role>`. It is the field the module translates into its
    invocation and against which the correlation compares (§2.3), so it stays
    an ADDITIVE declared property of the request: it never enters the render.
    """
    stack = state.get("stack")
    if isinstance(stack, str) and stack:
        return f"cdad-{role}-{stack}"
    return f"cdad-{role}"


def prepare(args: argparse.Namespace, project_root: Path) -> bytes:
    """Build request, packet and state binding; write all of them or nothing."""
    if not args.role or not args.substage or not args.objective:
        raise PolicyError("prepare requires --role, --substage and --objective")
    role, substage = args.role, args.substage
    if role not in ROLE_SUBSTAGES or substage not in ROLE_SUBSTAGES[role]:
        raise PolicyError("role/substage pair is invalid")

    # PD-11/I5 + F2: exclusion covers resolution, identity reservation and the
    # whole publication. State, execution and the packet id are read/reserved
    # INSIDE the lock, so a concurrent writer consumes no stale decision and
    # never overwrites a published packet.
    with _ProjectLock(project_root):
        # Recover from an interrupted publication before reading state: drop the
        # transaction-owned files left under .cdad/.txn, never a foreign entry.
        cleanup_stale_transactions(project_root)
        state_path = project_root / "docs" / ".cdad-state.json"
        state = _load_json(state_path, "project state")

        execution_document, execution, write_context = _select_execution(args, project_root, state)
        if execution_document.get("schema_version") == V2_SCHEMA_VERSION:
            active = state.get("active_packet")
            if isinstance(active, dict) and active.get("status") in ACTIVE_PACKET_STATUSES:
                # PD-11/I5 recovery: if the bound context is coherent and the active
                # packet is not published (an interrupted publication, e.g. at the
                # packet-written point), discard that half-written reading and
                # prepare a coherent generation. A published pending packet still
                # blocks replacement (PD-4).
                pending_dir = project_root / ".cdad" / "packets" / active["id"]
                if pending_dir.is_dir():
                    published = any(
                        DOC.is_file() for DOC in (pending_dir / "REQUEST.json", pending_dir / "PACKET.md"))
                else:
                    published = False
                if published:
                    raise PolicyError(
                        f"active packet {active.get('id')!r} is {active.get('status')!r}: complete or "
                        f"fail it before preparing a new packet (PD-4)"
                    )
                state = dict(state)
                state["active_packet"] = None
                state["execution"] = None
        if FLAT_NAME.fullmatch(execution["feature_id"]) is None or ".." in execution["feature_id"]:
            raise PolicyError("execution.feature_id must be a flat name ([A-Za-z0-9._-], no '..')")

        contract_kind, contract_path = _contract_for(role, execution)
        contract_object: dict[str, Any] = {
            "kind": contract_kind, "path": contract_path, "sha256": None, "commit": None,
        }
        # PD-1 (004-003 T1): `prepare` may render a reviewer packet whose
        # contract object is a DECLARED draft plan (kind `draft-plan`, its own
        # version + path). Only the explicit triple selects this surface; the
        # honest path resolves the contract from `--contract-path` exactly like
        # the approved paths, so a forge (an `approved-*` kind over a declared
        # draft) is rejected by validate_request before any publication.
        is_declared_draft = False
        if args.contract_kind or args.contract_path or args.plan_version:
            if not (args.contract_kind and args.contract_path and args.plan_version):
                raise PolicyError(
                    "a declared draft contract requires --contract-kind --contract-path "
                    "--plan-version together")
            contract_kind = args.contract_kind
            contract_path = args.contract_path
            if contract_kind not in VALID_CONTRACT_KINDS:
                raise PolicyError(f"unknown contract kind: {contract_kind!r}")
            contract_object["plan_version"] = args.plan_version
            is_declared_draft = contract_kind == "draft-plan"
            # F1 (PD-1 + §3 invariant 4): a declared draft plan is a REVIEW
            # object; it never authorizes implementation. Reject the draft
            # surface for any role other than the reviewer so a draft contract
            # cannot be dispatched with an implementation write scope.
            if is_declared_draft and role != "reviewer":
                raise PolicyError(
                    f"draft-plan contract is reviewer-only: role {role!r} cannot "
                    "review a declared draft plan (PD-1, invariant 4)")
        # 006-006 U1 (R-2): the declared form and the companion identity belong
        # to the declared-draft surface. Over any other contract they are a
        # forgery and are rejected before anything is published.
        if (args.object_kind or args.spec_path or args.spec_version) and not is_declared_draft:
            raise PolicyError(
                "the declared object form and its companion belong to a draft-plan "
                "contract: --object-kind --spec-path --spec-version are not "
                "admissible over an approved contract (PD-1, R-2)")
        # 006-006 U1 (R-3/R-4): the form of the reviewed object; absent means
        # `plan` (the fail-closed direction).
        object_form = _declared_object_form(args.object_kind, "--object-kind")
        if args.object_kind is not None:
            contract_object["object_kind"] = args.object_kind
        # 006-006 U1 (R-5/R-6/R-7/R-8): the companion identity. The three keys
        # appear together or not at all; the companion is the spec and only
        # exists over a plan-form principal; its digest is COMPUTED from the
        # file's bytes (never asserted from outside).
        if args.spec_path is not None or args.spec_version is not None:
            missing_companion = [key for key, value in (
                ("spec_path", args.spec_path), ("spec_version", args.spec_version))
                if value is None]
            if missing_companion:
                raise PolicyError(
                    "the companion spec identity is all-or-none: missing "
                    + ", ".join(missing_companion) + " (R-6)")
            if object_form != "plan":
                raise PolicyError(
                    "the companion document is the spec and only exists over a "
                    "plan-form principal: declare --object-kind plan (R-7, R-8)")
            companion_file = _project_path(project_root, args.spec_path, "spec.path")
            if not companion_file.is_file():
                raise PolicyError(
                    f"the companion spec document does not exist: {args.spec_path}")
            companion_digest = hashlib.sha256(
                _read_bytes(companion_file, "spec")).hexdigest()
            contract_object["spec_path"] = args.spec_path
            contract_object["spec_sha256"] = companion_digest
            contract_object["spec_version"] = args.spec_version
        contract_object["kind"] = contract_kind
        contract_object["path"] = contract_path
        contract_file = _project_path(project_root, contract_path, "contract.path")
        # 005-001 T4 (PD-3/PD-17/PD-12): the role-aware approval is enforced in
        # `validate_request`, but it needs the verified contract bytes. When the
        # contract file is absent (PD-17 creates the spec only after the blocked
        # attempt) the read below would raise a generic error before the approval
        # check ever runs; report the actionable approval gap instead.
        if not contract_file.is_file():
            _reject_absent_contract_without_approval(role, contract_object, state, execution)
        contract_bytes = _read_bytes(contract_file, "contract")
        digest = hashlib.sha256(contract_bytes).hexdigest()
        contract_object["sha256"] = digest
        # AC-3 (004-003 T3) + PD-8 (T4): a declared draft plan is subjected to
        # the mechanical producer/consumer and dependency checks AND to the
        # mandatory per-task validation plan BEFORE anything is published.
        # `prepare` is the only producer of packets (invariant 1), so it must
        # not publish a packet whose plan object fails these checks. PD-8 makes
        # the ```plan-tasks block mandatory: a plan without it (or with a
        # malformed fence) fails loud instead of being published with its
        # checks skipped (F1).
        # 006-006 U1 (R-4, §2.2): the plan checks apply ONLY to a principal
        # whose form is `plan`. A spec is reviewed without artificial tasks:
        # no `plan-tasks` block is demanded of it, and none is injected into it.
        if is_declared_draft and object_form == "plan":
            try:
                declared_tasks, validation_strategy = _plan_tasks_from_contract(contract_bytes)
            except PolicyError as exc:
                # The declared form was NOT declared: name the flag that declares
                # it. The rejection itself does not change (fail-closed).
                if args.object_kind is None:
                    raise PolicyError(
                        f"{exc} — if the reviewed object is a spec, declare its form "
                        "with --object-kind spec") from exc
                raise
            _check_plan_tasks(declared_tasks)
            _check_plan_validation_plan(declared_tasks, validation_strategy)
        out_dir = _cwd_path(args.out_dir) if args.out_dir else project_root / ".cdad" / "packets"
        packet_id = _next_packet_id(out_dir, f"{execution['feature_id']}-{role}-{substage}")
        # 005-013 T1 (PD-1..PD-5): the architect's contract is a projection of the
        # unit located STRUCTURALLY in the epic plan, published ONCE with this
        # packet and pinned by its digest. When the unit cannot be located without
        # ambiguity, the contract stays the approved epic plan (PD-2, declared
        # fallback, rc=0) and the reason is diagnosed on stderr (stdout keeps
        # being the PACKET.md byte for byte).
        projection_bytes: bytes | None = None
        projection_target: Path | None = None
        if role == "architect" and not is_declared_draft:
            anchors = _declared_plan_anchors()
            located, locator_reason = _locate_unit(
                contract_bytes.decode("utf-8", errors="replace"),
                execution["feature_id"])
            if located is None:
                print("CDAD prepare: " + _unit_contract_fallback_reason(
                    execution["feature_id"], contract_path, locator_reason),
                    file=sys.stderr)
            else:
                approving_entry = _approved_epic_plan_entry(
                    state, execution.get("epic_id")) or {}
                projection_bytes = _build_unit_projection(
                    feature_id=execution["feature_id"],
                    plan_rel=contract_path,
                    plan_bytes=contract_bytes,
                    approved_by=approving_entry.get("approved_by") or "",
                    policy_sha256=execution.get("policy_sha256") or "",
                    located=located,
                    anchors=anchors,
                )
                contract_kind = UNIT_CONTRACT_KIND
                contract_path = (Path(".cdad") / "packets" / packet_id
                                 / UNIT_PROJECTION_NAME).as_posix()
                digest = hashlib.sha256(projection_bytes).hexdigest()
                contract_object["kind"] = contract_kind
                contract_object["path"] = contract_path
                contract_object["sha256"] = digest
                projection_target = project_root / contract_path
                # INV-3/PD-4 (B1 of the 005-013 review): the projection is
                # published ONCE. When the minted packet id already has a
                # published projection on the canonical path — e.g. a second
                # generation with a custom --out-dir whose numbering collides
                # with an existing packet — fail CLOSED, naming the conflicting
                # packet, BEFORE the publication transaction stages or moves
                # anything. A published projection is never rewritten: no blind
                # `os.replace` over an existing target.
                if projection_target.exists():
                    raise PolicyError(
                        f"unit projection for packet {projection_target.parent.name!r} "
                        f"is already published at {projection_target.as_posix()!r}: "
                        "refusing to rewrite a published projection (INV-3/PD-4; "
                        "a new generation for the unit needs a new packet id)"
                    )
        read_default, write_default = _default_scopes(role, contract_path, execution_document["path_policy"])
        request = {
            "schema_version": 1,
            "packet_id": packet_id,
            "execution_id": execution["id"],
            "feature_id": execution["feature_id"],
            "role": role,
            "substage": substage,
            # PD-7 (006-005 U1c, §2.7/D-13): the agent travels in the package.
            # Declared OPTIONAL property (validate_request admits it, the render
            # ignores it): a package published before this feature stays valid.
            "agent": _packet_agent(role, state),
            "objective": args.objective,
            "contract": contract_object,
            # 006-006 U1 (R-9): ONE input per fixed document, principal first
            # and companion second, and each entry's purpose names the FORM of
            # its document.
            "inputs": ([{"path": contract_path,
                         "purpose": "draft spec for review" if object_form == "spec"
                         else "draft plan for review"}]
                       if is_declared_draft else
                       [{"path": contract_path, "purpose": "approved contract"}])
                      + ([{"path": contract_object["spec_path"],
                          "purpose": "draft spec for review"}]
                         if is_declared_draft and "spec_path" in contract_object else [])
                      + [_cli_input(raw) for raw in args.input],
            "read_scope": [_cli_scope(raw, project_root) for raw in args.read_scope] or read_default,
            "write_scope": [_cli_scope(raw, project_root) for raw in args.write_scope] or write_default,
            "invariants": DEFAULT_INVARIANTS.get(role, []) + args.invariant,
            "expected_output": args.expected_output or DEFAULT_EXPECTED_OUTPUT,
            "evidence_required": args.evidence or DEFAULT_EVIDENCE,
        }
        # PD-10/INV-4: the declared plan task is an ADDITIVE optional field; when
        # absent the request and the packet are byte-identical to today's render.
        if args.plan_task:
            request["plan_task"] = args.plan_task
        binding_fields = (V2_BINDING_FIELDS if execution_document.get("schema_version") == V2_SCHEMA_VERSION
                          else BINDING_FIELDS)
        new_state = dict(state)
        new_state["execution"] = {field: execution[field] for field in binding_fields}
        new_state["active_packet"] = {
            "id": packet_id, "role": role, "substage": substage, "status": "prepared",
            "packet_version": 1, "contract_kind": contract_kind, "contract_sha256": digest,
        }
        validate_request(request, execution_document, new_state, project_root,
                         contract_bytes_override=projection_bytes)
        packet = render_packet(request, execution_document, project_root).encode("utf-8")

        # The identity is reserved and the lock is held: the declared point is
        # here (I5b, F2). A second writer is rejected while we are paused.
        _fail_point("reserved-id")
        _pause_point("reserved-id")

        # PD-11: the publication is transactional and shared with
        # `--replace-packet`; see `_publish_generation`. Every artifact
        # (context, request, packet, derived OpenCode agents, the unit
        # projection and the state) is staged and committed atomically, so a
        # death before the commit never leaves a despachable packet.
        _publish_generation(
            project_root=project_root,
            execution_document=execution_document,
            execution=execution,
            write_context=write_context,
            request=request,
            new_state=new_state,
            packet=packet,
            packet_id=packet_id,
            out_dir=out_dir,
            extra_writes=([(projection_target, projection_bytes)]
                          if projection_target is not None and projection_bytes is not None
                          else None),
        )
        return packet


# ---------------------------------------------------------------- 005-007 T3
# PD-7: open the next queued unit of the approved plan with ONE operation of the
# CLI, so the state is never edited by hand. Selection trusts the plan order
# (`epic_features` order is the authority); the effect is atomic, under the same
# project lock and after the same vigency/coherence validation the other
# consumers run; authority, policy and version are never touched. The execution
# reuses the existing v2 bootstrap (`_bootstrap_v2_execution`) instead of
# duplicating the preparation path.

_QUEUED_UNIT_STATUS = "queued"
_DONE_UNIT_STATUS = "done"


def _select_open_unit_entry(features: list[Any],
                            requested: str | None) -> dict[str, Any]:
    """The entry to open: the requested `--feature` (must exist and be queued),
    or the FIRST `queued` entry (the plan order is the authority)."""
    if requested is not None:
        matching = [item for item in features
                    if isinstance(item, dict) and item.get("id") == requested]
        if not matching:
            raise PolicyError(
                f"unknown unit {requested!r}: --feature requires an existing "
                f"epic_features entry with status {_QUEUED_UNIT_STATUS!r}")
        entry = matching[0]
        if entry.get("status") != _QUEUED_UNIT_STATUS:
            raise PolicyError(
                f"unit {requested!r} is not {_QUEUED_UNIT_STATUS!r} (status "
                f"{entry.get('status')!r}): open-unit only opens a "
                f"{_QUEUED_UNIT_STATUS!r} unit")
        return entry
    first = next((item for item in features
                  if isinstance(item, dict)
                  and item.get("status") == _QUEUED_UNIT_STATUS), None)
    if first is None:
        raise PolicyError(
            f"no {_QUEUED_UNIT_STATUS!r} unit in epic_features: there is "
            f"nothing to open")
    return first


def _check_open_unit_dependencies(entry: dict[str, Any],
                                  features: list[Any]) -> str | None:
    """Obs 2: verify the entry's declared `depends_on`, or return the explicit
    declaration that UNDECLARED dependencies are not verified (the plan order is
    the authority). A declared dependency that is not `done` fails closed."""
    declared = entry.get("depends_on")
    if declared is None or declared == []:
        return None
    if not isinstance(declared, list) or not all(
            isinstance(dep, str) and dep for dep in declared):
        raise PolicyError(
            f"unit {entry.get('id')!r} declares an invalid depends_on: expected "
            f"a list of unit ids")
    done_ids = {item.get("id") for item in features
                if isinstance(item, dict)
                and item.get("status") == _DONE_UNIT_STATUS}
    missing = [dep for dep in declared if dep not in done_ids]
    if missing:
        raise PolicyError(
            f"unit {entry.get('id')!r} depends on units that are not "
            f"{_DONE_UNIT_STATUS!r}: {', '.join(missing)}; open-unit refuses to "
            f"open a unit before its declared dependencies are done")
    return (f"declared dependencies verified as {_DONE_UNIT_STATUS}: "
            + ", ".join(declared))


def open_unit(args: argparse.Namespace, project_root: Path) -> str:
    """PD-7: open the next queued unit; atomic state effect under the lock.

    Requires a legitimate resting state (`active_feature` null and
    `current_stage` idle); with a unit already open it rejects without writing.
    Everything is read and validated before the single atomic publication of the
    execution context and the state binding, so a rejection leaves the project
    untouched.
    """
    with _ProjectLock(project_root):
        cleanup_stale_transactions(project_root)
        state_path = project_root / "docs" / ".cdad-state.json"
        state = _load_json(state_path, "project state")
        # Precondition: the resting coherence the CLI already imposes. A unit
        # already open (or an incoherent state) fails closed, naming the record.
        if not _validate_idle_coherence(state):
            raise PolicyError(
                f"state is not at rest: unit {state.get('active_feature')!r} is "
                f"already open (current_stage {state.get('current_stage')!r}); "
                f"complete or close it before opening the next unit")
        features = state.get("epic_features")
        if not isinstance(features, list):
            raise PolicyError(
                "epic_features record missing: state.epic_features must be a list")
        entry = _select_open_unit_entry(features, args.feature)
        unit_id = entry.get("id")
        dependencies_note = _check_open_unit_dependencies(entry, features)

        opened_at = datetime.now(timezone.utc).isoformat()
        new_features = [
            {**item, "status": "in-progress", "opened_at": opened_at}
            if item is entry else item
            for item in features
        ]
        new_state = dict(state)
        new_state["epic_features"] = new_features
        new_state["active_feature"] = unit_id
        new_state["current_stage"] = "discovery"
        new_state["tdd_substage"] = None
        new_state["active_packet"] = None

        # Reuse the existing v2 bootstrap for the execution. `open-unit` is
        # feature-scoped, so `role=None` resolves the feature spec as the
        # contract; the authority reference follows the active epic's delegation.
        execution_document, execution, _ = _bootstrap_v2_execution(
            argparse.Namespace(role=None), project_root, new_state)
        new_state["execution"] = {
            field: execution[field] for field in V2_BINDING_FIELDS}
        # Conserva validaciones: the same vigency/coherence validation runs
        # before anything is written, so `validate-state` is green afterwards.
        _validate_v2_state(execution_document, new_state, project_root)

        context_path = (project_root / EXECUTIONS_DIR / execution["id"]
                        / "execution.json")
        context_path.parent.mkdir(parents=True, exist_ok=True)
        _publish_owned_atomically([
            (context_path, _serialize_document(execution_document, sorted_keys=True)),
            (state_path, _serialize_document(new_state)),
        ])

    if dependencies_note is None:
        dependencies_note = (
            f"no declared dependencies for {unit_id!r}; the plan order is the "
            f"authority (dependencies not verified)")
    return (f"opened unit {unit_id!r}: active_feature={unit_id} "
            f"current_stage=discovery execution={execution['id']}\n"
            f"{dependencies_note}\n")


# ---------------------------------------------------------------- 005-012 T1
# `register-transition` (`transition-registration-v1`): the CLI operation that
# registers an EXPLICIT orchestrator decision over a transition and applies its
# mechanical effect on the state, through the single writer (lock + atomic
# publication) and the single serialization. Declared surface: spec §2.1;
# additive entry form: §2.2; postconditions: PD-1..PD-4, PD-7, PD-10..PD-12,
# PD-17, PD-18, PD-20. The operation checks evidence, vocabulary and identity;
# it never decides meaning, quality or whether a dispatch must be dispositioned
# (INV-5). T1 declared the MINIMUM usable form (`delivery` and `advance`); T2
# adds the `gate` class over that base (PD-5/PD-6); the remaining classes are
# added by later tasks of the same feature, over this base.
TRANSITION_CLASSES = ("delivery", "advance", "gate", "closure", "late-delivery",
                      "disposition")
# PD-14: the stage-2 approval gate — the only transition whose vigency is
# structural per `(feature, contract_path)` (D-8: `supersedes`).
SPEC_GATE_STAGE = "specification"
# PD-21/D-13: `disposition` carries the CANONICAL label. §2.1 does not accept
# `--stage` for this class: its informative value is `--resolution`, and a free
# label would make the identity key depend on a text without effect.
DISPOSITION_STAGE = "dispatch-disposition"
# PD-13 (2)/D-5: `late-delivery` also carries a CANONICAL label (§2.2/§2.1: the
# class writes `stage: "late-delivery"`); like `disposition` it does not accept
# `--stage`, so its identity key never depends on a free text without effect.
LATE_DELIVERY_STAGE = "late-delivery"
# PD-21: the closed vocabulary of `--resolution` (the declared decision over a
# dispatch that will not come back).
DISPOSITION_RESOLUTIONS = ("abandoned", "superseded")
# PD-7: the closed vocabulary of the operational stage field `--current-stage`.
# Canonical text: skills/cdad-cycle/references/state-detection.md:20-37 (the
# resting value `idle` included; `done` is the closure result, not a stage of
# the cycle — closure lands on `idle`).
VALID_CURRENT_STAGES = {"discovery", "specification", "tdd", "review", "merge", "idle"}
RESULTS_RELDIR = Path(".cdad") / "runtime" / "results"
RECEIPT_FILENAME = "receipt.json"


def _transition_identity_payload(*, execution_id: str, feature_id: str,
                                 transition: str, stage: str,
                                 substage: str | None, packet_id: str | None,
                                 receipt_sha256: str | None,
                                 resolution: str | None, replaced_by: str | None,
                                 postcondition: dict[str, Any] | None,
                                 current_stage: str | None,
                                 artifacts: dict[str, str],
                                 approved_by: str | None,
                                 contract: dict[str, str] | None,
                                 plan: dict[str, str] | None,
                                 closure: dict[str, str] | None,
                                 exemption: dict[str, Any] | None = None
                                 ) -> dict[str, Any]:
    """PD-10 (B2): the canonical payload of the transition identity — the
    declared tuple PLUS the inputs that have an effect on the entry or on the
    state.

    The declared normalization is exact: an absent input is `null` (never
    `""`), only the class that declares an input fills it, the digests are the
    ones the CLI RESOLVED (derived from the bytes or verified against them,
    PD-20 — the value the entry writes, not the one the operator asserted), and
    `artifacts` is a list of `[path, sha256]` pairs SORTED BY PATH, because the
    entry keeps them as a mapping: the order of several `--artifact` has no
    effect and must not change the identity. `note` and `by` stay OUT of the
    payload: they are the annotation of the invocation, prose the CLI never
    interprets nor uses as a control (PD-18/D-8).

    Writing this payload in the entry (`transition_key_payload`, §2.2) makes
    the identity checkable FROM the state, and makes the version boundary
    explicit: an entry WITHOUT it was registered under the previous formula.

    006-006 PD-9 (R-11/R-12/R-13): the owner's exemption enters the identity
    ONLY when the invocation DECLARES it, as ONE conditional block (`exemption`)
    that carries EXACTLY the declared fields (the fields not declared are not
    in it, not as `null`). Without a declared exemption the payload keeps its
    16 keys, so its canonical serialization —and therefore the
    `transition_key`— is byte for byte the one of the previous product: the
    historical identities are preserved and no guarantee of a previous feature
    is amended (D-14)."""
    payload = {
        "execution_id": execution_id,
        "feature_id": feature_id,
        "transition": transition,
        "stage": stage,
        "substage": substage,
        "packet_id": packet_id,
        "receipt_sha256": receipt_sha256,
        "resolution": resolution,
        "replaced_by": replaced_by,
        "postcondition": postcondition,
        "current_stage": current_stage,
        "artifacts": sorted([[path_text, digest]
                             for path_text, digest in artifacts.items()]),
        "approved_by": approved_by,
        "contract": contract,
        "plan": plan,
        "closure": closure,
    }
    if exemption is not None:
        payload["exemption"] = exemption
    return payload


def _transition_key(payload: dict[str, Any]) -> str:
    """PD-10: the content identity of a transition: the sha256 of the canonical
    payload, with the declared serialization — `json.dumps(payload,
    ensure_ascii=False, sort_keys=True, separators=(",", ":"))` over UTF-8
    bytes.

    The same effect inputs always produce the same key, so an identical
    repetition is recognisable without depending on the head of
    `stage_history` (PD-11); and two invocations that differ in ANY effect
    input produce different keys, so a distinct transition is registered as a
    new entry instead of being swallowed as a silent no-op (PD-10/PD-12, B2)."""
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _transition_noop_message(transition: str, stage: str, key: str) -> str:
    """PD-11: an identical repetition is a successful no-op; the state is not
    written, so it stays byte for byte identical. The no-op is NOT silent (B2):
    it names the existing entry (the identity key) and DECLARES that the
    annotation of THIS invocation was not written — `note`/`by` are outside the
    payload, so they are the only difference an identical repetition admits, and
    they are never an effect (PD-10/PD-18)."""
    return (
        f"transition already registered: {transition} stage {stage!r} "
        f"({key}); no-op, no effects\n"
        f"no-op detail: the entry named above by its transition_key "
        f"already registered this transition; the annotation of this "
        f"invocation (--note/--by) is outside the identity payload and "
        f"was NOT written (PD-11)\n")


def _registered_transition(state: dict[str, Any], key: str) -> dict[str, Any] | None:
    """The entry that already registered this transition, if any (PD-11). The
    lookup scans the whole history on purpose: the no-op is independent of the
    head and of continuity."""
    history = state.get("stage_history")
    if not isinstance(history, list):
        return None
    for entry in history:
        if isinstance(entry, dict) and entry.get("transition_key") == key:
            return entry
    return None


def _vigente_spec_approval(state: dict[str, Any], feature_id: str,
                            contract_path: str, contract_sha256: str
                            ) -> dict[str, Any] | None:
    """The VIGENTE `specification` approval that competes with a new one
    (PD-14/D-8): the entries the reader considers vigente
    (`_approved_spec_entries`, which ignores the superseded ones) whose pin
    NAMES the current bytes of the contract — the same selection the PD-14
    rule already consumes, never a second declaration of it.

    006-006 PD-9 (R-14): this selection is what QUALIFIES the no-op branch —
    the replay of the entry this function returns is a no-op; an invocation
    that collides with a HISTORICAL entry while this one competes is not."""
    for item in _approved_spec_entries(state, feature_id):
        if (item.get("contract_path") == contract_path
                and item.get("contract_sha256") == contract_sha256):
            return item
    return None


def _transition_collision_message(feature_id: str, contract_path: str,
                                  key: str, vigente_key: str) -> str:
    """006-006 PD-9 (R-14(b)/D-15): the EXPLICIT rejection of an invocation
    that collides with a HISTORICAL entry while a VIGENTE approval competes.

    The rejection NAMES the colliding key (and that it is NOT the vigente one),
    the key of the vigente one and the TWO legitimate exits: register the
    change with a distinguishable value, or reconcile the history. It happens
    BEFORE any write, so the state stays byte for byte identical (INV-7)."""
    return (
        f"state incoherent: this invocation collides with the historical "
        f"transition_key {key!r}, which is NOT the vigente `specification` "
        f"approval of feature {feature_id!r} for the contract "
        f"{contract_path!r} (the vigente one is {vigente_key!r}); that "
        f"colliding key is already in the set of superseded keys, so a new "
        f"entry with it would stay inert for the vigency and the change "
        f"would be lost in silence. Two legitimate exits: (i) register the "
        f"change with a DISTINGUISHABLE value — an input that enters the "
        f"identity and differs from the historical one (cite the owner's "
        f"decision as evidence with `--artifact <path>`, or approve different "
        f"bytes of the contract) — so that the new entry has its own key and "
        f"becomes the vigente one; (ii) RECONCILE the history: withdraw or "
        f"re-approve the current approval so that the intended payload is the "
        f"one that becomes vigente (PD-9/R-14/D-15)")


def _resolve_evidence_digest(raw: str, label: str) -> tuple[str, str]:
    """PD-20: read `<path>[=<sha256>]` and DERIVE the digest from the current
    bytes, unless a 64-hex assertion follows the LAST `=`. Here the CLI only
    READS the cited file: a missing path or a divergent assertion fails closed
    with `evidence missing` and no effects."""
    path_text, _, asserted = raw.rpartition("=")
    if not path_text or re.fullmatch(r"[0-9a-f]{64}", asserted) is None:
        path_text, asserted = raw, None
    path = _cwd_path(path_text)
    if not path.is_file():
        raise PolicyError(
            f"evidence missing: {label} not found at {path_text!r}; the digest cannot be "
            f"derived from absent bytes. Cite an existing path, or register the transition "
            f"once the artifact exists")
    actual = hashlib.sha256(_read_bytes(path, label)).hexdigest()
    if asserted is not None and asserted != actual:
        raise PolicyError(
            f"evidence missing: the asserted {label} digest {asserted} does not match the "
            f"current bytes {actual} of {path_text!r}; the CLI derives the digest from the "
            f"bytes it reads, so omit the assertion or cite exactly the bytes reviewed")
    return path_text, actual


def _durable_receipt(project_root: Path, execution_id: str, packet_id: str,
                     asserted: str | None) -> tuple[str | None, str]:
    """PD-20 for the cited packet's durable receipt: verify an asserted digest
    against the current bytes of `receipt.json`, or derive it. Returns
    `(digest or None when the receipt is absent, project-relative receipt path)`."""
    relative = (RESULTS_RELDIR / execution_id / packet_id / RECEIPT_FILENAME).as_posix()
    path = project_root / relative
    if not path.is_file():
        if asserted is not None:
            raise PolicyError(
                f"evidence missing: packet {packet_id} has no durable receipt at {relative}, "
                f"so the asserted digest {asserted} cannot be verified against bytes. Receive "
                f"the delivery by the normal route (`cdad_result.py receive`) before "
                f"registering it")
        return None, relative
    actual = hashlib.sha256(_read_bytes(path, "durable receipt")).hexdigest()
    if asserted is not None and asserted != actual:
        raise PolicyError(
            f"evidence missing: the asserted receipt digest {asserted} for packet {packet_id} "
            f"does not match the current bytes {actual} of {relative}; omit --receipt to let "
            f"the CLI derive the digest, or cite exactly the bytes reviewed")
    return actual, relative


def _packet_is_dispatched(project_root: Path, execution_id: str, packet_id: str) -> bool:
    """Whether the cited packet has a dispatch record in the active execution —
    the derived notion of «dispatched» the closure also uses (PD-8(a))."""
    base = project_root / EXECUTIONS_DIR / execution_id / DISPATCHES_DIRNAME
    if not base.is_dir():
        return False
    try:
        candidates = list(base.iterdir())
    except OSError:
        return False
    for path in candidates:
        if not path.is_file() or path.suffix != ".json":
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(record, dict) and record.get("packet_id") == packet_id:
            return True
    return False


def _dispatched_packet_ids(project_root: Path, execution_id: str) -> list[str]:
    """PD-8(a): the packets of the active execution that have a dispatch record.

    Repeated dispatches of the SAME packet (two attempts of one packet) count
    ONCE: the required deliveries are the packets, not the attempts."""
    base = project_root / EXECUTIONS_DIR / execution_id / DISPATCHES_DIRNAME
    if not base.is_dir():
        return []
    try:
        candidates = sorted(base.iterdir())
    except OSError:
        return []
    packet_ids: list[str] = []
    for path in candidates:
        if not path.is_file() or path.suffix != ".json":
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        packet_id = record.get("packet_id") if isinstance(record, dict) else None
        if isinstance(packet_id, str) and packet_id and packet_id not in packet_ids:
            packet_ids.append(packet_id)
    return packet_ids


def _packet_has_disposition(state: dict[str, Any], packet_id: str) -> bool:
    """PD-8(a)/PD-21: whether a registered disposition NAMES the packet.

    A dispatched packet resolves its delivery with a durable receipt OR with
    the orchestrator's disposition; the closure accepts either (the disposition
    is a decision transcribed to structure, PD-18)."""
    history = state.get("stage_history")
    if not isinstance(history, list):
        return False
    return any(
        isinstance(entry, dict) and entry.get("transition") == "disposition"
        and entry.get("packet_id") == packet_id
        for entry in history
    )


def _feature_status(state: dict[str, Any], feature_id: str) -> str | None:
    """The `epic_features` status of the feature, when it is registered."""
    features = state.get("epic_features")
    if not isinstance(features, list):
        return None
    for item in features:
        if isinstance(item, dict) and item.get("id") == feature_id:
            status = item.get("status")
            return status if isinstance(status, str) else None
    return None


def _resolve_closure_feature(state: dict[str, Any], requested: str | None,
                             active: str | None) -> str | None:
    """PD-22: the feature a `closure` operates on, from three sources in order —
    `--feature` (`requested`), `state.active_feature` (`active`) and the feature
    bound by the active execution (`state.execution.feature_id`, the single
    value the closure effect does not clear).

    PD-24: a `requested` that names a feature outside `epic_features`, or that
    diverges from the feature resolved by the state, fails closed — a closure
    never deviates silently to another feature."""
    binding = state.get("execution")
    bound = binding.get("feature_id") if isinstance(binding, dict) else None
    if not isinstance(bound, str) or not bound:
        bound = None
    resolved = active or bound
    if not isinstance(requested, str) or not requested:
        return resolved
    features = state.get("epic_features")
    known = isinstance(features, list) and any(
        isinstance(item, dict) and item.get("id") == requested
        for item in features)
    if not known:
        raise PolicyError(
            f"state incoherent: --feature {requested!r} does not name a feature of "
            f"epic_features, so the closure cannot resolve the feature it would close; "
            f"name an existing feature (PD-24)")
    if resolved is not None and requested != resolved:
        raise PolicyError(
            f"state incoherent: --feature {requested!r} does not match the feature "
            f"{resolved!r} resolved from the state (state.active_feature or the feature "
            f"bound by the active execution); name the same feature or omit --feature "
            f"(PD-24)")
    return requested


def _missing_required_deliveries(project_root: Path, state: dict[str, Any],
                                 execution_id: str) -> list[str]:
    """PD-8(a): the dispatched packets of the active execution with NEITHER a
    durable receipt NOR a registered disposition, in dispatch order."""
    return [
        packet_id for packet_id in _dispatched_packet_ids(project_root, execution_id)
        if not _packet_has_receipt(project_root, execution_id, packet_id)
        and not _packet_has_disposition(state, packet_id)
    ]


def _pin_relative_digest(project_root: Path, path_text: str, asserted: str | None,
                         label: str) -> tuple[str, str]:
    """PD-5/PD-20 for a cited project-relative file (`--contract-path`,
    `--plan-path`): DERIVE its sha256 from the current bytes, or verify the
    asserted digest against them. The CLI only READS the cited file: a missing
    path or a divergent assertion fails closed with `evidence missing` and no
    effects (INV-7). Returns the cited relative string and the digest used, so
    the entry records exactly what was verified."""
    path = _project_path(project_root, path_text, f"{label} path")
    if not path.is_file():
        raise PolicyError(
            f"evidence missing: {label} not found at {path_text!r}; the digest cannot be "
            f"derived from absent bytes. Cite an existing {label} path, or register the gate "
            f"once the {label} exists")
    actual = hashlib.sha256(_read_bytes(path, label)).hexdigest()
    if asserted is not None and asserted != actual:
        raise PolicyError(
            f"evidence missing: the asserted {label} digest {asserted} does not match the "
            f"current bytes {actual} of {path_text!r}; the CLI derives the digest from the "
            f"bytes it reads, so omit the assertion or cite exactly the bytes reviewed")
    return path_text, actual


def _gate_authority(state: dict[str, Any], project_root: Path,
                    execution: dict[str, Any]) -> str | None:
    """PD-6 (the correction P2): the three cases of the authority that approves
    a gate.

    With a registered `hitl_delegation` its vigency is verified through the
    existing control `_validate_v2_vigency` — consumed, never re-declared
    (INV-4) — plus the declared date expiry that control does not read (D4:
    an ISO `expires_on` in the past is not vigente); revoked or expired fails
    closed with `approval pending`. Without a delegation record there is no
    authority to verify: the CLI does not invent one and cannot verify
    identities (debt D-6), so it does NOT block the owner, who is the original
    authority. Returns the verified delegation source, or None when there was
    no delegation to verify (no record, or no active epic)."""
    delegation = state.get("hitl_delegation")
    if not isinstance(delegation, dict):
        return None
    epic_id = execution.get("epic_id")
    try:
        source = _validate_v2_vigency(
            state, project_root, execution["feature_id"], epic_id)
    except PolicyError as exc:
        raise PolicyError(
            f"approval pending: the registered hitl_delegation is not vigente for the active "
            f"epic {epic_id!r} ({exc}); a revoked or expired delegation fails closed, renew "
            f"the delegation in state.hitl_delegation before registering the gate (PD-6)"
        ) from exc
    expires_on = delegation.get("expires_on")
    if isinstance(expires_on, str) and expires_on.strip():
        try:
            expiry = date.fromisoformat(expires_on.strip())
        except ValueError as exc:
            raise PolicyError(
                f"approval pending: the hitl_delegation declares expires_on {expires_on!r}, "
                f"which is not an ISO date, so its vigency cannot be verified; register a "
                f"dated or an event-based delegation (PD-6)"
            ) from exc
        if expiry < date.today():
            raise PolicyError(
                f"approval pending: the hitl_delegation expired on {expires_on} (expires_on "
                f"is in the past); an expired delegation fails closed, renew it before "
                f"registering the gate (PD-6)"
            )
    return source


def _authority_note(state: dict[str, Any], source: str | None) -> str:
    """PD-6: the note BOTH approvals (`gate` and `closure`) print for the three
    cases of the authority they consumed (`_gate_authority`). Shared so the two
    classes declare the same thing: without a delegation record the owner is not
    blocked and there was no delegation to verify (P2/D-6)."""
    if not isinstance(state.get("hitl_delegation"), dict):
        return ("authority: no hitl_delegation registered; the declared approver is "
                "recorded and there is no delegation to verify (PD-6)")
    if source is not None:
        return (f"authority: hitl_delegation verified (source {source}); the declared "
                f"approver is recorded (PD-6)")
    return ("authority: there is no active epic authority to verify; the declared "
            "approver is recorded (PD-6)")


def register_transition(args: argparse.Namespace, project_root: Path) -> str:
    """Register one explicit transition decision under the single writer.

    Everything (vocabulary, referenced evidence, identity) is resolved BEFORE
    the single atomic publication of the state, so any rejection leaves the
    state byte for byte identical (INV-7) and an identical repetition writes
    nothing at all (PD-11)."""
    transition = args.transition
    stage = args.stage
    # §2.1: `--stage` is the historical label of the transition (a plain token);
    # `--current-stage`/`--substage` are the OPERATIONAL fields, with the closed
    # vocabulary. The CLI never confuses the two.
    if transition == "disposition":
        # §2.1/D-13: this class does NOT accept `--stage`; it carries the
        # canonical label, so the identity key never depends on a free text
        # without effect.
        if stage is not None:
            raise PolicyError(
                f"state incoherent: --transition disposition does not accept --stage; the "
                f"class carries the canonical label {DISPOSITION_STAGE!r} (spec §2.1/D-13)")
        stage = DISPOSITION_STAGE
    if transition == "late-delivery":
        # §2.1/PD-13: like `disposition`, this class does NOT accept `--stage`:
        # it carries the canonical label `late-delivery` (§2.2), and a free label
        # would make the identity key depend on a text without effect.
        if stage is not None:
            raise PolicyError(
                f"state incoherent: --transition late-delivery does not accept --stage; the "
                f"class carries the canonical label {LATE_DELIVERY_STAGE!r} (spec §2.1/PD-13)")
        stage = LATE_DELIVERY_STAGE
    if not isinstance(stage, str) or not stage:
        raise PolicyError(
            f"register-transition --transition {transition!r} requires --stage <token>: the "
            f"label the entry carries in stage_history (§2.1)")
    if FLAT_NAME.fullmatch(stage) is None:
        raise PolicyError(
            f"state incoherent: --stage must be a plain token ([A-Za-z0-9._-]), got {stage!r}")
    if args.current_stage is not None and args.current_stage not in VALID_CURRENT_STAGES:
        raise PolicyError(
            f"state incoherent: --current-stage {args.current_stage!r} is outside the closed "
            f"vocabulary {sorted(VALID_CURRENT_STAGES)}; name one of those stages")
    if args.substage is not None and args.substage not in VALID_SUBSTAGES:
        raise PolicyError(
            f"state incoherent: --substage {args.substage!r} is outside the closed vocabulary "
            f"{sorted(VALID_SUBSTAGES)}; name one of those subphases")
    if transition == "gate" and (
            not isinstance(args.approve_by, str) or not args.approve_by.strip()):
        # PD-5: the entry of a gate records WHO approves it; a gate without a
        # declared approver has nothing to register.
        raise PolicyError(
            "state incoherent: --transition gate requires --approve-by <text>: the entry "
            "records the declared approver (PD-5/PD-6)")
    if (args.exempted_by is not None or args.exemption_reason is not None
            or args.requested_by is not None or args.delegated):
        # 006-006 PD-9 (§2.7): the owner's exemption travels IN the approval
        # that opens the gate, so the class `gate` is the ONLY one that admits
        # it. The rejection happens BEFORE any effect, so the state stays byte
        # for byte identical (INV-7), and it NAMES the admitted class.
        if transition != "gate":
            raise PolicyError(
                f"state incoherent: the exemption flags (--exempted-by, "
                f"--exemption-reason, --requested-by, --delegated) are only "
                f"admissible in the class `gate`; --transition {transition!r} "
                f"is not that class, so the exemption has no entry to be "
                f"registered in (PD-9)")
    if transition == "closure" and (
            not isinstance(args.approve_by, str) or not args.approve_by.strip()):
        # PD-6: the closure also records WHO approves it; a closure without a
        # declared approver has nothing to approve.
        raise PolicyError(
            "state incoherent: --transition closure requires --approve-by <text>: the entry "
            "records the declared approver (PD-6)")

    with _ProjectLock(project_root):
        cleanup_stale_transactions(project_root)
        state_path = project_root / "docs" / ".cdad-state.json"
        state = _load_json(state_path, "project state")
        execution_document, execution_id = _resolve_active_execution(project_root, state)
        if execution_document.get("schema_version") != V2_SCHEMA_VERSION:
            raise PolicyError("register-transition requires an active v2 execution context")
        feature_id = state.get("active_feature")
        # PD-27: whether there is an ACTIVE feature; without one the closure
        # never APPLIES a closure (it only recognises the registered one or
        # rejects closed).
        closure_active_feature = (
            feature_id if isinstance(feature_id, str) and feature_id else None)
        if transition == "late-delivery":
            # PD-13/§2.1: the late delivery is registered for a CLOSED feature,
            # so `state.active_feature` is null by construction; the cited
            # feature comes from `--feature` (whose declared default is
            # `active_feature`). No other class resolves its feature differently.
            feature_id = args.feature if args.feature else feature_id
        if transition == "closure":
            # PD-22/PD-24: the closure resolves its feature from three sources,
            # in order — `--feature`, `state.active_feature` and the feature
            # bound by the active execution (`state.execution.feature_id`, which
            # the closure effect does NOT clear).
            feature_id = _resolve_closure_feature(
                state, args.feature, closure_active_feature)
        if not isinstance(feature_id, str) or not feature_id:
            if transition == "closure":
                # PD-22 (none of the three sources): the closure fails closed
                # naming the situation and offering the legitimate exit; it does
                # NOT suggest opening the unit (the feature is closed or was
                # never opened for it).
                raise PolicyError(
                    "state incoherent: closure cannot resolve the feature it would close "
                    "(state.active_feature is null and no feature is bound by the active "
                    "execution); to repeat an already applied closure, name its feature "
                    "with --feature <feature-id> (PD-22)")
            raise PolicyError(
                "state incoherent: there is no active feature to register a transition for "
                "(state.active_feature is null); open the unit first (`open-unit`)")

        packet_id: str | None = None
        receipt_sha256: str | None = None
        receipt_ref: str | None = None
        artifacts: dict[str, str] = {}
        contract_path: str | None = None
        contract_sha256: str | None = None
        plan_path: str | None = None
        plan_sha256: str | None = None
        resolution: str | None = None
        replaced_by: str | None = None
        closure_path: str | None = None
        closure_sha256: str | None = None
        authority_note = ""
        if transition == "delivery":
            packet_id = args.packet
            if not isinstance(packet_id, str) or not packet_id:
                raise PolicyError(
                    "state incoherent: --transition delivery requires --packet <packet-id>: the "
                    "delivery must cite the packet it receives")
            if (args.postcondition is None) != (args.outcome is None):
                raise PolicyError(
                    "state incoherent: --postcondition <n> and --outcome <red|green> are "
                    "declared together (they are the recorded postcondition outcome)")
            request_path = project_root / ".cdad" / "packets" / packet_id / "REQUEST.json"
            if not _packet_request_belongs_to_execution(request_path, execution_id):
                raise PolicyError(
                    f"evidence missing: the cited packet {packet_id} does not belong to the "
                    f"active execution {execution_id} (no .cdad/packets/{packet_id}/REQUEST.json "
                    f"of this execution); cite a packet of the active execution")
            receipt_sha256, receipt_ref = _durable_receipt(
                project_root, execution_id, packet_id, args.receipt)
        if transition == "disposition":
            # PD-21: the disposition of a dispatch that will not come back, with
            # the feature OPEN. Everything mechanical is checked BEFORE writing:
            # the decision itself is the orchestrator's (INV-5), the CLI only
            # checks the coherence and registers it.
            resolution = args.resolution
            if resolution not in DISPOSITION_RESOLUTIONS:
                raise PolicyError(
                    f"state incoherent: --transition disposition requires --resolution "
                    f"<{'|'.join(DISPOSITION_RESOLUTIONS)}>: the entry records the declared "
                    f"decision over the dispatch (PD-21)")
            if resolution == "superseded":
                replaced_by = args.replaced_by
                if not isinstance(replaced_by, str) or not replaced_by:
                    raise PolicyError(
                        "state incoherent: --resolution superseded requires --replaced-by "
                        "<packet-id>: the entry records which packet replaces the disposed "
                        "dispatch (PD-21)")
            packet_id = args.packet
            if not isinstance(packet_id, str) or not packet_id:
                raise PolicyError(
                    "state incoherent: --transition disposition requires --packet <packet-id>: "
                    "the dispatch being dispositioned must be cited (PD-21)")
            request_path = project_root / ".cdad" / "packets" / packet_id / "REQUEST.json"
            if not _packet_request_belongs_to_execution(request_path, execution_id):
                raise PolicyError(
                    f"state incoherent: packet {packet_id} does not belong to the active "
                    f"execution {execution_id} (no .cdad/packets/{packet_id}/REQUEST.json of "
                    f"this execution), so there is no dispatch of this feature to disposition "
                    f"(PD-21/PD-12(iv))")
            if not _packet_is_dispatched(project_root, execution_id, packet_id):
                raise PolicyError(
                    f"state incoherent: packet {packet_id} has no dispatch record in the active "
                    f"execution {execution_id}, so it is not `dispatched` and there is no "
                    f"delivery to resolve; only a dispatched packet can be dispositioned "
                    f"(PD-21/PD-12(iv))")
            if _packet_has_receipt(project_root, execution_id, packet_id):
                raise PolicyError(
                    f"state incoherent: packet {packet_id} already has a durable "
                    f"{RECEIPT_FILENAME} under "
                    f"{RESULTS_RELDIR.as_posix()}/{execution_id}/{packet_id}/, so the evidence "
                    f"contradicts the disposition; receive the delivery by the normal route "
                    f"instead of dispositioning it (PD-21/PD-12(iv))")
            status = _feature_status(state, feature_id)
            if status in CLOSED_FEATURE_STATUSES:
                raise PolicyError(
                    f"state incoherent: feature {feature_id!r} is closed (its epic_features "
                    f"entry is {status!r}), so there is no open feature whose dispatch could be "
                    f"dispositioned; the late route for an already closed feature is declared by "
                    f"PD-13 (PD-21)")
        if transition == "late-delivery":
            # PD-13 (2)/D-5: the DECLARED exit for a delivery that exists but
            # arrives AFTER the closure. Everything mechanical is checked BEFORE
            # writing (INV-7): the feature is CLOSED (the inverse of the normal
            # route's precondition), the cited packet belongs to its (closed)
            # execution, and the durable receipt EXISTS — the receipt is the
            # evidence the trace cites, and its digest is derived (PD-20).
            packet_id = args.packet
            if not isinstance(packet_id, str) or not packet_id:
                raise PolicyError(
                    "state incoherent: --transition late-delivery requires --packet "
                    "<packet-id>: the late delivery must cite the packet it receives (PD-13)")
            status = _feature_status(state, feature_id)
            if status not in CLOSED_FEATURE_STATUSES:
                raise PolicyError(
                    f"state incoherent: feature {feature_id!r} is not closed (its epic_features "
                    f"entry is {status!r}), so there is no closed feature to receive a late "
                    f"delivery for; the late route is ONLY for an already closed feature — "
                    f"receive with the feature open and the packet dispatched is the normal "
                    f"route (PD-13)")
            request_path = project_root / ".cdad" / "packets" / packet_id / "REQUEST.json"
            if not _packet_request_belongs_to_execution(request_path, execution_id):
                raise PolicyError(
                    f"state incoherent: packet {packet_id} does not belong to the execution "
                    f"{execution_id} of the closed feature {feature_id!r} (no "
                    f".cdad/packets/{packet_id}/REQUEST.json of this execution); the late "
                    f"delivery cites a packet of its execution (PD-13)")
            receipt_sha256, receipt_ref = _durable_receipt(
                project_root, execution_id, packet_id, args.receipt)
            if receipt_sha256 is None:
                raise PolicyError(
                    f"evidence missing: packet {packet_id} has no durable receipt at "
                    f"{receipt_ref}, so the late delivery of feature {feature_id!r} cannot be "
                    f"registered; persist the staged delivery first with the declared late "
                    f"mode (`cdad_result.py receive --late`) (PD-13)")
        if transition == "closure":
            # PD-23/PD-25/PD-27: when the feature is ALREADY CLOSED or there is
            # NO active feature, the closure can only recognise the registered
            # transition or reject closed — it NEVER applies. In this branch the
            # resolution of the cited closure (PD-9/PD-20) and the identity
            # lookup (PD-23) precede PD-8(a), PD-8(b), the `--closure-path`
            # requirement and the authority: a legitimate replay is a no-op even
            # when the world changed after the closure.
            closure_status = _feature_status(state, feature_id)
            if (closure_active_feature is None
                    or closure_status in CLOSED_FEATURE_STATUSES):
                if args.closure_path is not None:
                    closure_path, closure_sha256 = _pin_relative_digest(
                        project_root, args.closure_path, args.closure_sha256,
                        "closure")
                elif args.closure_sha256 is not None:
                    raise PolicyError(
                        "state incoherent: --closure-sha256 asserts the digest of a closure "
                        "that was not cited; pass --closure-path too, so the CLI can check "
                        "the bytes (PD-20)")
                for raw in args.artifact:
                    path_text, digest = _resolve_evidence_digest(raw, "artifact")
                    artifacts[path_text] = digest
                # PD-10: the identity payload of THIS closure; the digests it
                # carries are the RESOLVED ones (the same the entry writes).
                closure_key = _transition_key(_transition_identity_payload(
                    execution_id=execution_id, feature_id=feature_id,
                    transition=transition, stage=stage, substage=args.substage,
                    packet_id=None, receipt_sha256=None, resolution=None,
                    replaced_by=None,
                    postcondition=(None if args.postcondition is None else
                                   {"n": str(args.postcondition),
                                    "outcome": args.outcome}),
                    current_stage=args.current_stage, artifacts=artifacts,
                    approved_by=args.approve_by, contract=None, plan=None,
                    closure=(None if closure_path is None else
                             {"path": closure_path, "sha256": closure_sha256})))
                if _registered_transition(state, closure_key) is not None:
                    # PD-23: an identical repetition of an applied closure is a
                    # successful no-op; the state is not written.
                    return _transition_noop_message(transition, stage, closure_key)
                if closure_status in CLOSED_FEATURE_STATUSES:
                    # PD-25: the resolved feature is already closed and this is
                    # a DIFFERENT closure — reject closed, naming the feature and
                    # its state, without offering to open the unit, and pointing
                    # at the legitimate exits.
                    raise PolicyError(
                        f"state incoherent: feature {feature_id!r} is already closed (its "
                        f"epic_features entry is {closure_status!r}); this closure is not "
                        f"the registered one, so there is nothing to apply. Repeat the "
                        f"SAME closure order (already registered, a no-op), or register a "
                        f"delivery that arrived after the closure with the declared late "
                        f"route (--transition late-delivery) (PD-25)")
                # PD-27(c): without an active feature the closure NEVER applies;
                # this one is not registered and the feature is not closed.
                raise PolicyError(
                    f"state incoherent: there is no active feature to apply the closure of "
                    f"{feature_id!r} (state.active_feature is null) and this closure is not "
                    f"registered; to repeat an already applied closure, name its feature "
                    f"with --feature <feature-id> (PD-27)")
            # PD-8: the closure checks its two mechanical requirements BEFORE
            # anything else (and before reading the closure document it will
            # cite, PD-9): a rejection here leaves the state byte for byte
            # identical (INV-7).
            #
            # PD-8(a): EVERY dispatched packet of the active execution needs a
            # durable receipt OR a registered disposition. The rejection NAMES
            # the packet and the missing receipt and offers the TWO legitimate
            # exits (receive by the normal route, or disposition with the feature
            # open); the late route is for a CLOSED feature and is not offered
            # here (B1).
            missing = _missing_required_deliveries(project_root, state, execution_id)
            if missing:
                pending = missing[0]
                raise PolicyError(
                    f"evidence missing: packet {pending} of the active execution {execution_id} "
                    f"has a dispatch record and no durable receipt at "
                    f"{RESULTS_RELDIR.as_posix()}/{execution_id}/{pending}/{RECEIPT_FILENAME}, "
                    f"so the closure of feature {feature_id!r} cannot be registered before every "
                    f"required delivery is resolved. Two legitimate exits: (i) receive the "
                    f"delivery by the normal route (`cdad_result.py receive` then "
                    f"`register-transition --transition delivery`); (ii) if the dispatch will "
                    f"not come back, register its disposition while the feature is open "
                    f"(`register-transition --transition disposition --packet {pending} "
                    f"--resolution abandoned`). The closure checks the required deliveries "
                    f"before applying anything (PD-8(a))")
            # PD-8(b): a VIGENTE `specification` approval whose pin NAMES the
            # feature's contract with its DERIVED digest (§2.5). The pin
            # convention is the one `validate_request`/`_contract_for` already
            # declare for a feature's contract (consumed, never re-declared).
            contract_rel = f"docs/specs/{feature_id}/spec.md"
            contract_file = project_root / contract_rel
            if not contract_file.is_file():
                raise PolicyError(
                    f"approval pending: the contract {contract_rel!r} of feature {feature_id!r} "
                    f"does not exist, so the closure cannot verify the `specification` approval "
                    f"that pins it; register the contract and its approval before closing "
                    f"(PD-8(b))")
            current_contract = hashlib.sha256(
                _read_bytes(contract_file, "contract")).hexdigest()
            vigente = [
                item for item in _approved_spec_entries(state, feature_id)
                if item.get("contract_path") == contract_rel
                and item.get("contract_sha256") == current_contract]
            if not vigente:
                raise PolicyError(
                    f"approval pending: feature {feature_id!r} has no VIGENTE `specification` "
                    f"approval whose pin names the contract {contract_rel!r} with its current "
                    f"digest {current_contract}; register the spec approval in stage_history "
                    f"with stage 'specification', approved_by, contract_path {contract_rel!r} "
                    f"and contract_sha256, or re-approve the contract after it changed "
                    f"(PD-8(b))")
            # PD-8 green: PD-9/PD-20 — the closure cites the closure document; the
            # digest is DERIVED from the bytes unless it is asserted, and an
            # absent or divergent one fails closed with `evidence missing`.
            if args.closure_path is not None:
                closure_path, closure_sha256 = _pin_relative_digest(
                    project_root, args.closure_path, args.closure_sha256, "closure")
            elif args.closure_sha256 is not None:
                raise PolicyError(
                    "state incoherent: --closure-sha256 asserts the digest of a closure that "
                    "was not cited; pass --closure-path too, so the CLI can check the bytes "
                    "(PD-20)")
            else:
                raise PolicyError(
                    "state incoherent: --transition closure requires --closure-path <path>: the "
                    "closure must cite the closure document it registers (PD-9)")
            # PD-6/PD-9: the closure ALSO verifies the authority that approves it
            # — the same three cases the gate verifies, through the same consumed
            # control `_gate_authority` (INV-4, never re-declared), and before any
            # write: with a registered hitl_delegation a revoked or expired one
            # fails closed with `approval pending` and no effects (INV-7); without
            # a delegation record the owner is not blocked (P2/D-6) and the output
            # declares that there was no delegation to verify.
            source = _gate_authority(state, project_root, execution_document["execution"])
            authority_note = _authority_note(state, source)
        if transition == "gate":
            # PD-5: the gate of stage 2 pins the contract — and the plan — by
            # verifying the cited BYTES before writing; PD-20: the digest is
            # derived unless it is asserted, and a divergent assertion (or an
            # absent file) fails closed with `evidence missing`.
            if args.contract_path is not None:
                contract_path, contract_sha256 = _pin_relative_digest(
                    project_root, args.contract_path, args.contract_sha256, "contract")
            elif args.contract_sha256 is not None:
                raise PolicyError(
                    "state incoherent: --contract-sha256 asserts the digest of a contract that "
                    "was not cited; pass --contract-path too, so the CLI can check the bytes "
                    "(PD-20)")
            if args.plan_path is not None:
                plan_path, plan_sha256 = _pin_relative_digest(
                    project_root, args.plan_path, args.plan_sha256, "plan")
            elif args.plan_sha256 is not None:
                raise PolicyError(
                    "state incoherent: --plan-sha256 asserts the digest of a plan that was not "
                    "cited; pass --plan-path too, so the CLI can check the bytes (PD-20)")
            # PD-6: the authority has three cases; without a delegation record
            # there is nothing to verify and the owner is not blocked (P2). The
            # note is shared with `closure`, which consumes the same control.
            source = _gate_authority(state, project_root, execution_document["execution"])
            authority_note = _authority_note(state, source)
        for raw in args.artifact:
            path_text, digest = _resolve_evidence_digest(raw, "artifact")
            artifacts[path_text] = digest

        # 006-006 PD-9 (§2.7, R-12): the owner's exemption is DECLARED by the
        # invocation. The block carries EXACTLY the declared fields (the ones
        # not declared are not in it, not as `null`) and it is the SAME image
        # of the fields the entry writes, flat.
        exemption: dict[str, Any] = {}
        if transition == "gate":
            if args.exempted_by is not None:
                exemption["exempted_by"] = args.exempted_by
            if args.exemption_reason is not None:
                exemption["reason"] = args.exemption_reason
            if args.requested_by is not None:
                exemption["requested_by"] = args.requested_by
            if args.delegated:
                exemption["delegated"] = True

        # PD-10 (B2): the canonical payload of the identity. It is built AFTER
        # the evidence resolution on purpose: the digests it carries are the
        # RESOLVED ones (PD-20), the same ones the entry writes.
        payload = _transition_identity_payload(
            execution_id=execution_id, feature_id=feature_id,
            transition=transition, stage=stage, substage=args.substage,
            packet_id=packet_id, receipt_sha256=receipt_sha256,
            resolution=resolution, replaced_by=replaced_by,
            postcondition=(None if args.postcondition is None else
                           {"n": str(args.postcondition), "outcome": args.outcome}),
            current_stage=args.current_stage, artifacts=artifacts,
            approved_by=(args.approve_by if transition in ("gate", "closure")
                         else None),
            contract=(None if contract_path is None else
                      {"path": contract_path, "sha256": contract_sha256}),
            plan=(None if plan_path is None else
                  {"path": plan_path, "sha256": plan_sha256}),
            closure=(None if closure_path is None else
                     {"path": closure_path, "sha256": closure_sha256}),
            # R-11: the conditional block; without a declared exemption the
            # payload keeps its 16 keys and its key stays byte for byte the one
            # of the previous product (R-13/D-14).
            exemption=(exemption or None),
        )
        key = _transition_key(payload)
        registered = _registered_transition(state, key)
        if registered is not None:
            # PD-11: an identical repetition is a successful no-op; the state is
            # not written, so it stays byte for byte identical.
            #
            # 006-006 PD-9 (R-14, B-4): this branch is QUALIFIED. The replay
            # of the VIGENTE entry is a no-op (PD-11); an invocation that
            # collides with a HISTORICAL entry while a VIGENTE approval
            # competes is NEVER a no-op — it is an attempt to substitute the
            # vigente approval, and answering it with success would lose the
            # requested change in silence (D-15).
            vigente = (_vigente_spec_approval(
                state, feature_id, contract_path, contract_sha256)
                if (transition == "gate" and stage == SPEC_GATE_STAGE
                    and contract_path is not None) else None)
            if (vigente is None
                    or vigente.get("transition_key")
                    == registered.get("transition_key")):
                return _transition_noop_message(transition, stage, key)
            if isinstance(args.supersedes, str) and args.supersedes:
                # (b) with `--supersedes`: the EXPLICIT rejection of the
                # collision — it names the colliding key (and that it is NOT
                # the vigente one), the key of the vigente one and the two
                # exits (D-15).
                raise PolicyError(_transition_collision_message(
                    feature_id, contract_path, key,
                    str(vigente.get("transition_key"))))
            # without `--supersedes` the rejection is the vigente one of PD-14
            # (one vigente approval per feature and contract), below.

        # PD-12: the structural exclusions fail closed, before any write. The
        # marker split is by condition: a packet that is not dispatched is an
        # incoherent state; a dispatched packet without a receipt is missing
        # evidence (PD-3).
        if transition == "delivery":
            if not _packet_is_dispatched(project_root, execution_id, packet_id):
                raise PolicyError(
                    f"state incoherent: packet {packet_id} has no dispatch record in the "
                    f"active execution {execution_id}, so it cannot be received as a delivery "
                    f"(only a dispatched packet can have a durable receipt). Dispatch it "
                    f"first, or cite the dispatched packet")
            if receipt_sha256 is None:
                raise PolicyError(
                    f"evidence missing: packet {packet_id} has no durable receipt at "
                    f"{receipt_ref}; receive the delivery by the normal route "
                    f"(`cdad_result.py receive`) before registering it, or use the declared "
                    f"exit for a dispatch that will not come back")
        if (transition == "gate" and stage == SPEC_GATE_STAGE
                and contract_path is not None):
            # PD-14 (D-8): one VIGENTE `specification` approval per (feature,
            # contract_path). Registering a second one over an existing vigente
            # entry requires the structural mark `--supersedes` naming the entry
            # it replaces — which is never rewritten (INV-3, append-only), so
            # the reader derives the vigency from the new entry's declaration.
            # Without the mark the state is incoherent, not a silent second
            # approval.
            #
            # VIGENTE is the pin that NAMES the current bytes of the contract
            # —the `contract_path` AND the `contract_sha256` (already RESOLVED
            # from those bytes, PD-20)— which is the same criterion the closure
            # consumes in PD-8(b): an entry whose pin no longer names them (the
            # contract was amended after that approval) does not compete, so
            # re-approving amended bytes needs no `--supersedes` — not even when
            # the stale entry is keyless and therefore cannot be cited (B3). The
            # entry with the stale pin is not made inoperative by this: the
            # reader already required the pin to match (D3/PD-18), so nothing
            # that authorized keeps authorizing.
            vigente = [item for item in _approved_spec_entries(state, feature_id)
                       if item.get("contract_path") == contract_path
                       and item.get("contract_sha256") == contract_sha256]
            if isinstance(args.supersedes, str) and args.supersedes:
                replaced = _registered_transition(state, args.supersedes)
                if (replaced is None or replaced.get("feature") != feature_id
                        or replaced.get("contract_path") != contract_path):
                    raise PolicyError(
                        f"state incoherent: --supersedes {args.supersedes!r} does not name "
                        f"an existing `specification` approval of feature {feature_id!r} "
                        f"for the contract {contract_path!r}; name the transition_key of "
                        f"the vigente entry it replaces (PD-14)")
            elif vigente:
                prior = vigente[0]
                raise PolicyError(
                    f"state incoherent: feature {feature_id!r} already has a vigente "
                    f"`specification` approval for the contract {contract_path!r} "
                    f"(transition_key {prior.get('transition_key')!r}); registering a "
                    f"second vigente one requires --supersedes <transition-key> naming the "
                    f"entry it replaces, so that only the new approval authorizes the "
                    f"construction roles (PD-14)")

        at = datetime.now(timezone.utc).isoformat()
        entry: dict[str, Any] = {
            "feature": feature_id,
            "stage": stage,
            "substage": args.substage,
            "at": at,
            "by": args.by,
            "transition": transition,
            "transition_key": key,
            "transition_key_payload": payload,
            "supersedes": args.supersedes,
            "approval_effect": False,
            "packet_id": packet_id,
            "receipt_ref": receipt_ref,
            "receipt_sha256": receipt_sha256,
            "artifacts": artifacts,
            "note": args.note,
        }
        if transition == "gate":
            # PD-5/§2.2: a gate declares WHO approves and pins the contract and
            # the plan it approves when they are cited; it carries no packet, no
            # receipt and no judgement field (PD-18).
            entry["approved_by"] = args.approve_by
            if contract_path is not None:
                entry["contract_path"] = contract_path
                entry["contract_sha256"] = contract_sha256
            if plan_path is not None:
                entry["plan_path"] = plan_path
                entry["plan_sha256"] = plan_sha256
            # 006-006 PD-9 (§2.7, D-6): the owner's exemption travels IN this
            # entry (the same one that opens the gate), FLAT and only the
            # declared fields; without the flags the entry carries none of
            # them (R-11).
            entry.update(exemption)
        if transition == "closure":
            # PD-9/§2.2: the closure records WHO approves it and the closure
            # document it cites with the digest used (derived or verified).
            entry["approved_by"] = args.approve_by
            entry["closure_path"] = closure_path
            entry["closure_sha256"] = closure_sha256
        if transition == "disposition":
            # PD-21/§2.2: the disposition is a STRUCTURAL datum — the declared
            # decision over the dispatch — never an approval: it carries
            # `resolution` (and `replaced_by` for `superseded`) and no
            # `approved_by` (INV-9).
            entry["resolution"] = resolution
            if replaced_by is not None:
                entry["replaced_by"] = replaced_by

        new_state = dict(state)
        history = list(state.get("stage_history") or [])
        history.append(entry)
        new_state["stage_history"] = history
        if transition == "delivery":
            # §2.2: the packet effect applies when the cited packet is the active
            # one; receiving never approves (PD-4/PD-18) and never writes
            # judgement fields.
            active = state.get("active_packet")
            if isinstance(active, dict) and active.get("id") == packet_id:
                new_state["active_packet"] = {**active, "status": "completed"}
            if args.substage is not None:
                new_state["tdd_substage"] = args.substage
            if args.postcondition is not None:
                outcomes = dict(state.get("postconditions_status") or {})
                outcomes[str(args.postcondition)] = args.outcome
                new_state["postconditions_status"] = outcomes
        elif transition == "closure":
            # §2.2/PD-9: the closure applies the resting effect on the feature
            # and the operational fields; `postconditions_status` is not cleared
            # (PD-9) and the history stays append-only (INV-3).
            features = state.get("epic_features")
            if isinstance(features, list):
                new_state["epic_features"] = [
                    {**item, "status": _DONE_UNIT_STATUS, "closed_at": at,
                     "closure_evidence": {"path": closure_path,
                                          "sha256": closure_sha256}}
                    if isinstance(item, dict) and item.get("id") == feature_id
                    else item
                    for item in features
                ]
            new_state["active_feature"] = None
            new_state["current_stage"] = IDLE_STAGE
            new_state["active_packet"] = None
        elif transition == "disposition":
            # PD-21/INV-9: the disposition registers a DECISION, not a result.
            # It never fabricates a `completed`, never approves and never
            # touches a derived field of the feature.
            #
            # 006-005 PD-19/D-4 (amends the INV-9 consequence, approved by the
            # owner): the dispatch that will not come back gets its MECHANICAL
            # route to `failed`. Only the CITED packet changes — and only its
            # `status` — so nothing else of the state is touched and the
            # decision still approves nothing. `failed` is terminal and outside
            # `ACTIVE_PACKET_STATUSES`, so it unblocks the next `prepare`
            # without stopping any worker (it is a state mark); the `late-delivery`
            # route does not read the packet status, so it stays registrable.
            active = state.get("active_packet")
            if isinstance(active, dict) and active.get("id") == packet_id:
                new_state["active_packet"] = {**active, "status": "failed"}
        elif transition == "late-delivery":
            # PD-13 (2)/INV-9: the late delivery registers a TRACE, not a result.
            # Its only write is the entry (plus `last_updated`): it never
            # re-opens the feature, never approves and never touches
            # `epic_features[].status`, `closed_at`, `active_feature`,
            # `current_stage` or `active_packet`.
            pass
        else:
            # §2.2: `advance` and `gate` set the OPERATIONAL stage fields when
            # they are declared; neither has an effect on the packet or on the
            # feature, and neither approves by side effect.
            if args.current_stage is not None:
                new_state["current_stage"] = args.current_stage
            if args.substage is not None:
                new_state["tdd_substage"] = args.substage
        new_state["last_updated"] = at
        if transition == "closure":
            # PD-9/the task sheet: the resting coherence is verified BEFORE
            # publishing, so a closure that cannot rest fails closed (INV-7)
            # instead of publishing an incoherent state.
            _validate_idle_coherence(new_state)
        _publish_owned_atomically([
            (state_path, _serialize_document(new_state)),
        ])

    lines = [f"registered transition {transition} stage {stage!r} for {feature_id}",
             f"transition_key: {key}"]
    if packet_id is not None:
        lines.append(f"packet: {packet_id}")
    if receipt_sha256 is not None:
        lines.append(f"receipt_sha256: {receipt_sha256} ({receipt_ref})")
    for path_text, digest in artifacts.items():
        lines.append(f"artifact: {path_text} {digest}")
    if transition == "gate":
        lines.append(f"approved_by: {args.approve_by}")
        if contract_path is not None:
            lines.append(f"contract: {contract_path} {contract_sha256}")
        if plan_path is not None:
            lines.append(f"plan: {plan_path} {plan_sha256}")
        lines.append(authority_note)
    if transition == "closure":
        lines.append(f"approved_by: {args.approve_by}")
        lines.append(f"closure: {closure_path} {closure_sha256}")
        lines.append(authority_note)
    if transition == "disposition":
        lines.append(f"resolution: {resolution}")
        if replaced_by is not None:
            lines.append(f"replaced_by: {replaced_by}")
    if args.current_stage is not None:
        lines.append(f"current_stage: {args.current_stage}")
    if args.substage is not None:
        lines.append(f"tdd_substage: {args.substage}")
    lines.append(f"stage_history: {len(history)} entries (+1)")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- 005-003 T1
# The compact operational view (`compact-view-v1`, spec §2.1/§2.2/§2.5). It is a
# read-only PROJECTION of the existing sources (state, execution context, policy,
# version check), generated by code, deterministic, and bounded by a normative
# byte limit; it never emits `stage_history` and never writes (INV-1/INV-2).


def _read_optional_document(
    project_root: Path, rel: str, label: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Read a JSON object if present, never failing the read-only view (INV-9).

    A missing or unreadable source is surfaced as a cause in `unknowns[]`, never
    as a fabricated value.
    """
    path = project_root / rel
    if not path.is_file():
        return None, f"{label} not found: {rel}"
    try:
        with path.open(encoding="utf-8") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"cannot read {label} {rel}: {exc}"
    if not isinstance(document, dict):
        return None, f"{label} {rel} is not a JSON object"
    return document, None


# The four legs the canonical check prints, in its own order (spec §2.3 c1):
# the view NAMES the diverging leg by READING these lines, never by inferring
# it from the verdict or its rc.
VERSION_LEGS = ("project", "agents", "CLI", "claude-code")


def _version_legs(stdout: str) -> dict[str, str | None]:
    """Per-leg values the canonical check prints, read (never inferred)."""
    legs: dict[str, str | None] = {}
    for line in stdout.splitlines():
        match = re.match(r"\s*(project|agents|CLI|claude-code):\s*(.*?)\s*$", line)
        if match is None:
            continue
        raw = match.group(2)
        # An absent leg prints a parenthesized placeholder (`(none: …)`,
        # `(no version.txt found)`, `(not detected: …)`): absence, not a version.
        legs[match.group(1)] = None if not raw or raw.startswith("(") else raw
    return legs


def _divergent_legs(legs: dict[str, str | None]) -> list[str]:
    """The legs that diverge from the running installation (the `CLI` leg).

    Read from the printed values: a present leg whose version is not the CLI's
    diverges. Only meaningful for a `DRIFT`, where project/agents/CLI are all
    present (the check returns `UNKNOWN`/`NO-PROJECT-AGENTS` otherwise).
    """
    reference = legs.get("CLI")
    if reference is None:
        present = [value for value in legs.values() if value is not None]
        reference = max(set(present), key=present.count) if present else None
    return [leg for leg in VERSION_LEGS
            if legs.get(leg) is not None and legs.get(leg) != reference]


def _version_verdict(project_root: Path) -> dict[str, Any]:
    """Reuse the canonical version check (spec §2.4) for the `version` field.

    The single version check is the sibling `cdad-version-check.py`; any
    non-zero rc reads as "not verified as coherent", never as ok (F6). The
    projection is an ADDITIVE extension of 005-003 (§2.3 c1): the existing
    `verdict`/`verified`/`cause` are conserved, and a `DRIFT` additionally names
    the leg that diverges and — only for the verified `project` leg — what
    resolves it. `UNKNOWN`/`NO-PROJECT-AGENTS` are ABSENCE (never incoherence):
    their cause carries no resolution clause and reads differently from DRIFT.
    """
    checker = Path(__file__).resolve().parent / "cdad-version-check.py"
    if not checker.is_file():
        return {"verdict": "UNKNOWN", "verified": False,
                "cause": "the version check script is not present next to this CLI"}
    try:
        proc = subprocess.run(
            [sys.executable, str(checker), "--project-root", str(project_root)],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"verdict": "UNKNOWN", "verified": False,
                "cause": f"the version check could not run: {exc}"}
    verdict = "UNKNOWN"
    for line in proc.stdout.splitlines():
        if line.startswith("verdict:"):
            verdict = line.split(":", 1)[1].strip().split(" ", 1)[0]
            break
    projection: dict[str, Any] = {"verdict": verdict, "verified": proc.returncode == 0}
    if proc.returncode != 0:
        if verdict == "DRIFT":
            divergent = _divergent_legs(_version_legs(proc.stdout))
            if divergent:
                projection["divergent_legs"] = divergent
            # The verified resolution is asserted ONLY when the diverging leg
            # is `project` (spec §2.3 c1): the next `prepare` republishes the
            # project's derived agents. Another leg gets no promise (inventing
            # one would over-promise what `prepare` does not fix).
            if divergent == ["project"]:
                projection["resolution"] = (
                    "the next `prepare` republishes the project's derived agents "
                    "from the project source (project-execution.md §143-146)")
            projection["cause"] = (
                f"version not verified as coherent: the check reports a "
                f"divergence (verdict {verdict}, rc {proc.returncode}); any "
                "non-zero rc reads as not verified")
        else:
            projection["cause"] = (
                f"version not verified: absence of a version marker or of "
                f"derived agents (verdict {verdict}, rc {proc.returncode}); "
                "absence, not incoherence")
    return projection


def _active_execution(state: dict[str, Any]) -> dict[str, Any] | None:
    """The ACTIVE execution, or `None` when the state block is history (F2).

    An execution is active only if `active_feature` is non-null AND the state
    `execution` block's `feature_id` matches it (spec §2.2 «Reposo e historia»).
    The `execution` block left behind after closing a feature is history.
    """
    feature = state.get("active_feature")
    if not isinstance(feature, str) or not feature:
        return None
    binding = state.get("execution")
    if not isinstance(binding, dict):
        return None
    if binding.get("feature_id") != feature:
        return None
    return binding


def _packet_request_belongs_to_execution(request_path: Path,
                                         execution_id: str) -> bool:
    """Whether a packet directory's `REQUEST.json` is of the active execution."""
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    return isinstance(request, dict) and request.get("execution_id") == execution_id


def _packet_has_receipt(project_root: Path, execution_id: str,
                       packet_id: str) -> bool:
    """Whether the packet already has a receipt under the runtime results root."""
    return (project_root / ".cdad" / "runtime" / "results" / execution_id / packet_id
            ).is_dir()


def _pending_work(state: dict[str, Any], project_root: Path,
                  packet: dict[str, Any] | None) -> bool:
    """«Trabajo pendiente» from EXISTING fields/dirs — no new state field (INV-2)."""
    if isinstance(packet, dict) and packet.get("status") in ACTIVE_PACKET_STATUSES:
        return True
    active = state.get("active_packet")
    if isinstance(active, dict):
        return active.get("status") in ACTIVE_PACKET_STATUSES
    # active_packet absent: only a published packet directory OF THE ACTIVE
    # EXECUTION that has no receipt is still pending work; directories of a
    # closed feature are history (F2).
    execution = _active_execution(state)
    execution_id = execution.get("id") if isinstance(execution, dict) else None
    if not isinstance(execution_id, str) or not execution_id:
        return False
    base = project_root / ".cdad" / "packets"
    if not base.is_dir():
        return False
    try:
        entries = list(base.iterdir())
    except OSError:
        return False
    return any(
        entry.is_dir()
        and (entry / "REQUEST.json").is_file()
        and _packet_request_belongs_to_execution(entry / "REQUEST.json", execution_id)
        and not _packet_has_receipt(project_root, execution_id, entry.name)
        for entry in entries
    )


def _entry_selection(*, state: dict[str, Any], project_root: Path,
                     packet: dict[str, Any] | None,
                     policy_present: bool) -> str:
    """The explicit entry-selection map of §2.2 (never an inference by literal)."""
    if not policy_present:
        return ENTRY_DIAGNOSIS
    epic = state.get("active_epic")
    delegation = state.get("hitl_delegation")
    if isinstance(epic, str) and epic:
        status = delegation.get("status") if isinstance(delegation, dict) else None
        if status != "active":
            return ENTRY_DIAGNOSIS
    if _pending_work(state, project_root, packet):
        return ENTRY_CONTINUITY_RECONCILE
    if _active_execution(state) is not None:
        return ENTRY_CONTINUITY_RECONCILE
    return ENTRY_NEXT_UNIT


def _next_route(entry: str, packet: dict[str, Any] | None) -> dict[str, str]:
    """The next operational route, each with its declared source (§2.1)."""
    if entry == ENTRY_CONTINUITY_RECONCILE:
        if isinstance(packet, dict) and packet.get("status") == "dispatched":
            return {"route": "reconcile the dispatched packet before repeating (resume)",
                    "source": "docs/.cdad-state.json:active_packet.status"}
        if isinstance(packet, dict) and packet.get("status") == "prepared":
            # PD-5 (005-011): a `prepared` packet is ready to be dispatched, so
            # the route NAMES the natural action; `--replace-packet` is only the
            # conditional branch (a genuinely obsolete contract).
            return {"route": "dispatch the prepared packet: validate it, then "
                             "`begin` and `--record-dispatch` (--replace-packet "
                             "only if the contract changed)",
                    "source": "docs/.cdad-state.json:active_packet.status"}
        return {"route": "resume the active execution (continuity)",
                "source": "docs/.cdad-state.json:execution"}
    if entry == ENTRY_DIAGNOSIS:
        return {"route": "diagnosis: complete the configuration (project-start.md §8)",
                "source": "docs/cdad-policy.json / authority pin"}
    # PD-7 (005-007 T3): the next-unit route NAMES the operation that opens the
    # unit (`cdad_packet.py open-unit`); it is an operation of the CLI, not a
    # hand-edited state. The procedure it points to documents it by reference.
    return {"route": "next unit: run `cdad_packet.py open-unit` (project-start.md §6)",
            "source": "docs/.cdad-state.json:current_stage"}


def _plan_marker(project_root: Path, state: dict[str, Any]) -> bool:
    """Whether the feature/epic plan marker is present (spec §2.1 `project`)."""
    feature_id = state.get("active_feature")
    if isinstance(feature_id, str) and feature_id:
        if (project_root / "docs" / "specs" / feature_id / "plan.md").is_file():
            return True
    epic_id = state.get("active_epic")
    if isinstance(epic_id, str) and epic_id:
        if (project_root / "docs" / "epics" / epic_id / "plan.md").is_file():
            return True
    return False


def status_view(args: argparse.Namespace, project_root: Path) -> bytes:
    """Emit the compact operational view (`compact-view-v1`) — read-only (PD-1).

    The projection is a function of the declared operational fields, never of the
    state size (the history is not emitted), so the byte limit is the same for
    any state. Above the limit it fails closed (rc≠0) without a partial
    projection, naming the limit and the legitimate way to obtain more.
    """
    max_bytes = args.max_bytes
    if not isinstance(max_bytes, int) or max_bytes < 1:
        raise PolicyError("--max-bytes must be a positive integer")

    unknowns: list[str] = []

    state, state_error = _read_optional_document(
        project_root, "docs/.cdad-state.json", "project state")
    if state_error:
        unknowns.append(state_error)
        state = {}

    policy_present = (project_root / POLICY_RELPATH).is_file()
    if not policy_present:
        unknowns.append(
            f"project policy not found: {POLICY_RELPATH.as_posix()} "
            "(configuration incomplete)")

    epic = {"active_epic": state.get("active_epic"), "epic_stage": state.get("epic_stage")}
    feature = {
        "active_feature": state.get("active_feature"),
        "current_stage": state.get("current_stage"),
        "tdd_substage": state.get("tdd_substage"),
    }

    execution: dict[str, Any] | None = None
    binding = state.get("execution")
    if isinstance(binding, dict) and isinstance(binding.get("id"), str) and binding["id"]:
        document, error = _read_optional_document(
            project_root,
            f"{EXECUTIONS_DIR.as_posix()}/{binding['id']}/execution.json",
            "execution context")
        if error:
            unknowns.append(error)
        elif isinstance(document.get("execution"), dict):
            exec_obj = document["execution"]
            execution = {
                "id": exec_obj.get("id"),
                "authority_ref": exec_obj.get("authority_ref"),
                "model_policy": exec_obj.get("model_policy"),
                "policy_sha256": exec_obj.get("policy_sha256"),
            }
        else:
            execution = {
                "id": document.get("id"),
                "authority_ref": document.get("authority_ref"),
                "model_policy": document.get("model_policy"),
                "policy_sha256": None,
            }
    elif isinstance(binding, dict):
        unknowns.append("state.execution is present but carries no id")

    active_packet = state.get("active_packet")
    packet: dict[str, Any] | None = None
    if isinstance(active_packet, dict):
        packet = {
            "id": active_packet.get("id"),
            "role": active_packet.get("role"),
            "substage": active_packet.get("substage"),
            "status": active_packet.get("status"),
        }

    delegation = state.get("hitl_delegation")
    authority = {
        "hitl_delegation": {
            "status": delegation.get("status") if isinstance(delegation, dict) else None,
            "source": delegation.get("source") if isinstance(delegation, dict) else None,
        },
        "approver": state.get("approver"),
        "approval": {
            "authority_ref": execution.get("authority_ref") if execution else None,
            "contract_sha256": (active_packet.get("contract_sha256")
                                if isinstance(active_packet, dict) else None),
        },
    }

    version = _version_verdict(project_root)
    if not version.get("verified"):
        unknowns.append(str(version.get("cause")
                            or f"version not verified: {version.get('verdict')}"))

    entry = _entry_selection(
        state=state, project_root=project_root, packet=packet,
        policy_present=policy_present)

    document = {
        "project": {
            "root": project_root.name,
            "markers": {
                "state": (project_root / "docs" / ".cdad-state.json").is_file(),
                "policy": policy_present,
                "feature": bool(feature["active_feature"]),
                "plan": _plan_marker(project_root, state),
            },
        },
        "epic": epic,
        "feature": feature,
        "execution": execution,
        "packet": packet,
        "authority": authority,
        "version": version,
        "next": _next_route(entry, packet),
        "entry": entry,
        "unknowns": unknowns,
        # PD-11 (005-013 T1): the additive, READ-ONLY unit-contract block. It
        # reports the mode and (in fallback) the reason; it writes nothing.
        "unit_contract": _unit_contract_status(state, project_root),
    }

    payload = (json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2)
               + "\n").encode("utf-8")
    if len(payload) > max_bytes:
        raise PolicyError(
            f"status view exceeds the byte limit: {len(payload)} bytes > {max_bytes} bytes "
            f"(--max-bytes, default {DEFAULT_VIEW_MAX_BYTES}). The compact view is bounded and "
            "does not grow with the state history; pass a larger --max-bytes N to obtain more, "
            "or consult the concrete source by reference")
    return payload


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        self.exit(2, f"ERROR: {self.prog}: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="cdad_packet.py")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-state", help="validate execution/state binding")
    validate.add_argument("--project-root")
    validate.add_argument("--execution-context")
    validate_policy = commands.add_parser(
        "validate-policy", help="validate docs/cdad-policy.json and classify project paths")
    validate_policy.add_argument("--project-root")
    validate_policy.add_argument("--classify", action="append", default=[], metavar="PATH",
                                 help="print the I1 class of a project-relative path")
    for name in ("render", "validate-request", "validate-packet"):
        command = commands.add_parser(name)
        command.add_argument("--project-root")
        command.add_argument("--execution-context", required=True)
        command.add_argument("--request", required=True)
        if name == "validate-packet":
            command.add_argument("--packet", required=True)
    prep = commands.add_parser("prepare", help="write request, packet and state binding; print the packet")
    prep.add_argument("--project-root")
    prep.add_argument("--execution-context")
    prep.add_argument("--role")
    prep.add_argument("--substage")
    prep.add_argument("--objective")
    prep.add_argument("--new-execution", action="store_true",
                      help="start a new v2 execution instead of reusing a prior context")
    prep.add_argument("--resume-packet", metavar="PACKET_ID",
                      help="recover a published packet byte-for-byte without changing identity")
    prep.add_argument("--replace-packet", metavar="PACKET_ID",
                      help="replace a prepared, never-dispatched obsolete packet (PD-7)")
    prep.add_argument("--reason", metavar="TEXT",
                      help="mandatory non-empty reason for --replace-packet (PD-9)")
    prep.add_argument("--propose-policy", action="store_true",
                      help="print a deterministic policy proposal without writing")
    prep.add_argument("--reconcile-policy", metavar="SHA256",
                      help="accept a policy revision for the active execution (PD-5/I6)")
    prep.add_argument("--decision-ref", metavar="PATH",
                      help="project file containing the owner's accepted revision")
    prep.add_argument("--record-dispatch", metavar="PACKET_ID",
                      help="register a dispatch attempt observation (I8)")
    prep.add_argument("--attempt-id", metavar="ID",
                      help="flat attempt identifier for --record-dispatch")
    prep.add_argument("--input", action="append", default=[])
    prep.add_argument("--read-scope", action="append", default=[])
    prep.add_argument("--write-scope", action="append", default=[])
    prep.add_argument("--invariant", action="append", default=[])
    prep.add_argument("--expected-output")
    prep.add_argument("--evidence", action="append", default=[])
    prep.add_argument("--out-dir")
    # PD-10/INV-4 (005-003 T6): the ADDITIVE task selector. With it the packet
    # declares its plan task and emits its validation plan and applicable
    # contract references; absent, the render is byte-identical.
    prep.add_argument("--plan-task", metavar="TASK_ID",
                      help="declare the plan task this packet implements (PD-10)")
    # PD-1 (004-003 T1): the explicit declared-draft surface. All three flags
    # select the draft contract object (kind `draft-plan` + its version and
    # path); absent, the role default derivation is unchanged.
    prep.add_argument("--contract-kind")
    prep.add_argument("--contract-path")
    prep.add_argument("--plan-version")
    # 006-006 U1 (R-5): the declared form of the reviewed object and the
    # companion spec identity. The companion's digest is computed by `prepare`
    # from the file's bytes, never asserted from outside.
    prep.add_argument("--object-kind", metavar="FORM",
                      help="declare the form of the reviewed object: spec or plan "
                           "(absent means plan)")
    prep.add_argument("--spec-path", metavar="PATH",
                      help="the companion spec document (only over a plan-form principal)")
    prep.add_argument("--spec-version", metavar="VERSION",
                      help="the version of the companion spec document")
    open_unit_cmd = commands.add_parser(
        "open-unit",
        help="open the next queued unit of the active epic (PD-7, state operation)")
    open_unit_cmd.add_argument("--project-root")
    open_unit_cmd.add_argument(
        "--feature", metavar="ID",
        help="open this epic_features entry; it must exist and be queued")
    # PD-1..PD-4/PD-7/PD-20 (005-012 T1): the operation that registers an
    # explicit transition decision (`transition-registration-v1`). It is
    # symmetric to `open-unit`: one subcommand, one contract, discoverable by
    # `--help`. `prepare` keeps its role and never registers a transition.
    register = commands.add_parser(
        "register-transition",
        help="register an explicit orchestrator decision over a transition "
             "(state operation)")
    register.add_argument("--project-root")
    register.add_argument("--transition", choices=TRANSITION_CLASSES, required=True,
                          help="the decision class (closed vocabulary)")
    register.add_argument("--stage", metavar="TOKEN",
                          help="the historical label of the transition (a plain token)")
    register.add_argument("--feature", metavar="ID",
                          help="the feature the transition belongs to "
                               "(default: state.active_feature; REQUIRED by "
                               "`late-delivery`, whose feature is closed)")
    register.add_argument("--approve-by", metavar="TEXT",
                          help="who approves the gate (PD-5/PD-6)")
    register.add_argument("--contract-path", metavar="PATH",
                          help="the cited contract (the gate of stage 2 pins it)")
    register.add_argument("--contract-sha256", metavar="SHA256",
                          help="optional assertion on the contract digest (PD-20)")
    register.add_argument("--plan-path", metavar="PATH",
                          help="the cited plan (the gate of stage 2 pins it)")
    register.add_argument("--plan-sha256", metavar="SHA256",
                          help="optional assertion on the plan digest (PD-20)")
    # 006-006 PD-9 (§2.7): the owner's exemption, admissible ONLY in the
    # class `gate` (the CLI rejects it elsewhere, naming the class).
    register.add_argument("--exempted-by", metavar="TEXT",
                          help="the owner who exempts the review (class `gate` "
                               "only; PD-9)")
    register.add_argument("--exemption-reason", metavar="TEXT",
                          help="why the review is exempted (class `gate` only; "
                               "PD-9)")
    register.add_argument("--requested-by", metavar="TEXT",
                          help="who requested the exemption (class `gate` only; "
                               "PD-9)")
    register.add_argument("--delegated", action="store_true",
                          help="the exemption was delegated (class `gate` only; "
                               "PD-9)")
    register.add_argument("--current-stage", metavar="STAGE",
                          help="operational field state.current_stage (closed vocabulary)")
    register.add_argument("--substage", metavar="SUB",
                          help="operational field state.tdd_substage (closed vocabulary)")
    register.add_argument("--packet", metavar="PACKET_ID",
                          help="the cited packet (the delivery being received)")
    register.add_argument("--receipt", metavar="SHA256",
                          help="optional assertion on the durable receipt digest (PD-20)")
    register.add_argument("--artifact", action="append", default=[], metavar="PATH[=SHA256]",
                          help="cited artifact (repeatable); its digest is derived (PD-20)")
    register.add_argument("--postcondition", metavar="N", type=int,
                          help="the postcondition the delivery records")
    register.add_argument("--outcome", choices=("red", "green"),
                          help="the recorded outcome of --postcondition")
    register.add_argument("--supersedes", metavar="TRANSITION_KEY",
                          help="the entry this transition supersedes (structural vigency)")
    register.add_argument("--closure-path", metavar="PATH",
                          help="the cited closure document (the closure pins it)")
    register.add_argument("--closure-sha256", metavar="SHA256",
                          help="optional assertion on the closure digest (PD-20)")
    register.add_argument("--resolution", choices=DISPOSITION_RESOLUTIONS,
                          help="the declared disposition of a dispatch (PD-21)")
    register.add_argument("--replaced-by", metavar="PACKET_ID",
                          help="the packet that replaces a `superseded` dispatch (PD-21)")
    register.add_argument("--note", metavar="TEXT")
    register.add_argument("--by", metavar="ROLE")
    metric = commands.add_parser("validate-metric")
    metric.add_argument("--project-root")
    metric.add_argument("--record", required=True)
    status = commands.add_parser(
        "status", help="emit the compact operational view (compact-view-v1, read-only)")
    status.add_argument("--project-root")
    status.add_argument("--max-bytes", type=int, default=DEFAULT_VIEW_MAX_BYTES,
                        help="byte limit for the view (default: 16384)")
    # PD-9/PD-11 (005-013 T2): the READ-ONLY change verdict of the active unit
    # (`current` | `impact` | `impeded`), compared part by part against the
    # registered projection of the last packet of the unit.
    validate_unit = commands.add_parser(
        "validate-unit-contract",
        help="emit the change verdict against the registered unit projection "
             "(change-consequence-v1, read-only)")
    validate_unit.add_argument("--project-root")
    return parser


def _reject_propose_with_prepare_options(args: argparse.Namespace) -> None:
    """--propose-policy is exclusive with ordinary prepare options (spec §2)."""
    # Scalars are "present" when given, even as ""; lists when non-empty.
    scalars = (args.execution_context, args.role, args.substage, args.objective,
               args.expected_output, args.out_dir, args.resume_packet,
               args.replace_packet, args.reason,
               args.reconcile_policy, args.decision_ref, args.record_dispatch,
               args.attempt_id, args.contract_kind, args.contract_path,
               args.plan_version, args.plan_task,
               args.object_kind, args.spec_path, args.spec_version)
    lists = (args.input, args.read_scope, args.write_scope, args.invariant,
             args.evidence)
    if any(value is not None for value in scalars) or any(lists) or args.new_execution:
        raise PolicyError(
            "--propose-policy is exclusive with ordinary prepare options: "
            "--role, --substage, --objective, scopes, inputs and outputs are not accepted")


# A-2/B-3: the prepare sub-modes are mutually exclusive. The MODE is chosen by
# its selector flag; every other option must belong to that same mode, so a
# mixed argv is rejected once, in main and before any lock or write.
_ORDINARY_FLAGS = {
    "--role": lambda a: a.role,
    "--substage": lambda a: a.substage,
    "--objective": lambda a: a.objective,
    "--expected-output": lambda a: a.expected_output,
    "--out-dir": lambda a: a.out_dir,
    "--contract-kind": lambda a: a.contract_kind,
    "--contract-path": lambda a: a.contract_path,
    "--plan-version": lambda a: a.plan_version,
    "--plan-task": lambda a: a.plan_task,
    "--object-kind": lambda a: a.object_kind,
    "--spec-path": lambda a: a.spec_path,
    "--spec-version": lambda a: a.spec_version,
    "--execution-context": lambda a: a.execution_context,
    "--new-execution": lambda a: True if a.new_execution else None,
    "--read-scope": lambda a: a.read_scope or None,
    "--write-scope": lambda a: a.write_scope or None,
    "--invariant": lambda a: a.invariant or None,
    "--evidence": lambda a: a.evidence or None,
    "--input": lambda a: a.input or None,
}
_RECONCILE_FLAGS = {
    "--reconcile-policy": lambda a: a.reconcile_policy,
    "--decision-ref": lambda a: a.decision_ref,
}
# `--record-dispatch` is the record-mode SELECTOR; `--input` is shared with the
# ordinary mode, so it never selects a mode by itself.
_RECORD_FAILING_FLAGS = {
    "--record-dispatch": lambda a: a.record_dispatch,
    "--attempt-id": lambda a: a.attempt_id,
}
_RESUME_FLAGS = {"--resume-packet": lambda a: a.resume_packet}
# `--replace-packet` is the replace-mode SELECTOR; `--reason` belongs to it
# (and is likewise rejected outside it).
_REPLACE_FLAGS = {
    "--replace-packet": lambda a: a.replace_packet,
    "--reason": lambda a: a.reason,
}
# PD-20 (C2): the correction options the replace sub-mode admits (each replaces
# its whole list/field). They are foreign to every other sub-mode.
_REPLACE_CORRECTION_FLAGS = {
    "--input": lambda a: a.input or None,
    "--read-scope": lambda a: a.read_scope or None,
    "--write-scope": lambda a: a.write_scope or None,
    "--invariant": lambda a: a.invariant or None,
    "--expected-output": lambda a: a.expected_output,
    "--evidence": lambda a: a.evidence or None,
}


def _supplied(args: argparse.Namespace, flags: dict) -> list[str]:
    return [flag for flag, get in flags.items() if get(args) is not None]


def _reject_mode_mix(args: argparse.Namespace) -> None:
    """A-2/B-3: exactly one prepare sub-mode may be selected (spec §2).

    The mode is chosen by its selector (`--reconcile-policy`/`--decision-ref`,
    `--record-dispatch`, `--resume-packet`, else ordinary), and any option that
    belongs to a DIFFERENT mode is rejected. `--reconcile-policy` therefore
    admits only `--decision-ref`; `--attempt-id` is rejected outside
    `--record-dispatch`; the ordinary mode accepts role/substage/objective and
    its scopes/inputs. Evaluated once, in main and before the lock, so a mixed
    argv is rejected without any write and without silently discarding an
    operation.
    """
    reconcile = _supplied(args, _RECONCILE_FLAGS)
    record = _supplied(args, _RECORD_FAILING_FLAGS)
    resume = _supplied(args, _RESUME_FLAGS)
    replace = _supplied(args, _REPLACE_FLAGS)
    ordinary = _supplied(args, _ORDINARY_FLAGS)
    selectors = [name for name, flags in (
        ("reconcile", reconcile), ("record", record), ("resume", resume),
        ("replace", replace)) if flags]
    if len(selectors) > 1:
        raise PolicyError(
            "prepare sub-modes are mutually exclusive: reconcile, record, resume and "
            "replace cannot be combined in a single invocation")
    mode = selectors[0] if selectors else "ordinary"
    if mode == "reconcile":
        # `--input` is an ordinary option here (prepare consumes it as the
        # package inputs), so it is foreign to reconcile; only the record mode
        # shares it, where it is the observation document (R-1).
        foreign = ordinary + record + resume + replace
    elif mode == "record":
        # `--input` is shared with the ordinary mode: it is expected here.
        foreign = [f for f in ordinary + reconcile + resume + replace if f != "--input"]
    elif mode == "resume":
        foreign = ordinary + reconcile + record + replace
    elif mode == "replace":
        # `--reason` belongs to replace mode; it must accompany the selector.
        # PD-20 (C2): the correction options also belong to replace mode (they
        # are foreign to every other sub-mode, handled above).
        corrections = set(_REPLACE_CORRECTION_FLAGS)
        foreign = [flag for flag in ordinary + reconcile + record + resume
                   if flag not in corrections]
    else:
        foreign = reconcile + record + resume + replace
    if foreign:
        raise PolicyError(
            f"prepare sub-mode {mode!r} admits no options from another mode; "
            f"unexpected: {', '.join(sorted(foreign))}")


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        if args.project_root is None:
            project_root = Path.cwd().resolve()
        else:
            project_root = _absolute_existing_directory(args.project_root, "--project-root")
        if args.command == "status":
            sys.stdout.buffer.write(status_view(args, project_root))
            return 0
        if args.command == "validate-unit-contract":
            sys.stdout.write(validate_unit_contract(args, project_root))
            return 0
        if args.command == "validate-policy":
            policy_path = _project_path(project_root, POLICY_RELPATH.as_posix(), "policy path")
            policy_document = _load_json(policy_path, "project policy")
            path_policy = _validate_policy_document(policy_document, project_root)
            for raw in args.classify:
                print(f"{raw}\t{classify_path_observable(raw, path_policy, project_root, policy_document['temporary_roots'])}")
            if not args.classify:
                print(f"VALID: policy {POLICY_RELPATH.as_posix()}")
            return 0
        if args.command == "open-unit":
            sys.stdout.write(open_unit(args, project_root))
            return 0
        if args.command == "register-transition":
            sys.stdout.write(register_transition(args, project_root))
            return 0
        if args.command == "prepare":
            if args.propose_policy:
                _reject_propose_with_prepare_options(args)
                sys.stdout.write(propose_policy(project_root))
                return 0
            # A-2/B-3: the sub-modes are mutually exclusive; reject a mixed
            # argv once, here and before the lock or any write.
            _reject_mode_mix(args)
            if args.replace_packet is not None:
                sys.stdout.buffer.write(_replace_packet(args, project_root))
                return 0
            if args.reason is not None:
                raise PolicyError("--reason is only valid with --replace-packet (PD-9)")
            if args.resume_packet:
                sys.stdout.buffer.write(_resume_packet(args, project_root))
                return 0
            if args.reconcile_policy is not None or args.decision_ref is not None:
                if args.reconcile_policy is None or args.decision_ref is None:
                    raise PolicyError(
                        "--reconcile-policy requires both --reconcile-policy <sha256> "
                        "and --decision-ref <ruta>")
                reconcile_policy(args, project_root)
                return 0
            if args.record_dispatch is not None:
                _record_dispatch(args, project_root)
                return 0
            if args.attempt_id is not None:
                raise PolicyError(
                    "--attempt-id is only valid with --record-dispatch")
            sys.stdout.buffer.write(prepare(args, project_root))
            return 0
        if args.command == "validate-metric":
            state = _load_json(project_root / "docs" / ".cdad-state.json", "project state")
            validate_metric(_load_json(Path(args.record), "metric record"), state)
            return 0
        if args.command == "validate-state":
            state = _load_json(project_root / "docs" / ".cdad-state.json", "project state")
            if _validate_idle_coherence(state):
                print(f"VALID: {IDLE_STAGE}")
                return 0
            if args.execution_context:
                execution_document = _load_json(_cwd_path(args.execution_context), "execution context")
            else:
                execution_document, _ = _resolve_active_execution(project_root, state)
            mode = validate_state(execution_document, state, project_root)
            execution = execution_document["execution"]
            if execution_document.get("schema_version") == V2_SCHEMA_VERSION:
                print(f"VALID: execution={execution['id']} feature={execution['feature_id']} "
                      f"model_policy={mode}")
                return 0
            model = execution["model"]
            print(
                "VALID: execution={id} runtime={runtime} scope={scope} authority={authority_ref} "
                "configured_model={configured} reported_model={reported} model_policy={mode}".format(
                    **execution, configured=model.get("configured"), reported=model.get("reported"), mode=mode
                )
            )
            return 0
        execution_path = Path(args.execution_context)
        if not execution_path.is_absolute():
            execution_path = Path.cwd() / execution_path
        execution_document = _load_json(execution_path, "execution context")
        state = _load_json(project_root / "docs" / ".cdad-state.json", "project state")
        if args.command in {"render", "validate-request", "validate-packet"}:
            request = _load_json(Path(args.request), "packet request")
            validate_request(request, execution_document, state, project_root)
            rendered = render_packet(request, execution_document, project_root)
            if args.command == "render":
                sys.stdout.buffer.write(rendered.encode("utf-8"))
            elif args.command == "validate-packet":
                actual = _read_bytes(Path(args.packet), "packet")
                if actual != rendered.encode("utf-8"):
                    raise PolicyError("packet differs from canonical rendering")
            return 0
        raise PolicyError(f"unknown command: {args.command}")
    except PolicyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
