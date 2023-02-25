[out:json][timeout:300];
(
//Kanton Basel Stadt
area["ISO3166-2"="CH-BS"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;