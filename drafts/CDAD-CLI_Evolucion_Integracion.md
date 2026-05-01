# CDAD × OpenCode v2: Evolución de la Integración Metodológica

**Propuesta para agnósticismo de frameworks, automatización CLI multi-editor, y patrones escalables**

> **Nota importante**: Este documento propone una **evolución v2 de la integración**, no un refactor de CDAD. Estamos definiendo cómo evolucionan la metodología CDAD y su integración con OpenCode para ser más agnósticas, automatizadas y escalables.

---

## 📋 Resumen Ejecutivo

### El problema actual

El documento "CDAD × OpenCode — Estrategia de Implementación" (v1) define bien cómo usar CDAD en OpenCode, pero:

1. **Acoplamiento a Odoo**: Ejemplos y preset están muy específicos a Odoo
2. **Falta de multi-editor**: Solo OpenCode, no Zed/Claude Code/Qwen Coder
3. **Sin automatización de setup**: Usuario configura manualmente
4. **Escalabilidad limitada**: Cubre bien "feature", no "epic" o "sistema" completo
5. **Metodología incompleta**: No define patrones para diferentes escalas

### La solución v2

```
┌──────────────────────────────────────────────────┐
│           CDAD × OpenCode v2                     │
├──────────────────────────────────────────────────┤
│                                                  │
│ 1. Agnósticismo de frameworks                   │
│    ├─ cdad-core (agnóstico puro)                │
│    └─ cdad-preset-{framework} (especializaciones)│
│                                                  │
│ 2. CLI universal multi-editor                   │
│    ├─ OpenCode (wrapper sobre CLI)              │
│    ├─ VS Code (wrapper sobre CLI)               │
│    ├─ Zed (wrapper sobre CLI)                   │
│    └─ Terminal pura (CLI directa)               │
│                                                  │
│ 3. Patrones de escalabilidad                    │
│    ├─ Micro (1-2h, CDAD light)                  │
│    ├─ Feature (2-4d, CDAD estándar)             │
│    ├─ Epic (3-4w, CDAD + diseño)                │
│    └─ Sistema (8-12w, CDAD + gobernanza)        │
│                                                  │
│ 4. Arquitectura en 4 niveles (framework Qwen)   │
│    ├─ Orquestación (CLI)                        │
│    ├─ Aplicación (Core + Adapters)              │
│    ├─ Metodología (Specs + Scripts)             │
│    └─ Entorno (Editor + Sandbox)                │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 1. Agnósticismo de frameworks: Arquitectura Core + Presets

### 1.1 Principio fundamental

**Separación clara**: La metodología CDAD y la infraestructura de OpenCode son agnósticas. Los detalles específicos de cada framework (Odoo, Django, Rails) van en presets desacoplados.

```
┌─────────────────────────────────────────────────────────┐
│  CDAD Core (agnóstico, reusable en cualquier framework)│
├─────────────────────────────────────────────────────────┤
│ • Especificaciones (spec con contratos)                 │
│ • Tests (RED/GREEN/REVIEW ciclo)                        │
│ • Memory Bank (projectbrief, activeContext, ADRs)       │
│ • Agentes (architect, test-writer, implementer, reviewer)│
│ • Comandos slash (agnósticos)                           │
│ • Plugin state machine (agnóstico)                      │
└─────────────────────────────────────────────────────────┘
                          △
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▽                 ▽                 ▽
    ┌────────┐       ┌────────┐       ┌────────┐
    │ Preset │       │ Preset │       │ Preset │
    │ Odoo   │       │ Django │       │ Rails  │
    └────────┘       └────────┘       └────────┘
    • Docker-compose • pytest-django  • Rails generators
    • pylint-odoo    • Django test    • RSpec patterns
    • _inherit       • ORM patterns    • ActiveRecord
    • módulos        • Celery tasks    • Migrations
```

### 1.2 Estructura de distribución

```
cdad-core/                          [package principal, agnóstico]
├── .opencode/
│   ├── agents/                     [arquitecto, test-writer, implementer, reviewer, scribe]
│   ├── commands/                   [discover, spec, red, green, review, merge-check, matrix]
│   └── plugin/                     [state machine, agnóstico]
├── docs/
│   ├── specs/                      [plantillas agnósticas]
│   ├── adr/                        [plantillas agnósticas]
│   ├── patterns/                   [escalabilidad: micro, feature, epic, sistema]
│   └── .cdad-state.json            [state agnóstico]
├── scripts/
│   └── cdad/                       [detect-stage, run-tests, validate-spec, etc. agnósticos]
├── tests/                          [estructura agnóstica]
└── copier.yml                      [templating agnóstico]

