"""Appelle les actions de veaf-mission-mcp en Python, dans le processus, sur le code VMCT de develop.

python tools/mcp.py list
python tools/mcp.py describe <action>
python tools/mcp.py run <action> '<params json>' [--full]
python tools/mcp.py batch tools/batches/<lot>.json [--full]

Un lot s'exécute une seule fois : add_group ne dédoublonne pas, rejouer un lot d'ajouts crée des
doublons. Lire les avertissements dans la sortie obtenue, ne pas relancer pour les revoir.
"""
import json
import subprocess
import sys

from paths import VMCT  # noqa: E402  (met aussi le code VMCT sur sys.path)

sys.stdout.reconfigure(encoding="utf-8")
br = subprocess.run(["git", "-C", str(VMCT), "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
if br != "develop":
    sys.exit(f"le checkout VMCT est sur '{br}', pas sur develop : refusé")
from veaf_mission_mcp.actions import register_default_actions  # noqa: E402
from veaf_mission_mcp.catalog import ActionCatalog  # noqa: E402

cat = ActionCatalog()
register_default_actions(cat)
if __name__ == "__main__":
    full = "--full" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--full"]


    def show(name, res):
        if not full and isinstance(res, dict):
            res = {k: v for k, v in res.items() if k not in ("route", "units", "groups")}
        txt = json.dumps(res, ensure_ascii=False, default=str, indent=None if not full else 1)
        print(f"{name}: {txt if full else txt[:1500]}")


    cmd = args[0]
    if cmd == "list":
        for s in cat.list_catalog():
            print(s.name, "-", s.description[:110])
    elif cmd == "describe":
        print(json.dumps(cat.describe_action(args[1]).model_dump(), ensure_ascii=False, indent=1))
    elif cmd == "run":
        show(args[1], cat.run_action(args[1], json.loads(args[2]) if len(args) > 2 else {}))
    elif cmd == "batch":
        for i, it in enumerate(json.load(open(args[1], encoding="utf-8")), 1):
            try:
                show(f"[{i}] {it['name']}", cat.run_action(it["name"], it.get("params", {})))
            except Exception as e:  # noqa: BLE001
                print(f"[{i}] {it['name']} FAILED: {e!r}")
                sys.exit(1)
