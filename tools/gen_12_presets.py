"""Écrit src/presets.yaml (plan radio du Sinaï), puis les canaux de base par set_airfield_channels.

Bande des tours (describe_airfield_channels, 12/10/2026) : UHF 250.05-252.25 (une tour tous les 50 kHz, plus
225.9, 227.15, 227.85), VHF 118.0-134.6 éparpillée, FM 38.4-42.2. Tout le reste est hors de cette bande :
AWACS 282-286, ravitailleurs 290-294 (dernier chiffre = TACAN 50Y-53Y), S-3B 296-297 (56Y, 57Y), porte-avions
305-307, patrouilles VHF 130.0-130.9 / UHF 390-395.5, FARP 127.5-129.0 (AM, fréquences posées au lot 05b),
balises touristiques FM 31-34.
Une radio tient 20 canaux : UHF bleue = Guard, soutien et les 7 bases principales ; VHF bleue = Guard, FARP,
patrouilles et les 11 bases bleues.
Abu Suwayr et Ramat David partagent 251.1 dans DCS ; Ramat David n'est dans aucune liste.
"""
import yaml

from lib import M
from mcp import cat

TACTICAL = [
    ("Guard", "Guard", {"uhf": 243, "vhf": 121.5}),
    ("Overlord-1", "Overlord 1 AWACS ouest", {"uhf": 282.0}),
    ("Magic-1", "Magic 1 AWACS est", {"uhf": 283.0}),
    ("Wizard-1", "Wizard 1 AWACS", {"uhf": 284.0}),
    ("Darkstar-1", "Darkstar 1 Arène", {"uhf": 285.0}),
    ("Focus-1", "Focus 1 Arène", {"uhf": 286.0}),
    ("Texaco-1", "Texaco 1/BS/50Y", {"uhf": 290.0}),
    ("Arco-1", "Arco 1/BM/51Y", {"uhf": 291.0}),
    ("Texaco-2", "Texaco 2/BS/52Y", {"uhf": 292.0}),
    ("Arco-2", "Arco 2/BM/53Y", {"uhf": 293.0}),
    ("Shell-1", "Shell 1 IL-78", {"uhf": 294.0}),
    ("S3B-Stennis", "S-3B Stennis/56Y", {"uhf": 296.0}),
    ("S3B-Roosevelt", "S-3B Roosevelt/57Y", {"uhf": 297.0}),
    ("Stennis", "Stennis/74X/ICLS11", {"uhf": 305.0}),
    ("Roosevelt", "Roosevelt/71X/ICLS12", {"uhf": 306.0}),
    ("Tarawa", "Tarawa/73X/ICLS13", {"uhf": 307.0}),
    ("FARP-Pyramides", "FARP Pyramides", {"vhf": 127.5}),
    ("FARP-Range", "FARP Range", {"vhf": 128.0}),
    ("FARP-Canal", "FARP Canal", {"vhf": 128.5}),
    ("FARP-Negev", "FARP Negev", {"vhf": 129.0}),
]
BLUE_FLIGHTS = ["Archer", "Arctic", "Astro", "Nickel"]
RED_FLIGHTS = ["Berkut", "Sokol", "Strizh", "Vityaz", "Kobra", "Rus"]
BLUE_MAIN = ["Cairo West", "Abu Suwayr", "Fayed", "Hurghada International Airport", "Hatzerim", "Ramon Airbase",
             "Nevatim"]
BLUE_BASES = BLUE_MAIN + ["Inshas Airbase", "Beni Suef", "Kedem", "Ben-Gurion"]
RED_BASES = ["El Arish", "Melez", "St Catherine", "El Gora", "Bir Hasanah", "Abu Rudeis",
             "Sharm El Sheikh International Airport"]


def numbered(items):
    return {i: v for i, v in enumerate(items, 1)}


def fm_list():
    return {i: mhz for i, mhz in enumerate(range(30, 60), 1) if i <= 20}


