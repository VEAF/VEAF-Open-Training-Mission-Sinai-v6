"""Contrôles du .miz construit (section 8 du prompt Open Training), lus avec le lecteur de VMCT, jamais par texte.

Usage (depuis le dossier de la mission, environnement poetry de VMCT) :
    poetry -C ../VEAF-Mission-Creation-Tools run python "$PWD/tools/verify.py" [fichier.miz ...]
Sans argument : le .miz de base le plus récent (pas de variantes météo). Finit sur une ligne VERDICT.
"""

import collections
import glob
import json
import math
import os
import re
import sys
import zipfile

import yaml

sys.stdout.reconfigure(encoding="utf-8")
from paths import ROOT, TOOLS
from mission_tools.miz_tools import read_miz
from veaf_mission_mcp.map_tools import list_airfields

NM = 1852.0
Y = yaml.safe_load(open(ROOT / "mission.yaml", encoding="utf-8"))
UNITS_DB = yaml.safe_load(open(os.path.join(os.environ.get("VMCT_PY", str(ROOT.parent / "VEAF-Mission-Creation-Tools" / "src" / "python" / "veaf-tools")),
                                            "veaf_libs", "data", "veaf-units.yaml"), encoding="utf-8"))
AF = {a["id"]: a for a in list_airfields(theatre="SinaiMap")["airfields"]}
from lib import BLUE_SLOTS, RED_SLOTS  # noqa: E402
WANTED_SLOTS = {"blue": set(BLUE_SLOTS), "red": set(RED_SLOTS)}
# portées DCS (threat_range_m de list_unit_types, 12/10/2026), en nm, des lanceurs posés en permanent
THREAT_NM = {"Hawk ln": 24.3, "NASAMS_LN_C": 8.1, "M1097 Avenger": 2.4, "Patriot ln": 54.0, "S-300PS 5P85C ln": 64.8,
             "SA-11 Buk LN 9A310M1": 27.0, "Kub 2P25 ln": 13.5, "Tor 9A331": 6.5, "HQ-7_LN_SP": 8.1, "Soldier stinger": 2.4}
FAILS = []
# statiques que DCS refuse sans shape_name (limitation connue static-without-shape-name-is-refused) ;
# les véhicules, avions, bunkers, entrepôts « Warehouse » et réservoirs se résolvent seuls
SHAPE_REQUIRED = {".Command Center", ".Ammunition depot"}


def fail(msg):
    FAILS.append(msg)
    print("  ÉCHEC :", msg)


def seq(v):
    if v is None:
        return []
    if isinstance(v, dict):
        return [v[k] for k in sorted(v, key=lambda k: int(k))]
    return list(v)


def groups(m):
    for side, co in m["coalition"].items():
        for c in seq(co.get("country")):
            for cat in ("plane", "helicopter", "vehicle", "ship", "static"):
                for g in seq((c.get(cat) or {}).get("group")):
                    yield side, c.get("name"), cat, g


def alias_launchers():
    """alias de #veafInterpreter (-sa10…) → types d'unités que son groupe contient (veaf-units.yaml)."""
    out = {}
    for g in UNITS_DB["groups"]:
        types = set()
        for u in g.get("units") or []:
            types.add(u["type"] if isinstance(u, dict) else u)
        for a in g.get("aliases", []):
            out[a] = types
    return out


ALIASES = alias_launchers()
ALIASES_CI = {k.lower(): v for k, v in ALIASES.items()}
EXPECTED = {"zones": 26, "QRA": 4, "CAP": 6, "sanctuaires": 2}   # ce que mission.yaml déclare (9 + tourisme + 16)


def command_types():
    """alias #command (-sa6…) → types qu'il peut poser, d'après la commande VEAF de l'alias. None : tirage dynamique."""
    from veaf_mission_mcp.actions import register_default_actions
    from veaf_mission_mcp.catalog import ActionCatalog
    cat = ActionCatalog()
    register_default_actions(cat)
    sc = cat.run_action("list_shortcuts", {})
    unit_alias = {a: u["unitType"] for u in sc["units"] for a in u["aliases"]}
    out = {}
    for c in sc["commands"]:
        m = re.match(r"_spawn (group|unit), name ([^,]+)", c["veafCommand"])
        for a in c["aliases"]:
            if not m:
                out[a] = None
            elif m.group(1) == "group":
                out[a] = ALIASES_CI.get(m.group(2).strip().lower(), set())   # « name plz05 » désigne le groupe PLZ05
            else:
                name = m.group(2).strip()
                out[a] = {unit_alias.get(name, name)}
    return out


