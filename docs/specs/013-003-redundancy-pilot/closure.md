# Closure — 013-003-redundancy-pilot

**Epic:** `epic-013-test-criterion` — orden 3/4. **Cerrada:** 2026-11-02.
**Contrato:** `docs/specs/013-003-redundancy-pilot/spec.md`, sha256
`b8c4810d3a7e44fb54fa7c4edf540269d57fb31168d2c7cfb2457fca08baedbb`, aprobado por Pablo
(HITL delegada, `docs/epics/epic-013-test-criterion/execution.md`) el 2026-11-02.
**Estado:** cerrada en el repositorio; **no publicada ni desplegada**.

## 1. Resultado

El lote B1 de `tests/test_005_013_t1_unit_projection.py` quedó decidido con evidencia
contrastada: **Mantener A, Mantener B, Mantener C**, sin retiro, sustitución ni consolidación, y
**sin cambios en tests, mapa, inventario ni implementación**. Delta de tests y delta de mapa
**explícitamente vacíos con su razón**. La hipótesis del epic —poda de redundancia— **no se
confirma en este lote**: el piloto demuestra el procedimiento y que **Mantener es un resultado
legítimo, no un ahorro**.

Producto: `1e1ad7e3..a978b376` (**4 archivos, +646/−9**): `spec.md` (+244), `test-audit.md` (+98),
`review.md` (+89) y `docs/.cdad-state.json`. Verificado: el rango **no toca** `tests/`,
`docs/specs/008-002-suite-by-capability/` ni `docs/suite-maintenance.md`.

## 2. Evidencia (PC-8: cinco registros separados)

### 2.1 Control estructural

`python3 scripts/cdad-suite.py validate` → **rc=0** sobre `027064fb` (revisión que contiene el
AUDIT y el delta vacío materializados). Medido por la revisión independiente; **no se declara
equivalencia semántica** por `rc=0` (PC-8, 013-002 PC-4).

### 2.2 Ejecución focal

- Selección A/B/C (`3` nodeids de `tests/test_005_013_t1_unit_projection.py`), `-q
  -p no:cacheprovider`: **`3 passed in 3.10s`, RC=0** en `06fe83ce` (AUDIT, árbol limpio) y
  **`3 passed in 2.80s`**, RC=0 en `027064fb` (review).
- Contraste histórico 013-002 (`test_013_002_C_mapa_inicial_B1_identificado_por_entrada` +
  `test_013_002_C_conserva_origen_y_metadatos_historicos`): **`2 passed`, RC=0**.
- Configuración: `HOME` aislado por fixture (tempdir, nunca real); ids `999-…` sintéticos;
  `CLI_TIMEOUT_S=120`. Sin fallo inicial que declarar.
- Estas corridas son las registradas por AUDIT y review; **quien suscribe no las reprodujo**.

### 2.3 Revisión semántica del lote

`review.md` (ruta C válida: `render` == `PACKET.md`, `cmp` rc=0; revisión evaluada `027064fb`,
árbol limpio): **1 BLOCKING documental (F1, PC-5)** y **2 OPTIONAL (F2, F3)**.
F1 —la viabilidad de mutación se fundaba en un alcance al CLI inexistente— **cerrado** por nota de
corrección fechada del orquestador en `test-audit.md`: PC-5 es **«no realizado»** y la viabilidad
por fixtures queda **inconclusa**. Confirmado en el código citado: `PACKET_CLI` apunta a
`REPO_ROOT/skills/...` (`tests/test_005_013_t1_unit_projection.py:124,127`) y solo el proyecto
fixture vive en tempdir; los fixtures ejercitan el CLI real pero **no inyectan defecto**. F2 y F3
se recogen en este registro (§4). **No hubo segunda revisión independiente** de la corrección.

### 2.4 Resultado y límites del experimento (PC-5)

Estado: **no realizado**; **viabilidad inconclusa**. Mutantes aplicados por el reviewer en una
copia temporal (`git archive HEAD` en `/tmp`, repo sin tocar, copia eliminada; línea base
`3 passed`):

| Mutante | A | B | C | Lectura |
|---|---|---|---|---|
| M1: guard de colisión retirado | falla | falla | pasa | solape real en la conservación del pin y los bytes |
| M2: diagnóstico sin el nombre del paquete | falla | pasa | pasa | **contribución diferencial de A** (Mantener no es inercia) |
| M3: `if True` (no discrimina: rompe el primer `prepare`) | falla | falla | falla | **no acredita sensibilidad** |

Un cuarto intento sobre `semantic_status` **aplicó 0 ocurrencias**: su verde **no vale** como
evidencia. Inyectar un defecto exige una **copia mutada de la implementación bajo encargo
separado** (PC-5); **un futuro Sustituir/Consolidar no puede heredar «viabilidad ya evaluada»**.
Los fixtures no ofrecen control caja negro demostrado para este lote.

### 2.5 Suite completa

