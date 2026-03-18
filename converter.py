import json
import csv
import os
from pathlib import Path

JSON_DIR = Path("data/json")
CSV_DIR = Path("data/csv")

CSV_DIR.mkdir(parents=True, exist_ok=True)


def geojson_to_csv(geojson_path: Path, csv_path: Path) -> None:
    with open(geojson_path, encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    if not features:
        print(f"  Keine Features gefunden: {geojson_path.name}")
        return

    rows = []
    for feature in features:
        row = {}

        # OSM Node-ID aus dem "id"-Feld (z.B. "node/123456")
        raw_id = feature.get("id", "")
        row["osm_id"] = raw_id.split("/")[-1] if "/" in str(raw_id) else raw_id
        row["osm_type"] = raw_id.split("/")[0] if "/" in str(raw_id) else ""

        # Koordinaten aus geometry
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates", [])
        if coords and len(coords) >= 2:
            row["lon"] = coords[0]
            row["lat"] = coords[1]
        else:
            row["lon"] = ""
            row["lat"] = ""

        # Alle properties flach hinzufügen
        properties = feature.get("properties") or {}
        for key, value in properties.items():
            row[key] = value

        rows.append(row)

    # Alle Spalten über alle Rows sammeln (union), Reihenfolge: Basis-Felder zuerst
    base_cols = ["osm_id", "osm_type", "lat", "lon"]
    all_keys = set()
    for row in rows:
        all_keys.update(row.keys())
    extra_cols = sorted(all_keys - set(base_cols))
    fieldnames = base_cols + extra_cols

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"  {geojson_path.name} → {csv_path.name} ({len(rows)} Einträge, {len(fieldnames)} Spalten)")


def main():
    geojson_files = sorted(JSON_DIR.glob("*.geojson"))

    if not geojson_files:
        print(f"Keine .geojson Dateien gefunden in {JSON_DIR}")
        return

    print(f"{len(geojson_files)} GeoJSON-Dateien gefunden\n")

    for geojson_path in geojson_files:
        csv_path = CSV_DIR / (geojson_path.stem + ".csv")
        try:
            geojson_to_csv(geojson_path, csv_path)
        except Exception as e:
            print(f"  FEHLER bei {geojson_path.name}: {e}")

    print("\nFertig.")


if __name__ == "__main__":
    main()
