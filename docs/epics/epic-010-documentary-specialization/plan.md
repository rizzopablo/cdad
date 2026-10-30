---
epic_id: epic-010-documentary-specialization
epic_name: Especialización documental de CDAD
created_at: 2026-10-29
approved_by: Pablo
approved_at: 2026-10-29
---

<!-- cdad:plan-anchors
{"history": ["Plan changes", "Cambios al plan"], "authorization": ["Stakeholders", "Autoridad"]}
-->

# Epic 010: Especialización documental de CDAD

## Resumen

Extender CDAD para producir documentación funcional verificable: relevamientos,
procesos e historias de usuario. La documentación es el producto bajo contrato;
no se confunde con el Memory Bank. Se conserva la separación entre especificar,
producir, construir verificadores y revisar de manera independiente.

## Alcance

Entra:
- Conocimiento documental compartido, independiente del cliente y del dominio.
- Especialización de los roles existentes, sin un agente con permisos acumulados.
- Verificación estructural automática y revisión semántica contra fuentes.
- Integración con paquetes, generación e instalación de agentes y selección del
  perfil documental, conservando el dominio Odoo cuando corresponda.
- Piloto con fuentes sintéticas compartibles y entregable Markdown pequeño.

No entra:
- Nueva etapa del ciclo, reemplazo del scribe o aprobación autónoma de entregables.
- Modelos fijados en textos instalables, nombres de clientes o reglas particulares
  del caso que motivó la propuesta.
- Editor general de Word/XLSX, publicación externa o corpus real de clientes.
- Garantía de verdad semántica mediante un script o un puntaje de un LLM.

## Descomposición

| Orden | Feature | Resultado observable | Dependencias |
|---|---|---|---|
| 0 | `010-000-continuity-relative-root` | Continuidad acepta raíces relativas equivalentes a absolutas sin debilitar controles; el fix queda validado mediante la vía de generación e instalación distribuible. | Ninguna |
| 1 | `010-004-packet-dispatch-ergonomics` | Los roles reciben el contexto de ejecución sin inferirlo y el transporte del paquete deja de depender de transcripción manual; los rechazos por intake ganan diagnóstico accionable. | 010-000 |
| 2 | `010-001-documentary-contracts` | Los roles disponen de criterios documentales compartidos para distinguir evidencia, propuesta, contradicción y pendiente, con límites explícitos de escritura y verificación. | 010-000, 010-004 |
| 3 | `010-002-documentary-role-integration` | El orquestador puede encargar trabajo documental al rol correspondiente mediante el flujo canónico, sin perder su dominio ni ampliar sus permisos. | 010-001 |
| 4 | `010-003-documentary-pilot` | Un piloto recorre el ciclo con un entregable trazable y evidencia independiente de detección de defectos estructurales y semánticos. | 010-001, 010-002 |

Ejecución secuencial. Cada feature tendrá su propio Discovery, spec aprobada,
pruebas relevantes previas a GREEN y revisión independiente. Esta descomposición
no fija todavía nombres de skills, agentes ni campos nuevos del estado.

## Contratos transversales

- Cada encargo corresponde a un solo rol y una sola subfase. Discovery/Spec
  producen borradores; GREEN modifica únicamente el producto autorizado; el
  test-writer conserva el verificador; el reviewer es independiente y read-only.
- El paquete declara las fuentes, el producto editable y los insumos de
  aceptación protegidos. Una plantilla usada como oráculo no se modifica en GREEN
  para obtener un resultado favorable.
- Las afirmaciones documentales referencian fuentes localizables. La ausencia de
  evidencia se declara como pendiente; una propuesta no se presenta como hecho.
  Las contradicciones se registran, no se resuelven inventando consenso.
- La evidencia distingue controles automáticos de revisión semántica: resultado,
  referencias examinadas y limitaciones. Un control estructural verde no acredita
  por sí mismo fidelidad a las fuentes.
- El scribe conserva el Memory Bank; los demás roles devuelven observaciones para
  su actualización, no lo actualizan directamente. El orquestador materializa y
  registra conforme al contrato vigente.

## Criterios de aceptación de la épica

