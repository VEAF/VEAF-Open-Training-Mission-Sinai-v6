"""Lot 07 : les 3 familles d'entraînement × 3 niveaux (facile ⊂ moyen ⊂ difficile, clé `includes:`), et la zone
touristique des pyramides.

H — hélicoptères, plateau au nord-est d'Arad, à 10 nm du FARP Range (v5) et 32 nm de Kedem. Le champ de la v5,
    9 nm à l'est, est dans les bassins de la mer Morte : DCS y répond « eau » (sonde du 12/10/2026, lot
    17). Le difficile s'arrête au SA-13 et aux SA-18, posés au sud-ouest du centre, loin du FARP.
A — attaque, désert au sud-ouest de Cairo West, à 17 nm de la base mère et à plus de 100 nm du front.
S — SEAD, désert occidental, à 52 nm de Cairo West. SA-11 au plus (27 nm) : Cairo West à 52 nm, Kom Awshim à
    43 nm, champ A à 35 nm, piste d'Overlord 1 à 57 nm. Pas de longue portée (décision du 01/10/2026).
T — tourisme : plateau de Gizeh, hors combat (training, non complétable). Des autocars de touristes au parking du
    plateau ; les balises radio et le guide (messages au survol) sont permanents, posés par gen_07b_tourisme.py.
Toutes les distances des briefings sont calculées ici, pas tapées.

Cibles inertes des niveaux faciles : groupes d'un véhicule nommés « …-Inert-… », rendus chauds, tir interdit
et sans dispersion par tools/inert_targets.py (aucune action MCP ne règle ROE ni dispersion).
"""
from lib import AIRFIELDS, BLUE_EG, PLACES, RED, Batch, cmd_unit, nm, off, position_text, spot, tankers_text, xy

P = PLACES
H = (140000, 384000)   # lot 17 : l'emplacement de la v5 (138 265, 400 241) est dans la mer Morte
A = (-10000, -60000)
S = (-45000, -115000)
T = off(P["Pyramid of Khafre"], 135, 700)   # entre les trois pyramides et le Sphinx
FARP_RANGE = (155074, 394983)               # gen_05b
FARP_PYR = off(P["Pyramid of Khafre"], 225, 3000)   # gen_05b
DAHCHOUR = ((P["Red Pyramid"][0] + P["Bent Pyramid"][0]) / 2, (P["Red Pyramid"][1] + P["Bent Pyramid"][1]) / 2)


def inert(zone_center, items, prefix):
    """Groupes d'un véhicule, en couronne autour du centre : (type, relèvement, distance)."""
    groups = []
    for i, (typ, brg, dist) in enumerate(items, 1):
        p = spot(zone_center, brg, dist, f"{prefix}{i}")
        groups.append({"name": f"Inert-{typ.split()[0]}-{i}", "position": xy(p), "keep_position": True,
                       "units": [{"type": typ, "count": 1}]})
    return groups


def fake(zone_center, items, tagbase):
    """Faux porteurs #command : (alias, type du porteur, relèvement, distance, balises de tirage)."""
    groups = []
    for i, (alias, carrier, brg, dist, extra) in enumerate(items, 1):
        p = spot(zone_center, brg, dist, f"{tagbase}-{i}")
        groups.append({"name": f"{tagbase}-{i}", "position": xy(p), "keep_position": True,
                       "units": [cmd_unit(alias + ", country russia", carrier, f"{tagbase}-{i}", extra)]})
    return groups


