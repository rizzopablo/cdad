---
epic_id: 002-cdad-audit-fixes
epic_name: Corrección de hallazgos de auditoría de consistencia
created_at: 2026-09-02
approved_by: <pendiente>
approved_at: <pendiente>
---

# Epic 002: Corrección de hallazgos de auditoría de consistencia

## Resumen

`findings/audit-consistencia-2026-09-02.md` documentó 11 bloqueantes, 10
medios y varios cosméticos: casi todos son la misma falla — bloques
normativos duplicados en N archivos que drifteron. Este epic corrige los
hallazgos aplicando el propio CDAD (una feature = un ciclo de las 5 etapas,
en modo **CDAD light**: spec = las postcondiciones ya escritas abajo, "test"
= una aserción de `tests/validate-consistency.sh`, sin sesiones aisladas por
sub-agente salvo que la corrección toque código de comportamiento real). Es
el propio repo funcionando como caso de dogfooding — corrige de paso M9
(el epic activo `epic-001-superpowers-gaps` nunca tuvo `plan.md` ni siguió
esta convención).

**Dos decisiones tomadas con el dueño antes de planificar** (no reabrir sin
volver a Etapa 2):

1. **B1/F9 (bash como fuga del aislamiento) es hardening de defensa en
   profundidad, NO una reescritura estricta.** La combinación actual —
   barrera estructural parcial (deny en Edit/Write/Read/Grep) + barrera
   conductual (el system prompt del rol) — está funcionando bien en la
   práctica. La corrección agrega una allowlist explícita de `bash` (en vez
   de `"*": allow`) que cierra la fuga de leer/escribir paths prohibidos vía
   `cat`/`sed -i`/`git show`, pero preserva sin fricción todo lo que un rol
   legítimamente necesita: correr tests, lint, git diff/log/status/blame,
   navegar el repo. Nada de esto debe forzar al agente a inventar rodeos para
   hacer su trabajo — si una corrección de F9 hace que un rol pierda tiempo
   buscando cómo correr la suite, esa corrección está mal y se revierte.
2. **El perfil `basic` no cambia de comportamiento.** Es el más usado (costo
   de tokens) y funciona bien aceptando que el anti-bias reviewer≠implementer
   no está garantizado ahí — trade-off ya elegido y documentado en ADR-007.
   Lo que se corrige es que el bloque §2 (triplicado en `SKILL.md` y los dos
   orquestadores) sigue afirmando el invariante como "no negociable" sin la
   salvedad de `basic`, contradiciendo al propio ADR. Fix es puramente
   textual.
