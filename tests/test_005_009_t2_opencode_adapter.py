#!/usr/bin/env python3
"""005-009 T2 RED — Adaptador del destino OpenCode (PD-4, PD-5, PD-6, PD-7).

Contract: docs/specs/005-009-cli-delegation/spec.md (PD-4, PD-5, PD-6, PD-7;
INV-4..INV-6) + plan.md T2 (skills/cdad-cycle/scripts/cdad_delegate_opencode.py
+ tests/test_005_009_t2_opencode_adapter.py). T2 depende de la interfaz común
de T1 (GREEN: 56770e0), reutilizada aquí por la superficie observable fijada
en tests/test_005_009_t1_interface.py.

Superficie observable bajo prueba (proyecto sintético en tempdir, destino
de prueba y binario falso: NINGUNA lectura de implementación, ningún runtime
vivo):

    python3 <cdad_delegate.py> --project-root <raíz> --packet <packet-id> \
        --destination opencode --exec-config <config.json>

DECISIONES DE ORÁCULO (declaradas para que el implementer las satisfaga;
nada fija funciones internas ni plumbing: el BINARIO FALSO es la frontera
del proceso):

1. DESTINO e INVOCACIÓN: el id de destino es `opencode`; el adaptador se
   resuelve por convención de módulo como `cdad_delegate_opencode.py`
   COLOCADO junto a `cdad_delegate.py` (misma convención que T1). La
   configuración de ejecución llega por `--exec-config`; llegando al
   ADAPTADOR por la convención que la interfaz ya usa para el registro I8
   (el cableado interno adaptador↔interfaz no es observable y no se fija).
   Los campos del archivo que este fichero usa (la tolerancia a claves
   desconocidas queda a la interfaz/adaptador):
     {"runtime": <texto>,         # registrado en I8 (ya cubierto por T1)
      "binary": <ruta>,           # EL binario del CLI destino a invocar
      "binary_version": <texto>,  # versión declarada por la ejecución
      "model": <texto>,           # model_configured en I8 (ya cubierto)
      "logs_dir": <ruta>,
      "sessions_db": <ruta>,      # la SEÑAL DURABLE (base de sesiones)
      "wait": {"timeout_seconds": <num>}}  # espera ACOTADA
   `sessions_db` es la superficie de la SEÑAL DURABLE sobre la que el
   adaptador espera (PD-5: base de sesiones, NO el rc del cliente): en una
   instalación real apunta a la base de sesiones del runtime; el fixture la
   apunta a un fichero del tempdir (punto 2). `binary_version` y el binario
   SE TABULAN desde la config de ejecución — nada del binario/versionado es
   hardcodeado del producto (PD-8: la red no aporta valores de host). La
   espera es ACOTADA por `wait.timeout_seconds` (sin sondeo en bucle sin
   límite y sin callback prometido: no existe).

2. BINARIO FALSO (el fixture lo ESCRIBE como fichero ejecutable; el
   adaptador lo ve por `exec-config.binary` y lo invoca como proceso; su
   protocolo está comentado EN SU fuente, plantilla FAKE_BINARY_SOURCE):
   se ubica en `<fake>/bin/opencode-fake` y todo su estado de fixture vive
   junto a su propia ruta (`<fake>` = directorio bisabuelo del binario):
     - `<fake>/variant`: variante (escrita por el test: succeeded|failed|
       interrupted|no-idle|unknown-schema|not-sqlite|transport-error) que
       gobierna el comportamiento (punto 3);
     - `<fake>/calls.jsonl`: registro append de CADA invocación: argv
       (rutas existentes como nombres de base; demás tokens VERBATIM),
       cwd, pwd (VERBATIM de su entorno), agente derivado hallado en
       <PWD>/.opencode/agents (agent_found_in_project), env keys con
       PACKET/CDAD/DELIVER, stdin
       visto, transporte/paquete (sha256, bytes), rc del cliente;
     - `<fake>/sent-packet.md`: copia de los bytes recibidos como paquete
       (transporte comparado byte a byte con PACKET.md publicado);
     - el STORE SQLite del fixture: LA SEÑAL DURABLE (= campo
       `sessions_db` de la config, ruta `<fake>/sessions.db`): base
       SQLite REAL CHICA con el esquema observado (`session_v2` +
       `session_message`, discovery §3.4 de 005-010) — migrado por T1 de
       005-010 (PD-7): el doble JSON `sessions.json` se reemplaza; la
       fila `session_v2` correlacionada lleva el id recibido en
       `--session`.
   Transporte del paquete al binario: tokens de ARGV que sean ficheros,
   ficheros nombrados en env con PACKET/CDAD/DELIVER, o stdin — el MISMO
   contrato de transporte del stub `testdest` de T1 (la BEGIN-marcación
   `---cdad-packet-json` decides). `--version` apenas imprime la versión
   declarada y NO es despacho (sin paquete).

3. SEÑAL DURABLE y CLASIFICACIÓN (hechos materiales; PD-5/PD-6). El
   adaptador clasifica la terminación desde lo material, jamás del rc del
   cliente. Con el doble migrado, el hecho material es la fila
   `session_v2` CORRELACIONADA por el id de `--session` y su
   `idle_outcome` (PD-5 de 005-010; el nombre de la variante ES el hecho
   durable):
     a) fila con `idle_outcome` `succeeded` + `time_idle` y TEXTO FINAL en
        el ÚLTIMO `session_message` `assistant` → terminación `completed`,
        identidad de sesión desde la fila, entrega durable por el
        `receive` existente (la entrega contiene el TEXTO FINAL; recibo
        `semantic_status:"pending"`, jamás cierra el gate);
     b) fila con `idle_outcome` `failed` → terminación `blocked` con
        diagnóstico accionable no vacío y SIN entrega durable (NUNCA un
        recibo);
     c) fila con `idle_outcome` `interrupted` → terminación `cancelled`,
        sin entrega ni recibo;
     d) invocación del cliente que FALLA EN EL TRANSPORTE antes de ninguna
        fila (rc != 0 con error en stderr, store sin filas) → terminación
        `transport-error`, sin entrega ni recibo (no se retiene una espera
        que la convierta en timeout);
     e) fila SIN idle (`time_idle`/`idle_outcome` NULL) dentro de la
        espera acotada (aunque el cliente haya retornado rc=0 e incluso
        impreso el texto final por stdout) → terminación `timeout`, NO
        `completed`, sin entrega ni recibo: la ausencia de señal NO PRUEBA
        ausencia de efectos y el recibo jamás se fabrica; el intento I8
        del ledger queda intacto (hecho material) para que la
        RECONCILIACIÓN (reconcile / dispatched-unknown, dominio T4) decida
        antes de repetir;
     f) [PD-2 de 005-010] store con esquema desconocido (sin
        `idle_outcome`) o NO SQLite → fallo CERRADO: terminación `blocked`
        con diagnóstico accionable que nombra el esquema/columna, SIN
        entrega ni recibo y SIN esperar de más (el hecho ya conocido no se
        degrada a `timeout`).

4. MODO DE CARGA (unidad INVERTIDA por T2 de 005-010: PD-3 de
   docs/specs/005-010-real-opencode-delegation/spec.md): el modo de la
   entry DEJA de condicionar el despacho — `mode: subagent` (configuración
   vigente de los roles, fuente canónica
   `sources/agents/adapters/opencode.md:14`) YA NO es fallo cerrado. La
   barrera es la IDENTIDAD desde la fila durable: el adaptador exige el
   derivado `cdad-<rol>` publicado (`.opencode/agents/cdad-<rol>.md`,
   publicado por `prepare`, I9) y verifica `session_v2.agent ==
   "cdad-<rol>"`. El fallo cerrado pasa a ser: (a) el derivado NO
   publicado — fallo CERRADO pre-despacho, sin invocar el binario, sin
   sesión, sin recibo —, o (b) la fila durable declarando OTRO agente —
   `blocked` con diagnóstico que nombra AMBOS agentes (el foráneo de la
   fila y el cdad-<rol> esperado), sin entrega, sin recibo y SIN desvío a
   un agente genérico no-Cdad (`general`, `coder`, `bootstrapper`,
   `probe`, `researcher`; la variante `wrong-agent` del binario falso
   escribe la fila con el agente foráneo FOREIGN_ROW_AGENT). El registro
   I8 del intento ES material del flujo (discovery §8 paso 2:
   «antes/junto con el envío») y no es leña de este postcondición. El
   vocabulario de salida es el envelope de T1 {attempt, session,
   termination, delivery_ref, diagnosis} con terminación EN EL
   VOCABULARIO (PD-1): las terminaciones blocked/timeout/cancelled/
   transport-error salen por el ENVELOPE con rc 0 — la causa vive en
   `termination`, no en el rc; así declara la interfaz «entrega» y «sin
   entrega suficiente».

5. PD-7 (contexto acotado): el despacho transporta al worker EXACTAMENTE
   los bytes del PACKET.md publicado (UNA sola invocación porta el paquete;
   sin encadenar sesiones nuevas ni esperar subagentes que el worker no
   creó); la entrega durable contiene el texto final acordado y la
   referencia de entrega es del flujo `receive` (recibo pending).

FIXTURE (reutilización por import, precedentes de la suite): proyecto
sintético (`test_004_002_t2_bootstrap.build_project`); agentes derivados
publicados por `prepare` CON la adopción `CDAD_OPENCODE_AGENTS_DIR` hacia
una copia temporal de `agents/cdad-*.md` (copiada SIN inspección, mismo
precedente que T5 de 004-002); la variante de modo soportado se siembra con
un sed mecánico sobre ESA COPIA temporal (`mode: all` en cdad-test-writer.md
— bytes del fixture, jamás sobre archivos de producto). La interfaz y el
adaptador se STAGEAN copiando el ÁRBOL CANÓNICO COMPLETO de la skill
(= `staged_interface()` de T1 desde la review-fix de T2: scripts + packets +
references + assets + SKILL.md, con paridad de nombres verificada por el
propio fixture), de modo que un adaptador fiel al producto que resuelve
recursos co-ubicados a sí mismo funcione SIN ningún fallback al checkout
del coordinador (PD-3/PD-8). El adaptador por convención viaja en la copia
del producto.

Mapa test → postcondición (mapa ACTUALIZADO por T2 de 005-010; PD-4 se
ejercita en las unidades de modo invertidas; la semilla de modo es distinta
por clase; la cláusula de reconciliación post-interrupción
(dispatched-unknown) pertenece a T4 por plan — T2 deja los hechos
materiales intactos para ella):

  1  TestPd4SubagentEntryDispatches::test_pd4_subagent_entry_no_longer_fails_closed
       PD-3 de 005-010 (positiva invertida: subagent ya NO es fallo cerrado)
  2  TestPd4FailClosedUnpublishedDerived::test_pd4_unpublished_derived_fails_closed_before_dispatch
       PD-3 de 005-010 (fallo cerrado pre-despacho: derivado ausente)
  3  TestPd4FailClosedDurableIdentityMismatch::test_pd4_durable_identity_mismatch_fails_closed_without_delivery
       PD-3 de 005-010 (identidad desde la fila durable; INV-6)
  4  TestPd4LoadModeSupported::test_pd4_supported_mode_dispatches_…        PD-3/005-009 (se conserva; el modo ya no condiciona)
  5  TestPd5::test_pd5_durable_signal_gates_completion_not_client_rc       PD-5
  6  TestPd6::test_pd6_termination_vocabulary_from_material_facts_rc0_no_gate PD-6
  7  TestPd7::test_pd7_bounded_context_single_dispatch_final_text_delivery PD-7
  8  TestAdapterCwdIndependent::test_delegation_completes_durable_…  PD-3, PD-8 (review-fix)

REVIEW-FIX FOCAL (encargo T2, subetapa red): defecto detectado por el
orquestador al verificar el GREEN de T2 — el adaptador del producto resuelve
el árbol de la skill desde el CWD DEL COORDINADOR (os.environ["PWD"], línea
297 del producto) cuando el árbol co-ubicado está incompleto; contradice la
independencia del directorio del coordinador (PD-3) y la portabilidad
(PD-8). Encargo en este fichero de tests: (1) la fixture stagea el árbol
COMPLETO de la skill (staged_interface de T1, punto FIXTURE); (2) test
focal nuevo #6 que fija la independencia del cwd POR COMPORTAMIENTO —
invocando la interfaz + el adaptador DESDE UN CWD AJENO (tempdir que no es
el repo ni el proyecto, con PWD del proceso = ese cwd ajeno como lo dejaría
un shell cd'ed), la delegación completa (terminación `completed` con
entrega durable por receive) sigue funcionando SIN resolver nada desde ese
cwd (el cwd ajeno no recibe escrituras); la comprobación estructural
complementaria es sobre el ARTEFACTO PUBLICADO (no sobre nombres de
funciones internas): el adaptador no resuelve recursos desde el PWD del
coordinador — el árbol debe resolverse co-ubicado a sí mismo. Los tests de
T1 y T2 existentes NO se debilitan.

RED de esta review-fix: con la fixture completa y el adaptador vigente que
resuelve desde PWD, el test focal falla por comportamiento AssertionError
(terminación distinta de completed / escrituras en el cwd ajeno /
resolución desde PWD), no por import/sintaxis.

RED de 005-010 T1 (estado actual de este oráculo): el adaptador del
producto EXISTE desde el GREEN de 005-009, pero lee la señal durable como
JSON (`sessions.json`). Con el doble migrado a SQLite real chico (PD-7 de
005-010), el RED esperado (plan §T1): (i) el lector JSON no encuentra la
señal — las variantes con fila idle fallan (timeout, o la excepción NO
capturada de PD-2) en vez de su terminación declarada; (ii) el argv no
lleva `--session <id>`; (iii) `model_reported`/`session` del registro I8
no salen de la fila durable; (iv) `unknown-schema` no falla cerrado. La
unidad del modo de carga (PD-4 vigente `mode: all`) se CONSERVA: la
inversión es T2 de 005-010. GREEN: lector SQLite ro + correlación +
clasificación + observación (mínimo del implementer).

RED de 005-010 T2 (estado actual de este oráculo tras la INVERSIÓN de la
unidad de modo, plan §T2): (1) `TestPd4SubagentEntryDispatches` falla —
con la entry `subagent` el adaptador vigente (exige `mode: all`) RECHAZA
con `blocked` en vez de despachar a `completed`; (2)
`TestPd4FailClosedDurableIdentityMismatch` falla — con la fila durable
declarando el agente foráneo, el adaptador vigente no verifica identidad
desde la fila y DECLARA ENTREGA (`completed`) en vez de `blocked` con
diagnóstico que nombra ambos agentes; `TestPd4LoadModeSupported` se
conserva verde (el modo `all` sembrado ya no condiciona el despacho bajo
T2). El argv sin `--standalone`/`--auto` se fija en el oráculo T2 nuevo
(tests/test_005_010_t2_load_mode_invocation.py).

RED de 005-010 T2b (PWD del proyecto; corrección del orquestador, hecho
verificado contra OpenCode v2.0.26 REAL): `opencode run` toma el DIRECTORIO
DEL PROYECTO de la variable de entorno PWD, NO del cwd del proceso (cwd=tmp
con PWD=repo -> la sesión queda en el repo y no ve los agentes del proyecto
temporal; PWD=tmp -> correcto). El adaptador vigente HEREDA el PWD del
coordinador. Fidelidad del fixture (PD-7): el binario falso REGISTRA el
valor de PWD de su entorno (campo `pwd` del registro de llamada, VERBATIM;
sin filtrar rutas del fixture más allá de lo necesario) y — como el runtime
real — usa ese PWD como directorio del proyecto: busca el agente derivado
en <PWD>/.opencode/agents/<agente>.md (resultado grabado en
`agent_found_in_project`; el fixture NO falla duro por agente ausente en
PWD — la variante gobierna: un endurecimiento rompería tests vigentes que
hoy pasan y no dependen de este defecto) y escribe la columna
session_v2.directory con ese PWD (ya no con el cwd del proceso). RED: el
test focal nuevo en tests/test_005_010_t2_load_mode_invocation.py
(TestPd4PwdProjectDirectory) delega desde un coordinador con PWD apuntando
a OTRO directorio y exige pwd == project root, directory == project root y
delegación completa — bajo el producto vigente falla con AssertionError
(pwd heredado del coordinador, fila directory ajena). Ningún test previo
lee la columna directory ni el campo pwd: los demás tests no dependen de
este defecto.

HALLAZGO DE FLAKINESS REGISTRADO (medido por el implementer en el GREEN del
review-fix, sin corregir aquí — el arreglo es de PRODUCTO, unidad siguiente
del implementer; este oráculo NO cambia su cota): `TestPd6` (y de rebote
`TestPd7`) fallan de forma INTERMITENTE (~10-11 de 40 invocaciones, también
en el HEAD base) por una carrera de tiempos: el adaptador del producto
espera ~1.8s internos sobre la cota `wait.timeout_seconds` (2.0s del
fixture), y el arranque del subproceso hace que la interfaz lo mate y
clasifique `timeout` en vez de `transport-error`/`completed`. La espera
interna del adaptador consumiendo casi toda la cota es un defecto de
margen del PRODUCTO (no del oráculo): si se decidiera ajustar la cota del
fixture, la propuesta — NO aplicada, a decisión del orquestador — es subir
`TEST_WAIT_TIMEOUT_SECONDS` a un valor con margen real sobre la espera
interna (p.ej. 10) en la(s) variante(s) `transport-error` durante la
unidad de
producto que corrige la espera.

RED de B1 (review-codex-2026-10-11; encargo del orquestador, fichero
tests/test_005_010_b1_last_assistant.py): corrección requerida — el
ÚLTIMO mensaje `assistant` es la ÚNICA fuente del texto final (PD-1);
succeeded SIN texto EN ESE mensaje → blocked (PD-5), aunque un assistant
ANTERIOR tenga texto (texto intermedio 'Voy a analizar...'). Dos
variantes NUEVAS del doble (`b1-last-assistant-reasoning-only` /
`b1-last-assistant-multi-text`; NINGUNA variante previa cambia de
conducta) y el oráculo `durable_last_assistant_text` ALINEADO: toma SOLO
el último assistant (concatenación de sus partes textuales), sin
debilitar las precondiciones vigentes que lo usaban (succeeded /
succeeded-no-text de T1 y reviewfix).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (
    build_project,
    published_packets,
    read_state,
    tree_snapshot,
)
from test_005_009_t1_interface import (
    STATE_FILE_REL,
    DelegateCase,
    dispatch_records,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIR = REPO_ROOT / "skills" / "cdad-cycle" / "scripts"
ADAPTER_PRODUCT = CANONICAL_DIR / "cdad_delegate_opencode.py"

AGENTS_ENV = "CDAD_OPENCODE_AGENTS_DIR"
GENERIC_AGENT_NAMES = ("general", "coder", "bootstrapper", "probe",
                       "researcher")  # agentes no-Cdad del namespace (R-2)
GENERIC_AGENT_RE = re.compile(
    r"(?<!cdad)\b(" + "|".join(GENERIC_AGENT_NAMES) + r")\b")

# T2 de 005-010 (PD-3/INV-6): variante de fila durable con OTRO agente — el
# agente que la FILA declara (distinto del cdad del paquete). Se usa un
# nombre genérico no-Cdad para que la JAMÁS-invocación de un genérico sea
# observable en el argv y la identidad desde la fila sea la ÚNICA barrera.
FOREIGN_ROW_AGENT = "general"

SESSION_ID = "ses-fake-opencode-0001"
FAKE_FINAL_TEXT = (
    "# Entrega del rol (binario opencode falso)\n\n"
    "Texto final acordado por la fixture T2 de 005-009: el adaptador "
    "transporta el paquete íntegro, espera sobre la señal durable, "
    "classifica la terminación desde hechos materiales y persiste la "
    "entrega por receive.\n")
# Texto INTERMEDIO de un assistant ANTERIOR (mensajería del store): la
# entrega debe llevar el TEXTO FINAL del ÚLTIMO assistant, no este decoy
# (PD-1 de 005-010: «el último mensaje assistant»).
DECOY_FINAL_TEXT = (
    "[assistant intermedio descartado] Paso previo del rol: este texto NO "
    "es la entrega final; el adaptador debe tomar el ÚLTIMO assistant del "
    "store (PD-1 de 005-010).")
# B1 (review-codex-2026-10-11, corrección requerida): un texto INTERMEDIO
# de un assistant ANTERIOR no puede sustituir una entrega final ausente.
# PD-1: el texto final es el del ÚLTIMO mensaje `assistant`; PD-5: si ESE
# mensaje no tiene parte textual (`type: text`), succeeded → blocked.
B1_INTERMEDIATE_TEXT = (
    "Voy a analizar el contrato; todavía no tengo el resultado.")
# Parte de razonamiento del ÚLTIMO assistant (variante B1): NO es parte
# textual (no `type: text`); el store del fixture la escribe como la única
# parte de `content` de ese mensaje.
B1_REASONING_TEXT = (
    "Paso de razonamiento intermedio del rol: sigo sin tener la entrega.")
# B1 REGRESIÓN: el ÚLTIMO assistant con VARIAS partes textuales — la
# entrega es la CONCATENACIÓN de las partes de ESE mensaje solamente (sin
# texto de mensajes assistant anteriores).
B1_FINAL_PART1 = "Entrega final del rol — parte 1 del ÚLTIMO assistant."
B1_FINAL_PART2 = "Entrega final del rol — parte 2 del ÚLTIMO assistant."
# El `model` de la FILA DURABLE del store: DIFERENTE de `FAKE_MODEL` (el
# model_configured de la config de ejecución) para que PD-6 de 005-010
# pueda probar POR COMPORTAMIENTO que `model_reported` sale de la fila y
# no de la configuración.
ROW_MODEL = "fixture-durable-row-model"
# Review-fix R2 de 005-010: la fila durable puede traer el modelo
# SERIALIZADO COMO OBJETO JSON (forma reportada por la propia evidencia de
# aceptación de 005-010, pd10-acceptance.md, para el runtime real:
# {"id": ..., "providerID": ...}). La observación I8 del worker debe
# normalizarlo a 'providerID/id' (PD-6: observabilidad útil); si la fila
# trae TEXTO PLANO, se conserva tal cual (ROW_MODEL).
ROW_MODEL_OBJECT_ID = "fixture-model-id"
ROW_MODEL_PROVIDER = "fixture-provider"
ROW_MODEL_OBJECT = json.dumps(
    {"id": ROW_MODEL_OBJECT_ID, "providerID": ROW_MODEL_PROVIDER},
    sort_keys=True)
ROW_MODEL_NORMALIZED = f"{ROW_MODEL_PROVIDER}/{ROW_MODEL_OBJECT_ID}"
# Review-fix R3 de 005-010: un `idle_outcome` NO declarado por el
# vocabulario observado (succeeded|failed|interrupted|NULL, discovery
# §3.4) — el hecho material es ese valor foráneo; la terminación esperada
# es `unknown` (PD-5), nunca `completed` ni recibo fabricado.
UNKNOWN_OUTCOME = "expired"
FAKE_USER_TEXT = (
    "Encargo canónico recibido por el binario opencode falso (fixture "
    "T2 005-009 / T1 005-010).")
# Variantes del binario falso (migrado 005-010 T1): el hecho material es la
# fila `session_v2` del store SQLite (idle_outcome observado:
# succeeded|failed|interrupted|NULL). `no-signal` pasa a `no-idle` (fila sin
# idle); `error` pasa a `transport-error` (rc!=0 sin fila); `completed`,
# `blocked` y `cancelled` pasan a los NOMBRES del hecho durable:
# succeeded/failed/interrupted. Dos variantes NUEVAS de fallo cerrado (PD-2
# de 005-010): `unknown-schema` (falta la columna idle_outcome) y
# `not-sqlite` (el store no es una base SQLite). Review-fix de 005-010
# (R1/R2/R3): tres variantes nuevas (ver FAKE_VARIANTS y la cabecera de
# FAKE_BINARY_SOURCE): `hangs` (R1: invocación que no retorna en la cota →
# timeout, no transport-error), `succeeded-no-text`/`unknown-outcome`
# (R3: ramas de PD-5 sin cobertura previa) y `model-object` (R2: fila con
# `model` objeto JSON → I8 normalizado a 'providerID/id').
FAKE_VARIANTS = ("succeeded", "failed", "interrupted", "no-idle",
                 "unknown-schema", "not-sqlite", "transport-error",
                 "wrong-agent",
                 # Review-fix de 005-010 (R1/R2/R3, decisión del
                 # orquestador): variantes NUEVAS del doble que fijan los
                 # hechos faltantes; NINGUNA cambia el comportamiento de
                 # las variantes previas:
                 "hangs",              # R1: invocación que NO retorna dentro de la cota (R-E)
                 "succeeded-no-text",  # R3: idle 'succeeded' SIN texto final (PD-5)
                 "unknown-outcome",    # R3: idle_outcome NO declarado (PD-5)
                 "model-object",       # R2: fila con `model` serializado como objeto JSON (PD-6)
                 # B1 (review-codex-2026-10-11, corrección requerida):
                 "b1-last-assistant-reasoning-only",  # ÚLTIMO assistant SIN parte text (PD-1/PD-5)
                 "b1-last-assistant-multi-text",      # ÚLTIMO assistant con VARIAS partes textuales (PD-1)
                 )
# terminación esperada por variante (hecho material del fixture).
VARIANT_TERMINATION = {
    "succeeded": "completed",
    "failed": "blocked",
    "interrupted": "cancelled",
    "no-idle": "timeout",
    "unknown-schema": "blocked",
    "not-sqlite": "blocked",
    "transport-error": "transport-error",
    # T2 de 005-010 (PD-3): la fila declara OTRO agente → fallo cerrado
    # (sin entrega), aunque el resto de la fila sea un hecho `succeeded`.
    "wrong-agent": "blocked",
    # Review-fix de 005-010 (R1/R2/R3):
    "hangs": "timeout",              # R1: sin fila, cota vencida, cliente sin terminar
    "succeeded-no-text": "blocked",  # R3: succeeded sin texto final (PD-5)
    "unknown-outcome": "unknown",    # R3: idle_outcome no declarado (PD-5)
    "model-object": "completed",     # R2: como succeeded; la observación es I8 (PD-6)
    # B1 (review-codex-2026-10-11, corrección requerida):
    "b1-last-assistant-reasoning-only": "blocked",  # succeeded sin texto en el ÚLTIMO assistant (PD-5)
    "b1-last-assistant-multi-text": "completed",    # succeeded + varias partes textuales (PD-1)
}
NON_COMPLETED_VARIANTS = ("no-idle", "failed", "interrupted",
                          "unknown-schema", "not-sqlite", "transport-error")
# Cota del fixture: 5s (antes 2s). 008-001 PC-8: el adaptador no despacha sin
# presupuesto útil y con 2s la preparación (~0.65-0.8s medidos) agota su parte;
# la cota es INSTRUMENTAL en los tests que la heredan (los que miden tiempo
# escalan con esta constante).
TEST_WAIT_TIMEOUT_SECONDS = 5  # espera acotada del fixture
FAKE_RUNTIME = "opencode"
FAKE_MODEL = "fixture-opencode-model"
FAKE_BINARY_VERSION = "opencode-fake 1.0.0"

# Review-fix T2 (defecto del orquestador): el adaptador vigente resuelve el
# árbol de la skill desde el PWD del coordinador (os.environ["PWD"], línea
# 297). Estructural (artefacto publicado, no nombres internos): el adaptador
# NO debe leer el PWD del coordinador como fuente de recursos — el árbol
# debe resolverse co-ubicado a sí mismo (PD-3/PD-8).
PWD_COORDINATOR_RESOLUTION_RE = re.compile(
    r"\benviron\s*\[\s*[\"']PWD[\"']\s*\]"
    r"|\benviron\.get\s*\(\s*[\"']PWD[\"']"
    r"|\bgetenv\s*\(\s*[\"']PWD[\"']")


def _as_literal(text: str) -> str:
    """Incrusta un TEXTO como literal python dentro del fuente del binario."""
    return json.dumps(text)


# ------------------------------------------------- binario falso (fixture)


FAKE_BINARY_SOURCE = r'''#!/usr/bin/env python3
# Binario OpenCode FALSO — fixture de tests/test_005_009_t2_opencode_adapter.py.
# NO es producto: simula el CLI destino sin runtime vivo. Protocolo declarado
# por el fichero de tests (oráculo T1; migrado por T1 de 005-010: la señal
# durable pasa de <fake>/sessions.json a un SQLite REAL CHICO con el esquema
# observado del runtime v2 — PD-7 de docs/specs/005-010-real-opencode-
# delegation/spec.md):
#   1. localiza el paquete canónico (marca ---cdad-packet-json) en: tokens de
#      ARGV que sean fichero -> ficheros nombrados en env con PACKET/CDAD/
#      DELIVER -> stdin.
#   2. registra CADA invocación en <fake>/calls.jsonl (append JSONL): argv
#      (rutas existentes como nombres de base; DEMÁS tokens VERBATIM, p.ej.
#      el valor de --server), cwd, PWD del entorno (VERBATIM), resultado de
#      la búsqueda del agente derivado en el proyecto PWD
#      (agent_found_in_project), env keys observadas, stdin visto, paquete
#      (transporte, sha256, bytes), emitted_final_text (si este cliente
#      imprimió el texto final acordado por stdout), session_id_written y rc
#      del cliente.
#   3. copia los bytes recibidos como paquete en <fake>/sent-packet.md.
#   4. variante leída de <fake>/variant. La SEÑAL DURABLE es una base SQLite
#      pequeña ESCRITA EN LA RUTA `sessions_db` DECLARADA POR LA CONFIGURACIÓN
#      DE EJECUCIÓN (el fixture la lee de <fake>/exec-config.json, campo
#      "sessions_db"; fallback <fake>/sessions.db) — el análogo material de
#      la base de sesiones del runtime real. Escritura atómica (tmp +
#      os.replace). Esquema observado (discovery §3.4 de 005-010):
#        session_v2(id, agent, model, directory, time_created, time_updated,
#                   time_idle, idle_outcome)
#        session_message(id, session_id, type, seq, data JSON)
#      La fila session_v2 lleva el id RECIBIDO EN --session (o el id por
#      defecto del fixture si la invocación no trae --session) y el agent
#      recibido en --agent (fallback "cdad-test-writer"). El DIRECTORIO DEL
#      PROYECTO es la env PWD (como OpenCode real — hecho del orquestador
#      contra v2.0.26 — NO el cwd del proceso): la columna
#      session_v2.directory lleva ese PWD y el agente derivado se busca en
#      <PWD>/.opencode/agents/<agente>.md (resultado grabado en
#      agent_found_in_project; el fixture NO falla duro si no está en ese
#      proyecto: la variante gobierna). Variantes:
#        succeeded       -> fila con idle_outcome='succeeded' + time_idle;
#                           session_message: user, assistant (texto
#                           intermedio decoy), assistant (TEXTO FINAL);
#        failed          -> fila con idle_outcome='failed' (sin texto);
#        interrupted     -> fila con idle_outcome='interrupted' (sin texto);
#        no-idle         -> fila SIN time_idle/idle_outcome: el cliente
#                           retorna rc=0 ANTES de que el rol quede idle (el
#                           texto por stdout NO es señal);
#        unknown-schema  -> SQLite VÁLIDO sin la columna idle_outcome
#                           (esquema desconocido: el adaptador debe fallar
#                           cerrado con diagnóstico, PD-2 de 005-010);
#        not-sqlite      -> el store NO es SQLite (bytes basura no UTF-8:
#                           nunca una excepción no capturada, PD-2);
#        wrong-agent     -> fila con idle_outcome='succeeded' y TEXTO
#                           final, PERO `agent` = el agente foráneo del
#                           fixture (FOREIGN_ROW_AGENT), NO el declarado
#                           en --agent: la identidad del rol se verifica
#                           desde la FILA durable (PD-3 de 005-010;
#                           variante de T2 de 005-010);
#        transport-error -> store SQLite válido SIN filas; stderr error de
#                           transporte; rc=2 (rc!=0 sin fila).
#        hangs           -> [R1 review-fix 005-010] store SQLite válido SIN
#                           filas, la invocación duerme MÁS que la espera
#                           acotada y NO retorna: registra su invocación
#                           ANTES de dormir (el adaptador la mata en la
#                           cota); hecho material = ausencia de señal en la
#                           cota → `timeout`, nunca `transport-error`.
#        succeeded-no-text -> [R3 review-fix 005-010] fila idle
#                           'succeeded' + time_idle SIN mensajes assistant
#                           (sin texto final) → `blocked` con diagnóstico
#                           (PD-5), nunca completed.
#        unknown-outcome -> [R3 review-fix 005-010] fila con
#                           idle_outcome NO declarado (UNKNOWN_OUTCOME) →
#                           `unknown` (PD-5), nunca completed, sin recibo.
#        model-object    -> [R2 review-fix 005-010] fila como `succeeded`
#                           pero con la columna `model` serializada como
#                           OBJETO JSON ({id, providerID}) → la
#                           observación I8 del worker la normaliza a
#                           'providerID/id' (PD-6).
#        b1-last-assistant-reasoning-only -> [B1 review-codex-2026-10-11,
#                           corrección requerida] fila 'succeeded' con un
#                           assistant INTERMEDIO con texto ('Voy a
#                           analizar...') y el ÚLTIMO assistant SOLO con
#                           una parte de razonamiento (SIN parte
#                           `type: text`): el texto final (PD-1) está
#                           AUSENTE → `blocked` (PD-5); el texto
#                           intermedio JAMÁS sustituye la entrega.
#        b1-last-assistant-multi-text -> [B1 review-codex-2026-10-11,
#                           REGRESIÓN] decoy + ÚLTIMO assistant con DOS
#                           partes textuales: la entrega es la
#                           CONCATENACIÓN de las partes de ESE mensaje
#                           solamente (sin el texto del decoy).
#   5. rc del cliente: 0 salvo transport-error (rc=2; el rc del cliente NO
#      es el fin del rol, PD-5).
#   6. sin paquete localizado: registra la entrada igual y señala en stderr
#      que no hubo transporte (frontera honesta del fixture).
#   7. `--version` imprime la versión declarada por la fixture y NO es
#      despacho (la versión vive en <fake>/version.txt): responde ANTES de
#      localizar el paquete, escribir el store o registrar la llamada
#      (oráculo 2 de 006-001 T1, plan §3: así el preflight del modo
#      servidor de la spec 006-001 §2.3 no crea fila ni cuenta como
#      invocación del rol; ANTES de localizar el paquete, no solo antes de
#      escribir/registrar, porque _locate_packet() lee stdin cuando no es
#      una tty: un --version del preflight que heredara un pipe abierto se
#      colgaría).

import hashlib
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent        # <fake>/bin
_FAKE = _HERE.parent                          # <fake>
_MARKER = b"---cdad-packet-json"


def _locate_packet():
    for token in sys.argv[1:]:
        candidate = Path(token)
        if candidate.is_file():
            data = candidate.read_bytes()
            if data.lstrip().startswith(_MARKER):
                return data, "argv-file"
    for key in sorted(os.environ):
        if any(part in key.upper()
               for part in ("PACKET", "CDAD", "DELIVER")):
            candidate = Path(os.environ[key])
            if candidate.is_file():
                data = candidate.read_bytes()
                if data.lstrip().startswith(_MARKER):
                    return data, "env:" + key
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            if data.lstrip().startswith(_MARKER.decode("utf-8")):
                return data.encode("utf-8"), "stdin"
    except Exception:
        pass
    return None, "unfounded"


def _argv_option(name):
    """Valor de una opción `--name <valor>` o `--name=<valor>` del argv."""
    argv = sys.argv[1:]
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith(name + "="):
            return token[len(name) + 1:]
    return None


def _argv_record():
    """Tokens de argv[1:] que el registro conserva: los que nombran una
    RUTA EXISTENTE como nombre de base (no filtran el tmpdir del fixture
    en el registro); los DEMÁS tokens VERBATIM (valores de opciones como
    la URL de `--server`). El basename global ANTERIOR truncaba cualquier
    valor con esquema (`http://fixture.invalid:4747` ->
    `fixture.invalid:4747`) y volvía injustificable la aserción PD-4 de
    005-010 (testfix; ningún producto podía satisfacerla)."""
    tokens = []
    for token in sys.argv[1:]:
        try:
            if token and Path(token).exists():
                tokens.append(Path(token).name)
                continue
        except (OSError, ValueError):
            pass
        tokens.append(token)
    return tokens


def _sessions_db_path():
    """La SEÑAL DURABLE vive DONDE LA DECLARA la config de ejecución
    (campo `sessions_db`; la config del fixture es <fake>/exec-config.json).
    Nunca una ruta hardcodeada: si la config no declara el campo, el
    fallback es el nombre heredado junto al propio fixture."""
    try:
        config = json.loads(
            (_FAKE / "exec-config.json").read_text(encoding="utf-8"))
        value = config.get("sessions_db")
    except (OSError, ValueError):
        value = None
    if value:
        return Path(value)
    return _FAKE / "sessions.db"


def _append_calls(calls_path, entry):
    """Registro append de invocaciones (JSONL, protocolo punto 2). Helper
    extraído para que la variante `hangs` (R1 de 005-010) pueda registrar
    su invocación ANTES de dormir: el adaptador mata el proceso al vencer
    la cota y sin este registro temprano el test no podría observar NADA."""
    if calls_path.is_file():
        try:
            lines = [line
                     for line in calls_path.read_text(
                         encoding="utf-8").splitlines()
                     if line.strip()]
            calls = [json.loads(line) for line in lines]
        except (json.JSONDecodeError, OSError):
            calls = []
    else:
        calls = []
    calls.append(entry)
    calls_path.write_text(
        "\n".join(json.dumps(call, sort_keys=True) for call in calls) + "\n",
        encoding="utf-8")


def _message_data(text):
    """Columna `data` JSON de session_message (esquema observado):
    content[].text con tipo `text`."""
    return json.dumps(
        {"content": [{"type": "text", "text": text}]}, sort_keys=True)


def _write_store(store_path, variant, session_id, agent_id, row_model,
                 final_text, decoy_text, user_text, project_dir):
    """Escribe el store SQLite del fixture según la variante (protocolo
    punto 4), atómicamente (tmp + os.replace). `project_dir` es el
    DIRECTORIO DEL PROYECTO que este cliente declara en la fila
    session_v2.directory: la env PWD (como OpenCode real), no el cwd del
    proceso."""
    now = time.time()
    outcomes = {"succeeded": "succeeded", "failed": "failed",
                "interrupted": "interrupted", "wrong-agent": "succeeded",
                "succeeded-no-text": "succeeded",
                "unknown-outcome": %UNKNOWN_OUTCOME%,
                "model-object": "succeeded",
                "b1-last-assistant-reasoning-only": "succeeded",
                "b1-last-assistant-multi-text": "succeeded"}
    idle = now if (variant in outcomes or variant == "unknown-schema") else None
    store_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = store_path.parent / (store_path.name + ".tmp")
    try:
        tmp_path.unlink()
    except OSError:
        pass
    if variant == "not-sqlite":
        # Bytes basura NO UTF-8: el UnicodeDecodeError del adaptador vigente
        # debe pasar a fallo cerrado diagnosticado (PD-2 de 005-010).
        tmp_path.write_bytes(
            b"\xff\xfe garbage-not-sqlite \x00\x01\x02 not a database\n")
        os.replace(tmp_path, store_path)
        return
    conn = sqlite3.connect(str(tmp_path))
    try:
        if variant == "unknown-schema":
            # Esquema válido pero SIN la columna idle_outcome.
            conn.execute(
                "CREATE TABLE session_v2 ("
                " id TEXT PRIMARY KEY, agent TEXT, model TEXT,"
                " directory TEXT, time_created REAL, time_updated REAL,"
                " time_idle REAL)")
        else:
            conn.execute(
                "CREATE TABLE session_v2 ("
                " id TEXT PRIMARY KEY, agent TEXT, model TEXT,"
                " directory TEXT, time_created REAL, time_updated REAL,"
                " time_idle REAL, idle_outcome TEXT)")
        conn.execute(
            "CREATE TABLE session_message ("
            " id TEXT PRIMARY KEY, session_id TEXT, type TEXT,"
            " seq INTEGER, data TEXT)")
        if variant not in ("transport-error", "hangs"):
            # `hangs` (R1 de 005-010): la invocación NO retorna dentro de
            # la cota — el hecho material es la AUSENCIA de fila/signal
            # dentro de la espera acotada; el store queda VÁLIDO pero SIN
            # filas (nunca una fila tardía fabricada por el fixture).
            if variant == "unknown-schema":
                conn.execute(
                    "INSERT INTO session_v2 (id, agent, model, directory,"
                    " time_created, time_updated, time_idle)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (session_id, agent_id, row_model, project_dir,
                     now - 5.0, now, idle))
            else:
                conn.execute(
                    "INSERT INTO session_v2 (id, agent, model, directory,"
                    " time_created, time_updated, time_idle, idle_outcome)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (session_id, agent_id, row_model, project_dir,
                     now - 5.0, now, idle, outcomes.get(variant)))
            messages = [("user", 1, _message_data(user_text))]
            if variant in ("succeeded", "wrong-agent", "model-object"):
                # `model-object` (R2 de 005-010): fila como `succeeded`
                # (decoy + TEXTO FINAL) pero con la columna `model`
                # serializada como OBJETO JSON (la forma del runtime real
                # reportada por la evidencia de aceptación).
                # `succeeded-no-text` (R3 de 005-010) deliberadamente NO
                # recibe mensajes `assistant`: idle succeeded SIN texto
                # final → blocked con diagnóstico (PD-5), nunca completed.
                messages.append(
                    ("assistant", 2, _message_data(decoy_text)))
                messages.append(
                    ("assistant", 3, _message_data(final_text)))
            elif variant == "b1-last-assistant-reasoning-only":
                # B1 (review-codex-2026-10-11, corrección requerida):
                # assistant INTERMEDIO con texto ('Voy a analizar...') +
                # ÚLTIMO assistant SOLO con una parte de razonamiento
                # (SIN parte `type: text`) + fila 'succeeded': el texto
                # final (PD-1) está AUSENTE → `blocked` (PD-5); el texto
                # intermedio JAMÁS sustituye la entrega ausente.
                messages.append(
                    ("assistant", 2, _message_data(b1_intermediate_text)))
                messages.append(
                    ("assistant", 3,
                     json.dumps({"content": [
                         {"type": "reasoning",
                          "text": b1_reasoning_text}]},
                         sort_keys=True)))
            elif variant == "b1-last-assistant-multi-text":
                # B1 REGRESIÓN (review-codex-2026-10-11): decoy + ÚLTIMO
                # assistant con DOS partes textuales — la entrega es la
                # CONCATENACIÓN de las partes de ESE mensaje solamente
                # (sin el texto del decoy).
                messages.append(
                    ("assistant", 2, _message_data(decoy_text)))
                messages.append(
                    ("assistant", 3,
                     json.dumps({"content": [
                         {"type": "text", "text": b1_final_part1},
                         {"type": "text", "text": b1_final_part2}]},
                         sort_keys=True)))
            for msg_type, seq, data in messages:
                conn.execute(
                    "INSERT INTO session_message (id, session_id, type,"
                    " seq, data) VALUES (?, ?, ?, ?, ?)",
                    (f"msg-{seq:04d}-{session_id}", session_id, msg_type,
                     seq, data))
        conn.commit()
    finally:
        conn.close()
    os.replace(tmp_path, store_path)


variant = (_FAKE / "variant").read_text(encoding="utf-8").strip()
if not variant:
    variant = "no-idle"
calls_path = _FAKE / "calls.jsonl"
sent_path = _FAKE / "sent-packet.md"
final_text = %FINAL_TEXT%
decoy_text = %DECOY_TEXT%
user_text = %USER_TEXT%
# B1 (review-codex-2026-10-11): textos del doble para las variantes del
# ÚLTIMO assistant (ver _write_store).
b1_intermediate_text = %B1_INTERMEDIATE_TEXT%
b1_reasoning_text = %B1_REASONING_TEXT%
b1_final_part1 = %B1_FINAL_PART1%
b1_final_part2 = %B1_FINAL_PART2%
session_id = _argv_option("--session") or %SESSION_ID%
agent_id = _argv_option("--agent") or "cdad-test-writer"
if variant == "wrong-agent":
    # La FILA durable declara OTRO agente (fixture T2 de 005-010): la
    # identidad del rol se verifica desde la fila, no desde el argv.
    agent_id = %FOREIGN_AGENT%
row_model = %ROW_MODEL%
if variant == "model-object":
    # Review-fix R2 de 005-010: la fila trae el modelo SERIALIZADO COMO
    # OBJETO JSON (forma del runtime real reportada por la evidencia de
    # aceptación); la observación I8 del worker debe normalizarlo a
    # 'providerID/id' (PD-6), no conservarlo verbatim.
    row_model = %ROW_MODEL_OBJECT%
version_line = %FAKE_VERSION%
if "--version" in sys.argv[1:]:
    # Oráculo 2 de 006-001 T1 (plan §3): responde ANTES de localizar el
    # paquete, escribir el store o registrar la llamada — un --version del
    # preflight de modo servidor (spec 006-001 §2.3) no crea fila ni
    # cuenta como invocación del rol. Antes de _locate_packet() también:
    # esa función lee stdin cuando no es una tty, y un --version que
    # heredara un pipe abierto se colgaría.
    sys.stdout.write(version_line + "\n")
    sys.stdout.flush()
    sys.exit(0)
store_path = _sessions_db_path()

# Directorio del PROYECTO, como OpenCode real (hecho del orquestador contra
# v2.0.26): la env PWD — NO el cwd del proceso. El agente derivado se busca
# en <PWD>/.opencode/agents/<agente>.md y la fila session_v2.directory
# lleva ese PWD. Sin caer duro si el agente no está en ese proyecto: la
# variante gobierna (el fixture grueba el hecho).
pwd_value = os.environ.get("PWD")
project_dir = Path(pwd_value) if pwd_value else Path(os.getcwd())
agent_found_in_project = (project_dir / ".opencode" / "agents"
                          / (agent_id + ".md")).is_file()

packet, transport = _locate_packet()
if packet is not None:
    sent_path.write_bytes(packet)

stdin_seen = transport == "stdin"

_write_store(store_path, variant, session_id, agent_id, row_model,
             final_text, decoy_text, user_text, project_dir=str(project_dir))

entry = {
    "argv0": os.path.basename(sys.argv[0] if sys.argv else ""),
    "argv": _argv_record(),
    "cwd": os.getcwd(),
    "pwd": pwd_value,
    "agent_found_in_project": agent_found_in_project,
    "env_keys": sorted(
        key for key in os.environ
        if any(part in key.upper()
               for part in ("PACKET", "CDAD", "DELIVER"))),
    "stdin_seen": stdin_seen,
    "packet": {"transport": transport, "sha256": None, "bytes": 0},
    "version_line": version_line,
    "emitted_final_text": variant in ("succeeded", "no-idle", "wrong-agent",
                                      "model-object"),
    # rc del cliente del registro: para `hangs` (R1 de 005-010) el
    # registro es HONESTO — esta invocación NUNCA retorna un rc (el
    # adaptador la mata en la cota): rc=None.
    "rc": None if variant == "hangs" else (2 if variant == "transport-error"
                                           else 0),
    "session_id_written": session_id,
    "agent_written": agent_id,
}
if packet is not None:
    entry["packet"] = {
        "transport": transport,
        "sha256": hashlib.sha256(packet).hexdigest(),
        "bytes": len(packet),
    }
    if transport == "stdin":
        entry["packet"]["stdin"] = packet.decode("utf-8")

if variant == "hangs":
    # Review-fix R1 de 005-010 (R-E de la spec: binario que cuelga): la
    # invocación NO RETORNA dentro de la cota. Registra la invocación
    # ANTES de dormir (el adaptador mata el proceso al vencer la cota),
    # emite NADA por stdout, NUNCA escribe fila (punto 4) y duerme MÁS
    # que la espera acotada: el hecho material observable es SOLO la
    # ausencia de señal dentro de la cota — la terminación declarada
    # debe ser `timeout` (sin fila / sin idle / cliente sin terminar),
    # NUNCA `transport-error` con un rc que no existe (el cliente no
    # retornó; lo mató el adaptador).
    _append_calls(calls_path, entry)
    sys.stdout.flush()
    time.sleep(120)
    sys.exit(0)

if variant == "transport-error":
    sys.stderr.write(
        "opencode-fake: error de conexión simulado (fixture)\n")

if packet is not None and variant in ("succeeded", "no-idle"):
    sys.stdout.write(final_text)
    if not final_text.endswith("\n"):
        sys.stdout.write("\n")
    sys.stdout.flush()

_append_calls(calls_path, entry)

if packet is None:
    sys.stderr.write("opencode-fake: sin paquete en el transporte "
                     "(argv/env/stdin): no aplica el rol\n")

sys.exit(entry["rc"])
'''


def under_results(base: Path, path: Path) -> bool:
    resolved = path.resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError:
        return False
    return True


# ---------------------------------------------- lectores del store (oráculo)
# Observadores de la SEÑAL DURABLE del fixture (SQLite real chico con el
# esquema observado). Los usan este fichero y tests/test_005_010_t1_durable_
# signal.py (import). SOLO-LECTURA (uri mode=ro): ningún test escribe el
# store del runtime (INV-3 de 005-010).


def durable_session_rows(store_path: Path) -> list[dict]:
    """Filas `session_v2` del store, como dicts column->valor (SOLO
    lectura). Lanza sqlite3.Error si el archivo no es una base SQLite."""
    conn = sqlite3.connect(f"file:{store_path}?mode=ro", uri=True)
    try:
        cursor = conn.execute("SELECT * FROM session_v2")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()


def durable_messages(store_path: Path, session_id: str) -> list[dict]:
    """Mensajes `session_message` de UNA sesión correlacionada, ordenados
    por seq, con `data` ya parseado (SOLO lectura)."""
    conn = sqlite3.connect(f"file:{store_path}?mode=ro", uri=True)
    try:
        cursor = conn.execute(
            "SELECT type, seq, data FROM session_message"
            " WHERE session_id = ? ORDER BY seq", (session_id,))
        return [
            {"type": msg_type, "seq": seq, "data": json.loads(data)}
            for msg_type, seq, data in cursor.fetchall()
        ]
    finally:
        conn.close()


def durable_last_assistant_text(store_path: Path, session_id: str) -> str | None:
    """El TEXTO del ÚLTIMO mensaje `assistant` de la sesión correlacionada
    (PD-1 de 005-010): la CONCATENACIÓN de los trozos `type == 'text'` de
    `data.content` de ESE ÚNICO mensaje. B1 (review-codex-2026-10-11,
    alineación del oráculo): JAMÁS acumula texto de mensajes assistant
    ANTERIORES — si el ÚLTIMO assistant no tiene parte textual, el texto
    final está AUSENTE (None; PD-5: succeeded → blocked), aunque un
    assistant anterior lo tuviera."""
    last_assistant = None
    for message in durable_messages(store_path, session_id):
        if message["type"] == "assistant":
            last_assistant = message
    if last_assistant is None:
        return None
    texts = [
        part["text"]
        for part in last_assistant["data"].get("content", [])
        if part.get("type") == "text" and part.get("text")
    ]
    return "\n".join(texts) if texts else None


# ---------------------------------------------------------------- fixture


class AdapterCase(DelegateCase):
    """Base T2: además de la base de T1, publica los agentes derivados del
    proyecto por adopción (CDAD_OPENCODE_AGENTS_DIR sobre una copia temporal
    de agents/cdad-*.md copiada sin inspección) y stagea la interfaz."""

    SEED_MODE = "subagent"  # modo REAL del rol derivado (desde T2 de 005-010: entry válida, ya NO fallo cerrado)

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-009-t2-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)
        self.agents_src = self.seed_agents()
        self.prepare_ok()
        self.execution_id = read_state(self.root)["execution"]["id"]
        self.packet_id = read_state(self.root)["active_packet"]["id"]
        self.state_before_bytes = (self.root / STATE_FILE_REL).read_bytes()
        self.tree_before = tree_snapshot(self.root)
        staged, _ = self.staged_interface()
        self.staged = staged

    # -- puertas y fixtures ------------------------------------------------

    def assert_adapter_in_product(self) -> None:
        """Puerta común del RED: el ADAPTADOR OpenCode debe existir en el
        producto (AssertionError, no import/sintaxis)."""
        self.assertTrue(
            ADAPTER_PRODUCT.is_file(),
            msg="RED: no existe el adaptador del destino OpenCode en el "
                "producto (se espera "
                f"{ADAPTER_PRODUCT.relative_to(REPO_ROOT)} por T2 del plan, "
                "resuelto por convención de módulo junto a la interfaz)")

    def seed_agents(self) -> Path:
        """Copia temporal de los agentes generados del repo (fuente I9),
        copiada SIN inspección (precedente T5 de 004-002). Con
        SEED_MODE='all' se declara en esa copia TEMPORAL el modo de entrada
        soportado (sed mecánico sobre el fixture, nunca sobre producto)."""
        agents_src = Path(self._tmp) / "agents-src"
        agents_src.mkdir(parents=True, exist_ok=True)
        for agent in sorted((REPO_ROOT / "agents").glob("cdad-*.md")):
            copied = agents_src / agent.name
            subprocess.run(["cp", str(agent), str(copied)], check=True)
            if self.SEED_MODE == "all" and agent.name == "cdad-test-writer.md":
                before = copied.read_bytes()
                subprocess.run(
                    ["sed", "-i", "s/^mode:.*/mode: all/", agent.name],
                    cwd=str(agents_src), check=True)
                self.assertNotEqual(
                    copied.read_bytes(), before,
                    msg="fixture: el sed mecánico de SEED_MODE no cambió la "
                        "copia temporal de cdad-test-writer.md (¿el modo "
                        "declarado del generador cambió de forma?)")
        return agents_src

    def prepare_ok(self, *extra: str) -> subprocess.CompletedProcess:
        """prepare del proyecto sintético CON adopción de agentes (I9)."""
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "cdad_packet.py"),
             "prepare", "--project-root", str(self.root),
             "--role", "test-writer", "--substage", "red",
             "--objective", "encargo T2 005-009 (adaptador OpenCode)",
             *extra],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            env={**dict(os.environ), AGENTS_ENV: str(self.agents_src)})
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): prepare publicó el paquete y los "
                f"agentes derivados: {proc.stdout + proc.stderr}")
        return proc

    def assert_derived_agents_published(self) -> None:
        derived = self.root / ".opencode" / "agents"
        self.assertTrue(
            (derived / ".cdad-derived.json").is_file(),
            msg="precondición (fixture): prepare no publicó el manifiesto "
                "de derivados .cdad-derived.json")
        self.assertTrue(
            (derived / "cdad-test-writer.md").is_file(),
            msg="precondición (fixture): prepare no publicó el agente "
                "derivado cdad-test-writer.md (entry del paquete)")

    # -- escenarios del binario falso --------------------------------------

    def fake_runtime(self, name: str, *, variant: str = "succeeded") -> dict:
        """Escribe el binario falso ejecutable + sus ficheros de fixture y
        la configuración de ejecución (esquema declarado en el docstring).
        Devuelve dict con rutas: dir/binary/config/calls/sent/sessions_db
        (sessions_db es el store SQLite del fixture)."""
        self.assert_adapter_in_product()
        assert variant in FAKE_VARIANTS, f"variante desconocida: {variant!r}"
        fake_dir = Path(self._tmp) / "fake-runtime" / name
        bin_dir = fake_dir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        binary = bin_dir / "opencode-fake"
        binary.write_text(
            FAKE_BINARY_SOURCE
            .replace("%FINAL_TEXT%", _as_literal(FAKE_FINAL_TEXT))
            .replace("%DECOY_TEXT%", _as_literal(DECOY_FINAL_TEXT))
            .replace("%USER_TEXT%", _as_literal(FAKE_USER_TEXT))
            .replace("%SESSION_ID%", _as_literal(SESSION_ID))
            .replace("%ROW_MODEL%", _as_literal(ROW_MODEL))
            .replace("%ROW_MODEL_OBJECT%", _as_literal(ROW_MODEL_OBJECT))
            .replace("%UNKNOWN_OUTCOME%", _as_literal(UNKNOWN_OUTCOME))
            .replace("%B1_INTERMEDIATE_TEXT%",
                     _as_literal(B1_INTERMEDIATE_TEXT))
            .replace("%B1_REASONING_TEXT%", _as_literal(B1_REASONING_TEXT))
            .replace("%B1_FINAL_PART1%", _as_literal(B1_FINAL_PART1))
            .replace("%B1_FINAL_PART2%", _as_literal(B1_FINAL_PART2))
            .replace("%FAKE_VERSION%", _as_literal(FAKE_BINARY_VERSION))
            .replace("%FOREIGN_AGENT%", _as_literal(FOREIGN_ROW_AGENT)),
            encoding="utf-8")
        binary.chmod(0o755)
        (fake_dir / "version.txt").write_text(
            FAKE_BINARY_VERSION + "\n", encoding="utf-8")
        (fake_dir / "variant").write_text(variant + "\n", encoding="utf-8")
        logs_dir = fake_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        config_path = fake_dir / "exec-config.json"
        config = {
            "runtime": FAKE_RUNTIME,
            "binary": str(binary),
            "binary_version": FAKE_BINARY_VERSION,
            "model": FAKE_MODEL,
            "logs_dir": str(logs_dir),
            "sessions_db": str(fake_dir / "sessions.db"),
            "wait": {"timeout_seconds": TEST_WAIT_TIMEOUT_SECONDS},
        }
        config_path.write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return {
            "dir": fake_dir,
            "binary": binary,
            "config": config_path,
            "calls": fake_dir / "calls.jsonl",
            "sent": fake_dir / "sent-packet.md",
            "sessions_db": fake_dir / "sessions.db",
        }

    def empty_user_home(self) -> Path:
        """`HOME`/`XDG_CONFIG_HOME` VACÍOS del fixture para UNA invocación de
        despacho: un temporal del test SIN `cdad/` (ni `delegation.json` ni
        `runtimes.json`), jamás la config de usuario del host. Lo usan los
        casos cuya premisa es la AUSENCIA de config de usuario (p.ej.
        `model_configured` null sin `delegation.json`, A-1 de 006-003 U4/D3):
        sin este aislamiento el test lee la config del host y la premisa deja
        de ser cierta. Precedente de la misma familia: `delegation_home()` de
        tests/test_005_010_t4_integration.py."""
        home = Path(self._tmp) / "user-home"
        (home / ".config").mkdir(parents=True, exist_ok=True)
        return home

    def run_opencode(self, fake: dict, *,
                     destination: str = "opencode",
                     cwd: Path | None = None,
                     user_home: Path | None = None) -> subprocess.CompletedProcess:
        """Invoca la interfaz STAGEADA con destino `opencode` y la config
        del binario falso (el env del test se hereda al árbol de procesos).
        Con `cwd` dado, el proceso corre EN ese directorio y su PWD ES ese
        mismo directorio (como lo deja un shell `cd`: simulación fiel de un
        coordinador cuya sesión corre desde un cwd ajeno). Con `user_home`
        dado (`empty_user_home()`), `HOME` y `XDG_CONFIG_HOME` se redirigen a
        ese temporal VACÍO: la corrida NO lee la config de usuario del host
        (corrige el AISLAMIENTO del caso, nunca su aserción)."""
        overrides: dict[str, str] = {}
        if user_home is not None:
            overrides["HOME"] = str(user_home)
            overrides["XDG_CONFIG_HOME"] = str(user_home / ".config")
        if cwd is not None:
            overrides["PWD"] = str(cwd)
        env = {**os.environ, **overrides} if overrides else None
        return subprocess.run(
            [sys.executable, str(self.staged),
             "--project-root", str(self.root),
             "--packet", self.packet_id,
             "--destination", destination,
             "--exec-config", str(fake["config"])],
            capture_output=True, text=True, env=env,
            cwd=str(cwd) if cwd is not None else None, timeout=300)

    # -- observadores del fixture ------------------------------------------

    def binary_calls(self, fake: dict) -> list[dict]:
        path = fake["calls"]
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def packet_call(self, fake: dict, label: str) -> dict:
        """LA ÚNICA invocación que transporta el paquete (sin encadenar
        sesiones ni invocaciones con paquete propio, PD-7)."""
        calls = [call for call in self.binary_calls(fake)
                 if isinstance(call.get("packet"), dict)
                 and call["packet"].get("sha256")]
        self.assertEqual(
            len(calls), 1,
            msg=f"{label}: el número de invocaciones que transportaron el "
                f"paquete no es UNA (sin encadenamiento de sesiones nuevas, "
                f"PD-7): {len(calls)}; argv: "
                f"{[call.get('argv') for call in calls][:4]!r}")
        return calls[0]

    def assert_no_generic_agent_fallback(self, fake: dict) -> None:
        """Ninguna invocación menciona un agente genérico no-Cdad (R-2;
        jamás fallback silencioso, PD-4)."""
        calls = self.binary_calls(fake)
        joined = " ".join(" ".join(call.get("argv", [])) for call in calls)
        self.assertIsNone(
            GENERIC_AGENT_RE.search(joined),
            msg=f"el despacho seleccionó un agente genérico no-Cdad (R-2; "
                f"prohibido por PD-4): argv "
                f"{[call.get('argv') for call in calls]!r}")

    # -- entregas durables -------------------------------------------------

    def results_base(self) -> Path:
        """Ubicación canónica de la entrega durable (discovery §2.4):
        .cdad/runtime/results/<exec>/<packet>/."""
        return (self.root / ".cdad" / "runtime" / "results"
                / self.execution_id / self.packet_id)

    def receipt_doc(self) -> dict:
        path = self.results_base() / "receipt.json"
        self.assertTrue(
            path.is_file(),
            msg=f"la entrega durable no dejó recibo en "
                f"{path.relative_to(self.root)} (receive)")
        return json.loads(path.read_text(encoding="utf-8"))

    def assert_receipt_no_gate(self) -> dict:
        """El recibo durable queda semantic_status 'pending': rc=0 /
        entregada NO aprueba el gate (PD-6/INV-5; el re-entry decide)."""
        receipt = self.receipt_doc()
        self.assertEqual(
            receipt.get("semantic_status"), "pending",
            msg=f"el recibo durable no queda 'pending' (rc=0 NO aprueba un "
                f"gate, PD-6/INV-5): {receipt.get('semantic_status')!r}")
        self.assertEqual(
            receipt.get("packet_id"), self.packet_id,
            msg="el recibo no corresponde al paquete despachado")
        return receipt

    def assert_final_text_in_delivery(self) -> None:
        """El TEXTO FINAL acordado está en la entrega durable (texto final
        + evidencia referenciada, PD-7)."""
        base = self.results_base()
        hits = [
            path for path in sorted(base.rglob("*"))
            if path.is_file() and FAKE_FINAL_TEXT.encode("utf-8")
            in path.read_bytes()
        ]
        self.assertTrue(
            hits,
            msg="ningún archivo de la entrega durable contiene el texto "
                "final acordado del rol (PD-7: texto final y evidencia)")

    def assert_durable_delivery_ref(self, out: dict) -> None:
        """La entrega declarada del envelope es DURABLE (flujo receive),
        bajo el árbol canónico de results."""
        ref = out.get("delivery_ref")
        self.assertIsInstance(
            ref, str, msg="delivery_ref de la entrega no es texto")
        self.assertTrue(ref, msg="delivery_ref vacío: sin entrega declarada")
        base = self.results_base()
        path = Path(ref)
        self.assertTrue(
            path.is_file(),
            msg=f"delivery_ref no apunta a un artefacto durable existente: "
                f"{ref!r}")
        self.assertTrue(
            under_results(base, path),
            msg=f"la entrega declarada quedó fuera del árbol canónico de "
                f"results ({base}): {ref!r}")

    def assert_no_receipt_fabricated(self, label: str) -> None:
        """Sin entrega durable fabricada: no hay recibo para el paquete."""
        self.assertFalse(
            (self.results_base() / "receipt.json").is_file(),
            msg=f"{label}: se fabricó recibo (entrega sin señal durable "
                f"material)")


# ---------------------------------------------------------------- PD-4


class TestPd4SubagentEntryDispatches(AdapterCase):
    """PD-4 — unidad INVERTIDA por T2 de 005-010 (PD-3 de
    docs/specs/005-010-real-opencode-delegation/spec.md): la entry derivada
    `mode: subagent` (configuración vigente de los roles, semilla real de
    esta fixture) DEJA de ser fallo cerrado: el adaptador SÍ despacha.

    RED de T2 (plan §T2): con el adaptador vigente (post T1-GREEN de
    005-010, que aún exige `mode: all`), la entry `subagent` es rechazada
    con terminación `blocked` — este test falla con AssertionError sobre
    ese comportamiento (blocked != completed)."""

    def test_pd4_subagent_entry_no_longer_fails_closed(self) -> None:
        """PD-3 de 005-010 (invertida): con la entry derivada
        `mode: subagent` publicada, el adaptador SÍ despacha: terminación
        `completed` con entrega durable, el argv nombra el agente cdad del
        paquete (cdad-test-writer) y jamás un genérico no-Cdad. El detalle
        completo del recorrido es el oráculo T2 nuevo
        (tests/test_005_010_t2_load_mode_invocation.py)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd4-subagent", variant="succeeded")

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "entry mode:subagent")

        self.assertEqual(
            out["termination"], "completed",
            msg=f"entry subagent: el adaptador sigue tratándola como fallo "
                f"cerrado (T2 de 005-010: mode: subagent DEJA de ser fallo "
                f"cerrado y DEBE despachar): termination "
                f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")
        call = self.packet_call(fake, "entry mode:subagent")
        self.assertIn(
            "cdad-test-writer", " ".join(call["argv"]),
            msg=f"la invocación del binario no nombra el agente cdad del "
                f"paquete (cdad-test-writer): {' '.join(call['argv'])!r}")
        self.assert_no_generic_agent_fallback(fake)


class TestPd4FailClosedUnpublishedDerived(AdapterCase):
    """PD-4 — unidad INVERTIDA por T2 de 005-010: el fallo cerrado del modo
    pasa a ser «el derivado cdad-<rol> NO está publicado»: falla CERRADO
    ANTES de despachar (sin invocación del binario), con diagnóstico que
    nombra el agente, sin sesión, sin entrega y sin recibo."""

    def test_pd4_unpublished_derived_fails_closed_before_dispatch(self) -> None:
        """PD-3 de 005-010: con el derivado `cdad-test-writer.md` AUSENTE
        del proyecto publicado, el adaptador falla cerrado pre-despacho:
        terminación `blocked` con diagnóstico accionable que nombra el
        agente; el binario falso NUNCA es invocado, no hubo transporte de
        bytes, no se declara identidad de sesión y no hay recibo; jamás un
        agente genérico no-Cdad."""
        self.assert_derived_agents_published()
        derived = self.root / ".opencode" / "agents" / "cdad-test-writer.md"
        self.assertTrue(
            derived.is_file(),
            msg="precondición (fixture): el derivado cdad-test-writer.md no "
                "está publicado antes de la manipulación")
        derived.unlink()  # fixture: el derivado cdad-<rol> NO está publicado
        fake = self.fake_runtime("pd4-absent", variant="succeeded")

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "derivado ausente")

        # Fallo cerrado pre-despacho, nombrado en el vocabulario.
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"derivado ausente: el adaptador no falló cerrado en la "
                f"clase 'blocked' (PD-3: sin derivado publicado no hay "
                f"despacho): {out['termination']!r}")
        diagnosis = out.get("diagnosis")
        self.assertIsInstance(
            diagnosis, str, msg="derivado ausente: el diagnóstico no es texto")
        self.assertTrue(
            diagnosis.strip(),
            msg="derivado ausente: diagnóstico vacío (la salida legítima "
                "ante bloqueo es un diagnóstico accionable)")
        self.assertIn(
            "cdad-test-writer", diagnosis.lower(),
            msg=f"derivado ausente: el diagnóstico no nombra el agente "
                f"derivado faltante 'cdad-test-writer' (PD-3): {diagnosis!r}")

        # SIN despacho: el binario falso nunca fue invocado y no hubo
        # transporte/identidad/recibo fabricados.
        self.assertEqual(
            self.binary_calls(fake), [],
            msg="derivado ausente: DESPACHÓ sesión (el binario falso fue "
                "invocado; argv ver fixtures)")
        self.assertFalse(
            fake["sent"].is_file(),
            msg="derivado ausente: entregó bytes al binario falso (despacho "
                "parcial prohibido)")
        self.assertFalse(
            out.get("session"),
            msg="derivado ausente: declaró identidad de sesión sin fila "
                "durable (nunca hubo sesión)")
        self.assert_no_receipt_fabricated("derivado ausente")
        self.assert_no_generic_agent_fallback(fake)


