# Dictamen draft-004

Objeto: `docs/specs/006-006-spec-plan-review/plan.md`  
SHA256: `0c8a8d80a35553cea14f2d15eb1f9b05685e6bace3902cd56b64770b88da48da`

## B-4: cerrado en el diseño

`plan.md:58-70` y `spec.md:170-177` distinguen ahora:

- A→B→A sin `--supersedes`: rechazo por aprobación vigente.
- Con `--supersedes B`: rechazo explícito de colisión, sin escritura.
- Replay de B: no-op.
- Retirada con evidencia distinguible: nueva clave y nueva aprobación vigente.

Contrastado con `cdad_packet.py:5045-5079,5098-5108,5766-5829`: la identidad vuelve efectivamente a A; la búsqueda encuentra A en el historial antes del control de vigencia. La nueva calificación corrige ese recorrido sin cambiar claves históricas.

El cálculo con las funciones actuales y el bloque condicional propuesto produjo:

```text
A->B->A: A_equals_return_key=True A_differs_B=True historical_match=True
reader after B: selected=['B']
distinct artifact: new_key=True selected=['C']
```

Es evidencia del **diseño**, no de una implementación futura.

## B-5 — El oráculo de `prepare` no distingue aprobaciones con el mismo pin

**Verdict: BLOCKING · Bucket: m · Severidad: Required**

**Ubicación:** `plan.md:68-69`; consumidor: `skills/cdad-cycle/scripts/cdad_packet.py:1563-1574,1580-1625`.

El recorrido mantiene iguales los bytes y la ruta del contrato: A y B difieren únicamente en la exención; C añade evidencia. Sin embargo, exige comprobar mediante `prepare` que la aprobación vigente habilita y la sustituida queda bloqueada.

`prepare` recibe el contrato, **no la clave de la aprobación**. El lector excluye entradas sustituidas y busca una aprobación cuyo pin coincida. Con B vigente, el contrato que antes aprobó A también pasa: es exactamente el mismo contrato. Después de C sucede lo mismo respecto de B.

**Consecuencia:** el RED central no puede satisfacer literalmente el bloqueo declarado mediante ese consumidor. No es una variante nueva: afecta al recorrido obligatorio usado como evidencia de cierre de B-4.

**Movimiento propuesto:** separar dos comprobaciones:

1. El selector real de vigencia devuelve únicamente B —y después C—, excluyendo las claves sustituidas.
2. `prepare` acepta el contrato aprobado; no se le atribuye capacidad de distinguir qué entrada histórica presentó el solicitante.

**Cierre verificable:** corregir ese oráculo en las fichas y checks de U5/U6, conservando los rechazos, no-op, invariancia del estado y selección de vigencia ya exigidos.

## Idempotencia histórica: B-3 conservado

No identifico otra regresión de diseño sobre **005-014 PD-23** ni **006-005 PD-19(b)**:

- `plan.md:58-60,70-74` conserva las 16 claves sin exención.
- La nueva calificación queda limitada al `gate specification` con pin y aprobación competidora.
- `closure` y `disposition` conservan su ruta de replay.
- Sus regresiones están declaradas sin modificar oráculos: `tests/test_005_014_closure_replay.py:220-275` y `tests/test_006_005_u5_disposition_failed.py:376-411`.

Cálculo de identidad:

```text
gate:        payload_equal=True key_equal=True keys=16
closure:     payload_equal=True key_equal=True keys=16
disposition: payload_equal=True key_equal=True keys=16
```

## E1–E6

Citas relativas a la carpeta de esta feature:

- **E1:** PD-1/3/5/7/10/12–15 → U1–U4/U6; spec sin tareas artificiales, recepción y destino declarados (`plan.md:41-47,81-96,116`).
- **E2:** PD-1–5/8/13/15 → U1/U6; ambos digests fijados y checks sobre el plan (`:44-45,117`).
- **E3:** PD-1/4–7/13 → U1/U2/U6; objeto B, ejecución y destino A (`:81,118`).
- **E4:** PD-8/10/12/13 → U2/U3/U6; cambio de digest y re-review focal (`:90,119`).
- **E5:** PD-7/14/15 → U1/U3/U6; dictamen separado de aprobación (`:47,95-96,120`).
- **E6:** PD-10/12/13 → U2/U3/U6; intención incumplida como bloqueante semántico, evidencia textual (`:81-83,90,121`).

## Validación y evidencia

Separada del juicio semántico:

- Hashes del contrato, política y tres fuentes: coinciden con el paquete.
- `plan-tasks`: JSON válido; seis tareas; dependencias existentes y acíclicas; validación por tarea presente.
- Comandos de verificación: `sha256sum` sobre los archivos declarados; `git rev-parse HEAD`; `git status --short`; `git log --oneline 7f39e24..HEAD -- skills/ sources/ agents/ scripts/ assets/`; `python3 -B -` para extracción AST, cálculo y validación estructural.
- El `git log` acotado no produjo entradas.
- Commit observado: `448e1b44b87e3811ff9c861b3c160dcf8ea469c6`.
- **Archivos modificados:** ninguno; estado Git final igual al inicial.
- **Commit propio:** ninguno. No ejecuté tests ni suite completa.

## Abstentions

- No certifico RED/GREEN ni aceptación real del producto futuro.
- No tengo evidencia para acreditar independencia de familia de modelo respecto del autor.

**Veredicto final: requiere cambios por B-5. B-4 queda cerrado como defecto de diseño; no se aprueba ni autoriza implementación.**