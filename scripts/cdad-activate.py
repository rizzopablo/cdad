#!/usr/bin/env python3
"""Generador de activación CDAD por proyecto (contrato T2, spec 003-006 §2.2).

Emite, bajo ``--project-root``, los archivos de activación git-ignorados de cada
runtime (OpenCode, Claude Code, Codex) apuntando a la raíz aislada adoptada
``--adopted-root``. El conjunto de artefactos es el que declara el
``.cdad-install-manifest.json`` de la raíz adoptada (identidad de versión, R-4):
es determinista, aplica no-clobber con propiedad (R-5) y nunca escribe en las
configuraciones del HOME real.

stdlib solamente.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

RUNTIMES = ("opencode", "claude-code", "codex")

MANIFEST_NAME = ".cdad-install-manifest.json"
REGISTRY_REL = ".cdad/activation.json"
OPENCODE_CONFIG_REL = ".opencode/opencode.jsonc"
OPENCODE_SKILLS_REL = ".config/opencode/skills"
CLAUDE_SKILLS_REL = ".claude/skills"
CODEX_SKILLS_REL = ".agents/skills"
GUARD_SOURCE_REL = ".claude/cdad-scripts/path-guard.sh"
PACKET_CLI_REL = ".claude/skills/cdad-cycle/scripts/cdad_packet.py"
HOOK_TILDE = "~/.claude/cdad-scripts/path-guard.sh"


class ActivationError(Exception):
    """Error de contrato: se reporta y no se escribe nada."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rel_posix(root: str, path: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def path_escape_conflict(project_root: str, path: str) -> str | None:
    """Conflicto B-1 o ``None``: contención de ruta antes de escribir/podar.

    Resuelve con ``realpath`` el directorio contenedor de ``path`` (todos los
    componentes intermedios, incluidos symlinks). Si no queda estrictamente bajo
    ``realpath(project_root)``, hay un componente symlink que escapa de R y no
    se escribe ni se poda nada a través de él.
    """
    root = os.path.realpath(project_root)
    parent = os.path.realpath(os.path.dirname(path))
    if parent == root or parent.startswith(root + os.sep):
        return None
    return (
        f"contención de ruta (B-1): {rel_posix(project_root, path)} resuelve "
        f"fuera de --project-root ({parent})"
    )


def require_file(path: str) -> None:
    if not os.path.isfile(path):
        raise ActivationError(f"falta el archivo requerido en la raíz adoptada: {path}")


def declared(artifacts: dict, prefix: str) -> list[str]:
    """Entradas del manifest bajo ``prefix`` (relativas a la raíz adoptada)."""
    return sorted(rel for rel in artifacts if rel.startswith(prefix))


def skill_names(artifacts: dict, prefix: str) -> list[str]:
    """Nombres de skill declarados por el manifest bajo ``prefix``."""
    names = set()
    for rel in artifacts:
        if not rel.startswith(prefix):
            continue
        rest = rel[len(prefix):]
        if "/" in rest:
            names.add(rest.split("/", 1)[0])
    return sorted(names)


