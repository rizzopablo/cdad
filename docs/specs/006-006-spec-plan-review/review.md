# Review — 006-006-spec-plan-review

**Veredicto: apta para cierre.** No encontré bloqueantes observables. Quedan dos opcionales; este dictamen no aprueba la feature ni sustituye las verificaciones del cierre.

Revisión sobre `0192a95d631c2b74475530ddb2e6f3ba11854731`, con el diff solicitado. Verifiqué los hashes del contrato, política y tres fuentes del paquete: coinciden.

## B — Bloqueantes

Ninguno.

## O — Opcionales / deuda

### O-1 — Automatizar la selección de vigencia exigida por B-5

**Verdict: OPTIONAL · Bucket: h**

**Ubicación:** `tests/test_006_006_u5_exemption_record.py:1237-1247` y `:1331-1337`.  
**Contrato:** `docs/specs/006-006-spec-plan-review/plan.md:391`, errata B-5; PD-9.

Los tests comprueban que `prepare` acepta el contrato, pero eso no demuestra que el selector devuelva **solo B y después solo C**, excluyendo las entradas sustituidas: todas comparten pin.

Lo comprobé independientemente usando las transiciones reales y `_approved_spec_entries`:

```text
after A->B: selected_only_B= True excludes_A= True
withdrawal_rc= 0 selected_only_C= True excludes_A_and_B= True
```

No observé un defecto de vigencia; falta conservar esta comprobación como regresión automática. **Remedio:** añadir las aserciones del selector al recorrido, manteniendo `prepare` como comprobación adicional de habilitación.

### O-2 — Actualizar la evidencia de aceptación después de W-1

**Verdict: OPTIONAL · Bucket: h**

**Ubicación:** `docs/specs/006-006-spec-plan-review/u6-acceptance.md:12,16,22`.  
**Escenarios:** E4 y PD-9/PD-13.

El documento todavía presenta el rodeo previo y W-1 como «RED/GREEN en curso». Además, remite a los tests para U5 sin adjuntar las salidas detalladas previstas por el plan.

La evidencia posterior permite localizar la corrección, por lo que no lo considero bloqueo funcional. **Remedio:** enlazar el GREEN definitivo, actualizar el estado de W-1 e incorporar las salidas de los recorridos, incluida la selección B/C.

## Traza de escenarios

| Escenario | Resultado de la revisión |
|---|---|
| **E1 — spec sin plan** | La forma `spec` evita exclusivamente los checks de plan. El paquete conserva digest, forma y propósito; la recepción/materialización está documentada en U6. |
| **E2 — spec + plan** | Principal y acompañante quedan fijados por digest. Los checks estructurales se aplican al plan. |
| **E3 — otra feature** | El objeto y la feature activa permanecen distinguibles. El destino sigue restringido a la carpeta de la feature activa. |
| **E4 — corrección y re-review** | W-1 conserva forma, rutas y versiones; recalcula los digests, incluida la deriva del acompañante. El sucesor vuelve a validarse antes de publicarse. |
| **E5 — sin aprobación implícita** | No encontré una vía nueva de aprobación: W-1 conserva `draft-plan`, no añade aprobaciones y mantiene los guardas de pairing, rol y aprobación para construcción. |
| **E6 — coherencia insuficiente** | El procedimiento exige juzgar la intención y permite un bloqueante aunque pase la validación estructural. U6 documenta ese juicio semántico. |
| **E7 — cambio de fuentes** | La recepción conserva la comparación canónica. La política declara ambas salidas sin tolerar silenciosamente fuentes distintas. |

**U5:** sin exención no cambia el payload histórico. Con exención, el bloque contiene únicamente los campos declarados. El recorrido A→B→A conserva los rechazos y el no-op de la vigente.

**V-5:** medí **3033 bytes**, frente al techo de **12000**. El substage conserva la referencia al hogar canónico de `detail`; no introduce otra regla independiente.

En los cinco ejes no identifiqué otro defecto material. Los tests nuevos examinados se vinculan a las PD y usan el CLI real; las comprobaciones textuales corresponden a superficies procedimentales del contrato.

## Verificación independiente

Comandos ejecutados:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_006_006_u1_draft_object_form.py tests/test_006_006_u2_review_procedure.py tests/test_006_006_u3_review_route_and_gate.py tests/test_006_006_u4_reviewer_role_agents.py tests/test_006_006_u5_exemption_record.py tests/test_006_006_w1_replace_draft_packet.py -q -p no:cacheprovider
```

```text
72 passed in 40.77s
```

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_004_003_t1_draft_contract.py tests/test_004_003_t1_reviewfix.py tests/test_004_003_t2_plan_review.py tests/test_004_003_t2_reviewfix.py tests/test_005_007_t1_progressive_detail_rule.py tests/test_005_012_t2_gate_authority.py tests/test_005_012_t5_approval_vigency.py tests/test_005_014_closure_replay.py tests/test_006_005_u5_disposition_failed.py tests/test_005_001_t2_replace_packet.py tests/test_005_005_t1_replace_conserved.py -q -p no:cacheprovider
```

```text
62 passed in 75.07s
```

La sonda adicional de vigencia terminó correctamente tras corregir dos errores iniciales de importación; ninguno ejerció el producto.

**Archivos modificados por esta revisión:** ninguno.  
**Commit creado:** ninguno. El estado de trabajo observado al terminar coincide con el inicial. No leí el archivo privado excluido.

## Abstentions

- No reproduje los despachos reales de U6 ni inspeccioné sus artefactos originales; distingo su evidencia documental de las comprobaciones independientes anteriores.
- No certifiqué `make validate` verde: los informes registran **168 PASS / 1 FAIL**, atribuido a F011 ambiental.
- No ejecuté la suite completa: corresponde a quien cierre, según la política del paquete.