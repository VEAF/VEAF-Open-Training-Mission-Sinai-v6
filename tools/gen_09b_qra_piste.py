"""Lot 09b : les QRA refaites en décollage de la piste, une fois les parkings du Sinaï capturés.

Le lot 09 les avait posées en départ en vol au-dessus de leur base : VMCT n'avait pas de données de parking pour
SinaiMap. La capture du 12/10/2026 (`veaf-tools dcs capture-map --parking`, 3 614 places sur 56 aérodromes, ajoutée
à `veaf_libs/data/parking/SinaiMap.json` du checkout VMCT) permet le départ par défaut de `create_qra` : la piste
de la base, ce que demande le prompt (§4.8, `airport_link`).
Ce lot retire les 16 groupes, les 4 zones et les 4 définitions du lot 09, puis les recrée à l'identique, sauf le
départ. Les CAP du lot 09 ne bougent pas.
"""
from gen_09_qra_cap import QRAS
from lib import M, Batch, xy

if __name__ == "__main__":
    b = Batch()
    for q in QRAS:
        for count, members in q["levels"]:
            for gname, *_ in members:
                b.act("remove_group", group_name=gname)
        b.items.append({"name": "edit_zone", "params": {"mission_path": M, "zone_name": q["zone"], "remove": True}})
    b.items.append({"name": "set_mission_module", "params": {"mission_yaml_path": M + "/mission.yaml", "module_id": "QRA",
                                                             "value": {"enabled": True, "definitions": []}}})
    for q in QRAS:
        groups, levels = [], []
        for count, members in q["levels"]:
            names = []
            for gname, typ, n, loadout in members:
                groups.append({"name": gname, "units": [{"type": typ, "count": n}], "airfield": q["airfield"], **loadout})
                names.append(gname)
            levels.append({"enemy_count": count, "groups": names, "random_pick": 1})
        side = q["side"]
        b.act("create_qra", name=q["name"], coalition=side["coalition"], country_id=side["country_id"],
              country_name=side["country_name"], trigger_zone=q["zone"], position=xy(q["center"]), radius=q["radius"],
              groups=groups, enemy_coalitions=[q["enemy"]],
              qra={"groups_by_enemy_count": levels, "delay_before_activating": 90, "delay_before_rearming": 600,
                   "react_on_helicopters": False, "airport_link": q["airfield"]})
    b.save("09b-qra-piste.json")
