# plan-review: 010-004 packet-dispatch-ergonomics, PLAN v2

- **Objeto:** `docs/specs/010-004-packet-dispatch-ergonomics/plan.md`. Forma: plan. Kind: draft-plan. plan_version 2.
- **Digest:** `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685`. Recalculado con `sha256sum` al inicio y al final; coincide con el contrato.
- **Spec companion (no reabierta):** `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`.
- **Packet:** `010-004-packet-dispatch-ergonomics-reviewer-plan-review-007` · ejecución `exec-010-004-packet-dispatch-ergonomics-001` · HEAD `ece189cc5cb6e973014a4ea8a3048cacdb44e043`.

**Dictamen:** esto es una revisión, no una aprobación. Hay **0 BLOCKING** y **1 OPTIONAL**.

- **P-1:** cerrado en todas sus condiciones.
- **P-2, P-3 y P-4:** tratados y cerrados.
- **Lo que debe saber quien apruebe:** T1 queda libre, pero **T2 se detendrá con certeza** en su primer despacho, hasta que Pablo decida cómo emitir un POST-AUDIT de una sola subfase (hallazgo V2-1). La parada es segura y no acredita ningún bypass. Aprobar v2 tal como está significa aprobar esa parada conocida.

## Intake (ruta C)

```
P=.cdad/packets/010-004-packet-dispatch-ergonomics-reviewer-plan-review-007
E=.cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json
python3 -I scripts/cdad_packet.py validate-request --project-root . --execution-context $E --request $P/REQUEST.json → rc=0
python3 -I scripts/cdad_packet.py render --project-root . --execution-context $E --request $P/REQUEST.json > /dev/shm/render-007.out → rc=0
cmp /dev/shm/render-007.out $P/PACKET.md → rc=0
sha256 de ambos → 02b219caae43010178d3719cdbb95a019ef91572129056e43170f416fba34907
python3 -I scripts/cdad_packet.py validate-packet --project-root . --execution-context $E --request $P/REQUEST.json --packet $P/PACKET.md → rc=0
```

La identificación despachada (packet_id, execution_id, contrato con su sha256 y metadatos `spec_*`) coincide con REQUEST.json y PACKET.md. A diferencia de `-006`, este bloque sí trae los `spec_*`.

## Cierre trazado de P-1

| Condición (`implementation-plan-review.md:67-70` y objetivo del packet) | Estado | Evidencia en PLAN v2 |
|---|---|---|
| T2 abre con POST-AUDIT tras T1 y antes de GREEN | Cerrada | `plan.md:19,30,51,62,105,108` |
| Tres dispatches, sesiones y paquetes separados | Cerrada | `:19` (literal), `:30`, `:62`, `:85`, `:108` |
| T5 ya no usa POST-AUDIT | Cerrada | `:12`, `:33`, `:132`, `:135` |
| Relevancia obligatoria en T6, por reviewer Stage 4, en sesión distinta del autor de los tests | Cerrada | `:34`, `:144`; admitido por `stage-3-tdd.md:45-47,270` |
| Aprobación del AUDIT explícita y sin autoaprobación | Cerrada | `:55`, `:99-100`; concuerda con `test-writer-audit.md:1` («for user approval») y con el límite del mandato en `execution.md` |
| Tabla, prosa y owners concordantes | Cerrada | Pasos `:8-13`, tabla `:29-34`, prosa `:19,51,55,62`, JSON `:85,99-100,105-109,132-136,144` |

**Corrección a la condición original:** `implementation-plan-review.md:68` admitía «post-audit + RED». Esa alternativa no era conforme, porque `orchestrator.md:126-131` y `spec.md:436` (INV-01) prohíben dos subfases por invocación. Separar en tres dispatches, como hizo el architect, es correcto.

**Citas de `:38` verificadas:** `handoff-prompts.md:220-225,334,347` y `test-writer-post-audit.md:1` contienen la combinación citada.

## Estado de los opcionales

| Hallazgo | Estado | Evidencia |
|---|---|---|
| **P-2** | Tratado. T4 es el gate transversal anticipado; T6 conserva el cierre, y la equivalencia queda sujeta a `re-entry.md`. Esto satisface la condición de `:84`. | `plan.md:74`, `:136`; `stage-3-tdd.md` regla 2 |
| **P-3** | Tratado. PC-08a queda en T3 como regresión existente, sin RED artificial, en línea con `spec.md:465`. | `plan.md:31`, `:114` |
| **P-4** | Tratado. El detalle viaja en el paquete sin `--plan-task`. `prepare` admite esa vía: `plan_task` es opcional (`cdad_packet.py:1600-1615`). | `plan.md:23`, `:109` |

N-4, N-5 y N-6 siguen abiertos y postergados (`plan.md:79`). No los toqué.

## Hallazgos

**Derivación del bucket:** objeto completo, spec y convenciones en contexto, y citas exactas en cada fundamento. Son 3 puntos, es decir `h`, contando el objeto completo como «diff completo», igual que en la revisión anterior. La familia del modelo autor es desconocida y puntúa 0.

### V2-1: la devolución de `:38` es válida, pero describe como condicional una parada segura y T2 no la declara

**Verdict: OPTIONAL · Bucket: h · Severity: Consider (correctness / usabilidad)**

