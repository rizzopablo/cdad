# Resoluciones de la tercera vuelta del plan-review — 010-003 — 2026-10-31

Resoluciones de la autoridad habilitada (ejercida por el orquestador bajo el
mandato HITL del 2026-10-30, §1 y §3) sobre `plan-review-003.md` (plan v4,
spec v3). La tercera vuelta cerró BN-1, NB-1..NB-6, B-1..B-4 y O-1..O-8, y
abrió **BN-2**, introducido al cerrar NB-5. Aquí se elige la vía y se adoptan
los cuatro no bloqueantes nuevos.

## BN-2 — El `read_scope` de T4 no se puede construir sin incluir la clave

**Decisión: vía 1, la recomendada por el dictamen.** El verificador sale del
`read_scope` **y** de los insumos de T4; el implementer lo **ejecuta** y usa su
salida, sin leer el archivo.

### Fundamento

1. **La ruta exacta no es declarable.** Una ruta exacta de clase `tests` exige
   figurar en `test_files`, y la política vigente no declara ese campo: el
   validador la rechaza con `exact tests path is not declared by path_policy`.
2. **La raíz contiene la clave.** La única raíz admitida que contiene el
   verificador es `tests`, y `tests/` contiene
   `tests/fixtures/010_003_documentary_pilot/oracle/`. Aceptar la raíz para
   ganar el verificador reintroduce exactamente el riesgo que NB-5 cierra.
3. **No hace falta leerlo.** El implementer ejecuta el comando declarado en
   `focal_tests` y trabaja con la salida. No necesita el código del test para
   producir un documento Markdown cuya convención de anclas ya viene fijada por
   el inventario y la spec.
4. **Es más fuerte, no más débil.** Un oráculo que el productor no lee no se
   puede moldear; la corrección se escribe contra el contrato y las fuentes, no
   contra el test.
5. **No toca política ni rutas.** Las vías 2 y 3 cambian una ruta de la spec o
   la política de la ejecución; la vía 1 sólo corrige la lista de insumos.

### Qué debe quedar escrito

- **Spec y plan:** el `read_scope` de T4 es contrato exacto, `inventory.md`, las
  dos fuentes, el candidato y el producto autorizado. El verificador **no** es
  insumo ni lectura: se ejecuta como `focal_test`.
- **Los tres lugares** que citan la lista —spec, prosa del plan y entrada T4 de
  `plan-tasks`— se corrigen juntos.
- **Se conserva el resto de NB-5:** `oracle/` y `structural/` quedan fuera; el
  recorte se declara porque el default `repository-read` incluiría la clave.
- **La comprobación previa** de T4 verifica que el paquete sea construible
  (`validate-request`/`validate-packet` rc=0), no sólo que la intención esté
  escrita.

### Límite que se declara

El implementer puede ver la salida del verificador —incluidos los nombres de los
casos que fallan— y eso informa la corrección. No ve el código del test ni la
clave. Es el mismo límite que ya declara D-4: el control estructural no acredita
fidelidad semántica, y esta unidad no promete aislamiento técnico.

## O-9 — El «antes de T4» necesita un ancla comprobable

**Adoptado.** El request de T4 **cita** el commit de preparación, y el commit
del producto **desciende** de él. Sin esas dos piezas, «anterior a T4» es una
declaración del orquestador que un tercero no puede fechar.

## O-10 — Lecturas normativas no reveladoras: se registran, no invalidan

**Decidido: se registran sin invalidar.** El paquete del reviewer nombra
referencias de método (`design-principles.md`, `stage-4-review.md`,
`verdict-tuple.md`); el selector mecánico de la raíz las alcanza. Ninguna revela
los tres defectos ni la clave.

La regla queda explícita y sin ambigüedad:

| Lectura declarada antes del cierre | Efecto |
|---|---|
| `product/`, `oracle/`, `structural/`, `discovery.md`, informes GREEN o de contraste y sus copias | **Invalida** el ensayo como independiente |
| El diff de la unidad y operaciones git que muestren contenido (`git show`, `git log -p`, `git diff`) | **Invalida** |
| Referencias normativas de método que no revelan respuestas | Se **registra**; no invalida |
| Cualquier otro documento no listado como insumo | Se **registra**; el auditor decide y funda si revela respuestas |

El criterio es uno solo y se declara: **invalida lo que revela respuestas**, no
lo que enseña a revisar. Así el ensayo no se pierde por una lectura normativa y
la invalidación conserva su filo donde importa.

## O-11 — T4 declara su lectura normativa

**Adoptado.** El paquete de T4 remite a `stage-3-tdd.md`; se declara como lectura
normativa de T4, igual que `documentary-contracts.md`, con la misma advertencia:
el selector mecánico más amplio no autoriza otras referencias. Es la misma clase
de defecto que B-1, en un encargo donde no cuesta nada cerrarlo.

## O-12 — T7 repite el recorte de lectura de T4

**Adoptado.** El `review-fix` de T7 es un encargo del implementer y su default
`repository-read` incluye `oracle/`. Se repite el recorte corregido por BN-2:
contrato, inventario, fuentes, candidato, producto, informe de T6 y lectura
normativa declarada; ni `oracle/` ni `structural/` ni el veredicto del reviewer
sobre el desafío.

## Lo que esta resolución no hace

No cambia el orden de gates, no crea mecanismo, no edita los bloques de
instrucciones, no toca la política de la ejecución, no autoriza publicar y no
adelanta la aprobación. La spec pasa a v4 y el plan a v5, y vuelven al
plan-review en una revisión **acotada al delta**: BN-2 y O-9..O-12, más la
comprobación de que nada de lo ya cerrado se movió.
