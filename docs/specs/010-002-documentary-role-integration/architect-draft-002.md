## 3. Cambios respecto de v1

| Hallazgo | Cambio propuesto en v2 |
|---|---|
| **B1** | Base de aplicabilidad por rol; frontera de addon y documentación interna; PC-04/05 enumeran documental/addon/mixto. Reviewer y orquestador deciden por diff real. |
| **B2** | `skills/cdad-cycle/SKILL.md` añadido a citas y T4 en ambas proyecciones; `TestDispatchDoctrine` cubre «otro valor» en ambas superficies. |
| **O1** | Coherencia contra stack vigente solo al publicar y registrar despacho nuevo; recepción publicada no se reinterpreta. Riesgo y transición comprometidos. |
| **O2** | Contexto presente exige agente; históricos sin ambos siguen admitidos. T2 mide impacto y T5 adapta fixtures antes de GREEN. |
| **O3** | PC-08 distingue rechazo mecánico externo y obligación procedimental nativa. |
| **O4** | PC-12.a corresponde a T4; PC-12.b a T6/T7. |
| **O5** | «Perfil documental» equivale expresamente a especialización por contrato; documental/Odoo comprometido en PC-12 y EV-04. |
| **O6** | Regresiones de T4 y T6 idénticas en prosa y `plan-tasks`. |
| **Abstenciones** | T2 debe medir fixtures discordantes; T4 inventaría cuatro referencias Odoo concretas antes de decidir su modificación. |

D-1, D-3 y D-5 permanecen, con los límites temporales y de compatibilidad expresamente solicitados.

## 4. Evidencia de esta tarea

- **Archivos modificados:** ninguno.
- **Commit creado:** ninguno.
- **HEAD:** `3bea7a8d356e35ccb93d22d010632f1d7e7406bf`.
- **Suite, generación, instalación o publicación:** no ejecutadas.
- **Estado del repositorio:** mismas modificaciones preexistentes al inicio y al final.

Comandos de intake ejecutados:

```sh
python3 -B scripts/cdad_packet.py validate-request --request .cdad/packets/010-002-documentary-role-integration-architect-draft-002/REQUEST.json

python3 -B scripts/cdad_packet.py validate-packet --request .cdad/packets/010-002-documentary-role-integration-architect-draft-002/REQUEST.json --packet .cdad/packets/010-002-documentary-role-integration-architect-draft-002/PACKET.md

python3 -B scripts/cdad_packet.py render --request .cdad/packets/010-002-documentary-role-integration-architect-draft-002/REQUEST.json
```

Resultados:

```text
validate-request: rc=0, stdout='', stderr=''
validate-packet: rc=0, stdout='', stderr=''
full canonical equality: True
context schema_version: 2
contract sha256:
14c88f6289da3f5dedce5a390b10fbd008c8ce15c30800c9721713350087c624
```

La identificación de ruta C también coincide con su render canónico. El censo acotado de requests publicados encontró **44 con contexto y agente, y ninguno con contexto sin agente**; la revisión anterior registraba 43 con ambos. Esto no mide todavía los fixtures: esa obligación queda explícitamente en T2.

**Ambos textos son borradores; no constituyen aprobación ni autorización de implementación.**
</subagent>
