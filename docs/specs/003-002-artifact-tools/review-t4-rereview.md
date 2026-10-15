# Re-review focal T4 — 003-002-artifact-tools (cierre de T4)

> Materializado por el orquestador **a través del flujo de 003-002** (receive →
> materialize) desde el TEXTO FINAL del reviewer: este archivo es el original
> persistido por `receive` y copiado por `materialize` (bytes idénticos).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-60>`.
> Paquete: `003-002-artifact-tools-reviewer-review-010`.
> Contrato verificado: `spec.md` sha256 `ba73e645…01f37` = el del paquete ✓.
> **Dictamen: F1 (F1.1 y F1.2) CIERRA; F2 cerrada 3/3; sin regresiones; sin
> hallazgos nuevos. T4 CIERRA.**

**HEAD:** `a18375a`. **Modo:** read-only; ningún archivo modificado, ningún commit.
**Calibración:** enmienda vigente aplicada (regla 4: se verifica F1 contra su condición
y las regresiones; no se abre nueva caza).

## 1. F1.1 (BLOCKING, `re-entry.md`) — CIERRA ✓

**Condición:** «el paso RECEIVE de `re-entry.md` contiene una cláusula que define el
staging como paso previo del orquestador (bytes del TEXTO FINAL bajo `.cdad/inbox` +
`RESULT.json` con descriptor válido, cf. spec §3/§4) antes de invocar `receive`».

**Evidencia:** `re-entry.md:25-45` (commit `aabb614`). La cláusula existe y cumple la
condición verbatim:
- staging definido como «a prior mechanical step, before invoking `receive`» (`:29`);
- «write the **exact bytes** … under `.cdad/inbox` … without retyping, summarizing or
  regenerating» (`:30-31`);
- «write the `RESULT.json` descriptor» con `source.kind`,
  `parts[].name`/`artifact_kind`/`staged_path` bajo el inbox y `observed_changes` con su
  baseline manifest (`:32-34`);
- «only then invoke `receive` with that descriptor» (`:37`).

**Corrección respecto de lo que `receive` exige** (contraste independiente con la spec y
el código, no con la afirmación del autor):
- `source.kind` obligatorio `staged-file` — declarado en la cláusula (`:27`) y coincidente
  con `spec.md:147`/`:172` y con la exigencia del código (`cdad_result.py:232-234`).
- parts como archivos regulares bajo el inbox fijo — `:27-28` coincide con
  `spec.md:172-174`.
- campos del descriptor — coinciden con el ejemplo §3 (`spec.md:141-168`) y el manifiesto
  de §4 (`spec.md:209-228`).
- **No duplica la interfaz:** la cláusula declara «The owner of those fields is the feature
  spec (§3/§4) and the CLI — consult them; do not duplicate the interface here»
  (`:34-36`), coherente con el principio preexistente (`:21-23`). «Staging is transport,
  not authority» (`:39-41`) es consistente con §9 (el inbox es aditivo dentro de `.cdad/`;
  el manifiesto lo prepara la orquestación, `spec.md:228`).

**Verdict:** PASS — condición de cierre satisfecha, cláusula correcta y sin duplicación.

## 2. F1.2 (README, opción (ii)) — CIERRA ✓

**Condición:** (ii) «el dueño registra la decisión de retirar README del alcance de T4».

**Evidencia:** `plan.md:232-245`, «Desviaciones registradas de T4 (2026-10-05)». La
decisión está registrada y la razón es fundada, verificada independientemente:

```
grep README docs/cdad-policy.json → sin coincidencias (rc=1)
entries de path_policy: agents, build, docs, install.sh, scripts, skills, sources,
tests, tests/.sensitive-patterns.local
→ README.md NO está clasificado
```

Ningún rol puede escribir `README.md` bajo la política vigente (no cae en
`documentation_roots` ni es `implementation_file`); revisar la política está fuera de
alcance de 003-002 y cambiarla a mitad de ciclo invalidaría `policy_sha256` (firma del
paquete). La desviación deja de ser silenciosa y registra la brecha de política
(clasificar `README.md`) como decisión del dueño. `git diff d7ffbcc..HEAD` no toca
`README.md` — coherente con la disposición.

**Verdict:** PASS — opción (ii) cumplida con razón fundada.

## 3. F2 (familia `handoff-prompts`) — CIERRA ✓ (3/3)

```
grep "materializ|Orchestrator materialization protocol" handoff-prompts.md (case-insensitive)
→ 3 coincidencias: :123, :209, :511 — las tres llevan
  'the canonical mechanism is the "Orchestrator materialization protocol" in references/re-entry.md'
