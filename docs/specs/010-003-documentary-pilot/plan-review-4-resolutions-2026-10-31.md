# Resoluciones de la cuarta vuelta del plan-review — 010-003 — 2026-10-31

Resoluciones de la autoridad habilitada (ejercida por el orquestador bajo el
mandato HITL del 2026-10-30, §1 y §3) sobre `plan-review-004.md` (plan v5,
spec v4). La cuarta vuelta —acotada al delta— cerró BN-2 y O-9..O-12, confirmó
la no regresión y abrió **BN-3**: el límite declarado en el cierre de BN-2 es
falso para el comando focal. Aquí se adoptan las dos condiciones de cierre y los
dos no bloqueantes nuevos.

## BN-3 — El comando focal muestra el código del verificador

**Decisión: se adoptan las dos condiciones del dictamen**, no la alternativa de
rebajar el límite.

### Medición propia

```
pytest -q test_x.py          → muestra el cuerpo de la función y los valores
pytest -q --tb=no test_x.py  → sin cuerpo, pero la línea FAILED conserva
                               el mensaje de la aserción y sus valores
```

Con `--tb=no` el implementer ve nombres de casos y mensajes de aserción; no ve
el cuerpo del test. La aserción, en cambio, sigue imprimiendo lo que compara.

### Qué debe quedar escrito

1. **Comando focal acotado.** T4 y T7 declaran
   `python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py`
   en todos los lugares donde el comando aparece —spec, prosa del plan y bloque
   `plan-tasks`—, sin variantes divergentes.
2. **El verificador no lee la clave ni la imprime.** T3 incorpora a su
   inspección previa a GREEN una comprobación explícita: el verificador **no
   lee** `oracle/`, y sus mensajes y valores de aserción **no reproducen
   contenido de la clave**. Si una aserción necesita comparar contra la clave,
   la comparación no pertenece al verificador: pertenece al contraste del
   orquestador.
3. **Límite declarado, verdadero.** El implementer ve nombres de casos y
   mensajes de aserción del verificador; **no ve su cuerpo**. No ve la clave ni
   las muestras estructurales como insumo. `pytest` es una herramienta, no un
   sandbox: no se promete aislamiento técnico.

### Por qué no se rebaja el límite

La alternativa honesta —«puede ver fragmentos del test; no se le entrega el
archivo»— sería verdadera, pero cede el punto 4 de la resolución de BN-2: un
oráculo cuyo cuerpo se puede leer se puede moldear. `--tb=no` cuesta una opción
y conserva el fundamento. La fuga de clave, que es el riesgo real, se cierra en
T3 con una comprobación, no con una promesa.

## O-13 — «Exacta» sólo donde el selector es exacto

**Adoptado.** El mapa de selectores queda explícito, con lo que el mecanismo
acepta y lo que rechaza:

| Insumo | Selector que se declara | Estado |
|---|---|---|
| Contrato | ruta exacta, clase `contract` | aceptado |
| `inventory.md` y candidato | raíces `sources/` y `challenge/`, clase `tests` | aceptado (la ruta exacta de clase `tests` se rechaza) |
| Normas (`documentary-contracts.md`, `stage-3-tdd.md`) | raíz `skills/cdad-cycle/references`, clase `implementation`, con autorización contractual restringida a esos archivos | aceptado |
| Producto en T7 | raíz `product/`, clase `contract` | aceptado |

La palabra «exacta» se reserva para el contrato. Para las raíces se dice raíz y
se nombra la restricción contractual que impide leer el resto.

## O-14 — El producto como insumo en T7

**Adoptado.** T7 añade `product/` como raíz de lectura de clase `contract`,
para que el producto declarado como insumo quede dentro del `read_scope`. Sin
esa raíz, `prepare` rechaza el input de forma visible y el encargo no se puede
construir.

## Lo que esta resolución no hace

No cambia el orden de gates, no crea mecanismo, no edita los bloques de
instrucciones, no toca la política ni la instalación, no autoriza publicar y no
adelanta la aprobación. La spec pasa a v5 y el plan a v6, y vuelven al
plan-review en una revisión acotada al delta: BN-3, O-13 y O-14, y la
comprobación de que lo ya cerrado sigue en su lugar.
