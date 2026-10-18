El código y la estructura de la prueba se ven sólidos. Ahora, mi propia verificación: ejecutaré la suite focal en mi carril y comprobaré las dos superficies restantes (eliminación limpia en ejecución mediante el test de control; `--dry-run` sondeado directamente, ya que el propio GREEN lo declaró solo como lectura de código).
La prueba focal es reproducible en mi entorno (6/6). Ahora una prueba directa para `--dry-run` (la superficie que el propio GREEN solo declaró por lectura de código) con un registro degenerado, más un control de eliminación limpia, utilizando las mismas herramientas de prueba en un archivo de prueba temporal fuera del repositorio:
La sonda `--dry-run` es concluyente. Dos verificaciones finales: el `grep` residual `TSV-read` y el `u7 prune suite` (la ruta `modified/CONFLICT` comparte ahora la nueva rama `unverifiable`):
Los sitios de TSV restantes tienen el sha como último campo (inmunes al colapso, coincidiendo con la afirmación de GREEN). Ahora, el conjunto de regresión de prune:
# Informe de revisión — 006-003 (RE-REVIEW FOCAL 2, paquete `…-reviewer-review-003`)

**Cargo:** revisor · **Escrituras:** ninguna en el repositorio (write_scope vacío); la única sonda propia se escribió en `/tmp/opencode/probe_rf2_dryrun.py` (entorno temporal declarado, fuera del repo). `~/.config/cdad/*` y `tests/.sensitive-patterns.local` no leídos. · **Contrato:** `sha256(spec.md) = c25ebf0e…d890` ✓ verificado contra el paquete.

**Objeto juzgado:** diff `26667b5^..HEAD` — RED `26667b5` (`tests/test_006_003_rf2_review_fixes.py`, 566 líneas, test-only) + GREEN `738a380` (`install.sh` +142/−30, `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` +12/−6). Los commits intermedios (`b3bfdc3`…`83569e8`) son documentación de estado del orquestador, no producto. Insumos: `rereview.md` (B-1 con condición de cierre de 5 puntos, OPT-1, Disposición), `rf2-red.md`, `rf2-green.md`.

## Verificación previa

```
$ sha256sum docs/specs/006-003…/spec.md
c25ebf0e0c7867c03de072439128e7a77e4b2a7dcd7f52228535ea9785d18890  ✓

$ timeout 900 python3 -m pytest tests/test_006_003_rf2_review_fixes.py -q
......  [100%]   6 passed in 72.61s        ← reproducible en mi carril
```

## Blockings

Ninguno.

## Opcionales

**OPT-2 · Consideración opcional · Bucket: m · Verdict: OPTIONAL — el comentario de la nueva regla afirma para los symlinks un veredicto que el código ya no entrega cuando el digest está vacío.**

*Procedencia:* `install.sh:663-664` («A symlink is not the bytes we deployed …, so it keeps the historical removable verdict») y `rf2-green.md` §5 (misma afirmación declarada como intención) vs. el orden del código en `install.sh:654-656`:

```sh
if [ ! -L "$path" ] && [ ! -e "$path" ]; then printf 'absent'; return 0; fi
if [ -z "$recorded" ]; then printf 'unverifiable'; return 0; fi   # ← ANTES del check de symlink
if [ -L "$path" ]; then printf 'removable'; return 0; fi
```

Con digest vacío + symlink presente, el código devuelve `unverifiable` (preservado), no el `removable` que el comentario declara. No es el escape de B-1 (la dirección del error es conservadora: nunca borra, nunca pierde datos del usuario) y solo es alcanzable con manifiesto editado a mano (el instalador siempre registra un digest real, incluso para symlinks — `record_owned` calcula `sha256_of`); los oráculos rf2 ejercitan solo archivos regulares, y la preservation extra en `--uninstall` de un symlink sin digest es inofensiva. Es un defecto de documentación del método (la cláusula 3 pide el comentario «actualizado a la nueva regla» y este reclamo es falso), no de comportamiento dañino.

