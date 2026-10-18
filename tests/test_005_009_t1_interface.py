#!/usr/bin/env python3
"""005-009 T1 RED — Interfaz común de delegación (PD-1, PD-2, PD-3, PD-8).

Contract: docs/specs/005-009-cli-delegation/spec.md (PD-1, PD-2, PD-3, PD-8;
INV-1..INV-3, INV-7) + plan.md T1 (skills/cdad-cycle/scripts/cdad_delegate.py
+ wrapper scripts/cdad_delegate.py + references/cli-delegation.md).

Superficie observable bajo prueba (proyecto sintético en tempdir, ninguna
lectura de implementación):

    python3 <cdad_delegate.py> --project-root <raíz> --packet <packet-id> \
        --destination <destino> --exec-config <config.json>

Superficie de CLI fijada por este contrato (detalle que fija el fichero de
tests aprobado; ningún flag interno): `--project-root`, `--packet <id>`
(paquete CANÓNICO ya publicado por `prepare`), `--destination <id>` (id del
adaptador), `--exec-config <config.json>` (configuración de ejecución:
runtime/modelo/binario/logs/tiempos) y `--role` NO en la invocación (el
rol/substage del registro salen del PAQUETE, PD-3). La salida es el esquema
del plan T1 `{attempt, session, termination, delivery_ref, diagnosis}` en
stdout (JSON único), como prepare publica el paquete.

DECISIÓN DE ORÁCULO (declarada en el módulo): no se lee ni inspecciona
implementación (skills/**). El fixture COPIA el ÁRBOL CANÓNICO COMPLETO de la
skill publicado (byte a byte con shutil.copytree de la raíz skills/cdad-cycle:
scripts + packets + references + assets + SKILL.md, SIN inspección, con la
paridad de nombres del árbol verificada por el propio fixture; el único
contenido leído es el hash del fichero de la interfaz para probar que «agregar
un destino no edita la interfaz») a un directorio de prueba en tempdir con la
MISMA TOPOLOGÍA del producto (la interfaz queda en <staged-root>/scripts/ y
todo lo demás junto a ella), de modo que un adaptador fiel al producto que
resuelve recursos co-ubicados a sí mismo funcione SIN ningún fallback al
checkout del coordinador (review-fix de T2: el staging de solo scripts/
escondería una resolución desde el cwd del coordinador, PD-3/PD-8). Junto a
esa copia se escriben los módulos del DESTINO DE PRUEBA por convención
(`cdad_delegate_testdest.py`, `cdad_delegate_beta.py`). El paquete canónico se
publica con el mecanismo real (`prepare`, fixture probado de 004-002 T2) sobre
un proyecto sintético. El barrido de portabilidad de los ficheros de producto
NUEVOS lo hace el reviewer (PD-8); aquí se ancla lo observable por
comportamiento: la configuración llega por `--exec-config`/flags, el registro
I8 refleja la configuración y lo no observado es `unknown`/null honesto, y la
ejecución no requiere ningún valor de este VPS.

El destino de prueba (`testdest`, fixture en el string TESTDEST_ADAPTER_SOURCE)
declara su comportamiento con cero de configuración: registra su transporte
(`testdest-calls.json`), copia los bytes recibidos (`testdest-sent-packet.md`),
escribe su texto final (`testdest-final-text.md`, sesión
`ses-testdest-fixture-0001`) y emite su envelope JSON por stdout; si no localiza
el paquete falla CERRADO (synmetrical a la spec: sin fallback, sin entrega).
Rotación de llamadas: la invocación esperada es como proceso (stdout envelope,
rc); si el interfaz la ejecuta in-process (runpy), el stub no contamina stdout
ni hace exit y persiste el envelope en `testdest-calls.json`.

Mapa test → postcondición:

  1  pd1_interface_resolves_adapter_by_id_and_returns_output_schema   PD-1
     (+ control negativo: destino sin adaptador → fallo cerrado con
      diagnóstico nombrado, sin entrega; + `beta`: agregar un destino NO
      edita la interfaz: hash de la copia intacto)
  2  pd2_packet_transport_byte_identical_single_ledger_state_untouched PD-2
  3  pd3_project_explicit_independent_of_cwd_i8_closed_shape_from_packet PD-3
  4  pd8_exec_config_portable_config_beats_product_no_host_values     PD-8

RED hoy: NO existe `cdad_delegate.py` en el producto (ni canónico ni
wrapper): cada unidad falla en su puerta común con AssertionError
(«interfaz ausente»), no por import/sintaxis.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (
    build_project,
    published_packets,
    read_state,
    run_cli,
    tree_snapshot,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
CANONICAL_DIR = SKILL_DIR / "scripts"
CANONICAL = CANONICAL_DIR / "cdad_delegate.py"
WRAPPER = REPO_ROOT / "scripts" / "cdad_delegate.py"

PACKET_BEGIN = "---cdad-packet-json"
TERMINATION_VOCABULARY = {
    "completed", "blocked", "transport-error", "timeout", "cancelled", "unknown",
}
OUTPUT_KEYS = {"attempt", "session", "termination", "delivery_ref", "diagnosis"}
# Forma cerrada del registro I8 (esquema aprobado; discovery §2.2).
I8_RECORD_KEYS = {
    "execution_id", "packet_id", "role", "substage", "runtime",
    "model_configured", "model_reported", "session", "started_at", "provenance",
}
I8_FIELDS = ("runtime", "model_configured", "model_reported", "session",
             "started_at")
HONEST_UNKNOWN_VALUE = {"unknown"}
FORBIDDEN_ACTIVE_STATUSES = {"completed", "failed"}

# Perfijos del árbol del proyecto que la invocación exitosa puede tocar
# (mismo ledger + entrega durable), PD-2: TODO lo demás es «otro state».
TOUCHED_ALLOWED_PREFIXES = (
    ".cdad/executions/",
    ".cdad/runtime/",
    ".cdad/results/",
    ".cdad/.lock",
)
STATE_FILE_REL = "docs/.cdad-state.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_files_by_dir(base: Path) -> set[str]:
    """Conjunto de rutas de archivo relativas a `base` (posix, sin
    __pycache__). Comparación de NOMBRES del árbol, sin inspección de
    contenido (mismo precedente que la copia sin inspección del fixture)."""
    result: set[str] = set()
    for item in sorted(base.rglob("*")):
        rel_path = item.relative_to(base)
        if "__pycache__" in rel_path.parts:
            continue
        if item.is_file():
            result.add(rel_path.as_posix())
    return result


def state_normalized(state: dict) -> dict:
    """Copia comparable: excluye last_updated y el status del paquete activo
    (transición del mecanismo reutilizado; idéntico oráculo de 004-002 T4)."""
    doc = copy.deepcopy(state)
    doc.pop("last_updated", None)
    active = doc.get("active_packet")
    if isinstance(active, dict):
        active.pop("status", None)
    return doc


def dispatch_dir(root: Path, eid: str) -> Path:
    return root / ".cdad" / "executions" / eid / "dispatches"


def dispatch_records(root: Path, eid: str) -> dict[str, Path]:
    base = dispatch_dir(root, eid)
    if not base.is_dir():
        return {}
    return {p.stem: p for p in sorted(base.glob("*.json"))}


# ------------------------------------------------------------- fixture stub


TESTDEST_ADAPTER_SOURCE = '''#!/usr/bin/env python3
"""Destino de prueba `testdest` por convención de módulo (fixture del test).

