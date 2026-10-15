# Review — T4 (004-003): bloque plan-tasks obligatorio + plan de validación por unidad + F1 + F2

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-19>`.
> Paquete: `004-003-planning-procedures-reviewer-review-006`.
> **Dictamen: changes-required (2 bloqueantes, 1 opcional, 1 nit, 1 FYI).**
>
> *Nota del orquestador:* este archivo se materializó tarde — la entrada de
> `stage_history` `review-1-t4` lo citó antes de existir. Error detectado por el
> re-review focal (R1) y corregido aquí. Registrado en `supervision-record.md`.

**Artefacto:** commits `5126c75..37911a2` — `37911a2` (GREEN PD-8/F1), `b0e4424` (registro §4.1), `2461bed`+`b67a5ee` (migración de fixtures), `e7fbca7` (docs de evidencia RED). El RED (`5126c75`) precede al GREEN ✓.
**Contrato:** `spec.md` sha256 `ba395fed…bf766` **verificado ✓**.

## Verificación realizada

| Comando | Resultado |
|---|---|
| `sha256sum …/spec.md` | `ba395fe…bf766` = contract ✓ |
| `git log --oneline 5126c75..37911a2` | 5 commits ✓ |
| `git diff --stat 5126c75..37911a2` | 8 archivos, +216/−34; diff de tests revisado línea por línea; **ninguna aserción retirada** |
| `pytest tests/test_004_003_t4_validation_fields.py tests/test_004_003_t{1,2,3}_*.py -q` | **24 passed** ✓ |
| `make validate` | FAIL: 2 asserts (drift de install + A3), descompuestos abajo |
| `git log <rango> -- skills/cdad-cycle/references/stage-2-specification.md` | **vacío** |
| `grep "focal\|regresion\|gate de\|plan de validación" stage-2-specification.md` | rc=1 (nada) |
| `grep "observable_checks" planning-contract-draft.md` | rc=1 (nada) |
| `grep "validation_strategy\|@validation" planning-contract-draft.md` | sin hit |

## Bloqueantes

**F-A — Required · bucket m — `plan.md:20,34` vs. el rango revisado.** La fila T4 del plan aprobado y §5/G5 declaran `stage-2-specification.md` entre los archivos de T4 y como segundo dueño canónico del campo de plan de validación por unidad. **Cero commits en el rango lo tocan** y el grep confirma que no tiene el campo, ni referencia a `plan-tasks`, ni vocabulario de focales/regresiones/gate. PD-12/invariante 6 violado hoy: el procedimiento de stage-2 discrepa en silencio con un esquema obligatorio que `prepare` ya enforcea — un autor que siga solo stage-2 produce planes rechazados, sin rastro hacia §4.1. **Remedio estructural:** una edición en `stage-2-specification.md` que *referencie* `planning-contract-draft.md` §4.1 (sin segundo manual), o un re-alcance trazado de ese actor a T7 registrado en `plan.md` — una de las dos, con justificación, antes de cerrar T4.

**F-B — Required · bucket m — `planning-contract-draft.md` §4.1 (`b0e4424`) vs. `tests/test_004_003_t4_validation_fields.py:89-102,140-145,229-266`.** El registro §4.1 — el entregable explícito de F2 — **no es fiel al formato que los tests fijan**:
1. `observable_checks` como clave JSON **no aparece** en el documento (la prosa dice "comprobaciones observables", pero quien derive el formato del ejemplo de §4.1 no conoce el nombre de la clave; el esquema lo enforcea en `cdad_packet.py:2445-2467`).
2. `validation_strategy` (campo a nivel de plan, `cdad_packet.py:2309-2312`) y el literal `"@validation_strategy"` (`:2262`) están ausentes de §4.1 y de todo el documento. El mecanismo de referencia de estrategia que PD-8 manda ("referenciar una estrategia común una vez") está implementado y testeado, pero su única declaración vive **dentro de la implementación y del test** — exactamente el "hogar de facto competidor" que F2 debía cerrar.
3. Habilitante: el test F2 (`:564-576`) fija solo los *tokens de prosa en castellano*, nunca un nombre de parámetro — más débil que el oráculo que su propio docstring RED declara.

**Remedio:** extender el ejemplo único de §4.1 con `observable_checks` (variante sin código o segunda tarea), declarar `validation_strategy` + el `@literal` en el mismo fence; y fortalecer el test F2 para tomar los nombres de campo como tokens, de modo que el registro no pueda derivar otra vez.

## Required no bloqueante

**F-C — bucket l — `cdad_packet.py:2465-2471` vs. `tests/test_004_003_t4_validation_fields.py:46-48`.** El oráculo RED dice que una tarea puede referenciar la estrategia "en lugar de repetir contenido en `focal_tests`, `regressions` **o** `integration_gate`". Implementación: `integration_gate` acepta el literal (y `["@validation_strategy"]` vía `_is_strategy_ref`), `regressions` lo rechaza ("must declare its regressions"). Asimétrico, no descubierto porque ningún test fija la forma desnuda en regressions, y el fallo es ruidoso (no skip silencioso). **Remedio:** agregar `_is_strategy_ref(entry["regressions"])` al guard, o enmendar el texto del oráculo en ambos docstrings.

## Nits / opcionales

- **F-D — Nit · bucket l — `planning-contract-draft.md:95-107`.** El ejemplo de §4.1 (ilustrativo) muestra una tarea que consume `contract: "contrato-v1"` de `producer: "T0"` sin declarar T0; ejecutado por `prepare` es el defecto "entrada sin productor". Sugerencia: declarar T0 en el ejemplo o anotar el bloque como solo-formato.
- **F-E — FYI · bucket l — `tests/validate-odoo-specialization.sh:260-264`.** El escáner A3 recorre `tests/` incluyendo `__pycache__/*.pyc`, así que cualquier corrida de tests crea ruido transitorio de patrones sensibles. Agregar `--exclude=__pycache__`. Fuera del alcance de este diff.

## Verificaciones positivas (observables comprobados)

- **F1 cerrado correctamente:** las cinco variantes malformadas (open indentado, sin cierre, tag, CRLF, segundo bloque) fallan ruidoso. El cruce conteo-de-token × match-regex en `cdad_packet.py:2286-2295` no deja camino de skip silencioso; un cuerpo que rompe el JSON falla ruidoso en `:2297-2300`.
- **La migración de fixtures no debilitó garantías, las fortaleció:** pre-T4 los fixtures de T1/T2/T3 usaban la base sin bloque, que caía en la leniencia de T3 — sus checks estructurales se *saltaban* en silencio. Post-migración llevan bloques válidos completos, así que los mismos tests ejercitan la cadena completa. Orden verificado en `prepare` (`:2567-2569`): los defectos estructurales de T3 levantan *antes* que los de plan de validación. Las aserciones de `sha256` se actualizaron al nuevo contenido del fixture — consecuencia legítima de PD-8, autorizada y registrada, no acomodo: el *objeto* de la aserción (el paquete lleva el sha del borrador) no cambió.
- **Anti-gaming intacto:** tests black-box por subprocess; los commits del test-writer (`5126c75`) preceden al GREEN (`37911a2`); la implementación no editó tests.
- **Coherencia de estado:** `t3-closed → tdd-red-t4` consistente con el rango.

**Verdict tuple:** F-A (BLOCKING, m, verificado) · F-B (BLOCKING, m, verificado) · F-C (OPTIONAL, l, verificado).

## Abstenciones

- El RED citado en el state ("5 failed / 3 passed" en `5126c75`) es estado histórico no re-ejecutable sin forzar fallos; no re-verificado.
- `validate-subagents.sh` drift: no se construyó un worktree base para probar preexistencia; la atribución a instalación stale en `$HOME` es basada en evidencia (paths intactos) pero el estado verde *histórico* de `make validate` dentro de la feature queda UNKNOWN (PD-7/PD-5: declaración explícita, no equivalencia asumida).
- El hit de A3 sobre `tests/test_role_packets.py` se confirmó contra `tests/.sensitive-patterns.local` (contenido no divulgado); si el árbol pasaba A3 en `5126c75` bajo el mismo archivo de patrones locales no se re-verificó pre-rango.
- No se evaluó la calidad semántica (PD-2) de los fixtures más allá del contrato estructural: las formas son válidas; si `focal_tests: ["tests/test_004_003_t1_draft_contract.py"]` es un focal *significativo* es juicio de plan-review, no un hecho de corrección establecido aquí.
