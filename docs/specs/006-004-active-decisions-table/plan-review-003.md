# Dictamen — draft-003

**1 BLOCKING · 0 OPTIONAL nuevos.** B-3 queda parcialmente corregido; O-3 queda cerrado. Este dictamen no aprueba ni autoriza implementación.

## Identidad revisada

| Documento | SHA-256 |
|---|---|
| `docs/specs/006-004-active-decisions-table/plan.md` | `a192fbe900d2f6508fac307150c06102168ec5d26e51fbdd3a861b5888108106` |
| `docs/specs/006-004-active-decisions-table/spec.md` | `99b160bcc4c222f0b4d04ec0e01fc004213bbc3f962a61e4250a5280b6b4e6e7` |
| `docs/specs/006-004-active-decisions-table/adr-034-draft.md` | `476086092551c6ab54cb1118d81a80b46235d1b3c1753d7ede689563cee9b76e` |

Los digests contractuales coinciden. También coinciden las tres fuentes de instrucciones y la política del paquete.

## Hallazgo

### B-3 — Persiste una fotografía de vigencia dentro del validador permanente

**Required · Verdict: BLOCKING · Bucket: m**

**Provenance:** `plan.md:147-157,440`; `spec.md:170,204`. Contrato de upkeep: `docs/epics/epic-006-opencode-concurrency/plan.md:278-279`.

La corrección elimina los conteos permanentes, pero U7 todavía exige que **ADR-034 permanezca `vigente`, con sus roles y referencia iniciales**. Esa condición no es una invariante duradera: sigue fijando parte del inventario sembrado.

Recorrido permitido por el contrato:

1. Se aprueba un ADR que reemplaza ADR-034 —por ejemplo, una revisión de su alcance, conservando la casa canónica del principio—.
2. El orquestador conserva ADR-034 como `obsoleto`, declara su reemplazo existente y añade la fila nueva.
3. La tabla cumple el procedimiento de upkeep, pero incumple la exigencia permanente de U7 de que ADR-034 sea `vigente`.

**Consecuencia:** mantener correctamente esa decisión vuelve a exigir modificar tests históricos, o conservar una vigencia falsa. El caso descartable puede reemplazar otra decisión y pasar sin detectar esta restricción.

**Remedio estructural:** llevar también el estado, los roles y la referencia iniciales de ADR-034 a la evidencia puntual de siembra. Conservar en el validador las propiedades de coherencia que admiten el reemplazo de cualquier decisión, sin excepciones de vigencia por identidad.

**Cierre verificable:** además de agregar un ADR y rechazar un archivo inexistente, el caso descartable **reemplaza expresamente ADR-034**. La tabla actualizada pasa el mismo comprobador permanente, sin editarlo; ADR-034 queda obsoleto y la fila sucesora vigente.

## Hallazgos anteriores

- **B-1 sigue cerrado:** U4 verifica plantilla/procedimiento; U5 materializa; U7 verifica después (`plan.md:114-160`).
- **B-2 sigue cerrado en el contrato propuesto:** digest base, rechazo, re-despacho y evidencia de bytes aplicados (`plan.md:171-180`). Sigue siendo procedimiento, no una capacidad nueva del materializador.
- **O-1 sigue cerrado:** borrador, aprobación y materialización están separados (`plan.md:135-138`).
- **O-2 sigue cerrado:** el ADR referencia la casa canónica en lugar de reproducir el principio completo (`adr-034-draft.md:12,45`).
- **O-3 cerrado:** el cierre declara el orden corregido, sin la obligación circular anterior (`plan.md:210`).

## Validación y evidencia

**Estructural:** se parseó el bloque `plan-tasks` con `json.loads`; se comprobaron dependencias existentes, campos de validación y ausencia de paralelismo. Salida:

```text
U1 detail=next validation_fields=True
U2 detail=next validation_fields=True
U3 detail=next validation_fields=True
U4 detail=next validation_fields=True
U5 detail=next validation_fields=True
U7 detail=next validation_fields=True
U6 detail=next validation_fields=True
DAG: U1 -> U2 -> U3 -> U4 -> U5 -> U7 -> U6
```

Esto no certifica la semántica del comprobador futuro.

**Comandos de identidad y estado ejecutados:**

```sh
sha256sum docs/specs/006-004-active-decisions-table/{plan.md,spec.md}
sha256sum docs/specs/006-004-active-decisions-table/adr-034-draft.md docs/epics/epic-006-opencode-concurrency/plan.md skills/cdad-cycle/packets/common.md skills/cdad-cycle/packets/roles/reviewer.md skills/cdad-cycle/packets/substages/reviewer-plan-review.md docs/cdad-policy.json
git rev-parse HEAD
git status --short
```

**HEAD observado:** `474c12fdfa8ef433b51db438e001a9e0deb022e5`.

**Archivos modificados:** ninguno. **Commit propio:** ninguno. El estado inicial y final conserva:

```text
 M docs/.cdad-state.json
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
?? findings/superlite-transferable-ideas-2026-10-19.md
```

No ejecuté suite completa, generación ni aceptación futura.

## Abstentions

- No acredito el comportamiento del comprobador futuro: el defecto señalado es una contradicción del contrato propuesto, no un fallo ejecutado.
- No certifico regresiones verdes ni aceptación real E1–E7; sus pruebas y recorridos siguen pendientes.
- La entrega completa de todas las decisiones aplicables sigue dependiendo del procedimiento del orquestador, conforme a D-1. Esta revisión no convierte esa limitación aceptada en una garantía mecánica.