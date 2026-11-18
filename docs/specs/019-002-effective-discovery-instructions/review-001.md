# Revisión independiente — 019-002, candidato T1/T2

**Resultado: hay hallazgos bloqueantes.** Esta revisión no aprueba la feature. PC-4 y PC-11 requieren observaciones previstas para T3 que todavía no se ejecutaron; las señalo como evidencia faltante, pero no bloqueo esta revisión inicial únicamente por ese paso futuro.

Revisé contra la especificación fijada por SHA-256 `5cca6fa6…eb0`, el plan, el diseño aceptado de 019-001 y el diff desde `bc922c04` hasta `5aa4bad0`.

## Hallazgos bloqueantes

### 1. El contexto atribuido no llega de forma fiable al redactor ni al reviewer

**Required · Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-cycle/references/stage-2-specification.md:34–40,55–58`; `skills/cdad-cycle/references/handoff-prompts.md:262–272`; `skills/cdad-cycle/references/re-entry.md:234–244`.  
**Contrato:** PC-2 y PC-9, `spec.md:45–49,115–117`.

La reentrada pide entregar al architect decisiones vigentes, evidencia, propuestas, pendientes y conflictos. Sin embargo, la instrucción concreta de redacción y su plantilla legacy solo enumeran un **resumen del brainstorm**, la plantilla y `systemPatterns.md`. La instrucción de despacho del reviewer identifica el borrador, pero no exige entregarle el **Dialogue context completo**, con entradas superadas identificadas.

Esto deja dos rutas efectivas que permiten perder autoridad, correcciones o calificaciones: el architect puede redactar desde un resumen insuficiente y el reviewer no necesariamente recibe el registro necesario para detectar la pérdida. Una referencia general a que el contexto sea recuperable no asegura que se entregue en estos handoffs.

**Cierre verificable:** reconciliar las instrucciones de redacción y revisión —incluidas las rutas legacy y por paquete que correspondan— para que el architect reciba el contexto cualificado exigido y el reviewer el registro completo con supersesiones. Revisión contextual independiente de las rutas corregidas.

### 2. El registro de diálogo no instruye cómo conservar la procedencia de las correcciones

**Required · Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `sources/roles/orchestrator.md:137–150`; `skills/cdad-cycle/references/stage-2-specification.md:17–19`; `skills/cdad-cycle/references/re-entry.md:232–239`.  
**Contrato y fuente:** PC-2, `spec.md:45–49`; diseño aceptado `operating-design/handoff-fidelity.md`, §§1, 3 y 5.

Las instrucciones efectivas nombran las seis clases y dicen que una corrección sin autoridad no supersede nada. No indican de forma operativa que cada entrada conserve un identificador de mensaje recuperable, fragmento afectado, vínculo entre entrada anterior y corrección, y próxima acción; tampoco ordenan preservar la entrada anterior al aplicar la corrección. Esos elementos están en el diseño aceptado, pero el consumidor operativo examinado no remite a él ni los reproduce.

La comprobación posterior «la corrección está reflejada» no reconstruye una entrada reemplazada o una autoridad que nunca se registraron. Por tanto, una corrección válida puede gobernar el borrador sin que un architect o reviewer nuevo pueda comprobar qué reemplazó y quién la autorizó.

**Cierre verificable:** incorporar o referenciar desde el procedimiento operativo una convención recuperable que cubra autoridad, fragmento, vínculos de supersesión, conservación y siguiente acción; contrastarla independientemente con el diseño aceptado.

### 3. La ruta documentada de redacción presupone una consulta que el contrato hace condicional

**Required · Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-cycle/references/stage-2-specification.md:9–10,19,30–40`; `skills/cdad-cycle/references/re-entry.md:230–244`; `skills/cdad-cycle/references/handoff-prompts.md:267–270`.  
**Contrato:** PC-1, PC-3 y PC-8, `spec.md:41–53,111–113`.

La consulta técnica se dispara solo ante incertidumbre consecuencial o evidencia faltante, pero la instrucción de readiness comienza **«When the consultation returns»**, y el handoff de redacción exige un resumen de esa consulta. No define cómo registrar y comprobar R1–R5 cuando el diálogo ya resolvió las decisiones y no hay motivo para consultar.

El resultado práctico es una bifurcación sin procedimiento: forzar una consulta innecesaria o pasar a redacción sin la comprobación de readiness comprometida. Esto afecta especialmente a la feature trivial del ciclo normal.

**Cierre verificable:** definir explícitamente la ruta sin consulta, manteniendo el diálogo atribuido, R1–R5 y el mismo handoff de decisiones; conservar la consulta condicionada y la ruta de revisión/exención.

### 4. La orientación de cierre vuelve incorrecta la inferencia cuando no existe state

