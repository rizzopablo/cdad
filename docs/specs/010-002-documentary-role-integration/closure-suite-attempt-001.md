# Suite de cierre, intento 1 — medición, cuatro regresiones y deriva del canario

**Fecha:** 2026-10-31 (UTC del entorno).
**Ámbito:** orquestador CDAD, bajo el mandato HITL del 2026-10-30 (§1 y §3).
**Objeto:** el primer intento de la suite de cierre de `010-002` midió el commit
`35b81093` y **no pasó**. Este documento registra la medición, clasifica cada
fallo y deja declarado el límite que el canario no puede cubrir. No es un gate:
es la evidencia que obliga a corregir antes de reintentar.

## 1. Medición

```
python3 scripts/cdad-suite.py close --all --evidence-root .cdad/evidence/010-002-closure
```

| Campo | Valor |
|---|---|
| Evidencia | `.cdad/evidence/010-002-closure/attempt-20261031T154550334011Z-2834037-2f17e4a0` |
| Commit medido | `35b81093195651e6484ca0aa705ca52a562d23f3` |
| `dirty` | 1 (el `discovery.md` de `010-000`, declarado fuera de índice) |
| Inicio / fin | `15:45:50Z` / `16:52:03Z` |
| Duración | `3967,32 s` (1:06:07) |
| Resultado | **`rc=1`** — `4 failed, 1914 passed, 5 skipped`, 0 errores |
| Canario | `delta_lines: 18` |

Los 5 `skipped` son los mismos condicionados por entorno que ya declaró el
cierre de `010-001`.

## 2. Los cuatro fallos, clasificados

Los cuatro son **regresiones estructurales introducidas por esta unidad** en
superficies compartidas. Ninguno es un fallo de entorno y ninguno toca la
sustancia del producto de `010-002`: los 29 tests del módulo y los 7 de
propiedades siguen verdes en la misma corrida.

| # | Oráculo | Causa medida |
|---|---|---|
| R1 | `tests/test_005_006_t1_start_procedure.py::test_pd10_installed_cli_paths_in_t1_wiring_points` | El GREEN de T4 insertó 9 líneas netas en `SKILL.md` §3.1 (línea ≈137). La fila de la tabla que invoca el CLI instalado estaba en la línea 464, **justo en el borde** de la ventana `(444, 464)` que el test declara; con el corrimiento quedó en la 473. La promesa de PD-10 —«el punto de cableado sigue invocando el CLI instalado y su ruta es corregible»— está intacta; lo que se rompió es su localizador. |
| R2/R3 | `tests/test_006_002_u1_delegation_section.py::TestPd2bSourceOwnsDelegationContent` (OpenCode y Claude Code) | El GREEN de T4 reescribió el bloque `delegation` de los dos adaptadores. La asociación `subagent_type` ↔ mapeo rol→subagente sigue existiendo, pero quedó partida por un salto de línea; el control de 006-002 PD-2(b) exige ambos conceptos en la **misma línea** y a ≤80 caracteres. |
| R4 | `tests/test_006_003_u8_acceptance.py::TestPd8bMakeValidate::test_pd_8b_make_validate_passes_on_the_acceptance_install` → `FAIL: F007` | El mismo rewrap eliminó la frase «resolve the stack» del orquestador de Claude Code. F007 la exige por paridad con OpenCode: el orquestador resuelve el sufijo del stack antes de delegar. |

Los tres comparten la misma causa próxima: **el conjunto de regresiones de T4 y
del review-fix no incluía los oráculos de las superficies que el encargo
editaba**. T4 verificó 36 + 78 tests y la matriz Odoo, pero no
`test_005_006_t1_start_procedure.py` ni `test_006_002_u1_delegation_section.py`
ni el validador consolidado; el review-fix verificó el módulo de la unidad, sus
propiedades, el generador y `010-001`, pero tampoco esos tres. El dictamen de
T8 tampoco los ejecutó. La suite de cierre fue el único control que los miró, y
por eso los encontró.

**Consecuencia de proceso, registrada como tal:** una unidad que edita
`SKILL.md` o los adaptadores debe incluir en su verificación los oráculos de
esas superficies, no sólo los de su propio contrato. No es un defecto de
cobertura —los tests ya existían— sino de selección al verificar.

## 3. La deriva del canario, atribuida

El canario (`delta_lines: 18`) corresponde a **un solo archivo**:
`~/.config/opencode/agents/cdad-implementer.md`, que pasó de 12.035 a 11.630
bytes con marca de tiempo `13:42:36 -0300` (y su directorio, que cambió por el
mismo motivo).

**No lo escribió la suite.** El journal del usuario, en la misma ventana,
registra al servidor de OpenChamber (PID 743460) haciendo exactamente eso:

```
13:42:29 openchamber[743460]: [Server] Updating agent: cdad-implementer
13:42:29 openchamber[743460]: Successfully wrote markdown file: .../cdad-implementer.md
13:42:36 openchamber[743460]: [Server] Updating agent: cdad-implementer
```

La traza de la propia herramienta muestra además el modelo que el servidor
arrastra (`opencode-go/muse-spark-1.3-contributor`), que el generador de este
repositorio ya no emite. Los bytes escritos **no son** el derivado del
repositorio (13.141 bytes, SHA-256 `3dbf6c87…` frente a los 11.630 y
`59b5d7c7…` del archivo instalado). Y ningún destino del instalador escapa de
`CDAD_INSTALL_ROOT`: `set_install_paths()` resuelve las siete superficies bajo
la raíz de instalación, y los tests de aceptación afirman explícitamente que
ninguna corrida usa el HOME real.

**Límite declarado.** El canario mide el *entorno*, no sólo la suite. Con otro
gestor de agentes vivo sobre el mismo HOME —el que atiende esta sesión— una
deriva de este tipo no distingue escritura de test de gestión del runtime. Un
`delta_lines: 0` sólo es alcanzable en un entorno sin otro gestor de agentes en
la ventana medida. Lo que sí se puede afirmar, y se afirma: la suite no escribió
en el HOME real y el archivo cambiado no lleva bytes del producto de este
repositorio.

## 4. Qué NO se relajó

- **No se editó ningún test.** Los cuatro oráculos caen son de features
  cerradas (`005-006`, `006-002`) y el control de F007 vive en el validador
  consolidado: se corrigen en el producto, no en el control.
- **No se declararon «fallos de entorno».** Los cuatro son regresiones
  reproducidas en aislamiento, una por una, sobre `HEAD`.
- **No se reintentó la suite antes de corregir.** El intento 1 queda como
  evidencia de que el gate funcionó.

## 5. Qué sigue

1. `review-fix` del implementer sobre los dos adaptadores y `SKILL.md`, con los
   cuatro tests como oráculo congelado y sin tocar tests.
2. Re-verificación de la unidad (módulo, propiedades, generador, `010-001`,
   techo estático, aceptación hermética con el validador) y regeneración
   reproducible de los 22 agentes.
3. Reintento completo de la suite de cierre sobre el commit corregido.

La fragilidad de los dos localizadores —la ventana fija de `005-006` y la
regex por línea de `006-002`— queda registrada en el backlog del epic: son
controles que se rompen con una edición legítima del texto que vigilan.
