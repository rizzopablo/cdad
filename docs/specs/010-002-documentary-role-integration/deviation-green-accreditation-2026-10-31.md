# Desviación de acreditación — GREEN de T4 — 010-002 — 2026-10-31

Documento del ámbito del orquestador. Registra **cómo** se acreditó el despacho del
GREEN de T4 pese a un defecto del mecanismo de admisión de paquetes, y **qué no se
relajó**. Ejercido bajo el mandato HITL del 2026-10-30 (§1 y §3).

## 1. Regla que se aplicó

`skills/cdad-cycle/scripts/cdad_packet.py` (`verify_published_packet`, 008-004
PC-01/PC-03): un paquete publicado solo se admite si `PACKET.md` es **byte a byte**
igual a `render_packet(request, execution_document, project_root)`.

`render_packet` (`cdad_packet.py:1947-1955`) **no pineа** las fuentes de
instrucción: lee en cada corrida `common.md`, `roles/<rol>.md` y
`substages/<rol>-<substage>.md` desde el árbol vivo y recalcula sus `sha256` para
la cabecera.

## 2. Qué ocurrió

El paquete `010-002-documentary-role-integration-implementer-green-001` se publicó
con el árbol en `0d935bc8`. Su cabecera declara:

```
roles/implementer.md  sha256 d93b44e411b89e35eae03184b341338bcd88e1345dbfc767eea314b0dc964fbe
```

El encargo autorizaba —y el plan aprobado exigía— escribir en `skills`, donde vive
ese mismo bloque estático. El GREEN entregado (`c0126040`) agregó **una línea** a
`skills/cdad-cycle/packets/roles/implementer.md` (nuevo `sha256 ef3dab65…`).

Consecuencia: al terminar el trabajo, el árbol ya no reproduce los bytes
publicados, así que `record-dispatch` rechazó el registro con el diagnóstico
«packet differs from the canonical rendering of its validated request». El paquete
publicado **no fue alterado**; lo alterado es la fuente que el render lee.

`git show 0d935bc8:skills/cdad-cycle/packets/roles/implementer.md | sha256sum`
devuelve exactamente `d93b44e4…`: el paquete es el render canónico de las fuentes
que él mismo declara.

## 3. Cómo se acreditó — secuencia exacta

**Declaración expresa (enmienda tras el bloqueante B3 del review de T8):** no fue
solo una comparación. Las dos operaciones que la guarda bloquea —`record-dispatch`
y `receive`— **se ejecutaron con el árbol restituido** a los bytes de publicación
del bloque de rol, y el árbol se restauró a los bytes entregados inmediatamente
después. Es una **excepción a una guarda fail-closed**, no una comparación pasiva,
y así queda declarada.

Secuencia ejecutada (hora local `-0300`, un solo script con `trap` de
restauración, de modo que la restitución se deshace aunque el comando falle):

| # | Operación | Estado del árbol | Resultado | Marca de tiempo |
|---|---|---|---|---|
| 1 | `git show 0d935bc8:skills/cdad-cycle/packets/roles/implementer.md > <archivo>` | bloque de rol en `d93b44e4…` | `sha256` = el declarado en la cabecera | — |
| 2 | `validate-packet --request … --packet …` | `d93b44e4…` | `rc=0` | — |
| 3 | `prepare --record-dispatch … --attempt-id green-001-attempt01 --continuity-attempt 1` | `d93b44e4…` | `rc=0`; escribe `dispatches/green-001-attempt01.json` | `09:45:32` |
| 4 | `cdad_result.py receive … --continuity-attempt 1` | `d93b44e4…` | `rc=0`; escribe `receipt.json` | `09:45:48` |
| 5 | `trap` → `git checkout HEAD -- <archivo>` | vuelve a `ef3dab65…` | restauración verificada | `09:45:48` |
| 6 | `register-transition --transition delivery …` | árbol entregado | `tdd-green-t4` registrado | `09:45:58` |

`PACKET.md` (`e49f4b06…`) y `REQUEST.json` (`198ac0e6…`) no se modificaron en
ningún momento. El árbol quedó sin cambios en esa ruta (`ef3dab65…`, `git status`
limpio para ese archivo) y el estado de la unidad avanzó con el árbol ya
restaurado.

## 4. Por qué no se usó otra vía

- **`prepare --replace-packet`**: exige obsolescencia del predecesor (PD-8). El
  contrato y la política no cambiaron; habría sido un sucesor ficticio.
- **`withdraw`**: la clase retira un paquete **no despachado**. Aquí hubo
  transporte real y producto real; retirarlo habría borrado una entrega existente.
