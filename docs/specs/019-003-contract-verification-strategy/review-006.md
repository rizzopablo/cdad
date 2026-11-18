# Revisión independiente — 019-003

**Resultado: un bloqueo de entrega pendiente.** La revisión no constituye aprobación. La candidata examinada es `73b44e62`, contra la base `0b11b5fb` y la especificación aprobada.

## Hallazgo

### El instalador entrega una versión anterior del agente orchestrator

**Required — Verdict: BLOCKING · Bucket: h**  
**PC afectada:** PC-6; evidencia de PC-5.  
**Ubicación:** `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`, `build/staging/agents/` e `install.sh:92-95`.

La instalación aislada terminó con código `0`, pero la comparación de los 14 agentes modificados mostró que **ambas variantes instaladas de `cdad-orchestrator.md` difieren de la candidata**. Las otras 12 coincidieron.

La causa observable es que el instalador toma los agentes exclusivamente de `build/staging`, y las dos copias de orchestrator allí no coinciden con los agentes candidatos. Por ejemplo, staging todavía dice que cada postcondición se vincula a “at least one test”, mientras que la candidata la vincula al método seleccionado, incluida la revisión contextual para partes semánticas.

**Consecuencia:** una instalación puede terminar correctamente y entregar al orchestrator una instrucción incompatible con la ruta semántica comprometida. Los controles verdes de generación y la presencia de agentes no demuestran que esta entrega concreta contenga esos bytes candidatos.

**Cierre verificable:** regenerar la entrega de staging desde las fuentes candidatas conforme al procedimiento del proyecto y repetir, en una raíz aislada, la comparación de ambas variantes instaladas de orchestrator con sus candidatas. Registrar comandos, salidas y códigos de retorno. No hace falta desplegar sobre la instalación real.

## Resultado por postcondición

- **PC-1 y PC-2:** en la guía y plantilla examinadas se declara la estrategia por promesa y la revisión de suficiencia o exención registrada. Sin nuevo defecto identificado en esas superficies.
- **PC-3:** los dos conflictos concretos de `review-005` están corregidos en la guía de especificación y el handoff examinado: distinguen comportamiento ejecutable, fidelidad semántica y compromisos mixtos.
- **PC-4:** no identifiqué en las instrucciones examinadas un debilitamiento adicional de la protección de criterios aprobados.
- **PC-5:** la evidencia ahora distingue resultados satisfactorios y fallidos; no obstante, la evidencia de entrega revela el bloqueo anterior.
- **PC-6:** **no acreditada** por la discrepancia efectiva entre candidata y agentes instalados desde staging.

La preservación física de `tests/` y de los directorios de especificación 019-001 y 019-002 se verificó contra la base: `git diff --quiet …` devolvió `0`. Esto no demuestra por sí solo toda la fidelidad semántica ni sustituye las obligaciones separadas de 019-002.

## Evidencia y límites

- **Intake:** `validate-request` y `validate-packet` terminaron sin error; `render --route C` reprodujo la identificación recibida.
- **Tests primero:** examiné `test-audit.md` y el test de instalación aislada. El log atribuible de la selección indica `75 passed`, código `0`; no repetí esa selección.
- **Generación independiente:** ejecuté `scripts/cdad-generate.py` para `opencode/auto`, `opencode/odoo` y `claude-code/auto` en directorios temporales. Las salidas comparadas con los agentes versionados no presentaron diferencias.
- **Instalación independiente:** ejecuté `bash install.sh` con `CDAD_INSTALL_ROOT` temporal y `CDAD_SKILL_EXTRA_DIRS=""`. Terminó con código `0`. Los 16 archivos de skills modificados coincidieron con la candidata en los tres destinos comprobados; la comparación de agentes produjo las dos diferencias descritas en el hallazgo.
- **Comprobaciones de la instalación real:** los logs registran `install.sh --check` y `validate-subagents.sh` con código `1`. No se presentan como verdes. No está establecida su baseline; esa incertidumbre no es necesaria para demostrar la discrepancia aislada de staging.
- **Diff:** instrucciones, agentes generados y documentación; no observé cambios de addon que justifiquen exigir una batería de instalación limpia Odoo.
- **Suite completa:** no realizada; excluida por el encargo.
- **Archivos modificados por esta revisión:** ninguno. **Commit de esta revisión:** ninguno. `docs/.cdad-state.json` ya aparecía modificado al inicio.

## Abstentions

- No determino qué parte del drift de la instalación real es anterior a la candidata.
- No acredito un recorrido integral con agentes reales ni comportamiento fuera de las superficies y comparaciones descritas.