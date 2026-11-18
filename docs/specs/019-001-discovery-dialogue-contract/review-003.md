# Revisión independiente — 019-001

**Resultado: persisten bloqueos documentales.** Los dos hallazgos de la revisión 002 recibieron cambios, pero la corrección del límite de escritura introduce una prohibición más amplia que interfiere con el ciclo. También permanece una contradicción sobre la exención de revisión del borrador. Esta revisión no constituye aprobación.

## Hallazgos

### 1. El límite de registro prohíbe escrituras necesarias para el resto del ciclo

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

`roles-and-dialogue.md:68` indica que el orquestador, al aplicar la nueva autorización de registro, «writes no other section or file in the feature directory». `handoff-fidelity.md:31` formula una restricción aún más amplia: «writes no other section or file».

Sin embargo, el propio diseño requiere que el orquestador materialice el dictamen de revisión (`readiness-and-approval.md:43`) y reciba y materialice el informe independiente fuera del directorio del producto (`verification.md:16-19`). La especificación también exige un borrador, revisión y aprobación registrados. Leída literalmente como regla general de escritura, la nueva prohibición impide materializar esos artefactos, incluido el informe de revisión fuera de `discovery.md`.

**Consecuencia:** 019-002 podría activar una instrucción que permite conservar el diálogo, pero impide completar o acreditar otras responsabilidades existentes del orquestador.

**Remedio y cierre verificable:** acotar expresamente la restricción a la **autoría y ubicación del registro de diálogo y del informe técnico**, sin prohibir las demás escrituras o materializaciones ya autorizadas por el ciclo. Alinear `roles-and-dialogue.md`, `handoff-fidelity.md`, `activation-map.md` y el ítem 5 del handoff; comprobar que siguen permitidos el informe independiente y los demás artefactos del ciclo.

### 2. La ruta de revisión obligatoria contradice la exención explícita que el propio diseño conserva

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

`readiness-and-approval.md:68-73` permite una exención explícita de la revisión del borrador, registrada con los campos indicados; `lightweight-paths.md:41-43,63` también la reconoce. En cambio:

- `readiness-and-approval.md:55-57` dice que el borrador pasa al aprobador **solo después** de cerrar los bloqueos de la revisión.
- `activation-map.md`, R4, prescribe el despacho a revisión antes de aprobar sin mencionar la exención.
- `activation-handoff-019-002.md`, ítem 2, prohíbe una ruta que permita aprobar antes del dictamen, sin excepción.

**Consecuencia:** la activación y su regresión pueden eliminar en la práctica una excepción vigente que el mismo producto pretende preservar, o dejar a los consumidores con rutas incompatibles.

**Remedio y cierre verificable:** expresar uniformemente que la revisión precede a la aprobación **salvo la exención explícita y registrada conforme a la regla vigente**; incluir ambas rutas en la obligación de regresión, sin tratar la exención como una aprobación ni como un dictamen.

## Cierre de hallazgos anteriores

| Hallazgo anterior | Resultado |
|---|---|
| Revisión 002: regla general de delegación por epic | **Cerrado en el alcance examinado.** `roles-and-dialogue.md:27-36` aplica la concesión concreta dentro de sus términos y niega su generalización; el ítem 5 del handoff ya no ordena añadir una regla general a §2.3. |
| Revisión 002: informe técnico frente a notas de diálogo | **Cierre parcial.** La distinción solicitada aparece de forma uniforme en `roles-and-dialogue.md:68`, `handoff-fidelity.md:29-31`, `activation-map.md` R1 y el ítem 5 del handoff. La prohibición adicional de otras escrituras mantiene bloqueado el procedimiento: hallazgo 1. |
| Revisión 001: soporte durable anterior al borrador | **Cierre parcial.** `handoff-fidelity.md:29-31,107-127` prevé crear el archivo antes del informe y materializar este después. El hallazgo 1 impide considerar coherente el procedimiento completo. |
| Revisión 001: prohibición y delegación | **Cerrado en la regla examinada.** `roles-and-dialogue.md:27-36` conserva la regla ordinaria, la excepción explícita y la aplicación limitada de la concesión concreta. |

## Resultados por postcondición

Rutas de producto abreviadas bajo `docs/specs/019-001-discovery-dialogue-contract/operating-design/`. Los resultados se refieren al contenido documental, no a instrucciones activadas.

