# Contrato de la corrida final — T7 (017-001-suite-performance)

Fijado antes de ejecutar (plan T7: «antes de consumir la corrida final se fijan
candidata, base honesta del gate, selección vigente, condiciones y evaluación
del objetivo»). No sustituye al contrato aprobado: lo operacionaliza.

## Candidata

- Una sola revisión: el commit de cierre que resulte de aprobar T6, con árbol
  limpio (`dirty = 0`). Serial y paralelo se ejecutan sobre esa misma revisión.
  Revisión fijada: `a1209087` + el commit de cierre de T6 que lo sucede; la
  corrida aborta si el árbol no está limpio al arrancar.
- Nota operativa: `docs/.cdad-state.json` cambia con cada `begin`/`receive`. La
  corrida se lanza con el estado commiteado y **no** se escribe en el repo
  hasta que termina el par; de lo contrario `dirty` deja de ser 0 en una de las
  dos corridas y la comparación queda invalidada (ocurrió y se descartó un par
  completo por eso).
- No se modifica ningún archivo entre las dos corridas; si hiciera falta un
  cambio, se descarta la corrida y se repite el par completo.

## Selección

- **Suite completa**: `--all` (2034 nodeids en la revisión de la base).
- No se admite recortar la selección para alcanzar el objetivo. Si un archivo
  demuestra colisión real de recursos en el lote (evidencia, no sospecha), se
  documenta, se excluye con lista explícita y la comparación se hace sobre el
  resto **declarando la diferencia de cobertura**; esa exclusión no puede
  presentarse como reducción de pared.

## Condiciones

- `--workers 2`, `--balance-from <profile.json de la corrida serial de la misma
  revisión>`.
- Carga del host registrada en ambas corridas (`parallel.json.host` y el
  journal del intento serial); misma máquina, mismas variables de entorno del
  suite, sin otras suites corriendo.
- Canario de configuración y canario del checkout (`build/`, `.cdad/`) limpios
  en ambas corridas.
- Evidencia cruda en rutas estables del workspace
  (`evidence/017-001-final/serial` y `.../parallel`) y copia de solo lectura
  dentro del repo (`.cdad/tmp/017-001-final-evidence/`) para revisión.

## Regla de evaluación (PC-4, registrada en `parallelism.md`)

```
(pared_serial - pared_paralela) / pared_serial >= 0.15
```

**y** conjuntos de `passed/failed/skipped` idénticos por nodeid, **y** cero
fallos, errores o skip no declarado en ambas corridas.

- `pared_serial`: `T_exterior` del comando `close --all` (reloj de pared,
  resolución 1 s).
- `pared_paralela`: `total_wall_s` del comando `parallel --workers 2` (ventana
  de ejecución concurrente; el barrido de canario queda fuera y se informa
  aparte como `command_wall_s`).
- No se usa la suma de tiempos concurrentes como pared. El trabajo medido
  (`total_work_s`) y la preparación duplicada (`duplicated_preparation_s`) se
  informan por separado y no se presentan como ahorro.

## Comparación de resultados

- Se comparan los nodeids ejecutados, no solo los totales: el consolidado del
  lote debe cubrir exactamente los mismos nodeids que la corrida serial y el
  mismo resultado por nodeid.
- Diferencias de skip se listan; un skip nuevo respecto de la base se declara
  con su motivo.
- El conteo de tests ejecutados debe coincidir con el de la corrida serial; un
  worker que no ejecuta su partición es un fallo, no un ahorro.

## Atribución final

- `reconcile` sobre el intento serial produce `reconciliation.json` con los
  totales de corrida (preparación, resto, `R_pytest`, `R_exterior`) y la cota de
  redondeo.
- El resto no desglosado se publica como **desconocido**, con el alcance
  medido en `remainder-measurement.md` (75 % externo en la muestra más cara) y
  la regla de la spec: no se clasifica por descarte.
- `comparison.json` registra las dos corridas, sus revisiones y condiciones, la
  pared de cada una, el porcentaje de reducción, la equivalencia de resultados
  y el veredicto frente al objetivo.

## Cierre

1. Review independiente sobre la candidata: `validate` a la entrada, integridad
   de la evidencia, comparación reproducible desde los JSON, sin bloqueantes.
2. Aceptación del dueño sobre spec §7 (la firma la ejecuta el orquestador).
3. `progress.md`, Memory Bank y unidad nueva de CDAD para paralelismo como
   capacidad (reglas de tests paralelizables, declaración de aislamiento por
   módulo, runner en la herramienta del ciclo).

## Qué no autoriza este contrato

- No autoriza una segunda corrida completa «por si acaso»: una repetición exige
  autorización suficiente y un motivo declarado, y nunca se usa para esconder un
  rojo.
- No autoriza a tocar tests para llegar al objetivo.
- No autoriza a publicar ni desplegar (reservado al dueño).

## Condiciones no instrumentadas en la pierna serial (declarado)

`close` **no registra** la carga del host ni toma canario del checkout; solo
`parallel` lo hace. Por lo tanto, de las condiciones fijadas arriba, en la
pierna serial **no quedan demostradas** la carga del host ni el canario del
checkout, y no se presentan como demostradas.

Lo que sí queda registrado y es verificable en ambos intentos:

- `commit` idéntico en `attempt.json` (serial) y `parallel.json`, con
  `dirty: 0` en los dos;
- resultados idénticos por nodeid (2059 en cada régimen, 0 diferencias);
- la pared serial es consistente con las corridas seriales previas de la
  feature (4235 s, 4239 s, 4370 s, 4459 s: ±5 %), sin indicio de anomalía.

Eso es evidencia de consistencia, **no** una medición de la carga ni del
checkout en la pierna serial. La carencia se registra como límite declarado y
como mejora pendiente: `close` debe instrumentar carga y canario del checkout
igual que `parallel`, para que un contrato futuro pueda exigirlas en ambas
piernas sin depender de un proxy.
