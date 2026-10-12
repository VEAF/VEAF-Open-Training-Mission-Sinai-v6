"""Écrit README.md, le briefing des pilotes, depuis tools/briefing_data.json, et redessine les cartes (gen_map.py).

Lancer gather.py avant : toutes les valeurs viennent du dossier de la mission, rien n'est tapé ici à part le
contexte et les consignes. Construit comme le README de l'Open Training GermanyCW v6.
"""

import json

import gen_map
from paths import ROOT, TOOLS

D = json.load(open(TOOLS / "briefing_data.json", encoding="utf-8"))
gen_map.render()

side = {"blue": "Bleu", "red": "Rouge"}
ADL = {"-avenger_squad": "Avenger", "-nasams": "NASAMS", "-hawk": "Hawk", "-patriot": "Patriot", "-sa10": "SA-10",
       "-sa11": "SA-11", "-sa6": "SA-6", "-sa15": "SA-15", "-sa22": "Pantsir (SA-22)", "-ewr": "Radar d'alerte 55G6",
       "EWR 1L13": "Radar d'alerte 1L13", "EWR 55G6": "Radar d'alerte 55G6", "-hq7": "HQ-7", "-stinger": "Stinger",
       "-blue_ewr": "Radar d'alerte FPS-117"}
NAME = {"FA-18C_hornet": "F/A-18C", "F-16C_50": "F-16C", "F-4E-45MC": "F-4E", "MiG-21Bis": "MiG-21bis",
        "F-14A-135-GR": "F-14A", "AV8BNA": "AV-8B", "F-16C bl.50": "F-16C (IA)", "M-2000C": "Mirage 2000C"}
BASE_MERE = "Cairo West"
ROLE = {"Texaco 1": "perche · canal", "Arco 1": "panier · canal", "Texaco 2": "perche · Néguev", "Arco 2": "panier · Néguev",
        "Overlord 1": "AWACS · ouest", "Magic 1": "AWACS · est", "Shell 1": "ravitailleur rouge", "Wizard 1": "AWACS rouge",
        "Darkstar 1": "AWACS · arène", "Focus 1": "AWACS rouge · arène"}
ZOOM = {s: (f"docs/cartes/carte_{i:02d}_{s}.jpg", t) for i, (s, t, _) in enumerate(gen_map.ZOOMS, 1)}
md = []
w = md.append


def c(v):
    return f"`{v}`"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(x).replace("|", "/") for x in r) + " |" for r in rows]
    return "\n".join(out)


def zooms(*slugs):
    """Les cartes zoomées d'une section, deux par ligne, chacune cliquable (une seule : pleine largeur)."""
    if len(slugs) == 1:
        w(f"![{ZOOM[slugs[0]][1]}]({ZOOM[slugs[0]][0]})")
        w("")
        return
    cells = [f'<td width="50%"><a href="{ZOOM[s][0]}"><img src="{ZOOM[s][0]}" alt="{ZOOM[s][1]}"></a><br>'
             f'<sub>{ZOOM[s][1]}</sub></td>' for s in slugs]
    w("<table>" + "".join("<tr>" + "".join(cells[k:k + 2]) + "</tr>" for k in range(0, len(cells), 2)) + "</table>")
    w("")


def fl(ft):
    return f"FL{round(ft / 100):03d}"


date, start, bu = D["date"], D["start"], D["bullseye"]
w("# VEAF Open Training — Sinaï (moderne, 2025)")
w("")
w("Mission d'entraînement ouverte des serveurs VEAF, sur la carte **Sinai** de DCS, dans un scénario moderne. Ce document "
  "est le briefing complet : bases, soutien, zones, QRA, CAP, radio, météo. Les positions sont données en coordonnées "
  "(degrés, minutes décimales) et en relèvement/distance depuis le bullseye (relèvement vrai, nautiques).")
w("")
w(table(["Mission", "Date", "Heure de base", "Bullseye (bleu et rouge)", "Météo", "ATC"],
        [[c(D["name"]), f'{date["Day"]:02d}/{date["Month"]:02d}/{date["Year"]}',
          f'{start // 3600:02d}:{start % 3600 // 60:02d} (heure de la carte, UTC+2)', f'aérodrome de Bir Hasanah · {c(bu["ddm"])}',
          "celle du serveur VEAF", "coupé sur tous les aérodromes"]]))
