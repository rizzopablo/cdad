# Resoluciones del plan-review — 010-003 — 2026-10-31

Resoluciones de la autoridad habilitada (ejercida por el orquestador bajo el
mandato HITL del 2026-10-30, §1 y §3) sobre el dictamen
`plan-review.md` (plan v2, spec v1). Cada bloqueante se cierra por la vía que
el propio dictamen declara como condición de cierre, o se resuelve con una
decisión registrada. Ninguna resolución relaja una promesa de la spec.

## B-1 — El encargo del ensayo debe poder leer la norma que el paquete le manda leer

**Resuelto: sí.** El bloque común de todo paquete instruye leer
`skills/cdad-cycle/references/documentary-contracts.md`; un encargo cuyo alcance
lo excluye se contradice a sí mismo. La spec v2 y el plan v3 declaran esa
referencia —y sólo esa— como lectura e insumo de T5. No revela respuestas: es la
norma que el piloto aplica, no la clave ni el candidato.

## B-2 — Orden del ensayo y del producto corregido

**Resuelto: se mantiene el orden `T3 → T4 → T5 → T6`, con la razón registrada y
la exposición cerrada por contrato y por alcance.**

Motivo: el ciclo exige GREEN antes de un encargo de review (etapa 3 cerrada antes
de la etapa 4); adelantar T5 obligaría a abrir una subfase `review` durante TDD y
rompería el orden de gates que el propio repositorio verifica.

La exposición se cierra así, y la spec v2 lo hace explícito:

1. El producto de T4 **no forma parte del alcance** del reviewer de T5: su
   paquete declara scopes que excluyen `product/`, `oracle/`, `structural/` y
   cualquier informe GREEN o de contraste.
2. Cualquier lectura declarada de esas rutas antes del cierre del primer informe
   **invalida el ensayo** como independiente; no se oculta ni se reclasifica.
3. La exclusión es **contractual y de alcance**, no aislamiento técnico: la spec
   ya lo declara y el plan lo repite donde corresponde.
4. El contraste con la clave y la revisión del producto ocurren **después** del
   primer informe cerrado.

Esta es la alternativa que el dictamen admite («o que la autoridad registre por
qué se mantiene el orden actual»).

## B-3 — Punto de fijación verificable de la clave

**Resuelto: sí.** Antes de despachar T5 debe existir:

- un **commit identificado** que contenga corpus, candidato negativo, muestras
  estructurales y clave de contraste; y
- un **registro de preparación** (`preparation-record.md`) que declare ese
  commit, el `sha256` de cada artefacto y el resultado de la inspección de los
  tres defectos, **sin reproducir las respuestas**.

`.cdad/` está ignorado por git, así que la evidencia de transporte no se
conserva por la vía versionada: el registro cita el commit y las rutas de la
feature donde se copia lo que deba perdurar (informes originales, contraste y
snapshots declarados por hash). El plan v3 lo hace obligatorio en T3 y lo
verifica antes de T5.

## B-4 — Insumos del reviewer del producto corregido

**Resuelto: sí.** El candidato negativo es **obligatorio** en T4: el producto es
una corrección de los tres defectos conocidos, no un documento nuevo. T6 recibe
candidato, clave y `challenge-contrast.md` además del producto, el contrato y las
fuentes, en una sesión distinta de la de T5. Sin esos insumos, PC-11 y PC-13 no
se pueden acreditar.

## No bloqueantes adoptados

| # | Resolución |
|---|---|
| O-1 | **Aceptado como decisión registrada**: T1..T8 son hitos; cada encargo dentro de un hito conserva un rol y una subfase. La autoridad lo registra aquí y el plan lo declara en su estrategia. |
| O-2 | **Adoptado**: nombrar la convención de ancla y el artefacto de inventario que T3 entrega a T4 (interfaz explícita). |
| O-3 | **Adoptado**: el control rechaza un producto con **cero referencias** y toda referencia a una fuente no inventariada. Un verde vacío no acredita nada. |
| O-4 | **Adoptado**: crear `.cdad/evidence/010-003-closure/` antes de invocar la suite de cierre. |
| O-5 | **Adoptado**: auditar en T5 las lecturas declaradas de la transcripción contra `oracle/`, `structural/`, `product/` y los informes reveladores. |
| O-6 | **Adoptado**: la re-verificación de T7 cubre **todo el diff** del producto, no sólo los hallazgos afectados. |
| O-7 | **Resuelto (D-8)**: una falla técnica sin FINAL TEXT (transporte o paquete inválido) **no consume** el ensayo y admite un re-despacho declarado; un informe entregado al que le falta uno de los tres hallazgos **no acredita** la detección y no se reintenta para «encontrarlo». |
| O-8 | **Adoptado**: los ejemplos ilustrativos del `discovery.md` no se reutilizan como respuestas; `discovery.md` queda fuera de los insumos de T5. |

## Lo que esta resolución no hace

No cambia ninguna postcondición de la spec: B-1..B-4 y los nits se cierran con
precisiones de alcance, de orden o de registro. No autoriza publicar, no toca la
instalación y no adelanta ninguna aprobación: la spec v2 y el plan v3 vuelven al
plan-review.
