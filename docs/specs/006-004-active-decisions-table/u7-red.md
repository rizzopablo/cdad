RED of U7 complete and committed. Here is the role report.

---

# 006-004 U7 RED — «verificación duradera de la tabla»

**Paquete** `006-004-active-decisions-table-test-writer-red-006` · **Contrato** `docs/specs/006-004-active-decisions-table/spec.md` (sha256 `ee88d426…`) · **Ficha** U7 de `plan.md` (sha256 `6b45058b…`) · **Commit** `1bebbc5`

## 1. Archivos (escritura: sólo `tests/`)

| Archivo | Qué es |
|---|---|
| `tests/validate-consistency.sh` (+234) | **El bloque de la siembra de U7** (marcadores `# BEGIN/END 006-004 U7`): el focal que nombra la ficha. 7 comprobaciones, una por invariante duradera, cada una con su código. |
| `tests/test_006_004_u7_seed_verification.py` (nuevo, 845) | **El control negativo del comprobador**: ejecuta el bloque como proceso real sobre proyectos descartables, y vigila el bloque mismo (que no nombre decisiones, que no fije figuras del inventario). |

Fuera de `tests/` no se tocó nada. El estado del árbol tras el commit: sólo `docs/.cdad-state.json`, `docs/planning/` y `findings/` sin trackear — **no míos** (ya estaban así al empezar).

## 2. Mapa test → PD (15 casos, uno por comprobación observable)

| # | Caso | PD / DEC | Estado |
|---|---|---|---|
| 1 | el bloque de la siembra existe (7 códigos) | PD-11 | ✅ |
| 2 | el bloque **no nombra ninguna decisión** | PD-11, DEC-16, INV-16 | ✅ |
| 3 | el bloque **no fija ninguna figura del inventario** | PD-11, DEC-15, INV-15 | ✅ |
| 4 | el bloque **pasa** con una tabla coherente | PD-11 | ✅ |
| 5 | línea → archivo inexistente ⇒ **falla** y lo nombra | PD-11, E4 | ✅ |
| 6 | línea fuera de `docs/adr/` ⇒ falla | PD-11 | ✅ |
| 7 | línea obsoleta **sin** reemplazo ⇒ falla | PD-11 | ✅ |
| 8 | línea obsoleta con reemplazo **inexistente** ⇒ falla | PD-11 | ✅ |
| 9 | rol fuera del vocabulario cerrado ⇒ falla | PD-11 | ✅ |
| 10 | línea con la **forma rota** ⇒ falla | PD-11 | ✅ |
| 11 | archivo apuntado que **re-enuncia el principio** ⇒ falla | PD-11, DEC-16 | ✅ |
| 12 | nota sin «el estado lo declara quien mantiene la tabla» ⇒ falla | PD-11, D-3 | ✅ |
| 13 | sección que no es el **primer H2** ⇒ falla | PD-11 | ✅ |
| 14 | **cierre del comprobador**: (i) desalineada⇒FALLA, (ii) decisión aprobada nueva⇒PASA, (iii) decisión reemplazada expresamente⇒PASA, **digest del bloque idéntico antes y después** | PD-11, E4, V-7 | ✅ |
| 15 | el bloque **pasa con la tabla viva** (el gate de la unidad) | PD-11 | ❌ **RED** |

## 3. A-1 (declarada, plan §4)

**No se reemplaza ningún oráculo vigente.** El bloque sólo **crece**; los 15 casos son **controles negativos añadidos**, no oráculos reemplazados. El bloque que se añade **no fija ninguna figura del inventario** y **no contiene ninguna comprobación por identidad** (DEC-15, DEC-16). Ningún test histórico se editó.

## 4. Por qué el RED falla hoy (la razón, medida)

El bloque encuentra un **defecto real en la tabla sembrada por U5**: la fila de ADR-007 lleva barras sin escapar en la celda de resumen.

```
docs/systemPatterns.md:17
| `docs/adr/ADR-007-perfiles-de-modelos.md` | `obsoleto (reemplazado por ADR-033)` | Perfiles de modelos CDAD (economical | optimus | premium). | `orchestrator` | el propio ADR |
```

La tabla declara 5 columnas; esa fila trae 7 ⇒ la celda de **roles** se lee desplazada (`optimus`), que no está en el vocabulario cerrado. Tal como se renderiza, la fila **no declara** los roles (`orchestrator`) ni la referencia (`el propio ADR`) que dice declarar. El oráculo lo **reporta, no lo salta** — el GREEN corrige la fila sembrada (el dueño de `docs/**` es el orquestador), no el test.

