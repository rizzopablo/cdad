# review.md: 010-004-packet-dispatch-ergonomics, reverificación T6 (Stage 4, review-002)

**Resultado: B1, B2, B3 y B4 están CERRADOS. No hay bloqueantes nuevos ni regresiones en lo probado. Quedan 2 hallazgos requeridos no bloqueantes y 3 opcionales.** El cierre de la unidad **puede declararse**, pero **todavía no**: faltan las condiciones listadas en «Veredicto final». Este informe no aprueba el cierre.

## Admisión y base

- **Paquete:** ruta C, sin cuerpo inline. Usé los scripts del repo.
  - `validate-request` rc=0 y `validate-packet` rc=0.
  - `render` es idéntico a `PACKET.md` (`cmp` rc=0).
  - El JSON recibido coincide en contenido con `render --route C` (comparación a la vista).
  - El sha256 de `spec.md` es `fc6b2ccc…5d64`, igual al pin.
- **Base `1dd7661f`:** es correcta para el código.
  - `--is-ancestor` rc=0; `rev-list --count` = 7; `diff --stat` = 29 archivos.
  - **Imprecisión del encargo:** el rango no contiene «exactamente» fix y guarda. Son esos 2 commits de código (`4118b794`, `4a652890`) más 5 commits de `docs`.
  - **Fuera del rango:** `tests/test_010_004_t6_red.py` (`932e0288`) es anterior a la base, pero es el oráculo de B2 y B4. Lo revisé aparte, de forma parcial (ver Abstenciones).

## Veredicto por bloqueante

| Bloqueante | Veredicto | Evidencia |
|---|---|---|
| **B1** intake A+C / v2 para C | **CERRADO** | `sources/roles/architect.md:15-61`: enuncia C solo-v2 con diagnóstico v1, y A+C rechazado aunque el inline coincida. La regla está en 20/20 derivados. |
| **B2** v1 activo | **CERRADO** en el camino `prepare` (ver R-A y R-B) | `cdad_packet.py:630` y la llamada dentro de `prepare()`, antes de `_select_execution`. |
| **B3** PC-10/PC-11 | **CERRADO** | `re-entry.md`, sección «Integrity, observability and fidelity»: tabla de cinco evidencias y reglas I-4 e I-5. `t4-closure.md:103-114` corrige la traza y conserva la original. |
| **B4** localizador del sucesor | **CERRADO** | `test_b4_…` pasa, con control positivo y predecesor histórico. Su helper declara comprobar request, cabecera y bytes del predecesor. |

**Prueba propia de B2** (fixture temporal con los helpers de T6):

| Caso | rc | Árbol | Salida |
|---|---|---|---|
| v1 `prepared`, ambos comandos | 2 | sin cambios | Cubierto por el oráculo T6, que pasa |
| v1 `dispatched`, `prepare` | 2 | sin cambios | Diagnóstico nuevo: paquete nombrado, sin ruta terminal, escala al owner |
| v1 `dispatched`, `--new-execution` | 2 | sin cambios | El mismo diagnóstico |
| `REQUEST.json` ilegible | 2 | sin cambios | Sin ruta terminal, escala al owner |

El oráculo T6 solo cubre `prepared`. El caso `dispatched` lo acredita esta prueba, no un test del repo.

## Comprobaciones de no debilitamiento

- **(a) Diagnóstico B2: cumple.** El helper solo lee y lanza `PolicyError`. Corre dentro del lock y antes de cualquier escritura. No abre migración, withdraw, replay ni fallback; esas palabras solo aparecen negadas en el mensaje.
- **(b) Dueño único del intake: cumple.**
  - El diff de `sources/roles/` toca solo `architect.md`.
  - `implementer`, `reviewer`, `scribe` y `test-writer` conservan su puntero.
  - `orchestrator.md:70` conserva su regla propia y los derivados del orquestador no cambian.
  - La regla aparece en exactamente 20 agentes.
