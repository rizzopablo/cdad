# Desviación declarada del AUDIT — lectura de la norma por `bash` — 010-003

**Fecha:** 2026-10-31. **Ámbito:** orquestador CDAD, bajo el mandato HITL del
2026-10-30 (§1 y §3). **Objeto:** el AUDIT de T2 (`test-audit.md`) declara que
el guard de lectura le denegó `read` sobre
`skills/cdad-cycle/references/documentary-contracts.md` y
`skills/cdad-cycle/references/stage-3-tdd.md` —raíz de implementación— y que las
leyó **por `bash`**. Esta nota registra el hecho, lo clasifica y decide.

## Qué pasó

- El bloque del rol `test-writer` dice: «The shared norm lives in
  `skills/cdad-cycle/references/documentary-contracts.md` (read it, never
  restate it)». El bloque común del paquete repite la remisión.
- La política de rutas clasifica `skills/**` como `implementation`, y el
  test-writer no admite esa clase en lectura (`_validate_scope`). El guard negó
  la lectura.
- El rol leyó las dos referencias por `bash` y lo declaró en su informe, sin
  ocultarlo.

## Clasificación

**Es una desviación de I-8** («una denegación de lectura necesaria al
test-writer se informa y escala; no se rodea con otra herramienta»). La
declaración no la convierte en conducta correcta: la vía correcta era detenerse
en esa parte y reportar el bloqueo.

**Atenuantes que se registran como tales, no como excusa:**

1. El conflicto es del paquete, no una invención del rol: su propio bloque le
   ordena leer la norma que la política de rutas le prohíbe.
2. No existían producto, clave ni muestras: la lectura no pudo revelar ninguna
   respuesta del piloto.
3. Las dos referencias son norma y procedimiento de método, no código de
   implementación del producto.

**Efecto sobre la sustancia del AUDIT: ninguno verificable.** El mapeo se deriva
del contrato de la feature; la única cita a la norma sostiene C-1 y su conclusión
se verificó, en el POST-AUDIT, contra el silencio del contrato (`spec.md:115`,
`176-177`, `180`, `240-242`).

## Decisión

**Se acepta el AUDIT; no se rehace.** Rehacerlo en una sesión limpia reproduciría
la misma disyuntiva, porque el bloque del rol seguiría ordenando leer la norma y
el guard seguiría denegándola; el resultado sería el mismo mapeo sin la cita, no
un mapeo mejor. El valor de la evidencia está en el mapeo, y el mapeo está
verificado por una sesión distinta (POST-AUDIT) que **no** intentó la lectura
prohibida y lo declaró.

## Condición que se fija para T3

El paquete de T3 declarará, en su `objective` y en sus `invariants`:

- que el contrato de la feature es la fuente del encargo y que
  `skills/cdad-cycle/references/**` **no es insumo**;
- que si el bloque del rol remite a la norma y el guard la deniega, el rol **se
  detiene en esa parte y lo reporta**, sin leerla por otra vía;
- que una lectura por otra vía invalida el encargo y se re-despacha.

Si T3 necesita una convención que solo la norma fija, el contrato ya la
contiene (§2.4: identificadores, anclas, enlaces relativos); no hay razón para
leerla.

## Deuda que queda

**I-14** en el backlog del epic: el bloque del test-writer ordena leer una norma
que su alcance de lectura no admite. Hasta que se corrija —mover la norma a una
clase admitida, permitir la ruta exacta o corregir el bloque—, todo encargo
documental del test-writer repite la disyuntiva. Esta nota la declara; no la
resuelve, porque editar `packets/{roles,substages}` está fuera de esta unidad
(INV-06, D-5).
