# Review formal — 005-006-guided-project-start (etapa 4)

**Role:** reviewer · **Packet:** 005-006-guided-project-start-reviewer-review-001 (validado) ·
**Sesión:** independiente (GLM/mofgw; familia distinta del implementador).
**Contrato:** docs/specs/005-006-guided-project-start/spec.md (PD-1..PD-17, INV-1..INV-8) + plan.md (T1..T5).
**Diff:** `git diff ce67a6e..e0ca829` (rama codex/epic-005-real-operation). Commits verificados:
0c7d951 + 91eaaaf (T1 RED + enmienda de oráculo), 421ddf2 (T1 GREEN), b2740a0 (T2 RED),
4d96905 (T2 GREEN), 485503f (T3 RED), 8dd8c09 (T3 GREEN), 3c4b2be (T4 RED), fe8d742 (T4
GREEN), 2b69074 (T5 RED/locks), e0ca829 (aceptación registrada).
Nota: durante la review HEAD avanzó a 613dfa2 («chore(state): checkpoint active_packet
reviewer/prepared») = e0ca829 + 1 commit que toca solo `docs/.cdad-state.json` (checkpoint del
orquestador al preparar este paquete). No es producto del feature; no lo evaluo como diff.
**Write scope real:** ninguno (paquete `write_scope: []`) — el repo quedó intocado por esta
review (verificado). Workspace de evidencia: `/tmp/opencode` (clones desechables:
`/tmp/opencode/e5-006-rev-base`).

**Bucket por observables (verdict-tuple):** familia distinta del implementador (+1) · diff de
producto completo en contexto (los 6 archivos de producto íntegros) + tests leídos por
inventario completo y cuerpos con aserciones (+1) · citas exactas file:line (+1) ·
spec+plan+referencias en contexto (+1) → **h**.

---

## 1. Gate de evidencia — mis comandos y salidas

| # | Comando (exacto) | Resultado |
|---|---|---|
| G1 | `git diff --stat ce67a6e..HEAD` | 15 archivos; +2.963/−37; archivos de producto: `project-start.md` (nuevo, 106 l.), `SKILL.md`, `continuity.md`, `state-detection.md`, `orchestrator.md`, `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`, `epic-planning.md`, `README.md` (+10 l.) |
| G2 | `pytest (5 focales 005-006) -q` | **31 passed** (T1:15, T2:6, T3:4, T4:2, T5:4) en 1.50s |
| G3 | `pytest tests/ -q -p no:cacheprovider` | **680 passed / 0 failed** en 743.6s (12m23s) — CONSISTENTE con lo declarado en T4-close (676 + 4 de T5) |
| G4 | `make validate` (árbol del repo, con prepare en vuelo) | 141 PASS / **2 FAIL** |
| G5 | `make validate` en **clone limpio @613dfa2** | 142 PASS / **1 FAIL** |
| G6 | `python3 -m pytest …focales…` en clone con files de producto revertidos a ce67a6e (RED audit) | **25 failed / 6 passed** — coherencia exacta con los RED declarados (T1:14+T2:6+T3:3+T4:2=25) y los locks verdes declarados: `pd15` (guard de ausencia), `pd12_enforcement_lock`, los 4 de T5 (locks de comportamiento «verdes hoy» por diseño) |
| G7 | `git diff --stat -- scripts/ skills/cdad-cycle/scripts/` (ce67a6e..HEAD) | **vacío** → `cdad_packet.py`, `cdad_continuity.py`, `cdad_result.py` intactos (PD-12(c), PD-10 lectura) |
| G8 | `make agents` en clone @613dfa2 + `git status` | **sin ninguna modificación** → los agentes comprometidos son byte-parity del generador (PD-2(b)) |
| G9 | `git diff --stat -- docs/epics/epic-005-real-operation/plan.md …/execution.md` | **vacío** (INV-7) |

### G4/G5 — los 2 FAIL de `make validate`, separados del diff

