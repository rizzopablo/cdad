# Review T2 (004-002) — Codex gpt-6-astra, 2026-09-30

> Sesión `01a0f10a-dab2-7482-9c83-2cfd8454f368`. Materializado verbatim salvo rutas del worktree.

Dictamen: **6 hallazgos BLOCKING**, pese a que la verificación solicitada termina en **71 passed**. No modifiqué el repositorio ni hice commits.

## BLOCKING

Todos los hallazgos tienen severidad **Required** y **Bucket: h**, por diff completo, contrato y convenciones consultados, y reproducciones con ubicación verificable.

### F1 — Reutilizar v2 omite comprobar autoridad y feature vigentes

- **Verdict:** BLOCKING
- **Bucket:** h
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:984-985` y `:471-483`; PD-3, PD-4, I2/I3.
- **Rationale:** la selección de una v2 existente valida su estructura, pero no vuelve a comprobar autoridad, cierre de feature ni correspondencia con `active_feature`/`active_epic`.

**Evidencia:** después de completar el primer paquete, las siguientes modificaciones permiten preparar otro con `rc=0`:

1. Delegación revocada.
2. Feature marcada `done`.
3. `active_feature` sustituida por otra feature.

En el tercer caso, el paquete y binding conservan la feature anterior. Además, `validate-state` devuelve `VALID` ante esa contradicción.

**Remedio:** centralizar la validación vigente para bootstrap y reutilización; rechazar cambios incompatibles y exigir `--new-execution` cuando corresponda. Validar el state original antes de construir el nuevo binding.

### F2 — La autoridad acepta epic terminado y scopes de otro epic

- **Verdict:** BLOCKING
- **Bucket:** h
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:866-901`, especialmente `:891`; PD-3/I2.
- **Rationale:** no se comprueba el estado terminal del epic; el alcance se verifica mediante pertenencia de una subcadena.

**Evidencia:**

- Con `epic_stage="epic-done"`, publica contexto y paquete, `rc=0`.
- Con `scope="epic-004-single-source-planning-unrelated"`, acepta autoridad para `epic-004-single-source-planning`, `rc=0`.

**Remedio:** comprobar vigencia del epic y reconocer referencias inequívocas al identificador autorizado, sin aceptar identificadores diferentes por prefijo.

### F3 — Resume acepta cambios cuando la opción aparece una sola vez

- **Verdict:** BLOCKING
- **Bucket:** h
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:998-1016`; `tests/test_004_002_t2_bootstrap.py:578-585`; PD-4.
- **Rationale:** contar opciones repetidas no determina si sus valores modifican el encargo. `role`, `substage` y `objective` no se contrastan con el paquete almacenado.

**Evidencia:** reanudar pasando una única opción `--objective CHANGED` devuelve `rc=0`. El test negativo pasa porque su helper introduce un primer `--objective` y el test añade otro: verifica repetición, no incompatibilidad.

**Remedio:** comparar las opciones admitidas con el request original, o rechazarlas explícitamente en resume. Añadir el negativo con una única aparición y valor diferente.

### F4 — Resume devuelve contenido sin validar identidad ni confinamiento

- **Verdict:** BLOCKING
- **Bucket:** h
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:1017-1021`; PD-4 e invariante de productor único.
- **Rationale:** concatena el identificador como ruta y devuelve cualquier `PACKET.md` encontrado; no verifica paquete canónico, ejecución ni compatibilidad con state.

**Evidencia:**

- `--resume-packet ../unrelated` devuelve `UNRELATED BYTES\n`, `rc=0`.
- Sustituir el paquete publicado por `TAMPERED\n` también produce resume exitoso.

**Remedio:** validar identificador plano y ruta confinada; comprobar identidad y contenido contra los artefactos canónicos antes de devolver bytes.

### F5 — Los errores de publicación dejan directorios y pueden producir traceback

