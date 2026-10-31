# T2 — cierre del gate GREEN (010-004)

Fecha: 2026-10-30 · Feature: `010-004-packet-dispatch-ergonomics` · Execution:
`exec-010-004-packet-dispatch-ergonomics-001` · Packet recibido:
`010-004-packet-dispatch-ergonomics-test-writer-post-audit-005` (attempt 22) ·
Recibo: `354ab7652e3e8ad2998584fb1c1af5dcfd62520c14a6dd1118be6d86d426ae60`.

Verificación propia del orquestador, sin confiar en el reporte del rol. Todas las
cifras son líneas resumen reales de ejecuciones locales en este árbol.

## 1. Alcance del commit del rol

`git show --stat 60fa29a1`:

```
tests/test_packet_prepare.py | 46 ++++++++++++++++++++++++++++++++++++++------
1 file changed, 40 insertions(+), 6 deletions(-)
```

`git show --name-status 60fa29a1` → solo `M tests/test_packet_prepare.py`. Los
cuatro hunks caen íntegros dentro de los tres tests nombrados por el packet:
`test_p1_prepare_writes_three_files_and_stdout_equals_packet_and_render`,
`test_p2_default_request_derivations_per_role` y
`test_p4_unserializable_state_fails_without_effects`. Ningún test más del
archivo cambia; `StateFixture`, `PrepareProject.__init__`/`execution_path`/`args`
y `tests/test_role_packets.py` quedan byte-idénticos (el grep del diff sobre
esas definiciones no devuelve nada).

## 2. Evidencia medida

| # | Comando | Línea resumen real |
|---|---|---|
| (a) | `python3 -m pytest tests/test_packet_prepare.py -q` | `19 passed in 22.13s` |
| (b) | `python3 -m pytest <14 archivos> -q --tb=no` | `99 passed in 116.14s (0:01:56)` |
| (c) | `python3 -m pytest <14 tests protegidos nombrados> -q` | `14 passed in 41.46s` |

Universo de 14 archivos = 13 C1 (`test_packet_prepare.py`,
`test_006_006_u1_draft_object_form.py`, `test_004_003_t4_validation_fields.py`,
`test_005_007_t2_progressive_plan_validator.py`, `test_004_003_t3_plan_checks.py`,
`test_004_003_t2_plan_review.py`, `test_004_003_t1_draft_contract.py`,
`test_004_003_t2_reviewfix.py`, `test_004_003_t1_reviewfix.py`,
`test_005_007_reviewfix_blockings.py`, `test_006_005_u1c_packet_agent.py`,
`test_006_006_u3_review_route_and_gate.py`, `test_005_007_t6_templates.py`) +
`tests/test_004_002_t7_acceptance.py`.

Los 14 protegidos: los 6 de `tests/test_010_004_t2_red.py`; el PD-12 legacy
intake; el p2 de contexto/out-dir; las 5 PC-08a de `test_role_packet_render.py` y
`test_role_packet_review_regressions.py`; y el C3 f6 de
`test_004_002_t2_reviewfix.py`. Todos verdes; los archivos que los contienen no
tienen diff desde el commit RED `10e6694e` (la única excepción de archivo es
`test_packet_prepare.py`, cuyo diff no toca el test protegido).

## 3. Pins y fixture compartida

```
fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64  docs/specs/010-004-packet-dispatch-ergonomics/spec.md
2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685  docs/specs/010-004-packet-dispatch-ergonomics/plan.md
```

Ambos coinciden con los pins aprobados. La fixture compartida no se tocó: sin
cambios en `StateFixture`, `PrepareProject` ni `test_role_packets.py`.

## 4. Evidencia de cierre — universo completo de consumidores de `prepare`

Comando (una sola invocación; lista reproducida del inventario medido
`fixture-impact-inventory.md` §1, `rg -l "PACKET_CLI|cdad_packet\.py" tests/*.py`):

```
python3 -m pytest $(rg -l "PACKET_CLI|cdad_packet\.py" tests/*.py) -q --tb=no -p no:cacheprovider
```

Archivos: **105**. Línea resumen real:

```
1043 passed, 2 skipped in 1775.91s (0:29:35)
```

`rc=0`, 0 fallos. Los 2 skips son los preexistentes de entorno (skip limpio con
diagnóstico, ya presentes en la línea base del inventario: 64 failed, 980
passed, 2 skipped). La corrida completa se conserva como evidencia por
referencia en `.cdad/closure-t2-105-files.log` (workspace, no versionado).

Nota de medición honesta: el inventario declaró 1046 tests en la línea base
(64+980+2). La colección actual del mismo universo es 1045 (1043+2). No hay
tests añadidos ni eliminados en la ventana (`git diff 3f39eefd..HEAD -- tests`
no muestra `def test_` agregados ni quitados, ni cambios de `parametrize`); la
diferencia de un caso no afecta el resultado (0 fallos) y se declara en vez de
omitirse.

## 5. Qué queda declarado y qué NO

Declarado green con esta evidencia: **PC-04, PC-05, PC-06 y PC-07** de
`spec.md` (preparación nueva declara el localizador canónico, matiz de tres CLI
sin argumento, validaciones compartidas de dominio y coincidencia, independencia
del directorio de invocación y campo histórico ausente).

NO se declara todavía:

- **PC-08a** (garantías de `validate-packet`, incluida la frontera de preámbulo
  de spec §4.4): pertenece al **RED de T3** por decisión A1 vigente
  (`audit-approval-2026-10-30.md`), aún no despachado.
- **T3, T4, T5 y T6**: no abiertos; el RED de T3 queda preparado, sin despachar.
- **Suite completa del repo**: no corrida en este cierre; corresponde al cierre
  de la feature en T6 (política de evidencia).
