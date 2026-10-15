# ADR-020 — Una sola política de evidencia con dueño canónico y la procedencia de la instalación declarada en el artefacto publicado

* Estado: **Aceptado** (2026-10-09; orquestador bajo delegación HITL de epic-005)
* Fecha: 2026-10-09
* Decisores: orquestador bajo delegación HITL de epic-005 (aprobación del dueño, `execution.md`)
* Confianza: **Media**

## Contexto y enunciado del problema

005-005 es la **continuación correctiva de 005-001**: no agrega roles ni sub-modos, cierra
tres incoherencias que quedaron abiertas y deja verificable la procedencia de la instalación
con la que corre el ciclo. Las decisiones con consecuencias arquitectónicas son:

1. **Una regla con dos dueños deriva en contradicción.** La frecuencia de la suite completa
   estaba afirmada en dos lugares que se contradecían: `stage-3-tdd.md:153` («the full suite
   runs once per GREEN») y `re-entry.md:149-150` («complete suite» por GREEN) **vs.**
   `stage-3-tdd.md:31` («gates, not for debugging») y el gate del epic
   (`epic-005/plan.md:60-61`: focales y módulos tocados; suite completa al cierre). Los
   paquetes canónicos decían «the required full regression suite» — un término indefinido
   (`implementer-green.md:1`). Nadie decía quién declara los comandos concretos.
2. **El reemplazo validaba sólo lo corregido.** `--replace-packet` validaba únicamente los
   campos presentes en el set `corrected` (`_validate_corrections`): un `input`
   **conservado** que apuntaba a un archivo inexistente pasaba sin diagnóstico, y un alcance
   conservado fuera de política fallaba con el mensaje genérico de `validate_request` (sin
   campo ni opción). El encargo resultante podía quedar inválido en lo que **no** se tocó.
3. **La instalación cambiaba de versión en silencio.** `prepare` resolvía el origen de los
   agentes de proyecto de OpenCode desde `CDAD_OPENCODE_AGENTS_DIR` o, sin ella, desde la
   instalación global de HOME (`_derived_source_dir`); **no** consultaba el registro de
   activación. El caso real **MIX-V6V7** re-derivó los 11 agentes desde **otra versión** sin
   avisar, y ni el manifiesto ni los agentes publicados declaraban qué versión cargó una
   sesión.

## Impulsores de la decisión

- Que cada regla tenga **un solo dueño canónico editable** y que los consumidores la
  **referencien** sin copiar su texto (evitar el drift que produjo las contradicciones).
- Que **la metodología defina qué evidencia** se exige y **el proyecto declare los comandos**;
  una condición local/entorno se registra y **no** se vuelve requisito.
- Que un encargo corregido quede **válido en su totalidad** (conservado + corregido), sin
  sumar restricciones al camino normal de `prepare`.
- Que **ninguna operación cambie de versión de instalación en silencio**: un cambio de origen
  produce un diagnóstico que nombra el registro y las versiones en juego.
- Que **qué versión cargó una sesión** sea verificable **desde el artefacto publicado**.
- Que el cierre se compruebe como **test de integración en una raíz aislada** (nunca HOME),
  sin prometer ni ejecutar un despliegue reservado al dueño.

## Opciones consideradas

1. **Dejar la frecuencia de la suite como estaba y «acordar» la lectura.** Rechazada: dos
   afirmaciones contradictorias siguen presentes; el operador no sabe a cuál obedecer y el
   drift vuelve.
2. **Duplicar la política de evidencia en cada consumidor (paquetes, `SKILL.md`, referencias).**
   Rechazada: N copias editables vuelven a divergir; es la causa raíz de la contradicción.
3. **Un solo dueño canónico de la política + consumidores que referencian** (elegida): la
   política vive en `stage-3-tdd.md` §«Test evidence policy»; la equivalencia conserva su
   dueño en `re-entry.md` §«Equivalence of a registered run» (la política la referencia).
4. **Validar en el reemplazo sólo los campos corregidos** (estado previo). Rechazada: el
   hueco queda en lo conservado; el reemplazo existe para dejar un encargo válido, no para
   validar un diff.
5. **Validar el encargo resultante completo también en el camino normal de `prepare`.**
   Rechazada: suma una restricción nueva (existencia de `inputs`) al camino normal, contra el
   pedido del dueño; la exigencia es propia del sub-modo de reemplazo.
6. **Origen de agentes: variable > registro de activación > global, con contradicción
   diagnosticada y versión declarada en el artefacto** (elegida): el registro **nombra la
   instalación**; la variable queda como opción explícita; el manifiesto publica
   `source_version`.

## Decisión

1. **Una sola política de evidencia (PD-8..PD-10; INV-6).** `skills/cdad-cycle/references/stage-3-tdd.md`
   §**«Test evidence policy»** es el **dueño canónico** de la política: (i) regresión
   **proporcional** al cambio (focales + módulos tocados); (ii) suite **completa al cierre**
   de la feature (o antes si se toca instalador, staging o renderer); (iii) **reutilización**
   de evidencia registrada equivalente, cuyo dueño canónico es `re-entry.md` §«Equivalence of
   a registered run» (la política la **referencia**, no copia su texto); (iv) la metodología
   define la evidencia y **el proyecto declara los comandos**; (v) una condición local/entorno
   se **registra** en la evidencia y **no** se vuelve requisito. Los consumidores (paquetes de
   GREEN/refactor/review-fix, `packets/roles/implementer.md`, `SKILL.md`, las referencias de
   etapa) **remiten** a la política; ningún consumidor afirma «suite completa por GREEN».
