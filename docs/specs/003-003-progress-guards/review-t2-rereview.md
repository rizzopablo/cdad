Revisión completa. Resumen final:

---

# Review T2 re-fix — `003-003-progress-guards` (F1 puntos 1-5, enmienda del dueño)

**Objeto:** diff `2204bab..dbe48e8` (RED `1ebe1a8` + GREEN `dbe48e8`) contra `docs/specs/003-003-progress-guards/spec.md` (sha256 verificado = `731cca5b…c5`, coincide con el packet) y `review-t2-decision.md` (puntos 1-5 + enmienda: fuera de raíz = allow honesto, preflight consultivo).

## Evidencia de ejecución (comandos exactos, read-only)

- `git log --oneline 2204bab..dbe48e8` → 6 commits; alcance: `dbe48e8` = solo `skills/cdad-cycle/scripts/cdad_guard.py` ✓ (raíz de implementación declarada); `1ebe1a8` = solo `tests/test_003_003_t2_preflight.py` + `tests/test_003_003_t2_reviewfix.py` ✓; los 4 commits de docs + `.cdad-state.json` son bookkeeping del orquestador ✓. Spec y `docs/cdad-policy.json` **sin cambios** en el rango ✓.
- `sha256sum docs/specs/003-003-progress-guards/spec.md` → `731cca5bc149…` = contract ✓.
- RED re-verificado en worktree en `1ebe1a8` (creado en `/tmp/opencode`, removido al terminar): `pytest tests/test_003_003_t2_reviewfix.py -q` → **5 failed, 1 passed in 1.03s** (fallan puntos 2-5; el caso positivo pasa trivialmente como precondición). Suite **no repetida** en dbe48e8 según instrucción.
- GREEN focal (HEAD tree): `pytest tests/test_003_003_t2_reviewfix.py -q` → **6 passed in 1.48s**; regresión T2: `pytest tests/test_003_003_t2_preflight.py -q` → **4 passed in 1.23s**. Aritmética de cobertura: 453 (T2) + 6 reviewfix = 459 ✓ — ningún test perdido.
- 2 sondas sintéticas en `/tmp/opencode/f2p` (proyecto propio, sin incidente real, P6; removido): travessía intra-raíz `secrets/x/../y` normaliza y deniega por rol-scope rc=1 ✓; orden de negación private→rol intacto (OP_PRIVATE en suite) ✓.

## Cierre de los puntos 1-5 (verificado contra el código, no por confianza)

| Punto | Veredicto | Ubicación |
|---|---|---|
| 1. Fuera de raíz ⇒ allow honesto «outside project root: not governed by project policy», nunca «within the declared scope» | **cerrado** | `cdad_guard.py:376-392` + focal F1-P01 (../ y abs) |
| 2. Sin destino resoluble (bash, sin path) ⇒ `unknown` rc=0, reason honesto | **cerrado** | `cdad_guard.py:377-385` + F1-P02 |
| 3. `read_scope` consultado para lecturas; deny role-scope; legítimo sigue allow | **cerrado** | `cdad_guard.py:394-413` (`scope_key`) + F1-P03 + positivo |
| 4. Política con shape inválido ⇒ rc≠0 «policy invalid»; ausente ⇒ vacía declarada | **cerrado** | `validate_policy` 299-315, llamado en 492-497 + F1-P04 (a/b/c) |
| 5. `--role` ≠ `exec_context.role` ⇒ rc≠0 con diagnóstico | **cerrado** | `cdad_guard.py:511-519` + F1-P05 |
| O-B (docstring tiempo-RED) | **cerrado** | `test_003_003_t2_preflight.py` docstring actualizado post-GREEN |
| O-D (limitación declarada en contrato) | **cerrado** | docstring del módulo («O-D limitation (declared, low debt)») |
| O-A, O-C | deuda baja declarada — sin cambios, correcto | — |

## Hallazgos

### Bloqueante de producto: ninguno

### Bloqueante de evidencia de proceso

**E1 — El RED del review-fix no está registrado como despacho de test-writer.** El ledger (`dispatch-ledger.md`) salta de fila 15 (reviewer) a fila 16 (implementer `green-t2rf-a1`, que declara «Focales 20/20 sin commitear»); no hay fila test-writer para el RED `1ebe1a8` (22:50:22, 1 min después del doc de calibración — cronología plausible pero no evidencia), ni entrada `tdd-red-t2-reviewfix` en `stage_history` de `docs/.cdad-state.json`. El commit RED respeta la disciplina de escritura del test-writer (solo tests), pero la **separación de sesiones no es verificable desde la evidencia registrada** — invariante central del ciclo (anti-gaming). El conteo «20/20» de la fila 16 tampoco concilia con lo observable (4+6 tests = 10). Cierre verificable: registrar la fila de despacho del RED (test-writer/modelo/sesión) + entrada de stage, o producir la evidencia del despacho. **Veredicto: BLOCKING** · **Bucket: m** · No afecta el veredicto del código; es un gate de evidencia barato de cerrar.

