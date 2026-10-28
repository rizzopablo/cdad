# 008-003 — Plan de extracción y adopción

## Steps

- [ ] Fijar el inventario de decisiones y sus bordes consumidores.
- [ ] Aprobar evidencia RED vinculada a las seis postcondiciones.
- [ ] Extraer el núcleo puro y migrar P/C/R retirando las ramas anteriores.
- [ ] Verificar compatibilidad, eliminación estructural y límites de deuda.
- [ ] Cerrar con los gates compartidos y evidencia de adopción.

## Detalle

### 1. Inventario

Partir de las referencias de la spec y registrar por decisión: fuente de hechos, entrada CLI/programática, regla actual, regla destino y rama que desaparecerá.

Incluir las guardas previas al replay y las funciones invocables sin pasar por `main`. Separar selección de archivos, comprobación física y presentación de la política migrada.

**Salida:** mapa revisable de alcance; cualquier borde adicional de P/C/R que decida estas mismas materias debe incorporarse. D/E permanece fuera.

### 2. RED

El test-writer aislado propone evidencia por postcondición y reutiliza contratos existentes antes de añadir tests. El dueño aprueba el criterio antes de implementación.

La comprobación estructural debe poder distinguir extracción de fachada sin imponer nombres privados arbitrarios.

### 3. GREEN

Introducir el núcleo sin I/O ni dependencia inversa de consumidores. Adaptar los hechos recogidos por P/C/R y retirar en el mismo cambio las decisiones reemplazadas.

Mantener almacenamiento, serializadores, comparaciones canónicas y publicación existentes. Integrar primero identidad/propietario, después autoridad/elegibilidad y finalmente orden replay/efecto nuevo, sin dejar una ruta alternativa que conserve la política antigua.

### 4. Review

El reviewer independiente contrastará PC-01..06 y el inventario antes/después, especialmente:

- Argumentos contradictorios en replay.
- Suspensión atribuida al propietario real.
- Invocación directa sin guarda exclusiva de CLI.
- Autoridad desconocida y excepción standalone.
- Recibo durable con cierre todavía pendiente.
- Historia legacy sin claves recalculadas.

Registrar cierre condicionado de IDENTITY, cierre parcial de GUARD y persistencia de LOCK/APPROVAL.

### 5. Cierre

Ejecutar los gates compartidos del epic sin redefinirlos y la suite completa una vez por el closer. Conservar el mapeo PC→evidencia y documentar `deferred-hardening`.

Actualizar memoria documental sólo mediante los roles y aprobaciones correspondientes. No incluye despliegue, activación ni publicación externa.
