# Dictamen de plan-review: 010-002-documentary-role-integration

**Recomendación: NO está listo para aprobación.** Hay dos bloqueantes y ambos se cierran con cambios acotados en spec y plan, sin rediseño. D-1, D-3 y D-5 están bien encauzados.

**Objeto revisado**
- `plan.md`, versión 1: `f95e4378f100cdaca90a867efb5bf6b4d4de27f5cd65bbf12e8c9aa029c47155`
- `spec.md`, draft-1: `a9f15413ef9c29c4c0236a63d7308d9af5a78899083a37e4a556b81f39996e1d`

**Intake:** ruta C válida. Los hashes coinciden, el contexto es v2, `validate-request` y `validate-packet` dieron rc=0, y `render` es idéntico a `PACKET.md` (`cmp` rc=0). Esta revisión no aprueba nada ni autoriza implementar.

## Hallazgos bloqueantes

### B1. La aplicabilidad Odoo no opera para los roles que no escriben el producto
- **Severidad:** Required
- **Verdict:** BLOCKING
- **Bucket:** h
- **Ubicación:** `spec.md:44-57`, PC-04/05 (`:133-136`), INV-05 (`:172`). Mecanismo: `cdad_packet.py:1467-1474`. Obligaciones: `sources/roles/reviewer.md:110-113`, `test-writer.md:120-122`.
- **Fundamento:**
  - D-2 decide por «producto declarado y su alcance editable», pero solo el implementer tiene un alcance que describa el producto.
  - Reviewer y architect siempre tienen `write_scope` vacío; el test-writer solo escribe tests o temporales.
  - La tabla §D2 no dice cómo clasifican esos roles el encargo, ni qué hace un test-writer que escribe un verificador documental en un proyecto Odoo: ¿sigue obligado a `TransactionCase`?
  - Tampoco define la frontera de «addon» para documentación dentro del módulo (`readme/`, `static/description/`), que podría ser producto documental y a la vez caer en alcance de implementación.
- **Consecuencia:**
  - Un reviewer Odoo puede omitir `make test-clean` porque el encargo se llama «documental» aunque el diff toque el addon. Eso es justo la elusión que D-2 prohíbe y solo se ve al revisar.
  - O puede exigir la batería a un documento puro y dejar el bloqueo que D-2 quería retirar.
  - Los casos sintéticos de PC-04/05 no tienen un resultado esperado definido para estos roles.
- **Condición de cierre:**
  1. La spec define la aplicabilidad de cada rol sin escritura de producto. El reviewer decide por el contrato aprobado y el **diff real**, y el diff prevalece sobre cualquier etiqueta.
  2. Define el régimen del verificador documental escrito por el test-writer.
  3. Define qué rutas cuentan como addon, incluida la documentación dentro del módulo.
  4. PC-04/05 enumeran los resultados esperados por rol en los casos documental, addon y mixto.

### B2. Queda una promesa contradictoria de selección fuera del alcance de T4
- **Severidad:** Required
- **Verdict:** BLOCKING
- **Bucket:** h
- **Ubicación:**
  - `skills/cdad-cycle/SKILL.md:136`: «Absence of `stack`, or another value, → generic agents».
  - `sub-agent-strategies.md`, §Activation by stack: «`stack` absent or with another value → delegation goes to the generic agents».
  - Frente a `plan.md:317` y `:97-99`, y las referencias de `spec.md:226`.
- **Fundamento:**
  - El mecanismo real publica `cdad-<role>-<stack>` para cualquier cadena no vacía (`cdad_packet.py`, `_packet_agent`). «Otro valor» no va al agente genérico.
  - `SKILL.md` no figura en la lista de archivos de T4 ni en las citas de la spec.
  - Es la misma contradicción que D-4 ordena eliminar, y la frase de `sub-agent-strategies.md` es más amplia que la que cita la spec.
