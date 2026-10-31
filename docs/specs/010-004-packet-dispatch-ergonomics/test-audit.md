# AUDIT T1 — pruebas de 010-004 (test-writer, solo lectura)

**Paquete:** `010-004-packet-dispatch-ergonomics-test-writer-audit-001` · **Ejecución:** `exec-010-004-packet-dispatch-ergonomics-001`
**Validación de entrada:** `validate-request` y `validate-packet` rc=0; `PACKET.md` byte-idéntico a `cdad_packet.py render` (diff vacío). Pins verificados: spec `fc6b2ccc…`, plan `2ae8ada3…`, owner V2-1 `8f1810ba…`, policy `f508ab1e…` (sha256sum ejecutados).
**Ediciones:** ninguna (subfase AUDIT read-only; `expected_output` FINAL TEXT; sin commit ni BOOT POST-AUDIT/RED — el campo `commit` de `evidence_required` no aplica a esta subfase, se registra la desviación).
**HEAD:** `8d50d2f34a7645a042072d0f08470a7a8bc91d8e`; `git diff` limpio; único untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md`. **Implementación no leída:** ningún archivo de `skills/`, `scripts/`, `sources/`, `agents/`, `build/` fue leído ( Specs y tests citados solo por lectura L; los marcados **[E]** incluyen evidencia de ejecución).

## 1. Inventario test ↔ promesa/PC (afectadas y vigentes)

### 1.1 Expectativas SUSTITUIDAS por PC-04 (actualizar en POST-AUDIT aprobado)

| Test | Promesa hoy (lectura L) | Estado tras PC-04 | Consecuencia R4 registrada |
|---|---|---|---|
| `tests/test_004_002_t6_landing.py:606-657` `TestPd12LegacyIntake::test_pd12_legacy_without_policy_keeps_legacy_intake` **[E hoy verde]** | PD-12 (004-002 spec:112-115): legacy sin policy ni v2, con v1 en `.cdad/execution.json`, `prepare` implícito publicado y no fabricó v2 ni tocó el v1 | La publicación implícita v1 queda sustituida: PC-04 rechaza la selección v1 implícita sin policy **antes de publicar**, sin efectos persistentes (INV-11); se conservan v1 intacto y reconocimiento histórico (§4.1) | Sin esta prueba actualizada, el orquestador recibiría paquetes nuevos preparados sobre autoridad v1 implícita, rompiendo INV-08/INV-12 y el despacho |
| `tests/test_packet_prepare.py:402-424` `TestPrepareDefaults::test_p2_default_execution_context_and_out_dir_under_project_cdad` **[E hoy verde]** | P2: sin flags, EXEC=`ROOT/.cdad/execution.json` y OUT=`ROOT/.cdad/packets` con publicación exitosa | Lado EXEC sustituido: la copia v2 en `.cdad/execution.json` no es localizador admisible para publicación nueva (§4.1: «copia en otra ubicación no es localizador admitido»; ubicación canónica `.cdad/executions/<id>/execution.json`) → rechazo previo a publicar. Lado OUT (default `.cdad/packets`) no está gobernado por §4.1 → conservable; ver §5 ambigüedad A2 | Sin ella, una preparación nueva declararía donde no hay — o resolvería por convenio de ruta no canónico — silenciando ubicaciones de contexto sin autoridad |

### 1.2 VIGENTES que comparten fixtures, sin promesa comprometida al cambio (no tocar)

- `tests/test_packet_prepare.py:534-556` `test_p4_default_out_dir_is_not_created_on_failure` **[L]** — mismo patrón de copia a `.cdad/execution.json`; promesa P4 (fallo rc=2, stdout vacío, sin out-dir ni cambio de state) sigue vigente; el punto de fallo observable puede cambiar (hoy: contrato faltante). Vigilar en GREEN.
- `tests/test_004_002_t2_bootstrap.py:649-665` `test_pd10_v1_present_without_flag_fails_demanding_new_execution` **[L]** — v1 presente sin flag **con policy** → rechaza pidiendo `--new-execution`, v1 intacto. Vigente; PC-04 extiende el rechazo al caso sin policy (RED nuevo de la tanda).
- `tests/test_004_002_t2_bootstrap.py:454-460` `test_pd3_negative_policy_missing` **[L]** — sin policy → rechazo sin defaults ni publicación. Vigente; distinta casuística que 1.1-r1 (proyecto con binding v2 vs consumidor instalado con v1); no duplicar RED.
- `tests/test_004_002_t2_bootstrap.py:468+` `TestPd4IdentityAndResume` (resume byte-idénticos) **[L]** — `--resume-packet` es reemisión, no preparación nueva; no se añade localizador (§4.1: reemisión byte-identical no sujeta a la regla v2 de publicación nueva). Vigente.

## 2. Traza expectativa anterior → 004-002 PD-12 → decisión owner → 010-004 §7/PC-04

Para cada fila de §1.1 (y las RED nuevas de PC-04):

1. **Expectativa anterior:** `tests/test_004_002_t6_landing.py:611-618` (docstring: «conserva el camino implícito anterior»; aserto de publicación implícita en `:645-651`) y `tests/test_packet_prepare.py:403` (sin flags, EXEC default en `.cdad/execution.json`), trazadas a `docs/specs/004-002-project-execution-bootstrap/spec.md:112-115` (PD-12: el proyecto legacy «conserva su intake»; architect standalone sigue ese camino) y a su criterio `:138` (PD-1–PD-12 con tests trazados).
2. **Sustitución declarada:** `docs/specs/010-004-packet-dispatch-ergonomics/spec.md:452-460` (§7, N-3): «esta spec sustituye explícitamente la garantía de 004-002:115 en cuanto permitía preparar implícitamente un encargo v1 sin policy». El `delta comprobado` de la spec (`:179`) marca la vía cerrada: selección implícita v1 al faltar policy + binding v1 de prepare.
3. **Autoridad del cambio:** `docs/specs/010-004-packet-dispatch-ergonomics/owner-decision-plan-v2-1.md:3-18` (decisión V2-1 vigente, pin plan/spec íntegros) junto a la citada `owner-decision-v2-new-assignments.md` (spec §2.4, `:50-56`): **todo encargo nuevo usa v2, también sobre proyectos políticos**.
4. **Requisito nuevo:** PC-04 (spec:406): rechazo de selecciones v1 explícitas/implícitas y de ubicaciones v2 incompatibles antes de publicar; toda publicación nueva declara localizador canónico en request y cabecera; sucesor lo declara aunque el predecesor no.
5. **Spec histórica 004-002: intocada** (solo lectura; verificación: `git status` sin cambios en `docs/specs/004-002-*`).

## 3. PC-08a (regresión existente) vs PC-08b (instrucción revisable) — separación explícita

**PC-08a — mecánica, ya verde, sin RED artificial (spec:418; plan.md:52):**

| Garantía | Test existente | Evidencia |
|---|---|---|
| Cuerpo alterado / metadata / hash de contrato → rechazo | `tests/test_role_packet_render.py:350-379` `test_p2_validate_packet_rejects_tampered_body_metadata_and_hash` | **[E] hoy PASS** (pytest, §6) |
| Variante CRLF → rechazo por bytes crudos | `tests/test_role_packet_review_regressions.py:468-501` `test_p2_validate_packet_rejects_crlf_byte_variant` | **[E] hoy PASS** |
| Aceptación canónica y determinismo del render | `tests/test_role_packet_render.py:258-284` `test_p1_all_role_substage_pairs_render_and_validate`, `:287-295` `test_p1_repeated_render_is_byte_deterministic`, `:328-349` `test_p2_metadata_is_canonical_and_matches_request` | **[L] cobertura identificable** |
| Frontera de preámbulo validate-packet (§4.4: «no elimina preámbulo») | **No se identificó test** en los archivos PC-08a declarados ni en `tests/` (grep `preamble/preámbulo` vacío) | Ver §5 ambigüedad A1 |

**PC-08b — instrucción revisable, verificación textual, no mecánica (spec:420):** el cierre JSON no termina el paquete; la comparación abarca instrucciones y cuerpo. Pertenece a T4 (plan.md:32); su revisión no acredita conducta de modelo — sin test de runtime en esta tanda.

## 4. Selección focal, regresiones, controles positivos, comandos y límites para la siguiente tanda

**Focales (RED tanda T2):**
1. **PC-04-a:** legacy sin policy + v1 en `.cdad/execution.json` + instalado (`run_installed`) → rc≠0, stdout vacío, v1 intacto, sin v2 fabricado ni paquete publicado (reemplazo trazado de §1.1-r1).
2. **PC-04-b:** `prepare` sin flags con contexto v2 en copia no canónica → rechazo rc≠0 sin publicar (reemplazo trazado de §1.1-r2, lado EXEC).
3. **PC-04-c:** preparación nueva exitosa (control positivo, contexto v2 canónico) declara `execution_context` canónico en request y cabecera; render igual a packet (I3: no rechazo universal).
4. **PC-05 fila 1:** request **con** localizador + sin `--execution-context` → los 3 CLI resuelven el localizador y validan. **PC-05 filas 3-4 ya hoy verdes** (fixtures pasan `--execution-context` siempre; fila 4 = error de contexto ausente vigente): solo control positivo tras el cambio, **no RED**.
5. **PC-06:** localizador fuera de dominio (absoluta, vacía, escapes, ubicación no canónica), identidad/schema discordantes, y arg explicitó que discrepa del localizador → los 3 CLI rechazan con diagnóstico y sin probar otra ubicación; confirmar **sin ampliar `cdad_result`** (fuera de alcance, §3).
6. **PC-07:** con raíz explícita y `cdar` distinto, los request con localizador resuelven el mismo contexto (positivo); el histórico conserva uso explícito (existente).
7. **PC-02/PC-01 (tanda T3):** C positivo determinista sobre paquete publicado v2; C negativo: contexto v1 con diagnóstico “C requiere v2”, request no publicado, contexto no canónico, paquete divergente → sin identidad usable ni efectos.

**Regresiones a reutilizar (sin RED):** §3 (PC-08a) más las vigentes §1.2.
**Comandos base:** `python3 -m pytest tests/<focal> -q` (mismos patrones que §6); suite completa **no** por despacho (política declarada en el paquete; corrida en T4/T6).

**Límites de evidencia:** la ejecución black-box de la tanda acredita conducta del CLI instalado en fixture, no recepción nativa del runtime ni obediencia del modelo (§4.7 de spec); tests textuales (PC-08b/PC-03/PC-07b parcial) no acréiditan más que la revisión documental.

## 5. Ambigüedades funcionales escaladas al orquestador (no resueltas aquí)

- **A1:** la frontera de preámbulo de §4.4 para `validate-packet` no tiene test identificable. El plan (T3) asigna 4 garantías PC-08a a reutilizar; 3 tienen cobertura. Escalar: ¿se añade un RED de PC-08a para preámbulo en T3 (no está “ya verde”: está sin cubrir) o se registra en deferred-hardening?
- **A2:** cuando PC-04 sustituye el lado EXEC de `test_p2_default_execution_context...` (:403), ¿debe conservarse el lado OUT (default `.cdad/packets`) en el test reescrito, o crear uno aparte? Propuesta: conservarlo en el test con contexto canónico explícito (una sola promesa, P2), verificado en POST-AUDIT aprobado.

## 6. Evidencia de ejecución (comandos y salida, subfase AUDIT)

```
python3 scripts/cdad_packet.py validate-request --request .cdad/packets/…/REQUEST.json --execution-context .cdad/executions/…/execution.json  → exit 0
python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md --execution-context …  → exit 0
python3 scripts/cdad_packet.py render … > /tmp/opencode/render-canonical.md && diff -u PACKET.md render-canonical.md → vacío ("PACKET == CANONICAL RENDER: OK")
python3 -m pytest <pd12 legacy, p2 default exec ctx, tampered body> -q  → "3 passed in 33.41s"
python3 -m pytest tests/test_role_packet_review_regressions.py -k "crlf" -q → "1 passed, 7 deselected in 9.02s"
```
Archivos modificados: ninguno. Commit: ninguno (subfase solo-lectura; reportado como desviación del campo `commit` de `evidence_required`).

---

**Estado de los movimientos:** AUDIT entregado FINAL TEXT, una sola subfase; no preparé, ni ejecuté POST-AUDIT o RED ni indagué más paquetes (fuente C única). El gate de integración corresponde al orquestador (`integration_gate` del paquete: Pablo aprueba o mandato explícito vigente antes de POST-AUDIT).