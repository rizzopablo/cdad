Validación de ruta C completa: `validate-request` rc=0, `validate-packet` rc=0, `render --route C` idéntico byte a byte al bloque recibido, `sha256` del contrato coincidente, contexto v2. Verifiqué por mi cuenta las cinco vueltas del `plan-review`, la atribución de D-1..D-6 al discovery y las etiquetas F-1/F-2/F-3 en `challenge-review.md`/`semantic-evidence.md` frente al F-1 de `product-review.md`, y los hashes y commits citados.

---

## (1) `docs/activeContext.md`

**Dónde va:** como **primera entrada**, justo después del `---` de la línea 5 y antes de `## 2026-10-31 — Feature: 010-002-documentary-role-integration` (el archivo declara «las entries más recientes arriba»).

```markdown
## 2026-10-31 — Feature: 010-003-documentary-pilot (epic 010, orden 4 del plan)

**Cierre declarado y aceptación funcional registrada por mandato; NO aprobado directamente
por el dueño y NO publicado.** `closure.md` reúne los tres registros exigidos por PC-14
(`structural-evidence.md`, `semantic-evidence.md`, `functional-acceptance.md`) y declara el
mapa PC-01..PC-15; la aceptación la ejerce el orquestador **en nombre del dueño** bajo el
mandato HITL del 2026-10-30 (§1 y §3), y se registra como tal: **no** es aprobación directa
del dueño. Este cierre no publica, no hace push y no actualiza la instalación global.
Contrato: `docs/specs/010-003-documentary-pilot/spec.md` v5,
`f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5`; plan v6,
`49ce6f813aeb4e0bea0ff4f44d541a48deef29dc42f2af5aa6e05e5bf3352b04`.

**Qué se cerró.** Un piloto recorrió el ciclo completo con un entregable documental
trazable sobre un corpus **sintético**: el producto `product/relevamiento.md`
(`007af655ef926e98df26920792f48d4098136cfc1d2a347a0cc427da1ef40e0f`, commit `6596e804`)
corrige el candidato negativo contra el inventario `inventory-010-003-v1` (14 citas, 10
anclas, **10/10 artefactos fijados sin deriva**). Sobre ese desafío **declarado y sembrado**,
un ensayo en sesión separada (`<session>`), **sin clave y sin producto**,
identificó y fundamentó las tres clases comprometidas —**F-1/F-2/F-3 del ensayo (T5)**:
afirmación presentada como hecho sin respaldo, contradicción omitida y referencia existente
que no sostiene— y el contraste posterior dio **3/3 coincidencias y cero omisiones**, más tres
extras que la clave no enumeraba. La revisión **T6** encontró un bloqueante nuevo, **el
bloqueante F-1 de T6 (divergencia del inicio del plazo)** —la divergencia de las fuentes sobre
el inicio del plazo no estaba declarada—; **T7** lo corrigió —atribuyendo cada inicio a su
fuente, declarando el vacío del corpus y agregando P-02 con todos los campos de PC-12— y
**re-verificó todo el diff** (`product-review-002.md`), sin bloqueantes abiertos. Suite de
cierre, intento 2: **1926 passed, 5 skipped, rc=0**, 3878.91 s, **canario delta 0**; el intento
1 se interrumpió sin veredicto y se conserva como incidente, no como evidencia.

**Decisiones relevantes.**

- **Desafío protegido y separado del producto (D-1).** Motivo: un ensayo que recibe la clave o
  el producto no acredita nada. La clave se fijó antes (`cd2d57b3`), el registro se versionó
  antes (`4c822805`) y el primer informe se cerró **antes** del contraste (`d2307c42`, que
  contiene ambos con el informe íntegro). Trade-off aceptado: el ensayo es **de un solo tiro**
  —no se re-despacha— y por eso una cláusula de forma incumplida se declara en vez de
  corregirse.
- **La divergencia se documenta, no se resuelve (D-2).** Las dos posiciones incompatibles
  sobre quién aprueba los casos límite se conservan y se declara que el corpus no decide.
  Trade-off: el producto no es «un proceso operativo inequívoco», y eso es exactamente lo que
  el contrato promete.
- **Reparto de la evidencia (D-4) sin confundir registros.** El control estructural acredita
  resolubilidad de citas, inventario y anclas; la **fidelidad semántica** la sostienen la
  revisión de T6 y la re-verificación de T7. Un verde de control **no** se presenta como prueba
  de corrección documental.
- **Objeto declarado de T5 con precedencia sobre la frase genérica del rol (BN-1, resuelto en
  `plan-review-2-resolutions-2026-10-31.md`) y criterio único de lecturas (O-10, resuelto en
  `plan-review-3-resolutions-2026-10-31.md`)**: invalida lo que revela respuestas, no lo que
  enseña a revisar; toda lectura observada se registra y las no clasificadas se fundan una por
  una. La auditoría no observó lectura invalidante.
- **Sin mecanismo nuevo (D-5).** No se creó agente, rol, etapa, subfase, campo del estado ni
  selector documental: el piloto usó los campos y el procedimiento ya existentes de
  `010-001`/`010-002`. Trade-off: la promesa queda atada a la disciplina de despacho, no a una
  guarda mecánica.

**Evidencia.** **Cinco vueltas de `plan-review`**, cada una con sus resoluciones registradas:
`plan-review.md` (primera; B-1..B-4 y O-1..O-8, resueltas en
`plan-review-resolutions-2026-10-31.md`), `plan-review-002.md` (segunda; BN-1 y NB-1..NB-6,
en `plan-review-2-resolutions-2026-10-31.md`), `plan-review-003.md` (tercera; BN-2 y
O-9..O-12, en `plan-review-3-resolutions-2026-10-31.md`), `plan-review-004.md` (cuarta,
acotada al delta; BN-3 y O-13/O-14, en `plan-review-4-resolutions-2026-10-31.md`) y
`plan-review-005.md` (quinta, acotada al delta: veredicto **aprobable, sin bloqueantes**),
cuyo cierre es `plan-review-closure-2026-10-31.md`. Las decisiones **D-1..D-6** son del
**discovery** (`discovery-decisions-2026-10-31.md`), no del `plan-review`. También:
`preparation-record.md` (fijación e inspección previa); `test-audit.md`/`post-audit.md`
(selección y auditoría); `challenge-review.md` (informe original) y `challenge-contrast.md`
(§1 auditoría de lecturas, §2 coincidencias, §4.1 la no conformidad); `product-review.md` (F-1
de T6) y `product-review-002.md` (re-verificación sin bloqueantes); `tdd-t3-red.md`,
`tdd-t4-green.md`, `tdd-t7-review-fix.md`; copias durables en `evidence/t5/`, `evidence/t6/`,
`evidence/t7/` y `evidence/closing-suite/`. Commits: `cd2d57b3`, `4c822805`, `7fcca219`,
`d2307c42`, `6596e804`, cierre `a6a2104e`.

**Deuda técnica detectada.**

- **I-15 (nuevo, no conformidad de forma declarada):** el request de T5 no citó los commits de
  fijación que el contrato (§2.3, PC-03) exige. La fijación existe y es comprobable
  (`cd2d57b3` y `4c822805`, ambos antecesores de `d2307c42`), pero la cláusula de forma se
  incumplió; se registra y va al backlog del epic con condición de cierre (un chequeo en
  `prepare` o en el procedimiento de despacho, con test). **No se borra del registro ni se
  presenta como cumplida.**
- **I-14 (heredada, defecto del skill):** el bloque del test-writer le manda leer
  `references/documentary-contracts.md`, que su `read_scope` no admite (`skills/**` es
  `implementation`). Hoy lo cubre el contrato de la feature, que cita y aplica la norma.
- **I-8 (heredada, desviación declarada y decidida):** la lectura de la norma por `bash` en el
  AUDIT de T2, registrada en `audit-reading-deviation-2026-10-31.md`; no afectó la sustancia.
- **P-01 y P-02 siguen abiertos y declarados** (información faltante, condición de cierre,
  responsable y clasificación). No se resuelven aquí; el contrato promete documentarlos.
- **N-2 y N-3** quedan como observaciones opcionales aceptadas como límite, no corregidas, para
  no reabrir un producto ya re-verificado.
- **Intento 1 de la suite interrumpido sin veredicto:** se conserva completo en
  `evidence/closing-suite/attempt-1-interrupted/`; no es fallo de la suite ni evidencia de nada.
- **`deferred-hardening` de la spec §7 — seis ítems conservados y transcriptos en `closure.md`
  §4 bis, ninguno aplaza una promesa comprometida:** parser documental universal / formatos
  binarios / corpus de clientes (el piloto usa Markdown sintético); detección semántica
  automática (no sustituye el contraste independiente); generalización estadística o
  comparación de modelos (una muestra sembrada no la acredita); sandbox, vigilancia de accesos
  o prueba de ausencia de escrituras (no son capacidades del mecanismo); reparar I-8–I-13 o
  actualizar la instalación global (requieren sus contratos y autorizaciones); rendimiento,
  cobertura exhaustiva y combinatoria sin consecuencia contractual. **Ninguna exclusión permite
  omitir los tres hallazgos, la revisión del producto ni la aceptación** (spec §7). `closure.md`
  §4 registra además las desviaciones y deudas (I-15, la lectura por `bash` de I-8, el intento 1
  interrumpido, N-2/N-3 y I-14) con su destino.
- **Límites que no se convierten en garantías (PC-15):** la detección es sobre un **desafío
  declarado y sembrado**, no a ciegas; no se acreditan detección infalible, conducta general de
  modelos, errores espontáneos del productor ni fidelidad de un documento de cliente; la
  independencia es **contractual y de alcance**, no aislamiento técnico; el implementer no leyó
  el verificador pero vio nombres de casos, mensajes y valores de aserción al ejecutarlo —
  `pytest` no es un sandbox y no se promete aislamiento; la suite usó `--all` y 5 casos quedaron
  omitidos por variables de entorno ausentes, declarados en el `attempt.json`.
- **Deriva de la instalación global:** los agentes instalados no llevan la obligación documental
  mientras no se publique; publicar es decisión del dueño y este cierre no lo hizo.

**Next feature in queue.** La descomposición del `epic-010-documentary-specialization` queda
completa (010-000, 010-004, 010-001, 010-002 y 010-003 cerradas individualmente), así que **no
hay unidad siguiente en el plan**: lo que falta es la **integración de las cinco features y el
cierre del epic** según `docs/epics/epic-010-documentary-specialization/plan.md`, con sus
criterios de aceptación todavía sin marcar. El epic 010 **no** cierra con esta feature. Sigue en
la cola del epic: I-6, R-A, I-8, I-9, I-10, I-11, I-12, I-13, I-14, I-15 y la publicación
(orden del dueño). Mientras no se publique, todo despacho real sigue necesitando la toolchain del
repositorio (I-9).
```

---

## (2) `docs/progress.md`

**Dónde va:** como **primera viñeta bajo `## Done`** (línea 12), antes de `- **010-002-documentary-role-integration**`. **No hay línea que quitar de `## In progress`:** verifiqué que esa sección (líneas 5–10) solo contiene la viñeta de **Despliegue**; `010-003` nunca figuró allí, así que agregar la entrada es la transición completa. No se borra ni reordena ninguna entrada previa.

```markdown
- **010-003-documentary-pilot** (2026-10-31, epic 010 — **orden 4 del plan**;
  **aceptación funcional registrada por mandato HITL, no aprobada directamente por el
  dueño y NO publicada**) — un piloto recorrió el ciclo completo con un entregable
  documental trazable y evidencia **independiente** de detección de defectos. Contrato
  **v5** `f2dce9e0…d5e5` y plan **v6** `49ce6f81…2b04` pineados; producto
  `product/relevamiento.md` (`007af655ef926e98df26920792f48d4098136cfc1d2a347a0cc427da1ef40e0f`,
  corrección del candidato negativo contra `inventory-010-003-v1`: 14 citas, 10 anclas,
  10/10 artefactos fijados sin deriva). Commits: `cd2d57b3` (corpus, clave, muestras y
  verificador), `4c822805` (registro de preparación), `7fcca219` (producto, GREEN),
  `d2307c42` (informe del ensayo y contraste) y `6596e804` (corrección T7).
  **Detección acreditada:** el ensayo en sesión separada (`<session>`),
  **sin clave ni producto**, identificó **F-1/F-2/F-3 del ensayo (T5)** —afirmación como
  hecho sin respaldo, contradicción omitida y referencia existente que no sostiene— y el
  contraste dio **3/3 coincidencias y cero omisiones**, más tres extras no enumerados por la
  clave. **Corrección y re-verificación:** T6 encontró **el bloqueante F-1 de T6 (divergencia
  del inicio del plazo)**; T7 lo corrigió y **re-verificó todo el diff**
  (`product-review-002.md`), sin bloqueantes abiertos. **Medición:** 8 focales
  (`test_010_003_documentary_pilot.py`, `8 passed`), **40 regresiones** (11 de `010-001` +
  29 de `010-002`) y suite de cierre `--all` en intento 2: **1926 passed, 5 skipped, rc=0**,
  3878.91 s, **canario delta 0**; el intento 1 se interrumpió sin veredicto y se conserva como
  incidente. **Aceptación registrada bajo mandato HITL** (mandato del 2026-10-30, §1 y §3),
  **no** aprobación directa del dueño y **no** publicada: no hay push ni actualización de la
  instalación global. **Proceso:** **cinco vueltas de `plan-review`** (B-1..B-4 y O-1..O-8;
  BN-1 y NB-1..NB-6; BN-2 y O-9..O-12; BN-3 y O-13/O-14; y la quinta con veredicto aprobable
  sin bloqueantes), cada una con sus resoluciones registradas; D-1..D-6 son decisiones del
  **discovery**, no del `plan-review`. **Límites PC-15:** muestra **sembrada y sintética** con
  contrato que anuncia tres defectos y sus clases, así que se acredita **detección sobre un
  desafío declarado, no a ciegas**; no se demuestran detección infalible, conducta general de
  modelos ni **fidelidad de un documento de cliente**; la independencia es **contractual y de
  alcance, no aislamiento técnico**. **Deuda:** **I-15** (el request de T5 no citó los commits
  de fijación — no conformidad de forma declarada, la fijación existe y es comprobable), **I-14**
  (el test-writer no puede leer la norma que su bloque le manda leer) e **I-8** (lectura de la
  norma por `bash` en el AUDIT, declarada y decidida en
  `audit-reading-deviation-2026-10-31.md`); P-01 y P-02 **abiertos y declarados**; N-2/N-3
  aceptados como límite; `deferred-hardening` de la spec §7 (seis ítems) conservado y
  transcripto en `closure.md` §4 bis, sin aplazar ninguna promesa. El **epic 010 no cierra**
  con esta feature: falta la integración de las cinco y el cierre del epic. Detalle en
  `docs/specs/010-003-documentary-pilot/closure.md`, `structural-evidence.md`,
  `semantic-evidence.md` y `functional-acceptance.md`.
```

---

## (3) NO ADR

**Dónde va:** no se crea archivo en `docs/adr/` ni fila en la tabla de «Decisiones vigentes» de `docs/systemPatterns.md`. `systemPatterns.md` **no se toca**.

```markdown
## NO ADR

No hay decisión arquitectónica nueva que registrar. Las decisiones del piloto —desafío
protegido separado del producto, divergencia documentada y no resuelta, primer informe cerrado
antes de revelar, reparto de evidencia entre control estructural y revisión semántica, y la
regla de no introducir mecanismo nuevo (D-1..D-6, del **discovery**)— más la precedencia del
objeto declarado (BN-1) y el criterio único de lecturas (O-10), resueltas en las vueltas segunda
y tercera del `plan-review`, ya quedaron registradas en `spec.md` v5 y en `systemPatterns.md`.

La implementación no creó mecanismo, superficie ni contrato nuevo: usó un verificador de
feature y los campos y el procedimiento existentes, así que el cierre no cambia ninguna regla
vigente del proyecto.
```

---

## Role report

**Archivos modificados:** ninguno. `write_scope` es `[]` y el rol es read-only; los tres borradores se entregan como FINAL TEXT para que el orquestador los materialice tras la aprobación del usuario.

**Comandos ejecutados (exactos) y salida:**

| Comando | Salida |
|---|---|
| `python3 scripts/cdad_packet.py validate-request --project-root . --execution-context .cdad/executions/exec-010-003-documentary-pilot-001/execution.json --request .cdad/packets/010-003-documentary-pilot-scribe-memory-002/REQUEST.json` | sin salida, `rc=0` |
| `python3 scripts/cdad_packet.py validate-packet … --packet .cdad/packets/010-003-documentary-pilot-scribe-memory-002/PACKET.md` | sin salida, `rc=0` |
| `python3 scripts/cdad_packet.py render … --route C` | identificación de 8 campos idéntica byte a byte al bloque recibido |
| `cat .cdad/executions/exec-010-003-documentary-pilot-001/execution.json` | `schema_version: 2` (contexto v2, admisible en ruta C) |
| `sha256sum docs/specs/010-003-documentary-pilot/spec.md` | `f2dce9e0…d5e5` = contrato declarado ✔ |
| `sha256sum …/plan.md …/product/relevamiento.md …/tests/test_010_003_documentary_pilot.py` | `49ce6f81…2b04`, `007af655…0e0f`, `8e2a1878…5737` ✔ (coinciden con `structural-evidence.md` §1 y `functional-acceptance.md` §1) |
| `head -8 plan-review{,-002,-003,-004,-005}.md` | cinco vueltas: `342cb14f/ea71cb5f` (v2/v1), `76307105/d3a9be99` (v3/v2), `352e42a2/397a3975` (v4/v3), `b7d396ca/eca09528` (v5/v4), `49ce6f81/f2dce9e0` (v6/v5); la quinta: «Veredicto: **aprobable**» |
| `grep -on "O-[0-9]*" plan-review.md` / `plan-review-003.md` / `plan-review-004.md` | O-1..O-8 (1.ª), O-9..O-12 (3.ª), O-13/O-14 (4.ª); B-1..B-4 por encabezado en la 1.ª |
| `grep -n "^## D-" discovery-decisions-2026-10-31.md` | D-1..D-6 en el **discovery**, con títulos propios (desafío protegido, divergencia documentada, informe cerrado antes, reparto de evidencia, sin mecanismo nuevo, aceptación) |
| `grep -n "F-1" product-review.md` | `### F-1 (Required): divergencia sobre el inicio del plazo sin declarar`; `functional-acceptance.md` §2 lo nombra «F-1 (divergencia del inicio del plazo)» |
| `git log --oneline -1 cd2d57b3 4c822805 7fcca219 d2307c42 6596e804 a6a2104e` | los cinco commits existen con los mensajes declarados; HEAD = `a6a2104e` (cierre) |
| `grep -n "^## " docs/progress.md` / `sed -n 1,25p docs/activeContext.md` | `## In progress` solo con la viñeta de Despliegue; `## Done` empieza en `010-002`; `activeContext.md` tiene el `---` en la línea 5 y `010-002` como primera entrada |

**Correcciones aplicadas a los tres defectos del intento 1:** (1) **cinco** vueltas de `plan-review`, enumeradas con su par de hashes y sus resoluciones; (2) **D-1..D-6 atribuidas al discovery** y las resoluciones del `plan-review` nombradas por sus cinco documentos, con BN-1 y O-10 asignados a la segunda y tercera vuelta respectivamente; (3) los hallazgos del ensayo se nombran **«F-1/F-2/F-3 del ensayo (T5)»** y el de la revisión **«el bloqueante F-1 de T6 (divergencia del inicio del plazo)»**, sin la etiqueta «F-1-deadline» (que no es etiqueta de ningún documento; `product-review.md:76` lo rotula `F-1`).

**Fidelidad aplicada:** detección presentada como *sobre desafío declarado y sembrado*, nunca a ciegas ni como capacidad general; aceptación como **mandato HITL, no aprobación directa, no publicada**; P-01/P-02 dejados abiertos; I-15, I-14 e I-8 conservadas; `deferred-hardening` de la spec §7 transportado explícitamente (R6) con remisión a `closure.md` §4 bis recién agregada, y las desviaciones/deudas de §4 citadas con su destino.

**Commit:** ninguno — no commiteo; la aprobación es del usuario y la materialización git del orquestador.
