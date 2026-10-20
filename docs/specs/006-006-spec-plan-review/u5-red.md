# RED de U5 (006-006-spec-plan-review) — informe del test-writer

## 1. Archivo modificado (único)

| Archivo | Estado |
|---|---|
| `tests/test_006_006_u5_exemption_record.py` | **NUEVO**, 1321 líneas, 14 tests |

Commit: **`96c99f2`** — `test: 006-006 U5 RED — exencion en la identidad de la transicion` (sólo `tests/`: `1 file changed, 1321 insertions(+)`). Sin `--no-verify`, sin `stash`, sin `push`. `docs/.cdad-state.json` (modificado), `docs/planning/` y `findings/*` (sin trackear) siguen **sin tocar** — no son míos.

## 2. Mapa test → postcondición (14 tests)

| # | Test | PD / reglas | Estado hoy |
|---|---|---|---|
| 1 | `test_pd9_exemption_flags_write_the_four_fields_in_the_entry` | PD-9 (entrada: `exempted_by`, `reason`, `requested_by`, `delegated`) | 🔴 RED |
| 2 | `test_pd9_without_the_flags_the_entry_carries_no_exemption_field` | PD-9 control negativo (R-11: «ni una clave, ni un valor») | 🟢 control |
| 3 | `test_pd9_flags_outside_the_gate_class_are_rejected_naming_the_class` | PD-9 admisibilidad (fuera de `gate` ⇒ rc≠0 nombrando la clase, sin efectos) | 🔴 RED |
| 4 | `test_pd9_exemption_entry_does_not_enable_construction` | PD-9 + PD-14 (la exención no habilita construir por sí sola) | 🔴 RED |
| 5 | `test_pd9_approval_with_exemption_stays_vigente_for_the_closure` | PD-9 + **V-4** (vigente para el cierre PD-8(b); 2ª aprobación sin `--supersedes` sigue rechazada) | 🔴 RED |
| 6 | `test_pd9_payload_carries_the_exemption_block_with_exactly_the_declared_fields` | PD-9 + R-11/R-12 (bloque `exemption` con exactamente lo declarado; clave recomputada) | 🔴 RED |
| 7 | `test_pd9_payload_block_carries_only_the_declared_fields` | PD-9 + R-12 (subconjunto ⇒ el bloque lleva sólo esos campos, no `null`) | 🔴 RED |
| 8 | `test_pd9_identical_repetition_with_the_same_exemption_is_a_noop` | PD-9 + PD-11 + R-14(a) | 🔴 RED |
| 9 | `test_pd9_repetition_that_changes_the_exemption_is_not_a_noop` | PD-9 + B-2 + INV-12 (se registra por `--supersedes` **o** se rechaza; nunca rc=0 sin registrar) | 🔴 RED |
| 10 | `test_pd9_two_revisions_gate_keeps_the_identity_and_the_replay_is_a_noop` | PD-9 + R-13 + D-14 + V-7 (**control**) | 🟢 control |
| 11 | `test_pd9_two_revisions_closure_keeps_the_identity_and_the_replay_is_a_noop` | PD-9 + R-13 + **PD-23** + V-7 (**control**) | 🟢 control |
| 12 | `test_pd9_two_revisions_disposition_keeps_the_identity_and_the_replay_is_a_noop` | PD-9 + R-13 + **PD-19(b)** + V-7 (**control**) | 🟢 control |
| 13 | `test_pd9_aba_walk_rejects_the_return_to_the_previous_payload` | PD-9 + R-14(b) + D-15 + V-8 (A→B→A: ambas ramas de rechazo, estado byte-idéntico, vigente comprobada con el lector, replay de la vigente) | 🔴 RED |
| 14 | `test_pd9_aba_walk_registers_the_return_with_a_distinguishable_value` | PD-9 + R-14(b) + D-15 (la salida que el rechazo declara: registro con valor distinguible → entrada nueva, vigente, **sin** bloque `exemption`) | 🔴 RED |

Cobertura de los `observable_checks` del paquete: 1→#1, 2→#2+#3, 3→#4, 4→#5, 5→#6+#7, 6→#8, 7→#9, 8→#10/#11/#12, 9→#8+#11/#12, 10→#13, 11→#14.

## 3. A-1 — **ninguna** (plan §4)

Este RED **no reemplaza ningún oráculo vigente**: **añade** casos. Los oráculos de identidad recomputan la clave desde el payload escrito y comprueban campos sueltos (no fijan el conjunto de claves ni un digest literal) → siguen verdes sin cambio. `tests/test_005_014_closure_replay.py` y `tests/test_006_005_u5_disposition_failed.py` **no se tocan: se ejecutan** (regresiones verdes). Ningún fichero con el fixture compartido `DRAFT_PLAN_RELPATH` fue tocado (fixtures propios).

## 4. Comandos y salida

**Focal (RED declarado):**
```
$ python3 -m pytest tests/test_006_006_u5_exemption_record.py -q
10 failed, 4 passed in 18.10s
```
Motivo del fallo (idéntico en los 10): **`AssertionError` de contrato**, nunca import/sintaxis/setup:
```
PD-9 violada (las cuatro banderas): el CLI no conoce las banderas de la exención
(`--exempted-by`, `--exemption-reason`, `--requested-by`, `--delegated`): la invocación
murió en el parser (error de uso) sin ejercer la postcondición:
'ERROR: cdad_packet.py: unrecognized arguments: --exempted-by Owner Demo (fixture 006-006 U5) ...'
```
Los 4 verdes son los **controles declarados** (recorrido de dos revisiones ×3 + control negativo), tal y como la ficha U5 los declara: «pasan con el producto vigente y deben seguir pasando con el nuevo»; el A→B→A es, en cambio, un caso que falla al abrir el RED.

