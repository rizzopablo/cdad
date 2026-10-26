"""RED 007-003 — reanclaje explícito de continuidad legada.

Contrato: amendment-legacy-reanchor.md §7 y §10, más
spec.md §2.3.1/§2.1/§2.5. Todas las verificaciones son por CLI, en
proyectos temporales con HOME/XDG aislados; no se importa implementación.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from test_007_003_continuity_at_edges import (
    AUTHORITY_REF,
    _Project,
    assert_rc0,
    canonical_body_bytes,
    json_doc,
    sha256_bytes,
)

from test_007_003_continuity_at_edges import CONTINUITY_CLI


def _dry_run(project: _Project, label: str) -> dict:
    proc = project.run(
        CONTINUITY_CLI,
        "reanchor", "--project-root", str(project.root),
        "--execution-context", str(project.ctx), "--dry-run", "--json")
    return json_doc(proc, label, "reanchor --dry-run")


def _legacyize(project: _Project, head_seq: int = 5, *, modern_head: bool = False
               ) -> tuple[list[str], str]:
    """Crear la forma legada a partir de artefactos reales del productor.

    El productor actual crea los cuerpos; el fixture sólo quita `prev`, vuelve
    a calcular sus digests content-addressed y deja una cabeza legada coherente.
    """
    first = project.begin(attempt=1)
    assert_rc0(first, "legacy fixture/begin", "begin del productor")
    for index in range(2, head_seq + 1):
        proc = project.checkpoint(attempt=1, label=f"legacy-{index}")
        assert_rc0(proc, f"legacy fixture/checkpoint-{index}",
                   "checkpoint del productor")

    original = project.head()
    current_sha = original["body_sha256"]
    chain: list[tuple[str, dict]] = []
    while current_sha:
        body = project.body(current_sha)
        chain.append((current_sha, body))
        prev = body.get("prev")
        current_sha = (prev or {}).get("checkpoint_sha256") if isinstance(prev, dict) else None

    # Los cuerpos son todos producidos por la CLI. Se archivan bajo sus nuevos
    # digests (sin `prev`) y la cabeza apunta al cuerpo legado de seq=head_seq.
    archived: list[str] = []
    for position, (old_sha, body) in enumerate(chain):
        legacy = dict(body)
        if not (modern_head and position == 0):
            legacy.pop("prev", None)
        # F265 retains the producer-created initial begin and one distinct
        # historical begin candidate under the same packet/attempt key: two
        # total, matching the prepared-package fixture in the contract.
        if modern_head and position == 10:
            legacy["record"] = "begin"
            legacy["attempt"] = 1
            legacy["goal"] = f"historical divergent begin {position}"
        digest = sha256_bytes(canonical_body_bytes(legacy))
        project.body_path(digest).write_bytes(canonical_body_bytes(legacy))
        archived.append(digest)
    head = dict(original)
    head["body_sha256"] = archived[0]
    head["seq"] = head_seq
    if modern_head:
        # Repoint the one modern head to the transformed seq=264 legacy body,
        # then recalculate its physical digest and retain the historical seq.
        modern = dict(chain[0][1])
        modern_prev = dict(modern.get("prev") or {})
        modern_prev["checkpoint_sha256"] = archived[1]
        modern["prev"] = modern_prev
        modern_sha = sha256_bytes(canonical_body_bytes(modern))
        project.body_path(modern_sha).write_bytes(canonical_body_bytes(modern))
        archived[0] = modern_sha
        head["body_sha256"] = modern_sha
        head["prev_checkpoint_sha256"] = archived[1]
    else:
        head["prev_checkpoint_sha256"] = None
    project.write_head(head)
    for old_sha, _ in chain:
        if old_sha not in archived:
            project.body_path(old_sha).unlink(missing_ok=True)
    return archived, archived[0]


def _write_approval(project: _Project, dry: dict, *, execution_id: str | None = None,
                    head_sha256: str | None = None,
                    inventory_sha256: str | None = None,
                    reason: str = "recuperar continuidad legada") -> tuple[Path, str]:
    approval = project.root / "docs" / "decisions" / "legacy-reanchor.md"
    approval.parent.mkdir(parents=True, exist_ok=True)
    approval.write_text(
        "---\n"
        f"reanchor_execution_id: \"{execution_id or dry['execution_id']}\"\n"
        f"reanchor_head_sha256: \"{head_sha256 or dry['head_sha256']}\"\n"
        f"reanchor_inventory_sha256: \"{inventory_sha256 or dry['pre_anchor_inventory_sha256']}\"\n"
        "approved_by: \"Pablo\"\n"
        "approved_at: \"2026-10-25\"\n"
        f"---\n\nAutorizo expresamente el reanclaje: {reason}.\n",
        encoding="utf-8")
    approval_sha = hashlib.sha256(approval.read_bytes()).hexdigest()
    return approval, approval_sha


def _reanchor(project: _Project, old_head: str, approval_ref: str =
              "docs/decisions/legacy-reanchor.md", reason: str =
              "recuperar continuidad legada"):
    return project.run(CONTINUITY_CLI, "reanchor", "--project-root", str(project.root),
                       "--execution-context", str(project.ctx), "--expected-head", old_head,
                       "--approval-ref", approval_ref, "--reason", reason, "--json")


def _continuity_bytes(project: _Project) -> dict[str, bytes]:
    return {p.relative_to(project.continuity_dir()).as_posix(): p.read_bytes()
            for p in sorted(project.continuity_dir().rglob("*")) if p.is_file()}


def _body_bytes(project: _Project) -> dict[str, bytes]:
    base = project.bodies_dir()
    return {p.name: p.read_bytes() for p in sorted(base.glob("*.json")) if p.is_file()}


def _ready_legacy(project: _Project, seq: int = 5) -> tuple[str, dict, Path]:
    _, head = _legacyize(project, seq)
    dry = _dry_run(project, f"{project.name}/dry-run")
    approval, _ = _write_approval(project, dry)
    return head, dry, approval


def _reanchored_segment(project: _Project, label: str, *, checkpoints: int = 4):
    head, dry, _ = _ready_legacy(project)
    anchor = _assert_an_anchor(project, dry, old_head=head, old_seq=5, label=label)
    assert_rc0(project.begin(attempt=1, label=f"{label}/fresh"),
               f"{label}/begin", "begin posterior al ancla")
    for index in range(checkpoints):
        assert_rc0(project.checkpoint(attempt=1, label=f"{label}/cp-{index}"),
                   f"{label}/cp-{index}", "checkpoint posterior al ancla")
    return anchor


def _assert_rc1_unchanged(project: _Project, proc, label: str,
                          before: dict[str, bytes]) -> None:
    violations = []
    if proc.returncode != 1:
        violations.append(
            f"rechazo de contrato esperado rc=1; rc={proc.returncode}: "
            f"{proc.stdout}{proc.stderr}")
    after = _continuity_bytes(project)
    if after != before:
        violations.append(
            f"continuity/ cambió con rechazo: {sorted(set(before) ^ set(after))}")
        violations.append("los bytes de continuity/ no son idénticos al snapshot previo")
    assert not violations, f"{label}: " + "; ".join(violations)


def _assert_dry_run_and_publish_reject_without_writes(
        project: _Project, old_head: str, label: str,
        before: dict[str, bytes]) -> None:
    violations = []
    dry = project.run(CONTINUITY_CLI, "reanchor", "--project-root", str(project.root),
                      "--execution-context", str(project.ctx), "--dry-run", "--json")
    if dry.returncode != 1:
        violations.append(f"dry-run rc esperado 1, visto {dry.returncode}: {dry.stderr}")
    if _continuity_bytes(project) != before:
        violations.append("dry-run modificó continuity/")
    publish = _reanchor(project, old_head)
    if publish.returncode != 1:
        violations.append(f"publicación rc esperado 1, visto {publish.returncode}: {publish.stderr}")
    if _continuity_bytes(project) != before:
        violations.append("publicación modificó continuity/")
    assert not violations, f"{label}: " + "; ".join(violations)


def _assert_an_anchor(project: _Project, dry: dict, *, old_head: str,
                      old_seq: int, label: str) -> dict:
    _, approval_sha = _write_approval(project, dry)
    args = [
        "reanchor", "--project-root", str(project.root),
        "--execution-context", str(project.ctx), "--expected-head", old_head,
        "--approval-ref", "docs/decisions/legacy-reanchor.md",
        "--reason", "recuperar continuidad legada", "--json",
    ]
    proc = project.run(CONTINUITY_CLI, *args)
    anchor = json_doc(proc, label, "publicación del ancla")
    assert anchor.get("record") == "reanchor", f"{label}: record != reanchor: {anchor}"
    assert anchor.get("seq") == 1, f"{label}: el ancla debe iniciar seq 1: {anchor}"
    assert anchor.get("legacy_anchor", {}).get("head_sha256") == old_head
    assert anchor.get("legacy_anchor", {}).get("head_seq") == old_seq
    assert anchor.get("legacy_anchor", {}).get("approval_ref", {}).get("sha256") == approval_sha
    assert dry.get("pre_anchor_inventory_sha256") == anchor.get("pre_anchor_inventory_sha256")
    return anchor


def test_reanchor_legacy_prepared_preserves_history(tmp_path: Path) -> None:
    """PC-R1: F5 se reancla, vuelve a begin y cierra; el archivo legado no cambia."""
    project = _Project(tmp_path, "reanchor-f5")
    archived, old_head = _legacyize(project, 5)
    before = project.continuity_files()
    prepared_packet = {p.name: p.read_bytes() for p in project.packet_dir().rglob("*")
                       if p.is_file()}
    dry = _dry_run(project, "PC-R1/F5")
    assert dry.get("execution_id") == project.execution_id
    assert dry.get("head_sha256") == old_head and dry.get("head_seq") == 5
    anchor = _assert_an_anchor(project, dry, old_head=old_head, old_seq=5,
                               label="PC-R1/F5")
    assert anchor["record"] == "reanchor"
    assert project.head().get("seq") == 1
    assert sorted(anchor.get("pre_anchor_bodies", [])) == sorted(archived)
    assert all(project.body_path(sha).is_file() for sha in archived)
    assert {p.name: p.read_bytes() for p in project.packet_dir().rglob("*")
            if p.is_file()} == prepared_packet, "reanchor no altera el paquete prepared"
    assert all(project.body_raw(sha) == before[f"bodies/{sha}.json"] for sha in archived)
    assert before != project.continuity_files(), "reanchor debe publicar cuerpo y cabeza"

    new_begin = project.begin(attempt=1, label="fresh begin")
    assert_rc0(new_begin, "PC-R1/new begin", "begin nuevo sobre el ancla")
    assert project.head().get("seq") == 2
    assert_rc0(project.verify_begin(attempt=1), "PC-R1/verify", "verify-begin")
    record = project.record_dispatch(n=1)
    assert_rc0(record, "PC-R1/record", "record del despacho")
    assert_rc0(project.receive(n=1), "PC-R1/receive", "receive y cierre")
    project.assert_close(1, "PC-R1/cierre")


def test_reanchor_long_mixed_chain_starts_demonstrable_segment(tmp_path: Path) -> None:
    """PC-R2: F265 conserva ambos begin archivados; límite del ancla no amplía el ordinario."""
    project = _Project(tmp_path, "reanchor-f265")
    archived, old_head = _legacyize(project, 265, modern_head=True)
    historical_begins = [project.body(sha) for sha in archived
                         if project.body(sha).get("record") == "begin"
                         and project.body(sha).get("packet_id") == project.packet_id
                         and project.body(sha).get("attempt") == 1]
    assert len(historical_begins) == 2, (
        "F265 debe incluir exactamente los dos begin históricos del paquete "
        "prepared con attempt=1")
    dry = _dry_run(project, "PC-R2/F265")
    assert dry.get("body_count") == 265
    assert dry.get("head_seq") == 265
    assert len(archived) == 265
    anchor = _assert_an_anchor(project, dry, old_head=old_head, old_seq=265,
                               label="PC-R2/F265")
    assert len(anchor.get("pre_anchor_bodies", [])) == 265
    assert_rc0(project.begin(attempt=1, label="fresh begin"), "PC-R2/begin",
               "primer begin posterior al ancla")
    assert_rc0(project.verify_begin(attempt=1), "PC-R2/verify", "verify-begin")
    assert_rc0(project.resume(), "PC-R2/resume", "resume sobre el segmento nuevo")
    reconciliation = json_doc(
        project.run(CONTINUITY_CLI, "reconcile", "--project-root", str(project.root),
                    "--execution-context", str(project.ctx), "--json"),
        "PC-R2/reconcile", "reconcile sobre el segmento nuevo")
    diagnostic = json.dumps(reconciliation, ensure_ascii=False).lower()
    assert "historia anterior conservada" in diagnostic
    assert "no demostrable" in diagnostic
    # El límite especial sólo cubre el inventario inline del ancla, no un cuerpo
    # ordinario sobredimensionado.
    oversized = project.write_update(attempt=1, label="ordinary oversized",
                                     changes=["x" * (1024 * 1024)])
    ordinary = project.run(
        CONTINUITY_CLI,
        "checkpoint", "--project-root", str(project.root),
        "--execution-context", str(project.ctx), "--update", str(oversized),
        "--max-bytes", "256", "--json")
    assert ordinary.returncode != 0, "cuerpo ordinario sobredimensionado debe rechazarse"
    record = project.record_dispatch(n=1)
    assert_rc0(record, "PC-R2/record", "record del despacho")
    assert_rc0(project.receive(n=1), "PC-R2/receive", "receive y cierre")
    project.assert_close(1, "PC-R2/cierre")


def test_reanchor_requires_fresh_begin_before_transport(tmp_path: Path) -> None:
    """PC-R3: ancla no es begin; sólo el begin nuevo habilita transporte y cierre."""
    project = _Project(tmp_path, "reanchor-r3")
    _, old_head = _legacyize(project, 5)
    dry = _dry_run(project, "PC-R3")
    _assert_an_anchor(project, dry, old_head=old_head, old_seq=5, label="PC-R3")
    rejected = project.verify_begin(attempt=1)
    assert rejected.returncode != 0, "reanchor no satisface verify-begin"
    historical_record = project.record_dispatch(n=1)
    assert historical_record.returncode != 0, "el ancla no habilita record/transporte"
    assert_rc0(project.begin(attempt=1, label="fresh"), "PC-R3/fresh", "begin nuevo")
    assert_rc0(project.verify_begin(attempt=1), "PC-R3/verified", "verify-begin tras begin")
    divergent = project.begin(attempt=1, label="divergent begin")
    assert divergent.returncode != 0, "begin divergente posterior debe rechazarse"
    orphan = dict(project.body(project.head()["body_sha256"]))
    orphan["goal"] = "divergent unlinked begin"
    orphan["record"] = "begin"
    orphan.pop("prev", None)
    project.write_body(orphan)
    assert project.verify_begin(attempt=1).returncode != 0, (
        "verify-begin debe detectar begin huérfano divergente fuera de inventario")
    reconcile = project.run(CONTINUITY_CLI, "reconcile", "--project-root",
                            str(project.root), "--execution-context", str(project.ctx),
                            "--json")
    assert reconcile.returncode != 0, "reconcile debe rechazar el begin huérfano divergente"


def test_reanchor_replay_is_idempotent_and_conflicts_fail(tmp_path: Path) -> None:
    """PC-R4: replay conserva identidad y no amplía la frontera inventariada."""
    project = _Project(tmp_path, "reanchor-r4")
    _, old_head = _legacyize(project, 5)
    dry = _dry_run(project, "PC-R4")
    original = _assert_an_anchor(project, dry, old_head=old_head, old_seq=5,
                                 label="PC-R4")
    before = project.continuity_files()
    replay = project.run(CONTINUITY_CLI, "reanchor", "--project-root", str(project.root),
                         "--execution-context", str(project.ctx), "--expected-head", old_head,
                         "--approval-ref", "docs/decisions/legacy-reanchor.md",
                         "--reason", "recuperar continuidad legada", "--json")
    replay_doc = json_doc(replay, "PC-R4/replay", "replay de reanchor")
    assert replay_doc.get("idempotent") is True
    assert replay_doc.get("body_sha256") == original.get("body_sha256")
    assert project.continuity_files() == before
    conflict = project.run(CONTINUITY_CLI, "reanchor", "--project-root", str(project.root),
                           "--execution-context", str(project.ctx), "--expected-head", old_head,
                           "--approval-ref", "docs/decisions/legacy-reanchor.md",
                           "--reason", "otro motivo", "--json")
    assert conflict.returncode == 1, "motivo divergente debe ser conflicto de contrato"


def test_reanchor_pc_r4_replay_after_begin_and_checkpoint(tmp_path: Path) -> None:
    project = _Project(tmp_path, "reanchor-r4-after-links")
    old_head, dry, approval = _ready_legacy(project)
    original = json_doc(_reanchor(project, old_head), "PC-R4/original", "reanclaje inicial")
    approval_bytes = approval.read_bytes()
    assert_rc0(project.begin(attempt=1, label="after anchor"), "PC-R4/begin",
               "begin posterior")
    assert_rc0(project.checkpoint(attempt=1, label="after anchor checkpoint"),
               "PC-R4/checkpoint", "checkpoint posterior")
    before = _continuity_bytes(project)
    replay = json_doc(_reanchor(project, old_head), "PC-R4/replay-after-links",
                      "replay tras begin y checkpoint")
    assert replay.get("idempotent") is True
    assert replay.get("body_sha256") == original.get("body_sha256")
    assert _continuity_bytes(project) == before

    alternate = project.root / "docs" / "decisions" / "same-approval-other-path.md"
    alternate.write_bytes(approval_bytes)
    before = _continuity_bytes(project)
    _assert_rc1_unchanged(
        project, _reanchor(project, old_head, "docs/decisions/same-approval-other-path.md"),
        "replay con approval-ref distinto", before)

    approval.write_bytes(approval_bytes + b"\n# bytes changed after approval\n")
    before = _continuity_bytes(project)
    _assert_rc1_unchanged(project, _reanchor(project, old_head),
                          "replay con bytes de aprobación distintos", before)


def test_reanchor_pc_r4_replay_rejects_alternate_approval_path(tmp_path: Path) -> None:
    project = _Project(tmp_path, "r4-alternate-approval-path")
    old_head, _, approval = _ready_legacy(project)
    _reanchor(project, old_head)
    alternate = project.root / "docs" / "decisions" / "approval-alias.md"
    alternate.parent.mkdir(parents=True, exist_ok=True)
    alternate.write_bytes(approval.read_bytes())
    before = _continuity_bytes(project)
    replay = _reanchor(project, old_head, "docs/decisions/approval-alias.md")
    _assert_rc1_unchanged(project, replay, "replay con --approval-ref distinto", before)


def test_reanchor_pc_r4_replay_rejects_modified_approval_bytes(tmp_path: Path) -> None:
    project = _Project(tmp_path, "r4-modified-approval")
    old_head, _, approval = _ready_legacy(project)
    _reanchor(project, old_head)
    approval.write_bytes(approval.read_bytes() + b"\\nmodificacion posterior\\n")
    before = _continuity_bytes(project)
    replay = _reanchor(project, old_head)
    _assert_rc1_unchanged(project, replay, "replay con bytes de aprobación modificados", before)


def test_reanchor_preconditions_fail_closed(tmp_path: Path) -> None:
    """PC-R5: todos los rechazos son fail-closed; dueño directo puede aprobar."""
    # Valida primero la superficie para que el rc=2 de argparse por subcomando
    # inexistente no pueda satisfacer falsamente el caso de argumentos incompletos.
    project = _Project(tmp_path, "reanchor-r5")
    help_proc = project.run(CONTINUITY_CLI, "reanchor", "--help")
    assert help_proc.returncode == 0, (
        "PC-R5: reanchor --help debe demostrar que existe el subcomando antes "
        f"de probar rc=2 por argumentos incompletos: {help_proc.stdout}{help_proc.stderr}")
    assert "--expected-head" in help_proc.stdout and "--approval-ref" in help_proc.stdout
    incomplete = project.run(CONTINUITY_CLI, "reanchor", "--project-root",
                             str(project.root), "--execution-context", str(project.ctx),
                             "--expected-head", "0" * 64)
    assert incomplete.returncode == 2
    assert "invalid choice" not in (incomplete.stdout + incomplete.stderr)
    assert "--approval-ref" in (incomplete.stdout + incomplete.stderr)

    _, old_head = _legacyize(project, 5)
    before = project.tree()
    dry = _dry_run(project, "PC-R5/dry-run")
    after = project.tree()
    assert before == after, "reanchor --dry-run no debe escribir artefactos"
    assert dry.get("head_sha256") == old_head
    anchor = _assert_an_anchor(project, dry, old_head=old_head, old_seq=5,
                               label="PC-R5/publication")
    assert anchor.get("pre_anchor_inventory_sha256") == dry.get("pre_anchor_inventory_sha256"), (
        "digest del inventario dry-run debe coincidir con publicación")

    # Un expected-head incorrecto rechaza sin alterar ni un byte de continuidad.
    project = _Project(tmp_path / "wrong-head", "wrong-head")
    _, old_head = _legacyize(project, 5)
    dry = _dry_run(project, "PC-R5/wrong-head/dry")
    _write_approval(project, dry)
    before_continuity = _continuity_bytes(project)
    _assert_rc1_unchanged(project, _reanchor(project, "0" * 64),
                          "expected-head discordante", before_continuity)

    # Cada campo de la aprobación debe coincidir exactamente con la frontera.
    for field, altered in (
        ("execution", {"execution_id": "foreign-execution"}),
        ("head", {"head_sha256": "0" * 64}),
        ("inventory", {"inventory_sha256": "f" * 64}),
    ):
        project = _Project(tmp_path / f"approval-{field}", f"approval-{field}")
        _, old_head = _legacyize(project, 5)
        dry = _dry_run(project, f"PC-R5/approval-{field}/dry")
        _write_approval(project, dry, execution_id=altered.get("execution_id"),
                        head_sha256=altered.get("head_sha256"),
                        inventory_sha256=altered.get("inventory_sha256"))
        before_continuity = _continuity_bytes(project)
        _assert_rc1_unchanged(project, _reanchor(project, old_head),
                              f"aprobación {field} discordante", before_continuity)

    # El inventario cambia luego de aprobar: el digest aprobado ya no autoriza
    # la lista actual, y el fallo no toca el almacenamiento de continuidad.
    project = _Project(tmp_path / "changed-inventory", "changed-inventory")
    _, old_head = _legacyize(project, 5)
    dry = _dry_run(project, "PC-R5/changed-inventory/dry")
    _write_approval(project, dry)
    added = dict(project.body(old_head))
    added["goal"] = "body added after inventory approval"
    project.write_body(added)
    before_continuity = _continuity_bytes(project)
    _assert_rc1_unchanged(project, _reanchor(project, old_head),
                          "inventario cambiado", before_continuity)

    # Revocación registrada y delegación expirada son estados distintos y
    # ambos deben fallar cerrados sin publicar el ancla.
    for kind in ("revoked", "expired"):
        project = _Project(tmp_path / f"authority-{kind}", f"authority-{kind}")
        _, old_head = _legacyize(project, 5)
        dry = _dry_run(project, f"PC-R5/authority-{kind}/dry")
        _write_approval(project, dry)
        state = project.read_state()
        if kind == "revoked":
            state["hitl_delegation"]["status"] = "user-revoked"
            (project.root / "docs/.cdad-state.json").write_text(
                json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            context = json.loads(project.ctx.read_text(encoding="utf-8"))
            context["hitl_delegation"] = {
                "authority_ref": "docs/epics/epic-004-single-source-planning/execution.md",
                "expires_on": "2020-01-01",
            }
            project.ctx.write_text(json.dumps(context, sort_keys=True) + "\n",
                                   encoding="utf-8")
        before_continuity = _continuity_bytes(project)
        _assert_rc1_unchanged(project, _reanchor(project, old_head),
                              f"delegación {kind}", before_continuity)

    # Un despacho ya registrado es un efecto durable: reanchor no puede
    # omitirlo ni modificar continuity/ al rechazar.
    project = _Project(tmp_path / "registered-dispatch", "registered-dispatch")
    old_head, dry, _ = _ready_legacy(project)
    project.mark_dispatched()
    before_continuity = _continuity_bytes(project)
    effects = project.run(CONTINUITY_CLI, "reanchor", "--project-root", str(project.root),
                          "--execution-context", str(project.ctx), "--dry-run", "--json")
    _assert_rc1_unchanged(project, effects, "despacho ya registrado", before_continuity)
    _assert_rc1_unchanged(project, _reanchor(project, old_head),
                          "publicación con despacho registrado", before_continuity)

    # Sin delegación registrada, la decisión del dueño directo (ya acreditada
    # por la aprobación documental fixture) sigue siendo admisible.
    project = _Project(tmp_path / "direct-owner", "direct-owner")
    _, old_head = _legacyize(project, 5)
    dry = _dry_run(project, "PC-R5/direct-owner/dry")
    state = project.read_state()
    state["hitl_delegation"] = None
    (project.root / "docs/.cdad-state.json").write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
    context = json.loads(project.ctx.read_text(encoding="utf-8"))
    context.pop("hitl_delegation", None)
    project.ctx.write_text(json.dumps(context, sort_keys=True) + "\n", encoding="utf-8")
    _write_approval(project, dry)
    direct = _reanchor(project, old_head)
    assert_rc0(direct, "PC-R5/direct-owner", "aprobación directa del dueño sin delegación")


def test_reanchor_pc_r5_rejects_demonstrable_modern_genesis(tmp_path: Path) -> None:
    """Una cadena demostrable iniciada con begin no es reparable por reanchor."""
    project = _Project(tmp_path, "r5-demonstrable")
    assert_rc0(project.begin(attempt=1), "PC-R5/modern-begin", "begin moderno")
    old_head = project.head()["body_sha256"]
    assert project.head().get("seq") == 1
    assert project.body(old_head).get("prev") is None
    # La aprobación se construye con la frontera exacta aunque dry-run también
    # deba rechazar; evita atribuir el rechazo a una aprobación discordante.
    inventory = sorted(project.bodies())
    inventory_sha = hashlib.sha256(
        json.dumps(inventory, separators=(",", ":")).encode("utf-8")).hexdigest()
    dry_data = {"execution_id": project.execution_id, "head_sha256": old_head,
                "pre_anchor_inventory_sha256": inventory_sha}
    _write_approval(project, dry_data)
    before = _continuity_bytes(project)
    dry = project.run(CONTINUITY_CLI, "reanchor", "--project-root", str(project.root),
                      "--execution-context", str(project.ctx), "--dry-run", "--json")
    violations = []
    if dry.returncode != 1:
        violations.append(f"dry-run debió rc=1, obtuvo {dry.returncode}")
    if _continuity_bytes(project) != before:
        violations.append("dry-run alteró continuity/")
    publish = _reanchor(project, old_head)
    if publish.returncode != 1:
        violations.append(f"publicación debió rc=1, obtuvo {publish.returncode}")
    if _continuity_bytes(project) != before:
        violations.append("publicación alteró continuity/")
    assert not violations, "génesis moderno demostrable: " + "; ".join(violations)


def test_reanchor_pc_r2_rejects_oversized_anchor_without_inventory(tmp_path: Path) -> None:
    project = _Project(tmp_path, "r2-oversized-reason")
    old_head, dry, _ = _ready_legacy(project)
    huge_reason = "motivo autorizado " + ("x" * 17000)
    _write_approval(project, dry, reason=huge_reason)
    before = _continuity_bytes(project)
    rejected = _reanchor(project, old_head, reason=huge_reason)
    _assert_rc1_unchanged(project, rejected,
                          "cuerpo de ancla sobredimensionado sin inventario", before)


def test_reanchor_pc_r5_rejects_packet_not_prepared(tmp_path: Path) -> None:
    project = _Project(tmp_path, "r5-not-prepared")
    old_head, dry, _ = _ready_legacy(project)
    state = project.read_state()
    state["active_packet"]["status"] = "dispatched"
    (project.root / "docs/.cdad-state.json").write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
    before = _continuity_bytes(project)
    _assert_rc1_unchanged(project, _reanchor(project, old_head),
                          "paquete fuera de prepared", before)


def test_reanchor_pc_r5_rejects_existing_receipt_even_if_empty(tmp_path: Path) -> None:
    project = _Project(tmp_path, "r5-existing-receipt")
    old_head, _, _ = _ready_legacy(project)
    receipt = project.receipt_path()
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_bytes(b"{}")
    before = _continuity_bytes(project)
    _assert_rc1_unchanged(project, _reanchor(project, old_head),
                          "recibo existente vacío", before)


def test_reanchor_pc_r5_rejects_registered_disposition(tmp_path: Path) -> None:
    project = _Project(tmp_path, "r5-disposition")
    old_head, _, _ = _ready_legacy(project)
    dispatch_record = project.mark_dispatched()
    disposition = project.transition("disposition", packet=project.packet_id,
                                     resolution="abandoned")
    assert_rc0(disposition, "PC-R5/disposition-fixture", "disposición fixture")
    # Keep the real registered disposition as the sole durable precondition:
    # remove its prerequisite dispatch record and restore the packet to
    # prepared, so neither condition can mask a missing disposition check.
    dispatch_record.unlink()
    state = project.read_state()
    state["active_packet"]["status"] = "prepared"
    (project.root / "docs/.cdad-state.json").write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
    before = _continuity_bytes(project)
    rejected = _reanchor(project, old_head)
    _assert_rc1_unchanged(project, rejected, "disposición registrada", before)
    diagnostic = (rejected.stdout + rejected.stderr).lower()
    assert "disposition" in diagnostic or "disposici" in diagnostic, (
        "el rechazo debe nombrar la disposición; no basta el despacho previo: "
        f"{diagnostic}")


def test_reanchor_pc_r5_rejects_inconclusive_dispatch_signal(tmp_path: Path) -> None:
    project = _Project(tmp_path, "r5-inconclusive-signal")
    old_head, _, _ = _ready_legacy(project)
    # A complete JSON object without packet identity is still inconclusive,
    # not a canonical dispatch and not evidence that no dispatch happened.
    dispatch_dir = (project.root / ".cdad" / "executions" / project.execution_id
                    / "dispatches")
    dispatch_dir.mkdir(parents=True, exist_ok=True)
    (dispatch_dir / "partial.json").write_text("{}", encoding="utf-8")
    before = _continuity_bytes(project)
    _assert_dry_run_and_publish_reject_without_writes(
        project, old_head, "dispatches/partial.json sin packet_id", before)


def test_reanchor_pc_r5_rejects_unverifiable_delegation(tmp_path: Path) -> None:
    project = _Project(tmp_path, "r5-unverifiable-authority")
    old_head, _, _ = _ready_legacy(project)
    context = json.loads(project.ctx.read_text(encoding="utf-8"))
    context["hitl_delegation"] = {
        "authority_ref": "docs/decisions/missing-authority.md",
        "expires_on": "2026-12-31",
    }
    project.ctx.write_text(json.dumps(context, sort_keys=True) + "\n", encoding="utf-8")
    before = _continuity_bytes(project)
    _assert_rc1_unchanged(project, _reanchor(project, old_head),
                          "delegación con authority_ref inexistente", before)


def test_reanchor_pc_r5_rejects_unknown_registered_delegation(tmp_path: Path) -> None:
    project = _Project(tmp_path, "r5-unknown-registered-authority")
    old_head, _, _ = _ready_legacy(project)
    authority = project.root / AUTHORITY_REF
    assert authority.is_file(), "fixture debe conservar la referencia de autoridad existente"
    state = project.read_state()
    delegation = dict(state["hitl_delegation"])
    delegation["status"] = "unknown"
    delegation["state"] = "unknown"
    state["hitl_delegation"] = delegation
    (project.root / "docs/.cdad-state.json").write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
    context = json.loads(project.ctx.read_text(encoding="utf-8"))
    context["hitl_delegation"] = {
        "authority_ref": AUTHORITY_REF,
        "state": "unknown",
        "expires_on": "2099-12-31",
    }
    project.ctx.write_text(json.dumps(context, sort_keys=True) + "\n", encoding="utf-8")
    before = _continuity_bytes(project)
    _assert_dry_run_and_publish_reject_without_writes(
        project, old_head, "delegación state=unknown con authority_ref existente", before)


def test_reanchor_pc_r6_orphan_divergent_begin_rejected(tmp_path: Path) -> None:
    """Cadena íntegra + huérfano divergente: cada consumidor rechaza por separado."""
    project = _Project(tmp_path, "r6-orphan")
    _reanchored_segment(project, "PC-R6/orphan", checkpoints=0)
    # Deja el begin como cabeza para que verify-begin sea una comprobación
    # positiva antes de introducir el cuerpo huérfano.
    assert_rc0(project.verify_begin(attempt=1), "PC-R6/orphan/baseline-verify",
               "begin vigente antes del huérfano")
    assert_rc0(project.resume(), "PC-R6/orphan/baseline-resume", "segmento íntegro")
    assert_rc0(project.run(CONTINUITY_CLI, "reconcile", "--project-root",
                           str(project.root), "--execution-context", str(project.ctx),
                           "--json"), "PC-R6/orphan/baseline-reconcile", "segmento íntegro")
    orphan = dict(project.body(project.head()["body_sha256"]))
    orphan["record"] = "begin"
    orphan["goal"] = "divergent unlisted begin after approved boundary"
    orphan.pop("prev", None)
    project.write_body(orphan)
    before = _continuity_bytes(project)
    commands = {
        "verify-begin": project.verify_begin(attempt=1),
        "resume": project.resume(),
        "reconcile": project.run(CONTINUITY_CLI, "reconcile", "--project-root",
                                 str(project.root), "--execution-context", str(project.ctx),
                                 "--json"),
    }
    violations = []
    for consumer, proc in commands.items():
        if proc.returncode == 0:
            violations.append(f"{consumer}: aceptó el begin huérfano divergente")
        if _continuity_bytes(project) != before:
            violations.append(f"{consumer}: escribió durante el rechazo")
    assert not violations, "; ".join(violations)


def test_reanchor_pc_r6_interior_corruption_rejected(tmp_path: Path) -> None:
    """Corrupción interior sin huérfano: verify-begin/resume/reconcile rechazan."""
    project = _Project(tmp_path, "r6-interior-corruption")
    _reanchored_segment(project, "PC-R6/corruption")
    # Abrir otro intento legítimo deja un begin vigente en cabeza y varios
    # eslabones anteriores para corromper fuera de cabeza/predecesor inmediato.
    assert_rc0(project.begin(attempt=2, label="current attempt"),
               "PC-R6/current-begin", "begin de intento vigente")
    assert_rc0(project.verify_begin(attempt=2), "PC-R6/valid-verify", "cadena válida")
    assert_rc0(project.resume(), "PC-R6/valid-resume", "cadena válida")
    assert_rc0(project.run(CONTINUITY_CLI, "reconcile", "--project-root",
                           str(project.root), "--execution-context", str(project.ctx),
                           "--json"), "PC-R6/valid-reconcile", "cadena válida")
    chain = project.chain()
    assert len(chain) >= 7
    sha, body = chain[3]
    broken = dict(body)
    broken["tampered_contract_field"] = True
    project.body_path(sha).write_bytes(canonical_body_bytes(broken))
    before = _continuity_bytes(project)
    commands = {
        "verify-begin": project.verify_begin(attempt=2),
        "resume": project.resume(),
        "reconcile": project.run(CONTINUITY_CLI, "reconcile", "--project-root",
                                 str(project.root), "--execution-context", str(project.ctx),
                                 "--json"),
    }
    violations = []
    for consumer, proc in commands.items():
        if proc.returncode == 0:
            violations.append(f"{consumer}: aceptó la corrupción interior")
        if _continuity_bytes(project) != before:
            violations.append(f"{consumer}: escribió durante el rechazo")
    assert not violations, "; ".join(violations)
    dry = project.run(CONTINUITY_CLI, "reanchor", "--project-root", str(project.root),
                      "--execution-context", str(project.ctx), "--dry-run", "--json")
    _assert_rc1_unchanged(project, dry, "reanchor no oculta corrupción moderna", before)


def test_reanchor_does_not_rehabilitate_legacy_evidence(tmp_path: Path) -> None:
    """PC-R7: la evidencia histórica se conserva, pero no cruza el ancla."""
    project = _Project(tmp_path, "reanchor-r7")
    archived, old_head = _legacyize(project, 5)
    # Evidencia real de fixture en el cuerpo legado: sólo bytes/referencias, no
    # se la declara vigente en el segmento posterior.
    evidence_path = project.root / "docs" / "evidence" / "legacy.txt"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text("historical evidence\n", encoding="utf-8")
    old_body = project.body(old_head)
    old_body["evidence"] = [{
        "id": "legacy-proof", "reference": {
            "path": "docs/evidence/legacy.txt",
            "sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest()},
        "status": "vigente", "reason": "evidencia histórica", "antecedent": None,
    }]
    old_raw = canonical_body_bytes(old_body)
    old_head = sha256_bytes(old_raw)
    project.body_path(old_head).write_bytes(old_raw)
    head = project.head()
    head["body_sha256"] = old_head
    project.write_head(head)
    evidence_bytes = evidence_path.read_bytes()
    historical_bodies = _body_bytes(project)
    dry = _dry_run(project, "PC-R7")
    _assert_an_anchor(project, dry, old_head=old_head, old_seq=5, label="PC-R7")
    assert evidence_path.read_bytes() == evidence_bytes
    after_bodies = _body_bytes(project)
    assert set(historical_bodies) <= set(after_bodies), (
        "reanclar debe conservar todos los archivos de cuerpo históricos")
    assert {name: after_bodies[name] for name in historical_bodies} == historical_bodies, (
        "reanclar debe conservar byte a byte el snapshot completo de cuerpos históricos")
    projection = json_doc(project.resume(), "PC-R7/resume", "resume tras reanchor")
    evidence = projection.get("projection", {}).get("evidence", [])
    assert not any(item.get("id") == "legacy-proof" and item.get("status") == "vigente"
                   for item in evidence), "reanclar no rehabilita evidencia histórica"
    assert all(project.body_path(sha).is_file() for sha in archived)
    assert_rc0(project.begin(attempt=1, label="fresh evidence segment"),
               "PC-R7/fresh-begin", "begin del segmento nuevo")
    cross_boundary = project.checkpoint(
        attempt=1, label="cross-boundary evidence", evidence=[{
            "id": "new-proof", "reference": {
                "path": "docs/evidence/legacy.txt",
                "sha256": hashlib.sha256(evidence_bytes).hexdigest()},
            "status": "vigente", "reason": "intento de usar evidencia legada",
            "antecedent": {"body_sha256": old_head, "evidence_id": "legacy-proof"},
        }])
    assert cross_boundary.returncode != 0, (
        "UPDATE no debe aceptar evidencia cuyo antecedente cruza el ancla")
