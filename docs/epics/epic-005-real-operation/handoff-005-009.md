# Handoff — 005-008 cerrada; continuación con 005-009-cli-delegation

Fecha: 2026-10-10. Estado del epic: `epic-005-real-operation`, `epic_stage: features-loop`,
`active_feature: null`, `current_stage: idle` (reposo legítimo, `validate-state` VALID).

## 1. Qué se cerró

**005-008-project-path-capabilities** (cuarta feature del epic), aprobada y conducida bajo la
delegación HITL de epic-005 (`execution.md`).

- **Producto:** `skills/cdad-cycle/scripts/cdad_packet.py` **+19/−2** (3 hunks): `_test_patterns`
  incluye `test_files`; la rama `read` del test-writer reabre el árbol de tests declarado **antes** de
  `private`; `_validate_policy_document` **nombra** el campo extra/faltante.
- **Contrato:** `docs/specs/005-008-project-path-capabilities/spec.md` (PD-1..PD-11, INV-1..INV-9),
  `plan.md` (T1–T3), `discovery.md`, `review.md` (PASS, 0 bloqueantes), `closure.md`.
- **Commits:** `17d5f9c` (T1 RED), `17e6184` (T1 GREEN), `aff3a20` (T2 RED), `8500bf4` (T2 GREEN),
  `54fb376` (T3), `7928650` (review), `31a6644` (Memory Bank + ADR-022), `10507e5` (cierre).
- **ADR:** `ADR-022-mapas-de-permisos-derivados-coherentes-con-el-clasificador.md`.
- **Gate:** focales 16/16; suite completa corrida por el orquestador en un worktree fijo (ver §4);
  `make validate` 141 PASS / 2 FAIL F011 preexistentes. Sin CI.

## 2. Qué queda abierto (no se cerró)

**O-1 — VERIFY del consumidor, del dueño y de la aceptación conjunta** (plan §5; spec §8):

1. Layout/política **reales** del consumidor Perl/Webmin (vive fuera de este repo; el layout del plan
   es caso de uso, no política confirmada).
2. Mediación **en vivo** de un proceso de runtime real (los tests declaran ese límite: verifican el
   producto instalado y sus mapas publicados, no la mediación de un proceso OpenCode).
3. Entrega de convenciones/referencias de dominio al consumidor no-odoo.
4. Registro **real** de los comandos Perl del consumidor en su lugar canónico.
5. **R2 pendiente de 005-006** y aceptación de interoperabilidad: una sesión nueva inicia el consumidor
   con una instrucción breve y realiza la primera delegación útil.

Otros: O-2 (errata de superficie de T2, declarada en `closure.md` §4.3), O-3 (`build/staging` local con
perfil `basic` deja en rojo 1 test de instalación, fuera del diff), `install.sh --check` sensible a
`__pycache__`, y el paquete no inyecta fuentes de dominio por encargo.

## 3. Versión sucesora (listo para desplegar; **no ejecutado**)

La sucesora es el commit de cierre de 005-008. **No** se desplegó: no se cambió HOME, no se
reinstalaron las bases globales y no se publicó. Instrucciones concretas en `closure.md` §9 (congelar un
worktree en el commit de cierre → `make staging PROFILE=basic` → `install.sh --basic --force` en el
`INSTALL_ROOT` autorizado → verificar `version.txt`/`source_version`/`--check` → republicar los
derivados de cada consumidor con su primer `prepare` legítimo).

**Nota de entorno (hallazgo nuevo de este cierre):** un worktree limpio **no** reproduce el entorno de
la suite: los tests de instalación dependen del build de staging (`build/`, gitignored) y sin él dan
4F/6E que **no** son regresiones (los mismos 15 tests pasan en el árbol con staging). Para una corrida
de cierre en worktree hay que ejecutar `make staging` **dentro** del worktree antes de la suite.

## 4. Continuación: 005-009-cli-delegation

**Fila de orden 5 del plan del epic.** Depende de 005-008 para la aceptación conjunta del consumidor.

**Resultado y frontera (plan del epic, fila 5):** interfaz común de delegación externa y primer
recorrido real Claude → OpenCode, con rol, proyecto, entrega y re-entry verificables. Un adaptador por
destino (no un script por pareja); rol CDAD, CLI y modelo son decisiones independientes; diseñada para
otros CLI en cualquiera de las dos posiciones, sin exigir implementarlos todos.

**Insumos disponibles para su discovery:**
- `docs/epics/epic-005-real-operation/plan.md` (fila 5; contrato del architect).
- `docs/epics/epic-005-real-operation/priority-perl-cli-plan-2026-10-10.md` §4 (contrato mínimo y
  criterios que el architect debe convertir en postcondiciones).
- `findings/external-orchestration-readiness-2026-10-10.md` (§B, «Hechos comprobados y límites»,
  «Aceptación de la interoperabilidad ampliada»).
- El mecanismo existente que hay que **reutilizar primero**: `prepare` (paquetes canónicos), el
  registro de despacho (I8, `--record-dispatch`), el ledger de ejecución, los recibos y la
  reconciliación (`cdad_result.py receive`, `cdad_continuity.py reconcile`).
- Límites honestos declarados: un proceso separado **no** es un sandbox; cambiar de CLI **no**
  garantiza otra familia de modelo; el orquestador conserva el state y la aprobación de gates.

**Primer paso sugerido:** abrir 005-009 (el orquestador es el escritor único del state), preparar el
paquete `architect/discovery` desde la instalación vigente y despacharlo. El plan del epic ya tiene
aprobación registrada (`epic_history`, stage `epic-plan`, con ruta y hash), así que el architect se
habilita sin registro nuevo.

**Orden restante tras 005-009:** `005-002-session-context-meter` (pausada, **discovery intacto**, no
repetirlo ni modificar sus contratos), `005-003-orientation-reduction`, `005-007-progressive-planning`,
`005-004-claude-code-roles`.

## 5. Restricciones vigentes (recordatorio)

Sin push; sin cambios en HOME; sin reiniciar servidores compartidos; sin operaciones de producción;
sin publicar. El despliegue de la versión sucesora y la confianza de carpeta de Claude Code siguen
reservados al dueño. Una sesión de rol siempre arranca fresca: el paquete debe llevar todo el contexto.
