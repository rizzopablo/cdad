Validated packet on first line — proceeding under the packet contract (focal re-review, read-only, write_scope empty). First step: verify the contract hash and gather the declared inputs.
Contrato verificado: `sha256(spec.md) = c25e…d890` ✓. Ahora leyendo los hallazgos de revisión (O-1/O-2/O-4/O-5 + Disposición), RED/GREEN y las secciones relevantes de la especificación.
Ahora se leen la spec §2.2/§2.3 y el diff en revisión.
Contrato verificado contra la hash del packet. Ahora leyendo el diff bajo revisión (production scripts + reference) y el nuevo test.
La spec y los informes están cargados. Ahora leyendo el estado actual del código modificado (contexto completo alrededor de los cambios), el nuevo test y la sección emptied-sha de `install.sh` (O-5).
El punto crítico (juicio 4) requiere la lectura completa del bloque de prune y del estado de remoción en `install.sh` — el código que leo ahora en `:654` (`[ -z "$recorded" ] → removable`) parece contradecir la afirmación del RED acerca de empty-sha → preservado como CONFLICT. Leyendo el contexto completo:
El bloque de prune está completamente a la vista y mi lectura lo contradice: dirijo el escenario de O-5 (decisionesichtlich — probe black-box, raíces temporales, nada fuera del alcance) más las reglas de regresión O-2/O-1 de forma concurrente:
Las comprobaciones de regresión de O-2 se están resolviendo (leer: `Path.home()` y `delegation_env_file_path` re-derivados de la única regla; otros `Path.home()` están fuera del alcance focal; la semántica `CDAD_INSTALL_ROOT=""` está alineada tanto en el lector como en el instalador). Ahora, la sonda decisiva para O-5 — escenarios black-box escritos a mano en el aspecto VANILLA (del RED) en un entorno temporal:
Manifiesto ubicado. Preparando las variantes de sha oobsoletas (registradas a mano) reejecutando en un entorno temporal:
El comportamiento observado contradice mi lectura directa del código; para cerrarlo y aclarar qué está cambiando: el tabulado se dobla en la lectura del shell. Obteniendo un registro de files: sha vacío probablemente indica un formato incorrecto y una ruta de eliminación inesperada.
La sonda es decisiva y falsifica lo que reporta el archivo RED — meaty finding. Confirming remaining axes: read the RED test file and rerun the focal suite as verification of the O-1/O-4/O-2 closures.
Las pruebas son black-box fieles con mapeo uno-a-uno hacia los hallazgos. Verificando que la afirmación del GREEN se mantenga en mi carril:
4/4 focal pasa en mi carril — las correcciones O-1/O-2/O-4 se mantienen. Un último sondeo para hacer la O-5 infalible en la superficie de `--uninstall` (la misma función compartida decide ambas), más limpieza:
# Informe de revisión — 006-003 (re-revisión focal, paquete `…-reviewer-review-002`)

**Cargo:** revisor · **Alcance de escritura:** vacío (sin escrituras realizadas — solo lecturas + sondas black-box en el entorno temporal `/tmp/opencode`, real `HOME`/`~/.config/cdad/*` y `tests/.sensitive-patterns.local` no leídos; INV-6 respetado durante las sondas) · **Contrato:** `sha256(spec.md) = c25e…d890` ✓ verificado contra el paquete.

**Objeto juzgado:** diff `c57fc79^..HEAD` (RED `c57fc79` test-only 398 líneas; GREEN `ef8d2f8` — `skills/cdad-cycle/scripts/cdad_delegate.py`, `…/cdad_delegate_opencode.py`, `…/references/cli-delegation.md`; + docs de estado del orquestador). Fuente de la re-revisión: `review.md` (Disposición O-1/O-2/O-4/O-5), `rf-red.md`, `rf-green.md`, spec §2.2/§2.3.

## Verificación de bloqueo previa (rápida)

- `sha256sum docs/specs/006-003…/spec.md` → `c25ebf0e…d890` — contrato válido.
- `git diff --stat c57fc79^..HEAD` → 7 archivos (sin `install.sh` — coherente con el informe del GREEN).
- **Sonda focal propia** (árbol temp, escrito solo en `/tmp/opencode`): `python3 -m pytest tests/test_006_003_rf_review_fixes.py -q` → **4 pasaron en 27.12s** — el informe del GREEN es reproducible en mi entorno.

## Bloqueantes

**B-1 · Requerido · Bucket: h · Veredicto: BLOQUEANTE — O-5 NO cumple su condición de cierre; el informe del RED que la cerró por observación es falso en 2 representaciones alcanzables, y el escape de INV-2 (retiro sin comparar sha) es real en ambas superficies (reinstalación y --uninstall).**