*Condición de cierre verificable:* reordenar (`[ -L ]` antes del check de digest) **o** corregir el comentario a «un symlink con digest verificable mantiene el veredicto `removable`; con digest ausente cae en `unverifiable` como todo registro sin digest», dejando comentario y código en la misma historia, con una línea de test o de declaración en el reporte que fije cuál de las dos es la regla del dueño.

*(Misclasificación descartada: no es blocking — sin pérdida de datos, sin escape de borrado, alcanzabilidad solo hand-edit.)*

Los demás ejes del diff — sin hallazgos: la mecánica NUL-framed es correcta (abajo, juicio 1/2), no queda ningún registro de manifiesto leído por `read` de bash en formato colapsable, el `*) die` nuevo sobre estados inesperados opera sobre un conjunto cerrado de 4 veredictos, y el adaptador no interpola ningún valor de credencial.

## Abstenciones

1. **Suite completa y `validate-consistency.sh`:** política del paquete — la corre quien cierra el task. No la re-corro; me abstengo de refrescar el F011 (drift de HOME real pre-existente, declarado por el GREEN, archivos que este paquete nunca tocó).
2. **Lotes de regresión amplios del GREEN (90/32/51/52 passed):** no los reproduzco todos; verifiqué la muestra de mayor riesgo para este cambio (`test_006_003_u7_prune_obsolete.py` + `test_install_ownership.py` → **17 passed in 252.55s**) y el focal completo (6/6). El resto queda como declaración del GREEN no contrastada.
3. **Pathologías de encuadre no sondeadas:** registro con NUL real (`\u0000` en JSON decodifica a byte NUL y rompería el framing — inexistente en manifest producidos por el instalador), symlinks con digest vacío en `--uninstall` real (cubierto por lectura de código, no sonda), y registros apuntando a directorios con digest vacío (caen en `unverifiable` en vez de `absent`, hand-edit only, misma clase conservadora que OPT-2).

## Resumen: 0 bloqueantes, 1 opcional, 3 abstenciones

## Juicios por punto pedido

1. **B-1 cumple cada punto de su condición de cierre, con remedio estructural: Sí (5/5).**
   - *Cláusula 1 (regla + remedio estructural):* `owned_removal_state` (`install.sh:652-666`) introduce el veredicto `unverifiable` — digest vacío o `null` **nunca** `removable` — y el mecanismo de colapso está eliminado, no parcheado: los 4 puntos de emisión/lectura (`prune_owned_obsolete` `:1245-1268`, `uninstall_by_manifest` `:1405-1437`, `load_previous_ownership` `:766-800`, `check_installed_staging` `:1736-1751`) viajan NUL-framed con `read -r -d ''`; los streams plan/keep que quedan en TSV los parsea **Python** `split("\t", 2)` (`:993`, `:1000`, `:1492`), que preserva campos vacíos; los `IFS=$'\t' read` residuales (`:939`, `:1761`, `:1899`) son todos `rel<TAB>sha` con sha al final — inmunes por construcción. Verificado por lectura + tests + sondas.
   - *Cláusula 2 (registro coherente):* el registro preservado se reconstruye desde los campos exactos → mi sonda publicó `{"sha256": "", "source": ""}`; el caso `source` presente está fijado por `test_b1_b` (source en su slot, nunca «registered <source>») y `null` por `test_b1_c` (slot del digest ≠ token `None`); el `field()` helper (`:1241-1246` y pares) publica `null` como `""`, nunca el repr `None`.
   - *Cláusula 3 (comentario):* actualizado (`:642-651`) a la nueva regla con la razón INV-2 — con la inexactitud de symlink reportada arriba (OPT-2).
   - *Cláusula 4 (aserciones para las representaciones retirantes y corruptas):* `test_b1_a` (sha `""`+source `""` y sha `""`+source ausente, con control in-run de hermano sano retirado), `test_b1_a2` (misma regla en `--uninstall`), `test_b1_b`, `test_b1_c` — todas RED confirmadas en `rf2-red.md` y GREEN en mi carril. Black-box fieles (producto en copia, `CDAD_INSTALL_ROOT`+HOME tempdir, hand-edit declarado y mínimo, sin mocks de plumbing).
   - *Cláusula 5 (corrección de `rf-red.md` §4):* hecha — la corrección del orquestador está en el archivo (`rf-red.md:68`, blockquote 2026-10-18 que refuta el «ya se cumple» citando el colapso TSV).
   - **No es un parche del caso probado:** la regla es una sola función compartida por ambas superficies, el framing es inmune a *cualquier* campo vacío (no solo al probado), y los tests cubren las 4 representaciones + control positivo en la misma corrida.
