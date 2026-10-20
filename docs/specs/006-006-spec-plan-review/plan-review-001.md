# Dictamen: requiere cambios

**2 B · 2 O.** Revisión de `draft-001`, no aprobación ni autorización para implementar.

Contrato, política y tres fuentes de instrucciones: SHA-256 coincidentes con el paquete. Bucket **m**: fundamento y contrato en contexto; sin atribuir independencia de familia de modelo ni revisión de un diff de implementación.

## Hallazgos bloqueantes

### B-1 — La compatibilidad prometida contradice la modificación de las instrucciones

**Verdict: BLOCKING · Bucket: m · Severidad: Required**

**Ubicación:** `docs/specs/006-006-spec-plan-review/plan.md:40,61-64,110`; `spec.md:68-69,192`.

U1 exige render byte-idéntico al HEAD medido para contratos sin claves nuevas; U2 modifica precisamente dos fuentes incluidas literalmente en ese render.

No es sólo una discrepancia documental:

- `skills/cdad-cycle/scripts/cdad_packet.py:1000-1004,1037-1044` incorpora los bytes actuales de las instrucciones y sus digests.
- `skills/cdad-cycle/scripts/cdad_result.py:563-566` vuelve a renderizar y rechaza un paquete publicado cuyos bytes difieran.

**Consecuencia:** un paquete anterior de `plan-review`, sin campos nuevos, no conserva su render ni necesariamente sigue siendo recibible después de U2. Es incompatible con R-10 e INV-10. Las regresiones citadas componen contra las fuentes actuales; no demuestran recepción de un paquete publicado antes del cambio.

**Movimiento propuesto:** separar compatibilidad de los campos/render dinámicos de compatibilidad entre revisiones del producto. Resolver explícitamente qué sucede con paquetes anteriores; no presentar la comparación dentro de una misma versión como prueba de actualización.

**Cierre verificable:** publicar un paquete con las fuentes anteriores y ejecutar su recepción después del cambio. El resultado debe cumplir la política de compatibilidad que acuerde la autoridad, y las PD deben expresar esa misma garantía.

### B-2 — U5 omite la identidad de transición: una exención puede desaparecer como no-op

**Verdict: BLOCKING · Bucket: m · Severidad: Required**

**Ubicación:** `docs/specs/006-006-spec-plan-review/plan.md:52-55,175-205`; afecta **PD-9**.

U5 limita los cambios a parser y construcción de la entrada. No contempla que los nuevos campos estructurados participen en la identidad de transición.

Actualmente, `skills/cdad-cycle/scripts/cdad_packet.py:5749-5768` calcula esa identidad y retorna por repetición **antes de escribir**. El payload no contiene la exención (`:5015-5066`).

**Escenario real:** se registra un gate y después se repite añadiendo la exención explícita del owner. Siguiendo las zonas declaradas por U5, ambas invocaciones conservan la misma identidad: la segunda puede devolver éxito sin registrar la exención. Cambiar posteriormente su razón tiene el mismo problema.

Todos los casos nuevos declarados pueden pasar usando entradas frescas, sin detectar esta pérdida.

**Movimiento propuesto:** integrar los campos de exención en el contrato de identidad/idempotencia, preservando append-only y la regla de aprobación vigente. Declarar cómo se registra una corrección mediante `--supersedes`, cuando corresponda.

**Cierre verificable:** RED con repetición idéntica y repetición modificando la exención. La primera debe ser no-op; la segunda debe registrarse por la vía permitida o rechazarse explícitamente, nunca perder datos con éxito.

## Hallazgos opcionales

### O-1 — Faltan regresiones directamente acopladas al gate

**Verdict: OPTIONAL · Bucket: m · Severidad: Optional/Consider**

**Ubicación:** `docs/specs/006-006-spec-plan-review/plan.md:54,100-116,195-204`.

U5 no incluye:

- `tests/test_005_012_t2_gate_authority.py`, que cubre precisamente autoridad, campos e idempotencia de `gate`;
- `tests/test_005_012_t5_approval_vigency.py`, directamente relacionado con la vigencia que U5 promete conservar.

