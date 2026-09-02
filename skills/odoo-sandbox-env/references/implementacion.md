# odoo-sandbox — detalles de implementación del entorno

Complementa a `SKILL.md`. Acá va el "por qué" de las decisiones que un agente
puede necesitar entender cuando algo no se comporta como espera.

## Fila de varianza (formato de `odoo-make-env`)

| Aspecto | odoo-sandbox |
|---|---|
| Crear DBs | ✅ rol con `CREATEDB`; además **odoo-bin crea la DB si no existe** |
| `test-clean` | `dropdb` + `-i` (no hace falta `createdb`: lo hace odoo-bin) |
| Demo data | inicialización de DB nueva |
| Binario | `odoo-sandbox exec <inst> -- odoo-bin` (host) · `odoo-bin` (dentro) |
| Postgres | **externo y típicamente compartido** → `--workers 0`, preflight de slots |

## Aislamiento: qué ve una instancia

- Rootfs **RO compartida por versión** de Odoo (una sirve a todas sus instancias).
- `$DATA` de la instancia bindeado **RW** en `/home/odoo/data`.
- Repos de `--addons` bindeados RW bajo `/home/odoo/data/addons/<basename>`.
- Capa IA (`--ia`): `/opt/ai` RO desde la ai-rootfs compartida.
- **Nunca** se bindea el `$DATA` de otra instancia. Sin binds cruzados.
- Red del host: Odoo escucha un puerto por instancia; el ruteo es de un proxy
  externo. No se usa `unshare -n`.

## Por qué el sandbox necesita un PID namespace

El sandbox corre con `unshare -Urm --pid --fork` y monta un **procfs nuevo**
(`mount -t proc`). No es un detalle: sin un `/proc` usable, `psutil` no encuentra
su propio proceso y **Odoo no arranca en modo servidor** (`init`, `run`, `update`
mueren con `NoSuchProcess`). Un `mount --bind /proc` no funciona ahí — falla con
"wrong fs type" contra la base remontada RO.

Consecuencia práctica para un agente: si ves `NoSuchProcess` de psutil, la rootfs
es vieja; reconstruíla.

## Por qué un symlink no sirve para conectar addons

El destino del symlink (`/home/usuario/repos/...`) **no existe dentro del chroot**.
El sandbox ve el link y no el contenido:

```
host:    addons/repo -> /home/usuario/repos/cliente-x     (ok)
sandbox: ls /home/odoo/data/addons/repo/ -> No such file or directory
```

Por eso `create --addons` hace un **bind mount** real.

## `odoo-bin` dentro del sandbox

El `odoo-bin` del source tiene shebang `#!/usr/bin/env python3` → python del
**sistema**, que no tiene las dependencias de Odoo (están en un virtualenv). La
rootfs incluye un shim en `/usr/local/bin/odoo-bin` que ejecuta el python del venv,
para que sea invocable como cualquier binario — desde un Makefile, un script o el
agente que trabaja dentro de una `--ia`.

## Tests de addons del core

El build **poda los directorios `tests/` de los addons** del core para reducir
tamaño (`--keep-tests` los conserva). **`odoo/tests/` — el framework — siempre se
preserva**; sin él ningún test corre.

Los addons del cliente viven en `$DATA/addons`, fuera de la rootfs: sus tests
nunca se ven afectados por la poda.

## Higiene de PostgreSQL

- Los nombres de base de test suelen usar el prefijo del proyecto; borralas al
  terminar. Una suite que no hace teardown deja decenas de bases.
- Un `make` que hizo timeout deja `odoo-bin` reteniendo conexiones. Antes de
  culpar al servidor: `make kill-orphans` o `odoo-sandbox stop <inst>`.
- Para diagnosticar quién consume slots:
  `psql -d postgres -c "select count(*), usename, datname from pg_stat_activity group by 2,3 order by 1 desc"`

## Límites conocidos

- **LXC unprivileged**: es la premisa de arquitectura del proyecto pero **no está
  verificada** end-to-end.
- **WSL**: sin verificar. Comprobalo con
  `unshare -Urm --map-root-user id` y `cat /proc/sys/user/max_user_namespaces`.
- `--tar` / `--deploy` a un host remoto: sin probar en real.