- **(c) `re-entry.md`: cumple.** Remite a `delivery` (007-004 §6.2) sin reescribirlo y usa vías existentes. Ver O-A.
- **(d) Guarda B1: cumple.**
  - Usa tokens estables y no cuenta ocurrencias.
  - **Mutación:** borrar cada uno de los 5 tokens hizo fallar el test en la fuente y en un derivado (10/10).
  - **Control negativo:** quitar la regla propia del orquestador falla, y filtrarle un token del dueño también. El control discrimina de verdad.
  - **Límite confirmado:** una inversión semántica («is accepted, never rejected as an invalid packet even when the inline matches») sigue en verde. Es el límite R3 ya declarado, no un defecto, y no debe arreglarse congelando prosa.
  - Ver O-B.

## Hallazgos requeridos no bloqueantes

### R-A. `--replace-packet` y `--resume-packet` no dan el diagnóstico de PC-07b

**Verdict: OPTIONAL · Bucket: m**

- **Ubicación:** el dispatch de `cdad_packet.py:10304,10309` llega a `_replace_packet` y `_resume_packet`, que nunca pasan por `prepare()`. El comentario en `prepare()` dice que el bloqueo cubre «EVERY preparation path», y eso no es cierto.
- **Medido:** sobre un paquete v1 `prepared`, ambos dan rc=2, sin cambios en el árbol, con `ERROR: execution context not found: .cdad/executions/exec-legacy-v1/execution.json`.
- **Consecuencia:** el rechazo es seguro, pero no nombra el bloqueo ni escala al owner, y apunta a un archivo que no debe crearse. No ofrece un procedimiento prohibido ni permite preparar v1. Por eso no bloquea: §7 no atribuye soporte v1 a `--resume-packet` y `--replace-packet` no está en la promesa.
- **Remedio:** corregir el comentario, o llamar al helper en esas dos entradas.

### R-B. Cláusula documental de B2 cumplida solo por referencia

**Verdict: OPTIONAL · Bucket: h**

- **Evidencia:** la condición anterior pedía que `project-execution.md` y el orquestador describieran el mismo resultado. `project-execution.md:118-121` lo hace.
- **Orquestador:** `orchestrator.md` no cambió. Solo su «Blocked exit» genérico remite a `project-execution.md`. No lo considero bloqueo porque evita duplicar la regla y no la contradice.
- **`project-start.md:93-95`:** sigue diciendo «Add --new-execution when prior context exists» sin salvedad. Quien lo siga recibe el diagnóstico correcto, así que la consecuencia es una vuelta de más, no un callejón sin salida.
- **Decisión pendiente:** si el orquestador exige la cláusula literal, B2 queda parcial solo en esa parte documental. Remedio: una línea en `project-start.md` que apunte a `project-execution.md`.

## Opcionales

- **O-A (Nit) · OPTIONAL · Bucket: m.** En I-5, la recuperación por «NEW v2 assignment» se describe como la ruta `receive`/`validate-receipt`/`materialize`/`register-transition`. Un encargo nuevo nace en `prepare`, y esa ruta no lo nombra. No inventa protocolo, pero la frase es imprecisa.
- **O-B (Nit) · OPTIONAL · Bucket: h.** Los `assertEqual(len(derived), 20)` y sobre `set` son tautológicos: la lista sale de un producto fijo de tuplas y no puede fallar. La comprobación útil es la de existencia de archivos. Además, el informe del implementer cita `cdad-orchestrator{,-odoo}.md`, pero la variante `-odoo` no existe.
- **O-C (Nit) · OPTIONAL · Bucket: l.** Con el `REQUEST.json` borrado y `PACKET.md` presente, `--new-execution` todavía emite «complete or fail it (PD-4)», el texto prohibido. Medido con fixture manual. Es un paquete dañado, no el estado de publicación normal, y sigue siendo rc=2 sin efectos.

## Veredicto final de la unidad

