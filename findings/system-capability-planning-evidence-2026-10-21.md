# Evidencia metodológica para planificar capacidades de sistema

Fecha: 2026-10-21. Caso consumidor anonimizado: **S-SYS-01**.
Estado: **insumo necesario para el plan de seguimiento de Superlite; no es una
spec aprobada, una auditoría nueva del producto ni autorización para cambiar
contratos activos o ejecutar trabajo sobre el consumidor**.

## Propósito y uso

Este hallazgo registra evidencia metodológica para que la planificación derivada
del análisis Superlite considere cómo construir y comprobar capacidades que
atraviesan componentes y dependencias operativas. Debe consumirse en el discovery
del Epic A, empezando por A1 (criterio de división), y justificar A2 únicamente
si el análisis encuentra una brecha concreta de verificación de interfaces.
La recepción posterior en A3 requiere un trabajo pendiente apropiado y autorizado.

Antes de activar cualquier propuesta, reconciliar este insumo con la propuesta
de [planificación y ejecución proporcional](../docs/planning/superlite-followups-2026-10-19/plan.md),
el [ciclo de construcción incremental](../docs/planning/proposed-cycle-incremental-construction.md)
y los contratos vigentes. El análisis complementa el hallazgo previo de
[construcción incremental y validación reproducible](incremental-construction-and-reproducible-validation-2026-10-17.md)
y la investigación de [planificación avanzada y aceptación de uso](agent-operation-strategy-2026-10-11.md).
No crea una tercera iniciativa ni un formato, rol o gate universal.

## Fuentes y alcance

- **E-RET — retrospectiva metodológica de S-SYS-01.** Documento aportado por el
  dueño, líneas 1–24, 26–40, 42–55, 57–82, 84–116 y 118–169. Resume relaciones
  operativas, secuencia recurrente, casos y preguntas para planificar. Es un
  análisis documental del caso, no evidencia independiente de cada ejecución.
- **E-G10 — informe de integración G10.** Líneas 5–8, 21–27, 40–53 y 66–81.
  Distingue arreglos comprobados localmente, estado incompleto y expectativas
  pendientes de comprobar en el host.
- **E-G13 — informe de integración G13.** Líneas 5–21, 25–42 y 49–62.
  Registra lectura nativa de configuración heredada, estados de observación,
  resultados de sonda con un Virtualmin falso y riesgos aún por verificar.
- **E-REC — recorrido operativo de referencia.** Líneas 1–18, 22–34,
  36–58 y 60–99. Documento vivo de integración que declara su alcance de
  laboratorio; contiene mediciones, límites y hallazgos relatados por el dueño.

Los localizadores privados de estas fuentes se conservan en un registro local
separado: `.cdad/local/system-capability-planning-2026-10-21/manifest.json`, con
copias de origen y hashes. Todo ese directorio está ignorado por Git. Las
referencias E-* y sus líneas identifican aquí el contenido sin
publicar rutas privadas, hosts, dominios, usuarios, credenciales ni sesiones.
Webmin, Virtualmin, Podman, Odoo y sus versiones son nombres de tecnologías
transferibles; no se identifica públicamente el proyecto consumidor.

## Evidencia observada y límites

La retrospectiva describe un patrón en que encargos delimitados y comprobaciones
locales eran válidos dentro de su alcance, pero el recorrido completo revelaba
diferencias en consumidores reales y generaba correcciones posteriores (E-RET,
líneas 26–40, 57–70). Los informes y el recorrido aportan ejemplos concretos:

