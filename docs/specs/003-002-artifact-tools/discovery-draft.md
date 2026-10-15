# Discovery — 003-002-artifact-tools

## Resultado mínimo viable

Recibir los bytes originales devueltos por una ejecución de rol ya identificada
por 001, persistirlos de forma inmutable y atómica, y devolver un recibo
mecánico breve. Repetir la misma recepción devuelve el mismo recibo sin duplicar
el payload; intentar reutilizar la identidad con bytes distintos falla. El
recibo deja el juicio semántico explícitamente pendiente para el re-entry CDAD.

002 no genera ni resume el resultado, no aprueba su contenido y no materializa
por sí solo `spec.md`, `review.md`, `test-audit.md` o Memory Bank. El
orquestador sigue copiando desde el original persistido hacia el artefacto
canónico después de validar el rol y obtener las aprobaciones aplicables.

## Dependencias verificadas de 001

002 debe consumir, sin redefinirlos:

- `execution.id`, `epic_id`, `feature_id`, runtime/scope/model policy y
  authority binding validados por `validate-state`;
- `active_packet.id`, rol, subfase, status, versión y hash del contrato;
- metadata canónica del paquete y `validate-packet`;
- clasificación de paths y scopes declarados;
- identidad separada de métricas. Un recibo no es una métrica ni reemplaza el
  registro de 001.

La recepción sólo procede para un paquete renderizado/validado y en status
`dispatched`. La transición a `completed` requiere recepción mecánica exitosa;
no significa aceptación semántica ni cierre de gate.

## Contrato de entrada pequeño propuesto

Un descriptor JSON identifica resultado y canal:

```json
{
  "schema_version": 1,
  "result_id": "result-003-001-0001",
  "execution_id": "exec-003-001-0001",
  "packet_id": "packet-003-001-0001",
  "feature_id": "003-001-role-packets",
  "source": {
    "kind": "staged-file",
    "path": "<path del inbox autorizado>",
    "sdk_message_ref": null
  },
  "claimed_artifacts": [
    {"path": "docs/specs/003-001-role-packets/review.md", "operation": "proposed-write"}
  ]
}
```

Canales mínimos:

1. `staged-file`: el core lee un archivo ya preparado en un inbox explícito,
   copia sus bytes sin decodificar/regenerar y calcula SHA-256 y longitud.
2. `sdk-message-ref`: referencia opaca del runtime más un export exacto a
   staged file realizado por un adaptador pequeño. El core persiste los bytes
   exportados y liga el ref al recibo; no inventa una API universal para leer
   conversaciones ni afirma que el runtime certificó autoría si no ofrece esa
   prueba.

Los payloads temporales usados durante construcción son sólo transporte. El
resultado durable es la copia inmutable bajo control de 002; los artefactos
finales siguen siendo copiados/materializados por el orquestador.

## Persistencia e idempotencia propuestas

Clave única: `(execution_id, packet_id, result_id)`.

Una recepción construye en un directorio hermano temporal:

```text
payload.bin       bytes originales
receipt.json      identidad, canal/ref, sha256, bytes, checks mecánicos
```

Después de escribir y sincronizar ambos archivos, renombra el directorio
temporal al destino final en una sola operación del mismo filesystem.

- Interrupción antes del rename: el destino final no existe; el retry puede
  limpiar/reemplazar sólo su temporal identificado.
- Interrupción después del rename: el retry encuentra el resultado completo.
- Mismo key + mismo digest/longitud/source identity: devuelve el recibo ya
  existente byte a byte.
- Mismo key + bytes o source identity distintos: conflicto, sin sobrescritura.

No hace falta una base de datos, cola ni lock distribuido en el MVP. La spec
debe resolver la conducta frente a dos procesos locales concurrentes, pero un
rename exclusivo y comparación posterior parecen suficientes para una única
raíz de proyecto.

## Recibo mecánico, separado del juicio

El recibo mínimo debería incluir:

```text
schema_version
result_id / execution_id / packet_id / feature_id / role / substage
source.kind / sdk_message_ref opcional
payload_sha256 / payload_bytes
stored_payload_ref
packet_validation: passed
identity_validation: passed
claimed_scope_validation: passed | failed | unknown
semantic_status: pending
received_at
```

`claimed_scope_validation` sólo compara `claimed_artifacts` con el write scope
del paquete. No prueba que esos sean todos los archivos modificados ni que el
contenido sea correcto. La comprobación real de changed files y las
validaciones específicas por rol permanecen en re-entry.

`semantic_status` no puede pasar a approved por efecto de `receive`. Architect,
reviewer, audit y scribe continúan entregando FINAL TEXT; el orquestador valida
estructura/contenido y materializa. Tests e implementación continúan requiriendo
diff/commit/suite según el rol. Un recibo sólo demuestra identidad, persistencia
y checks mecánicos declarados.

## Superficies mínimas

- Nueva implementación instalable junto a 001, por ejemplo
  `skills/cdad-cycle/scripts/cdad_result.py`, con wrapper fino en `scripts/`.
- Schemas pequeños para descriptor y receipt bajo
  `skills/cdad-cycle/assets/`.
- Extensión acotada del state: referencia al `result_id`/receipt y status de
  recepción; sin guardar payload ni historial creciente en `.cdad-state.json`.
- `skills/cdad-cycle/references/re-entry.md`: recibir primero, validar después,
  y materializar desde `stored_payload_ref` sin regeneración.
- Instrucciones de cierre de roles: devolver FINAL TEXT al canal capturable y
  una identidad de resultado; no pegar/resumir como sustituto del original.
- Instalación/smoke: ejecutar desde un proyecto consumidor como el CLI de 001.

## Decisiones todavía abiertas (resolver en brainstorm/spec)

1. **Raíz durable e inbox:** elegir paths project-local excluidos de git o una
   raíz operativa externa. Deben soportar rename en el mismo filesystem, límites
   de tamaño y cleanup sin mezclar resultados con artefactos versionados.
2. **SDK MVP:** confirmar qué runtime ofrece un message ref estable y export de
   bytes. Si ninguno lo garantiza, aceptar `sdk-message-ref + staged export`
   como binding declarado, sin prometer fetch directo.
3. **Payload textual/binario y límites:** decidir si MVP acepta bytes arbitrarios
   o sólo UTF-8, y fijar tamaño máximo antes de copiar para evitar incorporar un
   gestor de blobs general.
4. **Concurrencia local:** definir resultado observable de dos receives
   simultáneos del mismo key: uno crea y el otro devuelve el mismo receipt, o
   conflicto sólo si sus digests difieren.
5. **Transición de estado:** decidir si receive actualiza `active_packet` en la
   misma operación o emite una actualización que el orquestador aplica. La
   primera reduce ventanas inconsistentes; la segunda preserva ownership actual
   del state. En ambos casos `completed` significa recibido, no aprobado.

## Alcance a evitar

No leer logs reales, historiales o credenciales; no construir adapters para
todos los runtimes; no resumir payloads; no automatizar aprobación; no resolver
checkpoints, loops ni recuperación global; no usar los archivos temporales de
transporte como artefactos canónicos.
