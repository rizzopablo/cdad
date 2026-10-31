# review.md — 010-001, T5 (paquete `…reviewer-review-002`)

## Dictamen

**Hay dos hallazgos bloqueantes. No debería solicitarse la aceptación funcional hasta cerrarlos.** Este dictamen no aprueba ni acepta el producto: esa decisión es del dueño.

- La distribución, el determinismo, la frontera de escritura y la honestidad estructural se sostienen.
- La norma pierde dos reglas decisivas de D3.
- El contrato del implementer sigue diciendo solo «código» en `SKILL.md` §2 y en dos referencias instaladas.
- El verde de los 11 tests no detecta ninguno de los dos defectos, porque comprueba conceptos y no la cobertura semántica de D3.

**Intake (ruta C):** `validate-request` rc=0, `validate-packet` rc=0, `cmp` contra el render completo rc=0, identificación igual a `render --route C`, sha del contrato coincidente, contexto v2 y sin cuerpo inline.

## Bloqueantes

### B1 — Required · la norma omite reglas de clasificación de D3 (PC-04)
**Verdict: BLOCKING · Bucket: h**

- **Ubicación:** `skills/cdad-cycle/references/documentary-contracts.md:70-77` (§3), contra `spec.md`, D3.
- **Evidencia:** la referencia conserva el criterio general, pero omite dos reglas sin equivalente en ningún punto del archivo:
  1. «No se conoce todavía su impacto sobre una obligación del contrato» cuenta como bloqueante.
  2. Una contradicción puede permanecer si la promesa es documentar posiciones divergentes, pero **no** si se prometió una definición operativa inequívoca que depende de ella.

  También faltan los demás ejemplos de D3: hecho necesario sin respaldo, decisión que delimita el producto y verificación no ejecutable.
- **Consecuencia:** un productor puede marcar «no bloqueante» un pendiente de impacto desconocido, o entregar un proceso «definido» con una contradicción abierta, sin violar el texto de la norma. Como solo ella viaja por puntero, ningún rol recibe la regla. La cláusula «never downgrades an obligation» no lo evita: con impacto desconocido no consta que exista una obligación afectada. Es justo la rebaja que el encargo pedía excluir.
- **Por qué el test no lo ve:** `tests/test_010_001_documentary_contracts.py:798-827` solo busca los conceptos bloqueante, no bloqueante y unilateral.
- **Condición de cierre:** el implementer incorpora ambas reglas a §3 en redacción propia, sin tocar el oráculo. Después se re-examina semánticamente D3 y se repiten el módulo y la unicidad. Si se decide un test adicional, va por el test-writer.

### B2 — Required · el contrato del implementer queda dividido (PC-08, D4)
**Verdict: BLOCKING · Bucket: h**

- **Ubicación:**
  - `skills/cdad-cycle/SKILL.md:72`, «May edit: implementation code» (la tabla §2 de roles)
  - `skills/cdad-cycle/references/handoff-prompts.md:372`, «edit ONLY in implementation code»
  - `skills/cdad-cycle/references/sub-agent-strategies.md:35,137`
  - Contra `sources/roles/implementer.md:18-19,47` y los agentes generados.
- **Evidencia:** PC-08 exige sustituir la restricción nominal a «código» en el contrato del implementer. Solo se cambió la fuente de rol y sus agentes. Las superficies instalables anteriores siguen en vigor.
- **Consecuencia:** un encargo documental legítimo tiene dos contratos publicados que se contradicen. Quien sigue la tabla §2 o la plantilla de handoff debe rechazar el producto; quien sigue el agente lo acepta. 010-003 lo encontraría en el primer GREEN documental. El generador no compone esta tabla de `SKILL.md`, así que `make agents` no lo corrige.
- **Condición de cierre:** alinear esas tres superficies en una redacción que no amplíe defaults y conserve «NOT `tests/**`». La fila del refactorer no se toca. Regenerar solo si cambia alguna fuente y repetir las regresiones de instalación.

## Observaciones no bloqueantes

