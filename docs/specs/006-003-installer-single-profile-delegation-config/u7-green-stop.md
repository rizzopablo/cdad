I'll start by reading the approved contract and the RED test that defines my obligations.
Now let me examine the current `install.sh` implementation, especially the manifest python and `uninstall_by_manifest`.
Let me first establish the baseline: RED state of the U7 test and current state of the gate tests.
This is a critical finding. Let me examine the review-5 B3 fixture and prove the conflict empirically before going further.
Now I understand the code. Let me implement the prune. First, the state and helpers:
Now the manifest python — consuming the prune plan:
Now the shared-rule refactor of `uninstall_by_manifest`:
Now wire it into `main` and update the header documentation:
Focal is GREEN. Now the gates — starting with the oracle I suspect opposes PD-6a:
Decisive evidence obtained. Let me measure the full blast radius across all install.sh-invoking tests:
One failure in the batch (`u6`, a known tight 2s-timeout test). Let me check it in isolation plus the consistency gate:
Let me measure the precise B3-vs-PD-6a opposition black-box (independent of the test's own rc assertion):
I have decisive, measured evidence of the contradiction. Let me preserve the implementation as a patch and restore the tree to HEAD:
## Role report — implementer / GREEN · `006-003-installer-single-profile-delegation-config` U7

### 0. Result — **STOPPED. `tests/test_install_review5_regressions.py::TestReview5WithdrawnAgent` (oracle aprobado) se opone frontalmente a PD-6a. No hay commit. Árbol devuelto a HEAD.**

Contract verified: `docs/specs/006-003-…/spec.md` sha256 `c25ebf0e0c7867c03de072439128e7a77e4b2a7dcd7f52228535ea9785d18890` (matches packet). Write scope respected: **only `install.sh`** (now reverted); `tests/` untouched (`git diff --stat HEAD -- tests/` → empty); `docs/planning/` and `findings/` (untracked, not mine) untouched; no `--no-verify`, no stash, no push, **no commit** — HEAD is still `ef78451`.

### 1. What I built (and measured) before stopping

Minimal implementation of PD-6a..e in `install.sh` (+194/−34), focal **green**: `python3 -m pytest tests/test_006_003_u7_prune_obsolete.py -q` → **6 passed in 86.52s** (baseline before/after revert: `4 failed, 2 passed`).

- `owned_removal_state` / `install_root_abs`: the removal rule of `uninstall_by_manifest` extracted **once** and shared (nothing duplicated); `uninstall_by_manifest` refactored onto it with byte-identical semantics (incl. symlink and empty-recorded-sha cases).
- `prune_owned_obsolete`: candidates = previous `artifacts`+`pending_removal` entries neither redeployed (`OWNED_ABS`, tracked in **both** modes so `--dry-run` previews the same bajas) nor conflicted; `removable` → `rm` + drop from manifest, `modified` → PRESERVE + `CONFLICT` + **stay registered** (PD-6b), `absent` → no-op. Unregistered files are never read (PD-6c). `--dry-run` lists via `do_run` and writes nothing (PD-6d). The manifest-reading python receives **`INSTALL_ROOT`** and resolves absolute/relative recorded paths (PD-6e); the writing python consumes the plan (`%%KEPT%%`).

### 2. The contradiction (the reason for the stop)

`tests/test_install_review5_regressions.py:372-439` (approved oracle, review-5 B3, 004-001 T5) pins **exactly the opposite** of PD-6a for the same input (a registered own file, byte-identical, no longer deployed, not conflicted):

| B3 asserts | PD-6a requires |
|---|---|
| `old_installed.is_file()` (line 400) — the withdrawn file **survives** | el archivo **se retira** del disco |
| `--check` rc **≠ 0** naming `PENDING-REMOVAL` (line 412-424) | `--check` **no** lo reporta, rc **0**, PASS |
| (compatible) `--uninstall` retires it | (compatible) |

Measured, not inferred — with the implementation in place:

```
$ python3 -m pytest tests/test_install_review5_regressions.py -q
FAILED tests/test_install_review5_regressions.py::TestReview5WithdrawnAgent::test_review5_b3_…
1 failed, 4 passed in 68.53s
```

Black-box measurement of the B3 scenario itself (`python3 /tmp/opencode/measure_b3_vs_pd6a.py`, product copy + staging in the copy, root redirected):

```
withdrawn staged source : agents/opencode/cdad-architect-odoo.md
deployments registered  : ['.config/opencode/agents/cdad-architect-odoo.md']
install#2 rc            : 1
   | REMOVE (own obsolete: no longer deployed, bytes match the recorded sha256) …/.config/opencode/agents/cdad-architect-odoo.md
   | Obsolete prune: 1 own file(s) retired, 0 preserved …
   | Verify: FAIL — expected 11 cdad agents, found 10
still on disk           : []
--check rc              : 0
   | Check: PASS (395 artifact groups in sync with staging/skills)
```

So PD-6a's rule does retire the withdrawn staged agent (B3's two claims are both false under it), **and** surfaces a third, previously unrecorded interaction: retiring a *staged* artifact makes the installer's own post-install verification fail (`Verify: FAIL — expected N of N cdad agents present`) → install rc=1. That is why the test fails first on its `rc==0` assert, but the behavioural opposition is independent of it.

