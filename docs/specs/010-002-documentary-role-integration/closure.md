# Cierre — 010-002-documentary-role-integration

**Fecha:** 2026-10-31 (UTC del entorno).
**Autor:** orquestador CDAD bajo el mandato HITL vigente
(`docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md`
§1 y §3). Documento del ámbito documental del orquestador, no trabajo de rol.
**Contrato:** `docs/specs/010-002-documentary-role-integration/spec.md`, SHA-256
`0d630c49cfd4c8b0f671026437000617b96bf1bc44b2383dd2914bc7e5581abc` (versión 4).
**Plan:** `docs/specs/010-002-documentary-role-integration/plan.md`, SHA-256
`3ead624c39a2436d6629afa11883f9cbffde885b548bbecff14f8c9500671190` (versión 4).
**Base:** cuatro pasadas de `plan-review` (dos bloqueantes en la primera, uno
nuevo en la tercera), AUDIT aprobado con resolución de alcance, y review de T8
con tres bloqueantes cerrados por `review-fix` y re-verificados.

## 1. Alcance de la unidad

**Dentro.** Un encargo documental —relevamiento, mapa de proceso, historia de
usuario— llega al rol correspondiente por el flujo canónico existente, sin
perder el dominio del proyecto y sin ampliar permisos:

- el **procedimiento operativo** del encargo documental por los campos que ya
  existen (`objective`, `expected_output`, `inputs`, `read_scope`,
  `write_scope`, `invariants`, `evidence_required`), sin agente, campo del
  estado, etapa ni selector nuevos;
- la **aplicabilidad Odoo por rol y por producto/diff**: las obligaciones de
  addon rigen cuando el encargo modifica o verifica el addon; un producto
  exclusivamente documental conserva el conocimiento funcional de dominio y no
  exige una batería de addon que no modifica; en un encargo mixto rigen ambas
  familias y el diff real prevalece sobre la etiqueta;
- la **coherencia del destinatario** en dos niveles: estática (un `agent` de otro
  rol no valida ni produce render válido) y contextual (contra el `stack`
  vigente, solo al publicar y al registrar un intento nuevo);
- la **rederivación del agente en `--replace-packet`**, que deja de copiar el
  destinatario del predecesor;
- la **corrección del esquema publicado** (`agent` y `execution_context`), sin
  convertirlo en sustituto del validador contextual.

**Fuera.** Agentes, roles, etapas, subfases, campos o selectores nuevos;
ampliar permisos o defaults; sandbox o protección mecánica universal; cambiar
modelos, recepción o reglas de aprobación; el piloto funcional (`010-003`);
publicación, push o actualización de la instalación global.

## 2. Contrato, decisiones y su rastro

D-1 (especialización por contrato con los agentes existentes), D-2 (aplicabilidad
Odoo por producto y rol), D-3 (coherencia del destinatario), D-4 (variante no
publicada) y D-5 (esquema del request) se fijaron en
`discovery-decisions-2026-10-31.md`; P-1..P-4 precisaron D-3 y D-4 sin reabrirlas,
y P-5 fijó el régimen del verificador documental en proyecto Odoo.

Las cuatro pasadas de revisión dejaron rastro completo:

| Pasada | Objeto | Resultado |
|---|---|---|
| `plan-review.md` | v1 | Dos bloqueantes (B1 aplicabilidad Odoo fuera de los roles sin escritura de producto; B2 promesa contradictoria de selección) y O1..O6 |
| `plan-review-002.md` | v2 | Sin bloqueantes; B1/B2 cerrados, O1..O6 adoptados; N1..N4 |
| `plan-review-003.md` | v3 | Bloqueante nuevo (el reemplazo copiaba el agente); N5, N6 |
| `plan-review-004.md` | v4 | Sin bloqueantes; recomendación de aprobación; N7 declarado |

N7 —un cambio de `stack` sin otra obsolescencia deja un paquete `prepared` sin
salida directa— se acepta **fail-closed** con tres salidas legítimas declaradas
en `owner-approval-2026-10-31.md`: restituir el `stack`, producir la obsolescencia
legítima, o retirar el paquete con `withdraw`. Ningún trabajo llega a un rol
equivocado.

