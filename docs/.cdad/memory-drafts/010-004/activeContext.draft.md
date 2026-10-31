## 2026-10-31 — Feature: 010-004-packet-dispatch-ergonomics (epic 010, unidad 2/5)

**Cierre técnico declarado; NO aprobado.** `closure.md` declara el cierre de la
unidad con su evidencia de suite completa; la aprobación del cierre y del Memory
Bank es del dueño y publicar es una decisión separada. Contrato:
`docs/specs/010-004-packet-dispatch-ergonomics/spec.md`, pin
`fc6b2ccc…5d64`, aprobado por Pablo el 2026-10-30.

**Qué se cerró.** El encargo dejó de depender de retranscribir su cuerpo y el rol
dejó de inferir su contexto de ejecución: `render --route C` emite solo una
identificación (declaración + bloque JSON de 8 campos) que no reproduce
instrucciones, objetivo, entradas, scopes ni cuerpo, y exige request publicado,
contexto v2 canónico y `PACKET.md` completo verificado antes de emitir; toda
preparación nueva usa v2 y declara el localizador
`.cdad/executions/<execution_id>/execution.json` en request y cabecera; la vía
implícita v1 sin policy quedó cerrada. El intake de rol ahora declara que el
cierre JSON no termina el paquete, que la comparación va del marcador al final, y
rechaza la mezcla A+C. Doce postcondiciones (PC-01..PC-12), cuatro promesas de
problema y la de distribución.

**Decisiones relevantes.**

- **C emitida por el renderer común, no un conector nuevo.** Reutiliza la ruta C
  existente y evita inventar capacidades del runtime; se acepta explícitamente que
  C evita retranscribir pero **no prueba recepción** (spec §2.1, §4.7).
- **C es v2-only y ligada al request publicado.** El contexto v1 recibe diagnóstico
  explícito; una copia byte-idéntica fuera de `.cdad/packets/<packet_id>/` no puede
  emitir identificación. Trade-off: se conserva la diferencia de preámbulo entre
  `validate-packet` (archivo completo, sin prefacio) y las otras dos superficies, en
  vez de unificar comparadores (§4.4).
- **Localizador restringido y compartido, no rutas arbitrarias.** El campo es
  opcional en el esquema (admite histórico) pero obligatorio en toda publicación
  nueva; la matriz de §4.1 rige igual para `render`, `validate-request` y
  `validate-packet`, con rechazo del histórico sin argumento explícito y sin
  fallback por identidad. Trade-off: desde otro directorio hay que declarar la raíz
  y pasar argumentos válidos allí; una raíz explícita no reinterpreta los argumentos.
- **Laguna v1 activo no terminal: diagnóstico y escalación al dueño.** No hay ruta
  CLI terminal existente (incluido `prepared`); se declara la laguna en vez de
  prometer un procedimiento o inventar migración/withdraw v1 (§4.1, §4.5, PC-07b,
  N-2).
- **Precedencia de diagnósticos de configuración** (decisión del dueño,
  `decision-diagnostic-precedence.md`): cuando coexisten policy/autoridad/aprobación
  inválida y contexto v1, se emite primero la causa accionable de configuración; el
  rechazo por contexto v1 se conserva íntegro (rc≠0, sin efectos, sin conversión).
  No crea jerarquía general ni reabre la spec; N-4/N-5/N-6 siguen postergados.

**Evidencia.** Review independiente inicial: 4 bloqueantes (B1 intake A+C/v2, B2
paquete v1 activo con "complete or fail", B3 PC-10/11 sin procedimiento, B4 sin test
del localizador del sucesor), 3 requeridos no bloqueantes (R1/R2/R3) y 4 opcionales;
reverificación T6 (attempt 34) los declara **B1–B4 CERRADOS**, sin bloqueantes
nuevos; R-A y R-B resueltos en `review-fix-rar-b.md` (attempt 35, commits
`28991b4a` —comentario de `prepare()`, 8 líneas— y `6869301f` —una línea en
`project-start.md`—). Tests del feature: 7 archivos, **22 tests**; focales
**30 passed in 43.62s** (selección de 6 archivos + `test_cdad_generate.py`; excluye
a propósito `t5_properties`, 2 tests verdes en su propio gate). Gate de cierre
(quien cierra corre la suite, un solo intento completado): `--all` 1876 nodeids,
commit `daace667`, **rc=0**, `1871 passed, 5 skipped in 3668.03s`, `dirty 1`,
`canary_delta_lines=0`; los 5 skips son integraciones preexistentes por variables
de entorno, ninguna cubre una PC de esta unidad. Un intento previo quedó
interrumpido por el límite de tiempo de la herramienta (63 % de la selección, sin
`rc`): no se usa como medición de aceptación. Todo recibo de la unidad quedó
`semantic_status: pending`: recibir no aprobó ningún gate. Fuentes:
`docs/specs/010-004-packet-dispatch-ergonomics/{closure.md,review.md,review-verification.md,review-fix-rar-b.md}`.

