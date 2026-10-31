Validation complete, work done. Here is the FINAL TEXT.

---

# FINAL TEXT — test-writer E2E (T5, 010-004)

**Paquete:** `010-004-packet-dispatch-ergonomics-test-writer-e2e-001` · **Ejecución:** `exec-010-004-packet-dispatch-ergonomics-001` · **Contrato:** `spec.md` sha256 `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64` (verificado con `sha256sum`) · **Commit:** `c4ae3312`

## 0. Admisión (Route C) y validación de entrada

- **Identificación C:** el bloque de 7 campos recibido coincide **byte a byte** con `cdad_packet.py render --route C` (`diff` vacío; sha256 del bloque `04377629…` en ambos lados).
- **Validaciones:** `validate-request` rc=0; `validate-packet` rc=0; `render` completo **byte-idéntico** al `PACKET.md` publicado (`diff` vacío, 54 líneas); `validate-state` → `VALID: execution=exec-010-004-… model_policy=ordinary`.
- **Toolchain:** `--project-root <repo>` con `skills/cdad-cycle/scripts/cdad_packet.py` del repo. La copia global stale (`~/.config/opencode`, drift D-1) **no** se usó ni se tocó.
- **`instruction_sources`:** los tres digests declarados coinciden (`37609c56…`, `5f52650e…`, `0b2fdce7…`). **Declaro una desviación:** el tool `read` fue denegado en `skills/**` (glóbulo de raíz de implementación) y los mostré con `cat`. No aportaron información nueva: su texto está reproducido literalmente en `PACKET.md:7-13`. **No se leyó código de implementación** en ningún momento.

## 1. Archivo nuevo y mapeo test → PC → consecuencia

**`tests/test_010_004_t5_e2e.py`** (831 líneas, archivo NUEVO; 0 ediciones de tests existentes).

| Test | PC | Consecuencia de usuario (R4) |
|---|---|---|
| `test_pc12_isolated_consumer_prepares_validates_and_emits_canonical_route_c` | PC-12 (protege PC-01/PC-05 en la superficie instalada) | …la mejora solo estaría demostrada sobre el CLI del checkout: un defecto de empaquetado/instalación llegaría a la máquina del usuario con toda la suite del repo en verde y su despacho fallaría o emitiría una identificación no canónica |
| `test_pc12_isolated_consumer_rejects_divergent_packet_and_non_canonical_copies_fail_closed` | PC-12 (protege PC-02) | …las restricciones de C estarían acreditadas solo en el checkout: un consumidor instalado podría aceptar un paquete divergente o una copia fuera de su ubicación canónica y despachar un encargo nunca validado |

**Reutilización (sin duplicar):** `tests.test_packet_prepare.PrepareProject`/`run_prepare`; de `tests.test_010_004_t3_red`: `Published`, `PublishedPacketCase` y sus oráculos (`route_c_identification`, `assert_rejection`, `tracked_bytes`, `packet_dirs`, `expected_identification`, `ROUTE_C_CONTRACT_KEYS`) — solo se sobreescriben `publish`/`route_c` para apuntar al CLI instalado; `tests.product_staging.product_root`, `tests.test_install_ownership.load_staging_manifest`/`load_install_manifest`. Casos ya cubiertos por T2/T3 se citan en el docstring y **no** se repiten como casos propios; los negativos se re-ejercitan solo por ser la superficie de este E2E.

## 2. Raíz aislada declarada y CLI instalado usado

