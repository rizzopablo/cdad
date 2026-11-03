---
feature_id: 015-002-intake-guards
approved_by: Pablo (HITL delegada al orquestador, docs/epics/epic-015-dispatch-reception/execution.md)
approved_at: 2026-11-02
source: architect draft (sesión <ses-343>), materializado por el orquestador (ADR-003)
decision: se aprueban D1 (diagnósticos por formato), D2 (guía, PC-06 intacto) y D3 (elegibilidad por pertenencia documentada)
---

# Borrador de spec: 015-002-intake-guards (architect, sesión <ses-343>)

**Estado:** aprobada (2026-11-02, HITL delegada; D1+D2+D3 aprobados). **Base:** `4e1ba75f5263094cb0d3159d6b91142a67ad8a9b`.

## 0. Discovery

- El diagnóstico de scope exige `CLASS=SELECTOR` sin ejemplo; selector vacío produce otro mensaje sin explicar la forma CLI (`cdad_packet.py:2430-2437`).
- La observación de despacho tiene seis claves obligatorias cerradas; sus errores no ofrecen documento de ejemplo (`4208-4214`, `4258-4294`).
- `decisions` exige objetos con `decision`+`rationale` no vacíos; los errores no muestran un elemento válido (`cdad_continuity.py:530-560`).
- PC-06 rechaza referencias contract cubiertas por escritura sin reclasificarlas (`cdad_packet.py:1277-1324`; 008-004 spec:180-185).
- `docs=docs` no cubre la carpeta del contrato del paquete; sí puede cubrir otros contratos como el plan del epic (`cdad_packet.py:1477-1500`; sonda: spec 014-001 False, plan epic 014 True).
- `open-unit` selecciona la primera queued sin considerar cierres de epics (`cdad_packet.py:6998-7023`, `7052-7081`).
- 013-004 permanece queued; el cierre del 013 declara que no se abrió por decisión del dueño.
- GREEN-001 de 014-001 retirado por scope documental insuficiente.
- Límite: no se recuperó en stage_history el rechazo de begin.decisions ni la apertura accidental de 013-004; carencias respaldadas por código y sondas.

## 1. Objetivo
1. Explicar formatos cerrados rechazados con ejemplos válidos. 2. Guiar el choque scopes documentales amplios vs referencias contract, conservando PC-06. 3. Excluir de open-unit unidades de epics con cierre registrado. Sin cambiar la semántica de recepción de 015-001.

## 2. Contrato y alcance
Fuentes: contrato de unidad, plan epic-015, esta spec aprobada, 008-004 PC-06 como restricción. Producto: `skills/cdad-cycle/scripts/cdad_packet.py`, `cdad_continuity.py`, `references/project-execution.md`, `references/continuity.md`, `references/project-start.md`. Tests nuevos: `tests/test_015_002_intake_guards.py` (test-writer). Wrappers de `scripts/` delegan, no duplican. Fuera: contratos cerrados, permisos, edición manual del estado, publicar/desplegar, esquemas, reapertura de epics.

## 3. Decisiones
**D1.** Enriquecer errores de los validadores actuales, sin framework general. Cada diagnóstico distingue formato inválido de rechazos por autoridad/política/vigencia; no propone corregir autoridad cambiando JSON.
**D2.** Guía (no debilitamiento) ante PC-06: el diagnóstico mantiene referencia/selector/paquete; recomienda estrechar `--write-scope`; explica `class:"living"` solo para material genuinamente mutable; advierte que un contrato aprobado no se reclasifica para eludir; sin exclusiones negativas ni selectores inexistentes. Guía con scopes por subdirectorios.
**D3.** Elegibilidad por pertenencia documentada, no por prefijo: cierres = entradas `epic_history` con `stage:"epic-closure"` e identidad `epic`/`epic_id`; plan en `docs/epics/<epic>/plan.md`; pertenencia por fila estructural única (criterio `_locate_unit`, `cdad_packet.py:5805-5845`); excluir antes de seleccionar la primera queued. Sin prefijos/notas libres; sin reclasificar a done. Fuente ausente/ambigua → bloqueo con diagnóstico, nunca apertura silenciosa.

## 4. Postcondiciones
**PC-01** (observación de despacho): rechaza documento incompatible identificando campo/problema, formato esperado y ejemplo JSON con las seis claves (runtime/model_configured/model_reported/session/started_at/provenance; nulls si no observados). El ejemplo no autoriza inventar.
**PC-02** (decisions de begin): conserva rechazo, señala decisions/elemento, incluye forma esperada y ejemplo `[{"decision":"…","rationale":"…"}]`.
**PC-03** (write scope): CLI mal formado identifica la opción, exige `CLASS=SELECTOR` no vacíos, incluye ejemplo (`--write-scope implementation=skills`). No convierte repository-read en escritura.
**PC-04** (rechazo accionable PC-06): nuevo begin con referencia contract cubierta sigue rechazándose pre-persistencia; ofrece estrechar scope o living solo cuando corresponda.
**PC-05** (guía coherente): continuity.md documenta el caso `docs=docs`, su límite (carpeta del contrato) y ejemplo living mutable con aceptación fuera; contract fuera de scope admitido; living explícito admitido si valida; sin reclasificación automática; sin atajos sobre contratos aprobados.
**PC-06** (selección automática): open-unit omite queued de epic cerrado y abre la primera elegible, conservando orden; omitida e historia intactas.
**PC-07** (selección explícita): `--feature <ID>` de unidad excluida rechaza nombrando unidad y epic, sin abrir ni persistir.
**PC-08** (sin candidata): solo excluidas → informa sin candidata, sin ejecución ni cambios; fuente bloqueante → identifica fuente y motivo.
**PC-09** (apertura compatible): conserva comprobaciones de reposo/dependencias/autoridad/vigencia y atomicidad; validate-state acepta. project-start.md: «primera queued» = primera elegible; --feature no elude cierre.

## 5. Invariantes
Contratos intactos; diagnósticos sin ampliar permisos ni relajar esquemas; PC-06 intacto; formatos/semántica 015-001 intactos; omitidas no done; sin prefijos; escritor único/lock/atomicidad.

## 6. Aceptación
Verificadores CLI PC-01–09 sobre proyectos sintéticos; ausencia de efectos en rechazos; regresión proporcional (008-004, 005-007-t3-open-unit, despacho/continuidad/recepción congelada); revisión independiente de la guía; diff en scopes delegados.

## 7. deferred-hardening
Framework universal de errores; reapertura/cancelación/migración de epics; reconstrucción de cierres sin identidad; parser universal de planes; rendimiento/inventario global; sandbox/escrituras transitorias.

## Evidencia del architect
validate-request/packet rc=0; render byte-idéntico; route C coincidente. Sondas: `docs:docs`→CLASS=SELECTOR; `docs=`→selector no vacío; decisions ['texto']→objeto con decision+rationale; docs=docs cubre spec 014-001 False / plan epic 014 True; 013-004 membership True. Sin archivos modificados, sin tests, sin commit. Pendiente: aprobación explícita (D1/D2/D3) antes de materializar.
