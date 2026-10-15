# Informe de rol — test-writer, subetapa **RED** (review-fix de B1) · `005-013-unit-contract`

**Sesión:** aislada, rol `test-writer`, paquete `005-013-unit-contract-test-writer-red-003` (`substage: red`).
**Contrato:** `docs/specs/005-013-unit-contract/spec.md` (sha256 `4369822e…`), bloqueo **B1** de `docs/specs/005-013-unit-contract/review.md` y ficha T1 de `docs/specs/005-013-unit-contract/plan.md`.

## 0. Aislamiento y límites honestos

- **No leí código de implementación.** No abrí `skills/cdad-cycle/scripts/` ni ningún archivo fuera de `docs/specs/005-013-unit-contract/` y `tests/`. Para diseñar el fixture usé **solo la superficie de caja negra** (subprocess del CLI del producto sobre proyectos sintéticos en `<tmp>`, con `HOME` en un tempdir vacío), que es la superficie declarada del focal T1.
- **Anonimización:** fixtures sintéticos (`999-…`, `epic-999-fixture`, `ses-fixture-0001`); ninguna ruta absoluta del dueño ni id crudo de sesión en el archivo de test. En la salida pegada abajo la **única** redacción es `<repo>`/`<tmp>` por las rutas del dueño (nada más cambia).
- **No commiteé `docs/.cdad-state.json`:** está modificado por el **orquestador** (registró este paquete: `test-writer/red/dispatched`). Es su artefacto, fuera de mi write-scope; lo dejé intacto en el worktree.

## 1. (a) Casos agregados y qué cubre cada uno

Agregados al focal de T1 `tests/test_005_013_t1_unit_projection.py` (mismo producto: la publicación de la proyección). **No se borró ni debilitó ningún caso existente** (los 15 originales quedan verbatim; el único “−” del diff es el `sys.exit(pytest.main(...))` del pie, que se movió abajo).

| Caso nuevo | PD / INV / condición de cierre | Qué fija |
|---|---|---|
| `test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes` | **INV-3, PD-4**; condición de cierre 1 de B1 | Paquete ya publicado en el dir por defecto (su `UNIT-CONTRACT.md` + su `REQUEST.json` con el pin) + segunda corrida de `prepare` con `--out-dir` a un dir **custom VACÍO** (el `packet_id` acuñado es el **mismo** `-001`): debe **fallar cerrado (rc≠0)** con diagnóstico que **nombre el paquete en conflicto**, y los bytes de la proyección vieja **byte-idénticos** (`sha256` antes == después). Afirma las dos cosas (rc≠0 + nombre, e identidad byte a byte) y además que el `REQUEST.json` del paquete viejo no se toca. La proyección **viva** cambia antes del intento (se edita el alcance de la unidad activa, tramo 2 de AC-5): sin esa edición los bytes regenerados serían iguales y la identidad no probaría nada. |
| `test_b1_collision_leaves_the_old_packet_valid_and_receivable` | **INV-3, PD-4, PD-6**; condición de cierre 1 de B1 | Tras el intento de colisión, el paquete viejo (despachado) sigue siendo el registrado y utilizable: `contract.sha256` == digest del archivo **y** `receive` rc=0 con `packet_validation`/`identity_validation` `passed` y `semantic_status: pending`. |
| `test_b1_no_collision_with_custom_out_dir_still_publishes` | **PD-4, PD-5** (control) | Sin colisión (ningún paquete con ese `packet_id` en el dir por defecto): `prepare` rc=0, la proyección se publica en la ruta canónica `.cdad/packets/<packet_id>/UNIT-CONTRACT.md` con `sha256(archivo) == contract.sha256 == active_packet.contract_sha256`, y el paquete (`PACKET.md`+`REQUEST.json`) queda en el `--out-dir` custom. Evita que la corrección rompa el camino sin colisión. |

Derivados **del contrato** (INV-3/PD-4/PD-5/PD-6 + cierre de B1), no de la implementación. Dispositivos del fixture, declarados en los docstrings: transición del orquestador `active_packet.status = "completed"` (patrón ya usado en el epic, p. ej. `tests/test_005_001_t4_decisive.py:564`) para que la 2ª corrida de `prepare` llegue a la publicación, y restitución del binding `dispatched` antes de ejercitar `receive`.

## 2. (b) Archivo modificado

- `tests/test_005_013_t1_unit_projection.py` — **+277 / −1** (3 tests + 5 helpers de módulo + mapa test→postcondición del docstring y el párrafo de RED medido). Nada más.

## 3. (c) Comando exacto y salida completa del focal

```
$ python3 -m pytest tests/test_005_013_t1_unit_projection.py -q
```