w("")
w("**Sommaire** : [Situation](#situation) · [Carte](#carte) · [Bases](#bases) · [Ravitailleurs et AWACS](#ravitailleurs-et-awacs) · "
  "[Porte-avions](#porte-avions) · [Drones laser](#drones-laser) · [Entraînement](#entraînement) · "
  "[Tourisme aux pyramides](#tourisme-aux-pyramides) · [Zones de combat](#zones-de-combat) · "
  "[Missions scénarisées](#missions-scénarisées) · [QRA](#qra) · [CAP à la demande](#cap-à-la-demande) · "
  "[Combat entre joueurs](#combat-entre-joueurs) · [Défense aérienne](#défense-aérienne) · [Plan radio](#plan-radio) · "
  "[Météo et heures](#météo-et-heures) · [Commandes utiles](#commandes-utiles) · [Pour les créateurs de mission](#pour-les-créateurs-de-mission)")
w("")
w("## Situation")
w("")
w("Une force hostile a envahi la péninsule du Sinaï. L'Égypte et Israël, appuyés par les États-Unis et trois groupes "
  "aéronavals — le Stennis et le Tarawa en Méditerranée, le Roosevelt en mer Rouge —, la prennent en tenaille. Deux fronts : "
  f"à l'ouest le canal de Suez, de Port-Saïd à Suez ({D['fronts_nm'][0]} nm), tenu par les bases égyptiennes du canal ; à "
  f"l'est la frontière, de Rafah à Taba ({D['fronts_nm'][1]} nm), face aux bases israéliennes du Néguev. Le rouge tient tout "
  "le Sinaï, d'El Arish au nord à Sharm el-Cheikh au sud. Le bullseye commun est l'aérodrome de Bir Hasanah, au centre de la "
  "péninsule.")
w("")
w("La version 5 opposait Israël (bleu) à l'Égypte (rouge) ; la v6 réunit les deux en bleu face à un Sinaï occupé, ce qui "
  "laisse au bleu l'arrière égyptien et ses pyramides, d'où la zone de tourisme.")
w("")
w("Zones de combat, missions et soutien se pilotent par le menu radio F10 (*Zones de combat*, *Missions de combat*, *Assets*).")
w("")
w("## Carte")
w("")
w("![Carte de la mission](docs/carte.jpg)")
w("")
w("Cartes zoomées, reprises dans les sections qu'elles illustrent : "
  + " · ".join(f"[{t.split(' : ')[0]}]({f})" for f, t in ZOOM.values()) + ".")
w("")
w("Carrés : bases avec slots (bleu / rouge). Triangles : FARP. Traits pleins : hippodromes des ravitailleurs et AWACS. "
  "Pointillés : CAP à la demande. Cercles pleins : QRA. Pastilles vertes : entraînement (H hélicoptères, A attaque, S SEAD). "
  "Pastille marron T : tourisme aux pyramides. Pastilles rouges numérotées : zones de combat. Cercles en tirets : "
  "sanctuaires. Navires : porte-avions et LHA. L'arène est en Méditerranée, au nord-ouest du delta (zoom 8). Fond "
  "OpenStreetMap ; les lignes de front sont approximatives. Le briefing DCS montre cette "
  "carte puis les zooms (flèches sous l'image, molette pour grossir) ; la carte F10 porte les mêmes dessins : front, zones, "
  "QRA, sanctuaires et arène pour les deux camps, hippodromes de soutien pour leur camp seulement.")
w("")
w("## Bases")
w("")
rows = []
for b in D["bases"]:
    here = [ADL.get(a["alias"], a["alias"]) for a in D["ad"]
            if a["side"] == b["side"] and abs(a["x"] - b["x"]) < 9000 and abs(a["y"] - b["y"]) < 9000]
    rows.append([f'**{b["name"]}**' + (" (base mère)" if b["name"] == BASE_MERE else ""), side[b["side"]], c(b["ddm"]), c(b["be"]),
                 c(b.get("uhf", "—")), c(b.get("vhf", "—")), c(b.get("fm", "—")), " + ".join(dict.fromkeys(here)) or "—"])
