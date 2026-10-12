"""Réécrit modules.COMBATZONE de mission.yaml depuis gen_07_entrainement.py et gen_08_zones.py.

Les générateurs sont la source des noms, menus, inclusions et briefings ; un déplacement ou un renommage de zone
n'a donc qu'à être fait là, puis ce script remet mission.yaml d'accord. (Les positions sont recalculées avec la
grille d'altitude : elle doit être présente.)
"""
import gen_07_entrainement as e
import gen_08_zones as z
from lib import M, position_text, tankers_text
from mcp import cat

zones = []
for name, c, r, fname, menu, inc, groups, text in e.zones():
    cz = {"type": "zone", "zone_name": name, "friendly_name": fname, "radio_group_name": menu, "training": True}
    if inc:
        cz["includes"] = [inc]
    cz["briefing"] = f"{text}\n{position_text(c)} {tankers_text(c)}"
    zones.append(cz)
name, c, r, fname, menu, groups, text = e.tourism()
zones.append({"type": "zone", "zone_name": name, "friendly_name": fname, "radio_group_name": menu, "training": True,
              "completable": False, "briefing": f"{text}\n{position_text(c)}"})
for name, c, r, fname, menu, text, *_ in z.zones():
    zones.append({"type": "zone", "zone_name": name, "friendly_name": fname, "radio_group_name": menu,
                  "training": False, "briefing": f"{text}\n{position_text(c)} {tankers_text(c)}"})
print(cat.run_action("set_mission_module", {"mission_yaml_path": M + "/mission.yaml", "module_id": "COMBATZONE",
                                             "value": {"enabled": True, "combat_zones": zones}}))
print(len(zones), "zones")
