#!/usr/bin/env python3
"""010-000 RED (corrección tras devolución de gate) — raíces equivalentes.

Contract: docs/specs/010-000-continuity-relative-root/spec.md (aprobada
2026-10-29; sha256 623b15e1…f01737e2). AUDIT:
docs/specs/010-000-continuity-relative-root/test-audit.md. Gate:
docs/specs/010-000-continuity-relative-root/red-gate-findings.md
(commit previo 24eea61 conservado como evidencia; este archivo lo reemplaza).

Método (caja negra + API pública observada; ningún fuente de producto se
abre ni se lee):
- CLI por subproceso sobre `skills/cdad-cycle/scripts/` (fixtures vía
  `tests.test_004_002_t2_bootstrap.build_project`; HOME del subproceso en
  tempdir vacío).
- API directa sobre los mismos módulos usando SÓLO introspección pública
  (`python3 -c "import inspect, modulo"`). Firmas observadas (registradas;
  ver informe del rol):
    cdad_continuity.plan_write(root: Path, execution_context_path: Path,
        update: dict, *, command='checkpoint', max_bytes=None, state=None)
        -> dict   # {'envelope': {...record, seq, no_op, bytes,
                      body_sha256...}, 'writes': [[dest, bytes], ...]}
    cdad_packet.verify_published_packet(project_root: Path, packet_id, *,
        state=None) -> tuple[dict, dict]
    cdad_packet.classify_path(raw_path: str, path_policy: dict,
        project_root: Path) -> str | None   # benigna -> clase; insegura
        # -> PolicyError
    cdad_packet.classify_path_observable(raw_path: str, path_policy: dict,
        project_root: Path, temporary_roots: list[str]) -> str

Defecto: una raíz relativa que resuelve al mismo directorio que la absoluta
no permite operar (el `begin` nuevo con raíz relativa es rehusado: la CLI
falla con ruta duplicada y la API con ContinuityError de pertenencia).

Mapeo test → postcondición (una promesa observable por test, R2; la prueba
API directa extra de la promesa A la promueve el gate con razón registrada:
las entradas programáticas no quedan acreditadas por el CLI solo; sin cuota
por PC; regresiones existentes reutilizadas, no duplicadas):

  test_A_relative_root_begin_and_checkpoint_match_absolute
      -> PC-01/PC-02 (promesa A, vía CLI). Sin este test, el uso normal
         desde otro cwd depende de una restricción accidental del CLI.
  test_A2_programmatic_api_equivalence_and_purity
      -> PC-02/PC-03 (promesa A, vía API directa). Sin este test, la
         integración programática (plan_write / verify_published_packet /
         classify_path / classify_path_observable) seguiría rota aunque el
         CLI se arreglara, o plan_write escribiría efectos colaterales.
  test_B_portable_evidence_and_replay_across_equivalent_roots
      -> PC-04/PC-05 (promesa B). Sin este test, la corrección duplicaría
         trabajo o invalidaría evidencia ya emitida.
  test_C_existing_controls_hold_under_relative_root
      -> PC-06/PC-07 (promesa C). Sin este test, aceptar relativas
         legítimas podría debilitar barreras o dejar continuidad parcial.
  test_D_installed_consumer_reproduces_relative_equivalence
      -> PC-08 (promesa D). Sin este test, un arreglo que sólo funciona en
         el checkout no llegaría al producto distribuido.

RED hoy: cada test falla en una ASERCIÓN de comportamiento sobre la raíz
relativa (AssertionError de contrato, nunca ImportError/SyntaxError ni
error de fixture). Ninguna comparación de snapshot es condicional: toda
ausencia de efectos se comprueba siempre contra el árbol completo.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import build_project

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = REPO_ROOT / "skills" / "cdad-cycle" / "scripts"
PACKET_CLI = SKILL_SCRIPTS / "cdad_packet.py"
CONTINUITY_CLI = SKILL_SCRIPTS / "cdad_continuity.py"

CLI_TIMEOUT_S = 60
ROLE = "test-writer"
SUBSTAGE = "red"
OBJECTIVE = "010-000 RED raíces equivalentes (fixture)"


def _env(home: Path) -> dict:
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _run(cli: Path, args: list[str], cwd: Path, home: Path) -> subprocess.CompletedProcess:
    assert cli.is_file(), f"CLI del árbol ausente: {cli}"
    return subprocess.run(
        [sys.executable, str(cli), *args],
        capture_output=True, text=True, cwd=str(cwd), env=_env(home),
        stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
    )


def _output(proc: subprocess.CompletedProcess) -> str:
    return (proc.stdout or "") + (proc.stderr or "")


def _assert_begin_success(proc: subprocess.CompletedProcess, label: str) -> dict:
    text = _output(proc)
    assert "Traceback" not in text, (
        f"{label}: el `begin` con raíz relativa no debe resolver rutas por "
        f"concatenación (traceback de infraestructura); visto:\n{text[-1500:]}"
    )
    assert proc.returncode == 0, (
        f"{label}: un nuevo `begin` válido con raíz relativa equivalente debe "
        f"obtener éxito (rc=0); hoy rc={proc.returncode}:\n{text[-1500:]}"
    )
    assert proc.stdout.strip(), f"{label}: el `begin` no emitió su sobre por stdout"
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{label}: stdout del `begin` no es JSON válido: {proc.stdout[:300]!r}"
        ) from exc
    assert doc.get("record") == "begin", f"{label}: el sobre debe ser record=begin: {doc!r}"
    assert doc.get("seq") == 1, f"{label}: el primer begin tiene seq 1: {doc!r}"
    assert doc.get("no_op") is False, f"{label}: el begin nuevo publica efecto: {doc!r}"
    return doc


def _prepare_project(base: Path) -> tuple[Path, Path, str, str, Path]:
    """Proyecto sintético + prepare; devuelve (root, ctx, packet_id, home, feat)."""
    home = base / "home"
    home.mkdir(parents=True, exist_ok=True)
    root = base / "proj"
    build_project(root)
    proc = _run(
        PACKET_CLI,
        ["prepare", "--project-root", str(root), "--role", ROLE,
         "--substage", SUBSTAGE, "--objective", OBJECTIVE],
        REPO_ROOT, home,
    )
    assert proc.returncode == 0, (
        f"fixture: `prepare` debe tener éxito; rc={proc.returncode}:\n"
        f"{_output(proc)[-1000:]}"
    )
    state = json.loads((root / "docs" / ".cdad-state.json").read_text(encoding="utf-8"))
    packet_id = (state.get("active_packet") or {}).get("id")
    execution_id = (state.get("execution") or {}).get("id")
    assert packet_id and execution_id, f"fixture: sin paquete/ejecución activos: {state!r}"
    ctx = root / ".cdad" / "executions" / execution_id / "execution.json"
    assert ctx.is_file(), f"fixture: falta contexto {ctx}"
    feat = json.loads(ctx.read_text(encoding="utf-8"))["execution"]["feature_id"]
    return root, ctx, packet_id, home, feat


def _write_update(base: Path, name: str, packet_id: str, **over: object) -> Path:
    doc: dict = {
        "packet_id": packet_id,
        "attempt": 1,
        "goal": f"objetivo 010-000 ({name})",
        "decisions": [{"decision": "decisión 010-000", "rationale": "razón 010-000"}],
        "uncertainties": [],
        "next_action": "continuar el encargo",
        "references": [],
    }
    doc.update(over)
    path = base / f"{name}.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def _tree(root: Path) -> dict[str, bytes | None]:
    snap: dict[str, bytes | None] = {}
    for p in sorted(root.rglob("*")):
        if "__pycache__" in p.parts:
            continue
        snap[p.relative_to(root).as_posix()] = p.read_bytes() if p.is_file() else None
    return snap


def _copy_variants(base: Path, root: Path) -> tuple[Path, Path, Path]:
    """Tres expresiones del mismo estado inicial: absoluta, relativa, symlink."""
    abs_root = base / "abs" / "proj"
    rel_root = base / "rel" / "proj"
    for dst in (abs_root, rel_root):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(root, dst, symlinks=True)
    link_parent = base / "link"
    link_parent.mkdir(parents=True, exist_ok=True)
    sym_root = link_parent / "via-symlink"
    sym_root.symlink_to(rel_root, target_is_directory=True)
    return abs_root, rel_root, sym_root


def _ctx_for_variant(variant: Path) -> Path:
    found = sorted(variant.rglob("execution.json"))
    assert found, f"fixture: sin contexto copiado bajo {variant}"
    return found[0]


def _bodies(variant: Path) -> dict[str, bytes]:
    d = variant / ".cdad" / "executions" / sorted(
        (variant / ".cdad" / "executions").iterdir())[0].name / "continuity" / "bodies"
    if not d.is_dir():
        return {}
    return {p.name: p.read_bytes() for p in sorted(d.glob("*.json"))}


def _api_modules():
    """Importa los módulos públicos por su ruta instalada (sin leer fuentes).

    Sólo usa la ruta del módulo + import; las firmas empleadas son las
    observadas por introspección pública (ver docstring del archivo).
    """
    if str(SKILL_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SKILL_SCRIPTS))
    import cdad_continuity
    import cdad_packet
    return cdad_continuity, cdad_packet


def _policy_inputs(ctx: Path) -> tuple[dict, list]:
    data = json.loads(ctx.read_text(encoding="utf-8"))
    path_policy = data["path_policy"]
    temporary_roots: list = []
    try:
        snapshot = json.loads(base64.b64decode(data["policy"]["snapshot"]).decode("utf-8"))
        temporary_roots = snapshot.get("temporary_roots") or []
    except Exception:
        temporary_roots = []
    return path_policy, temporary_roots


def test_A_relative_root_begin_and_checkpoint_match_absolute(tmp_path: Path) -> None:
    """Promesa A (PC-01/PC-02, vía CLI): `begin` nuevo y `checkpoint` con raíz
    relativa, absoluta y symlink equivalente obtienen éxito y el mismo efecto
    lógico. Sin este test, el usuario no puede trabajar con la forma relativa
    de la raíz desde otro cwd."""
    base = tmp_path / "a"
    base.mkdir()
    root, ctx, packet_id, home, _feat = _prepare_project(base)
    abs_root, rel_root, _ = _copy_variants(base, root)
    # Symlink sobre copia FRESCA e independiente del proyecto: no reutiliza la
    # cadena ya publicada por la variante relativa (mismo estado inicial que
    # abs/rel; PC-01 exige comparar desde estados iniciales equivalentes).
    sym_origin = base / "symproj" / "proj"
    sym_origin.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root, sym_origin, symlinks=True)
    sym_link_parent = base / "linkfresh"
    sym_link_parent.mkdir(parents=True, exist_ok=True)
    sym_root = sym_link_parent / "via-symlink"
    sym_root.symlink_to(sym_origin, target_is_directory=True)

    upd_abs = _write_update(base, "upd-abs", packet_id)
    upd_rel = _write_update(base, "upd-rel", packet_id)

    proc_abs = _run(
        CONTINUITY_CLI,
        ["begin", "--project-root", str(abs_root),
         "--execution-context", str(_ctx_for_variant(abs_root)),
         "--update", str(upd_abs), "--json"],
        REPO_ROOT, home,
    )
    env_abs = _assert_begin_success(proc_abs, "PC-01 absoluta (control)")

    proc_rel = _run(
        CONTINUITY_CLI,
        ["begin", "--project-root", ".",
         "--execution-context", str(_ctx_for_variant(rel_root)),
         "--update", str(upd_rel), "--json"],
        rel_root, home,
    )
    env_rel = _assert_begin_success(proc_rel, "PC-01 relativa (RED: hoy rc=1 con ruta duplicada)")

    # Contenido IDENTICO al absoluto (mismo archivo: bytes garantizados
    # iguales; PC-01 compara el mismo efecto lógico desde el mismo estado).
    proc_sym = _run(
        CONTINUITY_CLI,
        ["begin", "--project-root", str(sym_root),
         "--execution-context", str(_ctx_for_variant(sym_origin)),
         "--update", str(upd_abs), "--json"],
        REPO_ROOT, home,
    )
    env_sym = _assert_begin_success(proc_sym, "PC-01 symlink equivalente")

    for label, env in (("relativa", env_rel), ("symlink", env_sym)):
        assert env["record"] == env_abs["record"] and env["seq"] == env_abs["seq"], (
            f"PC-01 violada: la raíz {label} debe publicar el mismo efecto lógico "
            f"que la absoluta; absoluta={env_abs!r} {label}={env!r}"
        )
        assert env["no_op"] == env_abs["no_op"], (
            f"PC-02 violada: el envelope con raíz {label} difiere del absoluto"
        )

    upd_cp = _write_update(base, "upd-cp", packet_id)
    proc_cp = _run(
        CONTINUITY_CLI,
        ["checkpoint", "--project-root", ".",
         "--execution-context", str(_ctx_for_variant(rel_root)),
         "--update", str(upd_cp), "--json"],
        rel_root, home,
    )
    text = _output(proc_cp)
    assert proc_cp.returncode == 0, (
        "PC-01 violada: `checkpoint` válido con raíz relativa debe tener éxito; "
        f"rc={proc_cp.returncode}:\n{text[-1500:]}"
    )
    cp_doc = json.loads(proc_cp.stdout)
    assert cp_doc.get("record") == "checkpoint" and cp_doc.get("seq") == 2, (
        f"PC-01 violada: el checkpoint relativo debe anexar seq 2: {cp_doc!r}"
    )


def test_A2_programmatic_api_equivalence_and_purity(tmp_path: Path) -> None:
    """Promesa A (PC-02/PC-03, vía API directa): con entradas idénticas y
    raíces equivalentes, `plan_write` (begin/checkpoint), el envelope y los
    destinos planificados coinciden; `verify_published_packet` admite el mismo
    paquete con documentos equivalentes; `classify_path` y
    `classify_path_observable` conservan clasificación y precedencia; y
    `plan_write` no crea, modifica ni elimina archivos al planear, al
    reconocer replay ni al rehusar. Sin este test, la integración
    programática seguiría rota aunque el CLI se arreglara, o el planificador
    tendría efectos colaterales invisibles."""
    cc, cp = _api_modules()
    base = tmp_path / "a2"
    base.mkdir()
    root, ctx, packet_id, home, _feat = _prepare_project(base)
    path_policy, temporary_roots = _policy_inputs(ctx)

    def update_doc(name: str) -> dict:
        return {
            "packet_id": packet_id,
            "attempt": 1,
            "goal": f"objetivo 010-000 ({name})",
            "decisions": [{"decision": "decisión 010-000", "rationale": "razón 010-000"}],
            "uncertainties": [],
            "next_action": "continuar el encargo",
            "references": [],
        }

    # PC-02: plan_write con la misma operación y raíces equivalentes.
    fresh = update_doc("api-plan")
    before_plan = _tree(root)
    try:
        plan_abs = cc.plan_write(root, ctx, dict(fresh), command="begin")
    except Exception as exc:
        raise AssertionError(
            f"PC-02 violada: plan_write absoluto (control) debe planear: "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    assert _tree(root) == before_plan, (
        "PC-03 violada: plan_write (plan) no debe crear, modificar ni eliminar archivos"
    )
    previous_cwd = os.getcwd()
    try:
        os.chdir(root)
        try:
            plan_rel = cc.plan_write(Path("."), ctx, dict(fresh), command="begin")
        except Exception as exc:
            raise AssertionError(
                "PC-02 violada: plan_write con raíz relativa equivalente debe "
                f"planear lo mismo que con la absoluta; hoy {type(exc).__name__}: {exc}"
            ) from exc
    finally:
        os.chdir(previous_cwd)
    assert _tree(root) == before_plan, (
        "PC-03 violada: plan_write relativo (plan) no debe dejar efectos en disco"
    )
    assert json.dumps(plan_rel["envelope"], sort_keys=True, default=str) == json.dumps(
        plan_abs["envelope"], sort_keys=True, default=str), (
        "PC-02 violada: el envelope planeado con raíz relativa difiere del absoluto"
    )
    assert plan_rel["writes"] == plan_abs["writes"], (
        "PC-02 violada: bytes planificados y destinos físicos difieren con otra raíz"
    )

    # Publicar el begin (control absoluto) para medir replay y verificación.
    upd_cli = _write_update(base, "upd-cli", packet_id,
                            goal="objetivo 010-000 (api-plan)")
    proc = _run(CONTINUITY_CLI,
                ["begin", "--project-root", str(root),
                 "--execution-context", str(ctx),
                 "--update", str(upd_cli), "--json"], REPO_ROOT, home)
    _assert_begin_success(proc, "PC-02/PC-03 control de publicación absoluta")

    # PC-03: replay reconocido sin escrituras ni publicaciones.
    replay_update = json.loads(upd_cli.read_text(encoding="utf-8"))
    before_replay = _tree(root)
    try:
        plan_replay = cc.plan_write(root, ctx, dict(replay_update), command="begin")
    except Exception as exc:
        raise AssertionError(
            f"PC-05/API violada: plan_write debe reconocer el replay ya publicado: "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    assert plan_replay["envelope"].get("no_op") is True, (
        "PC-05/API violada: repetir contenido publicado debe planear no_op verdadero; "
        f"visto {plan_replay['envelope']!r}"
    )
    assert not plan_replay["writes"], (
        "PC-05/API violada: el replay no debe planificar escrituras"
    )
    assert _tree(root) == before_replay, (
        "PC-03 violada: plan_write (replay) no debe modificar archivos"
    )

    # Nota: el caso de `packet_id` inexistente se RETIRA como oráculo de
    # autoridad (la admisión lo registra sin rehusar; ver nota en test_C).
    # El rechazo real con autoridad revocada se cubre en test_C vía
    # suspend-unit; aquí PC-03 queda acreditada por plan puro + replay puro.

    # PC-02: verify_published_packet admite el mismo paquete con ambas raíces.
    try:
        docs_abs = cp.verify_published_packet(root, packet_id)
    except Exception as exc:
        raise AssertionError(
            f"PC-02 violada: verify_published_packet absoluto (control) debe admitir "
            f"el paquete publicado: {type(exc).__name__}: {exc}"
        ) from exc
    previous_cwd = os.getcwd()
    try:
        os.chdir(root)
        try:
            docs_rel = cp.verify_published_packet(Path("."), packet_id)
        except Exception as exc:
            raise AssertionError(
                "PC-02 violada: verify_published_packet con raíz relativa debe "
                f"admitir el mismo paquete; hoy {type(exc).__name__}: {exc}"
            ) from exc
    finally:
        os.chdir(previous_cwd)
    assert len(docs_abs) == 2 and len(docs_rel) == 2, (
        f"PC-02 violada: verify debe devolver el par de documentos en ambas raíces: "
        f"abs={len(docs_abs)} rel={len(docs_rel)}"
    )
    for idx, (doc_abs, doc_rel) in enumerate(zip(docs_abs, docs_rel)):
        assert json.dumps(doc_rel, sort_keys=True, default=str) == json.dumps(
            doc_abs, sort_keys=True, default=str), (
            f"PC-02 violada: el documento verificado {idx} difiere con otra raíz"
        )

    # PC-02: clasificación y precedencia idénticas con ambas raíces.
    benign = "docs/cdad-policy.json"
    assert (root / benign).is_file(), f"fixture: falta referencia benigna {benign}"
    previous_cwd = os.getcwd()
    try:
        os.chdir(root)
        class_abs = cp.classify_path(benign, path_policy, root)
        class_rel = cp.classify_path(benign, path_policy, Path("."))
        obs_abs = cp.classify_path_observable(benign, path_policy, root, temporary_roots)
        obs_rel = cp.classify_path_observable(benign, path_policy, Path("."), temporary_roots)
    finally:
        os.chdir(previous_cwd)
    assert class_rel == class_abs and class_abs, (
        f"PC-02 violada: classify_path benigno debe conservar su clase con otra raíz: "
        f"abs={class_abs!r} rel={class_rel!r}"
    )
    assert obs_rel == obs_abs and obs_abs, (
        f"PC-02 violada: classify_path_observable benigno debe conservar su clase: "
        f"abs={obs_abs!r} rel={obs_rel!r}"
    )
    from cdad_packet import PolicyError as _PolicyError  # noqa: PLC0415  (vocabulario observado)
    for unsafe in ("../fuera.txt", "/etc/passwd"):
        for label, result in (
            ("classify_path/abs", _safe_call(cp.classify_path, unsafe, path_policy, root)),
            ("classify_path/rel", _safe_call_in(root, cp.classify_path, unsafe, path_policy)),
            ("observable/abs", _safe_call_obs(cp.classify_path_observable, unsafe, path_policy,
                                              root, temporary_roots)),
            ("observable/rel", _safe_call_obs_in(root, cp.classify_path_observable, unsafe,
                                                 path_policy, temporary_roots)),
        ):
            assert isinstance(result, _PolicyError), (
                f"PC-07/API violada: {label} debe rechazar {unsafe!r} sin falsos escapes; "
                f"visto {result!r}"
            )


def _safe_call(fn, raw, path_policy, project_root):
    try:
        return fn(raw, path_policy, project_root)
    except Exception as exc:  # noqa: BLE001 — el veredicto observado incluye el rechazo
        return exc


def _safe_call_in(cwd: Path, fn, raw, path_policy):
    previous_cwd = os.getcwd()
    try:
        os.chdir(cwd)
        return _safe_call(fn, raw, path_policy, Path("."))
    finally:
        os.chdir(previous_cwd)


def _safe_call_obs(fn, raw, path_policy, project_root, temporary_roots):
    try:
        return fn(raw, path_policy, project_root, temporary_roots)
    except Exception as exc:  # noqa: BLE001 — el veredicto observado incluye el rechazo
        return exc


def _safe_call_obs_in(cwd: Path, fn, raw, path_policy, temporary_roots):
    previous_cwd = os.getcwd()
    try:
        os.chdir(cwd)
        return _safe_call_obs(fn, raw, path_policy, Path("."), temporary_roots)
    finally:
        os.chdir(previous_cwd)


def test_B_portable_evidence_and_replay_across_equivalent_roots(tmp_path: Path) -> None:
    """Promesa B (PC-04/PC-05): sólo cambia la expresión de la raíz; bytes
    canónicos, identidad, digests, secuencia y enlaces se conservan sin la
    ruta absoluta, y el replay con otra raíz es `no_op` sin escrituras ni
    publicaciones mientras el conflicto conserva su rechazo. Sin este test,
    la corrección duplicaría trabajo o invalidaría evidencia."""
    base = tmp_path / "b"
    base.mkdir()
    root, ctx, packet_id, home, _feat = _prepare_project(base)
    abs_root = base / "abs" / "proj"
    rel_root = base / "rel" / "proj"
    for dst in (abs_root, rel_root):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(root, dst, symlinks=True)

    upd = _write_update(base, "upd", packet_id)
    proc_abs = _run(
        CONTINUITY_CLI,
        ["begin", "--project-root", str(abs_root),
         "--execution-context", str(_ctx_for_variant(abs_root)),
         "--update", str(upd), "--json"],
        REPO_ROOT, home,
    )
    _assert_begin_success(proc_abs, "PC-04 absoluta (control)")

    # MISMO contenido para ambas raíces (mismo archivo): PC-04 exige idéntico
    # estado inicial Y contenido; un goal distinto invalidaría la comparación.
    proc_rel = _run(
        CONTINUITY_CLI,
        ["begin", "--project-root", ".",
         "--execution-context", str(_ctx_for_variant(rel_root)),
         "--update", str(upd), "--json"],
        rel_root, home,
    )
    _assert_begin_success(proc_rel, "PC-04 relativa (RED: hoy rc=1 con ruta duplicada)")

    bodies_abs = _bodies(abs_root)
    bodies_rel = _bodies(rel_root)
    assert bodies_abs and bodies_rel, "fixture: ambas variantes deben publicar un cuerpo"
    assert set(bodies_abs) == set(bodies_rel), (
        "PC-04 violada: la misma operación con raíz equivalente debe conservar "
        f"identidad/digests; absoluta={sorted(bodies_abs)} relativa={sorted(bodies_rel)}"
    )
    for sha, raw in bodies_rel.items():
        assert str(abs_root) not in raw.decode("utf-8", "ignore"), (
            "PC-04 violada: la normalización incorporó la ruta absoluta a la "
            f"evidencia portable en {sha[:12]}…"
        )
        assert bodies_abs[sha] == raw, (
            f"PC-04 violada: los bytes canónicos difieren con otra raíz en {sha[:12]}…"
        )

    # Replay: repetir el mismo contenido con la otra expresión es no_op.
    before = _tree(rel_root)
    proc_replay = _run(
        CONTINUITY_CLI,
        ["begin", "--project-root", ".",
         "--execution-context", str(_ctx_for_variant(rel_root)),
         "--update", str(upd), "--json"],
        rel_root, home,
    )
    text = _output(proc_replay)
    assert proc_replay.returncode == 0, (
        f"PC-05 violada: el replay equivalente debe tener éxito:\n{text[-1200:]}"
    )
    rep_doc = json.loads(proc_replay.stdout)
    assert rep_doc.get("no_op") is True, (
        f"PC-05 violada: repetir contenido con otra raíz debe ser replay no_op; visto {rep_doc!r}"
    )
    after = _tree(rel_root)
    assert after == before, (
        "PC-05 violada: el replay no debe planificar ni publicar escrituras "
        f"(cambian {sorted(set(after) ^ set(before))[:5]!r} o sus bytes)"
    )

    # Conflicto: el mismo intento con contenido divergente conserva su rechazo.
    conflict = _write_update(base, "upd-conflicto", packet_id,
                             goal="contenido divergente 010-000",
                             decisions=[{"decision": "otra", "rationale": "x"}])
    before_conflict = _tree(rel_root)
    proc_conflict = _run(
        CONTINUITY_CLI,
        ["begin", "--project-root", ".",
         "--execution-context", str(_ctx_for_variant(rel_root)),
         "--update", str(conflict), "--json"],
        rel_root, home,
    )
    assert proc_conflict.returncode != 0, (
        "PC-05 violada: un conflicto de contenido con otra raíz debe conservar su rechazo"
    )
    assert _tree(rel_root) == before_conflict, (
        "PC-05 violada: el conflicto rechazado no debe publicar ni modificar nada"
    )


def test_C_existing_controls_hold_under_relative_root(tmp_path: Path) -> None:
    """Promesa C (PC-06/PC-07): con raíz relativa se conservan admisión
    (paquete alterado y autoridad revocada se rechazan antes de publicar) y
    pertenencia por resolución (traversal `..`, absolutas donde se exige
    relativa y symlinks exteriores rechazados sin efectos, testigo exterior
    intacto); `update.references` conserva su control léxico. Sin este test,
    la comodidad ampliaría la autoridad o dejaría continuidad parcial."""
    base = tmp_path / "c"
    base.mkdir()
    root, ctx, packet_id, home, feat = _prepare_project(base)
    pristine = base / "pristine" / "proj"
    pristine.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root, pristine, symlinks=True)

    def _pristine_copy(name: str) -> tuple[Path, Path]:
        case = base / name / "proj"
        case.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(pristine, case, symlinks=True)
        found = sorted(case.rglob("execution.json"))
        assert found, f"fixture: sin contexto copiado bajo {case}"
        return case, found[0]

    # Control positivo: el begin relativo válido es la precondición del resto.
    upd_ok = _write_update(base, "upd-ok", packet_id)
    proc_ok = _run(
        CONTINUITY_CLI,
        ["begin", "--project-root", ".",
         "--execution-context", str(ctx),
         "--update", str(upd_ok), "--json"],
        root, home,
    )
    _assert_begin_success(proc_ok, "PC-06/PC-07 precondición relativa (RED: hoy rc=1)")

    # PC-06: paquete alterado respecto de su render canónico.
    packet_dir = root / ".cdad" / "packets" / packet_id
    intact_packet = packet_dir / "PACKET.md"
    assert intact_packet.is_file(), f"fixture: falta paquete publicado {intact_packet}"
    request_doc = packet_dir / "REQUEST.json"
    before_admission = _tree(root)
    proc_intact = _run(
        PACKET_CLI,
        ["validate-packet", "--project-root", str(root),
         "--execution-context", str(ctx),
         "--request", str(request_doc), "--packet", str(intact_packet)],
        REPO_ROOT, home,
    )
    assert proc_intact.returncode == 0, (
        "PC-06 fixture: el paquete intacto debe validar; "
        f"rc={proc_intact.returncode}:\n{_output(proc_intact)[-800:]}"
    )
    altered_packet = base / "PACKET-alterado.md"
    raw_packet = intact_packet.read_text(encoding="utf-8")
    altered = raw_packet.replace("approved-feature-spec", "approved-feature-SPEC", 1)
    assert altered != raw_packet, "fixture: la alteración debe cambiar un byte real"
    altered_packet.write_text(altered, encoding="utf-8")
    proc_altered = _run(
        PACKET_CLI,
        ["validate-packet", "--project-root", str(root),
         "--execution-context", str(ctx),
         "--request", str(request_doc), "--packet", str(altered_packet)],
        REPO_ROOT, home,
    )
    assert proc_altered.returncode != 0, (
        "PC-06 violada: un paquete alterado respecto de su render canónico debe "
        "rechazarse aunque la raíz sea equivalente"
    )
    assert "differs from canonical" in _output(proc_altered), (
        f"PC-06 violada: el rechazo debe ser por diferencia canónica; visto:\n"
        f"{_output(proc_altered)[-800:]}"
    )
    assert _tree(root) == before_admission, (
        "PC-06 violada: la admisión (intacta o alterada) no debe publicar continuidad"
    )

    # PC-06: efecto nuevo sin autoridad vigente (unidad suspendida).
    proc_suspend = _run(
        PACKET_CLI,
        ["suspend-unit", "--project-root", str(root),
         "--feature", feat, "--reason", "revocación de autoridad (RED 010-000)"],
        REPO_ROOT, home,
    )
    assert proc_suspend.returncode == 0, (
        f"PC-06 fixture: suspender debe tener éxito:\n{_output(proc_suspend)[-800:]}"
    )
    suspended_snapshot = _tree(root)
    upd_new = _write_update(base, "upd-nuevo", packet_id,
                            goal="efecto nuevo sin autoridad vigente")
    proc_blocked = _run(
        CONTINUITY_CLI,
        ["checkpoint", "--project-root", ".",
         "--execution-context", str(ctx),
         "--update", str(upd_new), "--json"],
        root, home,
    )
    assert proc_blocked.returncode != 0, (
        "PC-06 violada: un efecto nuevo sin autoridad vigente (suspendida) con raíz "
        "relativa debe rechazarse antes de publicar"
    )
    assert "suspended" in _output(proc_blocked), (
        f"PC-06 violada: el rechazo debe ser por suspensión; visto:\n"
        f"{_output(proc_blocked)[-800:]}"
    )
    assert _tree(root) == suspended_snapshot, (
        "PC-06 violada: el rechazo por autoridad revocada no debe publicar efectos"
    )
    proc_resume = _run(
        PACKET_CLI,
        ["resume-unit", "--project-root", str(root), "--feature", feat],
        REPO_ROOT, home,
    )
    assert proc_resume.returncode == 0, (
        f"PC-06 fixture: reanudar debe tener éxito:\n{_output(proc_resume)[-800:]}"
    )

    # Nota: un `packet_id` inexistente en el update NO es un oráculo de
    # autoridad (la admisión lo registra sin rehusar: probado rc=0 con raíz
    # absoluta sobre copia prístina); la autoridad revocada real se ejerce
    # con suspensión, caso anterior.

    # PC-07: pertenencia por resolución — veredicto idéntico con raíz relativa
    # y absoluta; testigo exterior intacto; sin efectos en disco.
    witness = base / "testigo-exterior.txt"
    witness.write_text("secreto exterior 010-000\n", encoding="utf-8")
    escape_link = root / "docs" / "enlace-exterior.txt"
    if escape_link.is_symlink() or escape_link.exists():
        escape_link.unlink()
    escape_link.symlink_to(witness, target_is_directory=False)
    before_classify = _tree(root)
    cases = [
        ("../fuera.txt", 2, "unsafe"),
        ("/etc/passwd", 2, "unsafe"),
        ("docs/enlace-exterior.txt", 2, "escapes project root"),
        ("docs/cdad-policy.json", 0, "policy"),
    ]
    for raw_path, expected_rc, marker in cases:
        outs: list[str] = []
        for flag_root, cwd in ((str(root), REPO_ROOT), (".", root)):
            proc = _run(
                PACKET_CLI,
                ["validate-policy", "--project-root", flag_root, "--classify", raw_path],
                cwd, home,
            )
            out = _output(proc)
            outs.append(out)
            assert "Traceback" not in out, (
                f"PC-07: clasificar {raw_path!r} con raíz {flag_root!r} no debe romper; "
                f"visto:\n{out[-800:]}"
            )
            assert proc.returncode == expected_rc, (
                f"PC-07 violada: clasificar {raw_path!r} con raíz {flag_root!r} debe dar "
                f"rc={expected_rc} (rc={proc.returncode}):\n{out[-800:]}"
            )
            assert marker in out, (
                f"PC-07 violada: clasificar {raw_path!r} con raíz {flag_root!r} debe "
                f"emitir {marker!r}; visto:\n{out[-800:]}"
            )
        assert outs[0].splitlines() == outs[1].splitlines(), (
            f"PC-07 violada: el veredicto sobre {raw_path!r} difiere entre raíz "
            f"absoluta y relativa: {outs[0][:200]!r} vs {outs[1][:200]!r}"
        )
    assert _tree(root) == before_classify, (
        "PC-07 violada: clasificar no debe publicar ni modificar nada"
    )
    assert witness.read_text(encoding="utf-8") == "secreto exterior 010-000\n", (
        "PC-07 violada: el testigo exterior debe permanecer intacto"
    )

    # PC-07: control léxico de update.references (absolutas y traversal
    # rechazados; el symlink exterior en references queda diferido por contrato
    # y no se exige aquí). Casos sobre copias para no contaminar la cadena.
    for ref_value, marker in (("/etc/passwd", "must be relative"),
                              ("../fuera.txt", "escapes project root")):
        # Copias prístinas (sin cabeza): el control léxico se comprueba antes
        # que el idempotency-key y el veredicto es atribuible a la referencia.
        case_root, case_ctx = _pristine_copy(f"ref-{len(marker)}")
        upd_ref = _write_update(base, f"upd-ref-{len(marker)}", packet_id,
                                references=[ref_value])
        for flag_root, cwd in ((str(case_root), REPO_ROOT), (".", case_root)):
            proc_ref = _run(
                CONTINUITY_CLI,
                ["begin", "--project-root", flag_root,
                 "--execution-context", str(case_ctx),
                 "--update", str(upd_ref), "--json"],
                cwd, home,
            )
            out_ref = _output(proc_ref)
            assert proc_ref.returncode != 0, (
                f"PC-07 violada: la referencia {ref_value!r} con raíz {flag_root!r} "
                f"debe rechazarse (rc={proc_ref.returncode})"
            )
            assert "reference" in out_ref and marker in out_ref, (
                f"PC-07 violada: el rechazo de {ref_value!r} con raíz {flag_root!r} "
                f"debe ser léxico ({marker!r}); visto:\n{out_ref[-800:]}"
            )


def test_D_installed_consumer_reproduces_relative_equivalence(tmp_path: Path) -> None:
    """Promesa D (PC-08): los CLI instalados en raíz aislada reproducen el
    éxito relativo≈absoluto de `begin`/`checkpoint` y el rechazo inseguro sin
    publicaciones, sin wrappers del checkout y sin instalación global. Sin
    este test, el arreglo sólo valdría en el checkout y no llegaría al
    producto distribuido."""
    from tests.product_staging import product_root

    product = product_root()
    install_root = tmp_path / "install-root"
    install_root.mkdir()
    env = dict(os.environ)
    env["CDAD_INSTALL_ROOT"] = str(install_root)
    env["CDAD_SKILL_EXTRA_DIRS"] = ""
    inst = subprocess.run(
        ["bash", str(Path(product) / "install.sh")],
        cwd=str(product), env=env, text=True, capture_output=True, timeout=300,
    )
    assert inst.returncode == 0, (
        "PC-08 fixture: la instalación aislada debe tener éxito; "
        f"rc={inst.returncode}:\n{(inst.stderr or inst.stdout)[-1500:]}"
    )
    installed_cont = (
        install_root / ".config" / "opencode" / "skills" / "cdad-cycle"
        / "scripts" / "cdad_continuity.py"
    )
    installed_pkt = (
        install_root / ".config" / "opencode" / "skills" / "cdad-cycle"
        / "scripts" / "cdad_packet.py"
    )
    assert installed_cont.is_file() and installed_pkt.is_file(), (
        f"PC-08 fixture: faltan CLIs instalados bajo {install_root}"
    )

    base = tmp_path / "consumer"
    base.mkdir()
    home = base / "home"
    home.mkdir()
    assert not (base / "scripts" / "cdad_continuity.py").exists()
    from test_004_002_t2_bootstrap import build_project as _build

    # Dos expresiones del mismo consumidor: equivalencia instalada.
    seed = base / "seed"
    seed.mkdir()
    seed_proj = seed / "proj"
    _build(seed_proj)
    prep = subprocess.run(
        [sys.executable, str(installed_pkt), "prepare",
         "--project-root", str(seed_proj), "--role", ROLE, "--substage", SUBSTAGE,
         "--objective", OBJECTIVE],
        capture_output=True, text=True, cwd=str(REPO_ROOT), env=_env(home),
        stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
    )
    assert prep.returncode == 0, (
        f"PC-08 fixture: prepare instalado debe tener éxito:\n"
        f"{(prep.stdout + prep.stderr)[-1000:]}"
    )
    state = json.loads((seed_proj / "docs" / ".cdad-state.json").read_text(encoding="utf-8"))
    pid = (state.get("active_packet") or {}).get("id")
    eid = (state.get("execution") or {}).get("id")
    assert pid and eid, f"PC-08 fixture: sin paquete/ejecución: {state!r}"

    abs_proj = base / "abs" / "proj"
    rel_proj = base / "rel" / "proj"
    for dst in (abs_proj, rel_proj):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(seed_proj, dst, symlinks=True)

    def installed_ctx(variant: Path) -> Path:
        found = sorted(variant.rglob("execution.json"))
        assert found, f"PC-08 fixture: sin contexto instalado bajo {variant}"
        return found[0]

    upd_rel = _write_update(base, "upd-inst-rel", pid)
    proc_rel = _run(installed_cont, ["begin", "--project-root", ".",
                                    "--execution-context", str(installed_ctx(rel_proj)),
                                    "--update", str(upd_rel), "--json"], rel_proj, home)
    env_rel = _assert_begin_success(proc_rel, "PC-08 instalada relativa (RED: hoy rc=1)")

    upd_abs = _write_update(base, "upd-inst-abs", pid)
    proc_abs = _run(installed_cont, ["begin", "--project-root", str(abs_proj),
                                    "--execution-context", str(installed_ctx(abs_proj)),
                                    "--update", str(upd_abs), "--json"], base, home)
    env_abs = _assert_begin_success(proc_abs, "PC-08 instalada absoluta (control)")
    assert env_rel["record"] == env_abs["record"] and env_rel["seq"] == env_abs["seq"], (
        "PC-08 violada: la instalada relativa debe publicar el mismo efecto lógico "
        f"que la absoluta: {env_rel!r} vs {env_abs!r}"
    )

    # Checkpoint instalado con raíz relativa sobre la cadena relativa.
    upd_cp = _write_update(base, "upd-inst-cp", pid)
    proc_cp = _run(installed_cont, ["checkpoint", "--project-root", ".",
                                   "--execution-context", str(installed_ctx(rel_proj)),
                                   "--update", str(upd_cp), "--json"], rel_proj, home)
    assert proc_cp.returncode == 0, (
        "PC-08 violada: el checkpoint instalado con raíz relativa debe tener éxito; "
        f"rc={proc_cp.returncode}:\n{_output(proc_cp)[-1200:]}"
    )
    cp_doc = json.loads(proc_cp.stdout)
    assert cp_doc.get("record") == "checkpoint" and cp_doc.get("seq") == 2, (
        f"PC-08 violada: el checkpoint instalado debe anexar seq 2: {cp_doc!r}"
    )

    # Rechazo instalado sin publicaciones: traversal clasificado y referencia
    # absoluta rehusada, con el árbol idéntico antes y después.
    before_reject = _tree(rel_proj)
    proc_trav = _run(installed_pkt,
                     ["validate-policy", "--project-root", ".",
                      "--classify", "../fuera.txt"], rel_proj, home)
    assert proc_trav.returncode == 2, (
        "PC-08 violada: la instalada debe rechazar el traversal con raíz relativa; "
        f"rc={proc_trav.returncode}:\n{_output(proc_trav)[-800:]}"
    )
    assert "unsafe" in _output(proc_trav), (
        f"PC-08 violada: el rechazo instalado debe ser por inseguridad; visto:\n"
        f"{_output(proc_trav)[-800:]}"
    )
    upd_evil = _write_update(base, "upd-inst-evil", pid, references=["/etc/passwd"])
    proc_evil = _run(installed_cont, ["begin", "--project-root", ".",
                                     "--execution-context", str(installed_ctx(rel_proj)),
                                     "--update", str(upd_evil), "--json"], rel_proj, home)
    assert proc_evil.returncode != 0, (
        "PC-08 violada: la instalada con raíz relativa debe rehusar la entrada "
        "insegura sujeta al containment de PC-07"
    )
    assert _tree(rel_proj) == before_reject, (
        "PC-08 violada: los rechazos instalados no deben publicar nada"
    )
    bodies = _bodies(rel_proj)
    assert len(bodies) == 2, (
        f"PC-08 violada: sólo begin+checkpoint debían publicar cuerpos; hay {len(bodies)}"
    )
