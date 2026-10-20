#!/usr/bin/env python3
"""005-006 T3 RED — responsable de sincronizar `epic_features` (PD-12; INV-3).

Test de consistencia ESTRUCTURAL de artefactos distribuidos, caja negra
(precedente: `tests/test_005_006_t1_start_procedure.py`,
`tests/test_005_005_t2_docs_policy.py`). Cada test lee los archivos AL
EJECUTARSE y los evalúa contra postcondiciones derivadas de
`docs/specs/005-006-guided-project-start/spec.md` (§2 PD-12, §3 INV-3) y de la
tarea T3 del plan aprobado (`plan.md` §T3). Los oráculos no fueron derivados
leyendo los archivos evaluados — provienen del contrato aprobado, y nunca
buscan "frases del prompt" ni intentan probar determinísticamente que un
modelo seguirá instrucciones (`efficient-orchestration-requirements.md:107`).

Un test por postcondición (INV como foco estructural aparte):
- PD-12 (a) → `skills/cdad-epic/references/epic-planning.md`
          §«If the plan needs to be updated during the feature loop» ASIGNA el
          responsable de sincronizar `epic_features` al aplicar un cambio de
          plan aprobado: el **coordinador de epic** es responsable de la
          sincronización.
- PD-12 (b) → el procedimiento de arranque
          (`skills/cdad-cycle/references/project-start.md`) describe el
          manejo del desfase detectado (R2): nombra las entradas faltantes o
          sobrantes de `epic_features`, encamina la sincronización hacia
          `cdad-epic`, sin inventar features ni bloquearse en silencio.
- PD-12 (c) → LOCK DE REGRESIÓN (no cambio): el enforcement en código
          (`skills/cdad-cycle/scripts/cdad_packet.py`, en las DOS funciones que
          alojan las regiones declaradas por la spec: `validate_state` y
          `_active_feature_entry`) SIGUE exigiendo la entrada en
          `epic_features` (exactamente una vez, no cerrada). Debe pasar HOY;
          cualquier corrimiento del enforcement está fuera del alcance
          (spec §5: «Cambiar el comportamiento de prepare o el enforcement
          de epic_features en código» está fuera de alcance).
          Las regiones se localizan por SÍMBOLO (la función que las contiene),
          nunca por número de línea: los números de línea se corren con cada
          cambio del archivo (006-005 los desplazó) y un lock por línea
          degrada a «falla por corrimiento» —cuando el enforcement NO
          cambió— o, peor, a «falla por renombre» sin distinguir el caso.
- INV-3 (foco T3) → la misma sección de `epic-planning.md` respeta el escritor
          único del state: el coordinador de epic es responsable de la
          sincronización, pero el ESCRITOR ÚNICO del state sigue siendo el
          orquestador (el coordinador encamina / propone; no muta el state).

El modo de fallo esperado es AssertionError / `pytest.fail` de comportamiento
(documento inconsistente o inexistente respecto del contrato aprobado), nunca
ImportError/SyntaxError/NameError/AttributeError/ValueError.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EPIC_PLANNING = REPO / "skills" / "cdad-epic" / "references" / "epic-planning.md"
PROJECT_START = REPO / "skills" / "cdad-cycle" / "references" / "project-start.md"
CDAD_PACKET = REPO / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"


def _load(path: Path) -> str:
    if not path.is_file():  # documento faltante es estado conductual, no error de oráculo
        pytest.fail(f"documento requerido no existe: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers estructurales (caja negra; derivados del contrato aprobado).
# ---------------------------------------------------------------------------

def _section_body(text: str, heading_re: re.Pattern) -> str:
    """Cuerpo de la primera sección cuyo heading casa con heading_re.

    Devuelve "" si no existe el heading (el fallo lo declara el test).
    El cuerpo va del heading siguiente hasta el próximo heading de nivel
    igual o superior (misma convención de `test_005_005_t2_docs_policy.py`).
    """
    lines = text.splitlines()
    start, level = None, None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if heading_re.match(stripped):
            start = i
            level = len(stripped.split()[0])
            break
    if start is None:
        return ""
    body = []
    for line in lines[start + 1 :]:
        m = re.match(r"^(#{1,6})\s", line)
        if m and len(m.group(1)) <= level:
            break
        body.append(line)
    return "\n".join(body)


def _pair_near(text: str, anchor_re: re.Pattern, partner_re: re.Pattern, span: int = 3) -> bool:
    """Verdadero si alguna línea que casa `anchor_re` tiene `partner_re` dentro
    de una ventana de ±span líneas (palabras responsables, co-localizadas:
    nada de detectar coincidencias ajenas en todo el archivo)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if anchor_re.search(line):
            window = "\n".join(lines[max(0, i - span) : i + span + 1])
            if partner_re.search(window):
                return True
    return False


