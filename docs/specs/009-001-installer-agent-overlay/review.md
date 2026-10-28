# Review — 009-001 installer agent overlay

- **Fecha:** 2026-10-28
- **Contrato:** `docs/specs/009-001-installer-agent-overlay/spec.md` (sha256 `61caacb6…`)
- **Rango revisado:** `2ce4804^..HEAD` (`11cee10`) — el rango del paquete excluía `2ce4804`, que contiene el
  helper y el validador.
- **Veredicto:** **CAMBIOS REQUERIDOS** — 3 hallazgos bloqueantes, 1 opcional.

## Admisión (ruta A)

Paquete válido: `validate-packet` rc 0 y render canónico idéntico a `PACKET.md` y a los bytes recibidos.
Contrato y policy sha256 coinciden.

## Hallazgos bloqueantes

### F1 — Cambiar sólo el overlay produce conflicto: PC-1 falla y el agente deja de actualizarse (Critical, bucket h)

`install.sh:990-997`, `install.sh:1009-1012`, `install.sh:936-940`.

| Caso | Lo que dice install | Lo que dice `agent-overlay.py compare` |
|---|---|---|
| (a) El usuario cambia el modelo A→B, misma versión | `CONFLICT … modified outside the user-owned overlay`, owned: False, `--check` rc=1; en **ambos** destinos | `overlay-only: model=user/B` |
| (b) El usuario borra la línea `model:` (bytes == staging) | `CONFLICT … modified locally since the last install` | `identical` |
| (c) Copia que el instalador anterior (`87b8fe2`) ya había dejado en conflicto, luego upgrade a éste | `CONFLICT … unowned content at an owned destination differs from staging`, owned: False | `overlay-only: model=user/A` |

**Causa.** En (a) y (b) la única prueba aplicada es el digest registrado, que cubre los bytes **con el overlay
viejo** (PC-3), así que cualquier edición del overlay falla ambas comparaciones y nunca se compara contra el
staging vigente. En (c) el conflicto "unowned content" (`:1009`) ocurre **antes** de llamar a
`stage_user_overlay`, así que la rama `[ -z "$recorded" ]` (`:936`) nunca corre.

**Consecuencia.** Cambiar de modelo —la edición más común— congela el agente: deja de ser owned y de recibir
actualizaciones. (c) es exactamente la población del repro (paso 3): la feature no la repara al actualizar.
El mensaje "modified outside the overlay" es falso.

**Done when:** en (a), (b) y (c), en ambos destinos, install informa `SYNC` o redespliega sin `CONFLICT`, el
agente queda owned con digest de los bytes instalados y `--check` rc 0.

### F2 — El validador mantiene su propia copia de la lista de claves (Required, bucket h)

`scripts/validate-subagents.sh:206`.

`grep -c USER_OWNED_KEYS scripts/validate-subagents.sh` → `0`; el chequeo es un literal
`grep -q '^model:' "$f"`. Viola INV-2 («una sola definición de claves») y §2 (el validador debe consumir la
semántica del helper). Si se agrega una clave a `USER_OWNED_KEYS`, el validador deja de cubrirla en silencio;
además su semántica difiere (matchea en todo el archivo; el helper sólo en el frontmatter).

**Done when:** el validador no contiene el nombre de la clave y agregar una clave a la lista hace que rechace
esa clave en texto instalable.

### F3 — El resumen de `--check` sigue nombrando la ruta de staging (Required, bucket m)

`install.sh:2025`, `install.sh:2071`. En el caso (c) la salida termina con
`Check: FAIL — missing staged agents/opencode/cdad-reviewer.md`: el mismo mensaje que el repro marcó en el
paso 4. Sólo la línea por-archivo se movió a la ruta instalada; la entrada `problems+=("missing staged $srel")`
quedó igual. PC-6 lo prohíbe («nunca»).

**Done when:** la entrada del resumen nombra la ruta instalada de cada destino.

## Opcional

### O1 — "MISSING" para un archivo que existe (bucket m)

`install.sh:2019-2023`: una copia en conflicto no-owned se reporta como
`MISSING (staged but not installed): <ruta instalada>`, pero el archivo existe. "Presente pero no owned
(conflicto)" describiría el hecho.

## Observaciones

- **Sign-off de `462cedf`:** sólo cambia qué variante elige el fixture (opencode explícito, filtro por
  runtime); ninguna aserción cambió y corrige el desajuste reportado en `635babe`.
- **Lo que se sostiene:** ruta D4 intacta para ediciones fuera del overlay y para no-agentes; guard de
  symlinks primero; `--check` y validador read-only; PC-7 (uninstall preserva byte a byte); `merge` puro e
  idempotente; sin conflicto con ADR-033.
- **Formato:** `merge` escribe `model: <valor>` al final del frontmatter; el valor se conserva exacto, cambian
  posición y espaciado.

## Abstención

- No corrió la suite completa, `make validate` ni `./install.sh --check` de la instalación declarada: son del
  cierre.
- No reprodujo «cambio de modelo **y** cambio de staging en la misma actualización»: bajo §2/§8 obs 1 puede
  ser legítimamente «base no acreditable».
- No evaluó CRLF ni el prune de agentes obsoletos con overlay (`install.sh:1480-1487`): fuera de la spec.

## Evidencia

- Sin archivos modificados.
- `python3 -m unittest tests.test_009_001_installer_agent_overlay` → `Ran 7 tests in 153.255s — OK`.
- Casos (a)(b)(c) reproducidos en `/tmp/opencode/rv009/root{2,3,4}` con `CDAD_INSTALL_ROOT`.
- `python3 scripts/agent-overlay.py compare …` → `overlay-only: model=user/B` (ambos destinos) e `identical`.
- `grep -c USER_OWNED_KEYS scripts/validate-subagents.sh` → `0`.
