## Discovery 008-004 — mapa verificado

**Contrato comprobado:** SHA-256 coincide con `b209e013…38d01d`. La autoridad es el plan aprobado del epic; **no presupongo una spec de esta feature**.

### 1. Intake de los roles: posición, no verificación ejecutable

- La definición canónica exige primera línea `---cdad-packet-json`: `sources/roles/architect.md:14–34`.
- El generador comparte ese intake con los otros roles: `scripts/cdad-generate.py:68–72,586–603`. Las copias generadas reproducen la condición, por ejemplo `agents/cdad-architect.md:34`.
- Es una **instrucción al modelo**, no un parser del transporte ni una comprobación automática de digest.
- Orquestador y adaptadores exigen entregar bytes sin prefijos: `sources/roles/orchestrator.md:65–78`; `sources/agents/adapters/opencode.md:70–73`; equivalente Claude Code en líneas 89–92.

**Distinción importante:** validé el paquete publicado en disco; eso no demuestra que el prompt recibido sea byte-idéntico. El preámbulo de esta sesión es visible. La universalidad del comportamiento del runtime y sus incidentes históricos provienen de los insumos del orquestador; no repetí esas sondas.

### 2. Qué valida realmente `validate-packet`

En `skills/cdad-cycle/scripts/cdad_packet.py`:

- `validate_request`, línea 1569: valida request, identidad, contrato, scopes y vínculo con ejecución/estado.
- `render_packet`, líneas 1782–1843: reconstruye el paquete desde request, ejecución e instrucciones; incorpora digests de instrucciones y política.
- CLI, líneas 9610–9620: compara **los bytes completos** del archivo contra el render canónico.

**Corrección al insumo:** `REQUEST.json` no contiene un campo de digest del paquete completo. Sí contiene el digest del contrato. La garantía actual es:

`request validado → render canónico → igualdad exacta con PACKET.md`

Por tanto, “validación por digest contra REQUEST.json” necesita precisarse: digest de los bytes canónicos derivados del request, no un campo hoy inexistente ni un hash sólo del encabezado.

### 3. Superficie de despacho y huecos

| Frontera existente | Comprobación actual / hueco |
|---|---|
| `cdad_dispatch.dispatch` | Exige `--packet`; `_known_packet` comprueba existencia de `PACKET.md` y `REQUEST.json`, no igualdad canónica. Líneas 491–542. |
| `cdad_dispatch.record` | Exige paquete e intento; verifica continuidad antes de observación, registro y staging. No acredita el contenido que recibió el hijo. Líneas 1036–1135. |
| `cdad_delegate.delegate` | Transporte externo; resuelve paquete y verifica continuidad, después transmite bytes del archivo. No compara aquí el archivo con el render. Líneas 222–233,536–573. |
| `cdad_packet.prepare --record-dispatch` | Registro de observación; carga request y verifica continuidad. No constituye por sí mismo evidencia del prompt entregado. Líneas 3847–4016. |
| `cdad_result.receive` | Nueva recepción valida request y compara paquete canónico antes de persistir. La repetición durable se reconoce antes, por diseño. Líneas 635–679. |

**Hallazgo central:** los CLI ya rechazan algunos casos sin paquete. El desvío descrito usa delegación nativa fuera de esas fronteras. Endurecer únicamente `cdad_dispatch` **no impide** que el orquestador invoque directamente un rol sin paquete.

Sin cambiar el harness, la garantía alcanzable combina:

1. Preflight obligatorio de la operación CDAD.
2. Intake del rol que rechace una encomienda CDAD sin paquete verificable.
3. Registro/recepción que no acrediten resultados de una encomienda inválida.

Esto no es un sandbox ni intercepta todas las herramientas nativas.

### 4. Despacho de rol frente a operaciones internas

La separación ya tiene precedentes observables:

- `dispatch` transporta; `record` registra el intento nativo.
- `capabilities` y `migrate` son operaciones distintas; no requieren paquete.
- `cdad_result` también contiene recepción, materialización y evidencia de ejecución: no son nuevos despachos.
- Los roles admiten hoy un intake legacy; prohibirlo globalmente rompería un contrato existente.

