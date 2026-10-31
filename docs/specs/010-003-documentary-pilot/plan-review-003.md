# Dictamen plan-review (tercera vuelta) — 010-003-documentary-pilot

**Objeto:** `plan.md` v4, sha256 `352e42a25bf3cda50328cb74a59a8198c7ec30ac40323ff9c78a69c9ee9a14a8`, y `spec.md` v3, sha256 `397a3975762fc40673d1aa70e8be681cf1672ab5501460e2cb44b2428fa5a40e`. Los digests coinciden con los bytes en disco.

**Intake:** ruta C con contexto v2. `validate-request` dio rc=0, `validate-packet` rc=0 y `render | cmp PACKET.md` rc=0. La identificación coincide con `render --route C`.

**Recomendación: no aprobable todavía; aprobable con un cambio.** BN-1, NB-1..NB-6, B-1..B-4 y O-1..O-8 están cerrados, pero hay **un bloqueante nuevo (BN-2)**, introducido por el cierre de NB-5. Su corrección es local y requiere una elección de la autoridad. Este dictamen no aprueba nada.

## Bloqueante nuevo

### BN-2 — El `read_scope` prometido para T4 no se puede construir sin incluir la clave
**Required · Verdict: BLOCKING · Bucket: h**

- **Ubicación:** `spec.md:170`, `plan.md:174`, `plan.md:501` (entrada T4 de `plan-tasks`) y `skills/cdad-cycle/scripts/cdad_packet.py:1461-1464`.
- **Fundamento:** el contrato exige incluir en el `read_scope` el verificador `tests/test_010_003_documentary_pilot.py`, y ese archivo está directamente bajo `tests/`.
  - **Ruta exacta rechazada:** una ruta exacta de clase `tests` exige figurar en `test_files`, y la política vigente no declara ese campo. Ejecutado contra `_validate_scope`: `exact tests path is not declared by path_policy`.
  - **Raíz demasiado amplia:** la única raíz que lo contiene es `tests`, que incluye `oracle/` y `structural/`.
  - **Declararlo solo como input no sirve:** un input fuera del `read_scope` también se rechaza (`cdad_packet.py:1975`, `:3452`).
- **Consecuencia:**
  - **Si se respeta el plan:** T4 no se despacha tal como está contratado, y `plan.md:178` obliga a detenerse.
  - **Si se ensancha a `tests`:** reaparece lo que NB-5 quería evitar, porque una corrección escrita leyendo la clave debilita PC-11.
  - El defecto lo detecta `prepare`, así que no sería silencioso, pero el contrato aprobado sería inejecutable.
- **Condición de cierre:** spec y plan declaran un recorte que `_validate_scope` acepte, sin `oracle/` ni `structural/`, y sin tocar los bloques de instrucciones.
- **Decisión de la autoridad (elegir una vía):**
  1. **Recomendada:** sacar el verificador del `read_scope` y de los insumos de T4. El implementer lo ejecuta y usa su salida, sin leer el archivo. Es la vía más simple: no toca política ni rutas.
  2. Mover el verificador a una raíz propia sin clave, por ejemplo un directorio de pruebas del piloto. Cambia una ruta de la spec, la del bloque y las de los comandos.
  3. Declarar `test_files` en `docs/cdad-policy.json`. Cambia la política de la ejecución y exige reconciliarla, así que hay que evaluarla frente a D-5.

Con la vía 1 hay que corregir también la lista de `read_scope` en los tres lugares citados. Basta una revisión acotada a ese cambio.

## Veredicto sobre los anteriores

| # | Veredicto | Ubicación | Fundamento |
|---|---|---|---|
| BN-1 | **Cerrado** | `spec.md:49,149,155,198`; `plan.md:33,236-245,259,266,270`; T5 en `plan.md:521,523` | Objeto y exclusiones van en `objective` e `invariants`, y `prepare` admite ambos (`--objective`, `--invariant`). La comprobación previa reconoce la precedencia y sigue deteniendo otras imposiciones. Una operación git que muestre contenido invalida el ensayo. No promete nada que el mecanismo no pueda cumplir: declara que es contractual y auditable, no aislamiento técnico. No abre lecturas: citar los commits no autoriza abrirlos (`plan.md:247`). |
| NB-1 | **Cerrado**, con residuo en O-9 | `spec.md:73,82,84,124,215,218`; `plan.md:124-141,159,268,371` | Se cumplen las cuatro piezas. El verificador está en el commit, previo a T4; el registro se versiona antes de T5; el request cita ambos; y los informes van en un commit descendiente. No se apoya en la fecha de autor (`spec.md:84`, `plan.md:141`). El registro contiene el hash del commit de preparación, de modo que no puede ser anterior a él. |
| NB-2 | **Cerrado** | `spec.md:180`; `plan.md:46,396,588` | PC-15 declara los tres defectos, sus clases y la detección sobre un desafío declarado, no a ciegas. |
| NB-3 | **Cerrado** | `spec.md:153,217,234`; `plan.md:265-266,272,283` | Transcripción recuperada del store en modo lectura. Sin ella no se acredita independencia. La auditoría incluye `git show`, `git log -p` y `git diff`. |
| NB-4 | **Cerrado** | `spec.md:155,233`; `plan.md:270` | Leer `discovery.md` antes del cierre del primer informe invalida el ensayo. |
| NB-5 | **Cerrado en la intención; su ejecución queda en BN-2** | `spec.md:170`; `plan.md:174-178` | `oracle/` queda fuera y el recorte está exigido, pero la lista declarada no es construible. |
| NB-6 | **Cerrado** | `plan.md:389-394,585,590-593` | La prosa de T8 nombra las regresiones que lista su bloque. |
| B-1 | **Cerrado** | `spec.md:35,147`; `plan.md:219,233` | Selector aceptado por `_validate_scope` para `skills/cdad-cycle/references`. Ver O-10. |
| B-2 | **Cerrado** | `spec.md:47,151`; `plan.md:23,31,287` | El orden se conserva; la exclusión y la invalidación se endurecieron. |
| B-3 | **Cerrado** | `spec.md:73-84`; `plan.md:120-143` | Reforzado por NB-1. |
| B-4 | **Cerrado** | `spec.md:172`; `plan.md:172,293-300` | El candidato es obligatorio en T4 y T6 recibe candidato, clave y contraste. |
| O-1..O-8 | **Cerrados** | O-1 `plan.md:21`; O-2 `plan.md:112-118`; O-3 `spec.md:108,134`; O-4 `plan.md:372,384`; O-5 `plan.md:266`; O-6 `plan.md:332`; O-7 `plan.md:278-285`; O-8 `plan.md:106,225` | Siguen presentes en los textos nuevos. |

