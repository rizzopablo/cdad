# CDAD Workflow: Guía práctica comparativa

**Ejemplos reales: estado actual vs. futuro mejorado**

---

## Escenario 1: Micro-feature en Odoo (cambio rápido)

### Antes (documento actual OpenCode+CDAD)

```
1. Abres OpenCode en proyecto Odoo
2. Paso previo: proyecto ya inicializado con copier cdad-template --preset=odoo
   (esto requirió: clonar template, responder preguntas, esperar a que se
    descarguen deps, configurar pre-commit, crear Memory Bank manualmente)

3. Quiero cambiar: "Agregar campo `currency_id` al modelo `res.partner`"

4. Abres chat de OpenCode, corres: /cdad:discover
   - Lee .opencode/command/cdad-discover.md
   - Invoca agente architect
   - Architect (con acceso a todo el proyecto) explora modelos, campos existentes
   - Escribes discovery en docs/specs/partner-currency-discovery.md

5. Corres: /cdad:spec
   - Architect escribe spec con 4 postcondiciones

6. Corres: /cdad:red
   - Invoca test-writer (sesión aislada)
   - test-writer escribe tests en tests/partner/test_currency_field.py
   - Tests están RED (fallan, no hay implementación)

7. Corres: /cdad:green
   - Invoca implementer
   - implementer agrega campo en models/res_partner.py
   - Tests pasan (GREEN)

8. Corres: /cdad:review
   - Invoca reviewer (idealmente otro modelo)
   - Reviewer compara spec vs código
   - Genera reporte

9. Corres: /cdad:merge-check
   - Verifica que nada se rompió
   - Invoca scribe
   - Scribe propone update a progress.md, activeContext.md

10. Haces merge manual del PR

Tiempo total: 45-60 min para un cambio muy simple
Fricción: múltiples invocaciones de comando, esperar entre fases, OpenCode-bound
```

### Después (con refactor: core + CLI)

```
1. Nuevo proyecto: 
   $ cdad init --name my-odoo-project --framework odoo --odoo-version 17.0
   ✓ Template descargado
   ✓ Preset Odoo aplicado (docker-compose, pylint-odoo)
   ✓ Deps instalados
   ✓ Memory Bank inicializado
   ✓ Pre-commit configurado
   → Time: 2-3 min (vs. 10-15 min antes)

2. Cambio: agregar campo currency_id a res.partner

   $ cdad discover --feature "Add currency field to partner"
   → Architect (OpenCode o CLI interactivo):
     * Explora modelo res.partner
     * Pregunta: ¿currency_id es Many2One o Many2Many?
     * Pregunta: ¿se debe validar contra company currency?
     * Escribe discovery
   → Auto-guardado en docs/specs/add-currency-field-discovery.md

   $ cdad spec
   → Architect (desde discovery):
     * Escribe spec con postcondiciones verificables
     * [✓] Field exists with type Many2One to res.currency
     * [✓] Field is required for all partners
     * [✓] Validation: currency in company currencies
     * [✓] Default: company's currency
   → Auto-guardado en docs/specs/add-currency-field-spec.md

   $ cdad red
   → test-writer crea tests/partner/test_currency_field.py
   → Tests fallan (RED), como debe ser
   → Time: 5 min

   $ cdad green
   → implementer hace pasar tests
   → Agrega campo en models/res_partner.py
   → Tests pasan (GREEN)
   → Time: 10 min

   $ cdad review
   → reviewer valida spec vs código
   → Genera reporte
   → Time: 3 min

   $ cdad merge-check
   → Valida que todo está bien
   → Actualiza Memory Bank automáticamente
   → Done!

   Tiempo total: 25-30 min para un cambio muy simple
   Fricción: CERO (todo es un comando, todo es agnóstico)
   Bonus: funciona en terminal pura, VS Code, Zed, Claude Code, etc.

Comparación:
┌──────────────────────┬────────────┬──────────────┐
│ Métrica              │ Antes      │ Después      │
├──────────────────────┼────────────┼──────────────┤
│ Tiempo total         │ 45-60 min  │ 25-30 min    │
│ Setup proyecto nuevo │ 10-15 min  │ 2-3 min      │
│ OpenCode-bound       │ Sí         │ No (CLI)     │
│ Requiere copier      │ Sí, manual │ Sí, automático│
│ Error handling       │ Genérico   │ Agnóstico    │
└──────────────────────┴────────────┴──────────────┘
```

