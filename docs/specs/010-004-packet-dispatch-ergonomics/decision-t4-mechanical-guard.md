# Decisión T4 — guarda mecánica mínima del camino de despacho (ruta C)

**Fecha:** 2026-10-30
**Autor:** orquestador CDAD (mandato HITL vigente: `docs/epics/epic-010-documentary-specialization/execution.md`)
**Contrato:** `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`, SHA-256 `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`
**Plan:** `plan.md` v2, fila **T4** («Checks mecánicos pertinentes antes de GREEN; revisión semántica independiente posterior»)

## 1. Pregunta decidida

Las promesas de T4 (PC-08b instrucción revisable, PC-12 coherencia fuentes/derivados/adaptadores/handoff): ¿requieren una guarda mecánica propia antes del GREEN, o basta la cobertura existente?

## 2. Medición (ejecutada en este árbol, sin despacho)

| # | Comando | Resultado |
|---|---|---|
| M1 | `rg -l "route C\|--route" tests/` | `tests/test_010_004_t3_red.py` — **único** archivo |
| M2 | `rg -l -- "--route C" sources/ skills/cdad-cycle/references/` | **0 archivos**: ninguna superficie de instrucción nombra hoy el camino de despacho |
| M3 | `rg -l "Route C — explicit file backup"` en agentes derivados de rol | **20/20** en `agents/` + `agents/claude-code/`, **20/20** en `build/staging/agents/{opencode,claude-code}` (declaración de intake presente hoy) |
| M4 | `rg -c -- "route C\|--route"` en los 4 `cdad-orchestrator.md` derivados | **0** en cada uno: el agente que despacha no nombra el camino |
| M5 | `rg -c -- "route C\|--route" tests/validate-consistency.sh` | **0** |

M1 confirma la medición recibida: la cobertura de `test_010_004_t3_red.py` verifica la **emisión** del CLI (`render --route C`), no que las superficies de instrucción ni los derivados nombren el camino. M2/M4 fijan el hueco real: el driver (orquestador) y su handoff no tienen hoy la instrucción del camino de archivo; solo el lado intake (`Route C — explicit file backup`, host `sources/roles/architect.md:35-43`, constante `ROUTE_C_DECLARATION` en `skills/cdad-cycle/scripts/cdad_packet.py:10071`) existe y se replica en los 20 derivados por tree.

## 3. Cobertura existente examinada y por qué no equivale

- **`tests/test_cdad_generate.py`** (PC-2 determinismo byte-idéntico, PC-3 errores de composición, PC-4 manifiesto, PD-1e/PD-7a sin `model:`, PC-15 sin promesas de sandbox, PC-16 legacy-loads/dual path): es **paridad y estructura**, agnóstica al contenido del camino. Una edición de fuentes que borre `--route C` y su regeneración pasan PC-2…PC-16 intactas.
- **`tests/validate-consistency.sh`** (1008 líneas): asserts estructurales sobre derivados, contratos §2, ausencia de `model:` (F008) y deltas de runtime. M5: **cero** referencias al camino.
- **Cobertura de transporte/handoff existente** (`test_role_packet_consumers.py`, `test_006_002_u5_transport_equivalence.py`, `test_006_005_u4_single_entry.py`, `test_packet_prepare.py`, `test_opencode_read_map_and_steps.py`): verifican equivalencia de transporte, single entry, mapas de lectura y prepare; ninguna asserta el token del camino ni su presencia en `agents/`/`build/staging/`.
- **Drift/paridad staging↔agents** (`make agents` copia; `tests/test_install_ownership.py`, `test_009_001_installer_agent_overlay.py`): detectan desincronización entre árboles, no la **pérdida coordinada** del promise (fuente editada + regeneración coherente = paridad verde, camino perdido).

Conclusión del paso 1: **no existe guarda equivalente**; corresponde escribirla.

## 4. Decisión

**Sí corresponde una guarda mecánica mínima antes del GREEN de T4**, como RED del `test-writer` (T4), con alcance estrecho de tokens estables. Fundamento: la pérdida del camino no rompe ningún test actual, y su consecuencia de usuario está **medida en esta misma épica**, no hipotetizada:

- I-5 (`spec.md:44-48`; `observations-packet-dispatch.md:74-90`): un despacho por retranscripción inline perdió backticks aunque los archivos publicados eran íntegros; el rechazo se conservó y exigió un nuevo encargo válido.
- `incident-reviewer-packet-001.md:39`: una copia manual del snapshot base64 de política quedó incompleta y produjo un `cmp` divergente antes de corregirse; el propio revisor declara que el paquete recibido sí contenía el snapshot completo.

