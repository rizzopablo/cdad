# Bloqueo previo al dispatch de Discovery

Fecha: 2026-10-29.

## Estado y evidencia

- Plan aprobado por Pablo y registrado en git: `644d5fe`.
- Unidad abierta: `010-001-documentary-contracts`.
- Contexto creado por `open-unit`: `exec-010-001-documentary-contracts-001`.
- Paquete preparado: `010-001-documentary-contracts-architect-discovery-001`.
- `validate-state`, `validate-request` y `validate-packet` finalizaron correctamente.
- El version check instalado informó `COHERENT` para project, agents, CLI y
  Claude Code después de la preparación canónica.

`open-unit` ya había creado un contexto sin usar: `prepare --new-execution`
rechazó crear un segundo contexto huérfano. Se siguió su recuperación explícita
preparando sobre el contexto abierto, sin esa opción. No hubo doble paquete.

## Bloqueo

Desde la raíz del repositorio, el comando:

```sh
python3 <skill-dir>/scripts/cdad_continuity.py begin --project-root . \
  --execution-context .cdad/executions/exec-010-001-documentary-contracts-001/execution.json \
  --update .cdad/executions/exec-010-001-documentary-contracts-001/discovery-begin.json --json
```

finalizó con código 1:

```text
cdad_continuity: the begin is refused: path_policy.documentation_files escapes project root: 'README.md'
```

La comprobación read-only posterior mostró que `README.md` es un archivo regular
y que `readlink -f README.md` resuelve al README de la raíz del mismo repositorio.
Esto no establece la causa del rechazo: queda pendiente diagnosticar cómo
continuity interpreta la raíz y la política en esta invocación.

## Disposición

No se ejecutó transporte, no hay worker ni intento registrado ni resultado que
recibir. El paquete permanece preparado. No se cambió la política, no se editó el
CLI ni se intentaron invocaciones equivalentes para eludir el rechazo. Antes del
dispatch debe diagnosticarse y resolverse este bloqueo y obtenerse un `begin`
válido seguido de `verify-begin`. No aprobar ninguna spec ni gate por este registro.
