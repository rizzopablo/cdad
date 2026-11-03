# Review — 013-001-criterion-coherence

**Paquete:** `cmp` entre `render --request` y `PACKET.md` sin diferencias; metadatos y sha256 del contrato coinciden.
**Objeto:** `9e940e3c..838d6b08`.
**Archivos modificados:** ninguno. La regeneración y las mutaciones se hicieron en una copia `git archive` en `/tmp/tmp.KvHmnxnTGb`.
**Suite completa no realizada:** corrí solo la selección focal.

## Hallazgos bloqueantes

**B1. Required: Odoo mantiene corridas completas automáticas (PC-13, §5)**
- Verdict: BLOCKING · Bucket: h
- **Ubicación:** `skills/odoo-make-env/references/run-budget-protocol.md:38-40`, `skills/odoo-make-env/SKILL.md:35,140`.
- **Evidencia:** siguen «GREEN closure: ONE `test-all`», «Review: 1 `test-all`» y «Review fix: ONE `test-all` gate». §5 ordena quitarlas, y el principio 1 del mismo archivo las contradice.
- **Consecuencia:** un proyecto Odoo corre la suite completa en cada cierre sin autorización.
- **Cierre:** condicionar esas filas a autorización expresa, conservar `test-clean` cuando aplique y mantener el anti-loop.

**B2. Required: `make test` sigue siendo el runner por defecto de AUDIT y GREEN (PC-13)**
- Verdict: BLOCKING · Bucket: h
- **Ubicación:** `skills/odoo-make-env/SKILL.md:32`, `skills/odoo-test-writer/SKILL.md:6-7,118,130`, `sources/roles/test-writer.md:152`, `sources/roles/implementer.md:104`, y sus agentes derivados.
- **Evidencia:** el diff cambió la descripción de «full suite on the warm DB» a «focused + proportional regression», pero no cambió el target ni su asignación a roles. Ese texto describe una selección que `make test` no hace: la spec prohíbe inventar flags y targets, y el comando sigue siendo el de la suite.
- **Consecuencia:** obedecer la instrucción ejecuta la suite completa sin autorización.
- **Cierre:** AUDIT y GREEN usan una selección declarada (`test-one` o mecanismo del proyecto); `make test` queda como corrida completa autorizada, descrita con fidelidad.

**B3. Required: persisten presupuestos rivales de propiedades (PC-10, PC-11)**
- Verdict: BLOCKING · Bucket: h
- **Ubicación:** `run-budget-protocol.md:28-30,88-91`.
- **Evidencia:** «default N … small (8-10)» y «Raising N belongs to hardening». Contradice `odoo-test-writer` ya corregido y PC-11, que niega que aumentar sea automáticamente hardening. El encargo pedía incluir Odoo.
- **Cierre:** sustituir esas líneas por una referencia al presupuesto declarado de R2.

**B4. Required: los cierres de merge y epic siguen exigiendo suite completa (PC-13)**
- Verdict: BLOCKING · Bucket: h
- **Ubicación:**
  - `skills/cdad-cycle/references/stage-5-merge.md:9` («Verify full CI»), `:24` («Mandatory checks … Full suite») y `:174-177`.
  - `skills/cdad-cycle/SKILL.md:372-375,543`.
  - `skills/cdad-epic/references/epic-closure.md:93,101`.
- **Evidencia:** las líneas 27-32 de stage-5 dicen lo contrario de la línea 24. El gate «CI green» o «local green suite equals the gate» no se puede cumplir con «suite completa no realizada». `epic-closure.md` no está en §5, pero el encargo cubre cualquier consumidor.
- **Consecuencia:** no hay camino coherente de cierre sin autorización, o el cierre se declara verde sin evidencia.
- **Cierre:** expresar esos gates como evidencia según la política, y registrar «suite completa no realizada» y «gate no ejecutado» como salidas válidas.

