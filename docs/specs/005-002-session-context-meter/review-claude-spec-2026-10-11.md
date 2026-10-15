# Revisión de la spec y el plan — 005-002 (orquestador Claude, entre tramos)

Fecha: 2026-10-11. Objeto: spec `a70f6d50…` y plan `d373fc4f…` (commit `2bf24e6`), aprobados por
el orquestador OpenCode con la HITL delegada del epic.

## Dictamen

**Conforme; sin enmiendas.** La spec cubre los 8 puntos de `draft-inputs-2026-10-11.md`, conserva
el discovery, y los defaults y el borde del tramo quedan declarados. La ronda C1–C6 sobre la
superficie de invocación y las claves fue correcta (AP-13). La etapa 3 puede abrirse.

## Observaciones para la etapa 3 (sin cambiar el contrato)

1. **Fixtures sintéticos, no copias.** Los fixtures de T2/T4 reproducen la forma y los números de
   las muestras (101 llamadas, 12,55 min, #19, etc.) con contenido sintético. No se copia texto,
   identificadores de sesión, rutas ni modelos de la base real a `tests/` (PD-10). Si el
   test-writer necesita la forma real, el orquestador le da un resumen estructural; el
   test-writer no lee la base.
2. **Límite de bytes de PD-12.** La spec lo deja «declarado» sin un valor. El orquestador lo fija
   en el paquete AUDIT/RED de T3 (un número, en el reference/asset). No lo elige el implementer
   en GREEN.
3. **PD-11, sin escritura.** El test de «abrir no cambia tamaño/mtime del store ni de su WAL/SHM»
   corre contra un fixture SQLite en un directorio temporal del test, nunca contra la base real.
   La base real solo se usa en la integración opcional de T4, en solo lectura.

## Operación

- La versión instalada es `c9f4810`, que todavía tiene B1. B1 solo afecta al adaptador de la
  delegación externa, así que no afecta a 005-002.
- No desplegar ni recargar servidores: el otro proyecto activo corre en paralelo.

## Verificación del cierre (orquestador Claude, 2026-10-11 22:30)

- `validate-state` → `VALID: idle`. Focales de 005-002: 22 passed / 2 skipped.
- Integración real (base de sesiones en solo lectura; ids de las muestras en registros locales):
  `tests/test_005_002_t4_acceptance.py` → **5 passed**. Salida de la muestra 1: 8.336 bytes, bajo
  el límite de 16.384 de PD-12.
- Grep de privacidad sobre el diff de `tests/`, `skills/` y `scripts/` (ids de sesión, rutas del
  host, proveedor, modelos, proyectos): sin coincidencias.
- Las 3 observaciones se aplicaron. **D1 (`time_relative: 0.0` fabricado)** contradice PD-3/PD-4
  en un borde. Se acepta como deuda de prioridad 1 (no rompe el camino feliz) y conviene cerrarla
  antes de que 005-003 consuma el medidor.
- La suite de cierre 787/4 la declaró el orquestador OpenCode y no la re-ejecuté.
