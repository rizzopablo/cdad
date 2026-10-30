**Intake (ruta A) — validado antes de trabajar**
- Un único marcador `---cdad-packet-json` con su cierre; el preámbulo del runtime es transparente y no autoriza nada.
- `validate-request` y `validate-packet` → `rc=0` (CLI del repo `scripts/cdad_packet.py`, raíz absoluta, contexto v2 `.cdad/executions/exec-010-000-continuity-relative-root-001/execution.json`).
- `render` → `rc=0`; `cmp` render vs `PACKET.md` publicado → `IDENTICAL`, sha256 `1820b1d4c0df2a695d0cc7eea3b070d175cc7da026436f1c356a869d3bb8de67` en ambos (5846 B).
- Bytes recibidos (marcador→fin) contrastados contra ese render **completo**, campo por campo (cabecera JSON, bloque de instrucciones, objective, contract, inputs, scopes, invariants, expected output, evidencia): sin diferencias.
- Contrato `docs/specs/010-000-continuity-relative-root/spec.md` sha256 `623b15e14290739f6f7c099183a06348b91bcce02eac4dce37265019f01737e2` = declarado. Trabajé sólo con los 5 insumos declarados y el Memory Bank vigente. `write_scope` `[]`.

**Bases SHA256 (completas, medidas ahora)**
- `docs/activeContext.md` `40599bcf146343cddd73de57e4ae71d1afe0766904b9a616e55bdc07d8cd3bdc`
- `docs/progress.md` `d88a1ed324e2c56f0405f63545efebb4c486e89b21a2c6b9f1724fb466c45064`
- `review.md` `7845614e2b5a262fdcdd8ac59d245001a368662ff9ffba2896b1250abcab245b` · `closure-evidence.md` `fd38cfe978e34085769b3ee9be007adae46e210c7a96845e08679a3ca4f66e90`
- `full-suite-recovery.md` `b344c947e3bb891211aa5a15ef942f13046286ee61b87dbfea7f223f118ce1cc` · `isolated-validation.md` `65eb6ec73badacaa11c1942c73b4a8ba735c04e4eee5f1381e169a2043e28c0c`
- HEAD `c8ab0cb`; `git diff --stat 34dcd9b..HEAD` → `3 files changed, 57 insertions(+), 31 deletions(-)`.

---

# FINAL TEXT — borradores (propuestas; no los materialicé, no apruebo)

## Sección 1 — `docs/activeContext.md` (insertar como primera entry, bajo el `---` de la línea 5)

```markdown
## 2026-10-29 — Feature: 010-000-continuity-relative-root (epic 010)

**Propuesta de cierre local; no aprobada.** Con `.`, con una raíz relativa o con una raíz por symlink al
mismo proyecto, la continuidad y los paquetes rechazaban trabajo válido: el candidato ya resuelto se
comparaba contra la raíz tal como venía escrita. La corrección canonicaliza **la raíz, en los bordes**
(`_canonical_project_root` en `skills/cdad-cycle/scripts/cdad_packet.py`, aplicada en `_project_path`,
`classify_path_observable`, `verify_published_packet`; `plan_write` y `_run_write` en `cdad_continuity.py`):
toda pertenencia compara resuelto contra resuelto y nada más se normaliza — referencias, cuerpo durable,
digests e identidad conservan el texto relativo (PC-04). Diff `34dcd9b..HEAD` (`c8ab0cb`): 2 scripts del
skill + `tests/test_010_000_continuity_relative_root.py` (A, A2, B, C, D).

**Decisiones relevantes.** D1 — canonicalizar la raíz, no la variable del CLI: normalizar el argumento
dejaba incoherentes handlers y entradas programáticas, y se descartaron las excepciones para `"."` y exigir
absolutas al usuario. D2 — conservar el containment existente y separar la deuda: `update.references`
mantiene su control léxico, ampliar raíces no debía debilitar barreras (PC-07). D3 — acreditar en el
consumidor instalado aislado, no en el checkout ni en la instalación global.

**Evidencia.** Review independiente sin bloqueantes (6 opcionales, 2 abstenciones). Suite completa **por
composición, no en una corrida única verde**: la corrida original conserva `rc=1` (8 failed, 1624 passed,
5 skipped, 217 errors por `Errno 28`, inodos al 94%) y sus 225 casos se recuperaron en **23 lotes rc=0**
sobre fuente equivalente, sin cambiar producto ni tests → **1849 passed / 5 skipped**. Producto aislado:
`make staging`, `install.sh`, `--check` (393 grupos) y `make validate` `rc=0`; A3 allí usó sólo el patrón
público. Global: `make validate` sigue en drift, visible y no reparado. Sanitización privada: **68 PASS /
0 FAIL** sobre el checkout real, sin copiar ni publicar `tests/.sensitive-patterns.local`.

**Technical debt detected.** (1) `deferred-hardening` íntegro, 5 ítems: containment resuelto de
`update.references` (seguridad), TOCTOU de symlinks y concurrencia, fallos de disco entre escrituras,
nuevas plataformas/rendimiento/fuzzing de rutas, refactor de todos los consumidores de rutas; las sondas del
review no los convierten en garantías. (2) 6 opcionales del review, **propuestos para posterior y sin
priorizar**: O1 `verify-begin` con raíz relativa, O2 checkpoint por API + raíz symlink, O3 bytes del cuerpo
con raíz symlink, O4 `test_D` siempre desde copia aislada con scripts byte a byte, O5 `ValueError` en helpers
privados, O6 lista de ADR `Proposed` desactualizada (preexistente). (3) Drift de instalaciones globales: la
validación aislada no lo repara. (4) Desviación trazable 17/18: el RED 17 precedió a una enmienda del plan y
su registro se hizo en el intento 18 declarando el desfase — no prueba un `begin` previo al transporte ni se
usa como precedente. (5) Resultado fuera de alcance **invalidado**: el reviewer del intento 23 copió un
`private_path` y no acreditó la comparación por bytes; su PASS no es aprobación (`aa03482`). (6) La
extracción de interfaz por architect se detuvo por **cuota del modelo**; RED se reencauzó por introspección
pública.

**Next feature in queue:** `010-004-packet-dispatch-ergonomics` (instrucción del usuario, antes de `010-001`,
`010-002` y `010-003`), partiendo de `observations-packet-dispatch.md`. Cierre local propuesto, **sin
publicación ni instalación global**.
```

