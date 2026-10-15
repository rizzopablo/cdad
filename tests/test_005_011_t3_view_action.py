#!/usr/bin/env python3
"""005-011 T3 RED — versión y siguiente acción en la vista (PD-4, PD-5).

Contract:
- docs/specs/005-011-common-entry/spec.md §2.3 (`view-action-v1`), §3 PD-4/PD-5,
  §5 AC-4/AC-5, §4 INV-5.
- docs/specs/005-011-common-entry/plan.md §4 (T3) y el plan del epic-005 (fila
  11) que supersede C4 de 005-003.

Superficie observable bajo prueba (caja negra: SOLO subprocess; el módulo
NUNCA se importa y la implementación NUNCA se lee al escribir este test):

    python3 <skill-dir>/scripts/cdad_packet.py status --project-root <raíz>

El oráculo es el comportamiento observable: la vista `status` invocada como
subproceso sobre proyectos fixture en directorios temporales (state + política
propios, manifiesto de agentes derivados e instalación simulada cuando el caso
lo exige), leyendo su salida JSON y su `rc`.

**Instalación simulada.** El bloque `version` de la vista sale del chequeo de
versión, que lee el marcador de la instalación (`version.txt`) del árbol donde
vive el CLI; el checkout del repo no tiene marcador (sería `UNKNOWN` siempre).
Para los casos de `DRIFT` el fixture **simula la instalación**: copia el árbol
`skills/` a un tempdir, escribe su marcador y sus agentes derivados, e invoca
el CLI **copiado** — nunca toca el repo. El fixture se autocontiene (tempdirs,
HOME aislado en un tempdir vacío; sin datos de demo, sin la base real de
sesiones, sin rutas de este host).

**Fallo RED.** Los casos que dependen del cambio fallan por **AssertionError**
de contrato sobre la salida observable (la pata que diverge, la resolución, la
ruta de `next`, `entry`), jamás por ImportError, SyntaxError, JSONDecodeError
ni error de setup; los controles de no-regresión quedan verdes.

Mapeo test → postcondición/criterio (uno por afirmación observable):
  test_pd4_project_leg_drift_names_leg_and_resolution
      -> PD-4 / AC-4: con la pata `project` divergiendo (derivados del proyecto
         anteriores a la instalación; agents/CLI coincidentes) la vista NOMBRA
         la pata que diverge y dice QUÉ LO RESUELVE (el próximo `prepare`
         republica los derivados). HOY no nombra ninguna pata ni la resolución.
  test_pd4_non_project_leg_drift_names_leg_without_prepare_promise
      -> PD-4 / AC-4 borde: con una pata que NO es `project` (agents ≠ CLI)
         la vista nombra la pata y NO promete la resolución del `prepare`
         (afirmarla sería inventar). HOY no nombra la pata.
  test_pd4_absence_is_distinguished_from_incoherence_without_resolution
      -> PD-4 / AC-4: `UNKNOWN` (marca faltante) y `NO-PROJECT-AGENTS` son
         AUSENCIA: no llevan cláusula de resolución y se distinguen de `DRIFT`
         (hoy la causa es idéntica en forma: el veredicto y su rc son el único
         diferencial). La discriminación falla hoy por aserción.
  test_pd5_prepared_packet_route_names_dispatch_action
      -> PD-5 / AC-5: con `active_packet.status == "prepared"` la ruta
         `next.route` nombra la ACCIÓN NATURAL (despacharlo) con
         `--replace-packet` como rama condicional, y `entry` sigue siendo
         `continuity-reconcile`. HOY la ruta es el texto anterior
         «reconcile the pending packet…» (no nombra el despacho).
  test_pd5_dispatched_packet_keeps_reconcile_route
      -> PD-5 / AC-5 control de no-regresión: con `dispatched` se CONSERVA la
         ruta de reconciliación antes de repetir y `entry` sigue siendo
         `continuity-reconcile`; la ruta de `dispatched` difiere de la de
         `prepared`.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import (
    build_project,
    prepare_args,
    read_state,
    write_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
# Superficie declarada por la spec §2.3: `python3 <skill-dir>/scripts/cdad_packet.py status`.
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
SKILLS_TREE = REPO_ROOT / "skills"
MANIFEST_REL = ".opencode/agents/.cdad-derived.json"
CLI_TIMEOUT_S = 60

# Versiones sintéticas de fixture: opacas, distintas entre sí y sin subcadenas
# que se confundan con una declaración de ausencia.
INSTALL_VERSION = "aaa11111"  # marcador de la instalación simulada
OLDER_VERSION = "bbb22222"  # derivados del proyecto, una instalación atrás
OTHER_VERSION = "ccc33333"  # una segunda instalación (pata `agents`)

# Campos de la proyección que esta tarea necesita (contrato de §2.1 de 005-003,
# referenciado por la spec §2.3).
REQUIRED_TOP = ("project", "version", "next", "entry")

# La acción natural de un `prepared` es despacharlo (spec §2.3 c2: validar →
# `begin` → `--record-dispatch`). Ancla estructural: un token del despacho, no
# el sentido de la prosa (INV-5).
DISPATCH_ACTION = re.compile(r"--record-dispatch|\bdispatch(?:es|ed|ing)?\b", re.I)
# La resolución verificada de un `DRIFT` con la pata `project` es el próximo
# `prepare` (spec §2.3 c1); el sentido exacto de la prosa lo juzga la review.
PREPARE_RESOLUTION = re.compile(r"(?<![\w-])prepare(?![\w-])", re.I)
LEGS = ("project", "agents", "CLI", "claude-code")


# ---------------------------------------------------------------- helpers


def _assert_no_marker_ancestor(path: Path) -> None:
    """Setup: ninguna raíz por encima del fixture trae `version.txt`.

    El chequeo de versión resuelve el marcador de la instalación subiendo desde
    el árbol donde vive el CLI; un `version.txt` ajeno en un ancestro del
    tempdir volvería no determinista el caso de ausencia (`UNKNOWN`).
    """
    for ancestor in [path, *path.parents]:
        marker = ancestor / "version.txt"
        assert not marker.exists(), (
            "fixture: hay un marcador de versión ajeno en un ancestro del "
            f"tempdir ({marker}); el caso de ausencia no sería determinista"
        )


class _Fixture:
    """Proyecto sintético autocontenido en un tempdir, con HOME aislado."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        build_project(self.root)

    def env(self) -> dict:
        env = {k: v for k, v in os.environ.items() if not k.startswith("CDAD_")}
        env["HOME"] = str(self.home)  # NUNCA el HOME real
        env.pop("XDG_CONFIG_HOME", None)
        return env

    def run(self, argv: list[str], *, cli: Path = CLI,
            cwd: Path | None = None) -> subprocess.CompletedProcess:
        assert cli.is_file(), f"CLI ausente: {cli}"
        return subprocess.run(
            [sys.executable, str(cli), *argv],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT if cwd is None else cwd), env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
        )

    def status(self, *, cli: Path = CLI) -> subprocess.CompletedProcess:
        return self.run(["status", "--project-root", str(self.root)], cli=cli)

    def prepare(self, *, objective: str = "005-011 T3 fixture"
                ) -> subprocess.CompletedProcess:
        return self.run(prepare_args(self.root, objective=objective))

    def write_manifest(self, *, source_dir: Path, source_version: str) -> None:
        """Manifiesto de agentes derivados del proyecto (pata `project`)."""
        path = self.root / MANIFEST_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "schema_version": 1,
            "source_version": source_version,
            "source_dir": str(source_dir),
            "agents": {},
        }), encoding="utf-8")

    def remove_manifest(self) -> None:
        (self.root / MANIFEST_REL).unlink()

    def simulated_install(self, *, version: str | None, name: str) -> Path:
        """Instalación simulada en un tempdir: copia del árbol `skills/`.

        `version=None` deja la instalación **sin** marcador (`version.txt`) —
        el caso de AUSENCIA (`UNKNOWN`). Devuelve la raíz de instalación.
        """
        install = self.base / name
        shutil.copytree(SKILLS_TREE, install / "skills", symlinks=True)
        agents = install / ".config" / "opencode" / "agents"
        agents.mkdir(parents=True, exist_ok=True)
        if version is not None:
            (install / "version.txt").write_text(
                version + "\n", encoding="utf-8")
        else:
            _assert_no_marker_ancestor(install)
        return install


