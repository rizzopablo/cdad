# Discovery — 017-001-suite-performance

**Borrador para decisión del dueño. No es una spec ni una solución aprobada.**

## 1. Alcance y resultado

Ruta C validada: REQUEST válido, contrato con SHA256 coincidente, contexto v2 y `PACKET.md` idéntico al render canónico completo —7577 bytes—.

Inspección sobre `HEAD c3c38c5d1a7f2d362bc026edf4863e1e1ca82c4d`, con cambios documentales preexistentes. Fuentes admitidas: los inputs del packet y lecturas dirigidas dentro del repositorio. **No ejecuté tests, suite completa, generación ni instalación; no modifiqué archivos.**

**Conclusión:** el costo global histórico está acreditado, pero todavía no puede repartirse entre preparación, ejecución contractual, propiedades y esperas. Hay mecanismos concretos que merece medir; ninguno permite prometer aún un ahorro. El aislamiento actual tampoco acredita ejecución paralela segura.

## 2. Qué está medido

### Corridas completas históricas

Recalculé la duración entre `started_at` y `finished_at` de los siete intentos terminados de `.cdad/evidence/`:

- `t4-full-suite`, intentos `20261030T223309…` y `20261030T233338…`: **3566 y 3376 s**.
- `010-004-closure`, intento `20261031T035714…`: **3671 s**.
- `010-001-closure`, intento `20261031T085400…`: **4549 s**.
- `010-002-closure`, intento `20261031T154550…`: **3973 s**.
- `010-002-closure-2`, intento `20261031T171528…`: **4204 s**.
- `010-003-closure`, intento `20261031T201928…`: **3882 s**.

Procedencia: `attempt.json`, campos de tiempo, selección y resultado; contraste con el resumen de su `stdout.log`.

**Límites importantes:**

- Son tiempos del intento, con resolución de segundos; los tiempos impresos por pytest son distintos.
- Cambian revisión y selección: entre **1869 y 1931 nodeids**.
- Dos intentos terminaron con fallos; todos registran árbol sucio.
- Otros dos registros permanecen `running`: no los conté como corridas terminadas.

Por tanto, **3376–4549 s es un rango histórico observado, no una línea base comparable sobre una revisión fija ni siete verdes atribuibles**.

### Gate del epic 016

El intento del gate acreditado registra **4241 s**; pytest informa:

```text
1989 passed, 5 skipped in 4237.09s (1:10:37)
```

El gate acredita revisión limpia, un intento terminado y canario sin cambios. La selección contiene **1994 nodeids**: 1989 pases y cinco omisiones, no 1989 tests totales.

Fuentes: `docs/epics/epic-016-traceability-and-suite-review/integration.md:7-20,45-49`; `.cdad/local/gate-20261104T051729363892Z-3050014-fbd7fdcc/gate.json:2-15,62-92` y el intento referenciado.

El documento de CI conserva un rango histórico más amplio, **46–103 min**, que no queda refutado por esta selección de registros (`docs/ci-gate.md:67-74`).

### Muestra focal previa

La muestra deliberada de cinco archivos produjo **205 passed en 252,25 s**, con esta atribución XML:

- `test_007_001_unambiguous_entry.py`: **60,407 s**.
- `test_007_006_withdraw_and_republish.py`: **89,924 s**.
- `test_007_004_termination_not_success.py`: **89,385 s**.
- `test_005_013_t1_unit_projection.py`: **12,007 s**.
- `test_010_003_documentary_pilot.py`: **0,047 s**.

Suma: **251,770 s**. Diferencia respecto del resumen pytest: **0,480 s**; respecto del controlador, otros **0,842 s**. Son diferencias entre capas de medición, no costos ya explicados.

Las fases `call` sumaron **250,96 s**. Esto sitúa casi todo el costo **de esa muestra** dentro de las funciones de test, pero allí también se ejecutan constructores, CLI y preparación manual. No demuestra que preparar sea barato.

La muestra no fue aleatoria y sus temporales no se conservaron como artefactos durables; reutilizo el registro documental, sin reproducirla ni extrapolarla (`docs/specs/013-test-criterion-suite-review/discovery.md:172-202`).

## 3. Dónde puede estar el costo

### Preparación repetida dentro de `call`

Los constructores `_RecoveryProject` y `_Project` construyen proyectos y ejecutan `prepare` mediante procesos reales. Ese trabajo aparece mezclado con la acción verificada, no necesariamente como `setup`.

