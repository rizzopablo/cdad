# Verificación del paso habilitante V2-1 (supervisión proporcional)

- Fecha: 2026-10-30 (UTC del entorno).
- Autor: orquestador supervisor delegado (sesión subagente), mandato HITL vigente
  `docs/epics/epic-010-documentary-specialization/execution.md`.
- Objeto verificado: `affd5fea` (`feat: make the POST-AUDIT packet instruction single-subphase (V2-1)`),
  packet `010-004-packet-dispatch-ergonomics-implementer-green-001`, intento de continuidad 16,
  recibo `de4517d1d96f0798d79efa9c687c1c430a1d8adf1d3fd48a795ca20e6b0b38ae`
  (`semantic_status: pending` — recibir no aprueba).
- Informe del rol: `docs/specs/010-004-packet-dispatch-ergonomics/v2-1-implementation-report.md`
  (`6bcfe39b5ef7f953add2103ce080b66d953a3ac3157f7eef4b2146412a9c2e74`, bytes idénticos al FINAL TEXT).

Contratos citados, sin restarlos:

- `spec.md` `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64` (intacto).
- `plan.md` `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685` (intacto).
- `owner-decision-plan-v2-1.md` `8f1810ba6cdd212f97b5236bd27b0a234c8ba0e0c4f6846b240df0a455a79c2d`
  (opción (a): plantilla POST-AUDIT mono-subfase **y su generación**, incluida la publicación
  de la skill instalada «en lo que sea necesario para que el paquete POST-AUDIT emitido
  contenga esa instrucción mono-subfase»).

## Criterio aplicado

Se verifican los cuatro puntos del encargo —(a) la plantilla ya no pide RED, (b) el bloque
estático compuesto sigue bajo el límite, (c) `make staging`/`make agents` producen derivados
deterministas y sin la instrucción vieja, (d) no se tocaron `spec.md`, `plan.md` ni `tests/`—
y se añade (e) **efectividad en la superficie de emisión**, porque es la promesa que V2-1
existe para cumplir y el plan ya la exige: «Un render que aún combine subfases se devuelve al
orquestador para resolver la contradicción antes de despachar; no se parchean sus bytes»
(`plan.md:38`).

Verificación proporcional: lectura, composición en memoria y ejecución local de los
entrypoints declarados (`make staging`, `make agents`, `install.sh --check`). No se ejecutó
trabajo de rol: no se editó plantilla, renderer, tests ni producto.

## Resultado (a) — plantilla POST-AUDIT ya no pide RED: **PASS**

`skills/cdad-cycle/packets/substages/test-writer-post-audit.md`
`d709f82ab040444426ce2d78630b367b8d083b4a42b189735a5a7896187be4de` (583 B) ordena aplicar
solo los cambios auditados y aprobados sobre tests EXISTENTES, verificar que los declarados
intactos siguen pasando, separar la evidencia de actualizados e intactos y detenerse; prohibe
escribir tests nuevos, iniciar RED, implementar y correr la suite completa.

```
compuesto (repo)  «then add contract-mapped RED tests»: 0
                  «contract-mapped»: 0
                  «Do NOT write new tests»: 1
                  «Then stop: this is ONE subphase»: 1
```

Control positivo conservado: `substages/test-writer-red.md`
`3dfd2985df0b3bd1a83e5ed4d082489ae24f094793ee432cb5e737df77ab8859` sigue exigiendo un test
que falle por la aserción esperada.

## Resultado (b) — bloque estático bajo el límite: **PASS**

Composición con el mismo orden y separador que `render_packet`
(`cdad_packet.py:1780-1783`: `common.md` + `\n` + `roles/test-writer.md` + `\n` +
`substages/test-writer-post-audit.md`), sin tocar `CDAD_STATIC_BLOCK_LIMIT`:

| Origen del asset root | bytes | límite | veredicto |
|---|---|---|---|
| repo `skills/cdad-cycle/packets` | 1768 | 12000 | PASS |
| instalado `~/.config/opencode/skills/cdad-cycle/packets` | 1368 | 12000 | PASS |

## Resultado (c) — derivados deterministas y sin la instrucción vieja: **PASS**

```
make staging  (dos corridas)  -> 23 archivos, sha256 idénticos entre corridas
make agents                   -> sin cambios en agents/ (git status --porcelain -- agents/ vacío)
grep -rl "then add contract-mapped RED tests" build/ agents/ .opencode/agents/  -> sin coincidencias
```

Generación solo por los entrypoints reales del Makefile; ninguna copia derivada fue parcheada.

## Resultado (d) — spec, plan y tests intactos: **PASS**