@pytest.fixture
def fx(tmp_path: Path) -> _Fixture:
    return _Fixture(tmp_path)


def install_cli(install: Path) -> Path:
    """El CLI dentro de la instalación simulada (su árbol define la pata CLI)."""
    return install / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"


def install_agents(install: Path) -> Path:
    """El directorio de agentes derivados de la instalación simulada."""
    return install / ".config" / "opencode" / "agents"


def _status_doc(proc: subprocess.CompletedProcess) -> dict:
    """El único documento JSON de la vista, o AssertionError de contrato.

    Nunca deja escapar un JSONDecodeError (fallo de setup): si la vista no
    emitió el documento del contrato, la aserción lo declara.
    """
    assert proc.returncode == 0, (
        "PD-4/PD-5 violadas: la vista `status` debe emitir la proyección "
        f"(rc=0); hoy rc={proc.returncode}; stderr={proc.stderr.strip()!r}"
    )
    assert proc.stdout.strip(), (
        "PD-4/PD-5 violadas: la vista no emitió el documento por stdout; "
        f"stderr={proc.stderr.strip()!r}"
    )
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "PD-4/PD-5 violadas: stdout no es un ÚNICO documento JSON válido: "
            f"{proc.stdout[:200]!r}"
        ) from exc
    assert isinstance(doc, dict), (
        f"PD-4/PD-5 violadas: la proyección no es un objeto JSON: {doc!r}"
    )
    missing = [k for k in REQUIRED_TOP if k not in doc]
    assert not missing, (
        "PD-4/PD-5 violadas: la proyección no trae los campos del contrato: "
        f"faltan {missing}; documento: {sorted(doc)}"
    )
    return doc


