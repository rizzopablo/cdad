# Gate de CI — un comando, una corrida, un veredicto atribuible

`scripts/cdad-ci-gate.py` ejecuta los gates compartidos del ciclo en el orden fijado, deja la evidencia de
la corrida y falla cerrado cuando el verde no es atribuible. No publica, no despliega y no necesita
credenciales.

## Uso

```bash
python3 scripts/cdad-ci-gate.py --base origin/main
```

| Opción | Obligatoria | Default | Para qué |
|---|---|---|---|
| `--base <ref>` | **sí** | — | Ref contra la que se enumeran los cambios (sin default: un default adivina y miente) |
| `--repo-root <dir>` | no | checkout del script | Costura de test (repos sintéticos) |
| `--evidence-root <dir>` | no | `.cdad/local` | Base donde se crea la raíz de esta corrida |

Códigos de salida: `0` verde atribuible · `1` rojo (causa nombrada) · `2` error de uso.

## Qué corre, en qué orden

1. `validate-state` — el estado del proyecto ligado a su ejecución.
2. `surface --base <ref> --collect-only` — **sólo clasificación** (no ejecuta tests). Se declara «no
   aplica» cuando el cambio toca únicamente rutas `documentation` de la política.
3. `cdad-doctrine-check.py --quiet` — la doctrina de tests por contrato.
4. `tests/validate-odoo-specialization.sh` — la especialización Odoo.
5. `cdad-suite.py close --all` — **la única** corrida de pytest de la corrida entera.

El gate no reimplementa ninguno de esos comandos: los invoca. `make validate` queda fuera a propósito
(exige instalar los agentes en un HOME real).

## Dónde queda la evidencia

Cada invocación crea una raíz nueva `gate-<utc-stamp>-<pid>-<hex>` bajo `--evidence-root`, con:

- `gate.json` — veredicto para máquina (commit, dirty, base, gates con su rc, pytest con fallos y skips,
  atribución, canario, carga).
- `suite-report.md` — la misma información para humanos.
- `attempt-*/` — lo que `close` reserva: `attempt.json`, `stdout.log`, `stderr.log`, canarios.

Dos corridas nunca comparten raíz. Incluso una corrida que falla antes de llegar a `close` deja
`gate.json` con su causa.

## Cuándo el verde es atribuible

Sólo si hay **exactamente un** intento, está en estado `finished`, su resumen está verificado, su `rc` es
`0`, su `commit` no es nulo y el árbol está limpio. Cualquier otra combinación sale `!= 0` y nombra la
causa (`commit-null`, `dirty-no-cero`, `attempt-no-finished`, `summary-unverified`, `sin-intento`,
`intentos-multiples`, `close-rc`, `surface-rc`, `doctrine-rc`, `odoo-rc`, `validate-state-rc`,
`base-invalida`, `cambio-ilegible`, `fallo-interno`).

## Qué NO hace

- No publica: no hay push, tag, deploy ni red.
- No instala nada ni depende del HOME del operador.
- No corre `make validate` (necesita una instalación real).
- No reintenta para ocultar un rojo, ni promedia intentos.
- No decide qué runner lo ejecuta: es neutral de proveedor. Versionar un workflow (`.github/**`) o un
  target de `Makefile` exige una enmienda de la política de rutas, que hoy los clasifica `unclassified`.

## Costo

Una suite completa por corrida: 46–103 min medidos según la carga del host, sin paralelismo. El criterio
del epic pide la suite en cada push; reducirla (por ejemplo, sólo superficie en pushes de documentación) es
una decisión del dueño, no del gate.
