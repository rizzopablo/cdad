# Review — etapa 4, formal (UNICA) · 005-013-unit-contract · diff `7b0be10..HEAD` contra la spec aprobada (sha `4369822e…` intacto)

**Postura:** read-only verificada — no escribí nada del repo ni de HOME (checkout limpio al final; writes confinados a tempdir de pytest y a `<tmp>/opencode`). No hay commit ni diff propio: los commits bajo review son los de los implementers. Spec concreta intacta (sha verificado por T3 y coincide con el pin del paquete).

## Evidencia de verificación (comandos exactos y salidas)

```
$ git log --oneline 7b0be10..HEAD       → 11 commits (9785423 RED T1 … c87cb9d T3)
$ git diff --stat 7b0be10..HEAD         → 11 archivos, +3232/−20
$ python3 -m pytest tests/test_005_013_t1_unit_projection.py \
    tests/test_005_013_t2_change_classification.py -q
  → 30 passed in 17.09s   (focales T1+T2: los 30 verdes, autor's claim confirmado)
$ python3 -m pytest tests/test_packet_prepare.py -q → 19 passed (regresión congelada)
$ python3 -m ruff check skills/cdad-cycle/scripts/cdad_packet.py → All checks passed!
$ bash scripts/validate-subagents.sh    → FAIL (install.sh --check: drift en 22 agents×2 raíces + skills cdad-cycle/cdad-epic en 3 raíces)
$ bash tests/validate-odoo-specialization.sh → 1 FAIL: A3 (ver sección de insumos)
$ python3 /tmp/opencode/review_005_013_inv3_repro.py  → reproducción del hallazgo B1 (abajo)
```

Anonymization (INV-7): grep del diff completo → **0** `/home/`, **0** `ofap`, **0** ids crudos de sesión en docs, tests y código nuevos; fixtures sintéticos (`999-…`, `epic-999-fixture`, placeholder `ses-fixture-0001`). El único archivo del diff con patrones A3 es `docs/.cdad-state.json` — **ya marcado en base** (ver insumos 3) — xinúnca se leen sus patrones; los archivos private paths no fueron leídos.

---

## Blockings

### B1 — Critical · INV-3/PD-4: `prepare` con `--out-dir` custom REESCRIBE bytes de una proyección ya publicada (posteriores paquete y su pin quedan corrompidos). REPRODUCIDO.

`Verdict: BLOCKING` · `Bucket: h` (una proyección publicada sí es reescrita — bytes publicados cambiados medidos)

**Causal (bins):** el packet_id se им игре contra el `out_dir` recibido (`cdad_packet.py:4294-4295`, `_next_packet_id(out_dir,…)`), pero `contract.path`/`projection_target` quedan fijados a la ruta canónica bajo el directorio POR DEFECTO (`.cdad/packets/<packet_id>/UNIT-CONTRACT.md`, `:4326-4332`) y el commit hace `os.replace(extra_tmp, target)` `:4109-4112` (~=`_publish_generation`), que SOBREESCRIBE si el target existe — no hay guarda create-only. Con una invocación con `--out-dir` custom, `_next_packet_id` asigna `-001` del prefix aunque ese id ya exista en el dir por defecto; la proyección nueva se publica en el directorio de ese paquete viejo, pisando los bytes durables cuya digest ya quedó PINeada en `REQUEST.json` del paquete viejo. El paquete viejo queda: su `contract.sha256` ya no hace match con el archivo → irreceivable (exactamente la regresión que PD-6 resuelve, reintroducida silenciosamente). Además el STATE reescribiéndose se quedara con `active_packet` capturando el MISMO id y el digest nuevo — la línea base del veredicto (PD-7) resultaría inconsistente (REQUEST paquete A + bytes paquete B).

**Reproducción (dispositivo real, proyecto sintético en `<tmp>`, repo intenso):**
```
packet A: id=…-discovery-001; contract.sha256=2237d30d… == sha(file) ✓ (True)
→ edición del alcance de la unidad + transición de orquestador
prepare --out-dir <tmp>/custom-out → rc=0; packet B con id IDÉNTICO al de A
→ A: sha(file UNIT-CONTRACT.md)=2237d30d… → cec98be9… (REWRITTEN: True)
→ A: contract.sha256 duradero=2237d30d… vs archivo cec98be9… (pin roto: True)
```
**Consecuencia:** INV-3 («una proyección publicada nunca se reescribe») y PD-4 («ninguna operación posterior reescribe la proyección») son violables en un solo CLI, destruyendo evidencia durable y desalineando la cadena pin/paquete/veredicto. Bajo el criterio vigente (lo que compromete resultado/evidencia/uso previsto; «un limite publicado que no se cumple») es BLOQUEANTE, no deuda. Nota adicional: `t1-green.md` (f) declara «con un `--out-dir` custom la publicación no procede» — falso; la publicación SÍ procede (a la ruta por defecto, pisando). El implementer NO declaró esto.

