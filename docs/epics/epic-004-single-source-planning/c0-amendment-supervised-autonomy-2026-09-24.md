# Enmienda vigente de C0 — autonomía supervisada

Fecha: 2026-09-24. Responsable de esta actualización documental: GPT, a pedido
del usuario. Leer este documento antes del informe histórico del architect.

La dirección metodológica quedó decidida por el usuario: instrucciones claras,
libertad operativa razonable y supervisión del orquestador. Está formalizada en
[ADR-011](../../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md).
No hace falta volver a pedir que elija entre control exhaustivo y autonomía.
Las specs, la activación de 004 y la implementación siguen pendientes; no hay
modificación de permisos instalados en esta actualización.

## Qué cambia en el análisis de CDAD

El principio central sigue siendo que quien construye no sea su único
verificador. Spec, contratos, TDD, sesiones separadas, review y memoria siguen
vigentes. Cambia el medio de control: cada rol debe disponer de capacidades
suficientes para trabajar, con pocas restricciones justificadas por efectos.
El orquestador verifica al recibir resultados y decide proporcionalmente ante
incidentes; no necesita controlar cada herramienta.

Del aporte de Claude se adopta simplificar antes de generar y medir fricción
y desvíos. Se corrigen tres simplificaciones: sesión/paquete/worktree no son
sandbox; una lectura puede ser observable pero no se puede deshacer del
contexto; un incumplimiento no obliga a repetir todo el trabajo. No adoptamos
como evidencia los "27 commits", una tasa global de daño o incidentes
"de hoy" no comprobados. La evidencia local del conteo sí está documentada.

## Resolución documental de R1–R3 y D1–D10

| Punto | Decisión para el siguiente encargo |
|---|---|
| R1 / D9 | Mantener 003 activo solo durante preparación. Al activar 004, guardar snapshot/handoff de 003 y cambiar el único state activo a 004 con autoridad propia. Al retomar, reconciliar progreso e historia, sin restauración ciega ni nuevo motor multi-epic. |
| R2 / D2 | Baseline corregida: 22 agentes, 2.697 líneas (1.572 OC + 1.125 CC), 140.161 bytes de archivos completos. No son tokens. Eliminar el techo de líneas como gate; comprobar una fuente por regla, propagación, capacidad operativa y mantenimiento comprensible. |
| R3 / runtime | Separar observación Codex, ayuda/tipos OpenCode, smoke histórico y runtime actual. No inferir falta de sandbox OpenCode del informe Codex. Registrar versiones efectivas; el metadato de la sesión C0 es 1.18.16, no certifica el binario actual. |
| D1 | Markdown + Python stdlib sigue siendo candidato simple. JSON también dispone de parser stdlib y permite prompts autocontenidos; elegir por claridad de autoría. La spec fija paths/secciones concretos. |
| D3 | Medición estática inicial como preparación, con comandos y suma verificable. Incluir agente, paquete y lecturas pertinentes; no tratar el bloque estático solo como contexto total. |
| D4 | Manifest/dry-run: propiedad, hashes, conflictos de modificaciones locales y recuperación explícitos. No borrar archivos modificados solo porque alguna vez fueron instalados por CDAD. |
| D5 | Editar fuentes; regenerar salidas marcadas con origen. No prohibir editar legítimas fuentes de agentes. |
| D6 | Default en destinos runtime reales. Migrar fixtures. Opt-in público solo si se justifica por compatibilidad/consumidor, no para perpetuar el fixture. |
| D7 | Reemplazar assertions de mecanismo antiguo por comprobaciones de garantías/capacidades en el mismo cambio coherente; no congelar la política vieja por tests de frases. |
| D8 | Revisión de borradores explícita en 004-003; handoff legacy identificado mientras se construye esa capacidad, sin falsificar aprobaciones. |
| D10 | Tres features, tareas internas acotadas. Sin cuarto ciclo para esta política y sin ceremonia RED/GREEN para una medición documental. |
| D11 nueva | ADR-011 gobierna el diseño de permisos: capacidades + instrucciones + supervisión; generar después de simplificar. |

Esta enmienda incorpora las correcciones de revisión al plan de trabajo;
no reescribe el informe original ni declara aprobado retroactivamente C0.
La siguiente revisión debe ser focal sobre la spec/plan de 004-001 y sus
decisiones técnicas pendientes, no otra discusión desde cero del enfoque.

## Mapa de impacto y dueño de cada cambio

