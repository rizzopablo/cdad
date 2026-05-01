# Contract-Driven AI Development (CDAD)

**Una metodología disciplinada para construir software con agentes de IA**

---

## Sobre este documento

Este documento enseña una metodología de desarrollo de software pensada específicamente para trabajar con agentes de inteligencia artificial como implementadores. La metodología se llama **Contract-Driven AI Development** (CDAD).

CDAD parte de una observación incómoda: los modelos de lenguaje son brillantes pero inconsistentes. Pueden generar código excelente o código defectuoso, y la diferencia muchas veces no es predecible. Si dejás que un agente trabaje sin restricciones —el patrón conocido como *vibe coding*— vas a obtener resultados que oscilan entre asombrosos y catastróficos. CDAD propone una respuesta: introducir barreras estructurales (specs explícitos, contratos verificables, separación de fases en sub-agentes con permisos limitados, contract tests automatizados) que *fuerzan* que el resultado sea correcto, independientemente de la consistencia del modelo subyacente.

El documento está organizado en trece capítulos. Los primeros tres son conceptuales: por qué CDAD existe, sus principios fundacionales, y comparación con alternativas. Los capítulos cuatro al nueve son operativos: cómo se ejecuta cada fase del ciclo, paso a paso, con ejemplos concretos. Los capítulos diez al doce profundizan en aspectos específicos: configuración de herramientas, adaptación a frameworks opinados, anti-patrones a evitar. El capítulo trece es referencia: glosario, checklist, recursos.

**Cómo leer el documento.** Si nunca trabajaste con agentes de IA en serio, leelo lineal. Si ya tenés experiencia y querés solo el método, podés saltar al capítulo cuatro y volver atrás cuando algo no calce. Las cajas marcadas como **Para lectores avanzados** ofrecen profundidad técnica adicional sobre temas específicos; podés saltarlas en una primera lectura sin perder el hilo.

**Qué hace falta saber para aprovecharlo.** Asumimos que sabés programar en algún lenguaje moderno (Python, JavaScript, Java, Go, Rust, lo que sea), que entendés qué es Git y un test unitario, y que tenés cierta exposición a herramientas de IA generativa para código. No hace falta haber usado un agente de IA estructuradamente antes; eso es justamente lo que vas a aprender acá.

---

## Tabla de contenidos

