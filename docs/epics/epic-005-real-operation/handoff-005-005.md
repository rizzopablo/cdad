# Encargo para el orquestador — 005-005-adoption-coherence

Fecha: 2026-10-09. Portable: los valores de esta instalación (rutas, raíz adoptada, modelos)
están en el registro local `.cdad/local/handoff-005-005.local.md`, fuera de git. Si no lo tenés,
pedíselo al dueño; no los infieras.

## 1. Identidad

- **Proyecto:** este repo (`<project>` en el registro local), sin importar el directorio inicial
  de la sesión. Rama `codex/epic-005-real-operation`. Sin push.
- **Versión de ejecución:** todo el ciclo corre con la versión instalada al empezar (v8,
  `9396394`): skills, agentes y CLI de esa instalación (ruta en el registro local). El repo es lo
  que se desarrolla: **nunca** ejecutes el CLI del repo para operar el ciclo, ni reinstales a
  mitad de camino. La versión nueva se entrega en el repo; instalarla y desplegarla es otra
  tarea, fuera del ciclo y a cargo del dueño.
- **Agentes de proyecto:** la instalación de ejecución es la global (v8 desplegada el
  2026-10-09). Este repo ya no tiene activación ni agentes propios. `prepare` publica los agentes
  de proyecto desde la instalación global sin ninguna variable de entorno; verificá que
  `source_dir` de `.opencode/agents/.cdad-derived.json` sea la carpeta global de agentes. Antes de
  la primera delegación real, confirmá con una delegación chica que el subagente responde con la
  versión instalada.
- **Autoridad:** plan del epic y `execution.md`. La incorporación de 005-005 está aprobada
  («Cambios al plan», 2026-10-09).

## 2. Estado comprobado

- State en reposo legítimo (`VALID: idle`); 005-001 `done`; ningún paquete activo.
- `epic_features` todavía no tiene 005-005: agregala `in-progress` en el orden del plan y fijá
  `active_feature` y `current_stage: discovery`. Nada más.
- **Arranque verificado en una copia con el CLI instalado (v8 global), sin variables:** con solo
  esa transición, `prepare --new-execution --role architect --substage discovery` da rc 0 y
  publica los agentes de proyecto desde la carpeta global; un `prepare` del test-writer sin spec
  aprobada falla con `approval pending`. No hace falta ningún registro adicional.

## 3. Tareas (una review formal al final)

- **T1 — conservar el encargo:** `--replace-packet` valida también los campos conservados (insumos
  inexistentes, alcances fuera de la política), con un mensaje que nombre el campo y la opción
  para corregirlo; el reemplazo repetido con la corrección funciona. Regresión focal de rechazo
  sin efectos y de recuperación. Base: `_validate_corrections` en `cdad_packet.py`.
- **T2 — una política de tests:** alinear `references/stage-3-tdd.md` (hoy «una vez por GREEN»),
  `references/re-entry.md` y los paquetes canónicos (`packets/substages/implementer-green.md`
  pide «la regresión completa») con: regresión proporcional al cambio, suite completa al cierre de
  la feature, reutilización de evidencia equivalente. La metodología define la evidencia; los
  comandos los declara el proyecto. Si una corrida dependió de una condición del entorno, se
  registra en la evidencia; no se vuelve requisito. Incluye enmendar PD-17 de 005-001 según el
  recorrido ejecutado.
- **T3 — procedencia de la instalación:** `prepare` toma por defecto los agentes de la instalación
  registrada en el registro de activación del proyecto cuando existe; camino explícito para
  proyectos sin activación o para elegir otra instalación legítima; si dos fuentes se
  contradicen, el CLI dice cuál usaría y cómo resolverlo, sin cambiar de versión en silencio.
  **Modelo de ejecución real:** el dueño usa una GUI que mantiene un servidor de OpenCode
  permanente; los comandos de los agentes heredan el entorno de ese servidor, fijado al
  arrancarlo. Una variable de entorno solo sirve si va escrita en cada comando, por eso no puede
  ser el mecanismo normal: queda como opción explícita. T3 también debe dejar verificable qué
  versión cargó de verdad una sesión (por ejemplo, la versión declarada en cada agente
  publicado) y documentar en el adaptador de OpenCode si una sesión nueva relee agentes y skills
  o si hace falta recargar el servidor. Hoy no está comprobado.
  **Nivel correcto:** la regla es de la metodología y no depende del runtime: el registro de
  activación nombra la instalación, y cada adaptador (OpenCode, Claude Code, Codex, ampliable)
  sabe dónde lee su runtime los agentes y las skills, cómo publicarlos y cómo recargarlos. La
  variable `CDAD_OPENCODE_AGENTS_DIR` y `.opencode/agents/` son detalles del adaptador de
  OpenCode. Hecho verificado el 2026-10-09 (OpenCode 2.0.22, proceso nuevo): un agente de
  proyecto en `.opencode/agents/` reemplaza al global del mismo nombre. Sin agentes de proyecto,
  el runtime usa los globales; evaluar que la activación los publique, en vez de esperar al
  primer `prepare`. OpenCode tiene `opencode reload` (recargar configuración): comprobar si
  alcanza para que un servidor ya iniciado tome los agentes nuevos.
  Incluye normalizar `docs/specs/005-001-idle-and-v7-bootstrap/review.md` (coherencia y
  referencias, sin repetir la revisión) y sacar de los documentos del epic-005 las rutas
  personales, conservando los originales en el registro local.

## 4. Gates y cierre

- Focales y módulos tocados durante el trabajo. Suite completa al cierre, salvo que un cambio o
  un fallo den una razón concreta para adelantarla.
- Una review formal al final. Pedile que confirme que 005-005 elimina contradicciones y trabajo
  manual sin sumar restricciones, y que separe principio de CDAD, decisión del proyecto y
  particularidad del entorno.
- **Cierre:** una versión nueva en el repo que cumple los requisitos del ciclo. Como test de
  integración (no como despliegue), instalarla en una raíz aislada y comprobar que con ella se
  puede preparar, corregir con `--replace-packet` y despachar un encargo con la validación
  proporcional, sin rodeos manuales.
- Desplegar la versión nueva es una tarea aparte del dueño: dejá el commit de cierre y la evidencia.

## 5. Límites

- No instales CDAD en HOME ni actives versiones. Sin `--no-verify` ni push. No leas
  `tests/.sensitive-patterns.local`.
- Para comprobar un RED sin el arreglo, usá un worktree, no `git stash` en el árbol compartido.
- No vuelques salidas enormes al contexto.
- Ante un obstáculo fuera de tu ámbito, entregá el diagnóstico; no fabriques registros.
