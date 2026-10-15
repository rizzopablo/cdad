# Capacidades observadas del runtime — 2026-09-17

Probe independiente de lectura, agente `runtime_probe`, modelo solicitado
`gpt-5.6-sol`. Síntesis materializada por el orquestador. No contiene sesiones
de proyectos, credenciales ni rutas personales.

## Codex nativo: construcción

Las herramientas disponibles permiten seleccionar modelo y crear hijos sin
conversación heredada. Comparten filesystem; no exponen política de archivos
por rol. Separación de contexto comprobada por el contrato de la herramienta;
las restricciones de archivos son conductuales. No equivalen a un sandbox.

## OpenCode: integración prevista

Ejecutable local: **1.18.31**, presente fuera de PATH. SDK y plugin instalados:
**1.17.13**. La diferencia requiere prueba de compatibilidad antes de confiar
en los tipos del SDK como evidencia del comportamiento del servidor.

La ayuda y los tipos locales exponen:

- Servidor local `serve`, incluido modo `--pure` sin plugins externos.
- Sesiones: create, get, list, status, children, messages, fork y abort.
- Prompts síncronos o asíncronos con agente/modelo explícitos; continuar usa
  el identificador existente, crear uno nuevo permite reconstruir contexto.
- Eventos de mensajes, partes, estado, idle, compactación y errores.
- Mensajes/step-finish con tokens de entrada/salida/razonamiento/caché,
  identificadores de modelo/proveedor, tiempos y costo reportado.
- Export/import. Las opciones de replay visual del CLI no controlan el contexto
  del modelo ni garantizan idempotencia de efectos de herramientas.

El plugin instalado de agentes en segundo plano utiliza sesiones hijas,
prompts asíncronos, espera de idle/error y recuperación de mensajes. Su registro
en memoria no basta para recuperarse de un reinicio; debe reconciliarse con
sesiones y artefactos persistidos.

## Límites para los contratos de 003/004

Los tokens se reportan por pasos/mensajes. No se observó un campo público de
límite duro por sesión. Abortar tras observar un umbral puede llegar tarde;
no demuestra que una llamada en curso esté dentro del presupuesto.

La continuidad debe comprobar tanto la reconstrucción como el consumo real,
con margen preventivo y desconocidos explícitos. No se sumarán a la vez tokens
de mensajes y step-finish para el mismo trabajo. El límite de contexto y el
consumo acumulado durante horas son magnitudes diferentes.

Las APIs hacen viable la automatización, pero no prueban por sí solas que el
MVP complete un desarrollo real dentro de 200k. Ese criterio sigue pendiente.
Una prueba de sesiones vacías sin invocar modelos verifica sólo compatibilidad
del transporte; no demuestra routing, calidad ni permisos durante un desarrollo.

## Smoke test de sesiones vacías

El agente comprobó create/get/list/messages/fork/children/delete contra el
servidor local 1.18.31. Mensajes vacíos y estado `{}` para sesiones inactivas.
`create(parentID)` crea una relación padre/hijo; `fork` produce una sesión
independiente, sin esa relación. No deben tratarse como equivalentes al reconciliar.

Se detectó una limitación y se detuvo el probe: aunque los directorios XDG y la
base de sesiones eran temporales, OpenCode leyó su configuración heredada fuera
de esas raíces. Por eso el resultado es **inválido como prueba de aislamiento
completo**. No se enviaron prompts ni llamadas a proveedores; se eliminaron las
sesiones temporales y se apagó el servidor. No se repite sin resolver primero
esa lectura mediante una capacidad documentada o aislamiento de filesystem.

La compatibilidad de endpoints observada sigue siendo información útil; no
certifica una instalación limpia, permisos por rol ni aceptación del MVP.