class TestPd4FailClosedDurableIdentityMismatch(AdapterCase):
    """PD-4 — unidad INVERTIDA por T2 de 005-010: el fallo cerrado pasa a
    ser «la fila durable declara OTRO agente»: blocked con diagnóstico que
    nombra AMBOS agentes, sin entrega, sin recibo, y JAMÁS un desvío a un
    agente genérico no-Cdad (INV-6).

    SEED_MODE = "all": bajo el adaptador VIGENTE (que aún exige `mode:
    all`) la semilla `subagent` bloquearía ANTES de despachar y el RED
    sería indistinguible de un fallo de modo. Con `all` el vigente SÍ
    despacha, la fila durable declara el agente foráneo y el vigente
    declara entrega IGUAL — la violación PD-3 observada. Bajo GREEN T2 el
    modo ya no condiciona: la semilla es irrelevante y el test vale igual.
    """

    SEED_MODE = "all"

    def test_pd4_durable_identity_mismatch_fails_closed_without_delivery(self) -> None:
        """PD-3 de 005-010: con la fila durable declarando un agente
        DISTINTO de cdad-<rol> (variante wrong-agent del binario falso), el
        adaptador NO declara entrega: terminación `blocked` con
        diagnóstico que nombra AMBOS agentes (el foráneo de la fila y el
        cdad-<rol> esperado); sin recibo; la ÚNICA invocación al binario
        nombró al agente cdad del paquete (jamás un genérico no-Cdad,
        INV-6)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd4-identity", variant="wrong-agent")
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "identidad durable distinta")

        # Precondición del fixture: la fila durable declara el agente
        # foráneo (no el cdad del paquete).
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("agent") for row in rows], [FOREIGN_ROW_AGENT],
            msg="fixture: la fila durable no declara el agente foráneo "
                f"{FOREIGN_ROW_AGENT!r} (precondición de la unidad): filas "
                f"{[dict(row) for row in rows]!r}")

        # La identidad desde la fila es la barrera: blocked, SIN entrega.
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"identidad durable distinta (la fila declara "
                f"{FOREIGN_ROW_AGENT!r}, no cdad-test-writer): el adaptador "
                f"no falló cerrado en la clase 'blocked' (PD-3: la "
                f"identidad se verifica desde la fila durable): "
                f"{out['termination']!r}")
        self.assertFalse(
            out.get("delivery_ref"),
            msg=f"identidad durable distinta: se declaró entrega "
                f"(delivery_ref {out.get('delivery_ref')!r}; PD-3: un agente "
                f"distinto NO declara entrega)")
        self.assert_no_receipt_fabricated("identidad durable distinta")

        # Diagnóstico que nombra AMBOS agentes (PD-3).
        diagnosis = out.get("diagnosis")
        self.assertIsInstance(
            diagnosis, str, msg="el diagnóstico no es texto")
        self.assertTrue(
            diagnosis.strip(), msg="diagnóstico vacío (sin diagnóstico "
                                   "accionable)")
        for token in (FOREIGN_ROW_AGENT, "cdad-test-writer"):
            self.assertIn(
                token.lower(), diagnosis.lower(),
                msg=f"el diagnóstico no nombra {token!r} (PD-3: agente de "
                    f"la fila y agente cdad esperado): {diagnosis!r}")

        # JAMÁS un desvío a un agente no-Cdad (INV-6): UNA sola invocación,
        # y nombró al agente cdad del paquete.
        calls = self.binary_calls(fake)
        self.assertEqual(
            len(calls), 1,
            msg=f"la invocación no fue UNA sola (¿reintento con otro "
                f"agente?, PD-3/INV-6): {len(calls)}; argv: "
                f"{[call.get('argv') for call in calls]!r}")
        self.assertEqual(
            calls[0].get("agent_written"), FOREIGN_ROW_AGENT,
            msg="fixture: la fila no fue escrita por el binario falso con "
                "el agente foráneo (precondición rota)")
        self.assertIn(
            "cdad-test-writer", " ".join(calls[0].get("argv", [])),
            msg=f"la única invocación no nombró al agente cdad del paquete "
                f"(PD-3): {' '.join(calls[0].get('argv', []))!r}")
        self.assert_no_generic_agent_fallback(fake)
        # El intento quedó en el ledger (hecho material para reconciliar).
        self.assert_attempt_is_in_ledger(out, records_before)


class TestPd4LoadModeSupported(AdapterCase):
    """PD-4 lado POSITIVO (semilla derivados con `mode: all` en la COPIA
    temporal del fixture): la entry SÍ despacha, por el binario
    configurado, sin fallback a genérico. Se CONSERVA tras la inversión de
    T2 de 005-010: el modo ya no condiciona el despacho (la barrera es la
    identidad desde la fila durable), así que una entry `mode: all`
    sembrada también despacha — test de no-regresión del modo legacy."""

    SEED_MODE = "all"

    def test_pd4_supported_mode_dispatches_session_without_generic_fallback(self) -> None:
        """PD-4 positivo: con la entry derivada declarada `mode: all`
        (semilla del fixture; desde T2 de 005-010 el modo NO condiciona),
        el adaptador SÍ despacha: invoca EL BINARIO CONFIGURADO (desde la
        config de ejecución), el argv nombra el agente cdad del paquete
        (cdad-test-writer), jamás un genérico no-Cdad, y el envelope
        declara terminación `completed` con la identidad de sesión del
        worker."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd4-sop", variant="succeeded")
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "entry mode:all")

        self.assertEqual(
            out["termination"], "completed",
            msg=f"la entry soportada no despachó a terminación completed: "
                f"{out['termination']!r}")
        # La identidad de sesión es la que EL ADAPTADOR ELIGIÓ y pasó en
        # `--session <id>` (PD-1): la fila durable correlacionada lleva ESE
        # id (el binario falso escribe la fila con el id recibido en
        # `--session`; SESSION_ID del fixture es SOLO su default cuando la
        # invocación NO trae --session — PD-1 coherente con
        # TestPd1SessionCorrelation).
        call = self.packet_call(fake, "entry soportada")
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("id") for row in rows], [out["session"]],
            msg=f"la fila durable no correlaciona con la identidad de "
                f"sesión declarada (PD-1: el id lo ELIGE el adaptador y lo "
                f"pasa en --session): {out['session']!r} != "
                f"{[row.get('id') for row in rows]!r}")
        self.assertEqual(
            out["session"], call.get("session_id_written"),
            msg=f"la identidad de sesión declarada no es el id que la "
                f"invocación pasó en --session (PD-1): {out['session']!r} "
                f"!= {call.get('session_id_written')!r}")

        # El despacho usó EL BINARIO CONFIGURADO: una invocación que
        # transportó el paquete, con el agente cdad del paquete en el argv.
        joined = " ".join(call["argv"])
        self.assertIn(
            "cdad-test-writer", joined,
            msg=f"la invocación del binario no nombra el agente cdad del "
                f"paquete (cdad-test-writer): {joined!r}")
        self.assert_no_generic_agent_fallback(fake)

        # Coherencia del fixture (los bytes de transporte vs su registro).
        self.assertEqual(
            hashlib.sha256(fake["sent"].read_bytes()).hexdigest(),
            call["packet"]["sha256"],
            msg="incoherencia del fixture: sent-packet.md y el registro de "
                "la llamada difieren")

        # El intento declarado vive en el MISMO ledger I8 (PD-2 ya probada
        # por T1; aquí queda referenciado el intento del worker).
        self.assert_attempt_is_in_ledger(out, records_before)


