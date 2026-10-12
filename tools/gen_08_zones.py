"""Lot 08 : les vraies zones de combat, dans le Sinaï occupé (training: false), et le drone laser Reaper 2.

16 zones : front 3, SEAD 2, convois en mouvement 3, frappes dans la profondeur 4, OCA 2, antinavire 2.
Lieux réels (tools/places.json, geocode, ou coordonnées géographiques de lib.py) ou repris de la v5 (usines de
Port-Fouad, croiseur devant Damiette). Chaque position est ramenée sur la terre ferme (grille DCS) ; les navires
sont contrôlés en pleine mer. Portée des SAM de zone (aucune zone n'est active au démarrage) : check_portees.py
mesure chaque zone contre les bases amies, les pistes de ravitailleurs et les zones d'entraînement.
Reaper 2 tourne sur le col de Mitla (Z02), zone sans SAM au-delà de 10 km.
Le croiseur de la v5 (Piotr Velikiy, 103 nm de portée) est remplacé par un Moskva (40 nm) : posé n'importe où en
Méditerranée, le Piotr couvrirait les porte-avions ou les bases de la côte.
"""
from lib import (AIRFIELDS, BLUE, PLACES, RED, Batch, cmd_unit, land, nm, off, position_text, sea, spot,
                 tankers_text, xy)

A = AIRFIELDS
P = PLACES


def g_fake(c, items, tagbase):
    """Faux porteurs #command : (alias, type du porteur, relèvement, distance, balises de tirage)."""
    out = []
    for i, (alias, carrier, brg, dist, extra) in enumerate(items, 1):
        p = spot(c, brg, dist, f"{tagbase}-{i}")
        out.append({"name": f"{tagbase}-{i}", "position": xy(p), "keep_position": True,
                    "units": [cmd_unit(alias + ", country russia", carrier, f"{tagbase}-{i}", extra)]})
    return out


def g_native(c, name, brg, dist, units, route=None):
    p = spot(c, brg, dist, name)
    g = {"name": name, "position": xy(p), "keep_position": True, "units": units}
    if route:
        g["route"] = [xy(p)] + [xy(q) for q in route]
    return g


def s_items(c, items):
    """Statiques : (type, relèvement, distance)."""
    return [(typ, spot(c, brg, dist, typ)) for typ, brg, dist in items]


