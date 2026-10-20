# 006-005 U6 — recorrido de aceptación real (PD-22)

Status: recorrido del orquestador bajo la delegación HITL amplia del owner (2026-10-19). Bitácora con comandos y evidencia: `docs/epics/epic-006-opencode-concurrency/execution.md`, sección «006-005 U6: recorrido real». Este documento resume el resultado contra los escenarios E1–E5 y la sonda V-11.

**Entorno observado (no se generaliza):**
- OpenCode v2.0.27 en modo server, con el store `session_v2` leído solo con `mode=ro`;
- proyectos **descartables**: worktrees del repo, uno dentro de otro repo git (layout anidado), con `.cdad` copiado;
- coordinador iniciado desde la carpeta contenedora (E1, E3, E4) o desde la raíz (E1b, V-11);
- modelos según la política vigente.
Nunca HOME ni el proyecto activo.

## Resultado por escenario

| Escenario | Resultado | Evidencia (resumen) |
|---|---|---|
| **E5** migrar + verificar | Cumple, tras U6-1 | `migrate` escribió la sección `opencode` en `runtimes.json`; repetirlo da rc≠0 sin pisar; `capabilities` informa `opencode v2.0.27`, `session_correlation: true` y las columnas observadas. |
| **E3** externo con solo paquete y `--runtime` | Cumple | sin credencial en el entorno del coordinador ⇒ `completed`; un registro I8 (el del módulo) con `model_reported` del store; parte `test-writer-role-report` y `materialize` rc=0 con bytes idénticos. Scribe: `role-report` materializado dentro de la carpeta de la spec; hacia el Memory Bank ⇒ rechazo nombrando la raíz permitida. |
| **E2** auxiliar con la herramienta del rol + test real | Cumple en las dos vías tras U6-7 (aceptación A1b/A3) | **antes del fix**, con la palanca `write: ask` vigente: la externa escribía, pero sin barrera por ruta efectiva (P1); la nativa no interactiva rechazaba todo (E1b). **Con los agentes de HEAD** (instalación temporal desde el repo, derivados publicados desde ella): **A1b** externa ⇒ `docs/` «Permission denied: edit», auxiliar en `.cdad/tmp` y `tests/` escritos; **A3** nativa desde la raíz ⇒ el rol escribió el auxiliar (V-14) y su test con su herramienta, el test pasa, commit solo de `tests/`, correlación verificada por las tres llaves. Desde la carpeta de afuera rige O-2 (límite declarado). `scope_validation` queda `unknown` en las dos vías (U6-2, deuda). |
| **E1** nativo (`subagent` + `record`) | Cumple, tras U6-3 y U6-4 | desde la carpeta de afuera ⇒ **verificado** por (parent, moment), proyecto no evaluable (ancestro); desde la raíz ⇒ verificado por (parent, moment, project). Sesión del registro = la del hijo real; `model_reported` del store, con la forma de la vía externa tras U6-6; entrega recibida, un registro por despacho. |
| **E4** intento que no vuelve | Cumple en la vía externa, tras U6-5 | SIGKILL del coordinador con el cliente vivo ⇒ registro provisional `write-ahead:` con la sesión; `reconcile` ⇒ `dispatched-unknown` (no autoriza repetir); re-despacho ⇒ `blocked` sin segundo cliente; `disposition` ⇒ `failed`; `validate-state` VALID; el siguiente `prepare` procede. El huérfano commiteó tarde: el efecto queda visible en git y su salida en el store es deuda (D-U65-5). En la vía nativa no hay write-ahead por construcción: límite declarado D-U65-4, con salida procedimental. |
| **V-11** `stack: odoo` de punta a punta | Cumple | `REQUEST.json.agent` = `cdad-test-writer-odoo`; despacho externo real ⇒ `session_v2.agent` = `cdad-test-writer-odoo`, `idle_outcome` `succeeded`, un registro I8 final y la entrega recibida. |

## Hallazgos del recorrido

| Id | Clase | Estado |
|---|---|---|
| U6-1 | `capabilities` no pasaba la sección al módulo | corregido (`ed64092`/`caaab97`) |
| U6-2 | ningún productor de `observed_changes`, así que `scope_validation` siempre es `unknown` | deuda declarada, preexistente y transversal |
| U6-3 | la llave proyecto rechazaba al coordinador iniciado desde la carpeta contenedora | corregido: ancestro no evaluable (`e7c39a5`) |
| U6-4 | momento en ms no evaluable; selección arbitraria del hijo | corregido (`8fe0d8c`/`b06bd2f`) |
| U6-5 | registro externo solo al terminar: una caída dejaba un callejón sin salida | enmienda write-ahead (`u6-5-decision.md`, dos reviews; `a0d96b5`/`569682d`/`471db74`) |
| U6-6 | forma de `model_reported` distinta entre vías | corregido (`12c29a7`/`ef88817`) |
| U6-7 | la palanca `write: ask` es evaluada por v2.0.27 y anula el mapa `edit`: la externa con `--auto` escribía fuera de alcance; la nativa no interactiva rechazaba todo | corregido en el generador (RED `8506674`, GREEN `028cd79`). Aceptación real con instalación temporal de HEAD: **A1b** (test-writer externo: deny y allow vigentes), **A2** (reviewer: toda escritura denegada), **A3** (E2 nativo). **La copia instalada en HOME sigue con la palanca hasta el despliegue que ordene el owner** |
| U6-7b | los derivados de `prepare` se construyen desde la copia instalada y heredan su palanca, así que una instalación vieja anula el mapa derivado | RED/GREEN en curso (defensa en profundidad: protege los proyectos aunque HOME no se haya redesplegado) |

## Límites y deuda declarados

- **Transporte del paquete en la vía nativa:** la línea JSON de cabecera de `PACKET.md` mide más de 2000 caracteres (2378 en el recorrido). La herramienta de lectura del runtime la trunca, y un orquestador que copia el paquete leyéndolo puede no lograr bytes idénticos: en el recorrido, uno se negó a despachar en lugar de alterar el paquete. La ruta documentada, `cdad_packet.py render` con su stdout pasado sin cambios, despachó bien (A3). Queda como observación para la guía del orquestador nativo.

- **O-2:** con el coordinador fuera de la raíz, el runtime aplica la copia global de los agentes, cuyos mapas son relativos a otra carpeta. La vía nativa recomendada inicia el coordinador en la raíz del proyecto.
- **D-U65-4:** sin write-ahead nativo; si el coordinador muere antes de `record`, el siguiente lo ejecuta con `--parent`/`--since`.
- **D-U65-5:** recuperar desde el store la salida de un huérfano como entrega tardía.
- **U6-2:** manifiesto de cambios observados.
- **Enmiendas al texto de la spec aprobada:** la fila E4 de §3.1, §9 (D-U65-4), la llave proyecto de tres valores (U6-3) y la selección y el momento (U6-4). Se aplican al cierre de la feature con re-pin declarado.