**Hipótesis contrastable:** una parte relevante de los módulos CLI corresponde a construcción y preparación reiteradas. Falta medir cuántas veces y cuánto cuesta cada operación.

Fuentes: `tests/test_007_002_dispatch_recovery.py:409-426,506-518`; `tests/test_007_003_continuity_at_edges.py:490-537`.

### Staging y copias

Existen varias cachés independientes por proceso:

- `product_root()` reutiliza el checkout si encuentra el manifiesto; en caso contrario copia y genera staging.
- Otros helpers mantienen sus propias copias y generaciones.
- También se cachean instalaciones y entornos.

Fuentes: `tests/product_staging.py:57-92`; `tests/test_006_002_u1_delegation_section.py:169-205`; `tests/test_006_004_u3_principle_single_source.py:632-661`; `tests/test_010_002_documentary_role_integration.py:1161-1191`.

**Observación adicional:** algunas copias excluyen `.git`, `build` y cachés, pero **no `.cdad`**. En esta inspección:

```text
.cdad/evidence: 4949 archivos regulares, 149440916 bytes
.cdad/local:    4126 archivos regulares, 166440933 bytes
```

Es volumen contado, **no tiempo medido de copia ni ahorro posible**. Otros helpers sí excluyen `.cdad`; no corresponde atribuir el problema a todos.

**Hipótesis contrastable:** copiar evidencia histórica puede introducir costo y variación ajenos a las garantías verificadas.

Además, hoy existe `build/staging/manifest.json`; el helper comprueba su presencia, no su frescura en esa función. La futura comparación deberá declarar ese estado inicial.

### Esperas contractuales

La muestra contiene casos lentos de timeout. El código introduce procesos que duermen y configura límites de espera para comprobar terminaciones.

**Hipótesis contrastable:** una parte del tiempo es espera deliberada, no preparación eliminable. Debe distinguirse antes de optimizar.

Fuentes: `tests/test_007_004_termination_not_success.py:211-255,346-370`.

### Propiedades

Hay presupuestos internos de 100 publicaciones, 100 discordancias estáticas y 100 casos contextuales, además de publicaciones compartidas entre propiedades.

**No está medido que dominen la suite.** Tener pocos nodeids tampoco significa ejecutar poco trabajo (`tests/test_010_002_documentary_role_properties.py:108-114,271-279`).

## 4. Preparación y paralelismo: evaluación de seguridad

La base existente es favorable:

- HOME/XDG/TMP propios por test.
- Raíz estable de sesión para fixtures y cachés.
- Restauración de entorno y eliminación de temporales.
- Copias de agentes, no enlaces, para sembrar el HOME aislado.

Fuente: `tests/conftest.py:28-45,52-126`.

Pero quedan límites relevantes:

1. **El aislamiento modifica estado global del proceso.** No demuestra seguridad para ejecutar tests concurrentemente mediante hilos.
2. **Las cachés duran más que un test.** Hay que distinguir bytes reutilizables de proyectos, instalaciones y entornos mutables.
3. **El trabajo puede multiplicarse por proceso.** No hay evidencia de cuánto costaría reconstruir esas cachés con varios workers.
4. **Algunos recorridos deben regenerar realmente.** Por ejemplo, el test de determinismo ejecuta staging repetidamente; sustituirlo por un resultado cacheado evitaría la transición comprometida (`tests/test_006_005_u4_single_entry.py:884-924`).
5. **Copiar con `symlinks=True` no certifica confinamiento.** Deben revisarse destinos, escrituras y procesos supervivientes.
6. **El canario no es un monitor continuo.** No observa lecturas ni escrituras transitorias revertidas (`tests/test_008_001_home_xdg_isolation.py:30-35`).

Actualmente `pytest-xdist` no está disponible. **No recomiendo habilitar paralelismo todavía:** primero debe justificarse por costo residual y acreditarse sobre los recursos realmente compartidos.

La alternativa general es separar preparación reutilizable de estado mutable; las excepciones son los tests cuya promesa exige observar precisamente esa preparación. Ese criterio evita optimizaciones por prefijo de archivo o una migración masiva a ejecución en proceso.

## 5. Mínimo de medición propuesto — pendiente de autorización

### A. Calibración focal de la instrumentación

Antes de gastar una corrida completa, comprobar sobre una selección explícita que se conservan:

- nodeid, resultado y fases `setup/call/teardown`;
- XML y duraciones;
- tiempo exterior, comando efectivo y entorno;
- contabilización de preparación ejecutada dentro de `call`.

