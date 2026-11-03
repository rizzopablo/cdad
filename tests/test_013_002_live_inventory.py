"""013-002 RED — inventario vivo (7 focales del AUDIT aprobado).

Deriva de docs/specs/013-002-live-inventory/spec.md (PC-1..PC-8, Promesas A-D)
y de docs/specs/013-002-live-inventory/test-audit.md (delta de altas, una
promesa por test). Cada test protege una promesa observable y declara su
consecuencia ("sin este test, el usuario..."). Ningun oraculo se toma del
producto futuro: las expectativas vienen del contrato y de las entradas
autorizadas (inventario/mapa vivos). La norma documental comun vive en
skills/cdad-cycle/references/documentary-contracts.md.

Trazabilidad: A1 (PC-1, PC-3), A2 (PC-2, PC-4), B (PC-4), C1 (PC-5),
C2 (PC-5, PC-6), D1 (PC-7), D2 (PC-8).
"""

import ast
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INVENTORY = REPO / "docs/specs/008-002-suite-by-capability/suite-inventory.json"
MAP = REPO / "docs/specs/008-002-suite-by-capability/pc-map.json"
MAINT = REPO / "docs/suite-maintenance.md"

LOT = "013-002-live-inventory"
SELF = "tests/test_013_002_live_inventory.py"
B1_MODULE = "tests/test_005_013_t1_unit_projection.py"
B1_A = B1_MODULE + "::test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes"
B1_B = B1_MODULE + "::test_b1_collision_leaves_the_old_packet_valid_and_receivable"
VALIDATE_CMD = "python3 scripts/cdad-suite.py validate"
HELPER_DEBT = "tests/_rf2_open_pause.py"

# Instrucciones distribuidas que PC-7 compromete (localizadores del contrato,
# spec 013-002 seccion 2 y PC-7; se leen como verificacion, el oraculo es la
# spec, no su contenido actual).
HANDOFF_FILES = [
    "sources/roles/orchestrator.md",
    "skills/cdad-cycle/references/handoff-prompts.md",
    "skills/cdad-cycle/references/re-entry.md",
]


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _inventory_modules():
    return _load_json(INVENTORY)["modules"]


def _map_entries():
    return _load_json(MAP)["entries"]


def _collect_test_files():
    return sorted(
        str(p.relative_to(REPO))
        for p in (REPO / "tests").glob("test_*.py")
        if p.is_file()
    )


def _contract_recoverable(contract):
    if contract in ("VERIFY", "", None):
        return False
    return (REPO / contract).is_file()


# Promesa A1 ---------------------------------------------------------------
def test_013_002_A_inventario_efectivo_y_validate_rc0():
    """PC-1 + PC-3. Sin este test, el usuario puede cerrar con un inventario
    estructuralmente incompleto creyendo que el verde sintentico lo cubre."""
    inv = _load_json(INVENTORY)
    modules = {m["path"]: m for m in inv["modules"]}
    test_files = _collect_test_files()
    missing = [p for p in test_files if p not in modules]
    assert not missing, (
        "inventario incompleto sobre la coleccion efectiva (PC-1): faltan "
        "%s; %s debe terminar con rc=0 solo sobre la revision que ya "
        "contiene el ultimo delta y estos tests" % (missing, VALIDATE_CMD)
    )
    for path, mod in modules.items():
        assert (REPO / path).is_file(), (
            "inventario nombra un modulo inexistente (PC-1): %s" % path
        )
        assigns = mod.get("assignments", [])
        assert assigns, "modulo sin asignacion capacidad+contrato (PC-1): %s" % path
        for a in assigns:
            assert a.get("capability") and a.get("contract"), (
                "asignacion sin capacidad o contrato (PC-1): %s %s" % (path, a)
            )
            if a.get("scope") == "nodeids":
                for nid in a.get("nodeids", []):
                    fpart = nid.split("::")[0]
                    assert (REPO / fpart).is_file(), (
                        "asignacion a nodeid inexistente (PC-1): %s" % nid
                    )
    assert HELPER_DEBT in modules, "universo sin %s (PC-3)" % HELPER_DEBT


