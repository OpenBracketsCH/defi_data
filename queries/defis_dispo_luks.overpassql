[out:json][timeout:300];
(
//Kanton Luzern
area["ISO3166-2"="CH-LU"];
//Kanton Obwalden
area["ISO3166-2"="CH-OW"];
//Kanton Nidwalden
area["ISO3166-2"="CH-NW"];
//Kanton Uri
area["ISO3166-2"="CH-UR"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;
