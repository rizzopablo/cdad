# 008-003 — Decisor compartido de ciclo de vida

**Estado:** Draft — pendiente de aprobación del dueño.
**Autoridad:** `docs/epics/epic-008-suite-coherence/plan.md`, contrato de unidad aprobado y decisión HITL del encargo: opción A del discovery.

## 1. Resultado esperado

Packet, continuidad y recepción decidirán identidad, propietario, autoridad y elegibilidad mediante un núcleo compartido de decisiones puras. Los consumidores conservarán lectura, comprobación física de evidencia, serialización y publicación.

El cambio debe retirar las ramas decisorias migradas: compartir constantes o envolver las implementaciones actuales **no satisface** esta especificación.

No agrega capacidades del ciclo, otro registro ni otro recibo.

## 2. Superficie verificada

Todas las referencias P/C/R siguientes pertenecen a `skills/cdad-cycle/scripts/`.

| Superficie | Evidencia existente |
|---|---|
| Identidad y autoridad de packet | `cdad_packet.py:2552-2620`, `_validate_v2_vigency` |
| Guarda de suspensión | `cdad_packet.py:704-706`, `_suspended_unit_for` |
| Identidad y autoridad de continuidad | `cdad_continuity.py:286-417`, `:569-580` |
| Escritura y comparación de continuidad | `cdad_continuity.py:963-1093`, `plan_write`, `_plan_write`, `_run_write` |
| Cierre durable y replay | `cdad_continuity.py:1452-1535`, `close_durable_receipt` |
| Resolución legacy de propietario | `cdad_continuity.py:2305-2318`, `_execution_feature` |
| Guarda de continuidad por CLI | `cdad_continuity.py:2852-2865` |
| Recepción normal/tardía y replay | `cdad_result.py:516-545`, `:608-726`, `_late_vigency`, `receive` |
| Transición y publicación de packet | `cdad_packet.py:7458-7595`, `register_transition` |

Estas funciones son interfaces existentes; el núcleo descrito abajo es una **interfaz nueva propuesta**, no una API ya disponible.

## 3. Alcance

**Incluido:**

- Resolver identidad y propietario a partir de evidencia concordante.
- Clasificar ejecución gestionada frente a standalone/legacy usando evidencia existente.
- Unificar el criterio de autoridad vigente y la guarda de suspensión.
- Decidir elegibilidad de operaciones nuevas, replay y conflicto.
- Integrar el criterio en los bordes CLI **y funciones invocables directamente** de P/C/R que deciden estas materias.
- Retirar sus decisiones locales migradas.

**Excluido:**

- Tabla `termination/delivery`: permanece con sus dueños actuales en `cdad_dispatch`/`cdad_delegate` y su documentación canónica. No se mueve ni se declara unificada por esta feature.
- Coordinación de escritores, nuevos locks y reparación de aprobaciones.
- Sustitución de almacenamiento, publicación transaccional o validadores físicos.
- Selección de modelos, despacho obligatorio por paquete y CI.
- Reescritura de historia, claves o especificaciones cerradas.

## 4. Modelo de decisión

### 4.1 Separación entre hechos y política

El núcleo recibirá hechos y operación explícitos y devolverá una decisión sin leer archivos, escribir, consultar el reloj ni importar consumidores para ejecutar sus decisiones anteriores.

Los consumidores obtendrán y verificarán:

- Contexto y registro canónico de ejecución.
- Request, descriptor y recibo cuando correspondan.
- Binding del estado y registro de unidades suspendidas.
- Delegación, referencia de autoridad y existencia de su fuente.
- Evidencia durable, digests y cadena demostrable.

La fecha de evaluación y el resultado de comprobaciones físicas serán entradas explícitas. La forma Python concreta y los nombres del módulo y sus tipos se decidirán durante implementación; no se impone un framework.

Se elige este núcleo frente a un reducer universal porque la política compartida no exige reemplazar las publicaciones existentes. Tampoco se aloja otra fachada en packet: las reglas migradas deben tener un solo dueño.

