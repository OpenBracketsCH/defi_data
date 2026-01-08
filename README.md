# defikarte.ch Datensammlung

![Get data from Overpass](https://github.com/chnuessli/defi_archive/workflows/Get%20data%20from%20Overpass/badge.svg) [![Get data converted to csv](https://github.com/chnuessli/defi_data/actions/workflows/convert.yml/badge.svg)](https://github.com/chnuessli/defi_data/actions/workflows/convert.yml)

<img src="https://defikarte.ch/defikarte-logo-quer-gruen-positiv-rgb.png" alt="defikarte.ch" style="width:400px;"/>

## Beschreibung 
Sammlung von Files (JSON und CSV) für die Defikarte.ch und deren Partner die in Zukunft Daten beziehen möchten.
Die Daten können hier bezogen werden: [`data` Verzeichnis](https://github.com/chnuessli/defi_archive/tree/main/data)

**Wichtig**
Die Daten sind direkt aus OSM exportiert und in GeoJSON abgefüllt, danach werden die Daten in CSV konvertiert.

![data screenshot](data.png)

## Sinn und Zweck

Sinn dieses Archivs ist es, Datenveränderungen täglich nachzuvollziehen. Stündlich wird nun automatisiert ein GeoJSON generiert und somit Datenveränderungen dokumentiert. Für weitere Verarbeitung stellen wir nun auch CSV Dateien zu Verfügung.
Die Datensammlung soll stetig wachsen und so ein sauberes Archiv generieren.

## Overpass Abfragen via Overpass API

Die Abfragen sind immer gleich aufgebaut, hier ein paar Beispiele. Für alle Abfragen besuche bitte die TXT Files. Die TXT Files dazu findet man in `queries`.

Umgebaute Queries die mit der Overpass API korrespondieren können, ein Auszug und nicht vollständig. Die untenstehenden Snippets sind als Beispiel zu betrachten.

<details><summary>Abfragen ausklappen</summary>
<p>

## Defibrillatoren

### Dispogebiet SRZ

```json
[out:json][timeout:25];
(
//Kanton Zürich
area["ISO3166-2"="CH-ZH"];
//Kanton Schwyz
area["ISO3166-2"="CH-SZ"];
//Kanton Schaffhausen
area["ISO3166-2"="CH-SH"];
//Kanton Zug
area["ISO3166-2"="CH-ZG"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;
```

### Kanton ZH

```json
[out:json][timeout:25];
// fetch area “CH-ZH” to search in
area["ISO3166-2"="CH-ZH"]->.searchArea;
// gather results
(
  // query part for: “emergency=defibrillator”
  node["emergency"="defibrillator"](area.searchArea);
  way["emergency"="defibrillator"](area.searchArea);
  relation["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;
```

### Stadt ZH

```json
[out:json][timeout:25];
area[name="Zürich"]["wikipedia"="de:Zürich"]->.zurich;
// gather results
(
  node["emergency"="defibrillator"](area.zurich);
  way["emergency"="defibrillator"](area.zurich);
  relation["emergency"="defibrillator"](area.zurich);
);
// print results
out body;
>;
out skel qt;
```

### Kanton SG

```json
[out:json][timeout:25];
(
//Kanton St. Gallen
area["ISO3166-2"="CH-SG"];
//Kanton Glarus
area["ISO3166-2"="CH-GL"];
//Kanton Appenzell Innerhoden
area["ISO3166-2"="CH-AI"];
//Kanton Appenzell Ausserhoden
area["ISO3166-2"="CH-AR"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;
```

### KNZ St.Gallen

```json
[out:json][timeout:25];
(
//Kanton St. Gallen
area["ISO3166-2"="CH-SG"];
//Kanton Glarus
area["ISO3166-2"="CH-GL"];
//Kanton Appenzell Innerhoden
area["ISO3166-2"="CH-AI"];
//Kanton Appenzell Ausserhoden
area["ISO3166-2"="CH-AR"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;
```

### Defikarte.ch 24h Defis

Dieses JSON wird für die Webseite Defikarte.ch benötigt.

```json
[out:json][timeout:25];
(
//ganze Schweiz 24h Defis
area["ISO3166-1"="CH"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"]["opening_hours"="24/7"](area.searchArea);
);
// print results
out body;
>;
out skel qt;
```

### Defikarte.ch NICHT 24h Defis

Dieses JSON wird für die Webseite Defikarte.ch benötigt.

```json
[out:json][timeout:25];
(
//ganze Schweiz
area["ISO3166-1"="CH"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"]["opening_hours"!="24/7"](area.searchArea);
);
// print results
out body;
>;
out skel qt;
```

</p>
</details>

## Automation

In diesem Repository sind GitHub Actions eingerichtet, um täglich aktuelle Daten via [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) abzufragen und als GeoJSON abzulegen.

* Die aktuelle GeoJSON-Dateien sind im [`data` Verzeichnis](https://github.com/Schutz-Rettung-Zurich/json-archive/tree/main/data)
* Die GitHub Actions sind im [`overpass.yml`](https://github.com/Schutz-Rettung-Zurich/json-archive/blob/main/.github/workflows/overpass.yml) Workflow beschrieben
* Der Workflow verwendet das Skript [`run_queries.sh`](https://github.com/Schutz-Rettung-Zurich/json-archive/blob/main/run_queries.sh) um alle Queries laufen zu lassen
* Jedes Overpass-Query ist in einer eigenen Datei im [Verzeichnis `queries`](https://github.com/Schutz-Rettung-Zurich/json-archive/tree/main/queries) abgelegt

### Neues Query hinzufügen

Um ein neues Query hinzuzufügen, müssen folgende Schritte befolgt werden:

1. Query schreiben und via http://overpass-turbo.osm.ch/ testen. **ACHTUNG:** es ist nur die Overpass Query Syntax unterstützt, **keine [Overpass Turbo Shortcuts](https://wiki.openstreetmap.org/wiki/Overpass_turbo/Extended_Overpass_Turbo_Queries)** (z.B. ` {{geocodeArea:CH-ZH}}`)
2. Query als neue Datei in [`queries` Verzeichnis](https://github.com/Schutz-Rettung-Zurich/json-archive/tree/main/queries) ablegen
3. Neues Query in [`run_queries.sh`](https://github.com/Schutz-Rettung-Zurich/json-archive/blob/main/run_queries.sh) aufrufen

### Konvertierung der Daten

Um die Daten in CSV zu konvertieren wurde ein neuer Workflow eingerichtet.

1. In der Datei `converter.py` die Input Datei (GeoJSON) und die Output Datei (CSV) in eine neue Zeile schreiben. 
2. Den Workflow `convert.yml`laufen lassen


 ## Reporting: Änderungen an Defi-Daten per E-Mail

Dieses Repository enthält einen automatisierten Reporting-Mechanismus, der Änderungen an den Defi-Daten überwacht und als HTML-Mail verschickt.

### Ablauf

1. **Overpass-Update**
   - Der Workflow **„Get data from Overpass“** aktualisiert die GeoJSON-Dateien (z.B. `defis_kt_be.geojson`, `defis_kt_zh.geojson`) anhand eines Overpass-Queries.
   - Wenn sich der Inhalt einer Datei ändert, schreibt der Workflow einen neuen Commit auf den `main`-Branch.

2. **Diff-Reporting**
   - Für jeden Kanton gibt es einen eigenen Workflow, z.B.:
     - `GeoJSON Diff Mail (BE)`
     - `GeoJSON Diff Mail (ZH)`
   - Diese Workflows werden automatisch gestartet, sobald **„Get data from Overpass“** erfolgreich abgeschlossen ist (`workflow_run`-Trigger).

3. **Prüfung, ob ein Report nötig ist**
   - Der Reporting-Workflow checkt den aktuellen Stand von `main` aus.
   - Er merkt sich den zuletzt verarbeiteten Commit in einer Datei unter `.reporting/last_processed_sha_<KANTON>.txt`.
   - Wenn der aktuelle Commit bereits verarbeitet wurde, wird der Workflow ohne Mail beendet (Anti-Spam).
   - Falls der Commit neu ist, wird geprüft, ob die jeweilige GeoJSON-Datei im letzten Commit tatsächlich geändert wurde:
     ```bash
     git diff --quiet HEAD^..HEAD -- data/json/defis_kt_<KANTON>.geojson
     ```
   - Nur wenn sich die Datei geändert hat, wird ein Diff erzeugt und eine Mail versendet.

### Inhalt der E-Mail

Die E-Mail enthält eine HTML-Tabelle mit allen Änderungen an der jeweiligen GeoJSON-Datei seit dem letzten Commit:

- **Status**:
  - `neu` – neue Defi-Standorte
  - `geändert` – bestehende Standorte mit Änderungen in ausgewählten Attributen (z.B. Name, Adresse, Status)
  - `gelöscht` – entfernte Standorte
- **Name** des Defis
- **Adresse**, falls vorhanden (`addr:street`, `addr:housenumber`, `addr:postcode`, `addr:city`)
- **Koordinaten** (Lon/Lat)
- **Kartenlinks**:
  - OpenStreetMap-Link direkt auf den Node/Way/Relation (falls OSM-ID vorhanden)
  - Google Maps-Link auf die Koordinaten
- Bei `geändert` zusätzlich eine Liste der Feldänderungen, z.B.:
  ```text
  status: 'unknown' → 'verified'
  addr:street: 'Alte Gasse' → 'Neue Gasse'