1. [Por qué CDAD existe](#1-por-qué-cdad-existe)  
2. [Los cinco principios fundacionales](#2-los-cinco-principios-fundacionales)  
3. [CDAD comparado con alternativas](#3-cdad-comparado-con-alternativas)  
4. [El ciclo: visión general](#4-el-ciclo-visión-general)  
5. [Etapa 1 — Descubrimiento](#5-etapa-1--descubrimiento)  
6. [Etapa 2 — Especificación](#6-etapa-2--especificación)  
7. [Etapa 3 — TDD anti-trampa con sesiones aisladas](#7-etapa-3--tdd-anti-trampa-con-sesiones-aisladas)  
8. [Etapa 4 — Review en dos capas](#8-etapa-4--review-en-dos-capas)  
9. [Etapa 5 — Merge y Memory Bank](#9-etapa-5--merge-y-memory-bank)  
10. [Configuración de herramientas](#10-configuración-de-herramientas)  
11. [CDAD en frameworks opinados](#11-cdad-en-frameworks-opinados)  
12. [Anti-patrones documentados](#12-anti-patrones-documentados)  
13. [Referencia rápida y glosario](#13-referencia-rápida-y-glosario)

---

## 1\. Por qué CDAD existe

### 1.1 El problema de los agentes de IA sin restricciones

Trabajemos sobre un escenario concreto. Imaginá que le pedís a un agente de IA: *"Implementá una función que parsee fechas en formato ISO 8601 y devuelva un objeto datetime, manejando los casos típicos."*

En el mejor escenario, el agente devuelve algo correcto: una función robusta, con manejo de timezones, validación de inputs, mensajes de error claros, y tests que cubren casos típicos y bordes. En el peor escenario —y este es el que la mayoría de la gente experimenta más seguido de lo que admite— el agente devuelve algo plausible pero defectuoso: una función que funciona para los casos obvios, falla silenciosamente cuando el input incluye un timezone no estándar, no maneja microsegundos correctamente, y los tests que escribe son los que pasan para su propia implementación, no los que verifican el spec real.

El problema no es que el modelo sea malo. El problema es estructural: cuando le das a un agente la libertad de hacer todo (entender el problema, decidir qué hacer, escribir tests, escribir código, validar), el agente optimiza por *coherencia interna* (que su test pase para su código) en lugar de *corrección externa* (que el código resuelva el problema real).

**Por qué esto pasa**

Los modelos de lenguaje son entrenados para generar continuaciones plausibles del texto que ven. Si en su contexto está tanto el test que tienen que satisfacer como el código que están escribiendo, naturalmente tienden a alinear ambos: ajustan el código para que el test pase, o ajustan mentalmente el test para que sea lo que su código va a satisfacer. Es la opción de menor energía en el espacio de posibilidades. Esto no es un defecto de modelos específicos; es una propiedad emergente del paradigma de generación.

### 1.2 La respuesta intuitiva (que no funciona)

La respuesta intuitiva al problema es: *"que el humano revise todo cuidadosamente antes de aceptarlo."* Esta respuesta tiene tres problemas serios.

Primero, el humano se cansa. Después de revisar diffs de cientos de líneas durante horas, la atención decae y los errores se cuelan. La fatiga de review es un fenómeno real y bien documentado.

Segundo, el humano no es necesariamente mejor que el agente para detectar errores sutiles. Si el código está bien estructurado y los tests pasan, un revisor humano cansado o apurado va a aprobarlo aunque tenga bugs sutiles que solo se manifiestan en producción.

Tercero, el cuello de botella humano elimina el principal beneficio de usar agentes: la velocidad. Si cada línea de código requiere review humano cuidadoso, terminás trabajando más lento que si hubieras codificado vos solo.

CDAD propone una respuesta diferente: en lugar de confiar en review humano post-hoc, **insertá barreras estructurales antes y durante** el proceso de implementación. Estas barreras son automatizadas, no requieren atención humana sostenida, y *fuerzan* que el resultado tenga ciertas propiedades verificables. El humano sigue interviniendo en momentos clave (aprobación de specs, validación de priorización del review, decisiones arquitectónicas), pero no es el guardián principal de la calidad.

### 1.3 La idea central de CDAD

La idea central de CDAD se puede resumir en una frase: **el agente nunca debe ser el único responsable de verificar que su trabajo es correcto.**

Esta idea se materializa en cinco principios estructurales que veremos en detalle en el próximo capítulo, pero que en términos generales son: especificar con contratos verificables antes de codear, separar las fases del trabajo en sub-agentes con permisos limitados, escribir el test antes que el código (de verdad, no como ritual), validar la implementación contra el contrato (no contra el test que el mismo agente escribió), y mantener un memoria persistente del proyecto que sobrevive a las sesiones individuales.

flowchart LR

    A\[Idea funcional\] \--\> B\[Spec con\<br/\>contrato verificable\]

    B \--\> C\[Test escrito\<br/\>en sesión aislada\]

    C \--\> D\[Implementación\<br/\>en sesión aislada\]

    D \--\> E\[Review\<br/\>two-layer\]

    E \--\> F\[Merge con\<br/\>contract tests\]

    F \--\> G\[Memory Bank\<br/\>actualizado\]

    G \-.próxima feature.-\> A

Cada flecha en este diagrama es una *barrera estructural*. El agente que escribe el test no ve el código. El agente que implementa no ve el razonamiento del que escribió el test. El reviewer usa un modelo distinto al implementer para tener perspectiva independiente. Los contract tests parametrizados verifican automáticamente que cualquier implementación cumple las postcondiciones del contrato, no solo el caso particular que el agente probó. Y el Memory Bank captura aprendizajes para que la próxima sesión arranque con contexto.

### 1.4 Cuándo CDAD vale la pena

Antes de avanzar, vale aclarar que CDAD no es para todo. La metodología tiene un costo operativo: requiere disciplina, documentación, configuración de herramientas, y más sesiones de agente que un flujo libre. Para tareas chicas y desechables —un script de migración de datos one-off, un experimento exploratorio, un proof of concept que se va a tirar a la basura en una semana— la disciplina de CDAD es overkill.

CDAD vale la pena cuando se cumplen al menos dos de las siguientes condiciones:

- El código va a vivir mucho tiempo (meses o años), va a evolucionar, y otros van a leerlo y modificarlo después.  
- La corrección del código importa más allá de "compila y pasa tests": tiene consecuencias económicas, de seguridad, de reputación, o regulatorias si falla.  
- El proyecto es lo suficientemente grande como para que ningún humano pueda mantener todo el contexto en la cabeza.  
- El equipo que trabaja en el proyecto va a usar agentes de IA como parte regular del flujo, no como herramienta ocasional.  
- La calidad debe ser sostenible: no es solo "que ande hoy" sino "que siga siendo mantenible dentro de seis meses cuando vuelva a tocar este código."

**Matriz observable de activación.** La lista de arriba es un buen filtro intuitivo, pero cuando estás en el día a día y necesitás decidir rápido si una tarea concreta justifica el overhead, conviene tener un criterio más operacional. La siguiente matriz puntúa la tarea en tres ejes y sugiere qué nivel de CDAD aplicar:

| Eje | Bajo (1) | Medio (2) | Alto (3) |
| :---- | :---- | :---- | :---- |
| **Vida útil esperada del código** | \< 1 mes (script one-off, spike) | 1–12 meses (módulo de proyecto puntual) | \> 12 meses (core de producto, infraestructura compartida) |
| **Costo de bug en producción** | Cosmético (UI no crítica, log mal formateado) | Operativo (re-trabajo manual, fricción para el usuario) | Económico/legal (pérdida monetaria directa, datos corruptos, exposición regulatoria) |
| **Probabilidad de evolución** | Estable (no se va a tocar) | Cambios menores esperados | Cambios mayores esperados (varios desarrolladores, varias features encima) |

Sumás los puntajes (rango 3–9) y aplicás el siguiente criterio:

| Puntaje | Modo recomendado | Qué se aplica |
| :---- | :---- | :---- |
| 3–4 | **Vibe coding** | Pedís lo que necesitás, revisás el resultado, lo usás. Sin spec, sin sesiones aisladas. |
| 5–6 | **CDAD light** | Spec breve (un párrafo \+ criterios de aceptación), TDD con sesiones aisladas para los componentes críticos solamente, review opcional. Memory Bank si el proyecto ya lo tiene. |
| 7–9 | **CDAD completo** | Las cinco etapas como las describe el documento, sin atajos. |

**Cómo usar la matriz.** No es para sacar el papelito y puntuar cada tarea de cinco minutos; es para los casos donde dudás. Si una tarea cae claramente en "es un experimento exploratorio" o claramente en "es el core que mantenemos cinco años", la matriz no aporta. Aporta cuando la tarea está en la zona gris: un script que pensabas tirar pero al cliente le gustó y se quedó en producción, una integración con un servicio externo que parece simple pero toca un flujo crítico, un fix de bug que empieza chico y revela problemas estructurales. En esos casos, puntuar los tres ejes te da defensa cuando alguien te pregunta "¿por qué tanto proceso para esto?" o "¿por qué tan poco proceso para esto?".

**Defensa frente a presión externa.** La matriz también sirve para conversaciones con clientes, project managers, o vos mismo en modo apurado. Si un PM presiona por entregar rápido y la tarea puntúa 8/9 en la matriz, tenés un argumento concreto para no saltarte el proceso: el costo de un bug en producción supera por mucho el costo de una iteración cuidadosa. Inversamente, si vos tenés tendencia a sobre-diseñar y la tarea puntúa 4/9, la matriz es el recordatorio de que CDAD completo sería sobreingeniería.

**Quiz de autoevaluación**

1. ¿Por qué un agente que escribe el test y la implementación en la misma sesión tiende a producir tests débiles?  
2. ¿Cuál es la diferencia entre confiar en review humano post-hoc y confiar en barreras estructurales pre-hoc?  
3. ¿En qué tipo de proyectos NO conviene usar CDAD?

Ver respuestas 

1. Porque el agente optimiza por coherencia interna (que su test pase para su código) en lugar de corrección externa (que el código resuelva el problema real). Como el agente ve ambos al mismo tiempo, naturalmente los alinea entre sí, perdiendo la propiedad de que el test verifica el spec independientemente de la implementación.  
     
2. Review humano post-hoc depende de atención sostenida que se cansa, criterio que puede fallar bajo presión, y se convierte en cuello de botella. Las barreras estructurales pre-hoc son automatizadas (specs explícitos, contract tests, import-linter, sesiones aisladas con permisos limitados), no requieren atención sostenida del humano para funcionar, y son consistentes en cada ejecución.  
     
3. En tareas chicas, desechables, exploratorias, o donde la corrección no tiene consecuencias serias. Por ejemplo: un script one-off de migración, un experimento que se va a tirar, un proof of concept rápido. La disciplina de CDAD agrega overhead que solo se justifica cuando el código va a vivir mucho tiempo, evolucionar, o tener consecuencias serias si falla.

---

## 2\. Los cinco principios fundacionales

CDAD se sostiene sobre cinco principios que, juntos, conforman la columna vertebral de la metodología. Cada uno responde a un fallo específico del paradigma "dejar al agente trabajar libremente". En este capítulo los exploramos en detalle, con la justificación de por qué cada uno existe.

### 2.1 Principio 1 — Spec antes que código (siempre)

**El principio.** Antes de que cualquier agente toque una sola línea de código de implementación, debe existir un documento escrito que defina qué hace la feature, con contratos verificables y criterios de aceptación.

**Por qué.** El acto de escribir un spec antes de codear cumple tres funciones distintas que muchas veces se confunden. Primera función: *forzar la formalización del requisito*. Cuando intentás escribir qué tiene que hacer una función con precisión suficiente como para que otra persona (o un agente) lo implemente correctamente, descubrís ambigüedades que tu intuición original no había detectado. Segunda función: *crear un punto de aprobación humana antes del trabajo costoso*. El spec es el momento donde vos validás que entendiste el problema y que el agente entendió el problema, antes de gastar tiempo y tokens implementando algo equivocado. Tercera función: *establecer el oráculo de verdad contra el cual se va a verificar la implementación*. El test no verifica que el código compile; verifica que el código satisface las postcondiciones del spec.

**Qué incluye un spec en CDAD.** Un spec mínimo tiene cuatro secciones:

\# Spec: parseo de fechas ISO 8601

\#\# Descripción funcional

Función que recibe un string en formato ISO 8601 y devuelve un objeto

datetime nativo del lenguaje, con timezone explícito.

\#\# Contrato (firma e invariantes)

Función: parse\_iso\_date(s: str) \-\> DateTime

Postcondiciones:

1\. Si s es un string ISO 8601 válido, retorna DateTime correspondiente.

2\. Si s no es válido, lanza InvalidDateError con mensaje descriptivo.

3\. La precisión preservada es al menos hasta milisegundos.

4\. Si s tiene timezone offset (ej "+05:30"), DateTime resultante refleja ese offset.

5\. Si s no tiene timezone, DateTime resultante es UTC explícito.

6\. La función es pura: no tiene side effects.

\#\# Invariantes verificables (serán property tests)

\- ∀s válido: parse\_iso\_date(s).to\_iso\_string() es ISO 8601 válido

\- ∀s válido: parse\_iso\_date(s) es determinístico (mismo input → mismo output)

\#\# Criterios de aceptación

\- Test unitario para cada caso de la postcondición pasa

\- Property test con 1000 strings random pasa

\- Cobertura de líneas en archivo del solver ≥95%

\#\# Out of scope (qué NO hace)

\- No parsea formatos no estándar como "MM/DD/YYYY"

\- No infiere timezones desde el contexto

**Variante: spec más liviano para features simples.** Para features muy chicas (un fix de bug puntual, un campo computado simple), el spec puede ser de un párrafo \+ un test que falla. Lo importante es que existe *algo escrito* antes del código, no que tenga un formato específico.

**Para lectores avanzados — Specs ejecutables**

Una variante avanzada del principio es escribir specs en lenguajes ejecutables como Gherkin (Cucumber, behave), TLA+ (verificación formal), o property-based test specifications (Hypothesis stateful). Estos specs no solo describen qué hace la feature; *son* la verificación de que la feature lo hace. Es el ideal del principio llevado al extremo. En la práctica, para la mayoría de proyectos, specs en markdown bien escritos \+ tests Python regulares logran el 80% del valor con el 20% del costo de mantenimiento.

### 2.2 Principio 2 — Contratos verificables como guardián

**El principio.** Los contratos entre componentes deben ser definidos como tipos formales (interfaces, protocols, traits, según el lenguaje) con postcondiciones explícitas, y verificados automáticamente por tests parametrizados que iteran sobre todas las implementaciones registradas.

**Por qué.** Cuando hay múltiples implementaciones de la misma interfaz (varios solvers para el mismo problema, varios adapters para el mismo servicio externo, varios storage backends para el mismo modelo), el agente puede satisfacer el test de una implementación y romper otra sin darse cuenta. Los contract tests parametrizados son la red de seguridad que detecta esto automáticamente: si el contrato dice "todas las implementaciones deben satisfacer la postcondición X", y un test parametrizado prueba la postcondición X contra todas las implementaciones registradas, agregar una nueva implementación o modificar una existente que rompa la postcondición se detecta inmediatamente en CI.

**Ejemplo en Python con typing.Protocol.**

\# interfaces/optimizer.py

from typing import Protocol, Sequence, runtime\_checkable

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)

class Item:

    id: str

    weight: float

    value: float

@dataclass(frozen=True, slots=True)

class Solution:

    selected\_items: Sequence\[str\]

    total\_value: float

    total\_weight: float

@runtime\_checkable

class IKnapsackSolver(Protocol):

    """Solver para el problema de la mochila 0/1.

    

    Postcondiciones contractuales (verificadas por contract tests):

    1\. selected\_items ⊆ {item.id for item in items}

    2\. total\_weight ≤ capacity

    3\. total\_value \= sum(item.value for item.id in selected\_items)

    4\. Si capacity ≥ sum(item.weight for item in items), 

       todos los items son seleccionados

    5\. Determinismo: misma entrada → misma salida

    """

    name: str

    

    def solve(

        self, 

        items: Sequence\[Item\], 

        capacity: float,

        \*,

        timeout\_seconds: float \= 30.0,

    ) \-\> Solution: ...

\# tests/test\_contract\_solvers.py

import pytest

from interfaces.optimizer import IKnapsackSolver, Item

from algorithms.greedy\_solver import GreedySolver

from algorithms.dp\_solver import DynamicProgrammingSolver

from algorithms.milp\_solver import MILPSolver

\# Cada vez que se agrega una implementación, va acá

IMPLEMENTATIONS: list\[IKnapsackSolver\] \= \[

    GreedySolver(),

    DynamicProgrammingSolver(),

    MILPSolver(),

\]

@pytest.fixture

def sample\_items():

    return \[

        Item(id="a", weight=2.0, value=3.0),

        Item(id="b", weight=3.0, value=4.0),

        Item(id="c", weight=4.0, value=5.0),

    \]

@pytest.mark.parametrize("solver", IMPLEMENTATIONS, ids=lambda s: s.name)

def test\_contract\_selected\_items\_subset(solver, sample\_items):

    """Postcondición 1: selected\_items ⊆ items"""

    solution \= solver.solve(sample\_items, capacity=5.0)

    item\_ids \= {item.id for item in sample\_items}

    assert all(sid in item\_ids for sid in solution.selected\_items)

@pytest.mark.parametrize("solver", IMPLEMENTATIONS, ids=lambda s: s.name)

def test\_contract\_capacity\_respected(solver, sample\_items):

    """Postcondición 2: total\_weight ≤ capacity"""

    solution \= solver.solve(sample\_items, capacity=5.0)

    assert solution.total\_weight \<= 5.0

@pytest.mark.parametrize("solver", IMPLEMENTATIONS, ids=lambda s: s.name)

def test\_contract\_total\_value\_consistent(solver, sample\_items):

    """Postcondición 3: total\_value es la suma correcta"""

    solution \= solver.solve(sample\_items, capacity=5.0)

    expected \= sum(

        item.value for item in sample\_items 

        if item.id in solution.selected\_items

    )

    assert solution.total\_value \== pytest.approx(expected)

Cuando un agente agrega una cuarta implementación (digamos `BranchAndBoundSolver`), debe registrarla en la lista `IMPLEMENTATIONS`. Automáticamente el contract test parametrizado corre las tres postcondiciones contra ella. Si rompe alguna, CI falla y el merge se bloquea.

**Tabla: contratos verificables en distintos lenguajes**

| Lenguaje | Mecanismo de contrato | Verificación de postcondiciones |
| :---- | :---- | :---- |
| Python | `typing.Protocol` con `@runtime_checkable` | pytest parametrizado |
| TypeScript | `interface` \+ `satisfies` operator | jest con `describe.each` |
| Java | `interface` con métodos default | JUnit 5 con `@ParameterizedTest` |
| Go | `interface` (structural typing) | tests con table-driven approach |
| Rust | `trait` con métodos | `#[test]` con macros para parametrización |
| C\# | `interface` con `[Required]` | xUnit con `[Theory]` y `[MemberData]` |

**Por qué esto es el guardián real de la arquitectura**

Sin contratos verificables, el guardián de la consistencia entre implementaciones es la disciplina del developer (que el agente no tiene) o la atención del reviewer (que se cansa). Los contract tests son disciplina automatizada: corren en cada PR, detectan inconsistencias inmediatamente, no se cansan, no tienen mal día. El costo de escribirlos una vez se amortiza enormemente porque cada nueva implementación queda automáticamente cubierta.

### 2.3 Principio 3 — Sesiones aisladas con permisos granulares

**El principio.** Las distintas fases del trabajo (escribir test, escribir código, refactorizar, revisar) se ejecutan en sub-agentes diferentes con permisos de archivo distintos, en sesiones que no comparten contexto.

**Por qué.** Los modelos de lenguaje, cuando ven en su contexto tanto el test como el código que están implementando, naturalmente tienden a alinearlos entre sí. Esto es el problema central que vimos en el capítulo 1, expresado como propiedad emergente: el modelo optimiza coherencia interna sobre corrección externa. La única solución estructural es que el agente que escribe el test *no vea* el código de implementación, y que el agente que implementa *no vea el razonamiento* del que escribió el test.

flowchart TB

    subgraph "Sesión 1: test-writer"

        S1A\[Lee spec ✓\]

        S1B\[Lee interface ✓\]

        S1C\[NO lee algorithms ✗\]

        S1D\[NO lee adapters ✗\]

        S1E\[Escribe test que falla\]

    end

    

    subgraph "Sesión 2: implementer"

        S2A\[Lee spec ✓\]

        S2B\[Lee interface ✓\]

        S2C\[Lee test escrito ✓\]

        S2D\[NO lee razonamiento sesión 1 ✗\]

        S2E\[Escribe código que pasa\]

    end

    

    subgraph "Sesión 3: refactorer"

        S3A\[Lee código verde ✓\]

        S3B\[Lee suite completa ✓\]

        S3C\[Refactoriza manteniendo tests verdes\]

    end

    

    subgraph "Sesión 4: reviewer"

        S4A\[Lee diff completo ✓\]

        S4B\[Lee spec original ✓\]

        S4C\[Lee import-linter ✓\]

        S4D\[Genera reporte priorizado\]

    end

    

    S1E \--\> S2A

    S2E \--\> S3A

    S3C \--\> S4A

**Cómo se materializa.** En herramientas modernas como OpenCode, Claude Code, Cursor, y otros entornos agénticos, esto se hace mediante *sub-agentes* configurados con permisos granulares por glob patterns. Por ejemplo:

// opencode.jsonc (ejemplo simplificado)

{

  "agents": {

    "test-writer": {

      "permissions": {

        "edit": \["tests/\*\*"\],

        "read": \["docs/specs/\*\*", "interfaces/\*\*", "tests/\*\*"\],

        "deny\_edit": \["src/\*\*", "algorithms/\*\*", "adapters/\*\*"\]

      },

      "system\_prompt": "You write failing tests that verify the spec. You never write implementation code. After writing the test, exit so a different agent can implement."

    },

    "implementer": {

      "permissions": {

        "edit": \["src/\*\*", "algorithms/\*\*", "adapters/\*\*"\],

        "read": \["docs/specs/\*\*", "interfaces/\*\*", "tests/\*\*"\],

        "deny\_edit": \["tests/\*\*"\]

      },

      "system\_prompt": "You write the minimum code that makes the existing failing test pass. You never modify the test. You never add features the test does not require."

    }

  }

}

La regla operativa es estricta: la sesión del test-writer termina antes de que arranque la del implementer, y el implementer no recibe el contexto de pensamiento del test-writer. Solo recibe el spec, la interface, y el test ya escrito.

**Variante: fallback manual sin sub-agentes formales.** Muchos entornos reales no tienen orquestadores con permisos granulares por glob pattern. Trabajás con un IDE agéntico genérico, una interfaz web de chat con el modelo, o una herramienta que indexa todo el repo automáticamente. En esos casos no podés enforcar la separación a nivel de herramienta, pero podés simularla con disciplina y técnicas concretas:

1. **Conversaciones separadas por fase.** Cada fase del ciclo (test-writer, implementer, refactorer, reviewer) arranca en una conversación nueva, no en una continuación. Cerrás explícitamente la anterior antes de abrir la siguiente. La pereza acá es el enemigo: la tentación de "seguir en la misma conversación porque ya tiene el contexto cargado" rompe el principio.  
     
2. **Carga manual de contexto mínimo.** En lugar de dejar que la herramienta autocomplete con todo el repo, le pasás explícitamente al agente solo los archivos que ese sub-agente debería ver. Para el test-writer: el spec, la interface, los tests existentes. Para el implementer: el spec, la interface, el test recién escrito. Para el reviewer: el diff, el spec, los archivos de configuración de QA. La selección manual reemplaza al permission system.  
     
3. **Prompts de "ceguera contextual" explícita.** Al inicio de cada sesión, le decís al agente algo como: *"Para esta tarea vas a actuar como test-writer. NO leas archivos en `src/` ni `algorithms/`. Si la herramienta te muestra esos archivos, ignorálos. Tu tarea es escribir tests que verifiquen el spec adjunto, no validar que mi implementación funcione."* Es ritual, sí, pero los modelos modernos suelen respetar este tipo de instrucciones cuando se ponen al inicio.  
     
4. **Repos o ramas temporales como sandbox.** Una técnica más fuerte: hacés un clon del repo (o creás una rama temporal con `.aiignore` o equivalente) donde *físicamente* no existen los archivos que el sub-agente no debería ver. El test-writer trabaja en un repo donde solo está el spec, la interface, y la carpeta de tests. Cuando termina, copiás el test al repo principal y abrís la sesión del implementer ahí. El costo es de fricción (mantener dos checkouts), pero el aislamiento es real.  
     
5. **Verificación explícita post-hoc.** Cuando termines la sesión del test-writer, antes de pasar al implementer, verificás manualmente que el test no asume nada de la implementación. Una pregunta útil: *"¿Este test seguiría siendo válido si el código se reescribe completamente con otro algoritmo?"* Si la respuesta es no, el test está acoplado a una implementación particular y hay que reescribirlo.

**Cuándo elegir cada nivel del fallback.** Si tu herramienta soporta sub-agentes con permisos granulares (OpenCode, Claude Code, etc.), usalos: es el camino más limpio. Si no los soporta pero sí soporta múltiples conversaciones independientes, usá la técnica 1+2+3 combinadas. Si trabajás con una sola conversación que persiste todo el contexto del proyecto (algunos IDEs agénticos), tu única defensa real es la técnica 4 (repos temporales). En ningún caso es aceptable saltarse el principio simplemente porque "la herramienta no me lo facilita": la consecuencia es regresar al modo "una sesión para todo" con tests que no detectan bugs.

### 2.4 Principio 4 — TDD con la "Ley de Hierro"

**El principio.** Nunca se escribe código de implementación sin antes tener un test que falla por la razón correcta. Sin excepciones, sin atajos, sin "después agrego el test."

**Por qué.** Esto puede sonar como TDD clásico (Test-Driven Development de Kent Beck), y es. La diferencia es que en CDAD la regla se aplica con rigor extra porque el implementador es un agente, no un humano disciplinado. Un humano que se salta el test puede recordar el spec y escribir código correcto. Un agente que se salta el test no tiene oráculo: implementa lo que el modelo "cree" que el spec dice, sin verificación.

La regla tiene tres partes:

Primero, *el test debe fallar antes de la implementación*. No basta con que el test exista; debe correr y fallar. Esto verifica que el test efectivamente está probando algo. Si un test pasa antes de que exista la implementación, hay algo mal: o el test no verifica lo que dice verificar, o la implementación ya existía.

Segundo, *el test debe fallar por la razón correcta*. Si el test falla porque el módulo no se importa, eso no cuenta. Si falla porque el método no existe todavía, eso no cuenta. El test debe fallar porque el comportamiento que verifica no está implementado, con un mensaje de error claro que indica qué se esperaba y qué se obtuvo.

Tercero, *el código que se escribe debe ser el mínimo que hace pasar el test*. Si el test verifica el caso de un solo elemento, el código no debe ya manejar el caso de múltiples elementos. Esa funcionalidad llega cuando llegue el test que la verifica. Esto se llama YAGNI ("You Aren't Gonna Need It") y es crítico para mantener al agente enfocado.

**Ejemplo del ciclo.** Volvamos al parser de fechas.

\# Sesión 1: test-writer escribe el primer test

\# tests/test\_parse\_iso\_date.py

import pytest

from src.date\_parser import parse\_iso\_date  \# Falla acá: módulo no existe

from datetime import datetime, timezone

def test\_parse\_simple\_date\_with\_z\_timezone():

    """Postcondición 1: string ISO válido con Z retorna UTC."""

    result \= parse\_iso\_date("2026-04-29T15:30:00Z")

    assert result \== datetime(2026, 4, 29, 15, 30, 0, tzinfo=timezone.utc)

Ejecutamos: `pytest tests/test_parse_iso_date.py`. Falla con `ModuleNotFoundError: No module named 'src.date_parser'`. Eso no es un fallo válido todavía: falta crear el módulo.

\# Sesión 1 sigue: crea el archivo con stub que falla por razón correcta

\# src/date\_parser.py

def parse\_iso\_date(s: str):

    raise NotImplementedError("not yet")

Ejecutamos otra vez: ahora falla con `NotImplementedError: not yet`. Esto sí es un fallo válido. El test prueba que `parse_iso_date` debe retornar un datetime específico, y la implementación actual no lo hace.

\# Sesión 2: implementer escribe el código mínimo

\# src/date\_parser.py

from datetime import datetime, timezone

def parse\_iso\_date(s: str) \-\> datetime:

    if s.endswith("Z"):

        return datetime.fromisoformat(s\[:-1\]).replace(tzinfo=timezone.utc)

    raise NotImplementedError("only Z timezone supported in this iteration")

Ejecutamos: `pytest tests/test_parse_iso_date.py`. Pasa. Verde.

Ahora el siguiente test cubre el caso del offset explícito:

def test\_parse\_date\_with\_explicit\_offset():

    """Postcondición 4: offset preservado en datetime."""

    result \= parse\_iso\_date("2026-04-29T15:30:00+05:30")

    expected\_tz \= timezone(timedelta(hours=5, minutes=30))

    assert result \== datetime(2026, 4, 29, 15, 30, 0, tzinfo=expected\_tz)

Falla con `NotImplementedError: only Z timezone supported`. El implementer extiende el código mínimo para satisfacer este nuevo test, sin tocar lo que ya funciona. Y así sucesivamente, postcondición por postcondición.

**Tabla comparativa: TDD clásico vs TDD anti-trampa de CDAD**

| Aspecto | TDD clásico | TDD anti-trampa (CDAD) |
| :---- | :---- | :---- |
| Quién escribe el test | El developer | Sub-agente test-writer aislado |
| Quién escribe el código | El mismo developer | Sub-agente implementer aislado |
| Información compartida | El developer ve todo en su cabeza | Cada sub-agente ve solo lo que necesita |
| Riesgo de "trampa" | Moderado (depende de disciplina) | Bajo (estructural) |
| Velocidad inicial | Más rápido (una sola "sesión") | Más lento (cambios de contexto) |
| Calidad de tests resultantes | Variable | Más alta consistentemente |

### 2.5 Principio 5 — Memory Bank persistente

**El principio.** El proyecto mantiene un conjunto de archivos versionados que capturan el estado actual, las decisiones tomadas, los aprendizajes acumulados, y el contexto que las próximas sesiones de cualquier agente necesitan para arrancar productivos.

**Por qué.** Los agentes de IA no tienen memoria entre sesiones. Cada vez que iniciás una conversación nueva, el agente empieza desde cero. Si no hay nada que documente el estado del proyecto, el agente o reinventa la rueda (ineficiente) o asume cosas incorrectas basándose en patrones generales que no aplican a tu proyecto (peligroso). El Memory Bank resuelve esto: es lo primero que cualquier agente lee al arrancar una sesión.

**Estructura típica del Memory Bank.**

docs/

├── projectbrief.md         \# Qué es el proyecto, alcance, restricciones

├── systemPatterns.md       \# Patrones técnicos consolidados

├── activeContext.md        \# Estado actual: qué se está trabajando ahora

├── progress.md             \# Estado de cada feature (in progress, done, blocked)

├── adr/                    \# Architecture Decision Records

│   ├── 001-elegimos-X-en-vez-de-Y.md

│   └── 002-arquitectura-hexagonal.md

└── specs/                  \# Specs de features

    ├── 001-feature-A/

    │   ├── spec.md

    │   ├── plan.md

    │   └── tasks.md

    └── 002-feature-B/

        └── ...

**Diferencia entre specs y ADRs.** Los specs describen *qué hace* una feature: vivientes mientras la feature está en desarrollo, eventualmente convergiendo a documentación de la feature. Los ADRs (Architecture Decision Records) describen *por qué tomamos* una decisión arquitectónica: son inmutables una vez aceptados. Si más tarde la decisión se revisa, se crea un ADR nuevo que supersede al anterior, pero el ADR original queda como histórico.

**Ejemplo de ADR.**

\# ADR-003: Usar PostgreSQL en lugar de MongoDB

\*\*Status:\*\* Accepted  

\*\*Fecha:\*\* 2026-03-15  

\#\# Contexto

Necesitamos persistencia para \[...\]. Las opciones consideradas son

PostgreSQL, MongoDB, y SQLite.

\#\# Opciones consideradas

\#\#\# Opción A: PostgreSQL

\- Pros: ACID strong, queries SQL maduras, ecosistema rico, \[...\]

\- Contras: Requiere setup explícito de schema, \[...\]

\#\#\# Opción B: MongoDB

\- Pros: Schema flexible, escalado horizontal nativo, \[...\]

\- Contras: ACID weak, queries menos expresivas, \[...\]

\#\#\# Opción C: SQLite

\- Pros: Zero config, embebido, \[...\]

\- Contras: Concurrencia limitada, \[...\]

\#\# Decisión

PostgreSQL.

\#\# Razones

1\. ACID strong es crítico para nuestros casos de uso financieros.

2\. El equipo ya tiene experiencia con SQL.

3\. Las queries que necesitamos hacer (joins complejos) son nativas en SQL.

\#\# Consecuencias

\- Necesitamos definir schema explícitamente con migraciones.

\- Costo operativo de mantener un Postgres en producción.

\- Ganancia de poder usar herramientas SQL maduras.

**Cómo el agente usa el Memory Bank.** En cada nueva sesión, el primer comando del agente debería ser leer (en orden) `projectbrief.md` para entender el contexto general, `systemPatterns.md` para conocer las convenciones técnicas, `activeContext.md` para saber qué se está trabajando ahora, y los ADRs relevantes a la feature. Después de completar la feature, el agente (o vos, validando) actualiza `activeContext.md` y `progress.md` antes de cerrar la sesión.

**Quiz de autoevaluación**

1. ¿Por qué los contract tests parametrizados son más confiables que tests escritos a mano para cada implementación?  
2. Si un test pasa antes de escribir la implementación, ¿qué está mal?  
3. ¿Cuál es la diferencia entre un spec y un ADR?

Ver respuestas 

1. Porque los contract tests parametrizados verifican automáticamente que *todas* las implementaciones registradas cumplen las postcondiciones, no solo una particular. Cuando agregás una nueva implementación, automáticamente queda cubierta sin escribir tests adicionales. Tests escritos a mano para cada implementación pueden quedar olvidados o desactualizados.  
     
2. Hay tres posibilidades: el test no verifica lo que dice verificar (es trivial), el test verifica algo que ya estaba implementado (no era una feature nueva), o el test tiene un bug que lo hace siempre pasar. En cualquier caso, el test no está cumpliendo su función de oráculo.  
     
3. Un spec describe qué hace una feature (mutable durante desarrollo, eventualmente converge a documentación). Un ADR describe por qué tomamos una decisión arquitectónica (inmutable una vez aceptado; si la decisión se revisa, se crea un ADR nuevo que supersede).

---

## 3\. CDAD comparado con alternativas

Para entender CDAD en su contexto, vale comparar sus características con las de otras metodologías y enfoques. Esto ayuda a ver qué problemas resuelve CDAD que otras no, y qué pierde con respecto a alternativas más simples.

### 3.1 Tabla comparativa de enfoques

| Aspecto | Vibe coding | TDD clásico | BDD | DDD | CDAD |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Quién implementa** | Agente sin restricciones | Developer humano | Developer humano | Developer humano | Sub-agentes con permisos limitados |
| **Spec antes de código** | No | Implícito (en cabeza) | Sí (Gherkin features) | Sí (modelo de dominio) | Sí (markdown estructurado) |
| **Tests primero** | A veces (depende del prompt) | Sí (Ley de Beck) | Sí (escenarios Gherkin) | No prescriptivo | Sí (con sesiones aisladas) |
| **Contratos formales entre componentes** | No | Opcional | No central | Sí (boundaries) | Sí (Protocols \+ contract tests) |
| **Memoria persistente del proyecto** | No | No prescriptivo | No prescriptivo | Sí (modelo) | Sí (Memory Bank) |
| **Costo inicial** | Bajísimo | Medio | Medio-alto | Alto | Medio-alto |
| **Calidad sostenible a largo plazo** | Variable, frecuentemente baja | Alta si hay disciplina | Alta | Alta para dominio complejo | Alta consistentemente |
| **Funciona bien con agentes de IA** | "Funciona" pero impredecible | Parcialmente (riesgo de trampa) | Sí, pero pesado | No prescriptivo sobre IA | Diseñado para esto |

### 3.2 Cuándo elegir qué

**Elegí vibe coding cuando:** estás en exploración pura, prototipando algo desechable, aprendiendo una tecnología nueva sin compromiso de calidad, o haciendo un script one-off que vas a tirar en una semana.

**Elegí TDD clásico cuando:** trabajás solo o en equipo pequeño humano, sin agentes de IA significativos en el flujo, y la disciplina de no saltarse el test es asumible. TDD clásico bien aplicado es muy poderoso y CDAD básicamente lo extiende para resolver el problema específico de los agentes de IA.

**Elegí BDD cuando:** los stakeholders no técnicos son parte central del proceso de definir comportamiento, y los escenarios Gherkin son herramientas reales de comunicación con ellos. BDD agrega ceremonia que solo se justifica si la usás genuinamente.

**Elegí DDD cuando:** estás modelando un dominio complejo con muchas reglas de negocio, varios bounded contexts, y la complejidad del dominio domina la complejidad técnica. DDD se puede combinar con CDAD perfectamente: el modelo DDD se documenta en el Memory Bank, los bounded contexts se enforce con import-linter al estilo CDAD.

**Elegí CDAD cuando:** vas a usar agentes de IA como implementadores principales, el código va a vivir mucho tiempo, y la calidad sostenible importa más que la velocidad inicial.

### 3.3 CDAD no es exclusivo

Una observación importante: CDAD no excluye a las otras metodologías. Podés combinar CDAD con DDD perfectamente (de hecho, los bounded contexts de DDD se materializan muy bien como capas enforceadas con import-linter en CDAD). Podés combinar CDAD con BDD si tus specs son escenarios Gherkin ejecutables. Podés combinar CDAD con metodologías ágiles como Scrum o Kanban, porque CDAD habla del proceso técnico de implementación, no de cómo organizás iteraciones.

Lo que CDAD reemplaza explícitamente es vibe coding. Si estás usando agentes de IA y querés calidad sostenible, no podés simplemente dejar al agente trabajar libre. La disciplina estructural es lo que hace la diferencia.

---

## 4\. El ciclo: visión general

Antes de profundizar en cada etapa, vale tener una vista panorámica del ciclo completo. CDAD organiza el trabajo en cinco etapas secuenciales por feature, con feedback loops específicos cuando algo falla.

### 4.1 El ciclo en un diagrama

flowchart TD

    Start(\[Idea de feature\]) \--\> E1

    

    E1\[Etapa 1\<br/\>Descubrimiento\]

    E1 \--\> E2

    

    E2\[Etapa 2\<br/\>Especificación\]

    E2 \--\> ApprovalSpec{¿Spec\<br/\>aprobado?}

    ApprovalSpec \--\>|No| E2

    ApprovalSpec \--\>|Sí| E3

    

    E3\[Etapa 3\<br/\>TDD anti-trampa\]

    E3 \--\> TestsPass{¿Tests\<br/\>pasan?}

    TestsPass \--\>|No| E3

    TestsPass \--\>|Sí| E4

    

    E4\[Etapa 4\<br/\>Review two-layer\]

    E4 \--\> ReviewOk{¿Bloqueantes\<br/\>resueltos?}

    ReviewOk \--\>|No| E3

    ReviewOk \--\>|Sí| E5

    

    E5\[Etapa 5\<br/\>Merge \+ Memory Bank\]

    E5 \--\> CIPass{¿CI\<br/\>pasa?}

    CIPass \--\>|No| E3

    CIPass \--\>|Sí| Done(\[Feature done\])

    

    Done \-.próxima feature.-\> Start

    

    style E1 fill:\#e3f2fd

    style E2 fill:\#fff3e0

    style E3 fill:\#f3e5f5

    style E4 fill:\#e8f5e9

    style E5 fill:\#fff9c4

### 4.2 Las cinco etapas en una tabla

| Etapa | Nombre | Quién hace qué | Output | Tiempo típico |
| :---- | :---- | :---- | :---- | :---- |
| 1 | Descubrimiento | Vos manualmente o con agente architect read-only | Conocimiento del terreno (APIs, hooks, convenciones) | Variable: minutos a días |
| 2 | Especificación | Brainstorm con agente architect, vos editás y aprobás | `docs/specs/NNN-feature/spec.md` aprobado | 30 min a 2 hs por feature |
| 3 | TDD anti-trampa | Sub-agentes test-writer e implementer en sesiones separadas | Código verde con tests pasando | 1-8 hs por feature |
| 4 | Review two-layer | Sub-agente reviewer \+ vos validando priorización | Reporte de hallazgos clasificados | 15-30 min por feature |
| 5 | Merge \+ Memory Bank | CI automatizado \+ vos actualizando contexto | Feature en main, Memory Bank actualizado | 10-20 min por feature |

### 4.3 Reglas operativas del ciclo

Antes de profundizar en cada etapa individual, conviene internalizar tres reglas operativas que aplican a todas:

**Regla 1: nunca saltes etapas.** La tentación de saltarte el spec porque "es una feature simple" es real y peligrosa. Las features que parecen simples al principio frecuentemente revelan ambigüedades en la fase de implementación que un spec habría detectado. La disciplina del proceso es lo que hace que el resultado sea sostenible. Si genuinamente la feature es trivial (una sola línea de código), entonces el spec puede ser de un párrafo, pero existe.

**Regla 2: si una etapa falla, volvés a la etapa anterior, no más atrás.** Si los tests fallan en la etapa 3, no volvés al spec; ajustás la implementación. Si el reviewer detecta divergencias del spec en la etapa 4, vas a la etapa 3 con instrucciones específicas; no rehacés el spec. Si el spec entero estaba mal, sí volvés a la etapa 1 (descubrimiento) y rehacés. La regla minimiza retrabajo manteniendo la integridad del proceso.

**Regla 3: la aprobación humana en momentos clave es indelegable.** Vos aprobás el spec antes de que arranque la implementación. Vos validás la priorización del review antes del merge. Vos editás y commiteás las actualizaciones del Memory Bank. Estos tres puntos son donde tu juicio sobre el dominio, el cliente, y el producto importa más que la velocidad de ejecución del agente.

---

## 5\. Etapa 1 — Descubrimiento

### 5.1 Qué hace y por qué existe

La etapa de descubrimiento existe para destruir las suposiciones que cualquier modelo de IA arrastra desde su entrenamiento sobre el sistema en el que vas a trabajar. Los modelos vieron millones de líneas de código durante su entrenamiento, pero no vieron *tu* código, *tu* configuración, ni *tu* versión específica del framework. Si los dejás trabajar sin esta etapa, inventan APIs que no existen, asumen convenciones que no aplican, o usan patrones de versiones anteriores del framework que ya no son válidos.

La etapa tiene dos modalidades: el **descubrimiento inicial** del proyecto completo (que se hace una vez al arrancar) y el **descubrimiento por feature** (mini-fase que precede a cada spec).

### 5.2 Descubrimiento inicial del proyecto

Cuando arrancás un proyecto nuevo, antes de involucrar agentes IA en serio, vale invertir tiempo en mapear el terreno. La idea es producir un documento `docs/landscape.md` (el nombre es flexible) que captura conocimiento de primera mano sobre el sistema en el que vas a trabajar.

**Cómo se hace.** Levantás una instancia limpia del sistema. Configurás un escenario realista representativo de los casos de uso que el proyecto va a cubrir. Activás modo desarrollador y debugger. Trazás manualmente flujos importantes. Anotás los hooks reales, las APIs disponibles, las convenciones de naming, las superficies de extensión que vas a usar. Si es un framework, identificás qué métodos están pensados para `_inherit`, qué clases son extensibles, qué patrones recomienda la documentación oficial.

Este conocimiento se vuelca a `docs/landscape.md` con secciones por componente o módulo. Por ejemplo, en un proyecto que extiende un framework web, el documento podría tener secciones como "Modelos disponibles", "Hooks de ciclo de vida", "Convenciones de migraciones", "Sistema de plugins", "Cambios respecto a la versión anterior", etc.

**Por qué importa.** Sin esto, los agentes inventan nombres de campos que no existen y escriben código que falla en la primera carga. Con esto, la tasa de aciertos a la primera sube dramáticamente porque los agentes tienen contexto factual concreto sobre el que basarse.

**Caso de estudio: parser de fechas**

Imaginá que vas a construir el parser de fechas que usamos como ejemplo. ¿Qué descubrimiento inicial tiene sentido?

- Verificar qué módulos de fecha provee el lenguaje (`datetime` en Python, `Date` en JS, `time` en Go)  
- Verificar qué formatos ISO 8601 cubre el parser estándar y cuáles no (Python `fromisoformat` cubre menos casos que `dateutil`)  
- Investigar si hay librerías populares para casos no cubiertos (`python-dateutil`, `arrow`, `pendulum`)  
- Mapear cómo el lenguaje representa timezones (Python tiene `timezone`, `pytz`, `zoneinfo`)  
- Identificar gotchas específicos de versión (Python 3.11+ tiene `fromisoformat` mejorado vs versiones anteriores)

Esto se vuelca al `landscape.md`: "El parser estándar de Python 3.11+ cubre \[...\], no cubre \[...\]. Para cubrir \[...\] usaremos `dateutil` como fallback, importado solo cuando el parser estándar falla."

### 5.3 Descubrimiento por feature

Antes de cada feature, hay una mini-etapa de descubrimiento más liviana. Su objetivo es verificar que las suposiciones del agente sobre la API que va a tocar son correctas.

**Cómo se hace.** Abrís una sesión read-only con un agente architect (modelo grande, permisos solo de lectura). Le pasás el contexto general (Memory Bank) y le pedís que mapee qué hooks, métodos, y campos relevantes existen para la feature que vas a hacer. El agente explora el código, lee documentación si está disponible, y produce un mapeo. Vos validás que el mapeo coincide con tu intuición y con lo que ves en el código real. Si hay discrepancias, las investigás.

El output de esta mini-etapa se incorpora al spec de la feature como sección "Contexto técnico" o similar.

**Para lectores avanzados — Spike de exploración con código real**

Para features riesgosas o donde la API a usar es poco conocida, vale ejecutar un *spike* exploratorio: una sesión donde tu objetivo no es implementar la feature sino aprender suficiente sobre la API para poder especificarla. El spike puede involucrar escribir código exploratorio en una rama temporal que después tirás. La regla: el código del spike nunca se merge a main; lo que se merge es el conocimiento aprendido, vuelto al `landscape.md` o al spec.

### 5.4 Cómo gestionar esta etapa operativamente

**Vos hacés el descubrimiento inicial manualmente.** No delegás esto al agente porque es la oportunidad de ganar conocimiento de primera mano que después usarás para criticar lo que los agentes propongan. Si saltás esto, te quedás sin la base sobre la que evaluar críticamente las propuestas posteriores.

**El descubrimiento por feature lo hace un agente architect read-only**, supervisado por vos. Vos lanzás la sesión con un prompt como "explorá la sección X del código y mapeáme los hooks disponibles para hacer Y". Validás el output antes de incorporarlo al spec.

**Cuándo dar por terminada la etapa.** El descubrimiento inicial termina cuando podés explicarle a otra persona los conceptos centrales del sistema sin abrir el código. El descubrimiento por feature termina cuando podés escribir el spec sin tener que ir a buscar nombres de APIs al código.

---

## 6\. Etapa 2 — Especificación

### 6.1 El proceso en tres pasos

La especificación es donde una idea funcional se convierte en un documento técnico que puede ser implementado por un agente sin ambigüedad. El proceso tiene tres pasos: brainstorm socrático, redacción del spec, aprobación humana.

### 6.2 Paso 1: brainstorm socrático

**Cómo se hace.** Iniciás una sesión con un agente architect en modo plan-only (sin permisos de edit). Le pedís: *"vamos a diseñar la feature X. Hacéme las preguntas que necesites para entender exactamente qué quiero, antes de proponer un diseño."*

El agente, si está bien configurado, empieza a hacer preguntas socráticas. Preguntas típicas para nuestro ejemplo del parser de fechas serían:

- ¿Qué pasa si el string es `null` o vacío? ¿Excepción, default, o `None`?  
- ¿Qué nivel de precisión interesa preservar? ¿Milisegundos? ¿Microsegundos? ¿Nanosegundos?  
- ¿Hay formatos no estándar que debemos aceptar? Por ejemplo, ¿`"2026-04-29 15:30:00"` (espacio en lugar de T)?  
- ¿Qué hace si el offset de timezone es inválido (`"+99:99"`)?  
- ¿La función debe ser thread-safe? ¿Reentrante?  
- ¿Hay restricciones de performance? ¿Latencia máxima por llamada? ¿Throughput esperado?

Vos respondés. El agente refina. Pueden surgir preguntas que vos no habías considerado y que requieren consultar al cliente, ver datos reales, o investigar más. Esto es exactamente la función del brainstorm: detectar ambigüedades antes de que se conviertan en bugs.

**Cuándo terminar el brainstorm.** El brainstorm termina cuando el agente deja de hacer preguntas significativas (las que quedan son ya de detalle de implementación) y vos sentís que la feature está lo suficientemente clara como para empezar a escribir el spec. Esto puede tomar veinte minutos para una feature simple o dos horas para una compleja.

### 6.3 Paso 2: redacción del spec

Con el brainstorm completo, escribís (o pedís al agente que escriba y vos editás) el documento del spec. La estructura mínima es la que vimos en el capítulo 2:

\# Spec: \[nombre de la feature\]

\#\# Descripción funcional

\[Qué hace, en lenguaje no técnico\]

\#\# Contrato (firma e invariantes)

\[Tipos formales con postcondiciones explícitas\]

\#\# Invariantes verificables

\[Que se convertirán en property tests\]

\#\# Criterios de aceptación

\[Métricas medibles para considerar la feature done\]

\#\# Out of scope

\[Qué NO hace, para evitar scope creep\]

\#\# Notas de implementación (opcional)

\[Decisiones técnicas tomadas durante el brainstorm\]

**Variantes según tamaño de la feature.**

Para features triviales (un fix, un cambio de configuración), el spec puede ser un párrafo \+ un test que falla. Lo importante es que existe algo escrito.

Para features medianas (la mayoría), el formato anterior funciona perfecto.

Para features complejas que abarcan múltiples componentes, el spec puede dividirse en `spec.md` (qué hace), `plan.md` (cómo se va a implementar, en qué orden), y `tasks.md` (lista de tareas concretas con dependencias). Esta separación es valiosa cuando la feature requiere coordinación.

### 6.4 Paso 3: aprobación humana

**Cómo se hace.** Leés el spec completo. Marcás dudas. Pedís ajustes al agente si algo no está claro. Cuando estás conforme, lo aprobás explícitamente. La aprobación se materializa de alguna forma verificable: agregar al final del spec una línea `Status: Approved by [tu nombre] on [fecha]`, hacer un commit con mensaje `docs: approve spec for feature X`, o cualquier marca que indique inequívocamente que vos aprobaste.

**Por qué la aprobación es indelegable.** Esta es la etapa donde tu juicio sobre el dominio importa más. Vos sabés cosas que el agente no sabe: qué necesita el cliente realmente, qué le va a sorprender, qué le va a frustrar, qué encaja con el resto del producto. Si saltás este paso, vas a debuggear durante horas implementaciones que resolvieron un problema que no era el tuyo.

**Caso de estudio: API REST de inventario**

Imaginá que estás especificando un endpoint `POST /api/v1/products` que crea un producto. Algunas preguntas que el brainstorm debería sacar a la luz:

- ¿El producto tiene SKU único? ¿Se valida unicidad? ¿En qué scope (global, por tenant)?  
- ¿Qué campos son obligatorios y cuáles opcionales?  
- ¿El precio puede ser cero o negativo? ¿Cuál es el caso de uso si sí?  
- ¿Hay un campo `created_at` automático? ¿Y `updated_at`? ¿Qué pasa con ellos en el body del request?  
- ¿Qué status code retorna en éxito? ¿201 con el producto creado? ¿200 con confirmación?  
- ¿Qué status code en validación fallida? ¿400 genérico o 422 con detalles por campo?  
- ¿Hay rate limiting? ¿Idempotencia con header `Idempotency-Key`?  
- ¿Autorización? ¿Quién puede crear productos?

Cada pregunta no respondida en el spec se convierte en una decisión que el agente toma sin tu input. Vale la pena la inversión de tiempo.

### 6.5 Cómo gestionar esta etapa operativamente

**Vos guiás el brainstorm con tus preguntas y conocimiento del dominio.** El agente formula preguntas socráticas y redacta drafts. Vos editás y aprobás.

**Mantén el spec en el repo.** No es un Google Doc, no es un Notion. Es un archivo `.md` versionado en `docs/specs/NNN-feature/`. Esto permite que se referencie desde el código, que se vea su historial, que las próximas sesiones del agente lo lean.

**Si en plena implementación detectás algo no contemplado en el spec**, no lo agregás silenciosamente al código. Volvés al spec, lo actualizás, y commiteás el cambio del spec antes de implementarlo. Esto mantiene el spec como fuente de verdad.

**Quiz de autoevaluación**

1. ¿Cuál es la diferencia entre el brainstorm socrático y simplemente "pensar la feature antes de codear"?  
2. ¿Por qué la aprobación humana del spec es indelegable?  
3. ¿Qué hacés si en plena implementación descubrís un caso no cubierto en el spec?

Ver respuestas 

1. La diferencia principal es la externalización del razonamiento. Pensar a solas tiende a saltarse las preguntas que vos ya tenés "asumidas". El brainstorm socrático con un agente fuerza explicitar esos supuestos porque el agente no los tiene asumidos. Detecta ambigüedades que tu intuición había suprimido.  
     
2. Porque vos tenés conocimiento del dominio, del cliente, y del producto que el agente no tiene. Si delegás la aprobación, perdés la oportunidad de verificar que la feature resuelve el problema correcto. Las consecuencias se manifiestan después, cuando ya gastaste tiempo implementando algo que no era lo que querías.  
     
3. Volvés al spec, lo actualizás explícitamente, commiteás el cambio del spec, y recién entonces implementás el caso. Si el spec no captura algo, agregar el caso silenciosamente al código sin actualizar el spec rompe el principio de spec como fuente de verdad y degrada el valor del proceso.

---

## 7\. Etapa 3 — TDD anti-trampa con sesiones aisladas

Esta es la etapa más larga y donde la disciplina importa más. Vamos paso a paso con un ejemplo completo.

### 7.1 La estructura de cinco sub-fases

La etapa 3 se divide internamente en cinco sub-fases. Las tres primeras corresponden al ciclo TDD clásico (RED → GREEN → REFACTOR). Se agregan dos sub-fases adicionales: property tests para componentes algorítmicos con invariantes claras, y tests de integración / E2E para verificar los flujos cross-componente derivados de los criterios de aceptación.

sequenceDiagram

    participant Vos

    participant TW as test-writer

    participant Imp as implementer

    participant Ref as refactorer

    

    Vos-\>\>TW: Sesión 1: "Escribí test para postcondición X"

    TW-\>\>TW: Lee spec \+ interface (no ve código)

    TW-\>\>Vos: Test escrito que falla (RED)

    Vos-\>\>Vos: Verifica que falla por razón correcta

    

    Vos-\>\>Imp: Sesión 2: "Hacé pasar este test"

    Imp-\>\>Imp: Lee spec \+ test \+ interface

    Imp-\>\>Vos: Código mínimo (GREEN)

    Vos-\>\>Vos: Verifica que pasa

    

    Vos-\>\>Ref: Sesión 3: "Refactorizá manteniendo verde"

    Ref-\>\>Ref: Lee código \+ suite completa

    Ref-\>\>Vos: Código refactorizado (REFACTOR)

    

    Note over Vos,Ref: Cuando el algoritmo está estable

    Vos-\>\>TW: Sesión 4: "Property tests para invariantes"

    TW-\>\>Vos: Property tests (con Hypothesis o equiv.)

**Granularidad del ciclo: agrupación de postcondiciones ortogonales.** El diagrama muestra el ciclo aplicado a una postcondición. Si una feature tiene diez postcondiciones, ¿hay que repetir el ciclo diez veces? La respuesta corta es: no necesariamente. La respuesta larga requiere distinguir entre postcondiciones *ortogonales* y postcondiciones *acopladas*.

Dos postcondiciones son **ortogonales** cuando se implementan en paths de código que no se pisan: tocan distintas funciones, distintas ramas de un condicional, distintos campos de un modelo. Para postcondiciones ortogonales, podés agrupar varias en un mismo ciclo: el test-writer escribe los tests de varias postcondiciones en una sesión (siempre que ninguno de esos tests requiera ver código de implementación), el implementer las cubre todas en una iteración GREEN, y el refactor cierra el ciclo. Acelera el ritmo significativamente sin perder la red de seguridad, porque la separación de fases (test antes que código) y el aislamiento de sesiones (test-writer ciego al código) se mantienen.

Dos postcondiciones son **acopladas** cuando comparten lógica: implementar la segunda obliga a tocar el código que satisface la primera, o cambiar el approach algorítmico para acomodar ambas. Para postcondiciones acopladas, el ciclo de a una sigue siendo la opción correcta: si las metés juntas, el implementer puede tomar una decisión arquitectónica que después invalida cuando aparezca la siguiente postcondición, y terminás reescribiendo.

**Heurística práctica.** Antes de arrancar la etapa, mirás la lista de postcondiciones del spec y las agrupás en clusters. Postcondiciones que tocan diferentes campos del mismo modelo, distintos códigos de error, distintos formatos de input, distintos endpoints: típicamente ortogonales, agrupables. Postcondiciones que cambian el algoritmo central, modifican la estructura de datos compartida, o agregan lógica transversal (logging, transacciones, auth): típicamente acopladas, una a la vez.

**Ejemplo del parser de fechas.** De las cinco postcondiciones del spec original, las postcondiciones 1 (string válido → datetime), 2 (string inválido → InvalidDateError) y 6 (función pura) son ortogonales: la primera y la sexta no se pisan en absoluto, la segunda agrega un branch de validación independiente. Se pueden agrupar en un solo ciclo. La postcondición 3 (precisión hasta milisegundos) y la 4 (offset preservado) tocan el mismo path de parsing y suelen requerir decisiones algorítmicas conjuntas: vale la pena hacerlas en ciclos separados o como un cluster acoplado.

### 7.2 Sub-fase RED: escribir el test que falla

**Setup.** Iniciás sesión nueva con el sub-agente `test-writer`. Le pasás:

- El spec aprobado (`docs/specs/NNN-feature/spec.md`)  
- La definición de la interface si existe (`interfaces/[component].py`)  
- Eventualmente el `landscape.md` si la feature toca código existente

Le pedís: *"Escribí el test que verifica la postcondición \[N\] del spec. El test debe fallar porque la implementación no existe todavía."*

**Lo que el test-writer NO ve.** No ve la carpeta de algoritmos, no ve los adapters, no ve el código de implementación que pueda ya existir parcialmente. Sus permisos de read son explícitamente limitados.

**Lo que produce.** Un test que verifica la postcondición de manera independiente de cómo se va a implementar.

**Ejemplo recurrente — caso parser de fechas**

Spec: postcondición 4 dice "Si s tiene timezone offset (+05:30), DateTime resultante refleja ese offset."

El test-writer produce:

\# tests/test\_parse\_iso\_date.py

import pytest

from datetime import datetime, timezone, timedelta

from src.date\_parser import parse\_iso\_date

def test\_postcondition\_4\_explicit\_offset\_preserved():

    """Postcondición 4: offset explícito se preserva en el datetime resultante."""

    \# Caso simple: offset positivo

    result\_pos \= parse\_iso\_date("2026-04-29T15:30:00+05:30")

    expected\_pos \= datetime(

        2026, 4, 29, 15, 30, 0,

        tzinfo=timezone(timedelta(hours=5, minutes=30))

    )

    assert result\_pos \== expected\_pos

    

    \# Caso simétrico: offset negativo

    result\_neg \= parse\_iso\_date("2026-04-29T15:30:00-03:00")

    expected\_neg \= datetime(

        2026, 4, 29, 15, 30, 0,

        tzinfo=timezone(timedelta(hours=-3))

    )

    assert result\_neg \== expected\_neg

El test verifica que el offset se preserva. No asume nada sobre cómo el parser hace el parsing internamente.

**Verificación obligatoria antes de cerrar la sesión.** Corrés `pytest` y confirmás que el test falla por la razón correcta (el método retorna algo distinto a lo esperado, o lanza `NotImplementedError`, no por error de import o sintaxis). Si falla por una razón equivocada, el test no es válido y hay que arreglarlo dentro de esta misma sesión antes de pasar a la siguiente.

### 7.3 Sub-fase GREEN: implementar el código mínimo

**Setup.** Sesión nueva con el sub-agente `implementer`. Le pasás:

- El spec  
- El test que el test-writer escribió (visible)  
- La interface  
- Permisos de edit en `src/`, `algorithms/`, `adapters/`

Le pedís: *"Hacé pasar este test escribiendo el mínimo código necesario. No agregues funcionalidad que el test no requiera."*

**Lo que el implementer NO ve.** No recibe el contexto de pensamiento del test-writer (la conversación previa). Solo recibe el artefacto final: el test escrito. Esto evita que el implementer "hereede" el approach mental del test-writer y termine con código demasiado parecido a la mente del test-writer.

**Lo que produce.** Código que hace pasar el test específico, sin más.

**Continuando el caso parser de fechas**

El implementer recibe el test del paso anterior. Su tarea es agregar al `parse_iso_date` el soporte para offsets explícitos. Si el código actual maneja solo `Z`:

\# src/date\_parser.py (ANTES)

from datetime import datetime, timezone

def parse\_iso\_date(s: str) \-\> datetime:

    if s.endswith("Z"):

        return datetime.fromisoformat(s\[:-1\]).replace(tzinfo=timezone.utc)

    raise NotImplementedError("only Z timezone supported")

El implementer extiende para satisfacer el nuevo test, sin tocar lo que ya funciona:

\# src/date\_parser.py (DESPUÉS)

from datetime import datetime, timezone

import re

\_OFFSET\_RE \= re.compile(r"(\[+-\]\\d{2}):(\\d{2})$")

def parse\_iso\_date(s: str) \-\> datetime:

    if s.endswith("Z"):

        return datetime.fromisoformat(s\[:-1\]).replace(tzinfo=timezone.utc)

    \# Python 3.11+ fromisoformat ya maneja offsets, pero ilustramos

    \# el approach explícito para versiones anteriores

    return datetime.fromisoformat(s)

El implementer NO agrega funcionalidad para timestamps sin timezone (postcondición 5), porque no hay test que la requiera todavía. Esa postcondición vendrá en su propia iteración del ciclo.

**Verificación.** Corrés `pytest` y confirmás que el nuevo test pasa Y que todos los tests que ya estaban pasando siguen pasando. Si algún test anterior se rompió, el implementer hizo cambios que afectaron lo que ya funcionaba; volvé al implementer en la misma sesión con el reporte de fallas.

### 7.4 Sub-fase REFACTOR: mejorar manteniendo verde

**Setup.** Sesión nueva con el sub-agente `refactorer` (puede ser el mismo `implementer` con un prompt distinto, o un sub-agente dedicado). Le pasás:

- El código que ya pasa los tests  
- La suite de tests completa visible  
- Permisos de edit en código

Le pedís: *"Refactorizá este código para mejorar legibilidad, mantenibilidad, y consistencia con el resto del codebase. Todos los tests deben seguir pasando. No cambies el comportamiento observable."*

**Lo que el refactorer hace.** Renombra variables para mayor claridad, extrae funciones cuando hay duplicación, consolida estructuras de control, agrega docstrings, ajusta tipos. Lo que NO hace es cambiar funcionalidad, agregar features, o tocar tests.

**Cuándo no hacer refactor.** Si el código quedó simple y claro después del GREEN, esta sub-fase puede ser skippable. La regla es honesta: refactorizá cuando aporta, no por compulsión de proceso.

### 7.5 Sub-fase Property Tests: invariantes con generación aleatoria

Para componentes algorítmicos (donde la corrección no se reduce a casos discretos sino que tiene propiedades generales), agregamos una sub-fase final donde generamos property tests usando herramientas como Hypothesis (Python), QuickCheck (Haskell), fast-check (TypeScript), o equivalentes en otros lenguajes.

**Cómo funciona.** En lugar de escribir casos específicos, escribís *propiedades* que el algoritmo debe satisfacer para *todos* los inputs válidos. La librería genera cientos o miles de inputs aleatorios y verifica la propiedad en cada uno. Si encuentra un input donde falla, te lo reporta minimizado.

**Ejemplo: property tests del parser de fechas**

\# tests/test\_parse\_iso\_date\_properties.py

from hypothesis import given, strategies as st

from datetime import datetime, timezone, timedelta

from src.date\_parser import parse\_iso\_date

\# Estrategia que genera datetimes aleatorios con timezone

aware\_datetimes \= st.datetimes(

    min\_value=datetime(1900, 1, 1),

    max\_value=datetime(2100, 12, 31),

    timezones=st.timezones(),

)

@given(dt=aware\_datetimes)

def test\_round\_trip\_property(dt):

    """Invariante: parse(format(dt)) \== dt para todo dt."""

    iso\_string \= dt.isoformat()

    parsed \= parse\_iso\_date(iso\_string)

    assert parsed \== dt, (

        f"Round-trip failed for {iso\_string}: got {parsed}, expected {dt}"

    )

@given(s=st.from\_regex(r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"))

def test\_z\_timezone\_is\_utc\_property(s):

    """Invariante: cualquier string con Z al final se parsea como UTC."""

    try:

        result \= parse\_iso\_date(s)

        assert result.tzinfo \== timezone.utc

    except ValueError:

        pass  \# strings inválidos pueden lanzar ValueError, eso está OK

Hypothesis va a generar miles de strings y datetimes, y si encuentra alguno donde la propiedad no se cumple, lo reporta. Frecuentemente encuentra edge cases que tests determinísticos no detectan: fechas en el límite del rango aceptado, timezones inusuales, fechas en años bisiestos, etc.

**Cuándo agregar property tests.** No para todo. Funcionan especialmente bien para:

- Algoritmos puros (parsers, codificadores, solvers, transformaciones de datos)  
- Componentes con invariantes claras (round-trip, idempotencia, asociatividad)  
- Código crítico donde tests determinísticos pueden tener blind spots

Funcionan menos bien para:

- Código con muchos side effects  
- Lógica de negocio compleja con muchas condiciones  
- UI

### 7.6 Sub-fase de tests de integración y E2E

Los unit tests, contract tests y property tests cubren componentes individuales y sus invariantes. Pero los clientes no usan componentes; usan flujos completos. Si la feature toca varias capas (DB, lógica de negocio, API, UI), un test que verifica que cada componente funciona aislado puede pasar al 100% mientras el flujo end-to-end falla porque la integración entre las piezas no es la esperada.

**El riesgo del agente que se "alinea" sigue presente acá.** A primera vista, los tests E2E son la fase donde uno se siente tentado a relajar la disciplina: son lentos, son pocos, "ya tenemos cobertura unitaria". Pero el riesgo de que el agente alinee test E2E con su implementación es exactamente el mismo que en los unit tests. Si el implementer escribe el test E2E, va a verificar que el flujo "anda como yo lo construí", no que cumpla los criterios de aceptación del spec.

**La salida limpia: derivar tests E2E del spec, no del código.** Los criterios de aceptación de un spec bien escrito son, en gran medida, tests E2E en lenguaje natural. *"Al confirmar la venta, el stock disminuye y se genera factura draft"* es un test E2E. *"Si el usuario no tiene permisos de aprobación, el endpoint retorna 403"* es un test E2E. La regla operativa es: los tests E2E se escriben en una sesión `test-writer` que ve el spec (incluyendo criterios de aceptación) y la API pública del sistema, pero no ve la implementación de la feature en curso.

**Cómo encaja en el ciclo.** Hay dos modalidades válidas, según la naturaleza de la feature:

*Modalidad A — E2E primero (outside-in).* El test E2E se escribe antes que cualquier unit test. Se escribe del spec hacia abajo, expresando un flujo completo. Este test queda rojo durante todo el ciclo de implementación, hasta que las piezas individuales (cubiertas por unit tests) se conectan y el flujo completo pasa. Es el approach de Acceptance Test-Driven Development clásico. Funciona bien cuando el flujo es claro desde el inicio y querés tener una métrica continua de progreso ("¿cuánto falta para que el E2E pase?").

*Modalidad B — E2E al final como cierre.* El test E2E se escribe después de que las unidades están implementadas y verdes, pero antes del merge. Funciona como verificación de que el ensamblaje es correcto. Es más simple operativamente y menos pesado en CI durante el desarrollo, pero te perdés la métrica continua del approach A.

**Cuál elegir.** Para features con un flujo claro y central (un endpoint nuevo, un proceso de negocio definido), preferí modalidad A. Para features que son agregados a múltiples flujos existentes (un campo nuevo que aparece en cinco vistas, una validación que se aplica en varios endpoints), modalidad B es más práctica.

**Estructura de un test E2E en CDAD.** El test E2E sigue el mismo principio que los unit tests: arrange, act, assert, con assertions específicas de los criterios de aceptación. La diferencia es la granularidad del setup (fixtures de datos completas, no mocks puntuales) y el alcance del act (un flujo completo, no una llamada a función).

**Ejemplo: feature "confirmación de venta"**

Spec con criterio de aceptación: *"Al confirmar una orden de venta con productos en stock, (a) el estado de la orden pasa a 'sale', (b) el stock de los productos disminuye en la cantidad correspondiente, (c) se genera una factura draft con los líneas de la orden, (d) si el cliente no tiene crédito disponible, la confirmación falla con mensaje específico."*

El test-writer, en sesión aislada del implementer, traduce esto a algo como:

\# tests/integration/test\_sale\_confirmation\_e2e.py

def test\_confirm\_sale\_with\_stock\_succeeds(self):

    \# Arrange: cliente con crédito, productos con stock

    customer \= self.\_create\_customer(credit\_limit=10000)

    product \= self.\_create\_product(initial\_stock=10)

    order \= self.\_create\_draft\_order(customer, \[(product, 3)\])

    

    \# Act: confirmar la orden via la API pública

    result \= self.client.post(f"/api/orders/{order.id}/confirm")

    

    \# Assert: cuatro postcondiciones del criterio de aceptación

    assert result.status\_code \== 200

    order.refresh()

    assert order.state \== "sale"  \# (a)

    assert product.available\_stock \== 7  \# (b)

    invoice \= self.\_find\_draft\_invoice\_for(order)

    assert invoice is not None and invoice.state \== "draft"  \# (c)

    assert len(invoice.lines) \== 1

    assert invoice.lines\[0\].quantity \== 3

def test\_confirm\_sale\_without\_credit\_fails(self):

    customer \= self.\_create\_customer(credit\_limit=0)

    product \= self.\_create\_product(initial\_stock=10)

    order \= self.\_create\_draft\_order(customer, \[(product, 3)\])

    

    result \= self.client.post(f"/api/orders/{order.id}/confirm")

    

    assert result.status\_code \== 422

    assert "crédito" in result.json()\["error"\].lower()  \# (d)

    order.refresh()

    assert order.state \== "draft"  \# estado no cambió

El test-writer escribe estos casos viendo solo el spec y la API pública del sistema. No mira el código del confirmador. El implementer recibe estos tests y los hace pasar. La integración correcta se verifica automáticamente.

**Cuándo NO agregar tests E2E.** Para features puramente algorítmicas sin side effects (un parser, un transformador de datos), los unit tests \+ property tests cubren todo lo que necesitás. Agregar un E2E es ceremonia sin valor. La regla: E2E cuando hay flujo cross-componente con efectos observables; unit \+ property cuando no.

### 7.7 Cómo gestionar esta etapa operativamente

**Vos sos el orquestador.** Abrís y cerrás sesiones. Verificás que cada paso pasa antes de avanzar. Hacés commits intermedios entre sub-fases para tener checkpoints.

**El ritmo típico.** Para una postcondición con ciclo completo (RED → GREEN → REFACTOR): entre 30 y 90 minutos según complejidad. Para una feature con cinco postcondiciones, calculá entre 3 y 8 horas en total. Esto incluye los inevitables idas y vueltas cuando algún test falla por motivo equivocado o el implementer hace algo no pedido. Si agrupás postcondiciones ortogonales, el tiempo total baja sustancialmente.

**La tentación a resistir: "una sola sesión para todo."** Es la trampa principal de la etapa. Cuando el implementer también escribe el test, perdés el oráculo independiente. La velocidad aparente que ganás (no tener que cambiar de contexto) se paga con tests débiles que no detectan bugs reales.

**Commits granulares.** Cada paso del ciclo termina en un commit. Mensajes típicos: `test: add failing test for postcondition 4`, `feat: implement parsing of explicit offsets`, `refactor: extract offset parsing helper`. Esto da historial limpio y permite hacer `git bisect` cuando algo se rompe después.

**Quiz de autoevaluación**

1. ¿Por qué el test-writer no debe ver el código de implementación?  
2. ¿Qué hace específicamente el implementer cuando un test falla por una razón equivocada (ej: ImportError)?  
3. ¿Cuándo conviene saltarse la sub-fase REFACTOR?  
4. ¿En qué tipo de código los property tests son más valiosos?

Ver respuestas 

1. Porque si lo viera, su test tendería a alinearse con la implementación particular en lugar de verificar el spec independientemente. Esto haría que el test pase no porque el código sea correcto, sino porque el test fue escrito para que pase con ese código específico. La separación garantiza que el test sea un oráculo genuino.  
     
2. Vuelve al test-writer para arreglar el test, no al implementer. Si el test falla por ImportError u otro error técnico, el test no está verificando lo que dice verificar. Hay que arreglar el test antes de pasar al implementer.  
     
3. Cuando el código que salió del GREEN ya es claro, conciso, y consistente con el resto del codebase. La sub-fase REFACTOR no es obligatoria; es una oportunidad. Si no aporta, no la hagas. La regla es: refactorizá cuando aporta valor, no por ritualismo.  
     
4. En código algorítmico con invariantes claras: parsers, encoders/decoders, solvers, transformaciones de datos. Donde podés expresar propiedades generales que deben cumplirse para todos los inputs válidos (round-trip, idempotencia, asociatividad). Funciona menos bien en código con muchos side effects o lógica de negocio con muchas condiciones específicas.

---

## 8\. Etapa 4 — Review en dos capas

### 8.1 Por qué dos capas

El review tradicional en equipos humanos tiene dos problemas en proyectos donde los agentes implementan: el reviewer humano se cansa rápido frente a diffs grandes, y muchas veces no detecta divergencias del spec porque no recuerda el spec en detalle. CDAD propone un modelo de dos capas: primero un agente reviewer hace pasada exhaustiva con el spec en contexto y produce un reporte priorizado; después vos validás la priorización (no el diff completo).

flowchart LR

    Diff\[Diff completo\<br/\>de la feature\] \--\> AReviewer\[Capa 1\<br/\>Agente reviewer\]

    Spec\[Spec aprobado\] \--\> AReviewer

    Linter\[import-linter\<br/\>boundaries\] \--\> AReviewer

    

    AReviewer \--\> Reporte\[Reporte priorizado\<br/\>Bloqueantes / Opcionales\]

    

    Reporte \--\> Humano\[Capa 2\<br/\>Vos\]

    

    Humano \--\> Decision{¿Priorización\<br/\>correcta?}

    Decision \--\>|Sí| Done\[Lista de fixes\<br/\>para implementer\]

    Decision \--\>|Ajustar| Manual\[Agregás bloqueantes\<br/\>o desestimás opcionales\]

    Manual \--\> Done

### 8.2 Capa 1: agente reviewer

**Setup.** Sesión nueva con sub-agente `reviewer` con permisos de read-only. Le pasás:

- El diff completo de la feature  
- El spec aprobado  
- La interface que la feature implementa  
- El archivo `.importlinter` con los boundaries arquitectónicos  
- Convenciones del proyecto si existen (`AGENTS.md` o `CONTRIBUTING.md`)

**Idealmente, usás un modelo distinto al que implementó.** Esta es una práctica importante: si el implementer fue Claude Sonnet, el reviewer puede ser GPT-5 o Qwen. La razón es que distintos modelos tienen blind spots distintos; usar uno diferente para review da una segunda perspectiva real, no un eco. Si solo tenés un modelo, igual funciona, pero perdés esa diversidad.

**El prompt al reviewer.** Algo como:

\*"Revisá este diff contra el spec adjunto. Reportá hallazgos en estas categorías:

1. **Divergencias del spec**: el código no implementa lo que el spec pide, o agrega cosas que el spec no pide.  
2. **Violaciones de boundaries**: imports prohibidos por el import-linter, capas que no respetan las dependencias permitidas.  
3. **Riesgos de seguridad**: SQL injection, command injection, secretos hardcodeados, validación faltante.  
4. **Problemas de consistencia**: el código no sigue las convenciones del resto del proyecto.  
5. **Sugerencias de simplificación**: oportunidades de hacer el código más simple sin cambiar comportamiento.

Para cada hallazgo, marcá: **Bloqueante** (debe arreglarse antes del merge) u **Opcional** (sugerencia, no bloquea).

Producí un reporte estructurado en markdown."\*

**El output.** Un reporte estructurado, algo así:

\# Review de feature: parseo de fechas con offsets

\#\# Bloqueantes

\#\#\# 1\. Divergencia del spec — Postcondición 5 no cubierta

Ubicación: src/date\_parser.py:8-12

Problema: La postcondición 5 del spec dice "Si s no tiene timezone, 

DateTime resultante es UTC explícito". El código actual usa 

fromisoformat() que en Python \<3.11 retorna naive datetime, no UTC.

Sugerencia: agregar branch explícito para detectar ausencia de 

timezone offset y forzar UTC.

\#\#\# 2\. Violación de boundary — import desde algorithms a adapters

Ubicación: algorithms/parser\_helpers.py:3

Problema: import-linter contract "algorithms-pure" prohíbe imports 

desde algorithms/ hacia adapters/. La línea 3 viola este contrato.

Sugerencia: mover el helper a interfaces/ o duplicar la lógica si 

es trivial.

\#\# Opcionales

\#\#\# 3\. Sugerencia de simplificación — regex precompilado innecesario

Ubicación: src/date\_parser.py:5

Problema: El regex compilado en módulo no se usa en el código actual.

Sugerencia: removerlo si no se va a usar.

\#\#\# 4\. Estilo — docstring formato no consistente

Ubicación: src/date\_parser.py:7

Problema: el docstring usa formato distinto al resto del proyecto.

Sugerencia: ajustar al formato del resto.

### 8.3 Capa 2: validación humana

**Cómo se hace.** Leés el reporte, no el diff completo. El reviewer ya hizo el trabajo de filtrar y priorizar; tu trabajo es validar esa priorización.

Para cada bloqueante, decidís si genuinamente es bloqueante. La mayoría de las veces vas a estar de acuerdo, pero hay casos en que vos sabés algo que el reviewer no: tal vez la "divergencia del spec" es porque el spec cambió y todavía no se actualizó, tal vez la "violación de boundary" tiene una excepción legítima documentada en un ADR.

Para cada opcional, decidís si lo aplicás ahora o lo descartás. Algunas opcionales son francamente buenas y vale aprovechar el momentum; otras son sobre-ingenierización que no aporta.

**El output de la capa 2\.** Una lista priorizada de fixes que va al implementer en una nueva ronda. Algo como:

\*"Aplicá estos cambios al código:

1. \[Bloqueante\] Agregar branch en parse\_iso\_date para casos sin timezone, retornando UTC explícito.  
2. \[Bloqueante\] Mover parser\_helpers a interfaces/ y actualizar imports.  
3. \[Aceptado opcional\] Remover el regex no usado.

Ignoramos por ahora:

- Cambio de docstring (lo haré yo después en una pasada de cleanup)."\*

### 8.4 El feedback loop con la etapa 3

Si hay bloqueantes, volvés a la etapa 3 con la lista de fixes. El implementer aplica los cambios, los tests deben seguir pasando (si los fixes requieren cambios de comportamiento, eso significa que el spec necesita actualizarse y volver a la etapa 2). Después de los fixes, opcionalmente otra pasada del reviewer para verificar.

**Tabla: matriz de severidad de hallazgos**

| Tipo de hallazgo | Severidad por defecto | Excepción |
| :---- | :---- | :---- |
| Divergencia del spec | Bloqueante | Solo si vos validás que el spec estaba desactualizado |
| Violación de boundary | Bloqueante | Solo si hay ADR explícito autorizando |
| Riesgo de seguridad | Bloqueante | Sin excepciones |
| Bug funcional | Bloqueante | Sin excepciones |
| Inconsistencia de estilo | Opcional | Bloqueante si es masiva |
| Oportunidad de simplificación | Opcional | Bloqueante si la complejidad actual es problemática |
| Sugerencia de feature adicional | Descartar | Esto es scope creep |

### 8.5 Cómo gestionar esta etapa operativamente

**Mantén el reporte del reviewer en el PR o en un archivo temporal.** Útil cuando el implementer aplica fixes, para verificar que se cubrieron todos los bloqueantes.

**El review NO es opcional.** La tentación de saltarse el review en features pequeñas es fuerte. Resistila. Aunque sea un review breve de un agente reviewer corriendo sobre un diff de 30 líneas, vale la pena: detecta inconsistencias que en el momento parecen menores pero que se acumulan.

**Revisá tu propia priorización con escepticismo sano.** Es fácil rechazar un bloqueante porque te cuesta volver al implementer. Si lo hacés sistemáticamente, estás minando la calidad. Una heurística útil: si dudás de si un bloqueante es genuino, errate del lado de tratarlo como bloqueante. El costo de una iteración extra es bajo; el costo de mergear un bug es alto.

---

## 9\. Etapa 5 — Merge y Memory Bank

### 9.1 Verificación CI antes del merge

Antes de mergear, una suite completa de verificaciones automatizadas debe pasar. Esto NO es opcional, y NO se puede skipear porque "tengo confianza en este cambio". Las verificaciones son:

**Linter completo.** Ejecuta sobre todos los archivos modificados, no solo los del diff. Detecta violaciones de estilo, bugs comunes (variable no usada, import no usado), y patrones problemáticos.

**Type checker.** Si el lenguaje soporta tipos estáticos (Python con mypy, TypeScript con tsc, etc.), corre sobre el código. En CDAD, recomendamos modo strict al menos para los archivos de interfaces y contratos.

**Import-linter (o equivalente).** Verifica que los boundaries arquitectónicos no se violaron. Si hay contratos de capas (presentation no importa de domain, algorithms no importa de framework), import-linter los enforce.

**Tests unitarios y de integración.** La suite completa, no solo los nuevos. La razón es que los nuevos pueden haber roto cosas que ya funcionaban.

**Contract tests parametrizados.** Si la feature agrega una implementación de un Protocol, los contract tests automáticamente la verifican. Si rompe alguna postcondición, falla acá.

**Tests de propiedades.** Para código algorítmico con property tests configurados, corren con el seed configurado y verifican que las invariantes se cumplen.

**Verificaciones específicas del proyecto.** Cualquier check custom que el proyecto haya configurado (verificar que el manifest no se modificó sin justificación, verificar que no hay TODOs sin issue asociado, etc.)

flowchart LR

    PR\[PR listo para merge\] \--\> CI{CI pipeline}

    CI \--\> L\[Linter\]

    CI \--\> T\[Type checker\]

    CI \--\> I\[Import-linter\]

    CI \--\> U\[Unit tests\]

    CI \--\> Int\[Integration tests\]

    CI \--\> CT\[Contract tests\]

    CI \--\> P\[Property tests\]

    

    L \--\> All\[Todo pasa\]

    T \--\> All

    I \--\> All

    U \--\> All

    Int \--\> All

    CT \--\> All

    P \--\> All

    

    All \--\> Merge\[Merge to main\]

    

    L \-.falla.-\> Back\[Volver a etapa 3\]

    T \-.falla.-\> Back

    I \-.falla.-\> Back

    U \-.falla.-\> Back

    Int \-.falla.-\> Back

    CT \-.falla.-\> Back

    P \-.falla.-\> Back

### 9.2 La actualización del Memory Bank

Después del merge, actualizás el Memory Bank. Esto NO es trabajo busy-work; es lo que asegura que la próxima sesión arranque con contexto fresco.

**Qué actualizar.**

`activeContext.md`: agregás una entrada con la fecha, qué feature se cerró, decisiones técnicas relevantes que afectan el futuro, deuda técnica detectada (si aplica). Por ejemplo:

\#\# 2026-04-29 — Feature: parseo de fechas con offsets

Cerrada feature de parseo ISO 8601 con soporte para offsets explícitos.

Decisiones relevantes:

\- Usamos fromisoformat() de stdlib en lugar de dateutil para minimizar

  dependencias. Trade-off: en Python \<3.11 hay edge cases no cubiertos

  documentados en spec out-of-scope.

Deuda técnica detectada:

\- El parser asume strings ASCII; para soportar Unicode dates en otros

  scripts (japonés/árabe) necesitaríamos cambios. Por ahora out of scope.

Próxima feature en cola: formateo inverso (datetime → ISO string).

`progress.md`: movés la feature de "in progress" a "done", actualizás el estado general del proyecto.

**ADR si corresponde.** Si la feature involucró una decisión arquitectónica nueva que no estaba documentada, creás el ADR ahora. La regla es: si dentro de 6 meses, alguien (vos o un agente) podría preguntar "¿por qué hicimos X de esta forma?", esa decisión merece un ADR.

**Quién hace la actualización: el patrón Scribe.** Hay una tensión real acá. Por un lado, el principio dice que la actualización del Memory Bank es responsabilidad humana, porque define el contexto que la próxima sesión va a leer y delegarlo al agente sin supervisión degrada la calidad. Por otro lado, escribir desde cero la entrada de `activeContext.md` después de cada feature toma 15-20 minutos, y bajo presión de entrega es uno de los primeros pasos que el humano se salta. El resultado neto es Memory Bank desactualizado, que es peor que cualquier alternativa.

La solución que recomendamos es separar la generación del draft de la aprobación final, materializada como un sub-agente **Scribe**:

1. **El Scribe drafta.** Sub-agente con permisos read-only que recibe en su contexto: el spec aprobado de la feature, el diff completo del PR, el reporte del reviewer (etapa 4), y los archivos actuales del Memory Bank. Su tarea es producir tres outputs estructurados: una entrada propuesta para `activeContext.md`, las modificaciones propuestas para `progress.md`, y un draft de ADR si detecta que hubo decisión arquitectónica relevante (con un campo "confianza" indicando qué tan seguro está de que merece ADR).  
     
2. **Vos validás y editás.** Leés el draft. Corregís lo que el Scribe entendió mal. Agregás lo que el Scribe no podía saber (por ejemplo, contexto del cliente, decisiones de producto que se tomaron fuera del PR). Descartás el draft de ADR si la decisión no era tan arquitectónica como el Scribe creyó, o lo expandís si sí lo era.  
     
3. **Vos commiteás.** El commit final lleva tu autoría y refleja tu juicio. La marca distintiva de los commits que actualizan el Memory Bank es el prefijo `docs(memory):` para que el historial sea fácil de auditar.

**Por qué este patrón preserva el principio.** El argumento original ("si delegás esto al agente sin revisar, eventualmente pierde calidad") sigue siendo válido: el problema no era que el agente generara texto, sino que el humano dejara de revisar. El patrón Scribe explicita que la generación es asistida pero la aprobación es indelegable, igual que ya hacés en el review (etapa 4\) donde el reviewer drafta hallazgos y vos validás priorización. La fricción cae de 15-20 minutos a 3-5 minutos por feature, lo que hace mucho más probable que se haga consistentemente.

**Configuración mínima del Scribe.**

"scribe": {

  "default\_model": "claude-sonnet",  // modelo grande para síntesis

  "permissions": {

    "edit": \[\],  // read-only, solo propone

    "read": \["docs/\*\*", "src/\*\*", "tests/\*\*", ".git/\*\*"\]

  },

  "instructions": "instructions/scribe.md"

}

El prompt del Scribe en `instructions/scribe.md` es algo como:

*"Tu tarea es producir un draft del update de Memory Bank después de un PR mergeado. Recibís el spec aprobado, el diff del PR, y el reporte del reviewer. Producís tres outputs en bloques markdown separados:*

*1\. **Entrada para activeContext.md**: fecha, nombre de la feature, decisiones técnicas relevantes (con énfasis en las que afectan futuro código), deuda técnica detectada (si aplica), próxima feature en cola si la sabés.*

*2\. **Cambios para progress.md**: qué entradas mover de in-progress a done, qué actualizar.*

*3\. **Posible ADR**: si detectás una decisión arquitectónica que merece ADR, producí el draft completo con título, contexto, opciones consideradas, decisión, y consecuencias. Indicá tu confianza (alta/media/baja) de que esto realmente amerita un ADR.*

*Sé conciso. Escribí en el tono del resto del Memory Bank existente. NO inventes contexto que no esté en los inputs."*

**Variante automatizada vía CI.** Una alternativa más liviana que el sub-agente Scribe es un script de CI que extrae datos estructurados del PR (mensaje de commit, archivos modificados, hallazgos del reviewer si están en un comentario estandarizado) y genera un esqueleto de entrada que vos completás. Pierde la capacidad sintética del LLM (no te va a sintetizar "esta feature implica un cambio de approach en X"), pero gana en velocidad y predictibilidad. Funciona bien para proyectos donde las features son repetitivas.

### 9.3 Cómo gestionar esta etapa operativamente

**El merge en sí es trivial.** Si CI pasa, hacés el merge a main (idealmente con squash para tener historial limpio). El trabajo está en los pasos previos.

**La actualización del Memory Bank con Scribe toma 3-5 minutos.** Sin Scribe, toma 15-20 minutos. La diferencia es lo que hace que el paso se haga consistentemente o no se haga, lo que a su vez determina si el Memory Bank se mantiene útil o se degrada.

**Reseteá las sesiones del agente después del merge.** No reuses una sesión vieja para la próxima feature. Cada feature arranca con sesión nueva, leyendo el Memory Bank actualizado. Esto evita drift de contexto.

**Para lectores avanzados — Versionado del Memory Bank**

El Memory Bank vive en el repo, versionado con Git. Cada actualización es un commit. Esto te permite ver la evolución del proyecto, hacer `git blame` para entender por qué una decisión se tomó, y eventualmente hacer rollback si una decisión se demuestra equivocada. Una práctica útil: en commits que actualizan el Memory Bank, usar prefijo `docs(memory):` para distinguir de commits de código.

---

## 10\. Configuración de herramientas

CDAD es agnóstico del modelo de IA específico que uses, pero requiere herramientas que soporten ciertas capacidades. En este capítulo discutimos qué características buscar y configuraciones típicas.

### 10.1 Capacidades que el orquestador debe soportar

Independientemente de la herramienta concreta, el orquestador (la pieza de software con la que vos interactuás para coordinar agentes) debe soportar:

- **Sub-agentes con permisos granulares por glob patterns** (qué archivos puede leer, qué puede editar). Esto materializa el principio de sesiones aisladas.  
- **Configuración por modelo por agente** (el test-writer puede usar un modelo, el implementer otro). Esto permite usar modelos distintos para review independiente.  
- **Lectura jerárquica de instrucciones** (un `AGENTS.md` en raíz que se carga siempre, instrucciones específicas por sub-agente). Esto evita repetir contexto.  
- **Integración con Language Server Protocol** (linter, type checker en tiempo real disponible para los agentes). Esto les da feedback técnico inmediato.  
- **MCP (Model Context Protocol) o equivalente**: capacidad de conectar al agente con herramientas externas (DB queries, fetching de docs, etc.).

Herramientas que actualmente cumplen estas capacidades en distintos grados incluyen OpenCode, Claude Code, Cursor, Aider (parcialmente), entre otras. La elección entre ellas depende de tus preferencias de UI, presupuesto, y modelos disponibles. Lo importante es que **CDAD funciona con cualquier orquestador que cumpla las capacidades centrales**.

### 10.2 Configuración típica del orquestador

Independientemente de la herramienta concreta, la configuración suele tener una estructura similar:

// Pseudo-config del orquestador (sintaxis adaptada según herramienta)

{

  "providers": \[

    { "name": "anthropic", "models": \["claude-sonnet", "claude-opus"\] },

    { "name": "openai", "models": \["gpt-5"\] },

    { "name": "alibaba", "models": \["qwen3-coder", "kimi-k2"\] }

  \],

  "agents": {

    "architect": {

      "default\_model": "claude-opus",

      "permissions": {

        "edit": \[\],  // plan-only mode

        "read": \["\*\*"\]

      },

      "instructions": "instructions/architect.md"

    },

    "test-writer": {

      "default\_model": "qwen3-coder",

      "permissions": {

        "edit": \["tests/\*\*"\],

        "read": \["docs/specs/\*\*", "interfaces/\*\*", "tests/\*\*"\]

      },

      "instructions": "instructions/test-writer.md"

    },

    "implementer": {

      "default\_model": "claude-sonnet",

      "permissions": {

        "edit": \["src/\*\*", "algorithms/\*\*", "adapters/\*\*"\],

        "read": \["docs/specs/\*\*", "interfaces/\*\*", "tests/\*\*"\]

      },

      "instructions": "instructions/implementer.md"

    },

    "reviewer": {

      "default\_model": "kimi-k2",  // distinto al implementer

      "permissions": {

        "edit": \[\],  // read-only review

        "read": \["\*\*"\]

      },

      "instructions": "instructions/reviewer.md"

    }

  },

  "lsp": \["pyright", "ruff"\],

  "mcp\_servers": {

    "context7": "url-to-docs-server",

    "project-db": "url-to-db-mcp"

  }

}

### 10.3 El AGENTS.md raíz

Una pieza central de la configuración es el `AGENTS.md` en raíz del proyecto. Este archivo se carga automáticamente por todos los sub-agentes y contiene contexto que aplica al proyecto entero.

**Estructura típica.**

\# AGENTS.md — convenciones del proyecto X

\#\# Tech stack

\- Python 3.12, Postgres 16, FastAPI, SQLAlchemy

\- Tests con pytest, property tests con Hypothesis

\#\# Comandos importantes

\- \`make test\`: corre suite completa

\- \`make test-fast\`: corre solo tests unitarios

\- \`make lint\`: corre ruff \+ mypy \+ import-linter

\- \`make check\`: lint \+ tests, debe pasar antes de cada commit

\#\# Coding standards

\- Errores con clases específicas, no Exception genérico

\- Type hints completos en funciones públicas

\- Docstrings en formato Google style

\- Imports ordenados con isort

\#\# Don't touch list

\- \`migrations/\`: solo modificar mediante alembic, nunca a mano

\- \`\_\_manifest\_\_.py\`: requiere comentario \`\# AGENT-REVIEWED:\` antes de cambios

\- \`secrets/\`: nunca leer ni modificar

\#\# Boundaries arquitectónicos (enforced por import-linter)

\- \`algorithms/\` no importa de \`adapters/\`, \`models/\`, ni framework

\- \`domain/\` no importa de \`infrastructure/\`

\- \`presentation/\` puede importar de cualquier capa más profunda

\#\# Workflow de agentes

\- Antes de codear: leer \`docs/activeContext.md\`, leer spec relevante

\- TDD obligatorio: test que falla antes que código

\- Nunca usar /compact; cuando context \> 70%, hacer handoff fresco

\- Al terminar feature: actualizar \`docs/activeContext.md\` y \`docs/progress.md\`

\#\# Convenciones de commits

\- Prefijos: feat, fix, docs, refactor, test, chore

\- Mensajes en presente: "agrega validación", no "agregada validación"

\- Referencia a spec/issue cuando aplica

\#\# Cambios críticos en versión actual del framework

\[Lista de cambios entre versiones que los modelos no conocen\]

### 10.4 Configuración de herramientas QA

CDAD requiere ciertas herramientas QA configuradas. En Python típicamente:

**ruff** (linter \+ formatter) en `pyproject.toml`:

\[tool.ruff\]

line-length \= 100

target-version \= "py312"

\[tool.ruff.lint\]

select \= \["E", "F", "W", "I", "N", "UP", "B", "SIM", "RUF"\]

ignore \= \["E501"\]  \# line length manejado por formatter

**mypy** (type checker) en `pyproject.toml`:

\[tool.mypy\]

python\_version \= "3.12"

strict \= false  \# globalmente flexible

\[\[tool.mypy.overrides\]\]

module \= "interfaces.\*"

strict \= true  \# interfaces son strict

**import-linter** en `.importlinter`:

\[importlinter\]

root\_packages \= src

\[importlinter:contract:1\]

name \= algorithms-pure

type \= forbidden

source\_modules \= src.algorithms

forbidden\_modules \= src.adapters, src.models, framework

\[importlinter:contract:2\]

name \= layers

type \= layers

layers \=

    src.presentation

    src.application

    src.domain

    src.infrastructure

**pre-commit** en `.pre-commit-config.yaml`:

repos:

  \- repo: https://github.com/astral-sh/ruff-pre-commit

    rev: v0.7.0

    hooks:

      \- id: ruff

      \- id: ruff-format

  \- repo: https://github.com/pre-commit/mirrors-mypy

    rev: v1.13.0

    hooks:

      \- id: mypy

        files: ^src/interfaces/

  \- repo: local

    hooks:

      \- id: import-linter

        name: import-linter

        entry: lint-imports

        language: system

        pass\_filenames: false

### 10.5 Equivalentes en otros lenguajes

| Capacidad | Python | TypeScript | Java | Go | Rust |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Linter | ruff | eslint | checkstyle | golangci-lint | clippy |
| Type checker | mypy | tsc | (built-in) | (built-in) | (built-in) |
| Boundaries | import-linter | dependency-cruiser | ArchUnit | go-cleanarch | (manual via crates) |
| Tests | pytest | jest, vitest | JUnit | testing | cargo test |
| Property tests | hypothesis | fast-check | jqwik | rapid | proptest |
| Pre-commit | pre-commit | husky | (varios) | pre-commit | pre-commit |

---

## 11\. CDAD en frameworks opinados

Hasta acá el documento describe CDAD asumiendo arquitecturas relativamente desacopladas: módulos con responsabilidades claras, capas que se pueden enforzar con `import-linter`, contratos formales entre componentes. Eso funciona bien para servicios construidos con FastAPI, microservicios stateless, librerías puras, frontends bien estructurados. Pero gran parte del trabajo real de software ocurre dentro de **frameworks fuertemente opinados**: Odoo, Django, Rails, Webmin, WordPress, Drupal, Spring Boot, Laravel, y muchos otros. Estos frameworks imponen su propia forma de organizar el código, sus propios mecanismos de extensión, su propio ORM acoplado (cuando aplica), sus propios patrones de testing. CDAD funciona perfectamente bien adentro de estos frameworks, pero requiere algunas adaptaciones a la materialización concreta de los principios.

Este capítulo discute primero qué características de los frameworks opinados rompen las suposiciones del documento "estándar", después presenta cuatro casos de estudio en distintos frameworks y lenguajes (Odoo en Python, Django en Python, Rails en Ruby, Webmin en Perl), y cierra con una heurística general para adaptar CDAD a frameworks que el documento no cubre explícitamente. Todos los frameworks usados como ejemplo son software libre.

### 11.1 Qué se rompe y qué se mantiene

Los frameworks opinados tienen, casi por definición, las siguientes propiedades:

- **ORM acoplado al modelo de dominio.** El modelo no es una clase pura que después se mapea a la base de datos; el modelo *es* una entidad ORM que conoce la base de datos por construcción. Heredar de `models.Model` (Django, Odoo), `ApplicationRecord` (Rails) o equivalente trae automáticamente conexión a DB, validaciones, ciclo de vida, y una superficie de API enorme.  
    
- **Mecanismos de extensión ad-hoc.** En lugar de inyección de dependencias por interfaz, hay `_inherit` (Odoo), `class_eval` y monkey-patching (Rails), middleware y signals (Django), hooks y filtros (WordPress). Estos mecanismos son perfectamente válidos en su contexto, pero no se prestan a contratos verificables vía `Protocol` o `interface`.  
    
- **Convenciones implícitas que el framework asume.** Rails tiene convention over configuration; Django asume cierta organización de apps; Odoo asume cierta estructura de manifest. Saltarse las convenciones es técnicamente posible pero pelearse con el framework.  
    
- **Testing infrastructure provista por el framework.** En lugar de pytest puro, usás `TestCase` de Django con su test runner, `Minitest`/`RSpec` con fixtures de Rails, `TransactionCase`/`HttpCase` de Odoo. Estas clases traen setup/teardown, transacciones automáticas, fixtures, y patrones específicos.

**Qué cambia en CDAD ante estas propiedades.** Tres principios necesitan adaptarse:

*Principio 2 (contratos verificables).* No siempre es viable expresar contratos como `Protocol` o `interface` formal. La adaptación es expresar los contratos como **tests sobre comportamiento del modelo extendido o el endpoint expuesto**: en lugar de "todas las implementaciones de `IKnapsackSolver` cumplen postcondición X", el contrato se vuelve "todas las extensiones de `sale.order` que agregan método `confirm()` cumplen postcondición Y, verificado por test parametrizado sobre la herencia".

*Principio 3 (sesiones aisladas).* La idea se mantiene, pero los permisos por glob pattern son más finos. En Odoo, querés que el `test-writer` lea solo `models/`, `tests/`, y el manifest, pero no las views XML donde se podría inferir comportamiento. En Django, querés que lea `models.py`, `serializers.py`, `tests/`, pero no `views.py`.

*Principio 4 (TDD con Ley de Hierro).* Se mantiene literal, pero el "test que falla por la razón correcta" tiene un ritual más pesado: levantar la base de datos de test, correr migraciones, instanciar el framework. Las herramientas QA del framework (pylint-odoo, django-stubs, rubocop-rails) toman el rol que en CDAD genérico cumple `import-linter`.

**Qué se mantiene intacto.** Los otros tres principios no requieren adaptación:

- Principio 1 (spec antes que código): igual de válido, igual de necesario.  
- Principio 5 (Memory Bank persistente): igual de válido, igual de necesario; el Memory Bank de un proyecto Odoo o Django se ve idéntico al de cualquier otro proyecto.  
- Las cinco etapas del ciclo (descubrimiento, spec, TDD anti-trampa, review, merge) se aplican igual.

Y todos los anti-patrones del capítulo 12 siguen siendo anti-patrones acá.

### 11.2 Caso de estudio 1 — Odoo

Odoo es un framework ERP de Python con una arquitectura particular: todo el dominio se modela como clases que heredan de `models.Model`, con un ORM propietario, mecanismo de herencia múltiple por nombre (`_inherit`), descriptors específicos para campos, vistas declarativas en XML, sistema de permisos basado en records y grupos, y un manifest por módulo. El uso típico es construir módulos custom que extienden modelos del core o módulos OCA (Odoo Community Association).

**Qué rompe las suposiciones del documento estándar.**

- No hay manera limpia de aplicar `import-linter` ortodoxo. Los modelos importan del ORM del core constantemente; las vistas referencian modelos por string; el `self.env` es ubicuo y atraviesa todas las capas.  
- Las "interfaces" no son Python `Protocol`; son patrones de `_inherit` que extienden modelos existentes. La superficie de extensión está definida por los métodos públicos de los modelos del core.  
- Los tests usan `TransactionCase` o `HttpCase`, con setup que depende del registry de Odoo. No se pueden correr como pytest puro sin levantar el framework.  
- El manifest (`__manifest__.py`) declara dependencias entre módulos; cambios mal hechos rompen el orden de carga.

**Adaptaciones recomendadas.**

*Herramienta QA esencial: pylint-odoo (OCA).* La OCA mantiene `pylint-odoo`, un plugin de pylint con checks específicos para Odoo: detección de campos sin `string`, traducciones faltantes, `sql_constraint` mal definidos, métodos `compute` sin `@api.depends`, dependencias en manifest mal declaradas, y muchos más. **En proyectos Odoo, pylint-odoo no es opcional**: cumple el rol que `import-linter` cumple en proyectos genéricos: enforzar reglas estructurales que el agente de IA no conoce de oficio. Configuración mínima:

\# pyproject.toml

\[tool.pylint.MASTER\]

load-plugins \= \["pylint\_odoo"\]

\[tool.pylint."MESSAGES CONTROL"\]

enable \= \[

    "manifest-required-author",

    "manifest-required-key",

    "missing-readme",

    "no-write-in-compute",

    "translation-required",

    "sql-injection",

    "external-request-timeout",

    \# ... (lista completa según necesidad del proyecto)

\]

El reviewer (etapa 4\) y el CI (etapa 5\) ejecutan `pylint --load-plugins=pylint_odoo` sobre los módulos modificados como parte del pipeline obligatorio.

*Contratos verificables como tests sobre el modelo extendido.* En lugar de `Protocol`, expresás el contrato como una clase base abstracta de tests parametrizados que se ejecuta contra cualquier extensión del modelo:

\# tests/contracts/test\_sale\_order\_confirm\_contract.py

from odoo.tests.common import TransactionCase

class SaleOrderConfirmContract(TransactionCase):

    """Contrato: cualquier extensión que sobreescriba sale.order.action\_confirm()

    debe preservar estas postcondiciones.

    

    Subclases concretas: una por cada extensión que el módulo introduce.

    """

    

    def setUp(self):

        super().setUp()

        self.order \= self.\_build\_test\_order()  \# subclase puede customizar

    

    def \_build\_test\_order(self):

        \# default; las subclases pueden overridear si su extensión 

        \# requiere setup específico

        ...

    

    def test\_postcondition\_state\_changes\_to\_sale(self):

        self.order.action\_confirm()

        self.assertEqual(self.order.state, 'sale')

    

    def test\_postcondition\_invoice\_draft\_generated(self):

        self.order.action\_confirm()

        invoices \= self.order.\_get\_invoiced()

        self.assertTrue(any(inv.state \== 'draft' for inv in invoices))

    

    def test\_postcondition\_stock\_reserved(self):

        initial\_stock \= self.\_get\_total\_available\_stock()

        self.order.action\_confirm()

        self.assertLess(self.\_get\_total\_available\_stock(), initial\_stock)

Cada extensión registra una subclase concreta que activa los tests del contrato:

\# modules/custom\_sale/tests/test\_custom\_sale\_contract.py

from odoo.addons.contracts.tests.test\_sale\_order\_confirm\_contract import (

    SaleOrderConfirmContract

)

class TestCustomSaleContract(SaleOrderConfirmContract):

    """Verifica que custom\_sale.action\_confirm() respeta el contrato base."""

    \# No necesita más; hereda los tests

Cuando se agrega una nueva extensión, basta con crear su subclase y los tests del contrato se ejecutan automáticamente. Es exactamente el mismo principio de los `parametrize` en CDAD genérico, adaptado a la herencia de Odoo.

*Permisos granulares para sub-agentes.*

"odoo-test-writer": {

  "permissions": {

    "edit": \["modules/\*/tests/\*\*"\],

    "read": \[

      "docs/specs/\*\*",

      "modules/\*/models/\*\*",  // necesita ver firmas y herencia, no implementación

      "modules/\*/\_\_manifest\_\_.py",

      "modules/\*/tests/\*\*"

    \],

    "deny\_edit": \["modules/\*/models/\*\*", "modules/\*/views/\*\*", "modules/\*/data/\*\*"\]

  }

},

"odoo-implementer": {

  "permissions": {

    "edit": \["modules/\*/models/\*\*", "modules/\*/wizards/\*\*"\],

    "read": \[

      "docs/specs/\*\*",

      "modules/\*/tests/\*\*",

      "modules/\*/models/\*\*",

      "modules/\*/\_\_manifest\_\_.py"

    \],

    "deny\_edit": \["modules/\*/tests/\*\*", "modules/\*/\_\_manifest\_\_.py"\]

  }

}

Notar que el implementer tiene `deny_edit` sobre el manifest: cambios al manifest son decisiones estructurales que requieren tu aprobación explícita, no las hace el agente solo.

*Adaptaciones operativas.*

- El AGENTS.md del proyecto incluye una sección "Convenciones Odoo" con: cómo nombrar campos (`x_` para custom, `name` para descriptivos), cómo organizar módulos, cuándo usar `_inherit` vs `_inherits` vs delegation, qué métodos del core son seguros de extender y cuáles no.  
- El `docs/landscape.md` mapea la versión específica de Odoo en uso, módulos OCA instalados, customizaciones del cliente que afectan al core, y decisiones de hosting (Odoo.sh, on-premise, Docker).  
- Los tests usan `TransactionCase` por default (rollback automático) y solo `HttpCase` cuando el flujo realmente requiere HTTP (tipo controllers o widgets JS).

### 11.3 Caso de estudio 2 — Django

Django es un framework web de Python con una filosofía "batteries included": ORM propio (basado en active record con managers), sistema de apps modulares, middleware, signals, sistema de templates, admin generado automáticamente, autenticación incorporada. La curva de adopción es más suave que Odoo, pero comparte muchas de las mismas tensiones con CDAD genérico.

**Qué rompe las suposiciones.**

- Los modelos heredan de `models.Model` y traen acoplamiento con la DB por construcción. Querer un dominio puro y una capa de persistencia separada es nadar contra la corriente.  
- Las views (en sentido Django: controllers) tienen acceso directo al request, los modelos, el ORM, la session, todo. Aplicar arquitectura hexagonal estricta significa pelearse con la convención.  
- Los tests usan `django.test.TestCase` con su propio ciclo de vida (transactional rollback, fixtures, client de pruebas). Pytest puro funciona pero requiere `pytest-django`.

**Adaptaciones recomendadas.**

*Herramientas QA específicas:*

- **`django-stubs`** para mypy: agrega type hints específicos de Django (QuerySets, Managers, fields). Sin esto, mypy no detecta errores comunes como llamar a `.filter()` en algo que no es un Manager.  
- **`pylint-django`**: análogo a `pylint-odoo`. Detecta problemas específicos del framework: campos sin `verbose_name`, modelos sin `__str__`, `Meta` mal configurado.  
- **`django-test-plus`**: extiende los tests con assertions específicos (assertions de status, assertions de redirects, contextos de templates).

*Contratos verificables como tests parametrizados sobre managers o views.* Patrón análogo al de Odoo:

\# core/tests/contracts/test\_search\_manager\_contract.py

from django.test import TestCase

class SearchManagerContract:

    """Contrato: cualquier Manager que implemente .search(query) debe cumplir.

    

    Subclases concretas: una por cada modelo que tenga search.

    """

    model\_class \= None  \# subclase setea

    

    def setUp(self):

        super().setUp()

        self.searchable \= self.model\_class.objects.create(

            name="Test Item Searchable"

        )

        self.not\_searchable \= self.model\_class.objects.create(

            name="Different content"

        )

    

    def test\_search\_finds\_matching(self):

        results \= self.model\_class.objects.search("Searchable")

        self.assertIn(self.searchable, results)

    

    def test\_search\_excludes\_non\_matching(self):

        results \= self.model\_class.objects.search("Searchable")

        self.assertNotIn(self.not\_searchable, results)

    

    def test\_search\_empty\_query\_returns\_all(self):

        results \= self.model\_class.objects.search("")

        self.assertEqual(results.count(), 2\)

class ProductSearchContractTest(SearchManagerContract, TestCase):

    model\_class \= Product

class CategorySearchContractTest(SearchManagerContract, TestCase):

    model\_class \= Category

*Boundaries adaptadas.* Aunque no podés enforzar arquitectura hexagonal pura, podés enforzar reglas razonables con `import-linter` (sí, funciona en Django con cuidado):

\[importlinter\]

root\_package \= myproject

\[importlinter:contract:1\]

name \= no-cross-app-imports

type \= forbidden

source\_modules \= myproject.apps.billing

forbidden\_modules \= myproject.apps.inventory.models, myproject.apps.users.models

\# obliga a que apps se comuniquen vía services o signals, no imports directos

\[importlinter:contract:2\]

name \= views-no-orm-direct

type \= forbidden

source\_modules \= myproject.apps.\*.views

forbidden\_modules \= django.db.models

\# fuerza a que las views usen managers/services, no .filter() directo

*Permisos granulares para sub-agentes.*

"django-test-writer": {

  "permissions": {

    "edit": \["myproject/apps/\*/tests/\*\*"\],

    "read": \[

      "docs/specs/\*\*",

      "myproject/apps/\*/models.py",  // ver schema, no lógica de views

      "myproject/apps/\*/serializers.py",

      "myproject/apps/\*/tests/\*\*"

    \],

    "deny\_edit": \["myproject/apps/\*/views.py", "myproject/apps/\*/services/\*\*"\]

  }

}

### 11.4 Caso de estudio 3 — Ruby on Rails

Rails es un framework web de Ruby con la filosofía más extrema de "convention over configuration": ActiveRecord como ORM, controladores RESTful por convención, callbacks de modelo, concerns para mixins, y una cultura fuerte de metaprogramación. CDAD aplica perfectamente, pero requiere las mayores adaptaciones porque el framework abraza patrones (callbacks, monkey-patching) que en CDAD genérico evitarías.

**Qué rompe las suposiciones.**

- ActiveRecord acopla modelo y persistencia hasta el extremo. Todo el dominio "vive" en `app/models/`.  
- Callbacks (`before_save`, `after_create`) introducen lógica que se ejecuta automáticamente y que no aparece explícita en los tests si no la buscás.  
- `class_eval` y reapertura de clases hacen que la "definición de un modelo" pueda estar en cinco archivos distintos, todos cargados implícitamente.  
- Tests usan Minitest o RSpec con fixtures (estáticas) o factories (FactoryBot). Setup más rico, semántica distinta a pytest.

**Adaptaciones recomendadas.**

*Herramientas QA específicas:*

- **`rubocop-rails`**: linter con cops específicos de Rails. Detecta callbacks pesados, queries N+1, validaciones mal escritas, migraciones reversibles.  
- **`brakeman`**: análisis estático de seguridad específico de Rails. Detecta SQL injection, mass assignment vulnerabilities, command injection.  
- **`bullet`**: detecta queries N+1 en runtime durante los tests.  
- **`sorbet` o `rbs`**: type checking gradual para Ruby; equivalente conceptual a mypy.

*Contratos verificables como shared examples (RSpec) o módulos de test (Minitest).* Patrón análogo:

\# spec/contracts/billable\_contract\_spec.rb

RSpec.shared\_examples "a billable resource" do

  \# Contrato: cualquier modelo que incluye Billable concern debe cumplir

  

  it "responds to \#total\_amount" do

    expect(subject).to respond\_to(:total\_amount)

  end

  

  it "\#total\_amount is non-negative" do

    expect(subject.total\_amount).to be \>= 0

  end

  

  it "transitions to :paid when payment is recorded" do

    subject.record\_payment(amount: subject.total\_amount)

    expect(subject.payment\_state).to eq("paid")

  end

end

\# spec/models/invoice\_spec.rb

RSpec.describe Invoice do

  it\_behaves\_like "a billable resource" do

    subject { create(:invoice, :with\_lines) }

  end

end

\# spec/models/subscription\_spec.rb

RSpec.describe Subscription do

  it\_behaves\_like "a billable resource" do

    subject { create(:subscription, :active) }

  end

end

*Boundaries con packwerk.* Rails tiene su propio equivalente a `import-linter`: `packwerk` (de Shopify), que enforce boundaries entre "packages" del monolito. Es esencial cuando el proyecto crece más allá de unas pocas decenas de modelos.

*Adaptaciones operativas.*

- Los callbacks de modelo se documentan explícitamente en el spec de la feature: si una postcondición se cumple por un `after_save`, el spec debe decirlo. Esto evita que el implementer agregue un callback "invisible" que el reviewer no detecta.  
- Las migraciones siempre se hacen reversibles (`change` simétrico o `up`/`down`), enforced por `rubocop-rails`.  
- Los tests usan FactoryBot con factories explícitas; los fixtures globales se evitan porque acoplan tests que deberían ser independientes.

### 11.5 Caso de estudio 4 — Webmin

Webmin es una herramienta de administración de servidores escrita en Perl, distribuida bajo licencia BSD-like, con un sistema de módulos donde cada módulo administra un servicio del sistema (Apache, BIND, MySQL, usuarios Unix, cuotas de disco, etc.). Su arquitectura es muy distinta a los tres casos anteriores: no tiene ORM (los "datos" son archivos de configuración del sistema operativo), su mecanismo de extensión son módulos con estructura de directorios bien definida, y la mayor parte de la "lógica" son scripts CGI que renderizan HTML y manipulan archivos del sistema. El uso típico de CDAD acá aparece cuando un sysadmin o equipo construye módulos custom de Webmin para administrar servicios propios o configuraciones específicas del cliente.

**Qué rompe las suposiciones del documento estándar.**

- Perl como lenguaje principal: el ecosistema de tooling es maduro pero diferente al de Python, Ruby o Java. Las técnicas de typing estático están disponibles (`Type::Tiny`, `Moose` con type constraints) pero no son la norma cultural.  
- No hay ORM ni capa de modelo: el "dominio" son archivos de configuración (`/etc/apache2/apache2.conf`, `/etc/bind/named.conf`, etc.) que se parsean, modifican y reescriben. Las "entidades" son funciones Perl que abstraen estos archivos.  
- Mecanismo de extensión por estructura de directorios: cada módulo es un directorio con archivos `.cgi` (acciones), `*-lib.pl` (librerías compartidas), `module.info` (metadata), `config-*` (configuración por OS), y archivos de traducción en `lang/`. No hay herencia tipo `_inherit`; se extiende sobreescribiendo o agregando archivos.  
- Privilegios elevados por construcción: Webmin corre como root (o con sudo extensivo). Cualquier bug es potencialmente un riesgo de seguridad serio. Esto eleva el costo de error y, por lo tanto, la matriz observable de la sección 1.4 casi siempre puntúa alto en módulos de Webmin.

**Adaptaciones recomendadas.**

*Herramientas QA esenciales:*

- **`Perl::Critic`** con perfil estricto (`--severity 1`): linter genérico de Perl con cientos de policies. No es específico de Webmin pero es el equivalente más cercano. Permite policies custom escritas en Perl que sí pueden enforzar convenciones específicas del proyecto (ej: prohibir `system()` sin escape de argumentos, prohibir `open` sin tres argumentos, etc.).  
- **`Perl::Tidy`** para formato consistente.  
- **`Devel::Cover`** para coverage de tests.  
- **Policies custom de `Perl::Critic` para convenciones Webmin específicas.** Esto cumple el rol que `pylint-odoo` cumple en Odoo: es donde encapsulás el conocimiento del framework. Por ejemplo, una policy custom que prohíba leer archivos de configuración sin pasar por las funciones `lock_file`/`unlock_file` de la librería de Webmin (`web-lib-funcs.pl`), o que verifique que cualquier archivo `.cgi` empiece con la inicialización estándar (`require './something-lib.pl'; &init_config(); &ReadParse();`).

\# .perlcriticrc del proyecto

severity \= 1

verbose \= 8

\[Subroutines::ProhibitBuiltinHomonyms\]

\[InputOutput::ProhibitTwoArgOpen\]

\[InputOutput::RequireBriefOpen\]

\[Subroutines::RequireFinalReturn\]

\[ValuesAndExpressions::ProhibitInterpolationOfLiterals\]

\# Policies custom (en lib/Perl/Critic/Policy/Webmin/)

\[Webmin::RequireLockFileForConfig\]

\[Webmin::RequireInitConfigInCgi\]

\[Webmin::ProhibitDirectSystemCall\]

*Contratos verificables como tests parametrizados sobre archivos de configuración.* En lugar de `Protocol` o herencia, expresás el contrato como un test que verifica que cualquier función del módulo que parsea/serializa archivos de configuración respeta el round-trip:

\# t/contracts/config\_roundtrip.t

use strict;

use warnings;

use Test::More;

use File::Temp qw(tempfile);

\# Cualquier módulo que parsea config files debe registrar su par

\# (parser, serializer) en este array

my @config\_handlers \= (

    {

        name      \=\> 'apache\_vhost',

        parser    \=\> \\\&apache::parse\_vhost,

        serializer \=\> \\\&apache::serialize\_vhost,

        sample    \=\> "t/fixtures/apache\_vhost\_sample.conf",

    },

    {

        name      \=\> 'bind\_zone',

        parser    \=\> \\\&bind8::parse\_zone,

        serializer \=\> \\\&bind8::serialize\_zone,

        sample    \=\> "t/fixtures/bind\_zone\_sample.conf",

    },

    \# ... agregás handlers a medida que aparecen módulos

);

for my $handler (@config\_handlers) {

    subtest "round-trip for $handler-\>{name}" \=\> sub {

        my $original \= read\_file($handler-\>{sample});

        my $parsed \= $handler-\>{parser}-\>($original);

        my $serialized \= $handler-\>{serializer}-\>($parsed);

        my $reparsed \= $handler-\>{parser}-\>($serialized);

        is\_deeply($parsed, $reparsed,

            "parse(serialize(parse(x))) \== parse(x) for $handler-\>{name}");

    };

}

done\_testing();

Cuando se agrega un nuevo módulo que maneja un nuevo formato de config, registrás el handler en el array y los tests del contrato se ejecutan automáticamente. Es el mismo principio que viste en los otros casos, adaptado a la idiosincrasia Perl/Webmin.

*Permisos granulares para sub-agentes.*

"webmin-test-writer": {

  "permissions": {

    "edit": \["modules/\*/t/\*\*", "modules/\*/tests/\*\*"\],

    "read": \[

      "docs/specs/\*\*",

      "modules/\*/\*-lib.pl",  // ver firmas de librerías, no implementación

      "modules/\*/module.info",

      "modules/\*/t/\*\*",

      "t/fixtures/\*\*"

    \],

    "deny\_edit": \[

      "modules/\*/\*.cgi",

      "modules/\*/\*-lib.pl",

      "modules/\*/module.info",

      "modules/\*/config-\*"

    \]

  }

},

"webmin-implementer": {

  "permissions": {

    "edit": \[

      "modules/\*/\*.cgi",

      "modules/\*/\*-lib.pl",

      "modules/\*/lang/\*\*"

    \],

    "read": \[

      "docs/specs/\*\*",

      "modules/\*/t/\*\*",

      "modules/\*/\*-lib.pl",

      "modules/\*/module.info"

    \],

    "deny\_edit": \[

      "modules/\*/t/\*\*",

      "modules/\*/module.info",

      "modules/\*/config-\*"

    \]

  }

}

Como en Odoo el manifest, acá `module.info` y los archivos `config-*` (configuración por sistema operativo) son decisiones estructurales que requieren tu aprobación: el implementer no las toca solo.

*Adaptaciones operativas específicas.*

- **Tests de seguridad como ciudadanos de primera clase.** Dado que Webmin corre con privilegios elevados, cada módulo nuevo o modificado debe tener al menos un test que verifique: (a) que las inputs del usuario se escapan antes de pasar a `system()` o construir comandos shell, (b) que se respeta el sistema de ACLs de Webmin (`&foreign_available()` y `&can_access_*()`), (c) que se usa `&lock_file()` antes de modificar archivos del sistema.  
- **El AGENTS.md del proyecto** incluye una sección "Convenciones Webmin" con: cómo nombrar funciones (`module_name::function_name`), uso obligatorio de `&error()` para terminar con error, uso de `ui_*` para generar HTML (no inline), patrón de internacionalización con `&text()` y archivos `lang/`.  
- **El `docs/landscape.md`** mapea la versión específica de Webmin en uso (las API de `web-lib-funcs.pl` cambian entre majors), módulos del core de los que dependés, y el sistema operativo target (las funciones de manipulación de servicios cambian entre Debian/RedHat/BSD).  
- **Spec con foco en idempotencia.** Las operaciones de un módulo Webmin típicamente modifican estado del sistema operativo. Los specs deben explicitar la postcondición de idempotencia ("ejecutar la acción dos veces produce el mismo estado final que ejecutarla una vez"), y los tests deben verificarla.

**Nota: por qué Webmin es un caso particularmente claro de la matriz de la sección 1.4.**

Casi cualquier feature de un módulo Webmin puntúa alto en los tres ejes: vida útil larga (los módulos se mantienen años), costo de bug alto (privilegios root), probabilidad de evolución alta (los servicios que administra evolucionan). Es prácticamente siempre territorio de "CDAD completo" según la matriz. Esto hace de Webmin un buen recordatorio de que la matriz no es solo para decidir si bajar el rigor; también confirma cuándo aplicarlo en su totalidad.

### 11.6 Heurística general para frameworks no cubiertos

Si trabajás con un framework libre que el documento no cubre explícitamente (Spring Boot, Laravel, WordPress, Drupal, Plone, NestJS, ASP.NET Core con Mono, etc.), la heurística para adaptar CDAD es la siguiente:

1. **Identificá el linter específico del framework.** Casi todos los frameworks opinados tienen una herramienta análoga a `pylint-odoo`/`pylint-django`/`rubocop-rails`/policies custom de `Perl::Critic`. Para Spring Boot: `spring-javaformat` \+ `archunit`. Para Laravel: `larastan` \+ `php-cs-fixer` con preset Laravel. Para WordPress: `phpcs` con `WordPress-Coding-Standards`. Para Drupal: `drupal-check` \+ reglas de PHPStan específicas. Para Plone: `plone.recipe.codeanalysis`. Esta herramienta cumple el rol de `import-linter` en CDAD genérico: es no opcional.  
     
2. **Identificá el mecanismo de extensión nativo del framework.** En Odoo es `_inherit`, en Rails son concerns y callbacks, en Django son signals y middleware, en Webmin es estructura de directorios \+ librerías compartidas, en Spring son `@Configuration` y AOP, en WordPress son hooks/filters, en Drupal son hooks. El "contrato verificable" se materializa como tests parametrizados sobre extensiones de ese mecanismo, no como `Protocol` formal.  
     
3. **Identificá las clases base de testing del framework.** TransactionCase/HttpCase en Odoo, TestCase de Django, ActiveSupport::TestCase en Rails, Test::More \+ módulos del proyecto en Webmin/Perl, `@SpringBootTest` en Spring, `TestCase` con `RefreshDatabase` en Laravel, `WP_UnitTestCase` en WordPress. Tus tests heredan de esas clases o usan esos módulos, no son tests "puros" del lenguaje.  
     
4. **Adaptá los permisos de sub-agentes a la estructura del framework.** Las separaciones que cumplen el principio "test-writer no ve implementación" se materializan según el framework. En Spring: `test-writer` ve interfaces y `@Service` signatures pero no `@Service` bodies. En Laravel: ve `App\Models` y signatures de `App\Services` pero no `app/Services/*` bodies. En WordPress: ve declaraciones de hooks (`add_action`/`add_filter`) registradas pero no las callbacks que implementan la lógica.  
     
5. **Mantené los principios intactos.** Spec antes que código, sesiones aisladas, TDD con Ley de Hierro, Memory Bank persistente, review en dos capas, ciclo de cinco etapas. Lo que se adapta es siempre la materialización técnica, nunca el principio.

**Para lectores avanzados — Cuando el framework imposibilita un principio**

Hay casos donde un principio de CDAD genuinamente no se puede aplicar de manera completa. Ejemplo común en software libre: en plataformas como Drupal con su sistema de configuración exportable (`config/sync/`), o en WordPress con el Customizer y los Block Patterns visuales, gran parte de la "lógica" de presentación y workflow no es código sino configuración declarativa serializada en YAML, JSON o entradas de base de datos. No hay manera limpia de aplicar TDD sobre esa configuración como si fuera código. La respuesta correcta no es abandonar CDAD; es aplicarlo donde el framework lo permite (custom modules, hooks, services, código PHP/Python/Perl) y aceptar que la parte declarativa requiere otras técnicas: testing manual estructurado con scripts de regresión, change sets revisados por pares, sandboxes con datos de regresión que se replayean automáticamente. El documento prefiere este pragmatismo a un purismo que no es aplicable. Lo importante es no usar la existencia de partes declarativas como excusa para relajar CDAD en las partes que sí son código.

**Quiz de autoevaluación**

1. ¿Por qué `pylint-odoo` (o el equivalente del framework que uses) es no opcional en proyectos sobre frameworks opinados?  
2. ¿Cómo se materializa un contrato verificable en Rails sin tener `Protocol` o `interface` formal?  
3. ¿Qué principios de CDAD se mantienen intactos al pasar a un framework opinado, y cuáles requieren adaptación?

Ver respuestas 

1. Porque cumple el rol que `import-linter` cumple en proyectos genéricos: enforzar automáticamente reglas estructurales del framework que el agente de IA no conoce de oficio (campos sin string, traducciones faltantes, queries inseguras, manifest mal definido, etc.). Sin esa herramienta, el principio de "barreras estructurales que no requieren atención humana" se debilita: muchas reglas del framework quedan dependiendo del juicio del reviewer, que se cansa y se le escapan.  
     
2. Mediante `shared examples` en RSpec o módulos de test compartidos en Minitest. Definís un set de tests parametrizados que verifican postcondiciones sobre cualquier modelo o resource que cumple el contrato; cada implementación concreta hereda esos tests con un setup específico. Es el mismo principio que `parametrize` en pytest, adaptado al ecosistema Ruby.  
     
3. Se mantienen intactos: spec antes que código (principio 1), Memory Bank persistente (principio 5), las cinco etapas del ciclo, todos los anti-patrones documentados. Requieren adaptación: contratos verificables (principio 2, se materializa con tests parametrizados sobre el mecanismo de extensión del framework), sesiones aisladas (principio 3, los permisos por glob se ajustan a la estructura del framework), TDD con Ley de Hierro (principio 4, se mantiene literal pero el ritual del "test que falla por razón correcta" es más pesado por el setup del framework).

---

## 12\. Anti-patrones documentados

Los anti-patrones son tan importantes como los patrones. En este capítulo documentamos los errores más comunes que hemos visto al adoptar CDAD, con el "antes" (qué hace mal) y el "después" (cómo se hace correcto).

### 12.1 Anti-patrón: "una sesión para todo"

**Síntoma.** El developer (vos) abre una sola sesión con el agente y le pide "implementá la feature X completa, con tests". El agente escribe el spec mentalmente, escribe los tests, escribe el código, todo en la misma conversación.

**Por qué es problemático.** El agente ve test e implementación al mismo tiempo. Naturalmente los alinea entre sí. Los tests resultantes verifican lo que el código hace, no lo que el spec pide. Si hay un bug en el código, el test no lo detecta porque fue escrito para el código.

**Cómo se hace bien.** Sesiones separadas: una para el spec, una para el test-writer, una para el implementer. Cambia de contexto, te tarda más, y produce calidad muy superior.

### 12.2 Anti-patrón: "el test que siempre pasa"

**Síntoma.** El test-writer escribe un test que pasa antes de que la implementación exista. Eso debería levantar una alarma, pero en la prisa, se da por bueno.

\# ANTI-PATRÓN

def test\_parse\_iso\_date():

    result \= parse\_iso\_date("2026-04-29T15:30:00Z")

    assert result is not None  \# esto pasa con cualquier implementación

**Por qué es problemático.** El test no verifica nada concreto. `assert result is not None` pasa con cualquier implementación que retorne algo distinto de `None`, incluso una incorrecta.

**Cómo se hace bien.**

def test\_parse\_iso\_date():

    result \= parse\_iso\_date("2026-04-29T15:30:00Z")

    expected \= datetime(2026, 4, 29, 15, 30, 0, tzinfo=timezone.utc)

    assert result \== expected

El test compara con un valor esperado específico. Si el código devuelve algo distinto, falla con mensaje claro de qué esperaba y qué obtuvo.

### 12.3 Anti-patrón: "implementar más de lo que el test pide"

**Síntoma.** El test verifica el caso de un solo elemento, pero el implementer ya escribe código que maneja listas, edge cases, validaciones extras, optimizaciones. Por las dudas.

**Por qué es problemático.** El código no está cubierto por tests. Si un bug está en la parte "extra", nadie lo va a detectar. Además, agrega complejidad que probablemente no se necesita (YAGNI).

**Cómo se hace bien.** El implementer escribe el mínimo código que hace pasar el test. La funcionalidad adicional llega cuando llega el test que la verifica. Esto se llama "incremental development" en TDD clásico y es disciplina central.

### 12.4 Anti-patrón: "el reviewer solo lee el código"

**Síntoma.** El reviewer recibe el diff y lo evalúa por sus méritos técnicos (es elegante, sigue convenciones, etc.) sin contrastarlo contra el spec.

**Por qué es problemático.** El código puede estar técnicamente impecable y aun así no resolver el problema correcto. La función principal del reviewer es verificar que el código satisface el spec, no que sea lindo.

**Cómo se hace bien.** El reviewer recibe explícitamente el spec en su contexto y se le pide que reporte divergencias del spec como categoría primaria. Sin el spec, el review pierde gran parte de su valor.

### 12.5 Anti-patrón: "skip Memory Bank because the agent already knows"

**Síntoma.** Después de varias sesiones productivas con un agente en el mismo proyecto, el developer asume que el agente "ya sabe" el contexto y deja de actualizar el Memory Bank.

**Por qué es problemático.** Los agentes no tienen memoria entre sesiones. Lo que sabía la sesión de ayer se perdió. La próxima sesión arranca de cero. Sin Memory Bank actualizado, el agente reinventa la rueda o asume cosas incorrectas.

**Cómo se hace bien.** Después de cada feature, actualizás `activeContext.md` con las decisiones relevantes. Este trabajo de consolidación de 10-20 minutos paga enormes dividendos en sesiones futuras.

### 12.6 Anti-patrón: "el spec se ajusta para que el código compile"

**Síntoma.** En medio de la implementación, el agente encuentra un caso que el spec no contempla. En lugar de pausar, volver al spec, y actualizarlo, el agente "interpreta libremente" el spec para que su implementación tenga sentido.

**Por qué es problemático.** El spec deja de ser fuente de verdad. La próxima vez que alguien lea el spec, va a entender algo distinto de lo que el código hace. La consistencia entre spec y código se rompe.

**Cómo se hace bien.** Cuando aparece un caso no contemplado, el implementer pausa, vos volvés al spec, lo actualizás explícitamente, commiteás el cambio del spec, y recién entonces seguís con la implementación. Toma 10 minutos pero mantiene la consistencia.

### 12.7 Anti-patrón: "review optional para features pequeñas"

**Síntoma.** Para features pequeñas (un fix de un campo, un cambio de configuración), saltarse el review "porque es trivial".

**Por qué es problemático.** Las features triviales son las que menos atención tienen y donde se cuelan más bugs. El costo de review es bajo (un agente reviewer puede revisar 30 líneas en segundos). El beneficio de detectar inconsistencias es alto.

**Cómo se hace bien.** El review siempre se hace, pero su profundidad es proporcional a la complejidad. Para features triviales, el reviewer solo verifica que no hay regresión, que el spec se cumple, y que no hay riesgos de seguridad. Esto toma poco tiempo.

**Caso de estudio: optimización de pricing**

Imaginá una feature: "calcular precio final aplicando descuentos por cantidad y descuentos por categoría de cliente, con reglas de prioridad."

Anti-patrón: "es solo un cálculo", el developer abre una sesión, le pide al agente "implementá pricing con descuentos", el agente escribe spec mentalmente, código, y un test rápido. Funciona. Lo merge.

Tres semanas después, contabilidad detecta que para clientes corporativos con pedidos grandes, el descuento se está aplicando dos veces. El bug entró porque el "test rápido" verificaba el caso simple (un cliente, una compra), no el caso compuesto.

Con CDAD: en el spec, el brainstorm habría preguntado: "¿qué pasa si un cliente califica para descuento por cantidad Y descuento por categoría?". La respuesta hubiera sido "se aplica el mayor de los dos, no la suma". Esa postcondición se hubiera convertido en test específico. El agente implementer no podría haber acumulado descuentos sin romper el test.

**Quiz de autoevaluación**

1. Si un test pasa antes de escribir la implementación, ¿qué tres cosas pueden estar mal?  
2. ¿Por qué el implementer no debe agregar funcionalidad que el test no requiere?  
3. ¿Qué hacés si en plena etapa 3 descubrís que el spec no contempla un caso?

Ver respuestas 

1. (a) El test no verifica lo que dice verificar (es trivial, como `assert result is not None`); (b) la funcionalidad ya existía y no era una feature nueva genuina; (c) el test tiene un bug que lo hace siempre pasar (ej: condicional invertido).  
     
2. Por dos razones: (a) la funcionalidad extra no está cubierta por tests, así que bugs ahí no se detectan; (b) agrega complejidad que probablemente no se necesita (YAGNI: You Aren't Gonna Need It). La funcionalidad debe llegar cuando llegue el test que la verifica.  
     
3. Pausás la implementación. Volvés al spec en la etapa 2, lo actualizás para cubrir el caso, lo commiteás explícitamente, y recién entonces volvés a la etapa 3 con el spec actualizado. La consistencia entre spec y código es invariante; nunca lo rompas por velocidad.

---

## 13\. Referencia rápida y glosario

### 13.1 Cheatsheet del ciclo

┌─────────────────────────────────────────────────────────────────┐

│                     CDAD — Cheatsheet del ciclo                 │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│  0\. DECISIÓN                                                    │

│     □ Puntuar la tarea (3-9) en matriz observable               │

│     □ 3-4 → vibe coding;  5-6 → CDAD light;  7-9 → completo     │

│                                                                 │

│  1\. DESCUBRIMIENTO                                              │

│     □ Mapear APIs/hooks relevantes                              │

│     □ Documentar en docs/landscape.md                           │

│                                                                 │

│  2\. SPEC                                                        │

│     □ Brainstorm socrático con architect                        │

│     □ Redactar docs/specs/NNN-feature/spec.md                   │

│     □ Postcondiciones explícitas \+ criterios de aceptación      │

│     □ Aprobación humana obligatoria                             │

│                                                                 │

│  3\. TDD ANTI-TRAMPA                                             │

│     □ Identificar postcondiciones ortogonales para agrupar      │

│     □ Sesión 1 (test-writer): test falla                        │

│     □ Verificar fallo por razón correcta                        │

│     □ Sesión 2 (implementer): código mínimo, test pasa          │

│     □ Sesión 3 (refactorer): mejorar manteniendo verde          │

│     □ Sesión 4 (test-writer): property tests si aplica          │

│     □ Sesión 5 (test-writer): tests E2E desde criterios accept. │

│                                                                 │

│  4\. REVIEW TWO-LAYER                                            │

│     □ Sesión reviewer (modelo distinto al implementer)          │

│     □ Reporte priorizado: bloqueantes / opcionales              │

│     □ Validación humana de la priorización                      │

│     □ Si hay bloqueantes: volver a etapa 3                      │

│                                                                 │

│  5\. MERGE \+ MEMORY BANK                                         │

│     □ CI completo pasa: lint, types, imports, tests, contracts  │

│     □ Merge a main                                              │

│     □ Sesión Scribe: drafta update de Memory Bank               │

│     □ Validar/editar y commitear con prefijo docs(memory):      │

│     □ Crear ADR si hubo decisión arquitectónica                 │

│                                                                 │

└─────────────────────────────────────────────────────────────────┘

### 13.2 Checklist antes de cada feature

Antes de arrancar una feature, verificá:

- [ ] El Memory Bank está actualizado al estado actual (última feature reflejada)  
- [ ] Las herramientas QA están configuradas y pasando en main  
- [ ] El AGENTS.md raíz está al día con convenciones actuales  
- [ ] Los sub-agentes están configurados con sus permisos correctos  
- [ ] El landscape.md cubre el área de código que vas a tocar (si no, descubrimiento por feature)

### 13.3 Checklist al terminar una feature

Antes de cerrar la feature como done:

- [ ] Todos los tests pasan localmente y en CI  
- [ ] El review se hizo y los bloqueantes se resolvieron  
- [ ] El spec aprobado está en el repo y refleja lo implementado  
- [ ] `docs/activeContext.md` se actualizó con la entrada de la feature  
- [ ] `docs/progress.md` refleja el nuevo estado  
- [ ] Si hubo decisión arquitectónica, hay ADR creado  
- [ ] El branch está mergeado y el PR cerrado  
- [ ] Las sesiones de agente activas se cerraron (no reusar para próxima feature)

### 13.4 Glosario

**ADR (Architecture Decision Record).** Documento que captura una decisión arquitectónica, su contexto, alternativas consideradas, decisión tomada, y consecuencias. Inmutable una vez aceptado; si la decisión se revisa, se crea un ADR nuevo que supersede al anterior.

**Anti-trampa (TDD).** Variante de TDD donde la separación entre quien escribe el test y quien escribe el código es estructural (sub-agentes con permisos limitados), no solo disciplinaria. Diseñada para mitigar la tendencia de los modelos LLM a alinear test e implementación.

**Boundaries arquitectónicos.** Reglas sobre qué módulos pueden importar de cuáles. Enforceadas automáticamente por herramientas como import-linter (Python), dependency-cruiser (TypeScript), ArchUnit (Java), packwerk (Rails). En frameworks opinados, frecuentemente se delegan a herramientas QA específicas (pylint-odoo, pylint-django, rubocop-rails).

**Brainstorm socrático.** Conversación con un agente architect en modo plan-only donde el agente formula preguntas para clarificar la feature antes de escribir el spec. Análogo al método socrático filosófico, adaptado a desarrollo de software.

**CDAD (Contract-Driven AI Development).** La metodología que este documento describe.

**CDAD light.** Variante reducida de CDAD para tareas que puntúan 5-6 en la matriz observable de activación: spec breve, TDD con sesiones aisladas para componentes críticos, review opcional, Memory Bank si el proyecto ya lo tiene.

**Contract test.** Test parametrizado que verifica las postcondiciones de un Protocol/interface contra todas sus implementaciones registradas. Cuando se agrega una nueva implementación, automáticamente queda cubierta sin tests adicionales. En frameworks opinados, se materializa con `shared examples` (RSpec), módulos de test compartidos (Minitest), o clases base de TestCase parametrizadas (Odoo, Django).

**E2E modalidad outside-in.** Modalidad de tests E2E donde el test del flujo completo se escribe primero (antes de los unit tests) y queda rojo durante todo el ciclo de implementación, hasta que las piezas individuales se conectan. Da una métrica continua de progreso de la feature.

**E2E modalidad cierre.** Modalidad de tests E2E donde el test del flujo se escribe después de que las unidades están verdes, como verificación final de ensamblaje correcto antes del merge. Más simple operativamente; pierde la métrica continua.

**Frameworks opinados.** Frameworks que imponen una forma específica de organizar el código, mecanismos de extensión propios, ORM acoplado al modelo (cuando aplica), y testing infrastructure provista. Ejemplos: Odoo, Django, Rails, Webmin, WordPress, Drupal, Spring Boot, Laravel. CDAD aplica con adaptaciones puntuales (capítulo 11).

**Hosting-agnostic.** Propiedad de un módulo de software de funcionar en distintos entornos de hosting sin depender de convenciones específicas de uno. Importante en proyectos donde el código se va a distribuir a clientes con setups diversos.

**Implementer.** Sub-agente con permisos de edit en código de implementación, sin permisos en tests. Su tarea es hacer pasar los tests existentes con código mínimo.

**Import-linter.** Herramienta de Python que enforce contratos sobre imports (qué módulo puede importar de cuál). Equivalentes existen en otros lenguajes con nombres distintos.

**Ley de Hierro (TDD).** Regla absoluta: nunca escribir código de implementación sin antes tener un test que falla por la razón correcta. Sin excepciones, sin atajos.

**Matriz observable de activación.** Herramienta de decisión (sección 1.4) que puntúa una tarea en tres ejes (vida útil, costo de bug, probabilidad de evolución) y sugiere el nivel de CDAD a aplicar: vibe coding, light, o completo.

**Memory Bank.** Conjunto de archivos versionados (`projectbrief.md`, `activeContext.md`, `progress.md`, `adr/*`, `specs/*`) que capturan el estado del proyecto y se cargan al inicio de cada sesión de agente.

**Postcondiciones ortogonales.** Postcondiciones que se implementan en paths de código independientes, sin pisarse entre sí. Pueden agruparse en un mismo ciclo RED-GREEN-REFACTOR para acelerar el desarrollo sin perder la red de seguridad. Contraste con postcondiciones acopladas, que requieren ciclos separados.

**Property test.** Test que verifica una propiedad general (invariante) sobre todos los inputs válidos, generando inputs aleatorios automáticamente. Detecta edge cases que tests determinísticos pueden no encontrar.

**Protocol (Python).** Mecanismo de typing estructural que define una interfaz por el conjunto de métodos que una clase tiene, sin requerir herencia explícita. Permite contratos verificables. Equivalentes: TypeScript `interface` con `satisfies`, Java `interface`, Go `interface`, Rust `trait`.

**pylint-odoo.** Plugin de pylint mantenido por la OCA (Odoo Community Association) con checks específicos para Odoo. En proyectos Odoo cumple el rol que `import-linter` cumple en proyectos genéricos: enforzar reglas estructurales que el agente de IA no conoce de oficio.

**Refactorer.** Sub-agente cuya tarea es mejorar código existente (legibilidad, consistencia, simplicidad) sin cambiar comportamiento observable. Todos los tests deben seguir pasando después del refactor.

**Reviewer.** Sub-agente con permisos read-only que evalúa un diff completo contra el spec y produce un reporte priorizado de hallazgos. Idealmente usa un modelo distinto al implementer.

**Scribe.** Sub-agente con permisos read-only cuya tarea es draftar la actualización del Memory Bank después de un PR mergeado: entrada propuesta para `activeContext.md`, cambios para `progress.md`, y posible draft de ADR. El humano valida y commitea. Reduce la fricción del Memory Bank update de 15-20 minutos a 3-5 minutos por feature.

**Sesión aislada.** Conversación con un agente que NO comparte contexto con otras sesiones. Usada en CDAD para forzar separación de fases (test-writer no ve código, implementer no ve razonamiento del test-writer).

**Sub-agente.** Configuración de un agente con permisos específicos (qué archivos puede leer/editar), instrucciones específicas, y eventualmente modelo específico. Permite materializar el principio de sesiones aisladas.

**Test-writer.** Sub-agente con permisos de edit solo en `tests/`, sin permisos en código de implementación. Su tarea es escribir tests que verifican el spec y fallan inicialmente porque no hay implementación.

**Vibe coding.** Patrón anti-CDAD donde se le pide al agente "implementá X" sin spec previo, sin separación de fases, sin contratos verificables. Funciona para tareas chicas pero no produce calidad sostenible para proyectos serios.

### 13.5 Recursos para profundizar

**TDD clásico.**

- Kent Beck — *Test-Driven Development by Example* (libro fundacional)  
- James Shore — *The Art of Agile Development* (capítulo sobre TDD práctico)

**Domain-Driven Design (complementario a CDAD).**

- Eric Evans — *Domain-Driven Design* (libro fundacional)  
- Vaughn Vernon — *Implementing Domain-Driven Design* (más práctico)

**Property-based testing.**

- David MacIver — documentación de Hypothesis (Python)  
- Scott Wlaschin — *Domain Modeling Made Functional* (incluye PBT en F\#)

**Clean Architecture y boundaries.**

- Robert Martin — *Clean Architecture* (capítulos sobre layers y boundaries)  
- Vladimir Khorikov — *Unit Testing Principles, Practices, and Patterns*

**Architecture Decision Records.**

- Michael Nygard — artículo original sobre ADRs (2011)  
- adr.github.io — patrón consolidado y plantillas

**Trabajo con agentes de IA.**

- Anthropic — guías de prompt engineering y trabajo con Claude  
- Documentación de herramientas: Claude Code, OpenCode, Cursor, Aider

---

## Cierre

CDAD nace de una observación pragmática: los agentes de IA son útiles pero impredecibles, y la única manera de obtener calidad sostenible al trabajar con ellos es introducir disciplina estructural que no dependa de la consistencia del modelo subyacente. Los cinco principios fundacionales (spec antes que código, contratos verificables, sesiones aisladas con permisos granulares, TDD con Ley de Hierro, Memory Bank persistente) se materializan en un ciclo de cinco etapas (descubrimiento, especificación, TDD anti-trampa, review two-layer, merge con Memory Bank) que se aplica feature por feature.

La disciplina inicial es real: configurar herramientas, escribir specs, separar sesiones, mantener Memory Bank. Pero la disciplina paga dividendos crecientes a medida que el proyecto avanza: las features futuras son más rápidas porque el contexto está consolidado, los bugs son más raros porque las barreras estructurales los detectan temprano, los cambios de scope son más manejables porque el spec es la fuente de verdad. La curva de aprendizaje es de algunos días para los conceptos y algunas semanas para que el ciclo se sienta natural.

El documento que estás leyendo es la versión 1.0 de CDAD. La metodología va a evolucionar con la experiencia y con la evolución de las herramientas. Los principios fundacionales son robustos, pero la materialización concreta (qué herramientas, qué patrones específicos) se va a refinar. Si la usás y descubrís mejoras, vale documentarlas y compartirlas.

Buena suerte con tu próximo proyecto.

---

**Sobre la versión.** Documento v1.1, redactado en abril de 2026\. Revisión 1.1 incorpora: matriz observable de activación de CDAD (1.4), variantes de fallback manual cuando el orquestador no soporta permisos granulares (2.3), agrupación de postcondiciones ortogonales (7.1), sub-fase explícita de tests de integración / E2E (7.6), patrón Scribe para asistir la actualización del Memory Bank (9.2), y capítulo nuevo sobre adaptación de CDAD a frameworks opinados con casos de estudio en Odoo (Python), Django (Python), Rails (Ruby) y Webmin (Perl) (capítulo 11). Todos los ejemplos del documento corresponden a software libre.  
