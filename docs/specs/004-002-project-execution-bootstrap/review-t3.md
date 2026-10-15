# Review T3 (004-002) — Codex gpt-6-astra, 2026-09-30

> Sesión `01a0f260-c3c0-76d0-ae48-d42260e2bccc`. Materializado verbatim salvo rutas del worktree.

**Dictamen: 6 hallazgos bloqueantes, 1 mejora opcional y 1 abstención.** La exclusión se rompe y la recuperación puede borrar archivos ajenos. La reconciliación también permite emitir permisos correspondientes a una política anterior.

Revisión sobre `954f14c4dbaffaf2e91619ae385d4a00dbe22a3f`, con RED `df2adfa`. SHA-256 del contrato verificado: coincide con el packet. No modifiqué archivos del producto ni hice commits; `git status --short` y `git diff --check` quedaron sin salida.

## Hallazgos bloqueantes

**F1 — Critical: eliminar `.lock` rompe la exclusión.**
**Verdict: BLOCKING · Bucket: h**

Ubicación: [cdad_packet.py:967](skills/cdad-cycle/scripts/cdad_packet.py:967), líneas 967–990. Contrato: PD-11/I5.

La eliminación no ocurre siempre: depende de `_created_file`. Cuando ocurre, sigue siendo insegura. Reproduje esta secuencia mediante procesos separados y barreras de sincronización:

1. A libera el lock y queda pausado antes de `_remove_own`.
2. B adquiere el inodo existente.
3. A elimina el archivo.
4. C crea otro inodo y adquiere su lock mientras B sigue dentro de la sección protegida.

Salida: `two simultaneous holders True`, inodos `11695785` y `11695787`.

**Remedio:** conservar el archivo de rendezvous y liberar únicamente el descriptor/lock. Su existencia no significa que haya un lock huérfano.

**F2 — Critical: resolución y reserva ocurren fuera del lock; se sobrescriben paquetes.**
**Verdict: BLOCKING · Bucket: h**

Ubicación: [cdad_packet.py:1402](skills/cdad-cycle/scripts/cdad_packet.py:1402), líneas 1402–1474 y 1530–1532. Contrato: PD-11/I5 y PD-4.

State, ejecución, identificador y contenido del paquete se calculan antes de adquirir exclusión. Pausé A justo antes de adquirir el lock; B completó su preparación; después A continuó y sobrescribió el mismo paquete con otro objetivo.

Salida: `B rc 0 same_ids True overwritten True`.

Esta carrera existe aunque se corrija F1: las publicaciones pueden estar serializadas y consumir decisiones obsoletas.

**Remedio:** adquirir el lock antes de leer state y resolver/reservar identidades, manteniéndolo hasta terminar la publicación. El gancho `reserved-id` también debe situarse después de reservar: actualmente precede incluso a la lectura del state.

**F3 — Critical: recuperar una transacción borra archivos ajenos.**
**Verdict: BLOCKING · Bucket: h**

Ubicación: [cdad_packet.py:1489](skills/cdad-cycle/scripts/cdad_packet.py:1489), líneas 1489–1506 y 1536. Contrato: PD-11 e invariante 7.

Después de interrumpir en `context-written`, añadí `foreign.txt` dentro del directorio de transacción existente. Repetí la interrupción y ejecuté una recuperación normal. Terminó con rc 0 y state válido, pero eliminó ese archivo mediante `shutil.rmtree(stage_dir)`.

El directorio reutilizado no pertenece íntegramente a la nueva invocación.

**Remedio:** registrar los archivos propios de la transacción y limpiar exclusivamente esos archivos, conservando cualquier entrada ajena. Compartir ese mecanismo entre recuperación y rollback.

**F4 — Required: reconciliar cambia el hash, pero conserva la clasificación anterior.**
**Verdict: BLOCKING · Bucket: h**

