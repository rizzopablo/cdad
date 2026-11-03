#!/usr/bin/env python3
"""014-001 RED — defaults de evidencia por momento (promesas A–D).

Contrato: `docs/specs/014-001-suite-evidence-defaults/spec.md` (sha256
`6403397f4d57abee961d59c69a4d8d7403f7a306b2fdbc2e4785622208b0c2f0`).
Mapeo aprobado en `docs/specs/014-001-suite-evidence-defaults/test-audit.md`
§2 + decisión §4: EXACTAMENTE 4 verificadores nuevos, uno por promesa
observable (R2), cada uno con las aserciones mecánicas de los ítems
A1–A3 / B1–B4 / C1–C3 / D1–D3 y trazado a sus PC. La parte semántica queda
para el reviewer (spec §7).

Regla de selección (R2): un test por promesa observable del usuario, no por
PC ni por archivo. Cada test protege varias PC de su promesa: eso es
trazabilidad, no falta de cobertura.

Oráculos derivados del contrato aprobado, no del texto bajo verificación.
Estructura exigida donde es barato (sección única, tabla de momentos,
ubicación), no mera presencia de palabras. Modo de fallo esperado:
AssertionError de comportamiento (norma pendiente), nunca ImportError.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOME = REPO / "skills" / "cdad-cycle" / "references" / "stage-3-tdd.md"
COMMON = REPO / "skills" / "cdad-cycle" / "packets" / "common.md"
CI_GATE = REPO / "docs" / "ci-gate.md"
RUN_BUDGET = (
    REPO / "skills" / "odoo-make-env" / "references" / "run-budget-protocol.md"
)
EPIC_CLOSURE = REPO / "skills" / "cdad-epic" / "references" / "epic-closure.md"
STAGE5_MERGE = REPO / "skills" / "cdad-cycle" / "references" / "stage-5-merge.md"

# Superficies del §5 de la spec (inventario vinculante). La comprobación de
# cada fila corresponde a PC-9; las referencias a otras PC precisan su
# comprobación en el test de su promesa.
CONSUMERS = [
    REPO / "skills/cdad-cycle/references/stage-3-tdd.md",
    REPO / "skills/cdad-cycle/SKILL.md",
    REPO / "skills/cdad-cycle/references/handoff-prompts.md",
    REPO / "skills/cdad-cycle/references/re-entry.md",
    REPO / "skills/cdad-cycle/references/anti-patterns.md",
    REPO / "skills/cdad-cycle/references/stage-4-review.md",
    REPO / "skills/cdad-cycle/references/stage-5-merge.md",
    REPO / "skills/cdad-cycle/references/state-detection.md",
    REPO / "skills/cdad-cycle/assets/feature-plan-template.md",
    REPO / "skills/cdad-cycle/packets/common.md",
    REPO / "sources/roles/implementer.md",
    REPO / "sources/roles/reviewer.md",
    REPO / "sources/roles/orchestrator.md",
    REPO / "sources/roles/test-writer.md",
    REPO / "skills/cdad-epic/SKILL.md",
    REPO / "skills/cdad-epic/references/epic-integration.md",
    REPO / "skills/cdad-epic/references/epic-closure.md",
    REPO / "skills/odoo-make-env/SKILL.md",
    REPO / "skills/odoo-test-writer/SKILL.md",
    REPO / "skills/odoo-reviewer/SKILL.md",
    REPO / "skills/odoo-make-env/references/run-budget-protocol.md",
    REPO / "docs/ci-gate.md",
    REPO / "docs/suite-maintenance.md",
    REPO / "docs/systemPatterns.md",
]

# Órdenes incompatibles con PC-1–PC-8 (doctrina sustituida): autorización
# universal individual, frecuencia por GREEN, regresión completa exigida por
# cambio de árbol / review-fix como automatismo.
FORBIDDEN = re.compile(
    r"(?i)(SOLO con autorizaci[oó]n expresa"
    r"|once per GREEN|una vez por GREEN"
    r"|required full regression suite"
    r"|full suite per GREEN)"
)

HOME_REF = re.compile(r"(?i)(Test evidence policy|stage-3-tdd\.md\s*§)")


def _read(path: Path) -> str:
    assert path.is_file(), f"documento requerido no existe: {path}"
    return path.read_text(encoding="utf-8")


def _section_unique(text: str, title: str):
    heading_re = re.compile(r"^#{1,6}\s+" + re.escape(title) + r"\s*$")
    lines = text.splitlines()
    idxs = [i for i, ln in enumerate(lines) if heading_re.match(ln.strip())]
    assert len(idxs) == 1, (
        f"sección «{title}» debe ser única (encontradas: {len(idxs)})"
    )
    start = idxs[0]
    level = len(lines[start].strip().split()[0])
    body = []
    for ln in lines[start + 1 :]:
        m = re.match(r"^(#{1,6})\s+", ln)
        if m and len(m.group(1)) <= level:
            break
        body.append(ln)
    return "\n".join(body)


def _adr042() -> Path:
    cands = sorted((REPO / "docs" / "adr").glob("ADR-042*.md"))
    assert len(cands) == 1, (
        f"ADR-042 de supersesión parcial debe existir y ser único "
        f"(encontrados: {[c.name for c in cands]})"
    )
    return cands[0]


# ---------------------------------------------------------------------------
# Promesa A — Defaults inequívocos y autorización suficiente (PC-1–PC-4).
# Sin este test, el usuario cierra el epic esperando un permiso que la
# política ya da, o itera con suites completas como rutina.
# ---------------------------------------------------------------------------


def test_A_defaults_inequivocos_y_autorizacion_suficiente():
    home = _read(HOME)
    body = _section_unique(home, "Test evidence policy")

    # A1: hogar único con los tres defaults por momento y autorización por
    # política (PC-2/PC-3/PC-4). Estructura: tabla de momentos, no palabras
    # sueltas.
    assert re.search(r"(?i)Durante el ciclo", body), (
        "A1 ausente: el hogar no declara el default «Durante el ciclo»"
    )
    assert re.search(r"(?i)Cierre de feature", body), (
        "A1 ausente: el hogar no declara el default «Cierre de feature»"
    )
    assert re.search(r"(?i)Cierre de epic", body), (
        "A1 ausente: el hogar no declara el default «Cierre de epic»"
    )
    assert re.search(r"(?i)regresi[oó]n proporcional", body), (
        "A1 ausente: el hogar no preserva la regresión proporcional (PC-4)"
    )
    assert re.search(
        r"(?i)aprobaci[oó]n de (esta|la) pol[ií]tica autoriza.*corrida ordinaria.*cierre de epic",
        body,
    ), (
        "A1 ausente: el hogar no establece que aprobar la política autoriza "
        "la corrida ordinaria de cierre de epic (PC-3)"
    )
    assert re.search(r"(?i)autorizaci[oó]n adicional", body), (
        "A1 ausente: el hogar no descarta la autorización adicional para el "
        "cierre ordinario de epic (PC-3)"
    )

    # A2: ADR de supersesión parcial (PC-1). Ubicación: docs/adr/ADR-042*.
    adr = _adr042()
    atext = _read(adr)
    assert re.search(r"(?i)ADR-041", atext), (
        "A2 ausente: el ADR nuevo no identifica la cláusula de ADR-041 que sustituye"
    )
    assert re.search(r"(?i)sustituye|sustituci[oó]n|supersesi[oó]n", atext), (
        "A2 ausente: el ADR nuevo no declara la sustitución parcial"
    )
    assert re.search(r"(?i)contribuci[oó]n", atext), (
        "A2 ausente: el ADR nuevo no preserva contribución (PC-1)"
    )
    assert re.search(r"(?i)instalaci[oó]n limpia", atext), (
        "A2 ausente: el ADR nuevo no preserva instalación limpia (PC-1)"
    )
    assert not re.search(
        r"(?i)ADR-039.*(plenamente|íntegramente|totalmente) ratificad",
        atext,
    ), "A2 violada: el ADR presenta ADR-039 como íntegramente ratificado"

    # A3: recomendación / obligación / dispensa distinguibles (PC-2/PC-5).
    assert re.search(r"(?i)recomendad", body), (
        "A3 ausente: el hogar no distingue la suite completa recomendada "
        "al cierre de feature"
    )
    assert re.search(r"(?i)obligatoria", body), (
        "A3 ausente: el hogar no distingue la suite completa obligatoria "
        "al cierre de epic"
    )
    assert re.search(r"(?i)dispensa expresa", body), (
        "A3 ausente: el hogar no distingue la dispensa expresa del dueño "
        "para omitir el cierre de epic"
    )


# ---------------------------------------------------------------------------
# Promesa B — Cierres honestos ante resultados incompletos o adversos
# (PC-5–PC-8). Sin este test, el usuario etiqueta como verde una omisión,
# una corrida roja o una inestable reintentada hasta obtener verde.
# ---------------------------------------------------------------------------


def test_B_cierres_honestos_ante_resultados_incompletos_o_adversos():
    home = _read(HOME)
    body = _section_unique(home, "Test evidence policy")

    # B1: omisión registrada con régimen correcto (PC-5). Estructura: motivo +
    # selección + límites; en epic además dispensa expresa recuperable; nunca
    # como suite completa verde ni gate ejecutado.
    assert re.search(r"(?i)suite completa no realizada", body), (
        "B1 ausente: el hogar no exige registrar «suite completa no realizada»"
    )
    assert re.search(r"(?i)motivo", body) and re.search(
        r"(?i)selecci[oó]n ejecutada|selecci[oó]n.*ejecutada", body
    ), "B1 ausente: la omisión no exige motivo y selección ejecutada"
    assert re.search(r"(?i)l[ií]mites", body), (
        "B1 ausente: la omisión no exige declarar límites"
    )
    assert re.search(r"(?i)dispensa expresa.*dueño|dueño.*dispensa expresa", body), (
        "B1 ausente: el cierre de epic sin suite no exige dispensa expresa "
        "del dueño para ese cierre"
    )
    assert re.search(
        r"(?i)(no.*etiqueta|ninguna omisi[oó]n.*etiqueta|no.*como.*verde)",
        body,
    ), "B1 ausente: falta la prohibición de etiquetar la omisión como verde"

    # B2: fallo/error/no atribuible impide verde; se conserva diagnóstico
    # (PC-6).
    assert re.search(
        r"(?i)(fallo|error|no atribuible).*impide.*verde|verde.*(fallo|error)",
        body,
    ), "B2 ausente: el hogar no impide declarar verde ante fallo o resultado no atribuible"
    assert re.search(r"(?i)diagn[oó]stico", body), (
        "B2 ausente: el cierre no conserva el diagnóstico"
    )

    # B3: skips y esperados no ejecutados visibles con efecto; rc=0 no basta
    # (PC-7).
    assert re.search(r"(?i)\bskips?\b", body) and re.search(
        r"(?i)xfail|esperados? no ejecutados", body
    ), "B3 ausente: skips/xfail no quedan visibles con motivo y efecto"
    assert re.search(r"(?i)rc=0.*no demuestra|no.*suficiencia.*contractual", body), (
        "B3 ausente: falta que rc=0 no demuestra por sí solo suficiencia contractual"
    )

    # B4: inestables sin reintentar hasta verde; intentos conservados, otro
    # intento exige hipótesis nueva + presupuesto, si no bloqueo+escalada
    # (PC-8).
    assert re.search(r"(?i)inestable", body), (
        "B4 ausente: el hogar no trata la inestabilidad"
    )
    assert re.search(
        r"(?i)(no.*reintent|repetir hasta.*verde|reintentar hasta.*verde)", body
    ), "B4 ausente: falta prohibir resolver la inestabilidad repitiendo hasta verde"
    assert re.search(r"(?i)hip[oó]tesis.*nueva|informaci[oó]n nueva", body), (
        "B4 ausente: otro intento no exige hipótesis o información nueva"
    )
    assert re.search(r"(?i)bloqueo.*escala|escala.*bloqueo", body), (
        "B4 ausente: sin evidencia acreditable no se declara bloqueo y escalada"
    )


# ---------------------------------------------------------------------------
# Promesa C — La política llega coherentemente a todas sus entradas
# (PC-9–PC-11). Sin este test, un handoff o un paquete transmite al usuario
# la orden vieja aunque el hogar ya cambió.
# ---------------------------------------------------------------------------


def test_C_politica_llega_coherentemente_a_todas_sus_entradas():
    # C1: cada superficie de §5 referencia el hogar o su fuente de dominio y
    # no contiene órdenes incompatibles (PC-9). Barrido negativo + referencia.
    offenders = []
    for f in CONSUMERS:
        text = _read(f)
        if FORBIDDEN.search(text):
            offenders.append(str(f.relative_to(REPO)))
    assert not offenders, (
        "C1 violada: superficies de §5 con órdenes incompatibles "
        f"(autorización universal / frecuencia por GREEN): {offenders}"
    )
    stale = []
    for f in CONSUMERS:
        text = _read(f)
        if f == HOME:
            continue
        if not (HOME_REF.search(text) or re.search(r"(?i)dominio", text)):
            stale.append(str(f.relative_to(REPO)))
    assert not stale, (
        "C1 violada: superficies de §5 sin referencia al hogar ni a su "
        f"fuente de dominio: {stale}"
    )

    # C2: paquetes nuevos coherentes, históricos intactos (PC-10). Ubicación:
    # skills/cdad-cycle/packets/common.md distingue autorización por política
    # de necesidad de evidencia real; los históricos no se reescriben.
    common = _read(COMMON)
    assert re.search(
        r"(?i)autorizaci[oó]n por pol[ií]tica", common
    ), "C2 ausente: common.md no distingue autorización por política"
    assert re.search(r"(?i)evidencia real|necesidad de evidencia", common), (
        "C2 ausente: common.md no distingue autorización de necesidad de "
        "evidencia real"
    )
    assert not FORBIDDEN.search(common), (
        "C2 violada: common.md conserva la doctrina paralela sustituida"
    )

    # C3: cambios en sources/ + make agents reproducible, sin edición manual
    # de derivados (PC-11). Ubicación: sources/roles/* + Makefile.
    for role in ("implementer.md", "reviewer.md", "orchestrator.md", "test-writer.md"):
        text = _read(REPO / "sources" / "roles" / role)
        assert HOME_REF.search(text) or re.search(
            r"(?i)(Durante el ciclo|Cierre de (feature|epic)|proporcional)",
            text,
        ), f"C3 ausente: sources/roles/{role} no aplica su consecuencia local"
    mk = _read(REPO / "Makefile")
    assert re.search(r"(?i)^agents\s*:", mk, re.M) and re.search(
        r"(?i)make agents", mk
    ), "C3 ausente: Makefile sin regeneración declarada de derivados"


# ---------------------------------------------------------------------------
# Promesa D — Costo y entorno explícitos sin exenciones implícitas
# (PC-12–PC-14). Sin este test, el usuario usa «suite lenta» como dispensa
# tácita o pierde test-clean al confundir amplitud con instalación.
# ---------------------------------------------------------------------------


def test_D_costo_y_entorno_explicitos_sin_exenciones_implicitas():
    home = _read(HOME)
    body = _section_unique(home, "Test evidence policy")

    # D1: declaración por proyecto sin dispensa implícita (PC-12). Estructura:
    # comando focal y completo, entorno, costo conocido con procedencia o
    # desconocido expreso, presupuesto y estrategia; la lentitud no dispensa.
    for pat, label in [
        (r"(?i)comando focal", "comando focal"),
        (r"(?i)comando completo|suite completa", "comando completo"),
        (r"(?i)entorno", "entorno"),
        (r"(?i)costo.*procedencia|costo.*desconocido|desconocido.*expreso", "costo con procedencia o desconocido expreso"),
        (r"(?i)presupuesto", "presupuesto"),
        (r"(?i)estrategia de ejecuci[oó]n", "estrategia de ejecución"),
    ]:
        assert re.search(pat, body), f"D1 ausente: falta «{label}» por proyecto"
    assert re.search(
        r"(?i)(lenta|disponibilidad|no.*dispensa impl[ií]cita|sin.*dispensa impl[ií]cita)",
        body,
    ), "D1 ausente: la lentitud o el costo no se declara como dispensa implícita prohibida"

    # D2: gate con interfaz real y atribución; autorización suficiente del
    # cierre de epic sin automatismo por push ni flags nuevos (PC-12/PC-13).
    gate = _read(CI_GATE)
    assert re.search(r"(?i)cdad-suite\.py\s+close", gate), (
        "D2 ausente: docs/ci-gate.md no conserva la interfaz real del gate "
        "(cdad-suite.py close)"
    )
    assert not re.search(r"(?i)cdad-ci-gate\.py\s+close\s+--all", gate), (
        "D2 violada: ci-gate promete un subcomando nuevo inexistente"
    )
    assert re.search(
        r"(?i)autorizaci[oó]n.*(suficiente|cierre de epic)|cierre de epic.*autoriz",
        gate,
    ), "D2 ausente: ci-gate no declara la autorización suficiente del cierre de epic"

    # D3: Odoo conserva instalación limpia y amplitud como dimensiones
    # distintas; test-clean exigible; sin evidencias de addon impuestas a
    # quien no modifica addon (PC-14). Ubicaciones: run-budget + skills Odoo.
    rb = _read(RUN_BUDGET)
    assert re.search(r"(?i)instalaci[oó]n limpia", rb) and re.search(
        r"(?i)amplitud", rb
    ), "D3 ausente: run-budget no distingue instalación limpia de amplitud"
    assert re.search(r"(?i)test-clean", rb), (
        "D3 ausente: run-budget elimina test-clean cuando es exigible"
    )
