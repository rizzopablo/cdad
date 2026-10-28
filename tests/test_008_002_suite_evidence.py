"""PC-6 / AJ7: independent, non-overwriting closure evidence."""

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest


CLI = Path(__file__).resolve().parents[1] / "scripts" / "cdad-suite.py"


@pytest.fixture
def workspace(tmp_path):
    assert CLI.is_file(), "PC-6: canonical close/measure CLI is absent"
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    (tmp_path / "test_sample.py").write_text(
        "import time\nimport pytest\n"
        "def test_pass(): pass\n"
        "def test_fail(): assert False, 'deliberate failure'\n"
        "@pytest.mark.skip(reason='intentional opt-in skip')\n"
        "def test_skip(): pass\n"
        "def test_wait(): time.sleep(30)\n"
    )
    subprocess.run(["git", "-C", str(tmp_path), "add", "test_sample.py"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "fixture"], check=True)
    (tmp_path / "evidence").mkdir()
    return tmp_path


def start_close(workspace, selection, label):
    nodeids = workspace / (label + ".txt")
    nodeids.write_text("\n".join("test_sample.py::" + name for name in selection) + "\n")
    return subprocess.Popen(
        [sys.executable, str(CLI), "close", "--evidence-root", str(workspace / "evidence"),
         "--nodeids", str(nodeids)],
        cwd=workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
    )


def attempts(workspace):
    return sorted(p for p in (workspace / "evidence").iterdir() if p.is_dir())


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def finish(process):
    out, err = process.communicate(timeout=60)
    return process.returncode, out, err


def test_sequential_attempts_preserve_first_bytes(workspace):
    """PC-6: sin este test, el usuario puede perder evidencia de una corrida anterior."""
    assert finish(start_close(workspace, ["test_pass"], "pass"))[0] == 0
    first, = attempts(workspace)
    before = hashes(first)
    assert finish(start_close(workspace, ["test_fail"], "fail"))[0] != 0
    after = attempts(workspace)
    assert len(after) == 2 and first in after
    assert hashes(first) == before


def test_simultaneous_attempts_are_independent(workspace):
    """PC-6: sin este test, el usuario puede perder evidencia por una colisión concurrente."""
    a = start_close(workspace, ["test_pass"], "parallel-a")
    b = start_close(workspace, ["test_pass"], "parallel-b")
    assert finish(a)[0] == 0
    assert finish(b)[0] == 0
    found = attempts(workspace)
    assert len(found) == 2
    for attempt in found:
        assert json.loads((attempt / "attempt.json").read_text())["state"] == "finished"
        assert (attempt / "stdout.log").is_file()
        assert (attempt / "stderr.log").is_file()


def test_attempt_records_selection_result_and_skip_reason(workspace):
    """PC-6: sin este test, el usuario no puede interpretar ni reproducir el cierre."""
    rc, _, _ = finish(start_close(workspace, ["test_pass", "test_skip"], "selected"))
    assert rc == 0
    attempt, = attempts(workspace)
    data = json.loads((attempt / "attempt.json").read_text())
    assert {"schema_version", "state", "command", "selection", "commit", "dirty", "started_at",
            "finished_at", "rc", "pytest_summary", "canary", "artifacts"} <= data.keys()
    assert data["state"] == "finished" and data["rc"] == rc
    assert data["command"] and data["commit"] and isinstance(data["dirty"], int)
    assert data["started_at"] and data["finished_at"]
    assert {"kind", "value", "nodeids"} <= data["selection"].keys()
    assert data["selection"]["kind"] == "nodeids"
    assert set(data["selection"]["nodeids"]) == {"test_sample.py::test_pass", "test_sample.py::test_skip"}
    summary = data["pytest_summary"]
    assert {"passed", "failed", "skipped", "skips"} <= summary.keys()
    assert (summary["passed"], summary["failed"], summary["skipped"]) == (1, 0, 1)
    assert any("test_skip" in skip["nodeid"] and "intentional opt-in skip" in skip["reason"]
               for skip in summary["skips"])
    assert {"scope", "before", "after", "delta_lines"} <= data["canary"].keys()
    assert {"stdout", "stderr"} <= data["artifacts"].keys()
    for name in ("stdout.log", "stderr.log", "canary-before.txt", "canary-after.txt"):
        assert (attempt / name).is_file()


def test_interrupted_attempt_is_never_success(workspace):
    """PC-6: sin este test, el usuario puede confundir una interrupción con éxito."""
    process = start_close(workspace, ["test_wait"], "wait")
    try:
        deadline = time.monotonic() + 20
        evidence = None
        while time.monotonic() < deadline:
            found = attempts(workspace)
            if found and (found[0] / "attempt.json").is_file():
                evidence = found[0] / "attempt.json"
                break
            assert process.poll() is None, "close exited before recording a running attempt"
            time.sleep(0.05)
        assert evidence is not None, "close did not record a running attempt"
        os.killpg(process.pid, signal.SIGKILL)
        finish(process)
        data = json.loads(evidence.read_text())
        assert data["state"] in {"running", "interrupted"}
        assert data["rc"] is None or data["rc"] != 0
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()


def test_measure_does_not_modify_tree(workspace):
    """PC-6 §5: sin este test, el usuario puede alterar archivos al medir la suite."""
    before = hashes(workspace)
    result = subprocess.run([sys.executable, str(CLI), "measure"], cwd=workspace,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert isinstance(json.loads(result.stdout), dict)
    assert hashes(workspace) == before
