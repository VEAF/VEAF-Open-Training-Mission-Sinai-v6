"""Render the briefing maps on a real basemap: the theatre map and the zoomed maps of each area.

Outputs: docs/carte.jpg (the README map), docs/cartes/*.jpg (the zooms), and the same pictures in
src/mission/l10n/DEFAULT/ for the DCS briefing, declared in mapResource and listed in the mission's
pictureFileName* tables (this script rewrites them, so the mission always lists exactly what was drawn).

Data: briefing_data.json (from gather.py, DCS x/y). Basemap: OpenStreetMap standard raster tiles, Web Mercator. Tiles
are cached next to this script (tiles/), so the maps can be re-rendered offline once fetched.
"""

import glob
import json
import math
import os
import re

import requests
from PIL import Image, ImageDraw, ImageFont

from paths import ROOT as _ROOT  # noqa: E402  (also puts VMCT on sys.path)
from veaf_libs import coordinates as C  # noqa: E402

S = os.path.dirname(os.path.abspath(__file__))
ROOT = str(_ROOT)
D = json.load(open(os.path.join(S, "briefing_data.json"), encoding="utf-8"))
L10N = os.path.join(ROOT, "src", "mission", "l10n", "DEFAULT")

TILE = 256
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
UA = {"User-Agent": "veaf-briefing-map/1.0 (+https://github.com/VEAF/VEAF-Mission-Creation-Tools)"}  # jamais de donnée personnelle


def ll(x, y):
    return C.xy_to_latlon("SinaiMap", x, y)


def merc01(lat, lon):
    """Web Mercator coordinates of the whole world in [0, 1] (zoom-independent)."""
    u = (lon + 180) / 360
    v = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2
    return u, v


class View:
    """A window of the basemap (Mercator [0, 1] bounds), the tile zoom it is drawn from, and its output width."""

    def __init__(self, u0, v0, u1, v1, zoom, out_w):
        self.u0, self.v0, self.u1, self.v1, self.zoom, self.out_w = u0, v0, u1, v1, zoom, out_w
        self.scale = out_w / ((u1 - u0) * 2 ** zoom * TILE)  # output px per tile px
        self.out_h = round((v1 - v0) * 2 ** zoom * TILE * self.scale)

    def px(self, x, y):
        u, v = merc01(*ll(x, y))
        k = 2 ** self.zoom * TILE * self.scale
        return ((u - self.u0) * k, (v - self.v0) * k)

    def px_per_m(self, x, y):
        """Local scale at a DCS point (Mercator stretches with latitude)."""
        return self.px_per_m_at(ll(x, y)[0])

    def px_per_m_at(self, lat):
        m_per_tilepx = 156543.03 * math.cos(math.radians(lat)) / (2 ** self.zoom)
        return self.scale / m_per_tilepx

    def centre_lat(self):
        v = (self.v0 + self.v1) / 2
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * v))))


# the view being drawn: every drawing helper reads it
V = None
NAMED = None   # zones whose name a zoom writes (the ones it frames); None: all


def px(x, y):
    return V.px(x, y)


def px_per_m(x, y):
    return V.px_per_m(x, y)


# ── basemap ────────────────────────────────────────────────────────────────────────────────
def basemap():
    cache = os.path.join(S, "tiles")
    os.makedirs(cache, exist_ok=True)
    n = 2 ** V.zoom
    X0, Y0, X1, Y1 = V.u0 * n, V.v0 * n, V.u1 * n, V.v1 * n
    tx0, ty0, tx1, ty1 = int(X0), int(Y0), int(X1), int(Y1)
    sheet = Image.new("RGB", ((tx1 - tx0 + 1) * TILE, (ty1 - ty0 + 1) * TILE), "#f4f6f2")
    sess = requests.Session()
    for i, tx in enumerate(range(tx0, tx1 + 1)):
        for j, ty in enumerate(range(ty0, ty1 + 1)):
            f = os.path.join(cache, f"{V.zoom}_{tx}_{ty}.png")
            if not os.path.exists(f):
                url = TILE_URL.format(z=V.zoom, x=tx, y=ty)
                r = sess.get(url, headers=UA, timeout=30)
                r.raise_for_status()
                open(f, "wb").write(r.content)
            sheet.paste(Image.open(f).convert("RGB"), (i * TILE, j * TILE))
    # crop the window then scale to the output size
    box = (round((X0 - tx0) * TILE), round((Y0 - ty0) * TILE), round((X1 - tx0) * TILE), round((Y1 - ty0) * TILE))
    return sheet.crop(box).resize((V.out_w, V.out_h), Image.LANCZOS)


