# 010-000 — Raíces equivalentes en continuidad

**Estado: aprobado por Pablo el 2026-10-29.**

## 1. Descripción funcional

Una raíz de proyecto relativa que identifica el mismo directorio que una absoluta debe permitir las mismas operaciones de continuidad, planificación, verificación de paquetes y clasificación de rutas. La normalización no debe modificar la evidencia portable ni convertir un escape real en una ruta admisible.

El defecto identificado compara un candidato absoluto resuelto con una raíz todavía relativa. Normalizar una variable local del CLI no basta: la raíz utilizada por los handlers y las entradas programáticas debe ser coherente.

Fuentes: `skills/cdad-cycle/scripts/cdad_packet.py:279–293`; `skills/cdad-cycle/scripts/cdad_continuity.py:1012–1038,1154–1164,3172–3197`.

## 2. Contrato y alcance

Para un proyecto válido, se consideran equivalentes las raíces que, desde el CWD de la llamada, resuelven al mismo directorio. Esto incluye `.`, `..`, un nombre relativo de directorio y su ruta absoluta cuando corresponda. También incluye una raíz absoluta que atraviesa un symlink al mismo proyecto: la equivalencia se determina por resolución, no solamente por convertir a ruta absoluta.

Un symlink usado para expresar la raíz del proyecto no se confunde con una referencia interior cuyo destino escape de esa raíz.

La corrección comprende las interfaces existentes:

- CLI de continuidad: `begin` y `checkpoint`.
- API de continuidad: `plan_write`, para ambas operaciones.
- API de paquetes: `verify_published_packet`.
- Clasificación: `classify_path` y `classify_path_observable`.
- Conversiones y controles compartidos necesarios para esas operaciones.

Se conserva la semántica actual de los demás argumentos: en continuidad, contexto y update del CLI relativos se interpretan respecto del proyecto; las entradas de packet relativas al CWD no cambian de base.

La fuente corregible es `skills/cdad-cycle/scripts/`. Los wrappers de `scripts/` y una instalación global no sustituyen su corrección.

**Fuera de alcance:** nuevas interfaces, cambios de esquema, rediseño del ciclo o del instalador, especialización documental, instalación global y publicación. Tampoco se incorpora containment resuelto nuevo a `update.references`; se conserva su control léxico actual y se declara su limitación en `deferred-hardening`.

### Decisión de diseño

Se prefiere normalizar coherentemente la raíz en los bordes y operaciones afectados, manteniendo los controles de pertenencia existentes. Las excepciones exclusivas para `"."` o exigir rutas absolutas al usuario no resuelven la familia del defecto. No se exige un nuevo subsistema general de rutas ni refactorizar consumidores ajenos.

Añadir ahora containment a todas las referencias de continuidad sería otra modificación de seguridad y compatibilidad, no una corrección de equivalencia de raíces. Se mantiene separada y explícitamente pendiente.

## 3. Promesas observables y postcondiciones

### Promesa A — La forma de expresar la raíz no impide trabajar

**PC-01.** Un nuevo `begin` válido y un `checkpoint` válido obtienen éxito con raíces relativas y absolutas equivalentes, partiendo del mismo estado inicial para cada operación. Publican el mismo efecto lógico correspondiente; el `begin` queda verificable mediante el mecanismo existente.

**PC-02.** Con entradas idénticas y raíces equivalentes:

- `plan_write`, para `begin` y `checkpoint`, devuelve el mismo envelope, bytes planificados y destinos físicos equivalentes;
- `verify_published_packet` admite el mismo paquete y devuelve documentos equivalentes;
- `classify_path` y `classify_path_observable` conservan su clasificación y precedencia vigentes, sin falsos escapes ni errores residuales de conversión relativa.

**PC-03.** `plan_write` continúa siendo exclusivamente planificador: no crea, modifica ni elimina archivos, tanto al producir un plan como al reconocer replay o rechazar una operación.

**Razón de usuario:** el uso normal desde distintos directorios y la integración programática no deben depender de conocer una restricción accidental del CLI.

### Promesa B — La continuidad conserva evidencia e idempotencia

**PC-04.** Para el mismo estado inicial y contenido de `begin` o `checkpoint`, cambiar solamente la expresión de la raíz conserva los bytes canónicos del cuerpo durable, identidad, referencias y digests, secuencia y enlaces previos. La normalización no incorpora la ruta absoluta de la instalación o del proyecto a los campos portables.

