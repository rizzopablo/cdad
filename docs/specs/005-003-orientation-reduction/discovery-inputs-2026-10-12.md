# Delta de entrada al discovery — 005-003

Fecha: 2026-10-12. Aprobado por el dueño («ok»), a partir de la verificación de Codex sobre la
reapertura de 005-002 y de la revisión del orquestador Claude. Complementa
[discovery-inputs.md](discovery-inputs.md) sin reemplazarlo. No cambia el plan del epic: aplica su
sección «Ajuste de los ciclos pendientes» («la mejora debe llevar a un encargo útil, no solo a una
invocación temprana de `resume`»). Si la spec necesita enmendar la fila de 005-003, se hace con la
autoridad pertinente.

## Alcance: el proceso completo de delegación

Además de las lecturas previas al `resume`, el discovery cubre cómo se prepara, delega y valida el
trabajo. Línea base real: la reapertura de 005-002 (2026-10-12), con 12 sesiones de roles en unas
2 h 55 min, unos 40 min del orquestador entre despachos, el implementer corriendo dos veces la
suite completa (unos 15 min cada una) dentro de GREEN, y cada sesión de rol re-orientándose sobre
una spec de unos 50 KB.

Prácticas a evaluar (son hipótesis a medir, no soluciones decididas):

1. **Validación concreta en cada encargo.** El paquete trae los comandos de validación aplicables
   y dice cuándo ampliarla. No deja «regresiones necesarias» como invitación a correr todo. La
   suite completa la corre una vez quien cierra.
2. **Verificación en dos niveles.** Siempre: procedencia, diff, alcance y los focales, que tardan
   segundos. Solo con un motivo concreto: la suite o la integración. Se reutiliza la evidencia
   equivalente cuando su procedencia está verificada.
3. **Agrupar sin mezclar roles.** Un paquete RED para varios defectos de una misma clase y
   después un GREEN, cada uno en su sesión. El paquete lleva el contrato aplicable y referencias
   para ampliar, sin obligar a releer la spec entera.

## Aceptación

Además de las lecturas previas al `resume`, se observan con el medidor de 005-002 y con trabajo
real:
- el tiempo de preparación del orquestador entre despachos;
- la reorientación de cada rol (llamadas y salidas antes de la primera acción del encargo);
- las ejecuciones redundantes, como la suite fuera del cierre o el mismo gate re-ejecutado sin
  motivo.

No se repiten desarrollos para comparar.

## Consumo de métricas (R4 de 005-002)

Entregar 20 documentos de unos 8 KB es demasiado para decidir qué ocurrió. El consumidor necesita
primero un resumen del conjunto: sesiones incluidas, cobertura, hitos, magnitudes relevantes y
referencias al detalle. El detalle por sesión sale solo a pedido. No es un dashboard.

## Prerrequisito de validación (D11 de 005-002)

D11 (`docs/specs/005-002-session-context-meter/debt.md`) se cierra antes de usar la integración real
del medidor como gate de 005-003, con su condición de cierre causal. No bloquea el discovery.
