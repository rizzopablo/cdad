# Deuda de 005-014-closure-replay

Consolida lo declarado por la unidad: la deuda de la spec (§6: E-1..E-6), los opcionales de la review
(O-1..O-4) y los límites del arreglo. Cada ítem con su motivo y su condición de cierre. **Nada de esto
bloquea el cierre**: por el criterio de review vigente 2026-10-12, es mejora o variante sin impacto material
sobre el resultado, la evidencia o el uso previsto.

## Deuda de la spec (§6)

| Id | Deuda | Motivo / condición de cierre |
|---|---|---|
| **E-1** (priorizada) | `gate` **ignora** `--feature` en silencio: `gate --feature X` con B activa registra una entrada `feature: B` pinneando el `contract_path` de X — desvío silencioso; la entrada queda huérfana (nunca autoriza: PD-8(b) exige `docs/specs/<feat>/spec.md`). | **Arreglo distinto** al de esta unidad (la fila manda a deuda lo que no es el mismo arreglo). Se cierra con una unidad que haga actuar/validar `--feature` en todas las clases, con RED. |
| **E-2** (priorizada) | Replay tras un **cambio** de feature activa: la identidad incluye `execution_id` y `open-unit` acuña una ejecución nueva, así que aun con `--feature X` el payload lleva otra ejecución → otra clave → no hay no-op. | Es una cuestión de **identidad (PD-10)**, no de orden → fuera de la fila. Se cierra con una unidad que decida comparar el payload sin `execution_id` o buscar la ejecución de la feature, con RED. |
| **E-3** | El chequeo feature↔ejecución de `validate-state` **no** se replica en `register_transition`: con `active_feature` presente, la resolución no compara contra `state.execution.feature_id`. | El payload lleva `feature_id` y `execution_id`, y PD-24/PD-25/PD-27 hacen de un `--feature` desalineado un rechazo cerrado; replicarlo ampliaría el alcance. Se cierra si un caso real lo exige. |
| **E-4** | Una entrada `closure` registrada con la **fórmula anterior** de la clave (sin `transition_key_payload`) **no** se reconoce como no-op; con la feature cerrada, PD-25 la rechaza. | D-12 de 005-012 no se cubre; no se migra el state ni se recomputan claves históricas. Se cierra si aparece una entrada histórica que deba reconocerse. |
| **E-5** | Predicado `_packet_has_receipt` (**directorio**) vs `_durable_receipt` (**archivo** `receipt.json`). | Divergencia de predicado **no** relacionada con esta unidad (anotada por el discovery §3.6). Se cierra con una unidad propia sobre PD-8(a), con RED. |
| **E-6** | La rama «ninguna de las tres» de PD-22 (sin `--feature`, `active_feature` nulo y `state.execution.feature_id` ausente/vacío) **no** tiene caso propio en el focal. | Fallback defensivo: en un state v2 bien formado la clave `execution` se escribe con `feature_id`. La review comprobó que **funciona**, lo que no la convierte en cubierta. Se cierra con un focal del binding malformado. |

## Opcionales de la review (2026-10-14)

| Id | Hallazgo | Bucket | Disposición |
|---|---|---|---|
| **O-1** | La rama cerrada/sin-activa **no exige** `--closure-path`: la omisión cae en PD-25/PD-27(c) (clave sin cierre) en vez del mensaje de requisito de PD-9. Ambos caminos son rc=2 fail-closed, sin `open-unit` y sin efectos. | m | **Deuda.** Se cierra exigiendo PD-9 antes del cómputo de identidad en la rama, o declarando en la spec que la omisión produce PD-25/PD-27(c). |
| **O-2** | `--feature ''` se trata como ausente: el cierre procede contra la feature resuelta (consistente con la convención preexistente de `late-delivery`); no hay desvío a otra feature. | m | **Deuda.** Se cierra rechazando el valor vacío con `state incoherent` o declarando la convención «vacío = ausente». |
| **O-3** | El «límite declarado» de PD-23 se extiende a los `--artifact` citados: un artefacto borrado bloquea el replay con `evidence missing` en vez de no-op. | m | **Deuda.** Se cierra ampliando la frase del límite para incluir los `--artifact` citados. |
| **O-4** | El mensaje de PD-25 nombra `--transition late-delivery` pero no el paso `receive --late` de la ruta declarada. | l | **Deuda.** Se cierra nombrando los dos pasos (el operador que siga sólo el mensaje recibe el diagnóstico exacto en el paso siguiente). |

## Límites del arreglo (declarados, no deuda accionable)

- **Un replay legítimo es no-op aunque el mundo haya cambiado** después del cierre (contrato editado, recibo
  borrado, delegación revocada): consecuencia de que, en la rama de feature cerrada, la identidad decide
  antes que PD-8 y la autoridad.
- **El documento de cierre citado debe seguir existiendo**: la identidad lleva su digest resuelto (PD-20); si
  falta, el replay falla cerrado con `evidence missing` en vez de ser no-op.
- **La mitad «árbol» de INV-7 no se asertó**: lo verificado es el state byte a byte (misma salvedad que
  declaran los focales de 005-012: el lock/cleanup crea y borra su archivo transitorio).
- **El comportamiento nuevo no existe en la versión instalada** hasta el despliegue (del dueño): el uso
  previsto en un proyecto real no está ejercido todavía.
