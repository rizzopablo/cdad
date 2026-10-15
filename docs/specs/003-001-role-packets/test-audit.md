# Test Audit — 003-001-role-packets

Fecha: 2026-09-17  
Rol: test-writer (AUDIT), sesión aislada de implementación  
Resultado: **AUDIT listo para aprobación; RED de Tarea 1 todavía no debe abrirse**.

## Alcance y evidencia

Se auditó el contrato aprobado P1–P6 sin leer `scripts/**`, `install.sh`,
`agents/**`, `src/**`, `lib/**` ni diffs de implementación. Los runners se
trataron como interfaces black-box cuando se ejecutaron.

Evidencia empírica de baseline:

- `bash tests/validate-consistency.sh`: **123 PASS / 1 FAIL**. El único fallo
  reportado es F011 al ejecutar `scripts/validate-subagents.sh`; coincide con el
  drift de copia instalada ya declarado y no prueba una regresión de 003-001.
- `bash tests/validate-odoo-specialization.sh`: **141 PASS / 0 FAIL**.
- `bash docs/specs/cdad-010-opencode-permissions/run-checks.sh`: termina rojo
  por su sección de regresión A10, consistente con el mismo drift instalado.
  Sus checks estáticos de permisos observados antes del resumen permanecen en
  verde; no se usa este runner como prueba de P1–P6 de la nueva feature.

## Mapeo de cobertura existente

| Superficie existente | Qué protege hoy | Relación con 003-001 | Decisión |
|---|---|---|---|
| `tests/validate-consistency.sh`, F001/F004/F006 | Duplicados textuales del contrato de roles, formato de reviewer y disciplina RED en skills/agentes | P1/P3/P6 migran esas instrucciones a fuentes canónicas y consumidores finos | **Cambiar sólo las assertions de ubicación** cuando el texto se mueva. Deben exigir el mismo requisito en `packets/common.md`, `packets/roles/*.md` o `packets/substages/*.md`, y además que el consumidor apunte a esa fuente. No eliminar requisitos. Justificación: sección “Justificación de tests existentes modificados” del spec. |
| `tests/validate-consistency.sh`, F008 | Diversidad reviewer/implementer en perfiles ordinarios | P4 introduce una excepción ligada a ejecución, no elimina el guard global | **Mantener sin debilitar.** Agregar cobertura separada de excepción válida/inválida; no convertir la desigualdad ordinaria en aceptación global. |
| `tests/validate-consistency.sh`, F009 y F011 | Permisos por rol, higiene del validator y baseline de instalación | P3/P4/P6 preservan scopes y compatibilidad | **Mantener.** F011 sigue siendo deuda de copia instalada y debe compararse como 123/1 hasta probar el destino aislado. |
| `tests/validate-odoo-specialization.sh`, P1 | Scopes de test-writer/implementer y diversidad reviewer/implementer Odoo | P3 y compatibilidad ordinaria de P4 | **Mantener.** La desigualdad de modelos sigue siendo correcta fuera de una ejecución autorizada ADR-010. |
| `tests/validate-odoo-specialization.sh`, P5 | Presencia/integración básica de instalación | P6 agrega raíz instalable aislada | **Mantener y complementar**, no reemplazar, con `CDAD_INSTALL_ROOT` y smoke desde proyecto consumidor en integración final. |
| `docs/specs/cdad-010-opencode-permissions/run-checks.sh`, A1–A7/A11 | Clasificación task-able, scopes y allowlists | P3 declara que el paquete conserva exactamente esas restricciones | **Mantener.** Son oráculo de no regresión; el nuevo runner black-box debe verificar además el paquete resultante, sin duplicar toda esta batería textual. |
| `docs/specs/cdad-010-opencode-permissions/run-checks.sh`, A8 | Frases en `opencode-delegation.md`, `SKILL.md` y orquestador | P6 migra consumidores hacia paquete canónico | **Cambiar únicamente si la frase se mueve**, exigiendo referencia explícita al renderer/policy canónicos y conservación de `write: ask`/Task. Aplica la justificación expresa del spec. |
| `docs/specs/cdad-005-receiving-feedback/run-checks.sh`, C4b | Handoff conserva transmisión íntegra del protocolo | P1/P3/P6 reducen y componen handoffs | **Cambiar si `handoff-prompts.md` deja de contener el cuerpo**: comprobar referencia canónica más presencia de la regla en el paquete común/rol correspondiente. |
| `docs/specs/cdad-009-parallel-dispatch/run-checks.sh`, C4a y reglas de packet | Handoff autocontenido, scopes disjuntos y packet ortogonal | P1/P3/P6 | **Mantener semántica; ajustar ubicación si se canonicaliza.** El renderer no puede borrar owned files/do-not-touch ni el aislamiento entre sesiones. |
| Otros `docs/specs/*/run-checks.sh` auditados (006, 007, 008) | Seguridad git, debugging y planning | Reglas potencialmente incluidas en common/deltas pero no alteradas por P1–P6 | **Mantener sin cambios**, salvo movimiento textual demostrado por el diff futuro; en ese caso aplica la misma regla de fuente canónica + referencia del consumidor. |

