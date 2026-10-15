# Cierre — 005-002-session-context-meter

Fecha: 2026-10-11. Feature del epic `epic-005-real-operation` (fila 7 del plan), orquestada por el
**orquestador OpenCode** bajo la **delegación HITL del epic** (`docs/epics/epic-005-real-operation/execution.md`).
Spec aprobada: `a70f6d500457e86769e85168f7cf5e3850d034b9cc79661856e99de53bd42e8f`. Plan aprobado:
`d373fc4fd58bb81278cb8f5af32645fb25433f590a9fa8bc3826fa52cdfaa157`.

## 1. Qué se entregó

Un **formato de medición neutral respecto del runtime** (opcional para la metodología) y su **primer
adaptador**: un lector de **solo lectura** de las sesiones de OpenCode que informa, por sesión y por
rol, tokens, lecturas, llamadas de herramienta y el momento del primer `resume`, distinguiendo
**observado / estimado / desconocido** y separando contexto por paso, procesamiento acumulado y costo.

| Archivo | Qué es |
|---|---|
| `skills/cdad-cycle/scripts/cdad_context_meter.py` | Adaptador canónico: lector SQLite `?mode=ro`, detección de esquema por columnas/tabla requeridas, fallo cerrado con diagnóstico que nombra el faltante y sin números, registro neutral por stdout, hitos separados, corte con borde fijado, medidas de orientación, tres magnitudes, anotación de aplicación referenciada, familias sin doble conteo, privacidad. |
| `scripts/cdad_context_meter.py` | Wrapper fino (`runpy.run_path`), convención del repo. |
| `skills/cdad-cycle/assets/context-meter.schema.json` | Contrato neutral `context-meter-v1` (draft 2020-12): cubos y regla de asignación, claves requeridas y obligatoriedades. |
| `skills/cdad-cycle/references/context-meter.md` | Procedimiento, semántica de cubos, anotación de aplicación, privacidad y **límite normativo de 16384 bytes** por documento de sesión. **No enganchado en ningún gate** (medición opcional). |
| `tests/test_005_002_t1_neutral_record.py` … `t4_acceptance.py` | 4 archivos de tests (RED/GREEN por tarea, fixtures sintéticos). |

## 2. Commits de la etapa 3

| Commit | Qué |
|---|---|
| `dc6b454` | RED T1 (registro neutral, contrato de invocación, fallo cerrado) |
| `eac25ac` | GREEN T1 (4 archivos de producto) |
| `c192c2d` | RED T2 (hitos, corte con borde fijado, orientación, tres magnitudes) |
| `b153cb3` | GREEN T2 (+ asset: `measure.value` admite objeto) |
| `9cc1c40` | RED T3 (anotación de aplicación, privacidad, salida compacta) |
| `fd58199` | GREEN T3 (+ reference: anotación y límite de 16384 bytes) |
| `2884f67` | RED T4 (aceptación: fixtures fieles + integración real omitida por defecto) |
| `49d27ad` | Corrección de tests: `total_output` del tramo (defecto detectado por el gate de integración) |
| `1dc4e9c` | GREEN T4 (docs-only: criterio de la sesión de cierre de 005-001 y su resolución) |

## 3. Gates de la etapa 3 (evidencia verificada por el orquestador)

| Gate | Evidencia |
|---|---|
| RED T1 | **7 failed** / 0 passed, **todas AssertionError** del contrato (corrida propia del orquestador; ninguna por import/sintaxis/setup). Commit `dc6b454` toca solo el test. |
| GREEN T1 | Focal **7 passed**; regresiones de los módulos tocados **10 passed** (corrida propia). `tests/**` intacto. |
| RED T2 | **5 failed** / 0 passed, todas AssertionError. |
| GREEN T2 | Focales T2+T1 **12 passed** (corrida propia); registro emitido validado **ad-hoc contra el asset** con jsonschema (2 fixtures). |
| RED T3 | **5 failed / 2 passed** (los 2 pre-satisfechos por el GREEN de T2, declarado por el rol y confirmado por el reviewer: F6/D9). |
| GREEN T3 | Tres focales **19 passed** (corrida propia). |
| RED T4 | **3 passed / 2 skipped** (los skip son la integración real y S-BOOT-04, con diagnóstico de habilitación). |
| GREEN T4 | Cuatro focales **22 passed / 2 skipped** (corrida propia). |
| **Gate de integración (real, no unitario)** | Reproducción de las **dos muestras sobre la base real en solo lectura** (store + ids por variables de entorno): **1 passed**; **S-BOOT-04**: **1 passed**. El store queda intacto (aserciones de tamaño/mtime del propio test). |
| Mapeo test↔postcondición | Auditado por una sesión **distinta** de la que escribió los tests (el reviewer): sin PD sin test salvo PD-14 (documental, por contrato), sin tests huérfanos, sin mocks sobre plumbing ni aserciones sobre nombres internos. |

