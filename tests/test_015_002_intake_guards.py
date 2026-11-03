#!/usr/bin/env python3
"""RED 015-002-intake-guards — guardas de admisión (D1+D2+D3).

Contract:
- docs/specs/015-002-intake-guards/spec.md, aprobada (D1 y D2 y D3
  aprobados expresamente; decisión §4 de test-audit.md).
- PC-01: observación de despacho incompatible → rechaza identificando
  campo/problema, formato esperado y ejemplo JSON con las seis claves
  (runtime/model_configured/model_reported/session/started_at/provenance;
  nulls si no observados). El ejemplo no autoriza inventar.
- PC-02: decisions de begin → conserva rechazo, señala decisions/elemento,
  incluye forma esperada y ejemplo `[{"decision":"…","rationale":"…"}]`.
- PC-03: write scope malformado → identifica la opción, exige
  CLASS=SELECTOR no vacíos, incluye ejemplo
  (`--write-scope implementation=skills`). No convierte repository-read
  en escritura.
- PC-04: nuevo begin con referencia contract cubierta sigue rechazándose
  pre-persistencia; ofrece estrechar scope o living solo cuando corresponda.
- PC-05: continuity.md documenta el caso `docs=docs` (límite: carpeta del
  contrato; ejemplo living mutable; contract fuera de scope admitido;
  living explícito admitido; sin reclasificación automática; sin atajos).
- PC-06: open-unit omite queued de epic cerrado y abre la primera elegible,
  conservando orden; omitida e historia intactas.
- PC-07: `--feature <ID>` de unidad excluida rechaza nombrando unidad y
  epic, sin abrir ni persistir.
- PC-08: solo excluidas → informa sin candidata, sin ejecución ni cambios;
  fuente bloqueante → identifica fuente y motivo.
- PC-09: apertura compatible conserva reposo/dependencias/autoridad/vigencia
  y atomicidad; validate-state acepta. project-start.md: «primera queued»
  = primera elegible; --feature no elude cierre.

Oráculo caja negra: CLIs públicos (`scripts/cdad_packet.py`,
`scripts/cdad_continuity.py` vía wrappers delegados del repo;
`skills/cdad-cycle/scripts/cdad_packet.py`, el mismo de
tests/test_005_007_t3_open_unit.py) sobre proyectos sintéticos
descartables en tempdirs. Nunca se editan `skills/` ni `scripts/` reales;
ningún módulo de producto se importa; ningún archivo de implementación
se lee. La parte semántica de PC-05 (revisión independiente de la guía)
es no-mecánica y se declara como tal en Añ-E: aquí solo se verifica la
presencia mecánica mínima de la guía.

Cobertura (un bloque por promesa observable A–I; cada test declara su
"sin este test"):

- Añ-A (PC-01): observación incompatible explica campo/problema + formato
  + ejemplo seis claves.
- Añ-B (PC-02): decisions conserva rechazo + señala elemento + forma
  esperada + ejemplo objeto.
- Añ-C (PC-03): write-scope malformado identifica opción + exige
  CLASS=SELECTOR no vacíos + ejemplo; no convierte read en escritura.
- Añ-D (PC-04): begin con contract cubierta sigue rechazado
  pre-persistencia + ofrece estrechar scope / living cuando corresponda.
- Añ-E (PC-05, mecánica mínima): la guía del caso `docs=docs` está
  presente en continuity.md. El resto (coherencia semántica de la guía)
  es revisión independiente, no mecánica: se declara, no se finge cubrir.
- Añ-F (PC-06): open-unit omite queued de epic cerrado, abre primera
  elegible, orden conservado, intactas.
- Añ-G (PC-07): --feature de excluida rechaza nombrando unidad+epic, sin
  abrir ni persistir.
- Añ-H (PC-08): solo excluidas → sin candidata sin ejecución/cambios.
- Añ-I (PC-09): apertura elegible conserva garantías + validate-state
  acepta + project-start.md documenta «primera elegible».

RED hoy (sondas declaradas en el encargo): los diagnósticos actuales no
traen ejemplo/forma/guía; `open-unit` selecciona la primera queued sin
considerar cierres de epics; continuity.md no menciona `docs=docs` ni
`write-scope`; project-start.md no dice «elegible». Cada test falla en la
ASERCIÓN sobre el comportamiento del contrato, nunca en la invocación ni
en una precondición de fixture.

RED (paquete): corre solo este archivo, en primer plano:
    env -u TMPDIR python3 -m pytest -q tests/test_015_002_intake_guards.py < /dev/null
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import test_004_002_t2_bootstrap as b
from test_007_002_dispatch_recovery import (
    CONTINUITY_CLI,
    PACKET_CLI,
    REPO_ROOT,
    _RecoveryProject,
)
from test_008_004_packet_enforcement import _begin

CLI_TIMEOUT_S = 120

CLOSED_EPIC = "epic-015-guards-cerrado"
OPEN_EPIC = "epic-015-guards-abierto"
UNIT_CLOSED = "015-901-cerrada"
UNIT_OPEN = "015-902-abierta"

CONTINUITY_MD = (REPO_ROOT / "skills" / "cdad-cycle" / "references"
                 / "continuity.md")
PROJECT_START_MD = (REPO_ROOT / "skills" / "cdad-cycle" / "references"
                    / "project-start.md")


# ---------------------------------------------------------------- helpers


def _run_cli(script: Path, args: list[str], home: Path
             ) -> subprocess.CompletedProcess:
    """Corrida caja negra con HOME aislado (nunca el HOME real)."""
    assert script.is_file(), f"CLI del repo ausente: {script}"
    env = dict(os.environ)
    env["HOME"] = str(home)
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, cwd=REPO_ROOT, env=env,
        stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
    )


def _open_unit_project(base: Path, queued: list[str]) -> tuple[Path, Path]:
    """Proyecto en reposo con cola `queued`, cierre del epic CLOSED_EPIC y
    cada plan declarando solo su propia unidad (una fila estructural por
    plan; sin ambigüedad entre planes tras el fix F1 de 015-002).

    Precondición (comportamiento existente, verificado por sonda): el reposo
    con la entrada de cierre es coherente hoy (validate-state rc=0) y
    `open-unit` abre hoy la primera queued sin mirar cierres.
    """
    home = base / "home"
    home.mkdir(parents=True, exist_ok=True)
    root = base / "proj"
    b.build_project(root)
    proc = _run_cli(PACKET_CLI, [
        "prepare", "--project-root", str(root),
        "--role", "test-writer", "--substage", "red",
        "--objective", "015-002 RED: reposo con cierre de epic",
    ], home)
    assert proc.returncode == 0, (
        "precondición (fixture, comportamiento existente): `prepare` debe "
        f"publicar la ejecución (rc=0): {proc.stdout!r} {proc.stderr!r}")
    state = b.read_state(root)
    for fid in (UNIT_CLOSED, UNIT_OPEN):
        data = f"# Spec fixture ({fid})\n".encode()
        path = root / f"docs/specs/{fid}/spec.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        state.setdefault("stage_history", []).append({
            "feature": fid,
            "stage": "specification",
            "approved_by": "Pablo",
            "approved_at": "2026-11-02T00:00:00Z",
            "contract_path": f"docs/specs/{fid}/spec.md",
            "contract_sha256": hashlib.sha256(data).hexdigest(),
        })
    for epic, fid in ((CLOSED_EPIC, UNIT_CLOSED),
                       (OPEN_EPIC, UNIT_OPEN)):
        epic_dir = root / f"docs/epics/{epic}"
        epic_dir.mkdir(parents=True, exist_ok=True)
        (epic_dir / "plan.md").write_text(
            f"# Plan fixture ({epic})\n\n## Entregas\n\n"
            f"| Orden | Feature | Estado | Depende de |\n"
            f"|---|---|---|---|\n"
            f"| 1 | {fid} — unidad del fixture | queued | — |\n"
            f"\n## Cambios\n\n- alta del fixture\n",
            encoding="utf-8")
        (epic_dir / "execution.md").write_text(
            f"# Autoridad del fixture ({epic})\n", encoding="utf-8")
    state["epic_history"] = [{
        "epic": CLOSED_EPIC,
        "epic_id": CLOSED_EPIC,
        "stage": "epic-closure",
        "approved_by": "Pablo",
        "approved_at": "2026-11-02T00:00:00Z",
    }]
    state["epic_features"] = [{"id": fid, "status": "queued"}
                              for fid in queued]
    state["active_feature"] = None
    state["current_stage"] = "idle"
    state["tdd_substage"] = None
    state["active_packet"] = None
    b.write_state(root, state)
    valid = _run_cli(PACKET_CLI,
                     ["validate-state", "--project-root", str(root)], home)
    assert valid.returncode == 0, (
        "precondición (fixture, comportamiento existente): el reposo con "
        f"cola y cierre debe ser coherente hoy: "
        f"{valid.stdout!r} {valid.stderr!r}")
    return root, home


def _tree(root: Path) -> dict[str, bytes | None]:
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


# ------------------------------------------------------------------ Añ-A


def test_ana_observacion_incompatible_explica_campo_formato_y_ejemplo(
        tmp_path) -> None:
    """Añ-A (PC-01): la observación de despacho incompatible se rechaza
    identificando campo/problema, formato esperado y ejemplo JSON con las
    seis claves.

    Sin este test, el usuario recibe «fields do not match the closed
    schema» sin saber qué campo falta ni cuál es la forma válida, y acaba
    adivinando el documento de observación o, peor, inventando valores.
    """
    fx = _RecoveryProject(tmp_path / "obs")
    bad = {
        "runtime": "demo-runtime",
        "model_configured": "demo-model",
        "model_reported": "demo-model",
        "session": "ses-ana-0001",
        "started_at": "2026-11-02T00:00:00Z",
    }
    bad_path = tmp_path / "obs-incompatible.json"
    bad_path.write_text(json.dumps(bad) + "\n", encoding="utf-8")
    proc = fx.run_packet(
        "prepare", "--project-root", str(fx.root),
        "--record-dispatch", fx.packet_id,
        "--attempt-id", "attempt-ana-001",
        "--input", str(bad_path))
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        "PC-01: la observación incompatible debe rechazarse: "
        f"got rc={proc.returncode} {out!r}")
    assert "Traceback" not in out, (
        f"PC-01: el rechazo es diagnóstico, no un traceback: {out[:400]!r}")
    assert "provenance" in out, (
        "PC-01: el diagnóstico identifica el campo/problema "
        f"(falta `provenance`): {out[:500]!r}")
    assert ('"model_configured"' in out and '"provenance"' in out
            and '"started_at"' in out), (
        "PC-01: el diagnóstico incluye un ejemplo JSON con las seis "
        f"claves: {out[:800]!r}")
    assert ("ejemplo" in out.lower() or "example" in out.lower()), (
        "PC-01: el diagnóstico presenta la forma válida como ejemplo "
        f"(no autoriza inventar valores): {out[:800]!r}")


# ------------------------------------------------------------------ Añ-B


def test_anb_decisions_senala_elemento_forma_y_ejemplo(tmp_path) -> None:
    """Añ-B (PC-02): decisions malformado conserva el rechazo, señala
    decisions/elemento, incluye la forma esperada y un ejemplo objeto.

    Sin este test, el usuario recibe «must be an object with
    decision+rationale» sin ver la forma exacta del elemento válido y
    acaba iterando a ciegas sobre el cuerpo del begin.
    """
    fx = _RecoveryProject(tmp_path / "dec")
    update = tmp_path / "update-decisions.json"
    update.write_text(json.dumps({
        "packet_id": fx.packet_id,
        "attempt": 1,
        "goal": "015-002 RED Añ-B: decisions malformado",
        "decisions": ["texto sin objeto"],
        "uncertainties": [],
        "next_action": "corregir decisions",
    }) + "\n", encoding="utf-8")
    proc = fx._run(CONTINUITY_CLI, [
        "begin", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--update", str(update), "--json",
    ])
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        "PC-02: decisions sin objeto debe seguir rechazándose: "
        f"got rc={proc.returncode} {out!r}")
    assert "Traceback" not in out, (
        f"PC-02: el rechazo es diagnóstico, no un traceback: {out[:400]!r}")
    assert "decisions" in out, (
        f"PC-02: el diagnóstico señala decisions/elemento: {out[:500]!r}")
    assert '"decision"' in out and '"rationale"' in out, (
        "PC-02: el diagnóstico incluye un ejemplo objeto con "
        f"decision+rationale: {out[:800]!r}")


# ------------------------------------------------------------------ Añ-C


def test_anc_write_scope_malformado_identifica_opcion_exige_forma_y_ejemplo(
        tmp_path) -> None:
    """Añ-C (PC-03): el write scope malformado identifica la opción, exige
    CLASS=SELECTOR no vacíos e incluye un ejemplo; no convierte
    repository-read en escritura.

    Sin este test, el usuario recibe «scope must be CLASS=SELECTOR»
    suelto y no sabe qué opción corregir ni cuál es la forma válida
    (`--write-scope implementation=skills`).
    """
    for tag, ws_value in (("bare", "docs"), ("empty", "docs=")):
        root = tmp_path / f"ws-{tag}"
        root.mkdir(parents=True, exist_ok=True)
        proj = root / "proj"
        b.build_project(proj)
        proc = b.run_cli(b.prepare_args(
            proj, objective="015-002 RED Añ-C: write scope malformado")
            + ["--write-scope", ws_value])
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            f"PC-03 ({tag}): el write scope malformado debe rechazarse: "
            f"got rc={proc.returncode} {out!r}")
        assert "Traceback" not in out, (
            f"PC-03 ({tag}): el rechazo es diagnóstico: {out[:400]!r}")
        assert "--write-scope" in out, (
            f"PC-03 ({tag}): el diagnóstico identifica la opción: "
            f"{out[:500]!r}")
        assert "CLASS=SELECTOR" in out, (
            f"PC-03 ({tag}): el diagnóstico exige CLASS=SELECTOR: "
            f"{out[:500]!r}")
        assert "implementation=skills" in out, (
            f"PC-03 ({tag}): el diagnóstico incluye un ejemplo válido: "
            f"{out[:800]!r}")


# ------------------------------------------------------------------ Añ-D


def test_and_begin_contract_cubierta_ofrece_estrechar_o_living(
        tmp_path) -> None:
    """Añ-D (PC-04): el begin con referencia contract cubierta por el
    write_scope sigue rechazándose antes de persistir y el diagnóstico
    ofrece estrechar el scope o usar living solo cuando corresponda.

    Sin este test, el usuario recibe el rechazo PC-06 sin salida
    accionable: no sabe si debe estrechar `--write-scope`, si cabe una
    referencia living genuinamente mutable, ni que un contrato aprobado
    no se reclasifica para eludir.
    """
    fx = _RecoveryProject(tmp_path / "covered")
    rel = "tests/exact_test_015_002_d.py"
    data = b"# fixture 015-002 A\xc3\xb1-D: referencia contract cubierta\n"
    path = fx.root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    before_tree = fx.tree()
    before_state = fx.state_bytes()
    proc = _begin(fx, [{"path": rel, "class": "contract",
                        "sha256": hashlib.sha256(data).hexdigest()}])
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        "PC-04: el begin con contract cubierta sigue rechazándose: "
        f"got rc={proc.returncode} {out!r}")
    assert "Traceback" not in out, (
        f"PC-04: el rechazo es diagnóstico, no un traceback: {out[:400]!r}")
    assert fx.tree() == before_tree, (
        "PC-04: el rechazo persiste nada antes de persistir (árbol intacto)")
    assert fx.state_bytes() == before_state, (
        "PC-04: el rechazo persiste nada antes de persistir (state intacto)")
    assert ("living" in out.lower()), (
        "PC-04: el diagnóstico ofrece la vía living (solo cuando "
        f"corresponda) y advierte contra reclasificar: {out[:800]!r}")
    assert ("estrech" in out.lower() or "narrow" in out.lower()
            or "--write-scope" in out), (
        "PC-04: el diagnóstico ofrece estrechar el scope: "
        f"{out[:800]!r}")


# ------------------------------------------------------------------ Añ-E


def test_ane_guia_docs_docs_documentada() -> None:
    """Añ-E (PC-05, mecánica mínima): continuity.md documenta el caso
    `docs=docs`: su límite (no cubre la carpeta del contrato del paquete),
    el ejemplo living mutable y la admisión de contract fuera de scope.

    Sin este test, la guía D2 podría perderse en una edición y el usuario
    ante el choque scopes documentales amplios vs referencias contract no
    tendría documento que explique estrechar el scope ni la vía living.
    El resto de PC-05 (coherencia semántica de la guía, revisión
    independiente) es no-mecánico y se declara como tal: este test solo
    verifica la presencia mecánica mínima de la guía.
    """
    assert CONTINUITY_MD.is_file(), (
        f"PC-05: la guía vive en {CONTINUITY_MD}")
    text = CONTINUITY_MD.read_text(encoding="utf-8")
    assert "docs=docs" in text, (
        "PC-05: continuity.md documenta el caso `docs=docs` "
        "(choque scope documental amplio vs referencia contract)")


# ------------------------------------------------------------------ Añ-F


def test_anf_open_unit_omite_cerrada_y_abre_primera_elegible(
        tmp_path) -> None:
    """Añ-F (PC-06): open-unit omite la queued del epic cerrado y abre la
    primera elegible, conservando el orden; la omitida y la historia quedan
    intactas.

    Sin este test, el usuario reabre por accidente una unidad de un epic ya
    cerrado (la primera queued), contaminando un cierre registrado.
    """
    root, home = _open_unit_project(tmp_path / "f", [UNIT_CLOSED, UNIT_OPEN])
    state_before = (root / "docs/.cdad-state.json").read_bytes()
    proc = _run_cli(PACKET_CLI,
                    ["open-unit", "--project-root", str(root)], home)
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "PC-06: con una candidata elegible la apertura procede "
        f"(rc=0): {out!r}")
    state = b.read_state(root)
    assert state.get("active_feature") == UNIT_OPEN, (
        "PC-06: open-unit abre la primera ELEGIBLE "
        f"(omite la del epic cerrado): {state.get('active_feature')!r} "
        f"{out[:400]!r}")
    omitted = [entry for entry in state.get("epic_features", [])
               if entry.get("id") == UNIT_CLOSED]
    assert omitted and omitted[0].get("status") == "queued", (
        "PC-06: la unidad omitida permanece queued (no done): "
        f"{state.get('epic_features')!r}")
    assert state.get("epic_history") == json.loads(
        state_before.decode("utf-8")).get("epic_history"), (
        "PC-06: la historia (incluido el cierre) queda intacta")


# ------------------------------------------------------------------ Añ-G


def test_ang_feature_excluida_rechaza_nombrando_unidad_y_epic(
        tmp_path) -> None:
    """Añ-G (PC-07): `--feature` de una unidad excluida (epic cerrado) se
    rechaza nombrando unidad y epic, sin abrir ni persistir.

    Sin este test, el usuario elude el cierre con `--feature` y reabre una
    unidad de un epic cerrado sin diagnóstico que lo detenga.
    """
    root, home = _open_unit_project(tmp_path / "g", [UNIT_CLOSED, UNIT_OPEN])
    before_tree = _tree(root)
    before_state = (root / "docs/.cdad-state.json").read_bytes()
    proc = _run_cli(PACKET_CLI, [
        "open-unit", "--project-root", str(root), "--feature", UNIT_CLOSED,
    ], home)
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        "PC-07: --feature de unidad excluida debe rechazarse: "
        f"got rc={proc.returncode} {out!r}")
    assert UNIT_CLOSED in out and CLOSED_EPIC in out, (
        "PC-07: el rechazo nombra la unidad y su epic cerrado: "
        f"{out[:600]!r}")
    assert b.read_state(root).get("active_feature") is None, (
        "PC-07: el rechazo no abre nada")
    assert _tree(root) == before_tree, (
        "PC-07: el rechazo no escribe el árbol")
    assert (root / "docs/.cdad-state.json").read_bytes() == before_state, (
        "PC-07: el rechazo no persiste el state")


# ------------------------------------------------------------------ Añ-H


def test_anh_solo_excluidas_informa_sin_candidata_sin_cambios(
        tmp_path) -> None:
    """Añ-H (PC-08): con solo unidades excluidas, open-unit informa que no
    hay candidata, sin ejecutar ni cambiar nada.

    Sin este test, el usuario obtiene una apertura silenciosa sobre un
    epic cerrado en vez de un informe que lo detenga.
    """
    root, home = _open_unit_project(tmp_path / "h", [UNIT_CLOSED])
    before_tree = _tree(root)
    before_state = (root / "docs/.cdad-state.json").read_bytes()
    proc = _run_cli(PACKET_CLI,
                    ["open-unit", "--project-root", str(root)], home)
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        "PC-08: sin candidatas elegibles no hay apertura: "
        f"got rc={proc.returncode} {out!r}")
    assert "candidata" in out.lower(), (
        f"PC-08: el informe declara que no hay candidata: {out[:600]!r}")
    assert b.read_state(root).get("active_feature") is None, (
        "PC-08: sin ejecución (nada activo)")
    assert _tree(root) == before_tree, (
        "PC-08: sin cambios en el árbol")
    assert (root / "docs/.cdad-state.json").read_bytes() == before_state, (
        "PC-08: sin cambios en el state")


# ------------------------------------------------------------------ Añ-I


def test_ani_apertura_elegible_conserva_garantias_y_documenta(
        tmp_path) -> None:
    """Añ-I (PC-09): la apertura elegible conserva reposo/dependencias/
    autoridad/vigencia/atomicidad (validate-state acepta) y
    project-start.md documenta que «primera queued» = primera elegible.

    Sin este test, una implementación podría abrir sin las comprobaciones
    conservadas, o la regla «primera elegible» quedaría sin documentar y
    el usuario leería «primera queued» como la primera sin filtrar.
    """
    root, home = _open_unit_project(tmp_path / "i", [UNIT_OPEN])
    proc = _run_cli(PACKET_CLI,
                    ["open-unit", "--project-root", str(root)], home)
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "PC-09 (control de montaje): con candidata elegible la apertura "
        f"procede: {out!r}")
    assert b.read_state(root).get("active_feature") == UNIT_OPEN, (
        "PC-09 (control de montaje): se abre la elegible")
    valid = _run_cli(PACKET_CLI,
                     ["validate-state", "--project-root", str(root)], home)
    assert valid.returncode == 0, (
        "PC-09: la apertura conserva las comprobaciones "
        f"(validate-state acepta): {(valid.stdout + valid.stderr)!r}")
    assert PROJECT_START_MD.is_file(), (
        f"PC-09: la regla vive en {PROJECT_START_MD}")
    doc = PROJECT_START_MD.read_text(encoding="utf-8")
    assert "elegible" in doc.lower() and "queued" in doc.lower(), (
        "PC-09: project-start.md documenta que «primera queued» es la "
        "primera ELEGIBLE (--feature no elude el cierre)")


# ------------------------------------------------------------------ Añ-J


UNIT_AMBIGUOUS = "015-903-ambigua"


def _ambiguous_unit_project(base: Path) -> tuple[Path, Path]:
    """Proyecto en reposo donde UNIT_AMBIGUOUS tiene fila estructural en los
    dos planes a distinta línea y uno de los epics está cerrado.

    El plan del epic cerrado declara su propia unidad y además la ambigua
    (la ambigua queda una línea más abajo); el plan del epic abierto declara
    solo la ambigua. Así la premisa de sensibilidad queda fijada en texto:
    el comportamiento previo (comparación de `row_index` entre archivos)
    atribuía al dueño de la línea más baja en vez de bloquear.
    """
    home = base / "home"
    home.mkdir(parents=True, exist_ok=True)
    root = base / "proj"
    b.build_project(root)
    proc = _run_cli(PACKET_CLI, [
        "prepare", "--project-root", str(root),
        "--role", "test-writer", "--substage", "red",
        "--objective", "015-002 POST-AUDIT Añ-J: reposo con unidad ambigua",
    ], home)
    assert proc.returncode == 0, (
        "precondición (fixture, comportamiento existente): `prepare` debe "
        f"publicar la ejecución (rc=0): {proc.stdout!r} {proc.stderr!r}")
    state = b.read_state(root)
    for fid in (UNIT_CLOSED, UNIT_OPEN, UNIT_AMBIGUOUS):
        data = f"# Spec fixture ({fid})\n".encode()
        path = root / f"docs/specs/{fid}/spec.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        state.setdefault("stage_history", []).append({
            "feature": fid,
            "stage": "specification",
            "approved_by": "Pablo",
            "approved_at": "2026-11-02T00:00:00Z",
            "contract_path": f"docs/specs/{fid}/spec.md",
            "contract_sha256": hashlib.sha256(data).hexdigest(),
        })
    closed_dir = root / f"docs/epics/{CLOSED_EPIC}"
    closed_dir.mkdir(parents=True, exist_ok=True)
    (closed_dir / "plan.md").write_text(
        f"# Plan fixture ({CLOSED_EPIC})\n\n## Entregas\n\n"
        f"| Orden | Feature | Estado | Depende de |\n"
        f"|---|---|---|---|\n"
        f"| 1 | {UNIT_CLOSED} — unidad del fixture | queued | — |\n"
        f"| 2 | {UNIT_AMBIGUOUS} — unidad ambigua | queued | — |\n"
        f"\n## Cambios\n\n- alta del fixture\n",
        encoding="utf-8")
    (closed_dir / "execution.md").write_text(
        f"# Autoridad del fixture ({CLOSED_EPIC})\n", encoding="utf-8")
    open_dir = root / f"docs/epics/{OPEN_EPIC}"
    open_dir.mkdir(parents=True, exist_ok=True)
    (open_dir / "plan.md").write_text(
        f"# Plan fixture ({OPEN_EPIC})\n\n## Entregas\n\n"
        f"| Orden | Feature | Estado | Depende de |\n"
        f"|---|---|---|---|\n"
        f"| 1 | {UNIT_AMBIGUOUS} — unidad ambigua | queued | — |\n"
        f"\n## Cambios\n\n- alta del fixture\n",
        encoding="utf-8")
    (open_dir / "execution.md").write_text(
        f"# Autoridad del fixture ({OPEN_EPIC})\n", encoding="utf-8")
    state["epic_history"] = [{
        "epic": CLOSED_EPIC,
        "epic_id": CLOSED_EPIC,
        "stage": "epic-closure",
        "approved_by": "Pablo",
        "approved_at": "2026-11-02T00:00:00Z",
    }]
    state["epic_features"] = [{"id": UNIT_AMBIGUOUS, "status": "queued"}]
    state["active_feature"] = None
    state["current_stage"] = "idle"
    state["tdd_substage"] = None
    state["active_packet"] = None
    b.write_state(root, state)
    valid = _run_cli(PACKET_CLI,
                     ["validate-state", "--project-root", str(root)], home)
    assert valid.returncode == 0, (
        "precondición (fixture, comportamiento existente): el reposo con "
        f"cola y cierre debe ser coherente hoy: "
        f"{valid.stdout!r} {valid.stderr!r}")
    closed_lines = (closed_dir / "plan.md").read_text(
        encoding="utf-8").splitlines()
    open_lines = (open_dir / "plan.md").read_text(
        encoding="utf-8").splitlines()
    closed_row = next(i for i, line in enumerate(closed_lines)
                      if UNIT_AMBIGUOUS in line)
    open_row = next(i for i, line in enumerate(open_lines)
                    if UNIT_AMBIGUOUS in line)
    assert closed_row != open_row, (
        "premisa de sensibilidad Añ-J: la unidad ambigua está a distinta "
        f"línea en cada plan (cerrado={closed_row}, abierto={open_row}); "
        "el comportamiento previo comparaba row_index entre archivos y no "
        "bloqueaba")
    return root, home


def _assert_ambiguous_block(out: str, proc_label: str) -> None:
    """El bloqueo ambiguo nombra unidad, ambos epics y ambas rutas."""
    assert "cannot decide eligibility" in out, (
        f"F1 ({proc_label}): el bloqueo identifica que no puede decidir "
        f"la elegibilidad: {out[:600]!r}")
    assert "ambiguous" in out, (
        f"F1 ({proc_label}): el bloqueo declara la ambigüedad: "
        f"{out[:600]!r}")
    assert UNIT_AMBIGUOUS in out, (
        f"F1 ({proc_label}): el bloqueo nombra la unidad: {out[:600]!r}")
    assert CLOSED_EPIC in out and OPEN_EPIC in out, (
        f"F1 ({proc_label}): el bloqueo nombra ambos epics: {out[:800]!r}")
    assert (f"docs/epics/{CLOSED_EPIC}/plan.md" in out
            and f"docs/epics/{OPEN_EPIC}/plan.md" in out), (
        f"F1 ({proc_label}): el bloqueo nombra ambas rutas de plan: "
        f"{out[:800]!r}")


def test_anj_unidad_en_dos_planes_bloquea_sin_abrir(tmp_path) -> None:
    """Añ-J (D3/F1; PC-08 rama bloqueante): la unidad con fila estructural
    en dos planes a distinta línea, uno de epic cerrado, bloquea `open-unit`
    y `--feature` sin abrir ni persistir.

    Sin este test, una tabla de contexto que nombre la unidad en un plan
    abierto por encima de su fila en el plan cerrado haría que `open-unit`
    reabriera la unidad (el defecto que la feature previene): la comparación
    de `row_index` entre archivos atribuía al dueño de la línea más baja.
    """
    root, home = _ambiguous_unit_project(tmp_path / "j")
    for proc_label, extra in (("open-unit", []),
                              ("--feature", ["--feature", UNIT_AMBIGUOUS])):
        before_tree = _tree(root)
        before_state = (root / "docs/.cdad-state.json").read_bytes()
        proc = _run_cli(PACKET_CLI,
                        ["open-unit", "--project-root", str(root), *extra],
                        home)
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            f"F1 ({proc_label}): la unidad ambigua debe bloquear "
            f"(rc≠0): got rc={proc.returncode} {out!r}")
        assert "Traceback" not in out, (
            f"F1 ({proc_label}): el bloqueo es diagnóstico, no un "
            f"traceback: {out[:400]!r}")
        _assert_ambiguous_block(out, proc_label)
        assert b.read_state(root).get("active_feature") is None, (
            f"F1 ({proc_label}): el bloqueo no abre nada")
        assert _tree(root) == before_tree, (
            f"F1 ({proc_label}): el bloqueo no escribe el árbol")
        assert ((root / "docs/.cdad-state.json").read_bytes()
                == before_state), (
            f"F1 ({proc_label}): el bloqueo no persiste el state")
