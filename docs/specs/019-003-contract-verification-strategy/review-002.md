# Revisión independiente — 019-003

**Resultado: no corresponde acreditar todavía la implementación.** La revisión no constituye aprobación. La candidata examinada es `fcfb75e1`, con correcciones de producto en `cc4465d0`; la base del trabajo es `0b11b5fb`.

Los tres hallazgos de `review-001.md` quedan cerrados en las rutas que señalaban. Encontré, sin embargo, dos inconsistencias bloqueantes en superficies incluidas en el contrato.

## Hallazgos bloqueantes

### 1. El flujo ligero autónomo no establece la revisión previa de la estrategia de verificación

**Required — Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-spec-and-test/SKILL.md:18-25, 55-57, 96-105`  
**Afecta:** PC-1, PC-2 y PC-6.

La guía ligera declara que se usa al inicio de cualquier tarea y ofrece su propio formato mínimo y tabla de gates. Su formato pide una postcondición y una lista de verificación; la regla 2 agrega método, criterio, evidencia y límites, pero no pide identificar la **propiedad** por promesa. Tampoco instruye a realizar, antes de la aprobación, la revisión independiente de la corrección y suficiencia de cada promesa, ni presenta la alternativa de exención registrada. La referencia general a que `cdad-cycle` es dueño de los gates no indica en esa ruta cuándo ni cómo aplicar esas condiciones.

**Consecuencia:** siguiendo el flujo ligero como guía autónoma, el dueño puede iniciar la producción con una estrategia que nunca recibió la comprobación de suficiencia exigida por PC-2. La revisión independiente posterior del producto no sustituye esa decisión previa.

**Cierre verificable:** hacer que el flujo ligero conduzca explícitamente, antes de producción, a la declaración completa por promesa y a la revisión de suficiencia o a la exención existente, preferentemente mediante una referencia operativa al procedimiento canónico. Comprobar el recorrido autónomo con una promesa mixta y una exención registrada.

### 2. La instrucción de reingreso describe incorrectamente los paquetes congelados

**Required — Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-cycle/references/re-entry.md:283-291`; contraste con `skills/cdad-cycle/scripts/cdad_packet.py:1762-1771, 1868-1879`.  
**Afecta:** PC-5 y PC-6.

La guía afirma que un paquete publicado deja necesariamente de ser recibible cuando cambian las fuentes de instrucciones, porque ya no coincidiría con el render canónico. Pero el renderer documenta e implementa lo contrario para solicitudes con `instruction_sources`: valida y renderiza desde los bytes congelados en la solicitud, **sin consultar las fuentes vivas**. Solo las solicitudes históricas sin ese campo usan validación contra fuentes vivas.

La afirmación ya existía en la base; no la atribuyo a la corrección `cc4465d0`. No obstante, el contrato pide revisar reingreso y consumidores efectivos, y esta incompatibilidad afecta directamente la coherencia comprometida.

**Consecuencia:** el operador puede esperar un rechazo que no ocurrirá y dar por supuesto que un paquete antiguo no puede recibirse bajo instrucciones congeladas. También puede republicar innecesariamente o adoptar una decisión de recuperación sobre una premisa falsa.

**Cierre verificable:** distinguir las solicitudes congeladas de las históricas sin snapshot y describir su recepción real, sin presentar la coincidencia estructural como prueba de vigencia semántica. Contrastar la instrucción corregida con un paquete congelado cuyo origen vivo haya cambiado.

## Cierre de los hallazgos anteriores

1. **Stage 3 → Stage 4:** cerrado para la contradicción señalada. `stage-3-tdd.md:322-342` permite producción semántica con revisión independiente pendiente, exige verde para las partes ejecutables y ambas familias para mixtas, sin RED fabricado.
2. **Exención de revisión:** cerrado para el gate señalado. `stage-2-specification.md:238-244` y `cdad-cycle/SKILL.md:349-350` expresan revisión o exención con los cuatro campos, sin atribuir revisión ejecutada ni suficiencia verificada.
3. **Cierre mixto ligero:** cerrado para el escape señalado. `cdad-spec-and-test/SKILL.md:57, 66-78, 103-105` exige checks ejecutables y revisión contextual independiente de la parte semántica.

El primer hallazgo nuevo no reabre ese tercer defecto: trata de la **revisión de la estrategia antes de aprobar y producir**, no de la revisión del producto al cierre.

## Resultado por postcondición

| PC | Dictamen y evidencia examinada |
|---|---|
| **PC-1** | Guía normal y plantilla incorporan la estrategia; la ruta ligera autónoma no la expresa completa. Hallazgo 1. |
| **PC-2** | El gate normal y la exención están reconciliados; falta una ruta previa inequívoca en la guía ligera autónoma. Hallazgo 1. |
| **PC-3** | Las rutas normal y ligera examinadas distinguen producción semántica, ejecutable y mixta. Los tres defectos operativos anteriores quedan cerrados. |
| **PC-4** | Las instrucciones de implementer y packet protegen criterios aprobados y devuelven cambios necesarios a aprobación. No observé cambios de tests ni criterios protegidos en el diff examinado. |
| **PC-5** | Las categorías de evidencia están declaradas; la afirmación errónea sobre recepción congelada compromete la interpretación del resultado del control. Hallazgo 2. |
| **PC-6** | No acreditado: persisten los dos hallazgos y los límites de comparación indicados abajo. El diff real es documental y de instrucciones; no observé un cambio de addon que active una batería de instalación Odoo. |

## Evidencia y límites

- **Entrada:** `validate-request` y `validate-packet` terminaron sin error; `render --route C` reprodujo la identificación recibida. La revisión se realizó con contexto de ejecución v2.
- **Prueba independiente:** ejecuté `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_010_001_documentary_contracts.py tests/test_010_002_documentary_role_integration.py tests/test_010_003_documentary_pilot.py`: **48 passed in 47.28s**. Estos controles no demuestran por sí solos la fidelidad semántica.
- El implementer reporta `155 passed`, otra selección con `217 passed, 2 failed`, una validación de consistencia con un fallo y `68 PASS` de especialización Odoo. **No reproduje esas corridas ni la atribución de los fallos a la base o al drift instalado.** Su informe no enumera los comandos exactos completos de las tandas de pytest, por lo que no permite reproducirlas directamente a partir de él.
- `git diff --name-only 0b11b5fb HEAD -- docs/specs/019-001* docs/specs/019-002* tests` no mostró cambios. Esto ayuda a verificar preservación física, no demuestra por sí solo toda la preservación semántica.
- Contrasté la tabla de decisiones y el directorio de ADR en lo pertinente a la revisión; no identifiqué una contradicción adicional atribuible al diff.
- **Suite completa:** no realizada; el encargo la excluye. **Archivos modificados por esta revisión:** ninguno. **Commit de esta revisión:** ninguno. `docs/.cdad-state.json` ya aparecía modificado al comenzar y seguía así al terminar.
- Runtime observado: Python `3.13.5`.

## Abstentions

- No acredito la totalidad de PC-6: no completé una comparación semántica exhaustiva de todos los agentes generados de ambos runtimes, variantes de dominio y salidas instaladas.
- No determino si los dos fallos de la selección amplia ni el fallo de instalación reportados por el implementer son exclusivamente preexistentes.
- No ejecuté un recorrido integral de preparación y transición de una feature nueva; la conclusión sobre paquetes congelados se apoya en el código del renderer y sus instrucciones, no en una prueba propia de cambio de fuente viva.