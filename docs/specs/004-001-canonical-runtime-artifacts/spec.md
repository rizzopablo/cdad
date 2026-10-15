# Spec — 004-001-canonical-runtime-artifacts

**Feature ID**: `004-001-canonical-runtime-artifacts` · **Epic**: `epic-004-single-source-planning` · **ADR-011 gobierna el diseño de permisos** (`docs/adr/ADR-011-autonomia-supervisada-limites-proporcionales.md:151-153`).

## 1. Descripción funcional

La política de roles de CDAD se define por capacidades y efectos (ADR-011:88-101): cada rol recibe las capacidades necesarias para su encargo y pocas barreras duras, cada una con efecto protegido, mecanismo y límite declarado. Esa política vive en **fuentes canónicas editables** (Markdown con delimitadores, decisión D1) de las que un generador determinista (Python stdlib) produce los 22 agentes en **staging** con manifest (`cdad_packet.py:418-421` es el patrón de hashes ya probado); el instalador despliega en destinos runtime reales con **propiedad de archivos** (manifest de instalación, D4).

La feature aterriza en **dos entregas**:

- **Aterrizaje A (intermedio utilizable)**: aterrizaje 0 de capacidad de medición (par `rtk wc *` completo en fuente e instalación — primer aterrizaje del rediseño, no parche aislado) + baseline PD-13 medida con esa capacidad **antes de la primera generación** + fuentes canónicas + generador determinista + adaptadores simplificados (OpenCode primero) con la **instalación sin cambios** (`install.sh` opera hoy igual que ayer: sin manifest, sin migración de fixtures, sin reemplazo de validadores).
- **Aterrizaje B**: instalación con propiedad (manifest, D4 completo), coherencia Claude Code contra el mismo contrato semántico, migración de fixtures a destinos runtime reales (D6) y reemplazo de assertions de mecanismo por comprobaciones de garantía en el mismo cambio coherente (D7). La prueba de capacidad obligatoria se ejecuta **desde el producto instalado**, sin el checkout como ruta de ejecución. Si T5 crece más allá de su mini-ciclo, pasa a candidata a feature propia en vez de estirar el ciclo.

Dentro del mismo cambio: el vocabulario de `epic_stage` deja de vivir en dos fuentes divergentes (R13, PD-4), el techo de bytes del bloque estático del paquete pasa de constante dura a parámetro de política con diagnóstico (PD-19), y el instalador deja de poder leer `sources/` (PD-18). La supervisión tiene dueño desde la primera tarea (PD-17). La feature termina demostrando **capacidad operativa real desde el producto instalado** (PD-11/12).

## 2. Contrato

**Firma del generador**: `scripts/cdad-generate.py --runtime <opencode|claude-code> --stack <auto|odoo> --profile <nombre> --out <staging-dir>` → escribe `staging/agents/<runtime>/cdad-*.md` + `staging/manifest.json` (por artefacto: sha256, fuentes que lo produjeron, comando de regeneración, stack/perfil usados).

**Firma del instalador**: la actual de `install.sh`, consumiendo **exclusivamente staging** (nunca `sources/`); generar on-the-fly queda deshabilitado una vez aterrizado el generador.

**Postcondiciones:**

