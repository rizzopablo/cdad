# Plan prioritario: proyecto Perl/Webmin y delegación entre CLI

Fecha: 2026-10-10. Preparado por instrucción del dueño para habilitar el siguiente
proyecto consumidor. **Propuesta de ampliación del epic**, lista para aprobar y
aplicar mediante el encargo de continuación. No es una spec de feature aprobada.
No modifica todavía `plan.md`, `.cdad-state.json` ni contratos de 005-002.

## 1. Punto de partida verificado

- 005-006 figura `done`, el ciclo está en `idle` y su último paquete está
  `completed`. El cierre y la instrucción del dueño autorizan su despliegue.
- La instalación global declara `35062b0cf1842c5fc4a09bd68c18084f78e7c8f5`,
  perfil `basic`. Marcador y manifiesto coinciden: **334/334 archivos del
  manifiesto con hash correcto, ninguno ausente y cero conflictos**.
- `SKILL.md`, `project-start.md`, `cdad-version-check.py` y `epic-planning.md`
  de las tres bases instaladas coinciden byte a byte con ese commit. El
  orquestador global de OpenCode contiene la entrada de arranque desde reposo
  y `<skill-dir>`, sin el marcador incorrecto de instalación anterior.
- Los agentes derivados de **este repo** todavía declaran `7f66619`. La
  comprobación instalada da `DRIFT`, rc=1. No es un fallo del despliegue global:
  esos derivados locales deben republicarse desde la fuente vigente antes del
  siguiente despacho. No editar su manifiesto ni sus agentes a mano.
- Esta revisión comprueba archivos instalados y procedencia; **no** demuestra
  que un servidor persistente o una sesión ya abierta los haya cargado.
- R2, el arranque real del consumidor en una sesión nueva, sigue sin evidencia
  registrada. El dueño cerró 005-006 aceptando esa verificación pendiente; no
  reabrirla por documentación. Reabrir o corregir si el uso real falla.
- 005-002 tiene discovery realizado y está marcada `in-progress`, pero pausada;
  no hay paquete de ella activo. Conservar su trabajo y su condición de pausa.

No repetir la suite completa de 005-006: su cierre declara 685 tests verdes y
review sin bloqueantes. La comprobación anterior es propia; esa suite es
evidencia heredada del cierre, no una nueva corrida de esta revisión.

## 2. Enmienda propuesta al epic

Resultado inmediato: desde una instalación estable, los roles pueden trabajar
en el proyecto Perl/Webmin con su organización real, y un coordinador Claude
puede encargar trabajo a OpenCode y recibirlo por el flujo CDAD existente.

| Prioridad | Feature | Resultado y frontera | Dependencia |
|---|---|---|---|
| 1 | `005-008-project-path-capabilities` | Capacidades de lectura, edición y validación coherentes con la política del proyecto; primer consumidor Perl/Webmin con tests anidados. No crea agentes Perl manuales ni otro sistema de políticas. | 005-006 cerrada y desplegada |
| 2 | `005-009-cli-delegation` | Interfaz común de delegación externa y primer recorrido real Claude → OpenCode, con rol, proyecto, entrega y re-entry verificables. Diseñada para otros CLI en cualquiera de las dos posiciones; no exige implementarlos todos. | 005-008 para la aceptación conjunta del consumidor |

Orden después de ambas: retomar 005-002, luego 005-003, 005-007 y 005-004 según
el plan vigente y sus dependencias. No cancelar 005-002 ni volver a hacer su
discovery por cambiar la prioridad. La ampliación de 005-004 solo corresponde
si su discovery confirma trabajo compartido; no dar su soporte nativo por hecho
porque Claude pudo orquestar un worker externo.

Al aplicar la enmienda:

1. Añadir las dos filas después de 005-006 y ampliar el alcance con capacidades
   de rutas de proyecto y delegación externa interoperable.
2. Registrar la instrucción del dueño que aprueba esta propuesta. El prompt
   de continuación incluye esa aprobación; **no** registrar una respuesta que
   todavía no se haya recibido.
3. Sincronizar `epic_features` a través de su escritor único, el orquestador.
   Añadir ambas como `queued`; conservar 005-002 pausada y las features cerradas.
4. Registrar la aprobación del plan actualizado con su ruta y hash reales,
   según el mecanismo vigente, antes de preparar el architect. No transferir
   una aprobación de otro archivo ni inventar una aprobación de spec.
5. Mantener los criterios existentes del epic y agregar la aceptación conjunta
   del §5. Una capacidad nueva no equivale a una cifra de ahorro demostrada.

POLICY-CLASS completa, CI, sandbox y una plataforma universal de jobs siguen
fuera. La corrección focal de coherencia clasificador→permisos **sí** entra.
Los valores de modelos y rutas de instalación son configuración local, no
nuevas constantes de la metodología.

## 3. 005-008: capacidades de proyecto, primer consumidor Perl/Webmin

### Problema reproducido