- **Consecuencia:**
  - Una instrucción canónica seguiría prometiendo la sustitución que PC-08 y PC-09 prohíben.
  - Si el implementer la corrige, se sale de los archivos del plan y T4 falla el gate de «diff conforme».
  - Si no la corrige, una prueba completa de PC-09 no puede pasar.
- **Condición de cierre:** añadir `skills/cdad-cycle/SKILL.md` a las citas de la spec, a T4 en prosa y a `plan-tasks`, con la cláusula «otro valor» corregida en ambas superficies. `TestDispatchDoctrine` debe cubrir esa formulación, no solo las líneas ya citadas.

## Hallazgos no bloqueantes

### O1. Un rechazo en la validación compartida alcanza más que un despacho nuevo
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `spec.md:66,213`; `plan.md:368`. Llamadores: `cdad_result.py:674,1362`, `cdad_packet.py:2137,3331,3827,10233,10374`, `cdad_continuity.py:1257`.
- **Fundamento:** `validate_request` también se ejecuta al recibir resultados y en verificación y continuidad. La spec solo describe el rechazo antes del render validado o del registro.
- **Consecuencia:** si `stack` cambia durante una ejecución, un paquete ya despachado podría dejar de recibirse. La spec no decide ese comportamiento.
- **Condición de cierre:** declarar en la spec si `receive` y continuidad también fallan cerrados, y cubrir la decisión con un test.

### O2. Borrar `agent` esquiva el fail-closed
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `spec.md:70`; INV-04 «cuando existe» (`:171`).
- **Fundamento:** quitar el campo deja el render idéntico y la validación sigue pasando.
- **Sonda sobre los 864 requests reales:**

| `execution_context` | `agent` | Requests |
|---|---|---|
| ausente | ausente | 592 |
| ausente | presente | 229 |
| presente | presente | 43 |
| presente | ausente | 0 |

- **Consecuencia:** un request nuevo alterado a mano evita el rechazo. Aun así, la forma es de bajo coste de cierre: el request publicado no refleja lo validado por D-3.
- **Condición de cierre (recomendada):** exigir `agent` cuando exista `execution_context`, lo que no afecta a ningún histórico. Si no, declarar el límite en `deferred-hardening`.

### O3. El rechazo de variante no publicada no dice en qué superficie ocurre
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** PC-08 (`spec.md:142`), `plan.md:351`.
- **Fundamento:**
  - `prepare` no comprueba si la variante existe; quien rechaza es el adaptador externo (`cdad_delegate_opencode.py:417-458`).
  - T6 solo toca `cdad_packet.py` y el esquema.
  - `record-dispatch` no comprueba publicación en el tramo revisado.
- **Consecuencia:** PC-08 puede leerse como una garantía universal que en sesiones nativas es solo instrucción.
- **Condición de cierre:** PC-08 declara que el rechazo es mecánico en el adaptador externo y procedimental en la vía nativa.

### O4. El gate de T4 pide verde lo que depende de T6
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** PC-12 (CLI y esquema «corregidos», `spec.md:161`); `plan.md:112`; `plan.md:382`.
- **Consecuencia:** `TestDistribution` no puede cubrir en T4 los bytes corregidos que entrega T6. O el test es débil, o el gate queda rojo por diseño.
- **Condición de cierre:** dividir PC-12: T4 cubre agentes, skills y referencias; T6/T7 cubren CLI y esquema.

### O5. La aceptación del epic no queda trazada
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `plan.md:75-78` del epic; PC-12.
- **Fundamento:** la spec nunca dice que «perfil documental» sea la especialización por contrato de D-1. Tampoco compromete expresamente el recorrido de un encargo documental con `stack=odoo`.
- **Condición de cierre:** añadir esa equivalencia y el caso documental/Odoo a PC-12 y EV-04.