- **Verdict:** BLOCKING
- **Bucket:** h
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:1111-1135`; PD-3 y contrato §2.
- **Rationale:** el rollback elimina el directorio de ejecución, pero no sus padres recién creados. Además, la limpieza puede lanzar otra excepción.

**Evidencia:**

- Si `.cdad/packets` es un archivo, falla con `rc=2` pero deja `.cdad/executions` vacío.
- Si `docs/.cdad-state.json.tmp` es un directorio, falla con `rc=1`, traceback y deja `.cdad`, `.cdad/executions` y `.cdad/packets`.

**Remedio:** registrar qué directorios creó esta operación y retirarlos si siguen vacíos; preservar entradas preexistentes y evitar que errores de limpieza oculten el diagnóstico original. Esto es rollback de errores ordinarios, independiente de la recuperación ante interrupciones prevista para T3.

### F6 — Una ubicación de política inválida activa el fallback legacy

- **Verdict:** BLOCKING
- **Bucket:** h
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:819-820` y `:987-992`; I4 refinado, PD-1/PD-10.
- **Rationale:** `is_file()` equipara una política ausente con una ubicación existente que no es archivo.

**Evidencia:** con contexto v1 y `docs/cdad-policy.json` convertido en directorio, `prepare` implícito publica un paquete legacy, `rc=0`. Con política regular presente —incluso JSON inválido— exige correctamente `--new-execution`.

**Remedio:** distinguir ausencia real de ubicación inválida; esta última debe producir error, sin fallback.

## OPTIONAL

Ninguno.

## Evidencia y verificaciones

Snapshot: `HEAD=28c2a92f1e680946b4534dd2b6c31d3a4595ef30`. Los dos archivos T2 no difieren de `91d0310`. El SHA-256 de la spec coincide con el contrato declarado.

La primera ejecución sin staging dio **64 passed, 7 failed**; los siete fallos identificaron exclusivamente el manifest ausente. Generé staging en una copia:

```bash
mkdir -p /tmp/cdad-t2-review-evidence
git archive HEAD | tar -x -C /tmp/cdad-t2-review-evidence
make -C /tmp/cdad-t2-review-evidence staging
```

Desde esa copia ejecuté exactamente:

```bash
env -u TMPDIR python3 -m pytest tests/test_004_002_t2_bootstrap.py tests/test_004_002_t1_policy.py tests/test_004_002_t1_reviewfix.py tests/test_packet_prepare.py tests/test_role_packets.py -q
```

Resultado: **71 passed in 76.53s**. [Salida completa](/tmp/cdad-t2-review-evidence/compatibility.log).

También comprobé:

- Aprobador vacío y source inexistente: rechazo específico, árbol intacto.
- Delegación de otro epic: rechazo sin publicación.
- Legacy sin política: camino implícito conservado.
- `--new-execution`: permite iniciar la nueva feature.
- Identidad v2 sin campos runtime/modelo; los tests verifican continuidad entre roles, resolución automática, bloqueo `prepared`/`dispatched`, preservación v1 y ausencia de migración.

Las sondas reproducibles y sus resultados están en [probes.py](/tmp/cdad-t2-review-evidence/probes.py), [probes.log](/tmp/cdad-t2-review-evidence/probes.log), [extra_probes.py](/tmp/cdad-t2-review-evidence/extra_probes.py) y [extra_probes.log](/tmp/cdad-t2-review-evidence/extra_probes.log).

**Mutaciones contra T2:**

| Garantía alterada | Resultado |
|---|---|
| Aprobación obligatoria | Detectada |
| Delegación obligatoria | Detectada |
| Bloqueo prepared/dispatched | Detectada |
| Identidad estable | Detectada |
| Bytes idénticos en resume | Detectada |
| Rechazo implícito v1 con política | Detectada |
| Preservación de bytes v1 | Detectada |
| Ausencia de publicación ante error | Detectada |
| Resolución automática de validate-state | Detectada |
| Existencia de source | **Sobrevive: 18 passed** |
| Rechazo de opciones modificadoras en resume | **Sobrevive: 18 passed** |

Comando: `python3 /tmp/cdad-t2-review-evidence/mutations.py`. [Harness](/tmp/cdad-t2-review-evidence/mutations.py) y [resultados](/tmp/cdad-t2-review-evidence/mutations.log).

