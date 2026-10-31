Validación completa y trabajo terminado. Informe final (para materializar como `red-t6.md`):

## 0. Validación Route C (antes de trabajar) — PASS

- Una sola identificación, sin cuerpo inline y sin marcador A (no hay mezcla de rutas).
- `render --route C` (repo, `--project-root <repo>`) coincide **campo por campo** con el bloque recibido: `project_root`, `packet_id`, `execution_id`, `execution_context`, `request`, `packet`, `contract` (kind/path/sha256/commit). Diferencias: **ninguna**.
- `validate-request` rc=0; `validate-packet` rc=0; `render` completo **byte-idéntico** al `PACKET.md` publicado (sha256 `caaa7fd9…` en ambos); `validate-state` → `VALID`.
- `spec.md` = `fc6b2ccc…d64`, igual al pin del request y del paquete.
- Toolchain: solo los scripts del repo (`skills/cdad-cycle/scripts/cdad_packet.py`); nada instalado ni modificado globalmente (D‑1 declarado por el despacho).

## 1. Las dos pruebas (archivo NUEVO `tests/test_010_004_t6_red.py`, 652 líneas, exactamente dos tests)

| Test | PC | Promesa observable | R4: sin este test el usuario… |
|---|---|---|---|
| `TestB2ActiveV1PacketDiagnosis::test_b2_active_v1_packet_is_diagnosed_and_escalated_without_effects` | PC‑07b / `spec.md:205,222,352` | Con paquete v1 activo `prepared` (contexto v1 en `.cdad/execution.json` + paquete publicado), `prepare` y `prepare --new-execution` devuelven rc≠0 con `ERROR:`, nombran el paquete que bloquea, no dicen «completar o fallar», declaran `owner` y `terminal`, y dejan árbol y state byte-idénticos | …sigue la indicación que hoy recibe (`prepare --new-execution`), choca con «complete or fail it» —orden que la spec prohíbe— y queda en callejón sin salida, sin ningún paso que escale al owner (bloqueante **B2**). |
| `TestB4ReplaceSuccessorDeclaresLocator::test_b4_replace_successor_declares_locator_over_historical_predecessor` | PC‑04 / `spec.md:462` | `prepare --replace-packet` publica un sucesor que declara el localizador canónico `.cdad/executions/<id>/execution.json` en request y cabecera **aunque el predecesor histórico no lo declarara**, sin reescribir el predecesor | …si esa línea se rompe, el sucesor se publica sin localizador y aun así pasa con `--execution-context` explícito: el defecto no se ve hasta el gate del padre, o no se ve (bloqueante **B4**). |

Fixtures (siempre en `tempfile`, nunca en el repo; `docs/cdad-policy.json` con los **bytes reales del repo**, contexto v2 canónico construido desde esos mismos bytes; contrato, autoridad HITL y aprobación pineada propios):

- **B2:** control positivo (a) primero —la misma fixture v2 sin paquete activo: `prepare` rc=0 y publica— y después el caso v1 con `.cdad/execution.json` `schema_version: 1` + `active_packet` `prepared` publicado en `.cdad/packets/<id>/{REQUEST.json,PACKET.md}`; instantánea sha256 del árbol completo y del state antes de correr.
- **B4:** control positivo (b) primero —predecesor que **ya** declara `execution_context`: `--replace-packet` rc=0, sucesor con el localizador, bytes del predecesor intactos— y después el caso histórico (campo retirado de request y cabecera). Obsolescencia verificable (PD‑8a) por la vía legítima: cambian los bytes del contrato y el registro `specification` se re‑pinea (el test no finge autoridad).

Nota de interfaz declarada: `--replace-packet` **no admite** flags de otro sub‑modo (el CLI responde `prepare sub-mode 'replace' admits no options from another mode; unexpected: --objective, --role, --substage`). Por eso se invoca con argv puro (`--replace-packet <id> --reason "<motivo>"`), igual que lo documentan `test_005_001_t2_replace_packet.py` y `test_006_006_w1_replace_draft_packet.py`; el sucesor conserva `role`/`substage` del predecesor (verificado: `test-writer`/`red`). No se duplica PC‑04a de `test_010_004_t2_red.py`: el control (a) no asserta el localizador, solo rc=0 y publicación.

## 2. Evidencia RED real

```
python3 -m pytest tests/test_010_004_t6_red.py -q --tb=short     # rc=1
F.                                                                       [100%]
=================================== FAILURES ===================================
_ TestB2ActiveV1PacketDiagnosis.test_b2_active_v1_packet_is_diagnosed_and_escalated_without_effects _
tests/test_010_004_t6_red.py:467: in test_b2_...
    self.assertIn(
E   AssertionError: 'legacy-v1-packet' not found in 'ERROR: an existing v1 execution context is present at .cdad/execution.json: ... Start the new v2 execution with `prepare --new-execution` (bootstrap); ...'
     : prepare: el diagnóstico no nombra el paquete v1 activo que bloquea ('legacy-v1-packet'), así que el usuario no sabe qué registro lo detiene
=========================== short test summary info ============================
FAILED tests/test_010_004_t6_red.py::TestB2ActiveV1PacketDiagnosis::test_b2_...without_effects
1 failed, 1 passed in 2.24s
```

El fallo es `AssertionError` de comportamiento ausente, **después** del control positivo (asserts del control en líneas 408‑434; fallo en 467). No es `ImportError`, `SyntaxError`, `FileNotFoundError` ni fixture rota: el mismo archivo compila y su segundo test pasa.

## 3. Declaración honesta de qué falla y qué queda verde

- **Falla (RED genuino, B2):** `prepare` sin `--new-execution` ofrece `prepare --new-execution` y **no nombra** el paquete v1 activo; la prueba corta ahí. Por contrato, el segundo comando tampoco cumple (el orquestador ya midió que responde «complete or fail», y ninguno de los dos declara `owner`/`terminal`); esas aserciones no llegan a ejecutarse porque la prueba se detiene en la primera.
- **Queda verde (guarda aceptada, B4):** el producto ya escribe el localizador en el sucesor de `--replace-packet`; la exigencia del contrato era **la prueba faltante**, no un cambio de conducta. No se debilitó ni se borró: control (b) + caso histórico con los mismos asserts 2‑4 y bytes del predecesor invariantes.

## 4. Diff y commit

```
git show --name-status --format= HEAD
A   tests/test_010_004_t6_red.py
git show --stat --format= HEAD
 tests/test_010_004_t6_red.py | 652 +++++++++++++++++++++++++++++++++++++++++++
```

Commit **`932e02882354b8a77f4efb2eae1dbd0acd54e443`** — `test(010-004): RED T6 - diagnostico de paquete v1 activo (B2) y localizador del sucesor (B4)`. Árbol limpio salvo el untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md`, intacto.

## 5. Declaraciones

- No leí código de implementación: nunca abrí `skills/`, `scripts/`, `sources/`, `agents/` ni `build/`; el CLI se ejercitó solo como subproceso (`--help`, invocaciones) y su contenido no se inspeccionó.
- Edité únicamente `tests/test_010_004_t6_red.py` (archivo nuevo); no toqué tests existentes ni fixtures compartidas, no escribí en el repo desde las pruebas (todo en temporales) y **no corrí la suite completa**.
- Tokens estables y estrechos (`packet id`, `ERROR:`, `owner`, `terminal`, `complete or fail`/«completar o fallar», y el campo JSON `execution_context`); ninguna aserción congela prosa, orden ni número de ocurrencias.
- El informe RED queda como texto final para que el orquestador lo materialice (`docs/` está fuera de mi write scope).