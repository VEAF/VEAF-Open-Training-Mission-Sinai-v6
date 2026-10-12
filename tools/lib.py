"""Outils communs aux générateurs de lots (tools/gen_*.py).

Un générateur écrit un fichier de lot dans tools/batches/ ; `python tools/mcp.py batch <lot>` l'exécute
sur le catalogue d'actions de veaf-mission-mcp (code VMCT de develop). Un lot ne s'exécute qu'une fois.

Scénario (tracé B, David, 12/10/2026) : l'Égypte et Israël sont bleus, une force hostile (pays Russie, que
CTLD veut dans le camp rouge) occupe la péninsule du Sinaï. Deux fronts : le canal de Suez et la frontière
Rafah–Taba.

Terre / mer : la grille d'altitude SinaiMap balayée dans DCS (`veaf-tools dcs terrain-sweep SinaiMap`) ;
tant qu'elle manque, `ground()` refuse et aucun placement au sol ne se génère.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT  # noqa: E402  (met aussi le code VMCT sur sys.path)
from veaf_libs.coordinates import latlon_to_xy, xy_to_latlon  # noqa: E402
from veaf_libs.terrain_elevation import grid_for_theatre  # noqa: E402

M = ROOT.as_posix()
THEATRE = "SinaiMap"

BLUE = dict(coalition="blue", country_id=2, country_name="USA")
BLUE_EG = dict(coalition="blue", country_id=29, country_name="Egypt")
BLUE_IL = dict(coalition="blue", country_id=15, country_name="Israel")
RED = dict(coalition="red", country_id=0, country_name="Russia")

# Aérodromes (list_airfields, SinaiMap : points de référence du terrain)
AIRFIELDS = {
    "Abu Rudeis": (-128441, 188949), "Abu Suwayr": (57580, 82565), "Al Bahr al Ahmar": (-388006, 181277),
    "Al Ismailiyah": (60078, 95845), "Al Khatatbah": (30001, -35161), "Al Mansurah": (101487, 19421),
    "Al Rahmaniyah Air Base": (111445, -53679), "As Salihiyah": (81974, 77621), "AzZaqaziq": (60146, 41193),
    "Baluza": (104349, 126474), "Ben-Gurion": (217468, 348036), "Beni Suef": (-93776, -23379),
    "Bilbeis Air Base": (38473, 35431), "Bir Hasanah": (15112, 208961), "Birma Air Base": (88052, -28173),
    "Borg El Arab International Airport": (99767, -146756), "Cairo International Airport": (6583, 18420),
    "Cairo West": (7349, -33539), "Damascus Intl": (375327, 495741), "Difarsuwar Airfield": (40837, 105396),
    "Ein Shamer": (265763, 357946), "El Arish": (108775, 247388), "El Gora": (112947, 278771),
    "El Minya": (-214835, -53828), "Fayed": (30164, 98806), "Gebel El Basur Air Base": (55664, -65567),
    "Hatzerim": (131918, 327168), "Hatzor": (189869, 332622), "Hurghada International Airport": (-319085, 247648),
    "Inshas Airbase": (31533, 19894), "Jiyanklis Air Base": (87972, -99356), "Kedem": (134332, 325364),
    "Khalkhalah Air Base": (340304, 499771), "Kibrit Air Base": (20568, 120267),
    "King Feisal Air Base": (35758, 471806), "Kom Awshim": (-54135, -34872), "Megiddo": (283510, 378523),
    "Melez": (38907, 183605), "Mezzeh Air Base": (383580, 468789), "Nevatim": (129123, 360906),
    "Ovda": (-11513, 355893), "Palmachim": (205487, 329305), "Quwaysina": (59124, -10187),
    "Rafic Hariri Intl": (420155, 399041), "Ramat David": (291107, 374036), "Ramon Airbase": (80825, 328661),
    "Ramon International Airport": (-35075, 364020), "Sde Dov": (229224, 337370),
    "Sharm El Sheikh International Airport": (-229685, 306247), "St Catherine": (-151745, 273037),
    "Taba International Airport": (-50857, 341452), "Tabuk": (-181719, 522695), "TabukHeliBase": (-188034, 531109),
    "Tel Nof": (198387, 341243), "Wadi Abu Rish": (-119841, 42431), "Wadi al Jandali": (2085, 56775),
}
EGYPT_SLOTS = ["Cairo West", "Inshas Airbase", "Beni Suef", "Abu Suwayr", "Fayed", "Hurghada International Airport"]
ISRAEL_SLOTS = ["Hatzerim", "Kedem", "Nevatim", "Ramon Airbase", "Ben-Gurion"]
BLUE_SLOTS = EGYPT_SLOTS + ISRAEL_SLOTS
EGYPT_NO_SLOTS = ["Al Ismailiyah", "Al Khatatbah", "Al Mansurah", "Al Rahmaniyah Air Base", "As Salihiyah",
                  "AzZaqaziq", "Bilbeis Air Base", "Birma Air Base", "Borg El Arab International Airport",
                  "Cairo International Airport", "Difarsuwar Airfield", "El Minya", "Gebel El Basur Air Base",
                  "Jiyanklis Air Base", "Kibrit Air Base", "Kom Awshim", "Quwaysina", "Wadi Abu Rish",
                  "Wadi al Jandali", "Al Bahr al Ahmar"]
ISRAEL_NO_SLOTS = ["Hatzor", "Palmachim", "Tel Nof", "Sde Dov", "Ramat David", "Megiddo", "Ein Shamer", "Ovda",
                   "Ramon International Airport"]
RED_SLOTS = ["El Arish", "Melez", "St Catherine"]
RED_NO_SLOTS = ["El Gora", "Bir Hasanah", "Baluza", "Abu Rudeis", "Sharm El Sheikh International Airport",
                "Taba International Airport"]
NEUTRAL = ["King Feisal Air Base", "Tabuk", "TabukHeliBase", "Damascus Intl", "Mezzeh Air Base",
           "Khalkhalah Air Base", "Rafic Hariri Intl"]

_GEO = json.loads((ROOT / "tools/places.json").read_text(encoding="utf-8"))
PLACES = {k: (v["x"], v["y"]) for k, v in _GEO.items()}
# Géocodage tombé sur un homonyme ou introuvable : coordonnées géographiques réelles (Wikipédia), converties
for _n, (_la, _lo) in {
    "Great Sphinx of Giza": (29.9753, 31.1376), "El Qantara": (30.8556, 32.3125), "Bir Tamada": (30.15, 33.50),
    "Mount Sinai": (28.5394, 33.9750), "Fayoum": (29.3084, 30.8428), "Zafarana": (29.1167, 32.65),
    "Jebel Maghara": (30.70, 33.40), "Giddi Pass": (30.17, 32.90), "Jebel Libni": (30.70, 33.80),
    "Abu Ageila": (30.85, 34.12), "Sheikh Zuweid": (31.2167, 34.1167), "Rumana, North Sinai": (31.0167, 32.6667),
    "El Quseima": (30.67, 34.37), "Kuntilla": (29.98, 34.68), "Ras Nasrani": (27.9667, 34.4167),
    "Tiran Island": (27.94, 34.56),
}.items():
    PLACES[_n] = tuple(round(c) for c in latlon_to_xy(THEATRE, _la, _lo))

# Bullseye commun : l'aérodrome de Bir Hasanah, au centre du Sinaï, à mi-chemin du canal et de la frontière ; pas
# Bir Gifgafa, qui est le centre du cercle de la QRA de Melez
BULLSEYE = AIRFIELDS["Bir Hasanah"]


def nm(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1]) / 1852


def km(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1]) / 1000


def off(p, brg, m):
    """Point à `m` mètres de `p`, au relèvement `brg` (degrés vrais, x = nord, y = est)."""
    r = math.radians(brg)
    return (p[0] + m * math.cos(r), p[1] + m * math.sin(r))


def bearing(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 360


def bullseye(p):
    """« 123°/45 nm » depuis le bullseye : cap = atan2(Δy, Δx)."""
    return f"{bearing(BULLSEYE, p):03.0f}°/{nm(BULLSEYE, p):.0f} nm"


def xy(p):
    return {"x": round(p[0]), "y": round(p[1])}


_GRID = None


def ground(x, y):
    global _GRID
    if _GRID is None:
        _GRID = grid_for_theatre(THEATRE)
        if _GRID is None:
            raise SystemExit("pas de grille d'altitude SinaiMap (veaf-tools dcs terrain-sweep SinaiMap)")
    return _GRID.elevation_at(x, y)


def _ring(p, r, n=12):
    return [p] + [(p[0] + r * math.cos(2 * math.pi * i / n), p[1] + r * math.sin(2 * math.pi * i / n))
                  for i in range(n)]


def is_land(p, margin=300):
    """Terre ferme : le point et un cercle de `margin` m autour sont au-dessus de 0 m (la mer vaut 0)."""
    return all((ground(*q) or 0) > 0 for q in _ring(p, margin))


def is_sea(p, margin=1000):
    return all((ground(*q) or 0) <= 0 for q in _ring(p, margin, 16))


def land(p, what, margin=300):
    if not is_land(p, margin):
        raise SystemExit(f"PAS SUR LA TERRE FERME (marge {margin} m) : {what} {p}")
    return p


def sea(p, what, margin=1500):
    if not is_sea(p, margin):
        raise SystemExit(f"PAS EN PLEINE MER (marge {margin} m) : {what} {p}")
    return p


def nearest_land(x, y, margin=300, step=100, max_r=6000):
    """Le point à terre le plus proche de (x, y), à `margin` m au moins de l'eau (anneaux croissants)."""
    if is_land((x, y), margin):
        return (x, y)
    r = step
    while r <= max_r:
        n = max(8, int(2 * math.pi * r / step))
        for i in range(n):
            a = 2 * math.pi * i / n
            p = (x + r * math.cos(a), y + r * math.sin(a))
            if is_land(p, margin):
                return (round(p[0]), round(p[1]))
        r += step
    return None


