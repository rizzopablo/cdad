# Enmienda 007-003 §2.3.1 — reanclaje de historia legada

<!-- materializado de cdad-architect ses_e8d1a4be4ffem4SA7tR8Iy5Wuq ronda 2 (excepción de arranque, sin recibo) -->

**Estado:** aprobada por el orquestador (HITL delegada; el dueño autorizó la reparación el 2026-10-25) tras review ronda 2 APTO CON AJUSTES; ajustes de §10 aplicados. No autoriza por sí sola una reparación concreta.  
**Fecha:** 2026-10-25.  
**Contrato enmendado:** `docs/specs/007-003-continuity-at-edges/spec.md` §2.3.1, con ajustes a §2.1 y §2.5.  
**Decisión recibida:** adoptar el reanclaje explícito, sujeto a aprobación y verificación.

## 1. Motivo y evidencia

La lectura de cuerpos legados no demuestra su pertenencia histórica. El contrato actual exige enlaces `prev` hasta el génesis (§2.3.1, líneas 87–97).

Casos aportados por el orquestador:

| Caso | Forma real | Estado operativo |
|---|---|---|
| CDAD, `exec-007-004-termination-not-success-001` | Cinco cuerpos **sin `prev`**, incluida la cabeza `begin`, posición 5, digest `08fbdc07…` | Paquete `prepared`, nunca registrado como despachado |
| Otro proyecto activo | 265 cuerpos: 264 legados y cabeza moderna sobre antecedente legado; existen dos `begin` del paquete preparado con `attempt=1` | Paquete `prepared`, nunca registrado como despachado |

Son datos recibidos del orquestador; esta entrega no constituye una nueva medición. La aprobación concreta debe citar el diagnóstico original y contener el digest completo, nunca su abreviatura.

El código confirma tres obstáculos:

- `_chain_links` detiene la demostración ante ausencia de `prev` (`skills/cdad-cycle/scripts/cdad_continuity.py:1683–1747`).
- `_same_key` y el rechazo de `begin` divergente impedirían escribir sobre un ancla con la misma identidad operativa (`931–935`, `970–989`).
- `_detect_split_brain` inspecciona todos los cuerpos, incluidos legados y huérfanos (`1842–1875`); `verify-begin` lo invoca en `1128`.

**Decisión:** abrir un segmento demostrable nuevo con frontera histórica explícita y aprobada. No relajar globalmente la integridad ni migrar cuerpos. La frontera debe distinguir los cuerpos archivados de cualquier divergencia posterior, incluidos huérfanos modernos.

## 2. Texto normativo de §2.3.1

Se conservan almacenamiento, digest físico, límites de bytes y reglas generales de coherencia. Se sustituyen las reglas de pertenencia e historia de las líneas 89–90 y se añade:

### 2.3.1.a Génesis de reanclaje

El comando explícito `reanchor` puede sustituir una cabeza cuya historia no es demostrable por ausencia de `prev`. Conserva `execution_id`, publica un cuerpo nuevo y reinicia la posición de continuidad en 1.

El cuerpo completo conserva los campos obligatorios existentes y añade:

```json
{
  "record": "reanchor",
  "prev": null,
  "legacy_anchor": {
    "execution_id": "<misma ejecución>",
    "head_sha256": "<digest completo de la cabeza sustituida>",
    "head_seq": 5,
    "reason": "<motivo no vacío>",
    "approval_ref": {
      "path": "docs/decisions/legacy-reanchor.md",
      "sha256": "<digest del archivo aprobado>"
    }
  },
  "pre_anchor_bodies": [
    "<digest completo de un cuerpo existente antes de reanclar>"
  ]
}
```

`pre_anchor_bodies` es la lista ordenada lexicográficamente, sin duplicados, de **todos los cuerpos de esa ejecución presentes al aprobar la frontera**, no sólo los alcanzables. Cada entrada debe corresponder a un cuerpo íntegro en el almacenamiento existente.

La cabeza nueva declara `seq: 1`, `record: "reanchor"` y `prev_checkpoint_sha256: null`. `seq` no se añade al cuerpo.