# ---------------------------------------------------------------- PD-5


class TestPd5(AdapterCase):
    """PD-5: la espera es sobre la SEÑAL DURABLE (sessions_db), no sobre el
    rc del cliente; acotada; sin sondeo sin fin ni callback inventado.

    Orden del caso: primero la NEUTRA discriminante (rc=0 sin señal → NO
    completed), después la positiva (señal durable → completed): así la
    ausencia de recibo fabricado del caso negativo no se contamina con un
    recibo anterior de la positiva."""

    SEED_MODE = "all"

    def test_pd5_durable_signal_gates_completion_not_client_rc(self) -> None:
        """PD-5: (negativa discriminante) un cliente que retorna rc=0 ANTES
        de que el rol termine — sin señal durable — NO produce `completed`:
        la terminación es `timeout` (espera ACOTADA por
        wait.timeout_seconds), sin recibo fabricado y el intento I8 queda
        en el ledger (los efectos no se niegan: hechos materiales para la
        reconciliación antes de repetir); (positiva) la señal durable
        presente SÍ otorga terminación `completed` con entrega declarada."""

        # --- negativa discriminante: rc=0 + texto por stdout, SIN señal.
        fake_late = self.fake_runtime("pd5-late", variant="no-idle")
        records_before = dispatch_records(self.root, self.execution_id)
        out_late = self.envelope(
            self.run_opencode(fake_late), "rc=0 sin señal")
        self.assertNotEqual(
            out_late["termination"], "completed",
            msg="el rc=0 del cliente produjo terminación completed (PD-5 "
                "violada: la espera sobre el CLIENTE, no sobre la señal)")
        self.assertEqual(
            out_late["termination"], "timeout",
            msg=f"el caso rc=0-sin-señal no terminó en la clase acotada "
                f"'timeout': {out_late['termination']!r}")
        self.assertTrue(
            out_late.get("diagnosis"),
            msg="diagnóstico de timeout vacío (sin diagnóstico accionable)")
        # Hecho material del fixture: el cliente SÍ retornó rc=0 y la fila
        # de sesión existe SIN idle (time_idle/idle_outcome NULL: el hecho
        # material esperable — la señal nunca apareció).
        call = self.packet_call(fake_late, "rc=0 sin señal")
        self.assertEqual(
            call.get("rc"), 0,
            msg="fixture: el cliente no retornó rc=0 (precondición del "
                "caso discriminatorio)")
        rows_late = durable_session_rows(fake_late["sessions_db"])
        self.assertEqual(
            [row.get("idle_outcome") for row in rows_late], [None],
            msg="fixture: la variante no-idle escribió idle en el store "
                "(precondición rota): filas "
                f"{[dict(r) for r in rows_late]!r}")
        # Hecho material adicional: el TEXTO FINAL acordado SÍ fue emitido
        # por stdout (pues el texto por stdout no es la señal durable).
        self.assertTrue(
            call.get("emitted_final_text") is True,
            msg="fixture: el texto final acordado no fue emitido por stdout "
                "en la variante no-idle (precondición rota)")
        # Timeout NO fabrica entrega durable.
        self.assert_no_receipt_fabricated("rc=0 sin señal")
        # Los efectos quedaron en el ledger (timeout NO prueba ausencia de
        # cambios: el intento I8 persiste para reconciliar antes de repetir)
        self.assert_attempt_is_in_ledger(out_late, records_before)

        # --- positiva: la señal durable (sessions_db) otorga completed.
        fake_ok = self.fake_runtime("pd5-ok", variant="succeeded")
        out_ok = self.envelope(self.run_opencode(fake_ok), "señal durable")
        self.assertEqual(
            out_ok["termination"], "completed",
            msg=f"con la señal durable presente la terminación no fue "
                f"completed: {out_ok['termination']!r}")
        self.assertTrue(
            out_ok.get("delivery_ref"),
            msg="con señal durable la entrega final no se declaró "
                "(delivery_ref vacío)")
        self.assertEqual(
            [row.get("idle_outcome")
             for row in durable_session_rows(fake_ok["sessions_db"])],
            ["succeeded"],
            msg="fixture: la señal durable del caso positivo no es la fila "
                "idle 'succeeded' en el store SQLite")
        self.assertTrue(
            len(self.binary_calls(fake_ok)) >= 1,
            msg="fixture: el binario falso del caso positivo nunca fue "
                "invocado")


