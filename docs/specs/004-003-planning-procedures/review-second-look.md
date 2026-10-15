# Segunda mirada — 004-003-planning-procedures (consolidada)

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-28>`.
> Paquete: `004-003-planning-procedures-reviewer-review-009`.
> Árbol revisado: `287f6c7`. Objeto: diff completo `5367e02..287f6c7`
> (43 commits; 17 archivos de código+tests, +2837/−19) + artefactos documentales.

## Evidencia ejecutada

| Comando | Resultado |
|---|---|
| `sha256sum …/spec.md` | `ba395fed…bf766` = contract sha ✓ |
| `pytest tests/test_004_003_t*.py -q` | **35 passed** |
| `pytest tests/ -q` | **364 passed in 475.38s** — confirma la cita del orquestador |
| `make validate` | **141 PASS / 2 FAIL** (F011: drift de mirrors `$HOME`; odoo en RED esperado de otra feature) |
| Validador real sobre el plan de 003-002 | `VALIDATOR OK — tasks: 4, strategy`, sha `781994fb…` = el citado en `t7-journey.md` ✓ |
| REDs (`git show --stat`) | tocan **solo** `tests/` ✓; marcadores ausentes en las bases → **REDs genuinos** ✓ |

## Parte A — Segunda mirada consolidada

**Dictamen: contenido fiel, salvo 1 hallazgo bloqueante de cierre y 8 opcionales/nits. Ningún bloqueante de código en el diff.**

- **AC-1** trazabilidad PD↔tests ✓ · **AC-2** borrador revisado sin aprobar, sesión distinta, producto instalado ✓ · **AC-3** fixtures de los 4 defectos contra checks reales ✓ · **AC-5** Go co-ubicado + ciclo sin código ✓ · **AC-6** dictamen + cambios concretos sin reimplementar 003-002 ✓ · **AC-8** limitaciones declaradas (parcial: el conflicto AC-7 no se declara — ver F-C1).
- **AC-4** ⚠ **satisfecha por disposición documentada** (uso real del ciclo + T7), NO por caso de flujo ejecutable; enmienda post-hoc de `plan.md` bajo HITL delegada, trazada. Residual declarado: **PD-5/PD-6 no tienen enforcement ejecutable** (disciplina del orquestador).
- **AC-7** ✗ ver F-C1.
- **Invariantes 1–7** ✓ en lo observable.

### F-C1 — AC-7 «los validadores pasan» no descargado al cierre · **BLOCKING (condición de cierre) · bucket m**

En `287f6c7`, `make validate` = **141 PASS / 2 FAIL** (F011-A: drift de mirrors `$HOME`; F011-B: odoo en RED esperado de otra feature). Ambos fallos **preexisten** a la feature (ningún archivo del diff está implicado). El defecto es procedimental: `review-t5.md` clasificó F011 como condición de cierre y el registro lo convirtió en deuda **sin decisión del dueño que exima AC-7**.
**Remedio:** decisión explícita del dueño (exención registrada) o fixing del patrón A3 + nota formal de alcance en el cierre.

### Opcionales

- **O-A (m)** — Los negativos de T1/T2 no fijan tokens del diagnóstico (T3/T4 sí): una denegación «por otra razón» seguiría pasando. Remedio: fijar los tokens.
- **O-B (m)** — La paridad instalada tiene test automatizado solo para el render `plan-review`; el contenido T1/T4/T5 en la instalación se evidencia solo con conteos grep de T7. Remedio: extender el test de producto instalado.
- **O-C (m)** — `--contract-path` de draft-plan acepta **cualquier** archivo del proyecto (p. ej. la lista privada de patrones); su sha queda en los artefactos publicados. Exposición local baja, pero es superficie de lectura no declarada. Remedio: restringir a `docs/**`.
- **O-D (m)** — `handoff-prompts.md:543` (deuda O2 confirmada abierta): la plantilla de `plan-review` omite las 3 flags obligatorias.
- **O-E (l)** — Las citas de suite del ciclo registran commit+conteo pero no `path+línea+commit` como exige la regla instalada.
- **O-F (l)** — El discriminador por `count(token)!=1` rechaza planes que **mencionen** ```plan-tasks en prosa (falso positivo conservador, fail-loud).
- **O-G (nit)** — Números de comentario fuera de orden en `_check_plan_tasks`.
- **O-H (l)** — `evidence/t7-journey.md` no registra las líneas de comando exactas de `prepare`/render del recorrido.

**FYI:** el encargo decía «5 archivos de test»; la feature entregó **7** — la auditoría cubre los 7.

## Parte B — Auditoría test↔postcondición

Ver `test-audit.md` (materializado junto a este informe).

## Deuda consolidada (abierta, trazada; ninguna rompe el camino feliz)

T1: F3 (`plan_version: null` por valor), F4 (path doble), F5 (huecos negativos) · T2: O1 (newline), O2 (=O-D), O3 · T4: F-C (parcialmente cubierto por el lock), F-E (`__pycache__` en A3) · T5: F-C1, F4/F5 (co-dueño SKILL mal etiquetado), F6 (comparadores concretos), F011 · T7→003-002: F3–F6 de `review-plan-001` · T6/F4 condicional para el primer consumidor Go.

## Abstenciones

1. No reprodujo los estados RED en worktrees frescos; verificación estructural alternativa (commits RED solo-tests + ausencia de marcadores en las bases).
2. No re-ejecutó la instalación aislada: la cita PASS (303 grupos) de T7 no es reproducible desde este checkout; su `install.sh --check` mide el drift de `$HOME` (otra cosa). No verdicta sobre esa cita.
3. Dictamen T7 y sesiones independientes: juzgados desde artefactos; la salida original de los modelos no es verificable.
4. Alcance exacto de `plan_version` como identidad: indecidible desde la spec sola.
5. Contenido del paquete en disco: fuera de su lectura necesaria.