guard_uhf = {"title": "Guard/UHF", "channel": "Guard"}
guard_vhf = {"title": "Guard/VHF", "channel": "Guard"}


def bases(names):
    return ["Base-" + b for b in names]


doc = {
    "channel_lists": {
        "blue": {
            "primary_1": numbered([guard_uhf, "Overlord-1", "Magic-1", "Texaco-1", "Arco-1", "Texaco-2", "Arco-2",
                                   "Stennis", "Roosevelt", "Tarawa", "S3B-Stennis", "S3B-Roosevelt", "Darkstar-1",
                                   *bases(BLUE_MAIN)]),
            "primary_2": numbered([guard_vhf, "FARP-Pyramides", "FARP-Range", "FARP-Canal", "FARP-Negev",
                                   *BLUE_FLIGHTS, *bases(BLUE_BASES)]),
            "fm_supplement": fm_list(),
        },
        "red": {
            "primary_1": numbered([guard_uhf, "Wizard-1", "Shell-1", "Focus-1", *bases(RED_BASES)]),
            "primary_2": numbered([guard_vhf, *RED_FLIGHTS, *bases(RED_BASES)]),
            "fm_supplement": fm_list(),
        },
    },
    # Gabarit 6.29 : le Mi-8 garde ses radios d'origine, le CH-47 reçoit un jeu FM/UHF ; l'exclusion de tous les
    # appareils rouges (`red: plane: all: none`) est retirée, puisque le rouge vole ici.
    "presets_assignments": {"blue": {"helicopter": {"Mi-8MT": "none", "CH-47Fbl1": "modern_blue_fm_uhf"}}},
    "radios_collection": {"blue_radios": {
        "radio_uhf_30": {"title": "UHF", "type": "uhf", "channels": None},
        "radio_fm_30": {"title": "FM", "type": "fm", "channels": {i: 29 + i for i in range(1, 31)}},
    }},
    "presets_collection": {"blue_presets": {"modern_blue_fm_uhf": {
        "title": "Blue coalition - FM/UHF (CH-47)", "radios": {"radio_1": "radio_fm_30", "radio_2": "radio_uhf_30"}}}},
    "channels_collection": {
        "tactical": {k: {"title": t, "freqs": f} for k, t, f in TACTICAL},
        "flights": {
            **{n: {"title": n, "freqs": {"vhf": round(130.0 + i / 10, 1), "uhf": round(390.0 + i / 10, 1)}}
               for i, n in enumerate(BLUE_FLIGHTS)},
            **{n: {"title": n, "freqs": {"vhf": round(130.0 + (i + len(BLUE_FLIGHTS)) / 10, 1),
                                         "uhf": round(395.0 + i / 10, 1)}}
               for i, n in enumerate(RED_FLIGHTS)},
        },
        "bases": {},
    },
}
HEADER = """# Plan radio de l'Open Training Sinaï — écrit par tools/gen_12_presets.py, ne pas éditer à la main.
# Hors bande des tours : les tours du théâtre occupent UHF 250.05-252.25 (et 225.9, 227.15, 227.85), une partie
# de la VHF 118.0-134.6, FM 38.4-42.2 (describe_airfield_channels, 12/10/2026). AWACS 282-286, ravitailleurs
# 290-294 (dernier chiffre = TACAN), S-3B 296-297, porte-avions 305-307, patrouilles VHF 130.0-130.9 /
# UHF 390-395.5, FARP 127.5-129.0.
# Les canaux d'aérodromes (collection `bases`) viennent de set_airfield_channels : fréquences DCS.
"""
doc["radios_collection"]["blue_radios"]["radio_uhf_30"]["channels"] = doc["channel_lists"]["blue"]["primary_1"]

if __name__ == "__main__":
    for side in ("blue", "red"):
        for name, lst in doc["channel_lists"][side].items():
            assert len(lst) <= 20, (side, name, len(lst))
    path = M + "/src/presets.yaml"
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER)
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
    print(cat.run_action("set_airfield_channels", {"mission_path": M, "airfields": BLUE_BASES + RED_BASES}))
