#!/usr/bin/env python3
"""006-005 review-fix 2 RED — B-3 y B-4 de
`docs/specs/006-005-native-path-parity/rereview.md`.

Contrato y autoridad:

- `docs/specs/006-005-native-path-parity/spec.md` (aprobada, sha256
  `3a824be31e45cd8e6122b7d6f23d3f4d3e6af847ab73f7babef8aa90ce20df01`):
  §2.1 (la entrada `record` y sus banderas `--session`/`--parent`/`--since`),
  §2.3 (correlación por transporte: los TRES resultados — verificada, no
  verificable, verificada e incorrecta; «una llave no evaluable ⇒ `unknown`»
  y «el diagnóstico nombra la llave»), §2.4 (la observación de la vía
  nativa), §3 (PD-5, PD-6, PD-22), §4 (INV-1, INV-2, INV-8).
- `docs/specs/006-005-native-path-parity/rereview.md` (dictamen de etapa 4
  de la re-review): **B-3** — el procedimiento al que remiten los agentes
  GENERADOS todavía ordena escenificar y recibir la entrega EXTERNA (que ya
  está recibida y con recibo durable); **B-4** — el fix de B-2 cambió la
  semántica de la correlación: cuando la fila expone `parent_id` pero falta
  `--parent`, la llave se OMITE (antes producía `parent: unknown`) y el
  resultado acredita identidad donde el contrato exige `unknown`.
- Decisión del orquestador para B-4 (declarada en el encargo): se CONSERVA
  el contrato (spec §2.3, PD-5/PD-6) — una llave que la fila expone sin su
  declaración queda `unknown`, sin enmienda. Los tres resultados del
  contrato se conservan: verificada / no verificable (`unknown`) / verificada
  e incorrecta (rechazo).

QUÉ SE ESCRIBE AQUÍ (un archivo nuevo) y QUÉ SE REFORMULA (A-1)

- Nuevo: `tests/test_006_005_reviewfix2.py` (este archivo) — B-3 y B-4.
- A-1 (reformulación DECLARADA): los dos tests positivos de B-2 en
  `tests/test_006_005_reviewfix.py` acreditaban la fila seleccionada por
  `--session` SIN declarar `--parent`. Con el contrato conservado (B-4) esa
  omisión es exactamente el caso «no verificable» (la fila expone `parent_id`
  y la llave `parent` no tiene declaración ⇒ `unknown`), así que el oráculo
  positivo DEBE aportar la declaración que el contrato exige para acreditar.
  Se reformulan (el resto del test, sus fixtures y su propósito NO cambian):
  - `test_b2_session_selection_accredits_the_row_and_reports_the_model`
    (`:708-750`): la invocación pasa a declarar `--parent` (la fila ya lo
    expone; el padre declarado coincide).
  - `test_b2_session_selection_gives_the_same_result_as_parent_selection`
    (`:752-794`): la invocación por `--session` pasa a declarar `--parent`
    también; la comparación con la invocación por `--parent` sigue siendo la
    MISMA fila y el MISMO resultado.
  **PD enmendada:** ninguna. Lo que se corrige es el ORÁCULO, que fijaba un
  comportamiento ausente del contrato (acreditar sin declarar la llave que
  la fila expone); el contrato (spec §2.3, PD-5) queda intacto.

MAPA test → hallazgo (docstrings «review-fix 2 B-n (006-005)»)

  B-4 (la llave expuesta sin declaración queda `unknown`) — `TestB4ParentDeclaration`
    test_b4_exposed_parent_without_declaration_is_not_verified
    test_b4_matching_parent_declaration_verifies_the_row
    test_b4_contradictory_parent_declaration_is_a_rejection_without_delivery
  B-3 (el procedimiento distingue por estado de llegada) — `TestB3ReentryProtocol`
    test_b3_reentry_protocol_distinguishes_the_three_arrival_states
    test_b3_external_arrival_state_validates_the_receipt_without_staging_or_receiving
    test_b3_neither_generated_nor_reference_orders_staging_or_receiving_the_external_delivery
  B-3 (el recorrido real que la referencia debe describir) — `TestB3ExternalWalk`
    test_b3_external_walk_ends_with_a_valid_receipt_that_materialize_accepts

SUPERFICIE OBSERVABLE (caja negra; NO se lee implementación)

- B-4: la entrada `skills/cdad-cycle/scripts/cdad_dispatch.py` se invoca COMO
  PROCESO desde una copia staged del árbol del skill, de modo que el módulo
  REAL del runtime (`cdad_delegate_opencode.py`) es el que se resuelve; el
  store es un SQLite descartable con la forma REAL de la versión instalada
  (`time_created` INTEGER en epoch MILISEGUNDOS, `model` con el documento
  JSON observado) y la fila EXPONE `parent_id`. Se observan el sobre
  declarado (§2.1), el registro I8 que la entrada escribe, la entrega
  escenificada y su descriptor. El config, el store y el binario del usuario
  no se leen ni se escriben: todo es temporal.
- B-3: la REFERENCIA NORMATIVA (`skills/cdad-cycle/references/re-entry.md`,
  el «Orchestrator materialization protocol» al que remiten los agentes
  generados) y los ORQUESTADORES GENERADOS (`agents/cdad-orchestrator.md` y
  `agents/claude-code/cdad-orchestrator.md`) son ARTEFACTOS LEGIBLES del
  producto (no implementación); y el RECORRIDO se ejecuta de verdad (entry
  `dispatch` + módulo real + binario falso → sobre → `validate-receipt` →
  `materialize`).

RED ESPERADO HOY (medido en este HEAD, declarado, nunca accidental)

- B-4 (RED): con la fila exponiendo `parent_id` y SIN `--parent` declarado, la
  entrada ACREDITA la sesión (`verified: … matches the declared evidence
  (moment, project)`, `session: <hijo>`, `model_reported` informado) en vez
  de declarar `unknown`: la llave `parent` —que la fila expone— se omite y
  el diagnóstico NO la nombra. El contrato exige `unknown` + la garantía
  menor PD-6 (`session: null`, entrega persiste).
- B-4 (ANCLAS): con `--parent` coincidente la fila se acredita (hoy ya lo
  hace) y con `--parent` contradictorio la entrega es un RECHAZO sin entrega
  (hoy ya lo hace). Esas dos se conservan como guardas del contrato.
- B-3 (RED): la referencia NO distingue el estado de llegada: conserva la
  escenificación manual para «external CLI dispatch» (`:42-43`), ordena
  `receive` sin distinguir la entrega ya recibida (`:47-49`) y presenta la
  secuencia `receive → validate-receipt → materialize → transición` como la
  ruta del adaptador CLI (`:85-87`); el estado «descriptor ya escenificado»
  (nativa: `record` ⇒ `receive`) no está declarado en la referencia.
- B-3 (ANCLA): el RECORRIDO externo real ya es el correcto — el módulo
  recibe, el sobre trae `delivery_ref` = el RECIBO DURABLE, `validate-receipt`
  lo acepta y `materialize` procede sobre él. Ese test fija el
  comportamiento real que la referencia debe describir.

Ningún fallo es ImportError/SyntaxError/NameError ni error de fixture.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from test_006_005_reviewfix import (
    CHILD,
    MODEL_NORMALIZED,
    PARENT,
    ReviewFixB2Case,
    clauses,
    paragraphs,
    sentences_of,
)
from test_006_005_u6fix8_version_by_observation import (
    SERVER_VERSION,
    U6Fix8Case,
    tail,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_CLI = REPO_ROOT / "scripts" / "cdad_result.py"

# La REFERENCIA NORMATIVA: el procedimiento al que remiten los agentes
# generados (artefacto legible del producto; NO implementación).
REENTRY = REPO_ROOT / "skills" / "cdad-cycle" / "references" / "re-entry.md"

# Los ORQUESTADORES GENERADOS: salida declarada del generador.
GENERATED_ORCHESTRATORS = (
    REPO_ROOT / "agents" / "cdad-orchestrator.md",
    REPO_ROOT / "agents" / "claude-code" / "cdad-orchestrator.md",
)

# El padre CONTRADICTORIO del caso de rechazo (B-4).
OTHER_PARENT = "ses-parent-contradictory-9999"


# ===========================================================================
# B-4 — la llave que la fila expone sin declaración queda `unknown`
# ===========================================================================

# «Una llave no evaluable ⇒ `unknown`, y el diagnóstico nombra la llave»
# (spec §2.3, PD-5). La nota puede nombrar la llave como no evaluable,
# desconocida, ausente o no declarada: son SINONIMOS del mismo resultado
# (la llave no se pudo evaluar porque nadie la declaró).
PARENT_NOT_EVALUABLE_RE = re.compile(
    r"(?is)(?:parent|padre)[^.\n]{0,200}"
    r"(?:not evaluable|no evaluable|not evaluated|no evaluad|not declared"
    r"|no declarad|not verifiable|no verificable|unknown|desconocid"
    r"|missing|absent|not supplied|not given|falta|sin )"
    r"|(?:not evaluable|no evaluable|not evaluated|no evaluad|not declared"
    r"|no declarad|not verifiable|no verificable|unknown|desconocid"
    r"|missing|absent|not supplied|not given|falta|sin )"
    r"[^.\n]{0,200}(?:parent|padre)")

# La contradicción EVALUABLE de la llave `parent` (spec §2.3, resultado 3):
# un rechazo que NOMBRA la llave que contradice.
PARENT_CONTRADICTION_RE = re.compile(
    r"(?is)(?:parent|padre)[^.\n]{0,200}"
    r"(?:does not match|doesn't match|not match|no coincide|does not coincide"
    r"|contradict|mismatch|discrepan|not the declared|not the observed"
    r"|is not the parent|different parent)"
    r"|(?:does not match|doesn't match|not match|no coincide|contradict"
    r"|mismatch|discrepan|not the declared|not the observed)"
    r"[^.\n]{0,200}(?:parent|padre)")

# La procedencia que declara que la identidad NO se pudo verificar (PD-6).
UNVERIFIED_PROVENANCE_RE = re.compile(
    r"(?i)not verified|no verified|could not be verified|cannot be verified"
    r"|couldn't be verified|no se pudo verificar|no pudo verificarse"
    r"|unknown|not evaluable|no evaluable|unverified|without verifying")


def note_text(out: dict | None = None, record: dict | None = None) -> str:
    """Sólo la NOTA que la invocación declara (el diagnóstico del sobre y los
    valores de la procedencia del registro); nunca el intento ni la sesión: un
    id podría contener una palabra que la nota debe decir."""
    parts: list = []
    if out is not None and out.get("diagnosis"):
        parts.append(str(out["diagnosis"]))
    if record is not None:
        provenance = record.get("provenance")
        if isinstance(provenance, dict):
            parts.extend(str(value) for value in provenance.values())
    return "\n".join(parts)


class TestB4ParentDeclaration(ReviewFixB2Case):
    """review-fix 2 B-4 (006-005): la llave que la fila EXPONE pero que
    nadie declara queda `unknown` — la selección de la fila y la suficiencia
    de la evidencia son cosas distintas (spec §2.3, PD-5, PD-6, INV-2)."""

    def test_b4_exposed_parent_without_declaration_is_not_verified(
            self) -> None:
        """review-fix 2 B-4 (006-005) — spec §2.3 (resultado 2), PD-5, PD-6:
        la fila SELECCIONADA expone `parent_id` pero la llave `parent` no
        tiene DECLARACIÓN (no se pasó `--parent`) ⇒ esa llave NO es evaluable
        ⇒ el resultado es `unknown`: NO se acredita ninguna sesión
        (`session: null`), la NOTA nombra la llave `parent` como no evaluable
        y, con resultado nativo byte-exacto, la entrega PERSISTE bajo la
        garantía menor declarada (PD-6: `session: null` + procedencia que
        declara que la identidad no se pudo verificar).

        La fila está bien seleccionada (`--session` la fija); lo que falta es
        la EVIDENCIA: sin la declaración del padre, la llave que la fila
        expone no se puede evaluar y no se puede acreditar identidad.

        HOY la entrada OMITE la llave expuesta y acredita la sesión
        (`verified: … (moment, project)`), que es exactamente lo que el
        contrato prohíbe."""
        project = self.new_project()
        self.write_store([self.row(project)])
        before = self.records(project)

        proc = self.record(project, attempt="att-rf2-b4-0001", session=CHILD)
        out = self.envelope(proc, "B-4 (fila con padre expuesto, sin "
                                  "declaración)")
        record = self.single_record(project, before)

        self.assertIsNone(
            out.get("session"),
            msg="review-fix 2 B-4 (006-005)/§2.3: la fila expone `parent_id` "
                "pero la llave `parent` NO tiene declaración ⇒ el resultado "
                "es `unknown` y NO se acredita ninguna sesión; el sobre "
                "declara %r (acreditar sin declarar la llave que la fila "
                "expone contradice el resultado «no verificable» del "
                "contrato)" % (out.get("session"),))
        self.assertIsNone(
            record.get("session"),
            msg="review-fix 2 B-4 (006-005)/PD-5: el registro I8 acreditó la "
                "sesión (%r) sin que la llave `parent` expuesta por la fila "
                "tuviera declaración; una llave no evaluable es `unknown`, "
                "nunca una sesión acreditada"
                % (record.get("session"),))

        note = note_text(out, record)
        self.assertRegex(
            note, PARENT_NOT_EVALUABLE_RE,
            msg="review-fix 2 B-4 (006-005)/§2.3: el diagnóstico NO nombra la "
                "llave `parent` como no evaluable (la fila la expone y nadie "
                "la declaró):\n%s" % self.tail(note, 12))
        self.assertNotEqual(
            out.get("termination"), "blocked",
            msg="review-fix 2 B-4 (006-005)/INV-2: la llave ausente NO es una "
                "contradicción: el resultado es `unknown`, no un rechazo; la "
                "terminación observada es %r" % (out.get("termination"),))

        # PD-6: la garantía menor declarada — la entrega PERSISTE con la
        # sesión nula y una procedencia que declara lo que no se pudo
        # verificar (INV-1: el recibo nace pendiente, nada se aprueba).
        self.assertTrue(
            self.staged_payloads(project),
            msg="review-fix 2 B-4 (006-005)/PD-6: con resultado nativo "
                "byte-exacto y identidad no verificable, la entrega se "
                "persiste (garantía menor declarada); no se escenificó "
                "nada")
        self.assertTrue(
            self.descriptor_path(project).is_file(),
            msg="review-fix 2 B-4 (006-005)/PD-6: la entrega persistida lleva "
                "su descriptor `RESULT.json`; no existe")
        provenance = record.get("provenance")
        self.assertIsInstance(
            provenance, dict,
            msg="review-fix 2 B-4 (006-005)/PD-6/INV-8: el `provenance` del "
                "intento no es un objeto: %r" % (provenance,))
        declared = str(provenance.get("session") or "")
        self.assertTrue(
            declared.strip(),
            msg="review-fix 2 B-4 (006-005)/PD-6: la procedencia no declara "
                "nada sobre la sesión: %r" % (provenance,))
        self.assertRegex(
            declared, UNVERIFIED_PROVENANCE_RE,
            msg="review-fix 2 B-4 (006-005)/PD-6: la procedencia de la "
                "sesión NO declara que la identidad no se pudo verificar: %r"
                % (declared,))

    def test_b4_matching_parent_declaration_verifies_the_row(self) -> None:
        """review-fix 2 B-4 (006-005) — ANCLA: con la llave `parent`
        DECLARADA y coincidente con la que la fila expone, el resultado es
        VERIFICADA: se acredita la sesión observada, `model_reported` sale
        en la forma normalizada y la entrega byte-exacta se escenifica.

        ANCLA (verde hoy): fija el comportamiento que la corrección de B-4
        NO debe romper — acreditar la identidad cuando la evidencia está
        declarada."""
        project = self.new_project()
        self.write_store([self.row(project)])
        before = self.records(project)

        proc = self.record(project, attempt="att-rf2-b4-0002", session=CHILD,
                           parent=PARENT)
        out = self.envelope(proc, "B-4 (padre declarado y coincidente)")
        record = self.single_record(project, before)

        self.assertEqual(
            out.get("session"), CHILD,
            msg="review-fix 2 B-4 (006-005)/§2.3: con el padre declarado y "
                "coincidente, la sesión observada se acredita; el sobre "
                "declara %r" % (out.get("session"),))
        self.assertEqual(
            record.get("session"), CHILD,
            msg="review-fix 2 B-4 (006-005): con el padre declarado y "
                "coincidente la sesión observada se acredita; el registro "
                "guardó %r" % (record.get("session"),))
        self.assertEqual(
            record.get("model_reported"), MODEL_NORMALIZED,
            msg="review-fix 2 B-4 (006-005)/§2.4: `model_reported` sale de la "
                "observación del módulo en la forma normalizada "
                "`<provider>/<model>`; el registro guardó %r"
                % (record.get("model_reported"),))
        self.assertTrue(
            self.staged_payloads(project),
            msg="review-fix 2 B-4 (006-005): la entrega nativa byte-exacta no "
                "se escenificó")

    def test_b4_contradictory_parent_declaration_is_a_rejection_without_delivery(
            self) -> None:
        """review-fix 2 B-4 (006-005) — ANCLA: con la llave `parent`
        DECLARADA y CONTRADICHA por la fila, el resultado es el tercero —
        VERIFICADA E INCORRECTA: un RECHAZO que nombra la llave, sin entrega
        (nada se escenifica, ni descriptor, ni recibo) y sin acreditar
        ninguna sesión (INV-2: una contradicción evaluable es rechazo, nunca
        `unknown`).

        ANCLA (verde hoy): el tercer resultado del contrato se conserva; la
        corrección de B-4 no puede rebajarlo a `unknown`."""
        project = self.new_project()
        self.write_store([self.row(project)])
        before = self.records(project)

        proc = self.record(project, attempt="att-rf2-b4-0003", session=CHILD,
                           parent=OTHER_PARENT)
        out = self.envelope(proc, "B-4 (padre declarado y contradictorio)")

        self.assertEqual(
            out.get("termination"), "blocked",
            msg="review-fix 2 B-4 (006-005)/INV-2: una contradicción evaluable "
                "de la llave `parent` es un RECHAZO (la terminación cerrada "
                "del rechazo es `blocked`); se observó %r"
                % (out.get("termination"),))
        self.assertIsNone(
            out.get("session"),
            msg="review-fix 2 B-4 (006-005): un rechazo NO acredita sesión; "
                "el sobre declara %r" % (out.get("session"),))
        note = self.diagnosis_text(out)
        self.assertRegex(
            note, PARENT_CONTRADICTION_RE,
            msg="review-fix 2 B-4 (006-005)/§2.3: el rechazo debe NOMBRAR la "
                "llave que contradice:\n%s" % self.tail(note, 12))
        self.assertFalse(
            self.staged_payloads(project),
            msg="review-fix 2 B-4 (006-005)/PD-4: se escenificó la entrega "
                "pese a la contradicción: un rechazo NO entrega")
        self.assertFalse(
            self.descriptor_path(project).is_file(),
            msg="review-fix 2 B-4 (006-005)/PD-4: se escribió el descriptor "
                "RESULT.json pese a la contradicción")
        self.assertFalse(
            self.receipt_path(project).is_file(),
            msg="review-fix 2 B-4 (006-005)/INV-1: se escribió un recibo pese "
                "a la contradicción: un rechazo no fabrica recibo")
        for stem, document in ((stem, json.loads(path.read_text(encoding="utf-8")))
                               for stem, path in self.records(project).items()
                               if stem not in set(before)):
            self.assertNotEqual(
                document.get("session"), CHILD,
                msg="review-fix 2 B-4 (006-005): el registro I8 acreditó la "
                    "sesión contradicha (%r): una contradicción evaluable "
                    "nunca se guarda como sesión verificada" % (stem,))


# ===========================================================================
# B-3 — el procedimiento distingue por ESTADO DE LLEGADA
# ===========================================================================

# --- marcadores del contrato (conceptos, no frases literales) -------------

# El texto final del rol, todavía NO escenificado.
FINAL_TEXT_RE = re.compile(r"(?i)final\s+text|texto\s+final")
# La acción de escenificar (escribir los bytes exactos bajo el inbox).
STAGE_ORDER_RE = re.compile(
    r"(?i)\bstag(e|es|ed|ing)\b|\bescenific\w*|\bwrite the exact bytes\b")
# El verbo `record` de la entrada (la vía nativa).
RECORD_RE = re.compile(r"(?i)(?<!\w)record(?!\w)")
# El verbo `receive` como COMANDO (no el sustantivo «receipt»).
RECEIVE_RE = re.compile(r"(?i)(?<!\w)receive(?!\w)")
# El recibo durable: el artefacto de la vía EXTERNA.
DURABLE_RECEIPT_RE = re.compile(
    r"(?i)durable|already received|already persisted|recibo\s+durable")
# La clave del sobre que nombra el recibo durable.
DELIVERY_REF_RE = re.compile(r"(?i)delivery_ref")
# La validación del recibo durable (cualquier redacción del verbo).
VALIDATION_RE = re.compile(
    r"(?i)validat\w*|validar|verif\w*|comprobar|check")
# La materialización de las partes.
MATERIALIZE_RE = re.compile(r"(?i)materializ\w*")
# La transición de estado.
TRANSITION_RE = re.compile(
    r"(?i)register[-_]transition|transition|transici[oó]n")
# La vía EXTERNA (la que no devuelve un FINAL TEXT al orquestador).
EXTERNAL_ROUTE_RE = re.compile(
    r"(?i)\bexternal\b|\bexterno\b|cli adapter|cli delegation|cli dispatch"
    r"|other runtime|the other runtime")
# La vía EXTERNA en la DECLARACIÓN del estado de llegada (tolerante: el
# módulo del runtime es quien recibió la entrega).
EXTERNAL_ARRIVAL_RE = re.compile(
    r"(?i)\bexternal\b|\bexterno\b|cli adapter|cli delegation|cli dispatch"
    r"|other runtime|the other runtime|runtime module|the module"
    r"|el módulo")
# Negación o hecho consumado: la cláusula NO ordena la acción.
NEGATION_RE = re.compile(
    r"(?i)\b(not|no|never|nothing|nada|nunca|without|sin|instead|already"
    r"|done|hecho|hecha)\b")


def section_region(text: str, heading_re: str) -> str:
    """La región de una sección markdown (desde su encabezado hasta el
    siguiente encabezado del mismo nivel o superior)."""
    lines = text.splitlines()
    start = None
    level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match and re.search(heading_re, match.group(2), re.IGNORECASE):
            start = index
            level = len(match.group(1))
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = re.match(r"^(#{1,6})\s", lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end])


LIST_ITEM_RE = re.compile(r"^\s*(?:\d+\.|[-*+])\s")


def logical_blocks(paragraph: str) -> list:
    """Los bloques lógicos de un párrafo markdown: una línea que abre un ítem
    de lista CORTA el bloque anterior (en markdown, un ítem y el texto que lo
    precede pueden no estar separados por una línea vacía: sin esta cortesía
    una ruta declarada se mezclaría con las rutas vecinas y la unidad
    declarada no sería la que el documento dice)."""
    blocks: list = []
    current: list = []
    for line in paragraph.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if LIST_ITEM_RE.match(line) and current:
            blocks.append(current)
            current = []
        current.append(stripped)
    if current:
        blocks.append(current)
    return blocks


def text_units(text: str) -> list:
    """Unidades candidatas de una región: cada BLOQUE LÓGICO, cada LÍNEA no
    vacía y cada ventana de DOS líneas consecutivas DENTRO del mismo bloque.
    Un estado puede declararse en prosa (bloque o frase envuelta) o en una
    tabla (una fila = un estado); en un bloque de tabla cada fila es su
    propia unidad y las filas NO se combinan entre sí (una tabla declara un
    estado por fila: mezclarlas produciría un estado que nadie declaró)."""
    units: list = []
    for para in paragraphs(text):
        for block in logical_blocks(para):
            if any(line.startswith("|") for line in block):
                for line in block:
                    units.append((line, 1))
                continue
            units.append(("\n".join(block), len(block)))
            for index, line in enumerate(block):
                units.append((line, 1))
                if index + 1 < len(block):
                    units.append((line + " " + block[index + 1], 2))
    return units


def units_matching(units: list, predicate) -> list:
    return [(text, width) for text, width in units if predicate(text)]


def smallest(matches: list):
    """La unidad coincidente MÁS ESTRECHA (la fila de la tabla o la frase):
    la que cubre menos líneas del documento."""
    if not matches:
        return None
    return min(matches, key=lambda item: (item[1], len(item[0])))


def ordered_actions(unit: str) -> list:
    """Las cláusulas de la unidad que ORDENAN escenificar o recibir (sin
    negación): una orden es un imperativo de acción, no su prohibición."""
    offenders: list = []
    for clause in clauses(unit):
        if NEGATION_RE.search(clause):
            continue
        if STAGE_ORDER_RE.search(clause):
            offenders.append(clause)
        if RECEIVE_RE.search(clause):
            offenders.append(clause)
    return offenders


class TestB3ReentryProtocol(unittest.TestCase):
    """review-fix 2 B-3 (006-005): el procedimiento al que remiten los
    agentes generados (`references/re-entry.md`, «Orchestrator materialization
    protocol») DISTINGUE POR ESTADO DE LLEGADA y no ordena escenificar ni
    recibir la entrega del despacho EXTERNO (que ya está recibida y con
    recibo durable)."""

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REENTRY.read_text(encoding="utf-8")
        # La región es el «Orchestrator materialization protocol»; si el
        # encabezado se renombra más allá de lo reconocible, la referencia
        # COMPLETA se busca (la exigencia del contrato es que la referencia
        # distinga los estados de llegada).
        cls.region = section_region(cls.text, r"materialization protocol")
        if not cls.region.strip():
            cls.region = cls.text
        cls.units = text_units(cls.region)

    # -- (a) los tres estados de llegada ---------------------------------

    def test_b3_reentry_protocol_distinguishes_the_three_arrival_states(
            self) -> None:
        """review-fix 2 B-3 (006-005) — cierre del dictamen: la referencia
        COMÚN distingue POR ESTADO DE LLEGADA, con una ruta declarada para
        cada estado:

        1. **FINAL TEXT pendiente de escenificar** ⇒ el orquestador lo
           escenifica (los bytes exactos) y ejecuta `receive`;
        2. **descriptor ya escenificado** (la vía NATIVA: el verbo `record`
           ya escribió el texto y su descriptor) ⇒ `receive`, sin
           escenificar otra vez;
        3. **recibo ya durable** (la vía EXTERNA: el sobre trae
           `delivery_ref`) ⇒ se valida el recibo y se sigue con
           `materialize`/`register-transition`, SIN escenificar y SIN
           recibir otra vez.

        HOY la referencia no declara el estado 2 (no dice que `record` deja
        el descriptor escenificado y que basta `receive`) ni el estado 3."""
        # Estado 1 — FINAL TEXT pendiente de escenificar.
        state_one = units_matching(
            self.units,
            lambda unit: (FINAL_TEXT_RE.search(unit)
                          and STAGE_ORDER_RE.search(unit)
                          and RECEIVE_RE.search(unit)))
        self.assertTrue(
            state_one,
            msg="review-fix 2 B-3 (006-005): la referencia no declara el "
                "estado de llegada «FINAL TEXT pendiente de escenificar» con "
                "su ruta (escenificar los bytes exactos y ejecutar "
                "`receive`). La región examinada:\n%s"
                % tail(self.region, 40))

        # Estado 2 — descriptor ya escenificado (nativa: `record` ⇒
        # `receive`).
        state_two = units_matching(
            self.units,
            lambda unit: RECORD_RE.search(unit) and RECEIVE_RE.search(unit))
        self.assertTrue(
            state_two,
            msg="review-fix 2 B-3 (006-005): la referencia no declara el "
                "estado de llegada «descriptor ya escenificado» con su ruta "
                "(la vía NATIVA: el verbo `record` ya dejó el texto y su "
                "descriptor ⇒ `receive`, sin escenificar otra vez). Hoy la "
                "referencia sólo dice que el `record` hace la escenificación "
                "MECÁNICA y manda a `receive` a otra parte, sin declarar el "
                "estado. La región examinada:\n%s"
                % tail(self.region, 40))

        # Estado 3 — recibo ya durable (externa: el sobre trae
        # `delivery_ref`).
        state_three = units_matching(
            self.units,
            lambda unit: ((DURABLE_RECEIPT_RE.search(unit)
                           or DELIVERY_REF_RE.search(unit))
                          and EXTERNAL_ARRIVAL_RE.search(unit)
                          and VALIDATION_RE.search(unit)
                          and (MATERIALIZE_RE.search(unit)
                               or TRANSITION_RE.search(unit))))
        self.assertTrue(
            state_three,
            msg="review-fix 2 B-3 (006-005): la referencia no declara el "
                "estado de llegada «recibo ya durable» con su ruta (la vía "
                "EXTERNA: el sobre trae `delivery_ref` ⇒ validar el recibo y "
                "seguir con `materialize`/`register-transition`). La región "
                "examinada:\n%s" % tail(self.region, 40))

    # -- (b) la ruta externa no ordena escenificar ni recibir -------------

    def test_b3_external_arrival_state_validates_the_receipt_without_staging_or_receiving(
            self) -> None:
        """review-fix 2 B-4 → B-3 (006-005): la ruta del estado «recibo ya
        durable» (la EXTERNA) VALIDA el recibo y sigue con
        `materialize`/`register-transition`; NO ordena escenificar la
        entrega otra vez ni recibirla otra vez (el módulo ya la recibió y el
        recibo ya es durable: la operación que la referencia pedía ya
        ocurrió y su insumo no vuelve).

        Este es el recorrido real medido: `dispatch → el módulo registra y
        recibe → sobre con `delivery_ref`=recibo → validate-receipt →
        materialize → register-transition`."""
        matches = units_matching(
            self.units,
            lambda unit: ((DURABLE_RECEIPT_RE.search(unit)
                           or DELIVERY_REF_RE.search(unit))
                          and EXTERNAL_ARRIVAL_RE.search(unit)
                          and VALIDATION_RE.search(unit)
                          and (MATERIALIZE_RE.search(unit)
                               or TRANSITION_RE.search(unit))))
        self.assertTrue(
            matches,
            msg="review-fix 2 B-3 (006-005): la referencia no declara la "
                "ruta del estado «recibo ya durable» (la EXTERNA: validar el "
                "recibo y seguir con `materialize`/`register-transition`); no "
                "hay ninguna unidad que la declare. La región examinada:\n%s"
                % tail(self.region, 40))
        unit = smallest(matches)[0]
        offenders = ordered_actions(unit)
        self.assertEqual(
            offenders, [],
            msg="review-fix 2 B-3 (006-005): la ruta del estado «recibo ya "
                "durable» ORDENA escenificar o recibir la entrega externa "
                "(que ya está recibida): %r. La ruta externa entra "
                "directamente por la validación del recibo. Unidad:\n%s"
                % (offenders, tail(unit, 12)))

    # -- (c) ni el generado ni la referencia ordenan la entrega externa ----

    def test_b3_neither_generated_nor_reference_orders_staging_or_receiving_the_external_delivery(
            self) -> None:
        """review-fix 2 B-3 (006-005): NI el orquestador GENERADO NI la
        REFERENCIA ordenan escenificar o recibir la entrega del despacho
        EXTERNO. La entrega externa llega con su recibo durable (el módulo
        ya la recibió); lo que queda por hacer es validarlo, materializarlo y
        registrar la transición.

        HOY la referencia presenta la secuencia `receive` → `validate-receipt`
        → `materialize` → transición como la ruta del adaptador CLI, con
        `receive` atribuido al CLI adapter."""
        documents = [("references/re-entry.md", self.text)]
        for path in GENERATED_ORCHESTRATORS:
            documents.append((path.relative_to(REPO_ROOT).as_posix(),
                              path.read_text(encoding="utf-8")))

        offenders: list = []
        for label, text in documents:
            for block in paragraphs(text):
                for sentence in sentences_of(block):
                    if not EXTERNAL_ROUTE_RE.search(sentence):
                        continue
                    # La frase que DECLARA el estado «recibo ya durable» (o
                    # el hecho consumado) no ordena nada: la entrega ya
                    # está recibida y su insumo no vuelve.
                    if (DURABLE_RECEIPT_RE.search(sentence)
                            or DELIVERY_REF_RE.search(sentence)
                            or NEGATION_RE.search(sentence)):
                        continue
                    actions = ordered_actions(sentence)
                    if actions:
                        offenders.append((label, actions, sentence))
        self.assertEqual(
            offenders, [],
            msg="review-fix 2 B-3 (006-005): una frase ordena escenificar o "
                "recibir la entrega del despacho EXTERNO (que ya está "
                "recibida y con recibo durable): %r. La entrega externa no "
                "se escenifica otra vez ni se recibe otra vez."
                % (offenders,))


# ===========================================================================
# B-3 — el recorrido externo real (ancla del comportamiento que la
#      referencia debe describir)
# ===========================================================================


class TestB3ExternalWalk(U6Fix8Case):
    """review-fix 2 B-3 (006-005) — el RECORRIDO externo real: el módulo
    REAL recibe la entrega, el sobre trae `delivery_ref` = el RECIBO DURABLE,
    `validate-receipt` lo acepta y `materialize` PROCEDE sobre él."""

    def test_b3_external_walk_ends_with_a_valid_receipt_that_materialize_accepts(
            self) -> None:
        """review-fix 2 B-3 (006-005) — ANCLA: el recorrido externo real
        (entry + módulo real del runtime + binario falso) termina con un
        RECIBO DURABLE que `validate-receipt` acepta y sobre el que
        `materialize` procede (copia los bytes a su target declarado).

        Ésta es la salida real que la referencia debe describir: la ruta
        externa entra por la validación del recibo, no por una escenificación
        ni por una recepción nuevas."""
        server = self.start_server(SERVER_VERSION)
        self.write_runtimes(self.section(server=server.url))

        proc = self.dispatch()
        out = self.envelope(proc, "B-3 (recorrido externo)")

        ref = out.get("delivery_ref")
        self.assertIsInstance(
            ref, str,
            msg="review-fix 2 B-3 (006-005): `delivery_ref` no es texto: %r"
                % (ref,))
        receipt = Path(ref)
        self.assertTrue(
            receipt.is_file(),
            msg="review-fix 2 B-3 (006-005): `delivery_ref` no apunta a un "
                "recibo durable existente: %r" % (ref,))
        self.assertTrue(
            str(receipt).endswith("receipt.json"),
            msg="review-fix 2 B-3 (006-005): `delivery_ref` debe ser el RECIBO "
                "durable (`receipt.json`); apunta a %r" % (ref,))

        valid = subprocess.run(
            [sys.executable, str(RESULT_CLI), "validate-receipt",
             "--project-root", str(self.project["root"]),
             "--receipt", str(receipt)],
            capture_output=True, text=True, cwd=str(self.project["root"]),
            timeout=120)
        self.assertEqual(
            valid.returncode, 0,
            msg="review-fix 2 B-3 (006-005): `validate-receipt` debe aceptar el "
                "recibo que declara `delivery_ref`; rc=%s stderr=%r"
                % (valid.returncode, (valid.stderr or "")[:400]))

        # `materialize` PROCEDE sobre ese recibo: la parte se copia a su
        # target declarado, con los bytes exactos (PD-3 del receipt).
        document = json.loads(receipt.read_text(encoding="utf-8"))
        parts = document.get("parts") or []
        self.assertTrue(
            parts,
            msg="review-fix 2 B-3 (006-005): el recibo no declara ninguna "
                "parte: el módulo no llegó a recibir la entrega: %r"
                % (document,))
        part = parts[0]
        target = ("docs/specs/004-002-project-execution-bootstrap/"
                  "reviewfix-b3-role-report.md")
        authorization = {
            "schema_version": 1,
            "execution_id": document["execution_id"],
            "packet_id": document["packet_id"],
            "receipt_sha256": hashlib.sha256(
                receipt.read_bytes()).hexdigest(),
            "authorized_by": "006-005 review-fix 2 (B-3) — orquestador",
            "authority_ref": ("docs/epics/epic-004-single-source-planning/"
                              "execution.md"),
            "approval_effect": False,
            "copies": [
                {
                    "part": part["name"],
                    "target": target,
                    "expected_previous_sha256": None,
                }
            ],
        }
        authorization_path = (self.project["root"] / ".cdad" / "inbox"
                              / "MATERIALIZE.json")
        authorization_path.write_text(
            json.dumps(authorization, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")

        materialized = subprocess.run(
            [sys.executable, str(RESULT_CLI), "materialize",
             "--project-root", str(self.project["root"]),
             "--receipt", str(receipt),
             "--authorization", str(authorization_path)],
            capture_output=True, text=True, cwd=str(self.project["root"]),
            timeout=120)
        self.assertEqual(
            materialized.returncode, 0,
            msg="review-fix 2 B-3 (006-005): `materialize` debe PROCEDER sobre "
                "el recibo durable de la vía externa; rc=%s stdout=%r "
                "stderr=%r"
                % (materialized.returncode, (materialized.stdout or "")[:200],
                   (materialized.stderr or "")[:400]))
        target_path = self.project["root"] / target
        self.assertTrue(
            target_path.is_file(),
            msg="review-fix 2 B-3 (006-005): `materialize` no escribió el "
                "target declarado: %r" % (target,))
        stored = target_path.read_bytes()
        self.assertEqual(
            len(stored), part.get("bytes"),
            msg="review-fix 2 B-3 (006-005): el materializado no conserva los "
                "bytes declarados por la parte (%r vs %r)"
                % (len(stored), part.get("bytes")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
