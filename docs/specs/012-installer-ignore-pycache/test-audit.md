# AUDIT — 012 installer-ignore-pycache (test-writer)

## Mapeo test<->PC (37 tests inventariados)
- PC-1 (manifiesto sin __pycache__/.pyc/.pyo): HUECO. Todos los fixtures excluyen __pycache__ al copiar el arbol (test_install_ownership.py:229, test_install_review5_regressions.py:302, test_009_001:43, test_005_004_t2:342,678): el instalador nunca se ejercita con cache presente.
- PC-2 (paridad con/sin cache): HUECO. Ningun test compara ambas instalaciones.
- PC-3 (--check rc 0 con cache regenerado en el origen): HUECO. test_review5_b1 no introduce cache.
- PC-4 (poda de .pyc preexistentes al reinstalar): HUECO. test_review5_b3 retira artefactos del staging, nunca entradas .pyc.
- PC-5 (sin cambio para contenido): CUBIERTO por los 37 tests de los 4 archivos (ownership 11, review5 6, 009_001 12, 005_004_t2 8). No hay asserts de conteo exacto del manifiesto ni exigencia de .pyc.

## RED propuesto: 4 tests, uno por promesa
1. install con __pycache__ y .pyc -> cero entradas con segmento __pycache__ ni extension .pyc/.pyo (PC-1, protege INV-1 con .pyo y anidamiento).
2. Paridad con/sin cache: mismo conjunto de artefactos (PC-2).
3. --check rc 0 con cache regenerado en el origen (PC-3).
4. Reinstalacion poda .pyc preexistentes y preserva contenido byte a byte (PC-4).

## Intactos
Los 37 tests existentes. test_006_003_u3 y test_005_009_t1 son higiene de fixture, no oraculo.

## Riesgos
- Mantener el patron ignore=__pycache__ en fixtures futuros.
- El eje "cache en la raiz instalada" no esta en PC-3: fuera de RED salvo decision del dueno.

## Comandos
validate-request rc 0; render --route C identico; validate-packet rc 0; sha256sum spec coincide (b475b7dd...); pytest --collect-only 37 tests; grep sin oraculos de .pyc; grep sin asserts de conteo exacto.
