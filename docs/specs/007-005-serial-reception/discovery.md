# Discovery — 007-005-serial-reception (epic 007)

## Recomendación y autoridad

**Recepcionar un único architect read-only, condicionado a confirmar que queda una pregunta sin resolver.** Objetivo propuesto: contrastar la compatibilidad de las alternativas de origen de `odoo` con los contratos vigentes y señalar qué decisión corresponde al consumidor, **sin elegirla, aprobar enmiendas ni modificar producto**.

El paquete antecedente del consumidor `<paquete antecedente>/PACKET.md:18-19` ya encargó una decisión más amplia sobre ese mismo problema y, por premisa, está completado. Por tanto, «Despachar architect» no basta para justificar repetirlo: primero debe contrastarse su resultado recibido con la continuidad vigente. **VERIFY:** cuál es el delta realmente pendiente. Si no existe, este tramo no es elegible; no debe fabricarse trabajo para acreditar CDAD.

Frente a un test-audit o review menor, architect conserva la intención pendiente y evita introducir una auditoría sin objeto ni gate identificado. Presupuesto recomendado: **un paquete, una sesión, una pregunta diferencial, cero escrituras del rol y un informe breve**; sin laboratorio, implementación ni iteraciones automáticas.

La autoridad del consumidor delega preparación, despacho y materialización al orquestador que opera ese repositorio (`docs/epics/E001/execution.md:50-64`). Esta sesión architect **no hereda ese mandato operativo**. Antes de ejecutar, el orquestador debe registrar quién actuará bajo esa autoridad; cambios de alcance siguen reservados al usuario (:66-78).

## Cadena de evidencia y verificación

Usar las herramientas **instaladas de la versión adoptada**, no las del checkout por conveniencia. Con `C` como raíz del consumidor, `S` como scripts instalados, `E` como ejecución y `P` como nuevo paquete:

| Borde | Evidencia exigida |
|---|---|
| Entrada | Captura de `status`, autoridad vigente, versión/procedencia y objetivo diferencial autorizado. `.cdad/packets/$P/{PACKET.md,REQUEST.json}` conserva identidad, contrato y scopes. |
| Antes del transporte | `begin` identifica ejecución, paquete e **intento entero N**; conservar su salida y la de `verify-begin`, ejecutado inmediatamente antes del despacho. |
| Despacho | Registro correlacionado con P, sesión e intento; `runtime`, `model_configured`, `model_reported` y procedencia honesta de los valores desconocidos (`cdad_dispatch.py:147,912-927`). |
| Entrega | Conservar el sobre completo. Ruta nativa: `completed/staged` → descriptor `RESULT.json` bajo `.cdad/inbox` → recepción. Ruta externa: `completed/received` → validar el recibo, **sin recibir otra vez**. |
| Recepción y cierre | Recibo en `.cdad/runtime/results/$E/$P/receipt.json`; payload y digests válidos, `semantic_status=pending`; cierre de continuidad enlazado al mismo P/N y recibo mediante `receipt_checkpoint`. |
| Salida | Transición autorizada y `status` final coherentes; siguiente acción explícita, sin aprobación implícita. |

Fuentes: `references/re-entry.md:27-87`; `references/continuity.md:22-23`; `cdad_result.py:215-232`; `cdad_continuity.py:255-275`.

Comandos **read-only reproducibles**, completando las identidades registradas:

```sh
python3 "$S/cdad_packet.py" status --project-root "$C"
python3 "$S/cdad_result.py" validate-receipt \
  --project-root "$C" --receipt "$R"
python3 "$S/cdad_continuity.py" reconcile \
  --project-root "$C" --execution-context "$X" --packet "$P" --json
python3 "$S/cdad_continuity.py" resume \
  --project-root "$C" --execution-context "$X" --json
sha256sum "$C/.cdad/packets/$P/"{PACKET.md,REQUEST.json} "$R"
```

La prueba temporal de `verify-begin` debe conservarse **antes** del despacho: no se exige que vuelva a aprobar tras avanzar la cabeza (`cdad_continuity.py:2771-2805`). `checkpoint-receipt` es escritura, no comando de auditoría read-only.

## Producto frente a adopción

**No hay cambio de producto demostrado todavía.** 007-004 excluye expresamente el envoltorio privado y remite su adopción a esta unidad (`spec.md:34-44,285`).

El `deleg.sh` encontrado pertenece a **CDAD**, no al consumidor: `.cdad/local/deleg.sh:7-17` prepara y lanza el adaptador asincrónicamente, pero no integra explícitamente `begin`, `verify-begin` ni consumo de `delivery`; tampoco acredita recepción. Recomiendo **retirarlo del recorrido de aceptación** y usar el recorrido publicado, antes que ampliar un segundo orquestador privado. Si se conserva, debe declararse lanzador parcial, no indicador de éxito. No se encontró ese archivo en la ruta equivalente del consumidor.

Una brecha reproducible de orientación o consumo podrá justificar después un cambio general en su dueño canónico; no corresponde anticiparla ni crear otro ledger.

## Verificación, límites y postcondiciones candidatas

Preferir **manifiesto de evidencia verificable**, con rutas, identidades, hashes, comandos y salidas. No duplicar tests de entrega, continuidad, retirada o suspensión ya cubiertos. Sólo un defecto nuevo demostrado justificaría una regresión de producto.

Postcondiciones candidatas:

1. Adopción y autorización vigentes quedan referenciadas con procedencia verificable.
2. El paquete nuevo declara un delta pendiente respecto del resultado 076, contrato y scope read-only.
3. `begin` y su verificación pretransporte corresponden al mismo P/N.
4. El despacho real conserva correlación y observaciones de modelo sin override contrario a I8.
5. El sobre declara una entrega válida y la ruta aplicada coincide con `delivery`.
6. El recibo valida los bytes entregados y mantiene aprobación semántica pendiente.
7. El cierre de continuidad referencia ese recibo/P/N; el estado final no exige repetir efectos.

No hay presupuesto de créditos medido: fijar límite operativo antes del despacho y detenerse ante cuota, sin cambiar modelo ni reintentar automáticamente. La evidencia íntegra permanece privada en el consumidor; los documentos compartidos de CDAD usan alias y omiten rutas internas, identidades y configuración local. Reparación, rollback o fallos no ocurridos naturalmente deben declararse **«verificado en entorno controlado, no observado en consumidor»**, sólo cuando exista esa evidencia controlada (`plan.md:69-81`).

**Evidencia de esta discovery:** JSON del packet parseado íntegramente mediante Python; SHA-256 del contrato coincide con `44b44b11…ae862`. HEAD observado: `61d3f8826ec033248f60f0245950198e6acbb960`. Se ejecutaron lecturas `read`, `nl`, `sed`, búsquedas acotadas `rg`, y consultas `git status --short`/`git rev-parse HEAD`; estado inicial y final: ` M docs/.cdad-state.json`. No escribí archivos, no ejecuté tests ni despachos y no creé commits. **Recepción real aún no observada; propuesta no aprobada.**
