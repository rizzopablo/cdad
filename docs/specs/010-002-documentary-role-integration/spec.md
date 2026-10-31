# Spec — 010-002-documentary-role-integration

**Versión:** 4.  
**Estado:** borrador revisado, pendiente de revisión y aprobación explícitas.  
**Épica:** `epic-010-documentary-specialization`.  
**Base:** Discovery, decisiones D-1–D-5 y precisiones P-1–P-4 del 2026-10-31; N1–N4 conservadas y B1, N5 y N6 adoptadas.  
**Dependencia:** contratos documentales compartidos entregados en 010-001.

## 1. Descripción funcional

Permitir que el orquestador encargue un producto documental al rol correspondiente mediante el flujo canónico existente, conservando dominio, separación de responsabilidades y permisos.

En esta spec, **«perfil documental» significa la especialización por contrato de D-1**, no una identidad de agente ni otro mecanismo de selección. Su generación, instalación y resolución se acreditan mediante los agentes existentes y un encargo que declara producto, fuentes, alcances, verificadores y evidencia.

`stack` conserva su significado de dominio.

Esta unidad entrega:

- Un procedimiento operativo de preparación y aceptación documental.
- Aplicabilidad por rol de las obligaciones Odoo propias de addons.
- Coherencia estática entre rol y agente, y coherencia contextual entre rol, dominio y agente en publicaciones nuevas —ordinarias y por reemplazo— e intentos nuevos de despacho con agente declarado.
- Instrucciones de selección concordantes con el mecanismo.
- Corrección del esquema publicado del request.
- Evidencia estructural de generación, instalación y resolución aisladas, incluida la combinación documental/Odoo.
- Compatibilidad histórica expresamente delimitada, sin reinterpretar retrospectivamente un despacho.

No acredita todavía la fidelidad de un documento funcional real ni los resultados semánticos del piloto 010-003.

## 2. Decisiones y alternativas

### D1. Especialización documental por contrato

Se utilizan los seis roles actuales y los campos existentes:

| Declaración | Transporte |
|---|---|
| Objetivo y promesas | Contrato aprobado, `objective` |
| Producto esperado | `expected_output` |
| Fuentes autorizadas | `inputs`, `read_scope` |
| Producto editable | `write_scope` |
| Separación y verificadores protegidos | Contrato, `invariants`, alcances |
| Comprobaciones y límites | `evidence_required` |

Se descartan variantes documentales, un selector paralelo y la sobrecarga de `stack`: el transporte actual expresa las promesas necesarias sin multiplicar resolución, clasificación y distribución.

La norma documental conserva su casa única en `skills/cdad-cycle/references/documentary-contracts.md`. El procedimiento operativo se incorpora a `references/handoff-prompts.md`; los consumidores remiten a él sin reproducir la norma.

### D2. Aplicabilidad Odoo por producto y responsabilidad del rol

Se conservan los agentes Odoo, sus cargas de dominio y los límites de cada rol. La aplicabilidad no se deduce del `write_scope` del propio rol cuando este no escribe el producto.

#### Frontera del addon

Dentro de un módulo Odoo, se consideran trabajo de addon:

- `models/`, `views/`, `controllers/`, `wizards/`, `security/`, `data/` y `static/src/`.
- `__manifest__.py`.
- Código ejecutable o recursos funcionales equivalentes: imports, hooks, archivos Python de ejecución, informes y directorios `wizard/` o `report/`, cuando existan.

La documentación del módulo —`readme/`, `static/description/`, `README.rst`, `doc/`— es **producto documental**, salvo que el contrato la declare parte del entregable funcional del addon. Su ubicación dentro del módulo, por sí sola, no exige una batería de addon.

Los tests de addon verifican un producto de addon aunque el test-writer escriba exclusivamente bajo `tests/`. Un verificador estructural documental no se convierte en test de addon por estar en un proyecto Odoo.

Esta frontera delimita obligaciones; **no cambia la clasificación de rutas de la política, los permisos ni los alcances admitidos**. Una ubicación o función ambigua se resuelve antes de continuar esa parte.

#### Base de decisión por rol

| Rol | Base de aplicabilidad |
|---|---|
| Architect | Producto propuesto en el contrato y sus alcances; nunca su propio `write_scope`, que permanece vacío. |
| Test-writer | Producto y promesas que verifica, declarados en el contrato; nunca el hecho de escribir tests ni la inspección del producto producido. |
| Implementer | Producto aprobado y `write_scope` declarado. |
| Reviewer | Contrato y **diff real**. El diff prevalece sobre una etiqueta documental. |
| Orquestador | Producto y alcances al preparar; **diff real** y evidencia al validar los gates. El diff prevalece sobre la etiqueta. |
| Scribe | Su función de Memory Bank y la evidencia del cierre; no asume producción ni verificación de addons. |

