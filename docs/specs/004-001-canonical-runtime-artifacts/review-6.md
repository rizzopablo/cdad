# Review-6 focal T5 — 004-001-canonical-runtime-artifacts (cierre de T5)

Fecha: 2026-09-28. Reviewer: GPT/Codex (familia distinta del implementer GLM).
Probes propios del reviewer en worktree y raíces aisladas; sin modificar código,
tests, estado ni instalaciones reales.

## Verdict

```
dictamen: changes-required
blocking: 1 (chico, bucket m)
optional: 2 (observaciones)
abstain:  0
```

## Cierre verificado de review-5 (evidencia propia del reviewer, no asumida)

| Hallazgo | Probe del reviewer | Resultado |
|---|---|---|
| B1 | instaló, modificó `cdad-reviewer.md`, `--check` | **rc=1**, `DRIFT: differs ...` nombra el archivo |
| B2 | modificó `SKILL.md` de cdad-cycle y `path-guard.sh`, reinstaló | 3 `CONFLICT: ... preserved`; preservados byte a byte (sha256 idéntico) |
| B3 | sacó `cdad-scribe-odoo.md` del staging y del manifest, reinstaló | `PENDING-REMOVAL` en `--check` (rc=1), persistido, **retirado** por `--uninstall` |
| B4 | `--basic` con staging `optimus` | `PROFILE MISMATCH` informado; marker == manifest == staging; sin etiquetas contradictorias |
| E1 | modificó agente, `--uninstall --force` | `CONFLICT: ... PRESERVED`; `362 of 363 removed, 1 preserved`; archivo intacto |

Gates reproducidos: suite **85/85** con `env -u TMPDIR` (19m39s, configuración
honesta); tres validadores PASS en raíz aislada; contra HOME real, único FAIL
F011 (deuda de migración → T6, ya acordada). PD-18 se sostiene: `install.sh`
no lee `sources/`. R3-B1 sigue bien cerrado (y el test ahora también limpia
`TMPDIR`).

## Hallazgo bloqueante

### R6-B1 — `--basic` promete lo contrario de lo que hace, y termina con éxito

- **Verdict:** BLOCKING · **Bucket:** m · **Confianza:** alta
- **Ubicación:** ayuda de `--basic` en `install.sh`; comportamiento con staging
  `optimus`.
- **Motivo:** la ayuda dice *"--basic: NO fixed models — agents inherit the
  runtime's default model. Portable across providers (useful when the primary
  provider's accounts are exhausted...)"*. Con staging `optimus`, `--basic`
  termina con **rc=0** e instala `model:` del staging. El desacuerdo se informa
  en el log (lo que pedía review-5), pero el pedido explícito queda anulado con
  salida exitosa. En el caso de uso documentado —cambiar de proveedor por
  agotamiento de cuenta— alguien correría `--basic`, vería éxito y desplegaría
  los modelos del proveedor agotado.
- **Cierre mínimo aceptado por el reviewer:** (i) corregir la ayuda ahora (una
  línea, igual que la entrada de `--optimus`, que sí aclara que los bytes llevan
  el perfil del staging) + (ii) decisión registrada; el resto del
  comportamiento (rc≠0 / regeneración de staging / retirar flags) se dispone a
  T6. Lo único inaceptable es el estado actual: flag aceptado, promesa
  incumplida, rc=0.

## Observaciones (opcionales)

- Reinstalar con conflictos devuelve rc=1 aunque el resto instale bien:
  defendible, pero conviene una línea en la ayuda: rc=1 significa conflictos
  pendientes, no instalación rota.
- La huella en el home crece (`.cdad-install-manifest.json`, layout público
  `$HOME/agents|skills`): bien si D6 aterriza en T6, como está planeado.

## Disposición de la fuga de fase (test-writer)

**Desviación registrada, no incumplimiento material**, con dos condiciones
verificadas por el reviewer: (1) oráculos de efecto observable, no de
estructura interna; (2) los cinco probes del reviewer reproducen el
comportamiento sin depender de los tests — el cierre no descansa en oráculos
posiblemente contaminados.

**Regla para T6:** oráculos congelados antes del GREEN; todo cambio posterior
requiere firma del reviewer declarando qué invariante semántica no cambió
(exactamente lo que hizo `9302c1f`).

**Causa de fondo → bucket 003-003, no disciplina:** el test-writer necesitaba
saber si un fixture era viable — necesidad legítima de información que el
paquete no cubría. La solución es completar el paquete, no pedir más
autocontrol.

## Cierre de T5

Con R6-B1 resuelto (ayuda corregida + decisión registrada), **T5 cierra**.
"El resto está sólido: es el trabajo más prolijo de este ciclo."

Materializado por el orquestador (GLM) desde el reporte final del reviewer
(ADR-003).