**Required · Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-cycle/references/state-detection.md:57–72`.  
**Contrato:** PC-7, `spec.md:99–105`.

El cambio de la fila «Memory Bank updated, feature merged» a `idle` está dentro del **paso 2: si no hay archivo de estado**, pero ahora presenta además `current_stage: idle` y `active_feature: null` como si un cierre hubiera dejado esos valores. En esa ruta no hay state del que verificar tales valores ni transición registrada que los haya escrito. Un consumidor puede confundir una inferencia documental de que una feature terminó con un reposo operativo legítimo y orientar la apertura sin establecer las precondiciones reales.

La corrección de la guía hacia `idle/null` era relevante para PC-7; el problema es aplicar una afirmación de estado persistido a la ruta que explícitamente carece de ese archivo.

**Cierre verificable:** distinguir en esa fila la inferencia sobre el trabajo terminado del estado operativo verificado; conservar `idle/null` como resultado de la transición legítima, sin afirmar que existe cuando falta el state.

## Evidencia pendiente y límites por promesa

Las categorías siguientes se aplican al **candidato actual**, no constituyen aceptación final:

| Promesa | Categoría | Alcance observado |
|---|---|---|
| PC-1–3 | **Failed** | Hallazgos 1–3. La fidelidad observada de PC-11 todavía falta. |
| PC-4 | **Missing** | La ruta supervisada aparece en las instrucciones, pero faltan las observaciones de ruta revisada, exenta y exenciones incompletas previstas para T3. No se exige ni se infiere enforcement automático del CLI. |
| PC-5 | **Supported within declared limits** | Tests focales y controles de materialización/roles pasan; esto verifica transporte, no calidad semántica de la consulta. |
| PC-6 | **Missing** | Los tests de congelamiento pasan, pero la evidencia examinada no registra individualmente los paquetes en vuelo afectados ni acredita aún las publicaciones candidatas necesarias para T3. A2/B1 mutan `common.md`, no las fuentes concretas de architect modificadas; son soporte mecánico útil, no prueba de activación efectiva de esos bytes. |
| PC-7 | **Failed** | El recorrido ejecutable focal pasa; persiste el hallazgo 4 en la guía contextual. |
| PC-8–10 | **Failed / Missing** | Las instrucciones de las rutas efectivas tienen los hallazgos anteriores; falta además evidencia de versiones efectivamente consumidas en T3. Las comprobaciones mecánicas no prueban comprensión. |
| PC-11 | **Missing** | No se observaron J1–J7 ni C1–C5. No se han fabricado resultados; la selección del runtime candidato sin instalación sigue pendiente según el plan. |

## Alcance, separación y comprobaciones

- **Tests primero:** revisé los tests nuevos y la modificación de la expectativa antigua. Los commits `91835a6b` y `215b0b52` contienen únicamente archivos bajo `tests/`; el cambio de expectativa elimina solo `architect/brainstorm`, con motivo registrado. Los commits de implementación `3322aaf3` y `c11825b4` no modifican tests.
- **Inventario:** ejecuté `python3 scripts/cdad-suite.py validate`: salida `status: ok`, 250 módulos inventariados y 2074 nodeids recogidos. La salida conserva sus propios avisos de placeholders y timing pendiente; no los interpreto como una ejecución de la suite.
- **Regresión independiente:** ejecuté:

  ```text
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:tests python3 -m pytest -q -p no:cacheprovider \
    tests/test_019_002_discovery_delivery.py \
    tests/test_019_002_resting_orientation.py \
    tests/test_006_005_u7_scribe_role_report.py \
    tests/test_005_007_t4_architect_report_materialization.py \
    tests/test_015_001_frozen_reception.py \
    tests/test_006_006_u3_review_route_and_gate.py \
    tests/test_006_006_u5_exemption_record.py \
    tests/test_cdad_generate.py \
    tests/test_role_packet_render.py \
    tests/test_role_packet_consumers.py
  ```

  Resultado: **86 passed in 231.17s**. No ejecuté la suite completa ni repetí toda la selección T2 del informe de implementación.
- **`state-detection.md` fuera de la lista literal T2:** su reconciliación era materialmente pertinente para PC-7 y el paquete T2 autorizaba la raíz `skills`; no observo una violación del alcance de escritura del paquete por ese archivo. La redacción concreta introduce, no obstante, el hallazgo 4.
- **`skills/cdad-cycle/SKILL.md:69`:** conserva «Socratic brainstorm». Es un consumidor legacy obsoleto, pero esa frase aislada no demuestra por sí sola una instrucción de entrevistar directamente al dueño; no la elevo por separado. Conviene reconciliarla junto con las rutas del hallazgo 1, mediante el alcance que corresponda.
- **Tabla de decisiones:** los 32 ADR indexados existen. Los ADR sin fila están marcados `Proposed` en los archivos examinados; no identifico una fila rota ni una contradicción demostrada con los ADR que gobiernan esta revisión.
- **Archivos modificados por esta revisión:** ninguno. **Commit:** ninguno. `git status --short` seguía mostrando únicamente `docs/.cdad-state.json` modificado, preexistente y fuera del producto revisado.
- **Intake:** ruta C validada con `validate-request` y `validate-packet`; ambos terminaron con rc 0 y la identificación renderizada coincidió con la recibida.

## Abstentions

- No puedo acreditar la fidelidad de una ejecución real ni las rutas PC-4/PC-11 antes de los transcripts, versiones efectivas y artefactos de T3.
- No verifiqué la autoría de familia de modelo del implementador ni una instalación o distribución desplegada; esta revisión no afirma compatibilidad instalada.
- No repetí `make validate` ni investigué su fallo `F011`; el informe de implementación lo declara también presente sin sus cambios, pero no lo doy por verificado independientemente.