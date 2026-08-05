# Anti-patrones del epic-level

Específicos de coordinación de epics. Son aditivos a los anti-patrones de feature (`cdad-cycle/references/anti-patterns.md`); los AP-N siguen aplicando dentro de cada feature.

## EAP-1 — Plan kilométrico que nunca cierra

**Síntoma**: el planning del epic lleva más de 90 minutos. El plan supera 5 páginas. Aparecen secciones como "Apéndice A", "Anexo de consideraciones".

**Por qué es malo**: el plan light se vuelve plan pesado. La mayoría del contenido extra es especulación sobre el cómo (que es trabajo de cada feature) o sobre riesgos hipotéticos.

**Corrección**: cortás donde estás. Lo que falta queda como TBD a decidir cuando arranque la feature correspondiente. El plan se actualiza sobre la marcha.

> *"Llevamos <X minutos>. El plan ya tiene lo esencial. Lo que sigue parece más detalle del cómo de cada feature, que es trabajo del cdad-cycle, no del plan del epic. ¿Cerramos planning y arrancamos la primera feature?"*

## EAP-2 — Mini-specs dentro del plan

**Síntoma**: cada feature en la decomposición del plan tiene su propio bloque de 1 página con detalles técnicos, postcondiciones, criterios de aceptación.

**Por qué es malo**: duplica el trabajo de la spec real (que se hace en `cdad-cycle` cuando la feature arranca). El mini-spec dentro del plan envejece mal: cuando la feature arranca, el spec real puede divergir, y queda el mini-spec del plan como ruido.

**Corrección**: en el plan, una línea por feature. Suficiente para entender qué hace y por qué está en el epic. La spec se hace cuando la feature se ejecuta.

## EAP-3 — ADRs especulativos al inicio del epic

**Síntoma**: el plan incluye una sección "Decisiones arquitectónicas" con varios ADRs hipotéticos: "Vamos a usar PostgreSQL", "Vamos a separar en bounded contexts", etc., **antes** de que ninguna feature haya empezado.

**Por qué es malo**: ADRs son inmutables. Si los creás especulativamente y después la realidad de las features te dice otra cosa, tenés que crear ADR-NNN-Supersede que reemplace al original. Eso es ruido.

**Corrección**: ADRs surgen cuando la decisión es real. Si en E1 (descubrimiento) está clarísimo que "vamos a usar PostgreSQL" y eso afecta a varias features, vale crear UN ADR del epic. Pero no llenes el plan con 5 ADRs especulativos. Cuando dudes, **diferí**: ADR cuando la feature lo necesita.

## EAP-4 — Saltar la integración cross-feature

**Síntoma**: las features individuales pasaron sus E2E. El usuario quiere ir directo a closure. *"Ya están todos verdes, ¿qué más?"*

**Por qué es malo**: tests individuales no cubren el flujo cross-feature. Bugs cross-feature solo aparecen en integración.

**Corrección**: identificá los criterios de aceptación cross-feature del plan y exigí E2E para cada uno. Si tu argumento es "no queda tiempo", al menos exigí UNO: el flujo principal del epic.

## EAP-5 — Sub-epics que aparecen sin pedir (epic creep)

**Síntoma**: durante el epic, aparece "una funcionalidad relacionada" que no estaba en el plan, y se mete al epic actual en lugar de quedar como epic separado o feature standalone posterior.

**Por qué es malo**: el scope del epic crece sin control. El epic nunca cierra porque "siempre queda algo más".

**Corrección**: si la funcionalidad nueva NO está en el scope original del plan, queda fuera del epic. Opciones:

- Crear feature standalone para hacerla después del epic actual.
- Crear epic siguiente con esa funcionalidad como base.
- Si es realmente urgente y bloquea el epic actual: actualizar plan con reaprobación del usuario, agregar la funcionalidad como feature explícita.

NO la metas silenciosamente. Es la principal causa de epics que tardan el doble de lo previsto.

## EAP-6 — Trackeo del epic solo en cabeza

**Síntoma**: el state file no se actualiza. `epic_features` queda con datos viejos. `progress.md` no refleja el estado real.

**Por qué es malo**: cuando volvés al epic después de unos días, no recordás dónde estabas. Se pierde tiempo redescubriendo.

**Corrección**: cada cierre de feature actualiza el state. Cada cambio de plan actualiza el state. La actualización es responsabilidad del coordinador del epic; vos como skill la hacés cuando corresponde.

## EAP-7 — Coordinación con `cdad-cycle` rota

**Síntoma**: el usuario está en `cdad-cycle` trabajando una feature del epic y nunca vuelve a `cdad-epic` para coordinar la siguiente. Las features se completan pero el epic queda en `features-loop` indefinidamente.

**Por qué es malo**: pierde la coordinación. La feature siguiente podría tener dependencias que el plan considera pero que el usuario olvidó.

**Corrección**: en el handoff de feature (cuando delegás a `cdad-cycle`), recordale al usuario que vuelva al `cdad-epic` cuando la feature cierre. En `cdad-cycle`, el cierre de feature debe sugerir volver al coordinador del epic si pertenece a uno.

(Nota: esto requiere cambio menor en `cdad-cycle`; ver `references/coordination-with-cdad-cycle.md` o equivalente.)

## EAP-8 — Closure ritualista

**Síntoma**: closure del epic termina siendo "marca todo done y mergea", sin retrospectiva ni reflexión sobre qué se aprendió.

**Por qué es malo**: pierde el valor del cierre. La retrospectiva breve (3 puntos de "lo que funcionó", 3 de "lo que se complicó", 3 de "aprendizajes") es lo que hace que el próximo epic sea mejor.

**Corrección**: insistí en la retrospectiva breve. No es ritualismo; es ROI sobre el trabajo invertido. Si genuinamente no hay nada que retrospectar, marcalo: *"Sin hallazgos relevantes para retrospectiva."*

---

## Cómo usar este archivo

Cargalo cuando detectes señales. Citá el código (`EAP-N`) en tu mensaje al usuario:

> *"Estamos en EAP-1: el plan está creciendo más allá de lo light. ¿Cerramos lo que tenemos y arrancamos features?"*

No lo cargues preventivamente.
