# Línea base medida con el medidor de 005-002 — 005-003

Fecha: 2026-10-12. Medición **en solo lectura** de trabajo real ya hecho, por el orquestador del
epic-005, antes del discovery de 005-003. No repite ningún desarrollo: mide sesiones que ya
ocurrieron (la reapertura de 005-002 del 2026-10-12 y su ciclo original del 2026-10-11) y el caso
S-BOOT-04 ya documentado en [discovery-inputs.md](../discovery-inputs.md).

Este documento es **evidencia**, no contrato. No aprueba alcance, no fija la meta numérica y no
declara el medidor como gate de 005-003.

## 1. Procedencia

| Qué | Valor |
|---|---|
| Instrumento | `cdad_context_meter.py` del repo, sha256 `d2655e0413abead264786be4ff182c530b0934def57d472407df9b9b6ab20d74` |
| Versión del instrumento | sin cambios desde `d435e9b` (el último commit que lo toca): `git log --oneline d435e9b..HEAD -- skills/cdad-cycle/scripts/cdad_context_meter.py` → vacío. Es el artefacto que cerró 005-002 tras la reapertura |
| Store | base de sesiones de OpenCode, abierta por el medidor en `mode=ro`; `run.store_ref = sha256:0674cab53843244d5e05636b09039e60` |
| Versión de runtime observada | `2.0.26` en todas las sesiones medidas (homogénea en estas corridas) |
| Esquema | `recognized` (sin fallo cerrado) en las tres corridas |
| Salidas crudas | `.cdad/local/runs/005-003-baseline/` (ignorado por Git; incluye el mapeo `ref hasheada ↔ identificador crudo`) |
| Comandos | ver §7 |

**Hallazgo de procedencia que condiciona el uso del medidor como gate:** la versión **instalada**
(`cdad-version-check.py` → `COHERENT` en `c9f4810`) **no contiene** `cdad_context_meter.py`; el
medidor entra al repo en `eac25ac` (T1 de 005-002), posterior a `c9f4810`. Medir hoy exige invocar
el artefacto **del repo**; el medidor no está en ninguna instalación (ni en la de OpenCode ni en la
de Claude Code, comprobado en ambas rutas de skills). Desplegar está reservado al dueño y fuera de
este tramo.

## 2. Cuts y definiciones (lo que hace comparables o no los números)

- **Tramo (stretch).** «Primer tramo contiguo: corte en el primer hueco de inactividad mayor al
  umbral» (`--idle-threshold` por defecto 60 min). En las tres sesiones de orquestación el tramo
  coincide con la sesión completa porque no hay huecos de más de 60 min.
- **`time_to_first_dispatch`.** Del inicio del tramo (primer mensaje de usuario) al *primer* hito
  de despacho reconocido (`reader.dispatch_tools = ["subagent","task"]`). Es una medida del **primer**
  despacho, no de los siguientes.
- **`time_to_first_resume`.** Del inicio del tramo al primer `resume` observado (llamada de shell al
  subcomando `resume` de la CLI de continuidad; las llamadas de ayuda se excluyen).
- **`previous_calls` / `previous_reads` / `previous_calls_by_tool`.** Llamadas de herramienta
  **antes del primer `resume`**. Sólo existen si hay primer `resume`; sin él son `unknown` con causa.
- **`input_per_step`.** `estimated`: proxy `input + cache.read + cache.write` por paso. **No** es la
  ventana de contexto, **no** es consumo y **no** es el costo. El resumen por defecto es de tamaño
  fijo: `count/last/previous/min/max/unobserved`. Con `--steps` se emite la lista ordenada completa.
- **`accumulated` / `cache.read` / `cost`.** Sumas sobre los pasos del tramo; **completas sólo con
  cobertura total**, si no `unknown` con causa — nunca un subtotal parcial (contrato de 005-002
  tras `d435e9b`).
- **Tamaño.** El límite publicado de 16.384 B es **por documento de sesión**. Las corridas
  multi-sesión lo superan en el total (ver §6.3).

## 3. Caso A — reapertura de 005-002 (2026-10-12)

Sesión de orquestación abierta 13:15:09 y cerrada 16:09:49 (ART, 174,65 min) con **12 sesiones de
rol hijas**. Es el caso que el delta de discovery toma como línea base real.

### 3.1