cdad-cli/                           [CLI universal, agnóstica]
├── src/
│   ├── commands/                   [init, status, discover, spec, red, green, review, merge-check]
│   ├── lib/
│   │   ├── stage-detector.ts
│   │   ├── framework-detector.ts   [detecta framework automáticamente]
│   │   └── ...
│   └── types/
├── package.json
└── README.md

cdad-preset-odoo/                   [especialización Odoo, separada]
├── preset-files/
│   ├── docker-compose.yml
│   ├── scripts/framework/
│   │   ├── test-runner-odoo.sh
│   │   └── odoo-lint.sh            [pylint-odoo + oca-checks]
│   ├── .opencode/commands/         [/cdad-odoo-new-addon, etc.]
│   └── copier.yml-odoo             [opciones de configuración Odoo]
└── README.md

cdad-preset-django/                 [especialización Django, separada]
cdad-preset-rails/                  [especialización Rails, separada]
```

**Ventaja clave**: Un usuario que necesita CDAD genérico (Python, Node, Go, Rust) obtiene `cdad-core` solamente. Usuario Odoo obtiene `cdad-core` + `cdad-preset-odoo`. Cambios a la metodología central se propagan a todos.

---

## 2. CLI universal: Orquestadora multi-editor

### 2.1 Concepto

La CLI (`cdad-cli`) es el **single source of truth**. OpenCode, VS Code, Zed, Claude Code, terminal pura: todos invocan la misma CLI.

```
Terminal pura          VS Code                OpenCode
$ cdad init            $ cdad init            /cdad:init
$ cdad discover        $ cdad discover        /cdad:discover
$ cdad red             $ cdad red             /cdad:red
$ cdad green           $ cdad green           /cdad:green
$ cdad review          $ cdad review          /cdad:review
$ cdad merge-check     $ cdad merge-check     /cdad:merge-check
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                      │
         ╔════════════▼═════════════╗
         ║    cdad-cli (orquestador)║
         ║  - Detecta framework    ║
         ║  - Carga presets        ║
         ║  - Ejecuta scripts      ║
         ║  - Maneja state machine ║
         ║  - Invoca agentes       ║
         ╚════════════════════════╝
```

### 2.2 Flujo de uso real

**Ejemplo 1: Terminal pura (local, sin editor)**
```bash
$ cd mi-proyecto-odoo
$ cdad status
  Current stage: RED
  Active feature: user-authentication
  Progress: tests 3/5 passing

$ cdad green
  → Detecta framework: odoo (por leyenda detectada)
  → Carga preset: odoo (docker-compose, pylint-odoo, etc.)
  → Ejecuta: scripts/cdad/implementer-runner.sh
  → Agente implementa
  → Tests pasan
```

**Ejemplo 2: OpenCode (con agentes integrados)**
```bash
Dentro de OpenCode chat:
/cdad:discover --feature "Email notifications"
  → OpenCode invoca: cdad discover --feature "Email notifications" --opencode
  → CLI detecta framework, carga preset
  → CLI invoca agente @architect (OpenCode subagent)
  → Arquitecto descubre requisitos
```

**Ejemplo 3: Zed (editor minimalista)**
```bash
Zed terminal integrada:
cdad status
  → CLI devuelve estado
  → Zed muestra en panel

O con MCP server (futuro):
  Zed + MCP se conecta a cdad-cli como MCP server
  → Zed puede usar comandos CDAD como herramientas
```

### 2.3 Stack técnico de la CLI

```
cdad-cli (TypeScript/Node.js 18+)
├── CLI Parser (commander.js)
├── Stage Detector (detecta etapa actual)
├── Framework Detector (detecta framework automáticamente)
├── Preset Loader (carga preset dinámicamente)
├── Script Executor (ejecuta scripts agnósticos + framework-specific)
├── OpenCode Integration (si está disponible)
└── State Manager (maneja .cdad-state.json)
```

### 2.4 Comandos principales

```bash
# Setup
cdad init                              # Inicializa proyecto (interactive)
cdad init --framework odoo             # Init con framework especificado
cdad matrix [--feature X]              # Matriz observable de complejidad

