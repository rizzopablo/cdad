"""017-001 T6 RED: oraculo del lote paralelo con workers configurables.

Derivado del contrato aprobado ``docs/specs/017-001-suite-performance/spec.md``
(PC-10, promesa E) y de ``performance/parallelism.md`` (contrato del lote y
evidencia PC-10). No lee implementacion: ejercita la CLI fija
``python3 scripts/cdad-suite.py parallel --workers N --evidence-root <dir>
[--nodeids <archivo>]`` como caja negra sobre una seleccion pequena y rapida
de tests reales (dos archivos de un test cada uno), en directorios de
evidencia descartables (``tmp_path``).

Busqueda pre-RED: ningun verificador existente cubre el lote paralelo (las
menciones a "parallel" en la suite son de otros contextos); sin estos tests,
el usuario podria adoptar un runner paralelo que mezcle trabajo con pared,
repita nodeids, comparta HOME/TMP o deje hijos huerfanos sin que nada lo
detecte.

Cada test falla hoy por AssertionError de promesa ausente (subcomando
``parallel`` inexistente: el parser sale con codigo 2), nunca por ImportError
ni error de coleccion. Los timeouts de subprocess son guardas de liveness,
no oraculos de duracion (convencion 11: sin par correcto/defecto declarado
no hay cota; aqui solo se evita un hang eterno).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE = [sys.executable, "scripts/cdad-suite.py"]

# Seleccion pequena y rapida de tests reales: dos archivos de un test cada
# uno, para que la particion por archivo sea observable con 2 workers.
NODEIDS = [
    "tests/test_017_001_suite_tranche1.py"
    "::test_real_product_lookup_emits_branch_and_stays_neutral",
    "tests/test_017_001_suite_tranche2.py"
    "::test_real_tranche2_lookups_emit_branch_and_stay_neutral",
]

TIMEOUT_S = 300  # liveness, no oraculo (convencion 11).


def _write_nodeids(path):
    path.write_text("".join(n + "\n" for n in NODEIDS), encoding="utf-8")
    return path


def _run(*args, timeout=TIMEOUT_S):
    return subprocess.run(
        SUITE + list(args),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _parallel_json(evidence_root, what):
    candidate = evidence_root / "parallel.json"
    assert candidate.is_file(), (
        "017-001 T6 RED (%s, PC-10): falta parallel.json en %s; "
        "el lote paralelo prometido no existe" % (what, evidence_root))
    try:
        data = json.loads(candidate.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "017-001 T6 RED (%s, PC-10): parallel.json no es JSON: %s"
            % (what, exc))
    assert isinstance(data, dict), (
        "017-001 T6 RED (%s, PC-10): parallel.json debe ser un objeto, no %s"
        % (what, type(data).__name__))
    return data


def _run_parallel_evidence(tmp_path, name, extra=()):
    evidence_root = tmp_path / name
    evidence_root.mkdir(parents=True, exist_ok=True)
    nodeids_file = _write_nodeids(tmp_path / (name + ".nodeids"))
    proc = _run("parallel", "--evidence-root", str(evidence_root),
                "--nodeids", str(nodeids_file), *extra)
    assert proc.returncode == 0, (
        "017-001 T6 RED (%s, PC-10): el lote paralelo debe terminar con "
        "rc=0 sobre la seleccion de referencia; rc=%d stderr=%r"
        % (name, proc.returncode, proc.stderr[-2000:]))
    return evidence_root, _parallel_json(evidence_root, name)


def _find_first_key(node, *names):
    wanted = {n.lower() for n in names}
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key).lower() in wanted:
                return value
        for value in node.values():
            found = _find_first_key(value, *names)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = _find_first_key(value, *names)
            if found is not None:
                return found
    return None


def _worker_count(data, what):
    workers = data.get("workers")
    count = len(workers) if isinstance(workers, list) else workers
    assert count == 2, (
        "017-001 T6 RED (%s, PC-10): parallel.json debe informar N=2 "
        "workers; informa %r" % (what, workers))
    return workers


def _per_worker_entries(data, what):
    workers = data.get("workers")
    if isinstance(workers, list) and workers and all(
            isinstance(w, dict) for w in workers):
        return list(workers)
    for key in ("per_worker", "worker_details", "workers_detail", "by_worker"):
        value = data.get(key)
        if isinstance(value, list) and value:
            return list(value)
        if isinstance(value, dict) and value:
            return list(value.values())
    raise AssertionError(
        "017-001 T6 RED (%s, PC-10): parallel.json no trae detalle por "
        "worker (lista de workers o per_worker/worker_details); claves: %r"
        % (what, sorted(map(str, data.keys()))))


def _first_number(entry, what, *names):
    for name in names:
        value = entry.get(name) if isinstance(entry, dict) else None
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
    raise AssertionError(
        "017-001 T6 RED (%s, PC-10): sin cantidad %s en %r"
        % (what, "/".join(names), entry))


def _nodeid_lists(node):
    found = []
    if (isinstance(node, list) and node
            and all(isinstance(x, str) and "::" in x for x in node)):
        found.append(list(node))
    elif isinstance(node, dict):
        for value in node.values():
            found.extend(_nodeid_lists(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_nodeid_lists(value))
    return found


def _worker_nodeid_groups(data, evidence_root, what):
    groups = []
    for entry in _per_worker_entries(data, what):
        merged = set()
        for lst in _nodeid_lists(entry):
            merged.update(lst)
        groups.append(merged)
    if any(groups):
        return groups
    # Repliegue: worker-<i>/ con nodeids registrados en archivos.
    fallback = []
    for worker_dir in sorted(evidence_root.glob("worker-*")):
        collected = set()
        for path in sorted(worker_dir.rglob("*")):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "::" not in text:
                continue
            try:
                payload = json.loads(text)
            except ValueError:
                payload = None
            for lst in _nodeid_lists(payload) if payload is not None else []:
                collected.update(lst)
            for line in text.splitlines():
                line = line.strip()
                if "::" in line and " " not in line:
                    collected.add(line)
        fallback.append(collected)
    assert fallback and any(fallback), (
        "017-001 T6 RED (%s, PC-10): ni parallel.json ni worker-*/ "
        "registran los nodeids por worker" % what)
    return fallback


def _collect_roots(data):
    homes, xdgs, tmps = set(), set(), set()

    def visit(node):
        if isinstance(node, dict):
            for key, value in node.items():
                lowered = str(key).lower()
                if isinstance(value, str) and value.startswith("/"):
                    if "home" in lowered and "xdg" not in lowered:
                        homes.add(value)
                    elif "xdg" in lowered:
                        xdgs.add(value)
                    elif "tmp" in lowered:
                        tmps.add(value)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(data)
    return homes, xdgs, tmps


def _serial_counts(tmp_path):
    """Pared serial de referencia (close) sobre los mismos nodeids."""
    evidence_root = tmp_path / "ev-serial"
    evidence_root.mkdir(parents=True, exist_ok=True)
    nodeids_file = _write_nodeids(tmp_path / "ev-serial.nodeids")
    proc = _run("close", "--evidence-root", str(evidence_root),
                "--nodeids", str(nodeids_file))
    assert proc.returncode == 0, (
        "017-001 T6 RED (equivalencia, PC-10): el close serial de "
        "referencia debe pasar; rc=%d stderr=%r"
        % (proc.returncode, proc.stderr[-2000:]))
    found = list(evidence_root.rglob("attempt.json"))
    assert found, (
        "017-001 T6 RED (equivalencia, PC-10): close no conservo attempt.json")
    summary = json.loads(found[0].read_text(encoding="utf-8")).get(
        "pytest_summary", {})
    return (summary.get("passed"), summary.get("failed"),
            summary.get("skipped"))


def test_parallel_workers2_aggregate_reports_wall_work_overlap_and_matches_serial(
        tmp_path):
    """PC-10: sin este test, el usuario podria leer un agregado que suma
    tiempos concurrentes como si fueran pared, sin solapamiento declarado y
    sin equivalencia con el serial de los mismos nodeids."""
    evidence_root, data = _run_parallel_evidence(tmp_path, "ev-batch")
    _worker_count(data, "agregado")
    entries = _per_worker_entries(data, "agregado")
    assert len(entries) == 2, (
        "017-001 T6 RED (agregado, PC-10): dos workers deben traer dos "
        "entradas de detalle, no %d" % len(entries))
    worker_walls = [_first_number(
        e, "agregado", "wall_s", "wall", "elapsed_s", "duration_s",
        "pared_s", "pared") for e in entries]
    total_wall = _find_first_key(
        data, "wall_total_s", "total_wall_s", "total_wall", "pared_total_s",
        "pared_total")
    assert isinstance(total_wall, (int, float)) and total_wall > 0, (
        "017-001 T6 RED (agregado, PC-10): falta la pared total del comando "
        "en parallel.json; claves: %r" % sorted(map(str, data.keys())))
    works = [_first_number(
        e, "agregado", "work_s", "work_measured_s", "measured_work_s",
        "phases_sum_s", "trabajo_medido_s", "trabajo_medido") for e in entries]
    overlap = _find_first_key(
        data, "overlap_s", "overlap", "solapamiento_s", "solapamiento")
    assert isinstance(overlap, (int, float)), (
        "017-001 T6 RED (agregado, PC-10): falta el solapamiento declarado "
        "(pared de workers menos pared total) en parallel.json")
    expected = sum(worker_walls) - float(total_wall)
    tolerance = max(2.0, 0.2 * float(total_wall))
    assert abs(float(overlap) - expected) <= tolerance, (
        "017-001 T6 RED (agregado, PC-10): solapamiento %r no concilia con "
        "suma de paredes %r menos pared total %r" % (
            overlap, worker_walls, total_wall))
    md_path = evidence_root / "parallel.md"
    assert md_path.is_file(), (
        "017-001 T6 RED (agregado, PC-10): falta parallel.md junto a "
        "parallel.json")
    lowered = md_path.read_text(encoding="utf-8").lower()
    assert "worker" in lowered, (
        "017-001 T6 RED (agregado, PC-10): parallel.md no menciona workers")
    assert ("wall" in lowered or "pared" in lowered), (
        "017-001 T6 RED (agregado, PC-10): parallel.md no informa pared")
    assert ("work" in lowered or "trabajo" in lowered), (
        "017-001 T6 RED (agregado, PC-10): parallel.md no rotula el trabajo "
        "medido como tal")
    assert ("overlap" in lowered or "solap" in lowered), (
        "017-001 T6 RED (agregado, PC-10): parallel.md no declara "
        "solapamiento")
    consolidated = _find_first_key(
        data, "consolidated", "summary", "result", "totals")
    assert isinstance(consolidated, dict), (
        "017-001 T6 RED (agregado, PC-10): falta el resultado consolidado "
        "en parallel.json")
    triplet = (consolidated.get("passed"), consolidated.get("failed"),
               consolidated.get("skipped"))
    assert triplet == _serial_counts(tmp_path), (
        "017-001 T6 RED (agregado, PC-10): el consolidado %r difiere del "
        "serial %r sobre los mismos nodeids" % (
            triplet, _serial_counts(tmp_path)))


def test_parallel_workers_have_distinct_recorded_home_xdg_tmp_roots(tmp_path):
    """PC-10: sin este test, dos workers podrian compartir HOME/XDG/TMP sin
    que quede registrado, y el usuario creeria aislado lo que se pisa."""
    evidence_root, data = _run_parallel_evidence(tmp_path, "ev-roots")
    homes, xdgs, tmps = _collect_roots(data)
    for worker_dir in sorted(evidence_root.glob("worker-*")):
        for profile in sorted(worker_dir.glob("*.json")):
            try:
                extra = json.loads(profile.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                continue
            more = _collect_roots(extra)
            homes |= more[0]
            xdgs |= more[1]
            tmps |= more[2]
    assert len(homes) >= 2, (
        "017-001 T6 RED (raices, PC-10): los HOME de los workers deben ser "
        "distintos y quedar registrados; hallados: %r" % sorted(homes))
    assert len(xdgs) >= 2, (
        "017-001 T6 RED (raices, PC-10): las raices XDG de los workers deben "
        "ser distintas y quedar registradas; halladas: %r" % sorted(xdgs))
    assert len(tmps) >= 2, (
        "017-001 T6 RED (raices, PC-10): las raices TMP de los workers deben "
        "ser distintas y quedar registradas; halladas: %r" % sorted(tmps))


def test_parallel_partition_is_by_file_without_repetition(tmp_path):
    """PC-10: sin este test, el lote podria partir por test suelto o repetir
    nodeids entre workers, rompiendo fixtures por archivo sin aviso."""
    evidence_root, data = _run_parallel_evidence(tmp_path, "ev-partition")
    groups = _worker_nodeid_groups(data, evidence_root, "particion")
    assert len(groups) == 2, (
        "017-001 T6 RED (particion, PC-10): dos workers deben repartirse "
        "los nodeids en dos grupos, no %d" % len(groups))
    union = set().union(*groups)
    assert union == set(NODEIDS), (
        "017-001 T6 RED (particion, PC-10): el reparto debe cubrir los "
        "nodeids de entrada; faltan %r sobran %r" % (
            set(NODEIDS) - union, union - set(NODEIDS)))
    assert sum(len(g) for g in groups) == len(union), (
        "017-001 T6 RED (particion, PC-10): ningun nodeid puede repetirse "
        "entre workers; grupos: %r" % [sorted(g) for g in groups])
    by_file = {}
    for nodeid in NODEIDS:
        by_file.setdefault(nodeid.split("::")[0], []).append(nodeid)
    for filename, members in by_file.items():
        owners = [i for i, group in enumerate(groups)
                  if any(m in group for m in members)]
        assert len(owners) == 1 and all(
            m in groups[owners[0]] for m in members), (
            "017-001 T6 RED (particion, PC-10): todos los nodeids de %s "
            "deben caer en un solo worker; grupos: %r" % (
                filename, [sorted(g) for g in groups]))


def test_parallel_keeps_canary_clean_and_terminates_children(tmp_path):
    """PC-10: sin este test, el lote podria ensuciar el checkout o dejar
    hijos huerfanos, y el usuario lo adoptaria como seguro sin evidencia."""
    evidence_root, data = _run_parallel_evidence(tmp_path, "ev-safety")
    canary = _find_first_key(data, "canary")
    if isinstance(canary, dict):
        before, after = canary.get("before"), canary.get("after")
        if before is not None or after is not None:
            delta = canary.get("delta_lines", canary.get("delta"))
            assert before == after and delta in (None, 0, [], ""), (
                "017-001 T6 RED (canario, PC-10): el canario cambio durante "
                "el lote: %r" % (canary,))
            canary_ok = True
        else:
            canary_ok = canary.get("unchanged") is True or \
                canary.get("clean") is True
    else:
        canary_ok = canary is None
    if not canary_ok or canary is None:
        files_ok, where = None, "ausente"
        for base in [evidence_root, *sorted(evidence_root.glob("worker-*"))]:
            before_p, after_p = (base / "canary-before.txt",
                                 base / "canary-after.txt")
            if before_p.is_file() and after_p.is_file():
                files_ok = (before_p.read_bytes() == after_p.read_bytes())
                where = base.name
                break
        assert files_ok is True, (
            "017-001 T6 RED (canario, PC-10): sin canario limpio verificable "
            "(registro %r, archivos en %s)" % (canary, where))
    orphans = _find_first_key(
        data, "orphans", "orphan_count", "leftover_children",
        "children_orphaned")
    if orphans is not None:
        try:
            children_ok = int(orphans) == 0
        except (TypeError, ValueError):
            children_ok = orphans in ([], {}, "none", "0", "")
    else:
        flag = _find_first_key(
            data, "children_terminated", "no_orphans", "all_children_reaped")
        children_ok = flag is True if flag is not None else None
    try:
        ps_proc = subprocess.run(["ps", "-ef"], capture_output=True,
                                 text=True, timeout=30)
        leftovers = [line for line in ps_proc.stdout.splitlines()
                     if "pytest" in line and str(evidence_root) in line]
        ps_ok = ps_proc.returncode == 0 and not leftovers
    except Exception:
        ps_ok, leftovers = None, []
    assert children_ok is True or ps_ok is True, (
        "017-001 T6 RED (hijos, PC-10): sin evidencia de hijos terminados "
        "(registro %r, ps %r)" % (orphans, ps_ok))
    assert not leftovers, (
        "017-001 T6 RED (hijos, PC-10): quedaron procesos pytest con la "
        "evidencia abierta: %r" % leftovers[:3])


def test_parallel_rejects_invalid_worker_counts(tmp_path):
    """PC-10: sin este test, el usuario podria pedir 0, negativo o mas
    workers que nucleos menos uno y obtener un reparto absurdo o caido."""
    nproc = os.cpu_count() or 8
    evidence_root = tmp_path / "ev-workers"
    evidence_root.mkdir(parents=True, exist_ok=True)
    nodeids_file = _write_nodeids(tmp_path / "ev-workers.nodeids")
    for bad in (0, -1, nproc):
        proc = _run("parallel", "--workers", str(bad), "--evidence-root",
                    str(evidence_root), "--nodeids", str(nodeids_file))
        assert proc.returncode == 2 and "worker" in proc.stderr.lower(), (
            "017-001 T6 RED (workers, PC-10): --workers %d debe rechazarse "
            "con salida 2 y motivo por stderr; rc=%d stderr=%r" % (
                bad, proc.returncode, proc.stderr[-1000:]))


def test_parallel_default_is_two_workers_without_using_all_cores(tmp_path):
    """PC-10 (decision PC-9): sin este test, el default podria usar todos los
    nucleos y dejar al operador sin margen, contra lo decidido por el dueno."""
    evidence_root = tmp_path / "ev-default"
    evidence_root.mkdir(parents=True, exist_ok=True)
    nodeids_file = _write_nodeids(tmp_path / "ev-default.nodeids")
    proc = _run("parallel", "--evidence-root", str(evidence_root),
                "--nodeids", str(nodeids_file))
    assert proc.returncode == 0, (
        "017-001 T6 RED (default, PC-10): el lote sin --workers debe correr "
        "con el default; rc=%d stderr=%r" % (
            proc.returncode, proc.stderr[-2000:]))
    data = _parallel_json(evidence_root, "default")
    workers = data.get("workers")
    count = len(workers) if isinstance(workers, list) else workers
    assert count == 2, (
        "017-001 T6 RED (default, PC-10): el default debe ser 2 workers, "
        "no %r" % (workers,))
    nproc = os.cpu_count() or 2
    assert nproc <= 2 or count < nproc, (
        "017-001 T6 RED (default, PC-10): el default (%r) no debe usar todos "
        "los nucleos (%r)" % (count, nproc))


# ---------------------------------------------------------------------------
# 017-001 T6 review-fix RED (packet ...-red-024): cinco protecciones nuevas por
# los cinco bloqueantes de review-T6.md. No modifican los seis tests
# existentes de arriba: solo agregan M1..M5. Una por promesa observable,
# todas -> PC-10 (promesa E: paralelismo justificado y seguro). Cada una falla
# hoy por promesa ausente (AssertionError o pytest.fail con motivo), nunca por
# ImportError ni error de coleccion. Los timeouts son guardas de liveness, no
# oraculos de duracion (convencion 11). M1 y M3b usan start_new_session +
# killpg para no dejar procesos vivos.
# ---------------------------------------------------------------------------

SINGLE_NODEID = [NODEIDS[0]]  # un solo archivo (tranche1): caso worker vacio.

M1_TIMEOUT_S = 90  # <= 120 s exigido por el packet; liveness, no oraculo.


def _write_single_nodeids(path):
    path.write_text(SINGLE_NODEID[0] + "\n", encoding="utf-8")
    return path


def _serial_triplet_for(nodeids, tmp_path, name):
    evidence_root = tmp_path / name
    evidence_root.mkdir(parents=True, exist_ok=True)
    nodeids_file = tmp_path / (name + ".nodeids")
    nodeids_file.write_text("".join(n + "\n" for n in nodeids),
                            encoding="utf-8")
    proc = _run("close", "--evidence-root", str(evidence_root),
                "--nodeids", str(nodeids_file))
    assert proc.returncode == 0, (
        "017-001 T6 RED (M1/M5, PC-10): el close serial de referencia debe "
        "pasar; rc=%d stderr=%r"
        % (proc.returncode, proc.stderr[-2000:]))
    found = list(evidence_root.rglob("attempt.json"))
    assert found, (
        "017-001 T6 RED (M1/M5, PC-10): close no conservo attempt.json")
    summary = json.loads(found[0].read_text(encoding="utf-8")).get(
        "pytest_summary", {})
    return (summary.get("passed"), summary.get("failed"),
            summary.get("skipped"))


def _parse_iso_with_zone(value, what):
    import datetime
    assert isinstance(value, str) and value.strip(), (
        "017-001 T6 RED (%s, PC-10): instante ausente o no textual: %r"
        % (what, value))
    try:
        parsed = datetime.datetime.fromisoformat(
            value.strip().replace("Z", "+00:00"))
    except ValueError:
        raise AssertionError(
            "017-001 T6 RED (%s, PC-10): instante no ISO 8601: %r"
            % (what, value))
    assert parsed.tzinfo is not None, (
        "017-001 T6 RED (%s, PC-10): el instante debe traer zona: %r"
        % (what, value))
    return parsed


def _live_pids_with_marker(marker):
    """PIDs vivos cuya linea de comandos menciona marker (lectura de /proc)."""
    try:
        entries = os.listdir("/proc")
    except OSError:
        return None
    me = os.getpid()
    found = []
    for entry in entries:
        if not entry.isdigit() or int(entry) == me:
            continue
        try:
            with open("/proc/%s/cmdline" % entry, "rb") as handle:
                raw = handle.read()
        except OSError:
            continue
        if raw and marker in raw.decode("utf-8", errors="replace"):
            found.append(int(entry))
    return found


def _measured_preparation(profile):
    """preparation_measured_s de un profile.json, o suma de sus operaciones de
    preparacion si el campo aun no existe; None si no hay de donde sacarlo."""
    if not isinstance(profile, dict):
        return None
    value = profile.get("preparation_measured_s")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    operations = profile.get("operations")
    if isinstance(operations, list) and operations:
        total, seen = 0.0, False
        for operation in operations:
            if not isinstance(operation, dict):
                continue
            if "prepar" not in json.dumps(
                    operation, ensure_ascii=False).lower():
                continue
            duration = operation.get("duration_s", operation.get("duration"))
            if isinstance(duration, (int, float)) and not isinstance(
                    duration, bool):
                total += float(duration)
                seen = True
        if seen:
            return total
    return None


def _find_checkout_canaries(node):
    """Dicts canarios que hablan del checkout (checkout/build/.cdad)."""
    found = []

    def visit(item):
        if isinstance(item, dict):
            blob = json.dumps(item, ensure_ascii=False).lower()
            if "checkout" in blob or "build" in blob or ".cdad" in blob:
                found.append(item)
            for value in item.values():
                visit(value)
        elif isinstance(item, list):
            for value in item:
                visit(value)

    visit(node)
    return found


def test_parallel_single_file_launches_no_empty_worker(tmp_path):
    """PC-10 (bloqueante 1): sin este test, una seleccion de UN archivo con
    --workers 2 lanzaria un worker vacio con pytest sin seleccion (la suite
    completa) sin que nada lo detecte."""
    import signal
    import pytest as pytest_mod
    evidence_root = tmp_path / "ev-single"
    evidence_root.mkdir(parents=True, exist_ok=True)
    nodeids_file = _write_single_nodeids(tmp_path / "ev-single.nodeids")
    expected = _serial_triplet_for(
        SINGLE_NODEID, tmp_path, "ev-single-serial")
    proc = subprocess.Popen(
        SUITE + ["parallel", "--workers", "2", "--evidence-root",
                 str(evidence_root), "--nodeids", str(nodeids_file)],
        cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True)
    try:
        _, stderr = proc.communicate(timeout=M1_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        proc.wait(timeout=30)
        pytest_mod.fail(
            "017-001 T6 RED (M1, PC-10): el lote de un archivo con --workers "
            "2 no termino en %d s: el worker sin archivos corre pytest sin "
            "seleccion (bloqueante 1 de review-T6)" % M1_TIMEOUT_S)
    candidate = evidence_root / "parallel.json"
    partial = None
    if candidate.is_file():
        try:
            partial = json.loads(candidate.read_text(encoding="utf-8"))
        except ValueError:
            partial = None
    if isinstance(partial, dict):
        raw_workers = partial.get("workers")
        if isinstance(raw_workers, list):
            empties = [position for position, item in enumerate(raw_workers)
                       if isinstance(item, dict)
                       and not _nodeid_lists(item)]
            assert not empties, (
                "017-001 T6 RED (M1, PC-10): el lote lanzo %d worker(s) sin "
                "archivos (pytest sin seleccion); rc=%d stderr=%r"
                % (len(empties), proc.returncode, stderr[-2000:]))
    assert proc.returncode == 0, (
        "017-001 T6 RED (M1, PC-10): el lote de un archivo debe terminar con "
        "rc=0; rc=%d stderr=%r" % (proc.returncode, stderr[-2000:]))
    data = _parallel_json(evidence_root, "un-archivo")
    launched = data.get("workers_launched")
    skipped = data.get("skipped_empty_workers")
    assert launched == 1 or skipped == 1, (
        "017-001 T6 RED (M1, PC-10): con un archivo y --workers 2 el lote no "
        "debe lanzar ningun worker sin archivos "
        "(workers_launched==1 o skipped_empty_workers==1); informa %r"
        % ({k: data.get(k) for k in ("workers_launched",
                                     "skipped_empty_workers", "workers")}))
    consolidated = _find_first_key(
        data, "consolidated", "summary", "result", "totals")
    assert isinstance(consolidated, dict), (
        "017-001 T6 RED (M1, PC-10): falta el resultado consolidado")
    triplet = (consolidated.get("passed"), consolidated.get("failed"),
               consolidated.get("skipped"))
    assert triplet == expected, (
        "017-001 T6 RED (M1, PC-10): el consolidado %r debe ser exactamente "
        "el serial %r del archivo pedido" % (triplet, expected))


def test_parallel_workers_record_real_walls_and_overlap(tmp_path):
    """PC-10 (bloqueante 2): sin este test, las paredes por worker medidas al
    volver de cada wait() secuencial inflarian el solapamiento sin que nada lo
    detecte. Tranche2 es claramente mas lento que tranche1 (pared serial
    medida: ~2.1 s vs ~0.7 s), asi la pared inflada es observable."""
    evidence_root, data = _run_parallel_evidence(tmp_path, "ev-walls")
    entries = _per_worker_entries(data, "paredes")
    assert len(entries) == 2, (
        "017-001 T6 RED (M2, PC-10): dos workers deben traer dos entradas "
        "de detalle, no %d" % len(entries))
    walls = []
    for position, entry in enumerate(entries):
        what = "paredes/w%d" % position
        started = _parse_iso_with_zone(entry.get("started_at"), what)
        finished = _parse_iso_with_zone(entry.get("finished_at"), what)
        wall = _first_number(entry, what, "wall_s")
        assert abs(float(wall) - (finished - started).total_seconds()
                   ) <= 1e-3, (
            "017-001 T6 RED (M2, PC-10): wall_s %r del worker %d no coincide "
            "con finished_at - started_at (%r -> %r)"
            % (wall, position, entry.get("started_at"),
               entry.get("finished_at")))
        walls.append(float(wall))
    total = data.get("total_wall_s")
    if total is None:
        total = _find_first_key(data, "wall_total_s", "total_wall",
                                "pared_total_s", "pared_total")
    assert isinstance(total, (int, float)) and total > 0, (
        "017-001 T6 RED (M2, PC-10): falta total_wall_s del comando en "
        "parallel.json; claves: %r" % sorted(map(str, data.keys())))
    total = float(total)
    assert total >= max(walls) - 1e-3, (
        "017-001 T6 RED (M2, PC-10): la pared total %r no puede ser menor "
        "que la mayor pared por worker %r" % (total, walls))
    assert total - max(walls) <= 1.0, (
        "017-001 T6 RED (M2, PC-10): los workers deben arrancar juntos "
        "(total %r - max %r <= 1.0 s)" % (total, max(walls)))
    overlap = data.get("overlap_s")
    if overlap is None:
        overlap = _find_first_key(data, "overlap", "solapamiento_s",
                                  "solapamiento")
    assert isinstance(overlap, (int, float)), (
        "017-001 T6 RED (M2, PC-10): falta overlap_s == sum(wall_s) - "
        "total_wall_s en parallel.json")
    assert abs(float(overlap) - (sum(walls) - total)) <= 1e-2, (
        "017-001 T6 RED (M2, PC-10): overlap_s %r no concilia con "
        "sum(wall_s) - total %r" % (overlap, sum(walls) - total))


def test_parallel_checks_descendants_and_cleans_up_partial_launch(tmp_path):
    """PC-10 (bloqueante 3): sin este test, el agregado declararia
    'orphans: 0' sin comprobar descendientes y un fallo parcial de lanzamiento
    dejaria workers vivos sin que nada lo detecte."""
    import signal
    import pytest as pytest_mod
    evidence_root, data = _run_parallel_evidence(tmp_path, "ev-orphans")
    checked = _find_first_key(data, "orphans_checked")
    assert checked is True, (
        "017-001 T6 RED (M3a, PC-10): parallel.json debe declarar la "
        "comprobacion real de descendientes (orphans_checked == true); un "
        "'orphans: 0' fijo no es evidencia; claves: %r"
        % sorted(map(str, data.keys())))
    live = _live_pids_with_marker(str(evidence_root))
    assert live is not None and not live, (
        "017-001 T6 RED (M3a, PC-10): quedaron procesos vivos que mencionan "
        "la raiz de evidencia %s: %r" % (evidence_root, live))
    partial_root = tmp_path / "ev-partial"
    partial_root.mkdir(parents=True, exist_ok=True)
    (partial_root / "worker-1").write_text(
        "bloqueo M3b: archivo donde el segundo worker crearia su directorio",
        encoding="utf-8")
    nodeids_file = _write_nodeids(tmp_path / "ev-partial.nodeids")
    proc = subprocess.Popen(
        SUITE + ["parallel", "--workers", "2", "--evidence-root",
                 str(partial_root), "--nodeids", str(nodeids_file)],
        cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True)
    try:
        _, stderr = proc.communicate(timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        proc.wait(timeout=30)
        pytest_mod.fail(
            "017-001 T6 RED (M3b, PC-10): el lote con fallo de lanzamiento "
            "no termino en %d s y dejo su grupo colgado" % TIMEOUT_S)
    assert proc.returncode != 0, (
        "017-001 T6 RED (M3b, PC-10): forzar el fallo del segundo worker "
        "debe salir distinto de 0; rc=%d" % proc.returncode)
    lowered = (stderr or "").lower()
    assert "worker" in lowered and ("1" in (stderr or "")
                                    or "evid" in lowered
                                    or str(partial_root) in (stderr or "")), (
        "017-001 T6 RED (M3b, PC-10): debe nombrar la causa por stderr; "
        "stderr=%r" % (stderr or "")[-2000:])
    live = _live_pids_with_marker(str(partial_root))
    if live:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        live = _live_pids_with_marker(str(partial_root))
    assert live is not None and not live, (
        "017-001 T6 RED (M3b, PC-10): el fallo parcial dejo procesos vivos "
        "con la raiz en su linea: %r" % (live,))


def test_parallel_declares_checkout_canary_covering_build_and_cdad(tmp_path):
    """PC-10 (bloqueante 4): sin este test, el canario cubriria solo
    configuracion y un test que escriba en build/ o .cdad/ pasaria como
    seguro sin que nada lo detecte."""
    evidence_root, data = _run_parallel_evidence(tmp_path, "ev-canary")
    count_keys = {"files", "file_count", "n_files", "count", "num_files"}
    size_keys = {"bytes", "total_bytes", "size", "total_size"}
    time_keys = {"max_mtime", "mtime_max", "latest_mtime", "newest_mtime"}
    hash_keys = {"fingerprint", "hash", "digest"}
    flag_keys = {"unchanged", "clean"}
    matching = None
    for candidate in _find_checkout_canaries(data):
        lowered = {str(key).lower(): key for key in candidate.keys()}
        counts = [candidate[lowered[key]] for key in count_keys
                  if key in lowered]
        sizes = [candidate[lowered[key]] for key in size_keys
                 if key in lowered]
        times = [candidate[lowered[key]] for key in time_keys
                 if key in lowered]
        hashes = [candidate[lowered[key]] for key in hash_keys
                  if key in lowered]
        flags = [candidate[lowered[key]] for key in flag_keys
                 if key in lowered]
        if (any(isinstance(value, int) and value >= 0 for value in counts)
                and any(isinstance(value, (int, float))
                        and not isinstance(value, bool) and value >= 0
                        for value in sizes)
                and (any(isinstance(value, (int, float))
                         and not isinstance(value, bool) for value in times)
                     or any(isinstance(value, str) and value
                            for value in hashes))
                and any(flag is True for flag in flags)):
            matching = candidate
            break
    assert matching is not None, (
        "017-001 T6 RED (M4, PC-10): parallel.json debe declarar un canario "
        "del checkout que cubra build/ y .cdad/ (conteo de archivos, tamano "
        "total y mtime maximo o huella equivalente) con unchanged == true en "
        "la corrida limpia; candidatos: %r"
        % [sorted(map(str, item.keys()))
           for item in _find_checkout_canaries(data)])
    assert _find_first_key(data, "canary") is not None, (
        "017-001 T6 RED (M4, PC-10): el canario de configuracion existente "
        "debe seguir declarado ademas del canario del checkout")


def test_parallel_reports_measured_preparation_cost_not_by_subtraction(
        tmp_path):
    """PC-10 (bloqueante 5): sin este test, el costo de reconstruir caches por
    worker se presentaria como (trabajo paralelo - pared serial) sin medirlo,
    y el neto publicado no seria verificable."""
    serial_root = tmp_path / "ev-prep-serial"
    serial_root.mkdir(parents=True, exist_ok=True)
    nodeids_file = _write_nodeids(tmp_path / "ev-prep.nodeids")
    proc = _run("close", "--evidence-root", str(serial_root),
                "--nodeids", str(nodeids_file))
    assert proc.returncode == 0, (
        "017-001 T6 RED (M5, PC-10): el close serial de referencia debe "
        "pasar; rc=%d stderr=%r"
        % (proc.returncode, proc.stderr[-2000:]))
    profiles = sorted(serial_root.rglob("profile.json"))
    assert profiles, (
        "017-001 T6 RED (M5, PC-10): close no conservo profile.json de "
        "referencia para --balance-from")
    reference = json.loads(profiles[0].read_text(encoding="utf-8"))
    ref_prep = _measured_preparation(reference)
    evidence_root = tmp_path / "ev-prep-parallel"
    evidence_root.mkdir(parents=True, exist_ok=True)
    proc = _run("parallel", "--workers", "2", "--evidence-root",
                str(evidence_root), "--nodeids", str(nodeids_file),
                "--balance-from", str(profiles[0]))
    assert proc.returncode == 0, (
        "017-001 T6 RED (M5, PC-10): el lote con --balance-from debe "
        "terminar con rc=0; rc=%d stderr=%r"
        % (proc.returncode, proc.stderr[-2000:]))
    data = _parallel_json(evidence_root, "preparacion")
    assert data.get("preparation_source") == "per-worker-profiles", (
        "017-001 T6 RED (M5, PC-10): parallel.json debe declarar "
        "preparation_source == 'per-worker-profiles' (medido desde los "
        "perfiles por worker, no por resta); informa %r"
        % (data.get("preparation_source"),))
    entries = _per_worker_entries(data, "preparacion")
    assert len(entries) == 2, (
        "017-001 T6 RED (M5, PC-10): dos workers deben traer dos entradas "
        "de detalle, no %d" % len(entries))
    worker_profiles = sorted(evidence_root.glob("worker-*/profile.json"))
    assert worker_profiles, (
        "017-001 T6 RED (M5, PC-10): cada worker debe conservar su "
        "profile.json para verificar preparation_measured_s")
    for candidate in worker_profiles:
        profile = json.loads(candidate.read_text(encoding="utf-8"))
        assert isinstance(profile.get("operations"), list), (
            "017-001 T6 RED (M5, PC-10): %s no trae operations para "
            "respaldar preparation_measured_s" % candidate.parent.name)
    preps = []
    for position, entry in enumerate(entries):
        prep = entry.get("preparation_measured_s")
        assert (isinstance(prep, (int, float))
                and not isinstance(prep, bool) and float(prep) >= 0), (
            "017-001 T6 RED (M5, PC-10): el worker %d debe informar "
            "preparation_measured_s calculado desde SU profile.json; "
            "informa %r" % (position, prep))
        wall = _first_number(entry, "preparacion/w%d" % position, "wall_s")
        assert float(prep) <= float(wall) + 0.01, (
            "017-001 T6 RED (M5, PC-10): preparation_measured_s %r del "
            "worker %d no puede superar su pared %r (es un subconjunto)"
            % (prep, position, wall))
        preps.append(float(prep))
    assert ref_prep is not None, (
        "017-001 T6 RED (M5, PC-10): el perfil serial de referencia no trae "
        "preparation_measured_s ni operaciones de preparacion medibles; sin "
        "el no hay duplicado verificable")
    duplicated = data.get("duplicated_preparation_s")
    assert (isinstance(duplicated, (int, float))
            and not isinstance(duplicated, bool)), (
        "017-001 T6 RED (M5, PC-10): con --balance-from debe informar "
        "duplicated_preparation_s == sum(worker.preparation_measured_s) - "
        "preparacion del perfil de referencia (o null con motivo solo si no "
        "se paso referencia, que aqui si se paso); informa %r" % (duplicated,))
    assert abs(float(duplicated) - (sum(preps) - ref_prep)) <= 1e-3, (
        "017-001 T6 RED (M5, PC-10): duplicated_preparation_s %r no equivale "
        "a sum(worker.preparation_measured_s) - referencia %r "
        "(prohibido derivarlo como trabajo paralelo - pared serial)"
        % (duplicated, sum(preps) - ref_prep))


# ---------------------------------------------------------------------------
# 017-001 T6 RED correccion orphans (packet ...-red-025): una proteccion nueva
# por el hallazgo 3 verificado aparte (orphans=1 con children_terminated=true
# y ningun pytest vivo: el barrido de /proc cuenta procesos cuyo cmdline
# contiene la raiz de evidencia, aunque no sean descendientes del lote — en
# produccion el invocador, sus ancestros o envoltorios; aqui modelado con un
# hermano determinista con la raiz en su cmdline, muerto siempre antes de la
# comprobacion). No modifica los once tests existentes: solo agrega M6.
# M6 -> PC-10 (promesa E). Falla hoy por AssertionError de promesa
# (orphans >= 1), nunca por ImportError ni error de coleccion. Timeout de
# subprocess heredado: guarda de liveness, no oraculo (convencion 11).
# ---------------------------------------------------------------------------


def _self_and_ancestor_pids():
    """PID propio mas cadena de ancestros via /proc/<pid>/status (PPid)."""
    seen = {os.getpid()}
    pid = os.getpid()
    for _ in range(128):
        try:
            with open("/proc/%d/status" % pid, encoding="utf-8",
                      errors="replace") as handle:
                text = handle.read()
        except OSError:
            break
        ppid = None
        for line in text.splitlines():
            if line.startswith("PPid:"):
                try:
                    ppid = int(line.split()[1])
                except (IndexError, ValueError):
                    ppid = None
                break
        if not ppid or ppid <= 0:
            break
        if ppid in seen:
            break
        seen.add(ppid)
        if ppid == 1:
            break
        pid = ppid
    return seen


def _live_descendant_pids_with_marker(marker):
    """PIDs vivos que mencionan marker, excluyendo invocador y ancestros.

    Lo que queda tras excluir la cadena propia son verdaderos descendientes
    (u otros procesos ajenos): justo lo que `orphans` debe contar. El
    invocador y sus ancestros nunca son huerfanos del lote.
    """
    try:
        entries = os.listdir("/proc")
    except OSError:
        return None
    excluded = _self_and_ancestor_pids()
    found = []
    for entry in entries:
        if not entry.isdigit() or int(entry) in excluded:
            continue
        try:
            with open("/proc/%s/cmdline" % entry, "rb") as handle:
                raw = handle.read()
        except OSError:
            continue
        if raw and marker in raw.decode("utf-8", errors="replace"):
            found.append(int(entry))
    return found


def test_parallel_single_worker_reports_zero_orphans_excluding_invoker_and_ancestors(
        tmp_path):
    """PC-10 (T6 hallazgo 3, correccion): sin este test, el lote contaria como
    huerfano a cualquier proceso vivo cuya cmdline mencione la raiz de
    evidencia aunque no sea descendiente suyo (en produccion: el shell
    invocador, envoltorios del lanzador o el propio runner; aqui modelado con
    un hermano determinista), y el usuario creeria que quedan hijos vivos
    cuando no queda ninguno."""
    import signal
    import pytest as pytest_mod
    evidence_root = tmp_path / "ev-orphans-zero"
    evidence_root.mkdir(parents=True, exist_ok=True)
    nodeids_file = _write_single_nodeids(tmp_path / "ev-orphans-zero.nodeids")
    marker = str(evidence_root)
    # Sonda determinista del barrido defectuoso: proceso vivo NO descendiente
    # del lote con la raiz en su cmdline (hermano del lote). El conteo
    # correcto (solo descendientes vivos) debe ignorarlo; el barrido que
    # cuenta por coincidencia de cmdline lo incluye (verificado: un hermano
    # asi eleva orphans a 1 con children_terminated == true). Vive 300 s para
    # cubrir el lote sin depender de la suerte; se mata siempre (finally).
    decoy = subprocess.Popen(
        ["bash", "-c", "sleep 300 & wait", "DECOY-NOT-A-CHILD-" + marker],
        cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True)
    try:
        try:
            proc = _run("parallel", "--workers", "1", "--evidence-root",
                        marker, "--nodeids", str(nodeids_file))
        except subprocess.TimeoutExpired:
            pytest_mod.fail(
                "017-001 T6 RED (M6, PC-10): el lote limpio de un archivo con "
                "--workers 1 no termino en %d s" % TIMEOUT_S)
    finally:
        try:
            os.killpg(decoy.pid, signal.SIGKILL)
        except OSError:
            pass
        try:
            decoy.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass
    assert proc.returncode == 0, (
        "017-001 T6 RED (M6, PC-10): el lote limpio de un archivo con "
        "--workers 1 debe terminar con rc=0; rc=%d stderr=%r"
        % (proc.returncode, proc.stderr[-2000:]))
    data = _parallel_json(evidence_root, "huerfanos-cero")
    checked = _find_first_key(data, "orphans_checked")
    assert checked is True, (
        "017-001 T6 RED (M6, PC-10): parallel.json debe declarar la "
        "comprobacion real de descendientes (orphans_checked == true); "
        "informa %r; claves: %r" % (checked, sorted(map(str, data.keys()))))
    live = _live_descendant_pids_with_marker(str(evidence_root))
    assert live is not None and not live, (
        "017-001 T6 RED (M6, PC-10): justo despues de la corrida exitosa "
        "quedan procesos vivos (no invocador ni ancestros) que mencionan la "
        "raiz %s: %r" % (evidence_root, live))
    orphans = _find_first_key(data, "orphans", "orphan_count",
                              "leftover_children", "children_orphaned")
    assert orphans is not None, (
        "017-001 T6 RED (M6, PC-10): parallel.json debe informar el conteo "
        "medido orphans (no basta orphans_checked == true); claves: %r"
        % sorted(map(str, data.keys())))
    assert isinstance(orphans, int) and not isinstance(orphans, bool), (
        "017-001 T6 RED (M6, PC-10): orphans debe ser un conteo entero, no %r"
        % (orphans,))
    assert orphans == 0, (
        "017-001 T6 RED (M6, PC-10): la corrida limpia con --workers 1 no "
        "deja ningun hijo (barrido /proc sin descendientes vivos) pero "
        "informa orphans=%r: el conteo incluye al invocador o a sus "
        "ancestros en vez de medir solo descendientes vivos" % (orphans,))


# ---------------------------------------------------------------------------
# 017-001 T6 RED correcciones review-T6-002 (packet ...-red-026): dos
# protecciones nuevas por los dos bloqueantes. No modifican los doce tests
# existentes: solo agregan N1..N2. Una por promesa observable, ambas -> PC-10
# (promesa E: paralelismo justificado y seguro). Cada una falla hoy por
# AssertionError de promesa ausente, nunca por ImportError ni error de
# coleccion. Los timeouts son guardas de liveness, no oraculos de duracion
# (convencion 11). Las sondas son archivos de test creados por el test fuera
# de tests/ (arbol temporal) y pasados a --nodeids, para que NUNCA entren en
# la coleccion de --all ni en la suite completa; se borran al terminar
# (finally). No se lee implementacion: CLI como caja negra.
# El canario de configuracion queda cubierto por el mismo codigo de veredicto
# que el canario del checkout (no se fuerza una segunda sonda sobre archivos
# reales del usuario).
# ---------------------------------------------------------------------------

import time as _time_mod
import uuid as _uuid_mod


def _all_pids():
    try:
        return {int(e) for e in os.listdir("/proc") if e.isdigit()}
    except OSError:
        return set()


def _kill_new_sleep60(before_pids):
    """Higiene: mata sleep 60 aparecidos tras before_pids (huérfanos de sonda).

    No es oráculo: solo evita dejar procesos vivos tras el RED. El veredicto
    se decide antes, con pgid/ppid y el campo orphans.
    """
    import signal as _signal_mod
    try:
        entries = os.listdir("/proc")
    except OSError:
        return
    me = os.getpid()
    for entry in entries:
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid == me or pid in before_pids:
            continue
        try:
            with open("/proc/%d/cmdline" % pid, "rb") as handle:
                raw = handle.read()
        except OSError:
            continue
        if not raw:
            continue
        parts = raw.decode("utf-8", errors="replace").split("\x00")
        base = os.path.basename(parts[0]) if parts else ""
        if base == "sleep" and "60" in parts:
            try:
                os.kill(pid, _signal_mod.SIGKILL)
            except OSError:
                pass


def _pgids_from_data(data):
    """pgids de workers registrados en parallel.json (familia por worker)."""
    found = []

    def visit(node):
        if isinstance(node, dict):
            for key, value in node.items():
                lowered = str(key).lower()
                if ("pgid" in lowered or "pgrp" in lowered
                        or "process_group" in lowered):
                    if isinstance(value, bool):
                        pass
                    elif isinstance(value, int) and value > 0:
                        found.append(value)
                    elif isinstance(value, list):
                        for item in value:
                            if (isinstance(item, int)
                                    and not isinstance(item, bool)
                                    and item > 0):
                                found.append(item)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(data)
    return found


def _live_pids_in_pgrp(pgrp):
    """PIDs vivos con pgrp dado, excluyendo invocador y ancestros (/proc/stat)."""
    try:
        entries = os.listdir("/proc")
    except OSError:
        return None
    excluded = _self_and_ancestor_pids()
    found = []
    for entry in entries:
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid in excluded:
            continue
        try:
            with open("/proc/%d/stat" % pid, encoding="utf-8",
                       errors="replace") as handle:
                stat = handle.read()
        except OSError:
            continue
        cut = stat.rfind(")")
        if cut < 0:
            continue
        fields = stat[cut + 1:].split()
        if len(fields) < 4:
            continue
        try:
            entry_pgrp = int(fields[2])
        except ValueError:
            continue
        if entry_pgrp == pgrp:
            found.append(pid)
    return found


def test_parallel_cleans_process_family_without_cmdline_marker(tmp_path):
    """PC-10 (bloqueante 1 de review-T6-002): sin este test, el conteo de
    huérfanos por coincidencia de cmdline no vería a un descendiente vivo
    sin la raíz en sus argumentos y publicaría orphans=0 como si no quedara
    nadie, con éxito limpio y sin familia registrada."""
    probe_dir = tmp_path / "probe-family"
    probe_dir.mkdir(parents=True, exist_ok=True)
    probe_path = probe_dir / "test_probe_family_026.py"
    probe_path.write_text(
        "import subprocess\n"
        "\n"
        "\n"
        "def test_probe_spawns_markerless_child_surviving_pytest():\n"
        "    subprocess.Popen([\"/bin/sleep\", \"60\"],\n"
        "                     stdin=subprocess.DEVNULL,\n"
        "                     stdout=subprocess.DEVNULL,\n"
        "                     stderr=subprocess.DEVNULL)\n",
        encoding="utf-8")
    nodeids_path = tmp_path / "ev-family.nodeids"
    nodeids_path.write_text(
        "%s::test_probe_spawns_markerless_child_surviving_pytest\n"
        % probe_path, encoding="utf-8")
    evidence_root = tmp_path / "ev-family"
    evidence_root.mkdir(parents=True, exist_ok=True)
    before = _all_pids()
    try:
        proc = _run("parallel", "--workers", "1", "--evidence-root",
                    str(evidence_root), "--nodeids", str(nodeids_path),
                    timeout=TIMEOUT_S)
        data = _parallel_json(evidence_root, "familia")
        orphans = _find_first_key(data, "orphans", "orphan_count",
                                  "leftover_children", "children_orphaned")
        cleaned = _find_first_key(data, "orphans_cleaned", "orphans_reaped",
                                  "descendants_cleaned", "cleaned_orphans",
                                  "reaped_orphans")
        honest = (isinstance(orphans, int)
                  and not isinstance(orphans, bool) and orphans >= 1)
        if not honest and isinstance(cleaned, int) \
                and not isinstance(cleaned, bool) and cleaned >= 1:
            honest = True
        assert honest, (
            "017-001 T6 RED (N1, PC-10): el lote con un hijo vivo sin la "
            "raíz en su cmdline debe reportar honestamente que encontró y "
            "limpió descendientes vivos (orphans >= 1 o campo equivalente); "
            "informa orphans=%r cleaned=%r (el conteo por cmdline no ve al "
            "hijo y publica orphans=0)" % (orphans, cleaned))
        pgids = _pgids_from_data(data)
        if not pgids:
            for entry in _per_worker_entries(data, "familia"):
                if isinstance(entry, dict):
                    for key in ("pgid", "pgrp", "process_group", "family"):
                        value = entry.get(key)
                        if (isinstance(value, int)
                                and not isinstance(value, bool)
                                and value > 0):
                            pgids.append(value)
        assert pgids, (
            "017-001 T6 RED (N1, PC-10): parallel.json debe registrar la "
            "familia del worker (por ejemplo pgid por worker); claves: %r"
            % sorted(map(str, data.keys())))
        assert proc.returncode != 0, (
            "017-001 T6 RED (N1, PC-10): el lote que encontró descendientes "
            "vivos debe terminar con estado de descarte/fallo declarado, no "
            "con éxito limpio; rc=%d" % proc.returncode)
        for pgid in pgids:
            live = _live_pids_in_pgrp(pgid)
            assert live is not None and not live, (
                "017-001 T6 RED (N1, PC-10): tras el comando queda familia "
                "viva con pgid %r: %r (barrido /proc por pgid, no por "
                "cmdline)" % (pgid, live))
    finally:
        _kill_new_sleep60(before)
        for path in (probe_path, nodeids_path):
            try:
                path.unlink()
            except OSError:
                pass


def test_parallel_altered_checkout_canary_rejects_run(tmp_path):
    """PC-10 (bloqueante 2 de review-T6-002): sin este test, una corrida con
    el checkout alterado a mitad del lote saldría 0 con solo un aviso y se
    presentaría como utilizable pese a haber perdido el aislamiento."""
    import signal as _signal_mod
    import pytest as _pytest_mod
    probe_dir = tmp_path / "probe-canary"
    probe_dir.mkdir(parents=True, exist_ok=True)
    probe_path = probe_dir / "test_probe_canary_026.py"
    probe_path.write_text(
        "import time\n"
        "\n"
        "\n"
        "def test_probe_slow_enough_for_midrun_canary():\n"
        "    time.sleep(5)\n",
        encoding="utf-8")
    nodeids_path = tmp_path / "ev-canary-reject.nodeids"
    nodeids_path.write_text(
        "%s::test_probe_slow_enough_for_midrun_canary\n" % probe_path,
        encoding="utf-8")
    evidence_root = tmp_path / "ev-canary-reject"
    evidence_root.mkdir(parents=True, exist_ok=True)
    sentinel = REPO_ROOT / "build" / (
        ".canary_probe_%s" % _uuid_mod.uuid4().hex[:12])
    proc = subprocess.Popen(
        SUITE + ["parallel", "--workers", "1", "--evidence-root",
                 str(evidence_root), "--nodeids", str(nodeids_path)],
        cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True)
    try:
        _time_mod.sleep(2)  # deja arrancar el lote (la sonda tarda ~5 s).
        sentinel.write_text("canary probe 026\n", encoding="utf-8")
        try:
            _, stderr = proc.communicate(timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, _signal_mod.SIGKILL)
            except OSError:
                pass
            proc.wait(timeout=30)
            _pytest_mod.fail(
                "017-001 T6 RED (N2, PC-10): el lote con canario alterado no "
                "terminó en %d s" % TIMEOUT_S)
    finally:
        try:
            sentinel.unlink()
        except OSError:
            pass
        for path in (probe_path, nodeids_path):
            try:
                path.unlink()
            except OSError:
                pass
    assert proc.returncode != 0, (
        "017-001 T6 RED (N2, PC-10): el lote con el checkout alterado a "
        "mitad de corrida debe salir distinto de 0 (descarte/fallo), no con "
        "éxito limpio; rc=%d stderr=%r"
        % (proc.returncode, (stderr or "")[-2000:]))
    data = _parallel_json(evidence_root, "canario-rechazo")
    verdict = _find_first_key(data, "verdict", "decision", "disposition",
                              "run_verdict", "batch_verdict", "outcome")
    assert isinstance(verdict, str) and (
            "reject" in verdict.lower() or "discard" in verdict.lower()), (
        "017-001 T6 RED (N2, PC-10): parallel.json debe marcar la corrida "
        "como rechazada/descartada con un campo de veredicto explícito "
        "conservando la evidencia; informa %r" % (verdict,))


# ---------------------------------------------------------------------------
# 017-001 T6 RED correcciones review-T6-003 (packet ...-red-027): dos
# protecciones nuevas por los dos bloqueantes. No modifican los catorce tests
# existentes: solo agregan O1..O2. Una por promesa observable, ambas -> PC-10
# (promesa E: paralelismo justificado y seguro). Cada una falla hoy por
# AssertionError de promesa ausente, nunca por ImportError ni error de
# coleccion. Los timeouts son guardas de liveness, no oraculos de duracion
# (convencion 11). Las sondas son archivos de test creados por el test fuera
# de tests/ (arbol temporal) y pasados a --nodeids, para que NUNCA entren en
# la coleccion de --all ni en la suite completa; se borran al terminar
# (finally). No se lee implementacion: CLI como caja negra.
# Pre-RED: N1 cubre hijo sin marcador que sigue en el grupo (barrido por pgid
# lo veria); O1 cubre hijo que ABANDONA grupo y sesion (pgid ya no lo
# contiene). N2 cubre centinela AGREGADO en build/ (el conteo lo delata); O2
# cubre reescritura del MISMO tamano con mtime restaurado (conteo, bytes y
# mtime maximo no cambian: la huella ciega no lo ve).
# ---------------------------------------------------------------------------


def _stat_family(pid):
    """(ppid, pgrp, sid) de un PID vivo via /proc/<pid>/stat; None si murio."""
    try:
        with open("/proc/%d/stat" % pid, encoding="utf-8",
                   errors="replace") as handle:
            stat = handle.read()
    except OSError:
        return None
    cut = stat.rfind(")")
    if cut < 0:
        return None
    fields = stat[cut + 1:].split()
    if len(fields) < 5:
        return None
    try:
        return (int(fields[1]), int(fields[2]), int(fields[3]))
    except ValueError:
        return None


def _find_new_sleep120(before_pids):
    """sleep 120 aparecidos tras before_pids, con su familia (ppid/pgid/sid).

    Barrido por marca de la sonda (el binario y su duracion), no por grupo:
    un hijo con start_new_session=True ya no comparte pgid con el worker, asi
    que solo un barrido ajeno al grupo lo encuentra. Excluye invocador y
    ancestros.
    """
    try:
        entries = os.listdir("/proc")
    except OSError:
        return None
    excluded = _self_and_ancestor_pids()
    found = []
    for entry in entries:
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid in excluded or pid in before_pids:
            continue
        try:
            with open("/proc/%d/cmdline" % pid, "rb") as handle:
                raw = handle.read()
        except OSError:
            continue
        if not raw:
            continue
        parts = raw.decode("utf-8", errors="replace").split("\x00")
        base = os.path.basename(parts[0]) if parts else ""
        if base == "sleep" and "120" in parts:
            found.append({"pid": pid, "family": _stat_family(pid)})
    return found


def _kill_pids(pids):
    import signal as _signal_mod
    for pid in pids:
        try:
            os.kill(pid, _signal_mod.SIGKILL)
        except OSError:
            pass


def _mutate_same_size(data):
    """Bytes distintos del mismo tamano; None si no hay que mutar."""
    if not data:
        return None
    mutated = bytearray(data)
    mutated[0] = (mutated[0] + 1) % 256
    if bytes(mutated) == data:
        mutated[0] = (mutated[0] + 1) % 256
    return bytes(mutated)


def test_parallel_detects_session_escaped_descendant_and_discards_run(
        tmp_path):
    """PC-10 (bloqueante 1 de review-T6-003): sin este test, un descendiente
    que abandona grupo y sesion (start_new_session=True) quedaria vivo tras
    el lote mientras este declara orphans=0 con exito limpio, y el usuario
    adoptaria --workers 1 como seguro sin que nada lo detecte."""
    probe_dir = tmp_path / "probe-session"
    probe_dir.mkdir(parents=True, exist_ok=True)
    probe_path = probe_dir / "test_probe_session_027.py"
    probe_path.write_text(
        "import subprocess\n"
        "\n"
        "\n"
        "def test_probe_spawns_new_session_child_surviving_pytest():\n"
        "    subprocess.Popen([\"/bin/sleep\", \"120\"],\n"
        "                     stdin=subprocess.DEVNULL,\n"
        "                     stdout=subprocess.DEVNULL,\n"
        "                     stderr=subprocess.DEVNULL,\n"
        "                     start_new_session=True)\n",
        encoding="utf-8")
    nodeids_path = tmp_path / "ev-session.nodeids"
    nodeids_path.write_text(
        "%s::test_probe_spawns_new_session_child_surviving_pytest\n"
        % probe_path, encoding="utf-8")
    evidence_root = tmp_path / "ev-session"
    evidence_root.mkdir(parents=True, exist_ok=True)
    before = _all_pids()
    try:
        proc = _run("parallel", "--workers", "1", "--evidence-root",
                    str(evidence_root), "--nodeids", str(nodeids_path),
                    timeout=TIMEOUT_S)
        data = _parallel_json(evidence_root, "sesion")
        orphans = _find_first_key(data, "orphans", "orphan_count",
                                  "leftover_children", "children_orphaned")
        cleaned = _find_first_key(data, "orphans_cleaned", "orphans_reaped",
                                  "descendants_cleaned", "cleaned_orphans",
                                  "reaped_orphans")
        honest = (isinstance(orphans, int)
                  and not isinstance(orphans, bool) and orphans >= 1)
        if not honest and isinstance(cleaned, int) \
                and not isinstance(cleaned, bool) and cleaned >= 1:
            honest = True
        leftovers = _find_new_sleep120(before)
        leftover_detail = leftovers
        assert honest, (
            "017-001 T6 RED (O1, PC-10): el lote con un descendiente vivo que "
            "abandono grupo y sesion debe reportar honestamente que encontro "
            "y limpio actividad viva (orphans >= 1 o campo equivalente); "
            "informa orphans=%r cleaned=%r, familia viva %r (el barrido por "
            "grupo no ve al hijo con start_new_session=True y publica "
            "orphans=0)" % (orphans, cleaned, leftover_detail))
        verdict = _find_first_key(data, "verdict", "decision", "disposition",
                                  "run_verdict", "batch_verdict", "outcome")
        assert isinstance(verdict, str) and (
                "reject" in verdict.lower()
                or "discard" in verdict.lower()), (
            "017-001 T6 RED (O1, PC-10): el lote que encontro actividad viva "
            "fuera de su grupo debe marcar veredicto de descarte conservando "
            "la evidencia; informa %r" % (verdict,))
        assert proc.returncode != 0, (
            "017-001 T6 RED (O1, PC-10): el lote que encontro descendientes "
            "vivos fuera de su grupo NO debe devolver exito limpio; rc=%d "
            "stderr=%r" % (proc.returncode, proc.stderr[-2000:]))
        assert leftovers is not None and not leftovers, (
            "017-001 T6 RED (O1, PC-10): tras el comando no debe quedar "
            "ningun proceso vivo de esa familia (barrido /proc con "
            "ppid/pgid/sid); vivos: %r" % (leftovers,))
    finally:
        remaining = _find_new_sleep120(before) or []
        _kill_pids(item["pid"] for item in remaining)
        for path in (probe_path, nodeids_path):
            try:
                path.unlink()
            except OSError:
                pass


def test_parallel_checkout_fingerprint_detects_same_size_same_mtime_rewrite(
        tmp_path):
    """PC-10 (bloqueante 2 de review-T6-003): sin este test, una reescritura
    persistente en build/ del MISMO tamano con el mtime original restaurado
    (conteo, bytes totales y mtime maximo intactos) saldria 0 como aceptada,
    y el usuario creeria que la huella del checkout protege lo que no ve."""
    import signal as _signal_mod
    import pytest as _pytest_mod
    probe_dir = tmp_path / "probe-fingerprint"
    probe_dir.mkdir(parents=True, exist_ok=True)
    probe_path = probe_dir / "test_probe_fingerprint_027.py"
    probe_path.write_text(
        "import time\n"
        "\n"
        "\n"
        "def test_probe_slow_enough_for_midrun_rewrite():\n"
        "    time.sleep(5)\n",
        encoding="utf-8")
    nodeids_path = tmp_path / "ev-fingerprint.nodeids"
    nodeids_path.write_text(
        "%s::test_probe_slow_enough_for_midrun_rewrite\n" % probe_path,
        encoding="utf-8")
    evidence_root = tmp_path / "ev-fingerprint"
    evidence_root.mkdir(parents=True, exist_ok=True)
    build_root = REPO_ROOT / "build"
    candidates = []
    for path in sorted(build_root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if 1 <= size <= 65536 and os.access(path, os.R_OK | os.W_OK):
            candidates.append((size, str(path)))
    assert candidates, (
        "017-001 T6 RED (O2, PC-10): sin archivo reescribible bajo build/ no "
        "hay mutacion que proponer (entorno, no promesa)")
    target = None
    original = None
    saved_ns = None
    tried = []
    for _, name in candidates:
        candidate = Path(name)
        try:
            content = candidate.read_bytes()
        except OSError as exc:
            tried.append("%s: %s" % (name, exc))
            continue
        mutated = _mutate_same_size(content)
        if mutated is None or mutated == content:
            tried.append("%s: sin mutacion distinta" % name)
            continue
        try:
            st = candidate.stat()
        except OSError as exc:
            tried.append("%s: %s" % (name, exc))
            continue
        target, original = candidate, content
        saved_ns = (st.st_atime_ns, st.st_mtime_ns)
        break
    assert target is not None, (
        "017-001 T6 RED (O2, PC-10): ningun archivo bajo build/ se pudo "
        "reescribir (probados: %r)" % (tried[:5],))
    proc = subprocess.Popen(
        SUITE + ["parallel", "--workers", "1", "--evidence-root",
                 str(evidence_root), "--nodeids", str(nodeids_path)],
        cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True)
    stderr = ""
    try:
        _time_mod.sleep(2)  # deja arrancar el lote (la sonda tarda ~5 s).
        target.write_bytes(_mutate_same_size(original))
        os.utime(target, ns=saved_ns)  # misma huella: tamano y mtime.
        check = target.stat()
        assert check.st_size == len(original) and \
            (check.st_atime_ns, check.st_mtime_ns) == saved_ns, (
            "017-001 T6 RED (O2, PC-10): la mutacion debe conservar tamano y "
            "mtime de %s (entorno, no promesa)" % target)
        try:
            _, stderr = proc.communicate(timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, _signal_mod.SIGKILL)
            except OSError:
                pass
            proc.wait(timeout=30)
            _pytest_mod.fail(
                "017-001 T6 RED (O2, PC-10): el lote con reescritura del "
                "mismo tamano y mtime en %s no termino en %d s"
                % (target, TIMEOUT_S))
    finally:
        try:
            target.write_bytes(original)
        except OSError:
            pass
        try:
            os.utime(target, ns=saved_ns)
        except OSError:
            pass
        for path in (probe_path, nodeids_path):
            try:
                path.unlink()
            except OSError:
                pass
    assert proc.returncode != 0, (
        "017-001 T6 RED (O2, PC-10): el lote con una reescritura persistente "
        "del mismo tamano y mtime en %s debe salir distinto de 0 "
        "(descarte), no con exito limpio; rc=%d stderr=%r"
        % (target, proc.returncode, (stderr or "")[-2000:]))
    data = _parallel_json(evidence_root, "huella")
    verdict = _find_first_key(data, "verdict", "decision", "disposition",
                              "run_verdict", "batch_verdict", "outcome")
    assert isinstance(verdict, str) and (
            "reject" in verdict.lower() or "discard" in verdict.lower()), (
        "017-001 T6 RED (O2, PC-10): parallel.json debe marcar la corrida "
        "como rechazada/descartada con un campo de veredicto explícito "
        "conservando la evidencia; informa %r" % (verdict,))


# ---------------------------------------------------------------------------
# 017-001 T6 RED correccion ventana de gracia (packet ...-red-028): una
# proteccion nueva por la correccion de T6 (la corrida real de dos workers
# sobre los seis archivos mas caros se descarto porque, al terminar pytest,
# quedaban 10 procesos de la familia vivos; 5 murieron solos y 5 se
# limpiaron, y el veredicto fue descarte: sin ventana de gracia, cualquier
# hijo transitorio hace imposible correr --all). No modifica los dieciseis
# tests existentes: solo agrega P1. Una promesa observable -> PC-10
# (promesa E: paralelismo justificado y seguro). Falla hoy por AssertionError
# de promesa (rc 3 con descarte), nunca por ImportError ni error de
# coleccion. El timeout es guarda de liveness, no oraculo (convencion 11).
# La sonda es un archivo de test creado por el test fuera de tests/ (arbol
# temporal) y pasado a --nodeids, para que NUNCA entre en la coleccion de
# --all ni en la suite completa; se borra al terminar (finally). No se lee
# implementacion: CLI como caja negra. Pre-RED: ningun verificador cubre al
# hijo transitorio que muere solo poco despues de pytest (N1 cubre hijo sin
# marcador que SIGUE vivo con sleep 60; O1 cubre hijo con nueva sesion que
# SIGUE vivo con sleep 120; M6 cubre conteo cero excluyendo invocador; nada
# sobre hijo de ~1.5 s sin start_new_session que sigue vivo al salir pytest
# y muere solo dentro de la ventana).
# ---------------------------------------------------------------------------


def _grace_found_count(data):
    """orphans_found (o equivalente) a nivel agregado o suma por worker."""
    for key in ("orphans_found", "found_orphans", "family_found",
                "descendants_found", "grace_found"):
        value = _find_first_key(data, key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int) and value >= 0:
            return value
    try:
        entries = _per_worker_entries(data, "gracia")
    except AssertionError:
        return None
    total, seen = 0, False
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for key in ("orphans_found", "found_orphans", "family_found",
                    "descendants_found", "grace_found"):
            value = entry.get(key)
            if isinstance(value, int) and not isinstance(value, bool) \
                    and value >= 0:
                total += value
                seen = True
                break
    return total if seen else None


def _grace_pid_detail(data):
    """Detalle de pids de la familia encontrada (lista o dict no vacio)."""
    for key in ("orphans_found_pids", "found_pids", "orphan_pids",
                "family_pids", "descendant_pids", "descendants_pids",
                "grace_pids", "pids", "found_detail", "family_detail",
                "orphans_detail"):
        value = _find_first_key(data, key)
        if isinstance(value, list) and value:
            return value
        if isinstance(value, dict) and value:
            return value
    found = []

    def visit(node):
        if isinstance(node, dict):
            for key, value in node.items():
                lowered = str(key).lower()
                if "pgid" in lowered or "pgrp" in lowered \
                        or "process_group" in lowered:
                    pass
                elif "pid" in lowered:
                    if isinstance(value, int) \
                            and not isinstance(value, bool) and value > 0:
                        found.append(value)
                    elif isinstance(value, list) and value:
                        for item in value:
                            if isinstance(item, int) \
                                    and not isinstance(item, bool) \
                                    and item > 0:
                                found.append(item)
                            elif isinstance(item, dict) \
                                    and isinstance(item.get("pid"), int):
                                found.append(item["pid"])
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(data)
    return found or None


def _find_new_sleep15(before_pids):
    """sleep 1.5 aparecidos tras before_pids (marca de la sonda P1)."""
    try:
        entries = os.listdir("/proc")
    except OSError:
        return None
    excluded = _self_and_ancestor_pids()
    found = []
    for entry in entries:
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid in excluded or pid in before_pids:
            continue
        try:
            with open("/proc/%d/cmdline" % pid, "rb") as handle:
                raw = handle.read()
        except OSError:
            continue
        if not raw:
            continue
        parts = raw.decode("utf-8", errors="replace").split("\x00")
        base = os.path.basename(parts[0]) if parts else ""
        if base == "sleep" and "1.5" in parts:
            found.append(pid)
    return found


def _kill_new_sleep15(before_pids):
    """Higiene: mata sleep 1.5 aparecidos tras before_pids (hijos de sonda).

    No es oraculo: solo evita dejar procesos vivos tras el RED. El veredicto
    se decide antes, con rc, veredicto y los campos orphans_found/orphans.
    """
    import signal as _signal_mod
    try:
        entries = os.listdir("/proc")
    except OSError:
        return
    me = os.getpid()
    for entry in entries:
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid == me or pid in before_pids:
            continue
        try:
            with open("/proc/%d/cmdline" % pid, "rb") as handle:
                raw = handle.read()
        except OSError:
            continue
        if not raw:
            continue
        parts = raw.decode("utf-8", errors="replace").split("\x00")
        base = os.path.basename(parts[0]) if parts else ""
        if base == "sleep" and "1.5" in parts:
            try:
                os.kill(pid, _signal_mod.SIGKILL)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# 017-001 T7 RED correccion del veredicto del canario (packet
# ...-test-writer-red-029): UNA proteccion nueva por el veredicto descartado
# de la corrida final T7 (con --all el lote se rechazo aunque huella,
# conteo y bytes quedaron IDENTICOS; solo cambio max_mtime_ns porque el
# scratch declarado bajo .cdad/tmp crea y retira subdirectorios y eso mueve
# el mtime de los directorios padres). No modifica los diecisiete tests
# existentes: solo agrega Q1. Una promesa observable -> PC-10 (promesa E:
# paralelismo justificado y seguro; canario del checkout) con apoyo en
# PC-12 (promesa F: canario examinado en la corrida atribuible). Falla hoy
# por AssertionError de promesa (rc 3 con rechazo), nunca por ImportError ni
# error de coleccion. El timeout es guarda de liveness, no oraculo
# (convencion 11). La sonda es un archivo de test creado por el test fuera
# de tests/ (arbol temporal) y pasado a --nodeids, para que NUNCA entre en
# la coleccion de --all ni en la suite completa; se borra al terminar
# (finally) junto con el subdirectorio de churn bajo <repo>/.cdad/tmp/.
# No se lee implementacion: CLI como caja negra. Pre-RED: N2 cubre
# centinela AGREGADO (rechazo esperado); O2 cubre reescritura persistente
# del mismo tamano (rechazo esperado); nada cubre churn transitorio de
# directorios bajo .cdad/tmp sin cambio de contenido (aceptacion esperada).
# Sin este test, el usuario veria rechazada toda corrida --all con scratch
# declarado sin que nada lo detecte como defecto de veredicto.
# ---------------------------------------------------------------------------


def test_parallel_accepts_cdad_tmp_subdir_churn_without_content_change(
        tmp_path):
    """PC-10 (T7 correccion del veredicto del canario): sin este test, una
    corrida en la que una sonda crea y retira un subdirectorio unico bajo
    .cdad/tmp durante el lote (sin tocar contenido ni dejar archivos nuevos)
    se rechaza con rc 3 por el mtime de los directorios padres, y el usuario
    no podria aprobar --all con scratch declarado sin que nada lo detecte."""
    import shutil as _shutil_mod
    churn_name = "canary-churn-%s" % _uuid_mod.uuid4().hex[:12]
    churn_dir = REPO_ROOT / ".cdad" / "tmp" / churn_name
    probe_dir = tmp_path / "probe-canary-churn"
    probe_dir.mkdir(parents=True, exist_ok=True)
    probe_path = probe_dir / "test_probe_canary_churn_029.py"
    probe_path.write_text(
        "import shutil\n"
        "from pathlib import Path\n"
        "\n"
        "REPO = Path(%r)\n" % str(REPO_ROOT)
        + "\n"
        "\n"
        "def test_probe_creates_and_removes_tmp_subdir():\n"
        "    target = REPO / \".cdad\" / \"tmp\" / %r\n" % churn_name
        + "    target.mkdir(parents=True, exist_ok=True)\n"
        "    assert target.is_dir()\n"
        "    shutil.rmtree(target, ignore_errors=True)\n"
        "    assert not target.exists()\n",
        encoding="utf-8")
    nodeids_path = tmp_path / "ev-canary-churn.nodeids"
    nodeids_path.write_text(
        "%s::test_probe_creates_and_removes_tmp_subdir\n" % probe_path,
        encoding="utf-8")
    evidence_root = tmp_path / "ev-canary-churn"
    evidence_root.mkdir(parents=True, exist_ok=True)
    try:
        proc = _run("parallel", "--workers", "1", "--evidence-root",
                    str(evidence_root), "--nodeids", str(nodeids_path),
                    timeout=TIMEOUT_S)
        assert proc.returncode == 0, (
            "017-001 T7 RED (Q1, PC-10): el lote con churn transitorio bajo "
            ".cdad/tmp (crear y retirar %s sin tocar contenido) debe terminar "
            "con exito (rc 0), no rechazar la corrida; rc=%d stderr=%r"
            % (churn_name, proc.returncode, proc.stderr[-2000:]))
        data = _parallel_json(evidence_root, "canario-churn")
        verdict = _find_first_key(data, "verdict", "decision", "disposition",
                                  "run_verdict", "batch_verdict", "outcome")
        assert isinstance(verdict, str) and "accept" in verdict.lower(), (
            "017-001 T7 RED (Q1, PC-10): parallel.json debe marcar la corrida "
            "con churn transitorio como aceptada con veredicto explicito; "
            "informa %r" % (verdict,))
        canaries = _find_checkout_canaries(data)
        assert canaries, (
            "017-001 T7 RED (Q1, PC-10): parallel.json debe declarar el "
            "canario del checkout junto al veredicto; claves: %r"
            % sorted(map(str, data.keys())))
        unchanged_flags = [
            item.get("unchanged") for item in canaries
            if isinstance(item, dict) and "unchanged" in item]
        assert unchanged_flags and all(
            flag is True for flag in unchanged_flags), (
            "017-001 T7 RED (Q1, PC-10): el canario del checkout debe "
            "informar unchanged == true cuando solo hubo churn transitorio "
            "de directorios bajo .cdad/tmp (contenido identico); informa %r"
            % ([sorted(map(str, item.keys())) for item in canaries],))
        mtime_values = []
        for item in canaries:
            if not isinstance(item, dict):
                continue
            for key, value in item.items():
                lowered = str(key).lower()
                if "max_mtime" in lowered or "mtime_max" in lowered \
                        or "latest_mtime" in lowered \
                        or "newest_mtime" in lowered:
                    mtime_values.append(value)
        assert mtime_values and all(
            value is not None for value in mtime_values), (
            "017-001 T7 RED (Q1, PC-10): el canario debe seguir informando "
            "max_mtime_ns como informacion (no nulo) aunque ya no decida el "
            "veredicto; valores: %r" % (mtime_values,))
        assert not churn_dir.exists(), (
            "017-001 T7 RED (Q1, PC-10): la sonda no debe dejar residuos: "
            "%s sigue existiendo" % churn_dir)
    finally:
        _shutil_mod.rmtree(churn_dir, ignore_errors=True)
        for path in (probe_path, nodeids_path):
            try:
                path.unlink()
            except OSError:
                pass
def test_parallel_transient_child_within_grace_window_is_accepted(tmp_path):
    """PC-10 (T6 correccion ventana de gracia): sin este test, un hijo de
    vida corta que sigue vivo cuando pytest sale y muere solo poco despues
    (aqui sleep 1.5 sin start_new_session) descarta la corrida con rc 3, y
    cualquier hijo transitorio de un test haria imposible correr --all sin
    que nada lo detecte."""
    probe_dir = tmp_path / "probe-grace"
    probe_dir.mkdir(parents=True, exist_ok=True)
    probe_path = probe_dir / "test_probe_grace_028.py"
    probe_path.write_text(
        "import subprocess\n"
        "\n"
        "\n"
        "def test_probe_spawns_transient_child_dying_right_after_pytest():\n"
        "    subprocess.Popen([\"/bin/sleep\", \"1.5\"],\n"
        "                     stdin=subprocess.DEVNULL,\n"
        "                     stdout=subprocess.DEVNULL,\n"
        "                     stderr=subprocess.DEVNULL)\n",
        encoding="utf-8")
    nodeids_path = tmp_path / "ev-grace.nodeids"
    nodeids_path.write_text(
        "%s::test_probe_spawns_transient_child_dying_right_after_pytest\n"
        % probe_path, encoding="utf-8")
    evidence_root = tmp_path / "ev-grace"
    evidence_root.mkdir(parents=True, exist_ok=True)
    before = _all_pids()
    try:
        proc = _run("parallel", "--workers", "1", "--evidence-root",
                    str(evidence_root), "--nodeids", str(nodeids_path),
                    timeout=TIMEOUT_S)
        assert proc.returncode == 0, (
            "017-001 T6 RED (P1, PC-10): el lote con un hijo transitorio que "
            "muere solo dentro de la ventana (~1.5 s, sin start_new_session) "
            "debe terminar con exito (rc 0), no descartar la corrida; rc=%d "
            "stderr=%r" % (proc.returncode, proc.stderr[-2000:]))
        data = _parallel_json(evidence_root, "gracia")
        verdict = _find_first_key(data, "verdict", "decision", "disposition",
                                  "run_verdict", "batch_verdict", "outcome")
        assert isinstance(verdict, str) and "accept" in verdict.lower(), (
            "017-001 T6 RED (P1, PC-10): parallel.json debe marcar la corrida "
            "con hijo transitorio como aceptada con veredicto explicito; "
            "informa %r" % (verdict,))
        found = _grace_found_count(data)
        assert isinstance(found, int) and not isinstance(found, bool) \
            and found >= 1, (
            "017-001 T6 RED (P1, PC-10): el lote debe registrar que encontro "
            "procesos de la familia (orphans_found >= 1); informa %r; "
            "claves: %r" % (found, sorted(map(str, data.keys()))))
        detail = _grace_pid_detail(data)
        assert detail, (
            "017-001 T6 RED (P1, PC-10): el hallazgo de familia debe traer "
            "detalle de pids (lista o dict no vacio con los pids "
            "encontrados); sin detalle no hay evidencia de que se vio al "
            "hijo transitorio")
        orphans = _find_first_key(data, "orphans", "orphan_count",
                                  "leftover_children", "children_orphaned")
        assert isinstance(orphans, int) and not isinstance(orphans, bool), (
            "017-001 T6 RED (P1, PC-10): parallel.json debe informar el conteo "
            "final orphans como entero; informa %r" % (orphans,))
        assert orphans == 0, (
            "017-001 T6 RED (P1, PC-10): tras la ventana de gracia no debe "
            "quedar ningun hijo vivo (orphans == 0); informa orphans=%r "
            "(el hijo de 1.5 s muere solo dentro de la ventana)" % (orphans,))
        live = _find_new_sleep15(before)
        assert live is not None and not live, (
            "017-001 T6 RED (P1, PC-10): tras el comando no debe quedar "
            "ningun sleep 1.5 de la sonda vivo; vivos: %r" % (live,))
    finally:
        _kill_new_sleep15(before)
        for path in (probe_path, nodeids_path):
            try:
                path.unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# 017-001 T7 RED cierre fail-closed (packet ...-test-writer-red-032): CUATRO
# protecciones nuevas por los cuatro bloqueantes de review-final-product.md.
# No modifican los dieciocho tests existentes: solo agregan R1..R4. Una por
# promesa observable, todas -> PC-10 (promesa E: paralelismo justificado y
# seguro; R4 con apoyo en INV-1/INV-6 de atribuibilidad de la evidencia).
# Cada una falla hoy por AssertionError de promesa ausente, nunca por
# ImportError ni error de coleccion. Los timeouts son guardas de liveness, no
# oraculos de duracion (convencion 11). La costura de inyeccion de fallo
# CDAD_SUITE_FAULT (no-subreaper/no-sweep) es contrato acordado: en corridas
# normales no se define y no altera nada. No se lee implementacion: CLI como
# caja negra sobre seleccion liviana en evidencia descartable (tmp_path, fuera
# del checkout); los artefactos bajo build/ y .cdad/tmp se retiran en finally.
# Pre-RED: ningun verificador existente cubre garantia de familia no
# acreditable, canario previo a resolver la familia, barrido ilegible con
# campo de incompletitud, ni reuso de evidencia (sin CDAD_SUITE_FAULT ni
# veredictos incomplete/occupied en la suite).
# ---------------------------------------------------------------------------


def _run_with_fault(*args, fault, timeout=TIMEOUT_S):
    """Corre la CLI con CDAD_SUITE_FAULT=fault sin tocar os.environ."""
    env = dict(os.environ)
    env["CDAD_SUITE_FAULT"] = fault
    return subprocess.run(
        SUITE + list(args),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _find_incomplete_entries(node):
    """Entradas cuyo campo menciona incompletitud del barrido/canario."""
    found = []

    def visit(item, path):
        if isinstance(item, dict):
            for key, value in item.items():
                if "incomplete" in str(key).lower():
                    found.append((path + "/" + str(key), value))
                visit(value, path + "/" + str(key))
        elif isinstance(item, list):
            for position, value in enumerate(item):
                visit(value, "%s[%d]" % (path, position))

    visit(node, "$")
    return found


def test_parallel_unverifiable_family_is_not_accepted(tmp_path):
    """PC-10 (bloqueante 1 de review-final-product): sin este test, un lote
    cuya garantia de familia no puede acreditarse (subreaper inactivo o
    barrido no disponible) saldria accepted con pytest verde, y el usuario
    presentaria como limpio un lote que pudo dejar actividad viva."""
    for fault in ("no-subreaper", "no-sweep"):
        evidence_root = tmp_path / ("ev-fault-%s" % fault)
        evidence_root.mkdir(parents=True, exist_ok=True)
        nodeids_file = tmp_path / ("ev-fault-%s.nodeids" % fault)
        nodeids_file.write_text(
            "".join(n + "\n" for n in NODEIDS), encoding="utf-8")
        proc = _run_with_fault(
            "parallel", "--workers", "2", "--evidence-root",
            str(evidence_root), "--nodeids", str(nodeids_file), fault=fault)
        assert proc.returncode != 0, (
            "017-001 T7 RED (R1, PC-10): con CDAD_SUITE_FAULT=%s la corrida "
            "NO debe declararse accepted (la garantia de familia no esta "
            "acreditada); hoy sale accepted con rc=0" % fault)
        data = _parallel_json(evidence_root, "familia-%s" % fault)
        verdict = _find_first_key(data, "verdict", "decision", "disposition",
                                  "run_verdict", "batch_verdict", "outcome")
        assert isinstance(verdict, str) \
            and "accept" not in verdict.lower(), (
            "017-001 T7 RED (R1, PC-10): con CDAD_SUITE_FAULT=%s "
            "parallel.json debe declarar el veredicto como no aceptado; "
            "informa %r" % (fault, verdict))
        blob = ((proc.stderr or "") + " "
                + json.dumps(data, ensure_ascii=False)).lower()
        assert any(marker in blob for marker in (
                "subreaper", "sweep", "barrido", "family", "familia",
                "fault", "guarantee", "garant")), (
            "017-001 T7 RED (R1, PC-10): con CDAD_SUITE_FAULT=%s la salida y "
            "parallel.json deben nombrar el motivo (garantia de familia no "
            "acreditable); stderr=%r veredicto=%r"
            % (fault, (proc.stderr or "")[-1000:], verdict))


def _write_late_writer_helper(helper_path):
    """Ayudante que duerme y, si recibe destino, escribe (hijo de sonda)."""
    helper_path.write_text(
        "import sys\n"
        "import time\n"
        "from pathlib import Path\n"
        "\n"
        "\n"
        "def main():\n"
        "    delay = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0\n"
        "    time.sleep(delay)\n"
        "    if len(sys.argv) > 2:\n"
        "        Path(sys.argv[2]).write_text('late-032\\n', encoding='utf-8')\n"
        "\n"
        "\n"
        "main()\n",
        encoding="utf-8")
    return helper_path


def _write_late_probe(probe_path, helper_path, extra_args):
    """Sonda que lanza el ayudante sin esperarlo (hijo que sobrevive)."""
    probe_path.write_text(
        "import subprocess\n"
        "import sys\n"
        "\n"
        "\n"
        "%s\n"
        "    subprocess.Popen(\n"
        "        [sys.executable, %r] + %r,\n"
        "        stdin=subprocess.DEVNULL,\n"
        "        stdout=subprocess.DEVNULL,\n"
        "        stderr=subprocess.DEVNULL)\n"
        % (extra_args[0], str(helper_path), extra_args[1]),
        encoding="utf-8")
    return probe_path


def test_parallel_late_checkout_write_after_pytest_discards_run(tmp_path):
    """PC-10 (bloqueante 2 de review-final-product): sin este test, el canario
    final tomado ANTES de resolver la familia no veria a un hijo que escribe
    en build/ despues de la foto y termina dentro de la gracia, y el usuario
    adoptaria como intacto un checkout que cambio durante el lote."""
    probe_dir = tmp_path / "probe-late-write"
    probe_dir.mkdir(parents=True, exist_ok=True)
    helper_path = _write_late_writer_helper(
        probe_dir / "late_writer_032.py")
    late_name = ".late_write_%s" % _uuid_mod.uuid4().hex[:12]
    build_root = REPO_ROOT / "build"
    assert build_root.is_dir(), (
        "017-001 T7 RED (R2, PC-10): sin build/ no hay destino para la "
        "escritura tardia (entorno, no promesa)")
    late_path = build_root / late_name
    control_path = _write_late_probe(
        probe_dir / "test_probe_control_032.py", helper_path,
        ("def test_probe_control_passes_without_writing():", ["2"]))
    late_probe_path = _write_late_probe(
        probe_dir / "test_probe_late_032.py", helper_path,
        ("def test_probe_spawns_delayed_checkout_writer():",
         ["2", str(late_path)]))
    control_nodeids = tmp_path / "ev-late-control.nodeids"
    late_nodeids = tmp_path / "ev-late.nodeids"
    try:
        # Control: sin la escritura del hijo, la misma forma sale accepted.
        control_nodeids.write_text(
            "%s::test_probe_control_passes_without_writing\n" % control_path,
            encoding="utf-8")
        control_root = tmp_path / "ev-late-control"
        control_root.mkdir(parents=True, exist_ok=True)
        control_proc = _run(
            "parallel", "--workers", "1", "--evidence-root",
            str(control_root), "--nodeids", str(control_nodeids),
            timeout=TIMEOUT_S)
        assert control_proc.returncode == 0, (
            "017-001 T7 RED (R2, PC-10): el control sin escritura debe salir "
            "accepted (rc 0); rc=%d stderr=%r"
            % (control_proc.returncode, control_proc.stderr[-2000:]))
        control_verdict = _find_first_key(
            _parallel_json(control_root, "tardia-control"),
            "verdict", "decision", "disposition",
            "run_verdict", "batch_verdict", "outcome")
        assert isinstance(control_verdict, str) \
            and "accept" in control_verdict.lower(), (
            "017-001 T7 RED (R2, PC-10): el control sin escritura debe "
            "marcar veredicto de aceptacion; informa %r" % (control_verdict,))
        # Sonda: el hijo escribe ~2 s despues de pytest y termina en gracia.
        late_nodeids.write_text(
            "%s::test_probe_spawns_delayed_checkout_writer\n"
            % late_probe_path, encoding="utf-8")
        late_root = tmp_path / "ev-late"
        late_root.mkdir(parents=True, exist_ok=True)
        proc = _run(
            "parallel", "--workers", "1", "--evidence-root",
            str(late_root), "--nodeids", str(late_nodeids),
            timeout=TIMEOUT_S)
        assert proc.returncode != 0, (
            "017-001 T7 RED (R2, PC-10): el lote con escritura tardia en "
            "build/ (%s, ~2 s despues de pytest, dentro de la gracia) debe "
            "descartarse porque el canario final tiene que tomarse DESPUES "
            "de resolver la familia; hoy la foto se toma antes y sale "
            "accepted con rc=0" % late_name)
        data = _parallel_json(late_root, "tardia")
        verdict = _find_first_key(data, "verdict", "decision", "disposition",
                                  "run_verdict", "batch_verdict", "outcome")
        assert isinstance(verdict, str) and (
                "reject" in verdict.lower()
                or "discard" in verdict.lower()), (
            "017-001 T7 RED (R2, PC-10): parallel.json debe marcar la corrida "
            "con escritura tardia como rechazada/descartada conservando la "
            "evidencia; informa %r" % (verdict,))
        assert late_path.is_file(), (
            "017-001 T7 RED (R2, PC-10): el hijo debio escribir %s antes de "
            "terminar (entorno, no promesa)" % late_path)
    finally:
        try:
            late_path.unlink()
        except OSError:
            pass
        for path in (helper_path, control_path, late_probe_path,
                     control_nodeids, late_nodeids):
            try:
                path.unlink()
            except OSError:
                pass


def test_parallel_unreadable_sweep_area_discards_run_and_records_incomplete(
        tmp_path):
    """PC-10 (bloqueante 3 de review-final-product): sin este test, un barrido
    que no puede leer una zona del checkout sustituiria el error por el
    literal unreadable y omitiria el directorio en silencio, y el usuario
    leeria igualdad del canario donde hubo una zona no examinada."""
    import shutil as _shutil_mod
    assert os.geteuid() != 0, (
        "017-001 T7 RED (R3, PC-10): con euid 0 el modo 000 no bloquea la "
        "lectura y no hay zona ilegible que proponer (entorno, no promesa)")
    name = ".sweep_probe_%s" % _uuid_mod.uuid4().hex[:12]
    tmp_root = REPO_ROOT / ".cdad" / "tmp"
    assert tmp_root.is_dir(), (
        "017-001 T7 RED (R3, PC-10): sin .cdad/tmp no hay zona donde "
        "proponer el subdirectorio ilegible (entorno, no promesa)")
    probe = tmp_root / name
    probe.mkdir(parents=True, exist_ok=True)
    (probe / "inner.txt").write_text("sweep probe 032\n", encoding="utf-8")
    os.chmod(probe, 0o000)
    try:
        evidence_root = tmp_path / "ev-sweep"
        evidence_root.mkdir(parents=True, exist_ok=True)
        nodeids_file = _write_single_nodeids(tmp_path / "ev-sweep.nodeids")
        proc = _run("parallel", "--workers", "1", "--evidence-root",
                    str(evidence_root), "--nodeids", str(nodeids_file),
                    timeout=TIMEOUT_S)
        assert proc.returncode != 0, (
            "017-001 T7 RED (R3, PC-10): con %s ilegible (modo 000) el lote "
            "NO debe declararse accepted; hoy el error de lectura se "
            "sustituye por unreadable y el directorio se omite en silencio "
            "con rc=0" % name)
        data = _parallel_json(evidence_root, "barrido")
        verdict = _find_first_key(data, "verdict", "decision", "disposition",
                                  "run_verdict", "batch_verdict", "outcome")
        assert isinstance(verdict, str) \
            and "accept" not in verdict.lower(), (
            "017-001 T7 RED (R3, PC-10): con barrido incompleto "
            "parallel.json debe declarar el veredicto como no aceptado; "
            "informa %r" % (verdict,))
        entries = _find_incomplete_entries(data)
        assert entries, (
            "017-001 T7 RED (R3, PC-10): parallel.json debe registrar la "
            "incompletitud del barrido con un campo explicito; claves: %r"
            % sorted(map(str, data.keys())))
        blob = json.dumps(entries, ensure_ascii=False)
        assert name in blob, (
            "017-001 T7 RED (R3, PC-10): el campo de incompletitud debe "
            "nombrar la ruta no leida (%s); informa %r" % (name, entries))
    finally:
        try:
            os.chmod(probe, 0o755)
        except OSError:
            pass
        _shutil_mod.rmtree(probe, ignore_errors=True)


def _snapshot_worker_files(evidence_root):
    """{rel: bytes} de los artefactos por worker (primer intento)."""
    snapshot = {}
    for worker_dir in sorted(evidence_root.glob("worker-*")):
        if not worker_dir.is_dir():
            continue
        for path in sorted(worker_dir.rglob("*")):
            if not path.is_file():
                continue
            try:
                snapshot[str(path.relative_to(evidence_root))] = \
                    path.read_bytes()
            except OSError:
                continue
    return snapshot


def _newest_parallel_json(evidence_root, what):
    """parallel.json mas reciente bajo la raiz (intento propio reservado)."""
    candidates = sorted(evidence_root.rglob("parallel.json"))
    assert candidates, (
        "017-001 T7 RED (%s, PC-10): falta parallel.json en %s; "
        "el lote no dejo veredicto recuperable" % (what, evidence_root))

    def _key(path):
        try:
            return (path.stat().st_mtime_ns, str(path))
        except OSError:
            return (0, str(path))

    return max(candidates, key=_key)


def test_parallel_rejects_or_isolates_reused_evidence_root(tmp_path):
    """PC-10 con INV-1/INV-6 (bloqueante 4 de review-final-product): sin este
    test, una segunda invocacion sobre el directorio de evidencia ya poblado
    sobrescribiria con exist_ok=True y podria leer XML o perfiles del intento
    anterior, y el usuario atribuiria al intento nuevo mediciones viejas."""
    evidence_root = tmp_path / "ev-reuse"
    evidence_root.mkdir(parents=True, exist_ok=True)
    first_nodeids = _write_nodeids(tmp_path / "ev-reuse-first.nodeids")
    first = _run("parallel", "--workers", "2", "--evidence-root",
                 str(evidence_root), "--nodeids", str(first_nodeids),
                 timeout=TIMEOUT_S)
    assert first.returncode == 0, (
        "017-001 T7 RED (R4, PC-10): la primera corrida en evidencia limpia "
        "debe pasar; rc=%d stderr=%r"
        % (first.returncode, first.stderr[-2000:]))
    snapshot = _snapshot_worker_files(evidence_root)
    assert snapshot, (
        "017-001 T7 RED (R4, PC-10): la primera corrida debe conservar "
        "artefactos por worker (worker-*/...) para contrastar el reuso")
    second_nodeids = _write_single_nodeids(
        tmp_path / "ev-reuse-second.nodeids")
    second = _run("parallel", "--workers", "2", "--evidence-root",
                  str(evidence_root), "--nodeids", str(second_nodeids),
                  timeout=TIMEOUT_S)
    if second.returncode != 0:
        lowered = (second.stderr or "").lower()
        assert ("worker" in lowered or "evidence" in lowered
                or "evidencia" in lowered or "occup" in lowered
                or "ocupad" in lowered or "exist" in lowered
                or "previous" in lowered or "previo" in lowered
                or "attempt" in lowered or "intento" in lowered
                or str(evidence_root) in (second.stderr or "")), (
            "017-001 T7 RED (R4, PC-10): el rechazo del destino ocupado debe "
            "dar el motivo por stderr; rc=%d stderr=%r"
            % (second.returncode, (second.stderr or "")[-2000:]))
        return
    changed = []
    for rel, content in snapshot.items():
        try:
            now = (evidence_root / rel).read_bytes()
        except OSError:
            now = None
        if now != content:
            changed.append(rel)
    assert not changed, (
        "017-001 T7 RED (R4, PC-10): la segunda invocacion en el MISMO "
        "directorio ya poblado reutilizo los artefactos del intento anterior "
        "(sobrescritos o mezclados in situ en vez de rechazar el destino o "
        "reservar un intento propio); alterados: %r" % changed)
    newest = _newest_parallel_json(evidence_root, "reuso")
    data = json.loads(newest.read_text(encoding="utf-8"))
    consolidated = _find_first_key(
        data, "consolidated", "summary", "result", "totals")
    expected = _serial_triplet_for(
        SINGLE_NODEID, tmp_path, "ev-reuse-serial")
    assert isinstance(consolidated, dict), (
        "017-001 T7 RED (R4, PC-10): falta el resultado consolidado del "
        "segundo intento en %s" % newest)
    triplet = (consolidated.get("passed"), consolidated.get("failed"),
               consolidated.get("skipped"))
    assert triplet == expected, (
        "017-001 T7 RED (R4, PC-10): el segundo intento reporta %r pero su "
        "seleccion propia da %r: reutilizo resultados del primer intento "
        "(2 tests) en vez de los suyos (1 test)" % (triplet, expected))
    reported = set()
    for lst in _nodeid_lists(data):
        reported.update(lst)
    assert reported == set(SINGLE_NODEID), (
        "017-001 T7 RED (R4, PC-10): el segundo intento debe reportar solo "
        "sus nodeids %r; informa %r" % (SINGLE_NODEID, sorted(reported)))
