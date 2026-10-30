## Test audit — 010-000-continuity-relative-root

**Contrato:** `docs/specs/010-000-continuity-relative-root/spec.md`  
**Validación:** el SHA-256 del archivo coincide con el contrato aprobado del paquete (`623b15e1…f01737e2`).  
**Alcance inspeccionado:** únicamente el spec y los cuatro archivos de tests indicados. No leí implementación, no ejecuté tests y no edité archivos. La mención del spec a la instalación **sí** tiene precedente localizable: `tests/test_role_packet_consumers.py:31–57,70–96,110–153` instala bajo un directorio temporal y prueba un consumidor sin wrapper del checkout.

### Postcondiciones y brecha mínima

| PC | Evidencia existente (`archivo:línea`) | Conducta existente | Brecha mínima |
|---|---|---|---|
| 01 | `test_007_003_continuity_at_edges.py:1191–1399`; `test_008_004_packet_enforcement.py:304–321,471–488` | Ejercitan validación de begin/dispatch y paquetes no verificables, no equivalencia entre raíces relativas y absolutas para `begin` y `checkpoint`. | Un test conductual que cubra ambas operaciones con raíz relativa y su equivalente absoluta desde el mismo estado inicial, verificando éxito y efecto lógico. |
| 02 | `test_008_003_lifecycle_decisions.py:350–431,433–511`; `test_008_004_packet_enforcement.py:243–295` | Cubren decisiones de lifecycle y validación de referencias; no comparan resultados de `plan_write`, `verify_published_packet`, `classify_path` y `classify_path_observable` bajo raíces equivalentes. | Un test por promesa observable que compare resultados/clasificación para esas interfaces con entradas idénticas y raíces equivalentes. |
| 03 | `test_007_003_continuity_at_edges.py:1402–1581`; `test_008_004_packet_enforcement.py:493–520,632–689` | Verifican que ciertas operaciones no publiquen efectos ante rechazo/replay; no cubren la garantía de no escritura de `plan_write` para plan, replay y rechazo. | Test que compruebe ausencia de cambios de archivos en esas tres salidas del planificador. |
| 04 | `test_007_003_continuity_at_edges.py:1608–1802,2161–2604`; `test_008_003_lifecycle_decisions.py:742–870` | Cubren continuidad, replay e integridad en escenarios existentes; no comparan bytes canónicos y cadena al cambiar únicamente la expresión de la raíz. | Test que compare cuerpos, referencias, digests, secuencia y enlaces con raíz equivalente, sin incorporar la ruta absoluta. |
| 05 | `test_007_003_continuity_at_edges.py:2161–2604`; `test_008_003_lifecycle_decisions.py:648–870`; `test_008_004_packet_enforcement.py:523–576` | Hay cobertura de replay e idempotencia, pero no de replay/conflicto al cambiar a otra raíz equivalente. | Test de replay equivalente sin efectos nuevos y conflicto equivalente rechazado; conservar las comprobaciones de elegibilidad e identidad exigidas por el contrato. |
| 06 | `test_008_004_packet_enforcement.py:243–376,445–488,592–665`; `test_008_003_lifecycle_decisions.py:350–431` | Cubren paquete alterado, rechazo antes de publicar y restricciones de lifecycle. No relacionan esos controles con la normalización de raíces. | Test que, usando raíz relativa equivalente, conserve rechazos por paquete alterado y falta de autoridad antes de publicar. |
| 07 | `test_007_003_continuity_at_edges.py:2607–3059`; `test_008_004_packet_enforcement.py:243–376,471–488,692–716` | Hay precedentes de rechazo sin efectos y validación de rutas/paquetes, pero no una matriz de las superficies de pertenencia por resolución bajo raíces equivalentes ni testigo exterior intacto. | Test(s) para las superficies enumeradas en PC-07: escapes `..`, absolutas donde no se admiten y symlinks exteriores; verificar ausencia de efectos y testigo sin cambios. Mantener aparte la limitación declarada para `update.references`. |
| 08 | `test_role_packet_consumers.py:31–57,70–96,110–153` | Instala en raíz temporal aislada y prueba paridad de CLI packet para consumidor sin wrapper. No cubre continuidad instalada ni staging `make staging` del contrato. | Test de instalación aislada para ambos CLIs, `begin`/`checkpoint` con raíces equivalentes y rechazo inseguro definido en PC-07, sin wrappers del checkout. |

### Tests intactos y tests necesarios

**Intactos:** los cuatro archivos inspeccionados permanecen sin cambios. No propongo reemplazar ni modificar sus tests: sus escenarios protegen contratos previos distintos y no verifican la nueva equivalencia de raíces.

**Nuevos necesarios:** cobertura de las brechas descritas para PC-01–PC-08. Cada test nuevo debe nombrar los PC que protege y declarar la consecuencia para el usuario; agrupar cuando sea una misma promesa observable, no por cada variante interna. PC-08 debe seguir el precedente de staging temporal sin instalar globalmente.

### Evidencia de inspección

Comandos ejecutados (lectura, no ejecución de tests):

- `python3 …/cdad_packet.py validate-request …` y `render …` con la REQUEST y el execution context indicados: el CLI emitió el bloque canónico completo, coincidente con el paquete recibido.
- `sha256sum docs/specs/010-000-continuity-relative-root/spec.md`: `623b15e14290739f6f7c099183a06348b91bcce02eac4dce37265019f01737e2`.
- `head -100 …/spec.md`, `rg -n '^def test_|^    def test_'` en los cuatro archivos y `rg -n` dirigido a PC e instalación: salida usada para las referencias de la tabla.

**Tests ejecutados:** ninguno. Suite completa: no ejecutada.  
**Archivos modificados:** ninguno. **Commit:** ninguno.  
**Estado:** informe de auditoría para revisión; no constituye aprobación.
