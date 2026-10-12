# Outils de la mission

Scripts Python qui ont construit la mission et qui produisent ce qu'on ne tape pas à la main : le briefing, les cartes, la mission de test, les contrôles.
Ils importent le code Python de VMCT : par défaut le dépôt voisin `../VEAF-Mission-Creation-Tools` (branche `develop`), ou le dossier désigné par la variable `VMCT_PY` (le dossier `src/python/veaf-tools` d'un autre checkout).
Ils se lancent depuis `tools/`, avec le Python de l'environnement poetry de VMCT :

```powershell
$PY = (poetry -C ..\..\VEAF-Mission-Creation-Tools env info -p) + "\Scripts\python.exe"
& $PY gather.py
```

Pipeline repris de l'OT Golfe Persique v6 (lui-même venu des Mariannes), adapté au Sinaï.

## Construction (historique, à ne pas rejouer)

Chaque `gen_NN_*.py` écrit un lot d'actions `veaf-mission-mcp` dans `batches/`, que `mcp.py batch batches/<lot>.json` exécute dans le processus.
**Un lot ne se rejoue pas** : `add_group` ne dédoublonne pas, un second passage crée des doublons (les dessins F10, eux, sont refusés par nom).
Les lots au sol (05b, 06, 07, 07b, 08, 16) ont besoin de la grille d'altitude SinaiMap (`veaf-tools dcs terrain-sweep SinaiMap`) : `lib.spot()` et `lib.land()` ramènent chaque position sur la terre ferme et refusent sans elle.

| Script | Lot |
|---|---|
| `geocode_places.py` | Lieux réels (`places.json`) ; les homonymes hors du théâtre sont remplacés par leurs coordonnées réelles dans `lib.py` |
| `gen_04_bases.py` | Camp des aérodromes, slots dynamiques |
| `gen_05_soutien.py` | Ravitailleurs, AWACS, escortes, Reaper 1 |
| `gen_05b_farps_porte_avions.py` | Quatre FARP, trois groupes aéronavals, slots sur les ponts |
| `gen_06_defense.py` | Défense aérienne permanente (`#veafInterpreter`) |
| `gen_07_entrainement.py` | Les 3 familles × 3 niveaux d'entraînement, et la zone touristique |
| `gen_07b_tourisme.py` | Balises radio du circuit des pyramides (sons morse écrits dans `sons/`) |
| `gen_07c_guide.py` | Guide touristique : bloc Lua de `src/scripts/mission-script.lua` (se rejoue sans doublon) |
| `gen_08_zones.py` | Les 16 vraies zones de combat, Reaper 2 |
| `gen_09_qra_cap.py` | QRA et CAP à la demande |
| `gen_10_joueurs.py` | Sanctuaires, arène, groupes des missions scénarisées |
| `gen_11_config.py` | `mission.yaml` : identité, profils, ASSETS, SANCTUARY, `combat_missions:`, CTLD (se rejoue) |
| `gen_12_presets.py`, `gen_13_waypoints.py`, `gen_14_slots_dynamiques.py` | `src/presets.yaml`, `src/waypoints.yaml`, `src/dynamic-slot-templates.yaml` |
| `gen_15_identite.py`, `gen_16_dessins.py` | Date, météo de base, bullseye, briefing DCS ; dessins F10 |
| `inert_targets.py`, `ground_control_roles.py` | Cibles inertes (tir interdit, sans dispersion) ; rôles sans avion à 5 par camp |

## Après tout changement

| Script | Ce qu'il fait |
|---|---|
| `sync_zones.py` | Réécrit le bloc `COMBATZONE` de `mission.yaml` (noms, menus, inclusions, briefings) depuis `gen_07` et `gen_08`, qui en sont la source |
| `gather.py` | Relève dans la mission tout ce que le briefing affiche → `briefing_data.json` |
| `gen_readme.py` | Écrit `README.md` (le briefing des pilotes) et redessine les cartes par `gen_map.py` |
| `gen_map.py` | Carte générale `docs/carte.jpg` et zooms `docs/cartes/` sur fond OpenStreetMap (tuiles en cache dans `tiles/`), copiés dans `src/mission/l10n/DEFAULT/` et déclarés dans la mission |
| `check_portees.py` | Portée de chaque défense et de chaque zone face à ce qu'elle ne doit pas atteindre → `docs/portees.md` ; ligne `VERDICT` |
| `check_presets.py` | Plan radio : aucun doublon dans une liste, aucun canal sur une tour ; ligne `VERDICT` |
| `verify.py` | Contrôles du `.miz` construit (noms, slots, soutien, porteurs, images, météo, sécurité) ; ligne `VERDICT` |
| `make_test_mission.py` | Mission de test locale `bridge/bridge-Sinai-OT.miz` (LOCAL_TEST, game master, A-10C II à Cairo West, dcs-bridge), puis rebuild serveur |

Ordre : `sync_zones.py`, build serveur (`.\veaf-tools.exe mission build`), `gather.py`, `gen_readme.py`, rebuild serveur (les cartes sont dans le `.miz`), `check_portees.py`, `verify.py`.

Retours sur les outils VMCT : `retours-vmct.md`.