rows += [[f'**FARP {f["name"]}**', "Bleu", c(f["ddm"]), c(f["be"]), "—", "—", c(f'{float(f["freq"]):.1f}'), "dépôt de munitions (CTLD)"]
         for f in D["farps"]]
w(table(["Base", "Camp", "Position", "Bullseye", "UHF", "VHF", "FM", "Défense"], rows))
w("")
w("Slots dynamiques, démarrage moteur chaud, carburant et munitions illimités. Les autres aérodromes de chaque camp lui "
  "appartiennent, sans slots : côté bleu les autres terrains d'Égypte (delta, canal, vallée du Nil) et d'Israël ; côté "
  "rouge les autres terrains du Sinaï (El Gora, Bir Hasanah, Baluza, Abu Rudeis, Sharm el-Cheikh, Taba). La Jordanie, "
  "l'Arabie saoudite, le Liban et la Syrie sont neutres. Fréquences : celles que DCS donne à chaque tour (ATC coupé).")
w("")
zooms("lecaire", "canal", "negev", "sud")
w("## Ravitailleurs et AWACS")
w("")
w(table(["Indicatif", "Camp", "Appareil", "Rôle", "UHF", "TACAN", "Niveau", "Bullseye (milieu)", "Hippodrome (extrémités)", "Escorte"],
        [[f'**{s["name"]}**', side[s["side"]], s["type"], ROLE.get(s["name"], ""), c(f'{s["freq"]:.1f}'),
          c(s["tacan"]) if s["tacan"] else "—", c(fl(s["alt_ft"])), c(s["mid_be"]), f'{c(s["a"]["ddm"])}<br>{c(s["b"]["ddm"])}',
          "oui" if s["escort"] else "non"] for s in D["support"]]))
w("")
w("Les ravitailleurs et AWACS du théâtre sont escortés (F-16C égyptiens à l'ouest, F-15C israéliens à l'est, Su-27 côté rouge). Marqueurs F10 : `-tanker <nom>` "
  "amène un ravitailleur au marqueur ; `-tankerlow` et `-tankerhigh` mettent le plus proche au FL120 ou au FL220.")
w("")
w("## Porte-avions")
w("")
w(table(["Navire", "Position de départ", "Bullseye", "TACAN", "ICLS", "Link 4", "Tour", "Slots sur le pont"],
        [[f'**{cv["name"]}** ({cv["group"]}, {cv["escorts"]} escorteur{"s" if cv["escorts"] > 1 else ""})', c(cv["ddm"]), c(cv["be"]),
          c(cv.get("tacan", "—")), c(cv.get("icls", "—")), c(f'{cv["link4"]:.1f}') if cv.get("link4") else "—", c(f'{cv["tower"]:.1f}'),
          ", ".join(f'{x["n"]} × {NAME.get(x["type"], x["type"])}' for x in cv["deck"])] for cv in D["carriers"]]))
w("")
zooms("nord", "sud")
w("Le Stennis et le Tarawa en Méditerranée, au large d'El Arish et de Gaza ; le Roosevelt en mer Rouge, au sud de Ras "
  "Mohammed. "
  "Slots à froid et à chaud sur les ponts, plus les slots dynamiques. Le menu F10 *CARRIER OPS* met chaque "
  "porte-avions face au vent, avec son ravitailleur S-3B (Stennis 56Y U296.0, Roosevelt 57Y U297.0) et son hélicoptère "
  "de sauvetage.")
w("")
w("## Drones laser")
w("")
w(table(["Drone", "Appareil", "Au-dessus de", "Code laser", "Radio", "Hauteur", "Bullseye"],
        [[f'**{x["name"]}**', x["type"], x["where"], c(x["jtac"]), c(f'{x["freq"]} {x["mod"]}'), c("3 000 m sol"), c(x["be"])] for x in D["drones"]]))