**B5. Required: la ruta legacy no transmite el criterio nuevo (PC-4, PC-6, PC-8, PC-9)**
- Verdict: BLOCKING · Bucket: h
- **Ubicación:**
  - `skills/cdad-cycle/references/handoff-prompts.md:290` («Writing new tests is RED»), contradicho por `:324` en el mismo prompt.
  - `handoff-prompts.md:171-200`: AUDIT sigue con modificar/intacto/ignorar. No tiene disposiciones, contribución ni mapa de conservación, y exige justificar en la spec cada test modificado.
  - `skills/cdad-cycle/SKILL.md:204,303` y `handoff-prompts.md:714`: «one postcondition, one test» y «one postcondition per test-writer» son cuotas indirectas.
- **Consecuencia:** un AUDIT legacy no puede producir un sustituto aprobable, y la unidad atómica sigue siendo la postcondición.
- **Cierre:** alinear esos prompts con R2/PC-4/PC-6 y usar promesa en vez de postcondición como unidad.

**B6. Required: faltan el recorrido de sustitución en superficies obligadas y el control de la plantilla (PC-4, PC-6, PC-7, §5)**
- Verdict: BLOCKING · Bucket: h
- **Ubicación:** `references/stage-3-tdd.md`, `references/re-entry.md`, `skills/cdad-cycle/SKILL.md`, `skills/odoo-test-writer/SKILL.md`, `assets/spec-template/test-audit.md`.
- **Evidencia:**
  - Un grep sin distinguir mayúsculas de `sensibil|sustitu` no da ninguna coincidencia en los primeros cuatro.
  - §5 exige ahí recorrido POST-AUDIT, validación de sustitutos y recorridos RED/POST-AUDIT.
  - El diff de `test-audit.md` son 9 líneas añadidas; no se tocó el checklist «Test Audit Gate», que debe comprobar disposición única, destinos y aprobación.
- **Consecuencia:** el orquestador puede aceptar un sustituto sin verificar sensibilidad ni conservación en re-entry, así que la invariante de conservación no tiene control operativo.
- **Cierre:** añadir el recorrido y los checks por referencia a R2, y ampliar el gate de la plantilla.

## Hallazgos opcionales

**O1. Consider: los 5 tests no detectan B1 ni B3**
- Verdict: OPTIONAL · Bucket: m
- **Evidencia:** las 7 mutaciones literales fallaron en el test esperado. En cambio, sobrevivieron dos regresiones semánticas: un mandato «ALWAYS runs at closure» junto al token de autorización, y «8-10» en `odoo-test-writer`.
- **Consecuencia:** una regresión de presupuesto en Odoo pasaría en verde. La spec reparte esta carga con la revisión semántica. Va a deuda, salvo que se quiera un `assert not` para `8-10` en superficies Odoo.

**O2. Consider: `ADR-020` y `ADR-039` no apuntan a `ADR-041`**
- Verdict: OPTIONAL · Bucket: m
- ADR-041 registra bien la relación y no ratifica ADR-039, pero quien lea solo los ADR antiguos no ve la decisión posterior. Conviene una nota de una línea, o aceptar el índice de `systemPatterns.md` como mecanismo.

**O3. Nit: `cdad-spec-and-test` sigue presentando su tabla propia**
- Verdict: OPTIONAL · Bucket: m
- La duración quedó corregida y la skill no se retiró. La tabla de gates 0→4 (`SKILL.md:96-102`) sigue, y el aviso de que no sustituye al ciclo solo aparece en la última fila. Conviene moverlo a la cabecera de la tabla.

**O4. Nit: mandatos ambiguos de suite verde**
- Verdict: OPTIONAL · Bucket: l
- `stage-4-review.md:180,188`, `SKILL.md:73,541` y `sub-agent-strategies.md:36,138` dicen «suite green» o «suite always green» sin precisar. Se pueden leer como la selección ejecutada, pero conviene aclararlo al cerrar B4.

## Verificado sin defecto

- **Agentes:** `make agents` en la copia reproduce `agents/` sin diferencias. En `build/` solo difieren dos `probe_*.py` no presentes en la copia.
- **Gate:** el diff de `cdad-ci-gate.py` toca solo el docstring; no hay workflow ni CLI nuevos.
- **Instalación limpia:** se conserva en el hogar canónico y en `odoo-reviewer`, y queda distinguida de la suite completa.
- **Aislamiento del test-writer:** «Walk the codebase» fue retirado; RED y Pre-RED no ordenan leer implementación.
- **Suite en paquetes:** `common.md` y `feature-plan-template.md` están alineados.
- **Política y disposiciones:** los hogares `stage-3-tdd`, R2 y la disposición única en rol y paquetes son correctos.
- **ADR-041:** no inventa la vigencia de ADR-039.

