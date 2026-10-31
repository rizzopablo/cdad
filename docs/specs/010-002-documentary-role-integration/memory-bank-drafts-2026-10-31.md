Validé la ruta C contra el paquete publicado antes de trabajar. Entrego los cuatro borradores y el informe.

---

# Validación previa (ejecución de intake)

| Comprobación | Comando | Resultado |
|---|---|---|
| Contrato pineado | `sha256sum docs/specs/010-002-documentary-role-integration/spec.md` | `0d630c49cfd4c8b0f671026437000617b96bf1bc44b2383dd2914bc7e5581abc` — coincide con la identificación |
| Paquete válido | `python3 scripts/cdad_packet.py validate-packet --project-root . --execution-context .cdad/executions/exec-010-002-documentary-role-integration-001/execution.json --request .cdad/packets/010-002-documentary-role-integration-scribe-memory-001/REQUEST.json --packet .cdad/packets/010-002-documentary-role-integration-scribe-memory-001/PACKET.md` | `rc=0` |
| Identificación ruta C | `python3 scripts/cdad_packet.py render --project-root . --execution-context … --request … --route C` | idéntica byte a byte al bloque recibido |
| Contexto de ejecución | `python3 scripts/cdad_packet.py status --project-root .` | `schema_version: 2`, aprobación `vigente` para rol `scribe`, `contract_sha256` coincide |

Un solo bloque de identificación, sin cuerpo inline, sin mezcla A+C, sin cargar skills de ciclo. Write scope vacío: **ningún archivo modificado**.

---

# DRAFT 1 — `docs/activeContext.md` (entrada nueva, va arriba de `## 2026-10-31 — Feature: 010-001-documentary-contracts`, línea 7)

```markdown
## 2026-10-31 — Feature: 010-002-documentary-role-integration (epic 010, orden 3 del plan)

**Cierre técnico declarado y aceptación funcional registrada por mandato; NO aprobado
directamente por el dueño y NO publicado.** `closure.md` declara el cierre con su
medición de suite completa, y `owner-acceptance-2026-10-31.md` registra la aceptación
funcional del entregable y la aprobación de este Memory Bank, ambas ejercidas por el
orquestador bajo el mandato HITL del 2026-10-30 (§1 y §3) que cubre los gates del
epic-010. Contrato: `docs/specs/010-002-documentary-role-integration/spec.md`, pin
`0d630c49…81abc` (v4); plan v4 `3ead624c…1190`. Este cierre no publica, no hace push y
no actualiza la instalación global. La aprobación es recuperable en el estado del
proyecto; el encabezado de `spec.md` conserva la leyenda de borrador (N2 del dictamen
de T8, no bloqueante).

**Qué se cerró.** Un encargo cuyo producto es un documento —relevamiento, mapa de
proceso, historia de usuario— ya tiene **procedimiento operativo** sin inventar
mecanismo: se expresa con los campos que el encargo ya lleva (`objective` y promesas,
`expected_output`, `inputs`/`read_scope`, `write_scope`, `invariants` y alcances,
`evidence_required` con límites y pendientes). **No se creó** agente, rol, etapa,
subfase, campo del estado ni selector documental, y `stack` conserva su significado de
dominio. El procedimiento vive en `skills/cdad-cycle/references/handoff-prompts.md`
(`## Documentary engagement — operating procedure`: siete declaraciones, pasos de
preparación y de re-entry, parada ante superposición con insumos protegidos) y **remite**
a la casa normativa de `010-001` sin reproducirla.

Se incorporó la **aplicabilidad Odoo por rol y por producto o diff real**. Dentro de un
módulo, el trabajo de addon es `models/`, `views/`, `controllers/`, `wizards/`,
`security/`, `data/`, `static/src/`, `__manifest__.py` y el código o recurso funcional
equivalente (imports, hooks, archivos Python de ejecución, informes, `wizard/`,
`report/`); la documentación del módulo —`readme/`, `static/description/`, `README.rst`,
`doc/`— es **producto documental** salvo que el contrato la declare parte del entregable
funcional. La base de decisión es por rol: el architect se ata al producto propuesto en
el contrato y sus alcances (nunca a su propio `write_scope`, que está vacío); el
test-writer, al producto y las promesas que verifica (nunca al hecho de escribir tests);
el implementer, al producto aprobado y su `write_scope`; el reviewer y el orquestador, al
contrato **y al diff real**, que prevalece sobre la etiqueta. Esta frontera delimita
obligaciones y **no** cambia la clasificación de rutas de la política, los permisos ni los
alcances admitidos. Un verificador documental **no** es un test de addon: no exige
`TransactionCase` ni `@tagged`, corre por el runner declarado del proyecto y, si ese
runner no lo cubre, el encargo **declara el límite de evidencia** sin emitir comandos
crudos ni ampliar permisos.

Se cerró la **coherencia del destinatario** en dos niveles con momentos distintos.
Contraste **estático** agente↔rol, en la validación compartida (`validate-request`,
`render`, `validate-packet`, `receive`, `prepare` y reemplazo): `cdad-<role>` exacto o
prefijo completo `cdad-<role>-` con sufijo no vacío; un agente de otro rol no valida ni
produce render válido, y el diagnóstico nombra rol, agente recibido y familia esperada
declarando que el stack no se evalúa. Contraste **contextual** rol/stack/agente, solo en
dos límites: publicación de un request nuevo —ordinaria o por `prepare --replace-packet`—
y registro de un intento nuevo de despacho con `agent` declarado. `--replace-packet`
**rederiva** el agente del rol y del stack vigente y deja de copiar el del predecesor:
un predecesor histórico sin agente produce un sucesor con agente derivado y un cambio de
`stack` produce un sucesor acorde al dominio vigente, sin reescribir bytes históricos.
La regla de presencia quedó explícita: `execution_context` exige `agent`. La distinción
temporal protege la continuidad sin abrir reutilización: recepción de un paquete ya
despachado, repetición idempotente de un registro idéntico y finalización válida del
write-ahead **no** se reevalúan contra el stack vigente; un intento nuevo con agente
declarado sí. Un histórico admitido sin contexto ni agente puede registrar un intento
nuevo sin contraste contextual del destinatario y **sin** derivar ni sustituir agente en
silencio. En la vía nativa la comprobación de publicación es **deber procedimental** del
orquestador; la guarda mecánica pertenece solo al adaptador externo. El esquema publicado
del request (`agent` y `execution_context`, `additionalProperties: false`,
`dependentRequired`) **describe forma** y no sustituye al validador contextual.

