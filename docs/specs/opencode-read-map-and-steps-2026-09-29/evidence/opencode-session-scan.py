#!/usr/bin/env python3
"""Permission-friction scan over OpenCode sessions (read-only).

Usage: opencode-session-scan.py [--since YYYY-MM-DD[ HH:MM]] [--until ...] [--dir-like %projects/cdad]

Reads ~/.local/share/opencode/opencode.db (table session_v2 + session_message)
through a read-only SQLite URI and prints, per agent and per tool, how many tool
calls were rejected by the permission layer ("permission.rejected"), the shell
verbs most rejected, and the assistant-step count per session (input for the
`steps` ceiling). A rejection of a legitimate operation is a product defect.
"""
import argparse, collections, json, os, re, sqlite3, statistics

ap = argparse.ArgumentParser()
ap.add_argument("--since", default="2026-09-24 22:00")
ap.add_argument("--until", default="2999-01-01")
ap.add_argument("--dir-like", default="%projects/cdad")
ap.add_argument("--db", default=os.path.expanduser("~/.local/share/opencode/opencode.db"))
a = ap.parse_args()

db = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
sessions = db.execute(
    "select id, agent, parent_id is not null from session_v2 "
    "where directory like ? and time_created >= strftime('%s', ?) * 1000 "
    "and time_created < strftime('%s', ?) * 1000",
    (a.dir_like, a.since, a.until),
).fetchall()

per_tool = collections.defaultdict(lambda: [0, 0])      # tool -> [ok, denied]
per_agent = collections.defaultdict(lambda: [0, 0])
verbs = collections.defaultdict(lambda: [0, 0])
steps = collections.defaultdict(list)                   # agent -> [assistant messages per session]
for sid, agent, is_child in sessions:
    n_steps = 0
    for (data,) in db.execute("select data from session_message where session_id=?", (sid,)):
        try:
            d = json.loads(data)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("agent") and d.get("content") is not None:
            n_steps += 1
        for c in (d.get("content") or []) if isinstance(d, dict) else []:
            if not isinstance(c, dict) or c.get("type") != "tool":
                continue
            st = c.get("state", {})
            den = int(st.get("error", {}).get("type") == "permission.rejected")
            per_tool[c["name"]][den] += 1
            per_agent[agent][den] += 1
            if c["name"] == "shell":
                cmd = st.get("input", {}).get("command", "").strip()
                verb = re.split(r"\s*(?:&&|\|\||;|\|)\s*", cmd)[0].split(" ")[0] or "?"
                verbs[verb][den] += 1
    if is_child:
        steps[agent].append(n_steps)

print(f"window: {a.since} -> {a.until}; sessions: {len(sessions)}")
print("per tool  [ok, denied]:", {k: tuple(v) for k, v in per_tool.items()})
print("per agent [ok, denied]:", {k: tuple(v) for k, v in per_agent.items()})
print("shell verbs [ok, denied] (top 15 by volume):")
for v, (ok, den) in sorted(verbs.items(), key=lambda x: -sum(x[1]))[:15]:
    print(f"  {v:<14} ok={ok:<5} denied={den}")
print("assistant steps per subagent session:")
for ag, v in sorted(steps.items()):
    v.sort()
    print(f"  {ag:<22} n={len(v):<3} median={int(statistics.median(v)):<4} max={v[-1]}")