| rol | sesión (ref hasheada, prefijo) | tramo (min) | 1.er resume (min) | 1.er despacho (min) | llamadas del tramo | lecturas | salida total (car.) | salida máx. (car.) | input acumulado | proxy del último paso | pasos |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cdad-orchestrator` | `97af3aeaaca1…` | 174.6 | 1.92 | 9.42 | 241 | 15 | 563,582 | 51,309 | 1,337,730 | 456,591 | 223 |
| `cdad-reviewer` | `419f09112942…` | 5.0 | - | - | 36 | 3 | 129,503 | 42,549 | 90,081 | 73,326 | 31 |
| `cdad-implementer` | `1f2c4fcbf204…` | 20.4 | - | - | 47 | 12 | 279,486 | 56,634 | 124,041 | 145,930 | 46 |
| `cdad-test-writer` | `972446192999…` | 7.1 | - | - | 44 | 12 | 221,957 | 52,975 | 119,488 | 141,640 | 40 |
| `cdad-reviewer` | `c32364098923…` | 9.5 | - | - | 37 | 9 | 305,723 | 56,328 | 201,660 | 135,338 | 37 |
| `cdad-implementer` | `4d2ae3bd6ccc…` | 8.5 | - | - | 84 | 22 | 348,571 | 52,975 | 143,608 | 166,952 | 66 |
| `cdad-test-writer` | `ce6c82f99c2c…` | 2.5 | - | - | 29 | 12 | 223,997 | 56,346 | 85,430 | 108,894 | 21 |
| `cdad-implementer` | `020075378360…` | 9.7 | - | - | 72 | 17 | 316,589 | 52,975 | 153,772 | 174,551 | 63 |
| `cdad-test-writer` | `add03026a83f…` | 6.4 | - | - | 32 | 10 | 299,840 | 56,310 | 135,261 | 159,568 | 23 |
| `cdad-test-writer` | `f32b4463f7bd…` | 4.4 | - | - | 36 | 6 | 165,204 | 56,381 | 83,042 | 105,544 | 30 |
| `cdad-implementer` | `f8cac5394dc5…` | 30.0 | - | - | 88 | 24 | 386,850 | 56,381 | 223,000 | 217,987 | 76 |
| `cdad-test-writer` | `65f29ed2af20…` | 5.6 | - | - | 23 | 4 | 152,778 | 52,939 | 92,964 | 116,316 | 21 |
| `cdad-test-writer` | `7ee0477409ec…` | 7.3 | - | - | 35 | 4 | 187,018 | 52,939 | 132,885 | 133,392 | 30 |

| rol | sesiones | input acumulado | costo (u.m.) | llamadas | salida total (car.) |
|---|---:|---:|---:|---:|---:|
| `cdad-implementer` | 4 | 644,421 | 0.64023534 | 291 | 1,331,496 |
| `cdad-orchestrator` | 1 | 1,337,730 | 1.049545656 | 241 | 563,582 |
| `cdad-reviewer` | 2 | 291,741 | 0.22364883000000002 | 73 | 435,226 |
| `cdad-test-writer` | 6 | 649,070 | 0.557934888 | 199 | 1,250,794 |

Hitos de la sesión de orquestación: `first_resume` en la llamada **29** (`seq 198`, 1,92 min);
`first_dispatch` en la llamada **76** (`seq 596`, 9,42 min), con `previous_calls = 28`
(`shell` 25, `read` 3) y `previous_reads = 3`.

### 3.2 Tiempo del orquestador entre despachos (derivación, no medida del medidor)

**Advertencia de procedencia:** el medidor **no** emite el tiempo entre despachos. Lo que sigue es
una **derivación del orquestador** sobre `session_v2` (solo lectura) usando `time_created` /
`time_updated` de las 12 sesiones hijas y de la sesión madre; no es una medida del instrumento y
tiene los límites de §6.2.

| Concepto | Valor |
|---|---:|
| Preparación hasta el primer despacho (madre creada → primer hija) | 9,84 min |
| Suman de los 11 huecos entre sesiones de rol | 28,62 min (mín. 1,43 · máx. 3,93) |
| **Preparación total entre despachos** (primer tramo + huecos) | **38,46 min** |
| Cola final (última rol → cierre de la sesión madre) | 19,79 min |
| Suma de duraciones de las 12 sesiones de rol | 116,40 min |
| Duración de la sesión madre | 174,65 min |

El delta de discovery declara «unos 40 min del orquestador entre despachos» y «el implementer
corriendo dos veces la suite completa (unos 15 min cada una) dentro de GREEN»: la derivación
**reproduce el ~40 min** (38,46) con esta definición, y la sesión de `cdad-implementer` de
**30,01 min** (`f8cac5394dc5…`) es compatible con dos corridas de suite en un mismo GREEN. La
duración de la sesión (174,65 min = 2 h 54 min 39 s) reproduce el «unas 2 h 55 min» declarado.

## 4. Caso B — ciclo original de 005-002 (2026-10-11)

Sesión de orquestación 18:44:48→22:21:19 (ART, 216,51 min) con **13 sesiones de rol hijas**
(incluye architect, scribe y el cierre).

| rol | sesión (ref hasheada, prefijo) | tramo (min) | 1.er resume (min) | 1.er despacho (min) | llamadas del tramo | lecturas | salida total (car.) | salida máx. (car.) | input acumulado | proxy del último paso | pasos |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cdad-orchestrator` | `8ad25f4bf60c…` | 216.5 | 0.42 | 6.17 | 316 | 41 | 729,880 | 50,513 | 382,688 | 591,897 | 300 |
| `cdad-scribe` | `37bf39278855…` | 5.6 | - | - | 24 | 16 | 315,087 | 53,587 | 129,445 | 147,494 | 11 |
| `cdad-reviewer` | `703dc4de4f18…` | 5.8 | - | - | 18 | 12 | 385,807 | 55,962 | 160,536 | 151,530 | 16 |
| `cdad-implementer` | `cdc9fda8d8e4…` | 3.2 | - | - | 16 | 7 | 155,207 | 55,926 | 106,960 | 81,193 | 13 |
| `cdad-test-writer` | `afa3ea8640e1…` | 8.0 | - | - | 52 | 7 | 223,004 | 55,915 | 153,183 | 124,006 | 51 |
| `cdad-test-writer` | `26b5b1269559…` | 11.2 | - | - | 28 | 6 | 233,082 | 55,879 | 144,406 | 132,774 | 26 |
| `cdad-implementer` | `d6c04694ae70…` | 12.2 | - | - | 54 | 15 | 362,519 | 55,915 | 439,224 | 181,457 | 45 |
| `cdad-test-writer` | `633c33a7b521…` | 12.5 | - | - | 31 | 6 | 193,162 | 55,915 | 161,225 | 142,902 | 31 |
| `cdad-implementer` | `6b59c1c1ba5b…` | 24.0 | - | - | 46 | 10 | 286,892 | 55,879 | 93,831 | 160,121 | 33 |
| `cdad-test-writer` | `8144f63bf81e…` | 19.3 | - | - | 52 | 6 | 249,514 | 55,894 | 205,946 | 181,229 | 51 |
| `cdad-implementer` | `615687e7de2a…` | 26.8 | - | - | 50 | 14 | 276,888 | 57,466 | 150,532 | 156,057 | 39 |
| `cdad-test-writer` | `f73361c85847…` | 4.7 | - | - | 24 | 7 | 117,449 | 52,975 | 281,151 | 96,946 | 20 |
| `cdad-architect` | `fb0d440305ee…` | 9.5 | - | - | 12 | 6 | 139,245 | 38,275 | 62,832 | 109,098 | 8 |
| `cdad-architect` | `da27cbfdef44…` | 8.9 | - | - | 38 | 17 | 262,890 | 57,430 | - | 141,267 | 29 |