# ---------------------------------------------------------------- PD-6


class TestPd6(AdapterCase):
    """PD-6: vocabulario de terminación derivado de HECHOS MATERIALES;
    entrega ≠ gate (recibo pending; state intacto); sin fabricación de
    entregas en las terminaciones que no declaran entrega. La victimaria
    post-interrupción (reconcile / dispatched-unknown) es de T4 por plan:
    aquí la terminación jamás cierra el gate ni borra hechos."""

    SEED_MODE = "all"

    def test_pd6_termination_vocabulary_from_material_facts_rc0_no_gate(self) -> None:
        """PD-6: cada causa de terminación sale de su hecho material
        (signal durable / fallo de transporte / espera acotada); el recibo
        queda `pending` (rc=0 NO aprueba gate, INV-5); el state no cambia
        más allá de la frontera del mecanismo reutilizado; las
        no-completadas jamás fabrican recibo."""
        # -- 4 terminaciones no-completadas (cada una desde su hecho):
        for variant in NON_COMPLETED_VARIANTS:
            with self.subTest(variant=variant):
                fake = self.fake_runtime(f"pd6-{variant}", variant=variant)
                out = self.envelope(self.run_opencode(fake),
                                    f"PD-6 {variant}")
                expected = VARIANT_TERMINATION[variant]
                self.assertEqual(
                    out["termination"], expected,
                    msg=f"{variant}: la terminación no ES la clase derivada "
                        f"del hecho material: {out['termination']!r} != "
                        f"'{expected}'")
                self.assertNotEqual(
                    out["termination"], "completed",
                    msg=f"{variant}: terminación completed (un gate cerrado "
                        f"por un hecho que no lo autoriza)")
                self.assertTrue(
                    out.get("diagnosis"),
                    msg=f"{variant}: diagnóstico vacío (el vocabulario "
                        f"exige diagnóstico accionable)")
                self.assert_no_receipt_fabricated(f"PD-6 {variant}")

        # -- completa: la ÚNICA terminación que declara entrega (hecho:
        #    señal durable existente): entrega durable + recibo PENDING.
        fake_ok = self.fake_runtime("pd6-ok", variant="succeeded")
        records_before = dispatch_records(self.root, self.execution_id)
        out_ok = self.envelope(self.run_opencode(fake_ok), "PD-6 completed")
        self.assertEqual(
            out_ok["termination"], "completed",
            msg=f"el caso con señal durable no terminó completed: "
                f"{out_ok['termination']!r}")
        self.assert_attempt_is_in_ledger(out_ok, records_before)
        self.assert_durable_delivery_ref(out_ok)
        self.assert_receipt_no_gate()         # pending: entrega ≠ gate (INV-5)
        self.assert_final_text_in_delivery()  # el texto final viaja durable

        # -- el state/árbol no cambia más allá de la frontera del mecanismo
        #    reutilizado (PD-2/INV-1 ahora con el adaptador: sin cierres de
        #    gate ni borrados de hechos materiales).
        state_before = json.loads(self.state_before_bytes.decode("utf-8"))
        self.assert_state_untouched_beyond_dispatch_frontier(state_before)
        changed = self.unexpected_touched(self.tree_changed())
        self.assertEqual(
            changed, [],
            msg=f"la delegación escribió fuera de la frontera del "
                f"mecanismo reutilizado: {changed}")


