# Review — cdad-010-opencode-permissions

> Etapa 4, Capa 1 · 2026-09-13 · Reviewer: qwen3.7-plus (familia distinta al
> implementer deepseek-v4-flash ✓). Materializado por el orquestador desde el
> output textual del rol (Contrato de roles §5) — feedback íntegro, sin editar.

Familia de modelo: **qwen3.7-plus** (implementer: deepseek-v4-flash — familias distintas ✓)
Bucket de sesión: **h** — puntos: **4/4** (+1 familia de modelo distinta al implementer; +1 diff completo `b352bf6..HEAD` en contexto — 23 archivos revisados, incl. los 11 frontmatters completos, install.sh, generador, docs; +1 rationale con cita exacta `archivo:líneas`; +1 spec + VALIDATION + test-audit + systemPatterns + ADR-009 + validate-consistency.sh en contexto).

**Enmiendas evaluadas:** G9 (enmienda de fila: `go version` DENEGADO es diseño correcto según P4 — corroborada por probe-B del RED) y G14 (misreport del modelo, no del runtime; log con cero evaluaciones + re-test con evaluación loggeada) — **ambas justificaciones válidas, bien documentadas** (VALIDATION.md:156-174). Los pares repo↔copias instaladas verificados por muestreo directo: `~/.config/opencode/agents/*.md` tienen `permission.write: ask` anidado (línea 14-18) y las copias de writers llevan pares derivados completos (`rtk go vet*`, `rtk gofmt *`, `rtk npm test*`) — coherente con Fase 1 (`--check` PASS contra expectativa derivada).

## Hallazgos

### H1: El commit fix(agents) 5f9f4d2 modificó el artefacto de tests (run-checks.sh A1) fuera de rol
- Veredicto: **BLOQUEANTE**
- Bucket: h
- Rationale: el commit `fix(agents): cdad-010 P1 — palanca write:ask ANIDADA... + A1 actualizado` mezcla el cambio de implementación (10 agentes) con la edición del script de verificación (run-checks.sh:86-96, grep `^write:` → `^  write:`). Es un commit de firma implementer tocando un test — exactamente la trampa que AP-4 y el contrato de roles previenen (el implementer ajusta su propio test para pasar). El hallazgo de fondo es legítimo (probe demostró que `write` top-level es inerte: KNOWN_KEYS), pero el proceso exige: enmienda al spec (P1 sigue describiendo la clave sin precisar anidamiento; spec.md sin cambios post-aprobación), registro de la desviación como G9/G14 (que sí se registraron — esta no), o la edición vía sesión test-writer. Ninguna de las tres ocurrió.
- Provenance: `git show 5f9f4d2` (toca `docs/specs/cdad-010-opencode-permissions/run-checks.sh` 7+/3- junto a 10 agentes) + run-checks.sh:86-96 + spec.md:54-61 (P1 sin enmienda) + VALIDATION.md:156-174 (G9/G14 registradas; esta no). Convención: cdad-cycle Contrato de roles §2 (implementer NO toca tests), Gate 3→4 ("cada test modificado tiene justificación explícita en spec.md"), AP-4.

### H2: Sin re-corrida estática registrada tras el último cambio de código — la evidencia "174/174" corresponde a un árbol previo
- Veredicto: **BLOQUEANTE**
- Bucket: h
- Rationale: la única corrida de run-checks registrada (174 PASS / 0 FAIL, VALIDATION.md:96) es previa a 5f9f4d2 (commit que cambió los 10 agentes Y el assert A1). El checklist marca criterio 1 "[x] run-checks.sh todo PASS — 174/174" (VALIDATION.md:181) y el state file repite "run-checks 174/174" para el árbol final, sin output pegado post-fix. Regla de Oro: "seems right" no cierra gates; la evidencia se pega, no se describe. Cierre trivial: una corrida post-5f9f4d2 con output pegado (presupuesto 0: solo si el árbol volvió a cambiar).
- Provenance: VALIDATION.md:96 y :181 + orden de commits 9c6e1c3 (evidencia) < 5f9f4d2 (cambio) < f2c1425 (HEAD) + `docs/.cdad-state.json:101` (green_note). Regla: cdad-cycle Verification §Reglas de evidencia 1-3; Gate 4→5 "suite sigue verde tras los fixes".
- Nota de agregación: H1 y H2 son del mismo bloque/commit (κ-dedupe → 1 bloque independiente efectivo para el diagnóstico de drift; se reportan separados porque las resoluciones difieren).

