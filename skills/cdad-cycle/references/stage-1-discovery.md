# Etapa 1 — Descubrimiento

Destruir las suposiciones del LLM sobre el sistema antes de codear. Sin esto, el agente inventa APIs, métodos y convenciones que no existen.

## Dos modalidades

- **Descubrimiento inicial** del proyecto completo: una vez al arrancar el proyecto. Output: `docs/landscape.md`.
- **Descubrimiento por feature**: mini-fase antes de cada spec. Output: sección "Contexto técnico" del spec.

## Modalidad A — Descubrimiento inicial

Solo aplica si `docs/landscape.md` no existe **y** es la primera feature del proyecto. Si ya existe, saltá a Modalidad B.

### Pasos

1. **Confirmá con el usuario que va a invertir tiempo en esto**. No es pereza saltarlo: si el sistema es muy chico o conocido, alcanza con `landscape.md` mínimo. Para frameworks grandes (Odoo, Django, Rails, Spring), vale la inversión.

2. **El usuario hace el descubrimiento manualmente**, no vos. Razón: la idea es que el humano gane conocimiento de primera mano para después poder criticar lo que el LLM proponga. Si delegás esto, perdés la base de evaluación.

3. **Tu rol es estructurador**. Hacé preguntas para que el usuario cubra los aspectos relevantes:
   - ¿Qué entidades/modelos centrales existen en el sistema?
   - ¿Qué hooks o puntos de extensión tiene el framework?
   - ¿Qué convenciones de naming, organización de carpetas, layering aplican?
   - ¿Hay diferencias entre la versión que están usando y la documentada que conviene anotar?
   - ¿Qué patrones recomendados / desaconsejados hay en este framework?

4. **El usuario te pasa notas crudas** y vos las estructurás en `docs/landscape.md` con secciones claras. Devolvé el draft, el usuario lo edita y lo confirma.

### Estructura típica de `landscape.md`

```markdown
# Landscape — <nombre del proyecto>

## Contexto del sistema
<framework, versión, propósito>

## Entidades y modelos centrales
<lista con qué hace cada uno>

## Puntos de extensión
<hooks, herencias, mecanismos del framework>

## Convenciones del proyecto
<naming, layering, organización>

## Diferencias con documentación oficial
<gotchas específicos de la versión>

## Lo que NO usamos
<patrones del framework que el proyecto evita>
```

## Modalidad B — Descubrimiento por feature

Esta es la modalidad habitual, aplicada antes de cada feature.

### Objetivo

Verificar que las suposiciones del LLM sobre la API que va a tocar son correctas. No exhaustivo: lo justo para escribir el spec sin volver a buscar al código.

### Pasos

1. **Identificá qué partes del sistema toca la feature**. Pedile al usuario que las nombre: módulos, modelos, endpoints, capas.

2. **Mapeo en sesión read-only**. Si el entorno soporta sub-agentes, abrí una sesión `architect` con permisos de **solo lectura**. Si no, hacelo vos en el flujo principal pero declarando "ahora estoy explorando, sin escribir nada". El mapeo cubre:
   - Firmas de los métodos/funciones que la feature va a tocar o extender.
   - Hooks del ciclo de vida disponibles para inyectar comportamiento.
   - Convenciones de tests del proyecto (qué fixture usar, cómo se levanta el entorno).
   - Imports/dependencias permitidos según `import-linter` o equivalente.

3. **Validá las suposiciones contra código real**. Cualquier "yo creo que X" se verifica abriendo el archivo. Si no podés ejecutar bash/lectura de código, pedí al usuario que abra el archivo y te confirme.

4. **Documentá lo aprendido**. Va a la sección "Contexto técnico" del spec en Etapa 2. Mantené durante esta etapa un draft mental o en archivo temporal.

### Spike opcional

Si la API es poco conocida o riesgosa, vale un **spike**: rama temporal donde escribís código exploratorio que vas a tirar. La regla: el código del spike no se merge; lo que se merge es el conocimiento aprendido, vuelto al landscape o al spec.

Si arrancás un spike, avisale al usuario explícitamente:

> *"Esto es un spike — voy a escribir código para aprender, lo vamos a tirar al final. ¿OK?"*

## Gate de salida (Etapa 1 → Etapa 2)

No avances sin verificar **todos**:

- [ ] Si es la primera feature: `docs/landscape.md` existe con contenido real (no solo placeholders).
- [ ] Para esta feature: el usuario puede explicarte qué APIs/hooks va a tocar sin abrir el código. Validalo preguntando: *"contame en una frase cómo va a interactuar la feature con el sistema actual"*.
- [ ] No quedan suposiciones del tipo "yo creo que existe el método X" pendientes de verificación.
- [ ] El usuario aprueba pasar a Especificación.

Si alguno falla, identificá qué falta y volvé a iterar.

## Anti-patrones

- **Saltar al spec sin descubrimiento**, asumiendo que el LLM "ya sabe" cómo es el framework. Garantía de inventos en Etapa 3.
- **Hacer descubrimiento exhaustivo** mapeando el proyecto entero. Es modalidad A, no B; consume tiempo sin ROI por feature.
- **Dejar el descubrimiento solo en cabeza**. Si no se documenta (en landscape o spec), se pierde y la próxima feature lo redescubre.

## Cómo cerrar la etapa

Cuando todos los items del gate están OK, actualizá el state file:

```json
{
  "current_stage": "specification",
  "stage_history": [
    ..., 
    {"stage": "discovery", "completed_at": "<timestamp>"}
  ]
}
```

Y avisale al usuario: *"Discovery cerrado. Pasamos a Especificación."* Cargá `references/stage-2-specification.md`.
