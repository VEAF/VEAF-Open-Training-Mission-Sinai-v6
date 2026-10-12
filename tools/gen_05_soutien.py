"""Lot 05 : ravitailleurs, AWACS, escortes, drone laser du champ de tir d'attaque.

Les groupes aéronavals viennent après (lot 05b, contrôle « pleine mer » sur la grille d'altitude) : ravitailleurs
AVANT porte-avions, sinon les S-3B de add_carrier_group prennent Texaco11 / Arco11 (constaté aux Mariannes).

Plan radio hors de la bande des tours du théâtre (describe_airfield_channels : UHF 250.05-252.25, plus 225.9,
227.15, 227.85 ; FM 38.4-42.2) : AWACS 282-286, ravitailleurs 290-293 (dernier chiffre = TACAN 50Y..53Y),
S-3B des porte-avions 296-297, porte-avions 305-307.
Escortes : sur tous les ravitailleurs et AWACS (décision de David, 12/10/2026), sauf les AWACS de l'arène.
Secteur canal : à l'est du Caire, 40 nm du canal. Overlord 1 : à l'ouest de Cairo West (lot 17c). Secteur Néguev : Nevatim, Dimona, Arad (Israël est étroit,
toutes les pistes y sont proches du front). Rouge : centre-sud du Sinaï.
"""
from lib import BLUE, BLUE_EG, BLUE_IL, RED, TANKERS, Batch, xy

b = Batch()

F16 = ("F-16C bl.50", {"payload": "AIM-120C*4, AIM-9M*2, Fuel"})
F15 = ("F-15C", {"payload": "AIM-9*4,AIM-120*4,Fuel"})
SU27 = ("Su-27", {"payload": "R-73*4,R-27ER*6"})


def tk(name):
    (a, bb), fl, tacan, f, kind = TANKERS[name]
    return a, bb, fl, f, int(tacan[:-1])


# nom, type, camp, a, b (hippodrome), FL, kt, MHz, rôle, TACAN (canal, indicatif), escorte (camp, type, emport)
SUPPORT = []
for n, typ, side, cs, esc in [("Texaco 1", "KC-135", BLUE_EG, "TX1", (BLUE_EG, *F16)),
                              ("Arco 1", "KC135MPRS", BLUE_EG, "AR1", (BLUE_EG, *F16)),
                              ("Texaco 2", "KC-135", BLUE_IL, "TX2", (BLUE_IL, *F15)),
                              ("Arco 2", "KC135MPRS", BLUE_IL, "AR2", (BLUE_IL, *F15))]:
    a, bb, fl, f, ch = tk(n)
    SUPPORT.append((n, typ, BLUE, a, bb, fl, 400 if typ == "KC-135" else 380, f, "Refueling", (ch, cs), esc))
SUPPORT += [
    # AWACS : ouest au-dessus du Caire, est au large d'Ashdod et du Néguev
    ("Overlord 1", "E-3A", BLUE, (50000, -50000), (-30000, -50000), 300, 360, 282.0, "AWACS", None, (BLUE_EG, *F16)),
    ("Magic 1", "E-3A", BLUE, (210000, 300000), (170000, 345000), 300, 360, 283.0, "AWACS", None, (BLUE_IL, *F15)),
    # rouge, centre-sud du Sinaï
    ("Shell 1", "IL-78M", RED, (-60000, 225000), (-120000, 225000), 200, 380, 294.0, "Refueling", None, (RED, *SU27)),
    ("Wizard 1", "A-50", RED, (-30000, 255000), (-110000, 255000), 300, 360, 284.0, "AWACS", None, (RED, *SU27)),
    # arène, Méditerranée au nord-ouest : un AWACS par camp, sans escorte
    ("Darkstar 1", "E-3A", BLUE, (250000, -30000), (250000, -90000), 300, 360, 285.0, "AWACS", None, None),
    ("Focus 1", "A-50", RED, (410000, -30000), (410000, -90000), 300, 360, 286.0, "AWACS", None, None),
]
for n, typ, side, a, bb, fl, kt, f, task, beacon, esc in SUPPORT:
    b.act("add_air_group", **side, name=n, unit_type=typ, count=1, start="air", position=xy(a),
          altitude_ft=fl * 100, speed_kt=kt, frequency_mhz=f, task=task, skill="High")
    b.act("edit_route", group_name=n, operation="add", position=xy(bb), altitude_ft=fl * 100, speed_kt=kt)
    b.act("edit_route", group_name=n, operation="add_task", index=1, task="set_unlimited_fuel", task_params={"value": True})
    if beacon:
        b.act("edit_route", group_name=n, operation="add_task", index=1, task="activate_beacon",
              task_params={"channel": beacon[0], "mode": "Y", "callsign": beacon[1], "bearing": True, "aa": True})
    if task == "Refueling":
        b.act("edit_route", group_name=n, operation="add_task", index=1, task="tanker", task_params={})
    else:
        b.act("edit_route", group_name=n, operation="add_task", index=1, task="awacs", task_params={})
        b.act("edit_route", group_name=n, operation="add_task", index=1, task="eplrs", task_params={"value": True})
    b.act("edit_route", group_name=n, operation="add_task", index=1, task="orbit",
          task_params={"pattern": "Race-Track", "altitude_ft": fl * 100, "speed_kt": kt})
    if esc:
        eside, etype, loadout = esc
        en = n + " - Escort"
        b.act("add_air_group", **eside, name=en, unit_type=etype, count=2, start="air",
              position=xy((a[0] - 3000, a[1] - 3000)), altitude_ft=fl * 100, speed_kt=kt, frequency_mhz=f,
              task="Escort", skill="High", **loadout)
        b.act("edit_route", group_name=en, operation="add_task", index=1, task="set_unlimited_fuel", task_params={"value": True})
        b.act("edit_route", group_name=en, operation="add_task", index=1, task="escort",
              task_params={"group_name": n, "engagement_distance_nm": 30})

# ── Drone de guidage laser du champ de tir d'attaque (le second, sur une vraie zone, vient avec le lot 08)
b.act("add_air_group", **BLUE, name="Reaper 1", unit_type="MQ-9 Reaper", count=1, start="air",
      position=xy((-10000, -60000)), altitude_ft=10000, speed_kt=110, task="AFAC", skill="High")

if __name__ == "__main__":
    b.save("05-soutien.json")
