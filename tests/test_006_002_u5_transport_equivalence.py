#!/usr/bin/env python3
"""006-002 U5 RED — equivalencia de transporte en `re-entry.md` (PD-5; INV-3/INV-4).

Contract (oráculo — nada se deriva de la implementación):
- ``docs/specs/006-002-delegation-by-layer/spec.md`` §2 **PD-5(a)(b)(c)**,
  §3 **INV-3** (el paquete y el recibo son independientes del transporte: el
  mismo `receive` termina toda ruta) e **INV-4** (`/tmp` no es canal; el recibo
  va a `.cdad/inbox`), §4 **D-4** (la equivalencia de transporte vive en
  `re-entry.md`, enlazada desde §4 y desde cada sección `delegation`).
- ``docs/specs/006-002-delegation-by-layer/plan.md`` ficha **U5** (archivos:
  la nueva subsección de ``references/re-entry.md`` + los enlaces desde §4 y
  desde cada sección `delegation`; regresiones declaradas
  ``tests/test_003_002_t1_receive.py`` y
  ``tests/test_004_003_t5_reentry_equivalence.py``) + **enmienda A-1** (los
  asserts acoplados de la superficie de esta unidad se reformulan en ESTE RED).

PD-5 — «The native receipt is linked». La equivalencia de transporte que el
contrato exige: con delegación nativa el rol devuelve su **FINAL TEXT** en la
sesión del **orquestador**; el orquestador escenifica los **bytes exactos** bajo
``.cdad/inbox`` con su descriptor (``RESULT.json``), **sin retipear, resumir ni
regenerar**; corre ``receive → validate-receipt → materialize → transición``;
recibir **no aprueba nada** (``semantic_status: pending``); y la MISMA ruta vale
para el handoff a chat nuevo y para el adaptador CLI.

Superficie observable (caja negra, la del propio contrato): los documentos
fuente del skill que son el producto publicado de este repo (mismo precedente
declarado por ``tests/test_004_003_t5_reentry_equivalence.py``: cuando el
entregable ES una regla, el doc es el artefacto), el orquestador GENERADO
(staging `basic`, patrón de ``tests/test_006_002_u1_delegation_section.py``) y
el COMPORTAMIENTO del CLI de recibo. El test-writer no leyó implementación
(``skills/``, ``scripts/``, ``sources/``) para derivar aserciones: los oráculos
salen del spec y del plan; el CLI se ejecuta (comportamiento), no se lee.

Marcadores = conceptos con alternativas de idioma (patrón ``require_any`` de
``tests/test_005_010_t3_references.py``/u2), no frases literales, con tres
excepciones normativas que el contrato fija como NOMBRES: ``.cdad/inbox`` (ruta
del inbox, INV-4), ``semantic_status`` (campo del recibo, PD-5/003-002) y
``staged-file`` (el único ``source.kind`` aceptado, PD-5(c)). La forma de la
prosa la verifica el review de stage 4.

Mapa test → postcondición (un test por afirmación observable):

  1 ``TestPd5aTransportEquivalence::test_pd5a_reentry_declares_the_transport_equivalence_route``      PD-5(a)
  2 ``…::test_pd5a_reentry_keeps_the_bytes_verbatim_and_the_receipt_pending``                          PD-5(a)
  3 ``…::test_pd5a_transport_route_is_the_same_for_handoff_and_cli_adapter``                           PD-5(a)
  4 ``TestPd5bMaterializationProtocolLink::test_pd5b_section4_links_to_the_materialization_protocol``  PD-5(b)
  5 ``…::test_pd5b_delegation_sections_link_to_the_materialization_protocol``                          PD-5(b)
  6 ``TestPd5cReceiveStillRequiresStagedFile::test_pd5c_receive_rejects_a_descriptor_with_another_source_kind`` PD-5(c)

RED esperado contra el árbol vigente (U1–U4 en GREEN, U5 sin implementar):

- (1)(2)(3) **FALLAN por AssertionError de CONTENIDO** (OBSERVADO): ``re-entry.md``
  no declara ninguna región de equivalencia de TRANSPORTE (las marcas
  «transporte» + «equivalenc» no co-ocurren en ninguna sección/párrafo; el único
  «equivalencia» del archivo es el de corridas registradas de 004-003, que este
  oráculo discrimina porque exige además el transporte). El fallo es
  AssertionError sobre la región ausente; nunca ImportError.
- (4) **GUARD pre-satisfecho declarado** (OBSERVADO, verde hoy): §4 de
  ``SKILL.md`` ya enlaza al protocolo de materialización — el cierre de §4
  (línea 172) declara «Packet and re-entry are independent of the transport…
  native dispatch, a handoff packet to a new chat, or the extern[al]…» con el
  nombre del protocolo. Lo dejó así el GREEN de U2 (PD-3 punto 7), antes que U5;
  el plan U5 también lo incluía, y por eso este test lo fija como guard.
- (5) **GUARD pre-satisfecho declarado** (OBSERVADO, verde hoy): U1 ya compone el
  enlace en la sección `delegation` de ambos orquestadores generados
  (PD-2(d)/PD-5(b)); este test lo protege contra degradación con un oráculo de
  CO-UBICACIÓN (el enlace debe estar en la región de delegación, no en cualquier
  parte del documento), más estrecho que el de U1.
- (6) **GUARD pre-satisfecho declarado** (OBSERVADO, verde hoy; PD-5(c)):
  `receive` ya rechaza un descriptor con otro ``source.kind`` — fijado por
  comportamiento observable del CLI (dos kinds inválidos, sin finalización, sin
  escritura del árbol), nunca leyendo el código. Es la mitad «la equivalencia de
  transporte no relaja la puerta» (INV-3); su dueño funcional es 003-002.
- Regresiones declaradas de la ficha (sin cambio, verdes): ``test_003_002_t1_receive``
  (PD-5(c) no cambia el comportamiento de `receive`) y
  ``test_004_003_t5_reentry_equivalence`` (U5 AGREGA una subsección a
  ``re-entry.md``; ninguno de los textos que esa regresión fija cambia, así que
  no hay nada que reformular por A-1; se corre como regresión).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Reuso declarado (una sola definición de cada helper/constante, patrón u2→u4):
# la delimitación de secciones numeradas y el oráculo de conceptos de u2; el
# fixture de staging `basic` y las rutas de los orquestadores generados de u1;
# el fixture de paquete disputado/`receive` y su snapshot de árbol de 003-002 T1.
from tests.test_003_002_t1_receive import (
    EstablishedProjectCase,
    err_text,
)
from tests.test_004_002_t2_bootstrap import tree_snapshot
from tests.test_006_002_u1_delegation_section import (
    CC_ORCH_REL,
    OC_ORCH_REL,
    basic_staging_root,
)
from tests.test_006_002_u2_neutral_skill import (
    numbered_section_region,
    require_any,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"
REENTRY = REPO_ROOT / "skills" / "cdad-cycle" / "references" / "re-entry.md"

# ---------------------------------------------------------------------------
# Regiones: la subsección de equivalencia de TRANSPORTE de `re-entry.md`.
# ---------------------------------------------------------------------------

HEADING_SPLIT_RE = re.compile(r"(?m)^#{1,6}[ \t].*$")

# El nombre que el contrato le da a la regla («transport equivalence»,
# PD-5/D-4; plan U5). La región es la que declara LA EQUIVALENCIA y su objeto
# es el TRANSPORTE: la mención suelta de «transporte» junto a otra regla (p. ej.
# la equivalencia de corridas registradas de 004-003) NO localiza esta regla,
# así que ambas marcas se exigen juntas y no hay respaldo por palabra suelta
# (evita un guard falso-verde por texto incidental).
TRANSPORT_RE = re.compile(r"transport|transporte", re.IGNORECASE)
EQUIVALENCE_RE = re.compile(r"equivalenc", re.IGNORECASE)
# Verbos de TRANSFORMACIÓN del resultado y su negación co-ubicada (PD-5(a):
# «sin retipear, resumir ni regenerar» los bytes exactos).
REWRITE_VERB_RE = re.compile(
    r"ret[iy]p|re-?t[iy]p|summar|resum|regener|re-?gener|reescrib|rewrit"
    r"|parafras|transcrib",
    re.IGNORECASE,
)
NEGATION_RE = re.compile(
    r"\b(without|never|nunca|jam[áa]s|sin)\b|\bnot\b|\bno\b",
    re.IGNORECASE,
)


def sections(text: str) -> list[str]:
    """Máximas regiones por encabezado markdown (el texto suelto inicial cuenta
    como una región). El oráculo es indiferente a la jerarquía de la subsección:
    acepta que la regla viva en su propia sección o dentro de otra."""
    return [chunk for chunk in HEADING_SPLIT_RE.split(text) if chunk.strip()]


def paragraphs(text: str) -> list[str]:
    return [para for para in re.split(r"\n\s*\n", text) if para.strip()]


def read(path: Path, why: str) -> str:
    """Artefacto declarado por el contrato: existe y no está vacío."""
    assert path.is_file(), (
        f"{why}: el documento declarado por el contrato no existe (drift de la "
        f"superficie): {path.relative_to(REPO_ROOT).as_posix()}"
    )
    text = path.read_text(encoding="utf-8")
    assert text.strip(), (
        f"{why}: el documento declarado está vacío: "
        f"{path.relative_to(REPO_ROOT).as_posix()}"
    )
    return text


def transport_regions(text: str) -> list[str]:
    """Regiones (secciones + párrafos) que declaran la EQUIVALENCIA de
    TRANSPORTE (ambas marcas juntas). Vacío = la regla no existe."""
    hits: set[str] = set()
    for region in sections(text) + paragraphs(text):
        if TRANSPORT_RE.search(region) and EQUIVALENCE_RE.search(region):
            hits.add(region)
    return sorted(hits)


def require_all(region_text: str, concepts: tuple[tuple[str, tuple[str, ...]], ...],
                where: str) -> None:
    """Todos los conceptos (con alternativas) presentes en la región; el
    mensaje nombra cada ausente (una sola definición, patrón `require_any`)."""
    missing = [
        detail
        for concept, alternatives in concepts
        if (detail := require_any(region_text, alternatives, concept))
    ]
    if missing:
        raise AssertionError(
            f"PD-5(a): {where} no declara el protocolo de transporte completo. "
            f"Conceptos ausentes: {missing}"
        )


# ---------------------------------------------------------------------------
# Conceptos de PD-5(a) — la ruta única de toda entrega (INV-3).
# ---------------------------------------------------------------------------

# (1) delegación NATIVA y su salida: FINAL TEXT en la sesión del ORQUESTADOR.
NATIVE_CONCEPT = (
    ("despacho/delegación nativa", ("native", "nativo")),
    ("texto final del rol en la sesión del orquestador",
     ("final text", "texto final", "final answer", "respuesta final",
      "final output", "salida final", "final message", "mensaje final",
      "orchestrator's session", "orchestrator session",
      "session of the orchestrator", "sesión del orquestador",
      "sesion del orquestador", "sesión del orquestador")),
)

# (2) escenificación de los BYTES EXACTOS bajo `.cdad/inbox` con su descriptor.
STAGING_CONCEPT = (
    ("bytes exactos (sin transformación)",
     ("exact bytes", "byte-identical", "byte for byte", "same bytes",
      "bytes exactos", "byte a byte", "verbatim", "unaltered", "sin alterar",
      "idénticos bytes", "identicos bytes", "identical bytes")),
    ("inbox fijo `.cdad/inbox` (INV-4)", (".cdad/inbox",)),
    ("descriptor del resultado",
     ("descriptor", "result.json", "RESULT.json")),
)

# (3) la cadena de comandos declarada por el contrato.
COMMAND_CONCEPTS = (
    ("`receive`", ("receive", "recibir")),
    ("`validate-receipt`",
     ("validate-receipt", "validate receipt", "validate_receipt",
      "validar el recibo", "validar recibo")),
    ("`materialize`", ("materialize", "materialise", "materializar")),
    ("transición de estado",
     ("transition", "transición", "transicion", "transicionar", "transita")),
)


# ---------------------------------------------------------------------------
# PD-5(a) — equivalencia de transporte declarada en `re-entry.md`
# ---------------------------------------------------------------------------


class TestPd5aTransportEquivalence(unittest.TestCase):
    """PD-5(a)/D-4: ``references/re-entry.md`` declara la equivalencia de
    transporte — la salida del rol delegado llega por una ruta ÚNICA
    (INV-3: el mismo `receive` termina toda ruta) y esa ruta no transforma los
    bytes ni aprueba nada."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(REENTRY, "PD-5(a)")
        cls.regions = transport_regions(cls.text)
        cls.region_text = "\n\n".join(cls.regions)

    def test_pd5a_reentry_declares_the_transport_equivalence_route(self) -> None:
        """PD-5(a): ``re-entry.md`` declara la equivalencia de transporte: el
        despacho nativo devuelve el FINAL TEXT en la sesión del orquestador;
        el orquestador escenifica los BYTES EXACTOS bajo ``.cdad/inbox`` con su
        descriptor y corre ``receive → validate-receipt → materialize →
        transición``."""
        self.assertTrue(
            self.regions,
            msg=(
                "PD-5(a): re-entry.md no declara ninguna región de equivalencia "
                "de TRANSPORTE (el marcador de transporte + el protocolo de "
                "materialización): el recibo nativo queda sin enlazar y cada "
                "ruta re-documenta su propia transcripción. D-4: la regla vive "
                "aquí y §4 / las secciones `delegation` la enlazan."
            ),
        )
        require_all(
            self.region_text,
            NATIVE_CONCEPT + STAGING_CONCEPT + COMMAND_CONCEPTS,
            "la región de equivalencia de transporte de re-entry.md",
        )

    def test_pd5a_reentry_keeps_the_bytes_verbatim_and_the_receipt_pending(
            self) -> None:
        """PD-5(a): la ruta escenifica los bytes EXACTOS sin retipear, resumir
        ni regenerar el resultado del rol; y recibir NO aprueba nada — el
        recibo queda ``semantic_status: pending`` (la aprobación es de la
        revisión, nunca del transporte)."""
        self.assertTrue(
            self.regions,
            msg=(
                "PD-5(a): re-entry.md no declara la equivalencia de transporte "
                "(sin región de transporte no puede exigir el pasaje verbatim "
                "ni el recibo pending)"
            ),
        )
        verbatim = None
        for para in paragraphs(self.region_text):
            if REWRITE_VERB_RE.search(para) and NEGATION_RE.search(para):
                verbatim = para
                break
        self.assertIsNotNone(
            verbatim,
            msg=(
                "PD-5(a): la regla de transporte no prohíbe transformar la "
                "salida del rol — falta la prohibición co-ubicada de "
                "retipear/resumir/regenerar (el orquestador escenifica los "
                "bytes EXACTOS, sin retipear, resumir ni regenerar)"
            ),
        )
        require_all(
            self.region_text,
            (
                ("el recibo no aprueba nada (semantic_status)",
                 ("semantic_status",)),
                ("estado `pending` del recibo",
                 ("pending", "pendiente")),
                ("recibir no aprueba",
                 ("approves nothing", "does not approve", "no approval",
                  "not an approval", "no aprueba", "no aprueban",
                  "aprobación pendiente", "aprobacion pendiente",
                  "no semantic approval", "semantic status stays",
                  "approval stays")),
            ),
            "la región de equivalencia de transporte de re-entry.md",
        )

    def test_pd5a_transport_route_is_the_same_for_handoff_and_cli_adapter(
            self) -> None:
        """PD-5(a)/INV-3: la MISMA ruta vale para el handoff a un chat nuevo y
        para el adaptador CLI — la equivalencia no es una ruta más, es la
        declaración de que el transporte no cambia la entrega."""
        self.assertTrue(
            self.regions,
            msg=(
                "PD-5(a): re-entry.md no declara la equivalencia de transporte "
                "(sin región no puede declarar que la ruta es la misma en todo "
                "transporte)"
            ),
        )
        require_all(
            self.region_text,
            (
                ("handoff a un chat nuevo",
                 ("handoff", "new chat", "new session", "chat nuevo",
                  "nueva sesión", "nueva sesion", "sesión nueva")),
                ("adaptador CLI",
                 ("cli adapter", "cli delegation", "cli-delegation",
                  "cdad_delegate", "adaptador cli",
                  "adaptador de línea de comandos")),
                ("la ruta es la MISMA en todo transporte",
                 ("the same route", "same route", "same path", "same way",
                  "misma ruta", "misma vía", "misma via", "toda ruta",
                  "every route", "applies to both", "por igual",
                  "the same for", "same applies", "idéntica", "identica",
                  "identical route")),
            ),
            "la región de equivalencia de transporte de re-entry.md",
        )


