# Evidencia semántica — 010-003-documentary-pilot

Registro 2 de los tres que exige PC-14. Reúne, en orden y enlazados, el informe
original del desafío, la auditoría de lecturas, el contraste posterior, la
revisión del producto corregido y su re-verificación. No incluye la aceptación
funcional (registro 3) ni las mediciones de tests (registro 1).

## 1. Cadena de custodia

| Pieza | Artefacto durable | SHA-256 (16) | Commit o sesión |
|---|---|---|---|
| Contrato aprobado | `spec.md` v5 | `f2dce9e0d1eb35d9` | pineado por el gate `7a23f46c…` |
| Plan aprobado | `plan.md` v6 | `49ce6f813aeb4e0b` | pineado por el mismo gate |
| Fijación del desafío | `preparation-record.md` | `e84f1e2712596738` | registro versionado en `4c822805`; artefactos en `cd2d57b3` |
| Informe original T5 | `challenge-review.md` | `f2598dc1b13eba1f` | commit `d2307c42`, sesión `<session>` |
| Auditoría y contraste | `challenge-contrast.md` | `cb43ad07b8736c9b` | commit `d2307c42` |
| Revisión del producto | `product-review.md` | `a037609bbcb324d9` | sesión `<session>` |
| Corrección T7 | `tdd-t7-review-fix.md` + producto | `0a0ecf0adb92d9cd` | commit `6596e804`, sesión `<session>` |
| Re-verificación T7 | `product-review-002.md` | `f68f2ba3d0288d73` | sesión `<session>` |

Los request y paquete validados de cada encargo, los recibos de entrega y la fila
de sesión del store del runtime están copiados bajo `evidence/t5/`, `evidence/t6/`
y `evidence/t7/`. Esas copias son las que hacen recuperable el despacho sin
depender de `.cdad/`, que no se versiona.

## 2. Independencia del ensayo T5

- **Sesión distinta** de la del productor y de la del autor de la clave:
  `<session>`, registrada en `evidence/t5/t5.session.json`
  con agente, modelo y directorio tomados del store en modo lectura.
- **Insumos recibidos:** contrato, inventario, las dos fuentes y el candidato;
  más la norma documental y tres referencias de método declaradas. No recibió la
  clave, el producto, `structural/`, `discovery.md` ni informes reveladores.
- **Objeto declarado:** solo el candidato frente al contrato, el inventario y las
  fuentes; el diff y las operaciones git que muestran contenido quedaron fuera
  (decisión BN-1).
- **Auditoría de lecturas declaradas:** sin lectura invalidante. Las referencias
  de método se registraron sin invalidar; no se observó lectura de `product/`,
  `oracle/`, `structural/`, `discovery.md` ni de informes. El detalle está en
  `challenge-contrast.md` §1.
- **Primer informe cerrado antes de revelar:** el informe se materializó en
  `challenge-review.md` y recién después se escribió el contraste. La secuencia
  está en los commits: `d2307c42` contiene ambos, con el informe íntegro tal como
  se recibió.
- **Límite declarado:** la auditoría examina las lecturas declaradas y las
  operaciones observadas; no prueba la ausencia de accesos no registrados ni
  constituye aislamiento técnico. La exclusión es contractual y de alcance.

## 3. Detección acreditada

El primer informe, sin clave y sin producto, identificó y fundamentó las tres
clases comprometidas:

| Clase | Hallazgo | Ubicación en el candidato | Fundamento contra el corpus |
|---|---|---|---|
| Afirmación presentada como hecho sin respaldo | F-1 | sección «Revisión del proceso» | ningún fragmento de `s1` ni `s2` trata revisión periódica, encuesta ni satisfacción |
| Contradicción omitida | F-2 | sección «Aprobación de casos límite» | `s1-f02` (Jefe de Registro con visto bueno de Cumplimiento) frente a `s2-f03` (solo Dirección de Operaciones); el candidato afirma consenso |
| Referencia existente que no sostiene | F-3 | sección «Archivo» | el enlace resuelve a `s1-f03`, que trata el plazo; el respaldo real está en `s1-f04` |

El contraste con la clave dio **tres coincidencias y cero omisiones**, más tres
extras que la clave no enumeraba (`challenge-contrast.md` §2 y §3).

## 4. Producto corregido

- **T6** revisó el producto contra contrato, inventario, fuentes, candidato,
  clave y contraste: los tres defectos quedaron corregidos y apareció un
  bloqueante nuevo, **F-1-deadline** —la divergencia sobre el inicio del plazo no
  estaba declarada—, que el producto no podía dejar pasar (`product-review.md`).
- **T7** corrigió: atribuyó cada inicio a su fuente, declaró que el corpus no
  aclara el registro posterior de una solicitud completada, agregó P-02 con todos
  los campos de PC-12 y adoptó O-1, O-2 y N-1; commit `6596e804`, que desciende de
  `7fcca219`.
- **Re-verificación de todo el diff** (`product-review-002.md`): F-1 cerrado, sin
  regresiones, las tres correcciones y las citas intactas, 8 focales y 40
  regresiones verdes. Dos observaciones opcionales (N-2, N-3) quedan como
  límites declarados, no como deuda.

## 5. Desviaciones declaradas

1. **El request de T5 no citó los commits de fijación.** El contrato (§2.3, y
   PC-03) exige que el request de T5 identifique el commit de preparación y el del
   registro. El request despachado no los cita; lo detectó el propio reviewer y
   quedó registrado en `challenge-contrast.md` §4.1. La fijación existe y es
   comprobable —`cd2d57b3` y `4c822805`, ambos antecesores de `d2307c42`—, pero la
   cláusula de forma del request no se cumplió. No se re-despacha: el ensayo es de
   un solo tiro y el primer informe ya estaba cerrado. Se registra como
   no conformidad declarada y se traslada al backlog del epic (I-15).
2. **Lectura de la norma por `bash` en el AUDIT de T2.** Desviación de I-8,
   registrada y decidida en `audit-reading-deviation-2026-10-31.md`; no afectó la
   sustancia del mapeo, que una sesión distinta verificó.
3. **El `spec.md` conserva la línea de estado «pendiente de revisión y
   aprobación».** La aprobación se registró en el estado y en el gate, no
   editando el contrato pineado; misma convención que `010-002`.

## 6. Confidencialidad de la clave

`product-review.md` y `product-review-002.md` se fundamentan contra las fuentes y
la clave sin transcribirla: la comprobación automática sobre las oraciones de la
clave (más de 40 caracteres) dio **0 coincidencias** en ambos informes. La clave
sigue siendo insumo sólo de T6 y de la re-verificación de T7, nunca del
implementer.

## 7. Límites que este registro declara

- La muestra es **sembrada y sintética**; el contrato anuncia tres defectos y sus
  clases. Se acredita **detección sobre un desafío declarado**, no detección a
  ciegas.
- Se acredita sobre **esta** muestra: no se demuestra detección infalible,
  conducta general de modelos, errores espontáneos del productor ni fidelidad de
  un documento de cliente.
- La independencia es **procedimental y de alcance**, no aislamiento técnico.
- El control estructural no acredita fidelidad semántica; esa fidelidad la
  sostienen la revisión de T6 y la re-verificación de T7.
