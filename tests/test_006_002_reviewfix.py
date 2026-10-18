#!/usr/bin/env python3
"""006-002 review-fix RED — hallazgo B-1: alias de modelo de un runtime y
gateway de un despliegue concreto en el texto instalable de la skill
(PD-1/INV-2).

Contract:
- ``docs/specs/006-002-delegation-by-layer/spec.md`` §2 **PD-1** («No
  installable skill text (``skills/cdad-cycle/**``, ``skills/cdad-epic/**``)
  names a runtime dispatch tool or **a concrete model in a delegation
  context**»), §3 **INV-2** («No installable text fixes models in a delegation
  context; the model is the configured one»).
- ``docs/specs/006-002-delegation-by-layer/review.md`` hallazgo **B-1**
  (Required · BLOCKING · bucket m): ``skills/cdad-cycle/references/sub-agent-
  strategies.md:51`` (*"``model:`` accepts aliases (``haiku``, ``sonnet``,
  ``opus``, ``fable``) or a full model ID — there is no ``mofgw`` gateway"*)
  nombra alias de modelo de Claude Code **y** un gateway interno, y **escapa**
  al oráculo de PD-1: los alias desnudos no son identificadores concretos
  (``CONCRETE_MODEL_ID_RE`` exige familia + guion; ``SPACED_MODEL_LINE_RE``
  exige el dígito pegado al alias) y ``mofgw`` no está en ``PROVIDER_RE``
  (verificado por sonda directa en el review).
- Condición de cierre verificable declarada por B-1: reescribir
  ``sub-agent-strategies.md:51`` en el estilo ya usado en ``:53`` (el modelo
  vive en el orquestador generado / la configuración del runtime), quitando los
  alias y el gateway; **capturarlo en un RED que extienda el oráculo de PD-1**
  (p.ej. un patrón de alias desnudo) para que la conservación sea observable;
  foco U2+U4 en verde con el oráculo nuevo. Cubierto por:
  ``grep -RniE '\\bhaiku\\b|\\bsonnet\\b|\\bopus\\b|\\bfable\\b|mofgw' skills/`` → 0.

Este focal EXTIENDE el oráculo de PD-1/INV-2 — una sola definición de la
superficie instalable y de los patrones base (``scanned_documents``/
``model_offences``/``TOOL_FORM_EXCLUSIONS`` de
``tests/test_006_002_u2_neutral_skill.py``; no se copian) — con la clase que
B-1 señaló:
- **alias de modelo de un runtime** (frontera que el contrato PD-1 fija: solo es
  ofensor en **contexto de modelo/delegación**, y ese contexto se acota a la
  MISMA línea — «opus» en otra acepción (p.ej. «magnum opus», una obra) no
  cuenta: el contrato dice «a concrete model in a delegation context», no la
  palabra suelta);
- **nombre de gateway/proveedor de un DESPLIEGUE concreto** (``mofgw``), valor
  de despliegue que INV-2/INV-7 ya prohíben en texto instalable.
``references/context-meter.md`` **sigue excluido** (INV-8: contrato de
LECTOR/MEDICIÓN con dueño declarado).

Mapa test → postcondición (un test por afirmación observable):
  1 ``TestB1OracleSelfCheck::test_b1_oracle_flags_bare_alias_in_model_context``   PD-1/INV-2 (B-1) — guard del oráculo
  2 ``TestB1OracleSelfCheck::test_b1_oracle_ignores_alias_outside_model_context`` PD-1/INV-2 (B-1) — anti-falso-positivo
  3 ``TestB1OracleSelfCheck::test_b1_oracle_flags_deployment_gateway_token``      PD-1/INV-2 (B-1) — guard del oráculo
  4 ``TestPd1Inv2B1NoRuntimeModelDetail::test_pd1_inv2_no_bare_runtime_model_alias_or_concrete_gateway_in_installable_skill_text`` PD-1/INV-2 (B-1)

RED esperado (árbol actual — B-1 sin implementar):
- (1)/(2)/(3): PASAN — autocontrol del oráculo sobre texto sintético; no tocan
  el producto (declarado: son guardas del propio oráculo, no del árbol).
- (4): FALLA por AssertionError de CONTENIDO: el texto instalable sigue
  nombrando los alias ``haiku``/``sonnet``/``opus``/``fable`` y el gateway
  ``mofgw`` en ``sub-agent-strategies.md:51`` (la línea que B-1 cita), porque
  el oráculo base (``model_offences``) no los captura.
Ningún fallo es ImportError/SyntaxError.
"""

