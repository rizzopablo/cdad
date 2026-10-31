#!/usr/bin/env python3
"""010-003 RED — piloto documental: corpus, inventario y control estructural.

Contrato: ``docs/specs/010-003-documentary-pilot/spec.md`` (v5, sha256
``f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5``), §2.4
(corpus y localizadores) y §3 Promesas A, B y D (PC-01, PC-04, PC-05, PC-06,
PC-10) más INV-06 (``spec.md:211``). Plan aprobado v6, tarea T3
(``plan.md:90-164``), que entrega a T4 la convención de citación ya fijada.
AUDIT aprobado: ``test-audit.md`` §2 (ocho controles focales). POST-AUDIT:
``post-audit.md`` §2-§3 (precisiones de fixtures y composición del RED).

Mapeo test → promesa → postcondiciones (un test por consecuencia observable;
la trazabilidad múltiple es deliberada, no una cuota por postcondición):

  T1 ``test_broken_locator_is_rejected_with_document_reference_and_cause``
      Promesa B — PC-04
  T2 ``test_corrected_locator_is_accepted_and_the_pair_differs_only_in_the_locator``
      Promesa B — PC-05
  T3 ``test_semantically_defective_candidate_is_structurally_accepted``
      Promesa B — PC-06, solo la fracción estructural (límite C-2)
  T4 ``test_product_with_no_references_is_rejected``
      §2.4:111 + ``spec.md:137`` — rechazo del verde vacío
  T5 ``test_product_citing_an_uninventoried_source_is_rejected``
      §2.4:111 — frontera de autorización
  T6 ``test_the_product_cites_only_inventoried_fragments_and_at_least_one``
      Promesa D — PC-10, fracción estructural
  T7 ``test_inventory_accounts_for_every_source_with_matching_digest_and_declares_synthetic_origin``
      Promesa A — PC-01 + §2.4:95-109
  T8 ``test_control_verdict_is_invariant_under_rewrap_of_the_examined_document``
      §2.2:44 + INV-06 (``spec.md:211``)

Sin consecuencia nombrada no hay control: los ocho protegen resultados que el
usuario del piloto observa (rechazo con diagnóstico, aceptación de la muestra
corregida, resolubilidad del candidato, verde no vacío, inventario íntegro,
producto trazable e invariancia al rewrap). PC-02, PC-03, PC-07..PC-09 y
PC-11..PC-15 quedan en ejecución real con evidencia recuperable (AUDIT §1 y
§7): no se automatizan aquí ni se simulan.

Límites declarados (no deuda oculta):

- El control comprueba resolubilidad estructural: **no** decide si un
  fragmento sostiene semánticamente una afirmación (``spec.md:113``).
- La clave de contraste no es lectura de ningún control (``spec.md:82,186``;
  ``plan.md:126``): comparar contra ella pertenece al contraste del
  orquestador. Los mensajes y valores de aserción no reproducen su contenido.
- Ningún control depende de números de línea, de un veredicto textual de un
  informe ni de un parser universal: solo interpreta la convención fijada en
  ``spec.md:102-109``.
- RED de este módulo: T1-T5, T7 y T8 se crean verdes (operan sobre fixtures
  que construye el test-writer) y T6 falla por ``AssertionError`` de producto
  inexistente (``plan.md:151-152``); nunca por ``ImportError`` ni
  ``FileNotFoundError``.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
FIXTURES = TESTS_DIR / "fixtures" / "010_003_documentary_pilot"
INVENTORY = FIXTURES / "sources" / "inventory.md"
NEGATIVE = FIXTURES / "challenge" / "negative.md"
BROKEN = FIXTURES / "structural" / "broken.md"
CORRECTED = FIXTURES / "structural" / "corrected.md"
NO_REFERENCES = FIXTURES / "structural" / "no-references.md"
UNINVENTORIED = FIXTURES / "structural" / "uninventoried.md"
PRODUCT = (
    REPO_ROOT / "docs" / "specs" / "010-003-documentary-pilot" / "product"
    / "relevamiento.md"
)

INVENTORY_ID = "inventory-010-003-v1"

# Convención fijada por la spec §2.4: tabla del inventario y anclas explícitas.
INVENTORY_ROW_RE = re.compile(
    r"^\|\s*(s\d+)\s*\|\s*(\S+)\s*\|\s*([0-9a-f]{64})\s*\|\s*$",
    re.MULTILINE,
)
ANCHOR_LINE_RE = re.compile(r'^<a id="(s[12])-f(\d{2})"></a>$', re.MULTILINE)
ANCHOR_EXACT_RE = re.compile(r'^<a id="s(1|2)-f(\d{2})"></a>$')
ANCHOR_UNIT_RE = re.compile(r"<a\b[^>]*></a>")
ANCHOR_OPEN_RE = re.compile(r"<a\b")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
URL_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


@dataclass(frozen=True)
class Diagnostic:
    """Un rechazo del control: documento examinado, referencia y causa."""

    document: str
    reference: str
    cause: str


@dataclass(frozen=True)
class Verdict:
    """Resultado del control sobre un documento: veredicto y diagnósticos."""

    accepted: bool
    diagnostics: tuple[Diagnostic, ...]


# ---------------------------------------------------------------------------
# Control estructural acotado (artefacto de tests/, no interfaz de producto)
# ---------------------------------------------------------------------------


def load_inventory(inventory_path: Path = INVENTORY) -> tuple[str, dict]:
    """Devuelve el texto del inventario y sus filas {id: (ruta, sha256)}."""
    text = Path(inventory_path).read_text(encoding="utf-8")
    rows = {}
    for source_id, relative_path, digest in INVENTORY_ROW_RE.findall(text):
        rows[source_id] = (relative_path, digest)
    return text, rows


def source_anchors(source_path: Path) -> list[str]:
    """Anclas registradas en una fuente, como identificadores ``s1-f01``."""
    text = Path(source_path).read_text(encoding="utf-8")
    return [
        "{}-f{}".format(match.group(1), match.group(2))
        for match in ANCHOR_LINE_RE.finditer(text)
    ]


def citations(text: str) -> list[str]:
    """Referencias locales a archivos, en el orden en que aparecen.

    Un enlace absoluto con esquema o un ancla interna del propio documento no
    es una cita a una fuente del corpus y no se interpreta.
    """
    targets = []
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = match.group(1)
        if target.startswith("#") or URL_SCHEME_RE.match(target):
            continue
        targets.append(target)
    return targets


def _resolve_target(reference: str, examined_path: Path) -> Path:
    path_part = reference.split("#", 1)[0]
    return Path(os.path.normpath(Path(examined_path).parent / path_part)).resolve()


def _resolution_index(corpus_root: Path, inventory_path: Path):
    """Índice {ruta resuelta: identificador} y {identificador: anclas}."""
    corpus_root = Path(corpus_root).resolve()
    _text, inventory = load_inventory(inventory_path)
    by_path = {}
    anchors = {}
    for source_id, (relative_path, _digest) in inventory.items():
        by_path[
            Path(os.path.normpath(corpus_root / relative_path)).resolve()
        ] = source_id
        anchors[source_id] = set(
            source_anchors(corpus_root / relative_path)
        )
    return by_path, anchors


def run_control(
    examined_path: Path,
    corpus_root: Path = FIXTURES,
    inventory_path: Path = INVENTORY,
) -> Verdict:
    """Comprueba que las referencias del documento resuelven a fuentes y anclas.

    Causas posibles: ``no_reference`` (el documento no cita ninguna fuente),
    ``uninventoried_source`` (la referencia no resuelve a una fuente de la
    tabla del inventario) y ``missing_fragment`` (la fuente está inventariada
    pero el fragmento citado no está registrado en ella).
    """
    examined_path = Path(examined_path).resolve()
    corpus_root = Path(corpus_root).resolve()
    by_path, anchors = _resolution_index(corpus_root, inventory_path)
    document = os.path.relpath(examined_path, corpus_root)
    targets = citations(examined_path.read_text(encoding="utf-8"))
    if not targets:
        return Verdict(False, (Diagnostic(document, "", "no_reference"),))
    diagnostics = []
    for target in targets:
        source_id = by_path.get(_resolve_target(target, examined_path))
        if source_id is None:
            diagnostics.append(Diagnostic(document, target, "uninventoried_source"))
            continue
        fragment = target.split("#", 1)[1] if "#" in target else ""
        if not fragment or fragment not in anchors.get(source_id, set()):
            diagnostics.append(Diagnostic(document, target, "missing_fragment"))
    return Verdict(not diagnostics, tuple(diagnostics))


def resolved_citations(
    examined_path: Path,
    corpus_root: Path = FIXTURES,
    inventory_path: Path = INVENTORY,
) -> list[tuple[str, str]]:
    """Citas que resuelven a una fuente inventariada y a un ancla registrada."""
    examined_path = Path(examined_path).resolve()
    corpus_root = Path(corpus_root).resolve()
    by_path, anchors = _resolution_index(corpus_root, inventory_path)
    resolved = []
    for target in citations(examined_path.read_text(encoding="utf-8")):
        source_id = by_path.get(_resolve_target(target, examined_path))
        fragment = target.split("#", 1)[1] if "#" in target else ""
        if source_id is not None and fragment in anchors.get(source_id, set()):
            resolved.append((source_id, fragment))
    return resolved


# ---------------------------------------------------------------------------
# Derivación del rewrap para T8
# ---------------------------------------------------------------------------

INLINE_LINK_RE = re.compile(r"\[[^\]]*\]\([^)\s]+\)")
STRUCTURAL_PREFIXES = ("#", "-", "|", "<a ", "**")


def _protect_links(block: str) -> tuple[str, dict]:
    tokens = {}

    def _replace(match: re.Match) -> str:
        token = "<<LINK{}>>".format(len(tokens))
        tokens[token] = match.group(0)
        return token

    return INLINE_LINK_RE.sub(_replace, block), tokens


def rewrap_markdown(text: str, width: int) -> str:
    """Re-envuelve los párrafos conservando encabezados, anclas y enlaces.

    Cambia dónde termina cada línea sin cambiar el contenido ni romper los
    enlaces: es la transformación que distingue un control por identificadores
    internos de uno por ventanas de línea.
    """
    blocks = []
    for block in text.split("\n\n"):
        stripped = block.strip("\n")
        if not stripped:
            continue
        first_line = stripped.split("\n", 1)[0]
        if first_line.startswith(STRUCTURAL_PREFIXES):
            blocks.append(stripped)
            continue
        protected, tokens = _protect_links(stripped)
        joined = " ".join(line.strip() for line in protected.split("\n"))
        wrapped = textwrap.wrap(
            joined, width=width, break_long_words=False, break_on_hyphens=False
        )
        rendered = "\n".join(wrapped) if wrapped else ""
        for token, link in tokens.items():
            rendered = rendered.replace(token, link)
        blocks.append(rendered)
    return "\n\n".join(blocks) + "\n"


# ---------------------------------------------------------------------------
# T1-T5 — comportamiento del control sobre las muestras estructurales
# ---------------------------------------------------------------------------


def test_broken_locator_is_rejected_with_document_reference_and_cause():
    """PC-04: un fragmento citado inexistente se rechaza con diagnóstico.

    Consecuencia: sin este control, el usuario recibiría un verde sobre una
    cita que no localiza nada en el corpus.
    """
    verdict = run_control(BROKEN)

    assert verdict.accepted is False, (
        "una cita a un fragmento inexistente debe rechazarse; el control "
        "aceptó la muestra rota"
    )
    assert len(verdict.diagnostics) == 1, (
        "se esperaba un único diagnóstico para la muestra rota: {!r}".format(
            verdict.diagnostics
        )
    )
    diagnostic = verdict.diagnostics[0]
    assert diagnostic.document == "structural/broken.md", (
        "el diagnóstico debe identificar el documento examinado: {!r}".format(
            diagnostic
        )
    )
    assert diagnostic.reference == "../sources/s1.md#s1-f99", (
        "el diagnóstico debe identificar la referencia problemática tal como "
        "está escrita: {!r}".format(diagnostic)
    )
    assert diagnostic.cause == "missing_fragment", (
        "la causa del rechazo debe ser el fragmento inexistente: {!r}".format(
            diagnostic
        )
    )


def test_corrected_locator_is_accepted_and_the_pair_differs_only_in_the_locator():
    """PC-05: corregido el localizador, y solo él, la muestra se acepta.

    Consecuencia: sin este control, el usuario no sabría si la aceptación se
    debe a la corrección del localizador o a que se relajó todo lo demás.
    """
    verdict = run_control(CORRECTED)

    assert verdict.accepted is True, (
        "la muestra con el localizador corregido debe aceptarse: {!r}".format(
            verdict.diagnostics
        )
    )
    assert verdict.diagnostics == (), (
        "la muestra aceptada no debe producir diagnósticos: {!r}".format(
            verdict.diagnostics
        )
    )

    broken_text = BROKEN.read_text(encoding="utf-8")
    corrected_text = CORRECTED.read_text(encoding="utf-8")
    assert broken_text != corrected_text, (
        "las muestras rota y corregida no pueden ser el mismo texto"
    )
    assert broken_text.count("#s1-f99") == 1, (
        "el localizador inexistente debe aparecer exactamente una vez en la "
        "muestra rota"
    )
    assert corrected_text.count("#s1-f99") == 0, (
        "la muestra corregida no debe conservar el localizador inexistente"
    )
    assert broken_text.replace("#s1-f99", "#s1-f03") == corrected_text, (
        "las muestras deben diferir solo en el localizador corregido; "
        "cualquier otra diferencia anularía la equivalencia de PC-05"
    )


def test_semantically_defective_candidate_is_structurally_accepted():
    """PC-06: el candidato negativo tiene referencias estructuralmente resolubles.

    Este control acredita **resolubilidad**, NO que persistan los tres
    defectos del candidato (límite C-2): la persistencia se acredita con la
    clave y el contraste posterior, que no son lectura de este verificador.
    """
    verdict = run_control(NEGATIVE)

    assert verdict.accepted is True, (
        "el candidato negativo debe ser estructuralmente resoluble; este "
        "verde acredita resolubilidad de las citas, no la persistencia de "
        "los tres defectos (C-2) — diagnósticos: {!r}".format(
            verdict.diagnostics
        )
    )
    assert verdict.diagnostics == (), (
        "el candidato no debe producir diagnósticos estructurales: {!r}".format(
            verdict.diagnostics
        )
    )
    resolved = resolved_citations(NEGATIVE)
    assert len(resolved) >= 1, (
        "el candidato debe conservar al menos una cita resuelta: un documento "
        "sin referencias no acredita resolubilidad"
    )


def test_product_with_no_references_is_rejected():
    """§2.4:111 y spec:137 — un documento con cero referencias no se acepta.

    Consecuencia: sin este control, un relevamiento sin una sola cita pasaría
    como verde vacío.
    """
    verdict = run_control(NO_REFERENCES)

    assert verdict.accepted is False, (
        "un documento con cero referencias a fuentes debe rechazarse"
    )
    assert [diagnostic.cause for diagnostic in verdict.diagnostics] == [
        "no_reference"
    ], (
        "el rechazo debe declarar la ausencia de referencias: {!r}".format(
            verdict.diagnostics
        )
    )


def test_product_citing_an_uninventoried_source_is_rejected():
    """§2.4:111 — toda referencia a una fuente no inventariada se rechaza.

    Consecuencia: sin este control, el relevamiento podría citar material que
    no forma parte del corpus autorizado.
    """
    verdict = run_control(UNINVENTORIED)

    assert verdict.accepted is False, (
        "una referencia a una fuente no inventariada debe rechazarse"
    )
    causes = [diagnostic.cause for diagnostic in verdict.diagnostics]
    assert "uninventoried_source" in causes, (
        "el rechazo debe declarar la fuente no inventariada: {!r}".format(
            verdict.diagnostics
        )
    )
    assert any(
        "s9" in diagnostic.reference for diagnostic in verdict.diagnostics
    ), (
        "el diagnóstico debe nombrar la referencia no inventariada: {!r}".format(
            verdict.diagnostics
        )
    )


# ---------------------------------------------------------------------------
# T6 — trazabilidad estructural del producto
# ---------------------------------------------------------------------------


def test_the_product_cites_only_inventoried_fragments_and_at_least_one():
    """PC-10 (fracción estructural): el producto existe y toda cita resuelve.

    Consecuencia: sin este control, el relevamiento podría presentar
    afirmaciones sin respaldo localizable, que es lo que PC-10 compromete.
    """
    assert PRODUCT.is_file(), (
        "El relevamiento del piloto todavía no existe: la obligación ausente "
        "de GREEN es crear docs/specs/010-003-documentary-pilot/product/"
        "relevamiento.md como corrección del candidato negativo. Este RED "
        "falla por la aserción de existencia, no por FileNotFoundError ni "
        "ImportError."
    )

    resolved = resolved_citations(PRODUCT)
    assert len(resolved) >= 1, (
        "el producto debe incluir al menos una cita que resuelva a una fuente "
        "inventariada y a un ancla registrada"
    )

    verdict = run_control(PRODUCT)
    assert verdict.accepted is True and verdict.diagnostics == (), (
        "toda cita del producto debe resolver a fuente inventariada y ancla "
        "registrada; diagnósticos: {!r}".format(verdict.diagnostics)
    )


# ---------------------------------------------------------------------------
# T7 — integridad del inventario
# ---------------------------------------------------------------------------


def test_inventory_accounts_for_every_source_with_matching_digest_and_declares_synthetic_origin():
    """PC-01 + §2.4:95-109: inventario completo, digests y origen sintético.

    Acredita **bytes en disco == bytes registrados** (límite C-3), no que
    fueran las versiones usadas en el ensayo: eso lo acreditan snapshots y
    registro. Consecuencia: sin este control, una fuente podría cambiar o
    faltar del inventario sin que nadie lo note.
    """
    inventory_text, inventory = load_inventory()

    assert INVENTORY_ID in inventory_text, (
        "el inventario debe identificarse como {!r}".format(INVENTORY_ID)
    )
    assert {"s1", "s2"} <= set(inventory), (
        "el inventario debe listar las dos fuentes del corpus: {!r}".format(
            sorted(inventory)
        )
    )

    for source_id, (relative_path, expected_digest) in sorted(inventory.items()):
        source_path = FIXTURES / relative_path
        assert source_path.is_file(), (
            "la fuente inventariada {!r} no existe en {!r}".format(
                source_id, relative_path
            )
        )
        actual_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        assert actual_digest == expected_digest, (
            "el SHA-256 registrado para {!r} no coincide con sus bytes: "
            "registrado {!r}, en disco {!r}".format(
                source_id, expected_digest, actual_digest
            )
        )

        text = source_path.read_text(encoding="utf-8")
        assert "sintétic" in text.lower(), (
            "la fuente {!r} debe declararse sintética".format(source_id)
        )

        anchor_units = ANCHOR_UNIT_RE.findall(text)
        anchor_ids = source_anchors(source_path)
        assert len(anchor_units) == len(ANCHOR_OPEN_RE.findall(text)), (
            "toda ancla de {!r} debe cerrarse en su unidad: {!r}".format(
                source_id, anchor_units
            )
        )
        assert len(anchor_ids) == len(anchor_units), (
            "cada ancla de {!r} debe ocupar sola su línea y casar la forma "
            "exacta: {!r}".format(source_id, anchor_units)
        )
        for anchor_unit in anchor_units:
            assert ANCHOR_EXACT_RE.match(anchor_unit), (
                "ancla fuera de la convención en {!r}: {!r}".format(
                    source_id, anchor_unit
                )
            )
        assert anchor_ids, (
            "la fuente {!r} debe registrar al menos un ancla".format(source_id)
        )
        assert len(anchor_ids) == len(set(anchor_ids)), (
            "las anclas de {!r} deben ser únicas: {!r}".format(
                source_id, anchor_ids
            )
        )
        assert all(
            anchor_id.startswith(source_id + "-") for anchor_id in anchor_ids
        ), (
            "cada ancla de {!r} debe llevar el identificador de su fuente: "
            "{!r}".format(source_id, anchor_ids)
        )

    present = sorted(
        str(path.relative_to(FIXTURES))
        for path in (FIXTURES / "sources").iterdir()
        if path.is_file() and path.name != "inventory.md"
    )
    listed = sorted(relative_path for relative_path, _digest in inventory.values())
    assert present == listed, (
        "todo archivo bajo sources/ debe figurar en el inventario y toda "
        "fuente listada debe existir: presentes {!r}, listadas {!r}".format(
            present, listed
        )
    )

    negative_text = NEGATIVE.read_text(encoding="utf-8")
    assert "sintétic" in negative_text.lower(), (
        "el candidato negativo debe declararse sintético"
    )


# ---------------------------------------------------------------------------
# T8 — invariancia al rewrap
# ---------------------------------------------------------------------------


def test_control_verdict_is_invariant_under_rewrap_of_the_examined_document(
    tmp_path,
):
    """INV-06: el control no depende de líneas ni de ventanas de texto.

    Compara las cuatro combinaciones del mismo par documento × rewrap:

      1. ``structural/corrected.md`` original   → aceptado, cero diagnósticos;
      2. ``structural/corrected.md`` re-envuelto en este test → igual a 1;
      3. ``structural/broken.md`` original      → rechazado, un diagnóstico;
      4. ``structural/broken.md`` re-envuelto en este test → igual a 3.

    Consecuencia: sin este control, una implementación por ventanas de línea
    pasaría T1 y T2 y el usuario creería que las citas se localizan por
    identificador.
    """
    variant_root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "sources", variant_root / "sources")
    (variant_root / "structural").mkdir()
    variant_inventory = variant_root / "sources" / "inventory.md"

    origins = {"corrected": CORRECTED, "broken": BROKEN}
    variants = {}
    for name, origin in origins.items():
        original_text = origin.read_text(encoding="utf-8")
        rewrapped_text = rewrap_markdown(original_text, width=44)
        assert rewrapped_text != original_text, (
            "la variante de {!r} debe mover el contenido entre líneas para "
            "falsificar las implementaciones por ventanas de línea".format(name)
        )
        variant_path = variant_root / "structural" / "{}.md".format(name)
        variant_path.write_text(rewrapped_text, encoding="utf-8")
        variants[name] = variant_path

    corrected_original = run_control(CORRECTED)
    corrected_variant = run_control(
        variants["corrected"],
        corpus_root=variant_root,
        inventory_path=variant_inventory,
    )
    broken_original = run_control(BROKEN)
    broken_variant = run_control(
        variants["broken"],
        corpus_root=variant_root,
        inventory_path=variant_inventory,
    )

    assert corrected_original.accepted is True, (
        "la combinación 1 (corregida original) debe aceptarse"
    )
    assert corrected_variant.accepted == corrected_original.accepted, (
        "las combinaciones 1 y 2 (corregida original y re-envuelta) deben "
        "compartir veredicto"
    )
    assert corrected_variant.diagnostics == corrected_original.diagnostics, (
        "las combinaciones 1 y 2 deben compartir diagnóstico: {!r} frente "
        "a {!r}".format(
            corrected_original.diagnostics, corrected_variant.diagnostics
        )
    )

    assert broken_original.accepted is False, (
        "la combinación 3 (rota original) debe rechazarse"
    )
    assert broken_variant.accepted == broken_original.accepted, (
        "las combinaciones 3 y 4 (rota original y re-envuelta) deben "
        "compartir veredicto"
    )
    assert broken_variant.diagnostics == broken_original.diagnostics, (
        "las combinaciones 3 y 4 deben compartir diagnóstico: {!r} frente "
        "a {!r}".format(broken_original.diagnostics, broken_variant.diagnostics)
    )
