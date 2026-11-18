# Propuesta sustitutoria — sin cambio de mecanismo

**Borrador no aprobado. Recomiendo retirar el cargador propuesto y completar 019-003 mediante un encargo sucesor acotado.**

## 1. Diagnóstico

La investigación anterior convirtió una necesidad de aclarar el encargo en una nueva infraestructura de acceso. No encuentro esa infraestructura justificada para completar **este AUDIT**.

La conclusión no es «AUDIT no escribe, por tanto no tiene obligaciones documentales». El criterio es **qué debe verificar**:

- La especificación asigna la suficiencia y coherencia semántica de las instrucciones a la **revisión contextual independiente** (`spec.md:34–56,64–72`).
- El test-writer identifica protección existente y contribuciones faltantes; no recibe la aceptación semántica del documento como responsabilidad.
- Los informes parciales no identifican un nuevo verificador documental necesario: proponen mantener controles existentes y seleccionar revisión contextual (`test-audit-partial.md:34–38`; `test-audit-partial-002.md:35–41`).
- La obligación del bloque de rol es condicional: «when the artifact to verify is a document» (`skills/cdad-cycle/packets/roles/test-writer.md:2`). El substage AUDIT no impone una lectura documental adicional (`…/substages/test-writer-audit.md:1`).

Además, la norma documental limita expresamente su aplicación al producto documental y no concede accesos adicionales (`…/references/documentary-contracts.md:55–59,178–188`).

**Por tanto, puede completarse la selección de verificadores ejecutables existentes sin encargar al test-writer una verificación documental nueva ni la lectura del producto.** La fidelidad semántica sigue siendo obligatoria, pero corresponde al reviewer.

Esto no convierte los informes anteriores en auditorías completas retroactivamente ni autoriza ignorar una dependencia que realmente resulte necesaria.

## 2. Alternativas consideradas

**A. Precisar el encargo con las herramientas existentes — recomendada.**  
Usar el `objective`, los inputs y los scopes actuales. No requiere código, instalación ni permisos nuevos. Conserva íntegra la aceptación de PCs 1–6.

**B. Autorizar directamente la referencia instalada.**  
No basta con escribir su ruta: los inputs deben pertenecer al scope, y el test-writer no admite scopes de implementación (`skills/cdad-cycle/scripts/cdad_packet.py:1419–1475,2095–2112`). El guard también bloquea destinos externos (`scripts/claude-code-path-guard.sh:117–138`). No recomiendo rodearlo mediante Bash.

**C. Incorporar la referencia a las instrucciones congeladas.**  
El mecanismo existente captura exactamente common, rol y substage; no ofrece una referencia adicional arbitraria (`…/cdad_packet.py:1762–1879`). Manipular snapshots o copiar la norma no constituye una solución autorizada.

**D. Implementar el cargador del borrador anterior.**  
Introduce selección de fuentes, interfaz, validación, bootstrap y mantenimiento para una dependencia que este encargo no necesita. Su costo y frontera nueva no están justificados aquí.

El criterio elegido es resolver la responsabilidad efectiva, no generalizar un acceso cuya necesidad todavía no se ha demostrado.

## 3. Encargo sucesor propuesto

Publicar mediante el procedimiento existente, sin modificar paquetes históricos, con esta delimitación explícita:

> Complete the executable-test maintenance AUDIT for approved specification 019-003 using the authorized contract, existing tests and suite inventory/map. Identify existing protection, missing executable contributions and one disposition per selected verifier. No documentary verifier creation, documentary-content acceptance or implementation inspection is assigned. Identify contextual independent review required by the specification without performing or accrediting that review. Do not load documentary-contracts.md for this assignment or seek an alternative copy. If completing an assigned obligation genuinely requires that reference or implementation access, stop that obligation and report the precise dependency. Do not create RED without identified pending executable behavior.

Mantener los inputs autorizados de contrato, informes parciales, `systemPatterns`, mantenimiento, inventario, mapa y tests pertinentes. **Ninguna lectura de implementación ni edición de tests en AUDIT.** No entregar al test-writer los hallazgos de implementación de esta investigación.

### Postcondiciones de esta corrección de encargo

1. **AUDIT utilizable:** cada promesa identifica protección existente, límites, disposición y verificación seleccionada; ninguna coincidencia textual acredita suficiencia semántica.
2. **Responsabilidad conservada:** la revisión contextual independiente cubre las obligaciones semánticas de PCs 1–6; no se declara realizada desde AUDIT.
3. **Aislamiento conservado:** no se lee producto, metodología candidata ni una copia alternativa; una dependencia nueva se reporta.
4. **Historia conservada:** los paquetes e informes anteriores permanecen intactos; el resultado sucesor obtiene aprobación antes de continuar.

**Verificación:** revisión independiente de esta interpretación y del encargo; después, AUDIT independiente y aprobación en el procedimiento existente. No añado un gate.

**Aceptación:** encargo sin obligaciones incompatibles y AUDIT suficiente para decidir la continuación, sin suplantar la revisión final.

## 4. Tratamiento de los tres bloqueantes

Los tres hallazgos siguen siendo válidos **contra el borrador 002**. No afirmo haber corregido un cargador inexistente.

Propongo retirar sus PCs 7–10 y su plan B0–B5:

- **Interfaz:** no se introduce ninguna.
- **Bootstrap candidato:** no se ejecuta ni despliega un runtime nuevo.
- **Raíces y symlinks:** no se incorpora una operación de lectura externa que necesite esa frontera.

Si posteriormente aparece una dependencia metodológica externa indispensable, requerirá una propuesta específica. Este encargo no la autoriza anticipadamente.

### deferred-hardening

- Cargador general y acceso externo: necesidad no demostrada.
- Ejercicios adicionales en dos runtimes: no corresponden a una funcionalidad nueva.
- Garantías universales de cumplimiento o sandbox: no prometidas.

No se difiere ninguna obligación aprobada de 019-003 ni de 019-002.

## 5. Evidencia y siguiente paso

**Revisión examinada:** `5becdc28ebfe7fc38eca19ef39415c85b01a41da`.

Ruta C validada mediante `validate-request`, `validate-packet` y `render --route C`, con las rutas recibidas y el contexto declarado. Ambos validadores terminaron correctamente; la identificación coincidió.

Comparación completa, en memoria, contra `render`:

```text
render rc: 0
full canonical equality: True
bytes: 7905
contract sha256 matches: True
execution schema: 2
Python: 3.13.5
```

Los comandos exactos y programas de contraste constan íntegros en las llamadas de esta sesión.

**Archivos modificados:** ninguno. **Commit:** ninguno. **Tests:** no ejecutados. Al entrar y salir, `git status --short` mostró únicamente la modificación preexistente de `docs/.cdad-state.json`.

**Siguiente paso:** revisión independiente focal de esta propuesta; si se acepta bajo la delegación vigente, registrar la decisión y publicar el AUDIT sucesor. No abrir una feature de cargador ni modificar la instalación.