**Regresiones de la ficha (12 ficheros, verdes):**
```
$ python3 -m pytest -q tests/test_005_012_t1_... tests/test_005_012_t2_... tests/test_005_012_t3_... \
    tests/test_005_012_t4_... tests/test_005_012_t5_... tests/test_005_014_closure_replay.py \
    tests/test_006_005_u5_disposition_failed.py
71 passed in 89.41s

$ python3 -m pytest -q tests/test_005_001_t2_replace_packet.py tests/test_005_001_t3_idle.py \
    tests/test_006_003_rf_review_fixes.py tests/test_006_003_rf2_review_fixes.py tests/test_packet_prepare.py
41 passed in 116.73s
```

**Corrida final focal + regresiones acopladas:**
```
$ python3 -m pytest -q tests/test_006_006_u5_exemption_record.py tests/test_005_012_t2_gate_authority.py \
    tests/test_005_012_t5_approval_vigency.py tests/test_005_014_closure_replay.py tests/test_006_005_u5_disposition_failed.py
10 failed, 36 passed in 54.38s
```

**`make validate`:** `Assert PASS: 168 · Assert FAIL: 1` → **F11 = `scripts/validate-subagents.sh`**. **Fallo preexistente y ajeno a este RED**: se reproduce idéntico sobre un árbol limpio `git archive HEAD` (sin mi fichero): *DRIFT* de la instalación del HOME (`<home>/.claude/skills/cdad-cycle/scripts/cdad_packet.py`) y «`cdad-reviewer.md` declares model». No lo toco (está fuera de mi write scope) y lo declaro. El resto de validadores, incluido el escaneo de patrones sensibles sobre `tests/`, pasan con mi fichero.

## 5. Cómo se resuelve «el producto anterior» (y por qué no es una simulación)

`git archive eabe2801683fe35852672d9afcad3d4c5c728cde skills` → directorio temporal (nunca la instalación del HOME). El commit está **congelado** en el test: es la revisión del producto vigente cuando se abrió este RED (antes de U5), y seguirá siendo el «anterior» cuando U5 se implemente.

El recorrido de dos revisiones usa **dos copias byte a byte idénticas** del mismo proyecto (mismo `execution_id`, `packet_id` y bytes citados): el producto anterior registra en una, el vigente en la otra ⇒ los payloads son comparables byte a byte, y además el vigente **repite** la orden sobre la entrada del anterior (no-op, misma entrada nombrada, sin segunda entrada, state byte-idéntico). La **fórmula de identidad anterior** queda además congelada como literal en el test (las 16 claves + la serialización canónica), y la clave se recomputa desde el payload escrito (mismo oráculo de 005-012 PD-10).

## 6. Interpretaciones declaradas (para que las juzgue el orquestador)

1. **Vigencia por el lector**: A y B comparten pin (mismo contrato) porque, si el contrato cambiase entre A y B, la aprobación de A dejaría de ser vigente por la regla vigente y el rechazo de colisión no se dispararía. El lector (prepare de un rol de construcción) se sondea **sobre una copia del proyecto** (la sonda publica un paquete y mutaría el state que el recorrido compara byte a byte). Tras los rechazos, lector rc=0 + state byte-idéntico ⇒ la vigente sigue habilitando.
2. **Mensajes**: el contrato fija el *contenido* (claves nombradas, marcador `state incoherent`, las dos salidas), no la prosa; el rechazo de colisión se acepta con cualquier forma léxica que describa las dos salidas («valor distinguible» / «reconciliar»).
3. **`prepare` y la errata B-5**: el lector se usa como lector real (efecto observable), sin pedirle que distinga qué entrada histórica presentó el solicitante.
4. **Aislamiento de fase**: no leí código de implementación de `skills/cdad-cycle/scripts/`; el payload de identidad lo obtuve **en negro** (subproceso) y lo congelé como literal. La suite completa **no** la corrí (la corre una vez quien cierra).

## 7. Lo que el implementer tiene que hacer para poner este RED en verde

1. Parser: `--exempted-by`, `--exemption-reason`, `--requested-by`, `--delegated`, admisibles **sólo** con `--transition gate` (fuera ⇒ rc≠0 nombrando la clase, sin efectos).
2. Entrada `gate`: sumar `exempted_by`, `reason`, `requested_by`, `delegated` **planos** sólo si se declaran.
3. Payload: bloque `exemption` **condicional** con exactamente los campos declarados; sin exención el payload sigue siendo **byte-idéntico** al anterior (16 claves) ⇒ identidades históricas intactas (sin enmienda de 005-014 PD-23 ni 006-005 PD-19(b)).
4. Rama de no-op **calificada** (R-14): replay de la vigente ⇒ no-op; colisión con una entrada histórica **no** vigente mientras compite una vigente ⇒ rechazo explícito (con `--supersedes`: rechazo de colisión que nombra la clave que colisiona, la de la vigente y las dos salidas; sin `--supersedes`: el rechazo vigente de una sola aprobación).