Los resultados comprometidos para documental, addon y mixto se enumeran en PC-04 y PC-05.

El architect conserva conocimiento funcional, criterio de configuración primero, mapeo proceso→módulo y declaración de `VERIFY`. El inventario core/OCA como paso acreditado de verificación, y la resolución del entorno de pruebas de addon, son exigibles cuando se propone modificar un addon, antes de avanzar a esa modificación. No se exige inventar un inventario ni una ejecución para completar documentación pura.

Si un encargo declarado exclusivamente documental permite modificar addon, se detiene esa parte y vuelve al orquestador. Si el diff real revela modificaciones de addon no autorizadas, reviewer y orquestador registran la desviación y mantienen las obligaciones correspondientes: no conceden permiso retroactivo ni aceptan el trabajo como documental puro.

### D3. Coherencia del destinatario y momento de comprobación

La derivación canónica existente se conserva:

- `stack` ausente, `null` o `""`: `cdad-<role>`.
- Cualquier cadena no vacía: `cdad-<role>-<stack>`.

Se reutiliza el productor canónico de esa derivación, sin resolutores independientes en consumidores.

Se distinguen dos comprobaciones.

#### Contraste estático agente↔rol

La validación compartida del request comprueba, cuando aparece `agent`, que pertenece al rol declarado:

- Nombre genérico exacto `cdad-<role>`, o
- Prefijo completo `cdad-<role>-` seguido de un sufijo no vacío.

No basta una coincidencia parcial del nombre del rol. Este contraste **no consulta ni compara el stack vigente** y no acredita que la variante esté publicada.

Un agente de otro rol es inválido: `validate-request` lo rechaza y `render` no produce un paquete válido. La misma regla se conserva donde se utiliza la validación compartida, incluida la comprobación de un paquete publicado.

Su diagnóstico identifica el rol, el agente recibido y la familia de agente esperada; declara que el stack no se evalúa en este contraste estático.

Esta precisión conserva P-1 y D-3: la discordancia de rol no obtiene un render válido. No se introduce una comparación temporal en la recepción.

#### Contraste contextual rol/stack/agente

La comprobación contextual se ejecuta:

1. Al preparar o publicar un **request nuevo**, por preparación ordinaria o por reemplazo, antes de publicar sus artefactos.
2. Al registrar un **intento nuevo de despacho con agente declarado**, antes de publicar su registro o habilitar la invocación del trabajo de rol.

En esos límites se contrasta el agente con el rol y el `stack` vigente admitido. La discordancia falla cerrada con diagnóstico de rol, stack y agente esperado.

**Garantía por construcción en ambas vías públicas de publicación:**

- La preparación ordinaria deriva el agente del rol y del stack vigente.
- `prepare --replace-packet` publica un sucesor nuevo que **rederiva** el agente del rol y del stack vigente; **no copia** el agente del predecesor.
- Si el predecesor histórico carece de `agent`, el sucesor publica el agente derivado y su `execution_context`.
- Si el stack cambió durante la vida del predecesor, el sucesor publica el agente correspondiente al stack vigente, no el anterior.

Ninguna de estas vías acepta un agente alternativo del llamador. Por su interfaz pública, la garantía se verifica observando el agente publicado; no se promete una rama de rechazo de agente inyectado que esa interfaz no permite alcanzar.

Se adopta la regla general de **publicación nueva → derivación vigente**, frente a conservar el agente anterior y rechazar ciertos reemplazos. Mantiene una sola regla para las dos vías públicas y evita tanto el sucesor con contexto sin agente como el sucesor discordante tras cambiar el dominio. No modifica los bytes históricos ni las demás condiciones de reemplazo, conservación, corrección o publicación transaccional.

**Intento nuevo frente a continuidad de un registro:** la comprobación contra el stack vigente no se reaplica a una repetición idempotente de un registro idéntico ni a la finalización válida del registro write-ahead del mismo intento ya iniciado. Un cambio de stack durante la ejecución no impide completar ese registro por ese único motivo.

Esta delimitación no permite reutilizar un identificador con datos distintos fuera de la finalización ya admitida, ni relaja identidad, integridad, continuidad, transacciones u otras precondiciones existentes. La repetición conserva sus bytes y las transiciones pendientes previstas; la finalización conserva las reglas existentes de identidad fija y única sustitución del registro provisional.

