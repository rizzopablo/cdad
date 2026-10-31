# Plan v2 — materialización, no aprobación

Fuente: FINAL TEXT de architect `<session>`, mensaje `msg_18d436268001DndB1NM4FQf8Uv`, recuperado íntegro mediante `session.messages`. Materialización textual autorizada ADR-003 mediante `functions.patch`, sin exportación SQLite. Original preservado en `architect-plan-v2-original.md`: 19883 bytes UTF-8, SHA-256 `970063cd77d6427021665601a4e29b8b36108611a0a68e2fbc7ab8e7efff0b9b`; sin LF terminal, como el campo text recuperado.

Packet `010-004-packet-dispatch-ergonomics-architect-draft-006`, ejecución `exec-010-004-packet-dispatch-ergonomics-001`, continuidad attempt entero 13. `record` devolvió `delivery: staged`; `receive` y `validate-receipt` rc=0. Receipt `.cdad/runtime/results/exec-010-004-packet-dispatch-ergonomics-001/010-004-packet-dispatch-ergonomics-architect-draft-006/receipt.json`, SHA-256 `da063c58e7f41511a39f1f88fe1d3c8f512d925c74d0af2cfa115ec694465eed`, `semantic_status: pending`. La recepción cerró continuidad 13; no se creó begin 14.

El diff se extrajo literalmente del original y se reconstruyó en memoria verificando cada línea de contexto sobre la base CAS `9deee470f708a26d3e9418fcf0df5710693a510e7557d8e289494bcc349edd23`. Resultado exacto `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685`, 15577 bytes; `git apply --check` y `git apply` rc=0. No hubo mismatch del resultado ni edición de contenido por el orquestador. La spec permanece `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`.

Transición delivery `cfc71792f0c64bdcbb9085fd3b26268aa46b043079a9601cfe741fe483e5da84`: original y plan registrados. No cambia la etapa specification ni aprueba el plan. Próximo paso: revisión independiente acotada del PLAN v2, no revisión de la spec.

Límites reales: la correlación nativa no pudo acreditar parent/moment; record lo declaró y recibió los bytes bajo garantía reducida PD-6/INV-2, sin inventar identidad acreditada. La plantilla POST-AUDIT vigente combina subfases; el plan exige resolver esa contradicción antes de despachar, sin parchear paquetes. El reviewer debe juzgar ese procedimiento y señalar cualquier defecto real, sin autorizar bypass ni exigir producto extra no aprobado. La aprobación del plan sigue siendo decisión separada de Pablo.

Incidencias mecánicas sin efecto de producto: primer patch rechazado por faltar encabezado Begin Patch; corregido. Consulta verify-begin con flag incorrecto devolvió rc=2; record verificó internamente el begin vigente de attempt 13 antes de registrar. El dispatch histórico no se repitió.

No se ejecutaron tests, implementación, suite, generación, instalación ni push. El untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md` no se alteró ni se incluye en el commit.