| Superficie | Cambio necesario | Entrega |
|---|---|---|
| `CDAD_metodologia.md`, README, systemPatterns, ADR-009/011 | Principio actualizado y distinción entre decisión y runtime desplegado. | Actualización documental presente; ejemplos operativos restantes se reconcilian en 004. |
| `agents/cdad-*.md`, `agents/claude-code/cdad-*.md` | Instrucciones comprensibles, capacidades efectivas, read-only del producto y permisos proporcionales por runtime/dominio. | 004-001 |
| `scripts/cdad-bash-allowlist.sh`, `scripts/claude-code-path-guard.sh`, `install.sh` | Revisar necesidad de cada mecanismo; simplificar/reutilizar antes de generar. No conservar listas cerradas por inercia ni abrir configuración global. | 004-001 |
| `tests/validate-consistency.sh`, `tests/validate-odoo-specialization.sh`, `scripts/validate-subagents.sh`, tests Python | Probar tareas legítimas, fronteras retenidas, wrappers/salidas y producto instalado. Migrar asserts de detalle con trazabilidad al requisito nuevo. | 004-001/002 |
| path policy, execution context, `cdad_packet.py` y schemas | Scopes, scratch/logs, autoridad e identidad estables; declarar capacidad/limitación efectiva antes del despacho. | 004-002 |
| Skills cycle/epic, paquetes, handoffs, re-entry y anti-patterns | Encargo positivo con razones, decisiones delegadas, evidencia y tratamiento proporcional. No replicar ADR completo en cada prompt. | 004-001 composición; 004-003 procedimiento completo |
| Resultado/receipt/evidencia | Conservar hechos y referencias, separar recepción de juicio sobre cumplimiento; registrar incidente sin regenerar reporte. | 003-002 |
| Pre-flight/watchdog/progreso | Distinguir tarea difícil, falta de capacidad, política defectuosa e incumplimiento. Medir fricción y riesgo, sin cambio automático de permisos. | 003-003 |
| Checkpoint/re-entry prolongado | Restaurar decisiones, autoridad, versión de política, incidentes y presupuestos sin repetir aprobaciones. | 003-004 |

## Encargo inmediato para GLM — preparación de 004-001

**Objetivo:** entregar una spec y un plan ejecutables que simplifiquen la
política antes de convertir los agentes en salidas generadas.

**Entradas:** esta enmienda, ADR-011, plan de epic actualizado, inventario
R1–R12 existente y finding de fricción. Consultar fuentes del mapa solo según
necesidad; no volver a leer toda la historia ni cargar el ADR a cada ejecutor.

**Entregable acotado:**

- [ ] Tabla por rol: resultado, decisiones autónomas, capacidades necesarias,
  invariantes con motivo y evidencia que comprobará el orquestador.
- [ ] Para los controles actuales: conservar/simplificar/retirar con razón.
  Las pocas barreras retenidas tienen efecto protegido y garantía comprobable.
- [ ] Simplificación OpenCode como primera aplicación y coherencia Claude/Odoo;
  no una corrección aislada de `wc` ni un framework de seguridad.
- [ ] Interfaces/fuentes y tareas de 004-001, incluyendo la prueba de capacidad
  de medir/calcular/ejecutar lo autorizado desde producto instalado.
- [ ] Matriz breve: trabajo permitido termina; efecto fuera de alcance se trata
  según contrato; error de entorno vuelve al orquestador sin bucle; evidencia
  conserva exactitud. Fronteras de roles y limitaciones se describen honestamente.
- [ ] Procedimiento concreto para activar 004 y luego retomar 003 conservando
  la historia y sin delegaciones heredadas. No ejecutarlo aún.

**Salida:** delta y spec/plan para revisión GPT o Claude. Conservar trabajo
válido del informe; resolver VERIFY relevantes durante este discovery.
El autor propone opciones recomendadas y costos; pregunta solo por información
o autoridad que realmente falte. Trabajo documental/medición independiente
puede continuar dentro del alcance ya autorizado.

**Antes de construir:** versión durable de los documentos revisados, spec con
postcondiciones aprobada y autoridad de ejecución registrada. El usuario ya
autorizó este ajuste metodológico; no convertir cada tarea en otra aprobación.
La implementación permanece a cargo de GLM; GPT/Claude hacen análisis/review.

## Progresión prevista de 004-001

Preparación/medición e inventario ya iniciado → contrato de capacidades y
fuentes → simplificación mínima de adaptadores y comprobación de trabajo
legítimo → generación de artefactos → instalación/integración. Las tareas
pueden integrarse si resulta más simple; evitar dos políticas editables en
paralelo o copiar nuevas instrucciones manualmente a los 22 agentes.

El resultado del primer recorrido real alimenta 003-003. No se exige ahorro
porcentual, cero incidentes ni repetir un desarrollo para comparar. Toda
desviación material necesita resolución; un falso rechazo también es un
defecto del producto, no un éxito del guard.
