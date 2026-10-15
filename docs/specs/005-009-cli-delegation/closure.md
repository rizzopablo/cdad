# Cierre — 005-009-cli-delegation

**Feature:** `005-009-cli-delegation` · **Epic:** `epic-005-real-operation`
**Fecha:** 2026-10-11 · **Estado:** cerrada (etapa 5 cumplida)
**Aprobación:** orquestador OpenCode bajo la delegación HITL de epic-005
(`docs/epics/epic-005-real-operation/execution.md`).

## 1. Resultado

Un agente autorizado puede **encargar un paquete CDAD ya preparado a una sesión de rol
en otro CLI** y recibir su entrega por el flujo CDAD existente, con proyecto, rol,
configuración, entrega y re-entry verificables. La pieza nueva es una **interfaz común
de delegación con un adaptador por destino** (el primero, OpenCode), que **reutiliza**
`prepare`, el registro I8, el ledger, los recibos y la reconciliación, y **no crea otro
state del ciclo**.

- **PD-1/INV-2:** interfaz agnóstica del destino; el adaptador se resuelve por
  **convención de módulo** (`cdad_delegate_<id>.py`), así que **agregar un destino no
  edita la interfaz**.
- **PD-2/INV-1/INV-3:** el `PACKET.md` se transporta **byte-idéntico**; el intento se
  registra en el **mismo ledger** con la forma cerrada de I8 tomando
  `execution_id`/`packet_id`/`role`/`substage` **del paquete publicado**; el orquestador
  sigue siendo el **único escritor** del state.
- **PD-3/PD-8:** el proyecto es explícito (`--project-root`) e **independiente del
  directorio del coordinador**; la configuración de ejecución llega por `--exec-config`
  y **no hay valores de este VPS** en el producto.
- **PD-4/INV-2:** se **verifica el modo de carga soportado** contra los agentes derivados
  publicados; una entry no soportada **falla cerrado** con diagnóstico que nombra agente
  y modo, **sin despachar sesión y sin fallback a un agente genérico**.
- **PD-5/PD-6/INV-5/INV-6:** la espera es sobre una **señal durable** (no sobre el `rc`
  del cliente), acotada y sin sondeo sin límite; la terminación se clasifica desde
  **hechos materiales** (`completed`/`blocked`/`transport-error`/`timeout`/`cancelled`);
  **`rc=0` no aprueba un gate** (el recibo queda `pending`); un `timeout` **no** prueba
  ausencia de cambios y la reconciliación distingue el intento en vuelo
  (`dispatched-unknown`) del éxito, sin autorizar repetición.
- **PD-7:** el worker recibe **solo** el paquete y sus insumos declarados, en **una sola
  invocación**, y devuelve su texto final y evidencia durable.
- **PD-9/INV-1/INV-4:** la prohibición heredada de spawn se **conserva** donde el runtime
  no soporta el spawn nativo y se **distingue** de la delegación externa autorizada; una
  delegación no amplía autoridad ni permite al worker escribir el state.
- **PD-10:** el recorrido real Claude → OpenCode → recepción CDAD es el **gate de
  integración**, no simulado (ver §7).

No se construyó un scheduler, ni instalación automática de CLI, ni un sandbox; no se
implementaron todos los destinos; la dirección inversa y otros CLI quedan después (INV-9).

## 2. Gate de etapa 5

| Comprobación | Resultado |
|---|---|
| Suite completa (worktree fijo, corrida del orquestador) | **734 passed / 1 skipped** (860.35 s, exit 0); el skip es PD-10 |
| Focales de la feature | 33 passed / 1 skipped (el skip es PD-10, declarado) |
| `make validate` | 141 PASS / 2 FAIL **preexistentes** (F011 y A3); la familia F011 que este diff agravaba **se cerró con el despliegue del dueño** (§9) |
| Review formal | **OK, sin bloqueantes** (ver §6) |
| Memory Bank | borradores del scribe, revisados y aprobados bajo la delegación HITL |

## 3. Decisiones aprobadas (D1–D10, tal como se propusieron)

D1 interfaz común como CLI nuevo con adaptadores por convención de módulo; D2 reutilizar
`prepare`/I8/ledger/`receive`/`reconcile` sin otro state; D3 alimentar I8 con el esquema
cerrado y registrar configurado/observado o `unknown`; D4 vocabulario de terminación con
**entrega ≠ gate**; D5 verificación del modo de carga con **fail-closed** y sin fallback
genérico; D6 espera sobre señal durable, no sobre el `rc`; D7 configuración portable sin
valores del VPS; D8 reconciliación del SPAWN GUARD; D9 el recorrido real como gate de
integración; D10 frontera explícita.

## 4. Defectos detectados durante el ciclo (y cómo se resolvieron)

El valor del ciclo estuvo, más que en el verde, en los tres defectos que aparecieron:

1. **El adaptador resolvía el árbol de la skill desde el directorio del coordinador**
   (`os.environ["PWD"]`). Detectado por el orquestador al verificar el primer GREEN de T2
   (el rol lo había reportado como nota, no como bloqueante). Riesgo real: en una
   delegación real podía resolver **otra versión** del producto. Se corrigió en dos pasos:
   la fixture pasó a stagear el **árbol completo** de la skill (causa próxima) y el
   adaptador ahora resuelve todo **co-ubicado al artefacto**, fallando cerrado si el árbol
   está incompleto (`d413c0c`).
2. **Una aserción del test nuevo era insatisfacible:** el mensaje del `assertIsNone`
   evaluaba `hit.group(0)` dentro de un f-string **antes** de la aserción, así que con el
   arreglo presente reventaba con `AttributeError` y sin él fallaba por `AssertionError`.
   El implementer **se detuvo y lo reportó** en vez de forzar el verde; el test-writer la
   corrigió con formateo perezoso **sin debilitar la garantía** (`8f6b812`).