1. **PD-1 (simplificación previa)**: la política de bash por rol resultante es derivable de la fuente canónica y cada regla se justifica por efecto declarado; no existen reglas retenidas sin justificación. Verificable: el bloque generado para cada rol × stack contiene solo reglas con comentario de efecto en su fuente.
2. **PD-2 (determinismo)**: misma entrada (fuentes + runtime + stack + perfil) produce outputs byte-idénticos en dos corridas (hash comparado).
3. **PD-3 (fallo explícito)**: fuente incompleta, duplicada o combinación no soportada (runtime×stack×perfil) → el generador termina con error y **no publica salida parcial** (staging ausente o limpio).
4. **PD-4 (fuente única)**: cada regla compartida (directiva de intake, contrato §2, regla de property tests, política de commits, corrección del intake R3 del arquitecto CC, **y el vocabulario de `epic_stage` — R13: definición canónica en `skills/cdad-epic/references/state-detection.md:14`; `VALID_EPIC_STAGES` pasa a subconjunto declarado con trazabilidad**) existe en exactamente una fuente editable; el manifest referencia la fuente de cada archivo. Verificable: búsqueda repo-wide de cada regla encuentra exactamente una definición editable.
5. **PD-5 (propagación)**: cambiar una regla canónica y regenerar actualiza todos los consumidores declarados; `install.sh --check` detecta la copia instalada que difiere de staging.
6. **PD-6 (propiedad, primera instalación)**: sin manifest previo, la instalación registra propiedad y **no borra nada**.
7. **PD-7 (conflicto)**: archivo instalado con hash ≠ registrado → dry-run e instalación lo reportan como conflicto; ni sobrescribe ni borra sin resolución explícita.
8. **PD-8 (uninstall)**: borra solo entradas del manifest; archivos ajenos (incl. `cdad-*.md` creado por el usuario que no vino del repo) sobreviven.
9. **PD-9 (destinos y layout público)**: instalación por defecto solo en destinos runtime reales; el layout público (`install.sh:34-35,605,627-628`) no se instala por defecto. La decisión sobre un flag opt-in se toma **después de migrar los fixtures** (T6): si no aparece un consumidor real documentado, **no hay flag**.
10. **PD-10 (reemplazo coherente de assertions, D7)**: al cerrar la feature, F001/F009 y las listas FORBIDDEN de P1 se validan contra la fuente/salida generada con comprobaciones semánticas equivalentes (trazabilidad registrada en los asserts nuevos); ningún control se elimina sin su reemplazo funcionando.
11. **PD-11 (prueba de capacidad desde producto instalado)**: sin el repo en el path, desde la instalación aislada se completa un recorrido positivo por rol: medir (conteo de líneas con la capacidad aterrizada en el aterrizaje 0), agregar deterministamente (suma recomputada mecánicamente por el propio comando, sin repetir la agregación fallida de C0), ejecutar el runner acordado y git de inspección no-mutante. Se registra salida exacta por comando, separada de la evidencia estática.
12. **PD-12 (pruebas positivas y negativas de fronteras)**: cada barrera retenida se prueba en ambas direcciones: la operación legítima representativa del rol **tiene éxito**, y el efecto fuera de rol queda bloqueado por el mecanismo declarado. Un rechazo de operación legítima durante el recorrido cuenta como defecto y se registra con diagnóstico.
13. **PD-13 (baseline, T1, revisada)**: artefacto de medición previo a la generación, ejecutado por el architect **con la capacidad de medición aterrizada en el propio feature** (aterrizaje 0: par `rtk wc *` completo en fuente e instalación — no evidencia prestada). Contiene: conteo línea/byte por rol×runtime×camino (clásico vs paquete), método (`rtk wc -l`/`-c`), versión, configuración y sesión ejecutora registrados; totales mecánicos del propio comando (no agregación manual); los bytes son de archivos completos UTF-8, no tokens ni contexto observado; incluye el **valor efectivo del techo de bytes del bloque estático** (PD-19), porque es parte del presupuesto medido. Un valor no medible con la capacidad aterrizada se declara VERIFY y se diagnostica — nunca se sustituye por estimación.
14. **PD-14 (coherencia entre runtimes)**: tests semánticos comprueban el significado del rol en cada runtime (p. ej. la copia CC no menciona modelos que `cdad_model_claude` no produce); la igualdad byte-a-byte del §2 deja de ser requisito y su sustituto está en verde.
15. **PD-15 (honestidad)**: ningún texto de agente/paquete generado describe sesión/paquete/worktree como sandbox ni promete aislamiento no implementado; el espacio de trabajo temporal está declarado (ADR-011:75-79).
16. **PD-16 (fallback legacy)**: el camino legacy (sin paquete) sigue cargando los skills correctos desde la instalación (incluye la corrección R3 del arquitecto genérico CC, `agents/claude-code/cdad-architect.md:17` vs `agents/cdad-architect.md:65`).
17. **PD-17 (supervisión con dueño)**: al cierre de cada tarea de 004-001 (T1–T7), el orquestador registra en el resultado de la tarea: (a) resultado vs contrato de la tarea; (b) ámbito de cambios (`git diff --stat` como orientación + revisión de contenido, ADR-011:111-116); (c) desviaciones halladas con su disposición proporcional según la matriz de tratamiento (ADR-011:118-124). Un cierre sin registro completo = gate incompleto de la tarea.
18. **PD-18 (instalador y fuentes)**: el instalador **no lee `sources/`** (solo staging). Verificable: (a) revisión de rutas del camino de instalación sin referencias a `sources/`; (b) prueba conductual: la instalación se completa con staging presente y `sources/` inaccesible; (c) un cambio en `sources/` no altera el comportamiento del instalador.
19. **PD-19 (techo de bytes parametrizado)**: el límite de 12.000 bytes del bloque estático del paquete (`cdad_packet.py:411-412`) pasa de constante dura a parámetro de política declarado; superarlo produce error de entorno con diagnóstico breve al orquestador, no una salida mezclada; el valor efectivo vigente queda registrado en la baseline PD-13. La selección de modelos no se altera; `cdad-models.sh` sigue siendo la única fuente del mapa.