**Deuda técnica detectada.**

- **D-1 / publicación (R1):** «La unidad queda cerrada en el repositorio, NO vigente
  en la instalación». La copia instalada conserva el comportamiento anterior y
  rechaza estos paquetes por esquema cerrado; hashes medidos tras el fix R-A: repo
  `d62278a1…` vs. instalación `171fcd14…` en `~/.config/opencode`, `~/.agents` y
  `~/.claude`. Publicar es decisión del dueño; ninguna afirmación de vigencia en el
  CLI instalado puede sostener un cierre o un despacho.
- **R-A endurecimiento diferido:** `--replace-packet` y `--resume-packet` no pasan
  por `_reject_active_v1_packet`; con un paquete v1 activo rechazan con el
  diagnóstico de contexto inexistente en vez de nombrar el bloqueo y escalar. Es
  seguro (rc=2, sin efectos) pero no accionable; requiere unidad propia con su test
  (backlog de la épica).
- **I-8:** el test-writer no puede leer sus propios `instruction_sources` (`skills`
  es `implementation_root` y el `read_scope` del rol no lo incluye); el rol se
  detiene y reporta —correcto— pero la instrucción sigue inaccesible. Fuera de
  alcance; tres salidas registradas, sin unidad asignada.
- **R2 (clase I-6 abierta):** la fila 3 de la matriz no distingue un request
  histórico de uno nuevo sin localizador; un paquete nuevo publicado por la copia
  instalada pasa con `--execution-context` y C puede emitir identificación con
  `execution_context` aunque el request no lo declare. El caso quedó corregido;
  cerrar la clase exige un gate del orquestador con su propio contrato.
- **`deferred-hardening` de la spec §10 (ocho ítems, ninguno aplaza una promesa
  comprometida):** exportación independiente del mensaje recibido por cada runtime
  (capacidad pendiente de verificar); conexión mecánica renderer→herramienta nativa
  (requiere superficie demostrada); atomicidad entre validación y
  lectura/transmisión posterior (ventana conservada); unificación del tratamiento de
  preámbulos (diferencia de §4.4 conservada a propósito); endurecimiento exhaustivo
  de diagnósticos ajenos al cambio; nuevas restricciones generales sobre enlaces
  internos o rutas explícitas históricas (controles existentes conservados);
  interoperabilidad entre versiones instaladas distintas (PC-12 compromete el
  consumidor actualizado aislado, no un protocolo de negociación); rendimiento y
  variantes equivalentes adicionales (sin promesa ni necesidad evidenciada).
- **Límites declarados que no se convierten en garantías:** R3 — las guardas
  documentales comprueban tokens estables y su supervivencia en los derivados, no
  acreditan obediencia de un modelo (la mutación por inversión semántica de B1 siguió
  en verde); **F011 medido y no oculto** — `make validate` sigue en 182 PASS / 1 FAIL
  (`rc=2`), FAIL único en F011, drift preexistente y ambiental: la condición de
  cierre es «declarado», no PASS; **fidelidad del recibo del attempt 32** — el recibo
  (`5c5293e8…`, 2.811 B) acredita la entrega y la identidad del intento, **no el
  informe íntegro**, restituido aparte en `review-fix-t6-report.md` con procedencia
  declarada.
- **Desviaciones de proceso registradas (no ocultas):** el AUDIT submidió el universo
  de fixtures (2 expectativas nombradas vs. 105 archivos y 64 fallos en 15 archivos,
  `fixture-impact-inventory.md` §0); un encargo del POST-AUDIT correctivo acotó los
  cambios a una sola celda y dejó tres oráculos residuales (defecto del orquestador
  que redactó el encargo, corregido en `scope-correction-residual-oracles.md`); dos
  `record` sin sesión acreditada, sin inventar datos de procedencia.
- **Archivo no rastreado ajeno:** `docs/specs/010-000-continuity-relative-root/discovery.md`
  sigue `untracked`; es preexistente y ajeno a esta unidad, no se borró ni se movió.

**Next feature in queue.** `010-001-documentary-contracts` (epic 010, orden 2;
`depends_on: 010-004`, ya satisfecha por esta unidad). Al cerrarse el Memory Bank y
aprobarse el cierre, `010-004` pasa a `done` y `010-001` queda desbloqueada: su
Discovery debe abrirse desde el estado coherente de la épica. Publicar la
instalación **no** es requisito de arranque, pero mientras no se publique, todo
despacho real sigue necesitando la toolchain del repo (R1).