**Histórico sin contexto ni agente:** un request histórico admitido sin `execution_context` ni `agent` puede registrar un intento nuevo. No hay agente declarado que contrastar, por lo que no se aplica el contraste contextual del destinatario y **no se deriva ni sustituye un agente en silencio**. Se conserva el tratamiento histórico declarado y las demás precondiciones del registro. Esta admisión no promete que cualquier adaptador pueda lanzar trabajo sin destinatario ni introduce un fallback para variantes ausentes.

**Recepción y lectura de un paquete publicado:** no se reevalúa su agente contra el `stack` vigente. El request publicado es la autoridad de su destinatario; la recepción, el render canónico, la verificación y la continuidad conservan sus comprobaciones existentes y el contraste estático de rol, sin introducir el contraste temporal.

Por tanto, no se inserta indiscriminadamente la comparación contra el estado vigente en todos los llamadores de la validación compartida. La distinción es el propósito de la operación y la condición ya existente del request o intento, no un campo ni un selector nuevo.

Un cambio de `stack` puede bloquear un intento nuevo de despacho del paquete anterior con agente declarado, pero no invalida por ese único motivo la recepción del resultado de un despacho ya realizado, la repetición idéntica de su registro ni la finalización válida de su write-ahead. El reemplazo, si satisface sus precondiciones, publica otro request con agente rederivado; no reescribe el request, paquete ni registros del predecesor.

**Presencia de `agent`:**

- Si existe `execution_context`, `agent` es obligatorio y una cadena no vacía.
- Los históricos sin ninguno de esos dos campos siguen admitidos.
- Los históricos sin `execution_context` y con `agent` mantienen su admisión estructural, sujetos al contraste estático agente↔rol.
- Toda publicación nueva, ordinaria o por reemplazo, publica ambos campos.
- `agent` continúa excluido del render.

La regla de presencia y el contraste estático se aplican también al validar un request publicado. Ninguno compara el agente con el stack vigente.

Se descarta tanto validar solo al despachar —dejaría renderizar agentes de otro rol— como comparar el stack vigente en toda lectura —invalidaría continuidad histórica legítima—. La separación conserva la garantía de rol sin convertir un cambio posterior de dominio en una invalidación retrospectiva.

### D4. Variante no publicada e instrucciones de selección

Las instrucciones deben expresar:

- La derivación genérica solo corresponde al stack ausente, `null` o vacío.
- Cualquier stack no vacío deriva un sufijo; «otro valor» no significa agente genérico.
- El despacho utiliza el agente del request validado.
- Una variante requerida pero no publicada impide el despacho; no se sustituye silenciosamente.

La garantía tiene dos superficies distintas:

- **Adaptador externo:** rechazo mecánico antes de lanzar el trabajo de rol.
- **Vía nativa:** obligación procedimental del orquestador de comprobar publicación y detenerse; no se promete una nueva guarda mecánica.

`prepare` y el registro de despacho no pasan a ser detectores universales de publicación.

La corrección alcanza los adaptadores nativos, el orquestador, `skills/cdad-cycle/SKILL.md` y `references/sub-agent-strategies.md`, incluidas sus cláusulas de «otro valor».

El tratamiento histórico declarado de requests sin `agent` es distinto del fallback silencioso de una variante solicitada y ausente.

### D5. Esquema publicado

El asset declara las propiedades ya admitidas `agent` y `execution_context`, preservando:

- El conjunto cerrado de campos.
- La admisión histórica sin ambos campos.
- `agent` como cadena no vacía cuando aparece.
- `execution_context` como cadena no vacía y descripción de su ubicación canónica.
- La condición estructural: presencia de `execution_context` exige `agent`.

El esquema comprueba forma y dependencia de campos. No sustituye las verificaciones del CLI sobre coherencia estática agente↔rol, rutas canónicas, archivos, estado, autoridad, hashes, identidades o momento de publicación/despacho.

## 3. Procedimiento operativo comprometido

Antes de preparar un encargo documental, el orquestador:

1. Identifica dominio, rol y subfase, sin introducir un stack documental.
2. Declara objetivo, producto esperado y fuentes recuperables.
3. Delimita un directorio editable separado del contrato, fuentes y oráculos. Una ruta exacta requiere estar admitida por la política existente.
4. Identifica verificadores e insumos protegidos mediante los campos actuales.
5. Determina la aplicabilidad Odoo con la base correspondiente a cada rol.
6. Registra evidencia exigible, límites y pendientes.
7. Prepara y valida por la vía canónica; publica el destinatario coherente. Si utiliza reemplazo, el sucesor rederiva su agente conforme a D3.
8. Despacha sin reconstruir el paquete, alterar la ruta de intake ni sustituir el agente.
9. Al re-entry, contrasta el diff real y la evidencia, separando estructura, revisión semántica y aceptación.