---

## Escenario 2: Feature de tamaño medio (Django)

### Antes

```
Proyecto Django existente. Feature: "User email verification on signup"

1. OpenCode init? → No existe para Django, lo haces manualmente
2. Copias estructura CDAD a mano (o de otro proyecto)
3. Configuras pre-commit para Django (coverage, black, isort)
4. Configuras Django test runner (pytest-django)

5. Corres /cdad:discover → Architect me ayuda
   - Descubre: models (User, Verification), signals, email backend, tokens
   - Descubre: integraciones con email service (SendGrid? Gmail?)
   - Escribe discovery

6. /cdad:spec → Spec con 6 postcondiciones
7. /cdad:red → test-writer escribe tests
8. /cdad:green → implementer implementa views, models, signals
9. /cdad:review → reviewer valida
10. /cdad:merge-check → scribe actualiza Memory Bank

Time: 3-4 horas
Fricción: OpenCode no "conoce" Django de oficio, requiere context extra
```

### Después

```
$ cdad init --name email-verify-django --framework django --python-version 3.11
✓ Template base descargado
✓ Preset Django aplicado:
  - requirements-django.txt (pytest-django, factory-boy, etc.)
  - Django test runner configuration
  - Django-specific linters (flake8-django, pylint-django)
  - docker-compose para postgresql
✓ Agentes especializados opcionales (django-test-writer.md)
✓ Memory Bank + pre-commit configurados

$ cdad discover --feature "Email verification on signup"
→ Architect (Django-aware):
  * Detecta que es Django (leyendo manage.py, settings.py)
  * Ofrece preguntas contextuales:
    - Email backend: Celery tasks o synchronous?
    - Token generation: use django-rest-auth o custom?
    - Where to verify: new view o activation link?
  * Escribe discovery con patrón Django

$ cdad spec
→ Spec con postcondiciones:
  * [✓] User.email_verified field exists (bool)
  * [✓] signup() creates User + Verification record
  * [✓] Verification token is time-limited (24h)
  * [✓] GET /auth/verify?token=X marks user as verified
  * [✓] Verification links are one-time use
  * [✓] Unverified users can't login
  * [✓] Email sent via configured backend (sync or async)

$ cdad red --framework django
→ test-writer (django-test-writer.md):
  * Escribe tests en tests/auth/test_email_verification.py
  * Usa TransactionTestCase (Django convention)
  * Genera fixtures con Factory Boy
  * Tests para: signup, token validation, one-time use, expiry, etc.

$ cdad green
→ implementer (odoo-implementer.md):
  * models/user.py: agrega field email_verified
  * models/verification.py: crea modelo con token + expiry
  * views.py: signup + verification view
  * signals.py: send email on signup
  * management/commands/cleanup_expired_tokens.py
  * Tests pasan

$ cdad review
→ reviewer:
  * Valida contra spec
  * Checa: SQL queries (N+1?), email sending reliability, security (token predictable?)
  * Checa: password reset vs email verification (no conflicts?)
  * Genera reporte

$ cdad merge-check
→ automático:
  * Valida pre-commit hooks
  * Corre full test suite
  * Actualiza Memory Bank:
    - activeContext.md: feature done
    - progress.md: agregó un entry
    - adr/: posiblemente ADR sobre token strategy
  * Done!

Time: 2-3 horas (vs. 3-4 antes)
Bonus: CLI + agentes Django-aware hacen todo más fluido
Bonus: Funciona en terminal pura, VS Code, Zed, Claude Code
```

