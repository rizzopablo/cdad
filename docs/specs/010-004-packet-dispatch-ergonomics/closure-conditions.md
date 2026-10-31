# Condiciones de cierre — 010-004-packet-dispatch-ergonomics

**Fecha:** 2026-10-30 (UTC del entorno).
**Autor:** orquestador CDAD (mandato HITL vigente: `docs/epics/epic-010-documentary-specialization/execution.md`; `owner-mandate-hitl-2026-10-30.md`). Documento del ámbito documental del orquestador, no trabajo de rol.
**Contrato:** `spec.md` SHA-256 `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`.
**Origen:** revisión independiente de Stage 4 (T6), `review.md` (recibo `3c9a73d7…`, `semantic_status: pending`), que devolvió **4 hallazgos bloqueantes (B1–B4)** y **3 requeridos no bloqueantes (R1–R3)**.

**La unidad NO queda cerrada por este documento.** B1–B4 abren remediación en repo y la revisión se repite cuando estén resueltos. Lo que sigue fija las condiciones documentales que el cierre deberá cumplir y los límites que el cierre no puede ocultar.

## 1. R1 — D-1: cerrada en repo, NO vigente en la instalación

Formulación exacta del límite, que debe aparecer en cualquier declaración de cierre de esta unidad:

> **La unidad queda cerrada en el repositorio, NO vigente en la instalación.** El despacho real requiere la toolchain del repositorio (`skills/cdad-cycle/scripts/…` y sus envoltorios `scripts/`) hasta que el owner decida publicar. Mientras el owner no lo decida, ninguna afirmación de vigencia en el CLI instalado puede sostener un cierre, un despacho ni una verificación de aceptación.

Medido en esta fecha (mismo módulo, dos fuentes):

| Fuente | `cdad_packet.py` sha256 |
|---|---|
| Repo (producto de la unidad) | `44a950a54fb56d303e6ecc4357c09c913ddca7a170e26b015e572ac29d48fe54` |
| Instalación (`~/.config/opencode`, `~/.agents`, `~/.claude` — las tres coinciden) | `171fcd1413ec8446272564388fe2165716569e6c3c070f02f4dca8008960e679` |

Consecuencias operativas declaradas, no silenciadas:

- Toda preparación, validación, despacho y recepción de esta unidad se ejecuta con los scripts del repo (D-1), como ya ocurrió en T2–T6.
- La admisión en la frontera re-renderiza con el asset root instalado (`v2-1-verification.md`, D-1); el `prepare` instalado sigue admitiendo v1 implícito sin policy (comportamiento anterior a esta unidad).
- La decisión de publicar es del owner: no es delegable al orquestador ni se fabrica por conveniencia de cierre.

## 2. F011 — seguirá en FAIL al cierre

`make validate` (`scripts/validate-subagents.sh` → `install.sh --check`) compara el repo contra la instalación global, que está desactualizada por diseño del mandato. El drift es preexistente y **ambiental**: incluye archivos que esta unidad no tocó. Corregir F011 exige publicar la instalación, acto que el mandato vigente no autoriza.

Por lo tanto:

- **F011 seguirá en FAIL al cierre de esta unidad, y el cierre lo declara.** El número medido en el gate T4 es `Assert PASS: 182 / Assert FAIL: 1` (`make validate` rc=2); la condición de cierre no es «F011 en PASS» sino «F011 declarado, medido y no oculto».
- No se cierra F011 debilitando la aserción, actualizando la instalación global ni retirando la comprobación.
- La aceptación de la unidad se sostiene en las aserciones repo-internas (que pasan) más la evidencia de T5/T6, nunca en un `make validate` verde que hoy no puede darse sin publicar.

## 3. R3 — las guardas documentales son un límite declarado

Las guardas documentales de esta unidad (`tests/test_010_004_t4_red.py`) comprueban **un token** (`--route C`) y su supervivencia en los agentes derivados. Eso es todo lo que acreditan:

- **No acreditan obediencia** de un modelo, ni recepción nativa, ni que el texto instruido se cumpla en la práctica. `spec.md:466` ya lo dice y esta unidad no lo cambia.
- Por eso B1 (intake sin el rechazo A+C ni v2-para-C) y B3 (PC-10/PC-11 sin procedimiento real) quedaron en verde durante el gate T4: la guarda miraba el token, no la promesa.
- El límite se declara aquí y en la traza corregida de `t4-closure.md` §3. No se «arregla» ampliando la guarda a prosa congelada (AP-14): la revisión independiente es el control que corresponde a la semántica.

Corrección aplicada a `t4-closure.md` §3 (traza de postcondiciones): se marca que las filas PC-03, PC-07b, PC-10 y PC-11 **no quedaron acreditadas** por las líneas citadas, con el motivo de cada una; se conserva el texto original como registro histórico y la corrección se fecha.

## 4. Backlog de la épica

R2 e I-8 no se resuelven dentro de esta unidad (el mandato lo prohíbe). Quedan encolados, una línea cada uno, en `docs/epics/epic-010-documentary-specialization/backlog.md`:

- **R2 — clase I-6 abierta:** la fila 3 de la matriz no distingue un request histórico de uno nuevo sin localizador; un gate del orquestador que exija el campo en paquetes nuevos necesita su propio contrato. Corregir el caso no cierra la clase.
- **I-8 — el test-writer no puede leer sus propios `instruction_sources`:** defecto de diseño de scopes (`skills` es raíz de implementación y el `read_scope` del rol no la incluye). Tres salidas posibles registradas en `observations-packet-dispatch.md`; sin unidad asignada.

## 5. Afirmación histórica superada

`v2-1-verification.md` §«Decisión tomada», punto 4, ruta A, afirma que `cdad_packet.py` y `cdad_continuity.py` difieren de la instalación **«sólo en la canonicalización de raíz de 010-000»**. Esa afirmación era cierta cuando se escribió (paso habilitante V2-1) y **ya no lo es**: el producto de 010-004 diverge además en la emisión de ruta C, el localizador `execution_context`, la validación v2-only de la preparación y el diagnóstico de bloqueo. Queda marcada como **afirmación histórica superada**; el límite vigente es el de §1 de este documento.
