# Ideas transferibles de Superlite para CDAD

**Objeto de estudio:** copia local de Superlite, versión 1.1.0, tag `v1.1.0`, commit `eea16ee079393feafc6b2ed2da6b6938b6fef503` (2026-10-18; árbol limpio al inspeccionarlo). No se ejecutaron scripts, pruebas ni instalaciones. Las cifras y capacidades que pueden cambiar se consignan como afirmaciones documentadas, no como resultados verificados en esta revisión.

Este análisis alimenta la [propuesta de dos futuros epics](../docs/planning/superlite-followups-2026-10-19/plan.md), contrastada con el [inventario de CDAD](../docs/planning/superlite-followups-2026-10-19/inventory.md). Los documentos están preparados; los epics no están activados.

**Ampliación necesaria, 2026-10-21 (dirección del dueño):** consumir junto con
este análisis el [caso S-SYS-01 y su evidencia histórica](system-capability-planning-evidence-2026-10-21.md).
La continuación debe atender capacidades completas, dependencias operativas,
transferencia de aprendizaje y recorrido de uso. Los ejemplos contractuales y
las comprobaciones fake→real de Superlite son instrumentos parciales: su éxito
no acredita por sí solo identidades, configuración heredada, efectos ni uso del
sistema completo. El marco de planificación es **contratos, garantías y evidencia**,
sin equiparar cobertura de obligaciones con cobertura de código o cantidad de tests.
La relación y las condiciones de entrada quedan incorporadas en el plan enlazado;
esta ampliación no cambia la descripción histórica de Superlite ni activa epics.

## Epic 1: planificación e interfaces

**Separar contrato de dependencia de ejecución.** `skills/writing-plans/SKILL.md:31-35,58,74-78` pide firmas exactas en `Consumes`/`Produces`, y aristas solo cuando pruebas consumidoras ejecutan código productor. Los consumidores pueden avanzar con stubs y fakes. Para retornos estructurados, el productor ofrece ejemplos ejecutables, por ejemplo `parse("1+2") -> Binary("+", Num(1), Num(2))`; el fake reproduce esos ejemplos y las pruebas del productor los verifican. **Transferencia posible:** hacer los contratos de CDAD verificables y permitir trabajo paralelo cuando no hay dependencia de ejecución. **Condición/riesgo:** firmas y ejemplos deben ser inequívocos; el seam check posterior sigue siendo necesario para confirmar compatibilidad real.

**Estabilidad y congelación.** `lint --stable` divide tareas STABLE/FIX, despacha las estables y exige que las ya despachadas permanezcan idénticas; cambios se convierten en tareas posteriores (`skills/writing-plans/SKILL.md:14-16`; `skills/subagent-driven-development/SKILL.md:27-31`). **Transferencia posible:** hacer visible qué contratos ya consumen otros roles y protegerlos de cambios silenciosos. **Condición/riesgo:** congelar no acredita corrección; los cambios de interfaz o alcance deben volver al mecanismo de decisión de CDAD.

## Epic 2: ejecución supervisada proporcional

**Seam checks fake→real.** El implementer prueba cada productor consumido con un fake intercambiable; `SUPERLITE_REAL=1` repite las pruebas contra el productor (`agents/implementer.md:15-16`). `commit_task` inicia probes y seam checks cuando ambos lados del contrato están comprometidos (`skills/subagent-driven-development/SKILL.md:42-53`). **Transferencia posible:** automatizar la evidencia de integración en límites entre tareas. **Condición/riesgo:** los fakes deben proceder de ejemplos contractuales y cubrir los casos relevantes; pasar el seam no garantiza robustez general.

**Comandos que absorben coordinación.** `dispatch` ofrece tareas listas por tier; `commit_task` compromete archivos asignados y dispara verificaciones; `run_tests` guarda un resumen; `finish` e historial recogen resultados (`skills/subagent-driven-development/SKILL.md:46-53,86-98`; `docs/tools.md:17-24`). **Transferencia posible:** encapsular operaciones repetitivas con estado y evidencia legibles. **Condición/riesgo:** no convertir decisiones arquitectónicas o de aceptación de CDAD en automatismos opacos.

**Contexto de arranque y reparación.** El implementer recibe el plan común y luego su tarea, archivos, rulings y Review Focus (`agents/implementer.md:11,24-30`). Las rondas de reparación usan notas de hasta 1.500 caracteres con objetivo, spans, intentos fallidos, evidencia y próxima hipótesis (`skills/subagent-driven-development/fixing.md:16-31`). **Transferencia posible:** dar a cada rol solo contexto pertinente y preservar evidencia útil entre rondas. **Condición/riesgo:** notas incompletas pueden perpetuar diagnósticos erróneos; retener contexto proporcional no significa descartar la especificación o la historia necesaria.

## Límites: decisiones de no transferir tal cual

- **No juntar test-writer e implementer.** Superlite asigna al mismo implementer pruebas y código (`agents/implementer.md:11,15-16`). Para CDAD se conserva la independencia de roles.
- **No hacer que el reviewer corrija su propia revisión.** `package-reviewer` revisa y corrige hallazgos (`agents/package-reviewer.md:9,18`). Su flujo no reemplaza revisión independiente en CDAD.
- **No limitar automáticamente la revisión final a un packet cerrado.** `final-reviewer` lee el packet una vez y solo reporta findings (`agents/final-reviewer.md:9-24`). Ese mecanismo puede omitir evidencia que el packet no incluya.
- **No adoptar 80k como límite universal.** Aparece como tope fijo de asignación/contexto (`skills/subagent-driven-development/SKILL.md:49`; `skills/writing-plans/SKILL.md:79,121`); capacidades varían por runtime. Adaptar contexto a runtime y tarea es una línea de investigación, no una propiedad demostrada por ese umbral.
- **Modelos fuera de la metodología.** Los perfiles Superlite fijan tiers/modelos; OpenCode indica despachar el subagente genérico con el modelo del perfil (`agents/implementer.md:2-8`; `docs/README.opencode.md:41-43`). CDAD debe mantener metodología independiente de proveedor/modelo y documentar capacidades del runtime como adaptación.
- **No importar el rewrite de pruebas sin conservar su alcance.** `hooks/rewrite-test-runs:50-76` transforma pruebas reconocidas en `run_tests --full` en background; puede ampliar una petición focal a suite completa.
- **Presupuestos son avisos, no corte duro.** Se advierte al 70% y se frena trabajo opcional al exceder el tope; los bloqueos automáticos aparecen como propuestos (`skills/subagent-driven-development/metrics.md:34-40`). Métricas de coste/contexto son aproximaciones con límites documentados (`:42-52`).

## Benchmark: distinguir versiones y límites

`bench/report.md` es el informe inicial Superlite 0.1: una corrida por brazo (8,8 min frente a 34,4 min); documenta solapamiento de corridas, corrección del cálculo de coste y una suite que mide conformidad con spec, no robustez (`bench/report.md:1-4,34-49`). El `README.md:33-49` posterior atribuye al build actual una corrida de 16,1 min y 177/177 pruebas; incluye comparaciones de builds/versiones anteriores y señala menor puntuación en probes adicionales de robustez (4/7 frente a aproximadamente 5,7/7). El README advierte que son indicaciones, no prueba estadística, y que Superlite puede costar más. Las dos fuentes no deben mezclarse como una serie homogénea ni extrapolarse como ahorro esperado de CDAD; son evidencia contextual con tamaños de muestra y condiciones distintos.
