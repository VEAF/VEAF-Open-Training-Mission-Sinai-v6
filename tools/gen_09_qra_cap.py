"""Lot 09 : QRA (rouges, et bleues puisque le rouge est jouable) et CAP à la demande.

QRA : cercle dans le territoire du camp qui défend, réponse graduée, deux appareils différents par niveau tirés
(refaites en décollage de la piste par le lot 09b, une fois les parkings du Sinaï capturés ; texte ci-dessous d'origine)
au sort, délai 90 s, pas de réaction aux hélicoptères, pas de menu radio ouvert à tous. Départ en vol au-dessus
de la base (SinaiMap n'a pas de données de parking dans VMCT : describe_known_limitations,
no-parking-data-outside-three-theatres).
  - Melez : 25 nm autour de la base, le centre du Sinaï (Bir Gifgafa, djebel Maghara). Fayed à 46 nm, Abu Suwayr
    à 55 nm : hors du cercle.
  - El Arish : 25 nm autour de la base, le nord du Sinaï. Hatzerim et Ramon à 45 nm : hors du cercle.
  Couloirs libres : tout le sud (golfe de Suez, St Catherine, Sharm, Tiran), Mitla et Nakhl, la rive du canal.
  - Abu Suwayr et Hatzerim : 20 nm, centrés en retrait de la base, contre les joueurs rouges.
CAP rouges dans le territoire rouge, CAP bleues dans le territoire bleu.
"""
from lib import AIRFIELDS, BLUE_EG, BLUE_IL, RED, Batch, xy

A = AIRFIELDS
MIG29 = {"payload": "R-73*2,R-60M*2,R-27R*2,Fuel-1500"}
SU27 = {"payload": "R-73*4,R-27ER*6"}
SU30 = {"payload": "R-73*4,R-77*4,R-27ER*2"}
F16 = {"payload": "AIM-120C*4,AIM-9M*2,ECM,Fuel*2"}
M2000 = {"payload": "R 550*2,MICA AR*4,Fuel*3"}
F15 = {"payload": "AIM-9*4,AIM-120*4,Fuel"}
F16IL = {"payload": "AIM-120C*4, AIM-9M*2, Fuel"}

QRAS = [
    dict(name="QRA Melez", side=RED, zone="QRA-Melez", center=A["Melez"], radius=46300, airfield="Melez",
         enemy="BLUE", levels=[
             (1, [("QRA-Melez-MiG29", "MiG-29S", 2, MIG29), ("QRA-Melez-Su27", "Su-27", 2, SU27)]),
             (3, [("QRA-Melez-Su30", "Su-30", 2, SU30), ("QRA-Melez-MiG29x4", "MiG-29S", 4, MIG29)])]),
    dict(name="QRA El Arish", side=RED, zone="QRA-ElArish", center=A["El Arish"], radius=46300, airfield="El Arish",
         enemy="BLUE", levels=[
             (1, [("QRA-ElArish-Su27", "Su-27", 2, SU27), ("QRA-ElArish-MiG29", "MiG-29S", 2, MIG29)]),
             (3, [("QRA-ElArish-Su30", "Su-30", 2, SU30), ("QRA-ElArish-Su27x4", "Su-27", 4, SU27)])]),
    dict(name="QRA Abu Suwayr", side=BLUE_EG, zone="QRA-AbuSuwayr", center=(55000, 60000), radius=37000,
         airfield="Abu Suwayr", enemy="RED", levels=[
             (1, [("QRA-AbuSuwayr-F16", "F-16C bl.52d", 2, F16), ("QRA-AbuSuwayr-M2000", "Mirage 2000-5", 2, M2000)]),
             (3, [("QRA-AbuSuwayr-F16x4", "F-16C bl.52d", 4, F16), ("QRA-AbuSuwayr-M2000x4", "Mirage 2000-5", 4, M2000)])]),
    dict(name="QRA Hatzerim", side=BLUE_IL, zone="QRA-Hatzerim", center=(140000, 340000), radius=37000,
         airfield="Hatzerim", enemy="RED", levels=[
             (1, [("QRA-Hatzerim-F15", "F-15C", 2, F15), ("QRA-Hatzerim-F16", "F-16C bl.50", 2, F16IL)]),
             (3, [("QRA-Hatzerim-F15x4", "F-15C", 4, F15), ("QRA-Hatzerim-F16x4", "F-16C bl.50", 4, F16IL)])]),
]