def zones():
    return [
        # ── H : hélicoptères ──
        ("combatZone_Arad_Easy", H, 2500, "H1 Hélico Arad — facile", "Entraînement hélicoptères", None,
         inert(H, [("T-72B", 0, 600), ("T-72B", 60, 700), ("BMP-2", 120, 500), ("BMP-2", 180, 800),
                   ("BRDM-2", 240, 600), ("Ural-375", 300, 700), ("Ural-375", 330, 400)], "H1-"),
         f"Champ de tir hélicoptères d'Arad, sur le plateau au nord-est de la ville, à {nm(H, FARP_RANGE):.0f} nm du FARP Range : "
         "cibles inertes (chars, blindés et camions immobiles, tir interdit)."),
        ("combatZone_Arad_Medium", H, 2500, "H2 Hélico Arad — moyen", "Entraînement hélicoptères",
         "combatZone_Arad_Easy",
         fake(H, [("-zu23", "Ural-375 ZU-23", 210, 1200, '#spawngroup="H2AAA" #spawncount=2'),
                  ("-zu23", "Ural-375 ZU-23", 270, 1100, '#spawngroup="H2AAA" #spawncount=2'),
                  ("-zu23", "Ural-375 ZU-23", 150, 1300, '#spawngroup="H2AAA" #spawncount=2'),
                  ("-shilka", "ZSU-23-4 Shilka", 240, 900, "#spawnchance=50")], "H2"),
         "Champ de tir hélicoptères d'Arad : de l'artillerie antiaérienne légère (ZU-23, parfois un Shilka) en "
         "plus des cibles du niveau facile."),
        ("combatZone_Arad_Hard", H, 2500, "H3 Hélico Arad — difficile", "Entraînement hélicoptères",
         "combatZone_Arad_Medium",
         fake(H, [("-sa13", "Strela-10M3", 200, 1000, '#spawngroup="H3SR" #spawncount=1'),
                  ("-sa13", "Strela-10M3", 250, 1000, '#spawngroup="H3SR" #spawncount=1'),
                  ("-sa18", "SA-18 Igla manpad", 220, 1500, '#spawngroup="H3MP" #spawncount=1'),
                  ("-sa18", "SA-18 Igla manpad", 180, 1400, '#spawngroup="H3MP" #spawncount=1')], "H3"),
         "Champ de tir hélicoptères d'Arad, avec une défense courte portée réaliste : un SA-13 et une équipe de "
         "lance-missiles portatifs SA-18, à guidage infrarouge."),
        # ── A : attaque ──
        ("combatZone_DesertGizeh_Easy", A, 2500, "A1 Attaque désert de Gizeh — facile", "Entraînement attaque",
         None,
         inert(A, [("T-72B", 0, 700), ("T-72B", 40, 900), ("T-72B", 80, 600), ("BMP-2", 120, 800),
                   ("BMP-2", 160, 500), ("BTR-80", 200, 700), ("BTR-80", 240, 900), ("Ural-375", 280, 600),
                   ("Ural-375", 320, 800), ("KAMAZ Truck", 350, 400)], "A1-"),
         f"Champ de tir air-sol dans le désert au sud-ouest de Cairo West, à {nm(A, AIRFIELDS['Cairo West']):.0f} nm "
         "de la base : blindés et camions immobiles en tir interdit, dépôt de carburant et poste de commandement. "
         "Le drone Reaper 1 tourne au-dessus."),
        ("combatZone_DesertGizeh_Medium", A, 2500, "A2 Attaque désert de Gizeh — moyen", "Entraînement attaque",
         "combatZone_DesertGizeh_Easy",
         fake(A, [("-armor, defense 0", "T-72B", 220, 1300, ""),
                  ("-zu23", "Ural-375 ZU-23", 60, 1500, '#spawngroup="A2AAA" #spawncount=1'),
                  ("-zu23", "Ural-375 ZU-23", 300, 1400, '#spawngroup="A2AAA" #spawncount=1')], "A2"),
         "Champ de tir du désert de Gizeh : une compagnie blindée active et de l'artillerie antiaérienne légère en "
         "plus des cibles du niveau facile."),
        ("combatZone_DesertGizeh_Hard", A, 2500, "A3 Attaque désert de Gizeh — difficile", "Entraînement attaque",
         "combatZone_DesertGizeh_Medium",
         fake(A, [("-armor, defense 1", "T-72B", 260, 1600, ""),
                  ("-sa13", "Strela-10M3", 200, 1200, '#spawngroup="A3SR" #spawncount=1'),
                  ("-sa9", "Strela-1 9P31", 320, 1200, '#spawngroup="A3SR" #spawncount=1'),
                  ("-shilka", "ZSU-23-4 Shilka", 250, 800, "")], "A3"),
         "Champ de tir du désert de Gizeh : un second groupe blindé et une défense courte portée à guidage "
         "infrarouge (SA-13 ou SA-9), avec un Shilka."),
        # ── S : SEAD ──
        ("combatZone_DesertOuest_Easy", S, 3000, "S1 SEAD désert occidental — facile", "Entraînement SEAD", None,
         fake(S, [("-sa6", "Kub 2P25 ln", 0, 0, '#spawngroup="S1MR" #spawncount=1'),
                  ("-sa11", "SA-11 Buk LN 9A310M1", 90, 300, '#spawngroup="S1MR" #spawncount=1')], "S1"),
         f"Site SEAD dans le désert occidental, à {nm(S, AIRFIELDS['Cairo West']):.0f} nm au sud-ouest de Cairo "
         "West : une batterie sol-air moyenne portée, SA-6 ou SA-11 tirée au sort."),
        ("combatZone_DesertOuest_Medium", S, 3000, "S2 SEAD désert occidental — moyen", "Entraînement SEAD",
         "combatZone_DesertOuest_Easy",
         fake(S, [("-sa15", "Tor 9A331", 45, 1500, '#spawngroup="S2SR" #spawncount=2'),
                  ("-sa8", "Osa 9A33 ln", 165, 1500, '#spawngroup="S2SR" #spawncount=2'),
                  ("-sa15", "Tor 9A331", 285, 1500, '#spawngroup="S2SR" #spawncount=2')], "S2"),
         "Site SEAD du désert occidental : la batterie moyenne portée est protégée par une défense courte portée "
         "(SA-15, SA-8)."),
        ("combatZone_DesertOuest_Hard", S, 3000, "S3 SEAD désert occidental — difficile", "Entraînement SEAD",
         "combatZone_DesertOuest_Medium",
         fake(S, [("-ewr", "55G6 EWR", 120, 2200, "")], "S3"),
         "Site SEAD du désert occidental en réseau Skynet : un radar d'alerte avancée guide les batteries, qui "
         "restent éteintes jusqu'au dernier moment."),
    ]


