# T2 — Mapeo y registro de operaciones propuesto

**Borrador para revisión; no aprobado ni materializado.**

## 1. Evidencia y límites

Ruta C validada:

- REQUEST válido y contexto de ejecución **v2**.
- `PACKET.md` coincide byte por byte con el render canónico completo: **8.752 bytes**.
- Contrato: SHA256 `5524dfdde86a5314884690a5d3b13202be5034c0eadad1669d6f92ae2262d9b6`.
- Revisión examinada: `05b58cc413cfd0669ddf9b5c6fd7e558502be672`.
- Cambio preexistente: `docs/.cdad-state.json`; ninguna modificación de producto.

La spec y el plan conservan banners de borrador, pero sus hashes coinciden con los documentos fijados en `progress.md:8-18`. No reinterpreto esos banners como revocación de la aprobación registrada.

**Alcance de esta entrega:** inspección estática y conteo de volumen. Las ocurrencias siguientes son expectativas derivadas del código, **no resultados de calibración**. No ejecuté pytest, generación, instalación ni suite completa.

## 2. Decisiones propuestas

### Observación explícita, no profiler general

Propongo marcas de entrada/salida en las fronteras concretas de los helpers, conservando íntegramente sus cuerpos, subprocesos, argumentos, resultados y excepciones.

**Costura nueva propuesta, no API existente:**

- Un pequeño helper bajo `tests/` emite eventos síncronos de comienzo y fin mediante un canal de logging dedicado.
- El observador bajo `scripts/` recibe esos eventos, toma tiempos monotónicos y agrega contexto de fase, identidad de intervalo y anidamiento.
- Sin observador activo, las marcas no escriben evidencia ni modifican la ejecución contractual.
- Un fallo de captura se diagnostica como medición incompleta; no convierte un fallo contractual en pase ni oculta su excepción.
- La firma concreta del helper y la compatibilidad de los hooks de pytest son **VERIFY anterior al despacho GREEN**, conforme a spec §4.2.

Esta alternativa permite observar preparación dentro de `call` sin importar implementación en los verificadores. No propongo interceptar indiscriminadamente funciones, comandos o procesos.

### Clasificar por propósito y frontera, no por nombre del comando

Un `prepare` ejecutado durante el constructor puede ser preparación del escenario. El mismo CLI ejecutado después para comprobar una transición no lo es.

Igualmente, `_run_make_staging` sirve tanto a preparación inicial como a las dos generaciones contractuales del test de determinismo. **No debe clasificarse el helper completo como preparación.**

### Contabilidad

Cada evento tendrá, como mínimo:

- operación, ocurrencia, proceso e intervalo;
- contexto de test/fase o preparación compartida;
- comienzo, fin, estado de terminación y padre;
- clasificación y atributos de rama —fría, reutilización o checkout existente—;
- referencia al alcance aplicado.

El tiempo inclusivo de un padre no se suma nuevamente con sus hijos. Para clasificarlo se descuentan los hijos: por ejemplo, el contenedor de preparación de una copia puede contener una generación contractual que debe permanecer real.

El aislamiento de sesión se identifica como **compartido**, aunque pytest lo ejecute durante el `setup` del primer nodeid. Se conserva esa relación de contención, sin adjudicar su costo semánticamente al primer consumidor ni agregarlo otra vez al total.

## 3. Mapeo de fronteras

En las referencias siguientes, «cuerpo» significa desde antes de la primera instrucción indicada hasta después de la última; una salida excepcional cierra el intervalo mediante `finally`.

### A. Construcción dentro de `call`

**`_RecoveryProject`**

- Constructor: `tests/test_007_002_dispatch_recovery.py:411-440`.
- Construcción del proyecto: cuerpo de `_build_project`, `:445-502`.
- Preparación inicial: llamada `self.prepare(...)`, `:416`, cuyo subproceso real termina en `:514-518`.
- Clasificación: preparación, con los dos últimos intervalos contenidos en el constructor.
- Calibración: `test_reconcile_abandoned_dispatch_is_disposed`, cuya construcción ocurre en `:839`.
- Esperado: un constructor, una construcción y un `prepare` inicial. El despacho, disposición y reconciliación posteriores (`:840-861`) **no pertenecen** a esa preparación.

**`_Project`**