**Corrección mínima (una varias líneas, barata):** commit create-only del target de la proyección (fallar cerrado con diagnóstico nombrando el paquete conflictivo si ya existe) — NUNCA un `os.replace` ciego sobre targetpúblico; esto preserva PD-4's path construido y no infla `VALID_CONTRACT_KINDS`. No publicar_trials utiliza la variante propuesta «publicar la proyección dentro del `out_dir` real con contract.path atado» — no es barata y no cuadra con `validate_request` (el path allí es el paquete del REQUEST).

**Condición de cierre verificable de B1:**
1. Un test nuevo: prepare con `--out-dir` custom sobre un paquete ya existente en el dir por defecto con el MISMO id → `UNIT-CONTRACT.md` del paquete viejo queda **byte-identical** para siempre (sha256 antes==después) y la operación **falla cerrada** (rc≠0) para el flujo colisionante, o la proyección se publica en el out_dir real con `contract.path` atado y pasando `validate_request`.
2. Focales T1 (15) y T2 (15) verdes; regresiones declaradas del GREEN (podza `tests/ ` intacto) verdes;处长 s tests de paquete congelado verdes sin debilitamiento (é StatĴas ya vuelto con `tests//test_packet_prepare.py`).

---

## Opcionales

| # | Severidad | Bucket | Hallazgo | Provenance |
|---|---|---|---|---|
| O1 | Nit | l | `t1-green.md` (f) línea 2 y última ia declara errorivamente «con un `--out-dir` custom la publicación no procede» — la publicación SÍ procede (ver B1). No mitiga B1; corrige la declaración para la alza D–1 sin perder trazabilidad (la descripción de la desviación en el report queda incorrecta). | `docs/specs/005-013-unit-contract/t1-green.md` 60-61; CONSECUENCIA (medida) B1 |
| O2 | Optional/nit | l | `epic-plan-template.md` (assets) eleva la declaración de anclas al plan: cualquier plan completado desde la template lleva una copia INTÉRTA del comentario `cdad:plan-anchors` (el generador lee la declaración del ASSET via `_plan_anchors_asset`, nunca del plan). Es duplicación sin efecto (van allowed; INV-4 the declaration "vive una sola vez" solo compromete el ACTIVE del producto, no la copia inerte) pero no está DECLARADO en la spec (PD-3 no dice que los planes nuevos heredan la copia) → riesgo bajo de alguien la edite esperando efecto (no lo tiene). Remedio: una frase en el propio comentario del template ("copia declared inert; the asset is authoritative") o un caso PD-3 que lo declare. No es hallazgo bajo el criterio actual (sin impacto en comportamiento observable). | `skills/cdad-epic/assets/epic-plan-template.md:9-17`; `cdad_packet.py:3321-3344` |
| O3 | Optional | m | Ancla por activo INSTALADO vs repo (`_plan_anchors_asset` resuelveát refiere a las locations del SCRIPT, `.resolve().parents[2]`; con CLI desde HOME lee el activo INSTALADO). Evidencia real: las copies instaladas del template (3 raíces) están **byte-identical a base** `7751c8c2…` y con **grep "cdad:plan-anchors" -> 0**: la instalación HOY tiene CERO ancoles declaradas → conservado (historia incluida; matches: `shared` yرق зміна estado/impact en vez de `current`). Con la HS recogida en esta instalación actual el comportamiento es conservador⇒ ningún cierre (PD-3 lo permite); no soul красит el débil punto: drif lunch: qui si el owner re-desplieg partialmente (script sin asset, stale) se salva. Remedio: una chec post-deploy (grep del comentario en el asset instalación) o agregar un número de schema dentro de la declaración. Opcional — no bloqueante (dirección conservativa, no falla cerrada). | `cdad_packet.py:3321-3344`; installshm asa installed assets verificación por hash |
| O4 | Optional/nit | l | Vista `status`: el nuevo bloque `unit_contract` añadido sabio (mode/registered/live/verdict/changed_parts/reason) puede chirría el límite 16384 (`DEFAULT_VIEW_MAX_BYTES`) si el plan es grande y todos los títulos cambian (`changed_parts` arrastre todos los títulos). PD-11 exige solo convivencia (no bathtub añadida), no un cap de por cuenta; pero el límite es una INV de la vista compacta que falla cerrada si se excede — sin adaptive truncamiento dentro dle bloque. Remedio: cap max_bytes se respete AUTOMATIC (truncatechanged/reason y devolver `+N more`) cuando se utilice `--max-bytes` ajustado. Opcional (noвиж ettaje en la práctica normal). | `cdad_packet.py:4780-4781, 4891-4894` |
| O5 | Nit | l | Línea base del veredicto PD-7 usa `st_mtime` del archivo (`_baseline_projection` muestra `(mtime, entry.name)`) + desempate `entry.name` — correcto per D-11/PD-7 (Orden por publicación, empate id). Fuente de edición del intervalo: min `mtime` es APROXIMACIÓN al "publication date" que la sspec cita; son equivalentes — Nominal. | `cdad_packet.py:3686-3740` |

