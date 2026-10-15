# Aprobación delegada — 2026-09-17

Codex aprueba spec y plan bajo el mandato explícito del usuario para el epic.
El contrato responde a reducción de contexto y continuidad: preserva los roles,
permite validar paquetes y prepara identidades reutilizables por 002–004. No
modifica instalaciones reales ni despliega cambios. El review independiente
seguirá siendo obligatorio; esta aprobación no certifica implementación.

Fuente del architect: dos payloads temporales, copiados por el orquestador.
Hashes de los drafts recibidos:

- Spec: `4174820951d3c634fccb38b1c8a206c2774fff2566c18c368e26b4596cbaf8c3`.
- Plan: `4d46b71d612aae5292d10caa7a3f8fd4232ec64ce33f9191809b30f7095933ac`.

Ajustes explícitos al aprobar: límite de 12.000 bytes para instrucciones
estáticas por combinación (no tokens); metadata incluye ejecución y clasificación
de paths; tests conservan precedencia sobre implementación cuando comparten
directorio; compatibilidad del flujo existente sin paquete preparado; política
y CLI inicial instalables desde Tarea 1, ampliados en Tarea 2. Son decisiones
de contrato, no código anticipado. Los hashes aprobados son los del commit del spec.

TDD secuencial por tareas. La primera auditoría puede leer tests existentes y
contratos aprobados, sin scripts, agentes ni implementación nueva. No se certifica
RED mediante fallos de importación o ausencia de ejecutable.

Enmienda aprobada antes de T2: selectores de archivo exacto `path`, mutuamente
excluyentes con `root`, mediante listas opcionales `*_files`. Resuelve archivos
como install.sh y README.md sin permiso de escritura sobre todo el repositorio.
Propuesta del architect; conserva fixtures existentes y se verifica en T2.

Precisión de P4: aceptar una excepción no prueba los modelos ejecutados. El
recibo declara diversidad no exigida/acreditada y conserva reported=null
cuando no hay observación; no inventa igualdad efectiva entre roles.

Antes de RED T2 se fija un delimitador público del bloque de instrucciones
estáticas. Permite medir el límite desde el paquete renderizado, sin leer
implementación ni depender de headings arbitrarios. No convierte esa medida
en tokens ni reemplaza el juicio semántico del reviewer.

Antes de RED T3 se fija la ruta instalada
`CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/cdad_packet.py` y el consumo
portable: el orquestador entrega los bytes de `render` sin cambios; el rol no
recarga el ciclo completo. No se promete todavía interceptar Task dentro del
runtime.

Enmienda posterior al POST-AUDIT: metadata pública `instruction_sources` liga
common + rol + subfase mediante paths y SHA-256, en orden canónico, para evitar
que renderer y validator sean el mismo oráculo. Métricas fijan timestamps RFC
3339 y outcomes cerrados. Aprobado por Codex (agent-delegated) antes del GREEN
correctivo.
