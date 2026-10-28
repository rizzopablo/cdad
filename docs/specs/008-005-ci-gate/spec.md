# 008-005 — Gate de CI: un comando, una corrida, un veredicto atribuible

Status: Aprobada por el orquestador (HITL delegada del dueño) el 2026-10-28, con D1–D10 y PC-6 corregido.
Epic: epic-008-suite-coherence
Dependencia: 008-001..008-004
Autoridad: plan aprobado del epic (`docs/epics/epic-008-suite-coherence/plan.md`, fila 5) y su UNIT-CONTRACT.
Base técnica: `docs/specs/008-005-ci-gate/discovery.md`.

## Autoridad y objetivo

Hacer que el criterio del epic —«suite, gate por superficie y `validate-state` en cada push; el rojo no
se publica»— tenga **un solo entrypoint versionado** que lo ejecute, lo evidencie y falle cerrado cuando
el verde no es atribuible. No se crea capacidad nueva del ciclo ni un segundo mecanismo de cierre: el
gate consume los comandos que ya existen.

La política de rutas clasifica `Makefile` y `.github/workflows/*` como `unclassified`
(`python3 scripts/cdad_packet.py validate-policy --classify Makefile` → `unclassified`), de modo que el
único hogar admitido para el gate es `scripts/` (+ `docs/`).

## Alcance y límites

Dentro:

- `scripts/cdad-ci-gate.py`: entrypoint neutral de proveedor, orden fijo, cada paso una vez.
- `scripts/cdad-suite.py`: una línea de entorno del hijo en `run_pytest_to_logs` (`COLUMNS`).
- `sources/roles/test-writer.md`: la regla de cotas de reloj de pared, en su única casa, y los agentes
  derivados regenerados (`make agents`).
- Los tests de las specs cerradas 005-010 y 006-001 cuyas cotas superiores se ajustan.
- `docs/`: una página con el entrypoint y la ubicación de la evidencia.

Fuera:

- Versionar un workflow o un target de `Makefile` (requiere enmienda de política del dueño).
- Elegir runner, publicar, pushear, taggear, desplegar o activar nada.
- Duplicar `close`, `surface` o `validate-state`; redefinir sus contratos o sus PCs cerradas.
- Cambiar `parse_pytest_verbose` (D3: parser sin cambios).
- `make validate` dentro del gate (exige instalar agentes en un HOME efímero; ver D7).
- Paralelismo, caché, reintentos, tope propio de reloj para la suite, reloj inyectable (T-C).
- Debilitar por cuenta propia el criterio del epic para pushes docs-only (D9: decisión del dueño).

## Decisiones fijadas (HITL, no se re-discuten)

- **D1** Entrypoint `scripts/cdad-ci-gate.py`, orden fijo y una sola vez por paso: `validate-state` →
  `surface --collect-only` (solo clasificación) → doctrina → especialización Odoo → `close --all` (la
  única corrida de pytest) → consumo del `attempt.json`. Sin workflow versionado; sin segundo cierre.
- **D2** La clasificación por superficie se consume de `scripts/cdad-suite.py surface`;
  `.cdad/local/surface-gate.sh` queda fuera del camino operativo (ningún archivo versionado lo invoca;
  el archivo no está versionado: `.gitignore:11`).
- **D3** `COLUMNS` se fija en el entorno del hijo en `run_pytest_to_logs` para que `skips[].reason` no se
  trunque; el parser no cambia.
- **D4** Atribución fail-closed: commit no nulo, `dirty == 0`, intento en estado `finished`,
  `pytest_summary.verified` y exactamente un intento; si algo falla, salida != 0 nombrando la causa.
- **D5** El canario se reporta y no bloquea.
- **D6** `--base` obligatorio, sin default silencioso.
- **D7** `make validate` fuera del gate; se incluyen `scripts/cdad-doctrine-check.py` y
  `tests/validate-odoo-specialization.sh` (portables y verdes: rc 0 hoy).
