# Plan — 010-002-documentary-role-integration

**Versión:** 4.  
**Estado:** borrador revisado, pendiente de revisión y aprobación explícitas.  
**Contrato propuesto:** `docs/specs/010-002-documentary-role-integration/spec.md`, versión 4.

## Steps

- [ ] T1. Materializar y aprobar spec y plan.
- [ ] T2. Auditar cobertura, independencia y fixtures existentes.
- [ ] T3. RED de procedimiento, aplicabilidad y distribución de instrucciones.
- [ ] T4. GREEN de instrucciones, referencias y agentes generados.
- [ ] T5. RED de publicación ordinaria y por reemplazo, coherencia estática y temporal, compatibilidad y esquema.
- [ ] T6. GREEN de publicación, validación y esquema.
- [ ] T7. Verificar propiedades acotadas y distribución final integrada.
- [ ] T8. Revisar independientemente y resolver hallazgos.
- [ ] T9. Cerrar con evidencia, aceptación y Memory Bank.

## Estrategia

Ejecución secuencial. Cada rol/subfase recibe paquete y sesión propios. Solo se prepara el encargo siguiente tras cerrar el anterior.

La autoridad vigente aprueba; el architect no aprueba sus propuestas. La materialización corresponde al orquestador.

Los nombres de clases y módulos siguientes son productos propuestos, no interfaces existentes:

| Grupo propuesto | Compromiso |
|---|---|
| `TestEngagement` | PC-01–03 |
| `TestOdooApplicability` | PC-04–05, matriz por rol y frontera de addon |
| `TestAgentBinding` | PC-06–08 y parte de PC-12.b |
| `TestDispatchDoctrine` | PC-09, incluidas ambas cláusulas de «otro valor» |
| `TestRequestSchema` | PC-10 y parte de PC-12.b |
| `TestDistribution` | PC-11 y PC-12.a |
| Dictamen independiente | PC-13 y suficiencia semántica de las anteriores |

Tests focalizados propuestos: `tests/test_010_002_documentary_role_integration.py`.

Propiedades propuestas: `tests/test_010_002_documentary_role_properties.py`.

Los verificadores observan interfaces públicas y artefactos distribuidos. El test-writer no inspecciona implementación ni el documento producido para deducir el oráculo. Las salidas de fallo no vuelcan fuentes completas.

**Separación de distribución:** T4 no exige CLI ni esquema corregidos por T6. T6/T7 acreditan PC-12.b con una instalación actualizada; los controles finales se alojan en los grupos de agente y esquema.

**Separación de garantías de destinatario:** la preparación ordinaria y `prepare --replace-packet` garantizan por construcción el agente publicado, derivado del rol y stack vigente. La validación compartida rechaza estáticamente agentes de otro rol; el registro de un intento nuevo con agente declarado contrasta además el stack vigente. La recepción, la repetición idéntica y la finalización válida del write-ahead no añaden ese contraste temporal. Un histórico admitido sin contexto ni agente puede registrar un intento nuevo sin contraste contextual del destinatario ni derivación o sustitución silenciosa.

## T1 — Aprobación y materialización

**Responsables:** autoridad vigente y orquestador.

- Materializar fielmente spec y plan v4.
- Obtener aprobación recuperable antes de RED/GREEN.
- Registrar decisiones, alcance, verificaciones y exclusiones.
- Preparar únicamente el paquete de AUDIT.

**Archivos de rol:** ninguno; materialización por el orquestador.

**Gate:** spec y plan aprobados. La entrega de este texto no constituye aprobación.

## T2 — AUDIT independiente

**Rol:** test-writer, subfase `audit`.

Contrastar cada postcondición con su oráculo y consecuencia observable:

- Distinguir presencia textual y suficiencia de las cláusulas.
- Cubrir las matrices de PC-04/05 sin usar el `write_scope` del reviewer o architect como descripción del producto.
- Cubrir documentación dentro de un módulo, verificador documental y diff de addon contrario a la etiqueta.
- Separar el contraste estático agente↔rol de la comparación contra el stack vigente.
- Clasificar en `consequence` la preparación ordinaria y el reemplazo como **garantía por construcción**, verificando el agente publicado, no como ramas de rechazo de agente inyectado alcanzables mediante CLI.
- Cubrir reemplazo de predecesor histórico sin agente y reemplazo tras cambio de stack.
- Identificar separadamente el rechazo estático de `validate-request`/`render` y el rechazo contextual de un intento nuevo con agente declarado por `record-dispatch`.
- Cubrir el intento nuevo histórico sin contexto ni agente, sin contraste contextual del destinatario ni derivación o sustitución silenciosa.
- Separar intentos nuevos de recepción histórica, repetición idéntica y finalización válida del write-ahead.
- Cubrir presencia condicionada de `agent`, históricos sin ambos campos y render sin agente entre requests válidos.
- Separar rechazo mecánico externo y obligación procedimental nativa.
- Confirmar PC-12.a en T4 y PC-12.b en T6/T7.
- Confirmar aislamiento y límites de ambos runtimes.

### Medición de fixtures existentes

El AUDIT debe medir, no estimar:

1. Fixtures con `agent` discordante respecto de su rol y estado, distinguiendo discordancia estática de rol y discordancia contextual de stack.
2. Fixtures que simulan históricos quitando `agent` pero conservan `execution_context`.
3. Oráculos afectados por la condición nueva, el contraste estático y la distinción temporal del intento.
4. Fixtures y oráculos de reemplazo afectados por la rederivación del agente del sucesor.

