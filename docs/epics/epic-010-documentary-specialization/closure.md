# Epic epic-010-documentary-specialization — Closure

**Cerrado:** 2026-10-31 · **5/5 features** · **aceptación del piloto ejercida por
mandato HITL, no aprobada directamente por el dueño** · **sin push y sin publicación
del producto documental**.

## Summary

Extender CDAD para producir documentación funcional verificable —relevamientos,
procesos, historias de usuario— sin crear agentes, etapas, campos del estado ni etiquetas
nuevas: la especialización se declara con el transporte existente, se gobierna por una
casa normativa única y se acredita con dos registros de cierre que no se sustituyen
(control estructural y revisión semántica independiente). El resultado se validó con un
piloto que detectó, en un desafío sembrado y sin ver el producto, las tres clases de
defecto comprometidas.

## Features delivered

| Orden | Feature | Cierre | Resultado observable |
|---|---|---|---|
| 0 | `010-000-continuity-relative-root` | 2026-10-29 (aprobado por Pablo) | raíces relativas/absolutas equivalentes aceptadas sin debilitar controles, validado por la vía instalable |
| 1 | `010-004-packet-dispatch-ergonomics` | 2026-10-31 | contexto de ejecución v2 declarado, `render --route C` sin retranscribir el cuerpo, intake exclusivo con diagnóstico |
| 2 | `010-001-documentary-contracts` | 2026-10-31 | una casa normativa documental y obligación por puntero en fuentes, bloques y 22 agentes |
| 3 | `010-002-documentary-role-integration` | 2026-10-31 | encargo documental operable con los campos existentes; aplicabilidad Odoo y destinatario coherente |
| 4 | `010-003-documentary-pilot` | 2026-10-31 | piloto con entregable trazable y detección independiente 3/3 de los defectos comprometidos |

## Acceptance criteria (plan §Criterios de aceptación, los nueve)

| # | Criterio | Estado |
|---|---|---|
| 1 | Las cinco features cierran individualmente con evidencia de sus contratos | ✅ **cumplido — evidencia, no test**: los cinco `closure.md` con sus reviews y recibos; un test que compruebe que los archivos existen sería tautológico (`integration.md` §1, fila 1) |
| 2 | `010-000`: regresión de raíces relativas/absolutas, rechazo de escapes reales, revisión independiente y validación del artefacto instalable; la instalación global no se usa como sustituto de corregir la fuente | ✅ **cumplido con alcance declarado**: `test_A` (relativo == absoluto), `test_C` (paquete alterado, `../fuera.txt`, `/etc/passwd` y symlink exterior rechazados), `test_D` (`CDAD_INSTALL_ROOT` aislado); la revisión independiente es evidencia (`review.md`, `isolated-validation.md`) y el drift global se declaró, no se reparó |
| 3 | El flujo canónico genera, instala y resuelve los perfiles documentales; las restricciones por rol se conservan | ✅ **cumplido (test)**: `TestDistribution` y `TestFinalIsolatedDistribution` de 010-002 |
| 4 | Los agentes genéricos y Odoo mantienen su comportamiento previo; la combinación documental/Odoo se verifica según 010-002 | ✅ **cumplido (test + regresión)**: derivación sobre 100 combinaciones, 11 agentes por runtime, `documentary_odoo_journey`, guardas de Claude idénticas |
| 5 | El piloto identifica un defecto estructural mediante un control automático | ✅ **cumplido (test)**: veredicto negativo con `cause == missing_fragment`, documento y referencia; producto que cita sólo fragmentos inventariados |
| 6 | La revisión independiente identifica una afirmación sin respaldo, una contradicción omitida y una referencia incorrecta, con ubicación y evidencia | ✅ **cumplido sobre el desafío declarado**: `challenge-review.md` (F-1/F-2/F-3), `challenge-contrast.md` (3/3, cero omisiones), `semantic-evidence.md` §2. No se exige a un script decidir verdad semántica: la fracción testable es que un candidato semánticamente defectuoso **sea estructuralmente aceptado** |
| 7 | El entregable corregido conserva trazabilidad; límites y pendientes visibles; la aceptación funcional queda registrada | ✅ **cumplido**, con la precisión del plan: la aceptación fue **ejercida por mandato HITL** (mandato del 2026-10-30, §1 y §3), **no** aprobada directamente por el dueño (`010-003/functional-acceptance.md`) |
| 8 | No se modifican verificadores ni insumos protegidos desde GREEN; cambios legítimos vuelven al rol competente y a aprobación | ✅ **cumplido como evidencia de proceso**: `review.md`/`review-002.md` y `deviation-green-accreditation-2026-10-31.md` (I-10 declarado y restituido). El control de inventario detecta deriva **actual** de las fuentes, no la historia del diff |
| 9 | Validación y regresión pertinentes pasan; sin datos privados ni modelos concretos en el producto instalable; sin push ni publicación | ✅ **cumplido en lo medido**, con una excepción declarada: suite `1926 passed, 5 skipped, rc=0`; `offenders == []` en skills y 11 agentes × 2 runtimes sin `model:`; nombre del aprobador ausente de `skills/`, `sources/`, `agents/`. **No hubo push.** El dueño aprobó publicar 010-004 el 2026-10-31 como acto **separado**; la publicación documental no se hizo y la instalación volvió a quedar por detrás (`--check` rc=1, 52 archivos) |