- **D8** Evidencia por corrida bajo `.cdad/local`: `gate.json` con commit, dirty, base, ruta del intento,
  rc por gate, nodeids fallidos con motivo y skips con motivo; `loadavg` como diagnóstico.
- **D9** El criterio del epic se mantiene literal (la suite corre en cada push). Un push que solo toca
  documentación no hace fallar el paso de superficie; la suite igual corre. El costo se declara como
  límite y la excepción docs-only sobre la corrida de la suite es decisión del dueño, no del implementer.
- **D10** `suite-report.md` por corrida en la raíz de evidencia (no versionado).
- **PC-6** Regla de cotas de reloj de pared en una sola casa; T-A y T-B sobre los sitios de los 5 archivos
  de 005-010/006-001; T-C (reloj inyectable) diferido. **Corrección del orquestador sobre la formulación
  inicial del encargo:** el techo debe quedar a ≥10× el valor que produce la **conducta correcta** —no el
  defecto—, nunca igual al plazo que vigila, y cuando el defecto no queda por encima del techo admisible
  la aserción de duración no discrimina y se degrada a liveness. (La fórmula del encargo habría dejado
  pasar el defecto.)

## Contrato del gate

### Interfaz

    python3 scripts/cdad-ci-gate.py --base <ref> [--repo-root <dir>] [--evidence-root <dir>]

- `--base` es obligatorio; no hay default (D6). Se registra el sha resuelto de la ref.
- `--repo-root` existe para la costura de test (repos sintéticos, precedente
  `tests/test_008_002_suite_evidence.py`); su default es el checkout del script.
- `--evidence-root` default `.cdad/local`. La raíz de evidencia de **esta corrida** es un directorio
  nuevo `gate-<utc-stamp>-<pid>-<hex>` creado en exclusiva bajo esa base; la base se crea si no existe
  (un checkout solo-versionado no tiene `.cdad/`, y `.cdad/` está ignorado: `.gitignore:11`).
- Códigos de salida: `0` verde atribuible; `1` rojo (cualquier causa, nombrada); `2` error de uso
  (falta `--base`, raíz inutilizable). Se sigue la convención ya usada por `scripts/cdad-suite.py:980-1001`.

### Pasos (orden fijo, cada uno una vez)

| # | Paso | Comando | Aplicabilidad |
|---|------|---------|---------------|
| 1 | `validate-state` | `python3 scripts/cdad_packet.py validate-state` | siempre |
| 2 | `surface` | `python3 scripts/cdad-suite.py surface --base <ref> --collect-only` | solo si el cambio incluye alguna ruta no documental |
| 3 | `doctrine` | `python3 scripts/cdad-doctrine-check.py --quiet` | siempre |
| 4 | `odoo-specialization` | `bash tests/validate-odoo-specialization.sh` | siempre |
| 5 | `close` | `python3 scripts/cdad-suite.py close --evidence-root <raíz-de-la-corrida> --all` | siempre |

Si la precondición falla (base no resoluble o cambio ilegible) **no se ejecuta ningún paso** y los cuatro
de «siempre» se registran con `applicable: false`, `rc: null` y un detalle que nombra la precondición; el
paso de superficie no se registra porque su aplicabilidad depende de la clasificación que la precondición
impide. `gates` nunca queda vacío.

`close --all` es la **única** invocación de pytest del gate y de la corrida entera. El paso 2 no ejecuta
pytest: `--collect-only` (`scripts/cdad-suite.py:965`) emite la selección sin correrla.

### Aplicabilidad del paso de superficie (D9)

El gate enumera los cambios que `surface` considera —comprometidos, indexados y no ignorados desde
`<ref>`, sin renombrar— y clasifica **cada** ruta con el clasificador canónico de la política
(`python3 scripts/cdad_packet.py validate-policy --classify <ruta>`), no con un prefijo escrito a mano.
Con ese resultado:

- Todas las rutas son `documentation` (o no hay rutas): el paso se declara **no aplica** y no se ejecuta;
  se registra el motivo y el número de rutas. La suite corre igual.
- Alguna ruta no es `documentation`: el paso se ejecuta una vez y su `rc` debe ser `0`. Un `rc != 0`
  («cambio sin superficie clasificada», «selección resultante vacía», base sin inventario/mapa) es rojo
  del gate y nombra las rutas que lo producen.

La regla de clasificación vive en un solo lugar (la política y su clasificador); el gate solo enumera
rutas.

### Veredicto

`gate.json` (raíz de la corrida) — esquema 1:

```json
{
  "schema_version": 1,
  "tool": "cdad-ci-gate",
  "base": "<ref>", "base_commit": "<sha>",
  "commit": "<sha>|null", "dirty": 0,
  "run_root": ".cdad/local/gate-...", "attempt": "<run_root>/attempt-...|null",
  "change": {"kind": "sin-cambios|solo-documentacion|codigo|desconocido", "paths": 0, "documentation_paths": 0},
  "gates": [{"name": "validate-state", "rc": 0, "applicable": true, "detail": "..."}],
  "pytest": {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "xfailed": 0, "xpassed": 0,
             "verified": true,
             "failures": [{"nodeid": "...", "reason": "..."}],
             "skips": [{"nodeid": "...", "reason": "..."}]},
  "attribution": {"attributable": true,
                  "commit": "<sha>", "dirty": 0, "attempt_state": "finished",
                  "summary_verified": true, "attempts": 1, "causes": []},
  "canary": {"delta_lines": 0},
  "loadavg": [0.0, 0.0, 0.0],
  "verdict": "green|red",
  "causes": ["<token>: <detalle>"]
}
```

`verdict` es `green` sólo si **todos** los pasos aplicables tienen `rc == 0` y
`attribution.attributable` es `true`. `causes` lista cada causa bloqueante con un token estable
(`validate-state-rc`, `surface-rc`, `doctrine-rc`, `odoo-rc`, `close-rc`, `sin-intento`,
`intentos-multiples`, `attempt-no-finished`, `commit-null`, `dirty-no-cero`, `summary-unverified`).
Los caminos de precondición —base no resoluble o cambio ilegible— se declaran con `change.kind =
"desconocido"` y las causas `base-invalida` / `cambio-ilegible`; una excepción imprevista deja `gate.json`
con `fallo-interno`. Los tres valores son parte del esquema 1: el gate falla cerrado y nombra la causa en
vez de inventar una clasificación que no pudo medir.

`suite-report.md` (misma raíz) es la forma humana del mismo contenido: base y sha, commit, dirty, tipo de
cambio, una línea por gate con su rc, los recuentos de pytest, la lista de fallos con motivo y la de
skips con motivo, y el canario y la carga como diagnóstico.

El motivo de un fallo se toma de `stdout.log` del intento (bloque de fallos de pytest). Si no es
atribuible sin ambigüedad —incluidos los **errores de colección** (`ERROR <ruta>` sin `::`), que se
nombran con la ruta como nodeid—, `reason` queda `null` y el reporte referencia `stdout.log`: no se
inventa un motivo, y el aviso de no atribuibles cuenta fallos **y** errores. El motivo de un skip es el que la línea de estado publicó, completo (D3).

### Escrituras

El gate escribe **sólo** bajo la raíz de la corrida: `gate.json`, `suite-report.md` y lo que `close`
reserva en su intento (`attempt.json`, `stdout.log`, `stderr.log`, `canary-*.txt`). No toca el índice,
el árbol de trabajo ni el estado del proyecto; no hay push, tag, red ni instalación.

## Postcondiciones verificables

### PC-1 — Un comando, un orden, una corrida

