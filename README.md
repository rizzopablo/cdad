# Contract-Driven AI Development (CDAD)

**Una metodología disciplinada para construir software con agentes de IA**

---

## ¿Qué es CDAD?

CDAD es una metodología de desarrollo de software diseñada específicamente para trabajar con agentes de inteligencia artificial como implementadores. Resuelve un problema fundamental: los modelos de lenguaje son brillantes pero inconsistentes. Pueden generar código excelente o defectuoso, y la diferencia muchas veces no es predecible.

En lugar de confiar en review humano post-hoc y cansador, **CDAD inserta barreras estructurales antes y durante el proceso de implementación**. Estas barreras son automatizadas y garantizan que el agente nunca sea el único responsable de verificar que su trabajo es correcto.

---

## Los Cinco Principios Fundacionales

CDAD se sostiene sobre cinco principios estructurales que conforman la columna vertebral de la metodología:

### 1. **Spec antes que código (siempre)**
Antes de que cualquier agente toque una sola línea de código de implementación, debe existir un documento escrito que defina qué hace la feature, con contratos verificables incluidos.

### 2. **Contratos verificables como guardián**
Los contratos entre componentes se definen como tipos formales (interfaces, protocols, traits) con postcondiciones explícitas, verificados automáticamente mediante contract tests parametrizados.

### 3. **Sesiones aisladas con permisos granulares**
Las distintas fases del trabajo (escribir test, escribir código, refactorizar, revisar) se ejecutan en sub-agentes diferentes con permisos de archivo distintos, en sesiones separadas.

### 4. **TDD con la "Ley de Hierro"**
Nunca se escribe código de implementación sin antes tener un test que falla por la razón correcta. Sin excepciones, sin atajos, sin "después agrego el test."

### 5. **Memory Bank persistente**
El proyecto mantiene un conjunto de archivos versionados que capturan el estado actual, las decisiones tomadas, los aprendizajes acumulados, y el contexto para futuras sesiones.

---

## El Ciclo: Las Cinco Etapas

### 🔍 Etapa 1: Descubrimiento
Mapea el terreno del sistema. Destruye las suposiciones que el modelo de IA arrastra desde su entrenamiento. Genera documentación del landscape y contexto técnico.

### 📋 Etapa 2: Especificación
Brainstorm socrático, redacción del spec con descripción funcional, contrato, invariantes y criterios de aceptación, y aprobación humana.

### 🧪 Etapa 3: TDD Anti-trampa
Sub-agentes separados escriben tests (que fallan), implementan código (que pasa), refactorizan, y escriben property tests. Todo en sesiones aisladas.

### 👀 Etapa 4: Review Two-Layer
Sub-agente reviewer genera reporte priorizado de hallazgos. Vos validás la priorización antes del merge.

### ✅ Etapa 5: Merge + Memory Bank
CI automatizado valida. Actualizás el Memory Bank con decisiones, aprendizajes, y estado del proyecto.

---

## ¿Cuándo Vale la Pena CDAD?

CDAD tiene un costo operativo. No es para todo. Vale la pena cuando se cumplen al menos **dos de estas condiciones**:

- El código va a vivir mucho tiempo (meses o años) y va a evolucionar
- La corrección del código importa más allá de "compila y pasa tests"
- El proyecto es lo suficientemente grande como para que ningún humano pueda mantener todo el contexto
- El equipo va a usar agentes de IA como parte regular del flujo
- La calidad debe ser sostenible a largo plazo

### Matriz de Decisión

| Puntaje | Modo Recomendado | Aplicación |
|---------|------------------|-----------|
| 3-4 | **Vibe Coding** | Sin spec, sin sesiones aisladas, sin Memory Bank |
| 5-6 | **CDAD Light** | Spec breve, TDD con sesiones aisladas en componentes críticos |
| 7-9 | **CDAD Completo** | Las cinco etapas completas sin atajos |

---

## Estructura de un Proyecto CDAD

```
proyecto/
├── docs/
│   ├── projectbrief.md          # Qué es el proyecto
│   ├── landscape.md             # Mapeo del terreno
│   ├── systemPatterns.md        # Patrones técnicos
│   ├── activeContext.md         # Estado actual
│   ├── progress.md              # Estado de features
│   ├── adr/                     # Architecture Decision Records
│   │   ├── 001-decisión.md
│   │   └── 002-decisión.md
│   └── specs/                   # Especificaciones versionadas
│       ├── 001-feature-a/
│       │   ├── spec.md
│       │   ├── plan.md
│       │   └── tasks.md
│       └── 002-feature-b/
├── src/                         # Implementación
├── tests/                       # Tests
└── .aiignore                    # Control de permisos para sub-agentes
```