3. **Carrera de tiempos preexistente** (medida: ~10-11 de 40 invocaciones, también en la
   base): el adaptador agotaba su presupuesto interno y la **interfaz** lo mataba por
   exceder la cota, clasificando `timeout` en vez de `transport-error`. Se corrigió **en el
   producto** —un fallo de transporte observable se clasifica desde el hecho material sin
   agotar el presupuesto, y el adaptador responde siempre dentro de la cota que recibe—,
   **no** subiendo la cota del fixture (`15c8dab`).

## 5. Evidencia

**Commits de la feature** (base `9f11b4f`):

| Commit | Unidad |
|---|---|
| `1d5c946` | T1 GREEN — interfaz común + wrapper + referencia |
| `896637b` | T3 GREEN — distinción de la delegación externa (fuentes + generados) |
| `b483c05` | T2 GREEN — adaptador OpenCode |
| `6fc958d`, `8f6b812` | review-fix del test (fixture completa + aserción satisfacible) |
| `d413c0c`, `15c8dab` | review-fix del producto (sin cwd; dentro de la cota) |
| `29c8480` | T4 — aceptación (entrega ≠ gate; interrupción/reconciliación) |

**Suite completa** (worktree fijo al commit de cierre, corrida del orquestador):
**734 passed / 1 skipped** en `860.35 s` (exit 0); el único skip es PD-10, declarado. El reviewer
corrió la misma suite en el árbol con idéntico resultado (935 s). Registro:
`/tmp/opencode/close-suite-005-009.log`. Nota de entorno: el worktree necesitó `make staging`
**dentro** del worktree antes de la suite (`build/` está gitignoreado).

**Recorrido del producto instalado:** la aceptación de T4 ejercita el adaptador con un
**binario falso** (frontera del proceso) y la reconciliación contra el CLI real; el
recorrido con un **runtime real** es el gate de §7.

## 6. Review

Una sola review formal (`review.md`), read-only, con **modelo de familia distinta** a la
del implementer. **Veredicto: OK, sin bloqueantes.** Verificó por sí misma: suite completa
734/1 skip; `make validate` con 2 FAIL de familias **preexistentes** (comprobadas en un
worktree sobre la base); paridad de los **22 agentes generados** byte-idéntica a su
regeneración; estabilidad del focal de T2 en 5 corridas (la flakiness quedó extinguida);
RED genuino confirmado en los commits de RED; tests **no debilitados** entre RED y HEAD;
portabilidad limpia y sin resolución desde el cwd del coordinador. **Dictamen:** los dos
review-fix de T2 son correctos y **no enmascaran** el defecto.

**Opcionales** (no prolongan el ciclo): cota de espera ausente → invocación sin cota
(contra PD-5); falso positivo del barrido A3 en la prosa del fixture; presupuesto nulo si
la cota es menor o igual a la reserva; la referencia prohíbe «polling loop» mientras el
sondeo es acotado a 50 ms; el adaptador no valida el id de paquete antes de componer rutas
(la interfaz sí). **Abstenciones:** PD-10 (recorrido real, sin evidencia por diseño),
VERIFY-3 (entry soportada contra la versión vigente) y la lectura del archivo de patrones
privados.

## 7. VERIFY abiertos y aceptación conjunta (del dueño)

1. **PD-10 / recorrido real:** una sesión de **Claude coordinador** despachando a un
   **worker OpenCode** real sobre la instalación elegida, con su re-entry registrado. Es
   el gate de integración y **no** se simula.
2. **VERIFY-3:** confirmar la entry soportada (`mode: all`) contra la versión de OpenCode
   vigente en la instalación elegida.
3. **Aceptación conjunta (plan §5):** una sesión nueva inicia el consumidor Perl/Webmin
   con una instrucción breve y realiza la primera delegación útil. Aporta la **R2
   pendiente de 005-006** y la aceptación de interoperabilidad.

## 8. Deuda

- Los cinco opcionales de la review (arriba), ponderados por efecto real.
- `install.sh --check` sigue siendo sensible a los `__pycache__` que Python escribe junto
  al CLI instalado (señal del verificador, no requisito del consumidor).
- La estabilidad medida del focal de T2 depende de la carga del host; la reserva de 1 s
  cubre con margen el arranque y los subprocesos reutilizados, no es garantía ilimitada.
- El paquete de CDAD no inyecta fuentes de dominio por encargo (VERIFy 5 de 005-008).

## 9. Despliegue de la versión sucesora (ejecutado por instrucción del dueño)

Por instrucción directa del dueño («si, despliega») se desplegó la sucesora, que incluye
005-008 y 005-009: commit `6f4d5db`, perfil `basic`, en las tres bases, con respaldo
previo en `archive/20261011-opencode-agents-pre-005-009`. Verificado: `version.txt` y
`source_version` del manifiesto iguales al commit; 343 archivos propios y **0 conflictos**;
11/11 agentes presentes; los CLI de delegación y la referencia instalados. El único FAIL de
`install.sh --check` es la deuda conocida de `__pycache__`. La familia **F011** que la
review atribuía a este diff **quedó cerrada** por el despliegue. Los derivados del proyecto
se republicaron con el primer `prepare` legítimo y `cdad-version-check.py` da **COHERENT**.

## 10. Próxima unidad del epic

Retomar **005-002-session-context-meter** (pausada, discovery intacto), luego
**005-003**, **005-007** y **005-004**, según el plan vigente. El recorrido real de §7 y
la aceptación conjunta del consumidor siguen siendo del dueño.
