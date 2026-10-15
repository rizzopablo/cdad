# Cierre — 005-004-claude-code-roles

Fecha: 2026-10-13. Epic: `epic-005-real-operation` (fila 10). Ejecución: `exec-005-004-claude-code-roles-001`.
Contrato aprobado: `spec.md` (`5e11f2ef3199ca4f9072c04341abf15e6cac6b49cdf26a5dcab7abee51a33f5e`) y `plan.md`
(`953e4ba564c91a188592d7255e5384146a9bafda6326f3fc9bf6bf8d6857f8db`), re-aprobados con las **dos enmiendas**
del orquestador Claude (`review-claude-spec-2026-10-13.md`). Decisión arquitectónica: **ADR-026**.

## Resultado

La feature deja los **roles CDAD activos en Claude Code para este proyecto** por el **mecanismo nativo**
—`Agent` con `subagent_type: cdad-<rol>`, subagentes `cdad-*` instalados— y **un ciclo corto real despachado desde
una sesión nueva de Claude Code, con la versión instalada al empezar, recibido por el flujo CDAD** (I8
`runtime: claude-code` → rol nativo → `receive` → `reconcile`). **Sin infraestructura nueva:** se reusan paquete,
I8, `receive`, `materialize`, `reconcile` y la vista compacta. De paso, se corrigen tres enunciados del propio
producto que un consumidor de Claude Code leería como fuente: la herramienta de despacho declarada pasa a ser la
real (`Agent`), el mecanismo del instalador se describe como es (despliega los bytes staged sin transformarlos; la
ausencia de `model:` bajo `basic` la produce el generador) y el chequeo de versión gana una **pata Claude Code
aditiva** (participa solo si la instalación CC es detectable, no altera los cuatro veredictos/`rc`, marca faltante
= `unknown` con causa).

## Gates con números

- **T1..T4 (producto), RED→GREEN por tarea, un commit de cada rol:** T1 `34703b6`/`cc6e5a5` (focal 3 failed → 7
  passed); T2 `0964694`/`96786de` (6 failed/2 passed → 8 passed); T3 `4828c0c`/`b05c5c1` (8 failed → 8 passed);
  T4 `0cdec77`/`65a0de9` (3 failed/3 passed → 6 passed). **29 focales passed** en la corrida del reviewer; el
  implementer **no tocó `tests/`** en ningún GREEN y los focales no se relajaron (un solo commit RED por foco).
- **Gate de la feature = T5** (`t5-acceptance.md`): recorrido real de 11 pasos desde una sesión nueva de Claude
  Code; **I8 `runtime: claude-code`**; `Agent` con `subagent_type: cdad-reviewer` e identidad en la fila durable
  **sin fallback** a un agente genérico; **recibo durable `semantic_status: pending`** (`VALID`); **`reconcile:
  received`**; transición del state por el **escritor único**. **Paso a: APROBADO** por el orquestador Claude con
  la HITL delegada por el dueño. **Paso b: BLOQUEADO** hasta el despliegue del dueño (no es gate).
- **Review formal única** (`review.md`): **0 bloqueantes / 3 opcionales / 2 abstenciones**, reviewer de familia
  distinta a la del implementer; los 2 FAIL del validador del repo son **preexistentes con delta 0** probados en un
  árbol pre-feature.
- **Suite completa, una vez, por quien cierra** (`closure-suite.md`): worktree fijado a `c8ab21f`,
  **915 passed / 2 failed / 4 skipped** (17 min). Una **regresión real de T4** —la negación de INV-8 partida en dos
  líneas, que el oráculo de 005-009 lee línea por línea y que las regresiones declaradas de T4 no cubrían— corregida
  en **`5d6f667`** (una línea de documentación, sin tocar el test); el otro fallo fue **error del lanzador**
  (staging con el perfil equivocado), no del producto. **Verificación en `5d6f667`**: los 4 focales + INV-8 +
  `test_install_review5_regressions` → **55 passed**; **`make validate` 155 PASS / 1 FAIL** (F011 preexistente). El
  resto de la suite se toma por **equivalencia declarada** (`references/re-entry.md`, *Equivalence of a registered
  run*), porque entre `c8ab21f` y `5d6f667` solo cambia esa línea de documentación.
