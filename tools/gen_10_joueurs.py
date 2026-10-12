"""Lot 10 : sanctuaires, arène AirQuake, groupes des missions scénarisées.
(Les slots sur les ponts viennent avec les porte-avions, lot 05b.)

Sanctuaires (cercles tirés de zones de déclenchement) :
  - bleu « Le Caire » : 75 km autour du désert au sud-ouest de Cairo West — la base mère, les pyramides, le FARP
    Pyramides et les champs de tir A et S ;
  - rouge : 20 km autour de St Catherine, l'arrière rouge. El Arish et Melez n'en ont pas : ils bloqueraient les
    zones du nord et du centre.
Arène AirQuake : Méditerranée au nord-ouest, centre (330 000, -60 000), 40 nm de rayon, loin de tout (la v5 y faisait
naviguer le Kuznetsov) ; emports AirQuake de la v5 de l'OT Golfe Persique (FOX1 = AIM-7M / Super 530D, FOX3 =
AIM-120C / AIM-54C), départ en vol au FL250. F-14B rouges sous l'Iran, comme au Golfe Persique.
"""
import json

from lib import AIRFIELDS, BLUE, RED, ROOT, Batch, xy

V5 = json.loads((ROOT / "tools/loadouts-arene.json").read_text(encoding="utf-8"))
RED_IR = dict(coalition="red", country_id=34, country_name="Iran")

SANCTUARIES = [
    ("Sanctuaire Le Caire", "SANCT-LeCaire", (-20000, -65000), 75000, "BLUE"),
    ("Sanctuaire St Catherine", "SANCT-StCatherine", AIRFIELDS["St Catherine"], 20000, "RED"),
]

ARENA = ((330000, -60000), 74000)   # centre, rayon (40 nm)
ARENA_SLOTS = [
    # nom v6, groupe AirQuake de la v5 du Golfe, camp, position (sud = bleu, nord = rouge)
    ("Arène bleue F-14B Fox 3", "BLUE F-14B AirQuake FOX3", BLUE, (270000, -80000)),
    ("Arène bleue F-14B Fox 1", "F-14B AirQuake FOX1 BLUE", BLUE, (270000, -70000)),
    ("Arène bleue F/A-18C Fox 3", "BLUE F/A-18C AirQuake FOX3", BLUE, (270000, -60000)),
    ("Arène bleue F/A-18C Fox 1", "F/A-18C AirQuake FOX1 BLUE", BLUE, (270000, -50000)),
    ("Arène bleue M-2000C Fox 1", "M2000C AirQuake FOX1 BLUE", BLUE, (270000, -40000)),
    ("Arène rouge F-14B Fox 3", "RED F-14B AirQuake FOX3", RED_IR, (390000, -80000)),
    ("Arène rouge F-14B Fox 1", "RED F-14B AirQuake FOX1", RED_IR, (390000, -70000)),
    ("Arène rouge F/A-18C Fox 3", "RED F/A-18C AirQuake FOX3", RED, (390000, -60000)),
    ("Arène rouge F/A-18C Fox 1", "RED F/A-18C AirQuake FOX1", RED, (390000, -50000)),
    ("Arène rouge M-2000C Fox 1", "RED M2000C AirQuake FOX1", RED, (390000, -40000)),
]

ABU_SUWAYR = AIRFIELDS["Abu Suwayr"]
EL_ARISH = AIRFIELDS["El Arish"]
# Missions scénarisées : groupes en activation différée (combat_missions: de mission.yaml)
SCENARIO = [
    # nom, camp, type, nombre, départ, altitude ft, kt, tâche, emport, points suivants
    ("SC-Defense-AbuSuwayr-SEAD", RED, "Su-24M", 2, (15000, 215000), 18000, 480, "SEAD",
     {"payload": "Kh31P*2_Kh25ML*2_L-081"}, [(50000, 120000), ABU_SUWAYR]),
    ("SC-Defense-AbuSuwayr-Bombers", RED, "Su-34", 4, (18000, 220000), 20000, 450, "Ground Attack",
     {"payload": "FAB-500*8,R-73*2,ECM"}, [(55000, 125000), ABU_SUWAYR]),
    ("SC-Defense-AbuSuwayr-Escort", RED, "Su-30", 2, (16000, 218000), 24000, 450, "Escort",
     {"payload": "R-73*4,R-77*4,R-27ER*2"}, [(55000, 125000), ABU_SUWAYR]),
    ("SC-Intercept-VIP-Il76", RED, "IL-76MD", 1, (-145000, 270000), 22000, 350, "Transport",
     {}, [(-20000, 260000), EL_ARISH]),
    ("SC-Intercept-VIP-Escort", RED, "MiG-29S", 2, (-147000, 268000), 24000, 350, "Escort",
     {"payload": "R-73*2,R-60M*2,R-27R*2,Fuel-1500"}, [(-20000, 260000), EL_ARISH]),
]

if __name__ == "__main__":
    b = Batch()
    for name, zone, c, r, side in SANCTUARIES:
        b.act("add_trigger_zone", name=zone, position=xy(c), radius=r)
    b.act("add_trigger_zone", name="Arene", position=xy(ARENA[0]), radius=ARENA[1])
    for name, v5name, side, p in ARENA_SLOTS:
        g = V5[v5name]
        hdg = 0 if side is BLUE else 180
        b.act("add_air_group", **side, name=name, unit_type=g["type"], count=2, start="air",
              position=xy(p), altitude_ft=25000, speed_kt=450, heading_deg=hdg, skill="Client",
              task="CAP", pylons=g["pylons"])
    for name, side, typ, n, p, alt, kt, task, loadout, route in SCENARIO:
        b.act("add_air_group", **side, name=name, unit_type=typ, count=n, start="air", position=xy(p),
              altitude_ft=alt, speed_kt=kt, task=task, skill="High", late_activation=True, **loadout)
        for q in route:
            b.act("edit_route", group_name=name, operation="add", position=xy(q), altitude_ft=alt, speed_kt=kt)
    b.act("edit_route", group_name="SC-Defense-AbuSuwayr-Bombers", operation="add_task", index=3, task="bombing",
          task_params={"position": xy(ABU_SUWAYR), "expend": "All", "attack_qty": 1})
    for esc, target in [("SC-Defense-AbuSuwayr-Escort", "SC-Defense-AbuSuwayr-Bombers"),
                        ("SC-Intercept-VIP-Escort", "SC-Intercept-VIP-Il76")]:
        b.act("edit_route", group_name=esc, operation="add_task", index=1, task="escort",
              task_params={"group_name": target, "engagement_distance_nm": 30})
    b.save("10-joueurs.json")
