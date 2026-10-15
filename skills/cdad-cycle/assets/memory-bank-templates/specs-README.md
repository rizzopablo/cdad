# Specs

Specs per feature, one folder per feature with format `NNN-feature-id/`.

## Structure per feature

```
specs/
└── 001-feature-id/
    ├── spec.md       ← mandatory, approved before Stage 3
    ├── review.md     ← created in Stage 4
    └── plan.md       ← optional, for large features with several phases
```

## Numbering

Sequential by order of creation. `001-`, `002-`, etc. The suffix is kebab-case.

## Approval

Each `spec.md` carries an unambiguous approval mark at the end or in frontmatter. Without that mark, implementation does not start.
