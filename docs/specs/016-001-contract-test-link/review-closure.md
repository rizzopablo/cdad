Paquete validado por la ruta C; todos los hallazgos están cerrados; sin bloqueantes nuevos.

# Review de cierre — 016-001-contract-test-link

**Veredicto de cierre:** B1, B2, O3 y O4 están cerrados. El fix no abrió ningún hallazgo bloqueante. Queda un único FYI.

## Validación del paquete (ruta C)
- `cdad_packet.py validate-request --request .cdad/packets/016-001-contract-test-link-reviewer-review-002/REQUEST.json` dio rc=0.
- `cdad_packet.py render --request …` comparado con `PACKET.md` mediante `cmp` da **MATCH**.
- `validate-packet` con el contexto de ejecución dio rc=0. El contexto es v2 (`schema_version` 2).
- Los metadatos coinciden: packet_id, execution_id, ruta del contrato y sha256. `sha256sum docs/specs/016-001-contract-test-link/spec.md` da `88b144e5…a8bb…ca688e`, el mismo que declara el paquete.

## Qué revisé
- El commit `f767cc62` solo toca `skills/cdad-cycle/scripts/cdad_contract_links.py` y `skills/cdad-cycle/references/contract-test-links.md`. No toca tests ni el registro.
- En `d46ed99f..HEAD`, el único cambio en tests es el commit RED `49ad6fa7`, del test-writer: 276 líneas añadidas y 2 borradas. Las 2 borradas son solo el docstring, que ahora dice «6 → 11 verificadores». No se debilitó ningún assert.
- `contract-test-links.json` no cambió desde `d46ed99f`.
- Archivos modificados por mí: ninguno. Trabajé en modo de solo lectura y usé directorios temporales de `mktemp` para reproducir los casos.

## Evidencia por punto

**1. B1 cerrado.**
- La función `_flush_paragraph` cierra un span sin balancear al llegar a una línea en blanco, un fence o el final del archivo. En ese caso vuelve a contar las líneas que se habían saltado.
- Caso pedido: PC-1, un párrafo con un backtick suelto, una línea en blanco y PC-2, con un registro que vincula solo PC-1. Resultado: `status invalid`, `gaps [PC-2]`, rc=1.
- Variante sin línea en blanco: también da rc=1 con PC-2 como hueco.
- Contrato normal con PC-1, un ejemplo dentro de un span de varias líneas (PC-9) y PC-2: da `ok`. Las obligaciones son exactamente PC-1 y PC-2, así que el ejemplo sigue excluido. rc=0.

**2. B2 cerrado.**
- El payload trae `mode`, `coverage` y `obligations`. Cada obligación lleva `id`, `promise` y `verifiers`, y la lista está ordenada por id.
- Un contrato sin marcadores, sin índice legacy y con `links: []` da `invalid` con el código `no_obligations`, rc=1. Nunca da `ok`.
- El registro real en modo legacy da `coverage: "cubre las obligaciones indexadas, no una extracción exhaustiva del contrato."`

**3. O3 y O4 cerrados.**
- O3: `_error_belongs_to_link` empareja por igualdad exacta o por prefijo seguido de punto. Lo probé con 11 vínculos y un error en la evidencia de `links[10]`: `links[1]` sigue cubriendo PC-1 y solo se informa `broken_reference`.
- O4: se eliminaron el `pass` muerto y la guarda `is not None`. Esta última era segura de quitar, porque `current_nodeids` se inicializa como lista en la línea 454.
- No encontré efectos colaterales.

**4. Los verificadores no se debilitaron.**
- `python3 -m pytest -q tests/test_016_001_contract_test_link.py` da **11 passed**.
- Validé el registro real con la colección real: hice `pytest --collect-only -q` sobre el archivo de test (11 nodeids) y pasé el resultado como `/tmp/col.json`. El resultado es `ok`, modo `legacy`, 8 obligaciones (PC-1 a PC-8, PC-3 con 2 verificadores), sin errores, rc=0.

## Hallazgos nuevos
- **FYI** (Verdict: OPTIONAL · Bucket: l), en `cdad_contract_links.py` dentro de `_extract_markers`. El validador trata un marcador dentro de un span de varias líneas cerrado en el mismo párrafo como ejemplo. Es lo que dicen la spec y los tests. En CommonMark estricto, en cambio, una línea `<!--` corta el párrafo, así que ese marcador sería real. No es una regresión del fix y no tiene un camino realista de falso verde con los contratos que se usan hoy. Lo dejo como deuda, no como hallazgo.

## Abstenciones
- No ejecuté la suite completa, de acuerdo con la política por momento. Tampoco ejecuté `cdad-suite.py validate`: tomo su `ok` como dato del encargo, sin verificarlo yo.
