# Test Audit Report — <feature-id>

**Feature**: <nombre>
**Spec version**: <version o fecha>
**Test Writer**: <nombre/rol>
**Audit completed**: <fecha>

## Comportamiento que cambia (resumen)

(Párrafo corto con los cambios principales listados. Referencia a líneas en spec.md)

Ejemplo:
- Descuento por cliente frecuente ahora valida período de 6 meses (antes 12 meses)
- Descuento es mutualmente excluyente con cupones (comportamiento nuevo)
- Cálculo de descuento en % se mantiene igual

---

## Tests modificados

Cada entrada tiene esta estructura:

```
### <test-name>
- **Cambio**: [descripción breve]
- **Spec ref**: [línea/sección donde se justifica el cambio]
- **Nueva expectativa**: [qué verifica ahora]
- **Porqué**: [Justificación breve]
```

**Ejemplo:**

```
### test_descuento_aplicado_a_cliente_frecuente
- **Cambio**: Actualizar ventana temporal de 12 a 6 meses
- **Spec ref**: Section "Elegibilidad", línea "últimos 6 meses"
- **Nueva expectativa**: Cliente con compras >$10k en últimos 6 meses califica para descuento
- **Porqué**: Feature nuevo requiere período más restrictivo para control de presupuesto Q2
```

---

## Tests nuevos a escribir

Lista de tests que no existían y esta feature requiere:

- `test_descuento_incompatible_con_cupones`
- `test_cupones_validos_sin_descuento_por_cliente_frecuente`

---

## Tests sin cambios (untouched)

**Estos tests se mantienen EXACTAMENTE como están** porque validan comportamiento que sigue siendo válido:

- `test_aplicar_descuento_si_criterio_cumple` (el cálculo % es igual)
- `test_sin_descuento_si_cliente_nuevo` (regla de cliente nuevo se mantiene)
- `test_descuento_maximo_permitido` (límite máximo no cambia)

**Importancia**: listarlos explícitamente confirma que el implementer NO debe tocar estos tests.

---

## Regression Risk Assessment

¿Hay comportamiento descrito en spec nuevo que NO tiene cobertura de test?

- ✅ Cobertura completa
- ⚠️ Riesgo: [listar qué falta]

---

## Gate de Test Audit

- [ ] Cada test modificado está justificado en spec.md con referencia explícita
- [ ] No hay test modificado sin justificación documentada
- [ ] Tests untouched están listados (confirma que se conocen las implicaciones)
- [ ] Regression risk assessment completado
- [ ] Humano aprobó este report antes de pasar a RED