- [ ] Las cinco features cierran individualmente con evidencia de sus contratos.
- [ ] El ciclo 010-000 incluye regresión de raíces relativas/absolutas y rechazo de escapes reales, revisión independiente y validación del artefacto instalable; no se modifica la instalación global como sustituto de corregir la fuente.
- [ ] El flujo canónico genera, instala y resuelve los perfiles documentales
  definidos en Specification; sus restricciones por rol se conservan.
- [ ] Los agentes genéricos y Odoo mantienen su comportamiento previo; la
  combinación documental/Odoo se verifica según el mecanismo aprobado en 010-002.
- [ ] El piloto identifica un defecto estructural mediante un control automático.
- [ ] La revisión independiente del piloto identifica una afirmación sin respaldo,
  una contradicción omitida y una referencia incorrecta, con ubicación y evidencia
  en las fuentes sintéticas. No se exige a un script decidir verdad semántica.
- [ ] El entregable corregido conserva trazabilidad; las limitaciones y pendientes
  quedan visibles y el usuario aprueba su aceptación funcional.
- [ ] No se modifican verificadores ni insumos protegidos desde GREEN; cambios
  legítimos vuelven al rol competente y, si alteran el contrato, a aprobación.
- [ ] Validación y regresión pertinentes pasan; no se incluyen datos privados ni
  modelos concretos en el producto instalable. No se realiza push ni publicación.

## Riesgos y límites

- Un único campo `stack` podría no expresar dominio y tipo de producto a la vez.
  Discovery de 010-002 debe verificar el mecanismo actual y proponer la solución
  mínima; este plan no autoriza añadir un segundo mecanismo por anticipado.
- Una revisión semántica puede equivocarse. Se exige trazabilidad de sus hallazgos
  y aceptación del usuario, no una promesa de detección infalible.
- Los formatos binarios y corpus de clientes quedan para ampliaciones posteriores.

## Autoridad

- Aprobador del plan y de las specs: Pablo.
- Aceptación funcional y aprobación del Memory Bank: Pablo.
- Orquestador: coordinación, paquetes, validación de gates y materialización.
- No se hereda la delegación de autoridad de otras épicas. Las instrucciones de
  construir y avanzar autorizan preparar esta propuesta, no aprobarla en nombre
  del usuario ni registrar como aprobadas specs todavía inexistentes.

## Antecedentes verificados

- Propuesta de documenter aportada por el usuario y discusión de alcance de esta
  sesión. El borrador original es evidencia de partida, no un contrato aprobado.
- `sources/roles/scribe.md`: el scribe mantiene el Memory Bank y no es un agente
  general de documentación.
- `sources/roles/{architect,implementer,test-writer,reviewer}.md`: contratos de rol
  que la especialización debe conservar.
- Estado operativo al iniciar: sin épica ni feature activas; `open-unit` rechazó
  la apertura por no existir una unidad queued. La vista compacta informa DRIFT
  solamente en la pata project; resolver mediante `republish-agents` antes del
  primer dispatch y verificar coherencia, sin cambiar la instalación global.

## Cambios al plan

### 2026-10-29 — Ergonomía de despacho encolada tras el fix de raíces

Pablo indicó investigar y resolver el rechazo de paquetes por verificación tras
cerrar `010-000`. Se agrega `010-004-packet-dispatch-ergonomics` como unidad
siguiente: contexto de ejecución explícito en la cabecera, emisión de ruta C por
el renderer, aclaración del intake y regresión de los tres fallos observados
(transcripción, cierre del bloque JSON y contexto inferido). No cambia el
alcance de las features documentales; solo su orden.

### 2026-10-29 — Fix previo autorizado por Pablo

El usuario solicita salvar el bloqueo mediante raíz absoluta e incluir primero
el fix distribuible para otras instalaciones. Se agrega 010-000 como dependencia
de 010-001. Se mantiene aprobación de specs por Pablo y la prohibición de push o
actualización automática de otras instalaciones. El paquete de Discovery
documental no despachado se retira para no mezclar ambos encargos.

---

Status: Approved by Pablo on 2026-10-29