def _version_block(doc: dict) -> dict:
    """El bloque `version` de la vista (extensión aditiva de 005-003 §2.4).

    Los campos existentes (`verdict`/`verified`/`cause`) se conservan.
    """
    block = doc["version"]
    assert isinstance(block, dict), (
        f"PD-4 violada: `version` no es un objeto: {block!r}"
    )
    assert "verdict" in block and "verified" in block, (
        "PD-4/PD-6 violadas: el bloque `version` no conserva los campos "
        f"existentes (`verdict`/`verified`): {sorted(block)}"
    )
    return block


def _strings(value: object):
    """Todas las cadenas de un valor JSON, recursivamente."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _strings(item)


def _block_text(block: dict, *, exclude: tuple[str, ...] = ("verdict",)) -> str:
    """Texto del bloque `version`, sin las claves excluidas.

    El veredicto se excluye porque sus literales contienen nombres de pata
    (`NO-PROJECT-AGENTS`) y confundirían la lectura de la pata que diverge.
    """
    parts: list[str] = []
    for key, value in block.items():
        if key in exclude:
            continue
        parts.extend(_strings(value))
    return " ".join(parts)


def _names_leg(block: dict, leg: str) -> bool:
    """¿El bloque `version` nombra esta pata como token aislado?"""
    return re.search(
        rf"(?i)(?<![\w-]){re.escape(leg)}(?![\w-])", _block_text(block)
    ) is not None


def _promises_prepare_resolution(block: dict) -> bool:
    """¿El bloque `version` afirma la resolución del `prepare`?"""
    return PREPARE_RESOLUTION.search(_block_text(block)) is not None


def _normalized_form(block: dict) -> str:
    """Forma del bloque sin el veredicto ni su `rc`.

    Hoy la causa es idéntica en forma entre AUSENCIA (`UNKNOWN`/
    `NO-PROJECT-AGENTS`) e INCOHERENCIA (`DRIFT`): el veredicto y el `rc` son
    el único diferencial. La discriminación exige un diferencial más.
    """
    text = _block_text(block)
    text = re.sub(r"(?i)\b(?:COHERENT|DRIFT|UNKNOWN|NO-PROJECT-AGENTS)\b",
                  "<verdict>", text)
    text = re.sub(r"(?i)\brc\s*=?\s*\d+", "<rc>", text)
    return text


def _next_route(doc: dict) -> str:
    route = (doc["next"] or {}).get("route")
    assert isinstance(route, str) and route.strip(), (
        f"PD-5 violada: `next.route` vacío o ausente: {doc['next']!r}"
    )
    return route


# ---------------------------------------------------------------- PD-4


def test_pd4_project_leg_drift_names_leg_and_resolution(fx: _Fixture) -> None:
    """PD-4/AC-4: ante un `DRIFT` con la pata `project` divergiendo (agentes
    derivados del proyecto con la versión anterior a la instalación; `agents` y
    `CLI` coincidentes entre sí) la vista NOMBRA la pata que diverge y dice
    QUÉ LO RESUELVE: el próximo `prepare` republica los derivados del proyecto.

    HOY la vista no nombra ninguna pata ni la resolución (sólo el veredicto y
    su `rc`): las aserciones sobre la pata y la resolución fallan por
    AssertionError."""
    install = fx.simulated_install(version=INSTALL_VERSION, name="install")
    fx.write_manifest(source_dir=install_agents(install),
                      source_version=OLDER_VERSION)

    doc = _status_doc(fx.status(cli=install_cli(install)))
    block = _version_block(doc)
    assert block["verdict"] == "DRIFT", (
        "fixture: la pata `project` debe divergir de la instalación "
        f"(derivados {OLDER_VERSION!r} vs {INSTALL_VERSION!r}); veredicto: "
        f"{block['verdict']!r} — {block.get('cause')!r}"
    )

    assert _names_leg(block, "project"), (
        "PD-4 violada: con un `DRIFT` de la pata `project` la vista no nombra "
        "la pata que diverge (debe leerla del chequeo, no inferirla): "
        f"version={block!r}"
    )
    assert _promises_prepare_resolution(block), (
        "PD-4 violada: con la pata `project` divergiendo la vista no dice qué "
        "lo resuelve (el próximo `prepare` republica los derivados del "
        f"proyecto): version={block!r}"
    )


def test_pd4_non_project_leg_drift_names_leg_without_prepare_promise(
        fx: _Fixture) -> None:
    """PD-4/AC-4 borde: con una pata que NO es `project` divergiendo (`agents`
    contra `CLI`, con la pata `project` coincidente con la instalación) la
    vista nombra la pata y **no** promete la resolución del `prepare`: afirmar
    esa resolución sería inventar (la resolución verificada es sólo de la pata
    `project`).

    HOY la vista no nombra la pata: la aserción sobre el nombre falla por
    AssertionError (y la ausencia de promesa es el control)."""
    install = fx.simulated_install(version=INSTALL_VERSION, name="install")
    other = fx.simulated_install(version=OTHER_VERSION, name="other-install")
    # La pata `project` coincide con la instalación (CLI); `agents` sale de otra
    # instalación y diverge.
    fx.write_manifest(source_dir=install_agents(other),
                      source_version=INSTALL_VERSION)

    doc = _status_doc(fx.status(cli=install_cli(install)))
    block = _version_block(doc)
    assert block["verdict"] == "DRIFT", (
        "fixture: la pata `agents` debe divergir del CLI "
        f"({OTHER_VERSION!r} vs {INSTALL_VERSION!r}); veredicto: "
        f"{block['verdict']!r} — {block.get('cause')!r}"
    )

    assert _names_leg(block, "agents"), (
        "PD-4 violada: con un `DRIFT` de la pata `agents` la vista no nombra la "
        f"pata que diverge: version={block!r}"
    )
    assert not _promises_prepare_resolution(block), (
        "PD-4 violada: con una pata que NO es `project` la vista promete la "
        "resolución del `prepare` (inventa: esa resolución sólo está verificada "
        f"para la pata `project`): version={block!r}"
    )


def test_pd4_absence_is_distinguished_from_incoherence_without_resolution(
        fx: _Fixture) -> None:
    """PD-4/AC-4: la AUSENCIA (`UNKNOWN` por marca faltante y
    `NO-PROJECT-AGENTS` por falta de derivados) no lleva cláusula de resolución
    y se DISTINGUE de la INCOHERENCIA (`DRIFT`).

    HOY la causa es idéntica en forma entre ausencia e incoherencia (sólo
    cambian el veredicto y su `rc`), así que la aserción de discriminación
    falla por AssertionError; las ausencias sin resolución son los controles."""
    # UNKNOWN: instalación sin marcador, con manifiesto presente.
    no_marker = fx.simulated_install(version=None, name="install-no-marker")
    fx.write_manifest(source_dir=install_agents(no_marker),
                      source_version=INSTALL_VERSION)
    unknown = _version_block(_status_doc(fx.status(cli=install_cli(no_marker))))

    # NO-PROJECT-AGENTS: instalación con marcador, sin manifiesto derivado.
    with_marker = fx.simulated_install(version=INSTALL_VERSION,
                                       name="install-with-marker")
    fx.remove_manifest()
    no_agents = _version_block(_status_doc(fx.status(cli=install_cli(with_marker))))

    # INCOHERENCIA verificada: pata `project` divergiendo.
    drift_install = fx.simulated_install(version=INSTALL_VERSION,
                                         name="install-drift")
    fx.write_manifest(source_dir=install_agents(drift_install),
                      source_version=OLDER_VERSION)
    drift = _version_block(_status_doc(fx.status(cli=install_cli(drift_install))))

    assert unknown["verdict"] == "UNKNOWN", (
        f"fixture: sin marcador el veredicto debe ser UNKNOWN: {unknown!r}"
    )
    assert no_agents["verdict"] == "NO-PROJECT-AGENTS", (
        "fixture: sin derivados el veredicto debe ser NO-PROJECT-AGENTS: "
        f"{no_agents!r}"
    )
    assert drift["verdict"] == "DRIFT", (
        f"fixture: con la pata `project` divergiendo el veredicto debe ser "
        f"DRIFT: {drift!r}"
    )

    # La ausencia no afirma resolución (controles).
    for label, block in (("UNKNOWN", unknown), ("NO-PROJECT-AGENTS", no_agents)):
        assert block["verified"] is False, (
            f"PD-4 violada: la ausencia ({label}) no se surfacea como no "
            f"verificada: {block!r}"
        )
        assert not _promises_prepare_resolution(block), (
            f"PD-4 violada: la ausencia ({label}) lleva una cláusula de "
            f"resolución (la causa de ausencia no la lleva): {block!r}"
        )

    # Discriminación (lo que depende del cambio): la incoherencia verificada se
    # distingue de la ausencia por algo más que el veredicto y su `rc`.
    for label, block in (("UNKNOWN", unknown), ("NO-PROJECT-AGENTS", no_agents)):
        assert _normalized_form(block) != _normalized_form(drift), (
            "PD-4 violada: la vista no distingue la AUSENCIA "
            f"({label}) de la INCOHERENCIA: ambas causas son idénticas en "
            "forma (sólo cambian el veredicto y su `rc`); la incoherencia "
            "verificada debe nombrar la pata y su resolución — "
            f"ausencia={block!r} drift={drift!r}"
        )


# ---------------------------------------------------------------- PD-5


def test_pd5_prepared_packet_route_names_dispatch_action(fx: _Fixture) -> None:
    """PD-5/AC-5: con `active_packet.status == "prepared"` la ruta `next.route`
    nombra la ACCIÓN NATURAL —despacharlo— con `--replace-packet` como rama
    condicional, y `entry` sigue siendo `continuity-reconcile`.

    HOY la ruta es el texto anterior «reconcile the pending packet
    (--replace-packet if the contract changed)», que no nombra el despacho: la
    aserción sobre la acción natural falla por AssertionError."""
    prepared = fx.prepare()
    assert prepared.returncode == 0, (
        "fixture: `prepare` del proyecto sintético debe tener éxito; "
        f"rc={prepared.returncode}; stderr={prepared.stderr.strip()!r}"
    )

    doc = _status_doc(fx.status())
    assert doc["packet"]["status"] == "prepared", (
        f"fixture: el paquete activo no quedó `prepared`: {doc['packet']!r}"
    )
    assert doc["entry"] == "continuity-reconcile", (
        "PD-5 violada: con un paquete `prepared` la entrada debe seguir siendo "
        f"`continuity-reconcile` (el mapa de `entry` no cambia): {doc['entry']!r}"
    )

    route = _next_route(doc)
    assert DISPATCH_ACTION.search(route), (
        "PD-5 violada: la ruta de un paquete `prepared` no nombra la acción "
        "natural (despacharlo: validar → `begin` → `--record-dispatch`): "
        f"{route!r}"
    )
    assert "--replace-packet" in route, (
        "PD-5 violada: la ruta de un paquete `prepared` no conserva "
        "`--replace-packet` como rama condicional (contrato cambiado): "
        f"{route!r}"
    )


def test_pd5_dispatched_packet_keeps_reconcile_route(fx: _Fixture) -> None:
    """PD-5/AC-5 control de no-regresión: con `active_packet.status ==
    "dispatched"` se CONSERVA la ruta de reconciliación antes de repetir y
    `entry` sigue siendo `continuity-reconcile`; además la ruta de `dispatched`
    difiere de la de `prepared` (no se colapsan en un solo texto)."""
    prepared = fx.prepare()
    assert prepared.returncode == 0, (
        "fixture: `prepare` del proyecto sintético debe tener éxito; "
        f"rc={prepared.returncode}; stderr={prepared.stderr.strip()!r}"
    )
    route_prepared = _next_route(_status_doc(fx.status()))

    state = read_state(fx.root)
    state["active_packet"]["status"] = "dispatched"
    write_state(fx.root, state)

    doc = _status_doc(fx.status())
    assert doc["packet"]["status"] == "dispatched", (
        f"fixture: el paquete activo no quedó `dispatched`: {doc['packet']!r}"
    )
    assert doc["entry"] == "continuity-reconcile", (
        "PD-5 violada: con un paquete `dispatched` la entrada debe seguir "
        f"siendo `continuity-reconcile`: {doc['entry']!r}"
    )

    route = _next_route(doc)
    assert re.search(r"(?i)\breconcil", route), (
        "PD-5 violada: la ruta de un paquete `dispatched` no conserva la "
        f"reconciliación: {route!r}"
    )
    assert re.search(r"(?i)\b(?:repeat|resume)\b", route), (
        "PD-5 violada: la ruta de un paquete `dispatched` no conserva la "
        f"reconciliación ANTES DE REPETIR: {route!r}"
    )
    assert route != route_prepared, (
        "PD-5 violada: la ruta de `dispatched` y la de `prepared` son el mismo "
        f"texto (deben diferir): {route!r}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
