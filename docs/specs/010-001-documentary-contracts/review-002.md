# review — 010-001, T5, re-verificación (paquete `…reviewer-review-003`)

## Dictamen

**B1 y B2 están cerrados. O2 y O3 quedaron incorporadas. No hay bloqueantes nuevos.** Hay dos Nits no bloqueantes. Este informe no aprueba ni acepta el producto.

| Hallazgo | Estado |
|---|---|
| B1 | **Cerrado** (N1 es matiz de redacción) |
| B2 | **Cerrado con reparo** (N2) |
| O2 | **Incorporada** |
| O3 | **Incorporada** |
| Bloqueantes nuevos | Ninguno |

**Intake (ruta C):**
- `validate-request` rc=0 y `validate-packet` rc=0.
- `cmp` contra el render completo rc=0.
- La identificación es igual a `render --route C`.
- El sha del contrato coincide, el contexto es v2 y no hay cuerpo inline.

## Examen por hallazgo

### B1 — Cerrado
Contraste de `documentary-contracts.md` §3 con D3:

- **Impacto desconocido:** L73-75 lo declara bloqueante sin condición y añade que desconocer el efecto no prueba que ninguna obligación se toque. Eso cierra la vía de escape que señaló `review.md`: «no consta que exista una obligación afectada».
- **Contradicción:** L81-83 cubre los dos lados de D3. Solo permanece si se prometió documentar divergencias, y debe resolverse si se prometió una definición operativa que depende de ella.
- **Ejemplos:** L70-73 recoge el hecho sin respaldo, la decisión de delimitación y la verificación no ejecutable. El quinto ejemplo de D3, la contradicción que impide el proceso, queda cubierto por L82-83.
- **Rebaja unilateral:** los ejemplos solo amplían lo bloqueante. El «for example» no abre otro camino, y las dos salidas no bloqueantes de L77-79 son las de D3. L85-87 conserva la prohibición.
- **Datos mínimos de D3:** intactos en L63-67.

### B2 — Cerrado con reparo
- **Tres superficies:** `SKILL.md:72`, `handoff-prompts.md:372` y `sub-agent-strategies.md:35,137` admiten el producto solo si se encarga expresamente, tal como pide PC-08.
- **Permisos por defecto:** sin ampliar. `scripts/` no cambió, de modo que `_default_scopes` tampoco.
- **Prohibición de tests:** presente en las cuatro líneas.
- **Refactorer:** ninguna línea suya aparece en el diff (`SKILL.md:73`, `sub-agent-strategies.md:36,138`, `handoff-prompts.md:408`).
- **Coherencia con el rol:** concuerda con `sources/roles/implementer.md:18-19,47`, con los agentes generados y con el bloque de paquete `packets/roles/implementer.md:2`.
- **Reparo:** ver N2.

### O2 — Incorporada
L98-101 recoge el directorio propio, la ruta exacta condicionada a la política y la ausencia de campos nuevos. Esto coincide con el comportamiento de `cdad_packet.py:1461-1464`.

### O3 — Incorporada
L107-111 añade el contrato de aceptación y la ambigüedad sobre qué papel juega un archivo, como pide PC-06.

## Observaciones no bloqueantes

### N1 — Nit · «only» en la regla de contradicción
**Verdict: OPTIONAL · Bucket: m**

- **Ubicación:** `documentary-contracts.md:81`.
- **Evidencia:** D3 dice que la contradicción «puede permanecer si…», y la norma dice «only when». El «only» coincide con lo que pide este encargo. Sin embargo, no contempla la contradicción fuera del alcance comprometido, que por L77 sería un pendiente no bloqueante.
- **Consecuencia:** una lectura literal exigiría resolver una contradicción ajena a la promesa. Es más estricta que D3 y nunca permite una rebaja, así que el defecto va en dirección segura.
- **Condición de cierre (opcional):** retirar «only» o precisar que la regla aplica dentro del alcance comprometido. Puede llevarse al piloto.

### N2 — Nit · residuo en la plantilla del implementer
**Verdict: OPTIONAL · Bucket: h**

- **Ubicación:** `handoff-prompts.md:377`, «Expected output: implementation code + commit…».
- **Evidencia:** la línea está en la misma plantilla que la L372 corregida, pero no figuraba en las ubicaciones de B2.
- **Consecuencia:** es una descripción de salida, no un permiso. La L372 prevalece y un encargo documental no queda impedido, solo descrito de forma imprecisa.
- **Condición de cierre (opcional):** cambiarla a «implementation product».

**FYI:** el vocabulario varía entre «documentary deliverable» (las tres superficies) y «documentary product» (fuente de rol y norma). No cambia el sentido.

## Defectos nuevos buscados y no encontrados
- **Contradicciones entre superficies:** ninguna más allá de N2.
- **Vocabulario y rutas:** el texto añadido no contiene `/tmp`, `/home`, `~/`, nombres internos ni identidades.
- **Duplicación normativa:** las frases nuevas buscadas aparecen solo en la referencia.
- **Alcance:** el commit toca cuatro archivos bajo `skills/`. No hay cambios en tests, `sources`, `agents`, `build`, `scripts`, `install.sh`, `Makefile` ni la spec. O2 y O3 eran observaciones aceptadas y están declaradas en el informe.
- **Informe de corrección:** sus referencias de línea coinciden con el árbol vigente.
- **Pendiente de la orquestación:** `tdd-t5-review-fix.md` sigue sin commit.

## Abstenciones
- **Regresión de instalación:** no repetí `test_004_001_t6`. Su resultado de 9 tests verdes es dato del autor.
- **`make agents`:** no lo repetí. El diff vacío en `sources`, `agents` y `build` hace que no aplique.
- **Suite completa y `make validate`:** no los ejecuté, por política.
- **O1 (inventario de deriva) y O4:** quedan fuera de este encargo y siguen abiertas. O1 corresponde a T6.
- **Tabla de decisiones contra `docs/adr/`:** no la cotejé, porque el commit no la toca.
- **Fidelidad de un documento real:** no existe producto documental en esta unidad.
- **Escrituras transitorias del autor:** no son demostrables por diff.

## Evidencia

**Archivos modificados y commits:** ninguno. Revisé `71c2a7e2` sobre HEAD.

**Escrituras transitorias:** mi primer render fallido dejó un archivo vacío `<workspace>/tmp-r.683326`, ya borrado, y `/tmp/e`, que sigue ahí. Ambas rutas están fuera del repositorio. `git status` final coincide con el inicial, aunque eso no prueba la ausencia de otras escrituras.

```bash
C=skills/cdad-cycle/scripts/cdad_packet.py
python3 -B $C validate-request --project-root . --request $P/REQUEST.json                    # rc=0
python3 -B $C validate-packet --project-root . --request $P/REQUEST.json --packet $P/PACKET.md   # rc=0
python3 -B $C render --project-root . --request $P/REQUEST.json | cmp - $P/PACKET.md         # rc=0
python3 -B $C render --project-root . --request $P/REQUEST.json --route C                    # igual a la identificación recibida
python3 -B -m unittest tests.test_010_001_documentary_contracts                              # Ran 11, OK
python3 -B -m unittest tests.test_006_004_u3_principle_single_source tests.test_006_003_u3_texts_without_profiles  # Ran 25, OK; techo 3709/12000
git diff --stat HEAD~1 HEAD -- tests sources agents build scripts install.sh Makefile <spec> # sin salida
git diff --stat HEAD -- skills sources agents tests                                          # sin salida
rg -n -i 'implementation code|implementer.{0,50}\bcode\b|...' skills/...                     # residuo: handoff-prompts.md:377
```
