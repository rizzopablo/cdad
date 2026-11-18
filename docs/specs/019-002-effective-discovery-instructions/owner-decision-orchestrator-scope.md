# Owner decision — orchestrator scope (2026-11-15)

Pablo (owner), verbatim: "no puedes prohibirle al orquestador tantas cosas, es el agente
con el que yo hablo y necesito que pueda resolver situaciones. cada agentes tiene su rol y
el orquestador es el encargado de hacer que cada uno realice su parte. lo que no debe hacer
nunca el orquestador es escribir los tests y el producto (codigo o lo que sea) pero no se le
puede impedir lo demas."

Effect on 019-002:
- The orchestrator MAY read code, run the product and investigate to resolve situations.
- Its only hard prohibition is writing tests or the product (code or any deliverable).
  Existing non-delegable owner approvals are unchanged (they are the owner's, not a
  restriction on investigation).
- PC-1's "does not perform technical investigation" is superseded by this decision.
  What remains required: technical findings that ground a decision or the spec are
  recorded as attributed technical evidence (who found it, how), and the architect is
  consulted when an independent technical judgment or the spec draft is needed.
- The fix-007 F1/F6 and fix-008 "do not investigate" wording is withdrawn (fix-009).
- run1/run2 findings F1 and the C5 "routing" criterion are reclassified: not an error
  by themselves; the error is only an unrecorded or unattributed technical claim.
