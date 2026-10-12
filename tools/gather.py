"""Relève dans la mission tout ce que les cartes et les briefings affichent → tools/briefing_data.json.

Sources : mission.yaml (zones, QRA, sanctuaires, actifs), src/mission/mission (positions, routes, tâches,
dessins F10 dont la ligne de front), src/mission/warehouses (camps et slots des aérodromes). Rien n'est tapé
à la main ici : relancer après tout changement de la mission.
"""

import json
import math

import yaml
from paths import ROOT, TOOLS  # noqa: F401  (met aussi VMCT sur sys.path)
from veaf_libs import coordinates as C
from veaf_mission_mcp.map_tools import list_airfields
from veaf_mission_mcp.mission_folder import load_folder_mission

NM = 1852.0
THEATRE = "SinaiMap"
CARRIER_TYPES = {"Stennis", "CVN_71", "CVN_72", "CVN_73", "CVN_75", "Forrestal", "LHA_Tarawa"}


def seq(t):
    """Une table Lua lue en Python : liste, ou dict à clés entières."""
    if t is None:
        return []
    if isinstance(t, list):
        return t
    return [t[k] for k in sorted(t, key=lambda k: int(k))]


def ddm(x, y):
    lat, lon = C.xy_to_latlon(THEATRE, x, y)

    def one(v, p, n, w):
        h = p if v >= 0 else n
        minutes = round(abs(v) * 60, 3)  # arrondi avant de séparer : jamais « 60.000' »
        d = int(minutes // 60)
        return f"{h}{d:0{w}d}°{minutes - d * 60:06.3f}'"

    return f"{one(lat, 'N', 'S', 2)} {one(lon, 'E', 'W', 3)}"


mission_obj = load_folder_mission(ROOT)
M = mission_obj.mission_content["mission"] if "mission" in mission_obj.mission_content else mission_obj.mission_content
WH = mission_obj.warehouses_content  # la table `warehouses` elle-même : airports, warehouses (FARP, navires), weapons
Y = yaml.safe_load(open(ROOT / "mission.yaml", encoding="utf-8"))
MOD = Y["modules"]

BULL = {"x": M["coalition"]["blue"]["bullseye"]["x"], "y": M["coalition"]["blue"]["bullseye"]["y"]}


def be(x, y):
    """Relèvement vrai (quadrillage DCS : x nord, y est) et distance DEPUIS le bullseye."""
    dx, dy = x - BULL["x"], y - BULL["y"]
    if math.hypot(dx, dy) < NM:
        return "sur le bullseye"
    return f"{round((math.degrees(math.atan2(dy, dx)) + 360) % 360) % 360:03d}°/{round(math.hypot(dx, dy) / NM)} nm"


# ── groupes de la mission ────────────────────────────────────────────────────────────────
groups = []
for side, coal in M["coalition"].items():
    for country in seq(coal.get("country")):
        for cat in ("plane", "helicopter", "vehicle", "ship", "static"):
            for g in seq((country.get(cat) or {}).get("group")):
                groups.append((side, country["name"], cat, g))
units_by_name = {u["name"]: (side, u) for side, _, _, g in groups for u in seq(g["units"])}


def first_tasks(g):
    pts = seq(g["route"]["points"]) if g.get("route") else []
    if not pts or "task" not in pts[0]:
        return []
    out = []
    for t in seq(pts[0]["task"]["params"].get("tasks")):
        tid = t["id"]
        if tid == "WrappedAction":
            tid = t["params"]["action"]["id"]
            if tid == "ActivateBeacon":
                p = t["params"]["action"]["params"]
                out.append(("TACAN", f"{p['channel']}{p['modeChannel']}"))
                continue
        out.append((tid, None))
    return out


# ── aérodromes ───────────────────────────────────────────────────────────────────────────
afs = {a["id"]: a for a in list_airfields(theatre=THEATRE)["airfields"]}
bases = []
exclude = {s: set(map(str, (Y_w or {}).get("exclude_airports") or []))
           for s, Y_w in (yaml.safe_load(open(ROOT / "src" / "warehouses.yaml", encoding="utf-8")) or {}).items()
           if isinstance(Y_w, dict)}
for aid, w in (WH.get("airports") or {}).items():
    coal = str(w.get("coalition", "")).lower()
    if coal not in ("blue", "red") or not w.get("dynamicSpawn"):
        continue
    a = afs[int(aid)]
    if a["name"] in exclude.get(coal, set()):
        continue
    bases.append({"name": a["name"], "side": coal, "x": round(a["x"]), "y": round(a["y"]), "be": be(a["x"], a["y"])})
bases.sort(key=lambda b: (b["side"], b["name"]))

farps = [{"name": g["name"].replace("FARP ", ""), "x": g["x"], "y": g["y"], "freq": seq(g["units"])[0].get("heliport_frequency")}
         for side, _, cat, g in groups if cat == "static" and seq(g["units"])[0].get("category") == "Heliports"
         and g["name"].startswith("FARP ")]   # pas les plates-formes pétrolières (Heliports aussi)

# ── soutien, CAP, porte-avions ───────────────────────────────────────────────────────────
support, caps, carriers = [], [], []
for side, _, cat, g in groups:
    if cat == "plane" and g["name"].startswith("OnDemand-"):
        pts = seq(g["route"]["points"])
        caps.append({"name": g["name"][len("OnDemand-"):], "side": side, "type": seq(g["units"])[0]["type"],
                     "a": {"x": pts[0]["x"], "y": pts[0]["y"]}, "b": {"x": pts[-1]["x"], "y": pts[-1]["y"]}})
        continue
    tasks = dict(first_tasks(g))
    if cat == "plane" and ("Tanker" in tasks or "AWACS" in tasks) and not g.get("lateActivation"):
        pts = seq(g["route"]["points"])
        if len(pts) < 2:
            continue  # ravitailleur embarqué : il suit son porte-avions
        u = seq(g["units"])[0]
        support.append({"name": g["name"], "side": side, "type": u["type"], "kind": "tanker" if "Tanker" in tasks else "awacs",
                        "tacan": tasks.get("TACAN"), "freq": g.get("frequency"), "alt_ft": round(u["alt"] / 0.3048, -2),
                        "a": {"x": pts[0]["x"], "y": pts[0]["y"]}, "b": {"x": pts[1]["x"], "y": pts[1]["y"]}})
    if cat == "ship" and seq(g["units"])[0]["type"] in CARRIER_TYPES:
        u = seq(g["units"])[0]
        carriers.append({"name": u["name"], "x": u["x"], "y": u["y"]})

# ── zones de trigger ─────────────────────────────────────────────────────────────────────
tz = {z["name"]: z for z in seq(M["triggers"]["zones"])}

zones = []
real_num = 0
for z in MOD["COMBATZONE"]["combat_zones"]:
    t = tz[z["zone_name"]]
    zones.append({"key": z["zone_name"], "name": z.get("friendly_name", z["zone_name"]), "training": bool(z.get("training")),
                  "menu": z.get("radio_group_name"), "x": round(t["x"]), "y": round(t["y"]), "radius_nm": t["radius"] / NM,
                  "be": be(t["x"], t["y"]), "ddm": ddm(t["x"], t["y"])})

qra = []
for q in MOD["QRA"]["definitions"]:
    t = tz[q["trigger_zone"]]
    qra.append({"name": q["name"], "side": q["coalition"].lower(), "x": round(t["x"]), "y": round(t["y"]),
                "radius_nm": round(t["radius"] / NM), "airport": q.get("airport_link")})

sanct = []
for s in MOD["SANCTUARY"]["sanctuary_zones"]:
    if s.get("trigger_zone"):   # cercle tiré d'une zone de déclenchement
        t = tz[s["trigger_zone"]]
        sanct.append({"name": s["name"], "side": s["coalition"].lower(), "x": t["x"], "y": t["y"],
                      "radius_nm": t["radius"] / NM, "radius_km": t["radius"] / 1000})
        continue
    poly = [{"x": units_by_name[u][1]["x"], "y": units_by_name[u][1]["y"]} for u in s["polygon_units"]]
    sanct.append({"name": s["name"], "side": s["coalition"].lower(), "poly": poly,
                  "x": sum(p["x"] for p in poly) / len(poly), "y": sum(p["y"] for p in poly) / len(poly)})

# ── dessins F10 : ligne de front, arène ──────────────────────────────────────────────────
front, arena = [], None
for layer in seq(M["drawings"]["layers"]):
    for o in seq(layer.get("objects")):
        if o["name"] in ("Front ouest", "Front est"):
            front.append([{"x": o["mapX"] + p["x"], "y": o["mapY"] + p["y"]} for p in seq(o["points"])])
        if o["name"] == "Arène cercle":
            arena = {"x": o["mapX"], "y": o["mapY"], "radius_nm": round(o["radius"] / NM), "be": be(o["mapX"], o["mapY"]),
                     "ddm": ddm(o["mapX"], o["mapY"])}


# ── ravitailleur le plus proche (distance au segment de piste) ───────────────────────────
def dseg(p, a, b):
    ax, ay, bx, by = a["x"], a["y"], b["x"], b["y"]
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


blue_tankers = [s for s in support if s["side"] == "blue" and s["kind"] == "tanker"]
for z in zones:
    best = {}
    for s in blue_tankers:
        kind = "perche" if s["type"] == "KC-135" else "panier"
        d = dseg((z["x"], z["y"]), s["a"], s["b"]) / NM
        if kind not in best or d < best[kind][1]:
            best[kind] = (s, d)
    z["tankers"] = " ; ".join(f"{s['name']} ({k}, TACAN {s['tacan']}, {s['freq']:.1f}) à {round(d)} nm" for k, (s, d) in sorted(best.items()))

# ── compléments pour le README (briefing des pilotes) ────────────────────────────────────
for z in zones:
    z["briefing"] = next(c["briefing"] for c in MOD["COMBATZONE"]["combat_zones"] if c["zone_name"] == z["key"]).split("\nPosition :")[0]
for b in bases + farps:
    b.setdefault("be", be(b["x"], b["y"]))
    b["ddm"] = ddm(b["x"], b["y"])
for s in support + caps:
    for k in ("a", "b"):
        s[k]["ddm"] = ddm(s[k]["x"], s[k]["y"])
    mid = ((s["a"]["x"] + s["b"]["x"]) / 2, (s["a"]["y"] + s["b"]["y"]) / 2)
    s["mid_be"] = be(*mid)
by_name = {g["name"]: (side, country, cat, g) for side, country, cat, g in groups}
for s in support:
    s["escort"] = f"{s['name']} - Escort" in by_name
for c in caps:
    g = by_name["OnDemand-" + c["name"]][3]
    u0 = seq(g["units"])[0]
    c.update(n=len(seq(g["units"])), fl=round(u0["alt"] / 0.3048 / 100))
    cm = next(x for x in Y.get("cap_missions") or [] if x["group_name"] == c["name"])
    c.update(menu=cm.get("menu_name", c["name"]), briefing=cm.get("briefing", ""))
for q in qra:
    d = next(x for x in MOD["QRA"]["definitions"] if x["name"] == q["name"])
    q["tiers"] = [{"n": t["enemy_count"], "pick": t.get("random_pick", 1),
                   "types": [f"{len(seq(by_name[gname][3]['units']))} × {seq(by_name[gname][3]['units'])[0]['type']}" for gname in t["groups"]]}
                  for t in d.get("groups_by_enemy_count") or []]
    q["ddm"], q["be"] = ddm(q["x"], q["y"]), be(q["x"], q["y"])
    q["delay"], q["helos"] = d.get("delay_before_activating", 0), bool(d.get("react_on_helicopters"))

# défense aérienne permanente : porteurs #veafInterpreter et radars d'alerte réels
ad = []
for side, country, cat, g in groups:
    u0 = seq(g["units"])[0]
    if "#veafInterpreter" in u0["name"]:
        alias = u0["name"].split('["', 1)[1].split(",")[0]
        ad.append({"name": g["name"].replace("AD ", ""), "side": side, "alias": alias, "x": u0["x"], "y": u0["y"]})
    elif u0["type"] in ("1L13 EWR", "55G6 EWR") and cat == "vehicle" and not g["name"].startswith("combatZone_"):
        ad.append({"name": g["name"], "side": side, "alias": "EWR " + u0["type"].split()[0], "x": u0["x"], "y": u0["y"]})
for a in ad:
    a["ddm"], a["be"] = ddm(a["x"], a["y"]), be(a["x"], a["y"])

# porte-avions : balises lues dans les tâches du navire
for cv in carriers:
    g = next(g for _s, _c, cat, g in groups if cat == "ship" and seq(g["units"])[0]["name"] == cv["name"])
    for t in seq(seq(g["route"]["points"])[0]["task"]["params"].get("tasks")):
        a = t["params"]["action"] if t["id"] == "WrappedAction" else None
        if not a:
            continue
        p = a.get("params", {})
        if a["id"] == "ActivateBeacon":
            cv["tacan"] = f"{p['channel']}{p['modeChannel']} {p.get('callsign', '')}".strip()
        elif a["id"] == "ActivateICLS":
            cv["icls"] = p["channel"]
        elif a["id"] == "ActivateLink4":
            cv["link4"] = p["frequency"] / 1e6
    cv["tower"] = seq(g["units"])[0].get("frequency", 0) / 1e6
    cv["group"], cv["escorts"] = g["name"], len(seq(g["units"])) - 1
    cv["ddm"], cv["be"] = ddm(cv["x"], cv["y"]), be(cv["x"], cv["y"])
    cv["deck"] = [{"group": dg["name"], "type": seq(dg["units"])[0]["type"], "n": len(seq(dg["units"]))}
                  for _s, _c, cat, dg in groups if cat == "plane" and seq(dg["route"]["points"])[0].get("linkUnit") == seq(g["units"])[0]["unitId"]]

# drones laser, arène
assets = {a["name"]: a for a in MOD["ASSETS"]["assets"]}
drones = []
for side, country, cat, g in groups:
    if cat == "plane" and g.get("task") == "AFAC":
        a = assets.get(g["name"], {})
        u0 = seq(g["units"])[0]
        drones.append({"name": g["name"], "type": u0["type"], "where": a.get("description", "").split("— ")[-1], "jtac": a.get("jtac"),
                       "freq": a.get("freq"), "mod": a.get("mod"), "be": be(u0["x"], u0["y"]), "ddm": ddm(u0["x"], u0["y"])})
arena_slots = [{"group": g["name"], "side": side, "type": seq(g["units"])[0]["type"], "n": len(seq(g["units"])),
                "fox": "Fox 3" if "Fox 3" in g["name"] else "Fox 1", "fl": round(seq(g["units"])[0]["alt"] / 0.3048 / 100)}
               for side, country, cat, g in groups if cat == "plane" and g["name"].startswith("Arène")]

# plan radio et canaux de base (src/presets.yaml), variantes météo (src/versions.yaml)
P = yaml.safe_load(open(ROOT / "src" / "presets.yaml", encoding="utf-8"))
channels = {k: v["freqs"] for coll in P["channels_collection"].values() for k, v in coll.items()}
titles = {k: v.get("title", k) for coll in P["channels_collection"].values() for k, v in coll.items()}
radio = {side: {role: {int(n): (c["channel"] if isinstance(c, dict) else c) for n, c in lst.items()}
                for role, lst in roles.items() if role != "fm_supplement"} for side, roles in P["channel_lists"].items()}
for b in bases:
    b.update(channels.get(f"Base-{b['name']}", {}))
# pas de variantes météo dans une Open Training (le serveur fixe météo et heure) : la météo de base de la mission
W = M["weather"]
weather = {"temperature": W["season"]["temperature"], "wind_from": (W["wind"]["atGround"]["dir"] + 180) % 360,
           "wind_ms": W["wind"]["atGround"]["speed"], "clouds": "aucun" if not W["clouds"].get("density") else "oui",
           "visibility_km": min(W["visibility"]["distance"], 10000) / 1000,
           "sky": (f"quelques nuages à {round(W['clouds']['base'] / 0.3048, -2):,.0f} ft".replace(",", " ")
                   if W["clouds"].get("preset") else "ciel dégagé")}

# ── tourisme : balises (gen_07b_tourisme.py) à leur position dans la mission ─────────────────
from gen_07b_tourisme import BEACONS  # noqa: E402
from lib import PLACES as _P  # noqa: E402

_pos = {}
for _side, _co in M["coalition"].items():
    for _c in seq(_co.get("country")):
        for _g in seq((_c.get("vehicle") or {}).get("group")):
            _pos[_g["name"]] = (_g["x"], _g["y"])
beacons = [{"code": code, "site": sub.split(" — ")[1], "mhz": mhz, "ddm": ddm(*_pos[n]), "be": be(*_pos[n]),
            "x": _pos[n][0], "y": _pos[n][1]} for n, code, mhz, p, sub in BEACONS if n in _pos]
# longueur des deux fronts, de bout en bout (lieux réels)
fronts_nm = [round(math.hypot(_P[a][0] - _P[b][0], _P[a][1] - _P[b][1]) / NM)
             for a, b in (("Port Said", "Suez, Egypt"), ("Rafah, North Sinai", "Taba, Egypt"))]

D = {"name": Y["mission"]["name"], "date": M["date"], "start": M["start_time"],
     "bullseye": {**BULL, "ddm": ddm(BULL["x"], BULL["y"])}, "bases": bases, "farps": farps, "support": support, "caps": caps,
     "carriers": carriers, "zones": zones, "qra": qra, "sanctuaries": sanct, "front": front, "arena_zone": arena,
     "ad": ad, "drones": drones, "arena_slots": arena_slots, "radio": radio, "channels": channels, "titles": titles,
     "weather": weather, "beacons": beacons, "fronts_nm": fronts_nm, "combat_missions": [{"name": c["friendly_name"], "briefing": c["briefing"]} for c in Y.get("combat_missions") or []]}
json.dump(D, open(TOOLS / "briefing_data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"bases {len(bases)}, FARP {len(farps)}, soutien {len(support)}, CAP {len(caps)}, porte-avions {len(carriers)}, "
      f"zones {len(zones)}, QRA {len(qra)}, sanctuaires {len(sanct)}, fronts {len(front)}, arène {'oui' if arena else 'NON'}")
