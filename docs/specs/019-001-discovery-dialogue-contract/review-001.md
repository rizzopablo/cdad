# Revisión independiente — 019-001

**Resultado: hay bloqueos documentales.** El diseño todavía no ofrece una instrucción inequívoca sobre cómo una corrección autorizada llega al borrador, dónde recuperar el contexto antes de redactar cuando no existe archivo de discovery, ni cómo aplicar la delegación de aprobación. No apruebo el diseño; la decisión corresponde a la autoridad designada.

## Hallazgos bloqueantes

### 1. Una corrección autorizada puede quedar fuera del borrador

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

En `handoff-fidelity.md:7-18`, cada entrada pertenece a **una sola clase** y «correction» es distinta de «confirmed decision». Sin embargo, `:56-61` indica que **solo las entradas confirmadas no sustituidas** alimentan la redacción. El ejemplo de `:76-86` clasifica DC-06 como corrección, no como decisión confirmada. Así, una lectura literal excluye tanto la decisión anterior —porque fue sustituida— como su corrección.

**Consecuencia:** el arquitecto puede redactar sin el requisito corregido, precisamente la pérdida de significado que PC-3 y PC-4 deben evitar.

**Cierre verificable:** definir que una corrección con autoridad recuperable es una decisión vigente utilizable, sin ambigüedad respecto de la clasificación, y hacer consistente el procedimiento, el ejemplo y el contenido del handoff.

### 2. El soporte alternativo del contexto puede no existir antes del borrador

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

`handoff-fidelity.md:25-29` prescribe el artefacto de discovery para el diálogo, pero, cuando no existe un archivo separado, remite a la sección «Technical context» del **borrador**. Al mismo tiempo, `readiness-and-approval.md:19-26` exige que los insumos sean recuperables por una sesión nueva **antes** de redactar. La fuente citada, `stage-1-discovery.md:59-63`, dice que la salida técnica pasa a esa sección en Stage 2; no establece que exista un borrador durable disponible durante el diálogo previo.

**Consecuencia:** en ese camino, el orquestador no tiene instrucciones claras sobre dónde registrar respuestas y correcciones para entregarlas a una nueva sesión del arquitecto. Se compromete la recuperación de contexto de D2 y PC-3/PC-4.

**Cierre verificable:** identificar un artefacto existente y autorizado disponible antes del borrador, o precisar cómo se materializa esa sección sin atribuir al arquitecto escritura prohibida ni añadir un subsistema; mostrar el handoff de recuperación para ese camino.

### 3. La prohibición de aprobación contradice la delegación reconocida por el propio diseño

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**

`roles-and-dialogue.md:16-22` admite aprobación por un agente de mayor jerarquía cuando está expresamente delegada, y `readiness-and-approval.md:44,66` contempla que el orquestador apruebe bajo delegación de epic. Pero `roles-and-dialogue.md:49-53` ordena que el orquestador **nunca apruebe una especificación**, sin excepción.

**Consecuencia:** una activación que copie ambas instrucciones deja al agente sin una regla inequívoca para una delegación válida, incluida la modalidad admitida para esta unidad.

**Cierre verificable:** expresar una única frontera: prohibición ordinaria y excepción explícitamente delegada, con sus límites y autoridad registrable, alineada en todas las secciones y el mapa de activación.

### 4. Faltan ejemplos de ambos resultados para comportamientos comprometidos

**Severidad:** Required · **Verdict: BLOCKING** · **Bucket: m**

PC-10 exige un ejemplo pretendido y uno inaceptable para **cada comportamiento de fidelidad**. El índice de `examples.md:204-231` no sustituye esa comparación:

