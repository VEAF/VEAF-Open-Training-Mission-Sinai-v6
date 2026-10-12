"""Lot 04 : camp de chaque aérodrome et slots dynamiques.

Bleu avec slots (11) : en Égypte Cairo West (base mère), Inshas, Beni Suef (arrière), Abu Suwayr et Fayed (canal,
avancées), Hurghada (sud, face à la mer Rouge) ; en Israël Hatzerim, Kedem (hélicoptères, comme en v5), Nevatim,
Ramon AB (avancée), Ben Gurion (arrière, comme en v5).
Bleu sans slots : les autres terrains d'Égypte et d'Israël. Rouge avec slots : El Arish (nord, avancée), Melez
(centre), St Catherine (arrière sud) ; les autres terrains du Sinaï rouges sans slots.
Neutres : Jordanie, Arabie saoudite, Syrie, Liban.
Les FARP viennent avec le lot 05b, une fois la grille d'altitude disponible (contrôle terre ferme).
"""
from lib import (EGYPT_NO_SLOTS, EGYPT_SLOTS, ISRAEL_NO_SLOTS, ISRAEL_SLOTS, NEUTRAL, RED_NO_SLOTS, RED_SLOTS,
                 Batch)

if __name__ == "__main__":
    b = Batch()
    for n in EGYPT_SLOTS + ISRAEL_SLOTS:
        b.act("set_airbase_coalition", name=n, coalition="blue")
    for n in EGYPT_NO_SLOTS + ISRAEL_NO_SLOTS:
        b.act("set_airbase_coalition", name=n, coalition="blue", dynamic_spawn=False)
    for n in RED_SLOTS:
        b.act("set_airbase_coalition", name=n, coalition="red")
    for n in RED_NO_SLOTS:
        b.act("set_airbase_coalition", name=n, coalition="red", dynamic_spawn=False)
    for n in NEUTRAL:
        b.act("set_airbase_coalition", name=n, coalition="neutral", dynamic_spawn=False)
    b.save("04-bases.json")
