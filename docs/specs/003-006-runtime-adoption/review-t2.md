# Review T2 — `003-006-runtime-adoption` (diff `673e3e7..04ba3d8`)

**Packet:** `003-006-runtime-adoption-reviewer-review-002` (reviewer/review, read-only) · **Contrato:** spec `dc485e80…d7cb7` (hash verificado ✓) · **Nota de contrato:** `t2-contract-note.md` · **Test:** `tests/test_003_006_t2_activation.py`

---

## Evidencia de verificación (comandos y salida)

| Comando | Resultado |
|---|---|
| `git log --oneline 673e3e7..04ba3d8` | 2 commits: `ed816ce` (fixture A2) → `04ba3d8` (generador) |
| `git diff --stat 673e3e7..04ba3d8` | 4 archivos: `.gitignore` (+2), `scripts/cdad-activate.py` (nuevo, 377), `skills/cdad-cycle/references/runtime-adoption.md` (nuevo, 60), `tests/test_003_006_t2_activation.py` (1 línea) |
| `sha256sum docs/specs/003-006-runtime-adoption/spec.md` | `dc485e80aa86b545c75c86f71a3fa590321c1ca6a66221e1115c69b75a7d7cb7` = contract ✓ |
| `python3 -m pytest tests/test_003_006_t2_activation.py -q` | **11 passed in 2.35s** — la afirmación "Focal T2: 11/11" del autor es verificable ✓ |
| `/tmp/opencode/cdad-rev-t2/verify_escape.py` (CLI contra raíces tmpdir propias) | **rc=0 y escrituras FUERA de `--project-root`** — ver hallazgo B-1 |

No modifiqué nada (write_scope `[]`); los únicos rastros son en `/tmp/opencode/`, que el orquestador autorizó y se autolimpian.

---

## Verificación de los 5 puntos del orquestador

1. **Escritura fuera de `--project-root` / enlaces que salen de él — FALLA.** Hallazgo B-1 (bloqueante, evidencia medida).
2. **Todo-o-nada ante conflicto — OK** (detección previa a toda escritura, `cdad-activate.py:346-366`; test `test_r5_no_clobber_conflict` mata el snapshot). **Ante error a mitad de escritura — defecto menor**: escrituras parciales sin rollback → O-1 (opcional, se autorecupera).
3. **Poda solo de rutas propias — OK en diseño** (registro previo + verificación de sha/readlink, `cdad-activate.py:230-253`), pero **hereda el escape de B-1**: arranca enlaces fuera de R por el mismo defecto (demostrado). No borra contenido de A en el camino feliz ✓.
4. **Variantes de `command:` del generador — OK**: el único punto de emisión real es `scripts/cdad-generate.py:501` (`command: ~/.claude/cdad-scripts/path-guard.sh <rol>`, tilde sin comillas); `rg "command:" scripts/cdad-generate.py sources/agents/` no encuentra otra variante. `text.replace(HOOK_TILDE, …)` en `cdad-activate.py:116-118` cubre esa forma y cualquier sufijo de rol. Ningún `command:` emitido contiene `~/.claude` (afirmado por test P5, verificado).
5. **`runtime-adoperation.md` — OK contra ambos criterios**: solo marcadores `<project-root>`/`<adopted-root>` (líneas 12-15, 23-33), cero rutas absolutas locales; solo los flags del contrato (`--project-root`, `--adopted-root`, `--runtime`, `--dry-run`, líneas 11-16), ningún flag extra copiado.

---

## Bloqueantes

### B-1 · La activación escribe y poda fuera de `--project-root` cuando un componente de la ruta destino es un symlink que sale de la raíz
`Verdict: BLOCKING` · `Bucket: h`

- **Ubicación:** `scripts/cdad-activate.py:196-227` (`detect_conflict` solo inspecciona la hoja), `:256-267` (`write_emission` opera a través de componentes symlink vía `os.makedirs(exist_ok=True)`), `:368-371` (bucle de escritura/`os.unlink` de poda sin contención).
- **Evidencia medida** (CLI ejecutado en tmpdir, escena exacta que el orquestador pidió — dotfiles que enlazan `.claude` a `$HOME`): con `R/.claude → <dir externo>/.claude`, primera corrida `rc=0` y se crean `<dir externo>/.claude/agents/cdad-architect.md` y `<dir externo>/.claude/skills/cdad-cycle` **fuera de R**; el repoint a A2 poda un symlink en el directorio externo (`run2: SYMLINK PODADO FUERA de R: True`). Con `R/.claude → ~/.claude` real, esa escritura aterriza en la configuración del HOME real.
- **Consecuencia contractual:** viola I1 y §2.2 («cero escrituras en las configuraciones del HOME real», «nunca escribe fuera de R»), y el punto (3) del orquestador («la poda nunca debe borrar contenido fuera/dentro de la raíz adoptada»). R-5 falla safe en el caso *frecuente* (contenido divergente → conflicto), por eso los 11 tests pasan: el caso därmino requiere hoja idéntica o destino inexistente — exactamente el estado de un `.claude` externo vacío o compartido.
- **Cierre verificable:** comprobación de contención antes de escribir/podar — resolver cada destino hoja (`os.path.realpath`) y exigir que quede estrictamente bajo `realpath(project_root)`, rechazando como conflicto (o error nombrado) cualquier componente symlink que escape R; más un test de unidad que haga `R/.claude` symlink externo y afirme rc≠0/ningún archivo fuera de R (y la poda equivalente).

