# Cierre del plan-review — 010-003 — 2026-10-31

Quinta vuelta del plan-review sobre `spec.md` v5 (`f2dce9e0…1d5e5`) y
`plan.md` v6 (`49ce6f81…352b04`): **veredicto aprobable, sin bloqueantes.**
BN-3, O-13 y O-14 cerrados; los scopes de T4 y T7 construibles; las quince PC
idénticas a las de la spec v3; `plan-tasks` aceptado con T1..T8; ninguna
contradicción nueva entre spec y plan.

Cinco vueltas, cuatro dictámenes con bloqueantes y ninguno inventado: cada uno
señaló una promesa que el mecanismo no podía cumplir o una contradicción entre
el paquete y el alcance (B-1: la norma que el paquete manda leer fuera del
alcance; BN-1: el diff completo frente al objeto documental; BN-2: el
`read_scope` de T4 no construible; BN-3: el comando focal mostraba el cuerpo del
verificador). Todos se cerraron endureciendo el contrato, no rebajándolo.

## Resolución de los dos hallazgos opcionales

**O-15 — la clave podría viajar a T7 dentro de `product-review.md`.** Se cierra
**en el despacho**, no en el contrato: el paquete de T6 fija como invariante que
sus hallazgos se fundamentan contra las fuentes y el inventario **sin transcribir
la clave** en el informe. El plan ya prohíbe a T7 leer `oracle/`; esta precisión
cierra la vía indirecta sin tocar el texto aprobado.

**O-16 — la inspección de T3 cubre `oracle/` y no `structural/`.** Aceptado como
**límite declarado**: el verificador debe leer las muestras estructurales para
PC-04..PC-06, de modo que sus diagnósticos pueden mostrarlas. No son respuestas
semánticas ni la clave, y el límite del contrato dice «como insumo», que sigue
siendo verdadero. Queda en el cierre como límite, no como deuda.

## Aprobación bajo el mandato

La spec v5 y el plan v6 se aprueban en nombre de Pablo (dueño del repo) bajo el
mandato HITL del 2026-10-30 (§1 y §3): el piloto implementa la descomposición ya
aprobada del epic (`010-003`: «un piloto recorre el ciclo con un entregable
trazable y evidencia independiente de detección de defectos estructurales y
semánticos»). No se aprueba nada fuera de ese alcance, no se publica y no se
toca la instalación.

Con esta aprobación, `spec.md` y `plan.md` quedan **pineados** por el gate: un
cambio posterior exige una enmienda registrada.