# ---------------------------------------------------------------------------
# PD-12 (a) — epic-planning.md asigna el responsable de sincronizar
# epic_features al aplicar un cambio de plan aprobado: el coordinador de epic.
# ---------------------------------------------------------------------------

PD12_HEADING = re.compile(
    r"^#{1,6}\s+If\sthe\splan\sneeds\sto\sbe\supdated\sduring\sthe\s"
    r"feature\sloop\s*:?\s*$"
)
PD12_COORDINATOR = re.compile(r"(?i)epic\s+coordinator|coordinador\s+de\s+epic")
PD12_SYNC_VERB = re.compile(r"(?i)\bsynchroniz\w*|\bsync\b|\bupdate[sd]?\b|\bactualiz\w*")
PD12_APPROVED_CHANGE = re.compile(r"(?i)\bapprov\w+\b|\baprobado\b")


def test_pd12_epic_planning_assigns_epic_features_sync_owner():
    text = _load(EPIC_PLANNING)

    # 1) La sección declarada por la spec sigue existiendo (título exacto registrado).
    body = _section_body(text, PD12_HEADING)
    assert body, (
        "PD-12 violada: skills/cdad-epic/references/epic-planning.md ya no "
        "declara la sección «If the plan needs to be updated during the "
        "feature loop» (la spec la registra como el lugar del arreglo)"
    )

    # 2) La sección asigna la sincronización de epic_features (el objeto del
    #    desfase) — hoy la sección NO la menciona: este es el rojo del contrato.
    assert re.search(r"\bepic_features\b", body), (
        "PD-12 violada: la sección «If the plan needs to be updated during "
        "the feature loop» de epic-planning.md no menciona epic_features; "
        "aplicar un cambio de plan aprobado debe incluir sincronizar "
        "epic_features (spec PD-12)"
    )

    # 3) La sección nombra al responsable: el coordinador de epic.
    assert PD12_COORDINATOR.search(body), (
        "PD-12 violada: la sección de epic-planning.md no asigna el "
        "responsable de sincronizar epic_features (debe ser el coordinador "
        "de epic, según PD-12/D5)"
    )

    # 4) El marco del cambio es el plan APROBADO con un verbo de sincronización
    #    co-localizado con epic_features (estructura: cambio aprobado → sync).
    assert PD12_APPROVED_CHANGE.search(body), (
        "PD-12 violada: la sección de epic-planning.md no enmarca la "
        "sincronización en la aplicación de un cambio de plan APROBADO"
    )
    assert _pair_near(
        body,
        re.compile(r"\bepic_features\b"),
        PD12_SYNC_VERB,
        span=4,
    ), (
        "PD-12 violada: la sección de epic-planning.md no enuncia la "
        "sincronización (synchronize/update) de epic_features como parte de "
        "aplicar el cambio de plan"
    )


# ---------------------------------------------------------------------------
# PD-12 (b) — project-start.md describe el manejo del desfase de
# epic_features (R2): nombra entradas faltantes/sobrantes, encamina a
# cdad-epic, no inventa features ni se bloquea en silencio.
# ---------------------------------------------------------------------------

PD12_DRIFT = re.compile(
    r"(?i)\b(desfase|drift|\bout of sync\b|misalignment|mismatch|stale\s*(?:plan|state))\b"
)
PD12_MISSING_OR_LEFTOVER = re.compile(
    r"(?i)\b(missing|ausente|faltante[s]?|faltan\b|leftover|stale|extra\b|"
    r"sobrant\w*|sobra[nr]?\b)"
)
PD12_ROUTE_VERB = re.compile(
    r"(?i)\b(route|encamin\w*|redirect|hand[- ]?off|re[- ]?run|rerun|"
    r"refer\w*|volver|go back|return)\b"
)
PD12_NO_INVENT = re.compile(
    r"(?i)\b(no|not|never|nunca|jamás|sin|without|do\s+not|don't|must\s+not)\b"
    r"[^.\n]{0,40}\b(invent\w*|fabricat\w*|synthesize)\b"
)
PD12_FEATURES_WORD = re.compile(r"(?i)\b(features?|epic_features)\b")
PD12_NO_SILENT_BLOCK = re.compile(
    r"(?i)\b(no|not|never|nunca|jamás|without|sin|do\s+not|don't)\b"
)