```
git show --name-status affd5fea
M skills/cdad-cycle/packets/substages/test-writer-post-audit.md
M skills/cdad-cycle/references/handoff-prompts.md
archivos bajo tests/ en el commit: 0
sha256 spec.md = fc6b2ccc… (pin íntegro)
sha256 plan.md = 2ae8ada3… (pin íntegro)
```

## Resultado (e) — efectividad en la superficie de emisión: **FAIL (defecto D-1)**

El paquete que se despacha no se compone desde el repo: el renderer resuelve su asset root
desde su propia ubicación (`_asset_root()` = `Path(__file__).parents[1]`, `cdad_packet.py:1773`)
y el orquestador de esta ejecución usa el CLI instalado
(`~/.config/opencode/skills/cdad-cycle`, verificado en el `skill` tool de la sesión
padre). Esa copia conserva la instrucción vieja:

```
instalado  packets/substages/test-writer-post-audit.md = 041f1a8ce2a4d48d4e1ab9bab8623dcbc90d019adb0017fc948566d836825a37
repo       packets/substages/test-writer-post-audit.md = d709f82ab040444426ce2d78630b367b8d083b4a42b189735a5a7896187be4de
instalado  references/handoff-prompts.md              = 0b34e22deb3eb54b6d802ddc3a9a7eaeabebc67da2fcb50f814f6dbe3191782a
repo       references/handoff-prompts.md              = 3262048cb3c98b325a3224243ac526740db67a3f9b0696c824d8dda96e7dff70

compuesto (instalado)  «then add contract-mapped RED tests»: 1
                       «contract-mapped»: 1
                       «Do NOT write new tests»: 0
                       «Then stop: this is ONE subphase»: 0

install.sh --check  ->  DRIFT: differs …/skills/cdad-cycle/packets/substages/test-writer-post-audit.md
                        DRIFT: differs …/skills/cdad-cycle/references/handoff-prompts.md
                        (en las tres destinaciones: .config/opencode, .agents, .claude)
```

Consecuencia medida: un `prepare` del substage `post-audit` con el CLI instalado emite un
paquete que **combina POST-AUDIT + RED**, contra INV-01 y contra `plan.md:38`; y prepararlo
con el CLI del repo no es una salida, porque la admisión de la frontera re-renderiza con el
asset root instalado (`cdad_dispatch.py:503-514` → `verify_published_packet`,
`cdad_packet.py:1948-1959`) y rechazaría el paquete por diferencia de bytes antes del
transporte. Ningún paquete POST-AUDIT despachable puede portar V2-1 hasta sincronizar la
skill instalada.

### Defecto D-1 (registrado, no reparado)

**Causa raíz:** inconsistencia de alcance en la orquestación, no en el trabajo del rol. La
decisión owner V2-1 incluye explícitamente la generación —«la publicación de la skill
instalada (`install.sh`, copias por archivo a los runtimes) … para que el paquete POST-AUDIT
emitido contenga esa instrucción mono-subfase»— y el packet del implementer la excluyó
(«NO instalacion global, NO publicacion»). El implementer cumplió su packet y declaró la
diferencia («My two files were byte-in-sync … and now appear as drift»).

**Radio de impacto medido (segunda cara de D-1):** `prepare` no sólo compone el paquete,
también republica los agentes derivados del proyecto desde las fuentes **instaladas**
(`_derived_source_dir` → `.cdad/activation.json` o `~/.config/opencode/agents`;
`cdad_packet.py:4230-4247`, publicación dentro de la transacción de `prepare`). Al preparar
este packet (13:42:32) se reescribieron `.opencode/agents/*.md` desde esa fuente: el agente
derivado `cdad-test-writer.md` quedó en 15 017 B frente a los 16 548 B del agente del repo.
El packet no se ve afectado (la instrucción de subfase viaja en el paquete), pero el elenco
de subagentes hereda la revisión instalada: publicar la skill refresca también esa fuente.

**Contexto preexistente:** el drift es sistémico y anterior (F011 falla ya en un checkout
limpio; los scripts instalados son más viejos que el repo: `cdad_packet.py` instalado
`171fcd1413ec8446272564388fe2165716569e6c3c070f02f4dca8008960e679` vs repo
`64f739e9c341117bdfc7c12b8eabe0af4fdd3bbdaca5e20dd7ef46452215e94c`). V2-1 no lo creó; lo
hace visible porque su efecto depende de la copia instalada.

## Decisión tomada (con fundamento)