def build_plan(adopted_root: str, runtimes: list[str], artifacts: dict):
    """Devuelve ``(emissions, source_rels)``.

    ``emissions``: [{"rel", "kind": "file"|"symlink", "content"|"target"}].
    ``source_rels``: entradas del manifest que se consumen (verificadas en R-4).
    El plan deriva del manifest: la raíz adoptada define su versión ahí.
    """
    emissions: list[dict] = []
    source_rels: list[str] = []

    def add_source(rel: str) -> None:
        source_rels.append(rel)

    if "opencode" in runtimes:
        prefix = OPENCODE_SKILLS_REL + "/"
        for rel in declared(artifacts, prefix):
            add_source(rel)
        skills_dir = os.path.join(adopted_root, OPENCODE_SKILLS_REL.replace("/", os.sep))
        content = json.dumps(
            {
                "$schema": "https://opencode.ai/config.json",
                "skills": [skills_dir],
            },
            indent=2,
            sort_keys=True,
        ) + "\n"
        emissions.append(
            {
                "rel": OPENCODE_CONFIG_REL,
                "kind": "file",
                "content": content.encode("utf-8"),
            }
        )

    if "claude-code" in runtimes:
        agents_prefix = ".claude/agents/"
        for rel in declared(artifacts, agents_prefix):
            name = rel[len(agents_prefix):]
            if "/" in name or not name.endswith(".md"):
                continue
            add_source(rel)
            with open(os.path.join(adopted_root, rel), "rb") as fh:
                text = fh.read().decode("utf-8")
            # RU-1 (t4-ru1-decision.md): el hook fija CDAD_PACKET_CLI al
            # clasificador de la raíz adoptada antes del guard, de modo que
            # path-guard.sh no lo resuelva desde HOME.
            guard = os.path.join(adopted_root, GUARD_SOURCE_REL)
            packet_cli = os.path.join(adopted_root, PACKET_CLI_REL)
            rewritten = text.replace(
                HOOK_TILDE, f"CDAD_PACKET_CLI={packet_cli} {guard}"
            )
            emissions.append(
                {"rel": rel, "kind": "file", "content": rewritten.encode("utf-8")}
            )

        if GUARD_SOURCE_REL not in artifacts:
            raise ActivationError(
                f"identidad de versión: falta la entrada {GUARD_SOURCE_REL!r} "
                f"en {MANIFEST_NAME}"
            )
        add_source(GUARD_SOURCE_REL)

        prefix = CLAUDE_SKILLS_REL + "/"
        for name in skill_names(artifacts, prefix):
            for rel in declared(artifacts, prefix + name + "/"):
                add_source(rel)
            emissions.append(
                {
                    "rel": CLAUDE_SKILLS_REL + "/" + name,
                    "kind": "symlink",
                    "target": os.path.join(
                        adopted_root, CLAUDE_SKILLS_REL.replace("/", os.sep), name
                    ),
                }
            )

    if "codex" in runtimes:
        prefix = CODEX_SKILLS_REL + "/"
        for name in skill_names(artifacts, prefix):
            for rel in declared(artifacts, prefix + name + "/"):
                add_source(rel)
            emissions.append(
                {
                    "rel": CODEX_SKILLS_REL + "/" + name,
                    "kind": "symlink",
                    "target": os.path.join(
                        adopted_root, CODEX_SKILLS_REL.replace("/", os.sep), name
                    ),
                }
            )

    return emissions, list(dict.fromkeys(source_rels))


def verify_identity(adopted_root: str, source_rels: list[str], artifacts: dict) -> None:
    for rel in source_rels:
        src = os.path.join(adopted_root, rel.replace("/", os.sep))
        if not os.path.isfile(src):
            raise ActivationError(
                f"identidad de versión: falta el archivo {rel!r} en la raíz adoptada"
            )
        record = artifacts.get(rel)
        if not isinstance(record, dict) or not record.get("sha256"):
            raise ActivationError(
                f"identidad de versión: falta la entrada {rel!r} en {MANIFEST_NAME}"
            )
        actual = sha256_file(src)
        if actual != record["sha256"]:
            raise ActivationError(
                f"identidad de versión: sha256 divergente para {rel!r} "
                f"(manifest {record['sha256']}, actual {actual})"
            )


def load_prior_paths(project_root: str) -> dict:
    path = os.path.join(project_root, REGISTRY_REL)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (ValueError, OSError):
        return {}
    if not isinstance(data, dict) or not isinstance(data.get("paths"), dict):
        return {}
    return data["paths"]


def detect_conflict(project_root: str, emission: dict, prior: dict):
    """Mensaje de conflicto o ``None`` si la ruta es escribible (R-5)."""
    dest = os.path.join(project_root, emission["rel"])
    if not os.path.lexists(dest):
        return None
    record = prior.get(emission["rel"])

    if os.path.islink(dest):
        target = os.readlink(dest)
        if emission["kind"] == "symlink" and target == emission["target"]:
            return None
        if (
            isinstance(record, dict)
            and record.get("kind") == "symlink"
            and record.get("target") == target
        ):
            return None
    elif os.path.isfile(dest) and emission["kind"] == "file":
        with open(dest, "rb") as fh:
            if fh.read() == emission["content"]:
                return None
        if (
            isinstance(record, dict)
            and record.get("kind") == "file"
            and record.get("sha256") == sha256_file(dest)
        ):
            return None

    return (
        f"destino en conflicto: {emission['rel']} "
        "(existe y difiere de lo que se emitiría)"
    )


def prune_candidates(project_root: str, prior: dict, planned_rels: set[str]) -> list[str]:
    """Rutas propias registradas que ya no se emiten y siguen intactas."""
    out: list[str] = []
    for rel in sorted(prior):
        if rel in planned_rels:
            continue
        record = prior[rel]
        dest = os.path.join(project_root, rel)
        if not isinstance(record, dict) or not os.path.lexists(dest):
            continue
        if (
            record.get("kind") == "symlink"
            and os.path.islink(dest)
            and os.readlink(dest) == record.get("target")
        ):
            out.append(dest)
        elif (
            record.get("kind") == "file"
            and os.path.isfile(dest)
            and not os.path.islink(dest)
            and record.get("sha256") == sha256_file(dest)
        ):
            out.append(dest)
    return out


