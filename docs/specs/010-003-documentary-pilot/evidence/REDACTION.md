# Redacción para publicación — evidencia del cierre

Los archivos de este directorio y los documentos de la feature se **redactaron
para la publicación**: se reemplazaron rutas absolutas del entorno local por
`<repo>`, `<workspace>`, `<home>` y los identificadores de sesión del runtime por
`<session>`. La redacción no altera ningún resultado medido, ningún veredicto ni
ninguna decisión: cambia sólo identificadores del entorno.

- **Alcance:** los archivos del delta de publicación que contenían esos datos
  (29 archivos), no el árbol ya publicado con anterioridad.
- **Manifiesto:** `SHA256SUMS` se recalculó sobre los bytes redactados; los
  digests de los canarios se conservan porque los canarios no se publican.
- **Originales:** los bytes sin redactar permanecen en el store local de la
  ejecución (`.cdad/`), que no se versiona.
- **Hashes de gate:** algunos documentos cambiaron de hash después de su gate por
  esta redacción; el estado conserva el hash registrado en el gate. La redacción
  es posterior al cierre y no reabre ninguna aprobación.
