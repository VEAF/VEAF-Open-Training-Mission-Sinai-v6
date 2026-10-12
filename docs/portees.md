# Portées des défenses — contrôle de tools/check_portees.py

Portée = `threat_range_m` du lanceur dans la base d'unités DCS (cercles de l'éditeur). Distance = au plus proche de ce que l'arme ne doit pas atteindre (base adverse avec slots ; pour une zone, aussi les pistes des ravitailleurs bleus et les zones d'entraînement des autres familles).

| Type | Groupe ou zone | Arme | Portée (km) | Cible la plus proche | Distance (km) | |
|---|---|---|---|---|---|---|
| permanent | AD Abu Suwayr Avenger | M1097 Avenger | 4.5 | Melez | 101.4 | ✅ |
| permanent | AD Abu Suwayr Hawk | Hawk ln | 45.0 | Melez | 105.8 | ✅ |
| permanent | AD Ben Gurion Avenger | M1097 Avenger | 4.5 | El Arish | 147.7 | ✅ |
| permanent | AD Ben Gurion Patriot | Patriot ln | 100.0 | El Arish | 149.1 | ✅ |
| permanent | AD Beni Suef Avenger | M1097 Avenger | 4.5 | Melez | 247.4 | ✅ |
| permanent | AD Beni Suef Hawk | Hawk ln | 45.0 | Melez | 242.9 | ✅ |
| permanent | AD Cairo West Avenger | M1097 Avenger | 4.5 | Melez | 217.2 | ✅ |
| permanent | AD Cairo West Hawk | Hawk ln | 45.0 | Melez | 221.6 | ✅ |
| permanent | AD Cairo West Patriot | Patriot ln | 100.0 | Melez | 217.6 | ✅ |
| permanent | AD El Arish SA-11 | SA-11 Buk LN 9A310M1 | 50.0 | Kedem | 86.8 | ✅ |
| permanent | AD El Arish SA-15 | Tor 9A331 | 12.0 | Kedem | 80.7 | ✅ |
| permanent | AD Fayed Avenger | M1097 Avenger | 4.5 | Melez | 85.5 | ✅ |
| permanent | AD Fayed Hawk | Hawk ln | 45.0 | Melez | 89.2 | ✅ |
| permanent | AD Hatzerim Hawk | Hawk ln | 45.0 | El Arish | 87.4 | ✅ |
| permanent | AD Hatzerim NASAMS | NASAMS_LN_C | 15.0 | El Arish | 81.6 | ✅ |
| permanent | AD Hurghada Avenger | M1097 Avenger | 4.5 | St Catherine | 167.5 | ✅ |
| permanent | AD Hurghada Hawk | Hawk ln | 45.0 | St Catherine | 169.9 | ✅ |
| permanent | AD Inshas Avenger | M1097 Avenger | 4.5 | Melez | 164.0 | ✅ |
| permanent | AD Inshas Patriot | Patriot ln | 100.0 | Melez | 163.7 | ✅ |
| permanent | AD Kedem Avenger | M1097 Avenger | 4.5 | El Arish | 81.8 | ✅ |
| permanent | AD Melez SA-11 | SA-11 Buk LN 9A310M1 | 50.0 | Fayed | 90.2 | ✅ |
| permanent | AD Melez SA-15 | Tor 9A331 | 12.0 | Fayed | 83.6 | ✅ |
| permanent | AD Nevatim Avenger | M1097 Avenger | 4.5 | El Arish | 114.2 | ✅ |
| permanent | AD Nevatim Patriot | Patriot ln | 100.0 | El Arish | 118.3 | ✅ |
| permanent | AD Ramon Hawk | Hawk ln | 45.0 | El Arish | 88.6 | ✅ |
| permanent | AD Ramon NASAMS | NASAMS_LN_C | 15.0 | El Arish | 84.6 | ✅ |
| permanent | AD Sharm SA-15 | Tor 9A331 | 12.0 | Hurghada International Airport | 108.6 | ✅ |
| permanent | AD Sinai Centre SA-10 | S-300PS 5P85C ln | 120.0 | Fayed | 141.2 | ✅ |
| permanent | AD St Catherine SA-10 | S-300PS 5P85C ln | 120.0 | Hurghada International Airport | 174.0 | ✅ |
| permanent | AD St Catherine SA-15 | Tor 9A331 | 12.0 | Hurghada International Airport | 167.7 | ✅ |
| permanent | ARG-1 Tarawa | LHA_Tarawa | 20.0 | El Arish | 115.8 | ✅ |
| permanent | ARG-1 Tarawa | PERRY | 100.0 | El Arish | 115.8 | ✅ |
| permanent | CSG-71 Roosevelt | CVN_71 | 25.0 | St Catherine | 190.2 | ✅ |
| permanent | CSG-71 Roosevelt | TICONDEROG | 100.0 | St Catherine | 190.2 | ✅ |
| permanent | CSG-71 Roosevelt | USS_Arleigh_Burke_IIa | 100.0 | St Catherine | 190.2 | ✅ |
| permanent | CSG-74 Stennis | Stennis | 25.0 | El Arish | 145.3 | ✅ |
| permanent | CSG-74 Stennis | TICONDEROG | 100.0 | El Arish | 145.3 | ✅ |
| permanent | CSG-74 Stennis | USS_Arleigh_Burke_IIa | 100.0 | El Arish | 145.3 | ✅ |
| zone | combatZone_AbuAgeila | Osa 9A33 ln | 10.3 | Ramon Airbase | 53.0 | ✅ |
| zone | combatZone_AbuAgeila | Strela-10M3 | 5.0 | Ramon Airbase | 52.0 | ✅ |
| zone | combatZone_AbuAgeila | Ural-375 ZU-23 | 2.5 | Ramon Airbase | 52.5 | ✅ |
| zone | combatZone_AbuRudeis | Ural-375 ZU-23 | 2.5 | piste Arco 1 | 161.2 | ✅ |
| zone | combatZone_Arad_Hard | SA-18 Igla manpad | 5.2 | piste Texaco 2 | 11.0 | ✅ |
| zone | combatZone_Arad_Hard | Strela-10M3 | 5.0 | piste Texaco 2 | 11.3 | ✅ |
| zone | combatZone_Arad_Medium | Ural-375 ZU-23 | 2.5 | piste Texaco 2 | 10.3 | ✅ |
| zone | combatZone_Arad_Medium | ZSU-23-4 Shilka | 2.5 | piste Texaco 2 | 11.8 | ✅ |
| zone | combatZone_ConvoiElArish | Strela-1 9P31 | 4.2 | Ramon Airbase | 79.0 | ✅ |
| zone | combatZone_ConvoiElArish | Ural-375 ZU-23 | 2.5 | Ramon Airbase | 79.0 | ✅ |
| zone | combatZone_ConvoiFeiran | Ural-375 ZU-23 | 2.5 | Hurghada International Airport | 180.4 | ✅ |
| zone | combatZone_ConvoiNakhl | Strela-10M3 | 5.0 | Ramon Airbase | 132.9 | ✅ |
| zone | combatZone_Croiseur | MOSCOW | 75.0 | CSG-74 Stennis (route) | 125.6 | ✅ |
| zone | combatZone_Croiseur | NEUSTRASH | 12.0 | CSG-74 Stennis (route) | 125.5 | ✅ |
| zone | combatZone_Croiseur | REZKY | 16.0 | CSG-74 Stennis (route) | 125.3 | ✅ |
| zone | combatZone_DesertGizeh_Hard | Strela-1 9P31 | 4.2 | piste Overlord 1 | 10.8 | ✅ |
| zone | combatZone_DesertGizeh_Hard | Strela-10M3 | 5.0 | piste Overlord 1 | 10.4 | ✅ |
| zone | combatZone_DesertGizeh_Hard | ZSU-23-4 Shilka | 2.5 | piste Overlord 1 | 10.8 | ✅ |
| zone | combatZone_DesertGizeh_Medium | Strela-10M3 | 5.0 | piste Overlord 1 | 10.8 | ✅ |
| zone | combatZone_DesertGizeh_Medium | Ural-375 ZU-23 | 2.5 | piste Overlord 1 | 8.7 | ✅ |
| zone | combatZone_DesertOuest_Easy | Kub 2P25 ln | 25.0 | zone d'entraînement DesertGizeh | 62.7 | ✅ |
| zone | combatZone_DesertOuest_Easy | SA-11 Buk LN 9A310M1 | 50.0 | zone d'entraînement DesertGizeh | 62.4 | ✅ |
| zone | combatZone_DesertOuest_Medium | Osa 9A33 ln | 10.3 | zone d'entraînement DesertGizeh | 63.2 | ✅ |
| zone | combatZone_DesertOuest_Medium | Tor 9A331 | 12.0 | zone d'entraînement DesertGizeh | 61.2 | ✅ |
| zone | combatZone_ElGora | Tor 9A331 | 12.0 | Kedem | 49.9 | ✅ |
| zone | combatZone_ElGora | ZSU-23-4 Shilka | 2.5 | Kedem | 51.4 | ✅ |
| zone | combatZone_EtatMajor | Tor 9A331 | 12.0 | Fayed | 120.1 | ✅ |
| zone | combatZone_EtatMajor | ZSU-23-4 Shilka | 2.5 | Fayed | 120.5 | ✅ |
| zone | combatZone_Maghara | Kub 2P25 ln | 25.0 | Fayed | 116.2 | ✅ |
| zone | combatZone_Maghara | ZSU-23-4 Shilka | 2.5 | Fayed | 115.9 | ✅ |
| zone | combatZone_Mitla | Strela-10M3 | 5.0 | Fayed | 69.0 | ✅ |
| zone | combatZone_Mitla | ZSU-23-4 Shilka | 2.5 | Fayed | 70.0 | ✅ |
| zone | combatZone_Nakhl | 5p73 s-125 ln | 18.0 | Ramon Airbase | 125.9 | ✅ |
| zone | combatZone_Nakhl | S_75M_Volhov | 43.0 | Ramon Airbase | 126.1 | ✅ |
| zone | combatZone_Nakhl | ZSU-23-4 Shilka | 2.5 | Ramon Airbase | 126.3 | ✅ |
| zone | combatZone_Scud | Tor 9A331 | 12.0 | Ramon Airbase | 83.6 | ✅ |
| zone | combatZone_Scud | ZSU-23-4 Shilka | 2.5 | Ramon Airbase | 83.0 | ✅ |
| zone | combatZone_Sharm | Kub 2P25 ln | 25.0 | Hurghada International Airport | 107.0 | ✅ |
| zone | combatZone_Sharm | Ural-375 ZU-23 | 2.5 | Hurghada International Airport | 106.1 | ✅ |
| zone | combatZone_TeteDePont | Strela-10M3 | 5.0 | Abu Suwayr | 35.1 | ✅ |
| zone | combatZone_TeteDePont | Tor 9A331 | 12.0 | Abu Suwayr | 36.3 | ✅ |
| zone | combatZone_TeteDePont | Ural-375 ZU-23 | 2.5 | Abu Suwayr | 34.8 | ✅ |
| zone | combatZone_Tiran | speedboat | 1.0 | CSG-71 Roosevelt (route) | 107.7 | ✅ |
| zone | combatZone_UsinesPortFouad | Kub 2P25 ln | 25.0 | Abu Suwayr | 62.6 | ✅ |
| zone | combatZone_UsinesPortFouad | Strela-1 9P31 | 4.2 | Abu Suwayr | 62.4 | ✅ |
| zone | combatZone_UsinesPortFouad | Ural-375 ZU-23 | 2.5 | Abu Suwayr | 62.1 | ✅ |
