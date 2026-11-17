"""Build the Exeter & Topsham family map from data/exeter-topsham-places.json.

    python3 scripts/build_exeter_map.py

Writes, every run (safe to re-run):
  site   content/maps/exeter-topsham.html          interactive Leaflet map (public places only)
         content/images/Exeter-Topsham-map.jpg, Topsham-map.jpg   static numbered maps (public only)
         content/Places/Exeter-and-Topsham-Map.md  the site page: map + numbered table
  vault  attachments/Exeter and Topsham family map.jpg, Topsham family map.jpg   (all places)
         Exeter and Topsham Family Map.md          the vault note: map + table + how to update
and adds a link to the map on every site page and vault note named in the data
(only if the link isn't there already).

Map tiles: OpenStreetMap standard tiles, cached in ~/.cache/silver-map-tiles.
Then commit + push the site repo, and commit the vault.
"""
import json
import math
import os
import re
import sys
import time
import urllib.request

from PIL import Image, ImageDraw, ImageFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT = "/Users/jagosilver/whoami-vault"
DATA = os.path.join(SITE, "data", "exeter-topsham-places.json")
CACHE = os.path.expanduser("~/.cache/silver-map-tiles")
SITE_PAGE = "Places/Exeter-and-Topsham-Map"
VAULT_NOTE = "Exeter and Topsham Family Map"
LIVE_URL = "https://jagosilver.github.io/silver-family-archive/" + SITE_PAGE
ZOOM = 14
UA = "silver-family-archive-map-builder/1.0 (personal family history site)"

sys.path.insert(0, os.path.join(SITE, "scripts"))
from site_layout import site_path  # noqa: E402

places = json.load(open(DATA))["places"]
public = [p for p in places if p.get("public", True)]


