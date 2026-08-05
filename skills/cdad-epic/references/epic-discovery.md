# Etapa E1 — Descubrimiento del epic

Mapear el dominio del epic completo. Es light: identificar qué áreas funcionales toca, no exhaustivo.

## Tu rol

Coordinás. No hacés el descubrimiento vos, ni emitís handoff a un rol específico. Esta etapa es **vos + usuario (humano o agente dueño del proceso)** directamente, igual que el descubrimiento inicial del proyecto en `cdad-cycle`.

## Por qué es light

El epic ya tiene un alcance definido. La diferencia con descubrimiento de feature es que tocás múltiples áreas funcionales que tienen que coordinarse. Lo que necesitás establecer:

1. **Scope claro**: qué entra al epic y qué no.
2. **Áreas funcionales**: qué módulos/dominios del sistema toca.
3. **Dependencias externas**: APIs, servicios, librerías, integraciones que el epic requiere.
4. **Restricciones**: regulatorias, de performance, de compatibilidad, deadlines duros.
5. **Stakeholders**: quién aprueba, quién va a usar el resultado.

## Pasos

### Paso 1 — Confirmar arranque

Si el usuario dice "arranquemos epic X", confirmá que es trabajo nuevo:

> *"Vamos a arrancar el epic `<X>`. Voy a hacerte unas preguntas para mapear el alcance, sin entrar en diseño todavía. ¿OK?"*

### Paso 2 — Hacer las preguntas

Una a tres preguntas por turno, esperando respuestas. Cubrí:

**Sobre el scope:**
- ¿Cuál es el problema que el epic resuelve, en una frase?
- ¿Qué resultado esperás cuando el epic esté done?
- ¿Qué deliberadamente NO entra en este epic? (out of scope inicial)

**Sobre áreas funcionales:**
- ¿Qué módulos o áreas del sistema toca?
- ¿Hay áreas nuevas a crear (módulos nuevos, subdominios nuevos)?

**Sobre dependencias:**
- ¿Hay APIs externas? ¿Servicios de terceros?
- ¿Hay librerías nuevas que vas a tener que evaluar/elegir?
- ¿Hay datos preexistentes a migrar o consumir?

**Sobre restricciones:**
- ¿Hay deadlines? ¿Compromisos con terceros?
- ¿Restricciones regulatorias (compliance, auditoría)?
- ¿Performance esperada? ¿Carga prevista?

**Sobre stakeholders:**
- ¿Quién aprueba el plan del epic?
- ¿Quién va a usar/operar el resultado?

No hacés un cuestionario. Tres a cinco preguntas concretas y avanzás. Si al usuario le surge algo importante por su lado, lo capturás.

### Paso 3 — Capturar en `docs/epics/<id>/discovery-notes.md` (opcional)

Para epics chicos esto puede ser parte del `plan.md` directamente. Para epics más grandes, vale tener notas separadas que después se condensan en el plan.

Si optás por archivo separado:

```markdown
# Epic <id> — Discovery Notes

## Problema
<una frase>

## Resultado esperado
<qué cambia cuando esté done>

## Áreas funcionales tocadas
<lista>

## Dependencias externas
<lista>

## Restricciones
<lista>

## Stakeholders
<lista>

## Out of scope inicial
<lista>
```

Si optás por capturar directamente en `plan.md`, saltá este archivo y construí el plan en E2.

### Paso 4 — Cerrar la etapa

Cuando tenés respuestas a las preguntas y el usuario confirma que el scope es claro:

> *"Discovery del epic cerrado. Tenemos: <resumen 1-2 líneas>. ¿Pasamos a planning para definir las features que lo componen?"*

## 🛑 Gate de salida (E1 → E2)

- [ ] Scope del epic claro: qué entra, qué no.
- [ ] Áreas funcionales identificadas.
- [ ] Dependencias externas conocidas.
- [ ] Restricciones documentadas.
- [ ] Aprobador del plan identificado.

Si todos OK: actualizá state file (`epic_stage: epic-planning`). Cargá `references/epic-planning.md`.

## Anti-patrones

- **EAP-1**: discovery se convierte en plan exhaustivo. Acá NO definís features todavía. Eso es E2. Si el usuario empieza a listar features con detalle, frenalo y guardá la lista para E2.
- **Evitar análisis paralizante**: el discovery del epic es light. Si no tenés respuesta a una pregunta, marcala como "VERIFICAR en feature N" y avanzás. Algunas restricciones se descubren al implementar, no al planificar.
