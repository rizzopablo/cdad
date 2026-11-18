# Re-verificación T8, 010-002: B1, B2, B3 y N1 cerrados, sin bloqueantes nuevos

**Recomendación:** T8 puede darse por cerrado y puede abrirse el cierre de la unidad. Esto es una recomendación, no una aprobación: decide el dueño. EV-07 sigue pendiente, porque le faltan la suite de cierre y la aceptación de la autoridad.

## Intake (ruta C)
Válido. El render completo es igual byte a byte a `PACKET.md` y `render --route C` coincide con la identificación recibida. El sha256 del contrato coincide (`0d630c49…`) y `execution.json` es v2.

## Mediciones propias (HEAD `7d3a85d9`, copia `git archive`)

| Comprobación | Resultado |
|---|---|
| Módulo 010-002, propiedades, `test_cdad_generate`, 010-001 y `TestPd13StaticBlockCeiling` | **58 passed**, rc=0, 235 s |
| `make agents` dos veces | rc=0, hash idéntico (`8e76d33e…`) |
| `diff -rq` contra `agents/` | Sin diferencias; 22 agentes |
| `git diff 58b0bcd7 HEAD -- tests` | Vacío |
| `validate-state` | VALID, rc=0 |

- **Alcance de `735d977c`:** 13 archivos, solo `sources/roles`, `sources/agents/adapters` y `agents`. No toca CLI, permisos, guardas ni defaults.
- **Suite completa:** no ejecutada, por política; la corre quien cierra.
- **Temporales:** usé `~/clawd/tmp/rv8b`, ya eliminado. No modifiqué nada del repo.

## Verificación

### B1: cerrado
- **Fuentes:** `sources/agents/adapters/opencode.md:76-82` y `claude-code.md:90-96`.
- **Generados:** `agents/cdad-orchestrator.md:311-317`; `agents/claude-code/cdad-orchestrator.md` compone el mismo texto.
- **Contenido:** declara «procedural duty, not a mechanical guard», detener y reportar, y prohíbe la sustitución silenciosa. El rechazo mecánico queda «to the external adapter alone» y no promete guarda nueva.
- **Coherencia:** concuerda con `sources/roles/orchestrator.md:79-83` y `:340-342`, con `skills/cdad-cycle/SKILL.md:142-148` y con `references/sub-agent-strategies.md:163-167`.
- **Laguna:** no se abre. El texto le niega al orquestador nativo cualquier guarda en la que apoyarse. `verify-begin` (`agents/cdad-orchestrator.md:184-188`) se describe por cabeza, ejecución, paquete e intento, y no menciona la publicación del agente.

### B2: cerrado
- **Misma sección:** `sources/roles/reviewer.md`, `implementer.md:99-105` y `test-writer.md:134-143` condicionan la batería dentro de `cdad-section:odoo`.
- **Agentes:** los seis `-odoo` coinciden con la generación limpia y sus controles de la sección pasan.
- **Regla de mezcla:** es operativa («both families», «both regimes»).
- **Prevalencia del diff:** explícita. Una etiqueta documental no exime lo que el diff modifica.
- **Dominio:** se conservan las cargas de skills, el juicio y el conocimiento.
- **P-5:** es coherente con la prohibición de comandos crudos, que sigue intacta en `test-writer.md:146`. Si el runner no cubre el verificador, el test-writer declara el límite de evidencia, así que tiene una salida legítima. No se conceden permisos nuevos.

### B3: cerrado
- **Sellos contra evidencia:**

| Evento | Sello |
|---|---|
| Dispatch | 09:45:32.48 |
| `received_at` | 12:45:47.98Z (09:45:47.98) |
| Receipt (mtime) | 09:45:48.006 |
| Bloque de rol | 09:45:48.129 |
| `tdd-green-t4` | 12:45:58.28Z (09:45:58) |

  El orden coincide con §3, y el bloque de rol se restauró después del receipt. Los hashes `d93b44e4…` y `ef3dab65…` están reproducidos.