```
...............FFF                                                       [100%]
=================================== FAILURES ===================================
___ test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes ___

fx = <test_005_013_t1_unit_projection.Fixture object at 0x72f9f9338a10>

    def test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes(
            fx: Fixture) -> None:
        """B1 (INV-3/PD-4; condición de cierre 1): con un paquete YA PUBLICADO en
        el directorio por defecto (su `UNIT-CONTRACT.md` y su `REQUEST.json` con el
        pin) y una segunda corrida de `prepare` con `--out-dir` a un directorio
        custom VACÍO —de modo que el `packet_id` acuñado sea el MISMO que el del
        paquete existente— `prepare` debe FALLAR CERRADO (rc!=0) con un diagnóstico
        que NOMBRE el paquete en conflicto, y los bytes del `UNIT-CONTRACT.md` del
        paquete viejo deben quedar BYTE-IDÉNTICOS (sha256 antes == sha256 después).

        RED hoy (medido): la colisión REESCRIBE la proyección publicada y devuelve
        rc=0 sin nombrar ningún paquete en conflicto → fallan las tres aserciones.
        """
        fx.prepare_ok()
        packet_id = fx.packet_id()
        projection = fx.unit_contract_path(packet_id)
        sha_before = sha256_bytes(projection.read_bytes())
        request_before = (fx.packet_dir(packet_id) / "REQUEST.json").read_bytes()

        edit_active_unit_scope(fx)
        complete_active_packet(fx)

        custom_out = make_custom_out_dir(fx)
        assert list(custom_out.iterdir()) == [], (
            "precondición (fixture): el `--out-dir` custom debe estar VACÍO (el "
            "`packet_id` acuñado vuelve a ser el `-001` del paquete ya publicado)")

        proc = fx.run(
            PACKET_CLI, "prepare", "--project-root", str(fx.root),
            "--role", "architect", "--substage", "discovery",
            "--objective", "005-013 T1 B1 colision", "--out-dir", str(custom_out))
        sha_after = sha256_bytes(projection.read_bytes())

>       assert proc.returncode != 0, (
            "INV-3/PD-4 violadas (B1): `prepare` con `--out-dir` custom NO debe "
            "reescribir la proyección de un paquete ya publicado: debe fallar "
            "cerrado (rc!=0) nombrando el paquete en conflicto. "
            f"rc={proc.returncode} stdout={proc.stdout[:200]!r} "
            f"stderr={proc.stderr[:400]!r} "
            f"sha256(proyección) antes={sha_before} después={sha_after}")
E       AssertionError: INV-3/PD-4 violadas (B1): `prepare` con `--out-dir` custom NO debe reescribir la proyección de un paquete ya publicado: debe fallar cerrado (rc!=0) nombrando el paquete en conflicto. rc=0 stdout='---cdad-packet-json\n{"contract":{"commit":null,"kind":"approved-unit-contract","path":".cdad/packets/999-001-fixture-unit-architect-discovery-001/UNIT-CONTRACT.md","sha256":"cec98be9caaaf0e77997fbdb8a' stderr='CDAD prepare: OpenCode agents source directory not found; derived agents were not published without a source directory (CDAD_OPENCODE_AGENTS_DIR)\n' sha256(proyección) antes=2237d30df0650a7e8ac0fc3d77d923c02438dd8e2c0aaed938cee8fc70b5f464 después=cec98be9caaaf0e77997fbdb8ada20243b5a5fe906c0416bfa1f96b889f2abcd
E       assert 0 != 0
E        +  where 0 = CompletedProcess(args=['/usr/bin/python3', '<repo>/skills/cdad-cycle/scripts/cdad_packet....source directory not found; derived agents were not published without a source directory (CDAD_OPENCODE_AGENTS_DIR)\n').returncode

tests/test_005_013_t1_unit_projection.py:1150: AssertionError
_________ test_b1_collision_leaves_the_old_packet_valid_and_receivable _________

fx = <test_005_013_t1_unit_projection.Fixture object at 0x72f9f9339e50>

    def test_b1_collision_leaves_the_old_packet_valid_and_receivable(
            fx: Fixture) -> None:
        """B1 (INV-3/PD-4/PD-6; condición de cierre 1): tras el intento de colisión
        fallido, el paquete viejo sigue siendo el registrado y utilizable: su
        `contract.sha256` sigue coincidiendo con el archivo de la proyección y
        `receive` sigue dando lo que daba antes (rc=0 con `packet_validation` /
        `identity_validation` `passed` y `semantic_status: pending`, porque el
        paquete estaba despachado).

        Dispositivo del fixture (declarado): el paquete viejo se despacha; para que
        la segunda corrida de `prepare` llegue a la publicación el state pasa por la
        transición del orquestador, y antes de ejercitar `receive` se restituye el
        binding del paquete registrado (su `active_packet` dispatched).

        RED hoy (medido): la colisión reescribe la proyección del paquete viejo, su
        `contract.sha256` durable deja de coincidir con el archivo y `receive`
        responde rc=2 («contract sha256 does not match exact content») → el paquete
        queda irrecebible.
        """
        fx.prepare_ok()
        packet_id = fx.packet_id()
        fx.dispatch_ok(packet_id)
        active_before = fx.state()["active_packet"]

        edit_active_unit_scope(fx)
        complete_active_packet(fx)
        custom_out = make_custom_out_dir(fx)
        fx.run(
            PACKET_CLI, "prepare", "--project-root", str(fx.root),
            "--role", "architect", "--substage", "discovery",
            "--objective", "005-013 T1 B1 colision", "--out-dir", str(custom_out))

        restore_active_packet(fx, active_before)

        contract = fx.request(packet_id)["contract"]
        sha_file = sha256_bytes(fx.unit_contract_path(packet_id).read_bytes())
>       assert contract["sha256"] == sha_file, (
            "INV-3/PD-4 violadas (B1): el `contract.sha256` durable del paquete "
            "viejo debe seguir coincidiendo con los bytes de su proyección: "
            f"{contract['sha256']!r} != {sha_file!r}")
E       AssertionError: INV-3/PD-4 violadas (B1): el `contract.sha256` durable del paquete viejo debe seguir coincidiendo con los bytes de su proyección: '2237d30df0650a7e8ac0fc3d77d923c02438dd8e2c0aaed938cee8fc70b5f464' != 'cec98be9caaaf0e77997fbdb8ada20243b5a5fe906c0416bfa1f96b889f2abcd'
E       assert '2237d30df065...ee8fc70b5f464' == 'cec98be9caaa...f96b889f2abcd'
E         
E         - cec98be9caaaf0e77997fbdb8ada20243b5a5fe906c0416bfa1f96b889f2abcd
E         + 2237d30df0650a7e8ac0fc3d77d923c02438dd8e2c0aaed938cee8fc70b5f464

tests/test_005_013_t1_unit_projection.py:1205: AssertionError
___________ test_b1_no_collision_with_custom_out_dir_still_publishes ___________

fx = <test_005_013_t1_unit_projection.Fixture object at 0x72f9f92fd020>

    def test_b1_no_collision_with_custom_out_dir_still_publishes(
            fx: Fixture) -> None:
        """Control de B1 (PD-4/PD-5): con un `--out-dir` custom VACÍO y NINGÚN
        paquete con ese `packet_id` en el directorio por defecto, `prepare` rc=0 y
        la proyección se publica en la ruta canónica
        (`.cdad/packets/<packet_id>/UNIT-CONTRACT.md`), con
        `sha256(UNIT-CONTRACT.md) == contract.sha256 ==
        active_packet.contract_sha256`; el paquete (PACKET.md + REQUEST.json) queda
        en el directorio custom. Evita que la corrección de B1 rompa el camino sin
        colisión.

        El fixture publica primero un paquete de OTRA subetapa (draft) con el
        directorio por defecto, de modo que `.cdad` existe y el `packet_id` de la
        subetapa `discovery` (el `-001` acuñado contra el `--out-dir` vacío) NO
        existe en el directorio por defecto.

        RED hoy (medido): `prepare` rc=2 («cannot write prepared packet: [Errno 2]
        … extra-000 -> …/UNIT-CONTRACT.md») porque el commit de la proyección asume
        que el directorio del paquete ya existe en la ruta canónica.
        """
        fx.prepare_ok(substage="draft")
        draft_packet_id = fx.packet_id()
        complete_active_packet(fx)

        custom_out = make_custom_out_dir(fx)
        assert list(custom_out.iterdir()) == [], (
            "precondición (fixture): el `--out-dir` custom debe estar VACÍO")
        proc = fx.run(
            PACKET_CLI, "prepare", "--project-root", str(fx.root),
            "--role", "architect", "--substage", "discovery",
            "--objective", "005-013 T1 B1 control", "--out-dir", str(custom_out))
>       assert proc.returncode == 0, (
            "PD-4/PD-5 violadas (control de B1): sin colisión, `prepare` con "
            "`--out-dir` custom debe publicar el paquete y su proyección (rc=0): "
            f"rc={proc.returncode} stdout={proc.stdout[:200]!r} "
            f"stderr={proc.stderr[:400]!r}")
E       AssertionError: PD-4/PD-5 violadas (control de B1): sin colisión, `prepare` con `--out-dir` custom debe publicar el paquete y su proyección (rc=0): rc=2 stdout='' stderr="CDAD prepare: OpenCode agents source directory not found; derived agents were not published without a source directory (CDAD_OPENCODE_AGENTS_DIR)\nERROR: cannot write prepared packet: [Errno 2] No such file or directory: '<tmp>/pytest-NNN/test_b1_no_collision_with_cust0/proj/.cdad/.txn/999-001-fixture-unit-architect-discovery-001/extra-000' -> '<tmp>/pytest-NNN/test_b1_n"
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=['/usr/bin/python3', '<repo>/skills/cdad-cycle/scripts/cdad_packet....2/test_b1_no_collision_with_cust0/proj/.cdad/packets/999-001-fixture-unit-architect-discovery-001/UNIT-CONTRACT.md'\n").returncode

tests/test_005_013_t1_unit_projection.py:1257: AssertionError
=========================== short test summary info ============================
FAILED tests/test_005_013_t1_unit_projection.py::test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes
FAILED tests/test_005_013_t1_unit_projection.py::test_b1_collision_leaves_the_old_packet_valid_and_receivable
FAILED tests/test_005_013_t1_unit_projection.py::test_b1_no_collision_with_custom_out_dir_still_publishes
3 failed, 15 passed in 8.21s
```

