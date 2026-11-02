# review.md — 012-installer-ignore-pycache

**Veredicto:** 1 BLOCKING, 2 OPTIONAL, 2 abstenciones. El comportamiento cumple PC-1..PC-5 en sondas; lo que bloquea es la evidencia: el test de PC-4 quedo vacuo tras GREEN. El reviewer no aprueba.

Objeto: 935328d8 (install.sh +29/-1) y test 887c057c, contra spec sha b475b7dd...a2ca4.

## F1 — El test de PC-4 no ejerce la poda (BLOCKING, bucket h)
tests/test_012_installer_ignore_pycache.py::test_pc4_reinstall_prunes_preexisting_pyc_records y install.sh:1496-1506.
El test genera el "manifiesto anterior" con el mismo instalador ya corregido, que no registra .pyc: tras GREEN no hay nada que podar y cache_keys(manifest_after) == [] se cumple sin ejecutar la rama.
Evidencia: en copia aislada se elimino la rama de poda completa y pytest -k pc4 dio 1 passed.
Consecuencia: si la poda se rompe, nada falla; quien actualice desde un manifiesto con .pyc conservaria los registros y --check seguiria en FAIL.
Cierre: el test debe sembrar en un manifiesto real registros .pyc en artifacts y pending_removal, reinstalar y comprobar la poda; debe fallar con la mutacion anterior y pasar sin ella.

## F2 — Coincidencia contra la ruta absoluta de origen (OPTIONAL, bucket m)
install.sh:1285, 1813, 205. El filtro evalua la ruta completa, no la relativa a la skill: si el repo vive bajo un directorio __pycache__, se excluye todo (sonda: --basic rc=0 con 0 archivos en skills y --check rc=0, un verde falso). Sin camino realista hoy: deuda. Remedio: evaluar ${src_file#"$src"/} y find relativo al arbol.

## F3 — El bloque de poda deja un __pycache__/ vacio (OPTIONAL/Nit, bucket m)
install.sh:1496-1506. Medido: 0 archivos .pyc/.pyo y 1 directorio. No afecta a --check (rc=0).

## Verificacion por PC
| PC/INV | Resultado | Evidencia |
|---|---|---|
| PC-1 | OK | Test focal verde; exclusion en sync_skill_to cubre __pycache__, .pyc y .pyo |
| PC-2 | OK | Test verde: claves y digests iguales con y sin cache |
| PC-3 | OK | Test verde; sonda adicional con cache en la raiz instalada: --check rc=0 |
| PC-4 | Comportamiento OK, test vacuo (F1) | Manifiesto sembrado con 4 registros: stale con archivo, .pyo, pending_removal y archivo ausente. Reinstalacion rc=0, 0 registros cache, 0 archivos, --check rc=0. --dry-run no toco el manifiesto |
| PC-5 | OK | 37 tests de regresion verdes; ramas de contenido sin cambios |
| INV-1 | OK | Exclusion por forma de ruta, sin lista de nombres |
| INV-2 | OK | Contenido alterado con cache presente: --check rc=1 |

Criterio 2: 4 archivos de regresion verdes. Suite completa no corrida (no es gate).

## FYI
- --check antes de reinstalar con manifiesto antiguo sigue rc=1 por .pyc registrados: deuda declarada en la spec, se resuelve al reinstalar.
- --uninstall deja un .pyc generado despues de instalar porque ya no es propio: coincide con la regla de no tocar archivos ajenos.

## Abstenciones
- No se comparo la tabla de decisiones vigentes contra docs/adr/.
- Instalacion real en HOME y perfiles distintos de --basic: no probados.

## Comandos
validate-request rc=0; render + cmp PACKET.md = 0; sha256sum de spec coincide; pytest de los 5 archivos -> 41 passed en 503.83s. Sondas en copia temporal /tmp/rev012.lAEL con CDAD_INSTALL_ROOT aislado: instalacion, --check, --dry-run, --uninstall, mutacion de install.sh + pytest -k pc4 (1 passed), origen bajo __pycache__. Sin cambios en el repo.

## Resolución del bloqueante (orquestador, 2026-11-01)

**F1 CERRADO.** El test-writer reforzó `test_pc4_reinstall_prunes_preexisting_pyc_records` (commit `4241e337`): instala sobre un árbol con caché, obtiene un manifiesto real, inyecta de forma declarada 4 registros stale (`.pyc` por segmento `__pycache__`, `.pyo` por extensión) en `artifacts` y `pending_removal`, reinstala y exige cero claves con forma de caché en ambas secciones con los registros de contenido byte-idénticos.

Evidencia de no vacuidad: mutación literal ejecutada por el orquestador en una copia `git archive` en un directorio temporal aislado, eliminando el bloque de poda de `install.sh`. Resultado: `pytest -k pc4` → **1 failed** (`AssertionError`, los 4 registros stale siguen registrados). Con el bloque presente: **4 passed**. Es exactamente la condición de cierre que pidió F1.

**F2 y F3 quedan como deuda declarada** (OPTIONAL y Nit): coincidencia contra ruta absoluta de origen y `__pycache__/` vacío tras la poda. Sin consecuencia de usuario observada; destino: hardening del instalador.