**Decisiones relevantes.**

- **Especialización documental por contrato, con los seis roles y los campos
  existentes.** Motivo: el transporte actual expresa producto, fuentes, producto
  editable, verificadores protegidos, evidencia y límites sin multiplicar resolución,
  clasificación y distribución. Trade-off aceptado: la obligación vive en superficies
  compartidas —fuentes de rol, cinco bloques estáticos de `packets/roles/`, referencias
  de despacho, cinco skills Odoo con su inventario de referencias y los 22 agentes
  derivados— y ninguna sustituye a otra; el generador **no** compone la tabla §2 de
  `SKILL.md`, que se corrige a mano.
- **La frontera de addon es una delimitación de obligaciones, no un permiso.** Su casa
  única es `skills/odoo-expert/SKILL.md` (`## Addon work vs. module documentation`) y los
  demás consumidores la citan; el architect conserva conocimiento funcional, criterio de
  configuración primero y `VERIFY`, y solo se le exigen inventario core/OCA y entorno de
  pruebas cuando propone **modificar** un addon. Trade-off declarado: la palabra clave no
  acredita la legitimidad de una exclusión; quien decide es el contrato o el diff, y un
  addon oculto bajo etiqueta documental se informa y **bloquea** su aceptación como
  documental puro, sin permiso retroactivo.
- **Dos niveles de coherencia en lugar de un contraste único.** Se descartó validar solo
  al despachar —dejaría renderizar agentes de otro rol— y se descartó comparar el stack
  vigente en toda lectura —invalidaría continuidad histórica legítima—. Trade-off
  aceptado: un cambio de `stack` puede bloquear un intento nuevo del paquete anterior sin
  invalidar por ese motivo su recepción, su repetición idéntica ni la finalización de su
  write-ahead; el reemplazo legítimo publica un sucesor rederivado. Consecuencia
  registrada: **N7**, un paquete `prepared` sin otra obsolescencia queda sin salida
  directa tras cambiar el stack; se acepta **fail-closed** con tres salidas legítimas
  (restituir el `stack`, producir la obsolescencia legítima o retirar con `withdraw`).
- **Garantía por construcción en las dos vías públicas de publicación.** La preparación
  ordinaria y el reemplazo publican el agente derivado; la verificación observa el valor
  publicado. No se atribuye a `prepare` una rama de rechazo de agente inyectado que su
  interfaz pública no permite alcanzar.
- **El esquema declara los campos admitidos y su dependencia estructural**, preservando
  la admisión histórica sin ambos campos y la exclusión de `agent` del render entre
  requests válidos. Trade-off: no se promete paridad total JSON Schema↔CLI contextual
  —el esquema carece de archivos, estado y autoridad— y esa paridad queda en
  `deferred-hardening`.
- **Un verificador documental se ejecuta por el runner declarado del proyecto.** Precisión
  incorporada al cerrar B2 (P-5, no presente en la spec original, declarada como tal en la
  re-revisión): evita que la prohibición de comandos crudos del test-writer obligue a
  fabricar un test de addon para un verificador documental, y prohibe que la salida sea
  ampliar permisos.

**Evidencia.** Cuatro pasadas de `plan-review` (v1 con dos bloqueantes —aplicabilidad
Odoo fuera de los roles sin escritura de producto, y promesa contradictoria de
selección—, v2 sin bloqueantes con N1–N4, v3 con un bloqueante nuevo —el reemplazo copiaba
el agente—, v4 sin bloqueantes y recomendación de aprobación). AUDIT aprobado con
resolución de alcance. RED/GREEN por tarea: T4 con `13 passed` en los grupos
`TestEngagement`, `TestOdooApplicability`, `TestDispatchDoctrine` y `TestDistribution`, sin
tocar tests; T6 con la derivación canónica única, los dos contrastes y la regla de
presencia en `cdad_packet.py` y las dos propiedades del esquema. Review de T8 con **tres
bloqueantes**: **B1** —los adaptadores nativos prometían un rechazo mecánico inexistente—,
**B2** —los deltas Odoo de reviewer, implementer y test-writer conservaban la batería de
addon incondicional— y **B3** —el registro de I-10 omitía que el registro del despacho
corrió durante la restitución—. Los tres se cerraron **con los controles escritos antes de
la corrección** (`735d977c`: 13 archivos, +106/−30) y `review-002.md` los declara
**B1–B3 cerrados, sin bloqueantes nuevos**, con ocho mediciones propias (58 passed,
`make agents` ×2 con hash idéntico, `diff -rq` sin diferencias, `git diff … -- tests`
vacío, `validate-state` VALID).

Suite de cierre en **dos intentos, ambos conservados**: el intento 1 (`35b81093`) dio
**rc=1 — `4 failed, 1914 passed, 5 skipped`** en 1:06:07 con `canary_delta_lines: 18`, y
encontró **cuatro regresiones estructurales** que el resto de la verificación no había
ejecutado, todas introducidas por esta unidad en superficies compartidas: `005-006` PD-10
(la fila que invoca el CLI instalado quedó en la 473, fuera de la ventana `(444, 464)`,
por +9 líneas netas en `SKILL.md` §3.1), dos controles de `006-002` PD-2(b) (la
asociación `subagent_type` ↔ mapeo quedó partida por un salto de línea) y `F007` del
validador consolidado (el rewrap eliminó «resolve the stack»). Se corrigieron en
`cc6dad54` (5 archivos, +29/−42) **sin editar ningún test**. El intento 2 (`d37227ea`,
`--evidence-root .cdad/evidence/010-002-closure-2`) dio **rc=0**, **1923 nodeids**,
`1918 passed, 0 failed, 0 errors, 5 skipped` en 1:10:04, `dirty 1` y
**`canary_delta_lines: 0`**; los 5 skips son los condicionados por entorno ya declarados
en el cierre de `010-001`. Verificación de la unidad: módulo `29 passed`, propiedades
`7 passed` (semilla `20261031`), generador + `010-001` + techo estático `23 passed`,
aceptación hermética `pd8b` `1 passed`; `make agents` ×2 con hash idéntico
(`7f9c2d65…`), 22 agentes, ninguno editado a mano. Fuentes:
`docs/specs/010-002-documentary-role-integration/{spec.md, plan.md, closure.md,
closure-suite-attempt-001.md, owner-acceptance-2026-10-31.md, owner-approval-2026-10-31.md,
review.md, review-002.md, review-fix.md, review-fix-002.md, test-audit.md,
tdd-t4-green.md, tdd-t6-green.md, tdd-t7-properties.md,
deviation-green-accreditation-2026-10-31.md}`.