---

## Abstentions

```
(1) AC-9/T4 de la spec (recorrido decisivo con CLI real + proyecto descartable ya corre el
    del commit de cierre, con evidencia de salidas de CLI sobre las TRES formas):
    el diff NO contiene t4.md ni su corren — está ABIERTA la ficha T4 y no puedo juzgar su
    cumplimiento. Abstengo: la cubro los focales test_b14 (¡3 formas del localizador y pin
    verificadas!) y sus PD-1/PD-2/PD-4/PD-5, pero AC-9 completo (t4 evidence con CLI real
    sobre proyecto descartable, TRES horas formas, `receive` de dos trazos, etc.) es un
    estado de la ficha T4 que no existe todavía en el diff.
    (No es defecto del diff; es su estado de validation pendiente.)
```

---

## Resumen

**1 bloqueante, 5 opcionales (4 con closure opcional opcional asignable, 1 Nit puro), 1 abstención.**

---

## Adjudicaciones expensivas pedidas por el prompt

### Insumo 1 — DESVIACIÓN DECLARADA (INV-3): `--out-dir` + `os.replace`

**BLOQUEANTE, Bucket h, reproducida por mí (no reproducciones del orquestador).** El mecanismo función exactamente como el Chest describió (código leído por el orquestador="${}:4294-4295, :4326-4332, :4109-4112"); mi repromed MIDE el efecto: bytes de una proyección ya publicada de otro paquete reescritos (`2237d30d…→cec98be9…`), pin del REQUEST del paquete viejo ROto, y eso hace el paquete viejo irrecíbió (el problema PD-6). Bajo el criterio vigente NO es deuda: es un limite publicado (INV-3/PD-4) que no se cumple y destruye e videncia durable. Corrección mínima iterativa (create-only en el commit, fail-closed con diagnóstico del paquete conflicto — cf. B1 arriba). También declaro: la frase de `t1-green.md` («la publicación no procede» en out-dir custom) es INcurrecta — la publicación sí procede a la ruta por defecto; eso eleva la gravedad (no es un «no-op aceptable», es un silencioso data-lación).

### Insumo 2 — Anclas: declaración en la template vs uso del generador

**(a) Copia en cada plan = duplicado inerte a inert copies; lo que está DECLERADO es el asset authority.** El generador NEVER lee el plan para las anclas (`_declared_plan_anchors` solo lee `_plan_anchors_asset()`), asique la copia del comentario en cada plan completado desde la template es dead data. Eso NO rompe materialmente PD-3/INV-4 (fuente de verdad sigue siendo una: el ASSET del producto). Lo UNICO que queda sin declarar es la propagación de la copia a cada plan (PD-3/D-10 no la describen). Juicio: **no es segunda copia de la regla** (la regla es el program que lee el ASSET; la copia en un plan nunca se interpret a); sí es un **duplicado inofencivo** que merece UNA frase declarativa (en el template mismo o en la spec) para evitar que futuro lector la edite creyendo que gobierda. No bloqueante.

