# Dictamen — draft-004

**0 BLOCKING · 0 OPTIONAL nuevos.** B-3 queda cerrado **en el contrato propuesto**. No apruebo los documentos ni autorizo implementación.

## Identidad revisada

Rutas relativas a `docs/specs/006-004-active-decisions-table/`:

| Documento | SHA-256 |
|---|---|
| `plan.md` | `dc0d31fb2fb01023a73c10e5e7692ccb897765275a1707830864e6044846ec06` |
| `spec.md` | `9ceb7a25682c82689464e92266ec840cb81fdd4b03e6428b2e78aa5d706f2a02` |
| `adr-034-draft.md` | `001cd5515c5d07715e1a4befd6daf7d676727e8b40c0cabe11875029e9402941` |

Los digests contractuales coinciden. También coinciden las tres fuentes de instrucciones y la política del paquete.

## Cierre de hallazgos

- **B-3:** el inventario y la ficha inicial de ADR-034 pasan a evidencia puntual; el validador permanente no fija identidades, estados, roles ni referencias particulares (`plan.md:140-165`; `spec.md:179,213-214`). El cierre exige agregar una decisión, **reemplazar expresamente ADR-034** y rechazar un archivo inexistente, usando el mismo comprobador y verificando su digest (`plan.md:47-50,165-168,444-461`). Esto satisface la condición solicitada en `plan-review-003.md:33-35`, sin retirar las comprobaciones generales de coherencia.
- **B-1 sigue cerrado:** U4 verifica plantilla/procedimiento sin siembra; U5 materializa; U7 verifica después (`plan.md:121-168,218`).
- **B-2 sigue cerrado:** digest base, rechazo, re-despacho sobre D1 y evidencia de los bytes aplicados (`plan.md:179-190`). Sigue siendo disciplina del procedimiento, no una nueva garantía del materializador.
- **O-1 sigue cerrado:** borrador, aprobación y materialización permanecen separados (`plan.md:142-148`; `adr-034-draft.md:3-9`).
- **O-2 sigue cerrado:** el ADR referencia la casa canónica sin reproducir el principio completo (`adr-034-draft.md:13,46`).
- **O-3 sigue cerrado:** el cierre conserva el orden corregido, sin la obligación circular (`plan.md:218`).

No identifico una regresión material introducida por esta corrección. La entrega de **todas** las decisiones aplicables continúa dependiendo del procedimiento del orquestador, limitación expresamente aceptada en `execution.md:403-407`; no se convierte aquí en garantía mecánica.

## Validación y evidencia

**Estructural, separada del juicio semántico:** se parseó `plan-tasks` con `json.loads`, comprobando dependencias anteriores, ausencia de paralelismo y campos de validación conforme a la regla canónica de detalle progresivo.

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

**Comandos de identidad y contraste ejecutados:**

```sh
sha256sum docs/specs/006-004-active-decisions-table/{plan.md,spec.md}
sha256sum skills/cdad-cycle/packets/common.md skills/cdad-cycle/packets/roles/reviewer.md skills/cdad-cycle/packets/substages/reviewer-plan-review.md docs/cdad-policy.json docs/specs/006-004-active-decisions-table/adr-034-draft.md
sha256sum docs/epics/epic-006-opencode-concurrency/plan.md
git log -4 --oneline -- docs/specs/006-004-active-decisions-table/plan.md
git diff 474c12fdfa8ef433b51db438e001a9e0deb022e5 HEAD -- docs/specs/006-004-active-decisions-table/{plan.md,spec.md,adr-034-draft.md}
git rev-parse HEAD
git status --short
```

El contrato de la épica devuelve `d6da11dbed6571039c05b237eb257388c616d290028d6c9c5ce1cf0a3baf9809`. Se contrastó además `_apply_copy` en `cdad_result.py:822-855`: compara el destino con el digest esperado; no acredita la base de redacción.

**HEAD observado:** `1fc0dafbddf7f634289a2ddb5e2474711d555f6d`.

**Archivos modificados:** ninguno. **Commit propio:** ninguno. Estado inicial y final idéntico:

```text
 M docs/.cdad-state.json
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
?? findings/superlite-transferable-ideas-2026-10-19.md
```

No ejecuté suite completa, generación ni aceptación futura.

## Abstentions

- No acredito todavía que el comprobador admita el reemplazo real: U7 debe aportar las corridas y digests exigidos.
- No certifico regresiones verdes, exhaustividad de A-1 ni aceptación real E1–E7: sus pruebas y recorridos siguen pendientes.
- No certifico completitud automática de la distribución ni resolución íntegra de referencias en la ruta de paquete; permanecen los límites D-1 y D-2 aceptados.