### H3: `"find *": allow` es un backdoor bash de escritura/ejecución en los roles read-only
- Veredicto: **BLOQUEANTE**
- Bucket: h
- Rationale: el patrón `find *` matchea la invocación completa del comando: `find . -name '*.py' -delete` (borrado arbitrario — escritura) y `find . -name x -exec sh -c '...' \;` (ejecución arbitraria) resuelven a allow bajo el catch-all-deny, en los 6 roles read-only (architect/reviewer/scribe + odoo) cuya allowlist P4 declara "de SOLO lectura... sin backdoor bash de escritura". El generador repite el vector en TODAS las copias derivadas (`emit_base_allow` es común a todos los roles). El vector preexiste a cdad-010, pero esta feature reescribió estos bloques afirmando explícitamente el invariante "solo lectura", cerró los proxies análogos (`rtk find*` deny en writers) y A6 solo assertiona `sed -i`/`tee` — el riesgo de seguridad de la matriz no admite excepciones. Desestimación solo con motivo escrito del dueño; el fix es restringir find a formas acotadas o moverlo tras un patrón sin `-exec/-delete` (el matcher no permite negación por flag → elimina el patrón o acepta el riesgo documentado en ADR).
- Provenance: `agents/cdad-architect.md:34`, `cdad-reviewer.md:41`, `cdad-scribe.md:39`, `cdad-architect-odoo.md:37`, `cdad-reviewer-odoo.md:38`, `cdad-scribe-odoo.md:37` + `scripts/cdad-bash-allowlist.sh:153` + run-checks.sh:213-214 (A6 no cubre find). Ref: spec P4 (líneas 112-113, "sin backdoor bash de escritura"), matriz de severidad (riesgo de seguridad = bloqueante sin excepciones).

### H4: Excepciones de lectura de tests colocados incompletas (test-writer puede escribir pero no releer .spec/.mjs/.cjs colocados)
- Veredicto: **BLOQUEANTE**
- Bucket: h
- Rationale: P2 exige que `read` agregue "las mismas excepciones de lectura para tests colocados bajo `src/**`/`lib/**`". El `edit:` de test-writer permite `**/*.test.mjs`, `**/*.test.cjs`, `**/*.spec.ts`, `**/*.spec.js` colocados, pero el `read:` solo agrega excepciones para `*_test.go`, `test_*.py`, `.test.js`, `.test.ts` (agents/cdad-test-writer.md:23-28; idéntico en test-writer-odoo:26-31). Consecuencia funcional: el test-writer crea `src/foo.spec.ts` (edit allow) y no puede releerlo con Read (`src/**: deny` gana por findLast). Divergencia del spec (spec no desactualizado) + el assert A4 de lectura (run-checks.sh:181-182) sub-cubre (solo verifica el glob Go), por lo que el check no detecta el hueco.
- Provenance: spec.md:73-74 (P2 "mismas excepciones") vs agents/cdad-test-writer.md:19-28 y cdad-test-writer-odoo.md:20-31 + run-checks.sh:181-182. Matriz: divergencia del spec → bloqueante; bug funcional de alcance acotado.

