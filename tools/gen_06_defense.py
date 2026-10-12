"""Lot 06 : défense aérienne permanente des bases et des arrières (#veafInterpreter).

Porteur = le lanceur que génère l'alias (l'éditeur montre son cercle de portée), nom unique.
Portées DCS (list_unit_types, threat_range_m) : Patriot 54 nm, SA-10 65 nm, SA-11 27 nm, Hawk 24 nm,
SA-6 13,5 nm, SA-15 6,5 nm, NASAMS 8,1 nm. Aucune ne doit couvrir une base adverse avec slots :
  - Israël : El Arish (rouge) est à 45 nm de Hatzerim, Kedem et Ramon : Hawk et NASAMS là, Patriot seulement à
    Nevatim (62 nm) et Ben Gurion (80 nm) ;
  - canal : Melez (rouge) est à 46 nm de Fayed et 55 nm d'Abu Suwayr : Hawk sur le canal, Patriot au Caire et à
    Inshas (88 nm) ;
  - rouge : SA-11 à El Arish et Melez (27 nm < 44 nm), SA-10 à St Catherine (Hurghada à 91 nm, Ramon à 129 nm)
    et au centre-sud du Sinaï (Fayed à 81 nm, Ramon à 96 nm).
Le contrôle des distances est check_portees.py. Chaque emplacement est ramené sur la terre ferme (grille DCS).
"""
from lib import AIRFIELDS, BLUE_EG, BLUE_IL, PLACES, RED, Batch, interp_unit, land, spot, xy

A = AIRFIELDS

