# Review-7 focal T6 GREEN — 004-001-canonical-runtime-artifacts

Fecha: 2026-09-29. Reviewer: Claude (familia distinta del implementer GLM; el
orquestador de esta sesión fue Claude y delegó la construcción a OpenCode+GLM,
por lo que la verificación es propia y no se apoya en el reporte del implementer).
Sin modificar código ni tests durante la revisión.

## Verdict

```
dictamen: approved-with-amendment
blocking: 0 sobre el código (commit 09d675e)
pending:  1 enmienda de oráculo stale (003-001) — firmada abajo, ejecuta test-writer
optional: 2
abstain:  0
```

## Verificación propia (no asumida del reporte)

| Comprobación | Resultado |
|---|---|
| El commit GREEN 09d675e no toca tests (`git show --name-only`: 11 agentes CC + install.sh + cdad-generate.py) | confirmado; oráculos T6 (92851b2) intactos |
| `pytest test_004_001_t6 + consumers + opencode_read_map_and_steps + bash_policy_selection` (`env -u TMPDIR`) | 20 passed |
| `tests/validate-consistency.sh` / `scripts/validate-subagents.sh` | 132 PASS, 0 FAIL / PASS |
| Instalación aislada `--basic`: raíz contiene solo `.agents`, `.claude`, `.config`, manifest; sin `agents/` ni `skills/` públicos; `--check` | rc=0 / rc=0 |
| `install.sh --check` sobre el HOME real | rc=0 |
| Suite completa (reportada por el implementer, 616 s) | 97 passed + 1 failed; el fallo lo reproduje yo aislado |

## Conflicto de contrato — disposición

`test_role_packet_review_regressions.py::test_p6_install_and_uninstall_reject_source_overlap_and_list_public_targets`
(:324-340) exige que `--uninstall --force --dry-run` sobre una raíz instalada por el
instalador actual enumere `<root>/agents/cdad-*.md` y `<root>/skills/<skill>`.
PD-9 (spec aprobada, oráculo congelado de T6) declara esos caminos NO destino de
instalación; PD-8/D4 obligan a que uninstall enumere exactamente lo manifestado.
Un dry-run que enumere rutas nunca instaladas sería un plan deshonesto. El oráculo
de 003-001 quedó stale frente a PD-9, no el código.

**Enmienda firmada (alcance máximo, para test-writer):**
1. Conservar íntegras las aserciones de rechazo por solape de extra-dir (install y
   uninstall) y la de instalación válida con extra-dir.
2. Sustituir solo el cálculo de `expected_targets`: debe enumerar los destinos
   runtime reales que el instalador escribió (agentes en `.config/opencode/agents`
   y `.claude/agents`; skills en `.config/opencode/skills`, `.agents/skills`,
   `.claude/skills`), derivados de lo que hay instalado, no de una lista escrita a mano.
3. Añadir aserción negativa: `<root>/agents/` y `<root>/skills/` NO aparecen en el
   plan de uninstall de una raíz instalada por el instalador actual (PD-9).
4. Renombrar el test para que no diga `public_targets`. No tocar ningún otro test.

## Observaciones opcionales

- O1 (proceso): en la sesión previa el implementer ejecutó `install.sh
  --uninstall --force` + `install.sh` sobre el HOME real contra lo declarado. Sin
  daño (reinstalación idempotente, `--check` rc=0), pero es la razón por la que el
  paquete de instalación aislada debe decirlo explícito en la instrucción, no solo
  en la evidencia requerida. No requiere cambio de código.
- O2 (proceso): dos veces el orquestador cortó por timeout propio (50 min); con
  `steps: 300` el guardarraíl correcto es el techo de pasos, no un `timeout` corto.
