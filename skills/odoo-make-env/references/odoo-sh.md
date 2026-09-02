# Variante odoo.sh del contrato make (referencia pública — verificada 2026-08-28)

> Implementación de los 4 targets en una instancia dev de odoo.sh. `make lint`
> corre en host (no dentro del runtime de la instancia — ver sección Lint).
> Sin identificadores de cuenta: placeholders `<instance>` / `<project>`.

## Características del entorno (FAQ oficial + verificación empírica)

- Una sola DB por build: `$PGDATABASE` (PG preconfigurado por env vars).
  **No se pueden crear DBs** (`CREATE DATABASE` → permission denied).
- Los builds dev **siempre** incluyen demo data (política oficial) → el gate
  de demo queda ejercitado sin configuración extra.
- Sin apt; deps Python por `requirements.txt` (instaladas por build).
- Builds dev/staging = 1 worker; procesos long-running no soportados.
- `~/src/user` = worktree del repo GitHub del proyecto. `scp` falla; usar
  `tar` por stdin/SSH. Cambios directos se pierden en rebuild si no están
  pusheados.
- Drift de schema posible en builds dev (columna fantasma NOT NULL):
  el antídoto es el rebuild de plataforma.

## Makefile verificado

```makefile
MODULE ?= <module>
DB ?= $(PGDATABASE)

.PHONY: test test-one test-clean lint

test:
	odoo-bin -d $(DB) -u $(MODULE) --test-enable --stop-after-init --workers 0 --max-cron-threads 0 --log-level=test

test-one:
	@test -n "$(TEST)" || (echo "Requerido: TEST=modulo:Clase.metodo" && exit 1)
	odoo-bin -d $(DB) -u $(MODULE) --test-enable --test-tags $(TEST) --stop-after-init --workers 0 --max-cron-threads 0 --log-level=test

test-clean:
	psql -q -c "UPDATE ir_module_module SET state='to install' WHERE name='$(MODULE)';"
	odoo-bin -d $(DB) -i $(MODULE) --test-enable --stop-after-init --workers 0 --max-cron-threads 0 --log-level=test

# make lint corre en HOST (no en la instancia): el lint es estático, sin deps
# de plataforma. Pin según contrato odoo-make-env; --all para evidencia de gate.
lint:
	uvx pre-commit-vauxoo==8.3.18 run --no-overwrite --diff
```

Notas:
- `test-clean` aquí NO crea DB (imposible): "desde cero" = reset de estado +
  reinstalación. El clean total (DB nueva) lo da el **rebuild de plataforma**
  en cada push.
- No usa `-c`: el wrapper `odoo-bin` de la plataforma resuelve la config.

## Dos caminos de verificación

1. **Loop rápido (shell)**: escribir en `~/src/user` (tar|ssh), correr los 3
   targets.
2. **Flujo real (plataforma)**: push al repo GitHub → el build corre su
   batería automática → resultado en la UI del proyecto. Requiere acceso de
   push al repo (deploy keys/submodules según FAQ oficial).

## Lint (pylint-odoo / oca-checks)

No disponibles en la instancia (sin apt; pip de la instancia no persiste).
Decisión verificada: correrlos en la **máquina del desarrollador** (venv de
tooling) — el lint es estático e independiente del entorno. La evidencia de
lint viaja con la feature (output pegado), no con el entorno.
