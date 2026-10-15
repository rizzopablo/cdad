# ADR-017 — Activación por proyecto hacia una raíz aislada adoptada (nunca las configuraciones del HOME real)

* Estado: **aceptado** (2026-10-08, orquestador bajo delegación HITL de epic-003; borrador del scribe)
* Fecha: 2026-10-08
* Decisores: dueño (Pablo); orquestador bajo delegación HITL de epic-003
* Confianza: **Media**

## Contexto y enunciado del problema

Varias features de epic-003 (`prepare`/`receive`, `cdad_guard`, `cdad_continuity`) existen
y están probadas, pero cada runtime (OpenCode, Claude Code, Codex) cargaba **versiones
distintas** de skills/agentes y las copias globales de HOME derivan (F011). Hacía falta un
mecanismo soportado para que un runtime cargue una **versión operativa concreta** dentro de
un proyecto, sin escribir las configuraciones del HOME real (I1) y sin duplicados que
puedan divergir.

## Impulsores de la decisión

- Una sola versión operativa por runtime, verificable (I2) e identificable por manifest.
- Cero escrituras en `~/.claude`, `~/.agents`, `~/.config/opencode`.
- Determinismo, no-clobber y seguridad de ruta (nada fuera de la raíz del proyecto).

## Opciones consideradas

1. **Instalar CDAD globalmente en HOME** (estado de facto). Rechazada: deriva entre copias,
   F011, y la regla vigente que prohíbe instalar CDAD en HOME real.
2. **Copiar las skills dentro del repo.** Rechazada: `install.sh` rechaza un destino dentro
   del repo fuente (L2) y las copias pueden divergir.
3. **Raíz aislada versionada + activación de proyecto que apunta a ella** (elegida).

## Decisión

La versión operativa se instala en **una raíz aislada versionada** bajo `~/.cache`
(`cdad-adopted-<rev>`), se registra con verificación de consumidor, y los runtimes la
cargan mediante **archivos de activación por proyecto, git-ignorados**, generados por
`scripts/cdad-activate.py` (`--project-root/--adopted-root/--runtime/--dry-run`):
determinista, `--dry-run` sin efectos, **no-clobber** (destino divergente → error) y
**contención de ruta** (`realpath` estricto bajo la raíz del proyecto). El hook de Claude
Code se emite con `CDAD_PACKET_CLI` fijado a la raíz adoptada (RU-1). La activación **no**
se commitea; activar y apuntar a una versión nueva es **decisión del dueño**.

## Consecuencias

- **Positivas:** una sola fuente de la versión operativa; identidad verificable; ninguna
  escritura en HOME; adopción reproducible y auditable; `receive`/continuidad cableados.
- **Negativas / límites declarados:** los archivos de activación no se versionan (producto =
  generador + procedimiento + tests); **Claude Code** mezcla versiones (skills de usuario
  ganan) y sus hooks requieren confianza de carpeta (mitigación `--setting-sources
  project,local`); **Codex** presenta catálogo ambiguo y no tiene adaptador de agentes;
  **T4-REF** bloquea la reanudación si cambia una referencia a documento vivo; sin CI.

## Alternativas y trabajo futuro

Endurecimiento a deuda: referenciar solo artefactos inmutables o `path@sha` en los
checkpoints (T4-REF); semántica de la clave del checkpoint de límite (T4-CKPT); lector de
sesiones por runtime (`classify`); medición de contexto; CI; anonimización de rutas
absolutas (ANON-1).

## Enlaces

- Spec/plan: `docs/specs/003-006-runtime-adoption/{spec,plan}.md`
- Evidencia: `docs/specs/003-006-runtime-adoption/adoption-ledger.md`, `dispatch-ledger.md`,
  `debt.md`
- ADR relacionados: ADR-002 (repo fuente + `install.sh`), ADR-008 (Claude Code como segundo
  runtime), ADR-012 (política de límites por proyecto), ADR-014 (recepción/materialización/
  aprobación), ADR-016 (continuidad)
- Enmienda de cierre pendiente: `docs/epics/epic-003-context-efficiency/closure-amendment-draft.md`
