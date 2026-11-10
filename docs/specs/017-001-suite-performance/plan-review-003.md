# Revisión focal del borrador 017-001 v3

**Dictamen:** no encontré bloqueantes en la corrección focal. El borrador es **presentable al dueño para su decisión de aprobación**, sujeto a que el orquestador fije en el gate la identidad de ambos documentos indicados abajo. Esta revisión no los aprueba ni autoriza la implementación.

## Hallazgos

No identifico hallazgos nuevos con confianza suficiente para reportar.

### Cierre del bloqueante anterior

El bloqueante de `plan-review-002.md` queda **cerrado en el borrador leído**:

- PC-8 exige ejecutar y medir primero la optimización serial, pero no alcanzar todavía el objetivo final (`spec.md:367-368`).
- T5 entrega ese resultado medido a T6 aunque sea insuficiente; T6 puede evaluar el paralelismo sin presuponer que sea útil o seguro (`plan.md:343-388`).
- La aceptación sigue exigiendo el objetivo acordado y todas las garantías (`spec.md:413-421`; `plan.md:390-408`).
- Una obligación de mantener toda la solución serial requiere decisión expresa del dueño; no resulta de la dependencia entre tareas (`spec.md:149-153,372-373`).

En el contraste focal no encontré contradicciones nuevas entre spec y plan ni una ampliación de la promesa del epic. La spec conserva las doce postcondiciones, los invariantes y los VERIFY; el plan conserva las tareas T1–T7 y sus dependencias.

## Identidad y evidencia

Documentos efectivamente leídos:

- `docs/specs/017-001-suite-performance/spec.md` — SHA-256 `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e`
- `docs/specs/017-001-suite-performance/plan.md` — SHA-256 `781dd61ca268f36979778d34a2083432c05c279f2862acb31e21a1bc3a890ca1`

La ruta C se validó: `validate-request` y `validate-packet` terminaron sin errores, y `render --route C` reprodujo la identificación recibida. El contexto declara versión 2.

Comprobaciones ejecutadas:

```text
python3 scripts/cdad_packet.py validate-request --request .cdad/packets/017-001-suite-performance-reviewer-plan-review-003/REQUEST.json
python3 scripts/cdad_packet.py validate-packet --request .cdad/packets/017-001-suite-performance-reviewer-plan-review-003/REQUEST.json --packet .cdad/packets/017-001-suite-performance-reviewer-plan-review-003/PACKET.md
python3 scripts/cdad_packet.py render --request .cdad/packets/017-001-suite-performance-reviewer-plan-review-003/REQUEST.json --route C
sha256sum docs/specs/017-001-suite-performance/{spec.md,plan.md}
git status --short
git rev-parse HEAD
```

Los hashes son los indicados arriba. `git status` mostró `docs/.cdad-state.json` modificado; HEAD observado: `ae6d2c6b901416181c55955b1302f8e5355aa1bf`.

No ejecuté tests ni suite completa: esta es una revisión de borrador. **Archivos modificados por esta revisión: ninguno. Commit creado: ninguno.**

## Abstentions

- El despacho fija contractualmente el hash de la spec, pero no el del plan. El hash calculado identifica el plan leído; no acredita por sí solo que el gate haya fijado ambos documentos para la aprobación.
- No puedo determinar todavía qué preparación dominará el costo, si el objetivo futuro será alcanzable ni si el paralelismo será útil y seguro: faltan la base y la evidencia correspondientes.