# ── drawing helpers ────────────────────────────────────────────────────────────────────────
FONT = r"C:\Windows\Fonts\segoeui.ttf"
FONTB = r"C:\Windows\Fonts\segoeuib.ttf"
FONTI = r"C:\Windows\Fonts\segoeuii.ttf"


def font(size, bold=False, italic=False):
    return ImageFont.truetype(FONTB if bold else FONTI if italic else FONT, size)


BLUE, RED, TKB, TKR, GREEN, INK, FRONT = "#1f5fbf", "#c2362b", "#0b86a8", "#c96a10", "#2e7f38", "#1b2629", "#a4221a"
HALO = "#ffffff"


def dashed(draw, a, b, fill, width, dash=(14, 8)):
    dashed_poly(draw, [a, b], fill, width, dash)


def dashed_poly(draw, pts, fill, width, dash):
    """Dashes along a polyline, the pattern running on across vertices (short segments would otherwise draw solid)."""
    left, on = dash[0], True  # what remains of the current dash or gap
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        length = math.hypot(bx - ax, by - ay)
        if length == 0:
            continue
        ux, uy = (bx - ax) / length, (by - ay) / length
        t = 0.0
        while t < length:
            t2 = min(t + left, length)
            if on:
                draw.line([(ax + ux * t, ay + uy * t), (ax + ux * t2, ay + uy * t2)], fill=fill, width=width)
            left -= t2 - t
            t = t2
            if left <= 1e-9:
                on = not on
                left = dash[0] if on else dash[1]


def obstacles():
    """Pixels where a mission object or its name sits: a line's name keeps away from them."""
    pts = []
    for o in D["bases"] + D["farps"] + D["zones"]:
        x, y = px(o["x"], o["y"])
        pts += [(x + k * 40, y) for k in range(6)]  # the object and its name, written to its right
    for s in D["support"] + D["caps"]:
        a, b = px(s["a"]["x"], s["a"]["y"]), px(s["b"]["x"], s["b"]["y"])
        pts += [(a[0] + (b[0] - a[0]) * k / 8, a[1] + (b[1] - a[1]) * k / 8) for k in range(9)]
    return pts