FIXTURE de tests/test_005_009_t1_interface.py — NO es producto: cero
configuración, zero red, no abre ningún CLI real ni ejecuta el binario
configurado. Comportamiento declarado (contrato del stub):

1. Registra cada invocación en `testdest-calls.json` (append): argv, cwd,
   claves de env con PACKET/CDAD/DELIVER, stdin visto, y el transporte
   localizado (sha256/bytes del paquete cuando lo ubica).
2. Copia los bytes del paquete recibido a `testdest-sent-packet.md` (el test
   los compara con el PACKET.md publicado: transporte byte-idéntico, PD-2).
3. Escribe su texto final en `testdest-final-text.md`.
4. Emite su envelope JSON por stdout:{"attempt", "session", "termination",
   "delivery_ref", "diagnosis"}; la invocación esperada es como proceso
   (stdout + rc). En ejecución in-process (runpy dentro de la interfaz) NO
   imprime ni hace exit (no contamina el stdout/rc de la interfaz): persiste
   el envelope en el log de llamadas.
5. Sin paquete localizado: falla CERRADO, sin inventar entrega (PD-4
   simétrico en la interfaz: sin fallback, diagnosóstico accionable).

La localización del transporte busca el paquete canónico (primera línea
`---cdad-packet-json`) en: ficheros pasados por argv, ficheros nombrados en
env con PACKET/CDAD/DELIVER, stdin. Nada outside su propio directorio.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_CALLS_PATH = HERE / "testdest-calls.json"
_SENT_PATH = HERE / "testdest-sent-packet.md"
_FINAL_PATH = HERE / "testdest-final-text.md"
_MARKER = "---cdad-packet-json"
_SESSION = "ses-testdest-fixture-0001"


def _packet_from_file(value: str):
    candidate = Path(value)
    if not candidate.is_file():
        return None
    try:
        data = candidate.read_bytes()
    except OSError:
        return None
    if data.lstrip().startswith(_MARKER.encode("utf-8")):
        return data, "argv-file"
    return None


