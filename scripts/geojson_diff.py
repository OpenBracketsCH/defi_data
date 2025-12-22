import json
import sys
import html

old_file = sys.argv[1]
new_file = sys.argv[2]

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

old = load(old_file)
new = load(new_file)

def index(features):
    return {
        f["properties"].get("id"): f
        for f in features
        if "id" in f.get("properties", {})
    }

def coords(feature):
    try:
        lon, lat = feature["geometry"]["coordinates"]
        return lon, lat
    except Exception:
        return None, None

def address(props):
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

def maps_links(lon, lat, osm_id=None):
    links = []
    if osm_id:
        links.append(f'<a href="https://www.openstreetmap.org/node/{osm_id}">OSM</a>')
    elif lon is not None and lat is not None:
        links.append(f'<a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=19/{lat}/{lon}">OSM</a>')

    if lon is not None and lat is not None:
        links.append(f'<a href="https://www.google.com/maps?q={lat},{lon}">Google Maps</a>')

    return " | ".join(links)

old_idx = index(old.get("features", []))
new_idx = index(new.get("features", []))

added = new_idx.keys() - old_idx.keys()
removed = old_idx.keys() - new_idx.keys()
common = new_idx.keys() & old_idx.keys()

rows = []
summary = {"neu": 0, "entfernt": 0, "geändert": 0}

# Welche Felder willst du als "Änderungen" anzeigen?
RELEVANT_FIELDS = [
    "name",
    "status",
    "addr:street",
    "addr:housenumber",
    "addr:postcode",
    "addr:city",
]

def add_row(category, feature, changes=None):
    p = feature.get("properties", {})
    lon, lat = coords(feature)
    osm_id = p.get("id")
    addr = address(p)
    links = maps_links(lon, lat, osm_id)

    css_class = {
        "🆕 Neu": "new",
        "❌ Entfernt": "removed",
        "✏️ Geändert": "changed",
    }.get(category, "")

    rows.append(f"""
    <tr class="{css_class}">
      <td>{category}</td>
      <td>{html.escape(str(p.get("name","(ohne Name)")))}<br><small>ID: {html.escape(str(p.get("id","")))}</small></td>
      <td>{html.escape(addr) if addr else ""}</td>
      <td>{html.escape(f"{lon}, {lat}") if lon is not None and lat is not None else ""}</td>
      <td>{links}</td>
      <td>{"<br>".join(html.escape(c) for c in changes) if changes else ""}</td>
    </tr>
    """)

# Neu
for i in sorted(added):
    add_row("🆕 Neu", new_idx[i])
    summary["neu"] += 1

# Entfernt
for i in sorted(removed):
    add_row("❌ Entfernt", old_idx[i])
    summary["entfernt"] += 1

# Geändert
for i in sorted(common):
    old_p = old_idx[i].get("properties", {})
    new_p = new_idx[i].get("properties", {})

    changes = []
    for k in RELEVANT_FIELDS:
        if old_p.get(k) != new_p.get(k):
            changes.append(f"{k}: '{old_p.get(k)}' → '{new_p.get(k)}'")

    if changes:
        add_row("✏️ Geändert", new_idx[i], changes)
        summary["geändert"] += 1

# Keine Änderungen → KEIN diff.html schreiben
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
