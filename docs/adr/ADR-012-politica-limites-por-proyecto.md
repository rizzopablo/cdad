# ADR-012 — Política de límites por proyecto, paquetes v2 y aplicación por runtime

## Estado
Propuesto (2026-10-02)

## Contexto
La clasificación de archivos, los scopes y los permisos vivían dispersos entre
agentes, instalador y guard. 004-002 introduce una política de proyecto única y
una ejecución durable con identidad separada de las observaciones de runtime.

## Decisión
1. `docs/cdad-policy.json` es la única política editable (schema_version,
   path_policy, temporary_roots); ningún rol la edita.
2. Los paquetes v2 residen en `.cdad/packets/` + `.cdad/executions/<id>/`; la
   identidad lógica es independiente de runtime/modelo/sesión.
3. La política se aplica por runtime: agentes derivados de proyecto en OpenCode
   y guard dinámico en Claude Code.
4. Los límites mecánicos se aplican solo cuando son obvios y no restrictivos
   (`private_paths`); el resto es instrucción + auditoría del orquestador.

## Consecuencias
- (+) Una superficie auditable, con hash y reconciliación explícita del dueño.
- (+) Adopción hacia adelante sin migrar v1.
- (−) Cada cambio de política requiere reconciliación; barreras no uniformes
  entre runtimes; R5 (~252 ms/llamada) aceptado.

## Confianza
Media — la decisión está verificada en vivo para `read` (OpenCode) y para las
herramientas mediadas (Claude Code); `edit`/`write`/`grep`/`glob` y bash no
tienen barrera mecánica y dependen de instrucción + auditoría.
