# Review 006-005 — requiere cambios

**Resultado: 3 B bloqueantes · 2 O opcionales.** No implica aprobación.

Contrato y plan: hashes coincidentes con el paquete. Código revisado hasta `0af4dcb`; respecto del HEAD inicial `126887f`, sólo cambió documentación de la épica.

## B — Bloqueantes

### B-1 — Los allows de implementación anulan la barrera de tests del implementer
**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `skills/cdad-cycle/scripts/cdad_packet.py:3088-3104`.

El derivado emite primero `_IMPLEMENTER_TEST_GLOBS` como `deny`, pero después permite todas las raíces de implementación. Por findLast, esos allows reabren tests convencionales dentro de dichas raíces.

Reproducción con la política vigente y el evaluador usado por los tests:

```text
scripts/tests/test_example.py generated=deny derived=allow
skills/demo/test_example.py generated=deny derived=allow
sources/ui/widget.spec.ts generated=deny derived=allow
tests/test_example.py generated=deny derived=deny
```

Esto contradice la barrera del rol en `sources/roles/implementer.md:18-20,50-52`: no editar tests, incluidos los co-ubicados. U6-7/U6-7b retiran correctamente `write`, pero **no conservan el mismo límite de escritura entre generado y derivado**.

Existe un conflicto contractual que debe resolverse explícitamente: `tests/test_004_002_t5_reviewfix.py:371-404` exige permitir `src/tests/x.py` cuando la política lo clasifica como implementación. Esa exigencia no justifica borrar indiscriminadamente las convenciones de test del rol.

**Consecuencia:** un implementer puede modificar validadores mediante su herramienta de escritura aunque el agente generado los deniegue. Los focales actuales pasan porque sus sondas no cubren estas colisiones.

**Cierre verificable:** resolver la precedencia entre clasificación y barrera del rol sin ampliar autoridad silenciosamente; probar generado y derivado contra tests convencionales dentro de raíces de implementación, además de tests declarados, privados y derivados. Declarar cualquier enmienda necesaria al contrato previo.

