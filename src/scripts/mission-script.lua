-- mission-script.lua
-- Mission-specific Lua code that cannot be generated from mission.yaml.
--
-- This file is loaded AFTER veaf-config.lua (which is generated automatically
-- from mission.yaml by the veaf-tools build command).
--
-- Put here:
--   - Custom shortcuts / aliases  (VeafAlias:new():...)
--   - Custom Lua helper functions
--   - Third-party script setup (CTLD, CSAR, …) that requires Lua code
--
-- Do NOT put here:
--   - Module initialization calls  → use mission.yaml (modules:)
--   - Mission identity             → use mission.yaml (mission:)
--   - QRA definitions              → use mission.yaml (modules.QRA)
--   - Combat/CAP missions          → use mission.yaml (combat_missions: / cap_missions:)
--   - Assets lists                 → use mission.yaml (modules.ASSETS.assets)

-- >>> guide touristique des pyramides (écrit par tools/gen_07c_guide.py, ne pas éditer à la main)
do
  veafTourGuide = { seen = {} }
  veafTourGuide.monuments = {
    { x = -7372, z = -10782, r = 240, text = "Pyramide de Khéops, la Grande Pyramide. Tombeau du pharaon Khéops (IVe dynastie, vers 2560 av. J.-C.). 146 m à l'origine, environ 138 m aujourd'hui : le plus haut monument bâti par l'homme pendant près de 4 000 ans, et la seule des Sept Merveilles du monde antique encore debout." },
    { x = -7718, z = -11124, r = 240, text = "Pyramide de Khéphren, fils de Khéops. 143 m à l'origine : un peu moins haute que sa voisine, elle paraît plus grande parce qu'elle est bâtie sur un terrain plus élevé. Son sommet garde une partie du revêtement de calcaire blanc qui couvrait toutes les pyramides." },
    { x = -8095, z = -11369, r = 200, text = "Pyramide de Mykérinos, la plus petite des trois grandes pyramides de Gizeh (environ 65 m à l'origine). Sa base était revêtue de granit rouge venu d'Assouan, à plus de 800 km au sud." },
    { x = -7805, z = -10463, r = 200, text = "Le Grand Sphinx : un lion à tête humaine taillé dans le calcaire du plateau, environ 73 m de long et 20 m de haut. On l'attribue généralement à Khéphren, dont il garde la chaussée." },
    { x = -19464, z = -3022, r = 600, text = "Saqqarah, pyramide à degrés de Djoser (IIIe dynastie, vers 2650 av. J.-C.), œuvre de l'architecte Imhotep. La première pyramide d'Égypte : six mastabas empilés, environ 62 m." },
    { x = -26392, z = -4127, r = 600, text = "Dahchour, pyramide rouge de Snéfrou, père de Khéops : la première pyramide réussie à faces lisses, environ 105 m. Sa teinte vient du calcaire rougeâtre mis à nu quand son revêtement a disparu." },
    { x = -28427, z = -3847, r = 600, text = "Dahchour, pyramide rhomboïdale de Snéfrou : sa pente passe d'environ 54° à 43° à mi-hauteur, sans doute pour éviter l'effondrement. Environ 101 m ; elle garde une grande partie de son revêtement d'origine." },
    { x = -72886, z = -9615, r = 800, text = "Meïdoum, la pyramide effondrée : commencée pour Houni et achevée sous Snéfrou, elle a perdu son revêtement, et il n'en reste qu'un noyau en forme de tour, environ 65 m au-dessus d'un champ de gravats." },
  }
  veafTourGuide.maxAgl = 457      -- 1 500 ft
  veafTourGuide.repeatAfter = 600 -- s
  function veafTourGuide.check()
    local now = timer.getTime()
    for _, side in pairs({ coalition.side.BLUE, coalition.side.RED }) do
      for _, unit in pairs(coalition.getPlayers(side) or {}) do
        if unit and unit:isExist() and unit:inAir() then
          local p = unit:getPoint()
          local agl = p.y - land.getHeight({ x = p.x, y = p.z })
          if agl < veafTourGuide.maxAgl then
            for i, m in ipairs(veafTourGuide.monuments) do
              local dx, dz = p.x - m.x, p.z - m.z
              if dx * dx + dz * dz < m.r * m.r then
                local key = unit:getName() .. '#' .. i
                local last = veafTourGuide.seen[key]
                if not last or now - last > veafTourGuide.repeatAfter then
                  veafTourGuide.seen[key] = now
                  trigger.action.outTextForGroup(unit:getGroup():getID(), m.text, 25)
                end
              end
            end
          end
        end
      end
    end
    return now + 2
  end
  timer.scheduleFunction(function(_, t) local ok, nxt = pcall(veafTourGuide.check) if ok then return nxt end env.error('veafTourGuide: ' .. tostring(nxt)) return t + 10 end, nil, timer.getTime() + 10)
end
-- <<< guide touristique des pyramides
