# Review 1 — 003-005 (cdad-reviewer, Claude)

Veredicto: **CAMBIOS-REQUERIDOS**. 3 bloqueantes, 5 opcionales, 2 abstenciones.

- [Critical] Si el packet_id choca, el rollback (`rmtree` sin condición) borra el directorio de otro proceso.
- [Critical] Si el state no se puede serializar (surrogate suelto), sale con traceback y rc=1, y deja el directorio del paquete y `.cdad-state.json.tmp`.
- [Required] Un `feature_id` no plano (`/tmp/x`) hace escribir el paquete fuera de `--out-dir`.
- Opcionales: `--out-dir` libre es advisory (lo elige un llamador confiable); `.cdad/packets` queda creado si falla después;
  los errores de argparse no llevan el prefijo `ERROR:`; hay una línea larga en el orquestador de Claude Code; diferencia de redacción con OpenCode (justificada).
- Confirmado: `prepare` usa el mismo `validate_request` que `render`; el template de execution.json funciona en modo ordinary
  (fixture: prepare → render → validate-packet OK); los agentes tienen el mismo contrato que OpenCode, conservan hooks y skills odoo; no hay scope creep hacia 002.

RED correctivo (test-writer): 4 tests nuevos en P4. Fallan 3: carrera B1 con inyección en `os.mkdir` vía sitecustomize,
B2 y B3 absoluto. Pasan 2 sin fix: symlink colgante B1 y B3 `a/../b`.
Spec enmendado en §3.