def clear_point(line, inset=150, step=30):
    """The point of a line, well inside the view, farthest from every other object (a zoom shows part of it)."""
    obs, best = obstacles(), None
    for a, b in zip(line, line[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        for k in range(n + 1):
            p = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
            if not (inset < p[0] < V.out_w - inset and inset < p[1] < V.out_h - inset):
                continue
            score = min(math.hypot(p[0] - o[0], p[1] - o[1]) for o in obs)
            if best is None or score > best[0]:
                best = (score, p)
    return best[1] if best else None


def dashed_circle(draw, c, r, fill, width, dash):
    n = max(48, int(r / 6))
    ring = [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
    dashed_poly(draw, ring, fill, width, dash)


def label(draw, xy, text, fill, size=17, bold=True, anchor="la", italic=False, halo=3):
    draw.text(xy, text, font=font(size, bold, italic), fill=fill, anchor=anchor, stroke_width=halo, stroke_fill=HALO)


def disc(draw, c, r, fill, outline, w=3):
    draw.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=fill, outline=outline, width=w)


# label placement chosen by eye on the rendered maps, to keep names off each other
QRA_LABEL_BELOW = set()
QRA_LABEL_LEFT = set()
TRAINING_LABEL_RIGHT = set()
SHORT_NAME = {"Hurghada International Airport": "Hurghada", "Inshas Airbase": "Inshas", "Ramon Airbase": "Ramon AB",
              "Sharm El Sheikh International Airport": "Sharm"}  # theatre map only
SUPPORT_LABEL_AT_END = set()
BASE_LABEL_LEFT = set()
FARP_LABEL_BELOW = set()
TRAINING_LABEL_LEFT = set()
FRONT_LABEL_AT = (0, 0)  # vertex of each front line where its name goes on the theatre map
# zoomed maps only: combat zone names that go left of their number (a neighbour sits on the right)
ZONE_NAME_LEFT = {"combatZone_ConvoiNakhl", "combatZone_Sharm"}  # zooms centre et sud : Nakhl (5) et Tiran (16) juste à droite
CAP_LABEL_AT_A = set()
LETTER = {"Arad": "H", "DesertGizeh": "A", "DesertOuest": "S"}
FAMILY_NAME = {"Arad": "Arad", "DesertGizeh": "Désert de Gizeh", "DesertOuest": "Désert occidental"}
TOURISM = (139, 87, 0, 255)   # marron : la zone touristique


# ── layers (common to the theatre map and the zooms) ───────────────────────────────────────
def draw_layers(img, detail):
    """Every mission object, in the view V. detail: zoomed map (zone names, SAR area, arena circle)."""
    # translucent areas (QRA discs) on their own layer
    area = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ad = ImageDraw.Draw(area)
    for q in D["qra"]:
        col = (194, 54, 43) if q["side"] == "red" else (31, 95, 191)
        c = px(q["x"], q["y"])
        r = q["radius_nm"] * 1852 * px_per_m(q["x"], q["y"])
        ad.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col + (38,), outline=col + (230,), width=3)
    img = Image.alpha_composite(img, area)
    d = ImageDraw.Draw(img)

    # QRA names
    for q in D["qra"]:
        col = RED if q["side"] == "red" else BLUE
        c = px(q["x"], q["y"])
        r = q["radius_nm"] * 1852 * px_per_m(q["x"], q["y"])
        if q["name"] in QRA_LABEL_LEFT:
            label(d, (c[0] - r - 8, c[1]), q["name"], col, 18, anchor="rm")
        elif q["name"] in QRA_LABEL_BELOW:
            label(d, (c[0], c[1] + r + 6), q["name"], col, 18, anchor="mt")
        else:
            label(d, (c[0], c[1] - r - 6), q["name"], col, 18, anchor="ms")

    # sanctuaries (dashes, the colour of the side they protect): an hexagon around each base and FARP with slots
    for z in D["sanctuaries"]:
        col = BLUE if z["side"] == "blue" else RED
        if "poly" in z:
            poly = [px(p["x"], p["y"]) for p in z["poly"]]
            dashed_poly(d, poly + poly[:1], col, 4 if detail else 3, (12, 8) if detail else (8, 6))
        else:   # cercle tiré d'une zone de déclenchement
            r = z["radius_nm"] * 1852 * px_per_m(z["x"], z["y"])
            dashed_circle(d, px(z["x"], z["y"]), r, col, 4 if detail else 3, (12, 8) if detail else (8, 6))

    # front lines (north and south)
    for k, line in enumerate(D["front"]):
        front = [px(p["x"], p["y"]) for p in line]
        dashed_poly(d, front, FRONT, 6, (22, 12))
        fm = clear_point(front) if detail else front[FRONT_LABEL_AT[k]]
        if fm:
            label(d, (fm[0] - 16, fm[1] + (0 if detail else 22)), "ligne de front (approx.)", FRONT, 18, bold=False, italic=True, anchor="rm")

    # arena: its circle on every map (it lies inside the theatre map's frame)
    az = D["arena_zone"]
    c = px(az["x"], az["y"])
    r = az["radius_nm"] * 1852 * px_per_m(az["x"], az["y"])
    dashed_circle(d, c, r, INK, 5 if detail else 3, (16, 10))
    if detail:
        label(d, (c[0], c[1] - r - 8), f"Arène (rayon {az['radius_nm']} nm)", INK, 20, anchor="ms")
    else:  # the arena AWACS tracks sit just above and below the circle
        label(d, (c[0] + r + 10, c[1]), f"Arène (rayon {az['radius_nm']} nm)", INK, 16, anchor="lm")
    if detail:
        label(d, (c[0], c[1]), f"centre : bullseye {az['be']}", INK, 17, bold=False, anchor="md")
        label(d, (c[0], c[1] + 6), az["ddm"], INK, 17, bold=False, anchor="ma")

    # CAP on demand (dashed) and support racetracks (solid, thick)
    for cp in D["caps"]:
        a, b = px(cp["a"]["x"], cp["a"]["y"]), px(cp["b"]["x"], cp["b"]["y"])
        dashed(d, a, b, RED if cp["side"] == "red" else BLUE, 4, (10, 8))
        if detail:
            m = a if cp["name"] in CAP_LABEL_AT_A else ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            label(d, (m[0] + 10, m[1]), cp["name"].split(" - ")[0], RED if cp["side"] == "red" else BLUE, 15,
                  bold=False, italic=True, anchor="lm")
    for s in D["support"]:
        a, b = px(s["a"]["x"], s["a"]["y"]), px(s["b"]["x"], s["b"]["y"])
        col = TKR if s["side"] == "red" else TKB
        d.line([a, b], fill=col, width=9)
        for p in (a, b):
            disc(d, p, 4.5, col, col, 1)
        low = s["name"] in SUPPORT_LABEL_AT_END  # label at the far end, where nothing else sits
        anc = b if low else a
        label(d, (anc[0] + 9, anc[1] + (18 if low else -6)), s["name"], col, 17)

    # bullseye, under the zones
    bu = px(D["bullseye"]["x"], D["bullseye"]["y"])
    disc(d, bu, 22, None, INK, 3)
    disc(d, bu, 3.5, INK, INK, 1)
    label(d, (bu[0] + 20, bu[1] - 20), "BULLSEYE", INK, 17, anchor="ls")

    # training zones (green, lettered) and combat zones (red, numbered as in the briefing: Z01…)
    drawn_discs = []
    for z in D["zones"]:
        c = px(z["x"], z["y"])
        if z["training"] and z["key"] == "combatZone_Pyramides":
            disc(d, c, 14, HALO, TOURISM, 4)
            label(d, (c[0], c[1]), "T", TOURISM, 16, anchor="mm", halo=0)
            if detail:   # à gauche : la balise GIZ est juste à droite du plateau
                label(d, (c[0] - 20, c[1]), "Tourisme : pyramides", TOURISM, 17, anchor="rm")
            else:
                label(d, (c[0] + 20, c[1]), "Pyramides", TOURISM, 15, anchor="lm")
            continue
        if z["training"]:
            if z["key"].endswith("_Easy"):
                fam = z["key"].split("_")[1]
                disc(d, c, 14, HALO, GREEN, 4)
                label(d, (c[0], c[1]), LETTER[fam], GREEN, 16, anchor="mm", halo=0)
                text = {"H": "Entraînement hélicoptères", "A": "Entraînement attaque", "S": "Entraînement SEAD"}[LETTER[fam]]
                if detail and fam in TRAINING_LABEL_LEFT:
                    label(d, (c[0] - 20, c[1]), f"{LETTER[fam]} {text}", GREEN, 17, anchor="rm")
                elif detail:
                    label(d, (c[0] + 20, c[1]), f"{LETTER[fam]} {text}", GREEN, 17, anchor="lm")
                elif fam in TRAINING_LABEL_RIGHT:
                    label(d, (c[0] + 18, c[1]), FAMILY_NAME[fam], GREEN, 15, anchor="lm")
                else:  # below its disc: on the theatre map a base or a FARP is often beside it
                    label(d, (c[0], c[1] + 18), FAMILY_NAME[fam], GREEN, 15, anchor="ma")
            continue
        num = int(z["name"][1:3])
        if not detail:  # theatre map: two neighbouring zones (Morek, Khan Shaykhun) would print one number over the other
            for prev in drawn_discs:
                if math.hypot(c[0] - prev[0], c[1] - prev[1]) < 26:
                    c = (prev[0] + 26, prev[1])
            drawn_discs.append(c)
        disc(d, c, 14, RED, HALO, 3)
        label(d, (c[0], c[1]), str(num), HALO, 15, anchor="mm", halo=0)
        if detail and (NAMED is None or z["key"] in NAMED):   # un zoom ne nomme que les zones qu'il cadre
            left = z["key"] in ZONE_NAME_LEFT
            label(d, (c[0] + (-20 if left else 20), c[1]), z["name"][4:], RED, 17, anchor="rm" if left else "lm")

    # tourisme : les balises radio du circuit (zooms seulement)
    if detail:
        for bc in D.get("beacons", []):
            c = px(bc["x"], bc["y"])
            d.polygon([(c[0], c[1] + 10), (c[0] + 9, c[1] - 6), (c[0] - 9, c[1] - 6)], fill=TOURISM, outline=HALO)
            label(d, (c[0] + 14, c[1]), f"{bc['code']} {bc['site']} · FM {bc['mhz']:.1f}", TOURISM, 17, anchor="lm")

    # bases and FARPs
    for b in D["bases"]:
        col = RED if b["side"] == "red" else BLUE
        c = px(b["x"], b["y"])
        d.rectangle([c[0] - 8, c[1] - 8, c[0] + 8, c[1] + 8], fill=col, outline=HALO, width=2)
        name = b["name"] if detail else SHORT_NAME.get(b["name"], b["name"])
        if b["name"] in BASE_LABEL_LEFT:
            label(d, (c[0] - 14, c[1]), name, col, 18, anchor="rm")
        else:
            label(d, (c[0] + 14, c[1]), name, col, 18, anchor="lm")
    for f in D["farps"]:
        c = px(f["x"], f["y"])
        d.polygon([(c[0], c[1] - 11), (c[0] + 11, c[1] + 8), (c[0] - 11, c[1] + 8)], fill=GREEN, outline=HALO)
        if f["name"] in FARP_LABEL_BELOW:
            label(d, (c[0], c[1] + 14), f"FARP {f['name']}", GREEN, 16, anchor="ma")
        else:
            label(d, (c[0] + 14, c[1] + 10), f"FARP {f['name']}", GREEN, 16, anchor="lm")

    # carriers (ship markers)
    for cv in D["carriers"]:
        c = px(cv["x"], cv["y"])
        d.polygon([(c[0] - 16, c[1] - 5), (c[0] + 16, c[1] - 5), (c[0] + 10, c[1] + 7), (c[0] - 10, c[1] + 7)], fill=BLUE, outline=HALO)
        label(d, (c[0] + 22, c[1]), cv["name"], BLUE, 16 if detail else 14, anchor="lm")
    return img, d


def faded_basemap():
    img = basemap().convert("RGBA")
    # slightly fade the basemap so the overlays lead
    return Image.alpha_composite(img, Image.new("RGBA", img.size, (255, 255, 255, 95)))


def attribution(d):
    label(d, (V.out_w - 24, V.out_h - 24), "Fond de carte © OpenStreetMap contributors", "#5a6668", 15,
          bold=False, anchor="rs", halo=2)


# ── theatre map ────────────────────────────────────────────────────────────────────────────
# window in lat/lon (checked against the mission: every drawn object falls inside)
LAT_N, LAT_S, LON_W, LON_E = 32.55, 26.75, 29.95, 35.75
MAIN_ZOOM, MAIN_W = 8, 2000


def render_main():
    global V
    (u0, v0), (u1, v1) = merc01(LAT_N, LON_W), merc01(LAT_S, LON_E)
    V = View(u0, v0, u1, v1, MAIN_ZOOM, MAIN_W)
    img, d = draw_layers(faded_basemap(), detail=False)
    label(d, (24, 22), "VEAF Open Training — Sinaï (moderne, 2025)", INK, 30, anchor="la")
    label(d, (24, 62), f"Bullseye : l'aérodrome de Bir Hasanah {D['bullseye']['ddm']}", INK, 17, bold=False, anchor="la")
    arena_arrow(d)
    # top right: the Mediterranean north of Lebanon is out of the frame; the legend sits over the Jordanian desert
    legend(d, (V.out_w - 24 - 470, 20))
    scalebar(d, (V.out_w - 24, V.out_h - 70), 50, px_per_m(D["bullseye"]["x"], D["bullseye"]["y"]), "échelle au bullseye")
    attribution(d)
    return img.convert("RGB")


def arena_arrow(d):
    """L'arène sort du cadre de la carte générale : une flèche en bordure, vers elle, avec sa distance."""
    az = D["arena_zone"]
    c = px(az["x"], az["y"])
    if 0 <= c[0] <= V.out_w and 0 <= c[1] <= V.out_h:
        return
    bu = px(D["bullseye"]["x"], D["bullseye"]["y"])
    ang = math.atan2(c[1] - bu[1], c[0] - bu[0])
    ts = []   # bord du cadre (avec une marge) sur la demi-droite bullseye -> arène
    for edge, val in (("x", 40), ("x", V.out_w - 40), ("y", 40), ("y", V.out_h - 40)):
        k = math.cos(ang) if edge == "x" else math.sin(ang)
        o = bu[0] if edge == "x" else bu[1]
        if abs(k) > 1e-9 and (val - o) / k > 0:
            ts.append((val - o) / k)
    t = min(ts)
    tip = (bu[0] + t * math.cos(ang), bu[1] + t * math.sin(ang))
    tail = (tip[0] - 120 * math.cos(ang), tip[1] - 120 * math.sin(ang))
    d.line([tail, tip], fill=GREEN, width=6)
    for s in (-1, 1):
        a2 = ang + math.pi + s * 0.45
        d.line([tip, (tip[0] + 26 * math.cos(a2), tip[1] + 26 * math.sin(a2))], fill=GREEN, width=6)
    dist = math.hypot(az["x"] - D["bullseye"]["x"], az["y"] - D["bullseye"]["y"]) / 1852
    label(d, (min(tip[0], tail[0]), min(tip[1], tail[1]) - 14), f"Arène à {dist:.0f} nm (zoom {len(ZOOMS)})", GREEN, 17, anchor="ls")


# ── zoomed maps ────────────────────────────────────────────────────────────────────────────
# Each zoom is named by what it must show; its window is the box around those objects (areas with their radius),
# plus a margin. The DCS briefing shows them after the theatre map, in this order.
ZOOMS = [
    ("lecaire", "Le Caire : Cairo West (base mère), Inshas, FARP Pyramides, entraînement A et S, Overlord 1, Texaco 1, Arco 1",
     ["base:Cairo West", "base:Inshas Airbase", "farp:Pyramides", "zone:combatZone_DesertGizeh_Easy",
      "zone:combatZone_DesertOuest_Easy", "support:Overlord 1", "support:Texaco 1", "support:Arco 1"]),
    ("pyramides", "Tourisme : Gizeh, Saqqarah et Dahchour depuis le FARP Pyramides",
     ["zone:combatZone_Pyramides", "farp:Pyramides", "place:Pyramid of Djoser", "place:Bent Pyramid"]),
    ("canal", "Canal de Suez : Abu Suwayr, Fayed, FARP Canal, tête de pont, Port-Fouad, croiseur",
     ["base:Abu Suwayr", "base:Fayed", "farp:Canal", "zone:combatZone_TeteDePont", "zone:combatZone_UsinesPortFouad",
      "zone:combatZone_Croiseur", "qra:QRA Abu Suwayr"]),
    ("centre", "Centre du Sinaï : Melez, Bir Hasanah, Mitla, Maghara, Nakhl, état-major",
     ["base:Melez", "qra:QRA Melez", "zone:combatZone_Mitla", "zone:combatZone_Maghara", "zone:combatZone_Nakhl",
      "zone:combatZone_ConvoiNakhl", "zone:combatZone_EtatMajor"]),
    ("nord", "Nord du Sinaï : El Arish, El Gora, Abu Ageila, djebel Libni, Stennis, Tarawa",
     ["base:El Arish", "qra:QRA El Arish", "zone:combatZone_AbuAgeila", "zone:combatZone_ConvoiElArish",
      "zone:combatZone_Scud", "zone:combatZone_ElGora", "carrier:CSG-74 Stennis", "carrier:ARG-1 Tarawa"]),
    ("negev", "Néguev : Hatzerim, Kedem, Nevatim, Ramon, FARP Negev et Range, entraînement H, Texaco 2, Arco 2",
     ["base:Hatzerim", "base:Nevatim", "base:Ramon Airbase", "farp:Negev", "farp:Range", "zone:combatZone_Arad_Easy",
      "support:Texaco 2", "support:Arco 2", "qra:QRA Hatzerim"]),
    ("sud", "Sud du Sinaï : St Catherine, Feiran, Abu Rudeis, Sharm, Tiran, Roosevelt, Hurghada",
     ["base:St Catherine", "zone:combatZone_ConvoiFeiran", "zone:combatZone_AbuRudeis", "zone:combatZone_Sharm",
      "zone:combatZone_Tiran", "carrier:CSG-71 Roosevelt", "base:Hurghada International Airport"]),
    ("arene", "Arène de combat entre joueurs (Méditerranée, au nord-ouest du delta du Nil)",
     ["arena", "support:Darkstar 1", "support:Focus 1"]),
]
ZOOM_W = 1600  # px: the DCS briefing panel shows one picture at a time, fitted
MARGIN = 0.10  # of the box, on each side
TITLE_H = 110  # px of the title band, kept clear of the objects to frame
ASPECT = (1.0, 1.5)  # width / height kept in this range, so the panel shows the zoom large


def extents(ref):
    """(x, y, radius in m) points a zoom must contain, for one reference."""
    kind, _, name = ref.partition(":")
    nm = 1852

    def one(items, key="name"):
        found = [o for o in items if o[key] == name]
        if not found:
            raise KeyError(f"zoom : {ref} absent de briefing_data.json")
        return found[0]

    if kind == "base":
        o = one(D["bases"])
        return [(o["x"], o["y"], 8 * nm)]
    if kind == "farp":
        o = one(D["farps"])
        return [(o["x"], o["y"], 8 * nm)]
    if kind == "zone":
        o = one(D["zones"], "key")
        return [(o["x"], o["y"], max(o["radius_nm"], 6) * nm)]
    if kind == "qra":
        o = one(D["qra"])
        return [(o["x"], o["y"], o["radius_nm"] * nm)]
    if kind in ("support", "cap"):
        o = one(D["support"] if kind == "support" else D["caps"])
        return [(o["a"]["x"], o["a"]["y"], 6 * nm), (o["b"]["x"], o["b"]["y"], 6 * nm)]
    if kind == "carrier":
        o = one(D["carriers"])
        return [(o["x"], o["y"], 10 * nm)]
    if kind == "place":   # un lieu réel de tools/places.json (les monuments du circuit touristique)
        pl = json.load(open(os.path.join(S, "places.json"), encoding="utf-8"))[name]
        return [(pl["x"], pl["y"], 1.5 * nm)]
    if kind == "arena":
        az = D["arena_zone"]
        return [(az["x"], az["y"], (az["radius_nm"] + 4) * nm)]
    raise KeyError(f"zoom: unknown reference {ref}")


def zoom_view(refs):
    us, vs = [], []
    for ref in refs:
        for x, y, r in extents(ref):
            for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                u, v = merc01(*ll(x + dx, y + dy))
                us.append(u)
                vs.append(v)
    u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
    w, h = u1 - u0, v1 - v0
    u0, u1, v0, v1 = u0 - w * MARGIN, u1 + w * MARGIN, v0 - h * MARGIN, v1 + h * MARGIN
    w, h = u1 - u0, v1 - v0
    # keep the aspect in range: grow the short side around the centre
    if w / h < ASPECT[0]:
        g = (h * ASPECT[0] - w) / 2
        u0, u1 = u0 - g, u1 + g
    elif w / h > ASPECT[1]:
        g = (w / ASPECT[1] - h) / 2
        v0, v1 = v0 - g, v1 + g
    # room for the title band above the box (the output keeps its width, so px scale with the width)
    v0 -= TITLE_H * (u1 - u0) / ZOOM_W
    # the tile zoom whose own resolution is closest to the output: OSM labels stay legible
    zoom = round(math.log2(ZOOM_W / ((u1 - u0) * TILE)))
    return View(u0, v0, u1, v1, zoom, ZOOM_W)


def nice_scale_nm(ppm):
    """A round scale bar about a fifth of the width."""
    target = V.out_w / 5 / ppm / 1852
    return max(n for n in (2, 5, 10, 20, 25, 50) if n <= max(target, 2))


def render_zoom(index, title, refs):
    global V, NAMED
    V = zoom_view(refs)
    NAMED = {r.split(":", 1)[1] for r in refs if r.startswith("zone:")}
    img, d = draw_layers(faded_basemap(), detail=True)
    # title band
    t = title
    sub = f"VEAF Open Training Sinaï — zoom {index} sur {len(ZOOMS)} · bullseye Bir Hasanah {D['bullseye']['ddm']}"
    tw = max(d.textlength(t, font=font(30, True)), d.textlength(sub, font=font(16))) + 40
    d.rounded_rectangle([12, 12, 12 + tw, 100], radius=8, fill=(255, 255, 255, 235), outline="#b7c1c3")
    d.text((32, 24), t, font=font(30, True), fill=INK, anchor="la")
    d.text((32, 68), sub, font=font(16), fill="#3c4a4d", anchor="la")
    ppm = V.px_per_m_at(V.centre_lat())
    scalebar(d, (V.out_w - 24, V.out_h - 70), nice_scale_nm(ppm), ppm, "échelle au centre")
    attribution(d)
    return img.convert("RGB")


# ── outputs ────────────────────────────────────────────────────────────────────────────────
def render():
    """Draw every map, write docs/ and the DCS briefing pictures, and list them in the mission. Returns the theatre map."""
    # render everything first: a failed tile download must leave the mission and its pictures as they were
    main = render_main()
    zooms = [(f"carte_{i:02d}_{slug}.jpg", render_zoom(i, title, refs)) for i, (slug, title, refs) in enumerate(ZOOMS, 1)]

    os.makedirs(os.path.join(ROOT, "docs", "cartes"), exist_ok=True)
    main.save(os.path.join(ROOT, "docs", "carte.jpg"), quality=88, optimize=True)
    # DCS briefing picture: 1600 px JPEG (keeps the .miz light; the zooms carry the detail)
    small = main.resize((1600, round(main.height * 1600 / main.width)), Image.LANCZOS)
    small.save(os.path.join(L10N, "carte.jpg"), quality=80, optimize=True)
    for old in glob.glob(os.path.join(ROOT, "docs", "cartes", "carte_*.jpg")) + glob.glob(os.path.join(L10N, "carte_*.jpg")):
        os.remove(old)  # a zoom renamed or removed must not linger in the .miz
    for name, im in zooms:
        im.save(os.path.join(ROOT, "docs", "cartes", name), quality=85, optimize=True)
        im.save(os.path.join(L10N, name), quality=80, optimize=True)
    declare_pictures(["carte.jpg"] + [name for name, _ in zooms])
    return main


def reskey(name):
    return "ResKey_ImageBriefing_" + os.path.splitext(name)[0]


def declare_pictures(pictures):
    """mapResource entries and pictureFileName* lists of the mission.

    Blue and neutral list every picture; red lists none. DCS shows the red list followed by the blue one to a player
    whose side it does not know (Client slots, dynamic slots, spectators: read in me_autobriefing.lua; the in-flight
    briefing's rule is the engine's and unverified), so the same picture in both lists shows twice. Red classic slots
    are only in the arena.
    """
    path = os.path.join(L10N, "mapResource")
    text = open(path, encoding="utf-8").read()
    nl = eol(path)
    kept = [ln for ln in text.splitlines() if "=" in ln and "ResKey_" in ln and "ResKey_ImageBriefing_" not in ln]
    lines = [f'  {reskey(p)} = "{p}",' for p in pictures] + kept
    open(path, "w", encoding="utf-8", newline=nl).write("mapResource = \n{\n" + "\n".join(sorted(lines)) + "\n}")

    mpath = os.path.join(ROOT, "src", "mission", "mission")
    mission, nl = open(mpath, encoding="utf-8").read(), eol(mpath)
    listed = "{\n" + "".join(f'    [{i}] = "{reskey(p)}",\n' for i, p in enumerate(pictures, 1)) + "  },"
    for side, value in (("B", listed), ("N", listed), ("R", "{},")):
        mission, n = re.subn(r"(?m)^  pictureFileName%s = (?:\{\},|\{\n(?:    .*\n)*?  \},)" % side,
                             f"  pictureFileName{side} = {value}", mission)
        if n != 1:
            raise RuntimeError(f"pictureFileName{side}: {n} matches in {mpath}")
    open(mpath, "w", encoding="utf-8", newline=nl).write(mission)


def eol(path):
    """The line ending a file uses (Git may check them out either way): a rewrite keeps it."""
    return "\r\n" if b"\r\n" in open(path, "rb").read(4096) else "\n"


def legend(d, origin):
    x, y = origin
    rows = [
        ("rect", BLUE, "Base bleue avec slots"), ("rect", RED, "Base rouge avec slots"),
        ("tri", GREEN, "FARP"), ("line", TKB, "Ravitailleur / AWACS bleu (hippodrome)"),
        ("line", TKR, "Ravitailleur / AWACS rouge"), ("dash", BLUE, "CAP à la demande (bleue / rouge)"),
        ("qra", RED, "QRA : rayon d'intervention"), ("num", RED, "Zone de combat (numéro du briefing)"),
        ("let", GREEN, "Entraînement : H hélicos, A attaque, S SEAD"), ("front", FRONT, "Ligne de front (approx.)"),
        ("sanct", BLUE, "Sanctuaire : pas de combat entre joueurs"), ("ship", BLUE, "Porte-avions"),
        ("arena", INK, "Arène de combat entre joueurs"),
    ]
    lh, w = 28, 470
    top = y
    y = top + len(rows) * lh + 20
    d.rounded_rectangle([x, top, x + w, y], radius=8, fill=(255, 255, 255, 235), outline="#b7c1c3")
    for i, (kind, col, text) in enumerate(rows):
        cy = top + 14 + i * lh + lh / 2
        cx = x + 22
        if kind == "rect":
            d.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=col, outline=HALO, width=2)
        elif kind == "tri":
            d.polygon([(cx, cy - 10), (cx + 10, cy + 7), (cx - 10, cy + 7)], fill=col)
        elif kind == "line":
            d.line([(cx - 14, cy), (cx + 14, cy)], fill=col, width=8)
        elif kind == "dash":
            dashed(d, (cx - 14, cy), (cx + 14, cy), col, 4, (7, 5))
        elif kind == "qra":
            disc(d, (cx, cy), 11, (194, 54, 43, 40), col, 2)
        elif kind == "num":
            disc(d, (cx, cy), 11, col, HALO, 2)
            label(d, (cx, cy), "1", HALO, 12, anchor="mm", halo=0)
        elif kind == "let":
            disc(d, (cx, cy), 11, HALO, col, 3)
            label(d, (cx, cy), "H", col, 12, anchor="mm", halo=0)
        elif kind == "sanct":
            dashed(d, (cx - 14, cy), (cx + 14, cy), col, 6, (8, 5))
        elif kind == "ship":
            d.polygon([(cx - 13, cy - 4), (cx + 13, cy - 4), (cx + 8, cy + 6), (cx - 8, cy + 6)], fill=col)
        elif kind == "arena":
            dashed(d, (cx - 14, cy), (cx + 14, cy), col, 4, (8, 5))
        elif kind == "front":
            dashed(d, (cx - 14, cy), (cx + 14, cy), col, 5, (10, 6))
        d.text((x + 46, cy), text, font=font(15), fill=INK, anchor="lm")


def scalebar(d, origin, nm, ppm, where):
    x1, y = origin
    length = nm * 1852 * ppm
    x0 = x1 - length
    d.rectangle([x0 - 6, y - 26, x1 + 6, y + 8], fill=(255, 255, 255, 220))
    d.line([(x0, y), (x1, y)], fill=INK, width=4)
    for x in (x0, x0 + length / 2, x1):
        d.line([(x, y - 8), (x, y + 4)], fill=INK, width=3)
    d.text(((x0 + x1) / 2, y - 12), f"{nm} nm ({where})", font=font(14), fill=INK, anchor="ms")


if __name__ == "__main__":
    im = render()
    print(im.size)
