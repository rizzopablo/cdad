# Revisión del borrador de acceso a metodología

**Objeto:** `docs/specs/019-003-contract-verification-strategy/reference-access-amendment-draft-002.md`  
**SHA-256:** `e19913da53ec8308782ea50d2c7874617b44b0e57daf59b48533c8faef02a2bc`

## Hallazgos

### 1. La interfaz se deja para después de la revisión y aprobación

**Required — Verdict: BLOCKING · Bucket: m**

El borrador enumera los datos que debería contener `methodology_references`, pero no define su representación, la identidad de cada referencia ni la forma exacta de seleccionar una. La CLI es solo un ejemplo y el propio texto indica que su interfaz definitiva debe fijarse antes de RED (borrador, líneas 73–93). Sin embargo, B0 propone revisar y aprobar **esta** enmienda antes del AUDIT y RED (líneas 161–182).

Eso deja sin una interfaz aprobada al test-writer independiente: no puede escribir verificadores de declaración, selección, diagnóstico y entrega sin inventar parte del contrato o recibir una definición posterior que esta revisión no cubrió. La especificación aprobada exige criterios anteriores a la producción y que los cambios necesarios vuelvan por revisión y aprobación (PC-4, `spec.md:52–56`).

**Cierre verificable:** presentar y revisar antes de RED un contrato protegido que fije los campos y sus reglas, identificación y selección de referencia, invocación, canales de salida y fallos observables. Alternativamente, declarar explícitamente una revisión y aprobación adicional de esa interfaz antes del AUDIT y RED, sin atribuirlas a la aprobación de este borrador.

### 2. Falta una ruta autorizada para usar el cargador candidato sin desplegarlo

**Required — Verdict: BLOCKING · Bucket: m**

El borrador prohíbe actualizar la instalación operativa (`:157`) y exige después que una sesión fresca de test-writer use la vía nueva para completar el AUDIT original (`:204–208`). También distingue correctamente que el wrapper del repositorio ejecuta los assets candidatos y no selecciona automáticamente la instalación vigente (`:38–43`).

No identifica, sin embargo, **qué ejecutable concreto usará el destinatario en B5**, cómo se seleccionará y acreditará su versión ni cómo se autoriza esa ejecución sin convertir la implementación candidata en lectura de producto del test-writer. Las instalaciones de prueba de aceptación (`:212–225`) no establecen que una instalación de prueba aceptada sea la herramienta autorizada para el encargo sucesor real.

**Consecuencia:** aun con GREEN y observaciones satisfactorias, el sucesor puede recibir la CLI instalada antigua —sin el subcomando— o necesitar una ejecución cuya autoridad y separación de lectura no están resueltas. El desbloqueo prometido se detendría precisamente en B5.

**Cierre verificable:** definir una ruta de bootstrap y de reanudación que nombre la distribución candidata, su selección y procedencia, autorización para ejecutarla y separación respecto de los inputs de producto; demostrarla en el runtime efectivo sin modificar la instalación operativa. Si requiere despliegue, hacerlo una decisión y gate explícitos, no una suposición.

### 3. La autorización de la carga no cierra la frontera de rutas y alias

**Required — Verdict: BLOCKING · Bucket: m**

PC-8 declara una raíz instalada, una ruta relativa y un hash (`:75–81`), y ordena rechazar destinos dentro del producto, escapes o alias hacia él (`:95–103`). Pero no fija cómo se vincula la **raíz resuelta y el destino efectivo** con la instalación expresamente aprobada, ni qué constituye un escape cuando hay symlinks o una raíz declarada falsamente.

La revisión humana de la autorización (`:85`) es necesaria, pero la operación propuesta debe aplicar la declaración aprobada sin transformar una raíz o referencia manipulada en una lectura autorizada. El hash identifica los bytes, no acredita por sí mismo su procedencia, como reconoce el propio borrador (`:152–155`). Dado que el cargador abre mediante un proceso una ruta que el guard rechaza directamente (`:38–41, 146`), esa frontera es parte funcional del mecanismo, no una garantía del guard.

**Consecuencia:** una implementación puede cumplir literalmente con «destino fuera del producto» y «digest coincidente» sin demostrar que leyó la referencia de la instalación admitida. El destinatario podría consumir otra fuente bajo una identificación engañosa o el mecanismo podría convertirse en una vía indirecta de lectura no autorizada.

**Cierre verificable:** definir la relación entre declaración aprobada, raíz y destino reales, incluyendo resolución de symlinks, contención y rechazo de declaraciones incompatibles con la autorización. Los verificadores deben distinguir una referencia admitida de raíces falsas, escapes y alias hacia producto u otras ubicaciones no admitidas, sin reclamar que el mecanismo sea un sandbox.

## Evidencia y límites de la revisión

- Contrasté el borrador con la especificación aprobada, la revisión anterior, los tests existentes de recepción congelada y las fuentes de revisión y contratos documentales. Los tests existentes consultados no constituyen evidencia del comportamiento nuevo.
- Validé la ruta C con `cdad_packet.py validate-request`, `validate-packet` y `render --route C`: ambos validadores finalizaron sin error y la identificación renderizada coincidió con la recibida.
- `sha256sum` devolvió el digest indicado arriba. La comprobación de la tabla de decisiones no encontró rutas de ADR inexistentes; los ADR no incluidos que inspeccioné se declaran propuestos.
- No ejecuté tests ni una sesión real de destinatario; esta es una revisión de especificación, no una aceptación de implementación. No modifiqué archivos ni hice commit. `git status --short` mostró `M docs/.cdad-state.json`, preexistente durante esta revisión.

## Abstentions

- No determino que el esquema y las observaciones propuestas sean la **solución mínima**: el borrador documenta límites de las rutas actuales, pero no presenta una comparación suficiente de alternativas más pequeñas con sus costos y autoridad.
- No puedo acreditar que los dos ejercicios operativos sean ejecutables en los runtimes y permisos reales hasta que se concrete y pruebe la ruta señalada en el hallazgo 2.
- No atribuyo una vulnerabilidad ya existente: el cargador todavía no está implementado.

**Dictamen:** tres hallazgos bloqueantes sobre el borrador identificado. La revisión no aprueba la enmienda; la decisión corresponde al responsable autorizado.