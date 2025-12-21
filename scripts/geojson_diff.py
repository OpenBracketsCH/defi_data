import json
import sys
import html
import os

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

def maps_links(lon, lat, osm_id=None):
    links = []
    if osm_id:
        links.append(f'<a href="https://www.openstreetmap.org/node/{osm_id}">OSM</a>')
    elif lon is not None and lat is not None:
        links.append(f'<a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=19/{lat}/{lon}">OSM</a>')
    if lon is not None and lat is not None:
        links.append(f'<a href="https://www.google.com/maps?q={lat},{lon}">Google Maps</a>')
    return " | ".join(links)

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

old_idx = index(old["features"])
new_idx = index(new["features"])

added = new_idx.keys() - old_idx.keys()
removed = old_idx.keys() - new_idx.keys()
common = new_idx.keys() & old_idx.keys()

rows = []
summary = {"neu":0, "entfernt":0, "geändert":0}

def row(category, feature, changes=None):
    p = feature["properties"]
    lon, lat = coords(feature)
    osm_id = p.get("id")
    addr = address(p)
    links = maps_links(lon, lat, osm_id)
    cls = ""
    if category == "🆕 Neu": cls = "new"
    elif category == "❌ Entfernt": cls = "removed"
    elif category == "✏️ Geändert": cls = "changed"

    rows.append(f"""
    <tr class="{cls}">
        <td>{category}</td>
        <td>{html.escape(p.get("name","(ohne Name)"))}<br><small>ID: {p.get("id")}</small></td>
        <td>{html.escape(addr) if addr else ""}</td>
        <td>{f"{lon}, {lat}" if lon else ""}</td>
        <td>{links}</td>
        <td>{"<br>".join(html.escape(c) for c in changes) if changes else ""}</td>
    </tr>
    """)

# Neue Einträge
for i in added:
    row("🆕 Neu", new_idx[i])
    summary["neu"] +=1

# Entfernte Einträge
for i in removed:
    row("❌ Entfernt", old_idx[i])
    summary["entfernt"] +=1

# Geänderte Einträge
for i in common:
    old_p = old_idx[i]["properties"]
    new_p = new_idx[i]["properties"]
    changes = []
    relevant_fields = ["status", "addr:street", "addr:housenumber", "addr:city", "addr:postcode", "name"]
    for k in relevant_fields:
        if old_p.get(k) != new_p.get(k):
            changes.append(f"{k}: '{old_p.get(k)}' → '{new_p.get(k)}'")
    if changes:
        row("✏️ Geändert", new_idx[i], changes)
        summary["geändert"] +=1

# Prüfen, ob es Änderungen gibt
if not rows:
    print("Keine Änderungen an der GeoJSON-Datei. Mail wird nicht gesendet.")
    exit(0)

# HTML-Mail
html_mail = f"""
<html>
<head>
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
