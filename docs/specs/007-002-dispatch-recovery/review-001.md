# Review de etapa 4 — 007-002-dispatch-recovery (2026-10-24)

Dictamen: **NO APTO**. Dos BLOCKING reproducidos.

## BLOCKING 1 — el lector admite payloads que el productor no puede emitir
`cdad_packet.py:5798-5803,5817-5818,5844-5861`; §2.1.4, PC-10, INV-7.
Admite `exemption={}`, `current_stage`/`substage` fuera de vocabulario y digests de artefactos que no son SHA-256. Reproducido: variantes con hash recalculado dieron `rc=0`, `disposed` y, con `current_stage="not-a-stage"`, `--replace-packet` publicó el sucesor. Remedio: completar el verificador compartido con campos admitidos, vocabularios y representación canónica de artefactos.

## BLOCKING 2 — estado con codificación ilegible aborta `reconcile`
`cdad_continuity.py:984-998`; §2.2 fila 6, PC-10 y PC-13.
`read_text(encoding="utf-8")` sólo captura `OSError`; `UnicodeDecodeError` escapa. Reproducido con `b"\xff"`: rc=1, stdout vacío y traceback en lugar de envelope con `unknown`. Remedio: tratar errores de decodificación como fuente ilegible conservando el envelope.

## Resto
`21f14f7` no relaja oráculos. Selector único de disposición compartido. Reutilización de la publicación existente. Tres rechazos de `replaced_by` cubiertos. No se certificó la regresión completa (timeout).
