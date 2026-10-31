# Discovery — 010-002-documentary-role-integration

**Resultado:** el mecanismo existente ya permite encargar un producto documental al rol productor, conservando el agente de dominio. No encontré evidencia que justifique añadir ahora otro campo de estado, un selector paralelo o agentes nuevos. El cambio mínimo propuesto es **operacionalizar el contrato documental existente y delimitar la aplicabilidad de las obligaciones Odoo propias de addons**.

Esto es una propuesta de Discovery, no una spec ni una decisión aprobada.

## 1. Base examinada

- Revisión del producto: `1b6629a0e726bdd60633068225187e3fedb2da5c`.
- Estado vivo examinado: SHA-256 `9ab26f74a2bf03db81fc24f90966d7874fcb55014f0833f21c0a499230c28144`.
- Intake **ruta C válido**: identificación coincidente, contrato con hash correcto, contexto de ejecución v2 y comparación completa de `PACKET.md` contra el render canónico: **7.719 bytes idénticos**.
- La unidad está activa y `stack` es `null`.

El cierre de 010-001 dejó expresamente fuera la selección documental y su combinación con Odoo, pero ya entregó las obligaciones documentales en roles, paquetes y agentes, incluidas variantes Odoo: `docs/specs/010-001-documentary-contracts/closure.md:18-35`.

## 2. Landscape verificado

### 2.1 Selección actual de agente

`prepare` resuelve:

| Estado | Agente resultante |
|---|---|
| `stack` ausente, `null` o `""` | `cdad-<rol>` |
| `stack: "odoo"` | `cdad-<rol>-odoo` |
| Cualquier otra cadena no vacía | `cdad-<rol>-<stack>` |

**Evidencia:** `skills/cdad-cycle/scripts/cdad_packet.py:6412-6425`. La selección se publica en `REQUEST.json.agent`: misma ruta, línea 6666.

Hay una discrepancia que debe permanecer visible:

