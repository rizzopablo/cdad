## Dictamen

**El bloqueo es real; no encontré una excepción general acreditada para leer referencias instaladas.** Recomiendo una aclaración acotada de instrucciones, **sin cambiar el renderer, el guard ni el esquema de paquetes**.

Este es un borrador, no una aprobación ni una autorización de implementación.

### Evidencia y límites

- El paquete recibido es válido: REQUEST y PACKET pasan validación; el PACKET coincide con el render canónico completo: **8.108 bytes**.
- El renderer admite selectores relativos al proyecto y prohíbe al test-writer scopes de implementación. La referencia del repositorio no cabe en el scope del AUDIT-002 (`skills/cdad-cycle/scripts/cdad_packet.py:295–310,1419–1475,2095–2112`).
- Hay una autorización expresa y separada para cargar skills de dominio, pero no una equivalente para cualquier referencia metodológica. La recepción de paquetes tampoco amplía el alcance de producto (`sources/roles/architect.md:26–45`).
- La orden documental exige leer la referencia, mientras el encargo permite hacerlo solamente si su scope lo admite. El auditor hizo bien en detener esa porción (`skills/cdad-cycle/packets/roles/test-writer.md:2`; REQUEST del AUDIT-002:9,30–43).
- El guard real de Claude Code rechazó tanto la referencia del proyecto —clasificada como implementación— como su ruta instalada externa. **No se abrió ninguno de esos destinos durante la prueba del guard.**
- El analizador `cdad_guard.py` devuelve `allow` para rutas externas porque no las gobierna la política del proyecto. Eso **no acredita autorización contractual** y no equivale al comportamiento del hook de Claude Code (`scripts/claude-code-path-guard.sh:117–138,211–215`; `skills/cdad-cycle/scripts/cdad_guard.py:492–508`).
- La congelación actual comprende common, role y substage; **no congela transitivamente los documentos que estos mencionan** (`cdad_packet.py:1760–1879`).

Revisión examinada: `3bfd475efb36cd6ee35836f77878fb5d2c08845e`.

La referencia documental del working tree coincide con HEAD, SHA-256:

```text
a1e0aeafa61a265ffa7c4bc4c013cfef53ee9b71aa5d4298d57f2f6f176be58a
```

**Límites:** no inspeccioné la instalación externa ni ejecuté una sesión real en un proyecto consumidor. En ese caso comprobé las funciones reales con una política de consumidor suministrada en memoria; no presento esa simulación como prueba de integración.

## Resolución propuesta

Usar una **representación documental protegida de la referencia metodológica**, autorizada como input dentro del proyecto, con identidad, revisión y hash fijados en el nuevo encargo.

No sería una nueva casa normativa: sería evidencia congelada de la fuente canónica, sin edición independiente. Tampoco permitiría leer el candidato bajo prueba, aunque tenga el mismo nombre.

Esto reutiliza dos mecanismos existentes:

- Fuentes recuperables mediante una representación dentro del alcance autorizado (`documentary-contracts.md:38–59`).
- Separación del baseline examinado cuando las instrucciones son el producto (`spec.md:26–28`).

Descarto ampliar scopes a `skills/**`, reclasificar la implementación como documentación o permitir genéricamente lecturas fuera del proyecto. Esas alternativas conceden más acceso del necesario y no resuelven por sí solas identidad ni procedencia.

## Enmienda propuesta a 019-003 — no aprobada

Se conservan PCs 1–6. Añadir:

### Promesa D — Las referencias necesarias pueden consultarse sin romper el aislamiento

**PC-7. Referencia autorizada y distinguible del producto.**  
Cuando una instrucción exige consultar una referencia metodológica que el destinatario no puede leer por su alcance, el encargo identifica una representación protegida y autorizada de esa referencia. Declara:

- Identidad canónica y revisión examinada.
- Ruta documental autorizada y SHA-256 esperado.
- Procedencia y responsable de preparar la representación.
- Exclusión del alcance editable del productor.

El test-writer no obtiene esa representación del candidato ni inspecciona implementación para completarla. Una ruta instalada o un nombre coincidente no constituyen autorización.

**Verificación:** revisión contextual independiente del encargo, procedencia, instrucciones efectivas y separación respecto del producto.

**Criterio/evidencia:** el informe permite recuperar la fuente y comprobar que el destinatario dispone de un input legítimo, sin acceso adicional a implementación.

**PC-8. Ausencia o divergencia no se resuelven con fallback.**  
El destinatario comprueba el hash esperado antes de utilizar la representación. Si falta la representación, falta su identidad verificable, difieren los bytes o existen instrucciones incompatibles, detiene esa porción y solicita corrección. No busca silenciosamente otra copia ni carga el ciclo completo.

La comprobación de bytes acredita identidad del snapshot, no suficiencia semántica.

**Verificación:** revisión contextual de instrucciones y casos de aceptación con representación correcta, ausente y divergente.

**Criterio/evidencia:** los casos muestran continuación solamente con el input autorizado y detención explícita en los restantes, sin lecturas alternativas.

