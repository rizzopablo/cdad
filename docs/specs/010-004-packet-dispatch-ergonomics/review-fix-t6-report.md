# Review-fix T6 — informe sustantivo del implementer (procedencia corregida)

> **Procedencia (declarada, no reconstruida).**
> - Sesión de origen: `<session>` (título «Corregir bloqueantes de revisión», directorio `<repo>`, padre `<session>`, agente `cdad-implementer`).
> - Mensaje de origen: `msg_18fd58a4a001fvn3nTYhZvzDnp` — el **inmediatamente anterior** al mensaje de confirmación del commit (`msg_18fd6840a001fM9Po3cgaRr2iJ`, «Hecho. Commit creado con exactamente las 24 rutas…»).
> - Bytes del informe: **12.535** · `sha256 c70a1795bf4244800db9ecc26c1e706f73f053115fd41468b92e0f0ec4e0d1f8`.
> - Lectura: fila `session_message` del almacén durable de OpenCode (`~/.local/share/opencode/opencode.db`), contenido `content[0].text`, escrita aquí byte por byte tras esta cabecera.
>
> **Límite declarado (no se borra).** El recibo durable del intento 32 (`receipt.json`, `sha256 5c5293e8a4fe3e448ea9693ee18e6b9ce98c847a63c695fbc6b900123e0931ca`, bundle `5d37ef9b…b6c`, part `0b0997f9…1c21`, 2.811 B) acredita la **entrega del packet** y la identidad del intento, pero **no** el contenido íntegro: lo staged en `.cdad/inbox` fue el mensaje de confirmación del commit, no este informe. Este documento restituye el contenido sustantivo tal como lo emitió el rol; **no** reescribe el recibo, ni el asiento del ledger, ni el artefacto materializado `review-fix-t6.md` (que conserva los 2.811 B acreditados). La discrepancia queda registrada como limitación de fidelidad, no corregida retroactivamente.
>
> Materializado por el orquestador CDAD (ADR-003) el 2026-10-31, a pedido del usuario, como evidencia complementaria de la unidad 010-004.

---

**Admisión (Route C, verificada antes de trabajar).** Bloque de identificación único, idéntico a `render --route C`; `validate-request` rc=0 y `validate-packet` rc=0 con los scripts del repo; `PACKET.md` byte-idéntico al `render` completo (`sha256 7d3bef34…9831` en ambos, `cmp` sin diferencias); `spec.md` en su pin `fc6b2ccc…5d64`.

---

## 1. Diff de cada archivo tocado y por qué cumple B1/B2/B3

**Producto — `skills/cdad-cycle/scripts/cdad_packet.py` (+61)**

```diff
@@ -627,6 +627,62 @@ def _validate_active_packet(packet: Any) -> None:
+def _reject_active_v1_packet(project_root: Path, state: dict[str, Any]) -> None:
+    """§4.1 row 3 (PC-07b): a v1 packet that is still active has no CLI exit.
+    ...
+    """
+    active = state.get("active_packet")
+    if not isinstance(active, dict): return
+    if active.get("status") not in ACTIVE_PACKET_STATUSES: return
+    packet_id = active.get("id")
+    if not _safe_packet_component(packet_id): return
+    request_path = project_root / PACKETS_TREE / packet_id / "REQUEST.json"
+    if not request_path.is_file(): return          # publicación interrumpida
+    try:
+        request = _load_json(request_path, "published request")
+    except PolicyError as exc:
+        raise PolicyError(f"active packet {packet_id!r} is ... unreadable (...); there is no
+            terminal CLI route to resolve it: escalate to the owner") from exc
+    if REQUEST_LOCATOR_FIELD in request: return     # generación v2: conserva su lectura
+    execution_id = request.get("execution_id")
+    if (... FLAT_NAME ...):
+        if context_path.is_file() and _load_json(context_path, ...).get("schema_version")
+                == V2_SCHEMA_VERSION: return        # histórica en la forma, v2 en sus vías
+    if active.get("status") == "dispatched" and _has_durable_receipt(project_root, state): return
+    raise PolicyError(f"active v1 packet {packet_id!r} is {active.get('status')!r}: no terminal ...")
@@ -6399,6 +6455,11 @@ def prepare(args: argparse.Namespace, project_root: Path) -> bytes:
         state = _load_json(state_path, "project state")
+        # §4.1 row 3 (PC-07b): a published v1 active packet blocks EVERY
+        # preparation path, `--new-execution` included, before any selection or
+        # write: its diagnostic names the packet and escalates to the owner.
+        _reject_active_v1_packet(project_root, state)
         execution_document, execution, write_context = _select_execution(args, project_root, state)
```

Cumple **B2** sin abrir ninguna vía: sólo añade un rechazo previo a `_select_execution` (por tanto también delante del bootstrap que alcanza `--new-execution`); no publica, no escribe state, no convierte ni reescribe v1, no añade migración/withdraw/replay/fallback. Las ramas existentes que hoy sí tienen salida (paquete v2 activo → su bloque PD-4 de `:6470`; publicación interrumpida; `dispatched` con recibo durable) conservan su lectura intacta.

