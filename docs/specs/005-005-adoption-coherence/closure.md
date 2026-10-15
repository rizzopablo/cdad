# Cierre — 005-005-adoption-coherence

**Feature:** `005-005-adoption-coherence` · **Epic:** `epic-005-real-operation`
**Cerrada:** 2026-10-09 · **Aprobada por:** orquestador OpenCode (HITL delegada epic-005)
**Contrato:** `spec.md` sha256 `9349b0c1468de48b4223798e4209a1f16959ff5f0869a39c101ca039f7fe4d22`
(aprobada 2026-10-09; decisiones D1–D8) · **Plan:** `plan.md` (T1–T4)
**Versión de ejecución del ciclo:** instalación global v8 `9396394` (el repo se desarrolla; su CLI no
se usó para operar).

## 1. Resultado

Continuación correctiva de 005-001: **preparar, corregir y despachar un encargo con la versión
esperada y la validación proporcional, sin rodeos manuales.**

- **T1 — el reemplazo valida también lo conservado (PD-1..PD-7, INV-4/INV-5).**
  `prepare --replace-packet` valida el **encargo resultante completo** (campos conservados **y**
  corregidos): cada `input` existe y queda dentro de algún `read_scope`; `read_scope`/`write_scope`
  pasan la política; `invariants`/`evidence_required` no vacíos; `expected_output` no vacío. Todo
  rechazo nombra **campo, motivo y opción** (p. ej. `--input`), sin publicar nada y con el paquete
  anterior byte a byte idéntico; el reemplazo repetido con la corrección funciona. El **camino
  normal de `prepare` no cambia** (PD-5/INV-4): 005-005 no suma restricciones. Commit `65e887f`.
- **T2 — una sola política de tests (PD-8..PD-11, INV-6).** Sección única **«Test evidence policy»**
  en `references/stage-3-tdd.md` (dueño canónico de la política) con los cinco puntos: regresión
  **proporcional al cambio**; **suite completa al cierre** de la feature; **reutilización de
  evidencia registrada equivalente** (dueño canónico de la equivalencia: `references/re-entry.md`
  §«Equivalence of a registered run», referenciada sin copiar su texto); la **metodología define la
  evidencia y el proyecto declara los comandos**; una condición local/entorno se **registra** en la
  evidencia y **no** se vuelve requisito. Consumidores alineados (referencias, paquetes canónicos y
  `SKILL.md`) y **enmienda fechada de PD-17** de 005-001 para que su letra coincida con el recorrido
  ejecutado (con re-registro del pin). Commits `4b990bb` + pin en el state.
- **T3 — procedencia de la instalación y documentación de 005-001 (PD-12..PD-17, INV-7).**
  `prepare` resuelve el origen de los agentes de proyecto **variable > registro de activación
  (`.cdad/activation.json` → `adopted_root`) > global**; una contradicción de origen (variable vs
  registro, o vs el `source_dir` anterior — caso MIX-V6V7) emite un **diagnóstico que nombra el
  registro y las versiones/commits** y dice cómo resolverla, **nunca en silencio**; la **versión es
  verificable desde el artefacto publicado** (`version.txt` en la raíz de la instalación +
  `source_version` en el manifiesto de propiedad y en el manifiesto de agentes). Adaptador de
  OpenCode documentado (recarga y procedencia). Además: `review.md` de 005-001 **normalizada** sin
  repetir la revisión y **rutas personales fuera** de los documentos del epic-005 (originales en el
  registro local `.cdad/local/`). Commits `6f7363c`, `b4ce4d9`, `1f1cc63`.
- **T4 — integración desde una instalación aislada (PD-18, INV-8).** Prueba end-to-end con el CLI
  de una **instalación real del repo en una raíz aislada** (nunca HOME): `prepare`, corrección con
  `--replace-packet` (validación completa) y **despacho con la validación proporcional**, **sin
  rodeos manuales**. El escenario **destapó un defecto real** (la instalación no declaraba su
  versión) y se corrigió (`9e5215f`); el RED del oráculo de versión se corrigió por el test-writer
  (`eda293c`). Commits `012ccac`, `eda293c`, `9e5215f`.

## 2. Gate de cierre