En el producto instalado, una política con implementación
`webmin-module/module/` y tests `webmin-module/module/t/` clasifica correctamente
`main.pl` y `index.cgi` como implementación, y `t/basic.t` **y** `t/helper.pl`
como tests. Pero `_derived_maps` del test-writer genera el deny de lectura de
la raíz de implementación sin el allow posterior del árbol de tests anidado.
Permite editar esos tests mientras puede impedir leerlos.

Referencias de discovery: `skills/cdad-cycle/scripts/cdad_packet.py`,
`classify_path`, `_test_patterns`, `_derived_maps`; tests existentes de política
y publicación derivados de 004-002. La sonda prueba mapas generados; aún falta
probar mediación real en una sesión del runtime.

### Criterios que el architect debe convertir en postcondiciones

1. Una política válida con tests anidados permite al test-writer leer y editar
   sus tests y auxiliares declarados; la implementación conserva el deny de
   lectura mediada. El implementer puede editar implementación y no tests.
2. Clasificación y permisos derivados concuerdan con la prioridad vigente de
   `test_roots`/`test_files`, implementación y rutas privadas. Incluir un caso
   focal de `test_files` bajo implementación: no corregir solo el ejemplo `.t`.
   Una excepción de tests nunca reabre una ruta privada.
3. Un segundo layout convencional funciona sin regresión. No añadir reglas
   globales `**/t/**` o `**/*.t`: el proyecto declara sus árboles concretos.
4. El proyecto registra comandos apropiados para sintaxis y tests Perl en el
   lugar canónico existente, con regresión proporcional y suite al cierre.
   Los roles reciben las convenciones y referencias de dominio necesarias.
   Descubrir intérprete, runner y dependencias disponibles; una ausencia genera
   diagnóstico útil, no cambios no autorizados en máquinas productivas.
5. El producto instalado demuestra las capacidades positivas y negativas
   relevantes mediante operaciones reales del runtime. No presentar grep,
   shell o sesión separada como sandbox ni volver a allowlists por comando.

### Unidades de trabajo propuestas

- **T1: coherencia de política y derivados.** RED focal contra comportamiento
  observable, GREEN de la familia de permisos afectada y regresión de módulos
  tocados. Reusar fixtures existentes. No imponer funciones internas al test.
- **T2: procedimiento de uso Perl/Webmin.** Reutilizar la política y el arranque
  de 005-006; documentar solo la brecha real de comandos/referencias de dominio
  que discovery encuentre. Si ya está resuelta, verificarla y no agregar otra
  skill ni duplicar el bootstrap.
- **T3: recorrido instalado.** Preparar agentes desde la política, comprobar
  capacidades con pruebas pequeñas y dejar una entrega desplegable. Un fixture
  puede verificar comandos de tests sin implementar el producto consumidor.

Antes de RED, el plan de la feature asigna productor, consumidor y evidencia a
cada paso. La aprobación de política/alcance del consumidor pertenece a su
dueño; el mandato del epic de CDAD no autoriza su implementación ni producción.

## 4. 005-009: delegación interoperable, primer adaptador OpenCode

### Contrato mínimo

Un agente autorizado invoca un adaptador del CLI destino con proyecto, paquete
canónico, rol y configuración de ejecución. Obtiene entrega final durable,
identidad de intento/sesión cuando exista y causa de terminación. El responsable
del ciclo recibe el resultado, hace re-entry y decide el gate.

Hay **un adaptador por destino**, no un script por pareja de herramientas.
Rol CDAD, CLI y modelo son decisiones independientes. Claude, OpenCode, Codex y
Pi son participantes posibles del diseño; no declarar sus adaptadores listos
sin evidencia. La dirección inversa y otros destinos son siguientes incrementos.

### Criterios que el architect debe convertir en postcondiciones

1. Reutiliza paquetes, observaciones de despacho, ledger, receipts y
   reconciliación existentes. El adaptador no crea otro state del ciclo ni
   reescribe las reglas del paquete en una plantilla paralela.
2. El proyecto es explícito e independiente del directorio del coordinador;
   el worker usa el rol, configuración y versión esperados. Comprobar el modo
   de carga soportado: no asumir que `mode: subagent` sirve como agente principal
   de un CLI, ni permitir fallback silencioso a un agente genérico.
3. El worker recibe contexto suficiente y acotado. Devuelve su texto final y
   evidencia referenciada, sin esperar mensajes de subagentes que no creó ni
   encadenar nuevas sesiones por iniciativa fuera de su mandato.
4. Distingue entrega completada, bloqueo del rol, error de transporte, timeout
   y cancelación. `rc=0` no aprueba un gate; timeout no prueba ausencia de cambios.
   Tras una interrupción se reconcilian los efectos antes de repetir.
5. Ofrece espera o finalización **realmente soportada**. No exigir callback,
   background o notificación si una espera fiable resuelve el recorrido. Si
   se usan, probarlos; no inventar señales de finalización ni sondear en bucle.
6. Configuración portable: selección de modelo, binarios, logs, servidores y
   tiempos viven en el nivel correcto. Registrar configurado/observado o
   desconocido, sin valores de este VPS en producto o contratos públicos.
