# Capabilities inventory — effective capabilities and portable fallback

This is a short **inventory**, not a manual. It records how the orchestrator finds
the capabilities that **already exist** in the loaded version to present **plans**,
**files**, **previews** and **diffs**, and it declares the **portable fallback** by
**files or links** — the minimum already possible. Contract: `capabilities-inventory-v1`.

It does **not** create a dashboard, a scheduler or a second source of state, and it
does **not** implement any external surface. It is an inventory: it classifies what
exists, it does not build anything.

## 1. The four classes and the criterion that assigns them

Every capability is declared in **exactly one** of four classes. The criterion that
assigns a capability to its class is the **evidence available now**, never an
expectation:

| Class | Criterion — how a capability is assigned to this class |
|---|---|
| **observed** | verified in the current version/configuration by exercising the capability **now**: its own command or endpoint returns a result. |
| **documented** | asserted by a **versioned source** (a reference, a schema, or a tool's own help) for the current version/configuration, but **not** re-run now. |
| **not available** | the capability **does not exist** in the current version/configuration. |
| **unknown** | **not** verified and **not** documented for the current version/configuration; it is never promoted to available by assumption. |

The classification is a **map** over evidence, applied the same way every time: what
is verified now is **observed**; what a versioned source asserts is **documented**;
what does not exist is **not available**; and everything else is **unknown** — what
was not verified is never invented.

## 2. Capabilities for presenting plans, files, previews and diffs

The surfaces to cover are **plans**, **files**, **previews** and **diffs**. The
capabilities found are grouped by class.

### 2.1 Observed (verified in the current version/configuration)

- **Presenting files** — by the **path** of the file, and by a **link** to it.
- **Presenting a diff** — by the version-control tool's diff over the **files** (a
  file, or a link to the rendered diff).
- **Presenting a plan** — by writing the plan as a **file** (the approved plan
  document) and referencing it by path or link; the plan is read from that file.
- **Presenting a preview** — by a **file**/**link** plus a short explanation.
- **OpenChamber's installation and access mechanism** — a CLI on `PATH` and a live
  server (verified). This is the installation and access mechanism, not a
  presentation surface for the agent.

### 2.2 Documented (asserted by a versioned source, not re-run here)

- The **version disposition** and the **CLI surfaces** are asserted by the skill
  references (`orientation.md`, `project-start.md`); this inventory **cites** them
  and does not repeat their checks.
- OpenChamber's **CLI subcommands** (`session`, `projects`, `control`, `schedule`,
  `connect-url`, `logs`) as asserted by the tool's own help.

### 2.3 Not available (does not exist in the current version/configuration)

- A **dedicated dashboard**, a **scheduler** or a **second source of state** — none
  exists, and none is created by this feature.
- A **dedicated preview surface** richer than files/links — there is no such
  capability in the product.

### 2.4 Unknown (not verified, not documented)

- OpenChamber's **stable contract agent↔surface** for notes/previews/diffs — this is
  **unknown**: it is **not** verified. See §4.

## 3. Version/config binding (by reference)

This inventory is **bound to version/configuration**: it describes the capabilities
of the **loaded version** and its **configuration**, and it is read against them —
not against an assumed one. The version disposition is **cited by reference**
(`orientation.md` §4: the installed version check with its verdicts
`COHERENT`/`DRIFT`/`UNKNOWN`/`NO-PROJECT-AGENTS`); this inventory does **not** repeat
that check. It carries **no** environment-specific value: no host path, no provider,
no model, no server and no raw session id.

A capability whose class changes with either the version or the configuration is
**re-read**, never assumed.

## 4. Portable fallback and the chain agent → artifact → review

When no richer surface is available, the **portable fallback** is the minimum
already possible: present a **plan**, a **file**, a **preview** or a **diff** as a
**file** or a **link**, plus a short explanation. It needs no dedicated UI, so it
works in any environment and for any version/configuration.

**Chain:** agent → artifact → review, by **files** or **links**.

- **agent** — the role produces the artifact (the plan, the file, the rendered diff).
- **artifact** — the artifact is written to a **file**, or referenced by a **link**.
- **review** — the reviewer reads that **file** or follows that **link**; the review
  is done over the file/link, not over a UI surface.

This chain is the **demonstration** of the portable fallback: without any UI, the
path agent → artifact → review by files/links already works.

### OpenChamber — verified consumer, not a dependency

**OpenChamber** is a **verified consumer** of its **installation** and its **access
mechanism** (a CLI on `PATH`; a live server answering HTTP 200). Its **stable
contract agent↔surface** for notes/previews/diffs is **NOT verified** — it is
**unknown** — so a complex UI integration is a **proposed later** item and is **not**
committed here. **No** integration of OpenChamber or OnlyOffice is implemented or
announced; **no** dashboard, scheduler or second source of state is created.

## 5. Boundaries

- This is an **inventory**, not a manual: it classifies capabilities, it does not
  document how to operate the CLI (that is `orientation.md`) nor how to start and
  re-enter (that is `project-start.md`).
- It does **not** redefine the start procedure and does **not** create another
  bootstrap.
- It does **not** promise a stable agent↔surface contract for OpenChamber, and it
  does **not** create a dashboard, a scheduler or a second source of state.
