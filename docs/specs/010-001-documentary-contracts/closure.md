# Cierre — 010-001-documentary-contracts

**Fecha:** 2026-10-31 (UTC del entorno).
**Autor:** orquestador CDAD bajo el mandato HITL vigente
(`docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md`
§1 y §3). Documento del ámbito documental del orquestador, no trabajo de rol.
**Contrato:** `docs/specs/010-001-documentary-contracts/spec.md`, SHA-256
`9bf17a398b55384e271815c8a6c2910563f75a5d2475ec291c31d4f4d26c94da`.
**Plan:** `docs/specs/010-001-documentary-contracts/plan.md`, SHA-256
`cb3c25a8ba6b420baab8ec495620560c122ca17fbe749c95cb171e5867ab0265` (versión 4).
**Commit medido por el intento de cierre:** ver §7.
**Base:** review de T5 (`review.md`) con dos bloqueantes, corrección
(`71c2a7e2`), re-verificación (`review-002.md`) con B1 y B2 cerrados y sin
bloqueantes nuevos.

## 1. Alcance de la unidad

**Dentro:** una casa normativa documental única
(`skills/cdad-cycle/references/documentary-contracts.md`) con las cuatro
categorías (evidencia, propuesta, contradicción, pendiente) y sus distinciones;
el localizador mínimo por tipo de fuente; la clasificación de pendientes
bloqueantes y no bloqueantes; las cuatro declaraciones de todo encargo
documental; la regla «quien produce no modifica su oráculo»; la separación entre
control estructural y revisión semántica; la autoridad de aceptación del
usuario/dueño; la obligación breve y el puntero en las seis fuentes de rol, en
los cinco bloques estáticos de paquete y en los agentes generados y promovidos
de ambos runtimes, incluidas las variantes Odoo; y la alineación del contrato
del implementer en las superficies instalables.

**Fuera (no se hizo):** selección del perfil documental y su combinación con
Odoo (010-002); piloto funcional (010-003); validador universal de documentos o
motor de verdad semántica; protección mecánica por hash de todos los insumos;
campos nuevos del request o del estado; agentes, skills o etapas nuevas;
permisos por defecto ampliados; publicación, push o actualización de la
instalación global.

Superficies tocadas: `skills/cdad-cycle/references/documentary-contracts.md`
(nueva), `skills/cdad-cycle/SKILL.md`,
`skills/cdad-cycle/references/{handoff-prompts,sub-agent-strategies}.md`,
`skills/cdad-cycle/packets/roles/{architect,implementer,test-writer,reviewer,scribe}.md`,
`sources/roles/{architect,implementer,test-writer,reviewer,scribe,orchestrator}.md`,
`agents/**` (22 derivados), `tests/test_010_001_documentary_contracts.py` y
`docs/specs/010-001-documentary-contracts/**`.

## 2. Las 16 postcondiciones y su evidencia

Clases: **TEST** = verificada por una ejecución real de test; **REVISIÓN** =
verificada por dictamen independiente (stage 4), no por test. La distinción se
mantiene explícita: un verde estructural no acredita fidelidad semántica
(PC-10/INV-06).

| PC | Promesa (resumen) | Evidencia | Clase |
|---|---|---|---|
| **PC-01** | La referencia define las cuatro categorías con las distinciones de D1 | `documentary-contracts.md` §1; `TestPromiseA` (conceptos y distinciones); `review-002.md` B1 | TEST + REVISIÓN |
| **PC-02** | Respaldo localizable, propuestas explícitas, contradicciones conservadas | §1-§2; `TestPromiseA`; `review-002.md` | TEST + REVISIÓN |
| **PC-03** | Localizador mínimo por tipo de fuente y tratamiento de fuentes inaccesibles/mutables | §2 (cinco tipos); `TestPromiseA`; `review-002.md` | TEST + REVISIÓN |
| **PC-04** | Clasificación de pendientes, datos mínimos y prohibición de rebaja unilateral | §3; `TestPromiseA`; B1 cerrado con impacto desconocido y contradicción | TEST + REVISIÓN |
| **PC-05** | Las cuatro declaraciones del encargo | §4; `TestPromiseB` | TEST |
| **PC-06** | Fuentes, verificadores e insumos protegidos fuera del alcance editable de GREEN; ambigüedad detiene | §4 (O3 incorporada); `TestPromiseB` | TEST + REVISIÓN |
| **PC-07** | «Quien produce no modifica su oráculo» | §4; `TestPromiseB` | TEST |
| **PC-08** | Fronteras de los seis roles y contrato del implementer alineado | §5; seis fuentes; `SKILL.md:72`; `handoff-prompts.md:372`; `sub-agent-strategies.md:35,137`; `TestPromiseB`; B2 cerrado | TEST + REVISIÓN |
| **PC-09** | Dos registros separados: control estructural y revisión semántica | §6; `TestPromiseC` | TEST |
| **PC-10** | Estructura ≠ fidelidad; obligación o paquete ≠ sandbox | §6; `TestPromiseC`; informes de T3/T4 y `red-t2.md` declaran el límite | TEST + REVISIÓN |
| **PC-11** | Contraste con fuentes y alcance real declarado | §7; `TestPromiseC` | TEST + REVISIÓN |
| **PC-12** | Aceptación funcional del usuario/dueño; pendientes admisibles visibles | §7; `TestPromiseC`; INV-07 como ausencia medida | TEST + REVISIÓN |
| **PC-13** | Casa única, fila en la tabla de referencias y consumidores por puntero | `TestPromiseD` (unicidad por frases, espacios normalizados, `skills|sources|agents`) | TEST |
| **PC-14** | Seis fuentes, cinco bloques y agentes de ambos runtimes con obligación y puntero | `TestPromiseD` (11 tests, 22 agentes por árbol) | TEST |
| **PC-15** | Instalación aislada con bytes esperados, generación reproducible, techo vigente | `TestPromiseD`; `make staging` ×2 idéntico; instalación aislada con `cmp`; techo 3709/12000 | TEST |
| **PC-16** | Sin agentes, skills, etapas, campos ni selector nuevos; sin ampliar permisos | Regresiones verdes; diff sin `scripts/`, `install.sh`, `Makefile` ni esquema | TEST + REVISIÓN |