## Evidencia

```
python3 scripts/cdad_packet.py render --request <REQUEST>   → rc=0; cmp SAME
sha256sum spec.md → 79b9c12b…bfd00 (coincide)
git diff 9e940e3c..HEAD; rg de suite/cuotas/sustitutos sobre skills y sources
make agents (copia); diff -rq agents build
pytest tests/test_013_001_criterion_coherence.py tests/test_004_003_t5_reentry_equivalence.py → 13 passed
Mutación: A, A2, B, C, D, E, E2 → cada una falla el test esperado; PC13-regress, PC10-odoo → rc=0 (sobreviven)
```

## Abstentions

- **Fidelidad semántica por línea:** la comparación con `docs/epics/.../plan.md` y con `UNIT-CONTRACT.md` no se hizo; contrasté contra la spec aprobada.
- **`test-audit.md` y POST-AUDIT:** no audité el acta de sustitución de `test_004_003_t5`, salvo su diff y su verde focal.
- **`cdad-doctrine-check.py` y validadores de paquetes:** no los ejecuté; no aprecié que la unidad los tocara.
- **`implementer.md:104`:** vi el fragmento relevante, no el párrafo completo; el hallazgo B2 se sostiene por `odoo-make-env:32`.
- **Conducta real de agentes:** queda fuera del alcance, porque la spec promete la norma y no la obediencia.

## Priorización del delegado del dueño (2026-11-02)

B1-B6 BLOQUEANTES: se corrigen en review-fix (comprometen el uso previsto: suite completa sin autorización o recorrido de sustitución inaplicable). O3 se corrige junto con B4/B5 si es trivial. O1, O2 y O4 van a deuda declarada (O1: los 5 tests no detectan regresión semántica en Odoo; la spec reparte esa carga con la revisión independiente).

---

# Re-review — 013-001-criterion-coherence (review-002)

**Resultado: quedan 3 bloqueantes.** B1, B2, B3 y B6 están cerrados; B4 y B5 cerraron solo en parte, y el fix introdujo una regresión en la instalación limpia de Odoo.

**Paquete:** ruta C. `render --request` y `PACKET.md` coinciden (`cmp` SAME), y la identificación de ruta C coincide con la recibida. El sha256 del contrato coincide.
**Objeto:** commit `88bd4335`, contra la spec aprobada y `review.md`.
**Archivos modificados:** ninguno. `make agents` corrió en una copia `git archive`.
**Suite completa no realizada:** solo selección focal, según el encargo.

## Cierre de B1-B6

| Hallazgo | Estado | Evidencia propia |
|---|---|---|
| B1 corridas completas Odoo | **Cerrado** | `run-budget-protocol.md:41-43` y `odoo-make-env/SKILL.md:35,139` quedan condicionadas a autorización; el anti-loop se conserva. |
| B2 `make test` por defecto | **Cerrado** | `odoo-make-env/SKILL.md:32-33`, `odoo-test-writer/SKILL.md:118,130`, `implementer.md:104-105`, `test-writer.md:152`. |
| B3 presupuestos rivales | **Cerrado** | No quedan coincidencias de `8-10` en `skills` ni `sources`; `run-budget-protocol.md` remite a R2. |
| B4 cierres de merge y epic | **Parcial** | Ver R2 más abajo. |
| B5 ruta legacy | **Parcial** | Las cuotas de `SKILL.md:204` y `handoff-prompts.md:713` están corregidas, y AUDIT tiene disposiciones. El fix abrió la contradicción R3. |
| B6 recorrido de sustitución | **Cerrado** | `stage-3-tdd.md`, `re-entry.md`, `cdad-cycle/SKILL.md:127`, `odoo-test-writer/SKILL.md`, y el gate de `test-audit.md:115-117`. |
| O3 `cdad-spec-and-test` | **Cerrado** | El aviso quedó en la cabecera de la tabla (`SKILL.md:96`). |

## Hallazgos bloqueantes

