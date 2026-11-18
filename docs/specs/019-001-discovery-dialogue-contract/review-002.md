# Revisión independiente — 019-001

**Resultado: bloqueos documentales pendientes.** Los cuatro hallazgos anteriores recibieron cambios, pero la corrección de la autoridad de aprobación incorpora una regla general fuera del contrato y la nueva regla de registro introduce una contradicción operativa. La revisión no constituye aprobación.

## Hallazgos

### 1. La regla general de delegación por epic amplía la autoridad fuera del alcance aprobado

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

`roles-and-dialogue.md:27-36` establece que una solicitud a nivel de epic que nombre sus especificaciones cuenta automáticamente como solicitud para cada feature. `activation-handoff-019-002.md:66-74` exige añadir esa regla a la fuente canónica `stage-2-specification.md` §2.3 y probarla como comportamiento general.

La fuente vigente limita la excepción a una solicitud explícita para **la feature o etapa específica** (`stage-2-specification.md:90-94`). La autoridad registrada para este epic sí menciona sus especificaciones (`docs/epics/epic-019-discovery-dialogue/execution.md:8-14`), pero una concesión concreta no demuestra autorización para modificar la regla general para epics futuros. El contrato aprobado pide identificar la autoridad delegada aplicable; no pide ampliar su alcance.

**Consecuencia:** 019-002 recibiría la instrucción de cambiar una frontera general de aprobación que no fue autorizada por esta especificación. Una futura delegación podría considerarse suficiente bajo una regla nueva en vez de la vigente.

**Cierre verificable:** retirar del producto la regla general de epic y su modificación/regresión canónica, conservando la exigencia de citar y evaluar la autoridad explícita aplicable a este epic. Alternativamente, obtener una modificación contractual explícita que autorice ese cambio general.

### 2. El nuevo límite de escritura contradice la materialización del informe técnico

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

`roles-and-dialogue.md:66-70` dice que el orquestador escribe el informe del arquitecto y registra respuestas «solo en la sección Dialogue context»; después prohíbe escribir el cuerpo del informe. En cambio, `handoff-fidelity.md:27-30,124-127` indica que el informe conserva **su propia sección**, separada del diálogo, y que el orquestador lo materializa allí. `activation-map.md:24` también permite escribir el informe y la sección de diálogo, mientras que `activation-handoff-019-002.md:75` limita el permiso de registro a Dialogue context.

**Consecuencia:** 019-002 no recibe una instrucción inequívoca sobre si puede materializar el informe fiel del arquitecto fuera de Dialogue context. Una implementación literal puede impedir el soporte durable previo al borrador o mezclar autorías.

**Cierre verificable:** distinguir de forma uniforme **materializar sin alterar el informe recibido en su propia sección** de **redactar notas y respuestas atribuidas únicamente en Dialogue context**; alinear roles, mapa, handoff y regresión.

## Cierre de los cuatro hallazgos anteriores

1. **Corrección vigente:** cerrado. `handoff-fidelity.md:16-18,64-68` define la corrección con autoridad como decisión vigente y la incluye en la redacción; `:80-105` muestra la recuperación.
2. **Soporte anterior al borrador:** cierre **parcial**. `handoff-fidelity.md:26-30,109-127` propone crear `discovery.md` antes del informe y muestra el handoff; la contradicción del hallazgo 2 impide acreditar un procedimiento completo inequívoco.
3. **Prohibición y delegación:** cierre **parcial**. `roles-and-dialogue.md:24-34,69-70` sustituye la prohibición absoluta por regla y excepción coherentes, pero añade la ampliación general del hallazgo 1.
4. **Ejemplos límite:** cerrado. `examples.md:204-220` contrasta exclusión autorizada con silenciosa y `VERIFY` admisible con uno que bloquea un compromiso verificable.

## Resultados por postcondición

**Versiones examinadas:** HEAD `04794b78`; producto versionado en ese HEAD, sin modificaciones locales en su directorio. El producto declara fuentes históricas en `64aa4670`; discovery declara `265174993b4213be9a96545578016657bc8b09ba`. SHA-256 verificados: spec `1e50141c91b84a309be92d115c8df025a1fb5e138dc0ba35b2c13f74bd864853`; discovery `6d77f4ba7c342bdf7c99f5b8b8a506eed71a021ebc035456be302a090357bb43`; checklist `41161a34802e0a4945de042f03b2e65f146c827342d0433079924f3d94a9a83f`.

Las rutas de producto abreviadas están bajo `docs/specs/019-001-discovery-dialogue-contract/operating-design/`.