---

## Escenario 3: Epic (refactor grande)

### Ejemplo: "Migrate database MySQL → PostgreSQL" (Odoo)

### Estado futuro con escalabilidad

```
$ cdad epic create --name "mysql-to-postgres"
→ Crea estructura:
  docs/epics/mysql-to-postgres/
  ├── README.md (overview, timeline)
  ├── rfd.md (architecture decisions)
  ├── features/ (1 carpeta por feature)
  ├── integration-tests/
  └── status.md (daily dashboard)

$ cdad epic design --epic "mysql-to-postgres"
→ RFD colaborativa:
  * Architect propone estrategia
  * Tech lead revisa + feedback
  * ADRs para decisiones críticas:
    - ADR-01: Migrate on zero-downtime (shadow writes)
    - ADR-02: Test matrix coverage (Odoo + PostgreSQL versions)
    - ADR-03: Rollback strategy

$ cdad epic feature-split --epic "mysql-to-postgres"
→ Sugiere features y dependencias:

  Feature 1: Schema validation
    ├─ Descubre diferencias: MySQL UNSIGNED → PostgreSQL types
    ├─ Descubre: collations, character sets
    └─ Descubre: custom functions/procedures

  Feature 2: Migration script
    ├─ Depends on: Schema validation (Feature 1)
    ├─ Escribe data migration (safe, testeable)
    └─ Descubre: timeout strategies

  Feature 3: Shadow writes
    ├─ Depends on: Migration script (Feature 2)
    ├─ Parallel writes a MySQL + PostgreSQL
    ├─ Compara resultados para detectar diffs
    └─ Critical for zero-downtime

  Feature 4: ORM layer abstraction
    ├─ Depends on: Shadow writes (Feature 3)
    ├─ Prepara código para ambos backends
    └─ Tests contra ambos

  Feature 5: Cutover + validation
    ├─ Depends on: All features above
    ├─ Toggle read traffic a PostgreSQL
    ├─ Validation: reads match MySQL
    └─ Rollback plan

Precedence graph (generated):
  Schema Validation (Feat 1)
  └─ Migration Script (Feat 2)
    └─ Shadow Writes (Feat 3)
      └─ ORM Layer (Feat 4)
        └─ Cutover (Feat 5)

Roadmap:
  Week 1: Features 1-2 (design + implementation)
  Week 2: Feature 3 (shadow writes, critical)
  Week 3: Feature 4 (abstraction)
  Week 4: Feature 5 (cutover, vert testing)
  Slack: 2 days per week for fixes + unknowns

$ cdad discover --feature "Schema validation" --epic "mysql-to-postgres"
→ Architect explora:
  * MySQL schema actual
  * PostgreSQL equivalences
  * Incompatibilities (UNSIGNED → constraint)
  * Differences in functions/procedures

$ cdad spec --feature "Schema validation" --epic "mysql-to-postgres"
→ Spec con postcondiciones:
  * [✓] Script detects all MySQL tables vs PostgreSQL equivalents
  * [✓] Identifies type mismatches (UNSIGNED, DOUBLE vs NUMERIC, etc.)
  * [✓] Flags unsupported features (MySQL triggers → PostgreSQL functions)
  * [✓] Generates report with mapping suggestions
  * [✓] Report is machine-readable (JSON) for next feature
  * [✓] Validation runs on both staging + production schemas

$ cdad red → $ cdad green → $ cdad review → $ cdad merge-check
→ Feature 1 done, merged

$ cdad epic checkpoint --epic "mysql-to-postgres" --after-feature "schema-validation"
→ Valida que Feature 2 (Migration Script) puede comenzar:
  * Output de Feature 1 (JSON schema mapping) accesible
  * Tests de Feature 1 pasan
  * Documentation actualizada
  * Green light para Feature 2

$ cdad discover --feature "Migration script" --epic "mysql-to-postgres"
→ Architect USA output de Feature 1:
  * Lee schema-mapping.json
  * Diseña migration strategy
  * Considera: large tables (batching), foreign keys, triggers

$ cdad spec ... $ cdad red ... $ cdad green ... $ cdad review ... $ cdad merge-check
→ Feature 2 done

... (Features 3, 4, 5 en paralelo, con checkpoints entre ellas)

$ cdad epic finalize --epic "mysql-to-postgres"
→ Cuando todos Features están merged:
  * Consolida integration tests
  * Corre E2E tests completos
  * Genera documento final: "Migration complete" ADR
  * Actualiza architecture docs
  * Cierra epic
  * Updates Memory Bank global (ya no es "work in progress")

Time total: 4 semanas (vs. 6-8 estimadas en proyecto manual)
Quality: Alta (spec + tests + review en cada feature)
Risk: Bajo (validaciones en cada checkpoint)
Visibility: Alta (cdad epic status muestra % complete, blockers, etc.)
```

