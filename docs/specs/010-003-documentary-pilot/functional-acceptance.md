# Aceptación funcional — 010-003-documentary-pilot

Registro 3 de los tres que exige PC-14. Decisión de la autoridad habilitada sobre
la versión identificada, con sus pendientes admisibles y sus límites.

## 1. Versión aceptada

| Elemento | Identidad |
|---|---|
| Feature | `010-003-documentary-pilot` |
| Contrato | `spec.md` v5, `f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5` |
| Plan | `plan.md` v6, `49ce6f813aeb4e0bea0ff4f44d541a48deef29dc42f2af5aa6e05e5bf3352b04` |
| Producto | `product/relevamiento.md`, `007af655ef926e98df26920792f48d4098136cfc1d2a347a0cc427da1ef40e0f` |
| Commit del producto corregido | `6596e804654f9b76d3e7710c2011b312350fe75d` |
| Cierre estructural | `structural-evidence.md` |
| Cierre semántico | `semantic-evidence.md` |
| Suite de cierre | intento 2: 1926 passed, 5 skipped, rc=0, canario delta 0 |

## 2. Qué se acepta

- El **relevamiento corregido** como producto documental del piloto: trazable al
  inventario `inventory-010-003-v1`, con las dos posiciones incompatibles
  conservadas y la incertidumbre declarada.
- La **detección semántica** acreditada sobre esta muestra: el ensayo independiente
  identificó y fundamentó las tres clases de defecto sin clave ni producto, y el
  contraste dio tres coincidencias y cero omisiones.
- La **corrección y la re-verificación**: F-1 (divergencia del inicio del plazo)
  corregido y re-verificado sobre todo el diff, sin bloqueantes.
- La **evidencia estructural**: control focal de 8 casos, 40 regresiones y la
  suite completa de cierre, sobre la misma versión.

## 3. Pendientes admisibles (no bloqueantes)

| Pendiente | Estado aceptado |
|---|---|
| **P-01** — quién aprueba los casos límite y si requiere visto bueno | Abierto y declarado, con información faltante, condición de cierre y responsable. El contrato promete documentar la divergencia, no resolverla. |
| **P-02** — inicio exacto del plazo cuando la solicitud se completa después | Abierto y declarado con los mismos campos. |
| **N-2, N-3** — precisión de redacción («esta nota», «las formulaciones del inicio») | Observaciones opcionales del revisor; no afectan ninguna promesa y no se corrigen para no reabrir un producto ya re-verificado. |
| **I-15** — el request de T5 no citó los commits de fijación | No conformidad de forma declarada: la fijación existe y es comprobable (`cd2d57b3`, `4c822805`), pero la cita en el request se omitió. Se acepta como desviación registrada, no se presenta como cumplida. Va al backlog. |
| **Lectura de la norma por `bash` en el AUDIT** | Desviación de I-8 registrada y decidida en `audit-reading-deviation-2026-10-31.md`; no afectó la sustancia. |
| **Línea de estado del `spec.md`** | Conserva «pendiente de revisión y aprobación»: la aprobación vive en el estado y el gate, no en el contrato pineado (misma convención que `010-002`). |

## 4. Qué no se acepta como demostrado

- **Detección a ciegas.** El contrato anuncia tres defectos y sus clases: se
  acredita detección sobre un desafío declarado.
- **Detección infalible, conducta general de modelos o errores espontáneos del
  productor.** No se midieron.
- **Fidelidad de un documento de cliente.** El corpus es sintético.
- **Aislamiento técnico del ensayo.** La independencia es contractual y de
  alcance; la auditoría examina lo declarado, no prueba la ausencia de accesos no
  registrados.
- **Fidelidad semántica por el control estructural.** El verde acredita
  resolubilidad de citas, inventario y anclas; la fidelidad la sostienen las
  revisiones.

## 5. Autoridad de la decisión

Aceptación ejercida por el orquestador **en nombre del dueño** bajo el mandato
HITL registrado en
`docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md`
(§1 y §3), en tanto la feature implementa la descomposición y el alcance ya
aprobados del epic (`010-003`: «un piloto recorre el ciclo con un entregable
trazable y evidencia independiente de detección de defectos estructurales y
semánticos»). **No** es una aprobación directa del dueño, y se registra como tal.

No se publica, no se hace push y no se actualiza la instalación global: eso sigue
reservado a una instrucción explícita del dueño.

## 6. Decisión

**Aceptada con pendientes admisibles y una no conformidad de forma declarada.**
No hay bloqueantes abiertos: el producto es trazable, la detección se acredita
sobre la muestra, la corrección se re-verificó y la suite de cierre pasó. Lo que
no se cumple —la cita de los commits en el request de T5— queda registrado y
trasladado al backlog, sin borrarlo del registro.
