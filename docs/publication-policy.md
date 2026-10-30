# Política de publicación del repositorio

Decisión del usuario: 2026-10-29. Publicar los cambios acumulados mediante
**un commit squash**, conservando el historial detallado local. Esta decisión
rige las próximas publicaciones de este proyecto.

- Cada publicación parte del `main` remoto actualizado y crea un único commit
  descendiente suyo con el delta aprobado. No publica los commits intermedios
  locales ni elimina historia ya publicada.
- Conservar `main` local y su historial de trabajo. Preparar la publicación en
  una rama separada; no usar reset/rebase destructivo ni force push.
- Antes del push, actualizar la referencia remota, comprobar divergencias y
  detenerse ante conflictos reales: no sustituir silenciosamente cambios remotos.
- Revisar todo el árbol trackeado candidato, no solamente el último diff, para
  excluir secretos, datos privados y rutas locales identificables. Los controles
  automáticos no sustituyen esta revisión. Un hallazgo sensible bloquea el push
  hasta autorizar y verificar su saneamiento o una exclusión explícita.
- Excluir archivos ignorados y untracked, incluidos paquetes, recibos y borradores
  locales. Demostrar la equivalencia del árbol aprobado o documentar exclusiones.
- Publicar únicamente fast-forward a `main`, verificar el hash con `ls-remote`
  y demostrar que hay exactamente un commit desde la base remota capturada.

Después de publicar, las siguientes entregas vuelven a partir del nuevo `main`
remoto y condensan únicamente el delta nuevo. Squash no borra historia previa.

## Intento de publicación del 2026-10-29: bloqueado antes del push

Fuente inspeccionada: `26f9121`; remoto actualizado: `5dc2021`.
La comparación `origin/main...main` arroja 4 commits exclusivos remotos y
299 exclusivos locales. El sondeo read-only de integración detecta conflictos
de contenido en `docs/.cdad-state.json`, `docs/activeContext.md`,
`docs/progress.md`, `skills/cdad-cycle/scripts/cdad_continuity.py` y
`skills/cdad-cycle/scripts/cdad_packet.py`. Requieren decisión de integración;
no se autoriza resolverlos sustituyendo el árbol remoto sin más.

Además, el examen de los 1334 archivos trackeados de la fuente detecta rutas
locales identificables en
`docs/specs/010-000-continuity-relative-root/memory-bank-draft.md`, líneas 14 y
223. No se reproducen sus valores aquí. El escaneo por patrones privados
configurados no detecta coincidencias: ese resultado no cubre estas rutas.

Controles: `tests/validate-odoo-specialization.sh`: 68 PASS / 0 FAIL.
`make validate`: 182 PASS / 1 FAIL en el primer validador, F011
(`scripts/validate-subagents.sh`, perfil activo); no se declara gate verde.
Logs y escaneo detallado conservados localmente en `.cdad/publication/`.

No se creó commit publicable ni se hizo push. No se modificaron la autoridad,
la continuidad ni el paquete preparado de Discovery 010-004. El borrador
untracked `discovery.md` quedó excluido. Para continuar: autorizar alcance de
saneamiento documental e integración de las diferencias remotas y repetir la
verificación del árbol candidato antes de construir/publicar el único commit.

## Continuación autorizada: saneamiento e integración

El usuario autorizó sanear las referencias e integrar preservando ambos trabajos.
La inspección posterior prueba que los conflictos del sondeo basado en historia
divergente no requieren resolver código: el árbol completo del remoto `5dc2021`
es **idéntico** al del ancestro local `6de69b6dd09cbeef2cc10ce50f72bd0fd59545f6`
(`b80b643130ae02b93ce96df66af7759d15a03cb0`), que pertenece a la historia de
`main`. `git diff --exit-code` entre ambos da rc=0 y `merge-base --is-ancestor`
del ancestro local a `main` da rc=0. El remoto ya publica un squash de trabajo
local anterior: comparar historias mediante merge textual produjo falsos
conflictos. Usar el árbol local posterior conserva el contenido remoto y añade
su evolución local, sin decisiones nuevas de implementación ni merge de código.

Se anonimizaron las dos rutas identificables del borrador histórico y se marcó
expresamente que sus comandos ya no son transcripciones literales. El original
privado queda fuera del árbol publicado. Los demás candidatos de rutas de HOME
son expresiones regulares, placeholders o ejemplos genéricos; los ejemplos de
otro usuario y del usuario estándar del sandbox no identifican al dueño.

La integración no altera código ni tests respecto de la fuente local aprobada.
La evidencia de suite completa por composición sigue en
`docs/specs/010-000-continuity-relative-root/full-suite-recovery.md`: 1849 passed,
5 skipped; no se convierte en una corrida monolítica ni se oculta el rc=1
original. Las verificaciones nuevas de publicación se conservarán localmente
en `.cdad/publication/`, asociadas al árbol candidato y a sus rc.

### Preflight verificado el 2026-10-30

En worktree separado, con índice y archivos idénticos al árbol saneado
`2dab53222c442032ec20f1c8f955a0b46b804b09`:

- `make staging`: rc=0.
- Instalación y `--check` en raíz aislada existente: ambos rc=0; 402 grupos.
- `make validate` con esa instalación: rc=0; 183/0 y 68/0.
- Sanitización con patrones privados configurados: rc=0; 68/0.
- Escaneo de los 1335 archivos del índice completo por patrones privados,
  direcciones privadas, credenciales reconocibles y HOME identificables:
  cero coincidencias. No es una garantía universal de ausencia de secretos.
- `pytest -q tests/test_010_000_continuity_relative_root.py`: rc=0,
  5 passed. Código y tests idénticos a la fuente con suite completa compuesta
  citada arriba; no se realizó otra corrida monolítica ni se editaron tests.
- Índice vs fuente saneada y archivos vs índice: rc=0, sin exclusiones de
  archivos trackeados. Ignorados y untracked no entran en el commit.

Se conservan los intentos fallidos: la primera instalación aislada devolvió
rc=1 porque su directorio destino aún no existía; su `--check` también rc=1
y el `make validate` posterior rc=2/F011. La segunda ejecución usó una raíz
aislada existente y produjo los resultados anteriores, sin modificar HOME
global, tests o código. Los logs están fuera del árbol publicado. Esta nota
es la única modificación documental posterior a aquel árbol preflight;
la equivalencia final y el hash publicado se registran localmente tras el push.
