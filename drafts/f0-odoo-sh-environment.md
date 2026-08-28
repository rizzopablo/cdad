# F0 — Entorno Odoo.sh (Discovery)

> Fase F0 del proyecto CDAD×Odoo. Sujeto: instancia de desarrollo odoo.sh.
> Verificado empíricamente por SSH el 2026-08-28 + FAQ oficial de odoo.sh.
> Doc público: sin identificadores de cuenta ni hostnames reales.

## Inventario del entorno

| Aspecto | Hallazgo |
|---|---|
| Usuario/shell | `odoo`@contenedor (sin root; shell restringido) |
| Odoo | 19.0, fuente en `~/src/odoo/` (+ `~/src/enterprise/`, `~/src/themes/`) |
| Wrapper | `odoo-bin` (en PATH, provisto por la plataforma) |
| Módulos propios | `~/src/user/` — git worktree del repo GitHub del proyecto |
| Python | 3.12.3 (system); deps Python vía `requirements.txt` por build |
| PostgreSQL | env preconfigurado: `PGDATABASE`, `PGUSER`, `PGHOST` → `psql` funciona directo |

## Restricciones verificadas (condicionan el contrato make)

1. **No se pueden crear bases de datos.** `CREATE DATABASE` → `permission denied`.
   Solo existe la DB de la instancia (`$PGDATABASE`). → `test-clean` NO puede
   implementarse como dropdb/createdb aquí.
2. **Los builds de desarrollo SIEMPRE se construyen con demo data.**
   Fuente: FAQ oficial de odoo.sh ("Development branches are always built with
   demo data installed... The point of the development branches is to run the
   unit tests."). → El gate "instalación con demo" se cumple por diseño del
   entorno; la demo data de dependencias también está presente.
3. **Sin paquetes de sistema** (no apt). Solo `requirements.txt` (se instalan
   por build). → Las herramientas de lint (pylint-odoo, oca-checks, pre-commit)
   deben instalarse como deps Python del proyecto o correr localmente fuera
   de la instancia.
4. **Builds dev/staging = 1 worker**; procesos long-running no soportados;
   workers idle pueden ser reciclados. → Las corridas de tests son jobs
   efímeros: `--stop-after-init` obligatorio, `--workers 0`.
5. **Postgres sin extensiones**; tablas+secuencias ≤ 10.000 por DB.
6. **Sin API de plataforma** para rebuilds programáticos (no planeada).
7. `ODOO_STAGE` (production|staging|dev) y `ODOO_VERSION` disponibles como
   env vars para que el código se adapte al entorno.

## Implicaciones para `make test*` en odoo.sh

| Target | Implementación en odoo.sh |
|---|---|
| `test` | `odoo-bin -d $PGDATABASE -u <module> --test-enable --stop-after-init --workers 0` |
| `test-one` | ídem + `--test-tags <mod>:<Clase>.<metodo>` |
| `test-clean` | `odoo-bin -d $PGDATABASE -i <module> --test-enable --stop-after-init --workers 0` — "limpio" = reinstalación del módulo desde cero (la única DB es la de la instancia; los tests usan savepoints, no ensucian) |

- La demo data ya está presente (política del entorno): el gate de demo queda
  ejercitado por `-i` sin config extra.
- **Dos caminos de verificación**: (a) loop rápido en shell (escribir en
  `~/src/user`, correr tests); (b) flujo real de plataforma: push al repo
  GitHub → rebuild → el build corre su propia batería. El skill make debe
  documentar ambos.
- `~/src/user` es un worktree: cambios directos se pierden en rebuild si no
  están pusheados a GitHub.

## Pendientes

- [ ] Verificar cómo la plataforma corre sus tests automáticos al rebuild
      (naming de build, dónde se ve el resultado) — fuente: doc odoo.sh.
- [ ] Definir dónde viven pylint-odoo/oca-checks/pre-commit en este entorno
      (opciones: requirements.txt del proyecto; o lint en máquina del dev).
- [ ] Flujo real push→rebuild: el repo GitHub del proyecto es privado y el
      acceso de push está en manos del owner (28 Ago 2026: sin acceso desde
      cuenta de trabajo; requiere colaborador o push del owner).

## Notas operativas del spike F2 (verificadas en vivo)

1. **Transferencia de archivos**: `scp`/`sftp` fallan (subsistema restringido);
   `tar czf - ... | ssh ... 'tar xzf -'` funciona.
2. **`-i` sobre módulo instalado es no-op** → `test-clean` resetea estado con
   `UPDATE ir_module_module SET state='to install'` antes de `-i`.
3. **Drift de esquema en builds dev**: columna `res_users_settings.color_scheme`
   NOT NULL sin default presente en la DB pero ausente del código (revisión
   distinta de `web_enterprise`). Rompe la creación de usuarios en tests.
   Workaround de spike: `ALTER TABLE ... SET DEFAULT 'light'` (descartable);
   solución de raíz: rebuild de plataforma.
4. **Módulo de ejemplo verde**: `idea_log` 7/7 tests con los 3 targets; demo
   data (3 registros) cargada por `test-clean`.
