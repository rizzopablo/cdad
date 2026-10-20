# Dictamen — draft-002

**1 BLOCKING · 1 OPTIONAL.** Re-review focal; no aprueba los documentos ni autoriza implementación.

## Identidad revisada

| Documento | SHA-256 |
|---|---|
| `docs/specs/006-004-active-decisions-table/plan.md` | `c8c26d3ed2ba5b058af11530fb3149aade715ec396a570d20f5422d01c98510f` |
| `docs/specs/006-004-active-decisions-table/spec.md` | `a194e5ca67a75a035077735f4a2f4234db2d3c646ddedf0c129517c83bfc0f51` |
| `docs/specs/006-004-active-decisions-table/adr-034-draft.md` | `6e714bb1b5bc1a8e2fbd70e6c23e63c5b4e5004d28970aecdecd4e63336f070d` |

Los dos digests contractuales coinciden. También coinciden las tres fuentes de instrucciones y la política declaradas en el paquete.

## Cierre de los hallazgos anteriores

- **B-1:** resuelta la dependencia circular: U4 verifica plantilla/procedimiento; U5 materializa; U7 comprueba después. La nueva comprobación introduce el defecto B-3 descrito abajo.
- **B-2:** resuelto en el contrato propuesto: digest **base**, re-despacho sobre D1 y evidencia de los bytes aplicados (`plan.md:155-164`). Sigue siendo disciplina de procedimiento, como declara L-7; no se presenta como protección adicional del producto.
- **O-1:** corregido: borrador, aprobación y materialización quedan separados (`plan.md:125-127`).
- **O-2:** corregida la reproducción del principio completo; el ADR remite a su casa canónica (`adr-034-draft.md:12,45`).

## Hallazgos

### B-3 — U7 convierte el inventario inicial en una restricción permanente

**Required · Verdict: BLOCKING · Bucket: m**

**Provenance:** `docs/specs/006-004-active-decisions-table/plan.md:134-144,419-431`; contraste con `spec.md:125` y el upkeep aprobado en el epic §10.2.

U7 exige incorporar a `tests/validate-consistency.sh` comprobaciones sobre la **tabla viva** con exactamente **25 filas vigentes, una obsoleta y ocho ADR Proposed excluidos**. Su gate incluye `make validate`, que ejecuta ese archivo (`Makefile:20-23`).

Ese inventario sirve para acreditar la **siembra inicial**, pero no es una propiedad estable del proyecto. El siguiente ADR aprobado requiere añadir una fila: habrá 26 vigentes y el validador rechazará una tabla correctamente mantenida. Aprobar uno de los Proposed o reemplazar una decisión rompe igualmente las cantidades fijadas.

**Consecuencia:** el procedimiento normal que esta feature introduce obliga a modificar sus tests históricos después de cada cambio legítimo del inventario.

**Remedio estructural:** separar la evidencia puntual de siembra de las invariantes duraderas. Conservar los conteos iniciales en la aceptación de U5/U7; dejar en el validador permanente comprobaciones de coherencia que admitan nuevas aprobaciones y reemplazos.

**Cierre verificable:** después de validar la siembra, un caso descartable añade un ADR aprobado y otro reemplaza una decisión; las tablas actualizadas pasan el comprobador permanente, mientras una fila con archivo inexistente sigue fallando.

### O-3 — El cierre conserva la descripción de la circularidad como obligación vigente

**Nit · Verdict: OPTIONAL · Bucket: m**

**Provenance:** `docs/specs/006-004-active-decisions-table/plan.md:194`.

La frase «U4 no puede pasar su gate sin la siembra» contradice las fichas corregidas y §1.1. El resto del documento permite identificar el orden correcto; es una inconsistencia textual, no una nueva dependencia efectiva.

**Propuesta:** marcar esa frase como descripción de `draft-001` o sustituirla por el orden corregido.

## Validación y evidencia

**Estructural:** el bloque `plan-tasks` es JSON legible. La comprobación de dependencias devolvió:

```text
DAG: U1 -> U2 -> U3 -> U4 -> U5 -> U7 -> U6
```

U1–U7 declaran `detail=next`, campos de validación y ninguna dependencia inexistente. Esto no certifica la corrección semántica de sus gates.

**Comandos de identidad y estado ejecutados:**

```sh
sha256sum docs/specs/006-004-active-decisions-table/{plan,spec}.md
sha256sum docs/specs/006-004-active-decisions-table/adr-034-draft.md docs/epics/epic-006-opencode-concurrency/plan.md
sha256sum skills/cdad-cycle/packets/common.md skills/cdad-cycle/packets/roles/reviewer.md skills/cdad-cycle/packets/substages/reviewer-plan-review.md docs/cdad-policy.json
git rev-parse HEAD
git status --short
```

**HEAD:** `5240389b47a4073cffd894faf280d6e97cfeba28`.

Se leyeron además el dictamen anterior, las superficies contractuales y las reglas canónicas de calibración, verdict-tuple y detalle progresivo. No ejecuté suite completa, generación ni aceptación futura.

**Archivos modificados:** ninguno. **Commit propio:** ninguno. El estado inicial y final conserva los mismos cambios preexistentes:

```text
 M docs/.cdad-state.json
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
?? findings/superlite-transferable-ideas-2026-10-19.md
```

## Abstentions

- No certifico exhaustividad de A-1 ni regresiones verdes: esta revisión contrasta el borrador corregido; todavía no existe su RED implementado.
- No acredito el recorrido real E1–E7 ni la preservación efectiva de ambos escritores. El plan ahora exige esa evidencia, pero U6 sigue pendiente.