Reproduje asimismo los tests corregidos contra el productor de `c0511e1`: **16 failed, 2 passed**, consistente con el RED registrado. [Salida](/tmp/cdad-t2-review-evidence/red-reproduction.log).

## Abstentions

Ninguna dentro del alcance revisado. No ejecuté la suite completa ni evalué las garantías de T3–T6.

Archivos del repositorio modificados: **ninguno**. `git status --porcelain` final: vacío. Evidencia auxiliar y mutaciones: únicamente bajo `/tmp`.
## Disposición del orquestador

Corregir F1–F6 ahora (F5 es rollback de errores ordinarios; la recuperación
ante interrupciones sigue en T3). Los tests de la corrección deben además
matar las dos mutaciones que sobrevivieron (existencia de `source`; resume
con una única opción modificadora).

## Re-review (suplente: subagente Claude Opus `cdad-reviewer`, 2026-09-30)

Codex llegó a su límite de uso (reset 06:43); se aplicó la regla del dueño y
revisó un subagente Opus, de familia distinta de los constructores.

**Dictamen: changes-required.** F1–F6 cerrados en el producto (sondas
propias en todos los casos) e I7 cumplido para todas las opciones, incluidos
valores idénticos y paquete `prepared`. Las dos mutaciones que antes
sobrevivían ahora se detectan. Pero:

- **B1 (BLOCKING, m):** la comparación de autoridad (`authority_ref ==
  hitl_delegation.source`) solo está en `_select_execution`
  (`cdad_packet.py:1031`). Con el `source` cambiado, reutilizar da rc=2,
  pero `validate-state` da VALID y la reanudación reemite los bytes. Remedio:
  moverla a `_validate_v2_state`, después de la validación de vigencia, y
  retirar el duplicado. Falta el negativo; la mutación M12 sobrevive.
- **B2 (BLOCKING, h):** los tests de F4 (`test_004_002_t2_reviewfix.py:314`
  y `:336`) usan `run_prepare`, que inyecta `--role/--substage/--objective`:
  los rechaza I7 antes de llegar a la lógica de F4. El mutante M3 (sin
  verificación canónica) pasa la suite de T2. Remedio: argv puro.
- **B3 (BLOCKING, h):** los subtests de I7 (`:527`) y el test de F3 (`:283`)
  llevan las tres opciones del helper, así que no aíslan ninguna opción; las
  mutaciones M2b y M2c sobreviven. Además, `ORDINARY_CASES` omite
  `--expected-output`, `--out-dir`, `--execution-context`, `--new-execution`
  y los scopes, inputs, invariants y evidence. Remedio: argv desde cero por
  opción y la lista completa de I7.
- **O1:** falta un negativo de resume puro con la delegación revocada (la
  mutación M11 sobrevive).
- **O2:** el diagnóstico de `active_feature` cambiada nombra la feature
  equivocada; invertir el orden de las comprobaciones.
- **O3 (FYI):** un paquete con `--out-dir` no se puede reanudar (coherente
  con I7, se documentará en T6); mensaje engañoso con un symlink roto de la
  política; el scope se interpreta por tokens.

**Disposición del orquestador:** corregir B1, B2, B3, O1 y O2 en un
micro-ciclo (tests primero, después la implementación). O3 queda para la
documentación de T6.

## Verificación de cierre (suplente Opus, misma sesión, sobre `6cea734`)

**Dictamen: approved.** B1–B3, O1 y O2 cerrados; sin hallazgos nuevos.

- Todas las mutaciones que antes sobrevivían ahora hacen fallar tests: M2b,
  M2c, M3, M3+M2b, M11 y M12.
- Mutación extra: quitar la vigencia de `_validate_v2_state` hace fallar 17
  tests. Confirma que ese es ahora el único punto de validación.
- Sonda B1 con el `source` cambiado: `validate-state`, reanudación pura y
  reutilización dan rc=2, las tres con el mismo diagnóstico.
- O2: el diagnóstico nombra la feature que cambió.
- 5 archivos focales: 86 passed en una copia con staging.
- Los FYI de O3 se documentan en T6.
