## Cierre del encargo — RED T4 (005-003, etapa 3, subetapa `red`)

**Rol:** test-writer · **Producto:** oráculo documental de T4 (ciclo sin código) · **Sin leer implementación.**

### (1) Archivo de tests

- `tests/test_005_003_t4_capabilities_inventory.py` (nuevo, 305 líneas)
- sha256: `d26fe7c8c6cd51e15a5fe5457aeb41c90141fd2df9c8533092caaa058f639864`

Localiza el producto por su **ruta declarada en runtime** (`skills/cdad-cycle/references/capabilities.md`) y **no lo crea** (eso es el GREEN). No importa código de producto; solo stdlib + pytest.

### (2) Mapeo test → PD-9 / INV

| Test | Postcondición / invariante |
|---|---|
| `test_pd9_inventory_exists_and_is_non_empty` | PD-9 (i): el inventario existe en su ruta declarada y no está vacío |
| `test_pd9_inventory_declares_four_classes_with_criterion` | PD-9 / §2.7: declara las cuatro clases (observada/documentada/no disponible/desconocida) + una capacidad por clase **o** el criterio que la asigna |
| `test_pd9_inventory_declares_surfaces_and_version_link` | PD-9 / §2.7: nombra planes, archivos, previews y diffs; ligado a versión/configuración |
| `test_pd9_inventory_declares_portable_fallback_and_file_link_path` | PD-9 / §2.7: fallback portable por archivos o enlaces + camino agente → artefacto → revisión |
| `test_pd9_inventory_does_not_promise_openchamber_agent_surface_contract` | PD-9 / §2.7 + §7: toda mención de «contrato estable agente↔superficie»/«API de UI» está negada (no se promete lo no verificado) |
| `test_inv6_inventory_carries_no_this_vps_values` | INV-6 (y frontera INV-7/§7): sin rutas absolutas del host, proveedor/modelo concreto, servidor ni ids crudos de sesión |

Antes de commitear verifiqué el oráculo en dos sentidos (fuera del repo, con un documento sintético): un documento plausible **pasa** los seis checks; un documento con promesa sin negar, ruta `/home/…`, proveedor/modelo y IP **falla** — no es vacuo.

### (3) Focal (RED)

```
$ python3 -m pytest tests/test_005_003_t4_capabilities_inventory.py -q
...
FAILED ...::test_pd9_inventory_exists_and_is_non_empty
FAILED ...::test_pd9_inventory_declares_four_classes_with_criterion
FAILED ...::test_pd9_inventory_declares_surfaces_and_version_link
FAILED ...::test_pd9_inventory_declares_portable_fallback_and_file_link_path
FAILED ...::test_pd9_inventory_does_not_promise_openchamber_agent_surface_contract
FAILED ...::test_inv6_inventory_carries_no_this_vps_values
6 failed in 0.09s
```

Las seis fallan por **`AssertionError`** de contrato (`_load_doc` afirma `DOC.is_file()`; el documento no existe todavía) — no por `FileNotFoundError`, `ImportError` ni `SyntaxError`. No corrí la suite completa.

### (4) Commit

- `afd7fd4b7bb427d9363ee604181bdbc809d755eb` — `test(005-003): RED T4 - inventario de capacidades y fallback portable`
- `git show --stat`: **1 file changed** (solo el test). `docs/.cdad-state.json` quedó modificado por el orquestador y **no** lo commiteé.

### (5) Bordes sin cubrir y por qué

1. **Existencia real de la capacidad:** el test afirma que la **clase está declarada**, no que la capacidad exista (por instrucción del encargo). La veracidad de cada clasificación se liga a versión/configuración y se comprueba en operación, no con un oráculo documental.
2. **«Demostración» vs «declaración» del camino:** el test afirma que el camino agente → artefacto → revisión por archivos/enlaces está **declarado con sus elementos**; no ejecuta el fallback (ciclo sin código: no hay artefacto ejecutable). La demostración es la cadena documentada.
3. **INV-7 negativo (sin dashboard/scheduler/fuente de estado nueva):** no se afirma por prosa (degeneraría en grep de frases). Se cubre **por construcción**: el producto de T4 es un documento, el test solo lee y no importa código; no hay camino de producto que cree fuente de estado.
4. **Privacidad heurística:** el denylist de proveedor/modelo es una lista genérica curada y los prefijos de ruta absoluta son los habituales; un nombre fuera de la lista o un prefijo de montaje inusual no se detectarían. Es un heurístico, declarado, no exhaustivo.
5. **Rama OR de las clases:** el test satisface «capacidad por clase **o** criterio» con **cualquiera** de las dos, tal como fija §2.7/el encargo; no exige ambas.
6. **Longitud «corta» del inventario:** no se afirma — PD-9 no fija una cota de tamaño.

Sin desviaciones: no leí implementación, no escribí fuera de `tests/**`, no toqué HOME, no leí `tests/.sensitive-patterns.local`, no hice push.