---

## Escenario 4: Sistema completo (multi-equipo, dirigido por dependencias)

**Concepto clave**: En un sistema, la unidad de orquestación es el **ÁREA DE CONTRATO**, no el calendario ni los equipos. El progreso se mide por áreas completadas.

```bash
# DIFERENCIA CLAVE: NO hay "teams" ni "--timeline"
# La unidad es el ÁREA (contrato entre equipos)

# Fase 0: Crear sistema + definir áreas de contrato
$ cdad system create --name "checkout-redesign"
$ cdad system area-add --system "checkout-redesign" --area "api-v2"
$ cdad system area-add --system "checkout-redesign" --area "database-schema"
$ cdad system area-add --system "checkout-redesign" --area "payment-flow"
$ cdad system area-add --system "checkout-redesign" --area "observability"

→ State: DESIGN_PHASE
→ Ready to design each area

# Fase 1: Diseñar CADA ÁREA (RFD colaborativa)
$ cdad system rfd --system "checkout-redesign" --area "api-v2"
  → Colaboran: Backend + Frontend tech leads
  → Output: rfd-api-v2.md
  → Contrato: api-v2.yaml (OpenAPI spec)
  → State: api-v2 DESIGN_COMPLETE

$ cdad system rfd --system "checkout-redesign" --area "database-schema"
  → Colaboran: Data engineer + Backend lead
  → Output: rfd-schema.md
  → Contrato: schema.sql
  → State: database-schema DESIGN_COMPLETE

$ cdad system rfd --system "checkout-redesign" --area "payment-flow"
  → Output: rfd-payment.md
  → State: payment-flow DESIGN_COMPLETE

$ cdad system rfd --system "checkout-redesign" --area "observability"
  → Output: rfd-observability.md
  → State: observability DESIGN_COMPLETE

# Fase 2: Mapear dependencias entre features
$ cdad system feature-map --system "checkout-redesign"
  → Feature "Cart Service" depends on: api-v2 ✓, database-schema ✓ → CAN START NOW
  → Feature "Cart UI" depends on: api-v2 ✓ → CAN START NOW (will mock)
  → Feature "Payment Integration" depends on: payment-flow ✓, api-v2 ✓ → CAN START NOW

# Fase 3: TEAMS trabajan en PARALELO (no por calendario, por dependencias)
# NO espera a "semana 2" o "semana 5"
# Equipos arranca CUANDO su dependencia está DESIGN_COMPLETE

Backend Team:
$ cdad discover --feature "Cart Service" \
  --system "checkout-redesign" \
  --depends-on-areas "api-v2,database-schema"
  → Tiene ambos RFDs, puede comenzar AHORA
  → Spec + Red + Green + Review + Merge

$ cdad discover --feature "Order Persistence" \
  --system "checkout-redesign" \
  --depends-on-areas "database-schema,api-v2"
  → Comenzar cuando ambos RFDs done

Frontend Team (SIN esperar backend):
$ cdad discover --feature "Cart UI" \
  --system "checkout-redesign" \
  --uses-areas "api-v2" \
  --mock-from-contracts
  → Comienza INMEDIATAMENTE (mockea api-v2.yaml)
  → NO depende de database-schema
  → Cuando backend Cart Service esté GREEN, tests contra API real

Infrastructure Team:
$ cdad discover --feature "Observability Integration" \
  --system "checkout-redesign" \
  --depends-on-areas "observability"
  → Comienza AHORA (tiene observability RFD)

# Cada feature sigue CDAD estándar
$ cdad spec --feature "Cart Service" --system "checkout-redesign"
$ cdad red --feature "Cart Service"
$ cdad green
$ cdad review
→ Feature merged, contract tests validated

# Fase 4: CHECKPOINTS = "Área completada" (NO "semana 9")
# Checkpoint NO es temporal, es "estado de completitud del área"

$ cdad system checkpoint --system "checkout-redesign" \
  --completed-area "api-v2"
  
  Validates:
  ✓ ALL features producing api-v2 are GREEN
    ├─ Cart Service ✓
    ├─ Order Service ✓
    └─ Payment API ✓
  ✓ ALL contract tests pass (response matches OpenAPI spec)
  ✓ ALL frontend features tested against real API
  
  → api-v2 state: COMPLETE
  → Unblocks: features waiting on api-v2

$ cdad system checkpoint --system "checkout-redesign" \
  --completed-area "database-schema"
  
  Validates:
  ✓ All migrations created and tested
  ✓ Schema normalized
  ✓ Indexes efficient
  
  → database-schema state: COMPLETE

$ cdad system checkpoint --system "checkout-redesign" \
  --completed-area "payment-flow"
  
  → payment-flow state: COMPLETE

$ cdad system checkpoint --system "checkout-redesign" \
  --completed-area "observability"
  
  → observability state: COMPLETE

# Fase 5: INTEGRACIÓN = Cuando TODAS las áreas COMPLETE (NOT "week 9")
$ cdad system status --system "checkout-redesign"
  Status: ALL_AREAS_COMPLETE ✓
  
  Areas:
  ├─ api-v2 ✓ COMPLETE
  ├─ database-schema ✓ COMPLETE
  ├─ payment-flow ✓ COMPLETE
  └─ observability ✓ COMPLETE
  
  Features: 18/18 merged
  Total tests: 523
  
  Next: cdad system integration-check

# AHORA SÍ: Integración completa (porque TODO está listo)
$ cdad system integration-check --system "checkout-redesign" \
  --all-areas-complete
  
  Validates:
  ✓ E2E test: complete user flow (signup → cart → checkout → payment)
  ✓ Load test: 1000 concurrent users
  ✓ Security: SQL injection, CSRF, XSS, CORS
  ✓ Data consistency: inventory correct, no race conditions
  ✓ Observability: all metrics being collected
  ✓ Performance: P99 latency < 200ms
  
  Green light: Ready for staging

# Fase 6: Finalización
$ cdad system finalize --system "checkout-redesign"
  → All features merged to main
  → E2E tests passing
  → Load tests passing
  → Security scan clean
  → Observability complete
  → Documentation complete
  → Team runbooks written
  → Final ADR written
  → Status: COMPLETE

$ cdad system status --system "checkout-redesign"
  Status: COMPLETE
  Created: 2026-05-01
  Duration: 7 weeks 3 days (VARIABLE, not calendar-driven)
  Teams: 22 personas
  Features: 18 completed
  Total tests: 523
  Coverage: 94%

RESULTADO:
- Duration variable (depends on actual completion, not week number)
- Progress measured by areas completed, not calendar
- Parallelism driven by dependency graph
- NO waiting for "week 9": integration happens when ready
- NO artificial delays due to calendar: if api-v2 done in week 4, checkpoint happens week 4
```