def zones():
    Z = []

    def zone(name, c, r, fname, menu, text, groups, statics=(), side=RED, cat="vehicle", extra=()):
        Z.append((name, c, r, fname, menu, text, side, cat, groups, list(statics), list(extra)))

    # ── Front ────────────────────────────────────────────────────────────────
    C = spot((62000, 118000), 0, 0, "tête de pont")
    zone("combatZone_TeteDePont", C, 2500, "Z01 Front ouest — tête de pont face à Ismaïlia", "Front",
         "La brigade blindée rouge qui tient la rive est du canal, face à Ismaïlia : chars, blindés et lance-roquettes "
         "en position. Détruire les blindés et l'artillerie ; défense SA-15 possible, SA-13 et artillerie "
         "antiaérienne. Les Hawk d'Abu Suwayr couvrent la rive ouest.",
         g_fake(C, [("-armor, defense 2", "T-72B", 0, 800, ""), ("-armor, defense 1", "T-72B", 120, 900, ""),
                    ("-sa15", "Tor 9A331", 90, 600, "#spawnchance=50"), ("-sa13", "Strela-10M3", 240, 700, ""),
                    ("-zu23", "Ural-375 ZU-23", 300, 1200, "")], "Z01")
         + [g_native(C, "Artillerie", 90, 1300, [{"type": "Grad-URAL", "count": 4}])],
         s_items(C, [(".Command Center", 60, 1500), ("Fuel tank", 70, 1700)]))

    C = spot(P["Mitla Pass"], 0, 0, "Mitla")
    zone("combatZone_Mitla", C, 2500, "Z02 Front ouest — ligne du col de Mitla", "Front",
         "La ligne de défense rouge du col de Mitla, la route de Suez vers Nakhl : chars enterrés, blindés et "
         "artillerie automotrice. Défense courte portée seulement (SA-13, Shilka) : le drone Reaper 2 la désigne "
         "au laser.",
         g_fake(C, [("-armor, defense 1", "T-72B", 30, 800, ""), ("-armor, defense 0", "BMP-2", 150, 900, ""),
                    ("-sa13", "Strela-10M3", 270, 700, ""), ("-shilka", "ZSU-23-4 Shilka", 90, 500, "")], "Z02")
         + [g_native(C, "Artillerie", 210, 1200, [{"type": "SAU Msta", "count": 3}])],
         s_items(C, [("Barracks 2", 330, 1300), ("Barracks 2", 340, 1500)]))

    C = spot(P["Abu Ageila"], 0, 0, "Abu Ageila")
    zone("combatZone_AbuAgeila", C, 2500, "Z03 Front est — carrefour d'Abu Ageila", "Front",
         "Le carrefour fortifié d'Abu Ageila, sur la route d'El Arish à Ismaïlia, face à la frontière israélienne : "
         "une brigade mécanisée et ses lance-roquettes. Détruire les blindés et les Grad ; défense SA-8 et "
         "artillerie antiaérienne, sous la QRA d'El Arish.",
         g_fake(C, [("-armor, defense 2", "T-72B", 330, 800, ""), ("-armor, defense 1", "BMP-2", 90, 900, ""),
                    ("-sa8", "Osa 9A33 ln", 200, 600, ""), ("-zu23", "Ural-375 ZU-23", 30, 1000, "")], "Z03")
         + [g_native(C, "Lance-roquettes", 250, 1300, [{"type": "Grad-URAL", "count": 4}])],
         s_items(C, [("Bunker", 0, 400), ("Bunker", 120, 450), ("Bunker", 240, 420)]))

    # ── SEAD ─────────────────────────────────────────────────────────────────
    C = spot(P["Jebel Maghara"], 0, 0, "Maghara")
    zone("combatZone_Maghara", C, 2000, "Z04 SEAD — site SA-6 du djebel Maghara", "SEAD",
         "Le site SA-6 perché au djebel Maghara, au nord du Sinaï, relié à un radar d'alerte avancée en réseau "
         "Skynet. Détruire le radar de conduite de tir et les lanceurs ; un Shilka protège le site.",
         g_fake(C, [("-sa6", "Kub 2P25 ln", 0, 0, ""), ("-ewr", "55G6 EWR", 90, 1500, ""),
                    ("-shilka", "ZSU-23-4 Shilka", 200, 500, "")], "Z04"))

    C = spot(P["Nakhl, Egypt"], 0, 6000, "Nakhl")
    zone("combatZone_Nakhl", C, 2000, "Z05 SEAD — site sol-air de Nakhl", "SEAD",
         "Le site sol-air qui couvre le carrefour de Nakhl, au centre du Sinaï : une batterie SA-2 ou SA-3 tirée au "
         "sort, son radar d'alerte avancée et un Shilka. Sous la couverture lointaine du SA-10 du centre-sud.",
         g_fake(C, [("-sa2", "S_75M_Volhov", 0, 0, '#spawngroup="Z05MR" #spawncount=1'),
                    ("-sa3", "5p73 s-125 ln", 60, 300, '#spawngroup="Z05MR" #spawncount=1'),
                    ("-ewr", "55G6 EWR", 180, 1200, ""), ("-shilka", "ZSU-23-4 Shilka", 300, 500, "")], "Z05"))

    # ── Convois en mouvement (un groupe natif, route sur route, AAA dans le groupe) ──
    C = spot(A["El Arish"], 160, 12000, "convoi El Arish")
    zone("combatZone_ConvoiElArish", C, 1500, "Z06 Convoi — El Arish vers Abu Ageila", "Convois",
         "Un convoi de renforts quitte El Arish par la route du sud-est vers le carrefour d'Abu Ageila. L'arrêter "
         "avant Abu Ageila ; il porte sa propre artillerie antiaérienne (ZU-23) et un SA-9.",
         [g_native(C, "Convoi", 0, 0, [{"type": "BTR-80", "count": 1}, {"type": "Ural-375", "count": 4},
                                       {"type": "Ural-375 ZU-23", "count": 1}, {"type": "Strela-1 9P31", "count": 1}],
                   route=[spot(off(C, 140, 15000), 0, 0, "r"), spot(P["Abu Ageila"], 0, 2000, "r")])])

    C = spot(P["Nakhl, Egypt"], 300, 10000, "convoi Nakhl")
    zone("combatZone_ConvoiNakhl", C, 1500, "Z07 Convoi — Nakhl vers le col de Mitla", "Convois",
         "Des renforts blindés roulent de Nakhl vers le col de Mitla, pour renforcer la ligne face à Suez. Les "
         "arrêter avant le col ; le convoi est escorté par un SA-13.",
         [g_native(C, "Convoi", 0, 0, [{"type": "T-72B", "count": 2}, {"type": "BMP-2", "count": 2},
                                       {"type": "Ural-375", "count": 2}, {"type": "Strela-10M3", "count": 1}],
                   route=[spot(off(P["Mitla Pass"], 90, 25000), 0, 0, "r"), spot(P["Mitla Pass"], 90, 6000, "r")])])

    C = spot(A["St Catherine"], 300, 26000, "convoi Feiran")   # hors du sanctuaire rouge de St Catherine (20 km)
    zone("combatZone_ConvoiFeiran", C, 1500, "Z08 Convoi — oasis de Feiran vers Abu Rudeis", "Convois",
         "Un convoi de carburant descend l'oued Feiran vers les dépôts d'Abu Rudeis, sur le golfe de Suez. Le "
         "détruire avant la côte ; il porte sa propre artillerie antiaérienne. Sous la couverture du SA-10 de "
         "St Catherine.",
         [g_native(C, "Convoi", 0, 0, [{"type": "BTR-80", "count": 1}, {"type": "ATZ-10", "count": 3},
                                       {"type": "Ural-375 ZU-23", "count": 1}],
                   route=[spot(P["Wadi Feiran"], 0, 0, "r"), spot(P["Abu Zenima"], 90, 4000, "r")])])

    # ── Frappes dans la profondeur ───────────────────────────────────────────
    C = spot((115783, 105229), 0, 0, "Port-Fouad")
    zone("combatZone_UsinesPortFouad", C, 1500, "Z09 Frappe — usines de Port-Fouad", "Frappes en profondeur",
         "Les usines de la zone industrielle au sud de Port-Fouad, sur la rive est du canal, reconverties en "
         "ateliers d'armement : ateliers, hangars, réservoirs chimiques. Tout détruire ; défense SA-6, SA-9 et "
         "artillerie antiaérienne (reprise de la v5).",
         g_fake(C, [("-sa6", "Kub 2P25 ln", 300, 700, ""), ("-sa9", "Strela-1 9P31", 120, 400, ""),
                    ("-zu23", "Ural-375 ZU-23", 240, 400, "")], "Z09"),
         s_items(C, [("Workshop A", 0, 150), ("Workshop A", 20, 250), ("Tech hangar A", 90, 200),
                     ("Repair workshop", 140, 250), ("Chemical tank A", 200, 150), ("Chemical tank A", 210, 200),
                     ("Fuel tank", 250, 250), ("Comms tower M", 320, 200)]))

    C = spot(P["Bir Tamada"], 0, 0, "Bir Tamada")
    zone("combatZone_EtatMajor", C, 1200, "Z10 Frappe — état-major de Bir Tamada", "Frappes en profondeur",
         "Le poste de commandement de l'armée rouge du Sinaï, enterré à Bir Tamada : bunkers, centre de "
         "transmissions, véhicules de commandement. Tout détruire ; défense SA-15 et Shilka, sous la QRA de Melez.",
         g_fake(C, [("-sa15", "Tor 9A331", 200, 600, ""), ("-shilka", "ZSU-23-4 Shilka", 60, 400, "")], "Z10")
         + [g_native(C, "PC mobile", 300, 300, [{"type": "SKP-11", "count": 2}, {"type": "Ural-375 PBU", "count": 1}])],
         s_items(C, [(".Command Center", 0, 0), ("Bunker", 90, 200), ("Bunker", 180, 200), ("Bunker", 270, 200),
                     ("Comms tower M", 45, 250), ("Military staff", 135, 250)]))

    C = spot(P["Jebel Libni"], 0, 0, "Libni")
    zone("combatZone_Scud", C, 1500, "Z11 Frappe — base de missiles du djebel Libni", "Frappes en profondeur",
         "Une base de missiles sol-sol au pied du djebel Libni, d'où les Scud menacent Le Caire et Beer-Sheva : "
         "lanceurs et camions de ravitaillement. Détruire les lanceurs ; défense SA-15 et Shilka.",
         [g_native(C, "Lanceurs", 0, 0, [{"type": "Scud_B", "count": 3}, {"type": "Ural-375", "count": 2}])]
         + g_fake(C, [("-sa15", "Tor 9A331", 200, 600, ""), ("-shilka", "ZSU-23-4 Shilka", 60, 400, "")], "Z11"),
         s_items(C, [("Bunker", 300, 300), ("Military staff", 320, 400)]))

    C = spot((-124092, 193268), 0, 0, "Abu Rudeis")   # lot 17b : 2,5 km au nord-nord-est de la ville, sondé dégagé
    zone("combatZone_AbuRudeis", C, 1200, "Z12 Frappe — dépôts pétroliers d'Abu Rudeis", "Frappes en profondeur",
         "Les dépôts pétroliers d'Abu Rudeis, sur la côte du golfe de Suez : ils ravitaillent toute l'armée rouge du "
         "sud. Détruire réservoirs et pompes ; ZU-23 sur place, et le SA-10 de St Catherine à moins de 40 nm.",
         g_fake(C, [("-zu23", "Ural-375 ZU-23", 0, 300, ""), ("-zu23", "Ural-375 ZU-23", 180, 300, "")], "Z12"),
         s_items(C, [("Fuel tank", 30, 150), ("Fuel tank", 60, 200), ("Fuel tank", 90, 150), ("Tank", 120, 200),
                     ("Tank", 140, 250), ("Electric power box", 240, 120), ("Workshop A", 300, 150)]))

    # ── Bases aériennes (OCA) ────────────────────────────────────────────────
    C = spot(off(A["El Gora"], 90, 600), 0, 0, "El Gora")
    zone("combatZone_ElGora", C, 1500, "Z13 OCA — base aérienne d'El Gora", "Bases aériennes",
         "La base aérienne d'El Gora, à 30 km de la frontière israélienne : chasseurs-bombardiers au parking, "
         "hangars et carburant. Tout détruire au sol ; défense SA-15 et Shilka.",
         g_fake(C, [("-sa15", "Tor 9A331", 90, 900, ""), ("-shilka", "ZSU-23-4 Shilka", 270, 700, "")], "Z13"),
         s_items(C, [("Su-24M", 0, 300), ("Su-24M", 15, 340), ("MiG-29S", 40, 300), ("MiG-29S", 50, 340),
                     ("Hangar A", 330, 300), ("Fuel tank", 180, 400)]))

    C = spot(off(A["Sharm El Sheikh International Airport"], 270, 800), 0, 0, "Sharm")
    zone("combatZone_Sharm", C, 1500, "Z14 OCA — base aérienne de Sharm el-Cheikh", "Bases aériennes",
         "L'aéroport de Sharm el-Cheikh, devenu base aérienne rouge à la pointe sud du Sinaï : avions de transport "
         "et hélicoptères d'attaque au sol, hangars. Tout détruire au sol ; défense SA-6 et ZU-23, plus le SA-15 "
         "permanent de la base.",
         g_fake(C, [("-sa6", "Kub 2P25 ln", 90, 1000, ""), ("-zu23", "Ural-375 ZU-23", 270, 600, "")], "Z14"),
         s_items(C, [("IL-76MD", 0, 300), ("IL-76MD", 20, 380), ("Mi-24V", 300, 250), ("Mi-24V", 310, 290),
                     ("Mi-8MT", 330, 250), ("Hangar A", 180, 300), ("Fuel tank", 200, 400)]))

    # ── Antinavire ───────────────────────────────────────────────────────────
    C = (220000, 70000)
    zone("combatZone_Croiseur", C, 6000, "Z15 Antinavire — croiseur Moskva devant Damiette", "Antinavire",
         f"Le croiseur lance-missiles rouge Moskva et deux frégates croisent en Méditerranée, à {nm(C, P['Damietta']):.0f} "
         "nm au nord de Damiette, pour couper la route des porte-avions. Les couler : le Moskva porte des missiles sol-air à "
         "40 nm, les frégates à courte portée (reprise de la v5, dont le croiseur était le Piotr Velikiy).",
         [{"name": "Escadre", "position": xy(C), "keep_position": True, "patrol": True,
           "units": [{"type": "MOSCOW", "count": 1}, {"type": "NEUSTRASH", "count": 1}, {"type": "REZKY", "count": 1}],
           "route": [xy(C), xy((215000, 95000))]}], cat="ship")

    # dans le chenal du détroit, entre Ras Nasrani et l'île de Tiran (relevé sur la grille : 4 km de large)
    C = (P["Ras Nasrani"][0] - 2000, P["Ras Nasrani"][1] + 4000)
    zone("combatZone_Tiran", C, 6000, "Z16 Antinavire — détroit de Tiran", "Antinavire",
         "Le rouge ferme le détroit de Tiran, la sortie du golfe d'Aqaba : une batterie de missiles antinavires "
         "(HY-2 Silkworm, portée 54 nm) à Ras Nasrani et un essaim de vedettes rapides dans le détroit. Détruire "
         "lanceurs et radar, couler les vedettes ; SA-15 permanent à Sharm el-Cheikh.",
         [{"name": "Vedettes", "position": xy(C), "keep_position": True, "patrol": True,
           "units": [{"type": "speedboat", "count": 6}], "route": [xy(C), xy((C[0] + 6000, C[1]))]}], cat="ship",
         extra=[("Silkworm", spot(P["Ras Nasrani"], 270, 1500, "Silkworm", margin=200),
                 [{"type": "hy_launcher", "count": 2}, {"type": "Silkworm_SR", "count": 1}])])
    return Z