El inventario forma parte del cuerpo y su digest físico; no crea otro almacén. Su digest de aprobación se calcula sobre el JSON UTF-8 compacto de la lista ordenada, sin espacios ni salto final.

### 2.3.1.b Identidad operativa y primer `begin`

El ancla conserva `packet_id` y `attempt` de la cabeza sustituida como **identidad contextual**, no como un `begin` ni como reserva de esa clave.

Un cuerpo `record: "reanchor"`:

- no cuenta como candidato de conflicto entre `begin`;
- no satisface `verify-begin`;
- no acredita un cierre ni un antecedente de evidencia.

La comparación de repetición de `begin` no se aplica contra una cabeza `reanchor`, aunque coincidan `(execution_id, packet_id, attempt)`. El primer `begin` válido publica posición 2 con `prev` apuntando al ancla, conservando las validaciones ordinarias de request, paquete y autoridad.

Después de ese primer `begin` rigen las reglas ordinarias de repetición y split-brain. Un `begin` divergente posterior bajo la misma clave se rechaza. No se renumera `attempt` para evitar el conflicto histórico.

### 2.3.1.c Frontera y detector de divergencias

Desde una cabeza reanclada se recorre `prev` hasta el génesis `reanchor`. Ese recorrido debe ser íntegro y decrecer exactamente hasta posición 1.

`legacy_anchor` no es un enlace `prev`. Los cuerpos inventariados permanecen conservados y explícitamente fuera del segmento demostrable nuevo; no acreditan sus `begin`, cierres ni evidencia.

Tras reanclar, el detector:

1. Valida primero la cadena vigente y su ancla.
2. Excluye del conjunto operativo **únicamente** los digests incluidos en `pre_anchor_bodies`, comprobando sus bytes.
3. Excluye el propio registro `reanchor` como candidato `begin`.
4. Aplica las reglas existentes de divergencia a todos los demás cuerpos de la ejecución y paquete, incluidos los huérfanos no alcanzables.

Por tanto, los dos `begin` anteriores del otro proyecto pueden archivarse mediante la aprobación exacta de esa frontera. Un cuerpo divergente creado después, aunque sea huérfano, no queda excluido por antigüedad declarada, fecha, ausencia de `prev` ni falta de alcanzabilidad.

El inventario no cambia después de publicar. Un cuerpo nuevo con enlace hacia la historia archivada no se incorpora al segmento válido ni puede habilitar operaciones. La ausencia de ancla conserva el alcance previo del detector.

El reanclaje no permite encubrir corrupción: un enlace moderno presente pero inválido, cuerpo ausente, digest incorrecto o ciclo produce rechazo. Sólo la falta histórica de `prev` habilita esta excepción.

## 3. CLI

```text
cdad_continuity.py reanchor
  --project-root ROOT
  --execution-context EXEC.json
  --expected-head SHA256
  --approval-ref PATH
  --reason TEXT
  [--json]
```

Todos los flags son obligatorios salvo `--json`. La ejecución se obtiene del contexto. El productor calcula inventario, referencias, `prev`, secuencia y digests; no acepta sustitutos proporcionados por el usuario.

Salida JSON de éxito:

```json
{
  "execution_id": "<id>",
  "record": "reanchor",
  "body_sha256": "<digest del ancla>",
  "seq": 1,
  "legacy_anchor": {
    "execution_id": "<id>",
    "head_sha256": "<cabeza sustituida>",
    "head_seq": 5,
    "reason": "<motivo>",
    "approval_ref": {
      "path": "docs/decisions/legacy-reanchor.md",
      "sha256": "<digest>"
    }
  },
  "pre_anchor_inventory_sha256": "<digest del inventario>",
  "idempotent": false
}
```

Sin `--json`, devuelve diagnóstico legible con las mismas identidades.

| Código | Significado |
|---|---|
| `0` | Publicación o reconocimiento idempotente |
| `1` | Rechazo de contrato, integridad, autoridad, aprobación o precondición; motivo por `stderr` |
| `2` | Argumentos inválidos o incompletos |

