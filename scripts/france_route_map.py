"""Draw content/images/France-1951-route.svg: David Silver's motorbike tour, c. summer 1951.

Route from his three letters (see David-Silver/France-Letters.md). Base map from
Natural Earth 10m land, rivers and land borders (public domain); pass the folder
holding the three .geojson files as the first argument.
"""
import json, math, os, sys

NE = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), "..", "content", "images", "France-1951-route.svg")

W, H = 1000, 900
LON0, LON1, LAT0, LAT1 = -3.75, 4.35, 46.7, 51.35
KX = math.cos(math.radians(49.2))
SCALE = (W - 40) / ((LON1 - LON0) * KX)


def xy(lon, lat):
    return 20 + (lon - LON0) * KX * SCALE, 20 + (LAT1 - lat) * SCALE


def path(coords, closed):
    out, last = [], None
    for lon, lat in coords:
        lon = min(max(lon, LON0 - 0.3), LON1 + 0.3)
        lat = min(max(lat, LAT0 - 0.3), LAT1 + 0.3)
        x, y = xy(lon, lat)
        if last and abs(x - last[0]) < 0.7 and abs(y - last[1]) < 0.7:
            continue
        out.append("%.1f,%.1f" % (x, y)); last = (x, y)
    if len(out) < 2:
        return ""
    return "M" + "L".join(out) + ("Z" if closed else "")


def inbox(coords):
    return any(LON0 - 1 < c[0] < LON1 + 1 and LAT0 - 1 < c[1] < LAT1 + 1 for c in coords)


def geoms(fn, keep=lambda p: True):
    for f in json.load(open(os.path.join(NE, fn)))["features"]:
        if not keep(f["properties"]):
            continue
        g = f["geometry"]
        parts = {"Polygon": [g["coordinates"]], "MultiPolygon": g["coordinates"],
                 "LineString": [[g["coordinates"]]], "MultiLineString": [[l] for l in g["coordinates"]]}[g["type"]]
        for poly in parts:
            for ring in poly:
                if inbox(ring):
                    yield ring


land = "".join(path(r, True) for r in geoms("ne_10m_land.geojson"))
rivers = [path(r, False) for r in geoms("ne_10m_rivers_lake_centerlines.geojson",
          lambda p: p.get("name") in ("Loire", "Seine", "Somme", "Cher", "Eure", "Thames", "Exe"))]
borders = [path(r, False) for r in geoms("ne_10m_admin_0_boundary_lines_land.geojson")]

P = {  # name: (lon, lat)
    "Exeter": (-3.534, 50.718), "Fenny Bridges": (-3.253, 50.766), "Honiton": (-3.189, 50.799),
    "Dorchester": (-2.437, 50.715), "Ringwood": (-1.790, 50.846), "Romsey": (-1.499, 50.989),
    "Portsmouth": (-1.070, 50.845), "Chichester": (-0.779, 50.837), "Arundel": (-0.554, 50.855),
    "Lancing": (-0.323, 50.828), "Shoreham": (-0.274, 50.832), "Brighton": (-0.137, 50.823),
    "Rottingdean": (-0.057, 50.810), "Lewes": (0.009, 50.873), "Hastings": (0.573, 50.855),
    "Winchelsea": (0.709, 50.925), "Rye": (0.733, 50.950), "Hythe": (1.084, 51.071),
    "Sandgate": (1.153, 51.074), "Dover": (1.313, 51.128), "Calais": (1.859, 50.951),
    "Boulogne": (1.615, 50.726), "Samer": (1.745, 50.639), "Amiens": (2.296, 49.894),
    "Paris": (2.295, 48.874), "Porte d'Italie": (2.360, 48.819), "Bourges": (2.399, 47.081),
    "Blois": (1.336, 47.586), "Chartres": (1.489, 48.444), "Dreux": (1.366, 48.737),
    "Evreux": (1.151, 49.027),
}
OUTWARD = ["Exeter", "Fenny Bridges", "Honiton", "Dorchester", "Ringwood", "Romsey", "Portsmouth",
           "Chichester", "Arundel", "Lancing", "Shoreham", "Brighton", "Rottingdean", "Lewes",
           "Hastings", "Winchelsea", "Rye", "Hythe", "Sandgate", "Dover"]
FRANCE = ["Calais", "Boulogne", "Samer", "Boulogne", "Amiens", "Paris", "Porte d'Italie", "Bourges", "Blois"]
RETURN = ["Blois", "Chartres", "Dreux", "Evreux", "Amiens", "Boulogne"]