# Flujo estándar CDAD
cdad discover --feature "X"            # Discovery phase
cdad spec --feature "X"                # Especificación con contrato
cdad red --feature "X"                 # Red phase (test-writer aislado)
cdad green [--feature "X"]             # Green phase (implementer aislado)
cdad review [--feature "X"]            # Review phase (reviewer independiente)
cdad merge-check                       # Pre-merge validation + Memory Bank

# Estado
cdad status                            # Estado actual del proyecto
cdad status --json                     # Para integración
cdad status --watch                    # Modo watch (actualiza cada 5s)

# Escalabilidad
cdad epic create --name "X"            # Crear epic
cdad epic design --epic "X"            # RFD session para epic
cdad epic feature-split --epic "X"     # Sugerir features + dependencias
cdad epic checkpoint --epic "X"        # Validar checkpoint entre features
cdad epic finalize --epic "X"          # Consolidar epic, actualizar docs

cdad system create --name "X"          # Crear sistema
cdad system rfd --system "X"           # RFD colaborativa multi-team
cdad system team-setup --system "X"    # Setup inicial por equipo
cdad system integration-check --system "X"  # Validar integración
cdad system finalize --system "X"      # Finalizar, lessons learned
```

---

## 3. Patrones de escalabilidad: Micro, Feature, Epic, Sistema

### 3.1 Matriz de complejidad

```
           │ Micro   │ Feature │ Epic    │ Sistema
───────────┼─────────┼─────────┼─────────┼──────────────
Duración   │ 1-2h    │ 2-4d    │ 3-4w    │ 8-12w
Scope      │ Bug fix │ Nueva   │ 5-8     │ 20+ features
           │ simple  │ function│features │ multi-equipo
CDAD       │ Light   │ Estándar│ Estándar│ Estándar
intensidad │ (red+   │ (full   │ + Diseño│ + Gobernanza
           │ green)  │ cycle)  │         │
User       │ Dev     │ Dev +   │ Tech    │ Tech Lead +
involved   │ indiv.  │ Arch    │ Lead    │ Product
─────────────────────────────────────────────────────
Commands   │ cdad    │ cdad    │ cdad    │ cdad
           │ red,    │ discover│ epic    │ system
           │ green   │ spec    │ create/ │ create/rfd/
           │         │ red,    │ design/ │ team-setup/
           │         │ green,  │ feature-│integration
           │         │ review, │ split/  │-check/
           │         │ merge   │ check   │ finalize
```

### 3.2 Micro: Fix rápido, CDAD light

**Ejemplo: Remover parámetro deprecated de función**

```bash
$ cdad red --scope micro
  → Skip discovery (obvio qué hacer)
  → Plantilla de tests mínima
  → Test-writer escribe 1-2 tests

$ cdad green
  → Implementer arregla en 5 minutos

Duración total: 30-45 min
Memory Bank: Solo progress.md (1 línea)
```

### 3.3 Feature: CDAD estándar

**Ejemplo: Email verification on signup (Django)**

```bash
$ cdad discover --feature "Email verification"
  → Architect explora: models, signals, email backend, validaciones
  → Escribe discovery en docs/specs/email-verify-discovery.md

$ cdad spec
  → Spec con 6-8 postcondiciones verificables

$ cdad red
  → test-writer escribe tests (TransactionTestCase, fixtures)
  → Tests están RED

$ cdad green
  → implementer crea models, views, signals
  → Tests pasan GREEN

$ cdad review
  → reviewer valida contra spec
  → Genera reporte

$ cdad merge-check
  → Validación final, Memory Bank update
  → Merge a main

Duración total: 2-3 días
Memory Bank: Completa (specs, ADRs, activeContext, progress)
```

### 3.4 Epic: Múltiples features con checkpoint

**Ejemplo: Migrar MySQL → PostgreSQL (Odoo)**

```bash
$ cdad epic create --name "mysql-to-postgres"
$ cdad epic design --epic "mysql-to-postgres"
  → RFD colaborativa: arquitecto + tech lead diseñan estrategia

$ cdad epic feature-split --epic "mysql-to-postgres"
  → Sugiere features secuenciadas:
    1. Schema validation (descubre diffs)
    2. Migration script (usa output de 1)
    3. Shadow writes (paralelo, zero-downtime)
    4. ORM layer abstraction
    5. Cutover + validation

$ cdad discover --feature "Schema validation" --epic "..."
  → Feature 1: Discovery + Spec + Red + Green + Review + Merge
  
$ cdad epic checkpoint --epic "..." --after-feature "schema-validation"
  → Valida que Feature 2 puede comenzar
  → Archivos de output de Feature 1 accesibles
  → Tests de Feature 1 pasan

