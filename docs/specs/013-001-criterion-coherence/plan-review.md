# Review del borrador: 013-001-criterion-coherence

**Objeto:** `docs/specs/013-001-criterion-coherence/spec.md`
**sha256:** `65a48f9280eadb090966bc34615e9463be3f6e76657a65d81733bab5c493e1fa`, recalculado y coincide. El commit del contrato es `null`; los bytes están en HEAD `43cd83c0`.

**Dictamen:** el borrador tiene **3 bloqueos**. La intención y el alcance coinciden con el plan, pero el recorrido de sustitución (promesa B) y la reconciliación de la suite completa (promesa E) no se pueden ejecutar tal como están escritos. Esto no es una aprobación; decide el dueño o su delegado.

## Admisión (ruta C)

- Hay un único bloque de identificación, y sus metadatos coinciden con `REQUEST.json` y `PACKET.md`.
- El contexto de ejecución es v2.
- `cdad_packet.py render --request …` terminó con rc=0, y `cmp` contra `PACKET.md` dio idéntico.
- No hay cuerpo inline.

## Hallazgos

Validación estructural: los hallazgos 1 a 3 son semánticos; el 4 y el 5 son de hechos y formato. Ninguno de los cinco es un defecto de esquema.

### 1. PC-6 envía el sustituto a una subfase que exige fallar antes de implementar (Required)

**Verdict: BLOCKING | Bucket: h**
**Ubicación:** `spec.md:101`, promesa B.

- **Evidencia:** `spec.md:101` dice que la creación del sustituto «pertenece a RED». Pero `packets/substages/test-writer-red.md:1` exige demostrar que falla «before implementation exists», y `handoff-prompts.md`, en su sección RED, dice «must FAIL».
- **Consecuencia:** un sustituto o consolidación por redundancia protege un comportamiento ya implementado y vigente, así que pasa en verde desde la primera ejecución. RED no puede cumplirse de buena fe, y esto afecta justamente al caso del piloto 013-003 (recorrido consolidado, discovery §7). El test-writer queda ante dos salidas malas: bloquearse o forzar un rojo artificial.
- **Secuencia:** la nota de `handoff-prompts.md` fija tres despachos, POST-AUDIT → RED → GREEN. El segundo POST-AUDIT posterior no aparece en ninguna superficie como cambio de esa secuencia, y la nota no se reconcilia.
- **Remedio:** declarar en PC-6 qué evidencia sustituye al rojo para un verificador de comportamiento ya existente, por ejemplo verde más sensibilidad demostrada. Indicar también en qué subfase existente se crea y actualizar la nota de secuencia.
- **Cierre:** la spec nombra la subfase y su evidencia, y la instrucción de RED deja de contradecirla.

### 2. Los gates mecanizados y la especialización Odoo quedan fuera de PC-12/13 (Required)

**Verdict: BLOCKING | Bucket: h**
**Ubicación:** `spec.md:134-146`, `148`, `177`, `179`.

PC-12 limita la suite completa a autorización expresa «también en cierre». Sin embargo, estas fuentes de exigencia no están en la tabla de superficies ni en PC-14:

- **Gate de CI:** `scripts/cdad-ci-gate.py:312-313` ejecuta `close --all` de forma incondicional.
- **ADR-039:** decisión 6, «la suite corre igual», aun en cambios solo documentales. Además rechaza expresamente la excepción como «decisión del dueño».
- **`docs/ci-gate.md:64-65`:** el criterio pide la suite en cada push.
- **`sources/roles/implementer.md:26`:** «run the FULL suite… All green». Se propaga a los agentes regenerados y contradice incluso la política vigente.
- **Odoo:** `skills/odoo-make-env/SKILL.md:32-34,137`, `references/run-budget-protocol.md:17-18`, `skills/odoo-test-writer/SKILL.md:130-132` y `sources/roles/reviewer.md:123` (`make test-clean` verde).
- **Otros consumidores:** `skills/cdad-epic/SKILL.md:119`, `assets/feature-plan-template.md:41`.

**Consecuencia:** tras la unidad seguirían vivas dos normas sobre el cierre, justo la contradicción que el plan encarga resolver. La fila genérica «consumidores de evidencia» no permite derivar un alcance de escritura, y un implementer podría cerrar sin tocar el rol que más ordena correr la suite. ADR-039 tampoco queda superado, aunque es una decisión vigente listada junto a ADR-020 en `systemPatterns.md`.