def test_pd12_project_start_names_drift_and_routes_sync_to_cdad_epic():
    text = _load(PROJECT_START)

    # 1) El desfase de epic_features es reconocido en el arranque (R2).
    assert re.search(r"\bepic_features\b", text), (
        "PD-12 violada: el procedimiento de arranque (project-start.md) no "
        "trata el desfase de epic_features (R2, fricción 5)"
    )
    assert PD12_DRIFT.search(text), (
        "PD-12 violada: el procedimiento de arranque no declara el desfase "
        "(drift) detectado entre el plan aprobado y epic_features"
    )

    # 2) Nombra las entradas faltantes o sobrantes del desfase (co-localizado).
    assert _pair_near(
        text, re.compile(r"\bepic_features\b"), PD12_MISSING_OR_LEFTOVER, span=5
    ), (
        "PD-12 violada: el procedimiento de arranque no NOMBRA las entradas "
        "faltantes o sobrantes de epic_features; declara el desfase sin "
        "decir qué falta o sobra (spec PD-12)"
    )

    # 3) Encamina la sincronización hacia cdad-epic (ruta explícita, no un
    #    arreglo local del ciclo).
    assert re.search(r"\bcdad-epic\b", text), (
        "PD-12 violada: el procedimiento de arranque no encamina la "
        "sincronización del desfase hacia cdad-epic (spec PD-12: «encamina "
        "la sincronización, volver a cdad-epic»)"
    )
    assert _pair_near(
        text, re.compile(r"\bcdad-epic\b"), PD12_ROUTE_VERB, span=4
    ), (
        "PD-12 violada: la mención de cdad-epic en el procedimiento de "
        "arranque no está enunciable como RUTA de sincronización (verbo de "
        "encaminar/referir co-localizado)"
    )

    # 4) Sin inventar features ni bloquearse en silencio (salida legítima).
    invent_lines = [
        i
        for i, line in enumerate(text.splitlines())
        if PD12_NO_INVENT.search(line)
    ]
    no_invent_near_features = any(
        PD12_FEATURES_WORD.search(
            "\n".join(text.splitlines()[max(0, i - 2) : i + 3])
        )
        for i in invent_lines
    )
    assert no_invent_near_features, (
        "PD-12/INV-3 violadas: el procedimiento de arranque no prohíbe "
        "INVENTAR features ante un desfase (spec PD-12: «no inventa "
        "features»)"
    )
    silent_lines = [
        (i, line)
        for i, line in enumerate(text.splitlines())
        if re.search(r"(?i)\bsilently\b|\bsilenciosamente\b|\ben\s+silencio\b|\bsilencio\b", line)
        and re.search(r"(?i)\bblock\w*|bloque\w*|wait\b|halt\b|stall\b", line)
    ]
    assert silent_lines and any(
        PD12_NO_SILENT_BLOCK.search(line) for _, line in silent_lines
    ), (
        "PD-12/INV-3 violadas: el procedimiento de arranque no prohíbe "
        "bloquearse en silencio ante el desfase (spec PD-12: «ni se bloquea "
        "en silencio»); debe nombrar qué falta y cómo seguir"
    )


