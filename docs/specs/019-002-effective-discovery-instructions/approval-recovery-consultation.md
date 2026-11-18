## Dictamen — propuesta de recuperación, no aprobación

**Procede una corrección administrativa explícita, seguida de reaprobación y nuevos pins. No procede borrar la aprobación histórica, editar paquetes publicados ni reiniciar automáticamente el trabajo realizado.**

### Lo comprobado

- La recepción **Route C es válida**: contexto v2, identificación coincidente y `PACKET.md` idéntico al render canónico completo: **7.097 bytes**. El hash del contrato coincide.
- La transición `6ed1e2ef…` registra aprobación atribuida al orquestador delegado y fija los hashes actuales de spec y plan. Ambos archivos todavía dicen `UNAPPROVED DRAFT`. **Los pins no han sufrido deriva**; el defecto es documental y de procedencia, no ausencia demostrada de intención de aprobar (`docs/.cdad-state.json:42089`; `t3-progress.md:18–25`).
- Existe mandato expreso para aprobar especificaciones dentro del epic, sin autorizar publicación ni despliegue (`docs/epics/epic-019-discovery-dialogue/execution.md:3–14`).
- La metodología exige tanto la marca de aprobación delegada como los campos separados `approved_by`, `delegated: true` y `requested_by` (`stage-2-specification.md:131–149`). Lo mismo aparece en la revisión de repositorio identificada por el manifiesto de instalación.
- La continuidad tiene cabeza **seq 69**, con spec y plan como referencias `contract`, actualmente sin cambios.

## Secuencia segura propuesta

1. **Recibir y cerrar normalmente esta consulta antes de cambiar los contratos.**  
   Conservar su paquete, resultado, recibo y cadena de continuidad. No retirar un encargo ya ejecutado como si nunca se hubiera despachado.

2. **Registrar una decisión de recuperación acotada.**  
   Debe identificar la transición anterior, sus hashes, el mandato delegado y los dos defectos. Declarar expresamente:
   - corrección de procedencia y estado textual;
   - ninguna modificación de promesas, aceptación, alcance o tareas;
   - ninguna exención de revisión;
   - ninguna acreditación retroactiva de evidencia faltante.

3. **Obtener revisión independiente focalizada de esa recuperación.**  
   Contrastar spec/plan con el borrador revisado y comprobar que la corrección propuesta sólo afecta la aprobación documental. Mi comparación encontró que sus cuerpos corresponden a las secciones de `architect-draft-006.md`, excluyendo separadores y saltos finales de extracción.

   **No hace falta repetir íntegramente el diseño.** Si aparece cualquier cambio sustantivo, vuelve al architect y después a revisión: ya no sería una corrección puramente administrativa. La re-review es obligatoria cuando cambia el diseño (`re-entry.md:278–289`).

4. **El aprobador delegado realiza nuevamente la autoevaluación y marca ambos documentos.**  
   Usar su identidad real y fecha actual, indicando la delegación de Pablo y enlazando la recuperación. **No antedatar ni presentar la nueva marca como una aprobación directa de Pablo.** La marca de aprobación corresponde al aprobador, no al implementer.

5. **Registrar un nuevo gate sobre los bytes finales.**  
   Fijar nuevamente **spec y plan**, después de incorporar sus marcas. Preservar la entrada histórica.

   Forma propuesta, **no ejecutada**:

   ```sh
   python3 "<skill-dir>/scripts/cdad_packet.py" register-transition \
     --project-root ROOT \
     --transition gate \
     --stage specification \
     --feature 019-002-effective-discovery-instructions \
     --approve-by "<identidad del aprobador delegado>" \
     --contract-path docs/specs/019-002-effective-discovery-instructions/spec.md \
     --plan-path docs/specs/019-002-effective-discovery-instructions/plan.md \
     --delegated \
     --requested-by Pablo \
     --supersedes 6ed1e2ef60fe84754156a0a81506f8e170f8cf130b72364ad2acbc94a75f5573 \
     --artifact "<decisión de recuperación>" \
     --artifact "<revisión focalizada>" \
     --note "Corrección de procedencia y reaprobación; revisión ejecutada, no eximida."
   ```

   El CLI permite citar mediante `--supersedes` la aprobación previa del mismo contrato. **Con bytes modificados no lo exige**, pero propongo incluirlo para dejar explícita la sustitución; nunca reescribir la entrada anterior (`cdad_packet.py:9087–9127`).

   **Omitir `--current-stage` y `--substage`** evita retroceder artificialmente desde `review` o alterar el progreso TDD.

