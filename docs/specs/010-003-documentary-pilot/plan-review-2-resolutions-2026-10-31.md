# Resoluciones de la segunda vuelta del plan-review — 010-003 — 2026-10-31

Resoluciones de la autoridad habilitada (ejercida por el orquestador bajo el
mandato HITL del 2026-10-30, §1 y §3) sobre `plan-review-002.md` (plan v3,
spec v2). La segunda vuelta cerró B-1..B-4, verificó O-1..O-8 y abrió **BN-1**
con una decisión que el dictamen deja explícitamente a la autoridad. Aquí se
toma esa decisión y se adoptan los seis no bloqueantes. No se relaja ninguna
promesa: todas las resoluciones endurecen la fijación o la acreditación.

## BN-1 — El bloque del reviewer manda revisar «el diff completo»: decide la autoridad

**Decisión: una precisión de `objective` e `invariants` basta, y se registra la
precedencia en la spec y en el plan.** No se editan los bloques de
`packets/{roles,substages}` (INV-06 y D-5), y T5 no espera una corrección de
`common.md`.

### Fundamento

1. **El propio bloque del reviewer ya hace prevalecer el objeto declarado.** Su
   primera frase es «assess the object the contract declares, with its declared
   form»: el bloque fija **cómo** se revisa, no **qué** se revisa. «El diff
   completo» es la forma por defecto de un contrato aprobado cuyo objeto es
   código; el objeto de T5 es un documento.
2. **No existe otra vía declarativa.** `--object-kind` sólo admite `spec` y
   `plan`; un producto documental no tiene forma declarable en el request. El
   `objective` y los `invariants` son el único lugar donde el encargo puede
   nombrar su objeto, y son la parte más específica del paquete.
3. **El bloque común y el plan ya coinciden en el alcance.** El bloque común
   manda «Read only declared inputs and scope»; el plan declara scopes disjuntos
   que excluyen `product/`, `oracle/` y `structural/`. La contradicción no está
   en el alcance —que es único— sino en la frase genérica sobre la forma del
   objeto revisado.
4. **No es un cambio de mecanismo ni una promesa nueva.** Es una declaración de
   precedencia dentro del texto del encargo, que hace operativa la exclusión que
   PC-07 ya exige. No autoriza ninguna lectura: la prohíbe con más precisión.
5. **La conducta sigue siendo auditable.** Si el reviewer lee el diff o ejecuta
   una operación git que muestre contenido, esa lectura queda declarada en la
   transcripción, la auditoría la encuentra y el ensayo se invalida. La decisión
   no crea una zona ciega: crea una obligación explícita.

### Qué debe quedar escrito

- **Spec:** el request de T5 fija como objeto revisado **sólo**
  `challenge/negative.md` frente al contrato, el inventario y las fuentes
  declaradas; el diff de la unidad y cualquier operación que muestre su
  contenido (`git show`, `git log -p`, `git diff`) quedan **fuera del objeto** y
  del alcance. La declaración específica del encargo prevalece sobre la frase
  genérica del bloque de rol sobre «el diff completo», y esa precedencia se
  registra como decisión de la autoridad.
- **Plan:** la comprobación previa al despacho de T5 («que el paquete no imponga
  otra lectura fuera de los insumos autorizados») **reconoce esa precedencia**:
  la frase genérica del bloque no cuenta como imposición porque el objeto está
  declarado en el request; cualquier otra lectura que el paquete sí imponga se
  detiene y se escala igual que hoy.
- **Auditoría:** una operación git que muestre contenido cuenta como lectura del
  objeto excluido y sigue la misma regla de invalidación.

### Límite que se declara

La precedencia es **contractual y de alcance**, no aislamiento técnico. Que el
objeto esté declarado no impide un acceso no registrado; lo que permite es
auditar lo declarado y tratar como contaminación la lectura observada. Se suma
al límite que ya declara PC-07.

## NB-1 — La fijación se adelanta a T4 y se hace fechable por un tercero

**Adoptado en sus tres huecos, con el orden de gates intacto.**

1. El commit de preparación —corpus, candidato, muestras, clave, inventario y
   **verificador**— existe **antes de T4**, no sólo antes de T5. T3 ya es
   dependencia de T4, así que el orden no cambia; lo que cambia es que la clave
   no puede moverse con el producto ya escrito.
2. El commit incluye el verificador (`tests/test_010_003_documentary_pilot.py`):
   el hash de un verificador fuera del commit no fija nada.
3. `preparation-record.md` se **versiona** (commit en el directorio de la
   feature) antes del despacho de T5. Un registro sin fecha de git no permite a
   un tercero fechar la inspección.
4. El request de T5 **cita** el commit de preparación y el commit del registro.
5. `challenge-review.md` y `challenge-contrast.md` se versionan en un commit
   **descendiente** del de preparación; la cronología queda en git, no en una
   declaración.

Las fechas de git no prueban orden por sí solas —el reloj del autor es
manipulable— pero junto con el hash de los artefactos y la inspección previa
hacen la fijación comprobable por un tercero, que es lo que PC-03 promete.

## NB-2 — PC-15 declara que la detección está cebada

**Adoptado.** PC-15 suma un límite: el contrato del ensayo declara que hay tres
defectos y sus clases, de modo que lo que se acredita es **detección sobre un
desafío declarado**, no detección a ciegas. Sin ese límite, PC-08 puede leerse
como más de lo que mide. Es la mínima redacción adicional y no cambia ninguna
otra postcondición.

## NB-3 — Fuente de la transcripción y auditoría de lecturas por git

**Adoptado.** El plan declara:

- la transcripción se recupera del **store de sesiones del runtime en modo
  lectura**, con la sesión identificada en el despacho;
- si la transcripción **no se puede recuperar**, la independencia **no se
  acredita** (no se presume por ausencia de evidencia);
- la auditoría incluye **lecturas por git que muestren contenido** (`git show`,
  `git log -p`, `git diff`), que evitan la ruta del archivo y no evitan la regla.

## NB-4 — Leer `discovery.md` invalida la independencia

**Decidido: invalida.** `discovery.md` contiene ejemplos que anticipan
respuestas y por eso está excluido de los insumos (O-8). Excluirlo de los
insumos y no de las causas de invalidación dejaría la exclusión sin efecto. La
lectura declarada de `discovery.md` antes del cierre del primer informe se
registra y **invalida el ensayo como independiente**, igual que las otras rutas
excluidas.

## NB-5 — El alcance de lectura de T4 excluye la clave

**Adoptado.** El request de T4 declara un `read_scope` acotado: contrato,
`inventory.md`, las fuentes, el candidato, el verificador y el producto
autorizado. **`oracle/` queda fuera.** El default del implementer es
`repository-read` y, sin recorte, incluiría la clave: una corrección escrita
leyendo la clave convierte la corrección en copia y debilita PC-11.

## NB-6 — La prosa de T8 se alinea con su bloque

**Adoptado.** La prosa de T8 nombra las regresiones que su entrada de
`plan-tasks` ya lista, para que el hito no dependa de que el despachante lea el
bloque.

## Lo que esta resolución no hace

No cambia el orden de gates, no crea mecanismo, no edita los bloques de
instrucciones, no autoriza publicar y no adelanta la aprobación: la spec v3 y el
plan v4 vuelven al plan-review. Las quince postcondiciones conservan su
numeración; PC-15 suma el límite de NB-2 y el resto de las precisiones se
incorporan fuera de las PC, salvo la precedencia de BN-1, que se declara donde
el reviewer la va a leer.