# ---------------------------------------------------------------------------
# PD-12 (c) — LOCK DE REGRESIÓN: el enforcement en código NO cambia.
# cdad_packet.py sigue exigiendo la entrada en epic_features en sus dos
# regiones declaradas por la spec. Este test DEBE pasar HOY: es un cerco, no
# un cambio (spec §2 «Sin cambios de código de producto», §5 fuera de
# alcance).
#
# LAS REGIONES SE LOCALIZAN POR SÍMBOLO, NO POR NÚMERO DE LÍNEA.
# Las dos regiones de enforcement que la spec declara viven, respectivamente,
# en las funciones `validate_state` (el enforcement de la entrada del
# execution feature) y `_active_feature_entry` (el enforcement de la entrada
# del active feature). Los números de línea que la spec cita son de su HEAD
# medido y se corren con cada cambio del archivo: 006-005 los desplazó y el
# lock por línea pasó a fallar sin que el enforcement hubiera cambiado (un
# oráculo que miente sobre el código es peor que no tener oráculo). El
# símbolo NO se corre: la función que aloja el enforcement es el ancla
# estable, y un renombre del enforcement es un cambio real que este lock
# debe señalar (se declara, no se absorbe).
#
# LO QUE EL LOCK PROTEGE NO CAMBIA: el enforcement de epic_features sigue
# exigiendo la entrada en los DOS sitios, y en cada uno:
#   (a) la entrada se EXIGE (hay un raise vivo que nombra `epic_features`);
#   (b) la entrada ocurre EXACTAMENTE UNA vez (cardinalidad);
#   (c) la entrada NO está CERRADA (status en curso).
# Cada sitio se evalúa por separado (son funciones distintas): el lock es de
# las dos regiones, no de un único punto.
# ---------------------------------------------------------------------------

# Los dos sitios del enforcement, por el símbolo que los aloja.
LOCK_SITES = {
    "validate_state": "la entrada del execution feature en epic_features",
    "_active_feature_entry": "la entrada del active feature en epic_features",
}

# Cardinalidad: «exactamente una vez» (variantes de redacción toleradas).
LOCK_CARDINALITY = re.compile(
    r"(?i)exactly\s+(once|one)\b|exactamente\s+una\s+vez|una\s+sola\s+vez"
)
# Estado cerrado de la entrada: «cerrada / hecha / cancelada».
LOCK_CLOSED = re.compile(
    r"(?i)\bclosed\b|\bdone\b|\bcancelled\b|cancelad\w*|cerrad\w*|in[- ]progress"
)
# Referencia al status de la entrada (la que se comprueba contra el estado).
LOCK_STATUS = re.compile(r"(?i)\bstatus\b")
# Referencia a la entrada misma (la fila de epic_features de la que se habla).
LOCK_ENTRY = re.compile(r"(?i)feature|matching|entry|entrada")


def _function_body(lines: list[str], symbol: str) -> tuple[int, list[str]] | None:
    """(línea_absoluta_de_inicio, cuerpo) de la función de nivel de módulo
    `symbol` (ancla estable).

    Devuelve None si el símbolo no existe (el fallo lo declara el test: un
    enforcement movido o renombrado es un cambio que hay que declarar, no
    algo que el lock pueda absorber en silencio).
    """
    pattern = re.compile(rf"^def\s+{re.escape(symbol)}\s*\(")
    start = None
    for i, line in enumerate(lines):
        if pattern.match(line):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^(def\s|class\s|@)", lines[j]):
            end = j
            break
    return start, lines[start:end]


def _raise_windows(
    body: list[str], before: int = 1, after: int = 3
) -> list[tuple[int, str]]:
    """(índice, texto) por cada `raise` del cuerpo, con su contexto.

    La ventana empareja el ENFORCEMENT (el `raise`) con la condición que lo
    dispara (el `if` de la línea anterior) y con el texto del mensaje
    (continuaciones en las líneas siguientes). Se exige que el `raise` esté
    VIVO (código, no comentario) y que la ventana no contenga líneas
    comentadas: si no, un enforcement comentado («raise muerto») seguiría
    satisfaciendo el lock por el texto de su mensaje.
    """
    windows = []
    for i, line in enumerate(body):
        if not line.strip().startswith("raise "):
            continue
        lo = max(0, i - before)
        hi = min(len(body), i + after + 1)
        code = [
            w for w in body[lo:hi] if not w.strip().startswith("#")
        ]
        windows.append((i, "\n".join(code)))
    return windows


