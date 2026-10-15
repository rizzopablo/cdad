> Plan **DRAFT (etapa 2, subetapa `draft`) — SIN APROBAR. Cuarta corrección del draft.** Texto del
> **architect** (`mofgw/deepseek-v4.1-flash`), como **enmienda del contrato aprobado** pedida por el
> **orquestador Claude** (hallazgo **B3**, bloqueante para el uso previsto, sobre el **predicado de vigencia**
> del control de exclusión de PD-14). **Esta entrega REEMPLAZA el plan aprobado por el orquestador OpenCode**
> el **2026-10-14** (el draft-003, sha256 `fb270b70…`, con su spec `56d0be4b…`): esa aprobación queda
> **sustituida y no vigente** hasta la **reaprobación** de esta versión **junto con la spec corregida** (una
> sola acción), por el orquestador OpenCode bajo la HITL delegada del epic-005
> (`docs/epics/epic-005-real-operation/execution.md:8-23`) o por el **dueño**; el architect **no** aprueba su
> propia propuesta (anti-sesgo). Contrato: `docs/epics/epic-005-real-operation/plan.md`, **fila 12** (`:45`),
> sha256 `63dda3b83561a8763a6b3ab9613f2b26029796921cdede4dfd65e7ab3ad059a6`, más «Ajuste de los ciclos
> pendientes» (`:48-88`). Deriva de
> `docs/specs/005-012-transition-registration/discovery.md` (§1-§19) y de la spec de esta feature
> (`docs/specs/005-012-transition-registration/spec.md`, corregida), ambas resueltas **por referencia**.
> El bloque canónico de §4 queda **intacto** (mismo reparto y mismo orden, T1..T8) y se **revalidó** con las
> funciones del propio CLI en solo lectura; los cambios de esta versión son las fichas y la trazabilidad
> declaradas en §1/§2/§5. **Sin valores de este VPS; sin rutas absolutas del dueño ni ids crudos de sesión**
> (`<home>`, `<repo>`, `<tmp>`, `<ses-…>`, `<exec-id>`).

# Plan — 005-012-transition-registration

## 1. Ficha de la feature

- **Feature ID:** `005-012-transition-registration` · **Epic:** `epic-005-real-operation` ·
  **Estado:** DRAFT (etapa 2, **cuarta corrección del draft**: B3; la aprobación del draft-003
  —`fb270b70…`— queda **sustituida y no vigente**).
- **Resultado buscado (fila 12, `plan.md:45`):** una **operación del CLI** que registra una **decisión
  explícita del orquestador** sobre una transición —recepción de una entrega, aprobación de un gate,
  avance de etapa, cierre de feature y **disposición de un despacho sin recibo**—, **comprueba sus
  requisitos** y la aplica **sin edición manual del state**; (a) exige la **evidencia referenciada** y que
  el gate lo apruebe quien tiene la **autoridad vigente**; (b) **recibir nunca aprueba**; (c) repetirla
  **no duplica efectos**; (d) **automatiza la contabilidad y conserva el juicio**. Cubre **D-3 de 005-007**
  (simetría con `open-unit`).
- **Corrección de esta versión (B3):** el **predicado de vigencia** del control de exclusión de **PD-14** pasa a
  ser el que el cierre ya usaba en **PD-8(b)** —la entrada debe **nombrar los bytes actuales**—, así que una
  aprobación `specification` cuyo pin **ya no nombra** los bytes actuales **no compite**: la **reaprobación tras
  una enmienda** registra **sin `--supersedes`**, aunque la entrada vieja sea **keyless**; `--supersedes` queda
  para reaprobar los **mismos** bytes (como hoy); el caso raro de los mismos bytes desde una entrada vigente
  **sin clave** va a **deuda D-16** (**declarada como límite**, sin inventar mecanismo). Toca **PD-14** y
  **D-8** (spec §0.1/§2.3/§5/§6/§7); **T5** gana el caso de evidencia y **§5** de este plan la línea de
  trazabilidad; el **bloque canónico no cambia**. Trazabilidad completa en la spec §0.1.
- **Corrección anterior, conservada (draft-003, aprobada y ahora sustituida):** (B2) la **identidad de la
  transición** (PD-10) incluye los
  **insumos con efecto** —la postcondición resuelta con su `outcome`, el `current_stage` declarado, los
  `artifacts` citados y los campos propios de cada clase—, con su **payload canónico** escrito en la entrada
  (`transition_key_payload`), para que dos invocaciones distintas (p. ej. N `delivery` del mismo paquete con
  la misma `--stage`) **no** se traguen como no-op (PD-12; **deuda D-12** por las entradas ya registradas,
  sin migración del state); (O1) el caso del cierre pasa a «aprobación **faltante** o pin que **ya no
  nombra** los bytes»; (O2) `--stage` es obligatoria **salvo `disposition` y `late-delivery`**; (O3) la
  operación se declara en una **sección nueva contigua a las operativas §5-§8** (no en una «tabla»); (O4)
  PD-6 declara el **mecanismo** de la vigencia por fecha (vocabulario D4) y que la forma por eventos conserva
  su dueño. Trazabilidad completa en spec §0.2.
- **Corrección anterior, conservada (draft-002, aprobada y sustituida):** (B1) la clase **`disposition`**
  resuelve el despacho que **nunca vuelve** con la feature **abierta** (PD-21; el cierre la acepta y la
  ofrece, PD-8(a); AC-4 suma el caso); (P1) los **digests los deriva el CLI** y afirmarlos es opcional
  (PD-20; AC-1 corre sin digests); (P2) la autoridad del gate tiene **tres casos** —delegación vigente /
  **sin delegación** (el dueño no se bloquea) / sin epic— (PD-6).
- **Requisitos de la review de Codex (dirección del encargo, `execution.md:83-88`):** el **cierre**
  comprueba las **entregas requeridas** y sus **aprobaciones** antes de aplicar; hay una **salida
  explícita** (dos, tras B1: recepción tardía de una entrega que existe y disposición de un despacho que
  no vuelve) sin reabrir ni aprobar una feature cerrada; registrar una transición **no aprueba** un gate al
  recibir y **no duplica** efectos.
- **Criterio del dueño:** cada avance debe **reducir trabajo operativo**, sin compensarlo con más
  controles frágiles ni mantenimiento documental. **Sin tests que decidan el significado de un párrafo
  por listas de palabras** (el sentido lo juzga la review). **Fuente única:** la spec **no** agrega una
  segunda copia de una regla existente; toda extensión es **aditiva y declarada**.
- **Contrato y reglas reusadas:** spec §8. **Dependencia del epic:** `005-011` (cerrada y desplegada).
- **Fronteras de contrato (no reescritura):** 005-001 (aprobación pineada D3/PD-18 y marcadores PD-12:
  **extendidas** de forma aditiva y declarada), 005-003 (vista/`entry`), 005-007 (`open-unit`),
  005-013 (tabla de consecuencias: **nombrada**, no implementada), 003-002/003-004/003-007 (recibos y
  continuidad, **referenciadas**).
- **Baseline:** el CLI **instalado** es `7212ead` (sha256 `776d1168…`) y **no** contiene la operación
  nueva; el diseño es sobre **HEAD**. El despliegue es **deuda D-4** (§7 de la spec).
- **Convención de anonimización:** `<home>`, `<repo>`, `<tmp>`, `<ses-…>`, `<exec-id>`; fixture
  sintético y anónimo.

## 2. Ajuste de las unidades del discovery a tareas atómicas

Una tarea por **clase de producto y oráculo**; un **RED** cubre una clase y su **GREEN** va en **otra
sesión**, sin mezclar roles. El discovery (§16) propuso U1..U7; se reagrupan así:

| Unidad del discovery | Tarea | Por qué se agrupa así |
|---|---|---|
| **U1** (superficie + escritura única + forma del state) | **T1** | Clase **código del CLI + oráculo de test focal**: la superficie, la clave de identidad, la **derivación de digests** (PD-20) y **la forma mínima usable** —la transición `delivery` **y** `advance`— comparten un solo producto (el registro) y no se pueden rechazar por separado. Incluye el invariante «recibir no aprueba» (fila 12(b)). **La forma mínima (`delivery` y `advance`) queda usable en T1** (criterio de orden de la review del orquestador). |
| U1 (resto de clases) | **T2** | Clase **código del CLI** con oráculo propio (autoridad vigente + pin verificado): `gate`, con los **tres casos de autoridad** (P2/PD-6). Mismo archivo que T1 → **serializada**. |
| **U5** (vigencia) | **T5** | Clase **código del CLI** con oráculo propio (lector aditivo + exigencia de `supersedes`): es un predicado distinto sobre entradas de otro tipo. Mismo archivo → serializada; **va antes de T3** porque la comprobación del cierre consume la vigencia. |
| **U2 + U3** (idempotencia + comprobación del cierre) | **T3** | Clase **código del CLI** con oráculo de cierre (comprobación antes de aplicar) **más la clase `disposition`** (B1/PD-21), que es la **salida** que el cierre ofrece y consume: el despacho sin recibo, el rechazo que lo nombra, la disposición y el cierre que avanza son **un mismo oráculo** (AC-4) y no se rechazan por separado. Consume la vigencia de T5. |
| **U4** (entrega tardía) | **T4** | Clase **código de dos módulos** (`cdad_result.py` + `cdad_packet.py`) con oráculo end-to-end: el modo `--late` del recibo y la traza no se rechazan por separado (rechazar uno deja la salida inservible). Es la **entrega que existe y llega tarde**, distinta de la disposición. |
| Deuda de 005-013 (ejecución huérfana) | **T6** | Clase **código del CLI** con oráculo propio (rechazo de `prepare --new-execution`): cierre mecánico y acotado pedido a esta unidad. Mismo archivo → serializada. |
| **U6** (documentación por referencia) | **T7** | Clase **documental** (dos referencias); su oráculo son **comprobaciones observables** + la review del texto. `files: []` (convención de 005-011 T2 / 005-007 T6). |
| **U7** (aceptación) | **T8** | **Gate** (no RED/GREEN de producto): `observable_checks` + gate de integración; requiere T1..T7. |

**Qué NO se planifica** (fuera de alcance, spec §6): RD-a/RD-b; la tabla de consecuencias de 005-013; el
staging del buzón y el descriptor `RESULT.json` (deuda D-10 de 005-004); el veredicto fino de
`reconcile` a nivel de ejecución (deuda D-1); el inventario de campos derivados sin dueño (deuda D-2);
los **despachos sin recibo de ejecuciones cerradas** (deuda D-11); la autoridad sin delegación a nivel de
**estado** (deuda D-10); CI, sandbox, plataforma de jobs, paralelismo, HOME, push y despliegue; **no** se
reabren 005-003/005-* ni 003-*.

**Nota de paralelismo.** T1, T2, T3, T4, T5 y T6 editan el **mismo archivo**
(`skills/cdad-cycle/scripts/cdad_packet.py`) → **no** se declaran paralelas (`parallel: []`, con
`depends_on` explícito), consistente con el validador del producto. T7 es documental y T8 es gate.

**Deuda de esta corrección (draft-003).** Se agregan a la spec §7, con condición de cierre: **deuda D-12**
(las entradas ya registradas con la fórmula anterior de la clave dejan de reconocerse como no-op candidato;
consecuencia declarada de B2, **sin** migración del state) y **deuda D-13/D-14/D-15** (los opcionales **O5**
—`tdd_substage` no se puede limpiar y el vocabulario del protocolo no está en `VALID_SUBSTAGES`—, **O6** —
PD-12(i) sin guard ni test propio— y **O7** —nits de cobertura declarada, salvo el no-op independiente de la
cabeza, que lo cubre el RED de B2—). **O1..O4 no son deuda**: se corrigieron en el contrato (spec §0.2 y las
fichas T3/T7 de este plan).

**Deuda de esta corrección (draft-004).** Se agrega a la spec §7, con condición de cierre, la **deuda D-16**
(reaprobar los **mismos** bytes desde una aprobación vigente **sin `transition_key`**: la entrada compite y
`--supersedes` no puede citarla, así que la segunda aprobación de bytes idénticos no tiene salida; **no** se le
inventa un mecanismo). **B3 no es deuda**: se corrige en el contrato —el predicado de vigencia de **PD-14**
(el pin que **ya no nombra** los bytes actuales no compite) y el texto de **D-8**—, y su caso de comportamiento
(**reaprobación sin `--supersedes`**) es **RED primero** en el focal de **T5**.

**Deuda retirada por esta corrección.** La fila **D-9** de la spec §7 («un despacho que el orquestador
considere anulado también exige resolución») **deja de ser deuda**: la **disposición** (PD-21/D-13) es su
salida, con la feature **abierta**. Se agregan **D-10** (la vigencia del **estado** sigue exigiendo
delegación con epic activo; el límite se declara) y **D-11** (despachos sin recibo de ejecuciones
cerradas).

## 3. Estrategia de validación (declarada una vez)

- **Dos niveles.** **Siempre:** procedencia, `git diff` contra el alcance del paquete, alcance declarado
  y **pruebas focales** (segundos). **Sólo con un motivo concreto:** la suite o la integración. Se
  **reutiliza evidencia equivalente** con procedencia verificada **por referencia** a
  `skills/cdad-cycle/references/re-entry.md` (*Equivalence of a registered run*, `:67-79`).
- **Suite completa una vez, al cierre** (motivo: toca el CLI del state, un módulo de recibos y el
  texto de orientación; cierra la feature). No se corre dentro de cada tarea; **no se corre salvo que el
  paquete lo pida** (la corre quien cierra).
- **Comandos concretos por encargo** (fichas de §4), **tomados del bloque canónico** de §4 y rendidos en
  el paquete (mecanismo de 005-003 T6). RED: el focal debe fallar por **aserción** (no por
  import/sintaxis; precedente declarado en `tests/test_005_007_t3_open_unit.py:20-41`). GREEN: focal
  verde + regresiones del área.
- **El sentido de los textos lo juzga la review** (T7): se valida con **comprobaciones observables**
  (estructura + referencias presentes) y con la review; **no** con tests que decidan el significado de un
  párrafo por listas de palabras.
- **La identidad se prueba por su efecto observable** (B2/PD-10): dos invocaciones que difieren en un
  insumo con efecto (otra `--postcondition` del mismo paquete con la misma `--stage`; otro
  `--current-stage`) son **dos** entradas y ambas dejan su resultado escrito; la repetición **idéntica** es
  una sola entrada con el state **byte-idéntico**, también **después de appends posteriores**. No se aserta
  el digest ni se lee la implementación: el oráculo es el conteo de entradas y los campos escritos.
- **Los tests son caja negra sobre el CLI real:** subprocess, sin importar el módulo y sin leer la
  implementación (patrón de `tests/test_005_003_t1_compact_view.py` y
  `tests/test_005_007_t3_open_unit.py`). Proyecto **descartable** en `<tmp>`, `HOME` del subproceso en
  un tempdir **vacío**. **Nunca el repo real, nunca HOME.**
- **Los digests se prueban en su forma derivada** (P1/PD-20): el focal de T1 comprueba que **sin**
  afirmar ningún digest el CLI lo **deriva**, lo **escribe** en la entrada y lo **imprime**; y que un
  digest **afirmado** divergente falla cerrado. No se asertan **porcentajes ni conteos del state vivo**
  (PD-17 se verifica con `validate-state` rc=0 antes y después).
- **El cierre incluye el commit** y el reporte del rol lo declara; un rol que termina sin commitear es
  **bloqueo declarado**.
- **Sin `--no-verify`; sin push; sin desplegar; sin tocar HOME; sin leer
  `tests/.sensitive-patterns.local`.**

## 4. Fichas mínimas de tarea y bloque canónico