## Comparación visual: Micro vs Feature vs Epic vs System

```
Complejidad y tiempo (aproximado)

                                │ Micro │ Feature │ Epic │ System │
────────────────────────────────┼───────┼─────────┼──────┼────────┤
Setup time                       │ 0 min │ 0 min   │ 1h   │ 1 day  │
Discover phase                   │ skip  │ 2h      │ 4h   │ 1 week │
Design/RFD phase                 │ -     │ -       │ 4h   │ 1 week │
Implementation (discover→merge)  │ 30m   │ 2 days  │ 2wks │ 10 wks │
Test coverage                    │ 2-3   │ 10-15   │ 50+  │ 500+   │
Review ciclos                    │ 1     │ 1       │ 5-7  │ 15-20  │
Total time (wall clock)          │ 1h    │ 3-4d    │ 4w   │ 12w    │
Memory Bank size                 │ small │ medium  │ 5MB  │ 50MB+  │
Participants                     │ 1     │ 3-4     │ 5-8  │ 20-50  │
Lines of docs                    │ 20    │ 200     │ 2KB  │ 20KB   │

Tool usage pattern:
Micro:   cdad discover (skip) → cdad spec → cdad red → green → review → merge
         (or just: cdad green if it's obvious)
         
Feature: cdad discover → cdad spec → cdad red → cdad green → cdad review → cdad merge-check
         Standard full cycle
         
Epic:    cdad epic create → cdad epic design → cdad epic feature-split
         (then CDAD standard per feature)
         → cdad epic checkpoint (between features)
         → cdad epic finalize
         
System:  cdad system create → cdad system rfd (multiple areas)
         → cdad system team-setup (per team)
         → (CDAD standard features, in parallel)
         → cdad system integration-check (weekly)
         → cdad system finalize
```