| PC | Resultado | Evidencia y límites |
|---|---|---|
| **1** | No satisfecho | `roles-and-dialogue.md:7-53`; spec D1/PC-1. La asignación existe, pero la autoridad propuesta incluye el hallazgo 1. |
| **2** | No satisfecho | `roles-and-dialogue.md:60-81`, `activation-map.md` R1/R11; spec D1/PC-2. Los límites de registro y materialización se contradicen; hallazgo 2. |
| **3** | Satisfecho en la regla de fidelidad | `handoff-fidelity.md:7-18,53-68`; spec D2/PC-3. Correcciones, propuestas y decisiones se distinguen; la ubicación operativa está afectada por el hallazgo 2. |
| **4** | No satisfecho | `handoff-fidelity.md:70-127`; spec D2/PC-4. El ejemplo contiene decisión, autoridad, antecedente y pregunta, pero la producción del soporte encuentra el conflicto del hallazgo 2. |
| **5** | Satisfecho | `readiness-and-approval.md:9-26`; spec D3/PC-5. Se distinguen silencio, respuesta parcial, propuestas, elecciones y supuestos técnicos. |
| **6** | No satisfecho | `readiness-and-approval.md:33-73`; spec D3/PC-6. La secuencia separa eventos, pero la regla general de autoridad excede el contrato; hallazgo 1. |
| **7** | Satisfecho | `lightweight-paths.md:17-72`; spec D4/PC-7 y discovery §2. Distingue ciclo normal y trabajo independiente; no acredita ejecución. |
| **8** | No satisfecho | `activation-map.md` R1–R12; spec PC-8 y discovery §§3–4. El mapa incluye consumidores y propietarios, pero incorpora ambos hallazgos. |
| **9** | Satisfecho respecto de los cuatro ítems exigidos | `activation-handoff-019-002.md` ítems 1–4; spec D5/PC-9. El ítem adicional 5 contiene los bloqueos señalados. No se afirma reparación ejecutable. |
| **10** | Satisfecho para los contrastes examinados | `examples.md` B-01–B-26, especialmente `:204-220`; spec PC-10. Los dos contrastes faltantes de la revisión anterior ahora están presentes y son ilustrativos. |
| **11** | Satisfecho como protocolo | `acceptance-protocol-019-002.md` §§1–4; spec PC-11. Exige recorrido observado y cinco casos; **no es evidencia de ejecución real**. |
| **12** | Satisfecho como procedimiento | `verification.md:5-69`; spec PC-12 y checklist protegida. Exige revisión independiente y resultado por PC; esta revisión no equivale a aceptación. |

Para todos los resultados, las versiones y hashes comunes son los indicados arriba. Los límites de comprobación histórica figuran en las abstenciones.

## D1–D5 y alcance de los cambios nuevos

- **D1:** la mediación y las responsabilidades técnicas están descritas, pero la frontera de aprobación añade autoridad general no aprobada y el registro tiene instrucciones contradictorias.
- **D2:** la preservación de correcciones está resuelta semánticamente; la materialización del informe no está resuelta de manera consistente.
- **D3:** readiness y sus ejemplos límite reflejan el contrato.
- **D4:** distingue los caminos ligeros sin cuota ni cuestionario fijo.
- **D5:** conserva la consulta de brainstorm y delega su corrección ejecutable y regresión a 019-002.

El **delta de registro** es pertinente para hacer recuperable el contexto exigido por D2 y cerrar el hallazgo anterior; el problema no es proponerlo, sino su formulación contradictoria. La **regla general de delegación por epic** y su cambio a §2.3 sí exceden el alcance aprobado. No identifiqué un rol, estado, gate o campo de paquete nuevo.

## Evidencia de ejecución

- `python3 scripts/cdad_packet.py validate-request …` y `validate-packet …`: finalizaron con éxito, sin salida. `render --route C …` reprodujo la identificación recibida.
- `sha256sum` confirmó los tres hashes indicados. `git status --short` mostró cambios de estado y un archivo de inicio de revisión ajenos a esta revisión; ningún cambio local en `operating-design/`.
- Revisé primero la checklist protegida y la revisión anterior; después el contrato, producto y fuentes pertinentes. No ejecuté una suite: la especificación define la revisión semántica independiente como verificación de esta unidad documental.
- **Archivos modificados por esta revisión:** ninguno. **Commit creado:** ninguno.

## Abstentions

- No verifiqué independientemente cada locator histórico ni todas las cadenas de generación de consumidores; los resultados no acreditan compatibilidad universal.
- No observé el ejercicio real de agentes, despliegue ni las correcciones ejecutables de 019-002.