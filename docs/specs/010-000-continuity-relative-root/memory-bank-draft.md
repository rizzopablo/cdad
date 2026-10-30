> Nota de publicación: rutas locales anonimizadas con autorización del usuario.
> El original literal se conserva privadamente en `.cdad/publication/` y en el
> historial local; los resultados y hashes históricos no se recalcularon ni se
> presentan como producidos por los comandos editados para publicación.

## Validación de intake (ruta A) — antes de trabajar

| Check | Resultado |
|---|---|
| Marcadores `---cdad-packet-json` en el prompt | **exactamente 1**, con su cierre `---end-cdad-packet-json` |
| Comparación byte a byte: recibido vs `render` canónico **completo** (marcador → fin del paquete) | `equal: True`, sha256 recibido = canónico = `61c8998488e62588da115853f7e84b3a20472b0d9b8fb27cc25962cc694aad41` (5864 bytes ambos) |
| `render` vs `PACKET.md` publicado | sha256 idéntico (`61c89984…aad41`) |
| `validate-request` (CLI del repo, raíz absoluta, contexto declarado) | `rc=0` |
| Contrato `docs/specs/010-000-continuity-relative-root/spec.md` | sha256 `623b15e1…f01737e2` = declarado ✅ |

Comandos exactos y salidas relevantes:

```
python3 scripts/cdad_packet.py render --project-root <project-root> \
  --execution-context .cdad/executions/exec-010-000-continuity-relative-root-001/execution.json \
  --request .cdad/packets/010-000-continuity-relative-root-scribe-memory-001/REQUEST.json   → rc=0
sha256sum render vs PACKET.md → 61c8998488e62588da115853f7e84b3a20472b0d9b8fb27cc25962cc694aad41 (ambos)
python3 scripts/cdad_packet.py validate-request … (mismos args) → rc=0
sha256sum docs/specs/010-000-continuity-relative-root/spec.md → 623b15e1…f01737e2
```

Paquete íntegro. Procedo solo con los insumos declarados y el Memory Bank vigente. **No edité archivos** (un `write` a `/tmp/opencode` fue denegado por permisos; la comparación íntegra se hizo por stdin, igual que el reviewer).

---

# BORRADOR DE MEMORY BANK — 010-000 (FINAL TEXT, pendiente de aprobación del usuario)

> **Advertencia de estado, no negociable en la materialización:** estos borradores **no declaran cierre logrado**. La suite completa tiene log sin resumen ni `rc` (17 líneas, última ~66 %), y `make validate`/`validate-subagents` está en `rc=1` por drift de instalaciones globales, no por la fuente. Ninguna sección de abajo puede materializarse como «cerrada» hasta que exista resumen y `rc` reales de la suite y el usuario apruebe.

## Sección 1 — Propuesta de entrada `docs/activeContext.md`

Insertar como primera entry (después de `# Active Context` / `---`, encima de `## 2026-10-29 — Cierre de epic-009-installer-updates (2/2)`):