Ubicación: [cdad_packet.py:1335](skills/cdad-cycle/scripts/cdad_packet.py:1335), líneas 1335–1354. Contrato: PD-5; PD-1 y PD-7.

Cambié `implementation_roots` de `["src","lib"]` a `["app"]`, aporté el hash actual y una decisión válida. Reconciliación y preparación posterior devolvieron rc 0, pero contexto y permisos conservaron `["src","lib"]`.

Además, sustituir la política por `{}` también permitió reconciliar y preparar con rc 0. Se valida el contexto anterior, no la nueva política.

**Remedio:** validar y derivar `path_policy`, snapshot y hash desde una misma lectura de los bytes aceptados; publicar juntos esos valores.

**F5 — Required: la reconciliación deja inválido el binding del state.**
**Verdict: BLOCKING · Bucket: h**

Ubicación: [cdad_packet.py:1344](skills/cdad-cycle/scripts/cdad_packet.py:1344), líneas 1344–1354. Contrato: PD-5 y coherencia contexto/binding.

Tras reconciliar correctamente, cambia `execution.policy_sha256` en el contexto, pero no en `state.execution`. Inmediatamente:

```text
validate-state → rc 2
ERROR: execution binding mismatch: policy_sha256
```

Un `prepare` posterior reconstruye el binding y oculta el defecto en el test positivo existente.

**Remedio:** actualizar contexto y binding mediante una publicación recuperable, comprobando coherencia inmediatamente después de reconciliar.

**F6 — Required: el paquete carece del snapshot verificable de política.**
**Verdict: BLOCKING · Bucket: h**

Ubicación: [cdad_packet.py:700](skills/cdad-cycle/scripts/cdad_packet.py:700), líneas 700–710. Contrato: PD-5 y comprobación solicitada de contexto y paquetes.

El renderer incorpora el hash y `path_policy`, pero omite `policy.snapshot`. La clasificación tampoco reproduce los bytes completos de la política, incluidos `temporary_roots`.

Sonda sobre el paquete publicado:

```text
snapshot_literal False
snapshot_base64 False
hash True
```

El test de T3 comprueba el snapshot únicamente en el contexto.

**Remedio:** incorporar al paquete el snapshot exacto y comprobar que su digest coincide con la revisión declarada.

## Mejora opcional

**O1 — Cobertura vacua del bloqueo de `record-dispatch`.**
**Verdict: OPTIONAL · Bucket: h**

Ubicación: [test_004_002_t3_durable.py:355](tests/test_004_002_t3_durable.py:355), líneas 355–365; implementación, líneas 1364–1367.

Eliminar exclusivamente `_ensure_policy_reconciled` de `_record_dispatch_control` deja **9 passed**. El error genérico de funcionalidad T4 pendiente también contiene “reconciliation” y satisface el oráculo.

Conviene distinguir el rechazo por cambio de política del rechazo por funcionalidad pendiente. No atribuyo a T3 la implementación todavía pendiente de T4.

## Evidencia de ejecución

Comando solicitado, ejecutado con `TMPDIR` eliminado:

```bash
env -u TMPDIR python3 -m pytest tests/test_004_002_t3_durable.py tests/test_004_002_t2_bootstrap.py tests/test_004_002_t2_reviewfix.py tests/test_004_002_t1_policy.py tests/test_packet_prepare.py -q
```

Resultado: **81 passed, 6 failed en 85.70 s**. Los seis fallos fueron exclusivamente por ausencia de `build/staging/manifest.json`.

En una copia temporal del checkout:

```bash
make -C /tmp/review-t3-staging staging
cd /tmp/review-t3-staging
env -u TMPDIR python3 -m pytest tests/test_packet_prepare.py::TestPreparedInstalled -q
```

Resultados: staging rc 0; **6 passed en 43.92 s**. Los casos seleccionados de T1/T2 no mostraron regresiones. No ejecuté la suite completa ni T4.