def write_emission(project_root: str, emission: dict) -> None:
    dest = os.path.join(project_root, emission["rel"])
    parent = os.path.dirname(dest)
    if parent:
        os.makedirs(parent, exist_ok=True)
    if os.path.lexists(dest):
        os.unlink(dest)
    if emission["kind"] == "file":
        with open(dest, "wb") as fh:
            fh.write(emission["content"])
    else:
        os.symlink(emission["target"], dest)


def build_registry(adopted_root: str, manifest_sha: str, emissions: list[dict]) -> bytes:
    paths: dict = {}
    for emission in emissions:
        if emission["kind"] == "file":
            paths[emission["rel"]] = {
                "kind": "file",
                "sha256": sha256_bytes(emission["content"]),
            }
        else:
            paths[emission["rel"]] = {
                "kind": "symlink",
                "target": emission["target"],
            }
    payload = {
        "adopted_root": adopted_root,
        "manifest_sha256": manifest_sha,
        "paths": paths,
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_registry(project_root: str, content: bytes) -> None:
    dest = os.path.join(project_root, REGISTRY_REL)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(content)
    os.replace(tmp, dest)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Genera la activación CDAD por proyecto apuntando a la raíz adoptada."
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--adopted-root", required=True)
    parser.add_argument("--runtime", action="append", choices=RUNTIMES, default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    # O-4: resolver las raíces a realpath en la validación de argumentos, de
    # modo que ortografías relativa/absoluta/vía-symlink produzcan bytes
    # idénticos (P2) y que la contención B-1 compare contra la raíz real.
    project_root = os.path.realpath(args.project_root)
    adopted_root = os.path.realpath(args.adopted_root)
    runtimes = list(dict.fromkeys(args.runtime)) or list(RUNTIMES)

    try:
        if not os.path.isdir(project_root):
            raise ActivationError(f"--project-root no es un directorio: {project_root}")
        if not os.path.isdir(adopted_root):
            raise ActivationError(f"--adopted-root no es un directorio: {adopted_root}")
        manifest_path = os.path.join(adopted_root, MANIFEST_NAME)
        require_file(manifest_path)
        with open(manifest_path, "rb") as fh:
            manifest_raw = fh.read()
        manifest_sha = sha256_bytes(manifest_raw)
        manifest = json.loads(manifest_raw.decode("utf-8"))
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, dict):
            raise ActivationError(
                f"manifest inválido: falta el mapa 'artifacts' en {MANIFEST_NAME}"
            )

        emissions, sources = build_plan(adopted_root, runtimes, artifacts)
        verify_identity(adopted_root, sources, artifacts)
    except ActivationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    prior = load_prior_paths(project_root)
    planned_rels = {emission["rel"] for emission in emissions}

    # B-1: la contención se comprueba antes de cualquier escritura o poda. Un
    # componente symlink que salga de R es conflicto nombrado y aborta todo.
    conflicts: list[str] = []
    for emission in emissions:
        dest = os.path.join(project_root, emission["rel"])
        escape = path_escape_conflict(project_root, dest)
        if escape is not None:
            conflicts.append(escape)
            continue
        message = detect_conflict(project_root, emission, prior)
        if message is not None:
            conflicts.append(message)

    prunes = prune_candidates(project_root, prior, planned_rels)
    for path in prunes:
        escape = path_escape_conflict(project_root, path)
        if escape is not None:
            conflicts.append(escape)

    registry_escape = path_escape_conflict(
        project_root, os.path.join(project_root, REGISTRY_REL)
    )
    if registry_escape is not None:
        conflicts.append(registry_escape)

    if args.dry_run:
        for emission in emissions:
            print(f"would write {emission['rel']}")
        for path in prunes:
            print(f"would remove {rel_posix(project_root, path)}")
        for message in sorted(conflicts):
            print(f"conflict {message}", file=sys.stderr)
        return 1 if conflicts else 0

    if conflicts:
        for message in sorted(conflicts):
            print(f"error: {message}", file=sys.stderr)
        print("error: no se escribió nada (todo o nada)", file=sys.stderr)
        return 1

    for emission in emissions:
        write_emission(project_root, emission)
    for path in prunes:
        os.unlink(path)
    write_registry(project_root, build_registry(adopted_root, manifest_sha, emissions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
