# Decisiones del Discovery — 010-003-documentary-pilot — 2026-10-31

Decisiones del orquestador sobre las tres preguntas que el Discovery dejó abiertas
y sobre el reparto de evidencia. Ejercidas bajo el mandato HITL del 2026-10-30
(`docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md`
§1 y §3), porque el piloto implementa la descomposición ya aprobada del epic:
«un piloto recorre el ciclo con un entregable trazable y evidencia independiente
de detección de defectos estructurales y semánticos».

## D-1 — Desafío protegido, separado del producto corregido

Se aprueba un **corpus sintético con tres defectos sembrados** y una **clave de
contraste fijada antes de revisar**:

1. una afirmación sin respaldo en el corpus autorizado;
2. una contradicción omitida (dos posiciones incompatibles presentadas como consenso);
3. una referencia que existe pero no sostiene lo afirmado.

El borrador defectuoso es un **candidato negativo declarado**: nunca se presenta
como conforme ni se hace pasar por entregable aceptado. El producto corregido se
produce después, y la corrección no revela la clave antes de que el reviewer
cierre su primer informe.

**Motivo.** Sin defectos conocidos no hay forma de medir detección; con la clave
visible no hay forma de acreditar que la revisión fue independiente.

## D-2 — El entregable documenta la divergencia, no la resuelve

Cuando dos fuentes autorizadas se contradicen y no existe una decisión que
resuelva el conflicto, el entregable **conserva ambas posiciones con sus
localizadores** y registra la divergencia. No se inventa consenso ni se elige una
posición por conveniencia.

**Motivo.** Es la regla ya normativa de `documentary-contracts.md` (una
contradicción se registra; no se resuelve inventando consenso) y evita que el
piloto acredite una capacidad que el método no promete.

## D-3 — El primer informe del reviewer se cierra antes de mostrar la corrección

El reviewer recibe contrato, borrador defectuoso y fuentes autorizadas **sin la
clave de contraste ni el entregable corregido**. Su primer informe se conserva
cerrado. Si falta uno de los tres hallazgos semánticos, **esa detección no queda
acreditada**: una revisión posterior que ya conoce la clave puede verificar la
corrección, pero no reemplaza retrospectivamente el primer ensayo.

**Motivo.** Sin esta separación, el informe podría reconstruirse a partir de la
corrección y la acreditación sería circular.

## D-4 — Reparto de evidencia: qué puede un test y qué exige una sesión real

| Puede acreditarlo un test de repositorio | Exige ejecución real de un rol |
|---|---|
| El control estructural detecta el defecto elegido (localizador roto) y acepta la muestra corregida | Que el reviewer encontró y fundamentó los tres defectos semánticos |
| Los localizadores cumplen la convención acordada para este piloto | Que contrastó cada afirmación con las fuentes declaradas |
| Los bytes protegidos se conservan en los estados observados | Que produjo un informe independiente, con alcance y abstenciones |
| Los paquetes transportan alcances y declaraciones correctas | Que el productor entregó la corrección y fue revisada |

Un informe simulado puede probar transporte o materialización; **nunca sustituye**
el informe de la sesión real. Ninguna prueba de texto se presentará como conducta
acreditada.

## D-5 — Sin mecanismo nuevo

El piloto **no** crea roles, agentes, selectores, campos del estado ni formatos
nuevos, y no modifica la toolchain. Usa el procedimiento documental de `010-002`,
la norma de `010-001` y los tipos de artefacto existentes (`review`,
`role-report`, `test-writer-role-report`). Los defectos abiertos del epic
(I-8, I-9, I-10, I-11, I-12, I-13) se respetan: no se editan bloques de
instrucciones (`packets/{roles,substages}`) en esta unidad, no se usan controles
dependientes de números de línea ni de rewrap, y el tipo de artefacto se verifica
antes de recibir.

## D-6 — Aceptación

La aceptación funcional del piloto es de la autoridad habilitada y no se solicita
con bloqueantes abiertos. El cierre separa tres registros: evidencia estructural
(qué se ejecutó y con qué resultado), informe semántico independiente (qué se
contrastó, hallazgos y abstenciones) y aceptación funcional.

## Lo que este piloto NO va a acreditar

- Que los defectos hayan surgido espontáneamente de un productor: la muestra es
  sembrada y así se declara.
- Detección infalible: se acredita detección **sobre esta muestra**.
- Conducta de modelos en general: se acredita el informe de **una** sesión real,
  con su alcance y sus límites.
- Fidelidad de un documento de cliente: el corpus es sintético.
