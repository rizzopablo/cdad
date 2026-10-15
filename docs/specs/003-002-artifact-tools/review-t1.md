# Review — T1 (003-002): `receive` atómico e idempotente

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-32>`.
> Paquete: `003-002-artifact-tools-reviewer-review-001`.
> Objeto: diff `02ebb0e..3f619c4` contra `spec.md` (P1/P2/P3/P6 base) + `plan.md` T1.
> **Dictamen: 3 BLOCKING (R1, R2, R3) + R4/R5 opcionales + 6 nits.**

## 0. Identidad del contrato y evidencia

| Chequeo | Resultado |
|---|---|
| `sha256sum …/spec.md` | `ba73e645…f37` — coincide con el packet ✅ |
| Focales T1 (`unittest discover`) | **7/7 OK (5.536 s)** — corrida por el reviewer ✅ |
| Sintaxis (`ast.parse`) | OK ✅ |

**Commits del rango (atribución limpia):** `02ebb0e` RED (solo el test, +791) · `e116d38` orquestador (state + ledger) · `3f619c4` implementer (exactamente los 5 archivos declarados; no toca tests ni state) ✅.
**Evidencia citada, NO verificada por el reviewer (PD-5):** suite completa del implementer, **371 passed / 493 s** (el proceso murió con la sesión; el árbol de código no cambió desde esa corrida).

## Hallazgos

### R1 — Junction de part con `name` controlado por el input en `_verify_durable` · **BLOCKING · bucket m · Required**

`skills/cdad-cycle/scripts/cdad_result.py:348-351`: `stored = final_dir / "parts" / f"{name}.utf8"`; el único chequeo de `name` es "string no vacío" (:349). En el flujo `validate-receipt` (CLI :535-542) el recibo es **input del caller**: un recibo forjado con `parts[i].name = "../../../x"` resuelve y **lee archivos fuera del project root**. El resto del módulo proyecta input a path vía `_segment`/`_project_path` (p. ej. `:202`).
**Remedio:** `_segment(part.get("name"), "durable receipt part name")` antes de construir el junction — cubre ambos call sites (:344 retry, :542 validate-receipt).

### R2 — Batería RED de T1 incompleta vs. plan aprobado · **BLOCKING · bucket m · Required**

`plan.md` T1 declara la verificación RED como "…retry/interrupción/dos procesos"; el test RED (7 métodos) cubre retry pero **no** kill-antes-de-rename ni receives concurrentes. Los dos únicos caminos de convergencia de `_publish` (`:421-424`, `:521-528`) quedan sin observable, y el criterio de aceptación de la spec ("dos procesos concurrentes idénticos convergen") va declarado sin prueba.
**Remedio:** 2 tests en el archivo focal: (a) kill de un subprocess antes del publish → sin finalización, el retry completa; (b) dos `subprocess.run` idénticos en carrera → ambos rc=0, un solo `receipt.json`, mismo stdout byte a byte.

### R3 — Scope-validation positivo con cambios in-scope nunca ejercitado · **BLOCKING · bucket m · Required**

Los únicos manifests con cambios son el negativo y el ausente; los `scope_validation="passed"` se obtienen con `changes=[]`, lo que hace vacua toda la lógica `_scope_contains`. El ramal de `renamed`/`previous_path` (`:304-305`) queda sin prueba.
**Remedio:** 1 test con manifest trusted + change in-scope (`tests/…` bajo write_scope `{"class":"tests","root":"tests"}`) → rc=0, `scope_validation="passed"`; 1 variante con `previous_path`.

### R4 — Reutilización de `_scope_contains` (pregunta del encargo) · OPTIONAL · bucket m

La dirección es **correcta** (una sola semántica de scope, consistente con los selectores reales de los packets). El riesgo es **acoplamiento a API privada** y que `_project_path` está **copiado literalmente** (`:115-129` vs `cdad_packet.py:147-161`): dos copias del primitivo de seguridad de path que pueden divergir.
**Remedio:** promover a names públicos (o módulo compartido) `scope_contains` + `project_path` y borrar la copia local; T2/T3 consumen la fachada.

### R5 — `validate-receipt` declarado en alcance T1, cero observables · OPTIONAL · bucket m

`plan.md:80` incluye `validate-receipt` en T1; no tiene tests (positivo ni negativo).

### R6 — Nits mecánicos · OPTIONAL · bucket l

1. `_fsync_dir` traga errores en silencio (`:326-334`).
2. Tras `os.rename` no se hace fsync del `parent`.
3. El límite de 1 MiB se chequea **después** de leer la part completa en memoria (`:218`, `:233-235`).
4. `HEX_RE.fullmatch(str(manifest.get("baseline_sha256")))` (`:257`) acepta un JSON integer de 64 dígitos como si fuera hex.
5. Tmp dirs de procesos matados (`:408-410`) quedan sin limpiar.
6. En el retry (`:444-447`) los args `--execution-context/--packet/--request` se ignoran por completo (coherente con §5, pero deja pasar un descriptor con identidad discordante).

## Lo que está sólido (observado)

- P1/P3/P6 base con focales verdes corridos por el reviewer (7/7); el stdout byte-a-byte del receipt y la no-escritura fuera de `.cdad/runtime/` están asercionados por árbol completo; la no-escritura de state/contexto es explícita por bytes.
- Atribución de commits impecable (el implementer no sobrepasó el write_scope).
- `receive` falla **antes de publicar** en todos los ramales negativos; los fixtures negativos aserciónan árbol sin delta y stdout vacío.
- El wrapper `scripts/cdad_result.py` es genuinamente delgado (runpy) y los focales lo ejercitan.

## Abstenciones

1. Suite completa citada del implementer, no medida por el reviewer (el proceso murió con la sesión).
2. Comportamiento de race no probado empíricamente (análisis POSIX, no corrida viva).
3. Los 3 schemas JSON no se validaron contra un validador JSON Schema (consistencia por lectura).

## Dictamen

T1 GREEN es **funcionalmente sólido en su superficie y limpio en propiedad de escritura/commits**, pero **no es mergeable directo**: 3 bloqueantes exigen un ciclo de corrección (R1 una línea de código + tests; R2/R3 la batería focal que el plan declara). Ruta recomendada: RED (R1 negativo + R2/R3/R5 locks) → review-fix GREEN (R1, R4 fachada) → re-review focal.
