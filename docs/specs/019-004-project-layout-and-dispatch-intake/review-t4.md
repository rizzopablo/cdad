# Revisión contextual — 019-004, T4

**Promise E: Failed.** La guía efectiva todavía no establece una vía utilizable y coherente de intake para todos los consumidores previstos. El ejercicio instalado es evidencia relevante, pero no cierra por sí solo la revisión contextual.

## Hallazgos

### 1. El rol puede quedar sin forma autorizada de localizar el comando instalado

**Required — Verdict: BLOCKING · Bucket: h**

**Evidencia.** `sources/roles/architect.md:63–68`, distribuido por ejemplo en `agents/cdad-reviewer.md:74–79`, define `<skill-dir>` como el directorio que informa el runtime, prohíbe cargar el skill para obtenerlo y también prohíbe buscarlo en el filesystem. En esta sesión, el catálogo disponible informa el ID y la descripción del skill, pero no su directorio. La prueba `tests/test_019_004_installed_intake.py` conoce la ruta de instalación directamente; no demuestra que un rol recién iniciado pueda descubrirla siguiendo esas instrucciones.

**Consecuencia.** En un runtime con ese catálogo, el rol debe detenerse y escalar la ausencia de ruta aunque el CLI esté instalado. Esto incumple la finalidad de PC-15: usar el procedimiento instalado sin tener que redescubrirlo.

**Remedio y cierre verificable.** Definir una vía proporcionada y autorizada para resolver el CLI instalado, o una alternativa operativa explícita cuando el runtime no reporte la ruta; regenerar las distribuciones y comprobar el recorrido desde las instrucciones efectivas, sin introducir de antemano la ruta en el consumidor.

### 2. Falta la alternativa contractual cuando no hay captura fiel del mensaje

**Required — Verdict: BLOCKING · Bucket: h**

**Evidencia.** La especificación §6.1 exige que, si el runtime no puede exponer fielmente el mensaje recibido, se informe el límite y se use el procedimiento manual existente sobre el mensaje original. `agents/cdad-reviewer.md:74–88` exige pasar el mensaje realmente recibido y reconoce que la captura nativa no está verificada, pero no indica esa alternativa. El mismo texto procede de `sources/roles/architect.md:63–77`.

**Consecuencia.** En un entorno sin exportación fiel, el rol recibe la obligación de invocar `intake` sin disponer del insumo exigido y sin una instrucción efectiva que le permita continuar por la vía manual. PC-15 y PC-16 requieren que la guía preserve las distinciones de intake y sus límites.

**Remedio y cierre verificable.** Referenciar la alternativa manual canónica en las instrucciones efectivas y regenerar los consumidores. Verificar tanto el caso con representación fiel como el caso sin ella: este último debe informar la limitación y aplicar la validación manual al original, sin atribuirse validación automatizada.

### 3. La confirmación de bootstrap mezcla respuestas de sentido opuesto

**Required — Verdict: BLOCKING · Bucket: h**

**Evidencia.** `skills/cdad-cycle/references/bootstrap.md`, paso 1, pregunta primero si es la primera aplicación de CDAD y después si CDAD ya existe en otra ubicación. A continuación dice que «only an explicit affirmative answer» permite continuar, pero también que, si el usuario dice que existe en otra ubicación, se detenga.

**Consecuencia.** Para un proyecto genuinamente nuevo, las respuestas correctas son **sí** a la primera pregunta y **no** a la segunda. La instrucción no identifica a cuál respuesta se aplica el «affirmative» y su frase «if they say no» también puede referirse a cualquiera de las dos. El operador puede detener un bootstrap válido o interpretar incorrectamente la confirmación.

**Remedio y cierre verificable.** Formular las condiciones por separado: continuar únicamente cuando se confirme que es una primera aplicación **y** que no existe CDAD en otra ubicación; detenerse ante incertidumbre o existencia previa. Revisar la guía efectiva con ambos casos y sus respuestas explícitas.

## Evidencia y límites

- Revisé primero `tests/test_019_004_installed_intake.py`, después la especificación y las instrucciones afectadas por `aad01db5` y `71e3d694`; la prueba instalada corresponde a `3a9d3b30`.
- Validé `REQUEST.json` y `PACKET.md` mediante `validate-request` y `validate-packet`, y contrasté la identificación recibida con `render --route C`. Ambos validadores terminaron sin diagnóstico; el render coincidió con la identificación recibida.
- No ejecuté tests, conforme al encargo. La prueba instalada inspeccionada contempla aceptación, rechazo de una identificación alterada y comparación del árbol, pero **no constaté una salida de ejecución** que acredite su resultado. El encargo indica que una suite completa está en curso por separado.
- La revisión fue de solo lectura; no modifiqué archivos ni generé commits. El checkout ya mostraba cambios en `docs/.cdad-state.json` y `suite-inventory.json`.
- El alcance fue la alineación contextual de T4 y la evidencia instalada señalada; no constituye una revisión integral de las implementaciones de layout e intake.

## Abstentions

- **Resultado efectivo de la prueba instalada y de la suite completa:** no verificado en esta sesión; se requiere su salida y estado finales.
- **Otros runtimes:** no comprobé qué metadatos de ruta de skill proporciona cada uno. El primer hallazgo se sustenta en el catálogo visible en esta sesión y en la prohibición explícita de las instrucciones.