# T3 — cierre del gate GREEN (010-004)

Fecha: 2026-10-30 · Feature: `010-004-packet-dispatch-ergonomics` · Execution:
`exec-010-004-packet-dispatch-ergonomics-001` · Packet recibido:
`010-004-packet-dispatch-ergonomics-implementer-green-003` (attempt 24) ·
Recibo: `c0a83da6e080892eb3172e282d23eb1112baaf8eac093a2e02b6aca074cac33f`
(bundle `5a870fedf4f8997bb680302f46bd68e66da87f944922697e7dc1a0695621d8b4`).

Verificación propia del orquestador, sin confiar en el reporte del rol. Todas las
cifras son líneas resumen reales de ejecuciones locales en este árbol.

## 1. Alcance del commit del rol

`git show --numstat --format= 931dddea`:

```
141     0       skills/cdad-cycle/scripts/cdad_packet.py
```

`git show --name-only --format= 931dddea` → solo
`skills/cdad-cycle/scripts/cdad_packet.py`: el diff es **puramente aditivo**
(0 líneas eliminadas) en tres hunks — `build_parser()` (añade `--route` solo a
`render`, `choices=("C",)`), una sección nueva tras
`_resolve_request_execution_context`, y el branch dedicado en `main()`:

```
if args.command == "render" and args.route == "C":
    ... route_c_identification(...)
    return 0
request = _load_json(Path(args.request), "packet request")
```

La rama por defecto (`render` sin `--route`, `validate-request`,
`validate-packet`) queda textualmente intacta.

Superficies conservadas: wrapper `scripts/cdad_packet.py` sha256
`df6463fbd968f20b30ca4df308064d93ffa44644d0549a4c3c39afea3477800a` (sin
cambio) y `git diff --stat 1b96efa5 -- tests scripts` vacío (tests del RED
`e5701b84…` intactos).

## 2. Evidencia medida

| # | Comando | Línea resumen real |
|---|---|---|
| (a) | `python3 -m pytest tests/test_010_004_t3_red.py -q --tb=line` | `7 passed in 6.78s` |
| (b) | `python3 -m pytest <los 6 reutilizados de red-t3.md §4> -q --tb=short` | `6 passed in 21.76s` |
| (c) | `render` (sin `--route`) del packet de esta unidad vs su `PACKET.md` | byte-idéntico, sha256 `90d519df1f7e87222e6dfe1eb217e0647607b5d51e4014d548224debcc22255b` en ambos |
| (c') | `render` (sin `--route`) de un paquete histórico (`…-test-writer-red-003`) vs su `PACKET.md` | byte-idéntico, sha256 `c323e4a67a19f7c5e192b56457643a63f2c58510746dfa6c78039effbdc7b235` en ambos (el mismo que declara `red-t3.md` §1) |
| (d) | `render … --route A` | rc=2, stdout 0 bytes, `ERROR: cdad_packet.py render: argument --route: invalid choice: 'A' (choose from C)` |
| (d') | `render --route C` con contexto v1 legítimo | rc=2, stdout 0 bytes, `ERROR: route C requires a v2 execution context: … schema_version 1. A v1 context is recognized for historical use and is never converted or relocated; prepare a new v2 execution (prepare --new-execution) …` |
| (e) | pins | spec `fc6b2ccc…`, plan `2ae8ada3…`, policy `f508ab1e…`, execution.md `9bf27909…`, plan del epic `b9375189…` — los cinco coinciden con los aprobados y con los declarados en la cabeza de continuidad del attempt 24 |
| (f) | `python3 -m pytest tests/test_role_packet_render.py tests/test_role_packet_review_regressions.py tests/test_role_packets.py tests/test_role_packet_consumers.py tests/test_packet_prepare.py tests/test_010_004_t3_red.py tests/test_010_004_t2_red.py -q --tb=short -p no:cacheprovider` | `65 passed in 238.40s (0:03:58)`, rc=0 |

Control positivo de C verificado además sobre el paquete de la propia unidad:
`render --route C` → rc=0, declaración literal `Route C — explicit file backup`
y un único bloque ```json con los 7 campos de §4.2 (`project_root` absoluto y
canónico; `execution_context`, `request`, `packet` relativos al proyecto;
`contract` con su sha256 verificado).

Nota de método para (c'): `render`/`validate-packet` exigen que el request sea
el `active_packet` del estado, de modo que un paquete histórico no puede
re-renderizarse en la raíz viva sin alterar el estado. La comprobación se hizo
en una **copia aislada** del árbol (`docs/` + el packet histórico + su
`execution.json`, con `active_packet` apuntado a ese packet en la copia): los
bytes de `docs/` y del packet son los del repo (mismo sha256) y el estado de la
raíz viva no se tocó. `validate-packet` en la copia: rc=0 (comparación desde el
marcador A hasta el final).

## 3. Selección proporcional, no suite completa

La corrida de cierre de T3 cubre las superficies que T3 toca —los archivos
conocidos de `render`/`validate` (`test_role_packet_render.py`,
`test_role_packet_review_regressions.py`, `test_role_packets.py`,
`test_role_packet_consumers.py`, `test_packet_prepare.py`) más los dos archivos
de la unidad (`test_010_004_t3_red.py`, `test_010_004_t2_red.py`)—: 65 passed,
rc=0. **La suite completa del repo no se corrió en este cierre**: por
`plan.md` §«Gates de aceptación» corresponde al **gate transversal de T4**
(pedida explícitamente en su paquete al responsable de integración) y, como
suite de cierre, a **T6**. Se declara, no se omite.

## 4. Qué queda declarado y qué NO

Declarado green con esta evidencia: **PC-01, PC-02, PC-08a y PC-09** de
`spec.md` (identificación C determinista y concordante; rechazos v1 / request no
publicado / contexto no canónico / paquete divergente sin identificación
utilizable ni efectos; regresión mecánica PC-08a con la frontera de preámbulo de
§4.4; diagnósticos distinguibles, con siguiente acción y referencia segura, sin
divulgar el cuerpo ni cambiar semánticas de salida).

NO se declara todavía:

- **PC-08b** (instrucción revisable del intake y de sus salidas generadas):
  pertenece a **T4**, con revisión semántica independiente posterior. El par
  `PC-08` no se declara completo: en `postconditions_status` la clave `8` queda
  green con alcance explícito «PC-08a» y T4 la re-registra al cerrar PC-08b.
- **T4, T5 y T6**: no abiertos. T4 queda encuadrado en esta misma sesión
  (decisión y paquete preparado, sin despachar).
- **Suite completa del repo**: ver §3.
- **Consumidor instalado aislado y distribución regenerada** (PC-12): T4/T5.
