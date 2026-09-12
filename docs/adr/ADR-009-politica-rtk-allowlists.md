# ADR-009 — Política de allowlists rtk: pares `X*` + `rtk X*` por rol, denies de subcomandos peligrosos

**Fecha:** 2026-09-12  
**Status:** **Proposed** (pasa a **Verified** tras los probes post-restart de cdad-010 desde sesión primaria)  
**Contexto:** Feature `cdad-010-opencode-permissions` (P4): los modelos del workspace envuelven comandos en `rtk`, rompiendo las allowlists de bash por patrón de los agentes `cdad-*`.

---

## Problema

Los modelos del workspace envuelven comandos en `rtk` (proxy CLI que filtra y
comprime output; convención del workspace, documentada en AGENTS.md). Las
allowlists por patrón del frontmatter de los agentes (`bash: {"pytest*": allow, "*": deny}`)
**no matchean el wrapper**: `pytest*` ≠ `rtk pytest*`.

Evidencia en logs (probe 2026-09-12, spec cdad-010): `evaluated permission=bash
pattern="rtk pytest --version" action.pattern=* action.action=deny` — el
test-writer no pudo correr `pytest --version` porque el modelo lo envolvió en
`rtk` y el matcher cayó al catch-all deny.

Resultado: fricción constante (todo comando allowlisteado falla cuando el
modelo lo envuelve) o presión a abrir el catch-all, que es exactamente lo que
la política no permite.

## Opciones consideradas

### Opción A: No allowlistear rtk (dejar el envoltorio fuera)

- Los agentes permiten `pytest*` y el modelo aprende a no usar `rtk`, o cada
  uso de `rtk X` cae en deny.
- Desventaja: fricción constante — el envoltorio `rtk` es la convención por
  defecto del workspace; cada corrida de tests/compilación genera un deny y
  reintentos. Descartada.

### Opción B: `"rtk *": allow` catch-all

- Un solo patrón habilita cualquier uso de `rtk`.
- Desventaja: **fuga total**. `rtk` es un proxy genérico: `rtk read` lee
  `src/` (rompe el aislamiento test-writer ↔ src, AP-7), y `rtk err` /
  `rtk summary` ejecutan comandos arbitrarios (la fuga de ejecución se
  reproduce vía proxy). Descartada.

### Opción C: Pares `X*` + `rtk X*` por rol + denies explícitos de subcomandos peligrosos (ELEGIDA)

- Cada comando allowlisteado lleva su par: `"pytest*": allow` y
  `"rtk pytest*": allow` (en el stack que corresponda).
- Los subcomandos peligrosos de `rtk` se deniegan explícitamente, después del
  catch-all (semántica findLast: la última regla que matchea gana).
- La matriz de pares por stack la genera `scripts/cdad-bash-allowlist.sh`.

## Decisión

**Opción C**, con cuatro puntos:

1. **Pares por comando allowlisteado:** toda entrada `X*: allow` de bash lleva
   su par `rtk X*: allow` (por rol, según el stack detectado por el generador
   `cdad-bash-allowlist.sh`).
2. **`rtk err*` / `rtk summary*: deny` en TODOS los roles** — ejecutan
   comandos arbitrarios vía proxy (fuga de ejecución).
3. **`rtk read*` / `rtk grep*` / `rtk find*` / `rtk diff*: deny` en roles
   write-capables (test-writer, implementer + variantes odoo)** — la fuga B1
   (leer `src/` saltándose el path-scoping) se reproduce vía proxy; **allow en
   los roles lectores** (architect, reviewer, scribe + variantes odoo), donde
   leer `src/` es legítimo.
4. **`rtk git *: deny` en TODOS los roles** (AP-17 vía proxy — hallazgo AUDIT
   3.1: `rtk git push` es commit/push mutante saltándose las reglas
   específicas de git). Git queda siempre acotado a subcomandos explícitos
   (`git diff*`, `git log*`, `git status*`, `git blame*`, `git add *`,
   `git commit*`); nunca `git *: allow`, nunca `rtk git *: allow`.