packet = None
transport = None

for token in sys.argv[1:]:
    found = _packet_from_file(token)
    if found is not None:
        packet, transport = found
        break

if packet is None:
    listened_keys = sorted(
        key for key in os.environ
        if any(token in key.upper()
               for token in ("PACKET", "CDAD", "DELIVER"))
    )
    for key in listened_keys:
        found = _packet_from_file(os.environ[key])
        if found is not None:
            packet, transport = found
            break

stdin_seen = False
if packet is None:
    try:
        stdin_seen = not sys.stdin.isatty()
    except Exception:
        stdin_seen = False
    if stdin_seen:
        data = sys.stdin.read()
        if data.lstrip().startswith(_MARKER):
            packet, transport = data.encode("utf-8"), "stdin"
        else:
            transport = "stdin-sin-paquete"

entry = {
    "argv": list(sys.argv[1:]),
    "argv0": sys.argv[0] if sys.argv else "",
    "cwd": os.getcwd(),
    "env_keys": sorted(
        key for key in os.environ
        if any(token in key.upper()
               for token in ("PACKET", "CDAD", "DELIVER"))
    ),
    "stdin_seen": stdin_seen,
    "transport": transport,
    "packet": None,
    "envelope": None,
}
if packet is not None:
    entry["packet"] = {
        "sha256": hashlib.sha256(packet).hexdigest(),
        "bytes": len(packet),
        "begins_with_packet_mark": bool(
            packet.lstrip().startswith(_MARKER.encode("utf-8"))),
    }

if packet is None:
    envelope = {
        "attempt": None,
        "session": None,
        "termination": "blocked",
        "delivery_ref": None,
        "diagnosis": "testdest: sin paquete en el transporte (argv/env/stdin): "
                     "entrega posible, sin invento",
    }
else:
    _SENT_PATH.write_bytes(packet)
    _FINAL_PATH.write_text(
        "# Texto final del rol (destino testdest, fixture)\\n"
        "\\n"
        "Entrega final del worker de prueba: interfaz probada por "
        "tests/test_005_009_t1_interface.py.\\n",
        encoding="utf-8")
    envelope = {
        "attempt": None,
        "session": _SESSION,
        "termination": "completed",
        "delivery_ref": str(_FINAL_PATH),
        "diagnosis": None,
    }

entry["envelope"] = envelope