# (nom, type, nombre, camp, a, b, FL, kt, emport, menu, briefing)
CAPS = [
    ("CAP-Centre-MiG29", "MiG-29S", 2, RED, (20000, 190000), (50000, 215000), 220, 420, MIG29,
     "CAP rouge MiG-29S (Fox 1) — centre du Sinaï — FL220",
     "Deux MiG-29S armés de R-27R, R-73 et R-60 patrouillent entre Bir Hasanah et Bir Gifgafa, au FL220. "
     "Emport : R-73*2,R-60M*2,R-27R*2,Fuel-1500."),
    ("CAP-Nord-Su27", "Su-27", 2, RED, (110000, 200000), (100000, 250000), 260, 450, SU27,
     "CAP rouge Su-27 (Fox 1, longue portée) — nord du Sinaï — FL260",
     "Deux Su-27 armés de R-27ER et R-73 patrouillent le long de la côte nord, de Bir al-Abd à El Arish, au FL260. "
     "Emport : R-73*4,R-27ER*6."),
    ("CAP-Sud-MiG31", "MiG-31", 2, RED, (-140000, 245000), (-100000, 285000), 380, 520, {"payload": "R-40R*2,R-33*4"},
     "CAP rouge MiG-31 (intercepteur haut et rapide, R-33) — sud du Sinaï — FL380",
     "Deux MiG-31 armés de R-33 patrouillent haut et vite au-dessus de St Catherine, au FL380. "
     "Emport : R-40R*2,R-33*4."),
    ("Raid-Tu22M", "Tu-22M3", 2, RED, (-20000, 230000), (15000, 260000), 300, 450, {"payload": "FAB-500*33"},
     "Raid rouge Tu-22M3 à intercepter — Nakhl — FL300",
     "Deux bombardiers Tu-22M3 chargés de bombes tournent au-dessus de Nakhl, au FL300, prêts à frapper le canal : "
     "les intercepter. Emport : FAB-500*33."),
    ("CAP-Canal-F16", "F-16C bl.52d", 2, BLUE_EG, (40000, 70000), (0, 80000), 220, 420, F16,
     "CAP bleue F-16C (Fox 3) — rive ouest du canal — FL220",
     "Deux F-16C égyptiens patrouillent sur la rive ouest du canal, d'Ismaïlia à Suez, au FL220. "
     "Emport : AIM-120C*4,AIM-9M*2,ECM,Fuel*2."),
    ("CAP-Negev-F15", "F-15C", 2, BLUE_IL, (120000, 320000), (70000, 340000), 250, 440, F15,
     "CAP bleue F-15C (Fox 3) — Néguev — FL250",
     "Deux F-15C israéliens couvrent le Néguev, de Hatzerim à Ramon, au FL250. Emport : AIM-9*4,AIM-120*4,Fuel."),
]

if __name__ == "__main__":
    b = Batch()
    for q in QRAS:
        groups, levels = [], []
        ap = A[q["airfield"]]
        for count, members in q["levels"]:
            names = []
            for i, (gname, typ, n, loadout) in enumerate(members):
                groups.append({"name": gname, "units": [{"type": typ, "count": n}], "start": "air",
                               "position": xy((ap[0] + 1500 * i, ap[1] + 1500 * len(names))), "altitude_ft": 5000,
                               "speed_kt": 350, "airfield": q["airfield"], **loadout})
                names.append(gname)
            levels.append({"enemy_count": count, "groups": names, "random_pick": 1})
        side = q["side"]
        b.act("create_qra", name=q["name"], coalition=side["coalition"], country_id=side["country_id"],
              country_name=side["country_name"], trigger_zone=q["zone"], position=xy(q["center"]), radius=q["radius"],
              groups=groups, enemy_coalitions=[q["enemy"]],
              qra={"groups_by_enemy_count": levels, "delay_before_activating": 90, "delay_before_rearming": 600,
                   "react_on_helicopters": False, "airport_link": q["airfield"]})
    for name, typ, n, side, a, bb, fl, kt, loadout, menu, brief in CAPS:
        b.act("create_cap_mission", mission_name=name, units=[{"type": typ, "count": n}], **side, position=xy(a),
              route=[{**xy(bb), "altitude_ft": fl * 100}], altitude_ft=fl * 100, speed_kt=kt,
              cap={"menu_name": menu, "briefing": brief}, **loadout)
    b.save("09-qra-cap.json")
