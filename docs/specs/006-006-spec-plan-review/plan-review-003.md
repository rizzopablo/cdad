# Dictamen draft-003: requiere cambios

Revisión de diseño, no aprobación ni autorización para implementar.

## B-3: cerrado en el diseño

`plan.md:57,66-69` y `spec.md:167-169` conservan las **16 claves actuales**, añadiendo `exemption` únicamente cuando se declara.

Contrastado con `skills/cdad-cycle/scripts/cdad_packet.py:5045-5079`: sin exención, la serialización canónica y su digest permanecen idénticos para **gate, closure y disposition**. El cálculo con las funciones actuales produjo:

```text
gate: no-exemption payload_equal=True key_equal=True keys=16
closure: no-exemption payload_equal=True key_equal=True keys=16
disposition: no-exemption payload_equal=True key_equal=True keys=16
```

Esto cierra B-3 **como defecto del plan**. La verificación del producto futuro sigue pendiente del RED y del recorrido declarado.

## B-4 — Volver a una exención histórica puede devolver éxito sin registrar el cambio

**Verdict: BLOCKING · Bucket: m · Severidad: Required**

**Ubicación:** `docs/specs/006-006-spec-plan-review/plan.md:58,65`; `spec.md:172,196,232`.

El diseño conserva expresamente la decisión de no-op, pero exige que cambiar la exención —también retirarla— nunca termine en éxito sin registrar.

Existe este recorrido realista, manteniendo iguales los restantes insumos:

1. **A:** aprobación sin exención.
2. **B:** aprobación con exención, mediante `--supersedes A`.
3. Se solicita retirar la exención, mediante `--supersedes B`.

El tercer payload recupera exactamente la clave de **A**. `_registered_transition` busca en **todo** el historial (`cdad_packet.py:5098-5107`), y la rama conservada devuelve no-op **antes** de examinar `--supersedes` o la aprobación vigente (`:5766-5770,5789-5829`).

**Consecuencia:** rc=0 sin nueva entrada; B continúa vigente y la retirada solicitada no queda registrada. Lo mismo ocurre al regresar a un valor de exención anterior.

Comprobación con las funciones actuales y el bloque condicional propuesto:

```text
A(no exemption) -> B(exemption,supersedes A) -> A: historical_match=True
unchanged no-op branch returns before supersedes/approval checks
```

**Movimiento propuesto:** distinguir el replay histórico del intento de sustituir la aprobación vigente, sin cambiar las claves históricas. Ante esa colisión, el rechazo explícito satisface la alternativa que ya permite PD-9.

**Cierre verificable:** incorporar A→B→A —retirada y restauración de un valor anterior— y exigir registro válido o rechazo explícito, nunca no-op exitoso que deje B vigente. Conservar los replays históricos de B-3.

## Retr trazabilidad

Citas de esta tabla relativas a `docs/specs/006-006-spec-plan-review/`.

| Garantía | Trazabilidad y resultado |
|---|---|
| **E1: spec sin plan** | PD-1/3/5/7/10/12–15 → U1–U4/U6 (`plan.md:35-50,76-96,111`). Forma explícita, sin tareas artificiales; aceptación real pendiente. |
| **E2: spec + plan** | PD-1–5/8/13/15 → U1/U6 (`:43-44,112,114`). Ambos digests fijados; checks sobre el plan. |
| **E3: otra feature** | PD-1/5/6/7/13 → U1/U2/U6 (`:76,113`). Ejecución A separada del objeto B; destino A y rechazo de B declarados. |
| **E4: corrección focal** | PD-8/10/12/13 → U2/U3/U6 (`:76,85,114`). Comparación de bytes y re-review focal; no se atribuye esa función al CAS. |
| **E5: no aprobación** | PD-7/14/15 → U1/U3/U6 (`:46,90-91,115`). Dictamen y autorización permanecen separados. |
| **E6: intención incumplida** | PD-10/12/13 → U2/U3/U6 (`:76-78,85,116`). Juicio semántico y evidencia textual declarados; no certificación automática. |
| **005-014 PD-23** | `plan.md:66-69,137`: fórmula histórica preservada y regresión incorporada. Oráculo vigente: `tests/test_005_014_closure_replay.py:220-275`. |
| **006-005 PD-19(b)** | Mismo mecanismo y regresión incorporada. Oráculo vigente: `tests/test_006_005_u5_disposition_failed.py:376-411`. |

**Garantías aprobadas:** no identifiqué otra PD/INV aprobada contradicha sin declaración en el alcance focal. La excepción a la normalización uniforme de 005-012 PD-10 está declarada en `spec.md:293`; PD-23 y PD-19(b) no necesitan enmienda. **B-4 contradice PD-9/INV-12 del propio borrador.**

## Validación estructural y evidencia

Separada del juicio semántico:

- `plan-tasks`: JSON válido, seis tareas, dependencias existentes y acíclicas; validación por tarea presente.
- Hash del contrato, política y tres fuentes de instrucciones: coinciden con el paquete.
- Commit observado: `593a6f693890cc24190fdd4536ee2d6b8737afe7`.

Comandos de comprobación ejecutados:

```text
sha256sum docs/specs/006-006-spec-plan-review/plan.md docs/cdad-policy.json
sha256sum skills/cdad-cycle/packets/common.md skills/cdad-cycle/packets/roles/reviewer.md skills/cdad-cycle/packets/substages/reviewer-plan-review.md
sha256sum docs/specs/006-006-spec-plan-review/spec.md
git rev-parse HEAD
git status --short
git log --oneline 7f39e24..HEAD -- skills/ sources/ agents/ scripts/ assets/
python3 -B -
```

El último comando analizó el bloque JSON y extrajo por AST las funciones de identidad y búsqueda; sus resultados relevantes figuran arriba. No ejecutó una implementación futura.

**Archivos modificados:** ninguno; estado Git final igual al inicial.  
**Commit propio:** ninguno. **Suite completa:** no ejecutada.

## Abstentions

- No certifico RED/GREEN, producto instalado ni aceptación real: siguen pendientes de implementación.
- No está acreditada la independencia de familia de modelo respecto del autor.

**Veredicto final: requiere cambios por B-4; B-3 queda cerrado en el diseño.**