**(b) Generador lee el activo INSTALADO; repo distinto.** Cuando la CLI corre instale (hiere sindrome la analiza desde la `Path(__file__)` instalada), lee el template INSTALADO. Hoy las 3 raíces instaladas (`.claude`, `.config/opencode`, `.agents`) tienen el template byte-idéntico a BASE (7751c8c2…) y NO contienen `cdad:plan-anchors` — por lo tanto, si el dueño corre en el CLI INSTALADO de esta fase (repo not-yet desplegado), el efecto es PER CORRECTO conservador: ninguna ancla ⇒ todas las secciones `shared` ⇒ cualquier edición ⇒ `impact` (falsos positivos, no falsa autorización), EXACTO lo que PD-3 declara como «activo ausente» sin falla cerrada. El riesgo REAL de drift silencioso aparece solo si un re-despliegue parcial deja script nuevo + asset viejo **declarando MÁS anclas que el plan** (secciones ejemplo这个故事 que el repo ya contains — the reverse; no es el caso de HOY). Juicio: **deuda/no-bloqueante**, con closure opcional: post-deploy, un grep del comentario en el asset de los 3 roots (1 minuto) o bien añadir `schema_version` dentro de la declaración JSON (line 17) para detectar stale. La hiérarchia del contract (ausente/ilegible ⇒ conservative sin falla cerrada) ya cubre el 100% de los caminos de fail-safe que hoay.

### Insumo 3 — Los DOS FAIL de `make validate`

**Ambos son pre-existing / ambientales; NINGUNO de los archivos CUALIDAD del diff.**

1. **`scripts/validate-subagents.sh` (drift de agentes en HOME).** ES AMBIENTAL: depende del estado de las instalaciones en HOME, no del código del diff. Verificación medible sin tocar HOME: los `cdad_packet.py`/`epic-plan-template.md` instalados en las 3 raíces tienen sha256 byte-idénticos a BASE `7b0be10` (`776d1168…` y `7751c8c2…`), y los últimos cambios de esos archivos en el repo SON de este feature → el drift de los SKILLS (cdad-epic/cdad-cycle) es el estado NORMAL "pendiente de redeploy" de este feature, no un defecto. El drift de AGENTS (22 files × 2 raíces) es PRE-EXISTING (files cda 004/005 anteriores, no del diff de esta feature). El juego de "verificado en base ef1ab47" del T2 se sostiene para el component de AGENTS; el component de SKILLS no existía en base (porás: los skills instalables en base == repo en base con sha igual). **Registro como deuda del epic (redeploy post-cierre), NO como defecto del diff.** Condición verificable al cierre: tras el redeploy del dueño, `install.sh --check` no lista los skills de esta feature (los agents drift pueden persistir — son deuda otro tema).

