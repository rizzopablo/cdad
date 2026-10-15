# Verificación T3/T4 review-fix 2 (004-002) — OpenCode glm-5.3-flash, 2026-10-01

> Paquete `004-002-project-execution-bootstrap-reviewer-review-004`, worktree fijado en `814c980`. Materializado verbatim; las rutas de sondas son temporales del reviewer.

**Dictamen: 2 hallazgos bloqueantes, 2 mejoras opcionales (1 nit) y 2 abstenciones.** Las siete garantías del alcance (A-1, A-2/B-3, A-3, A-4, B-1, B-2, B-5) están implementadas correctamente —lo verifiqué con sondas CLI propias, incluida una muerte real por SIGKILL en la ventana de commit—, pero la exclusividad de modos conserva una brecha (`reconcile` + `--input`) y una rama de recuperación de B-1 no tiene test que la fije (mutación superviviente sobre la suite completa).

Revisión sobre `814c980` (delta `fc184c1..814c980`) en el worktree propio. SHA-256 del contrato verificado: `f72e65403482bc35065f10bd14ec00dec9c3d3a4ba8ce519e6ef860ef107b57c` — coincide con el packet. No modifiqué producto ni tests, ni hice commits; `git status --short` quedó sin salida. Todo lo ejecutado corrió en primer plano.

## Hallazgos bloqueantes

**R-1 — Required/Critical: `reconcile` admite `--input` (opción ordinaria) y la descarta en silencio.**
**Verdict: BLOCKING · Bucket: h**

Ubicación: [cdad_packet.py:2120](skills/cdad-cycle/scripts/cdad_packet.py:2120) — en `_reject_mode_mix`, la rama del modo `reconcile` excluye `--input` de los foráneos (`foreign = [f for f in ordinary + record + resume if f != "--input"]`). La exención de `--input` es legítima solo para el modo `record` (línea 2123, donde `--input` es el documento de observación); en `reconcile` es una opción ordinaria (el prepare ordinario la consume como `inputs` del paquete) y el enunciado del fix la cubre: «`--reconcile-policy` con cualquier opción ordinaria → rc 2 sin escrituras» y «reconcile solo admite `--decision-ref`» (I5d).

Sonda reproducible (rc 0, `policy_history` crece a 2, `execution.policy_sha256` reconciliado; `--input` jamás usado):

```bash
python3 - <<'EOF'   # proyecto sintético build_project; bootstrap; paquete completed
prepare --project-root <root> --reconcile-policy <sha> --decision-ref docs/dec.md --input <obs.json>
# → rc 0; history=2; policy_sha256==sha; ninguna mención de --input
EOF
```

Es la misma clase de defecto que A-2 corregía («descarta en silencio una de las operaciones»). Remedio estructural: mover la exención de `--input` a la rama `record` exclusivamente (`foreign = ordinary + reconcile + resume` en reconcile, sin filtro). Los dos tests A-2 nuevos tampoco cubren esta variante: añadir `--input` a la invocación mixta de `test_a2_reconcile_plus_ordinary_options_rejected_no_writes` (o un caso propio) para que la regresión no vuelva.

**R-2 — Required: la rama de recuperación de B-1 (registro ya en disco + transición pendiente) no tiene test; la mutación sobrevive la suite completa.**
**Verdict: BLOCKING · Bucket: h**

Ubicación: [tests/test_004_002_t34_reviewfix2.py:727](tests/test_004_002_t34_reviewfix2.py:727) (`TestB1RecordAtomicWithState`) e implementación [cdad_packet.py:1729](skills/cdad-cycle/scripts/cdad_packet.py:1729). `test_b1` solo ejercita el fallo de *staging* (docs/ no escribible): en su reintento `already_recorded` es falso. La rama `already_recorded and transition_pending` —el reintento tras una **muerte real en la ventana entre los dos `os.replace`** (registro renombrado, state no)— no es alcanzada por ningún test: la mutación `M-B1b` (`if already_recorded: return` antes de completar la transición) deja la suite de 9 archivos en **127 passed** (verificada sobre copia mutada). El test declara cubrir «el reintento idéntico completa la transición» y no lo hace para ese camino.

La implementación está bien (sonda fase 2, sin mutación): SIGKILL antes del rename del state con el registro ya renombrado → registro publicado con state `prepared`; reintento idéntico → rc 0 y `dispatched`. El defecto es de cobertura del test, pero fija una garantía nombrada de este mismo ciclo de review-fix. Remedio: un test que siembre registro-en-disco + state `prepared` (p. ej. restaurando el state previo, o matando en la ventana como en mi sonda) y afirme que el reintento deja `dispatched`; con eso `M-B1b` queda detectada.

