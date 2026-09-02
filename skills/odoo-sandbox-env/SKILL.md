---
name: "odoo-sandbox-env"
description: >
  Entorno de ejecución odoo-sandbox para proyectos CDAD-Odoo: runtime bwrap-style
  (unshare -Urm + chroot, sin Docker) que corre instancias Odoo aisladas sin root.
  Enseña cómo levantar cada tipo de instancia (staging, prod, clone, restore desde
  backup de cliente, dev con capa IA), cómo conectar el repo de addons del cliente,
  y cómo implementa el contrato `odoo-make-env` en sus DOS modos de ejecución
  (agente en el host vs. agente dentro de la instancia). Usar cuando el proyecto
  Odoo corre sobre odoo-sandbox — señal: existe el binario `odoo-sandbox` en el
  PATH, o el Makefile del proyecto lo invoca. Complementa a `odoo-make-env` (que
  define el contrato); este skill provee la implementación concreta del entorno.
---

# odoo-sandbox — entorno de ejecución para CDAD-Odoo

**Relación con `odoo-make-env`:** ese skill define **QUÉ** se verifica (los targets
`test` / `test-one` / `test-clean` y la evidencia). Este define **CÓMO** en un
entorno concreto, igual que `references/odoo-sh.md` lo hace para odoo.sh.
odoo-sandbox es un entorno más entre varios posibles (odoo.sh, deployv, docker,
oca-ci); este skill solo aplica **si odoo-sandbox está instalado**.

## Qué es

Runtime que corre Odoo aislado con `unshare -Urm --map-root-user` + `chroot`,
**sin Docker ni root**. Funciona donde los contenedores rootless no pueden (LXC
unprivileged, hosts sin subuids). Rootfs compartida RO por versión de Odoo; cada
instancia aporta su `$DATA` RW.

## Antes de nada: `doctor`

```sh
odoo-sandbox doctor
```

Verifica herramientas, user namespaces, PostgreSQL y disco, y **dice qué falta con
el comando exacto**. Correlo en una máquina nueva antes de cualquier otra cosa.

### Requisitos (declaración, no procedimiento)

Ya presentes en cualquier base Debian/Ubuntu (`Essential: yes`): `unshare`,
`chroot`, `tar`.

**Hay que instalar** (único paso privilegiado de todo el flujo):

```sh
sudo apt install -y curl jq git make postgresql postgresql-client
sudo -u postgres createuser -s "$USER"   # o un rol con CREATEDB
```

PostgreSQL es **externo**: odoo-sandbox nunca provisiona el motor. Todo lo demás
—build de la rootfs, instancias, Odoo, tests— corre **sin root**.

> Si el usuario no dio permisos para instalar, pedíselo o pedile que lo corra él.
> No hace falta enseñarle al agente a administrar el sistema: es un requisito.

## Levantar el entorno

```sh
scripts/build-rootfs.sh --version 19.0        # ~4 min, sin root
scripts/build-ai-rootfs.sh                    # solo para el modo (a), abajo
```

### Tipos de instancia

| Quiero… | Comando |
|---|---|
| Staging para trabajar | `create x --version 19.0` |
| Que además tenga base y esquema | `create x --version 19.0 --ensure-db` + `init x --version 19.0` |
| Producción | `create x --version 19.0 --env prod` |
| Staging neutralizado desde prod | `clone mi-prod mi-staging` |
| **Arrancar del backup de un cliente** | `restore x --version 19.0 --dump d.sql.gz --filestore ./fs` |
| Dev con agente adentro | `create x --version 19.0 --ia` |
| **Con el repo de addons del cliente** | `create x --version 19.0 --addons ~/repos/cliente-x` |

**`create` NO toca PostgreSQL por default** — es una operación de sistema de
archivos. `--ensure-db` garantiza la base; `init` carga el esquema; `clone` y
`restore` traen su propio esquema.

### Conectar el repo del cliente: `--addons`

```sh
odoo-sandbox create cliente-x --version 19.0 --addons ~/repos/cliente-x-addons
```

Bindea el repo **RW** en `/home/odoo/data/addons/<nombre>`: el usuario edita en su
repo git del host y el sandbox lo ve al instante. Repetible.

