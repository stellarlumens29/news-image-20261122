#!/usr/bin/env python3
"""Verify map pins in main.py: every pair of pin centres >= 15 px apart."""
import importlib.util
import math

spec = importlib.util.spec_from_file_location("entry", "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

pts = {}
for num, _h, _o, lon, lat, _r in m.STORIES:
    x, y = m.lonlat_to_xy(lon, lat)
    dx, dy = m.PIN_DXDY.get(num, (0, 0))
    pts[num] = (x + dx, y + dy)

bad = []
nums = sorted(pts)
for i, a in enumerate(nums):
    for b in nums[i + 1:]:
        d = math.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1])
        if d < 15:
            bad.append((a, b, round(d, 1)))

# Also check pins stay inside the map frame (radius 7).
out = [n for n, (x, y) in pts.items()
       if x - 7 < m.MAP_X or x + 7 > m.MAP_X + m.MAP_W
       or y - 7 < m.MAP_Y or y + 7 > m.MAP_Y + m.MAP_H]

print("stories:", len(pts))
print("pairs < 15px:", bad if bad else "NONE")
print("pins outside map:", out if out else "NONE")
print("region counts:", {r: sum(1 for s in m.STORIES if s[5] == r)
                         for r in ["EUROPE", "ASIA", "MIDDLE EAST",
                                   "AFRICA", "AMERICAS", "OCEANIA", "GLOBAL"]})
