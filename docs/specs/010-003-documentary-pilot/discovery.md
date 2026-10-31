# Discovery — 010-003-documentary-pilot

**Resultado:** el piloto puede apoyarse en el mecanismo existente. Recomiendo añadir fuentes sintéticas, controles acotados, un entregable Markdown y evidencia de sesiones reales; **no encuentro necesidad de modificar la toolchain ni crear roles, selectores o campos**.

Es una propuesta para decisión, no una spec ni una aprobación.

## 1. Landscape verificado

| Ya disponible | Evidencia y límite |
|---|---|
| Norma documental: evidencia, propuesta, contradicción y pendiente; fuentes recuperables; separación de producto y oráculo | `skills/cdad-cycle/references/documentary-contracts.md:9-119`. |
| Producción documental por el implementer, verificación por test-writer y revisión independiente read-only | Misma referencia, `121-149`. El scribe conserva Memory Bank. |
| Procedimiento de encargo mediante campos existentes | `skills/cdad-cycle/references/handoff-prompts.md:120-165`. Exige alcance editable explícito y detener superposiciones. |
| Admisión técnica de escritura documental | `skills/cdad-cycle/scripts/cdad_packet.py:1419-1474`. El implementer admite scopes `docs`; su default sigue siendo implementación, sin documentación: `2314-2324`. |
| Evidencia estructural y revisión semántica como registros distintos | `skills/cdad-cycle/references/documentary-contracts.md:151-176`. |
| Recepción durable, sin aprobación semántica automática | `skills/cdad-cycle/scripts/cdad_result.py:725-751`: el recibo conserva `semantic_status: pending`. |

**Qué entregó 010-001:** criterios compartidos, obligaciones de rol y distribución de esas obligaciones. Excluyó expresamente el validador universal y la ejecución/acreditación del piloto: `docs/specs/010-001-documentary-contracts/spec.md:118-178,205-225`.

**Qué agregó 010-002:** procedimiento operativo, aplicabilidad Odoo, coherencia del destinatario e integración distribuible. Su cierre acredita esas piezas y declara que sus pruebas **no acreditan fidelidad documental ni conducta efectiva de modelos**: `docs/specs/010-002-documentary-role-integration/closure.md:66-112,155-168`.

**Qué falta:** ejecutar y conservar evidencia del piloto comprometido: detección estructural, los tres hallazgos semánticos, corrección trazable y aceptación funcional. Son obligaciones de `docs/epics/epic-010-documentary-specialization/plan.md:79-88`. No encontré archivos bajo `docs/specs/010-003-documentary-pilot/` en este relevamiento.

## 2. Corpus sintético y defectos conocidos

### Propuesta

Preparar insumos pequeños, exclusivamente sintéticos y textuales, con:

- Inventario cerrado de fuentes y versiones recuperables.
- Posiciones incompatibles conservadas como tales.
- Un borrador deliberadamente defectuoso, identificado como **muestra de evaluación no aceptada**.
- Una clave de contraste protegida, separada de los insumos del reviewer.

Ejemplos ilustrativos, **no hechos del repositorio ni contenido ya aprobado**:

| Defecto sembrado | Construcción propuesta | Evidencia esperada del reviewer |
|---|---|---|
| Afirmación sin respaldo | El borrador asegura que existe una notificación automática; ninguna fuente autorizada la acredita. | Ubicación de la afirmación, corpus examinado y ausencia de respaldo **en ese corpus**, sin afirmar falsedad universal. |
| Contradicción omitida | Dos fuentes atribuyen la aprobación a responsables incompatibles; el borrador presenta una sola posición como consenso. | Ambas posiciones y sus localizadores; ubicación de la omisión; ausencia de decisión acreditada que resuelva el conflicto. |
| Referencia existente pero insuficiente | Una afirmación sobre conservación de registros cita un fragmento que únicamente describe la recepción de solicitudes. | Afirmación, referencia resoluble, contenido real del fragmento y explicación de por qué no sostiene la conclusión. |

La clave debe fijarse antes de revisar. No debe reconstruirse después para hacer coincidir los hallazgos.

