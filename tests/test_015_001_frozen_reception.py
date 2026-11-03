#!/usr/bin/env python3
"""RED 015-001-frozen-reception — recepción congelada (frozen reception).

Contract:
- docs/specs/015-001-frozen-reception/spec.md, aprobada (D1 y D2 aprobados
  expresamente; decisión §4 de test-audit.md).
- PC-01: prepare publica REQUEST con fuentes, snapshots y hashes coherentes;
  stdout coincide con PACKET.md publicado. Sucesor legítimo captura sus
  propias instrucciones vigentes.
- PC-02: tras preparar un paquete congelado, mutar las fuentes vivas no
  altera `render`; `validate-request` y `validate-packet` siguen aceptando.
- PC-03: con esa deriva, `prepare --record-dispatch` registra y permite la
  transición a `dispatched`; `receive` conserva `packet_validation=passed`
  y alcanza la recepción, sin `withdraw`.
- PC-04: alterar cuerpo/metadatos de PACKET.md respecto del request
  congelado impide registrar/recibir (incluye instrucciones alteradas con
  hashes de encabezado actualizados a lo alterado). Respaldo inválido
  también se rechaza sin recurrir a fuentes vivas.
- PC-05: request histórico sin el campo conserva comportamiento anterior;
  validarlo no añade snapshots ni modifica archivos.
- PC-06: repetir recepción acreditada conserva precedencia del replay
  durable y devuelve el mismo recibo aunque cambien instrucciones vivas;
  sin duplicar registros. La congelación no valida un contrato alterado
  ni una referencia contract cubierta por write_scope.

Oráculo caja negra: CLIs públicos sobre proyectos descartables y sobre una
DISTRIBUCIÓN descartable (copia temporal del checkout) cuando hay que mutar
fuentes vivas. Nunca se editan `skills/` ni `scripts/` del checkout real;
ningún módulo de producto se importa; ningún archivo de implementación se
lee. Las fuentes vivas se consultan en ejecución como el oráculo de
composición ya aprobado (`test_role_packet_render.py`, P1/P3), nunca como
lógica de producto.

Cobertura (un bloque por promesa observable A–D; cada test declara su
"sin este test"):

- Añ-A1 (A/PC-01): prepare congelado publica REQUEST con fuentes ordenadas,
  claves exactas, `sha256 == sha256(snapshot)`, snapshot idéntico a lo
  vivo, proyección del encabezado derivada del respaldo y
  stdout ≡ PACKET.md.
- Añ-A2 (A/PC-01): el sucesor legítimo (preparación posterior, con deriva
  de por medio) captura sus instrucciones vigentes, no las del predecesor.
- Añ-A2b (A/PC-01, cierre de F-2 de la review): el sucesor por reemplazo
  (`prepare --replace-packet`), con deriva de por medio, captura sus
  instrucciones vigentes, no los bytes congelados del predecesor (mata al
  mutante M6: sucesor que reutiliza bytes del predecesor).
- Añ-B1 ★ (B/PC-02, RED nuclear): tras preparar congelado, mutar las tres
  fuentes vivas deja `render` byte-idéntico y validate-request/packet rc=0.
  Hoy falla (el renderer lee fuentes vivas).
- Añ-B2 (B/PC-03): con esa deriva, `record-dispatch` registra
  (`dispatched`) y `receive` acredita con `packet_validation=passed`.
- Añ-C1 ★ (C/PC-04): clases de alteración rechazadas en record y receive,
  incluida la forja viva-consistente (instrucciones alteradas + encabezado
  actualizado + fuentes vivas mutadas a juego): el respaldo congelado la
  rechaza aunque el vivo coincida.
- Añ-C2 (C/PC-04): respaldo inválido (base64 roto, digest discordante,
  ruta faltante/duplicada/discordante, clave faltante) se rechaza con
  diagnóstico de la causa, idéntico con deriva y sin ella (sin consultar
  fuentes vivas).
- Añ-D1 (D/PC-05): el histórico sin el campo conserva validación estricta
  viva, sin snapshots y sin modificar archivos, conviviendo con un
  congelado válido que el validador sí acepta.
- Añ-D2 (D/PC-06): recepción acreditada repetida tras deriva devuelve el
  mismo recibo (replay durable, cero registros nuevos); contrato alterado
  y referencia cubierta por write_scope siguen rechazados.

Estado al RED: A1, A2, B1, B2, C1, C2 y D1 fallan por comportamiento
(AssertionError sobre la promesa pendiente, jamás ImportError/traceback);
D2 es guarda verde hoy (el replay tras deriva ya funciona porque `receive`
no re-deriva instrucciones vivas; el test clava la durabilidad del replay
para que la congelación no la rompa, más los controles de contrato
alterado y referencia cubierta). Controles verdes incluidos prueban que
el montaje no rechaza ni acepta todo.

RED (paquete): corre solo este archivo, en primer plano:
    env -u TMPDIR python3 -m pytest -q tests/test_015_001_frozen_reception.py < /dev/null
Suite completa no realizada (momento «durante el ciclo»: regresión
proporcional = este archivo; límites: sin suite completa, sin e2e
instalado, sin propiedades con semilla — pertenecen a sus subfases).
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from test_007_002_dispatch_recovery import (
    CLI_TIMEOUT_S,
    REPO_ROOT,
    _RecoveryProject,
)
from test_008_004_packet_enforcement import (
    TEST_BYTES as COVERED_TEST_BYTES,
    TEST_REL as COVERED_TEST_REL,
    _begin as continuity_begin,
    _sha as sha_hex,
    _write as write_rel,
)

PACKET_BEGIN_B = b"---cdad-packet-json\n"
PACKET_END_B = b"\n---end-cdad-packet-json\n"
STATIC_START_B = b"<!-- cdad-instructions:start -->\n"
STATIC_END_B = b"\n<!-- cdad-instructions:end -->"

PACKETS_DIR = Path("skills") / "cdad-cycle" / "packets"
CANONICAL_SOURCES = (
    "common.md",
    "roles/test-writer.md",
    "substages/test-writer-red.md",
)
DRIFT_MARKER_B = (
    b"\n# 015-001 deriva simulada: fuente viva mutada en distribucion descartable\n"
)

ROLE, SUBSTAGE = "test-writer", "red"


# ------------------------------------------------------------------ helpers


def _dist_packet(dist: Path) -> Path:
    return dist / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"


def _dist_result(dist: Path) -> Path:
    return dist / "skills" / "cdad-cycle" / "scripts" / "cdad_result.py"


def _run(script: Path, args: list[str], home: Path, cwd: Path) -> subprocess.CompletedProcess[str]:
    """CLI caja negra con HOME aislado (nunca el real) y stdin nulo."""
    assert script.is_file(), f"precondición (fixture): CLI ausente: {script}"
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        stdin=subprocess.DEVNULL,
        timeout=CLI_TIMEOUT_S,
    )


def _make_distribution(base: Path) -> Path:
    """Copia descartable del checkout para mutar fuentes vivas sin tocar el real."""
    dist = base / "dist"
    assert not dist.exists(), f"precondición (fixture): dist limpio en {dist}"
    shutil.copytree(
        REPO_ROOT,
        dist,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            ".git", ".cdad", ".pytest_cache", "__pycache__", "build",
            ".ruff_cache", "*.pyc", "*.pyo",
        ),
    )
    return dist


def _live_bytes(root: Path, rel: str) -> bytes:
    return (root / PACKETS_DIR / rel).read_bytes()


def _drift_common(dist: Path) -> tuple[bytes, bytes, str]:
    """Muta common.md SOLO en la distribución descartable."""
    target = dist / PACKETS_DIR / "common.md"
    old = _live_bytes(REPO_ROOT, "common.md")
    assert target.read_bytes() == old, (
        "precondición (fixture): la copia parte del vivo idéntico al checkout")
    new = old + DRIFT_MARKER_B
    target.write_bytes(new)
    return old, new, hashlib.sha256(new).hexdigest()


def _repo_packet() -> Path:
    return REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"


def _packet_paths(fx: _RecoveryProject):
    packet_dir = fx.packet_dir()
    return packet_dir / "REQUEST.json", packet_dir / "PACKET.md"


def _split_packet(raw: bytes) -> tuple[dict, bytes]:
    assert raw.startswith(PACKET_BEGIN_B), (
        "precondición (fixture): PACKET.md publicado con marcador de apertura")
    rest = raw[len(PACKET_BEGIN_B):]
    idx = rest.find(PACKET_END_B)
    assert idx != -1, (
        "precondición (fixture): PACKET.md publicado con marcador de cierre")
    return json.loads(rest[:idx].decode("utf-8")), rest[idx + len(PACKET_END_B):]


def _render_args(fx: _RecoveryProject, request: Path) -> list[str]:
    return [
        "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--request", str(request),
    ]


def _packet_text_of(packet_md: Path) -> str:
    return packet_md.read_text(encoding="utf-8")


def _active_id(fx: _RecoveryProject) -> str:
    active = fx.read_state().get("active_packet") or {}
    assert active.get("id"), "precondición (fixture): hay paquete activo"
    return active["id"]


def _frozen_candidate(historic: dict, live: dict[str, bytes]) -> dict:
    """REQUEST histórico + respaldo congelado bien formado (a mano)."""
    cand = copy.deepcopy(historic)
    cand["instruction_sources"] = [
        {
            "path": path,
            "sha256": hashlib.sha256(live[path]).hexdigest(),
            "snapshot": base64.b64encode(live[path]).decode("ascii"),
        }
        for path in CANONICAL_SOURCES
    ]
    return cand


def _assert_rechazo_limpio(proc: subprocess.CompletedProcess[str], label: str) -> str:
    text = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        f"{label}: debe rechazarse (rc≠0); got rc={proc.returncode} "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
    assert "Traceback" not in text, (
        f"{label}: el rechazo es diagnóstico, no un traceback: {text[:400]!r}")
    assert proc.stdout == "", (
        f"{label}: el rechazo deja stdout vacío; got {proc.stdout[:200]!r}")
    return text


# ------------------------------------------------------------------ A (PC-01)


class TestA1FrozenPublication(unittest.TestCase):
    def test_an_a1_prepare_congelado_publica_respaldo_coherente(self) -> None:
        """Añ-A1 (A/PC-01): el prepare congelado publica REQUEST con fuentes
        ordenadas, claves exactas, `sha256 == sha256(snapshot)`, snapshot
        idéntico a lo vivo, proyección del encabezado derivada del respaldo
        y stdout ≡ PACKET.md.

        Sin este test, el usuario recibiría un paquete cuya recepción no
        puede anclarse a bytes congelados: cualquier deriva posterior de
        las fuentes vivas rompería el render y el despacho.
        """
        import tempfile

        from test_packet_prepare import PrepareProject, run_prepare
        from test_role_packets import PACKET_CLI

        base = Path(tempfile.mkdtemp(prefix="cdad-015-a1-"))
        self.addCleanup(shutil.rmtree, base, True)
        project = PrepareProject(base / "proj")

        result = run_prepare(PACKET_CLI, *project.args())
        assert result.returncode == 0, (
            "precondición (comportamiento existente): el prepare publica "
            "(rc=0): " + result.stderr.decode(errors="replace"))
        packet_dir = project.out_dir / project.packet_id()
        packet_bytes = (packet_dir / "PACKET.md").read_bytes()

        # Control verde: la publicación existente ya cumple stdout ≡ PACKET.md.
        assert result.stdout == packet_bytes, (
            "A/PC-01 (control): stdout del prepare coincide con PACKET.md")

        request = json.loads((packet_dir / "REQUEST.json").read_text(
            encoding="utf-8"))
        assert "instruction_sources" in request, (
            "A/PC-01 violada: el prepare congelado publica "
            "`instruction_sources` en REQUEST.json; claves vistas: "
            f"{sorted(request)}")
        sources = request["instruction_sources"]
        assert [entry["path"] for entry in sources] == list(CANONICAL_SOURCES), (
            "A/PC-01 violada: fuentes canónicas ordenadas "
            f"(common, rol, subfase); visto {[e.get('path') for e in sources]}")
        live = {path: _live_bytes(REPO_ROOT, path) for path in CANONICAL_SOURCES}
        for entry in sources:
            assert set(entry) == {"path", "sha256", "snapshot"}, (
                "A/PC-01 violada: cada entrada lleva exactamente "
                f"path/sha256/snapshot; visto {sorted(entry)}")
            snapshot = base64.b64decode(entry["snapshot"])
            assert snapshot == live[entry["path"]], (
                f"A/PC-01 violada: el snapshot de {entry['path']} es el "
                "vivo byte a byte")
            assert entry["sha256"] == hashlib.sha256(snapshot).hexdigest(), (
                f"A/PC-01 violada: sha256 == sha256(snapshot) para "
                f"{entry['path']}")

        metadata, _ = _split_packet(packet_bytes)
        assert metadata.get("instruction_sources") == [
            {"path": path, "sha256": hashlib.sha256(live[path]).hexdigest()}
            for path in CANONICAL_SOURCES
        ], "A/PC-01 violada: el encabezado proyecta path+sha256 del respaldo"


class TestA2SuccessorCapturesCurrent(unittest.TestCase):
    def test_an_a2_sucesor_legitimo_captura_instrucciones_vigentes(self) -> None:
        """Añ-A2 (A/PC-01): la preparación posterior (sucesor legítimo), con
        deriva de por medio, captura sus instrucciones vigentes, no las del
        predecesor.

        Sin este test, un sucesor podría reutilizar los bytes congelados
        del predecesor y el usuario ejecutaría instrucciones ya
        sustituidas sin que ningún recibo lo revele.
        """
        import tempfile

        from test_packet_prepare import PrepareProject, run_prepare
        from test_role_packets import PACKET_CLI

        base = Path(tempfile.mkdtemp(prefix="cdad-015-a2-"))
        self.addCleanup(shutil.rmtree, base, True)
        project = PrepareProject(base / "proj")

        first = run_prepare(
            PACKET_CLI, *project.args(objective="015-001 A2 predecesor"))
        assert first.returncode == 0, (
            "precondición (comportamiento existente): el predecesor se "
            "publica (rc=0): " + first.stderr.decode(errors="replace"))

        dist = _make_distribution(base)
        _drift_common(dist)
        dist_live = {path: _live_bytes(dist, path)
                     for path in CANONICAL_SOURCES}
        second = run_prepare(
            _dist_packet(dist),
            *project.args(objective="015-001 A2 sucesor"), cwd=dist)
        assert second.returncode == 0, (
            "precondición (comportamiento existente): el sucesor se publica "
            "(rc=0): " + second.stderr.decode(errors="replace"))
        request = json.loads(
            (project.out_dir / project.packet_id(2) / "REQUEST.json")
            .read_text(encoding="utf-8"))
        assert "instruction_sources" in request, (
            "A/PC-01 (sucesor) violada: la preparación posterior publica "
            "`instruction_sources`; claves vistas: "
            f"{sorted(request)}")
        by_path = {entry["path"]: entry
                   for entry in request["instruction_sources"]}
        assert set(by_path) == set(CANONICAL_SOURCES), (
            "A/PC-01 (sucesor) violada: el respaldo trae las tres fuentes "
            f"canónicas; visto {sorted(by_path)}")
        snapshot = base64.b64decode(by_path["common.md"]["snapshot"])
        assert snapshot == dist_live["common.md"], (
            "A/PC-01 (sucesor) violada: el sucesor captura lo vigente "
            "(deriva incluida), no lo del predecesor")
        assert snapshot != _live_bytes(REPO_ROOT, "common.md"), (
            "A/PC-01 (sucesor) violada: el snapshot no es el de la "
            "publicación anterior")


def _entry_by_path(request: dict, path: str) -> dict:
    """Entrada del respaldo congelado para `path` (precondición del fixture)."""
    for entry in request.get("instruction_sources", []):
        if entry.get("path") == path:
            return entry
    raise AssertionError(
        "precondición (fixture): el request trae respaldo congelado para "
        f"{path!r}; visto "
        f"{[e.get('path') for e in request.get('instruction_sources', [])]}")


def _assert_sucesor_captura_vigente(entry: dict, vivo: bytes,
                                    predecesor_snapshot: bytes,
                                    label: str) -> None:
    """Oráculo A2b (A/PC-01, F-2): el sucesor por reemplazo captura lo vivo
    derivado, no los bytes congelados del predecesor."""
    assert set(entry) == {"path", "sha256", "snapshot"}, (
        f"{label} violada: la entrada del sucesor lleva exactamente "
        f"path/sha256/snapshot; visto {sorted(entry)}")
    snapshot = base64.b64decode(entry["snapshot"])
    assert snapshot != predecesor_snapshot, (
        f"{label} violada: el sucesor por reemplazo reutiliza los bytes "
        "congelados del predecesor (mutante M6)")
    assert snapshot == vivo, (
        f"{label} violada: el sucesor por reemplazo no captura sus "
        "instrucciones vigentes (la deriva de por medio no quedó congelada)")
    assert entry["sha256"] == hashlib.sha256(snapshot).hexdigest(), (
        f"{label} violada: sha256 == sha256(snapshot) para el sucesor")


class TestA2bReplaceSuccessorCapturesCurrent(unittest.TestCase):
    def test_an_a2b_replace_packet_sucesor_captura_vigente_no_predecesor(self) -> None:
        """Añ-A2b (A/PC-01, F-2 de la review): el sucesor por reemplazo
        (`prepare --replace-packet`), con deriva de por medio, captura sus
        instrucciones vigentes, no los bytes congelados del predecesor.

        Sin este test, un sucesor por reemplazo podría reutilizar los bytes
        congelados del predecesor (mutante M6 de la review: sobrevive
        143 passed) y el usuario ejecutaría instrucciones ya sustituidas sin
        que ningún recibo lo revele.
        """
        import tempfile

        from test_007_002_dispatch_recovery import SPEC_REL as _SPEC_REL

        base = Path(tempfile.mkdtemp(prefix="cdad-015-a2b-"))
        self.addCleanup(shutil.rmtree, base, True)
        fx = _RecoveryProject(base / "fx")
        predecessor = json.loads(
            (fx.packet_dir() / "REQUEST.json").read_text(encoding="utf-8"))
        predecessor_common = _entry_by_path(predecessor, "common.md")
        predecessor_snapshot = base64.b64decode(
            predecessor_common["snapshot"])
        assert predecessor_snapshot == _live_bytes(REPO_ROOT, "common.md"), (
            "precondición (comportamiento existente): el predecesor congela "
            "lo vivo byte a byte")

        # Control: sin obsolescencia verificable el reemplazo se rechaza
        # (PD-8); el test ejerce la vía real de reemplazo, no un prepare más.
        intact = _run(_repo_packet(),
                      ["prepare", "--project-root", str(fx.root),
                       "--replace-packet", fx.packet_id,
                       "--reason", "015-001 A2b control sin obsolescencia"],
                      fx.home, REPO_ROOT)
        assert intact.returncode != 0, (
            "precondición (control): sin obsolescencia, `--replace-packet` "
            "se rechaza (rc≠0); "
            f"got rc={intact.returncode}: {intact.stdout!r} "
            f"{intact.stderr!r}")
        assert "Traceback" not in (intact.stdout + intact.stderr), (
            "precondición (control): el rechazo no es un traceback")

        dist = _make_distribution(base)
        _, new_common, _ = _drift_common(dist)

        # Obsolescencia autorizada del fixture (patrón `outdate_contract`
        # con reauthorize=True de
        # tests/test_005_001_t2_replace_packet.py): el contrato del proyecto
        # deriva y su pin de aprobación se re-pinea a lo actual.
        spec = fx.root / _SPEC_REL
        spec.write_bytes(
            spec.read_bytes() + b"\n# 015-001 A2b: contrato obsoleto\n")
        re_sha = hashlib.sha256(spec.read_bytes()).hexdigest()
        state = fx.read_state()
        pins = [entry for entry in state.get("stage_history", [])
                if entry.get("contract_path") == _SPEC_REL]
        assert pins, (
            "precondición (fixture): el proyecto trae pin de especificación")
        for pin in pins:
            pin["contract_sha256"] = re_sha
        (fx.root / "docs" / ".cdad-state.json").write_text(
            json.dumps(state), encoding="utf-8")

        replaced = _run(
            _dist_packet(dist),
            ["prepare", "--project-root", str(fx.root),
             "--replace-packet", fx.packet_id,
             "--reason", "015-001 A2b: sucesor tras deriva"],
            fx.home, dist)
        assert replaced.returncode == 0, (
            "A/PC-01 (sucesor por reemplazo) violada: con obsolescencia, "
            "`prepare --replace-packet` publica el sucesor (rc=0); "
            f"got rc={replaced.returncode}: {replaced.stdout!r} "
            f"{replaced.stderr!r}")
        successor_id = (fx.read_state().get("active_packet") or {}).get("id")
        assert successor_id and successor_id != fx.packet_id, (
            "A/PC-01 (sucesor por reemplazo) violada: el reemplazo publica "
            f"un paquete NUEVO activo; visto {successor_id!r}")
        successor = json.loads(
            (fx.packet_dir(successor_id) / "REQUEST.json")
            .read_text(encoding="utf-8"))
        assert "instruction_sources" in successor, (
            "A/PC-01 (sucesor por reemplazo) violada: el sucesor publica "
            f"`instruction_sources`; claves vistas: {sorted(successor)}")
        _assert_sucesor_captura_vigente(
            _entry_by_path(successor, "common.md"), new_common,
            predecessor_snapshot, "A/PC-01 (sucesor por reemplazo)")

        # Sensibilidad contra el mutante M6 (review F-2): el sucesor que
        # reutiliza los bytes congelados del predecesor —la salida observable
        # exacta del mutante— es rechazado por el oráculo A2b, con la falla
        # pertinente observada y atribuida.
        m6 = copy.deepcopy(successor)
        for entry in m6["instruction_sources"]:
            if entry.get("path") == "common.md":
                entry["snapshot"] = predecessor_common["snapshot"]
                entry["sha256"] = predecessor_common["sha256"]
        with self.assertRaises(AssertionError) as caught:
            _assert_sucesor_captura_vigente(
                _entry_by_path(m6, "common.md"), new_common,
                predecessor_snapshot, "A/PC-01 (sucesor por reemplazo)")
        assert "predecesor" in str(caught.exception), (
            "sensibilidad M6: la falla pertinente nombra la reutilización "
            f"del predecesor; visto {str(caught.exception)[:300]!r}")


# ------------------------------------------------------------------ B (PC-02/PC-03)

class TestB1RenderStableUnderDrift(unittest.TestCase):
    def test_an_b1_render_byte_identico_tras_mutar_fuentes_vivas(self) -> None:
        """Añ-B1 ★ (B/PC-02, RED nuclear): tras preparar congelado, mutar las
        fuentes vivas no altera `render`; `validate-request` y
        `validate-packet` siguen aceptando.

        Sin este test, cambiar una coma en las instrucciones vivas impediría
        registrar el despacho de un paquete ya publicado, y el usuario
        perdería el encargo aunque nada de su contrato haya cambiado.
        """
        import tempfile
        base = Path(tempfile.mkdtemp(prefix="cdad-015-b1-"))
        self.addCleanup(shutil.rmtree, base, True)
        fx = _RecoveryProject(base / "fx")
        request_path, packet_md = _packet_paths(fx)
        published = packet_md.read_bytes()

        dist = _make_distribution(base)
        _drift_common(dist)

        rendered = _run(_dist_packet(dist),
                        ["render", *_render_args(fx, request_path)],
                        fx.home, dist)
        assert rendered.returncode == 0, (
            "B/PC-02: `render` emite el paquete (rc=0) aunque las fuentes "
            f"vivas hayan derivado; rc={rendered.returncode}: "
            f"{rendered.stdout!r} {rendered.stderr!r}")
        assert "Traceback" not in (rendered.stdout + rendered.stderr), (
            "B/PC-02: el render tras deriva no es un traceback")
        assert rendered.stdout.encode("utf-8") == published, (
            "B/PC-02 violada: con fuentes vivas mutadas, el render del "
            "paquete congelado deja de ser byte-idéntico al publicado "
            f"(deriva viva rompe render: {len(rendered.stdout)} vs "
            f"{len(published)} bytes)")

        valid_request = _run(_dist_packet(dist),
                             ["validate-request", *_render_args(fx, request_path)],
                             fx.home, dist)
        assert valid_request.returncode == 0, (
            "B/PC-02 violada: `validate-request` sigue aceptando tras la "
            f"deriva; rc={valid_request.returncode}: "
            f"{valid_request.stdout!r} {valid_request.stderr!r}")
        valid_packet = _run(
            _dist_packet(dist),
            ["validate-packet", *_render_args(fx, request_path),
             "--packet", str(packet_md)],
            fx.home, dist,
        )
        assert valid_packet.returncode == 0, (
            "B/PC-02 violada: `validate-packet` sigue aceptando tras la "
            f"deriva; rc={valid_packet.returncode}: "
            f"{valid_packet.stdout!r} {valid_packet.stderr!r}")


class TestB2DispatchReceiveUnderDrift(unittest.TestCase):
    def test_an_b2_record_y_receive_acreditan_con_deriva(self) -> None:
        """Añ-B2 (B/PC-03): con deriva viva, `prepare --record-dispatch`
        registra y lleva a `dispatched`; `receive` conserva
        `packet_validation=passed` y alcanza la recepción, sin `withdraw`.

        Sin este test, una deriva inocua de instrucciones condannaría un
        despacho válido al retiro: el usuario vería su encargo en
        `withdraw` por una causa ajena a su contrato.
        """
        import tempfile
        base = Path(tempfile.mkdtemp(prefix="cdad-015-b2-"))
        self.addCleanup(shutil.rmtree, base, True)
        fx = _RecoveryProject(base / "fx")
        request_path, packet_md = _packet_paths(fx)

        dist = _make_distribution(base)
        _drift_common(dist)

        recorded = _run(
            _dist_packet(dist),
            ["prepare", "--project-root", str(fx.root),
             "--record-dispatch", fx.packet_id,
             "--attempt-id", "attempt-015-001-b2-001",
             "--input", str(fx._observation)],
            fx.home, dist,
        )
        assert recorded.returncode == 0, (
            "B/PC-03 violada: con deriva viva, `prepare --record-dispatch` "
            "registra el paquete congelado (rc=0); "
            f"rc={recorded.returncode}: {recorded.stdout!r} "
            f"{recorded.stderr!r}")
        assert "Traceback" not in (recorded.stdout + recorded.stderr), (
            "B/PC-03: el registro tras deriva no es un traceback")
        assert (fx.read_state().get("active_packet") or {}).get("status") == "dispatched", (
            "B/PC-03 violada: el registro permite la transición a "
            "`dispatched`")
        assert len(fx.dispatch_files()) == 1, (
            "B/PC-03 violada: el registro publica el despacho sin retirarlo "
            f"(sin withdraw); despachos: {fx.dispatch_files()}")

        descriptor = fx._stage_result()
        received = _run(
            _dist_result(dist),
            ["receive", "--project-root", str(fx.root),
             "--execution-context", str(fx.execution_context_path()),
             "--packet", str(packet_md), "--request", str(request_path),
             "--descriptor", str(descriptor)],
            fx.home, dist,
        )
        assert received.returncode == 0, (
            "B/PC-03 violada: con deriva viva, `receive` acredita la "
            f"entrega (rc=0); rc={received.returncode}: "
            f"{received.stdout!r} {received.stderr!r}")
        try:
            receipt = json.loads(received.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                "B/PC-03 violada: stdout de `receive` no es el recibo JSON: "
                f"{received.stdout[:200]!r}") from exc
        assert receipt.get("packet_validation") == "passed", (
            "B/PC-03 violada: el recibo conserva "
            f"`packet_validation=passed`; visto {receipt.get('packet_validation')!r}")
        assert fx.receipt_path().is_file(), (
            "B/PC-03 violada: la recepción publica el recibo durable")


# ------------------------------------------------------------------ C (PC-04)


def _forge_packet_with(fx: _RecoveryProject, old_common: bytes,
                        new_common: bytes, new_sha: str) -> None:
    """Aplica la forja viva-consistente ya calculada al PACKET.md de `fx`.

    Altera una línea de instrucciones en PACKET.md, actualiza el hash del
    encabezado a lo alterado. Quien llama aporta la deriva (`old/new/sha`)
    ya aplicada a la distribución descartable; así varios proyectos pueden
    forjarse contra la misma deriva sin re-derivar (la re-deriva fallaría
    la precondición «la copia parte del vivo idéntico»).
    Solo el respaldo congelado puede distinguirla del paquete legítimo."""
    _, packet_md = _packet_paths(fx)
    raw = packet_md.read_bytes()
    metadata, body = _split_packet(raw)
    pre, rest = body.split(STATIC_START_B, 1)
    static_head, static_tail = rest.split(STATIC_END_B, 1)
    assert static_head.count(old_common) == 1, (
        "precondición (fixture): common.md aparece una vez en el bloque vivo")
    forged_static = static_head.replace(old_common, new_common)
    forged_body = pre + STATIC_START_B + forged_static + STATIC_END_B + static_tail
    entries = metadata.get("instruction_sources")
    if isinstance(entries, list) and any(
            entry.get("path") == "common.md" for entry in entries):
        for entry in entries:
            if entry.get("path") == "common.md":
                entry["sha256"] = new_sha
    else:
        # Request histórico sin respaldo: el encabezado proyecta los hashes
        # vivos (vía `instruction_sources` del render). La forja actualiza
        # esa proyección a lo alterado para ser viva-consistente.
        metadata["instruction_sources"] = [
            {"path": path,
             "sha256": (new_sha if path == "common.md"
                        else hashlib.sha256(_live_bytes(REPO_ROOT, path)).hexdigest())}
            for path in CANONICAL_SOURCES
        ]
    forged_head = (
        PACKET_BEGIN_B
        + json.dumps(metadata, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
        + PACKET_END_B
    )
    packet_md.write_bytes(forged_head + forged_body)


def _historic_request(vigente: dict) -> dict:
    """Request histórico real sin respaldo: el vigente sin `instruction_sources`.

    El vigente ya trae respaldo (prepare congelado); el histórico es el mismo
    request sin ese campo, como los publicados antes del cambio (D2)."""
    hist = copy.deepcopy(vigente)
    hist.pop("instruction_sources", None)
    return hist


class TestC1AlterationsRejected(unittest.TestCase):
    def test_an_c1_alteraciones_rechazadas_en_record_y_receive(self) -> None:
        """Añ-C1 ★ (C/PC-04): clases de alteración rechazadas en record y
        receive — objetivo alterado, línea de instrucciones alterada, y la
        forja viva-consistente (instrucciones alteradas + encabezado
        actualizado a lo alterado + fuentes vivas mutadas a juego).

        Sin este test, un encabezado maquillado para que coincida con unas
        instrucciones alteradas pasaría el registro y el usuario despacharía
        una encomienda distinta de la validada sin que ningún recibo lo
        revele.
        """
        import tempfile
        base = Path(tempfile.mkdtemp(prefix="cdad-015-c1-"))
        self.addCleanup(shutil.rmtree, base, True)

        # Control verde (008-004 PC-03): el objetivo alterado no se registra.
        fx_control = _RecoveryProject(base / "control")
        _, packet_control = _packet_paths(fx_control)
        request_control = json.loads(
            (fx_control.packet_dir() / "REQUEST.json").read_text(encoding="utf-8"))
        objective = request_control["objective"]
        text = _packet_text_of(packet_control)
        assert text.count(objective) == 1, (
            "precondición (fixture): el objetivo aparece una vez en PACKET.md")
        packet_control.write_text(
            text.replace(objective, objective + " (alterado en disco)"),
            encoding="utf-8")
        rejected = fx_control.dispatch()
        assert rejected.returncode != 0, (
            "C/PC-04 (control): el objetivo alterado no se registra "
            f"(rc≠0); got rc={rejected.returncode}")

        # Forja viva-consistente: debe rechazarse en record…
        # Con requests congelados la forja ya no es «viva-consistente rc=0»
        # contra el congelado (el snapshot la rechaza). Se demuestra en dos
        # pasos: contra un histórico sin respaldo lo vivo la acepta, y contra
        # el congelado el snapshot la rechaza. La deriva se aplica una vez y
        # se reutiliza para ambos proyectos (re-derivar fallaría la
        # precondición de copia limpia).
        fx_record = _RecoveryProject(base / "record")
        dist = _make_distribution(base)
        old_common = _live_bytes(REPO_ROOT, "common.md")
        new_common = old_common + DRIFT_MARKER_B
        new_sha = hashlib.sha256(new_common).hexdigest()
        assert (dist / PACKETS_DIR / "common.md").read_bytes() == old_common, (
            "precondición (fixture): la copia parte del vivo idéntico al checkout")
        (dist / PACKETS_DIR / "common.md").write_bytes(new_common)
        _forge_packet_with(fx_record, old_common, new_common, new_sha)
        _, forged_md = _packet_paths(fx_record)
        frozen_request_path = fx_record.packet_dir() / "REQUEST.json"
        historic_data = _historic_request(json.loads(
            frozen_request_path.read_text(encoding="utf-8")))
        historic_path = base / "record-historico-REQUEST.json"
        historic_path.write_text(
            json.dumps(historic_data, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")), encoding="utf-8")
        check_live = _run(
            _dist_packet(dist),
            ["validate-packet", *_render_args(fx_record, historic_path),
             "--packet", str(forged_md)],
            fx_record.home, dist,
        )
        assert check_live.returncode == 0, (
            "precondición (forja): la forja es viva-consistente contra el "
            "histórico sin respaldo en la distribución (validate-packet "
            "rc=0); "
            f"got rc={check_live.returncode}: {check_live.stdout!r} "
            f"{check_live.stderr!r}")
        check_frozen = _run(
            _dist_packet(dist),
            ["validate-packet", *_render_args(
                fx_record, frozen_request_path),
             "--packet", str(forged_md)],
            fx_record.home, dist,
        )
        assert check_frozen.returncode != 0, (
            "C/PC-04: el respaldo congelado rechaza la forja aunque el vivo "
            "coincida (el snapshot distingue lo forjado); "
            f"got rc=0 stdout={check_frozen.stdout!r}")
        assert "Traceback" not in (check_frozen.stdout + check_frozen.stderr), (
            "C/PC-04: el rechazo del snapshot no es un traceback")
        forged_record = _run(
            _dist_packet(dist),
            ["prepare", "--project-root", str(fx_record.root),
             "--record-dispatch", fx_record.packet_id,
             "--attempt-id", "attempt-015-001-c1-001",
             "--input", str(fx_record._observation)],
            fx_record.home, dist,
        )
        assert forged_record.returncode != 0, (
            "C/PC-04 violada: la forja viva-consistente (instrucciones "
            "alteradas + encabezado maquillado + vivas a juego) NO se "
            "registra como despacho; got rc=0 "
            f"stdout={forged_record.stdout!r}")
        assert "Traceback" not in (forged_record.stdout + forged_record.stderr), (
            "C/PC-04: el rechazo de la forja no es un traceback")

        # …y en receive tras un despacho válido.
        # Reutiliza la misma deriva (sin re-derivar la distribución).
        fx_receive = _RecoveryProject(base / "receive")
        dispatched = fx_receive.dispatch()
        assert dispatched.returncode == 0, (
            "precondición (fixture): el despacho intacto se registra "
            f"(rc=0): {dispatched.stdout!r} {dispatched.stderr!r}")
        _forge_packet_with(fx_receive, old_common, new_common, new_sha)
        descriptor = fx_receive._stage_result()
        _, forged_receive_md = _packet_paths(fx_receive)
        forged_receive = _run(
            _dist_result(dist),
            ["receive", "--project-root", str(fx_receive.root),
             "--execution-context",
             str(fx_receive.execution_context_path()),
             "--packet", str(forged_receive_md),
             "--request",
             str(fx_receive.packet_dir() / "REQUEST.json"),
             "--descriptor", str(descriptor)],
            fx_receive.home, dist,
        )
        assert forged_receive.returncode != 0, (
            "C/PC-04 violada: la forja viva-consistente NO se recibe; "
            f"got rc=0 stdout={forged_receive.stdout!r}")
        assert not fx_receive.receipt_path().exists(), (
            "C/PC-04 violada: la forja publicó recibo durable")


class TestC2InvalidBackupRejected(unittest.TestCase):
    def test_an_c2_respaldo_invalido_rechazado_sin_fuentes_vivas(self) -> None:
        """Añ-C2 (C/PC-04): respaldo inválido — snapshot con base64 roto,
        digest discordante, ruta faltante/duplicada/discordante y entrada
        sin snapshot — se rechaza con diagnóstico de la causa, idéntico con
        deriva y sin ella (sin consultar fuentes vivas).

        Sin este test, un respaldo corrupto o manipulado podría aceptarse
        según el estado de las fuentes vivas del momento, y el usuario no
        sabría si su paquete está anclado o a la deriva.
        """
        import tempfile
        base = Path(tempfile.mkdtemp(prefix="cdad-015-c2-"))
        self.addCleanup(shutil.rmtree, base, True)
        fx = _RecoveryProject(base / "fx")
        request_path, _ = _packet_paths(fx)
        vigente = json.loads(request_path.read_text(encoding="utf-8"))
        historic = _historic_request(vigente)
        assert "instruction_sources" not in historic, (
            "precondición (fixture): el histórico deriva del vigente sin respaldo")
        live = {path: _live_bytes(REPO_ROOT, path) for path in CANONICAL_SOURCES}

        def mutate(label: str, cand: dict) -> dict:
            entries = cand["instruction_sources"]
            if label == "base64-roto":
                entries[0]["snapshot"] = "!!!no-es-base64!!!"
            elif label == "digest-discordante":
                entries[1]["sha256"] = "0" * 64
            elif label == "ruta-faltante":
                cand["instruction_sources"] = [entries[0], entries[2]]
            elif label == "ruta-duplicada":
                cand["instruction_sources"] = [entries[0], entries[1],
                                               entries[2], dict(entries[0])]
            elif label == "ruta-discordante":
                entries[2]["path"] = "roles/inexistente.md"
            elif label == "clave-faltante":
                del entries[0]["snapshot"]
            else:  # pragma: no cover
                raise AssertionError(f"clase desconocida: {label}")
            return cand

        keywords = {
            "base64-roto": ("base64", "snapshot"),
            "digest-discordante": ("digest", "sha256"),
            "ruta-faltante": ("faltante", "missing"),
            "ruta-duplicada": ("duplicad",),
            "ruta-discordante": ("discord",),
            "clave-faltante": ("snapshot",),
        }
        dist = _make_distribution(base)
        _drift_common(dist)

        problems: list[str] = []
        for label in keywords:
            candidate = mutate(label, _frozen_candidate(historic, live))
            cand_path = base / f"candidato-{label}.json"
            cand_path.write_text(
                json.dumps(candidate, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")),
                encoding="utf-8",
            )
            intact = _run(_repo_packet(),
                          ["validate-request", *_render_args(fx, cand_path)],
                          fx.home, REPO_ROOT)
            drifted = _run(_dist_packet(dist),
                           ["validate-request", *_render_args(fx, cand_path)],
                           fx.home, dist)
            try:
                assert intact.returncode != 0, (
                    f"[{label}]: respaldo inválido se rechaza (rc≠0)")
                assert drifted.returncode != 0, (
                    f"[{label}]: con deriva también se rechaza (rc≠0)")
                for proc, where in ((intact, "intacto"), (drifted, "deriva")):
                    text = proc.stdout + proc.stderr
                    assert "Traceback" not in text, (
                        f"[{label}/{where}]: diagnóstico, no traceback")
                    assert proc.stdout == "", (
                        f"[{label}/{where}]: stdout vacío en el rechazo")
                assert intact.stderr == drifted.stderr, (
                    f"[{label}]: el diagnóstico no consulta fuentes vivas "
                    "(idéntico con deriva y sin ella)")
                lowered = intact.stderr.lower()
                assert any(key in lowered for key in keywords[label]), (
                    f"[{label}]: el diagnóstico nombra la causa "
                    f"({keywords[label]}); visto {intact.stderr[:300]!r}")
            except AssertionError as exc:
                problems.append(str(exc))
        assert not problems, (
            "C/PC-04 violada: respaldos inválidos aceptados o sin "
            "diagnóstico de causa:\n" + "\n".join(problems))


# ------------------------------------------------------------------ D (PC-05/PC-06)


class TestD1HistoricPreserved(unittest.TestCase):
    def test_an_d1_historico_sin_campo_conserva_validacion_estricta(self) -> None:
        """Añ-D1 (D/PC-05): el request histórico sin el campo conserva la
        validación estricta viva, sin snapshots y sin modificar archivos,
        conviviendo con un congelado válido que el validador sí acepta.

        Sin este test, introducir la congelación podría reescribir o
        invalidar silenciosamente los paquetes históricos, y el usuario
        perdería la recepción de encargos publicados antes del cambio.
        """
        import tempfile
        base = Path(tempfile.mkdtemp(prefix="cdad-015-d1-"))
        self.addCleanup(shutil.rmtree, base, True)
        fx = _RecoveryProject(base / "fx")
        request_path, packet_md = _packet_paths(fx)
        vigente = json.loads(request_path.read_text(encoding="utf-8"))
        historic = _historic_request(vigente)
        assert "instruction_sources" not in historic, (
            "precondición (fixture): el histórico deriva del vigente sin respaldo")
        historic_path = base / "historico-REQUEST.json"
        historic_path.write_text(
            json.dumps(historic, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")), encoding="utf-8")

        before = {rel: data for rel, data in fx.tree().items()}
        ok = _run(_repo_packet(),
                  ["validate-request", *_render_args(fx, historic_path)],
                  fx.home, REPO_ROOT)
        assert ok.returncode == 0, (
            "D/PC-05 (control): el histórico valida con las vivas intactas "
            f"(rc=0); got rc={ok.returncode}: {ok.stdout!r} {ok.stderr!r}")
        assert fx.tree() == before, (
            "D/PC-05 (control): validar el histórico no añade snapshots ni "
            "modifica archivos")

        live = {path: _live_bytes(REPO_ROOT, path) for path in CANONICAL_SOURCES}
        cand_path = base / "congelado-candidato.json"
        cand_path.write_text(
            json.dumps(_frozen_candidate(historic, live), ensure_ascii=False,
                       sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        frozen_ok = _run(
            _repo_packet(),
            ["validate-request", *_render_args(fx, cand_path)],
            fx.home, REPO_ROOT)
        assert frozen_ok.returncode == 0, (
            "D/PC-05 violada: el validador acepta el congelado bien formado "
            "que convive con el histórico; "
            f"got rc={frozen_ok.returncode}: {frozen_ok.stdout!r} "
            f"{frozen_ok.stderr!r}")
        frozen_render = _run(
            _repo_packet(),
            ["render", *_render_args(fx, cand_path)], fx.home, REPO_ROOT)
        assert frozen_render.returncode == 0, (
            "D/PC-05 violada: el congelado bien formado rinde (rc=0)")
        assert frozen_render.stdout.encode("utf-8") == packet_md.read_bytes(), (
            "D/PC-05 violada: con snapshots idénticos a lo vivo, el render "
            "del congelado coincide con el histórico publicado")

        dist = _make_distribution(base)
        _drift_common(dist)
        # El histórico sin respaldo conserva validación estricta viva: con
        # deriva, su render (desde fuentes vivas) ya no coincide con el
        # PACKET.md publicado, y `validate-packet` lo rechaza. `validate-request`
        # solo acredita coherencia interna del request, así que la deriva se
        # observa en la comparación contra el paquete publicado.
        historic_drifted = _run(_dist_packet(dist),
                                ["validate-packet",
                                 *_render_args(fx, historic_path),
                                 "--packet", str(packet_md)],
                                fx.home, dist)
        assert historic_drifted.returncode != 0, (
            "D/PC-05 (control): el histórico conserva validación estricta "
            "viva — con deriva se rechaza (rc≠0)")
        frozen_drifted = _run(_dist_packet(dist),
                              ["validate-request",
                               *_render_args(fx, cand_path)],
                              fx.home, dist)
        assert frozen_drifted.returncode == 0, (
            "D/PC-05 violada: el congelado sigue aceptándose tras la "
            f"deriva; got rc={frozen_drifted.returncode}: "
            f"{frozen_drifted.stdout!r} {frozen_drifted.stderr!r}")


class TestD2ReplayDurable(unittest.TestCase):
    def test_an_d2_recepcion_repetida_tras_deriva_es_replay(self) -> None:
        """Añ-D2 (D/PC-06): la recepción acreditada repetida tras deriva
        devuelve el mismo recibo (replay durable, cero registros nuevos);
        el contrato alterado y la referencia contract cubierta por
        write_scope siguen rechazados.

        Guarda verde hoy: `receive` no re-deriva instrucciones vivas, así
        que el replay tras deriva ya funciona; el test clava esa
        durabilidad para que la congelación no la rompa.
        Sin este test, un reintento del orquestador tras una deriva inocua
        podría duplicar recibos o perder la entrega sin que nadie lo
        note, y el usuario no sabría cuál es el recibo válido de su
        encargo.
        """
        import tempfile
        base = Path(tempfile.mkdtemp(prefix="cdad-015-d2-"))
        self.addCleanup(shutil.rmtree, base, True)
        fx = _RecoveryProject(base / "fx")
        request_path, packet_md = _packet_paths(fx)
        dispatched = fx.dispatch()
        assert dispatched.returncode == 0, (
            "precondición (fixture): el despacho se registra (rc=0): "
            f"{dispatched.stdout!r} {dispatched.stderr!r}")
        first = fx.receive()
        assert first.returncode == 0, (
            "precondición (fixture): la primera recepción se acredita "
            f"(rc=0): {first.stdout!r} {first.stderr!r}")
        receipt_before = fx.receipt_path().read_bytes()
        first_receipt = json.loads(first.stdout)
        assert first_receipt.get("packet_validation") == "passed", (
            "precondición (fixture): la primera recepción trae "
            "`packet_validation=passed`")
        dispatches_before = fx.dispatch_files()
        assert len(dispatches_before) == 1, (
            "precondición (fixture): un único registro de despacho")

        dist = _make_distribution(base)
        _drift_common(dist)
        descriptor = fx._stage_result()
        replay = _run(
            _dist_result(dist),
            ["receive", "--project-root", str(fx.root),
             "--execution-context", str(fx.execution_context_path()),
             "--packet", str(packet_md), "--request", str(request_path),
             "--descriptor", str(descriptor)],
            fx.home, dist,
        )
        assert replay.returncode == 0, (
            "D/PC-06 violada: repetir la recepción acreditada tras deriva "
            "es replay (rc=0); "
            f"got rc={replay.returncode}: {replay.stdout!r} "
            f"{replay.stderr!r}")
        assert "Traceback" not in (replay.stdout + replay.stderr), (
            "D/PC-06: el replay tras deriva no es un traceback")
        try:
            replay_receipt = json.loads(replay.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                "D/PC-06 violada: el replay devuelve el recibo JSON: "
                f"{replay.stdout[:200]!r}") from exc
        assert replay_receipt.get("packet_validation") == "passed", (
            "D/PC-06 violada: el replay conserva `packet_validation=passed`")
        assert fx.receipt_path().read_bytes() == receipt_before, (
            "D/PC-06 violada: el recibo durable no cambia en la repetición")
        assert fx.dispatch_files() == dispatches_before, (
            "D/PC-06 violada: el replay no publica registros nuevos")

        # Controles verdes: la congelación no valida lo indebido.
        from test_007_002_dispatch_recovery import SPEC_REL as _SPEC_REL
        fx_bad = _RecoveryProject(base / "mala")
        spec_path = fx_bad.root / _SPEC_REL
        spec_before = spec_path.read_bytes()
        dispatched_bad = fx_bad.dispatch()
        assert dispatched_bad.returncode == 0, (
            "precondición (fixture): el despacho con contrato vigente se "
            "registra (rc=0)")
        # La recepción con el contrato alterado en disco se rechaza.
        spec_path.write_bytes(spec_before + b"\n# contrato alterado 015-001-D2\n")
        bad_receive = fx_bad.receive()
        assert bad_receive.returncode != 0, (
            "D/PC-06 (control): con el contrato alterado, `receive` se "
            f"rechaza (rc≠0); got rc={bad_receive.returncode}")
        assert not fx_bad.receipt_path().exists(), (
            "D/PC-06 (control): el contrato alterado no publica recibo")

        fx_covered = _RecoveryProject(base / "cubierta")
        write_rel(fx_covered.root, COVERED_TEST_REL, COVERED_TEST_BYTES)
        covered = continuity_begin(
            fx_covered,
            [{"path": COVERED_TEST_REL, "class": "contract",
              "sha256": sha_hex(COVERED_TEST_BYTES)}],
        )
        assert covered.returncode != 0, (
            "D/PC-06 (control): la referencia contract cubierta por "
            f"write_scope se rechaza (rc≠0); got rc={covered.returncode}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