**R1. Required: el fix permite omitir la instalación limpia sin bloqueo (PC-12, invariante 6; regresión)**
- Verdict: BLOCKING · Bucket: h
- **Ubicación:**
  - `sources/roles/implementer.md:104`, y sus agentes derivados
  - `sources/roles/reviewer.md:123`
  - `sources/roles/orchestrator.md:344`
  - `skills/odoo-make-env/SKILL.md:34,139`
  - `skills/odoo-test-writer/SKILL.md:131-132`
- **Evidencia:** antes del fix, `make test-clean` era obligatorio cuando la spec lo marcaba. Ahora dice «when … the run is authorized (otherwise suite completa no realizada)».
  - El hogar canónico, `stage-3-tdd.md:88-93`, ordena otra cosa: si el runner une instalación y suite no autorizada, se informa el bloqueo y se pide autorización o resolución, sin omitir nada en silencio.
  - `odoo-reviewer/SKILL.md:84-85` sigue exigiendo `test-clean` en verde, sin esa condición. El fix dejó dos hogares en desacuerdo.
- **Consecuencia:** un addon puede cerrar sin demostrar instalación desde cero, registrando solo «suite completa no realizada». Esa nota describe otra dimensión y no acusa la obligación incumplida. Es el defecto de esquema que `make-env:45,106` quiere detectar.
- **Cierre:**
  - En esas superficies, sin autorización, la salida pasa a ser **bloqueo de instalación limpia y solicitud de autorización o resolución**, por referencia a `stage-3-tdd.md`.
  - Quitar «otherwise suite completa no realizada» como salida válida de `test-clean`.
  - Conservar `test-clean` acotado al módulo (`make-env:115`) como evidencia de instalación, sin tratarlo como corrida de suite completa.
  - Regenerar agentes.

**R2. Required: quedan gates de cierre que exigen CI o suite en verde (PC-13; resto de B4)**
- Verdict: BLOCKING · Bucket: h
- **Ubicación:**
  - `skills/cdad-epic/SKILL.md:120`: «CI green on main / the epic's release branch», en el gate E3→E4.
  - `skills/cdad-cycle/SKILL.md:376-377` y `stage-5-merge.md:176-177`: «local suite green equals the gate».
- **Evidencia:** las líneas previas ya admiten «suite completa no realizada», pero estas no se tocaron. `cdad-epic/SKILL.md` está en §5, y `review.md` citaba expresamente el segundo texto en B4.
- **Consecuencia:** sin autorización, E3→E4 no puede pasarse honestamente. Los proyectos sin CI siguen con una redacción que se lee como suite completa.
- **Cierre:** expresar ambos como evidencia según la política, con la misma fórmula de `epic-closure.md:101`.

**R3. Required: el prompt legacy de AUDIT prohíbe planificar Añadir (PC-2, PC-4, PC-9; regresión)**
- Verdict: BLOCKING · Bucket: h
- **Ubicación:** `handoff-prompts.md:187`, y también `:377`.
- **Evidencia:** la línea 187 dice «A physically new test is admitted only as Sustituir/Consolidar … new tests for pending behavior belong to RED, never to this AUDIT». Eso contradice:
  - el mismo prompt, que lista Añadir y pide «New tests to write»;
  - `test-audit.md:46`;
  - `packets/substages/test-writer-audit.md`, que sí distingue Añadir.

  Además, `:377` sigue diciendo que POST-AUDIT actualiza «ONLY the audited existing tests» y que los tests nuevos se escriben en RED, contra PC-6.
- **Consecuencia:** legacy y paquetes dan criterios distintos. Un AUDIT legacy no declara la protección faltante de lo pendiente, o se contradice.
- **Cierre:**
  - Reformular `:187`: AUDIT **declara** Añadir, RED lo **escribe**, y solo los destinos de Sustituir/Consolidar se crean en POST-AUDIT.
  - Alinear `:377` con PC-6.

## Hallazgos opcionales

**O5. Consider: `SKILL.md:315,356` conserva «every postcondition has at least one test»**
- Verdict: OPTIONAL · Bucket: m
- La frase admite que un test cubra varias postcondiciones, así que no es una cuota 1:1. Aun así, está redactada por postcondición. Conviene usar «obligation protected» y añadir POST-AUDIT al diagrama de `SKILL.md:303`, que tampoco lo muestra.

