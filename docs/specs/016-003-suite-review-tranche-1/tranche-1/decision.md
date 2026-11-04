# Decisión de continuación — tramo 1 de 016-003

**Decisión:** continuar con el tramo siguiente aplicando cambios explícitos de método.

**Responsable:** orquestador CDAD de 016-003 (HITL delegada por el dueño del proyecto).

**Autoridad:** mandato del dueño del 2026-11-02 («te delego hitl, eres el dueño del proceso… hasta
completar las correcciones pendientes y el epic completo»), dentro del plan del epic 016 y de la
spec aprobada de 016-003 §7. No se crea autoridad nueva: la misma delegación que autorizó este
tramo autoriza el siguiente con los cambios que se declaran abajo.

**Motivo:** el tramo se completó con estructura verificada y sin hallazgos que justifiquen detenerlo.

- Las 398 filas del 20 % congelado están auditadas, una por nodeid, todas con evidencia
  recuperable y disposición `Mantener`; no apareció ningún candidato.
- Las 25 unidades afectadas tienen registro de vínculo validado (sin backfill fuera del tramo) y
  los 26 registros del proyecto validan rc 0 contra su colección.
- El costo por test es medido y su dispersión es conocida: 17,79 s de sesión por test en promedio
  (7.081,8 s de auditoría sobre 398 tests en 17 actividades, piloto incluido), con lotes que van de
  4,9 a 9,7 minutos según el tamaño y la cantidad de unidades. No hay componente experimental porque
  no hubo candidatos.
- El control estructural detectó un defecto real de producto durante el trabajo (resolución de
  obligaciones de contratos sin marcadores, ya corregida con RED/GREEN) y dos defectos de forma en
  entregas de rol (filas duplicadas en B8, hash transcripto en B12), ambos contenidos sin pérdida de
  contenido. La revisión independiente agregó un vínculo faltante (H1) y dos correcciones de forma
  (H3, H4), ya aplicadas.

**Evidencia de costo:** `costs.json` (17 actividades de auditoría, la revisión independiente, el
bloque de cierre con 31 comandos medidos y 3 bloques de preparación compartida, con sesión, rol,
alcance, nodeids, comandos, tokens —entrada, salida y caché cuando el runtime las expone—, inicio,
fin y duración observada; totales separados de auditoría, revisión, preparación y cierre, y
proyección con supuestos y cantidades). Resumen: 398 tests auditados en 22 sesiones, 7.081,8 s de
auditoría, 353,6 s de revisión, 1.304,6 s de preparación compartida (con un solapamiento declarado
de 90,1 s), 8.692,5 s de tiempo agregado por unión de intervalos y 9.643,7 s de reloj; 2.716.861
tokens de entrada, 702.509 de salida y 92.903.503 de lectura de caché. Proyección lineal del resto
(1.590 nodeids): 28.286,1 s de auditoría más 1.700,5 s fijos ≈ 8,3 h, sin descontar el ahorro
esperado de los cambios de método (cota alta).

**Alcance de lo autorizado:**

1. Auditar el tramo 2 del 20 % con el mismo contrato (016-003) y el mismo validador, sin relajar
   umbrales ni vocabulario.
2. Cambios de método autorizados para el tramo 2:
   - lotes de 25–40 nodeids con el registro de la unidad en la misma entrega (elimina la segunda
     pasada de normalización que consumió B1a/B1b/B2a/B2b);
   - objetivo del lote generado por script desde el plan, para no transcribir rutas ni esquema;
   - auditoría dirigida por promesa cuando la unidad tenga muchas obligaciones: leer el contrato
     primero y después los tests que lo citan;
   - el materializador descarta solo repeticiones byte-idénticas y aborta ante contenido
     divergente, para que un defecto de forma no se confunda con contenido nuevo.
3. Reutilizar el índice de vínculo de las unidades que ya lo tienen; el tramo 2 sólo agrega los
   vínculos que sus propios tests demandan.

**Lo que esta decisión no autoriza:** poda, consolidación o retiro de tests (requieren unidades
propias con conservación y sensibilidad acreditadas); backfill de vínculos fuera del tramo;
reescritura de contratos cerrados; reducción de la selección congelada; ni presentar la ausencia de
candidatos como prueba de redundancia universal.

**Condición de revisión:** si el tramo 2 arrojara candidatos cuyo costo experimental por candidato
supere el costo de auditoría del tramo, esta decisión debe revisarse antes de comprometer el tramo 3.
Del mismo modo, si el costo observado del tramo 2 se aparta más de un 30 % de la proyección
(28.286,1 s de auditoría, ≈ 7,9 h de auditoría), la diferencia se registra antes de comprometer el
tramo siguiente.
