# Review-5 focal T5 — 004-001-canonical-runtime-artifacts

Fecha: 2026-09-27. Reviewer: GPT/Codex (familia distinta del implementer GLM).
Árbol: `d47533a`. Read-only: código, tests, estado e instalaciones reales sin
modificaciones (comprobaciones sobre copias temporales).

## Verdict

```
dictamen: changes-required
blocking: 4
optional: 0
abstain:  0
```

## Hallazgos

| Hallazgo | Verdict / bucket | Motivo comprobado | Procedencia |
|---|---|---|---|
| **B1 — `--check` no comprueba los bytes del agente instalado** | BLOCKING / h | Instaló, modificó el agente y ejecutó `--check`: **PASS**. Compara el hash histórico del manifest contra staging, sin calcular el del archivo instalado. | `install.sh:1216`. PD-5. |
| **B2 — Los cambios locales de skills y del guard se sobrescriben** | BLOCKING / h | Modificó una skill y el guard. El dry-run no informó conflictos; la reinstalación sobrescribió ambos y terminó exitosamente. La protección está implementada para agentes, pero estos archivos también figuran como propiedad del instalador. | `install.sh:822`, `install.sh:885`. PD-7. |
| **B3 — Reinstalar hace olvidar archivos obsoletos** | BLOCKING / h | Retiró un agente de staging y reinstaló. El archivo antiguo permaneció instalado, desapareció del manifest y `--check` dio **PASS**. Después sobrevivió al uninstall. La actualización pierde información necesaria para gestionar lo que CDAD instaló. | `install.sh:733`, `install.sh:744`. D4, PD-5 y ciclo de propiedad de T5. |
| **B4 — El perfil solicitado puede diferir del instalado** | BLOCKING / h | `--basic` terminó exitosamente y escribió el marcador `basic`, pero instaló staging `optimus`, conservando modelos fijos. Una opción que antes seleccionaba modelos ahora solo cambia una etiqueta; puede usar un proveedor/modelo distinto del esperado. | `install.sh:835`, `install.sh:1430`. Compatibilidad de perfiles e invariante 4. |

Reproducciones del reviewer: `/tmp/cdad-review5-ck32p_qi/observations.json`,
`/tmp/cdad-review5-ck32p_qi/profile-observation.json`.
Reproducidas además por el orquestador (B1: drift → PASS; B4: marker `basic`
con `model:` de optimus y manifest `optimus`).

## Adicional (recomendación)

`--uninstall` elimina un agente modificado localmente sin informar esa
modificación. Aplicar allí la misma política de preservación y resolución
explícita: la propiedad histórica no es autorización automática para descartar
cambios posteriores.

## Por qué los 80/80 no contradicen los hallazgos

El test de drift modifica staging, no el archivo instalado; el de obsoletos
comprueba antes de reinstalar. **Faltan regresiones de recorrido completo** de
esas transiciones. No se repitió la suite completa.

## Cómo continuar (avalado)

T5 permanece dentro de 004-001; estos arreglos completan su semántica original:

1. Tratamiento común de propiedad y conflictos para agentes, skills y guard.
2. Comparar archivo actual, hash registrado y versión propuesta; conservar el
   registro de archivos pendientes de retirada o resolución.
3. Perfil efectivo inequívoco: si staging no coincide con lo solicitado,
   informar el desacuerdo antes de instalar; no publicar etiquetas
   contradictorias.
4. Regresiones de recorrido completo: editar y actualizar; retirar y
   actualizar; seleccionar perfil e instalar.

**Migración pre-T5 → T6** (confirmado): preservar archivos diferentes cuando no
hay manifest previo es correcto. GLM prepara inventario, comparación y
propuesta de adopción dentro del alcance delegado; archivos que coincidan con
una versión previa identificable pueden tener migración definida; cambios
locales desconocidos se conservan hasta resolverlos.

## Opinión de diseño (registro)

Conservar contratos, sesiones independientes, paquetes y supervisión del
orquestador; conservar la separación generación→staging→instalación.
Simplificar la convivencia de caminos antiguos y nuevos: hoy una misma
instalación aplica criterios diferentes según el tipo de archivo (complejidad y
resultados engañosos).

## Feedback de proceso (para el bucket de 003-003 y el contrato de evidencia)

- Que el orquestador ejecute la evidencia es válido y trazable, pero **no
  elimina el costo de que quien construye no pueda comprobar su trabajo**:
  resolver la capacidad operativa del implementer; no darla por resuelta por el
  rodeo.
- Exigir siempre un reporte, incluso "bloqueado, sin cambios", es mejor que
  exigir cambios cuando quizá no corresponde hacerlos.
- El éxito de CDAD debe verse en desarrollos reales terminados con menos
  intervención y retrabajo; el número de controles no demuestra ese resultado.

Materializado por el orquestador (GLM) desde el reporte final del reviewer
(ADR-003).
