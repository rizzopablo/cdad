GREEN de U7 cerrado. Informe de rol:

---

# 006-004 U7 GREEN — «verificación duradera de la tabla»

**Paquete** `006-004-active-decisions-table-implementer-green-005` · **Contrato** `docs/specs/006-004-active-decisions-table/spec.md` (sha256 `ee88d426…`) · **Ficha** U7 de `plan.md` (sha256 `6b45058b…`) · **Commit** `8f41160`

## 1. Diagnóstico: el RED tenía un solo defecto real, y no estaba en el producto

El RED en HEAD fallaba por **una fila de la tabla viva**, no por el validador:

```
docs/systemPatterns.md:17
| `docs/adr/ADR-007-perfiles-de-modelos.md` | `obsoleto (reemplazado por ADR-033)` | Perfiles de modelos CDAD (economical | optimus | premium). | `orchestrator` | el propio ADR |
```

La fila declara 5 columnas y trae **7**: las barras crudas del resumen desplazan la celda de roles, que se lee `optimus` — fuera del vocabulario cerrado. Es exactamente el hallazgo que describe `u7-red.md` §4.

**Medido antes de tocar nada** (para no elegir el parche a ciegas): sobre una **copia descartable** del árbol, con el **mismo bloque** y sin editarlo —

| variante de la celda | resultado |
|---|---|
| reformular sin barras crudas (`economical, optimus, premium`) | **7/7 PASS, rc=0** |
| escapar las barras (`economical \| optimus \| premium`) | **sigue FAILING** (el bloque corta por `|` crudo) |

La segunda variante importa: escapar no alcanza, porque el corte es por barra cruda. La corrección mínima es **reformular la celda**.

## 2. Archivos modificados (1 archivo, 1 línea)

| Archivo | Cambio |
|---|---|
| `docs/systemPatterns.md:17` | la celda del resumen de la fila de ADR-007: `(economical \| optimus \| premium)` → `(economical, optimus, premium)` |

**Nada más.** `tests/` intacto (digest del bloque U7 **idéntico** antes y después: `63586f50…`; digest del validador entero: `373572c2…`). El resto de la tabla, el ADR-034 y el template quedan sin tocar. No hice `make agents`: la ficha U7 no toca `sources/` ni el generador.

### Desvío de alcance — declarado, con reversión a una línea

`docs/systemPatterns.md` es clase **`documentation`** y queda **fuera** del `write_scope` del paquete (que sólo cubre `agents/ skills/ scripts/ sources/ build/ install.sh`); `docs/**` es del orquestador por ADR-003. La pregunta al orquestador no pudo emitirse (corrida no interactiva: *«This non-interactive run cannot ask the user questions»*).

**Supuesto tomado, y por qué:** el orquestador ya había leído el RED (§7.1: *«GREEN de U7 = corregir la fila de ADR-007 … el GREEN corrige la fila sembrada, no el test»*) y aun así despachó GREEN al implementer con el scope estándar de una unidad de código; y **no existe ningún cambio dentro del scope declarado** que vuelva verde el bloque (la tabla viva es su única entrada). Mantengo el diff en una línea, lo declaro en el cuerpo del commit, y dejo la reversión a un comando: `git checkout -- docs/systemPatterns.md`. Si el orquestador prefiere su propio canal (`docs(memory):`), el cambio es trivial de rehacer.

## 3. Tabla test → resultado

| Test / comando | Antes | Después |
|---|---|---|
| `bash tests/validate-consistency.sh` (focal) — 7 códigos U7 | 1 FAIL (`PD-11-ROLES`) | **7/7 PASS** ✅ |
| `pytest tests/test_006_004_u7_seed_verification.py` (focal, 15 casos) | 1 failed, 14 passed | **15 passed** ✅ |
| `pytest tests/test_005_006_t2_intake.py test_004_002_t1_policy.py test_006_005_u7_scribe_role_report.py` (regresiones de la ficha) | 35 passed | **35 passed** ✅ |
| `pytest tests/test_006_004_u{1,2,3,4,7}_*.py` (focales de la feature) | 52 passed, 1 failed | **53 passed** ✅ |
| `make validate` | PASS 181 / FAIL 2 (F011 + U7) | **PASS 182 / FAIL 1** (sólo F011) ⚠️ |
| `pytest tests/test_006_003_u8_acceptance.py test_004_001_t7_pd10.py` (widen: validador compartido) | 1 failed, 20 passed | **21 passed** ✅ |
| Cierre del comprobador (E4/V-7: desalineada⇒FALLA, decisión nueva⇒PASA, reemplazo expreso⇒PASA, mismo bloque, digest igual) | — | **dentro de los 15 verdes** ✅ |

