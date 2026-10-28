# Cierre 008-006-contract-not-coverage

Fecha: 2026-10-27. Epic: `epic-008-suite-coherence`. Feature 6 de 6.

## Resultado

La regla «test por contrato de usuario final, no por cobertura» deja de ser una instrucción verbal y pasa
a estar **en las fuentes de los cinco roles**, en el detalle de stage 3, en las plantillas y en los agentes
generados de los dos runtimes, con **un solo hogar editable por regla** y un **verificador ejecutable** que
falla cerrado.

## Contrato

`docs/specs/008-006-contract-not-coverage/spec.md` — 6 promesas (A–F) con sus PCs, la tabla de las siete
reglas y sus siete hogares, el contrapeso (R7) y el límite verificable. Ajustes AJ1–AJ4:

- **AJ1** — el generador (`scripts/cdad-generate.py:523-531`) inyectaba «one test per numbered postcondition»
  en el agente del test-writer: actualizar los siete hogares sin eso habría distribuido **las dos reglas a
  la vez**. Ahora apunta a R2.
- **AJ2** — «un test por promesa» **no es un techo**: no se multiplican tests para resultados equivalentes,
  y sí se escriben los de comportamientos comprometidos distintos y los que R4 promueva con motivo.
- **AJ3** — `deferred-hardening` registra **cada** diferimiento con motivo; `None` significa «no hay», no
  «no lo pensamos».
- **AJ4** — esta unidad **no tiene RED de test-writer**: la política de alcance le prohíbe leer `sources/` y
  `agents/`, que son el objeto bajo prueba (verificado: el paquete se rechaza). La verificación es
  inspección estática del reviewer + verificador ejecutable. Conversión a tests: `deferred-hardening`.

## Cambios

- **Siete hogares:** `sources/roles/{architect,test-writer,reviewer,orchestrator,implementer,scribe}.md` y
  `skills/cdad-cycle/references/stage-3-tdd.md`. El implementer ya **no** dice «MINIMAL CODE»: declara
  implementación simple con **robustez razonable aunque ningún test la exija**.
- **Consumidores que citan y no redefinen:** `stage-3-tdd.md`, `test-audit.md`, `SKILL.md`,
  `handoff-prompts.md`, `feature-plan-template.md` (schema intacto), y el fragmento RED del generador.
- **Plantillas:** `spec-template/spec.md` gana `## deferred-hardening` y la agrupación por promesa;
  `test-audit.md` registra promesa, PCs protegidas y «sin este test, el usuario…».
- **Generación:** `make agents` regenera **22 agentes** (11 por runtime). Ninguno incorpora `model:`; la
  política de modelos queda intacta y las personalizaciones instaladas del operador no se sobrescriben por
  esta feature.
- **Verificador:** `scripts/cdad-doctrine-check.py` — exige los 7 hogares con su marcador, barre fuentes y
  agentes buscando las cuotas retiradas y **exige los 22 artefactos declarados por runtime**. Control
  negativo: borrar un agente, un directorio, un hogar o reintroducir la cuota vieja ⇒ rc 1.

## Evidencia

- Discovery `bf58a05`; spec `84b8324` + AJ1–AJ3; plan-review con 3 bloqueantes (generador, techo de R2,
  registro de diferimientos) cerrados; AJ4 y re-gate (`6f288cb`).
- GREEN `1e2811d` (36 archivos). Review con **3 bloqueantes**: R4 con segunda definición editable en el
  reviewer, R2 reformulada en stage 3, y verificador que aceptaba la ausencia de agentes. Cerrados en
  `5584bba` y `b77176a` (regenerados los agentes afectados).
- Regresiones: `707 passed, 2 skipped` (todo lo que lee fuentes/agentes/plantillas), más 34+68+58+29+30 en
  los conjuntos de generación, plantillas y paquetes; `validate-odoo-specialization` 68/0.
- **Gate de cierre:** `python3 scripts/cdad-suite.py close --evidence-root .cdad/local/008-006/evidence --all`
  sobre `1e2811d` → intento `attempt-20261027T174755955579Z-977440-e4741b10`: **1774 passed, 5 skipped,
  0 failed, 0 errors, rc 0**, `pytest_summary.verified: true`, 46:18. Los 5 skips son los opt-in reales de
  siempre.

## Hallazgo del canario (declarado, no resuelto)

El canario reportó **6 líneas de delta** en el HOME real durante el gate: `~/.config/opencode/agents/
cdad-test-writer.md` y `cdad-test-writer-odoo.md` cambiaron (+15 bytes) y el directorio `agents` cambió de
mtime. **Algo repubblicó los agentes derivados sobre el HOME real del operador durante la suite.**

- **No es un fallo del gate**: el intento terminó `rc 0` y el canario de 008-006 informa, no bloquea.
- **No está identificado el mecanismo.** Se descartó la hipótesis de un hijo con `env` sin `HOME` (los
  candidatos copian `os.environ`). No se afirma causa.
- **Efecto observado:** los agentes instalados quedaron **actualizados con la doctrina nueva** (el cambio es
  el puntero de R2). No se corrompió nada, pero se escribió en el HOME sin autorización explícita.
- **Deuda `HOME-LEAK-DERIVED-AGENTS` (media):** la suite no puede publicar en el HOME real. Requiere
  reproducir el write y aislarlo; no entra en esta unidad.

## Límites declarados

- Los tests de esta unidad son **presencia de marcadores**, no integridad semántica: el juicio sobre si una
  consecuencia de usuario es verdadera o suficiente queda en el reviewer y en el gate, con evidencia.
- `cdad-doctrine-check.py` verifica presencia y composición; **no** compara byte a byte los agentes contra
  una regeneración (lo cubren los tests de generación).
- `validate-consistency.sh` F011 sigue fallando: es **preexistente y ambiental** (inspecciona la copia
  instalada del operador, que lleva `model:`), verificado sobre un worktree en `HEAD`.

## deferred-hardening

| Qué | Por qué | Dónde |
|---|---|---|
| Rechazo operativo de informes sin la declaración «sin este test…» | Exigiría un contrato de formato y recepción que esta unidad no tiene | Otro contrato |
| Juicio automatizado de la consecuencia declarada | No es mecanizable con honestidad | Reviewer + gate |
| Convertir la doctrina en tests bajo `tests/` | La política de alcance impide al test-writer leer el objeto (AJ4) | Cuando la política lo permita |
| QA intensivo de variantes equivalentes, carga y rendimiento | No comprometido en esta unidad | Epic de endurecimiento |

Ninguno permite diferir una promesa comprometida (R7).

## Deuda observada

- `HOME-LEAK-DERIVED-AGENTS` (media, arriba).
- `suite-report.md` ausente y `skips[].reason` vacío en `attempt.json`, heredados de 008-002 → 008-005.
- `make validate` F011 preexistente.