| Caso | Evidencia documental y alcance |
|---|---|
| Configuración sin `[options]` | El lector empleado por los tests aceptaba la salida sin sección, mientras el lector real de Odoo la rechazaba; G10 registra que el generador se corrigió y que `configparser` leyó `[options]` con 11 claves (E-RET, 44–46; E-G10, 5–8, 55–60). La suite local no acreditaba esa frontera real. |
| Decidir init/start sin ejecutar init | G10 registra que existía el predicado, pero faltaban la inicialización real, fijación de credencial/URL y borrado del inicializador. El inicio quedó cerrado en fail-closed para `init`/`fix`; `exec` sí iniciaba el contenedor (E-RET, 47; E-G10, 24–27). |
| Rechazo permanente que satisface una implicación | Una garantía «si declara éxito, debe cumplir propiedades» evita falsos éxitos, pero `ok=0` constante también satisface esa implicación. G10 documenta que la superficie carecía de observables para acreditar `ok=1`; mantener rechazo veraz no completaba el servicio (E-RET, 48; E-G10, 21–26, 70–81). |
| Configuración heredada no observada | La lectura manual no resolvía el valor global de la plantilla Virtualmin; el driver se abstenía e inyectaba `none`. G13 registra el uso de la API/CLI nativa y estados `measured`, `unresolved` y `unavailable`; ante valor no resuelto, el producto rechaza antes de efectos (E-RET, 49; E-G13, 5–20, 32–40). |
| Conocimiento de Odoo 20 no transferido | La particularidad de red ya figuraba en la receta experimental, pero no llegó a la configuración del producto. En el entorno documentado, Odoo 20 escuchaba en loopback; `http_interface=0.0.0.0` permitió acceso desde el host en la sonda. No se generaliza el comportamiento observado a toda instalación (E-RET, 50; E-REC, 31–33, 66–70). |
| Copia que elimina inicializador y arranque que omite credencial | El recorrido documenta que repoblar `runtime/` eliminó el programa D7 y que el comando alternativo inició Odoo sobre base inicializada sin el testigo y con credencial predeterminada; una barrera de red impidió que quedara accesible. Recomienda cierre seguro y reponer el programa antes del inicio (E-RET, 51; E-REC, 30–33, 71–75). |
| Preparación del laboratorio repetida | La retrospectiva refiere reconstrucción de preparación y repetición de operaciones sobre dominio/certificado; el hallazgo incremental previo también registra pérdida de recursos reutilizables al limpiar el entorno. Son evidencia del caso y de relato documentado, no una medición comparativa del costo (E-RET, 52; `incremental-construction-and-reproducible-validation-2026-10-17.md`, líneas 31–45). |
| Credencial visible y espacios al copiar | La retrospectiva refiere confusión de la plantilla y espacios al copiar. E-REC confirma que la variante plantilla mostró una credencial que se confundió con una instancia (líneas 83–86), y atribuye espacios al HTML nativo de Virtualmin, no al valor guardado (líneas 88–93). El impacto de uso se registra como observado/relatado en ese recorrido, no como prueba general de interfaz. |

E-G10 separa explícitamente los PASS locales de la integración con host y deja
pendiente la ejecución real de D7 (líneas 40–53, 74–81). E-G13 presenta salida
de una sonda con Virtualmin falso y expectativas para una corrida futura; no
acredita aceptación posterior en el host (líneas 25–42, 57–62). E-REC sí registra
mediciones de laboratorio, pero no demuestra que todas las causas remotas de la
retrospectiva hayan sido verificadas independientemente. En particular, causas
raíz posibles —como el estado de D7 que no llegó a la superficie— siguen siendo
hipótesis si la fuente así las califica (E-G13, líneas 9–11, 61–62).

Este material no permite atribuir todo costo a CDAD, estimar ahorro, inferir una
tasa general de fallos ni concluir que cada diferencia era previsible (E-RET,
141–153). No confundir decisión local, ejecución, integración con consumidor y
uso por una persona: cada nivel necesita evidencia y alcance declarados.

## Marco de análisis acordado con el dueño

El marco es **contratos, garantías exigidas y evidencia**. El contrato expresa
obligaciones y condiciones; la garantía nombra la propiedad necesaria; la
comprobación es el procedimiento elegido y la evidencia es lo observado con su
alcance y limitaciones. La planificación pregunta qué necesita el consumidor,
bajo qué condiciones, quién produce el resultado, cómo se comprueba y qué sigue
sin demostrar.

No se toma TDD como marco principal de este análisis ni se equipara garantía
con un test de código. Una comprobación puede ser automatizada, una ejecución
del consumidor real, una inspección, observación operativa o recorrido visible.
La cobertura pertinente es la de las obligaciones y relaciones del sistema,
sin inferirla de porcentajes de código ejecutado ni exigir un test por frase.
Esto no elimina la separación de roles ni modifica contratos activos.

## Consecuencias para el discovery de planificación

El problema transferible no es simplemente que falten pruebas. Es que tareas
válidas y una cadena de dependencias entre tareas pueden dejar sin representar
dependencias operativas: configuración efectiva, identidad, estado previo,
orden, espera, efectos, observación y aceptación por el siguiente consumidor.
La planificación debe preguntar qué capacidad completa necesita el consumidor,
qué supuestos operativos debe resolver el productor y qué evidencia acredita la
unión. Un DAG de tareas no basta cuando omite esas relaciones.

Evaluar durante A1, y llevar a A2 sólo los gaps concretos:

- Organizar el recorrido operativo temprano con el usuario/sistema consumidor
  y sus requisitos verificables. Identificar capacidades consumibles, no sólo
  entregas parciales o decisiones previas a la capacidad que las ejecuta.
- Buscar una primera capacidad vertical real temprana que atraviese productor,
  operación y consumidor. Esto descubre incompatibilidades antes de acumular
  entregas parciales; no obliga a integrar todo en cada iteración.
- Guiar exploración e integración por riesgo e incertidumbre: ensayar pronto lo
  que depende de APIs nativas, estado heredado, identidad o efectos irreversibles;
  detallar después lo que sólo puede conocerse al observar la etapa anterior.
  No pretender enumerar de antemano toda incógnita ni fijar mecanismo sobre hechos
  no comprobados.
