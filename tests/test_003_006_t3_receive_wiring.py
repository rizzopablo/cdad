#!/usr/bin/env python3
"""003-006 T3 RED — `receive` + continuidad en el cuerpo del orquestador
(P1 mitad orquestador, P7, P8, P9) y corrección F1 de `SKILL.md`.

Contract:
- docs/specs/003-006-runtime-adoption/spec.md:
    §2.1 cableado del ciclo; §2.3 `receive` en el flujo (staging del FINAL
    TEXT bajo `.cdad/inbox` con `RESULT.json`, ejecución de `receive`,
    validación del receipt, transición ÚNICA de state; `receive` NO aprueba —
    `semantic_status` = `pending`, el state lo escribe solo el orquestador,
    I5); §2.4 continuidad en el ciclo.
    P1 (mitad orquestador): el cuerpo del orquestador (`sources/roles/
    orchestrator.md` y sus agentes regenerados) nombra `receive`, `begin`,
    `checkpoint`, `reconcile` y `resume` en el paso correspondiente, SIN
    duplicar las interfaces.
    P7: la salida FINAL TEXT de un rol se stagea y se recibe (rc=0); un
    retry idéntico converge al mismo receipt byte a byte; una única
    transición de state.
    P8: con `receive` en el flujo, `cdad_continuity reconcile` clasifica
    `received` (deja de ser `dispatched-unknown`).
    P9: `begin` (write-ahead antes de despachar), `checkpoint` (límite de
    tarea) y `resume` (sesión nueva) se usan en el ciclo.
- docs/specs/003-006-runtime-adoption/plan.md (T3; test focal declarado
  `tests/test_003_006_t3_receive_wiring.py`; Neck: "regenerar los agentes
  (OpenCode + Claude Code) desde `sources/`"; Excluidos: cambios a
  `cdad_result.py`/`cdad_continuity.py` — se reutilizan — y el recorrido
  real de T4).
- docs/specs/003-006-runtime-adoption/review-t1-decision.md (F1: el
  paréntesis de `SKILL.md:278` debe remitir `receive` a
  `references/re-entry.md` y a `cdad_result.py`, NO a `continuity.md`;
  "El RED de T3 lo cubre con una aserción").

Superficie observable:
- (a)"Los cuerpos operativos" (documentación observable, no plumbing):
  `sources/roles/orchestrator.md`, `agents/cdad-orchestrator.md`,
  `agents/claude-code/cdad-orchestrator.md` — los tres deben nombrar los
  comandos en su paso del ciclo, sin copiar flags.
- (b) Coherencia: el agente regenerado refleja la fuente (los tres archivos
  concuerdan en los pasajes de cableado).
- (c) F1 en `skills/cdad-cycle/SKILL.md` (El SISTEMA ASUME SKILL.md, pero
  su contenido es superficie observable de la feature 002 y de T1; T3 solo
  toca la frase que nombra `receive` en Step 6).
- (d) P7/P8 SIN runtime: paquete DESPACHADO + dispatch registrado + receipts
  producidos por los CLIs REALES (`scripts/cdad_packet.py` via
  `prepare --record-dispatch` de 001, `scripts/cdad_result.py` de 002,
  `scripts/cdad_continuity.py` de 004) sobre un proyecto sintético en un
  tmpdir. Los CLIs se consumen EXECUTÁNDOSE (fixture + `--help` antes de
  escribir este test); su CÓDIGO NO se leyó (aislamiento de fase).

RED honesto (probes observables, 2026-10-08):
- (a)/(b)/(c): los cuerpos operativos hoy NO nombran el cableado
  receive+continuidad y la frase Step 6 de SKILL.md remite `receive` a
  `continuity.md` (F1) ⇒ AssertionError sobre comportamiento ausente/presente.
- (d) P7 y P8 YA PASAN con los CLIs reales (003-002/003-004 verdes) ⇒ se
  DECLARAN GUARDS honestos (el orquestador pidió declararlos si ya pasan).
Todos los fallos son AssertionError (nunca ImportError ni sintaxis).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]

# (a)+(b): cuerpos operativos del orquestador (fuente + agentes regenerados)
ORCH_REL = "sources/roles/orchestrator.md"
AGENT_RELS = (
    ORCH_REL,
    "agents/cdad-orchestrator.md",
    "agents/claude-code/cdad-orchestrator.md",
)
DOC_PATHS = {rel: REPO_ROOT / rel for rel in AGENT_RELS}

# (c): SKILL.md (superficie F1 de review-t1-decision)
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"

# CLIs REALES (se ejecutan; su código no se lee)
RESULT_SCRIPT = REPO_ROOT / "scripts" / "cdad_result.py"
CONTINUITY_SCRIPT = REPO_ROOT / "scripts" / "cdad_continuity.py"

CLI_TIMEOUT_S = 120

STATE_REL = "docs/.cdad-state.json"

# Flags que NO deben copiarse como interfaz (§2.1 "sin duplicar las
# interfaces"): SOLO las de los CLIs que T3 introduce en el cuerpo del
# orquestador (cdad_result.py + cdad_continuity.py; decisión del
# orquestador sobre la nota NO_DUP_FLAGS del RED-004). Las flags de
# cdad_packet.py (--record-dispatch etc.) y las transversales
# (--project-root) quedan FUERA: su invocación documentada ya está
# cableada y es contenido legítimo preexistente. Guardia: debe pasar hoy
# o fallar solo si se copian flags de esos dos CLIs.
NO_DUP_FLAGS = [
    "--execution-context",   # cdad_result + cdad_continuity
    "--packet",              # cdad_result receive + reconcile
    "--attempt",             # continuidad (nombres de attempt en AC)
    "--body",                # continuidad (cuerpos del store D11)
]

# ---------------------------------------------------------------- helpers


def skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


HEADING_RE = re.compile(r"^#{1,6}\s")

# Banner FIJO del generador de agentes (decisión del orquestador sobre el
# defecto de coherencia): cada agente regenerado agrega frontmatter (entre
# los --- iniciales) y una frase de introducción del cuerpo. Esas unidades
# NO son cableado del rol y la coherencia debe comparar solo pasajes de
# cableado — si no, nunca puede pasar editando solo la fuente.
BANNER_PHRASE = re.compile(r"start\s*/\s*resume\s*/\s*advance", re.IGNORECASE)


def strip_frontmatter(text: str) -> str:
    """Quita el frontmatter inicial (entre los primeros --- de YAML), que
    el generador de agentes agrega como banner fijo (no es cableado)."""
    if text.startswith("---"):
        m = re.match(r"^---[ \t]*\n.*?\n---[ \t]*\n?", text, re.DOTALL)
        if m:
            return text[m.end():]
    return text


def strip_banner_units(text: str) -> str:
    """Quita las unidades que son SOLO el banner fijo del generador
    (frase de introducción 'start/resume/advance ...'). Exclusión mínima:
    cualquier otra unidad permanece intacta."""
    kept = []
    for para in re.split(r"(\n\s*\n)", text):
        if not BANNER_PHRASE.search(para):
            kept.append(para)
    return "".join(kept)


def doc_text(rel: str) -> str:
    """Texto del cuerpo operativo (sin frontmatter ni banner del
    generador de agentes)."""
    return strip_banner_units(strip_frontmatter(
        DOC_PATHS[rel].read_text(encoding="utf-8")))


def units(text: str) -> list[str]:
    """Unidades de redacción tolerantes: líneas sin '#' de encabezado +
    párrafos (líneas no vacías unidas). Un cableado puede quedar partido
    por el wrap de Markdown; se matchea a nivel línea O párrafo."""
    line_units = []
    for raw in text.splitlines():
        if raw.startswith("#"):
            raw = raw.lstrip("#").strip()
        stripped = raw.strip()
        if stripped:
            line_units.append(stripped)
    paragraphs = []
    for para in re.split(r"\n\s*\n", text):
        joined = " ".join(
            ln.strip().lstrip("# ").lstrip("- ").lstrip("* ")
            for ln in para.splitlines() if ln.strip())
        if joined:
            paragraphs.append(joined)
    return line_units + paragraphs


def wired(text: str, command: str, keywords: list[str]) -> list[str]:
    """Unidades que NOMBRAN `command` y contienen una marca de su paso del
    ciclo (redacción-tolerante ES+EN, a nivel línea o párrafo)."""
    cpat = re.compile(rf"\b{re.escape(command)}\b", re.IGNORECASE)
    kps = [re.compile(re.escape(kw), re.IGNORECASE) for kw in keywords]
    hits = []
    for unit in dict.fromkeys(units(text)):  # dedup conservando orden
        cmatch = cpat.search(unit)
        if cmatch and any(kp.search(unit) for kp in kps):
            hits.append(unit)
    return hits


def flagged_units(text: str, flags: list[str]) -> list[str]:
    """Unidades que copian flags de los CLIs (filas de tabla, bloques de
    comandos): una unidad con flag + tabulación/pipes de tabla/código."""
    out = []
    for unit in units(text):
        for flag in flags:
            if flag in unit and re.search(r"\||`|```", unit):
                out.append(unit)
                break
    return out


# ---------------------------------------------------------------- tests


class T3OrchestratorBodyWiring(unittest.TestCase):
    """(a) P1 (mitad orquestador) + P9 — los TRES cuerpos nombran cada
    comando en su paso del ciclo (§2.1/§2.3/§2.4), sin copiar flags."""

    @classmethod
    def setUpClass(cls):
        cls.texts = {rel: doc_text(rel) for rel in AGENT_RELS}

    # -- receive: staging del FINAL TEXT (§2.3) ----------------------------

    def test_p1_receive_names_staging_of_final_text(self):
        """P1/§2.3: cada cuerpo asocia `receive` con el STAGING del FINAL
        TEXT bajo `.cdad/inbox` (stageo) antes de ejecutarlo."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                hits = wired(text, "receive",
                             ["staged", "stageo", "stagea", "staging", "stage",
                              "inbox", "final text", "texto final", "final_text"])
                self.assertTrue(
                    hits,
                    f"P1/§2.3: el cuerpo operativo {rel} NO nombra el "
                    "staging del FINAL TEXT del rol como paso previo a "
                    "`receive` (los contratos viven en las references; el "
                    "paso debe estar NOMBRADO en el cuerpo) ⇒ AssertionError "
                    "por comportamiento ausente. Unidades con `receive`: "
                    f"{sorted({u[:110] for u in self._receive_units(text)})}")

    def test_p1_receive_names_cdad_result_and_receipt_validation(self):
        """P1/§2.3: cada cuerpo asocia `receive` con `cdad_result` y con la
        VALIDACIÓN del receipt antes de registrar el avance."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                tool_hits = wired(text, "receive", ["cdad_result"])
                self.assertTrue(
                    tool_hits,
                    f"P1/§2.3: el cuerpo operativo {rel} NO nombra `receive` "
                    "junto a `cdad_result` (el comando que produce el "
                    "receipt) ⇒ AssertionError por comportamiento ausente. "
                    "Unidades con `receive`: "
                    f"{sorted({u[:110] for u in self._receive_units(text)})}")
                receipt_hits = wired(text, "receive", ["receipt", "recibo"])
                self.assertTrue(
                    receipt_hits,
                    f"P1/§2.3: el cuerpo operativo {rel} NO nombra la "
                    "validación del RECEIPT como parte del paso `receive` "
                    "⇒ AssertionError por comportamiento ausente. "
                    "Unidades con `receive`: "
                    f"{sorted({u[:110] for u in self._receive_units(text)})}")

    def test_p1_receive_names_single_state_transition(self):
        """P1/I5/§2.3: cada cuerpo nombra la TRANSICIÓN ÚNICA de state
        (receive no aprueba; el state lo escribe solo el orquestador)."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                hits = wired(
                    text,
                    "receive",
                    ["única", "único", "única transición", "single",
                     "una sola", "única vez", "once", "solo el orquestador",
                     "transición"])
                self.assertTrue(
                    hits,
                    f"P1/I5/§2.3: el cuerpo operativo {rel} NO nombra la "
                    "TRANSICIÓN ÚNICA de state al cerrar `receive` (ni el "
                    "solo-escritor orquestador) ⇒ AssertionError por "
                    "comportamiento ausente. Unidades con `receive`: "
                    f"{sorted({u[:110] for u in self._receive_units(text)})}")

    # -- begin / checkpoint / reconcile / resume (P9, §2.1/§2.4) -----------

    def test_p9_begin_named_before_dispatch(self):
        """P9/§2.1: `begin` — write-ahead ANTES de despachar un paquete."""
        self._assert_named_in_step(
            "begin",
            ["despach", "dispatch", "write-ahead", "paquete", "packet",
             "antes de despach", "before dispatch"],
        )

    def test_p9_checkpoint_named_at_task_boundary(self):
        """P9/§2.1: `checkpoint` — al cerrar el límite de tarea/subfase."""
        self._assert_named_in_step(
            "checkpoint",
            ["cierre", "cerrar", "close", "límite", "limit", "tarea", "task",
             "subfase", "subphase", "boundary"],
        )

    def test_p9_reconcile_named_before_retry_or_resume(self):
        """P9/§2.4: `reconcile` — antes de TODO retry o resume."""
        self._assert_named_in_step(
            "reconcile",
            ["retry", "reintento", "resume", "rehacer", "antes de", "before"],
        )

    def test_p9_resume_named_at_new_session_start(self):
        """P9/§2.1: `resume` — al iniciar una sesión nueva (Step 1)."""
        self._assert_named_in_step(
            "resume",
            ["sesión nueva", "nueva sesión", "new session", "session start",
             "step 1", "iniciar", "inicia", "inicio", "start", "comienza",
             "al iniciar"],
        )

    def test_p1_continuity_commands_associated_with_cdad_continuity(self):
        """P1/§2.4: algún comando de continuidad viaja asociado a
        `cdad_continuity` (el cuerpo nombra el CLI responsable)."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                hits = []
                for cmd in ("begin", "checkpoint", "reconcile", "resume"):
                    hits.extend(wired(text, cmd, ["cdad_continuity"]))
                self.assertTrue(
                    hits,
                    f"P1/§2.4: el cuerpo operativo {rel} NO asocia ningún "
                    "comando de continuidad (begin/checkpoint/reconcile/"
                    "resume) con `cdad_continuity` ⇒ AssertionError por "
                    "comportamiento ausente")

    def _assert_named_in_step(self, command: str, step_keywords: list[str]):
        """P1/P9: cada cuerpo nombra `command` asociado a SU PASO (linea o
        párrafo; redacción-tolerante ES+EN)."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                hits = wired(text, command, step_keywords)
                self.assertTrue(
                    hits,
                    f"RED esperado para `{command}` en {rel}: el cuerpo "
                    "operativo NO lo nombra asociado a SU PASO del ciclo "
                    f"(keywords {step_keywords}; §2.1) ⇒ AssertionError por "
                    "comportamiento ausente. Unidades con el comando: "
                    f"{sorted({u[:110] for u in self._cmd_units(text, command)})}")

    # -- helpers de diagnóstico (sin leer nada fuera del doc) ---------------

    @staticmethod
    def _receive_units(text: str) -> list[str]:
        return wired(text, "receive", [""])

    @staticmethod
    def _cmd_units(text: str, command: str) -> list[str]:
        return wired(text, command, [""])

    # -- sin copiar flags (§2.1 "sin duplicar las interfaces") -------------

    def test_p1_no_duplicated_interface_flags(self):
        """P1: los cuerpos operativos NO copian la interfaz de los CLIs
        (bloques de comandos/filas de tabla con flags de los generators/
        CLIs CDAD; los contratos viven en las references y specs 002/003/
        004)."""
        offenders = []
        for rel, text in self.texts.items():
            for unit in flagged_units(text, NO_DUP_FLAGS):
                offenders.append(f"{rel}: {unit[:140]}")
        self.assertEqual(
            offenders, [],
            "P1/§2.1: los cuerpos del orquestador DUPLICAN la interfaz de "
            "los CLIs (flags copiados en tablas/bloques de comandos en vez "
            "de referenciar los contratos) ⇒ AssertionError por "
            f"comportamiento presente que no debería estar. Ofensores: "
            f"{offenders}")