Registrar método, selección, comandos, resultados, ubicaciones y clasificación: caso negativo intencional, fixture válido afectado o pendiente.

El test-writer utiliza tests, contrato e interfaces públicas autorizadas; no lee implementación para reconstruir el resultado.

Se identificaron simulaciones que eliminan solo `agent` en:

- `tests/test_006_005_u1c_packet_agent.py:245-355`.
- `tests/test_006_005_u1b_dispatch_entry.py:819-837`.
- `tests/test_006_005_u2_opencode_module.py:936-955`.

La interfaz pública de reemplazo se utiliza en `tests/test_007_002_dispatch_recovery.py:526-570`.

Estos archivos están previstos en T5 y sus regresiones pertinentes en T6. **Las listas de T5/T6 no sustituyen la medición completa obligatoria de T2**, ni se consideran un inventario exhaustivo de fixtures afectados.

Las adaptaciones legítimas se realizan en RED, nunca desde GREEN. Si aparecen archivos necesarios no enumerados en T5, se detiene esa adaptación y el orquestador actualiza el alcance y obtiene la aprobación requerida antes de continuar.

**Salida:** informe FINAL TEXT; materialización por el orquestador.

**Gate:** mapa PC→verificación suficiente, consecuencias correctamente clasificadas, impacto de fixtures medido y dudas contractuales resueltas antes de RED.

## T3 — RED de instrucciones y distribución

**Rol:** test-writer, subfase `red`.

**Archivo:** `tests/test_010_002_documentary_role_integration.py`.

Construir `TestEngagement`, `TestOdooApplicability`, `TestDispatchDoctrine` y `TestDistribution`.

```sh
python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py \
  -k 'TestEngagement or TestOdooApplicability or TestDispatchDoctrine or TestDistribution'
```

El harness:

- Usa el aislamiento de `tests/conftest.py`.
- Genera en una copia descartable cuando necesite escribir.
- Instala con `CDAD_INSTALL_ROOT` propio y `CDAD_SKILL_EXTRA_DIRS=""`.
- Comprueba origen y bytes, no la instalación global.
- Comprueba alcance documental explícito y separación de insumos.
- Verifica documental genérico y documental/Odoo.
- Verifica ambos runtimes sin prometer sesiones vivas.
- Cubre en `TestDispatchDoctrine` tanto `skills/cdad-cycle/SKILL.md` como `sub-agent-strategies.md`: cualquier stack no vacío deriva sufijo; «otro valor» no activa genérico.
- Limita `TestDistribution` a PC-11 y PC-12.a.

**Gate RED:** fallos por obligaciones ausentes o contradictorias, no por imports, dependencias o fixtures rotos. Los controles de conservación ya verdes se registran como tales.

## T4 — GREEN de instrucciones, referencias y generación

**Rol:** implementer, subfase `green`.

**Archivos previstos:**

- `sources/roles/{orchestrator,architect,test-writer,implementer,reviewer,scribe}.md`.
- `sources/agents/adapters/{opencode,claude-code}.md`.
- `skills/cdad-cycle/SKILL.md`.
- `skills/cdad-cycle/references/{handoff-prompts,sub-agent-strategies}.md`.
- `skills/{odoo-architect,odoo-test-writer,odoo-expert,odoo-reviewer,odoo-make-env}/SKILL.md`.
- Salidas generadas bajo `agents/` y staging.

### Inventario acotado de referencias Odoo

Examinar y registrar aplicabilidad, consumidores y decisión de inclusión de:

- `skills/odoo-expert/references/evidence-and-quality.md`.
- `skills/odoo-make-env/references/run-budget-protocol.md`.
- `skills/odoo-make-env/references/odoo-sh.md`.
- `skills/odoo-make-env/references/odoo-19-traps.md`.

Estos archivos son **candidatos delimitados**, no una obligación de modificarlos todos. Antes de editarlos, el orquestador confirma su inclusión en el `write_scope` del paquete de T4.

La decisión debe distinguir:

- Una obligación incondicional que requiere delimitarse.
- Una regla ya contextualizada a ejecutar o verificar un addon.
- Una referencia técnica sin conflicto.

Solo se admite la corrección de aplicabilidad necesaria para PC-04/05. No se alteran recetas, presupuestos, APIs, catálogos ni normas ajenas al compromiso. Si se descubre otra superficie necesaria fuera de la lista, se detiene esa parte y se reencauza.

### Implementación y verificación

- Aplicar la matriz por rol y la frontera de addon.
- Conservar cargas de dominio y permisos.
- Corregir «otro valor» y fallback en todas las superficies de PC-09.
- Limitar modificaciones de rol a obligaciones operativas, punteros y aplicabilidad.
- No duplicar la norma documental compartida.
- No editar agentes manualmente.

Verificar:

```sh
python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py \
  -k 'TestEngagement or TestOdooApplicability or TestDispatchDoctrine or TestDistribution'
make agents
```

Repetir la generación y comparar bytes y manifiestos, incluidos promovidos frente a staging.

**Regresiones de T4:**

- `tests/test_cdad_generate.py`.
- `tests/test_010_001_documentary_contracts.py`.
- `tests/test_install_ownership.py`.
- `tests/test_install_review5_regressions.py`.
- `tests/test_007_006_withdraw_and_republish.py`.
- `tests/validate-odoo-specialization.sh`.

Todas con entorno y destino aislados cuando corresponda.

**Gate:** grupo de T3 verde, PC-12.a acreditada, inventario resuelto y diff conforme. Este gate no exige PC-12.b. Modificar generador, instalador, guardas o permisos obliga a detener y volver al orquestador.