> **Nunca uses un symlink para esto.** Su destino (`/home/usuario/...`) no existe
> dentro del chroot: el sandbox ve el link pero no el contenido. Por eso existe
> `--addons`, que hace un bind real.

### Lazo diario

```sh
odoo-sandbox run x --version 19.0 --detach   # arranca y vuelve
odoo-sandbox status x                        # running/stopped; exit 0 si corre
odoo-sandbox logs x -f
odoo-sandbox restart x --version 19.0
odoo-sandbox stop x                          # sin dejar huérfanos
```

## El contrato `make`: DOS modos, un solo Makefile

| | (b) agente en el HOST | (a) agente DENTRO de una `--ia` |
|---|---|---|
| Invocación | `odoo-sandbox exec <inst> -- odoo-bin …` | `odoo-bin …` directo |
| Por qué | hay que entrar al sandbox | ya estás adentro; envolver anidaría sandboxes |
| El código entra por | `create --addons <repo>` | clonar el repo en `$DATA/addons` |

**El `Makefile` se autodetecta** con `ODOO_SANDBOX_NAME`, que el wrapper exporta
dentro del sandbox y no existe en el host. No mantengas dos.

```sh
make setup                          # instancia lista (DB + esquema)
make test-env                       # ¿entorno OK? correlo antes de empezar
make test-clean MODULE=mi_addon     # DB nueva + install + suite  (gate GREEN)
make test       MODULE=mi_addon     # suite sobre DB caliente
make test-one   MODULE=mi_addon TEST=mi_addon:Clase.metodo   # RED
```

Copiá el `Makefile` del repo de odoo-sandbox al repo del proyecto y apuntá al
binario: `make test ODOO_SANDBOX_BIN=/ruta/a/odoo-sandbox` (o ponelo en el `PATH`).

**Requisito de host para el contrato:** `psql` y `dropdb` (paquete
`postgresql-client`). Odoo y sus dependencias NO hacen falta en el host: corren
dentro del sandbox. `make test-env` lo verifica.

## Trampas verificadas (ninguna es deducible)

1. **`-u <mod>` sobre un módulo no instalado es no-op**: Odoo reporta
   `0 failed, 0 error(s) of 0 tests` con **rc=0** — un gate lo leería como verde
   habiendo corrido cero tests. Los targets lo guardan; no invoques `odoo-bin` a
   mano en un gate.
2. **PostgreSQL suele ser compartido** con instancias de producción del host. Usá
   siempre `--workers 0`. La suite hace preflight de conexiones y falla rápido
   (rc=2) en vez de colgarse (`OSX_MIN_PG_SLOTS`, `OSX_SKIP_PG_PREFLIGHT`).
3. **`odoo-bin` huérfanos** de un `make` que hizo timeout retienen conexiones y
   después aparecen como "sin slots": `make kill-orphans`, o usá `stop`.
4. **`chroot` vive en `/usr/sbin`**, fuera del PATH de un usuario común:
   `export PATH="$PATH:/usr/sbin"`. `doctor` lo detecta y lo dice.
5. **Crear un módulo nuevo**: `odoo-bin scaffold <mod> .` funciona dentro del
   sandbox (verificado).

## Evidencia que pide CDAD

```
odoo.tests.result: 0 failed, 0 error(s) of N tests when loading database '...'
```

Exit code 0 en verde, ≠0 si algo falla: sirve como gate real.

**Logs de corrida con nombre en `~/tmp/` (NUNCA `/tmp/`):** cada corrida de
gate deja su log con nombre referenciable (p.ej.
`~/tmp/gate-final-<feat>.log`). Eso habilita la reutilización de evidencia del
protocolo de presupuesto de corridas
(`odoo-make-env/references/run-budget-protocol.md`): el reviewer puede citar
`ruta:linea` en vez de re-corrida si el árbol de código no cambió. `/tmp/` es
efímero y por-proceso — un log ahí no es evidencia recuperable.

## Referencias

- `references/implementacion.md` — detalles internos del entorno y por qué.
- En el repo de odoo-sandbox: `docs/guia-de-uso.md` (guía completa),
  `AGENTS.md` (convenciones), `docs/adr/` (decisiones).