```

`:123` y `:511` en `aabb614`; `:209` (tercera instancia, spec draft del architect) en
`b0f9ade`. No queda ninguna instancia sin referencia al protocolo canónico.

**Verdict:** PASS.

## 4. Regresiones — NO HAY ✓

| Corrida | Comando | Resultado | Esperado |
|---|---|---|---|
| Guards focales T4 | `cd tests && python3 -m unittest test_003_002_t4_integration -v` | **Ran 6 tests — OK** (32.4 s) | 6/6 ✓ |
| `test_packet_prepare` | `python3 -m unittest tests.test_packet_prepare -v` (desde la raíz) | **Ran 19 tests — OK** (12.2 s) | 19/19 ✓ |
| `validate-consistency` | `bash tests/validate-consistency.sh` | **PASS 141 / FAIL 2** (`F011` ×2) | preexistentes ✓ |

Los 2 FAIL son el set preexistente declarado y son ajenos: (a) `grep handoff-prompts|re-entry`
en esos validadores → sin coincidencias (rc=1); (b) `git diff d7ffbcc..HEAD --stat` no toca
ningún script objetivo. `tests/` intacto.

**Observación de reproducibilidad (FYI, no reabre):** `test_packet_prepare` importado desde
`tests/` falla con `ModuleNotFoundError: No module named 'tests'` y exige invocarse desde la
raíz — propiedad preexistente (`tests/` sin cambio desde `d7ffbcc`). OPTIONAL · Bucket l.

## 5. Nuevas variantes

Ninguna con evidencia nueva de incumplimiento material o riesgo relevante.

## Abstenciones

1. **No corrió la suite completa** (mandato del encargo: la corre el orquestador en el
   cierre sobre el commit final). Se abstiene de afirmar el conteo completo.
2. **No corrió internamente los dos validadores que fallan** para establecer su causa raíz:
   fuera del mandato; se confirmó que son ajenos por grep + `diff --stat`.
3. **No re-auditó T1–T3** (ya revisadas en `review-t1/t2/t3` y sus re-reviews).

## Evidencia

```
sha256sum docs/specs/003-002-artifact-tools/spec.md
→ ba73e645560d03c090e2a8525a63d79e12168d38a1da6a9d091fd27cf0201f37 (= contrato)

git log --oneline -8 → HEAD = a18375a (registro del review-fix)
git show aabb614 → re-entry.md +19/−4, handoff-prompts.md +2/−2 (F1.1 + F2 :123/:511)
git show b0f9ade → handoff-prompts.md +1/−1 (:209)
git diff d7ffbcc..HEAD --stat → sólo docs/* y los 2 archivos de referencia; tests/ intacto
grep README docs/cdad-policy.json → rc=1 (no clasificado)
```

**Archivos modificados por esta revisión: ninguno. Commits: ninguno** (`write_scope` vacío).

## Dictamen

Las condiciones de cierre de la familia **F1** están cumplidas: F1.1 con cláusula de staging
correcta, verificada contra spec §3/§4 y sin duplicación de interfaz; F1.2 con la desviación
efectivamente registrada y razón fundada (política sin clasificar `README.md`, verificada
empíricamente). **F2 cerrada 3/3.** Sin regresiones (6/6, 19/19, 141/2 con FAILs
preexistentes y ajenos). No se abren hallazgos nuevos. **T4 CIERRA.**
