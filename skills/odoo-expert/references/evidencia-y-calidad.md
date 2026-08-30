# Evidencia requerida y anti-racionalización

Rescatado del skill `odoo-dev-methodology` (retirado; su contenido vive acá).

## Evidencia — no negociable

**Regla de oro:** "parece andar" nunca alcanza. Un módulo está listo cuando hay
**evidencia**, no cuando parece funcionar.

| Verificación | Evidencia requerida (empírica, no asumida) |
|---|---|
| Lint | `pylint --load-plugins=pylint_odoo -d all -e odoolint <module>/` sin errores |
| Checks OCA | `oca-checks-odoo-module <module>/` sin hallazgos |
| Tests | el runner del proyecto en verde, con la línea de resumen: `0 failed, 0 error(s) of N tests` |
| Instalación desde cero | instalación en **DB limpia**, no un update sobre la de desarrollo |
| Fuentes | cada decisión de diseño citando el addon de Odoo donde se verificó |

> **Cómo se corren los tests lo define el entorno, no este skill.** Si el
> proyecto expone el contrato `odoo-make-env`, es `make test` (suite),
> `make test-one` (uno) y `make test-clean` (instalación desde cero). **No
> invoques `odoo-bin` a mano en un gate**: perdés las guardas del contrato — en
> particular, `-u` sobre un módulo no instalado reporta *"0 failed, 0 error(s)
> of 0 tests"* con **exit 0**, que un gate leería como verde habiendo corrido
> cero tests.

**Reglas de evidencia**

1. **El output es la prueba.** Pegá las últimas líneas del run, con el resumen.
   "Los tests pasan" sin output no es evidencia.
2. **Sin evidencia, no hay deploy.** Un módulo sin suite verde no se instala en
   producción.
3. **Cobertura ≠ correctitud.** Un test que pasa prueba que el código hace lo que
   el test dice, no que el contrato sea correcto. Verificar contra el source de
   Odoo es complementario, no opcional.
4. **Demo data ≠ test data.** Los tests deben pasar sin depender de registros
   demo (regla OCA).
5. **Deuda documentada ≠ deuda oculta.** Si un check no se puede correr hoy, se
   registra explícito; nunca se omite en silencio.

## Anti-racionalización

Cuando aparezca la excusa, la refutación ya está escrita. No se negocia.

| Excusa | Refutación |
|---|---|
| "Es un módulo chico, no hace falta test" | El tamaño no predice el riesgo: 50 líneas pueden romper la vista de un modelo base. Todo módulo lleva sus tests. |
| "Lo probé a mano y anda" | Probar a mano verifica un camino; los tests verifican el contrato y lo protegen de regresiones. |
| "pylint-odoo da falsos positivos, lo salteo" | Los checks Odoo son la diferencia entre un módulo mantenible y uno que alguien va a tener que desarmar. Un falso positivo se justifica por comentario, no por omisión. |
| "Es un cambio de una línea en el XML" | Un `<field>` mal ubicado en un xpath rompe la vista entera en runtime y se descubre en producción. Los checks lo atrapan en dev. |
| "No hay tiempo, el test lo agrego después" | Un test escrito después verifica lo que el código hace, no lo que el spec pide. Y "después" no llega. |
| "El cliente lo necesita YA" | La urgencia no elimina el riesgo: lo transfiere. Un deploy roto cuesta más que el tiempo ahorrado. |
| "Odoo ya lo hace así, no hace falta verificar" | Eso es el punto de partida de la verificación, no su final: se lee el source y se cita dónde. |
| "Lo hago rápido por el editor web" | El editor web genera deuda no versionada: no se revisa, no se testea, no se migra, no se audita. Módulo, no editor. |

**Red flags que disparan esta tabla:** "es rápido", "lo probé a mano", "no hace
falta", "el cliente espera", "pylint molesta", "después lo testeo".

## pre-commit (setup OCA)

OCA usa `pre-commit` para el formateo automático. En una migración, el paso de
`pre-commit run -a` va en un commit **aparte** (`[IMP] <module>: pre-commit auto
fixes`), separado del trabajo real, para que el diff de la migración sea legible.
