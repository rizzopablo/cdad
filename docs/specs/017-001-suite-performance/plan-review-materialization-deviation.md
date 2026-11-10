# Desviación de materialización — `plan-review.md` (2026-11-07)

El descriptor del receptor declaró `artifact_kind: role-report` para el informe
del reviewer en la subfase `plan-review`. `receive` lo admitió y lo fijó en un
recibo durable; `materialize` lo rechazó porque la tabla cerrada §7 solo admite
`plan-review` para ese rol y subfase.

El recibo durable no se sobrescribe. El artefacto se copió **byte a byte** desde
el parte almacenado del recibo
(`.cdad/runtime/results/exec-017-001-suite-performance-001/017-001-suite-performance-reviewer-plan-review-001/parts/017-001-plan-review.utf8`),
cuyo SHA-256 es `ae7ff32d9383d30a44eb7938902e482db1e536dd87cf7e5b6796580ac4506c76`
y coincide con el FINAL TEXT staged y con la copia en
`docs/specs/017-001-suite-performance/plan-review.md`.

No cambia el contenido, el veredicto ni la separación de roles: la desviación es
de forma en el descriptor. Se registra para el cierre y para corregir el hábito
de despacho (declarar el kind de la subfase en el descriptor de recepción).
