The fix and test look coherent. Now I verify independently — I don't accept the author's reports as proof. Running the focal suite, the coupled U2/U4 oracles, and mechanically reproducing the RED state against the old content (`git show 8c4ead5:...` — read-only, no tree mutation):
RED reproduced mechanically against the old tree — the author's RED is genuine, and the fix removes all 5 offenders. Now verifying the author's GREEN verification and the closure grep over the whole installable tree:
All evidence gathered. No file was modified by my verification (read-only commands, `git show`/pytest over gitignored caches only). Final report:

---

# Re-Review acotada — `006-002-delegation-by-layer` (stage 4, fix B-1)

**Objeto:** cierre del bloqueante B-1 (`docs/specs/006-002-delegation-by-layer/review.md:22-28`) sobre el diff `8c4ead5..HEAD -- skills/ tests/` (RED `5c85d68` → GREEN `a25fc20`). Dif verificado: exactamente 2 archivos — `skills/cdad-cycle/references/sub-agent-strategies.md` (1 línea) y `tests/test_006_002_reviewfix.py` (nuevo, 239 líneas). Nada más entró al scope.

**Verificación del autor reproducida por mí (comandos exactos y salida):**

1. `python3 -m pytest -q tests/test_006_002_reviewfix.py tests/test_006_002_u2_neutral_skill.py tests/test_006_002_u4_skill_without_models.py` → **13 passed**.
2. Suite focal completa 006-002 (u1..u6 + reviewfix) → **41 passed** (coincide con rf-green.md:56).
3. `grep -RniE '\bhaiku\b|\bsonnet\b|\bopus\b|\bfable\b|mofgw' skills/` → **0 coincidencias** (exit=1). Condición de cierre de B-1 (`review.md:28`) cumplida literalmente.
4. **Reproducción mecánica del RED sin mutar el árbol:** corrí el oráculo extendido (`runtime_model_detail_offences`) sobre `git show 8c4ead5:skills/cdad-cycle/references/sub-agent-strategies.md` dentro de la superficie completa de U2 → **5 ofensores, todos en la línea 51** (4 alias + gateway), y el documento citado está en la superficie escaneada. El RED del autor es genuino: no es un test trivialmente verde disfrazado.
5. Lectura directa del test (`tests/test_006_002_reviewfix.py`): reusa la única definición de superficie/oráculo de U2 (sin duplicar patrones), autocontrol del oráculo con los 3 guards (captura la clase, no genera falso positivo en prosa «magnum opus»), y el guard de drift asegura que el documento de B-1 permanece escaneado. Cada test mapea a una postcondición observable (convention cumplida).

## Tabla hallazgo → CERRADO/ABIERTO

| Hallazgo | Severidad original | Estado | Provenance |
|---|---|---|---|
| **B-1** — detalle de modelo de runtime (alias + gateway) en texto instalable | Required · BLOCKING · m | **CERRADO** | Línea reescrita (`sub-agent-strategies.md:51`, estilo `:53`/`:55`: modelo = configuración del entorno, sintaxis en capa agente, sin alias/proveedor/gateway); oráculo extendido captura la clase y el RED falló genuinamente contra el árbol viejo (5 ofensores reproducidos por mí, punto 4); grep de cierre → 0; U2/U4 intactos (13 passed). Los dos mecanismos que B-1 exigía (texado + oráculo observable) están ambos presentes. |

**Regresiones introducidas por el fix:** ninguna encontrada. La nueva línea 51 no nombra herramienta de despacho ni modelo concreto (no recae bajo PD-1); la suite focal 006-002 completa sigue en verde (41). No reabro O-1..O-4 ni las abstenciones del review anterior: fuera de scope de este packet.

## Hallazgos nuevos (solo los que el fix introduce)