### T1 — Superficie `register-transition` + clave de identidad + digests derivados + forma mínima (`delivery` y `advance`)
- **Resultado observable / PD cubiertas:** PD-1, PD-2, PD-3, PD-4, PD-7, PD-10, PD-11, PD-12, PD-17,
  PD-18, PD-20; INV-1, INV-2, INV-3, INV-6, INV-7.
- **Alcance incluido:** declarar el subcomando en `build_parser` (`cdad_packet.py:4927-5010`) y
  despacharlo en `main` (`:5134-5233`); implementar la **forma aditiva** del registro (§2.2 de la spec:
  las claves existentes + `transition`, `transition_key`, `supersedes`, `approval_effect` y, cuando la
  clase lo use, `resolution`/`replaced_by`) con el **escritor único** (`_ProjectLock` +
  `_publish_owned_atomically`, y `_publish_generation` cuando la transición toca la generación del
  paquete); el **marcador nuevo `evidence missing`** para la evidencia ausente/divergente; el
  **resolvedor de digests derivados** (PD-20: si el digest se omite, se calcula sobre los bytes actuales,
  se escribe y se imprime; si se afirma, se verifica y una diferencia falla cerrado; la forma de
  `--artifact` es `<path>[=<sha256>]`); la clase `delivery` (efecto `active_packet.status: "completed"` +
  `postconditions_status`/`tdd_substage` si se declaran) **y la clase `advance`** (vocabulario operativo
  cerrado); la **clave de identidad** `transition_key` **con su payload canónico** (PD-10: la tupla más los
  insumos con efecto —postcondición resuelta, `current_stage`, `artifacts` y los campos propios de cada
  clase—, con la normalización declarada y escrito en la entrada como `transition_key_payload`) y el
  comportamiento de repetición (idéntica = no-op byte-idéntico; distinta = nueva entrada; estructuralmente
  excluyente = `state incoherent`); la
  **contra-prueba de que `delivery` nunca aprueba**. **La forma mínima (`delivery` y `advance`) queda
  usable al terminar T1.** **Excluido:** `gate` (T2), `closure` y `disposition` (T3), `late-delivery`
  (T4), la vigencia estructural (T5), el rechazo del contexto abierto (T6); **no** tocar `prepare`
  (conserva su rol), ni el lock/publicación existentes, ni `receive`/`materialize`.
- **Consume:** — . **Produce:** `transition-registration` (`transition-registration-v1`).
- **Dependencias:** — .
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`; *Test*
  `tests/test_005_012_t1_register_transition_base.py`.
- **Contexto por rol:** RED — spec §2.1-§2.4 (PD-1..PD-4, PD-7, PD-10..PD-12, PD-17, PD-18, PD-20),
  `discovery.md` §1-§2, §5; GREEN — ídem + `cdad_packet.py:1257-1380,2235-2266,2401-2483,4485-4551`
  (lock, serialización, publicación, registro de despacho, `open-unit` como precedente exacto). El
  test-writer **no** ve la implementación (oráculo desde el contrato).
- **Evidencia al re-entry:** focal rojo→verde sobre proyecto descartable: reposo/ejecución activa con un
  paquete `dispatched` + recibo real (`prepare` → `--record-dispatch` → `receive`); una invocación
  `delivery` **sin afirmar ningún digest** deja `active_packet.status: "completed"`, el `receipt_sha256`
  **derivado** en la entrada y en la salida, y `validate-state` verde; un `--receipt <sha256>` **afirmado**
  divergente → rc=2 `evidence missing` nombrando el paquete, con el state **byte-idéntico**; un `advance`
  mueve `current_stage`/`tdd_substage` y rechaza un valor fuera del vocabulario; repetir la invocación
  idéntica → rc=0 y **una sola** entrada (también **después de appends posteriores**); **dos `delivery` del
  mismo paquete con la misma `--stage` y `--postcondition` distinta → dos entradas** (cada resultado escrito
  en `postconditions_status`), y **dos `advance` con la misma etiqueta y `--current-stage` distinto → dos
  entradas** (B2/PD-10); la entrada de `delivery` no lleva `approved_by`; `git diff`
  acotado (sin tocar `prepare`).
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_012_t1_register_transition_base.py -q`;
  regresiones `tests/test_005_007_t3_open_unit.py`, `tests/test_005_003_t1_compact_view.py`,
  `tests/test_005_003_f2_idle_history.py`, `tests/test_packet_prepare.py`,
  `tests/test_004_002_t2_bootstrap.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si el subcomando exigiera **relajar** una validación existente de
  `prepare` o compartir su serialización por otra vía, **detener** (INV-1); si el no-op de la repetición
  exigiera reescribir una entrada existente, **detener** (INV-3: append-only); si la derivación de
  digests exigiera escribir el archivo citado o tocar el state más allá de la entrada, **detener**
  (PD-20: sólo lee y escribe la entrada).

### T2 — `gate` (pin verificado con digests derivados + autoridad vigente en tres casos)
- **Resultado observable / PD cubiertas:** PD-5, PD-6 (tres casos, P2).
- **Alcance incluido:** la clase `gate` (`approved_by` no vacío; `contract_path`/`contract_sha256` y
  `plan_path`/`plan_sha256` **verificados contra los bytes** antes de escribir, con el **digest derivado**
  cuando no se afirma —PD-20— y el mismo control que `_contract_approval_for` hace al leer); y la
  **autoridad** con los **tres casos** de PD-6: con `hitl_delegation` presente se verifica su **vigencia**
  (no revocada/vencida y resoluble: el control de `_validate_v2_vigency`, sin re-declararlo) y una
  delegación revocada/vencida **falla cerrado** (`approval pending`); **sin** delegación se **registra el
  aprobador declarado** (`--approve-by`) y la salida **declara que no hubo delegación que verificar** (no
  se bloquea al dueño, D-6); con `active_epic: null`, igual. **Excluido:** la vigencia estructural
  `supersedes` (T5); el `closure` (T3); parsear la prosa de un plan o de una spec (INV-5); imponer una
  tabla de progresión de etapas más allá del vocabulario; **cambiar** `_validate_v2_vigency` (se consume,
  no se re-declara).
- **Consume:** `transition-registration` (`transition-registration-v1`) de T1. **Produce:**
  `stage-gate-registration` (`stage-gate-registration-v1`).
- **Dependencias:** T1.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`; *Test*
  `tests/test_005_012_t2_gate_authority.py`.
- **Contexto por rol:** RED — spec §2.1-§2.3 (PD-5, PD-6, PD-20), `005-001/spec.md:58-73,99` (registro de
  aprobación y marcadores), `discovery.md` §7; GREEN — ídem + `cdad_packet.py:1381-1486,1558-1624`
  (aprobación pineada y vigencia).
- **Evidencia al re-entry:** focal rojo→verde: `gate --stage specification` con pin correcto **derivado
  de los bytes** (rc=0) y con un `--contract-sha256` **afirmado** divergente (rc=2 `evidence missing`);
  con delegación **revocada** → rc=2 `approval pending`; **sin** delegación registrada → rc=0, con el
  aprobador declarado en la entrada y la salida declarando que **no hubo delegación que verificar**; `git
  diff` acotado.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_012_t2_gate_authority.py -q`; regresiones
  `tests/test_005_001_t1_role_approval.py`, `tests/test_005_001_t4_decisive.py`,
  `tests/test_005_007_t3_open_unit.py`, `tests/test_packet_prepare.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si verificar la autoridad exigiera cambiar `_validate_v2_vigency`,
  **detener** (se **consume**, no se re-declara: INV-4); si el `gate` necesitara una tabla de progresión
  semántica, **detener** (INV-5); si el caso «sin delegación» exigiera **relajar** la vigencia del estado
  (no sólo la de la operación), **detener** y declararlo como deuda D-10 (no se cambia 005-001).

