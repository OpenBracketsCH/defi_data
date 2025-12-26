import json
import requests
import os
import smtplib
import ssl
from email.message import EmailMessage

# --- KONFIGURATION ---
GEOJSON_URL = "https://raw.githubusercontent.com/OpenBracketsCH/defi_data/main/data/json/defis_kt_be.geojson"
STATE_FILE = "last_known_version.json" # Dateiname für die vorherige Version
# Felder, die in der E-Mail angezeigt werden sollen (anpassen, falls nötig)
DISPLAY_FIELDS = ['name', 'address', 'operator'] 

# --- HILFSFUNKTIONEN ---

def fetch_geojson(url):
    """Holt die aktuelle GeoJSON-Datei."""
    print(f"Lade GeoJSON von: {url}")
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def features_to_dict(data):
    """
    Indiziert die GeoJSON Features anhand eines eindeutigen Schlüssels.
    ANNAHME: Der eindeutige Schlüssel liegt im 'properties'-Dictionary und heißt 'id' oder 'name'.
    """
    return {
        # Verwende 'id' oder 'name' als Schlüssel; falls keines da, wird es ignoriert
        f['properties'].get('id') or f['properties'].get('name'): f['properties']
        for f in data.get('features', []) 
        if f['properties'].get('id') or f['properties'].get('name')
    }

def calculate_diff(old_features, new_features):
    """Berechnet die hinzugefügten, gelöschten und geänderten Features."""
    
    old_keys = set(old_features.keys())
    new_keys = set(new_features.keys())
    
    diff = {
        "added": [new_features[k] for k in new_keys - old_keys],
        "deleted": [old_features[k] for k in old_keys - new_keys],
        "modified": []
    }
    
    # Überprüfe geänderte Features (Features, die in beiden Sets existieren)
    for key in old_keys.intersection(new_keys):
        old_props = old_features[key]
        new_props = new_features[key]
        
        # Vereinfachte Prüfung: JSON-String-Vergleich der Properties
        if json.dumps(old_props, sort_keys=True) != json.dumps(new_props, sort_keys=True):
             diff["modified"].append({
                "key": key,
                "old": old_props,
                "new": new_props
            })

    return diff

def format_email_body(diff):
    """Formatiert die Unterschiede in einen menschlich lesbaren Text."""
    body = "Hallo,\n\nHier sind die Änderungen an den Defibrillatoren im Kanton Bern:\n\n"
    
    found_changes = diff["added"] or diff["deleted"] or diff["modified"]
    
    if diff["added"]:
        body += "--- ✅ NEU HINZUGEFÜGT ---\n"
        for item in diff["added"]:
            info = ', '.join([f"{field}: {item.get(field, 'N/A')}" for field in DISPLAY_FIELDS])
            body += f"- {info}\n"
        body += "\n"
        
    if diff["deleted"]:
        body += "--- ❌ ENTFERNT ---\n"
        for item in diff["deleted"]:
            info = ', '.join([f"{field}: {item.get(field, 'N/A')}" for field in DISPLAY_FIELDS])
            body += f"- {info}\n"
        body += "\n"
        
    if diff["modified"]:
        body += "--- 📝 GEÄNDERT ---\n"
        for item in diff["modified"]:
            body += f"- Objekt ID/Name: {item['key']}\n"
            # Füge hier komplexere Diff-Details hinzu, falls gewünscht
            body += "  - Details: Eigenschaften wurden aktualisiert (siehe GeoJSON für genaue Diff).\n"
        body += "\n"


    if not found_changes:
        body += "Keine neuen oder geänderten Features in dieser Version gefunden.\n"
        
    return body, found_changes

def send_email(body):
    """Sendet die formatierte E-Mail."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = 'Automatischer Defi-Daten-Update (Kt. BE)'
    msg['From'] = os.environ.get('SMTP_USERNAME')
    msg['To'] = 'christian@defikarte.ch' # <--- PASSE DIES AN

    # SMTP-Konfiguration aus Umgebungsvariablen (GitHub Secrets)
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'asmtp.mail.hostpoint.ch') # Kann angepasst werden
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('MAIL_USER')
    SMTP_PASSWORD = os.environ.get('MAIL_PASS')

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("FEHLER: SMTP Zugangsdaten (Benutzername/Passwort) fehlen in Umgebungsvariablen.")
        return

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            print("E-Mail erfolgreich gesendet.")
    except Exception as e:
        print(f"FEHLER beim Senden der E-Mail: {e}")


# --- HAUPT-LOGIK ---

def main():
    print("Starte den Diff-Prozess...")
    
    # 1. Lade die vorherige Version (State File)
    old_data = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                old_data = json.load(f)
            print(f"Vorherige Version ({STATE_FILE}) erfolgreich geladen.")
        except Exception as e:
            print(f"Warnung: Fehler beim Laden von {STATE_FILE}: {e}. Behandle als ersten Lauf.")
            
    # 2. Lade die aktuelle Version von GitHub
    try:
        new_data = fetch_geojson(GEOJSON_URL)
    except Exception as e:
        print(f"Fehler beim Abrufen der GeoJSON-Datei: {e}")
        return

    # 3. Diff berechnen und E-Mail senden (nur wenn alter State existiert)
    if old_data:
        old_features = features_to_dict(old_data)
        new_features = features_to_dict(new_data)
        
        diff = calculate_diff(old_features, new_features)
        email_body, found_changes = format_email_body(diff)
        
        if found_changes:
            print(f"Unterschiede gefunden: {len(diff['added'])} hinzugefügt, {len(diff['deleted'])} gelöscht, {len(diff['modified'])} geändert.")
            send_email(email_body)
        else:
            print("Keine relevanten Änderungen gefunden.")
    else:
        print("Kein alter Zustand gefunden. Überspringe Diff-Berechnung und Mail-Versand für diesen Lauf.")
        
    # 4. Speichere die aktuelle Version als neue "last_known_version"
    print(f"Speichere neue Version als {STATE_FILE}...")
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(new_data, f, indent=2)
        print("Neue Version erfolgreich gespeichert.")
    except Exception as e:
        print(f"FEHLER beim Speichern der neuen Version: {e}")

if __name__ == "__main__":
    main()