| rol | sesiones | input acumulado | costo (u.m.) | llamadas | salida total (car.) |
|---|---:|---:|---:|---:|---:|
| `cdad-architect` | 2 | *desconocido* (cobertura 1/2) | *desconocido* (cobertura 1/2) | 50 | 402,135 |
| `cdad-implementer` | 4 | 790,547 | 0.5171068679999999 | 166 | 1,081,506 |
| `cdad-orchestrator` | 1 | 382,688 | 1.100603616 | 316 | 729,880 |
| `cdad-reviewer` | 1 | 160,536 | 0.07973464 | 18 | 385,807 |
| `cdad-scribe` | 1 | 129,445 | 0.08366252399999999 | 24 | 315,087 |
| `cdad-test-writer` | 5 | 945,911 | 0.84442059 | 187 | 1,016,211 |

**Evidencia lateral útil:** el rol `cdad-architect` aparece con `accumulated`/`cost` **desconocidos
con causa y cobertura 1/2** en lugar de un subtotal parcial aritméticamente plausible. Es la
corrección R1 (`d435e9b`) observada en datos reales, no en un fixture.

## 5. Caso C — S-BOOT-04 (arranque desde reposo, 2026-10-10)

Caso ya documentado y anonimizado en [discovery-inputs.md](../discovery-inputs.md) §«Caso nuevo:
S-BOOT-04»; su mapeo local está en `.cdad/local/orientation-analysis-005-003-2026-10-10.json`.

