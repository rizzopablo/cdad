# Fricción de permisos durante la medición de C0

Fecha: 2026-09-24. Análisis de una sesión architect OpenCode a partir de su
registro local, la captura aportada por el usuario y las reglas fuente/instaladas.
No se copian identificadores de sesión, rutas personales ni transcript privado.
No se modificaron permisos, agentes o configuración ni se ensayaron evasiones.

## Hechos observados

1. Tres llamadas de conteo de líneas fueron rechazadas: una con `rtk wc -l`
   y dos con `wc -l` en la entrada registrada de la herramienta.
2. El architect obtuvo después los **22 conteos correctos** mediante
   `rtk grep -c '' agents/cdad-*.md agents/claude-code/cdad-*.md`.
3. La salida incluía ambos scribe-odoo: 97 líneas OpenCode y 46 Claude Code.
   Los subtotales publicados omitieron exactamente esas cantidades:
   1.475 en vez de 1.572 y 1.079 en vez de 1.125. El total correcto es 2.697.
4. No aparece una llamada posterior que calcule/verifique mecánicamente la suma
   en la sesión inspeccionada. La omisión está en la agregación del informe,
   no en los conteos devueltos por la herramienta.
5. Se rechazaron además `du -b`, un pipeline `find ... | wc -l` y `wc -c`.
   Son **seis llamadas de medición rechazadas** en total. También hubo rechazos
   de navegación/inspección ajenos a esas seis llamadas.
6. Como alternativas, `rtk find ... -printf` informó que ignoraba esa opción;
   otras dos llamadas `rtk find ... -size` informaron que no soportaban los
   predicados. Esas llamadas figuran como completadas, pero no produjeron la
   medición solicitada. Estado de herramienta completada no equivale a éxito
   semántico del encargo.

## Qué está explicado y qué falta atribuir

`scripts/cdad-bash-allowlist.sh:51-56` dispone de un helper para producir pares
de permisos comando/RTK. Sin embargo, `emit_base_allow` (`:143-160`) permite
`wc *` mediante `rule`, sin su par `rtk wc *`. Esa omisión también está en la
copia instalada del architect y en las reglas incluidas en el error real.
El catch-all deny deja sin permiso explícito la variante con RTK, en contra
de la intención declarada de emparejar comandos del propio generador.

Las dos llamadas simples a `wc -l` y la llamada `wc -c` también fallaron pese
a que el error enumera `wc *: allow`. La traza consultada no identifica la
regla ganadora ni la forma efectiva evaluada. No permite atribuir su rechazo
con certeza a una reescritura RTK, al parser, al orden de reglas o a otra capa.
No corresponde llamarlo aleatorio ni afirmar que lo causaron las reglas `/tmp`:
los comandos solicitados no acceden a `/tmp`.

Para cerrar esa atribución, observar la llamada efectiva y la regla ganadora
en un entorno controlado, usando la versión y configuración de esa ejecución.
El registro de sesión contiene versión **1.18.16**, distinta de la **1.18.31**
del probe histórico. Es un metadato de la sesión, no una comprobación del binario
instalado hoy. No reproducir prompts pagos ni cambiar permisos globales para
diagnosticar esta discrepancia.

## Interpretación causal

La política/herramientas bloquearon operaciones legítimas y desviaron al agente
hacia alternativas menos directas. El agente terminó publicando una suma
incorrecta pese a tener los valores individuales correctos disponibles.

La secuencia respalda que la fricción contribuyó al fallo y al costo de trabajo.
No demuestra que una restricción obligara matemáticamente a omitir esos archivos,
ni que sin ella GLM nunca se equivocaría. Tampoco permite estimar la frecuencia
global de falsos rechazos o concluir que toda separación de permisos es inútil.

La medición de bytes quedó pendiente y fue declarada como tal, correctamente.
El total de líneas se presentó como medido aunque su agregación no estaba
verificada: ese dato debe corregirse sin atribuir todo el incidente a aritmética
del modelo ni dar por irrelevante la conducta de las herramientas.