### 4.2 Identidad y propietario

La identidad suministrada selecciona el objeto que se solicita examinar; **no acredita su propietario**.

Las identidades presentes en fuentes aplicables deberán concordar. En particular:

- `execution.id` y `execution_id`, si ambos existen, no pueden discrepar.
- Contexto, registro canónico, request, descriptor y recibo deberán concordar en los campos de identidad que declaran para la operación.
- El estado activo no sustituye al propietario de una ejecución histórica o suspendida.
- La unidad activa distinta no constituye por sí sola contradicción: recepción tardía y replay pueden pertenecer legítimamente a otra unidad.

El propietario se resolverá del binding acreditado por evidencia concordante. Ante contradicción o falta de evidencia necesaria para producir un efecto gestionado, se rechazará antes de publicar.

La ausencia de un campo opcional no equivale a contradicción. La compatibilidad legacy no autoriza inventar bindings ni atribuir historia a la unidad actualmente activa.

### 4.3 Autoridad y elegibilidad

Habrá un único criterio semántico de autoridad para los hechos equivalentes:

- Revocación presente o estado explícitamente incompatible: no vigente.
- Fecha estructurada inválida: desconocida; fecha vencida: no vigente.
- Delegación sin fecha: puede vencer por eventos, conforme a su declaración estructurada.
- Para una operación gestionada que requiere delegación de epic: scope y epic concordantes, fuente declarada y verificable.
- `unknown` no autoriza efectos nuevos que requieren autoridad.
- Standalone no adquiere artificialmente el requisito de delegación de epic.
- Las aprobaciones específicas de rol/contrato mantienen sus verificadores existentes; el decisor no las concede.

`active` y `current` no podrán representar políticas distintas. Los formatos públicos existentes se conservarán mediante adaptación de presentación, sin volver a decidir vigencia.

La suspensión bloqueará efectos nuevos sobre el propietario suspendido. No bloqueará operaciones de otra unidad sólo por existir una suspensión.

### 4.4 Replay, conflicto y efecto nuevo

Orden obligatorio:

1. Comprobar identidad y evidencia necesaria.
2. Reconocer replay durable o conflicto dentro de su dominio.
3. Para efectos nuevos, exigir la elegibilidad correspondiente.

Un replay íntegramente acreditado no requerirá paquete activo, unidad activa ni autoridad actualmente vigente y no publicará otra vez.

Los dominios siguen separados:

- Transición: payload y clave canónicos existentes.
- Continuidad: ejecución, paquete e intento, con comparación de contenido existente.
- Recibo/cierre: evidencia durable y cadena demostrable existentes.

Un checkpoint divergente permitido sigue agregando enlace; no se convierte en replay. Un recibo existente cuyo cierre de continuidad aún falta **no acredita replay de ese cierre**: agregarlo sigue siendo un efecto nuevo sujeto a sus precondiciones.

### 4.5 Adopción y compatibilidad

La política nueva se aplica a las operaciones evaluadas por la versión nueva; no migra retrospectivamente datos.

Se conservan claves, digests, encadenamiento y formatos históricos. La historia previamente no demostrable no se convierte en demostrable por inferencia desde el estado activo.

La recepción normal conserva la exigencia de unidad abierta activa y paquete despachado. La tardía conserva su excepción explícita de destino cerrado y paquete perteneciente a esa ejecución; no relaja identidad, contenido, scope ni validación física.

## 5. Postcondiciones

### PC-01 — Contradicciones rechazadas sin efectos

En todos los bordes de P/C/R que consumen identidad para estas decisiones, una contradicción entre fuentes aplicables produce rechazo diagnosticable y no modifica estado, continuidad, recibos ni artefactos administrados. Incluye contradicciones en los argumentos de una repetición durable.

**Evidencia:** correspondencia borde→decisión, resultado de rechazo y comparación antes/después de artefactos afectados.