Las responsabilidades permanecen:

| Rol | Resultado y frontera |
|---|---|
| Orquestador | Prepara, coordina, materializa y verifica gates; no ejecuta trabajo de rol inline. |
| Architect | Devuelve contratos y borradores verificables, sin escribir producto ni aprobarlos. |
| Test-writer | Construye verificadores desde contrato e insumos autorizados; no deriva el oráculo del producto producido. |
| Implementer | Escribe únicamente el producto autorizado; no modifica tests, fuentes ni oráculos protegidos. |
| Reviewer | Contrasta independientemente producto, contrato y fuentes, en read-only. |
| Scribe | Devuelve borradores de Memory Bank; no asume producción documental general. |

Este procedimiento no constituye un sandbox ni añade detección automática universal de superposiciones.

## 4. Contrato y postcondiciones

### Promesa A — El encargo documental llega al rol correcto sin ampliar autoridad

- **PC-01.** El procedimiento explica cómo expresar objetivo, producto, fuentes, alcance, verificadores protegidos, evidencia y límites mediante los campos existentes, sin otro selector.
- **PC-02.** Conserva las fronteras de los seis roles y utiliza los agentes actuales; no crea variantes documentales.
- **PC-03.** La producción documental requiere alcance editable explícito. Las pruebas confirman que el default del implementer no incorpora documentación, que este no obtiene escritura en tests y que los roles read-only no obtienen escritura de producto. El procedimiento exige detener superposiciones o ambigüedades con insumos protegidos.

**Verificación:** controles estructurales y preparación de encargos sintéticos, más revisión independiente de suficiencia.

### Promesa B — Documentar en Odoo no exige fingir pruebas de un addon ni permite eludirlas

- **PC-04.** Las fuentes competentes y sus artefactos distribuidos contienen la frontera de addon y los siguientes resultados para los roles que especifican, verifican y producen:

| Rol | Documental puro | Addon | Mixto |
|---|---|---|---|
| Architect | Conserva dominio, mapeo pertinente y `VERIFY`; no exige inventario acreditado ni entorno de pruebas de un addon no modificado. | Exige inventario core/OCA y entorno resuelto antes de avanzar a modificar el addon, conservando su función read-only. | Especifica ambas familias; las obligaciones de addon se aplican a esa parte. |
| Test-writer | Construye el verificador documental comprometido; no exige `TransactionCase`, `@tagged` ni runner de addon solo por el dominio del proyecto. Conserva aislamiento y prohibición de derivar el oráculo del producto. | Los tests de addon conservan framework, tags, fixtures y runner Odoo aplicables. | Separa verificadores documentales y tests de addon; cada uno conserva su régimen. |
| Implementer | Produce únicamente el documento autorizado y aporta su evidencia; no exige pruebas, instalación ni lint de addon no modificado. | Conserva pruebas, lint, OCA e instalación limpia cuando el contrato la exige. | Cumple ambas familias sobre sus productos respectivos; la etiqueta documental no exime addon. |

- **PC-05.** Las fuentes competentes y sus artefactos distribuidos contienen los siguientes resultados para los roles de revisión, coordinación y memoria, conservando cargas de dominio y permisos:

| Rol | Documental puro | Addon | Mixto |
|---|---|---|---|
| Reviewer | Confirma que el diff real es documental; contrasta documento, contrato y fuentes sin exigir batería de addon ajeno al diff. | El diff real activa las obligaciones de revisión de addon, incluidas evidencias de instalación limpia, lint y OCA correspondientes. | Revisa ambas partes y ambas evidencias. Un cambio de addon oculto bajo una etiqueta documental se informa y bloquea su aceptación como documental puro. |
| Orquestador | Prepara declaraciones documentales y, al re-entry, confirma el diff y sus verificaciones. | Exige evidencia del contrato de addon delegado según el diff real, sin realizar trabajo de rol inline. | Exige ambas familias. Si el diff contradice el encargo, detiene y corrige o reencauza; no concede permisos retroactivos. |
| Scribe | Redacta Memory Bank desde la evidencia documental del cierre. | Redacta Memory Bank desde la evidencia de addon del cierre; no ejecuta ni sustituye sus verificaciones. | Conserva ambas clases de evidencia en su borrador, sin producir el entregable ni aprobarlo. |

**Verificación:** comprobaciones estructurales de fuentes y artefactos, y revisión independiente de casos sintéticos documental, addon y mixto. Incluye documentación dentro de un módulo y un diff de addon contrario a la etiqueta. Las palabras clave no acreditan por sí solas la legitimidad de una exclusión.