calls = []
if _CALLS_PATH.is_file():
    try:
        calls = json.loads(_CALLS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        calls = []
calls.append(entry)
_CALLS_PATH.write_text(
    json.dumps(calls, indent=2, sort_keys=True) + "\\n", encoding="utf-8")

is_direct = Path(sys.argv[0] or "").resolve().name == Path(__file__).name
if is_direct:
    sys.stdout.write(json.dumps(envelope) + "\\n")
    sys.stdout.flush()
    sys.exit(0 if packet is not None else 1)
'''


# --------------------------------------------------------------- helpers


class DelegateCase(unittest.TestCase):
    """Base: proyecto sintético con paquete publicado + staging de la
    interfaz y los destinos de prueba en tempdir."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-009-t1-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)
        self.prepare_ok()
        self.execution_id = read_state(self.root)["execution"]["id"]
        self.packet_id = read_state(self.root)["active_packet"]["id"]
        self.state_before_bytes = (
            self.root / STATE_FILE_REL).read_bytes()
        self.tree_before = tree_snapshot(self.root)

    # -- fixture -----------------------------------------------------------

    def prepare_ok(self, *extra: str) -> subprocess.CompletedProcess:
        proc = run_cli([
            "prepare", "--project-root", str(self.root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "encargo T1 005-009", *extra,
        ])
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): prepare publicó el paquete: "
                f"{proc.stdout + proc.stderr}")
        return proc

    def assert_interface_in_product(self) -> None:
        """Puerta común del RED: la interfaz debe existir en el producto
        (AssertionError, no import/sintaxis)."""
        self.assertTrue(
            CANONICAL.is_file(),
            msg="RED: no existe la interfaz común cdad_delegate.py en el "
                "producto (se espera "
                f"{CANONICAL.relative_to(REPO_ROOT)} por T1 del plan)")
        self.assertTrue(
            WRAPPER.is_file(),
            msg="RED: no existe el wrapper scripts/cdad_delegate.py en el "
                "producto")

    def staged_interface(self) -> tuple[Path, str]:
        """Fixture: copia byte a byte del ÁRBOL CANÓNICO COMPLETO de la
        skill (raíz skills/cdad-cycle: scripts + packets + references +
        assets + SKILL.md, en la misma topología del producto) a la zona de
        prueba + destinos de prueba por convención. Devuelve la ruta de la
        interfaz staged y el sha256 de la copia (para probar que agregar un
        destino NO edita la interfaz).

        Review-fix de T2 (subetapa red): el staging de SOLO
        skills/cdad-cycle/scripts dejaba el árbol co-ubicado incompleto y
        escondía que un adaptador puede verse forzado a resolver el resto
        del árbol desde otro lado (el cwd del coordinador, PD-3/PD-8). Con
        el árbol completo, un adaptador fiel al producto que resuelve todo
        co-ubicado a sí mismo funciona SIN ningún fallback al checkout del
        coordinador. La paridad de nombres del staging se verifica aquí
        (honestidad del fixture)."""
        self.assert_interface_in_product()
        stage_root = Path(self._tmp) / "iface" / "cdad-cycle"
        stage_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            SKILL_DIR, stage_root,
            ignore=shutil.ignore_patterns("__pycache__"))
        # Paridad del staging (precondición del fixture): la copia contiene
        # el mismo conjunto de archivos del canónico publicado (menos
        # __pycache__); nada quedó incompleto en el staging.
        expected_files = skill_files_by_dir(SKILL_DIR)
        staged_files = skill_files_by_dir(stage_root)
        self.assertEqual(
            staged_files, expected_files,
            msg="fixture: el staging del árbol de la skill no es la copia "
                "completa del canónico publicado (scripts + packets + "
                "references + assets + SKILL.md): dif "
                f"{sorted(staged_files ^ expected_files)[:8]}")
        scripts_dir = stage_root / "scripts"
        for name in ("cdad_delegate_testdest.py", "cdad_delegate_beta.py"):
            (scripts_dir / name).write_text(
                TESTDEST_ADAPTER_SOURCE, encoding="utf-8")
        staged = scripts_dir / "cdad_delegate.py"
        self.assertTrue(staged.is_file(), msg="fixture: copia de la interfaz")
        return staged, sha256_file(staged)

    def exec_config(self, name: str, *, runtime: str, model: str) -> Path:
        """Configuración de ejecución portátil: valores generados bajo el
        tempdir del test; ningún valor de este host ni modelo/proveedor
        concreto (PD-8/INV-7)."""
        base = Path(self._tmp)
        doc = {
            "runtime": runtime,
            "model": model,
            "binary": str(base / f"{name}-bin"),
            "logs_dir": str(base / name / "logs"),
            "wait": {"timeout_seconds": 30},
        }
        path = base / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def run_delegate(
            self, staged: Path, *, config: Path, destination: str,
            cwd: Path | None = None,
            project_root: Path | None = None) -> subprocess.CompletedProcess:
        root = project_root if project_root is not None else self.root
        return subprocess.run(
            [sys.executable, str(staged),
             "--project-root", str(root),
             "--packet", self.packet_id,
             "--destination", destination,
             "--exec-config", str(config)],
            capture_output=True, text=True,
            cwd=str(cwd) if cwd is not None else None, timeout=300)

    # -- aserciones --------------------------------------------------------

    def envelope(self, proc: subprocess.CompletedProcess,
                 label: str) -> dict:
        """Esquema de salida del plan T1: JSON único en stdout."""
        self.assertEqual(
            proc.returncode, 0,
            msg=f"{label}: la interfaz terminó con error: "
                f"{proc.stdout + proc.stderr}")
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.fail(
                msg=f"{label}: stdout no es el esquema de salida JSON: "
                    f"{proc.stdout[:400]!r}")
        self.assertIsInstance(
            out, dict,
            msg=f"{label}: el esquema de salida no es un objeto: {type(out)}")
        missing = OUTPUT_KEYS - set(out)
        self.assertEqual(
            missing, set(),
            msg=f"{label}: faltan claves del esquema de salida: {missing}")
        return out

    def assert_attempt_is_in_ledger(
            self, out: dict, before: dict[str, Path]) -> Path:
        """El intento declarado vive en el MISMO ledger I8."""
        attempt = out["attempt"]
        self.assertIsInstance(
            attempt, str, msg="la identidad de intento no es texto")
        self.assertTrue(
            attempt, msg="la identidad de intento está vacía")
        after = dispatch_records(self.root, self.execution_id)
        new = {
            stem: path for stem, path in after.items()
            if stem not in set(before) and not stem.startswith(".")
        }
        self.assertTrue(
            new, msg="la invocación no dejó registro en el ledger de "
                     "despachos (mismo ledger I8)")
        self.assertIn(
            attempt, set(new),
            msg=f"el intento declarado ({attempt!r}) no coincide con el "
                f"registro nuevo del ledger: {sorted(new)}")
        return new[attempt]

    def assert_state_untouched_beyond_dispatch_frontier(
            self, state_before: dict) -> None:
        """PD-2/INV-1: docs/.cdad-state.json sin cambios, salvo la transición
        del mecanismo reutilizado (prepared→dispatched); nunca
        completed/failed ni segundo paquete activo."""
        bytes_after = (self.root / STATE_FILE_REL).read_bytes()
        self.assertTrue(
            bytes_after.endswith(b"\n") or bytes_after.endswith(b"}"),
            msg="state terminado no es un documento JSON reconocible")
        state_after = json.loads(bytes_after.decode("utf-8"))
        self.assertIsNotNone(
            state_after.get("active_packet"),
            msg="la invocación dejó el state sin paquete activo")
        active_id = state_after["active_packet"].get("id")
        self.assertEqual(
            active_id, self.packet_id,
            msg="la invocación habilitó otro paquete activo (PD-2)")
        status = state_after["active_packet"].get("status")
        self.assertNotIn(
            status, FORBIDDEN_ACTIVE_STATUSES,
            msg=f"la interfaz cerró el gate por su cuenta "
                f"(status {status!r}; rc=0 no aprueba gate)")
        self.assertEqual(
            state_normalized(state_after),
            state_normalized(state_before),
            msg="la interfaz escribió en docs/.cdad-state.json más allá de la "
                "frontera del mecanismo reutilizado (PD-2/INV-1): campos "
                "distintos del status del paquete activo")

    def tree_changed(self) -> list[str]:
        before = self.tree_before
        after = tree_snapshot(self.root)
        return sorted(
            rel for rel in set(before) | set(after)
            if before.get(rel) != after.get(rel))

    @staticmethod
    def unexpected_touched(paths: list[str]) -> list[str]:
        return [
            rel for rel in paths
            if rel != STATE_FILE_REL
            and not any(
                rel.startswith(prefix) or rel == prefix
                for prefix in TOUCHED_ALLOWED_PREFIXES)
            and "__pycache__" not in rel
        ]


# ----------------------------------------------------------------- PD-1


class TestPd1CommonInterfaceAndAdapterResolution(DelegateCase):
    """PD-1: interfaz única agnóstica del destino; el adaptador se resuelve
    por id (convención de módulo); el esquema de salida declara entrega,
    identidad y terminación; agregar un destino no edita la interfaz."""

    def test_pd1_interface_resolves_adapter_by_id_and_returns_output_schema(
            self) -> None:
        """PD-1: invocada con proyecto/paquete/destino/configuración, con un
        destino de prueba devuelve el esquema de salida completo y el
        adaptador se resuelve por id; sin adapter para un id distinto falla
        cerrado con diagnóstico nombrado (control negativo); con otro id
        (`beta`, misma convención) también funciona sin editar la interfaz
        (hash de la copia intacto)."""
        self.assert_interface_in_product()
        staged, staged_sha = self.staged_interface()
        config = self.exec_config("cfg-a", runtime="opencode-clone",
                                  model="exec-config-model-a")
        records_before = dispatch_records(self.root, self.execution_id)

        # Positivo: destino de prueba resuelto por id (convención de módulo).
        proc = self.run_delegate(staged, config=config, destination="testdest")
        out = self.envelope(proc, "destino testdest")
        self.assertIn(
            out["termination"], TERMINATION_VOCABULARY,
            msg=f"terminación fuera del vocabulario aprobado: "
                f"{out['termination']!r}")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"terminación declarada: {out['termination']!r} (el destino "
                f"de prueba declaró entrega)")
        attempt = out["attempt"]
        self.assertIsInstance(attempt, str, msg="intento no es texto")
        self.assertTrue(attempt, msg="intento vacío")
        self.assertEqual(
            out["session"], "ses-testdest-fixture-0001",
            msg=f"la identidad de sesión no es la declarada por el destino: "
                f"{out['session']!r}")
        delivery_ref = out["delivery_ref"]
        self.assertIsInstance(
            delivery_ref, str, msg="delivery_ref no es texto")
        self.assertTrue(
            delivery_ref, msg="delivery_ref vacío: sin entrega declarada")
        if "/" in delivery_ref:
            self.assertTrue(
                Path(delivery_ref).is_file(),
                msg=f"delivery_ref no apunta a una entrega durable en disco: "
                    f"{delivery_ref!r}")
        self.assert_attempt_is_in_ledger(out, records_before)
        self.assertEqual(
            sha256_file(staged), staged_sha,
            msg="la interfaz se editó a sí misma al resolver el adaptador "
                "(agregar destinos no debe tocar la interfaz)")

        # Agregar un destino (beta, mismo stub por convención) NO edita la
        # interfaz: se resuelve igual por id, sin script por pareja.
        config_b = self.exec_config("cfg-b", runtime="opencode-clone",
                                    model="exec-config-model-b")
        proc_b = self.run_delegate(staged, config=config_b, destination="beta")
        out_b = self.envelope(proc_b, "destino beta")
        self.assertEqual(
            out_b["termination"], "completed",
            msg=f"el segundo destino no se resolvió por convención: "
                f"{out_b['termination']!r}")
        self.assertEqual(
            sha256_file(staged), staged_sha,
            msg="agregar el destino `beta` editó la interfaz (un adaptador "
                "por destino, INV-2)")

        # Control negativo: id sin adaptador → fallo cerrado, diagnóstico
        # nombrado, sin entrega (sin fallback a un genérico ni a otro id).
        config_n = self.exec_config("cfg-n", runtime="opencode-clone",
                                    model="exec-config-model-n")
        proc_n = self.run_delegate(staged, config=config_n,
                                   destination="destino-inexistente")
        output_n = proc_n.stdout + proc_n.stderr
        self.assertNotEqual(
            proc_n.returncode, 0,
            msg="un id de destino sin adaptador fue aceptado (sin fallo "
                "cerrado)")
        self.assertTrue(
            re.search(r"destino-inexistente|adapter|adaptador|destination",
                      output_n, re.IGNORECASE),
            msg=f"el diagnóstico no nombra el destino/adaptador faltante: "
                f"{output_n[:400]!r}")
        if proc_n.stdout.strip():
            try:
                out_n = json.loads(proc_n.stdout)
            except json.JSONDecodeError:
                out_n = None
            if out_n is not None:
                self.assertNotEqual(
                    out_n.get("termination"), "completed",
                    msg="un destino inexistente produjo terminación completed")


# ----------------------------------------------------------------- PD-2


class TestPd2ByteIdenticalTransportAndSingleLedger(DelegateCase):
    """PD-2: reutiliza el paquete y el mismo ledger I8; PACKET.md
    byte-idéntico; sin otro state ni otro paquete activo."""

    def test_pd2_packet_transport_byte_identical_single_ledger_state_untouched(
            self) -> None:
        """PD-2 (INV-1/INV-3): el paquete que llega al adaptador es el
        PACKET.md publicado, byte a byte; el registro vive en
        .cdad/executions/<id>/dispatches/<attempt>.json (mismo ledger); el
        state no cambia más allá de la transición del mecanismo reutilizado;
        sin ficheros de state nuevos ni segundo paquete; el paquete no se
        re-publica."""
        staged, _ = self.staged_interface()
        config = self.exec_config("cfg-pd2", runtime="opencode-clone",
                                  model="exec-config-model-pd2")
        records_before = dispatch_records(self.root, self.execution_id)
        packets_before = published_packets(self.root)
        self.assertIn(
            self.packet_id, packets_before,
            msg="precondición (fixture): paquete publicado")

        proc = self.run_delegate(staged, config=config, destination="testdest")
        out = self.envelope(proc, "PD-2 transporte")

        # Transporte byte-idéntico (el stub copió los bytes recibidos).
        sent = staged.parent / "testdest-sent-packet.md"
        self.assertTrue(
            sent.is_file(),
            msg="el destino de prueba no recibió ningún paquete (transporte "
                "ausente en el fixture stub)")
        published = packets_before[self.packet_id]
        self.assertEqual(
            sent.read_bytes(), published,
            msg="los bytes transportados al destino NO son los del PACKET.md "
                "publicado (PD-2)")
        calls = json.loads(
            (staged.parent / "testdest-calls.json").read_text("utf-8"))
        published_sha = hashlib.sha256(published).hexdigest()
        self.assertTrue(
            any(entry.get("packet", {}).get("sha256") == published_sha
                for entry in calls),
            msg="ninguna llamada del stub registró el sha256 del paquete "
                "transportado")

        # Mismo ledger I8: intento declarado ↔ fichero del ledger.
        record_path = self.assert_attempt_is_in_ledger(out, records_before)
        expected_prefix = (
            f".cdad/executions/{self.execution_id}/dispatches/")
        self.assertTrue(
            record_path.relative_to(self.root).as_posix()
            .startswith(expected_prefix),
            msg=f"el registro no vive en el ledger compartido "
                f"({expected_prefix}): {record_path}")

        # State: solo la frontera del mecanismo reutilizado.
        state_before = json.loads(self.state_before_bytes.decode("utf-8"))
        self.assert_state_untouched_beyond_dispatch_frontier(state_before)

        # Sin otro archivo de state ni re-publicación del paquete.
        changed = self.unexpected_touched(self.tree_changed())
        self.assertEqual(
            changed, [],
            msg=f"la invocación escribió fuera de {expected_prefix} y del "
                f"state controlado: {changed}")
        # Sin segundo paquete activo: nada se re-publicó y el paquete activo
        # sigue siendo el mismo (PD-2; el id lo fija el state normalizado).
        self.assertEqual(
            set(published_packets(self.root)), set(packets_before),
            msg="la invocación publicó o eliminó paquetes (segundo paquete "
                "activo prohibido, PD-2; igual que ningún fichero de state "
                "nuevo: los cambios del árbol ya están acotados arriba)")


# ----------------------------------------------------------------- PD-3


class TestPd3ExplicitProjectAndClosedI8Shape(DelegateCase):
    """PD-3: proyecto explícito e independiente del cwd del coordinador;
    registro I8 con forma cerrada e identidad del paquete; provenance
    campo→fuente."""

    def test_pd3_project_explicit_independent_of_cwd_i8_closed_shape(
            self) -> None:
        """PD-3: correr desde un cwd NO relacionado con el proyecto resuelve
        el paquete de ESE proyecto (--project-root); el intento queda en el
        ledger del proyecto con la forma cerrada, ejecución/paquete/rol/
        substage del paquete publicado y provenance que mapea cada campo a su
        fuente; el cwd ajeno no recibe registros del proyecto."""
        staged, _ = self.staged_interface()
        foreign = Path(tempfile.mkdtemp(prefix="cdad-005-009-t1-cwd-"))
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", str(foreign)], check=False))
        foreign_tree_before = {
            p.relative_to(foreign).as_posix(): p.read_bytes()
            for p in sorted(foreign.rglob("*")) if p.is_file()
        }
        config = self.exec_config("cfg-pd3", runtime="opencode-clone",
                                  model="exec-config-model-pd3")
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.run_delegate(staged, config=config, destination="testdest",
                                 cwd=foreign)
        out = self.envelope(proc, "PD-3 cwd ajeno")
        record = self.assert_attempt_is_in_ledger(out, records_before)

        # Forma cerrada del registro I8.
        data = json.loads(record.read_bytes().decode("utf-8"))
        self.assertEqual(
            set(data), I8_RECORD_KEYS,
            msg=f"la forma del registro I8 no es la cerrada aprobada: "
                f"{sorted(data)}")
        # Identidad DEL PAQUETE (nunca del documento de observación).
        self.assertEqual(
            data["execution_id"], self.execution_id,
            msg="execution_id del registro no es el del paquete")
        self.assertEqual(
            data["packet_id"], self.packet_id,
            msg="packet_id del registro no es el del paquete")
        request = json.loads(
            (self.root / ".cdad" / "packets" / self.packet_id
             / "REQUEST.json").read_text(encoding="utf-8"))
        self.assertEqual(
            data["role"], request["role"],
            msg=f"rol del registro no es el del paquete "
                f"({data['role']!r} != {request['role']!r})")
        self.assertEqual(
            data["substage"], request["substage"],
            msg=f"substage del registro no es el del paquete "
                f"({data['substage']!r} != {request['substage']!r})")
        # started_at presente; provenance mapea cada campo a su fuente.
        self.assertIsInstance(
            data["started_at"], str, msg="started_at no es texto")
        self.assertTrue(
            data["started_at"], msg="started_at vacío")
        provenance = data["provenance"]
        self.assertIsInstance(
            provenance, dict, msg="provenance no es un objeto campo→fuente")
        for field in I8_FIELDS:
            value = data.get(field)
            if value is None or value in HONEST_UNKNOWN_VALUE:
                continue
            self.assertIn(
                field, provenance,
                msg=f"provenance no mapea el campo observado {field!r}")
            self.assertIsInstance(
                provenance[field], str,
                msg=f"la fuente de {field!r} en provenance no es texto")
            self.assertTrue(
                str(provenance[field]).strip(),
                msg=f"la fuente de {field!r} en provenance está vacía")

        # Independencia del cwd: el cwd ajeno no ganó nada del proyecto.
        foreign_after = {
            p.relative_to(foreign).as_posix(): p.read_bytes()
            for p in sorted(foreign.rglob("*")) if p.is_file()
        }
        self.assertEqual(
            foreign_after, foreign_tree_before,
            msg="el cwd ajeno del coordinador recibió escrituras (el "
                "proyecto no es explícito/independiente, PD-3)")
        self.assertFalse(
            (foreign / ".cdad" / "executions").is_dir(),
            msg="el registro de despacho quedó en el cwd del coordinador en "
                "lugar del proyecto (--project-root)")


# ----------------------------------------------------------------- PD-8


class TestPd8PortableExecConfigNotVpsValues(DelegateCase):
    """PD-8: la configuración (modelo, runtime, binario, logs, tiempos) llega
    por configuración de ejecución/flags; lo no observado es honesto
    `unknown`; la ejecución no exige valores de este VPS."""

    def test_pd8_exec_config_portable_config_beats_product_no_host_values(
            self) -> None:
        """PD-8 (INV-7): el registro I8 refleja la configuración de
        ejecución pasada por `--exec-config` (dos configs distintas → dos
        registros distintos: la config de la ejecución gana sobre cualquier
        valor por defecto del producto); lo que el destino no reporta queda
        `unknown`/null honesto (sin invento); el registro no lleva rutas de
        host de este VPS.

        A-1 (006-003 U4/D3, reemplazo declarado): el `model` de la
        exec-config dejó de ser la fuente de `model_configured` — desde U4 la
        única fuente es la config de delegación (`delegation.json`, sin
        fallback). Esta corrida NO provisiona config de delegación para el
        destino `testdest`, así que el valor observado honesto es null; el
        oráculo que exigía `model_configured == model de la exec-config` se
        reemplaza por esa ausencia (el acoplamiento lo declara A-1)."""
        # El barrido de los ficheros de producto NUEVOS lo hace el reviewer
        # (PD-8); aquí el ancla es el comportamiento observable sobre el
        # registro I8 y la no-necesidad de valores del host.
        staged, _ = self.staged_interface()
        config_one = self.exec_config(
            "cfg-pd8-a", runtime="opencode-clone",
            model="exec-config-model-alpha")
        config_two = self.exec_config(
            "cfg-pd8-b", runtime="codex-clone",
            model="exec-config-model-beta")
        records_before = dispatch_records(self.root, self.execution_id)

        proc_one = self.run_delegate(staged, config=config_one,
                                     destination="testdest")
        out_one = self.envelope(proc_one, "PD-8 config A")
        record_one_path = self.assert_attempt_is_in_ledger(out_one,
                                                           records_before)
        record_one = json.loads(record_one_path.read_bytes().decode("utf-8"))
        self.assertEqual(
            record_one["runtime"], "opencode-clone",
            msg=f"runtime del registro no es el de la configuración de "
                f"ejecución: {record_one['runtime']!r}")
        # A-1 (006-003 U4/D3): sin config de delegación para el destino
        # `testdest`, `model_configured` es null honesto (dejó de reflejar el
        # `model` de la exec-config, que ya no es la fuente).
        self.assertIsNone(
            record_one["model_configured"],
            msg=f"model_configured refleja la exec-config pese a que U4/D3 la "
                f"retiró como fuente (sin delegación debe ser null): "
                f"{record_one['model_configured']!r}")

        # Segunda invocación con OTRA configuración: la config gana (no hay
        # valores fijos del producto).
        proc_two = self.run_delegate(staged, config=config_two,
                                     destination="testdest")
        out_two = self.envelope(proc_two, "PD-8 config B")
        record_two_path = self.assert_attempt_is_in_ledger(out_two,
                                                           records_before)
        record_two = json.loads(record_two_path.read_bytes().decode("utf-8"))
        self.assertNotEqual(
            record_two, record_one,
            msg="dos configuraciones de ejecución distintas produjeron el "
                "mismo registro: la configuración no llega al registro")
        # A-1 (006-003 U4/D3): la segunda config tampoco provisiona delegación,
        # así que `model_configured` es null honesto (la fuente es la config de
        # delegación, no la exec-config).
        self.assertIsNone(
            record_two["model_configured"],
            msg="model_configured de la segunda invocación refleja la "
                "exec-config pese a U4/D3 (sin delegación debe ser null): "
                f"{record_two['model_configured']!r}")
        self.assertEqual(
            record_two["runtime"], "codex-clone",
            msg="runtime de la segunda invocación no siguió su configuración")

        # config{ured}/observado/unknown: lo NO reportado por el destino es
        # honesto (null/unknown), nunca un valor por defecto del producto.
        self.assertIn(
            (record_one["model_reported"] or "unknown"),
            HONEST_UNKNOWN_VALUE | {"unknown"},
            msg=f"model_reported no es honesto (el destino de prueba no "
                f"reporta modelo): {record_one['model_reported']!r}")

        # Sin rutas de este host en los registros de ejecución (la
        # configuración es portátil: todo lo material llegó por --exec-config
        # con rutas del tempdir del test).
        for label, record in (("A", record_one), ("B", record_two)):
            self.assertNotIn(
                "/home/", json.dumps(record),
                msg=f"el registro de ejecución {label} lleva una ruta "
                    f"absoluta de host (PD-8/INV-7): "
                    f"{json.dumps(record)[:300]!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
