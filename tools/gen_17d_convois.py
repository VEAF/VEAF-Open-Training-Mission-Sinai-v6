"""Lot 17d : les convois roulaient à 5,6 m/s (20 km/h), la vitesse que `create_combat_zone` écrit par défaut ;
mesuré en jeu le 12/10/2026 (probe_zones.py convois) : 2 à 3 m/s au départ, 1 h 30 à 4 h pour aller au bout de
routes de 31 à 78 km. Passés à 23 kt (12 m/s, environ 43 km/h) sur tous leurs points. Se rejoue sans dommage.
"""
from lib import Batch

CONVOYS = ["combatZone_ConvoiElArish-Convoi", "combatZone_ConvoiNakhl-Convoi", "combatZone_ConvoiFeiran-Convoi"]

if __name__ == "__main__":
    b = Batch()
    for g in CONVOYS:
        for i in (1, 2, 3):
            b.act("edit_route", group_name=g, operation="set", index=i, speed_kt=23)
    b.save("17d-convois.json")