## Mejoras opcionales / nits

**R-3 — Nit: el marcador `.cdad-txn` no está autenticado; un directorio ajeno que lo porte es limpiado.**
**Verdict: OPTIONAL · Bucket: h**

Ubicación: [cdad_packet.py:973](skills/cdad-cycle/scripts/cdad_packet.py:973). Caso ambiguo verificado por sonda: un directorio ajeno dentro de `.cdad/.txn` que contiene un archivo plantado llamado `.cdad-txn` es tratado como propio y la recuperación **borra su `execution.json`** (el resto de nombres propios también). Todo directorio ajeno sin manifiesto se conserva íntegro (probado con 5 archivos + archivo suelto en la raíz de `.txn`). Es un caso hostil/pathológico (plantar el marcador requiere escribir dentro de `.cdad`), por eso OPTIONAL: documentar la ambigüedad o reforzar la propiedad (p. ej. manifestar identidad de creación verificable) si se quiere cerrar del todo.

**R-4 — Nit: el punto de pausa `before-lock-open` queda antes de la decisión de creación, no después como dice el comentario/I5d.**
**Verdict: OPTIONAL · Bucket: h**

Ubicación: [cdad_packet.py:1039-1044](skills/cdad-cycle/scripts/cdad_packet.py:1039). El comentario afirma «sits after deciding whether the file must be created and before opening it» y plan I5d dice «después de decidir si hay que crear el archivo y antes de abrirlo»; en el código la pausa precede al `exists()` que decide la creación (y al `mkdir` de `.cdad`, que ocurre antes). Sin daño observable en las carreras usadas (mismo resultado; solo deja `.cdad` creado mientras el proceso está pausado). Ajustar el comentario o mover la pausa una línea abajo para que el texto y el código coincidan.

**FYI — redundancia de `--attempt-id` (no defecto):** la mutación `M-B3` (quitar el check explícito de main) sobrevive porque `_reject_mode_mix` ya rechaza todo argv con `--attempt-id` fuera de `--record-dispatch`, y el check explícito residual queda enmascarado por el requisito `--role/--substage/--objective` del prepare ordinario. Defensa en profundidad válida; no requiere acción.

## Tabla de cierre por hallazgo

