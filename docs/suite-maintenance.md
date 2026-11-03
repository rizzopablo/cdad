# Mantenimiento de la suite

Documento operativo del proyecto. La sección fija `## Inventario vivo`
es la declaración consumida por el orquestador (013-002 PC-7).

## Inventario vivo

Declaración del proyecto (013-002-live-inventory, PC-7):

- **Comando de integridad:** `python3 scripts/cdad-suite.py validate`.
- **Inventario:** `docs/specs/008-002-suite-by-capability/suite-inventory.json`.
- **Mapa:** `docs/specs/008-002-suite-by-capability/pc-map.json`.

Son instrucciones documentales consumidas por el orquestador, no un nuevo
esquema de política ni una interfaz de detección automática.

El orquestador lee esta sección en los re-entries de cambios de tests y
transmite la regla aplicable en los handoffs correspondientes, tanto por
la ruta legacy como por paquetes.

Si falta el documento o la sección, la regla condicional no aplica y el
orquestador registra explícitamente **«sin inventario vivo declarado»**,
sin bloquear por esa ausencia. No presume rutas ni comandos.

### Vocabulario: clasificación vs acreditación

Para evitar confundir presencia de campos y verde estructural con
protección semántica (PC-4):

- **asignación** a capacidad y contrato: qué nodeid pertenece a qué
  capacidad y con qué contrato recuperable. `confidence` del inventario
  y `validate rc=0` no acreditan protección semántica.
- **obligación** y **variante** asociadas a un test: qué debe conservarse
  y qué resultado observable distingue una variante de otra.
- **acreditación** y **evidencia** de esa asociación: qué revisión
  independiente contrastó la asignación contra contratos y tests, con
  fuentes, hallazgos e incertidumbres declaradas.
- **incertidumbre** declarada: lo que aún no se sabe o no se cubre; una
  incertidumbre que afecte a una sustitución bloquea esa sustitución, no
  obliga a inventar acreditación global.

Las disposiciones se consumen desde 013-001/R2, sin definiciones nuevas.
Los valores legacy `decision` del inventario y mapa permanecen
diferenciados de la disposición única del AUDIT.

En particular, un registro legacy `eliminar` **no significa
automáticamente Retirar**: puede representar la eliminación física de un
origen sustituido cuya obligación continúa vigente.

Los 29 registros preexistentes del mapa no se presentan como 29 tests ni
como acreditación de toda la suite.

### Altas ordinarias y materialización (PC-7)

En RED, properties y E2E, el test-writer entrega en su informe un delta
de altas que identifica, para cada nodeid nuevo:

- nodeid.
- capacidad.
- contrato.
- procedencia de la asignación.

El delta es texto para materialización; el test-writer no escribe el
inventario documental. El orquestador lo materializa al re-entry,
**antes de la siguiente transición**.

Los cambios de orígenes o destinos incorporan además el delta del mapa
de PC-6. POST-AUDIT devuelve los deltas documentales pertinentes bajo la
misma separación de responsabilidades.

Materializar el delta no equivale a exigir `validate rc=0` en los pasos
no bloqueantes. La desactualización residual queda visible y debe
resolverse antes de entrar a Review.

### Sustitución y genealogía del piloto (PC-6)

Procedimiento entregado a 013-003 para cada sustitución, con los
mecanismos existentes y sin crear fase, receptor ni gate:

1. AUDIT identifica la revisión anterior y los registros afectados.
2. El test-writer propone el delta de tests y mapa, con la disposición
   de 013-001 y sus evidencias.
3. POST-AUDIT ejecuta el mantenimiento autorizado y devuelve los deltas
   documentales como texto; no adquiere permiso para editar documentos.
4. El orquestador materializa esos deltas al re-entry, antes de la
   siguiente transición.
5. La revisión independiente contrasta el mapa anterior, los tests y los
   destinos actuales antes de aceptar la sustitución.

