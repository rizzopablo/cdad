
```
cdad_continuity: reference digest mismatch:
docs/specs/003-006-runtime-adoption/dispatch-ledger.md changed since the checkpoint
(expected 63fb39f1657ad29b807cc63652cbde616b3bdd1b9ce154206fc4332bd49b92e5,
 got      1a7e196deea7a10dfeee4264a19ed591297f6c63a2982ad422a9776859d08252)
```

`resume`, `reconcile` y `trigger` abortan **antes** de emitir JSON: el guardrail de integridad de referencias corta la lectura. Por lo tanto no tengo objetivo, autoridad, decisiones, stage ni próxima acción provenientes del checkpoint. Respondo con lo que sí es evidencia verificable (la salida anterior) y marco explícitamente lo que NO sé.

---

**1) Objetivo**
No disponible. El checkpoint no se materializó. Lo único inferible de la evidencia es el *scope nominal* del execution context: feature/epic `003-006-runtime-adoption`, execution `exec-003-006-runtime-adoption-001`, y un packet de reviewer en revisión (`…-reviewer-review-005`). Eso es nomenclatura, no objetivo.

**2) Autoridad vigente y de dónde sale**
No disponible. La autoridad se resuelve a partir del contenido del checkpoint/execution context, y ninguno de los tres comandos lo devolvió. No puedo citar rol autorizado, mandato ni gate vigente sin inventarlo. Lo único firme: **la autoridad del checkpoint está suspendida** por el mismatch de digest.

**3) Decisiones tomadas con su razón**
Ninguna decisión de ciclo. La única decisión que tomé es procedimental y forzada por la evidencia:
- **No despachar, no tocar state, no leer otros archivos** — instrucción explícita del usuario + los tres comandos de lectura fallaron.
- **No tratar el error como “no hay trabajo”**: el fallo es un guardrail de integridad, no un estado vacío. Reportarlo, no interpretarlo.

**4) Incertidumbres**
- Qué cambió en `dispatch-ledger.md` y **quién** lo cambió (mutación legítima post-checkpoint vs. alteración fuera de banda).
- Si el checkpoint quedó inválido de forma permanente o basta re-anclar el digest.
- En qué stage está la feature y en qué estado quedó el packet `…-reviewer-review-005` (¿emitido? ¿materializado? ¿pendiente?).
- Si el reviewer llegó a correr y si hubo resultado (review.md) antes de la mutación del ledger.
- Si los digests esperados de otras referencias también están desfasados (el guardrail cortó en la primera).

**5) Próxima acción concreta**
Reportar el bloqueo. La acción *técnica* que desbloquea es re-anclar/refrescar el digest de referencia del checkpoint (o reconciliar la mutación del ledger), pero **eso es escritura de state y estoy en modo solo lectura**, así que **no la ejecuto**. Queda como acción propuesta para el orquestador con permiso de escritura.

**6) ¿Hay algo que deba repetir o re-despachar?**
**No puedo justificarlo con `reconcile`, porque `reconcile` no emitió salida** — falló con el mismo digest mismatch. Su único valor probatorio aquí es negativo y contundente: **el canal de reconciliación está ciego**, luego no hay base para afirmar “repetir”, “re-despachar” ni “no hacer nada” respecto del packet `…-reviewer-review-005`. Despachar sin ese dato sería adivinar. Conclusión: **re-despacho indeterminado por falta de evidencia, no por ausencia de trabajo.**

**7) ¿Necesito preguntarle algo al usuario?**
**Sí.** Concretamente:
- ¿Cómo procedo con el mismatch: **(a)** re-anclar el digest de referencia del checkpoint (aceptar el ledger actual como nuevo baseline) o **(b)** tratar el cambio de `dispatch-ledger.md` como mutación sospechosa y auditarla antes de continuar?
- ¿Me autorizás un modo de solo-lectura ampliado (leer el checkpoint y el ledger directamente) para reconstruir el estado, o preferís re-ejecutar la continuidad vos mismo tras resolver el digest?
- ¿Hay trabajo de reviewer en vuelo que deba considerarse no confiable hasta reconciliar?

**8) Qué me faltó que el checkpoint no me dio**
El checkpoint **no me dio nada sustantivo**: solo un error de integridad. Faltó, literalmente:
- objetivo atómico y postcondición del packet,
- rol autorizado y mandato/authority,
- stage y gate actual,
- estado del packet `review-005` (emitido/pendiente/resultado),
- decisiones previas y su razón,
- próxima acción esperada,
- referencia válida de `dispatch-ledger.md` (el digest esperado ya no coincide con el real).

En una línea: **tenés un checkpoint que se autodeclara inválido por integridad de referencias — el trabajo no puede reanudarse hasta reconciliar el digest, y esa reconciliación excede mi modo solo-lectura.**