Una invocación del gate ejecuta los pasos aplicables en el orden declarado, cada uno **una** vez, y
ejecuta pytest **exactamente una** vez, siempre dentro de `close --all`; el paso de superficie no corre
pytest.

**Consecuencia para el usuario final:** el dueño obtiene un veredicto por push pagando una suite, no dos,
y no puede «arreglar» el resultado repitiendo el cierre por otra vía.

**Oráculo:** argv observado de los comandos hijos en un repo sintético con CLIs grabadoras (una entrada
por invocación), más `gates[]` de `gate.json`. Falsificador: dos invocaciones de `close`, o una invocación
de pytest desde `surface` (nodeids ejecutados), o un paso omitido sin declararse «no aplica».

### PC-2 — Verde atribuible o salida distinta de cero

El gate sale `0` sólo si hay exactamente un intento, está en estado `finished`, su
`pytest_summary.verified` es `true`, su `rc` es `0`, su `commit` no es nulo y su `dirty` es `0`.
Cualquier otra combinación sale `!= 0` nombrando la causa.

**Consecuencia para el usuario final:** un verde significa «este commit, árbol limpio, resumen
verificable»; un verde no atribuible —el que la discovery midió con `commit: null`/`dirty: null`— deja de
ser posible como resultado del gate.

**Oráculo:** `attribution` + `causes` + código de salida sobre evidencias sintéticas (una por condición) y
sobre un intento real. Falsificador: un árbol con un archivo modificado produce `0`/`green`; o un
`attempt.json` con `commit: null` produce `0`.

### PC-3 — Rojo diagnosticable sin repetir la suite

En un rojo, `gate.json` y `suite-report.md` nombran cada nodeid fallido con su motivo (o `null` declarado
con referencia a `stdout.log`) y cada skip con el motivo completo que pytest publicó; el gate no vuelve a
ejecutar pytest para explicar el rojo.

**Consecuencia para el usuario final:** quien lee el reporte sabe qué contrato se rompió y por qué, con
una sola corrida; un skip nunca se lee como verde ni pierde su variable por truncado.

**Oráculo:** sobre un log sintético con fallos y skips conocidos (incluido un motivo largo) y sobre el
intento real del cierre. Falsificador: un nodeid fallido ausente del reporte, un skip con motivo vacío
cuando la línea de estado lo traía, o una segunda invocación de pytest después de un rojo.

### PC-4 — Superficie clasificada sin castigar la documentación

Un cambio que sólo toca rutas `documentation` de la política no hace fallar el paso de superficie y la
suite igual corre; un cambio que toca cualquier otra ruta exige una selección por superficie completa
(`rc == 0`) y, si falta, el gate es rojo nombrando las rutas sin superficie.

**Consecuencia para el usuario final:** un cambio de documentación no se bloquea por un mapeo que no
puede aplicar, y un cambio de producto con el mapa desactualizado no pasa como verde.

**Oráculo:** `change.kind`, `gates[surface]` y código de salida sobre repos sintéticos (diff sólo
`docs/`, diff sólo `README.md`, diff de producto sin consumidores declarados). Falsificador: diff
docs-only → salida `!= 0`; o diff de producto con el mapa incompleto → salida `0`.

### PC-5 — Portable, hermético y sin publicar

El gate corre desde un checkout sólo-versionado, sin rutas del host, sin HOME instalado, sin red y sin
secretos; no escribe fuera de la raíz de la corrida y no publica nada.

**Consecuencia para el usuario final:** cualquier máquina o runner puede ejecutarlo tal cual, y su
resultado no tiene efectos externos.

**Oráculo:** ejecución desde un `git archive` extraído en un directorio temporal con `HOME` vacío; grep de
rutas del host en lo versionado; inventario de escrituras (sólo la raíz de la corrida). Falsificador: una
ruta absoluta del host, una dependencia de red, una escritura fuera de la raíz, o una invocación de
`push`/`tag`/`curl`.

