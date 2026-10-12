"""Lot 15 : date, météo de base, bullseye commun et briefing DCS de la mission.

Le texte est composé depuis les données (fréquences DCS des aérodromes, soutien, zones), pas tapé.
`python gen_15_identite.py [suffixe]` : un lot d'identité se rejoue sans danger (set_* remplacent), d'où le suffixe
de nom de lot pour garder chaque passage.
Météo : une seule, celle de la mission (le serveur VEAF fixe météo et heure de chaque session, décision de David du
12/10/2026) ; une matinée d'octobre plausible au Caire (METAR HECA du 12/10/2026 : 35007KT CAVOK 24/13 Q1015),
avec quelques nuages à 4 000 ft pour que le ciel ne soit pas vide.
"""
import json
import sys

from gen_05b_farps_porte_avions import CARRIERS, FARPS
from gen_09_qra_cap import QRAS
from gen_10_joueurs import SANCTUARIES
from lib import BLUE_SLOTS, BULLSEYE, RED_SLOTS, ROOT, TANKERS, Batch, xy

_t = (ROOT / "tools/airfield_channels.json").read_text(encoding="utf-8")
CH = {a["name"]: a for a in json.loads(_t[_t.index("{"):])["candidates"]}
SHORT = {"Hurghada International Airport": "Hurghada", "Inshas Airbase": "Inshas", "Ramon Airbase": "Ramon AB"}

ZONE_COUNT = 16


def base(n):
    a = CH[n]
    f = a["freqs"]
    tac = f", TACAN {a['tacan']}" if a.get("tacan") else ""
    return f"{SHORT.get(n, n)} (U{f['uhf']:.2f} / V{f['vhf']:.2f}{tac})"


def carriers():
    out = []
    for c in CARRIERS:
        s = f"{c['name'].split(' ', 1)[1]} U{c['tower_mhz']:.1f}, TACAN {c['tacan_channel']}X, ICLS {c['icls_channel']}"
        if c.get("link4_mhz"):
            s += f", Link 4 {c['link4_mhz']:.1f}"
        out.append(s)
    return " ; ".join(out)


def tankers():
    return ", ".join(f"{n} ({k}) {tac} U{f:.1f} FL{fl}" for n, (ab, fl, tac, f, k) in TANKERS.items())


def qras(side):
    return ", ".join(f"{q['name'].replace('QRA ', '')} ({q['radius'] / 1852:.0f} nm)" for q in QRAS
                     if q["side"]["coalition"] == side)


def farps():
    return ", ".join(f"{n} (V{f:.1f})" for n, p, f, cs, side in FARPS)


SITUATION = f"""VEAF Open Training — Sinaï (moderne, octobre 2025).
Une force hostile a envahi la péninsule du Sinaï. L'Égypte et Israël, appuyés par les États-Unis, la prennent en tenaille : à l'ouest depuis le canal de Suez, à l'est depuis le Néguev. Deux fronts : le canal, de Port-Saïd à Suez, et la frontière, de Rafah à Taba. Bullseye commun : l'aérodrome de Bir Hasanah, au centre du Sinaï.

BASES BLEUES (slots dynamiques) : {", ".join(base(n) for n in BLUE_SLOTS)}. {farps()}.
PORTE-AVIONS : {carriers()}.
SOUTIEN : AWACS Overlord 1 U282.0 (à l'ouest du Caire) et Magic 1 U283.0 (Néguev). Ravitailleurs : {tankers()} ; S-3B du Stennis 56Y U296.0, du Roosevelt 57Y U297.0. Tous escortés. Drones laser : Reaper 1 (code 1511, FM 35.55) sur le champ de tir d'attaque, Reaper 2 (1512, FM 35.6) sur le col de Mitla.

ENTRAÎNEMENT (menu F10 VEAF, zones) : H Arad (hélicoptères), A désert de Gizeh (attaque), S désert occidental (SEAD), trois niveaux chacun.
TOURISME : visite aérienne des pyramides de Gizeh, Saqqarah et Dahchour depuis le FARP Pyramides, balises FM GIZ 31.0, SAQ 32.0, DAH 33.0, et un guide qui raconte chaque monument survolé bas.
COMBAT : {ZONE_COUNT} zones (front, SEAD, convois, frappes, bases aériennes, antinavire), chacune avec son briefing dans le menu. Missions à la demande : CAP rouges et bleues, raid rouge sur Abu Suwayr, interception d'un transport VIP.
QRA rouges : {qras('red')} ; QRA bleues : {qras('blue')}. Décollage 90 s après l'entrée du premier intrus ; elles ignorent les hélicoptères. Couloirs sans QRA : tout le sud du Sinaï (golfe de Suez, St Catherine, Sharm, Tiran), Mitla et Nakhl.
JOUEURS CONTRE JOUEURS : libre hors des sanctuaires. Sanctuaire bleu : Le Caire, les pyramides et les champs de tir de l'ouest ({SANCTUARIES[0][3] // 1000} km) ; rouge : St Catherine ({SANCTUARIES[1][3] // 1000} km). Un intrus y est détruit après 60 s ; un missile tiré sur un défenseur est détruit. Arène AirQuake en Méditerranée, au nord-ouest du delta, slots en vol Fox 1 et Fox 3.

Plan radio, cartes et détail de chaque zone : voir les images du briefing et le README de la mission."""

BLUE_TASK = ("Reprendre le Sinaï : s'entraîner sur les champs de tir H, A et S, puis frapper les zones de combat rouges. "
             "Cairo West est la base mère ; Abu Suwayr et Fayed tiennent le canal, Hatzerim et Ramon le Néguev, "
             "Hurghada la mer Rouge ; le Stennis et le Tarawa croisent en Méditerranée, le Roosevelt en mer Rouge.")
RED_TASK = (f"Tenir le Sinaï. Bases rouges avec slots : {', '.join(base(n) for n in RED_SLOTS)}. "
            "AWACS Wizard 1 U284.0, ravitailleur Shell 1 (IL-78) U294.0 FL200. Arène : AWACS Focus 1 U286.0. "
            "Le sanctuaire bleu du Caire (pyramides comprises) détruit tout appareil rouge qui y entre.")

if __name__ == "__main__":
    b = Batch()
    b.act("set_mission_date", date="2025-10-15", start_time="09:00")
    b.act("set_weather", metar="HECA 150700Z 35008KT 9999 FEW040 26/14 Q1015")
    for side in ("blue", "red"):
        b.act("set_bullseye", coalition=side, position=xy(BULLSEYE))
    b.act("set_briefing", sortie="VEAF Open Training — Sinaï", situation=SITUATION, blue_task=BLUE_TASK,
          red_task=RED_TASK)
    b.save(f"15-identite{('-' + sys.argv[1]) if len(sys.argv) > 1 else ''}.json")
    print(SITUATION)
