# Encargo al reviewer — borrador spec/plan 003-007-living-continuity

Rol: `cdad-reviewer`, solo lectura, adversarial. Revisa
`docs/specs/003-007-living-continuity/architect-draft-001.md` (discovery, D1–D10,
V1–V8, spec P1–P10, plan T1–T4) contra el encargo `handoff-architect-001.md`.
Sin `opencode run`/`claude`/`codex` anidados, sin instalar. Objetivo ~20-30 min.

## Qué evaluar
1. ¿Resuelve T4-REF y T4-CKPT **en la práctica** (no solo en el CLI) con alcance
   proporcional? Señala scope creep (MVP: lo que no rompe el camino feliz → deuda).
2. ¿Las postcondiciones son verificables por test o evidencia observable? ¿P9 (rotación
   real) es ejecutable por el orquestador sin editar la spec aprobada ni reactivar el repo?
3. ¿Se preserva la integridad que importa (contrato/autoridad falla cerrado, tamper,
   aislamiento de rol)? ¿Algún camino deja pasar un cambio de contrato en silencio?
4. Restricciones del dueño (nunca HOME, sin push, anonimizar, no endurecer permisos,
   gate de tests vigente).

## Observaciones del orquestador para verificar (compruébalas, no las des por ciertas)
- **O-A (el default puede no resolver nada en la práctica):** con D2/P3 una referencia
  string sin clase = `contract`. El cableado actual del orquestador
  (`sources/roles/orchestrator.md:77-82`, "Continuity wiring") y el ejemplo de
  `continuity.md` no dicen qué clase declarar. Si el orquestador sigue pasando los ledgers
  como strings, seguirán bloqueando y T4-REF no se resuelve en uso real. ¿Hace falta que
  el cableado del orquestador (fuente de rol, se regenera en T4) y `continuity.md` digan
  explícitamente qué se declara `living`? ¿En qué tarea?
- **O-B (legado = vivo, D6/D7/P7):** contradice "no clasificado = contrato" para cuerpos
  viejos, incluida la spec aprobada de esas ejecuciones. ¿Es aceptable dado que ambas
  ejecuciones están cerradas? ¿Debería `resume` marcar `legacy: true` de forma visible y
  limitarse a cuerpos sin `record`? ¿Hay un puente más estrecho?
- **O-C (`stage_history` como progreso, D1):** las aprobaciones (`approved_by`) viven
  en `stage_history` y `prepare` las exige (I2). Si el digest de autoridad las excluye,
  ¿una aprobación revocada o editada pasa sin aviso? ¿Basta con que la spec/plan aprobados
  sean referencias `contract`?
- **O-D (cadena de checkpoints, D5/D6):** al apendear un checkpoint con la misma clave,
  ¿el `prev` se ata al head actual (CAS) para que no se formen bifurcaciones? Con la
  redefinición de split-brain, ¿qué detecta hoy un fork de checkpoints y qué deja de
  detectar respecto de 003-004/RU-2? ¿Los tests de RU-2 (`test_003_006_t4_ru2_*`) siguen
  teniendo sentido?
- **O-E (proyección `fields`):** ¿qué pasa si `fields` se declara sobre un archivo no
  JSON, o con claves que no existen? ¿Debe fallar cerrado al escribir?
- **O-F (T4):** ¿el texto de D9 conserva lo que protegía la regla original (no agrupar
  subfases, trazabilidad test↔postcondición, diff revisable)?

## Entrega
Veredicto (aprobable / aprobable con cambios / no aprobable), bloqueantes (BL-n),
recomendaciones (R-n) con razón y archivo:línea, y qué pasaría a deuda.
