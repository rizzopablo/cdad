# Fb — Contrato común `make` (extraído de F2 odoo.sh y F3 staging privado)

> Entregable de la fase Fb del proyecto CDAD×Odoo. Publico (sin referencias
> privadas). Resultado: el contrato que el skill make-env y los agentes
> CDAD-Odoo deben exigir, más la tabla de varianza por entorno.

## El contrato (3 targets, semántica fija)

| Target                          | Semántica (invariable entre entornos)                                        | Evidencia exigida                                   |
| ------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------- |
| `make test`                       | Suite completa del módulo sobre DB caliente                                   | resumen final verde: `0 failed, 0 error(s)`           |
| `make test-one TEST=mod:Clase.met` | Un único test (para RED)                                                       | resumen `0 failed, 0 error(s) of 1 tests`             |
| `make test-clean`                 | **Instalación del módulo desde cero + suite** (semántica común; mecanismo varía) | instalación OK + suite verde + demo data cargada     |

**Reglas del contrato:**
1. Los 3 targets deben existir con esos nombres exactos — es la interfaz que
   invocan los agentes CDAD-Odoo (test-writer usa `test`/`test-one`,
   implementer usa `test`/`test-clean`, reviewer usa `test-clean`).
2. `test-clean` = "instalación desde cero", no "dropdb/createdb": cada
   entorno resuelve "desde cero" con sus medios (ver tabla).
3. Corrida de tests SIEMPRE con `--stop-after-init --test-enable` y sin
   workers (`workers = 0` / `--workers 0`): jobs efímeros, mínimo consumo de
   conexiones.
4. Demo data: `test-clean` debe ejercitar la instalación CON demo (en
   odoo.sh es por política de plataforma; en el staging privado la DB nueva se inicializa
   con base+demo por defecto).
5. Evidencia = output pegado con la línea de resumen. Sin output no hay gate.
6. El Makefile vive en el repo del proyecto (versionado, revisable); las
   variables de entorno específicas se resuelven dentro de cada entorno.

## Varianza por entorno (lo que F2/F3 descubrieron)

| Aspecto                      | odoo.sh (F2)                                                    | staging privado (F3)                                     |
| ---------------------------- | --------------------------------------------------------------- | ------------------------------------------------------- |
| Crear DBs                    | ❌ solo `$PGDATABASE` (la del build dev)                          | ✅ `createdb`/`dropdb` (rol con CREATEDB)                |
| Mecanismo `test-clean`         | reset estado `to install` por SQL + `-i`                          | `dropdb` + `createdb` + `-i`                             |
| Demo data                    | SIEMPRE presente (política oficial de builds dev)               | se carga al inicializar la DB nueva (default Odoo)      |
| Binario odoo                 | wrapper `odoo-bin` en PATH, PG por env vars                     | `venv/bin/python3 <src>/odoo-bin -c odoo-test.conf`     |
| Config de test               | la del build (no se toca)                                        | `odoo-test.conf` propia (la de plataforma NO se edita)  |
| Concurrencia postgres        | dedicado al build                                               | **compartido multi-tenant, saturable** → retry + guard  |
| Seguridad/guard              | —                                                               | guard fail-closed: `instance.yaml` staging + db_name    |
| Riesgo operativo             | DB dev descartable (rebuild limpia todo, incluso drift de schema) | NUNCA tocar `<ruta-instancia>` (producción) ni otros dominios |

## Descubrimientos técnicos con impacto en el contrato

1. **`-i` sobre módulo instalado es no-op** (0 tests). El mecanismo de
   "reinstalar" debe ser explícito por entorno (ver tabla).
2. **Drift de esquema** posible en builds dev gestionados (columna fantasma
   NOT NULL): el antídoto real es el rebuild/DB nueva — `test-clean` con DB
   fresca es el gate que detecta estos estados.
3. **Postgres compartido** (staging privado): el make debe tolerar "connection slots"
   con retry y fallar cerrado; `db_maxconn` bajo en la conf de test es
   cortesía con los demás tenants.
4. **`Form` requiere `web`** y **tests que crean usuarios** dependen del
   estado del schema — lecciones para el skill del test-writer, no del make.

## Qué hereda F1 de este contrato

- Los agentes CDAD-Odoo invocan SOLO estos targets (allowlist bash `make *`).
- El skill make-env publica `Makefile.template` + `odoo-test.conf.template`
  con placeholders, y la tabla de varianza como guía para implementar un
  entorno nuevo.
- El gate de evidencia de cada etapa CDAD se define sobre las líneas de
  resumen de estos targets (`0 failed, 0 error(s) of N tests`).