from __future__ import annotations

import re
import unittest

# Reuso declarado (spec §2, una sola definición): superficie instalable,
# oráculo de modelos base, exclusión de LECTOR (INV-8) y utilidades — de U2.
from tests.test_006_002_u2_neutral_skill import (
    REPO_ROOT,
    TOOL_FORM_EXCLUSIONS,
    model_offences,
    read,
    relative,
    scanned_documents,
)

# Documento que el hallazgo B-1 cita (review.md B-1): su presencia en la
# superficie escaneada se declara (guard de drift del oráculo), su línea exacta
# NO se fija (número = detalle de implementación; el contrato es de ausencia).
B1_DOCUMENT = (REPO_ROOT / "skills" / "cdad-cycle" / "references"
               / "sub-agent-strategies.md")

# --------------------------------------------------------------------------
# PD-1/INV-2 (B-1) — patrones de la clase que escapaba al oráculo
# --------------------------------------------------------------------------

# Alias de modelo de un runtime (Claude Code nombra sus familias por alias
# desnudo): ``haiku``, ``sonnet``, ``opus``, ``fable``. Es la forma que
# ``SPACED_MODEL_LINE_RE`` (005-010: ``<alias><dígito>``) NO captura — motivo del
# escape de B-1. La palabra suelta fuera de contexto de modelo NO es ofensor.
RUNTIME_MODEL_ALIAS_RE = re.compile(r"(?i)\b(?:haiku|sonnet|opus|fable)\b")

# Marcador de contexto de modelo/delegación en la MISMA línea: acota el alias a
# la frontera que fija PD-1 («a concrete model in a delegation context»). Cubre
# `model:`/«model»/«modelo», delegación/«delegate» y «sub-agent»/«subagent».
MODEL_CONTEXT_MARKER_RE = re.compile(
    r"(?i)(?:\bmodel\w*|\bdelegat\w*|\bsub[- ]?agent\w*)"
)

# Nombre de gateway/proveedor de un DESPLIEGUE concreto (INV-2/INV-7): el
# gateway interno que el hallazgo B-1 nombra en ``sub-agent-strategies.md:51``.
# Es un valor de despliegue, no un identificador de modelo: se prohíbe en
# cualquier contexto del texto instalable (como los proveedores de ``PROVIDER_RE``).
DEPLOYMENT_GATEWAY_TOKENS = ("mofgw",)
DEPLOYMENT_GATEWAY_RE = re.compile(
    r"(?i)\b(?:" + "|".join(re.escape(token)
                            for token in DEPLOYMENT_GATEWAY_TOKENS) + r")\b"
)


def runtime_model_detail_offences(text: str) -> list[str]:
    """Oráculo de PD-1/INV-2 extendido por B-1: el base (``model_offences``, una
    sola definición en U2) MÁS la clase que escapaba — alias de modelo de un
    runtime en contexto de modelo/delegación (misma línea) y gateway de un
    despliegue concreto. Sin duplicar los patrones base."""
    found = list(model_offences(text))
    for number, line in enumerate(text.splitlines(), start=1):
        if not MODEL_CONTEXT_MARKER_RE.search(line):
            continue
        for match in RUNTIME_MODEL_ALIAS_RE.finditer(line):
            found.append(
                "alias de modelo de un runtime en contexto de "
                f"modelo/delegación: {match.group(0)!r} (línea {number})"
            )
    for number, line in enumerate(text.splitlines(), start=1):
        for match in DEPLOYMENT_GATEWAY_RE.finditer(line):
            found.append(
                "nombre de gateway/proveedor de un despliegue concreto: "
                f"{match.group(0)!r} (línea {number})"
            )
    return found


# --------------------------------------------------------------------------
# Autocontrol del oráculo (el oráculo se prueba a sí mismo: ni ciego ni bobo)
# --------------------------------------------------------------------------