- **Descripción de la operación:** §3 ya no la presenta como comparación. Dice que se ejecutó con «árbol restituido» y la califica de excepción a una guarda fail-closed.
- **Registro:** §7 fija que no es reutilizable y que una recurrencia exige corregir I-10 o una decisión del dueño. Es suficiente para que no se repita en silencio.
- **Límite:** los pasos 1 y 2, y el hecho de que corrieran en un solo script con `trap`, no dejan huella propia. Son declaración del orquestador. Los sellos solo son consistentes con ella y no la prueban.

### N1: cerrado para EV-02
- Los diez documentos están trackeados y sin diferencias con HEAD.
- **Precisión del objetivo:** `7d3a85d9` solo incorpora `red-t5`, `red-t8`, `tdd-t6-green`, `tdd-t7-properties`, `review`, `review-fix` y la enmienda. `red-t3`, `tdd-t4-green` y `owner-approval` ya estaban en commits anteriores. El efecto es el mismo.
- **EV-02:** recuperable desde el repositorio.
- **EV-07:** su base documental es recuperable, pero su evidencia de cierre todavía no existe.

## Bloqueantes nuevos
Ninguno.

## No bloqueantes nuevos

- **O1 — Registro del epic desactualizado (Consider, OPTIONAL, bucket h).** `docs/epics/epic-010-documentary-specialization/execution.md:100-101` sigue diciendo «Se acreditó comparando…». B3 citaba esa ubicación. No bloquea porque la misma frase remite a la desviación y su condición de cierre solo pedía corregir ese documento. Conviene alinearla al cerrar.
- **O2 — Condición más estrecha en dos roles (Nit, OPTIONAL, bucket m).** `implementer.md:99` y `test-writer.md:134` dicen «addon code», mientras el reviewer dice «code, views, security or data». Un diff solo de `security/` podría leerse como exento. Lo atenúan dos cosas: `skills/odoo-expert/SKILL.md:60` define el trabajo de addon de forma amplia, y un diff así no es «documentary-pure». Remedio: una remisión a esa frontera.
- **O3 — Rótulo impreciso en la desviación (Nit, OPTIONAL, bucket h).** §7 llama «restitución de la entrega (09:45:58)» a lo que fue el registro `delivery`. Según §3, la restauración ocurrió a las 09:45:48. Además, §7 no declara que esos sellos viven en `.cdad/`, ignorado por git, así que no son recuperables desde un clon.
- **O4 — Procedimiento de comprobación sin definir (Optional, OPTIONAL, bucket m).** El adaptador manda comprobar que el agente esté publicado, pero no dice cómo. Un orquestador no puede creer que ya lo comprobó, aunque el método queda a su criterio.
- **FYI — Digest histórico.** La transición T4 registra la desviación con `6109970e…`, y la versión enmendada es `c7ad1bdf…`. Es correcto: ese digest corresponde al blob de `1f3e1416`, que verifiqué, y `validate-state` da VALID.
- **FYI — P-5 no está en la spec.** La spec solo define P-1 a P-4. P-5 se añadió para resolver la decisión que pedía el cierre de B2. No amplía permisos, pero es una precisión que conviene que el dueño vea al aceptar.

N2, N3 y N4 quedan diferidos, sin reabrir.

## Abstenciones
- **Ejecución de los pasos 1, 2 y 5 de §3:** solo puedo juzgar su consistencia, no reconstruirla.
- **Conducta efectiva de modelos ante el texto nuevo:** los controles son estructurales (PC-13).
- **Revisión global de la unidad:** fuera del alcance de esta re-verificación limitada.

## Evidencia requerida
- **Archivos modificados:** ninguno.
- **Commit:** ninguno; revisé `7d3a85d9`.
- **Comandos principales:**
  - `scripts/cdad_packet.py render`, con y sin `--route C`
  - `make agents` ×2, seguido de `diff -rq`
  - `python3 -B -m pytest -q -p no:cacheprovider` sobre los cinco objetivos de la tabla
  - `cdad_packet.py validate-state --project-root .`
  - `git show`, `git diff`, `sha256sum` y `ls --time-style=full-iso`