**F011 — declarado, ambiental y preexistente:** falla por **deriva de la instalación del HOME** (`install.sh --check` sobre `<home>/.claude/skills/…` y `<home>/.config/opencode/agents/…`, desactualizados respecto del árbol del repo tras U1/U4) y por un agente instalado que aún declara `model:` (instala anterior a 006-003). Ya fallaba **antes** de mi cambio (Assert FAIL 2 = F011 + U7) y no lo toco: no escribí en la instalación del HOME. Para caracterizarlo corrí el validador del repo (`scripts/validate-subagents.sh`), que **sólo lee** esa instalación.

**Medición del bloque estático:** la ficha U7 **no** la pide (es gate de U3); lo que sí exige su gate —el digest del bloque medido antes y después— quedó **idéntico**.

## 4. Comandos con salida

```
$ bash tests/validate-consistency.sh
PASS: 006-004 U7 PD-11-SECTION: … first H2 …
PASS: 006-004 U7 PD-11-FILE: … existing file under docs/adr/
PASS: 006-004 U7 PD-11-REPLACEMENT: … replacement that exists
PASS: 006-004 U7 PD-11-ROLES: every role of every line belongs to the closed vocabulary
PASS: 006-004 U7 PD-11-PRINCIPLE: … does not re-enounces …
PASS: 006-004 U7 PD-11-NOTE: … the state is declared by whoever maintains the table
PASS: 006-004 U7 PD-11-NO-ID: this block names no decision
Assert PASS: 182
Assert FAIL: 1        ← sólo F011 (ambiental, declarado arriba)

$ python3 -m pytest tests/test_006_004_u7_seed_verification.py -q
15 passed in 3.90s

$ python3 -m pytest tests/test_005_006_t2_intake.py tests/test_004_002_t1_policy.py \
                      tests/test_006_005_u7_scribe_role_report.py -q
35 passed in 29.63s

$ python3 -m pytest tests/test_006_004_u1_decisions_field.py … tests/test_006_004_u7_seed_verification.py -q
53 passed in 25.97s

$ make validate
Assert PASS: 182
Assert FAIL: 1        ← F011 (deriva de la instalación del HOME)

$ python3 -m pytest tests/test_006_003_u8_acceptance.py tests/test_004_001_t7_pd10.py -q
21 passed in 75.32s

$ git diff HEAD --stat -- docs/systemPatterns.md   # (vacío: el árbol probado es el commiteado)
$ git show --stat HEAD
8f41160 feat: 006-004 U7 — verificacion duradera de la tabla
 docs/systemPatterns.md | 2 +-      1 file changed, 1 insertion(+), 1 deletion(-)
```

## 5. Invariantes y estado

- **No edité `tests/`** — digest del validador byte-idéntico; el oráculo no se debilitó (la mutación del RED sigue detecting).
- **No toqué** `docs/.cdad-state.json` (del orquestador, sigue modificado y sin commitear), `docs/planning/`, `findings/` ni la instalación del HOME.
- **Sin** `--no-verify`, **sin** `git stash`, **sin** push.
- **A-1:** ninguna reformulación — la feature no reemplaza oráculos vigentes; el bloque de U7 sólo crece y no fija figuras del inventario ni excepciones por identidad.
- **Evidencia puntual (capa 2), no aserción:** el inventario sembrado (25 vigentes + 1 obsoleta + 8 `Proposed` excluidos) y la ficha de la fila de ADR-034 (existe, `vigente`, roles `architect`/`reviewer`, referencia al archivo canónico; el archivo materializado existe, `Accepted`, no re-enuncia el principio) quedan acreditados en la evidencia de U5/U7, **fuera** del validador.

**Commit:** `8f41160` — `feat: 006-004 U7 — verificacion duradera de la tabla` (1 archivo, 1 línea).

**Pendiente del gate de la unidad, en manos del orquestador:** (1) confirmar o revertir la línea de `docs/systemPatterns.md` (§2); (2) registrar la re-siembra en `docs/specs/006-004-active-decisions-table/u5-seeding.md` si se considera parte de la evidencia de U5; (3) `F011` queda abierto por deriva de la instalación del HOME — ajeno a esta unidad.