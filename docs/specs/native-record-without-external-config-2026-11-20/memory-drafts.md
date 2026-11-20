Validation complete: route C identification matches the canonical render byte-for-byte, REQUEST.json and PACKET.md validate, execution context v2, `intake` rc=0 on the exact capture file. Now the drafts — read-only, nothing edited.

# Draft 1 — `docs/activeContext.md` entry (prepend above the 2026-11-19 entry)

```markdown
## 2026-11-20 — Feature: native-record-without-external-config

**Closed** — standalone maintenance fix (no epic; not part of `epic-019-discovery-dialogue`, which stays closed). Recording a native delegation no longer requires the runtime configuration used to launch an external worker. Approved contract: `docs/specs/native-record-without-external-config-2026-11-20/spec.md` (sha256 `cb0ded8a…b97109c`), approved by <owner> on 2026-11-20; review accepted with no blockers.

**Product.** `cdad_dispatch.py record` now reads its runtime section optionally: an absent `runtimes.json`, an absent `runtimes` map or an absent section is the empty configuration `{}`, which is still handed to the module's single bounded observation when there is a motive. Unreadable/invalid JSON, a present non-object section, forbidden keys, and a missing or invalid runtime module still fail nonzero with nothing written; `dispatch`, `capabilities`, migration, retired-option rejection and the installer are unchanged and stay fail-closed. Motivated observation (declared session, declared parent, or no native payload; `--since` alone does not motivate) calls the runtime module exactly once with the available section, even `{}`, and no longer gates on `sessions_db` or another module-specific key — availability belongs to the module. Unverified identity is recorded as `completed + staged` with null session/model and an explicit provenance note; an observed contradictory evaluable identity still returns `blocked + none + null` naming the key, with no attempt and no staging; omitted native text never creates a delivery. Targeted clarification in `cli-delegation.md`; no new receipt, approval path, launch or inferred store location.

**Relevant decisions.**
- *The recording of a delivery that already happened does not depend on transport configuration.* `load_runtime_section(optional=True)` is scoped to the native `record` path only; the external paths keep their fail-closed diagnostic. Reason: PD-6 permits byte-exact native delivery with reduced identity assurance, while PD-9's required configuration was written for external transport. Trade-off: one loader with two modes, and the relaxation is path-scoped rather than global.
- *The runtime module owns whether its observation surface is available.* The runtime-neutral entry passes the section as-is and never inspects module-specific keys; the module reports its own unavailability. Reason: an entry-level `sessions_db` check silently skipped observation and could hide a contradictory identity. Trade-off: modules receive no synthetic `runtime` key during `--observe` (accepted limit F2).
- *Missing evidence is declared; contradictory evidence is never downgraded.* Unverified identity → null accredited fields plus provenance; contradiction → rejection with no effects. Reason: PC-4/PC-5 protect the promise that recording must not be mistaken for reception or approval.

**Evidencia (Evidence).** Product `5be4ff93` (two files, +33/−7); test adaptations `2f7e1d7f`, `51b89346`, `2140c64a`, with the same 36 `u1b`/`u1a` nodeids before and after and no original assertion removed. Orchestrator proportional selection: **95 passed in 419.98 s** over nine modules (`.cdad-execution/native-record-proportional-verification.txt`). Independent reviewer: **63 passed in 129.08 s, rc=0**, same 36 focal ids, PC-1..PC-9 met, no blocking findings. Inventory `python3 scripts/cdad-suite.py validate` **rc=0** (2208 nodeids, 260 modules). Bounded families closed at draft 1/2, audit 0/2, result 2/2; the two corrected defects were test-fixture defects (unavailable observation conflated with a successful `null`; an unreadable-file cleanup running after `tearDown`) and the product needed no additional correction round. Full suite **not run**: the proportional selection covers native/external configuration, observation, correlation, reference wording, capabilities and continuity edges; no full-suite green, live client recovery, deployment or publication is claimed.

**Technical debt detected.**
- Spec `deferred-hardening`, carried with its dispositions: no new runtime-config schema/version enforcement; no store discovery, live-runtime provisioning, exhaustive timeout testing or upstream capture attestation; no orchestrator redesign, installer change, broad test replacement or new epic.
- **F1 (accepted as deferred hardening):** syntactically valid JSON whose top-level document is not an object, or whose `runtimes` value is not an object, is treated as absent configuration on the native path. PC-7 deliberately selected invalid-JSON/non-object-*section* rejection without broader schema validation; this records the current behaviour, not that malformed structure is validated.
- **F2 (accepted as a disclosed compatibility limit):** native observation no longer adds the synthetic `runtime` key to the available section. No supported OpenCode regression observed; third-party observation modules relying on that key remain unverified.
- **N1 (accepted as cosmetic residue):** indentation drift in `docs/specs/008-002-suite-by-capability/suite-inventory.json`; JSON parses and integrity is rc=0.
- Two preexisting installer helper entries (`tests/install_backup_oracle.py`, `tests/install_harness.py`) are recorded with `VERIFY` contracts, low confidence and zero nodeids; they are inventory presence, **not** semantic accreditation.
- Limits: fixtures establish recording behaviour, not the authenticity of upstream native capture; no live runtime/schema compatibility claim; one cleanup role did not run automated received-dispatch intake, so no such validation is claimed for it.
- No deployment or publication was authorized or performed; the installed methodology and the user's runtime configuration were not modified by this work. Direct-to-disk agent delivery remains deferred at the owner's request.

**Next feature in queue.** None. Open items are owner acts, not cycle work: publication/deployment (never authorized here) and the deferred direct-to-disk agent delivery.
```