**O6. Consider: exigencia residual de justificar en la spec cada test modificado**
- Verdict: OPTIONAL · Bucket: m
- **Ubicación:** `handoff-prompts.md`, regla «Every modified test MUST have explicit justification in the spec», y `test-audit.md:118,121`.
- Queda de B5. Es cumplible si la spec declara el mantenimiento, pero una sustitución de comportamiento vigente debería acreditarse con el mapa de PC-5. Por criterio MVP no bloquea.

**O7. FYI: `state-detection.md:69,71` dice «Whole suite green»**
- Verdict: OPTIONAL · Bucket: l
- Solo enruta estado, no es un gate, y no está en §5. Va a deuda.

## Regresiones buscadas sin defecto

- **Suite automática:** no quedan mandatos en las superficies Odoo aparte de R1 y R2.
- **Runner por defecto:** `test-one` sirve para iterar, sin targets ni flags inventados.
- **Presupuestos rivales:** ninguno.
- **Cuotas:** ninguna 1:1. `test-writer.md:84` y `handoff-prompts.md:401` hablan de promesa.
- **Distribución:** `agents/` no deriva. En `build/` solo difieren `probe_contract.py` y `probe_pd19.py`, ausentes de la copia, igual que en la review anterior.

## Evidencia

```
python3 scripts/cdad_packet.py render --request $P/REQUEST.json → rc=0; cmp SAME
sha256sum spec.md → 79b9c12b…bfd00 (coincide)
git show 88bd4335 (stat y diff de skills/sources); rg de suite/cuotas/CI sobre skills y sources
make agents (copia git archive); diff -rq agents → sin diferencias
pytest tests/test_013_001_criterion_coherence.py tests/test_004_003_t5_reentry_equivalence.py → 13 passed
```

**Commit revisado:** `88bd4335`, con HEAD en `9ed493bd`. Los 13 tests en verde no detectan R1-R3; el defecto es semántico, una carga que la spec asigna a esta revisión.

## Abstentions

- No re-ejecuté las mutaciones de la review previa, porque O1 es deuda declarada.
- `docs/ci-gate.md`, los ADR y `systemPatterns.md`: el fix no los tocó. Solo leí un grep de `ci-gate.md`, no los re-contrasté.
- `epic-integration.md` y `epic-closure.md`: revisé la línea 101 de `epic-closure.md` y el stat del commit; el diff de `epic-integration.md` no lo leí línea por línea.
- Las líneas de `stage-5-merge.md:24-32` las vi en el grep, no en el contexto completo de la sección.
- Sigo sin evaluar la conducta real de los agentes, que queda fuera de la spec.

## Priorización (2026-11-02)

R1-R3 BLOQUEANTES (R1: omitir instalación limpia sin bloqueo compromete el uso previsto de Odoo). O5, O6, O7 a deuda declarada.


## Cierre de R1-R3 (verificación del orquestador, 2026-11-02)

Tras `4adc1e46`: R1 — `test-clean` sin autorización produce bloqueo de instalación limpia y solicitud de autorización (grep en implementer, reviewer, orchestrator, odoo-make-env, odoo-test-writer); las menciones restantes de «suite completa no realizada» corresponden a `make test`/`test-all` (amplitud), no a `test-clean`. R2 — los tres gates usan la fórmula de `epic-closure.md:101`. R3 — `handoff-prompts.md:187,323,377` alineados con PC-2/PC-4/PC-6. `make agents` sin deriva; 30 passed focal (013-001, G2, pd10, generate); `cdad-doctrine-check` OK. **No hubo tercera revisión independiente**: se verificaron los criterios de cierre exactos del reviewer; queda declarado.

Deuda declarada: O1 (los 5 tests no detectan regresión semántica en Odoo), O2 (retroenlaces ADR-020/039 → ADR-041), O4/O5/O7 (redacciones «suite green» y por postcondición residuales), O6 (justificación en spec de cada test modificado frente al mapa PC-5), suite completa no realizada, tests `007_00*` sin agotar en la regresión del POST-AUDIT 2.
