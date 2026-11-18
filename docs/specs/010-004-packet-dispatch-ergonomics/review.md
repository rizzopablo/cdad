# review.md: 010-004-packet-dispatch-ergonomics (T6, Stage 4)

**Resultado: 4 hallazgos BLOQUEANTES, 3 requeridos no bloqueantes y 4 opcionales.** El código de `cdad_packet.py` cumple lo que probé. Los bloqueantes están en PC-03, PC-07b y PC-10/11, y en la falta de un test exigido por §7.1 para PC-04. Este informe no aprueba la publicación ni el cierre: decide el usuario.

## Admisión y base

- **Paquete:** ruta C, sin cuerpo inline. `validate-request` dio rc=0, `validate-packet` dio rc=0 y `render` es idéntico a `PACKET.md` (`cmp`). Usé los scripts del repo.
- **Identificación:** el objeto JSON recibido coincide con `render --route C`, comparado a la vista. El sha256 de `spec.md` es `fc6b2ccc…5d64`.
- **Base:** `922db1a6` es ancestro de HEAD (`--is-ancestor` rc=0), con 73 commits y 75 archivos en el diff. No encontré evidencia de otra base mejor.
- **Tests ejecutados:**
  - T2, T3, T4 y propiedades T5: **17 passed**.
  - `tests/test_010_004_t5_e2e.py`: **2 passed**, en 24,72 s frente a los ~99 s que registra `e2e-t5.md`. La diferencia no cambia el resultado.
  - No hay `skip` ni `xfail` en los tests `test_010_004_t*`.
- **Derivados:** regeneré los agentes fuera del repo con `cdad-generate.py` y `cmp` no da diferencias frente a `agents/` y `agents/claude-code/`.

## Hallazgos bloqueantes

### B1. El intake del rol no rechaza A+C ni exige v2 para C (Required)

**Verdict: BLOCKING · Bucket: h**

- **Ubicación:** `sources/roles/architect.md:15-57`, bloque `intake-core`, sin cambios en el diff.
- **Evidencia:**
  - §4.3 (`spec.md:296,309-311`) y PC-03 exigen que el intake pida contexto v2 para C y rechace la mezcla A+C aunque el inline coincida.
  - El intake compartido no contiene "A+C", "mix" ni "v2". Un grep sobre `sources/roles/*.md` solo encuentra "A+C" en `orchestrator.md:70`.
  - Solo la capa de despacho (orquestador, adaptadores, handoff) enuncia la regla. La fila PC-03 de `t4-closure.md:96` también cita solo esa capa.
- **Consecuencia:** una identificación C junto con un paquete A completo tiene exactamente un marcador, así que el rol admite por ruta A en vez de rechazar. Un rol que recibe C sobre v1 tampoco tiene diagnóstico prescrito.
- **Cierre:** `intake-core` y los derivados por árbol enuncian el rechazo de A+C y C solo-v2, con su diagnóstico. Una guarda mecánica comprueba esos textos en fuentes y derivados.

### B2. Paquete v1 activo: se ofrece el procedimiento que la spec prohíbe (Required)

**Verdict: BLOCKING · Bucket: h**

- **Ubicación:** `skills/cdad-cycle/scripts/cdad_packet.py:6424`.
- **Evidencia del contrato:** `spec.md:205,222,352` y PC-07b comprometen un único resultado: diagnosticar el bloqueo y la ausencia de ruta CLI terminal, y escalar al owner. `:222` dice "No indicar «completar o fallar»".
- **Prueba:** usé una fixture temporal con `.cdad/execution.json` v1 y `active_packet` `prepared`. Fue armada a mano y sus campos de contrato eran ficticios. El rechazo sale de la rama PD-4, que no evalúa esos campos.

```text
prepare                  → rc=2 "... Start the new v2 execution with `prepare --new-execution`"
prepare --new-execution  → rc=2 "active packet 'old-v1-packet' is 'prepared': complete or fail it
                                 before preparing a new packet (PD-4)"
Árbol .cdad/ + docs/ idéntico por sha256 en ambos casos.
```

- **Lo que sí cumple:** no modifica el state, no prepara v1 y no deja contexto huérfano.
- **Consecuencia:** el usuario sigue la primera indicación y llega a un callejón sin salida con una orden que no se puede ejecutar. Ningún paso escala al owner.
- **Superficie documental:** no hallé la cláusula en `orchestrator.md`, en `references/*.md` ni en el script (grep: `v1 activo`, `active v1`, `v1 packet`, `terminal route`). `project-start.md` solo se rastreó con otros términos (`PC-07b`, `v1 activ`, `resume-packet`, `escalat`, `not terminal`), sin resultados. `project-execution.md:115-117` recomienda `--new-execution` sin esa salvedad, y ese archivo no cambió, aunque `spec.md:80` lo declara superficie.
- **Cierre:** con un paquete v1 activo, ambos comandos diagnostican el bloqueo, la ausencia de ruta terminal y la escalación al owner, y no dicen "complete or fail". Un test exige árbol y state idénticos. `project-execution.md` y el orquestador describen el mismo resultado.

