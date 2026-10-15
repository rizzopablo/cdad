# Discovery — 003-001-role-packets

2026-09-17. Architect en sesión nueva `architect_001`, modelo solicitado
`gpt-5.6-sol`; resultado recibido por el orquestador. Síntesis materializada
por Codex, con decisiones posteriores del HITL delegado señaladas abajo.

## Terreno verificado

- `skills/cdad-cycle/references/handoff-prompts.md` concentra templates de
  todos los roles. La delegación OpenCode remite a esa misma fuente.
- Los agentes contienen permisos y procedimiento propio, pero piden cargar
  el ciclo completo: hay contexto redundante e identidad de rol contradictoria.
- `skills/cdad-cycle/assets/state-template.json` es la fuente canónica del
  snapshot; no debe convertirse en un historial ilimitado.
- `scripts/cdad-models.sh` define perfiles. La autorización temporal pertenece
  a la ejecución, no al perfil global.
- `scripts/validate-subagents.sh` compara modelos por identificador exacto y
  depende de la instalación mediante `install.sh --check`.
- Tests existentes: validadores Bash en `tests/`, guard en `scripts/`, checks
  históricos por feature en `docs/specs/`. No hay workflow de CI; deuda ya
  registrada en `docs/projectbrief.md`.

## Aislamiento y baseline

El probe independiente `runtime_probe` confirmó que la herramienta nativa de
Codex permite sesión nueva y selección de modelo, pero no permisos de archivos
por hijo. Se usarán límites conductuales explícitos, declaraciones de lecturas
y comprobación de archivos modificados; no se afirma prevención de lecturas ni
auditoría completa de herramientas cuando el runtime no exponga esa evidencia.
El contrato vigente de `cdad-cycle`, sección de roles, admite ese modo.

Baseline de `tests/validate-consistency.sh`: **123 PASS / 1 FAIL**. El fallo
F011 procede del guard dependiente de copias instaladas con drift. No se ha
modificado la instalación. La corrección se verificará en un destino aislado.
El ejecutable local de OpenCode existe fuera de PATH; su API se releva aparte.

## Brainstorm resuelto por HITL delegado

1. Markdown por rol con diferencias pequeñas por subfase, sin duplicar el
   ciclo entero. Paquete renderizado de forma determinista y validable; una
   CLI pequeña en 001 está justificada para verificar su contrato observable.
2. Hash del contenido del spec obligatorio; commit opcional. Identidad de
   ejecución y paquete en el estado; medición en registros separados.
3. Distinguir modelo configurado y reportado. Desconocidos como `null`.
   No atribuir conteo de tokens, ahorro ni observación en runtime inexistentes.
4. Excepción ADR-010 ligada a autoridad, epic activo y ejecución identificada;
   un intento inválido no se oculta cayendo al perfil `basic`.
5. Destino de instalación configurable para pruebas si es necesario, manteniendo
   el destino habitual por defecto y sin modificar variables del sistema.
6. Recepción de artefactos, vigilancia y reanudación pertenecen a 002–004.

Gate discovery aprobado por Codex (agent-delegated) el 2026-09-17. Se conocen
los archivos y contratos afectados; el architect redacta ahora spec y plan.