```markdown
## 2026-10-29 — Feature: 010-000-continuity-relative-root (epic 010)

**Cierre pendiente, no logrado.** El defecto: un candidato ya resuelto a absoluto se comparaba contra la
raíz tal como venía escrita, así que `.`, un nombre relativo o una raíz por symlink al mismo proyecto
podían rechazarse como si escaparan. La corrección canonicaliza la raíz **en los bordes** —
`cdad_packet._canonical_project_root()` (`resolve(strict=False)`, `PolicyError` si no resuelve), aplicada en
`_project_path`, `classify_path_observable`, `verify_published_packet`, `plan_write` y `_run_write` — de modo
que toda comprobación de pertenencia compara resuelto contra resuelto. Solo se canonicaliza la raíz: los
campos portables (referencias, cuerpo durable, digests) conservan el texto relativo que declaran
(PC-04). Fuente: 2 scripts del skill, `+33/−8`; tests `+24/−23`, sin cambio de oráculos en GREEN.

**Decisiones relevantes.**
- **D1 — Canonicalizar la raíz, no la variable del CLI.** Normalizar el argumento local dejaba incoherentes
  a los handlers y a las entradas programáticas; la spec descartó además las excepciones para `"."` y exigir
  rutas absolutas al usuario (`spec.md` §«Decisión de diseño»). Costo aceptado: un helper privado que reciba
  la raíz sin resolver ahora falla con `ValueError` en lugar de `PolicyError` (O5), fuera de las entradas
  comprometidas y fail-closed.
- **D2 — Se conserva el containment existente y se separa la deuda.** `update.references` mantiene su
  control **léxico**; el containment resuelto de esas referencias no entra en esta unidad y queda como deuda
  de seguridad explícita. Aceptar raíces relativas no debía debilitar barreras (PC-07).
- **D3 — La corrección se acredita en el consumidor instalado, no en el checkout.** PC-08 exige staging +
  instalación **aislada**; se mantiene la prohibición de tocar la instalación global como sustituto de
  corregir la fuente.

**Technical debt detected.**
- `deferred-hardening` de la spec (5 ítems, íntegros y sin degradar): containment resuelto de
  `update.references`; TOCTOU de symlinks y cambios concurrentes; fallos de disco e interrupciones entre
  escrituras; nuevas plataformas/rendimiento/fuzzing de rutas; refactor de todos los consumidores de rutas.
  Las sondas del reviewer no convierten estos pendientes en garantías.
- Review sin bloqueantes con **6 opcionales** (O1–O6) y **2 abstenciones**; disposición propuesta en
  `closure-evidence.md`, **pendiente de decisión de Pablo**, sin elevarlas a requisitos.
- **Gates abiertos, declarados como tales:** suite completa en curso (log sin resumen ni `rc`);
  `validate-subagents` en `rc=1` por drift de copias **globales** (`.claude`, `.agents`, `.config/opencode`,
  incluidos dos `.pyc`), no por la fuente ni por la instalación aislada.
- **Desviación trazable:** el despacho RED 17 precedió a una enmienda del plan; su registro falló por drift
  contractual y el orquestador registró bajo el intento 18 el texto obtenido en el 17, declarando el
  desfase. **No es prueba de un `begin` previo al transporte del 18** y no se usa como precedente normativo.
- La extracción de interfaz por architect se detuvo por **cuota del modelo**; RED se reencauzó con
  introspección pública, sin lectura de implementación.
- Incidencia de transporte: una re-recepción del mismo paquete colisionó por nombres de partes; se conservó
  el recibo anterior, sin forzar reemplazo (alimenta `010-004`).

**Next feature in queue:** `010-004-packet-dispatch-ergonomics`, por instrucción del usuario y **antes** de
las tres features documentales (`010-001`, `010-002`, `010-003`). Investigar los tres fallos observados
(`docs/epics/epic-010-documentary-specialization/observations-packet-dispatch.md`) antes de elegir
mecanismo. No publicar ni cambiar modelos por cuenta propia.
```

## Sección 2 — Propuesta de entrada `docs/progress.md`

**(2.a) Estado a materializar hoy (honesto, sin mover a `Done`).** En `## In progress` (línea 5), añadir al final de esa sección:

```markdown
- **010-000-continuity-relative-root** (epic 010, **1/5**) — *en cierre, no cerrada*: fix de raíces
  equivalentes en continuidad y packet (`_canonical_project_root`, 2 scripts del skill) con review
  independiente **sin bloqueantes** (6 opcionales, 2 abstenciones). **Gates abiertos:** suite completa sin
  resumen ni `rc`; `validate-subagents` `rc=1` por drift de instalaciones **globales** —la fuente y la
  instalación aislada se revisaron por separado—. Evidencia y límites:
  `docs/specs/010-000-continuity-relative-root/closure-evidence.md`.
```

**(2.b) Entrada `Done` condicionada** — mover el bloque anterior a `## Done` **solo** tras completar los dos marcadores `PENDIENTE`. No materializar con los marcadores dentro:

