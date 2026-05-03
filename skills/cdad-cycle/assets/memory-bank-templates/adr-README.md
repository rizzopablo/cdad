# Architecture Decision Records (ADR)

Decisiones arquitectónicas del proyecto. Inmutables una vez aceptadas.

## Cuándo crear un ADR

Si dentro de 6 meses, alguien (vos o un agente) podría preguntar **"¿por qué hicimos X de esta forma?"**, esa decisión merece un ADR.

Ejemplos típicos:

- Elección de base de datos.
- Decisión de arquitectura (monolito vs servicios, layering, bounded contexts).
- Elección de librería principal cuando había alternativas.
- Patrones que se prohíben deliberadamente.

## Cuándo NO crear un ADR

- Decisiones de implementación local (qué algoritmo usar dentro de una función).
- Convenciones generales del proyecto (van a `systemPatterns.md`).
- Estado actual o trabajo en curso (va a `activeContext.md`).

## Numeración y formato

`ADR-NNN-titulo-en-kebab-case.md`. Numeración sequencial.

Template en `<skill>/assets/adr-template/ADR.md`.

## Estados posibles

- **Proposed**: en discusión.
- **Accepted**: aprobado, en vigor.
- **Deprecated**: ya no aplica pero no fue reemplazado.
- **Superseded by ADR-NNN**: reemplazado por otro ADR.

Una vez **Accepted**, un ADR no se modifica. Si la decisión cambia, se crea un nuevo ADR que `supersede` al anterior.
