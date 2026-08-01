"""
Erzeugt das HTML für den wöchentlichen Änderungs-Report aus einer
pending_changes_<id>.json Datei.

Verwendung:
    python build_weekly_report.py <pending_file> <kanton_name> <output_html>
"""

import json
import html
import os
import sys
from datetime import datetime, timezone

SHOW_PARTNER_LOGO = os.environ.get("SHOW_PARTNER_LOGO", "false").lower() == "true"
PARTNER_LOGO_URL = os.environ.get("PARTNER_LOGO_URL", "")
DEFIKARTE_LOGO_URL = os.environ.get(
    "DEFIKARTE_LOGO_URL",
    "https://defikarte.ch/defikarte-logo-quer-gruen-positiv-rgb.png"
)


def maps_links(lon, lat, key=None):
    links = []
    if key and key.startswith(("node/", "way/", "relation/")):
        links.append(f'<a href="https://www.openstreetmap.org/{key}">OSM</a>')
    elif lon is not None and lat is not None:
        links.append(f'<a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=19/{lat}/{lon}">OSM</a>')
    if lon is not None and lat is not None:
        links.append(f'<a href="https://www.google.com/maps?q={lat},{lon}">Google Maps</a>')
    return " | ".join(links)


def build_logo_header():
    if SHOW_PARTNER_LOGO and PARTNER_LOGO_URL:
        return f"""
        <table width="100%" style="border-collapse: collapse; margin-bottom: 16px;">
          <tr>
            <td align="left" valign="middle">
              <img src="{DEFIKARTE_LOGO_URL}" alt="defikarte.ch" style="width:200px; display:block;"/>
            </td>
            <td align="right" valign="middle">
              <img src="{PARTNER_LOGO_URL}" alt="Partner" style="max-height:60px; display:block;"/>
            </td>
          </tr>
        </table>
        """
    return f'<img src="{DEFIKARTE_LOGO_URL}" alt="defikarte.ch" style="width:200px;"/>'


def main():
    pending_file = sys.argv[1]
    kanton_name = sys.argv[2]
    output_file = sys.argv[3]

    with open(pending_file, encoding="utf-8") as f:
        entries = json.load(f)

    rows = []
    for e in entries:
        lon, lat = e.get("lon"), e.get("lat")
        key = e.get("key", "")
        addr = e.get("address") or ""
        name = e.get("name", "(ohne Name)")
        changes = e.get("changes", [])
        detected = e.get("detected_at", "")[:10]
        links = maps_links(lon, lat, key)

        rows.append(f"""
        <tr class="changed">
          <td>geändert</td>
          <td>{html.escape(name)}<br><small>ID: {html.escape(key)}</small></td>
          <td>{html.escape(addr)}</td>
          <td>{html.escape(f"{lon}, {lat}") if lon is not None and lat is not None else ""}</td>
          <td>{links}</td>
          <td>{("<br>".join(html.escape(c) for c in changes))}<br><small>Erkannt: {html.escape(detected)}</small></td>
        </tr>
        """)

    today = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    logo_header = build_logo_header()

    output = f"""
    <html>
    <head>
    <meta charset="utf-8"/>
    <style>
    body {{ font-family: Arial, sans-serif; }}
    table.data {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background-color: #f4f4f4; }}
    tr.changed {{ background-color: #fff8e6; }}
    small {{ color: #666; }}
    </style>
    </head>
    <body>
    {logo_header}
    <h2>Wöchentlicher Änderungs-Report – {html.escape(kanton_name)}</h2>
    <p>Zusammenstellung aller geänderten Defibrillatoren der letzten Woche (Stand {html.escape(today)}).</p>
    <p><strong>{len(entries)} Einträge geändert</strong></p>
    <table class="data">
      <tr>
        <th>Status</th><th>Name</th><th>Adresse</th>
        <th>Koordinaten</th><th>Karte</th><th>Details</th>
      </tr>
      {"".join(rows)}
    </table>
    <br>
    <p>Zur Erklärung: Die Tabelle zeigt geänderte Datensätze mit Pfeilen alt → neu.</p>
    <h6>Dies ist eine automatisch generierte E-Mail von defikarte.ch</h6>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"{output_file} geschrieben mit {len(entries)} Einträgen.")


if __name__ == "__main__":
    main()
