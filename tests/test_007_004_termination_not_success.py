"""RED 007-004 — delivery distinguishes staged, received and none.

Each stable test maps one-to-one to PC-01..PC-18 in the approved spec. CLI
integration cases use the disposable project/runtime fixtures from 007-003;
no product module is imported or inspected by this test-writer.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from test_007_003_continuity_at_edges import (
    _Project,
    _Stage,
    FIXTURE_ATTEMPT_ID,
    FIXTURE_MODULE_SOURCE,
    FIXTURE_RUNTIME,
    FIXTURE_SESSION,
    RESULT_CLI,
    _orphan_receipt,
    REPO_ROOT,
    SKILL_DIR,
)

SPEC = REPO_ROOT / "docs/specs/007-004-termination-not-success/spec.md"
DELIVERY_VALUES = {"none", "staged", "received"}


def _envelope(proc, pc: str) -> dict:
    output = (proc.stdout or "") + (proc.stderr or "")
    assert proc.returncode == 0, f"{pc}: CLI envelope expected (rc=0): {output[-1200:]}"
    assert proc.stdout.strip(), f"{pc}: expected JSON envelope on stdout"
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{pc}: stdout must be a JSON envelope") from exc
    assert isinstance(result, dict), f"{pc}: envelope must be a JSON object"
    return result


def _delivery(envelope: dict, pc: str, expected: str) -> None:
    assert "delivery" in envelope, f"{pc}: new envelope must contain delivery"
    assert envelope["delivery"] == expected, (
        f"{pc}: expected delivery={expected!r}, got {envelope['delivery']!r}")
    assert envelope.get("delivery_ref") is not None if expected != "none" else \
        envelope.get("delivery_ref") is None, f"{pc}: delivery_ref conflicts with delivery"


def _adapter_emits(stage, envelope: dict) -> None:
    """Make the fixture adapter print exactly `envelope` on its transport call."""
    runtime_module = stage.scripts / f"cdad_delegate_{FIXTURE_RUNTIME}.py"
    source = runtime_module.read_text(encoding="utf-8")
    marker = 'if _direct():\n    sys.stdout.write(json.dumps(envelope, sort_keys=True) + "\\n")'
    assert marker in source, "fixture marker for the transport envelope is missing"
    source = source.replace(marker, f"envelope = {envelope!r}\n" + marker)
    runtime_module.write_text(source, encoding="utf-8")


def _orientation(fx) -> dict:
    """Projection of the 007-001 orientation contract: situation + next.operation."""
    proc = fx.run(fx_packet_cli(), "status", "--project-root", str(fx.root))
    assert proc.returncode == 0, f"orientation status failed: {(proc.stdout + proc.stderr)[-800:]}"
    doc = json.loads(proc.stdout)
    assert "situation" in doc and isinstance(doc.get("next"), dict) \
        and "operation" in doc["next"], f"orientation shape (007-001) missing: {sorted(doc)}"
    return {"situation": doc["situation"], "next.operation": doc["next"]["operation"]}


def fx_packet_cli() -> Path:
    return SKILL_DIR / "scripts" / "cdad_packet.py"


def _fx_source(stage):
    return stage.scripts / f"cdad_delegate_{FIXTURE_RUNTIME}.py"


def _patch_adapter(stage, old: str, new: str) -> None:
    module = _fx_source(stage)
    source = module.read_text(encoding="utf-8")
    assert old in source, f"fixture marker missing: {old!r}"
    module.write_text(source.replace(old, new), encoding="utf-8")


_SEND = 'if _direct():\n    sys.stdout.write(json.dumps(envelope, sort_keys=True) + "\\n")'


def _side_effects(fx) -> tuple:
    """Observable acceptance effects: attempts ledger, staging, receipts."""
    results = fx.root / ".cdad/runtime/results"
    receipts = sorted(str(p) for p in results.rglob("*") if p.is_file()) if results.is_dir() else []
    return (fx.dispatch_files(), fx.inbox_files(), receipts)


def _received_project(base: Path):
    """A project whose errand already has a real, linked durable receipt."""
    fx = _Project(base)
    assert fx.begin(attempt=1).returncode == 0, "fixture: begin"
    recorded = fx.record_dispatch(n=1)
    assert recorded.returncode == 0, f"fixture: record dispatch: {recorded.stderr[-600:]}"
    received = fx.receive(n=1)
    assert received.returncode == 0, f"fixture: receive: {(received.stdout + received.stderr)[-600:]}"
    assert fx.receipt_path().is_file(), "fixture: durable receipt"
    return fx


def _opencode_case():
    from test_006_005_u2_opencode_module import U2ModuleCase
    case = U2ModuleCase()
    case.setUp()
    return case


def _validate(root: Path, receipt: str) -> subprocess.CompletedProcess:
    path = Path(receipt)
    if not path.is_absolute():
        path = root / path
    return subprocess.run([sys.executable, str(RESULT_CLI), "validate-receipt",
                           "--project-root", str(root), "--receipt", str(path)],
                          capture_output=True, text=True, timeout=120)


def _external(tmp_path: Path):
    project = _Project(tmp_path)
    stage = _Stage(tmp_path)
    return project, stage


def test_007_004_record_payload_is_staged_not_received(tmp_path: Path) -> None:
    """PC-01: prepared payload is staged, byte-preserved, without a receipt."""
    fx, stage = _external(tmp_path)
    payload = b"# fixture payload\r\nbytes stay exact"
    source = tmp_path / "payload.md"
    source.write_bytes(payload)
    proc = stage.record(fx, "--native-result", str(source))
    envelope = _envelope(proc, "PC-01")
    _delivery(envelope, "PC-01", "staged")
    ref = Path(envelope["delivery_ref"])
    if not ref.is_absolute():
        ref = fx.root / ref
    assert ref.is_file(), "PC-01: staged reference must identify an existing descriptor"
    assert any(p.read_bytes() == payload for p in (fx.root / ".cdad/inbox").rglob("*") if p.is_file()), \
        "PC-01: payload bytes must be preserved in staging"
    assert not fx.receipt_path().exists(), "PC-01: record must not create a durable receipt"


def test_007_004_record_without_payload_has_no_delivery(tmp_path: Path) -> None:
    """PC-02: no payload records an attempt but declares no delivery."""
    fx, stage = _external(tmp_path)
    envelope = _envelope(stage.record(fx), "PC-02")
    assert envelope.get("termination") == "unknown", "PC-02: no-payload record is unknown"
    _delivery(envelope, "PC-02", "none")
    assert not (fx.root / ".cdad/inbox/RESULT.json").exists(), "PC-02: no descriptor may be staged"


def test_007_004_record_contradiction_blocks_without_effects(tmp_path: Path) -> None:
    """PC-03: contradictory correlation blocks with no effects and rc=0."""
    fx, stage = _external(tmp_path)
    # The adapter double observes the requested session in a SIBLING project
    # directory (neither the root, a descendant nor an ancestor): a real
    # contradiction, not an unknown identity.
    sibling = tmp_path / "sibling-project-007004"
    sibling.mkdir()
    assert sibling != fx.root and sibling != fx.root.parent
    assert not str(sibling).startswith(str(fx.root) + "/")
    row = {"id": "requested-session", "directory": str(sibling)}
    runtime_module = stage.scripts / f"cdad_delegate_{FIXTURE_RUNTIME}.py"
    source = runtime_module.read_text(encoding="utf-8")
    source = source.replace('"session_correlation": False', '"session_correlation": True')
    source = source.replace('sys.stdout.write("null\\n")',
                            f'sys.stdout.write(json.dumps({row!r}) + "\\n")')
    runtime_module.write_text(source, encoding="utf-8")
    assert fx.begin(attempt=1).returncode == 0, "PC-03 fixture: begin continuity"
    payload = tmp_path / "contradictory.md"
    payload.write_text("contradictory correlation fixture\n", encoding="utf-8")
    dispatches_before = fx.dispatch_files()
    inbox_before = fx.inbox_files()
    proc = stage.record(fx, "--continuity-attempt", "1", "--session", "requested-session",
                        "--native-result", str(payload))
    envelope = _envelope(proc, "PC-03")
    assert envelope.get("termination") == "blocked", (
        f"PC-03: contradiction must be blocked, got {envelope!r}")
    _delivery(envelope, "PC-03", "none")
    assert envelope.get("diagnosis"), "PC-03: block must be diagnosable"
    assert fx.dispatch_files() == dispatches_before, "PC-03: rejected attempt must not be registered"
    assert fx.inbox_files() == inbox_before, "PC-03: rejection must not stage a delivery"
    assert not fx.receipt_path().exists(), "PC-03: contradictory observation must not create a receipt"


def test_007_004_opencode_completed_has_valid_received_delivery() -> None:
    """PC-04: the real OpenCode adapter (runtime double) declares received; ref validates."""
    case = _opencode_case()
    try:
        ctx = case.new_project()
        fake = case.fake_runtime()
        proc = case.dispatch(ctx, fake)
        envelope = _envelope(subprocess.CompletedProcess(proc.args, proc.returncode,
                             proc.stdout.decode(), proc.stderr.decode()), "PC-04")
        assert envelope.get("termination") == "completed", f"PC-04: fixture completes: {envelope!r}"
        _delivery(envelope, "PC-04", "received")
        checked = _validate(ctx["root"], envelope["delivery_ref"])
        assert checked.returncode == 0, f"PC-04: received ref must pass validate-receipt: {checked.stderr[-600:]}"
    finally:
        case._tmp.cleanup()


# Scenario -> exact termination. The producer runs as a process against the
# U2 runtime double; the observed `session_v2` row is injected by that double
# (`outcome` = idle_outcome). `client-hangs` replaces the double's `run` with a
# client that never finishes and writes no row, under a short wait bound. The
# mapping reuses 005-009 T2 (failed/interrupted/hangs/unknown-outcome).
_PC05_SCENARIOS = {
    "idle-failed": "blocked",
    "client-refuses": "blocked",
    "binary-missing": "transport-error",
    "client-hangs": "timeout",
    "interrupted": "cancelled",
    "undeclared-outcome": "unknown",
}


@pytest.mark.parametrize(("scenario", "expected"), sorted(_PC05_SCENARIOS.items()))
def test_007_004_opencode_noncompleted_never_claims_delivery(scenario: str, expected: str) -> None:
    """PC-05: each non-completed OpenCode termination is exact, with none/null delivery."""
    from test_006_001_t1_selection import FAST_WAIT
    case = _opencode_case()
    try:
        ctx = case.new_project()
        outcome = {"idle-failed": "failed", "interrupted": "interrupted",
                   "undeclared-outcome": "fixture-undeclared-outcome"}.get(scenario, "succeeded")
        fake = case.fake_runtime(outcome=outcome,
                                 require_credential=scenario == "client-refuses")
        if scenario == "binary-missing":
            case.patch_config(fake, {"binary": str(fake["dir"] / "bin" / "absent-opencode")})
        if scenario == "client-hangs":
            source = fake["binary"].read_text(encoding="utf-8")
            marker = "_spec = json.loads("
            assert marker in source, "PC-05 fixture: runtime double marker"
            fake["binary"].write_text(source.replace(
                marker, "if 'run' in _argv:\n    time.sleep(60)\n" + marker, 1), encoding="utf-8")
            case.patch_config(fake, {"wait": dict(FAST_WAIT, timeout_seconds=5)})
        proc = case.dispatch(ctx, fake)
        out = (proc.stdout or b"").decode()
        assert proc.returncode == 0 and out.strip(), (
            f"PC-05[{scenario}]: producer must emit an envelope: rc={proc.returncode} "
            f"{(proc.stderr or b'').decode()[-600:]}")
        envelope = json.loads(out)
        assert envelope.get("termination") == expected, (
            f"PC-05[{scenario}]: expected termination {expected!r}: {envelope!r}")
        _delivery(envelope, f"PC-05[{scenario}]", "none")
        assert envelope.get("delivery_ref") is None, f"PC-05[{scenario}]: delivery_ref must be null"
    finally:
        case._tmp.cleanup()


_RELAYED = [
    {"attempt": "attempt-relay-007004", "session": "ses-relay-007004", "termination": "blocked",
     "delivery": "none", "delivery_ref": None, "diagnosis": "relay fixture: blocked"},
    {"attempt": "attempt-relay-007004", "session": None, "termination": "unknown",
     "delivery": "none", "delivery_ref": None, "diagnosis": "relay fixture: unknown"},
]


@pytest.mark.parametrize("relayed", _RELAYED, ids=["blocked", "unknown"])
def test_007_004_delegate_relays_delivery_without_duplicate_effects(tmp_path: Path, relayed: dict) -> None:
    """PC-06: delegate preserves the six fields exactly, with no extra effects."""
    fx, stage = _external(tmp_path)
    _adapter_emits(stage, relayed)
    before = _side_effects(fx)
    envelope = _envelope(stage.delegate(fx), "PC-06")
    assert {k: envelope.get(k) for k in relayed} == relayed, f"PC-06: six fields must be relayed exactly: {envelope!r}"
    assert _side_effects(fx) == before, "PC-06: relay must not register, stage or receive"


@pytest.mark.parametrize("relayed", _RELAYED, ids=["blocked", "unknown"])
def test_007_004_dispatch_relays_external_delivery(tmp_path: Path, relayed: dict) -> None:
    """PC-07: dispatch preserves the validated envelope exactly, no extra effects."""
    fx, stage = _external(tmp_path)
    _adapter_emits(stage, relayed)
    before = _side_effects(fx)
    envelope = _envelope(stage.dispatch(fx), "PC-07")
    assert {k: envelope.get(k) for k in relayed} == relayed, f"PC-07: envelope must be relayed exactly: {envelope!r}"
    assert _side_effects(fx) == before, "PC-07: dispatch must not stage, receive or add attempts"


@pytest.mark.parametrize(("termination", "delivery", "ref_kind"), [
    ("completed", "none", "null"),
    ("blocked", "staged", "valid"), ("blocked", "received", "valid"),
    ("transport-error", "staged", "valid"), ("transport-error", "received", "valid"),
    ("timeout", "staged", "valid"), ("timeout", "received", "valid"),
    ("cancelled", "staged", "valid"), ("cancelled", "received", "valid"),
    ("unknown", "staged", "valid"), ("unknown", "received", "valid"),
    ("completed", "staged", "null"), ("completed", "staged", "empty"),
    ("completed", "staged", "wrong-type"),
    ("completed", "received", "null"), ("completed", "received", "empty"),
    ("completed", "received", "wrong-type"),
    ("blocked", "none", "valid"), ("transport-error", "none", "valid"),
    ("timeout", "none", "valid"), ("cancelled", "none", "valid"),
    ("unknown", "none", "valid"),
    ("not-a-termination", "none", "null"), ("completed", "unknown", "valid"),
])
def test_007_004_delegate_rejects_invalid_delivery_combinations(
    tmp_path: Path, termination: str, delivery: str, ref_kind: str,
) -> None:
    """PC-08: invalid envelope combinations fail closed with a protocol diagnostic."""
    fx, stage = _external(tmp_path)
    ref = {"null": None, "empty": "", "valid": "/fixture/artifact",
           "wrong-type": 17}[ref_kind]
    malformed = {"attempt": "attempt-fixture-007-003",
                 "session": "ses-fixture-007-003",
                 "termination": termination, "delivery": delivery,
                 "delivery_ref": ref, "diagnosis": None}
    runtime_module = stage.scripts / f"cdad_delegate_{FIXTURE_RUNTIME}.py"
    source = runtime_module.read_text(encoding="utf-8")
    source = source.replace('if _direct():\n    sys.stdout.write(json.dumps(envelope, sort_keys=True) + "\\n")',
                            f'envelope = {malformed!r}\nif _direct():\n    sys.stdout.write(json.dumps(envelope, sort_keys=True) + "\\n")')
    runtime_module.write_text(source, encoding="utf-8")
    envelope = _envelope(stage.delegate(fx), "PC-08")
    assert envelope.get("termination") == "transport-error", "PC-08: invalid adapter envelope must be rejected"
    _delivery(envelope, "PC-08", "none")
    assert envelope.get("diagnosis"), "PC-08: protocol rejection must be diagnosed"


def test_007_004_external_route_rejects_staged_delivery(tmp_path: Path) -> None:
    """PC-09: external arrivals reject completed/staged even though record may emit it."""
    fx, stage = _external(tmp_path)
    staged = fx.root / ".cdad/inbox/RESULT.json"
    _adapter_emits(stage, {"attempt": "attempt-fixture-007-003", "session": "ses-fixture-007-003",
                           "termination": "completed", "delivery": "staged",
                           "delivery_ref": str(staged), "diagnosis": None})
    inbox_before = fx.inbox_files()
    proc = stage.dispatch(fx)
    envelope = _envelope(proc, "PC-09")  # rc 0: an envelope was produced (spec §7)
    assert envelope.get("termination") == "transport-error", (
        f"PC-09: external completed/staged must be a protocol rejection, got {envelope!r}")
    _delivery(envelope, "PC-09", "none")
    assert envelope.get("diagnosis"), "PC-09: rejection must be diagnosed"
    assert fx.inbox_files() == inbox_before, "PC-09: rejection must not stage anything"
    assert not fx.receipt_path().exists(), "PC-09: rejection must not receive"


@pytest.mark.parametrize("failure", ["no-envelope", "unreadable", "start-failure", "own-timeout"])
def test_007_004_transport_failures_have_no_delivery(tmp_path: Path, failure: str) -> None:
    """PC-10: unusable/absent adapter output and own timeout have no delivery."""
    fx, stage = _external(tmp_path)
    expected = "transport-error"
    if failure == "no-envelope":
        _patch_adapter(stage, _SEND, "sys.exit(0)")
    elif failure == "unreadable":
        _patch_adapter(stage, _SEND, 'sys.stdout.write("{not json\\n"); sys.exit(0)')
    elif failure == "start-failure":
        _fx_source(stage).write_text("this is not python (\n", encoding="utf-8")
    else:
        expected = "timeout"
        _patch_adapter(stage, _SEND, "import time\ntime.sleep(20)\n" + _SEND)
        runtimes = stage.config_home / "cdad" / "runtimes.json"
        doc = json.loads(runtimes.read_text(encoding="utf-8"))
        doc["runtimes"][FIXTURE_RUNTIME]["wait"] = {"timeout_seconds": 2}
        runtimes.write_text(json.dumps(doc), encoding="utf-8")
        cfg = json.loads(stage.exec_config.read_text(encoding="utf-8"))
        cfg["wait"] = {"timeout_seconds": 2}
        stage.exec_config.write_text(json.dumps(cfg), encoding="utf-8")
    envelope = _envelope(stage.delegate(fx), f"PC-10[{failure}]")
    assert envelope.get("termination") == expected, f"PC-10[{failure}]: expected {expected}: {envelope!r}"
    _delivery(envelope, f"PC-10[{failure}]", "none")
    assert envelope.get("diagnosis"), f"PC-10[{failure}]: must be diagnosed"


@pytest.mark.parametrize("ref_kind", ["linked-receipt", "descriptor", "plain-text", "foreign-receipt"])
def test_007_004_legacy_external_requires_valid_receipt(tmp_path: Path, ref_kind: str) -> None:
    """PC-11: a legacy external envelope crossing dispatch is received only with its own receipt."""
    fx = _received_project(tmp_path / "main")
    stage = _Stage(tmp_path / "main")
    refs = {"linked-receipt": lambda: fx.receipt_path(),
            "descriptor": lambda: fx.root / ".cdad/inbox/RESULT.json",
            "plain-text": lambda: _plain(fx.root),
            "foreign-receipt": lambda: _received_project(tmp_path / "other").receipt_path()}
    ref = refs[ref_kind]()
    assert Path(ref).is_file(), f"PC-11[{ref_kind}] fixture: reference exists"
    legacy = {"attempt": FIXTURE_ATTEMPT_ID, "session": FIXTURE_SESSION,
              "termination": "completed", "delivery_ref": str(ref), "diagnosis": None}
    _adapter_emits(stage, legacy)
    assert fx.begin(attempt=2, label="attempt-2").returncode == 0, "PC-11 fixture: begin attempt 2"
    receipt_bytes = fx.receipt_bytes()
    receipts_before = _side_effects(fx)[2]
    envelope = _envelope(stage.dispatch(fx, "--continuity-attempt", "2"), f"PC-11[{ref_kind}]")
    assert envelope.get("attempt") == FIXTURE_ATTEMPT_ID and envelope.get("session") == FIXTURE_SESSION, \
        f"PC-11[{ref_kind}]: identities must be preserved: {envelope!r}"
    if ref_kind == "linked-receipt":
        assert envelope.get("termination") == "completed", f"PC-11: linked receipt is accepted: {envelope!r}"
        _delivery(envelope, "PC-11[linked-receipt]", "received")
    else:
        assert envelope.get("termination") == "transport-error", \
            f"PC-11[{ref_kind}]: legacy ref is not this errand's receipt; must fail closed: {envelope!r}"
        _delivery(envelope, f"PC-11[{ref_kind}]", "none")
        assert envelope.get("diagnosis"), f"PC-11[{ref_kind}]: rejection must be diagnosed"
    assert fx.receipt_bytes() == receipt_bytes, "PC-11: receipt bytes preserved"
    assert _side_effects(fx)[2] == receipts_before, "PC-11: no additional reception"
    assert fx.receipt().get("semantic_status") == "pending", "PC-11: no gate approval"


def _plain(root: Path) -> Path:
    path = root / "notes-007004.txt"
    path.write_text("plain text, not a receipt\n", encoding="utf-8")
    return path


def test_007_004_legacy_native_requires_context_and_descriptor(tmp_path: Path) -> None:
    """PC-12: the scenario-selected native descriptor route receives correctly."""
    fx = _Project(tmp_path)
    assert fx.begin().returncode == 0, "PC-12 fixture: begin continuity"
    assert fx.record_dispatch().returncode == 0, "PC-12 fixture: publish dispatch"
    fx.mark_dispatched()
    received = fx.receive()
    assert received.returncode == 0, "PC-12: scenario-selected descriptor route must be received by existing CLI"
    assert fx.receipt_path().is_file(), "PC-12: receive must publish the durable receipt"
    assert fx.receive(descriptor=fx.receipt_path()).returncode != 0, \
        "PC-12: receipt presented as descriptor must be rejected"


_NONCOMPLETED = ["blocked", "transport-error", "timeout", "cancelled", "unknown"]


@pytest.mark.parametrize(("case", "legacy", "accepted"), [
    ("coherent-nondelivery", {"termination": "blocked", "delivery_ref": None}, True),
    ("completed-without-ref", {"termination": "completed", "delivery_ref": None}, False),
    ("delivery-present-null", {"termination": "completed", "delivery": None,
                               "delivery_ref": "/fixture/artifact"}, False),
    *[(f"{t}-with-{exists}-ref", {"termination": t, "delivery_ref": exists}, False)
      for t in _NONCOMPLETED for exists in ("existing", "missing")],
])
def test_007_004_legacy_compatibility_is_fail_closed(
    tmp_path: Path, case: str, legacy: dict, accepted: bool,
) -> None:
    """PC-13: historical non-delivery is accepted only when coherent (spec §5)."""
    fx, stage = _external(tmp_path)
    legacy = dict(legacy)
    if legacy.get("delivery_ref") == "existing":
        artifact = fx.root / "existing-artifact-007004.md"
        artifact.write_text("exists\n", encoding="utf-8")
        legacy["delivery_ref"] = str(artifact)
    elif legacy.get("delivery_ref") == "missing":
        legacy["delivery_ref"] = str(fx.root / "missing-artifact-007004.md")
    _adapter_emits(stage, {"attempt": "attempt-fixture-007-003", "session": "ses-fixture-007-003",
                           "diagnosis": None, **legacy})
    envelope = _envelope(stage.dispatch(fx), f"PC-13[{case}]")
    if accepted:
        assert envelope.get("termination") == "blocked", f"PC-13[{case}]: coherent legacy kept"
    else:
        assert envelope.get("termination") == "transport-error", (
            f"PC-13[{case}]: incoherent legacy must fail closed, got {envelope!r}")
        assert envelope.get("diagnosis"), f"PC-13[{case}]: rejection must be diagnosed"
    _delivery(envelope, f"PC-13[{case}]", "none")
    assert not fx.receipt_path().exists(), f"PC-13[{case}]: no receipt may appear"


@pytest.mark.parametrize("inner", ["blocked-rc0", "blocked-rc3", "valid-rc3"])
def test_007_004_exit_codes_preserve_envelope_semantics(tmp_path: Path, inner: str) -> None:
    """PC-14: envelope => rc 0; inner rc does not replace a valid envelope; no-envelope error nonzero."""
    fx, stage = _external(tmp_path)
    emitted = {"attempt": "attempt-rc-007004", "session": "ses-rc-007004",
               "termination": "blocked", "delivery": "none", "delivery_ref": None,
               "diagnosis": "rc fixture"}
    if inner == "valid-rc3":
        emitted = dict(emitted, termination="unknown", diagnosis="rc fixture: unknown")
    _adapter_emits(stage, emitted)
    if inner != "blocked-rc0":
        _patch_adapter(stage, _SEND, _SEND + "\n    sys.stdout.flush()\n    sys.exit(3)")
    for route in (stage.dispatch, stage.delegate):
        proc = route(fx)
        envelope = _envelope(proc, f"PC-14[{inner}/{route.__name__}]")
        assert {k: envelope.get(k) for k in emitted} == emitted, \
            f"PC-14[{inner}/{route.__name__}]: inner rc must not replace a valid envelope: {envelope!r}"
    missing = stage.dispatch(fx, "--runtime", "missing-runtime-007004")
    if missing.stdout.strip():
        doc = json.loads(missing.stdout)
        assert missing.returncode == 0 and doc.get("delivery") == "none", \
            "PC-14: an error reported as envelope is rc 0 with no delivery"
    else:
        assert missing.returncode != 0, "PC-14: invocation failure before envelope remains nonzero"


def test_007_004_reentry_routes_preserve_receipt_and_gate_boundaries(tmp_path: Path) -> None:
    """PC-15: scenario chooses staged receive vs received validation; no gate approval."""
    fx, stage = _external(tmp_path)
    assert fx.begin().returncode == 0, "PC-15 fixture: begin continuity"
    assert fx.record_dispatch().returncode == 0, "PC-15 fixture: publish dispatch"
    fx.mark_dispatched()
    assert fx.receive().returncode == 0, "PC-15: existing receive route accepts declared staged descriptor"
    receipt = fx.receipt()
    assert receipt.get("semantic_status") == "pending", "PC-15: receipt does not approve a gate"
    assert fx.validate_receipt().returncode == 0, "PC-15: received route validates without receiving again"


def test_007_004_received_delivery_preserves_continuity_recovery(tmp_path: Path) -> None:
    """PC-16: received delivery with pending close recovers via validate+close with N; no re-reception."""
    fx = _Project(tmp_path)
    stage = _Stage(tmp_path)
    _orphan_receipt(fx, close_attempt=2, label="PC-16")  # durable receipt, close pending (007-003)
    _adapter_emits(stage, {"attempt": FIXTURE_ATTEMPT_ID, "session": FIXTURE_SESSION,
                           "termination": "completed", "delivery": "received",
                           "delivery_ref": str(fx.receipt_path()), "diagnosis": None})
    receipt_bytes = fx.receipt_bytes()
    receipts_before = _side_effects(fx)[2]
    envelope = _envelope(stage.dispatch(fx, "--continuity-attempt", "2"), "PC-16")
    _delivery(envelope, "PC-16", "received")
    pending = fx.continuity_files()
    closed = fx.validate_receipt(close=True, attempt=2)
    assert closed.returncode == 0, f"PC-16: explicit-N recovery: {(closed.stdout + closed.stderr)[-600:]}"
    after_close = fx.continuity_files()
    assert after_close != pending, "PC-16: recovery must add the pending continuity close"
    fx.close(2, "PC-16 close")
    again = fx.validate_receipt(close=True, attempt=2)
    assert again.returncode == 0 and fx.continuity_files() == after_close, \
        "PC-16: repeating recovery must be idempotent"
    assert fx.receipt_bytes() == receipt_bytes and _side_effects(fx)[2] == receipts_before, \
        "PC-16: recovery must not receive again"


def test_007_004_documented_consumers_reference_canonical_delivery_rule() -> None:
    """PC-17: canonical owners define the rule; consumers point to them (spec §6.1)."""
    canonical = REPO_ROOT / "skills/cdad-cycle/references/cli-delegation.md"
    reentry = REPO_ROOT / "skills/cdad-cycle/references/re-entry.md"
    consumers = [REPO_ROOT / "sources/roles/orchestrator.md", REPO_ROOT / "agents/cdad-orchestrator.md"]
    texts = {p: p.read_text(encoding="utf-8") for p in [canonical, reentry, *consumers]}
    schema = texts[canonical]
    for token in ("`delivery`", "none", "staged", "received", "delivery_ref"):
        assert token in schema, f"PC-17: cli-delegation.md must define {token}"
    assert re.search(r"none\s*\|\s*staged\s*\|\s*received", schema), \
        "PC-17: cli-delegation.md must declare the closed vocabulary none | staged | received"
    assert re.search(r"(?i)hist[oó]ric|legacy", schema) and "rc" in schema, \
        "PC-17: cli-delegation.md owns historical compatibility and rc semantics"
    procedure = texts[reentry]
    for token in ("`delivery`", "staged", "received", "validate-receipt", "receive", "FINAL TEXT",
                  "cli-delegation.md"):
        assert token in procedure, f"PC-17: re-entry.md consumption procedure must mention {token}"
    for path in consumers:
        text = texts[path]
        rel = path.relative_to(REPO_ROOT)
        assert "delivery" in text, f"PC-17: {rel} must require consuming delivery"
        assert "cli-delegation.md" in text and "re-entry.md" in text, \
            f"PC-17: {rel} must point to both canonical owners"
        assert not re.search(r"none\s*\|\s*staged\s*\|\s*received", text), \
            f"PC-17: {rel} must not copy the canonical table"


@pytest.mark.parametrize("scenario", ["blocked", "received"])
def test_007_004_delivery_does_not_redefine_orientation(tmp_path: Path, scenario: str) -> None:
    """PC-18: with delivery in the envelope, situation/next.operation stay identical."""
    fx, stage = _external(tmp_path)
    if scenario == "blocked":
        sibling = tmp_path / "sibling-project-007004"
        sibling.mkdir()
        runtime_module = stage.scripts / f"cdad_delegate_{FIXTURE_RUNTIME}.py"
        source = runtime_module.read_text(encoding="utf-8")
        source = source.replace('"session_correlation": False', '"session_correlation": True')
        source = source.replace('sys.stdout.write("null\\n")', 'sys.stdout.write(json.dumps('
                                + repr({"id": "requested-session", "directory": str(sibling)})
                                + ') + "\\n")')
        runtime_module.write_text(source, encoding="utf-8")
        assert fx.begin(attempt=1).returncode == 0, "PC-18 fixture: begin continuity"
    # (a) fix today's projection before the envelope-producing command.
    before = _orientation(fx)
    assert before["situation"] not in {"success", "completed", "approved"}
    if scenario == "blocked":
        payload = tmp_path / "contradictory.md"
        payload.write_text("contradictory correlation fixture\n", encoding="utf-8")
        proc = stage.record(fx, "--continuity-attempt", "1", "--session", "requested-session",
                            "--native-result", str(payload))
    else:
        proc = stage.dispatch(fx)
    envelope = _envelope(proc, f"PC-18[{scenario}]")
    after = _orientation(fx)
    assert after == before, f"PC-18[{scenario}]: the envelope must not change orientation: {before} -> {after}"
    assert envelope.get("situation") is None, "PC-18: the envelope must not carry a situation"
    # (b) the same identical orientation must hold with delivery present.
    _delivery(envelope, f"PC-18[{scenario}]", "none" if scenario == "blocked" else "received")