class T3AgentRegenerationCoherence(unittest.TestCase):
    """(b) P1 — los agentes regenerados reflejan la fuente (make agents
    desde sources/; plan T3: "Regenerate agents/cdad-orchestrator.md,
    agents/claude-code/cdad-orchestrator.md (make agents)")."""

    @classmethod
    def setUpClass(cls):
        cls.texts = {rel: doc_text(rel) for rel in AGENT_RELS}
        source = AGENT_RELS[0]
        cls.source_wiring = {
            group: set(wired(cls.texts[source], *spec))
            for group, spec in cls._groups().items()
        }

    @staticmethod
    def _groups() -> dict[str, tuple[str, list[str]]]:
        return {
            "receive-staging": ("receive",
                                ["staged", "stageo", "stagea", "staging",
                                 "stage", "inbox", "final text",
                                 "texto final", "final_text"]),
            "receive-receipt": ("receive", ["receipt", "recibo"]),
            "receive-single-transition": (
                "receive",
                ["única", "único", "single", "una sola", "única vez",
                 "once", "solo el orquestador", "transición"]),
            "begin-dispatch": ("begin",
                               ["despach", "dispatch", "write-ahead",
                                "paquete", "packet", "antes de despach",
                                "before dispatch"]),
            "checkpoint-boundary": (
                "checkpoint",
                ["cierre", "cerrar", "close", "límite", "limit", "tarea",
                 "task", "subfase", "subphase", "boundary"]),
            "reconcile-retry": ("reconcile",
                                ["retry", "reintento", "resume", "rehacer",
                                 "antes de", "before"]),
            "resume-session": ("resume",
                               ["sesión nueva", "nueva sesión", "new session",
                                "session start", "step 1", "iniciar",
                                "inicia", "inicio", "start", "comienza",
                                "al iniciar"]),
        }

    def test_p1_regenerated_agents_reflect_source(self):
        """P1: para cada grupo de cableado, el conjunto de unidades que
        nombran el comando en los agentes regenerados es IDÉNTICO al de la
        fuente (los agentes reflejan `sources/roles/orchestrator.md`)."""
        for rel in AGENT_RELS[1:]:
            with self.subTest(archivo=rel):
                missing = []
                divergent = []
                for group, spec in self._groups().items():
                    agent_hits = set(wired(self.texts[rel], *spec))
                    src_hits = self.source_wiring[group]
                    if not agent_hits:
                        missing.append(group)
                    elif agent_hits != src_hits:
                        divergent.append({
                            "group": group,
                            "source": sorted(u[:100] for u in src_hits),
                            "agent": sorted(u[:100] for u in agent_hits),
                        })
                self.assertEqual(
                    missing, [],
                    f"P1: el agente regenerado {rel} pierde los grupos de "
                    f"cableado {missing}; la fuente es {AGENT_RELS[0]} "
                    "(regenerar con `make agents`) ⇒ AssertionError por "
                    "comportamiento ausente")
                self.assertEqual(
                    divergent, [],
                    f"P1: el agente regenerado {rel} DIVERGE de la fuente "
                    f"{AGENT_RELS[0]} en los grupos de cableado "
                    f"⇒ AssertionError por incoherencia. {divergent!r}")