- **Exclusión autorizada de una elección conductual:** `readiness-and-approval.md:14,22` permite resolver el bloqueo mediante exclusión explícita; B-05 (`examples.md:51-57`) solo muestra que se pregunta y se mantiene el bloqueo, frente a elegir un default. No ilustra la exclusión autorizada frente a una exclusión no autorizada o silenciosa.
- **Límite de `VERIFY`:** `readiness-and-approval.md:15` lo permite solo si subsiste un compromiso inequívoco y verificable. B-06 (`examples.md:59-65`) enumera `VERIFY`, pero no muestra cuándo es admisible frente a una incertidumbre que impide ese compromiso.

**Consecuencia:** los ejemplos no enseñan dos decisiones límite que determinan si puede avanzarse legítimamente; una lectura operativa puede confundir «hay una limitación» con «hay un compromiso verificable».

**Cierre verificable:** añadir para ambos comportamientos ejemplos contrastados que muestren autoridad, efecto sobre readiness y resultado inaceptable, sin presentarlos como observaciones reales.

## Resultados por postcondición

**Versiones examinadas:** producto en el árbol de trabajo sobre HEAD `f6132cc86ac391de15a52f633db4716e5ac73b5c`; último commit que afectó el directorio del producto `1f6aad5876a826ea10145ce54a366c42ec7ce24c`. Fuentes históricas declaradas por el producto: `64aa4670`; discovery examinó `265174993b4213be9a96545578016657bc8b09ba`. SHA-256: spec `1e50141c91b84a309be92d115c8df025a1fb5e138dc0ba35b2c13f74bd864853`, discovery `6d77f4ba7c342bdf7c99f5b8b8a506eed71a021ebc035456be302a090357bb43`, checklist `41161a34802e0a4945de042f03b2e65f146c827342d0433079924f3d94a9a83f`.

Las rutas abreviadas del producto se refieren a `docs/specs/019-001-discovery-dialogue-contract/operating-design/`. La fuente contractual es `spec.md`, PC correspondiente; discovery es `discovery.md` de la misma unidad.

1. **PC-1 — No satisfecho.** `roles-and-dialogue.md:7-35` asigna actividades y describe la ida y vuelta; la asignación de aprobación entra en conflicto con `:49-53`. Fuente: spec D1 y discovery §3.B. Hallazgo 3.
2. **PC-2 — No satisfecho.** `roles-and-dialogue.md:44-70` y `activation-map.md` R1/R2/R11 establecen cambios y separaciones, pero incluyen la prohibición contradictoria del hallazgo 3. Fuente: spec PC-2; discovery §3.A.
3. **PC-3 — No satisfecho.** `handoff-fidelity.md:7-18,47-61` distingue categorías y procedencia, pero la regla de alimentación del borrador excluye literalmente la corrección ilustrada. Hallazgo 1. Fuente: spec D2/PC-3.
4. **PC-4 — No satisfecho.** El ejemplo `handoff-fidelity.md:63-100` contiene los cuatro datos solicitados, pero su utilización como entrada de redacción queda contradicha por `:56-61`; además, el soporte anterior al borrador no está resuelto para todos los caminos (`:25-29`). Hallazgos 1 y 2. Fuente: spec PC-4.
5. **PC-5 — Satisfecho en las reglas.** `readiness-and-approval.md:9-26` distingue respuesta parcial, silencio, propuesta, elección pendiente y supuesto técnico, incluido el límite de `VERIFY`. La insuficiencia de ejemplos correspondientes se registra bajo PC-10. Fuente: spec D3/PC-5.
6. **PC-6 — No satisfecho.** `readiness-and-approval.md:33-73` separa borrador, revisión y aprobación e identifica la ruta de reentrada; la autoridad de aprobación contradice la prohibición absoluta citada en el hallazgo 3. Fuente: spec PC-6; discovery §3.D.
7. **PC-7 — Satisfecho.** `lightweight-paths.md:17-72` distingue variante trivial del ciclo y trabajo independiente, obligaciones y proporcionalidad. Fuente: spec D4/PC-7; discovery §2. No acredita ejecución de ninguno de los dos caminos.
8. **PC-8 — No satisfecho.** `activation-map.md` R1–R12 mapea propietarios, consumidores, variantes Odoo, instrucciones preparadas y legacy; sin embargo, las contradicciones de los hallazgos 1–3 impiden una propuesta de activación inequívoca. Fuente: spec PC-8; discovery §§3–4.
9. **PC-9 — Satisfecho.** `activation-handoff-019-002.md:18-62` asigna las cuatro correcciones y regresiones focalizadas: entrega única de brainstorm, reentrada de draft, paquetes congelados e idle/status/apertura. Fuente: spec D5/PC-9; discovery §§3.C–F. No se afirma que estén implementadas.
10. **PC-10 — No satisfecho.** Los ejemplos están marcados como ilustrativos (`examples.md:1-6`), pero faltan contrastes para exclusión autorizada y límite de `VERIFY`. Hallazgo 4. Fuente: spec PC-10 y D3.
11. **PC-11 — Satisfecho como protocolo.** `acceptance-protocol-019-002.md:9-79` exige tanto el recorrido completo J1–J7 como evidencia observable de los cinco casos, con entradas protegidas, respuestas, tratamiento, versiones y límites. Fuente: spec PC-11 y criterio 5. **No se ha observado el ejercicio.**
12. **PC-12 — Satisfecho como procedimiento de verificación.** `verification.md:5-39,53-69` identifica checklist protegido, revisión semántica independiente, resultados por PC y prohibición de aceptar evidencia faltante. El registro de materialización nombrado existe fuera del producto. Fuente: spec PC-12 y criterio 6. Esta revisión es el informe, no la aceptación.

