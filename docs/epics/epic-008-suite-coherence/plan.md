---
epic_id: epic-008-suite-coherence
epic_name: Coherencia y sostenibilidad de la suite
created_at: 2026-10-26
approved_by: Pablo (dueño)
approved_at: 2026-10-26
---

# Epic 008: Coherencia y sostenibilidad de la suite

## Resumen

El epic 007 dejó la operación serial confiable, pero su cierre expuso el problema que más veces
reapareció: **la suite creció por historia y no por capacidad**. Hoy hay ≈134k líneas de tests contra
≈21k de producto, los tests están agrupados por la feature que los creó (no por la capacidad que
protegen), y una parte depende de HOME/XDG compartidos: tests verdes en aislamiento fallan en corridas
grandes. Además, el ciclo sigue teniendo tres decisiones de ciclo de vida duplicadas —identidad,
transiciones y recepción— y no verifica que cada subfase de rol se despache con paquete.

Este epic no agrega capacidades al producto: **ordena lo que ya existe** para que la suite vuelva a ser
un gate confiable y el ciclo tenga un solo lugar donde se decide identidad y transición.

Insumos: `docs/research/testing-practices-2026-10-25.md`, `docs/epics/epic-007-reliable-cycle-operation/closure.md`,
deudas `SUITE-CONTAMINATION`, `SUSP-GUARD`, `SUSP-LOCK`, `SUSP-IDENTITY`, `DESPACHO-SIN-PAQUETE`, y el
gate por superficie (`.cdad/local/surface-gate.sh`).

## Alcance

**Dentro:**

- Inventario y auditoría de la suite por capacidad/contrato: mantener, fusionar, eliminar. Medición de
  duplicación y de cobertura por postcondición (no por líneas).
- Aislamiento de HOME/XDG y temporales por test, para eliminar la contaminación entre corridas.
- Modelo de ciclo de vida unificado: resolvedor de identidad y decisor de transiciones compartidos por
  `cdad_packet`, `cdad_continuity` y `cdad_result`; regla explícita de adopción de invariantes.
- Exigir paquete renderizado en cada subfase de rol (RED, GREEN, review, scribe): el ciclo falla
  cerrado si un despacho de rol no tiene paquete.
- Gate de CI: suite completa, gate por superficie y `validate-state` en cada push.

**Fuera:**

- Paralelismo, scheduler, jobs (B3/B4 de Superlite).
- Capacidades nuevas del ciclo (la operación serial ya está cerrada en 007).
- Selección de modelos.
- Reescritura del producto o de las specs cerradas.

## Descomposición en features

| # | Feature ID | Resultado consumible (1 línea) | Dependencias | Paralelizable |
|---|-----------|-------------------------------|--------------|---------------|
| 1 | 008-001-home-xdg-isolation | Cada test corre con HOME/XDG/temporales propios: tres corridas completas consecutivas sin contaminación | — | No |
| 2 | 008-002-suite-by-capability | La suite se organiza por capacidad/contrato, con inventario mantener/fusionar/eliminar y cobertura por postcondición medida | 001 | Parcial |
| 3 | 008-003-lifecycle-decision-model | Identidad y transiciones se resuelven en un solo decisor compartido; la adopción de invariantes es explícita | 002 | No |
| 4 | 008-004-role-packet-enforcement | Un despacho de rol sin paquete renderizado falla cerrado, con diagnóstico y sin efectos | 003 | No |
| 5 | 008-005-ci-gate | CI corre suite, gate por superficie y `validate-state`; el rojo no se publica | 001-004 | No |
| 6 | 008-006-contract-not-coverage | Los tests se escriben y se revisan por contrato de usuario final: sin goldplating y con diferimiento explícito del QA intensivo | 001 | Parcial |

El orden es deliberado: primero se estabiliza la suite (001), después se audita con corridas
confiables (002); el decisor compartido (003) habilita la exigencia de paquete (004); CI (005) cierra.