class T3F1ReceivePointer(unittest.TestCase):
    """(c) F1 (review-t1-decision) — la frase de Step 6 que nombra
    `receive` remite a `references/re-entry.md` (o `cdad_result`) y NO
    atribuye `receive` a `references/continuity.md`."""

    @classmethod
    def setUpClass(cls):
        cls.text = skill_text()
        cls.receive_units = wired(cls.text, "receive", [""])
        cls.pointer = cls._pointer_units()

    @classmethod
    def _pointer_units(cls) -> list[str]:
        """Unidades que nombra `receive` con un puntero de referencia."""
        return [
            u for u in units(cls.text)
            if re.search(r"\breceive\b", u, re.IGNORECASE)
            and re.search(r"references/|\.md|cdad_result", u, re.IGNORECASE)
        ]

    def test_f1_receive_pointer_points_to_re_entry_or_cdad_result(self):
        """F1: existe (al menos) una unidad que remite `receive` a
        `references/re-entry.md` o a `cdad_result.py` (el paréntesis de la
        frase Step 6 del cableado; decision F1). La mera mención del PASO
        "re-entry" junto a `receive` NO es un puntero de referencia: se
        exige la ruta de referencia."""
        hits = [
            u for u in self.pointer
            if re.search(r"references/re[-_]entry\.md|cdad_result", u,
                         re.IGNORECASE)
        ]
        self.assertTrue(
            hits,
            "F1/review-t1-decision: la frase de Step 6 en SKILL.md que "
            "nombra `receive` NO remite a `references/re-entry.md` (ni a "
            "`cdad_result`): el puntero sigue atribuyendo receive a otro "
            "documento ⇒ AssertionError por comportamiento ausente. "
            "Unidades con `receive` + puntero: "
            f"{sorted({u[:140] for u in self.pointer})}")

    def test_f1_no_line_attributes_receive_to_continuity_md(self):
        """F1: NINGUNA unidad de SKILL.md empareja `receive` con
        `continuity.md` (el puntero erróneo de SKILL.md:278; los contratos
        de receive viven en references/re-entry.md y el CLI en
        cdad_result.py)."""
        offenders = [
            u for u in units(self.text)
            if re.search(r"\breceive\b", u, re.IGNORECASE)
            and re.search(r"continuity\.md", u, re.IGNORECASE)
        ]
        self.assertEqual(
            offenders, [],
            "F1/review-t1-decision: SKILL.md sigue ATRIBUYENDO `receive` a "
            "`references/continuity.md` (paréntesis de la frase Step 6); "
            "debe remitir a references/re-entry.md y a cdad_result.py "
            "⇒ AssertionError por comportamiento presente que no debería "
            f"estar. Ofensores: {sorted({u[:140] for u in offenders})}")