# Promesa A2 ---------------------------------------------------------------
def test_013_002_A_contratos_recuperables_y_seleccion_cubre_union():
    """PC-2 (+PC-4). Sin este test, el usuario puede seleccionar por capacidad
    sin poder recuperar los contratos."""
    modules = {m["path"]: m for m in _inventory_modules()}
    assert SELF in modules, (
        "alta pendiente (PC-2): %s sin asignacion inventariada" % SELF
    )
    self_assigns = modules[SELF]["assignments"]
    assert self_assigns, "alta sin capacidad ni contrato (PC-2): %s" % SELF
    for a in self_assigns:
        assert a.get("contract") not in ("VERIFY", "", None), (
            "literal VERIFY como sustituto de contrato (PC-2): %s" % a
        )
        assert _contract_recoverable(a["contract"]), (
            "contrato no recuperable, sin procedencia (PC-2): %s" % a.get("contract")
        )
    assert (modules[SELF].get("rationale") or "").strip(), (
        "asignacion sin procedencia explicada (PC-2): %s" % SELF
    )
    for path, mod in modules.items():
        for a in mod.get("assignments", []):
            if a.get("contract") == "VERIFY":
                assert path == HELPER_DEBT and mod.get("confidence") == "baja", (
                    "VERIFY fuera de la deuda explicita del helper (PC-2): %s" % path
                )
                body = MAINT.read_text(encoding="utf-8") if MAINT.is_file() else ""
                assert "VERIFY" in body and "_rf2_open_pause" in body, (
                    "deuda del helper no declarada como deuda, separada de "
                    "pendientes estructurales y de acreditacion (PC-2/PC-3)"
                )
    test_files = set(_collect_test_files())
    covered = set(modules)
    assert not (test_files - covered), "union no cubre la coleccion (PC-2)"
    mixed_without_detail = [
        p for p, m in modules.items()
        if len(m.get("assignments", [])) == 1
        and m["assignments"][0].get("scope") == "module"
        and p == SELF
        and "nodeids" in json.dumps(m)
    ]
    assert not mixed_without_detail, "modulo mixto con capacidad por prefijo (PC-2)"


# Promesa B ----------------------------------------------------------------
def test_013_002_B_clasificacion_no_es_acreditacion():
    """PC-4. Sin este test, el usuario confunde presencia de campos y verde
    estructural con proteccion semantica."""
    assert MAINT.is_file(), (
        "documentacion operativa ausente (PC-4): sin %s no hay vocabulario "
        "que distinga asignacion de acreditacion" % MAINT.relative_to(REPO)
    )
    body = MAINT.read_text(encoding="utf-8")
    low = body.lower()
    for fragment in (
        "asignaci",
        "obligaci",
        "acreditaci",
        "evidencia",
        "incertidumbre",
    ):
        assert fragment in low, "vocabulario sin %s (PC-4)" % fragment
    assert "confidence" in low, "sin advertencia de confidence (PC-4)"
    assert "rc=0" in body or "rc = 0" in body, "sin limite de validate rc=0 (PC-4)"
    assert "eliminar" in low, "sin lectura legacy de eliminar (PC-4)"


# Promesa C1 ---------------------------------------------------------------
def test_013_002_C_mapa_inicial_B1_identificado_por_entrada():
    """PC-5. Sin este test, el usuario no puede recuperar el lote nuevo ni
    distinguirlo del piloto historico."""
    entries = _map_entries()
    lot = [
        e for e in entries
        if e.get("task") == LOT or (e.get("decision_note") or "").find(LOT) >= 0
    ]
    wanted = {B1_A, B1_B}
    found = {e.get("original_nodeid") for e in lot} | {
        e.get("target_nodeid") for e in lot
    }
    assert wanted <= found, (
        "mapa inicial acotado ausente (PC-5): faltan %s; el lote %s debe "
        "identificarse por entrada con task o decision_note" % (wanted - found, LOT)
    )
    required = (
        "contract", "accreditation_source", "original_nodeid", "target_nodeid",
        "variant_observable", "decision",
    )
    for e in lot:
        if e.get("original_nodeid") in wanted or e.get("target_nodeid") in wanted:
            for k in required:
                assert e.get(k), "entrada B1 sin %s (PC-5): %s" % (k, e)
            assert e.get("target_nodeid") in wanted, (
                "antes de sustitucion acreditada el destino es el test actual; "
                "no se inventa sustituto (PC-5): %s" % e
            )
            assert (e.get("variant_observable") or "").strip(), (
                "diferencias del par B1 no conservadas (PC-5)"
            )