## Brief retrospective

### What worked well

- **Detectar los defectos antes de construir.** Las rondas de `plan-review` y de review
  independiente encontraron bloqueantes reales —en `010-001` la norma omitía dos reglas de
  su propia decisión mientras 11 tests estaban verdes; en `010-002`, tres bloqueantes
  cerrados **con los controles escritos antes de la corrección**. El costo se pagó en
  papel, no en producto deshecho.
- **Re-verificar el diff completo, no el delta.** En `010-003`, T6 encontró un bloqueante
  nuevo (la divergencia sobre el inicio del plazo no estaba declarada) y T7 no sólo lo
  corrigió: re-verificó **todo** el diff (`product-review-002.md`), sin bloqueantes
  abiertos.
- **Auditar la cobertura antes de escribir tests.** La integración E3 se hizo con el mapa
  de cobertura existente primero y terminó con **cero tests nuevos y cero modificados**:
  el flujo completo ya estaba ejercitado de punta a punta por `TestDistribution` y
  `TestFinalIsolatedDistribution`. Un E2E nuevo habría duplicado el oráculo y creado una
  segunda definición de la misma promesa.

### What got complicated

- **Cinco vueltas de `plan-review` en `010-003`** (B-1..B-4 y O-1..O-8; BN-1 y NB-1..NB-6;
  BN-2 y O-9..O-12; BN-3 y O-13/O-14; la quinta acotada al delta), cada una con sus
  resoluciones registradas. El costo fue alto y el beneficio real, pero el epic no tiene
  todavía un criterio de corte para esa iteración.
- **La desviación I-15.** El request del ensayo no citó los commits de fijación que el
  contrato exigía. La fijación existe y es comprobable (`cd2d57b3`, `4c822805`, ambos
  antecesores de `d2307c42`), pero el ensayo es **de un solo tiro**: se declaró la no
  conformidad en `semantic-evidence.md` §5 en lugar de re-despachar. La cláusula de forma
  incumplida no se presenta como cumplida.
- **El intento 1 de la suite interrumpido** se conserva completo en
  `evidence/closing-suite/attempt-1-interrupted/` y **no es evidencia de nada**; el
  intento 2 dio el veredicto. A eso se suma, en `010-002`, un intento 1 con `rc=1` y
  cuatro regresiones estructurales en superficies compartidas: los oráculos existían; lo
  que falló fue **ejecutarlos**.

### Lessons for future epics

- Una unidad que toca superficies compartidas (`SKILL.md`, adaptadores, bloques de
  paquete) debe incluir en su verificación los oráculos de esas superficies, no sólo los
  de su propio contrato. La suite de cierre fue el único control que los miró.
- Un verde estructural no acredita cobertura ni fidelidad; declarar **dónde** vive cada
  evidencia —test, documento de proceso o sesión— evita presentar cumplimiento donde hay
  límite.
- La selección de tests por cobertura existente funciona y conviene formalizarla en las
  fuentes del skill (siete hogares y agentes generados) en vez de dejarla como directiva
  verbal del día.

## Technical debt carried forward

Registrada en `backlog.md` del epic, cada ítem con su condición de cierre; no se borra:

