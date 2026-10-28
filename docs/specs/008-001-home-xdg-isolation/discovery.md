# Discovery — 008-001-home-xdg-isolation (epic 008)

**Estado:** hipótesis plausible, causa de los fallos todavía no demostrada. Contrato y política: SHA-256 coincidentes con el paquete. No existe aquí una spec aprobada de la feature.

## Superficie verificada

- **Sin aislamiento transversal:** `tests/conftest.py:11-16` únicamente modifica `sys.path`; no fija HOME, XDG ni temporales.
- **Adaptador:** `tests/test_005_009_t2_opencode_adapter.py:1130-1153` hereda el entorno completo; redirige HOME/XDG_CONFIG_HOME solamente cuando recibe `user_home`. La DB del fixture sí es descartable (`:1097-1109`). Por tanto, hay exposición a configuración del usuario, no evidencia de acceso efectivo a su DB.
- **Selección/servicio/espera:** `tests/test_006_001_t1_selection.py:373-388` copia `os.environ`; `test_006_001_t1b_service_mode.py:289-295` añade únicamente XDG_STATE_HOME. `test_006_001_t2_wait_recovery.py:584-592` conserva esa vía y agrega trazado SQLite mediante PYTHONPATH. El recorrido integrado fija DATA/STATE/CACHE, pero no CONFIG/HOME (`test_006_001_t3_integration.py:254-265`).
- **Lecturas del producto:** `skills/cdad-cycle/scripts/cdad_delegate.py:123-151` resuelve configuración y credenciales por XDG_CONFIG_HOME → CDAD_INSTALL_ROOT → HOME; `cdad_dispatch.py:200-204` reutiliza esa ubicación para runtimes. `cdad_delegate_opencode.py:1592-1613` busca el registro del servicio por XDG_STATE_HOME/HOME; la DB es explícita en `sessions_db` (`:2625-2629`), no un descubrimiento automático del HOME.
- **Agentes derivados:** `cdad_packet.py:4071-4084` prioriza variable explícita, activación y origen global. Este último se calcula **al importar** con `Path.home()` (`:140`): una fixture por test no corrige valores ya capturados durante colección.
- **Excepciones legítimas:** aceptación contra store real requiere variables explícitas y se omite sin ellas (`tests/test_005_002_t4_acceptance.py:993-1014,1049-1066`). No debe activarse accidentalmente. Los servidores simulados usan loopback/puerto dinámico; la reserva de puerto cerrado conserva una carrera independiente (`test_006_001_t1_selection.py:236-237,272-275`).

## Diseño propuesto y secuencia

Preferir **una fixture autouse por test**, frente a parches por familia: directorio propio con HOME, XDG_CONFIG/DATA/STATE/CACHE/RUNTIME y TMPDIR/TMP/TEMP; restauración del entorno y caché de `tempfile`, limpieza después de cerrar procesos/servidores. Propagar por herencia, conservando overrides locales legítimos. Sanear overrides CDAD heredados, sin borrar los que construye cada fixture.

Primero resolver capturas durante colección; después introducir aislamiento y adaptar fixtures que esperan precedencias/configuración instalada. Mantener archivos reales sintéticos, DB SQLite y servicio HTTP de fixture: **no sustituir esos caminos por mocks ni debilitar aserciones**. Ejecutar familias afectadas antes del gate completo. Las tres corridas completas corresponden a validación posterior coordinada por el closer, no a este discovery.

## Postcondiciones candidatas

1. Cada test y su subprocess observan raíces HOME/XDG/temporales propias, distintas entre tests.
2. Configuración y agentes sintéticos se consumen por las precedencias reales; ausencia de configuración permanece observable.
3. Registro de servicio y DB utilizados pertenecen al fixture; ningún store externo se habilita implícitamente.
4. Canario negativo detecta intentos de lectura/escritura fuera de las raíces permitidas, incluidos subprocess; una comparación de bytes sola **no demuestra ausencia de lecturas**. **VERIFY:** mecanismo de observación disponible.
5. Tras teardown no sobreviven procesos/servidores del fixture ni cambios de entorno/caché temporal.
6. Tres ejecuciones completas consecutivas registran comando, rc y resultados, sin contaminación detectada; cualquier fallo residual se investiga sin atribuirlo automáticamente a HOME.

**Límites:** HOME/XDG no aíslan red, rutas absolutas, servicios vivos ni presión temporal. No se promete suite verde por esta intervención.

**Evidencia operativa:** lecturas mediante `cat`, `rg -n`, `sed -n`, `nl -ba`; comprobaciones `sha256sum`, `git status --short`, `git diff --stat`, `git rev-parse --short HEAD`. HEAD `7b30e3a`; modificación preexistente observada: `docs/.cdad-state.json`. Archivos modificados por este rol: **ninguno**. Tests ejecutados: ninguno. Commit creado: ninguno.