### B3. PC-10/PC-11 sin procedimiento real; la evidencia citada no los acredita (Required)

**Verdict: BLOCKING · Bucket: h**

- **Evidencia:**
  - `spec.md:426-428` y §4.7 exigen distinguir integridad publicada, observabilidad y fidelidad, y conservar I-4 e I-5.
  - El grep de `observab|I-4|I-5|integrity|stdin|reconstructed|literal|route C|fidelity` en `re-entry.md`, `project-execution.md`, `handoff-prompts.md`, `cli-delegation.md` y `orchestrator.md` no devuelve ninguna regla de ese tipo. En `re-entry.md` no aparece ninguna regla sobre I-4, I-5, stdin, el literal reconstruido o el prompt recibido.
  - `re-entry.md` no cambió en el diff.
- **`t4-closure.md:99-100` no acredita estas PC:**
  - `cli-delegation.md:405-407` trata de contención de locks del store.
  - `re-entry.md:159` trata de no repetir la suite.
  - Esos textos dicen que recibo y `rc` no aprueban, lo que coincide con INV-09, pero no dicen que archivo, stdin, literal o recibo no prueban el prompt recibido.
  - Tampoco dicen que la falta de observabilidad por sí sola no obliga a repetir.
- **Consecuencia:** los incidentes que motivaron esta promesa se pueden repetir en ambos sentidos. Se puede bloquear o repetir por no tener evidencia de entrega, o certificar una entrega por autoatestación.
- **Cierre:** `re-entry.md` (o su dueño declarado) contiene la distinción de §4.7 y las reglas I-4 e I-5, incluida la recuperación por encargo nuevo v2. La traza de `t4-closure.md` se corrige.

### B4. Sin test de que el sucesor declare el localizador (Required)

**Verdict: BLOCKING · Bucket: m**

- **Evidencia:** el producto lo implementa en `cdad_packet.py`, en `_replace_packet` (hunk `@@ -3550`). `spec.md:462` exige que "debe comprobarse… la incorporación del campo en las nuevas generaciones afectadas".
- **Búsqueda:** `--replace-packet` no aparece en `tests/test_010_004_*.py` ni en `test_packet_prepare.py`. `test_006_006_w1_replace_draft_packet.py:258,687` solo usa una ruta de contexto. No revisé cada test histórico de reemplazo.
- **Consecuencia para el usuario:** si esa línea se rompe, el sucesor se publica sin localizador y aun así pasa con `--execution-context` explícito, por la misma circularidad de I-6. El defecto no se ve hasta el gate del padre, o no se ve.
- **Cierre:** un test de `--replace-packet` con predecesor sin campo comprueba el localizador en el request y la cabecera del sucesor, y comprueba que los bytes del predecesor no cambian.

## Hallazgos requeridos no bloqueantes

### R1. D-1: nada de 010-004 rige en la cadena instalada

**Verdict: OPTIONAL · Bucket: h** (el contrato excluye publicar; el riesgo es de declaración)

- **Medido:** repo `44a950a5…`, instalado `171fcd14…`. El CLI instalado no tiene `--route` y rechaza este mismo paquete con `ERROR: request fields do not match schema`.
- **Veredicto contractual:** el cierre puede declararse sin publicar. `spec.md:95,378,521` excluyen la publicación y la interoperabilidad entre versiones, y PC-12 pide un consumidor aislado actualizado. No hay dependencia contractual oculta.
- **Dependencia operativa oculta:**
  - Hasta publicar, el despacho real necesita la toolchain del repo, como declara este encargo.
  - La admisión en la frontera re-renderiza con el asset root instalado (`v2-1-verification.md`, D-1), y `prepare` republica los agentes derivados desde esa fuente.
  - El `prepare` instalado sigue admitiendo v1 implícito sin policy, porque es el comportamiento anterior a la unidad. Lo deduzco del diff, no lo ejecuté.
- **Condición:** el texto de cierre debe decir "cerrada en repo, no vigente en la instalación" y registrar la decisión del owner sobre publicar. Una lectura dirigida de `e2e-t5.md`, `t4-closure.md` y `v2-1-verification.md` muestra que declaran no haber publicado, pero no vi esa formulación como límite de la unidad.
- **Texto obsoleto:** `v2-1-verification.md`, Decisión 4, dice que `cdad_packet.py` difiere "sólo en la canonicalización"; ya no es cierto. Hay que marcarlo como histórico.