**FAIL 1 — `F011: scripts/validate-subagents.sh (active profile)` — PREEXISTENTE, esperado por el diseño del epic.**
Detalle (run directo, clone): `install.sh --check` → DRIFT contra el producto **instalado en
HOME**: `DRIFT: missing <home>/.claude/skills/cdad-cycle/references/project-start.md` y
`differs` en los textos tocados (SKILL.md, state-detection.md, continuity.md, epic-planning.md,
agentes). La instalación no contiene todavía los textos nuevos — **la activación de versiones es
reservada al dueño** (restricción global del plan: «No instalar CDAD en HOME ni activar
versiones»; INV-7) y el criterio 2 del epic exige despachar con versión estable sin mezclas.
Es la señal esperada «repo adelantado a la instalación», no un defecto del diff (FAIL también
en ce67a6e, run en clone base). Nota ambiental: en árbol fresco el validator exige
`make staging` (build/ no está en git) — la corrida en clone requiere regenerar staging, ya hecho.
**Se auto-limpia** al activar el dueño; verificación de cierre: `bash install.sh --check` rc=0.

**FAIL 2 — `F011: tests/validate-odoo-specialization.sh` (A3) — PREEXISTENTE, dependiente del entorno local.**
A3 falla **solo donde existe `tests/.sensitive-patterns.local`** (85 bytes, gitignored, presente
solo en el árbol del repo): señala `docs/specs/004-003-planning-procedures/supervision-record.md`,
`review-t5.md`, `tests/test_role_packets.py` (+pyc del entorno). **Éstos son archivos de
004-003/005-001 (commit e49a1ce), anteriores al diff; 0 de ellos pertenece a 005-006.** En el
clone limpio @613dfa2 el validator pasa **67/67 PASS** (incluido A3) — la diferencia es
exclusivamente el archivo privado de patrones. No atribuible a 005-006.

**Delta del diff sobre `make validate`: cero fallos nuevos.** (Los FAIL transient de la primera
corrida G4 incluían el state `docs/.cdad-state.json` no-committeado del prepare del propio
paquete de review, en vuelo al correr; con el árbol limpio queda 1 FAIL preexistente.)

---

## 2. Auditoría de relevancia (AP-13 / AP-14)

**Cobertura PD → test (31 tests, 0 superfluos):**

| PD/INV | Test(s) |
|---|---|
| PD-1 | T1::pd1 (existe, fila de tabla, no reproduce intake) |
| PD-2 | T2::pd2 (entrada boot-at-rest en la source) + T2::pd2 parity (generador↔generados) |
| PD-3 | T1::pd3 (container/hint-not-norm, sin búsqueda global) |
| PD-4 | T1::pd4 (3 clases por referencia) |
| PD-5 | T1::pd5 (preservación + anti-patrones/no-clobber por referencia) |
| PD-6 | T1::pd6 (tabla restricción→lugar canónico, 6 filas máquina-legibles) |
| PD-7 | T1::pd7 (inferible vs usuario; 3-4 preguntas; activeContext sin usuario) |
| PD-8 | T1::pd8 (encadenado al primer encargo preparado) |
| PD-9 | T1::pd9 (rama no-resume en reposo: procedimiento + SKILL Step 1) |
| PD-10 | T1::pd10 (puntos de cableado SKILL/continuity) + T2::pd10 (wiring intake) |
| PD-11 | T4::pd11 (sección corta que remite; sin prompt largo) |
| PD-12 | T3::pd12×3 (propietario epic-planning; desfase en project-start; **lock** de enforcement en código) |
| PD-13 | T1::pd13 (dueño canónico declarado, no re-declarado) |
| PD-14 | T2::pd14 (salida legítima ante bloqueo en intake) + T5 R3 (comportamiento CLI) |
| PD-15 | T1::pd15 (guard: sin plantilla bajo assets) |
| PD-16 | T5::R3a, R3b, R1 (comportamiento) |
| PD-17 | T5::pd17 (empírico contra CLI) |
| INV-1 | T1::inv1 (detector estructural heading/fila ≥18/≥25 chars, owner-by-owner) |
| INV-2 | T1::inv2 |
| INV-3 | T1::inv3 (preguntas acotadas) + T3::inv3 (escritor único del state) |
| INV-4 | T1::inv4 + T2::inv4 (procedimiento e intake por separado) |
| INV-5 | T2::inv5 (barrido de TODA la source del orquestador) |
| INV-6 | T4::inv6 (ni bloque en README ni plantilla en assets) |
| INV-7 | **sin test** (script §9) — verificado por revisión (G9: epic plan/execution sin tocar) |
| INV-8 | **sin test** (script §9) — verificado por revisión (sin telemetría/presupuestos en el diff) |