## 3. Postcondiciones y clase de evidencia

| PC | Qué promete | Clase de evidencia | Estado |
|---|---|---|---|
| PC-01 | Procedimiento por los campos existentes, sin selector nuevo | Estructural (`TestEngagement`) + revisión | Acreditada |
| PC-02 | Fronteras de los seis roles, sin variantes documentales | Estructural + 22 agentes verificados | Acreditada |
| PC-03 | Alcance editable explícito; defaults y oráculos intactos | Estructural + regresiones de alcances | Acreditada (procedimental: no hay rechazo mecánico de un encargo sin alcance, y el contrato no lo promete) |
| PC-04 | Matriz por rol para quien especifica, verifica y produce | Estructural sobre fuentes y artefactos + revisión de cláusulas | Acreditada tras B2 |
| PC-05 | Matriz para revisión, coordinación y memoria | Ídem | Acreditada tras B2 |
| PC-06 | Toda publicación nueva deriva el agente; el reemplazo **rederiva** | Transiciones observables + propiedades | Acreditada tras B1 de v3 |
| PC-07 | Contraste estático y contextual con diagnóstico nombrado | CLI público sobre proyectos descartables | Acreditada |
| PC-08 | Presencia de `agent` con contexto, históricos admitidos, render sin `agent`, variante ausente sin fallback | Transiciones + regresión de recepción/write-ahead | Acreditada |
| PC-09 | Las superficies no prometen otra resolución | Estructural + revisión | Acreditada tras B1 de T8 |
| PC-10 | El esquema declara los campos admitidos y rechaza lo inválido | Evaluación real de JSON Schema | Acreditada |
| PC-11 | Generación reproducible; promovidos = staging; techo sin elevar | Medición de dos generaciones | Acreditada |
| PC-12.a | Instalación aislada distribuye las superficies corregidas | Instalación aislada con `CDAD_INSTALL_ROOT` | Acreditada |
| PC-12.b | CLI y esquema en la instalación aislada; recorrido documental genérico y con `stack=odoo` | Test de distribución final | Acreditada |
| PC-13 | Evidencia automática y juicio independiente separados | `review.md` + `review-002.md` | Sostenida; la aceptación es de la autoridad |

**Invariantes.** INV-01 (no hay selector documental nuevo), INV-02 (un rol y una
subfase por encargo), INV-03 (quien produce no modifica su oráculo, sin prometer
vigilancia exhaustiva), INV-04 (contrastes declarados, verificado además con
propiedades acotadas: semilla `20261031`, presupuesto declarado), INV-05 (la
excepción documental no exime addon), INV-06 (regresión de 010-001 verde),
INV-07 (generados e instalados desde fuentes canónicas) e INV-08 (hechos
distintos) quedan verificados por su vía declarada.

## 4. Distribución y procedencia

`make agents` genera los 22 agentes de ambos runtimes desde `sources/`. Se midió
**dos veces** con resultado idéntico y los promovidos coinciden con staging. La
instalación se verificó **en una raíz aislada** (`CDAD_INSTALL_ROOT` propio,
`CDAD_SKILL_EXTRA_DIRS` vacío, HOME/XDG aislados, canario del HOME visible sin
cambios): distribuye el CLI y el esquema con los bytes de la fuente y resuelve el
recorrido documental genérico y el de `stack=odoo`. Ningún agente se editó a
mano y el techo de bloques estáticos no se elevó.

**La instalación global no se actualiza en esta unidad, y su estado no se oculta.**
La publicación vigente es la del cierre de `010-004`, del **2026-10-31** (390
archivos propios, `install.sh --check` en PASS entonces). Desde esa publicación,
`010-001`, `010-002` y la corrección de esta unidad cambiaron el skill del
repositorio, así que **hoy la copia instalada está por detrás**: medido con
`bash install.sh --check` sobre el HOME real, `rc=1` y `Check: FAIL`, con drift
en **22/22 agentes**, en los tres árboles de `cdad-cycle` (opencode, agents y
claude), en las cinco skills Odoo y en `documentary-contracts.md`, que falta en
la copia de Claude Code. Publicar de nuevo es decisión del dueño; esta unidad no
publica, no hace push y no toca la instalación.