# Draft 2 — `docs/progress.md` changes

**2a. Replacement for the existing `## In progress` body** (the current text still says no feature is open):

```markdown
## In progress

**`native-record-without-external-config-2026-11-20` — standalone maintenance, stage 5 (Merge + Memory Bank).** Not part of `epic-019-discovery-dialogue`, which stays closed with 6/6. Opened as a standalone unit on 2026-11-20 after the owner confirmed that native `record --native-result` required external runtime configuration. Product `5be4ff93` (tolerates absent runtime configuration on the native record path only); independent review accepted with no blocking findings and PC-1..PC-9 met. **Pending:** owner approval of these Memory Bank drafts and the closure transition — the `## Done` entry below takes effect with that approval. No deployment, publication or installation was performed. Nothing else is open.
```

**2b. Proposed `## Done` entry, inserted as the first bullet** (applies once the owner approves and the feature is closed):

```markdown
- **native-record-without-external-config-2026-11-20** (2026-11-20, standalone maintenance; not part of epic 019) — recording a native delegation no longer requires the configuration used to launch an external worker. `record` reads the runtime section optionally: an absent `runtimes.json`, `runtimes` map or section is `{}`, while unreadable/invalid JSON, a present non-object section, forbidden keys and a missing or invalid runtime module still reject and write nothing; `dispatch`, `capabilities`, migration, retired-option rejection and the installer stay unchanged and fail-closed. Observation keeps its motive (declared session, declared parent, absent payload) and is delegated exactly once with the available section, even `{}`; availability belongs to the module, not to an entry-level `sessions_db` check. Unverified identity is recorded as `completed + staged` with null session/model and explicit provenance; contradictory evaluable identity still returns `blocked + none + null` with no attempt or staging. **Product:** `5be4ff93` (2 files, +33/−7). **Tests:** `2f7e1d7f`, `51b89346`, `2140c64a`; same 36 `u1b`/`u1a` nodeids, no original assertion removed. **Evidence:** orchestrator proportional selection 95 passed (419.98 s, nine modules, `.cdad-execution/native-record-proportional-verification.txt`); independent reviewer 63 passed (129.08 s, rc=0) with the same 36 focal ids and no blockers; `cdad-suite.py validate` rc=0 (2208 nodeids, 260 modules). **Rounds:** draft 1/2, audit 0/2, result 2/2; the two corrected defects were test-fixture defects and the product required no additional correction round. **Not run:** the full suite — selection, motive and limits are recorded above; no full-suite green, live client recovery, deployment or publication is claimed. **Debt:** spec `deferred-hardening` (no runtime-config schema/version enforcement; no store discovery, live-runtime provisioning, exhaustive timeout testing or upstream attestation; no orchestrator or installer redesign; no new epic) plus owner-accepted F1 (malformed top-level document or `runtimes` map treated as absent on the native path), F2 (synthetic `runtime` key no longer passed to `--observe`; third-party reliance unverified) and N1 (`suite-inventory.json` indentation). Direct-to-disk agent delivery remains deferred.
```

