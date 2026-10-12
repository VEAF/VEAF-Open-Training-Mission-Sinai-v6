"""Sonde DCS (mission en cours, dcs-serve) : type de sol et place libre à chaque point demandé.

python probe_points.py x,y [x,y ...]  ou importé : probe([(x, y), ...]) -> ["land:clear", "water:-", ...]
Type de sol DCS (land.getSurfaceType) : 1 terre, 2 eau peu profonde, 3 eau, 4 route, 5 piste.
« clear » : une place libre de 5 m à moins de 20 m (Disposition.getSimpleZones, la petite requête fiable).
"""
import sys

from probe_scenery import exec_lua

NAMES = {1: "land", 2: "shallow", 3: "water", 4: "road", 5: "runway"}
LUA = """local pts = %s
local out = {}
for i, q in ipairs(pts) do
  local s = land.getSurfaceType({x = q[1], y = q[2]})
  local p = {x = q[1], y = land.getHeight({x = q[1], y = q[2]}), z = q[2]}
  local ok, c = pcall(Disposition.getSimpleZones, p, 20, 5, 10)
  out[#out + 1] = i .. "=" .. s .. ":" .. ((ok and type(c) == "table" and #c > 0) and "clear" or "blocked") .. ":" .. math.floor(p.y)
end
return table.concat(out, ";")"""


def probe(points):
    res = []
    for i in range(0, len(points), 80):
        part = points[i:i + 80]
        code = LUA % ("{" + ",".join("{%d,%d}" % (round(x), round(y)) for x, y in part) + "}")
        ans = dict(kv.split("=") for kv in exec_lua(code).split(";"))
        for k in range(1, len(part) + 1):
            s, c, h = ans[str(k)].split(":")
            res.append(f"{NAMES.get(int(s), s)}:{c}:{h}m")
    return res


if __name__ == "__main__":
    pts = [tuple(float(v) for v in a.split(",")) for a in sys.argv[1:]]
    for p, r in zip(pts, probe(pts)):
        print(p, r)
