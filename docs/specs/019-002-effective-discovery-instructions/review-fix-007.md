Apliqué las correcciones de F1 a F8 y F11 en las fuentes canónicas, regeneré los agentes con `make agents` y lo dejé en el commit `abb83c85`. Las 62 pruebas de los siete archivos indicados pasan (62 passed en 164 s). No edité ningún test.

**Validación del paquete (ruta C):** `validate-request` y `validate-packet` dieron rc=0. El render completo es idéntico byte a byte a `PACKET.md`, y la identificación de ruta C coincide con la del prompt.

**Dónde quedó cada corrección:**
- **F1:** `sources/roles/orchestrator.md`. El orquestador no lee código ni ejecuta el producto para resolver afirmaciones sobre comportamiento existente, incluidas las del dueño; esas van a una consulta dirigida al arquitecto. Las partes técnicas de los documentos de arranque salen del informe del arquitecto.
- **F8:** `sources/roles/orchestrator.md`. Se materializa el TEXTO FINAL del revisor y del arquitecto tal cual; cualquier resumen va en una nota aparte con etiqueta. La misma regla de "tal cual" está en el punto del veredicto de `stage-2-specification.md`.
- **F2:** `stage-2-specification.md` §2.1. `discovery.md` con su sección de contexto del diálogo debe existir antes de cualquier despacho al arquitecto o borrador de spec. Cada mensaje del dueño se registra con su identificador. `stage-1-discovery.md` apunta a esa regla.
- **F11:** `stage-2-specification.md` §2.1. Se pregunta una decisión a la vez, con la referencia que la justifica.
- **F5:** `stage-2-specification.md`, convención de registro. Una corrección que nombra una declaración sin entrada equivalente se registra como declaraciones en conflicto. Se le pregunta al dueño cuál reemplaza y nunca se reemplaza por inferencia.
- **F7:** `stage-2-specification.md`, re-entrada. Despachar la redacción de la spec exige un resultado de preparación registrado. Ese resultado requiere la ruta de consulta o un R4 "sin consulta" registrado.
- **F8 (despacho nativo):** `stage-2-specification.md`, paquete del revisor. En despacho nativo se pega el contexto completo del diálogo en el prompt.
- **F3:** `re-entry.md`, R1. Una postergación es un ítem sin resolver, no una exclusión. Un "adelante" condicional cuenta solo si R1 a R5 pasan en ese momento, registrado.
- **F6:** `re-entry.md`, R4. Una suposición del dueño sobre comportamiento existente es incertidumbre técnica y va al arquitecto. Una contradicción verificada se registra como evidencia técnica y se refleja en el borrador o como límite o bloqueo explícito.
- **F4:** el control del borrador de spec en `re-entry.md`, el paquete de redacción en `handoff-prompts.md` y `skills/cdad-cycle/packets/substages/reviewer-plan-review.md`. Cada postcondición numerada y criterio de aceptación debe rastrearse a una decisión vigente. Lo no resuelto, las propuestas y los valores por defecto no aceptados aparecen solo como supuestos abiertos con etiqueta, nunca en el Contrato ni en los criterios.

`agents/cdad-orchestrator.md` y `agents/claude-code/cdad-orchestrator.md` son salida regenerada; no los toqué a mano. `docs/.cdad-state.json` ya figuraba modificado antes de mi trabajo, así que no lo incluí en el commit.

No ejecuté la suite completa; los gates focales y proporcionales (siete archivos) quedaron en verde.