---

## Spec: Estructura Mínima

Cada feature tiene un spec que sigue esta estructura:

```markdown
# Spec: [nombre de la feature]

## Descripción funcional
Qué hace, en lenguaje no técnico.

## Contrato (firma e invariantes)
Tipos formales con postcondiciones explícitas.

## Invariantes verificables
Que se convertirán en property tests.

## Criterios de aceptación
Métricas medibles para considerar la feature done.

## Out of scope
Qué NO hace, para evitar scope creep.
```

---

## Comparación con Otras Metodologías

| Aspecto | Vibe Coding | TDD Clásico | BDD | DDD | CDAD |
|---------|-------------|-------------|-----|-----|------|
| **Quién implementa** | Agente sin restricciones | Dev humano | Dev humano | Dev humano | Sub-agentes limitados |
| **Spec antes de código** | No | Implícito | Sí (Gherkin) | Sí (modelo) | Sí (markdown) |
| **Tests primero** | A veces | Sí | Sí | No prescriptivo | Sí |
| **Contratos formales** | No | Opcional | No central | Sí | Sí |
| **Memoria persistente** | No | No | No | Sí (modelo) | Sí |
| **Calidad a largo plazo** | Variable | Alta con disciplina | Alta | Alta | Alta consistente |
| **Diseñado para agentes IA** | No | Parcial | Parcial | No | Sí |

---

## Reglas Operativas Clave

✅ **Nunca saltes etapas.** Las features que parecen simples frecuentemente revelan ambigüedades.

✅ **Si una etapa falla, volvés a la etapa anterior.** No más atrás.

✅ **La aprobación humana en momentos clave es indelegable.** Aprobás spec, validás review, evaluás Memory Bank.

---

## Casos de Uso

**✅ Usar CDAD cuando:**
- Usarás agentes de IA como implementadores principales
- El código vivirá meses/años y evolucionará
- La calidad sostenible importa más que velocidad inicial
- Necesitas documentación persistente de decisiones

**❌ No usar CDAD cuando:**
- Estás en exploración pura o prototipando algo desechable
- Es un script one-off que irá a la basura
- El código tiene menos de un mes de vida útil esperada

---

## Diferencias Clave con Alternativas

### vs. Vibe Coding
CDAD trae estructura y garantías de calidad que vibe coding no ofrece. Con agentes, sin estructura = código impredecible.

### vs. TDD Clásico
CDAD + TDD, pero con separación de agentes. El test-writer no ve la implementación. Esto elimina el sesgo de coherencia interna que los agentes tienen naturalmente.

### vs. BDD
CDAD es más técnico y específico para agentes. BDD se enfoca en comunicación con stakeholders no técnicos.

### vs. DDD
CDAD no excluye DDD. Se pueden combinar perfectamente. CDAD se enfoca en *cómo* implementar con agentes; DDD se enfoca en *qué* modelar.

---

## Próximos Pasos

1. **Lee el documento completo** (`CDAD_metodologia.md`) para entender cada etapa en profundidad
2. **Empieza con CDAD Light** si es tu primer proyecto
3. **Configura tu Memory Bank** con los documentos estructurales
4. **Establece sub-agentes** con permisos granulares
5. **Aplica la disciplina:** specs antes de código, siempre

---

## Documentación Completa

- 📖 **[CDAD_metodologia.md](./CDAD_metodologia.md)** — Documento completo con 13 capítulos
- 🧑‍🎓  **[NotebookLM CDAD](https://notebooklm.google.com/notebook/c4a9bab2-d26d-49bd-9ec7-50d256ed1dec)** — Recursos para facilitar el estudio de CDAD
- 🎯 **[docs/specs/](./docs/specs/)** — Estructura de especificaciones
- 🏗️ **[docs/adr/](./docs/adr/)** — Architecture Decision Records
- 📝 **[docs/projectbrief.md](./docs/projectbrief.md)** — Brief del proyecto

---

## Licencia

Este repositorio contiene documentación y metodología abierta para construir software con agentes de IA.

---

**CDAD: Contract-Driven AI Development** — Disciplina estructural para agentes de IA que importa.
