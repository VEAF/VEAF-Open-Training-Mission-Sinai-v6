"""Lot 16 : dessins F10 (add_map_drawing, pour qu'ils survivent au build).

Chaque zone a son contour à son rayon réel ET son étiquette ; lignes de front, sanctuaires, QRA, hippodromes de
soutien, arène, circuit touristique. Étiquettes sur fond clair opaque (sans fond, l'action met du noir à moitié
transparent et le texte sombre devient illisible, Caucase 29/09/2026). Pas de trait en tirets : add_map_drawing
n'écrit que du plein (VMCT FIX-OPEN-TRAINING-CAUCASUS-FINDINGS ticket 03).
Couches : Common pour ce que les deux camps partagent (front, zones, sanctuaires, QRA, arène), Blue / Red pour
les hippodromes de soutien de chaque camp. Adapté de l'OT Golfe Persique.
"""
import gen_07_entrainement as e
import gen_08_zones as z
from gen_05_soutien import SUPPORT
from gen_07b_tourisme import BEACONS
from gen_09_qra_cap import QRAS
from gen_10_joueurs import ARENA, SANCTUARIES
from lib import Batch, xy

LABEL_BG = "0xffffffe0"
RED, BLUE, ORANGE, GREEN, MAGENTA, BROWN = "0xcc0000ff", "0x0040ccff", "0xe07000ff", "0x008000ff", "0xb000b0ff", "0x8b5a00ff"

# Fronts (approximatifs) : le canal puis le milieu du golfe de Suez ; la frontière Rafah–Taba puis le milieu du golfe
# d'Aqaba jusqu'au détroit de Tiran
FRONT_OUEST = [(133671, 104500), (100000, 106000), (60668, 105000), (29445, 110000), (-9263, 125000),
               (-60000, 135000), (-120000, 170000), (-200000, 215000), (-255000, 265000)]
FRONT_EST = [(136834, 286899), (92557, 305129), (30000, 330000), (-20000, 345000), (-61233, 352675),
             (-120000, 330000), (-200000, 318000), (-240000, 315000)]


def above(c, r, gap=800):
    return (c[0] + r + gap, c[1])


b = Batch()


def circle(layer, name, c, r, color, fill="0x00000000", thickness=3):
    b.act("add_map_drawing", layer=layer, shape="circle", name=name, position=xy(c), radius=r, color=color,
          fill_color=fill, thickness=thickness)


def label(layer, name, p, text, color, size=12):
    b.act("add_map_drawing", layer=layer, shape="textbox", name=name, position=xy(p), text=text, color=color,
          fill_color=LABEL_BG, font_size=size)


def build():
    for n, pts, lp, text in [("Front ouest", FRONT_OUEST, (45000, 80000), "FRONT OUEST (approximatif) : le canal de Suez"),
                             ("Front est", FRONT_EST, (60000, 345000), "FRONT EST (approximatif) : la frontière Rafah–Taba")]:
        b.act("add_map_drawing", layer="Common", shape="line", name=n, points=[xy(q) for q in pts], color=RED,
              thickness=6)
        label("Common", f"{n} étiquette", lp, text, RED, 14)

    # ── zones d'entraînement : un cercle et une étiquette par famille (niveaux imbriqués sur le même cercle) ──
    for zone, c, r, fname, *_ in e.zones():
        if not zone.endswith("_Easy"):
            continue
        fam = fname.split()[0][0]
        text = {"H": "H1-H3 Entraînement hélicoptères — Arad", "A": "A1-A3 Entraînement attaque — désert de Gizeh",
                "S": "S1-S3 Entraînement SEAD — désert occidental"}[fam]
        circle("Common", f"Zone {zone[:-5]}", c, r, ORANGE, "0xe0700018")
        label("Common", f"Zone {zone[:-5]} étiquette", above(c, r), text, ORANGE)

    # ── tourisme : la zone, les balises et le circuit ──
    zone, c, r, fname, *_ = e.tourism()
    circle("Common", "Zone tourisme", c, r, BROWN, "0x8b5a0018")
    label("Common", "Zone tourisme étiquette", above(c, r), fname, BROWN)
    b.act("add_map_drawing", layer="Blue", shape="line", name="Circuit touristique",
          points=[xy(e.FARP_PYR), xy(c)] + [xy(p) for n, code, mhz, p, sub in BEACONS], color=BROWN, thickness=2)
    for n, code, mhz, p, sub in BEACONS:
        label("Blue", f"{n} étiquette", (p[0], p[1] + 2500), f"{code} FM {mhz:.1f}", BROWN, 10)

    # ── vraies zones de combat ──
    for zone, c, r, fname, *_ in z.zones():
        circle("Common", f"Zone {zone}", c, r, RED, "0xcc000018")
        label("Common", f"Zone {zone} étiquette", above(c, r), fname, RED, 11)

    # ── QRA ──
    for q in QRAS:
        col = MAGENTA if q["side"]["coalition"] == "red" else BLUE
        circle("Common", f"QRA {q['name']}", q["center"], q["radius"], col, thickness=2)
        label("Common", f"QRA {q['name']} étiquette", (q["center"][0] + q["radius"] - 6000, q["center"][1]),
              f"{q['name']} ({round(q['radius'] / 1852)} nm)", col, 11)

    # ── sanctuaires ──
    for name, tz, c, r, side in SANCTUARIES:
        circle("Common", name, c, r, GREEN, "0x00800018", thickness=2)
        label("Common", f"{name} étiquette", (c[0] - r - 1500, c[1]), name, GREEN, 10)

    # ── arène ──
    circle("Common", "Arène cercle", ARENA[0], ARENA[1], GREEN, thickness=3)
    label("Common", "Arène étiquette", above(ARENA[0], ARENA[1], 3000), "ARÈNE joueurs contre joueurs (slots en vol)",
          GREEN, 14)

    # ── hippodromes de soutien (hors arène) ──
    for n, typ, side, a, bb, fl, kt, f, task, beacon, esc in SUPPORT:
        if n in ("Darkstar 1", "Focus 1"):
            continue
        layer = "Blue" if side["coalition"] == "blue" else "Red"
        col = BLUE if layer == "Blue" else RED
        what = f"TACAN {beacon[0]}Y" if beacon else ("AWACS" if task == "AWACS" else typ)
        b.act("add_map_drawing", layer=layer, shape="line", name=f"Piste {n}", points=[xy(a), xy(bb)], color=col,
              thickness=4)
        label(layer, f"Piste {n} étiquette", ((a[0] + bb[0]) / 2, (a[1] + bb[1]) / 2 + 6000),
              f"{n} — {what} — U{f:.1f} — FL{fl}", col, 10)


if __name__ == "__main__":
    build()
    b.save("16-dessins.json")