Los rechazos previos a publicación no escriben. La publicación reutiliza cuerpo inmutable y sustitución de cabeza existentes; no promete una transacción nueva entre ambos.

## 4. Precondiciones, repetición y rechazos

Antes de publicar:

1. Contexto, ejecución y cabeza existen y son coherentes.
2. `--expected-head` coincide con el digest íntegro de la cabeza vigente.
3. Existe aprobación mecánicamente válida conforme a §5.
4. La autoridad existente no está expirada ni revocada; una delegación desconocida o no comprobable no se acepta como delegación vigente.
5. Se valida todo el tramo moderno alcanzable hasta encontrar un cuerpo sin `prev`. Cabeza totalmente legada y cabeza moderna sobre legado son admisibles.
6. El inventario actual coincide con el digest aprobado. Todos sus cuerpos son legibles, íntegros y pertenecen a la ejecución.
7. El paquete está `prepared`, sin despacho canónico, recibo durable, materialización ni disposición que implique efectos registrados. Una señal inconclusa bloquea la reparación.
8. Antes de sustituir la cabeza se vuelven a comprobar cabeza esperada e inventario. El contrato sigue siendo serial; no introduce concurrencia general.

La existencia de candidatos históricos divergentes **no bloquea por sí sola** el reanclaje: deben quedar identificados en el inventario exacto aprobado. No se elige uno como ganador.

Se conservan todos los cuerpos anteriores byte a byte. No se modifica estado, request, paquete, despacho ni recibos. No existe `--force`.

**Idempotencia:** tras validar íntegramente el segmento vigente, se reconoce su ancla cuando apunta a `--expected-head` y coinciden ejecución, motivo, ruta normalizada y bytes de aprobación. Devuelve la identidad original, incluso tras checkpoints posteriores, sin recalcular la frontera con cuerpos posteriores ni escribir.

Una aprobación o motivo distintos para esa misma ancla producen conflicto. No se reconocen anclas huérfanas como éxito. Una cadena ya demostrable sin ese replay no puede reanclarse mediante esta excepción.

## 5. Aprobación mecánica y autoridad

`--approval-ref` debe resolver a un archivo regular dentro del repositorio mediante ruta relativa segura, sin escape por `..` o symlinks.

Frontmatter obligatorio:

```yaml
---
reanchor_execution_id: "<execution_id exacto>"
reanchor_head_sha256: "<digest completo esperado>"
reanchor_inventory_sha256: "<digest del inventario exacto>"
approved_by: "<aprobador declarado>"
approved_at: "2026-10-25"
---
```

El cuerpo del documento debe autorizar expresamente el reanclaje, describir el motivo y citar el diagnóstico y, cuando corresponda, la delegación existente.

### Responsabilidad del CLI

Comprueba determinísticamente:

- campos obligatorios únicos, tipos y valores no vacíos;
- fecha válida `YYYY-MM-DD`;
- igualdad exacta de ejecución, cabeza e inventario;
- admisibilidad de la ruta y digest de sus bytes;
- vigencia de la autoridad mediante las fuentes existentes.

No verifica que el nombre de `approved_by` corresponda realmente a una persona ni que esa persona haya producido el archivo. La igualdad de campos no autentica procedencia.

Una delegación expresamente expirada o revocada se rechaza. Si no hay delegación registrada y la decisión procede directamente del dueño, su ausencia **no equivale a expiración**: se sigue la ruta existente de aprobación directa, sin fabricar una delegación.

### Responsabilidad del gate del orquestador

Antes de invocar la reparación, verifica mediante el proceso de aprobación vigente:

- procedencia e identidad del aprobador;
- que es el dueño o posee delegación suficiente;
- que la decisión autoriza exactamente esa frontera;
- vigencia y ausencia de revocación de la delegación, si se invoca.

Si no puede acreditarlo, no ejecuta. El CLI no sustituye ese gate ni `_gate_authority` se presenta como verificador de identidades.

No se crea registro de aprobadores, firma o mecanismo nuevo de autoridad. Aprobar esta enmienda y autorizar una reparación concreta son decisiones distintas.

