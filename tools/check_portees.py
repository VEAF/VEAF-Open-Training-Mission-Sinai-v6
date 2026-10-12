"""Contrôle des portées (prompt §4.5, §4.6, §4.7, §8), lu dans la mission elle-même.

Pour chaque arme sol-air ou navale : la défense permanente (`#veafInterpreter`) et chaque zone de combat
(`#command` et groupes natifs), avec la portée DCS de son lanceur (`threat_range_m`, les cercles de l'éditeur).
Vérifie qu'elle n'atteint :
  - aucune base adverse avec slots (aérodromes, FARP, porte-avions sur toute leur route, lue dans la mission) ;
  - pour une zone : aucune base bleue avec slots, aucune piste de ravitailleur bleu, aucune zone d'entraînement
    d'une autre famille.
Finit sur une ligne VERDICT. Écrit le tableau dans docs/portees.md.
"""
import math
import re
import sys

import paths  # noqa: F401
from gen_05_soutien import SUPPORT  # noqa: E402
from gen_05b_farps_porte_avions import FARPS  # noqa: E402
from lib import AIRFIELDS, BLUE_SLOTS, RED_SLOTS, TANKERS, ROOT  # noqa: E402
from mcp import cat  # noqa: E402
from veaf_mission_mcp.mission_folder import load_folder_mission  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
M = str(ROOT)

# alias → lanceur (le type que génère l'alias ; sa portée est celle du cercle de l'éditeur)
ALIAS_LAUNCHER = {
    "-patriot": "Patriot ln", "-hawk": "Hawk ln", "-nasams": "NASAMS_LN_C", "-avenger_squad": "M1097 Avenger",
    "-stinger": "Soldier stinger", "-sa10": "S-300PS 5P85C ln", "-sa11": "SA-11 Buk LN 9A310M1", "-sa6": "Kub 2P25 ln",
    "-sa15": "Tor 9A331", "-sa8": "Osa 9A33 ln", "-hq7": "HQ-7_LN_SP", "-sa13": "Strela-10M3", "-sa9": "Strela-1 9P31",
    "-sa18": "SA-18 Igla manpad", "-zu23": "Ural-375 ZU-23", "-shilka": "ZSU-23-4 Shilka", "-armor": "Strela-10M3",
    "-infantry": "SA-18 Igla manpad", "-sa2": "S_75M_Volhov", "-sa3": "5p73 s-125 ln", "-ewr": None, "-blue_ewr": None, "-plz05": None, "-grad": None,
}
RANGE = {}
for c in ("Air Defence", "Ship", "MissilesSS"):
    for u in cat.run_action("list_unit_types", {"category": c})["units"]:
        if u.get("threat_range_m"):
            RANGE[u["type"]] = u["threat_range_m"]
RANGE["SA-18 Igla manpad"] = RANGE.get("SA-18 Igla manpad", 5200)
NOT_AIR = {"hy_launcher", "Silkworm_SR", "Scud_B"}   # missiles sol-mer / sol-sol : pas une menace aérienne

m = load_folder_mission(ROOT)
content = m.mission_content
weapons = []   # (catégorie, propriétaire, camp, type, x, y, portée)
for side, sd in content["coalition"].items():
    for country in sd.get("country") or []:
        for cat_ in ("vehicle", "ship"):
            for g in (country.get(cat_) or {}).get("group") or []:
                for u in g["units"]:
                    name = u["name"]
                    mm = re.search(r'#(?:veafInterpreter\["|command=")(-[a-z0-9_]+)', name)
                    if mm:
                        typ = ALIAS_LAUNCHER.get(mm.group(1), u["type"])
                    else:
                        typ = u["type"]
                    if typ is None or typ in NOT_AIR or typ not in RANGE:
                        continue
                    owner = g["name"].split("-")[0] if g["name"].startswith("combatZone_") else g["name"]
                    kind = "zone" if g["name"].startswith("combatZone_") else "permanent"
                    weapons.append((kind, owner, side, typ, u["x"], u["y"], RANGE[typ]))


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


BLUE_BASES = {n: (p, p) for n, p in AIRFIELDS.items() if n in BLUE_SLOTS}
for _n, _p, *_ in FARPS:
    BLUE_BASES[_n] = (_p, _p)


