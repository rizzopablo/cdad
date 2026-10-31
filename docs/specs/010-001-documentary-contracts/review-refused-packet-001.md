# Rechazo del paquete de review — 010-001 — 2026-10-31

Evidencia del orquestador sobre el intento `review-001-attempt01`: el reviewer
recibió el paquete `010-001-documentary-contracts-reviewer-review-001` y lo
**rechazó por inválido**, sin realizar la revisión. Este archivo es una
transcripción fiel del FINAL TEXT del rol, precedida por la lectura del
orquestador.

## Lectura del orquestador

- El paquete se compuso con el CLI **instalado**
  (`~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py`), cuya copia de
  `packets/roles/reviewer.md` es la anterior a T4 (`sha256 439287de…`).
- El árbol del proyecto ya tenía el bloque vigente (`bbc4b6f2…`, con la línea de
  obligación documental); el CLI del proyecto (`scripts/cdad_packet.py`) compone
  desde el árbol del proyecto y por eso el paquete publicado no coincide con su
  render canónico: `validate-packet` devuelve rc=2.
- El rechazo del reviewer es **correcto y esperado**: un paquete que no coincide
  con su render canónico no debe ejecutarse. La causa es del orquestador, no del
  rol ni del producto.
- Corrección: retirar este paquete con `disposition` (`superseded`) y publicar un
  sucesor compuesto con el CLI del proyecto, validado antes de despachar.

## FINAL TEXT del reviewer (transcripción)

# Dictamen: paquete inválido, revisión no realizada

**No hay `review.md`.** El paquete de ruta C `010-001-documentary-contracts-reviewer-review-001` no coincide con su render canónico. Por contrato me detengo aquí y no busco otro paquete. Este resultado no es una aprobación ni un rechazo del producto: T5 sigue sin hacerse y no hay hallazgos sobre PC-01 a PC-16 ni sobre D1–D4.

## Causa del rechazo

| Comprobación | Resultado |
|---|---|
| `validate-request` | rc=0 |
| `validate-packet` | **rc=2**: `ERROR: packet differs from canonical rendering` |
| `render --route C` | **Falla**: `packet ... differs from the canonical rendering of its validated request` (008-004 PC-03). No se pudo confirmar la identificación recibida contra su render. |
| `cmp` entre `PACKET.md` y el render completo | Difieren desde el byte 952 de la línea 2 |
| Tamaño | `PACKET.md` 9316 bytes; render canónico 9628 bytes |
| sha256 del contrato | Coincide (`9bf17a39…c94da`) |
| `execution.json` | Schema v2, admisible |

Hay dos diferencias, y las dos vienen del bloque del reviewer:

1. **Hash en la cabecera:** `instruction_sources` declara `roles/reviewer.md` con `439287de…`. Ese hash es el del bloque anterior a T4 (`git show 3344526e:…` da el mismo valor). El bloque actual tiene `bbc4b6f2…`, el mismo que `tdd-t4-green.md:28` declara como vigente.
2. **Línea ausente en el cuerpo:** falta la línea `Documentary duty: in an independent read-only session…`, con el puntero a `documentary-contracts.md`.

## Por qué importa

- **Se pierde lo que esta unidad debía transportar.** El paquete de la revisión de T5 no lleva la obligación documental del reviewer ni el puntero (PC-14). `plan.md:120,273` prohíbe usar instrucciones anteriores al cambio de bloques.
- **El paquete se publicó después del cambio que lo invalida.** `2a918b72` es de las 05:31:30 y `PACKET.md` de las 05:38:23, así que no es un paquete viejo reutilizado.
- **Hipótesis, no verificada:** `prepare` pudo tomar el bloque de la instalación global desactualizada, la misma deriva que `tdd-t4-green.md:112` declara como «no una regresión». Si se confirma, esa deriva no sería solo un problema de entorno: ya habría afectado a un despacho real. No lo comprobé porque el análisis se detuvo aquí. Por eso no me pronuncio sobre si esa declaración es honesta y suficiente.

## Condición de cierre para el orquestador

1. Averiguar qué copia de `skills/cdad-cycle/packets/roles/` usó `prepare`.
2. Cerrar el paquete activo, que sigue en `prepared` en `docs/.cdad-state.json`.
3. Publicar un paquete nuevo desde el árbol vigente.
4. Exigir `validate-packet` rc=0 y que `cmp` con el render completo no dé diferencias, antes de despachar.

## Abstenciones

Me abstengo de todo lo pedido por el encargo: trazabilidad PC-01 a PC-16, examen semántico de D1–D4, escapes de escritura, fuente única, distribución, honestidad estructural y la deriva de `make validate`.

Antes de detectar el rechazo ya había leído las entradas declaradas, la referencia y el diff de `3344526e` y `2a918b72`, y había listado los archivos cambiados. **Esas lecturas no constituyen revisión ni deben citarse como tal.** La revisión válida debe hacerse en una sesión nueva, sin heredar nada de esta.

## Evidencia

```bash
P=.cdad/packets/010-001-documentary-contracts-reviewer-review-001
E=.cdad/executions/exec-010-001-documentary-contracts-002/execution.json
python3 -B scripts/cdad_packet.py render --project-root . --execution-context $E --request $P/REQUEST.json > /tmp/opencode-r.md
cmp /tmp/opencode-r.md $P/PACKET.md
python3 -B scripts/cdad_packet.py render --project-root . --execution-context $E --request $P/REQUEST.json --route C
python3 -B scripts/cdad_packet.py validate-request --project-root . --execution-context $E --request $P/REQUEST.json
python3 -B scripts/cdad_packet.py validate-packet --project-root . --execution-context $E --request $P/REQUEST.json --packet $P/PACKET.md
diff /tmp/opencode-r.md $P/PACKET.md
sha256sum skills/cdad-cycle/packets/roles/reviewer.md
git show 3344526e:skills/cdad-cycle/packets/roles/reviewer.md | sha256sum
git log -3 --format='%h %cI %s' -- skills/cdad-cycle/packets/roles/reviewer.md
stat -c '%y %n' $P/PACKET.md $P/REQUEST.json
```

- **Archivos del repositorio modificados:** ninguno.
- **Commit:** ninguno.
- **Fuera del repositorio:** escribí y borré `/tmp/opencode-r.md`.
- **`git status --short` al final:** las mismas dos rutas previas. Esto no prueba la ausencia de escrituras transitorias.
- **No ejecuté:** tests, generación ni instalación.