### T5 — Vigencia estructural de la aprobación (`supersedes` + lector aditivo)
- **Resultado observable / PD cubiertas:** PD-14, PD-15.
- **Alcance incluido:** al registrar un `gate` de `--stage specification` para un
  `(feature, contract_path)` **compite** sólo la entrada **vigente** en el sentido de **PD-14 (B3)**: la que su
  **pin nombra los bytes actuales** —la entrada cuyo pin **ya no nombra** los bytes actuales **no compite**
  (y ya no habilita: el lector exige el pin), así que la **reaprobación tras una enmienda** registra
  **sin `--supersedes`**, tenga o no clave la entrada vieja, y la nueva queda como la **única** que habilita—;
  cuando **sí** compite una vigente: sin `--supersedes` → rc=2 `state
  incoherent` nombrando la entrada vigente; con `--supersedes <transition_key>` que nombre una entrada
  existente de la misma feature y el mismo `contract_path` → rc=0 (**el caso raro: reaprobar los MISMOS
  bytes**; la forma del campo no cambia). **Lector aditivo:** el filtro
  «vigente» se aplica donde ya se seleccionan las entradas `specification`
  (`_approved_spec_entries`/`_contract_approval_for`, `cdad_packet.py:1398-1486`), **sin** tocar la
  regla del pin (D3/PD-18) ni los tres marcadores existentes. **Excluido:** reescribir una entrada
  histórica (append-only, INV-3); decidir la vigencia por `note` o por prosa (prohibido, D-8/PD-15);
  migrar/limpiar entradas históricas; el caso raro de los **mismos** bytes desde una entrada vigente **sin
  clave** (**deuda D-16**: no hay clave que citar y **no** se inventa un mecanismo).
- **Consume:** `stage-gate-registration` (`stage-gate-registration-v1`) de T2. **Produce:**
  `approval-vigency` (`approval-vigency-v1`).
- **Dependencias:** T1, T2.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`; *Test*
  `tests/test_005_012_t5_approval_vigency.py`.
- **Contexto por rol:** RED — spec §2.3 (PD-14/PD-15), §5 D-8, `005-001/spec.md:58-65,130` (D3/PD-18:
  la regla que se **extiende**), `discovery.md` §4.3; GREEN — ídem + `cdad_packet.py:1398-1486`.
- **Evidencia al re-entry:** focal rojo→verde: dos entradas `specification` para el mismo
  `(feature, contract_path)` **sin** `supersedes` → **ambas** habilitan (comportamiento de hoy,
  declarado); la segunda **con** `supersedes` que nombra la primera → rc=0 y `prepare --role test-writer`
  sólo se habilita por la nueva; registro de una segunda vigente **sin** `supersedes` → rc=2
  `state incoherent`; un `note` en prosa que dice «reemplaza» **no** cambia qué entrada habilita (control
  negativo); **el caso B3:** con una aprobación previa **sin `transition_key`** cuyo pin **ya no nombra** los
  bytes actuales (el caso real de esta feature) → el `gate` de etapa 2 registra **rc=0 sin `--supersedes`** y
  `prepare --role test-writer` se habilita por la **nueva** entrada; el límite de los **mismos** bytes con una
  entrada vigente **sin clave** se declara (**deuda D-16**), sin test propio; `git diff` acotado.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_012_t5_approval_vigency.py -q`;
  regresiones `tests/test_005_001_t1_role_approval.py`, `tests/test_005_001_tcorr.py`,
  `tests/test_005_005_t1_replace_conserved.py`, `tests/test_packet_prepare.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si el predicado «vigente» obligara a **re-declarar** la regla del pin o
  a exigir un campo a entradas históricas, **detener** (INV-3/INV-4).

### T3 — `closure` (comprobación antes de aplicar) + `disposition` (la salida del despacho sin recibo)
- **Resultado observable / PD cubiertas:** PD-8, PD-9, PD-21 (B1); PD-12(iv).
- **Alcance incluido:** (i) la clase `disposition` (B1/PD-21): `--transition disposition --packet <id>
  --resolution <abandoned|superseded>` —con `--replaced-by <packet-id>` obligatorio para `superseded`—
  que comprueba **antes de escribir** que el paquete pertenece a la ejecución activa, está `dispatched`,
  **no** tiene recibo durable y la feature está **abierta**; escribe **sólo** la entrada de traza
  (`resolution`, `replaced_by`, `approval_effect: false`, `transition_key`), **sin** `approved_by` y
  **sin** tocar `active_packet`/`epic_features`/`closed_at` (**no** fabrica un `completed`), y es
  **idempotente por `transition_key`** (repetir = no-op); sus incumplimientos → rc=2 `state incoherent`
  nombrando el hecho, state byte-idéntico. (ii) la clase `closure` con las dos comprobaciones **previas a
  cualquier escritura** (a: toda entrega requerida —paquete de la ejecución activa con registro de
  despacho— tiene **recibo durable o disposición**, mismo predicado que `_packet_has_receipt`,
  `cdad_packet.py:4698-4702`; b: existe una entrada `specification` cuyo pin **nombra** el contrato
  actual con su **digest derivado** y es **vigente**); el rechazo que **nombra** la entrega o la
  aprobación faltante, con su marcador (`evidence missing` / `approval pending`) y la **oferta de las dos
  salidas** (recibir por el camino normal; o `disposition`, con la feature abierta); el efecto completo
  del cierre (entrada + `epic_features[].status` `done` + `closed_at` + `closure_evidence` —con el
  `closure_sha256` **derivado**— + `active_feature: null` + `current_stage: "idle"` + `active_packet`
  terminal/null) y la verificación de `_validate_idle_coherence` antes de publicar. **Excluido:** decidir
  si el **conjunto** de gates registrados es el correcto (INV-5); juzgar **si** un despacho debe
  disponerse (eso es del orquestador; el CLI sólo comprueba la coherencia y registra); interpretar el plan
  o los paquetes (semántica); el barrido de campos derivados sin dueño (deuda D-2); los despachos sin
  recibo de ejecuciones cerradas (deuda D-11).
- **Consume:** `transition-registration` (`transition-registration-v1`) de T1 y `approval-vigency`
  (`approval-vigency-v1`) de T5. **Produce:** `closure-required-check` (`closure-required-check-v1`).
- **Dependencias:** T1, T5.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`; *Test*
  `tests/test_005_012_t3_closure_dispatch_resolution.py`.
- **Contexto por rol:** RED — spec §1 (el caso B1), §2.3 (PD-8/PD-9/PD-21), §4 (AC-4), §5 D-4/D-13;
  `discovery.md` §4.1, §6; `005-013/debt.md:41-43`; GREEN — ídem + `cdad_packet.py:508-543,4698-4702` y
  `docs/specs/005-011-common-entry/closure.md:45-47` (caso 1 como fixture **sintético**).
- **Evidencia al re-entry:** focal rojo→verde: fixture con un paquete despachado **sin** recibo → cierre
  rc=2 `evidence missing` nombrando el paquete y **state byte-idéntico**; `--transition disposition
  --packet <id> --resolution abandoned` → rc=0, la entrada lleva `resolution`/`approval_effect: false`,
  **sin** `approved_by`, y `active_packet` **sin** `completed`; repetirla → rc=0 y **una sola** entrada,
  state byte-idéntico; tras la disposición el cierre **avanza** (reposo coherente, `validate-state`
  rc=0); el caso `superseded` con `--replaced-by` y su negativo (sin `--replaced-by` → rc=2); una
  disposición sobre un paquete **con** recibo o **no** despachado → rc=2 `state incoherent`; fixture con
  la aprobación **faltante** o su **pin que ya no nombra** los bytes actuales → rc=2 `approval pending`
  nombrando la aprobación (el caso «reemplazada **sin** `supersedes`» **no** pertenece al cierre: es de T5,
  PD-15); `git
  diff` acotado.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py -q`;
  regresiones `tests/test_005_001_t3_idle.py`, `tests/test_005_003_f2_idle_history.py`,
  `tests/test_005_007_t3_open_unit.py`, `tests/test_003_002_t1_receive.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si la disposición exigiera **fabricar** un estado terminal del paquete
  (un `completed` o un status nuevo), **detener** (B1: sin fabricar `completed`; el vocabulario de
  `active_packet.status` no se amplía); si el conjunto de entregas requeridas obligara a **interpretar**
  el plan o los paquetes (semántica), **detener** (D-4/INV-5) y declarar el límite como deuda.