### Requeridas (no bloqueantes — deuda declarada, hecha concreta; no re-abiertas)

- **R1 — Sobre-deny de lecturas legítimas con contextos sin `read_scope` usable.** Con el contexto de este propio packet (`read_scope: [{"class":"repository-read"}]` — entradas clase-sin-`root/path`), `_scope_targets` (`cdad_guard.py:331-343`) no extrae ningún target ⇒ **toda lectura dentro de la raíz se deniega rc=1** (deny de operación legítima, familia C4). Es exactamente la calibración que el dueño difirió a T5 («no la reabras»): la registro concreta con evidencia, **Veredicto: OPTIONAL (mapped a la deuda de calibración declarada)** · **Bucket: m**.

### Opcionales (bucket l, sin prolongar)

- **O-1** Docstring de `_root_relative` (`cdad_guard.py:270-276`) conserva «fails closed to "outside"» — tras la enmienda, «outside» = allow; la frase confunde fail-closed con la nueva semántica. Reescribir.
- **O-2** `validate_policy` solo se ancla en el borde CLI (`_cmd_preflight:494`); `evaluate_preflight` invocado como función de biblioteca sigue fail-open ante shape inválido (F1-E latente fuera del CLI). Remedio: llamar `validate_policy` dentro de `evaluate_preflight` o documentar la obligación del caller.
- **O-3** `private_paths` mal ubicado (nivel superior del policy, fuera de `path_policy`) se ignora silenciosamente por `_private_paths` (318-328) — fail-open adyacente a F1-E fuera de las condiciones de cierre acordadas; sugerencia: advertencia de claves desconocidas en `validate_policy`.
- **O-4** Docstring del reviewfix dice «Cada aserción es AssertionError contra… 2204bab», pero el caso positivo (1 de 6) pasa trivialmente en RED (verificado: 5/6). Precisión del mapping test↔postcondición.
- **O-5** `spec.md:221` (D6) conserva la semántica pre-enmienda («…o fuera de raíz»); la enmienda vive solo en `review-t2-decision.md` — un futuro lector de la spec señalaría falsamente el allow-out-of-root como violación. Registrar el addendum en stage 5 (scribe).

## Verificaciones positivas (con evidencia)

RED genuino (5/6 failed en `1ebe1a8`, verificado por mí en worktree); GREEN limpio (6/6 + 4/4 de T2); alcance de archivos exacto en ambos commits; enmienda aplicada sin tocar spec/policy; orden private→role-scope y normalización de travessía intactos; sin traceback ni salida parcial en las rutas rc=2; `denied_by` solo en deny, honesto en la vía deny; ningún consumidor de `evaluate_preflight` fuera del CLI (sin regresión de API).

## Abstenciones

- **Fricción real de integración (T5):** fuera de este diff; la calibración fina es deuda declarada por el dueño — no la re-abro (R1 es su concreción, no su re-apertura).
- **Rendimiento:** O(n·m) sobre listas pequeñas; sin hot path medible ni medición — no afirmo.
- **`--project-root` relativo:** no probado (retiene la abstención de review-t2; el runner actual usa rutas absolutas).
- **Prevalencia real de entradas clase-sin-root en contextos de ejecución:** el mismatch está verificado en código con la forma que el propio packet declara; no relevé exhaustivamente los contextos en `.cdad/` — cuantificación insuficiente.
- **Contenido de la sesión GREEN del implementer (`ses_eebf15cd…`):** no tengo acceso a su transcript; los conteos «Focales 20/20» no los puedo reconciliar — va dentro de E1 como evidencia a regularizar.

**Dictamen:** 0 bloqueantes de producto. 1 bloqueante de evidencia (E1: despacho test-writer del RED sin registrar — cierre: registrar la fila + stage entry). Puntos 1-5 y O-B/O-D **cerrados y verificados**; deuda declarada (O-A, O-C, calibración) correctamente diferida y sin regresiones. El diff es apto para avanzar a stage 5 una vez regularizado E1.