def spot(center, brg, dist, what, margin=150):
    """Point à `dist` m de `center` au relèvement `brg`, ramené sur la terre ferme la plus proche."""
    p = off(center, brg, dist)
    q = nearest_land(p[0], p[1], margin=margin)
    if q is None:
        raise SystemExit(f"pas de terre près de {what} {p}")
    return q


class Batch:
    def __init__(self):
        self.items = []

    def act(self, action, **params):
        self.items.append({"name": action, "params": {"mission_path": M, **params}})

    def save(self, name):
        path = ROOT / "tools/batches" / name
        if path.exists():
            raise SystemExit(f"{path.name} existe déjà : un lot ne se régénère pas après exécution (doublons)")
        path.write_text(json.dumps(self.items, indent=1, ensure_ascii=False), encoding="utf-8")
        print(len(self.items), "actions ->", path.relative_to(ROOT))


def cmd_unit(alias_cmd, carrier_type, tag, extra=""):
    """Faux porteur de zone : `#command="<alias ...>"` + balises de tirage + suffixe unique."""
    name = f'#command="{alias_cmd}"'
    if extra:
        name += " " + extra
    return {"type": carrier_type, "name": f"{name} #{tag}"}


def interp_unit(alias_cmd, carrier_type, tag):
    """Porteur permanent : `#veafInterpreter["<alias ...>"]` + suffixe unique."""
    return {"type": carrier_type, "name": f'#veafInterpreter["{alias_cmd}"] #{tag}'}