Why I did not resolve it myself: the spec/plan say "cada entrada que hoy queda como `pending_removal`" (no provenance scope), the U7 RED declares "Any product source works" (generality), and the U7 RED commit (`3a04ad1`) touched **no** pre-existing test although plan A-1 requires coupled oracles to be reformulated **declaring the replacement** — and `discovery.md` (§1.6, R1) only declared review-5 **B4** as coupled. Neither reformulating B3 (a test edit — not mine) nor scoping PD-6 by an invented rule (gaming) is mine to do.

### 3. Other gates, measured with the implementation in place

| Gate | Result |
|---|---|
| `tests/test_006_003_u7_prune_obsolete.py` (6) | **6 passed** (HEAD: 4 failed/2 passed) |
| `tests/test_install_ownership.py` (11) + `test_005_004_t2_installer_claims.py` (8) + `test_006_003_u2_…` (7) + `test_006_003_u4_…` (8) | **34 passed in 195.07s** |
| `tests/test_install_review5_regressions.py` (5) | **1 failed (B3)**, 4 passed |
| other 31 modules invoking `install.sh` (`grep -l "install.sh" tests/*.py`) | **232 passed, 1 failed** — `test_006_003_u6_server_credential.py::…redirects_the_source` (`'timeout' != 'completed'`, "did not answer within 2.0 seconds"); in isolation: **6 passed in 11.39s** (declared DT-9 2 s margin, unrelated code path) |
| `bash tests/validate-consistency.sh` | **168 PASS / 1 FAIL — F011 only** (declared by the packet) |

### 4. Disposition (orchestrator/owner decides — two options)

- **(a) Reformular el oráculo B3** (test-writer RED, declarando el reemplazo, plan A-1) y **además** corregir la verificación del instalador (`Verify: FAIL` con el staged set retirado). Costo: dos unidades, no "retiro puro".
- **(b) Enmendar PD-6/D6 (A-6) para acotar el retiro a lo no-staged** (`source` que no es `agents/*`). Justificación con evidencia ya aprobada: los dos casos reales del hallazgo son no-staged — el marcador de perfil retirado (`source`: `install.sh (model profile state)`) y las dos referencias retiradas de 006-002 (espejo de `skills/`), `discovery.md:186-190`, `execution.md:213-214` — y el conjunto staged tiene su propia disposición fijada por B3 + la verificación de instalación. Con un filtro de 2 líneas (`case "$source" in agents/*) continue ;; esac`) **PD-6a..e quedan verdes y B3 sigue verde sin tocar ningún test**. Es la que recomiendo.