## 5. Desviaciones y hallazgos de proceso

- **I-10, defecto del mecanismo (declarado).** El GREEN de T4 modificó
  `skills/cdad-cycle/packets/roles/implementer.md`, una de las fuentes de
  instrucción de su propio paquete. Como `render_packet` lee las fuentes del árbol
  vivo, `record-dispatch` y `receive` dejaron de reconocer un paquete **no
  alterado**. Se acreditó con el árbol restituido a los bytes que la cabecera
  declara (`d93b44e4…`, recuperables de `0d935bc8`), restaurándolo de inmediato y
  sin tocar `PACKET.md` ni `REQUEST.json`. La secuencia exacta, los `rc`, los
  sellos temporales y el estatus —**excepción a una guarda fail-closed, no
  práctica reutilizable**— están en
  `deviation-green-accreditation-2026-10-31.md`, verificado por la re-revisión
  independiente. El defecto con sus dos correcciones posibles está en el backlog.
- **Contradicción en el objetivo del RED de T5, resuelta a favor del contrato.**
  El objetivo listaba «contexto sin agente» entre los casos admitidos; `PC-10`,
  D5 y el AUDIT dicen lo contrario. El test-writer lo detectó, aplicó el contrato
  y lo declaró en el informe. El objetivo era el defectuoso.
- **Tres bloqueantes en el review de T8, cerrados con RED propio.** B1 (la vía
  nativa prometía una guarda mecánica inexistente) y B2 (los deltas Odoo seguían
  exigiendo la batería de addon de forma incondicional) se corrigieron **después**
  de escribir los controles que los detectan: el detector previo quedaba verde
  porque una negación vecina —la de la sustitución silenciosa— lo anulaba. B3 (el
  registro de I-10 omitía que `record-dispatch` y `receive` corrieron durante la
  restitución) se corrigió en el documento, no en el relato.
- **Cuatro pasadas de `plan-review` y una de re-verificación.** Coste real de
  encontrar los defectos antes de construir: dos bloqueantes de contrato y uno de
  mecanismo quedaron cerrados sin rehacer producto.
- **Recuperación de una materialización mal tipada (I-13, declarada).** El
  descriptor del despacho del scribe declaró `artifact_kind: scribe-role-report`,
  que `receive` admitió y fijó en un recibo durable; `materialize` lo rechazó
  porque la tabla cerrada del rol sólo admite `role-report` y los cuatro tipos
  por documento. Como el recibo durable no se sobrescribe, el artefacto se copió
  **byte a byte** (SHA-256 `270f4cc9…`, 48.557 bytes, verificado contra el
  recibo) a `memory-bank-drafts-2026-10-31.md` —raíz autorizada del tipo de
  informe— y los cuatro documentos del Memory Bank se actualizaron desde ese
  artefacto con los bloques insertados **verbatim** (verificado por programa).
  No hay efecto de aprobación. El defecto —la tabla se aplica al materializar y
  no al recibir, sin vía de reparación— queda en el backlog como **I-13**.
- **O2/O4 diferidos con motivo** (nits de redacción de los deltas y método de
  comprobación de publicación del agente). No habilitan ninguna rebaja.

## 6. Límites declarados

- **Control estructural no es fidelidad.** Los 36 tests de la unidad protegen
  postcondiciones; **no** acreditan que un documento sea fiel a sus fuentes. Esa
  acreditación corresponde al piloto `010-003`.
- **Los contrastes del destinatario son mecánicos en el CLI y en el adaptador
  externo; en la vía nativa la comprobación de publicación es procedimental.**
  El módulo no se atribuye una guarda que no existe.
- **El esquema describe forma.** No sustituye las comprobaciones contextuales que
  requieren estado, archivos, aprobación o hashes.
- **Los 22 agentes derivados no alcanzan la instalación global** hasta que el
  dueño vuelva a publicar: la copia instalada quedó en la publicación de
  `010-004` y hoy está por detrás, así que la obligación llega por el paquete y
  por la toolchain del repositorio, no por el agente instalado.