```markdown
- **010-000-continuity-relative-root** (2026-10-29, epic 010 — **1/5**) — la continuidad, la planificación,
  la verificación de paquetes y la clasificación aceptan raíces equivalentes (`.`, relativa, absoluta y por
  symlink al mismo proyecto) sin cambiar evidencia portable ni debilitar controles: la raíz se canonicaliza
  en los bordes (`_canonical_project_root`) y toda pertenencia compara resuelto contra resuelto; solo la
  raíz se normaliza, las referencias y el cuerpo durable conservan su texto relativo. **Contrato:**
  `spec.md` `623b15e1…f01737e2` (PC-01..PC-08, D1–D3, `deferred-hardening` de 5 ítems). **Producto:**
  `skills/cdad-cycle/scripts/cdad_packet.py` `+26/−7`, `cdad_continuity.py` `+7/−1`; tests
  `test_010_000_continuity_relative_root.py` `+24/−23` (5 casos: A, A2, B, C, D), sin cambio de oráculos en
  GREEN. **Review:** `review.md` `7845614e…` sin bloqueantes, 6 opcionales, 2 abstenciones; consumidor
  instalado verificado en copia aislada (1 caso, 19.85 s). **Gate: PENDIENTE** — `PENDIENTE: resumen y rc de
  la suite completa (`.cdad/evidence/full-suite-010-000.log`)`; `make validate` **rojo por drift de
  instalaciones globales**, no por la fuente. **Deuda:** `deferred-hardening` de la spec íntegro, O1–O6 con
  disposición propuesta (no aprobada), y la desviación trazable de continuidad 17/18, que no se presenta como
  continuidad íntegra. **No implica publicar ni instalar globalmente.**
```

**Nota de cola (opcional, misma edición):** en `## Queued` (línea 1093) no hace falta agregar nada: `010-004` ya está `queued` en `.cdad-state.json` con dependencia de `010-000`. Si se quiere visibilidad en el Memory Bank, una sola línea — «**epic-010 — siguiente:** `010-004-packet-dispatch-ergonomics` (raíces relativas resueltas; transporte y contexto de ejecución); después `010-001` → `010-002` → `010-003`».

## Sección 3 — ADR

**Sugerido: sí**, como **ADR-040 — Proposed**, con `Confidence: Media-baja`. Motivo: el cambio fija una invariante transversal (una sola raíz canónica en los bordes, texto portable intacto) que todos los consumidores de rutas futuros deben respetar, y el propio review mostró que **no está impuesta uniformemente** (O5). No se materializa sin ratificación de Pablo; alternativa legítima y más conservadora: **no ADR**, por considerarlo aplicación directa de ADR-038 (admisión en cada frontera invocable). Si el usuario prefiere esa lectura, la entry de `activeContext` sigue valiendo sin ADR.

```markdown
# ADR-040: Una sola raíz canónica en los bordes; la evidencia portable conserva su texto relativo

- **Status**: Proposed (pendiente de ratificación del dueño; epic-010, `010-000-continuity-relative-root`).
- **Date**: 2026-10-29
- **Confidence**: **Media-baja** — el comportamiento está evidenciado en las cinco superficies del contrato
  y en el consumidor instalado aislado, pero la invariante **no está impuesta en todos los consumidores**:
  tres helpers privados siguen esperando una raíz ya resuelta y fallan con `ValueError` (O5, fail-closed,
  fuera de las entradas comprometidas). La suite completa aún no tiene resumen ni `rc`.
- **Origen**: `docs/specs/010-000-continuity-relative-root/spec.md` (D1–D3, PC-01..PC-08),
  `docs/specs/010-000-continuity-relative-root/review.md`.

## Contexto

Un candidato resuelto a absoluto se comparaba contra la raíz **tal como venía escrita**. Consecuencia: `.`,
un nombre relativo de directorio y una raíz expresada por symlink al mismo proyecto podían rechazarse como
escape, mientras la ruta absoluta equivalente funcionaba. El defecto no era del CLI: los handlers, la API de
planificación, la verificación de paquetes y la clasificación compartían la misma comparación asimétrica.
Normalizar una variable local del CLI no lo corregía.

## Decisión

1. **Una sola definición** de raíz canónica (`_canonical_project_root`) aplicada **en los bordes**: CLI de
   continuidad (`begin`, `checkpoint`), `plan_write`, `verify_published_packet`, `classify_path_observable` y
   `_project_path`. Toda pertenencia compara **resuelto contra resuelto**.
2. **Solo la raíz se canonicaliza.** Referencias, cuerpo durable, digests e identidad conservan el texto
   relativo declarado: la corrección no debe meter rutas absolutas en la evidencia portable.
3. **El containment existente se conserva**, no se reemplaza: sigue rechazándose `..`, rutas absolutas donde
   se exige relativa y symlinks que resuelven fuera del proyecto.
4. **Los controles léxicos que hoy existen no se elevan ni se degradan** en esta decisión:
   `update.references` mantiene su normalización léxica y su limitación declarada como deuda de seguridad.
5. **La corrección se acredita en el consumidor instalado** en entorno aislado; la instalación global no es
   sustituto de corregir la fuente.

## Alternativas rechazadas

- **Normalizar el argumento en el CLI.** Deja incoherentes a los handlers y a las entradas programáticas: el
  mismo defecto reaparece por la API.
- **Excepciones para `"."` o exigir raíces absolutas al usuario.** Trata un síntoma y deja la familia del
  defecto abierta; traslada al usuario una restricción accidental.
- **Un subsistema nuevo de rutas o refactor de todos los consumidores.** Amplía el alcance sin promesa nueva
  y arriesga las interpretaciones relativas que la spec manda conservar.
- **Añadir containment resuelto a `update.references` en este mismo fix.** Es una decisión de seguridad y
  compatibilidad distinta; se mantiene separada y explícitamente pendiente.

## Consecuencias

- **Positivas:** la forma de expresar la raíz deja de impedir trabajar; replay e idempotencia se conservan
  (`no_op` real, cadena sin cambios); la comodidad no amplía autoridad (admisión y orden
  identidad → replay → elegibilidad intactos).
- **Negativas / límites:** la invariante es **convención de borde**, no tipo: quien llame un helper privado
  con una raíz sin resolver obtiene `ValueError` en lugar de `PolicyError` (O5, fail-closed). `TOCTOU`,
  fallos de disco y el containment resuelto de `update.references` siguen abiertos.
- **Vigilancia:** cualquier consumidor nuevo de rutas debe pasar por la raíz canónica o documentar la
  precondición.
```

