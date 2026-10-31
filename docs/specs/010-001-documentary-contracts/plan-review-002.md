# Dictamen de re-verificación: plan-review 002, 010-001-documentary-contracts

**Objeto revisado:**
- `docs/specs/010-001-documentary-contracts/plan.md`, versión 3, sha256 `9fee79a36dccb0faf6dbe9372f7d946e9aebf4886844b80162eb399fd506a478`.
- `docs/specs/010-001-documentary-contracts/spec.md`, draft-3, sha256 `a01969d7f51da614c6e502d8660bafea17ad5ae8bb7caf5aea624f43927d94ac`.

**Dictamen: NO LISTO PARA APROBACIÓN, con 1 bloqueante nuevo (N1).** F1 quedó cerrado, igual que F3, F4, F5 y F6. F2 queda cerrado con reparo: cumple la condición que fijó el dictamen anterior, pero esa misma condición era inejecutable, y de ahí sale N1. Este dictamen no aprueba nada ni autoriza implementar; la decisión es de Pablo.

## Estado de F1–F6

| Hallazgo | Estado | Evidencia frente a la condición de cierre |
|---|---|---|
| **F1** (bloqueante) | **Cerrado** | PC-12 dice «usuario/dueño que aprueba» (`spec.md:164`). INV-07 limita el nombre concreto a los documentos de autoridad bajo `docs/` (`spec.md:188`). `rg Pablo skills sources agents` no da coincidencias. Las menciones restantes están solo en `docs/`, por ejemplo `spec.md:201`. |
| **F2** | **Cerrado con reparo** | T1 prepara solo T2/T3, y los encargos posteriores se preparan justo antes de su despacho (`plan.md:39,42,181`). T4 declara obsoletos los paquetes anteriores (`plan.md:120,273`). Reparo: ver N1. |
| **F3** | **Cerrado** | PC-13 y el grupo D declaran unicidad por frases derivadas de la referencia, con espacios normalizados, sobre `skills/`, `sources/` y `agents/` (`spec.md:170`, `plan.md:205`). Coincide con el precedente (`tests/test_006_004_u3_principle_single_source.py:52-57`). |
| **F4** | **Cerrado** | T2 compromete `TestPromiseA` a `TestPromiseD` (`plan.md:59,207`) y T3 fija un comando exacto (`plan.md:84,252`). Sin `tests/__init__.py`, el import y la selección por clase funcionan desde la raíz; lo comprobé con módulos existentes. |
| **F5** | **Cerrado** | PC-10 incorpora el contenido de INV-08 (`spec.md:160`), y PC-10 pertenece al grupo C. T5 lo verifica expresamente (`plan.md:142,313`). |
| **F6** | **Cerrado** | T5 dice D1–D4 (`plan.md:142,310`). |

## Bloqueantes nuevos

### N1 — Required: T1 no puede preparar T2 y T3, porque solo admite un paquete activo
- **Verdict:** BLOCKING
- **Bucket:** h
- **Ubicación:** `plan.md:39`, `plan.md:42`, `plan.md:181`.
- **Evidencia:**
  - El estado guarda un único `active_packet`.
  - `prepare` rechaza un paquete nuevo mientras el anterior publicado siga `prepared` o `dispatched`: «complete or fail it before preparing a new packet (PD-4)» (`cdad_packet.py:6468-6489`).
  - La única salida anticipada es un recibo durable de un paquete ya `dispatched`, y T2 no puede tenerlo durante T1.
  - El bloque distingue además «T2/T3» de «posterior a T3», así que no admite leer que T3 se prepara después de T2.
- **Origen:** la corrección aplicó fielmente la condición de cierre de F2 del dictamen anterior. El defecto está en esa condición, no en el autor.
- **Consecuencia:** el gate de T1 no se puede cumplir tal como está escrito. Al preparar T3, la herramienta falla de forma cerrada y el orquestador tendría que apartarse del plan aprobado.
- **Condición de cierre:**
  1. T1 prepara y valida únicamente T2.
  2. T3 y todos los encargos siguientes se preparan y validan justo antes de su despacho, tras cerrar el encargo anterior.
  3. Se ajustan `plan.md:39,42,181` y se sincroniza `plan.md:207`, que ya admite esa secuencia.