Reglas de lectura e identidad:

- Los paquetes del test-writer que necesiten consultar el mapa deben
  declararlo expresamente en su `read_scope`, además de identificar la
  revisión anterior pertinente. Esa lectura no autoriza a usar el
  producto futuro como oráculo.
- No se identifica una obligación únicamente por su nodeid: se
  consideran contrato, identificador y variante.
- Se conserva el origen histórico. Si un destino vuelve a sustituirse,
  las obligaciones anteriores siguen llegando a un destino actual
  recolectable y la evidencia permite recuperar los pasos intermedios
  (cadena de re-sustitución).
- Cuando sean necesarios varios destinos, los registros explicitan qué
  parte conserva cada uno y la revisión contrasta el conjunto. No se
  introduce un valor de lista incompatible en `target_nodeid` (sigue
  siendo cadena; varios destinos se desglosan en registros, sin lista
  en `target_nodeid`).

Los registros históricos existentes —incluidos sus `VERIFY` y
placeholders declarados— no desaparecen para lograr verde. Una
incertidumbre que afecte a una sustitución bloquea esa sustitución, no
obliga a inventar acreditación global.

### Momentos de comprobación (PC-7)

| Momento | Obligación de mantenimiento | Efecto de `validate` |
|---|---|---|
| Re-entry de RED | Recibir y materializar el delta de altas antes de la siguiente transición | **No bloquea RED** ni exige rc=0 para acreditarlo |
| Re-entry de properties | Recibir y materializar el delta de altas antes de la siguiente transición | **No bloquea properties** ni exige rc=0 para acreditarlo |
| Re-entry de E2E | Recibir y materializar el delta de altas antes de la siguiente transición | **No bloquea E2E** ni exige rc=0 para acreditarlo |
| Re-entry de POST-AUDIT | Materializar los deltas pertinentes y registrar la desactualización detectada | Un resultado no cero **no bloquea por inventario**; no elimina los requisitos de conservación de PC-6 |
| Re-entry de GREEN | Comprobar y registrar la desactualización respecto de la revisión recibida | Un resultado no cero **no bloquea por inventario** |
| Entrada al gate existente de Review | Exigir inventario actualizado y mapa actualizado cuando corresponda | **Bloquea** si falta evidencia pertinente o `validate` no termina con rc=0 |
| Cierre | Confirmar la integridad sobre la revisión candidata final | **Bloquea** si falta evidencia pertinente o `validate` no termina con rc=0 |

Cuando se ejecute el comando en los pasos no bloqueantes, su resultado se
registra sin convertirlo en condición de verde de esa subfase. La ausencia
de exigencia de rc=0 no dispensa de entregar y materializar los deltas ni
de registrar la desactualización.

En la entrada a Review y en el cierre, rc=0 se mide sobre la revisión que
**ya contiene los deltas materializados y los últimos cambios de tests**.
Un resultado anterior a esos cambios no acredita la revisión posterior.

La aceptación exige además contraste independiente de conservación cuando
haya sustitución. Las demás condiciones de los gates existentes mantienen
su fuerza.

No se crea otra fase, receptor ni gate. La obligación no depende de
ejecutar el gate completo de CI y se aplica aunque los datos resultantes
estén bajo `docs/`.

### Datos comparables y contadores estáticos (PC-3)

`static_test_nodeids` es un contador auxiliar estático: no es colección
efectiva, no se actualiza por corrida y no se presenta como tal. Ejemplos
medidos en esta revisión: `tests/test_007_004_termination_not_success.py`
declara 18 y recolecta 69; `tests/test_005_013_t1_unit_projection.py`
declara 14 y recolecta 18. La colección efectiva se obtiene al verificar
(`python3 -m pytest tests --collect-only -q` y
`python3 scripts/cdad-suite.py validate`); unos 30 módulos preexistentes
conservan ese campo distinto de la colección real y se declaran aquí como
históricos, sin actualizarlos por esta unidad.