# Draft 3 — ADR draft (MADR, **Confidence: Medium**)

```markdown
# ADR-046 — El registro nativo no exige configuración de transporte; la superficie de observación pertenece al módulo de runtime

- **Estado:** Propuesto (vigente solo tras la aprobación del Memory Bank de `native-record-without-external-config-2026-11-20`).
- **Fecha:** 2026-11-20.
- **Decisor:** <owner> (aprobación pendiente al redactarse este borrador).
- **Confianza:** Media — alta sobre la frontera de configuración; media sobre si la decisión merece estatus permanente de ADR o basta la spec.
- **Origen:** `docs/specs/native-record-without-external-config-2026-11-20/{spec.md,review.md}`; producto `5be4ff93`.

**Contexto.** La delegación nativa ya entrega el texto final: la entrega ocurrió y sólo falta registrarla. Sin embargo, `record` exigía la sección de runtime del archivo de configuración de transporte externo, de modo que una instalación por defecto podía ejecutar la delegación nativa y no poder registrarla (`rc=1`, configuración de runtime faltante). A la vez, la observación debe seguir motivada y acotada, y una identidad contradictoria no puede convertirse en evidencia faltante.

**Decisión.**

1. **La configuración de lanzamiento externo no es requisito para registrar una entrega ya ocurrida.** La carga de la sección es opcional únicamente en la ruta `record` nativa: archivo, mapa `runtimes` o sección ausentes equivalen a `{}`. El resto de las rutas mantiene su fallo cerrado con su diagnóstico existente.
2. **La ausencia se tolera; el error de configuración no.** JSON ilegible o inválido, sección presente pero no-objeto, claves prohibidas, y runtime ausente o inválido siguen rechazando sin registro durable ni staging. No se introduce validación de esquema más amplia.
3. **La disponibilidad de la observación la decide el módulo de runtime.** Con motivo (sesión declarada, padre declarado o payload nativo ausente), la entrada neutral invoca al módulo una sola vez con la sección disponible, incluso `{}`, y no condiciona por `sessions_db` ni por otra clave específica de módulo. Sin motivo, no se observa.
4. **Evidencia faltante se declara; la contradicción nunca se degrada.** Identidad no verificable se registra como `completed + staged` con sesión y modelo acreditados en null y provenance explícita; una identidad contradictoria evaluable sigue devolviendo `blocked + none + null` nombrando la clave, sin intento ni staging.
5. **Sin cambio de productores ni del protocolo externo.** Despacho externo/default, capacidades, migración, rechazo de opciones retiradas e instalador permanecen intactos; no se infiere ubicación de store ni se reescribe la identidad suministrada.

**Consecuencias.**

- *Positivas:* una instalación por defecto puede registrar la delegación nativa; la observación conserva su motivo y su cota; el rechazo por contradicción no se relaja.
- *Costos:* el cargador de sección tiene dos modos y la relajación debe permanecer acotada a la ruta nativa; el módulo deja de recibir la clave sintética `runtime` durante `--observe`.
- *Límites:* un documento de nivel superior o un mapa `runtimes` sintácticamente válido pero mal formado se trata como configuración ausente (F1, hardening diferido); la compatibilidad de módulos de terceros que dependían de la clave sintética queda sin verificar (F2); los fixtures establecen conducta de registro, no autenticidad de la captura nativa upstream.
- *Alcance:* esta decisión no acredita despliegue, publicación, recuperación de un cliente real ni compatibilidad de esquema en vivo.

**Alternativas consideradas.**

- **Exigir `runtimes.json` y pedir al usuario que lo configure:** rechazada; convierte un registro de algo ya ocurrido en una dependencia de transporte externo y contradice la promesa de reducción declarada.
- **Hacer opcional la carga en todas las rutas:** rechazada; relajaría el fallo cerrado del despacho externo, que sí necesita configuración de lanzamiento.
- **Inferir la ubicación del store cuando no está configurada:** rechazada; la promesa prohíbe inferir ubicaciones y copiar identidad suministrada.
- **Validar el esquema completo del mapa `runtimes`:** diferida (F1), fuera del límite elegido; se registra como deuda en lugar de ampliar el fix.
```