## 6. Consumidores y ajustes puntuales

### §2.1 — añadir tras la línea 37

`reanchor` no satisface `verify-begin`. Debe publicarse y verificarse un `begin` nuevo en posición 2 antes del transporte. La coincidencia de clave contextual con el ancla no activa el rechazo de repetición divergente. El detector de split-brain usa la frontera exacta definida en §2.3.1, sin omitir huérfanos posteriores.

### `_chain_links` y `_require_head_coherence`

Mantienen las comprobaciones de identidad, digest, posición y enlace. Admiten como génesis el registro `reanchor` válido, con cabeza posición 1 cuando sea vigente. Validan estructura y frontera declarada; no atraviesan `legacy_anchor` como enlace.

No hay límite arbitrario de profundidad ni excepción de coherencia por tratarse de una reparación.

### `resume` y `reconcile`

Son de sólo lectura y recorren **toda la cadena vigente** hasta el génesis, no sólo cabeza y predecesor inmediato. Verifican también el alcance de divergencia definido en §2.3.1.c.

Exponen ancla y diagnóstico «historia anterior conservada, no demostrable». `reconcile` conserva sus clasificaciones de efectos: el ancla no equivale a despacho, recepción ni cierre. Una corrupción interior o divergencia operativa impide devolver éxito utilizable.

### §2.5 — añadir tras la línea 160

El reanclaje no importa evidencia previa como `vigente` ni permite antecedentes a través del ancla. Conserva objetivo, decisiones y contexto como reconstrucción con procedencia histórica no demostrable. La evidencia acreditada del segmento nuevo comienza vacía; la histórica permanece intacta en sus cuerpos.

Una acreditación nueva exige verificación nueva conforme a §2.5. La aprobación del reanclaje no aprueba resultados ni rehabilita evidencia.

## 7. Postcondiciones y aceptación

### Fixtures obligatorios

- **F5:** cinco cuerpos sin `prev`; cabeza `begin` legada, posición 5; paquete `prepared`, sin efectos registrados.
- **F265:** 264 cuerpos legados y cabeza moderna en posición 265; incluye los dos `begin` anteriores del paquete con `attempt=1`; paquete `prepared`, sin efectos registrados.
- **Fposterior:** ancla válida seguida de varios enlaces modernos; permite introducir una rotura interior y un `begin` divergente huérfano no inventariado.

Los inventarios, aprobaciones, requests, intentos y recibos son archivos reales con la forma de producción. Los tests invocan CLI, no helpers internos.

| PC | Postcondición observable | Test estable |
|---|---|---|
| **PC-R1** | En F5, la secuencia `reanchor → begin → verify-begin → record → receive/cierre` completa con éxito. El ancla queda en posición 1 y el nuevo `begin` en 2, incluso conservando paquete e intento. Los cinco cuerpos históricos y el paquete preparado no son alterados por `reanchor`. | `test_reanchor_legacy_prepared_preserves_history` |
| **PC-R2** | En F265, el mismo recorrido completo tiene éxito pese a los dos `begin` históricos de `attempt=1`, incluidos en la frontera aprobada. `resume` y `reconcile` reconocen el segmento nuevo y conservan el diagnóstico histórico. | `test_reanchor_long_mixed_chain_starts_demonstrable_segment` |
| **PC-R3** | `verify-begin` sobre el ancla rechaza; tras el nuevo `begin` devuelve éxito. Un `begin` divergente posterior bajo la misma clave se rechaza tanto al escribirlo como, si aparece como cuerpo huérfano no inventariado, al verificar o reconciliar. Los históricos no sirven para cerrar recepción. | `test_reanchor_requires_fresh_begin_before_transport` |
| **PC-R4** | Repetir la reparación inmediatamente o tras checkpoints devuelve la identidad original e `idempotent=true`, sin cambios. Motivo o aprobación divergentes producen conflicto; los cuerpos posteriores no amplían el inventario archivado. | `test_reanchor_replay_is_idempotent_and_conflicts_fail` |
| **PC-R5** | Por CLI: aprobación discordante, inventario cambiado, delegación expirada o revocada, cabeza incorrecta y efectos registrados devuelven `1` sin cambios; argumentos incompletos devuelven `2`. Una decisión directa del dueño sin delegación registrada, con campos válidos y gate de procedencia satisfecho, puede completar la reparación; ausencia de delegación no se confunde con revocación. | `test_reanchor_preconditions_fail_closed` |
| **PC-R6** | Una rotura posterior al ancla, situada fuera de cabeza y predecesor inmediato, hace fallar `verify-begin`, `resume` y `reconcile`. Una continuación larga válida no falla por corte artificial. `reanchor` no oculta esa corrupción moderna. | `test_reanchor_consumers_reject_post_anchor_corruption` |
| **PC-R7** | La evidencia histórica conserva sus bytes, pero no aparece acreditada como vigente en el segmento nuevo. Un UPDATE que intente usarla como antecedente cruzando el ancla se rechaza. | `test_reanchor_does_not_rehabilitate_legacy_evidence` |

