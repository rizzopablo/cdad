# Review — T2 (003-002): materialización por política de artefactos

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-38>`.
> Paquete: `003-002-artifact-tools-reviewer-review-003`. Objeto: diff
> `0494ab5..db72fb4` contra `spec.md` §7 (P4 + partes de P3/P6).
> **Dictamen: 5 BLOCKING (R1–R5) + O1–O3 opcionales + 2 FYI.**

**Contrato:** `sha256sum …/spec.md` → `ba73e645…f37` = el del paquete ✓ · **Diff:** 5 archivos, +350/−5.

## Evidencia ejecutada por el reviewer

| # | Comando | Resultado |
|---|---|---|
| E1 | `sha256sum spec.md` | coincide ✓ |
| E2 | `git diff --stat 0494ab5..db72fb4` | 5 files, +350/−5 |
| E3 | `unittest discover -p "test_003_002_t2_materialize.py"` | **11 OK** |
| E4 | `unittest discover -p "test_003_002_t1*.py"` | **14 OK** |
| E5 | Sonda adversarial `/tmp/opencode/review_t2_escape_repro.py` | **[A] delegación revocada post-receipt → `materialize` rc=0 (aplicó la copia)** · [B1] kind fuera de tabla → rc=2 con diagnóstico ✓ |
| E6 | grep estático | `receipt["role"]`/`substage`: **0 referencias**; la clave `test-writer-audit` de la política no se usa en ningún lado |

**Suite completa:** citada del implementer (389 passed / 773 s), **no verificada** por el reviewer (el proceso murió con la sesión).

## Hallazgos

### R1 — La vigencia de la autoridad no se aplica (escape empírico) · BLOCKING · bucket m

Spec §5: "La autoridad vencida impide nuevas recepciones y **materializaciones**". `materialize` nunca lee el estado ni invoca `validate-state`; su binding es igualdad de *string* `authorization.authority_ref == execution.authority_ref`. La delegación vive en `state.hitl_delegation` (`status`, vigencia) — exactamente lo que `validate_state` convalida y lo que T1 corre vía `validate_request`. §9 prohíbe **escribir** el estado; leerlo está permitido.
**Prueba E5-[A]:** con `hitl_delegation.status = "user-revoked"`, `materialize` → **rc=0, copia aplicada**.
**Remedio:** en el pre-flight, leer el estado y validar la delegación activa/vigente reutilizando el bloque de `validate_state`; rechazar con diagnóstico nombrado.

### R2 — La tabla cerrada no coincide con la spec nombre por nombre · BLOCKING · bucket m

`artifact-policy.json` define `test-writer-audit` **además** de `test-audit`; la spec §7 tiene **una** fila de auditoría. Se admite un kind que la tabla aprobada no nombra (sin ganancia de privilegio, pero la tabla es un control declarado y se ensancha en silencio).
**Remedio:** eliminar la clave, o enmienda de spec que fije la nomenclatura.

### R3 — El cierre rol↔kind no se aplica · BLOCKING · bucket m

Spec §7: "El rol/subfase y el artifact_kind usan una tabla cerrada; **un kind de otro rol falla**". La implementación indexa solo por kind; `materialize` no consulta `receipt.role`/`substage` (E6: 0 referencias). Un part etiquetado con el kind de otro rol se materializa si el kind está en la tabla.
**Remedio:** mapa cerrado `receipt.role(+substage) → kinds permitidos` en el pre-flight.

### R4 — El paquete RED no observa el journal · BLOCKING · bucket m

El fixture del retry multi-copy pre-escribe el contenido del target **pero nunca crea journal**: el "retry continúa desde el journal" queda cubierto por accidente vía la rama contenido-idéntico-sin-journal. La rama "journal con target divergido → rehusarse" (§7: "nunca repite ni sobrescribe un efecto divergente") queda **sin test**, y no hay kill en el límite observable para materialize.
**Remedio:** fixture con journal real (corrida previa truncada o pending-dir documentado §8) + negativo journal-divergente + kill.

### R5 — Filas de la matriz §7 sin cobertura · BLOCKING · bucket m

Sin tests: kinds del scribe (los únicos cuya raíz permitida es un **archivo**), `review`/`plan-review` (roles read-only), `test-audit` con target fijo, **CAS de Memory Bank** end-to-end, `approval_effect=true` rechazado, part con kind fuera de tabla. El comportamiento se ve correcto por lectura, pero "P4 completo" no es verdad observable.

## Opcionales / FYI

- **O1 (m):** para las filas con target fijo (`test-audit.md`, role-reports), la herramienta admite cualquier path bajo la raíz del kind.
- **O2 (l):** el journal indexa por el string crudo del target, no por path normalizado (§2 exige normalizados).
- **O3 (m):** `materialize.schema.json` no se carga: es documentación paralela sin test cruzado.
- **F1 (h):** el `plan.md` tiene frontmatter `approved` y un `> Estado: borrador` en el cuerpo (residuo del replan; el orquestador lo corrigió al aprobar).
- **F2 (m):** `M docs/.cdad-state.json` = binding del paquete (orquestador); ninguna escritura del reviewer.

## Verificado positivo

Escritura atómica por copia (temp + `os.replace` + fsync); pre-flight completo **antes de la primera escritura**; create-only estricto + caso idempotente; CAS solo contra digest exacto con conflicto sin overwrite (positivo y negativo); binding receipt/execution/packet/authority_ref; `approval_effect` ≠ false rechazado; state/receipt/context intactos; stdout vacío en fallo; escape de root rechazado (traversal, mixto, absoluto); kind ausente de tabla rechazado (E5-[B1]).

## Abstenciones

1. Suite completa citada, no medida (murió con el background de la sesión).
2. Concurrencia de dos `materialize` simultáneos sobre el mismo journal: §7 no la especifica; solo lectura de código.
3. Semántica exacta de vigencia en el runtime v2 real: el remedio de R1 debe reconciliarse con el contrato exacto de `validate_state` (abstención de detalle, no del hallazgo — R1 está reproducido).
4. Smoke instalado: alcance de T4.
5. Observación de dispatch I8 del paquete GREEN: obra del orquestador.

## Dictamen

**5 Requeridos.** El núcleo mecánico es fiel en lo testeado, pero R1 es un escape de contrato con relevancia de seguridad (autoridad revocada no bloquea materialización, **reproducido**), R2/R3 son divergencias literales de la tabla cerrada, y R4/R5 son brechas entre lo declarado ("P4 completo") y lo observado. R1–R3 → review-fix del implementer; R4–R5 → RED del test-writer.
