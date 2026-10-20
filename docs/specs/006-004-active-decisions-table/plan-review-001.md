# Dictamen — 006-004, draft-001

**2 BLOCKING · 2 OPTIONAL.** El plan contiene una dependencia circular de validación y un procedimiento CAS que puede sobrescribir la tabla que promete preservar. No apruebo ni autorizo implementación.

## Identidad revisada

| Documento | SHA-256 |
|---|---|
| `docs/specs/006-004-active-decisions-table/spec.md` | `20fc4fb9b1b0ff55a0c277e9cd320dc24a09f75dc5ce3e688f16c3e58956b237` |
| `docs/specs/006-004-active-decisions-table/plan.md` | `2a16f174c69becc94e13a3db1e364b0d82c9424b0e513f4d421fc25dbc175903` |
| `docs/specs/006-004-active-decisions-table/adr-034-draft.md` | `e6baabaefc442fe95d37f1d7ceb8ecb2d1b4926bde78c4baf6fb95546821fa2d` |

Los dos digests contractuales coinciden. Los buckets son `m`: citas verificables y contrato/convenios leídos; no atribuyo diversidad de modelo ni evidencia de un diff implementado.

## Hallazgos BLOCKING

### B-1 — U4 exige documentos que solamente produce U5

**Required · Verdict: BLOCKING · Bucket: m**

**Provenance:** `docs/specs/006-004-active-decisions-table/plan.md:85-106`; `Makefile:20-23`.

U4 incorpora a `tests/validate-consistency.sh` comprobaciones sobre la **tabla viva** y la existencia de ADR-034, y exige `make validate` verde. Pero ambos documentos los produce U5, que depende de U4.

No es una comprobación «verificable sin materializar»: actualmente la sección no existe y ADR-034 tampoco. Al llegar al GREEN de U4, sus productores siguen pendientes. Ni el implementer puede escribir esos documentos ni el orquestador puede ejecutar U5 respetando la dependencia declarada.

**Remedio estructural:** separar las comprobaciones de plantilla/procedimiento de las comprobaciones de siembra. Ubicar estas últimas en una unidad cuyo gate sea posterior a la materialización de U5, conservando los responsables de cada superficie.

**Cierre verificable:** existe un orden de ejecución en el que cada unidad pasa su gate sin documentos de unidades pendientes, sin saltarse dependencias ni ampliar permisos.

### B-2 — Usar el digest actual no detecta una propuesta obsoleta del scribe

**Required · Verdict: BLOCKING · Bucket: m**

**Provenance:** `docs/specs/006-004-active-decisions-table/spec.md:113,138`; `docs/specs/006-004-active-decisions-table/plan.md:121`; implementación existente: `skills/cdad-cycle/scripts/cdad_result.py:827-854,938-960`.

La spec prescribe materializar contra el digest **actual** y afirma que así se detecta que el destino cambió. El materializador solamente compara el destino con `expected_previous_sha256`; no comprueba contra qué versión redactó el scribe.

Recorrido normal:

1. El scribe redacta sobre D0.
2. El orquestador añade una fila, produciendo D1.
3. La autorización usa el digest actual D1.
4. El CAS pasa y copia la propuesta antigua: desaparece la fila añadida.

Además, tras un rechazo, cambiar solamente el digest esperado no reconcilia contenido: `materialize` copia la parte recibida. El plan no identifica cómo se produce y autoriza la versión fusionada que promete volver a materializar.

**Remedio estructural:** conservar el digest base de la propuesta para el primer CAS; después del conflicto, declarar una vía existente para producir y aplicar el documento reconciliado, sin alterar la entrega recibida ni sustituir una fusión por actualizar el digest.

**Cierre verificable:** U6 demuestra D0 → propuesta del scribe → D1 del orquestador → rechazo con base D0 → reconciliación autorizada. El documento final conserva **tanto la fila nueva como los cambios del scribe**, y la evidencia identifica los bytes aplicados.

## Hallazgos OPTIONAL

### O-1 — PD-11 exige simultáneamente una fila vigente y un ADR pendiente

**Verdict: OPTIONAL · Bucket: m**

**Provenance:** `docs/specs/006-004-active-decisions-table/spec.md:140`; `docs/specs/006-004-active-decisions-table/plan.md:104-106`.

PD-11 describe ADR-034 como *Proposed, a la espera de aprobación*, mientras U5 exige aprobación previa para sembrarlo vigente. El plan permite interpretar correctamente el orden, pero la postcondición mezcla el borrador previo con el estado de aceptación.

**Propuesta:** distinguir explícitamente ambas fases; la comprobación final debe reconocer la aprobación separada, no exigir que siga pendiente.

### O-2 — El ADR entregado re-enuncia el principio que declara no copiar

**Verdict: OPTIONAL · Bucket: m**

**Provenance:** `docs/specs/006-004-active-decisions-table/adr-034-draft.md:11,21`; `docs/specs/006-004-active-decisions-table/plan.md:107`.

El contexto reproduce el principio y su límite, pese a que U5 exige materializar un ADR que los referencia sin re-enunciarlos. No rompe por sí solo la unicidad del **árbol instalable**, pero contradice el artefacto documental solicitado.

**Propuesta:** sustituir la reproducción por la referencia al contrato aprobado y a la casa canónica.

## Validación y evidencia

**Separación estructural/semántica:** el bloque `plan-tasks` es JSON legible; U1–U6 declaran `detail: next`, campos de validación y dependencias existentes. Esa comprobación no resuelve B-1 ni B-2.

Comandos de comprobación ejecutados:

```sh
sha256sum docs/specs/006-004-active-decisions-table/{spec.md,plan.md}
git rev-parse HEAD
git status --short
```

**Salida relevante:** digests coincidentes; HEAD `9b676b51757a104ecb9cee7fd3f724f9830af507`. El estado inicial y final mostró los mismos cambios preexistentes:

```text
 M docs/.cdad-state.json
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
?? findings/superlite-transferable-ideas-2026-10-19.md
```

La comprobación Python de hashes, tareas y productores devolvió:

```text
instruction common.md: match=True
instruction roles/reviewer.md: match=True
instruction substages/reviewer-plan-review.md: match=True
U1–U6: validation_fields=True; missing_deps=set()
docs/systemPatterns.md: exists=True; seed_section=False
docs/adr/ADR-034-principio-general-antes-especifico.md: exists=False
```

**Archivos modificados por esta revisión:** ninguno. **Commit propio:** ninguno. No ejecuté suite completa ni generación.

## Abstentions

- No certifico que A-1 esté exhaustivamente cubierto: revisé superficies existentes relevantes, pero todavía no existe el RED de esta feature que contraste todas las regresiones declaradas.
- No acredito aceptación real ni comportamiento del producto instalado futuro: U6 sigue pendiente. D-1 y D-2 son límites expresamente aceptados en las decisiones de entrada; no los convierto en bloqueantes nuevos.