def test_pd12_enforcement_lock_cdad_packet_epic_features():
    if not CDAD_PACKET.is_file():
        pytest.fail(
            f"LOCK de regresión (PD-12) violado: el enforcement en código no "
            f"existe más: {CDAD_PACKET}"
        )
    lines = CDAD_PACKET.read_text(encoding="utf-8").splitlines()

    missing: list[str] = []
    weak: list[tuple[str, str]] = []
    evidence: dict[str, list[int]] = {}

    for symbol, what in LOCK_SITES.items():
        found = _function_body(lines, symbol)
        if found is None:
            missing.append(symbol)
            continue
        start, body = found
        windows = _raise_windows(body)
        # Dónde vive hoy el enforcement de este sitio (evidencia del fallo,
        # no oráculo: el oráculo es el símbolo).
        evidence[symbol] = [
            start + i + 1 for i, _ in windows if "epic_features" in body[i]
        ]

        # (a) la entrada se EXIGE: hay un raise vivo que nombra epic_features.
        if not any("epic_features" in w for _, w in windows):
            weak.append(
                (symbol, f"no hay un raise que nombre `epic_features` ({what})")
            )
            continue
        # (b) la entrada ocurre EXACTAMENTE UNA vez.
        if not any(
            "epic_features" in w and LOCK_CARDINALITY.search(w) for _, w in windows
        ):
            weak.append(
                (
                    symbol,
                    f"no exige que la entrada ocurra exactamente una vez ({what})",
                )
            )
        # (c) la entrada NO está cerrada (su status se comprueba).
        if not any(
            LOCK_STATUS.search(w)
            and LOCK_CLOSED.search(w)
            and LOCK_ENTRY.search(w)
            for _, w in windows
        ):
            weak.append(
                (symbol, f"no exige que la entrada no esté cerrada ({what})")
            )

    assert not missing, (
        "LOCK de regresión (PD-12) violado: el enforcement de epic_features "
        f"deja de estar en {missing} (las dos regiones declaradas por la spec "
        "deben seguir existiendo, cada una en su función); mover o renombrar "
        "el enforcement de epic_features está FUERA del alcance de 005-006 "
        "(spec §2/§5) — el ciclo no muta el código de registro de features"
    )
    assert not weak, (
        "LOCK de regresión (PD-12) violado: el enforcement de epic_features "
        f"existe pero ya no exige lo que exigía: {weak} (evidencia: "
        f"{evidence}); cambiar el enforcement de epic_features en código está "
        "FUERA del alcance de 005-006 (spec §2/§5)"
    )
    # El lock es de las DOS regiones distintas, no de un único punto: son
    # símbolos distintos (dos funciones), cada uno con su enforcement vivo.
    assert len(set(LOCK_SITES)) == 2 and all(
        evidence.get(symbol) for symbol in LOCK_SITES
    ), (
        "LOCK de regresión (PD-12) violado: las dos regiones de enforcement "
        "deben mantenerse como puntos independientes del enforcement de "
        f"epic_features (evidencia: {evidence})"
    )


# ---------------------------------------------------------------------------
# INV-3 (foco T3) — el escritor único del state sigue siendo el orquestador:
# el coordinador de epic es el responsable de la sincronización, pero NO
# muta el state por su cuenta (el state lo escribe el orquestador).
# ---------------------------------------------------------------------------

def test_inv3_sole_state_writer_remains_orchestrator_in_sync_section():
    text = _load(EPIC_PLANNING)
    body = _section_body(text, PD12_HEADING)
    assert body, (
        "INV-3 violada (foco T3): la sección «If the plan needs to be "
        "updated during the feature loop» de epic-planning.md no existe; no "
        "se puede verificar el reparto de responsabilidad del state"
    )

    # El orquestador mantiene el rol de escritor del state (co-localizado).
    orchestrator = re.compile(r"(?i)\borchestrator\b|\borquestador\b")
    assert orchestrator.search(body), (
        "INV-3 violada (foco T3): la sección de epic-planning.md no declara "
        "que el orquestador sigue siendo el escritor único del state"
    )
    assert _pair_near(
        body,
        orchestrator,
        re.compile(
            r"(?i)\b(sole|single|unique|only|único|única|unica|"
            r"escritor\w*|writer|writes|write[s]?)\b"
        ),
        span=4,
    ), (
        "INV-3 violada (foco T3): la sección de epic-planning.md no enuncia "
        "el reparto (coordinador de epic responsable de la sincronización; "
        "el ESCRITOR ÚNICO del state sigue siendo el orquestador) — sin ese "
        "enunciado, la sincronización por el coordinador podría mutar el "
        "state sin pasar por el escritor único"
    )
