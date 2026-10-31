# plan-review — 010-001-documentary-contracts

**Objeto revisado:**
- `docs/specs/010-001-documentary-contracts/plan.md`, versión 2, sha256 `67465c16a7ac0b95f43b03a4fec6798a9fc7e8f0b9e6187519e25138809ad79d`.
- `docs/specs/010-001-documentary-contracts/spec.md`, draft-2, sha256 `3cf014dd82c8f264d3555e74bd7dea997bf6921227f8740042f19ed1d75c8fb0`.

**Dictamen: NO LISTO PARA APROBACIÓN, con 1 bloqueante.** Hay que corregir PC-12 e INV-07. El resto del diseño alcanza la intención del epic: D1–D4 no amplían alcance ni contradicen exclusiones, y el transporte es viable. Este dictamen no aprueba nada ni autoriza implementar; la decisión es de Pablo.

## Bloqueantes

### F1 — Required: el contrato obliga a escribir el nombre del dueño en texto instalable
- **Verdict:** BLOCKING
- **Bucket:** h
- **Ubicación:** `spec.md:164` (PC-12), con arrastre a `spec.md:188` (INV-07).
- **Evidencia:**
  - PC-12 prescribe que la norma haga corresponder la aceptación «a Pablo», y esa norma vive en `skills/cdad-cycle/references/documentary-contracts.md`, que se distribuye.
  - `rg Pablo skills sources agents` no da ninguna coincidencia hoy.
  - `tests/.sensitive-patterns.local` contiene un patrón que coincide con ese nombre (solo conté la coincidencia).
  - `tests/validate-consistency.sh:286-289` ya protege contra el nombre del dueño en el skill distribuible.
  - El epic exige que no haya datos privados en el producto instalable (`epics/.../plan.md:87-88`).
- **Consecuencia:** un implementer fiel a PC-12 introduce un dato privado en el producto. Un oráculo derivado del texto de PC-12 chocaría con esa regla, así que T2/T3 no podrían cumplir ambas a la vez.
- **Condición de cierre:** PC-12 debe decir «el usuario/dueño que aprueba» en la norma, igual que `sources/roles/orchestrator.md` («the USER approves»). «Pablo» queda solo en la autoridad de esta unidad (`docs/`). INV-07 debe aclarar lo mismo o limitarse a esta feature.

## Observaciones no bloqueantes

### F2 — Required: T1 puede publicar paquetes que T4 deja inválidos
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `plan.md:181`, `plan.md:42`.
- **Evidencia:**
  - T1 dice «preparar los encargos posteriores».
  - `render_packet` lee los bloques vigentes (`cdad_packet.py:1949-1952`).
  - La validación rechaza un paquete que difiera de su render (`cdad_packet.py:2140-2144`).
  - T4 modifica cinco bloques de rol.
- **Consecuencia:** los paquetes de T5/T6 preparados en T1 fallarían en intake. Falla de forma cerrada y se recupera, pero cuesta un ciclo y puede tentar a saltarse el control.
- **Condición de cierre:** T1 prepara solo T2/T3. Cada encargo posterior se prepara justo antes de su despacho, y T4 declara que los paquetes publicados antes de su cambio quedan obsoletos.

### F3 — Consider: «sin copiar íntegramente» no tiene un criterio verificable
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `spec.md:170` (PC-13), `spec.md:182` (INV-01), `plan.md:205`.
- **Evidencia:** el precedente mide unicidad por frases normativas con espacios normalizados (`tests/test_006_004_u3_principle_single_source.py`, punto 3 de su cabecera). El grupo D no lo adopta.
- **Consecuencia:** aparte de ese precedente, nada detecta copias parciales de la norma.
- **Condición de cierre:** declarar en el grupo D la unicidad por frases derivadas de la referencia, sobre `skills/`, `sources/` y `agents/`, o declarar que queda a revisión de T5.

### F4 — Consider: el foco de T3 no es un comando ejecutable
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `plan.md:83-85`.
- **Evidencia:** T3 ejecuta «Grupos A-C… seleccionados», pero T2 no obliga a publicar selectores. Con el módulo completo, el grupo D sigue rojo por diseño hasta T4.
- **Condición de cierre:** T2 expone una clase por grupo y el paquete de T3 fija los comandos exactos.

### F5 — Consider: invariantes sin trazabilidad propia
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `spec.md:193`, `spec.md:189`.
- **Evidencia:** el criterio 1 traza solo PC-01–16. INV-08 (una obligación no es un sandbox) no tiene postcondición que lo publique en la norma ni verificación en T2 o T5.
- **Condición de cierre:** incorporar INV-08 a PC-10 o a PC-09, o asignarlo expresamente a T5.