**Deuda técnica detectada.**

- **`deferred-hardening` de la spec §9 (seis ítems, ninguno aplaza una promesa
  comprometida):** validación semántica automática universal (la estructura no demuestra
  fidelidad; sigue la revisión independiente); paridad total JSON Schema↔CLI contextual
  (el esquema carece de archivos, estado y autoridad); sesiones vivas en ambos runtimes o
  en una instancia Odoo (se acreditó integración distribuible y fixtures aislados);
  sellado criptográfico histórico de `agent` o snapshot nuevo de `stack` (requeriría otro
  contrato y transporte); guarda mecánica nueva para variantes ausentes en la vía nativa
  (se comprometió doctrina procedimental); cobertura exhaustiva, rendimiento y
  combinatoria sin consecuencia contractual. Registros de disposición en `closure.md` §8.
- **I-10 (nuevo, defecto del mecanismo): la identidad del paquete no está pineada a sus
  fuentes de instrucción.** `render_packet` lee `packets/{common,roles/<rol>,
  substages/<rol>-<subfase>}.md` del árbol vivo en cada corrida, así que un encargo
  autorizado a escribir `skills` invalida su propio paquete en cuanto el trabajo aterriza.
  El GREEN de T4 modificó `packets/roles/implementer.md` y `record-dispatch` y `receive`
  dejaron de reconocer un paquete **no alterado**. Se acreditó con el árbol restituido a
  los bytes que la cabecera declara (`d93b44e4…`, recuperables de `0d935bc8`),
  restaurándolo de inmediato y sin tocar `PACKET.md` ni `REQUEST.json`; los sellos
  (dispatch `09:45:32.48`, `received_at` `09:45:47.98`, receipt `09:45:48.006`, bloque de
  rol `09:45:48.129`, entrega `09:45:58`) son consistentes con esa secuencia, que corre en
  un solo script con `trap` y por eso no deja huella propia. **Es una excepción a una
  guarda fail-closed, no práctica reutilizable:** una recurrencia exige corregir I-10 o una
  decisión del dueño. Documentado en `deviation-green-accreditation-2026-10-31.md` y
  verificado por la re-revisión; en el backlog con dos correcciones posibles (verificar
  los `sha256` declarados y fallar «instruction source drifted», o comparar contra un
  render pineado al conjunto declarado).
- **I-11 e I-12 (nuevos, oráculos heredados de otras unidades):** `005-006` PD-10 ubica los
  puntos de cableado del CLI por rango de líneas de `SKILL.md` —la fila estaba en el
  último renglón de la ventana—; `006-002` PD-2(b) exige dos conceptos en la misma línea y
  a ≤80 caracteres. Ambos fallan con un rewrap legítimo aunque la promesa esté intacta.
  Condición de cierre registrada: localizar por contenido y comparar por bloque
  normalizado, en unidades propias sobre esos contratos.
- **El canario no distingue la suite de otro gestor de agentes.** La deriva de 18 líneas del
  intento 1 era el servidor de OpenChamber reescribiendo el agente instalado
  `cdad-implementer.md` de su propia instalación (journal `13:42:29/36`), no una escritura
  de la suite. El intento 2, en una ventana sin esa escritura, dio `0`. El canario mide el
  entorno; el límite queda declarado.
- **Deriva de la instalación global, declarada y no oculta:** los 22 agentes derivados **no
  alcanzan la instalación global** mientras no se publique. Hasta entonces la obligación
  llega por el paquete y por la toolchain del repositorio, no por el agente instalado.
  Publicar es decisión del dueño; esta unidad no publica ni hace push.
- **Heredados sin cambios:** **I-8** (el test-writer no puede leer sus propios
  `instruction_sources`: `skills` es `implementation_root` y el guard deniega; se repitió en
  T7, que leyó su doctrina por bash y lo declaró) e **I-9** (dos copias del skill componen
  paquetes distintos, con el CLI instalado declarando hashes viejos). **N1/N2/O4** de
  `010-001` siguen diferidos al piloto; **O2/O4** de esta unidad (condición «addon code» más
  estrecha que la frontera amplia de `odoo-expert`, y método de comprobación de publicación
  del agente sin fijar) quedan como nits diferidos, sin habilitar ninguna rebaja. También
  queda **O1** de la re-revisión: `docs/epics/epic-010-documentary-specialization/execution.md`
  sigue describiendo la acreditación como una comparación y conviene alinearlo.
- **Límites que no se convierten en garantías:** un verde estructural —incluidos los 36
  tests de la unidad— **no** acredita fidelidad semántica de un documento real ni conducta
  efectiva de modelos; los contrastes son mecánicos en el CLI y en el adaptador externo y
  solo procedimentales en la vía nativa; el esquema describe forma; la aceptación funcional
  es de la autoridad que aprueba, aquí ejercida por mandato.
- **Lección de proceso:** **los oráculos existían; lo que falló fue ejecutarlos.** Una
  unidad que edita `SKILL.md` o los adaptadores debe incluir en su verificación los
  oráculos de esas superficies (`005-006` PD-10, `006-002` PD-2b, `F007` del validador
  consolidado), no solo los de su propio contrato. La suite de cierre fue el único control
  que los miró.