# (camp, nom de groupe, centre, relèvement, distance (m), alias, type du porteur, cap)
SITES = [
    # ── Bleu, Égypte : Cairo West (base mère), Inshas, Beni Suef (arrière) ──
    (BLUE_EG, "AD Cairo West Patriot", A["Cairo West"], 20, 4000, "-patriot", "Patriot ln", 60),
    (BLUE_EG, "AD Cairo West Hawk", A["Cairo West"], 200, 4500, "-hawk", "Hawk ln", 60),
    (BLUE_EG, "AD Cairo West Avenger", A["Cairo West"], 110, 2500, "-avenger_squad", "M1097 Avenger", 0),
    (BLUE_EG, "AD Inshas Patriot", A["Inshas Airbase"], 0, 4000, "-patriot", "Patriot ln", 90),
    (BLUE_EG, "AD Inshas Avenger", A["Inshas Airbase"], 180, 2000, "-avenger_squad", "M1097 Avenger", 0),
    (BLUE_EG, "AD Beni Suef Hawk", A["Beni Suef"], 90, 3500, "-hawk", "Hawk ln", 90),
    (BLUE_EG, "AD Beni Suef Avenger", A["Beni Suef"], 270, 1800, "-avenger_squad", "M1097 Avenger", 0),
    # ── Bleu, Égypte : Abu Suwayr et Fayed (canal), Hurghada (mer Rouge) ──
    (BLUE_EG, "AD Abu Suwayr Hawk", A["Abu Suwayr"], 250, 3500, "-hawk", "Hawk ln", 90),
    (BLUE_EG, "AD Abu Suwayr Avenger", A["Abu Suwayr"], 60, 1800, "-avenger_squad", "M1097 Avenger", 0),
    (BLUE_EG, "AD Fayed Hawk", A["Fayed"], 270, 4000, "-hawk", "Hawk ln", 90),
    (BLUE_EG, "AD Fayed Avenger", A["Fayed"], 180, 1800, "-avenger_squad", "M1097 Avenger", 0),
    (BLUE_EG, "AD Hurghada Hawk", A["Hurghada International Airport"], 270, 4000, "-hawk", "Hawk ln", 60),
    (BLUE_EG, "AD Hurghada Avenger", A["Hurghada International Airport"], 0, 1800, "-avenger_squad", "M1097 Avenger", 0),
    # ── Bleu, Israël : Hatzerim / Kedem, Ramon AB (avancées), Nevatim, Ben Gurion (arrière) ──
    (BLUE_IL, "AD Hatzerim Hawk", A["Hatzerim"], 60, 4500, "-hawk", "Hawk ln", 240),
    (BLUE_IL, "AD Hatzerim NASAMS", A["Hatzerim"], 200, 2500, "-nasams", "NASAMS_LN_C", 240),
    (BLUE_IL, "AD Kedem Avenger", A["Kedem"], 330, 1200, "-avenger_squad", "M1097 Avenger", 0),
    (BLUE_IL, "AD Ramon Hawk", A["Ramon Airbase"], 60, 4000, "-hawk", "Hawk ln", 240),
    (BLUE_IL, "AD Ramon NASAMS", A["Ramon Airbase"], 240, 2000, "-nasams", "NASAMS_LN_C", 240),
    (BLUE_IL, "AD Nevatim Patriot", A["Nevatim"], 30, 4500, "-patriot", "Patriot ln", 240),
    (BLUE_IL, "AD Nevatim Avenger", A["Nevatim"], 210, 1800, "-avenger_squad", "M1097 Avenger", 0),
    (BLUE_IL, "AD Ben Gurion Patriot", A["Ben-Gurion"], 120, 4000, "-patriot", "Patriot ln", 210),
    (BLUE_IL, "AD Ben Gurion Avenger", A["Ben-Gurion"], 300, 1800, "-avenger_squad", "M1097 Avenger", 0),
    # ── Bleu : guet, derrière les lignes ──
    (BLUE_EG, "EWR Mokattam", PLACES["Cairo Citadel"], 90, 5000, "-blue_ewr", "FPS-117 Dome", 0),
    (BLUE_EG, "EWR Ain Sokhna", PLACES["Ain Sokhna"], 270, 12000, "-blue_ewr", "FPS-117 Dome", 0),
    (BLUE_IL, "EWR Mitzpe Ramon", PLACES["Mitzpe Ramon"], 0, 2000, "-blue_ewr", "FPS-117 Dome", 0),
    (BLUE_IL, "EWR Dimona", PLACES["Dimona"], 90, 4000, "-blue_ewr", "FPS-117 Dome", 0),
    # ── Rouge : El Arish (avancée), Melez (centre), St Catherine (arrière) ──
    (RED, "AD El Arish SA-11", A["El Arish"], 270, 5000, "-sa11", "SA-11 Buk LN 9A310M1", 60),
    (RED, "AD El Arish SA-15", A["El Arish"], 120, 2000, "-sa15", "Tor 9A331", 0),
    (RED, "AD Melez SA-11", A["Melez"], 90, 5000, "-sa11", "SA-11 Buk LN 9A310M1", 270),
    (RED, "AD Melez SA-15", A["Melez"], 300, 2000, "-sa15", "Tor 9A331", 0),
    (RED, "AD St Catherine SA-10", A["St Catherine"], 330, 6000, "-sa10", "S-300PS 5P85C ln", 0),
    (RED, "AD St Catherine SA-15", A["St Catherine"], 150, 2000, "-sa15", "Tor 9A331", 0),
    (RED, "AD Sinai Centre SA-10", (-50000, 215000), 0, 0, "-sa10", "S-300PS 5P85C ln", 0),
    (RED, "AD Sharm SA-15", A["Sharm El Sheikh International Airport"], 0, 2000, "-sa15", "Tor 9A331", 0),
    # ── Rouge : guet ──
    (RED, "EWR El Arish", A["El Arish"], 200, 12000, "-ewr", "55G6 EWR", 0),
    (RED, "EWR Bir Hasanah", A["Bir Hasanah"], 0, 4000, "-ewr", "55G6 EWR", 0),
    (RED, "EWR Ras Sudr", PLACES["Ras Sudr"], 90, 15000, "-ewr", "55G6 EWR", 0),
    (RED, "EWR St Catherine", A["St Catherine"], 60, 8000, "-ewr", "55G6 EWR", 0),
]

if __name__ == "__main__":
    b = Batch()
    for side, name, c, brg, dist, alias, carrier, hdg in SITES:
        p = spot(c, brg, dist, name, margin=300)
        land(p, name, margin=300)
        tag = name.replace("AD ", "").replace("EWR ", "EWR-").replace(" ", "-")
        cmd = f"{alias}, hdg {hdg}" + {"Egypt": ", country egypt", "Israel": ", country israel"}.get(side["country_name"], "")
        b.act("add_group", **side, category="vehicle", name=name, position=xy(p), keep_position=True,
              units=[interp_unit(cmd, carrier, tag)])
        print(f"{name:30} {round(p[0]):>8} {round(p[1]):>8}")
    b.save("06-defense.json")
