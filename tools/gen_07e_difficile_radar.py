"""Lot 07e : un vrai niveau difficile pour l'entraînement hélicoptères (FIX-OPEN-TRAINING-PILOT-FEEDBACK, ticket 01).

Retour de David après vol (15/11/2026) : le « difficile » n'était qu'un moyen, sans aucun système à guidage radar.
Décision D1 : le moyen prend le contenu de l'ancien difficile (artillerie légère + SA-13 et SA-18 à guidage
infrarouge), le difficile y ajoute deux systèmes courte portée à guidage radar tirés au sort parmi SA-15 Tor,
SA-19 Tunguska et SA-8 Osa.

  - les groupes `<zone>_Hard-H3-*` passent au niveau moyen (`<zone>_Medium-H3-*`), sans bouger ;
  - trois faux porteurs `H4-*` (`#spawngroup="H4RAD" #spawncount=2`) au niveau difficile.

Chaque lanceur est posé du côté opposé au FARP, au plus près des cibles qui laisse toute base bleue avec slots hors
de sa portée DCS (cercle de l'éditeur) avec 1 km de marge ; check_portees.py contrôle le reste (ravitailleurs, autres
familles). Le relief entre le FARP et les cibles reste le chemin d'approche.

Recalé après coup (check_portees.py) : le Tor H4-1 atteignait la piste de Texaco 2 (11,3 km). Les pistes de Texaco 2
(y = 395 000) et d'Arco 2 (y = 370 000) encadrent le champ de tir à 25 km l'une de l'autre ; le Tor ne tient qu'à
mi-chemin, posé à (138 300, 382 500) par set_group_properties : 12,5 km de chacune.
"""
import math

from gen_07_entrainement import H
from lib import AIRFIELDS, Batch, bearing, cmd_unit, off, spot, xy
from gen_05b_farps_porte_avions import FARPS

ZONE = "combatZone_Arad"
COUNTRY = ", country russia"            # suffixe de commande, ex. ", country russia" ; vide si inutile
RANGES = {"Tor 9A331": 12000, "2S6 Tunguska": 8000, "Osa 9A33 ln": 10300}   # threat_range_m (list_unit_types)
RADAR = [("-sa15", "Tor 9A331"), ("-sa19", "2S6 Tunguska"), ("-sa8", "Osa 9A33 ln")]
MEDIUM_FROM_HARD = ["H3-1", "H3-2", "H3-3", "H3-4"]
MARGIN = 1000
try:
    from lib import BLUE_SLOTS
except ImportError:  # pas de liste : toutes les bases comptent
    BLUE_SLOTS = list(AIRFIELDS)

BASES = [p for n, p in AIRFIELDS.items() if n in BLUE_SLOTS] + [f[1] for f in FARPS]
FARP = min((f[1] for f in FARPS), key=lambda p: math.dist(p, H))
AWAY = (bearing(H, FARP) + 180) % 360


def place(carrier, slot):
    """Le point le plus proche des cibles, côté opposé au FARP, d'où aucune base n'est à portée."""
    reach = RANGES[carrier] + MARGIN
    for dist in range(1500, 7001, 250):
        for delta in sorted(range(-60, 61, 10), key=abs):
            brg = (AWAY + delta + slot * 25 - 25) % 360
            if not all(math.dist(off(H, brg, dist), b) >= reach for b in BASES):
                continue
            p = spot(H, brg, dist, f"H4-{slot + 1}")   # ramené sur la terre ferme : recontrôlé
            if all(math.dist(p, b) >= reach for b in BASES):
                return p, brg, dist
    raise SystemExit(f"aucune place pour {carrier} à moins de 7 km des cibles")


if __name__ == "__main__":
    b = Batch()
    for tag in MEDIUM_FROM_HARD:
        b.act("set_group_properties", group_name=f"{ZONE}_Hard-{tag}", new_name=f"{ZONE}_Medium-{tag}",
              acknowledge_conventions=True)   # voulu : la zone moyenne capte le groupe
    for i, (alias, carrier) in enumerate(RADAR):
        p, brg, dist = place(carrier, i)
        print(f"H4-{i + 1} {alias:6} relèvement {brg:3.0f}°, {dist} m des cibles, FARP à "
              f"{math.dist(p, FARP) / 1000:.1f} km (portée {RANGES[carrier] / 1000:.1f} km)")
        b.act("add_group", coalition="red", country_id=0, country_name="Russia", category="vehicle", name=f"H4-{i + 1}",
              position=xy(p), keep_position=True, for_combat_zone=f"{ZONE}_Hard",
              units=[cmd_unit(alias + COUNTRY, carrier, f"H4-{i + 1}", '#spawngroup="H4RAD" #spawncount=2')])
    b.save("07e-difficile-radar.json")
