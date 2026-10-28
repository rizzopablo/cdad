## Dictamen

**BLOCKING** para la implementación revisada: la frontera `cdad_delegate.py` directamente invocable todavía puede lanzar un worker con un paquete alterado. La revisión es parcial; no constituye aprobación.

### 1. BLOCKING — El transporte directo omite la admisión del paquete

**Verdict: BLOCKING · Bucket: h**

- **Evidencia:** `skills/cdad-cycle/scripts/cdad_delegate.py:549-574` resuelve el paquete, verifica la prueba de continuidad cuando corresponde y envía `packet_md.read_bytes()` al adaptador. No llama a `verify_published_packet`. La comprobación nueva está únicamente en `cdad_dispatch.py:542-548`.
- **Consecuencia:** después de un `begin` válido, una invocación directa de `cdad_delegate` puede lanzar el worker con un `PACKET.md` cuyo objetivo o instrucciones fueron alterados. La comprobación posterior de registro no evita ese lanzamiento. Esto contradice PC-01/PC-03 y la exigencia de que las CLI directamente invocables comprueben sus propias precondiciones antes de efectos nuevos.
- **Cierre verificable:** verificar el paquete en la propia frontera `delegate`, antes de leer los bytes y ejecutar el adaptador; agregar una prueba que invoque esa CLI directamente y demuestre que el paquete alterado no lanza el worker, con un control válido que sí lo lance.

### 2. IMPORTANT — `record` observa y crea staging temporal antes de verificar el paquete

**Verdict: BLOCKING · Bucket: h**

- **Evidencia:** `skills/cdad-cycle/scripts/cdad_dispatch.py:1072-1100` comprueba existencia y continuidad, pero no integridad, antes de `observe_model`. La verificación sucede más tarde, mediante `prepare --record-dispatch`; antes de invocarlo, `_register_attempt` crea y escribe `.observation.json` (`cdad_dispatch.py:971-989`) y luego lo elimina.
- **Consecuencia:** con un paquete alterado, `record` puede efectuar la observación y escribir staging temporal antes del rechazo, pese al orden explícito del contrato.
- **Cierre verificable:** aplicar la admisión en `record` antes de observar o preparar staging, conservando la precedencia de replay que corresponda; probar directamente `record` con paquete alterado y verificar que no se observa ni se escribe staging.

### 3. IMPORTANT — La falta de `REQUEST.json` permite un nuevo `begin` sin admisión

**Verdict: BLOCKING · Bucket: h**

- **Evidencia:** `skills/cdad-cycle/scripts/cdad_continuity.py:1217-1222` devuelve `None` si falta el request publicado; el llamador en `:1110-1113` continúa sin verificar paquete ni referencias. Los tests PC-01 eliminan `PACKET.md`, pero no `REQUEST.json`.
- **Consecuencia:** la ausencia del request se interpreta como continuidad legacy, incluso para un identificador que pretende una encomienda CDAD. Un nuevo `begin` puede persistirse sin paquete verificable, escapando también de PC-06.
- **Cierre verificable:** distinguir con evidencia de contexto una operación legacy legítima de una encomienda CDAD cuyo request falta; rechazar esta última antes de persistir. Añadir un caso de request ausente y conservar controles de continuidad legacy.

## Verificación y límites

- El SHA-256 de la spec coincide con el paquete recibido. **No obstante, el archivo indica `Status: Draft` en `spec.md:3`**, mientras el paquete la identifica como contrato aprobado. El orquestador debe resolver esa discrepancia (ya corregida tras el dictamen).
- La comparación implementada en `cdad_packet.py:1869-1978` compara desde el marcador hasta el final contra `render_packet`, excluye el preámbulo y contiene rechazos explícitos para marcadores ausentes, múltiples o sin cierre.
- Los controles y replays inspeccionados realizan aserciones observables; no dependen únicamente de declaraciones textuales.
- La validación bajo `prepare --record-dispatch` precede al registro durable; la regla PC-06 usa `_scope_contains` antes de persistir y conserva `living` en los casos ejercitados.
- No se modificaron archivos. Commits inspeccionados: `126d68b`, `f10aeaa`.

**Comandos y resultados:**

```text
sha256sum docs/specs/008-004-role-packet-enforcement/spec.md
91622ff87d8cd972dc7fe008b52ddc399bac4c0df5473b59f1bf00428e106558
```

```text
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_008_004_packet_enforcement.py tests/test_003_004_t*.py tests/test_003_007_t*.py < /dev/null
85 passed in 73.14s
```

## Abstentions

- No verifiqué exhaustivamente PC-02, PC-04, PC-05 ni PC-08 en las definiciones de roles, adaptadores generados e instalación.
- Los 85 tests seleccionados no descartan todas las regresiones de continuidad legacy ni sustituyen la suite de cierre.
- No reproduje mediante una prueba nueva los tres escapes señalados; los hallazgos se basan en el flujo de código y las precondiciones visibles citadas.
