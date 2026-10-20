#!/usr/bin/env python3
"""006-006 U3 RED — el recorrido principal, el gate 2→3 y la política de
compatibilidad.

Contrato:
- `docs/specs/006-006-spec-plan-review/spec.md` — §2.6 (el recorrido principal
  y el gate 2→3), §2.7 (la exención: sus cuatro campos), §3 PD-10 (el gate
  2→3 y el exit gate de la etapa 2 declaran la evidencia de la revisión; sus
  DOS controles negativos), PD-14 (la revisión no habilita construir), PD-16(b)
  (la política de compatibilidad y sus dos salidas), INV-9/INV-10, D-10
  (el gate es supervisado), D-12 (la consecuencia se declara, no se corrige).
- `docs/specs/006-006-spec-plan-review/plan.md` §3 ficha U3 (archivos, RED,
  regresiones, A-1) y su bloque `plan-tasks` (los `observable_checks` de U3).

Superficie bajo prueba — TEXTO DE PROCEDIMIENTO y PROCESO REAL del CLI:

- `skills/cdad-cycle/references/stage-2-specification.md` — la subfase de la
  revisión de borrador, el exit gate y la forma declarada de la exención;
- `skills/cdad-cycle/SKILL.md` — el gate 2→3 y el mapa del ciclo;
- `skills/cdad-cycle/references/re-entry.md` — la re-entry del dictamen y la
  declaración de la política de compatibilidad;
- `skills/cdad-cycle/references/handoff-prompts.md` — la plantilla del reviewer
  (`plan-review`): la invocación con la forma y la identidad doble;
- `skills/cdad-cycle/scripts/cdad_packet.py` — SÓLO como SUBPROCESO (nunca se
  importa ni se lee su código): el gate 2→3 NO es un bloqueo del CLI.

Oráculos (por CONCEPTO, no por frase exacta; sólo se cita verbatim lo que la
ficha cita: el artefacto `plan-review.md`, las banderas `--object-kind`,
`--spec-path` y `--spec-version`, los cuatro campos de la exención y el
marcador `approval pending`):

- O-1 — el exit gate de la etapa 2 nombra el artefacto `plan-review.md` y la
  CONDICIÓN DE BLOQUEANTES (cada bloqueante resuelto o descartado con razón
  escrita), por vecindad.
- O-2 — la etapa 2 declara la SUBFASE de la revisión de borrador: despachar el
  paquete `plan-review` sobre el borrador, recibir el dictamen, rutear los
  bloqueantes (al architect o a la autoridad) y la re-review focal; y sólo
  entonces la aprobación. (El matiz de orden —«recién entonces»— es juicio de
  la revisión, no un oráculo por listas de palabras: aquí se fija el
  CONTENIDO declarado de la subfase.)
- O-3 — en la etapa 2 queda enunciada la FORMA DECLARADA de la exención: sus
  cuatro campos (`exempted_by`, `delegated`, `requested_by`, `reason`) juntos.
- O-4 — el gate 2→3 de `SKILL.md` nombra el artefacto `plan-review.md` y la
  condición de bloqueantes (espejo del gate 4→5).
- O-5 — el MAPA DEL CICLO (la flecha Stage 2→Stage 3) nombra la revisión del
  borrador.
- O-6 — `re-entry.md` tiene la RE-ENTRY DEL DICTAMEN de borrador (qué hacer con
  él: corregir, re-review focal, exención).
- O-7 — la plantilla del reviewer declara las banderas de la FORMA y de la
  IDENTIDAD DOBLE (`--object-kind`, `--spec-path`, `--spec-version`).
- O-8 — `re-entry.md` nombra la POLÍTICA entre revisiones (un paquete publicado
  bajo una revisión de las fuentes de instrucción no es recibible después de
  que cambien) y sus DOS SALIDAS (terminarlo bajo la revisión con la que se
  publicó, o preparar uno nuevo bajo la revisión vigente).

CONTROLES NEGATIVOS de PD-10 (los DOS casos, distintos entre sí — O-2 de la
ficha, que corrige el control viejo):

- (i) con una aprobación `specification` VIGENTE (pin que coincide con los
  bytes del contrato) y SIN dictamen (`plan-review.md` no existe en el
  proyecto), el `prepare` de un rol de construcción NO se rechaza: rc=0 y
  publica el paquete — el gate 2→3 es SUPERVISADO y el CLI no verifica la
  existencia del dictamen (D-10, §2.6).
- (ii) SIN aprobación, el mismo `prepare` se RECHAZA con el diagnóstico
  `approval pending` (PD-14), sin publicar nada.

Los dos casos se arman con la MISMA fixture descartable y difieren SÓLO en la
entrada de aprobación: la diferencia del resultado es atribuible a la
aprobación y no a otra cosa.

Fallos del modo RED esperado: `AssertionError` de comportamiento sobre el
texto (faltan el artefacto, la condición de bloqueantes, la subfase, la
re-entry, las banderas o la política) o `pytest.fail` de estado conductual
(archivo de procedimiento requerido inexistente). NUNCA ImportError,
SyntaxError, NameError ni error de fixture. Nada de skip.

CONTROLES DECLARADOS (verdes con el producto en vigor; NO son aserciones que
deban fallar al abrir el RED — los fija la ficha U3 y el A-1 del plan §4):

- Los dos controles negativos de PD-10 (i) y (ii) de arriba: hoy el CLI no
  comprueba el dictamen, luego (i) rc=0 y (ii) rc=2 con `approval pending`.
- La plantilla NO re-enuncia el procedimiento: referencia el substage pineado
  y no copia sus obligaciones (operacionalización determinista: la del
  oráculo vigente 005-007 PD-12/P5 — quien menciona el conjunto cerrado de
  valores del marcador `detail` tiene que REFERENCIAR la regla o su hogar;
  además, las obligaciones verbatim del procedimiento no aparecen copiadas).

A-1 (plan §4): este RED **NO reemplaza ningún oráculo vigente**; sólo AÑADE
casos. Comprobado sobre las siete regresiones de la ficha (intake 005-006 T2,
render y paquetes de rol, `cdad-generate`, detalle progresivo 005-007 T1,
materialización del informe del architect 005-007 T4 y materialización
003-002 T2): ninguna fija el texto de estas cuatro superficies, y las que
miden el paquete del reviewer calculan el sha256 del substage DINÁMICAMENTE
(luego no lo fijan). Los fixtures compartidos `DRAFT_PLAN_RELPATH` no se
tocan; este RED no usa ese fixture (usa su propia fixture descartable).

Mapeo test → postcondición:

  test_pd10_stage2_exit_gate_names_the_dictamen_artifact_and_the_blocker_condition
      -> PD-10 (O-1): el exit gate de la etapa 2 nombra `plan-review.md` y la
         condición de bloqueantes.
  test_pd10_stage2_declares_the_draft_review_subphase
      -> PD-10 (O-2): la subfase de la revisión de borrador en la etapa 2.
  test_pd10_stage2_states_the_declared_form_of_the_exemption
      -> PD-10 (O-3): la forma declarada de la exención (sus cuatro campos;
         los campos son de PD-9/§2.7, el LUGAR de la enunciación es de U3).
  test_pd10_skill_gate_2_to_3_names_the_dictamen_artifact_and_the_blocker_condition
      -> PD-10 (O-4): el gate 2→3 de `SKILL.md`.
  test_pd10_skill_cycle_map_names_the_draft_review
      -> PD-10 (O-5): el mapa del ciclo.
  test_pd10_reentry_has_the_draft_verdict_reentry
      -> PD-10 (O-6): la re-entry del dictamen de borrador.
  test_pd10_handoff_template_declares_the_form_and_the_double_identity_flags
      -> PD-10 (O-7): la invocación con la forma y la identidad doble.
  test_pd10_control_negative_handoff_template_does_not_restate_the_procedure
      -> PD-10 (O-7, control negativo): la plantilla NO re-enuncia el
         procedimiento.
  test_pd10_control_negative_vigente_approval_without_dictamen_is_not_rejected
      -> PD-10 (O-2, control negativo (i)): con aprobación vigente y sin
         dictamen, el `prepare` de un rol de construcción NO se rechaza
         (rc=0): el gate es supervisado.
  test_pd10_control_negative_without_approval_the_same_prepare_is_rejected
      -> PD-10 + PD-14 (control negativo (ii)): sin aprobación, el mismo
         `prepare` se rechaza con `approval pending`.
  test_pd16b_reentry_declares_the_compatibility_policy_between_revisions
      -> PD-16(b) (O-8): la política entre revisiones.
  test_pd16b_reentry_declares_the_two_exits_of_the_compatibility_policy
      -> PD-16(b) (O-8): sus dos salidas.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

import pytest

from tests.test_005_007_t1_progressive_detail_rule import (
    DETAIL_TOKEN,
    QUOTED_NEXT,
    QUOTED_PLANNED,
    RULE_REFERENCE,
    _lines,
    _restates_closed_values,
)
from tests.test_packet_prepare import PACKET_CLI, PrepareProject, run_prepare

REPO = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO / "skills" / "cdad-cycle"

STAGE2 = SKILL_ROOT / "references" / "stage-2-specification.md"
SKILL_MD = SKILL_ROOT / "SKILL.md"
RE_ENTRY = SKILL_ROOT / "references" / "re-entry.md"
HANDOFF = SKILL_ROOT / "references" / "handoff-prompts.md"

# El artefacto del dictamen (verbatim de la ficha U3 y de §2.6).
DICTAMEN_ARTIFACT = "plan-review.md"
# El marcador del rechazo sin aprobación (verbatim de PD-14).
APPROVAL_PENDING = "approval pending"
# Las tres banderas de la invocación (verbatim de la ficha U3).
FORM_FLAG = "--object-kind"
COMPANION_PATH_FLAG = "--spec-path"
COMPANION_VERSION_FLAG = "--spec-version"
# Los cuatro campos de la exención (verbatim de §2.7: la forma del registro).
EXEMPTION_FIELDS = ("exempted_by", "delegated", "requested_by", "reason")


# ---------------------------------------------------------------------------
# Anclas semánticas (familias de tokens; nunca prosa completa)
# ---------------------------------------------------------------------------

# Un bloqueante y su condición de cierre.
BLOCKER = re.compile(
    r"\bblock(?:er|ing|ers|ings)\b|\bbloqueantes?\b", re.IGNORECASE
)
RESOLUTION = re.compile(
    r"\bresolv\w*|\bdismiss\w*|\bdiscard\w*|\braz[oó]n\b|"
    r"written reason|\breason\b.{0,20}\bwritten\b|raz[oó]n\s+escrita",
    re.IGNORECASE,
)
# La revisión del borrador (concepto, no etiqueta fija).
REVIEW_WORD = re.compile(r"\breview\w*|\brevisi[oó]n\b", re.IGNORECASE)
DRAFT_WORD = re.compile(r"\bdraft\b|\bborrador\b", re.IGNORECASE)
# La exención y sus decisiones.
EXEMPTION_WORD = re.compile(r"\bexempt\w*|\bexenci[oó]n\b", re.IGNORECASE)
# La revisión (subfase) de la etapa 2: despacho, recepción, ruteo, re-review.
DISPATCH = re.compile(r"\bdispatch\w*|\bdespach\w*|\bprepar\w*", re.IGNORECASE)
RECEIVE = re.compile(r"\breceiv\w*|\brecibid\w*|\brecib\w*", re.IGNORECASE)
VERDICT = re.compile(r"\bverdict\w*|\bdictamen\w*", re.IGNORECASE)
REREVIEW = re.compile(
    r"\bre-?review\b|\bsecond review\b|\bfocused review\b", re.IGNORECASE
)
ROUTE_TO = re.compile(r"\barchitect\b|\bauthorit\w+|\bautoridad\b", re.IGNORECASE)
APPROVAL = re.compile(r"\bapprov\w+", re.IGNORECASE)
# La política de compatibilidad (PD-16(b)).
REVISION = re.compile(r"\brevisi[oó]n\b|\brevision\b", re.IGNORECASE)
INSTRUCTION_SOURCES = re.compile(
    r"\binstruction sources?\b|\bsources? of instruction\b|"
    r"fuentes?\s+de\s+instrucci[oó]n|\binstruction-source\b",
    re.IGNORECASE,
)
NOT_RECEIVABLE = re.compile(
    r"\bnot receivable\b|\bcannot be received\b|\bcan no longer be received\b|"
    r"no\s+es\s+recibible|\bnot be received\b|\bwill not be received\b|"
    r"\brejected\b|\brechazad|\bno longer accepted\b",
    re.IGNORECASE,
)
# Las DOS salidas de la política.
EXIT_SAME_REVISION = re.compile(
    r"\bsame revision\b|\bsame product revision\b|"
    r"\brevision (?:it|that it|which|with which) was published\b|"
    r"\bpublished (?:under|with) (?:the |that |its )?revision\b|"
    r"\bunder the revision (?:it|with which|that)\b|"
    r"\bwith the revision (?:it|that)\b|\bpublished revision\b|"
    r"revisi[oó]n\s+(?:con\s+la\s+que|en\s+la\s+que)\s+se\s+public",
    re.IGNORECASE,
)
EXIT_NEW_CURRENT = re.compile(
    r"\bprepare a (?:new|fresh)\b|\bnew (?:packet|package|one)\b|"
    r"\bcurrent revision\b|\brevision (?:now )?in force\b|"
    r"\bunder the (?:current|present)\b|\bcurrent product revision\b|"
    r"preparar\s+uno\s+nuevo|una?\s+revisi[oó]n\s+vigente",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers (caja negra; archivo faltante = estado conductual)
# ---------------------------------------------------------------------------


def _load(path: Path) -> str:
    """Archivo de procedimiento requerido faltante = estado conductual."""
    if not path.is_file():
        pytest.fail(f"archivo de procedimiento requerido no existe: {path}")
    return path.read_text(encoding="utf-8")


def _sections(text: str) -> list[tuple[str, str]]:
    """(título, cuerpo) por heading: el cuerpo va hasta el siguiente heading.

    El corte es por líneas que empiezan por `#` (el criterio de heading de
    Markdown). No se lleva cuenta de vallas de código: el producto tiene
    vallas desbalanceadas (p. ej. una valla suelta en
    `references/handoff-prompts.md`) y los cuerpos que este RED examina no
    contienen pseudo-headings dentro de vallas.
    """
    out: list[tuple[str, str]] = []
    heading: str | None = None
    body: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            if heading is not None:
                out.append((heading, "\n".join(body)))
            heading = stripped
            body = []
            continue
        if heading is not None:
            body.append(line)
    if heading is not None:
        out.append((heading, "\n".join(body)))
    return out


def _is_draft_review_heading(heading: str) -> bool:
    """True si el título identifica la revisión del borrador (o el dictamen
    que ella produce): `plan-review`, o review + borrador / veredicto."""
    if "plan-review" in heading.lower():
        return True
    return bool(
        DRAFT_WORD.search(heading)
        and (REVIEW_WORD.search(heading) or VERDICT.search(heading))
    )


def _section(text: str, matcher: re.Pattern) -> tuple[str, str] | None:
    """La primera sección cuyo TÍTULO casa con `matcher`."""
    for heading, body in _sections(text):
        if matcher.search(heading):
            return heading, body
    return None


def _near_chars(text: str, first: re.Pattern, second: re.Pattern, radius: int) -> bool:
    """True si algún match de `first` tiene un match de `second` a <= `radius`
    caracteres (el wrapping no rompe la pareja)."""
    for match in first.finditer(text):
        low = max(0, match.start() - radius)
        high = min(len(text), match.end() + radius)
        if second.search(text, low, high):
            return True
    return False


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text)


# ---------------------------------------------------------------------------
# PD-10 — el exit gate de la etapa 2 (O-1)
# ---------------------------------------------------------------------------


def test_pd10_stage2_exit_gate_names_the_dictamen_artifact_and_the_blocker_condition() -> None:
    """PD-10: el exit gate de la etapa 2 declara la evidencia de la revisión.

    O-1: el exit gate nombra el artefacto `plan-review.md` (verbatim de la
    ficha) y la CONDICIÓN DE BLOQUEANTES por vecindad (el bloqueante y su
    cierre: resuelto o descartado con razón escrita).
    """
    text = _load(STAGE2)
    found = _section(text, re.compile(r"(?i)exit\s*gate"))
    assert found is not None, (
        "PD-10: `skills/cdad-cycle/references/stage-2-specification.md` no "
        "tiene un exit gate de la etapa 2."
    )
    heading, body = found
    assert DICTAMEN_ARTIFACT in body, (
        f"PD-10: el exit gate de la etapa 2 ({heading!r}) no nombra el "
        f"artefacto del dictamen `{DICTAMEN_ARTIFACT}`: el gate 2→3 declara "
        "la evidencia de la revisión."
    )
    assert BLOCKER.search(body), (
        f"PD-10: el exit gate de la etapa 2 ({heading!r}) no nombra la "
        "condición de bloqueantes (qué debe pasar con cada bloqueante del "
        "dictamen)."
    )
    assert RESOLUTION.search(body), (
        f"PD-10: el exit gate de la etapa 2 ({heading!r}) no dice cómo se "
        "cierra cada bloqueante (resuelto o descartado con razón escrita)."
    )
    assert _near_chars(body, BLOCKER, RESOLUTION, 400), (
        f"PD-10: en el exit gate de la etapa 2 ({heading!r}) la mención de "
        "los bloqueantes y su condición de cierre no están unidas (vecindad "
        "de 400 caracteres)."
    )


# ---------------------------------------------------------------------------
# PD-10 — la subfase de la revisión de borrador en la etapa 2 (O-2)
# ---------------------------------------------------------------------------


def test_pd10_stage2_declares_the_draft_review_subphase() -> None:
    """PD-10: la etapa 2 declara la subfase de la revisión de borrador.

    O-2: existe una subfase que cubre el recorrido declarado en §2.6 —
    despachar el paquete `plan-review` sobre el borrador, recibir el dictamen,
    rutear sus bloqueantes y hacer la re-review cuando la corrección cambia
    el diseño — y sólo entonces se aprueba.
    """
    text = _load(STAGE2)
    candidates = [
        (heading, body)
        for heading, body in _sections(text)
        if _is_draft_review_heading(heading)
    ]
    assert candidates, (
        "PD-10: la etapa 2 no declara la subfase de la revisión de borrador "
        "(una subfase que nombre la revisión del borrador: `plan-review`, "
        "«draft review», «revisión del borrador»)."
    )
    heading, body = candidates[0]
    assert "plan-review" in _norm(body), (
        f"PD-10: la subfase de la revisión de borrador ({heading!r}) no nombra "
        "el paquete de revisión (`plan-review`) que se despacha sobre el "
        "borrador."
    )
    assert DISPATCH.search(body), (
        f"PD-10: la subfase de la revisión de borrador ({heading!r}) no dice "
        "que se prepara/despacha el encargo de revisión sobre el borrador."
    )
    assert RECEIVE.search(body) and VERDICT.search(body), (
        f"PD-10: la subfase de la revisión de borrador ({heading!r}) no dice "
        "que el dictamen se recibe (el veredicto de la revisión)."
    )
    assert BLOCKER.search(body) and ROUTE_TO.search(body), (
        f"PD-10: la subfase de la revisión de borrador ({heading!r}) no dice "
        "a dónde van los bloqueantes del dictamen (al architect o a la "
        "autoridad que aprueba)."
    )
    assert REREVIEW.search(body), (
        f"PD-10: la subfase de la revisión de borrador ({heading!r}) no "
        "declara la re-review (focal) cuando la corrección cambia el diseño."
    )
    assert APPROVAL.search(body), (
        f"PD-10: la subfase de la revisión de borrador ({heading!r}) no "
        "declara que la aprobación viene DESPUÉS de la revisión."
    )


# ---------------------------------------------------------------------------
# PD-10 — la forma declarada de la exención en la etapa 2 (O-3)
# ---------------------------------------------------------------------------


def test_pd10_stage2_states_the_declared_form_of_the_exemption() -> None:
    """PD-10: en la etapa 2 queda enunciada la forma declarada de la exención.

    O-3: los cuatro campos de la exención (`exempted_by`, `delegated`,
    `requested_by`, `reason` — §2.7) enunciados JUNTOS en el procedimiento de
    la etapa 2, que es su dueño canónico.
    """
    text = _load(STAGE2)
    anchors = list(re.finditer(r"(?i)\bexempted_by\b", text))
    assert anchors, (
        "PD-10: la etapa 2 no enuncia la forma declarada de la exención: "
        "falta el campo `exempted_by` (los cuatro campos: `exempted_by`, "
        "`delegated`, `requested_by`, `reason`)."
    )
    window = 400
    complete = False
    for match in anchors:
        segment = text[max(0, match.start() - window) : match.end() + window]
        if all(re.search(rf"(?i)\b{field}\b", segment) for field in EXEMPTION_FIELDS):
            complete = True
            break
    assert complete, (
        "PD-10: la forma declarada de la exención no aparece completa en la "
        "etapa 2: los cuatro campos (`exempted_by`, `delegated`, "
        "`requested_by`, `reason`) deben enunciarse juntos (ventana de 400 "
        "caracteres)."
    )


# ---------------------------------------------------------------------------
# PD-10 — el gate 2→3 de SKILL.md (O-4) y el mapa del ciclo (O-5)
# ---------------------------------------------------------------------------


def test_pd10_skill_gate_2_to_3_names_the_dictamen_artifact_and_the_blocker_condition() -> None:
    """PD-10: el gate 2→3 de `SKILL.md` declara la evidencia de la revisión.

    O-4: un criterio del gate 2→3 nombra el artefacto `plan-review.md`
    (verbatim de la ficha) y la condición de bloqueantes, por vecindad (espejo
    del gate 4→5).
    """
    text = _load(SKILL_MD)
    found = _section(text, re.compile(r"(?i)gate\s*2"))
    assert found is not None, (
        "PD-10: `skills/cdad-cycle/SKILL.md` no tiene la sección del gate "
        "2→3 (Specification → TDD)."
    )
    heading, body = found
    assert DICTAMEN_ARTIFACT in body, (
        f"PD-10: el gate 2→3 ({heading!r}) no nombra el artefacto del dictamen "
        f"`{DICTAMEN_ARTIFACT}`."
    )
    assert BLOCKER.search(body), (
        f"PD-10: el gate 2→3 ({heading!r}) no nombra la condición de "
        "bloqueantes."
    )
    assert RESOLUTION.search(body), (
        f"PD-10: el gate 2→3 ({heading!r}) no dice cómo se cierra cada "
        "bloqueante (resuelto o descartado con razón escrita)."
    )
    assert _near_chars(body, BLOCKER, RESOLUTION, 400), (
        f"PD-10: en el gate 2→3 ({heading!r}) la mención de los bloqueantes "
        "y su condición de cierre no están unidas (vecindad de 400 "
        "caracteres)."
    )


def test_pd10_skill_cycle_map_names_the_draft_review() -> None:
    """PD-10: el mapa del ciclo nombra la revisión del borrador.

    O-5: la flecha Stage 2→Stage 3 del mapa (hoy rotulada «gate: spec.md
    approved by the user») nombra la revisión del borrador.
    """
    text = _load(SKILL_MD)
    found = _section(text, re.compile(r"(?i)cycle at a glance"))
    assert found is not None, (
        "PD-10: `skills/cdad-cycle/SKILL.md` no tiene el mapa del ciclo "
        "(la sección «The cycle at a glance»)."
    )
    heading, body = found
    stage2 = re.search(r"(?i)stage\s*2[^\n]*", body)
    stage3 = re.search(r"(?i)stage\s*3[^\n]*", body)
    assert stage2 and stage3, (
        f"PD-10: el mapa del ciclo ({heading!r}) no muestra las etapas 2 y 3 "
        "con sus flechas."
    )
    arrow = body[stage2.start() : stage3.start()]
    assert REVIEW_WORD.search(arrow), (
        "PD-10: la flecha Stage 2→Stage 3 del mapa del ciclo no nombra la "
        f"revisión del borrador: {arrow.strip()!r}"
    )
    assert DRAFT_WORD.search(arrow) or "plan-review" in arrow, (
        "PD-10: la flecha Stage 2→Stage 3 del mapa del ciclo no dice que lo "
        f"que se revisa es el borrador: {arrow.strip()!r}"
    )


# ---------------------------------------------------------------------------
# PD-10 — la re-entry del dictamen (O-6)
# ---------------------------------------------------------------------------


def test_pd10_reentry_has_the_draft_verdict_reentry() -> None:
    """PD-10: `re-entry.md` tiene la re-entry del dictamen de borrador.

    O-6: una sección de re-entry para el dictamen de borrador que dice qué
    hacer con él: corregir (resolver sus bloqueantes), re-review focal y la
    exención.
    """
    text = _load(RE_ENTRY)
    candidates = [
        (heading, body)
        for heading, body in _sections(text)
        if _is_draft_review_heading(heading)
    ]
    assert candidates, (
        "PD-10: `skills/cdad-cycle/references/re-entry.md` no tiene la "
        "re-entry del dictamen de borrador (una sección que nombre la "
        "revisión del borrador: `plan-review`, «draft review», «revisión del "
        "borrador»)."
    )
    heading, body = candidates[0]
    assert BLOCKER.search(body), (
        f"PD-10: la re-entry del dictamen ({heading!r}) no dice qué se hace "
        "con sus bloqueantes (corregir / descartar con razón escrita)."
    )
    assert REREVIEW.search(body), (
        f"PD-10: la re-entry del dictamen ({heading!r}) no declara la "
        "re-review (focal) de la corrección."
    )
    assert EXEMPTION_WORD.search(body), (
        f"PD-10: la re-entry del dictamen ({heading!r}) no nombra la "
        "exención (la salida del owner cuando la revisión no se hace)."
    )


# ---------------------------------------------------------------------------
# PD-10 — la plantilla del reviewer (O-7) y su frugalidad (control)
# ---------------------------------------------------------------------------


def test_pd10_handoff_template_declares_the_form_and_the_double_identity_flags() -> None:
    """PD-10: la plantilla del reviewer declara la invocación con la forma y
    la identidad doble.

    O-7: la plantilla de `plan-review` nombra `--object-kind` (la forma),
    `--spec-path` y `--spec-version` (la identidad doble del acompañante).
    """
    text = _load(HANDOFF)
    found = _section(text, re.compile(r"(?i)plan-review"))
    assert found is not None, (
        "PD-10: `skills/cdad-cycle/references/handoff-prompts.md` no tiene la "
        "plantilla del reviewer para la subfase `plan-review`."
    )
    heading, body = found
    for flag in (FORM_FLAG, COMPANION_PATH_FLAG, COMPANION_VERSION_FLAG):
        assert flag in body, (
            f"PD-10: la plantilla del reviewer ({heading!r}) no declara la "
            f"bandera `{flag}` (la forma del objeto y la identidad doble del "
            "acompañante)."
        )


def test_pd10_control_negative_handoff_template_does_not_restate_the_procedure() -> None:
    """PD-10 (control negativo de la ficha U3): la plantilla NO re-enuncia el
    procedimiento.

    CONTROL: verde con el producto en vigor; debe seguir verde después (la
    plantilla sólo DECLARA la invocación; el procedimiento sigue en el
    substage). Operacionalización determinista: la del oráculo vigente
    005-007 PD-12/P5 (quien menciona el conjunto cerrado de valores del
    marcador `detail` tiene que REFERENCIAR la regla o su hogar) más la
    ausencia de las obligaciones verbatim del procedimiento.
    """
    text = _load(HANDOFF)
    found = _section(text, re.compile(r"(?i)plan-review"))
    assert found is not None, (
        "PD-10: `skills/cdad-cycle/references/handoff-prompts.md` no tiene la "
        "plantilla del reviewer para la subfase `plan-review`."
    )
    heading, body = found
    assert "reviewer-plan-review.md" in body, (
        f"PD-10 (control negativo): la plantilla del reviewer ({heading!r}) "
        "no referencia el substage pineado que es el dueño del procedimiento: "
        "debe REFERENCIARLO, no copiarlo."
    )
    norm = _norm(body).lower()
    for obligation in (
        "## abstentions",
        "verdict-tuple",
        "never mark the reviewed draft approved",
    ):
        assert obligation not in norm, (
            f"PD-10 (control negativo): la plantilla del reviewer "
            f"({heading!r}) re-enuncia el procedimiento (contiene "
            f"{obligation!r}): el procedimiento vive en el substage."
        )
    lines = _lines(body)
    if _restates_closed_values(lines):
        assert RULE_REFERENCE.search(body), (
            "PD-10 (control negativo): la plantilla menciona el conjunto "
            "cerrado de valores del marcador `detail` SIN referenciar la "
            "regla o su hogar: sería una segunda copia normativa (oráculo "
            "vigente 005-007 P5)."
        )
    assert not (
        DETAIL_TOKEN.search(body)
        and QUOTED_NEXT.search(body)
        and QUOTED_PLANNED.search(body)
        and "stage-2-specification.md" not in body
    ), (
        "PD-10 (control negativo): la plantilla declara el conjunto cerrado "
        "de valores del marcador `detail` sin apuntar a su hogar canónico."
    )


# ---------------------------------------------------------------------------
# PD-16(b) — la política de compatibilidad y sus dos salidas (O-8)
# ---------------------------------------------------------------------------


def test_pd16b_reentry_declares_the_compatibility_policy_between_revisions() -> None:
    """PD-16(b): `re-entry.md` nombra la política entre revisiones.

    O-8: la declaración dice que un paquete publicado con una revisión de las
    fuentes de instrucción NO es recibible después de que cambien (la
    consecuencia de R-10/D-12: el render canónico es parte de la identidad
    del paquete).
    """
    text = _load(RE_ENTRY)
    assert INSTRUCTION_SOURCES.search(text), (
        "PD-16(b): `re-entry.md` no nombra las fuentes de instrucción (la "
        "política de compatibilidad es sobre ellas)."
    )
    assert REVISION.search(text), (
        "PD-16(b): `re-entry.md` no nombra la revisión del producto (la "
        "política acota la compatibilidad a una revisión)."
    )
    assert NOT_RECEIVABLE.search(text), (
        "PD-16(b): `re-entry.md` no declara la consecuencia: un paquete "
        "publicado antes del cambio no es recibible después."
    )
    assert _near_chars(text, INSTRUCTION_SOURCES, NOT_RECEIVABLE, 1200), (
        "PD-16(b): la declaración de la política no une las fuentes de "
        "instrucción con su consecuencia (vecindad de 1200 caracteres)."
    )


def test_pd16b_reentry_declares_the_two_exits_of_the_compatibility_policy() -> None:
    """PD-16(b): `re-entry.md` nombra las DOS salidas de la política.

    O-8: las dos salidas son (1) terminarlo bajo la revisión con la que se
    publicó y (2) preparar uno nuevo bajo la revisión vigente. Se comprueban
    como dos alternativas de la MISMA declaración (vecindad), no como frases
    exactas.
    """
    text = _load(RE_ENTRY)
    assert EXIT_SAME_REVISION.search(text), (
        "PD-16(b): `re-entry.md` no nombra la primera salida de la política de "
        "compatibilidad: terminarlo bajo la revisión con la que se publicó."
    )
    assert EXIT_NEW_CURRENT.search(text), (
        "PD-16(b): `re-entry.md` no nombra la segunda salida de la política de "
        "compatibilidad: preparar uno nuevo bajo la revisión vigente."
    )
    assert _near_chars(text, EXIT_SAME_REVISION, EXIT_NEW_CURRENT, 1500), (
        "PD-16(b): las dos salidas de la política no están declaradas juntas "
        "(son alternativas de la misma política; vecindad de 1500 caracteres)."
    )


# ---------------------------------------------------------------------------
# PD-10 / PD-14 — los DOS controles negativos, con el proceso real del CLI
# ---------------------------------------------------------------------------


@pytest.fixture()
def disposable_project():
    """Proyecto descartable (política válida, contrato pineado, aprobación
    vigente) con el HOME del subproceso en un tempdir vacío: nunca el HOME
    real, nunca este repo."""
    with tempfile.TemporaryDirectory(prefix="cdad-006-006-u3-home-") as home:
        env = os.environ.copy()
        env["HOME"] = home
        with tempfile.TemporaryDirectory(prefix="cdad-006-006-u3-") as tmp:
            project = PrepareProject(Path(tmp).resolve(), "test-writer", "red")
            yield project, env


def _spec_relpath(project: PrepareProject) -> str:
    state = json.loads(project.state_path.read_text(encoding="utf-8"))
    for entry in state.get("stage_history", []):
        if entry.get("stage") == "specification" and entry.get("contract_path"):
            return entry["contract_path"]
    raise AssertionError("la fixture no trae la entrada de aprobación pineada")


def _vigente_approval(project: PrepareProject) -> dict:
    """La entrada de aprobación `specification` vigente (con su pin)."""
    state = json.loads(project.state_path.read_text(encoding="utf-8"))
    for entry in state.get("stage_history", []):
        if entry.get("stage") == "specification":
            return entry
    raise AssertionError("la fixture no trae la entrada de aprobación")


def test_pd10_control_negative_vigente_approval_without_dictamen_is_not_rejected(
    disposable_project,
) -> None:
    """PD-10 (control negativo (i) de la ficha U3): con aprobación vigente y
    SIN dictamen, el `prepare` de un rol de construcción NO se rechaza.

    Es el caso que DEMUESTRA que el gate 2→3 es SUPERVISADO: el CLI no
    verifica la existencia del dictamen (D-10, §2.6, PD-10). CONTROL: verde
    con el producto en vigor; debe seguir verde después (el gate no se
    convierte en un bloqueo duro del CLI).

    Precondiciones del caso, comprobadas: (a) NO existe `plan-review.md` en
    el proyecto; (b) la aprobación `specification` está vigente y su pin
    coincide con los bytes actuales del contrato.
    """
    project, env = disposable_project
    assert not list(project.root.rglob(DICTAMEN_ARTIFACT)), (
        "PD-10 (control negativo (i)): el proyecto descartable tiene un "
        f"`{DICTAMEN_ARTIFACT}`; el caso es SIN dictamen."
    )
    entry = _vigente_approval(project)
    relpath = _spec_relpath(project)
    contract = project.root / relpath
    assert contract.is_file(), (
        f"PD-10 (control negativo (i)): el contrato pineado no existe: {relpath}"
    )
    import hashlib

    assert entry.get("contract_sha256") == hashlib.sha256(
        contract.read_bytes()
    ).hexdigest(), (
        "PD-10 (control negativo (i)): el pin de la aprobación no coincide con "
        "los bytes actuales del contrato; el caso es una aprobación VIGENTE."
    )

    result = run_prepare(
        PACKET_CLI, *project.args(objective="sonda PD-10 (i)"), env=env
    )
    assert result.returncode == 0, (
        "PD-10 (control negativo (i)): con aprobación vigente y SIN dictamen, "
        "el `prepare` de un rol de construcción debe aceptarse (rc=0): el "
        "gate 2→3 es supervisado y el CLI no verifica la existencia del "
        "dictamen. stderr: " + result.stderr.decode(errors="replace")
    )
    packet_dir = project.out_dir / project.packet_id()
    assert (packet_dir / "PACKET.md").is_file(), (
        "PD-10 (control negativo (i)): el `prepare` aceptado no publicó el "
        "paquete."
    )


def test_pd10_control_negative_without_approval_the_same_prepare_is_rejected(
    disposable_project,
) -> None:
    """PD-10 (control negativo (ii) de la ficha U3) + PD-14: SIN aprobación, el
    mismo `prepare` se rechaza con `approval pending`.

    Es el caso DISTINTO del (i): la aprobación sí es un bloqueo; el dictamen
    no lo es. CONTROL: verde con el producto en vigor; debe seguir verde
    después (PD-14 vigente: la revisión no habilita construir).

    La fixture es la MISMA que en el caso (i) y difiere SÓLO en la entrada de
    aprobación: la diferencia del resultado es atribuible a la aprobación.
    """
    project, env = disposable_project
    state = json.loads(project.state_path.read_text(encoding="utf-8"))
    state["stage_history"] = [
        entry for entry in state.get("stage_history", [])
        if entry.get("stage") != "specification"
    ]
    project.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    result = run_prepare(
        PACKET_CLI, *project.args(objective="sonda PD-10 (ii)"), env=env
    )
    stderr = result.stderr.decode(errors="replace")
    assert result.returncode != 0, (
        "PD-10 (control negativo (ii)): sin aprobación, el `prepare` de un rol "
        "de construcción debe rechazarse (rc≠0); stdout: "
        + result.stdout.decode(errors="replace")
    )
    assert APPROVAL_PENDING in stderr, (
        "PD-10 (control negativo (ii)): el rechazo no nombra el diagnóstico "
        f"`{APPROVAL_PENDING}`: {stderr!r}"
    )
    assert result.stdout == b"", (
        "PD-10 (control negativo (ii)): el rechazo imprimió contenido por "
        "stdout."
    )
    assert list(project.out_dir.iterdir()) == [], (
        "PD-10 (control negativo (ii)): el rechazo publicó algo en el "
        "out-dir."
    )
