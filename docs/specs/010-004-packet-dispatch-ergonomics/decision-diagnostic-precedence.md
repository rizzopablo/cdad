# Decisión del proceso: precedencia de diagnósticos de configuración sobre el rechazo de contexto v1

**Fecha:** 2026-10-30 (UTC).
**Autoridad:** mandato HITL vigente (`docs/epics/epic-010-documentary-specialization/execution.md`); decisión del owner Pablo, transmitida por el orquestador supervisor a esta sesión subagente.
**Unidad:** `010-004-packet-dispatch-ergonomics`, T2 (GREEN entregado en `a273042e`, attempt19).
**Naturaleza:** decisión de proceso que gobierna la corrección del caso C3. **No edita** `spec.md` (pin `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`), **no edita** `plan.md` (pin `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685`) y **no cambia tests ni producto por sí misma**.

## Decisión

Cuando una preparación nueva encuentra a la vez (a) un defecto de configuración, autoridad o policy y (b) un contexto v1 (explícito o implícito), el diagnóstico que se emite primero es el de (a):

- policy ausente, mal formada o existente pero no-archivo;
- autoridad, aprobación o pin inválidos, cuando el CLI ya puede verificarlos sin seleccionar un contexto v2.

El rechazo de (b) se conserva: la operación sigue fallando en todos los casos, sin efectos persistentes, sin publicar paquete, sin binding v2, sin copiar/convertir/reubicar el contexto y sin fallback legacy. Lo que cambia es la causa que el usuario ve y puede accionar.

La precedencia no se aplica a la inversa ni crea una jerarquía general de diagnósticos: solo asegura que, cuando ambos defectos coexisten, el diagnóstico accionable de configuración no quede inalcanzable detrás del rechazo de versión/ubicación del contexto.

## Caso C3 que la motiva

- Test: `tests/test_004_002_t2_reviewfix.py::TestF6NoLegacyFallbackOnInvalidPolicyLocation::test_f6_policy_directory_with_v1_context_no_legacy_fallback` (`:462-501`).
- Escenario: `docs/cdad-policy.json` existe pero es un directorio, y hay un contexto v1 en `.cdad/execution.json`.
- Hoy: `prepare` falla (rc≠0), no publica paquete, deja el v1 byte-idéntico y el árbol sin cambios; pero el diagnóstico es el del v1: `an existing v1 execution context is present at .cdad/execution.json...` y no nombra la policy. La aserción de `:487-489` (regex `policy|pol[íi]tica`) falla.
- Clasificación: `docs/specs/010-004-packet-dispatch-ergonomics/fixture-impact-inventory.md` §0, §2 y §3(iii) lo registran como **C3, causa distinta**, fuera de la migración de fixtures y **no** corregible relajando el test.
- Incumplimiento: `spec.md` §4.5 (`:337-357`, párrafo de `:352`) exige que «La preparación nueva sobre legado informa los requisitos faltantes de §4.1: policy, autoridad/aprobación/pin o coherencia de estado». El rechazo del contexto v1 hace inalcanzable ese diagnóstico de policy en este escenario; el test protege exactamente esa promesa.

## Fundamento (criterio de uso real)

Cuando la configuración del proyecto está mal, ese es el bloqueo accionable. Decirle al usuario «tu contexto no es canónico» cuando el problema es la policy lo manda a arreglar lo que no corresponde: el contexto v1 no es el defecto a corregir en ese momento, y la acción que sugiere (migrar o convertir el contexto) no resuelve la policy inválida. El diagnóstico debe nombrar primero la causa que el usuario puede corregir con el procedimiento existente (proponer y materializar la policy, o corregir autoridad/aprobación/pin), sin dejar de rechazar por el contexto.

Esto no debilita ningún diagnóstico ni abre un fallback: agrega una comprobación previa de configuración y conserva intacto el rechazo posterior. Tampoco cambia los códigos de salida ni las envolturas existentes (`spec.md` §4.5, último párrafo).

## Relación con §4.5 y con N-5

§4.5 ya obligaba a informar los requisitos faltantes de §4.1; la decisión **restaura** ese requisito en el escenario C3, no crea un contrato nuevo. `PC-09` (`spec.md:422`) sigue exigiendo causa y siguiente acción pertinente.

`plan.md:79` declara N-4/N-5/N-6 **OPTIONAL abiertos/postergados** y pide «No se introduce precedencia diagnóstica ni interpretación legacy nueva»; `spec.md:576` conserva ese estado. Esta decisión **no reabre la spec**, no edita el plan y no declara N-5 resuelto como ítem del plan. Resuelve su **espíritu**: el riesgo que N-5 quería evitar era que el implementer eligiera en silencio una jerarquía o una interpretación legacy nueva. Aquí la jerarquía la decide explícitamente el owner, en la dirección que §4.5 ya exige, y queda registrada como fila vigente del packet. No hay interpretación legacy nueva: el v1 se sigue rechazando, no se convierte, no se adopta hacia adelante ni se reubica. N-4/N-5/N-6 permanecen postergados para cualquier otro alcance.

## Consecuencias observables

- El test C3 queda verde sin tocar el test, la regex ni la aserción.
- Se conservan los rechazos existentes: v1 explícito e implícito siguen rc≠0, stdout vacío, v1 byte-idéntico, sin contexto v2 fabricado, sin paquete y con el árbol sin cambios (INV-11/`PC-04`).
- Los 62 fallos C1 y el fallo C2 del inventario no cambian de causa; el fix no los absorbe ni los hace pasar.
- La corrección se implementa únicamente en `skills/cdad-cycle/scripts/cdad_packet.py`; `spec.md`, `plan.md`, `tests/**` y la copia instalada quedan intactos.

## Trazabilidad

- Caso C3 y medición: `fixture-impact-inventory.md` §0, §2, §3(iii) (commit `3f39eefd`).
- Requisito: `spec.md` §4.5 (`:337-357`; cita en `:352`), `PC-09` (`:422`), `PC-04` (`:406`), INV-11.
- Test: `tests/test_004_002_t2_reviewfix.py:462-501`, aserción de política en `:487-489`.
- Plan y estado de N-5: `plan.md:79`; `spec.md:576`.
- Mandato: `docs/epics/epic-010-documentary-specialization/execution.md`; instrucción del owner transmitida por el orquestador supervisor.
- Packet que aplica: `010-004-packet-dispatch-ergonomics-implementer-review-fix-001` (preparado, no despachado).