## Anexo A — Bases observadas (para verificación en la materialización)

| Base | sha256 |
|---|---|
| `docs/specs/010-000-continuity-relative-root/spec.md` | `623b15e14290739f6f7c099183a06348b91bcce02eac4dce37265019f01737e2` |
| `docs/specs/010-000-continuity-relative-root/review.md` | `7845614e2b5a262fdcdd8ac59d245001a368662ff9ffba2896b1250abcab245b` |
| `docs/specs/010-000-continuity-relative-root/closure-evidence.md` | `3d0c2ae96b0810d7d61730c98d906689527b80b265ac3ef8630a7a6da7c50726` |
| `docs/epics/epic-010-documentary-specialization/plan.md` | `b9375189b674dce8197f1cd69e79f5eba2934a92688d612607361db2edd5c698` |
| `docs/epics/epic-010-documentary-specialization/execution.md` | `9bf279098ea349bb79ea38a8ed32912c039a4b3fbba07cca175af1a3d510e46f` |
| `docs/epics/…/observations-packet-dispatch.md` | `b59839df02f6a78335259900f90f53523e1c48f68550bb889f0819c79d410ad8` |
| `tests/test_010_000_continuity_relative_root.py` | `6f5f84ef1fe1dd118951cb1e5b32c6259fa25201fae09dcc090b2d2945249ad9` |
| `.cdad/evidence/validate-subagents-010-000.log` | `103dd0011e9fce9997e80a32a5f15d8a6d7788fcd3037b624fb932bd15d3f177` |
| `.cdad/evidence/full-suite-010-000.log` (en curso) | `2d9d1136273bc281f69e2b776a2bb304b618f3cca4b5fcadca5a591f57447ccd` |
| `docs/activeContext.md` / `docs/progress.md` / `docs/systemPatterns.md` / `docs/.cdad-state.json` | `40599bcf…`, `d88a1ed3…`, `3ea2e05b…`, `927021cf…` |
| Rango revisado | `34dcd9b..HEAD` (`HEAD = e427777`), 8 archivos, `+582/−41` |

## Anexo B — Disposiciones pendientes de decisión del usuario (no son requisitos)