## D1–D5 y comprobaciones transversales

- **D1:** la mediación y la conservación del trabajo técnico del arquitecto están descritas; la regla de aprobación delegada es contradictoria. Hallazgo 3.
- **D2:** la atribución y reutilización están propuestas, pero los hallazgos 1 y 2 impiden considerarlas fieles y coherentes en todos los caminos.
- **D3:** las reglas de readiness reflejan la intención; faltan ejemplos límite exigidos por PC-10. Hallazgo 4.
- **D4:** distingue los dos caminos ligeros y comparte reglas sin imponer cuestionario ni cuota.
- **D5:** conserva brainstorm como consulta técnica y asigna su incompatibilidad de entrega a 019-002.

**Sin maquinaria nueva:** no identifiqué una propuesta de nuevo rol, estado, gate, servicio o campo de paquete. `current_decisions` se mantiene separado de propuestas y preguntas (`handoff-fidelity.md:25-34`).

**Límite de activación:** el producto declara que es documental y que no activa instrucciones (`README.md:3-5,72-77`). No se acredita despliegue ni cumplimiento observado.

**No bloqueantes:** ninguno adicional con suficiente evidencia para elevarlo.

## Evidencia de ejecución

- La validación de paquete `python3 scripts/cdad_packet.py validate-packet` con el request, packet y execution context identificados terminó sin salida y con éxito. `render --route C` devolvió la identificación recibida; el contexto declara `schema_version: 2`.
- `sha256sum` confirmó los tres hashes indicados arriba. `git rev-parse HEAD` devolvió `f6132cc86ac391de15a52f633db4716e5ac73b5c`. El producto no aparecía modificado en `git status --short` para su directorio.
- Revisé primero la checklist protegida y luego contrato, discovery y producto. No ejecuté suite: la especificación establece revisión semántica independiente como verificación de esta unidad documental.
- **Archivos modificados por esta revisión:** ninguno. **Commit creado:** ninguno.

## Abstentions

- No verifiqué independientemente **cada** locator histórico ni toda la afirmación del producto sobre el diff entre revisiones; sí contrasté los locators necesarios para los hallazgos y los resultados señalados.
- No puedo acreditar por esta revisión ejecución real de agentes, despliegue, compatibilidad universal de runtime ni correcciones ejecutables de 019-002.