Log completo (sin sanitizar) en `<tmp>/opencode/005-013-t1-redfix.log` (152 líneas, sha256 `2cfa25fd04dee146…`).

**Lectura del RED (medido, las tres fallas son `AssertionError` de comportamiento, ninguna por ImportError/sintaxis/fixture):**
1. La colisión **reescribe** la proyección publicada: `sha256` pasó de `2237d30d…` a `cec98be9…` — **la misma medición del reviewer** — y `prepare` devuelve **rc=0** sin nombrar ningún paquete en conflicto.
2. El `contract.sha256` durable del paquete viejo (`2237d30d…`) deja de coincidir con el archivo (`cec98be9…`); `receive` responde rc=2 (`contract sha256 does not match exact content`) → paquete irrecebible.
3. Sin colisión, `prepare` con `--out-dir` custom responde **rc=2** (`cannot write prepared packet: [Errno 2] … extra-000 -> …/UNIT-CONTRACT.md`).

Verificaciones adicionales (no sustitutivas del focal): `python3 -m ruff check tests/test_005_013_t1_unit_projection.py` → `All checks passed!`; `python3 -m pytest tests/test_005_013_t2_change_classification.py --collect-only -q` → `15 tests collected` (T2 importa el módulo de T1; mi cambio es aditivo y no lo afecta). La suite completa **no** se corrió (política del paquete: la corre quien cierra).

