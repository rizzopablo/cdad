# Review stage 4 — 008-005-ci-gate

**Dictamen: 1 BLOCKING (F1), 5 IMPORTANT (F2-F6), 3 MINOR (F7-F9), 8 abstenciones.**

## F1 — BLOCKING: en los sitios cuya promesa es "responde/termina en la cota", la cota dejo de estar assertada
Sitios 8, 9, 11, 14, 17 de la tabla W5: el techo paso de "cota + margen" a 10x la conducta correcta (25 s),
de modo que una espera acotada de 2x la cota (4-6 s con cota 2; 11,2 s con cota 10) pasa verde; el unico
otro limite es la espera de la interfaz (cota + gracia 5) que no se dispara. `termination == timeout` prueba
que hubo algun timeout, no que venciera la cota configurada, y el envelope no expone duracion. Contradice
PC-6 #3 (degradar a liveness conservando la decision que custodiaba). Cierre: (a) observable de duracion en
el producto (fuera de alcance) o (b) decision explicita que registre la perdida en deferred-hardening y
ajuste los textos que hoy la presentan como guarda "en la cota".

## F2 — IMPORTANT: falta docs/ci-gate.md (W6 del plan, "Dentro" de la spec)
## F3 — IMPORTANT: gate.json no reproduce el esquema: falta `attribution.causes`; `change.kind` puede ser
`desconocido` y las causas `base-invalida`/`cambio-ilegible` quedan fuera del vocabulario cerrado.
## F4 — IMPORTANT: con precondicion fallida no corre ningun paso y `gates: []`; los pasos "siempre" no se
registran como `applicable: false`.
## F5 — IMPORTANT: los errores de coleccion (ERROR sin `::`) no se nombran y el reporte no referencia
`stdout.log` aunque PC-3 lo exige.
## F6 — IMPORTANT: la evidencia de PC-5 es del gate aislado con CLIs grabadoras, no del AC-5 literal
(`git archive` + HOME vacio sobre el pipeline real); el inventario excluye `.git`.
## F7 — MINOR: docstrings de PD-11 siguen diciendo presupuesto total 10 s (la asercion admite 75).
## F8 — MINOR: exit 2 (sin `--base`, raiz inutilizable) sin test.
## F9 — MINOR: PC-7 no es total ante excepciones imprevistas (`attempt.json` JSON no-objeto, paths no UTF-8).

## Verificado OK
PC-1/INV-1/INV-4 (una corrida via close --all, surface --collect-only), PC-2 fail-closed (8 casos),
PC-3 fallos/skips, PC-4 (clasificador real), PC-7, PC-8/INV-5, INV-6 (no reimplementa los comandos);
fixture de PC-5 corregido sin debilitar la asercion; 17 sitios sin techo igual al plazo; regla 8 en su casa
con agentes regenerados; sin rutas del host; sin red; escrituras solo bajo la raiz.