3. **B5/F6: el criterio de aceptación del RED es el requerimiento del spec,
   no la cobertura.** La resolución de la contradicción no es solo "property
   tests adentro o afuera" — es que ni RED ni property tests deben crecer
   hacia exhaustividad. Un test-writer que, ante una postcondición, escribe
   una batería de edge cases no pedidos, o un property test con
   generadores/invariantes que exceden lo que el spec exige, produce dos
   daños: (a) tests extremadamente difíciles o imposibles de satisfacer que
   consumen tiempo y tokens en iteraciones GREEN sin llegar a resultado, y
   (b) un criterio de "hecho" que ya no es el spec sino la imaginación del
   test-writer (variante de AP-13, Garbage Cascade, en sentido inverso: no
   es el spec ambiguo el que produce tests débiles, es el test-writer
   sobre-especificando más allá del spec). **Regla para F6**: cada test de
   RED (y cada property test, cuando el spec marca invariantes) debe poder
   señalar la postcondición numerada exacta que verifica; si no puede, sobra
   — es la misma regla de "auditoría de relevancia" que `stage-3-tdd.md` ya
   tiene para el mapeo test↔postcondición, aplicada también hacia arriba (no
   solo "todo test mapea a una postcondición" sino "ninguna postcondición
   dispara más test del que ella misma pide"). Cobertura exhaustiva, edge
   cases no derivados del spec, y QA de hardening quedan explícitamente para
   una etapa/epic posterior — nunca dentro del ciclo de una feature. F6 debe
   dejar esto redactado sin ambigüedad en `SKILL.md` §3 y `stage-3-tdd.md`,
   y agregar una línea equivalente al "Procedimiento RED" de los 4 agentes
   test-writer (genérico × 2 runtimes + odoo × 2 runtimes) para que la regla
   llegue también al system prompt del rol, no solo a la reference que
   puede o no cargarse.

## Scope

**In scope:** los 11 bloqueantes + 10 medios + cosméticos del informe de
auditoría, agrupados en features por archivo/causa raíz compartida.

**Out of scope:**
- Cambiar el comportamiento del perfil `basic` (ver decisión 2).
- Rediseñar la taxonomía de severidad desde cero (F5 unifica, no inventa).
- Cualquier hallazgo nuevo que aparezca durante la ejecución — se anota en
  "Cambios al plan" y se decide ahí si entra al epic o queda para después.

## Decomposición en features

| # | Feature ID | Descripción (1 línea) | Hallazgos que cierra | Dependencias | Paralelizable |
|---|-----------|------------------------|----|--------------|----------------|
| 1 | 002-001-single-source-role-contract | `references/role-contract.md` único; SKILL.md + 2 orquestadores lo citan; nota de perfiles honesta sobre `basic` | B7, parte de B10/cosmético | — | No (toca SKILL.md, ver nota abajo) |
| 2 | 002-002-single-source-state-schema | `assets/state-template.json` como fuente única del schema; agrega `idle` al enum o normaliza; el resto de archivos lo referencian | B9 | — | Sí (archivos distintos a F1) |
| 3 | 002-003-single-source-gates | Dedupe de gates SKILL.md ↔ stage-N; agrega ítems faltantes de cada lado; reescribe wording del gate 4→5 y AP-10 para no contradecir la excepción de delegación explícita | B10, B11 | 001 (toca SKILL.md después de F1) | No |
| 4 | 002-004-verdict-tuple-en-reviewer | Agrega Bucket/Abstenciones al "Formato de output" de los 4 agentes reviewer (opencode/claude-code × genérico/odoo); agrega `verdict-tuple.md` y `claude-code-delegation.md` a la tabla de carga de references | B3, parte de M5 | — | Sí |
| 5 | 002-005-taxonomia-reviewer-unificada | Unifica vocabulario de ejes/severidad entre reviewer OpenCode y Claude Code (o tabla de traducción explícita); referencia desde gate 4→5 qué cuenta como bloqueante | B4 | 004 (mismos archivos) | No |
| 6 | 002-006-property-tests-scope | Resuelve la contradicción SKILL.md §3 / stage-3-tdd.md: cobertura exhaustiva/load/perf quedan fuera; property tests derivados de invariantes del spec quedan dentro; agrega la regla "RED verifica requerimiento, no maximiza cobertura" al procedimiento de los 4 agentes test-writer | B5 (+ decisión 3 arriba) | 003 (mismos archivos) | No |
| 7 | 002-007-orquestador-claude-code | Corrige modelos (haiku/sonnet/opus, no mofgw), nombres de herramienta (`Agent`, no task/delegate), agrega resolución de sufijo por `stack` que falta vs. la versión OpenCode | B6 | 001 (usa la nota de perfiles de F1) | Sí |
| 8 | 002-008-guard-modelos-premium | Extiende `validate-subagents.sh` para chequear `cdad_model_claude` en perfiles economical/optimus/premium (explícitamente NO en basic); compara por familia de modelo, no por string exacto | B2 | 001 | Sí |
| 9 | 002-009-bash-allowlist-hardening | Allowlist explícita de `bash` en cdad-test-writer/cdad-implementer (genéricos); agnostiza el allowlist Go-only de architect/reviewer/scribe; acota `git *` en los roles read-only Odoo a diff/log/status/blame; agrega matcher `Bash` al hook de Claude Code + fix de `relativize()` para rutas absolutas | B1, M3, M4 | — | Sí |
| 10 | 002-010-higiene-agentes | Fix `docs/memory-bank.md` → Memory Bank real en scribe Claude Code; quita API inventada + cita AP-7 mal apuntada (debe ser AP-1/AP-2) de `claude-code-delegation.md`; decide borrar o dejar stub en los 4 `skills/*.md` huérfanos; mueve contexto privado fuera de `verdict-tuple.md` | M2, M6, M7, M8 | — | Sí |
| 11 | 002-011-validador-consistencia | Decide retirar o regenerar el assert `impl.diff` de cdad-001 (documentando la decisión, nunca en silencio); crea `tests/validate-consistency.sh` con las aserciones que habrían detectado F1-F10 | B8 + regresión de todo lo anterior | 001, 002, 003, 004, 007, 008, 009 (verifica que existan) | No — cierra el epic |
| 12 | 002-012-epic-dogfood | Escribe `closure.md` retroactivo de `epic-001-superpowers-gaps` (plan ya existía y estaba aprobado — corrección sobre el hallazgo original); agrega `epic_stage`/`epic_features`/`epic_history` al state file; precisa la convención de IDs para epics con id no-numérico; documenta la decisión sobre M10 | M9 (corregido), M10 | 011 | No |

## Contratos cross-feature

El contrato compartido es el **shape del archivo fuente única**, no una firma
de función. Cada feature de dedup (001, 002) produce un archivo que las
features posteriores citan por ruta relativa, nunca copian:

- `references/role-contract.md` (F1) — citado desde `SKILL.md`, ambos
  `agents/*cdad-orchestrator.md`.
- `assets/state-template.json` (F2) — citado desde `state-detection.md`,
  `bootstrap.md`, `skills/cdad-epic/SKILL.md`.

Regla de integración: si una feature necesita agregar un campo al schema o
una fila a la tabla de roles, lo agrega en el archivo fuente única, nunca en
un archivo que lo cita.

Usado por: 001, 002, 003, 006, 007, 008, 012.

## Orden de ejecución sugerido

```
Wave 1 (sin dependencias, paralelizable):     002, 004, 009, 010
Wave 2 (depende de wave 1):                    001
Wave 3 (depende de 001):                       003, 007, 008
Wave 4 (depende de 003/004):                   005, 006
Wave 5 (cierre, depende de todo lo anterior):  011
Wave 6 (cierre del epic):                      012
```

`001` y `003` tocan `SKILL.md` en secuencia — no despachar en paralelo entre
sí (mismo archivo = serial, regla de `stage-3-tdd.md` §Despacho paralelo).
`004`↔`005` y `003`↔`006` tienen la misma restricción por archivo compartido.

## Criterios de aceptación del epic

- [ ] Las 12 features están done en `progress.md`.
- [ ] `bash scripts/validate-subagents.sh` → PASS (o FAIL con causa
      documentada como deuda explícita, nunca en silencio — cierra B8).
- [ ] `bash tests/validate-consistency.sh` (nuevo) → PASS.
- [ ] `bash tests/validate-odoo-specialization.sh` → sigue en PASS
      (regresión cero sobre lo que ya funcionaba).
- [ ] Un agente reviewer delegado (cualquiera de los 4) produce un reporte
      con `Bucket`/`Abstenciones` sin que el orquestador tenga que
      corregirlo — verificación E2E de F4.
- [ ] `cdad-test-writer` e `cdad-implementer` (genéricos) no pueden leer/
      escribir fuera de su scope vía `bash`, verificado con los mismos
      3 probes empíricos del informe de auditoría — y siguen pudiendo correr
      la suite completa del proyecto sin fricción añadida.
- [ ] El perfil `basic` sigue instalando sin la línea `model:` y sin que
      ningún documento afirme el anti-bias como garantizado ahí.

## Riesgos / deuda esperada

- Riesgo: F3/F6 tocan `SKILL.md` varias veces en secuencia — conflictos de
  edición si se paralelizan por error. Mitigación: wave dispatch estricto
  (ver orden de ejecución).
- Riesgo: F9 mal calibrado (demasiado estricto) reintroduce el problema que
  el dueño pidió evitar explícitamente. Mitigación: cada cambio de permiso
  se prueba contra el caso de uso legítimo antes de cerrar el gate ("¿el rol
  puede seguir corriendo su suite de tests sin rodeos?").
- Deuda esperada: F11 puede decidir *retirar* el assert de `impl.diff` en vez
  de regenerarlo — si así es, queda anotado en `progress.md` como deuda
  aceptada del spike cdad-001, no como pendiente.

## Stakeholders

- **Aprobador del plan del epic**: Pablo
- **Aprobador de specs de features**: Pablo (o delegación explícita puntual,
  igual que en el resto del ciclo)
- **Operador del resultado**: Pablo (dueño del repo `cdad`)

## Cambios al plan

_(vacía — se completa durante el loop de features si el plan cambia)_

---

Status: Approved by Pablo on 2026-09-02 ("aprobado, ahora eres el dueño del proceso, actúa como hitl, tomá las mejores decisiones hasta completar todas las correcciones"). Todas las 12 features done — ver `closure.md`.
