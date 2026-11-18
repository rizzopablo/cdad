# Borrador sustitutorio — acceso a metodología instalada

**Estado: no aprobado. Sin implementación ni despliegue.**

## Dictamen

La alternativa viable es **separar expresamente las instrucciones metodológicas instaladas del alcance de lectura del producto**, mediante una carga acotada y verificable. No basta con indicar otra ruta.

Recomiendo un pequeño cambio ejecutable en el protocolo de paquetes y su CLI, acompañado por instrucciones coherentes. **No recomiendo copiar la referencia, reclasificar `skills/`, abrir lecturas externas genéricas ni modificar el guard para permitirlas.**

El AUDIT original permanece parcial hasta verificar ese mecanismo y publicar un encargo sucesor.

## 1. Hechos comprobados

Revisión examinada del repositorio: `69c01a4fbe68d8cc104ea166a2c08aa0796ac720`.

### La instalación existe y esta referencia tiene procedencia contrastable

La referencia efectiva examinada es:

```text
~/.agents/skills/cdad-cycle/references/documentary-contracts.md
SHA-256: a1e0aeafa61a265ffa7c4bc4c013cfef53ee9b71aa5d4298d57f2f6f176be58a
```

Sus bytes coinciden con:

- La entrada correspondiente del manifiesto de instalación.
- El archivo de la revisión instalada declarada, `ff678d212d4dee400c9cc5a7a4bfe89c9e56941a`.
- El archivo del HEAD examinado.

El marcador `version.txt` y el manifiesto declaran esa revisión instalada. **El manifiesto también registra conflictos en otros archivos:** estos resultados acreditan la referencia examinada, no una instalación íntegra ni uniformemente actualizada.

La igualdad actual entre referencia instalada y candidato tampoco convierte al candidato en input autorizado.

### Los mecanismos actuales no resuelven la carga

- Los inputs y selectores del paquete son relativos al proyecto; el test-writer no admite scopes de implementación (`cdad_packet.py:1419–1475,2095–2112`).
- El hook de Claude Code rechaza tanto la referencia del proyecto como la instalada externa. La reproducción devolvió respectivamente `rc=2` y `rc=2`; el contrato autorizado devolvió `rc=0` (`scripts/claude-code-path-guard.sh:117–138,211–215`).
- El analizador de preflight permite destinos externos porque no los gobierna la política del proyecto. **Eso no concede autorización contractual ni reproduce el hook** (`cdad_guard.py:462–508`).
- Bash es deliberadamente permisivo; emplear `cat` para superar el rechazo seguiría siendo una infracción contractual, no una solución (`sources/roles/test-writer.md:62–75`).
- El paquete congela únicamente common, role y substage. No congela transitivamente sus referencias (`cdad_packet.py:1760–1879`).
- Los assets del renderer se resuelven respecto del propio script, mientras los agentes derivados tienen otro resolvedor. Ejecutar el wrapper del repositorio usa sus assets candidatos; **no selecciona automáticamente la metodología instalada** (`scripts/cdad_packet.py:10–11`; `cdad_packet.py:2127–2128,4715–4728`).

**Conclusión:** no encontré una solución existente que reúna autorización, selección inequívoca, comprobación de bytes y consumo sin segunda lectura.

## 2. Enmienda propuesta

Se conservan PCs 1–6 de la especificación aprobada. Se añaden las siguientes promesas.

### Promesa D — El rol conoce qué metodología está autorizado a usar

**PC-7. Autoridad explícita y separada del producto.**

Antes de publicar un encargo que necesite metodología fuera de su alcance de producto, el orquestador registra y somete a aprobación:

- La referencia metodológica aplicable al rol y a la tarea.
- La instalación admitida y su ruta resuelta.
- La revisión de procedencia y los bytes contrastados mediante SHA-256.
- El fundamento recuperable de esa elección.
- La distinción entre referencia vigente y producto candidato.

La propuesta concreta para desbloquear este caso es admitir la referencia instalada identificada arriba, **sujeto a aprobación explícita de esta enmienda**. Ni su nombre, ni su hash, ni su presencia en una instalación confieren autoridad por sí solos.