### PC-6 — Cotas de reloj de pared: una regla, una casa, cotas que discriminan

Toda cota superior de reloj de pared de los archivos `tests/test_005_010_b1_last_assistant.py`,
`tests/test_005_010_reviewfix.py`, `tests/test_005_010_t1_durable_signal.py`,
`tests/test_006_001_reviewfix.py` y `tests/test_006_001_t2_wait_recovery.py` cumple estas condiciones:

1. Declara el par de hipótesis que separa (conducta correcta vs. defecto concreto); sin par declarado no
   es una cota de duración: se declara liveness y no se presenta como cota.
2. Su techo queda a **>= 10x** el valor que produce la **conducta correcta** (margen contra la carga del
   runner) y **nunca** es igual al plazo que vigila (una cota igual al plazo no discrimina y convierte la
   carga en rojo falso).
3. Si el defecto produce un valor menor o igual al techo admisible, la aserción de duración no puede
   discriminar: se degrada a liveness en vez de conservarse.

La regla vive en una sola casa (`sources/roles/test-writer.md`, bloque `cdad-shared:convention-rule`); los
sitios la aplican con T-A (agrandar la separación del fixture) o T-B (degradar a liveness donde la
decisión ya está assertada). La promesa original de cada spec cerrada (005-010 PD-2/PD-5; 006-001
PC-8/PD-7/PD-11) se conserva: no se re-ancla a otra promesa.

**Consecuencia para el usuario final:** la carga del runner deja de producir rojos falsos y una espera
realmente desacotada sigue enrojeciendo.

**Pérdida declarada (decisión del orquestador, HITL, tras el review de stage 4).** En los cinco sitios cuya
promesa es «responde/termina en la cota» (B3a, B3b, PD-7, PD-11 ×2) el techo re-anclado ya no distingue una
espera **acotada pero por encima de la cota** (2×), porque el envelope del producto no expone duración y la
espera de la interfaz (cota + gracia) no se dispara con ese exceso. El gate deja de detectar esa clase:
queda registrada en `Deferred-hardening` con su motivo, y los textos/docstrings de esos sitios dejan de
presentar la guarda como «en la cota». Restituirla exige un observable de duración en el adaptador, que es
producto y otra unidad.

**Oráculo:** forma de cada cota en los 5 archivos (par declarado, techo y plazo vigilado) más la decisión
que la acompaña, y la suite de esos archivos en verde. Falsificador: una cota igual al plazo que vigila;
un sitio degradado a liveness cuya decisión ya no se asserta en ningún lado; una cota que no puede fallar
presentada como cota.

### PC-7 — Evidencia por corrida, sin sobrescritura

Cada corrida deja una raíz propia con `gate.json`, `suite-report.md` y exactamente un intento; una
corrida posterior no pisa ni adopta la anterior. Toda corrida deja `gate.json`, incluso cuando falla
antes de llegar a `close`.

**Consecuencia para el usuario final:** el dueño puede auditar cualquier push pasado —qué corrió, con qué
commit, qué falló y por qué— sin depender de la memoria de la sesión.

**Oráculo:** dos corridas consecutivas → dos raíces, ambas completas; corrida con `--base` inválido →
raíz con `gate.json` y causa. Falsificador: dos corridas comparten raíz, o una corrida no deja `gate.json`.

### PC-8 — Canario y carga: visibles, no decisorios

`canary.delta_lines` y `loadavg` aparecen en `gate.json` y en el resumen humano; ninguno altera el
veredicto ni el código de salida.

**Consecuencia para el usuario final:** la interferencia con el HOME real y la carga de la máquina son
visibles como diagnóstico sin convertir un verde de suite en rojo por una condición que esta feature no
gobierna.

**Oráculo:** evidencia con `delta_lines > 0` y con `loadavg` alto → mismo `verdict` que sin ellos, con
ambos campos presentes. Falsificador: un delta de canario cambia el veredicto; o el resumen humano y
`gate.json` discrepan sobre canario o carga.