**Suite completa no realizada** (sin autorización expresa del dueño; política declarada una sola
vez en `skills/cdad-cycle/references/stage-3-tdd.md`). No se declara verde global ni gate de CI
verde.

## 3. `deferred-hardening` de la spec §8 — conservado con su disposición

| Ítem de §8 | Disposición registrada |
|---|---|
| Auditoría semántica global | **Excluida por el epic**; el compromiso es el lote B1. |
| Más candidatos de poda | **No necesario** para demostrar el procedimiento; ampliar el lote excede el MVP. Sin unidad asignada. |
| Campaña universal de mutación o umbral de puntuación | **No acredita conservación** y excede el experimento. Sin unidad asignada. |
| Rendimiento, paralelismo y optimización de fixtures | **`013-004-suite-performance`**, que **sólo se abre por decisión del dueño**. |
| Rediseño del selector o del verificador de genealogía | **No necesario**: se usan los mecanismos existentes más contraste independiente. Sin unidad asignada. |
| Resolución de deudas históricas ajenas al piloto | **No necesaria** para las promesas de esta unidad; permanecen visibles. |
| Suite completa y despliegue | **Fuera de este encargo**; el despliegue sigue siendo **reserva del dueño**. |

Ninguna exclusión aplaza una postcondición PC-1–PC-8.

## 4. Deuda declarada (fuera de §8)

- **PC-5 — viabilidad de mutación inconclusa (F1).** El estado es «no realizado»; los fixtures
  ejercitan el CLI real pero **no inyectan defecto**. Repetir «viable como control negativo caja
  negra» sería falso: la sensibilidad exige copia mutada bajo encargo separado.
- **F2 — solape A/B no evaluado contractualmente.** Con el guard retirado (M1) fallan A y B; ambos
  comparten guard (`cdad_packet.py:6745`, solo comprueba existencia del archivo), así que las
  aserciones de A cabrían en el recorrido de B. Esa consolidación perdería el estado «sin
  despacho», **cuya relevancia contractual nadie evaluó**. Benevolent redaction: «contribuciones
  distintas con solape en la conservación del pin y los bytes».
- **F3 — citas imprecisas.** `test_pd1…:71-77` es el docstring de módulo (no existe un `test_pd1`
  con esa relación); la cita `pc-map.json:446-475` del AUDIT difiere de `446-474` en la spec. No
  afecta al resultado; corregir al próximo toque del documento.
- **INV-3/PD-4 en la entrada de mapa de B tipificada sólo como PD-6** (continuación declarada de
  O4 de 013-002): la variante observable sí menciona el pin, pero el `id` no. Enriquecerlo es
  **cambio de asignación** y pertenece a POST-AUDIT con aprobación; el delta de un Mantener es
  vacío. No se resuelve eliminando tests (invariante 2).
- **Hallazgos de uso para 013-004:** (a) `docs/suite-maintenance.md` describe **solo el flujo de
  sustitución**; el delta vacío y el resultado Mantener proceden de la spec, no del procedimiento;
  (b) el procedimiento **no asigna quién registra `validate` en Mantener** — el test-writer no lo
  ejecutó (§8 del AUDIT) y el documento lo asigna a la entrada de Review.
- **Abstenciones del reviewer sin cerrar:** exclusividad de `receive` en B (sin mutante válido; se
  apoya en lectura del test); exclusividad de C (M3 no discrimina y el defecto «bloquear sólo
  `--out-dir` custom» no se ejecutó); relevancia contractual del estado «sin despacho»; PC-3 sobre
  `06fe83ce` no reproducida en la review (los tests no cambian desde entonces); tabla de
  decisiones vigentes vs `docs/adr/` no contrastada en su totalidad.
- **Suite completa no realizada.**
- **Sin segunda revisión independiente** de la corrección de F1 (documental; criterios de cierre
  escritos en F1 y verificados por el orquestador, declarado).
- **Despliegue pendiente (reserva del dueño).** Esta unidad **no agrega producto instalable**: no
  hay drift nuevo. Sigue vigente la deuda de 013-001/013-002 —la CLI de HOME emite paquetes con
  instrucciones obsoletas, de modo que **hasta desplegar los paquetes se preparan con
  `scripts/cdad_packet.py` del repo**— y el desfase de instalación de ambas unidades.

## 5. Límites de esta evidencia

Control **estructural** (`validate rc=0`) sobre una revisión concreta (`027064fb`), no acreditación
semántica; evidencia de ejecución **focal** (3 nodeids) más el contraste histórico (2 nodeids), no
suite completa; la sensibilidad sólo está **parcialmente** observada (M1/M2 en copia del reviewer,
M3 no discrimina, un cuarto intento sin efecto) y **no** acreditada como control del producto; el
**estado del experimento es «no realizado»** y su viabilidad **inconclusa**; el solape A/B y la
relevancia del estado «sin despacho» quedan **sin evaluar**; `validate` y las corridas focales no
fueron reproducidos por quien suscribe. Ninguna afirmación de ahorro, tiempo, rendimiento ni
acreditación global.
