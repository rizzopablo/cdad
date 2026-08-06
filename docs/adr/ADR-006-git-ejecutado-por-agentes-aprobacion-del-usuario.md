# ADR-006: La ejecución de git es de la capa de agentes; la aprobación es del usuario

- **Status**: Accepted
- **Date**: 2026-08-05
- **Deciders**: Pablo (dueño del proyecto) + Ofap

## Contexto

Principio rector: **el humano nunca toca git**. Toda la ejecución de git la
hace la capa de agentes: los roles commitean su trabajo, el orquestador
commitea `docs/**` y el state file. El patrón Scribe asumía que el usuario
ejecutaba el commit del Memory Bank ("el usuario edita y commitea"); con el
humano fuera de git, el commit no puede ser su acción. Las decisiones
estratégicas (aprobar spec, priorizar review, aprobar Memory Bank) siguen
siendo del usuario — humano o agente autónomo de mayor jerarquía —, pero la
ejecución de git ya no le pertenece: la aprobación es indelegable, la
ejecución de git no.

Además, la causa raíz del commit blocker de los roles write-capable era el
patrón de staging con glob `*` (un solo nivel de path): `git add tests/*` /
`git add src/*` / `git add lib/*` denegaba los paths anidados y el rol no
podía commitear. Sin staging recursivo (`**`) los roles no ejecutan su propia
parte del git, y sin git del orquestador sobre `docs/**` no se commitean
artefactos ni state. El fix combina ambos: staging recursivo para roles y
allowlist de git del orquestador sobre docs.

## Opciones consideradas

### Opción A: Mantener el usuario como ejecutor del git (status quo)
- Pros: cero cambios de texto; el patrón Scribe original no se toca.
- Contras: contradice el principio "el humano nunca toca git"; en el modo
  autónomo (heartbeat) no hay humano que ejecute el commit → el Memory Bank
  queda sin commiteo o se delega informalmente a un agente sin definir quién.

### Opción B: La capa de agentes ejecuta todo el git; el usuario solo aprueba
- Pros: ciclo completamente autónomo sin fricción de humano para el git;
  granularidad preservada por scope (roles commitean tests/código, orquestador
  commitea `docs/**`); la frontera de poder queda explícita (aprobación =
  usuario, ejecución = agentes).
- Contras: el orquestador gana git-write sobre `docs/**` (responsabilidad
  nueva); el patrón Scribe pasa de una frontera estructural (el escriba no
  puede commitear) a behavioral (el orquestador commitear tras aprobación).

### Opción C: Un rol dedicado de "git runner" separado del orquestador
- Pros: separación de poderes máxima.
- Contras: sobre-ingeniería para este tamaño; el orquestador ya es el dueño de
  la materialización de artefactos y del state file — agregarle el commit de
  docs es su responsabilidad natural.

## Decisión

Toda la ejecución de git es de la capa de agentes:

- **Roles write-capable** (test-writer, implementer) commitean su propio
  trabajo (tests, código) con staging recursivo (`tests/**`, `src/**`,
  `lib/**`).
- **Orquestador** commitea `docs/**` y el state file (`git add docs/**` +
  `git commit`), incluido el Memory Bank tras la aprobación del usuario.
- **Decisiones estratégicas** (aprobar spec, priorizar review, aprobar Memory
  Bank) son del **usuario** — humano o agente autónomo de mayor jerarquía —,
  indelegables.

ADR-004 se refina: la aprobación es indelegable, la ejecución de git no. La
definición de "usuario" (ADR-004) no cambia; cambia el verbo que se le asigna:
aprueba, no commitea.

## Razones

1. El humano nunca toca git: sin un humano ejecutor, el commit del Memory
   Bank tenía que caer en algún agente — el orquestador es quien materializa
   los artefactos y actualiza el state, el candidato natural.
2. La aprobación indelegable se preserva: el orquestador ejecuta el git solo
   tras la aprobación del usuario; no se auto-aprueba (mismo guardrail que
   ADR-004).
3. Granularidad de commits preservada por scope: los roles commitean su capa
   (tests/código), el orquestador commitea la capa de docs/state — no hay un
   commit global (`git add .` queda fuera de la allowlist).

## Consecuencias

**Positivas:**
- Cero git humano: el ciclo es autónomo de punta a punta; el usuario solo
  decide, no ejecuta.
- El orquestador commitea `docs/**` + state: los artefactos de roles
  read-only y el Memory Bank dejan de quedar huérfanos de commit.
- Granularidad preservada: los roles commitean su propio trabajo con staging
  recursivo (`**`) que matchea paths anidados.

**Negativas / trade-offs:**
- El orquestador gana git-write sobre `docs/**` (responsabilidad nueva; la
  allowlist lo limita a docs, sin `git add .` ni `git add *`).
- La frontera del patrón Scribe pasa de estructural (el scribe tiene
  write: deny) a behavioral (el scribe sigue sin commitear, pero quien
  commitea por él es el orquestador tras aprobación, no el usuario).

**Neutrales:**
- `git push` queda fuera de la allowlist: es una acción externa y puntual que
  requiere aprobación explícita del usuario cuando corresponda.

## Verificación (realizada 2026-08-05)

- `bash install.sh --check` → PASS (12/12) tras el install.
- `bash scripts/validate-subagents.sh` → PASS (incluye la Etapa 1b de
  chequeo de modelos por agente).
- `bash docs/specs/cdad-001-validate-subagents/tests/run_all.sh` → PASS.
- Grep `edita y commitea|el humano edita y commitea` en `skills/ agents/` →
  0 resultados.

## Notas

Refina ADR-004 (quién es el usuario no cambia; qué ejecuta sí). Complementa
ADR-005 (modelos por agente) con la Etapa 1b del validator, que duplica el
mapa ADR-001/005 como guard de validación intencional.
