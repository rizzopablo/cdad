# Dictamen plan-review — 010-003-documentary-pilot

**Objeto:** `plan.md` v2, sha256 `342cb14f…0d7ae6`, y `spec.md` v1, sha256 `ea71cb5f…7f3510`. Ambos digests coinciden con los bytes en disco.

**Recomendación: aprobable con cambios.** Hay 4 bloqueantes, todos cerrables sin tocar las promesas del epic ni D-1..D-6, salvo la decisión de orden de B-2. Este dictamen no aprueba nada.

**Intake:** ruta C, contexto v2. `validate-request` y `validate-packet` dieron rc=0. `render | cmp PACKET.md` dio 0, y la identificación coincide con `render --route C`.

## Bloqueantes

### B-1 — El encargo del ensayo excluye una norma que el propio paquete manda leer
**Required · Verdict: BLOCKING · Bucket: h**
- **Ubicación:** `plan.md`, T5 «Preparación del encargo»; `spec.md`, PC-07.
- **Fundamento:** el bloque común de todo paquete instruye sobre `documentary-contracts.md`: «read it, never restate it». Ese archivo está bajo `skills/`, y T5 solo declara contrato, `sources/` y `challenge/`, con raíces delimitadas.
- **Consecuencia:** el reviewer obedece el paquete y sale del alcance, o lo respeta y no lee la norma. Un acceso fuera de alcance puede ser leído como contaminación, y el ensayo es de un solo tiro (D-3).
- **Condición de cierre:** declarar `skills/cdad-cycle/references/` como lectura e input de T5, porque no revela respuestas. Comprobar también que T5 no depende de ningún otro archivo fuera de alcance.

### B-2 — El producto corregido existe en el árbol durante el ensayo, sin necesidad
**Required · Verdict: BLOCKING · Bucket: m**
- **Ubicación:** `plan.md`, T5 `depends_on: ["T3","T4"]` y «T4 fija su posición»; D-1, «El producto corregido se produce después».
- **Fundamento:** el propio plan admite que T4 no aporta insumos a T5. El orden abre una exposición evitable, porque el reviewer tiene bash permisivo y la clase de rol es lectora. Además introduce un informe GREEN que hay que ocultar. D-1 se lee más naturalmente con la corrección después del ensayo.
- **Consecuencia:** se debilita PC-07 sin ningún beneficio contractual.
- **Condición de cierre:** ejecutar T5 antes de T4 (T3→T5→T4→T6), o que la autoridad registre por qué se mantiene el orden actual. No pude verificar si algún gate impide esa reordenación (ver Abstenciones).

### B-3 — La anterioridad de la clave no tiene punto de fijación verificable
**Required · Verdict: BLOCKING · Bucket: h**
- **Ubicación:** `plan.md`, T3 («fija hashes antes del ensayo»), `observable_checks` de T3 y T5; `spec.md`, PC-03, PC-09 e INV-03.
- **Fundamento:** el plan no nombra ningún artefacto, ruta ni commit que registre los hashes de clave y candidato, ni los snapshots. El plan tampoco fija dónde se conservan esos hashes. Además `.cdad/` está ignorado por git (`.gitignore:11`), de modo que requests, paquetes y evidencia no se conservan por la vía versionada salvo que alguien los copie.
- **Consecuencia:** «no reconstruida después» queda como afirmación sin prueba. Es el núcleo anti-circularidad de la promesa A.
- **Condición de cierre:** antes de despachar T5, un commit identificado que contenga corpus, candidato y clave, más un registro de preparación sin respuestas que declare commit y hashes. Definir además qué evidencia de `.cdad/` se copia o se fija por hash en la feature.

### B-4 — T6 no recibe lo necesario para verificar la corrección de los defectos
**Required · Verdict: BLOCKING · Bucket: h**
- **Ubicación:** `plan.md`, T4 («candidato negativo cuando lo declare el encargo») y T6 («producto, contrato y fuentes inventariadas»); `spec.md`, PC-11 y PC-13.
- **Fundamento:** T6 debe revisar «la corrección de los tres defectos conocidos» sin recibir candidato ni clave. Si T4 omite el candidato, el producto no es una corrección de nada: PC-11 queda sin referente.
- **Consecuencia:** PC-11 y PC-13 se acreditan sin evidencia, o el reviewer lee fuera de sus inputs.
- **Condición de cierre:** hacer obligatorio el candidato en T4 y añadir candidato, clave y `challenge-contrast.md` a los inputs de T6, en sesión distinta de T5.

## No bloqueantes