## Razones

### Por qué no basta el catch-all deny

Sin los pares, cada comando permitido falla la primera vez que el modelo lo
envuelve en `rtk` (evidencia del probe: `rtk pytest --version` denegado). Con
los pares, el comando legítimo pasa por las dos vías, y el riesgo se acota a
los subcomandos de `rtk` que de verdad son peligrosos, denegados uno por uno.

### Por qué el catch-all sigue cerrado

La política general del proyecto es default-deny explícito con catch-all
primero (findLast). `rtk` es el wrapper más obvio para intentar evadir una
allowlist por comando: cualquier fuga de `rtk *: allow` es una fuga de todo el
esquema. Los denies explícitos de los puntos 2-4 cubren los vectores conocidos
hoy; un vector nuevo se agrega con su deny cuando se detecta.

## Consecuencias

### Positivas

- Los comandos del stack corren igual con o sin envoltorio `rtk` — cero
  fricción para el uso normal.
- La matriz es generada por `scripts/cdad-bash-allowlist.sh` según el stack
  detectado en la máquina destino (go/pytest/node/deno/cargo/ruby/make...);
  el repo conserva el default agnóstico (`make *` + navegación git/ls).
- Un subcomando de `rtk` nuevo y peligroso queda cubierto por el catch-all
  deny mientras nadie agregue `rtk *: allow` — y el validador
  (`run-checks.sh` A3) assertiona esa prohibición (`rtk *: allow` y
  `rtk git *: allow` prohibidos; `rtk err*`/`rtk summary*: deny` requeridos).

### Negativas

- Duplicación de entradas (`X*` + `rtk X*`): las allowlists crecen ~2x.
- Mantenimiento acoplado a los subcomandos de `rtk`: si `rtk` agrega un
  subcomando que ejecuta arbitrario bajo otro nombre, hay deny nuevo que
  agregar (vigilancia manual, no estructural).

## Trade-offs Explícitos

| Aspecto | Con pares (C) | Con catch-all (B) |
|---------|---------------|-------------------|
| Fricción de uso | Baja | Cero (pero...) |
| Fuga de lectura `src/` vía `rtk read` | Cerrada (deny en write-capables) | Abierta |
| Ejecución arbitraria vía `rtk err`/`rtk summary` | Cerrada (deny en todos) | Abierta |
| Git vía proxy | Cerrado (`rtk git *: deny`) | Abierto (AP-17) |
| Superficie de mantenimiento | Pares por stack (generados) | Un patrón (pero toda la garantía perdida) |

## Verificación

1. **Estática** (`run-checks.sh` A3/A4/A6): `rtk err*`/`rtk summary*: deny` en
   TODOS; `rtk read*`/`grep*`/`find*`/`diff*` deny en write-capables y allow
   en lectores; prohibición de `rtk *: allow` y `rtk git *: allow`.
2. **Empírica (probes post-restart, sesión primaria, VALIDATION.md de
   cdad-010)**: `rtk pytest --version` PERMITIDO en test-writer/implementer
   (con pytest en stack); `rtk read`/`rtk err`/`rtk summary`/`rtk git log`
   DENEGADOS según la matriz.

**Criterio de aceptación:** ambos niveles verdes (asserts estáticos PASS +
probes con output pegado).

---

## Referencias

- `docs/epics/epic-002-cdad-audit-fixes/` — findings del epic (002-009
  bash-allowlist-hardening: primera calibración de allowlists por rol).
- `docs/activeContext.md` — entry 2026-09-04 (tests colocados: patrones
  reutilizados por la blocklist de implementer).
- `docs/specs/cdad-010-opencode-permissions/spec.md` — P4 (política rtk por
  rol) y P6 (documentación).
- `scripts/cdad-bash-allowlist.sh` — generador de la matriz por stack.
- `docs/systemPatterns.md` — convención de pares rtk + orden findLast.
- `docs/specs/cdad-010-opencode-permissions/test-audit.md` — AUDIT 3.1
  (hallazgo AP-17 vía proxy: `rtk git push` mutante).
