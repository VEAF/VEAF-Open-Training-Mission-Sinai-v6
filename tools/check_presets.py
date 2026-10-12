"""Contrôle du plan radio (src/presets.yaml) : aucune fréquence deux fois dans une même liste, aucun canal
non-aérodrome sur la fréquence d'une tour du théâtre. Ligne VERDICT à la fin."""
import json
import sys

import yaml

from paths import ROOT

sys.stdout.reconfigure(encoding="utf-8")
d = yaml.safe_load((ROOT / "src/presets.yaml").read_text(encoding="utf-8"))
coll = {}
for c in d["channels_collection"].values():
    coll.update(c)
t = (ROOT / "tools/airfield_channels.json").read_text(encoding="utf-8")
towers = {}
for a in json.loads(t[t.index("{"):])["candidates"]:
    for band, f in a["freqs"].items():
        towers.setdefault(round(float(f), 3), a["name"])
bad = 0


def freqs_of(entry, band):
    if isinstance(entry, (int, float)):
        return [("fm", float(entry))]
    if isinstance(entry, dict):
        key = entry["channel"]
    else:
        key = entry
    f = coll[key]["freqs"]
    return [(b, float(v)) for b, v in f.items()], key


for side, lists in d["channel_lists"].items():
    for lname, lst in lists.items():
        seen = {}
        for ch, entry in lst.items():
            if isinstance(entry, (int, float)):
                continue
            fs, key = freqs_of(entry, None)
            band = "uhf" if lname == "primary_1" else ("vhf" if lname == "primary_2" else "fm")
            sel = [v for b, v in fs if b == band] or [v for b, v in fs]
            f = round(sel[0], 3)
            if f in seen:
                print(f"DOUBLON {side}/{lname} : {f} canaux {seen[f]} et {ch} ({key})")
                bad += 1
            seen[f] = f"{ch} ({key})"
            if not str(key).startswith("Base-") and key != "Guard" and f in towers:
                print(f"SUR UNE TOUR {side}/{lname} canal {ch} {key} {f} = {towers[f]}")
                bad += 1
        print(f"{side}/{lname}: {len(lst)} canaux")
print("VERDICT", "OK" if not bad else f"{bad} défaut(s)")
