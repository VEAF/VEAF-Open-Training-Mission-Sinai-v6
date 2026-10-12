"""Relecture (lecture seule) des groupes de la mission : python inspect_groups.py [filtre de nom]."""
import json
import sys

import paths  # noqa: F401
from veaf_mission_mcp.mission_folder import load_folder_mission

sys.stdout.reconfigure(encoding="utf-8")
flt = sys.argv[1] if len(sys.argv) > 1 else ""
m = load_folder_mission(paths.ROOT).mission_content
for side, s in m["coalition"].items():
    for c in s.get("country") or []:
        for cat in ("plane", "helicopter", "vehicle", "ship", "static"):
            for g in (c.get(cat) or {}).get("group") or []:
                if flt not in g["name"]:
                    continue
                u0 = g["units"][0]
                pts = g.get("route", {}).get("points") or []
                tasks = [t.get("id") + ":" + str(t.get("params", {}).get("action", {}).get("id", "")) for t in
                         (pts[0].get("task", {}).get("params", {}).get("tasks") or [])] if pts else []
                print(f"{side:4} {c['name'][:6]:6} {cat:10} {g['name'][:32]:32} n={len(g['units'])} {u0['type'][:18]:18} "
                      f"cs={u0.get('callsign')!s:28.28} alt={u0.get('alt', 0):.0f} task={g.get('task')} "
                      f"fuel={u0.get('payload', {}).get('fuel')} pyl={len(u0.get('payload', {}).get('pylons') or {})} "
                      f"freq={g.get('frequency')} late={g.get('lateActivation', False)} pts={len(pts)} {tasks}")