- **Re-despachar el mismo trabajo**: habría fabricado un encargo para un trabajo
  ya hecho y entregado.
- **Usar el CLI instalado** para la comprobación: verifica contra **otro** conjunto
  de fuentes (su copia instalada, previa al cambio) y por eso «pasaría». Es el
  defecto I-9 de la tabla del epic (dos copias componen paquetes distintos) y
  acreditar por esa vía sería acreditar contra bytes que no son los del paquete.

## 5. Qué evidencia NO se relajó

La sustancia del GREEN se verificó por el orquestador **antes** de acreditar:

| Medición | Resultado |
|---|---|
| `tests/test_010_002_documentary_role_integration.py` (13 tests) | **13 passed** |
| `sha256` del archivo de tests vs. el artefacto del RED | `07c919ec…` — idéntico |
| Commit tocó `tests/` | **no** (`git show --stat c0126040 -- tests/` vacío) |
| Techo de bloques estáticos | 2 passed; `TestPd13StaticBlockCeiling` passed; **no elevado** |
| Generación reproducible | `make agents` dos veces: hash del árbol idéntico (`28d66968…`) |
| Regresiones de generación, 010-001 y unicidad | **36 passed** |
| Instalación, review5 y retiro/republicación | **78 passed** |
| Especialización Odoo | **68 PASS / 0 FAIL** |

No se presenta ninguna de esas mediciones como fidelidad semántica: son control
estructural.

## 6. Defecto registrado (I-10)

**I-10 — la identidad del paquete no está pineada a sus fuentes de instrucción.**
Un encargo autorizado a modificar `skills/cdad-cycle/packets/{roles,substages}`
invalida su propio paquete en cuanto el trabajo aterriza: la admisión vuelve a
derivar el render del árbol vivo y el resultado depende de qué copia del CLI
ejecute la comprobación (defecto hermano de I-9).

**Correcciones posibles, para una unidad propia (no para 010-002):**

1. `render_packet` verifica que los `sha256` de las fuentes coincidan con los que
   el request/cabecera declara y falla con un diagnóstico distinto
   («instruction source drifted», nombrando archivo y hashes) en vez de acusar al
   paquete de alterado.
2. La admisión compara contra un render **pineado** al conjunto de fuentes
   declarado (recuperable por `git` desde el commit de publicación), no contra el
   árbol vivo.

Ninguna de las dos se implementa aquí: la spec y el plan de 010-002 no las
incluyen y agregarlas sería un cambio de alcance. Queda en el backlog del epic.

## 7. Límites y estatus de la excepción

**La excepción no se establece como práctica reutilizable.** Vale para este
despacho y por este defecto; una recurrencia exige, en este orden: (i) corregir
I-10, o (ii) una decisión explícita del dueño. El orquestador no la repetirá por
iniciativa propia ni la presentará como mecanismo admitido.

**Verificabilidad por un tercero.** Un tercero puede reproducir la autenticidad
del paquete —el `sha256` del bloque de rol declarado se recupera de `0d935bc8` y
el render coincide byte a byte con `PACKET.md`— pero **no** puede reproducir la
igualdad completa «en el estado actual», porque el estado ya avanzó: re-renderizar
hoy el paquete de T4 falla primero por desajuste del paquete activo, no por la
guarda de fuentes. La afirmación verificable es la que este documento sostiene:
*el paquete es el render canónico de las fuentes que su cabecera declara*, y esa
comprobación se hizo en la ventana declarada arriba.

**Huella temporal observable.** `dispatches/green-001-attempt01.json` (`09:45:32`)
y `receipt.json` (`09:45:48`) son anteriores a la restauración del bloque de rol
(`09:45:48.129`) y al **registro de la entrega** `tdd-green-t4` (`09:45:58`), que
no es una restauración. Los sellos son consistentes con la secuencia de §3 y
ninguna operación posterior la contradice.

**Límite de esa huella.** Los sellos viven en `.cdad/`, ignorado por git, y en
`docs/.cdad-state.json`: **no son recuperables desde un clon**, solo desde esta
copia de trabajo. La igualdad completa del render tampoco es reproducible hoy,
porque el estado ya avanzó. Lo que sí es reproducible desde el repositorio es la
autenticidad del paquete respecto de las fuentes declaradas, recuperables de
`0d935bc8`.

Esta desviación no autoriza publicar, hacer push ni actualizar la instalación
global. No convierte la acreditación en aprobación de ningún gate: el despacho
queda registrado y la recepción sigue con `semantic_status: pending`.
