# cdad-007-systematic-debugging — Review (Etapa 4)

> **Caveat de aislamiento (registrado):** review INLINE por el orquestador
> (runtime `delegate` roto). HITL delegado por Pablo. Checks mecánicos
> re-corrídos por el orquestador post-GREEN.

## Layer 1 — Verificación contra spec

| Postcondición | Estado | Evidencia |
|---|---|---|
| P1 (reference, 7 piezas) | ✅ | `stage-debugging.md` nuevo (~160 líneas): ley de causa raíz, loop rojo = RED, 4 fases (diagnóstico/minimizar/hipótesis rankeadas/fix único), defense-in-depth + condition-based-waiting, 3+ → STOP → ADR, roles (implementer diagnostica / test-writer regresión / Fagan-Five Whys stubborn), anti-racionalización 8 filas, cuándo NO aplica |
| P2 (enlaces) | ✅ | SKILL.md:421 (tabla de lectura); stage-3-tdd.md:113 (§3.2 antes de re-delegar); stage-5-merge.md:31 (§5.1, mención ANTES de "volvé a Etapa 3" — awk del oráculo) |
| P3 (AP-18) | ✅ | anti-patterns.md: AP-18 con 3 sub-secciones, cita la reference |
| Guard (C4a-C4g) | ✅ | Sub-fases RED/GREEN/REFACTOR, gates etapa 3/5, §5.6, §5.1 intactos |
| R1-R5 / sin regresión | ✅ | 23/23 + 19/19 + 23/23 + 121/121 re-corrídos |

## Layer 2 — Calidad

- **Coherencia conceptual**: la síntesis "loop rojo = sub-fase RED" está bien
  anclada — stage-debugging no crea una metodología paralela al TDD, la
  alimenta (el fix de debugging entra por RED normal).
- La regla 3+ → ADR conecta con el mecanismo existente (`docs/adr/`,
  excepción "spec entero mal → Descubrimiento") sin duplicar gates.
- Nota de implementación aceptable: C1f usa BRE con `?` literal — el
  implementer resolvió con nota de notación en el header del skill, no
  tocando el oráculo. Documentado.
- H1 (hallazgo, resuelto inline): revisión de §5.1 confirma que el énfasis
  "Sin excepciones" se conservó con el orden correcto (diagnóstico → vuelta
  a Etapa 3).

## Hallazgos

| # | Severidad | Problema | Estado |
|---|---|---|---|
| H1 | advisory | El C2c awk valida orden pero el texto de §5.1 quedó con una oración larga (legibilidad, no contrato) | Aceptado tal cual |
| H2 | advisory | Dogfood: la reference no se ejercitó en un bug real aún | Próximo fallo de suite la valida |

## Veredicto

`aprobado` — 0 bloqueantes, 2 advisory.

LISTO. Resumen: 0 bloqueantes, 2 opcionales.