## Invariantes

- **INV-1** Una corrida del gate implica exactamente una ejecución de pytest.
- **INV-2** El gate escribe sólo bajo la raíz de la corrida; no modifica el árbol de trabajo, el índice
  ni el estado del proyecto.
- **INV-3** El gate no publica: no hay push, tag, deploy, red ni instalación.
- **INV-4** El paso de superficie no selecciona la suite: `close` corre siempre `--all`.
- **INV-5** Ningún diagnóstico (canario, carga, duración) convierte un rojo en verde ni un verde en rojo.
- **INV-6** El gate no reimplementa `validate-state`, `surface`, `close`, la clasificación de rutas ni el
  parser de pytest: los invoca.

## Criterios de aceptación medibles

- **AC-1 (PC-1)** En un repo sintético con CLIs grabadoras: 1 invocación de `validate-state`, 1 de
  `surface` (sólo si el cambio no es documental), 1 de doctrina, 1 de especialización Odoo, 1 de
  `close --all`; 0 invocaciones de pytest fuera de `close`.
- **AC-2 (PC-2)** Ocho evidencias sintéticas (una sana y una por condición de atribución) producen
  `green`/`red` y causa exacta; en el árbol real, un archivo modificado produce rojo con `dirty-no-cero`.
- **AC-3 (PC-3)** Un log sintético con 2 fallos y 3 skips (uno de 678 caracteres) produce los nodeids y
  los motivos completos en `gate.json` y en `suite-report.md`, y no hay segunda corrida de pytest.
- **AC-4 (PC-4)** Diff sólo `docs/` → `change.kind = solo-documentacion`, superficie no aplica, salida del
  gate determinada por los demás pasos; diff de producto sin consumidores → rojo que nombra la ruta.
- **AC-5 (PC-5)** `git archive HEAD` extraído en temporal con `HOME` vacío: el gate completa y deja su
  evidencia; `git status --porcelain` del árbol real queda igual antes y después.
- **AC-6 (PC-6)** Los 5 archivos no contienen ninguna cota superior igual al plazo que vigila; cada cota
  conservada declara su par; cada sitio degradado conserva la decisión que custodiaba.
- **AC-7 (PC-7)** Dos corridas seguidas dejan dos raíces con `gate.json` y `suite-report.md`; la segunda
  no modifica la primera.
- **AC-8 (PC-8)** Con `delta_lines > 0` el veredicto no cambia y el campo está en ambos artefactos.

## Superficie técnica verificada

- `scripts/cdad-suite.py:541-568` `cmd_surface` (`--base` obligatorio, `--collect-only`, JSON
  `{base, all, nodeids}`); `:412-422` `changed_paths`; `:102-115` `collect_nodeids`.
- `scripts/cdad-suite.py:818-839` reserva exclusiva del intento; `:841-857` commit y dirty; `:859-877`
  `run_pytest_to_logs` (argv `:870`, entorno `:872-873`); `:880-948` `cmd_close` (registro
  `attempt.json`); `:729-781` `parse_pytest_verbose`.
- `scripts/cdad_packet.py:1-11` wrapper → `skills/cdad-cycle/scripts/cdad_packet.py`;
  `validate-state` y `validate-policy --classify` (`:9641-9649`).
- `scripts/cdad-doctrine-check.py` (rc 0 verificado); `tests/validate-odoo-specialization.sh` (68 asserts,
  0 fallos, rc 0 verificado).
- `.gitignore:11` `.cdad/`; `docs/cdad-policy.json` (`documentation_roots: ["docs"]`,
  `documentation_files: ["README.md"]`).
- `sources/roles/test-writer.md:64-94` bloque `cdad-shared:convention-rule` (casa única de la convención;
  `sources/roles/reviewer.md:88-89` la apunta).
