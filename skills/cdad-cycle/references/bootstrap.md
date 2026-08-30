# Bootstrap — Inicialización de un proyecto nuevo en CDAD

Cuando el proyecto no tiene Memory Bank ni `docs/specs/`, el usuario está arrancando de cero. Esta es la primera vez que aplica CDAD a este proyecto.

## Tu objetivo

Dejar el proyecto listo para que la **primera feature** entre por la Etapa 1 (Descubrimiento) sin fricción. Esto significa:

1. Estructura `docs/` creada con templates rellenados.
2. State file inicializado.
3. Decisiones operativas tomadas (qué framework, qué tooling, qué se considera "verde").

## Pasos

### Paso 1: confirmar que el usuario quiere bootstrapear

Antes de crear archivos, preguntá:

> *"No detecté Memory Bank en este proyecto. ¿Es la primera vez que aplicás CDAD acá? Si sí, te ofrezco crear la estructura `docs/` con templates iniciales — vas a tener que rellenar partes vos (las que requieren conocimiento del proyecto que yo no tengo). ¿Avanzamos?"*

Si dice no, preguntale si el Memory Bank está en otra ubicación.

### Paso 2: recolectar contexto del proyecto

Hacé estas preguntas (una por turno o agrupadas si el usuario es expeditivo):

1. **Nombre y propósito del proyecto** — para `projectbrief.md`.
2. **Lenguaje y framework principal** — para `systemPatterns.md`. Ver Paso 2b
   (abajo) para la detección de `stack` — no dependas solo de esta pregunta: en
   bootstrap desatendido (sin humano presente) nadie la contesta.
3. **¿Hay tests existentes? ¿En qué herramienta?** (pytest, jest, rspec, etc.).
4. **¿Hay CI configurado?** Si no, mencionarlo como deuda a tomar pronto.
5. **¿Quién aprueba specs?** Generalmente el usuario, pero confirmá para registrar el nombre en el state.

No hagas un cuestionario largo. Tres o cuatro preguntas concretas y arrancá.

### Paso 2b: detección de `stack` (automática, no bloqueante)

`docs/.cdad-state.json.stack` es el campo genérico que activa variantes de rol
especializadas (`cdad-<rol>-<stack>`) — ver `cdad-cycle` §3.1. **CDAD no
conoce ningún stack por nombre**: la detección vive en cada skill de
especialización, no acá. Esto es lo que hace que Django, Rails, Odoo o
cualquier otra especialización futura se sumen sin tocar el core.

Convención: una especialización para `<stack>` se distribuye como skill
`<stack>-architect`, y **ese mismo skill declara cómo detectarse** — típicamente
una sección corta tipo "Detección automática" con marcadores objetivos del
repo (un archivo característico, una dependencia, etc.).

Procedimiento:

1. Listá los skills instalados que sigan el patrón `*-architect` (con guion,
   distinto de `cdad-architect`).
2. Para cada candidato, cargá su sección de detección automática (si la tiene)
   y evaluala contra el repo.
3. **Un solo candidato con evidencia objetiva y clara** → seteá
   `stack: <nombre>` en el state file, **sin preguntar**. Es automático a
   propósito: en bootstrap desatendido no hay a quién preguntarle.
4. **Ambigüedad (cero o más de un candidato)** → si hay usuario presente,
   preguntale; si no, dejá `stack` ausente (agentes genéricos) y registralo en
   `activeContext.md` como algo a confirmar cuando vuelva un humano.

No hace falta que sepas de antemano qué stacks existen: es autodescubrimiento
sobre lo que esté instalado.

### Paso 3: crear la estructura

Copiá los templates desde `assets/memory-bank-templates/` a `docs/` del proyecto. Rellená lo que sepas, dejá placeholders `<TODO: ...>` claros para lo que el usuario tenga que completar.

Estructura a crear:

```
docs/
├── projectbrief.md       (de assets/memory-bank-templates/projectbrief.md)
├── systemPatterns.md     (de assets/memory-bank-templates/systemPatterns.md)
├── activeContext.md      (de assets/memory-bank-templates/activeContext.md)
├── progress.md           (de assets/memory-bank-templates/progress.md)
├── adr/
│   └── README.md         (instructivo breve sobre cómo crear ADRs)
├── specs/
│   └── README.md         (instructivo breve sobre estructura de specs)
└── .cdad-state.json      (de assets/state-template.json)
```

`landscape.md` lo creás en la primera Etapa 1, no acá.

### Paso 4: inicializar state file

Contenido inicial:

```json
{
  "version": 1,
  "active_feature": null,
  "current_stage": "discovery",
  "stage_history": [],
  "tdd_substage": null,
  "postconditions_status": {},
  "approver": "<nombre que el usuario te dijo>",
  "last_updated": "<timestamp ISO>"
}
```

### Paso 5: ofrecer próximo paso

Después de crear la estructura, comunicá:

> *"Listo. Memory Bank creado en `docs/`, state file inicializado. Lo que falta que **vos** completes:*
>
> *- `docs/projectbrief.md`: las secciones marcadas TODO.*
> *- `docs/systemPatterns.md`: las convenciones técnicas que ya tengas (capas, naming, framework patterns).*
>
> *Cuando estés listo, contame cuál es la primera feature y arrancamos por Etapa 1 (Descubrimiento)."*

## Sobre `landscape.md`

`docs/landscape.md` es el documento de **descubrimiento inicial del sistema** — lo que el agente de IA aprende sobre las APIs, hooks, y convenciones del framework con el que va a trabajar. NO se crea en bootstrap; se crea en la primera Etapa 1 cuando el usuario empieza la primera feature, porque solo ahí se sabe qué partes del sistema vale mapear.

Si el usuario insiste en hacerlo en bootstrap, está bien — explicale que va a quedar como input estático del proyecto y que se va actualizando en cada Etapa 1 cuando descubran cosas nuevas.

## Anti-patrones a evitar en bootstrap

- **No crear specs en bootstrap.** Specs son por feature; en bootstrap no hay feature activa todavía.
- **No crear ADRs vacíos.** ADRs documentan decisiones tomadas; no se pre-llenan especulativamente. El folder `adr/` se crea, los ADRs concretos surgen cuando hay decisiones arquitectónicas reales.
- **No prometer que CDAD va a ser instantáneo.** El bootstrap toma 30-60 minutos honestos, principalmente por completar `projectbrief.md` y `systemPatterns.md`. Si el usuario espera 5 minutos, está subestimando el costo inicial — y ese costo es lo que paga el rendimiento posterior.

## Después del bootstrap

Cargá `references/stage-1-discovery.md` y arrancá la primera feature.