## Observaciones no bloqueantes

### N2 — Consider: T4 detecta un fallo que no puede corregir
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `plan.md:84`, `plan.md:103-111`, `spec.md:170,172`.
- **Evidencia:**
  - PC-13 y PC-14 cubren `sources/` y `SKILL.md`, pero pertenecen al grupo D.
  - T3 ejecuta solo A–C, y T4 no incluye esas rutas entre sus archivos.
- **Consecuencia:** una frase duplicada o un puntero mal resuelto en una fuente aparece recién en T4, fuera de su alcance. Falla de forma cerrada y cuesta un ciclo de vuelta a T3.
- **Condición de cierre:** el paquete de T3 ejecuta también las comprobaciones de D que no dependen de la distribución, o el plan declara que ese fallo vuelve a un despacho GREEN de T3.

## Resto de la verificación

- **Contrato:** no encontré contradicciones nuevas entre F1, PC-10, PC-13 e INV-07/08. La redacción genérica de PC-12 mantiene la autoridad en el aprobador humano.
- **Trazabilidad:** PC-01–16 siguen asignadas a los grupos A–D y a T5.
- **`plan-tasks`:** `_plan_tasks_from_contract`, `_check_plan_tasks` y `_check_plan_validation_plan` pasan con T1–T6. Este verde es solo estructural: no detecta N1.

## Abstentions

- **`prepare` real:** no ejecuté la secuencia T2→T3, porque modificaría el estado. N1 se apoya en la lectura del código y en el estado actual.
- **Agentes tras T4:** sigo sin poder juzgar el DRIFT de los agentes ni su efecto en T5/T6, porque no ejecuté `make agents` ni la instalación.
- **Citas y decisiones:** no reverifiqué todas las citas de línea ni la tabla de `docs/adr/`, por el alcance acotado de esta pasada.
- **Buckets:** los asigné sin leer `references/verdict-tuple.md`; son orientativos.

## Evidencia

**Intake (ruta C):**
- Contexto de ejecución schema 2.
- `validate-request`: rc=0.
- `validate-packet`: rc=0.
- `PACKET.md` idéntico al render canónico completo (7979 bytes).
- Identificación de ruta C coincidente con la recibida.
- Los dos sha256 del contrato coinciden con los archivos.

**Comandos** (con `E=.cdad/executions/exec-010-001-documentary-contracts-002/execution.json` y `P=.cdad/packets/010-001-documentary-contracts-reviewer-plan-review-002`):

```bash
C="python3 -B skills/cdad-cycle/scripts/cdad_packet.py"
$C validate-request --project-root . --execution-context $E --request $P/REQUEST.json
$C validate-packet --project-root . --execution-context $E --request $P/REQUEST.json --packet $P/PACKET.md
$C render --project-root . --execution-context $E --request $P/REQUEST.json > /tmp/rv2.md
cmp /tmp/rv2.md $P/PACKET.md
$C render --project-root . --execution-context $E --request $P/REQUEST.json --route C
sha256sum docs/specs/010-001-documentary-contracts/*
rg -n "Pablo" skills sources agents -c
python3 -B -c "import tests.test_006_004_u3_principle_single_source as m; print(m.__file__, m.__spec__.name)"
python3 -B -m unittest -v tests.test_cdad_generate.TestDeterministicGenerator
git status --short
```

Las comprobaciones de `plan-tasks` se ejecutaron en memoria con `runpy.run_path` sobre `cdad_packet.py`.

**Salidas relevantes:**
- `plan-tasks`: `['T1', 'T2', 'T3', 'T4', 'T5', 'T6']`, sin error.
- `rg` sobre `skills sources agents`: sin coincidencias.
- `TestDeterministicGenerator`: 10 tests, OK.
- Estado actual: `active_packet` es este paquete, en `prepared`.
- `git status --short` muestra las mismas tres rutas preexistentes.

**Archivos del repositorio modificados:** ninguno. **Commit:** ninguno. Escribí `/tmp/r.out`, `/tmp/r.err` y `/tmp/rv2.md`, fuera del repositorio. No ejecuté suite completa, generación ni instalación.