PC-R5 distingue la prueba CLI de estructura/vigencia de la evidencia del gate de procedencia: los tests no atribuyen al CLI autenticación de identidad.

**Aceptación:** PC-R1..PC-R7 verificadas, incluidos ambos recorridos completos de recepción/cierre, regresión proporcional verde y aprobación de la enmienda antes de modificar el contrato aprobado.

## 8. Fuera de alcance

- Salida general para paquetes `prepared` abandonados.
- Cancelación, sustitución o transición de paquetes.
- Migración o reconstrucción de enlaces históricos.
- Borrado, reescritura o garbage collection.
- Reanclaje de corrupción moderna o efectos ya registrados.
- Nuevos mecanismos de autoridad, transporte o almacenamiento.
- Segundo reanclaje de un segmento ya demostrable.

## 9. Documentos a alinear

**Único dueño normativo:** `docs/specs/007-003-continuity-at-edges/spec.md` §2.3.1, con las adiciones expresas a §2.1 y §2.5.

Tras aprobación:

- `skills/cdad-cycle/references/continuity.md`: interfaz, frontera y recuperación por referencia al contrato.
- Fuente canónica del orquestador y derivados generados: detener transporte ante legado, verificar procedencia de la aprobación y ejecutar el recorrido aprobado; nunca auto-reanclar.
- Esquema del cuerpo y validadores: extensión aditiva `record=reanchor`, `legacy_anchor` y `pre_anchor_bodies`; sin ampliar el envelope cerrado.
- Reglas del detector y consumidores: aplicar la misma frontera normativa, sin definiciones alternativas en cada guía.

## 10. Ajustes del orquestador (review ronda 2)

**10.1 Límite de bytes del ancla (bloqueante resuelto).** El inventario se conserva inline. El cuerpo `reanchor` sin el campo `pre_anchor_bodies` debe cumplir el límite ordinario (`DEFAULT_MAX_BYTES`, o `--max-bytes` si existe); el límite efectivo del ancla es el ordinario más el tamaño canónico exacto del campo, y se registra en el `max_bytes` existente del envelope. La excepción no se propaga a `begin`, checkpoints, cierres ni proyecciones, y no hay incremento libre. PC-R2 se cumple con opciones predeterminadas, y un cuerpo ordinario sobredimensionado sigue rechazándose (caso añadido a PC-R2).

**10.2 Obtener la frontera antes de aprobar (usabilidad).** `reanchor --dry-run` es de sólo lectura: no exige `--approval-ref` ni `--reason`, valida las mismas precondiciones de integridad (§4.1, 4.2, 4.5, 4.7) y emite `execution_id`, `head_sha256`, `head_seq`, cantidad de cuerpos y `pre_anchor_inventory_sha256`, sin escribir nada. Con esa salida se redacta el frontmatter de §5. Rechazos con los mismos códigos (`1`/`2`). Caso añadido a PC-R5: `--dry-run` no escribe y su digest coincide con el que después verifica la publicación.