Sondas reproducibles: [review_t3_probe.py](/tmp/review_t3_probe.py).

```bash
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 /tmp/review_t3_probe.py
```

| Interrupción | Primera / repetida / recuperación: rc | Resultado |
|---|---|---|
| `reserved-id` | 97 / 97 / 0 | State final válido |
| `context-written` | 97 / 97 / 0 | State válido; elimina archivo ajeno: F3 |
| `packet-written` | 97 / 97 / 0 | State válido; conserva los archivos ajenos sondeados |
| `before-state` | 97 / 97 / 0 | State válido; conserva los archivos ajenos sondeados |
| `after-state` | 97 / 2 / 2 | Conserva paquete pendiente; resume rc 0 y bytes idénticos |

Las interrupciones no emitieron paquetes por stdout. En `after-state`, las invocaciones siguientes rechazan correctamente reemplazar el paquete pendiente.

## Mutaciones

Ejecutadas exclusivamente en copias temporales, contra los nueve tests de T3:

```bash
env -u TMPDIR python3 /tmp/review_t3_mutations.py
env -u TMPDIR python3 /tmp/review_t3_dispatch_mut.py
env -u TMPDIR python3 /tmp/review_t3_extra_mut.py
```

**13 mutaciones detectadas y 1 superviviente**, sin errores sintácticos ni de colección.

| Garantía alterada | Tests fallidos |
|---|---:|
| Snapshot incorrecto | 1 |
| Eliminar control general de revisión | 1 |
| Eliminar adquisición del lock | 1 |
| Desactivar interrupciones | 2 |
| Imprimir antes de publicar | 2 |
| Omitir SHA literal de la decisión | 1 |
| Omitir coincidencia con SHA actual | 1 |
| Permitir reconciliación con paquete pendiente | 1 |
| Descartar historial anterior | 1 |
| Borrar archivos ajenos | 2 |
| Corromper paquetes anteriores | 1 |
| Omitir publicación del state | 6 |
| Modificar la política al reconciliar | 1 |
| Eliminar solamente control de revisión de despacho | **0: superviviente** |

Scripts y resultados: [mutaciones](/tmp/review_t3_mutations.py), [logs](/tmp/review-t3-mut-gspso6zm), [mutaciones adicionales](/tmp/review_t3_extra_mut.py).

En arquitectura, se conserva un único productor `prepare`. La recuperación y las limpiezas de éxito/error no comparten una gestión consistente de propiedad de archivos, como demuestra F3. El gancho es inerte sin la variable. No identifiqué otro defecto de rendimiento con evidencia suficiente.

## Abstentions

**A1 — Independencia de familia de modelo respecto del implementer.**
**Verdict: ABSTAIN · Bucket: m**

El packet declara modelos configurado/reportado como `null`; no puedo verificar esa condición de independencia. La revisión y las sondas se realizaron en esta sesión separada, sin adoptar las conclusiones del implementer como evidencia.
## Disposición del orquestador

- **Se corrigen F1–F6 y O1** después de que aterrice el GREEN de T4, que
  ya estaba en curso sobre este mismo archivo; va en secuencia, no en
  paralelo.
- **I5b (nuevo):** gancho de sincronización determinista para probar F2 sin
  carreras aleatorias. `CDAD_TEST_PAUSE_AT=<punto>` junto con
  `CDAD_TEST_PAUSE_FILE=<ruta>`: al llegar al punto, el proceso crea
  `<ruta>.reached` y espera hasta que exista `<ruta>` (máximo 30 s). Es
  inerte sin la variable. Con el remedio de F2, el punto `reserved-id`
  queda después de tomar el lock y reservar.
- **Enmienda de oráculo firmada:** `.cdad/.lock` es un artefacto legítimo y
  permanente (archivo de rendezvous de `flock`). Los oráculos de lista
  exacta de artefactos que lo excluían (p. ej. `test_packet_prepare` p1)
  deben admitirlo.