- `Makefile:1-29`: `agents/` son salidas declaradas de `scripts/cdad-generate.py`; `make agents`
  regenera; `make validate` = consistencia (necesita HOME real) + especialización Odoo.

## Decisiones de diseño

- **Superficie: decidir-y-no-ejecutar vs. ejecutar-y-absorber.** Se elige clasificar la ruta y no invocar
  `surface` cuando el cambio es sólo documentación. Criterio: `surface` no puede tener éxito en ese caso
  (008-002 fija «selección vacía termina no cero», `spec.md:136`), así que invocarlo fabricaría un rojo
  sin información. La regla de qué es documentación queda en un solo lugar (la política).
- **Fallo barato vs. suite**: se ejecutan todos los pasos y el veredicto agrega; un paso barato en rojo no
  suprime `close`. Criterio: el criterio del epic fija la suite en cada push y `close --all` no depende de
  los demás pasos.
- **Raíz por corrida vs. raíz fija**: raíz nueva por corrida. Criterio: `close` ya garantiza un intento
  único; una raíz fija haría ambigua la condición «exactamente un intento» de D4.
- **Casa de la regla de cotas**: el bloque de convención (`sources/roles/test-writer.md`), no un archivo
  nuevo: ya es la definición única y el punto al que apunta el reviewer.
- **Motivo de fallo: parser propio del gate vs. extender el de `close`.** El gate lee el bloque de fallos
  de `stdout.log` y `parse_pytest_verbose` no cambia (D3). Criterio: el resumen verificado de 008-002 es
  un contrato cerrado. Límite: la atribución del motivo es best-effort; si es ambigua queda `null`.
- **Dos validadores extra (D7)**: se insertan entre `surface` y `close`, conservando el orden relativo de
  D1 (validate-state primero, close último).

## Deferred-hardening

- **Discriminación de la espera acotada-por-encima-de-la-cota** en los cinco sitios de cota (B3a, B3b,
  PD-7, PD-11 ×2): hoy no es observable sin exponer la duración/deadline en el envelope del adaptador. El
techo re-anclado mide el host, no esa clase de defecto; se declara la pérdida en vez de presentarla como
cubierta.
- **T-C — reloj inyectable** en los tests de reloj: sustituiría las cotas de pared por un reloj
  controlado. Exige un punto de inyección en el producto que esta feature no necesita para PC-6.
- **Tope propio de reloj para la suite**: si `close` cuelga, el gate cuelga (46-103 min medidos). Un tope
  exige matar el hijo con semántica nueva; hoy el techo lo pone el runner. Se declara, no se implementa.
- **`make validate` completo dentro del gate**: depende de instalar agentes en un HOME efímero (F011).
- **Ejecución por superficie en vez de la suite completa**: reduciría el costo, pero el criterio del epic
  pide la suite en cada push; usarla sería debilitarlo por cuenta propia.
- **Enmienda de política para versionar un workflow**: decisión del dueño; hoy `.github/**` y `Makefile`
  son `unclassified`.
- **Cobertura porcentual, benchmark de duración y matriz de runners**: sin consecuencia contractual
  identificada.

## Límites declarados

- Sin runner, sin workflow versionado y sin publicación: el gate **no publica**; expresa «el rojo no se
  publica» como salida != 0, que cualquier paso de publicación condicionado a él respeta.
- Sin secretos: el gate no lee credenciales ni configura entornos; su portabilidad se verifica con `HOME`
  vacío.
- El costo por push es el de una suite completa (46-103 min, sin paralelismo): el criterio del epic se
  mantiene literal y su reducción no es decisión del implementer.
- La atribución del motivo de un fallo depende de que `stdout.log` lo publique; cuando no, se declara
  `null` con la ruta del log.
- Fuera del alcance del gate queda el extremo de un agente que ignore sus instrucciones: exigiría otro
  harness.