**No se debilitó el oráculo para que pase.** Mutación probada: con una decisión nombrada en el bloque, el control lo detecta (y el auto-chequeo del bloque también); con una figura del inventario fijada, el control lo detecta.

## 5. Comandos y salida

```
$ bash tests/validate-consistency.sh
PASS: 006-004 U7 PD-11-SECTION: the decisions section is the first H2 of the table document
FAIL: 006-004 U7 PD-11-ROLES: the line 'docs/adr/ADR-007-perfiles-de-modelos.md' declares a role outside the closed vocabulary: optimus
PASS: 006-004 U7 PD-11-FILE: every line of the table points to an existing file under docs/adr/
PASS: 006-004 U7 PD-11-REPLACEMENT: every obsolete line names a replacement that exists
PASS: 006-004 U7 PD-11-PRINCIPLE: no file pointed to by the table re-enounces the normative text of the principle
PASS: 006-004 U7 PD-11-NOTE: the note declares that the state is declared by whoever maintains the table
PASS: 006-004 U7 PD-11-NO-ID: this block names no decision
Assert PASS: 181
Assert FAIL: 2          ← 1 = el hallazgo de U7; 1 = F011 (deriva de la instalación del host, preexistente)
FAIL: 2 assert(s) failed.   rc=1

$ python3 -m pytest tests/test_006_004_u7_seed_verification.py -q
1 failed, 14 passed          ← el único rojo: test_pd11_the_block_passes_on_the_live_table (el hallazgo de la fila sembrada)

$ python3 -m pytest tests/test_005_006_t2_intake.py tests/test_004_002_t1_policy.py tests/test_006_005_u7_scribe_role_report.py -q
35 passed                    ← regresiones declaradas de la ficha U7: verdes

$ python3 -m pytest tests/test_006_003_u8_acceptance.py tests/test_004_001_t7_pd10.py -q   (widen: superficie compartida)
1 failed, 20 passed          ← PD-8b: Assert PASS: 182 / Assert FAIL: 1 (el mismo hallazgo de U7)
```

**Validación ampliada** (el validador es superficie compartida): `tests/test_006_003_u8_acceptance.py::test_pd_8b_make_validate_passes_on_the_acceptance_install` **pasa antes de este RED** (`Assert FAIL: 0`) y **falla ahora** con `Assert FAIL: 1` — exactamente el hallazgo de U7. Es la ventana RED normal de un validador compartido (igual que en el RED de U4): **no se reemplaza el oráculo**, vuelve a verde cuando la fila sembrada se corrija. `tests/test_004_001_t7_pd10.py` sigue verde (el bloque no reintroduce las listas retiradas).

## 6. Evidencia puntual (Capa 2) — acreditada aquí, **no** en el validador

- **Inventario sembrado**: 26 filas = **25 vigentes + 1 obsoleta**; **8 ADR `Proposed` excluidos** (ADR-012, 016, 025, 026, 027, 028, 029, 030) de 34 ADR en `docs/adr/`.
- **Ficha de la fila de ADR-034**: existe · `vigente` · roles `architect`, `reviewer` · referencia `skills/cdad-cycle/references/design-principles.md`.
- **Archivo ADR-034 materializado**: existe · estado `Accepted (aprobado el 2026-10-20 …)` — **no** `Proposed` · apunta a la casa única · **no** re-enuncia el texto normativo (0 coincidencias de ventanas de 6 palabras).

Ninguna de estas cifras está en el validador ni en una aserción permanente (DEC-15, DEC-16, INV-15).

## 7. Lo que pido al orquestador

1. **GREEN de U7 = corregir la fila de ADR-007** en `docs/systemPatterns.md:17` (escapar las barras del resumen o reformular la celda) y volver a sembrar/registrar; con eso el bloque queda verde y PD-8b vuelve a `Assert FAIL: 0`. El ADR-034 y el resto de la tabla **no** se tocan.
2. **Nota de ambiente**: en una corrida sin redirigir, `F011` falla por **deriva de la instalación del host** (`.claude/skills/…` desactualizado respecto del árbol del repo tras U1/U4) — es preexistente y ajeno a esta unidad; con la instalación de aceptación (PD-8b) no aparece.
3. El gate de la unidad (ficha U7) sigue: «el bloque pasa con la tabla viva + el control negativo detecta la desalineada y acepta la aprobación nueva y el reemplazo expreso, con el MISMO bloque, cuyo digest no cambia» — las tres cosas quedan **probadas por el control** y el digest medido antes/después es idéntico.

**Commit**: `1bebbc5` — `test: 006-004 U7 RED — verificacion duradera de la tabla` (2 archivos, 1079 inserciones, sólo `tests/`).