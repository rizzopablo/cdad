# Tabla de oro V1 -> V2 (derivada por el orquestador del frontmatter V1 actual)

Regla: cada fila es una entrada de la lista `permissions:` en V2, en ESTE orden;
`bash` se emite como `action: shell`. Los valores son literales del V1 vigente.

## cdad-test-writer (agents/cdad-test-writer.md)

| # | action | resource | effect |
|---|---|---|---|
| 1 | read | `src/**` | deny |
| 2 | read | `lib/**` | deny |
| 3 | read | `src/**/*_test.go` | allow |
| 4 | read | `src/**/test_*.py` | allow |
| 5 | read | `src/**/*.test.js` | allow |
| 6 | read | `src/**/*.test.ts` | allow |
| 7 | read | `src/**/*.test.mjs` | allow |
| 8 | read | `src/**/*.test.cjs` | allow |
| 9 | read | `src/**/*.spec.ts` | allow |
| 10 | read | `src/**/*.spec.js` | allow |
| 11 | read | `lib/**/*_test.go` | allow |
| 12 | read | `lib/**/test_*.py` | allow |
| 13 | read | `lib/**/*.test.js` | allow |
| 14 | read | `lib/**/*.test.ts` | allow |
| 15 | read | `lib/**/*.test.mjs` | allow |
| 16 | read | `lib/**/*.test.cjs` | allow |
| 17 | read | `lib/**/*.spec.ts` | allow |
| 18 | read | `lib/**/*.spec.js` | allow |
| 19 | edit | `*` | deny |
| 20 | edit | `tests/**` | allow |
| 21 | edit | `**/tests/**` | allow |
| 22 | edit | `**/*_test.go` | allow |
| 23 | edit | `**/*.test.js` | allow |
| 24 | edit | `**/*.test.ts` | allow |
| 25 | edit | `**/*.test.mjs` | allow |
| 26 | edit | `**/*.test.cjs` | allow |
| 27 | edit | `**/*.spec.ts` | allow |
| 28 | edit | `**/*.spec.js` | allow |
| 29 | edit | `**/test_*.py` | allow |
| 30 | shell | `*` | allow |
| 31 | grep | `src/**` | deny |
| 32 | grep | `lib/**` | deny |

## cdad-orchestrator

V1: `permission: allow` (permiso total). V2: una única entrada

| # | action | resource | effect |
|---|---|---|---|
| 1 | `*` | `*` | allow |