6. **Anexar un checkpoint de continuidad con los nuevos contratos.**  
   Registrar motivo, aprobación nueva, antecedente y alcance de reutilización de evidencia; conservar las referencias como `contract`. No editar cuerpos históricos, degradarlas a `living` ni hacer un `reanchor` para ocultar el cambio.

   Es necesario actualizar esta continuidad antes del siguiente transporte: con los archivos modificados y la cabeza antigua, `resume/reconcile` detectarán deriva. El escritor existente permite anexar un checkpoint enlazado con referencias actualizadas (`continuity.md:51–74,115–117`; `cdad_continuity.py:1052–1162`).

7. **Validar el estado resultante y continuar mediante publicaciones nuevas.**  
   Comprobar hashes finales, aprobación vigente, procedencia delegada, continuidad recuperable y conservación del historial. Los paquetes de construcción que fijaron los bytes anteriores permanecen históricos; no se “actualizan” manualmente.

## Delegación no significa exención

Utilizar **únicamente** `--delegated --requested-by Pablo`, sin `--exempted-by` ni `--exemption-reason`.

Aunque el CLI agrupa esos campos bajo una clave de identidad llamada `exemption`, el contrato aprobado **declara expresamente que también sirven para producir la procedencia de aprobación delegada** (`docs/specs/006-006-spec-plan-review/spec.md:168`). La entrada los escribe planos y sólo añade los campos declarados (`cdad_packet.py:8990–9003,9147–9162`).

Por ello, **la presencia de ese bloque técnico no acredita una exención**. La decisión y la revisión citadas deben dejar inequívoco que la revisión se realizó y no fue dispensada.

## Consecuencias para lo ya ejecutado

- Una corrección limitada a aprobación/procedencia **no obliga por sí sola a repetir RED/GREEN ni toda la implementación**. La reutilización exige declarar que las obligaciones sustantivas permanecen iguales.
- La aprobación nueva **no demuestra que el proceso histórico fuera impecable** ni subsana retrospectivamente otros incumplimientos.
- El redo por escritura fuera de scope mantiene su evaluación independiente; no queda legitimado por esta reaprobación.
- PC-4, PC-11 y las demás evidencias pendientes siguen abiertas. Esta recuperación no acepta la feature ni autoriza instalación.

## Evidencia y límites

Comandos principales ejecutados:

```text
python3 scripts/cdad_packet.py validate-request --request <REQUEST.json>
python3 scripts/cdad_packet.py validate-packet --request <REQUEST.json> --packet <PACKET.md>
python3 scripts/cdad_packet.py render --request <REQUEST.json> --route C
```

Los dos validadores terminaron sin diagnóstico; comparación completa del render: `True`.

```text
sha256sum .../spec.md .../plan.md
```

Resultado: coinciden con los pins históricos `5cca6fa6…` y `bce266fd…`.

```text
python3 scripts/cdad_continuity.py resume --project-root <repo> \
  --execution-context .cdad/executions/exec-019-002-effective-discovery-instructions-001/execution.json --json
```

Resultado: seq 69, autoridad activa, cuatro referencias contractuales `unchanged`.

**Límite de instalación:** consulté el manifiesto del proyecto y la revisión de repositorio que identifica (`1dc2e382…`), no los archivos externos de la instalación viva: el scope concedido es `repository-read`. El orquestador debe confirmar sus bytes efectivos antes de ejecutar la recuperación.

**Archivos modificados por mí:** ninguno. **Commit creado:** ninguno. HEAD examinado: `db00c022e5e053eabc63319d42fbffb4de40b965`. Al inicio y al final sólo constaba la modificación preexistente de `docs/.cdad-state.json`.