# Promesa C2 ---------------------------------------------------------------
def test_013_002_C_conserva_origen_y_metadatos_historicos():
    """PC-5 + PC-6. Sin este test, el usuario pierde la genealogia al primer
    mv o rm."""
    data = _load_json(MAP)
    entries = data["entries"]
    lot = [
        e for e in entries
        if e.get("task") == LOT or (e.get("decision_note") or "").find(LOT) >= 0
    ]
    assert lot, "lote %s sin entradas identificadas por entrada (PC-5/PC-6)" % LOT
    for e in lot:
        assert isinstance(e.get("target_nodeid"), str), (
            "target_nodeid incompatible con varios destinos sin desglose "
            "explcito (PC-6): %s" % e
        )
        c = e.get("contract") or {}
        assert c.get("spec") and c.get("id"), (
            "obligacion no identificada por contrato+identificador+variante "
            "(PC-6): %s" % e
        )
        assert (e.get("variant_observable") or "").strip(), (
            "varias obligaciones del mismo test colapsadas (PC-6): %s" % e
        )
    assert len(data.get("pilot_modules", [])) >= 1, (
        "metadatos del piloto historico reutilizados para el lote nuevo (PC-5)"
    )
    legacy_verify = [e for e in entries if e.get("status") == "VERIFY"]
    assert legacy_verify, (
        "registros historicos VERIFY/placeholders desaparecidos para lograr "
        "verde (PC-6)"
    )


# Promesa D1 ---------------------------------------------------------------
def test_013_002_D_inventario_vivo_declarado_momentos_y_handoffs():
    """PC-7. Sin este test, el usuario no ve la desactualizacion hasta entrar
    a Review."""
    assert MAINT.is_file(), (
        "producto comprometido ausente (PC-7): %s" % MAINT.relative_to(REPO)
    )
    body = MAINT.read_text(encoding="utf-8")
    assert "## Inventario vivo" in body, "seccion fija ausente (PC-7)"
    assert VALIDATE_CMD in body, "comando de integridad ausente (PC-7)"
    assert "docs/specs/008-002-suite-by-capability/suite-inventory.json" in body, (
        "ruta del inventario ausente (PC-7)"
    )
    assert "docs/specs/008-002-suite-by-capability/pc-map.json" in body, (
        "ruta del mapa ausente (PC-7)"
    )
    low = body.lower()
    assert "sin inventario vivo declarado" in low, (
        "salida explicita cuando falta la declaracion ausente (PC-7)"
    )
    assert "nodeid" in low and "procedencia" in low, (
        "delta de altas sin nodeid/capacidad/contrato/procedencia (PC-7)"
    )
    assert "materializ" in low, "materializacion al re-entry ausente (PC-7)"
    for rel in HANDOFF_FILES:
        p = REPO / rel
        assert p.is_file(), "instruccion distribuida ausente: %s" % rel
        text = p.read_text(encoding="utf-8").lower()
        assert "inventario vivo" in text or "suite-maintenance" in text, (
            "regla no transmitida en %s (PC-7)" % rel
        )


# Promesa D2 ---------------------------------------------------------------
def test_013_002_D_limites_y_surface_collect_only():
    """PC-8. Sin este test, el usuario ejecuta toda la suite creyendo que
    inspecciona o que fue autorizado."""
    assert MAINT.is_file(), "producto comprometido ausente (PC-8)"
    body = MAINT.read_text(encoding="utf-8")
    low = body.lower()
    assert "validate" in low, "sin distincion de validate (PC-8)"
    assert "contraste" in low or "conservaci" in low, (
        "sin distincion del contraste del mapa (PC-8)"
    )
    assert "revisi" in low and "evidencia" in low, (
        "sin distincion de revision independiente y evidencias (PC-8)"
    )
    assert "--collect-only" in body, (
        "sin advertencia de inspeccion con --collect-only (PC-8)"
    )
    assert "autorizaci" in low, (
        "sin prohibicion de ejecutar seleccion completa sin autorizacion "
        "expresa (PC-8)"
    )