## 4. Review formal (etapa 4)

`review.md` (reviewer `mofgw/glm-5.3-flash`, **familia distinta** a la del implementer
`mofgw/deepseek-v4.1-flash`): **0 blocking · 10 optional · 0 abstenciones**. El reviewer trajo el
diff completo (13 commits, 9 archivos, +5774/-6), verificó el pin del contrato, corrió los focales
(22 passed / 2 skipped) y respondió los cinco puntos que el orquestador pidió esclarecer.
**Disposición:** los 10 hallazgos no rompen el camino feliz → `debt.md`, con condición de cierre
verificable. Prioridad 1 (producto): el `time_relative: 0.0` fabricado cuando el tiempo del hito no
es observable (viola el invariante desconocido ≠ cero en un caso de borde válido).

## 5. Suite completa de cierre (etapa 5)

Worktree **fijado a `b1a8add`** (último commit que toca producto o tests; los commits posteriores son
**docs-only**, por lo que el árbol de producto y tests es idéntico y la corrida es equivalente):

- `make staging` dentro del worktree: OK (12 + 12 agentes).
- **Suite completa: `787 passed, 4 skipped` — exit 0, 939.85s (0:15:39).**
- `make validate`: **142 PASS / 1 FAIL**.
  - El único FAIL es **F011** (`scripts/validate-subagents.sh`), que compara el repo con las copias
    **instaladas** en HOME: reporta *drift* de los agentes (preexistente, de versiones anteriores) y
    de los **dos archivos nuevos de esta feature** (`references/context-meter.md`,
    `assets/context-meter.schema.json`), que la instalación todavía no tiene. **Desviación
    documentada, no silenciosa:** resolverlo exige **desplegar** la versión, acción **reservada al
    dueño** y **prohibida en este tramo**; el plan del epic ya prevé el despliegue *entre ciclos*.
    En el árbol principal, además, A3 falla por el archivo local no rastreado
    `tests/.sensitive-patterns.local` (que no se lee ni se commitea); en el worktree limpio A3 pasa
    (por eso 142 PASS allí frente a 141 PASS en el árbol principal).

## 6. Limitaciones, desviaciones y deuda

- **Defecto detectado y corregido durante el ciclo:** el gate de integración encontró que los tests
  de T2/T4 pineaban `total_output` del tramo en 51.243 (que es el **max_output**, lo único que la
  spec pinea). El orquestador verificó con sonda propia read-only que el tramo real tiene total
  317.170 y máximo 51.243; la corrección volvió al test-writer (`49d27ad`) y el fixture pasó a ser
  fiel (100 de 101 llamadas con salida). No se relajó ningún gate ni se tocó la spec aprobada.
- **Incidente de orquestador (transporte):** el descriptor del review se armó con el
  `artifact_kind` equivocado (`reviewer-report` en lugar de `review`); `receive` lo aceptó y
  `materialize` lo rechazó. Se conservó copia del recibo/bundle inválidos en
  `.cdad/local/incident-review-kind/`, se re-recibió el **mismo** texto final del rol (digest
  verificado idéntico) con el kind correcto y se materializó. Sin cambio en los bytes del rol.
- **Desviación de operación de un rol:** en el GREEN de T2 el implementer dejó la suite completa
  corriendo en segundo plano y terminó su turno; el orquestador mató el proceso huérfano y la suite
  de cierre la corrió él mismo en el worktree fijado (evidencia vinculante).