$ cdad discover --feature "Migration script" --epic "..."
  → Feature 2: similar, PERO usa output de Feature 1
  
... (Features 3-5 en paralelo)

$ cdad epic finalize --epic "..."
  → Consolida integration tests
  → Corre E2E completo
  → ADR final: lecciones aprendidas
  → Marca como "Complete"

Duración total: 4 semanas
Memory Bank: docs/epics/mysql-to-postgres/ (estructura completa)
```

### 3.5 Sistema: Multi-equipo, dirigido por dependencias (no timeline)

**Concepto clave**: Un sistema es un **conjunto de áreas de contrato** que múltiples equipos implementan en paralelo. El progreso se mide por **áreas completadas**, no por calendarios.

**Ejemplo: Redesign de plataforma checkout (e-commerce)**

#### Fase 0: Crear sistema y definir áreas de contrato

```bash
# Crear sistema (vacío, listo para áreas)
$ cdad system create --name "checkout-redesign"
  → Crea: docs/system/checkout-redesign/
  → State: DESIGN_PHASE

# Definir áreas (son los contratos entre equipos)
$ cdad system area-add --system "checkout-redesign" --area "api-v2"
$ cdad system area-add --system "checkout-redesign" --area "database-schema"
$ cdad system area-add --system "checkout-redesign" --area "payment-flow"
$ cdad system area-add --system "checkout-redesign" --area "observability"

# Ver estado
$ cdad system status --system "checkout-redesign"
  Status: DESIGN_PHASE
  Areas:
  ├─ api-v2 (PENDING → needs RFD)
  ├─ database-schema (PENDING → needs RFD)
  ├─ payment-flow (PENDING → needs RFD)
  └─ observability (PENDING → needs RFD)
```

#### Fase 1: Diseñar cada área (RFD colaborativa)

```bash
# RFD para cada área (en paralelo, sin orden específico)
$ cdad system rfd --system "checkout-redesign" --area "api-v2"
  → Colaboran: Backend tech lead + Frontend tech lead
  → Output: docs/system/checkout-redesign/rfd-api-v2.md
  → Contrato: docs/system/checkout-redesign/contracts/api-v2.yaml (OpenAPI spec)
  → State: api-v2 → DESIGN_COMPLETE

$ cdad system rfd --system "checkout-redesign" --area "database-schema"
  → Colaboran: Data engineer + Backend lead
  → Output: docs/system/checkout-redesign/rfd-schema.md
  → Contrato: docs/system/checkout-redesign/contracts/schema.sql
  → State: database-schema → DESIGN_COMPLETE

$ cdad system rfd --system "checkout-redesign" --area "payment-flow"
  → Colaboran: Backend lead + Payment expert
  → Output: docs/system/checkout-redesign/rfd-payment.md
  → Contrato: docs/system/checkout-redesign/contracts/payment-flow.yaml
  → State: payment-flow → DESIGN_COMPLETE

$ cdad system rfd --system "checkout-redesign" --area "observability"
  → Colaboran: Architect + Infrastructure lead
  → Output: docs/system/checkout-redesign/rfd-observability.md
  → Contrato: docs/system/checkout-redesign/contracts/metrics.yaml
  → State: observability → DESIGN_COMPLETE

# Validar que todas las áreas están diseñadas
$ cdad system status --system "checkout-redesign"
  Status: READY_FOR_FEATURE_WORK (all areas DESIGN_COMPLETE)
```

#### Fase 2: Mapear dependencias entre features

```bash
# Generar grafo de dependencias
$ cdad system feature-map --system "checkout-redesign"
  → Output: docs/system/checkout-redesign/feature-dependency-graph.md
  → Muestra: qué feature depende de qué área

# Feature: Cart Service (Backend)
#   └─ Depends on: api-v2 (DESIGN_COMPLETE ✓)
#   └─ Depends on: database-schema (DESIGN_COMPLETE ✓)
#   → Can start NOW
#
# Feature: Cart UI (Frontend)
#   └─ Depends on: api-v2 (DESIGN_COMPLETE ✓)
#   → Can start NOW (will mock api-v2 until backend ready)
```

#### Fase 3: Equipos trabajan en paralelo (desbloqueados por dependencias)

```bash
# Backend comienza Cart Service (AHORA tiene api-v2 RFD)
$ cdad discover --feature "Cart Service" \
  --system "checkout-redesign" \
  --depends-on-areas "api-v2,database-schema"

