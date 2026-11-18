Rehice la corrección del PC-8 (ligero/dominio) en `README.md` y `CDAD_metodologia.md`, dentro del alcance del paquete, y la dejé en dos commits. No corrí tests: el cambio es solo documentación y el paquete no los pide.

El paquete es válido. `validate-request` dio rc=0 y `PACKET.md` es idéntico byte a byte al render canónico. El bloque de identificación de la ruta C que recibí coincide con el render ruta C.

**Qué hice, con los comandos exactos**
1. `git checkout 3322aaf3~1 -- README.md CDAD_metodologia.md` y commit `baf2874f`. Esto devuelve ambos archivos a la versión anterior a `3322aaf3` y deja sin efecto esa edición, que estaba fuera del alcance del T1.
2. Reaplicé a mano, con la herramienta de edición, las mismas dos correcciones, y las confirmé en el commit `b38e3c26`:
   - `CDAD_metodologia.md`, fila "CDAD light": ahora dice que es una etiqueta explicativa y no un tercer protocolo. Una feature en el ciclo normal conserva sus puertas (diálogo, readiness, revisión o exención, aprobación y separación de roles) con artefactos más cortos. El trabajo acotado fuera del ciclo usa `cdad-spec-and-test` y declara qué puertas no corrió.
   - `README.md`: el párrafo sobre `cdad-spec-and-test` dice lo mismo, en versión corta.

**Resultado**
- `git diff 3322aaf3 HEAD -- README.md CDAD_metodologia.md` no muestra diferencias. El contenido final es idéntico al del T1 invalidado, lo que se rehízo es la procedencia dentro del alcance.
- Solo toqué esos dos archivos: no hubo cambios en tests ni fuera del alcance.
- `docs/.cdad-state.json` sigue modificado en el árbol de trabajo, pero ya estaba así antes y no lo incluí en mis commits.
- Esto no aprueba retroactivamente `3322aaf3`: el resto de ese commit (agents, skills, sources) sigue fuera de lo que cubre este paquete.