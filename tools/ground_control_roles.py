"""Rôles sans avion (game master, commandant, JTAC, observateur) : 5 par camp, véhicules pilotables.

blank_mission.py les écrit à 0 et rien dans mission.yaml ne les règle (VMCT FIX-OPEN-TRAINING-CAUCASUS-FINDINGS
ticket 01, ouvert) ; la v5 en avait 4 par rôle et par camp. Les OT recompilées en 6.29.0 sont à 5.
"""
import paths  # noqa: F401
from veaf_mission_mcp.mission_folder import load_folder_mission, save_folder_mission  # noqa: E402

m = load_folder_mission(paths.ROOT)
gc = m.mission_content["groundControl"]
gc["isPilotControlVehicles"] = True
for role in ("artillery_commander", "forward_observer", "instructor", "observer"):
    gc["roles"][role] = {"blue": 5, "red": 5, "neutrals": 0}
print(save_folder_mission(m, paths.ROOT)["mission_file"])
