[out:json][timeout:25];

// Stadt Zug als Suchgebiet definieren
area
  ["boundary"="administrative"]
  ["name"="Zug"]
  ["admin_level"="8"]
  ->.searchArea;

// Alle Objekte mit emergency=defibrillator im Stadtgebiet
(
  node["emergency"="defibrillator"](area.searchArea);
  way["emergency"="defibrillator"](area.searchArea);
  relation["emergency"="defibrillator"](area.searchArea);
);

out center;