Dos corrupciones independientes del mismo vehículo (texto inline) en la misma épica: la guarda protege la existencia del camino que evita ese vehículo.

## 5. R4 — «¿qué se rompe para el usuario sin este test?»

**Respuesta registrada:** sin la guarda, una edición futura de `sources/roles/orchestrator.md`, de los adaptadores o de `handoff-prompts.md` —o una regeneración que no propague el camino— deja el despacho **sin instrucción de ruta C** y todos los gates actuales siguen verdes (determinismo, manifiesto, composición, consistencia estructural, drift entre árboles). El orquestador vuelve entonces al vehículo inline, que en esta épica ya perdió backticks en un despacho y corrompió un snapshot base64 en otro: el usuario recibe payloads corruptos y el paquete ejecutado no es el publicado (INV-05/INV-12), con descubrimiento tardío y coste de rehacer el encargo. Es la clase de promoción admitida por R4: **integridad / pérdida silenciosa de datos y regresión evidente cara de descubrir tarde**, con razón registrada aquí.

Sin esta respuesta la prueba no entraría como requisito ordinario; con ella, entra como guarda de regresión del contrato, no como requisito nuevo.

## 6. Alcance estrecho (no congela prosa) — PC-09

La guarda asserta **solo tokens estables del contrato**, nunca frases, redacción ni orden:

1. **Literal del camino:** el token `--route` seguido de `C` (comparación tolerante a espacios/salto de línea, `--route\s+C`), en las superficies de despacho: `sources/roles/orchestrator.md`, `sources/agents/adapters/opencode.md`, `sources/agents/adapters/claude-code.md`, `skills/cdad-cycle/references/handoff-prompts.md`. El implementer decide **dónde** dentro de cada archivo y con qué redacción.
2. **Declaración de ruta C:** el literal de §4.2 `Route C — explicit file backup` (constante `ROUTE_C_DECLARATION`, `cdad_packet.py:10071`) en su host `sources/roles/architect.md` y en los agentes derivados de rol (hoy 20/20 por tree, M3). Es el token que el intake reconoce; su pérdida por edición o regeneración debe fallar.
3. **Derivados:** el token 1 en los cuatro `cdad-orchestrator.md` (`agents/`, `agents/claude-code/`, `build/staging/agents/opencode/`, `build/staging/agents/claude-code/`), para que una regeneración que lo pierda falle.

**Controles positivos obligatorios:** (a) el flag existe de verdad en el CLI — `render --help` nombra `--route` (verificado: `--route {C}`); (b) la declaración ya está hoy en las superficies correctas (M3, 20/20 por tree), de modo que el RED falla por el comportamiento ausente (`--route C` en superficies y orquestadores), nunca por fixture ausente.

**Prohibido en el RED:** assertar prosa o redacción; congelar frases completas; duplicar el determinismo/manifiesto de `test_cdad_generate.py`; tocar producto, `sources/`, `agents/`, `build/staging/` o el CLI; editar tests existentes.

## 7. Lo que la guarda NO acredita

- No acredita alineación semántica de las instrucciones (PC-03 v2-only, rechazo de mezcla A+C, I-4/I-5): eso lo revisa el reviewer (PC-08b/PC-12, `spec.md:466`), en sesión distinta y por lectura.
- No acredita conducta de un modelo ni exportación independiente del mensaje (`spec.md:390`).
- No acredita que la regeneración sea completa: solo que el token sobrevivió en los derivados declarados; el resto sigue cubierto por `test_cdad_generate.py` y `validate-consistency.sh`.
- No sustituye ni relaja ningún gate de T4/T5/T6.

## 8. Consecuencia operativa

1. Se **retira** el paquete `010-004-packet-dispatch-ergonomics-implementer-green-004` (prepared, nunca despachado; `reconcile` sin cabeza, sin dispatch, sin recibo y sin materialización) mediante `register-transition --transition withdraw`, motivo: requiere RED previo por la guarda de camino de despacho.
2. Se **prepara sin despachar** el paquete `test-writer` / `red` de T4 con los dos tests de §6.
3. Tras el RED y su gate, se prepara el GREEN de T4 (implementer), que alinea fuentes, regenera derivados y satisface la guarda sin reescribir prosa que ya cumple.