- **La aceptación funcional es de la autoridad que aprueba**, aquí ejercida por
  mandato.

## 7. Evidencia del cierre

### Suite completa — intento 2 (el que cierra)

```
python3 scripts/cdad-suite.py close --all --evidence-root .cdad/evidence/010-002-closure-2
```

| Campo | Valor |
|---|---|
| Evidencia | `.cdad/evidence/010-002-closure-2/attempt-20261031T171528941730Z-3633447-5e275562` |
| Commit medido | `d37227ea9683ecf06493ef6c0dea0b834b792ef6` |
| `dirty` | 1 (el `discovery.md` de `010-000`, declarado fuera de índice) |
| Inicio / fin | `17:15:29Z` / `18:25:33Z` (1:10:04) |
| Selección | `all` — 1923 nodeids |
| Resultado | **`rc=0`** — `1918 passed, 0 failed, 0 errors, 5 skipped` |
| Canario | **`delta_lines: 0`** |

Los 5 `skipped` son los condicionados por entorno ya declarados en el cierre de
`010-001`: `005-002` T4 (integración real y S-BOOT-04 opcional),
`005-009` T4 PD-10, `005-010` T4 PD-8 y `006-001` T3 PD-6 pierna (b), todos
habilitados por variables de entorno que este entorno no provee.

### Suite completa — intento 1 (el que encontró las regresiones)

| Campo | Valor |
|---|---|
| Evidencia | `.cdad/evidence/010-002-closure/attempt-20261031T154550334011Z-2834037-2f17e4a0` |
| Commit medido | `35b81093` |
| Resultado | `rc=1` — `4 failed, 1914 passed, 5 skipped` (1:06:07) |
| Canario | `delta_lines: 18` |

El intento 1 **no se descarta ni se oculta**: encontró cuatro regresiones
estructurales que el resto de la verificación no había ejecutado —el punto de
cableado del CLI en su ventana (`005-006` PD-10, dos controles de `006-002`
PD-2(b) y `F007` del validador consolidado)—, todas introducidas por esta
unidad en `SKILL.md` y en los adaptadores. Se corrigieron en `cc6dad54` sin
editar ningún test y el intento 2 pasó. La medición, la causa de cada fallo y la
atribución de la deriva del canario están en
`closure-suite-attempt-001.md`.

El canario del intento 1 se atribuyó al servidor de OpenChamber (journal
`13:42:29/36`), que reescribió el agente instalado de su propia instalación con
bytes que no son el derivado de este repositorio. El intento 2, en una ventana
sin esa escritura, dio `0`: la suite no escribe en el HOME real y el canario
mide el entorno, no sólo la suite.

### Verificación de la unidad (además de la suite)

| Comprobación | Resultado |
|---|---|
| Módulo de la unidad | 29 passed |
| Propiedades (INV-04, semilla `20261031`) | 7 passed |
| Generador, `010-001`, techo de bloques estáticos | 23 passed |
| Aceptación hermética con el validador (`pd8b`, incluye `F007`) | 1 passed |
| Regeneración `make agents` ×2 contra HEAD | hash idéntico (`7f9c2d65…`) |
| `tests/` tocados por el review-fix | no (`git diff` vacío) |

## 8. Diferidos y deuda

`deferred-hardening` de la spec §9: validación semántica automática universal,
paridad total JSON Schema↔CLI contextual, ejecuciones vivas en ambos runtimes o
en una instancia Odoo, blindaje de paquetes históricos y combinatoria sin
consecuencia contractual. Ninguna exclusión aplaza una postcondición comprometida
aquí.

Backlog del epic: **I-7** (heredado), **I-8** (test-writer sin lectura de
`skills/**`; se repitió en T7, que leyó su doctrina por bash y lo declaró), **I-9**
(dos copias del skill), **I-10** (identidad del paquete no pineada a sus fuentes),
**N1/N2/O4** de `010-001`, **O2/O4** de este review, y la **deriva de
publicación**.