**PC-9. Publicaciones históricas intactas.**  
La aclaración se publica mediante encargos nuevos. No modifica REQUEST, PACKET ni snapshots de publicaciones anteriores; tampoco incorpora referencias adicionales a `instruction_sources`, cuyo contrato vigente sigue limitado a las tres fuentes canónicas.

**Verificación:** comparación atribuible de publicaciones históricas y nuevos consumidores; reutilización de los controles existentes de integridad y render.

**Criterio/evidencia:** los originales permanecen intactos y el nuevo encargo declara explícitamente la representación y su hash.

### Alcance de implementación

Aclarar la resolución de referencias en las instrucciones canónicas de paquetes y sus consumidores afectados. Ajustar los pointers necesarios para que consultar la representación declarada satisfaga inequívocamente la obligación, sin copiar la norma en cada consumidor.

**No se especifica comportamiento ejecutable nuevo.** El renderer continúa validando scopes e inputs como hoy; el guard conserva sus rechazos. La identidad de esta representación se comprueba mediante el encargo y la verificación declarada, no mediante una garantía inexistente del renderer.

Si la implementación descubre que necesita modificar un mecanismo ejecutable, debe detener esa ampliación y volver con una promesa observable concreta y **RED/GREEN independiente**. No corresponde fabricar RED para esta aclaración semántica.

### Aceptación y regresión

Además de la revisión contextual, comprobar con controles existentes:

- **Self-host:** representación protegida accesible; candidato de `skills/` todavía inaccesible al test-writer.
- **Consumidor ordinario:** el mismo encargo funciona sin exigir una ruta externa ni un checkout de CDAD.
- Ausencia/divergencia producen detención, no selección de otra copia.
- Publicaciones congeladas anteriores conservan su contenido.

La revisión registra versiones, rutas realmente usadas y límites. Una simulación de clasificación no sustituye la comprobación de los consumidores efectivos.

### deferred-hardening

- Acceso directo general a metodología instalada: innecesario para esta resolución.
- Congelación transitiva automática de referencias: ampliaría el protocolo sin necesidad demostrada.
- Detección automática de contaminación o garantía de sandbox: no prometidas.
- Compatibilidad universal entre instalaciones y versiones: fuera del alcance; una divergencia debe quedar visible.

## Secuencia para desbloquear el AUDIT

1. **Revisión independiente y aprobación explícita** de esta enmienda y su estrategia. El AUDIT-002 permanece parcial.
2. El orquestador fija el baseline metodológico admitido. **VERIFY:** comprobar la instalación si se pretende atribuirle esa procedencia; esta investigación no certifica sus bytes.
3. Materializa la representación protegida y fija su hash en el nuevo encargo. No copia el candidato ni permite al productor editar ese input.
4. Produce y revisa independientemente la aclaración semántica mínima. Esto requiere autorización específica; no habilita cambios ejecutables incidentales.
5. Publica un **sucesor coherente**, bajo los gates vigentes, con la representación expresamente autorizada. No modifica los paquetes históricos ni pide al auditor reinterpretar silenciosamente el anterior.
6. Una sesión independiente de test-writer completa el AUDIT desde contrato, baseline y tests autorizados. No debe recibir este contexto de implementación investigado.
7. Continúa T1 de 019-003 y su revisión contextual según el contrato aprobado.

**Impacto en `plan-draft.md`:** anteponer este desbloqueo acotado a la continuación del AUDIT y aclarar la preparación del baseline. Mantener T1, la separación del test-writer y las obligaciones de 019-002. La previsión de detenerse ante un consumidor bloqueante ya existe en su línea 25.

## Evidencia operativa

Comandos de validación ejecutados desde la raíz declarada:

```bash
python3 -B scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/019-003-contract-verification-strategy-architect-draft-001/REQUEST.json
python3 -B scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/019-003-contract-verification-strategy-architect-draft-001/REQUEST.json --packet .cdad/packets/019-003-contract-verification-strategy-architect-draft-001/PACKET.md
python3 -B scripts/cdad_packet.py render --project-root . --request .cdad/packets/019-003-contract-verification-strategy-architect-draft-001/REQUEST.json --route C
```

Ambas validaciones finalizaron correctamente y la identificación coincidió. Las llamadas `shell` de esta sesión contienen íntegros los programas de reproducción en memoria y sus salidas. Resultados relevantes:

```text
complete canonical render equality: True bytes: 8108
live norm inside AUDIT-002 declared scope: False
implementation scope: REJECT
docs scope sobre skills/: REJECT
absolute/../ scope: REJECT
protected docs baseline scope: ACCEPT
CC guard project reference: rc=2
CC guard installed reference: rc=2
CC guard approved contract: rc=0
```

Python utilizado: **3.13.5**.

**Archivos modificados por esta tarea:** ninguno.  
**Commit:** ninguno.  
**Tests/suite completa:** no ejecutados; se realizaron reproducciones de diagnóstico, no una acreditación de suite verde.  
El único dirty observado al entrar y salir fue `docs/.cdad-state.json`, preexistente.

**Sin publicación, despliegue ni modificación de la instalación actual.**