## Implicación para el diseño de CDAD

Evaluar los límites por la garantía que aportan y por su fricción observable.
El contrato read-only del architect permite lectura global: contar archivos ya
legibles no cruza una frontera de rol. Debe existir una capacidad fiable para
medir y agregar esos datos con herramientas deterministas.

La allowlist actual no es por sí sola una frontera de filesystem: por ejemplo,
permite `make *` también a lectores, aunque el efecto de una receta depende
del proyecto. Bloquear utilidades de conteo no convierte los demás comandos
permitidos en operaciones demostrablemente de solo lectura.

Dirección recomendada, pendiente de especificación/revisión:

- Preservar las fronteras importantes: test-writer sin implementación,
  implementer sin edición de tests, reviewers sin edición del producto,
  autoridad de aprobación y operaciones externas conforme al mandato.
- Dar capacidades completas para la tarea autorizada: lectura, búsqueda,
  conteo y cálculo; temporales en un espacio definido cuando se necesiten.
  Evitar listas de prefijos incompletas como sustituto de esas capacidades.
- Cuando haga falta una garantía fuerte, limitar recursos/efectos desde el
  entorno de ejecución y su política de paths; las instrucciones conductuales
  y las comprobaciones posteriores cumplen funciones distintas. No declarar
  aislamiento fuerte donde no se implementó.
- Mantener salida original exacta para mediciones/evidencia. Un wrapper de
  reducción de salida solo es apropiado si conserva la semántica necesaria;
  soportar un comando de nombre parecido no demuestra equivalencia.
- Un rechazo inesperado de una operación legítima genera diagnóstico breve
  y escalamiento al coordinador. Evitar reintentos equivalentes y sustitución
  de cálculo por una estimación presentada como dato medido.
- Probar capacidades permitidas además de accesos prohibidos. Registrar
  rechazos legítimos/falsos, vueltas necesarias y tareas incompletas al usar
  desarrollos reales; sin comparar modelos ni rehacer features terminadas.

Este hallazgo puede incorporarse al inventario de permisos/adaptadores de
004-001 y a la coherencia de paths/capacidades de 004-002. No exige otro epic
ni un sandbox general construido ahora. Sí exige que el refactor de fuentes
no perpetúe una política defectuosa solo porque la versión antigua la contenía.

## Contraste con la propuesta posterior de Claude

- La ayuda del RTK instalado, consultada en esta revisión, sí lista `wc` como
  comando soportado. Corregir el par faltante es una reparación focal razonable;
  no explica por sí sola los rechazos de `wc` simple ni certifica preservación
  de toda la salida: la ayuda describe compactación de rutas y espaciado.
- El registro muestra que los tres intentos de `wc -l` fallaron. No hay un
  primer intento simple exitoso; no describir el caso como éxito con un glob
  seguido de fracaso con dos ni como no determinismo demostrado.
- Sesiones y worktrees separados aportan separación de contexto/trabajo, pero
  no impiden por sí mismos acceso a otros archivos. Un path-guard limitado a
  Edit/Write tampoco controla automáticamente los efectos de Bash.
- Reservar todos los denies para acciones irreversibles/externas eliminaría
  límites metodológicos relevantes: leer implementación durante RED o editar
  tests durante GREEN también puede invalidar las garantías aunque sea local
  y reversible. Preservar esos límites con mecanismos honestos y útiles.
- Medición/lectura se permite dentro del alcance del rol. Un permiso global
  por nombre de herramienta no sustituye comprobar los paths/efectos que
  importan. La prioridad es evitar falsos rechazos del trabajo autorizado.
- La telemetría de denegaciones encaja en 003-003; clasificar un falso rechazo
  requiere conocer objetivo, rol, paths y efecto, no solo contar eventos.

No se aplicó una modificación de permisos al documentar esta propuesta.
