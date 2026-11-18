# Revisión del borrador de acceso a referencias

**Objeto revisado:** `docs/specs/019-003-contract-verification-strategy/reference-access-amendment-draft.md`  
**SHA-256 del contrato:** `bb3ccda5b3332d76fa7676097dbde0cac57acf6fba3f6dac4d47226d8f6b0aad`

## Hallazgos

### 1. La autoridad de la representación propuesta no está establecida

**Required — Verdict: BLOCKING · Bucket: h**

El borrador propone que una copia protegida dentro del proyecto satisfaga una obligación de leer una **instrucción normativa** (`reference-access-amendment-draft.md:29–36, 46–58, 76–80`). Sin embargo, la norma citada como fundamento (`documentary-contracts.md:38–59`) exige que una *fuente de respaldo* sea recuperable dentro del alcance; también dice expresamente que no concede acceso adicional. No establece que una copia de una referencia se convierta en la autoridad aplicable a un rol.

La distinción importa en self-host: el archivo de `skills/` puede ser el **producto candidato**, mientras que la instalación efectiva puede contener la metodología vigente. El borrador reconoce que no inspeccionó esa instalación (`:25, 105`) y no fija cómo se selecciona una versión normativa cuando ambas difieren. Un hash comprueba que se recibió la copia elegida, pero no demuestra que esa copia sea la instrucción autorizada ni que no contenga cambios candidatos o maliciosos.

**Consecuencia:** el test-writer podría recibir como regla vigente una representación fielmente hasheada de la versión equivocada y producir un AUDIT bajo una autoridad no acreditada.

**Cierre verificable:** obtener una decisión explícita del dueño sobre la autoridad y procedencia admitidas; identificar y contrastar la fuente efectiva, revisión y bytes antes de fijar la copia; definir qué ocurre si instalación, fuente aprobada y candidato divergen. Si se mantiene la representación, distinguirla expresamente como snapshot autorizado, no atribuir esa autorización al pasaje documental citado. Evaluar también la alternativa de separar la autoridad de instrucciones instaladas del `read_scope` de producto; su viabilidad y posibles cambios de renderer o guard deben demostrarse, no presuponerse.

La encomienda informa que el dueño y el orquestador rechazaron antes copiar un archivo para eludir la restricción. No dispongo aquí del texto recuperable de esa decisión: **no puedo concluir que este snapshot sea exactamente la opción rechazada**, pero tampoco que la aprobación de una enmienda quede implícita.

### 2. La secuencia de desbloqueo deja sin resolver cómo se verifica el primer cambio

**Required — Verdict: BLOCKING · Bucket: h**

El AUDIT está bloqueado porque la instrucción vigente exige una lectura fuera del alcance (`test-audit-partial-002.md:3–5`; `packets/roles/test-writer.md:2`). La secuencia propone producir y revisar primero una aclaración de instrucciones y después publicar el sucesor con el que completar el AUDIT (`reference-access-amendment-draft.md:102–109`).

No identifica qué contrato, asignación y estrategia de verificación autorizan **esa aclaración previa**, ni cómo se determina independientemente si modifica solo semántica o también comportamiento ejecutable. El plan aprobado, por su parte, hace preceder la producción por el enrutamiento de la verificación aplicable (`plan-draft.md:21–25`), y la especificación distingue el tratamiento de cambios ejecutables, semánticos y mixtos (`spec.md:42–56`).

**Consecuencia:** la ruta puede avanzar hacia la modificación de las instrucciones que gobiernan el AUDIT sin haber resuelto el gate que decide cómo verificar esa modificación.

**Cierre verificable:** especificar un primer encargo acotado, su contrato protegido, responsables independientes, inputs autorizados, clasificación de cambios y gate anterior a producción. Si se demuestra necesario cambiar comportamiento ejecutable, volver con una promesa observable y aplicar el RED/GREEN independiente correspondiente; si es puramente semántico, justificar esa clasificación y su revisión contextual sin fabricar un RED.

### 3. Los casos de aceptación no identifican una comprobación operativa suficiente

**Required — Verdict: BLOCKING · Bucket: h**

PC-8 promete que el destinatario comprobará el hash y se detendrá ante ausencia o divergencia (`reference-access-amendment-draft.md:60–67`). La aceptación exige observar esos resultados tanto en self-host como en un consumidor ordinario (`:84–93`), pero solo invoca «controles existentes» sin identificar cuáles ejercen al destinatario real, cómo se provoca cada caso, ni cómo se observa que no hubo lectura alternativa. El propio borrador reconoce que una simulación de clasificación no demuestra integración real (`:25, 93`).

La validación de un scope o del paquete no demuestra por sí sola que el rol compruebe el archivo después de la admisión; el borrador también reconoce que el renderer no garantiza ese hash (`:80`). Queda además sin definir la conducta si el contenido cambia entre la comprobación y su uso.

**Consecuencia:** podría acreditarse la promesa con un paquete estructuralmente válido aunque el destinatario continúe con una referencia ausente, divergente o sustituida.

**Cierre verificable:** definir para ambos entornos el consumidor efectivo, preparación de los casos correcto/ausente/divergente, observables de continuación y detención, evidencia de la ruta y bytes usados, y tratamiento de cambio entre comprobación y uso. Identificar los controles existentes que realmente establecen cada resultado o declarar el mecanismo y verificación adicional necesarios. Mantener explícito que una observación acotada no prueba cumplimiento universal ni aislamiento de sandbox.

## Alcance y evidencia de esta revisión

- Revisé primero el AUDIT parcial y después el borrador, la especificación aprobada, el plan y las fuentes contractuales pertinentes. Contrasté la tabla de decisiones vigentes con los ADR relevantes, incluidos ADR-011 y ADR-040.
- La validación de la ruta C se realizó con `cdad_packet.py validate-request`, `validate-packet` y `render --route C`; los dos validadores terminaron sin salida ni error y la identificación renderizada coincidió con la recibida.
- No ejecuté tests, ni reproduje una sesión real de consumidor o self-host. Las pruebas enumeradas en el AUDIT son selecciones provisionales, no evidencia verde.
- No modifiqué archivos ni hice commit. `git status --short` mostró `M docs/.cdad-state.json`; no atribuyo ese cambio a esta revisión.

## Abstentions

- No puedo determinar, sin la decisión previa recuperable del dueño y del orquestador, si la copia propuesta contradice exactamente el rechazo anterior.
- No puedo determinar qué bytes de la instalación efectiva serían la autoridad aplicable: no se aportó una identificación y contraste verificables de esa instalación.
- No concluyo que necesariamente deba cambiarse el renderer o el guard; tampoco está demostrada la afirmación contraria del borrador.

**Dictamen:** el borrador tiene **tres hallazgos bloqueantes**. Esta revisión no lo aprueba; corresponde al dueño decidir su tratamiento.