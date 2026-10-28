# ADR-039: El verde de un gate es atribuible o no es verde

- **Status**: Proposed (pendiente de ratificación del dueño; epic-008, `008-005-ci-gate`).
- **Date**: 2026-10-28
- **Confidence**: **Media** — el mecanismo está evidenciado (19 tests con control negativo y tres corridas
  consecutivas verdes), pero **no se ha ejercido en su disparador**: no existe workflow versionado y crearlo
  exige una enmienda de política del dueño. La decisión rige hoy en local; su extensión al push está
  pendiente.
- **Origen**: `docs/specs/008-005-ci-gate/spec.md` (D1–D10, PC-1..PC-8), `docs/ci-gate.md` y su `closure.md`.

## Contexto

En `008-004` la suite produjo **siete falsos rojos** en dos corridas consecutivas por cotas de reloj de pared
con el host cargado (`loadavg` 5.4–6.9 sobre 8 CPU), verdes en aislamiento; la única corrida verde de la
unidad era **anterior** al commit final. El resultado fue honesto e inservible como gate: «pasó una corrida»
no decía **qué** se probó, **sobre qué árbol** ni **con qué intento**. El mecanismo de cierre de `008-002` ya
sabía reservar un intento y preservar su evidencia; lo que faltaba era un criterio que decidiera cuándo ese
resultado **cuenta**.

## Decisión

1. **Un solo entrypoint** (`scripts/cdad-ci-gate.py`) corre los gates compartidos en orden fijo, cada uno
   **una vez**: `validate-state`, superficie (sólo clasificación), doctrina, especialización Odoo y
   `close --all` — la **única** corrida de pytest.
2. **El gate invoca, no reimplementa.** Cada paso conserva su dueño y su contrato.
3. **Un `0` es atribuible o no es `0`**: exige commit no nulo, `dirty == 0`, **exactamente un** intento en
   estado `finished`, `pytest_summary.verified` y `rc == 0`. Cualquier otra combinación sale distinta de cero
   **nombrando la causa**.
4. **No se reintenta, no se promedia y no se elige ganador.**
5. **Cada corrida deja evidencia propia** (`gate.json`, `suite-report.md`, el intento); una corrida no pisa ni
   adopta otra.
6. **La aplicabilidad se decide por la clasificación de la política**: un cambio que sólo toca documentación
   no ejecuta el paso de superficie y **la suite corre igual**.
7. **El canario y la carga se informan y no deciden.**
8. **El gate no publica, no instala, no usa red ni credenciales** y es neutral de proveedor.

## Alternativas rechazadas

- **Confiar en el `rc` de pytest y en el resumen tal como se imprime.** `PYTEST_ADDOPTS='-qq'` producía «cero
  aprobados con rc 0»: el resumen sin verificar no distingue «no corrió» de «pasó».
- **Un workflow por proveedor como fuente de verdad.** Acopla el criterio a un proveedor, no es verificable
  en local y no corre en un checkout sin red.
- **Reintentar hasta el verde, o promediar intentos.** Convierte un defecto de estabilidad en ruido
  administrado.
- **Un gate que reimplementa los pasos.** Dos definiciones de lo mismo (mismo criterio que ADR-036).
- **Excepción docs-only sobre la corrida de la suite.** Debilitaría por cuenta propia el criterio del epic; es
  decisión del dueño.

## Consecuencias

**Positivas.** «Verde» pasa a ser un hecho verificable y repetible en local, con la causa del rojo a la vista.
El orden fijo y la corrida única hacen que un gate cueste una suite y no dos. El veredicto no depende del host.

**Negativas / límites.** Costo: una suite completa por corrida (46–103 min medidos, sin paralelismo), y el
criterio del epic pide la suite en cada push. **Sin workflow versionado no hay activación en el push**:
`.github/**` y `Makefile` son `unclassified`, y versionarlo exige enmienda de política del dueño. `make
validate` queda fuera (necesita instalar agentes en un HOME real). El motivo de un fallo se atribuye leyendo
la salida de pytest: es best-effort y puede quedar `null`. La clase «esperó **por encima** de la cota» no es
observable con el envelope actual (F1, `deferred-hardening`).

## Cumplimiento

`tests/test_008_005_ci_gate.py` — **19 tests**, con control negativo contra `df5af77` (3 fallan por la razón
correcta); 17 sitios de cota con par declarado y la pérdida F1 registrada. Evidencia: tres corridas
consecutivas de `scripts/cdad-ci-gate.py --base HEAD~1` sobre `443a43d`, árbol limpio, `verdict green`,
`attributable true`, canario 0, **1827 passed / 5 skipped** con `loadavg` 5.26–6.43, en
`.cdad/local/008-005/epic-runs/`.