# ---------------------------------------------------------------- PD-7


class TestPd7(AdapterCase):
    """PD-7: el worker recibe SOLO el paquete (y sus insumos declarados —
    ya transportados por la preparación del paquete), no la conversación
    del coordinador; UNA única invocación porta el paquete (sin encadenar
    sesiones, sin esperar subagentes ajenos); devuelve texto final +
    evidencia durables."""

    SEED_MODE = "all"

    def test_pd7_bounded_context_single_dispatch_final_text_delivery(self) -> None:
        """PD-7: los bytes que el worker recibió son EXACTAMENTE los del
        PACKET.md publicado (contexto acotado; si el transporte fue stdin,
        además stdin == PACKET.md); UNA sola invocación porta el paquete
        (sin cadena de sesiones); la entrega durable contiene el texto
        final y el delivery_ref es del flujo receive (recibo pending,
        evidencia referenciada).
        No leen impl: la frontera del proceso es el binario falso."""
        fake = self.fake_runtime("pd7", variant="succeeded")
        out = self.envelope(self.run_opencode(fake), "PD-7")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"PD-7 sin flujo completo (terminación {out['termination']!r})")

        # Contexto ACOTADO: los bytes transportados == PACKET.md publicado.
        published = published_packets(self.root)[self.packet_id]
        sent = fake["sent"]
        self.assertTrue(
            sent.is_file(),
            msg="el binario falso no copió bytes de paquete (transporte "
                "ausente al worker)")
        self.assertEqual(
            sent.read_bytes(), published,
            msg="los bytes transportados al worker NO son los del PACKET.md "
                "publicado (contexto acotado, PD-7)")
        call = self.packet_call(fake, "PD-7 contexto acotado")
        self.assertEqual(
            call["packet"].get("bytes"), len(published),
            msg="los bytes registrados por el transporte no son los del "
                "paquete publicado")
        if call["packet"].get("transport") == "stdin":
            self.assertEqual(
                call["packet"].get("stdin"), published.decode("utf-8"),
                msg="el stdin transportó más/menos que el PACKET.md "
                    "publicado (PD-7: contexto acotado)")
        self.assert_no_generic_agent_fallback(fake)  # cdad agent of packet

        # El worker devuelve texto final + evidencia durables: la entrega
        # (parte del flujo receive, pending) contiene EL TEXTO FINAL y la
        # referencia declarada es durable.
        self.assert_final_text_in_delivery()
        self.assert_receipt_no_gate()
        self.assert_durable_delivery_ref(out)