# Source notes (for the owner's approval decision)

- **Contract:** `spec.md` (PC-1..PC-9, invariants, correction ceiling 2, `deferred-hardening` §70-74) at the validated sha256.
- **Decisions/limits:** `discovery.md` §"Owner approval" (2026-11-20), §"RED re-entry — fixture correction required", §"GREEN re-entry — test cleanup defect", §"Final ordinary correction verified", §"Owner prioritization and closure preparation" (F1/F2/N1 dispositions and owner "si ok"; families draft 1/2, audit 0/2, result 2/2).
- **Review:** `review.md` (verdict no blockers, PC table, F1/F2/N1, L1 limit, 63 passed, 36 identical ids, full suite not run).
- **Test evidence:** `cleanup-report.md` (36 passed, commit `2140c64a`, no new nodeids); `.cdad-execution/native-record-proportional-verification.txt` (95 passed, 419.98 s); `discovery.md` §"Final ordinary correction verified" for the nine-module command and inventory rc=0 (2208/260).
- **Diff read directly:** `git show 5be4ff93` (the two files and the optional-load / `with_runtime=False` changes), `git show --stat` on `2f7e1d7f`, `51b89346`, `2140c64a`, `5cc18b23`.
- **Language:** the packet asks for English drafts 1 and 2, so they are English; the surrounding Memory Bank corpus is Spanish and the ADR corpus is Spanish, so draft 3 follows the ADR corpus. Say the word if you want 1 and 2 in Spanish to match the corpus — I will re-issue them, I won't silently switch.
- **Draft status:** all three assume your approval and the closure transition. They claim no closure, no full green, no deployment, no publication and no accreditation of the two `VERIFY` helpers.

# Role report (evidence)

- **Modified files:** none. Read-only; no edits, no commits, no approvals.
- **Commands run:**
  - `cdad_packet.py intake --project-root <repo> --received …/scribe-dispatch-001.txt` → rc=0, route C, packet/execution ids matching (structural only; origin of the capture not accredited).
  - `cdad_packet.py validate-request …` → rc=0; `cdad_packet.py validate-packet …` → rc=0; `render --route C` → identical to the dispatch identification.
  - `cdad_packet.py status --project-root .` → `active_feature: native-record-without-external-config-2026-11-20`, `current_stage: merge` (source of the "in progress" correction in draft 2).
  - `git show 5be4ff93`, `git show --stat 2f7e1d7f 51b89346 2140c64a 5cc18b23`, `cat .cdad-execution/native-record-proportional-verification.txt` → evidence quoted above.
- **Commit:** none. **Approval:** non-delegable, yours; the orchestrator commits with `docs(memory):` after you approve.