if __name__ == "__main__":
    b = Batch()
    for name, c, r, fname, menu, text, side, cat, groups, statics, extra in zones():
        if cat == "ship":
            sea(c, name, margin=1500 if r > 5000 and name != "combatZone_Tiran" else 1000)
        for g in groups:
            for q in g.get("route") or []:
                (sea if cat == "ship" else land)((q["x"], q["y"]), f"{name} route", 1000 if cat == "ship" else 100)
        cz = {"friendly_name": fname, "radio_group_name": menu, "training": False,
              "briefing": f"{text}\n{position_text(c)} {tankers_text(c)}"}
        b.act("create_combat_zone", zone_name=name, position=xy(c), radius=r, groups=groups, **side,
              category=cat, combat_zone=cz)
        for i, (typ, p) in enumerate(statics, 1):
            b.act("add_group", **side, category="static", name=f"Static-{typ.strip('.').split()[0]}-{i}",
                  position=xy(p), units=[{"type": typ}], for_combat_zone=name, keep_position=True)
        for gname, p, units in extra:
            b.act("add_group", **side, category="vehicle", name=gname, position=xy(p), units=units,
                  for_combat_zone=name, keep_position=True)
        print(f"{fname:52} {round(c[0]):>8} {round(c[1]):>8}  r={r}")
    # Drone laser sur la ligne du col de Mitla (SA-13 et Shilka seulement)
    b.act("add_air_group", **BLUE, name="Reaper 2", unit_type="MQ-9 Reaper", count=1, start="air",
          position=xy(P["Mitla Pass"]), altitude_ft=10000, speed_kt=110, task="AFAC", skill="High")
    b.save("08-zones.json")
