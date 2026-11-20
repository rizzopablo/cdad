# ADR-045 — Declaración versionada fija y almacenamiento operativo local por proyecto

- **Estado:** Aceptado.
- **Fecha:** 2026-11-19.
- **Decisor:** <owner>, aprobador de `020-001-versioned-layout-local-execution`.
- **Confianza:** Alta sobre la decisión; no acredita instalación ni publicación.
- **Origen:** `docs/specs/020-001-versioned-layout-local-execution/{spec.md,review.md}`.

**Contexto.** El localizador compartía `.cdad/` con registros operativos ignorados. Un clon debía reconocer la metodología sin transportar ejecuciones locales. La resolución por proyecto necesitaba extenderse al almacenamiento operativo sin introducir selección entre stores ni modificar evidencia histórica.

**Decisión.**

1. **Una declaración en una ubicación fija:** `cdad/project-layout.json`, independientemente del directorio de metodología. Esquema 2, con exactamente `schema_version`, `methodology_dir` y `operational_dir`. Los proyectos nuevos usan `cdad/` para metodología y `.cdad-execution/` para operación; los existentes conservan `docs/` o su ubicación registrada.
2. **Un único accessor compartido.** Cada consumidor deriva sus rutas del directorio operativo declarado. Las identidades persistidas son relativas al repositorio; el acceso físico las une con la raíz explícita del producto, conservando la semántica existente de cwd y argumentos.
3. **Migración exclusivamente manual**, documentada en `skills/cdad-cycle/references/layout-migration.md`: trasladar el localizador a su ubicación fija, actualizar su esquema, renombrar el store operativo y agregar manualmente una regla de ignore anclada en la raíz para el directorio realmente declarado. No se trasladan políticas, contratos ni Memory Banks.
4. **Rechazo antes de escrituras operativas** cuando falta migrar, con una indicación breve hacia esa referencia. Detectar la necesidad de migración no selecciona un store antiguo. No hay conversor automático, aliases, selección por contenido ni replay histórico.
5. **Continuidad del trabajo mediante un encargo nuevo.** Se conserva una copia del estado original; se limpian únicamente los vínculos vivos `execution` y `active_packet`, manteniendo progreso y aprobaciones, y se prepara con `--new-execution`. Seleccionar después una unidad suspendida no puede sobrescribir otra activa y conserva las demás suspensiones. Autoridad, política y aprobaciones vigentes siguen siendo obligatorias.
6. **Los efectos pendientes se esclarecen antes de autorizar efectos superpuestos.** El operador coordina agentes activos y conserva resultados y journals. Una situación desconocida requiere investigación, no repetición implícita. Migrar no exige terminar la feature o el epic.
7. **La evidencia histórica conserva sus bytes:** paquetes, recibos, checkpoints y journals son evidencia, no encargos reejecutables. No se reescriben rutas, digests ni cadenas para hacerlos compatibles.

**Consecuencias.**

- *Positivas:* el clon conserva una declaración suficiente para reconocer el proyecto; los registros locales quedan separados; todos los consumidores comparten la misma resolución.
- *Costos:* las instalaciones existentes requieren una migración manual única y un handoff explícito para trabajo abierto. La responsabilidad del operador no se sustituye por sincronización automática.
- *Límites:* el chequeo de versiones detecta diferencias entre marcadores, no ediciones con igual versión ni todo cambio pasado cuando los marcadores ya coinciden. El orquestador consulta el aviso de migración y genera un nuevo encargo antes del siguiente despacho; no hay invalidación automática de paquetes.
- *Alcance:* esta decisión no acredita despliegue, instalación global, publicación ni replay de evidencia histórica.

**Alternativas consideradas.**

- **Conservar `.cdad/` y versionar solo su localizador:** rechazada; no satisface el cambio de ubicación solicitado.
- **Compatibilidad permanente entre dos stores con selección por contenido:** rechazada; reproduce la complejidad del intento descartado.
- **Reescribir rutas y digests históricos:** rechazada; altera la evidencia y encadena reconciliaciones de integridad.
- **Exigir cierre del trabajo antes de migrar:** rechazada; la actualización debe permitir continuar desarrollo abierto mediante un encargo nuevo.
