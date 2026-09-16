---
epic_id: epic-003-context-efficiency
epic_name: Eficiencia de contexto y ejecución
created_at: 2026-09-16
status: draft
---

# Epic 003: eficiencia de contexto y ejecución

## Resumen y estado

Reducir, en orden de prioridad, tiempo, contexto necesario y costo por feature
aceptada conservando contratos, aislamiento
de roles, aprobaciones y evidencia. Usar `cdad-epic` para coordinar las entregas y
`cdad-cycle` para especificar, probar y revisar cada una.

Borrador de planificación basado en el [análisis](../../../findings/context-token-efficiency-2026-09-16.md).
Entorno informado: VPS, principalmente OpenCode y también Claude. Discovery
continúa con análisis retrospectivo de sesiones reales; acceso SSH y registros
ya verificados. El [primer relevamiento](../../../findings/session-efficiency-2026-09-16.md)
identifica bucles sin progreso y divergencia de versiones. No cierra E1 ni E2,
no activa el epic ni autoriza implementación. La delegación HITL registrada para
epic-002 no se extiende a este trabajo.

## Base verificada

- Repositorio local y remoto `translation-en`: `eb3a511181c3d76d0306dd149176b90ebe8b617c`.
- `main` remoto: `2af4a3b8bea8cd1d9b9630e79a8d05e46f5d1801`; incluido en la historia de esta rama.
- Verificación remota realizada el 2026-09-16. Las carpetas instaladas de
  `cdad-cycle` y `cdad-epic` coinciden íntegramente con las del repositorio.
- El informe ampliado tiene cambios locales sin commit; es la entrada de este
  plan y se conserva sin modificar. Su nota de transferencia es histórica.
- Persisten la exclusión contradictoria de properties en el agente orquestador,
  la recarga por turno y la tensión entre tarea atómica y paquete ortogonal.
- No hay epic activo; `cdad-010-opencode-permissions` figura cerrado en estado y
  Memory Bank. Este trabajo no vuelve a certificar los gates de esa feature.

## Alcance propuesto

Incluye línea base reproducible, instrucciones por rol consistentes, handoffs
acotados, continuidad automática/manual, recuperación tras compactación,
memoria activa separada del historial y presupuesto de ejecución con evidencia
vigente. Las comprobaciones mecánicas pequeñas se agregan donde las necesite
cada entrega; la interpretación semántica sigue siendo responsabilidad del rol.

Se difieren cambios de modelo/proveedor, migración local, paquetes de
postcondiciones acopladas, paralelismo adicional y un motor general en Go.
La compatibilidad existente de roles, stacks y runtimes debe conservarse;
la medición inicial se concentra en un entorno elegido por el usuario.

## Descomposición propuesta

| Orden | Feature | Entrega verificable | Dependencias |
|---|---|---|---|
| 1 | `003-001-baseline` | Análisis de sesiones reales y protocolo reproducible de tiempos, contexto, consumo, reintentos y calidad; captura prospectiva solo para datos faltantes. | Acceso y selección de casos del VPS |
| 2 | `003-002-role-contracts` | Fuentes canónicas y proyecciones por rol; resolver contradicciones de identidad, properties y agrupación ortogonal conservando restricciones. | 001 |
| 3 | `003-003-context-handoffs` | Paquetes por rol/subfase con referencias versionadas, dependencias críticas, retorno verificable y recuperación tras compactación. | 002 |
| 4 | `003-004-execution-continuity` | Selección explícita de modo automático/manual; re-entry automático autorizado y persistencia exacta de artefactos sin autoaprobación. | 003 |
| 5 | `003-005-memory-checkpoints` | Estado vigente separado del historial; reconstrucción de la próxima tarea desde archivos en una sesión nueva. | 003 |
| 6 | `003-006-evidence-budget` | Registro e invalidación conservadora de evidencia y presupuesto por propósito/stack, con resumen verificable y log íntegro. | 001, 002, 003 |

Orden inicial secuencial para atribuir efectos. Las dependencias permiten
reordenar 004–006; ejecutar en paralelo exige justificar beneficio y ausencia
de conflictos. Las specs detalladas se redactan al abrir cada ciclo.

## Contratos compartidos mínimos

- **Medición:** caso, revisión, runtime/perfil/modelos, variante, métricas de
  todos los roles y referencia a trazas. Dato no disponible se marca como tal;
  bytes no se presentan como tokens ni consumo parcial como costo total.
- **Paquete:** rol/subfase, objetivo/postcondiciones, versión del spec,
  lecturas autorizadas, dependencias críticas, alcance de edición y evidencia
  previa. Ampliación de contexto dentro de los permisos del rol.
- **Retorno:** resultado, artefactos y sus identidades, evidencia, bloqueos y
  próxima acción. Review conserva texto y procedencia de los hallazgos.
- **Checkpoint:** tarea vigente, decisiones/aprobaciones y alcance, pendientes,
  versiones y referencias suficientes para reconstruir el siguiente paquete.
- **Evidencia:** identidad de código/tests ejecutados, cambios sin commit,
  dependencias/configuración/fixtures/entorno relevantes, comando, selección,
  semilla, salida, conteos y log. Equivalencia incierta impide reutilización.

Estos campos son compromisos entre entregas; formato y almacenamiento se
resuelven en la primera spec que los produce, con sus consumidores identificados.

