# Informe test-writer — 010-004 T6, guarda mecánica B1 (red-009)

## 0. Admisión Route C (previa a trabajar)
Con los scripts del repositorio (copia fuente de verdad, sin tocar la copia global):

| Comando | Resultado |
|---|---|
| `validate-request --project-root … --execution-context .cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json --request .cdad/packets/010-004-packet-dispatch-ergonomics-test-writer-red-009/REQUEST.json` | rc=0 |
| `validate-packet … --packet .cdad/packets/…/PACKET.md` | rc=0 |
| `render … --route C` | idéntico al bloque de identificación recibido (packet_id, contract+sha256, execution_id, execution_context, packet, request, project_root) |

Sin cuerpo inline en el dispatch: ruta C válida, un solo bloque de identificación.

## 1. Archivo y test creado
- Archivo NUEVO: `tests/test_010_004_t6_b1_guard.py` (único archivo tocado).
- Test: `TestB1IntakeCoreGuard::test_b1_intake_core_and_derived_role_agents_keep_c_v2_and_a_plus_c_rejection` — un solo test, como exige el encargo.

## 2. Tokens estables y por qué discriminan
Solo `assertIn`/`assertNotIn` sobre palabras, con espacios normalizados únicamente para no depender del corte de línea del markdown. Sin frases completas, sin prosa congelada, sin conteo de ocurrencias.

| Token | Qué discrimina |
|---|---|
| `v2 execution context` | La ruta C exige contexto v2. En el intake previo a B1 no existía "v2" en absoluto: si se pierde, vuelve el intake ambiguo. |
| `v1 context` | El diagnóstico prescrito para C sobre contexto v1; sin él, C/v1 no tiene salida declarada. |
| `Route A and route C are exclusive` | El rechazo de mezcla de rutas A+C, núcleo del hallazgo B1. |
| `even when the inline matches` | La cláusula que impide admitir A+C cuando el inline coincide (el falso positivo exacto que B1 describe). |
| `rejected as an invalid packet` | Refuerzo admitido por el encargo: fija la disposición (paquete inválido, no admisión por A). |

El bloque del dueño se localiza por sus marcadores `<!-- cdad-shared:intake-core -->` / `<!-- /cdad-shared -->`, nunca por número de línea. Los 20 derivados se derivan (2 runtimes × 5 roles × 2 variantes), no se listan a mano; el test afirma las 20 rutas y que cada una contiene los tokens.

## 3. Control negativo (no vacuo)
El test verifica, en `agents/cdad-orchestrator.md` y `agents/claude-code/cdad-orchestrator.md`:
- **No** contienen los tokens del dueño de rol: `v2 execution context`, `Route A and route C are exclusive`.
- **Sí** contienen su regla propia: `A+C is rejected` y `even when the inline coincides`.

Pasó en verde: la ausencia de los tokens del dueño en los orquestadores no es vacua, porque cada orquestador enuncia su propio rechazo A+C con texto distinto.

## 4. Evidencia real de la corrida
```
$ python3 -m pytest tests/test_010_004_t6_b1_guard.py -q
.                                                                        [100%]
1 passed in 0.09s        (pre-commit)
1 passed in 0.06s        (post-commit, misma salida)
```
**`1 passed` al nacer: se declara GUARDA DE REGRESIÓN A1-style, no un RED fabricado.** El fix B1 ya estaba aplicado (4118b794); si esta prueba fallara, el defecto sería del árbol o del test y se reportaría sin tocar producto.

## 5. Alcance (git)
```
$ git show --name-status --format= HEAD
A	tests/test_010_004_t6_b1_guard.py

$ git status --porcelain
?? docs/specs/010-000-continuity-relative-root/discovery.md
```
Commit del artefacto: `4a652890 test(010-004): guarda B1 - intake C/v2 y rechazo A+C en fuente y 20 derivados (regresion)`.

Aclaración honesta: `docs/specs/010-000-continuity-relative-root/discovery.md` ya estaba sin trackear **antes** de empezar (verificado en el primer `git status`), es de otro feature y no lo toqué ni lo stages. Nada bajo `sources/`, `agents/`, `skills/`, `docs/`, `scripts/` ni `build/` fue modificado por este encargo. El HEAD previo (`fc270519`) era el binding del orquestador (modificaba `docs/.cdad-state.json`), no producto mío.

## 6. Oráculo y pins intactos
```
de085989351840361166c33fdcede1f5b41d48301f0ae9014217017c827d1b49  tests/test_010_004_t6_red.py
fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64  docs/specs/010-004-packet-dispatch-ergonomics/spec.md
2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685  docs/specs/010-004-packet-dispatch-ergonomics/plan.md
```

## 7. Declaraciones
- No edité producto ni fuentes: solo `tests/test_010_004_t6_b1_guard.py`.
- No corrí `make staging` ni `make agents`; no corrí la suite completa (solo el test nuevo).
- No leí ni importé `sources/**`, `agents/**` ni `skills/**/scripts/*.py`: el test lee fuente y derivados en tiempo de ejecución, como exige el encargo. Lecturas: contrato (`spec.md`, `plan.md`, `review.md`) y tests (`conftest.py`, oráculo `test_010_004_t6_red.py`), más `tdd_substage` del state por procedimiento de rol.
- Toolchain: únicamente `skills/cdad-cycle/scripts/cdad_packet.py` del repo; no instalé ni modifiqué nada global.

Trazabilidad: PC-03 (spec §4.3 `:296`,`:309-311`) y B1 de `review.md`; R4 declarado en el docstring del test.