**Fuente de rol — `sources/roles/architect.md` (+12/−6, dentro de `cdad-shared:intake-core`)**

```diff
-  partial inline body never stands in for the identification. Those
-  control-plane reads (the packet's own files) never widen the role's product
-  scope nor authorize other product reads.
+  partial inline body never stands in for the identification. Route C requires
+  a v2 execution context: a v1 context is reported with its explicit
+  diagnostic, never switched silently to route A. Those control-plane reads
+  (the packet's own files) never widen the role's product scope nor authorize
+  other product reads.
@@
-the canonical render. Never guess instructions and never fall back silently to
-legacy.
+the canonical render. Route A and route C are exclusive: a dispatch carrying a
+route C identification together with an inline packet is a route mixture and
+is rejected as an invalid packet even when the inline matches its render.
+Never guess instructions and never fall back silently to legacy.
```

Cumple **B1** en el dueño único del texto, sin duplicar la regla (ver §3).

**Referencia — `skills/cdad-cycle/references/project-execution.md` (+4)** — adyacente a la frase que recomendaba `--new-execution` como salida; describe el mismo resultado que el producto, sin procedimiento nuevo:

```diff
 - If any prior context exists (a v1 `.cdad/execution.json` or an active v2),
   add `--new-execution`; without it the call fails with a diagnostic.
+- A published v1 packet that is still active (`prepared`, or `dispatched`
+  without a durable receipt) has no terminal CLI route: `--new-execution` does
+  not bypass it. `prepare` names that packet, declares the absence of a route
+  and escalates to the owner, with no effect on the tree or the state.
```

**Referencia — `skills/cdad-cycle/references/re-entry.md` (+36)** — sección nueva, ver §4 (**B3**).

**Derivados — 20 archivos `agents/` (+14/−6 cada uno)** — sólo recomposición de `intake-core`; `cdad-orchestrator{,-odoo}.md` no cambia (su intake es declaradamente distinto). `build/staging/**` regenerado (está en `.gitignore`, por eso no aparece en `git status`).

## 2. B2 — rama exacta y diagnóstico nuevo

Rama: `prepare()` (`skills/cdad-cycle/scripts/cdad_packet.py:6428`), dentro de `_ProjectLock`, tras `state = _load_json(...)` y **antes** de `_select_execution(...)`; llamada en `:6461` al helper `_reject_active_v1_packet` (`:630`). Cubre por construcción `prepare` y `prepare --new-execution`.

Texto emitido (medido, `rc=2`, idéntico en ambos comandos):

```
ERROR: active v1 packet 'legacy-v1-packet' is 'prepared': no terminal CLI route resolves it
(no migration, withdraw, replay or legacy fallback opens one), so this preparation is refused
and nothing is written. `--new-execution` does not bypass this block: escalate to the owner,
the only authority that can decide the disposition of that v1 packet (010-004 §4.1 row 3/PC-07b)
```

(a) nombra el id exacto; (b) declara la ausencia de ruta CLI terminal; (c) escala al owner; sin «complete or fail» / «completar o fallar». Control de no-sobrebloqueo medido: un paquete **sin** locator pero con contexto v2 canónico conserva la salida existente (`… is 'prepared': complete or fail it before preparing a new packet (PD-4)`, rc=2) y sus vías reales.

## 3. B1 — bloque `intake-core` resultante y punteros

El bloque (líneas 15–60 de `sources/roles/architect.md`) ahora enuncia: (i) «Route C requires a v2 execution context: a v1 context is reported with its explicit diagnostic, never switched silently to route A»; (ii) «Route A and route C are exclusive: a dispatch carrying a route C identification together with an inline packet is a route mixture and is rejected as an invalid packet even when the inline matches its render», cerrando con «stop and report … never fall back silently to legacy». El resto de `sources/roles/*.md` no se tocó: siguen siendo punteros (`implementer.md:14`, `reviewer.md:14`, `scribe.md:12`, `test-writer.md:14` → «Intake: shared core (sources/roles/architect.md · cdad-shared:intake-core)»); `orchestrator.md` conserva la regla de emisión que le es propia (`:70`). Verificado en derivados: la regla aparece **una** vez por agente (11 artefactos × 2 runtimes; 0 en los orchestrator, 1 en los otros 20 = exactamente 20 archivos con la frase).

## 4. B3 — secciones incorporadas a `re-entry.md`

`## Integrity, observability and fidelity (what each evidence accredits)` — tabla espejo de §4.7 con las cinco evidencias (request validado y archivo igual al render; bytes a stdin; literal reconstruido; contraste del resultado; recibo) y su columna «Accredits / Does NOT accredit»; y dos reglas: **I-4** (evidencia insuficiente no prueba corrupción ni obliga por sí sola a repetir; se registra la limitación y se contrasta resultado ↔ contrato/fuentes, conservando revisión y aprobación; no licencia ignorar divergencia conocida, autoridad inválida ni contenido infiel) e **I-5** (divergencia comprobada → rechazo; cambiar de ruta no rescata un inline divergente; transporte correcto no justifica resultado infiel; recuperación = **nuevo encargo v2** con sus gates). Vocabulario y vías existentes, sin protocolo nuevo: `receive` / `validate-receipt` / `materialize` / `register-transition`, y el procedimiento por `delivery` de 007-004 §6.2 citado, no reescrito.