## 9. Trazabilidad

- `spec.md`: PC-03 (`:402`), PC-08b (`:420`), PC-09 (`:422`), PC-12 (`:432`), §7.5 (`:466`), §4.7 (`:380-392`).
- `plan.md`: fila T4 (`:32`), superficies previstas (`:63-64`).
- Evidencia de incidente: `spec.md:44-48`; `incident-reviewer-packet-001.md:39`; `observations-packet-dispatch.md:74-90` (citado por la spec).
- Punto abierto que esta decisión resuelve: la nota de la entrada `advance/t4-green-prepared` de `stage_history` al preparar `implementer-green-004` declaró que, si se exigía un check mecánico de las frases contractuales, se abriría una unidad RED separada antes del GREEN.

## 10. Ejecución registrada (misma sesión, sin despacho)

| Acto | Resultado |
|---|---|
| Retiro de `010-004-packet-dispatch-ergonomics-implementer-green-004` (`prepared`, nunca despachado) | `resolution: withdrawn`, `transition_key: ed145913fdff809576725e5e44b4c73e14b5d53f31d10a578a318218515619c7`; `reconcile` previo sin cabeza, sin dispatch, sin recibo y sin materialización; continuidad: nada anexado ni fabricado |
| Publicación del RED de T4 | `010-004-packet-dispatch-ergonomics-test-writer-red-005` (`prepared`, sin despachar) |
| Retiro del `...-test-writer-red-004` recién publicado | `resolution: withdrawn`, `transition_key: 5b0340aeb2baa9770115249d49e4e6ebc232a54d86c19d45a1d7bd3ca542b41a`; motivo: `expected_output` genérico, invariantes del alcance omitidos e input del contrato duplicado; nunca despachado |
| Validación | `validate-state` rc=0; `validate-request` rc=0; `validate-packet` rc=0; `render` por defecto == `PACKET.md` (`sha256 aa4863266deb94a123950eb20a66f75e8ee13b959e9ac5d7b873c6f14d55c90f`) |
| Handoff de ruta C | `render --route C` en `.cdad/010-004-t4-red-005-route-c.txt` (`sha256 79fac7a1134ed07f1e9744f3246f5d13e36f742e941113b0f58e413004651426`) |
| Avance operativo | `advance/t4-red-prepared`, `current_stage: tdd`, `tdd_substage: red` (`transition_key: dcebb663154f80f3310209daf91ae3bd2e3cf1a4d4de8ad60e85d735b5240dfa`) |

Nada fue despachado: no hubo `begin`, ni spawn, ni `record`, ni recibo. El GREEN de T4 queda supeditado al RED y a su gate.

**Corrección 2026-10-30 (I-6) — la fila «Validación» no acreditaba PC-04.** Las
validaciones de esa fila se midieron con `--execution-context` explícito sobre un
request que **no declaraba** el localizador; el gate del orquestador supervisor,
con el CLI del repo y **sin** el flag, rechazó `…-red-005` (rc=2: «the request
declares no request.execution_context (a historical request)»). El paquete quedó
retirado (`resolution: withdrawn`, `transition_key:
bad2e8185e3f89161f3821dec77258c29116a1782b9e82655a88bb48ff8a6016`) por
publicarse sin el locator PC-04, y se sustituyó por
`010-004-packet-dispatch-ergonomics-test-writer-red-007`, preparado con
`scripts/cdad_packet.py` del repo y `--execution-context` explícito: request
`16325428c8cdb6bdc1a674f9bb97043a4caa461074f3892dba98f06819e1ddc8` y cabecera
`fa2c96a89cc335d92c4573e231fcbfd1c4a7d2db09e55cac98c0919255904dc8`, ambos con
el locator canónico; `validate-request`, `validate-packet` rc=0 y `render` ==
`PACKET.md` **sin** flag. Handoff C emitido por el CLI del repo:
`.cdad/010-004-t4-red-007-route-c.txt`
(`7139c6bafcfd5b089ff7699aea1d6a9294d97a7c0ac086ea12ecee45d597ace0`). El primer
sustituto, `…-red-006`, se retiró por un defecto propio de preparación —el
contrato quedó duplicado en `inputs` al re-pasar el principal por `--input`,
misma clase que `-red-004`— (`transition_key:
dbbda8c4bf178e05e70dd3baf09a0867d666df87df32660fa4c37aa43cc7f727`). El
incidente y su lección quedan en `observations-packet-dispatch.md` I-6.