### R2. I-6 no quedó cerrado estructuralmente

**Verdict: OPTIONAL · Bucket: h**

La fila 3 de la matriz, que el contrato manda, no distingue un request histórico de uno nuevo sin localizador. Por eso un paquete nuevo publicado por la copia instalada pasa con `--execution-context`, y `--route C` puede emitir una identificación con `execution_context` aunque el request no lo declare. La corrección fue retirar el paquete y una lección manual. Publicar la instalación reduce la vía, pero no elimina la ambigüedad. Si se quiere cerrar, hace falta un gate del orquestador que exija el campo en paquetes nuevos, con su propio contrato.

### R3. Las guardas documentales son débiles

**Verdict: OPTIONAL · Bucket: h**

`test_010_004_t4_red.py` solo exige el token `--route C` y su supervivencia en derivados. Por eso B1 y B3 quedaron en verde. No es gaming: §7.5 pide revisión independiente y prohíbe tratar los tests de texto como obediencia. Pero `t4-closure.md` presenta como acreditación lo que no lo es.

## Opcionales y FYI

- **O1 (FYI) · OPTIONAL · Bucket: h.** Este despacho no fue "stdout ALONE" (`orchestrator.md:63-73`). Llevó prosa y una precondición de toolchain entre la declaración y el bloque JSON. La causa es D-1. El objeto JSON coincide y no invalida la admisión, pero muestra que la regla es solo instrucción, igual que la clase I-7.
- **O2 (Consider) · OPTIONAL · Bucket: m.** `_route_c_execution_context` y `_route_c_published_request` repiten comparaciones de resolución con `_resolve_request_execution_context`. No observé divergencia, así que no bloquea.
- **O3 (FYI) · OPTIONAL · Bucket: h.** La copia del contrato en `inputs` de I-6 (addendum) pasa los validadores. Es una lección manual sin guarda; conviene evaluarla aparte.
- **O4 (Nit) · OPTIONAL · Bucket: l.** La cabecera `Estado:` de `spec.md:3` sigue diciendo borrador pendiente. El registro final la supera, y el pin impide editarla sin nueva aprobación.

## (i) Correspondencia PC ↔ evidencia

| PC | Evidencia | Juicio |
|---|---|---|
| PC-01, PC-02 | `test_010_004_t3_red.py`, E2E, propiedad INV-04 | Acreditadas por test; verifiqué que pasan |
| PC-03 | Solo capa de despacho; test de token | **No cumplida en intake (B1)** |
| PC-04 | T2, `test_004_002_t6_landing.py`, `test_packet_prepare.py`, E2E | Ordinaria acreditada; sucesor sin test (**B4**) |
| PC-05, PC-06, PC-07 | T2 (`pc05a`, `pc06a`, `pc06b`, `pc07a`, `pc07c`) | Acreditadas por test |
| PC-07b | `t4-closure.md:97`; prueba propia | **Incumplida (B2)**; `project-execution.md:122-127` tampoco enuncia las "condiciones v2" que se le atribuyen |
| PC-08a | Tests T3 de preámbulo; INV-05 con bytes sembrados | Acreditada por test |
| PC-08b | `architect.md:19-30` y derivados | Texto presente; no acredita obediencia |
| PC-09 | Aserciones dentro de negativos T3 | Acreditada para C; contradicha por B2 en preparación |
| PC-10, PC-11 | Citas no pertinentes | **No acreditadas (B3)** |
| PC-12 | E2E 2/2; derivados sin diferencias | Recorrido aislado acreditado; consistencia documental rota por B1-B3 |

| INV | Evidencia | Juicio |
|---|---|---|
| INV-01 | V2-1, plantilla POST-AUDIT | Cumple en repo; la copia instalada sigue combinando subfases (R1) |
| INV-02, INV-03 | Validadores conservados; `_validate_declared_execution_context` corre antes | Sin defecto observado; revisión por lectura |
| INV-04, INV-05 | Propiedades T5 | Acreditadas por test |
| INV-06 | Texto de intake; I-8 muestra un límite relacionado | Sin enforcement mecánico (PD-15) |
| INV-07 | El diff no añade ledgers ni conectores | Cumple por lectura |
| INV-08, INV-11 | Tests T2/T6; prueba de B2 con árbol idéntico | Cumple en lo probado |
| INV-09 | `re-entry.md`, recibo `pending` | Cumple |
| INV-10 | Regeneración sin diferencias | Cumple, medido |
| INV-12 | PC-04 y C v2-only | Sin test del sucesor (B4); no rige en la instalación (R1) |

## (ii) Riesgos de gaming