COMMAND_TYPES = command_types()
CMD_TO_GROUP = {"-sa10": "sa10", "-sa11": "sa11", "-sa6": "sa6", "-sa15": "sa15_squad", "-sa22": "sa22_squad", "-ewr": "red_ewr",
                "-hawk": "hawk", "-nasams": "nasams_c", "-patriot": "patriot", "-avenger_squad": "avenger_squad",
                "-hq7": "hq7", "-blue_ewr": "blue_ewr", "-stinger": "stinger_squad"}


def check(path):
    print(f"\n===== {os.path.basename(path)}")
    miz = read_miz(path)
    m = miz.mission_content
    m = m.get("mission", m)
    gnames, unames, gid, uid = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    support, interp = {}, []
    for side, country, cat, g in groups(m):
        gnames[g["name"]] += 1
        gid[g["groupId"]] += 1
        units = seq(g["units"])
        for u in units:
            unames[u["name"]] += 1
            uid[u["unitId"]] += 1
            if cat in ("plane", "helicopter") and not g.get("dynSpawnTemplate") and not g["name"].startswith("veafSpawn-"):
                p0 = (seq(g["route"]["points"]) or [{}])[0]
                grounded = p0.get("linkUnit") or p0.get("airdromeId") or str(p0.get("type", "")).startswith("TakeOff")
                if (u.get("alt") or 0) <= 0 and not grounded:
                    fail(f"altitude <= 0 : {g['name']}")
                if not (u.get("payload") or {}).get("fuel"):
                    fail(f"sans carburant : {g['name']}")
                armed = g["name"].startswith(("QRA-", "OnDemand-", "Arène")) or g["name"].endswith("Escort")
                if armed and not (u.get("payload") or {}).get("pylons"):
                    fail(f"vol armé sans emport : {g['name']}")
                for pyl in seq((u.get("payload") or {}).get("pylons")):
                    if "'" in str(pyl.get("CLSID", "")) or "CLSID" in str(pyl.get("CLSID", "")):  # str(dict) écrit à la place du CLSID
                        fail(f"CLSID mal formé dans {g['name']} : {pyl.get('CLSID')}")
            if cat == "static" and not u.get("category"):
                fail(f"statique sans category : {g['name']}")
            if cat == "static" and not u.get("shape_name") and u["type"] in SHAPE_REQUIRED:
                fail(f"statique sans shape_name : {g['name']} ({u['type']})")
            if "#veafInterpreter" in u["name"]:
                interp.append((side, g, u))
            mc = re.search(r'#command="(-[\w]+)', u["name"])
            if mc and COMMAND_TYPES.get(mc.group(1)) is not None and u["type"] not in COMMAND_TYPES[mc.group(1)]:
                fail(f"porteur #command {g['name']} : {u['type']} n'est pas posé par {mc.group(1)} "
                     f"({sorted(COMMAND_TYPES[mc.group(1)])})")
        if cat == "plane" and not g.get("lateActivation"):
            ids = [t["id"] if t["id"] != "WrappedAction" else t["params"]["action"]["id"]
                   for t in seq(seq(g["route"]["points"])[0].get("task", {}).get("params", {}).get("tasks"))]
            # les S-3B embarqués sont routés et réapparus par le module CARRIER (veafCarrierOperations) : pas d'orbite à eux
            if ("Tanker" in ids or "AWACS" in ids) and not g["name"].endswith("S3B-Tanker"):
                support[g["name"]] = ids
        if g["name"].startswith("QRA-") and seq(seq(g["route"]["points"])[0].get("task", {}).get("params", {}).get("tasks")):
            fail(f"QRA avec une tâche sur son point : {g['name']} (le build ne lui donne pas le rôle zone_defense)")
        if "-Convoi" in g["name"]:
            acts = [p.get("action") for p in seq(g["route"]["points"])]
            print(f"  convoi {g['name']} : {acts}")
            if any(a != "On Road" for a in acts[1:]):
                fail(f"convoi hors route : {g['name']}")
    dups = [n for n, c in gnames.items() if c > 1] + [n for n, c in unames.items() if c > 1]
    print(f"  groupes {sum(gnames.values())}, unités {sum(unames.values())} ; doublons de nom {dups[:5]} ; "
          f"doublons d'id {sum(1 for c in gid.values() if c > 1)} / {sum(1 for c in uid.values() if c > 1)}")
    if dups or any(c > 1 for c in gid.values()) or any(c > 1 for c in uid.values()):
        fail("noms ou identifiants en double")
    print("  soutien :")
    for k, v in sorted(support.items()):
        print(f"    {k:22s} {v}")
        need = {"Tanker", "Orbit", "SetUnlimitedFuel"} if "Tanker" in v else {"AWACS", "Orbit", "SetUnlimitedFuel", "EPLRS"}
        if not need <= set(v):
            fail(f"tâches incomplètes : {k} {sorted(need - set(v))}")

    # slots dynamiques
    dyn = collections.defaultdict(set)
    for k, a in (miz.warehouses_content.get("airports") or {}).items():
        if isinstance(a, dict) and a.get("dynamicSpawn"):
            dyn[str(a.get("coalition", "")).lower()].add(AF[int(k)]["name"])
    for side in ("blue", "red"):
        if dyn[side] != WANTED_SLOTS[side]:
            fail(f"slots dynamiques {side} : en trop {sorted(dyn[side] - WANTED_SLOTS[side])}, manquants {sorted(WANTED_SLOTS[side] - dyn[side])}")
    print(f"  slots dynamiques : bleu {len(dyn['blue'])}, rouge {len(dyn['red'])}, autres camps {sorted(k for k in dyn if k not in ('blue', 'red'))}")

    # porteurs #veafInterpreter et portées
    red_slots = {AF[i]["name"]: (AF[i]["x"], AF[i]["y"]) for i in AF if AF[i]["name"] in WANTED_SLOTS["red"]}
    blue_slots = {AF[i]["name"]: (AF[i]["x"], AF[i]["y"]) for i in AF if AF[i]["name"] in WANTED_SLOTS["blue"]}
    for side, _c, cat, g in groups(m):
        u0 = seq(g["units"])[0]
        if cat == "static" and u0.get("category") == "Heliports" and side == "blue":
            blue_slots[g["name"]] = (u0["x"], u0["y"])
        if cat == "ship" and side == "blue" and u0["type"] in ("Stennis", "CVN_71", "LHA_Tarawa"):
            blue_slots[g["name"]] = (u0["x"], u0["y"])
    worst = None
    for side, g, u in interp:
        alias = re.search(r'#veafInterpreter\["(-[\w]+)', u["name"]).group(1)
        expected = ALIASES.get(CMD_TO_GROUP.get(alias, ""), set())
        if u["type"] not in expected:
            fail(f"porteur {g['name']} : {u['type']} n'est pas dans le groupe généré par {alias}")
        if u["type"] in THREAT_NM:
            tgt = red_slots if side == "blue" else blue_slots
            n, d = min(((k, math.hypot(u["x"] - p[0], u["y"] - p[1]) / NM) for k, p in tgt.items()), key=lambda t: t[1])
            margin = d - THREAT_NM[u["type"]]
            if worst is None or margin < worst[2]:
                worst = (g["name"], n, margin)
            if margin < 0:
                fail(f"défense permanente {g['name']} atteint {n} ({d:.1f} nm < {THREAT_NM[u['type']]} nm)")
    print(f"  #veafInterpreter : {len(interp)} porteurs ; marge la plus faible : {worst[0]} → {worst[1]}, {worst[2]:.1f} nm")

    # configuration VEAF
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        cfg = next((n for n in names if n.endswith("veaf-config.lua")), None)
        txt = z.read(cfg).decode("utf-8") if cfg else ""
        pics = [n for n in names if n.startswith("l10n/DEFAULT/carte") and n.endswith(".jpg")]
    counts = {k: len(re.findall(p, txt)) for k, p in {"zones": r"veafCombatZone\.AddZone", "QRA": r"VeafQRA:new\(\)",
                                                       "CAP": r"addCapMission\(", "sanctuaires": r"VeafSanctuaryZone:new\(\)|addZoneFromTriggerZone\("}.items()}
    sec = [ln.strip() for ln in txt.splitlines() if "SecurityDisabled" in ln][:1]
    lvl = [ln.strip() for ln in txt.splitlines() if "ForcedLogLevel" in ln][:1]
    print(f"  veaf-config.lua : {counts} ; sécurité {sec} ; log {lvl}")
    for k, v in EXPECTED.items():
        if counts[k] != v:
            fail(f"veaf-config.lua : {counts[k]} {k}, {v} attendus")
    test = "bridge" in os.path.basename(path) or "LOCAL_TEST" in os.path.basename(path)
    disabled = any("= true" in s for s in sec)
    if disabled != test:
        fail(f"sécurité {'coupée' if disabled else 'active'} dans un build {'de test' if test else 'serveur'}")
    for asset in Y["modules"]["ASSETS"]["assets"]:
        for key in ("name", "linked"):
            if asset.get(key) and gnames[asset[key]] == 0:
                fail(f"ASSETS : le groupe {asset[key]} n'existe pas")
    if m.get("requiredModules"):
        fail(f"requiredModules non vide : {m['requiredModules']}")
    pb, pn, pr = seq(m.get("pictureFileNameB")), seq(m.get("pictureFileNameN")), seq(m.get("pictureFileNameR"))
    print(f"  images : {len(pics)} dans le .miz, B {len(pb)}, N {len(pn)}, R {len(pr)}")
    if pr or len(pb) != len(pics) or pb != pn:
        fail("images de briefing mal listées")
    w = m["weather"]
    st = m.get("start_time", 0)
    print(f"  météo : clouds.preset {w.get('clouds', {}).get('preset')}, température {w.get('season', {}).get('temperature')}, "
          f"vent au sol {w.get('wind', {}).get('atGround')}, départ {st // 3600:02d}:{st % 3600 // 60:02d}, date {m.get('date')}")
    if (w.get("clouds", {}).get("base") or 0) < 300 and w.get("clouds", {}).get("density", 0) > 0:
        fail(f"nuages au sol : base {w.get('clouds', {}).get('base')} m")
    if (w.get("clouds", {}).get("base") or 0) == 0 and str(w.get("clouds", {}).get("preset", "")).startswith("Preset"):
        fail(f"nuages au sol : preset {w['clouds'].get('preset')} à 0 m (squelette du scaffold)")
    return {"preset": w.get("clouds", {}).get("preset"), "temp": w.get("season", {}).get("temperature"),
            "wind": json.dumps(w.get("wind", {}).get("atGround"), sort_keys=True), "start": st, "security": sec}


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        base = glob.glob(str(ROOT / "VEAF_OpenTraining_Sinai_ICAO_HECA_2*.miz"))
        paths = ([max(base, key=os.path.getmtime)] if base else []) + sorted(glob.glob(str(ROOT / "missions" / "*.miz")))
    results = {os.path.basename(p): check(p) for p in paths}
    if len(results) > 1:
        sig = {(r["preset"], r["temp"], r["wind"]) for r in results.values()}
        print(f"\n{len(results)} fichiers, {len(sig)} météos distinctes (preset, température, vent au sol)")
        # deux variantes de missions/ ne doivent pas être la même mission : même ciel ET même heure
        seen = {}
        for name, r in results.items():
            if not name.startswith("VEAF_OpenTraining_Sinai_ICAO_HECA_") or name[-12:-4].isdigit():
                continue
            k = (r["preset"], r["temp"], r["wind"], r["start"])
            if k in seen:
                fail(f"variantes identiques dans les champs que DCS lit : {seen[k]} et {name}")
            seen[k] = name
    print(f"\nVERDICT : {'OK' if not FAILS else f'{len(FAILS)} échec(s)'}")
