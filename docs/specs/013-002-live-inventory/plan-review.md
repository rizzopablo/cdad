# Plan review — `013-002-live-inventory`

**Objeto:** `docs/specs/013-002-live-inventory/spec.md`, sha256 `bf4f851f92ebc7224bbd178531538124b1b21c5ecadeab43159f8eac05f5e774`, en HEAD `ccc9129b`.
**Dictamen:** no apto para aprobar tal como está, con **2 bloqueantes**, ambos en la Promesa D (PC-7). Las promesas A, B y C no tienen bloqueantes. Esto es un informe de revisión: no aprueba el borrador; decide el dueño.

**Admisión (ruta C):** el paquete se aceptó. `cdad_packet.py render --request …` es idéntico byte a byte a `PACKET.md` (`cmp` → SAME). La identificación coincide con REQUEST, el contexto de ejecución es v2 y el sha del contrato coincide.

## Hallazgos

### B1 — PC-7 no fija cuándo se exige `validate` y choca con RED
**Severity:** Required · **Verdict: BLOCKING** · **Bucket: h**
**Ubicación:** spec PC-7 («re-entries pertinentes de cambios de tests»; «un resultado no cero… bloquea») y PC-6.

- **Evidencia:**
  - Todo módulo o nodeid nuevo da rc=1 hasta que se actualiza el inventario (`scripts/cdad-suite.py:208-209`, `:243-245`).
  - El inventario está en `docs/`, y el test-writer solo escribe en `tests/**`.
  - El recorrido de materialización de PC-6 cubre solo sustituciones. RED, properties y E2E añaden tests sin paso equivalente: PC-7 solo dice que «los handoffs contemplan» un delta.
  - La lista de RED en `re-entry.md:290-302` no incluye inventario.
- **Consecuencia:** hay dos lecturas posibles.
  - Si RED cuenta como «pertinente», cada RED queda bloqueado por rc=1 salvo que se materialice antes un delta cuyo momento y responsable no están definidos.
  - Si no cuenta, la obligación puede caer solo en la aceptación final, y la brecha vuelve a acumularse durante la feature.
  - Ambas lecturas cumplen el texto, así que PC-7 no es verificable. También afecta a PC-1, porque los verificadores de esta misma feature cambian el universo: el inventario debe actualizarse después del último commit de tests.
- **Condición de cierre:** PC-7 enumera los re-entries donde `validate` bloquea y aquellos donde solo se entrega delta. También define el flujo de altas ordinarias: quién propone, quién materializa y antes de qué transición. Deja explícito que rc=0 se mide sobre la revisión que ya contiene ese delta.

### B2 — «Cuando el proyecto declare inventario vivo» no tiene productor
**Severity:** Required · **Verdict: BLOCKING** · **Bucket: h**
**Ubicación:** spec PC-7 y §5 («no ampliar el CLI… ni cambios de esquema»; procedimiento condicional).

- **Evidencia:**
  - No hay ninguna mención a `cdad-suite` ni `suite-inventory` en `skills/`, `sources/`, `install.sh`, `build/`, `Makefile` ni `docs/cdad-policy.json` (grep vacío).
  - `docs/suite-maintenance.md` no existe, y `docs/` no se distribuye como norma del producto.
  - La spec no define dónde ni cómo se declara el inventario, ni dónde se declara el comando de integridad.
- **Consecuencia:** la norma distribuida no puede decidir si aplica, ni siquiera aquí. Se omite sin señal o se aplica por conocimiento implícito. Es un productor ausente para un consumidor comprometido.
- **Condición de cierre:** la spec nombra el lugar exacto y la forma de la declaración, compatible con §5. Ejemplo: una sección fija en un documento de proyecto que el orquestador lee. Indica qué rol la lee y qué pasa si falta: no aplica de forma explícita, sin bloquear. El test focal comprueba la transmisión de esa regla.

### O1 — Actualizar el inventario anula la selección focal de `surface`
**Severity:** Optional · **Verdict: OPTIONAL** · **Bucket: m**
**Ubicación:** PC-8; `scripts/cdad-suite.py:45`, `:508-510`.

Cualquier cambio en el inventario o el mapa selecciona toda la colección. PC-7 hace que eso ocurra en cada cambio de tests. PC-8 ya aclara que esto no autoriza ejecutar, y ninguna instrucción distribuida usa `surface`, así que no hay daño inmediato. Conviene que `docs/suite-maintenance.md` indique usar `--collect-only` o una selección explícita.

### O2 — El lote nuevo no se distingue en el mapa
**Severity:** Consider · **Verdict: OPTIONAL** · **Bucket: m**
**Ubicación:** PC-5; cabecera de `pc-map.json`.

