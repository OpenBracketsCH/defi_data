import json
import sys
import html
import re

old_file = sys.argv[1]
new_file = sys.argv[2]

RELEVANT_FIELDS = [
    "name",
    "status",
    "addr:street",
    "addr:housenumber",
    "addr:postcode",
    "addr:city",
]

def load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def coords(feature):
    try:
        g = feature.get("geometry") or {}
        if g.get("type") != "Point":
            return None, None
        c = g.get("coordinates")
        if not (isinstance(c, list) and len(c) >= 2):
            return None, None
        return c[0], c[1]  # lon, lat
    except Exception:
        return None, None

def address(props: dict):
    parts = []
    street = props.get("addr:street")
    housenumber = props.get("addr:housenumber")
    postcode = props.get("addr:postcode")
    city = props.get("addr:city")

    if street or housenumber:
        parts.append(" ".join(p for p in [street, housenumber] if p))
    if postcode or city:
        parts.append(" ".join(p for p in [postcode, city] if p))

    return ", ".join(parts) if parts else None

def normalize_osm_id(s: str) -> str:
    s = str(s).strip()
    if re.match(r"^(node|way|relation)/\d+$", s):
        return s
    m = re.match(r"^(node|way|relation)\s*/\s*(\d+)$", s)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    if re.match(r"^\d+$", s):
        return f"node/{s}"
    return s

def get_osm_key(feature) -> str | None:
    p = feature.get("properties", {}) or {}
    for k in ("id", "@id", "osm_id", "osm:id", "osmid", "osmId"):
        v = p.get(k)
        if v is not None and str(v).strip():
            return normalize_osm_id(v)

    v = feature.get("id")
    if v is not None and str(v).strip():
        return normalize_osm_id(v)

    lon, lat = coords(feature)
    name = p.get("name", "")
    if lon is not None and lat is not None:
        return f"fallback:{name}:{lon}:{lat}"
    return None

def osm_url_from_key(osm_key: str) -> str:
    return f"https://www.openstreetmap.org/{osm_key}"

def maps_links(lon, lat, osm_key=None):
    links = []
    if osm_key and osm_key.startswith(("node/", "way/", "relation/")):
        links.append(f'<a href="{osm_url_from_key(osm_key)}">OSM</a>')
    elif lon is not None and lat is not None:
        links.append(f'<a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=19/{lat}/{lon}">OSM</a>')

    if lon is not None and lat is not None:
        links.append(f'<a href="https://www.google.com/maps?q={lat},{lon}">Google Maps</a>')

    return " | ".join(links)

def index(features):
    out = {}
    for f in features:
        key = get_osm_key(f)
        if key:
            out[key] = f
    return out

def props(feature) -> dict:
    return feature.get("properties", {}) or {}

old = load(old_file)
new = load(new_file)

old_idx = index(old.get("features", []) or [])
new_idx = index(new.get("features", []) or [])

added = set(new_idx) - set(old_idx)
removed = set(old_idx) - set(new_idx)
common = set(new_idx) & set(old_idx)

rows = []
summary = {"neu": 0, "entfernt": 0, "geändert": 0}

def add_row(category, feature, changes=None):
    p = props(feature)
    lon, lat = coords(feature)
    key = get_osm_key(feature)
    addr = address(p)
    links = maps_links(lon, lat, key)

    css = {"🆕 Neu":"new","❌ Entfernt":"removed","✏️ Geändert":"changed"}.get(category,"")
    name = str(p.get("name","(ohne Name)"))
    fid = key or ""

    rows.append(f"""
    <tr class="{css}">
      <td>{category}</td>
      <td>{html.escape(name)}<br><small>ID: {html.escape(fid)}</small></td>
      <td>{html.escape(addr) if addr else ""}</td>
      <td>{html.escape(f"{lon}, {lat}") if lon is not None and lat is not None else ""}</td>
      <td>{links}</td>
      <td>{("<br>".join(html.escape(c) for c in changes)) if changes else ""}</td>
    </tr>
    """)

for k in sorted(added):
    add_row("🆕 Neu", new_idx[k])
    summary["neu"] += 1

for k in sorted(removed):
    add_row("❌ Entfernt", old_idx[k])
    summary["entfernt"] += 1

for k in sorted(common):
    op = props(old_idx[k])
    np = props(new_idx[k])
    changes = []
    for f in RELEVANT_FIELDS:
        if op.get(f) != np.get(f):
            changes.append(f"{f}: '{op.get(f)}' → '{np.get(f)}'")
    if changes:
        add_row("✏️ Geändert", new_idx[k], changes)
        summary["geändert"] += 1

# Wenn nichts zu reporten: KEIN diff.html erzeugen
if not rows:
    sys.exit(0)

html_mail = f"""
<html>
<head>
<meta charset="utf-8"/>
<style>
body {{ font-family: Arial, sans-serif; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
th {{ background-color: #f4f4f4; }}
tr:nth-child(even) {{ background-color: #fafafa; }}
tr.new {{ background-color: #e6ffe6; }}
tr.removed {{ background-color: #ffe6e6; }}
tr.changed {{ background-color: #fff8e6; }}
small {{ color: #666; }}
</style>
</head>
<body>
<h2>Änderungen an defis_kt_be.geojson</h2>
<p><strong>📊 Zusammenfassung:</strong> {summary['neu']} neu, {summary['geändert']} geändert, {summary['entfernt']} entfernt</p>

<table>
  <tr>
    <th>Typ</th>
    <th>Name</th>
    <th>Adresse</th>
    <th>Koordinaten</th>
    <th>Karte</th>
    <th>Änderungen</th>
  </tr>
  {''.join(rows)}
</table>
</body>
</html>
"""

with open("diff.html", "w", encoding="utf-8") as f:
    f.write(html_mail)
