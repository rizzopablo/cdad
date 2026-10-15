# Informe RED-FIX (test-writer) — 005-012 T1, bloqueante B2

**Paquete:** `005-012-transition-registration-test-writer-red-008` · **Ejecución:** `exec-005-012-transition-registration-001` · **Tarea:** T1 (review-fix B2)
**Contrato (oráculo):** `docs/specs/005-012-transition-registration/spec.md` sha256 `56d0be4b…edd5` (el pin del paquete; **verificado** con `sha256sum` antes de trabajar — es la spec **enmendada**: PD-10/PD-11/PD-12 vigentes, §2.2, D-7). **Plan:** `…/plan.md` §4 ficha T1. Insumos: `review.md` §1 B2 y su condición de cierre.
**Archivo escrito (único):** `tests/test_005_012_t1_register_transition_base.py` (1 346 líneas; 21 tests = 15 existentes + 6 nuevos). **Commit:** `f7fcbcc`.

*Nota de anonimización:* la raíz del repo se sustituye por `<repo>`; no hay rutas absolutas del dueño, ids crudos de sesión ni nombres de otros proyectos.

## (a) Casos agregados y PD que verifica cada uno

Los cinco casos mínimos del encargo más el control que el plan asigna a este RED, cada uno en su propio test, caja negra sobre el CLI real como subproceso, proyecto descartable en `<tmp>` con el `HOME` del subproceso en un tempdir **vacío**, fixture sintético reutilizado del focal (modos `ready` y `prepared`, construidos **sólo** por el camino legítimo `prepare` → `--record-dispatch` → `receive`).

| # | Test (línea) | Encargo | PD | Verifica |
|---|---|---|---|---|
| 1 | `test_b2_pd10_pd12_two_postconditions_of_the_same_packet_are_two_entries` (`:1043`) | caso 1 | PD-10 + PD-12 | `delivery --stage <misma> --packet <id> --postcondition 1 --outcome green` → rc=0; y **después** `--postcondition 2 --outcome green` → rc=0 y una **SEGUNDA** entrada (no no-op): **dos** entradas de esa etapa, con **claves distintas**, y `postconditions_status` con **las dos** postcondiciones (`green`); `validate-state` rc=0 |
| 2 | `test_b2_pd10_pd12_two_advances_with_the_same_stage_are_two_entries` (`:1104`) | caso 2 | PD-10 + PD-12 | dos `advance` con la **misma** etiqueta y distinto `--current-stage` → **dos** entradas con claves distintas y el state refleja el **último** valor (`merge`); `validate-state` rc=0 |
| 3 | `test_pd11_pd10_noop_is_independent_of_the_head_after_later_appends` (`:1152`) | caso 3 (control D-7) | PD-11 + D-7 | **control**: repetir la invocación idéntica **después de appends posteriores** → rc=0, **sin** tercera entrada, state **byte a byte idéntico** y salida que **nombra** la entrada existente |
| 4 | `test_pd10_entry_carries_a_recomputable_transition_key_payload` (`:1212`) | caso 4 | PD-10 / §2.2 | la entrada lleva `transition_key_payload` y el `transition_key` **se recomputa desde el state**: sha256 de la serialización canónica declarada == `transition_key` |
| 5 | `test_pd10_payload_declares_the_identity_tuple_and_the_effect_inputs` (`:1245`) | caso 4 (contenido) | PD-10 | el payload declara la **tupla** completa **y el insumo con efecto resuelto**: `postcondition == {"n": "1", "outcome": "green"}`, con los digests **resueltos** |
| 6 | `test_pd11_noop_names_the_entry_and_declares_the_annotation_not_written` (`:1297`) | caso 5 | PD-11 | repetir los mismos insumos con efecto cambiando **sólo** la anotación (`--note`/`--by`, fuera del payload) → rc=0, sin segunda entrada, state **byte-idéntico**, salida que **nombra** la entrada existente **y declara** que la anotación no se escribió |

**Caso 6 del encargo (D-12) — no testeado, límite declarado:** las entradas registradas con la **fórmula anterior** conservan su clave y no se invalidan; repetir una de esas invocaciones **anexa** una entrada nueva. No lo aserté: el fixture no puede reproducir una entrada de la fórmula vieja sin **fabricarla** a mano.

## (b) Corrida focal: comando exacto y salida real

```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py -v --tb=line
```
(salida real; raíz del repo sustituida por `<repo>`)

