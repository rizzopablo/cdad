# Corte C — 004-002 (v1 → v2), 2026-10-01

Procedimiento del corte en `plan.md`. Orquestador: Claude, por delegación del
dueño. Instalación aislada para el corte y T7 (decisión del dueño en
`owner-decision-policy-2026-10-01.md`).

## 1. Último paquete v1

- Paquete activo terminal: `004-002-project-execution-bootstrap-implementer-review-fix-007`,
  estado `completed`. No queda trabajo `prepared` ni `dispatched`.
- 65 paquetes v1 en `.cdad/packets/` (ignorado por git); sus hashes quedan en
  `evidence/cut-c-v1-packets.sha256` (sha256 del manifiesto:
  `8eb7622dea935cff1f87df0c62319e705d32143510db66eda725079857bbf20b`).

## 2. Herramienta anterior, contexto y state terminal

- Productor v1 fijado: copia instalada `~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py`
  (== `472c569`).
- Hashes (sha256):

```
8a4c1300792e1680931e93a99821d4b059b794cb98627f56159e2b9b5a75fd5a  .cdad/execution.json
4691a26509060820f2634cfd0d5e7c9f57334367d74ee2c9cae5d7f41d8f3fb5  .cdad/execution-004-001.json
1fd6eae47a1d5f3fedb5c5eb752e25a72206bd08fd7d7913b7f8a0bb5e0457f3  docs/.cdad-state.json
1037f126db130fbec7ce97a0cf2ebf3d52630beee9eafd1918b94d30b9e6ed03  ~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py
```

- El state terminal v1 es el de `b9a790b` (`docs/.cdad-state.json` arriba).
  El ledger interino (`dispatch-ledger.md`) se conserva tal cual; no se
  convierte en intentos v2.

## 3. Comprobación de T6

- T6 cerrada con review conforme tras su review-fix (`review-t56.md`,
  `supervision-record.md`); suite de cierre 284 passed en `28324af`.
- Política materializada por el dueño: `docs/cdad-policy.json`, sha256
  `f3474f36ef68122480488fe0c5bf2a852263f51b7067b760dfd3783f6a0ec216`;
  `validate-policy` → VALID.
- Autoridad verificable (I2): `stage_history` con la spec de 004-002
  aprobada por Pablo y `hitl_delegation` vigente para el epic 004.
- Producto instalado de forma aislada desde `9891e0c`
  (código igual a `28324af`): `install.sh --basic` → Verify PASS, 11
  agentes; CLI instalado sha256 `c249cc5c432f0b46ec1f1fd98aff30a1e972a99f69f62ab4de56f11946fab765`,
  idéntico al del repo.

## 4. Primer intento de publicación v2: rechazado (hallazgo W-1)

`prepare --new-execution --role test-writer --substage red` desde la
instalación aislada → **rc 2, `hitl_delegation is not active`, sin
escrituras** (`.cdad/execution.json` v1 intacto por sha256; sin
`.cdad/executions/` ni `.opencode/agents/`). El rechazo sin publicación es
correcto (PD-3, PD-11), pero su causa es un defecto que el recorrido real
encontró:

- **W-1:** el CLI exige `hitl_delegation.status == "active"`. I2 no lo pide
  (presencia, `source` existente, `scope` que nombre el epic, epic activo y
  sin `revoked_at`), y la spec exige reconocer los registros vigentes "sin
  exigirles retrospectivamente campos exclusivos de otro epic". El registro
  real de este repo no tiene `status`. Los tests de T2 lo incluían en sus
  fixtures, por eso no apareció antes.
- **Disposición del orquestador:** se corrige el producto, no el registro
  del dueño. Regla: sin `status`, deciden las condiciones de I2; con
  `status`, debe ser `active` (cualquier otro valor → no activa). La guía se
  alinea. El corte todavía no publicó nada, así que el micro-ciclo usa el
  productor v1 fijado y este intento no cuenta como un segundo corte (plan,
  paso 6).

### W-1b y W-1c (sonda del orquestador sobre una copia del repo con el state real)

Con W-1 corregido (`564b7a8`, `f9bb3a8`; suite 290 passed), una sonda sobre
una copia del repo con el state real encontró dos bloqueos más del mismo tipo.
Desactivados ambos solo en la copia, el bootstrap pasa (rc 0); no hay otros.

- **W-1b:** el CLI exige `hitl_delegation.epic_id`; I2 acredita el epic por
  `scope`, y el registro real no tiene `epic_id`. Disposición: si `epic_id`
  existe, debe coincidir; si falta, decide `scope`.
- **W-1c:** el `scope` real es `"epic-004-single-source-planning: alcance
  del epic, …"`. El tokenizador de F2 no separa por `:`, así que el token
  queda `epic-…-planning:` y no coincide. Disposición: `:` y paréntesis
  también separan tokens. Se conserva F2: coincidencia exacta del token,
  nunca subcadena ni prefijo de otro identificador.

## 5. Estado terminal v1 actualizado (tras W-1, W-1b y W-1c)

Los micro-ciclos de W-1 agregaron paquetes v1 antes de la publicación. Último
paquete v1: `004-002-project-execution-bootstrap-implementer-green-008`
(`completed`). El estado terminal v1 queda en `a129ffb`:

- paquetes v1: 69; manifiesto `evidence/cut-c-v1-packets.sha256` (reemplaza
  al de §1), sha256 `6e7057265dcc91d68fe2a7e5f32d43db99c150febddb7e14c5c38be0f1332b51`;
- `docs/.cdad-state.json` sha256 `759cdc0729c8a1ca44f428088c7844f979a9b1065fc1301cb03f4628a28a5abb`;
- `.cdad/execution.json` (v1) sha256 `8a4c1300792e1680931e93a99821d4b059b794cb98627f56159e2b9b5a75fd5a` (sin cambios);
- instalación aislada reinstalada desde `a129ffb`: Verify PASS; CLI
  instalado idéntico al del repo (sha256 `27da4df5…`).

## 6. Publicación v2 (pasos 4–5)

`prepare --new-execution --role test-writer --substage red` desde la
instalación aislada, con el state y la delegación reales sin modificar →
**rc 0**:

- ejecución anterior (v1): `exec-004-002`, `.cdad/execution.json` intacto
  (sha256 verificado antes y después);
- ejecución nueva (v2): `exec-004-002-project-execution-bootstrap-001` en
  `.cdad/executions/exec-004-002-project-execution-bootstrap-001/execution.json`,
  `policy_sha256` = la política aceptada (`f3474f36…`);
- primer paquete v2: `004-002-project-execution-bootstrap-test-writer-red-019` (`prepared`), primer encargo de T7 (matriz
  integral de aceptación);
- agentes de proyecto publicados en `.opencode/agents/` (11 + manifiesto),
  derivados de la instalación aislada; el test-writer deniega read/grep/glob
  sobre las raíces de implementación de la política;
- `validate-state` → VALID sobre la ejecución v2.

Desde esta publicación, todos los encargos nuevos de 004-002 son v2
(productor: instalación aislada, `prep2.sh` del orquestador).