**No quedan bloqueantes contractuales, así que el cierre puede declararse cuando se cumplan estas condiciones. Hoy no puede declararse:**

1. **Suite completa:** debe ejecutarla quien cierra. Ninguna evidencia que vi la registra sobre este árbol final (entry point en `plan.md:74`).
2. **Decisión sobre este informe:** revisión y aprobación del owner o del orquestador conforme a su mandato, incluida la lectura de R-B.
3. **Stage 5:** Memory Bank y aprobación separada.
4. **R1:** el cierre debe llevar la formulación literal **«La unidad queda cerrada en el repositorio, NO vigente en la instalación»**. Publicar es decisión del owner. La tabla de hashes de `closure-conditions.md` §1 se midió antes del fix, así que debe volver a medirse para citarla. Mi propio prompt de sesión carece del texto nuevo de intake, lo que confirma el límite.
5. **F011:** seguirá en FAIL y debe declararse medido y no oculto. El implementer reportó `182 PASS / 1 FAIL`, igual en la base; yo no lo reproduje. Su condición es «declarado», no PASS.
6. **R3:** las guardas no acreditan obediencia; la mutación por inversión lo demuestra. Tampoco se cerró por ampliar prosa congelada.
7. **Límite de fidelidad del intento 32:** el recibo acredita 2.811 B de confirmación, no el informe sustantivo. Está declarado en `review-fix-t6-report.md:9` y debe seguir visible. Este dictamen no depende de ese informe: verifiqué el diff directamente.

R2 e I-8 siguen fuera de la unidad, en el backlog de la épica.

## Current decisions / ADR

No aplicado: el paquete no declara `current_decisions`. Queda en abstenciones.

## Abstentions

- **Suite completa y `make validate`/F011:** no ejecutados.
- **`tests/test_010_004_t5_properties.py`:** no reejecutado. El código de producto no cambió tras el informe del implementer, que da 2 passed, pero esa cifra no es medición mía.
- **Regeneración con `cmp`:** no repetida. Lo que tengo es `test_cdad_generate.py` en verde dentro de los focales y los tokens en los 20 derivados; `cmp` solo lo reporta el implementer.
- **B4 en lectura completa:** leí hasta `:520` del test y sus helpers. No hice mutación del producto ni leí el cuerpo final de las aserciones.
- **Tabla de decisiones contra `docs/adr/`:** no realizada.
- **Conducta real de un modelo ante A+C o C/v1:** no juzgable aquí (PD-15).
- **Bucket:** asignado por evidencia observada, sin aplicar la regla completa de `verdict-tuple.md`.

## Evidence required

- **Archivos modificados:** ninguno. **Commit:** ninguno. Las fixtures y copias temporales se crearon bajo `~/clawd/tmp/rv002.*` y se borraron. `git status --short` conserva solo `docs/specs/010-000-continuity-relative-root/discovery.md`, que ya estaba.
- **Comandos de admisión:** `cdad_packet.py render --project-root $PWD --request <REQUEST>` con `cmp` contra `PACKET.md`; `render --route C`; `validate-request`; `validate-packet`.
- **Comandos de base:** `git merge-base --is-ancestor 1dd7661f HEAD`, `git rev-list --count`, `git log --oneline`, `git diff --stat`, `git merge-base --is-ancestor 932e0288 1dd7661f` (rc=0).
- **Tests:** `env -u TMPDIR python3 -m pytest tests/test_010_004_t6_red.py tests/test_010_004_t6_b1_guard.py tests/test_010_004_t2_red.py tests/test_010_004_t3_red.py tests/test_010_004_t4_red.py tests/test_010_004_t5_e2e.py tests/test_cdad_generate.py -q` → **30 passed in 44.91s**.
- **Probes:** las salidas de B2, R-A y O-C (reemplazo, resume, publicación parcial) y las 12 mutaciones de la guarda, más la inversión semántica, citadas arriba.
- **HEAD revisado:** `269834d5`.