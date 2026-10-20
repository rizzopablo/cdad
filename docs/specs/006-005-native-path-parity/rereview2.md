# Re-review focal 2 — 006-005

**Revisión:** `42b34a9..77a61c1`, incluidos RED `5306a28`, GREEN `88491b2` y testfix `b2395a2`. Hashes de contrato y política coincidentes con el paquete.

## B — Bloqueantes

**Ninguno nuevo. B-3 y B-4 quedan cerrados.**

| Hallazgo | Cierre y evidencia |
|---|---|
| **B-3** | `skills/cdad-cycle/references/re-entry.md:27-31` distingue los tres estados de llegada. La externa comienza en `validate-receipt`, sin escenificar ni recibir nuevamente; `:89-97` conserva esa distinción al explicar la equivalencia. |
| **B-4** | `skills/cdad-cycle/scripts/cdad_dispatch.py:705-708` conserva `parent: unknown` cuando la fila expone padre sin declaración. `:750-768,790-810` separa contradicción, incertidumbre y acreditación. No requiere enmienda contractual. |

## Recorrido: instrucción → salida real → siguiente comando

### Vía externa

1. Los generados ordenan consumir el sobre y prohíben una segunda recepción: `agents/cdad-orchestrator.md:35-42` y `agents/claude-code/cdad-orchestrator.md:39-46`.
2. El módulo registra, escenifica, ejecuta `receive`, elimina los transitorios y devuelve **el recibo durable**: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:1974-2016`.
3. La referencia consultada ahora conduce a `validate-receipt` → `materialize` con autorización explícita → `register-transition`: `skills/cdad-cycle/references/re-entry.md:31,55-77`.

El focal externo ejecutó `dispatch`, validación del recibo y materialización con **rc=0**. No necesita reconstruir un descriptor.

### Vía nativa y E1 con `--session`

1. Los generados ordenan herramienta nativa → `record` → `receive`: `agents/cdad-orchestrator.md:30-34` y `agents/claude-code/cdad-orchestrator.md:34-38`.
2. `record` registra un intento y devuelve **el descriptor escenificado**, no un recibo: `skills/cdad-cycle/scripts/cdad_dispatch.py:1024-1042`.
3. La referencia conduce desde ese descriptor a `receive`; después aplica la secuencia común: `skills/cdad-cycle/references/re-entry.md:30,55-77`.

Comprobación adicional sobre proyectos descartables y módulo real con store sintético:

| Declaración | Identidad | I8 | `receive` | `validate-receipt` |
|---|---|---:|---:|---:|
| `--session`, sin `--parent` | No acreditada; entrega PD-6 | Uno | rc=0 | rc=0 |
| `--session`, padre coincidente | Acreditada | Uno | rc=0 | rc=0 |
| `--session`, padre contradictorio | `blocked`, sin entrega | Sin acreditación | No procede | No procede |

El tercer caso está cubierto por `tests/test_006_005_reviewfix2.py:325-378`. Los dos primeros fueron también ejecutados hasta recepción y validación durante esta revisión.

## Lock PD-12 y permisos

**El testfix conserva lo que protegía el lock anterior.** Sustituye ventanas de líneas por los dos símbolos, comprobados separadamente: `tests/test_005_006_t3_epic_features.py:294-297,374-432`. Conserva presencia de ambas regiones y añade comprobaciones de cardinalidad y estado no cerrado.

Los enforcement siguen en `skills/cdad-cycle/scripts/cdad_packet.py:598-605,1695-1712`; ese archivo no cambia en este diff. El lock sigue siendo estructural: sus ventanas textuales no equivalen a una prueba semántica completa.

**Ningún cambio nuevo amplía mapas de escritura.** El único cambio ejecutable modifica correlación; no toca permisos ni destinos de escritura. La reformulación de los positivos B-2 declara expresamente el padre y conserva el contrato: `tests/test_006_005_reviewfix.py:720-796`.

## O — Opcionales

### O-3 — El focal externo comprueba longitud, no identidad de bytes

**Nit · Verdict: OPTIONAL · Bucket: m**

**Ubicación:** `tests/test_006_005_reviewfix2.py:795-805`.

Tras materializar sólo compara la longitud con `part["bytes"]`. Una sustitución de igual longitud pasaría, pese al comentario sobre bytes exactos.

**Mejora:** comparar el digest del destino con el digest declarado por la parte. No reabre B-3: el defecto revisado era el siguiente paso incompatible del procedimiento.

O-1 y O-2 anteriores no se reevalúan ni se convierten en bloqueantes por esta revisión focal.

## Evidencia

Comando ejecutado:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
  tests/test_006_005_reviewfix2.py \
  tests/test_006_005_reviewfix.py \
  tests/test_005_006_t3_epic_features.py \
  tests/test_006_005_u1b_dispatch_entry.py \
  tests/test_004_003_t5_reentry_equivalence.py \
  tests/test_003_006_t3_receive_wiring.py
```

**Salida:** `60 passed in 34.91s`.

También ejecuté mediante un harness Python los dos recorridos nativos indicados, reutilizando `ReviewFixB2Case` y los CLI reales. El primer intento pasó incorrectamente un id a `receive --packet`: **rc=2**. Corregido para pasar `PACKET.md`, ambos dieron **rc=0** en recepción y validación.

Inspección:

```sh
git diff 42b34a9 HEAD --stat
git diff 42b34a9 HEAD -- skills/cdad-cycle/scripts/cdad_dispatch.py \
  skills/cdad-cycle/references/re-entry.md \
  tests/test_005_006_t3_epic_features.py \
  tests/test_006_005_reviewfix.py
sha256sum docs/specs/006-005-native-path-parity/spec.md docs/cdad-policy.json
git status --short
```

**Archivos modificados por esta revisión:** ninguno. **Commit creado:** ninguno.

## Abstentions

- No repetí despachos reales, V-11 ni la aceptación U6 completa; los recorridos ejecutados usan fixtures.
- No ejecuté `make validate` ni leí el archivo privado prohibido. El informe GREEN registra un fallo F011, no un gate verde (`docs/specs/006-005-native-path-parity/rf2-green.md:40,46-47`).
- No ejecuté la suite completa: corresponde al cierre. Este dictamen no sustituye esos gates.
- No acredito independencia de familia de modelo respecto del implementer.

**Veredicto final: apta para cierre respecto de esta re-review focal; quedan los gates propios del cierre.**