- **V6 / PD-14 (sesión de cierre de 005-001):** con el criterio declarado (13 sesiones hijas)
  ninguna candidata de la ventana lo satisface (7, 22 y 30 hijos) → **`unknown` con causa** e ítem
  abierto; el criterio reproducible queda documentado en el reference.
- **V3 / V11 del discovery** (ruta exacta del CLI de continuidad; campo de ruta de `read` por
  versión) y **V4** (`resume_attempts`/`time_idle`/`idle_outcome` → `unknown` con causa) siguen
  abiertos o declarados.
- **Deuda priorizada:** `debt.md` (10 hallazgos OPTIONAL de la review con condición de cierre
  verificable; D1 = el cero fabricado en `time_relative` es el primero).
- **Sin CI configurado:** el gate de cierre es la suite local en el worktree fijado, más
  `make validate` con la desviación F011 declarada arriba.
- **Sin despliegue y sin push:** la activación de la versión en HOME queda reservada al dueño (el
  plan del epic la sitúa entre ciclos).

## 7. Criterios de aceptación del epic que esta feature alimenta

- El **informe de medición** (criterio 3 del epic) tiene ahora su instrumento: la medición se
  reproduce sobre las dos muestras pinneadas y sobre S-BOOT-04 con la base real en solo lectura.
- **005-003** (reducción de orientación) consume este instrumento; su entrada de discovery ya está
  en el repo. La meta numérica se fija allí con estos datos.
- **005-006** (arranque guiado) puede leer los registros de sus sesiones con el mismo medidor.

## 8. Acción del dueño pendiente

1. **Desplegar** la versión de cierre (incluye `context-meter.*`) cuando lo decida: resuelve F011
   (drift de las copias instaladas) y habilita el uso del medidor desde la instalación.
2. Revisar la **deuda priorizada** (`debt.md`), en particular D1. **(Actualizado 2026-10-12: D1 quedó
   cerrada por la reapertura; ver §9.)**

## 9. Reapertura acotada por el criterio de review vigente (2026-10-12)

La feature se **reabrió** el 2026-10-12, un día después de su cierre, cuando el dueño aprobó un
**criterio de review nuevo** (`docs/epics/epic-005-real-operation/execution.md`, sección «Criterio de
review vigente — 2026-10-12», aprobado con «De acuerdo, adelante» a partir de la verificación de
Codex): se **bloquea y corrige ya** lo que compromete el **resultado**, la **evidencia** o el **uso
previsto**; va a deuda priorizada lo que es una mejora o variante **sin impacto material**. El
criterio reemplaza al anterior («lo que no rompe el camino feliz va a deuda») que había mandado los
10 hallazgos de la review original a `debt.md`.

**Mecanismo** (precedente: la reapertura de 005-010 por B1, su `closure.md` §6): (1) la feature vuelve
a `in-progress` y queda activa; (2) RED y GREEN **focales**, sin cambiar el contrato aprobado
(PD-3, PD-4, PD-6, PD-12, PD-15); (3) suite completa de cierre en un **worktree fijado**; (4) cierre
con nota acá y en `debt.md`. Reglas del tramo: roles en primer plano y commitean; fixtures
**sintéticos** (sin copiar de la base real); reviewer de **otra familia** que el implementer; la
integración real de T4 (solo lectura) debe seguir verde; la HITL del epic delegada en el orquestador
OpenCode. Prohibido: desplegar o reinstalar en HOME, reiniciar servidores de OpenCode, push, leer
`tests/.sensitive-patterns.local`, tocar otros proyectos y arrancar 005-003.

### 9.1 Alcance y qué se corrigió

Una sola **clase** de defecto, corregida como familia: *desconocido informado como cero / magnitud
parcial presentada como completa / ausencia no declarada*.

