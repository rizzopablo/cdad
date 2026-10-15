# Decisión del dueño: P-1 rutas privadas y R5 (2026-10-02)

Aprobado por Pablo en sesión, sobre las recomendaciones del orquestador.

1. **P-1.** Se agrega a la política del proyecto el campo opcional
   `path_policy.private_paths`. Sirve para archivos que ningún rol necesita
   leer; el caso de este repo es `tests/.sensitive-patterns.local`.
   - Es la única barrera nueva, y es obvia y no restrictiva.
   - No reemplaza a la instrucción del rol ni a la auditoría del orquestador.
   - Criterio general del dueño: los límites mecánicos se aplican solo cuando
     son obvios. No se dedica tiempo a cerrar todas las grietas, porque
     restringir de más bloquea trabajo legítimo.
   - Las limitaciones residuales se declaran.
2. **R5.** El costo del guard de Claude Code, unos 252 ms por llamada con
   política v2 contra 32 ms en legacy (N=20, muestra del architect
   `discovery-001`), **se acepta** sin caché.

3. **Revisión de política aceptada:** `docs/cdad-policy.json` con
   `private_paths: ["tests/.sensitive-patterns.local"]`, sha256
   `9ffb7d16464416b18fa14ec7d20b7492d0ac9b92544293c62719c09e86db2678`.
