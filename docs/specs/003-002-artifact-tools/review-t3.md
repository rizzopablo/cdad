# Review — T3 (003-002): evidencia de runner (P5, §8)

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-44>`.
> Paquete: `003-002-artifact-tools-reviewer-review-005`. Objeto: `ed71c50..27c2a39`.
> **Dictamen: 3 BLOCKING (R1–R3) + O1–O3 opcionales. Lo verificado positivo se conserva.**

**Contrato:** `sha256sum …/spec.md` → `ba73e645…f37` = el del paquete ✓.

## Verificación empírica

| # | Comando | Resultado |
|---|---|---|
| V1 | `unittest tests.test_003_002_t3_run_evidence -v` | **13/13 OK** |
| V2 | clon read-only @ `ed71c50` + el test corregido | **13/13 FAILED por `AssertionError`**, 0 `ImportError`/`AttributeError`/`TypeError` ✓ (coincide con lo que afirma `27c2a39`) |
| V3 | `unittest discover -p "test_003_002_t[12]*.py"` | **37/37 OK** — sin regresión |
| V4–V7 | 4 experimentos adversariales en `/tmp` (repo intacto) | ver R1/R2 |

## Bloqueantes

### R1 — La degradación por selección incompleta/no relevante no está implementada · BLOCKING · bucket h

§8: "Las selecciones son roots/paths explícitos; **si no puede demostrarse que cubren lo relevante, la equivalencia es `unknown`**"; "selección incompleta… produce `stale`/`unknown`"; Limitaciones: "una selección incompleta o desconocida **degrada a `stale`/`unknown`, no a verde**".
`_validate_run_selection` (`:911`), `_load_run_request` (`:926`) y `validate_run_evidence` (`:1120`) usan **exclusivamente** las selecciones que declara el caller; **nada las liga a lo que argv ejecuta**.
**Exp-A:** RUN.json con `argv = discover -s tests` pero `source_selection=["docs"]`, `test_selection=["docs"]` → corrida verde + `validate-run-evidence` → **`valid-current` (rc=0)**. **Exp-C:** mutación de un archivo fuera de las selecciones declaradas → **`valid-current`**.
El pool RED de 13 solo cubre "campo ausente" y "path inexistente"; la forma **activa** de la regla no está probada ni implementada. Es el único vector vivo del gaming que §8 declara clausurar (los digests del caller sí están cerrados).
**Remedio:** acoplar mecánicamente selecciones y argv (`discover -s X` ⇒ `X ∈ test_selection`; `source_selection` ∩ árbol ejecutado ≠ ∅); si no, `unknown`. Y comparar las selecciones de `evidence` contra RUN.json.

### R2 — `validate-run-evidence` no re-deriva lo capturado · BLOCKING · bucket m

`validate_run_evidence` (`:1120-1178`) solo comprueba esquema, argv/execution/packet/contract vs RUN.json, y digests; **nunca re-parsea `evidence["log"]`** (capturado en `:1092` y jamás releído), compara conteos como enteros sueltos, y no compara selections/cwd grabados. `RUN_EVIDENCE_KEYS` (`:99`) está **declarado y sin usar** → evidence con claves extra pasa.
**Exp-B:** `tests_run: 1 → 7` y `log` reemplazado por `"LOG TAMPERED - no unittest output at all"` → **`valid-current`**. **Exp-D:** `source_selection=["/ABSOLUTELY/BOGUS"]`, `test_selection=[]` en evidence → **`valid-current`**.
**Remedio:** re-parsear el log con `_parse_unittest_counts` y exigir consistencia exit/`Ran N`/`skipped=`/`failures=`; comparar selections/cwd grabados vs RUN.json; imponer el conjunto cerrado de claves.

### R3 — Descubrimiento de snapshots por aproximación de `.gitignore` · BLOCKING · bucket m

`_ignore_patterns` (`:979`) y `_is_ignored` (`:995`): (a) los patrones se aplican **también a archivos tracked** (git no ignora tracked → mutación invisible → `valid-current` falso); (b) las líneas `!` se descartan; (c) `.gitignore` anidados y `.git/info/exclude` no se consultan; (d) `fnmatch` deja que `*` cruce `/`.
§8: "descubre **archivos tracked y untracked no ignorados**" — la aproximación no puede clasificar tracked (no consulta git).
**Remedio:** descubrir con git cuando el proyecto es un repo git (`git ls-files --cached --others --exclude-standard`); si no lo es, declarar la aproximación como limitación aceptada (decisión del dueño).

## Opcionales
- **O1 (m):** la clasificación de estado depende de substrings del texto de los `reasons` (`"stale" in reason`); un mensaje reescrito voltea `stale↔invalid`.
- **O2 (l):** raza de snapshooting (archivo que desaparece entre `is_file()` y `read_bytes` aborta la corrida; `iterdir` con `OSError` se traga).
- **O3 (l):** re-hashea el árbol completo por validate (coherente con "no existe cache genérica"; FYI).

## Verificado positivo (conservado)
Prefijo argv exacto con 7 subTests; digests del caller rechazados por conjunto cerrado; tamper de digests detectado por recomputación; conjunción valid-current completa; trampas unittest (0 tests / todo skipped) capturadas por parseo del log; contract drift vía `_load_run_binding`.

## Abstenciones
1. No evaluó `_parse_unittest_counts` contra todas las variantes de formato de unittest (buffering, `-q` extremo, tests que imprimen `failures=` propios); R2 introduce la re-derivación y ese riesgo debe re-validarse junto.
2. No reprodujo R3 con un fixture git (los fixtures son tempdirs sin `.git`); base = lectura de código.
3. No corrió la suite completa (el primer intento excedió 10 min); cobertura limitada a T1/T2 (37) + T3 (13).
4. No verificó la persistencia durable del evidence (alcance T4).

## Dictamen
**3 Requeridos.** R1 es el más fuerte (el runner fija su propio alcance de verificación, exactamente el hueco que §8 manda degradar). R1–R3 → review-fix; O1–O3 a deuda.