# ---------------------------------------------------------------- (d) CLIs


class T3RealCLICase(unittest.TestCase):
    """Proyecto sintético en tmpdir, con paquete DESPACHADO + staging del
    FINAL TEXT listo para `receive` (fixtures de tests del paquete 001/002,
    reutilizados como DATOS: solo se ejecutan los CLIs REALES)."""

    def setUp(self) -> None:
        sys.path.insert(0, str(REPO_ROOT / "tests"))
        from test_003_002_t1_receive import EstablishedProjectCase
        from test_004_002_t2_bootstrap import tree_snapshot

        self._TreeSnapshot = tree_snapshot
        case = EstablishedProjectCase("runTest")
        case.setUp()
        case.new_dispatched_project()  # real prepare + --record-dispatch
        self.case = case
        self.root = case.root
        # Staging del FINAL TEXT del rol (§2.3: role-report como part).
        parts = case.write_staged_parts()
        case.write_manifest(changes=[])
        descriptor = case.write_descriptor(
            case.build_descriptor(parts=parts,
                                  observed=case.observed_changes()))
        self.descriptor = descriptor
        self.state_bytes = (self.root / STATE_REL).read_bytes()
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", str(self.root.parent)],
                                   check=False))

    def run_receive(self) -> subprocess.CompletedProcess:
        return self.case.run_receive(self.descriptor)

    def run_reconcile(self) -> subprocess.CompletedProcess:
        ctx = self.root / ".cdad/executions" / self.case.execution_id / (
            "execution.json")
        argv = [sys.executable, str(CONTINUITY_SCRIPT), "reconcile",
                "--project-root", str(self.root),
                "--execution-context", str(ctx),
                "--packet", self.case.packet_id, "--json"]
        return subprocess.run(argv, cwd=REPO_ROOT, capture_output=True,
                              timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL)


