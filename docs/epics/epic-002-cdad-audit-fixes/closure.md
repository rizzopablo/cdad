# Epic epic-002-cdad-audit-fixes — Closure

**Cerrado**: 2026-09-02
**Duración**: 2026-09-02 → 2026-09-02 (sesión única, HITL delegado)

## Resumen

Corrige los 11 bloqueantes + 10 medios de
`findings/audit-consistencia-2026-09-02.md` — una auditoría de consistencia
de toda la metodología CDAD, sus agentes (OpenCode + Claude Code, genéricos
+ Odoo) y skills. El diagnóstico de fondo del informe: no eran bugs
dispersos, era un solo modo de falla repetido (bloques normativos
duplicados en N archivos sin generador ni test que drifteaban). Las 12
features corrigen las instancias concretas y, donde aplicaba, agregan la
verificación automatizada que faltaba para que no vuelvan a driftear en
silencio.

## Features entregadas

| ID | Nombre | Cerrada |
|----|--------|---------|
| 002-001 | single-source-role-contract (nota de perfiles honesta + drift automatizado) | 2026-09-02 |
| 002-002 | single-source-state-schema | 2026-09-02 |
| 002-003 | single-source-gates + wording del gate 4→5 (B11) | 2026-09-02 |
| 002-004 | verdict-tuple en los 4 reviewer + tabla de carga | 2026-09-02 |
| 002-005 | taxonomía del reviewer unificada | 2026-09-02 |
| 002-006 | contradicción property tests + disciplina RED | 2026-09-02 |
| 002-007 | orquestador Claude Code reparado | 2026-09-02 |
| 002-008 | guard anti-bias — perfil premium en Claude Code | 2026-09-02 |
| 002-009 | bash allowlist calibrada | 2026-09-02 |
| 002-010 | higiene de agentes (scribe path, API inventada, stubs, privacidad) | 2026-09-02 |
| 002-011 | validador consolidado (retira aserción auto-invalidante) | 2026-09-02 |
| 002-012 | epic dogfood (este archivo + closure de epic-001 + decisión M10) | 2026-09-02 |

## Criterios de aceptación

- [x] Las 12 features están done en `progress.md`.
- [x] `bash scripts/validate-subagents.sh` → PASS.
- [x] `bash tests/validate-consistency.sh` (nuevo) → PASS (124/124).
- [x] `bash tests/validate-odoo-specialization.sh` → sigue en PASS (141/141, regresión cero).
- [x] Los 4 agentes reviewer producen reporte con `Bucket`/`Abstenciones` sin que el orquestador tenga que corregirlo (verificado en el contenido de los 4 archivos; no se corrió un E2E con un sub-agente real dentro de esta sesión).
- [x] `cdad-test-writer`/`cdad-implementer` no pueden leer/escribir fuera de su scope vía bash (verificado con los mismos probes empíricos del informe) y siguen pudiendo correr su suite sin fricción — mismos probes re-corridos post-fix, mismo resultado esperado.
- [x] El perfil `basic` sigue instalando sin `model:` y ningún documento afirma el anti-bias como garantizado ahí.

## Retrospectiva breve

### Lo que funcionó bien
- El patrón "RED (assert en `validate-consistency.sh`) antes de GREEN (fix)" se sostuvo en casi todas las features — permitió confirmar empíricamente que cada bug descrito en el informe era real antes de tocar código, y que el fix efectivamente lo cerraba.
- Encontrar y corregir dos regresiones en el camino (la postcondición P1 de cdad-003 que exigía `git *` sin acotar; el bug de subshell en `path-guard.sh` que hacía inefectivo el fix C) — ambas se detectaron por correr la suite completa después de cada fix, no se asumieron.
- La calibración explícita del dueño sobre B1 (no ser tan estricto) y sobre el perfil `basic` (no tocar su comportamiento) cambió el diseño de 002-009 y 002-001 respectivamente, evitando un fix técnicamente "más completo" pero que hubiera ido contra cómo el dueño usa la herramienta en la práctica.

### Lo que se complicó
- Varias aserciones de `validate-consistency.sh` fallaron por bugs del propio arnés de test (comentarios explicativos que contenían literalmente el patrón que se buscaba evitar, case-sensitivity en regex, helpers no copiados al nuevo script) antes de capturar el bug real — cada una se detectó y corrigió en el momento, pero es fricción que un harness más maduro (compartido entre `validate-consistency.sh` y `validate-odoo-specialization.sh`, en vez de duplicado) evitaría.
- F001 y F003 originalmente se plantearon en el plan como "un archivo único que los demás citan" — en la práctica, dos de los tres archivos involucrados (los agentes orquestador) son prompts autocontenidos que no pueden citar una reference externa sin una llamada a herramienta adicional. El diseño real terminó siendo "contenido corregido + verificación de identidad automatizada", no "un solo archivo fuente" — más fiel a como ADR-007 ya lo describía.

### Aprendizajes para futuros epics
- Cuando el plan de un epic supone un cambio arquitectónico (como "un archivo cita a otro") sobre algo que no se auditó al nivel de detalle de "¿este archivo es un prompt autocontenido o una reference progresiva?", vale re-chequear esa premisa al ejecutar la feature, no forzar el diseño original.
- Los harnesses de test bash (`bash_section`, `assert_string_not_has`, etc.) deberían vivir en un solo archivo `tests/lib.sh` compartido, no copiados entre `validate-odoo-specialization.sh` y `validate-consistency.sh` — es exactamente el mismo anti-patrón de duplicación que este epic pasó el día corrigiendo, ahora en la capa de tests. Queda como deuda.

## Deuda técnica que se llevó

- El harness de test bash duplicado entre los dos scripts de `tests/` (ver aprendizaje arriba) — no se consolidó en este epic, cambia el layout de dos features históricas (cdad-002, cdad-003) sin beneficio directo a los 21 hallazgos que este epic corrige.
- `activeContext.md` no tiene entries retroactivas para cdad-005..009 (detectado durante el cierre, no backfilleado — ver esa entry).
- Ningún E2E real con un sub-agente delegado corriendo en runtime (OpenCode `task`/`delegate` o Claude Code `Agent`) verificó los fixes de 002-004/002-005/002-009 en ejecución — la verificación fue estática (contenido de los archivos de agente) más los probes directos de `path-guard.sh`. Dogfood real queda para cuando se ejecute la próxima feature con estos agentes.

## Decisiones arquitectónicas tomadas

Sin ADRs nuevos — los fixes de este epic corrigen drift de contenido y cierran huecos de verificación sobre decisiones ya tomadas (ADR-001, ADR-002, ADR-007, ADR-008), no introducen decisiones arquitectónicas nuevas.

## Notas finales

Sesión con delegación HITL completa (`docs/.cdad-state.json` campo
`hitl_delegation`, `requested_by: Pablo`, `requested_at: 2026-09-02`). La
severidad de los hallazgos no se relajó por la delegación (mismo criterio
que un humano, per AP-15) — cada fix quedó respaldado por una aserción
verificable en `tests/validate-consistency.sh`, no por juicio no
verificado.