w("")
w("Reaper 1 tourne au-dessus du champ de tir d'attaque du désert de Gizeh, Reaper 2 au-dessus de la ligne du col de Mitla "
  "(Z02), et chacun désigne au laser ce qu'il voit. CTLD le maintient à 3 000 m sol : l'artillerie antiaérienne de la zone "
  "peut l'abattre, et le menu F10 *Assets* le remet en vol. Il ne désigne que des véhicules — ce que sont aussi les cibles "
  "des niveaux faciles — et ne marque qu'à 10 km. Pas de drone sur une zone dont les SAM portent plus loin que le laser.")
w("")
w("## Entraînement")
w("")
w("Loin du front, à quelques minutes d'une base. Trois niveaux par famille, chacun comprenant ceux d'en dessous. "
  "**Activez un seul niveau par famille à la fois.** Les cibles des niveaux faciles sont des véhicules immobiles, en tir "
  "interdit : chauds au pod, inertes.")
w("")
zooms("lecaire", "negev")
for fam, label in (("Arad", "Hélicoptères — Arad (désert de Judée, près du FARP Range)"),
                   ("DesertGizeh", "Attaque — désert de Gizeh (au sud-ouest de Cairo West)"),
                   ("DesertOuest", "SEAD — désert occidental (au nord-ouest du Fayoum)")):
    lv = [z for z in D["zones"] if z["key"].startswith(f"combatZone_{fam}_")]
    z0 = lv[0]
    w(f"### {label}")
    w("")
    w(f'{c(z0["ddm"])} · bullseye {c(z0["be"])} · rayon {z0["radius_nm"]:.1f} nm · menu F10 « {z0["menu"]} » · {z0["tankers"]}')
    w("")
    for z in lv:
        w(f'- **{z["name"]}** — {z["briefing"]}')
    w("")
w("## Tourisme aux pyramides")
w("")
t = next(z for z in D["zones"] if z["key"] == "combatZone_Pyramides")
w(f'{c(t["ddm"])} · bullseye {c(t["be"])} · menu F10 « {t["menu"]} »')
w("")
w(t["briefing"].split("\n")[0])
w("")
w(table(["Balise", "Site", "FM", "Position"],
        [[f'**{x["code"]}**', x["site"], c(f'{x["mhz"]:.1f}'), c(x["ddm"])] for x in D["beacons"]]))
w("")
w("Chaque balise répète son indicatif en morse. Le guide parle à tout appareil d'un joueur qui passe sous 1 500 ft sol "
  "au-dessus d'un monument (Khéops, Khéphren, Mykérinos, le Sphinx, Djoser, la pyramide rouge, la rhomboïdale, Meïdoum) : "
  "un message par monument, renouvelé après 10 minutes. Le plateau est dans le sanctuaire bleu du Caire : un appareil rouge "
  "y est détruit, la visite est réservée aux bleus. La zone F10 *Tourisme* fait seulement apparaître des autocars au parking "
  "du plateau ; le circuit, les balises et le guide sont là en permanence. La présence des monuments dans le décor DCS est "
  "à confirmer en jeu.")
w("")
zooms("pyramides")
w("## Zones de combat")
w("")
w("Les numéros renvoient à la carte. Chaque zone s'active par le menu F10 *Zones de combat*, qui redonne son briefing et "
  "sa position. Une partie des sites change d'une activation à l'autre (batterie tirée au sort, groupes blindés tirés au sort).")
w("")
zooms("canal", "centre", "nord", "sud")
for menu in ("Front", "SEAD", "Convois", "Frappes en profondeur", "Bases aériennes", "Antinavire"):
    w(f"### {menu}")
    w("")
    for z in D["zones"]:
        if z["training"] or z["menu"] != menu:
            continue
        w(f'**{z["name"]}** — {c(z["ddm"])} · bullseye {c(z["be"])}')
        w("")
        w(f'{z["briefing"]} Ravitailleurs : {z["tankers"]}.')
        w("")
w("## Missions scénarisées")
w("")
for cm in D["combat_missions"]:
    w(f'- **{cm["name"]}** — {cm["briefing"]}'.replace("\n", " "))
w("")
w("À lancer par le menu F10 *Missions de combat*. Elles n'ont pas de condition de réussite automatique : ce sont les pilotes "
  "qui jugent.")
