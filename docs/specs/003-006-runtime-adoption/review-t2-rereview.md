# Review T2 review-fix (re-review FOCAL) — cierre de B-1 y O-4

**Packet:** `003-006-runtime-adoption-reviewer-review-003` · Contrato `docs/specs/003-006-runtime-adoption/spec.md` sha256 `dc485e80aa86b545c75c86f71a3fa590321c1ca6a66221e1115c69b75a7d7cb7` **= hash del packet ✓** · Diff `f1f3c0d..7ccea01` · Read-only (write_scope `[]`).

---

## Evidencia de verificación (comandos y salida)

| Comando | Resultado |
|---|---|
| `sha256sum docs/specs/003-006-runtime-adoption/spec.md` | `dc485e80…d7cb7` = contrato ✓ |
| `git diff --stat f1f3c0d..7ccea01` | 4 archivos: `docs/.cdad-state.json` (solo `active_packet`), `dispatch-ledger.md` (+1 fila 12), `scripts/cdad-activate.py` (+60/-3), `runtime-adoption.md` (+4 doc) |
| `git diff 7ccea01 -- scripts/cdad-activate.py tests/…` | **vacío** ⇒ HEAD (`380d849`) solo añade ledger; el código probado es el del diff ✓ |
| `python3 -m pytest tests/test_003_006_t2_activation.py -q` | **16 passed in 6.24s** (11 previos + 5 del review-fix: 3×B-1 parametrizado, poda B-1, O-4) |
| `python3 /tmp/opencode/cdad-rev-t2rf/verify_b1_t2rf.py` (escenario medido, tmpdir propio) | **11/11 PASS** — detalle abajo |
| `python3 /tmp/opencode/cdad-rev-t2rf/probe_leaf.py` (sonda adversarial hoja-symlink) | hoja ajena→externo: rc=1, dir externo intacto ✓ |
| `git status --short` | solo ` M docs/.cdad-state.json` (pre-existing del orquestador); **nada modificado por mí** |

Traces míos: solo `/tmp/opencode/cdad-rev-t2rf-*` (autolimpiados con `rm -rf` al final). Nunca este repo, nunca `$HOME` real (HOME siempre apuntado a tmpdir en cada CLI).

### Escenario medido (raíces todas bajo `/tmp/opencode/cdad-rev-t2rf-eavbj9sg`)

| # | Escenario | Resultado |
|---|---|---|
| s1 | `R/.claude → <ext>` (caso B-1 original): rc≠0 ✓; mensaje nombra rutas (`.claude/agents/cdad-architect.md`, `.claude/skills/cdad-cycle` …, cada uno con el resolved `/<ext>/…`); **cero cambios dentro de R**, **cero en `ext`**, **cero bajo HOME** | cerrado |
| s2 | Poda vía symlink externo (`R/.claude/skills → ext` con enlaces homónimos propios, repoint A1→A2 con subconjunto): `ext` **byte a byte intacto**, rc=1 sin escrituras — la poda ya no atraviesa el enlace | cerrado |
| s3 | Variante pedida — componente profundo `R/.claude/agents → <ext2>`: rc≠0, `ext2` intacto (con `ext2` vacío ⇒ hojas inexistentes: exactamente el estado que antes disparaba la escritura a través del enlace) | cerrado |
| s4 | O-4: ortografías **relativa** y **vía-symlink** de ambas raíces producen árbol **byte-idéntico** a la ortografía absoluta (incl. `.cdad/activation.json`) | cerrado |
| probe | hoja ajena dentro de contenedor contenido (`R/.agents/skills/cdad-cycle → ext`) tras activación: rc=1, `ext` intacto (la comparación de hoja de `detect_conflict` retiene el caso que no llega por `dirname`) | cerrado |

## Veredicto por hallazgo

- **B-1 — CERRADO.** Contención previa a toda escritura/poda (`path_escape_conflict` sobre `dirname` con `realpath`, aplicado a emisiones `:370-378`, podas `:381-384` y registro `:386-390`), todo-o-nada antes de la escritura (`:401-405`), documentado en el contrato de runtime (`runtime-adoption.md:60-63`). Reproduje el escenario exacto del review anterior: el defecto medido (rc=0 + escritura/poda fuera de R) ya no ocurre; rc≠0 nombrado y cero efectos fuera de R, incluida la variante de componente profundo. La decisión dictaba realpath *estrictamente* bajo R para destinos **y componentes intermedios** — la implementación comprueba el contenedor resuelto de cada destino, que cubre ambos (los enlaces-hoja propios → A quedan permitidos por diseño: el check es sobre el contenedor, no sobre el target del symlink, como exige la emisión legítima de enlaces a A).
- **O-4 — CERRADO.** `realpath` de ambas raíces en la validación de args (`:334-335`), verificado por suite (`test_o4_…`) y mi reproducción s4: bytes idénticos entre ortografías relativa/vía-symlink/absoluta. Residual formal: la equivalencia se cumple cuando la sintaxis **resuelve al mismo destino**; dos dir-names distintos que contienen el mismo contenido siguen produciendo árboles distintos correctamente (el registro es por proy, no por contenido — comportamiento correcto, no defecto).

**Sin bloqueantes. Sin residuos de B-1/O-4 detectados.**

## Opcionales (deuda, invariada respecto a review-t2)

- O-1 (escrituras no atómicas en el bucle de emisión, `:407-411`), O-2 (registro corrupto descartado en silencio, `:200-211`), O-3 (componentes de ruta de llaves de manifest sin sanitizar — nota: la contención B-1 bloquea hoy los que escaparían de R; el sub-caso interno es el residuo declarado), O-5 (sin test adicional sobre ellas). **Deuda declarada en `review-t2-decision.md`; fuera del alcance de esta re-review FOCAL — no re-evaluadas.**

## Cumplimiento del paquete y del proceso (sin hallazgo)

- Diff de código = `cdad-activate.py` + doc del contrato de runtime: ambos dentro de los archivos que la decisión T2 alcanzó; tests nuevos cubren los postconditions con asserts observables (rc, bytes, enlaces, ausencia), sin mocks. Doc `runtime-adoption.md` amplía §contención literal según la decisión ✓.
- RED previo documentado en ledger fila 12 (5 failed + 11 passed en `f1f3c0d`) y GREEN aquí (16/16 en `7ccea01`) — cadena RED→GREEN verificable ✓.

## Abstenciones

- **Comportamiento en runtime real (P4/P6/P11/P12, mitad runtime de P5):** fuera de alcance por contrato/spec (reservados a rehearsal T4); no re-evaluado.
- **`install.sh` y T1:** no modificados; evaluations previas aplican sin re-review (limitación igual que review-t2: no lo re-revisiono aquí).
- **TOCTOU de symlinks en carrera concurrente:** el check de contención no es racel-free si un componente cambia entre el check y la escritura; sin evidencia de amenaza concurrente declarada en el contrato, no la juzgo — queda como límite conceptual no siervo (observación FYI, sin precio).

## Dictamen

**Re-review FOCAL aprobado: B-1 y O-4 quedan CERRADOS con evidencia medida** (11/11 escenarios propios + 16/16 suite + sonda adversarial de hoja), sin residuos detectados, dentro solo de raíces temporales propias. Banknote adicional: la contención también retiene la variante de hoja dentro de contenedor contenido (probe), y el segundo `git status` nunca mostró modificación del repo desde mi parte. El camino a cierre de T2 queda conforme a la decisión del orquestador (con la deuda O-1..O-3/O-5 ya registrada; decisión de cierre es del dueño).