- **Suite completa:** `env -u TMPDIR python3 -m pytest tests/ -q -p no:randomly` →
  **649 passed, 0 failed** en `0d363f6` (12m29s; los commits posteriores son solo `docs/`: review,
  Memory Bank, ADR, deuda y state — ningún test los lee).
- **Focales de la feature:** T1 6, T2 6, T3 3, T4 5 → verde; regresiones del área (instalador,
  derivados, política, 005-001) verdes.
- **`make validate`:** 141 PASS / **2 FAIL F011 preexistentes** (drift de HOME vs repo;
  patrón sensible A3), ajenos al diff (R6).
- **Condición local registrada (no requisito):** la suite se corrió con `env -u TMPDIR`
  (condición del VPS, anotada en la evidencia).
- **Sin CI** (deuda declarada del epic).

## 3. Review formal (stage 4)

Una **única** review formal (`review.md`), que cubre T1–T4:
**veredicto `changes-approved` — SIN BLOQUEANTES.** Confirmó el pedido del dueño
(`handoff-005-005.md` §4): 005-005 **elimina contradicciones y trabajo manual sin sumar
restricciones** al camino normal de `prepare`, y separó **principio de CDAD / decisión del
proyecto / particularidad del entorno**. Verificación propia del reviewer: suite 649 passed,
focales/regresiones OK, `make validate` con los 2 F011 preexistentes.

- **5 opcionales → deuda** (`debt.md`): O1 registro de activación ilegible (caída silenciosa);
  O2 «versión desconocida» no explícita; O3 PD-1 sin subtest de sus rebanadas no-input;
  O4 `CDAD_OPENCODE_AGENTS_DIR` no esterilizada en el env de los tests T1; O5 instalación v8
  vigente con `source_version: null` (anterior al marcador; cierre post-despliegue del dueño).
- **Abstenciones declaradas** (5): MIX-V6V7 real de producción no reproducido; `opencode reload`
  en la 2.0.22 del dueño sin evidencia; VERIFY de D7 abierto; O1 por lectura; clasificación del
  runner `unittest`.

## 4. Registro y trazabilidad

- Paquetes y sesiones: `dispatch-ledger.md` (filas 1–12 + startup).
- Producto: T1 `65e887f`; T2 `4b990bb`; T3a `6f7363c`; T3b `b4ce4d9`+`1f1cc63`; T4 `9e5215f`.
- Tests: `dc66cb2`, `3d9e854`, `fd1aaa3`, `012ccac`, `eda293c`.
- Docs: discovery, spec+plan (pin `9349b0c1…`), review (`9b6f592a…`), Memory Bank (`e3c837e`),
  ADR-020, deuda.
- Receipts durables: `architect-draft-001`, `reviewer-review-001`, `scribe-memory-001`
  (materializados con CAS).
- `stage_history`: `discovery`, `specification` (con pin), `tdd-red/green-t1`, `tdd-red/green-t2`,
  `tdd-red/green-t3a`, `tdd-green-t3b`, `tdd-red/green-t4`, `tdd-red-t4-fix`, `review-1`,
  `merge-memory-bank`, `feature-closure`; más el re-registro del pin de 005-001.

## 5. Limitaciones y deuda

- **O5 (dueño):** la instalación viva (v8) es anterior al marcador de versión: su manifiesto
  declara `source_version: null`. La versión nueva sí lo declara; **desplegarla es tarea del
  dueño** (fuera del ciclo).
- **`opencode reload`:** no verificado en el servidor permanente del dueño (2.0.22); documentado
  como NO verificado (D6/PD-15).
- **VERIFY de D7:** confirmar con el dueño si `~/.claude`/`~/.agents`/`~/.config/opencode` en
  `handoff-opencode.md:63` y `execution.md:21` deben retirarse también.
- **O1..O4** (opcionales) — detalle en `debt.md`.
- **Sin CI**; `make validate` con 2 FAIL F011 preexistentes.

## 6. Estado al cerrar

`epic_features[005-005].status = "done"`; la ejecución queda en reposo legítimo
(`active_feature: null`, `current_stage: "idle"`, binding `execution` conservado) →
`validate-state` → `VALID: idle`. El epic-005 sigue activo (`features-loop`).
**005-002 no se abre por anticipado:** depende de 005-005 **y de la adopción de su versión**
(despliegue del dueño).
