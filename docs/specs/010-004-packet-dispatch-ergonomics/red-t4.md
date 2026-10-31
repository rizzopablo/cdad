## 0. Validación Route C (antes de trabajar) — PASS

- Exactamente una identificación, sin marcador A y sin cuerpo inline: no hay mezcla de rutas (§4.3).
- Los 7 campos canónicos de `render --route C` coinciden **exactamente** con el bloque recibido: `project_root`, `packet_id`, `execution_id`, `execution_context`, `request`, `packet`, `contract` (kind/path/sha256/commit). Diferencias: **ninguna**.
- Los 4 metadatos adicionales del despacho (`route`, `packet_sha256`, `request_sha256`, `plan`) los verifiqué contra los archivos: `packet_sha256=fa2c96a8…` y `request_sha256=16325428…` coinciden con los archivos publicados; `plan.sha256=2ae8ada3…` coincide con `plan.md`; el `contract` del bloque coincide con el de `REQUEST.json`. Es el mismo formato de metadatos del despacho que registró `red-t3.md:3`.
- CLI del repo con `--project-root <repo>`: `validate-request` rc=0, `validate-packet` rc=0, y `render` (completo) **byte-idéntico** al `PACKET.md` publicado (`diff` vacío). Nada instalado ni modificado globalmente.
- No busqué otro paquete ni caí a legacy.

## 1. Las dos pruebas (archivo nuevo `tests/test_010_004_t4_red.py`, 262 líneas)

**Prueba 1 — `TestDispatchSurfacesNameRouteC::test_pc03_pc12_dispatch_surfaces_name_the_route_c_path` · PC-03, PC-12.** Control positivo primero: `render --help` por subproceso (nunca importa el módulo) exige rc=0 y que la salida nombre `--route`. Después, token estable `--route\s+C` en cada una de las 4 superficies de despacho (`sources/roles/orchestrator.md`, ambos adaptadores, `handoff-prompts.md`); cada ausencia nombra archivo y token.
**R4 (decision-t4-mechanical-guard.md §5):** sin este test, una edición de esas superficies deja el despacho sin instrucción de ruta C con todos los gates verdes; el orquestador vuelve al vehículo inline que ya perdió backticks en un despacho y corrompió un snapshot base64 en otro, y el paquete ejecutado no es el publicado (INV-05/INV-12), con descubrimiento tardío.

**Prueba 2 — `TestRegeneratedAgentsKeepRouteC::test_pc12_declaration_and_derived_orchestrators_survive_regeneration` · PC-12.** (a) Control positivo PRIMERO: literal `Route C — explicit file backup` en `sources/roles/architect.md` y en cada agente de rol derivado de los 4 árboles (glob `cdad-*.md`, excluidos `cdad-orchestrator*`; árbol no vacío). (b) DESPUÉS, RED: `--route\s+C` en los 4 `cdad-orchestrator.md` derivados.
**R4 (decision-t4 §5):** sin este test, una regeneración coherente que no propague el camino (o un derivado parcheado a mano) deja el despacho sin ruta C y todos los gates siguen verdes —determinismo, manifiesto, composición, consistencia estructural y drift entre árboles—; el usuario recibe payloads corruptos y el paquete ejecutado no es el publicado (INV-05/INV-12).

Solo tokens estables (`--route\s+C`, literal de intake); nada de prosa, redacción, orden ni posición. No duplica `test_cdad_generate.py` ni la emisión C de T3. Las rutas son datos del paquete, leídos en tiempo de ejecución.

## 2. Evidencia RED real

```
python3 -m pytest tests/test_010_004_t4_red.py -q --tb=short     # rc=1
FF                                                                 [100%]
tests/test_010_004_t4_red.py:161: in test_pc03_pc12_..._route_c_path
    self.assertEqual(
E   AssertionError: Lists differ: [] != ["sources/roles/orchestrator.md: missing t[326 chars]C')"]
E   + ['sources/roles/orchestrator.md: missing token `--route C` ...',
E   +  'sources/agents/adapters/opencode.md: missing token `--route C` ...',
E   +  'sources/agents/adapters/claude-code.md: missing token `--route C` ...',
E   +  'skills/cdad-cycle/references/handoff-prompts.md: missing token `--route C` ...']
tests/test_010_004_t4_red.py:248: in test_pc12_declaration_and_derived_..._regeneration
    self.assertEqual(
E   AssertionError: Lists differ: [] != ["agents/cdad-orchestrator.md: missing tok[346 chars]C')"]
E   + ['agents/cdad-orchestrator.md: missing token `--route C` ...',
E   +  'agents/claude-code/cdad-orchestrator.md: missing token `--route C` ...',
E   +  'build/staging/agents/opencode/cdad-orchestrator.md: missing token `--route C` ...',
E   +  'build/staging/agents/claude-code/cdad-orchestrator.md: missing token `--route C` ...']
2 failed in 0.45s
```

Ambos fallos son `AssertionError` de la aserción del token `--route C` (líneas 161 y 248), por comportamiento ausente. Ninguno es `ImportError`, `SyntaxError` ni `FileNotFoundError`.

## 3. Controles positivos

- Prueba 1: el fallo ocurre en la línea 161, **después** de que `render --help` pasara rc=0 y nombrara `--route`; el flag es interfaz real del CLI.
- Prueba 2: el fallo ocurre en la línea 248, **después** del control de la declaración; su propio mensaje lo acredita: `declaration control passed for {'agents': 10, 'agents/claude-code': 10, 'build/staging/agents/opencode': 10, 'build/staging/agents/claude-code': 10}`. Precisión: son 10 agentes de rol por árbol (20/20 por par de árboles, como mide M3); la prueba no congela el número, solo exige árbol no vacío y literal presente en todos, para no freezar un dato no contractual (PC-09).

## 4. Diff y commit

```
git diff --cached --stat
 tests/test_010_004_t4_red.py | 262 +++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 262 insertions(+)
git show --name-status --format= HEAD
A   tests/test_010_004_t4_red.py
```

Commit `test(010-004)`: **`4a42778d4fe32379579cfb4286d60fa5a41919cb`** — `test(010-004): RED T4 - guarda mecanica del camino de despacho (ruta C)`. El árbol queda limpio salvo el untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md`, intacto.

## 5. Declaraciones

- No edité tests existentes ni fixtures compartidas (`StateFixture`, `PrepareProject`): solo creé el archivo nuevo.
- No toqué producto, `sources/`, `agents/`, `build/staging/`, `skills/**` ni el CLI; no modifiqué ni instalé nada globalmente (usé solo los scripts del repo).
- No corrí la suite completa: únicamente `pytest tests/test_010_004_t4_red.py -q`. No hice push.
- No leí las superficies bajo prueba (`sources/roles/orchestrator.md`, adaptadores, `handoff-prompts.md`, `sources/roles/architect.md`, agentes derivados): se leyeron solo en tiempo de ejecución dentro de los tests. Tampoco leí código de implementación; mis lecturas fueron el contrato/plan/decisión/cierre de T3, tests existentes y el control-plane del paquete.