### Despacho por ruta C y contexto de ejecución declarado (epic 010, 2026-10-31)

- **El contexto de ejecución se declara, no se infiere.** Toda publicación nueva de un
  encargo incorpora `execution_context` en `REQUEST.json` **y** en la cabecera de
  `PACKET.md`, con la forma exacta `.cdad/executions/<execution_id>/execution.json`,
  donde `<execution_id>` coincide con el del request y cumple el dominio de nombre
  plano ya usado por `_load_execution_context`. Se rechazan localizadores absolutos,
  vacíos, con escapes, con componentes alternativos o en otra ubicación, incluida una
  copia byte-idéntica: la ubicación canónica es parte del contrato, no una convención.
  El campo es opcional en el esquema para conservar la admisión de requests
  históricos, pero omitirlo **no** habilita a nadie a publicar un encargo nuevo v1.
  `.cdad/execution.json` no pertenece al dominio del campo: su uso explícito queda
  solo en la vía histórica. Base: `010-004` §4.1, PC-04..PC-07, INV-12.
- **Toda preparación nueva usa v2; la selección implícita v1 sin policy quedó
  cerrada.** La regla cubre preparación ordinaria, sucesores de reemplazo y
  recuperaciones que publiquen generación nueva, aunque el trabajo venga de un
  proyecto viejo o conservase el objetivo de un encargo anterior; un sucesor nuevo
  declara el campo aunque su predecesor histórico no lo tuviera, y no se añade
  retrospectivamente al predecesor. El delta medido: `_select_execution` devolvía v1
  sin policy y `prepare` consumía esa selección; ahora se rechaza la v1 explícita y la
  implícita antes de publicar. Reconocer, validar o reemitir lo histórico **no**
  autoriza adopción hacia adelante. Base: `010-004` §4.1, PC-04, PC-07b.
- **Ruta C es el vehículo de despacho que no retranscribe el cuerpo.** `render
  --project-root <raíz> --request <REQUEST.json> --route C` emite una línea literal
  `Route C — explicit file backup` y un único bloque JSON con `project_root`,
  `packet_id`, `execution_id`, `execution_context`, `request`, `packet` y `contract`
  (con todos sus campos y su digest); no reproduce instrucciones, objetivo, entradas,
  scopes, invariantes ni cuerpo, no usa el marcador de cabecera de A y no modifica
  archivos ni estado. Antes de emitir exige: request designando el archivo **publicado**
  en `.cdad/packets/<packet_id>/REQUEST.json` dentro de la raíz; contexto **v2**
  canónico (un v1 recibe diagnóstico explícito, sin intentar buscar uno v2 ni
  convertirlo); request validado contra ese contexto; y `PACKET.md` publicado completo
  verificado con `verify_published_packet`. El receptor resuelve las referencias
  project-relative contra `project_root`; para iguales archivos, raíz y configuración
  la salida es determinista. Base: `010-004` §4.2, PC-01/PC-02.
- **El intake del rol es exclusivo y completo, y esa exclusividad está escrita en la
  fuente y en los derivados.** Se cuentan primero los marcadores A: exactamente una
  apertura y su cierre son necesarios, y **el cierre JSON termina la cabecera, no el
  paquete**; la comparación comprende del marcador inicial al final del paquete
  recibido, incluido todo el cuerpo, sin reconstruir ni normalizar. Un dispatch con
  identificación C **y** paquete inline A se rechaza por mezcla aunque el inline
  coincida; C no requiere cuerpo inline, no busca otro paquete si el nombrado falla y
  exige contexto v2; un cuerpo parcial no sustituye la identificación; marcadores
  duplicados no se resuelven eligiendo uno; y un prompt que afirma ser paquete sin
  satisfacer su admisión se rechaza sin pasar a legacy. Las lecturas de control-plane
  no amplían el scope de producto. Base: `010-004` §4.3, PC-03/PC-08b.
- **Paquete v1 activo no terminal: diagnóstico que nombra el bloqueo y escala, sin
  ruta CLI terminal.** Con un paquete v1 activo, incluido `prepared`, el resultado
  observable único es diagnosticar el bloqueo **y** la ausencia de una ruta CLI
  terminal existente, y escalar al dueño, dejando state intacto y sin preparar v1;
  no se indica «completar o fallar» como procedimiento disponible y no se añade
  migración ni withdraw v1. `--resume-packet` conserva su función de reemisión
  byte-identical bajo sus condiciones v2 actuales y no se presenta como vía universal
  de replay v1. Límite declarado y aceptado: es una **laguna** de la spec, no un
  procedimiento inexistente disfrazado. Base: `010-004` §4.1/§4.5, PC-07b, N-2.
- **Precedencia de diagnósticos de configuración sobre el rechazo de contexto.** Cuando
  una preparación nueva encuentra a la vez (a) policy ausente, mal formada o existente
  pero no-archivo, o autoridad/aprobación/pin inválidos y (b) un contexto v1 explícito
  o implícito, **primero se emite (a)**. El rechazo de (b) se conserva completo: la
  operación falla igual, sin efectos persistentes, sin publicar, sin binding v2, sin
  copiar/convertir/reubicar el contexto y sin fallback legacy. La precedencia no se
  aplica a la inversa ni crea una jerarquía general de diagnósticos: solo impide que
  la causa accionable quede inalcanzable detrás del rechazo de versión/ubicación. No
  reabre la spec ni edita el plan; N-4/N-5/N-6 siguen postergados. Normativo en
  `docs/specs/010-004-packet-dispatch-ergonomics/decision-diagnostic-precedence.md`.
- **Integridad, observabilidad y fidelidad son tres hechos distintos.** Un request
  validado igual al render acredita integridad publicada, no el mensaje recibido por el
  runtime; bytes escritos a stdin acreditan entrega a esa frontera, no recepción;
  contrastar el resultado con contrato y fuentes acredita fidelidad examinada, con
  límites; un recibo acredita recepción según su contrato, no aprobación semántica. La
  falta de observabilidad de entrega, por sí sola, no demuestra corrupción ni obliga a
  repetir el trabajo; sí se mantiene el rechazo ante divergencia comprobada o
  autoridad inválida. Base: `010-004` §2.2/§2.3/§4.7, PC-10/PC-11.
- **Lo que esta convención NO promete.** No intercepta prompts nativos ni herramientas:
  es admisión documental. Las guardas de intake comprueban tokens estables y su
  supervivencia en los derivados, no conducta de un modelo (R3: la inversión semántica
  de la regla A+C siguió en verde). No hay exportación independiente del mensaje
  recibido ni conexión mecánica renderer→herramienta: C evita retranscribir, no prueba
  recepción. La unidad está cerrada en el repositorio y **no vigente en la instalación**
  (R1): el despacho real usa la toolchain del repo y publicar es decisión del dueño.
  Normativo en `docs/specs/010-004-packet-dispatch-ergonomics/spec.md` (PC-01..PC-12);
  este archivo no re-enuncia las postcondiciones.