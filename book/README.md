# Libro CDAD

Este directorio contiene una edición profesional del manuscrito **Contract-Driven AI Development (CDAD)**.

## Estructura
- `manuscrito.md`: versión principal lista para edición/maquetación.
- `chapters/01-13-base.md`: texto fuente original consolidado.
- `diagrams/`: diagramas Mermaid.
- `assets/cover.svg`: portada estilo técnico clásico con piche/armadillo.
- `styles/pandoc.css`: estilo base para exportación HTML/PDF.

## Build sugerido (local)
```bash
pandoc book/manuscrito.md -o CDAD-libro.pdf
pandoc book/manuscrito.md -o CDAD-libro.epub
```
