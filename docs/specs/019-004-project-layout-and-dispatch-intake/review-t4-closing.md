## Dictamen

**El alcance de instrucciones de T4 puede declararse cerrado**, sujeto a la decisión del orquestador. En el commit `847e3c9d` no encontré contradicciones que mantengan abiertos los tres hallazgos anteriores:

1. **Resolución del CLI:** el directorio informado por el runtime tiene prioridad. Si solo informa el ID, la instrucción permite leer el manifiesto de instalación para localizar el CLI, sin buscar en el filesystem ni cargar el cuerpo del skill.
2. **Sin captura fiel:** la guía indica informar la limitación, validar manualmente el mensaje original y no atribuirse validación automatizada.
3. **Bootstrap:** exige por separado confirmar que es la primera aplicación y que CDAD no existe en otra ubicación; ante incertidumbre o confirmación ausente, indica detenerse.

Estas conclusiones son una **revisión contextual de las instrucciones**, no una aprobación ni una demostración de despliegue o de recorrido completo.

## Evidencia y límites

- Revisé `tests/test_019_004_installed_intake.py`, la especificación, los hallazgos previos y el diff de `847e3c9d`. El commit modifica las instrucciones canónicas, sus agentes distribuidos y la guía de bootstrap.
- No ejecuté tests, conforme al encargo. La prueba inspeccionada fija directamente la ruta instalada; por sí sola no demuestra que un rol recién iniciado la resuelva siguiendo la nueva guía.
- `validate-packet` terminó sin diagnóstico. El comando `render --route C` emitió una identificación que contrasté con la recibida.
- **Limitación de mi propio intake:** ejecuté también `intake` pasando por stdin una reproducción del mensaje. Aunque devolvió éxito estructural, no puedo acreditar que esa reproducción fuera una captura nativa fiel. **No presento ese resultado como validación automatizada del despacho recibido**; el contraste manual y la validación del paquete son la evidencia utilizada.
- No modifiqué archivos ni creé commits. `git status --short` mostró `M docs/.cdad-state.json` ya presente en el checkout.

## Abstentions

- **Instalación real:** la copia instalada en HOME no fue redesplegada como parte de esta revisión. Un recorrido de rol fresco con estas instrucciones depende de ese despliegue y no quedó demostrado aquí.
- **Resultados de ejecución:** no verifiqué salida final de la prueba instalada ni de la suite completa. No afirmo que estén verdes.
- **Cierre integral de la feature:** esta revisión no vuelve a evaluar las implementaciones de layout e intake ni acredita procedencia nativa de entrega.