- Constructor: `tests/test_007_003_continuity_at_edges.py:494-515`.
- Construcción: llamada `build_project(self.root)`, `:501`; cuerpo real en `tests/test_004_002_t2_bootstrap.py:200-207`.
- Preparación inicial: llamada `self.prepare()`, `:502`; recorrido CLI `:533-537` y subproceso `:528-531`.
- Clasificación: preparación, anidada bajo el constructor.
- Calibración: `test_durable_registration_replay_does_not_require_current_continuity`.
- Esperado: dos constructores, dos construcciones y dos preparaciones iniciales, por las ramas `replay` y `different` (`:2854-2855,2880-2881,2896`).
- Los registros y replays comprobados después del constructor permanecen acciones reales.

### B. Copias, staging y reutilización

**`tests/product_staging.py`**

- Consulta/reutilización: cuerpo de `product_root`, `:86-92`.
- Copia fría: llamada `shutil.copytree`, `:61-68`.
- Generación fría: llamada `subprocess.run(["make", "staging"], ...)`, `:69-74`.
- Validación de resultado: `:75-81`, dentro de la preparación fría, pero fuera del intervalo del subproceso.
- El checkout con manifiesto se reutiliza por presencia (`:88-89`), no por frescura.
- La rama fría no ocurre necesariamente en el checkout examinado: **el manifiesto está presente**. Hace falta calibrarla con una fuente descartable real sin manifiesto, sin borrar ni regenerar el checkout.

**Helper U1**

- Consulta/reutilización: `tests/test_006_002_u1_delegation_section.py:182-205`.
- Copia: `:187-193`.
- Generación: `:194-197`.
- Calibración: los dos tests de `TestPd2aExactlyOneDelegationSection`, en el orden declarado más abajo.
- Esperado en proceso nuevo: dos consultas, una fría, una reutilización, una copia y una generación.

**Helper U4**

- Consulta/reutilización: `tests/test_006_005_u4_single_entry.py:859-881`.
- Copia: `:864-871`.
- Generación inicial: llamada `:872`, por el subproceso de `:844-850`.
- Calibración: primero determinismo y después etiqueta generada.
- Esperado: tres consultas —una fría y dos reutilizaciones—, una copia y una generación inicial. Las otras dos generaciones se registran separadamente como contractuales.

**Helper U3**

- Consulta/reutilización: `tests/test_006_004_u3_principle_single_source.py:641-661`.
- Copia: llamada `:646`.
- Generación inicial: subproceso `:652-659`.
- Su filtro excluye `.cdad` (`:607-622`).
- La generación inicial produce el resultado que comprueba `test_pd13_the_generated_agents_carry_the_duty_after_make_agents` (`:1038-1055`): se propone conservarla como **acción contractual**, no ofrecerla como preparación eliminable.
- Calibración: ese test seguido por el de determinismo de staging.
- Esperado: dos consultas, una copia, una generación inicial real y dos generaciones contractuales de staging.

**Instalación documental**

`installed_product()` no tiene una copia de producto independiente: reutiliza `disposable_product` importado desde U3 (`tests/test_010_002_documentary_role_integration.py:129-133,1172`).

- Consulta/reutilización: `:1170-1191`.
- Instalación: subproceso `:1180-1187`.
- La instalación real se conserva como acción contractual del recorrido instalado.
- En la selección documental propuesta se esperan cuatro consultas a `installed_product`: una fría y tres reutilizaciones (`:2369,1231,2474,1231`).
- El producto U3 se consulta dos veces: generación inicial y primera instalación. No se atribuye a esta familia una copia adicional de `.cdad`.

### C. Regeneraciones contractuales

Deben continuar ejecutándose, sin caché sustitutiva:

- U4: dos llamadas en `tests/test_006_005_u4_single_entry.py:893,913`; subproceso `:844-850`. Se comparan los resultados en `:910-934`.
- U3: dos llamadas a `staging_digests` en `tests/test_006_004_u3_principle_single_source.py:1123-1124`; subproceso `:667-674`.
- Documental: dos llamadas en `tests/test_010_002_documentary_role_integration.py:2303,2311`; subproceso de `_run_make_agents`, `:1138-1145`.

Sus intervalos son hermanos consecutivos, no hijos de una preparación inicial que ya terminó. Medirlos no autoriza a eliminarlos.