**Frontera de autoría:** los fixtures y verificadores pueden prepararse como insumos de aceptación bajo `tests/`, por el test-writer, desde el contrato aprobado; el documento funcional corresponde al implementer en su directorio documental autorizado. El test-writer no debe derivar su oráculo del documento producido: `sources/roles/test-writer.md:18-35`.

## 3. Control automático y límite semántico

**Hoy:** el validador consolidado dispone de comprobaciones de existencia, expresiones regulares, igualdad de archivos y resultado de comandos: `tests/validate-consistency.sh:26-77`. No encontré allí un control específico del piloto.

**Propuesta mínima:** un verificador bajo `tests/`, limitado a la convención documental que se apruebe para este caso. Por ejemplo, comprobar que un localizador citado corresponde a un fragmento existente de la fuente inventariada.

La demostración debe incluir:

1. Una muestra con un localizador roto y diagnóstico observable.
2. Una muestra equivalente con ese defecto corregido, aceptada por el control.
3. Una muestra estructuralmente válida que conserve los defectos semánticos.

Así queda demostrado **qué detecta y qué deja pasar**. No bastaría un test que encuentre la palabra «FAIL» en un informe.

La existencia del fragmento no demuestra que respalde la afirmación. Tampoco un patrón de texto puede acreditar por sí solo que se conservaron todas las posiciones relevantes. Esa separación ya es normativa: `skills/cdad-cycle/references/documentary-contracts.md:153-171`.

## 4. Acreditación de la revisión independiente

### Propuesta

Realizar una revisión real en sesión independiente del productor, con contrato, borrador defectuoso y fuentes autorizadas, **sin la clave de contraste ni el entregable corregido antes de cerrar su primer informe**.

Conservar:

- Request y paquete validados; identificación de la sesión y evidencia recuperable del despacho.
- Snapshot exacto del borrador y de las fuentes examinadas.
- Informe original del reviewer con cada hallazgo localizado y fundamentado.
- Alcance examinado y sección de abstenciones.
- Contraste posterior, por el orquestador, entre informe cerrado y clave protegida.

El reviewer ya tiene obligación de independencia, evidencia y abstenciones: `sources/roles/reviewer.md:21-43,58-85`.

**Abstenciones necesarias:** no inferir funcionamiento de un sistema real, no extender conclusiones fuera del corpus, no prometer exhaustividad ni aprobar funcionalmente el resultado.

Si falta uno de los tres hallazgos, **esa detección no queda acreditada**. Una revisión posterior que ya conozca la clave puede verificar una corrección, pero no reemplaza retrospectivamente el primer ensayo independiente.

La exclusión de la clave es contractual y de alcance; no debe presentarse como aislamiento técnico infalible.

## 5. Entregable corregido, trazabilidad y pendientes

El implementer produciría el documento corregido en un directorio propio, separado de fuentes, contrato y verificadores.

La revisión de cierre debería contrastar:

- Cada afirmación factual conservada con su fuente y versión.
- La corrección correspondiente a cada defecto conocido.
- La preservación de ambas posiciones cuando no existe decisión que resuelva la contradicción.
- Las propuestas como propuestas.
- Los pendientes con información faltante, ubicación, condición de cierre, responsable conocido o designación pendiente y clasificación justificada.

Una contradicción abierta puede ser admisible **si se promete documentar la divergencia**, no si se promete definir un proceso operativo inequívoco: `skills/cdad-cycle/references/documentary-contracts.md:61-87`.

La comparación de versiones y el diff permiten observar cambios persistentes y conservar procedencia; **no prueban ausencia de escrituras transitorias**. La aceptación sigue perteneciendo a la autoridad habilitada y no se solicita con bloqueantes abiertos: misma referencia, `160-176`.

## 6. Tests de repositorio frente a sesiones reales

| Puede acreditar un test | Exige ejecución real del rol |
|---|---|
| El control detecta el defecto estructural elegido. | Que el reviewer encontró y fundamentó los tres defectos semánticos. |
| Los localizadores cumplen la convención acotada. | Que contrastó realmente las afirmaciones con las fuentes declaradas. |
| Se mantienen los bytes protegidos en los estados observados. | Que produjo un informe independiente con límites y abstenciones. |
| Los paquetes transportan alcances y declaraciones correctas. | Que el productor entregó la corrección y esta fue revisada. |