class TestP7ReceiveStagesFinalTextAndReceipts(T3RealCLICase):
    """P7 (§2.3, guard honesto) — stageo + receive rc=0 con CLIs REALES.

    GUARD declarado (nota del orquestador): este recorrido YA PASA hoy
    (003-002 VERDE produce rc 0, receipt durable, retry idéntico y NO
    escribe el state). Su rol en T3 es de GUARDIA: si GREEN rompe el
    flujo, este test lo detecta. La mitad orquestador de P7
    (transición ÚNICA escrita por el orquestador) se cubre en el cuerpo
    operativo (clase T3OrchestratorBodyWiring, RED)."""

    def test_p07_staged_final_text_received_rc0_without_state_write(self):
        """P7/§2.3: el FINAL TEXT del rol stageado se recibe rc=0, stdout ==
        bytes del receipt.json canónico, el receipt NO aprueba
        (`semantic_status` = `pending`, I5) y el state NO es tocado por
        receive (el orquestador es su único escritor)."""
        proc = self.run_receive()
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P7/§2.3: receive del paquete staging debe terminar rc=0; "
                f"got rc={proc.returncode} stdout={out!r} stderr={err!r}")
        receipt_path = (self.root / ".cdad/runtime/results"
                        / self.case.execution_id / self.case.packet_id
                        / "receipt.json")
        receipt = json.loads(out)
        self.assertEqual(
            receipt.get("semantic_status"), "pending",
            msg=f"P7/I5/§2.3: receive NO aprueba — semantic_status "
                f"`pending`; got {receipt.get('semantic_status')!r} "
                f"(full={receipt!r})")
        self.assertEqual(
            proc.stdout, receipt_path.read_bytes(),
            msg="P7/§2.3: stdout == bytes del receipt.json canónico")
        self.assertEqual(
            (self.root / STATE_REL).read_bytes(), self.state_bytes,
            msg="P7/I5: receive NO escribe docs/.cdad-state.json (la "
                "transición la registra el orquestador; único escritor)")

    def test_p07_identical_retry_converges_byte_identical(self):
        """P7/§2.3: un retry idéntico converge al MISMO receipt byte a
        byte (idempotencia 002)."""
        first = self.run_receive()
        self.assertEqual(
            first.returncode, 0,
            msg="P7 (precondición del retry): el receive inicial debe "
                f"terminar rc=0; got {first.returncode} "
                f"stderr={first.stderr.decode()!r}")
        receipt_before = (self.root / ".cdad/runtime/results"
                          / self.case.execution_id / self.case.packet_id
                          / "receipt.json").read_bytes()
        second = self.run_receive()
        self.assertEqual(
            second.returncode, 0,
            msg=f"P7: el retry idéntico converge rc=0; got "
                f"{second.returncode} stderr={second.stderr.decode()!r}")
        receipt_after = (self.root / ".cdad/runtime/results"
                         / self.case.execution_id / self.case.packet_id
                         / "receipt.json").read_bytes()
        self.assertEqual(
            receipt_after, receipt_before,
            msg="P7/§2.3: el retry idéntico converge al MISMO receipt byte "
                "a byte (idempotencia; sin segundo efecto)")