### T4 — Entrega tardía: `receive --late` (máquina de recibos reusada) + `late-delivery` (traza durable)
- **Resultado observable / PD cubiertas:** PD-13, PD-4 (re-aplicado: la tardía tampoco aprueba), PD-20.
- **Alcance incluido:** en `cdad_result.py`, un modo **declarado** `receive --late` que **reusa** la
  máquina de recibos (`receive`, `:493-591`) —identidad, partes, digests, esquema de `receipt.json`,
  `semantic_status: "pending"` **siempre**— y **reemplaza** la única precondición que hoy bloquea
  (`validate_state` con la feature cerrada, `:513`→`cdad_packet.py:768`; y `active_packet` no
  `dispatched`, `:527-531`) por la precondición **inversa**: la feature destino **está** cerrada
  (`CLOSED_FEATURE_STATUSES`, `cdad_packet.py:114`) y el paquete pertenece a su ejecución. En
  `cdad_packet.py`, la clase `late-delivery` que exige el recibo durable (digest **derivado**, PD-20) y
  escribe **sólo** la traza (`stage: "late-delivery"`, `approval_effect: false`), sin tocar
  `epic_features[].status`, `closed_at`, `active_feature` ni `current_stage`. **Excluido:** una segunda
  máquina de recibos (prohibida: 005-004 PD-10); reabrir la feature; aprobar; borrar/mover los bytes del
  buzón; el staging y el descriptor (`RESULT.json`), que siguen siendo del orquestador (deuda D-8);
  cubrir el despacho que **nunca vuelve** (eso es `disposition`, T3, con la feature abierta).
- **Consume:** `transition-registration` (`transition-registration-v1`) de T1. **Produce:**
  `late-delivery` (`late-delivery-v1`).
- **Dependencias:** T1.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_result.py`,
  `skills/cdad-cycle/scripts/cdad_packet.py`; *Test* `tests/test_005_012_t4_late_delivery.py`.
- **Contexto por rol:** RED — spec §2.3 (PD-13), §5 D-5, `discovery.md` §6; `005-011/closure.md:45-47`
  (caso 1); GREEN — ídem + `cdad_result.py:493-591,802-842` y `cdad_packet.py:114,508-543`.
- **Evidencia al re-entry:** focal rojo→verde end-to-end: feature cerrada con el CLI → `receive --late`
  rc=0 y recibo durable con `semantic_status: "pending"`; `register-transition --transition
  late-delivery` rc=0 (con el `receipt_sha256` **derivado**); la feature **sigue `done`**
  (`epic_features`, `closed_at`, `active_feature`, `current_stage` **sin cambios**, con `sha256` del state
  antes/después y sólo el append de la traza); **ninguna** aprobación nueva; con la feature **abierta** →
  rc=2 `state incoherent`; sin recibo → rc=2 `evidence missing`; los negativos de `receive` normal
  (feature cerrada) **se conservan**; `git diff` acotado a los dos módulos.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_012_t4_late_delivery.py -q`; regresiones
  `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t2_materialize.py`,
  `tests/test_005_007_t4_architect_report_materialization.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si el modo `--late` exigiera **debilitar** una validación de identidad
  o de digest del recibo, **detener** (INV-2 y D-6: se invierte **sólo** la precondición de vigencia).

### T6 — `prepare --new-execution` rechaza el contexto ya abierto y sin uso
- **Resultado observable / PD cubiertas:** PD-16 (cierre pedido por 005-013, `debt.md:60-64`).
- **Alcance incluido:** detectar, en el camino de `prepare --new-execution`, que el contexto v2 de la
  feature activa está **abierto y sin uso** (sin paquetes publicados con su `execution_id` y sin
  registros de despacho) y **rechazar** con el marcador `state incoherent` **nombrando el contexto ya
  abierto** (`.cdad/executions/<exec-id>/execution.json`) y **cómo seguir**, en vez de acuñar un segundo
  id (`_next_execution_id`, `:1627-1632`; `_select_execution`, `:1702-1735`). El control vive **antes**
  de cualquier escritura. **Excluido:** tocar `open-unit`; tocar el camino de reuso del contexto
  (sin `--new-execution`); cubrir un contexto con paquetes o creado por otra vía (deuda D-5).
- **Consume:** — . **Produce:** `open-context-guard` (`open-context-guard-v1`).
- **Dependencias:** T1.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`; *Test*
  `tests/test_005_012_t6_open_context_guard.py`.
- **Contexto por rol:** RED — spec §2.3 (PD-16), §5 D-9, `005-013/debt.md:60-64`,
  `005-001/spec.md:69-73,99` (precedente del diagnóstico accionable), `discovery.md` §4.2; GREEN —
  ídem + `cdad_packet.py:1635-1660,1702-1735`.
- **Evidencia al re-entry:** focal rojo→verde: `open-unit` abre la unidad y deja el contexto v2 sin uso
  → `prepare --new-execution …` **rc=2** con el diagnóstico que **nombra** el contexto abierto y **no**
  acuña id nuevo (el directorio de ejecuciones no crece, el state queda byte-idéntico); control positivo:
  **sin** contexto abierto previo, `prepare --new-execution` sigue rc=0 y publica; `git diff` acotado.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_012_t6_open_context_guard.py -q`;
  regresiones `tests/test_004_002_t2_bootstrap.py`, `tests/test_packet_prepare.py`,
  `tests/test_005_007_t3_open_unit.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si el rechazo bloqueara un uso **legítimo** de `--new-execution`
  (control positivo en rojo), **detener** y re-acotar la condición en vez de ampliarla en silencio.

### T7 — Documentación por referencia (`re-entry.md` paso 4 + sección nueva de la operación)
- **Resultado observable / PD cubiertas:** PD-19; INV-4.
- **Alcance incluido:** en `skills/cdad-cycle/references/re-entry.md`, el **paso 4** (`:57-63`) pasa a
  **nombrar** la operación (`register-transition`) en lugar de dejar la transición al orquestador sin
  herramienta, **conservando** lo que el recibo liga y lo que **no** aprueba; en
  `skills/cdad-cycle/references/project-execution.md` (**sección nueva contigua a las operativas §5-§8**; en esa zona no existe una tabla literal), declarar
  la operación con su **referencia** a la spec. **Excluido:** copiar el texto de la spec; crear un
  documento nuevo; re-declarar la regla del pin, la del escritor único o la de idempotencia; tocar el
  mapa `entry` de 005-003 (`_entry_selection`, `:4736-4752`); tocar las skills de rol.
- **Consume:** `transition-registration` (T1), `stage-gate-registration` (T2), `closure-required-check`
  (T3), `late-delivery` (T4), `approval-vigency` (T5), `open-context-guard` (T6). **Produce:**
  `registration-docs` (`registration-docs-v1`).
- **Dependencias:** T1, T2, T3, T4, T5, T6. *docs-only* → `files: []` (convención de 005-011 T2 /
  005-007 T6); los paths viven en esta ficha.
- **Contexto por rol:** test-writer — spec §2.3 (PD-19), §8; reviewer — el texto **por sentido**.
- **Evidencia al re-entry:** comprobación observable roja→verde (el paso 4 no nombra operación → la
  nombra; la zona operativa no la declara → la declara la **sección nueva** con la referencia); `git diff` acotado a los dos
  archivos; el sentido del texto lo juzga la **review**.
- **Verificación:** `observable_checks`.
- **Integración / responsable:** `@validation_strategy`; implementer (edita las referencias); verificación
  por el orquestador y, por sentido, la review.
- **Incertidumbres / detención:** si conservar una guarda existente exigiera **copiar** el texto de un
  dueño, **detener** (INV-4).