- **A1 (abstención):** la independencia de familia está registrada en el
  ledger. El implementer usó `deepseek-v4.1-flash` y el reviewer
  `gpt-6-astra`.

## Decisión del orquestador durante el review-fix (I5c)

El implementer se detuvo sin commit: con el lock tomado antes de leer el
state (F2), un prepare rechazado deja `.cdad/.lock` y rompe los oráculos
"sin publicación" de T2. Se descartó enmendar esos oráculos, porque un
rechazo dejaría rastro en proyectos consumidores. Se adoptó la retirada
del `.lock` en el camino de fallo, con el `flock` todavía tomado, más la
verificación de inodo al adquirir (I5c en plan.md). Solo se enmienda p1.

## Re-review T3 + review T4 (suplente Opus, 2026-09-30, sobre `fc184c1`)

Codex quedó sin cuota semanal. Un primer intento con Opus se cortó por el
límite semanal de la API de Anthropic; este es el reintento, después del
reset.

**A) T3: changes-required.** F1–F6 y O1 quedan cerrados según sondas
propias. Hallazgos nuevos:
- **A-1 (Critical, BLOCKING):** el proceso que pierde la adquisición del
  lock hace `_remove_own()` sin tener el `flock` de ese inodo
  (`cdad_packet.py:1051–1066`) y borra el `.lock` del proceso que lo tiene.
  Reproducido con el CLI real: dos escritores dentro de la sección crítica,
  dos paquetes despachables impresos y uno sobrescrito. Es F2 reintroducido.
  La ventana existe siempre que falte `.lock`, y el repo principal está hoy
  en ese caso. Remedio: solo `__exit__`, tras una adquisición verificada,
  retira el archivo. Crear con `O_CREAT|O_EXCL`.
- **A-2 (BLOCKING):** reconciliar no aplica la exclusividad de modos.
  `--reconcile-policy` combinado con `--record-dispatch` o con opciones
  ordinarias da rc=0 y descarta en silencio la otra operación; `prepare`
  ignora `--attempt-id`. Remedio: un único rechazo por modo en `main`,
  antes del lock.
- **A-3 (OPTIONAL):** la comprobación de inodo de I5c no tiene test (el
  mutante M02 sobrevive).
- **A-4 (OPTIONAL):** la recuperación elige qué borrar por nombre de
  archivo y borra el `state.json` de un directorio ajeno dentro de
  `.cdad/.txn`.

**B) T4: changes-required.**
- **B-1 (BLOCKING):** el registro del intento y el state se escriben por
  separado. Si falla entre ambos, el registro queda publicado con rc≠0, y
  un reintento idéntico sale antes de llegar a la transición: el paquete
  queda `prepared` para siempre.
- **B-2 (BLOCKING, m):** `provenance` admite claves arbitrarias (p. ej.
  `result`, `gate`); es una vía para colar recepción.
- **B-3:** misma causa que A-2.
- **B-4 (OPTIONAL):** ni la exclusividad ni el lock del registro tienen
  tests (M21 y M22 sobreviven).
- **B-5 (Nit):** `Multi-Runtime` con mayúsculas se acepta.
- **B-6 (FYI):** el registro reescribe el formato del state sin alterar su
  semántica.

Mutaciones: 24 (20 muertas; M02, M21 y M22 las matan las sondas; M08b es
equivalente). Abstenciones: familia de modelo no verificable desde la
review, frecuencia de A-1 fuera del arnés, flock sobre NFS.

**Disposición del orquestador:** se corrigen A-1, A-2/B-3, B-1 y B-2, y se
cubren con tests A-3, A-4 (limpiar solo directorios de transacción propios),
B-4 y B-5 (comparación sin distinguir mayúsculas). Todo antes del GREEN de
T5. **I5d:** nuevo punto de pausa `before-lock-open` (I5b) para probar A-1
de forma determinista.