## T5 — RED de publicación, coherencia, compatibilidad y esquema

**Rol:** test-writer, subfase `red`.

**Archivos:**

- `tests/test_010_002_documentary_role_integration.py`.
- `tests/test_006_005_u1c_packet_agent.py`.
- `tests/test_006_005_u1b_dispatch_entry.py`.
- `tests/test_006_005_u2_opencode_module.py`.
- `tests/test_007_002_dispatch_recovery.py`.

Los tres archivos `006_005` se modifican únicamente para adaptar fixtures y oráculos legítimamente afectados por las nuevas obligaciones, sin debilitar sus comprobaciones restantes. El archivo de recuperación incorpora o adapta las verificaciones de reemplazo afectadas por la rederivación del agente. Su inclusión no sustituye la medición completa de T2.

Construir `TestAgentBinding` y `TestRequestSchema`, y los casos de transición de reemplazo correspondientes.

### Ejecución obligatoria antes de GREEN

Ejecutar cada comando y conservar su resultado, sin omitir los siguientes porque otro haya fallado:

```sh
python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py \
  -k 'TestAgentBinding or TestRequestSchema'

python3 -B -m pytest -q tests/test_006_005_u1c_packet_agent.py

python3 -B -m pytest -q tests/test_006_005_u1b_dispatch_entry.py

python3 -B -m pytest -q tests/test_006_005_u2_opencode_module.py

python3 -B -m pytest -q tests/test_007_002_dispatch_recovery.py
```

Antes de ejecutar, declarar para **cada archivo** los casos con RED esperado por una obligación todavía no implementada y los controles de conservación que deben seguir verdes. Después, registrar comando, selección, revisión medida, salida, rc, esperado frente a observado y causa de cada fallo.

Un archivo cuya adaptación solo conserva compatibilidad puede permanecer verde; se declara expresamente. No se fabrica un fallo para obtener un RED por archivo ni se acepta un fallo de fixture como evidencia de defecto del producto.

### Comportamientos comprometidos

- Preparación de destinatario genérico y Odoo: verificar el agente publicado como garantía por construcción y registrar como tales los controles ya verdes.
- `prepare --replace-packet` de un predecesor histórico admitido sin agente: el sucesor publica `execution_context` y el agente derivado del rol y stack vigente.
- `prepare --replace-packet` tras cambiar el stack: el sucesor publica el agente del stack vigente, no el copiado del predecesor.
- Los reemplazos se ejercitan mediante CLI público y con sus demás precondiciones satisfechas. Se verifica el sucesor y la conservación de los bytes históricos del predecesor y de sus registros, sin suprimir los efectos de recuperación ya autorizados.
- Request con agente de otro rol: `validate-request` rechaza y `render` no produce un paquete válido. El diagnóstico corresponde al contraste estático y no depende del stack vigente.
- Request con agente del mismo rol: el contraste estático no impone que su sufijo coincida con un stack posterior ni acredita publicación de variante.
- Intento nuevo con agente declarado discordante respecto del stack vigente: rechazo en el registro previo, con diagnóstico y sin nuevos efectos comprometidos.
- Adaptador externo sin lanzamiento del trabajo de rol tras rechazo de su registro previo.
- `execution_context` presente sin `agent`: rechazo.
- Histórico sin ambos campos: admisión.
- **Intento nuevo sobre ese histórico:** registro admitido sin contraste contextual del destinatario y sin derivación o sustitución silenciosa de agente. Se verifican el resultado durable y la conservación de los campos ausentes del request; no se relajan otras precondiciones ni se promete lanzamiento sin destinatario.
- Render sin `agent` entre requests válidos, preservando el conjunto de metadata.
- Paquete publicado y despachado: cambiar solo stack no provoca nuevo rechazo de recepción, verificación o continuidad por coherencia contextual del destinatario.
- Registro existente: cambiar solo stack y repetir la observación idéntica conserva la idempotencia, los bytes y las transiciones pendientes previstas.
- Write-ahead ya iniciado: cambiar solo stack durante la ejecución no impide completar una vez el registro del mismo intento con su identidad fija y las demás precondiciones existentes.
- Después de ese cambio, un intento nuevo con agente declarado discordante se rechaza sin alterar el paquete ni los registros anteriores.
- Se conserva el rechazo de reutilización de un identificador con datos distintos fuera de la finalización admitida; la excepción temporal no habilita un intento nuevo encubierto.
- Variante ausente: rechazo mecánico externo; la vía nativa se verifica como doctrina procedimental.
- Evaluación real de JSON Schema.
- Instalación aislada de CLI y esquema finales para PC-12.b, sin exigirlos antes de T6.

Las transiciones de reemplazo y write-ahead→cambio de stack→finalización se acreditan por sus efectos durables mediante interfaces públicas. No se simula una API interna para inventar un rechazo de agente inyectado en `prepare`.

### Adaptación de históricos

Las pruebas que antes quitaban solo `agent` deben distinguir:

- Request con contexto sin agente: ahora es un caso negativo.
- Histórico sin ambos campos: sigue siendo un caso positivo, incluido el registro de un intento nuevo conforme a D3.
- Exclusión de agente del render: comparar requests válidos, sin contexto declarado, que difieran solo en presencia o valor de `agent`; todo agente presente debe satisfacer el contraste estático del rol.

Si para simular un histórico se elimina `execution_context`, también debe construirse su paquete canónico correspondiente: ese campo sí participa en metadata. No se compara contra el paquete moderno como si sus bytes fueran iguales.

