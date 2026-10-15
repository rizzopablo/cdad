# CDAD: prioridades de operación, planificación y aceptación de uso

Fecha: 2026-10-11.
Estado: **dirección y ajustes de planificación solicitados por el dueño**;
las opciones de implementación e investigaciones siguen abiertas.
Origen: conversación sobre [Michael Lynch, Why Are Coding Agents So Dumb?](https://mtlynch.io/why-are-coding-agents-so-dumb/).

## 1. Decisión y prioridad confirmada

El dueño confirmó que «1, 2, 3 y 5» refiere a la lista final de próximos pasos
del análisis, no a sus secciones temáticas. Orden de prioridad:

1. Completar la interoperabilidad real: 005-010, continuación de 005-009.
2. Medir y simplificar la operación: 005-002 y 005-003.
3. Mejorar de manera sustancial la planificación: 005-007, con investigación
   previa suficiente; cambiar plantillas no alcanza.
4. Incorporar gradualmente paralelismo y selección de recursos, con uso real
   y validación de resultados. Todavía sin feature nueva aprobada.
5. Ampliar después la ejecución autónoma durable. Es deseable, pero no debe
   acelerar trabajo sin validar ni multiplicar gasto sin resultados.

Prioridad de producto no significa ignorar dependencias: el paralelismo puede
necesitar seguimiento mínimo de trabajos. Eso no obliga a construir primero
una plataforma general de jobs ni a terminar <otro-proyecto>.

Se conserva la secuencia del epic vigente, incluida 005-004; no se agregan
IDs, aprobaciones de specs, activaciones ni mandatos de ejecución por este
documento. La sesión 005-010 en curso conserva su contrato.

## 2. Problema y evidencia: distinguir fuentes

El artículo señala deficiencias en gestión de tareas, delegación, comunicación
de planes, conocimiento del propio agente y autonomía. Propone también una
interfaz de supervisión, estimaciones, mejora desde las sesiones y uso de
cuotas. Es una experiencia y una visión de producto, no un benchmark de todos
los runtimes ni evidencia suficiente sobre las causas empresariales.

**Observación del dueño:** pruebas anteriores de Project Management con un
agente coordinador avanzaban demasiado rápido, consumían muchos tokens y no
se detenían a validar resultados. No se midieron esas trazas en esta revisión;
se registra el problema relatado, sin fabricar cifras ni causalidad técnica.

**Evidencia CDAD disponible:** 005-009 pasó tests con un doble que producía una
señal inexistente en el runtime real; 005-010 corrige esa frontera. El caso
S-BOOT-04 muestra orientación extensa pese a existir información operativa.
Ambos motivan comprobar el recorrido legítimo y el acceso a información útil.
Ver [discovery de 005-010](../docs/specs/005-010-real-opencode-delegation/discovery.md)
y [entrada de 005-003](../docs/specs/005-003-orientation-reduction/discovery-inputs.md).

## 3. Restricciones e intenciones que se conservan

- La utilidad del resultado y el tiempo/atención del usuario son criterios
  de producto. Tokens, tests, commits y tareas cerradas no los sustituyen.
- Contratos, independencia de roles y evidencia proporcional se conservan.
  La autonomía opera dentro del mandato; el silencio no amplía autoridad.
- Un ciclo opera con una versión instalada estable. La sucesora se adopta
  entre ciclos; las mejoras no modifican retroactivamente un encargo activo.
- Evaluar hacia adelante en desarrollos pendientes; no repetir desarrollos
  completos para comparar modelos o estrategias.
- Conservar el horizonte de ejecuciones prolongadas con contexto menor a 200k
  y, cuando sea viable, menor a 100k. Son objetivos a demostrar con uso real,
  no un límite rígido universal ni una capacidad ya acreditada por los paquetes.
- Poder usar un mismo modelo sigue siendo una opción válida. El routing
  automático no es prerrequisito de estas mejoras; no cambia aquí ninguna
  política de modelos vigente en un encargo particular.
- El sistema sirve a distintos usuarios, SO, CLI y organizaciones de carpetas.
  Método, proyecto, adaptador y configuración local son niveles distintos.
- Capacidad disponible, capacidad cargada y capacidad comprobada no son
  equivalentes. Cuando falte evidencia, declarar desconocido y cómo verificar.

### Contexto global y fronteras

Para agentes internos se prefiere acceso amplio al conocimiento autorizado
de varios proyectos, con foco activo por encargo y autoridad de escritura
acotada. No se impone un sandbox por repositorio. La organización en una cuenta
de usuario de un VPS es una decisión de despliegue; su frontera real depende
de los permisos de esa cuenta y del entorno, no del nombre de una carpeta.

El contexto global es recuperable por relevancia, no inyectado íntegramente.
Los recuerdos llevan proyecto, fuente, fecha y vigencia. Una decisión local
no se promueve en silencio a regla metodológica. La independencia del
test-writer respecto de la implementación relevante permanece.

Los futuros agentes Vulpo expuestos a clientes externos requieren aislamiento
estricto y separación de datos/autoridad entre clientes. Ese perfil no se
deduce del usado por los agentes internos; requiere diseño y verificación
propios. No se presenta una allowlist de comandos como sandbox.

## 4. Validar resultados debe acompañar a la autonomía

La condición para aumentar autonomía o concurrencia es poder reconocer un
resultado válido y contener el trabajo que no progresa. Una devolución de
un worker, una suite verde o una sesión idle no aprueban por sí solas el gate.

Para cada unidad se debe poder contestar: qué resultado útil entrega, quién
lo comprueba, con qué evidencia y qué trabajo depende de esa comprobación.
Trabajo independiente autorizado puede continuar mientras se valida otra
unidad; el trabajo dependiente no hereda un éxito supuesto. No es necesario
consultar al humano ni correr toda la suite en cada frontera.

Antes de una futura ejecución automática, resolver como mínimo:

- Identidad y estado de los intentos; registro previo al efecto y recuperación
  que reconcilia antes de repetir. Reutilizar la maquinaria existente.
- Presupuesto de trabajo/costo y concurrencia autorizado; si el runtime no
  reporta tokens o cuotas, declarar límites observables alternativos y su
  alcance. No inventar consumo ni traducir minutos directamente a tokens.
- Evidencia de avance útil, repetición sin información nueva y punto de
  replanteamiento. Un límite de intentos es una señal, no la estrategia.
- Distinción entre detenido, bloqueado, esperando validación y terminado;
  cancelación y timeout no deshacen efectos ya realizados.
- Una autoridad de coordinación por ejecución, aunque existan varios workers.
  Evitar dos sistemas de auto-continuación que relancen el mismo objetivo.

## 5. OpenChamber: aprovechar antes de duplicar

**Experiencia reportada por el dueño:** la WebUI es pesada pero útil para
desarrollar; ofrece notas por proyecto, buen visor/editor de archivos,
Markdown renderizado, navegador integrado y diff avanzado. Los agentes
subutilizan esas capacidades. El navegador tiene limitaciones con sitios
externos; se desea explorar documentación HTML completa y edición/visualización
de textos y planillas mediante OnlyOffice embebido.

**Verificación documental inicial, no prueba de la instalación local:**

| Superficie | Base consultada / estado | Pregunta operativa pendiente |
|---|---|---|
| Notas, tareas y planes por proyecto | [Documentación oficial](https://docs.openchamber.dev/notes-todos-plans/) describe persistencia entre sesiones e importación de planes Markdown/texto | Qué puede leer/escribir el agente en el despliegue utilizado; cuál es la fuente canónica de cada dato |
| Control de sesiones por agente | [Agent Control Tool](https://docs.openchamber.dev/agent-control-tool/) documenta creación, seguimiento y consulta de sesiones | Disponible con servidor gestionado por OpenChamber; la documentación excluye servidor externo/skip-start y extensión VS Code. Verificar modo y versión instalados antes de proponer integración |
| Previews, diffs y presentación de cambios | [README oficial](https://github.com/openchamber/openchamber/blob/main/README.md) y [Preview](https://docs.openchamber.dev/preview/) | Qué enlaces/artefactos puede producir CDAD para que el usuario revise en el lugar adecuado, sin copiar el diff entero al chat |
| Continuación por objetivos | [Session Goals](https://docs.openchamber.dev/session-goals/) | Comprobar cómo convive con gates, presupuesto, bloqueos y autoridad CDAD; no habilitar auto-continuación por mera disponibilidad |
| HTML local y OnlyOffice | Deseo del dueño; integración no verificada | Hosting permitido, embedding, autenticación, guardado al archivo canónico, revisión de cambios, disponibilidad web frente a desktop y costo de mantenimiento |

No asumir que una función visible en la UI es accesible al agente o a todos
los runtimes. Tampoco exigir que CDAD administre la UI para aprovecharla:
entregar archivos, enlaces y una explicación breve puede ser suficiente.
Si una nota de UI duplica un contrato, decidir su propietario y actualización;
no crear dos fuentes editables que puedan discrepar. La edición visual de un
contrato aprobado conserva el proceso normal de cambio de contrato.

**Salida de investigación esperada:** matriz por capacidad y despliegue
(observada/documentada/no disponible/desconocida), una demostración pequeña
del camino agente → artefacto → revisión humana y recomendación de reutilizar,
integrar o descartar. Mantener un camino portable para CLI sin esa UI.

## 6. Backlog operativo para no perder ideas

Estas líneas son investigación, no features aprobadas ni requisitos de 005-002.

| Tema | Resultado de investigación deseado | Ubicación / secuencia |
|---|---|---|
| Plan entendible por el humano | Resumen de intención, recorrido, decisiones y riesgos; detalle técnico progresivo; diagramas solo cuando aclaran | 005-007 + investigación de planificación |
| Capacidades y ayuda de la propia herramienta | Inventario compacto ligado a versión y configuración; comandos y recuperación comprobados | 005-003; extensión UI posterior si lo requiere |
| Vista unificada, móvil y notificaciones | Reusar sesiones/UI existentes; avisos por cambio material o decisión necesaria | Investigar OpenChamber antes de construir un dashboard |
| Intervenir en workers | Abrir, orientar, detener y reconciliar una sesión sin perder autoridad ni duplicar efectos | Investigación de coordinación y UI |
| ETA | Rangos con incertidumbre y calibración con trabajo comparable; evitar precisión ficticia | Tras observación suficiente de 005-002 |
| Recursos, cuotas y modelos | Disponibilidad observada, costo total y capacidad por tarea; fallback explícito y sin ampliar presupuesto | Prioridad posterior a planificación; no requiere benchmark multimodelo |
| Aprendizaje desde sesiones | Fricción repetida → causa → mejora acotada → siguiente uso real | Alimentado por 005-002/003; sin autoeditar contratos vigentes |
| Lectura de logs y salidas grandes | Extracción determinista, referencia al original y contexto acotado | Elegir casos repetidos medidos, no herramientas especulativas |
| Credenciales mediadas | Acceso a servicios sin incorporar secretos al contexto cuando sea necesario | Adaptadores/infraestructura; especial atención a Vulpo |
| Apertura y portabilidad | Método utilizable con CLI/proveedor/UI elegidos; diferencias de capacidades explícitas | Criterio transversal; verificar condiciones reales por proveedor |
| E2E y usabilidad | Evidencia técnica del recorrido y evidencia de que un consumidor logra su objetivo | Investigación prioritaria asociada a 005-007; ver §7 |
| Ejecución durable y <otro-proyecto> | Reusar componentes comprobados, evaluar interfaces pequeñas sobre CLI existentes | Posterior; no migración de arnés como prerrequisito |

## 7. Planificación avanzada y aceptación de uso

El encargo completo de investigación está en
[005-007/discovery-inputs.md](../docs/specs/005-007-progressive-planning/discovery-inputs.md).
Es parte del trabajo de discovery de esa feature; no se acepta cerrar la mejora
solamente cambiando títulos de templates o agregando más casillas.

TDD aporta comprobaciones de contratos; puede contener pruebas E2E, pero no
demuestra por sí solo que el contrato represente la necesidad ni que un usuario
pueda completar la tarea con esfuerzo razonable. Un recorrido automatizado con
instrucciones internas perfectas tampoco demuestra descubribilidad o comprensión.
La aceptación debe declarar qué demuestra cada evidencia y qué queda pendiente.

Para ambas investigaciones, usar próximos desarrollos reales y evidencia ya
disponible. No expandir todo epic-005 con una plataforma de UX, scheduling o
memoria. El discovery propone la primera mejora útil y separa incrementos que
requieran otro ciclo. No crea un agente nuevo por defecto.

## 8. Consumo por los ciclos pendientes

| Ciclo | Ajuste autorizado de planificación | Frontera |
|---|---|---|
| 005-002 | Datos para evaluar orientación y costo junto al resultado; delta de entrada a su draft | No repetir discovery ni construir un evaluador semántico universal |
| 005-003 | Orientación suficiente y capacidades disponibles; presentación accesible de lo que sigue | No dashboard nuevo ni cargar todo el manual/contexto global |
| 005-007 | Investigación avanzada de descomposición y aceptación de uso; primera aplicación en trabajo real | No scheduler, agente planner obligatorio ni plataforma de tests de UX |
| 005-004 | Tener presentes capacidades efectivas y acceso a entregas al verificar el ciclo real | Sin ampliar su alcance actual con integración UI |
| Futuro | Paralelismo/recursos; luego ejecución autónoma durable con validación | Requiere descomposición y autoridad propias |

Esta decisión se enlaza desde el plan del epic y el handoff. Antes de preparar
el próximo architect, el orquestador incorpora el delta de su feature; no se
reconstruye esta conversación ni se carga todo el backlog a cada worker.

## Fuentes y límites

- Artículo enlazado al inicio: motivación y catálogo de problemas; sin adoptar
  sus conclusiones como medición del estado de CDAD.
- Documentación de OpenChamber enlazada en §5, consultada 2026-10-11. Falta
  inventario de la instalación y prueba de acceso efectivo desde los agentes.
- [ADR-011](../docs/adr/ADR-011-autonomia-supervisada-limites-proporcionales.md):
  autonomía supervisada y controles proporcionales existentes.
- Los documentos de <otro-proyecto> consultados en el análisis tienen distintas fechas;
  no se auditó su runtime actual. No dar sus componentes por listos para integrar.
- No se midió la experiencia previa de Project Management ni se probó OnlyOffice.