### Promesa C — El destinatario es coherente sin reinterpretar retrospectivamente un despacho

- **PC-06.** Toda publicación nueva, por preparación ordinaria o por `prepare --replace-packet`, publica `agent` y `execution_context`. Ambas vías derivan el agente del rol y del stack vigente conforme a D3. En el reemplazo:
  - Un predecesor histórico sin agente obtiene un sucesor con agente derivado.
  - Un cambio de stack produce un sucesor con agente del stack vigente, no una copia del anterior.
  - No se reescriben los bytes históricos del predecesor ni sus registros de despacho; se conservan las demás precondiciones y efectos autorizados del reemplazo.
- **PC-07.** Se distinguen tres vías observables:
  - **Publicación ordinaria y por reemplazo: garantía por construcción.** Ambas publican el agente derivado del rol y stack admitido. Se verifica el valor publicado, incluidas las transiciones de PC-06; no se exige provocar mediante CLI una discordancia que el llamador no puede introducir.
  - **`validate-request` y `render`: rechazo estático.** Un request con agente de otro rol es rechazado por la validación compartida y no produce un render válido, sin consultar el stack vigente. El diagnóstico identifica rol, agente recibido y familia esperada, y declara que el stack no se evalúa.
  - **`record-dispatch`: contraste contextual del intento nuevo.** Un intento nuevo con agente declarado que no corresponde al rol y stack vigente falla antes de publicar su registro o habilitar la invocación del trabajo de rol. El diagnóstico identifica rol, stack y agente esperado. El adaptador externo no lanza el trabajo de rol si falla su registro previo; la vía nativa conserva la obligación de no invocar tras el rechazo. El histórico admitido sin contexto ni agente puede registrar un intento nuevo sin contraste contextual del destinatario y sin derivar ni sustituir agente en silencio.
- **PC-08.** Se conservan conjuntamente:
  - Rechazo de `execution_context` presente sin `agent`.
  - Admisión histórica sin ambos campos, incluido el registro de un intento nuevo en las condiciones de PC-07.
  - Admisión de históricos con agente del mismo rol sin imponerles el stack vigente en la lectura.
  - Exclusión de `agent` del render entre requests válidos.
  - Recepción de un paquete ya publicado y despachado sin reevaluar su agente contra un stack cambiado, manteniendo el contraste estático de rol y las demás precondiciones.
  - Repetición idempotente de un registro idéntico tras cambiar solo stack, conservando bytes y las transiciones pendientes previstas.
  - Finalización válida del write-ahead del mismo intento tras cambiar solo stack durante la ejecución, conservando identidad fija, única finalización y demás precondiciones.
  - Rechazo de un **intento nuevo** con agente declarado discordante tras ese cambio, sin alterar el paquete ni los registros anteriores.
  - Variante no publicada: rechazo mecánico en el adaptador externo y detención procedimental en la vía nativa, sin fallback silencioso.

**Verificación:** CLI público y adaptador existente sobre proyectos descartables; diagnóstico, salida, bytes y efectos observados. Las dos vías públicas de publicación se clasifican en `consequence` como garantía por construcción, no como ramas de rechazo de agente inyectado. Se acreditan por separado reemplazo histórico, reemplazo tras cambio de stack, rechazo estático, rechazo de intento nuevo discordante, intento nuevo histórico sin agente, recepción, repetición idéntica y finalización write-ahead, conforme a sus consecuencias distintas.

### Promesa D — Las instrucciones no prometen otra resolución

- **PC-09.** Los adaptadores nativos, el orquestador, `skills/cdad-cycle/SKILL.md` y las referencias de selección expresan la derivación para cualquier stack no vacío y la regla de variante ausente. No mantienen «otro valor → genérico». Los agentes generados conservan la doctrina corregida.

**Verificación:** `TestDispatchDoctrine` cubre expresamente ambas formulaciones de «otro valor», además de las cláusulas de fallback, y revisión independiente de coherencia.

### Promesa E — El esquema describe los campos publicados y su compatibilidad

- **PC-10.** El asset:
  - Declara `agent` y `execution_context`.
  - Mantiene `additionalProperties: false`.
  - Admite requests actuales válidos e históricos representativos.
  - Rechaza tipos inválidos, claves desconocidas y contexto presente sin agente.
  - Distingue validación estructural del esquema, contraste estático de rol en el CLI y contraste contextual de publicación/despacho.

**Verificación:** evaluación real del JSON Schema y CLI sobre fixtures pertinentes. No basta encontrar los nombres de las propiedades.

