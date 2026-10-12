"""Lot 11 : configuration de mission.yaml — identité, profils, modules, ASSETS, SANCTUARY, missions scénarisées,
réglages CTLD. Se rejoue sans doublon (il écrit des blocs, il n'ajoute pas de groupes).

Un nom partout : nom de groupe = indicatif = libellé de preset = texte ASSETS. Chaque camp ne voit que ses
moyens (coalition). Drones : code laser imposé et fréquence que CTLD calcule pour ce code (35.55 / 35.6 FM,
mesuré sur Syrie v6, limitation ctld-jtac-imposed-code-and-radio), sous un jtacLaserCodeMax abaissé à 1686.
CTLD : rayon logistique des aérodromes 2 500 m. Pas de données de parking Sinaï pour le mesurer ici ; 2 500 m
couvrent 81 % des 254 places d'Al Dhafra (mesuré sur l'OT Golfe Persique), base de la taille de Cairo West.
Météo : pas de variantes (le serveur VEAF fixe météo et heure, décision de David du 12/10/2026) ; une météo de
base plausible est posée par gen_15_identite.py.
"""
import sys
from pathlib import Path

from ruamel.yaml import YAML

from gen_10_joueurs import SANCTUARIES
from lib import M, ROOT

sys.stdout.reconfigure(encoding="utf-8")

ASSETS = [
    ("Overlord 1", "Overlord 1 (E-3A) — AWACS ouest", "BLUE", "U282.0 — FL300 — orbite nord-sud à l'ouest de Cairo West", "Overlord 1 - Escort"),
    ("Magic 1", "Magic 1 (E-3A) — AWACS est", "BLUE", "U283.0 — FL300 — orbite du large d'Ashdod au Néguev", "Magic 1 - Escort"),
    ("Texaco 1", "Texaco 1 (KC-135, perche) — canal", "BLUE", "TACAN 50Y TX1 — U290.0 — FL220 — piste nord-sud à l'est du Caire", "Texaco 1 - Escort"),
    ("Arco 1", "Arco 1 (KC-135 MPRS, panier) — canal", "BLUE", "TACAN 51Y AR1 — U291.0 — FL180 — piste nord-sud près de la nouvelle capitale administrative", "Arco 1 - Escort"),
    ("Texaco 2", "Texaco 2 (KC-135, perche) — Néguev", "BLUE", "TACAN 52Y TX2 — U292.0 — FL240 — piste nord-sud au-dessus de la rive ouest de la mer Morte", "Texaco 2 - Escort"),
    ("Arco 2", "Arco 2 (KC-135 MPRS, panier) — Néguev", "BLUE", "TACAN 53Y AR2 — U293.0 — FL200 — piste nord-sud au-dessus de Nevatim", "Arco 2 - Escort"),
    ("CSG-74 Stennis", "CVN-74 Stennis — Méditerranée", "BLUE", "TACAN 74X STN — ICLS 11 — Link 4 336.0 — ACLS — U305.0", None),
    ("CSG-71 Roosevelt", "CVN-71 Roosevelt — mer Rouge", "BLUE", "TACAN 71X RSV — ICLS 12 — Link 4 337.0 — ACLS — U306.0", None),
    ("ARG-1 Tarawa", "LHA-1 Tarawa — Méditerranée", "BLUE", "TACAN 73X TRW — ICLS 13 — U307.0", None),
    ("CSG-74 Stennis S3B-Tanker", "S-3B du Stennis (ravitailleur embarqué)", "BLUE", "TACAN 56Y S74 — U296.0", None),
    ("CSG-71 Roosevelt S3B-Tanker", "S-3B du Roosevelt (ravitailleur embarqué)", "BLUE", "TACAN 57Y S71 — U297.0", None),
    ("Darkstar 1", "Darkstar 1 (E-3A) — AWACS bleu de l'arène", "BLUE", "U285.0 — FL300", None),
    ("Wizard 1", "Wizard 1 (A-50) — AWACS rouge", "RED", "U284.0 — FL300 — orbite est-ouest au nord de St Catherine", "Wizard 1 - Escort"),
    ("Shell 1", "Shell 1 (IL-78M) — ravitailleur rouge", "RED", "U294.0 — FL200 — orbite est-ouest au nord de St Catherine", "Shell 1 - Escort"),
    ("Focus 1", "Focus 1 (A-50) — AWACS rouge de l'arène", "RED", "U286.0 — FL300", None),
]
DRONES = [
    ("Reaper 1", "Reaper 1 (drone laser) — champ de tir d'attaque", 1511, "35.55",
     "Laser 1511 — FM 35.55. 3 000 m sol au-dessus du champ de tir d'attaque (zone A), au sud-ouest de Cairo West."),
    ("Reaper 2", "Reaper 2 (drone laser) — col de Mitla", 1512, "35.6",
     "Laser 1512 — FM 35.6. 3 000 m sol au-dessus de la ligne du col de Mitla (Z02)."),
]

