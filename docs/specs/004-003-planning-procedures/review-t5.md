# Review — T5 «Equivalencia y re-entry (G1–G3; PD-5/6/7/10; D4)»

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-25>`.
> Paquete: `004-003-planning-procedures-reviewer-review-008`.
> **Dictamen: contenido fiel (0 bloqueantes del GREEN); F1 y F2 son condiciones
> de cierre de feature; F3–F7 opcionales/nits; desviación PD-15 del test-writer
> ACEPTADA.**

**Contrato:** `spec.md` sha256 `ba395fed…bf766` verificado por ejecución ✓ · **Diff:** `cf8963a..b881235`.

## Evidencia

1. `sha256sum …/spec.md` → ✓.
2. `git log --oneline cf8963a..b881235` → `e851974` (docs RED), `b881235` (GREEN). `git show --stat cf8963a` → el RED contiene **solo** el test (+409). Aislamiento RED→GREEN ✓.
3. `git show cf8963a:<3 docs> | grep -ci equivalenc` → **0/0/0**; la base de SKILL tiene **0** hits de "new hypothesis" → RED genuino (6 fallos esperados; 2 controles D4 ya verdes en la base).
4. `pytest tests/test_004_003_t5_reentry_equivalence.py -v` → **8 passed**. `pytest tests/ -q` → **364 passed** (356 previos + 8; consistente con los 356 verificados en T4).
5. `make validate` → **FAIL: 2 asserts** (F011: drift de install + A3).
6. `diff <head> ~/.config/opencode/skills/.../re-entry.md` → la copia instalada **carece de toda la sección de T5** (y también del contenido de T2: falta `reviewer-plan-review.md` y el enum `draft-plan`) → la deriva **precede a T5, que la profundiza**.

## Hallazgos

### F1 — Criterio de aceptación §4.4 (PD-5/PD-6 "se ejercita") sin caso de flujo ejercitado · BLOCKING (cierre de feature) · bucket h

La spec §4.4 exige que la regla de equivalencia *"se ejercita con al menos un caso de flujo consecutivo donde se cita una corrida previa y uno donde un cambio material fuerza una corrida nueva"*. La trazabilidad del plan pone PD-5/6 → **T5 solo**. Los 8 tests entregados son **oráculos de marcadores textuales**; **ninguno ejercita un flujo** (no hay fixture "mismo árbol → citar corrida previa pasa sin re-ejecutar", ni "cambio material → corrida nueva", ni "reintento idéntico → revisión de estrategia", que la fila T5 del plan declaraba como RED).

**Remedio (decisión del dueño, una de dos):** (a) enmienda de RED que ejercite el flujo sobre una superficie ejecutable real, o (b) re-mapeo explícito del criterio §4.4 al recorrido real de T7, actualizando la trazabilidad del plan en el mismo cambio coherente.

### F2 — PD-12 "llega a la instalación": la regla T5 no está instalada y ningún plan-row promulga la instalación · BLOCKING (cierre de feature) · bucket h

El producto instalado no contiene la sección de equivalencia. El plan no asigna la reinstalación a ninguna tarea; T7 instala solo en **raíz aislada**.

**Remedio:** asignar explícitamente el paso de promulgación con `install.sh --check` verde como evidencia. *Nota del orquestador:* el target es **raíz aislada** (regla del handoff: nunca instalar en HOME real), así que la evidencia es la instalación aislada de T7, no los mirrors de `$HOME`.

### F3 — `make validate` rojo (F011: drift + A3) · BLOCKING como condición de cierre, no del GREEN · bucket h

- **Drift (F011-A):** preexistente y cubierto por F2.
- **A3 (F011-B):** el patrón local no acotado matchea "PROPONE" en `tests/test_role_packets.py:49` (archivo intacto desde `c50f521`, 004-002); los hits de `__pycache__` son subproducto de correr pytest. Ningún archivo de T5 aparece en los hits. **Remedio:** acotar el patrón a palabra completa y limpiar `__pycache__` antes del publish-scan — deuda del check, no de T5.

### F4 — Nit · OPTIONAL · bucket m

`re-entry.md:16` etiqueta a `SKILL.md` como "derived consumer … never copy it", pero G3 hace de `SKILL.md` **co-dueño canónico** de la regla de dos intentos y `SKILL.md:277` **sí contiene** ese párrafo. La regla de equivalencia en sí no está copiada en ningún consumidor ✓. Riesgo: un mantenedor podría borrar el párrafo co-canónico y romper `test_g3_skill_md_carries_orchestrator_conduct`. **Remedio:** reformular a "SKILL.md is co-owner of the two-attempt rule; it references — never copies — the equivalence clause".

### F5 — Nit · OPTIONAL · bucket m

`SKILL.md:277` replica la regla de reintentos sin puntero a `re-entry.md`; los dos dueños divergen levemente. **Remedio:** añadir "(reconciled with `references/re-entry.md`)".

### F6 — Optional/Consider · OPTIONAL · bucket m

Sobre "¿accionable o decorativo?": la regla **es accionable como procedimiento declarativo** (dimensiones enumeradas, discriminador "el mismo commit ≠ entorno equivalente", forzado de corrida, declaración de incertidumbre) — no es pura prosa. Pero "shown equivalent" / "materialmente cambiado" no define comparadores concretos. **Remedio:** anclar comparadores verificables (HEAD + árbol sin commitear diffable; `policy_sha256` ya existe; manifiesto de entorno) y un ejemplo de línea de cita `path+line+commit`.

### F7 — FYI · bucket l

`current_stage` quedaba en `tdd-red-t5` en el commit del GREEN; higiene de estado del orquestador, no defecto.

## Disposición de la desviación declarada del test-writer (PD-15) — ACEPTADA

La salida de los tests fallidos expuso fragmentos de los documentos a escribir. Disposición: **no compromete ningún invariante**. (1) El invariante 3 protege la dirección test-writer→implementador; que el implementador reciba el oráculo publicado de RED es TDD clásico. (2) El oráculo se fijó **antes** de la exposición (test commiteado en `cf8963a`, antes del GREEN; base verificada sin los marcadores → RED genuino). (3) Ningún hallazgo depende de la desviación. **Recomendación no bloqueante:** en REDs futuros usar rótulos abstractos de marcadores en los mensajes, y que el orquestador no pegue salida cruda de RED en paquetes GREEN.

## Auditoría test↔postcondición (segunda sesión, obligatoria)

8/8 tests mapean a PD-5/G1, PD-6/G1, PD-7, PD-10/G3 (re-entry), PD-10/G3 (SKILL), G2 (stage-3) y PD-12/invariante 6 (D4 ×2, controles declarados verdes en RED, corroborado en la base). **Superfluos: ninguno.** Ningún test usa mocks ni estructura interna (cero código). Lectura de `tests/.sensitive-patterns.local`: confirmada ausente.

## Abstenciones

1. No reprodujo el estado RED (requeriría worktree base; read-only). Mitigado con evidencia estructural.
2. Preexistencia exacta del fracaso A3: el archivo señalado está intacto desde 004-002; el historial del archivo local de patrones no es verificable.
3. Contenido exacto del paquete GREEN: fuera de alcance; la disposición se basa en la desviación auto-declarada y la cadena de commits verificable.

## Resumen

El contenido del GREEN es **fiel** a las dimensiones exigidas por el contrato (PD-5/6/7/10/G2), **no copia** la regla en consumidores derivados, y la desviación del test-writer queda **aceptada sin remedio bloqueante**. **F1 y F2 son las dos decisiones a resolver antes del cierre del feature; F3 es condición de cierre; F4–F7 a deuda.**