### O1 — Required · la declaración de la deriva de `make validate` es honesta pero insuficiente
**Verdict: OPTIONAL · Bucket: h**

- **Ubicación:** `tdd-t4-green.md:112`, `review-refused-packet-001.md`.
- **No oculta una regresión de producto:**
  - `install.sh --check` solo muestra deriva de instalación.
  - La instalación aislada está documentada como correcta. No la repetí, pero sí comprobé `make agents`.
- **El listado está incompleto.** El informe nombra `~/.claude`, `SKILL.md` y los 22 agentes. Omite:
  - `~/.agents/skills` y `~/.config/opencode/skills`
  - los **cinco bloques de `packets/roles` en los tres árboles** (15 archivos)
  - la `.pyc`
- **«Deriva de entorno esperada» subestima el efecto.** Esos bloques fueron la causa documentada de que `review-001` naciera inválido, y el agente reviewer de esta sesión tampoco trae la línea documental. Mientras no se publique, los roles reciben la obligación por el paquete, no por el agente instalado.
- **Condición de cierre:** T6 registra el inventario completo de deriva y exige componer paquetes con el CLI del proyecto. Quien decide si habrá publicación es el dueño, porque el plan la excluye. Además, T6 debe declarar `make validate` rc=2 como fallo conocido, no presentarlo como verde.

### O2 — Consider · el producto editable tiene una forma válida no documentada
**Verdict: OPTIONAL · Bucket: h**

- **Ubicación:** `documentary-contracts.md:86-92`; `cdad_packet.py:1461-1464`.
- **Evidencia:**
  - `{"class":"docs","root":"docs/specs/x/product"}` es aceptado.
  - `{"class":"docs","path":"…/a.md"}` es rechazado: «exact docs path is not declared by path_policy».
- **Consecuencia:** el encargo real es cumplible, pero solo con un directorio de producto propio, separado de las fuentes, o con una política ampliada. La norma tampoco recoge de D2 que las declaraciones se expresan mediante el contrato y los campos existentes, sin campos nuevos.
- **Condición de cierre:** añadir ambas precisiones a la norma, o llevarlas como entrada explícita a 010-002/003.

### O3 — Nit · la ambigüedad queda más estrecha que PC-06
**Verdict: OPTIONAL · Bucket: m**

- **Ubicación:** `documentary-contracts.md:91-92`.
- PC-06 detiene ante «superposición o ambigüedad». La norma solo define la superposición con fuente, verificador o plantilla: no cubre un archivo de estado dudoso ni nombra el contrato.
- **Condición de cierre:** mencionar la ambigüedad general.

### O4 — Nit · cumplimiento mínimo de la unicidad
**Verdict: OPTIONAL · Bucket: h**

- **Ubicación:** `sources/roles/test-writer.md:30-34` y `sources/roles/reviewer.md:58-62`, contra §5 de la referencia.
- Con 6-gramas propios aparecen 7 y 6 coincidencias: la frase del test-writer es casi la misma, con el pronombre cambiado.
- La medida contractual de PC-13 pasa y el origen común es la tabla de PC-08, así que no bloquea.
- **Consideración:** reformular cuando se toque el texto.

## Trazabilidad PC-01 a PC-16

| PC | Evidencia | Resultado |
|---|---|---|
| 01 | §1, contrastado con D1 | Acreditada semánticamente |
| 02 | §1-2 | Acreditada |
| 03 | §2: cinco tipos; fuente inaccesible, mutable o insuficiente | Acreditada |
| 04 | §3 | **Parcial, B1** |
| 05 | §4 | Acreditada; forma práctica en O2 |
| 06 | §4 | Acreditada; O3 |
| 07 | §4 | Acreditada |
| 08 | §5, fuentes de rol, bloques | **Parcial, B2** |
| 09 | §6 | Acreditada |
| 10 / INV-08 | §6, `tdd-t3-green.md`, `tdd-t4-green.md`, `red-t2.md`: ninguno presenta el paquete como sandbox | Acreditada |
| 11 | §7 | Acreditada |
| 12 / INV-07 | §7; `grep` sin el nombre del aprobador en la referencia | Acreditada |
| 13 | Fila en `SKILL.md`, test de unicidad verde; O4 | Acreditada por la medida contractual |
| 14 | 6 fuentes, 5 bloques y 22 agentes presentes; este paquete transporta la línea | Acreditada |
| 15 | `make agents` doble en copia limpia sin diferencias; test de instalación verde; techo de 3709 sobre 12000 | Acreditada |
| 16 | Diff: sin cambios en scripts, esquema, `install.sh` ni `Makefile`; 11 agentes por runtime | Acreditada (revisión de diff) |

