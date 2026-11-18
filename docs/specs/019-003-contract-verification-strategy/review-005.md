# Revisión independiente — 019-003

**Resultado: hay bloqueos pendientes.** La revisión no constituye aprobación. La candidata examinada es `32fe12c906aff5bce2e560440c835ab97d2f4c9e`, contra `0b11b5fb` y la especificación aprobada.

## Hallazgos

### 1. La guía de especificación todavía exige RED para tareas semánticas

**Required — Verdict: BLOCKING · Bucket: h**  
**PC afectadas:** PC-3 y PC-6.  
**Ubicación:** `skills/cdad-cycle/references/stage-2-specification.md:158-160, 169-176, 251-253`; contraste con `stage-3-tdd.md:146-155`.

La guía define *cada* tarea de un plan complejo como una unidad con ciclo RED→GREEN propio y exige sus pasos TDD con el test primero. Además, su antipatrón AP-5 presenta «un párrafo + test fallando» como mínimo, sin distinguir el método comprometido.

Eso contradice la ruta aprobada para producción exclusivamente semántica: quien prepare una tarea documental puede entender que debe crear un test fallido aunque no exista comportamiento ejecutable pendiente. En compromisos mixtos, tampoco queda claro que el RED corresponde solo a la parte ejecutable.

**Cierre verificable:** condicionar esas instrucciones al método de cada tarea: mantener test primero y RED→GREEN para comportamiento ejecutable pendiente; para fidelidad semántica, producción y revisión contextual independiente; para tareas mixtas, ambas familias en sus respectivas partes.

### 2. El handoff legacy semántico sigue pidiendo un test y salida verde

**Required — Verdict: BLOCKING · Bucket: h**  
**PC afectadas:** PC-3, PC-5 y PC-6.  
**Ubicación:** `skills/cdad-cycle/references/handoff-prompts.md:415-438`.

La instrucción del handoff ya admite explícitamente una promesa semántica sin inventar tests, pero la misma plantilla sigue pidiendo como contexto «el test que debe pasar» y como salida «todos los tests verdes», sin condición.

El consumidor que use esa plantilla para producción semántica recibe instrucciones incompatibles: puede exigir evidencia inexistente o presentar un resultado estructural como sustituto de la revisión contextual.

**Cierre verificable:** hacer condicionales el test de entrada y la salida verde a las comprobaciones aplicables; pedir para la parte semántica el producto y la evidencia pertinente, dejando explícita la revisión independiente posterior. La ruta mixta debe conservar ambos tipos de evidencia.

### 3. No está acreditada la protección de entrega aplicable

**Required — Verdict: BLOCKING · Bucket: h**  
**PC afectadas:** PC-5 y PC-6.

La especificación exige resultados satisfactorios de las comprobaciones de entrega pertinentes y comparaciones atribuibles entre candidata y salidas. El informe de fix-004 afirma que la selección de pytest pasó, pero el archivo `.cdad/orchestration/epic-019/019-003-fix-004-pytest.log` contiene únicamente progreso hasta `[100%]`: **no contiene resumen ni código de salida**. No acredita por sí solo un resultado verde.

Además, la revisión anterior registró fallos de consistencia y de `validate-subagents.sh`; el fix-004 no volvió a ejecutar este último ni midió su baseline. No hay base aquí para afirmar que todos esos fallos sean preexistentes o irrelevantes para la entrega candidata.

**Cierre verificable:** aportar resultados completos y atribuibles de las comprobaciones de generación, renderizado y distribución seleccionadas para las superficies cambiadas, junto con la comparación candidato/salida; resolver o clasificar con evidencia los fallos relevantes. No se requiere una suite completa por este hallazgo.

## Resultado por postcondición

| Postcondición | Resultado de esta revisión |
|---|---|
| **PC-1** | La estrategia por promesa aparece en la guía y la plantilla examinadas; sin nuevo defecto identificado en lo revisado. |
| **PC-2** | Se declara la revisión de suficiencia o la exención registrada; sin nuevo defecto identificado en lo revisado. |
| **PC-3** | No acreditada: persisten las contradicciones de los hallazgos 1 y 2. |
| **PC-4** | Las instrucciones examinadas protegen los criterios aprobados y devuelven los cambios necesarios a aprobación; no identifiqué un debilitamiento adicional de esa regla. |
| **PC-5** | No acreditada: el handoff pide verde incondicionalmente y falta evidencia atribuible de las comprobaciones indicadas. |
| **PC-6** | No acreditada: existen consumidores contradictorios y falta evidencia suficiente de entrega. |

El defecto específico de `review-004` en la tabla principal de evidencia fue corregido: `skills/cdad-cycle/SKILL.md:543-546` distingue partes ejecutables, semánticas y mixtas. Eso no cierra las contradicciones independientes señaladas arriba.

## Evidencia y límites

- **Entrada:** `validate-request` y `validate-packet` terminaron sin salida ni error; `render --route C` reprodujo la identificación recibida. El contexto declara versión 2.
- **Tests primero:** examiné `test-audit.md` y sus límites declarados antes de contrastar el producto. No ejecuté tests en esta revisión; no atribuyo verde al log de progreso.
- **Preservación física:** `git diff --quiet 0b11b5fb HEAD -- docs/specs/019-001* docs/specs/019-002* tests` devolvió `0`. Esto no demuestra por sí solo fidelidad semántica.
- **Diff:** incluye instrucciones canónicas, agentes generados y artefactos documentales; no observé cambios de addon que justifiquen exigir una instalación limpia Odoo.
- **Comprobación adicional:** `git diff --check 0b11b5fb` devolvió `2` por espacios finales en informes de revisión Markdown. No lo elevo como hallazgo funcional.
- **Suite completa:** no realizada, excluida por el encargo.
- **Archivos modificados por esta revisión:** ninguno. **Commit de esta revisión:** ninguno. `docs/.cdad-state.json` ya aparecía modificado al inicio.

## Abstentions

- No acredito la comparación completa de todas las variantes generadas, instalaciones y fuentes históricas protegidas; la evidencia de entrega disponible es insuficiente.
- No determino si los fallos previos de validación son preexistentes ni si afectan exclusivamente al entorno instalado.
- No ejecuté un recorrido integral con agentes reales ni una suite completa.