### Promesa F — La integración se distribuye reproduciblemente

- **PC-11.** `make agents` genera y promueve ambos runtimes desde sus fuentes. Dos generaciones con iguales entradas producen agentes y manifiestos idénticos; los promovidos coinciden con staging. No se editan agentes manualmente ni se eleva el techo estático.
- **PC-12.** La distribución se acredita en dos tramos:
  - **PC-12.a — T4:** instalación aislada de agentes, skills y referencias corregidos, con origen y bytes esperados. Un encargo documental genérico y otro con `stack=odoo` recorren generación→instalación→preparación→resolución conservando rol, dominio y fronteras de escritura. Esto acredita el perfil documental definido en D1.
  - **PC-12.b — T6/T7:** la instalación aislada actualizada distribuye CLI y esquema corregidos; el recorrido documental/Odoo se repite con las validaciones finales de PC-06–10.

  Se comprueba la derivación local existente de OpenCode y las superficies instaladas y guardas existentes de Claude Code. No se inventa una derivación equivalente para este último ni se acredita recepción nativa real.
- **PC-13.** La aceptación presenta por separado evidencia automática e informe independiente contra contrato y fuentes, con hallazgos y abstenciones. No atribuye fidelidad semántica ni conducta efectiva de modelos a pruebas estructurales o destinos simulados.

## 5. Invariantes verificables

| Invariante | Verificación |
|---|---|
| **INV-01.** `stack` representa dominio; no existe selector documental nuevo. | Esquema, preparación y diff. |
| **INV-02.** Cada encargo mantiene un rol y una subfase, sin acumular permisos. | Requests y regresiones de alcances. |
| **INV-03.** El productor no modifica su oráculo. | Alcances, diff y revisión, sin prometer vigilancia exhaustiva. |
| **INV-04.** Todo agente declarado satisface el contraste estático de rol. Toda publicación nueva, ordinaria o por reemplazo, y todo intento nuevo con agente declarado mantienen coherencia rol/stack/agente. Los requests con contexto no omiten agente. Un histórico admitido sin ambos campos puede registrar un intento nuevo sin contraste contextual del destinatario y sin agente derivado o sustituido en silencio. La recepción, la repetición idéntica y la finalización válida del write-ahead no reinterpretan el destinatario contra un stack posterior. | PC-06–08, propiedades acotadas de los contrastes declarados y pruebas de transición. |
| **INV-05.** La excepción documental no exime trabajo de addon; el diff real prevalece en revisión y gates. | PC-04–05 y revisión de casos sintéticos. |
| **INV-06.** La norma documental conserva casa única y consumidores por referencia. | Regresión de 010-001 y diff. |
| **INV-07.** Generados e instalados proceden de fuentes canónicas. | Manifiestos, hashes y bytes. |
| **INV-08.** Integridad, estructura, revisión semántica y aprobación son hechos distintos. | Informe independiente y aceptación. |

Los invariantes procedimentales o semánticos no se convierten artificialmente en propiedades aleatorias. La subfase de propiedades verifica la parte generable de INV-04 con semilla y presupuesto acotado. El reemplazo y la estabilidad de recepción, repetición y finalización se prueban mediante sus transiciones observables.

## 6. Aceptación y evidencia esperada

| Evidencia | Contenido exigido |
|---|---|
| **EV-01 — Trazabilidad** | PC-01–13, incluidos PC-12.a/b, enlazadas a tests o dictamen independiente. |
| **EV-02 — RED/GREEN** | Comandos, selección, revisión medida, salidas, rc y causa de RED; controles ya verdes identificados. En T5 se ejecutan el módulo nuevo y los cuatro archivos existentes previstos, registrando por archivo el resultado esperado y observado. |
| **EV-03 — Destinatario** | Tres vías separadas: publicación ordinaria y por `prepare --replace-packet`, clasificadas en `consequence` como garantía por construcción; rechazo estático de agente de otro rol por `validate-request` y ausencia de render válido; contraste contextual del intento nuevo por `record-dispatch`, con diagnóstico y efectos observados. El reemplazo acredita sucesor derivado para predecesor histórico sin agente y para stack cambiado, sin copia del agente anterior ni reescritura histórica. Incluye intento nuevo histórico sin contexto ni agente, sin contraste contextual del destinatario ni derivación o sustitución silenciosa; presencia condicionada de agente; render entre requests válidos; recepción tras cambio de stack; repetición idéntica; finalización write-ahead; y distinción mecánica/procedimental de variante ausente. No atribuye a ninguna vía de `prepare` una rama pública de rechazo de agente inyectado inalcanzable. |
| **EV-04 — Distribución** | Dos generaciones, manifiestos y bytes; instalación aislada; origen de resolución; recorrido documental genérico y **documental con `stack=odoo`**, separando T4 de CLI/esquema finales en T6/T7. |
| **EV-05 — Aislamiento** | HOME/XDG/temporales propios, overrides neutralizados, `CDAD_INSTALL_ROOT` explícito y canarios sin cambios en las rutas observadas del HOME real. |
| **EV-06 — Revisión** | Contraste independiente de D1–D5 y P-1–P-4, matriz Odoo por rol, diff real, permisos, compatibilidad, inventario de referencias y límites. |
| **EV-07 — Cierre** | Diff conforme, regresiones pertinentes, suite de cierre según política vigente y aceptación recuperable de la autoridad. |

