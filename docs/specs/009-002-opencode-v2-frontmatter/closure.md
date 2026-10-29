# Cierre — 009-002: frontmatter V2 nativo de OpenCode

Fecha de cierre: 2026-10-29 UTC (2026-10-28, UTC−03). Mandato: completar el fix light sin mezclar documentación general ni eficiencia de ejecución.

## Resultado

Los 11 agentes OpenCode distribuidos y los agentes derivados por proyecto emiten `permissions:` como lista V2. Se conservan reglas, recursos, efectos y orden; el reviewer usa `request.body.temperature`; Claude Code queda intacto. No se distribuyen modelos: el `model:` sigue perteneciendo al usuario.

El cambio está verificado en OpenCode 2.2.0 real, en una arena aislada de configuración: reconoce modelo y variante en los 11 agentes. Una actualización desde V1 conservó los modelos y dejó `install.sh --check` verde. No se modificó el HOME del operador ni se ejecutaron sesiones LLM para esa comprobación.

## Contrato y evidencia

Contrato aprobado: `spec.md`, SHA-256 `c62c9e7c8ea8c3600d24024957616a8c4b6d4fae69641469b32945293131d605`.

| PC | Evidencia y resultado |
|---|---|
| PC-1: forma V2 válida | `test_009_002_opencode_v2_frontmatter.py`; revisiones de todos los agentes comprometidos y staging. `agents/*.md` es la ruta real del repositorio; `agents/opencode` en la spec era un error de ubicación, no una segunda salida. |
| PC-2: mismas reglas y orden | Comparación de los 11 agentes con `9fc90b1`, tabla de oro y mutaciones PD-10 m1–m8: 16 tests pasan y cada alteración debe ser detectada. |
| PC-3: temperatura sólo reviewer | Generador y runtime confirman `request.body.temperature: 0.1` sólo en reviewers emitidos. |
| PC-4: orquestador válido y permisivo | YAML válido, `mode: all`, regla V2 catch-all con comodines entre comillas; runtime verificado. |
| PC-5: Claude Code intacto | `git diff 9fc90b1..1772563 -- agents/claude-code` vacío. |
| PC-6: generación idempotente e instalación verificable | Dos ejecuciones de `make agents` con bytes idénticos; arena externa: instalación y actualización preservando modelo, `--check` rc 0 (414 grupos). |
| PC-7: ruta legacy coherente | `apply_bash_block` y sus insumos retirados con motivo en `install.sh`; check compara artefactos emitidos más overlay, sin regenerarlos. |

También se migró `_rewrite_derived_agent`: ya no mezcla una lista V2 con mapas V1, conserva el cuerpo y las reglas no propias, aplica las barreras por proyecto y retira `write` antiguo. Los oráculos comprueban privacidad, temporales y permisos efectivos, no sólo palabras presentes.

## Gate final

`cdad-ci-gate.py --base 9fc90b1 --evidence-root .cdad/local/009-002/gate-final`, sobre `1772563e16ae1fc346d9c8120e68713d4a6cb68a`.

- **GREEN**, salida 0; atribución verdadera, un intento terminado, árbol limpio y resumen verificado.
- **1844 passed, 0 failed, 5 skipped, 0 errors**. Las cinco integraciones opt-in conservan sus motivos; omisión no significa pase de esas integraciones.
- Superficie: 1849 nodeids, paso collect-only rc 0. Inventario y helper nuevo clasificados para esta unidad.
- Canario: delta 0. Carga registrada: 5.00 / 5.18 / 5.18.
- Evidencia: `.cdad/local/009-002/gate-final/gate-20261029T011218177492Z-2292973-b28d0e32/gate.json` y logs del intento asociado.
- Validación de instalación independiente en arena externa: `make validate` rc 0, 68/68; `install.sh --check` rc 0, 414 grupos. Logs: `.cdad/local/009-002/{validate-final,install-check-final}.log`.

Después de este gate sólo se materializan documentos y el cierre del estado; no se cambia producto ni tests.

## Review y contrafactual

`review.md`, `review-2.md`, `review-final.md`, `review-gatefix.md` y `review-gatefix-final.md` conservan el historial. Los bloqueantes B1/B1-r/O2 y el control `write` V2 quedaron cerrados por sesiones de reviewer independientes de los implementers.

La primera corrida completa sobre `269d92f` fue **RED**, 1842 passed / 2 failed / 5 skipped: dos oráculos todavía esperaban V1. Se corrigieron sin tocar producto (`937bad1`, `21bd4fb`), con controles negativos que detectan permisos alterados y diferencias fuera de la raíz temporal. La revisión final focal dio 11 passed. No se promediaron intentos ni se ocultó el primer rojo; el gate verde corresponde al commit corregido.

## Límites y deuda explícita

- La premisa inicial «todo V1 ignora `model:`» no quedó demostrada universalmente: el reviewer observó un V1 de proyecto que sí resolvía modelo. Lo acreditado es compatibilidad V2 y actualización conservadora en el runtime probado.
- O1: el inventario histórico aún tiene módulos de 008-002…008-005 y 009-001 sin clasificar. Se agregó el helper V2, sus consumidores y las tres pruebas 009-002; `surface` pasa. No se declara que `cdad-suite.py validate` global esté limpio.
- O3: derivar directamente desde una fuente V1 antigua puede conservar `temperature`/`edit` top-level hasta reinstalar los agentes; el emisor estático V2 sí los ubica correctamente.
- El overlay 009-001 preserva `model:`; no promete preservar una clave independiente `variant:` ni YAML arbitrario. El modelo con variante incorporada se verificó en el runtime.
- El HOME real puede mantener conflictos por modificaciones fuera del overlay. El instalador los preserva; esta entrega no los borra ni los convierte silenciosamente.
- Documentación pública general, selección/ejecución eficiente y cotas justificadas quedan fuera de este fix, para planificación posterior.

## Cierre operativo

Sin ADR nueva: cambia la representación, no la política. Memory Bank actualizado a partir del borrador del scribe y la evidencia final. No implica push ni instalación sobre otros entornos: ambos requieren instrucción del dueño.