## Regresión

- **PC:** las quince conservan su numeración. El diff frente a la spec v2 solo cambia PC-15, y el cambio es el límite declarado.
- **`plan-tasks`:** bloque único, JSON válido, T1..T8. Hay `observable_checks` donde no hay archivos y rutas donde hay producto.
- **Orden y evidencia:** T3 → T4 → T5 → T6 se conserva, D-4 también (`spec.md:224`, `plan.md:419`), y §7 no se debilitó.
- **Scopes por clases existentes:** el resto de lo comprobado pasa; la única excepción es BN-2. Aceptados: `sources/` y `challenge/` por raíz, contrato por ruta, `product/` como lectura y como escritura `docs`, y la raíz de referencias.

## No bloqueantes nuevos

| # | Tupla | Ubicación | Hallazgo y remedio |
|---|---|---|---|
| O-9 | Consider · OPTIONAL · m | `plan.md:178,371,503`; `spec.md:124` | **«Anterior a T4» no tiene un ancla que un tercero pueda comprobar.** La comprobación la hace el orquestador. El request de T4 no cita el commit de preparación, y no se exige ningún commit del producto. Tampoco se exige que los informes desciendan del commit del registro. **Remedio:** que el request de T4 cite el commit de preparación y que el commit del producto descienda de él. |
| O-10 | Consider · OPTIONAL · m | `plan.md:219,226,266,270`; `spec.md:155` | **Una lectura no reveladora podría invalidar un ensayo de un solo intento.** El paquete nombra `design-principles.md` y `stage-4-review.md`, y el agente reviewer remite a `verdict-tuple.md`. El selector mecánico los alcanza. El plan los trata como documentos no autorizados, y `plan.md:270` no aclara si leerlos invalida o solo se registra. **Remedio:** la autoridad decide. Recomiendo registrar la lectura de referencias no reveladoras sin invalidar, y conservar la invalidación para lo que revele respuestas. |
| O-11 | Consider · OPTIONAL · m | `plan.md:174,178`; `skills/cdad-cycle/packets/roles/implementer.md`; `substages/implementer-green.md` | **El paquete de T4 también remite a `stage-3-tdd.md`,** pero el plan autoriza solo `documentary-contracts.md`. El mismo patrón ya dio lugar a B-1, aunque T4 no es de un solo intento. **Remedio:** declararla como lectura normativa de T4. |
| O-12 | Consider · OPTIONAL · m | `plan.md:324-337` | **T7 no recorta el `read_scope` del implementer.** El default `repository-read` incluye la clave, y `oracle/` sigue sin ser insumo de producción. **Remedio:** repetir el recorte de T4, ya corregido por BN-2. |

## Abstentions

- No ejecuté `prepare`, porque escribe. Sigue sin verificar que los gates admitan `reviewer/review` en T5, T6 y T7 con la fase vigente, y la razón de B-2 tampoco se contrastó con esos gates. Sí comprobé `VALID_SUBSTAGES` para reviewer (`cdad_packet.py:91`) y que `_default_scopes` y los inputs automáticos de un contrato aprobado no añaden el diff.
- No verifiqué que el store del runtime sea legible en la práctica. El plan cubre ese fallo: sin transcripción no se acredita independencia.
- No evalué el enforcement real del guard de lectura. El plan no lo presume.
- La vigencia de `docs/adr/` no se aplicó: no se tocan decisiones de código.
- No consulté al asesor externo; los hallazgos se apoyan en la ejecución directa y en la lectura del código.

## Evidencia

- **Archivos modificados:** ninguno en el repositorio; solo auxiliares en `/tmp/opencode/`. **Commit:** ninguno. **Tests:** no ejecutados.
- **Comandos:**
  - `scripts/cdad_packet.py validate-request`, `validate-packet`, `render` y `render --route C` sobre este encargo.
  - `sha256sum` de plan y spec.
  - `json.loads` del bloque `plan-tasks`.
  - `diff` de las líneas PC entre `c930a85c` y la spec actual.
  - Un script que invoca `_validate_scope` con los diez scopes de T4 y T5 sobre la política real.
  - Lectura de `_validate_scope`, `_scope_contains`, `_contract_for`, `_default_scopes` y `prepare`.
- **Salida relevante:**
  - rc=0 en las tres validaciones y `cmp` sin diferencias.
  - 1 bloque con `['T1'..'T8']`.
  - Diff de PC: solo la línea 15.
  - `REJ implementer ... tests/test_010_003_documentary_pilot.py: exact tests path is not declared by path_policy`.
  - Los scopes de raíz y contrato: `OK`.