### F6 — Nit: T5 omite D4 en el examen semántico
- **Verdict:** OPTIONAL
- **Bucket:** l
- **Ubicación:** `plan.md:142`, `plan.md:304`.
- **Evidencia:** T5 solo nombra D1–D3, aunque el punto 4 contrasta fuente única y punteros.
- **Condición de cierre:** decir D1–D4, o justificar que D4 se agota en ese punto.

## Resultado por foco

1. **Trazabilidad:** PC-01–16 tienen grupo y T5 como revisión. Sus únicos huecos son F3 y F5. PC-02, PC-11 y PC-12 se declaran como prescripciones verificables por presencia y revisión, no como eficacia real, y eso es correcto.
2. **D1–D4:** son coherentes con `epics/.../plan.md:53-69`. No crean mecanismos nuevos ni tocan `stack`. El cambio del implementer (`spec.md:150`) no altera `_default_scopes` (`cdad_packet.py:2271-2274`), porque `docs` sigue fuera de sus alcances por defecto.
3. **Estructura frente a semántica:** los límites son suficientes (PC-09/10, INV-06, `validation_strategy`, `spec.md:166`). No encontré ninguna afirmación que presente un verde estructural como fidelidad.
4. **Transporte:** es viable y no hace falta tocar renderer, instalador ni esquema.
   - El bloque estático mayor mide 3397 bytes (`reviewer-plan-review`) frente a un techo de 12000, así que no hay presión para elevarlo.
   - Son exactamente cinco bloques de rol.
   - El árbol `cdad-cycle` se instala completo (`install.sh:327-347`).
   - El orquestador no tiene bloque de paquete, y el spec ya lo distingue (seis fuentes, cinco bloques).
   - `build/staging` está ignorado por git, así que la auditoría de ese árbol no puede basarse en `git diff`; el paquete de T4 debe contrastarlo por bytes.

## Abstentions

- **Agentes tras T4:** no ejecuté `make agents` ni la instalación. No puedo juzgar si los agentes del proyecto entran en DRIFT tras T4 ni cómo afecta eso a los despachos de T5/T6, con `republish-agents` y la instalación global sin tocar.
- **Citas de línea:** verifiqué solo una muestra de `spec.md` §8 y `plan.md`, no todas.
- **`docs/adr/`:** no contrasté la tabla de decisiones vigentes.
- **Buckets:** los asigné sin leer `references/verdict-tuple.md`; tómalos como orientativos.

## Evidencia

**Intake (ruta C):**
- Contexto de ejecución schema 2.
- `validate-request`: rc=0.
- `validate-packet`: rc=0.
- `PACKET.md` idéntico al render canónico completo (8571 bytes).
- La identificación de ruta C coincide en su inicio; comparé solo los primeros 300 caracteres.
- Los dos sha256 del contrato coinciden.

**Comandos:**
```bash
python3 -B scripts/cdad_packet.py validate-request --project-root . --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --request .cdad/packets/010-001-documentary-contracts-reviewer-plan-review-001/REQUEST.json
python3 -B scripts/cdad_packet.py validate-packet  --project-root . --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --request .cdad/packets/010-001-documentary-contracts-reviewer-plan-review-001/REQUEST.json --packet .cdad/packets/010-001-documentary-contracts-reviewer-plan-review-001/PACKET.md
python3 -B scripts/cdad_packet.py render --project-root . --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --request .cdad/packets/010-001-documentary-contracts-reviewer-plan-review-001/REQUEST.json [--route C]
sha256sum docs/specs/010-001-documentary-contracts/*
wc -c skills/cdad-cycle/packets/common.md skills/cdad-cycle/packets/roles/* skills/cdad-cycle/packets/substages/*
rg -n -c 'Pablo' skills sources agents
grep -c -i 'pablo' tests/.sensitive-patterns.local
git status --short
```

**Salidas relevantes:**
- `rg` sobre `skills sources agents`: sin coincidencias.
- `grep -c` sobre los patrones sensibles: 1.
- Bloque estático máximo: 3397 bytes.
- `git status` muestra las mismas tres rutas preexistentes.

**Archivos del repositorio modificados:** ninguno. **Commit:** ninguno. Un primer intento fallido de `render` escribió `/tmp/opencode_render.md` y `/tmp/opencode_err`, fuera del repositorio. No ejecuté suite, generación ni instalación.
