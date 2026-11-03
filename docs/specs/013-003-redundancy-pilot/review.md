# Review 013-003-redundancy-pilot: stage 4

**Dictamen:** 1 BLOCKING (documental, PC-5) y 2 OPTIONAL. El resultado Mantener A/B/C se sostiene. La aprobación corresponde al dueño.

## Intake (ruta C)
- `PACKET.md` es byte-idéntico al render canónico de `REQUEST.json` (`render` rc=0, `cmp` rc=0).
- La identificación coincide con ambos archivos y el sha256 de la spec coincide con el contrato.
- Revisión evaluada: `027064fb`, árbol limpio.
- Desde `1e1ad7e3` el diff solo toca `docs/.cdad-state.json`, `spec.md` y `test-audit.md`. Tests y mapa quedan intactos.

## Hallazgos

### F1. Fundamento falso en la viabilidad de mutación (PC-5)
**Required. Verdict: BLOCKING. Bucket: h.**

- **Ubicación:** `docs/specs/013-003-redundancy-pilot/test-audit.md`, §7 y Resolución.
- **Evidencia:** §7 afirma alcance al CLI "vía `PACKET_CLI` en tempdir" y control "negro-caja vía los propios fixtures". Pero `tests/test_005_013_t1_unit_projection.py:124,127` fija `PACKET_CLI` en `REPO_ROOT/skills/...`; solo el proyecto fixture está en tempdir.
- **Por qué importa:** los fixtures ejercitan el CLI correcto y no inyectan ningún defecto. Para ver un fallo tuve que mutar `cdad_packet.py` en una copia, que es justo la mutación de implementación que PC-5 reserva a un encargo separado. Sin ese encargo no hay control caja negra demostrado.
- **Otro defecto:** PC-5 pide registrar "realizado, no viable o inconcluso", y "no realizado; no exigible" no es ninguno de los tres.
- **Consecuencia:** Mantener no se ve afectado, pero el registro de PC-5 descansa en un hecho incorrecto. Además, un futuro Sustituir podría heredarlo como viabilidad ya evaluada.
- **Condición de cierre:** antes del cierre, el orquestador añade una nota de corrección a `test-audit.md`. Debe indicar que el estado es "no realizado", que la viabilidad por fixtures queda inconclusa y que la inyección exige una copia mutada bajo encargo separado. `closure.md` no debe repetir "viable como control negativo caja negra".

### F2. "Contribuciones disjuntas" es excesivo
**Consider. Verdict: OPTIONAL. Bucket: h.**

- **Ubicación:** `test-audit.md` §9.
- **Evidencia:** A y B solapan en la protección frente a sobrescritura: con el guard retirado (M1) fallan los dos. Ambos pasan por el mismo guard (`cdad_packet.py:6745`), que solo mira si el archivo existe.
- **Implicación:** las aserciones de A cabrían técnicamente en el recorrido de B. Esa consolidación perdería el estado "sin despacho", cuya relevancia contractual nadie ha evaluado.
- **Mantener sigue justificado:** con el diagnóstico sin el nombre del paquete (M2) solo falla A. El `receive` y sus estados son exclusivos de B, y PC-1 admite Mantener.
- **Remedio:** en el cierre, escribir "contribuciones distintas con solape en la conservación del pin y los bytes".

### F3. Citas imprecisas
**Nit. Verdict: OPTIONAL. Bucket: h.**

`test_pd1…:71-77` es en realidad el docstring de módulo, sin relación con un `test_pd1`. La cita `pc-map.json:446-475` difiere de la `446-474` de la spec. No afecta al resultado.

## Verificación del objetivo

| Punto | Resultado |
|---|---|
| (a) Fidelidad PC-2 | Fiel en estados, acciones y comprobaciones de A/B/C contra `:1117-1288`. Confirmado: B no aserta `rc` ni `stderr`; A no despacha ni recibe; el docstring de `complete_active_packet` documenta el `rc=2`. |
| (b) Contribución diferencial | Mantener no es inercia: M2 discrimina a A. Solape en F2. |
| (c) Foco y validate | 3 passed; histórico 013-002: 2 passed; `cdad-suite.py validate` rc=0 en `027064fb`. |
| (d) Mapa PC-6 | Delta vacío correcto: dos registros `VERIFY`, `target_nodeid` como cadena y sin cambios. La incertidumbre INV-3/PD-4 de B está declarada en §5 y §9, y el docstring de B confirma la diferencia con la entrada PD-6. |
| (e) Afirmaciones | No se afirman ahorro, acreditación global ni mutación realizada. |
| (f) Mutación | "No realizado" y "no exigible" son honestos. "Viable caja negra" no lo es: ver F1. |
| (g) Procedimiento | Aplicable, con fricciones listadas abajo. |

**Mutantes en copia temporal** (repo sin tocar; copia eliminada):

| Mutante | A | B | C |
|---|---|---|---|
| M1: guard retirado | falla | falla | pasa |
| M2: diagnóstico sin nombre del paquete | falla | pasa | pasa |
| M3: `if True` (no discrimina: rompe el primer `prepare`) | falla | falla | falla |

Un cuarto intento sobre `semantic_status` no aplicó ningún cambio (0 ocurrencias), así que su verde no vale como evidencia.

**Hallazgos de uso para 013-004:**
- `suite-maintenance.md` describe solo el flujo de sustitución. El delta vacío y Mantener proceden de la spec, no del procedimiento.
- El test-writer no ejecutó `validate` y el documento lo asigna a la entrada de Review. Conviene nombrar quién registra esa evidencia.

## Comandos
```sh
python3 scripts/cdad_packet.py render --project-root . --execution-context $E --request $P/REQUEST.json   # cmp con PACKET.md: rc=0
python3 -m pytest -q -p no:cacheprovider <los 3 nodeids A/B/C>   # 3 passed in 2.80s
python3 -m pytest -q -p no:cacheprovider <los 2 nodeids 013-002> # 2 passed in 0.06s
python3 scripts/cdad-suite.py validate                           # rc=0
```

Mutantes con `sed` o Python sobre `git archive HEAD` en `/tmp`, misma selección focal. Línea base de la copia: 3 passed.

## Abstentions
- **Exclusividad de `receive` en B:** sin mutante válido; se apoya en la lectura del código del test.
- **Exclusividad de C:** M3 no discrimina y el defecto "bloquear solo `--out-dir` custom" no se ejecutó.
- **Relevancia contractual del estado sin despacho:** no evaluada.
- **PC-3 sobre `06fe83ce` y `validate` previo a mi corrida:** no reproduje esa revisión, aunque los tests no cambian desde entonces.
- **PC-8 / `closure.md`:** todavía no existe.
- **Suite completa no realizada.**

## Evidencia del rol
- **Archivos modificados en el repo:** ninguno.
- **Commit:** ninguno.
- **Tabla de decisiones vigentes frente a `docs/adr/`:** no contrastada en su totalidad; solo se usó ADR-041 a través de la spec.

## Priorización y cierre de F1 (delegado del dueño, 2026-11-02)

F1 BLOQUEANTE: corregido por el orquestador mediante la nota de corrección en `test-audit.md` (ver allí). F2 y F3 se recogen en el cierre. **No hubo segunda revisión independiente** de la corrección (es documental y sus criterios de cierre están escritos en F1).