`pilot_modules` y `pilot_nodeids_mapped: 17` conservan su sentido histórico, y las entradas nuevas comparten la misma lista `entries`. La spec no dice cómo identificar el lote. `decision_note` o `task` por entrada serviría sin cambiar el validador.

### O3 — Un helper conserva el contrato literal `VERIFY`
**Severity:** Nit · **Verdict: OPTIONAL** · **Bucket: h**
**Ubicación:** PC-2.

`tests/_rf2_open_pause.py` es `helper`, con contrato `VERIFY` y confianza `baja`. PC-2 habla de «tests» y de asignaciones nuevas o corregidas, así que el helper queda fuera. `validate` lo acepta, porque solo exige `contract` no vacío. Hay que declararlo como deuda o corregirlo, para que PC-3 lo refleje.

### O4 — El test-writer necesita leer el mapa de otra feature
**Severity:** Nit · **Verdict: OPTIONAL** · **Bucket: m**
**Ubicación:** PC-6, paso 2.

El rol lee `tests/`, spec y systemPatterns, y el mapa vive en `docs/specs/008-002…`. El `read_scope` de cada paquete debe declararlo. La spec ya dice que no concede permisos, así que esto solo requiere cuidado al despachar.

## Afirmaciones contrastadas sin defecto

- **Brecha actual:** `validate` da rc=1 con **19 módulos y 163 nodeids** sin asignar. Son 18/158 del plan más `test_013_001…` (1 módulo y 5 nodeids). Colección: **1942**. La spec no fija la cifra, así que es correcto.
- **PC-1:** los dos únicos tipos de problema son módulos y nodeids sin asignar, sin fallos de timing ni de mapa. Obtener el universo de nuevo al verificar es adecuado. No hay `importorskip` ni `collect_ignore` en `tests/*.py`. Los 231 `.py` bajo `tests` se miden desde el árbol de archivos, por lo que un archivo no versionado también altera el resultado.
- **Datos vivos:** 212 módulos (206/5/1). 29 registros: 28 `mantener` (26 acreditados y 2 `VERIFY`) y 1 `eliminar` acreditado. La referencia inexistente de `test_opencode_read_map_and_steps.py` es real.
- **PC-4:** el registro `eliminar` tiene destino vigente, lo que confirma la diferencia con Retirar.
- **PC-5:** los dos tests B1 existen en `tests/test_005_013_t1_unit_projection.py:1117,1169`. El mapa admite `mantener` con destino actual sin cambios de esquema.
- **PC-6:** `check_map` obliga a un destino recolectable (`cdad-suite.py:279-280`), así que las cadenas de sustitución son compatibles con el validador.
- **PC-8:** `validate` solo se invoca desde su subcomando (`:986-987`), y CI no lo incluye. La baseline `b65defa2` no contiene `pc-map.json` (`git show` → fatal), y la comparación usa solo `original_nodeid`.
- **Alcance:** PC-7 no es gold-plating. El encargo de la unidad incluye evitar que el inventario se desactualice sin que alguien lo note, sin gate nuevo.
- **Criterio MVP:** se respeta. No hay acreditación global, ni CLI nueva, ni clasificador.

## Abstentions

- **Asignaciones futuras:** no se juzga la corrección semántica de los 19 módulos, porque aún no existen.
- **Mínimo del lote:** no se juzga si la semilla B1 basta para las necesidades de 013-003. Eso depende de ese lote, y la spec la presenta como revisable.
- **Contrato de unidad:** no leí `UNIT-CONTRACT.md` completo. Me basé en el objetivo del REQUEST del architect y en el plan del epic.
- **Fuentes no releídas:** no releí 008-006 ni ADR-041 línea por línea. Tampoco comprobé todos los localizadores de la tabla de fuentes.

## Evidencia

- **Archivos modificados en el repositorio:** ninguno. Solo escribí salidas temporales en `/tmp`.
- **Commit:** ninguno nuevo. Referencia `ccc9129b`. Antes de esta revisión ya existía `docs/.cdad-state.json` modificado, que no toqué.
- **Comandos principales:**
  - `sha256sum docs/specs/013-002-live-inventory/spec.md` → coincide con el contrato.
  - `python3 scripts/cdad_packet.py render --request <REQUEST>` + `cmp … PACKET.md` → SAME.
  - `python3 scripts/cdad-suite.py validate` → rc=1, 163 nodeids + 19 módulos.
  - `python3 -m pytest --collect-only -q -p no:cacheprovider tests` → 1942 tests collected.
  - Inspección de los JSON con Python; `git show b65defa…:…/pc-map.json` → fatal, ruta ausente.
- **Suite completa no realizada:** solo se ejecutó la colección, que no corre los tests.
