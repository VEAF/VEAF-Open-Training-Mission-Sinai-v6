"""Lot 05b : les quatre FARP, les trois groupes aéronavals, et les slots sur les ponts.

Après le lot 05 (ravitailleurs AVANT porte-avions, sinon les S-3B prennent Texaco11 / Arco11).
FARP (fréquences VHF AM hors des tours, plan radio gen_12_presets.py) :
  - Pyramides : 3 km au sud-ouest de Khéphren, sur le plateau désertique — hélicoptères de l'ouest et tourisme ;
  - Range : position de la v5, à 18 km du champ de tir d'Arad (famille H) ;
  - Canal : 14 km à l'ouest de Fayed, en retrait de la rive — hélicoptères du front ouest ;
  - Negev : 15 km au nord-est de Ramon AB, côté israélien — hélicoptères du front est.
Porte-avions : Stennis et Tarawa en Méditerranée aux positions de la v5 (au large d'El Arish et de Gaza),
le Roosevelt en mer Rouge, 46 nm au sud de Ras Mohammed et 59 nm de la batterie Silkworm de Tiran (portée
54 nm) quand sa zone est active ; il fait route au 160, donc s'en éloigne. Toujours Stennis et Roosevelt (décision du 02/10/2026) ; le
Tarawa vient de la v5. SA-11 d'El Arish (27 nm) à 62 nm du Tarawa ; SA-10 de St Catherine (65 nm) à 103 nm du
Roosevelt (check_portees.py).
"""
from lib import BLUE, BLUE_EG, BLUE_IL, PLACES, Batch, land, off, sea, xy

FARPS = [
    ("FARP Pyramides", off(PLACES["Pyramid of Khafre"], 225, 3000), 127.5, 1, BLUE_EG),
    ("FARP Range", (155074, 394983), 128.0, 2, BLUE_IL),
    ("FARP Canal", (25000, 85000), 128.5, 3, BLUE_EG),
    ("FARP Negev", (95000, 340000), 129.0, 4, BLUE_IL),
]

CARRIERS = [
    dict(name="CSG-74 Stennis", carrier_type="Stennis", position=(243651, 193316), heading_deg=0, speed_kt=10,
         tower_mhz=305.0, tacan_channel=74, tacan_callsign="STN", icls_channel=11, link4_mhz=336.0,
         tanker_tacan_channel=56, tanker_tacan_callsign="S74", tanker_frequency_mhz=296.0,
         escorts=["TICONDEROG", "USS_Arleigh_Burke_IIa"]),
    dict(name="CSG-71 Roosevelt", carrier_type="CVN_71", position=(-340000, 300000), heading_deg=160, speed_kt=10,
         tower_mhz=306.0, tacan_channel=71, tacan_callsign="RSV", icls_channel=12, link4_mhz=337.0,
         tanker_tacan_channel=57, tanker_tacan_callsign="S71", tanker_frequency_mhz=297.0,
         escorts=["TICONDEROG", "USS_Arleigh_Burke_IIa"]),
    dict(name="ARG-1 Tarawa", carrier_type="LHA_Tarawa", position=(224206, 256976), heading_deg=0, speed_kt=8,
         tower_mhz=307.0, tacan_channel=73, tacan_callsign="TRW", icls_channel=13, link4_mhz=None,
         recovery_tanker=False, rescue_helicopter=True, escorts=["PERRY"]),
]

DECKS = [
    # porte-avions, nom du groupe, type, nombre, départ
    ("CSG-74 Stennis", "Stennis F/A-18C #1", "FA-18C_hornet", 2, "deck-cold"),
    ("CSG-74 Stennis", "Stennis F/A-18C #2", "FA-18C_hornet", 2, "deck-hot"),
    ("CSG-74 Stennis", "Stennis F-14B #1", "F-14B", 2, "deck-cold"),
    ("CSG-71 Roosevelt", "Roosevelt F/A-18C #1", "FA-18C_hornet", 2, "deck-cold"),
    ("CSG-71 Roosevelt", "Roosevelt F-14B #1", "F-14B", 2, "deck-cold"),
    ("CSG-71 Roosevelt", "Roosevelt F-14B #2", "F-14B", 2, "deck-hot"),
    ("ARG-1 Tarawa", "Tarawa AV-8B #1", "AV8BNA", 2, "deck-cold"),
    ("ARG-1 Tarawa", "Tarawa AV-8B #2", "AV8BNA", 2, "deck-hot"),
]

if __name__ == "__main__":
    b = Batch()
    for name, p, f, cs, side in FARPS:
        land(p, name, margin=300)
        b.act("add_farp", name=name, position=xy(p), **side, frequency_mhz=f, callsign_id=cs)
        print(f"{name:16} {round(p[0]):>8} {round(p[1]):>8}")
    for c in CARRIERS:
        c = dict(c)
        p = c.pop("position")
        sea(p, c["name"], margin=8000)
        b.act("add_carrier_group", **BLUE, position=xy(p), **c)
    for carrier, name, typ, n, start in DECKS:
        b.act("add_air_group", **BLUE, name=name, unit_type=typ, count=n, start=start, carrier=carrier,
              skill="Client", task="CAP")
    b.save("05b-farps-porte-avions.json")