### T8 — Gate de aceptación de la feature (AC-1..AC-4, con el CLI real del repo)
- **Resultado observable / PD cubiertas:** AC-1..AC-4; PD-1..PD-21 (verificación integrada).
- **Alcance incluido:** verificar los productos de T1..T6 en la corrida de aceptación: **AC-1** (ciclo
  representativo registrado **sólo** con la operación nueva, sin editar el state a mano, **en la forma
  mínima sin pasar ningún digest**), **AC-2** (entrega tardía sobre feature cerrada), **AC-3** (repetición
  tras interrupción), **AC-4** (el cierre rechaza nombrando la entrega/la aprobación faltante, con el
  state byte-idéntico, **y la disposición lo destraba**), más la comprobación de **no-regresión de PD-17**
  (`validate-state` verde sobre el state del repo —sólo lectura— antes y después; **sin** asertar
  porcentajes ni conteos del state vivo). Instrumento: **CLI real del repo** como subproceso, proyecto
  descartable en `<tmp>`, `HOME` en tempdir vacío, arnés fuera de git; evidencia cruda en `.cdad/local/`
  (no versionada). Declarar los **desconocidos** (número de invocaciones del recorrido; si
  alguna etapa sólo gana traza sin comprobación propia; si el fixture mínimo necesita plan del epic con
  anclas). **Excluido:** desplegar; correr el CLI instalado como versión bajo prueba; presentar la meta
  como umbral; declarar verde por proximidad.
- **Consume:** `transition-registration` (T1), `stage-gate-registration` (T2), `closure-required-check`
  (T3), `late-delivery` (T4), `approval-vigency` (T5), `open-context-guard` (T6), `registration-docs`
  (T7). **Produce:** `acceptance-report` (`acceptance-report-v1`).
- **Dependencias:** T1, T2, T3, T4, T5, T6, T7. **Gate:** cubre T1..T6 por la estrategia de validación
  (sus focales) y su cierre es el **gate de la feature**.
- **Archivos:** *Create* evidencia del informe (fuera del árbol publicable); *Test* — (gate, sin código).
- **Contexto por rol:** orchestrator — spec §4 (AC-1..AC-4) y §7; architect — lectura.
- **Evidencia al re-entry:** informe con la salida pegada de cada invocación y su `rc`; `sha256` del
  state antes/después de cada caso; **conteo de entradas** de `stage_history` (AC-3);
  `git diff --name-only`/`find` del fixture (AC-1: sólo lo que escribió el CLI; **cero** ediciones
  manuales); los digests **derivados** impresos por el CLI (AC-1); el recorrido B1 (rechazo → disposición
  → cierre avanza); los **desconocidos** con su causa.
- **Verificación:** `observable_checks`.
- **Integración / responsable:** **gate de aceptación de la feature 005-012**; orquestador OpenCode
  (HITL delegada); architect (lectura).
- **Incertidumbres / detención:** si falta evidencia de T1..T6 → **BLOQUEO declarado**, no atajo; si el
  despliegue se requiriera para AC-1..AC-4, **BLOQUEO declarado** (la aceptación corre el CLI del repo,
  §1); el despliegue es deuda D-4 y **no** bloquea la aceptación del gate.

### Bloque canónico

