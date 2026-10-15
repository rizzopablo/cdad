# Aceptación de 005-012-transition-registration (T8, gate de la feature)

**Instrumento.** El CLI **real del repo** (`skills/cdad-cycle/scripts/cdad_packet.py` y
`…/cdad_result.py`) corrido como **subproceso** sobre **proyectos descartables** creados en `<tmp>`
(`/tmp/opencode/…`), con el **`HOME` del subproceso en un tempdir VACÍO**. **Nunca este repo, nunca
HOME.** Arnés fuera de git: `.cdad/local/005-012-t8-acceptance.py`; evidencia cruda en
`.cdad/local/005-012-t8-evidence.json` (no versionada). Fixture **sintético y anónimo**
(`epic-demo-900-acceptance`, `900-001-demo-transition`); sin rutas del dueño.

**AC-1 — un ciclo representativo registrado SÓLO con la operación nueva, sin editar el state a mano
(forma mínima, sin digests).** 8 invocaciones, **todas rc=0**:
`open-unit` → `advance` (discovery→specification) → `gate` de etapa 2 (spec y plan, **sin pasar ningún
digest**) → `delivery` del RED → `delivery` del GREEN → `delivery` del Memory Bank → `gate` del T4 →
`closure` (**sin digests**). Resultado: **7 entradas** de la operación con
las clases `advance, gate, delivery, delivery, delivery, gate, closure`; la feature queda `done`, `active_feature:
None`, `current_stage: idle`. El **digest del recibo se derivó** en
**todas** las entregas (`True`) — el operador no calculó ninguno.
El state final es **byte a byte el que produjo el CLI**: `sha256` antes `5d0e23e5dea2…` → después
`f20d2dbe9265…`, y el arnés **nunca** escribió el state (la única escritura de arranque es el
bootstrap del fixture, anterior a todo ciclo).

**AC-2 — entrega tardía sobre una feature cerrada.** Con la feature cerrada por la operación: el `receive`
**normal** **sigue fallando cerrado** (rc=2, la precondición de vigencia **no** se
relajó); `receive --late` → **rc=0** con **recibo durable** creado
(`True`) y `semantic_status: "pending"`; `late-delivery` → **rc=0**.
La feature **sigue `done`**, `active_feature: None`, `current_stage:
idle`: **no se reabre**. La traza **no** lleva `approved_by` (`None`)
y su `approval_effect` es `False`: **no aprueba nada**. La única diferencia del state es el
append de la traza.

**AC-3 — repetición tras una interrupción.** Repetir la invocación **idéntica**: rc=0, **sin** segunda
entrada y con el state **byte a byte idéntico** (`True`), y la salida **nombra la entrada
existente** (`True`). Una transición **distinta** (otro `--current-stage`) **añade** una
entrada (`True`). Una **estructuralmente excluyente** (disposición de un paquete
inexistente) falla cerrado con `state incoherent` (`True`) y **sin efectos**
(`True`). Conteo de entradas en los cuatro pasos: `[1, 1, 2, 2]`.

**AC-4 — el cierre rechaza nombrando y la disposición lo destraba (B1).** (a) Sin la aprobación vigente:
`closure` → **rc=2** con el marcador **`approval pending`**
(`True`) y el state **intacto** (`True`). (b) Con un
paquete **despachado y sin recibo** (el run que no volvió): `closure` → **rc=2**
con el marcador **`evidence missing`**, **nombrando el paquete** (`True`) y el state
**intacto** (`True`); el rechazo **ofrece las dos salidas legítimas** (recibir o disponer:
`True`) y **ya no ofrece `late-delivery`** (`False`), que es el
defecto que B1 señaló. (c) Registrada la **disposición** (`--resolution abandoned`): rc=0
y el `closure` **avanza** (rc=0), aplicando el cierre
(`True`), con la feature en `done`.

**Límites declarados.** (1) La mitad «árbol» de INV-7 (snapshot completo del árbol, más allá del state byte a
byte idéntico) no se asertó, como declararon los focales. (2) La consecuencia de D-12 (repetir una invocación
registrada con la fórmula **anterior** de la identidad anexa una entrada nueva en vez de ser no-op) no es
reproducible en un fixture nuevo y queda como deuda declarada. (3) Los desconocidos de §4 de la spec siguen
declarados: el número de invocaciones del recorrido completo se midió acá (8 para el ciclo
representativo, que es un fixture, no un ciclo real de producto). (4) El ciclo de AC-1 corre con el CLI **del
repo**: la operación todavía **no existe en la instalación** (deuda D-4, despliegue del dueño).

**Reproducir:** `python3 .cdad/local/005-012-t8-acceptance.py` (escribe
`.cdad/local/005-012-t8-evidence.json`). No toca este repo ni HOME; cada caso usa su propio proyecto
descartable.

**Gate de la feature (T8).** AC-1..AC-4 con evidencia propia; el **review-fix** de los dos bloqueantes de la
review formal está aplicado y verde (focales de B1 y B2). **No** se corrió la suite completa ni `make
validate`: los corre quien cierra (el orquestador Claude).