Cada cambio de oráculo registra obligación anterior, obligación nueva y razón, sin debilitar las comprobaciones restantes. Los oráculos de reemplazo no exigen conservar el agente del predecesor: el sucesor lo rederiva conforme a P-4.

El motor de JSON Schema se resuelve antes de RED. Su ausencia es bloqueo de entorno, no defecto del producto.

**Gate RED:** los cinco archivos previstos han sido ejecutados; resultados esperados y observados registrados por archivo; fallos atribuibles a comportamientos comprometidos y no a fixtures rotos; garantías por construcción clasificadas como tales; reemplazo e histórico sin agente cubiertos; adaptaciones de fixtures aprobadas y protegidas antes de GREEN.

## T6 — GREEN de publicación, validación y esquema

**Rol:** implementer, subfase `green`.

**Archivos:**

- `skills/cdad-cycle/scripts/cdad_packet.py`.
- `skills/cdad-cycle/assets/packet-request.schema.json`.

Implementar:

- Contraste estático agente↔rol en la validación compartida del request, mediante el nombre genérico exacto o su prefijo completo con sufijo no vacío, sin consultar stack.
- Conservación de la derivación canónica y de la garantía por construcción de la preparación ordinaria.
- Rederivación del agente del sucesor en `prepare --replace-packet` mediante el mismo productor canónico, usando rol y stack vigente, sin copiar el agente del predecesor.
- Publicación del sucesor con contexto y agente derivado tanto para predecesor histórico sin agente como para stack cambiado; conservación de las demás reglas de reemplazo y publicación transaccional.
- Comprobación contextual compartida al preparar/publicar requests nuevos —ordinarios o por reemplazo— y al registrar intentos nuevos con agente declarado, usando la derivación canónica.
- Admisión del intento nuevo sobre histórico sin contexto ni agente sin contraste contextual del destinatario, derivación ni sustitución silenciosa, conservando las demás precondiciones del registro.
- Exclusión de la repetición idéntica y de la finalización válida del write-ahead del contraste contra el stack vigente; conservar sus reglas de identidad, única finalización, idempotencia y transiciones.
- Ausencia de reevaluación contra stack vigente en recepción y lectura de paquetes publicados, manteniendo el contraste estático y las demás validaciones.
- Requisito de agente cuando existe contexto.
- Corrección estructural y condición de campos en el esquema.
- Conservación del render y compatibilidad comprometida.

La reutilización de validación no autoriza introducir el contraste temporal en todos sus llamadores. Las excepciones temporales y la compatibilidad histórica no suprimen otras precondiciones. No se añaden selectores, campos ni flags públicos.

```sh
python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py
```

Actualizar la instalación aislada y acreditar CLI y esquema de PC-12.b.

**Regresiones de T6:**

- `tests/test_packet_prepare.py`.
- `tests/test_006_005_u1c_packet_agent.py`.
- `tests/test_006_005_u1b_dispatch_entry.py`.
- `tests/test_role_packet_render.py`.
- `tests/test_role_packet_consumers.py`.
- `tests/test_008_004_packet_enforcement.py`.
- `tests/test_006_005_u2_opencode_module.py`.
- `tests/test_007_002_dispatch_recovery.py`.

Esta lista tampoco sustituye la medición completa de T2.

**Gate:** módulo focalizado y regresiones verdes; garantía por construcción en ambas vías de publicación; reemplazos histórico y tras cambio de stack; contraste estático; intento nuevo histórico sin agente; y estabilidad temporal de recepción, repetición y finalización acreditados. Ningún cambio de render o esquema fuera del aprobado. El implementer no corrige tests.

## T7 — Propiedades y recorrido integrado final

**Rol:** test-writer, subfase `properties`.

**Archivo:** `tests/test_010_002_documentary_role_properties.py`.

Verificar la parte generable de INV-04:

- La publicación nueva deriva un agente coherente, como garantía por construcción.
- La validación compartida rechaza una discordancia estática de rol, sin depender del stack vigente.
- En el registro de un intento nuevo con agente declarado, una discordancia contextual se rechaza.
- La regla de presencia agente/contexto se conserva.

Registrar semilla, dominio y presupuesto acotado antes de ejecutar. No se exige una biblioteca de propiedades concreta; si no está disponible, se utiliza un generador determinista con semilla que respete el contrato.

El reemplazo de predecesor histórico, el reemplazo tras cambio de stack, el intento nuevo histórico sin agente, la recepción, la repetición idéntica y la finalización write-ahead permanecen como pruebas de sus transiciones y consecuencias observables, no como cuotas de escenarios aleatorios.

```sh
python3 -B -m pytest -q \
  tests/test_010_002_documentary_role_integration.py \
  tests/test_010_002_documentary_role_properties.py
```

Ejecutar sobre la instalación aislada actualizada después de T6 y conservar evidencia de:

- PC-12.a y PC-12.b.
- Encargo documental genérico y documental con `stack=odoo`.
- Bytes y procedencia de CLI, esquema, agentes, skills y referencias.
- Fronteras de escritura, límites de runtime y simulaciones.

Si se necesita un verificador E2E adicional, requiere otro paquete de subfase `e2e`; no se mezclan instrucciones en el de propiedades.

**Gate:** propiedades e integración verdes, sin skips de promesas y con límites identificados.

## T8 — Review independiente

**Rol:** reviewer read-only, distinto del implementer conforme al contrato vigente.

Revisar:

