#!/usr/bin/env python3
"""005-003 T4 RED — inventario de capacidades efectivas + fallback portable
(PD-9; INV-7).

Contract:
- docs/specs/005-003-orientation-reduction/spec.md §2.7 (capacidades efectivas
  y fallback portable), §3 PD-9, §4 INV-6/INV-7, §7 (fronteras: OpenChamber es
  consumidor verificado, NO dependencia ni dashboard).
- docs/specs/005-003-orientation-reduction/plan.md §3 (ficha T4) y §4 (T4).

CICLO SIN CÓDIGO. El producto de T4 es un DOCUMENTO
(`skills/cdad-cycle/references/capabilities.md`), así que este RED es un
ORÁCULO DOCUMENTAL: localiza el documento por su ruta DECLARADA en runtime y
afirma el contrato observable de §2.7/PD-9 —nunca lo implementa (eso es el
GREEN)—. El documento aún NO existe: `_load_doc` afirma su existencia con un
`AssertionError` de CONTRATO (nunca un `FileNotFoundError` no capturado, ni
`ImportError`, ni `SyntaxError`), de modo que cada test falla por la ASERCIÓN
sobre el contrato observable y no por un error de E/S.

El test NO usa valores de este VPS (INV-6): los patrones de privacidad se arman
a partir de prefijos/nombres genéricos y públicos, jamás de una ruta, proveedor,
modelo, servidor ni identificador de sesión concretos de esta instalación.

Mapeo test → postcondición/invariante:
  test_pd9_inventory_exists_and_is_non_empty
      -> PD-9 (el inventario existe como documento no vacío en su ruta
         declarada)
  test_pd9_inventory_declares_four_classes_with_criterion
      -> PD-9/§2.7 (declara las cuatro clases —observada/documentada/no
         disponible/desconocida— y, o bien una capacidad en cada clase, o bien
         el criterio que la asigna)
  test_pd9_inventory_declares_surfaces_and_version_link
      -> PD-9/§2.7 (nombra planes, archivos, previews y diffs; está ligado a
         versión/configuración)
  test_pd9_inventory_declares_portable_fallback_and_file_link_path
      -> PD-9/§2.7 (declara el fallback portable por archivos o enlaces y el
         camino agente → artefacto → revisión)
  test_pd9_inventory_does_not_promise_openchamber_agent_surface_contract
      -> PD-9/§2.7 (NO promete el contrato estable agente↔superficie de
         OpenChamber)
  test_inv6_inventory_carries_no_this_vps_values
      -> INV-6/INV-7 (sin rutas absolutas del host, proveedor/modelo concreto,
         servidor ni identificadores crudos de sesión)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Ruta DECLARADA por la spec/plan para el producto documental de T4.
DOC = REPO_ROOT / "skills" / "cdad-cycle" / "references" / "capabilities.md"


# --------------------------------------------------------------- §2.7 / PD-9

# Las cuatro clases de la matriz de capacidades (§2.7). Se aceptan los términos
# en español y su equivalente inglés de manera indistinta.
CLASS_LABELS = {
    "observada": re.compile(r"(?i)\bobservad[ao]s?\b|\bobserved\b"),
    "documentada": re.compile(r"(?i)\bdocumentad[ao]s?\b|\bdocumented\b"),
    "no disponible": re.compile(
        r"(?i)\bno[\s_-]+disponible\w*\b|\bnot\s+available\b|\bunavailable\b"),
    "desconocida": re.compile(r"(?i)\bdesconocid[ao]s?\b|\bunknown\b"),
}

# Criterio de asignación de la clase (alternativa a «una capacidad por clase»).
CRITERION_RX = re.compile(
    r"(?i)\bcriteri\w*\b|\bcriterion\b|\bclasific\w*\b|\bse\s+asigna\b|"
    r"\bis\s+assigned\b|\bassign\w*\b")

# Superficies de §2.7: cómo se presentan planes, archivos, previews y diffs.
PLAN_RX = re.compile(r"(?i)\bplanes?\b|\bplans?\b")
FILE_RX = re.compile(r"(?i)\barchivos?\b|\bfiles?\b")
PREVIEW_RX = re.compile(r"(?i)\bpreviews?\b|\bprevisualiz\w*\b")
DIFF_RX = re.compile(r"(?i)\bdiffs?\b|\bdiferencias?\b")
# Cualquier capacidad candidata (rama «una capacidad en cada clase»).
CAPABILITY_RX = re.compile(
    r"(?i)\bplanes?\b|\bplans?\b|\barchivos?\b|\bfiles?\b|\bpreviews?\b|"
    r"\bprevisualiz\w*\b|\bdiffs?\b|\bCLI\b|\bOpenChamber\b|\bartefact\w*\b|"
    r"\benlaces?\b|\blinks?\b")

# §2.7: el inventario está LIGADO a versión/configuración.
VERSION_RX = re.compile(r"(?i)\bversi[oó]n\w*\b|\bversion\w*\b")
CONFIG_RX = re.compile(
    r"(?i)\bconfiguraci[oó]n\w*\b|\bconfiguration\w*\b|\bconfig\b")

# §2.7: fallback portable por archivos o enlaces.
FALLBACK_RX = re.compile(r"(?i)\bfallback\b|\brepliegue\b")
PORTABLE_RX = re.compile(r"(?i)\bportable\w*\b")
LINK_RX = re.compile(r"(?i)\benlaces?\b|\blinks?\b")

# §2.7/PD-9 borde: camino agente → artefacto → revisión por archivos/enlaces.
AGENT_RX = re.compile(r"(?i)\bagent\w*\b")
ARTIFACT_RX = re.compile(r"(?i)\bartefact\w*\b|\bartifact\w*\b")
REVIEW_RX = re.compile(r"(?i)\brevisi[oó]n\w*\b|\breview\w*\b")

# §2.7: contrato estable agente↔superficie (NO verificado; no se promete).
CONTRACT_SURFACE_RX = re.compile(
    r"(?i)contrato\s+estable|stable\s+contract|"
    r"agente\s*(?:↔|<->|-->|→|->)\s*superficie|"
    r"agent\s*(?:↔|<->|-->|→|->)\s*surface|"
    r"agente[\s_-]superficie|agent[\s_-]surface|"
    r"API\s+de\s+(?:la\s+)?UI|UI\s+API")
NEGATION_RX = re.compile(
    r"(?i)\bno\b|\bnunca\b|\bjam[aá]s\b|\bnever\b|\bnot\b|\bsin\b|\bwithout\b|"
    r"\bunverified\b|\bpropuesta\b|\bproposed\b|\bposterior\b|\blater\b|"
    r"\bpendiente\b|\bpending\b|\bausente\b|\babsent\b")


# ------------------------------------------------------------- INV-6 / INV-7

# Patrones de privacidad armados con prefijos/nombres GENÉRICOS y públicos (el
# test no porta un valor concreto de este VPS).
_HOST_DIR_PREFIXES = ("home", "Users", "root", "srv", "mnt", "opt", "var")
HOST_PATH_RX = re.compile(
    r"(?:^|[\s`(\[=])/(?:" + "|".join(_HOST_DIR_PREFIXES) + r")/"
    r"|[A-Za-z]:\\")

_PROVIDER_NAMES = ("openai", "anthropic", "deepseek", "openrouter", "groq",
                   "mistral", "cohere", "gemini", "llama", "qwen", "xai",
                   "grok")
PROVIDER_MODEL_RX = re.compile(
    r"(?i)\b(?:" + "|".join(_PROVIDER_NAMES) + r")\b"
    r"|\b(?:gpt|claude|o[1-4])[\s_-]?[0-9]")

SERVER_IP_RX = re.compile(
    r"https?://\d{1,3}(?:\.\d{1,3}){3}|\b\d{1,3}(?:\.\d{1,3}){3}\b")
RAW_SESSION_RX = re.compile(r"\bses_[A-Za-z0-9]{6,}\b|\bses-[A-Za-z0-9]{6,}\b")

PRIVACY_PATTERNS = (
    ("ruta absoluta del host", HOST_PATH_RX),
    ("proveedor/modelo concreto", PROVIDER_MODEL_RX),
    ("servidor (IP/URL)", SERVER_IP_RX),
    ("identificador crudo de sesión", RAW_SESSION_RX),
)


# ---------------------------------------------------------------- helpers


def _load_doc() -> str:
    """Documento declarado por su ruta; ausente es estado conductual, no E/S."""
    assert DOC.is_file(), (
        "PD-9 violada: el inventario de capacidades no existe en su ruta "
        f"declarada: {DOC} (el documento es el producto de T4; todavía no se "
        "implementó)"
    )
    text = DOC.read_text(encoding="utf-8")
    assert text.strip(), (
        f"PD-9 violada: el inventario existe pero está vacío: {DOC}"
    )
    return text


def _paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", text)
    return [re.sub(r"\s+", " ", b).strip() for b in blocks if b.strip()]


def _window_around(text: str, pattern: re.Pattern, radius: int = 4):
    """Ventanas de líneas alrededor de cada coincidencia (para co-ocurrencia)."""
    lines = text.splitlines()
    windows = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            lo, hi = max(0, i - radius), min(len(lines), i + radius + 1)
            windows.append("\n".join(lines[lo:hi]))
    return windows


# ===================================================================== PD-9


def test_pd9_inventory_exists_and_is_non_empty() -> None:
    """PD-9: el inventario de capacidades existe en su ruta declarada y no está
    vacío (el documento es el producto de T4)."""
    text = _load_doc()
    assert text.strip(), (
        "PD-9 violada: el inventario de capacidades está vacío"
    )


def test_pd9_inventory_declares_four_classes_with_criterion() -> None:
    """PD-9/§2.7: el inventario declara cada capacidad en UNA de las cuatro
    clases (observada / documentada / no disponible / desconocida) y declara, o
    bien una capacidad en cada clase, o bien el criterio que la asigna."""
    text = _load_doc()

    missing = [cls for cls, rx in CLASS_LABELS.items() if not rx.search(text)]
    assert not missing, (
        "PD-9 violada: el inventario no declara las cuatro clases de §2.7 "
        f"(observada/documentada/no disponible/desconocida); faltan: {missing}"
    )

    windows = {cls: _window_around(text, rx, radius=3)
               for cls, rx in CLASS_LABELS.items()}
    capability_per_class = {
        cls: any(CAPABILITY_RX.search(w) for w in ws)
        for cls, ws in windows.items()
    }
    criterion = bool(CRITERION_RX.search(text))
    assert criterion or all(capability_per_class.values()), (
        "PD-9 violada: el inventario declara las clases pero no declara ni una "
        "capacidad en cada clase ni el criterio que asigna una capacidad a su "
        f"clase (§2.7); criterio={criterion}; "
        f"capacidad_por_clase={capability_per_class}"
    )


def test_pd9_inventory_declares_surfaces_and_version_link() -> None:
    """PD-9/§2.7: el inventario nombra las capacidades existentes para presentar
    planes, archivos, previews y diffs, y se declara ligado a
    versión/configuración."""
    text = _load_doc()

    surfaces = {
        "planes": PLAN_RX,
        "archivos": FILE_RX,
        "previews": PREVIEW_RX,
        "diffs": DIFF_RX,
    }
    missing = [name for name, rx in surfaces.items() if not rx.search(text)]
    assert not missing, (
        "PD-9/§2.7 violada: el inventario no nombra las superficies para las "
        "que encuentra capacidades existentes (planes, archivos, previews, "
        f"diffs); faltan: {missing}"
    )

    linked = [p for p in _paragraphs(text)
              if VERSION_RX.search(p) and CONFIG_RX.search(p)]
    assert linked, (
        "PD-9/§2.7 violada: el inventario no se declara LIGADO a "
        "versión/configuración (ningún bloque nombra a la vez la versión y la "
        "configuración)"
    )


def test_pd9_inventory_declares_portable_fallback_and_file_link_path() -> None:
    """PD-9/§2.7: el inventario declara el fallback portable por archivos o
    enlaces (el mínimo ya posible) y demuestra el camino
    agente → artefacto → revisión por archivos/enlaces."""
    text = _load_doc()

    assert FALLBACK_RX.search(text), (
        "PD-9/§2.7 violada: el inventario no declara el fallback"
    )
    assert PORTABLE_RX.search(text), (
        "PD-9/§2.7 violada: el fallback no se declara PORTABLE"
    )
    assert FILE_RX.search(text) and LINK_RX.search(text), (
        "PD-9/§2.7 violada: el fallback portable no se declara por archivos o "
        "enlaces (el mínimo ya posible)"
    )

    chain = [
        w for w in _window_around(text, ARTIFACT_RX, radius=4)
        if AGENT_RX.search(w) and REVIEW_RX.search(w)
        and (FILE_RX.search(w) or LINK_RX.search(w))
    ]
    assert chain, (
        "PD-9/§2.7 violada: el inventario no declara el camino "
        "agente → artefacto → revisión por archivos/enlaces (la demostración "
        "del fallback portable)"
    )


def test_pd9_inventory_does_not_promise_openchamber_agent_surface_contract() -> None:
    """PD-9/§2.7: el inventario NO promete el contrato estable agente↔superficie
    de OpenChamber (no está verificado; una integración compleja de UI es
    propuesta posterior, no comprometida)."""
    text = _load_doc()

    for window in _window_around(text, CONTRACT_SURFACE_RX, radius=4):
        assert NEGATION_RX.search(window), (
            "PD-9/§2.7 violada: el inventario afirma/promete el contrato "
            "estable agente↔superficie de OpenChamber (NO está verificado; una "
            "integración compleja de UI es propuesta posterior, no "
            f"comprometida): {window!r}"
        )


def test_inv6_inventory_carries_no_this_vps_values() -> None:
    """INV-6/INV-7: el inventario no porta valores de este VPS — ni rutas
    absolutas del host, ni proveedor/modelo concreto, ni servidor, ni
    identificadores crudos de sesión."""
    text = _load_doc()

    offenders: list[str] = []
    for label, rx in PRIVACY_PATTERNS:
        for match in rx.finditer(text):
            offenders.append(f"{label}: {match.group(0)!r}")
    assert not offenders, (
        "INV-6/INV-7 violada: el inventario porta valores de este VPS "
        "(prohibidos en el producto: rutas absolutas del host, proveedor/modelo "
        f"concreto, servidor, identificadores crudos de sesión): {offenders}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
