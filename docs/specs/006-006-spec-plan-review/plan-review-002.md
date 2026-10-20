# Dictamen: requiere cambios

Revisión de **draft-002**, no aprobación ni autorización para implementar. Contrato y fuentes de instrucciones: SHA-256 coincidentes con el paquete.

## Cierre de los hallazgos anteriores

| Hallazgo | Resultado |
|---|---|
| **B-1** | **Cerrado en el diseño.** La garantía ahora es intra-revisión; la incompatibilidad entre revisiones y sus dos salidas están declaradas (`spec.md:81-82,188`; `plan.md:85,91,115`). El precedente citado efectivamente contiene esa disposición. |
| **B-2** | **La pérdida silenciosa queda resuelta en el diseño**, con identidad, repetición idéntica y corrección por `--supersedes` o rechazo (`spec.md:154-157,181`; `plan.md:54-65`). Sin embargo, el arreglo introduce la regresión B-3 siguiente. |
| **O-1** | **Cerrado.** Ambas regresiones focales están incorporadas y justificadas (`plan.md:66-68`). |
| **O-2** | **Cerrado.** Los controles ahora distinguen construcción con aprobación y sin dictamen de construcción sin aprobación (`spec.md:182`; `plan.md:87-90`). |

Las citas abreviadas anteriores corresponden a `docs/specs/006-006-spec-plan-review/`.

## Hallazgo bloqueante

### B-3 — Añadir campos nulos cambia también las identidades históricas sin exención

**Verdict: BLOCKING · Bucket: m · Severidad: Required**

**Ubicación:** `docs/specs/006-006-spec-plan-review/plan.md:57,65,134`; `docs/specs/006-006-spec-plan-review/spec.md:154-157,181`.

U5 exige incorporar los cuatro campos al payload canónico, con `null` cuando no se declaran. Esto cambia la clave **también para invocaciones sin exención y para las demás clases**.

La afirmación de `plan.md:134` —que los ausentes se normalizan igual y la repetición conserva el no-op— sólo se sostiene para dos invocaciones ejecutadas **después** del cambio. No cubre una transición registrada con el producto actual.

**Evidencia del mecanismo:**

- El payload actual no contiene esas claves: `skills/cdad-cycle/scripts/cdad_packet.py:5045-5063`.
- La identidad depende de su serialización completa: `:5066-5079`.
- El reconocimiento histórico compara la clave exacta: `:5100-5110,5766-5770`.
- Si un gate histórico deja de reconocerse, puede rechazar por aprobación vigente: `:5821-5829`.
- Para un cierre histórico, la rama cerrada puede rechazarlo como distinto: `:5627-5633`.

Calculé con las funciones actuales y fixtures sintéticos la identidad antes/después de añadir los cuatro `null`: **las claves difieren en gate, closure y disposition**. Es un cálculo del diseño propuesto, no una ejecución de implementación inexistente.

**Consecuencia real:** actualizar el producto entre una transición y su reintento convierte una repetición idéntica en rechazo o nueva entrada. En particular:

- contradice el replay de cierre de **005-014 PD-23** y su reanudación prevista (`docs/specs/005-014-closure-replay/spec.md:45-53,104-110`);
- afecta la idempotencia de disposición aprobada en **006-005 PD-19(b)** (`docs/specs/006-005-native-path-parity/spec.md:219`).

La deuda histórica de 005-014 no cubre esta nueva frontera: se refiere a entradas **sin** `transition_key_payload` (`spec.md:158`); las entradas actuales ya lo tienen. PD-16 de esta feature trata paquetes/render, no identidades persistidas de transiciones.

**Movimiento propuesto:** preservar la identidad previa cuando no hay exención, o definir un reconocimiento compatible de esos payloads históricos. Cualquier alternativa que retire garantías anteriores requiere una enmienda explícita de autoridad, no presentarla como conservación sin cambios.

