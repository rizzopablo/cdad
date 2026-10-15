# ADR-022 — Los mapas de permisos derivados son una proyección coherente del clasificador único: la excepción de tests reabre solo los árboles/archivos declarados y `private` gana por findLast

* Estado: **Aceptado** (2026-10-10; orquestador bajo delegación HITL de epic-005)
* Fecha: 2026-10-10
* Decisores: orquestador bajo delegación HITL de epic-005 (aprobación del dueño, `execution.md`)
* Confianza: **Media-Alta**

## Contexto y enunciado del problema

005-008 alinea las capacidades mediadas por ruta de los agentes con el **clasificador único** para un
proyecto cuya política declara una **raíz de tests anidada dentro de una raíz de implementación** (primer
consumidor real: Perl/Webmin, implementación `webmin-module/module/` y tests en `webmin-module/module/t/`).

El defecto reproducido: `_derived_maps` emitía, en la rama `read` del `test-writer`, un mapa que
concatenaba el deny de implementación + los allows de tests co-ubicados + `private`, **sin** el allow del
árbol de tests declarado (`_test_patterns`); el `edit` del mismo rol **sí** lo incluía → el test-writer
podía **editar** sus tests pero **no leerlos**. Además `_test_patterns` **ignoraba `test_files`**: el
clasificador daba `tests` a un `test_files` bajo implementación (`exact("test_files")`) y los mapas
derivados lo denegaban.

La clasificación ya era correcta (tests > implementación por precedencia) y el guard de Claude Code ya era
correcto (bloquea solo si la clase es `implementation`): el defecto era **exclusivo del mapa OpenCode**. El
problema arquitectónico es cómo relacionar dos artefactos que ya existían por separado —el **clasificador**
(`classify_path`) y los **mapas de permisos derivados** (`_derived_maps`, evaluados por findLast)— de modo
que no diverjan, sin amplificar la política y sin reabrir la barrera privada.

## Decisión

1. **Los mapas derivados son una proyección del clasificador único (INV-1).** Un test anidado declarado →
   allow para el test-writer; la implementación → deny de lectura; un `tests/` literal no declarado bajo
   implementación → implementación. La fuente de patrones de tests es **única** (`_test_patterns`) y ahora
   **incluye `test_files`** (D1), de modo que el `read`/`edit` del test-writer y el `edit` del implementer
   quedan en paridad automática.
2. **El orden del mapa `read` es load-bearing (D2).** deny de implementación → allow de tests declarados
   (+ co-ubicados) → **`private` al final**. Por findLast, el allow reabre el árbol de tests y `private`
   conserva su precedencia: **una excepción de tests nunca reabre una ruta privada** (PD-6/INV-2). Mover el
   allow después de `private` anularía la barrera.
3. **Sin convenciones globales (D3).** Solo se reabren los **árboles y archivos declarados**; nunca
   `**/t/**` ni `**/*.t` (PD-7/INV-3). La corrección no amplifica la política.
4. **Sin entradas por ruta en `grep`/`glob` (INV-4/PD-9).** La barrera viva por ruta es `read`/`edit`; los
   derivados no declaran una barrera que no existe (W-2).
5. **El esquema de política permanece de exactamente tres campos (D4/INV-5).** `_validate_policy_document`
   **nombra** el campo extra/faltante (`unknown field(s): X` / `missing field(s): Y`) conservando el
   fail-closed; una política con un campo de comandos se **rechaza**. Los comandos de sintaxis/tests viven
   en el **lugar canónico del proyecto** (Makefile/systemPatterns), **nunca** en `docs/cdad-policy.json`.

## Consecuencias

* **Positivas.** Los permisos derivados expresan exactamente la política (ni amplificación ni
  sobre-restricción); el caso focal `test_files` queda coherente; la barrera privada se preserva sin
  depender de la intuición del lector; el diagnóstico del esquema nombra el defecto en vez de dar un
  mensaje genérico.
* **Negativas / costos.** El orden de las reglas del mapa es **frágil por diseño** (findLast): un cambio de
  orden futuro puede anular `private` o la reapertura de tests sin que el código lo impida; se protege con
  tests (PD-6/PD-7). La fuente única de patrones (con `test_files`) acopla el `read`/`edit` del test-writer
  con el `edit` del implementer: correcto por paridad, pero cualquier cambio de patrón afecta a los tres
  mapas.
* **Riesgo aceptado.** La mediación en vivo de un proceso OpenCode real (VERIFY 3) **no** se demuestra por
  los tests (que verifican mapas publicados + el oráculo findLast); los límites honestos se declaran
  (grep/shell/sesión separada **no** son sandbox; sin allowlists por comando).
* **Sin cambios de forma.** El clasificador (`classify_path`), el guard CC
  (`claude-code-path-guard.sh`), el esquema del manifiesto y la publicación atómica **no** cambian; solo
  cambia el contenido del mapa `read` del test-writer, la fuente de patrones de tests y el diagnóstico del
  esquema.

## Alternativas consideradas

* **Reabrir los tests con convenciones globales** (`**/tests/**`, `**/*.t`). Rechazada: rompería B3/PD-7
  (amplificación de la política).
* **Emitir el allow de tests después de `private`.** Rechazada: anularía la barrera privada (R2/PD-6).
* **Un helper solo-read en lugar de extender `_test_patterns`.** Rechazada (D1): crearía dos verdades y
  rompería la paridad `read`/`edit`/implementer.
* **Registrar los comandos en `docs/cdad-policy.json`.** Rechazada: el esquema es de tres campos; los
  comandos son del proyecto (D4).

## Referencias

* Contrato: `docs/specs/005-008-project-path-capabilities/spec.md` (PD-1..PD-11, INV-1..INV-9; D1–D7) y
  `plan.md` (T1–T3).
* Insumo: `docs/specs/005-008-project-path-capabilities/discovery.md` (defecto reproducido, mapa
  archivo:línea).
* Revisión: `docs/specs/005-008-project-path-capabilities/review.md` (PASS, 0 bloqueantes); cierre:
  `docs/specs/005-008-project-path-capabilities/closure.md`.
* Fronteras: ADR-012 (política de límites por proyecto) y ADR-020 (política única de evidencia y
  procedencia declarada).