---

## Opcionales (deuda, no bloquean el camino feliz)

- **O-1** (m) — `cdad-activate.py:368-371`: el bucle de escritura no está en try y emite archivos sin tmp+`os.replace` (a diferencia del registro, `:291-297`). Un fallo a mitad (disco lleno, `makedirs` contra archivo existente) deja escrituras parciales sin registro; la re-corrida converge (idempotente) pero deja al árbol en estado mezclado y a la hoja parcial en conflicto hasta intervención. Remedio: escritura atómica por archivo + informe de rollback/unwind en el path de error.
- **O-2** (l) — `cdad-activate.py:182-193`: un registro previo corrupto se descarta en silencio (`return {}`), perdiendo propiedad; los destinos propios vuelven a evaluarse como ajenos (falla safe con la ruta nombrada, pero el usuario queda atascado sin guía). Remedio: error explícito nombrando que el registro propio está corrupto y cómo recuperarlo.
- **O-3** (l) — `cdad-activate.py:61-70,131-141,146-156`: las llaves del manifest se usan como componentes de ruta sin sanitizar; una llave bajo prefijo skills con `..` produciría un symlink que apunta fuera de A. Supuesto de confianza de entrada (A la produce `install.sh`) — deunda declarable, hoy no explotable en el camino feliz.
- **O-4** (l) — `cdad-activate.py:313-314`: la determinismo P2 es respecto a la *ortografía* de `--adopted-root` dada en CLI (relativa ≠ absoluta ≠ destino con symlink ⇒ bytes distintos). Remedio: resolver `realpath` de ambas raíces en la validación de args (complementa el cierre de B-1).
- **O-5** (l) — fixture de test健 usa `make_adopted_root` con `a = base/"A"` codificado (`test_003_006_t2_activation.py:69`), por lo que dos bases distintas son obligatorias (correcto desde `ed816ce`); no hay test del escenario de B-1 — parte del cierre de B-1.

---

## Cumplimiento verificado (sin hallazgo)

- **P2** determinProductName ✓ (test`test_p2_deterministic_two_runs_identical`: snapshot r==r2, incl. `.cdad/activation.json`).
- **P3** ✓: todas las emisiones caen en `.opencode/`, `.claude/`, `.agents/`, `.cdad/` git-ignoradas; `test_p3_gitignore_covers_runtime_dirs` usa `git check-ignore -q` real sobre el repo (`; `cdad-activate.py` no escribe bajo HOME — test con HOME aislado).
- **P5 mitad unidad** ✓: hook reescrito a `<A>/.claude/cdad-scripts/path-guard.sh <rol>`, cero `~/.claude` en `command:` emitido, sin `.claude/settings.json` (:`test_p5_hook_rewrite_no_tilde_no_settings`); la mitad runtime queda declarada en la spec como rehearsal T4 ✓ (spec §2.2/P5).
- **R-4** ✓ (`test_r4_identity_manifest_sha`): sha divergente y entrada faltante → rc≠0 y nada escrito.
- **R-5** ✓: conflicto nombrado + todo-o-nada; repoint reemplaza lo propio y poda lo ya no emitido (fixture A2 arreglada en `ed816ce` — el cambio es correcto: antes A2 colisionaba con A1 en `base/"A"` haciendo el test vacuo; ahora raíces distintas y el test es real).
- **Nota de contrato ↔ spec**: el generador precisa §2.2 sin ampliarla (un archivo nuevo + un doc corto + 2 líneas de `.gitignore`); el manifiesto real de `install.sh` (`:47-52, :866-871, :916`) usa las llaves rel-prefijadas que `build_plan` consume ✓.
- **Docs sin rutas absolutas ni flags innecesarios** ✓ (punto 5).

---

## Abstenciones

- **Comportamiento en runtime real (P4/P6/P11/P12 y la mitad runtime de P5):** fuera de este review T2 por diseño (la spec los reserva a rehearsal T4/no implementados aún aquí); no abstinencia por insuficiencia de evidencia, sino fuera del alcance declarado del contrato T2.
- **`install.sh` y su evolución del manifiesto en repoint:** se verificaron solo las llaves/prefijos relevantes al consumo de `build_plan`; el mecanismo completo de `install.sh` (no modificado en este diff) se evaluó en T1 y no lo re-revisiones aquí.
- **Interacciones de OpenCode/Claude Code/Codex con `.jsonc`/symlinks de skills emitidos:** no verificable sin runtime; cobertura solo declarativa (unidades y P5-mitad-unidad).

---

**Ver dictamen final para el orquestador:** T2 es conforme al contrato aprobado **salvo un bloqueante** (B-1): el generador cumple P2/P3/P5-unidad y R-4/R-5 con tests observables reales y doc limpia, pero carece de contención de ruta frente a symlinks que salen de `--project-root` — defecto con evidencia medida que puede tocar las configuraciones del HOME real (la violación exacta que I1 y el punto (1)/(3) del orquestador prohíben). El cierre está localizado (contención realpath en `main`/`write_emission`/prune + dos tests) y es pequeño; con B-1 resuelto la tarea queda en condiciones de cerrar. Decisión de bloqueo→deuda es del dueño; yo la escalo dado que el orquestador pidió expresamente este escenario.