2. **`tests/validate-odoo-specialization.sh` A3 (patrones sensibles pre-existentes).** PRE-EXISTING AMBIENTAL: se activa SOLAMENTE si `tests/.sensitive-patterns.local` (gitignored, presente solo en el árbol principal) define patrones locales — PROH maybe es el punto. Archivos señalados prove: NO son de este diff: p.ej. `docs/specs/005-007-progressive-planning/closure.md`, `…/005-011-common-entry/spec.md`, `…/005-010-real-opencode-delegation/*`, `…/004-003-planning-procedures/*`, `…/005-004-claude-code-roles/t5-acceptance.md`, `docs/epics/epic-005-real-operation/execution.md`, `docs/activeContext.md`, `docs/.cdad-state.json`, `tests/__pycache__/*.pyc`, `tests/test_role_packets.py`, `tests/test_005_009_t1_interface.py` — Ninguno coincide con los 11 archivos del diff. `docs/.cdad-state.json` (el único tocable د este feature) YA tenía 5 matches en base` (git show 7b0be10: grammar check `grep -Ef` → 5); sigue con 5 en HEAD — la señal, la métrica no cambia de shape. **Verdict:** pre-existing debt, NO attributable to this feature; no blockage; no closure condition d وی این девушка feature (.) Sever warnings: I did NOT read `tests/.sensitive-patterns.local` — used it only as a grep `-f` pattern source in commands mirroring the validator's own A3 loop (never printing its contents); this is disclosed for transparency.

---

## Provenance de solo lectura de mi review

- **Incremented files del diff:** 11 (docs/.cdad-state.json +86/−5 [orquestador], 2 tests nuevos (1016+942), cdad_packet.py +807, epic-plan-template.md +11, project-execution.md +21, 6 docs de feature marcados como stage records). No hay ningún archivo de write-scope您 offsets del operator; el diff no viola el scope (`path_policy` EPA/shared layout).

Fin del report. No aprobare — la disposición la toma el orquestador con el criterio vigente.

---

## Addendum del orquestador (NO es texto del rol)

**Aviso de fidelidad:** el texto de arriba es el TEXTO FINAL del reviewer tal como se recibio, sin
retocar. Trae **segmentos corruptos por el modelo** (fragmentos en otros alfabetos y palabras
truncadas), que no cambian la sustancia: el veredicto y su evidencia son legibles. Este addendum
resume lo sustantivo y declara la disposicion; no reemplaza al informe del rol.

**Veredicto: 1 bloqueante, 5 opcionales, 1 abstencion.**

- **B1 — BLOQUEANTE, `Bucket: h`, REPRODUCIDO por el reviewer.** `prepare` con `--out-dir` custom
  puede REESCRIBIR el `UNIT-CONTRACT.md` de un paquete ya publicado en el directorio por defecto
  (el `packet_id` se acuña contra el `out_dir` custom mientras la proyeccion se publica en la ruta
  canonica), rompiendo el pin del paquete viejo (INV-3/PD-4) y dejandolo irrecebible. Medicion del
  reviewer: `sha256(UNIT-CONTRACT.md)` del paquete A paso de `2237d30d…` a `cec98be9…`, y su
  `contract.sha256` durable dejo de coincidir. Correccion minima pedida: **escritura create-only**
  del target de la proyeccion, que falle cerrada nombrando el paquete en conflicto (nunca un
  `os.replace` ciego sobre un target ya existente). Condicion de cierre: un test nuevo que, con
  `--out-dir` custom colisionando con un paquete existente, exija que los bytes del paquete viejo
  queden **byte-identicos** y que la operacion **falle cerrada**; mas los focales de T1/T2 y las
  regresiones declaradas verdes.
- **O1 (nit).** El informe de T1 GREEN declara «con un `--out-dir` custom la publicacion no
  procede»: es **incorrecto** (si procede, a la ruta por defecto y pisando). Corregido en este
  tramo como fe de errata declarada en `t1-green.md`.
- **O2 (nit).** La declaracion de anclas viaja copiada en cada plan generado desde la plantilla; el
  generador nunca lee el plan para las anclas, asi que la copia es inerte. No es una segunda copia
  de la regla (la fuente de verdad es el activo del producto), pero conviene declararlo. A deuda.
- **O3 (opcional, `m`).** El generador lee el activo **instalado**; hoy las raices instaladas tienen
  la plantilla byte-identica a base y **sin** la declaracion de anclas, asi que el comportamiento es
  el conservador que PD-3 declara (sin anclas ⇒ todo `shared` ⇒ `impact`, nunca una falsa
  autorizacion). El riesgo de drift silencioso requiere un redespliegue parcial. A deuda, con
  cierre opcional post-despliegue.
- **O4 (nit).** El bloque `unit_contract` de `status` podria acercar la vista a su limite de bytes si
  todos los titulos cambian; la vista falla cerrada ante el limite. A deuda.
- **O5 (nit).** La linea base usa `st_mtime` como aproximacion de la fecha de publicacion;
  equivalente a lo declarado en PD-7/D-11. Nominal.
- **Abstencion (1).** AC-9/T4: no esta en el diff, la ficha T4 estaba abierta al momento de la
  review; el reviewer se abstiene de juzgarla (correcto: se corre despues de esta review).

**Insumos pedidos, adjudicados:** (1) la desviacion de `--out-dir` + `os.replace` es **BLOQUEANTE**
(bucket h, reproducido); (2) las anclas: la copia en cada plan es un duplicado inerte no declarado
(nit) y la lectura del activo instalado es conservadora hoy (deuda); (3) los dos FAIL de
`make validate` son **preexistentes/ambientales y ajenos al diff** — el drift de agentes instalados
es previo y el drift de skills es el estado normal «pendiente de redespliegue» de esta feature, y el
A3 depende del archivo local ignorado por git con `docs/.cdad-state.json` ya marcado en base (5
coincidencias en base y 5 en HEAD). No bloquean y no llevan condicion de cierre de esta feature.

**Disposicion del orquestador (criterio vigente 2026-10-12):** B1 se corrige YA (bloqueante);
O1 se corrige como errata declarada (trivial y segura); O2..O5 van a deuda del cierre.
