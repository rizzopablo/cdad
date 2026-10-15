# Retoma en OpenCode: 004-002 (2026-10-01)

Desde este punto la orquestación pasa al agente `cdad-orchestrator` de OpenCode,
que delega en sus subagentes dentro del propio arnés. Claude interviene solo para
revisar entre ciclos (ver §5). Esta nota sustituye a `resume-2026-10-01.md`.

## 1. Estado al traspaso

- **T1–T6 cerradas**: registros PD-17 en `supervision-record.md` y suite de
  cierre de 284 passed en `28324af`.
- **El corte C está publicado** (`cut-c.md`). Contiene la política
  `docs/cdad-policy.json`, materializada por el dueño, y los defectos del
  producto W-1, W-1b y W-1c, ya corregidos. Los 69 paquetes v1 quedan
  congelados en `evidence/cut-c-v1-packets.sha256`.
- **T7 está en curso** y cada paquete es v2, con su despacho registrado en el
  ledger (tramo v2).
  - **red-019**: matriz integral PD-1..PD-13 (`7e7a3a9`).
  - **Verificación en vivo**: `t7-live-walk.md`. C1 queda verificado para
    `read` (§2–§4) y C2 en una sesión real de Claude Code (§5).
  - **W-2**: en OpenCode, `grep` y `glob` se evalúan contra el patrón de
    búsqueda y no contra la ruta (§3). Los mapas por ruta en esos permisos no
    protegen nada.
  - **red-020 (W-2 RED)**: cerrado. Commits `1bdcc90` y `9e148de` (enmiendas
    al oráculo, revisadas y aceptadas por el orquestador) y `f2bfc1e`
    (`tests/test_004_002_t7_w2.py`). El caso (a) está en RED en los tres
    layouts; (b) y (c) están en verde.
- En `docs/.cdad-state.json`, `active_packet` es red-020 con
  `status: completed`. El vínculo de ejecución es v2
  (`exec-004-002-project-execution-bootstrap-001`).

## 2. Próximos ciclos, en orden

1. **W-2 GREEN** (implementer). Objetivo:
   - Los agentes derivados por proyecto (I9) no emiten entradas por ruta en
     `grep` ni en `glob`. Los mapas de `read` y `edit` se conservan.
   - En la guía `skills/cdad-cycle/references/project-execution.md` (§7) se
     declara la limitación: en OpenCode las herramientas de búsqueda no tienen
     límite por ruta, igual que el bash permisivo. La única barrera viva por
     ruta es `read`.
   - Que pasen `test_004_002_t7_w2.py`, `t5_runtime`, `t5_reviewfix` y
     `004_001_t7_pd10`, y además la suite completa en primer plano.
   - Después: reinstalar la raíz aislada (§3), correr `prepare` y comprobar que
     `.opencode/agents/cdad-test-writer.md` ya no tiene entradas por ruta en
     `grep`/`glob`. Así se verifica en vivo que el derivado se regenera.
2. **Review del W-2** con un reviewer de otra familia que el implementer.
   Luego el review-fix si hace falta y el registro PD-17 del micro-ciclo en
   `supervision-record.md`.
3. **Resto de T7** (`plan.md`, fila T7):
   - integración pendiente y defectos observables;
   - un review del conjunto de T7;
   - medir R5, el costo del guard;
   - completar PD-13 y dar disposición a la fricción. La corrección del
     generador global (grep/glob) va a 003-003 según
     `docs/epics/epic-003-context-efficiency/friction-intake-004-001.md`, adenda
     W-2.
4. **Segunda mirada única** sobre 004-002 completa. La hace Codex con
   `gpt-6-astra` cuando vuelva a tener crédito (desde el 2026-10-03 14:45) o,
   si no hay, Claude Opus. Se registra en el ledger.
5. **Scribe**: borradores del Memory Bank → aprobación del dueño → cierre de
   004-002 (`stage_history`, `epic_features`). Después se pasa a 004-003.