def ship_route(name):
    for sd in content["coalition"].values():
        for country in sd.get("country") or []:
            for g in (country.get("ship") or {}).get("group") or []:
                if g["name"] == name:
                    pts = g["route"]["points"]
                    pts = pts if isinstance(pts, list) else [pts[k] for k in sorted(pts)]
                    return ((pts[0]["x"], pts[0]["y"]), (pts[-1]["x"], pts[-1]["y"]))
    raise KeyError(name)


for cv in ("CSG-74 Stennis", "CSG-71 Roosevelt", "ARG-1 Tarawa"):
    BLUE_BASES[f"{cv} (route)"] = ship_route(cv)
RED_BASES = {n: (AIRFIELDS[n],) * 2 for n in RED_SLOTS}
TRACKS = {n: v[0] for n, v in TANKERS.items()}
TRACKS.update({n: (a, bb) for n, typ, side, a, bb, *_ in SUPPORT if n in ("Overlord 1", "Magic 1")})
TRAINING = {}
for z in content.get("triggers", {}).get("zones", {}).values() if isinstance(content.get("triggers", {}).get("zones"), dict) else content.get("triggers", {}).get("zones", []):
    n = z["name"]
    mm = re.match(r"combatZone_(Arad|DesertGizeh|DesertOuest|Pyramides)(_|$)", n)
    if mm:
        TRAINING.setdefault(mm.group(1), ((z["x"], z["y"]), z["radius"]))

rows, bad = [], []
for kind, owner, side, typ, x, y, rng in weapons:
    p = (x, y)
    targets = dict(BLUE_BASES if side == "red" else RED_BASES)
    if kind == "zone":
        targets.update({f"piste {k}": v for k, v in TRACKS.items()})
        fam = re.match(r"combatZone_(Arad|DesertGizeh|DesertOuest|Pyramides)(_|$)", owner + "_")
        for f, (c, r) in TRAINING.items():
            if not fam or fam.group(1) != f:
                targets[f"zone d'entraînement {f}"] = ((c[0], c[1]),) * 2 + (r,)
    worst = None
    moving = next((v for k, v in BLUE_BASES.items() if k == f"{owner} (route)"), None) if side == "blue" else None
    for tname, t in targets.items():
        if moving:   # arme d'un navire en route : la distance la plus courte sur toute sa route
            d = min(seg_dist((moving[0][0] + (moving[1][0] - moving[0][0]) * k / 20,
                              moving[0][1] + (moving[1][1] - moving[0][1]) * k / 20), t[0], t[1]) for k in range(21))
            d -= t[2] if len(t) > 2 else 0
        else:
            d = seg_dist(p, t[0], t[1]) - (t[2] if len(t) > 2 else 0)
        if worst is None or d < worst[1]:
            worst = (tname, d)
    ok = worst[1] > rng
    rows.append((kind, owner, typ, rng, worst[0], worst[1], ok))
    if not ok:
        bad.append(rows[-1])

# une ligne par (propriétaire, type) : la plus défavorable
best = {}
for r in rows:
    k = (r[0], r[1], r[2])
    if k not in best or r[5] < best[k][5]:
        best[k] = r
lines = ["# Portées des défenses — contrôle de tools/check_portees.py", "",
         "Portée = `threat_range_m` du lanceur dans la base d'unités DCS (cercles de l'éditeur). Distance = au plus proche de ce que l'arme ne doit pas atteindre (base adverse avec slots ; pour une zone, aussi les pistes des ravitailleurs bleus et les zones d'entraînement des autres familles).", "",
         "| Type | Groupe ou zone | Arme | Portée (km) | Cible la plus proche | Distance (km) | |", "|---|---|---|---|---|---|---|"]
for k in sorted(best):
    kind, owner, typ, rng, tn, d, ok = best[k]
    lines.append(f"| {kind} | {owner} | {typ} | {rng / 1000:.1f} | {tn} | {d / 1000:.1f} | {'✅' if ok else '❌'} |")
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs/portees.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print(f"VERDICT : {len(weapons)} armes contrôlées, {len(bad)} à portée de ce qu'elles ne doivent pas atteindre"
      + ("" if not bad else " — " + "; ".join(f"{b[1]} {b[2]} → {b[4]} {b[5] / 1000:.1f} km" for b in bad)))