No existe cobertura black-box actual suficiente para P1, P2, P4, P5 o P6.
Los greps históricos prueban presencia de texto, no composición determinista,
JSON canónico, binding de autoridad, path policy, métricas ni paridad
source/installed. P3 tiene cobertura parcial de permisos, pero todavía no del
paquete renderizado.

## Tests nuevos requeridos por el contrato

El runner nuevo debe ser black-box y mapear cada caso a una postcondición:

- **P1:** matriz completa rol/subfase; composición common + role + delta +
  request, bytes deterministas, ausencia de reglas cruzadas y límite de 12.000
  bytes estáticos.
- **P2:** metadata JSON canónica; revalidación byte a byte; rechazo de
  tampering, hash/pareja/path/scope/input inválidos, traversal y symlink escape.
- **P3:** test-writer sin implementation/repository-read y sólo escritura de
  tests; implementer sin escritura de tests; architect/reviewer/scribe
  read-only; mismos límites con política de modelo único.
- **P4:** OpenCode autorizado y Codex construction autorizado; rechazo de cada
  binding discordante, autoridad ausente, revocación, vencimiento, epic cerrado,
  herencia y scope no permitido; `basic` ordinario compatible y excepción
  inválida rechazada antes de `basic`.
- **P5:** `active_packet=null`; validación exhaustiva cuando existe; match exacto
  al render; métricas con identidad ligada al estado, `configured`/`reported`
  separados, `null` honesto y enteros no negativos.
- **P6:** Task/chat producen el mismo contrato; clasificación y precedencia de
  tests colocados; roots aislados sin tocar `HOME`; CLI instalado invocable
  desde consumidor sin wrapper del repo y con paridad exacta.

No corresponden property tests en esta feature: los invariantes son finitos y
deterministas y el spec exige matriz/fixtures concretos. Tampoco corresponde un
E2E de runtime OpenCode en 003-001: está diferido explícitamente a integración
003/004. Sí corresponde un smoke de instalación aislada como aceptación P6.

## Plan RED propuesto para Tarea 1

Tarea 1 debe abrir con un runner focalizado y una separación explícita entre
comportamiento y disponibilidad.

1. Crear fixtures mínimos de proyecto, estado, execution context, autoridad y
   árbol de paths bajo `tests/`, todos autocontenidos y en raíces temporales.
2. Crear un bloque **T1-contract RED** que invoque un consumidor público ya
   existente con una ejecución ADR-010 válida donde reviewer e implementer
   reportan el mismo modelo. El assert esperado es aceptación; hoy debe fallar
   por rechazo de política/binding, con diagnóstico observable y no por
   `command not found`, import o archivo futuro ausente.
3. En el mismo bloque, conservar el control ordinario: misma igualdad sin
   `model_policy=epic-003-single-model` debe rechazarse. Así el RED prueba la
   excepción estrecha y no la eliminación del guard.
4. Agregar casos negativos atómicos P4, cambiando un solo campo por fixture:
   execution id, epic, feature, runtime/scope, authority, delegación, etapa y
   vencimiento. Cada caso debe fallar por una assertion de resultado/diagnóstico.
5. Agregar P5 parcial: `active_packet=null` válido y objeto incompleto inválido.
6. Agregar P6 parcial/path policy: traversal, symlink escape, test colocado con
   precedencia sobre implementation y `implementation` sin permiso de editar
   tests.
7. Crear un bloque separado **interface availability** para la futura
   `cdad_packet.py validate-state`. Puede quedar BLOCKED antes de la interfaz,
   pero no cuenta como evidencia RED. Cuando exista, migra los mismos fixtures
   al entrypoint canónico sin cambiar los resultados esperados.
8. Ejecutar sólo el runner focalizado para la evidencia RED. Gate: al menos el
   caso positivo autorizado falla por una comparación/assertion contractual;
   ningún fallo es import/ausencia de comando. Después, ejecutar los dos
   baselines para confirmar que RED no alteró pruebas históricas.

## Aclaración mínima de spec requerida antes de escribir RED

El contrato dice simultáneamente que antes de la CLI el RED se demuestra sobre
“consumidores existentes”, que la disponibilidad futura se separa, y que las
pruebas usan `CDAD_INSTALL_ROOT`/`--project-root`. Sin embargo, no define qué
interfaz pública existente recibe `EXECUTION.json`, project root e install root
durante ese RED. En el baseline, la ejecución observable de
`validate-subagents.sh` está acoplada a la copia instalada y produce F011; usarla
sin un canal de fixture confundiría el comportamiento P4 con drift externo.