### D. Volumen de `.cdad`

Las copias de `product_staging`, U1 y U4 excluyen `.git`, cachés y `build`, pero **no `.cdad`**. U3 sí la excluye.

Conteo realizado con Python **3.13.5**, `os.walk(followlinks=False)`, `lstat` y los mismos nombres excluidos recursivamente por las tres primeras copias:

- `.cdad`: **19.141 archivos regulares, 386.679.228 bytes y 49 symlinks**.
- Dentro de ese conjunto, `evidence`: **4.877 archivos, 148.403.929 bytes**.
- `local`: **4.258 archivos regulares, 162.680.025 bytes y 49 symlinks**.

Es volumen de entrada observado, **no tiempo de copia ni ahorro**. Es distinto del conteo histórico del discovery y no lo reemplaza.

Para cada copia medida se propone conservar origen absoluto, raíz relativa, política efectiva de exclusión, manifiesto de rutas/tipos/tamaños y conteo del destino. El escaneo queda fuera del intervalo de copia y se registra su propio sobrecosto.

**Límite:** medir la copia completa no separa causalmente el tiempo gastado en `.cdad`. Ese subcosto permanece desconocido. No se elegirá excluirla por tamaño solamente; si la decisión depende de ese subcosto, se resolverá mediante una focal adicional calibrada sobre revisión base recuperable.

La evidencia nueva debe quedar fuera de los orígenes copiados. Si una ubicación elegida entra recursivamente en las copias, se bloquea la medición hasta corregir la ubicación, no los filtros del producto.

### E. Esperas deliberadas

Se identifican, pero **no se compromete todavía un intervalo de espera pura**:

1. `client-hangs`: `tests/test_007_004_termination_not_success.py:239-246` introduce `sleep(60)` y un límite de cinco segundos.
2. `own-timeout`: `:357-367` introduce `sleep(20)` y configura límites de dos segundos.
3. Sondeos y finalización del adaptador: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:543-551,1016-1029`.
4. Espera del transporte externo: `skills/cdad-cycle/scripts/cdad_delegate.py:288-303`; espera al cliente y terminación: `cdad_delegate_opencode.py:625-639`.

Los números escritos son configuración, no duración observada.

**Por qué queda desconocida:** las marcas propuestas en el proceso pytest pueden medir el comando envolvente, pero no separar dentro de sus hijos espera, arranque, sondeo, recepción y terminación. Convertir esa envolvente en «espera medida» sería atribución ficticia. Sustituir el hijo por un doble más rápido, acortar deadlines o evitar su terminación alteraría justamente la transición comprobada.

Esto no afirma una imposibilidad universal de observarla. Haría falta una propuesta específica de observación multiproceso, con fidelidad y sobrecosto calibrados. Hasta entonces permanece en el resto de `call`, y cualquier decisión dependiente de ese costo queda detenida.

## 4. Borrador de `operation-scope.json`

El formato siguiente es una **propuesta nueva**. Las entradas heredan explícitamente los valores de `defaults`; las referencias de fuente y selección se resuelven dentro del propio registro.

`comprometida` significa «se propone exigir su captura y calibración», no «ya medida».

```json
{
  "schema_version": 1,
  "status": "draft",
  "feature_id": "017-001-suite-performance",
  "source_revision": "05b58cc413cfd0669ddf9b5c6fd7e558502be672",
  "calibrated": false,
  "defaults": {
    "state": "comprometida",
    "classification": "preparacion",
    "mechanism": "explicit-synchronous-markers",
    "producer": {
      "boundaries": "test-writer",
      "clock_context_capture_and_profile": "implementer",
      "materialization": "orchestrator"
    },
    "context": "current-nodeid-and-phase; shared-if-outside-test",
    "boundary_semantics": "before-first-statement through after-last-statement; finally-on-exception",
    "limits": "inclusive-wall-time; children-are-breakdowns-not-additional-cost",
    "missing_expected_interval": "incomplete; block-baseline; do-not-reclassify-as-unknown"
  },
  "mechanisms": {
    "explicit-synchronous-markers": {
      "status": "proposed-new-interface",
      "transport": "dedicated-logging-channel",
      "clock": "monotonic-in-observer",
      "interval_identity": "attempt-process-occurrence",
      "fields": [
        "operation",
        "interval_id",
        "parent_id",
        "process_id",
        "nodeid",
        "phase",
        "owner_scope",
        "branch",
        "started",
        "finished",
        "termination"
      ],
      "verify_before_green": [
        "marker-interface",
        "pytest-context-hooks",
        "capture-error-isolation",
        "shared-context",
        "exceptional-close",
        "nesting"
      ]
    }
  },
  "sources": {
    "I": "tests/conftest.py",
    "R": "tests/test_007_002_dispatch_recovery.py",
    "E": "tests/test_007_003_continuity_at_edges.py",
    "B": "tests/test_004_002_t2_bootstrap.py",
    "P": "tests/product_staging.py",
    "U1": "tests/test_006_002_u1_delegation_section.py",
    "U3": "tests/test_006_004_u3_principle_single_source.py",
    "U4": "tests/test_006_005_u4_single_entry.py",
    "D": "tests/test_010_002_documentary_role_integration.py",
    "W": "tests/test_007_004_termination_not_success.py",
    "DELEGATE": "skills/cdad-cycle/scripts/cdad_delegate.py",
    "OC": "skills/cdad-cycle/scripts/cdad_delegate_opencode.py"
  },
  "selections": {
    "C-R": {
      "existing": true,
      "fresh_process": true,
      "nodeids": [
        "tests/test_007_002_dispatch_recovery.py::test_reconcile_abandoned_dispatch_is_disposed"
      ]
    },
    "C-E": {
      "existing": true,
      "fresh_process": true,
      "nodeids": [
        "tests/test_007_003_continuity_at_edges.py::test_durable_registration_replay_does_not_require_current_continuity"
      ]
    },
    "C-P-cold": {
      "existing": false,
      "proposed_verifier": true,
      "fresh_process": true,
      "conditions": [
        "real-disposable-product-source-without-staging-manifest",
        "empty-product-root-cache",
        "two-calls-to-real-product_root",
        "real-make-staging",
        "no-checkout-mutation"
      ],
      "nodeids": [
        "tests/test_017_001_suite_operations.py::test_product_root_cold_then_reuse"
      ]
    },
    "C-P-present": {
      "existing": false,
      "proposed_verifier": true,
      "fresh_process": true,
      "conditions": [
        "real-disposable-product-source-with-staging-manifest-and-recorded-provenance",
        "empty-product-root-cache",
        "two-calls-to-real-product_root",
        "no-forced-generation"
      ],
      "nodeids": [
        "tests/test_017_001_suite_operations.py::test_product_root_existing_manifest_then_reuse"
      ]
    },
    "C-U1": {
      "existing": true,
      "fresh_process": true,
      "nodeids": [
        "tests/test_006_002_u1_delegation_section.py::TestPd2aExactlyOneDelegationSection::test_pd2a_opencode_adapter_has_exactly_one_delegation_section",
        "tests/test_006_002_u1_delegation_section.py::TestPd2aExactlyOneDelegationSection::test_pd2a_claude_code_adapter_has_exactly_one_delegation_section"
      ]
    },
    "C-U4": {
      "existing": true,
      "fresh_process": true,
      "nodeids": [
        "tests/test_006_005_u4_single_entry.py::TestPd20DeterministicStaging::test_pd20_staging_is_deterministic_and_matches_committed_outputs",
        "tests/test_006_005_u4_single_entry.py::TestPd20GeneratedDelegationLabel::test_pd20_generated_delegation_label_drops_the_adapter_qualifier"
      ]
    },
    "C-U3": {
      "existing": true,
      "fresh_process": true,
      "nodeids": [
        "tests/test_006_004_u3_principle_single_source.py::TestPd13GeneratedAgents::test_pd13_the_generated_agents_carry_the_duty_after_make_agents",
        "tests/test_006_004_u3_principle_single_source.py::TestPd13GeneratedAgents::test_pd13_make_staging_is_deterministic_across_two_runs"
      ]
    },
    "C-D": {
      "existing": true,
      "fresh_process": true,
      "nodeids": [
        "tests/test_010_002_documentary_role_integration.py::TestDistribution::test_generation_is_reproducible_and_promoted_matches_staging",
        "tests/test_010_002_documentary_role_integration.py::TestDistribution::test_isolated_install_distributes_corrected_surfaces_and_the_generic_journey",
        "tests/test_010_002_documentary_role_integration.py::TestDistribution::test_documentary_odoo_journey_keeps_domain_and_write_frontier"
      ]
    },
    "C-W": {
      "existing": true,
      "required_for_current_calibration": false,
      "purpose": "candidate-for-additional-calibration-if-wait-cost-becomes-decision-relevant",
      "nodeids": [
        "tests/test_007_004_termination_not_success.py::test_007_004_opencode_noncompleted_never_claims_delivery[client-hangs-timeout]",
        "tests/test_007_004_termination_not_success.py::test_007_004_transport_failures_have_no_delivery[own-timeout]"
      ],
      "verify": "confirm-parametrized-nodeids-from-collection-before-any-run"
    }
  },
  "families": [
    {
      "family": "isolation",
      "source": "I",
      "selection": "all-required-selections",
      "operations": [
        {
          "id": "isolation.seed",
          "begin": 55,
          "end": 68,
          "contexts": [
            {
              "caller": 98,
              "owner_scope": "session",
              "nodeid": null,
              "expected": "one-per-pytest-process"
            },
            {
              "caller": 122,
              "owner_scope": "test",
              "expected": "one-per-executed-test"
            }
          ],
          "limits": "session-operation-may-be-contained-in-first-setup; report-shared-without-double-counting"
        }
      ]
    },
    {
      "family": "recovery-project-in-call",
      "source": "R",
      "selection": "C-R",
      "context": "test-call",
      "operations": [
        {
          "id": "recovery.construct",
          "begin": 411,
          "end": 440,
          "expected": 1,
          "parent": null
        },
        {
          "id": "recovery.build",
          "begin": 445,
          "end": 502,
          "expected": 1,
          "parent": "recovery.construct"
        },
        {
          "id": "recovery.initial-prepare",
          "begin": 416,
          "end": 416,
          "boundary_kind": "around-call",
          "subprocess_source": "R:514-518",
          "expected": 1,
          "parent": "recovery.construct",
          "limits": "constructor-call-only; excludes-later-prepare-replacement-dispatch-and-reconcile"
        }
      ]
    },
    {
      "family": "continuity-project-in-call",
      "source": "E",
      "selection": "C-E",
      "context": "test-call",
      "operations": [
        {
          "id": "continuity.construct",
          "begin": 494,
          "end": 515,
          "expected": 2,
          "parent": null
        },
        {
          "id": "continuity.build",
          "begin": 501,
          "end": 501,
          "boundary_kind": "around-call",
          "callee_source": "B:200-207",
          "expected": 2,
          "parent": "continuity.construct"
        },
        {
          "id": "continuity.initial-prepare",
          "begin": 502,
          "end": 502,
          "boundary_kind": "around-call",
          "subprocess_source": "E:528-531,533-537",
          "expected": 2,
          "parent": "continuity.construct",
          "limits": "constructor-only; subsequent-continuity-and-registration-actions-stay-real"
        }
      ]
    },
    {
      "family": "portable-product-staging",
      "source": "P",
      "operations": [
        {
          "id": "product.lookup",
          "begin": 86,
          "end": 92,
          "expected": {
            "C-P-cold": {
              "total": 2,
              "cold": 1,
              "cached": 1
            },
            "C-P-present": {
              "total": 2,
              "checkout-manifest": 1,
              "cached": 1
            }
          },
          "limits": "manifest-presence-is-not-freshness"
        },
        {
          "id": "product.copy",
          "begin": 61,
          "end": 68,
          "parent": "product.lookup",
          "volume": "product-copy-volume",
          "expected": {
            "C-P-cold": 1,
            "C-P-present": 0
          }
        },
        {
          "id": "product.generate",
          "begin": 69,
          "end": 74,
          "parent": "product.lookup",
          "expected": {
            "C-P-cold": 1,
            "C-P-present": 0
          },
          "limits": "real-subprocess; excludes-post-run-manifest-validation"
        }
      ]
    },
    {
      "family": "u1-staging-cache",
      "source": "U1",
      "selection": "C-U1",
      "context": "test-call",
      "operations": [
        {
          "id": "u1.lookup",
          "begin": 182,
          "end": 205,
          "expected": {
            "total": 2,
            "cold": 1,
            "cached": 1
          }
        },
        {
          "id": "u1.copy",
          "begin": 187,
          "end": 193,
          "parent": "u1.lookup",
          "volume": "product-copy-volume",
          "expected": 1
        },
        {
          "id": "u1.generate",
          "begin": 194,
          "end": 197,
          "parent": "u1.lookup",
          "expected": 1
        }
      ]
    },
    {
      "family": "u4-recomputed-staging",
      "source": "U4",
      "selection": "C-U4",
      "context": "test-call",
      "operations": [
        {
          "id": "u4.lookup",
          "begin": 859,
          "end": 881,
          "expected": {
            "total": 3,
            "cold": 1,
            "cached": 2
          }
        },
        {
          "id": "u4.copy",
          "begin": 864,
          "end": 871,
          "parent": "u4.lookup",
          "volume": "product-copy-volume",
          "expected": 1
        },
        {
          "id": "u4.initial-generate",
          "begin": 872,
          "end": 872,
          "boundary_kind": "around-call",
          "subprocess_source": "U4:844-850",
          "parent": "u4.lookup",
          "expected": 1,
          "limits": "initial-generation-remains-real; preparatory-does-not-mean-removable"
        },
        {
          "id": "u4.contract-regenerate",
          "classification": "accion-contractual",
          "call_boundaries": [
            {
              "begin": 893,
              "end": 893
            },
            {
              "begin": 913,
              "end": 913
            }
          ],
          "boundary_kind": "around-call",
          "subprocess_source": "U4:844-850",
          "parent": null,
          "expected": 2,
          "relation": "ordered-siblings-after-u4.lookup",
          "limits": "both-real-generations-required; no-cache-substitution"
        }
      ]
    },
    {
      "family": "u3-disposable-product",
      "source": "U3",
      "context": "test-call",
      "operations": [
        {
          "id": "u3.lookup",
          "begin": 641,
          "end": 661,
          "expected": {
            "C-U3": {
              "total": 2,
              "cold": 1,
              "cached": 1
            },
            "C-D": {
              "total": 2,
              "cold": 1,
              "cached": 1
            }
          },
          "limits": "classify-exclusive-parent-time; initial-contract-generation-is-a-child"
        },
        {
          "id": "u3.copy",
          "begin": 646,
          "end": 646,
          "boundary_kind": "around-call",
          "parent": "u3.lookup",
          "expected": {
            "C-U3": 1,
            "C-D": 1
          },
          "volume": "product-copy-volume",
          "limits": "filter-U3:607-622-excludes-source-root-.cdad; do-not-attribute-that-volume"
        },
        {
          "id": "u3.initial-generate",
          "classification": "accion-contractual",
          "begin": 652,
          "end": 659,
          "parent": "u3.lookup",
          "expected": {
            "C-U3": 1,
            "C-D": 1
          },
          "limits": "preserve-real-producer-result-checked-by-consumers"
        },
        {
          "id": "u3.contract-staging",
          "classification": "accion-contractual",
          "begin": 667,
          "end": 674,
          "selection": "C-U3",
          "expected": 2,
          "parent": null,
          "relation": "ordered-siblings-after-u3.lookup",
          "limits": "calls-U3:1123-1124-remain-real"
        }
      ]
    },
    {
      "family": "documentary-generation-and-install-cache",
      "source": "D",
      "selection": "C-D",
      "context": "test-call",
      "operations": [
        {
          "id": "documentary.contract-regenerate",
          "classification": "accion-contractual",
          "begin": 1138,
          "end": 1145,
          "expected": 2,
          "parent": null,
          "relation": "ordered-siblings; callers-D:2303,2311",
          "limits": "do-not-count-u3-initial-generation-again"
        },
        {
          "id": "documentary.install-lookup",
          "begin": 1170,
          "end": 1191,
          "expected": {
            "total": 4,
            "cold": 1,
            "cached": 3
          },
          "limits": "cold-path-contains-u3.lookup-and-real-install; no-additional-product-copy"
        },
        {
          "id": "documentary.install",
          "classification": "accion-contractual",
          "begin": 1180,
          "end": 1187,
          "parent": "documentary.install-lookup",
          "expected": 1,
          "limits": "real-isolated-installer; no-global-installation"
        }
      ]
    },
    {
      "family": "deliberate-waits",
      "source": "W",
      "selection": "C-W",
      "state": "desconocida",
      "classification": "desconocida",
      "candidate_classification": "espera-deliberada",
      "mechanism": "none-for-pure-child-wait-in-current-scope",
      "producer": {
        "mapping": "architect",
        "additional-measurement-proposal": "implementer",
        "independent-oracle": "test-writer",
        "decision": "orchestrator"
      },
      "context": "child-processes-within-test-call",
      "operations": [
        {
          "id": "wait.client-hangs",
          "begin": 246,
          "end": 246,
          "boundary_kind": "candidate-parent-call-not-pure-wait",
          "fixture_source": "W:239-245",
          "child_sources": [
            "OC:625-639",
            "OC:543-551",
            "OC:1016-1029"
          ],
          "expected": "one-scenario; actual-sleep-poll-and-grace-occurrences-unknown"
        },
        {
          "id": "wait.external-own-timeout",
          "begin": 367,
          "end": 367,
          "boundary_kind": "candidate-parent-call-not-pure-wait",
          "fixture_source": "W:357-366",
          "child_sources": [
            "DELEGATE:288-303"
          ],
          "expected": "one-scenario; effective-sleep-time-unknown"
        }
      ],
      "limits": [
        "configured-sleep-and-deadline-are-not-observed-duration",
        "parent-command-duration-is-not-pure-wait",
        "no-shortened-timeouts-or-replaced-child-processes",
        "no-claim-of-universal-observation-impossibility"
      ],
      "decision_rule": "retain-in-call-remainder; if-decision-depends-on-wait-cost-stop-and-propose-calibrated-multiprocess-focal-on-recoverable-base-before-changing-it"
    }
  ],
  "volume_observations": {
    "product-copy-volume": {
      "producer": "implementer",
      "independent_checks": "test-writer",
      "mechanism": "source-and-destination-path-kind-size-manifests",
      "clock_context": "separate-from-copy-interval",
      "source_scope": "exact-source-root-of-each-copy",
      "required_fields": [
        "source_root",
        "destination_root",
        "ignore_policy",
        "regular_files",
        "regular_bytes",
        "symlinks",
        "manifest_sha256",
        "scan_started",
        "scan_finished"
      ],
      "limits": [
        "preserve-symlinks-policy",
        "do-not-follow-symlink-targets-for-regular-byte-count",
        "volume-is-not-time",
        "whole-copy-time-does-not-isolate-.cdad-time",
        "exclude-live-evidence-by-location-not-by-silent-product-filter-change"
      ],
      "calibration": {
        "C-P-cold": "one-including-.cdad-copy",
        "C-U1": "one-including-.cdad-copy",
        "C-U4": "one-including-.cdad-copy",
        "C-U3": "one-copy-excluding-source-root-.cdad",
        "C-D": "one-U3-copy-excluding-source-root-.cdad"
      },
      "unknown_component": {
        "id": "copy.cdad-specific-duration",
        "state": "desconocida",
        "classification": "desconocida",
        "reason": "current-boundaries-observe-the-whole-copy-not-recursive-.cdad-subtree-time",
        "decision_rule": "do-not-infer-from-size; calibrate-additional-focal-on-recoverable-base-if-exclusion-decision-depends-on-this-cost"
      }
    }
  },
  "acceptance": [
    "all-committed-intervals-exercised-and-captured-before-baseline",
    "constructor-preparation-observed-in-real-candidate-call-paths",
    "ordered-selection-and-expected-counts-fixed-before-run",
    "shared-preparation-not-arbitrarily-owned-by-first-test",
    "parent-child-time-not-double-counted",
    "contractual-generations-and-cli-transitions-preserved",
    "missing-capture-is-not-zero-or-retrospective-unknown",
    "unknown-cost-not-used-to-select-optimization"
  ]
}
```

## 5. Archivos por rol

**Test-writer, únicamente bajo `tests/`:**

- Crear `tests/suite_operation_markers.py`: costura neutra propuesta.
- Crear `tests/test_017_001_suite_operations.py`: oráculo de transporte, contexto, anidamiento, ramas reales y captura faltante.
- Adaptar con marcas, sin cambiar aserciones ni transiciones:
  - `tests/conftest.py`.
  - `tests/product_staging.py`.
  - `tests/test_007_002_dispatch_recovery.py`.
  - `tests/test_007_003_continuity_at_edges.py`.
  - `tests/test_006_002_u1_delegation_section.py`.
  - `tests/test_006_004_u3_principle_single_source.py`.
  - `tests/test_006_005_u4_single_entry.py`.
  - `tests/test_010_002_documentary_role_integration.py`.

No hace falta modificar `test_004_002_t2_bootstrap.py`: la llamada desde `_Project` permite observar su construcción. Tampoco se propone modificar los tests de timeout mientras su espera pura permanezca desconocida.

**Implementer, fuera de `tests/`:**

- `scripts/cdad_suite_observer.py`: recepción, relojes, contexto, intervalos y errores.
- `scripts/cdad-suite.py`: conservación y validación del alcance y operaciones en el perfil.

**Orquestador:**

- Materializar el registro y `calibration.md` bajo `docs/specs/017-001-suite-performance/performance/`.
- Declarar antes de ejecutar los workspaces de evidencia, fuera de los orígenes copiados.
- Separar los paquetes: el test-writer recibe contrato y tests autorizados, no la implementación examinada por el arquitecto.

Estas rutas son una propuesta para futuros paquetes, no permisos de escritura de esta sesión.

## 6. Calibración y aceptación propuestas

Cada selección `C-*` requerida se ejecutará en **su propio proceso nuevo**, respetando el orden declarado y mediante el `close` existente:

```sh
python3 scripts/cdad-suite.py close \
  --evidence-root <directorio-existente-fuera-del-origen-copiado> \
  --nodeids <archivo-con-la-seleccion-ordenada>