Las pruebas existentes de 010-001 verifican conceptos normativos, no revisión efectiva: `tests/test_010_001_documentary_contracts.py:970-1019`. Las de 010-002 comprueban scopes publicados, no conducta del agente: `tests/test_010_002_documentary_role_integration.py:1442-1537`.

Un informe simulado puede probar transporte o materialización, **nunca sustituir el informe de la sesión real**.

## 7. Alternativas y propuesta mínima

### Decisiones recomendadas

- **Verificador universal vs. control específico:** control específico del piloto. Cumple la promesa sin introducir un parser general no necesario.
- **Esperar errores espontáneos vs. desafío sembrado:** desafío protegido con defectos conocidos. Permite una evaluación reproducible sin garantizar que un productor cometerá esos errores.
- **Forzar un GREEN defectuoso vs. separar desafío y producto:** separar ambos. No hace falta fabricar una entrega presentada como correcta para demostrar detección.

### Recorrido mínimo propuesto

1. Aprobar el encargo, las fronteras y el criterio de aceptación.
2. AUDIT/POST-AUDIT/RED: preparar verificadores y fixtures protegidos; demostrar RED por la obligación documental ausente y el control estructural negativo.
3. GREEN: producir el entregable corregido, sin editar fuentes ni oráculos.
4. Review: primero cerrar el ensayo semántico sobre el borrador defectuoso, sin clave ni corrección; después revisar el producto corregido mediante otro encargo delimitado de la misma subfase.
5. Corregir hallazgos reales pendientes y re-verificarlos.
6. Cerrar con evidencia estructural, semántica y aceptación separadas; el scribe mantiene su función.

**Límite de esta alternativa:** acredita detección sobre una muestra sembrada y revisión del producto corregido. No acredita que los defectos hayan surgido espontáneamente del implementer.

## 8. Riesgos y preguntas para decidir

- **¿Se acepta el desafío protegido separado del producto corregido?** Es mi recomendación. Si se exige revisar un primer producto editable con defectos sembrados, debe autorizarse expresamente como candidato negativo, sin declararlo conforme.
- **¿El resultado promete documentar divergencias o resolverlas?** Recomiendo documentarlas; resolverlas sin una decisión adicional inventaría consenso.
- **¿Se fija primero el informe del desafío antes de mostrar la corrección?** Recomiendo que sí, para evitar que la corrección revele las respuestas.

Riesgos operativos existentes:

- I-8: acceso del test-writer a sus instrucciones; una denegación exige detenerse y escalar, no rodearla.
- I-9/I-10: copia del CLI y deriva de fuentes de paquetes; usar la toolchain del proyecto y evitar modificar bloques de instrucciones en este piloto.
- I-11/I-12: no ampliar controles dependientes de números de línea o rewrap.
- I-13: comprobar el tipo de artefacto antes de recibirlo; para reviewer/review existe `review`, no hace falta inventar otro.
- Instalación global desactualizada: no atribuirle las obligaciones acreditadas en el repositorio.

Fuentes: `docs/epics/epic-010-documentary-specialization/backlog.md:9-18`; tipos existentes en `skills/cdad-cycle/scripts/cdad_result.py:826-859`.

## 9. Evidencia de esta intervención

- **Ruta C:** identificación coincidente; request y paquete validados; contrato SHA-256 coincidente; contexto de ejecución v2.
- **Comparación:** `PACKET.md` idéntico byte a byte al render canónico completo.
- **Base examinada:** `3bc0c212185821f506e4c12f2d2789d8ff2b604a`.
- **Archivos modificados por este rol:** ninguno.
- **Commit creado:** ninguno.
- **Tests ejecutados:** ninguno; no se ejecutó la suite completa.

Comandos principales ejecutados:

```bash
python3 scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/010-003-documentary-pilot-architect-discovery-001/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/010-003-documentary-pilot-architect-discovery-001/REQUEST.json --packet .cdad/packets/010-003-documentary-pilot-architect-discovery-001/PACKET.md
```

Ambos finalizaron sin diagnóstico de error. La comparación adicional mediante Python emitió:

```text
PASS: complete PACKET.md bytes equal canonical render; contract sha256 matches; execution context v2.
```

Estado inicial y final observado:

```text
 M docs/.cdad-state.json
```

La modificación preexistente del estado se conservó; no hubo cambios de producto.