$ cdad spec --feature "Cart Service" --system "checkout-redesign"
$ cdad red --feature "Cart Service"
$ cdad green
$ cdad review
→ Feature MERGED, contract tests validated

# SIMULTÁNEAMENTE: Frontend comienza Cart UI (mockea api-v2)
$ cdad discover --feature "Cart UI" \
  --system "checkout-redesign" \
  --uses-areas "api-v2" \
  --mock-from-contracts
  → NO espera a backend, usa mock de OpenAPI spec

$ cdad spec --feature "Cart UI"
$ cdad red --feature "Cart UI"
$ cdad green
→ Tests pasan contra mock
→ Cuando backend listo, tests pasan contra API real
```

#### Fase 4: Checkpoints = "Área completada" (NO semana N)

```bash
# Cuando TODOS los features de api-v2 están GREEN:
$ cdad system checkpoint --system "checkout-redesign" \
  --completed-area "api-v2"
  
  Validates:
  ✓ Cart Service GREEN
  ✓ Order Service GREEN
  ✓ Payment API GREEN
  ✓ All contract tests pass
  ✓ All frontend features work against real API
  
  → api-v2 state: COMPLETE
  → Unblocks: other features waiting on api-v2

$ cdad system checkpoint --system "checkout-redesign" \
  --completed-area "database-schema"
  
$ cdad system checkpoint --system "checkout-redesign" \
  --completed-area "payment-flow"
```

#### Fase 5: Integración (cuando TODAS las áreas COMPLETE)

```bash
# Solo cuando TODAS las áreas estén COMPLETE:
$ cdad system status --system "checkout-redesign"
  Status: ALL_AREAS_COMPLETE ✓
  
  Areas: api-v2, database-schema, payment-flow, observability
  Features: 18/18 merged

# Integración completa (ahora SÍ, todo está listo)
$ cdad system integration-check --system "checkout-redesign" \
  --all-areas-complete
  
  Validates:
  ✓ E2E: flujo completo (signup → checkout → payment)
  ✓ Load test: 1000 concurrent users
  ✓ Security: SQL injection, CSRF, XSS
  ✓ Data consistency
  ✓ Observability: métricas activas
  ✓ Performance: P99 < 200ms
  
  Green light: Ready for staging
```

#### Fase 6: Finalización

```bash
$ cdad system finalize --system "checkout-redesign"
  → All features merged to main
  → Tests passing
  → Documentation complete
  → ADRs written
  → Status: COMPLETE