---

## Checklist: Transición de estado actual a futuro

### Fase 0: Validación (1 semana)

- [ ] Spike: implementar CLI mínima (5 comandos)
- [ ] Spike: crear template core (sin Odoo)
- [ ] Spike: crear preset Odoo
- [ ] Prueba: flujo micro-feature end-to-end
- [ ] Prueba: flujo feature end-to-end
- [ ] Documento: "Lecciones aprendidas"

### Fase 1: MVP (2-3 semanas)

- [ ] CLI completa (init, status, discover, spec, red, green, review, merge-check, matrix)
- [ ] Template core refactorizado (agnóstico)
- [ ] Preset Odoo completo
- [ ] Preset Django (opcional)
- [ ] OpenCode wrappers (commands slash actualizados)
- [ ] Plugin OpenCode actualizado
- [ ] Documentación: README + quick start

### Fase 2: Escalabilidad (2 semanas)

- [ ] Comandos epic (create, design, feature-split, checkpoint, finalize)
- [ ] Comandos system (create, rfd, team-setup, integration-check, finalize)
- [ ] Memory Bank extendido (epics, systems)
- [ ] Dogfood real: aplicar a proyecto cliente

### Fase 3: Integración (3+ semanas)

- [ ] Publicar CLI en npm
- [ ] Documentación por editor (VS Code, Zed, Claude Code)
- [ ] Blog post / demo video
- [ ] Community feedback loop

---

**Conclusión**: El refactor (core agnóstico + CLI + presets) **reduce fricción dramáticamente**:
- ✅ Setup: 10-15 min → 2-3 min
- ✅ Micro-feature: 45-60 min → 25-30 min
- ✅ Feature: 3-4h → 2-3h
- ✅ Multi-editor: OpenCode only → CLI + OpenCode + VS Code + Zed + Claude Code
- ✅ Framework diversity: Odoo only → Odoo + Django + Rails + FastAPI + ...
