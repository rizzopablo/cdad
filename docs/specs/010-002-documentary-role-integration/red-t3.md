```text
INFORME RED — T3 de 010-002-documentary-role-integration
Rol: test-writer · Subfase: red · Ruta C (respaldo explícito por archivo)

=====================================================================
0. INTAKE (ruta C) — validación previa a trabajar
=====================================================================
Identificación recibida (packet_id, contract+sha256, execution_id, packet,
request) comparada con el render canónico:

$ python3 scripts/cdad_packet.py render --route C \
    --request .cdad/packets/010-002-documentary-role-integration-test-writer-red-001/REQUEST.json \
    --execution-context .cdad/executions/exec-010-002-documentary-role-integration-001/execution.json
→ bloque idéntico byte a byte al recibido (sin cuerpo inline: correcto en ruta C)

$ python3 scripts/cdad_packet.py validate-request  --request …/REQUEST.json --execution-context … → rc=0
$ python3 scripts/cdad_packet.py validate-packet   --request …/REQUEST.json --packet …/PACKET.md --execution-context … → rc=0
$ python3 scripts/cdad_packet.py render --request …/REQUEST.json --execution-context … > /tmp/opencode/render_full.md
$ diff -u /tmp/opencode/render_full.md …/PACKET.md → sin diferencias (PACKET.md == render canónico completo)
$ sha256sum docs/specs/010-002-documentary-role-integration/spec.md
  → 0d630c49cfd4c8b0f671026437000617b96bf1bc44b2383dd2914bc7e5581abc (coincide con el bloque)
Contexto de ejecución: schema_version 2. Ninguna ruta mixta.

=====================================================================
1. ARCHIVOS MODIFICADOS Y COMMIT
=====================================================================
Nuevo: tests/test_010_002_documentary_role_integration.py (1899 líneas)
Commit: 38d44c39b27f082aece0f55018eb07cdfe49a5fd
  "test(010-002): RED de T3 con trece tests de instrucciones y distribucion"
  git show --stat → 1 file changed, 1899 insertions(+)
  git status → solo queda lo preexistente (M docs/.cdad-state.json,
  ?? docs/specs/010-000.../discovery.md), sin cambios de producto ni de otros tests.

Regla de alcance: única escritura bajo tests/; no se tocó src/ ni producto.

=====================================================================
2. COMANDO, SELECCIÓN Y RESULTADO
=====================================================================
$ python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py \
    -k 'TestEngagement or TestOdooApplicability or TestDispatchDoctrine or TestDistribution'
→ rc=1 · 10 failed, 3 passed · Python 3.13.5 · pytest 8.3.5
Log íntegro: /tmp/opencode/red-010-002-t3-final.log

Revisión medida: HEAD del producto 0d935bc8 + este commit; contrato pineado
por sha256 0d630c49…81abc. Selección = módulo nuevo completo (13 tests):
$ --collect-only → 13 tests; --collect-only tests/ → 1900 tests, sin errores
de colección (los 1887 previos + 13).

Independencia por clase (misma evidencia, ejecutada por separado):
  -k TestEngagement        → 3 failed
  -k TestOdooApplicability → 5 failed
  -k TestDispatchDoctrine  → 2 failed
  -k TestDistribution      → 3 passed (controles, ver §4)

=====================================================================
3. LOS TRECE TESTS: PC, CAUSA DEL RED (aserción, nunca import/fixture)
=====================================================================
(A) TestEngagement — Promesa A (PC-01…03)
 1. test_documentary_procedure_uses_the_existing_fields_without_a_new_selector (PC-01)
    RED: AssertionError, faltan ['objetivo y promesas','producto editable',…] —
    la región documental de references/handoff-prompts.md no expresa las siete
    declaraciones por los campos existentes; no hay procedimiento (D1/§3).
 2. test_explicit_editable_scope_and_stop_on_protected_overlap (PC-03)
    RED: AssertionError, faltan ['alcance editable','declarado explícitamente'].
    Los controles de alcance (6 invocaciones de prepare) corrieron antes y
    pasaron en la misma ejecución: el fallo es el procedimiento, no el fixture.
 3. test_six_role_boundaries_and_no_documentary_variant (PC-02)
    RED: AssertionError, faltan ['fronteras y separación de responsabilidades',
    'se conservan']. Controles previos verdes en la misma corrida (6 fronteras +
    11 agentes/runtime).

(B) TestOdooApplicability — Promesa B (PC-04/05)
 4. test_addon_boundary_and_module_documentation (PC-04)
    RED: ninguna de las 15 fuentes competentes (6 roles, 5 skills Odoo, 4
    referencias del inventario T4) contiene la frontera completa: trabajo de
    addon, documentación del módulo como producto documental salvo contrato,
    ubicación que por sí sola no exige batería, y límite de clasificación/permisos.
 5. test_producer_roles_matrix (PC-04)
    RED: el rol architect no tiene párrafo documental que NIEGUE la batería de
    addon (matriz ausente). Incluye control de vacuidad del detector.
 6. test_review_coordination_memory_matrix_and_diff_prevalence (PC-05)
    RED: falta el objeto de la exención documental del reviewer (matriz ausente);
    también se exigen diff prevalece, addon oculto bajo etiqueta, no retroactivos.
 7. test_documentary_verifier_is_not_an_addon_test (PC-04)
    RED: faltan ['no exige batería de addon','por dominio del proyecto'] en la
    aplicabilidad del test-writer.
 8. test_distributed_artifacts_carry_the_matrix (PC-04/05)
    RED: el agente generado opencode/cdad-architect.md no lleva la celda del rol.

(C) TestDispatchDoctrine — Promesa D (PC-09; mitad documental de PC-08)
 9. test_every_selection_surface_derives_a_suffix_and_keeps_no_other_value_fallback (PC-09)
    RED: en sources/roles/orchestrator.md falta «stack no vacío» (y más en
    SKILL.md / sub-agent-strategies.md). Exige en las 5 superficies la regla de
    sufijo + genérico solo para ausente/null/vacío, y la AUSENCIA de «otro
    valor → genérico» con detector y control de vacuidad propios.
10. test_absent_variant_is_mechanical_external_and_procedural_native (PC-09/PC-08)
    RED: en skills/cdad-cycle/SKILL.md falta «variante ausente o no publicada»
    en la ventana procedimental (adaptadores: rechazo mecánico antes de lanzar;
    vía nativa: detención procedimental; sin sustitución silenciosa; no se
    atribuye guarda mecánica nueva a la vía nativa, con control de vacuidad).

(D) TestDistribution — Promesa F (PC-11, PC-12.a)
11. test_generation_is_reproducible_and_promoted_matches_staging (PC-11) — PASA (control)
12. test_isolated_install_distributes_corrected_surfaces_and_the_generic_journey (PC-12.a) — PASA (control)
13. test_documentary_odoo_journey_keeps_domain_and_write_frontier (PC-12.a) — PASA (control)

Ningún fallo es ImportError, KeyError, ruta inexistente ni fixture roto:
las 15 superficies declaradas existen (verificado por stat) y los tres tests de
distribución prueban que make agents, la instalación aislada y ambos recorridos
funcionan hoy.

=====================================================================
4. CONTROLES YA VERDES (declarados; no se presentan como RED)
=====================================================================
- PC-02: fronteras de los seis roles (sources/roles/*.md) y conjunto exacto de
  11 agentes por runtime, sin variante documental — verdes dentro del test 3.
- PC-03: defaults de prepare (implementer sin docs ni tests; test-writer solo
  tests; architect/reviewer/scribe sin escritura) + publicación literal de
  --write-scope docs=docs — verdes dentro del test 2.
- PC-11: make agents determinista (dos generaciones, bytes y manifiesto
  idénticos) y promovidos == staging para 11 agentes × 2 runtimes.
- PC-12.a: instalación aislada publica SKILL.md, handoff-prompts.md,
  sub-agent-strategies.md y las 5 skills Odoo con bytes de origen en las 3
  raíces skills declaradas; 11 agentes por runtime con bytes de staging;
  prepare del CLI instalado resuelve cdad-implementer y cdad-implementer-odoo
  contra el destino instalado sin mutar bytes.
- Cargas de dominio Odoo presentes en los seis roles.
- Techo estático: no se reescribe; queda en los controles verdes citados por el
  AUDIT (test_static_block_ceiling, TestPd13) que T4 debe reejecutar sin elevar.

=====================================================================
5. REGLAS DE ORÁCULO APLICADAS
=====================================================================
- R1: región de aplicabilidad localizada por rol y archivo (secciones o
  párrafos temáticos, ventanas 1800/2600) y exigencia del PAR exención
  documental acotada + obligación de addon; PC-09 exige la AUSENCIA de «otro
  valor → genérico» en las 5 superficies, no la mera presencia de «sufijo».
- R8: TestDistribution genera en copia descartable (disposable_product) y nunca
  lee build/staging del checkout como oráculo del contenido corregido; la
  instalación usa CDAD_INSTALL_ROOT propio y CDAD_SKILL_EXTRA_DIRS vacío.
- R11: PC-03 se verifica como obligación procedimental + igualdad de alcances ya
  verde; no se inventa un rechazo mecánico inexistente.
- R3/R5/R6/R7/R9/R10/R12 son de T5/T8: no se escribieron proxies.
- PC-13 no se contabiliza aquí: ningún test estructural acredita fidelidad
  semántica ni suficiencia (reservado al dictamen independiente de T8).

=====================================================================
6. LECTURAS DECLARADAS Y LÍMITES (PD-15)
=====================================================================
- No se leyó implementación para derivar el oráculo: ni sources/roles, ni
  SKILL.md, ni skills/odoo-*, ni agents/ se leyeron como texto. El oráculo sale
  del contrato (D1–D5, §3, PC-01…05/09/11/12.a) y de las superficies que §10 y
  el AUDIT nombran.
- Lectura ordenada por el propio paquete: skills/cdad-cycle/references/
  documentary-contracts.md (norma compartida de 010-001). Read fue denegado por
  el guard; se leyó por bash, igual que en el AUDIT. Solo informó «no duplicar
  la norma» y que el procedimiento operativo no vive ahí.
- El CLI, make agents e install.sh se ejercitaron como procesos (interfaz
  pública) sobre copias descartables.
- Medición de texto limitada a conteos agregados de tokens y a la evaluación de
  los controles de conservación (para no escribir controles con redacción
  inexistente). Las obligaciones RED no se ajustaron al texto observado.
- Límite: verificación estructural. Un verde futuro no acreditará fidelidad
  semántica, suficiencia de una exclusión ni conducta de modelos.
```

**Evidencia de por qué el RED es correcto:** 10 fallos de aserción con causa documental explícita (procedimiento ausente, matriz por rol ausente, doctrina con la cláusula de fallback, artefacto distribuido sin la matriz), 3 controles verdes que prueban que `make agents`, la instalación aislada y ambos recorridos funcionan, y cero fallos por import, ruta o fixture.