**Next feature in queue.** `010-003-documentary-pilot` (epic 010, orden 4;
`depends_on: 010-001 y 010-002`, ambas cumplidas): es donde se acredita lo que esta unidad
**no** acredita —fidelidad semántica de un entregable real, detección de defectos
estructurales y semánticos con evidencia independiente, y conducta efectiva de modelos— y
donde pueden absorberse N1/N2/O4 de `010-001` y O2/O4 de esta unidad. El piloto **no**
cierra la épica por sí solo, y publicar la instalación sigue sin ser requisito de arranque
pero tampoco está hecho: mientras no se publique, todo despacho real sigue necesitando la
toolchain del repositorio (I-9) y los agentes instalados no llevan la obligación.
```

---

# DRAFT 2 — `docs/progress.md` (cambios exactos)

**Estado de la transición:** la unidad **no** tenía viñeta en `## In progress` —la única de
esa sección es `Despliegue`—, así que el cambio es **alta en `## Done`**, no un movimiento
entre secciones. `## In progress` queda intacto; no tengo evidencia de esta unidad para
tocarlo (ver límite declarado en el informe).

**2.a — Insertar como primera viñeta de `## Done`** (inmediatamente después de la línea
`## Done` y antes de `- **010-001-documentary-contracts**`):

```markdown
- **010-002-documentary-role-integration** (2026-10-31, epic 010 — **orden 3 del plan**;
  **aceptación funcional registrada por mandato HITL, no aprobada directamente por el
  dueño y NO publicada**) — un encargo documental encontró su procedimiento operativo en
  los **campos existentes** (`objective`, `expected_output`, `inputs`/`read_scope`,
  `write_scope`, `invariants`, `evidence_required`), **sin agente, campo del estado, etapa
  ni selector nuevos**, con el procedimiento en `references/handoff-prompts.md` y remisión
  a la casa normativa de `010-001`. **Aplicabilidad Odoo por rol y por producto/diff:** la
  frontera de addon (código, vistas, seguridad, datos, `__manifest__.py` y equivalentes
  funcionales; documentación del módulo como producto documental) delimita obligaciones
  sin cambiar clasificación de rutas ni permisos; la base es el contrato para architect y
  test-writer, el producto aprobado para implementer, y el **diff real** —que prevalece
  sobre la etiqueta— para reviewer y orquestador; un verificador documental no es test de
  addon y corre por el runner declarado, o el encargo declara el límite. **Destinatario
  coherente en dos niveles:** contraste estático agente↔rol sin consultar el stack, y
  contraste contextual rol/stack/agente solo al publicar (ordinario o
  `--replace-packet`) y al registrar un intento nuevo; el reemplazo **rederiva** el agente
  en vez de copiarlo; recepción, repetición idéntica y finalización del write-ahead no se
  reevalúan; vía nativa procedimental y guarda mecánica solo en el adaptador externo.
  **Esquema del request** con `agent`/`execution_context` y `dependentRequired`, que
  describe forma y no sustituye al validador contextual. PC-01..PC-13; INV-01..INV-08;
  commits `735d977c` (review-fix B1/B2) y `cc6dad54` (cuatro regresiones de cierre), sin
  ningún test editado. **Review de T8 con tres bloqueantes** —B1 guarda mecánica
  inexistente en la vía nativa, B2 batería de addon incondicional en los deltas de rol, B3
  registro incompleto de I-10— **cerrados con controles escritos antes de la corrección y
  re-verificados sin bloqueantes nuevos** (`review-002.md`). **Gate de cierre en dos
  intentos, ambos conservados:** el intento 1 (`35b81093`) dio **rc=1** —`4 failed, 1914
  passed, 5 skipped`, `canary_delta_lines: 18`— y encontró **cuatro regresiones
  estructurales en superficies compartidas** introducidas por la unidad (`005-006` PD-10,
  `006-002` PD-2b ×2, `F007`), corregidas en `cc6dad54`; el intento 2 (`d37227ea`) dio
  **rc=0**, **1923 nodeids**, `1918 passed, 0 failed, 5 skipped in 1:10:04`, `dirty 1`,
  `canary_delta_lines: 0`. Tests del feature: `tests/test_010_002_documentary_role_integration.py`
  (**29 tests**) y `tests/test_010_002_documentary_role_properties.py` (**7 tests**, semilla
  `20261031`), más cinco fixtures adaptados; `make agents` ×2 con hash idéntico
  (`7f9c2d65…`), 22 agentes, ninguno a mano. **Deuda:** los seis `deferred-hardening` de la
  spec §9; **I-10 nuevo** (la identidad del paquete no está pineada a sus fuentes de
  instrucción, acreditado con una excepción declarada a una guarda fail-closed, **no
  reutilizable**); **I-11/I-12** (localizadores frágiles de `005-006` y `006-002`); el
  canario no distingue otro gestor de agentes; I-8 e I-9 heredados; N1/N2/O4 de `010-001`
  y O2/O4 de esta unidad diferidos; **deriva de la instalación global** —los 22 agentes no
  llegan a los agentes instalados hasta que el dueño publique—; N7 aceptado fail-closed con
  tres salidas. Un verde estructural **no** acredita fidelidad semántica ni conducta de
  modelos: eso corresponde al piloto `010-003`. Detalle en
  `docs/specs/010-002-documentary-role-integration/closure.md` y
  `owner-acceptance-2026-10-31.md`.
```

**2.b — Sin otros cambios.** No se toca `## In progress`, `## Queued` ni `## Blocked`: el
piloto `010-003` ya está en la cola de la épica y agregarlo acá sería inventar una entrada
que el estado no declara.

---

# DRAFT 3 — `docs/systemPatterns.md` (sección nueva)

Va **después de la última viñeta de `### Contratos documentales — una casa, punteros y dos
registros (epic 010, 2026-10-31)`** (línea 540, la que termina en «este archivo no
re-enuncia las postcondiciones.») y **antes de `## Palanca \`write: ask\` y permisos de
bash (cdad-010, ADR-009)`**.