# ---------------------------------------------------------------------------
# PD-5(b) — §4 y las secciones `delegation` enlazan al protocolo
# ---------------------------------------------------------------------------

# El ANCLA del enlace es el destino (protocolo de materialización de
# `re-entry.md`): un enlace debe coincidir con su destino. Se aceptan las
# variantes de idioma de «materialization protocol».
MATERIALIZATION_PROTOCOL_RE = re.compile(
    r"materialization protocol|materialisation protocol|"
    r"protocolo de materializaci[óo]n",
    re.IGNORECASE,
)
DELEGATION_RE = re.compile(r"delegation|delegaci[óo]n", re.IGNORECASE)


class TestPd5bMaterializationProtocolLink(unittest.TestCase):
    """PD-5(b)/D-4: §4 de ``SKILL.md`` Y la sección ``delegation`` de cada
    orquestador generado (staging `basic`) enlazan al «Orchestrator
    materialization protocol» de ``re-entry.md``."""

    def test_pd5b_section4_links_to_the_materialization_protocol(self) -> None:
        """PD-5(b): §4 enlaza al protocolo de materialización (el recibo es la
        salida única de toda ruta).

        GUARD pre-satisfecho declarado (OBSERVADO verde): el GREEN de U2 dejó
        el enlace en el cierre de §4 (punto 7, «packet and re-entry are
        independent of the transport») al neutralizar la sección; el plan U5
        también incluía este enlace, y por eso el test lo fija como guard."""
        text = read(SKILL_MD, "PD-5(b)")
        region = numbered_section_region(text, 4)
        self.assertIsNotNone(
            region,
            msg=(
                "PD-5(b): SKILL.md no expone una §4 delimitable por su encabezado "
                "numerado (el contrato la llama «§4»)"
            ),
        )
        section, first, last = region
        self.assertRegex(
            section,
            MATERIALIZATION_PROTOCOL_RE,
            msg=(
                f"PD-5(b): §4 (líneas {first}-{last}) no enlaza al protocolo de "
                "materialización de re-entry.md (PD-5/D-4: §4 apunta a la regla "
                "única; el orquestador no puede quedar sin el enlace desde el "
                "principio neutral del skill)"
            ),
        )

    def test_pd5b_delegation_sections_link_to_the_materialization_protocol(
            self) -> None:
        """PD-5(b)/INV-3: la sección ``delegation`` de CADA orquestador
        generado (staging `basic`) enlaza al protocolo de materialización —
        co-ubicada en su propia región de delegación, no perdida en el resto
        del documento.

        GUARD pre-satisfecho declarado (U1 compone el enlace, PD-2(d)/PD-5(b));
        este test protege el GREEN contra degradación con un oráculo de
        co-ubicación más estrecho que el de U1."""
        root = basic_staging_root()
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            label = rel.parent.parent.name + "/" + rel.parent.name
            with self.subTest(orchestrator=label):
                path = root / rel
                self.assertTrue(
                    path.is_file(),
                    msg=f"PD-5(b): falta el orquestador generado {label} en el "
                        "staging `basic` (fixture de U1)",
                )
                text = path.read_text(encoding="utf-8")
                linked = [
                    section
                    for section in sections(text)
                    if DELEGATION_RE.search(section)
                    and MATERIALIZATION_PROTOCOL_RE.search(section)
                ]
                self.assertTrue(
                    linked,
                    msg=(
                        f"PD-5(b): la sección `delegation` de {label} no enlaza "
                        "al protocolo de materialización de re-entry.md "
                        "(D-4: cada sección `delegation` enlaza; INV-3: el "
                        "mismo `receive` termina toda ruta)"
                    ),
                )


