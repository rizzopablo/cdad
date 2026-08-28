---
name: "odoo-test-writer"
description: >
  Framework de tests Odoo para el rol test-writer de CDAD en proyectos Odoo.
  TransactionCase, @tagged obligatorio, Form→web, freeze_time para fechas,
  fixtures self-contained sin demo data (OCA), make test-one para RED / make
  test para AUDIT, new_test_user para permisos, post_install para cross-module.
  Usar en la etapa 3 (TDD) de cualquier feature sobre un addon Odoo.
---

# odoo-test-writer — framework de tests en addons Odoo

> Reglas OCA + docs oficiales Odoo (testing framework). El contrato de
> ejecución (`make test` / `make test-one` / `make test-clean`) vive en el
> skill `odoo-make-env`; acá está el contenido del test, no el runner.

## Clase de test: TransactionCase (clase única moderna)

Usá **`TransactionCase`** como clase base. Es la clase recomendada por Odoo
17+ (los tests corren dentro de una transacción que se revierte al final, una
`SavepointCase` que no crea DB propia). Evitá la fragmentación innecesaria en
varias clases heredadas de márgenes viejas; una sola clase TransactionCase por
archivo salvo que haya una razón real de agrupar.

```python
from odoo.tests import TransactionCase, tagged

@tagged("cdad")
class TestIdeaLog(TransactionCase):
    ...
```

## `@tagged` es OBLIGATORIO

Los tests **sin tag no corren** en la suite por `--test-enable` estándar de
Odoo (los tags son el filtro de selección). Todo test que quieras que corra
debe llevar un decorador `@tagged(...)` con al menos un tag. El tag también
permite seleccionar con `--test-tags` y marcar `post_install`.

```python
@tagged("cdad")          # corre en la suite default
@tagged("post_install", "-at_install")  # corre después de instalar todos los addons (cross-module)
```

## `Form[...]->web`: el helper Form exige la dependencia `web`

El objeto `Form` (UI mock para armar registros como un formulario) requiere
que el addon declare el módulo `web` en `depends` del `__manifest__.py`. Sin
esa dependencia, `Form` no está disponible en el entorno de test.

```
Form[self.model_name]->web   # el iterador autoenvía en la versión 17+
```

En Odoo 17+ `Form` es un iterable que agrega el registro al autoenvío; la
construcción se valida al `env["..."]` con `web` presente.

## Fechas: `freeze_time` (no reloj real)

Para aserciones sobre fechas, congelá el reloj con `freeze_time` de
`odoo.tests` (envuelve el cuerpo del test con una fecha fija) en vez de
depender del reloj real del runner. Esto hace el test determinista.

```python
from odoo.tests import freeze_time

def test_pago_fecha(self):
    with freeze_time("2026-01-15"):
        record.action_registrar()
        self.assertEqual(record.fecha, "2026-01-15")
```

## Fixtures self-contained — PROHIBIDO depender de demo data

Los fixtures de un test deben ser **self-contained**: creá los datos que el
test necesita dentro del propio test (registros de partners, productos, etc.)
**sin depender de la demo data** del addon o de datos preexistentes. Regla OCA:
un test no debe asumir que la demo data está cargada ni que un registro
"siempre existe". Si el módulo necesita crear un partner, lo creás vos en el
setUp con `env["res.partner"].create(...)`.

## Ubicación: tests/ del addon con __init__.py

- Los tests viven en `**/tests/` del addon, cada archivo con su
  `__init__.py`.
- El `__init__.py` de `tests/` importa los módulos de test.
- El `__init__.py` del addon importa `tests` (o declara el paquete).
- Un archivo de test por área/caso; nombres `test_<descripcion>.py`.

## Runner: `make test-one` para RED, `make test` para AUDIT

- **RED** (test nuevo que debe fallar): corré SOLO ese test con
  `make test-one TEST=mod:Clase.metodo` y verificá que falle por
  **AssertionError** (no por ImportError/error de carga).
- **AUDIT / suite completa**: `make test` corre toda la suite sobre la DB
  caliente.
- **Gate de instalación**: `make test-clean` instala desde cero con demo data.
- Evidencia = output pegado con la línea `0 failed, 0 error(s) of N tests`.

## Permisos: `new_test_user`

Para tests que ejercitan **permisos/seguridad**, creá el usuario de test con
`env["res.users"].new_test_user(...)` (helper Odoo 17+) con los grupos que el
escenario requiere, en vez de usuarios reales o disparos manuales de
`_check_access`. Verificá que el usuario sin el grupo falle (AccessError) y el
que lo tiene pase.

```python
user = self.env["res.users"].new_test_user(login="operario", groups="base.group_user")
```

## Cross-module: `post_install`

Cuando el test valida un flujo **cross-module** (involucra otros addons más
allá del bajo test), marcá el test con `@tagged("post_install",
"-at_install")` para que corra después de instalar todos los addons de la DB.

## Anti-patrones a evitar

- Test que depende de demo data o de registros asumidos (rompe en `test-clean`).
- Test sin `@tagged` (nunca corre en la suite).
- Usar `Form` en un addon que no declara `web` (ImportError en runtime).
- Fechas dependientes del reloj real del runner.
- `pass` o asserts que no verifican nada (test que no es oráculo).