- Hacer que cada aprendizaje útil viaje con productor, consumidor, versión,
  evidencia, alcance y estado de transferencia. Un hallazgo en receta o experimento
  no prueba que llegó a la configuración o al paquete que lo consume.
- Mantener una responsabilidad explícita de integración a través de roles y
  handoffs, preservando la revisión independiente. Distribuir contexto pertinente
  sin cargar toda la historia al orquestador ni crear otro agente por defecto.
- Hacer visible la aceptación de uso lo bastante pronto para informar el diseño.
  Una capacidad técnicamente integrada puede seguir siendo confusa o inutilizable
  desde la interfaz anfitriona.
- Consolidar con seguridad el contrato vigente: retirar historia acumulada sólo
  después de identificar las garantías actuales, sus consumidores y evidencia.
  Cualquier cambio de contrato requiere su autoridad y proceso propios; este
  análisis no autoriza modificar contratos activos ni paquetes despachados.
- Declarar para cada evidencia si demuestra decisión, ejecución, integración o
  uso; qué versión y consumidor cubre; y qué sigue sin observar. Los tests son
  instrumentos posibles, junto con sondas, logs y aceptación real, según el
  contrato. No hacen falta tests por frase ni porcentajes de cobertura.

Estas preguntas son insumo de discovery, no casillas obligatorias para toda tarea.
No convierten cada cambio en un recorrido E2E, una etapa universal, un formulario,
un gate adicional o una reconstrucción completa. Aplicar la evidencia proporcional
y la reutilización justificada por el contrato y el riesgo.

## Relación con trabajo metodológico previo y autoridad

### Antecedentes que esta planificación debe reconciliar

| Antecedente | Relación con el caso actual |
|---|---|
| [Contexto y eficiencia, 2026-09-16](context-token-efficiency-2026-09-16.md) | Origen del esfuerzo por reducir carga de coordinación y conservar contexto para el desarrollo. La eficiencia debe evaluarse junto al resultado útil, sin un techo universal. |
| [Fricción de permisos, 2026-09-24](permission-friction-c0-2026-09-24.md) y [ADR-011](../docs/adr/ADR-011-autonomia-supervisada-limites-proporcionales.md) | Un encargo válido puede resultar impracticable por las capacidades efectivas; las restricciones deben tener motivo y permitir el recorrido legítimo. |
| [Operación, planificación y aceptación, 2026-10-11](agent-operation-strategy-2026-10-11.md) | Ya se identificó la necesidad de planificación avanzada y aceptación de uso, con evidencia de proyectos reales; repetir esas palabras no resuelve su aplicación. |
| [Construcción incremental, 2026-10-17](incremental-construction-and-reproducible-validation-2026-10-17.md) | Conservar preparación, estado y aprendizaje; distinguir exploración y reproducción. El nuevo caso amplía la transferencia hacia las capacidades del producto y sus consumidores. |
| [Superlite, 2026-10-19](superlite-transferable-ideas-2026-10-19.md) | Contratos de dependencia, ejemplos y comprobaciones fake→real aportan mecanismos; requieren evidencia adicional de operación y uso cuando el objetivo la necesita. |
| S-SYS-01, 2026-10-21 | Relaciona entregas parciales, dependencias operativas, aprendizaje no transferido y experiencia de uso en un mismo sistema. |

Estos antecedentes no constituyen una serie experimental comparable ni prueban
una causa única. Sirven para identificar recurrencias, principios ya acordados
y brechas aún pendientes, evitando volver a planificar como si fueran nuevas.

La estrategia histórica ya pide planificación avanzada y aceptación de uso con
un desarrollo real, sin agregar un agente planner o plataforma UX por defecto
([agent-operation-strategy, §7](agent-operation-strategy-2026-10-11.md#7-planificación-avanzada-y-aceptación-de-uso),
líneas 165–181). El ciclo incremental ya propone investigar evidencia y reglas,
mapear fuente→consumidor, preservar avance y aceptar sobre trabajo pendiente;
mantiene la decisión de cuánto intervenir proporcional al riesgo, sin reinicio
ni secuencia universales ([hallazgo incremental](incremental-construction-and-reproducible-validation-2026-10-17.md),
§§2–7). Reconciliar explícitamente estos alcances con el plan Superlite y consolidar
el insumo en A1; no ejecutar ni registrar dos iniciativas equivalentes.

El análisis está autorizado como documentación y preparación de planificación.
No es spec aprobada, no activa el Epic A/B, no cambia estado ni contratos de
trabajo activo y no autoriza nuevas pruebas o acciones en S-SYS-01. La próxima
instancia responsable debe reconciliar versiones y contratos antes de proponer
el delta y obtener aprobación por el mecanismo vigente.
