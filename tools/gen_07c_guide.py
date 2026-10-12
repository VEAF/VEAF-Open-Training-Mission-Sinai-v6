"""Écrit le guide touristique des pyramides dans src/scripts/mission-script.lua (bloc entre deux marqueurs, réécrit
à chaque passage : ce script se rejoue sans doublon).

Toutes les 2 s, le guide regarde les appareils des joueurs des deux camps ; quand l'un passe à moins de 1 500 ft
sol et à moins du rayon d'un monument, son groupe reçoit le texte du monument (une fois par appareil et par
monument, puis à nouveau après 10 min). Positions : tools/places.json (geocode OSM) et lib.py (Sphinx).
Textes : connaissances générales, chiffres arrondis (source : articles Wikipédia en français de chaque
monument) — à relire.
Les rayons de Gizeh restent sous la moitié de l'écart entre deux monuments (Khéops–Khéphren 490 m) : un seul
message à la fois.
"""
from lib import M, PLACES

P = PLACES
MONUMENTS = [
    # clé de lieu, rayon (m), texte
    ("Great Pyramid of Giza", 240,
     "Pyramide de Khéops, la Grande Pyramide. Tombeau du pharaon Khéops (IVe dynastie, vers 2560 av. J.-C.). "
     "146 m à l'origine, environ 138 m aujourd'hui : le plus haut monument bâti par l'homme pendant près de "
     "4 000 ans, et la seule des Sept Merveilles du monde antique encore debout."),
    ("Pyramid of Khafre", 240,
     "Pyramide de Khéphren, fils de Khéops. 143 m à l'origine : un peu moins haute que sa voisine, elle paraît "
     "plus grande parce qu'elle est bâtie sur un terrain plus élevé. Son sommet garde une partie du revêtement de "
     "calcaire blanc qui couvrait toutes les pyramides."),
    ("Pyramid of Menkaure", 200,
     "Pyramide de Mykérinos, la plus petite des trois grandes pyramides de Gizeh (environ 65 m à l'origine). Sa "
     "base était revêtue de granit rouge venu d'Assouan, à plus de 800 km au sud."),
    ("Great Sphinx of Giza", 200,
     "Le Grand Sphinx : un lion à tête humaine taillé dans le calcaire du plateau, environ 73 m de long et 20 m de "
     "haut. On l'attribue généralement à Khéphren, dont il garde la chaussée."),
    ("Pyramid of Djoser", 600,
     "Saqqarah, pyramide à degrés de Djoser (IIIe dynastie, vers 2650 av. J.-C.), œuvre de l'architecte Imhotep. "
     "La première pyramide d'Égypte : six mastabas empilés, environ 62 m."),
    ("Red Pyramid", 600,
     "Dahchour, pyramide rouge de Snéfrou, père de Khéops : la première pyramide réussie à faces lisses, environ "
     "105 m. Sa teinte vient du calcaire rougeâtre mis à nu quand son revêtement a disparu."),
    ("Bent Pyramid", 600,
     "Dahchour, pyramide rhomboïdale de Snéfrou : sa pente passe d'environ 54° à 43° à mi-hauteur, sans doute "
     "pour éviter l'effondrement. Environ 101 m ; elle garde une grande partie de son revêtement d'origine."),
    ("Meidum pyramid", 800,
     "Meïdoum, la pyramide effondrée : commencée pour Houni et achevée sous Snéfrou, elle a perdu son revêtement, "
     "et il n'en reste qu'un noyau en forme de tour, environ 65 m au-dessus d'un champ de gravats."),
]

BEGIN = "-- >>> guide touristique des pyramides (écrit par tools/gen_07c_guide.py, ne pas éditer à la main)"
END = "-- <<< guide touristique des pyramides"


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def block():
    rows = []
    for key, r, text in MONUMENTS:
        x, y = P[key]
        rows.append(f"    {{ x = {x}, z = {y}, r = {r}, text = {lua_str(text)} }},")
    return "\n".join([
        BEGIN,
        "do",
        "  veafTourGuide = { seen = {} }",
        "  veafTourGuide.monuments = {",
        *rows,
        "  }",
        "  veafTourGuide.maxAgl = 457      -- 1 500 ft",
        "  veafTourGuide.repeatAfter = 600 -- s",
        "  function veafTourGuide.check()",
        "    local now = timer.getTime()",
        "    for _, side in pairs({ coalition.side.BLUE, coalition.side.RED }) do",
        "      for _, unit in pairs(coalition.getPlayers(side) or {}) do",
        "        if unit and unit:isExist() and unit:inAir() then",
        "          local p = unit:getPoint()",
        "          local agl = p.y - land.getHeight({ x = p.x, y = p.z })",
        "          if agl < veafTourGuide.maxAgl then",
        "            for i, m in ipairs(veafTourGuide.monuments) do",
        "              local dx, dz = p.x - m.x, p.z - m.z",
        "              if dx * dx + dz * dz < m.r * m.r then",
        "                local key = unit:getName() .. '#' .. i",
        "                local last = veafTourGuide.seen[key]",
        "                if not last or now - last > veafTourGuide.repeatAfter then",
        "                  veafTourGuide.seen[key] = now",
        "                  trigger.action.outTextForGroup(unit:getGroup():getID(), m.text, 25)",
        "                end",
        "              end",
        "            end",
        "          end",
        "        end",
        "      end",
        "    end",
        "    return now + 2",
        "  end",
        "  timer.scheduleFunction(function(_, t) local ok, nxt = pcall(veafTourGuide.check) "
        "if ok then return nxt end env.error('veafTourGuide: ' .. tostring(nxt)) return t + 10 end, nil, "
        "timer.getTime() + 10)",
        "end",
        END,
    ])


if __name__ == "__main__":
    path = f"{M}/src/scripts/mission-script.lua"
    t = open(path, encoding="utf-8").read()
    if BEGIN in t:
        t = t[:t.index(BEGIN)] + t[t.index(END) + len(END):].lstrip("\n")
    t = t.rstrip("\n") + "\n\n" + block() + "\n"
    open(path, "w", encoding="utf-8").write(t)
    print(len(MONUMENTS), "monuments écrits dans", path)