**PC-05.** Repetir contenido ya publicado utilizando otra raíz equivalente conserva el replay existente: `no_op` verdadero, ninguna escritura planificada o publicada y cadena sin cambios. Un conflicto de contenido conserva su rechazo. Se mantiene el reconocimiento de replay acreditado antes de exigir elegibilidad para un efecto nuevo, sin omitir las comprobaciones previas de identidad.

**Razón de usuario:** una corrección de rutas no debe duplicar trabajo ni invalidar evidencia previamente emitida.

### Promesa C — La comodidad no amplía la autoridad

**PC-06.** La normalización no modifica decisiones de admisión: un paquete alterado respecto de su render canónico o un efecto nuevo sin autoridad vigente sigue rechazándose antes de publicar continuidad. Se conservan las restricciones existentes de propietario, suspensión y referencias contractuales protegidas.

**PC-07.** Se conservan los controles de rutas existentes, distinguiendo estas dos superficies:

**Pertenencia por resolución.** En las entradas siguientes, ya procesadas mediante `_project_path` dentro de las operaciones alcanzadas, siguen rechazándose traversal con componentes `..`, rutas absolutas donde se exige una relativa y symlinks cuyo destino resuelve fuera del proyecto:

- Ruta de policy: `policy.path` y la ruta canónica `docs/cdad-policy.json`.
- Entradas de `path_policy`: `implementation_roots`, `test_roots`, `colocated_test_roots`, `documentation_roots`, `implementation_files`, `documentation_files`, `test_files` y `private_paths`; también las entradas de `temporary_roots` cuando se validan o utilizan.
- Ruta consultada mediante `raw_path` en `classify_path` y `classify_path_observable`, y los selectores de rutas de policy utilizados para clasificarla.
- Rutas verificadas durante la admisión del paquete: `contract.path`, `contract.spec_path` cuando existe, `inputs[].path`, selectores `root` o `path` de `read_scope` y `write_scope`, el directorio contractual derivado y las referencias de autoridad cuando las comprueban los validadores existentes.

Esta enumeración no convierte prefijos o sufijos de nombres de tests en rutas ni añade controles a argumentos que actualmente no pasan por ese mecanismo. Se conserva además la comprobación existente de que el directorio de un paquete pertenece al árbol de paquetes.

**Control léxico de continuidad.** `update.references`, tanto en `begin` como en `checkpoint`, conserva su normalización actual y el rechazo de rutas absolutas o de traversal cuyo resultado normalizado salga de la raíz. No se promete rechazo por symlink exterior para estas referencias: el digest actual no comprueba pertenencia resuelta y corregirlo queda fuera de esta unidad.

Los rechazos exigidos ocurren antes de publicar efectos: estado, head y cuerpos existentes permanecen idénticos; no aparecen nuevos cuerpos ni se modifica el destino exterior utilizado como testigo.

Esto exige atomicidad **ante rechazo de validación**, no añade una garantía transaccional frente a fallos de disco o interrupciones del proceso.

**Razón de usuario:** aceptar raíces relativas legítimas no debe debilitar las barreras existentes ni dejar continuidad parcial.

### Promesa D — La corrección llega al consumidor instalado

**PC-08.** Desde una copia aislada del producto corregido se genera staging y se instala mediante la vía existente:

```bash
make staging
CDAD_INSTALL_ROOT="$ISOLATED_ROOT" CDAD_SKILL_EXTRA_DIRS="" bash install.sh
```

`ISOLATED_ROOT` es una ruta absoluta a un directorio existente del entorno aislado.

Los CLI instalados de continuidad y packet se ejecutan contra un consumidor sintético sin wrappers del checkout. Reproducen el éxito de `begin` y `checkpoint` con raíz relativa y su equivalencia con raíz absoluta. También reproducen el rechazo sin publicaciones de una entrada insegura sujeta al containment existente definido en PC-07, no de un symlink exterior en `update.references`. Los scripts instalados corresponden a la fuente corregida.

La instalación queda confinada al entorno aislado; no se instala globalmente ni se publica.

**Razón de usuario:** un arreglo que funciona solamente desde el checkout no resuelve el problema del producto distribuido.

## 4. Invariantes verificables

- No cambian firmas públicas, esquemas ni vocabulario de clasificación.
- La raíz canónica sirve para operar y comprobar pertenencia; no reemplaza referencias relativas en evidencia portable.
- No se elimina el containment existente ni la comparación íntegra del paquete canónico.
- `update.references` conserva su control léxico; esta unidad no introduce containment resuelto para esas referencias.
- Se conserva el orden vigente de identidad, replay/conflicto y elegibilidad del efecto nuevo.
- La corrección no altera la interpretación independiente de otros argumentos relativos.
- Tests y verificadores permanecen bajo el rol competente; GREEN no modifica sus oráculos.