### H5: Documentación/comentarios stale sobre la ubicación de la palanca (dicen "top-level"; la implementación final es anidada)
- Veredicto: **OPCIONAL**
- Bucket: h
- Rationale: 5f9f4d2 movió la palanca a `permission.write` anidado pero no actualizó: `docs/systemPatterns.md:56` ("declaran `write: ask` a nivel top del frontmatter") y `:78` ("única excepción... `write: ask` top-level"), que además se contradicen con el propio párrafo interno :73-74 (el clasificador lee SOLO el bloque anidado); y los comentarios heredados en `agents/cdad-reviewer.md:26` y `cdad-scribe.md:25` ("la palanca es el `write: ask` top-level de arriba" — arriba hay `edit: deny`, no write). systemPatterns es la referencia de la regla de vigilancia: una instrucción de ubicación falsa puede hacer que un mantenedor futuro "restaure" la palanca top-level (inerte) y revierta task-ability sin darse cuenta. Sin impacto runtime hoy.
- Provenance: docs/systemPatterns.md:56 y :73-78 vs agents/cdad-architect.md:19 / cdad-reviewer.md:20 (palanca anidada) + run-checks.sh:86-89 + agents/cdad-reviewer.md:25-27, cdad-scribe.md:24-25. Ref: P6 ("convención documentada con motivo").

### H6: Default agnóstico del repo con allows sin par rtk (npm test/run, go vet/build, gofmt)
- Veredicto: **OPCIONAL**
- Bucket: h
- Rationale: ADR-009 punto 1: "toda entrada `X*: allow` de bash lleva su par `rtk X*: allow`". Los .md del repo declaran `npm test*`, `npm run*`, `go vet*`, `go build*`, `gofmt *` SIN sus pares (agents/cdad-implementer.md:65-71, cdad-test-writer.md:80-86) — el generador sí los emite (scripts/cdad-bash-allowlist.sh:160-183) y las copias instaladas de esta máquina están completas (verificado). Riesgo residual: el default del repo es el fallback si un agente corre sin install derivado — reaparecería la fricción exacta que P4/ADR-009 eliminan. Fix mecánico: agregar los 5 pares faltantes.
- Provenance: agents/cdad-implementer.md:65-71, cdad-test-writer.md:80-86 vs docs/adr/ADR-009-politica-rtk-allowlists.md (Decisión punto 1) + scripts/cdad-bash-allowlist.sh:160-183. Ref: P4 ("pares X* + rtk X* para los comandos de suite").

### H7: Cobertura empírica de P1 incompleta — 3 variantes odoo read-only sin ningún probe runtime
- Veredicto: **OPCIONAL**
- Bucket: h
- Rationale: P1 exige probe de task "para cada uno" de los 10. Los probes indirectos cubren 7/10 (test-writer G1-G6, implementer G7-G9b, architect G10, reviewer G11-G12, scribe G13, test-writer-odoo G14, implementer-odoo G15 — todos requerieron task aceptado). `cdad-architect-odoo`, `cdad-reviewer-odoo` y `cdad-scribe-odoo` no tienen probe alguno; están cubiertos estáticamente (A1/A6) y son estructuralmente idénticos a sus pares base probados, por lo que el riesgo es bajo — pero la verificación declarada del spec no está 100% evidenciada.
- Provenance: spec.md:58-59 (P1 "para cada uno") vs VALIDATION.md:113-135 (matriz sin filas para las 3 variantes odoo read-only) + run-checks A1/A6 (cobertura estática de los 10). Criterio de aceptación 2.

### H8: Código muerto en run-checks.sh (loop de aserción sin cuerpo)
- Veredicto: **OPCIONAL**
- Bucket: h
- Rationale: run-checks.sh:155 contiene `for forb in '"rtk read\*"... ; do :; done` — un loop que no hace nada (residuo de la iteración RED). Cosmético; sugiere que un patrón previsto se verificó por otra vía (156-167) y quedó el esqueleto. Limpieza menor, sin efecto en resultados.
- Provenance: run-checks.sh:155. Ref: limpieza del artefacto de tests (convención general).

## Abstenciones
ninguna

## Resumen
**4 bloqueantes** (H1/H2 mismo bloque-commit 5f9f4d2 → 3 bloques independientes efectivos) · **4 opcionales** · **0 abstenciones**