```markdown
### Especialización documental por contrato y destinatario coherente (epic 010, 2026-10-31)

- **El perfil documental es una especialización por contrato, no una identidad.** Un
  encargo cuyo producto es un documento se declara con los campos que el encargo ya lleva:
  objetivo y promesas en el contrato/`objective`, producto en `expected_output`, fuentes
  en `inputs`/`read_scope`, producto editable en `write_scope`, separación y verificadores
  en `invariants` y alcances, comprobaciones y límites en `evidence_required`. No se creó
  rol, agente, etapa, subfase, campo del estado ni selector; `stack` sigue significando
  dominio. Por eso la generación, la instalación y la resolución del perfil se acreditan
  con los agentes **existentes** y un encargo bien declarado. Base: `010-002` D1, PC-01–02.
- **La frontera de addon delimita obligaciones, no permisos.** Es trabajo de addon
  `models/`, `views/`, `controllers/`, `wizards/`, `security/`, `data/`, `static/src/`,
  `__manifest__.py` y el código o recurso funcional equivalente; la documentación del
  módulo (`readme/`, `static/description/`, `README.rst`, `doc/`) es producto documental
  salvo que el contrato la declare entregable funcional, y su ubicación dentro del módulo
  no exige batería de addon. Un test de addon verifica producto de addon aunque el
  test-writer escriba solo bajo `tests/`; un verificador estructural documental no se
  vuelve test de addon por el dominio del proyecto. Esta frontera **no** cambia la
  clasificación de rutas de la política, los permisos ni los alcances admitidos. Casa única:
  `skills/odoo-expert/SKILL.md` (`## Addon work vs. module documentation`); el resto de las
  skills Odoo la citan. Base: `010-002` D2, PC-04–05.
- **La aplicabilidad se ata al producto o al diff, según el rol.** Architect: producto
  propuesto en el contrato y sus alcances —nunca su propio `write_scope`, que está vacío—;
  conserva conocimiento funcional, configuración primero, mapeo proceso→módulo y `VERIFY`,
  y solo debe inventario core/OCA acreditado y entorno de pruebas cuando propone modificar
  un addon. Test-writer: producto y promesas que verifica, nunca el hecho de escribir
  tests. Implementer: producto aprobado y `write_scope`. Reviewer y orquestador: contrato
  **y diff real**, que prevalece sobre la etiqueta; un addon oculto bajo etiqueta
  documental se informa y **bloquea** su aceptación como documental puro, sin permiso
  retroactivo. Scribe: evidencia del cierre, sin producir ni verificar addon. Base:
  `010-002` D2, PC-05.
- **Un verificador documental no es un test de addon.** No exige `TransactionCase` ni
  `@tagged`; corre por el runner declarado del proyecto y, cuando ese runner no lo cubre,
  el encargo **declara el límite de evidencia** sin emitir comandos crudos fuera del
  contrato `make` ni ampliar permisos. Esta precisión nació al cerrar B2 del review de T8 y
  quedó registrada como P-5 (no estaba en la spec original); no crea permisos nuevos.
  Base: `010-002` PC-04, P-5.
- **El destinatario se comprueba en dos niveles, en momentos distintos.** Estático
  agente↔rol en la validación compartida: `cdad-<role>` exacto o prefijo completo
  `cdad-<role>-` con sufijo no vacío, sin consultar el stack y sin acreditar que la variante
  esté publicada; un agente de otro rol no valida ni produce render válido, y el
  diagnóstico nombra rol, agente recibido y familia esperada. Contextual rol/stack/agente
  solo en dos límites: publicación de un request **nuevo** (ordinaria o
  `prepare --replace-packet`) y registro de un **intento nuevo** de despacho con `agent`
  declarado. Se descarta validar solo al despachar —dejaría renderizar agentes de otro
  rol— y comparar el stack en toda lectura —invalidaría continuidad histórica legítima—.
  Base: `010-002` D3, PC-06–08, INV-04.
- **Publicación nueva deriva el agente; el reemplazo rederiva, nunca copia.** La derivación
  canónica es una sola: `stack` ausente, `null` o vacío → `cdad-<role>`; cualquier cadena
  no vacía → `cdad-<role>-<stack>`. `prepare --replace-packet` publica un sucesor con el
  agente derivado del rol y del stack **vigente**, incluso cuando el predecesor histórico no
  tenía agente o cuando el stack cambió durante su vida, sin reescribir bytes históricos ni
  sus registros. Es **garantía por construcción**: se verifica el valor publicado, y no se
  atribuye a las vías públicas una rama de rechazo de agente inyectado que su interfaz no
  permite alcanzar. Base: `010-002` PC-06, EV-03.
- **La distinción temporal protege continuidad y no abre reutilización.** La recepción de
  un paquete ya despachado, la repetición idempotente de un registro idéntico y la
  finalización válida del write-ahead del mismo intento **no** se reevalúan contra el stack
  vigente; un intento nuevo con agente declarado **sí**. Un histórico admitido sin
  `execution_context` ni `agent` puede registrar un intento nuevo sin contraste contextual
  del destinatario y **sin** derivar ni sustituir agente en silencio. La regla de presencia
  es explícita: `execution_context` exige `agent`, toda publicación nueva publica ambos y
  `agent` sigue excluido del render. Base: `010-002` PC-08, INV-04.
- **Lo mecánico y lo procedimental se atribuyen donde existen.** En la vía nativa, una
  variante requerida y no publicada es **deber procedimental**: el orquestador comprueba la
  publicación del agente derivado y, si falta, detiene esa parte y reporta el bloqueo, sin
  sustituirla en silencio. El rechazo mecánico antes de lanzar pertenece **solo** al
  adaptador externo y no se promete guarda nueva para la vía nativa. Este criterio se
  rompió una vez en los adaptadores y en los orquestadores generados (B1) y el detector
  existente no lo vio porque una negación vecina lo anulaba. Base: `010-002` D4, PC-09.
- **El esquema del request describe forma.** `packet-request.schema.json` declara `agent` y
  `execution_context` (cadenas no vacías, con la ubicación canónica del contexto),
  conserva el conjunto cerrado y agrega `dependentRequired` (`execution_context` →
  `agent`). No sustituye las comprobaciones del CLI sobre coherencia de rol, rutas
  canónicas, archivos, estado, autoridad, hashes, identidades ni el momento de
  publicación/despacho. Base: `010-002` D5, PC-10.
- **Lo que esta convención NO promete.** Nada de conducta de modelos: los controles son
  estructurales y la fidelidad semántica de un documento real corresponde al piloto
  `010-003`. Nada de sellado criptográfico del `agent` histórico ni de snapshot nuevo del
  stack. Nada de paridad total entre el esquema y el validador contextual. Nada publicado:
  los 22 agentes derivados no alcanzan la instalación global hasta que el dueño lo decida,
  y hasta entonces la obligación llega por el paquete y la toolchain del repositorio.
  Deudas registradas: I-10 (la identidad del paquete no está pineada a sus fuentes de
  instrucción), I-11 e I-12 (localizadores frágiles de `005-006` y `006-002`) y el límite
  del canario frente a otro gestor de agentes. Normativo en
  `docs/specs/010-002-documentary-role-integration/spec.md` (PC-01..PC-13); este archivo no
  re-enuncia las postcondiciones.
