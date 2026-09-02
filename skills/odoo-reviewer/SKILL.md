---
name: "odoo-reviewer"
description: >
  Checklist OCA + catálogo pylint-odoo vigente + split mandatory/advisory para
  el rol reviewer de CDAD en proyectos Odoo. Mapeo de checks a los 5 ejes de
  review (correctness/readability/architecture/security/performance) y
  evidencia requerida (make test-clean + output pegado + oca-checks). Usar en
  la etapa 4 (Review) de cualquier feature sobre un addon Odoo.
---

# odoo-reviewer — review de addons Odoo (OCA + pylint-odoo)

> Estándares OCA (CONTRIBUTING.rst, pylint-odoo, oda-pre-commit-hooks,
> manifestoo) + docs oficiales Odoo. Complementa al reviewer genérico CDAD
> (los 5 ejes del rol reviewer); acá está el catálogo específico Odoo.

## Check básica por eje (mapeo a los 5 ejes del reviewer genérico)

| Eje CDAD | Checks Odoo |
|---|---|
| **Correctness** | ORM sin escritura prohibida, `@api.depends` correctos, `_compute` puros, `onchange` sin persistencia, commits no en runtime, sin heredar estados sin super |
| **Readability & Simplicity** | nombrado de registros/campos, contexto de `_name` descriptivo, vistas sin vista duplicada innecesaria, manifest limpio (author/version/formato) |
| **Architecture** | módulo en su capa correcta (model/view/controller/wizard/security), manifest `depends` mínimo y correcto, no acoplamiento oculto entre addons |
| **Security** | SQL parametrizado (prohibido concatenar), `ir.rule`/grupos en `security/`, commands `sudo()` justificados, requests externos con timeout |
| **Performance** | N+1 (búsquedas dentro de loops), `search` sin límite, lecturas redundantes, métodos de cómputo ineficientes |

## Catálogo pylint-odoo vigente (checks clave)

Catálogo de `pylint-odoo` (reglas verificadas; código de regla → significado).
El prefijo E/W/C es severidad (error/warning/convention). Solo los `E`
bloquean en mandatory.

| Código | Regla | Significado |
|---|---|---|
| **E8103** | sql-injection | SQL con `%`/`format` interpolando sin parámetros — riesgo de inyección (Security) |
| **E8102** | invalid-commit | `self.env.cr.commit()` en runtime de Odoo (prohibido fuera de transacción propia) |
| **E8135** | no-write-in-compute | escritura dentro de un método `@api.depends`/`_compute` — efectos prohibidos (Correctness) |
| **E8140** | no-raise-unlink | `raise` dentro de `unlink()` sin contexto — eliminar registros con dependencias |
| **W8106** | method-required-super | método que exige llamar `super()` y no lo hace — herencia rota |
| **E8106** | external-request-timeout | request HTTP externo sin `timeout` — riesgo de colgar el worker |
| **E8130** | test-folder-imported | el package `tests` se importa sin `__init__.py` correcto |
| **C8102** | manifest-required-key | `__manifest__.py` falta una clave obligatoria (`license`, `category`, `version`, etc.) |
| **C8106** | manifest-version-format | `version` del manifest sin formato semver OCA correcto |
| **C8101** | manifest-required-author | falta `author` en el manifest |

## Split mandatory / advisory

El `.pylintrc-mandatory` del proyecto **bloquea solo los checks `E`** (errores),
que deben estar en cero para aprobar la review. Los `W` (warnings) y `C`
(conventions) son **advisory**: se reportan, se priorizan por leverage, pero
no bloquean el merge por sí solos salvo excepciones explícitas documentadas.
La review marca cada hallazgo como `mandatory` (bloqueante, severidad
Required/Critical) o `advisory` (opcional, severidad Optional/Nit/FYI).

Evidencia de lint obligatoria en la review:
- Output de `make lint --all` (`pre-commit-vauxoo`) pegado, con `0` bloqueantes.
- Output de `pylint` pegado, con `0` checks `E` y los `W`/`C` listados.

## Evidencia requerida (no negociable)

La review de una feature Odoo exige, además del análisis del diff:

1. **`make test-clean`** verde — gate de instalación desde cero con demo data,
   output pegado (línea `0 failed, 0 error(s) of N tests`).
2. **oca-checks** sin hallazgos — el checker de manifiesto OCA (`oca-checks
   --manifest` / `--oca-addons-cfg`) devuelve 0 problemas.
3. **pylint-odoo** sin `E` bloqueantes (ver catálogo arriba), `W`/`C`
   documentados como advisory.
4. **`make lint --all`** (`pre-commit-vauxoo`) con `0` bloqueantes, output
   pegado; los hallazgos `W`/`C` del lint son advisory según el split
   mandatory/advisory de arriba.
5. La evidencia se **pega**, no se describe ("la suite está verde" no basta).

> Nota: el lint (`make lint`) es estático y corre en la máquina del
> desarrollador (no en entornos gestionados); el output viaja con la review.

## Procedimiento

- Revisá el diff completo con la checklist de la tabla por eje.
- Verificá la verificación del autor: `make test-clean` + output pegado +
  oca-checks + pylint sin E.
- Reportá cada hallazgo con ubicación (archivo:líneas), problema, sugerencia
  (el movimiento), severidad y si es mandatory/advisory.
- Cerrá con "LISTO. Resumen: <X> bloqueantes, <Y> opcionales."

## Anti-rationalizations (rechazá estas)

| Racionalización | Realidad |
|---|---|
| "La suite pasa" | No atrapa sql-injection, mal diseño de vistas ni manifest mal formado. |
| "Es solo un warning (W)" | Un `W` puede ser gate de proceso o señal de un bug latente; sé mandatory cuando la regla lo exige. |
| "El código no toca security" | Un campo nuevo puede abrir un `ir.rule` o un endpoint sin grupos. |
| "Es custom, no aplica OCA" | Los estándares OCA aplican a TODO addon publicable, custom incluido. |