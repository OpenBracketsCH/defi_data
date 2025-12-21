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

def maps_links(lon, lat):
    if lon is None or lat is None:
        return ""
    osm = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=19/{lat}/{lon}"
    google = f"https://www.google.com/maps?q={lat},{lon}"
    return f"""
        <a href="{osm}">OSM</a> |
        <a href="{google}">Google Maps</a>
    """

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

    return ", ".join(parts)

old_idx = index(old["features"])
new_idx = index(new["features"])

added = new_idx.keys() - old_idx.keys()
removed = old_idx.keys() - new_idx.keys()
common = new_idx.keys() & old_idx.keys()

rows = []

def row(category, feature, changes=None):
    p = feature["properties"]
    lon, lat = coords(feature)

    rows.append(f"""
    <tr>
        <td>{category}</td>
        <td>{html.escape(p.get("name","(ohne Name)"))}<br><small>ID: {p.get("id")}</small></td>
        <td>{html.escape(address(p) or "")}</td>
        <td>{f"{lon}, {lat}" if lon else ""}</td>
        <td>{maps_links(lon, lat)}</td>
        <td>{"<br>".join(html.escape(c) for c in changes) if changes else ""}</td>
    </tr>
    """)

for i in added:
    row("🆕 Neu", new_idx[i])

for i in removed:
    row("❌ Entfernt", old_idx[i])

for i in common:
    old_p = old_idx[i]["properties"]
    new_p = new_idx[i]["properties"]

    changes = []
    for k in new_p:
        if old_p.get(k) != new_p.get(k):
            changes.append(f"{k}: '{old_p.get(k)}' → '{new_p.get(k)}'")

    if changes:
        row("✏️ Geändert", new_idx[i], changes)

html_mail = f"""
<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
th {{ background-color: #f4f4f4; }}
tr:nth-child(even) {{ background-color: #fafafa; }}
small {{ color: #666; }}
</style>
</head>
<body>
<h2>Änderungen an defis_kt_be.geojson</h2>

<table>
<tr>
    <th>Typ</th>
    <th>Name</th>
    <th>Adresse</th>
    <th>Koordinaten</th>
    <th>Karte</th>
    <th>Änderungen</th>
</tr>
{''.join(rows) if rows else '<tr><td colspan="6">Keine Änderungen</td></tr>'}
</table>

</body>
</html>
"""

print(html_mail)