```

`## Decisiones vigentes` **no cambia**: la unidad no adopta un ADR nuevo y la tabla indexa
ADRs, no secciones de patrón.

---

# DRAFT 4 — `docs/projectbrief.md` (documento completo)

```markdown
# Project Brief

## Propósito del proyecto

CDAD (Contract-Driven AI Development): metodología + framework de agentes para
desarrollar software con IA bajo disciplina de contratos — spec aprobado, TDD
anti-trampa con sesiones aisladas por rol, review two-layer y Memory Bank.
Para equipos (humanos + agentes) que quieren calidad verificable, no teatro.

## Stack técnico

- **Formato**: markdown (skills + agents frontmatter opencode) + bash + Python 3 (stdlib).
- **CLI canónicos del ciclo** (familia `skills/cdad-cycle/scripts/`, con wrapper fino en
  `scripts/`): paquetes/estado (`cdad_packet.py`), recepción/materialización/evidencia
  (`cdad_result.py`), continuidad (`cdad_continuity.py`), guards (`cdad_guard.py`),
  medición de contexto (`cdad_context_meter.py`), versión (`cdad-version-check.py`);
  generador/activación en `scripts/` (`cdad-generate.py`, `cdad-activate.py`).
- **Instalación**: `install.sh` (copia a `~/.config/opencode/` y `~/.agents/`,
  flags `--check/--force/--uninstall`); agentes generados desde `sources/` a staging
  (nunca editados a mano) e instalados solo desde staging.
- **Tooling de tests**: suite **pytest** (Python) por feature (`tests/test_<feature>_t*.py`,
  RED/GREEN por tarea) + validadores **bash** de consistencia (`tests/validate-*.sh`,
  `make validate`); checks por feature en `docs/specs/<id>/VALIDATION.md`.
- **Lint / type check**: para proyectos Odoo gestionados con CDAD:
  `make lint` (pre-commit-vauxoo) + `make test*` (contrato odoo-make-env).
- **CI**: pendiente (deuda registrada; la suite local hace de gate, ver progress).

## Despacho de encargos y frontera con la instalación

- **El paquete es un artefacto publicado, no un mensaje.** Un encargo CDAD se
  prepara con `cdad_packet.py prepare` y queda en `.cdad/packets/<packet_id>/`
  (`REQUEST.json` + `PACKET.md` canónico). El rol lo admite por una de dos rutas
  exclusivas: **ruta A** (paquete inline completo, comparado byte a byte contra el
  render) o **ruta C** (bloque de identificación + lectura del paquete publicado).
- **Ruta C es la vía de despacho sin retranscribir el cuerpo.** `render --route C`
  emite solo la declaración y un bloque JSON con `project_root`, `packet_id`,
  `execution_id`, `execution_context`, `request`, `packet` y `contract`; no reproduce
  instrucciones, objetivo, entradas, scopes ni cuerpo. Exige el request **publicado**
  en su ubicación canónica, contexto v2 canónico y el `PACKET.md` completo verificado
  contra el render antes de emitir. No modifica archivos ni estado. Base: `010-004`
  (`docs/specs/010-004-packet-dispatch-ergonomics/spec.md` §4.2, PC-01/PC-02).
- **El contexto de ejecución se declara, no se infiere.** Toda publicación nueva
  declara `execution_context` con la forma exacta
  `.cdad/executions/<execution_id>/execution.json` en `REQUEST.json` y en la cabecera
  de `PACKET.md`; toda preparación nueva —ordinaria, sucesora o de recuperación que
  publique generación nueva— usa ejecución **v2**, incluso al continuar un proyecto
  viejo. Los requests históricos v1 se reconocen, validan y reemiten por sus vías
  explícitas; ninguno de esos usos habilita preparación nueva v1.
- **El destinatario del encargo se comprueba en dos niveles, en momentos distintos**
  (`010-002` D3, PC-06..PC-08). **Estático** agente↔rol en la validación compartida:
  `cdad-<role>` exacto o prefijo completo `cdad-<role>-` con sufijo no vacío; un agente de
  otro rol no valida ni produce render válido, y el contraste **no** consulta el stack ni
  acredita que la variante esté publicada. **Contextual** rol/stack/agente solo al publicar
  un request nuevo —ordinario o `prepare --replace-packet`— y al registrar un **intento
  nuevo** de despacho con agente declarado. Toda publicación nueva deriva el agente del rol
  y del stack vigente; el reemplazo **rederiva** y deja de copiar el del predecesor (cubre
  predecesor histórico sin agente y stack cambiado, sin reescribir bytes históricos). La
  recepción de un paquete ya despachado, la repetición idempotente de un registro idéntico
  y la finalización válida del write-ahead **no** se reevalúan contra el stack vigente; un
  intento nuevo con agente declarado sí. `execution_context` exige `agent`, y `agent` sigue
  excluido del render.
- **Mecánico y procedimental se atribuyen donde existen.** Una variante requerida y no
  publicada es **deber procedimental** del orquestador en la vía nativa (comprobar
  publicación, detener y reportar, nunca sustituir en silencio); el rechazo mecánico antes
  de lanzar pertenece **solo** al adaptador externo.
- **El esquema del request describe forma, no autoridad.** `packet-request.schema.json`
  declara `agent` y `execution_context`, conserva el conjunto cerrado y exige la
  dependencia `execution_context` → `agent`. No sustituye las comprobaciones del CLI sobre
  coherencia de rol, rutas, archivos, estado, autoridad, hashes ni momento de publicación.
- **Frontera con la instalación (R1).** La unidad `010-004` queda **cerrada en el
  repositorio y NO vigente en la instalación**: el despacho real usa la toolchain del
  repo (`skills/cdad-cycle/scripts/…` y sus envoltorios `scripts/`) hasta que el dueño
  decida publicar. La copia instalada conserva el comportamiento anterior (sin
  `--route`, esquema cerrado que desconoce el campo, preparación v1 implícita sin
  policy). Publicar es decisión del dueño, no del orquestador. Detalle y hashes
  medidos en `docs/specs/010-004-packet-dispatch-ergonomics/closure.md` §7. **Publicada el 2026-10-31** con aprobación del dueño: `install.sh --check` rc=0 y hashes
  repo = instalado; ver `closure.md` §10.

## Producto documental — norma única y frontera de escritura

- **Una sola casa normativa.** Los criterios para encargos cuyo producto es un documento
  (relevamiento, mapa de proceso, historia de usuario) viven en
  `skills/cdad-cycle/references/documentary-contracts.md`, localizable desde la tabla de
  referencias de `skills/cdad-cycle/SKILL.md`. Los consumidores —las seis fuentes de rol,
  los cinco bloques estáticos de `skills/cdad-cycle/packets/roles/` y los agentes
  derivados de ambos runtimes— declaran su obligación en sus propias palabras y nombran
  el archivo; nadie reproduce sus frases normativas. Base: `010-001`, PC-13/PC-14.
- **Cuatro categorías, no un formato.** Evidencia, propuesta, contradicción y pendiente
  son distinciones obligatorias y localizables; no se exigen secciones vacías ni
  instancias ficticias. Toda afirmación factual identifica la fuente que la sostiene y
  dónde examinarla, con un **localizador mínimo por tipo de fuente** (archivo del repo,
  insumo recibido, mensaje o decisión, minuta, fuente mutable).
- **Pendientes clasificados por su efecto sobre el contrato.** Bloquea el pendiente que
  impide verificar una postcondición o un criterio de aceptación, y también el de
  impacto todavía desconocido. El productor no rebaja una obligación a «no bloqueante»
  por decisión unilateral: si hay que renunciar a una promesa, cambia el contrato por el
  procedimiento de aprobación vigente.
- **Frontera producto autorizado / fuentes / verificadores.** Todo encargo documental
  declara fuentes autorizadas, producto editable por rutas, verificadores e insumos de
  aceptación protegidos, evidencia esperada y límites de verificación. Compartir la
  clasificación `docs` **no** vuelve editable un archivo. Rige **«quien produce no
  modifica su oráculo»**, para código y para documento.
- **Dos registros en el cierre.** Control automático/estructural (qué se ejecutó,
  resultado, alcance, límites) y revisión semántica independiente (qué se contrastó,
  hallazgos, abstenciones). La presencia de secciones, etiquetas, archivos o referencias
  resolubles **no** demuestra fidelidad, suficiencia ni verdad semántica; un recibo de
  transporte o la aceptación estructural de un paquete tampoco acreditan revisión
  semántica. La aceptación funcional es del usuario/dueño que aprueba.
- **El perfil documental es una especialización por contrato, no una identidad**
  (`010-002` D1, PC-01..PC-03). Un encargo documental se declara con los campos que ya
  existen: objetivo y promesas en el contrato/`objective`, producto en `expected_output`,
  fuentes en `inputs`/`read_scope`, producto editable en `write_scope`, separación y
  verificadores en `invariants` y alcances, comprobaciones y límites en
  `evidence_required`. **No** hay agente, rol, etapa, subfase, campo del estado ni selector
  documental nuevos, y `stack` sigue significando dominio. El **procedimiento operativo** de
  preparación y aceptación vive en `skills/cdad-cycle/references/handoff-prompts.md`
  (`## Documentary engagement — operating procedure`) y remite a la norma, sin repetirla.
  La producción documental exige alcance editable explícito; los defaults de rol no se
  amplían.