| Punto | Qué se corrigió | Deuda cerrada |
|---|---|---|
| A | El hito observado ya no fabrica `time_relative: 0.0` (es `null` + causa) y la medida hermana deja de declararse `observed` con value null; el proxy por paso ya no suma `(x or 0)` (un paso incompleto es `null` + causa **agregada**); `max_output`/`total_output` sin evidencia de salida son `unknown` (con control positivo del 0 observado); barrido del resto de las métricas | D1 (+ la subclase que el RED detectó: `accumulated`, `cache.read`, `cost` con cobertura incompleta) |
| B | El límite publicado de 16.384 bytes **por documento de sesión** se cumple con cualquier tamaño de sesión: resumen de tamaño fijo + indicador de truncado con causa; el detalle por paso exige la bandera explícita `--steps`, documentada en el reference | D2 |
| C | La salida declara las herramientas de despacho reconocidas (`reader.dispatch_tools`: `subagent`, `task`) y la causa de `absent` distingue «no ocurrió» de «no reconocido por este lector» | D4 |
| D | `--session` parcialmente casado: la referencia pedida y no encontrada se declara `unknown` con causa (hasheada), sin medir un subconjunto en silencio | D5 |
| E | El oráculo de aceptación se relajó según su condición de cierre (`>= 101` llamadas pinneadas, con el conteo exacto como sonda declarada y las dos llaves de contrato intactas) | D3 |
| — | **R1** de la review de la reapertura (bloqueante): el **agregado por rol** deja de presentar subtotales parciales como completos | (hallazgo de la review, no deuda previa) |
| — | D6 (versión heterogénea del runtime) | **sigue en deuda** por encargo del dueño |

### 9.2 Commits del tramo

| Commit | Qué |
|---|---|
| `5a4d567` | Reapertura: la feature vuelve a `in-progress` y activa (state) |
| `0083d82` | RED unidad 1 (desconocido no es cero / ausencia declarada: D1, D4, D5) |
| `6bf350d` | RED addendum (subclase: agregados del tramo con cobertura parcial) |
| `3e481d4` | GREEN unidad 1 (adaptador + asset + reference) |
| `7635a90` | Testfix: refuerzo del oráculo de D5 |
| `f22d292` | RED unidad 2 (salida acotada a escala + oráculo de aceptación) y alineación de los tests que leían el detalle por defecto |
| `b89252f` | Testfix de alineación del oráculo de la unidad 1 a `--steps` (desbloqueó el GREEN de la unidad 2) |
| `41b45f9` | GREEN unidad 2 (`--steps`, resumen de tamaño fijo, indicador de truncado) |
| `bb3141e` | RED del bloqueante R1 (agregado por rol) + alineación de lectura de t3 |
| `d435e9b` | GREEN de R1 (cobertura declarada en `roles[].sums` y `distributions`) |

### 9.3 Gates del tramo (verificados por el orquestador con corridas propias)

| Gate | Evidencia |
|---|---|
| RED unidad 1 | **6 failed**, todas `AssertionError` de contrato (0.0 is not None; 110 is not None; observed != unknown; …) |
| RED addendum | **8 failed** (los 6 previos con los mismos mensajes + los 2 de la subclase de agregados) |
| GREEN unidad 1 | Focal T5 **8 passed**; t1..t4 **22 passed / 2 skipped**; **integración real 5 passed** (base de sesiones en solo lectura) |
| RED unidad 2 | **4 failed** (3 por `AssertionError` de comportamiento y 1 por la bandera declarada inexistente) + t1..t4 **3 failed** (las 3 por la misma bandera declarada) — gate **mixto declarado** de antemano |
| GREEN unidad 2 | T5b **4 passed**; T5 **8 passed**; t1..t4 **22 passed / 2 skipped**; **integración real 5 passed**; documento por defecto **8.001 B** (1.000 pasos) y **8.006 B** (4.000 pasos) |
| RED R1 | **4 failed**, todas `AssertionError` (números y lista planos donde va la entrada declarada) |
| GREEN R1 | Focal R1 **4 passed**; resto de 005-002 **34 passed / 2 skipped**; **integración real 5 passed**; cierre de R1 **verificado por sonda propia** del orquestador sobre un store sintético (cobertura parcial → `unknown` + `value: null` + causa con rol/componente/`k de n`; `sums.sessions` sigue entero; una causa agregada por (rol, componente)) |
| Bloqueo y reencauce | El primer despacho del GREEN de la unidad 2 se **bloqueó legítimamente**: el paquete de alineación había omitido `tests/test_005_002_t5_unknown_declared.py` y dos oráculos aprobados exigían por defecto formas incompatibles de la misma medida. El rol **paró** sin tocar tests ni producto y sin commitear; el orquestador reencauzó (testfix `b89252f`) y re-despachó el **mismo** paquete. Nada quedó modificado por el intento fallido. |

