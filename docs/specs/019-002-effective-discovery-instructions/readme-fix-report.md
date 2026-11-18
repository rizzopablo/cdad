Los cuatro tests que fallaban ya pasan, y el commit `2de6e72b` contiene solo `README.md`. No toqué tests ni ningún otro archivo.

**Validación del paquete (ruta C):** `cdad_packet.py render` generó un resultado idéntico byte a byte a `PACKET.md`, y el sha256 del spec coincide con el del contrato.

**Cambios en `README.md`:**
1. **Sección nueva `## Guided start`** (6 líneas no vacías, sin bloque cercado, sin puntero a plantilla). Dice que una instrucción breve basta hasta la primera delegación útil y apunta a `skills/cdad-cycle/references/project-start.md`. Está antes de `## Operating an adopted project`.
2. **Mención de `CDAD_INSTALL_ROOT` eliminada.** Ahora el párrafo dice que, para instalar en una raíz de adopción separada y activarla en OpenCode, Claude Code o Codex, se siga `runtime-adoption.md`. Así se conserva el sentido sin nombrar la variable.
3. **Invocación del CLI** (línea 127): `cdad_packet.py status` pasó a `<skill-dir>/scripts/cdad_packet.py status`.

**Comando y resultado:**
```
python3 -m pytest -q tests/test_005_006_t4_readme.py tests/test_005_006_t6_owner_reviewfix.py tests/test_005_006_t2_intake.py
13 passed in 0.53s
```

No corrí la suite completa: la selección fue solo esos 3 archivos, como pedía el encargo.