**Cierre verificable:** agregar un recorrido de dos revisiones: registrar con el producto anterior y repetir con el nuevo, sin exención, para gate, closure y disposition. Comprobar no-op, misma entrada y estado byte-idéntico; conservar además los casos nuevos que cambian la exención.

## Retr trazabilidad E1–E6

| Escenario | PD → plan | Resultado |
|---|---|---|
| **E1: spec sin plan** | PD-1/3/5/7/10/12–15 → U1–U4, U6 (`plan.md:40-50,74-104,109`) | La forma explícita permite preparar y recibir la revisión sin tareas artificiales. B-1 no elimina este recorrido dentro de la revisión vigente. |
| **E2: spec + plan** | PD-1–5/8/13/15 → U1, U6 (`plan.md:43-44,110,112`) | Principal y acompañante quedan fijados; la corrección invalida la cobertura por digest. La recepción efectiva queda pendiente de U6. |
| **E3: borrador de otra feature** | PD-1/3/5/6/7/13 → U1, U2, U6 (`spec.md:108-116`; `plan.md:111`) | **No identifiqué un bloqueo mecánico adicional.** La forma `spec` evita la puerta del plan; ejecución A y objeto B permanecen separados; materialización usa A y rechaza B. El procedimiento exige identificar el objeto revisado. |
| **E4: corrección/re-review** | PD-8/10/12/13 → U2, U3, U6 (`plan.md:74,83,112`) | Se distingue deriva del documento de incompatibilidad del producto. La comparación exige nueva cobertura; no se atribuye esa función al CAS. |
| **E5: no aprobación** | PD-7/14/15 → U1, U3, U6 (`plan.md:46,88-89,113`) | Dictamen y aprobación permanecen separados; O-2 ahora prueba el límite correcto. **B-3 afecta el reintento posterior del gate**, no convierte el dictamen en aprobación. |
| **E6: intención incumplida** | PD-10/12/13 → U2, U3, U6 (`plan.md:74-76,83,114`) | La vara semántica y su evidencia textual están declaradas. No se presentan como certificación automática del producto. |

**Respuesta sobre garantías previas:** sí, queda una contradicción no declarada en el alcance de B-2: el replay de transiciones persistidas señalado en B-3. No encontré otra contradicción material en los recorridos examinados. La incompatibilidad de paquetes de B-1 ahora está expresamente declarada.

## Validación estructural y evidencia

Separada del juicio semántico:

- `plan-tasks`: JSON válido; seis tareas; dependencias existentes y sin ciclos.
- Sin paralelismo declarado; todas las tareas incluyen validación por tarea.
- Los tests de idempotencia inspeccionados crean y repiten bajo el mismo producto; no acreditan actualización entre ambas operaciones.

Comandos ejecutados, con sus salidas relevantes:

```text
sha256sum docs/specs/006-006-spec-plan-review/plan.md docs/cdad-policy.json
824d25af9c7827c65a7c8653985f6ddcadd669ceadad9cd3924ba8eae6838712
f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711

git rev-parse --short HEAD
32cfec4
```

También ejecuté `python3 -B -` para comprobar el JSON/dependencias y calcular las identidades mediante las funciones extraídas por AST. Salida:

```text
plan-tasks: valid JSON; 6 tasks; dependencies resolved; acyclic;
per-task validation present; no parallel declarations
gate: equal=False
closure: equal=False
disposition: equal=False
```

Los comandos completos, lecturas y salidas constan en esta sesión.

**Archivos modificados:** ninguno; `git status --short` final coincide con el inicial.  
**Commit propio:** ninguno.  
**Suite completa:** no ejecutada; revisión de borrador.

## Abstentions

- No certifico RED/GREEN, producto instalado ni aceptación real: son verificaciones futuras del plan.
- No atribuyo independencia de familia de modelo respecto del autor; no está acreditada.

**Veredicto final: requiere cambios por B-3.**