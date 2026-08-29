# VALIDATION — cdad-003 Odoo-CDAD (bitácora de validación)

> Registro consolidado del recorrido completo: F0 → F2 → F3 → Fb → F1 (ciclo
> CDAD) → A1. Fecha: 2026-08-28. Los hallazgos operativos por entorno viven en
> `drafts/f0-odoo-sh-environment.md`, `drafts/fb-make-contract.md`,
> `drafts/odoo-test-module-definition.md` y (privado) en la infra interna.

## 1. F0 — Discovery de entornos

Dos entornos reales explorados por SSH (odoo.sh dev + staging privado).
Descubrimientos que condicionaron el diseño:
- odoo.sh: no se pueden crear DBs (solo la del build), builds dev siempre con
  demo data, sin apt, `scp` restringido (usar tar|ssh).
- staging privado: `CREATEDB` disponible, postgres compartido multi-tenant
  saturable, conf de plataforma no editable (se usa `odoo-test.conf` propia).

## 2. F2 / F3 — Spikes make (probar antes de especificar)

La secuencia correcta resultó ser **entornos primero, contrato después**: los
spikes descubrieron semánticas que habrían roto el spec si se escribía antes:

| Hallazgo | Consecuencia en el contrato |
|---|---|
| `-i` sobre módulo instalado = no-op | `test-clean` debe forzar "desde cero" explícito |
| Drift de schema en build gestionado (columna fantasma NOT NULL) | el clean real (DB nueva/rebuild) es el antídoto |
| Postgres compartido saturado | retry con fail-hard + `db_maxconn` bajo + `workers 0` |
| `Form` requiere `web` | `depends` del ejemplo incluye `web` |
| Odoo 19: `res.groups.category_id`→`privilege_id` | XML de seguridad actualizado |
| Odoo 19: `<tree>`→`<list>` | vistas actualizadas |
| Bug `score=0` falsy en el constraint | atrapado por el propio test (TDD real) |

## 3. F1 — Ciclo CDAD de la especialización

- **Spec** (`docs/specs/cdad-003-odoo/spec.md`): P1-P6, I1-I3, A1-A4. Aprobado
  por el orquestador/HITL designado (Pablo delegó la decisión).
- **RED**: `tests/validate-odoo-specialization.sh` — 63 asserts iniciales,
  52 en rojo (agentes/skills inexistentes).
- **GREEN**: 5 variantes de agente + 3 skills de rol + `odoo-make-env` +
  activación por stack + install.sh.
- **Review adversarial** (modelo distinto): 6 bloqueantes (3 Critical + 3
Required) + 9 opcionales. Los más valiosos: filtración del nombre de infra
privada y de su ruta de producción en archivos públicos (Critical — regla de
privacidad), bash allowlist `"*": allow`
  en 4 de 5 variantes (Critical), install.sh no instalaba los skills nuevos
  (Required), P4 enterrado en references/ (Required).
- **Fixes**: sanitización completa (grep = 0), allowlist unificada en las 5
  variantes, sección stack en SKILL.md principal, cita real de la metodología
  Odoo, SKILLS en install.sh, path-guard Claude Code con roles Odoo,
  validate-subagents consciente de 11 agentes.
- **Corrección del oráculo**: el test-writer había hecho un check demasiado
  amplio (denegaba tokens como `go `/`python` en TODO el archivo, no solo el
  frontmatter), lo que obligaba a deformar la prosa. Se acotó a la sección
  `bash:` del frontmatter, con prueba negativa. Lección de calidad: un oráculo
  demasiado amplio degrada la implementación.
- **Resultado**: 121/121 asserts PASS. Commit `9b5231a`.

## 4. A1 — Ciclo completo sobre el módulo de ejemplo (odoo.sh)

Postcondición nueva (`action_submit`: draft→submitted) validada de punta a punta:
1. RED: `make test-one` → `AttributeError: 'idea.log' object has no attribute
   'action_submit'` (RED válido por método inexistente).
2. GREEN: `action_submit()` implementado → `make test-one` 1/1 verde.
3. Suite: `make test` 8/8 verde.
4. Gate: `make test-clean` 8/8 verde + demo data cargada.

## 5. Incidente post-merge: esquema de permisos inválido (OpenCode no arrancaba)

**Síntoma:** OpenCode se caía al iniciar con los agentes variante instalados;
Pablo tuvo que eliminar los permisos granulares de las copias instaladas para
poder levantarlo.

**Causa raíz:** el implementer reescribió los permisos con un esquema de
LISTAS (`deny: [...]` / `allow: [...]`) que no es el esquema de OpenCode. El
esquema válido (doc oficial + agentes genéricos en producción) es: cada clave
(`read`/`edit`/`write`/`bash`/`grep`/...) acepta un **shorthand**
(`allow|ask|deny`) o un **objeto glob → acción string**. Las listas son
inválidas y tumban el startup.

**Por qué no lo atrapó nuestro proceso:** el oráculo es grep-based — valida
patrones de contenido, no validez de esquema YAML contra el runtime. La
verificación end-to-end real (boot de OpenCode con los agentes instalados) no
se ejecutó antes del merge. **Lección: un artefacto de configuración de agente
debe validarse arrancando el runtime, no solo con checks de texto.** El
validador YAML con asserts de esquema se agregó como verificación post-fix.

**Fix:** los 5 frontmatter reescritos al esquema objeto-glob (idéntico
estructura a los agentes genéricos que funcionan), verificados con parseo YAML
+ asserts de acciones válidas + oráculo 121/121 (con su regex de comodín
corregida: solo `"*": allow` puro dispara, no `"make *": allow`).
**Confirmado por el usuario**: OpenCode arranca correctamente con los agentes
reinstalados (commit `8ace12e`).

## 6. Estado por criterio de aceptación

| Criterio | Estado | Evidencia |
|---|---|---|
| A1 ciclo completo | ✅ | RED→GREEN→clean verde en odoo.sh (§4) |
| A2 dos entornos | ✅ | odoo.sh 8/8; staging privado: `test-clean` verde 7/7 en DB fresca (05:52) + gates estáticos ✅. Runs warm posteriores flaky por saturación de postgres (escalado). |
| A3 sanitización | ✅ | grep de patrones sensibles = 0 en lo publicable |
| A4 reviewer≠implementer | ✅ | qwen3.7-plus vs deepseek-v4-flash |

## 7. Pendientes (escalados a Pablo)

1. **Postgres del servidor privado saturado** (Tier 1): subir `max_connections`
   o pgbouncer — causa flakiness en los runs warm de F3. Se descubrió además
   que procesos `odoo-bin` huérfanos retienen conexiones y son una causa
   concreta: la mitigación operativa es matarlos antes de reintentar.
   Propuesta de producto: presupuesto de conexiones por tenant.
2. **Push al repo GitHub de odoo.sh** (flujo real push→rebuild): agregar
   colaborador (cuenta de trabajo) o push del owner.
3. **CI completa estilo OCA** (fuera de alcance de este ciclo, futuro).
