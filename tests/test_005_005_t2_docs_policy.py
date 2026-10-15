#!/usr/bin/env python3
"""005-005 T2 RED — una sola política de tests (PD-8..PD-11, INV-6).

Test de consistencia documental, caja negra: cada test lee los archivos de la
metodología y del epic AL EJECUTARSE y los evalúa contra las postcondiciones
derivadas de `docs/specs/005-005-adoption-coherence/spec.md` (§2 PD-8..PD-11,
§3 INV-6). Los oráculos no fueron derivados leyendo esos archivos — provienen
del contrato aprobado.

Un test por postcondición:
- PD-8  → política de evidencia única en `stage-3-tdd.md` §«Test evidence policy».
- PD-9  → sin afirmaciones de frecuencia por GREEN en consumers + referencia a la política.
- PD-10 → paquetes canónicos de GREEN/refactor/review-fix alineados a la política.
- PD-11 → enmienda fechada (2026-10-09) de PD-17 de 005-001 + decisión sobre el pin.

Expectativas de contenido de las secciones evaluadas (palabras clave) derivan
del texto de la PD correspondiente en la spec aprobada; el modo de fallo
esperado es AssertionError de comportamiento (documento inconsistente con la
política), nunca ImportError/NameError.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
STAGE3_REFS = REPO / "skills" / "cdad-cycle" / "references"
STAGE3_PACKETS = REPO / "skills" / "cdad-cycle" / "packets"
SPEC_005_001 = REPO / "docs" / "specs" / "005-001-idle-and-v7-bootstrap" / "spec.md"


def _load(path: Path) -> str:
    if not path.is_file():  # documento faltante es estado conductual, no error de oráculo
        pytest.fail(f"documento requerido no existe: {path}")
    return path.read_text(encoding="utf-8")


def _policy_section_heading_and_body(text: str):
    """Localiza la sección canónica «Test evidence policy» en un .md (caja negra).

    Devuelve (total_de_headings_con_ese_título, body_de_la_sección_única).
    Un heading es una línea que empieza por `#` y cuyo título es EXACTAMENTE
    «Test evidence policy» (la PD-8 exige «título exacto»).
    """
    heading_re = re.compile(r"^#{1,6}\s+Test evidence policy\s*$")
    matches = [
        (idx, line)
        for idx, line in enumerate(text.splitlines())
        if heading_re.match(line.strip())
    ]
    if not matches:
        return 0, ""
    start = matches[0][0]
    level = len(matches[0][1].split()[0].lstrip("#"))
    body_lines = []
    for line in text.splitlines()[start + 1 :]:
        m = re.match(r"^(#{1,6})\s+", line)
        if m and len(m.group(1)) <= level:
            break
        body_lines.append(line)
    return len(matches), "\n".join(body_lines)


def _split_packets_text(text: str):
    """Para archivos de paquete canónico (no necesariamente .md): texto entero."""
    return text


# ---------------------------------------------------------------------------
# PD-8 — política única de evidencia (owner canónico: stage-3-tdd.md §«Test
# evidence policy», sección ÚNICA con los cinco puntos).
# ---------------------------------------------------------------------------


def test_pd8_single_evidence_policy_section_with_five_points():
    text = _load(STAGE3_REFS / "stage-3-tdd.md")
    count, body = _policy_section_heading_and_body(text)

    # 1) La sección existe y es ÚNICA (título exacto).
    assert count == 1, (
        "PD-8 violada: la política de evidencia debe vivir en UNA sola sección "
        f"titulada exactamente «Test evidence policy» (encontradas: {count})"
    )

    # 2) Los cinco puntos de PD-8, derivados del contrato aprobado.
    # (i) regresión proporcional al cambio
    assert re.search(
        r"(?i)proportion\w+", body
    ), "PD-8(i) ausente: política sin «regresión proporcional al cambio»"
    # (ii) suite completa al cierre de la feature
    assert re.search(
        r"(?i)(full|complete)\s+suite", body
    ), "PD-8(ii) ausente: política sin «suite completa» en su texto"
    assert re.search(
        r"(?i)clos(e|ing|es|ed)|\bcierre\b", body
    ), "PD-8(ii) ausente: la suite completa no se ubica «al cierre de la feature»"
    # (iii) equivalencia de evidencia registrada REFERENCIADA desde re-entry.md
    assert re.search(
        r"(?i)re-entry\.md", body
    ), "PD-8(iii) ausente: la política no referencia el dueño canónico re-entry.md"
    assert re.search(
        r"(?i)Equivalence of a registered run", body
    ), "PD-8(iii) ausente: la política no referencia §«Equivalence of a registered run»"
    # (iv) la metodología define la evidencia; el proyecto declara los comandos
    assert re.search(
        r"(?i)(methodolog\w+|metodolog\w+)", body
    ) and re.search(
        r"(?i)(project|proyecto)[^\n]{0,60}(declar\w+|specif\w+)", body
    ), "PD-8(iv) ausente: falta el reparto metodología≠proyecto (evidencia definida por la metodología; comandos declarados por el proyecto)"
    # (v) condición local/entorno se registra en la evidencia y no se vuelve requisito
    assert re.search(
        r"(?i)(environ\w*|entorno\b|\blocal\b)", body
    ) and re.search(r"(?i)(registr\w+|registro)", body), (
        "PD-8(v) ausente: falta el tratamiento de condiciones locales/entorno "
        "(se registran en la evidencia, no se vuelven requisito)"
    )


# ---------------------------------------------------------------------------
# PD-9 — sin «suite completa por GREEN» en los consumidores: barrido negativo +
# cada consumidor remite a la política (PD-8) en vez de duplicarla.
# ---------------------------------------------------------------------------

PD9_FORBIDDEN = re.compile(
    r"(?i)once per GREEN|full suite per GREEN|required full regression suite"
)

PD9_CONSUMERS = [
    STAGE3_REFS / "stage-3-tdd.md",
    STAGE3_REFS / "re-entry.md",
    STAGE3_PACKETS / "substages" / "implementer-green.md",
    STAGE3_PACKETS / "substages" / "implementer-refactor.md",
    STAGE3_PACKETS / "substages" / "implementer-review-fix.md",
    STAGE3_PACKETS / "roles" / "implementer.md",
    REPO / "skills" / "cdad-cycle" / "SKILL.md",
    STAGE3_REFS / "handoff-prompts.md",
    STAGE3_REFS / "stage-4-review.md",
    STAGE3_REFS / "stage-5-merge.md",
    STAGE3_REFS / "sub-agent-strategies.md",
    STAGE3_REFS / "anti-patterns.md",
    STAGE3_REFS / "state-detection.md",
]

PD9_POLICY_REFERENCE = r"(?i)test evidence policy|evidence policy|\bPD-8\b"


def test_pd9_no_per_green_full_suite_retake_and_consumers_reference_policy():
    # Barrido en references/ y packets/ (INV-6: un solo dueño; los consumidores remiten).
    swept = {}
    for root in (STAGE3_REFS, STAGE3_PACKETS):
        for f in root.rglob("*"):
            if f.is_file() and (f.suffix == ".md" or f.suffix in {"", ".txt"}):
                swept[f] = _load(f)
    offenders = sorted(
        str(f) for f, content in swept.items() if PD9_FORBIDDEN.search(content)
    )
    assert not offenders, (
        "PD-9 violada: quedan afirmaciones de frecuencia por GREEN en: "
        f"{offenders}"
    )

    # Cada consumidor declarado en PD-9 remite a la política.
    stale = [str(f) for f in PD9_CONSUMERS if not re.search(PD9_POLICY_REFERENCE, _load(f))]
    assert not stale, (
        "PD-9 violada: consumidores que no referencian la política de evidencia: "
        f"{stale}"
    )


# ---------------------------------------------------------------------------
# PD-10 — paquetes canónicos alineados: GREEN refuerza regresión proporcional
# con comandos declarados por el proyecto y suite completa como gate de cierre;
# refactor y review-fix sin el término indefinido.
# ---------------------------------------------------------------------------

PD10_FILES = [
    STAGE3_PACKETS / "substages" / "implementer-green.md",
    STAGE3_PACKETS / "substages" / "implementer-refactor.md",
    STAGE3_PACKETS / "substages" / "implementer-review-fix.md",
]


@pytest.mark.parametrize("packet", PD10_FILES, ids=lambda p: p.name)
def test_pd10_canonical_packet_aligned_to_policy(packet):
    text = _load(_split_packets_text(packet))
    assert not PD9_FORBIDDEN.search(text), (
        f"PD-10 violada en {packet.name}: conserva el término indefinido "
        "«required full regression suite»"
    )
    assert re.search(PD9_POLICY_REFERENCE, text), (
        f"PD-10 violada en {packet.name}: no remite a la política de evidencia "
        "(debe referenciar «Test evidence policy» / PD-8, no duplicarla)"
    )
    assert re.search(r"(?i)proportion\w+", text), (
        f"PD-10 violada en {packet.name}: no declara la regresión proporcional "
        "que el cambio requiere"
    )


# ---------------------------------------------------------------------------
# PD-11 — enmienda fechada de PD-17 de 005-001: coincide con el recorrido
# ejecutado y hay decisión explícita sobre el pin de aprobación.
# ---------------------------------------------------------------------------


def test_pd11_dated_amendment_of_pd17_with_pin_decision():
    text = _load(SPEC_005_001)

    # Localiza el tramo del documento donde se habla de PD-17 (ventana ±12 líneas).
    lines = text.splitlines()
    pd17_idx = [i for i, line in enumerate(lines) if re.search(r"(?i)\bPD-17\b", line)]
    assert pd17_idx, "PD-11 violada: spec de 005-001 no menciona PD-17"
    window = "\n".join(
        "\n".join(lines[max(0, i - 12) : i + 13]) for i in pd17_idx
    )

    # Enmienda fechada (2026-10-09).
    assert re.search(r"(?i)2026-10-09", window), (
        "PD-11 violada: la enmienda de PD-17 no está fechada (2026-10-09) en su"
        " contexto"
    )
    assert re.search(
        r"(?i)(enmiend|amend)(ed|\w*)", window
    ), "PD-11 violada: el tramo de PD-17 no declara la enmienda"

    # Recorrido ejecutado, parte (a): paquete recibido y COMPLETADO antes de
    # preparar al test-writer (record-dispatch → staging → receive →
    # validate-receipt → transición).
    assert re.search(r"(?i)record-dispatch", window), (
        "PD-11 violada: la enmienda no declara el paso record-dispatch del "
        "recorrido ejecutado"
    )
    assert re.search(r"(?i)receive\w*", window), (
        "PD-11 violada: la enmienda no declara el paso receive"
    )
    assert re.search(r"(?i)validate-receipt", window), (
        "PD-11 violada: la enmienda no declara el paso validate-receipt"
    )
    assert re.search(r"(?i)test-writer", window), (
        "PD-11 violada: la enmienda no fija el orden «antes de preparar al "
        "test-writer»"
    )

    # Recorrido ejecutado, parte (b): el reemplazo se prueba sobre un paquete
    # todavía `prepared` y NO despachado.
    assert re.search(r"(?i)prepared", window), (
        "PD-11 violada: la enmienda exige probar el reemplazo sobre un paquete "
        "`prepared`"
    )
    assert re.search(r"(?i)(no despach\w+|not( |-)dispatch\w*)", window), (
        "PD-11 violada: la enmienda exige un paquete NO despachado"
    )

    # Decisión explícita sobre el pin de aprobación (re-registrarse o motivo
    # por el que no aplica a una feature done).
    assert re.search(r"(?i)\bpin\b", window), (
        "PD-11 violada: la enmienda no decide sobre el pin de aprobación"
    )
    assert re.search(
        r"(?i)(re-registr\w*|counter de pin|pin de aprobaci\w+)", window
    ), (
        "PD-11 violada: no hay decisión explícita de re-registro del pin (o "
        "motivo por el que no aplica a una feature done)"
    )