Una divergencia entre instalación y fuente aprobada bloquea la carga. Una divergencia del candidato no cambia la metodología vigente: el candidato continúa siendo producto bajo evaluación.

**Verificación:** revisión contextual independiente de la elección, procedencia, instrucciones efectivas y separación de responsabilidades.

**Aceptación:** existe una aprobación recuperable que identifica inequívocamente la referencia admitida. El productor no decide ni modifica esa elección.

### Promesa E — La carga entrega solamente los bytes metodológicos declarados

**PC-8. Declaración congelada y carga específica.**

Añadir al REQUEST un campo opcional **propuesto**, `methodology_references`, con una lista cerrada de declaraciones que identifiquen:

- Referencia relativa dentro del skill instalado.
- Raíz instalada resuelta.
- Revisión de procedencia.
- SHA-256 esperado.
- Referencia recuperable a la autorización.

Esta declaración **no es un `read_scope` de producto**, no contiene el documento ni incorpora referencias adicionales a `instruction_sources`.

La publicación incorpora únicamente declaraciones previamente aprobadas. La revisión del encargo contrasta esa correspondencia: la validación estructural no acredita por sí sola autoridad normativa.

Añadir una operación específica **propuesta**, por ejemplo:

```text
cdad_packet.py load-methodology --project-root ROOT --request REQUEST --reference ID
```

Su interfaz definitiva debe quedar fijada en el contrato aprobado antes de RED. No existe actualmente.

La operación:

1. Valida el paquete y selecciona exclusivamente una referencia declarada.
2. Resuelve su destino y rechaza destinos dentro del producto del proyecto, escapes o alias hacia ese producto.
3. Lee el archivo instalado una vez en memoria.
4. Comprueba el digest de ese mismo buffer.
5. Solo tras el éxito entrega ese buffer y su identificación: paquete, referencia, ruta resuelta, revisión y digest.

No admite una ruta arbitraria alternativa ni descubre instalaciones mediante búsqueda.

**PC-9. Ausencia, divergencia y sustitución no producen fallback.**

Ante referencia no declarada, instalación ausente, destino inadmisible, lectura fallida o digest divergente, la operación termina con diagnóstico y **sin entregar contenido metodológico**. El rol detiene la porción dependiente y solicita corrección; no consulta el candidato, otra instalación ni el ciclo completo.

El contenido utilizado es exclusivamente el devuelto por la carga verificada, no una reapertura posterior del archivo. Así:

- Una modificación anterior o durante la lectura solo puede aceptarse si el buffer obtenido coincide con el digest aprobado.
- Una modificación posterior no altera el buffer ya entregado.
- Una nueva carga vuelve a comprobar identidad; no reutiliza una autorización para aceptar bytes diferentes.

Esto establece identidad de los bytes consumidos por el mecanismo. No demuestra por sí mismo que cualquier agente siga sus instrucciones.

**Verificación:** pruebas deterministas independientes del comportamiento observable, con RED por ausencia de ese comportamiento y GREEN posterior; observación acotada del destinatario efectivo.

**Aceptación:** los casos válidos entregan exactamente los bytes aprobados; los rechazados no entregan contenido ni seleccionan otra fuente.

### Promesa F — El acceso nuevo no altera el aislamiento ni la historia

**PC-10. Publicaciones históricas y guard conservados.**

- Los paquetes antiguos conservan sus bytes y su comportamiento de renderizado.
- La declaración nueva queda congelada en cada publicación; renderizarla no depende de que la referencia instalada siga disponible.
- Validar integridad del paquete y cargar metodología son comprobaciones distintas: un paquete históricamente válido puede tener una dependencia actualmente no consumible.
- Un cambio de referencia exige aprobación y una publicación sucesora, no reparación del REQUEST anterior.
- El guard sigue rechazando lecturas directas de implementación y destinos externos. No se añaden excepciones genéricas.
- El test-writer sigue sin leer implementación del proyecto, incluido el candidato metodológico.
- Una denegación real del runtime al mecanismo autorizado se reporta; no se sustituye por `cat`, otra herramienta o una copia.

**Verificación:** regresión focal de integridad, congelación, scopes y guard, más revisión contextual de los consumidores afectados.

**Aceptación:** no existe ampliación del alcance de producto ni modificación de publicaciones históricas.