### B-2 — `--session` evita la normalización del momento y convierte contradicciones observables en `unknown`
**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:2190-2215`; normalización limitada a `_native_candidate`, `:744-749`.

**Afecta:** E1, PD-5/PD-14, INV-2 y enmienda U6-4.

La selección por padre convierte `time_created` de milisegundos a ISO. La selección por `--session` devuelve la fila sin convertir ese campo. Después, `cdad_dispatch.py:660-679` sólo interpreta texto ISO.

Sobre la misma fila SQLite descartable:

```text
by-parent  moment-type=str verified=True  session=child model=provider/model
by-session moment-type=int verified=False session=None  model=None
```

El efecto no es sólo perder evidencia positiva: con `--since` posterior a la creación de la sesión, el camino sin normalizar declara `unknown`; el control normalizado **rechaza por contradicción de momento**. Con resultado nativo, el primero todavía permite escenificar por PD-6 (`cdad_dispatch.py:1005-1008`).

**Consecuencia:** una asociación contradicha por el store puede tratarse como identidad no verificable, precisamente lo que INV-2 prohíbe.

**Cierre verificable:** normalizar la observación en una frontera común, independientemente de cómo se seleccionó la fila. Añadir casos por la entrada real con `--session`, `--parent`, `--since` y milisegundos: coincidencia ⇒ sesión/modelo observados; momento contradictorio ⇒ rechazo sin entrega.

### B-3 — Las instrucciones externas piden recibir un FINAL TEXT que la entrada no devuelve
**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:**
- `sources/roles/orchestrator.md:36-43`
- `sources/agents/adapters/opencode.md:95-100`
- `sources/agents/adapters/claude-code.md:114-118`

**Afecta:** E3, PD-20 y uso operativo de U4.

Las instrucciones afirman que `cdad_dispatch.py` devuelve FINAL TEXT y ordenan escenificarlo mediante `receive`. El código hace otra cosa:

- devuelve un sobre, no el texto (`cdad_dispatch.py:515-517,536`);
- el módulo ya ejecutó `receive`;
- `delivery_ref` apunta al **recibo durable**, y los temporales se eliminan (`cdad_delegate_opencode.py:2010-2017`).

**Consecuencia:** el orquestador que siga el mandato nuevo recibe instrucciones incompatibles con el resultado real: puede intentar recibir el sobre como informe o reconstruir una segunda recepción. La aceptación manual del adaptador no demuestra que esta guía operativa funcione.

**Cierre verificable:** documentar por separado:
- externa: consumir el recibo de `delivery_ref` y continuar el protocolo;
- nativa: `record` escenifica y el orquestador ejecuta `receive`.

Regenerar los agentes y comprobar el recorrido instrucción → salida real → siguiente comando. No basta un test de presencia de palabras.

## O — Opcionales y deuda

### O-1 — La aceptación conserva estados obsoletos y no satisface literalmente el oráculo de alcance
**Verdict: OPTIONAL · Bucket: m**

**Ubicación:** `docs/specs/006-005-native-path-parity/u6-acceptance.md:18,33-34`; `spec.md:222`.

El recorrido declara `scope_validation: unknown`, mientras PD-22 pide `passed`. U6-2 está identificado como deuda, por lo que no lo presento como un defecto nuevo ni exijo incorporar aquí toda la producción de manifiestos. Pero el cierre debe distinguir **operación conseguida** de **oráculo pendiente/enmendado**.

Además, la aceptación todavía dice que el despliegue está pendiente y U6-7b en curso; `execution.md:350-360` registra su resolución y despliegue.

**Movimiento propuesto:** actualizar el documento de aceptación y registrar, al re-pin, la enmienda o pendiente exacto de PD-22; no declarar ese campo como satisfecho.

### O-2 — La derivación del kind tiene dos implementaciones y una excepción ya innecesaria
**Verdict: OPTIONAL · Bucket: m**

**Ubicación:** `cdad_dispatch.py:896-913` y `cdad_delegate_opencode.py:446-475`.

Ambas funciones consultan la misma tabla, pero mantienen lógica paralela. El módulo conserva además un fallback específico para scribe aun cuando su fila ya admite `role-report`.

**Movimiento propuesto:** compartir la selección del kind desde la tabla cerrada y retirar la excepción transitoria. Reduce el riesgo de divergencia entre vías sin añadir una abstracción de runtimes.

## Trazabilidad por escenarios y enmiendas

| Recorrido | Dictamen |
|---|---|
| **E1 nativa** | Registro y escenificación cubiertos; **B-2** deja incompleta U6-4 para `--session`. U6-3 implementa los tres valores del proyecto en `cdad_dispatch.py:636-657`. |
| **E2 temporal** | Autorización, precedencia y escritura documentada; límite de copia global declarado. **B-1** impide acreditar la conservación general de barreras del implementer. Alcance durable: deuda U6-2, no `passed` real. |
| **E3 externa** | El camino mecánico de kind/recibo/materialización está cubierto, incluido scribe y rechazo del Memory Bank. **B-3** rompe su descripción para el orquestador real. |
| **E4 interrupción** | U6-5 escribe antes del lanzamiento y completa el mismo registro una vez. Recuperación externa cubierta por focales; ausencia de write-ahead nativo y recuperación del huérfano quedan declaradas como límites. |
| **E5 migración** | Paso explícito, negativa a sobrescribir y verificación por capacidades cubiertos. U6-8 compara versiones observadas y excluye `binary_version` de la migración. |
| **V-11** | La evidencia documental declara el agente `-odoo` observado y su entrega. No repetí la sonda real. |

U6-6 normaliza `model_reported` mediante la misma función en ambas vías (`cdad_delegate_opencode.py:2211-2215`). U6-7 elimina la palanca del generador; U6-7b la retira al derivar desde instalaciones anteriores. La reserva sobre estos últimos es **B-1**, no la retirada de `write`.

## Evidencia ejecutada

Comandos de verificación:

```text
sha256sum docs/specs/006-005-native-path-parity/spec.md \
          docs/specs/006-005-native-path-parity/plan.md \
          docs/cdad-policy.json
git diff 0815787~1 HEAD -- skills scripts sources agents tests
git diff 0815787~1 HEAD -- install.sh
```

Tests con `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider`, divididos en dos grupos:

- U1a, U1b, U1c, U2, U3, U3b, U4, U5 y U6fix1: **90 passed**.
- U6fix4, U6fix5, U6fix6, U6fix7, U6fix7b, U6fix8 y U7: **49 passed**.

El primer intento con `tests/test_006_005_*.py` agotó 120 segundos; **no se contabilizó como corrida completa**. Las reproducciones B-1/B-2 se ejecutaron aparte, sin modificar producto.

**Archivos modificados por esta revisión:** ninguno. **Commit creado:** ninguno.

## Abstentions

- No repetí despachos reales ni inspeccioné todos sus artefactos originales; E2/V-11 reales se reportan como evidencia documental, no como observación propia.
- No ejecuté `make validate`: su validador de especialización puede leer el archivo privado expresamente prohibido (`tests/validate-odoo-specialization.sh:265-271`).
- No ejecuté la suite completa del repositorio: corresponde a quien cierre, según PD-21.
- No acredité una familia de modelo distinta de la del implementer ni una auditoría exhaustiva de cada aserción del diff; los buckets no presuponen esas condiciones.

**Veredicto final: requiere cambios por B-1, B-2 y B-3.**