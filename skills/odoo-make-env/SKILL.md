---
name: "odoo-make-env"
description: >
  Contrato make para ejecutar tests Odoo en proyectos CDAD (targets test /
  test-one / test-clean) y guía para implementar el contrato en un entorno
  concreto (odoo.sh, staging privado, docker local, oca-ci). Usar cuando un proyecto
  Odoo debe exponer su runner de tests a los agentes CDAD-Odoo, o al crear
  el Makefile de un proyecto Odoo nuevo.
---

# odoo-make-env — contrato de ejecución de tests Odoo

**Principio:** CDAD define QUÉ se verifica (gates + evidencia); el proyecto
define CÓMO (Makefile versionado en el repo). Los agentes CDAD-Odoo invocan
solo los 3 targets — nunca comandos específicos de un entorno.

## El contrato (obligatorio, nombres exactos)

| Target | Semántica | Usado por |
|---|---|---|
| `make test` | suite completa sobre DB caliente | test-writer (AUDIT), implementer (GREEN) |
| `make test-one TEST=mod:Clase.metodo` | un solo test | test-writer (RED) |
| `make test-clean` | instalación del módulo desde cero + suite | implementer (gate GREEN), reviewer |

**Reglas:**
1. `test-clean` = "instalación desde cero" — el mecanismo es libre por
   entorno (DB nueva si se puede; reset+`-i` si no).
2. Corridas SIEMPRE `--stop-after-init --test-enable` y sin workers
   (`workers = 0`): jobs efímeros, mínimo uso de conexiones.
3. `test-clean` ejercita la instalación CON demo data.
4. Evidencia = output pegado con la línea `0 failed, 0 error(s) of N tests`.
5. El Makefile es versionable y revisable — vive en el repo del proyecto.

## Cómo implementar un entorno nuevo

1. Copiar `assets/Makefile.template` al repo del proyecto.
2. Resolver las 4 variables: binario odoo, config, DB de test, mecanismo de
   "desde cero".
3. Ver tabla de varianza (abajo) para entornos conocidos.
4. Agregar retry si el postgres es compartido (patrón `run_odoo` del
   template de staging privado, en referencias privadas de ese entorno).
5. Verificar los 3 targets con un módulo mínimo (sugerido: `idea_log`).

## Varianza por entorno (verificada empíricamente)

| Aspecto | odoo.sh | staging privado | docker local (patrón) |
|---|---|---|---|
| Crear DBs | ❌ solo la del build | ✅ CREATEDB | ✅ contenedor postgres |
| `test-clean` | reset `to install` + `-i` | dropdb+createdb+`-i` | dropdb+createdb+`-i` |
| Demo data | siempre en builds dev | inicialización DB nueva | inicialización DB nueva |
| Binario | wrapper `odoo-bin` | venv + `odoo-bin -c conf` | `docker compose exec` |
| Postgres | dedicado | **compartido: retry + `db_maxconn` bajo** | dedicado |

Detalle de la variante odoo.sh: `references/odoo-sh.md`.

## Trampas conocidas (verificadas 2026-08-28)

1. `-i` sobre módulo instalado = no-op (0 tests) → el mecanismo de
   "desde cero" es obligatorio en `test-clean`.
2. Builds dev gestionados pueden tener drift de schema (columna fantasma) →
   el antídoto es DB nueva/rebuild; `test-clean` real lo detecta.
3. En odoo.sh, `scp`/`sftp` fallan: transferir con `tar` por stdin/SSH.
4. `--workers 0` evita consumir slots del postgres compartido de otros
   tenants.

## Referencias

- `assets/Makefile.template` — base del contrato (placeholders).
- `assets/odoo-test.conf.template` — conf de test propia (no tocar la de
  plataforma en entornos gestionados).
- `references/odoo-sh.md` — implementación de referencia pública.
- `references/odoo-19-traps.md` — trampas de API Odoo 19 verificadas
  (`res.groups.privilege` / `<list>` y su relación con el drift de schema).