### O6. Las regresiones difieren entre la prosa y `plan-tasks`
- **Verdict:** OPTIONAL
- **Bucket:** l
- **Ubicación:**
  - T4: la prosa (`plan.md:328`) cita permisos e instalación; `plan-tasks` no lista esas pruebas.
  - T6: la prosa (`:370`) cita el adaptador externo; `plan-tasks` (`:163-167`) omite `test_006_005_u2_opencode_module.py` y `test_role_packet_render.py`.
- **Condición de cierre:** alinear ambas listas.

### FYI. Deriva de publicación
Las cláusulas Odoo viven en agentes y skills, no en el paquete. Según `closure.md` §5 de 010-001, siguen sin llegar a las sesiones que usan la instalación global hasta que el dueño publique. Las exclusiones de la spec lo cubren, pero el cierre debe volver a declararlo.

## Verificación por objetivo

| # | Objetivo | Resultado |
|---|---|---|
| 1 | Postcondiciones verificables | Sin confusión entre estructura y fidelidad. PC-04/05 quedan condicionadas a B1. |
| 2 | D-1..D-5 sin ampliar alcance | Sin agentes, campos, selectores ni permisos nuevos. D-2 falla por B1 y D-4 por B2. |
| 3 | Cláusula Odoo | No se cumple: B1. Para el implementer la mezcla sí es operable, porque admite `implementation` y `docs` a la vez. |
| 4 | Compatibilidad de D-3 | Los requests sin `agent` y el render se conservan. Quedan O1 y O2. |
| 5 | Corrección del esquema | Mínima. La sonda añadió `agent` y `execution_context` en memoria y los 864 requests validaron. `execution_context` ya se trata en el CLI y el esquema no sustituye al validador. |
| 6 | Separación RED/GREEN | Correcta, con archivos y gates nombrados y sin prometer sesiones vivas. Queda O4. |
| 7 | Contradicciones | B2, O5 y O6. |
| 8 | Riesgos de diseño | T4 no toca `packets/roles`, así que el techo estático no se mueve. `jsonschema` 4.19.2 está disponible aquí. `build/staging` está ignorado por git. Los directorios bajo `docs` no chocan con la exigencia de declarar rutas exactas. |

## Abstenciones
- **Fixtures con agente discordante:** no ejecuté la suite ni un parche simulado. No puedo afirmar qué fixtures existentes declaran un `agent` incompatible con su estado. Si alguno lo hace, T6 lo descubriría tarde, porque el implementer no puede editar tests. Conviene que el AUDIT de T2 lo mida.
- **Obligaciones en `references/`:** `skills/odoo-expert/references/evidence-and-quality.md` y varias referencias de `odoo-make-env` mencionan esas pruebas. No determiné si son incondicionales y por eso no lo clasifico como hallazgo. El AUDIT debería confirmarlo, porque T4 no las incluye.
- **Mutabilidad real de `stack`:** no verifiqué con qué frecuencia cambia dentro de una ejecución. Eso limita la probabilidad de O1, no su falta de definición.
- **Librería de propiedades:** `hypothesis` no está instalado. El plan no la exige, así que T7 debe resolver su generador con semilla antes de empezar.

## Evidencia
- **Archivos modificados:** ninguno.
- **Commit:** ninguno; `HEAD` es `3bea7a8d356e35ccb93d22d010632f1d7e7406bf`.
- **Comandos:**
  - `python3 -B scripts/cdad_packet.py validate-request|validate-packet|render --project-root . --request <REQUEST.json>`; `validate-packet` añade `--packet <PACKET.md>`.
  - `sha256sum` sobre `plan.md` y `spec.md`.
  - `python3 -B` en memoria: requests contra el esquema y conteo de `agent`/`execution_context`.
  - `grep` y `sed` sobre las rutas citadas.
- **Salidas:** `vr=0`, `vp=0`, `cmp=0`; esquema `Counter({'ok': 864})`; substages faltantes `set()`.
- **Suite completa:** no ejecutada; este paquete no la pide.
