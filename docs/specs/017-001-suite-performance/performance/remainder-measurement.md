# Medición adicional del resto — muestra de los seis archivos más caros (017-001)

Decisión del dueño (2026-11-07): medir el resto antes de fijar el objetivo de
reducción. Esta es la focal adicional que exige spec §4.4.

## Qué se midió

- Selección: los seis archivos de mayor `S_file` de la base (57 nodeids,
  1120 s en la base; 22.5 % del suite).
- Instrumentación: marcas `external.*` alrededor de cada llamada a
  `subprocess` en esos archivos (`external.install` = `bash install.sh`;
  `external.cli` = `bash scripts/validate-subagents.sh`;
  `external.python` = `[sys.executable, <cli>, …]`). Sin cambiar comandos,
  argumentos, entornos, aserciones ni orden.
- Corrida: `close --nodeids` sobre los 57 nodeids, revision `7ac59021`,
  arbol limpio, canary delta 0.
- Intento: `evidence/017-001-t4b/attempt-20261107T215757007671Z-3143831-4d1a67a0`.

## Resultado

| Archivo | Fases (s) | Externo atribuido (s) | % externo | In-process (s) |
|---|---:|---:|---:|---:|
| `test_009_001_installer_agent_overlay.py` | 212.7 | 207.9 | 98 % | 4.8 |
| `test_010_002_documentary_role_properties.py` | 192.3 | 12.6 | 7 % | 179.6 |
| `test_install_ownership.py` | 165.1 | 159.0 | 96 % | 6.0 |
| `test_role_packet_render.py` | 115.9 | 115.6 | 100 % | 0.3 |
| `test_install_review5_regressions.py` | 98.1 | 87.5 | 89 % | 10.7 |
| `test_012_installer_ignore_pycache.py` | 53.1 | 43.9 | 83 % | 9.2 |
| **Total** | **837.2** | **626.6** | **75 %** | **210.6** |

Eventos: 76 ejecuciones de `install.sh` (493.5 s), 301 procesos CLI
(118.2 s), 2 ejecuciones del validador (14.1 s). 57 tests, 0 fallos.

## Lectura

1. **En la muestra más cara, tres cuartas partes del tiempo es proceso
   externo**: instaladores y CLI reales. No es cómputo in-process.
2. El caso dominante son las **76 ejecuciones de `install.sh`** (493.5 s,
   ~6.5 s cada una) y las **301 invocaciones de la CLI** en un solo archivo
   (118.2 s).
3. `test_010_002_documentary_role_properties.py` es la excepción: 93 % de su
   tiempo es in-process (propiedades deterministas). Ese costo no es
   preparación duplicada y no se reduce sin cambiar lo que el test verifica.
4. Que el tiempo sea externo **no implica que sea reducible**: en varios de
   esos tests la instalación o la invocación de la CLI **es la acción bajo
   prueba** (ownership, overlay, pycache, determinismo del render). Solo es
   preparación compartible donde la ejecución externa es *setup* para otra
   aserción.

## Qué habilita y qué no

- Habilita una decisión de objetivo basada en costo observado: existe un
  candidato concreto y medido (instaladores y CLI repetidos en la muestra).
- No autoriza a recortar tests ni a cachear a ciegas: cada caché debe
  declarar qué transición deja de ejecutarse y qué promesa seguiría
  verificada. Eso es trabajo de T5 con su propio contraste antes/después.
- No dice nada todavía sobre el 78 % restante del suite (los otros ~4.1 ks):
  la muestra es representativa de los archivos más caros, no del total.

## Límites

- La muestra cubre 22.5 % del suite; no se extrapola a la suite completa.
- La corrida convivió con actividad del host; las paredes de la base y de esta
  focal no son estrictamente comparables (837 s vs 1120 s en la base para los
  mismos archivos).
- La sonda de neutralidad usó invocaciones rápidas; la neutralidad de las
  marcas se verificó con los 57 tests reales (0 fallos) y con eventos
  `termination: ok` en las corridas de sonda.