| Ítem | Qué queda abierto | Destino |
|---|---|---|
| **I-6 / R2** | la fila 3 de la matriz no distingue un request histórico de uno nuevo sin localizador | gate del orquestador con contrato propio |
| **R-A** | `--replace-packet` y `--resume-packet` no nombran el bloqueo v1 y no escalan | unidad propia con su test |
| **I-8 / I-14** | el test-writer no puede leer los `instruction_sources` que su propio bloque le manda leer | unidad sobre el diseño de scopes de 010-002 |
| **I-9** | dos copias del skill componen paquetes distintos (hashes viejos con el CLI instalado) | unidad que declare la raíz usada o haga fallar cerrado `prepare` |
| **I-10** | la identidad del paquete no está pineada a sus fuentes de instrucción | verificar los `sha256` declarados o render pineado al conjunto declarado |
| **I-11 / I-12** | localizadores frágiles de `005-006` PD-10 y `006-002` PD-2(b) | localizar por contenido y comparar por bloque normalizado |
| **I-13** | la tabla cerrada de tipos de artefacto se aplica al materializar y no al recibir | validar en `receive` o reparación explícita con disciplina CAS |
| **I-15** | el request del ensayo no citó los commits de fijación | chequeo en `prepare` o en el procedimiento de despacho, con test |
| **Canario** | no distingue la suite de otro gestor de agentes | declararlo medición del entorno o aislar la ventana |
| **Deriva de instalación** | 52 archivos; la instalación real está por detrás de la publicación de 010-004 | instrucción explícita del dueño para publicar |
| **Volumen de la suite** | ~1 h de corrida; reducirla exige su propia unidad con mapa test→promesa | unidad futura |
| **Directiva de selección** | «cobertura existente primero» no está escrita en las fuentes del skill | unidad sobre los siete hogares y los agentes generados |
| **`deferred-hardening`** | los de las cinco specs (parser universal, formatos binarios, corpus de clientes, detección semántica automática, protección por hash, paridad esquema↔CLI, sandbox) | conservados con sus disposiciones en cada `closure.md` y transcriptos en `010-003/closure.md` §4 bis (R6) |

También se llevan: `P-01` y `P-02` del producto del piloto (abiertos y declarados), y los
nits diferidos `N1/N2/O4` de `010-001` y `O2/O4` de `010-002`.

## Architectural decisions made

- **Ningún ADR fue adoptado por las cinco unidades.** `010-000`, `010-004` y `010-002`
  cerraron declarando «sin ADR nuevo»; `010-001` dejó una propuesta **no adoptada** en
  `scribe-report.md` y el reviewer se abstuvo de cotejar la tabla de decisiones.
- **En este cierre se propone uno**, por ser decisión del epic y no de una unidad:
  **ADR-040 — Especialización documental por contrato: una casa normativa y dos registros
  de cierre** (Confidence **Media**), destino
  `docs/adr/ADR-040-especializacion-documental-por-contrato-casa-unica-y-dos-registros.md`.
  Su aprobación y su fila en la tabla de decisiones son del dueño y del orquestador
  (ADR-003); este documento la propone, no la adopta.
- Las decisiones ya vigentes que gobiernan el epic —ADR-003 (materialización), ADR-014
  (recepción ≠ aprobación), ADR-034 (casa única con deberes de rol), ADR-036 (verificador
  del productor), ADR-011 (autonomía supervisada)— no se re-enuncian acá.

## Notas finales

- **Medición de cierre:** suite completa `1926 passed, 5 skipped, rc=0` sobre `c229a671`,
  canario delta 0; desde ese commit sólo cambiaron documentos y estado. Integración E3:
  **26 nodos decisivos verdes** (`26 passed in 140.91s`, rc=0), **cero tests nuevos**.
- **Lo que este cierre no declara:** el epic **no está publicado**; no hubo push ni
  actualización de la instalación global, y la instalación real está por detrás de la
  publicación de 010-004. Mientras tanto la obligación documental llega por el paquete y
  por la toolchain del repositorio, no por el agente instalado.
- **Límites del piloto, conservados:** muestra **sembrada y sintética**, no detección a
  ciegas, no detección infalible, no conducta general de modelos, no fidelidad de un
  documento de cliente; la independencia es **contractual y de alcance, no aislamiento
  técnico**; `pytest` no es un sandbox.
- La aprobación de este `closure.md` y del Memory Bank es del dueño; la materialización y
  el commit (`docs(memory): close epic epic-010-documentary-specialization`) son del
  orquestador (ADR-003).