- **NF-1 — El oráculo del gateway es de instancia, no de clase.** Verdict: OPTIONAL · Bucket: l · `tests/test_006_002_reviewfix.py:103` (`DEPLOYMENT_GATEWAY_TOKENS = ("mofgw",)`). El patrón fija el literal `mofgw`; otro gateway de despliegue futuro escaparía igual que escapó este. La condición de cierre declarada por B-1 (`review.md:28`) pedía exactamente este grep/instancia, así que el cierre es conforme al contrato — esto es deuda de generalización, no defecto del cierre. Consolidación sugerida: migrar el token a una lista configurada junto a `PROVIDER_RE` (U2) o documentar la frontera en el docstring. No bloquea: no compromete resultado, evidencia ni uso previsto del fix ya aprobado.

## Juicio separado pedido — `sub-agent-strategies.md:49-50` (frontmatter de permisos + hooks de CC)

- **Severidad:** Optional/Consider (deuda) · **Verdict: OPTIONAL · Bucket: l**.
- **Lectura:** PD-1 (`spec.md:47-49`) prohíbe nombrar *herramienta de despacho* o *modelo concreto en contexto de delegación*. Las líneas 49-50 no nombran ni lo uno ni lo otro: nombran campos de frontmatter de permisos (`permission`/`tools:`), `hooks.PreToolUse` y la ruta del guard (`~/.claude/cdad-scripts/path-guard.sh`) — mecanismo de **enforcement**, no de despacho ni de modelo. Por la letra del contrato, no son ofensores; por el principio de capas (PD-1 outcome «SKILL = methodology templates», `spec.md:32`), la *sintaxis de configuración por runtime* idealmente viviría en la capa agente (donde de hecho ya está declarada: `sources/agents/adapters/claude-code.md` §frontmatter, orquestadores generados), dejando en la skill solo el puntero al estilo de `:53`/`:55`.
- **Ponderación con el criterio vigente:** la sección es explícitamente comparativa («Key differences from OpenCode», «### Claude Code»), disambigua («NOT OpenCode — the syntaxes are different»), y el review anterior ya adjudicó ese árbol como neutralizado salvo `:51` (per-point 1, `review.md:46`). El detalle no compromete resultado, evidencia ni uso previsto: un lector de otro runtime no recibe una instrucción de despacho ni un acoplamiento de modelo. **Es detalle de runtime que *podría* salir por capas, pero es aceptable como referencia** → deuda, no bloqueo. Consolidación si el owner quiere la lectura estricta: mover la sintaxis de campos/hooks al adaptador CC y dejar el puntero; mismo patrón de refactor que `:51`.
- Nota: este juicio es interpretativo, no reabre lo ya juzgado (el packet lo pide como juicio separado y explícitamente no bloqueante).

## Abstentions

1. **Suite completa:** política declarada en el packet common — la corre el closer una vez, al cierre. Corrí focal + oráculos acoplados U2/U4 + suite 006-002 completa (41). ABSTAIN sobre superficies no ejecutadas.
2. **`make validate` / `make staging`:** verificados por el autor (rf-green.md:61-79, con F011 = baseline DT-8 preexistente y generación byte-idéntica). No los re-ejecuté: el cambio de 1 línea de texto instalable no toca generador ni adaptador, y la condición de cierre de B-1 no los exige. ABSTAIN como verificación directa propia; el estado reportado por el autor es coherente con el diff.
3. **Instalación HOME (DT-8):** el drift de `<home>/.claude/skills/...` es baseline ambiental preexistente declarada; su renovación no es producto de este diff. ABSTAIN (ya registrada como abstención 4 del review anterior).

## Comando/evidencia de integridad

- Commits del fix: `5c85d68` (RED, tests solamente) y `a25fc20` (GREEN, 1 archivo, +1/−1). HEAD = `36b08f9` (solo estado de orquestación posterior, dentro de `docs/**` permitido).
- Mi verificación no modificó nada trackeado; `git status --short` muestra solo untracked preexistentes ajenos (`docs/planning/`, `findings/…`).

---

**Resumen: 0 bloqueantes, 1 opcional (NF-1), 1 juicio separado opcional (líneas 49-50, deuda), 3 abstenciones.** B-1 **CERRADO** conforme a su condición de cierre verificable. Read-only: nada editado, nada aprobado.