2. **El reemplazo valida el encargo resultante completo (PD-1..PD-7; INV-4).**
   `--replace-packet` valida **todo** el encargo resultante (conservado + corregido): cada
   `input` existe y cae dentro de algún `read_scope`; scopes clasificados por la política;
   `invariants`/`evidence_required`/`expected_output` no vacíos; diagnóstico
   **campo/motivo/opción**. El **camino normal de `prepare` no cambia** (PD-5/INV-4): un
   `input` declarado inexistente sigue `rc=0`; una lista `inputs` vacía (`--input -`) sigue
   válida (PD-6).
3. **Procedencia de la instalación (PD-12..PD-15; INV-7).** `prepare` resuelve el origen de
   los agentes de proyecto en orden **`CDAD_OPENCODE_AGENTS_DIR` > registro de activación
   (`.cdad/activation.json`) → `<adopted_root>/.config/opencode/agents` > global**. Si el
   origen resuelto difiere del registro o del `source_dir` del manifiesto anterior, emite un
   **diagnóstico por stderr** que nombra el registro y las versiones en juego (nunca en
   silencio). El manifiesto publicado `.opencode/agents/.cdad-derived.json` declara
   `source_dir` y **`source_version`**, y `install.sh` escribe **`version.txt`** en la raíz
   instalada, de modo que **qué versión cargó una sesión es verificable desde el artefacto
   publicado**. `opencode reload` sobre un servidor ya iniciado queda **NO verificado**
   (se documenta el hecho del dueño y la comprobación aislada; **no** se afirma).
4. **El cierre es un test de integración en raíz aislada (PD-18; INV-8).** La versión nueva
   del repo se instala en una **raíz aislada** (nunca HOME) y con su CLI se corre `prepare` →
   `--replace-packet` (validación completa) → despacho con validación proporcional, **sin
   rodeos manuales** y sin tocar HOME (guard estructural).

## Consecuencias

- **Positivas:** una sola definición editable por regla elimina la clase de contradicción (no
  la instancia); el encargo corregido queda válido en su totalidad; la autoridad de rol y el
  camino normal no se degradan (el reemplazo no suma restricciones a `prepare`); el cambio de
  instalación es observable y la versión cargada es verificable desde el artefacto publicado;
  el CLI sigue determinista, read-only sobre el producto y nunca aprueba (ADR-003 intacto).
- **Negativas / límites declarados:** los comandos focales y de suite pasan a ser
  **declaración del proyecto** (Makefile/systemPatterns); el barrido de «frecuencia por GREEN»
  debe mantenerse; la instalación **v8 vigente** es anterior al marcador y sigue con
  `source_version: null` (su despliegue es del dueño, O5); el registro de activación ilegible
  cae silenciosamente a global (**O1**, hueco delgado de INV-7); `opencode reload` no se
  afirma; sin CI (el gate es la suite local). **VERIFY (dueño) abierto — D7:** si
  `~/.claude`/`~/.agents`/`~/.config/opencode` en `handoff-opencode.md:63` y `execution.md:21`
  también deben retirarse.

## Alternativas y trabajo futuro

Cerrar O1 (registro de activación ilegible → `rc=2`/warning que nombre el registro); O2
(«versión desconocida» explícita cuando falta el marcador); O3 (test de las rebanadas no-input
de PD-1); O4 (esterilizar `CDAD_OPENCODE_AGENTS_DIR` en el env de los tests T1); desplegar la
versión nueva (O5, dueño) y re-verificar `source_version` post-despliegue; comprobar `opencode
reload` contra 2.0.22 (dueño) antes de afirmarlo; CI del repo.

## Confianza

**Media.** Las postcondiciones están verificadas por tests focales (T1–T4), por la review
formal **única** `changes-approved` sin bloqueantes (verificación propia: suite completa
**649 passed / 0 fallos**, focales y regresiones OK, `make validate` con los 2 FAIL F011
preexistentes) y por el **walk-through PD-18** end-to-end con el CLI instalado en raíz
aislada. La confianza no es alta porque quedan opcionales no bloqueantes (O1..O5), un
**VERIFY del dueño** abierto (D7), la instalación v8 vigente sin `source_version` hasta su
despliegue, `opencode reload` **no verificado**, y el gate es una suite local **sin CI**.

## Enlaces

- Spec/plan: `docs/specs/005-005-adoption-coherence/{spec,plan}.md` (PD-1..PD-18; D1–D8)
- Evidencia: `docs/specs/005-005-adoption-coherence/{discovery,review,dispatch-ledger}.md`
- Referencias operativas: `skills/cdad-cycle/references/stage-3-tdd.md` §«Test evidence
  policy»; `references/re-entry.md` §«Equivalence of a registered run»;
  `references/runtime-adoption.md` §«Procedencia de los agentes de proyecto`;
  `references/opencode-delegation.md` §«Reload, version and provenance»
- ADR relacionados: ADR-003 (el orquestador materializa artefactos), ADR-011 (autonomía
  supervisada), ADR-017 (activación por proyecto hacia raíz aislada), ADR-019 (aprobación por
  rol que nombra el contrato; reemplazo que conserva y corrige el encargo)
