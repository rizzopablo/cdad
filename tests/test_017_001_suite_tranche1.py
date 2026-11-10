"""017-001 T2 tranche 1 RED: marcas reales en product_staging (spec §4.2).

Oraculo derivado del contrato aprobado
``docs/specs/017-001-suite-performance/spec.md`` §4.2 (PC-1 parte
operaciones, INV-1/INV-2/INV-8) y del mapeo
``operation-scope-mapping.md`` §3B (``tests/product_staging.py``:
``product.lookup`` con rama fria/reutilizacion, ``product.copy`` y
``product.generate`` anidados). No lee implementacion: ejercita la
frontera real ``product_root()`` en proceso, con y sin observador.

Contribucion respecto de lo existente (P1-P5 de
``test_017_001_suite_operations.py``): P1 acredita transporte,
identidad, contexto y anidamiento del helper sobre marcas
sinteticas; P3 acredita neutralidad del helper aislado. Ninguno
ejercita una frontera real: sin este test, las marcas reales pueden
faltar o adjudicar mal la rama y la calibracion entraria a la base
sobre captura rota confundiendola con medicion valida.

Sin umbrales temporales como oraculo (spec §4.2; convencion 11):
solo presencia, identidad, rama y neutralidad; nunca duraciones.
"""

from tests import product_staging
from tests.suite_operation_markers import detach, is_active, observed, use_context

NODEID = ("tests/test_017_001_suite_tranche1.py"
          "::test_real_product_lookup_emits_branch_and_stays_neutral")


def test_real_product_lookup_emits_branch_and_stays_neutral():
    """Sin este test, el usuario calibra product.lookup sin saber si la
    frontera real emite intervalos con su rama (fria/reutilizacion) o si
    las marcas alteran el resultado cuando nadie observa."""
    # Neutralidad de la frontera real: sin sumidero externo nadie debe estar
    # escuchando (como hoy); con sumidero externo —el observador del propio
    # suite conecta el suyo desde el arranque de sesion bajo close o en un
    # worker del lote— no se exige ausencia: se exige que no altere el valor
    # y que el contexto propio reciba sus eventos (verificado abajo con
    # observed() + igualdad de resultados en ambas ramas).
    external_sink_present = is_active()
    if not external_sink_present:
        assert not is_active(), (
            "017-001 T2 tranche 1: sin observador externo no debe haber "
            "sumidero activo antes de la frontera real")
    saved = product_staging._product_root
    try:
        # Sin observador: el resultado es el mismo y no hay a quien
        # entregar eventos (neutralidad sobre la frontera real).
        first = product_staging.product_root()
        second = product_staging.product_root()
        assert first == second and first.is_dir(), (
            "017-001 T2 tranche 1: product_root() debe devolver la misma "
            "raiz existente con o sin marcas: %r vs %r" % (first, second))

        # Con observador: dos lookups con identidad, contexto y rama; los
        # hijos, si existen (rama fria), cuelgan del lookup que los contiene.
        # Con manifiesto en el checkout se parte de cache vacia para
        # ejercitar la primera rama real seguida de la reutilizacion; sin
        # manifiesto no se fuerza una segunda generacion fria (su
        # calibracion dedicada es C-P-cold): se observa la reutilizacion.
        manifest_present = (
            product_staging.REPO_ROOT
            / product_staging.STAGING_MANIFEST).is_file()
        if manifest_present:
            product_staging._product_root = None
        with observed() as seen:
            with use_context(nodeid=NODEID, phase="call",
                             owner_scope="test"):
                third = product_staging.product_root()
                fourth = product_staging.product_root()
        assert (third, fourth) == (first, second), (
            "017-001 T2 tranche 1: las marcas alteraron el resultado de la "
            "frontera real: %r %r vs %r" % (third, fourth, first))
        if external_sink_present:
            # Con observador externo: su sumidero sigue conectado sin el
            # contexto propio y el valor no cambia — el externo no altera
            # la frontera (los eventos del contexto propio se verifican
            # abajo: deben llegar los dos lookups con su rama y contexto).
            later = product_staging.product_root()
            assert later == first, (
                "017-001 T2 tranche 1: el sumidero externo altero el valor "
                "de la frontera real: %r vs %r" % (later, first))
        begins = [r for r in seen if r["event"] == "begin"]
        ends = [r for r in seen if r["event"] == "end"]
        lookups = [r for r in begins if r["operation"] == "product.lookup"]
        assert len(lookups) == 2 and len(begins) == len(ends) == 2 + sum(
            1 for r in begins
            if r["operation"] in {"product.copy", "product.generate"}), (
            "017-001 T2 tranche 1 (PC-1 parte operaciones): la frontera "
            "real debe emitir sus dos lookups con comienzo y fin; sin esos "
            "intervalos no hay calibracion de staging: %r" % seen)
        assert lookups[0]["branch"] in (
            {"checkout-manifest", "cold"} if manifest_present else {"cached"}), (
            "017-001 T2 tranche 1: el primer lookup perdio su rama "
            "(fria, manifiesto del checkout o reutilizacion): %r" % lookups[0])
        assert lookups[1]["branch"] == "cached", (
            "017-001 T2 tranche 1: el segundo lookup no quedo como "
            "reutilizacion: %r" % lookups[1])
        assert lookups[0]["nodeid"] == NODEID, (
            "017-001 T2 tranche 1: se perdio el contexto de test en la "
            "frontera real: %r" % lookups[0])
        for record in begins:
            if record["operation"] in {"product.copy", "product.generate"}:
                assert (record["parent_id"]
                        == lookups[0]["interval_id"]), (
                    "017-001 T2 tranche 1: copia/generacion no cuelga del "
                    "lookup que la contiene: %r" % record)
    finally:
        product_staging._product_root = saved
        if not external_sink_present:
            # observed() ya retiro el sumidero propio; sin externo este
            # detach() es el no-op de seguridad de siempre. Con externo,
            # retiraria el sumidero ajeno del observador y corromperia la
            # medicion de la sesion.
            detach()