*Procedencia:* `install.sh:654` (`owned_removal_state`: `[ -z "$recorded" ] → removable`, comentario de `:643-644` que documenta explícitamente «when no digest was recorded … the historical --uninstall rule»), insumo al TSV del prune en `install.sh:1204-1247`, y transporte shell de ese TSV en `install.sh:1225-1247` (`while IFS=$'\t' read -r abs rel sha source`).

*Mecanismo verificado black-box* (10-supo propios en árbol desechable, manifiesto publicado editado a mano — exactamente el escenario declarado por Disposición): el TSV registra `abs<TAB>rel<TAB>sha<TAB>source`; con `sha` **vacío** la columna colapsa bajo `IFS=$'\t' read` (los tabs consecutivos son un solo delimitador en bash). Entonces:

- **sha vacío + `source` vacío/ausente** → `recorded=""` → `removable` → **el archivo se RETIRA con `rm -f`**, directamente contra la condición de cierre del O-5 («un registro con sha vacío no se retira; se conserva») e INV-2 («solo retira lo propio con sha256 sin cambios»). Verificado en **reinstalación** (`REMOVE (own obsolete…) zz-probe-shaless.txt`/`zz-probe-bare.txt`, `Obsolete prune: 2 retired`) y en **--uninstall** (`UNINSTALL … zz-probe-unins.txt`, rc=0).
- **sha vacío + `source` no vacío** → por el colapso, `$sha` recibe el valor de `source` («hand-edit») → `modified` → se conserva por ACCIDENTE de colisión de columnas, no por la regla pedida; bajo la corrupción visible: el registro continúa con campos **permutados** (`{"sha256": "hand-edit", "source": ""}` — el hueco del digest queda con el texto de la fuente) y el CONFLICT dice «registered hand-edit» (basura en lugar del digest). El RED observó esto (su «observación lateral», rf-red.md:107-113) pero no lo conectó: la preservación universal que reportó es un artefacto del colapso de columnas — sus 7 variantes nunca incluyeron sha vacío **con source también ausente**, que es la representación que retira.
- **sha `null`** → `recorded="None"` → conservado con registro corrupto persistente (`{"sha256": "None", …}`, motivo «registered None»).
- **Control positivo:** sha correcto y archivo ya no desplegado → retirado («REMOVE … zz-probe-sha.txt») — el prune sano funciona; el escape es exclusivo de la representación degenerada, tal como el O-5 original delimitó.

*Consecuencia:* el mandato de la Disposición para esta ronda («los opcionales baratos que contradicen la letra de la spec», O-5 incluido) quedó **descargado sobre evidencia falsa**: ni código ni test lo implementan; la cadena RED→GREEN se cerró con un mismatch del test-writer que la(s) sonda(s) refutan.

*Condición de cierre verificable:*
1. Regla decidida e implementada: registro con sha vacío **nunca** `removable` (→ conservar como CONFLICT), eliminando el mecanismo de colapso de columnas (remedio estructural: que el python que emite el registro decida el estado por registro o use un orden/delimitador inmune a campos vacíos — no un TSV de 4 columnas leído por `read` bash).
2. El registro conservado se publica **coherente** (sha en su slot; motivo sin «registered <source>»).
3. Comentario del método (`install.sh:643-644`) actualizado a la nueva regla.
4. RED+GREEN con aserciones para las representaciones hoy retirantes (sha+source vacíos) y hoy corruptas (sha vacío + source presente; null).
5. Corrección del registro en `rf-red.md` §4 (la afirmación «ya se cumple en todas las superficies y representaciones probadas» es refutada por las 2 representaciones arriba, con rutas `zz-probe-*` citadas).

## Opcionales

**OPT-1 · Consideración opcional · Bucket: m · Veredicto: OPPCIONAL — el diagnóstico 401/403 de la rama entorno ya no nombra ninguna ruta de archivo candidata.**
Procedencia: `cdad_delegate_opencode.py:1097-1101` (rama env: «…no credential file was consulted» sin ruta) vs *spec* §2.3 (`spec.md:48`): «nombres de variables, **ruta resuelta**, la procedencia del valor». La elección del GREEN (ramificar y omitir la cláusula) resuelve el `None` (O-4 ✓) pero en la rama entorno el diagnóstico dejó de nombrar el `delegation.json`/cripta por defecto como destino alternativo — el usuario que necesita migrar al archivo debe recurrir a `cli-delegation.md` (coincide con lo nueva prosa, `cli-delegation.md` § Configuration). Test O4 solo fija no-`None` + entorno nombrado. No es confuso para su caso de uso (el valor rechazado era del env; el fix es editar ese env). **Cierre:** nombrar la ficha por defecto parentéticamente también en la rama env, con test que la fija.