## 3. Alcance técnico y límites

### Cambios necesarios

1. **Renderer/CLI:** declaración opcional, validación de su forma, representación canónica y operación de carga verificada.
2. **Instrucciones de intake y paquetes:** distinguir metodología declarada de inputs del producto; ordenar su carga antes del trabajo dependiente y detenerse ante fallo.
3. **Consumidores generados:** regeneración por el mecanismo existente.
4. **Dispatch:** comprobar mediante sus pruebas que transporta y verifica correctamente el nuevo render. Solo modificar su código si se demuestra una necesidad concreta; hoy ya usa el verificador compartido (`cdad_dispatch.py:503–514,545–558`).

**No se requiere abrir el guard:** la vía nueva es una operación explícitamente autorizada, estrecha y sometida a TDD, no un permiso de lectura directa ni un rodeo informal por Bash.

Los consumidores legacy y ligeros deben expresar la misma distinción. Si una consulta metodológica ya está autorizada por su ruta vigente, se conserva. Si queda bloqueada, se prepara explícitamente un encargo compatible o se informa el bloqueo; no se cambia silenciosamente de ruta.

### Límites retenidos

- Ninguna garantía de sandbox o ausencia universal de lecturas.
- Ninguna autenticación criptográfica del aprobador añadida por este cambio.
- El hash acredita identidad, no bondad ni autoridad del contenido.
- La revisión contextual acredita la elección normativa dentro de su alcance.
- La observación del rol acredita solamente las ejecuciones examinadas.
- No se publica ni actualiza la instalación operativa bajo esta propuesta.

## 4. Plan de desbloqueo sin autorización circular

### B0 — Revisar y aprobar el requisito previo

Un reviewer independiente examina esta enmienda, su interfaz propuesta y su verificación. El orquestador, bajo la delegación registrada para epic 019, decide y registra la aprobación correspondiente. El architect no la aprueba.

Materializar el contrato protegido antes de cualquier producción, preservando la versión anterior de la especificación y la condición parcial del AUDIT.

### B1 — AUDIT acotado del mecanismo ejecutable

Asignar una sesión independiente de test-writer:

- **Objeto:** comportamiento ejecutable de declaración, carga, rechazo e integridad; no fidelidad semántica de documentos.
- **Inputs:** contrato aprobado, interfaz pública fijada, tests e inventario autorizados.
- **Lecturas:** docs y tests delimitados; ninguna implementación.
- **Salida:** selección y disposiciones de verificadores para PCs 8–10.

Esta tarea no necesita consultar la norma documental para evaluar un producto documental: verifica un mecanismo ejecutable usando fixtures sintéticos derivados del contrato. La obligación documental del packet vigente es condicional (`packets/roles/test-writer.md:2`). No se reinterpreta ni completa con ello el AUDIT bloqueado original.

Si otra instrucción efectiva impidiera esta asignación, se reporta antes de proceder; no se elimina informalmente.

### B2 — RED independiente

Tras aprobar el AUDIT acotado, el test-writer escribe los verificadores faltantes. El fallo RED debe ser una aserción sobre el comportamiento pendiente, no simplemente “subcomando desconocido”.

Reutilizar protección existente cuando corresponda; no imponer un test por postcondición.

### B3 — GREEN y coherencia de instrucciones

El implementer recibe contrato y tests protegidos; modifica únicamente implementación e instrucciones autorizadas. No modifica aceptación, referencias vigentes ni verificadores.

La integración de instrucciones recibe revisión contextual, además de los tests ejecutables.

### B4 — Revisión y aceptación del requisito previo

El reviewer independiente contrasta:

- Contrato y candidato.
- Evidencia RED/GREEN.
- Separación entre metodología y producto.
- Consumidores efectivos.
- Observaciones de aceptación descritas abajo.

Aceptar únicamente sin bloqueantes pendientes. La publicación o despliegue siguen sujetos a su autorización separada.

### B5 — Reanudar el trabajo original

Publicar un sucesor coherente del encargo original, con la referencia expresamente admitida y la vía ya verificada.

Una sesión fresca de test-writer completa el AUDIT original sin recibir los hallazgos de implementación de esta investigación. Después continúa T1 de 019-003 y su revisión contextual. Las obligaciones de 019-002 permanecen intactas.

