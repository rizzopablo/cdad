# Cierre — 010-003-documentary-pilot

Índice de la evidencia, de los registros y de los límites con que la feature se
cierra. No sustituye la aceptación: la decisión está en
`functional-acceptance.md`.

## 1. Los tres registros

| Registro | Documento | Contenido |
|---|---|---|
| 1. Estructural | `structural-evidence.md` | versión medida, integridad de la fijación, RED, control focal de 8 casos, 40 regresiones, suite de cierre con sus dos intentos, límites del control |
| 2. Semántico | `semantic-evidence.md` | cadena de custodia, independencia del ensayo, detección de los tres defectos, contraste con la clave, revisión del producto, corrección y re-verificación, desviaciones |
| 3. Aceptación | `functional-acceptance.md` | versión aceptada, pendientes admisibles, lo que no se acepta como demostrado, autoridad y decisión |

Documentos de soporte: `preparation-record.md` (fijación), `test-audit.md` y
`post-audit.md` (selección y auditoría de la prueba), `challenge-review.md`
(informe original), `challenge-contrast.md` (contraste y auditoría de lecturas),
`product-review.md` y `product-review-002.md` (revisión y re-verificación),
`tdd-t3-red.md`, `tdd-t4-green.md` y `tdd-t7-review-fix.md` (informes de rol),
`audit-reading-deviation-2026-10-31.md` (desviación declarada). Las copias
durables de requests, paquetes, recibos y sesiones están en `evidence/t5/`,
`evidence/t6/`, `evidence/t7/` y `evidence/closing-suite/`.

## 2. Mapa de postcondiciones

| PC | Evidencia decisiva | Estado |
|---|---|---|
| **PC-01** | inventario `inventory-010-003-v1`; 10/10 artefactos con digest coincidente (`structural-evidence.md` §2); declaraciones sintéticas en inventario, fuentes y candidato; control de bidireccionalidad | cumplida |
| **PC-02** | candidato negativo con las tres clases de defecto; inspección previa del orquestador en `preparation-record.md`; las tres clases encontradas por el ensayo | cumplida |
| **PC-03** | clave fijada en `cd2d57b3` y no reescrita (hash `91c277c1…` estable); registro versionado en `4c822805`; anterioridad comprobable por ascendencia. **La cita de ambos commits en el request de T5 no se cumplió** | cumplida en sustancia; **no conformidad de forma declarada** (I-15) |
| **PC-04** | control `test_broken_locator_is_rejected_with_document_reference_and_cause` | cumplida |
| **PC-05** | control `test_corrected_locator_is_accepted_and_the_pair_differs_only_in_the_locator` | cumplida |
| **PC-06** | control `test_semantically_defective_candidate_is_structurally_accepted`; su mensaje acredita resolubilidad, no persistencia | cumplida |
| **PC-07** | sesión `<session>`; request y paquete con scopes recortados; sin clave, producto ni informes reveladores (`semantic-evidence.md` §2) | cumplida |
| **PC-08** | informe original con F-1, F-2 y F-3, localizadores y fundamento contra el corpus | cumplida |
| **PC-09** | informe cerrado antes del contraste; `challenge-review.md` + `challenge-contrast.md` en `d2307c42`; request, paquete, recibo y fila de sesión copiados | cumplida |
| **PC-10** | producto separado; 14 citas, todas a fuente inventariada y ancla registrada; control y revisión | cumplida |
| **PC-11** | tres correcciones verificadas en T6 y re-verificadas en T7; ambas posiciones conservadas | cumplida |
| **PC-12** | P-01 y P-02 con información faltante, condición de cierre, responsable y clasificación; sin propuestas presentadas como hechos | cumplida |
| **PC-13** | T6 con un bloqueante real (F-1); T7 corrigió y re-verificó todo el diff; sin bloqueantes abiertos | cumplida |
| **PC-14** | los tres registros de §1, enlazados y separados; recibos de transporte no se usan como aceptación | cumplida |
| **PC-15** | límites de §3 de este documento | cumplida |

## 3. Límites que el cierre declara (PC-15)

- La muestra es **sembrada y sintética**; el contrato del ensayo anuncia tres
  defectos y sus clases. Se acredita **detección sobre un desafío declarado**, no
  detección a ciegas.
- Se acredita sobre **esta** muestra: no se demuestran detección infalible,
  conducta general de modelos, errores espontáneos del productor ni fidelidad de
  un documento de cliente.
- La independencia del ensayo es **contractual y de alcance**, no aislamiento
  técnico; la auditoría examina lo declarado.
- El **control estructural** acredita resolubilidad de citas, inventario y anclas,
  no fidelidad semántica.
- El **implementer no leyó el verificador** pero sí vio nombres de casos, mensajes
  y valores de aserción al ejecutarlo; `pytest` no es un sandbox y no se promete
  aislamiento.
- La suite completa se ejecutó con la selección `--all`; 5 casos quedaron
  omitidos por variables de entorno ausentes, declarados en el `attempt.json`.

## 4. Desviaciones y deudas

| Item | Naturaleza | Destino |
|---|---|---|
| I-15 — el request de T5 no citó los commits de fijación | no conformidad de forma declarada | backlog del epic, unidad de procedimiento |
| Lectura de la norma por `bash` en el AUDIT (I-8) | desviación declarada y decidida | `audit-reading-deviation-2026-10-31.md`; I-14 en backlog |
| Intento 1 de la suite interrumpido sin veredicto | incidente conservado; no es fallo ni evidencia | `evidence/closing-suite/attempt-1-interrupted/` |
| N-2, N-3 | observaciones opcionales de redacción | aceptadas como límite, no corregidas |
| I-14 — el test-writer no puede leer la norma que su bloque le manda leer | defecto del skill | backlog del epic |

## 4 bis. `deferred-hardening` (spec §7), conservado en el cierre

Ninguna exclusión de la spec aplaza una promesa comprometida; se transcribe para
que el cierre no las omita (R6):

| No comprometido | Motivo |
|---|---|
| Parser documental universal, formatos binarios y corpus de clientes | el piloto usa Markdown sintético y una convención acotada |
| Detección semántica automática | no sustituye el contraste independiente comprometido |
| Generalización estadística o comparación de modelos | una muestra sembrada y una sesión no acreditan esas conclusiones |
| Sandbox, vigilancia de accesos o prueba de ausencia de escrituras | no son capacidades del mecanismo existente |
| Reparar I-8..I-13 o actualizar la instalación global | requiere sus contratos y autorizaciones; aquí se respetan sus límites |
| Rendimiento, cobertura exhaustiva y combinatoria sin consecuencia contractual | no protegen otra promesa observable del piloto |

## 5. Estado de la feature y del epic

`010-003-documentary-pilot` **cierra** con su aceptación registrada. El
`epic-010-documentary-specialization` **no** cierra con esta feature: falta la
integración de las cinco features y el cierre del epic según
`docs/epics/epic-010-documentary-specialization/plan.md`. No se publica, no se
hace push y no se actualiza la instalación global.