La cabecera del inventario
(`draft T1 (test-writer audit); clasificacion por modulo; sin pc-map`)
es histórica: describe la auditoría T1, no el estado vigente. No se
reescriben mediciones históricas para aparentar actualidad; el estado
vigente se registra aquí.

Registro PC-3 (medido por el implementer, revisión
`bd84ed5b14295970dbcb75cc22cd53620f43d681`, árbol limpio):

- Revisión: `bd84ed5b14295970dbcb75cc22cd53620f43d681`.
- Comando y configuración de colección:
  `python3 -m pytest tests --collect-only -q` (1949 tests) y
  `python3 scripts/cdad-suite.py validate` (rc=0).
- Cantidades efectivas: 1949 nodeids, 232 módulos inventariados, 31
  entradas en el mapa, 0 pendientes estructurales (`status: ok`, sin
  nodeids sin asignar ni módulos inexistentes).
- Diferencias respecto del punto de partida (1942 nodeids, rc=1):
  +7 nodeids (los 7 focales de 013-002); `validate` pasa de rc=1 a rc=0
  tras materializar inventario, mapa y deltas.
- Deuda explícita del helper `tests/_rf2_open_pause.py`, aparte: contrato
  literal `VERIFY`, confianza baja; no es asignación recuperable ni
  acreditación; su resolución requiere contrato real y no se acredita
  por `validate rc=0`. Ver `### Deuda explícita del helper`.

Revalidado tras materializar los deltas de esta corrección con idénticos
valores (1949/232/31, rc=0); el cierre confirma la integridad sobre la
revisión candidata final con esos mismos comandos.

### Límites de los controles (PC-8)

La entrega y sus instrucciones distinguen:

- `validate`: integridad estructural.
- contraste del mapa anterior: conservación documental. La revisión
  independiente contrasta el mapa anterior, los tests y los destinos
  actuales antes de aceptar una sustitución.
- revisión independiente y evidencias de tests: protección semántica
  acotada.

No se afirma que `surface`, `close` o el gate de CI ya ejecuten
`validate`: el código inspeccionado no lo hace.

Tampoco se atribuye al chequeo histórico de conservación una garantía
que no presta: su baseline puede carecer de mapa y su comparación usa
únicamente el origen. El contraste de PC-6 debe usar una revisión que sí
contenga los registros anteriores.

Un cambio en el inventario o el mapa hace que `surface` seleccione toda
la colección. Para inspeccionar esa selección se usa `--collect-only`;
para evidencia focal se ejecuta una selección explícita. Ejemplo:

```sh
python3 scripts/cdad-suite.py surface --base HEAD --collect-only
python3 scripts/cdad-suite.py validate
```

La colección no es una ejecución de todos los tests. Que
`surface --collect-only` seleccione toda la colección tampoco autoriza
ejecutarla. La selección completa se rige por los defaults por momento del hogar canónico
`skills/cdad-cycle/references/stage-3-tdd.md` §"Test evidence policy" (Durante el ciclo sin completa
como rutina; Cierre de feature recomendada; Cierre de epic obligatoria por defecto o dispensa expresa):
sin autorización suficiente para esa corrida no se ejecuta una selección completa producida por
`surface`. La autorización para una corrida completa debe ser suficiente para esa corrida; sin
ella se registra suite completa no realizada.

### Deuda explícita del helper

`tests/_rf2_open_pause.py` conserva como deuda explícita su contrato
literal `VERIFY` con confianza baja. No se presenta esa asignación como
contrato recuperable ni como acreditación. Su resolución requiere
identificar y contrastar un contrato real; no se acredita por
`validate rc=0`.

- Contrato: `VERIFY` (pendiente, no recuperable).
- Procedencia: instrumentación A-3 review-fix 2 declarada en su docstring.
- Estado: deuda visible, separada de asignaciones estructurales
  pendientes y de acreditación semántica.