Agregar al spec/plan una sola firma de compatibilidad para Tarea 1, por ejemplo:

```text
validate-subagents.sh --project-root ROOT --execution-context EXECUTION.json
CDAD_INSTALL_ROOT=ROOT_INSTALADO
```

o declarar explícitamente otro consumidor público existente con argumentos
equivalentes. Debe especificarse que los tres inputs operan sobre fixtures y no
modifican la instalación. Esta aclaración no anticipa implementación: fija la
interfaz observable necesaria para que el RED requerido sea semántico y
reproducible. Hasta elegir esa firma, el AUDIT recomienda **no escribir T1 RED**.

## Archivos leídos

Repositorio:

- `docs/specs/003-001-role-packets/spec.md`
- `docs/specs/003-001-role-packets/plan.md`
- `docs/specs/003-001-role-packets/approval.md`
- `docs/specs/003-001-role-packets/discovery.md`
- `docs/systemPatterns.md`
- `docs/adr/ADR-010-modelo-unico-mvp-epic-003.md`
- `tests/validate-consistency.sh`
- `tests/validate-odoo-specialization.sh`
- `docs/specs/cdad-005-receiving-feedback/run-checks.sh`
- `docs/specs/cdad-006-git-safety-close/run-checks.sh`
- `docs/specs/cdad-007-systematic-debugging/run-checks.sh`
- `docs/specs/cdad-008-granular-planning/run-checks.sh`
- `docs/specs/cdad-009-parallel-dispatch/run-checks.sh`
- `docs/specs/cdad-010-opencode-permissions/run-checks.sh`
- `docs/specs/cdad-010-opencode-permissions/test-audit.md`

Instrucciones de rol fuera del repositorio:

- `<skills-instaladas>/cdad-cycle/SKILL.md`
- `<skills-instaladas>/cdad-cycle/references/handoff-prompts.md`
- `<skills-instaladas>/cdad-cycle/references/stage-3-tdd.md`
- `<skills-instaladas>/cdad-spec-and-test/SKILL.md`

## Comandos ejecutados

- Inventario con `rg --files tests docs/specs` filtrado a `tests/**`,
  `run-checks.sh` y `test-audit.md`.
- Búsqueda `rg -n -i` de términos de packet/handoff/model/scope/install sobre
  los archivos de prueba permitidos.
- `bash tests/validate-consistency.sh`.
- `bash tests/validate-odoo-specialization.sh`.
- `bash docs/specs/cdad-010-opencode-permissions/run-checks.sh`.
- Lecturas con `cat`/`sed` sólo de los archivos enumerados arriba.
- `context.sh list`, que respondió que no era una sesión nodeterm; no se
  reintentó.

## Límites de evidencia

- No se leyó implementación ni se ejecutó `install.sh` o
  `scripts/validate-subagents.sh` directamente; su resultado sólo se observó
  cuando lo invocaron runners permitidos.
- No se inspeccionó el diff ni se verificó el commit/branch desde git para no
  ampliar el perímetro recibido.
- Parte de las lecturas batch produjo salida truncada en la capa de herramienta;
  se hicieron lecturas dirigidas completas de los runners principales y del
  audit previo. Para los checks históricos 005–009, la conclusión se limita a
  las assertions relevantes encontradas y no certifica cada línea del archivo.
- La auditoría no afirma que los tests futuros pasen ni que la CLI exista. Su
  conclusión es de trazabilidad y diseño de RED.

## Veredicto del AUDIT

**Aprobar con una condición previa a RED:** materializar la aclaración mínima de
la interfaz del consumidor existente para Tarea 1. El resto del contrato es
testeable. Tras esa aclaración, el plan RED separa correctamente un fallo de
comportamiento actual de la indisponibilidad de la CLI futura y conserva los
oráculos históricos sin debilitar permisos ni diversidad ordinaria.

## Resolución HITL delegada del AUDIT

Aprobado por Codex (agent-delegated) el 2026-09-17. La firma propuesta ya
existe en §4 del spec; se añade precisión sobre el layout del destino aislado
y la separación de pruebas por disponibilidad. Tarea 1 implementa también
la raíz de instalación requerida por su propio guard, antes de consumidores.

Corrección al plan de tests: los invariantes explícitos sí requieren pruebas
por propiedades según CDAD. Incluir al menos 100 entradas con seed fijo para
integridad canónica/determinismo sobre contratos y objetivos válidos; no se
piden propiedades de cobertura ajenas al spec. La matriz finita de roles
complementa esa prueba, no la reemplaza.

Las rutas personales del payload se sustituyeron por referencias genéricas
al materializar este informe. Ningún test existente se elimina.
