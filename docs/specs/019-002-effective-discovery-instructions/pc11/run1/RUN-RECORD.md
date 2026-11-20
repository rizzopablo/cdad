# PC-11 run record — run1 (producer: orchestrator; NOT the verdict)

- Runtime: opencode 2.2.7, `opencode run --agent cdad-orchestrator --model openai/gpt-6.1-terra`, scratch project `~/<workspace>/tmp/cand019` with project-local `.opencode/agents` (candidate generated agents, no `model:` line) and `.opencode/skills/cdad-cycle`, `cdad-spec-and-test` copied from repository HEAD `732a7275` (candidate). No installation, config or global agent was touched.
- model_configured for the orchestrator: opencode-go/deepseek-v4.1-flash#max (global); model_used: openai/gpt-6.1-terra via --model because the Go plan was over weekly quota (error preserved in t3-runtime-probe.jsonl). Subagents (architect, reviewer) have no model line in the candidate files and inherited the run model unless the runtime reports otherwise (not verified).
- Precedence evidence: the orchestrator listed the task tool's subagent descriptions, which showed the candidate text ("Targeted technical consultation (returned to the orchestrator)…"), not the global text.
- Effective files and hashes: `effective-agents.sha256`, `effective-skills.sha256`. Packets: this scratch project uses no frozen repository packets; the agents were prompted by the orchestrator's own Task prompts (see transcripts).
- Protected inputs (written and write-protected before the run): `inputs/*.txt`, digests in `inputs/MANIFEST.sha256`:
  J1-need (096b2bdf…), T2-partial (d2d111cb…, intended C1/C2), T3-assumption (ac255345…, intended C5), T4-correction (bcc6456a…, intended C3), T5-open-choice (fbfa65d9…, intended C4), T6-resolve (14c9577a…, resolves C4).
- Transcripts: `run1/transcript-turn1..6.txt` (one file per owner turn, rendered from the raw JSON logs in `logs/run1-turn*.jsonl`).
- Resulting artifacts: `run1/artifacts-docs/` (scratch docs/ at end) and `run1/scratch-git-history.txt`.
- Not simulated: J8 approval (per protocol).
- Producer notes (observations, not verdicts): turn 1 the orchestrator itself read `notes/*.py` and stated technical facts, and asked questions through the `question` tool (no answer was available in headless mode); turn 2 it proceeded on recommended defaults and delegated discovery+draft to the architect in one step; no architect consultation returned as a separate role-report before drafting.