class TestP8ReconcileClassifiesReceived(T3RealCLICase):
    """P8 (§2.4, guard honesto) — con `receive` en el flujo, `cdad_continuity
    reconcile` clasifica `received` sin runtime.

    GUARD declarado (nota del orquestador): YA PASA hoy — con un receipt
    producido por el receive REAL, reconcile reporta `received`
    (`repeat_effect: false`) y deja de estar en `dispatched-unknown`.
    Para T4 queda el recorrido completo (`reconcile` de la sesión real)."""

    def test_p08_reconcile_classifies_received_after_real_receive(self):
        """P8/§2.4: paquete dispatch I8 + receipt del receive REAL →
        `reconcile` clasifica `received` (no `dispatched-unknown`)."""
        proc = self.run_receive()
        self.assertEqual(
            proc.returncode, 0,
            msg="P8 (precondición): el receive real debe producir el "
                f"receipt; got rc={proc.returncode} "
                f"stderr={proc.stderr.decode()!r}")
        rc = self.run_reconcile()
        out = rc.stdout.decode("utf-8", errors="replace")
        err = rc.stderr.decode("utf-8", errors="replace")
        self.assertEqual(
            rc.returncode, 0,
            msg=f"P8/§2.4: reconcile termina rc=0; got rc={rc.returncode} "
                f"stdout={out!r} stderr={err!r}")
        env = json.loads(out)
        self.assertEqual(
            env.get("classification"), "received",
            msg=f"P8/§2.4: con receive en el flujo, reconcile clasifica "
                f"`received` (deja de ser dispatched-unknown); got "
                f"{(env.get('classification') or '').__class__.__name__}="
                f"{env.get('classification')!r} (full env "
                f"keys={sorted(env)})")
        self.assertNotEqual(
            env.get("classification"), "dispatched-unknown",
            msg="P8/§2.4: la clasificación ya NO es dispatched-unknown "
                "(el receipt del flujo new de receive es la señal fiable)")
        self.assertIs(
            env.get("repeat_effect"), False,
            msg="P8/D10: el efecto ya recibido NO se ofrece repetir")


if __name__ == "__main__":
    unittest.main()
