# Decisiones del dueño — 004-002 (2026-09-29)

Decididas por Pablo en la sesión de orquestación (Claude), sobre
`architect-draft-001.md` y `spec-gate-claude-001.md`.

| # | Decisión | Resolución |
|---|---|---|
| D1 | Ruta y contenido de la política | `docs/cdad-policy.json`, versionada. Contiene solo `schema_version`, `path_policy` (clasificación de archivos) y `temporary_roots`. Sin modelos (siguen en `cdad-models.sh`), sin aprobaciones o autoridad, sin reglas de bash. Ningún rol la edita: cambiarla es una decisión del dueño (invariante O1 del gate). |
| D2 | Compatibilidad | **Solo hacia adelante.** Nada existente se migra ni se reescribe. Los 8 proyectos por camino legacy siguen igual y adoptan la política al iniciar una feature nueva. En este repo, los contextos y paquetes v1 quedan como evidencia histórica, validada por la versión de la herramienta que conserva git. La ejecución nueva se crea con el bootstrap v2 cuando aterrice. Hasta entonces 004-002 se construye con el contexto actual, con un único punto de corte definido en el plan. Se elimina `--migrate-execution`. Los tests con fixtures v1 se pasan al esquema nuevo o se retiran con trazabilidad. |
| D3 | Registro por despacho | Registro durable por **intento** de despacho, ligado a paquete y ejecución; los datos desconocidos van como `null`. |
| D4 | Architect standalone | Conserva el camino legacy (8 proyectos lo usan); bootstrap por paquetes para los roles con spec aprobada, sin epic ficticio. |
| D5 | Aplicación de la política por runtime | Generar agentes de OpenCode dentro del proyecto (`.opencode/agents/`) desde la política (spike: el agente de proyecto reemplaza al global y se aplica), y que el guard de Claude Code lea la política al ejecutarse. |
| D6 | Recorrido real (PD-13) | La propia ejecución de 004-002 por paquetes. |
