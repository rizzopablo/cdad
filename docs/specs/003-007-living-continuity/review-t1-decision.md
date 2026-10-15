# Decisión del orquestador — review T1 (003-007)

Informe: `review-t1.md`, recibido con `cdad_result receive` (receipt
`4e5cfd11…8353`, idempotente: el segundo `receive` volvió a validar sin duplicar) y
materializado sin cambios. **T1 cerrada**: sin bloqueantes; gate acotado 52/52.

| Hallazgo | Decisión |
|---|---|
| O-1: un body nuevo sin `class` pasa como legado y no bloquea | **Entra en T2.** Cuando el body gane `record`, un body es legado **solo si no tiene `record`**. Una referencia sin clase dentro de un body con `record` se trata como `contract` (P3), así que falla cerrada. No cambia la spec: precisa D6 y P7 con el discriminador que T2 introduce. Se agrega al RED de T2. |
| N-1: estado `missing` para un archivo existente pero no proyectable | Deuda (baja): distinguir `unreadable`. |
| N-2: un campo de `fields` que no resuelve protege cero, en silencio | Deuda (baja): documentarlo en `continuity.md`. Hoy solo falla cerrada la proyección vacía completa. |
| N-3: `begin`/`checkpoint` no verifican las referencias `contract` del head previo | Deuda (baja). Fuera de P1, preexistente. |