**Opción recomendada:** declarar como despacho de rol la encomienda de una subfase CDAD a una sesión de rol, independientemente del transporte. No clasificar por palabras del prompt ni exigir paquete a todos los comandos internos.

**VERIFY / decisión pendiente:** cómo se identifica inequívocamente esa encomienda frente a una consulta legacy legítima. No encontré un marcador estructurado vigente que resuelva ambos casos.

**Semántica de error existente:** `cli-delegation.md:125–133` distingue error de invocación sin envoltura —rc no cero— de envoltura `blocked`, que mantiene rc cero. No conviene introducir un rc nuevo.

### 5. `begin` con referencia dentro de `write_scope`

La cadena causal está respaldada por código:

1. Una referencia string se clasifica `contract`; `living` debe declararse explícitamente: `cdad_continuity.py:431–453`.
2. `_digest_references` comprueba existencia y congela digest, sin comparar con el `write_scope`: líneas 489–510.
3. `_plan_write` consume esas referencias y prepara el `begin`: líneas 1040–1139.
4. `record` vuelve a ejecutar `verify_begin`; éste llama `_reference_reports`: líneas 1195–1266.
5. Una referencia `contract` modificada produce P1; `living` reporta divergencia sin bloquear: líneas 2144–2173.

Alternativas: **preferida** rechazar antes de publicar un nuevo `begin` si una referencia `contract` queda cubierta por el `write_scope` del paquete, con diagnóstico; o usar `living` explícito; nunca reclasificar automáticamente ni debilitar P1. Reutilizable `_scope_contains` (`cdad_packet.py:1409–1432`).

### Opciones de contrato para el transporte

**A — Recomendada:** tolerar preámbulo, localizar un único bloque canónico y verificar **todo el paquete**, no sólo sus metadatos, contra el render del request validado. Mantener rechazo ante alteración, ambigüedad o identidad discordante.

**C — Respaldo explícito:** el prompt identifica el paquete publicado y el rol lee/valida `REQUEST.json` y `PACKET.md` antes de trabajar. Requiere autorización mínima de lectura del control-plane; no amplía lectura de producto del test-writer.

**B — No propuesta:** exigir que el harness suprima el preámbulo queda fuera de esta unidad.

### Postcondiciones candidatas — no aprobadas

1. Una encomienda CDAD sin paquete verificable se rechaza con diagnóstico; no publica nuevo `begin`, observación, entrega ni cambio de estado.
2. El mismo paquete íntegro, con o sin preámbulo, autoriza la misma encomienda y scopes.
3. Cambiar objetivo, instrucciones, contrato o scopes, aunque se conserve el encabezado, impide trabajar y acreditar la entrega.
4. El respaldo por archivo sólo acepta el paquete identificado y validado; archivo ausente, identidad discordante o selección ambigua bloquean.
5. `capabilities`, `migrate` y operaciones internas legítimas mantienen sus contratos sin exigirles un despacho ficticio.
6. Una referencia `contract` dentro del `write_scope` se rechaza antes del nuevo `begin`; una referencia `living` explícita puede cambiar sin convertir ese cambio en P1.
7. El rechazo no altera registros durables previos; las repeticiones válidas conservan la idempotencia existente.
8. Los agentes generados e instalados mantienen el mismo intake actualizado.

Superficie de regresión localizada: `test_role_packet_consumers.py`, `test_role_packet_render.py`, `test_006_005_u1b_dispatch_entry.py`, `test_003_007_t1_reference_classes.py` y `test_007_003_legacy_reanchor.py`.

### Evidencia de ejecución

```
PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad_packet.py validate-packet --project-root . \
  --execution-context .cdad/executions/exec-008-004-role-packet-enforcement-001/execution.json \
  --request .cdad/packets/008-004-role-packet-enforcement-architect-discovery-001/REQUEST.json \
  --packet .cdad/packets/008-004-role-packet-enforcement-architect-discovery-001/PACKET.md
```
Salida: sin diagnóstico; `validate_rc=0`.

- **Archivos modificados por mí:** ninguno.
- **HEAD observado:** `ffb2e4aa3dc80c631c7a3134e8139ecd7a48b92e`.
- **Commit creado:** ninguno. **Suite completa:** no ejecutada.
