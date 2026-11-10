# ADR-043: Lote paralelo por archivo con veredicto fail-closed

- **Status**: Accepted (decisión delegada del dueño, epic-017, 2026-11-08).
- **Origen**: `docs/specs/017-001-suite-performance/performance/parallelism.md` (contrato del lote y
  decisión), `docs/specs/017-001-suite-performance/acceptance.md` (PC-9/PC-10) y el cierre del epic 017.
- **Alcance**: la herramienta de suite **de este proyecto** (`scripts/cdad-suite.py`). **No** decide la
  promoción del paralelismo a capacidad del ciclo CDAD: eso exige una unidad nueva (workers configurables
  en la herramienta del ciclo, reglas de tests paralelizables y declaración de aislamiento por módulo) y
  no se abre aquí.

## Contexto

La suite completa medía **4994.27 s** y la preparación reducible demostrada era **nula**: de **76**
invocaciones de `install.sh`, **0** son preparación pura compartible (47 acción bajo prueba, 29 mixtas).
Con la poda prohibida por el contrato del epic, la única palanca de tiempo de pared que no cambia lo
verificado es ejecutar en paralelo. El dueño decidió paralelizar con workers configurables y sin usar todos
los núcleos, exigiendo demostrar aislamiento antes de aplicar.

## Decisión

1. **`close` queda serial e intacto.** El paralelismo es un **subcomando separado** de solo ejecución, no un
   modo de `close`; el camino serial permanece disponible en cualquier entorno.
2. **Partición por archivo, nunca por test suelto**: conserva el orden interno de cada archivo y no separa
   clases ni fixtures. Workers configurables: **default 2**, rango `1 <= N <= nproc-1`, nunca todos los
   núcleos por defecto.
3. **Cada worker es un proceso pytest independiente** con `HOME`, `XDG_*` y `TMPDIR` propios y su propio
   subdirectorio de evidencia. El agregado informa por worker y en total: pared de cada worker y pared
   total, Σ fases rotulada como **trabajo medido** y nunca como pared, solapamiento, preparación duplicada
   y trabajo sumado **aparte** — nunca presentados como ahorro.
4. **Veredicto fail-closed.** La corrida **no se acepta** si falta el subreaper o el barrido de `/proc`, si
   el barrido es incompleto, si el canario detectó cambios o si el directorio de evidencia ya estaba
   poblado. El canario del checkout se toma **después** de resolver la familia de procesos y se decide por
   **contenido** (`sha256` por archivo sobre rutas ordenadas), no por `mtime`.
5. **Los tests no escriben scratch dentro del checkout.** La raíz temporal de un test va fuera del árbol
   vigilado: con dos workers, el scratch de uno hace que el canario del otro rechace la corrida.

## Consecuencias

- La corrida final sobre `bf0e7483` midió **4459 s → 2593.15 s (−41.84 %)** con equivalencia exacta por
  nodeid (2059 vs 2059; 2054 passed + 5 skipped en ambos).
- Costo asumido y declarado: preparación duplicada por worker (**16.34 s** en la corrida final) y trabajo
  sumado mayor que la pared por concurrencia; ambos se informan aparte.
- La garantía de familia de procesos **requiere Linux** (`prctl` + `/proc`); fuera de ella el lote no se
  acepta.
- La huella del checkout no detecta cambios de modo ni directorios vacíos; se declara en lugar de
  presentarla como cobertura total.
- `close` sigue sin instrumentar carga del host ni canario del checkout: límite declarado del camino
  serial, no condición demostrada.
- La promoción a capacidad de CDAD queda **pendiente** y no se deriva de este ADR.