```

No es un comando ejecutado aquí. `C-W` queda fuera de la calibración comprometida actual; sus nodeids parametrizados deben confirmarse por colección si llega a necesitarse.

La aceptación de T2 requiere:

1. Correspondencia recuperable entre selección, XML, resultados, fases y operaciones.
2. Captura no vacía de los constructores reales de recovery y continuidad dentro de `call`.
3. Conteos y relaciones esperados satisfechos; ramas no ejercitadas distinguidas de captura fallida.
4. Conservación de generaciones, CLI, efectos, excepciones y aislamiento.
5. Volumen de copia vinculado a sus orígenes efectivos, sin presentarlo como costo temporal.
6. Desconocidos visibles y decisiones dependientes detenidas.

La ausencia de un intervalo comprometido bloquea la base. La calibración no exige una duración exacta ni demuestra ahorro.

**deferred-hardening:** profiler universal, atribución interna multiproceso de esperas y aislamiento causal del subcosto `.cdad`; no son necesarios para acreditar los intervalos comprometidos. Sí bloquean cualquier optimización cuya justificación dependa de esos costos desconocidos.

## 7. Evidencia de ejecución

Comandos de validación ejecutados, con `rc=0`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad_packet.py validate-request --request .cdad/packets/017-001-suite-performance-architect-draft-004/REQUEST.json

PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad_packet.py validate-packet --request .cdad/packets/017-001-suite-performance-architect-draft-004/REQUEST.json --packet .cdad/packets/017-001-suite-performance-architect-draft-004/PACKET.md

PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad_packet.py render --request .cdad/packets/017-001-suite-performance-architect-draft-004/REQUEST.json --route C

git rev-parse HEAD
git status --short
git diff --name-only
git diff --name-only -- sources skills tests scripts agents build install.sh
```

La comparación adicional en memoria produjo:

```text
canonical_packet_equal=True bytes=8752
contract_sha256=5524dfdde86a5314884690a5d3b13202be5034c0eadad1669d6f92ae2262d9b6
execution_context_schema_version=2
```

Los comandos Python íntegros de comparación, conteo y hashes están en las llamadas `shell` de esta sesión; no se guardaron archivos auxiliares.

**Archivos modificados por mí: ninguno. Commit creado: ninguno.** El diff final de producto está vacío y persiste únicamente el cambio preexistente de estado.

**Suite completa no realizada:** este encargo entrega mapeo estático y una propuesta de calibración focal, no evidencia de rendimiento ni autorización para iniciar la base.
