#!/usr/bin/env python3
"""013-001 RED — coherencia de criterio (un test por promesa A-E).

Contract:
- docs/specs/013-001-criterion-coherence/spec.md (sha256
  79b9c12b481efe1f240e09465c7687607c599c0aac8054c996950bf00e3bfd00),
  §3 Promesas A-E (PC-1–PC-14), §5 superficies, §6 evidencia.
- docs/specs/013-001-criterion-coherence/test-audit.md + Resolución
  2026-11-02 (a lo sumo UN módulo, UN test por promesa; estructural sobre
  artefactos reales; B incluye PC-6; pd10 de test_005_003_t6 ya en RED).

Régimen documentary: el oráculo deriva del contrato + entradas autorizadas
(§5 como inventario de superficies, §3 como norma), nunca del producto bajo
verificación. Este módulo NO lee implementación al escribirse; en ejecución
lee artefactos reales como caja negra (existencia + texto) y falla con
AssertionError cuando la norma nueva aún no está distribuida.

Mapeo (un test por promesa observable; la trazabilidad múltiple es
deliberada, no cuota por postcondición):
  test_A_selection_by_contribution -> promesa A; PC-1, PC-2, PC-3
  test_B_maintenance_with_post_audit_substitute -> promesa B; PC-4, PC-5, PC-6, PC-7
  test_C_coherent_instructions_without_quota_or_read -> promesa C; PC-8, PC-9
  test_D_budget_declared_before_campaign -> promesa D; PC-10, PC-11
  test_E_authorized_only_with_clean_install -> promesa E; PC-12, PC-13, PC-14
    (distinto de test_pd10_instruction_declares_full_suite_policy, que ya
    cubre common.md + contradicción de assets; este E cubre hogar canónico
    + instalación limpia + uso autorizado del gate + registro posterior.)

RED hoy: las cinco normas nuevas aún no están distribuidas; cada test falla
por AssertionError de CONTRATO (texto esperado ausente / prohibido presente),
nunca por ImportError, sintaxis ni error de E/S no capturado.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Superficies declaradas por la spec §5 (las rutas abreviadas references/,
# packets/ y assets/ pertenecen a skills/cdad-cycle/ según spec §2).
ROLE_TEST_WRITER = REPO_ROOT / "sources" / "roles" / "test-writer.md"
PACKETS_COMMON = REPO_ROOT / "skills" / "cdad-cycle" / "packets" / "common.md"
PACKET_RED = REPO_ROOT / "skills" / "cdad-cycle" / "packets" / "substages" / "test-writer-red.md"
PACKET_POST_AUDIT = (
    REPO_ROOT / "skills" / "cdad-cycle" / "packets" / "substages" / "test-writer-post-audit.md"
)
PACKET_PROPERTIES = (
    REPO_ROOT / "skills" / "cdad-cycle" / "packets" / "substages" / "test-writer-properties.md"
)
STAGE_3_TDD = REPO_ROOT / "skills" / "cdad-cycle" / "references" / "stage-3-tdd.md"
CI_GATE_DOC = REPO_ROOT / "docs" / "ci-gate.md"


def _read(path: Path) -> str:
    assert path.is_file(), (
        f"artefacto esperado ausente: {path.relative_to(REPO_ROOT)} — "
        f"GREEN debe crearlo o conservarlo según spec §5"
    )
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AssertionError(
            f"no se pudo leer {path.relative_to(REPO_ROOT)}: {exc}"
        ) from exc


def test_A_selection_by_contribution() -> None:
    """Promesa A (PC-1, PC-2, PC-3): AUDIT distingue protección existente/faltante.

    Sin este test, el usuario aprueba incorporaciones sin saber qué ya protege
    la suite y duplica verificadores equivalentes (o deja huecos creyéndolos
    cubiertos).
    """
    role = _read(ROLE_TEST_WRITER)
    red = _read(PACKET_RED)
    assert re.search(r"contribu", role, re.IGNORECASE), (
        "PC-2 violada: sources/roles/test-writer.md no declara la contribución "
        "respecto de lo existente"
    )
    assert re.search(r"recuperable", role, re.IGNORECASE), (
        "PC-1 violada: el rol no exige referencias recuperables para la "
        "protección existente"
    )
    assert re.search(r"promesa", role, re.IGNORECASE), (
        "PC-3 violada: la selección no se declara por promesa observable"
    )
    assert re.search(r"promesa", red, re.IGNORECASE), (
        "PC-8/PC-3 violada: test-writer-red.md no selecciona por promesa"
    )
    assert re.search(r"sin cuota|no convierte|sin convertir", red, re.IGNORECASE), (
        "PC-3 violada: test-writer-red.md aún convierte postcondición en cuota "
        "de test nuevo"
    )


def test_B_maintenance_with_post_audit_substitute() -> None:
    """Promesa B (PC-4, PC-5, PC-6, PC-7): disposición única y sustituto vigente a POST-AUDIT.

    Sin este test, el usuario acumula tests sin disposición o retira originales
    sin destino ejecutable, y envía sustitutos vigentes a RED (rojo artificial)
    en vez de acreditarlos en POST-AUDIT con verde + sensibilidad.
    """
    role = _read(ROLE_TEST_WRITER)
    post_audit = _read(PACKET_POST_AUDIT)
    red = _read(PACKET_RED)
    for expected in ("Mantener", "Extender", "Sustituir", "Consolidar", "Añadir", "Retirar"):
        assert expected.lower() in role.lower(), (
            f"PC-4 violada: falta la disposición {expected!r} en "
            f"sources/roles/test-writer.md"
        )
    assert re.search(r"disposici[óo]n [úu]nica|exactamente una", role, re.IGNORECASE), (
        "PC-4 violada: el rol no exige disposición exactamente única por test"
    )
    assert re.search(r"sustitut", post_audit, re.IGNORECASE), (
        "PC-6 violada: test-writer-post-audit.md no admite sustitutos nuevos"
    )
    assert re.search(r"vigente", post_audit, re.IGNORECASE), (
        "PC-6 violada: el POST-AUDIT no distingue comportamiento vigente"
    )
    assert re.search(r"verde", post_audit, re.IGNORECASE), (
        "PC-6 violada: el sustituto no exige ejecución verde"
    )
    assert re.search(r"sensibilidad", post_audit, re.IGNORECASE), (
        "PC-6 violada: el sustituto no exige sensibilidad ante defecto contractual"
    )
    assert re.search(r"vigente", red, re.IGNORECASE) and re.search(
        r"POST-AUDIT", red
    ), (
        "PC-6/PC-8 violada: test-writer-red.md no deriva el sustituto vigente "
        "a POST-AUDIT (lo reclama como RED)"
    )


def test_C_coherent_instructions_without_quota_or_read() -> None:
    """Promesa C (PC-8, PC-9): sin cuota por postcondición ni lectura de implementación.

    Sin este test, el usuario vuelve a exigir un test por postcondición o a
    ordenar inspección de implementación en pre-RED, y reedita doctrinas
    paralelas en vez de referenciar R2/R4/R7.
    """
    red = _read(PACKET_RED)
    role = _read(ROLE_TEST_WRITER)
    assert re.search(r"promesa", red, re.IGNORECASE), (
        "PC-8 violada: RED no selecciona por promesa"
    )
    assert not re.search(
        r"todo test nuevo pertenece a RED|todo test nuevo.*RED|siempre hay tres despachos",
        red,
        re.IGNORECASE,
    ), (
        "PC-6/PC-8 violada: RED aún afirma el universal «todo test nuevo "
        "pertenece a RED»"
    )
    assert re.search(r"POST-AUDIT|vigente", red, re.IGNORECASE), (
        "PC-8 violada: RED no distingue el sustituto vigente del pendiente"
    )
    assert not re.search(
        r"inspeccion(ar|a).*implementaci[óo]n|importar.*implementaci[óo]n|leer.*implementaci[óo]n para descubrir",
        red,
        re.IGNORECASE,
    ), (
        "PC-8 violada: pre-RED ordena leer/inspeccionar implementación"
    )
    assert re.search(r"R2|selecci[óo]n.*promesa|hogar", role, re.IGNORECASE), (
        "PC-9 violada: el rol no referencia el hogar R2 de selección"
    )


def test_D_budget_declared_before_campaign() -> None:
    """Promesa D (PC-10, PC-11): presupuesto finito/positivo declarado y reproducible.

    Sin este test, el usuario reintroduce cuotas universales rivales
    (100-1000, mínimo 100, 8-10) y acepta propiedades no reproducibles.
    """
    props = _read(PACKET_PROPERTIES)
    role = _read(ROLE_TEST_WRITER)
    assert re.search(r"presupuesto", props, re.IGNORECASE), (
        "PC-10 violada: test-writer-properties.md no declara presupuesto"
    )
    assert re.search(r"declarado", props, re.IGNORECASE), (
        "PC-10 violada: el presupuesto no se exige declarado antes de la campaña"
    )
    assert re.search(r"justific", props, re.IGNORECASE), (
        "PC-10 violada: el presupuesto no exige justificación (invariante/dominio/coste)"
    )
    assert re.search(r"semilla", props, re.IGNORECASE), (
        "PC-11 violada: la evidencia reproducible no exige semilla"
    )
    assert re.search(r"presupuesto", role, re.IGNORECASE), (
        "PC-10 violada: sources/roles/test-writer.md no presupuesta propiedades"
    )
    assert not re.search(r"100\s*-\s*1000|mínimo 100|minimum 100", props), (
        "PC-10 violada: persisten cuotas universales rivales en properties"
    )


def test_E_authorized_only_with_clean_install() -> None:
    """Promesa E (PC-12, PC-13, PC-14): hogar canónico, autorización e instalación limpia.

    Sin este test, el usuario dispersa la política en hogares paralelos, ejecuta
    suite completa sin autorización y confunde instalación limpia con suite
    completa. Distinto de pd10 (common.md + contradicción de assets): este
    verifica hogar canónico + test-clean + uso autorizado del gate.
    """
    home = _read(STAGE_3_TDD)
    gate_doc = _read(CI_GATE_DOC)
    assert re.search(r"Test evidence policy", home), (
        "PC-12 violada: stage-3-tdd.md no es el hogar canónico reconocido"
    )
    assert re.search(
        r"autorizaci[óo]n expresa|con autorizaci[óo]n|authorized|authorization",
        home,
        re.IGNORECASE,
    ), (
        "PC-12/PC-13 violada: el hogar canónico no exige autorización expresa "
        "para la suite completa"
    )
    assert re.search(r"no realizada|not run", home, re.IGNORECASE), (
        "PC-13 violada: el hogar no registra «suite completa no realizada»"
    )
    assert re.search(r"instalaci[óo]n limpia|test-clean", home, re.IGNORECASE), (
        "PC-12 violada: el hogar elimina la evidencia aplicable de instalación "
        "limpia de addon"
    )
    assert re.search(
        r"autorizaci[óo]n|authorized|authorization", gate_doc, re.IGNORECASE
    ), (
        "PC-13 violada: docs/ci-gate.md no condiciona el gate a autorización expresa"
    )
