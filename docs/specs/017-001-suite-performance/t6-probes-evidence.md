# Sondas independientes de las garantías del lote — T6 (017-001)

Ejecutadas por el **orquestador** el 2026-11-08 sobre la revisión
`3da3f4c6` (más el commit de documentación posterior), porque el contrato del
reviewer es de solo lectura y dos de las sondas exigen una mutación temporal
del checkout (restaurada). El revisor valida la evidencia y el código; la
ejecución destructiva acotada queda del lado de la supervisión.

## Sonda A — descendiente que abandona grupo y sesión

Archivo sonda fuera de `tests/` (bajo `~/<workspace>/tmp/017-001-probes/setsid`),
pasado por `--nodeids`; lanza `/bin/sleep 120` con `start_new_session=True` y
termina.

```
python3 scripts/cdad-suite.py parallel --workers 1 \
  --evidence-root ~/<workspace>/tmp/017-001-probes/setsid/evidence \
  --nodeids ~/<workspace>/tmp/017-001-probes/setsid/nodeids.txt
```

Salida medida:

```
rc = 3
verdict = discarded: orphaned process family found and cleaned
          (familia de procesos viva tras el lote: encontrados=1 limpiados=1 restantes=0)
orphans = 1   found = 1   cleaned = 1   remaining = 0
sleep vivos después de la corrida = 0
```

## Sonda B — hijo transitorio dentro de la ventana de gracia

Sonda que lanza `/bin/sleep 1.5` (sin `start_new_session`) y termina; el hijo
sigue vivo cuando pytest sale y muere solo dentro de la gracia de 5 s.

```
rc = 0
verdict = accepted
orphans_found = 1   orphans = 0   cleaned = 0
```

Sin la ventana de gracia esta corrida se descartaba (rc 3), como quedó
registrado en la corrida real de `final3`. La gracia solo se espera cuando el
primer barrido encuentra familia viva: las corridas limpias no pagan los 5 s.

## Sonda C — huella del checkout con reescritura de igual tamaño y mtime

Archivo centinela `build/.cdad_canary_probe_target` creado **antes** de la
corrida (para que la huella inicial lo incluya); a mitad de la corrida se
reescribe con el mismo tamaño y contenido distinto, restableciendo su
`mtime` original con `os.utime`. Se restaura el contenido y se borra el
centinela al final (verificado: `git status` limpio, archivo ausente).

```
rc = 3
verdict = rejected: canary detected changes, run discarded para esa seleccion
          (canario alterado (config delta_lines=0, checkout unchanged=False))
checkout_canary.unchanged = False
fingerprint = sha256-per-file-sorted (c4f52953…)
fingerprint_cost_s = 3.07
```

La huella anterior (conteo, bytes y `mtime` máximo) no detectaba este caso;
la huella por contenido sí.

## Límites

- Las sondas viven fuera de `tests/` y nunca forman parte de `--all`; el árbol
  quedó sin restos.
- La garantía de familia requiere Linux (`prctl` + `/proc`); fuera de Linux el
  runner lo declara en vez de publicar `orphans: 0`.
- Estas sondas verifican las garantías, no el rendimiento: las paredes se miden
  en el par serial/paralelo documentado en `performance/parallelism.md`.
