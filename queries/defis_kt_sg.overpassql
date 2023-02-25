[out:json][timeout:300];
(
//Kanton St.Gallen
area["ISO3166-2"="CH-SG"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;