# overnight stops: name -> (label, dx, dy, anchor)
NIGHTS = {
    "Romsey": ("Romsey · Sun night", 0, -14, "middle"),
    "Sandgate": ("Sandgate · Mon night", -10, -12, "end"),
    "Boulogne": ("Boulogne · Tue night", 14, 2, "start"),
    "Amiens": ("Amiens · Wed night", 12, 4, "start"),
    "Paris": ("Paris · Thu night", -12, 4, "end"),
    "Bourges": ("Bourges · Fri", 12, 5, "start"),
    "Blois": ("Blois · Sat–Sun nights", -12, 5, "end"),
}
LABELS = {  # minor places: (dx, dy, anchor)
    "Exeter": (0, 20, "middle"), "Dorchester": (0, 18, "middle"), "Chichester": (0, 18, "middle"),
    "Brighton": (0, 18, "middle"), "Lewes": (0, -10, "middle"), "Hastings": (0, -10, "middle"),
    "Dover": (0, -12, "middle"), "Calais": (10, 4, "start"), "Samer": (10, 20, "start"),
    "Chartres": (12, 5, "start"), "Dreux": (12, 5, "start"), "Evreux": (-12, 5, "end"),
}

INK, ROUTE, RET = "#3a3028", "#9a3f1c", "#6b4c2a"


def line(names, **kw):
    pts = " ".join("%.1f,%.1f" % xy(*P[n]) for n in names)
    attrs = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return '<polyline points="%s" fill="none" %s/>' % (pts, attrs)


def text(x, y, s, size=15, anchor="start", weight="normal", style="normal", fill=INK):
    s = s.replace("&", "&amp;").replace("'", "&#8217;")
    return ('<text x="%.1f" y="%.1f" font-size="%s" text-anchor="%s" font-weight="%s" font-style="%s" '
            'fill="%s" stroke="#f5f0e8" stroke-width="4" paint-order="stroke">%s</text>'
            % (x, y, size, anchor, weight, style, fill, s))


svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
       'font-family="Georgia, \'Source Serif 4\', serif" role="img" '
       'aria-label="Map of David Silver\'s motorbike route, c. summer 1951: Exeter along the south coast to Dover, '
       'Calais, Boulogne, Amiens, Paris, Bourges and Blois, returning by Chartres, Dreux, Evreux, Amiens and Boulogne.">'
       % (W, H, W, H),
       '<defs><clipPath id="frame"><rect x="20" y="20" width="%d" height="%d" rx="6"/></clipPath>'
       '<marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0,1 L9,5 L0,9 z" fill="%s"/></marker></defs>' % (W - 40, H - 40, ROUTE),
       '<rect width="%d" height="%d" rx="10" fill="#f5f0e8"/>' % (W, H),
       '<g clip-path="url(#frame)">',
       '<rect x="20" y="20" width="%d" height="%d" fill="#dfe6e3"/>' % (W - 40, H - 40),
       '<path d="%s" fill="#efe6d4" stroke="#a09080" stroke-width="0.8" fill-rule="evenodd"/>' % land]
svg += ['<path d="%s" fill="none" stroke="#a09080" stroke-width="0.8" stroke-dasharray="3 3"/>' % b for b in borders if b]
svg += ['<path d="%s" fill="none" stroke="#8fa9b3" stroke-width="1.3"/>' % r for r in rivers if r]

# sea and region names
for x, y, s, size in ((-1.2, 50.45, "ENGLISH CHANNEL", 17), (-2.9, 51.22, "ENGLAND", 18),
                      (0.2, 48.3, "FRANCE", 20), (0.45, 47.42, "Loire", 13), (1.55, 49.12, "Seine", 13),
                      (1.35, 50.02, "Somme", 13)):
    x0, y0 = xy(x, y)
    svg.append('<text x="%.1f" y="%.1f" font-size="%d" fill="#6a7f88" letter-spacing="%s" font-style="italic">%s</text>'
               % (x0, y0, size, "3" if s.isupper() else "0", s))

# route: outward solid, planned return dashed
svg.append(line(RETURN, stroke=RET, stroke_width=3, stroke_dasharray="8 6", stroke_linejoin="round"))
svg.append(line(OUTWARD, stroke=ROUTE, stroke_width=3.5, stroke_linejoin="round"))
svg.append(line(FRANCE, stroke=ROUTE, stroke_width=3.5, stroke_linejoin="round"))
cx0, cy0 = xy(*P["Dover"]); cx1, cy1 = xy(*P["Calais"])
svg.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.5" '
           'stroke-dasharray="2 5" stroke-linecap="round" marker-end="url(#arr)"/>'
           % (cx0, cy0, (cx0 + cx1) / 2 + 10, (cy0 + cy1) / 2 - 25, cx1, cy1, ROUTE))