def seg_nm(p, a, b):
    """Distance (nm) du point p au segment ab."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy) / 1852


def ddm(p):
    """« N30°11.051' E032°45.729' » (degrés, minutes décimales : ce que saisissent la plupart des avions)."""
    lat, lon = xy_to_latlon(THEATRE, *p)

    def one(v, pos, neg, w):
        h = pos if v >= 0 else neg
        v = abs(v)
        d = int(v)
        return f"{h}{d:0{w}d}°{(v - d) * 60:06.3f}'"
    return f"{one(lat, 'N', 'S', 2)} {one(lon, 'E', 'W', 3)}"


def position_text(p):
    return f"Position : bullseye {bullseye(p)} ({ddm(p)})."


# Ravitailleurs bleus : extrémités de l'hippodrome, FL, TACAN, MHz, type de ravitaillement (gen_05_soutien.py)
TANKERS = {
    "Texaco 1": (((20000, 30000), (-40000, 30000)), 220, "50Y", 290.0, "perche"),
    "Arco 1": (((10000, 50000), (-50000, 50000)), 180, "51Y", 291.0, "panier"),
    "Texaco 2": (((150000, 395000), (90000, 395000)), 240, "52Y", 292.0, "perche"),   # lot 17 : +10 km est
    "Arco 2": (((160000, 370000), (100000, 370000)), 200, "53Y", 293.0, "panier"),
}


def tankers_text(p):
    """« Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 12 nm ; Texaco 1 (...) à 30 nm. » — le plus proche de
    chaque type, mesuré jusqu'à sa piste."""
    out = []
    for kind in ("panier", "perche"):
        n, (ab, fl, tacan, f, k) = min(((n, v) for n, v in TANKERS.items() if v[4] == kind),
                                       key=lambda kv: seg_nm(p, *kv[1][0]))
        out.append(f"{n} ({kind}, TACAN {tacan}, {f:.1f}) à {seg_nm(p, *ab):.0f} nm")
    return "Ravitailleurs : " + " ; ".join(out) + "."