7. Encargo pequeño real Claude → OpenCode → recepción CDAD, desde la instalación
   elegida para la aceptación. El coordinador y el worker usados deben ser
   reales; una prueba que solo llama al script desde un shell no demuestra
   por sí sola la orquestación desde Claude.

### Unidades de trabajo propuestas

- **T1: inventario y contrato.** Encontrar el dispatcher previo por referencias
  locales concretas, verificar CLI/capacidades y decidir qué reutilizar. Si no
  está disponible, registrar esa ausencia, sin una búsqueda global interminable.
  Mantener el contrato mínimo y ubicar cada dato en los records existentes.
- **T2: adaptador OpenCode.** Transporte, carga de rol y resultado; RED/GREEN
  focales con pruebas deterministas de interfaz y de fallos materiales. No
  construir un scheduler, instalación automática de CLI ni un sandbox.
- **T3: recorrido real y procedimiento.** Una delegación útil desde Claude,
  re-entry y un caso acotado de interrupción/recuperación que no repita efectos.
  Documentar cómo otro coordinador usa la misma interfaz. No necesita toda la
  matriz de CLI para cerrar esta primera entrega.

Reconciliar la prohibición heredada de spawn desde subagentes: conservarla
donde el runtime no soporte esa acción y distinguirla de delegación externa
autorizada. Primer aterrizaje coordinador→worker, sin recursión automática.
Una delegación no amplía autoridad ni permite al worker escribir el state.

## 5. Aceptación conjunta y continuación del consumidor

Después de entregar y desplegar las correcciones **entre ciclos**, una sesión
nueva puede iniciar el consumidor con una instrucción breve, conservar sus IDs
y organización, registrar lo faltante y realizar la primera delegación útil.

Antes del primer RED del consumidor deben estar verificadas su política, las
capacidades de los roles, los comandos de validación y la autorización de su
spec. El discovery documental permitido no necesita esperar toda la maquinaria.
Una prueba del adaptador no autoriza implementación ni cambios en producción.

El recorrido real aporta la aceptación pendiente R2 de 005-006 y la aceptación
de interoperabilidad cuando efectivamente ejerza ambas; reutilizar evidencia
equivalente, no repetir el trabajo para cada documento. Anonimizar la evidencia
publicable; datos de acceso y logs crudos quedan en el registro local.

## 6. Encargo de arranque y restricciones

1. Cargar CDAD instalado y esta propuesta; aplicar la enmienda al plan y
   sincronizar el state bajo aprobación real del dueño.
2. Abrir 005-008. El primer `prepare` legítimo debe republicar derivados desde
   la instalación global vigente. Comprobar la coherencia después de publicar;
   un `DRIFT` de derivados antiguos no se arregla editando hashes a mano ni
   repitiendo el mismo chequeo antes de la publicación.
3. Confirmar que la sesión usada para despachar carga los agentes renovados.
   La comprobación de archivos no recarga una sesión ni un servidor. Si hace
   falta una sesión nueva, dejar handoff y usarla; no reiniciar servidores
   compartidos que puedan interrumpir otros trabajos sin autorización.
4. Discovery y spec/plan de 005-008 por el architect aislado. Luego el ciclo
   CDAD con delegación real. La HITL vigente permite al orquestador las
   aprobaciones internas del epic; preservar autoridad reservada al dueño.
5. Tras cerrar 005-008, entregar la versión sucesora y las instrucciones de
   despliegue. **No** cambiar la instalación global durante un ciclo. Desplegar
   sigue siendo una acción del dueño; esta propuesta no da nueva autorización
   para HOME. 005-009 puede construirse con una versión estable anterior si
   es suficiente; su aceptación conjunta usa la sucesora que incluya 005-008.
6. Mantener checkpoints y handoffs por unidad cerrada: estado, decisiones,
   evidencia vigente, pendientes y siguiente acción. El trabajo debe poder
   continuar en otra sesión sin reconstruir conversaciones completas.

Gates: focales y módulos tocados durante el desarrollo; suite completa al
cierre. Ampliar una corrida antes solo por impacto concreto o invalidación de
evidencia y registrar el motivo. Una review formal al cierre de cada feature;
re-review focal de bloqueantes. Usabilidad y defectos materiales mandan; no
abrir una caza infinita de variantes opcionales ni tratar un deny legítimo del
arnés como incumplimiento del agente.

La deuda de `__pycache__` en `install.sh --check` queda registrada por separado:
es una señal del verificador, no un requisito del consumidor. Tratarla como
corrección focal si impide un gate real; no atribuir archivos derivados de
Python a cambios de versión ni borrar cachés para fabricar una garantía.

Sin push, cambios en HOME, publicación, instalaciones de dependencias o
operaciones de producción por autoridad implícita de este encargo. La ausencia
de una capacidad debe devolver diagnóstico y siguiente acción legítima.

Análisis ampliado: [findings de interoperabilidad](../../../findings/external-orchestration-readiness-2026-10-10.md).
