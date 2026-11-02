# 012 — El instalador no registra `__pycache__` como artefacto propio

**Estado:** Approved by Pablo on 2026-11-01.

## 1. Descripcion

Al instalar las skills, el instalador enumera todos los archivos del arbol de origen y registra cada uno como artefacto propio en el manifiesto de propiedad. Python regenera `__pycache__/*.pyc` cada vez que se ejecuta un script de una skill instalada, y el repo tambien los genera al correr tests. Resultado: el manifiesto declara artefactos que no son contenido del producto, y `--check` reporta drift o missing sin que nada haya cambiado de verdad.

Reportado por un agente tras un install: 3 `.pyc` registrados como propios, luego "missing" al limpiarlos, poda de 375 a 372 artefactos al reinstalar.

## 2. Contrato

- **PC-1.** El registro de propiedad de una skill nunca incluye rutas con un segmento `__pycache__` ni archivos con extension `.pyc` o `.pyo`.
- **PC-2.** Un `install` sobre un arbol de origen que contiene `__pycache__` produce el mismo conjunto de artefactos registrados que el mismo arbol sin el: la presencia de cache no altera el manifiesto.
- **PC-3.** `--check` sobre una instalacion valida cuyo arbol de origen tiene `__pycache__` regenerado no reporta drift ni missing por esa causa, y sale 0.
- **PC-4.** Los registros de `.pyc` preexistentes en un manifiesto anterior se podan en la siguiente instalacion, sin afectar los artefactos de contenido.
- **PC-5.** El comportamiento existente no cambia para archivos de contenido: mismos artefactos, mismos digests, misma politica de conflicto y preservacion.

## 3. Invariantes

- **INV-1.** La exclusion es por forma de ruta (`__pycache__` como segmento, `.pyc`/`.pyo` como extension), no por lista de nombres concreta.
- **INV-2.** No se relaja ninguna comprobacion de contenido: un archivo de contenido alterado sigue siendo drift.

## 4. Criterios de aceptacion

1. Cada PC vinculada a un test automatizado de comportamiento sobre el instalador en un arbol temporal.
2. Regresion: `tests/test_install_ownership.py`, `tests/test_install_review5_regressions.py`, `tests/test_009_001_installer_agent_overlay.py` y `tests/test_005_004_t2_installer_claims.py` verdes.
3. Evidencia con comando, revision y resumen final. La suite completa no es gate (directiva del dueno).

## Contexto tecnico

- `install.sh:1275` (`sync_skill_to`): `find "$src" -type f -print0` alimenta `stage_owned_file` sin exclusion.
- `install.sh:1797` (check legacy de arbol de skills): mismo `find` sin exclusion.
- El manifiesto de staging ya se valida en `install.sh:564-573`.

## Deuda declarada

- Suite completa no corrida.
- Limpieza retroactiva de manifiestos ya instalados fuera de un `install` normal: no se implementa; la poda ocurre al reinstalar (PC-4).

Status: Approved by Pablo on 2026-11-01.
