# Decisión del orquestador — T1 GREEN (003-007)

GREEN `b1e56e9` deja 50 tests verdes y 2 rojos en el gate acotado. Ninguno de los dos rojos es un defecto de producción:

1. `test_p03_clase_desconocida_se_cierra_como_contract` llama a `begin` sin crear el
   archivo referenciado. `begin` falla cerrado ante una referencia inexistente (003-004 R-B1),
   así que el test no llega a probar la clase. **Defecto del test.**
2. `test_003_004_t1_checkpoint.py::test_p1_segundo_checkpoint_encadena_y_digesta_referencias`
   compara `references` exactamente con `[{path, sha256}]`. P3 exige estampar `class`.
   **Cambio de contrato declarado.** Se aceptan las claves `class`/`fields`, igual que se
   hizo con la faceta B de `test_003_004_t1_resume.py`.

**Contrato de dónde va la clase: opción A.** La clase se estampa en el body (spec §3) y la
envolvente `head.json` la refleja, porque la envolvente ya refleja `references` del body
(verificado en el head real de `exec-003-007`). Así se cumplen a la vez la spec y la lectura
del RED (S2, p04).

Siguiente paso: un paquete test-writer (`red-002`) corrige los dos tests sin tocar producción.
Después el orquestador corre el gate acotado y lo cita, y sigue la review de T1.