| medida | valor del medidor | valor declarado en el insumo | lectura |
|---|---:|---:|---|
| Duración del tramo | 265,52 min | no declarada (el insumo corta en el despacho) | el tramo del medidor cubre toda la sesión; **no** es comparable con el corte del insumo |
| `time_to_first_dispatch` | **8,29 min** | 526.661 ms ≈ 8,78 min | mismo orden; **cuts distintos** (§7), no se promedian |
| Posición del 1.er despacho | `call_index 73` | 72 herramientas antes del despacho | coherente: 72 previas ⇒ la 73 es el despacho |
| `first_resume` | **`absent`** con causa («ninguna llamada de shell del primer tramo invoca el subcomando `resume`…») | el insumo describe uso del comprobador de versión, no de `resume` | la ausencia es «no ocurrió», distinta de «no reconocido» (D4) |
| `tool_calls` del tramo | 232 | 72 antes del despacho | el medidor cuenta el tramo completo, no el corte pre-despacho |
| `session_reads` | 15 | 11 lecturas antes del despacho | ídem |
| `total_output` (car.) | 816,330 | 418,841 antes del despacho | ídem |
| `max_output` (car.) | 55,198 | no declarado | — |
| `input_per_step` (resumen) | `count 210`, `last 477,058`, `min 37,739` | máximo proxy previo al despacho **200,076** | **no comparable**: el insumo corta en el despacho y el medidor mide todo el tramo |
| `accumulated` / `cost` | 1,807,776 / 1.124611632 | — | — |
| Carga de skill inyectada con el mensaje inicial | **no observable** por el medidor | 37.667 car. | magnitud declarada por el insumo, ausente del registro |

Con `--steps` (lista ordenada completa de 210 proxies) el documento sube a 16.878 B y el límite
publicado deja de aplicar, según el contrato. **Slicing no declarado:** cortar esa lista por
`call_index 73` da 73 elementos con máximo 246.363, pero **pasos ≠ llamadas** (210 vs. 232 en esta
sesión; 223 vs. 241 en §3), así que alinear la lista de pasos con un `call_index` de llamada es una
suposición **no declarada por el contrato**. La magnitud de orientación *previa al primer despacho*
—la que el insumo reporta como 200.076 tokens con un cut explícito— **no es reproducible hoy desde
el medidor**.

## 6. Límites declarados de esta línea base (evidencia, no queja)

### 6.1 Lo que el medidor sí da, por rol y por sesión

Tramo, hitos con posición, llamadas y lecturas, salida total y máxima, `input_per_step`
(`count/last/previous/min/max/unobserved`), acumulado, caché y costo con cubos y cobertura. Todo lo
de §3.1, §4 y §5 sale de ahí.

### 6.2 Lo que el medidor no da hoy, y que el delta de aceptación pide

1. **Tiempo del orquestador entre despachos.** `time_to_first_dispatch` es sólo el **primero**. El
   resto de §3.2 es derivación externa, con límites reales: un hueco puede ser negativo si dos
   sesiones de rol se solapan (ocurre en §4: −12,54 min entre dos `cdad-test-writer`), el tiempo
   del orquestador **dentro** de la ventana de un rol es invisible, y `time_updated` de una sesión
   hija no marca necesariamente el fin del trabajo del orquestador.
2. **Reorientación de cada rol.** Para una sesión de rol, `previous_calls`, `previous_reads`,
   `previous_calls_by_tool`, `time_to_first_resume` y `time_to_first_dispatch` salen **`unknown`
   con causa**: `previous_*` está definido respecto del primer `resume` y una sesión de rol no
   invoca `resume`. No existe un hito de «primera acción del encargo». Medir «llamadas y salidas
   antes de la primera acción» exige **declarar un proxy** sobre las medidas existentes o **extender
   el medidor** con un hito nuevo (extensión del contrato de 005-002).
