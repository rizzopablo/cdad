# review-T2-003 — Revisión focal de T2

**Revisión examinada:** `89dabcc3e1e009fee28fb6638778b2d9d56ca444`  
**Dictamen: T2 no pasa todavía el gate.** La familia portable ya fue ejercitada y la evidencia cierra la ausencia señalada en `review-T2-002`. Sin embargo, el registro calibrado conserva una afirmación falsa sobre el contenido de la copia C-P y la regla de decisión describe incorrectamente el alcance de C-U3.

## Hallazgo 1 — El registro atribuye `.cdad` a una copia que no lo contiene

**Severidad:** Required  
**Verdict:** BLOCKING · **Bucket:** m

**Evidencia.** `performance/operation-scope.json:554-559` declara la calibración de volumen de `C-P-cold` como `one-including-.cdad-copy`. Sin embargo, `performance/calibration.md:75,102` y el verificador de C-P declaran que la fuente descartable excluye `.cdad`.

Además, `calibration.md:102` indica usar C-U1/U3/U4 «sobre el árbol completo» para dimensionar `product_root`, mientras que el propio registro establece que C-U3 excluye `.cdad` (`operation-scope.json:414,558`).

**Consecuencia.** El consumidor de T3/T4 recibe un registro marcado `calibrated=true` que describe incorrectamente qué copia incluye el volumen que interesa analizar. La advertencia de que las duraciones C-P no son comparables es útil, pero no corrige esa atribución ni convierte la medición de U3 en una copia del árbol completo. Una decisión sobre el costo de `.cdad` podría apoyarse en un alcance equivocado.

**Cierre verificable.** Corregir el registro para que C-P-cold refleje la fuente *slim* realmente utilizada y precisar la regla de decisión por selección: distinguir las copias que incluyen `.cdad` de C-U3, que la excluye. Mantener explícito que el tiempo específico de `.cdad` sigue siendo desconocido. Si alguna decisión requiere ese tiempo aislado, aplicar la regla de medición adicional ya declarada; no inferirlo del volumen.

## Contrastes efectuados

- **C-P:** revisé los `profile.json` crudos conservados bajo `~/clawd/tmp/017-001-calibration/`. C-P-cold contiene seis intervalos: `product.lookup[cold]`, sus hijos `product.copy` y `product.generate`, `product.lookup[cached]` y dos intervalos de aislamiento. C-P-present contiene cuatro: `checkout-manifest`, `cached` y dos de aislamiento, sin copy ni generate. Ambos perfiles figuran `complete` y sin errores de operación.
- **Sumideros:** P7 protege la coexistencia de `observed()` con otro sumidero; el helper agrega por identidad y distribuye los eventos a los sumideros conectados. La focal independiente pasó.
- **Selecciones anteriores:** los seis perfiles restantes —C-R, C-E, C-U1, C-U3, C-U4 y C-D— contienen respectivamente 5, 8, 7, 9, 10 y 15 operaciones, con los conteos registrados. C-W está expresamente declarada no requerida para esta calibración y sus esperas permanecen desconocidas.
- **Conservación:** contrasté el diff de los tests instrumentados frente a `05b58cc413cfd0669ddf9b5c6fd7e558502be672`. Los cambios examinados preservan las aserciones y llamadas visibles mediante envoltorios de marcas, además del cambio declarado de `_temp_root`. Esta revisión no acredita cada línea de todos los diffs.
- **Alcance real:** se examinaron **ocho selecciones en total**, incluidas las dos C-P; no hay ocho selecciones adicionales.

## Verificación independiente

| Comando | Resultado |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py tests/test_017_001_suite_profile.py tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py` | `28 passed in 32.62s` |
| `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` | `status: ok`, 2022 nodeids; rc 0 |

No ejecuté la suite completa. No modifiqué archivos ni generé commits; `docs/.cdad-state.json` ya figuraba modificado al comenzar la revisión.

## Abstentions

- No contrasté manifiestos de volumen de origen y destino ni acredito la cifra de archivos o bytes de `.cdad`.
- No verifiqué exhaustivamente todas las rutas excepcionales del observador ni cada línea de los diffs instrumentados.
- No completé la conciliación de la tabla de decisiones vigentes con todos los ADR.
