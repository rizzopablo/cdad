# Spec — 009-001: overlay de claves de usuario en agentes instalados

- **Feature:** `009-001-installer-agent-overlay` (epic-009-installer-updates, épica light de una feature)
- **Estado:** aprobada por el orquestador (HITL delegada del dueño, 2026-10-28)
- **Autoría:** architect (stage 2, `draft`), paquete `009-001-installer-agent-overlay-architect-draft-001`
- **Evidencia de la reproducción:** `.cdad/local/009-001/evidence/repro.md`

## 1. Descripción funcional y alcance

Actualizar CDAD **preserva el `model:` elegido por el usuario** en el frontmatter del agente instalado,
**actualiza el contenido distribuido restante** y mantiene verificable su instalación.

Aplica a los agentes declarados por staging destinados a `.config/opencode/agents/` y `.claude/agents/`.
No elige modelos, no modifica `opencode.json` y no preserva personalizaciones arbitrarias como si fueran
overlay.

## 2. Contrato

**Semántica única.** `scripts/agent-overlay.py` será el único propietario de `USER_OWNED_KEYS = ("model",)`
y del reconocimiento, extracción, reinserción y comparación del overlay. Install, `--check` —incluida su
ruta legacy— y el validador consumirán esa semántica. `extract`, `merge` y `compare` son **interfaces
propuestas**: el helper todavía no existe.

**Overlay válido.** Una clave declarada como de usuario pertenece exclusivamente al **frontmatter
delimitado** del agente. Su valor se conserva sin reinterpretar. Frontmatter ausente o malformado,
duplicación, declaración de la clave en el cuerpo o valor vacío producen un **diagnóstico explícito de
divergencia**; nunca una extracción parcial aceptada en silencio.

**Actualización.** El resultado se obtiene del **staging nuevo más el overlay instalado**, no conservando
íntegro el agente viejo. Fuera de los fragmentos del overlay, los bytes deben coincidir con staging.

**Ownership y procedencia.** La comparación con staging determina la sincronía actual; la **procedencia
registrada** determina si una diferencia restante es una actualización upstream autorizada o una
modificación local. El overlay no autoriza por sí mismo a sobrescribir diferencias fuera de él. Si no hay
evidencia suficiente para acreditar la base, **se preserva el conflicto** (nunca se adopta a ciegas).

**Desinstalación.** Un agente con overlay contiene datos del usuario y **se conserva**, aunque su digest
coincida con el manifiesto actualizado. Estar owned no autoriza borrar ese overlay.

## 3. Postcondiciones verificables

### Promesa: mi configuración sobrevive y recibo la actualización

- **PC-1.** Ante una copia cuya única personalización es un overlay válido, instalar **conserva exactamente
  su valor** y **no declara conflicto** por ese overlay.
- **PC-2.** Después de actualizar staging e instalar sobre una base acreditada, **todo contenido ajeno al
  overlay coincide byte a byte con el staging nuevo**; una modificación upstream observable aparece en la
  copia instalada.
- **PC-3.** El agente actualizado **sigue owned**, con procedencia y digest correspondientes a los bytes
  instalados. Una segunda instalación sin cambios informa `SYNC`; `--check` termina con código cero cuando
  no existen otros pendientes.

Aplican a **ambos destinos runtime**, sin exigir cuotas de escenarios equivalentes.

### Promesa: una excepción no destruye mis otras modificaciones

- **PC-4.** Una modificación local **fuera del overlay**, o una entrada ambigua según §2, se **conserva sin
  sobrescritura**, se informa con motivo y **no se adopta como owned**. El overlay no oculta el conflicto
  D4 ni convierte el drift en un resultado satisfactorio de `--check`.

### Promesa: CDAD no distribuye modelos y explica mis overrides

- **PC-5.** Ningún agente **instalable** (`agents/`, staging, salidas generadas) declara `model:`. El
  validador **falla** ante esa declaración en texto instalable; **no falla** por un overlay válido
  exclusivamente instalado.
