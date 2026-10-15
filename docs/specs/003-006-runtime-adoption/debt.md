# Deuda — 003-006-runtime-adoption

| Id | Origen | Prioridad | Descripción |
|---|---|---|---|
| T1-F2 | review-t1 | baja | `tests/test_003_006_t1_wiring.py`: las aserciones por paso no excluyen la tabla de referencias; la fila de `continuity.md` satisface 5 de 6. Excluir líneas de tabla del matching. |
| ANON-1 | validadores (T2) | media (antes de publicar) | `validate-odoo-specialization.sh` A3: patrones sensibles en `docs/specs/004-003-planning-procedures/{supervision-record,review-t5}.md` y `tests/test_role_packets.py` (preexistente, 2026-10-05). Además, `docs/runtime-adopted-version.md` lleva rutas absolutas locales. |
| T2-SCOPE | green-t2 | baja | El paquete de GREEN T2 no incluía `.gitignore` en `write_scope` aunque el plan lo exige; ajustar el `--write-scope` al preparar paquetes que tocan archivos raíz. |
| T2-O1 | review-t2 | media | Escrituras sin tmp+`os.replace` y sin rollback si falla a mitad; la re-corrida converge. |
| T2-O2 | review-t2 | baja | Registro `.cdad/activation.json` corrupto se descarta en silencio; debería dar error con guía. |
| T2-O3 | review-t2 | baja | Claves del manifest usadas como componentes de ruta sin sanear (`..`); `A` es de confianza (`install.sh`). |
| T2-TOCTOU | rereview-t2 | baja | La contención no es libre de carreras si un componente cambia entre la comprobación y la escritura; sin amenaza concurrente declarada. |
| T3-O1 | review-t3 | media | El bloque de re-entry del cuerpo del orquestador no nombra `materialize` (paso 3 de `re-entry.md`); hoy depende de cargar la referencia. |
| T3-O3 | review-t3 | baja | `BANNER_PHRASE` del test de coherencia es más ancho que el banner real; anclarlo a la oración exacta. |
| T3-O4 | review-t3 | baja | Palabras clave flojas en `wired()` (`stage`, `transición`). |
| RU1-H4 | rereview-ru1 | baja | La reescritura del hook no está anclada a `command:` y también reescribe el comentario del frontmatter (cosmético). |
| RU1-H5 | rereview-ru1 | baja | La activación no comprueba que el clasificador `cdad_packet.py` exista en `A` ni esté en el manifest; hoy se descubre al fallar cerrado. |
| T4-CKPT | T4 uso real | media | Un `checkpoint` de límite con la clave del paquete recién recibido choca con su `begin` y se rechaza (split-brain). `continuity.md` debería decir que el checkpoint de límite usa la clave del paquete siguiente (o que el `begin` siguiente cumple ese papel). |
| T4-REF | T4 uso real | **alta** | `resume`/`reconcile`/`trigger` fallan cerrados si cambió cualquier referencia del checkpoint; los ledgers y debt.md cambian en cada paso. Opciones: referenciar solo artefactos inmutables (commits, receipts, specs aprobadas) o fijar la referencia a un commit (`path@sha`); verificar los documentos vivos como "cambiado desde" sin bloquear. Con T4-CKPT, hoy la rotación exige no escribir entre el último `begin` y la reanudación. |
| RU2-F4 | rereview-ru2 | baja | La enmienda O1 compara `classification != "split-brain"`; sería más fuerte igualdad exacta con `"not-started"`. |
| RU2-F6 | rereview-ru2 | baja | `test_003_006_t4_ru2_refused_write.py` limpia con `rm -rf` por subproceso; el estándar del repo es `shutil.rmtree`. |
