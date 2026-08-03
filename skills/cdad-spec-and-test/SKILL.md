---
name: "cdad-spec-and-test"
description: "CDAD spec/test workflow: postcondición, formato mínimo, tests antes del build, TDD real con criterio de aceptación."
---

# Skill: CDAD Spec & Test

## Summary
Estandariza cómo se escriben specs y tests en el ciclo CDAD. Spec minimalista (postcondición + criterio de aceptación). Tests escritos antes del build. Aplica a código, documentación, setup de infra, lo que sea.

## Cuándo usarla
- Al empezar **cualquier** tarea: código, doc, setup, investigación
- En la transición de **Discovery → Spec** (Gate 0→1)
- Cuando el gate **Verify** no está claro porque no definiste qué significa "terminado"

## Cómo escribir una Spec CDAD

Una spec no es un documento de 50 páginas. Es:

```yaml
context: Breve — qué estamos haciendo y por qué
resolution: Qué problema resuelve / qué necesidad cubre
postcondition: Cómo sé que esto está terminado (frase única)
verification: Lista de verificación, un test por línea
```

### Ejemplo — Setup de instancia de proyecto:

```yaml
context: Configurar acceso de desarrollo a example.saas.ar
resolution: Tener acceso SSH + Odoo + GitHub para I+D
postcondition: Puedo hacer login a Odoo y clonar repos desde la instancia
verification:
  - ssh dev@localhost whoami → "dev"
  - curl http://127.0.0.1:8070/xmlrpc/2/common → versión Odoo
  - ssh -T git@github.com 2>&1 | grep "Hi ofapsaas"
  - test -d ~/src/virtualmin-opo → existe
  - test -d ~/.opo/src/custom-dev → existe
```

### Ejemplo — Módulo Odoo:

```yaml
context: Módulo de health check para el dominio del deploy
resolution: Que Odoo reporte su estado (DB, workers, espacio) vía API
postcondition: GET /health retorna JSON con db_status, worker_count, disk_usage
verification:
  - curl /health → HTTP 200, JSON con los 3 campos
  - Cuando la DB está caída, db_status = "error"
  - Cuando hay 0 workers, worker_count = 0
  - create_from_wizard=True crea el health check automáticamente
```

## Reglas de la Spec

1. **Postcondición obligatoria.** Si no podés escribir en una línea qué significa "terminado", no entendés bien la tarea.
2. **Tests antes del código.** La verification se escribe ANTES de Build. Si después los tests pasan, terminaste.
3. **Tests no son solo pytest.** Acepta:
   - `curl ... | grep ...` (integración)
   - `python3 -c "..."` (unittest inline)
   - Check de archivos (`test -f`, `test -d`)
   - Pasos manuales con resultado esperado (para UI)
4. **Si un test falla, la tarea no está terminada.** Punto. Sin excusas.

## Cómo cerrar el ciclo

```
[Build]  →  [Verify: correr tests]
                ↓
          ¿Pasan todos?
           /        \
          Sí         No
         /            \
    [Merge]       [Fix → Build again]
```

Si después de Verify todos los tests pasan → Merge (commit, wiki, skill, lo que corresponda).
Si no pasa alguno → volver a Build, no avanzar.

## Tests que NO sirven

❌ "Probar manualmente que anda" — sin criterio objetivo
❌ "El usuario debería poder ver la pantalla" — ¿cómo se mide?
❌ "Probar en staging" — sin especificar qué se prueba
❌ Cualquier test que no puedas ejecutar en <30 segundos

## Tests que SIRVEN

✅ `curl endpoint ; espero HTTP 200`
✅ `python3 -c "import modulo; modulo.funcion(); print('OK')"`
✅ `ssh server "comando; test condición"`
✅ `test -f archivo`
✅ Lista de pasos con resultado esperado por paso

## Integración con CDAD

| Gate | Acción |
|------|--------|
| 0→1 (Discovery→Spec) | Escribir spec.yaml con postcondition + verification |
| 1→2 (Spec→TDD) | Escribir tests (automáticos o checklist) |
| 2→3 (TDD→Review) | Ejecutar tests contra el build |
| 3→4 (Review→Merge) | Todos los tests pasan → merge |
