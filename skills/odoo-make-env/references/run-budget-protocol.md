# Protocolo de presupuesto de corridas de tests (CDAD-Odoo)

> Origen: protocolo diseñado y validado empíricamente durante la feature
> 001-004 del epic 001-liquidacion-repartos (repo reparto-odoo, sep 2026),
> donde el costo real resultó ser `setup completo × corridas repetidas ×
> property tests`, no la cantidad de tests. Incorporado a CDAD como estándar.
> Presupuestos numéricos: **defaults calibrados para setups de 15-20 min** —
> el owner (HITL) los ajusta por proyecto en `systemPatterns.md`.

## Principios

1. **La suite completa es de gate, no de depuración.** Depuración = `test-one`
   sobre DB caliente; suite completa UNA vez para cerrar el gate.
2. **El costo es el setup.** Se minimiza el número de setups, no el número de
   tests. Un setup que no sigue a un cambio con hipótesis es desperdicio puro.
3. **Toda corrida sigue a un cambio.** Ciclo: leer el fallo completo →
   hipótesis escrita → UN cambio → UNA corrida. Nunca re-correr "a ver si pasa".
4. **Presupuesto duro por etapa, fijado por el owner.** Excederlo = STOP y
   escalar, no reintentar.
5. **La evidencia ya producida es reutilizable** si el árbol de código es
   idéntico (ver "Review: presupuesto 0").
6. **El N de property tests es calibración de runtime, no contrato.** La
   postcondición define QUÉ invariante; M escenarios es presupuesto. N mayor
   pertenece al hardening.

## Presupuesto por etapa (defaults; ajustar por proyecto)

| Etapa | Corrida permitida | Presupuesto default |
|---|---|---|
| RED (test-writer) | `test-one` por clase, DB caliente | 1-2 corridas, 0 completas |
| GREEN (implementer, iteración) | `test-one` | max 2 por fallo sin convergencia → STOP. Prohibido `test-clean`/`make test` durante iteración |
| Cierre GREEN | UNA `test-all` (DB fresca) | 1 |
| Review (reviewer) | ninguna si el árbol es idéntico; si cambió, 1 `test-all` | 0-1 |
| Fix de review | mini-ciclo RED→fix con `test-one` + UN gate `test-all` | ~15 `test-one` y 2 completas por feature |

## Target `test-all` (multi-módulo: un setup para todas las suites)

Una sola DB fresca que instala el módulo más profundo (que arrastra al resto
por `depends`) y filtra los tests de todos los módulos del repo:

```make
test-all:
	$(require-module)
	-dropdb --if-exists $(TEST_DB) 2>/dev/null || true
	$(RUN) odoo-bin -c $(CONF) -d $(TEST_DB) -i <modulo_mas_profundo> \
		--test-tags /modulo_A,/modulo_B $(ODOO_FLAGS)
```

**Condición:** la abstracción "instalar el más profundo arrastra al resto"
solo vale si el grafo de dependencias es una cadena. Con módulos
independientes, usar `-i mod1,mod2`. Reemplaza N `test-clean` por 1 setup.

## Guards anti-falso-verde (obligatorios en el Makefile)

- `require-installed`: `-u` sobre módulo no instalado es no-op que reporta
  `0 failed, 0 error(s) of 0 tests` con rc=0 → rechazar, apuntar a
  `test-clean`/`test-all`.
- `require-module`: `-i` de módulo inexistente no instala nada y corre 0
  tests con rc=0 → verificar que el módulo exista en algún addons_path.
- La DB caliente (`$(INST)_test`) es de iteración; la fresca de `test-all` es
  la evidencia. **Nunca declarar gate cerrado con corrida caliente sola.**

## Trampa de la coma en `--test-tags` (verificada: `odoo/tests/tag_selector.py`,
`re.split(r',(?![^\[]*\])', spec)`)

La coma separa SPECS completos: `mod:ClaseA,mod:ClaseB` corre ambas clases;
`mod:ClaseA,ClaseB` toma `ClaseB` como otro spec (sin módulo) y corre menos
tests de los esperados, **sin error**. Regla: repetir el prefijo en cada
spec, y verificar la línea `of N tests` contra el conteo esperado.

## Review: presupuesto 0 con identidad de árbol

Si `git diff --stat <commit-de-la-corrida-evidencia>..HEAD` muestra solo
commits `[STATE]`/docs, el árbol de código es idéntico → **se cita el log**
(ruta + línea), no se re-corre. Requisito: cada corrida de gate queda
registrada con su log y su commit (state file o mensaje de commit). Los
analizadores estáticos (`make lint`) no consumen presupuesto.

## Property tests: N como calibración

El spec define la postcondición; el N por defecto del ciclo de feature es
chico (8-10), con **seed fija** y N explícito como constante. Reducir N se
documenta en el commit como calibración (no debilitamiento). Subir N
pertenece al hardening, sin tocar postcondiciones.

## Fixtures self-contained (condición de DB fresca)

Verificado en fuente Odoo 19 (`odoo/tools/config.py:233`): el CLI crea las DB
**sin demo data** (`--with-demo` default False). Consecuencia: todo test que
facturee o toque contabilidad configura sus propios diarios/cuentas (chart
template genérico) en su fixture. Sin esto, pasa en DB caliente (diarios de
historias previas) y falla en la DB fresca del gate con `UserError: No
journal could be found`, lejos de la causa.

## Caso de origen (evidencia)

Antes: 6 corridas completas en ~6 h para validar una enmienda; 1.5 h
post-commit sin cerrar gate; tarea cancelada. Después: 4 `test-one` de ~45 s
identificaron 4 fallos con aserción exacta en UNA corrida; gate final 87/87
en 6m50s con 1 setup (`test-all`); review con 0 corridas (identidad de
árbol). Ninguna postcondición ni aserción fue debilitada.
