### Spec draft — `docs/specs/018-001-orchestrator-start/spec.md` (borrador, sin aprobación)

**Promesas y postcondiciones (agrupadas por promesa observable):**

- **Promesa A — La entrada indica cómo avanzar sin reconstruir el sistema**
  - PC-1: fuentes del orquestador, ambos generados y skill dejan de exigir/prohibir simultáneamente la carga completa; entrada compacta y excepciones diferenciadas.
  - PC-2: procedimiento distingue sesión nueva, reposo y continuación tras `open-unit`; no prescribe `resume` por transición interna ni apertura por consulta.
- **Promesa B — Las interfaces ordinarias se usan sin leer implementación**
  - PC-3: ayudas explican los dos formatos de `--input`, archivo JSON de `--update`, contexto requerido de `resume`, opciones incompatibles de reemplazo.
  - PC-4: negativos comprometidos (entrada sin propósito, contexto omitido, actualización literal/Markdown, reemplazo mezclado) fallan con código aplicable, diagnóstico accionable y sin publicar efectos.
- **Promesa C — Los ejemplos llevan a un encargo válido**
  - PC-5: ejemplos del asset se ejecutan sobre fixtures autocontenidos; cubren formatos y secuencia nativa vigente (`verify-begin`, conservación del entero de continuidad).
  - PC-6: procedimiento transmite todos los requisitos del caso mediante campos existentes; C y A mantienen contrato; ausencia de autoridad no se resuelve inventándola.
- **Promesa D — La evidencia permite confiar en el resultado observado**
  - PC-7: patrón de captura conserva salida completa y retorno del CLI incluso ante fallo con `set -e`; payload renderizado mantiene bytes.
  - PC-8: generación determinista y coincide con salidas publicadas; verificaciones doctrinales conservan límites de roles/autoridad/orientación.
  - PC-9: ensayo real entrega registro comparable de llamadas, lecturas, contexto y tiempos, con cobertura y limitaciones explícitas.

**Invariantes:** no nuevos estados, gates, aprobaciones, macros ni executor. `status.next.operation` no concede autoridad. Se conservan ADR-003, ADR-011, ADR-032 y ADR-033.

**Caso de aceptación sintético (R1–R5) con sensibilidad R3:** architect/discovery sobre exportación CSV — columnas `id`, `fecha_utc`, `total` UTF-8 y orden dado; UTC y representación decimal del diccionario; excluir nombres y correos; orden estable por fecha e identificador; informar datos inválidos sin descarte silencioso. Verificador acepta encargo completo y rechaza la variante que omite R3, con oráculo intacto, sin autorización ni despacho real. Conservar `PIPESTATUS[0]` como alternativa documentada a la captura completa sin tubería.

**deferred-hardening:** control automático de lecturas/cumplimiento del modelo (fuera de alcance, exigiría otro mecanismo); benchmarks estadísticos y atribución causal (diferidos); ayudas exhaustivas para todo el CLI (limitado a operaciones implicadas); rediseño del historial/medidor/instalación (no necesario); transporte externo completo (conservado por regresión).


Status: Approved by Pablo on 2026-11-13
