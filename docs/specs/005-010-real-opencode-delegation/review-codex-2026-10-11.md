# Verificación posterior del cierre — 005-010

Fecha: 2026-10-11. Objeto: cierre `c9f4810`, producto final `3e556a8`
y correcciones posteriores del test de integración. Revisión focal solicitada
por el dueño; no cambia autoridad ni opera instalaciones.

## Dictamen

El recorrido principal está confirmado con evidencia real. **Una corrección
focal requerida antes del despliegue:** B1, selección del texto final. No se
propone ampliar la feature con otras familias de variantes ni repetir la
construcción. La aceptación global post-despliegue continúa pendiente.

## Verificado de forma independiente

- Estado actual: `validate-state` → `VALID: idle`; 005-010 figura `done`.
- Lectura RO de las filas reales de las dos aceptaciones y la integración:
  agentes esperados, directorios temporales correctos e `idle_outcome=succeeded`.
- Recibo de la última aceptación: `pending`, identidad/paquete `passed`;
  bytes almacenados coinciden con el digest de la parte del recibo.
- La entrega contiene el hash correcto de la spec y PD-1..PD-10; el state del
  consumidor conserva paquete `completed` y el re-entry de aceptación.
- Focales propias: `python3 -m pytest -q` sobre los módulos T1/T2/T3 y reviewfix
  de 005-010, más T2/T4 de 005-009 → **37 passed, 1 skipped**, 51.38 s. Sin
  invocar un LLM ni repetir la integración facturada.
- La instalación global continúa en `6f4d5db`; el producto nuevo no está
  desplegado. Los archivos estratégicos ajenos siguen fuera de los commits.

La suite completa **763/2** es evidencia declarada por el orquestador, no
re-ejecutada por esta revisión. El diff desde `3e556a8` confirma que el cambio
posterior de código está en la prueba de integración omitida por defecto;
el producto del adaptador no cambió. La reutilización de esa corrida, junto
a la integración habilitada posterior, es razonable con esa frontera.

## B1 — Un texto intermedio puede sustituir una entrega final ausente

Veredicto: **corrección requerida**. Contrato: PD-1 y PD-5.
Ubicación: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:387`,
`_last_assistant_text`.

PD-1 exige el texto del último mensaje `assistant`; PD-5 exige `blocked` si
`succeeded` carece de texto final. El código consulta todos los mensajes en
orden descendente y devuelve el primero que tenga texto. Si el último solo
contiene herramientas/razonamiento, toma texto de un mensaje anterior.

Reproducción dirigida, con SQLite temporal y la función del producto:

1. Mensaje assistant seq=1: «Voy a analizar el contrato; todavía no tengo el
   resultado.»
2. Mensaje assistant seq=2: solo una parte de razonamiento, sin texto final.
3. Fila de sesión correlacionada con `idle_outcome=succeeded`.
4. `_last_assistant_text` devuelve el avance de seq=1; `_classify` devuelve
   `completed` con ese avance como entrega.

Esto no se observó en las corridas reales revisadas: es una reproducción
controlada del comportamiento que contradice el contrato. El recibo `pending`
conserva el gate semántico, pero no corrige la identidad de la entrega.

El helper del oráculo `durable_last_assistant_text` en
`tests/test_005_009_t2_opencode_adapter.py:849` también acumula textos de
mensajes anteriores. El caso `succeeded-no-text` no contiene ningún mensaje
assistant, de modo que no detecta esta sustitución.

**Cierre proporcional:** un RED focal con texto intermedio seguido de último
assistant sin texto; exigir `blocked` y ausencia de entrega/recibo nuevo.
Seleccionar exclusivamente el último assistant (p.ej. `ORDER BY seq DESC
LIMIT 1`); si carece de texto, devolver ausencia. Conservar la concatenación
de las partes textuales de ese único mensaje y la regresión del caso normal.
No cambiar clasificación de otros outcomes ni el mandato del worker.

## Pendientes operativos

- Tras esa corrección: despliegue por el dueño y confirmación corta de PD-9(b).
- Antes del próximo architect, registrar la aprobación ya autorizada de la
  versión vigente del plan del epic por el camino legítimo. Hash actual
  `fbb0770b…`; el último registro conserva `996dd7e0…`. No es necesario volver
  a discutir la dirección estratégica ni simular una nueva aprobación.
- La observación previa sobre registro de despacho posterior a la ejecución
  sigue en la interfaz común: 005-010 la conserva por alcance explícito.
  Mantenerla como pendiente de recuperación para ejecución prolongada.
- El script local de despliegue transforma cualquier fallo de `--check` en
  una advertencia y luego informa terminado. Al desplegar, comprobar cuáles
  fallos corresponden a deuda conocida y detenerse ante otros; ese mensaje
  por sí solo no verifica una instalación correcta.