# ------------------------------------------------- review-fix PD-3/PD-8


class TestAdapterCwdIndependent(AdapterCase):
    """Review-fix focal de T2 (subetapa red): INDEPENDENCIA DEL CWD del
    coordinador (PD-3 con el adaptador OpenCode; PD-8 portabilidad).

    Defecto detectado por el orquestador al verificar el GREEN de T2: el
    adaptador resuelve el árbol de la skill desde el cwd del coordinador
    (os.environ["PWD"], línea 297 del producto) cuando el árbol co-ubicado
    está incompleto. La fixture completa el staging con el árbol completo
    de la skill (staged_interface de T1), y ESTE test fija, por
    comportamiento observable, que la delegación completa funciona desde un
    cwd ajeno SIN resolver nada desde ese cwd; la comprobación estructural
    complementaria es sobre el ARTEFACTO PUBLICADO (no nombres internos):
    el adaptador no lee el PWD del coordinador como fuente de recursos."""

    SEED_MODE = "all"

    def assert_adapter_artifact_no_pwd_resolution(self) -> None:
        """Estructural sobre el artefacto publicado (dependencia declarada
        del encargo de review-fix: comprobación sobre el artefacto, no
        sobre nombres de funciones internas): el adaptador del destino
        OpenCode NO resuelve recursos desde el PWD del coordinador."""
        self.assertTrue(
            ADAPTER_PRODUCT.is_file(),
            msg="precondición del review-fix: el adaptador OpenCode del "
                "producto no existe (puerta de T2)")
        source = ADAPTER_PRODUCT.read_text(encoding="utf-8")
        hit = PWD_COORDINATOR_RESOLUTION_RE.search(source)
        # Aserción SATISFACIBLE (review-fix del test): el formateo del
        # mensaje es PEREZOSO — solo se construye cuando hay un hit que
        # mostrar (hit.group(0) sobre None era AttributeError y hacía
        # INSATISFACIBLE la aserción: nunca podía pasar). Con hit None el
        # assertIsNone pasa sin evaluar ningún formateo.
        if hit is None:
            # Caso de pase: assertIsNone(None) pasa; unittest jamás muestra
            # msg en un pase — el formateo perezoso está aquí por eso.
            self.assertIsNone(hit, msg="no puede fallar: hit es None")
        else:
            self.assertIsNone(
                hit,
                msg=f"el adaptador publicado resuelve recursos desde el "
                    f"PWD del coordinador (os.environ['PWD']: defecto "
                    f"declarado por el orquestador; PD-3/PD-8): "
                    f"{hit.group(0)!r} — el árbol de la skill debe "
                    f"resolverse co-ubicado a sí mismo (junto al "
                    f"artefacto: scripts/ + packets/ + references/ "
                    f"+ assets/), sin fallback al checkout del "
                    f"coordinador")

    def test_delegation_completes_durable_from_foreign_cwd_without_pwd_resolution(self) -> None:
        """PD-3/PD-8 (review-fix): desde un CWD AJENO (tempdir que no es el
        repo ni el proyecto, con PWD del proceso = ese cwd como lo dejaría
        un shell cd'ed), la delegación COMPLETA funciona — terminación
        `completed`, identidad de sesión del worker, envío de paquete único
        con el agente cdad, intento en el ledger I8, entrega durable por
        receive con recibo `pending` y texto final dentro de la entrega —
        SIN resolver nada desde ese cwd (el cwd ajeno no recibe escrituras
        ni registros) y con el artefacto publicado sin resolución desde
        PWD."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("cwd-independent", variant="succeeded")
        records_before = dispatch_records(self.root, self.execution_id)

        # CWD ajeno: subdirectorio del tempdir del test que NO es el repo,
        # NI el proyecto, NI contiene el árbol de la skill stageado.
        foreign = Path(self._tmp) / "foreign-cwd"
        foreign.mkdir(parents=True, exist_ok=True)

        # PWD del proceso = cwd ajeno (simulación fiel de un shell cd'ed:
        # si el adaptador resolviera desde el cwd del coordinador, no
        # encontraría nada en PWD).
        proc = self.run_opencode(fake, cwd=foreign)
        out = self.envelope(proc, "delegación desde cwd ajeno")

        # La delegación completa funciona desde el cwd ajeno.
        self.assertEqual(
            out["termination"], "completed",
            msg=f"la delegación completa no funcionó desde un cwd ajeno "
                f"(PD-3/PD-8: el adaptador NO debe depender del cwd del "
                f"coordinador): termination {out['termination']!r}, "
                f"diagnosis {out.get('diagnosis')!r}")
        # La identidad de sesión es la que EL ADAPTADOR ELIGIÓ y pasó en
        # `--session <id>` (PD-1), no la constante del fixture (SESSION_ID
        # es solo el default del binario falso sin --session; coherente con
        # TestPd1SessionCorrelation): la fila durable correlacionada lleva
        # ESE id y el argv registrado lo nombra.
        call = self.packet_call(fake, "delegación desde cwd ajeno")
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("id") for row in rows], [out["session"]],
            msg=f"la fila durable no correlaciona con la identidad de "
                f"sesión declarada (PD-1, delegación desde cwd ajeno): "
                f"{out['session']!r} != "
                f"{[row.get('id') for row in rows]!r}")
        self.assertEqual(
            out["session"], call.get("session_id_written"),
            msg=f"la identidad de sesión declarada no es el id que la "
                f"invocación pasó en --session (PD-1, delegación desde cwd "
                f"ajeno): {out['session']!r} != "
                f"{call.get('session_id_written')!r}")
        self.assertIn(
            "cdad-test-writer", " ".join(call["argv"]),
            msg=f"la invocación desde cwd ajeno no nombra el agente cdad "
                f"del paquete: {' '.join(call['argv'])!r}")
        self.assert_no_generic_agent_fallback(fake)
        self.assert_attempt_is_in_ledger(out, records_before)
        self.assert_durable_delivery_ref(out)
        self.assert_receipt_no_gate()
        self.assert_final_text_in_delivery()

        # Sin resolver nada desde el cwd ajeno: nada recibió ese directorio
        # (escalaba registros, logs, state ni árboles del proyecto).
        foreign_after = [
            item.relative_to(foreign).as_posix()
            for item in sorted(foreign.rglob("*"))
            if item.is_file() or item.is_dir()]
        self.assertEqual(
            foreign_after, [],
            msg=f"el cwd ajeno del coordinador recibió escrituras "
                f"(resolución dependiente del cwd, PD-3): "
                f"{foreign_after[:8]}")

        # Estructural sobre el artefacto publicado: sin resolución desde
        # el PWD del coordinador (PD-3/PD-8).
        self.assert_adapter_artifact_no_pwd_resolution()


if __name__ == "__main__":
    unittest.main(verbosity=2)