| # | Severidad / tupla | Ubicación | Hallazgo y remedio |
|---|---|---|---|
| O-1 | Optional · OPTIONAL · h | `plan.md` «Estrategia», T1/T2/T7/T8 | **La forma no cumple el punto 7 de forma literal.** T1 y T8 son coordinación, porque el orquestador no es un rol en `VALID_ROLES`. T2 agrupa dos subfases y T7 dos roles (`owner: "implementer y reviewer…"`). La separación real se conserva en prosa, así que el efecto es de forma. No encontré autorización registrada del reencauce a «hitos»: la autoridad debe aceptarlo o dividir (T2a/b, T7a/b). |
| O-2 | Optional · OPTIONAL · h | `plan.md`, bloque `plan-tasks`; `stage-2-specification.md` §Task structure | No hay `consume`/`produce` ni PC por tarea; la cobertura va por promesa en la tabla de asignación. El interfaz T3→T4 (forma exacta del ancla) no está declarado. Remedio: nombrar la convención y el artefacto de inventario. |
| O-3 | Required · OPTIONAL · m | `spec.md` §2.4, PC-10; T3 | Verde vacío: un producto sin citas puede pasar «las referencias resuelven». El control debe rechazar cero referencias y enlaces a fuentes no inventariadas. Sin esto, T6 sigue cubriéndolo semánticamente. |
| O-4 | Optional · OPTIONAL · h | `plan.md`, T8 | `cdad-suite.py close` falla si `--evidence-root` no existe (`cdad-suite.py:891`), y `.cdad/evidence/010-003-closure` no existe. Añadir la creación previa del directorio. |
| O-5 | Consider · OPTIONAL · m | T5, spec §6 | La contaminación solo se detecta si es «declarada». Remedio: auditar en T5 las lecturas de la transcripción de sesión contra `oracle/`, `structural/` y `product/`. |
| O-6 | Consider · OPTIONAL · m | T7 | La re-verificación cubre solo hallazgos «afectados»; una afirmación nueva quedaría sin contraste. Debe cubrir todo el diff. |
| O-7 | Consider · OPTIONAL · m | T5 «Salida de fallo» | No se distingue una falla técnica sin informe (no consumió el ensayo) de un hallazgo faltante. Tampoco se define si cabe un corpus nuevo. Debe decidirlo la autoridad antes del ensayo. |
| O-8 | FYI · OPTIONAL · h | `discovery.md` §2 | Sus ejemplos ilustrativos anticipan respuestas plausibles. El test-writer no debería reutilizarlos sin más, y esa ruta debe quedar fuera de T5. La lectura exacta del contrato ya lo evita. |

## Verificación punto por punto

1. **Fidelidad:** D-2, D-3, D-4, D-5 y D-6 se respetan. D-1 tiene la tensión de orden de B-2.
2. **Contrato:** las 15 PC tienen vía de evidencia, y las semánticas exigen sesión real. PC-03 queda hueca por B-3; PC-11 y PC-13 por B-4.
3. **Clave y desafío:** se excluye a nivel contractual y de alcance, y las clases lo admiten (`tests` por raíz, `contract` por ruta exacta). **No lo impide de verdad**: la spec lo admite. Ver B-1, B-2, B-3 y O-5.
4. **Control estructural:** las tres muestras demuestran el límite y no dependen de líneas ni de `FAIL`. Ver O-3.
5. **Producto:** la separación, las dos posiciones y los pendientes están bien; el contraste de corrección no (B-4).
6. **Cierre:** los tres registros y los límites de PC-15 están completos.
7. **Ejecutable:** `_check_plan_tasks` pasa sobre las 8 tareas. Los hallazgos son O-1, O-2 y O-4. Comandos: pytest y `cdad-suite.py close` existen; sobre el HOME, ver Abstenciones.
8. **Riesgos:**
   - Verde leído como fidelidad: mitigado por T4 y PC-06; queda O-3.
   - Informe simulado: excluido expresamente.
   - Contaminación: B-1, B-2, O-5.
   - Postcondiciones más débiles que su promesa: PC-03, PC-07, PC-11.
9. **Defectos abiertos:**
   - **I-8:** riesgo real, porque el test-writer no lee `skills`, incluida la norma; el plan escala y no rodea.
   - **I-9:** usa el CLI del proyecto.
   - **I-10:** T4 no escribe en `skills`, así que no se dispara.
   - **I-11 e I-12:** respetados.
   - **I-13:** los tipos existen en `_allowed_kinds` (`review`, `test-audit`, `test-writer-role-report`, `implementer-role-report`); `artifact-policy.json` admite nombres propios bajo la raíz de la feature para `review`, por lo que `challenge-review.md` y `product-review.md` caben.
   - **Instalación global:** declarada, sin atribuirle obligaciones.

## Abstentions

- No probé un `prepare` real de T5, ni si los gates admiten `reviewer/review` antes de GREEN (afecta a B-2).
- No verifiqué si las regresiones focalizadas ejecutadas con pytest directo tocan el HOME real; el canario solo acompaña a la suite de cierre.
- No verifiqué qué hace efectivamente el guard de lectura sobre `read_scope` para un reviewer.
- `scripts/cdad_packet.py` y `skills/cdad-cycle/scripts/cdad_packet.py` difieren. No evalué esa diferencia; usé el primero para validar el paquete y las funciones del segundo para el check de `plan-tasks`.

## Evidencia

- **Archivos modificados:** ninguno. **Commit:** ninguno.
- **Tests:** no ejecuté tests ni la suite.
- **Comandos principales:** `scripts/cdad_packet.py validate-request`, `validate-packet` y `render` (también con `--route C`) sobre el REQUEST y el PACKET de este encargo; `sha256sum` de la carpeta de la feature; `_plan_tasks_from_contract` más `_check_plan_tasks` (8 tareas, sin diagnóstico); `git check-ignore` y `ls` de la ruta de evidencia.