## 5. Comprobación operativa de aceptación

Ejecutar sobre **dos entornos delimitados**:

- Self-host: checkout candidato separado de la instalación metodológica admitida.
- Consumidor independiente: proyecto pequeño con política propia, sin necesitar un checkout de CDAD; utiliza una instalación de prueba ordinaria.

Las instalaciones de prueba son ejercicios de distribución, **no copias documentales dentro del proyecto para eludir permisos**. Nunca alterar la instalación operativa del usuario para provocar fallos.

En cada entorno:

1. **Referencia correcta:** iniciar una sesión real de test-writer, validar el paquete, invocar la carga y observar continuación de una tarea acotada. Registrar ruta y digest efectivamente entregados.
2. **Referencia ausente:** retirar únicamente el archivo de la instalación de prueba. Observar diagnóstico, ausencia de contenido y detención de la tarea dependiente.
3. **Referencia divergente:** cambiar sus bytes manteniendo la declaración. Observar rechazo, incluso cuando exista una copia correcta en otra ubicación.
4. **Cambio entre comprobación y uso:** prueba determinista coordinada, sin depender de sleeps, que cambie el archivo después de capturar el buffer. La salida debe ser exactamente el buffer verificado, nunca una segunda lectura. Un cambio previo que altere el buffer debe rechazarse.
5. **Aislamiento conservado:** comprobar que el acceso directo al candidato y al destino externo sigue rechazado por el guard correspondiente.

Conservar comandos, versiones, hashes, salidas y trazas de herramientas de las sesiones observadas. Las trazas permiten examinar que **en esas ejecuciones** no hubo fallback ni lectura del candidato; no prueban ausencia universal de accesos.

No hace falta repetir íntegramente todas las rutas de transporte: seleccionar una ruta efectiva por entorno y cubrir la integridad de A/C con la regresión existente pertinente.

### Aceptación global

PCs 7–10 requieren conjuntamente:

- Elección normativa revisada y aprobada.
- RED/GREEN independiente satisfactorio para el mecanismo nuevo.
- Regresión focal pertinente.
- Observaciones efectivas satisfactorias en ambos entornos.
- Revisión contextual sin bloqueantes.
- Aceptación explícita del responsable autorizado.

### deferred-hardening

- **Congelación transitiva del contenido:** no se incorpora; la declaración queda fijada y una dependencia divergente bloquea.
- **Permisos generales para metodología externa:** innecesarios y demasiado amplios.
- **Sandbox y prevención universal de contaminación:** fuera del mecanismo propuesto.
- **Compatibilidad universal de instalaciones y runtimes:** no prometida; registrar exactamente los ejercitados.
- **Oráculo automático de autoridad o fidelidad semántica:** corresponde a aprobación y revisión contextual, no a comparación de hashes.

## 6. Evidencia de esta investigación

Desde `<repo>`:

```bash
python3 scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/019-003-contract-verification-strategy-architect-draft-002/REQUEST.json
python3 scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/019-003-contract-verification-strategy-architect-draft-002/REQUEST.json --packet .cdad/packets/019-003-contract-verification-strategy-architect-draft-002/PACKET.md
python3 scripts/cdad_packet.py render --project-root . --request .cdad/packets/019-003-contract-verification-strategy-architect-draft-002/REQUEST.json --route C
```

Ambos validadores finalizaron correctamente. La identificación coincide con la recibida. Comparación completa contra el render canónico:

```text
PACKET full canonical equality: True
bytes: 8078
sha256: f751c8af653c57b78e64b9fbe102515541fc50db051f559706f686b79157e193
```

Las llamadas de esta sesión conservan íntegros los programas de diagnóstico y sus salidas: contraste del manifiesto con archivos y blobs Git, resolución de assets y reproducción del hook sin abrir sus destinos.

**Python:** 3.13.5.  
**Archivos modificados por esta tarea:** ninguno. **Commit:** ninguno.  
**Tests y suite completa:** no ejecutados; los diagnósticos no constituyen GREEN ni aceptación end-to-end.  
**Estado observado al entrar y salir:** únicamente `M docs/.cdad-state.json`, preexistente.