## Sección 2 — `docs/progress.md`

**(2.a) `## In progress`:** la feature no figura hoy; no hay línea que retirar.
**(2.b) Insertar como primera entrada de `## Done` (línea 13), sólo una vez aprobado:**

```markdown
- **010-000-continuity-relative-root** (2026-10-29, epic 010 — **1/5**) — la continuidad, la planificación,
  la verificación de paquetes y la clasificación aceptan raíces equivalentes (`.`, relativa, absoluta, por
  symlink al mismo proyecto) sin alterar la evidencia portable ni debilitar controles: se canonicaliza la
  raíz en los bordes y toda pertenencia compara resuelto contra resuelto. Contrato `spec.md`
  `623b15e1…f01737e2` (PC-01..PC-08, 5 `deferred-hardening`). Review `review.md` sin bloqueantes, 6
  opcionales propuestos para posterior. Gate **1849 passed / 5 skipped por composición** (225 casos
  recuperados en 23 lotes rc=0 sobre fuente equivalente; la corrida original conserva rc=1) — **no** es una
  corrida única verde. Aislado: `install.sh`, `--check` y `make validate` rc=0; global sigue en drift;
  sanitización privada 68/68 sin copiar el fichero privado. Deuda, desviación 17/18 y resultado invalidado
  en `docs/specs/010-000-continuity-relative-root/closure-evidence.md`. Sin publicación ni instalación global.
```

## Sección 3 — ADR: **No ADR sugerido**

D1–D3 son la decisión de diseño del contrato ya aprobado, no una decisión arquitectónica nueva: la
canonicalización en los bordes es aplicación de ADR-038 (admisión en cada frontera y comparación por bytes),
con ADR-016 y ADR-017 intactas. Elevarla a ADR fijaría como arquitectura ratificada una invariante que O5
demuestra **no uniforme** (tres helpers privados aún exigen raíz ya resuelta) y convertiría una convención de
borde en garantía. Sí procedería un ADR (**Confidence: Media**) si el usuario decide imponer la raíz canónica
a todos los consumidores —incluido O5— y cerrar TOCTOU; hoy eso es deuda, no decisión. La entry de
`activeContext` vale sin ADR.

---

**Reporte de rol** — Modified files: **ninguno** (`write_scope: []`; tampoco edité el Memory Bank ni el state). Commands: `python3 scripts/cdad_packet.py validate-request|validate-packet|render …` (rc=0), `cmp`/`sha256sum`, `git diff --stat 34dcd9b..HEAD`, `git rev-parse HEAD`, lectura de los 5 inputs + `activeContext.md`/`progress.md`/`plan.md`/`state`. Output: el citado arriba (rc=0, `IDENTICAL`, 225 nodeids únicos en 23 lotes `all_rc_zero`). **No corrí suite ni instalé nada.** Commit: **ninguno** (patrón Scribe: drafts → aprueba Pablo → materializa el orquestador). Aprobación pendiente de tu decisión.