- **AP-14 (test→PD):** los 31 tests mapean 1:1 a PD/INV declarados en su docstring; ningún test
  suelto. Los 4 de T5 son comportamiento (la única caja negra de la feature); el resto es
  consistencia estructural de artefactos distribuidos — conforme a la condición de aprobación
  del plan §Aprobación y a la regla vigente
  (`docs/specs/004-003…/efficient-orchestration-requirements.md:104-107`: no son suites que
  busquen frases para *probar obediencia*; verifican existencia/referencia-en-vez-de-copia/
  wiring/parity — propiedades del sistema de artefactos). La parte de prosa pura queda, como
  previó el plan, a esta review: leída y sin hallazgo de género.
- **AP-13 (PD/INV→test):** 0 PD sin test. Únicos huecos de invariante: INV-7/INV-8, declarados
  por el propio plan («Declarados en spec §9») — hago el hueco visible abajo (F2) pero no lo
  cuento como violación: son invariantes *negativos* de no-cambio, el diff los cumple (G9 y
  ausencia de métricas), y un lock barato cerraría la deriva futura.
- Los RED registrados son reales y completos (G6): 25 fallos post-revert, sin falsos verdes.

---

## 3. Verificaciones propias de las afirmaciones clave (no por los reportes de los roles)

1. **`cdad_packet.py` no cambia (G7)** — enforcement `epic_features` y `prepare` intactos ✓ (PD-12(c), spec §2).
2. **Byte-parity de agentes (G8)** — regeneración desde `sources/` sin delta ✓ (PD-2(b)); ambos generados proyectan la entrada boot-at-rest (grep «Boot-at-rest» en agentes:40/:40) ✓.
3. **INV-1 referencia-una-vez:** `project-start.md` referencia los 5 dueños (líneas 7-11), declara «never by copying», clasifica *por referencia* (§2), la tabla restricción→lugar (§4) es la del spec (6 filas, lugares canónicos idénticos), y el detector estructural del INV-1 (headings ≥18 chars + filas ≥25 chars normalizados, owner-por-owner) no tiene falsos positivos con la nueva tabla (31/31 verdes incluye ese check); lectura directa: ninguna regla de política/autoridad ni algoritmo de detección duplicado ✓.
4. **Enmienda de oráculo 91eaaaf (T1 PD-9):** diff de 3 líneas: acumulador `window_hits` pasa de strings a tuplas `(lineno, line)`; misma ventana 230-300; la aserción final sigue exigiendo que el contexto ±4 líneas de *un hit* de `P9_RESUME` contenga `P9_BRANCH` — **intención conservada**, ámbito no ampliado, sin tocar 421ddf2. El defecto original enmascaraba la parte (b) en RED (abortaba antes en `_load(PSTART)`); post-enmienda la parte (b) se ejecuta de verdad. Sin objeción.
5. **Los 4 locks de T5 son legítimos, no verdes vacíos:** cada uno verifica *precondiciones* (Memory Bank ausente pre-verificado; `.cdad/` ausente; `execution`/`active_packet` null; head de continuidad ausente), y afirma comportamiento: PD-17 (rc=0, `state: no-checkpoint`, proyección vacía campo-por-campo, sin publicar nada con snapshot byte-a-byte, stdin cerrado + timeout + sin traceback); R3a (rc≠0 + stdout vacío + nombra `cdad-policy.json` + sin publicación); R3b (rc=2 + `approval pending` + tokens `stage_history`/`specification`/`contract_sha256` + nombra la spec + sin publicación); R1 (rc=0 + paquete canónico en stdout + `status: prepared` + REQUEST sirve a la spec pineada path/sha + `validate-request` del propio producto rc=0 + binding public). ✓.
6. **README (PD-11/INV-6):** +10 líneas, remite a `references/project-start.md`, sin prompt largo, sin plantilla nueva (G6 pd15 verde = ausencia) ✓.
7. **Intake (PD-2/14/INV-4/5):** entrada «Boot-at-rest path» que ordena cargar metodología primero y señala `references/project-start.md`; «Blocked exit» que reusa los marcadores `approval pending`/`state incoherent` por referencia y prohíbe fabricar autoridad/cambiar versión en silencio/publicar paquete inválido; `resume` recalificado («Start from rest: never resume without an active execution») y clase `living` recalificada coherentemente; wiring de continuidad/re-entry con `$CDAD_INSTALL_ROOT` ✓.
8. **epic-planning (PD-12/INV-3):** responsable = coordinador de epic; escritor único del state = orquestador ✓.
9. **state-detection (PD-13):** bloque de dueño canónico con puntero al arranque, sin absorber el vocabulario de epic ✓.