2. **¿El cambio alteró el retiro sano, el CONFLICT de lo modificado o el `--dry-run`? No en los tres.** (a) *Retiro sano:* el control in-run del focal pasa (hermano con digest correcto retirado y desregistrado); mi sonda lo reprodujo (`REMOVE (own obsolete…)`, `Obsolete prune: 2 retired, 1 preserved`). (b) *CONFLICT de lo modificado:* la rama `modified` comparte outcome con `unverifiable` pero su mensaje es idéntico al anterior («modified locally since the recorded install (registered $sha)») y el outcome (PRESERVED + registrado + disclosed) no cambió; `u7_prune_obsolete` + `install_ownership` = **17 passed**. (c) *`--dry-run`:* sondeado black-box (lo que el GREEN solo declaró por lectura de código) — con registro degenerado el dry-run **no borró nada** (ni el degenerado ni el sano), lo disclose como `DRY-RUN CONFLICT … preserved (… no recorded sha256 … explicit resolution needed)`, y la corrida real contrastante comporta exactamente lo esperado (degenerado preservado + registrado, sano retirado). Los `*) die` nuevos no pueden dispararse con los 4 veredictos que `owned_removal_state` emite.
3. **OPT-1 cerrado sin exponer el valor (INV-1): Sí.** `cdad_delegate_opencode.py:1095`: `path = credential["path"] or _credential_file_path()` — `_credential_file_path()` (`:969-980`) siempre devuelve una ruta **resuelta** (la `credential_env_file` configurada o el default `<config-dir>/cdad/opencode-server.env`; docstring: «Resolved even when no credential is found»), así que no hay camino a un `None` interpolado; la rama de entorno (`:1104-1111`) nombra la alternativa («the credential file <path> … with mode 0600 or 0400») con el motivo de migración. La aserción `assert_names_path` usa el default real del fixture y `INV-1` está fijada por dos oráculos (valor ausente del diagnosis **y** de stdout+stderr completos del proceso); leí `_unauthorized_diagnosis` completa — la única interpolación nueva es `path`, nunca `credential["value"]`.

## Evidencia requerida

- **Archivos modificados (diff `26667b5^..HEAD`):** `tests/test_006_003_rf2_review_fixes.py` (nuevo, 566), `install.sh` (+142/−30), `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (+12/−6), más docs de estado del orquestador (`docs/.cdad-state.json`, `rf2-red.md`, `rf2-green.md`).
- **Comandos y salidas:** los transcriptos arriba (hash del contrato; focal 6/6 en 72.61s; sonda dry-run 1 passed con salidas citadas; u7+ownership 17/17 en 252.55s; grep de `IFS=$'\t' read` residual).
- **Commit:** `738a380 fix: 006-003 review-fix 2 GREEN (B-1 sha-less manifest records never removable + OPT-1 env-branch diagnosis names the credential file)` — HEAD `83569e8` (doc de estado posterior, ajeno al producto). Sin push, sin `--no-verify` (declarado por el GREEN; `git log` consistente).

---

## Disposición del orquestador (2026-10-18)

0 bloqueantes: B-1 y OPT-1 cerrados. **OPT-2** (el comentario de `install.sh:663-664` sobre symlinks sin digest contradice el orden real del código, que es más conservador y preserva) pasa a deuda: no cambia el comportamiento, no pierde datos y solo se alcanza con un manifiesto editado a mano.