# ---------------------------------------------------------------------------
# PD-5(c) — `receive` sigue aceptando solo partes escenificadas
# ---------------------------------------------------------------------------


class TestPd5cReceiveStillRequiresStagedFile(EstablishedProjectCase):
    """PD-5(c)/INV-3: la equivalencia de transporte NO relaja la puerta de
    entrada del recibo: `receive` sigue aceptando solo partes escenificadas
    (``source.kind="staged-file"``). Se verifica por COMPORTAMIENTO observable
    del CLI (un descriptor con otro ``source.kind`` se rechaza), nunca leyendo
    el código del helper."""

    def test_pd5c_receive_rejects_a_descriptor_with_another_source_kind(
            self) -> None:
        """PD-5(c): un descriptor con ``source.kind`` distinto de
        ``staged-file`` se rechaza — rc≠0, stdout vacío, sin receipt ni
        directorio final, sin escritura del árbol, con diagnóstico por stderr.

        GUARD pre-satisfecho declarado: el comportamiento ya existe (dueño
        funcional 003-002 T1); el test lo fija aquí porque PD-5(c) lo declara
        observable de U5 y porque es la mitad «la ruta no relaja la puerta» de
        INV-3."""
        for kind in ("sdk-message", "inline-text"):
            with self.subTest(source_kind=kind):
                self.new_dispatched_project()
                parts = self.write_staged_parts()
                self.assertTrue(
                    all(parts.values()),
                    msg="precondición (fixture): todos los parts tienen bytes",
                )
                self.write_manifest(changes=[])
                doc = self.build_descriptor(
                    parts=parts, observed=self.observed_changes())
                doc["source"] = {
                    "kind": kind,
                    "sdk_message_ref": "msg-006-002-u5",
                }
                descriptor = self.write_descriptor(doc)
                before_tree = tree_snapshot(self.root)

                proc = self.run_receive(descriptor)
                err = err_text(proc)
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=(
                        f"PD-5(c): `receive` debe rechazar un descriptor con "
                        f"`source.kind={kind!r}` (solo `staged-file` es una "
                        f"parte escenificada); rc={proc.returncode}"
                    ),
                )
                # RED inválida: el rechazo no puede venir de un CLI ausente o de
                # un argv mal formado.
                self.assertNotIn(
                    "No such file or directory", err,
                    msg=(
                        f"PD-5(c) ({kind}): RED inválida — el rechazo es por CLI "
                        "ausente, no por el comportamiento bajo prueba"
                    ),
                )
                self.assertNotIn(
                    "unrecognized arguments", err,
                    msg=(
                        f"PD-5(c) ({kind}): RED inválida — el rechazo es por argv "
                        "mal formado, no por la puerta `staged-file`"
                    ),
                )
                self.assertNotIn(
                    "Traceback", err,
                    msg=f"PD-5(c) ({kind}): el rechazo terminó con traceback",
                )
                self.assertEqual(
                    proc.stdout, b"",
                    msg=(
                        f"PD-5(c) ({kind}): un rechazo no publica evidencia por "
                        "stdout (no hay receipt parcial)"
                    ),
                )
                self.assertFalse(
                    self.receipt_path().exists(),
                    msg=f"PD-5(c) ({kind}): el rechazo dejó un receipt final",
                )
                self.assertFalse(
                    self.final_dir().is_dir(),
                    msg=f"PD-5(c) ({kind}): el rechazo dejó el directorio final",
                )
                self.assertEqual(
                    tree_snapshot(self.root), before_tree,
                    msg=(
                        f"PD-5(c) ({kind}): el rechazo escribió el árbol "
                        "(receive no publica resultados fuera del store "
                        "operacional y no materializa nada)"
                    ),
                )
                self.assertTrue(
                    err.strip(),
                    msg=(
                        f"PD-5(c) ({kind}): el rechazo no proporcionó "
                        "diagnóstico por stderr"
                    ),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