- **PC-6.** Install y `--check` **identifican el agente y el overlay preservado**; el validador también
  informa los overrides instalados. Los diagnósticos de agente faltante o divergente señalan su **ruta
  instalada**, nunca presentan la ruta de staging como destino a reparar por el usuario.

### Promesa: desinstalar no elimina mi configuración

- **PC-7.** `--uninstall` **conserva byte a byte** un agente con overlay y comunica su preservación, también
  después de una actualización que lo haya dejado owned y registrado con su digest actual.

## 4. Invariantes verificables

1. **INV-3 (006-003) intacta:** los modelos del usuario existen **exclusivamente** en copias instaladas; no
   se propagan a fuentes, staging ni salidas generadas.
2. **Una sola definición** de claves y semántica de overlay; sin filtros bash independientes que ignoren
   `model:` indiscriminadamente.
3. La excepción de overlay **no cambia** la protección D4 de las modificaciones restantes ni la protección
   de destinos symlink/no regulares.
4. `--check` y el validador **inspeccionan sin modificar** instalación ni manifiestos.
5. No se modifica `opencode.json` ni se introduce un flag para activar la preservación.

## 5. Decisiones

| # | Elección | Criterio |
|---|---|---|
| **D1** | Lista de claves como **dato**, reconocimiento limitado al frontmatter | Una casa permite ampliar claves sin duplicar consumidores; no implica soportar YAML arbitrario |
| **D2** | **Reinsertar** el overlay sobre staging nuevo, no conservar el archivo viejo | Debe llegar la actualización sin perder datos; la procedencia distingue upstream de edición local |
| **D3** | Ambigüedad → **conflicto preservado** | Prima no destruir datos: nunca interpretación heurística ni descarte silencioso |
| **D4** | Validar la prohibición sobre **texto instalable** y reportar overlays instalados | Se distingue quién es propietario de la configuración |
| **D5** | Diagnósticos dirigidos a la **ruta instalada** | El usuario debe poder localizar el archivo afectado |
| **D6** | Preservación **por defecto**, sin flag | Actualizar no debe exigir descubrir una opción para conservar configuración |

> Nota: la **D4** de esta tabla es la decisión del validador; «conflicto D4» designa la política histórica
> del instalador (conflicto preservado, no-owned).

## 6. Aceptación y evidencia

- Evidencia de PC-1…PC-7 mediante pruebas focales y ejecución en **root de arena**, sin tocar el HOME real.
- Comparaciones de **bytes, manifiesto y códigos de salida**; no basta verificar mensajes.
- Prueba **negativa** del validador sobre texto instalable y comprobación **positiva** con overlay instalado.
- Prueba de que **agregar una clave** a la lista de datos usa la misma semántica en los consumidores.
- `make validate` sin fallos y `./install.sh --check` PASS sobre la instalación declarada.
- Review del consumidor legacy, de la procedencia entre versiones y de la protección de desinstalación.
- Cierre con evidencia y Memory Bank. **Sin push.**

## 7. deferred-hardening

- **YAML arbitrario, valores complejos y conservación de estilo de serialización:** no se promete un editor
  YAML general. Los formatos no soportados se rechazan con motivo y se preservan; **antes de RED** debe
  quedar explícita la gramática admitida.
- **Personalizaciones fuera de las claves declaradas:** quedan bajo conflicto D4; un merge general excede
  esta feature.
- **Validar disponibilidad o compatibilidad del modelo:** corresponde al runtime y a la configuración del
  usuario, no al instalador.

## 8. Observaciones del architect para la fase de tests

1. **Procedencia entre versiones.** `compare(installed, staged)` no basta para distinguir un cuerpo upstream
   antiguo de una edición local; hoy sólo se cargan digest y source (`install.sh:765-803`). La solución debe
   **acreditar la base**; no debe aprobar cualquier diferencia porque haya `model:`.
2. **PC-7 cambia una decisión real de borrado.** Hoy un archivo cuyo digest coincide se considera removible
   (`install.sh:659-667,1462-1487`); tras registrar los bytes con overlay, esa regla lo borraría si no se
   incorpora la protección.