x, y = xy(1.62, 51.12)
svg.append(text(x - 40, y + 34, "Invicta, Tue", 13, "middle", style="italic"))

# loops: Loire châteaux (Sunday) and the lost-pack detour to Samer
bx, by = xy(*P["Blois"])
svg.append('<ellipse cx="%.1f" cy="%.1f" rx="46" ry="22" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 4"/>' % (bx + 34, by + 4, ROUTE))
svg.append(text(bx + 34, by + 46, "Sunday: châteaux", 13, "middle", style="italic"))

for n in set(OUTWARD + FRANCE + RETURN):
    x, y = xy(*P[n])
    if n in NIGHTS:
        svg.append('<circle cx="%.1f" cy="%.1f" r="6.5" fill="%s" stroke="#f5f0e8" stroke-width="2"/>' % (x, y, ROUTE))
    else:
        svg.append('<circle cx="%.1f" cy="%.1f" r="3" fill="#f5f0e8" stroke="%s" stroke-width="1.6"/>' % (x, y, ROUTE))
for n, (s, dx, dy, a) in NIGHTS.items():
    x, y = xy(*P[n]); svg.append(text(x + dx, y + dy, s, 16, a, "bold"))
for n, (dx, dy, a) in LABELS.items():
    x, y = xy(*P[n]); svg.append(text(x + dx, y + dy, n, 14, a))

# notes on the map
for lon, lat, s, a in (
        (-3.3, 50.95, "Sunday afternoon: sets off,", "start"),
        (-3.3, 50.88, "elephants at Fenny Bridges", "start"),
        (2.25, 50.42, "pack with customs papers lost", "start"),
        (2.25, 50.35, "on the road; found by police", "start"),
        (2.55, 48.70, "round the Arc de Triomphe,", "start"),
        (2.55, 48.63, "out by the Porte d’Italie", "start"),
        (0.95, 49.38, "Mon: return planned via", "end"),
        (0.95, 49.31, "Chartres, Dreux, Evreux", "end")):
    x, y = xy(lon, lat); svg.append(text(x, y, s, 13, a, style="italic", fill="#5a4a3a"))
svg.append("</g>")

# title + legend box
svg.append('<rect x="34" y="%d" width="370" height="158" rx="6" fill="#f5f0e8" fill-opacity="0.94" stroke="#a09080"/>' % (H - 192))
y0 = H - 160
svg.append(text(50, y0, "David Silver’s motorbike tour", 21, weight="bold"))
svg.append(text(50, y0 + 24, "probably summer 1951, from his three letters home", 14, style="italic"))
svg.append('<line x1="52" y1="%d" x2="96" y2="%d" stroke="%s" stroke-width="3.5"/>' % (y0 + 52, y0 + 52, ROUTE))
svg.append(text(108, y0 + 57, "route ridden (letters 1 and 2)", 14))
svg.append('<line x1="52" y1="%d" x2="96" y2="%d" stroke="%s" stroke-width="3" stroke-dasharray="8 6"/>' % (y0 + 78, y0 + 78, RET))
svg.append(text(108, y0 + 83, "return he planned from Blois (letter 3)", 14))
svg.append('<circle cx="74" cy="%d" r="6.5" fill="%s"/>' % (y0 + 104, ROUTE))
svg.append(text(108, y0 + 109, "overnight stop", 14))
svg.append(text(W - 34, H - 30, "Lines join the places he names, not the exact roads. Base map: Natural Earth.", 12, "end", style="italic", fill="#6a5a48"))
# scale bar: 50 miles
mx = 80.47 / 111.32 * KX * SCALE / KX  # 50 miles in px along a meridian
sx, sy = W - 230, H - 62
svg.append('<line x1="%d" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2"/>' % (sx, sy, sx + mx, sy, INK))
svg.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>' % (sx, sy - 5, sx, sy + 5, INK))
svg.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2"/>' % (sx + mx, sy - 5, sx + mx, sy + 5, INK))
svg.append(text(sx + mx / 2, sy - 9, "50 miles", 13, "middle"))
svg.append("</svg>")

open(OUT, "w").write("\n".join(svg))
print(OUT, os.path.getsize(OUT) // 1024, "KB")