## Criterios de aceptación del epic

- Las seis features cierran su ciclo con evidencia y Memory Bank aprobado.
- Comparación antes/después sobre casos equivalentes, con modelos y condiciones
  controlados, incluye retrabajo y separa espera humana, agentes y tests.
  Umbrales numéricos se acuerdan tras 001 y antes del piloto optimizado; sin
  ellos este criterio permanece abierto. No se prometen ahorros de antemano.
- Integración: preparar paquete, ejecutar rol, persistir retorno, validar gate
  y reconstruir la siguiente tarea en sesión nueva; probar los modos manual y
  automático, incluyendo una aprobación estratégica pendiente.
- En evaluación aislada se detectan y bloquean: edición de tests por implementer,
  evidencia obsoleta y suite vacía exitosa; una auditoría independiente detecta
  un test que no verifica su postcondición.
- Restricciones críticas disponibles después de compactación/reinicio; ningún
  paquete del test-writer filtra implementación. Diversidad de modelos conforme
  a la política vigente y capacidades verificadas del entorno ejecutor.
- Suite completa e integración verdes; CI verde si existe. Si falta CI, resolver
  explícitamente el gate de integración del epic antes de cerrarlo, dado que
  `cdad-epic` lo exige; no trasladar silenciosamente la excepción de feature.

## Información necesaria y riesgos

1. **Entorno confirmado:** VPS accesible por SSH; OpenCode 1.18.30. Se relevaron
   85 sesiones del proyecto indicado. Modelo observado: `glm-5.3-flash` vía
   `mofgw` y OpenRouter. Checkout CDAD encontrado: `4aa2b02`, del 30 de agosto;
   skill instalada diferente de la local. Fijar versión efectiva antes del piloto.
2. **Casos disponibles:** el usuario informa muchas ejecuciones reales.
   Inventariarlas antes de seleccionar una muestra con casos rápidos, lentos,
   reintentos y tests costosos. Separar resultados por runtime/modelo/revisión
   y evitar atribuir causalidad a diferencias entre proyectos heterogéneos.
3. **Prioridad confirmada:** tiempo → contexto → costo, manteniendo calidad y
   garantías. Medirlos por separado: paralelismo, caché y reintentos pueden
   moverlos en direcciones distintas.

## Relevamiento previo al piloto

Primero inspeccionar registros existentes sin modificar proyectos ni reanudar
sesiones. Inventariar versiones, almacenamiento y sesiones padre/hijas; enlazar
features y gates con evidencia cuando exista. Empezar por metadatos y consultar
contenido de las sesiones seleccionadas cuando haga falta explicar un hallazgo.

Medir tiempo transcurrido y, cuando los eventos permitan distinguirlos, espera
humana, inferencia, herramientas/tests y coordinación. No sumar duraciones
solapadas como tiempo total ni clasificar todo intervalo inactivo como espera
humana. Distinguir tokens acumulados del contexto máximo; conservar desconocidos
los valores que el registro no permita reconstruir.

Extraer relecturas, cargas repetidas, transferencias, compactaciones, ciclos de
corrección y ejecuciones de suites, con referencias a sesiones/eventos. Generar
en un directorio temporal privado un inventario, métricas y hallazgos trazables;
incorporar al repositorio únicamente resultados depurados de datos sensibles.

Si conviene procesar junto a los datos, usar extracción determinista y, como
opción propuesta por el usuario, OpenCode o zot para un análisis acotado con
salida a archivos temporales. Verificar primero qué herramienta es zot y qué
interfaz/versiones están disponibles. Sus conclusiones deben citar eventos y
contrastarse con las trazas; registrar el costo del análisis separado del caso.

El resultado del relevamiento puede reducir o reordenar las seis entregas antes
de aprobar el plan. Una comparación histórica sirve para localizar problemas;
demostrar ahorro requiere después casos comparables bajo condiciones controladas.

### Hallazgos del 2026-09-16 que requieren ajustar la descomposición

Priorizar especificación de detección/recuperación de bucles sin progreso:
una review repitió 1.194 veces el mismo comando y salida en 50,9 minutos y fue
abortada. Evaluar si merece entrega propia o amplía `003-004` antes de aprobar
el plan; la tabla anterior aún es provisional. No confundirlo con polling útil.

La raíz del caso principal llega a 904.206 tokens de entrada reportados por
llamada, incluida caché: da fundamento a checkpoints. En cambio, las 65 cargas
explícitas de `cdad-cycle` ocurren en 65 sesiones distintas: no se confirmó la
recarga por turno. Revisar permisos y diversidad de modelos antes de comparar
variantes; los incidentes históricos no prueban fallos de la versión actual.

Riesgos: confundir ahorro de texto con ahorro real; trasladar costo a reintentos;
perder dependencias por recortar paquetes; cambios de instrucciones durante su
propia evaluación. Mitigación: revisión fijada por corrida, comparación incremental,
casos negativos y vuelta a la versión previa si se debilitan controles.

## Responsables

- Aprobador del plan y specs: Pablo, salvo delegación explícita para este epic.
- Operador del piloto: a confirmar junto con el entorno.
- Coordinación: orquestador CDAD; ejecución y evaluación en roles separados.

---

Status: Pending approval
