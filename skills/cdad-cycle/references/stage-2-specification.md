# Etapa 2 — Especificación

Convertir una idea funcional en un documento técnico implementable sin ambigüedad. Output: `docs/specs/<NNN-feature-id>/spec.md` aprobado por humano.

## Tres pasos

1. Brainstorm socrático
2. Redacción del spec
3. Aprobación humana

## Paso 1 — Brainstorm socrático

### Tu rol

Sos el **agente que pregunta**. El usuario tiene la idea funcional pero probablemente con ambigüedades; tu trabajo es exponerlas haciéndolas explícitas.

### Cómo arrancar

Abrí con:

> *"Vamos a diseñar el spec de `<feature>`. Antes de proponer nada, te hago las preguntas que necesito para entender exactamente qué querés. Avisame si alguna no aplica."*

Después hacé preguntas. **No le pidas al usuario que te pase un spec ya escrito** — el valor del brainstorm es justamente extraer lo que está implícito.

### Qué preguntar (adaptá según el dominio)

Categorías típicas:

- **Inputs**: ¿qué tipos? ¿qué pasa con `null`/vacío/inválido? ¿qué validaciones?
- **Outputs**: ¿qué retorna? ¿qué formato? ¿qué pasa cuando no hay resultado?
- **Errores**: ¿excepciones tipadas? ¿mensajes específicos? ¿logs?
- **Casos de borde**: límites, casos extremos, concurrencia, idempotencia.
- **No-funcionales**: performance esperada, consumo de memoria, thread-safety si aplica.
- **Permisos / autorización**: quién puede invocar, en qué contexto.
- **Persistencia**: ¿hay side effects? ¿transacciones? ¿qué pasa si falla a mitad?
- **Out of scope**: explícitamente, qué NO hace.

### Cuándo cortar

Cuando las preguntas que te quedan son **detalles de implementación** (cómo escribir un loop, qué algoritmo elegir) y no decisiones de comportamiento, ya está. El spec captura el **qué**, no el **cómo**.

Si el usuario se cansa antes de tiempo y querés cortar, mencionalo:

> *"Hay tres preguntas más que importan para el spec. Si querés las respondés ahora; si preferís, las marco como `<TODO>` en el spec y las resolvemos antes de aprobarlo."*

## Paso 2 — Redacción del spec

### Estructura mínima (cuatro secciones)

Copiá `assets/spec-template/spec.md` y rellenalo. La estructura:

```markdown
# Spec: <nombre de la feature>

## Descripción funcional
<qué hace, en lenguaje cercano al usuario final>

## Contrato (firma e invariantes)
<firma formal con tipos, postcondiciones numeradas y verificables>

## Invariantes verificables
<propiedades que se cumplen para todo input válido — base de property tests>

## Criterios de aceptación
<medibles, no adjetivos vagos>

## Out of scope
<qué NO hace, para evitar scope creep>

## Notas de implementación (opcional)
<decisiones técnicas tomadas en el brainstorm>
```

### Reglas para postcondiciones

Cada postcondición debe ser:

- **Numerada** (1, 2, 3...): para que se pueda referenciar desde el state file y los tests.
- **Verificable**: un test puede determinar pass/fail.
- **Sobre comportamiento observable**, no implementación: "retorna `DateTime` con timezone UTC explícito" sí; "usa `fromisoformat`" no.

Ejemplo:

```
1. Si `s` es ISO 8601 válido, retorna DateTime correspondiente con timezone explícito.
2. Si `s` no tiene timezone offset, DateTime resultante es UTC explícito (no naive).
3. Si `s` no es válido, lanza InvalidDateError con mensaje incluyendo el input recibido.
```

### Reglas para criterios de aceptación

Medibles:

- ✅ "Cobertura de líneas en `src/parser.py` ≥ 95%"
- ✅ "Property test con 1000 strings random pasa"
- ❌ "El código es performante" (¿cuánto?)
- ❌ "Bien testeado" (¿qué métrica?)

### Variantes según tamaño

- **Trivial** (un fix, un campo nuevo): un párrafo + un test que falla. La estructura entera es overkill.
- **Mediana** (la mayoría): la estructura de cuatro secciones funciona.
- **Compleja** (múltiples componentes): dividir en `spec.md` (qué), `plan.md` (cómo y orden), `tasks.md` (lista con dependencias).

Decidilo con el usuario. Cuando dudes, optá por la versión más simple que captura el valor.

### Quién escribe el draft

Vos podés draftear el spec basándote en el brainstorm. El usuario edita y aprueba. **Nunca apruebes vos el spec**. La aprobación es indelegable.

## Paso 3 — Aprobación humana

### Cómo se materializa

Una marca inequívoca, una de:

1. Línea al final del spec: `Status: Approved by <nombre> on <YYYY-MM-DD>`
2. Frontmatter YAML al inicio:
   ```yaml
   ---
   approved_by: <nombre>
   approved_at: <YYYY-MM-DD>
   ---
   ```
3. Confirmación explícita en este turno (si el entorno lo permite). En este caso, **vos** registrás la aprobación en el state file:
   ```json
   "stage_history": [
     ...,
     {"stage": "specification", "completed_at": "...", "approved_by": "<nombre>"}
   ]
   ```

### Antes de marcar aprobado, validá con el usuario

Pasá el spec en pantalla y preguntá:

> *"Antes de aprobar: revisá que (a) cada postcondición es lo que querés, (b) los criterios de aceptación son medibles, (c) no falta nada en out of scope. Si está OK, lo apruebo agregando la marca al final."*

Si el usuario marca dudas, volvé al brainstorm en esa parte específica.

### Si el usuario quiere saltar la aprobación

Es la trampa principal de esta etapa. Resistí amablemente:

> *"La aprobación es lo que define si el spec captura lo que necesitás. Sin esa marca, en Etapa 4 no vamos a poder verificar si el código diverge del spec porque no vamos a saber cuándo fue el spec 'oficial'. Tres minutos de leer y aprobar te ahorran un retrabajo en Etapa 3 o 4."*

## Gate de salida (Etapa 2 → Etapa 3)

- [ ] `docs/specs/<NNN-feature-id>/spec.md` existe.
- [ ] Las cuatro secciones mínimas están presentes y no son placeholders.
- [ ] Cada postcondición es numerada y verificable.
- [ ] Cada criterio de aceptación es medible.
- [ ] Hay marca de aprobación humana inequívoca.

## Si surge algo no contemplado durante implementación

Regla: **no agregues silenciosamente al código**. Volvés al spec, lo actualizás, commiteás el cambio del spec (`docs: update spec — add postcondition X`), y recién entonces implementás. El spec es la fuente de verdad.

## Cómo cerrar la etapa

Actualizá state file:

```json
{
  "current_stage": "tdd",
  "tdd_substage": "red",
  "active_feature": "<NNN-feature-id>",
  "stage_history": [..., {"stage": "specification", "completed_at": "...", "approved_by": "..."}]
}
```

Cargá `references/stage-3-tdd.md`.