**008-006 se agrega el 2026-10-27 por decisión del dueño, en cola después de 008-002.** No agrega
capacidad al producto: corrige la doctrina de los roles (test-writer, reviewer, orquestador) y agrega la
válvula de diferimiento del QA intensivo. Se ejecuta después de cerrar 008-002 y antes de 003/004/005, para
que rija en las tres unidades restantes.

## Contratos entre features

- **Vista compacta (`status`):** 001-004 no cambian su forma (007-001); toda información nueva es
  aditiva.
- **Continuidad:** 003 reutiliza el almacenamiento y el encadenamiento existentes; no crea otro
  registro ni otro recibo.
- **Evidencia:** el gate por superficie y `validate-state` son los gates compartidos; 005 los ejecuta,
  no los redefine.
- **Tests:** la reorganización de 002 no puede perder la cobertura por postcondición ya acreditada; el
  mapeo PC→test se conserva y se audita.

## Criterios de aceptación del epic

> Verificación completa en `docs/epics/epic-008-suite-coherence/closure.md` (2026-10-28).

- [x] Las features cerradas individualmente, cada una con su `closure.md` — **6/6** (008-006 se agregó por decisión del dueño; ver `closure.md`).
- [x] **Suite estable:** tres corridas completas consecutivas verdes, sin fallos intermitentes ni
  contaminación entre tests.
- [x] **Suite coherente:** cumplida en coherencia y trazabilidad; la reducción literal **no** se cumple y se declara sustituida por AJ6 (el piloto midió +3.317 bytes/+81 LF, publicado tal cual). Sin perder ninguna postcondición
  acreditada; inventario mantener/fusionar/eliminar con justificación.
- [x] **Un solo decisor:** identidad y transiciones resueltas en un punto compartido, con las
  duplicaciones retiradas; `SUSP-GUARD`/`SUSP-IDENTITY` cerradas o declaradas con su límite.
- [x] **Paquete obligatorio:** un despacho de rol sin paquete falla cerrado y no produce efectos (admite en las 5 fronteras y en el intake; límite: admite, no intercepta).
- [x] **Test por contrato:** ningún test exigido sin consecuencia observable para el usuario final; lo
  diferible queda registrado como `deferred-hardening` y no bloquea.
- [x] **CI verde:** suite, gate por superficie y `validate-state` en cada push; sin secretos — **mecanismo cumplido** (`scripts/cdad-ci-gate.py`); la **activación en el push queda pendiente del dueño** (sin workflow versionado: `.github/**` y `Makefile` son `unclassified`).
- [x] Sin mecanismos duplicados nuevos (dos excepciones declaradas: tabla `termination/delivery` y ramas de vigencia de `resume_unit`).

## Riesgos / deuda esperada

- **Borrar cobertura sin querer:** mitigación con el mapeo PC→test y el gate por superficie antes y
  después de cada fusión/eliminación.
- **Aislar con mocks de entorno:** el aislamiento debe ser real (HOME/XDG por test), no un parche que
  oculte contaminación.
- **Un decisor que se vuelve una fachada:** 003 debe retirar las duplicaciones, no envolverlas.
- **Exigir paquete y romper consumidores legítimos:** 004 debe distinguir despacho de rol de
  operaciones internas y fallar con diagnóstico, no con un `rc` nuevo sin contrato.
- **CI con costo o flakiness:** 005 empieza por el gate local y solo después publica.

## Autoridad

- **Aprobación del plan y de specs/planes de features:** el dueño (humano o agente de jerarquía
  superior que posee el proceso). Sin aprobación del plan, el epic no arranca.
- **Reservado al dueño:** push/publicación, servicios compartidos, runtime y cualquier activación.
- **Operador del resultado:** orquestador CDAD con la delegación HITL que el dueño establezca.

Status: Approved by Pablo on 2026-10-26
