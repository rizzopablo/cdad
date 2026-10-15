# Aceptación de la feature — 005-013-unit-contract (T4, gate de la etapa 3→4)

**Objeto.** El gate de aceptación de la ficha T4: verificar AC-1..AC-8 sobre los productos de T1..T3 y
correr la **prueba decisiva** (AC-9) con el **CLI real** sobre **proyectos descartables**, en las **tres
formas de plan** que declara B1.4, más los focales de B2 y P1.

**Instrumento y procedencia.** El CLI del producto **del repo**, corrido como **subproceso**
(`python3 skills/cdad-cycle/scripts/cdad_packet.py …` y `…/cdad_result.py …`) sobre proyectos sintéticos
descartables creados en un directorio temporal (`<tmp>`), con el **`HOME` del subproceso en un tempdir
vacío**. **Nunca este repo, nunca HOME.** El contrato bajo prueba es la spec aprobada
(`spec.md`, sha256 `4369822e…`, sin cambios) y el código de cierre del tramo es
`skills/cdad-cycle/scripts/cdad_packet.py`, sha256 `1f06855f…` (commit `5840819`). El arnés de la corrida
vive fuera de git (`.cdad/local/005-013-t4-acceptance.py`) y su evidencia cruda en
`.cdad/local/005-013-t4-evidence.json`; los proyectos descartables se borran al terminar.

**Las tres formas de plan (B1.4/AC-9).** (i) la de este epic (tabla de unidades + sección de historia);
(ii) una generada desde la **plantilla del producto** (títulos y columna de id de la plantilla); (iii) un
**fixture sintético y anónimo** con la forma de los planes de otro proyecto (celda de unidad como
**enlace**, **sin** historia ni autoridad; ids y títulos inventados). Ninguna de las tres nombra proyectos
reales.

## Resultado por criterio (idéntico en las tres formas)

| AC | Qué se verificó | Medición |
|---|---|---|
| **AC-1 / AC-3** (PD-1/PD-4/PD-5) | `prepare` del architect publica la proyección y la pinea | `contract.kind = approved-unit-contract`; `path = .cdad/packets/<packet_id>/UNIT-CONTRACT.md` exacto; `sha256(archivo) == contract.sha256 == active_packet.contract_sha256`; la parte `unit` (encabezado de la tabla + fila de la unidad) aparece **verbatim** en la proyección. **4/4 en las tres formas** |
| **AC-2** (PD-2) | fallback declarado cuando la unidad no se localiza sin ambigüedad | con un plan **sin** fila de la unidad: `prepare` **rc=0**, `kind = approved-epic-plan`, `path = docs/epics/<epic>/plan.md`, **sin** `UNIT-CONTRACT.md`, el motivo **nombra la ruta del plan en el diagnóstico**, y `status` informa **`mode: fallback`** |
| **AC-4** (PD-6; tramo 1) | recepción contra el contrato **recibido** | despacho real (`prepare` + `--record-dispatch`) → **agregar una unidad futura independiente** al plan (y registrarla en la historia) → `receive` **rc=0**, `packet_validation: passed`, `identity_validation: passed`, `semantic_status: pending`; veredicto **`current`** (rc=0) y **sin** registro de impacto |
| **AC-5** (PD-7/PD-8/PD-9; tramo 2) | cambio relevante → registro durable | editar el alcance de la unidad activa → veredicto **`impact`** (rc=0), `changed_parts = ["unit"]`, journal `.cdad/packets/<baseline>/.impact.json` con `schema_version` + `impact` y por registro `reason`, `contract_sha256_old` (**igual** al pin registrado), `contract_sha256_new` (**distinto**) y `changed_parts`; el registro **no** bloquea la recepción (segundo `receive` rc=0) |
| **AC-6** (PD-10) | ninguna sección del plan produce `impeded` | editar la **sección de autorización** (o, en la forma anónima sin ancla, otra sección compartida) → **`impact`**, rc=0, **nunca `impeded`**. Y el `impeded` real: autorización retirada → **rc=2** con el marcador `approval pending` y la **salida nombrada** (`Exit: register the epic-plan approval…`); registrarla → **`prepare` rc=0** y la proyección nueva queda como **línea base** (`registered` = el paquete nuevo, veredicto `current`) |
| **AC-7** (PD-11; focal de P1) | `status` de solo lectura y journal idempotente | dos `status` consecutivos dejan el proyecto **byte a byte idéntico** (instantánea del árbol completa, incluido el state) y **sin** journal; el bloque `unit_contract` **informa** el veredicto; **dos** corridas del veredicto con el mismo par de digests dejan el journal **byte a byte idéntico** (misma cantidad de registros) |
| **AC-8** (PD-12/PD-13) | origen y fuente única | el bloque de origen de la proyección registra **unidad**, **ruta del plan**, **sha del plan al generar**, **`approved_by`** de la entrada `epic_history` `epic-plan` y **`policy_sha256`** (5/5 en las tres formas). La no re-aprobación por unidad, la ausencia de documento nuevo y el **pin `specification` intacto** se verifican en T3 (`t3.md`, comprobaciones observables: 0 bloques `plan-tasks` a mano, 0 listas de títulos por proyecto, digests de `spec.md`/`plan.md` sin cambios) |
| **AC-9** (prueba decisiva) | los dos tramos con el CLI real sobre proyecto descartable, en las tres formas | **cumplido**: los dos tramos corren enteros en las **tres** formas, sin fallback en ninguna (la unidad se localiza incluso con la celda como enlace), con la evidencia de arriba |
| **AC-10** (cierre) | suite completa una vez, por quien cierra | **NO corrida en este tramo** (declarado): la corre quien cierre, en un worktree fijado al commit de cierre |

## Prueba decisiva — los dos tramos (resumen del recorrido)

1. **Tramo 1 (la planificación deja de bloquearse).** Se despacha un architect (proyección publicada y
   pineada) → se **agrega una unidad futura independiente** al plan y se registra la edición en la
   historia → **`receive` rc=0** contra el contrato que el agente efectivamente recibió, y el veredicto
   queda en **`current`**. Esto es exactamente lo que hoy falla con el pin del plan completo: la review
   formal midió el fallo (`receive` rc=2 «contract sha256 does not match exact content») y con la
   proyección pineada desaparece.
2. **Tramo 2 (el cambio relevante sí exige reconciliación).** Editar el alcance o una dependencia de la
   unidad activa → **`impact`** con el registro durable; editar la sección de autorización → **`impact`**
   (nunca `impeded`); retirar la autorización → **`impeded` rc=2** con el marcador y la **salida**
   nombrada, y la salida funciona con los mecanismos existentes (registrar la aprobación `epic-plan`).

## Lo que queda declaradamente desconocido o pendiente

- **AC-10 / suite completa y validadores**: no corridos acá; van al cierre, que coordina el orquestador
  Claude. Incluye los dos FAIL de `make validate` que la review adjudicó como **preexistentes/ambientales**
  (drift de agentes instalados en HOME y A3 de patrones sensibles), ajenos al diff.
- **Redespliegue**: el comportamiento nuevo no existe en la instalación (`7212ead`); el despliegue es del
  dueño y es la deuda declarada del epic (O3 de la review: tras el redespliegue, comprobar que el activo
  instalado declara las anclas).
- **Reconciliación de un paquete `dispatched`**: fuera de alcance (005-012); el veredicto la **nombra**,
  no la implementa.

**Anonimización:** este documento no contiene rutas absolutas del dueño ni ids crudos de sesión; usa
`<tmp>`, `<packet_id>`, `<baseline>` y ids de fixture sintéticos.
