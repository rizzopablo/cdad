# Dictamen plan-review (segunda vuelta) — 010-003-documentary-pilot

**Objeto:** `plan.md` v3, sha256 `76307105…7c87`, y `spec.md` v2, sha256 `d3a9be99…1aa9`. Los digests coinciden con los bytes en disco.

**Intake:** ruta C con contexto v2. `validate-request` dio rc=0, `validate-packet` rc=0 y `render | cmp PACKET.md` rc=0. La identificación coincide con `render --route C`.

**Recomendación: aprobable con cambios.** B-1..B-4 están cerrados en el texto, pero hay **un bloqueante nuevo (BN-1)**, y cerrarlo requiere una decisión de la autoridad. Este dictamen no aprueba nada.

## Bloqueantes anteriores

| # | Veredicto | Ubicación | Fundamento |
|---|---|---|---|
| B-1 | **Cerrado** | `spec.md:35,141`; `plan.md:199,212` | Input exacto de la norma. El selector mecánico es la raíz `skills/cdad-cycle/references`, porque `_validate_scope` rechaza una ruta exacta `implementation` no declarada en la política. La raíz es más amplia que la autorización, pero el plan lo declara, y las otras referencias quedan como exclusión contractual. La norma solo nombra las clases de defecto, igual que el contrato. |
| B-2 | **Cerrado en sus dos piezas, pero con la operatividad afectada por BN-1** | Razón: `spec.md:47`, `plan.md:23`. Exclusión: `spec.md:143`, `plan.md:201-206`. Invalidación: `spec.md:145,221`, `plan.md:224`. Límite no técnico: `spec.md:69`, `plan.md:31` | Exclusión e invalidación están presentes. Las clases de scope admiten el recorte (`plan.md:208-213`): contrato por ruta exacta y raíces disjuntas bajo `tests`, para un reviewer al que `_validate_scope` permite todas las clases. |
| B-3 | **Cerrado según su condición**, con refuerzo recomendado en NB-1 | `spec.md:71-80,118`; `plan.md:121-129,215` | Hay commit identificado, registro con sha256 por artefacto e inspección sin respuestas, y comprobación antes del despacho. La inspección la hace el orquestador, no el productor. |
| B-4 | **Cerrado** | `spec.md:22,160,162`; `plan.md:158,242-249`; bloque T4 y T6 | Candidato obligatorio en T4. T6 recibe candidato, clave y `challenge-contrast.md` en sesión distinta. Sin ellos, PC-11 y PC-13 no tendrían referente, y ahora se exigen. |

**O-1..O-8:** los ocho están presentes.

| Nit | Ubicación |
|---|---|
| O-1 | `plan.md:21` |
| O-2 | `spec.md:93-100`, `plan.md:109-115` |
| O-3 | `spec.md:102,128` |
| O-4 | `plan.md:321,333` |
| O-5 | `plan.md:221` |
| O-6 | `spec.md:162`, `plan.md:281` |
| O-7 | `spec.md:149`, `plan.md:230-231` |
| O-8 | `spec.md:67,141`, `plan.md:205` |

## Bloqueante nuevo

### BN-1 — El bloque común del paquete manda revisar el diff completo, que incluye lo excluido
**Required · Verdict: BLOCKING · Bucket: h**

- **Ubicación:** `plan.md:194-215`; `spec.md:143`; `skills/cdad-cycle/packets/common.md`, tal como se renderiza en este mismo paquete.
- **Fundamento:**
  - El bloque del reviewer dice: «the complete diff against the approved contract for approved contracts». T5 lleva por contrato `approved-feature-spec` (`_contract_for`), así que ese texto le aplica.
  - El diff de la unidad contiene `oracle/`, `structural/` y `product/`.
  - El mismo bloque común manda «Read only declared inputs and scope», de modo que el paquete se contradice.
  - INV-06 y D-5 impiden editar los bloques de `packets/{roles,substages}`, y el texto del diff no se puede quitar.
  - `plan.md:215` obliga a detenerse si «el paquete impone otra lectura fuera de los insumos autorizados».
- **Consecuencia:** es la misma clase de defecto que B-1, pero en la dirección peligrosa. Según lo que haga el reviewer:
  - Si obedece el bloque, lee `product/` u `oracle/` y el ensayo de un solo tiro queda invalidado.
  - Si el orquestador aplica `plan.md:215` al pie de la letra, T5 no se despacha.
  - Si nadie lo nota, la exclusión queda sin efecto real, justo donde el encargo pide que sea operativa.
- **Condición de cierre:** declarar en spec y plan que `objective` e `invariants` de T5 fijan como objeto revisado solo `challenge/negative.md` frente a los insumos. Deben negar expresamente el diff y las operaciones git que muestren contenido, y `plan.md:215` debe reconocer esa precedencia. También vale cualquier otra vía sin tocar los bloques.
- **Decisión de la autoridad:** debe decidir si una precisión de `objective` basta frente a un bloque común contradictorio. No tomo esa decisión. Si no basta, corregir `common.md` queda fuera de esta unidad y T5 debe esperar esa corrección.

## No bloqueantes