```plan-tasks
{"validation_strategy": "Verificacion en dos niveles: siempre procedencia + git diff contra el alcance + alcance declarado + pruebas focales (segundos); suite o integracion solo con un motivo concreto; la suite completa la corre una vez quien cierra; se reutiliza evidencia equivalente con procedencia verificada (regla canonica en skills/cdad-cycle/references/re-entry.md, seccion Equivalence of a registered run), sin repetir la suite. Los tests son caja negra sobre el CLI real como subproceso, con proyecto descartable en <tmp> y HOME del subproceso en un tempdir vacio (nunca el repo real, nunca HOME), y el test-writer no ve la implementacion. Los digests se prueban en su forma derivada por el CLI (sin afirmar ningun digest) y en el negativo de un digest afirmado divergente; no se asertan porcentajes ni conteos del state vivo (PD-17 se verifica con validate-state rc=0 antes y despues). El sentido de los textos documentales (T7) lo juzga la review: no se piden tests que decidan el significado de un parrafo por listas de palabras.",
 "tasks": [
  {"id": "T1",
   "objective": "Incorporar al CLI el subcomando register-transition con el escritor unico, la forma aditiva del registro, el marcador evidence missing, el resolvedor de digests derivados (si el digest se omite se calcula sobre los bytes actuales, se escribe y se imprime; si se afirma se verifica y una diferencia falla cerrado), la clase delivery (recepcion de una entrega) y la clase advance, mas la clave de identidad de la transicion con su comportamiento de repeticion, dejando usable la forma minima (delivery y advance), comprobando que recibir una entrega nunca aprueba y sin cambiar el rol de prepare.",
   "produce": [{"artifact": "transition-registration", "contract": "transition-registration-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
   "focal_tests": ["tests/test_005_012_t1_register_transition_base.py"],
   "regressions": ["tests/test_005_007_t3_open_unit.py", "tests/test_005_003_t1_compact_view.py", "tests/test_005_003_f2_idle_history.py", "tests/test_packet_prepare.py", "tests/test_004_002_t2_bootstrap.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "objective": "Cubrir la transicion gate (aprobacion de un gate, con el pin de contrato y plan verificado contra los bytes y su digest derivado cuando no se afirma) exigiendo la autoridad en sus tres casos: con delegacion registrada se verifica su vigencia (revocada o vencida falla cerrado); sin delegacion se registra el aprobador declarado y la salida declara que no hubo delegacion que verificar, sin bloquear al dueno; con active_epic null, sin autoridad que verificar. Consume la vigencia existente sin cambiarla.",
   "produce": [{"artifact": "stage-gate-registration", "contract": "stage-gate-registration-v1"}],
   "consume": [{"artifact": "transition-registration", "contract": "transition-registration-v1", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
   "focal_tests": ["tests/test_005_012_t2_gate_authority.py"],
   "regressions": ["tests/test_005_001_t1_role_approval.py", "tests/test_005_001_t4_decisive.py", "tests/test_005_007_t3_open_unit.py", "tests/test_packet_prepare.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T5",
   "objective": "Fijar la vigencia estructural de la aprobacion: una sola aprobacion vigente por (feature, stage, contract_path), con el campo supersedes en la entrada nueva, un lector aditivo que la ignora al reemplazarse y la exigencia de supersedes al registrar una segunda vigente, sin tocar la regla del pin de 005-001.",
   "produce": [{"artifact": "approval-vigency", "contract": "approval-vigency-v1"}],
   "consume": [{"artifact": "stage-gate-registration", "contract": "stage-gate-registration-v1", "producer": "T2"}],
   "depends_on": ["T1", "T2"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
   "focal_tests": ["tests/test_005_012_t5_approval_vigency.py"],
   "regressions": ["tests/test_005_001_t1_role_approval.py", "tests/test_005_001_tcorr.py", "tests/test_005_005_t1_replace_conserved.py", "tests/test_packet_prepare.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "objective": "Registrar el cierre de feature comprobando ANTES de aplicar que las entregas requeridas (paquetes despachados de la ejecucion con recibo durable o con una disposicion registrada) y la aprobacion vigente pinneada existan, fallando cerrado con el nombre de lo faltante y ofreciendo las dos salidas (recibir por el camino normal, o disponer), y agregar la clase disposition (B1) que registra una decision estructural sobre un despacho sin recibo con la feature abierta, sin aprobar nada y sin fabricar un completed, idempotente por transition_key, dejando la traza en stage_history y destrabando el cierre.",
   "produce": [{"artifact": "closure-required-check", "contract": "closure-required-check-v1"}],
   "consume": [{"artifact": "transition-registration", "contract": "transition-registration-v1", "producer": "T1"}, {"artifact": "approval-vigency", "contract": "approval-vigency-v1", "producer": "T5"}],
   "depends_on": ["T1", "T5"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
   "focal_tests": ["tests/test_005_012_t3_closure_dispatch_resolution.py"],
   "regressions": ["tests/test_005_001_t3_idle.py", "tests/test_005_003_f2_idle_history.py", "tests/test_005_007_t3_open_unit.py", "tests/test_003_002_t1_receive.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "objective": "Ofrecer la salida explicita de entrega tardia para una entrega que existe pero llega despues del cierre: un modo declarado receive --late que reusa la maquina de recibos invirtiendo solo la precondicion de vigencia para una feature cerrada, y la clase late-delivery que exige el recibo durable (digest derivado) y deja traza durable sin cambiar el estado de la feature y sin aprobar nada.",
   "produce": [{"artifact": "late-delivery", "contract": "late-delivery-v1"}],
   "consume": [{"artifact": "transition-registration", "contract": "transition-registration-v1", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_result.py", "skills/cdad-cycle/scripts/cdad_packet.py"],
   "focal_tests": ["tests/test_005_012_t4_late_delivery.py"],
   "regressions": ["tests/test_003_002_t1_receive.py", "tests/test_003_002_t2_materialize.py", "tests/test_005_007_t4_architect_report_materialization.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T6",
   "objective": "Rechazar prepare --new-execution cuando ya hay un contexto v2 abierto y sin uso, nombrando el contexto abierto y como seguir en vez de acunar un segundo id, conservando el funcionamiento legitimo sin contexto abierto previo.",
   "produce": [{"artifact": "open-context-guard", "contract": "open-context-guard-v1"}],
   "consume": [],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
   "focal_tests": ["tests/test_005_012_t6_open_context_guard.py"],
   "regressions": ["tests/test_004_002_t2_bootstrap.py", "tests/test_packet_prepare.py", "tests/test_005_007_t3_open_unit.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T7",
   "objective": "Documentar por referencia: que re-entry.md (paso 4) nombre la operacion en vez de dejar la transicion al orquestador, y que la seccion nueva de la operacion en project-execution.md (contigua a las operativas 5-8) la declare, sin copiar la regla de su dueno.",
   "produce": [{"artifact": "registration-docs", "contract": "registration-docs-v1"}],
   "consume": [{"artifact": "transition-registration", "contract": "transition-registration-v1", "producer": "T1"}, {"artifact": "stage-gate-registration", "contract": "stage-gate-registration-v1", "producer": "T2"}, {"artifact": "closure-required-check", "contract": "closure-required-check-v1", "producer": "T3"}, {"artifact": "late-delivery", "contract": "late-delivery-v1", "producer": "T4"}, {"artifact": "approval-vigency", "contract": "approval-vigency-v1", "producer": "T5"}, {"artifact": "open-context-guard", "contract": "open-context-guard-v1", "producer": "T6"}],
   "depends_on": ["T1", "T2", "T3", "T4", "T5", "T6"],
   "parallel": [],
   "files": [],
   "observable_checks": ["skills/cdad-cycle/references/re-entry.md, paso 4, nombra la operacion register-transition que registra la transicion del estado, conservando que el recibo liga las partes y que no aprueba (semantic_status pending); la seccion nueva de la operacion en skills/cdad-cycle/references/project-execution.md, contigua a las operativas 5-8 y a sus comandos por operacion, declara la operacion (incluida la disposicion y su resolucion) por referencia a la spec; ninguna regla de un dueno (pin de aprobacion, escritor unico, idempotencia, forma del state) se re-declara ni se copia; el mapa entry de la vista no cambia; el sentido de los textos lo juzga la review, no una lista de palabras"],
   "regressions": [],
   "integration_gate": "@validation_strategy",
   "owner": "implementer (docs-only; verificacion por el orquestador y por sentido en la review)"},
  {"id": "T8",
   "objective": "Gate de aceptacion de la feature con el CLI real del repo como subproceso sobre un proyecto descartable en <tmp> y HOME en un tempdir vacio: AC-1 (un ciclo representativo registrado solo con la operacion nueva, sin editar el state a mano y corriendo en la forma minima sin pasar ningun digest), AC-2 (entrega tardia sobre feature cerrada), AC-3 (repeticion tras interrupcion sin duplicar) y AC-4 (el cierre rechaza nombrando la entrega o la aprobacion faltante, con el state byte-identico, y la disposicion del despacho sin recibo lo destraba), declarando los desconocidos.",
   "produce": [{"artifact": "acceptance-report", "contract": "acceptance-report-v1"}],
   "consume": [{"artifact": "transition-registration", "contract": "transition-registration-v1", "producer": "T1"}, {"artifact": "stage-gate-registration", "contract": "stage-gate-registration-v1", "producer": "T2"}, {"artifact": "closure-required-check", "contract": "closure-required-check-v1", "producer": "T3"}, {"artifact": "late-delivery", "contract": "late-delivery-v1", "producer": "T4"}, {"artifact": "approval-vigency", "contract": "approval-vigency-v1", "producer": "T5"}, {"artifact": "open-context-guard", "contract": "open-context-guard-v1", "producer": "T6"}, {"artifact": "registration-docs", "contract": "registration-docs-v1", "producer": "T7"}],
   "depends_on": ["T1", "T2", "T3", "T4", "T5", "T6", "T7"],
   "parallel": [],
   "files": [],
   "observable_checks": ["AC-1: el ciclo representativo (open-unit, advance, gate de etapa 2, delivery del RED y del GREEN, gate de T4, delivery del Memory Bank, closure) se registra SOLO con register-transition sobre un proyecto descartable, con el CLI del repo como subproceso y HOME del subproceso en un tempdir vacio, SIN pasar ningun digest (los digests derivados se leen en la salida y en la entrada); el state resultante es byte a byte el producido por el CLI (cero ediciones manuales comprobadas por find/git diff del fixture) y validate-state queda verde. AC-2: tras cerrar con closure, receive --late + late-delivery sobre el buzon dejan la feature done, semantic_status pending, ninguna aprobacion nueva y traza durable. AC-3: la repeticion identica deja UNA sola transicion (conteo de entradas de stage_history) y el state byte-identico; una transicion distinta se registra como nueva; una excluyente falla cerrado nombrando el conflicto; idem para la disposicion. AC-4: el cierre rechaza con rc=2 y el marcador (evidence missing / approval pending / state incoherent) NOMBRANDO la entrega o la aprobacion faltante, con sha256 del state byte-identico tras el rechazo; y el caso B1: con la feature abierta y un despacho sin recibo, el cierre rechaza nombrandolo, se registra la disposicion (--transition disposition --resolution abandoned o superseded con --replaced-by), repetirla es no-op (una sola entrada, state byte-identico) y el cierre avanza con el reposo coherente. No-regresion PD-17: validate-state sobre el state del repo (solo lectura) verde antes y despues, sin asertar porcentajes ni conteos del state vivo. Desconocidos declarados: numero de invocaciones del recorrido, si alguna etapa solo gana traza sin comprobacion propia, y si el fixture minimo necesita plan del epic con anclas. El despliegue no es requisito del gate: la version bajo prueba es el CLI del repo"],
   "regressions": [],
   "integration_gate": "gate de aceptacion de la feature 005-012: AC-1..AC-4 con el CLI real del repo como subproceso sobre proyecto descartable en <tmp> y HOME en tempdir vacio, con evidencia pegada y digests del state antes/despues; cubre T1..T6 por sus focales rojo-a-verde y git diff acotado, y T7 por comprobaciones observables y review; el despliegue queda como deuda del dueno (D-4) y no bloquea este gate",
   "owner": "orquestador OpenCode (HITL delegada epic-005); architect (lectura)"}
 ]}
```

## 5. Trazabilidad PD/AC → tarea

