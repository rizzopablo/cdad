# Dictamen focal C0 — revisión Claude (delta + spec/plan 004-001)

Fecha: 2026-09-24. Receptor: orquestador GLM. Objeto:
[spec-plan-004-001-architect-2026-09-24.md](spec-plan-004-001-architect-2026-09-24.md)
(commit `b808e07`). Dictamen registrado por el orquestador desde la revisión
externa de Claude; el texto siguiente es fiel a lo recibido.

---

Dictamen: **conforme, con una corrección requerida y tres observaciones.**
No hace falta rediscutir el enfoque.

## Lo que está muy bien

- **La errata enlazada, sin reescribir el original.** Corrige los cinco
  errores propios y reproduce hoy el valor correcto (2.697; lo confirmé).
  Es la forma sana de corregirse.
- **PD-11 y PD-12 son lo mejor del documento:** exigen pruebas positivas de
  capacidad desde el producto instalado, y tratan un rechazo de operación
  legítima como defecto, no como acierto del control. Eso convierte ADR-011
  en algo comprobable en vez de declarativo.
- **§6 resuelve R1 en serio:** snapshot antes de tocar nada, un único write
  del state, la delegación de Codex archivada y no borrada, y reanudación por
  reconciliación.
- **Honestidad sobre los límites:** la lista de lo que el paquete y el guard
  **no** protegen (`make *` depende de la receta, el guard no cubre lo que
  lanza el propio runtime) es exactamente lo que faltaba en los documentos
  anteriores.
- **El par `rtk wc` resuelto dentro del rediseño**, no como parche suelto.

## Corrección requerida

**T1 depende de una capacidad que T4 recién arregla.** PD-13 pide medir bytes
por rol, runtime y camino, con la suma recomputada mecánicamente. Pero el
propio architect no pudo medir bytes en esta sesión: `wc` y `du` denegados,
sin par `rtk`, y tuvo que tomar el dato del dictamen de GPT. Si T1 es la
primera tarea y la capacidad llega en T4, la línea base se produce otra vez
con evidencia prestada, que es justo el fallo que originó la errata.

Dos salidas aceptables, y el plan debería elegir una:

- Incluir en T1 el mínimo de capacidad necesaria para medir (los pares
  faltantes), declarándolo como el primer aterrizaje del rediseño y no como
  parche.
- O que T1 lo ejecute un rol que sí tenga la capacidad, registrando método,
  versión y configuración.

Lo que no sirve es dejar la duda 4 como está: "la fricción persiste hasta
T3/T4" y a la vez pedir una línea base medida antes de generar son
incompatibles.

## Observaciones

1. **Hallazgo nuevo, encontrado al revisar §6.2.** El vocabulario de
   `epic_stage` está duplicado y en desacuerdo:
   `skills/cdad-epic/references/state-detection.md:14` define seis valores,
   incluido `epic-planning`, y `cdad_packet.py:34` solo admite tres
   (`features-loop`, `epic-integration`, `epic-closure`). El informe cita
   `cdad_packet.py:34` como respaldo de usar `epic-planning`, y esa cita no lo
   respalda. El impacto práctico hoy es nulo, porque el modo `ordinary` no
   valida esa etapa, pero es una fila más del inventario (sería R13) y entra
   de lleno en PD-4: una regla compartida viviendo en dos fuentes que ya
   divergieron.
2. **004-001 quedó grande.** Siete tareas que incluyen generador, rediseño de
   permisos, manifest de propiedad, migración de fixtures y sustitución de
   validadores. Por el propio criterio de tamaño ("que un reviewer pueda
   rechazar una sin rechazar la vecina"), pediría un aterrizaje intermedio
   utilizable: generador más adaptadores, con la instalación sin cambios. Si
   T5 crece, que sea candidata a feature propia en vez de estirar el ciclo.
3. **Falta verificar el lado de supervisión de ADR-011.** La matriz §5 define
   cómo tratar cada situación, pero ninguna postcondición comprueba que el
   orquestador efectivamente verifique al re-entry y registre el desvío. O se
   agrega una postcondición acá, o se asigna explícitamente a 004-003. Sin
   eso, la mitad "supervisada" de la autonomía supervisada queda sin dueño.

## Respuestas a las seis dudas

1. **Firma de autoridad:** el usuario, en `execution.md`, y alcanza con eso;
   no agregaría otra aprobación para la activación misma. Es decisión de
   Pablo, no mía.
2. **Esquema de `hitl_delegation`:** conservarlo, sin extenderlo en 004-001.
   De acuerdo.
3. **Layout público:** sacarlo del default y decidir el flag recién después
   de migrar los fixtures. Si al migrar no aparece un consumidor real, no hay
   flag.
4. **Fricción transitoria:** aceptable **solo** si se resuelve la corrección
   requerida; si no, el costo cae sobre la evidencia de T1.
5. **Rutas:** `sources/`, `scripts/cdad-generate.py` y `build/staging/` están
   bien. Dos detalles: `build/` va al `.gitignore`, y el instalador no debe
   leer nunca `sources/` (solo staging), para que la separación sea real y no
   una convención.
6. **Techo de 12.000 bytes:** parametrizar y diagnosticar, como propone.
   Agregaría que el valor efectivo se registre en la línea base, porque es
   parte del presupuesto que queremos medir.

## Conclusión

Con la corrección requerida resuelta y las tres observaciones incorporadas,
esto está listo para que Pablo apruebe y se active 004 según §6.

---

Status: dictamen técnico externo (review focal). No aprueba la spec ni activa
el epic; eso corresponde al usuario. Registrado por el orquestador el
2026-09-24.