## 4. (d) Commit

```
$ git add tests/test_005_013_t1_unit_projection.py
$ git commit -m "test(005-013): RED del review-fix de B1 — la proyeccion publicada nunca se reescribe (colision de --out-dir custom falla cerrada; control sin colision publica) ..."
4bf688c test(005-013): RED del review-fix de B1 — la proyeccion publicada nunca se reescribe (colision de --out-dir custom falla cerrada; control sin colision publica)
 tests/test_005_013_t1_unit_projection.py | 278 ++++++++++++++++++++++++++++++-
 1 file changed, 277 insertions(+), 1 deletion(-)
```

Rama `codex/epic-005-real-operation`; sin push, sin `--no-verify`, sin desplegar, sin tocar HOME, sin leer `tests/.sensitive-patterns.local`. Worktree tras el commit: solo ` M docs/.cdad-state.json` (del orquestador, **no** commiteado).

## 5. (e) Dónde me detuve / declaraciones que el orquestador debe conocer

1. **El “control” (caso 2) NO pasa hoy: es RED (rc=2).** Lo medí antes de escribirlo. La causa es que el commit de la proyección asume que el directorio del paquete existe en la ruta canónica; con `--out-dir` custom el paquete va al dir custom y el padre canónico no existe → `FileNotFoundError` en el `os.replace`. Con la corrección **create-only** el caso debe quedar verde (publicar la proyección creando el padre canónico). Lo declaro explícitamente en el docstring del test: no lo presento como “guardia que ya pasa”. Si el implementador considera que la corrección barata de B1 no debe cubrir ese camino, **es un conflicto de contrato que hay que resolver antes del GREEN** (el comportamiento 2 del paquete es explícito), no un defecto del test.
2. **La colisión es observable sin fabricar un state inválido:** requiere la transición del orquestador (`active_packet.status = "completed"`, patrón ya usado en el epic) porque el CLI bloquea una segunda corrida mientras el paquete activo está `prepared`/`dispatched` (`ERROR: active packet … is 'prepared'`). No me detuve por esto; queda declarado en el fixture y en los docstrings.
3. **No ejercité `receive` sin paquete despachado:** en el caso 2 el paquete viejo se despacha antes y el binding `dispatched` se restituye antes del `receive` (medido: `receive` rc=0 con el binding restituido; con `active_packet: null` el CLI responde `rendering requires an active_packet`). Por eso uso `receive` y no `validate-packet`: el fixture lo permite.
4. **No inventé nada fuera del alcance:** no toqué la implementación, la política, el esquema del recibo, ni tests de otras features; no commité el state del orquestador.
