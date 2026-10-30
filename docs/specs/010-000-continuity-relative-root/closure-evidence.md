# Evidencia y límites para el cierre de 010-000

Estado: cierre pendiente; este registro no aprueba gates ni Memory Bank.

## Evidencia disponible

- Contrato aprobado por Pablo: `spec.md`, sha256
  `623b15e14290739f6f7c099183a06348b91bcce02eac4dce37265019f01737e2`.
- Implementación: `3842e18`, dos scripts canónicos del skill, sin cambios de tests.
- Tests: `6e71e78`, corrección de fixtures/oráculos sin alterar el contrato.
- RED corregido sobre código pre-fix `34dcd9b`: cuatro fallos de comportamiento;
  cinco casos verdes sobre el fix, confirmados por el orquestador (18.44 s).
- Regresión proporcional reportada por implementer: lotes de 82 y 15 pruebas
  verdes. No sustituye la suite completa.
- Review independiente: `review.md`, sin bloqueantes. Prueba adicional del
  consumidor en una copia sin build: staging generado e instalación aislada,
  un caso verde (19.85 s). No hubo actualización global ni publicación.
- Suite completa: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests -q`
  terminó con **8 failed, 1624 passed, 5 skipped, 217 errors**, rc=1. Log
  `.cdad/evidence/full-suite-010-000.log`. Los errores examinados muestran
  agotamiento de temporales/inodos. Recuperación selectiva completada según
  `full-suite-recovery.md`: 225 casos verdes en 23 lotes rc=0, inventario exacto
  sin duplicados ni faltantes. Evidencia conjunta: **1849 passed, 5 skipped**,
  sin cambios de código o tests. No presentar como corrida única verde.
- El primer intento de colección sin ámbito incluyó el ejemplo Odoo y falló
  fuera de `tests/`; no se modificó ni ocultó ese ejemplo para obtener verde.

## Validación complementaria aceptable

- Reviewer: copia pública limpia de HEAD `aa03482`, staging, instalación y
  `install.sh --check` y `make validate` con raíz aislada: todos rc=0. Evidencia
  en `isolated-validation.md` y `.cdad/evidence/isolated-validate-010-000-20261029T211209Z-r006/`.
  El producto real y HOME global no se modificaron. A3 en esa copia usa solamente
  el fallback público; no acredita patrones privados.
- Orquestador: `bash tests/validate-odoo-specialization.sh` sobre el checkout
  real con su configuración local: 68 PASS / 0 FAIL, rc=0, incluido A3. Log
  `.cdad/evidence/odoo-private-scan-010-000.log`. No se copió ni publicó el
  archivo privado. Esto completa la verificación de sanitización por separado.
- El resultado anterior del reviewer (intento 23) no se acepta como gate: copió
  un private_path y no acreditó comparación del prompt por bytes. Se conserva
  en el recibo y se repitió el encargo; su PASS no se usa como aprobación.
- El fallo de `make validate` contra HOME global permanece visible: la validación
  aislada demuestra producto reproducible, no repara ni certifica HOME global.

## Opcionales del review — propuesta de disposición

Pendiente de decisión del usuario, no constituye priorización aprobada:

- O1–O3: las sondas del reviewer confirman comportamiento correcto de
  verify-begin relativo, checkpoint por API y raíz symlink. Proponer registrar
  ampliación de regresión como hardening posterior sin bloquear este fix.
- O4: el reviewer ejecutó el consumidor desde copia sin build, cerrando la
  evidencia funcional instalada. Automatizar siempre esa condición en test_D y
  comparación byte a byte de scripts queda como mejora de reproducibilidad.
- O5: helpers privados fuera de las entradas comprometidas pueden rechazar con
  ValueError en lugar de PolicyError; proponer corrección posterior acotada,
  no ampliar firmas ni debilitar containment en este ciclo.
- O6: lista de ADRs Proposed desactualizada, preexistente; proponer mantenimiento
  posterior de Memory Bank, sin atribuirlo al fix.

## Deuda que no debe desaparecer

Conservar `deferred-hardening` de la spec: containment resuelto de referencias
de continuidad (seguridad/compatibilidad), TOCTOU de symlinks, fallos de disco,
nuevas plataformas y refactor general de consumidores de rutas. Las sondas del
review no convierten estos pendientes en garantías.

## Incidencias operativas

La extracción de interfaz por architect se detuvo por cuota del modelo. Se
reencauzó RED con introspección pública, sin lectura de implementación. Un
reintento de recepción del mismo paquete produjo conflicto entre nombres de
partes; el recibo anterior se conservó y no se forzó su reemplazo.

El despacho RED 17 precedió a una enmienda del plan. Su registro falló por drift
contractual; el orquestador abrió después el intento 18 y registró allí el texto
obtenido bajo el 17, declarando el desfase. **No es prueba de un begin previo al
transporte del intento 18.** Mantenerlo como desviación trazable, no presentar
esa recuperación como continuidad íntegra ni usarla como precedente normativo.

Siguiente unidad por instrucción del usuario: `010-004-packet-dispatch-ergonomics`,
antes de las tres features documentales. Investigar sus fallos observados antes
de decidir un mecanismo. No publicar ni cambiar modelos por cuenta propia.
