## Veredicto por hallazgo

### B1 — CERRADO (con residuo)
- El render de `resume` declara `record: active-record-v1` (`cdad_continuity.py:60,468`), el RED (`test_003_004_t1_reviewfix.py:323-368`) aserta (a) head de `begin` valida contra `continuity-checkpoint-v1` y (b) `projection` valida contra `active-record.schema.json` — **10/10 focales en verde (V1)**. La decisión del orquestador se ejecutó tal cual: aserción en RED, no validación runtime.
- El head es ahora schema-válido **por construcción** para cualquier entrada (los campos son computados o validados por O2; probe A1: `head violations: []`).
- **Residuo R-B1 (nuevo, misma clase de defecto): el render puede violar el contrato que declara.** El CLI no valida `projection` contra `active-record-v1` en runtime, y `_require_key_fields` (O2) sólo cubre `packet_id`/`attempt` — el contenido del cuerpo (`goal`, `decisions[].rationale`, `uncertainties`, `next_action`) viaja sin validar. Probe A1: `resume rc=0` emitiendo una proyección con **4 violaciones** a `active-record-v1`. T2 consume esta proyección (`reconcile-v1`): el consumidor que valide verá el mismo tipo de fallo que motivó B1, ahora en un path no cubierto.
  - Verdict: **OPTIONAL** · Bucket: **m** · Eje: correctness/contract · Dónde: `cdad_continuity.py:199-213` (valida solo la clave), `:426-433,465-479` (emite sin validar).
  - Cierre verificable sugerido (natural en T2): validar `update.goal` (string|null), `decisions[]` (decision+rationale strings), `uncertainties[]` (strings) y `next_action` (string|null) en `begin`/`checkpoint` — fail-closed, mismo mecanismo que O2 — o validar `projection` contra el schema en `resume`. Condición: probe de cuerpo malformado → `rc≠0` en `begin`, o `jsonschema.validate(projection, active-record.schema.json)` garantizado.

### B2 — CERRADO (con residuo)
- La heurística por token `impl` **ya no existe**: `_IMPL_NAME_RE` eliminada (`209643f`), `_is_implementation_reference` clasifica **solo** por `path_policy` de `ROOT/docs/cdad-policy.json` (`:352-355`), el docstring ya no atribuye la regla a un supuesto "RED V6" (attribution falsa corregida, `:35-40`), el fixture del test vive bajo root declarado `build/` (RED `:88-89,385` y fix `071b61b` en `test_p05`), y el control negativo `docs/impl-decisiones.md` visible pasa (V1). Nada de clasificación por nombre queda en la superficie de implementación (V4). Fuente única de verdad: la política, según la decisión. ✓
- **Residuo R-B2: fail-open cuando la política no existe.** `_load_policy` (`:322-329`) devuelve `{}` si `docs/cdad-policy.json` no existe; con `--role test-writer` y sin política, `_visible_references` no filtra nada y la referencia de implementación se expone con `rc=0` (probe A2, V3). Antes de `209643f` el regex de nombre cubría parcialmente este caso; la remoción lo empeora. Contrasta con la postura fail-closed del módulo (roles desconocidos filtrados, `ContinuityError` en todo lo demás).
  - Verdict: **OPTIONAL** (no bloquea el cierre focal: con política presente el comportamiento es el pedido por P5 y verificado) · Bucket: **m** · Eje: correctness/security · Dónde: `cdad_continuity.py:322-329,463`.
  - Cierre verificable sugerido antes de T4 (adopción real): si `--role` está presente y el archivo de política no existe → `ContinuityError` (rc≠0); condición: probe sin política → rc≠0.

### O2 — CERRADO
- `_require_key_fields` (`:199-213`) corre en `_run_write` **antes** de digerir referencias y de cualquier escritura (`:280`); `packet_id` string no vacío (`.strip()`), `attempt` entero con exclusión de `bool`; el diagnóstico nombra el campo (`:206-208,211-213`); el test cubre 6 casos con aserción de store vacío y de `docs/.cdad-state.json` intacto (V1: `test_o02` PASSED). Fail-closed exactamente como pide la decisión. ✓
- Nota menor (no hallazgo): `attempt: true` también se rechaza por el exclusion de `bool` pero el test no lo cubre; comportamiento correcto no verificado por test.

### N1 — CERRADO
- Documentado tal como decidió el orquestador: "JSON is the only output mode (N1); `--json` is kept as an accepted no-op flag" (`cdad_continuity.py:42-43`); el flag sigue aceptado (`:500,510`). ✓

---

## Hallazgos nuevos (no corresponden a B1/B2/O2/N1; de plena diff focal)

- **R-STR (Nit):** `O2` declara que nunca se persiste un head schema-inválido, pero la validez del head contra `continuity-checkpoint-v1` sigue siendo una propiedad **de test**, no una garantía de runtime (el CLI no carga schemas). Hoy es válida por construcción (todos los campos del head son computados o validados); si alguien añade un campo al envelope sin actualizar el schema, nada fallará en runtime. FYI para T2/T3 — Verdict: OPTIONAL · Bucket: l.

## Abstentions

1. **Suite completa + validadores (criterio 10):** no corrida — la instrucción del orquestador acota a focales T1. La última evidencia de suite completa es la del implementer en `209643f` (496 passed / 1 failed sobre su árbol, que era exactamente el estado que `071b61b` corrigió) y el gate "por evidencia equivalente" del ledger #11. No verifiqué la suite sobre `071b61b`/`2c411c2`; el orquestador decide si la exige.
2. **O1 (begin divergente sobrescribe, criterio 3):** sigue abierto por diseño — la decisión lo planifica para T2 ("debe cerrarse antes de T4"). No lo re-evalúe; sin diff en el rango que lo toque. Confirmo solo que la ventana de riesgo T1→T2 persiste.
3. **Probes A1/A2 corren contra `scripts/cdad_continuity.py` (wrapper) en `/tmp/opencode`**: comportamiento del CLI confirmado, pero no verifiqué el flujo de `install.sh` con el wrapper (ya abstención de la review T1, fuera del diff).

**Commits revisados:** `f710617` (RED), `047d1c0` (bookkeeping), `209643f` (GREEN B1/B2/O2/N1), `071b61b` (fix test-writer), `2c411c2` (HEAD, ledger). Ningún archivo modificado por esta revisión (write_scope `[]`).

**Dictamen final:** B1 cerrado con residuo (OPTIONAL, cerrar en T2) · B2 cerrado con residuo (OPTIONAL, cerrar antes de T4) · O2 cerrado · N1 cerrado · sin bloqueantes nuevos en el rango evaluado.
