# Contrato del agregador y de la condición de entrada — T3 (017-001-suite-performance)

Fijado por el orquestador antes del despacho de T3, según `plan.md` T3
(`resolves_when`) y `spec.md` §4.4 + «Condición de entrada a la base». No
sustituye al contrato aprobado: lo operacionaliza.

## Comandos (superficie fija)

Sobre el mismo instrumento versionado de T1/T2:

```
python3 scripts/cdad-suite.py reconcile --attempt <attempt-dir> --out <out-dir> [--register <operation-scope.json>]
python3 scripts/cdad-suite.py entry-check --attempts <mapping.json> --out <out-dir> [--register <operation-scope.json>]
```

- `reconcile` agrega **un** intento (una corrida hija). Escribe
  `<out>/reconciliation.json` y `<out>/reconciliation.md`.
- `entry-check` comprueba la condición de entrada a la base sobre un mapa
  explícito selección→intento (`{"C-R": "<attempt-dir>", ...}`). Escribe
  `<out>/entry.json` y `<out>/entry.md`.
- Códigos de salida de ambos: `0` reconciliación/comprobación producida (aunque
  haya diagnósticos), `1` condición de entrada **no** satisfecha (solo
  `entry-check`), `2` entrada inutilizable (falta `profile.json`/`attempt.json`,
  JSON inválido, mapa incompleto). Siempre se informa por stderr el motivo del 2.
- Ambos son de solo lectura sobre la evidencia: no reescriben el intento, no
  reejecutan pytest, no tocan el checkout.

## Entrada

`attempt-dir` contiene, como los produce T1/T2: `profile.json` (fases,
operaciones con `started`/`finished` monotónicos del hijo, `owner_scope`,
`parent_id`, `phase`, `termination`, `duration_s`; `status`, `diagnosis`,
`capture_errors`, `operation_errors`, `pytest_wall_s`, `operation_scope`) y
`attempt.json` (`started_at`, `finished_at`, `commit`, `dirty`, `rc`,
`selection`, `pytest_summary`).

`--register` por defecto es el registro del propio perfil
(`profile.operation_scope.path`); si no se indica ni existe, la cobertura contra
registro se informa como `unavailable` y no se inventan conteos esperados.

## Reglas contables (spec §4.4)

1. **`S_test`** = suma de `duration_s` de las fases observadas de ese nodeid.
2. **Preparación medida** = tiempo exclusivo de las operaciones de alcance
   `test` de ese nodeid: **unión** de sus intervalos `[started, finished]`.
   Anidados y solapados no se suman dos veces; el hijo incluido en el padre se
   informa como desglose, nunca como costo adicional.
3. **Resto del test** = `S_test − preparación_medida`, con signo explícito.
   Puede ser negativo: eso es un diagnóstico de discrepancia, no un cero.
4. **Compartido** (`owner_scope: shared`): se informa en bloque propio; **no** se
   adjudica al primer test ni se resta de ningún `S_test`.
5. **`S_file`** = suma de `S_test` de sus nodeids. Las operaciones compartidas
   externas a esos tests quedan separadas.
6. **Corrida**: `T_pytest = profile.pytest_wall_s`; `R_pytest = T_pytest − Σ S_test`;
   `T_exterior` = `attempt.finished_at − attempt.started_at` (reloj de pared,
   resolución 1 s declarada); `R_exterior = T_exterior − T_pytest`.
7. Lo no identificado permanece como residual con alcance y signo. No se
   etiqueta como preparación por descarte ni se fuerza una identidad a cero.
8. Redondeo: se publican valores con 3 decimales y se declara la resolución de
   cada reloj; la comparación usa tolerancia `1e-3` s (o la resolución declarada
   si es mayor).
9. Orden: tests y archivos por costo descendente; empates por nodeid ascendente
   (salida determinista byte a byte para la misma entrada).

## Cobertura contra el registro

Para cada operación esperada del registro aplicable a la selección del intento,
se compara el conteo observado con el esperado (`expected` del registro, sea
entero o por rama/`total`). Códigos de diagnóstico:

- `missing-operation-vs-register`: esperada > observada (bloquea entrada).
- `unexpected-operation`: observada > esperada (diagnóstico, no bloquea por sí
  solo si la operación existe en el registro).
- `operation-without-register-entry`: operación observada que el registro no
  declara (diagnóstico).
- `profile-incomplete`: `status != complete` (bloquea entrada).
- `capture-error` / `operation-error`: tal cual del perfil (bloquean entrada).
- `attribution-exceeds-phases`: preparación_medida > `S_test + tolerancia`.
- `residual-sign`: `R_pytest` o `R_exterior` negativo fuera de tolerancia.
- `scope-unavailable` / `scope-not-calibrated`: registro ausente o
  `calibrated != true` (el segundo bloquea entrada).

## Condición de entrada (`entry-check`)

`entry.satisfied = true` solo si **todas** se cumplen, cada una como check
nombrado y verificable en `entry.json`:

1. `register-calibrated`: registro `calibrated: true` y `status: calibrated`.
2. `selection-coverage`: toda selección requerida tiene intento en el mapa y el
   mapa no trae entradas sin selección en el registro. Requeridas = las
   selecciones con `required_for_current_calibration != false`.
3. `attempts-complete`: cada intento con `profile.status == complete`, sin
   `capture_errors` ni `operation_errors`.
4. `counts-match-register`: sin `missing-operation-vs-register` en ningún intento.
5. `evidence-locatable`: cada intento declara `commit` y una ruta existente con
   `profile.json` y `attempt.json`.
6. `unknowns-declared`: el registro declara los desconocidos con regla de
   decisión (`volume_observations.*.unknown_component.decision_rule` presente) y
   un intento por selección no requerida no es obligatorio.

Cualquier check falso deja `satisfied: false`, enumera el motivo y hace que
`entry-check` salga `1`. La base no se inicia en ese estado (spec §4.4).

## Casos contables mínimos que el oráculo debe cubrir

1. Dos tests con fases y preparación: `S_test`, atribuido y resto correctos.
2. Anidamiento padre/hijo: el hijo no se suma aparte; el padre aparece como
   desglose.
3. Solapamiento parcial entre hermanos: unión, no suma.
4. Operación compartida: fuera de todo `S_test`, en bloque propio.
5. Residuo positivo de corrida y de exterior, con signo y resolución.
6. `status: incomplete`: reconciliación producida y entrada bloqueada con el
   diagnóstico del perfil.
7. Conteo faltante contra registro: `missing-operation-vs-register` y entrada
   bloqueada.
8. Determinismo: misma entrada ⇒ mismo `reconciliation.json` byte a byte.

## Fuera de alcance de T3

No se ejecuta la corrida base (T4), no se optimiza (T5), no se decide
paralelismo (T6) y no se extrapola ninguna muestra focal a la suite completa.