COMBAT_MISSIONS = [
    {"name": "Defense-AbuSuwayr", "friendly_name": "Défense — raid rouge sur Abu Suwayr", "secured": False,
     "briefing": "Deux Su-24M armés de missiles antiradar ouvrent la route à quatre Su-34 chargés de bombes, escortés "
                 "de deux Su-30, partis du centre du Sinaï vers la base d'Abu Suwayr, sur le canal. Abattez les "
                 "bombardiers avant le largage.\nÉchec si la base est bombardée (constaté par vous : la mission ne le "
                 "vérifie pas).",
     "elements": [{"name": "SEAD", "groups": ["SC-Defense-AbuSuwayr-SEAD"], "scalable": False},
                  {"name": "Bombardiers", "groups": ["SC-Defense-AbuSuwayr-Bombers"], "scalable": False},
                  {"name": "Escorte", "groups": ["SC-Defense-AbuSuwayr-Escort"], "scalable": True}]},
    {"name": "Interception-VIP", "friendly_name": "Interception — transport VIP de St Catherine à El Arish",
     "secured": False,
     "briefing": "Un IL-76 emmène l'état-major rouge de St Catherine vers El Arish, escorté par deux MiG-29S. "
                 "Interceptez-le avant El Arish : la fin de la route est sous la QRA et les défenses d'El Arish.",
     "elements": [{"name": "Transport", "groups": ["SC-Intercept-VIP-Il76"], "scalable": False},
                  {"name": "Escorte", "groups": ["SC-Intercept-VIP-Escort"], "scalable": True}]},
]

if __name__ == "__main__":
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    path = Path(M) / "mission.yaml"
    d = yaml.load(path.read_text(encoding="utf-8"))

    if "global_log_level" in d:
        d["global_log_level"] = "info"
    else:
        d.insert(0, "global_log_level", "info")
    mi = d["mission"]
    mi["name"] = "VEAF_OpenTraining_Sinai_ICAO_HECA"
    mi.yaml_add_eol_comment("HECA = Le Caire, METAR vivant vérifié le 12/10/2026 ; Cairo West (base mère) n'en publie pas", "name")
    mi["era"] = "MODERN"
    mi["language"] = "fr"
    mi["silence_atc_on_all_airbases"] = True
    mi["hide_names_from_spawned_groups"] = True

    mods = d["modules"]
    mods["SKYNET"] = {"enabled": True, "spotter_network": True, "spotter_view": "off"}
    mods["CTLD"]["airbase_logistics_radius"] = 2500
    mods["CTLD"].yaml_add_eol_comment("pas de parking Sinaï pour mesurer ; 2 500 m = 81 % d'Al Dhafra (OT Golfe Persique), "
                                      "base de la taille de Cairo West", "airbase_logistics_radius")
    assets = []
    for i, (name, desc, side, info, linked) in enumerate(ASSETS, 1):
        a = {"sort": i, "name": name, "description": desc, "coalition": side, "information": info}
        if linked:
            a["linked"] = linked
        assets.append(a)
    for name, desc, code, freq, info in DRONES:
        assets.append({"sort": len(assets) + 1, "name": name, "description": desc, "coalition": "BLUE",
                       "information": info, "jtac": code, "freq": freq, "mod": "FM"})
    mods["ASSETS"] = {"enabled": True, "assets": assets}
    mods["SANCTUARY"] = {"enabled": True, "sanctuary_zones": [
        {"name": n, "trigger_zone": z, "coalition": side, "delay_warning": 0, "delay_instant": 60,
         "protect_from_missiles": True} for n, z, c, r, side in SANCTUARIES]}

    d["pipeline"] = {"weather": False}
    d.yaml_add_eol_comment("pas de variantes météo : le serveur VEAF fixe météo et heure (David, 12/10/2026)", "pipeline")
    d["profiles"] = {"LOCAL_TEST": {"global_log_level": "debug", "security": {"disabled": True},
                                    "mission": {"hide_names_from_spawned_groups": False}}}
    d["combat_missions"] = COMBAT_MISSIONS
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(d, f)
    print("mission.yaml écrit")

    v = ROOT / "src/versions.yaml"
    if v.exists():
        v.unlink()
        print("src/versions.yaml supprimé (pas de variantes)")

    ctld = Path(M) / "ctld-config.yaml"
    c = ctld.read_text(encoding="utf-8")
    old = "  jtacLaserCodeMax: 1688\n"
    if old in c:
        c = c.replace(old, "  jtacLaserCodeMax: 1686   # codes imposés des drones (1511, 1512) sous le maximum, comme Syrie v6 (limitation ctld-jtac-imposed-code-and-radio)\n")
        ctld.write_text(c, encoding="utf-8")
    assert "jtacLaserCodeMax: 1686" in ctld.read_text(encoding="utf-8")
    print("ctld-config : jtacLaserCodeMax 1686")
