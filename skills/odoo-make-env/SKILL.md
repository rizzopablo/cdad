---
name: "odoo-make-env"
description: >
  Contrato make para ejecutar tests Odoo en proyectos CDAD (targets test /
  test-one / test-clean / lint) y guía para implementar el contrato en un entorno
  concreto (odoo.sh, staging privado, docker local, oca-ci). Usar cuando un proyecto
  Odoo debe exponer su runner de tests a los agentes CDAD-Odoo, o al crear
  el Makefile de un proyecto Odoo nuevo.
---

# odoo-make-env — contrato de ejecución de tests Odoo

**Principio:** CDAD define QUÉ se verifica (gates + evidencia); el proyecto
define CÓMO (Makefile versionado en el repo). Los agentes CDAD-Odoo invocan
solo los 4 targets — nunca comandos específicos de un entorno.

## El contrato (obligatorio, nombres exactos)

| Target | Semántica | Usado por |
|---|---|---|
| `make test` | suite completa sobre DB caliente | test-writer (AUDIT), implementer (GREEN) |
| `make test-one TEST=mod:Clase.metodo` | un solo test | test-writer (RED) |
| `make test-clean` | instalación del módulo desde cero + suite | implementer (gate GREEN), reviewer |
| `make lint` | lint del addon con `pre-commit-vauxoo` — `--diff` en desarrollo, `--all` para evidencia de gate | implementer (gate GREEN), reviewer |

**Reglas:**
1. `test-clean` = "instalación desde cero" — el mecanismo es libre por
   entorno (DB nueva si se puede; reset+`-i` si no).
2. Corridas SIEMPRE `--stop-after-init --test-enable` y sin workers
   (`workers = 0`): jobs efímeros, mínimo uso de conexiones.
3. `test-clean` ejercita la instalación CON demo data.
4. Evidencia = output pegado con la línea `0 failed, 0 error(s) of N tests`.
5. El Makefile es versionable y revisable — vive en el repo del proyecto.
6. `make lint` invoca el lint pinneado `uvx pre-commit-vauxoo==8.3.18` y
   SIEMPRE con `--no-overwrite`: la bootstrap de configs de pre-commit es
   decisión del proyecto, nunca del agente. Autofixes deshabilitados
   (default del tool).
7. El lint corre en host, no dentro del runtime del entorno de tests; la
   primera corrida requiere red (clona los repos de hooks).
8. Evidencia de lint = output de `make lint --all` pegado, con `0`
   bloqueantes.

## Cómo implementar un entorno nuevo

**Paso 0 — ¿hay un entorno ya resuelto instalado?** Este skill no depende de
ninguno en particular, pero si uno está disponible, usarlo es más rápido y
más confiable que fabricar el Makefile a mano.

Buscá, en este orden:

1. Un skill de entorno instalado (convención: `<algo>-env`, p.ej.
   `odoo-sandbox-env`) — su `description` declara cuándo aplica. Si hay uno y
   aplica a este proyecto, **cargalo primero** y seguí su guía: ya trae el
   Makefile verificado, dos veces más rápido que fabricar el propio.
2. Si no hay ninguno, el binario del entorno podría estar igual disponible sin
   el skill (p.ej. `command -v odoo-sandbox`). Poco común, pero revisalo.
3. **Nada de lo anterior → procedimiento genérico** (lo que sigue). Es el
   camino que siempre funciona, para cualquier entorno, con o sin skill
   dedicado.

### Procedimiento genérico (sin entorno dedicado)

1. Copiar `assets/Makefile.template` al repo del proyecto.
2. Resolver las 4 variables: binario odoo, config, DB de test, mecanismo de
   "desde cero".
3. Ver tabla de varianza (abajo) para entornos conocidos.
4. Agregar retry si el postgres es compartido (patrón `run_odoo` del
   template de staging privado, en referencias privadas de ese entorno).
5. Verificar los 4 targets con un módulo mínimo (sugerido: `idea_log`).

## Varianza por entorno (verificada empíricamente)

| Aspecto | odoo.sh | staging privado | docker local (patrón) | odoo-sandbox (si está instalado) |
|---|---|---|---|---|
| Crear DBs | ❌ solo la del build | ✅ CREATEDB | ✅ contenedor postgres | ✅ CREATEDB (u `odoo-bin` la crea sola) |
| `test-clean` | reset `to install` + `-i` | dropdb+createdb+`-i` | dropdb+createdb+`-i` | dropdb+`-i` (Makefile provisto) |
| Demo data | siempre en builds dev | inicialización DB nueva | inicialización DB nueva | inicialización DB nueva |
| Binario | wrapper `odoo-bin` | venv + `odoo-bin -c conf` | `docker compose exec` | `odoo-sandbox exec ... -- odoo-bin` (host) u `odoo-bin` directo (dentro de una instancia) |
| Postgres | dedicado | **compartido: retry + `db_maxconn` bajo** | dedicado | típicamente compartido: preflight de conexiones incluido |

Detalle de la variante odoo.sh: `references/odoo-sh.md`. odoo-sandbox trae su
propia guía en su propio skill (`odoo-sandbox-env`, si está instalado) —
deliberadamente no vive acá: es un entorno más entre varios posibles, y
CDAD/este skill no dependen de él.

## Trampas conocidas (verificadas 2026-08-28)

1. `-i` sobre módulo instalado = no-op (0 tests) → el mecanismo de
   "desde cero" es obligatorio en `test-clean`.
2. Builds dev gestionados pueden tener drift de schema (columna fantasma) →
   el antídoto es DB nueva/rebuild; `test-clean` real lo detecta.
3. En odoo.sh, `scp`/`sftp` fallan: transferir con `tar` por stdin/SSH.
4. `--workers 0` evita consumir slots del postgres compartido de otros
   tenants.
5. **DB fresca + `-i` corre los tests at_install de TODAS las dependencias
   (incluidos los de `base`, como `HttpCase`, que abren conexiones HTTP
   adicionales).** En postgres compartido esos tests cuelgan. Fix: acotar
   `test-clean` con `--test-tags $(MODULE)` para correr solo los tests del
   módulo (la instalación de dependencias sigue ocurriendo; solo se filtran
   sus tests).
6. **Procesos odoo-bin huérfanos retienen conexiones postgres** y pueden ser
   la causa real de "sin slots" (un `make` que hizo timeout deja el `odoo-bin`
   pegado en `connect`). Antes de reintentar: `ps -eo pid,cmd | grep odoo` y
   matar los huérfanos del runner (NUNCA los de la instancia de plataforma).
   Un huérfano pegado es peor que un reintento fresco.
7. **Evitá macro de retry sobre `odoo-bin`**: agrega complejidad (y bugs de
   escaping `$$`) sin resolver la causa raíz. Preferí comandos directos; el
   retry de slots, si existe, debe ser mínimo (solo `createdb`).

## Referencias

- `assets/Makefile.template` — base del contrato (placeholders).
- `assets/odoo-test.conf.template` — conf de test propia (no tocar la de
  plataforma en entornos gestionados).
- `references/odoo-sh.md` — implementación de referencia pública.
- `references/odoo-19-traps.md` — trampas de API Odoo 19 verificadas
  (`res.groups.privilege` / `<list>` y su relación con el drift de schema).