| PC | Resultado | Evidencia y límite |
|---|---|---|
| **PC-1** | Satisfecho en la asignación | `roles-and-dialogue.md:7-18,38-56`; spec D1/PC-1. El round trip identifica roles sin afirmar contacto directo arquitecto–owner. |
| **PC-2** | **No satisfecho** | `roles-and-dialogue.md:63-70`; spec PC-2. La prohibición de escritura es demasiado amplia: hallazgo 1. |
| **PC-3** | Satisfecho en la regla de fidelidad | `handoff-fidelity.md:11-25,55-66`; spec D2/PC-3. Correcciones, propuestas y decisiones permanecen distinguibles; la ubicación operativa está afectada por el hallazgo 1. |
| **PC-4** | **No satisfecho** | `handoff-fidelity.md:68-127`; spec PC-4. El ejemplo recupera los elementos exigidos, pero el procedimiento de soporte completo queda afectado por el hallazgo 1. |
| **PC-5** | Satisfecho | `readiness-and-approval.md:9-26`; spec D3/PC-5. Distingue respuestas parciales, silencio, propuestas, decisiones y supuestos técnicos. |
| **PC-6** | **No satisfecho** | `readiness-and-approval.md:37-73`; spec PC-6. Los eventos se distinguen, pero la ruta y su exención son contradictorias: hallazgo 2. |
| **PC-7** | Satisfecho con la salvedad de PC-6 | `lightweight-paths.md:17-72`; spec D4/PC-7. Distingue los dos caminos y sus obligaciones; la referencia a la exención entra en el conflicto del hallazgo 2. No acredita ejecución. |
| **PC-8** | **No satisfecho** | `activation-map.md` R1–R12; spec PC-8. El mapa identifica propietarios y consumidores, pero sus instrucciones incluyen los conflictos de los hallazgos 1 y 2. |
| **PC-9** | Satisfecho respecto de los cuatro ítems exigidos, con conflicto adicional | `activation-handoff-019-002.md`, ítems 1–4; spec D5/PC-9. Los cuatro ítems están presentes; la redacción del ítem 2 y el adicional ítem 5 están afectados por los hallazgos. No acredita reparación ejecutable. |
| **PC-10** | Satisfecho para los contrastes examinados | `examples.md`, índice B-01–B-26 y ejemplos B-25/B-26; spec PC-10. Son ilustrativos, no observaciones. |
| **PC-11** | Satisfecho como protocolo | `acceptance-protocol-019-002.md:9-79`; spec PC-11 y criterio 5. Exige recorrido completo y cobertura observada de los cinco casos. No se observó el ejercicio. |
| **PC-12** | Satisfecho como procedimiento | `verification.md:5-69`; spec PC-12 y checklist protegida. Exige revisión independiente y resultados por PC. Esta revisión no equivale a aceptación. |

## D1–D5 y cambios transversales

- **D1:** la mediación y la consulta técnica están descritas, pero el límite de escritura excede lo necesario para separar autorías.
- **D2:** las distinciones y la recuperación del contexto están descritas; la operación completa sigue afectada por el hallazgo 1.
- **D3:** las reglas de readiness reflejan la intención; la ruta posterior de revisión y aprobación contiene el hallazgo 2.
- **D4:** distingue los caminos ligeros y conserva proporcionalidad; su tratamiento de la exención debe alinearse con la ruta general.
- **D5:** conserva brainstorm como consulta y asigna su incompatibilidad de entrega a 019-002.

Por ello, **no puedo afirmar que D1–D5 estén implementadas fiel y consistentemente como conjunto**. No identifiqué en el alcance examinado una nueva regla general de delegación por epic ni un nuevo rol, estado, gate o campo de paquete.

## Versiones y evidencia

- **Producto examinado:** HEAD `2f36d99946e07820f7b42eeec93034286ff2f451`; `git status --short` no mostró cambios locales en `operating-design/`. Sí mostró `docs/.cdad-state.json` modificado y `docs/epics/epic-019-discovery-dialogue/rereview2-begin.json` sin seguimiento, ajenos a esta revisión.
- **Spec:** SHA-256 `1e50141c91b84a309be92d115c8df025a1fb5e138dc0ba35b2c13f74bd864853`.
- **Discovery:** SHA-256 `6d77f4ba7c342bdf7c99f5b8b8a506eed71a021ebc035456be302a090357bb43`.
- **Checklist:** SHA-256 `41161a34802e0a4945de042f03b2e65f146c827342d0433079924f3d94a9a83f`.
- La identificación Route C coincidió con `render --route C`; `validate-packet` terminó correctamente sin salida y el contexto declara `schema_version: 2`.
- Comandos adicionales: `git status --short`, `git rev-parse HEAD`, `sha256sum` de spec, discovery y checklist, y lectura de los documentos indicados. No ejecuté suite: la spec define revisión semántica independiente para esta unidad documental.
- **Archivos modificados por esta revisión:** ninguno. **Commit creado:** ninguno.

## Abstentions

- No verifiqué independientemente todos los locators históricos ni la integridad de cada cadena de generación de consumidores; los resultados no acreditan compatibilidad universal.
- No observé ejecución real de agentes, despliegue ni las correcciones ejecutables de 019-002.