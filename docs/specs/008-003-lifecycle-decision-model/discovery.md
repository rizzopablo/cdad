## Discovery 008-003 — resultado

**Contrato verificado:** SHA-256 coincide con `0c0b342c55e9ca9b2c435d218c99f562537e341511980fe0247331b422d9e645`. Trabajo read-only sobre `280e118313083f97d9f069ad44836ce9ab959781`. No se redactó ni aprobó spec.

**Hallazgo principal:** hay decisiones distribuidas y parcialmente duplicadas, pero **no tres implementaciones completas equivalentes**. Las constantes señaladas no están duplicadas entre los tres módulos. Unificar exige retirar las decisiones locales redundantes, conservando diferencias legítimas entre operaciones.

En las referencias siguientes, `P`, `C`, `R`, `D` y `E` significan archivos bajo `skills/cdad-cycle/scripts/`: `cdad_packet.py`, `cdad_continuity.py`, `cdad_result.py`, `cdad_dispatch.py` y `cdad_delegate.py`. Los archivos de `scripts/` son envoltorios; ver `scripts/cdad_packet.py:10-11`.

### 1. Mapa técnico y riesgo de divergencia

| Superficie | Evidencia y divergencia verificadas | Qué se rompe si evoluciona sólo una rama |
|---|---|---|
| Identidad ejecución/unidad | `C:286-297` prefiere `execution.id` y acepta `execution_id` plano; `C:2305-2318` resuelve feature desde contexto y, para legacy, desde estado activo. `P:2552-2620` exige coherencia feature/epic activos. `R:516-545` coteja request/contexto para recepción tardía; `R:653-658` coteja descriptor/contexto/request en recepción nueva. | Una identidad puede ser aceptada por continuidad y rechazada al recibir; el fallback a unidad activa puede atribuir historia legacy a una unidad distinta. |
| Propietario usado por suspensión | `P:704-706` guarda la feature **suministrada**. `C:2852-2865` la toma del contexto recibido; `R:617` del descriptor. Para retiro, `P:6782-6810` resuelve propietario desde registro suspendido/request. `D:1136-1146` lo obtiene del contexto canónico de la ejecución del request. | Una operación protege al propietario real mientras otra consulta una identidad manipulable; suspensión aplicada inconsistentemente. |
| Autoridad vigente | `P:2552-2620` verifica binding, epic, delegación, scope y existencia de fuente. `C:316-357` normaliza revocación/status/fecha/source; `C:398-417` acepta estado explícito o calcula fecha. | Continuidad puede considerar activa una autoridad que packet rechaza por scope/fuente/binding; también hay diferencias de vocabulario (`current`/`active`). No son validaciones equivalentes hoy. |
| Transiciones e idempotencia | `P:6319-6426`: clases de transición, payload de efectos y digest canónico; `P:7458-7595`: guardas, operación y lock. `C:963-1077`: clave `(execution, packet, attempt)`, comparación de contenido y encadenamiento; checkpoint divergente agrega enlace, begin divergente rechaza, con excepción de reanudación. | Una abstracción que confunda ambas identidades puede tragarse un checkpoint legítimo como no-op o permitir repetir una decisión de estado. **Son dos dominios de idempotencia, no copias textuales intercambiables.** |
| Recibo y cierre | `R:608-726` reconoce primero recibo durable idéntico y después valida recepción nueva; `C:1452-1535` reconoce primero cierre ya demostrado y autoriza después un cierre nuevo. `P:7228-7250` sólo obtiene/verifica digest del archivo para esa función. | Equiparar “archivo con digest” con “recibo validado” debilita evidencia; exigir estado activo antes de reconocer un replay rompe la convergencia después del avance. |
| Disposición | `C:2320-2337` **ya consume** `P.disposition_selection`; `P:6570` es el selector compartido. | Reimplementarlo en el nuevo modelo añadiría otra copia donde actualmente existe dueño único. |

**Constantes: resultado contrario a la hipótesis del encargo.**

- `VALID_SUBSTAGES`: definición en `P:56`.
- `CLOSED_FEATURE_STATUSES`: definición en `P:174`; `R:541` la consume mediante `cdad_packet`.
- `TRANSITION_CLASSES`: definición en `P:6319`.
- La búsqueda de esos símbolos en `P/C/R` no encontró definiciones alternativas en `C/R`.

No corresponde medirlas ni presentarlas como constantes duplicadas.

### 2. Recepción y tabla 007-004

La tabla del sobre **no vive triplicada en P/C/R**:

- `D:1036-1133`, `record`: produce `blocked+none` ante contradicción, sin registrar el intento; registra y produce `completed+staged` con payload; sin payload declara `unknown+none`.
- `E:376`, `interpret_arrival`: punto de interpretación del sobre externo; vocabulario comprobado desde `E:400`.
- `R:608-726`, `receive`: valida descriptor y publica recibo; no interpreta esa tabla de transporte.
- `C:1452`: cierra continuidad del recibo, no acredita terminación del transporte.