- Las instrucciones nativas dicen usar la variante **si existe**, y el agente genérico en caso contrario: `sources/agents/adapters/opencode.md:69-74`, `sources/agents/adapters/claude-code.md:83-88`.
- El resolver de `prepare` no comprueba existencia: concatena cualquier `stack` no vacío.
- El adaptador externo consume `request.agent` y rechaza antes del despacho si ese agente derivado no está publicado; no sustituye una variante ausente por otra: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:417-458`.
- El generador solo contempla explícitamente genérico y Odoo: `scripts/cdad-generate.py:834-864`.

**Consecuencia:** no conviene introducir una cadena documental en `stack` suponiendo que todas las superficies resolverán lo mismo.

Además, `agent` es una propiedad del request que **no entra en el render**. El validador comprueba que sea una cadena no vacía, pero no su correspondencia con el rol: `skills/cdad-cycle/scripts/cdad_packet.py:1761-1770,1977-1994`. Una sonda exclusivamente en memoria confirmó que un `agent` de otro rol valida y produce el mismo render.

Esto no autoriza manipular el request: demuestra por qué **usar ese campo como selector manual nuevo no sería una solución suficiente**.

### 2.2 Qué significa `stack`

La evidencia normativa lo define como **dominio**, no como tipo de producto:

- Selección de variantes "by domain": `skills/cdad-cycle/SKILL.md:130-137`.
- Especialización por stack con conservación de la directiva genérica del rol: `skills/cdad-cycle/references/sub-agent-strategies.md:144-165`.
- El orquestador delega al especialista para obtener más contexto de dominio, manteniendo el mismo contrato de rol: `sources/roles/orchestrator.md:312-323`.

El **producto documental**, en cambio, depende del encargo:

- La norma se aplica cuando el encargo declara un producto documental: `skills/cdad-cycle/references/documentary-contracts.md:3-7,178-188`.
- Sus declaraciones utilizan los campos existentes: misma referencia, líneas 89-101.
- El implementer ya puede producir código **o un producto documental expresamente encargado**: `sources/roles/implementer.md:17-20,36-47`.

**Conclusión:** hoy no hay evidencia de que `stack` represente ambas dimensiones. Sobrecargarlo con "documental" reemplazaría la selección de dominio, no la complementaría.

### 2.3 El transporte necesario ya existe

| Información | Superficie existente |
|---|---|
| Qué se produce y qué comportamiento se compromete | Contrato aprobado, `objective`, `expected_output` |
| Fuentes autorizadas | `inputs`, `read_scope` |
| Producto editable | `write_scope` |
| Protección de fuentes, oráculos y verificadores | Contrato, `invariants`, alcances separados |
| Comprobaciones y límites | `evidence_required`, plan de validación |
| Rol y dominio | `role`, `substage`, `REQUEST.json.agent` |

El renderer transporta objetivo, contrato, insumos, alcances, invariantes, salida y evidencia: `skills/cdad-cycle/scripts/cdad_packet.py:2010-2027`.

La capacidad decisiva ya está implementada:

- `implementer` admite escritura de clase `docs`.
- `test-writer` escribe solo tests, tests colocados y temporales declarados.
- Architect, reviewer y scribe no admiten escritura de producto.

**Evidencia:** `skills/cdad-cycle/scripts/cdad_packet.py:1419-1475`. Las sondas en memoria confirmaron esa separación.

**Precaución:** el alcance por defecto del implementer solo incluye implementación; un encargo documental necesita declarar explícitamente su directorio editable. No debe ampliarse ese default: misma ruta, líneas 2266-2276.

### 2.4 Generación, instalación y permisos

El flujo vigente es:

1. Fuentes de roles y adaptadores.
2. Generación por runtime.
3. Staging con manifiesto y hashes.
4. Instalación de los artefactos de staging.
5. Derivación local de agentes según la política del proyecto.
6. Despacho del agente declarado.

Referencias:

- Composición por rol y dominio: `scripts/cdad-generate.py:616-707`.
- Procedencia y hashes: misma ruta, líneas 915-967.
- Entradas de regeneración: `Makefile:10-18`.
- Instalación desde staging y sin transformar agentes: `install.sh:273-280,332-360`.
- Derivación local: `skills/cdad-cycle/scripts/cdad_packet.py:5045-5094`.

Añadir sufijos documentales **no sería solo añadir archivos**: `_derived_role` reconoce los roles actuales y únicamente elimina el sufijo `-odoo`. Sufijos documentales hipotéticos devolvieron `None` en la sonda: misma ruta, líneas 4439-4450. También habría que revisar hooks, inventarios, manifiestos y resolución.

## 3. La combinación documental/Odoo que debe preservarse

Las variantes Odoo **ya contienen el puntero documental y mantienen sus cargas de conocimiento de dominio**. La composición conserva esas cargas incluso en la ruta de paquete: `scripts/cdad-generate.py:634-648,688-689`.

El problema encontrado no es ausencia de conocimiento documental, sino **obligaciones de ejecución formuladas para addons**:

| Rol | Obligación actual relevante |
|---|---|
| Architect | Inventario core/OCA y formato proceso→módulo |
| Test-writer | `TransactionCase`, `@tagged`, ejecución por make |
| Implementer | Evidencia `make test`, lint y, cuando corresponda, instalación limpia |
| Reviewer | `make test-clean`, OCA y pylint |
| Orchestrator | Consume la evidencia del contrato Odoo delegado |

Referencias: `sources/roles/architect.md:145-153`; `test-writer.md:118-128`; `implementer.md:84-92`; `reviewer.md:106-115`; `orchestrator.md:312-323`.

También hay obligaciones en las fuentes de conocimiento: por ejemplo, resolución del entorno de pruebas antes de cerrar Discovery en `skills/odoo-architect/SKILL.md:38-47`, y base `TransactionCase` en `skills/odoo-test-writer/SKILL.md:17-23`.

**Propuesta:** conservar el dominio Odoo y delimitar, en sus fuentes competentes, qué obligaciones corresponden a modificar o verificar un addon y cuáles a producir exclusivamente documentación. Esa delimitación no puede improvisarla un paquete para ignorar instrucciones superiores.

En un encargo mixto deben conservarse las comprobaciones que correspondan a cada producto; declarar "documental" no debe servir para evitar pruebas de código modificado.

## 4. Alternativas y criterio

| Alternativa | Ventaja | Coste o riesgo | Dictamen propuesto |
|---|---|---|---|
| **Contrato documental con agentes actuales** | Reutiliza transporte, dominio y permisos existentes | Requiere instrucciones operativas inequívocas y resolver aplicabilidad Odoo | **Mínima recomendada** |
| Variantes documentales por rol | Identidad explícita del especialista | Multiplica combinaciones; exige actualizar resolución, clasificación, hooks y distribución | Solo si se demuestra comportamiento necesario que no pueda expresarse por encargo |
| Perfil independiente | Separa conceptualmente dominio y producto | Introduce otro mecanismo de selección sin necesidad probada | No justificado ahora |
| Selector explícito en el paquete | Podría dirigir la composición | Exigiría validación, transporte, compatibilidad y correlación coherentes | No usar `agent` libre como sustituto de ese diseño |
| Sobrecargar `stack` | Reutiliza un campo | Pierde o mezcla el dominio; activa discrepancias actuales de resolución | Descartar |

"Perfil documental" puede describir una especialización **por contrato**, sin implicar necesariamente otro agente o campo. La épica reserva esa concreción a Specification y prohíbe anticipar nombres o campos: `docs/epics/epic-010-documentary-specialization/plan.md:49-51,75-78,90-94`.

## 5. Propuesta mínima para la siguiente etapa

Sin fijar todavía nombres ni esquema:

1. **Conservar `stack` como dominio y la selección actual del agente de rol.**
2. Incorporar al procedimiento canónico del orquestador una preparación documental explícita mediante los campos existentes: fuentes, directorio de producto, verificadores e insumos protegidos, evidencia y límites.
3. Mantener la producción en implementer; architect propone, test-writer conserva el oráculo, reviewer contrasta independientemente y scribe mantiene su función de Memory Bank.
4. Resolver la aplicabilidad de las obligaciones Odoo de addon en las fuentes de rol y conocimiento afectadas, preservando las obligaciones de dominio pertinentes.
5. Regenerar y verificar ambos runtimes mediante el flujo existente, sin ampliar permisos por defecto.
6. Alinear las instrucciones de despacho para que no recomputen una selección distinta de la declarada en el encargo. La política general para variantes desconocidas requiere una decisión explícita; no la doy por resuelta aquí.

La propuesta **no requiere actualmente** campo nuevo, agente nuevo, skill nuevo ni modificación de permisos.

## 6. Cómo verificarlo

### Comprobación estructural propuesta

- Preparar encargos de código y documentales con dominio genérico y Odoo.
- Comprobar rol, subfase, agente declarado y agente realmente invocado.
- Verificar que el producto documental tiene alcance explícito, separado de fuentes, contrato y oráculos.
- Comprobar que implementer no obtiene escritura en tests; test-writer conserva escritura solo en tests; los roles read-only siguen sin escritura.
- Comparar generación reproducible, manifiestos, bytes instalados y derivados.
- Conservar regresión del comportamiento previo de código genérico y Odoo.
- Registrar separadamente estructura automática y revisión semántica.

No hace falta una batería de variantes equivalentes: cada comprobación debe proteger una promesa distinta.

### Verificación aislada, sin instalación global

El repositorio ya ofrece precedentes:

- Aislamiento de HOME, XDG y temporales, con limpieza de overrides heredados: `tests/conftest.py:28-68,80-126`.
- Instalación con `CDAD_INSTALL_ROOT` propio y comparación de agentes contra staging: `tests/test_010_001_documentary_contracts.py:1341-1399`.

La futura prueba debe recorrer **generación → instalación aislada → derivación → preparación → resolución**, usando fuentes sintéticas locales. Eso acreditaría la combinación del framework; no el conocimiento verdadero de cualquier instancia Odoo.

### Lo necesariamente semántico

Un test puede comprobar estructura, rutas, restricciones declaradas y referencias resolubles. No puede acreditar por sí solo:

- Que una afirmación esté respaldada.
- Que no se haya omitido una contradicción.
- Que una referencia existente sustente la conclusión.
- Que una exclusión de comprobaciones Odoo sea legítima.

Esas responsabilidades permanecen en revisión independiente y aceptación del dueño: `skills/cdad-cycle/references/documentary-contracts.md:151-176`.

**Límite adicional:** las barreras actuales no convierten el paquete en sandbox. Por ejemplo, los mapas derivados no identifican automáticamente un documento bajo `docs/` como producto que el test-writer no debe leer. La prohibición contractual sigue siendo necesaria; no debe declararse protección mecánica inexistente. Véase `skills/cdad-cycle/references/project-execution.md:169-185`.

## 7. Riesgos y preguntas abiertas

1. **Interpretación de "perfil documental".**
   ¿Se acepta la especialización por contrato con agentes existentes o se exige una identidad de agente distinta? **Bloqueante para cerrar la solución de Specification**, no para este landscape. La segunda opción necesita justificar su coste adicional.

2. **Aplicabilidad Odoo.**
   Debe aprobarse qué obligaciones de addon no corresponden a un producto exclusivamente documental y cómo se conserva el conocimiento funcional. **Bloqueante antes de comprometer el recorrido documental/Odoo.**

3. **Variantes inexistentes.**
   Las instrucciones nativas prometen fallback y el resolver publica un sufijo sin comprobarlo. No conviene extender esa ambigüedad. Falta decidir si se corrige dentro de esta unidad o se limita expresamente la promesa a las combinaciones soportadas.

4. **Deriva global conocida.**
   El cierre anterior declara agentes y CLI globales desactualizados. Las comprobaciones deben usar la fuente del proyecto y una instalación aislada, no actualizar el HOME real: `docs/specs/010-001-documentary-contracts/closure.md:157-176`.

5. **Esquema publicado desalineado.**
   El validador Python admite `agent` y `execution_context`, pero el asset `packet-request.schema.json` no los enumera pese a `additionalProperties: false`. Referencias: asset, líneas 5-22; validador, líneas 1743-1770. Es una divergencia existente, no evidencia para inventar otro campo. Debe considerarse al elegir el oráculo estructural.

## 8. Evidencia de ejecución

**Comandos de validación ejecutados:**

```sh
python3 scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/010-002-documentary-role-integration-architect-discovery-001/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/010-002-documentary-role-integration-architect-discovery-001/REQUEST.json --packet .cdad/packets/010-002-documentary-role-integration-architect-discovery-001/PACKET.md
```

Ambos terminaron correctamente, sin diagnóstico.

Las sondas se ejecutaron con **Python 3.13.5**, mediante `PYTHONDONTWRITEBYTECODE=1 python3 -B`, cargando funciones reales con `runpy.run_path`. Los cuerpos exactos y salidas constan en las llamadas `shell` de esta sesión. No invocaron `prepare`, construcción en disco ni instalación.

| Medición | Salida observada |
|---|---|
| Render canónico frente a publicado | `canonical bytes 7719 published bytes 7719 full byte equality True` |
| Escritura documental | Solo implementer aceptado; los otros cuatro roles rechazados |
| Generación Odoo por runtime, en memoria | 11 agentes; repetición idéntica; ninguna diferencia con staging |
| Generación genérica por runtime | 6 agentes |
| Variantes Odoo | Puntero documental presente y cargas de dominio conservadas en los cinco roles |
| `agent` de otro rol, solo en memoria | Validación aceptada; render sin cambios |

Control inicial y final:

```sh
git rev-parse HEAD
git status --short
git diff --stat
```

Ambos controles mostraron el mismo HEAD y las mismas modificaciones preexistentes:

```text
 M docs/.cdad-state.json
?? docs/specs/010-000-continuity-relative-root/discovery.md

docs/.cdad-state.json | 25 +++++++++++++++++--------
1 file changed, 17 insertions(+), 8 deletions(-)
```

**Archivos modificados por esta tarea: ninguno. Commit nuevo: ninguno.** No ejecuté suite, instalador, publicación ni cambios globales. La evidencia aportada es de Discovery y sondas acotadas; no acredita todavía la futura integración.