### 5. Estado del árbol y recuperación del trabajo

`git checkout -- install.sh` → `git status --short` sólo muestra los dos untracked ajenos; `install.sh` = `601b7e53…` (HEAD). El patch exacto (346 líneas) está en **`/tmp/opencode/u7-prune.diff`** (`git apply /tmp/opencode/u7-prune.diff` re-aplica la implementación completa) y en el anexo de este reporte. La medición reutilizable está en `/tmp/opencode/measure_b3_vs_pd6a.py`.

**Límites honestos:** (1) el `u6` rojo del batch de 31 módulos no lo reproduje sobre árbol limpio en el mismo contexto de carga (mi cambio no toca el despachador; verde aislado) — queda declarado, no atribuido; (2) F011 es el drift de HOME ya declarado en el packet; (3) no corrí la suite completa (política del paquete: la corre quien cierra).

### Anexo — patch exacto (idéntico a `/tmp/opencode/u7-prune.diff`)

```diff
diff --git a/install.sh b/install.sh
index 3b08e40..166d60e 100755
--- a/install.sh
+++ b/install.sh
@@ -24,8 +24,10 @@
 # modified owned file — agents, skills and the guard share the SAME
 # conflict-and-preserve policy, review-5 B2 — or a symlink at a destination)
 # and preserve the local bytes; files owned by a previous install that this
-# install no longer deploys stay registered as pending_removal (visible to
-# --check, retired by --uninstall; review-5 B3 — a reinstall never forgets).
+# install no longer deploys are RETIRED when their bytes still match the
+# recorded sha256 (006-003 U7/D6: the install retires its own obsoletes) and
+# stay registered as pending_removal when they were modified locally (visible
+# to --check, retired by --uninstall; review-5 B3 — a reinstall never forgets).
 # This is how a pre-T6 root's public-layout copies surface after a PD-9
 # reinstall: pending_removal, retired by --uninstall. --uninstall removes
 # exactly the manifest entries (artifacts + pending records), preserving a
@@ -103,6 +105,19 @@ OWNERSHIP_MANIFEST="$INSTALL_ROOT/$INSTALL_MANIFEST_NAME"
 OWNED=()
 # Conflicts detected during THIS run: "rel<TAB>reason".
 CONFLICTS=()
+# 006-003 U7/D6: the obsolete prune needs to know which DESTINATIONS this run
+# deploys (in BOTH modes: --dry-run must preview the same bajas) and which ones
+# it already disclosed as conflicts. Keyed by absolute path, so a manifest that
+# recorded absolute paths and one that recorded install-root-relative paths
+# describe the SAME destination.
+declare -A OWNED_ABS=()
+declare -A CONFLICT_ABS=()
+# Obsolete-retirement plan of this run (PD-6a/D6): keys retired from disk and
+# from the manifest, and entries preserved (locally modified) that must stay
+# REGISTERED. Consumed by write_ownership_manifest; "" until the prune runs.
+PRUNED=()
+KEPT=()
+PRUNE_PLAN_FILE=""
 # PD-14/INV-7: deterministic identifier of what this install deployed, resolved
 # once per run (installation_version) and published at the install root.
 INSTALL_VERSION=""
@@ -614,16 +629,49 @@ write_version_marker() {
   log "VERSION marker: $marker = $version"
 }
 
+# install_root_abs <recorded-path> — resolve a path RECORDED in the ownership
+# manifest against the install root (PD-6e): an absolute path is already
+# resolved, a relative one resolves under the — possibly redirected — root.
+install_root_abs() {
+  case "$1" in
+    /*) printf '%s' "$1" ;;
+    *)  printf '%s/%s' "$INSTALL_ROOT" "$1" ;;
+  esac
+}
+
+# owned_removal_state <path> <recorded-sha256> — the ONE rule that decides what a
+# registered own path is entitled to right now. Shared by --uninstall
+# (review-5 E1) and the obsolete prune (006-003 U7/D6) instead of duplicating it:
+#   removable — a symlink, or a regular file whose bytes match the recorded
+#               sha256 (also when no digest was recorded: there is no evidence of
+#               a local change to preserve — the historical --uninstall rule)
+#   absent    — nothing at that path (idempotent)
+#   modified  — a regular file whose bytes differ from a RECORDED digest: the
+#               user changed it after the install, so it is never discarded.
+owned_removal_state() {
+  local path="$1" recorded="$2" actual
+  if [ -L "$path" ]; then printf 'removable'; return 0; fi
+  if [ ! -f "$path" ]; then printf 'absent'; return 0; fi
+  actual="$(sha256_of "$path")"
+  if [ -z "$recorded" ] || [ "$actual" = "$recorded" ]; then printf 'removable'; return 0; fi
+  printf 'modified'
+}
+
 record_owned() {  # abs_path source — register an owned file for the ownership manifest
-  [ "$DRY_RUN" -eq 1 ] && return 0
   local abs="$1" source="$2" sha rel
-  sha="$(sha256_of "$abs")"
   rel="${abs#"$INSTALL_ROOT"/}"
+  # Tracked in BOTH modes (the manifest itself is not): the obsolete prune needs
+  # to know which destinations this run deploys, and --dry-run has to preview the
+  # same bajas it would perform.
+  OWNED_ABS["$abs"]=1
+  [ "$DRY_RUN" -eq 1 ] && return 0
+  sha="$(sha256_of "$abs")"
   OWNED+=("$rel"$'\t'"$sha"$'\t'"$source")
 }
 
 add_conflict() {  # rel reason — report and preserve (PD-7: never overwrite/delete)
   local rel="$1" reason="$2"
+  CONFLICT_ABS["$(install_root_abs "$rel")"]=1
   CONFLICTS+=("$rel"$'\t'"$reason")
   if [ "$DRY_RUN" -eq 1 ]; then
     log "DRY-RUN CONFLICT: $rel — preserved ($reason)"
@@ -739,6 +787,7 @@ stage_one_destination() {
     if [ "$DRY_RUN" -eq 1 ]; then
       log "DRY-RUN COPY $srel -> $dst"
       log "DRY-RUN STAGED-UPDATE $rel staging moved on; would redeploy the staged bytes"
+      record_owned "$dst" "$srel"
     else
       do_run "COPY (staging regenerated) $srel -> $dst" cp -p "$STAGING_DIR/$srel" "$dst"
       record_owned "$dst" "$srel"
@@ -747,6 +796,7 @@ stage_one_destination() {
   fi
   if [ "$DRY_RUN" -eq 1 ]; then
     log "DRY-RUN COPY $srel -> $dst"
+    record_owned "$dst" "$srel"
     return 0
   fi
   dst_dir="$(dirname "$dst")"
@@ -803,6 +853,7 @@ stage_owned_file() {
     if [ "$DRY_RUN" -eq 1 ]; then
       log "DRY-RUN COPY $source_label -> $dst"
       log "DRY-RUN UPDATE $rel source moved on; would redeploy the source bytes"
+      record_owned "$dst" "$source_label"
     else
       do_run "COPY (source moved on) $source_label -> $dst" cp -p "$src" "$dst"
       record_owned "$dst" "$source_label"
@@ -814,6 +865,7 @@ stage_owned_file() {
   fi
   if [ "$DRY_RUN" -eq 1 ]; then
     log "DRY-RUN COPY $source_label -> $dst"
+    record_owned "$dst" "$source_label"
     return 0
   fi
   dst_dir="$(dirname "$dst")"
@@ -864,10 +916,25 @@ write_ownership_manifest() {
     rm -f "$stream_file"
     die "Cannot write the ownership-manifest stream temp file: $stream_file"
   fi
-  python3 - "$STAGING_MANIFEST" "$OWNERSHIP_MANIFEST" "$stream_file" "$INSTALL_VERSION" <<'PY' || status=$?
+  python3 - "$STAGING_MANIFEST" "$OWNERSHIP_MANIFEST" "$stream_file" "$INSTALL_VERSION" "$PRUNE_PLAN_FILE" <<'PY' || status=$?
 import json, os, sys
 staging_path, out_path, stream_path, install_version = (
     sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
+# 006-003 U7/D6: the obsolete-retirement plan of the prune pass ("" when it did
+# not run, i.e. there was no previous manifest): the keys retired from disk (they
+# must leave the manifest) and the entries preserved because they were modified
+# locally (they must STAY registered — PD-6b/INV-2).
+prune_path = sys.argv[5] if len(sys.argv) > 5 else ""
+pruned, kept = set(), {}
+if prune_path and os.path.exists(prune_path):
+    blob = open(prune_path, encoding="utf-8").read()
+    pruned_blob, _, kept_blob = blob.partition("%%KEPT%%")
+    pruned = {line for line in pruned_blob.splitlines() if line.strip()}
+    for line in kept_blob.splitlines():
+        if not line.strip():
+            continue
+        rel, sha, source = line.split("\t", 2)
+        kept[rel] = {"sha256": sha, "source": source}
 stream = open(stream_path, encoding="utf-8").read().split("%%CONFLICTS%%", 1)
 artifacts = {}
 for line in stream[0].splitlines():
@@ -905,13 +972,16 @@ if os.path.exists(out_path):
                 previous_pending[rel] = record
 pending = {}
 for rel, record in sorted(previous.items()):
-    if rel in artifacts or rel in conflict_paths:
+    if rel in artifacts or rel in conflict_paths or rel in pruned:
         continue
     pending[rel] = {"sha256": record.get("sha256", ""), "source": record.get("source", "")}
 for rel, record in sorted(previous_pending.items()):
-    if rel in artifacts or rel in conflict_paths:
-        continue  # re-adopted or conflicted this run
+    if rel in artifacts or rel in conflict_paths or rel in pruned:
+        continue  # re-adopted, conflicted or retired this run
     pending[rel] = {"sha256": record.get("sha256", ""), "source": record.get("source", "")}
+# PD-6b: an obsolete own file the prune PRESERVED (modified locally) stays
+# registered — a conflict disclosure never unregisters a file.
+pending.update(kept)
 staging = json.load(open(staging_path, encoding="utf-8"))
 manifest = {
     "manifest_version": 1,
@@ -932,6 +1002,10 @@ with open(tmp_path, "w", encoding="utf-8") as fh:
 os.replace(tmp_path, out_path)
 PY
   rm -f "$stream_file"
+  if [ -n "$PRUNE_PLAN_FILE" ]; then
+    rm -f "$PRUNE_PLAN_FILE"
+    PRUNE_PLAN_FILE=""
+  fi
   if [ "$status" -ne 0 ]; then
     die "Cannot write the ownership manifest: $OWNERSHIP_MANIFEST (stream reader exit $status)"
   fi
@@ -1069,6 +1143,94 @@ install_user_config() {
   write_server_env_example "$config_dir/opencode-server.env.example"
 }
 
+# ---------------------------------------------------------------------------
+# Obsolete own files (006-003 U7/D6: PD-6a..e)
+# ---------------------------------------------------------------------------
+# The installer retires ITS OWN obsolete files. Candidate = every entry a
+# previous install registered (artifacts or pending_removal) that this run
+# neither redeploys nor discloses as a conflict; --uninstall's rule decides
+# (owned_removal_state, shared — never duplicated):
+#   removable (bytes match the recorded sha256) -> retired from DISK and from the
+#       manifest: the install no longer deploys it, so keeping it registered
+#       forever would leave --check reporting a PENDING-REMOVAL nobody resolves;
+#   modified -> PRESERVED, disclosed as CONFLICT and kept REGISTERED (PD-6b):
+#       a local change is never discarded by an install (INV-2);
+#   absent -> nothing to do (idempotent; the registered entry is left as it is).
+# A file the manifest does NOT register is never read nor written, so it cannot
+# be touched even while the prune is active (PD-6c/INV-2), and the user config
+# files are not registered either (A-3). --dry-run announces every baja through
+# do_run and performs none.
+prune_owned_obsolete() {
+  local prev="$OWNERSHIP_MANIFEST"
+  [ -f "$prev" ] || return 0
+  local reg_path
+  reg_path="$(mktemp)" || die "Cannot create the obsolete-prune registration temp file"
+  # PD-6e: the manifest-reading python receives INSTALL_ROOT and resolves every
+  # RECORDED path against it — absolute paths stay as they are, relative ones
+  # resolve under the (possibly redirected) root. The hash compares the bytes on
+  # DISK, and `owned_removal_state` decides with the recorded digest.
+  python3 - "$prev" "$INSTALL_ROOT" "$reg_path" <<'PY' || { rm -f "$reg_path"; die "Cannot read the ownership manifest: $prev"; }
+import json, os, sys
+manifest_path, root, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
+try:
+    data = json.load(open(manifest_path, encoding="utf-8"))
+except (OSError, ValueError):
+    raise SystemExit(0)
+records = {}
+for section_name in ("artifacts", "pending_removal"):
+    section = data.get(section_name)
+    if not isinstance(section, dict):
+        continue
+    for rel, record in sorted(section.items()):
+        if isinstance(record, dict) and rel not in records:
+            records[rel] = record
+with open(out_path, "w", encoding="utf-8") as out:
+    for rel, record in sorted(records.items()):
+        absolute = rel if os.path.isabs(rel) else os.path.join(root, rel)
+        out.write("%s\t%s\t%s\t%s\n" % (absolute, rel, record.get("sha256", ""), record.get("source", "")))
+PY
+  local abs rel sha source state preserved=0 plan_path
+  local -A pruned_abs=()
+  while IFS=$'\t' read -r abs rel sha source; do
+    [ -n "$rel" ] || continue
+    [ -n "${OWNED_ABS[$abs]:-}" ] && continue     # this run deploys it: not obsolete
+    [ -n "${CONFLICT_ABS[$abs]:-}" ] && continue  # already reported and preserved
+    if [ -n "${pruned_abs[$abs]:-}" ]; then
+      PRUNED+=("$rel")                            # same destination, another key
+      continue
+    fi
+    state="$(owned_removal_state "$abs" "$sha")"
+    case "$state" in
+      absent) continue ;;
+      removable)
+        do_run "REMOVE (own obsolete: no longer deployed, bytes match the recorded sha256) $abs" rm -f -- "$abs"
+        pruned_abs["$abs"]=1
+        PRUNED+=("$rel")
+        ;;
+      modified)
+        preserved=$((preserved + 1))
+        KEPT+=("$rel"$'\t'"$sha"$'\t'"$source")
+        add_conflict "$rel" "obsolete own file modified locally since the recorded install (registered $sha); PRESERVED and kept registered"
+        ;;
+    esac
+  done < "$reg_path"
+  rm -f "$reg_path"
+  log "Obsolete prune: ${#PRUNED[@]} own file(s) retired, $preserved preserved (locally modified — explicit resolution needed)"
+  [ "$DRY_RUN" -eq 1 ] && return 0
+  # The plan for write_ownership_manifest: keys to drop, then the entries that
+  # must stay REGISTERED (PD-6b).
+  plan_path="$(mktemp)" || die "Cannot create the obsolete-prune plan temp file"
+  if ! {
+    printf '%s\n' "${PRUNED[@]}"
+    printf '%s\n' '%%KEPT%%'
+    printf '%s\n' "${KEPT[@]}"
+  } > "$plan_path"; then
+    rm -f "$plan_path"
+    die "Cannot write the obsolete-prune plan: $plan_path"
+  fi
+  PRUNE_PLAN_FILE="$plan_path"
+}
+
 # ---------------------------------------------------------------------------
 # Uninstall operations (cdad-owned paths only)
 # ---------------------------------------------------------------------------
@@ -1147,7 +1309,7 @@ uninstall_cdad() {
 # No confirmation prompt: the manifest IS the explicit resolution of what is ours.
 uninstall_by_manifest() {
   local reg_path keep_file status=0 total=0 removed=0 preserved=0
-  local key rel sha source path actual
+  local key rel sha source path
   local -a keep_artifacts=() keep_pending=()
   reg_path="$(mktemp)" || die "Cannot create the uninstall registration temp file"
   python3 - "$OWNERSHIP_MANIFEST" "$reg_path" <<'PY' || { rm -f "$reg_path"; die "Cannot read the ownership manifest: $OWNERSHIP_MANIFEST"; }
@@ -1170,32 +1332,27 @@ PY
   while IFS=$'\t' read -r key rel sha source; do
     [ -n "$rel" ] || continue
     total=$((total + 1))
-    case "$rel" in
-      /*) path="$rel" ;;
-      *)  path="$INSTALL_ROOT/$rel" ;;
+    path="$(install_root_abs "$rel")"
+    # E1 (review-5) / 006-003 U7: historical ownership is not authorization to
+    # discard later local changes — a modified owned file is reported and
+    # PRESERVED. owned_removal_state is the ONE rule (also used by the obsolete
+    # prune); a symlink or an absent path is handled exactly as before.
+    case "$(owned_removal_state "$path" "$sha")" in
+      absent)
+        log "UNINSTALL (absent, idempotent) $path"
+        continue
+        ;;
+      modified)
+        preserved=$((preserved + 1))
+        if [ "$key" = "artifacts" ]; then
+          keep_artifacts+=("$rel"$'\t'"$sha"$'\t'"$source")
+        else
+          keep_pending+=("$rel"$'\t'"$sha"$'\t'"$source")
+        fi
+        log "CONFLICT: $rel — modified locally since the recorded install; PRESERVED for explicit resolution (--uninstall did not remove it)"
+        continue
+        ;;
     esac
-    if [ -L "$path" ]; then
-      do_run "UNINSTALL $path" rm -f -- "$path"
-      removed=$((removed + 1))
-      continue
-    fi
-    if [ ! -f "$path" ]; then
-      log "UNINSTALL (absent, idempotent) $path"
-      continue
-    fi
-    # E1 (review-5): historical ownership is not authorization to discard
-    # later local changes — a modified owned file is reported and PRESERVED.
-    actual="$(sha256_of "$path")"
-    if [ -n "$sha" ] && [ "$actual" != "$sha" ]; then
-      preserved=$((preserved + 1))
-      if [ "$key" = "artifacts" ]; then
-        keep_artifacts+=("$rel"$'\t'"$sha"$'\t'"$source")
-      else
-        keep_pending+=("$rel"$'\t'"$sha"$'\t'"$source")
-      fi
-      log "CONFLICT: $rel — modified locally since the recorded install; PRESERVED for explicit resolution (--uninstall did not remove it)"
-      continue
-    fi
     do_run "UNINSTALL $path" rm -f -- "$path"
     removed=$((removed + 1))
   done < "$reg_path"
@@ -1693,6 +1850,9 @@ main() {
   install_user_config
   INSTALL_VERSION="$(installation_version)"
   write_version_marker "$INSTALL_VERSION"
+  # 006-003 U7/D6 (PD-6a..e): retire the own obsolete files this run no longer
+  # deploys (byte-identical only; modified ones are preserved and reported).
+  prune_owned_obsolete
   write_ownership_manifest
   if [ "$DRY_RUN" -eq 1 ]; then
     print_dry_run_summary
```

> Para la opción (b) el único delta es la primera guarda del `while` dentro de `prune_owned_obsolete`: `case "$source" in agents/*) continue ;; esac` (los staged tienen su disposición propia: B3 + la verificación "N of N cdad agents").