| # | Tupla | Ubicación | Hallazgo y remedio |
|---|---|---|---|
| NB-1 | Required · OPTIONAL · h | `spec.md:71-78`; `plan.md:121-127,145`; bloque T3 | **La fijación admite tres huecos.** (a) El commit se exige «antes de T5», no antes de T4, mientras T3 promete «protegidos antes de GREEN» e INV-02 pide secuencia anterior a GREEN. Así, la clave podría cambiar con el producto ya existente sin que se note. (b) El verificador tiene sha256 en el registro, pero no está en el commit listado. (c) Nada exige versionar `preparation-record.md` antes de T5, así que un tercero no puede fechar la inspección. Las fechas de git tampoco prueban orden por sí solas. **Remedio:** commit de preparación antes de T4 y con el verificador; registro versionado antes del despacho; request de T5 citando ambos; `challenge-review.md` en un commit descendiente. |
| NB-2 | Required · OPTIONAL · h | `spec.md:84,113,170`; `plan.md:43` | **El reviewer sabe de antemano que son tres defectos y de qué clases.** El contrato también le dice que hay posiciones incompatibles en el corpus. La detección está cebada, y PC-15 no lo declara como límite. Un lector puede sobreestimar PC-08. **Remedio:** añadir ese límite a PC-15. |
| NB-3 | Consider · OPTIONAL · m | `plan.md:221`; `spec.md:145` | **La transcripción puede faltar.** El plan no fija de dónde sale ni qué pasa si no se recupera; sin ella no hay acreditación de independencia. Definir esa salida. La auditoría tampoco nombra lecturas por git (`git show`, `git log -p`), que evitan la ruta. |
| NB-4 | Consider · OPTIONAL · h | `plan.md:205-206` frente a `spec.md:145,221` | **Excluido no equivale a invalidante.** `discovery.md`, con ejemplos que anticipan respuestas, está excluido, pero leerlo no aparece entre las causas de invalidación. Decidir si invalida o si solo se registra. |
| NB-5 | Consider · OPTIONAL · m | `plan.md:158` | **La clave solo queda fuera de los insumos de T4.** El scope por defecto del implementer es `repository-read`, que la incluye, y `prepare` lo aplica si no se recorta. Declarar un `read_scope` acotado para T4, ya que una corrección escrita leyendo la clave debilita PC-11. |
| NB-6 | Nit · OPTIONAL · h | `plan.md:338` frente al bloque T8 | La prosa no exige repetir las regresiones de T8, pero el bloque las lista. El efecto es solo de forma. |

## Objeto de dictamen

1. **Postcondiciones:** las 15 tienen vía de evidencia, y PC-07..09 y PC-13 exigen sesión real. Ninguna se acredita por control estructural. PC-03 queda más débil de lo que promete hasta cerrar NB-1, y PC-08 hasta declarar NB-2.
2. **`plan-tasks`:** hay un único bloque, el JSON es válido y contiene T1..T8. Los campos son los de los bloques `next`, `observable_checks` está presente en las tareas sin archivos, y T3, T4 y T7 declaran rutas. El `owner` compuesto de T7 está aceptado por O-1. La única incoherencia con la prosa es el «antes de GREEN / antes de T5» de NB-1, más NB-6.
3. **Control y D-4:** el límite es correcto en `spec.md:102-104` y `:212`. El verde vacío está rechazado, y PC-06 prueba que un verde no equivale a fidelidad.
4. **Cierre:** los tres registros y los límites están declarados (PC-14, PC-15, `plan.md:309-316`), salvo lo de NB-2.
5. **Riesgos residuales:** la contaminación del ensayo por BN-1 es el riesgo principal. Le siguen la fijación temporal (NB-1) y la lectura de PC-08 como detección a ciegas (NB-2).

## Abstentions

- No ejecuté `prepare`, porque escribe. No verifiqué que admita `reviewer/review` en T5, T6 y T7 con la fase de gates vigente, ni la afirmación de B-2 de que el ciclo exige GREEN antes de review.
- No verifiqué si `prepare` añade inputs automáticos a un `approved-feature-spec`. Solo vi lo que añade para `draft-plan`.
- No evalué el enforcement real del guard de lectura. El plan no lo presume.
- No evalué la diferencia entre las dos copias de `cdad_packet.py`. Validé el paquete con `scripts/`, y la lectura de scopes viene de `skills/cdad-cycle/scripts/`.
- La vigencia de `docs/adr/` no se aplicó: no se tocan decisiones de código.

## Evidencia

- **Archivos modificados:** ninguno. **Commit:** ninguno. **Tests:** no ejecutados.
- **Comandos:** `scripts/cdad_packet.py validate-request`, `validate-packet` y `render` (con y sin `--route C`) sobre el REQUEST y el PACKET de este encargo; `sha256sum` de plan y spec; extracción del bloque `plan-tasks` con `json.loads` (1 bloque, T1..T8); lectura de `_validate_scope`, `_scope_contains`, `_default_scopes` y `_contract_for` en `skills/cdad-cycle/scripts/cdad_packet.py`; `git check-ignore` de las rutas de `product/` y `oracle/` (no ignoradas).
- **Salida:** rc=0 en las tres validaciones, `cmp` sin diferencias y `check-ignore` rc=1.