Se acepta cuando todas las postcondiciones están acreditadas, no quedan bloqueantes y se obtiene aprobación por la autoridad vigente. Ningún skip de una promesa cuenta como pase.

Las pruebas se agrupan por promesa observable, sin cuotas de escenarios equivalentes.

## 7. Riesgos y límites

- **Cambio de stack durante una ejecución:** un destinatario publicado puede dejar de coincidir con el dominio vigente. Se conserva para recibir el trabajo ya despachado, repetir su registro idéntico o completar válidamente su write-ahead; un intento nuevo con agente declarado debe superar la comprobación actual. Un reemplazo legítimo publica un sucesor con agente rederivado. El orquestador registra y resuelve la situación sin reescribir historia.
- **Histórico sin agente:** su admisión para registrar un intento nuevo no autoriza inferir ni sustituir destinatario, ni exime otras precondiciones.
- **Integridad del destinatario:** excluir `agent` del render se conserva por compatibilidad. Esta unidad no añade un sello criptográfico histórico del campo; su autoridad sigue siendo el request publicado y los límites de publicación/despacho. El contraste estático no acredita el stack histórico ni la publicación de una variante.
- **Fixtures anteriores:** se identificaron simulaciones de históricos que eliminan solo `agent` en `tests/test_006_005_u1c_packet_agent.py`, `tests/test_006_005_u1b_dispatch_entry.py` y `tests/test_006_005_u2_opencode_module.py`. T5 incluye sus adaptaciones legítimas y ejecución antes de GREEN. Incluye también `tests/test_007_002_dispatch_recovery.py` para el contrato de reemplazo. Las listas no sustituyen la medición completa obligatoria de T2 ni autorizan relajar otras obligaciones.
- **Referencias Odoo:** T4 inventaría también `odoo-expert/references/evidence-and-quality.md` y las referencias de `odoo-make-env`, resolviendo cualquier cláusula incondicional pertinente dentro del alcance aprobado.
- **Deriva global:** la instalación real puede permanecer desactualizada. Esta unidad verifica una instalación aislada y vuelve a declarar esa limitación al cierre.

## 8. Fuera de alcance

- Agentes, roles, etapas, subfases, campos o selectores nuevos.
- Ampliar permisos o defaults de lectura/escritura.
- Introducir un sandbox o protección mecánica individual de todos los insumos.
- Cambiar modelos, mecanismos de recepción o reglas de aprobación.
- Crear runtimes o adaptadores.
- Ejecutar el piloto 010-003 o cerrar la épica.
- Corpus real de clientes, formatos binarios o publicación externa.
- Push o actualización de la instalación global.

## 9. `deferred-hardening`

| No comprometido | Motivo |
|---|---|
| Validación semántica automática universal | La estructura no demuestra fidelidad; permanece la revisión independiente. |
| Paridad total JSON Schema↔CLI contextual | El esquema carece de archivos, estado y autoridad. Se comprometen las correcciones concretas de PC-10. |
| Sesiones vivas en ambos runtimes o instancia Odoo | Esta unidad acredita integración distribuible y fixtures aislados, no conducta de modelos ni un addon real. |
| Sellado criptográfico histórico de `agent` o snapshot nuevo de stack | Requeriría otro contrato y transporte. Aquí se mantienen el render y la autoridad del request publicado. |
| Guarda mecánica nueva para variantes ausentes en vía nativa | Se compromete doctrina procedimental; el rechazo mecánico existente corresponde al adaptador externo. |
| Cobertura exhaustiva, rendimiento y combinatoria sin consecuencia contractual | No protegen otra promesa observable de esta unidad. |

Ninguna exclusión pospone una postcondición comprometida.

## 10. Referencias verificadas

Snapshot de producto de base: `3bea7a8d356e35ccb93d22d010632f1d7e7406bf`, junto con los borradores e insumos locales identificados en el paquete.

