# Tema 3: Debugging sistemático — investigación (02 Sep 2026)

## Fuentes revisadas

| Fuente | Qué aporta |
|---|---|
| obra/superpowers `systematic-debugging/SKILL.md` (283 líneas, leído completo) | Ley de hierro (sin causa raíz no hay fix), 4 fases, regla 3+ fixes → arquitectura, red flags, tabla de racionalizaciones |
| obra/superpowers auxiliares (leídos completos): `root-cause-tracing.md`, `condition-based-waiting.md`, `defense-in-depth.md`, `find-polluter.sh` | Tracing hacia atrás por la call chain hasta el trigger original; fix en la fuente + defense-in-depth (validación por capas); reemplazar timeouts arbitrarios por polling de condición; bisección de test polutor |
| **Hermes Agent** (adaptación de superpowers, hermes-agent.nousresearch.com) — la más valiosa | **"The Feedback Loop Rule"**: antes de leer código para armar teoría, existir un loop de reproducción tight (un comando que va rojo con el síntoma EXACTO y verde solo al arreglar) — "adivinar sin loop rojo-capaz ES el failure mode". Minimización del repro (cortar de a un elemento hasta que quitar cualquiera lo ponga verde). **Hipótesis rankeadas** (3-5, ordenadas por verosimilitud × baratura de falsar) vs. una sola. Checklist de completitud de fase 1. Logs con tag único para cleanup (`[DEBUG-a4f2]`). Debugger/REPL > 10 logs |
| arjenschwarz/agentic-coding `systematic-debugger` | Fagan inspection modificada para bugs stubborn (post-múltiples-fallos): clarificar problema → inspección línea a línea SIN arreglar → **Five Whys (3-5 iteraciones)** con supuestos explícitos → fix con side-effects y verificación. Se dispara CUANDO ya hubo 3+ fallos |
| **Microsoft AgentRx** (MSR blog, mar 2026) | Debugging de AGENTES: trajectory normalization → constraint synthesis → guarded evaluation → LLM judge sobre evidence log (no sobre raw logs). Taxonomía de 9 categorías. +23.6% localización. Lección: la evidencia estructurada antecede al juicio |
| tianpan.co (feb 2026) | Causalidad entre pasos (el paso que CAUSA ≠ el paso que MUESTRA); replay de trajectories como testing artifact |
| doanchienthangdev/omgkit | 5 fases con git bisect para regresiones, ranking hipótesis por evidencia×(1/costo), logging con formato, documentar la sesión |

## Lo que CDAD YA tiene (verificado)

- GREEN fallido → test-writer/implementer loop con sub-fases (stage-3).
- "CI falla → volvé a Etapa 3 con el output" (§5.1) — vuelve, pero SIN protocolo de diagnóstico.
- "Spec entero mal → vuelta a Descubrimiento" (excepción existente — es el antecedente del disparador de ADR).
- Evidencia empírica obligatoria (output pegado, no confianza) — ya es cultura del repo.
- AP-3 (verde sin verificación), AP-4 (implementer toca tests) — cubren síntomas de debugging mal hecho, no el procedimiento.

## Gap real

1. Sin ley de causa raíz: "volvé a Etapa 3 con el output" invita a fix-patch sin diagnóstico.
2. Sin regla de escalamiento: 3+ fixes fallidos no dispara nada (ni ADR ni retorno de etapa).
3. Sin técnicas: tracing, hipótesis rankeadas, bisect, defense-in-depth.

## Propuesta adaptada (síntesis CDAD)

**Reference nueva `stage-debugging.md`** (invocable desde GREEN fallido y CI roto en 5.1) con:

- **Ley de hierro CDAD**: sin causa raíz verificada no hay fix — y la forma CDAD de verificarla es el **tight feedback loop: RED primero** (la síntesis más fuerte: el loop rojo de Superpowers/Hermes ES la sub-fase RED de CDAD; el debug no es otra metodología, es RED con disciplina de diagnóstico).
- 4 fases adaptadas: (1) leer error completo + armar loop rojo + cambios recientes (git diff/log) + evidencia en boundaries; (2) minimizar el repro (cut-one-thing hasta que dejar de cortar lo ponga verde) + comparar con código que sí funciona; (3) hipótesis rankeadas (3-5, falsables, ordenadas por verosimilitud × baratura de falsar), una variable por vez; (4) fix único sobre causa raíz, sin "while I'm here"; defense-in-depth DESPUÉS del fix (validación por capas), condition-based-waiting para flakiness (subir tasa de repro, nunca sleep arbitrario).
- **Regla del 3+ → STOP → ADR**: escalar al usuario con la evidencia; el ADR decide bug-de-diseño vs. diseño-malo (conecta con "spec entero mal → Descubrimiento").
- **Roles**: diagnóstico = implementer (puede leer suite, no puede tocar tests); test de regresión = test-writer (si postcondición nueva) o fix de test roto (si el test estaba mal); Five Whys/inspección Fagan citados como técnica para casos stubborn.
- Tabla anti-racionalización propia + "cuándo NO aplica" (infra/flaky puro documentado con plan de monitoreo).
- **AP-18 — Fix sin diagnóstico (thrashing)**: síntoma = 2+ fixes en la misma sesión sin repro estable; corrección = reference.

**Enlaces de entrada**: SKILL.md (tabla de lectura), stage-3 (GREEN fallido → antes de re-delegar, diagnosticar), stage-5 §5.1 (CI falla → stage-debugging ANTES de volver a Etapa 3).

**Formato: cycle light** (1 feature, cdad-007; toca ~5 archivos; un solo contrato de procedimiento).
