# Revisión de cierre T2 — 019-004

**Resultado: los dos hallazgos anteriores no están completamente cerrados.** La clasificación del destino concreto está implementada y tiene evidencia focal positiva. La resolución ambigua es estricta en los cuatro comandos operativos probados, pero las excepciones registradas para continuity y gap-report contradicen el contrato aprobado.

No apruebo la feature ni modifiqué archivos.

## Hallazgos

### 1. Continuity permite operaciones con un layout ambiguo

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

`skills/cdad-cycle/scripts/cdad_layout.py`, `optional_methodology_base()`, devuelve `None` tanto para un proyecto sin inicializar como para uno con evidencia insuficiente. `cdad_continuity.py` interpreta ese resultado como ausencia de estado y política; según `decisions.md`, permite que `begin`, `checkpoint` y `reconcile` continúen sobre registros `.cdad/`.

Esto evita seleccionar silenciosamente `docs/`, pero no satisface la otra mitad de PC-04 y §4.2: **un layout ambiguo debe diagnosticarse y fallar sin modificación**. La excepción registrada no modifica por sí sola el contrato aprobado.

**Consecuencia:** una operación de continuity puede avanzar y producir efectos operativos en un proyecto cuya ubicación metodológica requiere aclaración.

**Cierre verificable:** distinguir ambigüedad de ausencia genuina de layout y rechazar las operaciones afectadas antes de escribir, con pruebas de diagnóstico y árbol sin cambios; o elevar explícitamente la contradicción para una decisión sobre el contrato.

### 2. Gap-report vuelve a seleccionar `docs/` sin un marcador legacy

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

En `skills/cdad-cycle/scripts/cdad_contract_links.py`, `cmd_gap_report()` usa `registered_methodology_dir(root) or LEGACY_DIR`. Por tanto, si solo existe `docs/specs/` y no hay locator ni marcador legacy, busca especificaciones bajo `docs/`.

Que el informe sea de solo lectura limita el efecto —no escribe allí—, pero no elimina la contradicción: §4.2 prohíbe seleccionar legacy ante esa evidencia y PC-05 exige que la búsqueda convencional use el directorio seleccionado. El informe puede atribuir contratos a una ubicación no admitida.

**Cierre verificable:** resolver el layout con las mismas reglas antes de la búsqueda convencional y demostrar rechazo ante ambigüedad, además de conservar controles registrado y legacy válido; o resolver expresamente el conflicto con el contrato aprobado.

## Cierre de los hallazgos anteriores y límites de las decisiones

- **Destino concreto y protección privada:** cerrado para el caso alcanzable ejercitado. `check_materialization_destination()` clasifica cada destino y comprueba privacidad antes de agregarlo al plan de materialización. El test focal verifica rechazo sin cambios en los artefactos y éxito de un destino vecino compatible.
- **Consumidores operativos ambiguos:** cierre **parcial**. Los tests de `validate-state`, `status`, `open-unit` y `prepare` acreditan rechazo sin escritura para las señales ejercitadas; no cierran las excepciones de continuity y gap-report descritas arriba.
- **Propose-policy:** la excepción registrada es razonable dentro del alcance revisado: ante ambigüedad no añade una raíz metodológica inventada; sigue incluyendo `docs` si existe como documentación ordinaria.
- **Política legacy que no clasifica `docs/` como documentación:** su rechazo operacional es compatible con §4.4 y PC-06. Reconocer un marcador legacy selecciona la ubicación, pero no exime de validar la política efectiva.

## Evidencia

- Validación Route C: ejecuté `cdad_packet.py validate-packet` con el request, contexto y `PACKET.md` declarados; **salida vacía y código 0**.
- Pruebas:  
  `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_019_004_lifecycle_layout.py tests/test_019_004_layout.py`  
  **Resultado:** `41 passed in 67.80s`.
- Diff del fix revisado: `git diff fc44cdf3 415f9562`; cinco archivos modificados: `cdad_continuity.py`, `cdad_contract_links.py`, `cdad_layout.py`, `cdad_packet.py` y `cdad_result.py`.
- Commit del fix: `415f9562`; decisiones posteriores examinadas en `0560a224`. No creé commits. `docs/.cdad-state.json` aparecía modificado previamente en el árbol.
- No ejecuté la suite completa; la evidencia independiente se limita a la selección indicada.

## Abstentions

- No acredito exhaustivamente todos los consumidores del layout ni todos los caminos de materialización: la selección ejecutada no los demuestra.
- No acredito la reconciliación completa de la tabla de decisiones vigentes con todos los ADR.
- No evalúo el cierre integral de las promesas de intake e instrucciones instaladas como parte de este re-review focal.