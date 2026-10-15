# Decisión del dueño — política de límites de este repo (C1)

**Fecha:** 2026-10-01 · **Dueño:** Pablo (respuesta en la sesión del orquestador).

El dueño aprobó materializar tal cual la propuesta de `prepare --propose-policy`
(CLI en `28324af`) como `docs/cdad-policy.json`. Coincide con C1:

- implementación: `agents`, `skills`, `scripts`, `sources`, `build` y `install.sh`;
- tests: `tests`;
- documentación: `docs`;
- sin raíces temporales.

**sha256 de la política aceptada:** `f3474f36ef68122480488fe0c5bf2a852263f51b7067b760dfd3783f6a0ec216`

El orquestador escribió el archivo por delegación explícita del dueño. Ningún
rol la edita (D1, PD-7).

**Instalación para el corte C y T7:** aislada (decisión del dueño, misma
fecha). La versión nueva se instala en un `CDAD_INSTALL_ROOT` propio y este
repo la usa por `CDAD_PACKET_CLI` y agentes de proyecto `.opencode/agents/`.
La instalación global (`~/.claude`, `~/.config/opencode`) no se toca: otros
proyectos usan CDAD en esta máquina.
