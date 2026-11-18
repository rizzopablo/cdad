# Deployment record — 019-004

Authorized by Pablo on 2026-11-17 (“despliega localmente”), independently of the
feature closure, which stands on the isolated-HOME evidence.

- Backup: `~/clawd/archive/cdad-deploy-019-004-20261117-094730`
  (installed agents, skill trees and manifest, plus the model records before).
- Ten opencode agent conflicts were resolved with `agent-overlay.py merge`, so the
  staged bodies were installed while the configured `model:` lines survived.
- One skill document (`handoff-prompts.md`) was overwritten from the repository
  because the installed copy was a stale manual deploy of the same file.
- `install.sh` completed: 11 cdad agents present, verification PASS.
- `install.sh --check`: **PASS**, 379 artifact groups in sync.
- All 22 agent model records are unchanged after the deployment.
- The installed CLI now answers `layout` (resolves this project as legacy `docs`)
  and `intake --help`.

Limit: the deployment was performed after the 019-004 suite run; it is not the
evidence for that closure. A fresh-role journey on the deployed copy remains a
bounded observation the owner may request separately.