Duration: 7 weeks 3 days (VARIABLE, driven by actual completion)
Teams: 22 personas
Features: 18 completed
Tests: 523
Coverage: 94%
```

**Diferencia clave**: No hay timeline. Duración es variable. Progreso se mide por **áreas completadas**, no por semanas transcurridas.

Memory Bank: `docs/system/checkout-redesign/` (rfds/, contracts/, features/, checkpoints/, integration-tests/)


---

## 4. Arquitectura en 4 niveles (marco Qwen, adaptado)

Este framework proporciona una forma de pensar sobre cómo se estratifica la solución:

### 4.1 Nivel 1: Orquestación

**Responsabilidad**: Punto de entrada, gestión de sesiones, routing

**Componentes**:
- CLI (`cdad-cli`)
- Comandos OpenCode slash (wrappers sobre CLI)
- Detección de estado actual
- Enrutamiento a agentes/scripts

**Artefactos**:
- CLI commands (init, status, discover, spec, red, green, review, merge-check)
- Estado máquina (.cdad-state.json)

### 4.2 Nivel 2: Aplicación

**Responsabilidad**: Lógica central de CDAD, gestión de agentes, ejecución de tareas

**Componentes**:
- cdad-core (agnóstico)
- cdad-presets (especializaciones framework)
- Agentes CDAD (.opencode/agents/)
- Memory Bank

**Artefactos**:
- Subagentes (architect, test-writer, implementer, reviewer, scribe)
- Specs con contratos
- Tests
- Documentación

**Patrón**: Engine-Adapter (Core agnóstico + Adapters framework-específicos)

### 4.3 Nivel 3: Metodología

**Responsabilidad**: Codificar comportamiento esperado en texto plano, versionable

**Componentes**:
- BriefingScript (spec de tarea, reemplaza prompts vagos)
- MentorScript (rulebook del proyecto: convenciones, principios, mejores prácticas)
- Scripts de flujo (.opencode/commands/)
- Documentación de patrones

**Artefactos**:
- docs/specs/feature-name.md (BriefingScript)
- docs/.mentor.md o docs/conventions.md (MentorScript)
- docs/patterns/ (patrones por escala)
- docs/.cdad-state.json (control de estado)

**Nota**: Estos reemplazan prompts informales por documentación formal, versionable, reutilizable.

### 4.4 Nivel 4: Entorno

**Responsabilidad**: Proporcionar contexto seguro, gestionar ejecución aislada

**Componentes**:
- Editor (OpenCode, VS Code, Zed, Claude Code)
- Sandbox por defecto (Docker)
- Permisos granulares (glob patterns)

**Artefactos**:
- .opencode.json (permisos, modelos por agente)
- docker-compose.yml (para frameworks que lo necesitan)
- Scripts de ejecución (scripts/cdad/, scripts/framework/)

---

## 5. Mejoras respecto a v1

| Aspecto | v1 | v2 |
|---------|----|----|
| **Agnósticismo** | Parcial (Odoo-centric) | ✅ Total (core + presets) |
| **Multi-editor** | OpenCode only | ✅ CLI + OpenCode + VS Code + Zed |
| **Setup** | Manual (copier + config) | ✅ Automático (cdad init) |
| **Escalabilidad** | Feature level | ✅ Micro + Feature + Epic + Sistema |
| **Documentación** | Prompts vagos | ✅ BriefingScript/MentorScript |
| **Claridad arquitectónica** | Buena | ✅ Excelente (4 niveles formales) |

---

## 6. Roadmap de implementación

### Fase 0: Validación (1 semana)

- [ ] Spike CLI mínima (5 comandos, TS)
- [ ] Spike core agnóstico (remover Odoo-specifics)
- [ ] Spike preset Odoo (separado)
- [ ] Test end-to-end en proyecto pequeño

### Fase 1: MVP (2-3 semanas)

- [ ] CLI completa (todos comandos estándar)
- [ ] cdad-core template agnóstico
- [ ] cdad-preset-odoo, cdad-preset-django
- [ ] OpenCode wrappers actualizados
- [ ] Documentación: README, quick start

### Fase 2: Escalabilidad (2-3 semanas)

- [ ] Comandos epic + system agregados
- [ ] Memory Bank extendida (epics, systems)
- [ ] Patrones documentados (micro, feature, epic, system)
- [ ] Dogfood real (aplicar a proyecto cliente)

### Fase 3: Integración & Ecosistema (4+ semanas)

- [ ] Publicar CLI en npm
- [ ] Soporte multi-editor (VS Code, Zed, Claude Code)
- [ ] MCP server (integración profunda)
- [ ] Community preset registry
- [ ] Blog post / demo videos

### Fase 4: Optimización (futuro)

- [ ] ATLE (Agent Task Learning Environment)
- [ ] Mejoras performance
- [ ] Community feedback loop

---

## 7. Qué tomar de propuestas alternativas

### De Gemini: "Diseño Arquitectónico..."

✅ **Utilizar**:
- Confirmación de Engine-Adapter pattern
- MCP como integración futura
- C4 Model para épics (documentación optional)

❌ **No utilizar**:
- Headless ERP (es decisión de proyecto, no CDAD)
- HAWK framework (CDAD ya cubre)

### De Qwen: "Más Allá de Odoo..."

✅ **Utilizar**:
- 4 niveles de abstracción (marco teórico)
- BriefingScript/MentorScript (mejoras Memory Bank)
- Sandbox by default (best practice)

⚠️ **Considerar para Fase 2**:
- ATLE (cuando haya masa crítica de datos)

❌ **No utilizar**:
- LoopScript (conflicta con CLI)
- Demasiados nuevos conceptos en simultaneidad

---

## 8. Diferencia clave: v1 vs v2

### v1 (documento original)
- OpenCode-centric
- Preset Odoo acoplado
- Cubre feature level bien
- Método manual de setup

### v2 (esta propuesta)
- Framework-agnóstico
- CLI universal (single source of truth)
- Escalabilidad (micro → sistema)
- Setup automático
- 4 niveles de abstracción formales
- Preparado para futuro (MCP, múltiples editores)

---

## Conclusión

**CDAD × OpenCode v2 es una evolución metodológica**, no un refactor. Toma la solidez de CDAD, agrega agnósticismo de frameworks, automatización CLI, y patrones escalables. 

**Resultado**: Desarrollo agentico profesional, reproducible, y agnóstico a tools.