---

## 4. Hallazgos (con tuple)

### F1 — (OPTIONAL · h) SKILL.md:278: ruta relativa del CLI sin marcar en Step 6 (re-entry) — el único residuo de la familia fricción-2 en el recorrido guiado
- **Provenance:** `skills/cdad-cycle/SKILL.md:278` — «the CLI is `scripts/cdad_result.py`» (sin ningún marcador de instalación), frente al cableado del mismo CLI en la fuente del rol
  (`sources/roles/orchestrator.md`, re-entry wiring: `$CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/cdad_result.py`) y al `re-entry.md:19`, que va calificado («the installed entrypoint under the skill behaves the same»). La familia también deja hojas descriptivas menores: `continuity.md:3-4` («wrapper: `scripts/cdad_continuity.py`»).
- **Rationale (mechanismo):** PD-10 corrigió iónicamente los puntos que el plan enumeró (`SKILL.md:260-261`, `:451-452`, `continuity.md:31-44`, `orchestrator.md:80-98`) — el punto :278 del **mismo skill** quedó fuera del set de verificación declarado. Hoy conviven **dos declaraciones opuestas de ruta para el mismo CLI** dentro del mismo skill. En un proyecto consumidor la ruta relativa no existe (`discovery §4.2`).
- **Consecuencia (uso real):** el recorrido guiado termina SU característica observable pasando por re-entry (despachar → volver con result → `receive`/validar receipt): el paso atraviesado declara una ruta rota en consumidor; la corrida real R2 es exactamente donde se materializa (misma clase de fricción 2 que PD-10 prometió cerrar). No bloquea la review del diff: es instancia **preexistente** (no introducida ni debilitada por el diff) y fuera del set de verificación enumerado de PD-10.
- **Cierre verificable:** (1) 1 línea en `SKILL.md:278` → `$CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/cdad_result.py`; (2) extender el barrido de la familia (T1::pd10 + T2::inv5) a los Steps 5-8 de SKILL.md con regla «0 ofensores sin marcar» (la misma regex `PD10_CLI_RELATIVE` ya la clasifica correctamente como ofensor); focales + suite verdes. **Radio mínimo recomendado: antes de la corrida real R2**, que es la que ejercitará el punto.
- **Bucket h justificación:** familia distinta (+1), diff de producto completo (+1), cita exacta (+1), spec+referencias en contexto (+1).

### F2 — (OPTIONAL · m) INV-7 / INV-8 sin test dedicado: único hueco de cobertura de invariante (hoy declarado, mañana sin cerco)
- **Provenance:** plan.md §Auto-revisión («INV-7/INV-8 → declarados en spec §9»); G9 demuestra cumplimiento en este diff (epic plan/execution sin tocar), y el diff no añade métricas/presupuestos (INV-8).
- **Consecuencia:** sin test, un diff FUTURO podría pisar la fila 3 y/o los criterios del epic sin que la suite proteste — Exactly la clase de deriva que el lock de T3 cerro para `cdad_packet.py`.
- **Cierre verificable:** lock estructural de ~10 líneas (ventanas sobre `plan.md:35` fila 3 y §«Criterios de aceptación del epic» + ausencia de presupuesto/telemetría en el ciclo), en la familia de los locks existentes. No prolonga el ciclo (calibración: opcional no extiende). **No requiere acción para esta feature.**

