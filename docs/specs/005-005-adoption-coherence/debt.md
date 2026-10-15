# Deuda y observaciones — 005-005-adoption-coherence

Registrada al cierre de la review formal (stage 4, `review.md`, veredicto
`changes-approved` **sin bloqueantes**), 2026-10-09. Los opcionales no prolongan
el ciclo (calibración de la review); se registran con su disposición.

## Opcionales de la review

- **O1 (bucket l) — Registro de activación ilegible → caída silenciosa.** Si
  `.cdad/activation.json` está corrupto o su `adopted_root` es inválido,
  `_activation_registry` cae al camino siguiente (global/HOME) sin diagnosticar:
  hueco delgado de INV-7/PD-13. Cierre: rama que nombre el registro corrupto
  (`PolicyError` rc=2 o aviso por stderr).
- **O2 (bucket l) — «Versión desconocida» no explícita.** El diagnóstico de
  contradicción no distingue una instalación sin marcador
  (`_describe_installation`). Cierre: texto «(version unknown — no marker)»
  cuando `_installation_version` es None.
- **O3 (bucket l) — PD-1 sin test de sus rebanadas no-input.** El
  `--expected-output ''` conservado hoy lo cubre `validate_request` (preexistente),
  pero PD-1 no tiene subtest propio. Cierre: subtest `--expected-output ''` →
  rc=2 sin efectos.
- **O4 (bucket l) — `CDAD_OPENCODE_AGENTS_DIR` no esterilizada en el env de los
  tests T1** (T3/T4 sí la limpian) → flakiness potencial en la máquina del dueño.
  Cierre: limpiar la variable en `run_cli` (una línea).
- **O5 (FYI, dueño) — Instalación v8 vigente con `source_version: null`.** La
  instalación desplegada es anterior al marcador; el defecto se corrigió en la
  versión nueva (`install.sh` declara `version.txt` + `source_version`). Cierre
  post-despliegue (tarea del dueño): `source_version` del manifiesto ==
  `version.txt` de la raíz.

## Observaciones de gate

- **Guard de lectura vs `instruction_sources`.** Las `instruction_sources` de los
  paquetes viven en `skills/cdad-cycle/packets/**` (raíz de implementación) y el
  guard de lectura del test-writer las deniega: el rol ejecutó con el cuerpo
  compuesto de `PACKET.md` (que contiene la instrucción de rol + substage). No
  bloqueó nada; queda como observación del entorno (separación
  principio/decisión/entorno en `review.md`).
- **`opencode reload` NO verificado.** El CLI instalado (1.18.32) no tiene el
  subcomando; un `serve` aislado responde 401 sin token. El adaptador documenta lo
  verificado (en proceso nuevo, un agente de proyecto sombrea al global del mismo
  nombre) y declara lo no verificado (PD-15/D6). En el servidor permanente del
  dueño (2.0.22) queda por comprobar tras el despliegue.
- **VERIFY del dueño abierto (D7).** El criterio conserva `~/.claude`,
  `~/.agents` y `~/.config/opencode` (convención genérica de runtime / HOME
  reservado al dueño) y retira las rutas instalación-específicas; el encargo
  enumeraba `handoff-opencode.md:63` y `execution.md:21` → confirmar si también
  deben retirarse.
- **Sin CI.** El gate es la suite local + `make validate`; los 2 FAIL F011 son
  preexistentes y ajenos al diff.
