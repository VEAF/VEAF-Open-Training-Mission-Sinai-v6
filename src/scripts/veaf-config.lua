---------------------------------------------------------------------------------------------------------------------------------------------
-- Généré par veaf-tools build depuis mission.yaml
-- Ne pas éditer manuellement.
-- Relancez 'veaf-tools build' ou 'veaf-tools generate-config' pour régénérer.
---------------------------------------------------------------------------------------------------------------------------------------------

-- ── Mission identity ─────────────────────────────────────────────────────────
veaf.config.MISSION_NAME = "VEAF_OpenTraining_Sinai_ICAO_HECA"
veaf.config.era = veaf.ERA.MODERN
veaf.silenceAtcOnAllAirbases()
veaf.HideNamesFromSpawnedGroups = true

veaf.config.language = "fr"

-- ── Airfield channels of the mission's radio plan (src/presets.yaml, `bases`) ──────
if veafAirbases then
    veafAirbases.MissionChannels = {
        [2] = { alias = "Base-Abu Suwayr", title = "Abu Suwayr", uhf = 251.1, vhf = 118.85, fm = 39.5 },
        [5] = { alias = "Base-Melez", title = "Melez", uhf = 252.05, vhf = 119.65, fm = 40.45 },
        [6] = { alias = "Base-Fayed", title = "Fayed", uhf = 252.1, vhf = 119.7, fm = 40.5 },
        [7] = { alias = "Base-Hatzerim", title = "Hatzerim / 96X", uhf = 252.15, vhf = 119.75, fm = 40.55 },
        [8] = { alias = "Base-Nevatim", title = "Nevatim", uhf = 252.2, vhf = 132.4, fm = 40.6 },
        [9] = { alias = "Base-Ramon Airbase", title = "Ramon Airbase / 105X", uhf = 252.25, vhf = 119.8, fm = 40.65 },
        [12] = { alias = "Base-Kedem", title = "Kedem", uhf = 250.15, vhf = 118.15, fm = 38.55 },
        [18] = { alias = "Base-Cairo West", title = "Cairo West", uhf = 250.45, vhf = 131.2, fm = 38.85 },
        [19] = { alias = "Base-Inshas Airbase", title = "Inshas Airbase", uhf = 250.5, vhf = 118.4, fm = 38.9 },
        [24] = { alias = "Base-Ben-Gurion", title = "Ben-Gurion", uhf = 250.8, vhf = 134.6, fm = 39.2 },
        [25] = { alias = "Base-St Catherine", title = "St Catherine", uhf = 250.85, vhf = 124.5, fm = 39.25 },
        [26] = { alias = "Base-Abu Rudeis", title = "Abu Rudeis", uhf = 250.9, vhf = 118.5, fm = 39.3 },
        [28] = { alias = "Base-Bir Hasanah", title = "Bir Hasanah", uhf = 251.0, vhf = 118.8, fm = 39.4 },
        [29] = { alias = "Base-El Arish", title = "El Arish", uhf = 251.05, vhf = 121.0, fm = 39.45 },
        [30] = { alias = "Base-El Gora", title = "El Gora", uhf = 251.15, vhf = 118.2, fm = 39.55 },
        [33] = { alias = "Base-Beni Suef", title = "Beni Suef", uhf = 251.3, vhf = 127.1, fm = 39.7 },
        [38] = { alias = "Base-Hurghada International Airport", title = "Hurghada International Airport", uhf = 251.55, vhf = 119.6, fm = 39.95 },
        [42] = { alias = "Base-Sharm El Sheikh International Airport", title = "Sharm El Sheikh International Airport", uhf = 251.8, vhf = 118.9, fm = 40.2 },
    }
end

-- ── Global log level ─────────────────────────────────────────────────────────
veaf.ForcedLogLevel = "info"

-- ── CTLD 2 ───────────────────────────────────────────────────────────────────
-- Configuration lives in ctld-config.yaml (edit it with ctld-tools); this only starts it.
veaf.config.manage_airbase_logistics = true
veaf.config.airbase_logistics_radius = 2500
veaf.config.airbase_occupation_radius = 2000
veaf.config.airbase_logistics_tick = 30
-- One module's initialisation error must not take the others down (FIX-DEMO-MISSION-FINDINGS 02).
local function veafGuardedInit(name, initialize)
    local ok, err = xpcall(initialize, function(e)
        if debug and debug.traceback then
            return debug.traceback(tostring(e), 2)
        end
        return tostring(e)
    end)
    if not ok then
        veaf.loggers.get(veaf.Id):error("%s init failed: %s", name, err)
    end