**Evidencia:**
- `plan.md:38` dice «Un render que **aún** combine subfases se devuelve al orquestador». Hoy eso no es una eventualidad.
- `render_packet` compone siempre `substages/{role}-{substage}.md` (`cdad_packet.py:1797-1800`).
- La plantilla dice «…then add contract-mapped RED tests» (`test-writer-post-audit.md:1`).
- Comprobado sobre paquetes reales: los PACKET.md de `008-002-…-post-audit-002` y `008-003-…-post-audit-003` contienen tanto el hash de la plantilla vigente (`041f1a8c…`) como ese texto.
- Ninguna unidad anterior a T2 produce una instrucción de una sola subfase:
  - La plantilla se clasifica como `implementation` (`validate-policy --classify`).
  - No figura en las superficies de T2 (`plan.md:61-62`).
  - El plan solo la menciona en `:38`, para decir que no se copie.
  - Aunque §3 de la spec la cubriera como «instrucciones de despacho», T4 llegaría después de T2.
- El orquestador no tiene salida propia:
  - Despachar el render combinado incumple `:38` y `:19`.
  - Parchear bytes está prohibido por `:38`.
  - Editar la plantilla o volver a combinar subfases cambia alcance o plan, y eso «vuelve al owner» (`:23`).
- T2 tampoco lo declara. Su `uncertainty` y su `resolves_when` (`:107,109`) no mencionan esta decisión, aunque la regla de detalle progresivo (`stage-2-specification.md:154-157`) pide declarar la incertidumbre con owner y condición de resolución.

**Validez del procedimiento:** es **válido**.
- Falla cerrado, no parchea, no autoriza bypass y, leído junto con `:23`, termina en el owner.
- No exige producto adicional.
- Por eso no es BLOCKING: no hay camino abierto para despachar el render combinado ni para decidir sin el owner, y T1 no se ve afectada.
- No exijo modificar la plantilla: sería pedir producto no aprobado.

**Consecuencia:**
- Tras un AUDIT aprobado, T2 se detiene con certeza. No se rompe ninguna promesa; el coste es una decisión más de Pablo.
- La redacción invita a tratarlo como algo que el orquestador resuelve solo.
- El riesgo concreto es repetir el patrón 008, donde un objetivo acotado convivía con la plantilla combinada. `:38` lo cierra para esta feature, pero el plan no nombra ese patrón.

**Condición de cierre (si Pablo decide aplicarlo):** sin cambio de producto, el plan cumple estas tres cosas:
1. Afirma que hoy todo render `post-audit` combina subfases.
2. Nombra a Pablo como quien decide la vía antes del primer despacho POST-AUDIT.
3. Refleja esa decisión en `uncertainty` y `resolves_when` de T2.

También basta con que Pablo registre esa decisión junto a la aprobación del plan. Este hallazgo no prolonga el ciclo: aplicarlo o descartarlo es decisión de Pablo.

## Revisado sin hallazgo

- **Regresiones de la corrección v2:** dependencias lineales T1→T6 sin cambios y 6 tareas (T1 `next`, T2–T6 `planned`). No se reabre la spec.
- **Promesas:** la asignación de PC no pierde ninguna.
- **Límites:** las exclusiones `spec.md:513-524` se mantienen.
- **Evidencia del architect:** rotulada como histórica no normativa (`plan.md:153`).

**FYI, sin hallazgo:** `plan.md:74` dice «responsable de integración» sin nombrar rol. El paquete T4 lo concreta por diseño (`common.md`, `spec.md:468`).

## Abstentions

- **Decisiones vigentes / `docs/adr/`:** el packet no declara `current_decisions` y no revisé ese conjunto.
- **Tests:** no ejecutados, conforme al objetivo. Las referencias se comprobaron por lectura, y los tests citados de T1 no se reverificaron en esta pasada: `plan.md` no los cambió en esas líneas y ya se habían confirmado en `-006`.
- **Lista exhaustiva de tests afectados:** corresponde a T1.
- **Tareas `planned`:** juzgadas solo por objetivo, dependencias, incertidumbre, owner y condición de resolución.
- **Validez de `prepare --substage post-audit` tras T1 con el plan aprobado:** no ejecutada, porque publicaría un paquete.
- **Si §3 de la spec alcanza la plantilla de subfase:** no lo resuelvo, porque interpretarlo le corresponde al owner. La conclusión de V2-1 es la misma en ambas lecturas.
- **Familia del modelo autor:** desconocida.

## Evidencia

- **Archivos modificados:** ninguno (`write_scope: []`). **Commit:** ninguno.
- **Temporal:** `/dev/shm/render-007.out`, fuera del repo, eliminado tras la comparación.
- **Comandos adicionales al intake:**
  - `read` de las seis entradas.
  - `sed`, `grep` y `cat` sobre `orchestrator.md`, `handoff-prompts.md`, `stage-2-specification.md`, `stage-3-tdd.md`, `stage-4-review.md`, `re-entry.md`, `execution.md`, los `packets/substages/test-writer-*.md`, `cdad_packet.py`, `spec.md` y los paquetes 008.
  - `python3 -I` de solo lectura sobre REQUEST.json de los paquetes 008.
  - `python3 -I scripts/cdad_packet.py validate-policy --classify …`.
  - `git log`.
- **Error de comando:** una ayuda inicial con `validate --help` devolvió error: ese subcomando no existe. No tuvo efecto.
- **No ejecutado:** tests, suite, implementación, generación, instalación ni push.
- **Estado final:**
  - `plan.md` → `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685`
  - `spec.md` → `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`
  - HEAD → `ece189cc5cb6e973014a4ea8a3048cacdb44e043`
  - `git diff --exit-code` y `git diff --cached --exit-code` → 0
  - `git status --short` → solo `?? docs/specs/010-000-continuity-relative-root/discovery.md`, ya presente antes

**Plan no aprobado: la aprobación sigue pendiente de Pablo como decisión separada. Ni esta revisión, ni el receipt, ni la materialización la acreditan, y esta revisión no autoriza implementación.**