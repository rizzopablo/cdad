Validation, implementation and evidence are complete. Here is the FINAL TEXT.

---

# FINAL TEXT — test-writer PROPERTIES (T5, 010-004)

**Paquete:** `010-004-packet-dispatch-ergonomics-test-writer-properties-001` · **Ejecución:** `exec-010-004-packet-dispatch-ergonomics-001` · **Contrato:** `spec.md` sha256 `fc6b2ccc…` (verificado con `sha256sum`) · **Commit:** `2df0f6b5`

## 0. Admisión (Route C) y validación de entrada

- Identificación Route C contrastada contra el render canónico `--route C` (coincidencia exacta del objeto y sus 7 campos). `validate-request` y `validate-packet` rc=0; `render` byte-idéntico al `PACKET.md` publicado (`diff` vacío). Toolchain: scripts del repo con `--project-root` explícito (copia global stale **no** usada ni tocada).
- **Bloqueo declarado (sin workaround):** el paquete declara `instruction_sources` en `skills/cdad-cycle/packets/{common.md, roles/test-writer.md, substages/test-writer-properties.md}`; `skills/**` es raíz de implementación en la policy de este proyecto, así que el guard denegó su lectura (`Permission denied: read`, dos intentos, uno por archivo). Verifiqué sus **digests** con `sha256sum` —coinciden con los declarados— y **no** los leí por otra vía (no `cat`, no copia). Trabajé desde los invariantes/objetivo del paquete validado y el contrato de rol compuesto. Lo reporto como bloqueo, no como cumplimiento.

## 1. Invariantes cubiertos y suficiencia de la selección

| Invariante | Qué se verificó | Por qué alcanza frente a la cobertura existente |
|---|---|---|
| **INV-05** (igualdad completa ≠ igualdad de cabecera ≠ semejanza semántica) | 100 mutaciones sembradas del paquete publicado, por región: **cabecera 25** (indentación, separadores, reordenamiento de claves y relleno de llaves — todas **semánticamente equivalentes**, más 25 cambios de valor), **cuerpo 25**, **bytes posteriores al cierre JSON 25**. Cada una debe rechazarse por `render --route C` sin emitir identificación y **sin normalizar** el archivo; el canónico exacto se acepta antes y después | T3 cubre **una** divergencia de cuerpo por C; `test_role_packet_render` cubre cuerpo/metadata/CRLF por `validate-packet`. Faltaba la región *posterior al cierre* (cero casos) y la cabecera solo tenía casos puntuales: la propiedad ataca justo donde una comparación semántica de cabecera pasaría |
| **INV-04** (ninguna ruta elige otro paquete tras fallar la admisión) | 100 escenarios sembrados de admisión fallida —**copia fuera de la ubicación canónica 25, request no publicado 25, request ausente 25, identificación inválida 25**— contra un **segundo paquete presente en disco**: ningún caso emite identificación (ni la del otro paquete), ni publica paquetes | Las pruebas vigentes rechazan variantes elegidas a mano una por una; ninguna contempla un segundo paquete en disco ni verifica que un rechazo no se convierta en selección. No se duplicó ningún escenario existente |

No se inventaron propiedades para invariantes ya cubiertos (INV-01/02/03/06–12) ni para los no verificables con generador (PC-03/07b/08b/10/11 documentales; PC-12 es el E2E separado). **No edité ningún test existente** (`A` = alta, 0 hunks en archivos previos).

## 2. Semilla y muestras

- **Semilla fija:** `SEED = 20261030`, un único `random.Random(SEED)` por propiedad (sin generadores abiertos).
- **Entradas generadas y ejecutadas:** **100 por propiedad** (`CASES_PER_PROPERTY = 100`), estratificadas con cuota fija **25 × familia** (verificado en la propia prueba con `_family_quotas`).
- Guardas anti-vacuidad: 100 mutantes **distintos**, **ninguno igual al canónico**, las tres regiones presentes; control positivo **antes y después** de cada tanda (la identificación del paquete canónico se exige dos veces, de modo que el rechazo no pueda ser universal).

## 3. Archivo nuevo y mapeo test → invariante → consecuencia

**`tests/test_010_004_t5_properties.py`** (738 líneas; reutiliza `PublishedPacketCase` y los oráculos de ruta C de T3; CLI siempre por subproceso).

| Test | Invariante | PC | R4: sin este test el usuario… |
|---|---|---|---|
| `test_inv05_complete_equality_rejects_every_seeded_byte_divergence` | INV-05 | PC-08a (§4.4), PC-01/PC-02 (§4.2) | …una comparación «semántica» de cabecera o una normalización de bytes despacharía un paquete cuyas instrucciones nunca se validaron: el encargo ejecutado no sería el publicado (I-5: un despacho real perdió backticks). |
| `test_inv04_failed_admission_never_emits_another_packet_identification` | INV-04 | PC-02 (§4.2), PC-03 (§4.3) | …un rechazo podría deslizarse al paquete que sí existe en disco (u otra copia) y se ejecutaría un encargo que nunca fue admitido: el rechazo se convertiría en selección silenciosa. |

## 4. Evidencia real

```
$ python3 -m pytest tests/test_010_004_t5_properties.py -q
..                                                                       [100%]
2 passed in 71.82s (0:01:11)
rc=0
```

Regresión proporcional de la unidad (T2/T3/T4, sin suite completa):

```
$ python3 -m pytest tests/test_010_004_t2_red.py tests/test_010_004_t3_red.py tests/test_010_004_t4_red.py -q
...............                                                          [100%]
15 passed in 15.29s
rc=0
```

Baseline PC-08a reutilizado (solo lectura de apoyo): `5 passed, 20 deselected in 21.93s` — esa corrida se lanzó con tubería `| tail`, por lo que su `rc` **no quedó capturado**; no la uso como evidencia de gate. `ruff check` sobre el archivo nuevo: `All checks passed!`

## 5. Commit

`2df0f6b5` — `test(010-004): PROPERTIES T5 - INV-05 e INV-04 sembradas (semilla 20261030, 100 entradas c/u)`
`git show --name-status --format="" HEAD` → **una sola ruta**: `A tests/test_010_004_t5_properties.py` (+738, −0). Ninguna ruta fuera de `tests/**`. `git status` conserva únicamente el untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md` (no mío, intacto).

## 6. Declaraciones

- **Sin lectura de implementación**: no abrí `skills/**` (salvo nombres y digests), `scripts/**`, `sources/**`, `agents/**` ni `build/**`; el módulo del CLI **no** se importó en ningún momento (solo subproceso, caja negra, incluido `render --route C`, `validate-*` y `--help`).
- **Sin tocar producto/CLI**: 0 ediciones fuera de `tests/**`.
- **Sin instalación global** (`~/.config/opencode`, `~/.agents`, `~/.claude` intactas), **sin publicar ni push**, **sin construir el consumidor instalado aislado** (es el E2E separado de T5).
- **Suite completa NO ejecutada** (la corre el responsable del cierre, según la política declarada en el paquete).

## 7. Límites honestos

- La propiedad acredita conducta del CLI sobre archivos publicados; **no** acredita recepción nativa del mensaje por un runtime ni obediencia de un modelo (§4.7).
- Coste declarado: ~0,35 s por invocación → 71,8 s la tanda focal (200 invocaciones del CLI). Se prefirió el mínimo contractual de 100 entradas por propiedad antes que ampliar el tiempo del gate.
- `ruff format --check` discreparía en este archivo, igual que en los tests existentes (`test_010_004_t3_red.py`, `test_role_packet_render.py`): el repo no lo exige; `ruff check` sí pasa.