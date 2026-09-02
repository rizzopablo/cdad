# Contrato de Veredicto — Tuple de 4 campos (G2, Split the Labor 2608.14509)

> **Fuente:** https://arxiv.org/abs/2608.14509 (Wu, Atlassian — "Split the Labor:
> Separating Evidence Interpretation from Decision Aggregation", Prop 1-4 + §4.6).
> **Motivación:** la agregación ad-hoc de hallazgos de review (contar BLOQUEANTES
> a mano, sumar pesos fijos) hereda count-scale drift + misweighting que ningún
> umbral absorbe. Este contrato fija la INTERFAZ entre el reviewer (capa 1,
> interpretación aislada) y el orquestador (capa 2, agregación + priorización),
> sin cambiar quién decide: la priorización sigue siendo humana o del dueño del
> proceso (stage-4-review.md Capa 2).

## El tuple (por hallazgo)

Cada hallazgo de una review CDAD emite exactamente 4 campos:

| Campo | Símbolo | Qué es | Regla dura |
|-------|---------|--------|------------|
| Veredicto | Ŷ | `BLOQUEANTE` \| `OPCIONAL` \| `ABSTENER` | El reviewer NUNCA emite "no sé" como OPCIONAL. Si no puede juzgar (contexto faltante, fuera de su alcance), emite `ABSTENER`. Errar comprometido cuesta más que no responder. |
| Bucket de confiabilidad | b | `h` \| `m` \| `l` estimado por propiedades OBSERVABLES de la lectura | Prohibido elicitarlo ("mi confianza es 0.8"). Se deriva por regla determinística (abajo). |
| Rationale | r | Problema concreto, mecanismo causal | Debe ser verificable contra el código/spec, no opinión. |
| Provenance | a | `archivo:líneas` exactas + ref a postcondición o convención violada | Sin provenance, el hallazgo no entra en la agregación (peso 0). |

## Regla de bucket por observables (no elicitada)

Puntos acumulables, bucket = suma:

| Propiedad observable | +puntos |
|---------------------|---------|
| Modelo de familia DISTINTA al implementer (declarado al inicio) | +1 |
| Diff completo en contexto (no snippets sueltos) | +1 |
| Rationale grounded con cita exacta `archivo:líneas` verificable | +1 |
| Spec + convenciones en contexto | +1 |
| 0-1 puntos → `l` · 2 puntos → `m` · 3-4 puntos → `h` | |

El bucket NO mide calidad del reviewer: mide la CALIBRACIÓN ESPERADA de la
lectura por condiciones de la sesión — exactamente el diseño del paper
(buckets desde propiedades de la fuente, nunca confianza elicitada).

## Agregación (aritmética fija, diagnóstico — no decisión)

El orquestador NO decide por aritmética; usa la agregación como **diagnóstico
de drift** y pasa el reporte a Capa 2 (priorización humana) intacto.

1. **LLR pooling (Prop 4):** por cada BLOQUEANTE, evidencia
   ℓ = log(α_b / β_b) con α_b = tasa de acierto esperada del bucket,
   β_b = tasa de falso positivo esperada. Defaults conservadores a ajustar
   por datos (G3): h=(0.8, 0.1), m=(0.6, 0.3), l=(0.4, 0.5).
2. **κ-dedupe por bloques dependientes (§4.6):** hallazgos del MISMO commit,
   misma sesión o misma clase de falla NO acumulan como corroboración
   independiente — contarlos como 1 bloque (κ = 1/(1+ρ(|B|−1)), ρ implícito 1).
3. **ABSTENER no aporta evidencia** pero se reporta por separado:
   N abstenciones = señal de que la review tocó zonas fuera de alcance
   (esto ES información para Capa 2, no ruido).
4. **Salida del agregador:** `X bloqueantes · Y opcionales · Z abstenciones ·
   score-LLR total (→ drift check: comparar precisión por nº de fuentes,
   predicción falsable #1 del paper)`.

Ejemplo del drift que esto previene (Prop 2): 2/3 fuentes afirmando con
prior 0.2 → posterior 0.39; 2/6 → 0.001 — mismo conteo, 300× de diferencia.
Un review de 12 BLOQUEANTES no es 6× más severo que uno de 2 si vienen del
mismo commit bloque (κ) y del mismo bucket (ℓ idénticos).

## Aplicación actual

Este contrato aplica al ciclo `cdad-cycle`: el reviewer de Etapa 4 (cualquiera
de las variantes, genérica u Odoo, en cualquier runtime) emite el tuple de 4
campos por hallazgo; el orquestador lo usa como diagnóstico de drift al pasar
el reporte a la Capa 2 humana. No se extiende automáticamente a usos fuera
del ciclo (otros pipelines de review, otros formatos de auditoría) — cada
adopción nueva se evalúa por separado contra su propio contexto.

## Anti-scope

- NO cambia la Capa 2 de stage-4-review.md: la priorización sigue siendo
  humana o del dueño del proceso. La aritmética es diagnóstico, no veto.
- NO toca `cdad-epic` — solo `cdad-cycle`; extenderlo al nivel de epic requiere aprobación separada del dueño del proceso.
- Los defaults α_b/β_b son placeholders a estimar por datos (G3), no
  calibrados por benchmarks.

## Conducta del reviewer ante push-back (reconsideración)

Cuando el receptor emite push-back con evidencia (ver
`receiving-feedback.md`), el reviewer hace **steelman ANTES de retractar** un
hallazgo — «¿cuál es el caso más fuerte de que sigue válido dado este
contexto?» — y solo lo revierte con motivo escrito. 2+ reversals en una misma
review = yellow flag de capitulación → segunda pasada en sesión fresca. La
reconsideración re-emite el hallazgo con el mismo tuple de 4 campos: nada de
esto cambia el formato del veredicto.

**Estado:** descriptor mínimo activo en cdad-cycle (template de reviewer +
re-entry). G3/G4 del deep-read 2608.14509 quedan abiertos (estimación de
tasas por datos; bloques de dependencia en DCPM cluster weights).