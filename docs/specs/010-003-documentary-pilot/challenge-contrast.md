# Contraste posterior del desafío — 010-003-documentary-pilot

Contraste del orquestador contra la clave, **después** de recibir y cerrar el
informe original en `challenge-review.md`. Este documento no reabre el informe ni
lo corrige: lo compara con la clave y registra coincidencias, omisiones y
extras.

## 1. Auditoría de las lecturas declaradas

El reviewer declaró sus lecturas en el propio informe. La auditoría las clasifica
contra las exclusiones del contrato (promesa C, tabla de O-10).

| Lectura declarada | Clasificación | Efecto |
|---|---|---|
| `REQUEST.json`, `PACKET.md`, `execution.json` | Plano de control del encargo | Ninguno: no son producto ni informes reveladores |
| `spec.md`, `documentary-contracts.md`, `verdict-tuple.md`, `inventory.md`, `s1.md`, `s2.md`, `negative.md` | Insumos autorizados | Ninguno |
| `stage-4-review.md` (parcial, por `grep`) | Referencia normativa de método | Se registra; **no invalida** |
| `find . -name cdad_packet.py` (nombres bajo `.cdad/evidence/`, truncado) | Listado de rutas, sin contenido | Ninguno: no se leyó contenido de artefacto excluido |
| Contexto automático de la sesión (asuntos de commits y el nombre `tdd-t4-green.md`) | Metadato del entorno, sin contenido | Ninguno: no reveló respuestas |
| `product/`, `oracle/`, `structural/`, `discovery.md`, plan, registros, informes, verificador | **No leídos** (declarado) | — |

**Veredicto: no hay lectura invalidante.** La independencia se acredita sobre la
evidencia disponible, con el límite ya declarado: examina lo declarado, no prueba
la ausencia de accesos no registrados ni constituye aislamiento técnico.

## 2. Coincidencia con la clave

| Entrada de la clave | Hallazgo del informe | Ubicación | Fundamento del informe | Resultado |
|---|---|---|---|---|
| Defecto 1 — afirmación como hecho sin respaldo | **F-1** | «Revisión del proceso», oración única | `s1`/`s2` completos: ningún fragmento trata revisión periódica, encuesta ni satisfacción; lo único «anual» es el legajo, que no se relaciona | **Coincide** |
| Defecto 2 — contradicción omitida | **F-2** | «Aprobación de casos límite», oración única | `s1-f02` (Jefe de Registro con visto bueno de Cumplimiento) frente a `s2-f03` (solo Dirección de Operaciones, sin visto bueno); el candidato afirma consenso y omite una posición | **Coincide** |
| Defecto 3 — referencia existente que no sostiene | **F-3** | «Archivo», oración única, enlace a `s1-f03` | `s1-f03` trata el plazo de respuesta, no el archivo; el respaldo real está en `s1-f04`, que el candidato no cita | **Coincide** |

**Omisiones: ninguna.** El primer informe contiene las tres clases con ubicación
y fundamento propios, sin haber recibido la clave ni el producto.

## 3. Extras del informe que la clave no exigía

| Extra | Naturaleza | Efecto sobre la acreditación |
|---|---|---|
| **O-1** — `s1-f04` y `s2-f05` difieren en la organización del legajo | Observación opcional; el informe se abstiene de calificarla de contradicción | Ninguno: no es una de las tres clases comprometidas |
| **O-2** — el candidato omite desde cuándo corre el plazo | Observación opcional; el informe no la trata como contradicción | Ninguno |
| **O-3** — el candidato no identifica el inventario por ruta e identificador | Bloqueante **frente a la convención del inventario**, no una de las tres clases de PC-02 | Ninguno sobre la detección; se registra como observación válida sobre el candidato negativo |

Los extras no sustituyen ni debilitan las tres coincidencias: agregan
observaciones que la clave no enumeraba, que es lo esperable de una revisión real.

## 4. Avisos del informe al orquestador

1. **El request de T5 no cita los commits de preparación y del registro.** Es
   cierto. El contrato (§2.3, PC-03) pide esa cita en el request. La fijación
   existe —commit de preparación `cd2d57b3` con el verificador, registro
   versionado en `4c822805`, ambos anteriores al despacho de T5—, pero la cita
   en el request se omitió. Se registra como **desviación del despacho**, no del
   ensayo: no afectó la independencia ni el informe. La cita queda en este
   contraste y en el registro de preparación, y los requests de T6 y T7 la
   incluirán.
2. **El `spec.md` conserva el estado «pendiente de revisión y aprobación».** Es
   la convención del repositorio: el arquitecto redacta el borrador con ese
   estado y la aprobación se registra en el estado y en el gate, no editando el
   contrato pineado. `010-002` se cerró con la misma convención. Se declara como
   límite de forma, no como defecto de esta unidad.

## 5. Conclusión

**La detección semántica se acredita sobre esta muestra.** El informe original,
cerrado antes de cualquier revelación, identificó y fundamentó las tres clases de
defecto con localizadores contra el corpus, sin clave y sin producto. La
auditoría de lecturas no encontró contaminación. La muestra es sembrada y
sintética, el contrato anticipa las tres clases y la detección no es a ciegas ni
infalible: se acredita sobre este desafío, no como capacidad general.

El ensayo queda cerrado con una desviación de despacho declarada (la cita de
commits en el request) que no altera el resultado.