### 9.3-bis Suite completa de cierre del tramo (etapa 5)

Worktree **fijado a `d435e9b`** (el último commit que toca producto o tests; los commits posteriores
del tramo son docs-only, por lo que el árbol de producto y tests es idéntico y la corrida es
equivalente):

- `make staging` dentro del worktree: **OK** (12 + 12 agentes).
- **Suite completa: `803 passed, 4 skipped` — exit 0, 995.26s (0:16:35).**
- `make validate`: **142 PASS / 1 FAIL**.
  - El único FAIL es **F011** (`scripts/validate-subagents.sh`), que compara el repo con las copias
    **instaladas** en HOME: reporta *drift* (preexistente, de versiones anteriores, y de los archivos
    nuevos/modificados de esta feature). **Desviación documentada, no silenciosa:** resolverlo exige
    **desplegar** la versión, acción **reservada al dueño** y **prohibida en este tramo**. Es el mismo
    FAIL declarado en el cierre original (§5).
- Comparación con el cierre original: 787 passed / 4 skipped → **803 passed / 4 skipped** (los 16
  tests nuevos del tramo: 8 + 4 + 4 de las tres unidades focales).

### 9.4 Review de la reapertura y su disposición

`review-reopen-2026-10-12.md` (reviewer `mofgw/glm-5.3-flash`, **familia distinta** a la del
implementer `mofgw/deepseek-v4.1-flash`, con el criterio vigente): **1 blocking · 5 optional · 2
abstenciones declaradas**. Verificó el pin del contrato, corrió los focales (12 passed: 8 + 4) y
t1..t4 (22 passed / 2 skipped), reprodujo los RED en worktrees temporales, auditó el debilitamiento
de tests commit por commit (ninguna aserción de contrato cedió) y sondeó con fixtures propios.

- **R1 (BLOCKING) — `roles[].sums` agregaba subtotales parciales como número completo**: se corrigió
  ya (RED `bb3141e` + GREEN `d435e9b`). Segunda pasada acotada
  (`review-reopen-2026-10-12-second-pass.md`): **R1 CERRADO**, sin hallazgos nuevos, con la
  condición de cierre reproducida por el reviewer con sonda propia.
- **R2, R3, R4, R5 (OPTIONAL)**: a `debt.md` con condición de cierre verificable. R2 quedó
  **parcialmente avanzado** (el asset nuevo de `roles[]` es binding; el recorte original de
  `measure.value` sigue abierto).
- **R6 / D6**: sigue en deuda por encargo del dueño.
- **Abstenciones declaradas**: el reviewer **no** corrió la integración real de T4 (no tiene las
  variables de entorno) y no abrió la base real de sesiones. Esa evidencia la aporta el orquestador
  en cada gate (**5 passed**, store intacto).

### 9.5 Deuda cerrada y deuda que queda

- **Cerrada por la reapertura:** D1, D2, D3, D4 y D5 de `debt.md` (con su evidencia y su regresión
  focal), más la subclase de agregados del tramo y el hallazgo bloqueante R1.
- **Sigue abierta:** D6 (versión heterogénea del runtime, por encargo del dueño), D7–D10 (proceso y
  documentación de la review original) y **R2–R5** de la review de la reapertura, cada una con su
  condición de cierre verificable en `debt.md`.
- **Sesión de cierre de 005-001 (V6/PD-14)** y **V3/V11/V4 del discovery**: siguen como estaban
  (`unknown` con causa declarada).

### 9.6 Límites declarados del tramo

- **El límite de 16.384 bytes en corridas multi-sesión queda fuera de alcance** (es el hallazgo R4 de
  la review): el texto publicado acota el **documento de una sesión** y el encargo habló de
  «cualquier tamaño de sesión». El reviewer juzgó defendible el encuadre y pidió declarar la regla
  antes de que 005-003 consuma corridas multi-sesión: queda en `debt.md`.
- **La review de la reapertura no re-ejecutó la suite completa** (la declaró el orquestador, que la
  corrió en un worktree fijado a `d435e9b`); el reviewer sí corrió los focales y reprodujo los RED.
- **Sin despliegue, sin push y sin tocar HOME**: la versión de cierre queda para el dueño.
