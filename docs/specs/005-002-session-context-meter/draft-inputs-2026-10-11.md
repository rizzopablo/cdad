# Delta de entrada al draft — 005-002

Fecha: 2026-10-11. Estado: requisito de planificación solicitado por el dueño;
la spec y su aprobación siguen pendientes. Conservar el discovery realizado.
Fuente: [dirección estratégica](../../../findings/agent-operation-strategy-2026-10-11.md).

## Objetivo del ajuste

Medir para mejorar resultados, contexto y atención humana. Menos tokens o una
sesión que termina antes no demuestran una mejora si no entregó lo necesario.
La experiencia relatada de Project Management mostró avance y gasto continuos
sin validación suficiente: evitar optimizar solo actividad o velocidad.

## Qué llevar al draft

1. Conservar el formato neutral, primer lector OpenCode read-only y distinción
   entre datos observados, estimados y desconocidos del plan/discovery.
2. Además del primer `resume`, identificar el primer despacho de trabajo de rol
   cuando la traza lo permita; mantener ambos hitos separados. Despacho no prueba
   utilidad ni resultado aceptado. Distinguir sesión nueva/reanudada y ausencia
   del evento; excluir llamadas de ayuda. No inferir un despacho exitoso solo
   porque el texto del comando lo menciona.
3. Exponer las medidas de orientación disponibles: tiempo hasta esos hitos,
   llamadas/lecturas previas y volumen de salidas (total y máximo), junto a
   input por paso, acumulados y caché con su semántica. Reusar los datos ya
   relevados; precisar unidades, intervalo y procedencia en la spec.
4. El informe de aplicación vincula métricas con resultado/evidencia y límites:
   entrega aceptada, bloqueada, pendiente o desconocida según el registro
   disponible. Puede ser una anotación referenciada por el orquestador, no una
   nueva clasificación semántica del lector ni una aprobación automática.
5. No sumar el mismo costo dos veces al combinar coordinador y workers. Declarar
   qué sesiones están incluidas y qué relaciones se observaron; los enlaces
   entre CLI que no puedan verificarse permanecen desconocidos.
6. No equiparar input reportado con consumo facturado o capacidad máxima de
   contexto. Un costo nulo/reportado ausente no demuestra gratuidad.

## Datos útiles que no bloquean el primer incremento

Registrar cuando exista evidencia barata: repeticiones de suites, fricción de
permisos, correcciones tras review e intervenciones humanas. Clasificar cuáles
fueron innecesarias exige juicio; no atribuirlo al parser. Espera improductiva,
cuotas/ETA y calidad semántica quedan fuera del medidor mínimo.

## Aceptación a concretar

- Reproducir muestras existentes; usar S-BOOT-04 como entrada adicional si ayuda
  a cubrir primer despacho. Identificadores reales se resuelven en registros
  locales existentes; no se copian a contratos públicos.
- Una salida pequeña permite a 005-003 distinguir orientación de ejecución y
  consultar la evidencia original sin inyectar toda la sesión al contexto.
- El siguiente uso real permite relacionar ahorro con resultado. No se repite
  un desarrollo completo ni se afirma causalidad estadística por una muestra.
- Un evento no observable se informa como desconocido con causa, no como cero.

Antes de aprobar la spec, el architect ajusta la unidad para que siga siendo
pequeña: puede separar análisis cualitativo del instrumento determinista.
Este delta no autoriza cambiar contratos ya aprobados ni introducir un motor
de evaluación de sesiones, un dashboard o un scheduler.