- **Migraciones de tests:** revisé completos los diffs de `test_004_002_t6_landing.py` y de `test_004_003_t1_reviewfix.py`, tomado como muestra de las migraciones de fixture de 6-9 líneas; no leí las demás.
  - `pd12` se invierte a rechazo con traza a N-3 y añade aserciones. No se debilita.
  - La muestra de fixture solo materializa el contexto canónico.
  - De `test_packet_prepare.py` y `test_004_002_t7_acceptance.py` solo vi las líneas de aserción eliminadas: 3 en total, sin examinar con qué se reemplazaron.
- **Tests T2-T5:** el grep de patrones de salto o aserción trivial no encontró nada, y los E2E tienen controles positivos declarados en `e2e-t5.md`. No hice mutación.
- **Oráculos:** el E2E compara contra archivos publicados, según su documentación. No auditarlo línea a línea queda en abstenciones.
- **Prosa congelada y duplicación:** el bloque "Dispatch vehicle" está casi duplicado en cuatro superficies y solo se protege el token `--route C`, por lo que puede divergir. Además, `t4-closure.md:96-100` cita líneas que no respaldan lo afirmado.

## (iii) Incidentes

- **I-6:** corrección aplicada al caso, pero sigue abierta la clase (R2).
- **I-7:** paquete íntegro y fallo correcto del rol. `render --route C` reduce la causa, pero no la impide (O1). No revela un defecto del producto.
- **I-8:** sigue abierto como defecto de diseño de scopes. Está registrado con tres salidas posibles en `observations-packet-dispatch.md`, pero sin unidad asignada. El mandato prohíbe resolverlo aquí; conviene llevarlo al backlog de la épica.

## (iv) D-1 y F011

D-1 no impide cerrar según el contrato, con la condición de declarar el límite de R1. F011 está documentado como ambiental en `t4-closure.md:72-77`: `install.sh --check` compara el repo con la instalación desactualizada. Corregirlo exige publicar, de modo que **F011 seguirá en FAIL al cierre** y debe declararse así. No ejecuté `make validate`.

## (v) Limitaciones PD-15

**Declaradas:**
- no prueba recepción nativa ni obediencia del modelo (§4.7, `e2e-t5.md`);
- ventana entre validación y lectura;
- preámbulos no unificados;
- interoperabilidad de versiones;
- la instantánea global no ve escrituras transitorias;
- laguna v1 activo en la spec.

**No declaradas o insuficientes:**
- la unidad no está vigente en la cadena instalada (R1);
- A+C solo existe como instrucción de despacho, no en el intake (B1);
- la fila 3 no distingue un paquete nuevo sin campo (R2);
- las guardas documentales solo comprueban un token (R3);
- ningún validador comprueba que los `inputs` sean los pretendidos (O3).

## Current decisions / ADR

No comparé la tabla de decisiones vigentes con `docs/adr/`: el paquete no declara `current_decisions`. Queda en abstenciones.

## Abstentions

- **Suite completa:** no ejecutada; la corre quien cierra.
- **`make validate` y F011:** no reproducidos.
- **Tabla de decisiones contra `docs/adr/`:** no realizada.
- **Mutación y lectura línea a línea de los tests T5, y resto de migraciones de fixture:** no realizadas.
- **Bucket:** asignado a partir de la evidencia observada; no apliqué la regla completa de `verdict-tuple.md` ni verifiqué la familia del modelo del implementer.
- **PC-09 en preparación, salvo B2:** causas de pin y autoridad no probadas.
- **Cobertura de reemplazo en tests históricos fuera de los archivos citados:** no auditada; si existe, B4 se reduce.

## Evidence required

- **Archivos modificados:** ninguno. Las fixtures temporales se crearon en `~/clawd/tmp` y se borraron, y `git status --short` conserva solo `docs/specs/010-000-continuity-relative-root/discovery.md`, que ya estaba.
- **Commit:** ninguno.
- **Comandos principales:**
  - `cdad_packet.py render`, `validate-request`, `validate-packet` y `render --route C` con el `--project-root` y `--execution-context` del paquete.
  - `cmp` y `git merge-base --is-ancestor 922db1a6 HEAD`.
  - `git rev-list --count 922db1a6..HEAD` y `git diff 922db1a6..HEAD`.
  - `env -u TMPDIR python3 -m pytest tests/test_010_004_t2_red.py tests/test_010_004_t3_red.py tests/test_010_004_t4_red.py tests/test_010_004_t5_properties.py -q`.
  - `env -u TMPDIR python3 -m pytest tests/test_010_004_t5_e2e.py -q`.
  - `scripts/cdad-generate.py` con salida temporal para ambos runtimes, comparada con `cmp`.
  - Probe de B2 sobre la fixture de `TestPd10ForwardAdoption`.
- **Salidas clave:** citadas arriba.