Lo que sustenta lo que NO encontré (explícito): revisé el diff completo de los 10 agentes + orquestador contra P1-P4 y no hallé catch-all en posición incorrecta, ni `ask` en claves runtime (A2/G6/G16), ni `"rtk *": allow` ni `"rtk git *": allow` en ningún rol, ni `sed`/`tee` en read-onlys; los denies `rtk err*`/`rtk summary*` y el orden catch-all→específicas (findLast) están presentes en los 10 frontmatters; P5 verificado (generador rol×stack, invocado por install.sh, FORBIDDEN odoo respetado — sin go/python crudos en variantes odoo, pylint conservado); P6 completo en los 4 archivos + ADR-009; cero diff en `agents/claude-code/`; repo↔copias coherente (--check derivado PASS + muestreo directo de `~/.config/opencode/agents/`); F009 sin roturas (el "sin go test*" de F009 solo aplica a read-onlys genéricos — validate-consistency.sh:179-184 — y se cumple).

Veredicto global: **RECHAZADO** — los 4 bloqueantes son mecánicos y baratos de cerrar (enmienda de spec + registro AUDIT para la palanca anidada, una corrida de run-checks pegada, 5 pares rtk + restricción/eliminación de `find *` en lectores, 4 globs de lectura en test-writer); con ellos resueltos + los opcionales priorizados por Capa 2, la feature está en condiciones de avanzar a Etapa 5.

## Capa 2 — Priorización (usuario)

**Política de enforcement del dueño (Pablo, 2026-09-13, transcripta):**

> "No vamos a ser tan estrictos porque si no es infinito. La idea es bloquear
> las opciones más directas y evidentes, y dejar claro en los skills y demás
> archivos de procedimiento lo que debe y lo que no debe hacer el agente y
> para qué. Un agente con ganas de saltar las vallas siempre encontrará cómo
> hacerlo. Lo que queremos es que el agente *sepa* lo que esperamos de él y
> que si no hace lo que esperamos debe tener un motivo válido para nosotros
> que pueda explicar, o debe devolver la tarea explicando por qué no puede
> cumplir con su objetivo. Si un agente cumple una tarea sin respetar el
> protocolo, se considera que no cumplió la tarea, falló."

Derivados para reviews futuros: (1) bloquear vectores directos y evidentes,
no bypasses hipotéticos; (2) la expectativa se documenta en skills/
procedimientos (qué, qué no, y por qué); (3) violación de protocolo sin
motivo válido = tarea NO cumplida aunque el artefacto exista; (4) el agente
cumple o devuelve la tarea con explicación — nunca cumple violando en
silencio.

**Aplicación a los hallazgos:**

| Hallazgo | Decisión | Motivo |
|---|---|---|
| H1 | Resolver vía docs: enmienda spec P1 (palanca anidada) + registro de desviación en VALIDATION | La palanca anidada es el diseño correcto, verificado empíricamente (G-series); re-hacer el commit vía otra sesión sería strictness infinito. La violación de proceso queda REGISTRADA como precedente; bajo la política del dueño, una violación así futura = tarea fallida. |
| H2 | APLICAR (bloqueante) | Evidencia pegada post-fix es barata y es la Regla de Oro. |
| H3 | APLICAR (bloqueante) | `find -delete`/`-exec sh` es exactamente un vector "directo y evidente" — la filosofía del dueño lo CONFIRMA como bloqueante (coincide con matriz: seguridad sin excepciones). Fix: eliminar `"find *": allow` de los roles + generador. |
| H4 | APLICAR (bloqueante) | Divergencia mecánica del spec P2; fix de globs de lectura. |
| H5 | APLICAR | Docs stale contradicen la filosofía del dueño (expectativas claras de dónde vive la palanca); fix mecánico de docs + comentarios. |
| H6 | APLICAR | 5 pares rtk faltantes en default del repo; mecánico. |
| H7 | DESESTIMADO con motivo | Variantes odoo read-only estructuralmente idénticas a sus pares base probados en runtime + cobertura estática A1/A6 de los 10; el mecanismo de clasificación del plugin es por-config (idéntico entre pares), no por-nombre. Registrado como desviación aceptada en VALIDATION. |
| H8 | APLICAR | Limpieza trivial del loop muerto; se hace junto con los asserts de H3/H4. |