1. **No se repara inline.** El orquestador no ejecuta trabajo de rol, y la publicación de la
   instalación global no está autorizada por la autoridad vigente:
   `docs/epics/epic-010-documentary-specialization/execution.md:18-19` («No hay push,
   publicación ni modificación de instalaciones globales autorizados por este mandato») y
   `:32` («Cambios reales de alcance y publicación se elevan al dueño»); el mandato HITL lo
   repite (`owner-mandate-hitl-2026-10-30.md:64-66`). La instrucción literal del dueño que
   registra V2-1 es «Corregir plantilla en el plan»: la publicación instalada no forma parte
   de esas palabras, así que **se eleva al dueño** en lugar de ejecutarse por delegación.
2. **El packet POST-AUDIT de T2 se prepara, con el renderer del repo** (fuente corregida),
   no con el instalado, porque sólo la fuente corregida emite la instrucción mono-subfase que
   `plan.md:38` y INV-01 exigen. Artefacto:
   `.cdad/packets/010-004-packet-dispatch-ergonomics-test-writer-post-audit-001` (12 180 B,
   `b637c957d338dac1ceeebf6493506611bb2c94befa2a0d6074b13d799573bfe6`), objetivo y
   invariantes de POST-AUDIT (aplicar sólo los cambios auditados y aprobados, verificar
   intactos, evidencia separada, sin tests nuevos, sin RED, sin implementación, sin suite
   completa, traza PD-12 → decisión owner → §7/PC-04).
3. **El packet es exactamente el que emitiría una instalación publicada.** Se midió: copiando
   únicamente `packets/substages/test-writer-post-audit.md` sobre una copia de la skill
   instalada (`/tmp/opencode/installed-sim`, fuera del runtime), ese CLI instalado renderiza
   el mismo paquete **byte a byte** (`cmp` vacío contra `PACKET.md`).
4. **Precondición de admisión declarada, no silenciada.** Bajo el CLI instalado actual el
   paquete es rechazado con `ERROR: packet differs from canonical rendering` (el asset root
   instalado sigue combinando subfases); `validate-request` y `validate-state` sí pasan con el
   CLI instalado. Rutas válidas, en este orden de preferencia:
   - **A (sin mutación global):** preparar/validar/registrar este paquete con los scripts del
     repo (`skills/cdad-cycle/scripts/…`). `cdad_dispatch.py` y `cdad_result.py` son
     byte-idénticos a los instalados; `cdad_packet.py` y `cdad_continuity.py` difieren sólo en
     la canonicalización de raíz de 010-000 (no-op con raíz absoluta).
     > **Afirmación histórica superada (2026-10-30, revisión T6 de 010-004).** Esta
     > comparación era cierta al escribirse y ya no lo es: con el producto de 010-004 el
     > módulo del repo diverge además en la emisión de ruta C, el localizador
     > `execution_context`, la validación v2-only de la preparación y el diagnóstico de
     > bloqueo v1. Medido hoy: repo `44a950a5…48fe54`, instalación `171fcd14…60e679`. El
     > límite vigente —«cerrada en repo, NO vigente en la instalación»— está fijado en
     > `closure-conditions.md:§1`.
   - **B (cauce canónico):** el dueño autoriza la publicación mínima de las dos fuentes
     cambiadas y, desde ese momento, el paquete se valida y despacha con el CLI instalado sin
     regenerarlo (probado byte-idéntico en el punto 3).
5. **El re-dispatch de publicación queda especificado y no preparado.** No se prepara un
   packet que autorice publicar: la autoridad para publicar es del dueño y fabricarla sería
   inventar autoridad. Queda listo el objetivo exacto para emitirlo en cuanto el dueño lo
   instruya (sólo las dos fuentes, copia por archivo byte-idéntica a las tres destinaciones,
   sin `install.sh` completo —que además reescribiría scripts y agentes drifted, radio de
   impacto ajeno a V2-1—, y verificación con el asset root instalado).

## Pendiente declarado

- **Decisión del dueño (bloqueante del cauce canónico):** autorizar la publicación mínima de
  `skills/cdad-cycle/packets/substages/test-writer-post-audit.md` y
  `skills/cdad-cycle/references/handoff-prompts.md` en `.config/opencode`, `.agents` y
  `.claude`. Hasta entonces V2-1 no está en vigor para el CLI instalado.
- Publicación completa de la skill instalada (drift F011 preexistente: scripts y agentes):
  decisión de mantenimiento del owner, fuera del alcance de 010-004.
- Si se elige la ruta A, el paquete ya preparado se despacha con el toolchain del repo; si se
  elige la ruta B, el mismo paquete se valida con el CLI instalado tras la publicación
  (mismos bytes, sin regenerar).
