Arreglé el bloqueo de `review-006.md`: la definición de «CDAD light» en el glosario ya no contradice la fila de la matriz ni PC‑8/R8. Está commiteado como `89038416`. No ejecuté tests: es un cambio solo de documentación y no toqué ninguno.

**Cambio.** Modifiqué una sola línea de `CDAD_metodologia.md` (2937). La entrada ahora dice:
- «CDAD light» es una etiqueta explicativa y no un tercer protocolo.
- Una feature del ciclo normal conserva la revisión del borrador (o la exención registrada del dueño), la aprobación y la separación completa de roles, solo con artefactos más cortos. Ninguna de esas cosas es opcional.
- El trabajo acotado fuera del ciclo usa `cdad-spec-and-test` y declara las puertas que no ejecutó.

**Consistencia.** Con `grep -n -i "light" CDAD_metodologia.md` revisé todas las apariciones de «light» en el archivo. La línea 114 (la fila de la matriz) ya era correcta. La línea 2832 es solo una etiqueta del diagrama de decisión y la 2955 solo menciona «light» como nivel, y ninguna de las dos presenta la revisión como opcional. Las demás coincidencias son la palabra común «lighter», sin relación. `git diff --check` salió limpio.

**Intake de Route C.** `cdad_packet.py render --route C` salió con rc=0 y el bloque de identificación coincide con el del despacho. El `cmp` contra `PACKET.md` completo no sirve en esta ruta: el render solo da la identificación (787 bytes) y `PACKET.md` trae el cuerpo completo (7002).

**Fuera del commit.** `docs/.cdad-state.json` aparece modificado en el árbol de trabajo desde antes de mi cambio. No lo toqué ni lo commiteé.

Queda pendiente la revisión semántica independiente.