"""Lot 17b : la zone Z12 (dépôts d'Abu Rudeis) était sur la ville : la sonde DCS (probe_points.py, 12/10/2026) répond
« bloqué » sur tout le rayon de 1,1 km. Déplacée en entier (zone, groupes, statiques, dessins) de 2,5 km au
nord-nord-est, où 9 points sur 9 sont dégagés. Lot à ne pas rejouer (déplacements relatifs).
"""
import paths
from lib import Batch, M, xy
from veaf_mission_mcp.mission_folder import load_folder_mission

OLD, NEW = (-126441, 192413), (-124092, 193268)
D = (NEW[0] - OLD[0], NEW[1] - OLD[1])

if __name__ == "__main__":
    m = load_folder_mission(paths.ROOT).mission_content
    b = Batch()
    for co in m["coalition"].values():
        for c in co.get("country") or []:
            for cat in ("vehicle", "static"):
                for g in (c.get(cat) or {}).get("group") or []:
                    if g["name"].startswith("combatZone_AbuRudeis"):
                        b.act("set_group_properties", group_name=g["name"], move_to=xy((g["x"] + D[0], g["y"] + D[1])))
    b.act("edit_zone", zone_name="combatZone_AbuRudeis", position=xy(NEW))
    for name in ("Zone combatZone_AbuRudeis", "Zone combatZone_AbuRudeis étiquette"):
        o = next(o for lay in m["drawings"]["layers"] if lay["name"] == "Common" for o in lay["objects"] if o["name"] == name)
        b.items.append({"name": "edit_map_drawing", "params": {"mission_path": M, "layer": "Common", "name": name,
                                                               "position": xy((o["mapX"] + D[0], o["mapY"] + D[1]))}})
    b.save("17b-abu-rudeis.json")