# ---------------------------------------------------------------- static map
def deg2px(lat, lon, z):
    n = 256 * 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def tile(z, x, y):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"{z}_{x}_{y}.png")
    if not os.path.exists(f):
        req = urllib.request.Request(f"https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                                     headers={"User-Agent": UA})
        open(f, "wb").write(urllib.request.urlopen(req, timeout=30).read())
        time.sleep(0.3)
    return Image.open(f).convert("RGB")


def static_map(pts, out, numbers, ZOOM=ZOOM):
    xs, ys = zip(*[deg2px(p["lat"], p["lon"], ZOOM) for p in pts])
    pad = 90
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    tx0, tx1, ty0, ty1 = int(x0 // 256), int(x1 // 256), int(y0 // 256), int(y1 // 256)
    big = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            big.paste(tile(ZOOM, tx, ty), ((tx - tx0) * 256, (ty - ty0) * 256))
    ox, oy = tx0 * 256, ty0 * 256
    im = big.crop((int(x0 - ox), int(y0 - oy), int(x1 - ox), int(y1 - oy)))
    scale = 2  # draw at 2x for crisp markers
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
    small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    for p, num in zip(pts, numbers):
        x, y = deg2px(p["lat"], p["lon"], ZOOM)
        x, y = (x - x0) * scale, (y - y0) * scale
        r = 22
        if p.get("approx"):
            d.ellipse((x - r, y - r, x + r, y + r), fill="white", outline="#8a2b0e", width=5)
            col = "#8a2b0e"
        else:
            d.ellipse((x - r, y - r, x + r, y + r), fill="#8a2b0e", outline="white", width=4)
            col = "white"
        d.text((x, y), str(num), fill=col, font=font, anchor="mm")
    # credit
    txt = "Map data © OpenStreetMap contributors"
    d.text((im.width - 12, im.height - 12), txt, fill="#333", font=small, anchor="rd",
           stroke_width=3, stroke_fill="white")
    im = im.resize((im.width // 2 * 3 // 2, im.height // 2 * 3 // 2), Image.LANCZOS)
    im.convert("RGB").save(out, quality=82, optimize=True)


def maps_pair(pts, nums, overview, closeup):
    """Overview of everything at z14, plus a z16 close-up of the Topsham places."""
    static_map(pts, overview, nums)
    tp = [(p, n) for p, n in zip(pts, nums) if p["lat"] < 50.692 and p["lon"] > -3.48]
    if tp:
        static_map([p for p, _ in tp], closeup, [n for _, n in tp], ZOOM=16)


# ---------------------------------------------------------------- site
def find_site_page(base):
    """Resolve a link slug (folder hub, moved page or bare file name) to its .md file."""
    for f in (os.path.join(SITE, "content", base, "index.md"),
              os.path.join(SITE, "content", base + ".md"),
              site_path(SITE, base)):
        if os.path.exists(f):
            return f
    name = os.path.basename(base) + ".md"
    for root, _, fs in os.walk(os.path.join(SITE, "content")):
        if name in fs:
            return os.path.join(root, name)
    return None


def site_href(slug, from_dir=True):
    return slug


def build_site():
    nums = list(range(1, len(public) + 1))
    maps_pair(public, nums, os.path.join(SITE, "content/images/Exeter-Topsham-map.jpg"),
              os.path.join(SITE, "content/images/Topsham-map.jpg"))

    feats = []
    for n, p in zip(nums, public):
        links = " · ".join(f'<a href="../{s}" target="_top">{t}</a>' for t, s in p["site"])
        feats.append({"n": n, "lat": p["lat"], "lon": p["lon"], "approx": bool(p.get("approx")),
                      "name": p["name"], "area": p["area"], "years": p["years"],
                      "text": p["public_text"], "links": links})
    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Exeter and Topsham family map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>html,body,#map{height:100%;margin:0;font-family:Georgia,serif}
.num{background:#8a2b0e;color:#fff;border:2px solid #fff;border-radius:50%;width:26px;height:26px;line-height:24px;text-align:center;font:bold 13px Helvetica,Arial,sans-serif;box-shadow:0 1px 3px rgba(0,0,0,.5)}
.num.approx{background:#fff;color:#8a2b0e;border-color:#8a2b0e}
.leaflet-popup-content{font-size:14px;line-height:1.4}.leaflet-popup-content h3{margin:0 0 4px;font-size:15px}
.leaflet-popup-content .when{color:#666;font-size:12px;margin-bottom:6px}.leaflet-popup-content a{color:#8a2b0e}</style>
</head><body><div id="map"></div><script>
const places = """ + json.dumps(feats, ensure_ascii=False) + """;
const map = L.map('map', {scrollWheelZoom: false});
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'}).addTo(map);
const b = [];
for (const p of places) {
  const icon = L.divIcon({className: '', html: '<div class="num' + (p.approx ? ' approx' : '') + '">' + p.n + '</div>', iconSize: [30, 30], iconAnchor: [15, 15]});
  L.marker([p.lat, p.lon], {icon, title: p.name}).addTo(map).bindPopup(
    '<h3>' + p.n + '. ' + p.name + '</h3><div class="when">' + p.area + ' · ' + p.years + (p.approx ? ' · position approximate' : '') + '</div>' +
    p.text + (p.links ? '<br><br>' + p.links : ''));
  b.push([p.lat, p.lon]);
}
map.fitBounds(b, {padding: [30, 30]});
</script></body></html>
"""
    os.makedirs(os.path.join(SITE, "content/maps"), exist_ok=True)
    open(os.path.join(SITE, "content/maps/exeter-topsham.html"), "w").write(html)

    rows = []
    for n, p in zip(nums, public):
        links = ", ".join(f"[{t}]({s})" for t, s in p["site"])
        name = p["name"] + (" *(approx.)*" if p.get("approx") else "")
        rows.append(f"| {n} | **{name}**, {p['area']} | {p['years']} | {p['public_text']} | {links} |")
    md = f"""---
title: "Exeter and Topsham map"
description: "A map of the places in Exeter, Countess Wear and Topsham that appear in the Silver Family Archive: the family homes, Clifford's surgery, the Acotts' Mona Lodge, Anthea Leigh's Topsham childhood and more."
tags:
  - places
  - family
---

*← [Places & history](Places/) · [Silver Family Archive](./)*

Every place in Exeter and Topsham that appears in these pages, from the Acotts' Mona Lodge and the Silvers' Tresillian to Anthea Leigh's childhood homes by the Exe. Click a numbered marker for the story and the pages about it. A hollow marker means the position is approximate. The map is rebuilt whenever new places turn up in the archive.

<iframe src="../maps/exeter-topsham.html" title="Interactive map of family places in Exeter and Topsham" style="width:100%;height:600px;border:1px solid #ccc;border-radius:6px" loading="lazy"></iframe>

*[Open the map full screen](../maps/exeter-topsham.html)*

## The places

| # | Place | When | What happened | Pages |
| --- | --- | --- | --- | --- |
""" + "\n".join(rows) + """

![Static map of the same places, numbered as in the table above.](../images/Exeter-Topsham-map.jpg)\n\n![Close-up of the Topsham places.](../images/Topsham-map.jpg)

*Map data © OpenStreetMap contributors. Positions are street-level only.*
"""
    open(os.path.join(SITE, "content", SITE_PAGE + ".md"), "w").write(md)

    # link from every page named in the data
    line = "*Places on this page are on the [Exeter and Topsham map](Places/Exeter-and-Topsham-Map).*"
    targets = sorted({s.split("#")[0].rstrip("/") for p in public for _, s in p["site"]})
    for base in targets:
        f = find_site_page(base)
        if not f:
            print("  ! site page not found:", base)
            continue
        s = open(f).read()
        if "Exeter-and-Topsham-Map" in s:
            continue
        lines = s.split("\n")
        for i, l in enumerate(lines):
            if l.startswith("*←"):
                lines[i + 1:i + 1] = ["", line]
                break
        else:
            print("  ! no breadcrumb, not linked:", f)
            continue
        open(f, "w").write("\n".join(lines))
        print("  linked", os.path.relpath(f, SITE))


# ---------------------------------------------------------------- vault
def build_vault():
    nums = list(range(1, len(places) + 1))
    maps_pair(places, nums, os.path.join(VAULT, "attachments", "Exeter and Topsham family map.jpg"),
              os.path.join(VAULT, "attachments", "Topsham family map.jpg"))
    rows = []
    for n, p in zip(nums, places):
        links = " · ".join(f"[[{v}]]" for v in p["vault"])
        flag = []
        if p.get("approx"):
            flag.append("approx.")
        if not p.get("public", True):
            flag.append("vault only")
        name = p["name"] + (f" *({', '.join(flag)})*" if flag else "")
        txt = p["vault_text"].replace("|", "\\|")
        rows.append(f"| {n} | **{name}**, {p['area']} | {p['years']} | {txt} | {links} |")
    md = f"""---
tags:
 - Places
 - Family
 - Maps
---
Map of every Exeter, Countess Wear and Topsham place in the Silver, Acott, Leigh and Pyne family pages. Numbers match the table. Hollow markers are approximate positions. The public, interactive version (public places only, no house numbers) is on the archive site: [Exeter and Topsham map]({LIVE_URL}).

![[Exeter and Topsham family map.jpg]]\n\n**Topsham close-up**\n\n![[Topsham family map.jpg]]

## Places

| # | Place | When | What happened | Notes |
|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## How to update

The map is generated. Don't edit this note or the image by hand: add or change the place in `data/exeter-topsham-places.json` in the site repo (`christopher-silver`), then run `python3 scripts/build_exeter_map.py`. That rebuilds this note, the image, the site page and the interactive map, and links the map from every note listed for a place. Set `"public": false` for anything that should stay off the public site, and `"approx": true` when the exact spot isn't known.

## See also

- [[Exeter]]
- [[Topsham]]
- [[Tresillian, Exeter]]
- [[Acott Family]]
"""
    open(os.path.join(VAULT, VAULT_NOTE + ".md"), "w").write(md)

    link = f"- [[{VAULT_NOTE}]]"
    targets = sorted({v for p in places for v in p["vault"]} | {"Exeter", "Topsham"})
    for name in targets:
        f = os.path.join(VAULT, name + ".md")
        if not os.path.exists(f):
            print("  ! vault note not found:", name)
            continue
        s = open(f).read()
        if f"[[{VAULT_NOTE}" in s:
            continue
        if "\n## See also" in s:
            s = re.sub(r"(\n## See also[^\n]*\n)(\n?)", lambda m: m.group(1) + m.group(2) + link + "\n", s, count=1)
        else:
            s = s.rstrip() + "\n\n## See also\n\n" + link + "\n"
        open(f, "w").write(s)
        print("  linked vault:", name)


if __name__ == "__main__":
    print("site…")
    build_site()
    print("vault…")
    build_vault()
    print("done:", len(public), "public places,", len(places), "in vault")