- **Aplicabilidad Odoo por rol y por producto o diff real** (`010-002` D2, PC-04/PC-05).
  Las obligaciones de addon rigen cuando el encargo modifica o verifica el addon; un
  producto exclusivamente documental conserva el conocimiento funcional de dominio y **no**
  exige una batería de addon que no modifica. La frontera de addon —código, vistas,
  controladores, asistentes, seguridad, datos, estáticos, `__manifest__.py` y equivalentes
  funcionales— tiene casa única en `skills/odoo-expert/SKILL.md`; la documentación del
  módulo es producto documental salvo declaración en contrario. La base de decisión es por
  rol: contrato para architect y test-writer, producto aprobado para implementer, y
  **diff real** —que prevalece sobre la etiqueta— para reviewer y orquestador. Un addon
  oculto bajo etiqueta documental se informa y bloquea su aceptación como documental puro.
  La frontera **no** cambia la clasificación de rutas ni los permisos.
- **Un verificador documental no es un test de addon.** No exige `TransactionCase` ni
  `@tagged`; corre por el runner declarado del proyecto y, si ese runner no lo cubre, el
  encargo declara el límite de evidencia sin comandos crudos ni permisos nuevos.
- **Límite de vigencia.** La norma está en el repositorio; la instalación global no la
  distribuye todavía (`install.sh --check` en deriva, `010-001/closure.md` §5). Hasta que
  el dueño decida publicar, la obligación llega **por el paquete** y no por el agente
  instalado, y el despacho real usa la toolchain del repo.

## Stakeholders y roles

- **Aprobador de specs / dueño**: el dueño del repo (humano, HITL).
- **Orquestador de referencia**: `cdad-orchestrator` (agente); en epic-005 la HITL está
  delegada al orquestador OpenCode (`docs/epics/epic-005-real-operation/execution.md`).
- **Runtimes soportados**: OpenCode (nativo, ADR-008 para Claude Code), Zed.

## Restricciones conocidas

- Español rioplatense (vos) en toda la documentación.
- En OpenCode: TODOS los roles cdad son task-ables y se delegan vía `task`
  (palanca `write: ask`, cdad-010/ADR-009; el canal `delegate` está muerto en
  deploys con default global sin crédito). En otros runtimes, Agent/handoff
  manual.
- Los modelos por rol viven en el frontmatter de `agents/*.md` (perfiles
  optimus/economical/premium via install.sh).
- La admisión del rol es **documental**: las guardas verifican tokens estables y su
  supervivencia en los derivados, no la conducta de un modelo ni los bytes que recibió
  una sesión nativa. Toda afirmación de cumplimiento se lee con ese límite (R3).

## Scope general

