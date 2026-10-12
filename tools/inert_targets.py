"""Rend inertes les cibles des niveaux faciles : groupes de véhicules dont le nom contient « -Inert- ».

Chaque cible est un groupe d'un véhicule (pas un statique : un statique est froid au pod et le drone laser ne
le désigne pas). Ce script lui donne : moteur chaud au départ (`coldAtStart = false`), ROE « tir interdit » et
pas de dispersion sous le feu, sur le premier point de sa route. Aucune action MCP ne règle ROE ni dispersion.
Idempotent : il réécrit les deux options à chaque passage.
"""
import sys

import paths  # noqa: F401  (met VMCT sur sys.path)
from veaf_mission_mcp.mission_folder import load_folder_mission, save_folder_mission  # noqa: E402

ROE_WEAPON_HOLD = {"id": "WrappedAction", "auto": False, "enabled": True,
                   "params": {"action": {"id": "Option", "params": {"name": 0, "value": 4}}}}
# « Disperse under fire » décoché : l'éditeur écrit l'option sans valeur (sa valeur est un délai en secondes)
NO_DISPERSAL = {"id": "WrappedAction", "auto": False, "enabled": True,
                "params": {"action": {"id": "Option", "params": {"name": 8}}}}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mission = load_folder_mission(paths.ROOT)
    content = mission.mission_content
    done = 0
    for side in content["coalition"].values():
        for country in side.get("country") or []:
            for g in (country.get("vehicle") or {}).get("group") or []:
                if "-Inert-" not in g["name"]:
                    continue
                for u in g["units"]:
                    u["coldAtStart"] = False
                g["task"] = "Ground Nothing"
                pt = g["route"]["points"][0]
                pt["task"] = {"id": "ComboTask", "params": {"tasks": [
                    dict(ROE_WEAPON_HOLD, number=1), dict(NO_DISPERSAL, number=2)]}}
                done += 1
    if not done:
        sys.exit("aucune cible « -Inert- » trouvée")
    print(done, "cibles inertes réglées")
    print(save_folder_mission(mission, paths.ROOT))


if __name__ == "__main__":
    main()