3. **Ejecuciones redundantes** (suite completa fuera del cierre, gate re-ejecutado). El medidor no
   lee texto de comandos ni argumentos de herramientas (privacidad, PD-10/PD-12 de 005-002): no
   puede contar corridas de suite. Sólo son observables por **declaración** en el ledger/evidencia
   del paquete.

### 6.3 Tamaño del documento en corridas multi-sesión

| Corrida | Sesiones | Bytes totales | Media por sesión | Límite publicado 16.384 B |
|---|---:|---:|---:|---|
| Reapertura 005-002 | 13 | **113.333** | 8.717 | se cumple **por sesión**; el total lo supera |
| Ciclo original 005-002 | 14 | **135.297** | 9.664 | ídem |
| S-BOOT-04 (una sesión) | 1 | 13.111 | 13.111 | se cumple |
| S-BOOT-04 `--steps` | 1 | 16.878 | 16.878 | no aplica (detalle pedido explícitamente) |

Esto **reproduce el hallazgo R4** y **la observación del delta** («entregar 20 documentos de unos
8 KB es demasiado para decidir qué ocurrió»: la media medida es ~8,7 KB por sesión). R4 tiene por
condición de cierre declarar la regla del documento multiplexado en el reference **antes de que
005-003 consuma corridas multi-sesión**, y el delta pide que el consumidor reciba **primero un
resumen del conjunto**.

### 6.4 Prerrequisitos de 005-002 pendientes para usar el medidor como gate

- **D11** (integración real inestable contra la base viva): el delta lo declara **prerrequisito**
  para usar la integración real como gate de 005-003 y **no** bloqueante del discovery.
- **R4** (§6.3): declarar la regla del documento multiplexado antes de consumir corridas
  multi-sesión.
- **D6/R6** (versión de runtime heterogénea): en las corridas de §3, §4 y §5 la versión observada es
  **homogénea (2.0.26)**; la condición de revisión de D6 es que 005-003 compare contextos por
  versión de runtime antes de consumir `run.runtime_version`.

## 7. Comandos exactos de la medición

`<store>` = base de sesiones de OpenCode de esta instalación (ruta en el mapeo local). Todas las
corridas se hicieron **desde el repo**, con el artefacto del repo, y son de **solo lectura**.

```sh
# Caso A: orquestación de la reapertura de 005-002 + sus 12 sesiones de rol
python3 skills/cdad-cycle/scripts/cdad_context_meter.py --store "$STORE" \
  --session <orq-reapertura> --session <rol-01> … --session <rol-12>

# Caso B: orquestación del ciclo original de 005-002 + sus 13 sesiones de rol
python3 skills/cdad-cycle/scripts/cdad_context_meter.py --store "$STORE" \
  --session <orq-ciclo> --session <rol-01> … --session <rol-13>

# Caso C: S-BOOT-04 (una sesión), con y sin detalle por paso
python3 skills/cdad-cycle/scripts/cdad_context_meter.py --store "$STORE" --session <sboot04>
python3 skills/cdad-cycle/scripts/cdad_context_meter.py --store "$STORE" --session <sboot04> --steps
```

Los identificadores crudos están en el mapeo local
`.cdad/local/runs/005-003-baseline/README.md` (fuera de Git). **Criterio de re-derivación sin
identificadores** (aplicable a la base, solo lectura): la sesión de orquestación de la reapertura es
la sesión de nivel superior con `agent = cdad-orchestrator` cuyo intervalo cae en
2026-10-12 13:15→16:09 (ART) y que tiene **exactamente 12** sesiones hijas; sus roles son esas 12
hijas en orden de creación. Para el ciclo original: 2026-10-11 18:44→22:21 (ART) y **13** hijas.

## 8. Qué NO afirma este documento

- No afirma ahorro alguno ya demostrado: es una línea base.
- No fija la meta numérica de 005-003 (la fija la spec, según el plan del epic, «a partir de los
  datos»).
- No promedia los cuts distintos (medidor vs. insumo) ni presenta el proxy como ventana de
  contexto, consumo o costo.
- No declara el medidor como gate de 005-003: D11 y R4 siguen abiertos (§6.4).
- No publica identificadores crudos, rutas de host ni prompts.