w("")
w("## QRA")
w("")
w(table(["QRA", "Défend", "Centre", "Bullseye", "Rayon", "Base", "Réponse"],
        [[f'**{q["name"]}**', side[q["side"]], c(q["ddm"]), c(q["be"]), c(f'{q["radius_nm"]} nm'), q["airport"],
          "<br>".join(f'dès {t["n"]} intrus : {t["pick"]} vol parmi ' + ", ".join(t["types"]) for t in q["tiers"])] for q in D["qra"]]))
w("")
delay = D["qra"][0]["delay"]
w(f"Les chasseurs décollent {delay} s après l'entrée du premier intrus dans le cercle ; "
  + ("les hélicoptères les déclenchent." if any(q["helos"] for q in D["qra"]) else "les hélicoptères ne les déclenchent pas."))
w("")
w("Couloirs sans QRA rouge : tout le sud du Sinaï (golfe de Suez, St Catherine, Sharm el-Cheikh, détroit de Tiran), le "
  "col de Mitla et Nakhl. Les bases bleues les plus proches (Fayed, Abu Suwayr, Hatzerim, Ramon) sont hors des cercles "
  "rouges.")
w("")
w("## CAP à la demande")
w("")
w(table(["Mission", "Camp", "Appareils", "Niveau", "Bullseye (milieu)", "Description"],
        [[f'**{x["menu"]}**', side[x["side"]], f'{x["n"]} × {NAME.get(x["type"], x["type"])}', c(f'FL{x["fl"]:03d}'), c(x["mid_be"]),
          x["briefing"]] for x in D["caps"]]))
w("")
w("À lancer par le menu F10 *Missions de combat*.")
w("")
w("## Combat entre joueurs")
w("")
w("Des joueurs volent des deux côtés. Le combat entre joueurs est **permis sur le théâtre et dans l'arène, interdit dans les "
  "sanctuaires** : Le Caire, avec Cairo West, les pyramides et les champs de tir de l'ouest, côté bleu ; St Catherine "
  "côté rouge. El Arish et Melez n'en ont pas : leurs abords sont les plus disputés. Un pilote du camp adverse y est prévenu dès "
  "l'entrée, puis détruit au bout de 60 s, et les missiles tirés sur un appareil qui s'y trouve sont détruits. Les limites "
  "sont tracées sur la carte F10.")
w("")
def centre_be(z):
    """Relèvement / distance du centre d'un sanctuaire depuis le bullseye."""
    import math
    dx, dy = z["x"] - D["bullseye"]["x"], z["y"] - D["bullseye"]["y"]
    return f"{round((math.degrees(math.atan2(dy, dx)) + 360) % 360) % 360:03d}°/{round(math.hypot(dx, dy) / 1852)} nm"


w(table(["Sanctuaire", "Protège", "Centre (bullseye)", "Rayon"],
        [[z["name"].replace("Sanctuaire ", ""), side[z["side"]], c(centre_be(z)), c(f'{z["radius_km"]:.1f} km')]
         for z in D["sanctuaries"]]))
w("")
az = D["arena_zone"]
w("### Arène")
w("")
w(f'En Méditerranée, au nord-ouest du delta du Nil : {c(az["ddm"])} · bullseye {c(az["be"])} · rayon {az["radius_nm"]} nm. '
  "Slots en départ en vol, bleus au sud, rouges au nord, face à face : l'arène AirQuake des Open Training VEAF, mêmes "
  "appareils et mêmes emports des deux côtés.")
w("")
zooms("arene")
rows = []
for sd in ("blue", "red"):
    for fox in ("Fox 3", "Fox 1"):
        lst = [a for a in D["arena_slots"] if a["side"] == sd and a["fox"] == fox]
        if lst:
            rows.append([side[sd], fox, ", ".join(f'{NAME.get(a["type"], a["type"])} ×{a["n"]}' for a in lst), c(f'FL{lst[0]["fl"]:03d}')])
w(table(["Camp", "Missiles", "Slots", "Départ"], rows))
w("")
w("AWACS de l'arène : " + " ; ".join(f'{s["name"]} ({s["type"]}, {side[s["side"]].lower()}) U{s["freq"]:.1f}, {fl(s["alt_ft"])}'
                                     for s in D["support"] if s["name"] in ("Darkstar 1", "Focus 1")) + ".")
