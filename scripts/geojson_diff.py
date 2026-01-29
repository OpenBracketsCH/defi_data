def generate_html_report(diff_results, area_name):
    """
    Erstellt den HTML-Report im neuen Card-Design basierend auf der 
    bestehenden Datenstruktur von geojson_diff.py.
    """
    new_count = len(diff_results.get('added', []))
    changed_count = len(diff_results.get('changed', []))
    deleted_count = len(diff_results.get('removed', []))

    # Das neue CSS-Styling
    style = """
    <style>
        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .header { background-color: #ffffff; padding: 25px; text-align: center; border-bottom: 1px solid #eee; }
        .header img { width: 160px; margin-bottom: 10px; }
        .content { padding: 25px; }
        h2 { color: #2c3e50; font-size: 20px; margin-top: 0; }
        .summary-bar { padding: 10px 15px; border-radius: 6px; font-weight: bold; font-size: 14px; margin-bottom: 20px; background-color: #f8f9fa; border-left: 4px solid #dee2e6; }
        .defi-card { border: 1px solid #e0e0e0; border-radius: 10px; padding: 18px; margin-bottom: 20px; position: relative; }
        .card-new { border-left: 5px solid #28a745; }
        .card-changed { border-left: 5px solid #fd7e14; }
        .card-removed { border-left: 5px solid #dc3545; background-color: #fffafa; }
        .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; color: white; }
        .badge-new { background-color: #28a745; }
        .badge-changed { background-color: #fd7e14; }
        .badge-removed { background-color: #dc3545; }
        .defi-name { font-size: 17px; font-weight: bold; color: #2c3e50; }
        .defi-id { color: #999; font-size: 11px; margin-bottom: 12px; }
        .diff-line { font-size: 14px; margin-top: 5px; color: #555; }
        del { color: #dc3545; background-color: #ffe6e6; text-decoration: line-through; padding: 0 2px; }
        ins { color: #28a745; background-color: #e6ffe6; text-decoration: none; font-weight: bold; padding: 0 2px; }
        .btn-group { margin-top: 15px; }
        .btn { display: inline-block; padding: 7px 14px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: 500; margin-right: 8px; }
        .btn-google { background-color: #4285F4; color: white !important; }
        .btn-osm { background-color: #7eb617; color: white !important; }
        .footer { padding: 20px; text-align: center; font-size: 11px; color: #aaa; background-color: #fafafa; }
    </style>
    """

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {style}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://defikarte.ch/defikarte-logo-quer-gruen-positiv-rgb.png" alt="defikarte.ch">
                <h2>Updates für {area_name}</h2>
            </div>
            <div class="content">
                <div class="summary-bar">
                    <span style="color:#28a745;">{new_count} neu</span> • 
                    <span style="color:#fd7e14;">{changed_count} geändert</span> • 
                    <span style="color:#dc3545;">{deleted_count} gelöscht</span>
                </div>
    """

    # Wir nutzen die bestehende Logik deiner Schleifen
    for status in ['added', 'changed', 'removed']:
        for item in diff_results.get(status, []):
            props = item.get('properties', {})
            # ID Handling wie im Originalskript
            node_id = item.get('id', 'N/A')
            name = props.get('name') or "(ohne Name)"
            
            # Koordinaten-Logik
            geom = item.get('geometry', {})
            coords = geom.get('coordinates', [0, 0])
            # GeoJSON ist [lon, lat], für Maps brauchen wir lat,lon
            lat_lon = f"{coords[1]},{coords[0]}"
            
            google_url = f"https://www.google.com/maps?q={lat_lon}"
            osm_url = f"https://www.openstreetmap.org/{node_id}"

            card_class = "card-new" if status == "added" else f"card-{status}"
            badge_class = "badge-new" if status == "added" else f"badge-{status}"
            badge_text = "Neu" if status == "added" else ("Geändert" if status == "changed" else "Gelöscht")

            html += f"""
            <div class="defi-card {card_class}">
                <span class="badge {badge_class}">{badge_text}</span>
                <div class="defi-name">{name}</div>
                <div class="defi-id">ID: {node_id}</div>
            """

            if status == 'changed' and 'changes' in item:
                for key, (old_val, new_val) in item['changes'].items():
                    html += f'<div class="diff-line"><strong>{key}:</strong> <del>{old_val}</del> → <ins>{new_val}</ins></div>'
            elif status == 'removed':
                html += '<div class="diff-line">Dieser Defibrillator wurde entfernt.</div>'
            else:
                html += f'<div class="diff-line">Koordinaten: {lat_lon}</div>'

            if status != 'removed':
                html += f"""
                <div class="btn-group">
                    <a href="{google_url}" class="btn btn-google">Google Maps</a>
                    <a href="{osm_url}" class="btn btn-osm">OSM Details</a>
                </div>
                """
            html += "</div>"

    html += """
            </div>
            <div class="footer">
                Dies ist eine automatisch generierte E-Mail von <strong>defikarte.ch</strong>.<br>
                Danke für deinen Einsatz!
            </div>
        </div>
    </body>
    </html>
    """
    return html