**Consecuencia de alcance:** si la promesa futura incluye una única decisión sobre combinaciones `termination/delivery`, `D/E` deben entrar explícitamente en la superficie de la spec. Limitar cambios a P/C/R no demostraría esa promesa. **VERIFY:** inventario completo de productores/adaptadores antes de decidir mover la tabla; no se acredita aquí duplicación exhaustiva de sus ramas.

### 3. Opciones de decisor único

Todas son propuestas, **no APIs existentes**.

| Opción | Criterio | Límite |
|---|---|---|
| **A. Núcleo compartido de decisiones puras — recomendada** | Recibe hechos normalizados y operación explícita; decide identidad, autorización, elegibilidad y replay/conflicto. P/C/R conservan lectura, verificación física y publicación. Se retiran ramas decisorias locales migradas. | No convertirlo en motor universal: claves de transición, checkpoint y recibo siguen distintas y explícitas. No resuelve carreras por sí solo. |
| B. Reducer de ciclo de vida | Una función decide resultado y efectos previstos sobre snapshot validado; aprovecha el precedente `C.plan_write` (`C:969-984`). | Mayor cambio: representar publicación de recibos y cadena junto al estado puede exceder una reorganización sin capacidades nuevas. No implica otro registro. |
| C. Decisor alojado en `cdad_packet` | Menor desplazamiento inicial; aprovecha selector y vocabularios ya compartidos. Los demás consumidores dejan de decidir esos casos. | Packet ya mezcla CLI, política, publicación y status; aumenta acoplamiento y exige verificar importaciones. Preferible sólo si extraer módulo no reduce realmente ese acoplamiento. |
| D. Tabla cerrada operación × situación con evaluador único | Adecuada si el inventario revela pocas reglas estables; hace visibles normal/late/replay/suspendido y sus excepciones. | Digests, cadena y autoridad requieren predicados verificables. Una tabla que llama a las decisiones antiguas sería la fachada prohibida. |

**Criterio recomendado:** generalizar identidad y elegibilidad compartidas, no igualar artificialmente operaciones distintas. La prueba estructural del cambio será que las ramas migradas desaparezcan de consumidores; compartir sólo constantes o añadir un envoltorio no cumple el epic.

### 4. Adopción y deuda

La adopción debe ser explícita: distinguir contexto gestionado de standalone/legacy, resolver propietario desde evidencia concordante y rechazar contradicciones antes de efectos. No reinterpretar historia ni recalcular claves antiguas silenciosamente. El reconocimiento de evidencia durable existente debe seguir separado de la autorización para producir efectos nuevos.

| Deuda | Resultado que puede prometer 003 |
|---|---|
| **SUSP-IDENTITY** | Cierre del uso de identidad suministrada como autoridad **si** todos los bordes migran al resolvedor concordante, incluidos recepción y continuidad. No es frontera contra manipulación de todos los archivos. |
| **SUSP-GUARD** | Cierre parcial: clasificación y guarda únicas para evidencia disponible. El límite documentado de borrar contexto/registro para aparentar standalone **no desaparece sólo por centralizar**. Declararlo si no se incorpora evidencia suficiente ya existente. |
| **SUSP-LOCK** | **No cierra.** `P:7544` usa lock; `C:1080-1093` publica escrituras sin ese lock. Requiere coordinación de escritores, no un decisor puro. |
| **SUSP-APPROVAL** | **No cierra automáticamente.** `P:993-1038` comprueba pins/revocación y restaura estado, pero centralizar no repone una aprobación borrada. Exige decisión explícita sobre revalidación y evidencia conservada. |

Definición documentada de esas cuatro deudas: `docs/progress.md:1065-1071`.

### 5. Preguntas para el brainstorm

1. ¿Adoptamos A, manteniendo almacenamiento y publicación existentes?
2. ¿003 incluye D/E para la decisión del sobre o declara esa superficie fuera y conserva sus dueños actuales?
3. ¿Se acepta cierre limitado de SUSP-GUARD y mantener LOCK/APPROVAL abiertas?

No propongo batería de tests. Las futuras postcondiciones deberán nombrar promesas observables: rechazar identidad contradictoria sin efectos; respetar suspensión del propietario; reconocer replay sin duplicar efectos; conservar las rutas normal/tardía. Estrés concurrente y combinatoria sin promesa adicional irán a `deferred-hardening`.

### Evidencia operativa

- **Archivos modificados por esta tarea:** ninguno.
- **Estado inicial y final:** ` M docs/.cdad-state.json` — cambio preexistente, no tocado.
- **Commit creado:** ninguno.
- **Tests/suite:** no ejecutados.
- **Comandos ejecutados:** `sha256sum` del contrato; `git status --short` al inicio y final; `git rev-parse HEAD`; búsquedas `rg -n` acotadas a P/C/R, D/E y documentación de deuda; lecturas `sed -n` de los rangos citados; `cat skills/cdad-cycle/references/design-principles.md`. Sus salidas fundamentan el mapa anterior; no se ejecutaron comandos de escritura.
