# Specs

Specs por feature, una carpeta por feature con formato `NNN-feature-id/`.

## Estructura por feature

```
specs/
└── 001-feature-id/
    ├── spec.md       ← obligatorio, aprobado antes de Etapa 3
    ├── review.md     ← creado en Etapa 4
    └── plan.md       ← opcional, para features grandes con varias fases
```

## Numeración

Sequencial por orden de creación. `001-`, `002-`, etc. El sufijo es kebab-case.

## Aprobación

Cada `spec.md` lleva una marca de aprobación inequívoca al final o en frontmatter. Sin esa marca, no arranca implementación.
