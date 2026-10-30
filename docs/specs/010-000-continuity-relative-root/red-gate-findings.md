# Gate RED — devolución al rol

El commit de tests `24eea61` modifica solo el archivo nuevo autorizado. El fallo
relativo está reproducido según el resultado, pero esto no cierra RED por sí solo.

Defectos observados al verificar el resultado contra el contrato:

- Línea 385: `assert _tree(root) == before or True` es tautológica; no comprueba
  ausencia de efectos ante rechazo (PC-06/07).
- Línea 346: la comparación de snapshot está unida por `or` al no_op ya verificado;
  puede pasar aunque el replay cambie archivos (PC-05).
- Las APIs programáticas de PC-02/03 no se ejercitan; el rol declara firmas no
  deducibles. Un CLI no acredita por sí solo todas las entradas programáticas.
- El test C no comprueba el resultado de clasificación inválida ni demuestra
  todos los controles de seguridad que dice proteger. El caso de paquete ajeno
  no acredita paquete alterado y autoridad revocada.
- El consumidor instalado solo llega al begin relativo; no demuestra todavía la
  equivalencia, checkpoint y rechazo sin publicación comprometidos por PC-08.

Disposición: no abrir GREEN; no modificar los tests desde el orquestador. Pedir
al architect un contrato mínimo de interfaces, sin cuerpos ni algoritmos, y luego
al test-writer corregir su propio artefacto. Conservar el commit como evidencia,
sin borrar trabajo ni relajar PCs. No imponer una cuota de tests por PC: las
promesas pueden agruparse, pero ninguna aserción puede ser vacua.