w("")
w("## Défense aérienne")
w("")
w("Défense permanente des deux camps : courte et moyenne portée sur chaque base avec slots, quelques batteries longue "
  "portée, des radars d'alerte avancée. Aucune ne couvre une base adverse avec slots (portées DCS). Chaque zone de combat a "
  "en plus sa propre défense, décrite dans sa fiche.")
w("")
for sd in ("blue", "red"):
    w(f"**{side[sd]}** :")
    w("")
    w(table(["Site", "Système", "Position", "Bullseye"],
            [[a["name"], ADL.get(a["alias"], a["alias"]), c(a["ddm"]), c(a["be"])] for a in D["ad"] if a["side"] == sd]))
    w("")
w("## Plan radio")
w("")
for sd in ("blue", "red"):
    rows = []
    for role, title in (("primary_1", "Radio 1 (UHF)"), ("primary_2", "Radio 2 (V/UHF)")):
        for k, v in sorted(D["radio"][sd][role].items(), key=lambda kv: int(kv[0])):
            # VMCT ne pose sur une liste que la fréquence de sa bande (primary_1 UHF, primary_2 VHF) et écarte
            # sans le dire un canal qui n'en a pas : ne pas l'annoncer aux pilotes
            mhz = D["channels"].get(v, {}).get("uhf" if role == "primary_1" else "vhf")
            if mhz is None:
                print(f"[gen_readme] {sd} {role} canal {k} ({v}) : pas de fréquence dans la bande, non injecté")
                continue
            rows.append([title, c(k), D["titles"].get(v, v).replace("Base-", ""), c(mhz)])
    w(f"### {side[sd]}")
    w("")
    w(table(["Radio", "Canal", "Nom", "MHz"], rows))
    w("")
w("Préréglages injectés dans les appareils à radio programmable. FM : canaux 1 à 20 = 30 à 49 MHz. Les canaux VEAF sont "
  "hors de la bande des tours du Sinaï (UHF 250.05-252.25, une partie de la VHF 118.0-134.6) ; patrouilles en VHF "
  "130.0-130.9 et UHF 390-395.5. Les FARP Pyramides (127.5), Range (128.0), Canal (128.5) et Negev (129.0) sont sur la "
  "radio 2 ; les balises touristiques sur les canaux FM 2 à 4 (31.0, 32.0, 33.0).")
w("")
w("## Météo et heures")
w("")
wx = D["weather"]
w(f'La mission démarre le {date["Day"]:02d}/{date["Month"]:02d}/{date["Year"]} à {start // 3600:02d}:{start % 3600 // 60:02d} '
  f'(heure de la carte, UTC+2), {wx["sky"]}, {wx["temperature"]:.0f} °C, vent du {wx["wind_from"]:03.0f}° à '
  f'{wx["wind_ms"] * 1.944:.0f} kt. **Sur les serveurs VEAF, c\'est le serveur qui fixe la météo et l\'heure de chaque '
  "session** : la mission n'a pas de variantes météo.")
w("")
w("## Commandes utiles")
w("")
w("- `-tanker <nom>` : amène le ravitailleur nommé à la position du marqueur ; `-tankerlow` / `-tankerhigh` : FL120 / FL220.")
w("- `-cas` : fait apparaître une cible CAS aléatoire au marqueur.")
w("- `-point <nom>` : nomme un point de la carte.")
w("- `-smoke`, `-light`, `-signal` : fumigène, éclairage, fusée.")
w("- `-jtac`, `-afac` : JTAC au sol, drone AFAC.")
w("")
w("Rôles sans avion : 5 slots par camp pour chaque rôle (Game Master, commandant tactique, JTAC, observateur), et un "
  "pilote peut prendre la main sur les véhicules au sol. Le menu F10 VEAF reste vide pour un Game Master : il n'a pas de "
  "groupe, et les commandes sécurisées ne sont posées que groupe par groupe (VMCT #128, limite de DCS).")
w("")
w(open(TOOLS / "readme_makers.md", encoding="utf-8").read())
open(ROOT / "README.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print(f"VERDICT : README.md écrit ({sum(len(x) for x in md)} caractères), cartes redessinées")