### F3 — (FYI · l) Desviación T3 (tomo de proyecto-start.md además de epic-planning.md)
Declarada y autorizada por el orquestador como consecuencia directa de PD-12(b); el §9 de
`project-start.md` es de hecho el efecto de PD-12(b). Nota de orden leve: T1 y T3 corrieron en
**paralelo** tocando `project-start.md` (Files lo incluye en T1, no en T3) — en esta corrida no
generó conflicto (commits secuenciales en la práctica + suite verde al cierre). Recordatorio
para el planificador (005-007, tamaño de unidad/files por tarea), sin acción aquí.

### F4 — (FYI · h) R2 real: gate de integración abierta — condición objetiva de cierre de la feature y riesgo de **corrida con versión mezclada**
- No simula R2 y **no lo computo como incumplimiento del diff**: el criterio PD-16 lo define como
  arranque real con el dueño (identificado en registro local), y VERIFY 5 queda abierto por
  diseño (spec §8). La feature declara los 4 locks verdes y admite la pendiente (e0ca829).
- **Aviso operativo para el cierre (etapa 5):** el producto instalado en HOME **no contiene aún
  los textos nuevos** (G4/G5: `missing project-start.md`, `differs` en los 5 archivos tocados +
  agentes). Correr la R2 sobre la instalación vigente sería correr con la versión vieja — invalidaría
  el punto del feature y violaría el criterio epic 2 (versión estable sin mezclas). La **activación
  (reservada al dueño)** es la primera condición material de la R2: sin ella, el orquestador no
  cargará la metodología con la entrada boot-at-rest ni el procedimiento tampoco.
- **Condiciones verificables de cierre de la feature:** (1) activación del dueño →
  `bash install.sh --check` rc=0 (CLEAR de F1 del gate); (2) corrida R2 real registrada como
  evidencia hasta primera delegación útil → cierra VERIFY 5; (3) opcionalmente concentrar F1
  (línea :278) antes/durante esa activación — un solo viaje de regeneración.

### F5 — (Optional-Consider · l) Aserciones con ventanas absolutas y marcadores laxos (nota de robustez, sin efecto hoy)
- `test_pd9` (window 230-300) y `test_pd10`/`test_inv5` (`PD10_INSTALL_MARKERS` incluye
  «installation» genérico) son tolerantes por diseño declarado; no debilitan nada HOY (verifiqué
  que las líneas consideradas corregidas contienen rutas instaladas reales, no solo la palabra).
  Solo si otra feature desplaza las ventanas o reutiliza el marcador genérico conviene revisitar.
  Sin acción.

---

## 5. Veredicto agregado

- **0 hallazgos BLOCKING sobre el diff.** El diff implementa los PD-1..PD-17/INV-1..INV-8
  audibles desde el repo sin debilitar garantías existentes (enforcement intacto G7; byte-parity
  G8; epopeya epic-docs intacta G9; RED real G6; suite completa 680/0 G3; validate sin fallos
  nuevos G5).
- Los 2 FAIL de `make validate` son **preexistentes y externos al diff** (drift de instalación
  pendiente de activación del dueño; A3 de 004-003/005-001 con archivo privado de patrones el
  ambiente). Desglosados en §1.
- Pendiente NO audible desde este repo: **R2 real (con activación del dueño)** — único criterio
  de aceptación abierto; es el gate de integración del plan y el cierre de VERIFY 5.

## 6. Abstenciones

- **ABSTAIN (l): La semántica deseada de los patrones de `tests/.sensitive-patterns.local`** — el plan prohíbe leerlo (restricción global); no puedo evaluar si las coincidencias de A3 sobre los archivos de 004-003/005-001 son intencionales (nombres/IDs privados reales publicación-en-README) o false positives depatterns antiguos. La decisión de sanitizar esos archivos Transfer detallada en la declaración del FAIL: **difiere a la decisión del dueño/QA**, sin atribuir a 005-006.
- **ABSTAIN (l): Comportamiento del generador fuera de este diff** — evalué parity byte-a-byte (G8), no la idempotencia completa del generador ante cambios de runtime/perfil (skills de runtime distintos) — son de 005-005/feature/proyecto, fuera del contrato de esta review.

Los clones de verificación quedan en `/tmp/opencode/e5-006-rev-base` (desechables, sin tocar el repo).