| Garantía | Sonda propia (CLI real, no solo lectura) | Resultado | Mutación | Estado |
|---|---|---|---|---|
| **A-1** (Critical): perdedor nunca borra `.lock`; solo adquisición verificada (flock+inodo) y creada con O_EXCL retira en fallo | 3 escenarios: (1) A tenedor `reserved-id` + B perdedor `before-lock-open` + C observador → B rc 2 «busy», `.lock` intacto con inodo de A, C rc 2, árbol/state intactos, A publica 1 paquete con bytes==stdout; (2) B y C ambos pausados sin `.lock` previo → B crea (O_EXCL) y publica, C pierde sin retirar; (3) A falla por PD-5 tras adquisición verificada → retira SU `.lock`+`.cdad` (PD-3), siguiente prepare limpio | PASS | `M-A1` (perdedor borra: except-borra-en-adquisición-fallida) **detectada** (2 failed); `M-A1b` (`__exit__` sin `_acquired`) detectada por `TestF1` de t3_reviewfix; `M-I5d` (pausa eliminada) detectada | CIERRA A-1 |
| **A-2** (exclusividad en main, una vez, antes del lock) | 10 argv mixtos: reconcile+record+attempt-id, reconcile+role/substage/objective, reconcile+read-scope, ordinario+attempt-id, attempt-id+input sueltos, resume+record, reconcile sin decision-ref, decision-ref sin reconcile, record sin input, resume+ordinarias → todos rc 2, sin getopt, árbol y state intactos | PASS **salvo** `reconcile+--input` → rc 0, descartada en silencio (**R-1**) | `M-A2` (sin `_reject_mode_mix`) **detectada** (2 failed) | **NO CIERRA del todo (R-1)** |
| **B-3** | ordinario+`--attempt-id` → rc 2 sin escrituras | PASS | `M-B3` sobrevive (redundante; ver FYI) | CIERRA B-3 |
| **A-3** (fstat vs stat; fd de inodo retirado no entra) | vía test RED + harness `_rf2_open_pause.py` (B con fd del inodo viejo tras retiro de A; C nuevo) — suite | PASS (test_a3) | `M-A3` (sin verificación de inodo) **detectada** | CIERRA A-3 |
| **A-4** (recuperación borra solo transacciones propias, manifiesto `.cdad-txn`) | 2 interrupciones `context-written` + dir ajeno con execution.json/REQUEST.json/PACKET.md/state.json/extra + archivo suelto en raíz + caso con manifiesto plantado; recuperación rc 0, `validate-state` rc 0, ajenos íntegros | PASS salvo caso de manifiesto plantado (**R-3**, nit) | `M-A4` (limpieza sin manifiesto) **detectada** | CIERRA A-4 |
| **B-1** (registro+state en una transacción; reintento completa prepared→dispatched) | (1) staging falla (docs 0o555) → rc 2, sin registro, state `prepared`; reintento → rc 0 `dispatched`; (2) SIGKILL en ventana exacta entre renames (os.replace parcheado externamente) → registro publicado, state `prepared`; reintento idéntico → rc 0 `dispatched`; (3) directa `_publish_dispatch_atomic` con rename del state forzado a fallar → PolicyError, registro renombrado **retirado**, sin temporales | PASS (implementación); cobertura del test **incompleta** (**R-2**) | `M-B1a` (publicación no atómica) **detectada**; `M-B1b` (reintento sin transición) **SOBREVIVE la suite completa (127 passed mutado)** | **NO CIERRA del todo (R-2)** |
| **B-2** (provenance claves cerradas) | claves extra `result`/`gate`/`postconditions_status`/`model_reported_x`/`RUNTIME` → rc 2 con diagnóstico de las cinco permitidas, sin registro y sin escrituras; válido con las 5 claves → rc 0; `provenance: {}` con nulls → rc 0 | PASS | `M-B2` (claves abiertas) **detectada** | CIERRA B-2 |
| **B-5** (multi-runtime case-insensitive) | `Multi-Runtime` / `MULTI-RUNTIME` / `multi-runtime` / `␣multi-runtime␣` → todos rc 2 sin registro ni escrituras | PASS | `M-B5` (comparación case-sensitive revertida) **detectada** | CIERRA B-5 |

**Regresiones:** F1 (`.lock` permanente tras éxito — sonda), F2 (reserva bajo lock — test_a1/test_b4b + suite), F3 (rollback solo archivos propios — manifiesto compartido), F4/F5 (una sola lectura + binding coherente: `validate-state` rc 0 inmediato tras reconcile, snapshot reproduce bytes exactos — sonda), F6 (snapshot+sha en el paquete publicado — sonda). T1/T2 y el resto de la suite en verde. Ganchos inertes: sin variables → comportamiento normal y sin artefactos; `PAUSE_AT` sin `PAUSE_FILE` → inerte; `FAIL_AT` con punto inexistente → inerte. T5/T6: **RED por diseño** (23 failed), no contados.

## Tabla de mutaciones

Sobre copias en `/tmp/opencode/rf2-review/mut*/` (nunca el worktree ni el repo principal), contra `tests/test_004_002_t34_reviewfix2.py` (y suite amplia para los supervivientes):

| Mutación | Garantía | Resultado | Tests que la detectan |
|---|---|---|---|
| M-A1 perdedor borra `.lock` en fallo de adquisición | A-1 | **Detectada** (2 failed) | test_a1, test_b4b |
| M-A1b `__exit__` retira sin `_acquired` | A-1/F1 | Detectada (suite amplia: 1 failed) | TestF1 (t3_reviewfix); no en reviewfix2 |
| M-I5d pausa `before-lock-open` eliminada | A-1/I5d | **Detectada** | test_a1 |
| M-A2 sin `_reject_mode_mix` | A-2 | **Detectada** (2 failed) | test_a2×2 (+test_b4a) |
| M-B3 check explícito de `--attempt-id` eliminado | B-3 | **SOBREVIVE** (redundante; `_reject_mode_mix` + requisitos del prepare lo cubren) | — |
| M-A4 limpieza sin manifiesto | A-4 | **Detectada** | test_a4 |
| M-B1a publicación registro/state no atómica | B-1 | **Detectada** | test_b1 (fase staging) |
| M-B1b reintento sale sin transición pendiente | B-1 | **SOBREVIVE la suite completa de 9 archivos (127 passed mutado)** | — (**R-2**) |
| M-B2 provenance claves abiertas | B-2 | **Detectada** | test_b2 |
| M-B5 runtime case-sensitive revertido | B-5 | **Detectada** | test_b5 |
| M-A3 sin verificación fstat-vs-stat | A-3 | **Detectada** | test_a3 |

