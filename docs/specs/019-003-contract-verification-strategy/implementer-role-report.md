## Informe del implementer — 019-003 (GREEN, instrucciones canónicas)

**Resultado:** cambio de instrucciones aplicado y commiteado en dos commits del repo interno. **No es aceptación semántica:** eso corresponde al revisor independiente. Ningún test fue editado.

### Riesgo principal: el recibo de este resultado puede rechazarse
`re-entry.md` ("Compatibility between product revisions") dice que un paquete publicado con fuentes de instrucción cambiadas se rechaza al recibirlo. Cambié `packets/roles/implementer.md`, `packets/substages/implementer-green.md`, `reviewer-plan-review.md` y `architect-draft.md`, así que el orquestador puede recibir un rechazo. Según la regla documentada, las salidas son terminar bajo la revisión con la que se publicó o preparar un paquete nuevo bajo la revisión vigente. No intenté ningún rodeo.

Corrijo una afirmación previa: `validate-packet` **sigue pasando** tras los cambios, porque el render usa los snapshots embebidos en REQUEST.json. Verifiqué que el render sigue siendo byte a byte igual al PACKET.md.

### Validación de entrada (antes de editar)
- Identificación ruta C: `render --route C` coincide exactamente con el bloque del despacho. El hash del contrato (`969ff8e5…`) coincide.
- `validate-state`, `validate-request`, `validate-packet`, `validate-policy`: los cuatro rc=0.
- Render completo: byte a byte igual al PACKET.md.

### Commits (repo interno `cdad/cdad`)
- `5547c14a` — núcleo: stage-2 (verificación por promesa, chequeo de suficiencia, exención declarada como no-revisión), stage-3 (enrutamiento por método: ejecutable / semántico-solo / mixto; aceptación fijada antes de producir; R7 reconciliada), stage-4 (categorías de cierre de evidencia), plantilla de spec, packets, handoff, re-entry, roles y SKILL ligero.
- `2b801316` — hermanos: `reviewer-plan-review` y fuente del revisor (chequeo de suficiencia), `architect-draft`, re-entry (checklist de borrador y de revisión; los cuatro campos de exención intactos), SKILL de `cdad-cycle` y `cdad-spec-and-test`.
- Ambos commits incluyen `agents/` regenerados con `make agents`. No se stageó `docs/.cdad-state.json` (ya estaba modificado antes de empezar). El alcance de lo staged se verificó contra `agents|skills|scripts|sources|build|install.sh`: ninguno fuera de alcance.

### Evidencia de pruebas (sin suite completa)
- **Selección nombrada** (7 archivos: `test_role_packet_render`, `test_cdad_generate`, `test_010_001/002/003`, `test_install_ownership`, `test_004_002_t6_landing`): **94/94 antes y después**.
- **Selección amplia** (57 archivos que citan estos documentos): **504 passed, 2 failed**. Los dos fallos son `test_005_006_t6_owner_reviewfix::test_hallazgo_a1_no_install_root_in_wiring` y `…a2_cli_invocations_derived_from_skill_dir`. Ambos fallan también en la base previa `0b11b5fb`, medido en un worktree aislado que luego eliminé. Los dos solo inspeccionan `README.md`, que no cambié. La línea base de la selección amplia completa antes de editar no llegó a completarse (excedió el tiempo), así que la atribución se midió solo para estos dos tests.
- **Chequeo de doctrina:** OK (22/22 artefactos generados presentes).
- **Generador:** determinista (dos corridas consecutivas, sin diferencias).
- **`make validate`:** 182 pasan, 1 falla. El fallo es F011 (`validate-subagents.sh`), causado por drift de instalación preexistente: la copia instalada `~/.config/opencode/agents/cdad-architect.md` (sha `d0295cca…`) no coincide con el HEAD (`02052e45…`). No instalé ni desplegué nada.
- **Suite completa:** no realizada. El paquete la excluye. Limitación: la selección amplia es un subconjunto de los tests que citan estos documentos, no una cobertura completa.

### Lo que no hice (límites)
- Los consumidores de dominio Odoo (`skills/odoo-architect`, `skills/odoo-reviewer`) no los revisé en detalle; un grep de las frases cambiadas no encontró repeticiones incondicionales, pero no es una lectura completa.
- No se actualizaron las copias instaladas en `$HOME` (el paquete prohíbe instalar o desplegar).
- `handoff-prompts.md`, sección "Reviewer (plan-review)": es un puntero a `reviewer-plan-review.md`, así que el cambio llega por la fuente, no por el handoff.
- Ninguna afirmación de aceptación semántica: los PC-1..PC-6 requieren la revisión contextual independiente.

Evidencia en `/tmp/cdad-impl-validate/` (salidas de validadores, líneas base, logs de pytest).