| Ítem | Naturaleza | Disposición **propuesta** (sin efecto hasta que Pablo decida) |
|---|---|---|
| DH-1 containment resuelto de `update.references` | deuda de **seguridad** de la spec | unidad/ADR separada; no ampliar este fix |
| DH-2 TOCTOU de symlinks y concurrencia | deuda de la spec | diferida; se conserva la comprobación sobre el FS examinado |
| DH-3 fallos de disco / interrupciones | deuda de la spec | diferida; no es la causa del defecto |
| DH-4 plataformas, rendimiento, fuzzing | deuda de la spec | diferida; sin promesa nueva |
| DH-5 refactor de todos los consumidores de rutas | deuda de la spec | diferida; superficie afectada + controles compartidos |
| O1 `verify-begin` sin test con raíz relativa | opcional (review) | sonda del reviewer ya vio `rc=0` y mismo `body_sha256`; proponer **ampliación de regresión posterior**, no bloqueante |
| O2 `plan_write(checkpoint)` y raíz symlink sin test | opcional (review) | igual: comportamiento verificado en fixture; regresión posterior |
| O3 variante symlink en `test_A` sólo compara `record/seq/no_op` | opcional (review) | comparación byte a byte como hardening de test |
| O4 `test_D` puede saltar `make staging` con manifiesto stale | opcional (review) | aislar copia siempre + comparación byte a byte de scripts instalados: **reproducibilidad**, no corrección |
| O5 helpers privados con `ValueError` en vez de `PolicyError` | opcional (FYI) | corrección posterior acotada; **no** ampliar firmas ni debilitar containment ahora |
| O6 tabla de ADRs `Proposed` desactualizada (ADR-037/038/039) | opcional **preexistente** | mantenimiento de Memory Bank, **sin atribuirlo** a este fix |

## Anexo C — Registro honesto de desfases y límites

- **Continuidad 17/18:** desfase declarado y conservado como desviación trazable; **no** se presenta como continuidad íntegra ni como precedente. `head.json` vigente: `attempt: 22`.
- **Cuota del architect:** la extracción de interfaz se detuvo por cuota del modelo; RED se reencauzó con introspección pública sin lectura de implementación.
- **Suite completa:** log de 17 líneas sin resumen ni `rc`. **No se afirma éxito.** Corresponde al **closer** correr la suite una vez (política común del paquete).
- **`make validate` / `validate-subagents`:** `rc=1`; causa registrada = drift de copias **globales** (`~/.claude`, `~/.agents`, `~/.config/opencode`, incluidos `__pycache__/*.pyc`), con agentes de runtime `10/10 OK`, artefactos OK y política de modelos OK. No se corrigió ni se ocultó: no hay autorización para tocar instalaciones globales.

---

## Reporte de rol

**Archivos modificados: ninguno.** (Intento de `write` a `/tmp/opencode` → `Permission denied: edit`; por eso la comparación byte a byte se hizo por stdin, sin escribir archivos.)

**Comandos ejecutados (ruta local anonimizada):** `scripts/cdad_packet.py render` y `validate-request` con `--project-root <project-root> --execution-context .cdad/executions/exec-010-000-continuity-relative-root-001/execution.json --request .cdad/packets/010-000-continuity-relative-root-scribe-memory-001/REQUEST.json` (ambos `rc=0`); `sha256sum` sobre contrato, review, closure-evidence, plan, execution, observations, tests y logs; `git diff --stat/--numstat 34dcd9b..HEAD`; `git log --oneline 34dcd9b..HEAD`; `git status --short`.

**Salidas clave:** render = PACKET.md = recibido (`61c89984…aad41`); contrato `623b15e1…` ✅; diff `34dcd9b..HEAD` = 8 archivos `+582/−41`, producto `+33/−8`, tests `+24/−23`; `git status --short` = solo `?? docs/specs/010-000-continuity-relative-root/discovery.md` (fuera del rango); `validate-subagents` → `RESULT: FAIL` (drift global, `rc=1`).

**Commit: ninguno** — rol read-only, los borradores los aprueba el usuario y los ejecuta el orquestador (ADR-003/ADR-011).

**No aprobé nada, no edité archivos, no corrí la suite, no instalé, no publiqué, no abrí el Memory Bank a escritura.** Los borradores quedan a la espera de tu aprobación; si aprobás, decidí también el ADR (sugerido ADR-040 *Proposed*, confidence Media-baja) frente a la alternativa «no ADR» por aplicación de ADR-038, y la disposición de DH-1..DH-5 y O1..O6.