## Resto del encargo

- **Escapes de escritura y oráculo:**
  - `tests/`, spec, plan, audit, `scripts`, `install.sh`, `Makefile` y `build` no cambian entre `3344526e~1` y `HEAD`.
  - El implementer no tocó verificadores.
  - Los dos commits de implementación tienen el alcance declarado.
- **Oráculo del test-writer:** el RED precede a la referencia, y el volcado de fuentes declarado en `red-t2.md` §8 se produjo con el oráculo ya escrito, sobre otros archivos.
- **Permisos:** `_default_scopes` del implementer no añade `docs`. Se necesita una autorización explícita.
- **Honestidad estructural:** los informes separan estructura y fidelidad.
- **Punteros:** resuelven por el nombre de archivo que declaran.

## Abstenciones

- **Agentes generados:** verifiqué `make agents` sin diferencias, pero no puedo probar el proceso histórico de su edición, solo que sus bytes coinciden.
- **Instalación aislada:** no la repetí como comando manual; me apoyo en el test `test_isolated_install…` y en el informe de T4.
- **Suite completa y `make validate`:** no los ejecuté por política. El rc=2 es dato de T4, aunque coincide con el `install.sh --check` que sí corrí.
- **Escrituras transitorias del autor:** no son demostrables por diff.
- **Fidelidad de un documento real:** no existe producto documental en esta unidad y corresponde al piloto.
- **Tabla de decisiones contra `docs/adr/`:** no la cotejé en detalle. No detecté cambios en la tabla dentro del diff, pero eso no sustituye el cotejo.
- **Regresiones de T3/T4:** de esas baterías repetí solo el techo. Las 64+ pruebas de T4 quedan como dato del autor, no como comprobación propia.

## Evidencia

**Archivos modificados y commits:** ninguno. Revisé `3344526e` y `2a918b72` sobre HEAD `91f98569`.

**Escrituras transitorias:** usé una copia descartable bajo `/tmp`, ya borrada. Un primer intento de render fallido dejó `<home>/.cache/r.md` vacío y `/tmp/e`, ambos sin borrar. Esas dos rutas están fuera del repositorio; `git status` final coincide con el inicial, lo que no prueba ausencia de otras escrituras transitorias.

```bash
python3 skills/cdad-cycle/scripts/cdad_packet.py validate-request --project-root . --request $P/REQUEST.json          # rc=0
python3 skills/cdad-cycle/scripts/cdad_packet.py validate-packet --project-root . --request $P/REQUEST.json --packet $P/PACKET.md   # rc=0
python3 skills/cdad-cycle/scripts/cdad_packet.py render --project-root . --request $P/REQUEST.json | cmp - $P/PACKET.md   # rc=0
python3 -B -m unittest tests.test_010_001_documentary_contracts                                            # Ran 11, OK
python3 -B -m unittest tests.test_006_004_u3_principle_single_source.TestPd13StaticBlockCeiling            # OK, máx. 3709/12000
make agents   # dos veces en copia de git archive: rc=0, git status vacío
git diff --stat 3344526e~1 HEAD -- tests <spec> <plan> <test-audit> scripts install.sh Makefile build      # sin salida
bash install.sh --check                                                                                    # Check: FAIL, solo deriva
```

Además, invoqué `_validate_scope` para las dos formas de O2 y ejecuté una comparación ad hoc de 6-gramas para O4.
