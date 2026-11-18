# Revisión focal de `974d55d5`

**Resultado: permanecen dos hallazgos bloqueantes.** No apruebo la feature. La ruta sin consulta y la distinción entre cierre inferido y estado operativo corrigen los hallazgos 3 y 4 de la revisión anterior, dentro del alcance contextual examinado. Los hallazgos 1 y 2 están parcialmente corregidos, pero las nuevas instrucciones presentan los problemas siguientes.

## Hallazgos bloqueantes

### 1. El comando de handoff al reviewer no entrega el contexto tal como está escrito

**Required · Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-cycle/references/stage-2-specification.md:63–68`; `skills/cdad-cycle/references/handoff-prompts.md:606–614,627–631`; `skills/cdad-cycle/scripts/cdad_packet.py:2455–2459`.  
**Contrato:** PC-2 y PC-9, `spec.md:45–49,115–117`.

La corrección indica pasar el contexto como:

```text
--input docs/specs/<feature>/discovery.md=Dialogue context
```

Pero el CLI acepta un único argumento `PATH=PURPOSE`. Sin comillas ni escape, el shell separa `context` como otro argumento. Además, el comando completo de ejemplo situado inmediatamente antes no incluye `--input`.

**Consecuencia:** quien siga literalmente la instrucción no puede preparar ese paquete con el argumento indicado; quien copie el comando completo prepara el handoff sin el input requerido. En ambos casos, la ruta documentada no asegura que el reviewer reciba el registro completo necesario para detectar decisiones o correcciones perdidas.

**Cierre verificable:** corregir ambas instrucciones para que el ejemplo completo incluya un argumento válido, por ejemplo `--input 'docs/specs/<feature>/discovery.md=Dialogue context'`, y verificar una preparación representativa y su render: el input debe aparecer íntegro en el paquete entregado.

### 2. La convención de correcciones ordena modificar y no reescribir la misma entrada

**Required · Verdict: BLOCKING · Bucket: h**  
**Ubicación:** `skills/cdad-cycle/references/stage-2-specification.md:30–32`; `sources/roles/orchestrator.md:144–150`; consumidores generados `agents/cdad-orchestrator.md` y `agents/claude-code/cdad-orchestrator.md`.  
**Contrato y fuente:** PC-2, `spec.md:45–49`; diseño aceptado `operating-design/handoff-fidelity.md`, §§3 y 5.

La nueva convención exige que la entrada reemplazada **reciba** un vínculo recíproco `superseded-by`, pero en la misma frase afirma que la entrada anterior **nunca se reescribe**. El orchestrator generado también dice que se preserve y «never rewritten». Para una entrada ya registrada sin ese vínculo, añadirlo implica editarla; no se indica una forma compatible de hacer ambas cosas.

**Consecuencia:** ante una corrección real, el operador debe elegir entre incumplir la prohibición de reescritura o dejar de registrar el vínculo recíproco exigido. Esto afecta precisamente a la cadena atribuida que el architect y el reviewer deben poder recuperar.

**Cierre verificable:** definir una única operación coherente que preserve el contenido y la procedencia originales y haga recuperable la supersesión en ambos sentidos; reconciliar la fuente y sus consumidores generados. Contrastar el procedimiento con una entrada anterior ya existente y una corrección autorizada posterior.

## Estado de los hallazgos anteriores

| Hallazgo anterior | Resultado de esta revisión |
|---|---|
| 1. Handoff cualificado | **Parcialmente corregido:** se exige el contexto completo para architect y reviewer, pero subsiste el defecto concreto del comando de reviewer descrito arriba. |
| 2. Procedencia de correcciones | **Parcialmente corregido:** se añadieron autoridad, identificadores, fragmento, acción y vínculos; la operación de vínculo recíproco es contradictoria, como se indica arriba. |
| 3. Readiness sin consulta | **Corregido contextual y documentalmente:** se prescribe R1–R5 sin consulta y el mismo handoff. No acredita todavía una ejecución observada. |
| 4. Inferencia sin state | **Corregido contextual y documentalmente:** la fila distingue inferencia de trabajo terminado de estado operativo verificado. |

## Categorías de evidencia por promesa

- **PC-1–3: Failed.** Persisten los dos hallazgos anteriores; además, la aplicación observada de PC-11 está pendiente.
- **PC-4: Missing.** No se observaron las rutas revisada, exenta y de exenciones incompletas previstas para T3. Los tests ejecutados son regresión mecánica, no sustituyen esas observaciones.
- **PC-5: Supported within declared limits.** Los tests focales pasan para la derivación y materialización; no prueban fidelidad semántica de una consulta.
- **PC-6: Missing.** Sigue pendiente la identificación de publicaciones candidatas y de paquetes en vuelo afectados con sus versiones congeladas.
- **PC-7: Supported within declared limits.** Pasan las dos pruebas focales de cierre/orientación y la guía examinada distingue la inferencia sin state.
- **PC-8–10: Failed / Missing.** Los handoffs mantienen los defectos señalados; faltan también las versiones efectivamente consumidas y la evidencia de entrega candidata.
- **PC-11: Missing.** No se acreditaron el recorrido J1–J7 ni los casos C1–C5. Deben quedar pendientes, no presentarse como ejecutados.

La evidencia faltante de PC-4 y PC-11 es una condición pendiente para la **aceptación de la feature**, no una afirmación de que T3 ya se haya realizado.

## Comprobaciones y límites

- **Intake:** ruta C; `validate-request` y `validate-packet` terminaron con rc 0. El render de identificación coincidió con el recibido y `render | cmp PACKET.md` terminó con rc 0.
- **Tests primero:** examiné los tests focales de PC-5 y PC-7 y ejecuté:

  ```bash
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:tests python3 -m pytest -q -p no:cacheprovider \
    tests/test_019_002_discovery_delivery.py \
    tests/test_019_002_resting_orientation.py \
    tests/test_006_006_u3_review_route_and_gate.py \
    tests/test_006_006_u5_exemption_record.py
  ```

  Resultado: **32 passed in 51.62s**. No repetí la selección completa informada por el implementador ni ejecuté la suite completa.

- `git diff --check bc922c04 974d55d5 -- skills sources agents scripts tests README.md CDAD_metodologia.md`: **rc 0**.
- Contrato examinado: SHA-256 `5cca6fa6d0cde92cadab961c8218126a741432b575bc169df24c7901eef34eb0`.
- Tabla de decisiones: las **32 rutas ADR indexadas** existen; no detecté una contradicción con las decisiones gobernantes en el alcance focal.
- **Archivos modificados por esta revisión:** ninguno. **Commit de revisión:** ninguno. `git status --short` mostró únicamente `docs/.cdad-state.json` modificado, preexistente y excluido del producto.

## Abstentions

- No puedo acreditar comportamiento real de agentes, fidelidad de transcripts ni las rutas PC-4 y PC-11 sin la evidencia T3.
- No verifiqué independientemente la familia de modelo del implementador, una instalación desplegada ni toda la selección de regresión declarada en su informe.