- **Frontera de HOME:** intacta, con tres coberturas declaradas por separado (107 archivos comparados idénticos con
  digest `9cfa2717…`, excluye `__pycache__`; marcador de versión y manifiesto de propiedad por mtime anterior al
  inicio; barrido por mtime que expone dos archivos de sincronización del harness —ajenos a CDAD— y un `.pyc` de
  `__pycache__` de la skill instalada, F-4). La confianza de carpeta del proyecto está **ausente** antes y después.

## Incidentes y datos del proceso (declarados)

- **Dos `git stash` sobre el árbol compartido** (GREEN de T1 y de T2), prohibidos por las restricciones globales
  del plan §7: sin efecto material (stash list vacío, árbol íntegro, commits con alcance exacto, focales intactos y
  resultado re-verificado por la review). Es deuda de proceso (RD-2).
- **Saneamientos declarados de documentos versionados** (regla de anonimización del dueño): el informe de T3 y el
  de review traían rutas absolutas del dueño en salidas de comandos; se materializaron verbatim (los recibos
  conservan los bytes originales) y se aplicó después una sustitución mecánica por `<repo>`/`<home>`. Las notas del
  state quedaron con `<ses-…>` y el mapa real de sesiones vive en `.cdad/local/` (fuera de git).
- **Artefacto del rol retirado:** el reviewer dejó `archive-head.tar` (0 bytes) en la raíz del repo; siendo
  read-only, el orquestador lo movió a `<tmp>` sin borrarlo y lo declaró.
- **El recorrido NO es de intervención cero**: fricciones F-1..F-7 de `t5-acceptance.md` §5 (buzón y descriptor
  `staged-file` a mano, transición del state a mano, la pata CC desde el checkout necesita `--install-root`, el
  `.pyc` de la skill instalada, el kind de la parte para el reviewer, y el paquete tipeado en el prompt de `Agent`
  que pierde el salto de línea final).
- **Rechazo del oráculo de T5:** el rol informó `PD-1..PD-13` cuando la spec define `PD-1..PD-11`; el rechazo del
  ítem (2) es correcto y se registra como error de contenido del rol, sin reintento y sin presentarlo como verde.

## Deuda y bloqueo que la feature deja

Consolidada en `debt.md` (con condición de cierre): **RD-1..RD-6** (mapa de hooks en dos superficies máster;
`git stash`; pata CC que comparte el marcador de la raíz; rama del registro de activación sin focal; barrido de T2
sin `scripts/`; enunciado «references this map»), las **fricciones F-3/F-5/F-7** de T5 y la **deuda de proceso de
`closure-suite.md`** (las regresiones de una tarea que edita un reference deben incluir los oráculos de texto que lo
cubren; el procedimiento de la suite de cierre debe fijar el perfil de staging). Se citan además la deuda de la
spec §8 D-1..D-7 (D-2 → unidad **005-012**) y la **preexistente F011** (D-6, delta 0 probado).

**BLOQUEO declarado, del dueño (no verde por proximidad):** el **paso b de PD-6** (confirmación con el CLI
instalado tras el despliegue) y los **cuatro cruces reservados** —confiar la carpeta de este proyecto,
copias/despliegue en HOME, emitir la activación de proyecto para CC, activar versiones en el repo real—, ninguno
ejecutado. **Cuatro desconocidos conservados `unknown` con causa** (PD-8): `exit 2` en modo no interactivo,
aplicación de los hooks del frontmatter a subagentes nativos, herencia de modelo de un subagente sin `model:`, y la
medición de contexto por rol del lado CC (no hay adaptador CC del medidor).

## Estado final

Feature **cerrada** en el estado (`epic_features: done`, `closed_at: 2026-10-13`, evidencia este archivo). Memory
Bank actualizado (borradores del scribe aprobados por el orquestador bajo la HITL delegada del epic-005) con la
entrada de `activeContext`, el bullet de `progress.md` y **ADR-026**. Sin push, sin despliegue, sin tocar HOME.

## Retorno al bucle del epic

`epic-005-real-operation` sigue en **`features-loop`**: **10/13** unidades cerradas (las filas 1..10). Restan
`005-011-common-entry`, `005-013-unit-contract` y `005-012-transition-registration` (las dos últimas
`depends_on: 005-011`), **en cola y sin abrir** (no se ejecutó `open-unit`). Orden de ejecución acordado:
**005-011 → 005-013 → 005-012**. El despliegue y el paso b quedan del dueño.
