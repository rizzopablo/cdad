# Revisión de estrategia tras dos intentos de AUDIT bloqueados

No se acredita AUDIT ni RED. Ambos workers declaran no haber leído tests ni
implementación y no haber cambiado archivos.

1. El primer worker confundió el cierre del bloque JSON del formato canónico con
   el final del paquete, sin consultar el renderer.
2. El segundo utilizó `docs/.cdad-state.json` y el contexto legacy en lugar del
   contexto v2 que identifica la cabecera del encargo.

Decisión operativa: no repetir el encargo idéntico ni pedir que el worker infiera
rutas. Publicar un nuevo paquete con comandos completos de validación y render,
rutas absolutas del contexto v2, REQUEST y PACKET, y prohibición de sustituirlos
por el estado o un contexto legacy. La información nueva responde a los dos
fallos observados; no se elimina ni relaja el intake. Si este intento no valida
con esas entradas comprobadas, detener este transporte y elevar el bloqueo en
lugar de seguir consumiendo intentos.

Las rutas operativas se llevan solo en el paquete local; no forman parte de esta
nota compartible. No es una autorización para leer implementación ni ampliar el
alcance del test-writer.
