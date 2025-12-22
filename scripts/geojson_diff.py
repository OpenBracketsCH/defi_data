import json
import sys
import html
import re

old_file = sys.argv[1]
new_file = sys.argv[2]

# Welche Felder sollen als "Änderungen" angezeigt werden?
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
    """
    Returns (lon, lat) for Point geometry if present, else (None, None).
    """
    try:
        g = feature.get("geometry") or {}
        if g.get("type") != "Point":
            return None, None
        c = g.get("coordinates")
        if not (isinstance(c, list) and len(c) >= 2):
            return None, None
        lon, lat = c[0], c[1]
        return lon, lat
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
    """
    Normalizes various OSM id formats to:
      node/123, way/123, relation/123, or keeps string if unknown.
    """
    s = str(s).strip()

    # Already typed
    if re.match(r"^(node|way|relation)/\d+$", s):
        return s

    # Sometimes '@id' looks like 'node/123'
    m = re.match(r"^(node|way|relation)\s*/\s*(\d+)$", s)
    if m:
        return f"{m.group(1)}/{m.group(2)}"

    # Pure numeric -> assume node/<id> (fits your use case)
    if re.match(r"^\d+$", s):
        return f"node/{s}"

    return s

def get_osm_key(feature) -> str | None:
    """
    Returns a stable key for feature identity across exports.
    Tries several common fields used by Overpass/GeoJSON generators.
    """
    p = feature.get("properties", {}) or {}

    # 1) Common props fields
    for k in ("id", "@id", "osm_id", "osm:id", "osmid", "osmId"):
        v = p.get(k)
        if v is not None and str(v).strip() != "":
            return normalize_osm_id(v)

    # 2) Feature root id
    v = feature.get("id")
    if v is not None and str(v).strip() != "":
        return normalize_osm_id(v)

    # 3) Sometimes Overpass puts it under properties['type'] + properties['id']
    #    (rare, but cheap to check)
    t = p.get("type")
    pid = p.get("id")
    if t in ("node", "way", "relation") and pid is not None and str(pid).strip() != "":
        return f"{t}/{str(pid).strip()}"

    # 4) Last resort fallback: name + coords (not perfect, but better than losing everything)
    lon, lat = coords(feature)
    name = p.get("name", "")
    if lon is not None and lat is not None:
        return f"fallback:{name}:{lon}:{lat}"

    return None

def feature_display_id(feature) -> str:
    """
    Human-readable ID for table cell. Prefer OSM key; else empty.
    """
    key = get_osm_key(feature)
    return key or ""

def osm_url_from_key(osm_key: str) -> str:
    # osm_key like "node/123"
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

def get_props(feature) -> dict:
    return feature.get("properties", {}) or {}

# ---- Load data ----
old = load(old_file)
new = load(new_file)

old_features = old.get("features", []) or []
new_features = new.get("features", []) or []

old_idx = index(old_features)
new_idx = index(new_features)

added = set(new_idx.keys()) - set(old_idx.keys())
removed = set(old_idx.keys()) - set(new_idx.keys())
common = set(new_idx.keys()) & set(old_idx.keys())

rows = []
summary = {"neu": 0, "entfernt": 0, "geändert": 0}

def add_row(category, feature, changes=None):
    p = get_props(feature)
    lon, lat = coords(feature)
    osm_key = get_osm_key(feature)

    addr = address(p)
    links = maps_links(lon, lat, osm_key)
    fid = feature_display_id(feature)
    name = str(p.get("name", "(ohne Name)"))

    css_class = {
        "🆕 Neu": "new",
        "❌ Entfernt": "removed",
        "✏️ Geändert": "changed",
    }.get(category, "")

    changes_html = ""
    if changes:
        changes_html = "<br>".join(html.escape(c) for c in changes)

    rows.append(f"""
    <tr class="{css_class}">
      <td>{category}</td>
      <td>{html.escape(name)}<br><small>ID: {html.escape(fid)}</small></td>
      <td>{html.escape(addr) if addr else ""}</td>
      <td>{html.escape(f"{lon}, {lat}") if lon is not None and lat is not None else ""}</td>
      <td>{links}</td>
      <td>{changes_html}</td>
    </tr>
    """)

# New
for k in sorted(added):
    add_row("🆕 Neu", new_idx[k])
    summary["neu"] += 1

# Removed
for k in sorted(removed):
    add_row("❌ Entfernt", old_idx[k])
    summary["entfernt"] += 1

# Changed
for k in sorted(common):
    old_f = old_idx[k]
    new_f = new_idx[k]
    old_p = get_props(old_f)
    new_p = get_props(new_f)

    changes = []
    for field in RELEVANT_FIELDS:
        if old_p.get(field) != new_p.get(field):
            changes.append(f"{field}: '{old_p.get(field)}' → '{new_p.get(field)}'")

    # Optional: Koordinatenänderungen melden (wenn du willst, setze True)
    REPORT_COORD_CHANGES = False
    if REPORT_COORD_CHANGES:
        old_lon, old_lat = coords(old_f)
        new_lon, new_lat = coords(new_f)
        if (old_lon, old_lat) != (new_lon, new_lat):
            changes.append(f"coordinates: '{old_lon}, {old_lat}' → '{new_lon}, {new_lat}'")

    if changes:
        add_row("✏️ Geändert", new_f, changes)
        summary["geändert"] += 1

# If nothing to report: do NOT create diff.html
if not rows:
    print("No changes detected by geojson_diff.py; diff.html not created.")
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

print("diff.html created.")