La revisión v4 parte de los siguientes archivos bajo `docs/specs/010-002-documentary-role-integration/`:

| Insumo | SHA256 |
|---|---|
| `spec.md` v3 | `1a94dbc04477d82e02b5bfa4843167e4c7cdf339697ac5ed46f398b88809d80d` |
| `plan.md` v3 | `4025d22f7988f735f8a780fdd85e3f698e7974349095128a1631bd2a3fbbad2c` |
| `plan-review-003.md` | `de25e03f49c9054437ff6d542bb698374af3f50cfd2add63f80ff51d98ad18c7` |
| `discovery-decisions-2026-10-31.md` | `e10f746c574798f0b6d06bacc9438f50ff48ff5e1d938bfb2f59d6336523c0ad` |

Fuentes y localizadores:

- D-1–D-5: `discovery-decisions-2026-10-31.md:15-125`; P-1–P-4: `147-183`, bajo el directorio de esta spec.
- B1, N5 y N6: `plan-review-003.md:16-53`; preservación de N1–N4: `59-66`.
- Primera revisión: `docs/specs/010-002-documentary-role-integration/plan-review.md:13-130`.
- N1–N4: `docs/specs/010-002-documentary-role-integration/plan-review-002.md:20-67`.
- Aceptación de perfil documental y combinación Odoo: `docs/epics/epic-010-documentary-specialization/plan.md:71-88`.
- Norma documental: `skills/cdad-cycle/references/documentary-contracts.md:89-188`.
- Criterio de diseño: `skills/cdad-cycle/references/design-principles.md:7-23`.
- Campos y validación: `skills/cdad-cycle/scripts/cdad_packet.py:1724-1785`.
- Exclusión de agente del render: misma ruta, `1977-2027`.
- Verificación publicada: misma ruta, `2110-2147`.
- Registro, repetición y finalización write-ahead: misma ruta, `4238-4253,4297-4412`.
- Derivación y preparación ordinaria: misma ruta, `6412-6425,6655-6722`.
- Reemplazo actual que debe corregirse: misma ruta, `3745-3854`, especialmente copia de agente en `3796-3801`, contexto nuevo en `3802-3808` y validación previa a publicación en `3824-3828`.
- Interfaz pública de reemplazo usada por regresiones: `tests/test_007_002_dispatch_recovery.py:526-570`.
- Defaults de alcance: `skills/cdad-cycle/scripts/cdad_packet.py:2266-2276`.
- Llamadores de recepción y ejecución: `skills/cdad-cycle/scripts/cdad_result.py:674,1362`; continuidad: `skills/cdad-cycle/scripts/cdad_continuity.py:1257`.
- Agente y publicación en adaptador externo: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:417-458`; write-ahead previo al lanzamiento y bloqueo: `2998-3031`.
- Selección contradictoria: `skills/cdad-cycle/SKILL.md:130-137`; `skills/cdad-cycle/references/sub-agent-strategies.md:144-165`; `sources/agents/adapters/opencode.md:69-74`; `sources/agents/adapters/claude-code.md:83-88`; `sources/roles/orchestrator.md:312-323`.
- Obligaciones Odoo de rol: `sources/roles/architect.md:145-153`; `test-writer.md:118-128`; `implementer.md:84-92`; `reviewer.md:106-115`.
- Conocimiento Odoo: `skills/odoo-architect/SKILL.md:38-47,84-117`; `skills/odoo-test-writer/SKILL.md:17-38,96-117`; `skills/odoo-reviewer/SKILL.md:56-83`; `skills/odoo-expert/SKILL.md:22-55`; `skills/odoo-make-env/SKILL.md:13-46,124-143`.
- Referencias a inventariar: `skills/odoo-expert/references/evidence-and-quality.md:5-38`; `skills/odoo-make-env/references/run-budget-protocol.md:10-35,73-79`; `references/odoo-sh.md:20-64`; `references/odoo-19-traps.md:30-44`, estas dos últimas bajo `skills/odoo-make-env/`.
- Generación: `Makefile:1-24`; `scripts/cdad-generate.py:616-707`.
- Aislamiento: `tests/conftest.py:28-126`; `tests/test_010_001_documentary_contracts.py:1316-1399`.
- Compatibilidad y fixtures conocidos: `tests/test_006_005_u1c_packet_agent.py:18-57,245-355`; `tests/test_006_005_u1b_dispatch_entry.py:819-837`; `tests/test_006_005_u2_opencode_module.py:936-955`.

La rederivación del sucesor es el comportamiento propuesto y decidido para implementar; no se presenta como comportamiento ya existente.