**Lo que esta tabla no declara:** que la referencia sea semánticamente perfecta
para todo caso real. Eso lo juzgó el reviewer sobre D1–D4 y lo volverá a juzgar
el piloto (010-003). PC-04 y PC-08 quedaron acreditadas **después** de cerrar
B1 y B2; el dictamen que las acreditó es `review-002.md`.

## 3. Trazabilidad de gates

| Gate | Registro | Evidencia |
|---|---|---|
| Spec y plan | `gate`/`specification` `5b488a5e…` | `owner-approval-2026-10-31.md`; tres pasadas de `plan-review` |
| AUDIT | `gate`/`audit` `593f34ea…` | `test-audit.md`; `audit-approval-2026-10-31.md` (A1–A10) |
| RED | delivery `tdd-red-t2` | `red-t2.md`; 11 tests, 64 fallos por aserción, 0 errores |
| GREEN T3 | delivery `tdd-green-t3` | `tdd-t3-green.md`; `3344526e`; A–C verdes, D rojo por diseño |
| GREEN T4 | delivery `tdd-green-t4` | `tdd-t4-green.md`; `2a918b72`; módulo completo verde |
| Review | `gate`/`review` `bb7d63bb…` | `review.md`, `review-002.md`; `71c2a7e2` |

**Auditoría de digests (ejecutada al cerrar):** `stage_history` registra 39
artefactos de esta unidad sobre 33 rutas. Ocho registros corresponden a versiones
sucesivas de borrador legítimamente superadas (`spec.md` y `plan.md` en sus
iteraciones, `SKILL.md` y la referencia antes del review-fix). El estado vigente
coincide byte a byte con su registro aplicable en **las 33 rutas**: `spec.md`
`9bf17a39…` y `plan.md` `cb3c25a8…` con lo aprobado en el gate de
especificación, y las superficies del review-fix (`SKILL.md` `2465acee…`,
`documentary-contracts.md` `a1e0aeaf…`, `handoff-prompts.md` `02146ba2…`,
`sub-agent-strategies.md` `e83b183b…`) con su entrega de T5. Ningún artefacto
quedó con digest obsoleto.

## 4. Desviaciones de proceso declaradas

1. **Paquete de review inválido (attempt 20).** El orquestador compuso el paquete
   `…reviewer-review-001` con el CLI **instalado**, cuya copia de
   `packets/roles/` era anterior a T4, mientras el árbol del proyecto ya tenía el
   bloque vigente. El reviewer lo **rechazó** con `validate-packet` rc=2, sin
   revisar. Se dispuso como `superseded` (`6a883a84…`), se conservó el rechazo en
   `review-refused-packet-001.md` y se republicó con el CLI del proyecto
   (`…reviewer-review-002`), validado antes de despachar. **El fail-closed
   funcionó**: un paquete que no coincide con su render canónico no se ejecuta.
   Efecto colateral declarado: 1 despacho de reviewer consumido sin producto.
2. **Checkpoint entre `begin` y `record` (attempt 10 → 12).** En el tercer
   `plan-review` se ejecutó un checkpoint entre el `begin` y el registro del
   transporte; el CLI rechazó el registro porque la cabeza vigente ya no era el
   `begin`. Se re-despachó el mismo paquete (bytes y pins intactos) bajo un
   `begin` nuevo y se registró como attempt 12. El primer transporte quedó como
   intento no registrado, declarado aquí.