## 3. Producción de paquetes v2

La instalación global (`~/.config/opencode`, `~/.claude`) **no se toca**:
otros proyectos usan CDAD v1 en esta máquina (decisión del dueño). Los paquetes
v2 salen de la instalación aislada:

```bash
R=<home>/.cache/cdad-004-002-v2/root
CDAD_OPENCODE_AGENTS_DIR=$R/.config/opencode/agents \
  python3 $R/.claude/skills/cdad-cycle/scripts/cdad_packet.py prepare \
  --project-root "$PWD" --role <rol> ...
```

- **Registrar cada intento** con
  `--record-dispatch <packet-id> --attempt-id <id> --input <attempt.json>`
  (guía §5). El id del intento es único por ejecución, así que debe incluir el
  paquete (por ejemplo `green-021-a1`). Reutilizarlo hace fallar I8.
- **Reinstalar la raíz aislada** cuando el GREEN cambie el producto, para que
  el productor sea el código ya corregido:
  `CDAD_INSTALL_ROOT=$R ./install.sh` desde el repo. Nunca con el HOME real.
- **Antes de cada `prepare`**, marcar el paquete anterior como `completed` en
  el state (PD-4) y commitear `docs/` por pathspec.

## 4. Advertencias para el orquestador de OpenCode

- **Hay que verificar qué modelo usa cada subagente.** Los agentes de proyecto
  `.opencode/agents/*.md` heredan el `model:` del canónico, y no coincide con
  la selección vigente (ADR-007: `deepseek-v4.1-flash` para architect,
  implementer y scribe; `glm-5.3-flash` para test-writer y reviewer):
  - test-writer: `mofgw/glm-5.2`;
  - implementer: `mofgw/deepseek-v4-flash`;
  - reviewer: `mofgw/qwen3.7-plus`, que no es una variante flash.

  Hasta ahora el orquestador lo forzaba con `-m` al despachar. Delegando
  dentro del arnés, eso **queda pendiente de decisión del dueño**, porque
  editar los derivados a mano está rechazado por diseño (manifiesto I9). Las
  opciones son ajustar el `model:` en el canónico o un override en la config
  de OpenCode del proyecto. Esta segunda opción está sin verificar: hay que
  probarla antes de confiar en ella. El modelo efectivo de cada sesión se
  comprueba en `opencode.db` (`session_v2.model`) y se anota en el ledger.
- **Implementer y reviewer tienen que ser de familias distintas.** El
  orquestador valida cada oráculo y cada hallazgo contra el código antes de
  aceptarlo. Ya hubo tres defectos de oráculo atrapados así; ver
  `supervision-record.md`.
- **Las suites se corren en primer plano.** Si un rol las manda a segundo
  plano, su turno termina antes del resultado.
- **Fallos preexistentes, ajenos a 004-002:** dos en
  `tests/validate-consistency.sh` (`install.sh --check` y skills instalados) y
  uno en `validate-odoo-specialization.sh`. Se confirmó con la línea base del
  red-020.
- **Prohibido:**
  - `--no-verify`, que se audita en cada commit de un rol con escritura;
  - el push automático;
  - leer `tests/.sensitive-patterns.local`;
  - instalar sobre el HOME real.

  Antes de publicar en un repo público hay que anonimizar y sanear el
  historial local de `c0511e1`.

## 5. Revisión con Claude entre ciclos

Al cerrar cada ciclo (GREEN + review, o una tarea), traer:

1. el rango de commits del ciclo;
2. el paquete o los paquetes y sus filas del ledger;
3. la salida de la suite de cierre, idealmente de un worktree fijado en el
   commit que se cierra;
4. el registro PD-17 propuesto: (a) resultado contra el contrato, (b) alcance,
   (c) desvíos y su disposición.

Claude contrasta todo eso contra el código y dictamina si el ciclo cierra o
qué falta.