### PC-02 — El propietario acreditado determina la suspensión

Una identidad suministrada que señale otra unidad no permite eludir la suspensión del propietario real. Una unidad no suspendida conserva su operación legítima aunque exista otra suspendida.

La evidencia de ejecución gestionada disponible impide reclasificarla como standalone sólo por omitir identidad o retirar una de sus fuentes.

**Evidencia:** propietario resuelto desde fuentes concordantes y efecto permitido/rechazado sobre la unidad correspondiente.

### PC-03 — Autoridad con un solo criterio

Para los mismos hechos de autoridad y requisitos de operación, P/C/R obtienen la misma decisión. Una autoridad revocada, vencida, desconocida o incompatible no autoriza efectos gestionados que la requieran; la lectura histórica y los replays acreditados siguen disponibles.

**Evidencia:** decisión compartida y ausencia de publicación cuando falta autoridad requerida.

### PC-04 — Replay converge sin duplicación ni estado activo

Una transición, escritura o cierre reconocido como replay por su evidencia existente retorna sin duplicar efectos, aunque el estado activo haya avanzado. Los conflictos siguen rechazándose; los efectos pendientes no se presentan como ya realizados.

**Evidencia:** identidad durable conservada y ausencia de nuevos registros, enlaces o recibos para el efecto repetido.

### PC-05 — Rutas e historia conservadas

Las rutas normal y tardía siguen siendo utilizables con sus precondiciones propias. Los dominios de idempotencia conservan sus diferencias, incluida la extensión legítima de checkpoint. Leer o repetir historia legacy no recalcula claves ni altera bytes históricos.

**Evidencia:** resultados contractuales de ambas rutas y conservación de claves y artefactos preexistentes.

### PC-06 — Desaparecen las decisiones locales migradas

El núcleo contiene las reglas migradas y P/C/R las consumen, también por entradas programáticas directas. Desaparecen las ramas locales de precedencia de identidad, atribución de propietario, vigencia y elegibilidad que ese núcleo reemplaza.

**Evidencia estructural:** inventario antes/después de ramas retiradas y trazabilidad de sus llamadas. Una importación, un wrapper o constantes compartidas no bastan; tampoco un núcleo que delegue la política de vuelta a los consumidores.

Esta condición estructural acredita el resultado explícito «un solo decisor», no un objetivo cosmético de cobertura.

## 6. Deuda y límites

| Deuda | Resultado admisible |
|---|---|
| **SUSP-IDENTITY** | **Puede cerrar** al acreditar PC-01/02/06 en todos los bordes migrados: la identidad suministrada deja de ser autoridad sobre el propietario. No constituye protección frente a manipulación concordante de todos los archivos. |
| **SUSP-GUARD** | **Puede cerrar parcialmente** para evidencia gestionada disponible y guarda compartida. Sigue abierto el límite de eliminar contexto y registro para aparentar standalone; centralizar no recupera evidencia borrada. |
| **SUSP-LOCK** | **No cierra:** faltaría coordinación de escritores; un decisor puro no elimina carreras entre continuidad y suspensión/reanudación. |
| **SUSP-APPROVAL** | **No cierra:** decidir con evidencia existente no restaura aprobaciones borradas ni introduce su revalidación histórica. |

El cierre efectivo depende de evidencia de implementación y review, no de aprobar esta spec.

## 7. Verificación y deferred-hardening

Los tests se vincularán a estas seis postcondiciones, reutilizando cobertura existente. No se prescribe cantidad de tests ni combinatoria exhaustiva.

Quedan como `deferred-hardening`, sin bloquear esta unidad:

- estrés concurrente;
- campañas de manipulación de múltiples archivos;
- combinatoria sin consecuencia observable adicional;
- benchmarks y cobertura puramente cuantitativa.

Los rechazos y recorridos expresamente prometidos arriba no son diferibles.

La suite completa se ejecutará una vez por quien cierre la tarea, conforme al paquete.