3. **Aprobación aplicada antes del último registro de review.** Los marcadores
   `Status: Approved by …` movieron el pin de `spec.md` y `plan.md` y bloquearon
   el `record-dispatch` del `plan-review-003`, que pinneaba los bytes previos.
   Se restituyeron los bytes revisados desde las partes del recibo, se registró
   la entrega y se re-aplicó la aprobación byte a byte; los digests registrados
   en el gate (`9bf17a39…`, `cb3c25a8…`) se recuperaron exactos. Orden correcto:
   **registrar la entrega antes de mutar el contrato**.
4. **`make validate` rc=2 por deriva de la instalación global (F011).** Ver §5.
   No es una regresión del producto: `install.sh --check` compara contra el HOME
   real, que este ciclo no publica.
5. **Scope mecánico más ancho que el diff (T3).** La política de rutas solo
   admite rutas exactas declaradas en `implementation_files` (hoy `install.sh`),
   así que el `write_scope` de T3 se declaró como `skills/cdad-cycle` y
   `sources/roles` en lugar de los ocho archivos. El diff se auditó contra las
   rutas del plan y coincidió; la limitación del mecanismo queda declarada.
6. **Lectura denegada de la doctrina de subfase (I-8).** El test-writer tiene
   denegada la lectura de `skills/**`, que incluye
   `packets/substages/test-writer-*.md`, la doctrina que su paquete declara como
   fuente de instrucción. El AUDIT y el RED la leyeron con `cat` y lo declararon.
   No hubo fuga de implementación: el contenido es doctrina de la propia subfase.
   Se registra como evidencia de I-8; corregir permisos de agentes es un cambio
   de producto con su propio contrato.
7. **Volcado de fuentes en mensajes de fallo (RED).** El primer borrador del
   oráculo usó `assertIn` con el archivo completo como contenedor y los mensajes
   de fallo volcaron texto de `sources/roles/` y de agentes generados. El oráculo
   no cambió de concepto (`assertIn` → `assertTrue`, solo mensajes) y el rol lo
   declaró. Se acepta con la desviación registrada.
8. **H-0 descartada con evidencia.** El AUDIT reportó una deriva de
   `instruction_sources` comparando dos archivos distintos: la fuente declarada
   es `skills/cdad-cycle/packets/roles/test-writer.md` (`5f52650e…`) y el archivo
   comparado fue `sources/roles/test-writer.md` (`81d0bf01…`). No hubo deriva.
9. **Estado heredado limpiado al abrir la unidad.** `postconditions_status`,
   `audit_status` y `review_status` provenían de `010-004` y `009-002`; el
   orquestador los limpió al abrir `010-001` para que el gate de AUDIT no
   heredara un estado ajeno.
10. **Diversidad de modelos.** Architect y reviewer usaron modelos distintos
    (`openai/gpt-6.1-sol#high` y `claude-code/claude-opus-5-5#low`). Test-writer
    e implementer compartieron el modelo configurado por el runtime
    (`opencode-go/deepseek-v4.1-flash#max`), en sesiones distintas. El invariante
    exigido —reviewer distinto del implementer— se cumplió; la coincidencia
    test-writer/implementer no está prohibida por el contrato y se declara.

## 5. Deriva de la instalación global (O1)

`bash install.sh --check` devuelve rc=1 con **52 archivos** en deriva y tres
entradas de árbol:

| Árbol | Archivos | Detalle |
|---|---|---|
| `.config/opencode/skills/cdad-cycle` | 10 | `SKILL.md`; cinco `packets/roles/*.md`; `references/{handoff-prompts,sub-agent-strategies}.md`; `references/documentary-contracts.md` (falta); `scripts/__pycache__/cdad_packet.cpython-313.pyc` |
| `.agents/skills/cdad-cycle` | 10 | idéntico al anterior |
| `.claude/skills/cdad-cycle` | 10 | idéntico al anterior |
| `.config/opencode/agents` | 11 | los 11 agentes CDAD |
| `.claude/agents` | 11 | los 11 agentes CDAD |

**Lectura honesta:** es deriva de **publicación**, no una regresión del
producto. La instalación aislada de T4 verificó que el instalador distribuye la
referencia y los agentes con los bytes correctos cuando se le da un destino
propio. Mientras no se publique, los roles reciben la obligación documental
**por el paquete** (que sí la transporta) y no por el agente instalado; y el
`cdad_packet.py` instalado compone los bloques desde su propia copia antigua,
motivo del rechazo descrito en §4.1. **Este cierre no publica.**

