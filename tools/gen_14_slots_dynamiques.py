"""Écrit src/dynamic-slot-templates.yaml : le catalogue livré (published/ de la release installée), sans les
appareils d'une autre époque ni les mods.

Retirés : WW2 et premiers jets (Bf-109, FW-190, I-16, La-7, P-47, P-51, TF-51, Spitfire, Mosquito, F4U, F-86,
MiG-15, MiG-19, F-100) ; et les mods : A-4E-C, OV-10A Bronco, T-45 (absents de la base d'unités DCS,
list_unit_types) et MB-339 (présent dans la base, mais mod communautaire). Un seul mod dans la mission suffit à
fermer le serveur aux joueurs qui ne l'ont pas.
"""
import yaml

from lib import M
from paths import ROOT

SRC = ROOT / "published/src/defaults/mission-folder/src/dynamic-slot-templates.yaml"
DROP = {"Bf-109K-4", "FW-190A8", "FW-190D9", "I-16", "La-7", "P-47D-30", "P-47D-40", "P-51D", "P-51D-30-NA", "TF-51D",
        "SpitfireLFMkIX", "MosquitoFBMkVI", "F4U-1D", "F4U-1D_CW", "F-86F Sabre", "MiG-15bis", "MiG-19P", "F-100D",
        "A-4E-C", "Bronco-OV-10A", "T-45", "MB-339APAN"}
if __name__ == "__main__":
    d = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    kept = dropped = 0
    for fam in ("airplanes", "helicopters"):
        for side, cs in d[fam]["coalitions"].items():
            for c, gs in cs.items():
                for n in list(gs):
                    u = gs[n]["units"][1] if isinstance(gs[n]["units"], dict) else gs[n]["units"][0]
                    if u["type"] in DROP:
                        del gs[n]
                        dropped += 1
                    else:
                        kept += 1
    HEADER = """# Open Training Sinaï (moderne, 2025) : catalogue livré par veaf-tools 6.29.0 recopié le 12/10/2026 par
# tools/gen_14_slots_dynamiques.py, sans les appareils d'une autre époque ni les mods (A-4E-C, OV-10A, T-45, MB-339).
# Ce fichier n'est donc plus vide : le catalogue livré n'est plus lu, une mise à jour de veaf-tools n'y ajoute rien.
"""
    with open(M + "/src/dynamic-slot-templates.yaml", "w", encoding="utf-8") as f:
        f.write(HEADER)
        yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False, width=200)
    print(kept, "modèles gardés,", dropped, "retirés")