La muestra previa aporta una referencia de **4,2 min**, **no una predicción** de la nueva calibración.

**Costura pendiente:** `close` fija su argv de pytest y elimina `PYTEST_ADDOPTS`; tampoco expone opciones de duraciones/XML. No basta exportarlas y asumir que se aplicaron (`scripts/cdad-suite.py:859-880,954-979`). Resolver cómo conservar esa instrumentación requiere la siguiente especificación, no este discovery.

### B. Una línea base completa instrumentada

Sobre una revisión y selección fijadas, con autorización específica. Registrar además versiones, carga y recursos, estado del staging, configuración y omisiones.

La atribución debe separar:

- tiempo por test y fase;
- agregación por archivo;
- preparación interna y procesos relevantes;
- costo exterior: colección, arranque, finalización y evidencia.

**Criterio de conciliación propuesto:** las partes, **incluido el residual explícito**, deben explicar el tiempo total. No presentar la suma XML como si fuera automáticamente el tiempo de pared.

**Presupuesto orientativo, no garantía:** reservar inicialmente **56–76 min** según los siete intentos; el registro general de CI advierte que puede superar ese rango.

### C. Contraste focal y corrida final

Tras elegir una optimización basada en la línea base:

- medir antes/después focal con idéntica selección y condiciones declaradas;
- realizar la corrida completa final exigida por el epic, también instrumentada.

El mínimo planteado implica **dos corridas completas** —base y final— más focales: **112–152 min estimados por suma del rango histórico**, sin contar desarrollo ni comprobaciones adicionales justificadas. No propongo repeticiones completas rutinarias ni doy ese intervalo como límite máximo.

## 6. VERIFY y decisiones del dueño

Estos pendientes no bloquean entregar el discovery, que debe documentarlos; **sí bloquean acreditar los resultados posteriores afectados**:

- **Atribución completa:** falta la corrida instrumentada y su conciliación.
- **Ahorro de preparación:** falta medición por operación y contraste conservando garantías.
- **Seguridad paralela:** falta revisión de recursos compartidos y evidencia concurrente.
- **Comparabilidad:** faltan revisión candidata, selección, estado de staging y condiciones acordadas.

Preguntas para Pablo:

1. **¿Autorizas preparar y ejecutar una línea base completa instrumentada**, tras calibración focal, con ese presupuesto orientativo?
2. **¿Qué reducción de espera sería útil para dar por cumplido el objetivo?** Conviene acordarla con la línea base, no inventar ahora un porcentaje.
3. **¿Confirmamos optimización serial de preparación primero**, dejando paralelismo condicionado al costo restante y su seguridad?
4. **¿Aceptamos conciliar el total incluyendo sobrecosto exterior explícito**, sin forzar igualdad ficticia entre XML y tiempo de pared?

No reabro poda: el piloto B1 terminó en **Mantener**, sin ahorro demostrado (`docs/specs/013-003-redundancy-pilot/closure.md:9-16`). Tampoco propongo reducir presupuestos de propiedades sin demostrar primero su peso.

## 7. Evidencia de ejecución y límites

Comandos de control ejecutados:

```sh
python3 scripts/cdad_packet.py validate-request --request .cdad/packets/017-001-suite-performance-architect-discovery-001/REQUEST.json
python3 scripts/cdad_packet.py validate-packet --request .cdad/packets/017-001-suite-performance-architect-discovery-001/REQUEST.json --packet .cdad/packets/017-001-suite-performance-architect-discovery-001/PACKET.md
python3 scripts/cdad_packet.py render --request .cdad/packets/017-001-suite-performance-architect-discovery-001/REQUEST.json --route C
git rev-parse HEAD
git status --short
git diff --name-only -- sources skills tests scripts agents build install.sh
```

Validadores: **rc=0**. Comparación adicional en memoria: render completo idéntico, hash del contrato coincidente y contexto v2. Los comandos Python exactos de agregación histórica, conteo y comprobación constan en las llamadas de esta sesión; no ejecutan tests.

**Archivos modificados por mí: ninguno. Commit creado: ninguno.** El estado final conserva los mismos cambios documentales preexistentes y el diff de las superficies de producto indicadas está vacío.

**Suite completa no realizada**, por prohibición expresa del encargo. Este informe acredita inspección y cálculos sobre registros, no rendimiento actual, ahorro ni seguridad paralela. Su aceptación corresponde al dueño, mediante contraste de afirmaciones, fuentes y límites.
