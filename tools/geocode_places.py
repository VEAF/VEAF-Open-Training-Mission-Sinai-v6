"""Géocode une fois les lieux réels dont la mission a besoin → tools/places.json (x/y DCS).

Relancer ajoute seulement les lieux absents. Chaque point est à relire : l'outil peut tomber sur un
homonyme (osm_type et nom affiché sont gardés pour ça).
"""
import json
import sys

from paths import ROOT  # noqa: F401  (met aussi le code VMCT sur sys.path)
from veaf_mission_mcp.actions import register_default_actions
from veaf_mission_mcp.catalog import ActionCatalog

sys.stdout.reconfigure(encoding="utf-8")
PLACES = [
    # Tourisme : plateau de Gizeh, Saqqarah, Dahchour
    "Great Pyramid of Giza", "Pyramid of Khafre", "Pyramid of Menkaure", "Great Sphinx of Giza",
    "Pyramid of Djoser", "Bent Pyramid", "Red Pyramid", "Meidum pyramid", "Cairo Citadel", "Cairo Tower",
    # Canal de Suez
    "Port Said", "Port Fouad", "El Qantara", "Ismailia", "Great Bitter Lake", "Suez, Egypt", "Ras Sudr",
    "Ahmed Hamdi Tunnel",
    # Sinaï
    "El Arish", "Rafah, North Sinai", "Sheikh Zuweid", "Bir al-Abd", "Rumana, North Sinai", "Bir Gifgafa",
    "Bir Tamada", "Nakhl, Egypt", "Mitla Pass", "Giddi Pass", "Jebel Libni", "Abu Ageila", "Al Hasana, North Sinai",
    "Kuntilla", "El Quseima", "Abu Rudeis", "Abu Zenima", "El Tor", "Saint Catherine, Egypt", "Mount Sinai",
    "Nuweiba", "Dahab", "Taba, Egypt", "Sharm El Sheikh", "Ras Mohammed", "Wadi Feiran", "Jebel Maghara",
    "Bir Hasanah", "Bardawil Lake",
    # Égypte, delta et désert occidental
    "Bilbeis", "Zagazig", "10th of Ramadan City", "Belbeis", "Inshas", "Helwan", "Fayoum", "Wadi El Natrun",
    "Sadat City", "Tanta", "Mansoura, Egypt", "Damietta", "El Salhiya El Gedida", "Kom Ombo", "Beni Suef",
    "Ain Sokhna", "Zafarana", "Gebel Galala", "New Administrative Capital",
    # Israël, Négev
    "Beersheba", "Dimona", "Mitzpe Ramon", "Eilat", "Yeruham", "Nitzana", "Ashdod", "Ashkelon", "Kadesh Barnea",
    "Arad, Israel", "Mount Hermon", "Har Keren",
    # Jordanie, Arabie
    "Aqaba", "Ma'an", "Tabuk", "Haql", "Petra",
]
out_path = ROOT / "tools" / "places.json"
places = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
cat = ActionCatalog()
register_default_actions(cat)
for q in PLACES:
    if q in places:
        continue
    try:
        r = cat.run_action("geocode", {"mission_path": str(ROOT), "query": q})
    except Exception as e:  # noqa: BLE001
        print("ERREUR", q, e)
        continue
    if not r.get("found"):
        print("INTROUVABLE", q)
        continue
    places[q] = {"x": round(r["xy"]["x"]), "y": round(r["xy"]["y"]), "osm": r.get("osm_type"), "name": r["display_name"][:90]}
    print(f"{q:28} {places[q]['x']:>8} {places[q]['y']:>8}  {places[q]['osm']:<14} {places[q]['name']}")
    out_path.write_text(json.dumps(places, indent=1, ensure_ascii=False), encoding="utf-8")