La suite del cierre reduce el riesgo, pero no sustituye la regresión focal de esta unidad. Incorporarlos y evaluar el acoplamiento de identidad señalado en B-2. **No encontré evidencia de que sea necesario reemplazar sus oráculos existentes.**

### O-2 — El control negativo de PD-10 prueba el punto equivocado

**Verdict: OPTIONAL · Bucket: m · Severidad: Optional/Consider**

**Ubicación:** `docs/specs/006-006-spec-plan-review/plan.md:74,261`; afecta **PD-10 / E1 / E5**.

Preparar una revisión sin dictamen previo demuestra que se puede **pedir la revisión**. No demuestra que el gate hacia construcción siga siendo supervisado: podría añadirse un rechazo al preparar TDD y ese control permanecería verde.

Añadir el caso con aprobación vigente y sin dictamen, preparando un rol de construcción. Distinguirlo del rechazo esperado **sin aprobación** de PD-14.

## Trazabilidad de los recorridos

| Escenario | PD → unidades | Resultado de la revisión |
|---|---|---|
| **E1: spec sin plan** | PD-1/3/5/7/10/12–15 → U1–U4, U6 | El recorrido nuevo está declarado sin tareas artificiales; evidencia real pendiente. |
| **E2: spec + plan** | PD-1–5/8/13/15 → U1, U6 | Principal y acompañante están fijados; B-1 contradice la compatibilidad prometida. |
| **E3: borrador de otra feature** | PD-1/4–7/13 → U1, U2, U6 | Se separan objeto B y ejecución A; destino en A y rechazo de destino B están declarados. No identifiqué un rodeo adicional exigido. |
| **E4: corrección/re-review** | PD-8/10/12/13 → U2, U3, U6 | Hay comparación de digests y procedimiento focal; no confundirla con compatibilidad de paquetes anteriores. |
| **E5: no aprobación** | PD-7/14/15 → U1, U3, U6 | Se preserva aprobación separada; mejorar el control indicado en O-2. |
| **E6: intención incumplida** | PD-10/12/13 → U2, U3, U6 | La vara semántica está declarada; U6 no certifica por sí solo su aplicación por un reviewer real. |

**Respuesta a la vara:** los tres encargos nuevos están contemplados y no requieren kind, subfase, agente, etapa ni artefacto nuevos. Sin embargo, el conjunto no está listo para aprobar: mantiene una garantía incompatible con sus cambios y deja una pérdida observable en el registro de exenciones. **A-1 no está completo como evaluación de superficies acopladas**, aunque no se haya demostrado un oráculo que deba reemplazarse.

## Validación estructural y evidencia

Separada del juicio semántico:

- `plan-tasks`: JSON válido, seis tareas.
- Sin dependencias inexistentes ni ciclos.
- Sin paralelismo declarado.
- Todas las tareas, sin marcador `detail`, declaran validación por tarea.

Comandos relevantes ejecutados:

```sh
sha256sum docs/specs/006-006-spec-plan-review/plan.md docs/cdad-policy.json
git rev-parse --short HEAD
git status --short
```

Salidas:

```text
ede41e53f4c4e35021fc964d4387e4a593d93a6bde21b56e683415c98f33601a  docs/specs/006-006-spec-plan-review/plan.md
f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711  docs/cdad-policy.json
92f88e1
```

Se inspeccionaron mediante `read`, `rg`, `sed` y `nl` los documentos, tests y consumidores citados; la comprobación estructural se ejecutó con Python sobre el bloque JSON. Los comandos y salidas completos constan en esta sesión.

**Archivos modificados:** ninguno. El estado inicial y final mostró el mismo conjunto de cambios preexistentes.  
**Commit propio:** ninguno.  
**Suite completa:** no ejecutada; no corresponde al cierre de esta revisión de borrador.

## Abstentions

- No certifico aceptación real, producto instalado ni resultados RED/GREEN: esta entrega es un borrador y esos recorridos todavía no se ejecutaron en esta revisión.
- No atribuyo familia de modelo al autor; no está acreditada en los insumos.