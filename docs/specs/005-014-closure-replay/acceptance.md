# Aceptación — 005-014-closure-replay (T2)

**Escenario de reanudación con el CLI real sobre un proyecto descartable.** Instrumento: el CLI **del repo** (`skills/cdad-cycle/scripts/cdad_packet.py`) como subproceso, sobre un proyecto descartable en `<tmp>` con el `HOME` del subproceso en un tempdir vacío; **nunca** este repo ni HOME (patrón de `docs/specs/005-012-transition-registration/acceptance.md:3-8,57-59`). Arnés fuera de git: `.cdad/local/005-014-replay-acceptance.py`. Fixtures sintéticos y anónimos (epic y feature `demo`, sin datos del dueño).

**Comando:**

```
python3 .cdad/local/005-014-replay-acceptance.py
```

## Ciclo representativo, registrado SÓLO con la operación

`open-unit` → `register-transition --transition gate --stage specification` (pin del contrato) → `prepare` + `record-dispatch` + `receive` de una entrega (para PD-8(a)) → `register-transition --transition closure --stage feature-closure --approve-by … --closure-path docs/specs/<feat>/closure.md`.

Sin edición manual del state: el state del fixture se escribe UNA vez (bootstrap) y toda transición posterior pasa por el CLI.

| Paso | Observado |
|---|---|
| cierre aplicado | rc=0; `active_feature: null`; **1** entrada `transition: "closure"` |

## AC-1 / AC-3 — «interrupción» y repetición de la MISMA orden

| Observable | Valor |
|---|---|
| rc de la repetición | **0** |
| el no-op lo dice (`already registered`) | sí |
| nombra la entrada existente (su `transition_key`) | sí |
| `docs/.cdad-state.json` byte a byte igual (`sha256` antes = después) | **sí** |
| entradas `transition: "closure"` | **1** (la original, sin reescritura) |
| `validate-state` tras el replay | rc=0, `VALID: idle` |

## AC-2 — repetición con OTRO payload (otro `--stage`)

| Observable | Valor |
|---|---|
| rc | **2** |
| marcador | `state incoherent` |
| nombra la feature y su estado (`done`) | sí |
| contiene `open-unit` / `open the unit` | **no** |
| `sha256` del state antes = después (sin efectos) | **sí** |
| entradas `transition: "closure"` (no re-cierra) | **1** |

## Evidencia cruda

`.cdad/local/runs/005-014-acceptance.json` (no versionado):

```
[ciclo]               rc=0, closure_entries=1, active_feature=null
[AC-1_replay_identico] rc=0, dice_noop=true, nombra_entrada=true, bytes_iguales=true, closure_entries=1
[AC-3_reanudacion]    validate_rc=0, "VALID: idle"
[AC-2_cierre_distinto] rc=2, marcador=true, nombra_feature=true, nombra_estado=true,
                      sin_open_unit=true, bytes_iguales=true, closure_entries=1
[estado_final]        sha256 del state final a472be7a…, 1 entrada de cierre,
                      transition_key 4a47ef0e…
```

## Límites declarados

- La mitad «árbol» de INV-7 no se asevera (el lock/cleanup de la operación crea y borra su archivo): lo asertado es el state byte a byte (misma salvedad que declaran los focales de 005-012).
- El escenario es una corrida representativa, no una medición estadística.
- La suite completa no se corre acá: la corre quien cierra, una vez, en el worktree de cierre.