9/11 detectadas. Los 2 supervivientes están explicados arriba (uno es redundancia aceptable, el otro es el hallazgo R-2).

## Evidencia de ejecución

- Suite solicitada (worktree `814c980`, tras `make staging` — rc 0, 2×12 archivos):
  `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_004_002_t1_policy.py tests/test_004_002_t1_reviewfix.py tests/test_004_002_t2_bootstrap.py tests/test_004_002_t2_reviewfix.py tests/test_004_002_t3_durable.py tests/test_004_002_t3_reviewfix.py tests/test_004_002_t4_dispatch.py tests/test_004_002_t34_reviewfix2.py tests/test_packet_prepare.py -q -p no:cacheprovider`
  → **127 passed in 199.49s** (0 fallos; T5/T6 no incluidos). Re-run de control al final: **127 passed**.
- Disciplina RED: árbol extraído con `git archive 291c492` (pre-fix) → `tests/test_004_002_t34_reviewfix2.py` = **8 failed, 3 passed**, todos por `AssertionError` sobre comportamiento ausente (A-1, A-2×2, B-3, A-4, B-1, B-2, B-5); los 3 que pasan ya estaban garantizados por fc184c1 (A-3/I5c, B-4).
- Sondas reproducibles (propias, en `/tmp/opencode/rf2-review/`): `probe_a1.py` (3 escenarios A-1), `probe_a2.py` (10 mixtos + control), `probe_b1.py` (3 fases B-1 con SIGKILL en ventana), `probe_rest.py` (A-4, B-2, B-5, inercia, F-spot), `kill_in_window.py` (instrumentación), `mutations.py` (mutaciones). Comando tipo: `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 /tmp/opencode/rf2-review/probe_a1.py` → «SONDA: todas las comprobaciones PASS».
- No leí `tests/.sensitive-patterns.local`. Nada en segundo plano; sin commits; sin escrituras al repo principal. Archivos modificados por mí: ninguno en el repo (solo artefactos en `/tmp/opencode/rf2-review/`).

## Abstentions

**AB-1 — Independencia de familia de modelo respecto del implementer.**
**Verdict: ABSTAIN · Bucket: m**

El packet declara `model.configured` y `model.reported` como `null`; no puedo verificar desde aquí la condición de independencia de familia ni la observación del modelo del implementer. La revisión se realizó en sesión independiente y sin adoptar conclusiones del autor como evidencia.

**AB-2 — Semántica de `flock` sobre NFS y runtimes no Linux.**
**Verdict: ABSTAIN · Bucket: m**

Todas las sondas corren en Linux local. PD-11 excluye la pérdida física del almacenamiento y no hay evidencia en el repo del comportamiento del rendezvous/inodo sobre NFS ni en otros sistemas operativos del runtime multi-runtime declarado; no emito dictamen sobre esos entornos.

## Disposición del orquestador

Validé R-1 contra el código (`_reject_mode_mix`, rama `reconcile`, línea 2120: exime `--input`).

- **R-1 (BLOCKING):** se corrige. La exención de `--input` queda solo en el modo `record`. Lleva un test con argv puro: reconcile + `--input` → rc 2 sin escrituras.
- **R-2 (BLOCKING, cobertura):** test nuevo que siembra registro en disco + state `prepared` y exige `dispatched` tras el reintento idéntico. Debe matar M-B1b.
- **R-3 (OPTIONAL):** se acepta como limitación declarada. Plantar el marcador exige escribir dentro de `.cdad`, que es estado del orquestador y queda fuera del modelo de amenaza de PD-11 (los roles no lo editan). No se agrega autenticación.
- **R-4 (Nit):** se mueve la pausa después de la decisión de creación, como dice I5d.
- **AB-1:** la familia sí es distinta (implementer `deepseek-v4.1-flash`, reviewer `glm-5.3-flash`); consta en el ledger. **AB-2:** NFS y otros SO quedan fuera del alcance declarado.

Se hace en un micro-ciclo (RED GLM → GREEN DeepSeek) después del GREEN de T5, que edita el mismo archivo. El cierre de T3/T4 queda condicionado a ese micro-ciclo.
