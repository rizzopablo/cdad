# Revisión focal de `166b481a`

**Resultado: permanece un hallazgo bloqueante sobre el handoff al reviewer.** La convención de correcciones resuelve la contradicción anterior dentro del alcance contextual examinado. Esta revisión no aprueba la feature.

## Hallazgo bloqueante

### 1. El paquete enumera el contexto, pero no instruye al reviewer a leerlo

**Required · Verdict: BLOCKING · Bucket: h**

**Ubicación:** `skills/cdad-cycle/references/handoff-prompts.md:606–614,623–632`; `skills/cdad-cycle/references/stage-2-specification.md:63–68`; `skills/cdad-cycle/scripts/cdad_packet.py:2201–2202`; `skills/cdad-cycle/packets/substages/reviewer-plan-review.md:1`.  
**Contrato:** PC-2 y PC-9, `spec.md:45–49,115–117`.

Las comillas corrigen la separación del argumento y el ejemplo ahora incluye `--input`. Sin embargo, ese argumento entrega al paquete **una ruta y un propósito**, no el contenido del diálogo. El packet indica que solo se lean los inputs y ámbitos declarados, pero las instrucciones del reviewer de borrador no le ordenan leer ese input ni contrastar el borrador con sus decisiones y correcciones. La instrucción de «entregar el contexto completo» queda fuera del packet que recibe el reviewer.

**Reproducción independiente:** preparé, en un proyecto desechable, un packet `reviewer/plan-review` sobre una spec con `--object-kind spec` y el argumento citado. `prepare` terminó con **rc 0** y el render mostró:

```text
- docs/specs/006-006-w1-fixture/discovery.md: Dialogue context
```

El contenido del diálogo y el identificador `DC-01` **no aparecieron en el packet**. En una segunda comprobación, tras retirar el input de la fixture, `render` siguió terminando con rc 0 y enumerándolo. Esto no demuestra que todo reviewer lo ignore; sí muestra que el packet, por sí solo, no asegura su lectura ni que el archivo siga disponible.

**Consecuencia:** un reviewer que siga literalmente el packet puede revisar el borrador sin contrastarlo con el registro atribuido y no detectar una decisión, autoridad o corrección perdida: precisamente el riesgo que PC-2 exige cubrir.

**Cierre verificable:** hacer que la ruta efectiva del reviewer le ordene inequívocamente leer el `Dialogue context` completo declarado y contrastar el borrador con él, preservando las reglas de packet y de no modificar publicaciones históricas. Preparar un packet representativo y verificar tanto la ruta como la instrucción efectiva recibida; demostrar también que una ausencia o falta de acceso al contexto no se presenta como revisión fiel.

## Resultado de los dos bloqueos anteriores

1. **Handoff:** parcialmente corregido. El argumento es válido cuando se cita y aparece en el ejemplo, pero persiste el defecto de entrega efectiva descrito arriba. Además, para una **spec** el ejemplo necesita `--object-kind spec`: al reproducirlo sin esa opción el CLI rechazó la spec como plan; la explicación posterior sí documenta esa distinción. No abro otro hallazgo separado.
2. **Correcciones:** **corregido contextual y documentalmente**, dentro del alcance examinado. La entrada nueva contiene `supersedes`; la línea añadida al índice permite recuperar `superseded-by` sin editar la entrada anterior. La fuente y los dos orchestrators generados coinciden. No es evidencia de aplicación observada por agentes.

## Categorías de evidencia por promesa

- **PC-1–3: Failed.** Persiste el handoff del hallazgo 1; falta también la aplicación observada comprometida en PC-11.
- **PC-4: Missing.** No se observaron las rutas revisada, exenta ni los intentos con exenciones incompletas.
- **PC-5: Supported within declared limits**, según la regresión independiente registrada en `review-002.md:61–71`; verifica transporte y materialización, no fidelidad semántica.
- **PC-6: Missing.** Sigue pendiente la identificación de publicaciones candidatas y paquetes en vuelo afectados, con sus versiones congeladas.
- **PC-7: Supported within declared limits**, según la regresión y revisión contextual registradas en `review-002.md:42–52`.
- **PC-8–10: Failed / Missing.** Persiste el handoff señalado; faltan asimismo las versiones efectivamente consumidas y evidencia de entrega candidata.
- **PC-11: Missing.** No se observaron J1–J7 ni C1–C5.

PC-4 y PC-11 son trabajo futuro no realizado y su evidencia es necesaria para la aceptación de la feature; no la doy por ejecutada.

## Comprobaciones y límites

- **Intake:** ruta C. `validate-request` y `validate-packet` terminaron con rc 0; la identificación renderizada coincidió con la recibida y `render | cmp PACKET.md` terminó con rc 0. Contexto de ejecución v2.
- **Tests primero:** examiné `tests/test_019_002_discovery_delivery.py` y `tests/test_019_002_resting_orientation.py`. No repetí la suite ni los 63 tests declarados en `review-fix-002.md`; ese informe no registra el comando exacto ni un log recuperable. Reutilizo, con el límite indicado, los 32 tests independientes registrados en `review-002.md`.
- **Preparación representativa:** ejecuté el comando documentado con rutas concretas en una fixture desechable. Sin `--object-kind spec`: rc 2, con diagnóstico de bloque `plan-tasks` ausente. Con `--object-kind spec`: rc 0, input listado, contenido y `DC-01` ausentes del render.
- **Generación:** ejecuté `python3 scripts/cdad-generate.py --runtime "$r" --stack generic --out "$d/$r"` para `opencode` y `claude-code`, y comparé cada orchestrator generado con su correspondiente en `agents/` mediante `cmp`: **rc 0 en ambos**.
- **Diff:** `git diff --check bc922c04..166b481a -- skills sources agents scripts tests README.md CDAD_metodologia.md`: **rc 0**.
- **Contrato:** `sha256sum docs/specs/019-002-effective-discovery-instructions/spec.md` produjo `5cca6fa6d0cde92cadab961c8218126a741432b575bc169df24c7901eef34eb0`.
- **Decisiones:** las 32 rutas ADR indexadas existen; los 11 ADR sin fila examinados figuran como propuestos. No detecté contradicción con las decisiones que gobiernan esta revisión.
- **Archivos modificados por esta revisión:** ninguno. **Commit de revisión:** ninguno. `git status --short` mostró únicamente la modificación preexistente de `docs/.cdad-state.json`.

## Abstentions

- No puedo acreditar la fidelidad de agentes reales ni las rutas PC-4 y PC-11 sin las observaciones, transcripts y versiones efectivas previstas para T3.
- No verifiqué una instalación desplegada, la familia de modelo del implementador ni la selección completa de regresión informada en `review-fix-002.md`.