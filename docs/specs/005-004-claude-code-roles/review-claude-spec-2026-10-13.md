# Revisión del orquestador Claude — spec y plan de 005-004 (2026-10-13)

Revisión entre la etapa 2 y la etapa 3, con el criterio vigente del 2026-10-12: se bloquea lo que
compromete el resultado, la evidencia o el uso previsto; el resto va a deuda.

## Lo que está bien

- **Recorrido y alcance.** El alcance sigue la fila 10. D-i..D-iv están resueltas y los VERIFY se
  conservan con su causa.
- **Transiciones.** PD-10 decide de forma explícita que el registro automático de transiciones no
  entra, y lo fundamenta.
- **Diagnóstico.** Las dos incoherencias del adaptador (`Task` contra `Agent`, y la afirmación de
  que el instalador quita el modelo) están bien diagnosticadas y se corrigen sin tocar el
  instalador.
- **Pata CC.** Es aditiva y no altera los veredictos existentes.
- **Plan.** El bloque `plan-tasks` es válido: lo comprobé con `_plan_tasks_from_contract`,
  `_check_plan_tasks` y `_check_plan_validation_plan`.

## Hallazgos y disposición

1. **Bloqueante, corregido en la spec y el plan.** T5 nombraba como responsable a «orchestrator» sin
   decir cuál. Solo una sesión de Claude Code invoca subagentes nativos, así que el orquestador
   OpenCode no puede coordinar el recorrido. Ahora lo coordina el orquestador Claude (PD-6, T5).
2. **Bloqueante, corregido.** PD-6 exigía el veredicto de versión con la pata CC usando la versión
   instalada al empezar, y esa versión no la tiene, porque T1–T4 no estarán desplegados. Se separa
   en dos pasos:
   - **paso a (gate):** la instalación al empezar, más la pata CC desde el artefacto del repo en el
     commit de cierre, declarada así;
   - **paso b:** una confirmación con el CLI instalado después del despliegue que decida el dueño.
     No es gate.
3. **No bloqueante, ajustado por tamaño de unidad.** El focal de T4 repetía decisiones del guard
   que ya cubren `tests/test_004_002_t5_runtime.py` (`pd8_i10_c2_*`) y
   `tests/test_005_008_t1_nested_tests.py`. Ahora solo agrega lo no cubierto:
   - el rol desconocido con fail-open;
   - los roles sin hooks;
   - la coincidencia del frontmatter de hooks generado con `CC_GUARDS`.

   La cobertura existente queda como regresión.
4. **Documental, corregido.** La deuda D-2 y PD-10 apuntaban a «Entrada y transiciones»
   (`execution.md`); ahora apuntan a 005-012, la fila 12 del plan del epic.
5. **Observación, sin bloqueo.** `claude-code-delegation.md` ya afirma que Claude Code respeta el
   `exit 2`, verificado de forma empírica en `validation-cdad-002.md`. T4 debe conciliar esa
   afirmación con el VERIFY 1 de PD-8: conservarla con su alcance (sesión interactiva) o
   declararla no verificada en modo no interactivo. No debe quedar contradicción.
6. **Proceso.** Las entradas del state que registró el orquestador siguen llevando ids crudos de
   sesión. El state está versionado. Lo cubre el gate de saneamiento del epic (`execution.md`),
   y los encargos siguientes deben extender la regla a las notas del state.

## Aprobación

La spec y el plan corregidos se vuelven a aprobar con sus nuevos sha256, registrados en
`docs/.cdad-state.json` (`stage_history`, `stage: specification`). Sigue la etapa 3:
- T1–T4 los orquesta el orquestador OpenCode;
- T5 lo coordina el orquestador Claude.

## Segunda enmienda (2026-10-13, después de T4)

El dueño cuestionó la primera corrección. Si el coordinador de T5 es el orquestador Claude, que ya
conoce el recorrido, la aceptación prueba que las piezas encajan, pero no el uso previsto. T5 pasa a
coordinarlo una sesión nueva de Claude Code con una instrucción breve; el orquestador Claude la
lanza, mide su transcript y revisa. El adaptador `cdad_delegate` → Claude Code queda como mejora
futura, por decisión del dueño (`execution.md`).

Verificación de T1–T4 por el orquestador Claude:
- **Focales:** 29 passed.
- **Diff:** el diff de producto se acota a los archivos declarados.
- **Árbol:** sin stash pendiente y limpio.
- **Observación, sin bloqueo:** en la instalación global, la pata CC lee el mismo `version.txt` de
  la raíz que las patas de OpenCode, porque `install.sh` instala los dos runtimes juntos. Por eso
  no detecta que los agentes CC tengan otra versión dentro de una misma raíz. Para eso haría falta
  comparar con el manifiesto de propiedad. Queda como deuda.
- **Proceso:** dos usos de `git stash` sobre el árbol compartido. Se restauraron, sin efecto
  material; es reincidencia de proceso.
