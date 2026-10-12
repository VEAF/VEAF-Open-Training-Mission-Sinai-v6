"""Sonde DCS (mission de test en cours, dcs-serve) : imbrication des niveaux d'entraînement et convois qui roulent.

python probe_zones.py [niveaux] [convois]   (sans argument : les deux)

Niveaux : pour chaque famille (H, A, S), active le facile, puis le moyen, puis le difficile, un à la fois, et compte
les unités et statiques rouges vivants dans son cercle (recherche élargie à 1,5 rayon, pour voir ce qui déborde), avec la distance la plus grande au centre ; désactive avant le niveau suivant. Attendu : chaque niveau
fait apparaître plus que celui qu'il inclut, et tout tient dans le cercle.
Convois : active les trois zones de convoi, relève la position du premier véhicule de chaque convoi trois fois à
une minute d'intervalle, puis les désactive. Attendu : chacun a roulé.
"""
import sys
import time

from probe_scenery import exec_lua

FAMILIES = ["combatZone_Arad", "combatZone_DesertGizeh", "combatZone_DesertOuest"]
CONVOYS = ["combatZone_ConvoiElArish", "combatZone_ConvoiNakhl", "combatZone_ConvoiFeiran"]

COUNT = """local z = veafCombatZone.GetZone("%s")
if not z then return "r=absente" end
local tz = trigger.misc.getZone("%s")
local c = {x = tz.point.x, z = tz.point.z}
local n = {[Object.Category.UNIT] = 0, [Object.Category.STATIC] = 0}
local far = 0
for _, cat in ipairs({Object.Category.UNIT, Object.Category.STATIC}) do
  world.searchObjects(cat, {id = world.VolumeType.SPHERE, params = {point = {x = c.x, y = land.getHeight({x = c.x, y = c.z}), z = c.z}, radius = tz.radius * 1.5}},
    function(o)
      if o:isExist() and o:getLife() >= 1 and o:getCoalition() == coalition.side.RED then
        local p = o:getPoint()
        local d = math.sqrt((p.x - c.x) ^ 2 + (p.z - c.z) ^ 2)
        n[cat] = n[cat] + 1
        far = math.max(far, d)
      end
      return true
    end)
end
return "r=" .. tostring(z:isActive()) .. ":" .. n[Object.Category.UNIT] .. ":" .. n[Object.Category.STATIC] .. ":" .. math.floor(far) .. ":" .. math.floor(tz.radius)"""

LEAD = """local out = {}
for _, zn in ipairs(%s) do
  local z = veafCombatZone.GetZone(zn)
  local s = "aucun"
  for _, gn in ipairs((z and z:getSpawnedGroups()) or {}) do
    local g = Group.getByName(gn)
    if g and g:isExist() and g:getSize() > 0 then
      local u = g:getUnit(1)
      local p = u:getPoint()
      local v = u:getVelocity()
      s = gn .. "@" .. math.floor(p.x) .. "," .. math.floor(p.z) .. "@" .. string.format("%%.1f", math.sqrt(v.x ^ 2 + v.z ^ 2)) .. "m/s"
      break
    end
  end
  out[#out + 1] = zn .. "=" .. s
end
return "r=" .. table.concat(out, ";")"""


def lua(code):
    return exec_lua(code).split("r=", 1)[1]


def act(zone, on=True):
    lua(f'veafCombatZone.{"ActivateZone" if on else "DesactivateZone"}("{zone}", true) return "r=ok"')


def levels():
    for fam in FAMILIES:
        prev = None
        for lvl in ("Easy", "Medium", "Hard"):
            z = f"{fam}_{lvl}"
            act(z)
            time.sleep(12)
            active, units, statics, far, radius = lua(COUNT % (z, z)).split(":")
            total = int(units) + int(statics)
            trend = "" if prev is None else (" plus que le niveau inclus" if total > prev else " PAS PLUS que le niveau inclus")
            print(f"{z:32} actif={active:5} unités {units:>3}  statiques {statics:>2}  le plus loin {far:>5} m / rayon {radius} m"
                  f"{' HORS DU CERCLE' if int(far) > int(radius) else ''}{trend}")
            prev = total
            act(z, False)
            time.sleep(6)
            left = lua(COUNT % (z, z)).split(":")
            if int(left[1]) + int(left[2]):
                print(f"{'':32} après désactivation : encore {left[1]} unités et {left[2]} statiques dans le cercle")


def convoys():
    for z in CONVOYS:
        act(z)
    time.sleep(15)
    first = None
    for k in range(3):
        snap = dict(kv.split("=", 1) for kv in lua(LEAD % ("{" + ",".join(f'"{z}"' for z in CONVOYS) + "}")).split(";"))
        print(f"t+{15 + 60 * k:>3} s : " + " | ".join(f"{z.replace('combatZone_', '')} {v.split('@', 1)[-1]}" for z, v in snap.items()))
        if first is None:
            first = snap
        if k < 2:
            time.sleep(60)
    for z in CONVOYS:
        a, b = first[z], snap[z]
        if "@" not in a or "@" not in b:
            print(f"{z}: pas de véhicule relevé")
            continue
        (x0, y0), (x1, y1) = (map(int, a.split("@")[1].split(",")), map(int, b.split("@")[1].split(",")))
        d = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        print(f"{z}: {d:.0f} m en 120 s" + (" — IMMOBILE" if d < 50 else ""))
    for z in CONVOYS:
        act(z, False)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    what = sys.argv[1:] or ["niveaux", "convois"]
    if "niveaux" in what:
        levels()
    if "convois" in what:
        convoys()
