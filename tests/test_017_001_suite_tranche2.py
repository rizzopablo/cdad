"""017-001 T2 tranche 2 RED: marcas reales en U1/U3/U4 y documental (spec §4.2).

Oraculo derivado del contrato aprobado
``docs/specs/017-001-suite-performance/spec.md`` §4.2 (PC-1 parte
operaciones, INV-1/INV-2/INV-8) y del mapeo
``operation-scope-mapping.md`` §3B-C (``u1.lookup`` con rama
fria/reutilizacion y sus hijos ``u1.copy``/``u1.generate``;
``u3.lookup``/``u3.copy``/``u3.initial-generate`` como accion contractual
y ``u3.contract-staging`` con sus dos llamadas; ``u4.lookup``/``u4.copy``/
``u4.initial-generate`` como accion contractual y ``u4.contract-regenerate``
con sus dos llamadas; ``documentary.contract-regenerate``,
``documentary.install-lookup`` y ``documentary.install``). No lee
implementacion: ejercita las fronteras reales en proceso sobre su rama
reutilizacion (caches preexistentes, sin subprocesos), con y sin observador.

Contribucion respecto de lo existente (P1-P5 de
``test_017_001_suite_operations.py`` y oraculo tranche-1 de
``test_017_001_suite_tranche1.py`` sobre ``product.lookup``): ninguno
ejercita las fronteras reales de U1/U3/U4/documental. Sin este test, esas
marcas pueden faltar o adjudicar mal la rama y la calibracion entraria a la
base sobre captura rota confundiendola con medicion valida.

Sin umbrales temporales como oraculo (spec §4.2; convencion 11): solo
presencia, identidad, rama y neutralidad; nunca duraciones.
"""

import shutil
import tempfile
from pathlib import Path

import tests.test_006_002_u1_delegation_section as u1mod
import tests.test_006_004_u3_principle_single_source as u3mod
import tests.test_006_005_u4_single_entry as u4mod
import tests.test_010_002_documentary_role_integration as dmod
from tests.suite_operation_markers import detach, is_active, observed, use_context

NODEID = ("tests/test_017_001_suite_tranche2.py"
          "::test_real_tranche2_lookups_emit_branch_and_stay_neutral")

EXPECTED_LOOKUPS = (
    "u1.lookup",
    "u4.lookup",
    "u3.lookup",
    "documentary.install-lookup",
)


def _seed_caches(tmp: Path) -> dict:
    """Caches preexistentes: solo la rama reutilizacion, sin subprocesos."""
    u1mod._STAGING_ROOT = tmp / "u1"
    u1mod._STAGING_ROOT.mkdir()
    u4mod._STAGING_COPY = tmp / "u4"
    u4mod._STAGING_COPY.mkdir()
    u3mod._DISPOSABLE.update({"product": tmp / "u3"})
    dmod._INSTALL.update({"install_root": tmp / "install"})
    return {
        "u1": u1mod._STAGING_ROOT,
        "u4": u4mod._STAGING_COPY,
        "u3": u3mod._DISPOSABLE,
        "d": dmod._INSTALL,
    }


def test_real_tranche2_lookups_emit_branch_and_stay_neutral():
    """Sin este test, el usuario calibra U1/U3/U4/documental sin saber si
    las fronteras reales emiten intervalos con su rama (fria/reutilizacion)
    o si las marcas alteran el resultado cuando nadie observa."""
    # Neutralidad de las fronteras reales: sin sumidero externo nadie debe
    # estar escuchando (como hoy); con sumidero externo —el observador del
    # propio suite conecta el suyo desde el arranque de sesion bajo close o
    # en un worker del lote— no se exige ausencia: se exige que no altere
    # los valores y que el contexto propio reciba sus eventos (verificado
    # abajo con observed() + igualdad de resultados en ambas ramas).
    external_sink_present = is_active()
    if not external_sink_present:
        assert not is_active(), (
            "017-001 T2 tranche 2: sin observador externo no debe haber "
            "sumidero activo antes de las fronteras reales")
    tmp = Path(tempfile.mkdtemp(prefix="cdad-017-001-tranche2-"))
    saved = (u1mod._STAGING_ROOT, u4mod._STAGING_COPY,
             dict(u3mod._DISPOSABLE), dict(dmod._INSTALL))
    try:
        expected = _seed_caches(tmp)
        # Sin observador: los resultados son los mismos y no hay a quien
        # entregar eventos (neutralidad sobre las fronteras reales).
        assert u1mod.staging_root() == expected["u1"]
        assert u1mod.staging_root() == expected["u1"]
        assert u4mod._recomputed_root() == expected["u4"]
        assert u4mod._recomputed_root() == expected["u4"]
        assert u3mod.disposable_product() == expected["u3"]
        assert u3mod.disposable_product() == expected["u3"]
        assert dmod.installed_product() == expected["d"]
        assert dmod.installed_product() == expected["d"]

        # Con observador: cada frontera emite sus dos reutilizaciones con
        # identidad, contexto y rama; sin hijos en la rama reutilizacion.
        with observed() as seen:
            with use_context(nodeid=NODEID, phase="call",
                             owner_scope="test"):
                assert u1mod.staging_root() == expected["u1"]
                assert u1mod.staging_root() == expected["u1"]
                assert u4mod._recomputed_root() == expected["u4"]
                assert u4mod._recomputed_root() == expected["u4"]
                assert u3mod.disposable_product() == expected["u3"]
                assert u3mod.disposable_product() == expected["u3"]
                assert dmod.installed_product() == expected["d"]
                assert dmod.installed_product() == expected["d"]
        if external_sink_present:
            # Con observador externo: su sumidero sigue conectado sin el
            # contexto propio y ningun valor cambia — el externo no altera
            # las fronteras (los eventos del contexto propio se verifican
            # abajo: deben llegar las ocho reutilizaciones con rama cached
            # y el nodeid propio).
            assert u1mod.staging_root() == expected["u1"]
            assert u4mod._recomputed_root() == expected["u4"]
            assert u3mod.disposable_product() == expected["u3"]
            assert dmod.installed_product() == expected["d"]
        begins = [r for r in seen if r["event"] == "begin"]
        ends = [r for r in seen if r["event"] == "end"]
        lookups = [r for r in begins if r["operation"] in EXPECTED_LOOKUPS]
        assert len(lookups) == 8 and len(begins) == len(ends) == 8, (
            "017-001 T2 tranche 2 (PC-1 parte operaciones): las fronteras "
            "reales deben emitir sus ocho reutilizaciones con comienzo y "
            "fin; sin esos intervalos no hay calibracion de staging: %r"
            % seen)
        for record in lookups:
            assert record["branch"] == "cached", (
                "017-001 T2 tranche 2: una reutilizacion perdio su rama "
                "`cached`: %r" % (record,))
            assert record["nodeid"] == NODEID, (
                "017-001 T2 tranche 2: se perdio el contexto de test en la "
                "frontera real: %r" % (record,))
    finally:
        (u1mod._STAGING_ROOT, u4mod._STAGING_COPY) = (saved[0], saved[1])
        u3mod._DISPOSABLE.clear()
        u3mod._DISPOSABLE.update(saved[2])
        dmod._INSTALL.clear()
        dmod._INSTALL.update(saved[3])
        shutil.rmtree(tmp, ignore_errors=True)
        # observed() ya retiro el sumidero propio; sin externo este
        # detach() es el no-op de seguridad de siempre. Con externo,
        # retiraria el sumidero ajeno del observador y corromperia la
        # medicion de la sesion.
        if not external_sink_present:
            detach()