class TestB1OracleSelfCheck(unittest.TestCase):
    """Guardas del propio oráculo B-1 sobre texto sintético: captura la clase
    prohibida (alias desnudo en contexto de modelo; gateway de despliegue) y NO
    genera falsos positivos en prosa (alias en otra acepción)."""

    def test_b1_oracle_flags_bare_alias_in_model_context(self) -> None:
        """PD-1/INV-2 (B-1): una línea de contexto de modelo que nombra un alias
        desnudo ES ofensora (es exactamente la forma de ``:51`` que el oráculo
        base dejaba pasar)."""
        text = ("`model:` accepts aliases (`haiku`, `sonnet`, `opus`, `fable`) "
                "or a full model ID.")
        offenders = runtime_model_detail_offences(text)
        self.assertTrue(
            offenders,
            msg=("oráculo B-1 ciego: un alias de modelo desnudo en contexto de "
                 "modelo (`model:`) no fue capturado — retrocedió al defecto "
                 "que B-1 denunció"),
        )
        for alias in ("haiku", "sonnet", "opus", "fable"):
            self.assertTrue(
                any(alias in offence for offence in offenders),
                msg=f"oráculo B-1 ciego: el alias {alias!r} en contexto de modelo no fue capturado",
            )

    def test_b1_oracle_ignores_alias_outside_model_context(self) -> None:
        """PD-1/INV-2 (B-1): un alias en OTRA acepción, sin contexto de modelo/
        delegación en la línea, NO es ofensor (prosa legítima; el contrato acota
        a «a concrete model in a delegation context»)."""
        for prose in (
            "A magnum opus of methodology: the skill is a neutral template.",
            "The fable of the two runtimes illustrates layering.",
            "Haiku as a poetic form predates the runtime.",
        ):
            self.assertEqual(
                runtime_model_detail_offences(prose), [],
                msg=(
                    "oráculo B-1 con falso positivo en prosa (alias en otra "
                    f"acepción, sin contexto de modelo): {prose!r}"
                ),
            )

    def test_b1_oracle_flags_deployment_gateway_token(self) -> None:
        """PD-1/INV-2 (B-1): el nombre de un gateway de despliegue concreto ES
        ofensor en cualquier contexto del texto instalable."""
        text = "there is no `mofgw` gateway"
        offenders = runtime_model_detail_offences(text)
        self.assertTrue(
            any("mofgw" in offence for offence in offenders),
            msg=("oráculo B-1 ciego: el gateway de despliegue concreto `mofgw` "
                 "no fue capturado"),
        )


# --------------------------------------------------------------------------
# PD-1/INV-2 (B-1) — el árbol instalable no nombra alias de modelo de runtime
# ni gateway de despliegue concreto
# --------------------------------------------------------------------------


class TestPd1Inv2B1NoRuntimeModelDetail(unittest.TestCase):
    """PD-1/INV-2 (B-1): ningún texto instalable de ``skills/cdad-cycle/**`` y
    ``skills/cdad-epic/**`` nombra un alias de modelo de un runtime en contexto
    de modelo/delegación ni el nombre de un gateway de despliegue concreto,
    salvo la única exclusión con dueño (``context-meter.md``, INV-8)."""

    def test_pd1_inv2_no_bare_runtime_model_alias_or_concrete_gateway_in_installable_skill_text(self) -> None:
        """PD-1/INV-2 (B-1): ausencia de alias de modelo de runtime en contexto
        de modelo/delegación (``haiku``/``sonnet``/``opus``/``fable``) y de
        gateways de despliegue concretos (``mofgw``) en el texto instalable de
        la skill."""
        documents = scanned_documents(TOOL_FORM_EXCLUSIONS)
        self.assertGreater(
            len(documents), 0,
            msg=("drift del oráculo B-1: no se recolectó ningún documento "
                 "instalable bajo skills/cdad-cycle/** ni skills/cdad-epic/**"),
        )
        self.assertIn(
            B1_DOCUMENT, documents,
            msg=(f"drift del oráculo B-1: el documento que el hallazgo cita no "
                 f"está en la superficie escaneada: {relative(B1_DOCUMENT)}"),
        )

        offenders: list[str] = []
        for path in documents:
            text = read(path)
            for offence in runtime_model_detail_offences(text):
                offenders.append(f"{relative(path)} — {offence}")

        self.assertEqual(
            offenders, [],
            msg=(
                "PD-1/INV-2 (B-1): el texto instalable de la skill nombra alias "
                "de modelo de un runtime (en contexto de modelo/delegación) o "
                "un gateway de despliegue concreto — el modelo de cada rol es el "
                "configurado en el runtime y la skill no nombra gateways: "
                f"{offenders[:20]!r}"
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
