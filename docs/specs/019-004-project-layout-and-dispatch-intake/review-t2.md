# Revisión T2 — 019-004

**Resultado: hay dos hallazgos bloqueantes.** La revisión se limita al alcance T2 del paquete; no constituye aprobación de la feature.

## 1. La prevalidación no comprueba el destino concreto de materialización

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

`skills/cdad-cycle/scripts/cdad_packet.py:2622–2646` comprueba únicamente el directorio metodológico y sus hijos `specs` y `epics`. En `skills/cdad-cycle/scripts/cdad_result.py:1102–1135`, la prevalidación de cada copia comprueba la tabla cerrada de tipos y que el destino esté bajo la ruta permitida, pero no clasifica el destino concreto ni verifica si es privado.

Una política puede clasificar `process/cdad/specs` como documentación y, a la vez, declarar una ruta descendiente como tests, implementación o privada. En ese caso, la comprobación del directorio padre pasa y la materialización puede escribir en un destino incompatible. Esto contradice §4.4 y PC-06: la clasificación del padre no sustituye la del destino de la operación.

**Remedio y cierre verificable:** antes de cualquier escritura, clasificar cada destino efectivo con la política aplicable y verificar también la protección privada. Demostrar que un destino descendiente incompatible se rechaza con diagnóstico accionable y sin cambios, mientras otro compatible sigue funcionando.

## 2. Los consumidores operativos seleccionan `docs/` ante un layout ambiguo

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

`skills/cdad-cycle/scripts/cdad_layout.py:73–83` implementa `methodology_base()` devolviendo `docs/` siempre que no haya locator, incluidos proyectos ambiguos o no inicializados. Los consumidores operativos usan esa función, aunque §4.2 y PC-04 exigen diagnosticar la ambigüedad y no seleccionar implícitamente una ubicación cuando solo existen señales insuficientes, como `docs/specs/` o registros operativos sin layout admitido.

El comando de consulta puede resolver la ambigüedad correctamente, pero eso no protege a los consumidores que llaman directamente a `methodology_base()`: pueden interpretar rutas metodológicas bajo `docs/` sin que exista un marcador legacy admitido.

**Remedio y cierre verificable:** hacer que los consumidores operativos compartan la resolución y sus errores de ambigüedad, reservando la selección legacy para los marcadores establecidos. Verificar consultas y operaciones representativas contra fixtures ambiguos y confirmar que fallan sin escrituras; conservar controles de proyectos legacy válidos.

## Evidencia y límites

- Validación del paquete Route C: `cdad_packet.py validate-packet` terminó sin error para el request, contexto y `PACKET.md` identificados.
- Tests ejecutados: `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_019_004_lifecycle_layout.py` → **19 passed in 23.76s**. Estos tests no cierran los dos casos señalados arriba.
- Commits examinados: `348a1768`, `0ac76106`, `24d6ffe0`, `b0a759ed` y `77fa9908`.
- No modifiqué archivos ni creé commits. Al revisar, `git status --short` mostraba `M docs/.cdad-state.json`, cambio preexistente en el árbol de trabajo.
- La suite completa no se ejecutó; la evidencia independiente de esta revisión es la selección focal indicada.
- La decisión registrada de rechazar un locator que resuelva a la raíz cuenta con un test focal que pasó. No identifiqué una contradicción adicional en esa decisión dentro del alcance revisado.

## Abstentions

- No acredito todos los caminos de comparación de registros con layouts personalizados: no fueron demostrados por la selección ejecutada ni revisados exhaustivamente.
- No acredito la integración documental ni la instalación completa de la feature; pertenecen a trabajo y evidencia posteriores al alcance T2 de este encargo.
- No completo un dictamen de reconciliación exhaustiva entre la tabla de decisiones vigentes y todos los ADR; examiné la tabla, pero no contrasté cada ADR individualmente.