```
collected 21 items
… 15 existentes PASSED …
tests/…::test_b2_pd10_pd12_two_postconditions_of_the_same_packet_are_two_entries FAILED
tests/…::test_b2_pd10_pd12_two_advances_with_the_same_stage_are_two_entries FAILED
tests/…::test_pd11_pd10_noop_is_independent_of_the_head_after_later_appends PASSED
tests/…::test_pd10_entry_carries_a_recomputable_transition_key_payload FAILED
tests/…::test_pd10_payload_declares_the_identity_tuple_and_the_effect_inputs FAILED
tests/…::test_pd11_noop_names_the_entry_and_declares_the_annotation_not_written FAILED
5 failed, 16 passed in 20.98s
=================================== FAILURES ===================================
:1079: AssertionError: PD-10/PD-12 violada (B2): dos postcondiciones distintas del mismo paquete con la misma etiqueta son DOS entradas …; hay 1 entrada(s) de esa etapa (antes 1, después 2): el resultado de la 2ª quedó sin registrar
:1135: AssertionError: PD-10/PD-12 violada (B2): dos `advance` con la misma etiqueta y distinto `--current-stage` son DOS entradas …; hay 1 (antes 1, después 2)
:1232: AssertionError: PD-10 violada (B2): la entrada debe llevar el payload canónico de la identidad como clave nueva y aditiva `transition_key_payload` (§2.2) …: None
:1264: AssertionError: PD-10 violada (B2): falta `transition_key_payload` en la entrada: None
:1337: AssertionError: PD-11 violada (B2): el no-op debe DECLARAR que la anotación de esta invocación no se escribió …; la salida real fue "transition already registered: … no-op, no effects\n"
```

**Lectura del rojo (el defecto B2, reproducido):** los casos 1 y 2 pasan las aserciones de `rc == 0` y caen en la aserción de **conteo de entradas** — la 2ª invocación se tragó como **no-op silencioso** (1 entrada, `postconditions_status` sin la 2ª postcondición). Los casos 4 y 5 caen en la **presencia del payload** (la identidad no es verificable desde el state). El caso 6 cae en la **declaración** del no-op (la salida dice «no-op, no effects» y no declara que la anotación no se escribió).

**Los cinco rojos son `AssertionError` de contrato**: ningún `ImportError`, `SyntaxError`, `JSONDecodeError`, traceback de fixture ni fallo con el prefijo `precondición (fixture…`. **Los 15 tests existentes siguen pasando.**

## (c) Alcance, procedencia y commit

```
$ git show --stat --oneline HEAD | tail -2
f7fcbcc test: 005-012 review-fix B2 RED — identidad con los insumos con efecto (postcondición resuelta, current_stage), payload recomputable y no-op no mudo
 tests/test_005_012_t1_register_transition_base.py | 381 ++++++++++++++++++++++
 1 file changed, 381 insertions(+)
```

- **Un solo archivo escrito y commiteado**, en el alcance declarado (`tests/`): **+381 / −0** ⇒ los 15 casos existentes intactos. Las únicas ediciones sobre texto preexistente son **aditivas al docstring del módulo**; no se reescribió ninguna aserción.
- `M docs/.cdad-state.json` **no es del rol**: es el registro del despacho de este mismo paquete por el orquestador.
- **No se leyó código de implementación**: el archivo **no importa** el módulo (imports reales: stdlib, `pytest` y el módulo de test `test_004_002_t2_bootstrap`); `cdad_packet.py`/`cdad_result.py` aparecen sólo como **rutas de subproceso**. El contrato (PD-10/PD-11/§2.2/D-7 vigentes) fue el único oráculo.
- Sin rutas absolutas del dueño, ids crudos de sesión ni nombres de otros proyectos. No se corrió la suite completa (política: la corre quien cierra).

## (d) Límites y detenciones declarados (no inventé oráculo)

1. **D-12 no testeable con el fixture**: repetir una invocación registrada con la **fórmula anterior** exige **fabricar** una entrada vieja; no lo aserté.
2. **El control de D-7 corre hoy (verde) por construcción**: la clave vieja ya distingue las dos etiquetas usadas, así que el no-op tras appends pasa antes y debe pasar después; lo incluí porque `plan.md` lo asigna a este RED y `review.md` O7(b) lo declaraba sin probar. Es **control**, no rojo.
3. **La declaración de la anotación (PD-11) se asertó de forma estructural y tolerante** (clave de la entrada + el término del campo/bandera de la anotación). El contrato **fija la obligación** pero **no fija la redacción**: decidir si un mensaje dado «declara» lo suficiente queda al sentido de la review.
4. **No re-corrí las regresiones declaradas por la ficha T1** (test-only aditivo dentro del focal): evidencia equivalente por referencia (`re-entry.md`); el GREEN del implementador corre focal + regresiones.
5. **Verificaciones dejadas al gate de aceptación (T8)**: la mitad «árbol» de INV-7 y la byte-identidad de `prepare` con/sin una transición registrada.
6. **Ambigüedad resuelta, no bloqueante:** `PD-12(iii)` («`delivery` de un paquete no `dispatched`») convive con el caso 1 (2ª `delivery` del mismo paquete, que ya quedó `completed`). La lectura que la corrección exige es la **noción derivada del registro de despacho** (la que PD-8(a)/PD-21 usan): «despachado» no es `active_packet.status`. **Si el implementador interpretara que un paquete ya entregado no admite una segunda `delivery`, el caso es de contrato y no del test: detenerse y reportarlo.**
7. **No agregué casos extra** más allá de los mínimos + el control (p. ej. `--current-stage` en `delivery`): quedan al alcance del orquestador.