## 6. Diferido con motivo

| Elemento | Estado | Motivo |
|---|---|---|
| **N1** «only» en la regla de contradicción (`documentary-contracts.md:81`) | diferido al piloto | Es más estricto que D3, nunca habilita una rebaja; precisarlo toca la referencia por una lectura literal. |
| **N2** «Expected output: implementation code» (`handoff-prompts.md:377`) | diferido | Es una descripción de salida, no un permiso; la línea de permiso (L372) es la que gobierno. |
| **O4** solapamiento de 6-gramas entre fuente de rol y referencia | diferido | La medida contractual de PC-13 pasa; el origen es la tabla de PC-08. |
| **F011 / deriva de instalación** | declarada en §5 | Depende de una publicación que este ciclo no autoriza. |
| **I-8** (lectura de doctrina de subfase denegada) | backlog del epic | Cambiar permisos de agentes generados exige su propio contrato. |
| **Protección mecánica por hash de cada insumo** | `deferred-hardening` de la spec | Requiere diseño de esquema no autorizado. |
| **Parser o linter universal de documentos** | `deferred-hardening` de la spec | No hay promesa de interpretación automática. |
| **Detección automática de contradicciones semánticas** | `deferred-hardening` de la spec | No es acreditable por presencia estructural. |
| **Formatos binarios y captura genérica de fuentes externas** | `deferred-hardening` de la spec | Fuera del alcance inicial. |
| **Cobertura exhaustiva y rendimiento** | `deferred-hardening` de la spec | No protegen una promesa adicional. |

## 7. Evidencia del cierre

**Intento de cierre (suite completa, un solo intento completado):** medición
producida por `scripts/cdad-suite.py close --all`, no transcrita a mano.

| Campo | Valor |
|---|---|
| Directorio de evidencia | `.cdad/evidence/010-001-closure/attempt-20261031T085400631361Z-689502-aceee480/` |
| Selección | `--all` (1887 nodeids) |
| `commit` medido | `6c5b5a8c1e33611f5b9212afe3c25db93b05317d` |
| `dirty` al iniciar | 1 |
| `rc` | 0 |
| `pytest_summary` | `1882 passed, 5 skipped in 4527.94s (1:15:27)`; `verified: true`, `failed: 0`, `errors: 0`, `unparsed_lines: []` |
| `canary.delta_lines` | 0 |
| Artefactos | `stdout.log`, `stderr.log` (0 bytes), `canary-before.txt`, `canary-after.txt` (14350 líneas cada uno), `attempt.json` |

Lectura: `rc=0` con la selección completa, sin `failed`, `errors` ni diagnóstico;
`canary_delta_lines=0` significa que el intento no alteró el HOME real
(`~/.config/cdad`, `~/.config/opencode`, `~/.local/state/cdad` ni las entradas
de primer nivel de `~`). La suite corrió en **un solo intento**: no hubo corte,
reintento ni segunda medición.

**Los 5 skips son preexistentes y ajenos a esta unidad**: dos en
`tests/test_005_002_t4_acceptance.py`, uno en
`tests/test_005_009_t4_acceptance.py`, uno en
`tests/test_005_010_t4_integration.py` y uno en
`tests/test_006_001_t3_integration.py`. Todos son integraciones reales
condicionadas por variables de entorno que el ciclo no expone; ninguno cubre una
postcondición de 010-001 y **ninguno es un pase**: el motivo de cada omisión queda
registrado literal en `attempt.json`.

**`dirty: 1`** es `docs/specs/010-000-continuity-relative-root/discovery.md`,
archivo sin seguimiento y previo a esta unidad: este cierre no lo toca ni lo
commitea.

**Vigencia de la medición.** El `commit` medido es `6c5b5a8c`. Después de él,
`HEAD` es `a3d11cf5`, cuyo único cambio es
`docs/epics/epic-010-documentary-specialization/backlog.md` (+3 líneas,
`git diff --stat 6c5b5a8c..HEAD`): superficie documental, sin archivo de producto,
test ni instalador. Ningún archivo que la suite ejercite cambió después de la
medición. El tiempo de pared medido (75m27s) se declara tal cual: es mayor que el
de la medición de 010-004 (61m08s) en la misma máquina y no se normaliza.


## 8. Lo que este cierre NO declara

- **No publica ni actualiza la instalación global** (§5): la vigencia en los
  agentes instalados es una decisión pendiente del dueño.
- **No declara que la norma acredite fidelidad semántica** de un documento real:
  eso corresponde al piloto (010-003).
- **No declara F011 en PASS**: se declara medido y no oculto.
- **No convierte ningún recibo en aprobación**: todos quedaron
  `semantic_status: pending`.
- **No cierra el epic**: `010-002` y `010-003` siguen pendientes.