**Remedio:**
- Enumerar los consumidores.
- Ampliar PC-14 a ADR-039 con una decisión explícita: el gate es una herramienta que solo corre cuando alguien la autoriza, o queda como excepción declarada.
- Separar la **instalación limpia de addon** (`test-clean`) de la suite completa. Esa evidencia es específica y no debería caer como efecto colateral.

**Cierre:** cada línea citada tiene un destino en la tabla, y ADR-039 tiene una relación registrada.

### 3. El vocabulario de disposiciones no se puede consumir tal como queda (Required)

**Verdict: BLOCKING | Bucket: m**
**Ubicación:** `spec.md:75-87`, frente a `plan.md`, «Contratos entre features».

- **Evidencia:** el plan dice que 013-001 «fija los términos» y que 013-002 y 013-003 no los redefinen. La spec describe el retiro por desaparición del comportamiento (`spec.md:85`), pero no le da término y queda fuera de la tabla de cinco disposiciones. La plantilla y POST-AUDIT sí lo necesitan (`test-audit.md`, «Modified tests»; `test-writer-post-audit.md:1`, «delete»).
- **Consecuencia:** los consumidores tendrán que inventar un sexto valor o forzar «Sustituir», y este último exige un mapa de conservación que aquí no aplica.
- **Remedio:** añadir la fila **Retirar**, ligada a una obligación que desaparece por la spec, y decir cómo se relacionan las disposiciones con las secciones actuales de la plantilla.
- **Cierre:** todo test del AUDIT cae en exactamente una disposición con nombre.

### 4. Marca de estado obsoleta (Nit)

**Verdict: OPTIONAL | Bucket: h**
**Ubicación:** `spec.md:3`.

Dice «No materializado en el repositorio», pero el archivo está commiteado en `43cd83c0`. Solo afecta a los hechos del documento.

### 5. Localizadores imprecisos (Nit)

**Verdict: OPTIONAL | Bucket: m**
**Ubicación:** `spec.md:29`, `spec.md:37`.

- «A1–A8» no existe como etiqueta en `discovery.md`. Son §A.1–8; la etiqueta solo aparece en el addendum, sección (d).
- La fila «Política anterior» omite `epic-integration.md:76` y `SKILL.md:119`, que son gates equivalentes. Ya están cubiertos por el hallazgo 2.

## Verificado sin defecto

- **Skill auxiliar:** la decisión de corregir sin retirar coincide con el plan. La prescripción de `<30 seconds` está en `SKILL.md:85` y verde→merge en `:77,102`.
- **Propiedades:** las cuotas rivales citadas existen (`test-writer.md:101`, `handoff-prompts.md:494`, `re-entry.md:341`, Odoo `:141-147`).
- **Pre-RED:** el «import the modules» que PC-8 corrige existe en `handoff-prompts.md`.
- **Exclusión de `validate rc=0`:** es coherente con el plan, porque ese criterio es del epic y pertenece a 013-002.
- **Gold-plating:** no hallé ninguno bloqueante. PC-11 pide metadatos baratos que encajan con la semilla fija ya exigida.

## Abstentions

- **Tests:** no estimo cuántos tests quedarían afectados por el cambio de norma. Varios mencionan la política de suite (`test_005_005_t2_docs_policy`, `test_008_005_ci_gate`, entre otros), pero no los leí; eso corresponde al AUDIT.
- **`cdad-doctrine-check.py`:** no evalué si hace falta cambiarlo. Solo confirmé que ni él ni los tests fijan los literales `100-1000`, `<30 sec` o `closer runs`.
- **Fuentes externas:** no las contrasté. La spec tampoco las acredita.
- **Contrato de unidad:** no lo leí y no lo pude contrastar con la autoridad que cita `spec.md:5`.

## Evidencia

- **Archivos modificados:** ninguno. La tarea fue de solo lectura y no generó commit. El árbol sigue con `docs/.cdad-state.json` modificado y un discovery sin versionar, ambos ajenos a esta revisión.
- **Comandos:**
  - `python3 skills/cdad-cycle/scripts/cdad_packet.py render --project-root . --request <REQUEST>`, rc=0
  - `cmp` del render contra `PACKET.md`: SAME
  - `sha256sum spec.md`: coincide
  - `rg` y `sed` de solo lectura sobre las rutas citadas en cada hallazgo
- **Suite:** no ejecutada, según la política del paquete.