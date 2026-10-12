"""Lot 17c : la piste d'Overlord 1 passait au-dessus des pyramides et encombrait le zoom touristique (point ouvert 4,
David, 12/10/2026). Décalée avec son escorte de 10 km au nord et 40 km à l'ouest : (50 000, -50 000) → (-30 000,
-50 000), à l'ouest de Cairo West, à 10 km du champ de tir A (SA-13 à 5 km) et 67 km du champ S (SA-11 à 50 km).
Lot à ne pas rejouer (déplacement relatif).
"""
import paths
from lib import Batch, M, xy
from veaf_mission_mcp.mission_folder import load_folder_mission

D = (10000, -40000)

if __name__ == "__main__":
    m = load_folder_mission(paths.ROOT).mission_content
    b = Batch()
    for n in ("Overlord 1", "Overlord 1 - Escort"):
        g = next(g for co in m["coalition"].values() for c in co.get("country") or []
                 for g in (c.get("plane") or {}).get("group") or [] if g["name"] == n)
        b.act("set_group_properties", group_name=n, move_to=xy((g["x"] + D[0], g["y"] + D[1])))
    for name in ("Piste Overlord 1", "Piste Overlord 1 étiquette"):
        o = next(o for lay in m["drawings"]["layers"] if lay["name"] == "Blue" for o in lay["objects"] if o["name"] == name)
        b.items.append({"name": "edit_map_drawing", "params": {"mission_path": M, "layer": "Blue", "name": name,
                                                               "position": xy((o["mapX"] + D[0], o["mapY"] + D[1]))}})
    b.save("17c-overlord.json")