- PC-01–13 e invariantes, incluidos PC-12.a/b.
- D-1–D-5 y P-1–P-4 sin agentes, campos, selectores ni permisos nuevos.
- Aplicabilidad Odoo por rol y diff real.
- Documentación dentro de módulos y parte funcional declarada.
- Inventario de referencias, decisiones de inclusión y ausencia de obligaciones contradictorias.
- Distinción entre contraste estático de rol y contraste temporal de stack.
- Las tres vías de PC-07/EV-03, incluida la clasificación de **preparación ordinaria y reemplazo** como garantía por construcción.
- Rederivación del sucesor en los casos de predecesor histórico sin agente y cambio de stack, sin copia del agente anterior ni reescritura histórica.
- Momento del contraste contextual: publicación e intento nuevo con agente declarado frente a recepción, repetición idéntica y finalización write-ahead.
- Intento nuevo histórico sin contexto ni agente admitido sin contraste contextual del destinatario, derivación ni sustitución silenciosa.
- Conservación de identidad, integridad, continuidad, idempotencia y única finalización; ninguna excepción permite reescribir historia o encubrir otro intento.
- Compatibilidad de fixtures sin falsear históricos.
- Medición completa de T2, adaptaciones por el test-writer antes de GREEN y ejecución de los cinco archivos de T5 con esperado frente a observado.
- Distinción mecánica/procedimental de variante ausente.
- Eliminación de «otro valor → genérico» en las dos superficies.
- Procedencia de generación e instalación.
- Separación entre estructura y juicio semántico.

**Salida:** FINAL TEXT con ubicaciones, consecuencias, condiciones de cierre y abstenciones.

Las correcciones vuelven al rol competente. Los cambios de oráculo vuelven al test-writer y los de contrato requieren aprobación. El reviewer no edita.

**Gate:** bloqueantes resueltos y re-verificados.

## T9 — Cierre

**Responsables:** quien cierra y orquestador; aceptación por la autoridad vigente.

- Aplicar la política canónica de suite completa de cierre.
- Conservar comandos, revisión medida, salidas, skips, canarios y límites.
- Completar PC→evidencia.
- Declarar la deriva de instalación global si continúa.
- Obtener aceptación funcional.
- Despachar al scribe para borradores de Memory Bank; materializar solo tras aprobación.
- No publicar, hacer push ni actualizar el HOME real.
- No atribuir resultados del piloto ni cerrar la épica.

Comando previsto:

```sh
python3 scripts/cdad-suite.py close --all \
  --evidence-root .cdad/evidence/010-002-closure
```

**Gate:** contrato acreditado, aceptación recuperable y cierre dentro del alcance.

## Regresiones pertinentes

La asignación es idéntica en prosa y `plan-tasks`.

| Tarea | Regresiones o archivos existentes de verificación |
|---|---|
| T4 | `test_cdad_generate.py`, `test_010_001_documentary_contracts.py`, `test_install_ownership.py`, `test_install_review5_regressions.py`, `test_007_006_withdraw_and_republish.py`, `validate-odoo-specialization.sh` |
| T5 | Ejecución antes de GREEN de `test_006_005_u1c_packet_agent.py`, `test_006_005_u1b_dispatch_entry.py`, `test_006_005_u2_opencode_module.py` y `test_007_002_dispatch_recovery.py`, además del módulo nuevo focalizado; esperado frente a observado por archivo. |
| T6 | `test_packet_prepare.py`, `test_006_005_u1c_packet_agent.py`, `test_006_005_u1b_dispatch_entry.py`, `test_role_packet_render.py`, `test_role_packet_consumers.py`, `test_008_004_packet_enforcement.py`, `test_006_005_u2_opencode_module.py`, `test_007_002_dispatch_recovery.py` |

Todos los archivos están bajo `tests/`.

Las listas no sustituyen la medición completa obligatoria de fixtures de T2. Una superficie adicional necesaria se reencauza antes de modificarla.

Si se utiliza `make validate`, debe ejecutarse con destino y entorno aislados. Una comparación contra la instalación global desactualizada no acredita regresión ni pase.

## Proyección estructurada (`plan-tasks`)

El bloque proyecta las mismas tareas, archivos, comprobaciones y gates. No autoriza escrituras por sí mismo: cada paquete delimita su `write_scope`.

