# Revisión independiente — 019-003

**Resultado: hay defectos bloqueantes; no corresponde acreditar todavía la implementación.** La revisión no constituye aprobación.

Revisé el contrato aprobado, el AUDIT, el diff y consumidores candidatos. La base examinada es `0b11b5fb`; el candidato es `bff58892db2d36d531c1d41ced497979de6c7ffa`. La metodología instalada y el producto candidato son cosas distintas: los hallazgos siguientes se refieren al candidato del repositorio.

## Hallazgos bloqueantes

### 1. La ruta semántica llega a un gate que exige haber terminado la revisión futura

**Required — Verdict: BLOCKING · Bucket: h**

En `skills/cdad-cycle/references/stage-3-tdd.md:152-154`, la producción semántica se verifica mediante revisión contextual en Stage 4. Sin embargo, el loop de `:320-327` exige que cada promesa esté verificada para cerrar Stage 3, y el gate de `:329-343` exige que **toda** promesa ya esté verificada antes de pasar a Stage 4. Además, la tabla de `:162-166` dice que GREEN ocurre después de un RED válido.

**Consecuencia:** una promesa exclusivamente semántica no tiene una secuencia inequívoca para avanzar: su verificación se programa para después del gate que la exige, mientras otra instrucción exige un RED que esa ruta prohíbe fabricar. Esto afecta directamente PC-3 y PC-6.

**Cierre verificable:** distinguir en el loop, la tabla y el gate entre evidencia ejecutable ya obtenida y revisión semántica pendiente en Stage 4; comprobar una ruta exclusivamente semántica y otra mixta completas, sin RED ficticio ni aceptación anticipada.

### 2. La exención de revisión queda contradicha por el gate de especificación

**Required — Verdict: BLOCKING · Bucket: h**

`skills/cdad-cycle/references/re-entry.md:281` preserva correctamente la exención explícita y registrada del dueño. Pero `skills/cdad-cycle/references/stage-2-specification.md:238-241` exige sin alternativa que la revisión haya comprobado la suficiencia y que exista `plan-review.md`.

**Consecuencia:** quien siga el gate no puede avanzar con una exención válida sin declarar una revisión inexistente o incumplir una condición del gate. PC-2 exige preservar precisamente esa excepción sin presentarla como revisión ejecutada.

**Cierre verificable:** expresar ambas alternativas en el gate —revisión realizada y blockers tratados, o exención registrada con los campos exigidos— manteniendo explícito que la segunda no acredita suficiencia.

### 3. El flujo ligero todavía puede cerrar sin revisión contextual independiente de una promesa mixta

**Required — Verdict: BLOCKING · Bucket: h**

`skills/cdad-spec-and-test/SKILL.md:57,77,99-104` menciona revisión contextual para promesas *semantic-only*, pero no exige esa revisión para la parte semántica de una promesa combinada. Su diagrama de `:67-75` todavía presenta “todos los tests pasan → Merge”; la tabla conserva “escribir tests” y “ejecutar tests” sin la distinción de rutas.

**Consecuencia:** en el flujo ligero, una promesa mixta puede parecer cerrada por checks ejecutables verdes aunque no se haya contrastado independientemente su fidelidad semántica. Esto contraviene PC-3, PC-5 y PC-6.

**Cierre verificable:** hacer que el flujo ligero exija ambas familias para compromisos mixtos, identifique la revisión como independiente y reconcilie el diagrama y las acciones de gate con las tres rutas.

## Resultado por postcondición

| PC | Resultado de esta revisión |
|---|---|
| **PC-1** | La guía y plantilla incorporan los elementos de verificación por promesa; no identifiqué un defecto específico adicional en esa declaración. |
| **PC-2** | **No acreditado:** la exención está declarada, pero contradicha por el gate. Hallazgo 2. |
| **PC-3** | **No acreditado:** existen instrucciones de enrutamiento, pero los gates y el flujo ligero dejan contradicciones operativas. Hallazgos 1 y 3. |
| **PC-4** | La separación entre criterio aprobado, producción y devolución a aprobación aparece en `stage-3-tdd.md:158` y en las instrucciones del implementer. No identifiqué una edición de tests ni de criterios protegidos en el diff. |
| **PC-5** | Las categorías y límites están declarados en `stage-4-review.md:74-96`; el escape del flujo ligero impide acreditar coherencia de cierre. Hallazgo 3. |
| **PC-6** | **No acreditado:** las contradicciones anteriores afectan consumidores efectivos. La evidencia de entrega también conserva los límites indicados abajo. |

## Evidencia y alcance

- **Validación de entrada:** `validate-request` y `validate-packet` terminaron sin salida ni error; `render --route C` reprodujo la identificación recibida. El contexto de ejecución es versión 2.
- **Prueba independiente:** ejecuté `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_010_001_documentary_contracts.py tests/test_010_002_documentary_role_integration.py tests/test_010_003_documentary_pilot.py tests/test_cdad_generate.py tests/test_role_packet_render.py`. Mostró progreso hasta 96%, pero terminó por timeout a los 120 segundos, código 143. **No es una corrida verde.**
- El informe del implementer declara 94 pruebas focalizadas aprobadas, una selección amplia con dos fallos reproducidos en base y un fallo de `make validate` atribuido a drift instalado. No reproduje independientemente esas ejecuciones ni sus diagnósticos; no los trato como prueba propia.
- `git diff --name-only 0b11b5fb HEAD -- tests` no mostró cambios en tests. Tampoco mostró cambios en ADR ni en los directorios históricos consultados de 019-001 y 019-002. Eso **no demuestra por sí solo** la preservación semántica completa de sus obligaciones.
- El diff incluye instrucciones canónicas, packets, handoffs, plantilla y agentes genéricos y Odoo generados para dos runtimes; también incluye estado CDAD e informe de recepción. No observé creación de un rol nuevo. El árbol tenía `docs/.cdad-state.json` modificado al comenzar y seguía así al terminar; **esta revisión no modificó archivos ni creó commits**.
- El renderer usa snapshots de instrucciones en `REQUEST.json`; la validación del packet recibido pasó. La afirmación de `re-entry.md:285-291` de que un cambio posterior de fuentes necesariamente provoca rechazo merece contraste específico con ese comportamiento antes de usarla como procedimiento de recuperación; no la atribuyo como regresión de este diff.

## Abstentions

- No acredito PC-6 en su totalidad: no completé una comparación semántica exhaustiva de todos los consumidores de dominio, salidas instaladas y antecedentes protegidos.
- No determino si los fallos reportados de la selección amplia y `make validate` son exclusivamente preexistentes: no reproduje la comparación de base ni el diagnóstico de instalación.
- No afirmo que el renderer impida preparar una producción semántica: confirmé el par `implementer/green` y la validación del packet recibido, pero no ejecuté un recorrido completo de preparación y transición para una nueva feature semántica.