Cubre: ciclo de 5 etapas, roles especializados (+variantes Odoo), epic
coordinado, bootstrap de Memory Bank, ejecución por proyecto v2 (política
única + agentes derivados + guard), continuidad, medición de contexto,
orientación acotada del orquestador, despacho de encargos por paquete
publicado (rutas A y C), los contratos documentales compartidos (categorías,
localizadores, pendientes y frontera producto/fuentes/verificadores) y la
especialización documental por contrato (procedimiento operativo, aplicabilidad Odoo
por rol y diff, coherencia del destinatario y esquema del request). Fuera de scope: runtimes específicos de
CI, adaptadores privados de entornos Odoo (viven en repos privados),
conectores o interceptores nativos de transporte, y certificación automática
de fidelidad semántica.

## Recursos externos

- Repo: https://github.com/rizzopablo/cdad
- Referencia de skills externos: obra/superpowers (comparación documentada en
  el epic superpowers-gaps)

---

Última actualización: 2026-10-31
```

---

# DRAFT 4 bis — ADR: **No ADR sugerido**

**Motivo.** Las decisiones de la unidad ya son normativas en un contrato aprobado y
recuperable: `010-002` D1–D5 y PC-01..PC-13 en `spec.md`, sus consecuencias en el cierre, y
la sílaba durable recién añadida a `systemPatterns.md`. Un ADR las repetiría. El único
candidato con forma arquitectónica —«especialización documental por contrato en vez de
agentes/selectores nuevos»— es un límite de alcance ya fijado por la épica y por la spec,
no una alternativa técnica que vaya a sobrevivir a este contrato. Las unidades previas del
epic (`010-000`, `010-001`, `010-004`) cerraron igual, sin ADR nuevo.

---

# Informe breve

**Qué cambió en cada documento.**

| Documento | Cambio | Respaldo |
|---|---|---|
| `activeContext.md` | Entrada nueva fechada al tope: qué se cerró (procedimiento por campos existentes; frontera de addon y base de aplicabilidad por rol; verificador documental; coherencia del destinatario en dos niveles con regla de presencia y distinción temporal; esquema), decisiones con motivo y trade-off (incluidos N7 fail-closed y P-5), evidencia con los dos intentos de suite, deuda con `deferred-hardening`, I-10/I-11/I-12, drift y heredados, y próxima unidad. | `spec.md` v4 (D1–D5, PC, INV, §9), `closure.md` §§1–8, `review.md`, `review-002.md`, `review-fix.md`, `review-fix-002.md`, `closure-suite-attempt-001.md`, `tdd-t4-green.md`, `tdd-t6-green.md`, `tdd-t7-properties.md`, `owner-acceptance-2026-10-31.md`, `backlog.md` del epic |
| `progress.md` | Alta de una viñeta en `## Done` (la unidad no tenía viñeta en `## In progress`: es alta, no movimiento). Síntesis de producto, PC, commits, tres bloqueantes cerrados, los dos intentos de suite con sus números, tests, deuda y el límite del verde estructural. | Ídem |
| `systemPatterns.md` | Sección nueva de patrón (10 viñetas) con las reglas durables y una viñeta explícita de «lo que NO promete». `## Decisiones vigentes` sin cambios. | `spec.md` D1–D5/PC, `closure.md` §5–6, `documentary-contracts.md` |
| `projectbrief.md` | Tres viñetas nuevas en «Despacho de encargos» (destinatario en dos niveles, mecánico vs procedimental, esquema del request), tres en «Producto documental» (perfil por contrato + procedimiento, aplicabilidad Odoo, verificador documental), y ampliación de «Scope general». | `spec.md` §1–§4, `owner-acceptance-2026-10-31.md` |
| ADR | **No sugerido**, con motivo. | — |

**Qué quedó declarado como pendiente o límite.** Los seis `deferred-hardening` de la spec
§9 con su motivo; I-10 (nuevo, con la excepción a la guarda fail-closed marcada como **no
reutilizable**); I-11 e I-12; el límite del canario frente a otro gestor de agentes; la
deriva de la instalación global (los 22 agentes no llegan a los instalados hasta que el
dueño publique); I-8 e I-9 heredados; N1/N2/O4 de `010-001` y O2/O4 de esta unidad; O1 de
la re-revisión (`execution.md` del epic sigue describiendo la acreditación como
comparación); N7 aceptado fail-closed; P-5 como precisión posterior a la spec; y que un
verde estructural no acredita fidelidad semántica ni conducta de modelos, que es lo que
`010-003` debe acreditar.

**Dos observaciones honestas, sin acción tomada.**

1. **Formato de entrega.** El pedido dice «los cuatro documentos completos». Entregué
   `projectbrief.md` íntegro (132 líneas) y, para los otros tres, el **texto completo de lo
   nuevo** con ancla exacta de inserción: reproducir `activeContext.md` (468 KB),
   `progress.md` (177 KB) y `systemPatterns.md` (120 KB) en un informe de rol no es
   viable ni auditable, y la materialización es mecánica con el ancla. Si el orquestador
   necesita el cuerpo entero, lo pido como decisión suya, no lo doy por hecho.
2. **Posible inconsistencia ajena a esta unidad.** `progress.md` §`## In progress` sigue
   diciendo que «la publicación sigue reservada al dueño», mientras la viñeta de `010-004`
   en `## Done` registra que el dueño publicó el 2026-10-31 (`install.sh --check` rc=0,
   hashes repo = instalado). No la toqué: no es evidencia de esta unidad y el borrador no
   debe inventar el estado del despliegue.

**Archivos modificados:** ninguno (rol read-only, `write_scope: []`).
**Commit:** ninguno.
**Comandos ejecutados:** `sha256sum docs/specs/010-002-documentary-role-integration/spec.md`;
`python3 scripts/cdad_packet.py validate-packet --project-root . --execution-context .cdad/executions/exec-010-002-documentary-role-integration-001/execution.json --request .cdad/packets/010-002-documentary-role-integration-scribe-memory-001/REQUEST.json --packet .cdad/packets/010-002-documentary-role-integration-scribe-memory-001/PACKET.md` (rc=0);
`python3 scripts/cdad_packet.py render --project-root . --execution-context … --request … --route C` (idéntico al bloque recibido);
`python3 scripts/cdad_packet.py status --project-root .` (aprobación `vigente`, `contract_sha256` coincide, contexto v2).

Los borradores no aprueban nada: la aprobación es del usuario y materialización y commit
son del orquestador.