# Statiques du niveau facile attaque : ce qui ne vit pas (dépôt, poste de commandement)
A1_STATICS = [("Fuel tank", 100, 1100), ("Fuel tank", 110, 1200), (".Command Center", 20, 1300)]

TOURISM_TEXT = (
    f"Visite aérienne des pyramides, hors combat, au départ du FARP Pyramides ({nm(FARP_PYR, T):.0f} nm au "
    "sud-ouest du plateau). Circuit : Gizeh (Khéops, Khéphren, Mykérinos, le Sphinx), puis Saqqarah (pyramide à "
    f"degrés de Djoser, {nm(P['Great Pyramid of Giza'], P['Pyramid of Djoser']):.0f} nm au sud-sud-est), puis "
    f"Dahchour (pyramide rouge et pyramide rhomboïdale, {nm(P['Pyramid of Djoser'], DAHCHOUR):.0f} nm plus au sud). "
    "Une balise radio FM à chaque site (GIZ 31.0, SAQ 32.0, DAH 33.0) ; survolez un monument à moins de 1 500 ft "
    "sol et un guide vous le raconte. Excursion : la pyramide effondrée de Meïdoum, "
    f"{nm(DAHCHOUR, P['Meidum pyramid']):.0f} nm au sud de Dahchour. Dans le sanctuaire bleu du Caire : un appareil "
    "rouge y est détruit.")


def tourism():
    """Autocars et 4x4 au parking du plateau, bleus (égyptiens), hors combat."""
    return ("combatZone_Pyramides", T, 1500, "T Tourisme — pyramides de Gizeh", "Tourisme",
            [{"name": "Autocars", "position": xy(spot(T, 90, 600, "autocars")), "keep_position": True,
              "units": [{"type": "LAZ Bus", "count": 3}]},
             {"name": "4x4", "position": xy(spot(T, 60, 800, "4x4")), "keep_position": True,
              "units": [{"type": "Land_Rover_101_FC", "count": 2}]}],
            TOURISM_TEXT)


if __name__ == "__main__":
    b = Batch()
    for zone, c, r, fname, menu, inc, groups, text in zones():
        cz = {"friendly_name": fname, "radio_group_name": menu, "training": True,
              "briefing": f"{text}\n{position_text(c)} {tankers_text(c)}"}
        if inc:
            cz["includes"] = [inc]
        b.act("create_combat_zone", zone_name=zone, position=xy(c), radius=r, groups=groups, **RED,
              category="vehicle", combat_zone=cz)
    for i, (typ, brg, dist) in enumerate(A1_STATICS, 1):
        p = spot(A, brg, dist, f"A1-static-{i}")
        b.act("add_group", **RED, category="static", name=f"Static-{typ.strip('.').split()[0]}-{i}",
              position=xy(p), units=[{"type": typ}], for_combat_zone="combatZone_DesertGizeh_Easy",
              keep_position=True)
    zone, c, r, fname, menu, groups, text = tourism()
    b.act("create_combat_zone", zone_name=zone, position=xy(c), radius=r, groups=groups, **BLUE_EG,
          category="vehicle", combat_zone={"friendly_name": fname, "radio_group_name": menu, "training": True,
                                           "completable": False, "briefing": f"{text}\n{position_text(c)}"})
    b.save("07-entrainement.json")
