"""Écrit src/waypoints.yaml : plans de vol des groupes joueurs, par catégorie et par camp jouable.

Le build ajoute lui-même le BULLSEYE (Bir Hasanah) à chaque plan. Ravitailleurs : début de piste (lib.TANKERS,
gen_05_soutien.py). Positions des champs de tir : centres de gen_07_entrainement.py (sans grille d'altitude).
"""
import yaml

from gen_05b_farps_porte_avions import FARPS
from lib import M, TANKERS

H = (140000, 384000)
A = (-10000, -60000)
S = (-45000, -115000)
KT = 0.514444
FARP = {n: p for n, p, *_ in FARPS}
WP = {
    "TX1": (TANKERS["Texaco 1"][0][0], 22000, 300), "AR1": (TANKERS["Arco 1"][0][0], 18000, 280),
    "TX2": (TANKERS["Texaco 2"][0][0], 24000, 300), "AR2": (TANKERS["Arco 2"][0][0], 20000, 280),
    "SH1": ((-60000, 225000), 20000, 300),
    "RNG_A": (A, 3000, 250), "RNG_S": (S, 15000, 350), "RNG_H": (H, 500, 100),
    "FARP_PYR": (FARP["FARP Pyramides"], 500, 100), "FARP_RNG": (FARP["FARP Range"], 500, 100),
    "FARP_CNL": (FARP["FARP Canal"], 500, 100), "FARP_NGV": (FARP["FARP Negev"], 500, 100),
}
waypoints = {k: {"type": "Turning Point", "action": "Turning Point", "alt": round(ft * 0.3048), "alt_type": "BARO",
                 "speed": round(kt * KT, 1), "speed_type": "TAS", "x": round(p[0]), "y": round(p[1]), "name": k}
             for k, (p, ft, kt) in WP.items()}
settings = {
    "blue_planes": {"category": "plane", "coalition": "blue", "waypoints": ["TX1", "AR1", "TX2", "AR2", "RNG_A", "RNG_S"]},
    "blue_helicopters": {"category": "helicopter", "coalition": "blue",
                         "waypoints": ["FARP_PYR", "FARP_CNL", "FARP_NGV", "FARP_RNG", "RNG_H"]},
    "red_planes": {"category": "plane", "coalition": "red", "waypoints": ["SH1"]},
}
HEADER = """# Plans de vol injectés dans les groupes joueurs (Open Training Sinaï) — écrit par tools/gen_13_waypoints.py.
# TX1/AR1/TX2/AR2 = début de piste des ravitailleurs bleus ; SH1 = ravitailleur rouge ; RNG_H/A/S = champs de tir
# hélicoptères (Arad), attaque (désert de Gizeh), SEAD (désert occidental) ; FARP_PYR / CNL / NGV / RNG = FARP
# Pyramides, Canal, Negev et Range. Le build ajoute le BULLSEYE (Bir Hasanah) à chaque plan.
"""
if __name__ == "__main__":
    with open(M + "/src/waypoints.yaml", "w", encoding="utf-8") as f:
        f.write(HEADER)
        yaml.safe_dump({"waypoints": waypoints, "settings": settings}, f, allow_unicode=True, sort_keys=False)
    print("waypoints.yaml :", len(waypoints), "points,", len(settings), "plans")