## 5. Verificación y aceptación

La aceptación requiere:

1. Evidencia vinculada a cada PC, sin postcondiciones pendientes ni fallos en las comprobaciones pertinentes.
2. RED previo a GREEN que reproduzca el defecto real de un nuevo `begin` con raíz relativa; no basta una operación que termine por replay.
3. Comparación desde estados iniciales equivalentes para medir publicación de `begin` y `checkpoint`; repetición sobre una misma cadena para medir replay.
4. Comparación de bytes, inventario de archivos y destinos resueltos para distinguir equivalencia lógica, portabilidad y ausencia de efectos.
5. Evidencia de equivalencia que contemple raíces relativas, absolutas y una raíz expresada mediante symlink al mismo proyecto, sin confundirla con referencias que escapan.
6. Evidencia de conservación de los controles enumerados en PC-07, distinguiendo pertenencia resuelta de normalización léxica.
7. Evidencia de generación, instalación aislada y ejecución efectiva de los CLI instalados.
8. Revisión independiente contra esta spec y aprobación explícita del usuario.

Se agrupan escenarios equivalentes bajo una misma PC; no se fija una cantidad de tests. Las regresiones existentes de autoridad, replay y admisión aportan evidencia reutilizable, sin duplicarlas por cuota. La ejecución completa se rige por la política común del paquete.

## 6. deferred-hardening

- **Containment resuelto de `update.references`: deuda de seguridad explícita.** Actualmente `_digest_references` lee el destino de `root / rel` después del control léxico, sin comprobar que el destino resuelto pertenezca al proyecto. Una referencia mediante symlink puede leer y digerir un archivo exterior. Incorporar su rechazo requiere una decisión separada sobre seguridad y compatibilidad; no se amplía este fix para resolverlo.
- **Carreras de symlinks y cambios concurrentes del filesystem:** diferidos; para las entradas con containment existente se conserva la comprobación sobre el filesystem examinado, sin introducir resistencia a TOCTOU.
- **Fallos de disco e interrupciones entre escrituras:** diferidos; no son la causa del defecto y ampliarían el contrato transaccional.
- **Nuevas plataformas, rendimiento y fuzzing general de rutas:** diferidos; no hay una promesa de portabilidad o rendimiento nueva en esta unidad.
- **Refactorización de todos los consumidores de rutas:** diferida; se corrige la superficie afectada y sus controles compartidos necesarios.

No se difieren los rechazos por symlink exterior en las entradas con containment existente enumeradas en PC-07, la planificación sin efectos ni la verificación instalada comprometidas arriba.

## 7. Evidencia técnica del borrador

Interfaces y comportamiento contrastados en:

- `skills/cdad-cycle/scripts/cdad_continuity.py:1012–1168,3172–3197`: planificación y handlers compartidos de `begin` y `checkpoint`, replay, admisión y publicación.
- `skills/cdad-cycle/scripts/cdad_continuity.py:232–247,489–509`: resolución de argumentos, normalización léxica y digest de referencias sin containment resuelto.
- `skills/cdad-cycle/scripts/cdad_continuity.py:931–958`: envelope durable y campos portables.
- `skills/cdad-cycle/scripts/cdad_packet.py:228–244,279–330,343–427,496–555`: campos de policy, pertenencia, clasificación y raíces temporales.
- `skills/cdad-cycle/scripts/cdad_packet.py:1210–1212,1254,1345–1425,1695–1758`: rutas de autoridad, policy, scopes, contratos e inputs.
- `skills/cdad-cycle/scripts/cdad_packet.py:1297–1301`: precedente de resolución de la raíz en el CLI.
- `skills/cdad-cycle/scripts/cdad_packet.py:1917–1974`: pertenencia del directorio del paquete y admisión canónica.
- `Makefile:10–13`, `install.sh:518–525,1261–1285`: generación, raíz aislada e instalación del árbol del skill.
- `install.sh:301,391–396`: `--basic` obsoleto y sin efecto.
- `tests/test_role_packet_consumers.py:31–148`: precedente de consumidor instalado aislado.

**Pendiente de ejecución, no presentado como resultado:** regresiones del fix, publicaciones en fixtures, comprobaciones de symlinks, staging e instalación aislada.

Status: Approved by Pablo on 2026-10-29
