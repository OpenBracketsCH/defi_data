[out:json][timeout:300];
(
//Kanton Solothurn
area["ISO3166-2"="CH-SO"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;