PD-1, PD-2, PD-3, PD-4, PD-7, PD-10, PD-11, PD-12, PD-17, PD-18, **PD-20** → **T1**;
PD-5, PD-6 → **T2**; PD-14, PD-15 → **T5**; PD-8, PD-9, **PD-21** → **T3**; PD-13 → **T4**;
PD-16 → **T6**; PD-19 → **T7**; PD-1..PD-21 integradas → **T8**.
INV-1..INV-9 → transversal (cada tarea declara las suyas en su ficha; la verificación integrada es T8).
AC-1, AC-2, AC-3, AC-4 → **T8** (con los productos de T1..T7).
**B1 → T3** (PD-8(a)/PD-21) y su prueba en **T8** (AC-4). **P1 → T1** (PD-20) y en los consumidores
T2/T3/T4. **P2 → T2** (PD-6, tres casos).
**B2 → T1** (la identidad y su payload, PD-10/PD-11) y en sus **consumidores por la clave**: **T3** (la
disposición sigue idempotente por `transition_key`, ahora con `resolution` **y** `replaced_by` dentro) y
**T4**; su prueba integrada es de **T8** (AC-3 mide que una transición que difiere sólo en un insumo con
efecto se registra como nueva; AC-4 mide el no-op de la disposición). Implementación: **RED primero** en el
focal de T1 (y el caso de la disposición en el de T3) antes del GREEN; **esta entrega es el contrato**, no la
implementación.
**O1 → T3** (ficha) y **T8** (AC-4); **O2 → §2.1/PD-13** (superficie que consumen T1 y T4); **O3 → T7**
(ficha y observable canónico del bloque); **O4 → T2** (PD-6). **B1** (de la review) queda en la
implementación de **T3**, sin cambio de texto; **O5/O6/O7 → deuda** (spec §7, deuda D-13..D-15).
**B3 → T5** (el **predicado de vigencia** del control de exclusión, **PD-14**, y el texto de **D-8**): prueba en
el focal de T5 —con una aprobación previa **sin `transition_key`** y su pin **que ya no nombra** los bytes
actuales, el `gate` de etapa 2 registra **rc=0 sin `--supersedes`** y la nueva entrada queda como la única que
habilita—, más la **coherencia** de §6/§7 y de las referencias a PD-14 (spec §0.1); el límite de los **mismos**
bytes desde una entrada vigente **sin clave** queda como **deuda D-16** (declarada, sin test propio).
**RED primero** en el focal de T5 antes del GREEN; **esta entrega es el contrato**, no la implementación.

## 6. Meta de aceptación y gate de la feature

- **La feature cierra cuando** AC-1..AC-4 tienen evidencia **con el CLI del repo** y los focales de
  T1..T6 están rojo→verde con su `git diff` acotado; T7 por comprobaciones observables y la review del
  texto.
- **Meta de aceptación (fila 12 + discovery §17).** El recorrido de **AC-1** se registra **sólo** con la
  operación nueva y **en la forma mínima (sin digests)**; los **6 scripts de registro** del último ciclo
  cerrado (`docs/specs/005-013-unit-contract/debt.md:65-69`) dejan de ser necesarios; el **único**
  control nuevo es la comprobación del **cierre** (PD-8), con su **salida** para el despacho que no
  vuelve (PD-21). Los números son **orientación**, no umbral.
- **El gate de la feature es el de T8.** Instrumento: CLI real del repo como subproceso, proyecto
  descartable en `<tmp>`, `HOME` en tempdir vacío; nunca el repo real, nunca HOME.
- **Productor / actor / evidencia por caso:** el **orquestador** produce el proyecto descartable y corre
  las invocaciones; el **orquestador** (HITL delegada) evalúa; la evidencia es la salida pegada con `rc`,
  el `sha256` del state antes/después y el conteo de entradas (AC-3). La **review formal** juzga el
  contrato y el sentido de los textos, no los tests.
- **Deuda de la feature:** lista completa con condición de cierre en
  `docs/specs/005-012-transition-registration/spec.md` §7 (D-1..D-8, **D-9 retirada**, D-10, D-11,
  D-12..D-15 y **D-16**): el
  veredicto fino de reconciliación (D-1), el inventario de campos derivados sin dueño (D-2), el tamaño del
  state (D-3), el **despliegue** (D-4), el alcance acotado del rechazo del contexto abierto (D-5), la
  identidad de quien aprueba (D-6), D-3 de 005-013 (D-7), el staging del buzón (D-8), la autoridad sin
  delegación a nivel de estado (**D-10**), los despachos sin recibo de ejecuciones cerradas (**D-11**), el
  no-op de las entradas con la fórmula anterior de la clave (**D-12**), los opcionales O5/O6/O7 (**D-13..D-15**)
  y la reaprobación de los **mismos** bytes desde una aprobación vigente **sin clave** (**D-16**, B3).
  **D-9 (la anulación de un despacho) dejó de ser deuda**: su salida es la disposición (PD-21/D-13).
- **Suite completa una vez**, por quien cierra, en un worktree fijado al commit de cierre; `make
  validate` sin fallos nuevos.

## 7. Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**; **sin desplegar**; **sin
  tocar HOME**; **sin leer** `tests/.sensitive-patterns.local`.
- **Sin valores de este VPS** en spec, plan ni producto: sin rutas de HOME, sin rutas absolutas del
  dueño, sin ids crudos de sesión (`<home>`, `<repo>`, `<tmp>`, `<ses-…>`, `<exec-id>`).
- **No** reescribir los contratos de 005-001/005-003/005-005/005-007/005-011/005-013 ni los de 003-*:
  extensión **aditiva y declarada** o **referencia**. Las dos extensiones declaradas son el marcador
  `evidence missing` y el predicado «vigente» de **PD-14** de la spec (§2.3: el pin que **nombra** los bytes
  actuales, un solo criterio con el cierre, PD-8(b); B3).
- **Sin tests que decidan el significado de un texto** por listas de palabras: el sentido lo juzga la
  review (T7). **Sin tests que aserten porcentajes ni conteos del state vivo** (PD-17).
- **Sin volcar salidas enormes** al contexto; evidencia completa por referencia. Para comprobar un RED
  sin el arreglo: **worktree**, **nunca `git stash`** en el árbol compartido.
- **Ante un obstáculo fuera de alcance: entregar el diagnóstico, no fabricar registros.**

## 8. Estado
**Estado: APROBADO.** El **architect** no aprueba su propia propuesta (anti-sesgo). Se aprobó **junto con la spec corregida, en una sola acción**, por el **orquestador OpenCode** el **2026-10-14** bajo la **HITL delegada del epic-005** (`docs/epics/epic-005-real-operation/execution.md:8-23`). **Esta aprobación REEMPLAZA la del draft-003** (plan `fb270b70bc9841e1e027f1ec1561b204e95f3634ca275a991821c829f34885d0`), que queda **sustituida y no vigente**. Motivo: **B3** — el control de exclusión de PD-14 pasa a competir solo con las entradas cuyo pin **nombra los bytes actuales** (el mismo criterio que PD-8(b)), de modo que la reaprobación tras una enmienda no necesita `--supersedes` y no obliga a editar el state a mano; el caso raro de los mismos bytes con entrada keyless va a deuda **D-16**. La cabecera DRAFT del rol se conserva como registro de la entrega; el estado vigente es el de esta sección.

El bloque canónico `plan-tasks` de §4 queda **byte-idéntico** al aprobado y **revalidado por el orquestador** con las funciones del propio CLI (`_plan_tasks_from_contract`, `_check_plan_tasks`, `_check_plan_validation_plan`): **OK**, T1..T8, `validation_strategy` idéntica. La ficha **T5** y la trazabilidad (§5) incorporan B3. Rige el **criterio de review vigente del 2026-10-12** y las restricciones globales de §7. La meta de aceptación es la de §6. La verificación de esta versión está en la spec §11. **El arreglo de B3 no está implementado en esta entrega** (contrato): el RED va primero en el focal de T5. La firma y los hashes están en `docs/.cdad-state.json` (`stage_history`, `stage: specification`).

Status: Approved by orchestrator OpenCode (epic-005 delegated HITL) on 2026-10-14
