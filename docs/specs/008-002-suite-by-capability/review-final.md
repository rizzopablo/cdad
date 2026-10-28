## Hallazgos

### 1. BLOCKING — El resumen de pytest puede declarar cero resultados silenciosamente

**Verdict: BLOCKING · Bucket: h**
**Archivo:** `scripts/cdad-suite.py:621-625`, `:724-747`, `:836-843`, `:896-900`

`close` deriva `pytest_summary` exclusivamente de líneas de `pytest -v`. La salida cambia si el entorno define opciones de pytest. Verifiqué:

```text
PYTHON... PYTEST_ADDOPTS='-qq' python3 -m pytest -v -rs ... <un test>
.                                                                        [100%]
1 passed in 2.41s
```

Esa salida no coincide con `PYTEST_STATUS_LINE`: el intento terminaría con `rc=0`, pero el resumen registraría cero aprobados. También puede perder motivos de skips. El usuario recibe evidencia de cierre incorrecta sin diagnóstico, en contradicción con PC-6/AJ7.

**Cierre verificable:** obtener resultados y motivos mediante una fuente estructurada o controlar y validar la salida efectiva de pytest; comprobar que opciones de entorno no producen un resumen silenciosamente incorrecto.

### 2. IMPORTANT — Una colisión de nombre no falla como exige AJ7

**Verdict: BLOCKING · Bucket: h**
**Archivo:** `scripts/cdad-suite.py:793-812`

AJ7 establece que, si el nombre del intento ya existe, la reserva **falla**. `reserve_attempt` captura `FileExistsError` y genera otro nombre hasta 64 veces. No sobrescribe ni adopta el directorio ajeno, pero contradice la interfaz aprobada: una colisión no devuelve el error de reserva esperado.

**Cierre verificable:** ante una colisión forzada, devolver código 2 sin modificar ni adoptar el intento existente. Las invocaciones simultáneas con nombres distintos deben seguir reservando directorios independientes.

### 3. MINOR — Los controles nuevos no declaran la consecuencia para el usuario

**Verdict: OPTIONAL · Bucket: h**
**Archivo:** `tests/test_008_002_variant_controls.py:90-110`

Los controles C1–C3 y su baseline no incluyen la línea «sin este test, el usuario…» exigida para cada test nuevo por AJ6, cláusula 4. Esto es una omisión de declaración; **no afirmo que sean tests sin promesa**: C1–C3 comprueban desviaciones observables del modelo y del esquema I8.

## Comprobaciones y límites

- **Consolidación:** el diff conserva en el destino PD-6 las aserciones relevantes de R2 sobre modelo en texto plano y esquema cerrado. C3 inyecta una clave extra en el registro observado y exige un fallo del destino que nombre esa desviación. Los controles dirigidos pasaron.
- **Reserva y estado:** la creación usa `os.mkdir` exclusivo y la actualización de `attempt.json` usa archivo temporal y `os.replace`. Los tests ejercitan intentos secuenciales, simultáneos e interrupción; esta revisión no simuló un fallo del sistema de archivos.
- **Salida del hijo:** stdout y stderr se escriben directamente en archivos del intento, también durante la ejecución.
- **Canario:** el alcance se declara y apunta al HOME real incluso cuando el repositorio es sintético. Eso coincide con el canario heredado, pero puede registrar cambios ajenos al repositorio sintético; no lo interpreto como aislamiento del proceso.
- **Directorio de trabajo:** la CLI declara que se invoca desde la raíz del repositorio; no verifiqué funcionamiento desde otros directorios.
- Los tests de evidencia observan archivos, hashes, estados y resultados de procesos reales; no se limitan a aceptar una declaración del implementador. No identifiqué en los tests nuevos revisados uno que exista únicamente por cobertura y carezca de promesa conforme a la cláusula 1.

## Evidencia

- Contrato verificado: SHA-256 `c772585bbc859fe227f77dc9646bceaecbf8400fe7851183b84f8266da2599e3`.
- Commits revisados: `3bbfc8b`, `7c4e6a0`, `966bc1f`.
- Comando ejecutado:

  ```text
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_008_002_suite_evidence.py tests/test_008_002_variant_controls.py
  9 passed in 38.10s
  ```

- Para la reproducción del formato:

  ```text
  PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-qq' python3 -m pytest -v -rs -p no:cacheprovider tests/test_008_002_variant_controls.py::TestR2PlainTextVariantControls::test_baseline_pd6_destination_passes_without_deviation
  1 passed in 2.41s
  ```

- **Archivos modificados por esta revisión:** ninguno. Al iniciar y finalizar, `git status --short` mostraba `M docs/.cdad-state.json`, cambio preexistente.
- No ejecuté la suite completa: la política del paquete la reserva al closer.

## Abstenciones

- No contrasté exhaustivamente la tabla de decisiones vigentes contra todos los ADR del repositorio.
- No reproduje una colisión real del generador de nombres; el comportamiento está determinado por la rama `FileExistsError` inspeccionada.
- No verifiqué todos los consumidores adicionales del helper ni ejecuté las selecciones completas de PC-8.