end

veafGuardedInit("CTLD", function()
if ctld then
    veaf.ctld_initialize()
end
end)

-- ── Module configuration + initialization ────────────────────────────────────

-- ── Core ──

veafGuardedInit("SECURITY", function()
if veafSecurity then
    veafSecurity.initialize()
end
end)

veafGuardedInit("RADIO", function()
if veafRadio then
    veafRadio.initialize(true)
end
end)

veafGuardedInit("SHORTCUTS", function()
if veafShortcuts then
    veafShortcuts.initialize()
end
end)

veafGuardedInit("NAMEDPOINTS", function()
if veafNamedPoints then
    veafNamedPoints.initialize({})
end
end)

veafGuardedInit("SPAWN", function()
if veafSpawn then
    veafSpawn.initialize()
end
end)

-- ── Combat ──

veafGuardedInit("CARRIER", function()
if veafCarrierOperations then
    veafCarrierOperations.initialize(true)
end
end)

veafGuardedInit("CASMISSION", function()
if veafCasMission then
    veafCasMission.initialize()
end
end)

veafGuardedInit("TRANSPORTMISSION", function()
if veafTransportMission then
    veafTransportMission.initialize()
end
end)

veafGuardedInit("COMBATMISSION", function()
if veafCombatMission then
    veafCombatMission.addCapMission("CAP-Centre-MiG29", "CAP rouge MiG-29S (Fox 1) — centre du Sinaï — FL220", "Deux MiG-29S armés de R-27R, R-73 et R-60 patrouillent entre Bir Hasanah et Bir Gifgafa, au FL220. Emport : R-73*2,R-60M*2,R-27R*2,Fuel-1500.", false, true)
    veafCombatMission.addCapMission("CAP-Nord-Su27", "CAP rouge Su-27 (Fox 1, longue portée) — nord du Sinaï — FL260", "Deux Su-27 armés de R-27ER et R-73 patrouillent le long de la côte nord, de Bir al-Abd à El Arish, au FL260. Emport : R-73*4,R-27ER*6.", false, true)
    veafCombatMission.addCapMission("CAP-Sud-MiG31", "CAP rouge MiG-31 (intercepteur haut et rapide, R-33) — sud du Sinaï — FL380", "Deux MiG-31 armés de R-33 patrouillent haut et vite au-dessus de St Catherine, au FL380. Emport : R-40R*2,R-33*4.", false, true)
    veafCombatMission.addCapMission("Raid-Tu22M", "Raid rouge Tu-22M3 à intercepter — Nakhl — FL300", "Deux bombardiers Tu-22M3 chargés de bombes tournent au-dessus de Nakhl, au FL300, prêts à frapper le canal : les intercepter. Emport : FAB-500*33.", false, true)
    veafCombatMission.addCapMission("CAP-Canal-F16", "CAP bleue F-16C (Fox 3) — rive ouest du canal — FL220", "Deux F-16C égyptiens patrouillent sur la rive ouest du canal, d'Ismaïlia à Suez, au FL220. Emport : AIM-120C*4,AIM-9M*2,ECM,Fuel*2.", false, true)
    veafCombatMission.addCapMission("CAP-Negev-F15", "CAP bleue F-15C (Fox 3) — Néguev — FL250", "Deux F-15C israéliens couvrent le Néguev, de Hatzerim à Ramon, au FL250. Emport : AIM-9*4,AIM-120*4,Fuel.", false, true)
    veafCombatMission.AddMissionsWithSkillAndScale(
        VeafCombatMission:new()
        :setName("Defense-AbuSuwayr")
        :setFriendlyName("Défense — raid rouge sur Abu Suwayr")
        :setSecured(false)
        :setRadioMenuEnabled(true)
        :setBriefing([[Deux Su-24M armés de missiles antiradar ouvrent la route à quatre Su-34 chargés de bombes, escortés de deux Su-30, partis du centre du Sinaï vers la base d'Abu Suwayr, sur le canal. Abattez les bombardiers avant le largage.
Échec si la base est bombardée (constaté par vous : la mission ne le vérifie pas).]])
        :addElement(
            VeafCombatMissionElement:new()
            :setName("SEAD")
            :setGroups({"SC-Defense-AbuSuwayr-SEAD"})
            :setScalable(false)
        )
        :addElement(
            VeafCombatMissionElement:new()
            :setName("Bombardiers")
            :setGroups({"SC-Defense-AbuSuwayr-Bombers"})
            :setScalable(false)
        )
        :addElement(
            VeafCombatMissionElement:new()
            :setName("Escorte")
            :setGroups({"SC-Defense-AbuSuwayr-Escort"})
            :setScalable(true)
        )
    )
    veafCombatMission.AddMissionsWithSkillAndScale(
        VeafCombatMission:new()
        :setName("Interception-VIP")
        :setFriendlyName("Interception — transport VIP de St Catherine à El Arish")
        :setSecured(false)
        :setRadioMenuEnabled(true)
        :setBriefing([[Un IL-76 emmène l'état-major rouge de St Catherine vers El Arish, escorté par deux MiG-29S. Interceptez-le avant El Arish : la fin de la route est sous la QRA et les défenses d'El Arish.]])
        :addElement(
            VeafCombatMissionElement:new()
            :setName("Transport")
            :setGroups({"SC-Intercept-VIP-Il76"})
            :setScalable(false)
        )
        :addElement(
            VeafCombatMissionElement:new()
            :setName("Escorte")
            :setGroups({"SC-Intercept-VIP-Escort"})
            :setScalable(true)
        )
    )
    veafCombatMission.initialize()
end
end)