## 3. Invariantes verificables

1. Test-writer: no lee implementación por los caminos declarados; solo edita tests (dedicados y co-ubicados) — mecanismo actual conservado con límites declarados (ADR-011:93; finding de fricción:119-122).
2. Implementer/refactorer: no edita tests; conserva los tests aprobados (ADR-011:94).
3. Read-only (architect/reviewer/scribe): no modifican el producto; temporales en espacio declarado permitidos (ADR-011:98-101).
4. Contrato de materialización ADR-003 sin cambios; la selección de modelos no se altera en esta feature.
5. Invariantes anti-trampa y especialización Odoo preservadas semánticamente (no las listas de nombres por inercia — D7).
6. Un solo epic activo en el state; sin motor multi-epic; no se escribe ningún valor de `epic_stage` fuera del vocabulario canónico de `state-detection.md:14` (R13).
7. Instrucciones nunca prometen garantías de sandbox inexistentes (ADR-011:75-79).
8. La separación generación/instalación es real, no convencional: el instalador nunca lee `sources/` (PD-18); el stack/perfil es entrada explícita registrada en el manifest, no efecto oculto de la máquina.

## 4. Criterios de aceptación

1. Matriz smoke `runtime × rol (11 agentes por runtime) × perfil soportado` desde instalación aislada: todas las celdas instaladas y verificadas con datos sintéticos, sin llamadas a proveedor.
2. Cero archivos de agente editados a mano tras el aterrizaje del generador (los 22 pasan a ser salidas declaradas); al cierre del aterrizaje A, `install.sh` opera sin cambios de comportamiento.
3. Los tres validadores existentes en PASS o sus assertions migradas con trazabilidad en el mismo cambio (PD-10).
4. Recorrido de capacidad (PD-11) completo, con cero rechazos injustificados; cada rechazo real registrado con diagnóstico breve.
5. Baseline PD-13 registrada antes de la primera generación, **con la capacidad de medición (`rtk wc *`) aterrizada dentro de la feature** (aterrizaje 0), totales mecánicos del propio comando y el valor efectivo del techo de bytes registrado; conteos reportados como diagnóstico (no gate de líneas).
6. Fricción medida en el primer recorrido real y entregada como entrada a 003-003, sin exigir ahorro porcentual.
7. Cada tarea T1–T7 cierra con registro de supervisión completo (PD-17); el recorrido de instalación demuestra que no se lee `sources/` (PD-18); el exceso del techo parametrizado produce error claro, no mezcla (PD-19).

---

Status: Approved by Pablo (usuario) on 2026-09-24 — aprobación registrada en esta sesión tras el dictamen conforme focal de Claude (corrección requerida y observaciones incorporadas por el architect; ver `docs/epics/epic-004-single-source-planning/correction-004-001-architect-2026-09-24.md`).
