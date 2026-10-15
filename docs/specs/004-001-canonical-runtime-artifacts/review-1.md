# Review focal T4 — 004-001-canonical-runtime-artifacts

Fecha: 2026-09-26. Reviewer: GPT/Codex (familia distinta del implementer GLM,
cadena de autoridad de `docs/epics/epic-004-single-source-planning/execution.md`).
Árbol revisado: `643b4b0`. Diff: tests `580816f` + implementación `d011741`.
Read-only: no se modificaron código, tests ni estado.

## Verdict

```
dictamen: changes-required
blocking: 2
optional: 0
abstain:  0
```

## Hallazgos

### B1 — Expansión incorrecta de comandos git habituales

- **Verdict:** BLOCKING · **Bucket:** h
- El generador interpreta `git diff/git log/git status` agregando nuevamente el
  prefijo: produce `"git git log*"`, `"git git status*"`, `"git git blame*"`.
  Desaparecen las reglas correctas para architect, reviewer y scribe.
  **Confirmado que el defecto llega a las variantes Odoo instaladas.** Perjudica
  la inspección necesaria para trabajar y supervisar.
- Provenance: `d011741`, `scripts/cdad-generate.py:263` (especialmente 271–272);
  declaración en `sources/roles/architect.md:68`. Contrato: PD-1 y capacidades
  positivas de T4.

### B2 — La instalación descarta parte de las mejoras y conserva dos fuentes de permisos

- **Verdict:** BLOCKING · **Bucket:** h
- El generador nuevo lee las fuentes canónicas, pero el instalador reemplaza los
  permisos de los agentes genéricos usando el antiguo script (`cdad-bash-allowlist.sh`),
  cuya lógica sigue escrita por separado. Reproducido: `du` desaparece del
  architect instalado; `rtk ls`/`rtk pwd` desaparecen del test-writer instalado.
  **`install.sh --check` devuelve PASS igualmente**, porque compara contra esa
  misma política antigua. Cambiar la fuente canónica todavía no garantiza cambiar
  el producto utilizado.
- Provenance: `d011741`, `scripts/cdad-bash-allowlist.sh:6` y lógica independiente
  desde línea 147; consumidor en `install.sh:127`. Contrato: PD-1 y entrega de T4 —
  reglas canónicas, pares completos y aterrizaje utilizable.

## Comprobación independiente del reviewer

3 tests de T4 pasan; instalación aislada pasa; `install.sh --check` PASS 46/46.
Los dos defectos están presentes en esos archivos instalados. No se ejecutaron
sesiones de proveedores ni la suite completa de 67 tests.
Logs del reviewer: `/tmp/cdad-t4-review-yux00z4n/{focused,install,check}.log`.

## Corrección acotada propuesta (para el implementer)

1. Corregir la expansión de comandos (doble prefijo git).
2. Hacer que generación e instalación consuman una misma política, conservando
   la interfaz actual y dejando el manifest para T5.
3. Verificar desde lo instalado unas pocas operaciones representativas:
   inspeccionar cambios, medir y ejecutar el runner acordado. Sin batería de
   controles por cada comando.

> Nota del reviewer: centralizar reglas es un medio; la mejora tiene que llegar
> al trabajo cotidiano del agente. Esto aún no demuestra menor fricción.

## Dictamen

Conservar el trabajo válido; corregir B1/B2 antes de cerrar el aterrizaje A.
Materializado por el orquestador (GLM) desde el reporte final del reviewer
(ADR-003). El usuario (Pablo) transmitió el informe y avaló la corrección
acotada en la misma sesión.
