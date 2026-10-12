"""Lot 17 : ce que la sonde DCS du 12/10/2026 a trouvé (probe_scenery.py, probe_points.py), déplacé.

- Le champ de tir hélicoptères d'Arad (position de la v5) était dans les bassins de la mer Morte : DCS y répond
  « eau » (land.getSurfaceType = 3) pour les 12 véhicules, alors que la grille d'altitude y lit 2 m (DCS ne
  descend jamais sous 0 : limitation dcs-ground-never-below-sea-level), donc le test « terre = au-dessus de 0 »
  l'avait laissé passer. Les trois zones et leurs groupes passent sur le plateau au nord-est d'Arad
  (140 000, 384 000), terre dégagée relevée dans DCS entre 150 et 550 m.
- La piste de Texaco 2 (y = 385 000) passait alors à 1 km du champ : décalée de 10 km à l'est (y = 395 000),
  au-dessus de la rive ouest de la mer Morte, avec son escorte.
- Le faux porteur Z09-2 (Port-Fouad) était dans les bâtiments : 50 m à l'ouest, point dégagé relevé dans DCS.
Les dessins F10 suivent. Lot à ne pas rejouer (les déplacements sont relatifs aux positions d'avant).
"""
import paths
from lib import Batch, M, xy
from veaf_mission_mcp.mission_folder import load_folder_mission

OLD_H, NEW_H = (138265, 400241), (140000, 384000)
DH = (NEW_H[0] - OLD_H[0], NEW_H[1] - OLD_H[1])
TEXACO2_DY = 10000

if __name__ == "__main__":
    m = load_folder_mission(paths.ROOT).mission_content
    b = Batch()
    for co in m["coalition"].values():
        for c in co.get("country") or []:
            for cat in ("vehicle", "static"):
                for g in (c.get(cat) or {}).get("group") or []:
                    if g["name"].startswith("combatZone_Arad_"):
                        b.act("set_group_properties", group_name=g["name"], move_to=xy((g["x"] + DH[0], g["y"] + DH[1])))
    for lvl in ("Easy", "Medium", "Hard"):
        b.act("edit_zone", zone_name=f"combatZone_Arad_{lvl}", position=xy(NEW_H))
    for n in ("Texaco 2", "Texaco 2 - Escort"):
        b.act("set_group_properties", group_name=n, move_bearing=90, move_distance_m=TEXACO2_DY)
    b.act("set_group_properties", group_name="combatZone_UsinesPortFouad-Z09-2", move_bearing=270, move_distance_m=50)
    for layer, name, dx, dy in [("Common", "Zone combatZone_Arad", *DH), ("Common", "Zone combatZone_Arad étiquette", *DH),
                                ("Blue", "Piste Texaco 2", 0, TEXACO2_DY), ("Blue", "Piste Texaco 2 étiquette", 0, TEXACO2_DY)]:
        o = next(o for lay in m["drawings"]["layers"] if lay["name"] == layer for o in lay["objects"] if o["name"] == name)
        b.items.append({"name": "edit_map_drawing", "params": {"mission_path": M, "layer": layer, "name": name,
                                                               "position": xy((o["mapX"] + dx, o["mapY"] + dy))}})
    b.save("17-deplacements.json")