## 5. Evidencia real de la verificación focal (árbol final)

| Comando | Resultado |
|---|---|
| `python3 -m pytest tests/test_010_004_t6_red.py -q` | `2 passed in 2.57s` |
| `python3 -m pytest tests/test_010_004_t2_red.py tests/test_010_004_t3_red.py tests/test_010_004_t4_red.py -q` | `15 passed in 20.32s` |
| `python3 -m pytest tests/test_010_004_t5_properties.py -q` | `2 passed in 111.50s` |
| `python3 -m pytest tests/test_010_004_t5_e2e.py -q` | `2 passed in 30.33s` |
| `python3 -m pytest tests/test_cdad_generate.py -q` | `10 passed in 3.06s` |

Regresión proporcional declarada (el cambio toca `prepare`, `re-entry.md`, `project-execution.md` y los derivados): `test_packet_prepare.py + test_007_003_legacy_reanchor.py` → `38 passed in 291.39s`; `test_004_003_t5_reentry_equivalence.py + test_003_006_t3_receive_wiring.py + test_006_002_u5_transport_equivalence.py` → `29 passed in 12.24s`; `test_005_005_t2_docs_policy.py + test_005_006_t6_owner_reviewfix.py + test_006_004_u4_decisions_table.py + test_007_001_unambiguous_entry.py` → `69 passed in 71.28s`; `test_006_005_reviewfix.py + test_006_006_u3_review_route_and_gate.py + test_005_007_t7_unit_size_and_retries.py` → `25 passed in 13.16s`; `bash tests/validate-odoo-specialization.sh` → `Assert PASS: 68 / FAIL: 0`; `bash tests/validate-consistency.sh` → `Assert PASS: 182 / FAIL: 1`.

**Suite completa NO ejecutada** (plan.md:74 reserva el cierre para T6), como manda el paquete.

**Cero efectos de B2:** lo asserta el oráculo y pasa — `tree_digests(root)` y `state_bytes()` idénticos antes/después de ambos rechazos (`TestB2…` verde).

**F011 (declarado, no oculto):** el único FAIL es `F011: scripts/validate-subagents.sh → install.sh --check`. Es preexistente y ambiental (D-1: compara el repo contra la instalación desactualizada). Medido en un worktree limpio sobre `1dd7661f`, sin mis cambios y con `make staging` generado: `base_rc=1`, `Assert PASS: 182 / Assert FAIL: 1`, **el mismo** assert `F011`; `install.sh --check` rc=1 con 26 `DRIFT`. No publiqué nada.

## 6. Determinismo de la regeneración

`make staging` + `make agents` dos veces consecutivas; snapshot de `sha256` de todo `build/staging` + `agents` (45 archivos) entre corridas: `cmp` de los dos snapshots sin diferencias → **`DETERMINISTIC_identical_bytes_final`**. Además `cmp` archivo por archivo entre `build/staging/agents/opencode/*` ↔ `agents/*` y `build/staging/agents/claude-code/*` ↔ `agents/claude-code/*`: sin diferencias. `agents/**` no se editó a mano (sólo `cp` de `make agents`).

## 7. Alcance e integridad

```
$ git diff --stat
 24 files changed, 290 insertions(+), 105 deletions(-)
  agents/** (20 archivos) · skills/cdad-cycle/references/{project-execution,re-entry}.md
  · skills/cdad-cycle/scripts/cdad_packet.py · sources/roles/architect.md

$ git status --porcelain
 M agents/cdad-*.md (10)   M agents/claude-code/cdad-*.md (10)
 M skills/cdad-cycle/references/project-execution.md
 M skills/cdad-cycle/references/re-entry.md
 M skills/cdad-cycle/scripts/cdad_packet.py
 M sources/roles/architect.md
?? docs/specs/010-000-continuity-relative-root/discovery.md   ← preexistente (ya estaba al iniciar)
```

- `sha256 tests/test_010_004_t6_red.py` = `de085989351840361166c33fdcede1f5b41d48301f0ae9014217017c827d1b49` — **idéntico antes/después**; `git diff -- tests/` vacío: oráculo intacto.
- `sha256 spec.md` = `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64` (pin) y `plan.md` sin tocar; `docs/specs/**` sin cambios.
- `scripts/cdad_packet.py` (wrapper) no tocado; ningún archivo bajo `docs/`, `tests/` ni `scripts/`.
- Copia instalada y rutas globales intactas: sólo ejecuté `install.sh --check` (lectura); mtimes de `~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py` (2026-10-29 08:41) y `~/.claude/skills/cdad-cycle/references/re-entry.md` (2026-10-26 10:54) anteriores a esta sesión.
- **Sin commit**: la evidencia pedida es `git diff --stat` / `git status --porcelain`; los cambios quedan en el árbol para la auditoría y el commit del orquestador. No despaché ni registré transiciones.