```plan-tasks
{
  "validation_strategy": "Ejecucion secuencial con paquete y sesion por rol/subfase. T1 y T8 se acreditan por observable_checks. T2 mide cobertura y fixtures completos y clasifica preparacion ordinaria y reemplazo como garantia por construccion en consequence. T3/T4 cubren instrucciones y PC-12.a. T5/T6 cubren ambas vias publicas de publicacion, contraste estatico de rol, coherencia temporal de intentos nuevos con agente declarado, compatibilidad historica, esquema y PC-12.b. T5 ejecuta el modulo nuevo y los cuatro archivos existentes previstos, con esperado frente a observado por archivo. El sucesor rederiva agent del rol y stack vigente, incluso ante predecesor historico sin agente o stack cambiado. Un historico admitido sin contexto ni agente puede registrar un intento nuevo sin contraste contextual del destinatario y sin derivacion ni sustitucion silenciosa. Recepcion, repeticion identica y finalizacion valida del write-ahead no reevaluan el stack vigente. T7 verifica propiedades acotadas e integracion final. Se aplica la politica canonica de suite completa en T9. Ningun control estructural acredita fidelidad semantica ni conducta de modelos. Todas las escrituras de pruebas e instalacion usan entornos propios.",
  "tasks": [
    {
      "id": "T1",
      "detail": "next",
      "depends_on": [],
      "parallel": [],
      "files": [],
      "focal_tests": [],
      "observable_checks": [
        "Materializacion fiel de spec y plan v4 y aprobacion recuperable por la autoridad vigente.",
        "Preparar solo el paquete de AUDIT; los siguientes se preparan tras cerrar el anterior."
      ],
      "regressions": [],
      "integration_gate": "Spec y plan aprobados sin inferir aprobacion de la entrega.",
      "owner": "Autoridad vigente y orquestador."
    },
    {
      "id": "T2",
      "detail": "next",
      "depends_on": ["T1"],
      "parallel": [],
      "files": [],
      "focal_tests": [],
      "observable_checks": [
        "Mapa PC-01..PC-13, incluidos PC-12.a/b, a verificacion estructural o revision independiente.",
        "Matriz Odoo por rol, frontera de addon y diff real.",
        "Clasificar en consequence preparacion ordinaria y prepare --replace-packet como garantia por construccion mediante el agente publicado, no como rechazo publico de agente inyectado; separar rechazo estatico en validate-request/render y rechazo contextual de intento nuevo con agente declarado en record-dispatch.",
        "Cubrir sucesor de predecesor historico sin agente y sucesor tras cambio de stack: ambos rederivan el agente del rol y stack vigente.",
        "Separar contraste estatico de rol y temporal de stack; distinguir intento nuevo, recepcion, repeticion identica y finalizacion valida del write-ahead.",
        "Cubrir intento nuevo sobre historico admitido sin execution_context ni agent: registro sin contraste contextual del destinatario y sin derivacion ni sustitucion silenciosa.",
        "Medicion completa de fixtures con agent discordante respecto de rol/estado, historicos simulados quitando solo agent y oraculos de reemplazo afectados; registrar metodo, seleccion, comandos, resultados, ubicaciones y clasificacion.",
        "Las listas de archivos y regresiones de T5/T6 no sustituyen la medicion completa obligatoria de T2.",
        "Resolver alcance exacto de adaptaciones antes de RED; archivos adicionales requieren actualizar el plan y la autorizacion correspondiente."
      ],
      "regressions": [],
      "integration_gate": "Mapa suficiente, consecuencias correctamente clasificadas, impacto medido y dudas contractuales resueltas.",
      "owner": "test-writer (audit); orquestador materializa."
    },
    {
      "id": "T3",
      "detail": "next",
      "depends_on": ["T2"],
      "parallel": [],
      "files": [
        "tests/test_010_002_documentary_role_integration.py"
      ],
      "focal_tests": [
        "python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py -k 'TestEngagement or TestOdooApplicability or TestDispatchDoctrine or TestDistribution'"
      ],
      "observable_checks": [
        "RED por obligaciones ausentes o contradictorias, no por entorno ni fixtures rotos; controles ya verdes identificados.",
        "TestDispatchDoctrine cubre otro valor en skills/cdad-cycle/SKILL.md y sub-agent-strategies.md: todo stack no vacio deriva sufijo.",
        "TestDistribution cubre PC-11 y PC-12.a, sin exigir CLI/esquema corregidos por T6.",
        "Instalacion aislada, origen y bytes; encargos documental generico y documental/Odoo."
      ],
      "regressions": [],
      "integration_gate": "RED verificado y verificadores protegidos antes de GREEN.",
      "owner": "test-writer (red)."
    },
    {
      "id": "T4",
      "detail": "next",
      "depends_on": ["T3"],
      "parallel": [],
      "files": [
        "sources/roles/orchestrator.md",
        "sources/roles/architect.md",
        "sources/roles/test-writer.md",
        "sources/roles/implementer.md",
        "sources/roles/reviewer.md",
        "sources/roles/scribe.md",
        "sources/agents/adapters/opencode.md",
        "sources/agents/adapters/claude-code.md",
        "skills/cdad-cycle/SKILL.md",
        "skills/cdad-cycle/references/handoff-prompts.md",
        "skills/cdad-cycle/references/sub-agent-strategies.md",
        "skills/odoo-architect/SKILL.md",
        "skills/odoo-test-writer/SKILL.md",
        "skills/odoo-expert/SKILL.md",
        "skills/odoo-reviewer/SKILL.md",
        "skills/odoo-make-env/SKILL.md",
        "skills/odoo-expert/references/evidence-and-quality.md",
        "skills/odoo-make-env/references/run-budget-protocol.md",
        "skills/odoo-make-env/references/odoo-sh.md",
        "skills/odoo-make-env/references/odoo-19-traps.md",
        "agents/"
      ],
      "focal_tests": [
        "python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py -k 'TestEngagement or TestOdooApplicability or TestDispatchDoctrine or TestDistribution'",
        "make agents"
      ],
      "observable_checks": [
        "Inventario de las cuatro referencias candidatas: aplicabilidad, consumidores, contradiccion y decision de inclusion; confirmar write_scope antes de editar.",
        "Correccion acotada de aplicabilidad por rol y de seleccion, sin alterar recetas, presupuestos, APIs, permisos ni normas ajenas.",
        "Grupo T3 verde; dos generaciones identicas y promovidos coincidentes con staging.",
        "PC-12.a acreditada con agentes, skills y referencias; no exigir PC-12.b en este gate.",
        "Ningun agente editado manualmente ni techo estatico elevado."
      ],
      "regressions": [
        "tests/test_cdad_generate.py",
        "tests/test_010_001_documentary_contracts.py",
        "tests/test_install_ownership.py",
        "tests/test_install_review5_regressions.py",
        "tests/test_007_006_withdraw_and_republish.py",
        "tests/validate-odoo-specialization.sh"
      ],
      "integration_gate": "Grupo verde, inventario resuelto, PC-12.a y diff conformes; otra superficie o cambios de generador/instalador/guardas/permisos vuelven al orquestador.",
      "owner": "implementer (green)."
    },
    {
      "id": "T5",
      "detail": "next",
      "depends_on": ["T4"],
      "parallel": [],
      "files": [
        "tests/test_010_002_documentary_role_integration.py",
        "tests/test_006_005_u1c_packet_agent.py",
        "tests/test_006_005_u1b_dispatch_entry.py",
        "tests/test_006_005_u2_opencode_module.py",
        "tests/test_007_002_dispatch_recovery.py"
      ],
      "focal_tests": [
        "python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py -k 'TestAgentBinding or TestRequestSchema'",
        "python3 -B -m pytest -q tests/test_006_005_u1c_packet_agent.py",
        "python3 -B -m pytest -q tests/test_006_005_u1b_dispatch_entry.py",
        "python3 -B -m pytest -q tests/test_006_005_u2_opencode_module.py",
        "python3 -B -m pytest -q tests/test_007_002_dispatch_recovery.py"
      ],
      "observable_checks": [
        "Ejecutar los cinco comandos aun cuando otro falle. Declarar por archivo los casos con RED esperado y los controles de conservacion verdes; registrar comando, seleccion, revision medida, salida, rc, esperado frente a observado y causa de cada fallo.",
        "Una adaptacion de conservacion puede quedar verde; declararlo sin fabricar fallos. Ningun fallo de fixture acredita RED del producto.",
        "Preparacion ordinaria generica y Odoo: agente publicado coherente, clasificado como garantia por construccion; controles ya verdes identificados.",
        "prepare --replace-packet de predecesor historico admitido sin agente publica sucesor con execution_context y agente derivado del rol y stack vigente.",
        "prepare --replace-packet tras cambio de stack publica agente del stack vigente, no una copia del anterior. Verificar por CLI publico el sucesor y los bytes historicos conservados, manteniendo las demas precondiciones y efectos autorizados de recuperacion.",
        "validate-request rechaza agent de otro rol y render no produce paquete valido; contraste estatico por nombre generico exacto o prefijo completo con sufijo no vacio, sin consultar stack.",
        "Un agent del mismo rol no se rechaza en lectura solo por diferir del stack posterior; el contraste estatico no acredita publicacion de variante.",
        "Intento nuevo con agente declarado discordante con stack vigente rechazado en record-dispatch con diagnostico y ausencia de efectos comprometidos; adaptador externo no lanza el trabajo de rol tras fallo del registro previo.",
        "Contexto sin agent rechazado; historicos sin ambos admitidos; agent excluido del render entre requests validos.",
        "Intento nuevo sobre historico admitido sin contexto ni agente registra sin contraste contextual del destinatario y sin derivar ni sustituir agente en silencio; comprobar resultado durable y campos ausentes conservados, sin relajar otras precondiciones ni prometer lanzamiento sin destinatario.",
        "Cambio solo de stack no invalida recepcion/verificacion/continuidad por coherencia contextual del destinatario.",
        "Tras cambiar solo stack, repeticion identica conserva idempotencia, bytes y transiciones pendientes previstas.",
        "Write-ahead iniciado, cambio solo de stack durante ejecucion y finalizacion valida del mismo intento: registro final durable, identidad fija y unica finalizacion conservadas.",
        "Un intento nuevo con agente declarado discordante tras ese cambio se rechaza sin alterar paquete ni registros anteriores; reutilizar identificador con datos distintos fuera de la finalizacion admitida sigue rechazado.",
        "Adaptar solo fixtures y oraculos legitimamente afectados de los tres archivos 006_005 antes de GREEN: comparar renders entre requests validos sin contexto y reconstruir paquete historico canonico si cambia metadata.",
        "Incorporar o adaptar en test_007_002_dispatch_recovery.py los oraculos de reemplazo afectados por la rederivacion, registrando obligacion anterior, nueva y razon sin debilitar otras comprobaciones.",
        "Las listas de T5/T6 no sustituyen la medicion completa obligatoria de T2; otros archivos necesarios requieren reencauce antes de editar.",
        "Variante ausente mecanica en adaptador externo y procedimental en via nativa.",
        "Motor real de JSON Schema resuelto; tests de CLI/esquema instalados cubren PC-12.b."
      ],
      "regressions": [],
      "integration_gate": "Cinco archivos ejecutados con esperado y observado por archivo; RED por comportamientos comprometidos, no por fixtures rotos; garantias por construccion clasificadas como tales; reemplazos e intento nuevo historico sin agente cubiertos; adaptaciones aprobadas y protegidas. Otros archivos medidos exigen actualizar alcance antes de editarlos.",
      "owner": "test-writer (red)."
    },
    {
      "id": "T6",
      "detail": "next",
      "depends_on": ["T5"],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/scripts/cdad_packet.py",
        "skills/cdad-cycle/assets/packet-request.schema.json"
      ],
      "focal_tests": [
        "python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py"
      ],
      "observable_checks": [
        "Contraste estatico agent/role en validacion compartida, sin consultar stack; preparacion ordinaria conserva derivacion canonica y garantia por construccion.",
        "prepare --replace-packet rederiva agent del sucesor mediante el productor canonico usando rol y stack vigente; no copia el agente del predecesor.",
        "Sucesor con contexto y agente derivado ante predecesor historico sin agente y ante stack cambiado; conservar las demas reglas de reemplazo y publicacion transaccional.",
        "Comprobacion contextual compartida solo al preparar/publicar request nuevo, ordinario o por reemplazo, y registrar intento nuevo con agente declarado, usando derivacion canonica.",
        "Historico admitido sin execution_context ni agent registra intento nuevo sin contraste contextual del destinatario y sin derivacion ni sustitucion silenciosa; conserva las demas precondiciones.",
        "Repeticion identica y finalizacion valida del write-ahead no reevaluan stack vigente; conservar identidad, unica finalizacion, idempotencia, transiciones y demas precondiciones.",
        "Recepcion y lectura publicadas no reinterpretan agent contra stack vigente; conservan contraste estatico y presencia de agent condicionada al contexto.",
        "Esquema cerrado con ambas propiedades y dependencia de campos; render y compatibilidad conservados.",
        "Instalacion aislada actualizada con CLI y esquema corregidos para PC-12.b.",
        "Las regresiones enumeradas no sustituyen la medicion completa de T2; el implementer no adapta tests."
      ],
      "regressions": [
        "tests/test_packet_prepare.py",
        "tests/test_006_005_u1c_packet_agent.py",
        "tests/test_006_005_u1b_dispatch_entry.py",
        "tests/test_role_packet_render.py",
        "tests/test_role_packet_consumers.py",
        "tests/test_008_004_packet_enforcement.py",
        "tests/test_006_005_u2_opencode_module.py",
        "tests/test_007_002_dispatch_recovery.py"
      ],
      "integration_gate": "Modulo focalizado y regresiones verdes; garantia por construccion en ambas vias de publicacion, reemplazos historico y tras cambio de stack, contraste estatico, intento nuevo historico sin agente y estabilidad temporal de recepcion, repeticion y finalizacion acreditados; sin editar tests ni cambiar render/esquema fuera del contrato.",
      "owner": "implementer (green)."
    },
    {
      "id": "T7",
      "detail": "next",
      "depends_on": ["T6"],
      "parallel": [],
      "files": [
        "tests/test_010_002_documentary_role_properties.py"
      ],
      "focal_tests": [
        "python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py tests/test_010_002_documentary_role_properties.py"
      ],
      "observable_checks": [
        "Parte generable de INV-04 con semilla, dominio y presupuesto registrados; sin biblioteca concreta obligatoria.",
        "Publicacion nueva coherente por construccion, rechazo estatico de otro rol sin depender de stack, rechazo contextual de intento nuevo con agente declarado discordante y regla agent/contexto.",
        "Reemplazo historico y tras cambio de stack, intento nuevo historico sin agente, recepcion, repeticion identica y finalizacion write-ahead acreditados por sus transiciones y consecuencias observables, no por cuotas aleatorias.",
        "PC-12.a/b sobre instalacion final; documental generico y documental/Odoo con origen, bytes y fronteras conservados.",
        "Limites y simulaciones identificados; otro verificador E2E requiere paquete de esa subfase."
      ],
      "regressions": [],
      "integration_gate": "Propiedades e integracion verdes sin skips de promesas.",
      "owner": "test-writer (properties)."
    },
    {
      "id": "T8",
      "detail": "next",
      "depends_on": ["T7"],
      "parallel": [],
      "files": [],
      "focal_tests": [],
      "observable_checks": [
        "Dictamen independiente PC-01..PC-13 e INV-01..INV-08 con ubicaciones, consecuencias, condiciones de cierre y abstenciones.",
        "D-1..D-5 y P-1..P-4 conservadas, sin agentes, campos, selectores ni permisos nuevos.",
        "Matriz Odoo por rol y diff real; referencias inventariadas sin obligaciones contradictorias.",
        "Tres vias PC-07/EV-03: preparacion ordinaria y reemplazo por construccion, rechazo estatico validate-request/render y contraste contextual del intento nuevo con agente declarado en record-dispatch.",
        "Rederivacion del sucesor ante predecesor historico sin agente y stack cambiado, sin copiar el agente anterior ni reescribir historia.",
        "Intento nuevo historico sin contexto ni agente admitido sin contraste contextual del destinatario, derivacion ni sustitucion silenciosa.",
        "Coherencia temporal de recepcion, repeticion identica y finalizacion write-ahead; identidad, integridad, continuidad, idempotencia y unica finalizacion conservadas.",
        "Compatibilidad historica sin falsear fixtures, medicion completa T2, adaptaciones por test-writer antes de GREEN y ejecucion de los cinco archivos de T5 con esperado frente a observado.",
        "Distincion mecanica/procedimental de variante ausente y eliminacion de otro valor -> generico.",
        "Procedencia distribuida, permisos y oraculos intactos; estructura separada de juicio semantico."
      ],
      "regressions": [],
      "integration_gate": "Bloqueantes resueltos y re-verificados; reviewer no edita.",
      "owner": "reviewer (read-only)."
    },
    {
      "id": "T9",
      "detail": "next",
      "depends_on": ["T8"],
      "parallel": [],
      "files": [
        "docs/specs/010-002-documentary-role-integration/closure.md"
      ],
      "focal_tests": [
        "python3 scripts/cdad-suite.py close --all --evidence-root .cdad/evidence/010-002-closure"
      ],
      "observable_checks": [
        "Suite de cierre conforme a politica canonica, con comandos, revision medida, salidas, skips y canarios.",
        "PC -> evidencia completo, deriva global declarada y aceptacion recuperable.",
        "Scribe entrega borradores de Memory Bank y se materializan tras aprobacion.",
        "Sin push, publicacion, actualizacion del HOME real ni atribucion de resultados del piloto."
      ],
      "regressions": [],
      "integration_gate": "Contrato acreditado y aceptacion recuperable sin cerrar la epica.",
      "owner": "Quien cierra y orquestador; autoridad vigente acepta."
    }
  ]
}
```