Los demás ejes del diff — sin hallazgos: O-1 cierra por su condición (env `""`→ausente en ambas variables, `:962-967` + test O1 con oráculo de header); O-2 cierra sin regresión detectada (verdict abajo, juicio 2); el RED es black-box fiel para O-1/O-2/O-4; tipografía coherente con la regla única de ubicación.

## Abstenciones

1. **Suite completa y `make validate`:** política del paquete — la corre quien cierra el task; no las re-corro en review (O-7 heredado, sin reabrir).
2. **Enumeración 1-a-1 de las 7 variantes del RED:** reproduje las clases decisivas (sha vacío±source, null, digest correcto, registro vacío) en reinstall y --uninstall; no reconstruyo sus ediciones exactas (el script de hand-edit del test-writer no está en el repo) — la refutación vale por clase: existe representación alcanzable que RETIRA.
3. **Efectos de clientes externos de `delegation.json` con `CDAD_INSTALL_ROOT` exportado con valor distinto al de instalación** (nuevo vínculo O-2 en el lector): la regla única es la decisión registrada del dueño en la Disposición; no la reabro (calibración regla 4) y no evaluó consumo fuera del repo.

## Resumen: 1 bloqueante, 1 opcional, 3 abstenciones

## Juicios por punto pedido

1. **O-1, O-2, O-4 cerrados según su condición:** **Sí** (3/3). O-1: `""`→ausente en `_preflight_password` (loop con `if value:`) + oráculo de header-vacío; el file-case `KEY=` seguía bien. O-2: `cdad_config_dir` es la regla única y `delegation_env_file_path` re-deriva de ella — **sin regresión** para el uso primario (sin `CDAD_INSTALL_ROOT`, con `XDG_CONFIG_HOME` definido el lector resolved `XDG/cdad`, idéntico al pre-fix y al instalador `${XDG_CONFIG_HOME:-…}`); coincidencia lector–instalador verificada para las 4 combinaciones (incl. strings vacías de XDG y `CDAD_INSTALL_ROOT=""`, que el instalador rechaza en `:529-536`); los demás `Path.home()` del árbol (`:1343` state-dir, `cdad_packet.py:97`, `cdad-version-check.py:148`) son de otra función y no divergen. O-4: rama por `source`, nunca interpola `None`. GREEN reproducido: **4 passed**.
2. **Regresión de O-2 (primario sin root, XDG definido):** **No** — comportamiento byte-por-byte el mismo en esa configuración (`if xdg_config_home:` no toca la base); la divergencia mitad HOME-roa/mala-raíz que motivó el O-2 es el caso que el fix eliminó y resto de combinaciones alineadas.
3. **INV-1 (exposición del valor):** **Sin camino nuevo.** El único flujo nuevo interpreta vacío→ausente (el header se construye solo con no-`None`, comportamiento previo sin cambios); la nueva prosa del diagnóstico interpola solo variables (`OPENCODE_*`) y rutas, jamás `credential["value"]` (verificado en `_unauthorized_diagnosis` completo); el texto de la rama env es meta-información sin valor. El test O4 oracle busca no-`None` con fixture loopback y constantes centinela (sin valores de host).
4. **O-5 (7 variantes → conservado):** **No confirmado — refutado.** La lectura de `install.sh` degeneré la presunción del RED y las sondas en árbol desechable lo retraducen: con sha vacío y `source` vacío/ausente el archivo **se retira** (reinstalación y --uninstall), con la corrupción de registro descrita en B-1. La preservación que reportó el RED solo ocurre cuando la columna colapsada queda rellenada por el `source` — accidente, no regla. **B-1 bloqueante.**

---

## Disposición del orquestador (2026-10-18)

- **B-1 (O-5) se corrige.** Por el criterio MVP no bloquearía: solo se alcanza con un manifiesto editado a mano, porque el instalador siempre registra el sha. Pero es un defecto estructural de lectura (el TSV leído con `read` de bash colapsa columnas vacías), el arreglo es barato, y la ronda anterior ya lo había pedido. La afirmación de `rf-red.md` §4 («ya se cumple») queda refutada por esta re-review.
- **OPT-1** también se corrige en la misma ronda, porque es una línea: en la rama de entorno, el diagnóstico también nombra el archivo por defecto como alternativa.