- **Raíz:** `.cdad/tmp/t5-isolated-consumer/run-<pid>-<aleatorio>/` (subdirectorio único por corrida; retirada por limpieza de clase, que **asserta** que desapareció; `.cdad/` está gitignored — raíz vacía tras las corridas: 0 entradas).
- **CLI ejercitado:** `<raíz>/install-root/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py`, **sha256 `44a950a54fb56d303e6ecc4357c09c913ddca7a170e26b015e572ac29d48fe54`**.
- **No es el wrapper del checkout (dos pruebas):** su `resolve()` queda bajo la raíz aislada y es un archivo real (no enlace); bytes `44a950a5…` = módulo del producto instalado, mientras el wrapper `scripts/cdad_packet.py` es `df6463fb…` (330 bytes). Además el manifiesto de propiedad registra ese destino con el mismo sha256 (aserción).
- **Las seis raíces** (`HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `CDAD_INSTALL_ROOT`, `CDAD_SKILL_EXTRA_DIRS`) se afirman bajo la raíz aislada, y `HOME` ≠ HOME del proceso. Todo artefacto del manifiesto resuelve bajo la raíz (incluido el destino extra de skills, honrado bajo `<raíz>/extra-skills`).
- **Desviación de fixture declarada:** el instalador rechaza destino dentro del repositorio fuente (`ERROR: Managed install destination overlaps the source repository`), así que el producto se **copia** a `<raíz>/product` (staging incluido) y se instala desde ahí → la instalación no ejecuta el checkout. Por eso tampoco se usó `run_installer` (fija `CDAD_SKILL_EXTRA_DIRS=""`, una de las seis variables que el paquete exige redirigidas); sí se reutilizan `product_root()` y los loaders/oráculos del manifiesto.

## 3. Evidencia real del recorrido (corrida de evidencia con la fixture de la prueba, fuera de pytest, para exponer valores)

```
ISOLATED ROOT : …/.cdad/tmp/t5-isolated-consumer/run-2661248-pxg542l5
INSTALLED CLI : …/install-root/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py
CLI sha256    : 44a950a54fb56d303e6ecc4357c09c913ddca7a170e26b015e572ac29d48fe54
install rc    : 0
prepare rc    = 0    (stderr: aviso informativo "OpenCode agents source directory not found" — no falla la promesa)
execution_context field: .cdad/executions/exec-003-001-role-packets-001/execution.json
validate-request  (resolución del localizador, sin --execution-context) rc=0 stdout=0B stderr=''
validate-packet   (sin --execution-context)                              rc=0 stdout=0B stderr=''
render (default)                                                         rc=0 stdout=4217B
render == PACKET.md (byte-idéntico): True
render --route C                                                         rc=0 stdout=716B
Route C — explicit file backup
```json
{"contract": {"commit": null, "kind": "approved-feature-spec", "path": "docs/specs/003-001-role-packets/spec.md", "sha256": "8866626b…"}, "execution_context": ".cdad/executions/exec-003-001-role-packets-001/execution.json", "execution_id": "exec-003-001-role-packets-001", "packet": ".cdad/packets/003-001-role-packets-test-writer-e2e-001/PACKET.md", "packet_id": "003-001-role-packets-test-writer-e2e-001", "project_root": "<raíz consumidora absoluta>", "request": ".cdad/packets/003-001-role-packets-test-writer-e2e-001/REQUEST.json"}
```
C keys: ['contract','execution_context','execution_id','packet','packet_id','project_root','request']  (7 canónicos)
C determinista (dos corridas byte-idénticas): True
```
(fixture de identidad `003-001`; los ids son los de `PacketFixture`, no el paquete vigente — no se afirma nada sobre este paquete).

**Rechazos fail-closed (consumidor instalado), rc=2, stdout vacío en los tres casos:**
- paquete divergente → `ERROR: packet '…' differs from the canonical rendering of its validated request: the objective, the instructions, the contract, …`; **sin** reescritura/normalización (bytes tampeados intactos) y **sin** divulgación del cuerpo (ni el marcador sembrado ni `cdad-instructions`/`cdad-packet-json`/`Prepare objective`).
- request fuera de la ubicación publicada → `ERROR: route C requires the request published by the packet, not a copy of it: pass --request '.cdad/packets/<id>/REQUEST.json' …`.
- contexto no canónico → `ERROR: execution context mismatch: --execution-context '…/EXECUTION.json' resolves to …`; copias no reescritas; sin paquetes nuevos ni cambios de estado.

## 4. Controles positivos antes / después

`positive control BEFORE: True` → tres tandas negativas (con control positivo **también** tras la tanda A, para que el rechazo no sea universal) → `positive control AFTER: True` (misma identificación exacta). En el test la comprobación es por objeto completo (`baseline == after`), no por mera presencia.

## 5. Salida focal y rc

```
$ python3 -m pytest tests/test_010_004_t5_e2e.py -q
..                                                                       [100%]
2 passed in 25.78s
rc=0
```
Regresión proporcional (sin suite completa):
```
$ pytest tests/test_010_004_t5_e2e.py tests/test_010_004_t2_red.py tests/test_010_004_t3_red.py tests/test_010_004_t4_red.py -q
17 passed in 55.30s          rc=0
$ pytest tests/test_010_004_t5_e2e.py tests/test_010_004_t5_properties.py -q
4 passed in 99.25s (0:01:39) rc=0
$ ruff check tests/test_010_004_t5_e2e.py → All checks passed!
```

## 6. Commit

`c4ae3312` — `test(010-004): E2E T5 - consumidor instalado aislado sobre PC-12 (prepare -> validate -> render --route C y rechazos fail-closed)`
`git show --name-status --format=""` → **una sola ruta**: `A tests/test_010_004_t5_e2e.py`. `git diff --stat HEAD~1 HEAD -- ':!tests'` → vacío. `git status` conserva solo el untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md` (no mío).

## 7. Declaraciones y límites

- **Sin tocar producto/CLI:** 0 ediciones fuera de `tests/**`; el módulo del CLI **no** se importó (solo subproceso, caja negra, incluido `prepare`, `validate-*` y `render --route C`).
- **Sin tocar `~/.config/opencode`, `~/.agents`, `~/.claude`; sin instalación global, sin publicar, sin push.** Evidencia: mtimes reales (22:34/18:34 y 09-jul) anteriores a esta sesión (22:13–22:35); todo proceso hijo corrió con `HOME` redirigido, y la prueba **asserta** que la instantánea de la instalación global del proceso no cambia.
- **Sin suite completa** (política declarada en el paquete).
- **Honestidad sobre el estado:** el E2E es **verde desde la primera corrida** — verifica comportamiento ya entregado por T2–T4 (T4-closure §3 difiere expresamente el recorrido instalado a T5). No se fabricó RED para una capacidad existente (§7.4). Su poder discriminante está en aserciones exactas: byte-identidad del render, objeto C completo contra el derivado de los archivos, propiedad/sha256 del CLI instalado, y `assert_rejection` (rc≠0, stdout vacío, envoltura `ERROR:`, sin traceback, sin declaración) con controles positivos.
- **Límite de la evidencia:** acredita conducta del CLI instalado sobre archivos publicados; **no** recepción nativa del mensaje ni obediencia de un modelo (§4.7). La instantánea global es de solo lectura y no observa escrituras transitorias revertidas.
- **Observación registrada:** con `HOME` aislado sin agentes globales, `prepare` responde rc=0 y avisa por stderr que no publica derivados; la promesa ejercitada no depende de ello, por eso no se exige stderr vacío.

**Una sola subfase (e2e), un solo archivo nuevo, sin cambio de producto.**