veafGuardedInit("COMBATZONE", function()
if veafCombatZone then
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Arad_Easy")
        :setFriendlyName("H1 Hélico Arad — facile")
        :setRadioGroupName("Entraînement hélicoptères")
        :setBriefing([[Champ de tir hélicoptères d'Arad, sur le plateau au nord-est de la ville, à 10 nm du FARP Range : cibles inertes (chars, blindés et camions immobiles, tir interdit).
Position : bullseye 054°/116 nm (N31°18.143' E035°15.400'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 8 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 6 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Arad_Medium")
        :setFriendlyName("H2 Hélico Arad — moyen")
        :setRadioGroupName("Entraînement hélicoptères")
        :setBriefing([[Champ de tir hélicoptères d'Arad : de l'artillerie antiaérienne légère (ZU-23, parfois un Shilka) en plus des cibles du niveau facile.
Position : bullseye 054°/116 nm (N31°18.143' E035°15.400'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 8 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 6 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Arad_Hard")
        :setFriendlyName("H3 Hélico Arad — difficile")
        :setRadioGroupName("Entraînement hélicoptères")
        :setBriefing([[Champ de tir hélicoptères d'Arad, avec une défense courte portée réaliste : un SA-13 et une équipe de lance-missiles portatifs SA-18, à guidage infrarouge.
Position : bullseye 054°/116 nm (N31°18.143' E035°15.400'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 8 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 6 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_DesertGizeh_Easy")
        :setFriendlyName("A1 Attaque désert de Gizeh — facile")
        :setRadioGroupName("Entraînement attaque")
        :setBriefing([[Champ de tir air-sol dans le désert au sud-ouest de Cairo West, à 17 nm de la base : blindés et camions immobiles en tir interdit, dépôt de carburant et poste de commandement. Le drone Reaper 1 tourne au-dessus.
Position : bullseye 265°/146 nm (N29°56.835' E030°37.497'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 59 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 49 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_DesertGizeh_Medium")
        :setFriendlyName("A2 Attaque désert de Gizeh — moyen")
        :setRadioGroupName("Entraînement attaque")
        :setBriefing([[Champ de tir du désert de Gizeh : une compagnie blindée active et de l'artillerie antiaérienne légère en plus des cibles du niveau facile.
Position : bullseye 265°/146 nm (N29°56.835' E030°37.497'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 59 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 49 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_DesertGizeh_Hard")
        :setFriendlyName("A3 Attaque désert de Gizeh — difficile")
        :setRadioGroupName("Entraînement attaque")
        :setBriefing([[Champ de tir du désert de Gizeh : un second groupe blindé et une défense courte portée à guidage infrarouge (SA-13 ou SA-9), avec un Shilka.
Position : bullseye 265°/146 nm (N29°56.835' E030°37.497'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 59 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 49 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_DesertOuest_Easy")
        :setFriendlyName("S1 SEAD désert occidental — facile")
        :setRadioGroupName("Entraînement SEAD")
        :setBriefing([[Site SEAD dans le désert occidental, à 52 nm au sud-ouest de Cairo West : une batterie sol-air moyenne portée, SA-6 ou SA-11 tirée au sort.
Position : bullseye 259°/178 nm (N29°37.218' E030°03.892'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 89 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 78 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_DesertOuest_Medium")
        :setFriendlyName("S2 SEAD désert occidental — moyen")
        :setRadioGroupName("Entraînement SEAD")
        :setBriefing([[Site SEAD du désert occidental : la batterie moyenne portée est protégée par une défense courte portée (SA-15, SA-8).
Position : bullseye 259°/178 nm (N29°37.218' E030°03.892'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 89 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 78 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_DesertOuest_Hard")
        :setFriendlyName("S3 SEAD désert occidental — difficile")
        :setRadioGroupName("Entraînement SEAD")
        :setBriefing([[Site SEAD du désert occidental en réseau Skynet : un radar d'alerte avancée guide les batteries, qui restent éteintes jusqu'au dernier moment.
Position : bullseye 259°/178 nm (N29°37.218' E030°03.892'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 89 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 78 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Pyramides")
        :setFriendlyName("T Tourisme — pyramides de Gizeh")
        :setRadioGroupName("Tourisme")
        :setBriefing([[Visite aérienne des pyramides, hors combat, au départ du FARP Pyramides (2 nm au sud-ouest du plateau). Circuit : Gizeh (Khéops, Khéphren, Mykérinos, le Sphinx), puis Saqqarah (pyramide à degrés de Djoser, 8 nm au sud-sud-est), puis Dahchour (pyramide rouge et pyramide rhomboïdale, 4 nm plus au sud). Une balise radio FM à chaque site (GIZ 31.0, SAQ 32.0, DAH 33.0) ; survolez un monument à moins de 1 500 ft sol et un guide vous le raconte. Excursion : la pyramide effondrée de Meïdoum, 25 nm au sud de Dahchour. Dans le sanctuaire bleu du Caire : un appareil rouge y est détruit.
Position : bullseye 264°/119 nm (N29°58.296' E031°08.157').]])
        :setCompletable(false)
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_TeteDePont")
        :setFriendlyName("Z01 Front ouest — tête de pont face à Ismaïlia")
        :setRadioGroupName("Front")
        :setBriefing([[La brigade blindée rouge qui tient la rive est du canal, face à Ismaïlia : chars, blindés et lance-roquettes en position. Détruire les blindés et l'artillerie ; défense SA-15 possible, SA-13 et artillerie antiaérienne. Les Hawk d'Abu Suwayr couvrent la rive ouest.
Position : bullseye 297°/55 nm (N30°37.038' E032°27.935'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 46 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 53 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Mitla")
        :setFriendlyName("Z02 Front ouest — ligne du col de Mitla")
        :setRadioGroupName("Front")
        :setBriefing([[La ligne de défense rouge du col de Mitla, la route de Suez vers Nakhl : chars enterrés, blindés et artillerie automotrice. Défense courte portée seulement (SA-13, Shilka) : le drone Reaper 2 la désigne au laser.
Position : bullseye 248°/29 nm (N30°00.680' E032°53.471'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 59 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 70 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_AbuAgeila")
        :setFriendlyName("Z03 Front est — carrefour d'Abu Ageila")
        :setRadioGroupName("Front")
        :setBriefing([[Le carrefour fortifié d'Abu Ageila, sur la route d'El Arish à Ismaïlia, face à la frontière israélienne : une brigade mécanisée et ses lance-roquettes. Détruire les blindés et les Grad ; défense SA-8 et artillerie antiaérienne, sous la QRA d'El Arish.
Position : bullseye 043°/54 nm (N30°51.000' E034°07.200'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 51 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 64 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Maghara")
        :setFriendlyName("Z04 SEAD — site SA-6 du djebel Maghara")
        :setRadioGroupName("SEAD")
        :setBriefing([[Le site SA-6 perché au djebel Maghara, au nord du Sinaï, relié à un radar d'alerte avancée en réseau Skynet. Détruire le radar de conduite de tir et les lanceurs ; un Shilka protège le site.
Position : bullseye 359°/30 nm (N30°42.000' E033°24.000'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 89 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 100 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Nakhl")
        :setFriendlyName("Z05 SEAD — site sol-air de Nakhl")
        :setRadioGroupName("SEAD")
        :setBriefing([[Le site sol-air qui couvre le carrefour de Nakhl, au centre du Sinaï : une batterie SA-2 ou SA-3 tirée au sort, son radar d'alerte avancée et un Shilka. Sous la couverture lointaine du SA-10 du centre-sud.
Position : bullseye 128°/22 nm (N29°57.936' E033°44.784'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 91 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 99 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_ConvoiElArish")
        :setFriendlyName("Z06 Convoi — El Arish vers Abu Ageila")
        :setRadioGroupName("Convois")
        :setBriefing([[Un convoi de renforts quitte El Arish par la route du sud-est vers le carrefour d'Abu Ageila. L'arrêter avant Abu Ageila ; il porte sa propre artillerie antiaérienne (ZU-23) et un SA-9.
Position : bullseye 027°/50 nm (N30°56.152' E033°51.671'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 64 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 77 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_ConvoiNakhl")
        :setFriendlyName("Z07 Convoi — Nakhl vers le col de Mitla")
        :setRadioGroupName("Convois")
        :setBriefing([[Des renforts blindés roulent de Nakhl vers le col de Mitla, pour renforcer la ligne face à Suez. Les arrêter avant le col ; le convoi est escorté par un SA-13.
Position : bullseye 138°/19 nm (N29°57.423' E033°39.395'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 95 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 103 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_ConvoiFeiran")
        :setFriendlyName("Z08 Convoi — oasis de Feiran vers Abu Rudeis")
        :setRadioGroupName("Convois")
        :setBriefing([[Un convoi de carburant descend l'oued Feiran vers les dépôts d'Abu Rudeis, sur le golfe de Suez. Le détruire avant la côte ; il porte sa propre artillerie antiaérienne. Sous la couverture du SA-10 de St Catherine.
Position : bullseye 165°/86 nm (N28°48.247' E033°49.986'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 118 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 130 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_UsinesPortFouad")
        :setFriendlyName("Z09 Frappe — usines de Port-Fouad")
        :setRadioGroupName("Frappes en profondeur")
        :setBriefing([[Les usines de la zone industrielle au sud de Port-Fouad, sur la rive est du canal, reconverties en ateliers d'armement : ateliers, hangars, réservoirs chimiques. Tout détruire ; défense SA-6, SA-9 et artillerie antiaérienne (reprise de la v5).
Position : bullseye 314°/78 nm (N31°06.118' E032°19.738'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 64 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 66 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_EtatMajor")
        :setFriendlyName("Z10 Frappe — état-major de Bir Tamada")
        :setRadioGroupName("Frappes en profondeur")
        :setBriefing([[Le poste de commandement de l'armée rouge du Sinaï, enterré à Bir Tamada : bunkers, centre de transmissions, véhicules de commandement. Tout détruire ; défense SA-15 et Shilka, sous la QRA de Melez.
Position : bullseye 120°/5 nm (N30°09.000' E033°30.000'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 90 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 101 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Scud")
        :setFriendlyName("Z11 Frappe — base de missiles du djebel Libni")
        :setRadioGroupName("Frappes en profondeur")
        :setBriefing([[Une base de missiles sol-sol au pied du djebel Libni, d'où les Scud menacent Le Caire et Beer-Sheva : lanceurs et camions de ravitaillement. Détruire les lanceurs ; défense SA-15 et Shilka.
Position : bullseye 033°/36 nm (N30°42.000' E033°48.000'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 69 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 81 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_AbuRudeis")
        :setFriendlyName("Z12 Frappe — dépôts pétroliers d'Abu Rudeis")
        :setRadioGroupName("Frappes en profondeur")
        :setBriefing([[Les dépôts pétroliers d'Abu Rudeis, sur la côte du golfe de Suez : ils ravitaillent toute l'armée rouge du sud. Détruire réservoirs et pompes ; ZU-23 sur place, et le SA-10 de St Catherine à moins de 40 nm.
Position : bullseye 186°/76 nm (N28°56.323' E033°14.804'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 87 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 99 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_ElGora")
        :setFriendlyName("Z13 OCA — base aérienne d'El Gora")
        :setRadioGroupName("Bases aériennes")
        :setBriefing([[La base aérienne d'El Gora, à 30 km de la frontière israélienne : chasseurs-bombardiers au parking, hangars et carburant. Tout détruire au sol ; défense SA-15 et Shilka.
Position : bullseye 036°/65 nm (N31°04.377' E034°09.279'). Ravitailleurs : Arco 2 (panier, TACAN 53Y, 293.0) à 49 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 62 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Sharm")
        :setFriendlyName("Z14 OCA — base aérienne de Sharm el-Cheikh")
        :setRadioGroupName("Bases aériennes")
        :setBriefing([[L'aéroport de Sharm el-Cheikh, devenu base aérienne rouge à la pointe sud du Sinaï : avions de transport et hélicoptères d'attaque au sol, hangars. Tout détruire au sol ; défense SA-6 et ZU-23, plus le SA-15 permanent de la base.
Position : bullseye 158°/142 nm (N27°58.729' E034°23.109'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 169 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 179 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Croiseur")
        :setFriendlyName("Z15 Antinavire — croiseur Moskva devant Damiette")
        :setRadioGroupName("Antinavire")
        :setBriefing([[Le croiseur lance-missiles rouge Moskva et deux frégates croisent en Méditerranée, à 38 nm au nord de Damiette, pour couper la route des porte-avions. Les couler : le Moskva porte des missiles sol-air à 40 nm, les frégates à courte portée (reprise de la v5, dont le croiseur était le Piotr Velikiy).
Position : bullseye 326°/134 nm (N32°02.379' E031°56.947'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 114 nm ; Texaco 1 (perche, TACAN 50Y, 290.0) à 110 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Tiran")
        :setFriendlyName("Z16 Antinavire — détroit de Tiran")
        :setRadioGroupName("Antinavire")
        :setBriefing([[Le rouge ferme le détroit de Tiran, la sortie du golfe d'Aqaba : une batterie de missiles antinavires (HY-2 Silkworm, portée 54 nm) à Ras Nasrani et un essaim de vedettes rapides dans le détroit. Détruire lanceurs et radar, couler les vedettes ; SA-15 permanent à Sharm el-Cheikh.
Position : bullseye 157°/145 nm (N27°56.894' E034°27.427'). Ravitailleurs : Arco 1 (panier, TACAN 51Y, 291.0) à 173 nm ; Texaco 2 (perche, TACAN 52Y, 292.0) à 180 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.GetZone("combatZone_Arad_Medium"):addZoneElementsFromZoneNamed("combatZone_Arad_Easy")
    veafCombatZone.GetZone("combatZone_Arad_Hard"):addZoneElementsFromZoneNamed("combatZone_Arad_Medium")
    veafCombatZone.GetZone("combatZone_Arad_Hard"):addZoneElementsFromZoneNamed("combatZone_Arad_Easy")
    veafCombatZone.GetZone("combatZone_DesertGizeh_Medium"):addZoneElementsFromZoneNamed("combatZone_DesertGizeh_Easy")
    veafCombatZone.GetZone("combatZone_DesertGizeh_Hard"):addZoneElementsFromZoneNamed("combatZone_DesertGizeh_Medium")
    veafCombatZone.GetZone("combatZone_DesertGizeh_Hard"):addZoneElementsFromZoneNamed("combatZone_DesertGizeh_Easy")
    veafCombatZone.GetZone("combatZone_DesertOuest_Medium"):addZoneElementsFromZoneNamed("combatZone_DesertOuest_Easy")
    veafCombatZone.GetZone("combatZone_DesertOuest_Hard"):addZoneElementsFromZoneNamed("combatZone_DesertOuest_Medium")
    veafCombatZone.GetZone("combatZone_DesertOuest_Hard"):addZoneElementsFromZoneNamed("combatZone_DesertOuest_Easy")
    veafCombatZone.initialize()
end
end)

veafGuardedInit("QRA", function()
if veafQraManager then
    veafQraManager.initialize()
    local QRA_Melez = VeafQRA:new()
        :setName("QRA Melez")
        :setCoalition(coalition.side.RED)
        :addEnnemyCoalition(coalition.side.BLUE)
        :setTriggerZone("QRA-Melez")
        :setRandomGroupsToDeployByEnemyQuantity(1, {"QRA-Melez-MiG29", "QRA-Melez-Su27"}, 1)
        :setRandomGroupsToDeployByEnemyQuantity(3, {"QRA-Melez-Su30", "QRA-Melez-MiG29x4"}, 1)
        :setDelayBeforeRearming(600)
        :setDelayBeforeActivating(90)
        :setAirportLink("Melez")
        :start()
    local QRA_El_Arish = VeafQRA:new()
        :setName("QRA El Arish")
        :setCoalition(coalition.side.RED)
        :addEnnemyCoalition(coalition.side.BLUE)
        :setTriggerZone("QRA-ElArish")
        :setRandomGroupsToDeployByEnemyQuantity(1, {"QRA-ElArish-Su27", "QRA-ElArish-MiG29"}, 1)
        :setRandomGroupsToDeployByEnemyQuantity(3, {"QRA-ElArish-Su30", "QRA-ElArish-Su27x4"}, 1)
        :setDelayBeforeRearming(600)
        :setDelayBeforeActivating(90)
        :setAirportLink("El Arish")
        :start()
    local QRA_Abu_Suwayr = VeafQRA:new()
        :setName("QRA Abu Suwayr")
        :setCoalition(coalition.side.BLUE)
        :addEnnemyCoalition(coalition.side.RED)
        :setTriggerZone("QRA-AbuSuwayr")
        :setRandomGroupsToDeployByEnemyQuantity(1, {"QRA-AbuSuwayr-F16", "QRA-AbuSuwayr-M2000"}, 1)
        :setRandomGroupsToDeployByEnemyQuantity(3, {"QRA-AbuSuwayr-F16x4", "QRA-AbuSuwayr-M2000x4"}, 1)
        :setDelayBeforeRearming(600)
        :setDelayBeforeActivating(90)
        :setAirportLink("Abu Suwayr")
        :start()
    local QRA_Hatzerim = VeafQRA:new()
        :setName("QRA Hatzerim")
        :setCoalition(coalition.side.BLUE)
        :addEnnemyCoalition(coalition.side.RED)
        :setTriggerZone("QRA-Hatzerim")
        :setRandomGroupsToDeployByEnemyQuantity(1, {"QRA-Hatzerim-F15", "QRA-Hatzerim-F16"}, 1)
        :setRandomGroupsToDeployByEnemyQuantity(3, {"QRA-Hatzerim-F15x4", "QRA-Hatzerim-F16x4"}, 1)
        :setDelayBeforeRearming(600)
        :setDelayBeforeActivating(90)
        :setAirportLink("Hatzerim")
        :start()
end
end)

-- ── Features ──

veafGuardedInit("GRASS", function()
if veafGrass then
    veafGrass.initialize()
end
end)

veafGuardedInit("ASSETS", function()
if veafAssets then
    veafAssets.Assets = {
        {sort = 1, name = "Overlord 1", description = "Overlord 1 (E-3A) — AWACS ouest", information = "U282.0 — FL300 — orbite nord-sud à l'ouest de Cairo West", linked = "Overlord 1 - Escort", coalition = coalition.side.BLUE},
        {sort = 2, name = "Magic 1", description = "Magic 1 (E-3A) — AWACS est", information = "U283.0 — FL300 — orbite du large d'Ashdod au Néguev", linked = "Magic 1 - Escort", coalition = coalition.side.BLUE},
        {sort = 3, name = "Texaco 1", description = "Texaco 1 (KC-135, perche) — canal", information = "TACAN 50Y TX1 — U290.0 — FL220 — piste nord-sud à l'est du Caire", linked = "Texaco 1 - Escort", coalition = coalition.side.BLUE},
        {sort = 4, name = "Arco 1", description = "Arco 1 (KC-135 MPRS, panier) — canal", information = "TACAN 51Y AR1 — U291.0 — FL180 — piste nord-sud près de la nouvelle capitale administrative", linked = "Arco 1 - Escort", coalition = coalition.side.BLUE},
        {sort = 5, name = "Texaco 2", description = "Texaco 2 (KC-135, perche) — Néguev", information = "TACAN 52Y TX2 — U292.0 — FL240 — piste nord-sud au-dessus de la rive ouest de la mer Morte", linked = "Texaco 2 - Escort", coalition = coalition.side.BLUE},
        {sort = 6, name = "Arco 2", description = "Arco 2 (KC-135 MPRS, panier) — Néguev", information = "TACAN 53Y AR2 — U293.0 — FL200 — piste nord-sud au-dessus de Nevatim", linked = "Arco 2 - Escort", coalition = coalition.side.BLUE},
        {sort = 7, name = "CSG-74 Stennis", description = "CVN-74 Stennis — Méditerranée", information = "TACAN 74X STN — ICLS 11 — Link 4 336.0 — ACLS — U305.0", coalition = coalition.side.BLUE},
        {sort = 8, name = "CSG-71 Roosevelt", description = "CVN-71 Roosevelt — mer Rouge", information = "TACAN 71X RSV — ICLS 12 — Link 4 337.0 — ACLS — U306.0", coalition = coalition.side.BLUE},
        {sort = 9, name = "ARG-1 Tarawa", description = "LHA-1 Tarawa — Méditerranée", information = "TACAN 73X TRW — ICLS 13 — U307.0", coalition = coalition.side.BLUE},
        {sort = 10, name = "CSG-74 Stennis S3B-Tanker", description = "S-3B du Stennis (ravitailleur embarqué)", information = "TACAN 56Y S74 — U296.0", coalition = coalition.side.BLUE},
        {sort = 11, name = "CSG-71 Roosevelt S3B-Tanker", description = "S-3B du Roosevelt (ravitailleur embarqué)", information = "TACAN 57Y S71 — U297.0", coalition = coalition.side.BLUE},
        {sort = 12, name = "Darkstar 1", description = "Darkstar 1 (E-3A) — AWACS bleu de l'arène", information = "U285.0 — FL300", coalition = coalition.side.BLUE},
        {sort = 13, name = "Wizard 1", description = "Wizard 1 (A-50) — AWACS rouge", information = "U284.0 — FL300 — orbite est-ouest au nord de St Catherine", linked = "Wizard 1 - Escort", coalition = coalition.side.RED},
        {sort = 14, name = "Shell 1", description = "Shell 1 (IL-78M) — ravitailleur rouge", information = "U294.0 — FL200 — orbite est-ouest au nord de St Catherine", linked = "Shell 1 - Escort", coalition = coalition.side.RED},
        {sort = 15, name = "Focus 1", description = "Focus 1 (A-50) — AWACS rouge de l'arène", information = "U286.0 — FL300", coalition = coalition.side.RED},
        {sort = 16, name = "Reaper 1", description = "Reaper 1 (drone laser) — champ de tir d'attaque", information = "Laser 1511 — FM 35.55. 3 000 m sol au-dessus du champ de tir d'attaque (zone A), au sud-ouest de Cairo West.", jtac = 1511, freq = "35.55", mod = "FM", coalition = coalition.side.BLUE},
        {sort = 17, name = "Reaper 2", description = "Reaper 2 (drone laser) — col de Mitla", information = "Laser 1512 — FM 35.6. 3 000 m sol au-dessus de la ligne du col de Mitla (Z02).", jtac = 1512, freq = "35.6", mod = "FM", coalition = coalition.side.BLUE},
    }
    veafAssets.initialize()
end
end)

veafGuardedInit("MOVE", function()
if veafMove then
    veafMove.initialize()
end
end)

veafGuardedInit("SANCTUARY", function()
if veafSanctuary then
    veafSanctuary.initialize()
    do
        local zone = veafSanctuary.addZoneFromTriggerZone("SANCT-LeCaire")
        if zone then
            zone:setName("Sanctuaire Le Caire")
                :setCoalition(coalition.side.BLUE)
                :setDelayWarning(0)
                :setDelayInstant(60)
                :setProtectFromMissiles(true)
        end
    end
    do
        local zone = veafSanctuary.addZoneFromTriggerZone("SANCT-StCatherine")
        if zone then
            zone:setName("Sanctuaire St Catherine")
                :setCoalition(coalition.side.RED)
                :setDelayWarning(0)
                :setDelayInstant(60)
                :setProtectFromMissiles(true)
        end
    end
end
end)

veafGuardedInit("WEATHER", function()
if veafWeather then
    veafWeather.initialize()
end
end)

veafGuardedInit("REMOTE", function()
if veafRemote then
    veafRemote.initialize()
end
end)

veafGuardedInit("AIRBASES", function()
if veafAirbases then
    veafAirbases.initialize()
end
end)

-- ── Infrastructure ──

veafGuardedInit("MARKERS", function()
if veafMarkers then
    veafMarkers.initialize()
end
end)

veafGuardedInit("TIME", function()
if veafTime then
    veafTime.initialize()
end
end)

veafGuardedInit("UNITS", function()
if veafUnits then
    veafUnits.initialize()
end
end)

veafGuardedInit("CACHE", function()
if veafCacheManager then
    veafCacheManager.initialize()
end
end)

veafGuardedInit("EVENTS", function()
if veafEventHandler then
    veafEventHandler.initialize()
end
end)

-- ── Core ──

veafGuardedInit("GROUNDAI", function()
if veafGroundAI then
    veafGroundAI.initialize()
end
end)

-- ── Infrastructure ──

veafGuardedInit("COMMANDS", function()
if veafCommands then
    veafCommands.initialize()
end
end)

-- ── Features ──

veafGuardedInit("INTERPRETER", function()
if veafInterpreter then
    veafInterpreter.initialize()
end
end)

-- ── Community scripts disabled (VEAF leaves their globals alone) ──────────────
veaf.setConfig("tum", "enable", false)

-- ── Skynet-IADS ──────────────────────────────────────────────────────────────
veafGuardedInit("SKYNET", function()
if veafSkynet then
    veafSkynet.SpotterNetwork = true
    veafSkynet.SpotterView = "off"
    veafSkynet.initialize(false, false, false, false)
end
end)

-- ── CSAR configuration ───────────────────────────────────────────────────────
-- Note: CSAR.lua must be loaded by mission-script.lua before this block.
veafGuardedInit("CSAR", function()
if csar then
    csar.initialize()
end
end)
